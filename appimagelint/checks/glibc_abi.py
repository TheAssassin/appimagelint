import json
import logging
import shlex
import subprocess
from typing import Iterator

import packaging.version

from appimagelint.cache import load_json
from appimagelint.services.gnu_lib_versions_symbol_finder import GnuLibVersionSymbolsFinder
from ..services import BinaryWalker
from ..models import AppImage, TestResult
from .._logging import make_logger
from ..setup.paths import debian_glibc_versions_data_path, debian_codename_map_path, ubuntu_glibc_versions_data_path

from . import CheckBase


class GlibcABICheck(CheckBase):
    def __init__(self, appimage: AppImage):
        super().__init__(appimage)

    @staticmethod
    def get_logger() -> logging.Logger:
        return make_logger("glibc_abi_check")

    @staticmethod
    def name():
        return "GNU libc ABI check"

    @classmethod
    def _detect_glibc_versions(cls, path):
        return GnuLibVersionSymbolsFinder.detect_gnu_lib_versions("GLIBC_", path)

    def run(self) -> Iterator[TestResult]:
        glibc_versions = set()

        logger = self.get_logger()

        glibc_versions.update(self._detect_glibc_versions(self._appimage.path()))
        logger.info("detected required glibc version for runtime: {}".format(max(glibc_versions)))

        with self._appimage.mount() as mountpoint:
            payload_glibc_versions = set()

            for executable in BinaryWalker(mountpoint):
                # this check takes advantage of libc embedding static symbols into the binary depending on what
                # features are used
                # even binaries built on newer platforms may be running on older systems unless such features are used
                # example: a simple hello world built on bionic can run fine on trusty just fine
                executable_glibc_versions = self._detect_glibc_versions(executable)
                payload_glibc_versions.update(executable_glibc_versions)

            glibc_versions.update(payload_glibc_versions)

            if not payload_glibc_versions:
                logger.warning("AppImage payload does not seem to depend on glibc, this is quite unusual")
            else:
                logger.info("detected required glibc version for payload: {}".format(max(payload_glibc_versions)))

        if not glibc_versions:
            raise ValueError("Could not detect dependency of runtime on glibc")

        required_glibc_version = packaging.version.Version(max(glibc_versions))
        logger.debug("overall required glibc version: {}".format(required_glibc_version))

        for result in self._check_debian_compat(required_glibc_version):
            yield result

        for result in self._check_ubuntu_compat(required_glibc_version):
            yield result

    @classmethod
    def _get_debian_codename_map(cls):
        return load_json(debian_codename_map_path())

    @classmethod
    def _get_glibc_debian_versions_map(cls):
        return load_json(debian_glibc_versions_data_path())

    @classmethod
    def _get_glibc_ubuntu_versions_map(cls):
        return load_json(ubuntu_glibc_versions_data_path())

    @classmethod
    def _check_debian_compat(cls, required_glibc: packaging.version.Version) -> Iterator[TestResult]:
        codename_map = cls._get_debian_codename_map()
        glibc_versions_map = cls._get_glibc_debian_versions_map()

        for suite in ["oldstable", "stable", "testing", "unstable"]:
            codename = codename_map[suite]
            max_supported_glibc = glibc_versions_map[codename]

            should_run = required_glibc <= packaging.version.parse(max_supported_glibc)

            cls.get_logger().debug("Debian {} max supported glibc version: {}".format(suite, max_supported_glibc))
            yield TestResult(should_run, "AppImage can run on Debian {} ({})".format(suite, codename))

    @classmethod
    def _check_ubuntu_compat(cls, required_glibc: packaging.version.Version) -> Iterator[TestResult]:
        glibc_versions_map = cls._get_glibc_ubuntu_versions_map()

        for release, glibc_versions in glibc_versions_map.items():
            max_supported_glibc = max(glibc_versions)

            should_run = required_glibc <= packaging.version.Version(max_supported_glibc)

            cls.get_logger().debug("Ubuntu {} max supported glibc version: {}".format(release, max_supported_glibc))
            yield TestResult(should_run, "AppImage can run on Ubuntu {}".format(release))
