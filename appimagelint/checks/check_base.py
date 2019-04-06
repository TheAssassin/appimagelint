from ..models import AppImage


class CheckBase:
    def __init__(self, appimage: AppImage):
        self._appimage = appimage

    def run(self):
        raise NotImplementedError

    @staticmethod
    def name():
        raise NotImplementedError
