# interface for caches
from typing import Union, Mapping, Iterable


class CacheBase:
    """
    Interface for caches.
    """

    @classmethod
    def force_update(cls):
        """
        Force cache update.
        :return:
        """

        raise NotImplementedError()

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

        raise NotImplementedError()
