#!/usr/bin/env python3
"""Open an Allure report and stop its local server after the report tab is closed."""

from __future__ import annotations

import argparse
import threading
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "test-results" / "allure-report"
HEARTBEAT_TIMEOUT_SECONDS = 12

# The client periodically calls this endpoint while the report tab is alive.
# When the tab is closed, the server exits after the small grace period.  The
# grace period also makes a normal page refresh safe.
HEARTBEAT_SCRIPT = """
<script>
(() => {
  const heartbeat = () => fetch('/__allure_heartbeat', {cache: 'no-store'}).catch(() => {});
  heartbeat();
  window.setInterval(heartbeat, 2000);
})();
</script>
"""


class ReportHandler(SimpleHTTPRequestHandler):
    last_heartbeat = 0.0

    def log_message(self, *_args):
        """Keep the test runner output focused on test/report status."""

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/__allure_heartbeat":
            type(self).last_heartbeat = time.monotonic()
            self.send_response(204)
            self.end_headers()
            return

        if path in {"/", "/index.html"}:
            index = Path(self.directory) / "index.html"
            if index.exists():
                content = index.read_text(encoding="utf-8")
                content = content.replace("</body>", f"{HEARTBEAT_SCRIPT}</body>", 1)
                encoded = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(encoded)
                return

        super().do_GET()


def open_report(report_dir: Path, port: int) -> int:
    if not report_dir.is_dir() or not (report_dir / "index.html").is_file():
        print(f"Allure report topilmadi: {report_dir}")
        return 1

    handler = partial(ReportHandler, directory=str(report_dir))
    ReportHandler.last_heartbeat = time.monotonic()
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Allure report ochildi: {url}")
    print("Report tabini yoping — lokal Allure server avtomatik to'xtaydi.")
    webbrowser.open(url)

    def stop_when_inactive():
        while True:
            time.sleep(1)
            if time.monotonic() - ReportHandler.last_heartbeat > HEARTBEAT_TIMEOUT_SECONDS:
                print("Allure report tab yopildi; lokal server to'xtatildi.")
                server.shutdown()
                return

    threading.Thread(target=stop_when_inactive, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Allure server to'xtatildi.")
    finally:
        server.server_close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Allure reportni brauzer yopilganda avtomatik to'xtaydigan serverda ochadi.")
    parser.add_argument("report_dir", nargs="?", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--port", type=int, default=0, help="Lokal port (default: bo'sh port tanlanadi).")
    args = parser.parse_args()
    return open_report(args.report_dir.resolve(), args.port)


if __name__ == "__main__":
    raise SystemExit(main())
