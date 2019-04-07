import os

from appimagelint.cache import OutOfDateError
from . import store_json, _get_logger, load_json
from ..setup.download_resources import get_debian_package_versions_map, get_ubuntu_package_versions_map, \
    get_debian_glibcxx_versions_map, get_ubuntu_glibcxx_versions_map
from ..setup.paths import ubuntu_glibcxx_versions_data_path, debian_glibcxx_versions_data_path, \
    debian_glibc_versions_data_path, ubuntu_glibc_versions_data_path


def update_package_version_maps():
    logger = _get_logger()

    for distro, get_map_callback, out_path in [
        ("debian", lambda: get_debian_package_versions_map("glibc"), debian_glibc_versions_data_path()),
        ("ubuntu", lambda: get_ubuntu_package_versions_map("glibc"), ubuntu_glibc_versions_data_path()),
        ("debian", get_debian_glibcxx_versions_map, debian_glibcxx_versions_data_path()),
        ("ubuntu", get_ubuntu_glibcxx_versions_map, ubuntu_glibcxx_versions_data_path()),
    ]:
        try:
            load_json(out_path)
        except OutOfDateError as e:
            logger.debug("OutOfDateError: {}".format(" ".join(e.args)))
            pass
        else:
            logger.debug("{} still up to date, no update required".format(out_path, distro))
            continue

        logger.info("Fetching version data for {}".format(distro))

        try:
            data = get_map_callback()

        except OSError as e:
            if os.path.exists(out_path):
                logger.error("Could not connect to server, using existing (old) data file")
                logger.exception(e)
            else:
                raise

        else:
            store_json(out_path, data)

    # TODO: libstdc++
