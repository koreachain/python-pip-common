import subprocess
from subprocess import CompletedProcess
from typing import Any


def run(argv: Any[str, list], *args, **kwargs) -> CompletedProcess[str]:
    result = subprocess.run(
        argv,
        *args,
        capture_output=True,
        shell=True if isinstance(argv, str) else False,
        check=True,
        text=True,
        **kwargs
    )
    result.stdout = result.stdout.strip()
    result.stderr = result.stderr.strip()

    return result
