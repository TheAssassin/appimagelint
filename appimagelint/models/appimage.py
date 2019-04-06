import os


class AppImage:
    def __init__(self, path: str, custom_runtime: str = None):
        if not os.path.exists(path):
            raise FileNotFoundError("file not found: {}".format(path))

        self._path = os.path.abspath(path)

        self._custom_runtime = custom_runtime

    def path(self):
        return self._path

    def mount(self):
        # must not import near top of file to avoid problems with the circular dependency this helper method creates
        from ..services import AppImageMounter

        return AppImageMounter(self, self._custom_runtime)
