#!/usr/bin/env python3

import functools
from types import SimpleNamespace


@functools.singledispatch
def ns(obj):
    """Return created SimpleNamespace object."""
    return obj


@ns.register(dict)
def _wrap_dict(obj: dict) -> SimpleNamespace:
    """Create namespaces from dict objects."""
    return SimpleNamespace(**{k: ns(v) for k, v in obj.items()})


@ns.register(list)
def _wrap_list(obj: list) -> list:
    """Include lists in namespace recursion."""
    return [ns(v) for v in obj]
