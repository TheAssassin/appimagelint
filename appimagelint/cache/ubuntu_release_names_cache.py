import requests

from appimagelint.cache import JSONFileCacheBase


class UbuntuReleaseNamesCache(JSONFileCacheBase):
    @classmethod
    def _cache_file_name(cls) -> str:
        return "ubuntu_release_names.json"

    @classmethod
    def _fetch_data(cls):
        response = requests.get("https://api.launchpad.net/devel/ubuntu/series")
        response.raise_for_status()

        data = response.json()

        supported_releases = filter(lambda r: r["supported"], data["entries"])
        releases = [release["displayname"].lower() for release in supported_releases]

        return releases
