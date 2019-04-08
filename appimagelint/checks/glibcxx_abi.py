from . import GnuAbiCheckBase
from ..cache.package_version_maps import DebianGlibcxxVersionsCache, UbuntuGlibcxxVersionsCache
from ..models import AppImage
from ..services import GnuLibVersionSymbolsFinder


class GlibcxxABICheck(GnuAbiCheckBase):
    def __init__(self, appimage: AppImage):
        super().__init__(appimage)

    @staticmethod
    def _library_id():
        return "glibc"

    @staticmethod
    def name():
        return "GNU libstdc++ ABI check"

    @classmethod
    def _detect_versions_in_file(cls, path):
        return GnuLibVersionSymbolsFinder.detect_gnu_lib_versions("GLIBCXX_", path)

    @classmethod
    def _get_debian_versions_map(cls):
        return DebianGlibcxxVersionsCache.get_data()

    @classmethod
    def _get_ubuntu_versions_map(cls):
        return UbuntuGlibcxxVersionsCache.get_data()
