#! /bin/bash

set -x
set -e

# use RAM disk if possible
if [ "$CI" == "" ] && [ -d /dev/shm ]; then
    TEMP_BASE=/dev/shm
else
    TEMP_BASE=/tmp
fi

BUILD_DIR=$(mktemp -d -p "$TEMP_BASE" appimagelint-build-XXXXXX)

cleanup () {
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
    fi
}

trap cleanup EXIT

# store repo root as variable
REPO_ROOT=$(readlink -f $(dirname $(dirname "$0")))
OLD_CWD=$(readlink -f .)

SETUPPY_VERSION=$(cat "$REPO_ROOT"/setup.py | grep version | cut -d'"' -f2)

pushd "$BUILD_DIR"

mkdir -p AppDir

COMMIT=$(cd "$REPO_ROOT" && git rev-parse --short HEAD)
echo "$COMMIT" > AppDir/commit

wget https://github.com/TheAssassin/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
wget https://raw.githubusercontent.com/linuxdeploy/linuxdeploy-plugin-conda/master/linuxdeploy-plugin-conda.sh

chmod +x linuxdeploy*.AppImage
chmod +x linuxdeploy*.sh

export CONDA_PACKAGES="Pillow"
export PIP_REQUIREMENTS="."
export PIP_WORKDIR="$REPO_ROOT"
export OUTPUT=appimagelint-x86_64.AppImage
export VERSION="$SETUPPY_VERSION-git$COMMIT"

install -D "$REPO_ROOT"/resources/com.github.theassassin.appimagelint.appdata.xml -t AppDir/usr/share/metainfo/

./linuxdeploy-x86_64.AppImage --appdir AppDir --plugin conda \
    -e $(which readelf) \
    -e $(which desktop-file-validate) \
    -i "$REPO_ROOT"/resources/com.github.theassassin.appimagelint.svg \
    -d "$REPO_ROOT"/resources/com.github.theassassin.appimagelint.desktop \
    --custom-apprun "$REPO_ROOT"/resources/AppRun.sh

# bundle cache metadata
AppDir/usr/conda/bin/python3 -m appimagelint.cache bundle_metadata

# now, actually build AppImage
# guessing the output architecture from $ARCH does not seem to work (any more?), so we specify the output name manually
export OUTPUT=appimagelint-"$ARCH".AppImage
./linuxdeploy-x86_64.AppImage --appdir AppDir --output appimage

# test AppImage with itself
./appimagelint-x86_64.AppImage appimagelint-x86_64.AppImage --json-report appimagelint-report.json
cat appimagelint-report.json

mv appimagelint*.AppImage "$OLD_CWD"
