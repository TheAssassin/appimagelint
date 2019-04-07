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

pushd "$BUILD_DIR"

wget https://github.com/TheAssassin/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
wget https://raw.githubusercontent.com/linuxdeploy/linuxdeploy-plugin-conda/master/linuxdeploy-plugin-conda.sh

chmod +x linuxdeploy*.AppImage
chmod +x linuxdeploy*.sh


export PIP_REQUIREMENTS="."
export PIP_WORKDIR="$REPO_ROOT"
export OUTPUT=appimagelint-x86_64.AppImage

./linuxdeploy-x86_64.AppImage --appdir AppDir --plugin conda -i "$REPO_ROOT"/resources/appimagelint.svg -d "$REPO_ROOT"/resources/appimagelint.desktop --output appimage --custom-apprun "$REPO_ROOT"/resources/AppRun

# test AppImage with itself
./appimagelint-x86_64.AppImage appimagelint-x86_64.AppImage

mv appimagelint*.AppImage "$OLD_CWD"
