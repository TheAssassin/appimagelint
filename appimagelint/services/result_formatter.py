import os
import sys

from appimagelint.colors import Colors
from appimagelint.models.test_result import TestResult
from appimagelint.symbols import Symbols


class ResultFormatter:
    _default_format = "[{symbol}] {message}"

    def __init__(self, fmt: str = None, use_colors: bool = None):
        self._fmt = fmt or self._default_format

        if use_colors is None:
            use_colors = sys.stdin.isatty()
        self._use_colors = use_colors

    def format(self, result: TestResult):
        symbol = ""

        if self._use_colors:
            if result.success():
                symbol += Colors.GREEN
                symbol += Symbols.CHECK
            else:
                symbol += Colors.RED
                symbol += Symbols.CROSS

            symbol += Colors.ENDC

        else:
            if result.success():
                symbol += Symbols.CHECK
            else:
                symbol += Symbols.CROSS

        return self._fmt.format(symbol=symbol, message=result.message())

    def __repr__(self):
        return "ResultFormatter({})".format(repr(self._default_format))
