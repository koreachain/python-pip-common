#!/usr/bin/env python3

import logging
from inspect import cleandoc
from shlex import quote
from shutil import which

from common import cmd, own

log = logging.getLogger(__name__)


def mail(subject: str, message: str, address: str = "26373564-goldencedar@users.noreply.gitlab.com") -> None:
    """Email using existing system MTA."""
    if not which("mail"):
        log.warning(
            cleandoc(
                f"""
                Command "mail" not found, dumping intended message:
                {subject}
                {message}
                """
            )
        )
        return

    cmd.run(
        # if performance matters, shell=False won't start a new shell
        ["mail", "-s", f"[{own.hostname}] {quote(subject)}", address],
        input=cleandoc(message).encode(),
    )
