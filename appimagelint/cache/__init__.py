from .._logging import make_logger


def _get_logger():
    return make_logger("cache")


from .exceptions import OutOfDateError
from .io import load_json, store_json
from .cache_base import CacheBase
from .json_cache_impl_base import JSONCacheImplBase
from .distro_codenames import DebianCodenameMapCache
from .package_version_maps import PackageVersionMapsCache


__all__ = ("OutOfDateError", "store_json", "load_json", "CacheBase",)
