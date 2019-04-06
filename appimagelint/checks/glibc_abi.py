import json
import shlex
import subprocess
from typing import Iterator

import packaging.version

from ..services import BinaryWalker
from ..models import AppImage, TestResult
from .._logging import make_logger
from ..data import debian_glibc_versions_data_path, debian_codename_map_path

from . import CheckBase


class GlibcABICheck(CheckBase):
    _logger = make_logger("glibc_abi_check")

    def __init__(self, appimage: AppImage):
        super().__init__(appimage)

    @staticmethod
    def name():
        return "GNU libc ABI check"

    @classmethod
    def _detect_gnu_lib_versions(cls, pattern, path):
        data = subprocess.check_output(
            "strings {} | grep {} || true".format(shlex.quote(path), shlex.quote(pattern)),
            shell=True
        ).decode()

        versions = set()

        for line in data.splitlines():
            version = line.split("@@")[-1].split(pattern)[-1]

            versions.add(packaging.version.parse(version))

        return versions

    @classmethod
    def _detect_glibc_versions(cls, path):
        return cls._detect_gnu_lib_versions("GLIBC_", path)

    def run(self) -> Iterator[TestResult]:
        glibc_versions = set()

        self._logger.info("detecting runtime's glibc version requirements")
        glibc_versions.update(self._detect_glibc_versions(self._appimage.path()))

        self._logger.info("detecting AppImage payload's glibc version requirements")
        with self._appimage.mount() as mountpoint:
            for executable in BinaryWalker(mountpoint):
                # this check takes advantage of libc embedding static symbols into the binary depending on what
                # features are used
                # even binaries built on newer platforms may be running on older systems unless such features are used
                # example: a simple hello world built on bionic can run fine on trusty just fine
                glibc_versions = self._detect_glibc_versions(executable)

                glibc_versions.update(glibc_versions)

            required_glibc_version = max(glibc_versions)

            for result in self._check_debian_stable_compat(required_glibc_version):
                yield result

    @classmethod
    def _get_debian_codename_map(cls):
        with open(debian_codename_map_path(), "r") as f:
            return json.load(f)

    @classmethod
    def _get_glibc_debian_versions_map(cls):
        with open(debian_glibc_versions_data_path(), "r") as f:
            return json.load(f)

    @classmethod
    def _check_debian_stable_compat(cls, required_glibc: packaging.version.Version) -> Iterator[TestResult]:
        codename_map = cls._get_debian_codename_map()
        glibc_versions_map = cls._get_glibc_debian_versions_map()

        for suite in ["oldstable", "stable", "testing", "unstable"]:
            codename = codename_map[suite]
            max_supported_glibc = glibc_versions_map[codename]

            should_run = required_glibc <= packaging.version.parse(max_supported_glibc)

            yield TestResult(should_run, "AppImage can run on Debian {} ({})".format(suite, codename))
