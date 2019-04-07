import os
import string
import subprocess

from appimagelint.services import BinaryWalker


class GnuLibVersionSymbolsFinder:
    def __init__(self, dirpath: str):
        if not os.path.isdir(dirpath):
            raise FileNotFoundError("could not find directory {}".format(repr(dirpath)))

        self._dirpath = dirpath

    @classmethod
    def detect_gnu_lib_versions(cls, pattern, path):
        data = subprocess.check_output(["strings", path]).decode()

        versions = set()

        for line in data.splitlines():
            if not pattern in line:
                continue

            if "_{}".format(pattern) in line:
                continue

            # a few known invalid values (saves running the for loop below)
            if "DEBUG_MESSAGE_LENGTH" in line or "PRIVATE" in line:
                continue

            version = line.split("@@")[-1].split(pattern)[-1]

            def is_valid_version(version):
                for c in version:
                    if c not in string.digits + ".":
                        return False
                return True

            if not is_valid_version(version):
                continue

            versions.add(version)

        return versions

    def check_all_executables(self, prefix: str):
        versions = set()

        for binary in BinaryWalker(self._dirpath):
            versions.update(self.detect_gnu_lib_versions(prefix, binary))

        return versions
