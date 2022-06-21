#!/usr/bin/env python3

import json
import os
import time

from fasteners import InterProcessReaderWriterLock

from common import url

session = url.Session()


def main(base: str, quote: str) -> float:
    """Cache data from APILayer's Exchange Rates API for 8 hours."""

    # FIXME: global monthly rate limit, not per base currency
    limit = 250 // 30 * 60 * 60

    cache = f"{os.environ['XDG_RUNTIME_DIR']}/xr.{base.lower()}.json"
    rw_lock = InterProcessReaderWriterLock(cache)

    if os.path.exists(cache) and os.path.getmtime(cache) + limit >= time.time():
        with rw_lock.read_lock():
            with open(cache) as fd:
                data = json.load(fd)
    else:
        reply = session.get(
            f"https://api.apilayer.com/exchangerates_data/latest?base={base}",
            headers={"apikey": "FUmdHFwAguPbLI8eWnhD8EbyAeYoOrQj"},
        )
        data = reply.json()

        with rw_lock.write_lock():
            with open(cache, "w") as fd:
                json.dump(data, fd)

    return data["rates"][quote]


def usd(quote: str = "BRL") -> float:
    """Return exchange rates quoted against USD."""
    return main("USD", quote)


def eur(quote: str = "BRL") -> float:
    """Return exchange rates quoted against EUR."""
    return main("EUR", quote)


def brl(quote: str = "USD") -> float:
    """Return exchange rates quoted against BRL."""
    return main("BRL", quote)
