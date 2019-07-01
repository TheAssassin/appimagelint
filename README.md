# appimagelint

appimagelint is a tool to check [AppImage](https://appimage.org/) files for common issues.

appimagelint runs a variety of checks on AppImages and reports the
results in human-readable form in the console log.

![screenshot](https://github.com/TheAssassin/appimagelint/blob/944f85f74ede650a86ce01a18217d8834e2b3bb1/resources/screenshot.png)


## Usage

First, get a copy of appimagelint, either by downloading the AppImage from the [release page](https://github.com/TheAssassin/appimagelint/releases), or by installing it via [pip](https://pypa.python.org).

appimagelint is not published on [PyPI](https://pypi.org) right now, but you can install it directly from GitHub if you have `git` installed. Just call `pip install -e git+https://github.com/TheAssassin/appimagelint#egg=appimagelint` to install.

Now call appimagelint on any AppImage you want to evaluate:

```sh
# use via AppImage
> wget https://github.com/TheAssassin/appimagelint/releases/download/continuous/appimagelint-x86_64.AppImage
> chmod +x appimagelint-x86_64.AppImage
> ./appimagelint-x86_64.AppImage some_other.AppImage
[...]

# use via pip
# it is recommended to use a virtualenv for it, the following shows how it works with virtualenvwrapper
> mkvirtualenv appimagelint
> workon appimagelint
> pip install -e git+https://github.com/TheAssassin/appimagelint#egg=appimagelint
> appimagelint some_other.AppImage
```
