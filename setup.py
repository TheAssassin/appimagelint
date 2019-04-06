import logging

from setuptools import setup, find_packages
from appimagelint.setup import download_package_version_maps, get_logger, download_distro_codename_maps


logging.basicConfig(format="%(name)s [%(levelname)s] %(message)s")
logger = get_logger()

# in case there's a problem with the download and there's no existing data file, we log error and then abort the
# installation
try:
    download_package_version_maps()
except Exception:
    logger.error("Error: Failed to download package version maps, aborting")
    raise

try:
    download_distro_codename_maps()
except Exception:
    logger.error("Error: Failed to download distro codename maps, aborting")
    raise


setup(
    name="appimagelint",
    version="0.0.1",
    packages=find_packages(),
    license="MIT",
    long_description=open("README.md").read(),
    install_requires=[
        "coloredlogs",
        "packaging",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "appimagelint = appimagelint._cli:run",
        ],
    },
)
