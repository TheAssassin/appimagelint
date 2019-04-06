import json
import os

import requests

from ..data import debian_codename_map_path, debian_glibc_versions_data_path
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


def download_package_version_maps():
    logger = get_logger()

    try:
        debian_glibc_versions = _get_debian_package_versions_map("glibc")

    except OSError:
        if os.path.exists(debian_glibc_versions_data_path()):
            logger.error("Could not connect to server, using existing (old) data file")
        else:
            raise

    else:
        with open(debian_glibc_versions_data_path(), "w") as f:
            json.dump(debian_glibc_versions, f, indent=2)

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


