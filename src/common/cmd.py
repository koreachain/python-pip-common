import subprocess
from subprocess import CompletedProcess
from typing import Union


def out(argv: Union[str, list], *args, **kwargs) -> CompletedProcess[str]:
    result = subprocess.run(
        argv,
        *args,
        shell=True if isinstance(argv, str) else False,
        check=True,
        **kwargs
    )

    return result


def run(argv: Union[str, list], *args, **kwargs) -> CompletedProcess[str]:
    result = subprocess.run(
        argv,
        *args,
        shell=True if isinstance(argv, str) else False,
        check=True,
        capture_output=True,
        text=True,
        **kwargs
    )
    result.stdout = result.stdout.rstrip("\n")
    result.stderr = result.stderr.rstrip("\n")

    return result
