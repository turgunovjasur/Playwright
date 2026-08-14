"""HTTP 4xx/5xx response'lari uchun stateful FormMonitor diagnostikasi."""

from __future__ import annotations

from urllib.parse import urlsplit


MAX_PAGE_EVENTS = 20


def failed_request_label(response):
    """4xx/5xx response'ni query stringsiz qisqa yorliqqa aylantiradi."""
    try:
        status = int(response.status)
        if status < 400:
            return ""
        parts = urlsplit(str(response.url or ""))
    except (AttributeError, TypeError, ValueError):
        return ""
    return f"{status} {parts.netloc}{parts.path}"


class FailedRequestsDiagnostic:
    """Playwright response listenerining to'liq diagnostika lifecycle'i."""

    name = "failed_requests"

    def __init__(self, page, *, sample_limit=MAX_PAGE_EVENTS):
        self.page = page
        self.sample_limit = sample_limit
        self._listener_installed = False
        self.reset()

    def start(self):
        if self._listener_installed:
            return
        try:
            self.page.on("response", self._record)
        except (AttributeError, TypeError):
            return
        self._listener_installed = True

    def _record(self, response):
        label = failed_request_label(response)
        if not label:
            return
        self.count += 1
        if len(self.samples) < self.sample_limit:
            self.samples.append(label)

    def reset(self):
        self.samples = []
        self.count = 0

    def snapshot(self):
        return {
            "enabled": True,
            "execution_status": "COMPLETED",
            "count": self.count,
            "samples": list(self.samples),
        }

    def close(self):
        if not self._listener_installed:
            return
        try:
            self.page.remove_listener("response", self._record)
        except (AttributeError, TypeError, ValueError, KeyError):
            pass
        self._listener_installed = False
