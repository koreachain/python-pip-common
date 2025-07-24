#!/usr/bin/env python3

import builtins
import sys
from typing import Optional

from box import Box
from docopt import docopt

if sys.version_info >= (3, 9, 0):
    Doc = str | None
else:
    Doc = Optional[str]


def path(name: str) -> str:
    """Verify if given filesystem path is accessible."""
    try:
        with open(name):
            pass
    except IOError as e:
        raise TypeError(f"{type(e).__name__}: {e}")
    else:
        return name


def parse(doc: Doc | None = None, names: dict | None = None) -> Box:
    """Parse options as described in given __doc__."""
    assert doc or names
    if not doc:
        doc = names["__doc__"]

    assert isinstance(doc, str)
    parser = docopt(doc)

    tags = {}
    x = None
    for line in doc.splitlines():
        line = line.strip()

        if line == "Options:":
            x = "opts"
            continue
        elif line in ("Commands:", "Arguments:"):
            x = "args"
            continue
        elif not line:
            x = None
            continue

        if x == "opts":
            tag = None
            for word in line.split():
                if word.startswith("-") and word in parser:
                    tag = word.lstrip("-")
                elif all(x in word for x in ("<", ">", ":")):
                    val = word.strip("<>").split(":")[1]
                    assert tag is not None
                    tags.update({tag: val})
        elif x == "args":
            for word in line.split():
                if all(x in word for x in ("<", ">", ":")):
                    tag, val = word.strip("<>").split(":")
                    tags.update({tag: val})

    caller_globals = names or {}
    builtins_dict = vars(builtins)
    args = {}
    for key, value in parser.items():
        name = key.lstrip("-").strip("<>").split(":")[0]
        if name in tags and value is not None:
            value = (caller_globals.get(tags[name]) or builtins_dict[tags[name]])(value)
        args[name.replace("-", "_")] = value

    return Box(args, frozen_box=True)
