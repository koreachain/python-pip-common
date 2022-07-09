#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from subprocess import CompletedProcess
from typing import List, Union

if sys.version_info >= (3, 9, 0):
    Args = str | list[str]
else:
    Args = Union[str, List[str]]


def run(argv: Args, *args, check=True, **kwargs) -> CompletedProcess[str]:
    """Run command and capture stdout and stderr."""
    result = subprocess.run(
        argv,
        *args,
        shell=True if isinstance(argv, str) else False,
        check=check,
        capture_output=True,
        text=True,
        **kwargs
    )
    result.stdout = result.stdout.rstrip("\n")
    result.stderr = result.stderr.rstrip("\n")

    return result


def tty(argv: Args, *args, check=True, **kwargs) -> CompletedProcess[str]:
    """Run command and output to stdout and stderr."""
    result = subprocess.run(
        argv,
        *args,
        shell=True if isinstance(argv, str) else False,
        check=check,
        **kwargs
    )

    return result
