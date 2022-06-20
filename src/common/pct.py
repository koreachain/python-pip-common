#!/usr/bin/env python3


def get(amount: float, value: float) -> float:
    """Calculate percentage from value."""
    return value / 100 * amount


def dec(old: float, new: float) -> float:
    """Calculate percentage decrease."""
    return (old - new) / old * 100


def inc(old: float, new: float) -> float:
    """Calculate percentage increase."""
    return (new - old) / old * 100


def add(amount: float, value: float) -> float:
    """Add percentage to value."""
    return value + (value / 100 * amount)


def sub(amount: float, value: float) -> float:
    """Subtract percentage from value."""
    return value - (value / 100 * amount)


def afs(amount: float, value: float) -> float:
    """Add percentage for subtraction."""
    return value * 100 / (100 - amount)
