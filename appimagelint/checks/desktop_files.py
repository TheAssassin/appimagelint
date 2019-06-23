import shutil
import subprocess
from pathlib import Path

from appimagelint._logging import make_logger
from appimagelint.models import TestResult
from ..models import AppImage
from . import CheckBase


class DesktopFilesCheck(CheckBase):
    def __init__(self, appimage: AppImage):
        super().__init__(appimage)

    @staticmethod
    def name():
        return "Desktop files existence and validity"

    def run(self):
        logger = self.get_logger()

        with self._appimage.mount() as mountpoint:
            # find desktop files in AppDir root
            root_desktop_files = set(map(str, Path(mountpoint).glob("*.desktop")))
            # search entire AppDir for desktop files
            all_desktop_files = set(map(str, Path(mountpoint).rglob("*.desktop")))

            logger.info("Checking desktop files in root directory")

            exactly_one_file_in_root = len(root_desktop_files) == 1

            yield TestResult(exactly_one_file_in_root, "desktop_files_check.exactly_one_in_root", "Exactly one desktop file in AppDir root")

            dfv_cmd_name = "desktop-file-validate"
            dfv_cmd_path = shutil.which(dfv_cmd_name)

            validation_results = {}
            if not dfv_cmd_path:
                logger.error("could not find {}, skipping desktop file checks".format(dfv_cmd_name))
            else:
                for desktop_file in all_desktop_files:
                    logger.info("Checking desktop file {} with {}".format(desktop_file, dfv_cmd_name))

                    success = True

                    try:
                        subprocess.check_call([dfv_cmd_path, desktop_file])
                    except subprocess.SubprocessError:
                        success = False

                    validation_results[desktop_file] = success

                yield TestResult(all(validation_results.values()), "desktop_files_check.all_desktop_files_valid", "All desktop files in AppDir are valid")

    @staticmethod
    def get_logger():
        return make_logger("icon_check")
