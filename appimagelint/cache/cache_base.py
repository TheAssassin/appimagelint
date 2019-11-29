import os
from typing import Iterable

import xdg


class CacheBase:
    """
    Abstract base class for caches.
    """

    @staticmethod
    def _user_cache_base_path():
        path = os.path.abspath(os.path.join(xdg.XDG_CACHE_HOME, "appimagelint"))
        return path

    @staticmethod
    def _bundled_cache_base_path():
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "bundled_cache"))
        return path

    @staticmethod
    def _cache_file_name() -> str:
        """
        Get cache file path. Must be overridden by subclasses.
        :return: cache file's path
        """
        raise NotImplementedError

    @classmethod
    def _find_cache_files(cls) -> Iterable[str]:
        for dir in (cls._user_cache_base_path(), cls._bundled_cache_base_path()):
            file_path = os.path.join(dir, cls._cache_file_name())
            if os.path.exists(file_path):
                yield file_path

    @classmethod
    def update_now(cls, save_to_bundled_cache: bool = False):
        """
        Force cache update.
        :return:
        """

        raise NotImplementedError()

    @classmethod
    def get_data(cls, raise_on_error: bool = False):
        """
        Returns cached data.
        If the data is out of date, the method will attempt to update them (if possible).
        In case fetching the latest data fails, the method will return the cached data anyway unless raise_on_error
        is set to True.
        If this is impossible, an :class:`OutOfDateError` is thrown even if raise_on_error is set to False.

        :return: data represented by cache class
        :raises OutOfDateError: in case data is out of date, see method docstring for details
        """

        raise NotImplementedError()
