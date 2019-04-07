import os

import requests

from . import DefaultCacheImplBase
from .paths import debian_codename_map_path


class DistroCodenameMapsCache(DefaultCacheImplBase):
    @classmethod
    def _cache_file_path(cls):
        return debian_codename_map_path()

    @classmethod
    def _fetch_data(cls):
        # avoids circular import issues
        from .common import get_debian_releases

        rv = {}

        for suite in get_debian_releases():
            headers = {"Range": "bytes=0-512"}
            url = "https://ftp.fau.de/debian/dists/{}/Release".format(suite)
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            for line in response.text.splitlines():
                prefix = "Codename:"

                if line.startswith(prefix):
                    rv[suite] = line.split(prefix)[-1].strip()
                    break
            else:
                raise ValueError("could not find Release file for suite {} on Debian mirror".format(suite))

        return rv
