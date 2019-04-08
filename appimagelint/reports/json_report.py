import json

from appimagelint._logging import make_logger
from . import ReportBase


class JSONReport(ReportBase):
    @staticmethod
    def _get_logger():
        return make_logger("json_report")

    def _make_json(self):
        obj = {
            "results": {
                path: [
                    {
                        "name": check.name(),
                        "results": [
                            {
                                "id": res.id(),
                                "success": res.success(),
                                "message": res.message()
                            } for res in results
                        ]
                    } for check, results in checks.items()
                ] for path, checks in self._results.items()
            }
        }

        return obj

    def to_str(self):
        return json.dumps(self._make_json(), indent=4)

    def write(self, path: str):
        logger = self._get_logger()

        logger.info("Writing JSON report to {}".format(path))
        with open(path, "w") as f:
            json.dump(self._make_json(), f, indent=4)
