import os
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

            if "DEBUG_MESSAGE_LENGTH" in line:
                continue

            version = line.split("@@")[-1].split(pattern)[-1]

            versions.add(version)

        return versions

    def check_all_executables(self, prefix: str):
        versions = set()

        for binary in BinaryWalker(self._dirpath):
            versions.update(self.detect_gnu_lib_versions(prefix, binary))

        return versions
