#!/usr/bin/env python3

from shlex import quote

from common import cmd, own


def mail(subject: str, message: str, address: str = "26373564-goldencedar@users.noreply.gitlab.com") -> None:
    """Email using existing system MTA."""
    cmd.run(
        # if performance matters, shell=False won't start a new shell
        ["mail", "-s", f"[{own.hostname}] {quote(subject)}", address],
        input=message.encode(),
    )
