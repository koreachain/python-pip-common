#!/usr/bin/env python3

import requests
import warnings
from retrying import retry


class RetryError(Exception):
    """An HTTP error that can be safely retried."""


class Session(requests.Session):
    """Set better defaults for requests.Session()."""

    def __init__(self, *args, secure=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers.update({"User-Agent": "Mozilla/5.0 Gecko/20100101"})

        if not secure:
            self.verify = False
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    @staticmethod
    def _retry_exceptions(exception: Exception) -> bool:
        """List exceptions that should be retried."""
        return isinstance(
            exception,
            (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                RetryError,
            ),
        )

    @retry(retry_on_exception=_retry_exceptions, stop_max_attempt_number=3)
    def request(self, method, url, *args, timeout=30, **kwargs):
        """Set timeout and retries for all HTTP methods."""
        reply = super().request(method, url, *args, timeout=timeout, **kwargs)

        try:
            reply.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if reply.status_code in (408, 502, 503, 504):
                raise RetryError(e)
            else:
                raise

        return reply
