import os
import tempfile


def make_tempdir():
    # outside CI environments it's wise to use a ramdisk for storing the temporary data
    temp_base = None
    if os.path.isdir("/dev/shm"):
        temp_base = "/dev/shm"

    return tempfile.TemporaryDirectory(suffix=".tmp", prefix="appimagelint-", dir=temp_base)
