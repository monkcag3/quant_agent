
from decimal import Decimal
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
import asyncio
import contextlib
import decimal
import logging
import uuid
import warnings


class TaskGroup:
    def __init__(self):
        self._tasks = []
        self._exiting = False

    async def __aenter__(self) -> "TaskGroup":
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        self._exiting = True

        try:
            if not exc_type:
                await asyncio.gather(*self._tasks)
        finally:
            pending = self._cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

    def _cancel(self) -> List[asyncio.Task]:
        pending = [task for task in self._tasks if not task.done()]
        for task in pending:
            if not task.done():
                task.cancel()
        return pending
    
    def create_task(self, core) -> asyncio.Task:
        assert not self._exiting
        ret = asyncio.create_task(core)
        self._tasks.append(ret)
        return ret
    
    def cancel(self):
        self._cancel()


class TaskPool:
    """
    A class for managing a pool of asyncio tasks.
    """
    def __init__(
        self,
        max_tasks: int,
        max_queue_size: Optional[int] = None,
    ):
        assert max_tasks > 0, "Invalid max_tasks"
        assert max_queue_size is None or max_queue_size > 0, "Invalid max_queue_size"

        self._max_tasks = max_tasks
        self._queue = LazyProxy(
            lambda: asyncio.Queue(maxsize=max_tasks if max_queue_size is None else max_queue_size)
        )
        self._tasks: Dict[str, asyncio.Task] = {}
        self._queue_timeout = 1.0
        self._active = 0

    @property
    def idle(self) -> bool:
        return self._active == 0 and self._queue.empty()
    
    async def push(self, coroutine_func: Callable[[], Awaitable[Any]]):
        await self._queue.put(coroutine_func)

        idle_tasks = len(self._tasks) - self._active
        if idle_tasks == 0 and len(self._tasks) < self._max_tasks:
            task_name = uuid.uuid4().hex
            task = asyncio.create_task(self._task_main(task_name))
            if not task.done() and task_name not in self._tasks:
                self._tasks[task_name] = task

    def cancel(self):
        for task in self._tasks.values():
            task.cancel()

        while self._queue.qsize():
            self._queue.get_nowait()
            self._queue.task_done()

    async def wait(self, timeout: Optional[Union[int, float]] = None) -> bool:
        ret = False
        try:
            await asyncio.wait_for(self._queue.join(), timeout=timeout)
            ret = True
        except asyncio.TimeoutError:
            pass
        return ret

    async def _task_main(self, task_name: str):
        current_task = asyncio.current_task()
        if current_task not in self._tasks:
            assert current_task is not None
            self._tasks[task_name] = current_task

        try:
            eof = False
            while not eof:
                try:
                    coro_func = await asyncio.wait_for(self._queue.get(), timeout=self._queue_timeout)
                except asyncio.TimeoutError:
                    eof = self._queue.empty()
                    continue
                try:
                    self._active += 1
                    await coro_func()
                except Exception:
                    pass
                finally:
                    self._active -= 1
                    self._queue.task_done()
        finally:
            self._tasks.pop(task_name)

    
@contextlib.contextmanager
def no_raise(logger: logging.Logger, msg: str, **kwargs):
    try:
        yield
    except Exception as e:
        log_args = {"exception": e}
        log_args.update(kwargs)
        logger.exception(msg, **log_args)


def round_decimal(value: Decimal, precision: int, rounding=None) -> Decimal:
    return value.quantize(Decimal(f"1e-{precision}"), rounding=rounding)

def truncate_decimal(value: Decimal, precision: int) -> Decimal:
    return round_decimal(value, precision, rounding=decimal.ROUND_DOWN)

def deprecation_warning(msg: str):
    warnings.warn(msg, DeprecationWarning, stacklevel=2)

def classpath(obj: object):
    cls = obj.__class__
    module = cls.__module__
    parts = [str(module), cls.__qualname__] if module else [cls.__qualname__]
    return ".".join(parts)

class LazyProxy:
    def __init__(self, factory):
        self._factory = factory
        self._obj = None

    @property
    def initialized(self):
        return self._obj is not None

    @property
    def obj(self):
        if self._obj is None:
            self._obj = self._factory()
        return self._obj

    def __getattr__(self, name):
        return getattr(self.obj, name)