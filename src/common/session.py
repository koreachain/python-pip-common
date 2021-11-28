#!/usr/bin/env python3

import sys
import warnings
from typing import Tuple, Union

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout
from retrying import retry


if sys.version_info >= (3, 9, 0):
    HTTPErrors = int | tuple[int, ...]
else:
    HTTPErrors = Union[int, Tuple[()], Tuple[int]]


class RetryError(Exception):
    """HTTP errors that can be safely retried."""


class Session(requests.Session):
    """Set better defaults for requests.Session()."""

    def __init__(self, *args, insist: HTTPErrors = (), secure: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers.update({"User-Agent": "Mozilla/5.0 Gecko/20100101"})
        self.include = (insist,) if isinstance(insist, int) else insist

        if not secure:
            self.verify = False
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    @staticmethod
    def _retry_exc(exception: Exception) -> bool:
        """List exceptions that should be retried."""
        return isinstance(exception, (ConnectionError, Timeout, RetryError))

    @retry(retry_on_exception=_retry_exc.__func__, stop_max_attempt_number=3)
    def request(self, method, url, *args, timeout=30, **kwargs):
        """Set timeout and retries for all HTTP methods."""
        reply = super().request(method, url, *args, timeout=timeout, **kwargs)

        try:
            reply.raise_for_status()
        except HTTPError as e:
            if reply.status_code in (408, 502, 503, 504) + self.include:
                raise RetryError(e)
            else:
                raise

        return reply
