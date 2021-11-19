import subprocess
from subprocess import CompletedProcess
from typing import Any


def run(argv: Any[str, list], *args, **kwargs) -> CompletedProcess[str]:
    return subprocess.run(
        argv,
        *args,
        capture_output=True,
        shell=True if isinstance(argv, str) else False,
        check=True,
        text=True,
        **kwargs
    )
