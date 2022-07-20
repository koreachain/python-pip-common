#!/usr/bin/env python3


def sec(s: int) -> str:
    """Convert elapsed time in seconds to timestamp."""
    M, S = divmod(s, 60)
    H, M = divmod(M, 60)
    D, H = divmod(H, 24)
    return f"{D:d}d{H:02d}h{M:02d}m{S:02d}s"
