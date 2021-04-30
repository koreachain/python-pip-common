#!/usr/bin/env python3

import sys
import traceback

import pudb


def pudb_on_exceptions() -> None:
    """Launch a pudb breakpoint on unhandled exceptions."""
    sys.excepthook = excepthook


def excepthook(exc_type, exc_val, exc_tb):
    """Print traceback and launch post-mortem debugging."""
    traceback.print_tb(exc_tb)
    pudb.post_mortem(exc_tb)
