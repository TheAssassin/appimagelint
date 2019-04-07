import os
from typing import Iterable, Mapping, Union

from . import load_json, OutOfDateError, _get_logger, store_json, CacheBase


class DefaultCacheImplBase(CacheBase):
    """
    Template method kind of class that requires very little configuration by actual instances and implements most
    functionality already, based on primitives.
    """

    @classmethod
    def _get_logger(cls):
        return _get_logger()

    @classmethod
    def _cache_file_path(cls):
        """
        Get cache file path. Must be overridden by subclasses.
        :return: cache file's path
        """
        raise NotImplementedError

    @classmethod
    def _fetch_data(cls):
        """
        Fetch cache. Must be overridden by subclasses.
        :return: cache file's path
        """
        raise NotImplementedError

    @classmethod
    def _load(cls):
        return load_json(cls._cache_file_path())

    @classmethod
    def _store(cls, data):
        store_json(cls._cache_file_path(), data)

    @classmethod
    def force_update(cls):
        """
        Force cache update.
        :return:
        """

        data = cls._fetch_data()
        cls._store(data)

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
            cached_data = cls._load()
        except OutOfDateError as e:
            logger.debug("OutOfDateError: {}".format(" ".join(e.args)))

            # store cached data for use in next block (if possible, i.e., it's valid data)
            if e.cached_data is not None:
                cached_data = e.cached_data
        else:
            logger.debug("{} still up to date, no update required".format(os.path.basename(cls._cache_file_path())))
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

        cls._store(new_data)
        return new_data
