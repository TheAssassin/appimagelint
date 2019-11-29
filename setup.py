import logging
import os

from setuptools import setup, find_packages, Command


class BundleMetadataCommand(Command):
    description = "download and bundle cached metadata"

    user_options = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        from appimagelint._logging import setup
        setup(loglevel=logging.DEBUG, with_timestamps=True)

        logging.getLogger("urllib3").setLevel(logging.INFO)

        from appimagelint.cache import DebianCodenameMapCache, PackageVersionMapsCache, AppImageRuntimeCache
        for cache in DebianCodenameMapCache, PackageVersionMapsCache, AppImageRuntimeCache:
            cache.update_now(save_to_bundled_cache=True)


setup(
    name="appimagelint",
    version="0.0.1",
    packages=find_packages(),
    license="MIT",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    install_requires=[
        "coloredlogs",
        "packaging",
        "requests",
        "xdg",
        "pillow",
    ],
    cmdclass={
        "bundle_metadata": BundleMetadataCommand,
    },
    entry_points={
        "console_scripts": [
            "appimagelint = appimagelint.cli:run",
        ],
    },
)
