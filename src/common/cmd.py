import subprocess
from subprocess import CompletedProcess


def run(argv: str | list[str], *args, **kwargs) -> CompletedProcess[str]:
    """Run command and capture stdout and stderr."""
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


def tty(argv: str | list[str], *args, **kwargs) -> CompletedProcess[str]:
    """Run command and output to stdout and stderr."""
    result = subprocess.run(
        argv,
        *args,
        shell=True if isinstance(argv, str) else False,
        check=True,
        **kwargs
    )

    return result
