from typing import Iterator

from ..models import AppImage, TestResult


class CheckBase:
    def __init__(self, appimage: AppImage):
        self._appimage = appimage

    def run(self) -> Iterator[TestResult]:
        raise NotImplementedError

    @staticmethod
    def name():
        raise NotImplementedError
