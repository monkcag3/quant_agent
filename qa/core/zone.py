
import signal
import asyncio
import platform
from collections import defaultdict
from typing import cast, Any, Awaitable, Callable, Dict, Generator, List, Optional, Set, Tuple
import abc
import contextlib
import dataclasses
import datetime
import functools
import heapq
import logging

from . import helpers, event


logger = logging.getLogger(__name__)
EventHandler = Callable[[event.Event], Awaitable[Any]]
IdleHandler = Callable[[], Awaitable[Any]]
SchedulerJob = Callable[[], Awaitable[Any]]


@dataclasses.dataclass
class EventDispatch:
    event: event.Event
    handlers: List[EventHandler]


@dataclasses.dataclass(order=True)
class ScheduledJob:
    when: datetime.datetime
    job: SchedulerJob = dataclasses.field(compare=False) # Comparing function objects fails on Win32


class SchedulerQueue:
    def __init__(self):
        self._queue = []

    def push(self, when: datetime.datetime, job: SchedulerJob):
        heapq.heappush(self._queue, ScheduledJob(when=when, job=job))

    def peek_next_event_dt(self) -> Optional[datetime.datetime]:
        ret = None
        if self._queue:
            ret = self._queue[0].when
        return ret

    def peek_last_event_dt(self) -> Optional[datetime.datetime]:
        ret = None
        if self._queue:
            ret = heapq.nlargest(1, self._queue)[0].when
        return ret

    def pop(self) -> Tuple[datetime.datetime, SchedulerJob]:
        assert self._queue
        scheduled_job = heapq.heappop(self._queue)
        return scheduled_job.when, scheduled_job.job
    

class EventMultiplexer:
    """
    A multiplexer that manages multiple event sources and provides methods to retrieve events in chronological order.
    """
    def __init__(self) -> None:
        self._prefetched_events: Dict[event.EventSource, Optional[event.Event]] = {}

    def add(self, source: event.EventSource):
        self._prefetched_events.setdefault(source)

    def peek_next_event_dt(self) -> Optional[datetime.datetime]:
        self._prefetch()

        return min(
            [evnt.when for evnt in self._prefetched_events.values() if evnt],
            default=None
        )

    def pop(
        self,
        max_dt: datetime.datetime
    ) -> Tuple[Optional[event.EventSource], Optional[event.Event]]:
        ret_source: Optional[event.EventSource] = None
        ret_event: Optional[event.Event] = None
        when_upper = max_dt

        # Find the next event to return, this is, the oldest one that is <= max_dt and with the highest priority.
        for source, evnt in self._prefetched_events.items():
            # Prefetch the event if necessary.
            if evnt is None and (evnt := source.pop()):
                self._prefetched_events[source] = evnt

            # Skip it if its empty.
            if evnt is None:
                continue

            # Skip it its out of range
            if evnt.when > when_upper:
                continue

            # Select it if its older than the best one so far, or if both have the same age but current one has
            # higher priority.
            if evnt.when < when_upper or ret_source is None or source.priority > ret_source.priority:
                ret_source = source
                ret_event = evnt
                when_upper = evnt.when
 
        # Consume the event.
        if ret_source:
            self._prefetched_events[ret_source] = None

        return (ret_source, ret_event)

    def pop_while(
        self,
        max_dt: datetime.datetime
    ) -> Generator[Tuple[event.EventSource, event.Event], None, None]:
        while None not in (src_and_event := self.pop(max_dt)):
            yield (cast(event.EventSource, src_and_event[0]), cast(event.Event, src_and_event[1]))

    def _prefetch(self):
        sources_to_pop = [
            source for source, event in self._prefetched_events.items() if event is None
        ]
        for source in sources_to_pop:
            if event := source.pop():
                self._prefetched_events[source] = event


