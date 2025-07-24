#!/usr/bin/env python3

import logging
import sys
import warnings
from typing import Tuple, Union

import fastlogging
import requests
from requests.exceptions import ConnectionError as NetworkError  # overwrites builtin
from requests.exceptions import HTTPError, Timeout
from tenacity import RetryCallState, retry
from tenacity.retry import retry_if_exception_type as retry_exc
from tenacity.stop import stop_after_attempt as attempts
from tenacity.stop import stop_after_delay as total_sec
from tenacity.wait import wait_exponential as exponential

if sys.version_info >= (3, 10, 0):
    HTTPErrors = int | tuple[int, ...]
else:
    HTTPErrors = Union[int, Tuple[()], Tuple[int]]

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)


class RetryableHTTPError(Exception):
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
    def _log_retries(state: RetryCallState):
        """Log all retries with debug level."""
        attempt = state.attempt_number
        assert state.next_action is not None
        seconds = int(state.next_action.sleep)
        e = state.outcome._exception  # type: ignore
        log.debug(f"Retry #{attempt} in {seconds}s: {type(e).__name__}: {e}")

    @retry(
        retry=retry_exc((NetworkError, RetryableHTTPError)),
        wait=exponential(multiplier=3, max=45),
        stop=attempts(1 + 5) | total_sec(120),
        before_sleep=_log_retries.__func__,
    )
    @retry(
        retry=retry_exc(Timeout),
        stop=attempts(3),
        before_sleep=_log_retries.__func__,
    )
    def request(self, method, url, *args, timeout=30, **kwargs):
        """Set timeout and retries for all HTTP methods."""
        reply = super().request(method, url, *args, timeout=timeout, **kwargs)

        try:
            reply.raise_for_status()
        except HTTPError as e:
            if reply.status_code in (408, 502, 503, 504) + self.include:
                raise RetryableHTTPError(e)
            else:
                raise

        return reply
