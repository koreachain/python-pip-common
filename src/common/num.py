#!/usr/bin/env python3

from math import isclose


def approx(a, b, rel=1e-9, abs=1e-12) -> bool:
    "Handle numbers close to 0 in math.isclose()."
    return isclose(a, b, rel_tol=rel, abs_tol=abs)
