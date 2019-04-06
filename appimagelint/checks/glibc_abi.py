import shlex
import subprocess
from typing import Iterator

import packaging.version
import requests

from ..services import BinaryWalker
from ..models import AppImage, TestResult
from .._logging import make_logger
from ..colors import Colors
from ..symbols import Symbols

from . import CheckBase


class GlibcABICheck(CheckBase):
    _logger = make_logger("glibc_abi_check")

    _cache = {}

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
        cache_key = "version_aliases"

        if cache_key in cls._cache:
            return cls._cache[cache_key]

        cls._logger.info("Fetching release information from Debian FTP mirror")

        rv = {}

        for suite in ["oldstable", "stable", "testing", "unstable"]:
            headers = {"Range": "bytes=0-512"}
            url = "https://ftp.fau.de/debian/dists/{}/Release".format(suite)
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            for line in response.text.splitlines():
                prefix = "Codename:"

                if line.startswith(prefix):
                    rv[suite] = line.split(prefix)[-1].strip()
                    break
            else:
                raise ValueError("could not find Release file for suite {} on Debian mirror".format(suite))

        cls._cache[cache_key] = rv

        return rv

    @classmethod
    def _get_debian_package_versions_map(cls, package_name: str):
        cls._logger.info("Fetching {} package versions from Debian sources API".format(package_name))

        response = requests.get("https://sources.debian.org/api/src/{}/".format(package_name))
        response.raise_for_status()

        json = response.json()

        if "error" in json:
            raise ValueError("invalid response from Debian sources API: {}".format(json["error"]))

        versions_map = {}

        for version in json["versions"]:
            parsed_version = ".".join(version["version"].split(".")[:2]).split("-")[0]

            for suite in version["suites"]:
                # simple search for maximum supported version
                if suite not in versions_map or parsed_version > versions_map[suite]:
                    versions_map[suite] = parsed_version

        return versions_map

    @classmethod
    def _get_glibc_debian_versions_map(cls):
        cache_key = "glibc_versions_map"

        if cache_key in cls._cache:
            return cls._cache[cache_key]

        versions_map = cls._get_debian_package_versions_map("glibc")

        cls._cache[cache_key] = versions_map

        return versions_map

    @classmethod
    def _check_debian_stable_compat(cls, required_glibc: packaging.version.Version) -> Iterator[TestResult]:
        cache_key = "version_aliases"

        if "cache_key" in cls._cache:
            return cls._cache[cache_key]

        codename_map = cls._get_debian_codename_map()
        glibc_versions_map = cls._get_glibc_debian_versions_map()

        for suite in ["oldstable", "stable", "testing", "unstable"]:
            codename = codename_map[suite]
            max_supported_glibc = glibc_versions_map[codename]

            should_run = required_glibc < packaging.version.parse(max_supported_glibc)

            yield TestResult(should_run, "AppImage can run on Debian {} ({})".format(suite, codename))
