"""Joriy URL orqali legacy yoki A2 page-objectga chaqiruvlarni uzatish."""

import re
from functools import wraps
from urllib.parse import urlsplit

from playwright.sync_api import expect

from utils.base_pages.angular_base_page import AngularBasePage
from utils.base_pages.base_page import BasePage
from utils.base_pages.page_diagnostics import expectation_gate, report_page_expectation

# Logical Angular routes (kernel ng-serve AND packaged deploy under ``/a2``).
KERNEL_ANGULAR_PREFIXES = (
    "/auth",
    "/biruni",
    "/trade",
    "/anor",
    "/billing",
    "/core",
    "/finance",
    "/dwh",
    "/supply",
    "/wms",
    "/darmon",
    "/sb",
    "/plugins",
)


def angular_route_path(url):
    """Path without packaged ``/a2`` prefix.

    Local ``ng serve``: ``/anor/mr/user_list``.
    Prod/test SPA: ``/a2/anor/mr/user_list`` → same logical ``/anor/mr/user_list``.
    Legacy Metronic stays on ``/`` + hash ``#!/…`` — prefix is not stripped from hash.
    """
    path = urlsplit(str(url or "")).path or "/"
    if path == "/a2":
        return "/"
    if path.startswith("/a2/"):
        rest = path[3:]
        return rest if rest.startswith("/") else f"/{rest}"
    return path


def is_angular_page_url(url):
    path = urlsplit(str(url or "")).path
    if path == "/a2" or path.startswith("/a2/"):
        return True
    logical = angular_route_path(url)
    return any(logical == prefix or logical.startswith(f"{prefix}/") for prefix in KERNEL_ANGULAR_PREFIXES)


class AutoBasePage:
    """Har bir public metod chaqiruvida joriy sahifaga mos helperni tanlaydi.

    URL path'ida packaged ``/a2/…`` (prod/test) yoki shu route'lar
    prefix'siz (local ng-serve: ``/auth``, ``/trade``, ``/anor``, …)
    bo'lsa AngularBasePage, aks holda BasePage (legacy hash) ishlaydi.
    Public metodlarning parametrlari va return kontrakti ikkala helperda bir xil.
    Locator va UI amallari tanlangan helperda bajariladi; xatoda boshqa helper
    sinalmaydi. Explicit CSS selector va model nomlari avtomatik tarjima qilinmaydi.

    Forma ochadigan amaldan keyin ``expect_page(url=..., heading=...)``
    chaqirilsin: u destination URLni kutib, keyin helperni tanlaydi.
    ``root`` orqali berilgan Locator ham yangi formaga mos bo'lishi kerak.
    """

    def __init__(self, page):
        self.page = page
        self._legacy = BasePage(page)
        self._angular = AngularBasePage(page)

    # Sana hisoblash DOM yoki sahifa turiga bog'liq emas.
    date = staticmethod(BasePage.date)

    def _current_base(self):
        if is_angular_page_url(self.page.url):
            return self._angular
        return self._legacy

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

        method = getattr(self._legacy, name)
        if not callable(method):
            raise AttributeError(f"{type(self).__name__!s} has no method {name!r}")

        @wraps(method)
        def dispatch(*args, **kwargs):
            # Bound metodni saqlab qolmaslik: URL chaqiruv paytida tekshiriladi.
            return getattr(self._current_base(), name)(*args, **kwargs)

        return dispatch

    @report_page_expectation
    def expect_page(
        self,
        heading=None,
        url=None,
        timeout=30_000,
        check_unblocked=True,
        root=None,
    ):
        """Kutilgan URLga o'tishni kutib, destination helper bilan tekshiradi."""
        self._legacy._validate_options(
            "expect_page", timeout=timeout, check_unblocked=check_unblocked
        )
        if heading is None and url is None:
            raise ValueError("expect_page: kamida 'heading' yoki 'url' berilishi kerak")

        if url is not None:
            if isinstance(url, re.Pattern):
                pattern = url
            else:
                pattern = re.compile(re.escape(url).replace(r"\+", r"(?:\+|%2B)"))
            expectation_gate(self.page, "url")
            try:
                expect(self.page).to_have_url(pattern, timeout=timeout)
            except AssertionError:
                current_path = angular_route_path(self.page.url)
                expected = getattr(url, "pattern", str(url))
                # Post-login Trade shell: local `/trade`, packaged `/a2/trade`.
                if (
                    "dashboard" in expected.lower()
                    and is_angular_page_url(self.page.url)
                    and (current_path == "/trade" or current_path.startswith("/trade/"))
                ):
                    url = None
                else:
                    parent_kept = any(
                        token in expected.lower()
                        for token in ("template", "+add", "+edit", "_list")
                    )
                    if (
                        heading is None
                        or current_path == "/auth"
                        or current_path.startswith("/auth/")
                        or "dashboard" in expected.lower()
                        or not is_angular_page_url(self.page.url)
                        or not parent_kept
                    ):
                        raise
                    # Kernel type-D drawers keep the parent route (template list/add).
                    url = None

        return self._current_base().expect_page(
            heading=heading,
            url=url,
            timeout=timeout,
            check_unblocked=check_unblocked,
            root=root,
        )
