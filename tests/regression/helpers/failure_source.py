"""Run-time source coordinates and a fallback for older pytest tracebacks."""
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
PROJECT_PATH = r"(?:tests|utils|scripts)/(?:[\w.-]+/)*[\w.-]+\.py"
TRACE_LINE = re.compile(rf"^\s*({PROJECT_PATH}):([1-9]\d*):(?: in (\w+))?", re.MULTILINE)


def capture_failure_source(item, traceback):
    """Record coordinates at failure time so later edits cannot shift the line."""
    _, first_line, _ = item.location
    runner = Path(item.path).relative_to(ROOT).as_posix()
    source = {"test": f"{runner}:{first_line + 1}"}
    for entry in traceback:
        path = Path(str(entry.path))
        if not path.is_relative_to(ROOT):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if re.fullmatch(PROJECT_PATH, relative):
            source["failure"] = f"{relative}:{entry.lineno + 1}"
            if relative.startswith(("tests/regression/test_orders/business_cases/",
                                    "tests/regression/test_orders/setup_cases/")) or relative == runner:
                source["action"] = source["failure"]
    repository = os.getenv("GITHUB_REPOSITORY", "")
    sha = os.getenv("GITHUB_SHA", "")
    if (os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("GITHUB_SERVER_URL") == "https://github.com"
            and re.fullmatch(r"[\w.-]+/[\w.-]+", repository) and re.fullmatch(r"[0-9a-f]{40}", sha)):
        source.update(repository=repository, revision=sha)
    return source


def failure_locations(result, phase_data):
    """Use the coordinates for this attempt, or only lines present in its archived trace."""
    source = phase_data.get("source") or {}
    test_module, _, function = result["fullName"].partition("#")
    runner = test_module.replace(".", "/") + ".py"
    test_path = source.get("test", runner)
    failure = source.get("failure")
    if not source:
        for path, line, _ in TRACE_LINE.findall(result.get("statusDetails", {}).get("trace", "")):
            failure = f"{path}:{line}"
            if path == runner:
                test_path = failure
    locations = [("Test funksiyasi", test_path, function)]
    action = source.get("action")
    if action and action not in (test_path, failure):
        locations.append(("Testdagi chaqiruv", action, None))
    if failure:
        locations.append(("Xato chiqqan qator", failure, None))
    links = []
    repository, revision = source.get("repository", ""), source.get("revision", "")
    if re.fullmatch(r"[\w.-]+/[\w.-]+", repository) and re.fullmatch(r"[0-9a-f]{40}", revision):
        for label, coordinate, _ in locations:
            path, _, line = coordinate.rpartition(":")
            if re.fullmatch(PROJECT_PATH, path) and re.fullmatch(r"[1-9]\d*", line):
                links.append({"type": "link", "name": label,
                              "url": f"https://github.com/{repository}/blob/{revision}/{path}#L{line}"})
    return [(label, loc + (" · " + func if func else "")) for label, loc, func in locations], links
