from typing import Callable, Union, Mapping, Iterable

from . import CacheBase, JSONCacheImplBase
from .common import get_debian_package_versions_map, get_debian_glibcxx_versions_map, get_ubuntu_glibcxx_versions_map, \
    get_ubuntu_package_versions_map
from .paths import ubuntu_glibcxx_versions_data_path, debian_glibcxx_versions_data_path, \
    debian_glibc_versions_data_path, ubuntu_glibc_versions_data_path


def _make_cache_class(distro: str, get_map_callback: Callable, file_path: str):
    class _PackageVersionMap(JSONCacheImplBase):
        @classmethod
        def _cache_file_path(cls):
            return file_path

        @classmethod
        def _fetch_data(cls):
            cls._get_logger().info("Fetching version data for {}".format(distro))
            return get_map_callback()

    return _PackageVersionMap


DebianGlibcVersionsCache = _make_cache_class(
    "debian", lambda: get_debian_package_versions_map("glibc"), debian_glibc_versions_data_path()
)
DebianGlibcxxVersionsCache = _make_cache_class(
    "debian", get_debian_glibcxx_versions_map, debian_glibcxx_versions_data_path()
)
UbuntuGlibcVersionsCache = _make_cache_class(
    "ubuntu", lambda: get_ubuntu_package_versions_map("glibc"), ubuntu_glibc_versions_data_path()
)
UbuntuGlibcxxVersionsCache = _make_cache_class(
    "ubuntu", get_ubuntu_glibcxx_versions_map, ubuntu_glibcxx_versions_data_path()
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
    def force_update(cls):
        for c in cls._classes:
            c.force_update()

    @classmethod
    def get_data(cls, raise_on_error=False) -> Union[Mapping, Iterable]:
        raise NotImplementedError

    @classmethod
    def update_if_necessary(cls):
        for c in cls._classes:
            c.get_data()
