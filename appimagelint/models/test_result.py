class TestResult:
    def __init__(self, success: bool, message: str):
        self._success = success
        self._message = message

    def success(self):
        return self._success

    def message(self):
        return self._message

    def __repr__(self):
        return "TestResult({}, {})".format(self._success, repr(self._message))
