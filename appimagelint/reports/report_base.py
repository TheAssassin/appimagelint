class ReportBase:
    def __init__(self, results: dict):
        self._results = results

    def to_str(self):
        raise NotImplementedError

    def write(self, path: str):
        raise NotImplementedError
