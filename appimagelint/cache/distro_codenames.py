import os

from appimagelint.cache import OutOfDateError, load_json
from . import store_json, _get_logger
from ..setup.download_resources import get_debian_distro_codename_map
from ..setup.paths import debian_glibc_versions_data_path, debian_codename_map_path


def update_distro_codename_maps():
    logger = _get_logger()

    out_path = debian_codename_map_path()

    try:
        load_json(out_path)
    except OutOfDateError as e:
        logger.debug("OutOfDateError: {}".format(" ".join(e.args)))
        pass
    else:
        logger.debug("debian distro codename map still up to date, no update required")
        return

    logger.info("Fetching release information from Debian FTP mirror")

    try:
        debian_codename_map = get_debian_distro_codename_map()

    except OSError:
        if os.path.exists(debian_glibc_versions_data_path()):
            logger.error("Could not connect to server, using existing (old) data file")
        else:
            raise

    else:
        store_json(out_path, debian_codename_map)
