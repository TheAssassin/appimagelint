import os
from typing import Iterable, Mapping, Union

import xdg

from . import load_json, OutOfDateError, _get_cache_logger, store_json, CacheBase


class JSONFileCacheBase(CacheBase):
    """
    Template method kind of class that requires very little configuration by actual instances and implements most
    functionality already, based on primitives.
    """

    @classmethod
    def _get_logger(cls):
        return _get_cache_logger()

    @classmethod
    def _fetch_data(cls):
        """
        Fetch cache. Must be overridden by subclasses.
        :return: cache file's path
        """
        raise NotImplementedError

    @classmethod
    def _load(cls):
        cache_files = list(cls._find_cache_files())

        for path, is_fallback in cache_files:
            try:
                return load_json(path), is_fallback
            except FileNotFoundError:
                pass
        else:
            raise OutOfDateError("cache file missing, update required")

    @classmethod
    def _store(cls, data, path: str):
        store_json(path, data)

    @classmethod
    def update_now(cls, save_to_bundled_cache: bool = False):
        """
        Force cache update.
        :return:
        """

        if save_to_bundled_cache:
            cache_dir = cls._bundled_cache_base_path()
        else:
            cache_dir = cls._user_cache_base_path()

        os.makedirs(cache_dir, exist_ok=True)

        path = os.path.join(cache_dir, cls._cache_file_name())

        data = cls._fetch_data()
        cls._store(data, path)

    @classmethod
    def get_data(cls, raise_on_error=False) -> Union[Mapping, Iterable]:
        """
        Returns cached data.
        If the data is out of date, the method will attempt to update them (if possible).
        In case fetching the latest data fails, the method will return the cached data anyway unless raise_on_error
        is set to True.
        If this is impossible, an :class:`OutOfDateError` is thrown even if raise_on_error is set to False.

        :return: data represented by cache class
        :raises OutOfDateError: in case data is out of date, see method docstring for details
        """

        logger = cls._get_logger()

        cached_data = None

        try:
            cached_data, is_fallback = cls._load()

        except OutOfDateError as e:
            logger.debug("OutOfDateError: {}".format(" ".join(e.args)))

            # store cached data for use in next block (if possible, i.e., it's valid data)
            if e.cached_data is not None:
                cached_data = e.cached_data

        else:
            # just a fancy debug message, we don't necessarily have to update, the file might be recent enough
            if is_fallback:
                cls._get_logger().debug("found cached data in fallback location")

            logger.debug("Cache still up to date, no update required")

            return cached_data

        logger.debug("data out of date, updating")

        try:
            new_data = cls._fetch_data()
        except Exception as e:
            if not raise_on_error:
                if cached_data is not None:
                    logger.warning("codebase changed since last update, but updating failed, using cached data")
                    logger.exception(e)
                    return cached_data
                else:
                    raise

            raise

        # store updated data in user cache
        user_cache_file_path = os.path.join(cls._user_cache_base_path(), cls._cache_file_name())
        cls._store(new_data, user_cache_file_path)

        return new_data
