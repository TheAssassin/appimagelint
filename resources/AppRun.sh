#! /bin/bash

this_dir=$(dirname "$0")

# add own bin dir as fallback
# might come in handy if readelf binary is missing on the system (not sure if that's even possible, though)
export PATH="$PATH":"$this_dir"/usr/bin

"$this_dir"/usr/bin/python -m appimagelint "$@"
