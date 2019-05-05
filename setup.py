import os

from setuptools import setup, find_packages


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
    entry_points={
        "console_scripts": [
            "appimagelint = appimagelint.cli:run",
        ],
    },
)
