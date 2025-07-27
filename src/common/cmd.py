#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from subprocess import CompletedProcess
from typing import Union

Args = Union[str, list[str]]


def run(argv: Args, *args, check=True, **kwargs) -> CompletedProcess[str]:
    """Run command and capture stdout and stderr."""
    result = subprocess.run(
        argv,
        *args,
        shell=True if isinstance(argv, str) else False,
        check=check,
        capture_output=True,
        text=True,
        **kwargs,
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
        **kwargs,
    )

    return result
