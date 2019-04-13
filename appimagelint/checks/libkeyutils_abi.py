import logging

from . import GnuAbiCheckBase
from .._logging import make_logger
from ..cache.package_version_maps import DebianGlibcVersionsCache, UbuntuGlibcVersionsCache
from ..models import AppImage
from ..services import GnuLibVersionSymbolsFinder


class LibkeyfileABICheck(GnuAbiCheckBase):
    def __init__(self, appimage: AppImage):
        super().__init__(appimage)

    @staticmethod
    def get_logger() -> logging.Logger:
        return make_logger("libkeyfile_abi_check")

    @staticmethod
    def name():
        return "libkeyfile ABI check"

    @classmethod
    def _detect_versions_in_file(cls, path):
        return GnuLibVersionSymbolsFinder.detect_gnu_lib_versions("KEYFILE_", path)

    @classmethod
    def _get_debian_versions_map(cls):
        return DebianGlibcVersionsCache.get_data()

    @classmethod
    def _get_ubuntu_versions_map(cls):
        return UbuntuGlibcVersionsCache.get_data()
