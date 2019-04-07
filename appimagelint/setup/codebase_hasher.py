from appimagelint import cache, setup
import hashlib
import os


class CodebaseHasher:
    def __init__(self, modules=None):
        if modules is None:
            modules = [cache, setup]

        self._modules = modules

    @staticmethod
    def _get_module_path(module):
        return module.__file__

    def _calculate_hash(self, digest_impl):
        d = digest_impl()

        for module in self._modules:
            dirpath = os.path.dirname(self._get_module_path(module))
            for root, dirs, files in os.walk(dirpath):
                for file in files:
                    path = os.path.join(root, file)
                    if not path.endswith(".py"):
                        continue

                    with open(path, "rb") as f:
                        d.update(f.read())

        return d.hexdigest()

    def digest_md5(self):
        return self._calculate_hash(hashlib.md5)
