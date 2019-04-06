import logging


def get_logger():
    from .. import _logging
    logger = _logging.make_logger("setup")
    logger.setLevel(logging.DEBUG)
    return logger


from .download_resources import download_package_version_maps, download_distro_codename_maps

__all__ = ("download_package_version_maps", "download_distro_codename_maps",)
