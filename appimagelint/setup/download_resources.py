import json
import gzip
import os

import requests

from ..data import debian_codename_map_path, debian_glibc_versions_data_path, ubuntu_glibc_versions_data_path
from . import get_logger


def _get_debian_package_versions_map(package_name: str):
    logger = get_logger()

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


def _get_ubuntu_package_versions_map(package_name: str):
    logger = get_logger()

    logger.info("Fetching {} package versions from Ubuntu FTP mirror".format(package_name))

    versions_map = {}

    releases = ("trusty", "xenial", "bionic", "cosmic", "disco")
    for release in releases:
        url = "https://ftp.fau.de/ubuntu/dists/{}/main/binary-amd64/Packages.gz".format(release)
        response = requests.get(url)

        if response.status_code == 404 and releases.index(release) > releases.index("cosmic"):
            continue

        response.raise_for_status()

        data = gzip.decompress(response.content).decode()

        # TODO: implement as binary search
        pkg_off = data.find("Package: {}".format(package_name))
        pkg_ver_off = data.find("Version:", pkg_off)
        next_pkg_off = data.find("Package: {}".format(package_name), pkg_off+1)

        if pkg_ver_off == -1 or pkg_ver_off > next_pkg_off:
            raise ValueError()

        version = data[pkg_ver_off:pkg_ver_off+512].splitlines()[0].split("Version: ")[-1]
        parsed_version = ".".join(version.split(".")[:3]).split("-")[0]
        versions_map[release] = [parsed_version]

    return versions_map


def download_package_version_maps():
    logger = get_logger()

    for distro, get_map_callback, out_path in [
        ("debian", _get_debian_package_versions_map, debian_glibc_versions_data_path()),
        ("ubuntu", _get_ubuntu_package_versions_map, ubuntu_glibc_versions_data_path()),
    ]:
        logger.info("Fetching version data for {}".format(distro))

        try:
            glibc_versions = get_map_callback("glibc")

        except OSError as e:
            if os.path.exists(out_path):
                logger.error("Could not connect to server, using existing (old) data file")
                logger.exception(e)
            else:
                raise

        else:
            with open(out_path, "w") as f:
                json.dump(glibc_versions, f, indent=2)

    # TODO: libstdc++


def _get_debian_distro_codename_map():
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

    return rv


def download_distro_codename_maps():
    logger = get_logger()

    logger.info("Fetching release information from Debian FTP mirror")

    try:
        debian_codename_map = _get_debian_distro_codename_map()

    except OSError:
        if os.path.exists(debian_glibc_versions_data_path()):
            logger.error("Could not connect to server, using existing (old) data file")
        else:
            raise

    else:
        with open(debian_codename_map_path(), "w") as f:
            json.dump(debian_codename_map, f, indent=2)


