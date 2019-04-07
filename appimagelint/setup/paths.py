import os
import xdg


def data_cache_path():
    path = os.path.abspath(os.path.join(xdg.XDG_CACHE_HOME, "appimagelint"))
    os.makedirs(path, exist_ok=True)
    return path


def debian_glibc_versions_data_path():
    return os.path.join(data_cache_path(), "debian_glibc_versions.json")


def ubuntu_glibc_versions_data_path():
    return os.path.join(data_cache_path(), "ubuntu_glibc_versions.json")


def debian_codename_map_path():
    return os.path.join(data_cache_path(), "debian_codenames.json")
