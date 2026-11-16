"""Share the current pytest item and final outcomes with the CI progress process."""

import json
import os
from pathlib import Path


def pytest_configure(config):
    path = os.environ.get("SMARTUP_CURRENT_TEST_FILE")
    if path:
        config.pluginmanager.register(PhaseProgress(Path(path)))


class PhaseProgress:
    def __init__(self, path):
        self.path = path
        self.titles = {}
        self.results = {}
        self.current = ""
        self.reports = {}

    def publish(self):
        snapshot = {
            "total": len(self.titles),
            "current": self.current,
            "passed": sum(status == "passed" for status in self.results.values()),
            "failed": sum(status == "failed" for status in self.results.values()),
            "skipped": sum(status == "skipped" for status in self.results.values()),
            "last_failed": next((self.titles[node] for node in reversed(self.results)
                                 if self.results[node] == "failed"), ""),
        }
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)

    def pytest_collection_finish(self, session):
        self.titles = {item.nodeid: getattr(item.obj, "__allure_display_name__", None) or item.name
                       for item in session.items}
        self.publish()

    def pytest_runtest_logstart(self, nodeid, location):
        self.current = self.titles[nodeid]
        self.reports = {}
        self.publish()

    def pytest_runtest_logreport(self, report):
        self.reports[report.when] = report.outcome
        if report.when != "teardown":
            return
        outcomes = self.reports.values()
        # The Order runner emits "rerun" in place of a provisional failure.
        if "rerun" in outcomes:
            return
        if "failed" in outcomes:
            result = "failed"
        elif "skipped" in outcomes:
            result = "skipped"
        elif self.reports.get("call") == "passed":
            result = "passed"
        else:
            return
        self.results[report.nodeid] = result
        self.current = ""
        self.publish()
