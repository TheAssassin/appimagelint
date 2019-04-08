import os
import subprocess
from typing import List

from .._logging import make_logger
from ..services import BinaryWalker


class GnuLibVersionSymbolsFinder:
    _logger = make_logger("gnu_lib_versions_symbols_finder")

    def __init__(self, dirpath: str):
        if not os.path.isdir(dirpath):
            raise FileNotFoundError("could not find directory {}".format(repr(dirpath)))

        self._dirpath = dirpath

    @classmethod
    def detect_gnu_lib_versions(cls, pattern, path):
        env = dict(os.environ)
        env["LC_ALL"] = "C"
        env["LANGUAGE"] = "C"

        versions = []

        data: str = subprocess.check_output(["readelf", "-V", path], env=env).decode()
        lines: List[str] = data.splitlines()

        in_req_section = False
        for line in lines:
            if ".gnu.version_r" in line:
                in_req_section = True
                continue

            if in_req_section:
                if not line.strip():
                    break

                parts = line.split()

                if parts[1].lower() != "name:":
                    continue

                symbol = parts[2]

                if pattern in symbol:
                    version = symbol.split(pattern)[1]

                    for c in version:
                        if c not in "0123456789.":
                            cls._logger.debug("ignoring invalid version {} (parsed from {})".format(
                                repr(version), repr(symbol))
                            )
                            break
                    else:
                        versions.append(version)

        return versions

    def check_all_executables(self, prefix: str):
        versions = set()

        for binary in BinaryWalker(self._dirpath):
            versions.update(self.detect_gnu_lib_versions(prefix, binary))

        return versions
