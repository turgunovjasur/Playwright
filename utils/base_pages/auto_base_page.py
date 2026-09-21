"""Joriy URL orqali legacy yoki A2 page-objectga chaqiruvlarni uzatish."""

import re
from functools import wraps
from urllib.parse import urlsplit

from playwright.sync_api import expect

from utils.base_pages.angular_base_page import AngularBasePage
from utils.base_pages.base_page import BasePage
from utils.base_pages.page_diagnostics import expectation_gate, report_page_expectation


class AutoBasePage:
    """Har bir public metod chaqiruvida joriy sahifaga mos helperni tanlaydi.

    URL path'ida ``/a2/`` bo'lsa AngularBasePage, aks holda BasePage ishlaydi.
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
        if "/a2/" in urlsplit(self.page.url).path:
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
            pattern = url if isinstance(url, re.Pattern) else re.compile(re.escape(url))
            expectation_gate(self.page, "url")
            expect(self.page).to_have_url(pattern, timeout=timeout)

        return self._current_base().expect_page(
            heading=heading,
            url=url,
            timeout=timeout,
            check_unblocked=check_unblocked,
            root=root,
        )
