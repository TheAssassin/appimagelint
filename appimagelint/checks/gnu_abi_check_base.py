import logging
import packaging.version
from typing import Iterator

from .._logging import make_logger
from ..services import GnuLibVersionSymbolsFinder
from ..cache import DebianCodenameMapCache
from ..cache.common import get_debian_releases, get_ubuntu_releases, get_rocky_linux_releases
from ..models import TestResult
from ..services import BinaryWalker
from ..models import AppImage
from .._util import max_version
from . import CheckBase


class GnuAbiCheckBase(CheckBase):
    _gnu_lib_versions_symbol_finder = GnuLibVersionSymbolsFinder(query_reqs=True, query_deps=False)

    def __init__(self, appimage: AppImage):
        super().__init__(appimage)

    @classmethod
    def id(cls):
        return "{}_abi_check".format(cls._library_id())

    @classmethod
    def _test_result_id_prefix(cls):
        return cls.id()

    @staticmethod
    def name():
        raise NotImplementedError()

    @classmethod
    def _detect_versions_in_file(cls, path):
        raise NotImplementedError

    @staticmethod
    def _library_id():
        raise NotImplementedError

    def run(self) -> Iterator[TestResult]:
        versions = set()

        logger = self.get_logger()

        versions.update(self._detect_versions_in_file(self._appimage.path()))

        logger.info("detected required version for runtime: "
                    "{}".format(max_version(versions) if versions else "<none>"))

        with self._appimage.mount() as mountpoint:
            payload_versions = set()

            for executable in BinaryWalker(mountpoint):
                # this check takes advantage of libc embedding static symbols into the binary depending on what
                # features are used
                # even binaries built on newer platforms may be running on older systems unless such features are used
                # example: a simple hello world built on bionic can run fine on trusty just fine
                executable_versions = self._detect_versions_in_file(executable)
                payload_versions.update(executable_versions)

            versions.update(payload_versions)

            if payload_versions:
                logger.info("detected required version for payload: "
                            "{}".format(max_version(payload_versions) if versions else "<none>"))

        if not versions:
            logger.warning("could not find any dependencies, skipping check")
            return

        required_version = packaging.version.Version(max_version(versions))
        logger.debug("overall required version: {}".format(required_version))

        for result in self._check_debian_compat(required_version):
            yield result

        for result in self._check_ubuntu_compat(required_version):
            yield result

        for result in self._check_rocky_linux_compat(required_version):
            yield result

    @classmethod
    def _get_debian_codename_map(cls):
        return DebianCodenameMapCache.get_data()

    @classmethod
    def _get_debian_versions_map(cls):
        raise NotImplementedError()

    @classmethod
    def _get_ubuntu_versions_map(cls):
        raise NotImplementedError()

    @classmethod
    def _get_rocky_linux_versions_map(cls):
        raise NotImplementedError()

    @classmethod
    def _check_debian_compat(cls, required_version: packaging.version.Version) -> Iterator[TestResult]:
        codename_map = cls._get_debian_codename_map()
        versions_map = cls._get_debian_versions_map()

        for release in get_debian_releases():
            codename = codename_map[release]

            max_supported_version = None
            try:
                max_supported_version = versions_map[codename]
            except KeyError:
                cls.get_logger().warning("could not find version for {}, trying backports".format(release))

                try:
                    max_supported_version = versions_map["{}-backports".format(codename)]
                except KeyError:
                    cls.get_logger().error(
                        "could not find version for {} in backports either, aborting check".format(release)
                    )

            if max_supported_version is None:
                should_run = False
            else:
                should_run = required_version <= packaging.version.parse(max_supported_version)
            
            test_result_id = "{}_{}_{}".format(cls._test_result_id_prefix(), "debian", release)
            test_result_msg = "AppImage can run on Debian {} ({})".format(release, codename)

            cls.get_logger().debug("Debian {} max supported version: {}".format(release, max_supported_version))
            yield TestResult(should_run, test_result_id, test_result_msg)

    @classmethod
    def _check_ubuntu_compat(cls, required_version: packaging.version.Version) -> Iterator[TestResult]:
        versions_map = cls._get_ubuntu_versions_map()

        for release in get_ubuntu_releases():
            max_supported_version = versions_map[release]

            should_run = required_version <= packaging.version.Version(max_supported_version)

            test_result_id = "{}_{}_{}".format(cls._test_result_id_prefix(), "ubuntu", release)
            test_result_msg = "AppImage can run on Ubuntu {}".format(release)

            cls.get_logger().debug("Ubuntu {} max supported version: {}".format(release, max_supported_version))
            yield TestResult(should_run, test_result_id, test_result_msg)

    @classmethod
    def _check_rocky_linux_compat(cls, required_version: packaging.version.Version) -> Iterator[TestResult]:
        versions_map = cls._get_rocky_linux_versions_map()

        for release in get_rocky_linux_releases():
            max_supported_version = versions_map[release]

            should_run = required_version <= packaging.version.Version(max_supported_version)

            test_result_id = "{}_{}_{}".format(cls._test_result_id_prefix(), "ubuntu", release)
            test_result_msg = "AppImage can run on Rocky Linux {}".format(release)

            cls.get_logger().debug("Rocky Linux {} max supported version: {}".format(release, max_supported_version))
            yield TestResult(should_run, test_result_id, test_result_msg)
