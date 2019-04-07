import json
from typing import Union, Iterable, Mapping

from . import OutOfDateError
from ..setup.codebase_hasher import CodebaseHasher


# use a method to simulate "const values"
def cache_timeout():
    # update caches every week
    return 7 * 24 * 60 * 60


def store_json(path: str, data: Union[Mapping, Iterable]):
    json_root = {
        "codebase_digest": CodebaseHasher().digest_md5(),
        "data": data,
    }

    with open(path, "w") as f:
        json.dump(json_root, f, indent=2)


def load_json(path):
    try:
        with open(path, "r") as f:
            json_root = json.load(f)
    except FileNotFoundError:
        raise OutOfDateError("cache file missing, forcing update for initial download")

    codebase_digest = CodebaseHasher().digest_md5()
    try:
        if json_root["codebase_digest"] != codebase_digest:
            raise OutOfDateError("codebase changed since last update, forcing update")

        return json_root["data"]

    # capture all "invalid data format" kind of errors and force update
    except KeyError:
        raise OutOfDateError("file in invalid format, forcing update")
