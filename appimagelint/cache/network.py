from functools import lru_cache
from typing import FrozenSet

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# These are temporary service or gateway failures. Do not retry client errors such as 404.
_RETRY_STATUS_CODES: FrozenSet[int] = frozenset((429, 500, 502, 503, 504))
_RETRY_COUNT = 3
WGET_RETRY_OPTIONS = (
    "--tries={}".format(_RETRY_COUNT + 1),
    "--waitretry=1",
    "--retry-on-http-error={}".format(",".join(str(code) for code in sorted(_RETRY_STATUS_CODES))),
)


def _make_retry() -> Retry:
    kwargs = {
        "total": _RETRY_COUNT,
        "status": _RETRY_COUNT,
        "connect": _RETRY_COUNT,
        "read": _RETRY_COUNT,
        "backoff_factor": 1,
        "status_forcelist": _RETRY_STATUS_CODES,
        "raise_on_status": False,
    }

    # get() is the only request function in this module, and GET is retried by default.
    return Retry(**kwargs)


@lru_cache(maxsize=1)
def _get_session() -> requests.Session:
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=_make_retry())
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get(url: str, **kwargs) -> requests.Response:
    """Perform a GET request with retries for transient HTTP and network failures."""
    return _get_session().get(url, **kwargs)
