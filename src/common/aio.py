#!/usr/bin/env python3

import asyncio
import functools
import logging
import signal
import sys
import time
import traceback
from asyncio.exceptions import CancelledError
from asyncio.tasks import Task
from contextlib import suppress
from typing import Awaitable

import pudb
import uvloop
from aiodebug import log_slow_callbacks

from common import dbg

log = logging.getLogger(__name__)


class HandleSIGUSR1:
    """Write to a file the stack for all async tasks."""

    def __init__(self) -> None:
        self.trace: str = f"{time.strftime('%F-%R', time.localtime())}.trace"
        self.monitor: Task
        signal.signal(signal.SIGUSR1, self.handle_sigusr1)

    def handle_sigusr1(self, signum, frame):
        """Start or stop writing stacks on SIGUSR1."""
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


def init(coro: Awaitable, debug: bool = False) -> None:
    """Wrap call to asyncio.run(), use uvloop."""
    loop = uvloop.new_event_loop()

    if debug:
        loop.set_debug(enabled=debug)
    else:
        log_slow_callbacks.enable(0.1)

    HandleSIGUSR1()

    try:
        loop.run_until_complete(coro)
    except RuntimeError as e:
        if "Event loop stopped before Future completed." in str(e):
            log.warning(f"{type(e).__name__}: {e}")
            sys.exit(1)
        else:
            raise


def wrap(coro):
    """Handle exceptions from child coroutines."""

    @functools.wraps(coro)
    async def run_func(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except CancelledError:
            return
        except Exception as e:
            log.error(f"From task {coro.__name__}: {type(e).__name__}: {e}")

            asyncio.get_event_loop().stop()
            await asyncio.sleep(0)  # force uvloop to stop immediately

            if sys.excepthook is dbg.excepthook:
                traceback.print_exc()
                pudb.post_mortem()
            raise

    return run_func
