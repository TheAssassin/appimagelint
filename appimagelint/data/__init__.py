import os


def data_dir_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__)))


def debian_glibc_versions_data_path():
    return os.path.join(data_dir_path(), "debian_glibc_versions.json")


def ubuntu_glibc_versions_data_path():
    return os.path.join(data_dir_path(), "ubuntu_glibc_versions.json")


def debian_codename_map_path():
    return os.path.join(data_dir_path(), "debian_codenames.json")