class Zone(metaclass=abc.ABCMeta):
    def __init__(self, max_concurrent: int = 50):
        self._event_handlers: Dict[event.EventSource, List[EventHandler]] = defaultdict(list)
        self._sniffers_pre: List[EventHandler] = []
        self._sniffers_post: List[EventHandler] = []
        self._producers: Set[event.Producer] = set()
        self._core_tasks: Optional[helpers.TaskGroup] = None
        self._handler_tasks = helpers.TaskPool(max_concurrent, max_queue_size=max_concurrent*10)
        self._scheduler_queue = SchedulerQueue()
        self._event_mux = EventMultiplexer()
        self._running = False
        self._stopped = False
        self.stop_on_handler_exceptions = False

    @abc.abstractmethod
    def now(self) -> datetime.datetime:
        raise NotImplementedError()
    
    @property
    def stopped(self) -> bool:
        return self._stopped
    

    def stop(self):
        self._stopped = True
        if self._core_tasks:
            self._core_tasks.cancel()
        self._handler_tasks.cancel()

    def subscribe(
        self,
        source: event.EventSource,
        event_handler: EventHandler,
    ):
        assert not self._running, "Subscribing once we're running is not currently supported."

        self._event_mux.add(source)
        handlers = self._event_handlers[source]
        if event_handler not in handlers:
            handlers.append(event_handler)
        if source.producer:
            self._producers.add(source.producer)

    def subscribe_all(
        self,
        event_handler: EventHandler,
        front_run: bool = False,
    ):
        assert not self._running, "Subscribing once we're running is not currently supported."
        sniffers = self._sniffers_pre if front_run else self._sniffers_post
        if event_handler not in sniffers:
            sniffers.append(event_handler)

    def schedule(
        self,
        when: datetime.datetime,
        job: SchedulerJob,
    ):
        self._scheduler_queue.push(when, job)

    async def run(
        self,
        stop_signals: List[int] = [signal.SIGINT, signal.SIGTERM]
    ):
        
        if platform.system() != "Windows":
            for stop_singal in stop_signals:
                asyncio.get_event_loop().add_signal_handler(stop_singal, self.stop)

        self._running = True
        try:
            async with self._core_task_group_() as tg:
                for producer in self._producers:
                    tg.create_task(producer.initialize())
            async with self._core_task_group_() as tg:
                for producer in self._producers:
                    tg.create_task(producer.main())
                tg.create_task(self._dispatch_loop_())
        except asyncio.CancelledError:
            if not self.stopped:
                raise
        finally:
            self._handler_tasks.cancel()
            await self._handler_tasks.wait()
            self._core_tasks = None
            await gather_no_raise(*[producer.finalize() for producer in self._producers])

    @abc.abstractmethod
    async def _dispatch_loop_(self):
        raise NotImplementedError()
    
    @contextlib.asynccontextmanager
    async def _core_task_group_(self):
        try:
            async with helpers.TaskGroup() as tg:
                self._core_tasks = tg
                yield tg
        finally:
            self._core_tasks = None

    async def _dispatch_event_(
        self,
        event_dispatch: EventDispatch,
    ):
        if self._sniffers_pre:
            await asyncio.gather(
                *[self._call_event_handler_(event_dispatch.event, handler) for handler in self._sniffers_pre]
            )
        if event_dispatch.handlers:
            await asyncio.gather(
                *[self._call_event_handler_(event_dispatch.event, handler) for handler in event_dispatch.handlers]
            )
        if self._sniffers_post:
            await asyncio.gather(
                *[self._call_event_handler_(event_dispatch.event, handler) for handler in self._sniffers_post]
            )

    async def _call_event_handler_(
        self,
        event: event.Event,
        handler: EventHandler,
    ):
        try:
            return await handler(event)
        except Exception as e:
            if self.stop_on_handler_exceptions:
                self.stop()

    async def _execute_scheduled_(
        self,
        dt: datetime.datetime,
        job: SchedulerJob,
    ):
        try:
            await job()
        except Exception as e:
            if self.stop_on_handler_exceptions:
                self.stop()


class QAZone(Zone):
    def __init__(self, max_concurrent: int = 50):
        super().__init__(max_concurrent=max_concurrent)
        self._last_dt: Optional[datetime.datetime] = None

    @property
    def now_awailable(self) -> bool:
        return self._last_dt is not None
    
    def now(self) -> datetime.datetime:
        if self._last_dt is None:
            raise ValueError("Can't calculate current datetime since no events were processed")
        return self._last_dt
    
    async def _dispatch_loop_(self):
        while not self.stopped:
            next_dt = self._event_mux.peek_next_event_dt()
            if next_dt:
                assert self._last_dt is None or next_dt >= self._last_dt, \
                    f"{next_dt} can't be dispatched after {self._last_dt}"
                await self._dispatch_scheduled_(next_dt)
                await self._dispatch_events_(next_dt)
            else:
                if last_scheduled_dt := self._scheduler_queue.peek_last_event_dt():
                    await self._dispatch_scheduled_(last_scheduled_dt)
                self.stop()

    async def _dispatch_scheduled_(
        self,
        dt: datetime.datetime,
    ):
        next_scheduled_dt = self._scheduler_queue.peek_next_event_dt()
        while next_scheduled_dt and next_scheduled_dt <= dt:
            next_scheduled_dt, job = self._scheduler_queue.pop()
            if self._last_dt is None or next_scheduled_dt > self._last_dt:
                self._last_dt = next_scheduled_dt

            await self._handler_tasks.push(functools.partial(self._execute_scheduled_, next_scheduled_dt, job))
    
    async def _dispatch_events_(
        self,
        dt: datetime.datetime,
    ):
        self._last_dt = dt
        for source, evnt in self._event_mux.pop_while(dt):
            await self._handler_tasks.push(
                functools.partial(
                    self._dispatch_event_, EventDispatch(event=evnt, handlers=self._event_handlers[source])
                )
            )
        await self._handler_tasks.wait()
    



async def gather_no_raise(*awaitables):
    await asyncio.gather(*[await_no_raise(awaitable) for awaitable in awaitables])

async def await_no_raise(core: Awaitable[Any], msg: str = "Unhandled exception"):
    with helpers.no_raise(logger, msg):
        await core