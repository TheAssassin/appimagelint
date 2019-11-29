from typing import Callable, Union, Mapping, Iterable

from . import CacheBase, JSONFileCacheBase
from .common import get_debian_package_versions_map, get_debian_glibcxx_versions_map, get_ubuntu_glibcxx_versions_map, \
    get_ubuntu_package_versions_map


def _make_cache_class(distro: str, package: str, get_map_callback: Callable, cache_file_name: str):
    class _PackageVersionMap(JSONFileCacheBase):
        @classmethod
        def _cache_file_name(cls) -> str:
            return cache_file_name

        @classmethod
        def _fetch_data(cls):
            cls._get_logger().info("Fetching {} version data for {}".format(package, distro))
            return get_map_callback()

    return _PackageVersionMap


DebianGlibcVersionsCache = _make_cache_class(
    "debian", "glibc", lambda: get_debian_package_versions_map("glibc"), "debian_glibc_versions.json"
)
DebianGlibcxxVersionsCache = _make_cache_class(
    "debian", "glibcxx", get_debian_glibcxx_versions_map, "debian_glibcxx_versions.json"
)
UbuntuGlibcVersionsCache = _make_cache_class(
    "ubuntu", "glibc", lambda: get_ubuntu_package_versions_map("glibc"), "ubuntu_glibc_versions.json"
)
UbuntuGlibcxxVersionsCache = _make_cache_class(
    "ubuntu", "glibcxx", get_ubuntu_glibcxx_versions_map, "ubuntu_glibcxx_versions.json"
)


# "aggregator" for the other caches
# can be used for convenient updates
# does not return any data
class PackageVersionMapsCache(CacheBase):
    _classes = [
        DebianGlibcVersionsCache,
        DebianGlibcxxVersionsCache,
        UbuntuGlibcVersionsCache,
        UbuntuGlibcxxVersionsCache
    ]

    @classmethod
    def update_now(cls, save_to_bundled_cache: bool = False):
        for c in cls._classes:
            c.update_now(save_to_bundled_cache=save_to_bundled_cache)

    @classmethod
    def get_data(cls, raise_on_error=False) -> Union[Mapping, Iterable]:
        raise NotImplementedError

    @classmethod
    def update_if_necessary(cls):
        for c in cls._classes:
            c.get_data()
