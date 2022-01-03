import glob
import gzip
import os
import re

from xml.etree import ElementTree as ET

import requests
import subprocess

from . import DebianCodenameMapCache, UbuntuReleaseNamesCache
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
    """
    Fetches Ubuntu release codenames from Launchpad's series API endpoint.

    Ubuntu doesn't have any "stable" (as in, they don't change) aliases for their currently supported releases.

    :return: names of currently supported Ubuntu releases
    """

    releases = UbuntuReleaseNamesCache.get_data()

    return tuple(releases)


def get_centos_releases():
    """
    For now, only the still-supported old-style LTS CentOS 7 is supported.
    """

    # make sure to return only strings, the caching logic expects that
    releases = ["7"]

    return tuple(releases)


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


def get_centos_repodata_primary_xml(version: int):
    base_url = f"https://ftp.fau.de/centos/{version}/os/x86_64/repodata/"

    def get_request(url):
        response = requests.get(url)
        response.raise_for_status()
        return response

    namespaces = {
        "repo": "http://linux.duke.edu/metadata/repo"
    }

    repomd_xml_root = ET.fromstring(get_request(f"{base_url}/repomd.xml").content)
    data_elem = repomd_xml_root.find("repo:data[@type='primary']", namespaces)
    if not data_elem:
        raise KeyError("could not find primary data reference in repomd.xml")

    relative_href = data_elem.find("repo:location", namespaces).attrib["href"].split("/")[-1]
    primary_url = f"{base_url}/{relative_href}"

    return gzip.decompress(get_request(primary_url).content)


def get_centos_package_versions_map(package_name: str, pattern: str):
    logger = _get_logger()

    logger.info(f"Fetching {package_name} package versions from CentOS mirror")

    namespaces = {
        "common": "http://linux.duke.edu/metadata/common",
        "rpm": "http://linux.duke.edu/metadata/rpm",
    }

    versions_map = {}

    releases = get_centos_releases()
    for release in releases:
        primary_xml_root = ET.fromstring(get_centos_repodata_primary_xml(release))

        package_elem: ET.Element
        for package_elem in primary_xml_root.findall("common:package", namespaces):
            name = package_elem.find("common:name", namespaces).text

            if name == package_name:
                version_markers = []

                for rpm_entry in package_elem.findall("common:format/rpm:provides/rpm:entry", namespaces):
                    entry_name = rpm_entry.attrib["name"]

                    match = re.match(pattern, entry_name)
                    if match:
                        version_markers.append(match.group(1))

                versions_map[release] = max_version(version_markers)
                break

        else:
            raise KeyError("could not find primary data reference in primary xml")

    return versions_map


def get_glibcxx_version_from_debian_package(url: str):
    logger = _get_logger()

    with make_tempdir() as d:
        deb_path = os.path.join(d, "package.deb")

        logger.debug("Downloading {} to {}".format(url, deb_path))

        def check_call(args, **kwargs):
            logger.debug(f"Calling {repr(args)}")
            proc = subprocess.run(args, check=True, capture_output=True, **kwargs)
            logger.debug(f"stdout: {proc.stdout}")
            logger.debug(f"stderr: {proc.stderr}")

        out_path = os.path.join(d, "out/")
        os.makedirs(out_path, exist_ok=True)

        check_call(["wget", "-q", url, "-O", deb_path], cwd=d)

        # cannot use dpkg, but extracting Debian packages is quite easy with ar and tar
        check_call(["ar", "-xv", deb_path], cwd=d)

        data_archive_name = glob.glob(os.path.join(d, "data.tar.*"))[0]
        check_call(["tar", "-xvf", data_archive_name], cwd=out_path)

        finder = GnuLibVersionSymbolsFinder(query_deps=True, query_reqs=False)
        return finder.check_all_executables("GLIBCXX_", out_path)


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


def get_centos_glibc_versions_map():
    return get_centos_package_versions_map("glibc", r"libc\.so\.6\(GLIBC_(.*)\)")


def get_centos_glibcxx_versions_map():
    return get_centos_package_versions_map("libstdc++", r"libstdc\+\+\.so\.6\(GLIBCXX_(.*)\)")
