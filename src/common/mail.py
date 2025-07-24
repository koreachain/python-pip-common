#!/usr/bin/env python3

import logging
from inspect import cleandoc
from pathlib import Path
from shlex import quote

import fastlogging

from common import cmd, own

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)

recipient = Path("/var/local/.mail").read_text().strip()

def mail(subject: str, message: str, address: str = recipient) -> None:
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
