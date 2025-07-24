#!/usr/bin/env python3

import logging
import os
import time

import fastlogging
import orjson
import requests
from fasteners import InterProcessReaderWriterLock

from common import url

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)


class ExchangeRates:
    def __init__(self, apikey: str):
        self.apikey = apikey
        self.session = url.Session()


    def _read_cached(self, cache, cache_lock):
        with cache_lock.read_lock(), open(cache) as fd:
            return orjson.loads(fd.read())


    def conv(self, base: str, quote: str, retry=True) -> float:
        """Cache data from APILayer's Exchange Rates API for 8 hours."""

        # FIXME: global monthly limit, not per base currency: fix with USD as base
        limit = 250 // 30 * 60 * 60

        cache = f"/tmp/xr.{base.lower()}.json"
        cache_lock = InterProcessReaderWriterLock(cache)

        if os.path.exists(cache) and os.path.getmtime(cache) + limit >= time.time():
            data = self._read_cached(cache, cache_lock)
        else:
            try:
                reply = (self.session if retry else requests).get(
                    f"https://api.apilayer.com/exchangerates_data/latest?base={base}",
                    headers={"apikey": self.apikey},
                    timeout=5,
                )
            except Exception as e:
                if os.path.exists(cache):
                    log.warning(f"{type(e).__name__}: {e}, use cached {base}/{quote} rate")
                    data = self._read_cached(cache, cache_lock)
                else:
                    log.error(f"Failed to fetch {base}/{quote} exchange rate, not cached")
                    raise
            else:
                data = reply.json()

                with cache_lock.write_lock(), open(cache, "wb") as fd:
                    fd.write(orjson.dumps(data))

        return data["rates"][quote]
