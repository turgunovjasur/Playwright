"""Build the publishable HTML from Allure's disk report without buffering all attachments."""
import argparse
import base64
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SINGLE_BUNDLE = ROOT / "node_modules/@allurereport/web-awesome/dist/single"


def write_base64(source, output):
    with source.open("rb") as reader:
        # A multiple of three keeps the intermediate blocks free of padding.
        while chunk := reader.read(3 * 64 * 1024):
            output.write(base64.b64encode(chunk))


def inline_json(value):
    # Keep report strings and file names inert inside inline scripts.
    return json.dumps(value, ensure_ascii=True).replace("<", "\\u003c").encode("ascii")


def pack(report, destination):
    index = (report / "index.html").read_text(encoding="utf-8")
    match = re.search(r"window\.allureReportOptions\s*=\s*", index)
    if not match or not (report / "data/test-results").is_dir():
        raise ValueError("Expected an Allure Awesome disk report with test results")
    options, _ = json.JSONDecoder().raw_decode(index[match.end():])
    manifest = json.loads((SINGLE_BUNDLE / "manifest.json").read_text())
    with destination.open("wb") as output:
        title = html.escape(options["reportName"]).encode("utf-8")
        output.write(b'<!doctype html><html><head><meta charset="utf-8">')
        output.write(b'<meta name="viewport" content="width=device-width, initial-scale=1"><title>' + title + b'</title>')
        output.write((ROOT / "telegram_bot/deploy/report-preferences.html").read_bytes())
        output.write(b'</head><body><div id="app"></div><script>window.allure={};window.allureReportOptions=')
        output.write(inline_json(options))
        output.write(b';window.allureReportData=Object.create(null);</script>\n')
        for directory in (report / "data", report / "widgets"):
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    key = inline_json(path.relative_to(report).as_posix())
                    output.write(b'<script>window.allureReportData[' + key + b']="')
                    write_base64(path, output)
                    output.write(b'";</script>\n')
        output.write(b'<script>window.allureReportDataReady=true;</script>')
        output.write(b'<script src="data:text/javascript;base64,')
        write_base64(SINGLE_BUNDLE / manifest["main.js"], output)
        output.write(b'"></script></body></html>\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    pack(args.report, args.destination)
