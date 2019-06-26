import logging

from typing import Iterator

from appimagelint._logging import make_logger
from ..models import AppImage, TestResult


class CheckBase:
    def __init__(self, appimage: AppImage):
        self._appimage = appimage

    def run(self) -> Iterator[TestResult]:
        raise NotImplementedError

    @classmethod
    def get_logger(cls):
        return make_logger(cls.id())

    @staticmethod
    def name():
        raise NotImplementedError

    @staticmethod
    def id():
        raise NotImplementedError
