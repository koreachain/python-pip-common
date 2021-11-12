#!/usr/bin/env python3

import requests
from retrying import retry
from requests.packages.urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning


class RetryError(Exception):
    pass


class Session(requests.Session):
    def __init__(self, *args, secure=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers.update({"User-Agent": "Mozilla/5.0 Gecko/20100101"})

        if not secure:
            self.verify = False
            disable_warnings(category=InsecureRequestWarning)

    def _retry_exceptions(exception):
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
        reply = super().request(method, url, *args, timeout=timeout, **kwargs)

        try:
            reply.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if reply.status_code in (408, 502, 503, 504):
                raise RetryError(e)
            else:
                raise

        return reply
