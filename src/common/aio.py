#!/usr/bin/env python3

import asyncio
import functools
import logging
import signal
import sys
import threading
import time
from asyncio import CancelledError
from asyncio.tasks import Task
from contextlib import suppress
from typing import Coroutine

import aiodebug.log_slow_callbacks
import fastlogging
import pudb
import uvloop

from common import dbg

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)
    aiodebug.log_slow_callbacks.enable(0.1)


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


_main_thread = threading.current_thread() is threading.main_thread()
_loop_stopped = False

if _main_thread:
    HandleSIGUSR2()
else:
    log.warning("Import aio from the main thread: writing stacks on SIGUSR2 disabled")


def init(coro: Coroutine, debug: bool = False) -> None:
    """Wrap call to asyncio.run(), use uvloop."""
    uvloop.install()

    try:
        asyncio.run(coro, debug=debug)
    except Exception:
        # sys.exit() just exits the thread
        if _loop_stopped and _main_thread:
            sys.exit(1)
        else:
            raise  # also needed for pudb


def wrap(coro, warning=True):
    """Make scheduled tasks exceptions fatal, use create_task() if handling them."""

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
            log.exception(f"From task {coro.__name__}: {type(e).__name__}: {e}")

            global _loop_stopped
            _loop_stopped = True
            asyncio.get_event_loop().stop()
            await asyncio.sleep(0)  # force uvloop to stop immediately

            # asyncio_atexit is run after debugging when raised here!
            if sys.excepthook is dbg.excepthook:
                sys.excepthook = sys.__excepthook__
                pudb.post_mortem()
                return

            raise

    return run_func


def task(coro, *, name=None):
    """Schedule bg task, making its exceptions fatal."""
    return asyncio.create_task(wrap(coro, warning=False)(), name=name)
