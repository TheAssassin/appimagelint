import gzip
import os

import requests
import subprocess

from . import DebianCodenameMapCache
from ..services import GnuLibVersionSymbolsFinder
from .._logging import make_logger
from .._util import make_tempdir, max_version


def _get_logger():
    return make_logger("setup")


def get_debian_package_versions_map(package_name: str):
    logger = _get_logger()

    logger.info("Fetching {} package versions from Debian sources API".format(package_name))

    response = requests.get("https://sources.debian.org/api/src/{}/".format(package_name))
    response.raise_for_status()

    json_data = response.json()

    if "error" in json_data:
        raise ValueError("invalid response from Debian sources API: {}".format(json_data["error"]))

    versions_map = {}

    for version in json_data["versions"]:
        parsed_version = ".".join(version["version"].split(".")[:2]).split("-")[0]

        for suite in version["suites"]:
            # simple search for maximum supported version
            if suite not in versions_map or parsed_version > versions_map[suite]:
                versions_map[suite] = parsed_version

    return versions_map


def get_ubuntu_releases():
    releases = ("trusty", "xenial", "bionic", "cosmic", "disco")
    return releases


def get_debian_releases():
    releases = ("oldstable", "stable", "testing", "unstable",)
    return releases


def get_packages_gz_from_ftp_mirror(distro, release):
    url = "https://ftp.fau.de/{}/dists/{}/main/binary-amd64/Packages.gz".format(distro, release)
    response = requests.get(url)

    response.raise_for_status()

    data = gzip.decompress(response.content).decode()

    return data


def get_ubuntu_package_versions_map(package_name: str):
    logger = _get_logger()

    logger.info("Fetching {} package versions from Ubuntu FTP mirror".format(package_name))

    versions_map = {}

    releases = get_ubuntu_releases()
    for release in releases:
        data = get_packages_gz_from_ftp_mirror("ubuntu", release)

        # TODO: implement as binary search
        pkg_off = data.find("Package: {}".format(package_name))
        pkg_ver_off = data.find("Version:", pkg_off)
        next_pkg_off = data.find("Package:".format(package_name), pkg_off+1)

        if pkg_ver_off == -1 or pkg_ver_off > next_pkg_off:
            raise ValueError()

        version = data[pkg_ver_off:pkg_ver_off+512].splitlines()[0].split("Version: ")[-1]
        parsed_version = ".".join(version.split(".")[:3]).split("-")[0]
        versions_map[release] = parsed_version

    return versions_map


def get_glibcxx_version_from_debian_package(url: str):
    logger = _get_logger()

    with make_tempdir() as d:
        deb_path = os.path.join(d, "package.deb")

        logger.debug("Downloading {} to {}".format(url, deb_path))

        out_path = os.path.join(d, "out/")

        subprocess.check_call(["wget", "-q", url, "-O", deb_path], stdout=subprocess.DEVNULL)
        subprocess.check_call(["dpkg", "-x", deb_path, out_path], stdout=subprocess.DEVNULL)

        finder = GnuLibVersionSymbolsFinder(out_path)
        return finder.check_all_executables("GLIBCXX_")


def get_debian_glibcxx_versions_map():
    rv = {}

    debian_codenames = DebianCodenameMapCache.get_data()

    releases = [debian_codenames[i] for i in get_debian_releases()]

    for release in releases:
        url = get_glibcxx_package_url("debian", release)
        versions = get_glibcxx_version_from_debian_package(url)
        rv[release] = max_version(versions)

    return rv


def get_glibcxx_package_url(distro: str, release: str):
    data = get_packages_gz_from_ftp_mirror(distro, release)

    bin_pkg_name = "libstdc++6"

    pkg_off = data.find("Package: {}".format(bin_pkg_name))
    pkg_path_off = data.find("Filename:", pkg_off)
    next_pkg_off = data.find("Package:", pkg_off + 1)

    if pkg_path_off > next_pkg_off:
        raise ValueError("could not find Filename: entry for package {}".format(bin_pkg_name))

    pkg_path = data[pkg_path_off:pkg_path_off+2048].splitlines()[0].split("Filename:")[1].strip()

    url_template = "https://ftp.fau.de/{}/{}"\

    url = url_template.format(distro, pkg_path)
    return url


def get_ubuntu_glibcxx_versions_map():
    rv = {}

    for release in get_ubuntu_releases():
        url = get_glibcxx_package_url("ubuntu", release)
        versions = get_glibcxx_version_from_debian_package(url)
        rv[release] = max_version(versions)

    return rv
