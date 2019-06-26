from collections import OrderedDict
from typing import Iterable

from appimagelint.checks import CheckBase, GlibcABICheck, GlibcxxABICheck, IconsCheck, DesktopFilesCheck
from appimagelint.models import AppImage


class ChecksManager:
    _registered_checks = OrderedDict()

    @classmethod
    def register_check(cls, check_cls: type):
        if not issubclass(check_cls, CheckBase):
            raise RuntimeError("cannot register classes as check which do not implement CheckBase")

        check_id = check_cls.id()

        if id in cls._registered_checks:
            raise KeyError("check with ID {} already registered".format(id))

        cls._registered_checks[check_id] = check_cls

    @classmethod
    def init(cls):
        for check_cls in [GlibcABICheck, GlibcxxABICheck, IconsCheck, DesktopFilesCheck]:
            cls.register_check(check_cls)

    @classmethod
    def list_checks(cls) -> Iterable:
        return list(cls._registered_checks)

    @classmethod
    def get_instance(cls, check_id: str, appimage: AppImage) -> CheckBase:
        try:
            return cls._registered_checks[check_id](appimage)

        except KeyError:
            raise KeyError("could not find check with ID {}".format(check_id))
