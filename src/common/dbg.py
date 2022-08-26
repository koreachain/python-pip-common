#!/usr/bin/env python3

import logging
import sys
import traceback

import fastlogging
import pudb

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)


def pudb_on_exceptions() -> None:
    """Launch a pudb breakpoint on unhandled exceptions."""
    if sys.excepthook is not sys.__excepthook__:
        log.warning("sys.excepthook was already modified, overwriting…")
    sys.excepthook = excepthook


def excepthook(exc_type, exc_val, exc_tb):
    """Print traceback and launch post-mortem debugging."""
    traceback.print_tb(exc_tb)
    pudb.post_mortem(exc_tb)
