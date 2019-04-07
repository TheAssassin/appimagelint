import os
import tempfile

from typing import Iterable


def make_tempdir():
    # outside CI environments it's wise to use a ramdisk for storing the temporary data
    temp_base = None
    if os.path.isdir("/dev/shm"):
        temp_base = "/dev/shm"

    return tempfile.TemporaryDirectory(suffix=".tmp", prefix="appimagelint-", dir=temp_base)


def get_version_key(version) -> Iterable[int]:
    """
    Converts a version into keys used for sorting, max() etc, by human standards (e.g., to recognize that 0.1.10 is
    larger than 0.1.9).

    :param version: version to parse and convert
    :return: keys for version
    """
    return [int(i) for i in version.split(".")]


def max_version(data: Iterable[str]) -> str:
    """
    Get maximum version by human standards (semver like: 0.1.10 is larger than 0.1.9).

    Basically a wrapper of max() with a custom key command.

    :param data: versions in x.y.z... format (where x,y,z are ints)
    :return: max version
    """

    return max(data, key=get_version_key)
