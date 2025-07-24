#!/usr/bin/env python3

from time import time, time_ns


# Optimized time conversion functions
S = lambda x: x
M = lambda x: x * 60
H = lambda x: x * 60 * 60
d = lambda x: x * 60 * 60 * 24
w = lambda x: x * 60 * 60 * 24 * 7
m = lambda x: x * 60 * 60 * 24 * 30
y = lambda x: x * 60 * 60 * 24 * 365


# Time functions for various units
ts = lambda: int(time())
ms = lambda: int(time_ns() / 1_000_000)
us = lambda: int(time_ns() / 1_000)
ns = time_ns


def sec(s: int) -> str:
    """Convert elapsed time in seconds to timestamp."""
    M, S = divmod(s, 60)
    H, M = divmod(M, 60)
    D, H = divmod(H, 24)
    parts = []
    if D > 0:
        parts.append(f"{D}d")
    if H > 0:
        parts.append(f"{H}h")
    if M > 0:
        parts.append(f"{M}m")
    if S > 0:
        parts.append(f"{S}s")
    return ''.join(parts)
