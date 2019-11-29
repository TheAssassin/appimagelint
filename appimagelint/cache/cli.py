from appimagelint.cache import *


def bundle_metadata():
    """
    Downloads files and caches them inside the appimagelint package directory to provide a fallback cache location.
    """

    for cache in DebianCodenameMapCache, PackageVersionMapsCache, AppImageRuntimeCache:
        cache.update_now(save_to_bundled_cache=True)
