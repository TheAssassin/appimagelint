class TestResult:
    def __init__(self, success: bool, id: str, message: str):
        self._success = success
        self._message = message
        self._id = id

    def success(self):
        return self._success

    def message(self):
        return self._message

    def id(self):
        return self._id

    def __repr__(self):
        return "TestResult({}, {})".format(self._success, repr(self._message))
