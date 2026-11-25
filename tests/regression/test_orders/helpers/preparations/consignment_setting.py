"""Borrow the Order consignment setting in the API baseline's test branch."""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
from tempfile import gettempdir

import allure
from playwright.sync_api import expect

from utils.base_pages import A2_DOCUMENT_TIMEOUT_MS
from utils.base_pages.auto_base_page import AutoBasePage


MODEL = "/trade/pref/deal_setting:model"
SAVE = re.compile(r"/trade/pref/deal_setting:save(?:\?|$)")
FLAG = "consignment_allow"


@contextmanager
def order_settings_lock(baseline, *, delivery_addresses=False):
    # An address preference may be shared across branches of the same company.
    scope = "delivery-addresses" if delivery_addresses else str(baseline["filial_id"])
    identity = "|".join((str(baseline["url"]), str(baseline["company_code"]), scope))
    key = sha256(identity.encode()).hexdigest()[:24]
    connection = sqlite3.connect(Path(gettempdir()) / f"smartup-consignment-{key}.lock", timeout=120)
    try:
        connection.execute("BEGIN IMMEDIATE")
        yield
    finally:
        connection.close()


def _open_preference(page, filial_id):
    base = AutoBasePage(page)
    with page.expect_response(lambda r: r.url.split("?")[0].endswith(MODEL)) as loaded:
        base.open_route("trade/pref/system_setting", timeout=A2_DOCUMENT_TIMEOUT_MS)
        base.tab(name="Заказ")
    response = loaded.value
    request = response.request
    headers = {key: value for key, value in request.all_headers().items()
               if key in {"filial_id", "user_id", "company_id", "project_code", "lang_code"}}
    if response.status != 200 or headers.get("filial_id") != str(filial_id):
        raise AssertionError("Order sozlamasi test filialida ochilmadi")
    model = response.json()[2]
    if model[FLAG] not in {"N", "Y"}:
        raise AssertionError("Konsignatsiya sozlamasi noma’lum qiymatga ega")
    return model, response.url, headers


def _change(page, model, url, headers, enabled):
    expected = "Y" if enabled else "N"
    if model[FLAG] == expected:
        return
    toggle = page.get_by_role("checkbox", name="Разрешить консигнацию", exact=True)
    expect(toggle).to_have_attribute("aria-checked", "false" if enabled else "true")
    AutoBasePage(page).checkbox(locator=toggle, checked=enabled)

    def read_current():
        response = page.request.post(url, headers=headers, data={}, max_retries=0)
        try:
            if response.status != 200:
                raise AssertionError("Filialning joriy Order sozlamalarini o‘qib bo‘lmadi")
            return response.json()[2]
        finally:
            response.dispose()

    def save(route):
        data = route.request.post_data_json
        if (data.get(FLAG) != expected or route.request.headers.get("filial_id") != headers["filial_id"]
                or read_current() != model):
            route.abort()
            return
        # A2 serializes an untouched blank minimum advance as zero on any Save.
        percent = "deal_booked_payment_min_percent"
        if model[percent] == "" and data.get(percent) in ("0", 0):
            data[percent] = ""
        route.continue_(post_data=json.dumps(data))

    page.route(SAVE, save)
    try:
        with page.expect_response(lambda r: SAVE.search(r.url) is not None) as saved:
            AutoBasePage(page).click(name="Сохранить", exact=True)
        if saved.value.status != 200:
            raise AssertionError("Konsignatsiya sozlamasini saqlashda xato")
    finally:
        page.unroute(SAVE, save)
    if read_current() != {**model, FLAG: expected}:
        raise AssertionError("Konsignatsiya yoki boshqa Order sozlamasi kutilganiga mos emas")


@contextmanager
def temporary_consignment(open_page, filial_id):
    restore = False
    try:
        with allure.step("Test filialida konsignatsiyani tekshirish va zarur bo‘lsa yoqish"):
            with open_page() as page:
                model, url, headers = _open_preference(page, filial_id)
                restore = model[FLAG] == "N"
                _change(page, model, url, headers, True)
        yield True
    finally:
        if restore:
            with allure.step("Test filialining konsignatsiya sozlamasini tiklash"):
                with open_page() as page:
                    # Load the latest form so concurrent edits to other fields survive.
                    model, url, headers = _open_preference(page, filial_id)
                    _change(page, model, url, headers, False)
