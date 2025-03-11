#!/usr/bin/env python3

import logging
from inspect import cleandoc
from shlex import quote

import fastlogging

from common import cmd, own

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)


def mail(subject: str, message: str, address: str) -> None:
    """Email using existing system MTA."""
    try:
        cmd.run(
            # if performance matters, shell=False won't start a new shell
            ["mail", "-s", f"[{own.hostname}] {quote(subject)}", address],
            input=cleandoc(message),
        )
    except Exception as e:
        log.warning(
            cleandoc(
                f"""
                {type(e).__name__}: {e} - dumping intended message:
                {subject}
                {cleandoc(message)}
                """
            )
        )
        return
