from typing import Union, Iterable, Mapping


class OutOfDateError(Exception):
    def __init__(self, message: str, cached_data: Union[Iterable, Mapping] = None):
        self.args = (message,)
        self.cached_data = cached_data
