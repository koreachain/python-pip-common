#!/usr/bin/env python3

from math import isclose
from typing import Optional, Type

import numpy as np


def approx(a: float, b: float, rel: float = 1e-9, abs: float = 1e-12) -> bool:
    """Handle numbers close to 0 in math.isclose()."""
    return isclose(a, b, rel_tol=rel, abs_tol=abs)


def between(value: float, a: float, b: float) -> bool:
    """Check if value is between unknown numbers a and b."""
    return (value - a) * (value - b) <= 0


def exp_range(
    start: float,
    stop: float,
    count: int,
    ntype: Optional[Type[float]] = None,
    round: Optional[int] = None,
    unique: bool = False,
) -> tuple:
    """Return exponential range of ints or floats."""
    if not ntype:
        ntype = int if isinstance(start, int) and isinstance(stop, int) else float

    scale = np.geomspace(start, stop, count)

    if ntype is int:
        scale = np.around(scale).astype(int)
    elif round:
        scale = np.around(scale, decimals=round)

    if unique:
        scale = np.unique(scale)

    native = tuple(x.item() for x in scale)
    return native
