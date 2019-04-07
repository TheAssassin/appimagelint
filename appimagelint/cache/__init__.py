from .._logging import make_logger


def _get_logger():
    return make_logger("setup")


from .exceptions import OutOfDateError
from .io import load_json, store_json
from .distro_codenames import update_distro_codename_maps
from .package_version_maps import update_package_version_maps
