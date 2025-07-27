#!/usr/bin/env python3

import asyncio
import functools
import inspect
import logging
import signal
import sys
import threading
import time
import warnings
from asyncio import CancelledError
from asyncio import TimeoutError as AsyncioTimeout
from asyncio.tasks import Task
from contextlib import suppress
from typing import Awaitable, Callable, Optional

import fastlogging
import uvloop

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
    _debugging = log.level <= fastlogging.DEBUG
else:
    log = logging.getLogger(__name__)
    _debugging = log.isEnabledFor(logging.DEBUG)  # `log.level` is error prone

_loop_stopped = False


class AtExit:
    """async atexit, accepts async and blocking callbacks."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._tasks = []

    def register(self, func: Callable, *args, **kwargs) -> None:
        """Register function to run before loop is stopped."""
        self._tasks.append((func, args, kwargs))

    async def run(self) -> None:
        """Run aio.atexit() callbacks, in reverse order."""
        # ignore additional keyboard interrupts (ctrl+c 2x)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # lock to ensure all tasks are awaited before stop()
        async with self._lock:
            while self._tasks:
                func, args, kwargs = self._tasks.pop()
                try:
                    # handle blocking callbacks too
                    result = func(*args, **kwargs)
                    if inspect.isawaitable(result):
                        await result
                except Exception as e:
                    log.error(f"{func.__name__}: {type(e).__name__}: {e}")


class HandleSIGUSR2:
    """Write to a file the stack for all async tasks."""

    def __init__(self) -> None:
        self.trace: str = f"{time.strftime('%F-%R', time.localtime())}.trace"
        self.monitor: Task
        signal.signal(signal.SIGUSR2, self.handle_sigusr2)

    def handle_sigusr2(self, signum, frame):
        """Start or stop writing stacks on SIGUSR2."""
        try:
            self.monitor
        except AttributeError:
            log.info(f'Writing stack trace to "{self.trace}"')
            self.monitor = asyncio.create_task(self.do_monitor())
        else:
            log.info("Stopping writing of the stack trace")
            self.monitor.cancel()

    async def do_monitor(self) -> None:
        """Write stack of running tasks periodically."""
        with suppress(CancelledError):
            while True:
                with open(self.trace, "a") as fd:
                    for task in asyncio.all_tasks():
                        if task is not self.monitor:
                            task.print_stack(limit=5, file=fd)
                    print(file=fd)
                await asyncio.sleep(1)


atexit = AtExit()

if threading.current_thread() is threading.main_thread():
    HandleSIGUSR2()
else:
    log.warning("Import aio from the main thread: writing stacks on SIGUSR2 disabled")


def init(
    coro: Awaitable, debug: Optional[bool] = None
) -> None:  # debug has its own uses
    """Wrap call to asyncio.run(), use uvloop."""
    loop = uvloop.new_event_loop()

    if (_debugging if debug is None else debug) or loop.get_debug():  # via cli or env
        loop.set_debug(True)
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
        warnings.filterwarnings("always", category=ResourceWarning)

    try:
        loop.run_until_complete(coro)
    except Exception as e:
        # sys.exit() will exit the current thread
        if threading.current_thread() is threading.main_thread() and _loop_stopped:
            sys.exit(1)
        else:
            log.error(f"{type(e).__name__}: {e}")
            raise  # also needed to trigger pudb
    finally:
        if not _loop_stopped:
            loop.run_until_complete(atexit.run())


_bg_tasks = set()


def ref(_task: Task) -> Task:
    # use a strong reference, to stop a task from disappearing mid-execution:
    # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
    _bg_tasks.add(_task)
    _task.add_done_callback(_bg_tasks.discard)

    return _task


def wrap(coro, warning=True):
    """Make scheduled tasks exceptions fatal, use create_task() for handling them."""

    # exceptions from child coroutines are not propagated to parent task when wrapped
    if warning:
        log.warning(f"@aio.wrap is deprecated: start background tasks with aio.task()")

    @functools.wraps(coro)
    async def run_func(*args, **kwargs):
        decorated: bool = callable(coro)
        try:
            if decorated:
                return await coro(*args, **kwargs)
            else:
                return await coro
        except CancelledError:
            return
        except Exception as e:
            log.error(f"From task {coro.__name__}: {type(e).__name__}: {e}")

            await atexit.run()

            global _loop_stopped
            _loop_stopped = True
            asyncio.get_event_loop().stop()
            await asyncio.sleep(0)  # yield so uvloop can stop immediately

            sys.excepthook(*sys.exc_info())  # type: ignore

    return run_func


def task(coro, *, name=None):
    """Schedule bg task. Makes its exceptions fatal. Unhides print() from bg tasks."""
    return ref(asyncio.create_task(wrap(coro, warning=False)(), name=name))


class Lock(asyncio.Lock):
    def __init__(self):
        super().__init__()

    async def acquire(self, wait=True) -> bool:
        """Acquire the lock. If wait is set, block, else return False."""
        if wait:
            return await super().acquire()

        if self.locked():
            return False

        # workaround any self.locked() race conditions and avoid blocking
        try:
            return await asyncio.wait_for(super().acquire(), timeout=1e-9)
        except AsyncioTimeout:
            return False
