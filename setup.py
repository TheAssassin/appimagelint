from setuptools import setup, find_packages


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
