"""Publish CI reports atomically and retain the newest run/attempts on disk."""
import errno
import os
import re
import socketserver
import time
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path("/reports")
INCOMING = ROOT / ".incoming"
PENDING = INCOMING / "publisher.partial"
SOCKET = INCOMING / "publisher.sock"
REPORT = re.compile(r"([0-9]+)-([0-9]+)\.html", re.ASCII)
KEEP = 3
MIN_FREE = 5_000_000_000
MAX_UPLOAD = 4 * 1024**3


def run_order(path):
    return tuple(map(int, REPORT.fullmatch(path.name).groups()))


def reports():
    return sorted((p for p in ROOT.iterdir()
                   if REPORT.fullmatch(p.name) and not p.is_symlink() and p.is_file()),
                  key=run_order)


def available():
    fs = os.statvfs(ROOT)
    return fs.f_bavail * fs.f_frsize


def remove_report(path):
    path.unlink()
    print(f"Removed Allure report {path.name}", flush=True)


def prune():
    saved = reports()
    while saved and (len(saved) > KEEP or available() < MIN_FREE):
        remove_report(saved.pop(0))


def make_room(destination, size):
    saved = reports()
    if sum(run_order(p) > run_order(destination) for p in saved) >= KEEP:
        return 409
    needed = MIN_FREE + size
    older = [p for p in saved if run_order(p) < run_order(destination)]
    if available() + sum(p.stat().st_blocks * 512 for p in older) < needed:
        return 507
    for path in older:
        if available() >= needed:
            break
        remove_report(path)
    return 0 if available() >= needed else 507


class Publisher(BaseHTTPRequestHandler):
    timeout = 60

    def address_string(self):
        return "reports-nginx"

    def do_PUT(self):
        prefix = "/upload/"
        name = self.path.removeprefix(prefix)
        if not self.path.startswith(prefix) or not REPORT.fullmatch(name):
            return self.send_error(404)
        length = self.headers.get("Content-Length", "")
        if not re.fullmatch(r"[0-9]{1,12}", length) or int(length) == 0:
            return self.send_error(411)
        size = int(length)
        if size > MAX_UPLOAD:
            return self.send_error(413)
        destination = ROOT / name
        status = make_room(destination, size)
        if status:
            return self.send_error(status)
        existed = destination.exists()
        try:
            with PENDING.open("xb") as out:
                os.posix_fallocate(out.fileno(), 0, size)
                remaining = size
                while remaining:
                    if available() < MIN_FREE:
                        return self.send_error(507)
                    chunk = self.rfile.read(min(remaining, 1024**2))
                    if not chunk:
                        return self.send_error(400, "Incomplete upload")
                    out.write(chunk)
                    remaining -= len(chunk)
                out.flush()
                os.fsync(out.fileno())
            if available() < MIN_FREE:
                return self.send_error(507)
            PENDING.replace(destination)
            prune()
        except OSError as exc:
            if exc.errno not in (errno.ENOSPC, errno.EDQUOT):
                raise
            return self.send_error(507)
        finally:
            PENDING.unlink(missing_ok=True)
        self.send_response(204 if existed else 201)
        self.end_headers()


class ReportServer(socketserver.UnixStreamServer):
    # One disk reservation and atomic replacement at a time.
    next_prune = 0

    def service_actions(self):
        if time.monotonic() >= self.next_prune:
            prune()
            self.next_prune = time.monotonic() + 60


if __name__ == "__main__":
    os.umask(0o077)
    INCOMING.mkdir(mode=0o700, exist_ok=True)
    SOCKET.unlink(missing_ok=True)
    PENDING.unlink(missing_ok=True)
    with ReportServer(str(SOCKET), Publisher) as server:
        prune()
        server.serve_forever()
