"""Track A2 table loads and requests started by a confirmation button."""
from contextlib import contextmanager
from pathlib import Path
from time import monotonic
from urllib.parse import unquote, urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.base_pages import A2_LOADER_APPEARANCE_MS, UI_TIMEOUT_MS
from utils.base_pages.angular_page_errors import check_observed_error


_GRID_OBSERVER = Path(__file__).with_name("angular_grid_render.js").read_text(encoding="utf-8")


class AngularPageRequests:
    def __init__(self, page):
        self.page = page
        self.route = None
        self.latest_table = None
        self.pending = set()
        self.finished = None
        self.confirmation_route = None
        self.confirmed_requests = set()
        page.add_init_script(script=_GRID_OBSERVER)
        page.evaluate(_GRID_OBSERVER)
        page.on("request", self._started)
        page.on("requestfinished", self._finished)
        page.on("requestfailed", self._failed)

    def _started(self, request):
        if request.method != "POST":
            return
        url = urlsplit(request.url)
        path = unquote(url.path)
        if self.confirmation_route is not None:
            host, form = self.confirmation_route
            if url.netloc == host and path.startswith((form + "$", form + ":")):
                self.confirmed_requests.add(request)
        path, _, action = path.rpartition(":")
        route = (url.netloc, path)
        if action == "model":
            self.route = route
            self.pending.clear()
            self.finished = None
            self.latest_table = None
        elif route == self.route and action:
            # Tab grids also use names such as form_table or currency_rates.
            # Only a paginated data query can establish fresh grid evidence.
            try:
                data = request.post_data_json
            except (PlaywrightError, ValueError, TypeError):
                data = None
            params = data.get("p") if isinstance(data, dict) else None
            if isinstance(params, dict) and {"column", "filter", "offset", "limit"}.issubset(params):
                self.latest_table = request
                self.pending.add(request)
            elif action.startswith("table"):
                self.latest_table = None
                self.pending.add(request)

    def _finished(self, request):
        self.confirmed_requests.discard(request)
        if request in self.pending:
            self.pending.discard(request)
            self.finished = request

    def grid_result_rendered(self, grid):
        request = self.latest_table
        url = urlsplit(self.page.url)
        route = (url.netloc, unquote(url.path).replace("/a2/", "/b/", 1))
        if request is None or self.route != route:
            return False
        if request in self.pending and grid.evaluate(
            "grid => grid.closest('main')?.querySelectorAll('smt-data-table, smt-table:not(smt-data-table smt-table)').length === 1"
        ):
            # A previous row can remain clickable while the new body downloads.
            self._wait_for_requests(self.pending, UI_TIMEOUT_MS, "A2 jadval so‘rovi")
        if request is not self.finished or self.pending:
            return False
        response = request.response()
        if not response or not response.ok:
            return False
        rendered = grid.evaluate("(grid, timing) => window.__smartupGridRendered?.(grid, timing) === true",
                                 {"url": request.url, "startTime": request.timing["startTime"]})
        # Protocol events are dispatched during the DOM read as well.
        return rendered and request is self.latest_table and not self.pending

    def wait_for_initial_table(self, timeout):
        url = urlsplit(self.page.url)
        path = unquote(url.path).replace("/a2/", "/b/", 1)
        if not path.endswith("_list") or self.route != (url.netloc, path):
            return
        if self.finished is not None and not self.pending:
            return

        def table_finished(request):
            return request is self.finished and not self.pending

        start = monotonic()
        try:
            self.page.wait_for_event("requestfinished", predicate=table_finished,
                                     timeout=min(timeout, A2_LOADER_APPEARANCE_MS))
        except PlaywrightTimeoutError:
            # Client-side tables do not send a table query at all. Once a
            # real request has begun, give it the remaining UI timeout.
            if self.pending:
                remaining = max(1, timeout - (monotonic() - start) * 1000)
                self.page.wait_for_event("requestfinished", predicate=table_finished, timeout=remaining)

    def _failed(self, request):
        self.pending.discard(request)
        self.confirmed_requests.discard(request)

    @contextmanager
    def confirming(self):
        url = urlsplit(self.page.url)
        self.confirmation_route = (url.netloc, unquote(url.path).replace("/a2/", "/b/", 1))
        try:
            yield
        finally:
            self.confirmation_route = None

    def wait_for_confirmation(self, timeout):
        # The dialog can disappear while its POST is still processing on the
        # same URL. Return immediately for purely client-side confirmations.
        self._wait_for_requests(self.confirmed_requests, timeout, "A2 tasdiqlash so‘rovi")

    def _wait_for_requests(self, pending, timeout, description):
        deadline = monotonic() + timeout / 1000 if timeout else None
        while pending:
            remaining = (deadline - monotonic()) * 1000 if deadline is not None else None
            if remaining is not None and remaining <= 0:
                raise AssertionError(f"{description} belgilangan vaqtda tugamadi")
            try:
                # A cancelled request emits requestfailed instead of
                # requestfinished. Recheck the set in that case as well.
                self.page.wait_for_event("requestfinished", predicate=lambda _: not pending,
                                         timeout=250 if remaining is None else min(remaining, 250))
            except PlaywrightTimeoutError:
                check_observed_error(self.page)
