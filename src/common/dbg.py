#!/usr/bin/env python3

import logging
import sys
from functools import partial

import fastlogging
import pudb

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)


def pudb_on_exceptions() -> None:
    """Launch a pudb breakpoint on unhandled exceptions."""
    sys.excepthook = partial(excepthook, sys.excepthook)


def excepthook(prev_hook, exc_type, exc_val, exc_tb):
    """Print traceback and launch post-mortem debugging."""
    prev_hook(exc_type, exc_val, exc_tb)

    if issubclass(exc_type, KeyboardInterrupt):
        return

    pudb.post_mortem(exc_tb, exc_type, exc_val)
