#!/usr/bin/env python3
"""Open an Allure report and stop its local server after the report tab is closed."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import threading
import time
import uuid
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "test-results" / "allure-report"
HEARTBEAT_TIMEOUT_SECONDS = 12
SERVER_STATUS_PATH = "/__allure_status"
SERVER_HEARTBEAT_PATH = "/__allure_heartbeat"
SERVER_STATE_VERSION = 1


def _log(message: str) -> None:
    """Log without letting a closed parent stream stop the report server."""
    try:
        print(message, flush=True)
    except (BrokenPipeError, OSError):
        pass


def _open_browser(url: str) -> bool:
    try:
        opened = webbrowser.open(url)
    except Exception as exc:
        _log(f"Allure report brauzerda ochilmadi: {type(exc).__name__}: {exc}")
        return False
    if not opened:
        _log(f"Allure report brauzerda ochilmadi: {url}")
    return opened


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


def _inject_heartbeat(content: str) -> str:
    """Inject heartbeat before app scripts, with a nonstandard HTML fallback."""
    lower_content = content.lower()
    head_start = lower_content.find("<head")
    if head_start >= 0:
        head_end = content.find(">", head_start)
        if head_end >= 0:
            return (
                f"{content[:head_end + 1]}{HEARTBEAT_SCRIPT}"
                f"{content[head_end + 1:]}"
            )

    closing_body = "</body>"
    if closing_body in content:
        return content.replace(
            closing_body,
            f"{HEARTBEAT_SCRIPT}{closing_body}",
            1,
        )
    return f"{content}\n{HEARTBEAT_SCRIPT}"


class ReportHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        """Keep the test runner output focused on test/report status."""

    def do_GET(self):
        path = urlparse(self.path).path
        if path == SERVER_HEARTBEAT_PATH:
            self.server.last_heartbeat = time.monotonic()
            self.send_response(204)
            self.end_headers()
            return

        if path == SERVER_STATUS_PATH:
            self.server.last_heartbeat = time.monotonic()
            encoded = json.dumps(
                {
                    "version": SERVER_STATE_VERSION,
                    "server_id": self.server.server_id,
                    "pid": os.getpid(),
                    "port": self.server.server_port,
                    "report_dir": str(self.server.report_dir),
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)
            return

        if path in {"/", "/index.html"}:
            index = Path(self.directory) / "index.html"
            if index.exists():
                content = index.read_text(encoding="utf-8")
                content = _inject_heartbeat(content)
                encoded = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(encoded)
                return

        super().do_GET()


class ReportServer(ThreadingHTTPServer):
    """One local server for one generated Allure report directory."""

    daemon_threads = True

    def __init__(self, address, handler, *, report_dir: Path, server_id: str):
        super().__init__(address, handler)
        self.last_heartbeat = time.monotonic()
        self.report_dir = report_dir
        self.server_id = server_id


def _server_files(report_dir: Path) -> tuple[Path, Path]:
    prefix = f".{report_dir.name}-server"
    return report_dir.parent / f"{prefix}.json", report_dir.parent / f"{prefix}.lock"


def _read_server_state(state_path: Path) -> dict | None:
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    required = {"version", "server_id", "pid", "port", "report_dir", "url"}
    if not isinstance(state, dict) or not required.issubset(state):
        return None
    return state


def _server_is_healthy(state: dict, report_dir: Path) -> bool:
    if state.get("version") != SERVER_STATE_VERSION:
        return False
    if state.get("report_dir") != str(report_dir):
        return False
    port = state.get("port")
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65_535:
        return False
    url = f"http://127.0.0.1:{port}"
    if state.get("url") != url:
        return False

    try:
        with urlopen(f"{url}{SERVER_STATUS_PATH}", timeout=1) as response:
            status = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return False

    return (
        status.get("version") == SERVER_STATE_VERSION
        and status.get("server_id") == state.get("server_id")
        and status.get("pid") == state.get("pid")
        and status.get("port") == port
        and status.get("report_dir") == str(report_dir)
    )


def _write_server_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = state_path.with_suffix(f"{state_path.suffix}.{os.getpid()}.tmp")
    temporary_path.write_text(json.dumps(state), encoding="utf-8")
    temporary_path.replace(state_path)


def _remove_owned_server_state(state_path: Path, server_id: str) -> None:
    state = _read_server_state(state_path)
    if state and state.get("server_id") != server_id:
        return
    try:
        state_path.unlink()
    except FileNotFoundError:
        pass


def open_report(report_dir: Path, port: int) -> int:
    report_dir = report_dir.resolve()
    if not report_dir.is_dir() or not (report_dir / "index.html").is_file():
        _log(f"Allure report topilmadi: {report_dir}")
        return 1

    state_path, lock_path = _server_files(report_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        state = _read_server_state(state_path)
        if state and _server_is_healthy(state, report_dir):
            url = state["url"]
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            _log(f"Allure report server qayta ishlatildi: {url}")
            _log("Report tabini yoping — lokal Allure server avtomatik to'xtaydi.")
            return 0 if _open_browser(url) else 1

        try:
            state_path.unlink()
        except FileNotFoundError:
            pass

        handler = partial(ReportHandler, directory=str(report_dir))
        server_id = uuid.uuid4().hex
        server = ReportServer(
            ("127.0.0.1", port),
            handler,
            report_dir=report_dir,
            server_id=server_id,
        )
        url = f"http://127.0.0.1:{server.server_port}"
        _write_server_state(
            state_path,
            {
                "version": SERVER_STATE_VERSION,
                "server_id": server_id,
                "pid": os.getpid(),
                "port": server.server_port,
                "report_dir": str(report_dir),
                "url": url,
            },
        )
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def stop_when_inactive():
        while True:
            time.sleep(1)
            if time.monotonic() - server.last_heartbeat > HEARTBEAT_TIMEOUT_SECONDS:
                _log("Allure report tab yopildi; lokal server to'xtatildi.")
                server.shutdown()
                return

    try:
        _log(f"Allure report ochildi: {url}")
        _log("Report tabini yoping — lokal Allure server avtomatik to'xtaydi.")
        if not _open_browser(url):
            return 1
        threading.Thread(target=stop_when_inactive, daemon=True).start()
        server.serve_forever()
    except KeyboardInterrupt:
        _log("Allure server to'xtatildi.")
    finally:
        server.server_close()
        _remove_owned_server_state(state_path, server_id)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Allure reportni brauzer yopilganda avtomatik to'xtaydigan serverda ochadi.")
    parser.add_argument("report_dir", nargs="?", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--port", type=int, default=0, help="Lokal port (default: bo'sh port tanlanadi).")
    args = parser.parse_args()
    return open_report(args.report_dir.resolve(), args.port)


if __name__ == "__main__":
    raise SystemExit(main())
