import os


class BinaryWalker:
    """
    Walks a directory using os.walk() and yields all ELF binaries within.
    """

    def __init__(self, path: str):
        self._root_path = path
        self._walk_res = os.walk(self._root_path)
        self._last_res = next(self._walk_res)

    def __iter__(self):
        return self

    def __next__(self):
        def is_elf(path):
            with open(path, "rb") as f:
                sig = f.read(4)
                return sig == b"\x7fELF"

        while self._last_res is not None:
            while self._last_res[2]:
                to_test = self._last_res[2].pop()

                abspath = os.path.join(self._last_res[0], to_test)

                if os.path.isfile(abspath):
                    if not os.path.islink(abspath):
                        if is_elf(abspath):
                            return abspath

            self._last_res = next(self._walk_res)

        raise StopIteration
