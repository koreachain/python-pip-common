#!/usr/bin/env python3

from math import isclose
from typing import Type

import numpy as np


def approx(
    a: int | float, b: int | float, rel: float = 1e-9, abs: float = 1e-12
) -> bool:
    """Handle numbers close to 0 in math.isclose()."""
    return isclose(a, b, rel_tol=rel, abs_tol=abs)


def exp_range(
    start: int | float,
    stop: int | float,
    count: int,
    ntype: Type[int | float] | None = None,
    truncate: int | None = None,
    unique: bool = False,
) -> tuple[int | float, ...]:
    """Return exponential range of ints or floats."""
    if not ntype:
        ntype = int if isinstance(start, int) and isinstance(stop, int) else float

    scale = np.geomspace(start, stop, count)

    if ntype is int:
        scale = np.around(scale).astype(int)
    elif truncate:
        scale = np.around(scale, decimals=truncate)

    if unique:
        scale = np.unique(scale)

    native = tuple(x.item() for x in scale)
    return native
