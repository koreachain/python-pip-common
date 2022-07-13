#!/usr/bin/env python3

import os
import time

import orjson
from fasteners import InterProcessReaderWriterLock

from common import url

session = url.Session()


def conv(base: str, quote: str) -> float:
    """Cache data from APILayer's Exchange Rates API for 8 hours."""

    # FIXME: global monthly limit, not per base currency: fix with USD as base
    limit = 250 // 30 * 60 * 60

    cache = f"/tmp/xr.{base.lower()}.json"
    cache_lock = InterProcessReaderWriterLock(cache)

    if os.path.exists(cache) and os.path.getmtime(cache) + limit >= time.time():
        with cache_lock.read_lock(), open(cache) as fd:
            data = orjson.loads(fd.read())
    else:
        reply = session.get(
            f"https://api.apilayer.com/exchangerates_data/latest?base={base}",
            headers={"apikey": "FUmdHFwAguPbLI8eWnhD8EbyAeYoOrQj"},
        )
        data = reply.json()

        with cache_lock.write_lock(), open(cache, "wb") as fd:
            fd.write(orjson.dumps(data))

    return data["rates"][quote]
