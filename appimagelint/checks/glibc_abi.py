from . import GnuAbiCheckBase
from ..cache.package_version_maps import DebianGlibcVersionsCache, UbuntuGlibcVersionsCache, RockyLinuxGlibcVersionsCache
from ..models import AppImage


class GlibcABICheck(GnuAbiCheckBase):
    def __init__(self, appimage: AppImage):
        super().__init__(appimage)

    @staticmethod
    def _library_id():
        return "glibc"

    @staticmethod
    def name():
        return "GNU libc ABI check"

    @classmethod
    def _detect_versions_in_file(cls, path):
        return cls._gnu_lib_versions_symbol_finder.detect_gnu_lib_versions("GLIBC_", path)

    @classmethod
    def _get_debian_versions_map(cls):
        return DebianGlibcVersionsCache.get_data()

    @classmethod
    def _get_ubuntu_versions_map(cls):
        return UbuntuGlibcVersionsCache.get_data()

    @classmethod
    def _get_rocky_linux_versions_map(cls):
        return RockyLinuxGlibcVersionsCache.get_data()
