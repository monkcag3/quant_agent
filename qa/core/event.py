
import asyncio
from asyncio import Queue, QueueEmpty, QueueFull
from typing import Any, Callable
from collections import defaultdict


class Event:
    def __init__(self, type: str, data: Any = None) -> None:
        self.type: str = type
        self.data: Any = data


class EventEngine:
    """
    Event Engine distributes event object based on its type
    to those handlers registered.

    It also generates timer event by every interval seconds,
    which can be used for timing purpose.
    """
    
    def __init__(self, interval = 1) -> None:
        """
        Timer event is generated every 1 second by default, if
        interval not specified.
        """
        self.interval: int = interval
        self._queue: Queue = Queue()
        self._active: bool = False
        self._handlers: defaultdict = defaultdict(list)
        self._general_handlers: list = []
        self._queue_task = None
        self._timer_task = None

    async def run(self) -> None:
        self._active = True
        loop = asyncio.get_running_loop()
        self._queue_task = loop.create_task(self.__run_queue_process__())
        self._timer_task = loop.create_task(self.__run_timer_process__())

        tasks = [self._queue_task, self._timer_task]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            await self.stop()
        except Exception as e:
            await self.stop()


    async def __run_queue_process__(self) -> None:
        while self._active:
            try:
                event: Event = self._queue.get_nowait()
                self.__process__(event)
            except QueueEmpty:
                await asyncio.sleep(0.01)

    async def __run_timer_process__(self) -> None:
        pass

    def __process__(self, event: Event) -> None:
        if event.type in self._handlers:
            [handler(event.data) for handler in self._handlers[event.type]]
        if self._general_handlers:
            [handler(event.data) for handler in self._general_handlers]

    async def stop(self):
        """
        不直接设置_active标志，而是在队列最后插入一个stop标志，
        等待stop标志前的所有事件都处理完成。
        """
        self.register('stop', self.__stop__)
        await self.put(Event('stop'))

    def __stop__(self, data):
        self._active = False

    async def put(
            self,
            event: Event
        ) -> None:
        while True:
            try:
                self._queue.put_nowait(event)
                break
            except QueueFull:
                asyncio.sleep(0.01)

    def register(
            self,
            type: str,
            handler: Callable
        ) -> None:
        """
        Register a new handler function for a specific event type. Every
        function can only be registered once for each event type.
        """
        handler_list: list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(
            self,
            type: str,
            handler: Callable
        ) -> None:
        """
        Unregister an existing handler function from event engine.
        """
        handler_list: list = self._handlers[type]
        if handler in handler_list:
            handler_list.remove(handler)
        if not handler_list:
            self._handlers.pop(type)

    def register_general(
            self,
            handler: Callable
        ) -> None:
        """
        Register a new handler function for all event types. Every
        function can only be registered once for each event type.
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)
    
    def unregister_general(
            self,
            handler: Callable
        ) -> None:
        """
        Unregister an existing general handler function.
        """
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)