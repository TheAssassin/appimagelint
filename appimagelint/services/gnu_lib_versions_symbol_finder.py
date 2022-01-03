import os
import subprocess
from typing import List

from .._logging import make_logger
from ..services import BinaryWalker


class GnuLibVersionSymbolsFinder:
    @classmethod
    def _get_logger(self):
        return make_logger("gnu_lib_versions_symbols_finder")

    def __init__(self, query_reqs: bool = True, query_deps: bool = False):
        self._query_reqs = query_reqs
        self._query_deps = query_deps

    def detect_gnu_lib_versions(self, pattern, path):
        env = dict(os.environ)
        env["LC_ALL"] = "C"
        env["LANGUAGE"] = "C"

        versions = []

        data: str = subprocess.check_output(["readelf", "-V", path], env=env).decode()
        lines: List[str] = data.splitlines()

        elf_sections = []
        if self._query_deps:
            elf_sections.append(".gnu.version_d")
        if self._query_reqs:
            elf_sections.append(".gnu.version_r")

        for elf_section_name in elf_sections:
            in_req_section = False
            for line in lines:
                if elf_section_name in line:
                    in_req_section = True
                elif not in_req_section:
                    continue

                # end of section
                if not line.strip():
                    break

                parts = line.split()

                for index, part in enumerate(parts):
                    try:
                        if part.lower() != "name:":
                            continue
                    except IndexError:
                        continue

                    symbol = parts[index+1]

                    if pattern in symbol:
                        version = symbol.split(pattern)[1]

                        for c in version:
                            if c not in "0123456789.":
                                self._get_logger().debug("ignoring invalid version {} (parsed from {})".format(
                                    repr(version), repr(symbol))
                                )
                                break
                        else:
                            versions.append(version)

        return versions

    def check_all_executables(self, prefix: str, dirpath: str):
        logger = self._get_logger()

        if not os.path.isdir(dirpath):
            raise FileNotFoundError("could not find directory {}".format(repr(dirpath)))

        versions = set()

        for binary in BinaryWalker(dirpath):
            binary_versions = self.detect_gnu_lib_versions(prefix, binary)
            logger.debug(f"versions in {binary} (prefix {prefix}): {binary_versions}")
            versions.update(binary_versions)
        else:
            logger.warning(f"no binaries found in {dirpath}")

        return versions
