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
from tests.regression.test_orders.helpers.navigation import OrderPage


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
    base = OrderPage(page)
    with page.expect_response(lambda r: r.url.split("?")[0].endswith(MODEL)) as loaded:
        base.open_route("trade/pref/system_setting", timeout=A2_DOCUMENT_TIMEOUT_MS)
        base.tab(name="Заказ")
    response = loaded.value
    request = response.request
    headers = {key: value for key, value in request.all_headers().items()
               if key in {"filial_id", "user_id", "company_id", "project_code", "lang_code", "formurl"}}
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
    OrderPage(page).checkbox(locator=toggle, checked=enabled)

    def read_current():
        response = page.request.post(url, headers=headers, data={}, max_retries=0)
        try:
            if response.status != 200:
                raise AssertionError("Filialning joriy Order sozlamalarini o‘qib bo‘lmadi")
            return response.json()[2]
        finally:
            response.dispose()

    current = read_current()
    saved_fields = set()
    conflicts = []

    def save(route):
        data = route.request.post_data_json
        if (data.get(FLAG) != expected or route.request.all_headers().get("filial_id") != headers["filial_id"]):
            route.fulfill(status=409, body="Unexpected consignment flag or branch")
            return
        # The model also contains read-only option lists, e.g. available roles.
        # Check every preference the form is about to write.
        saved_fields.update(data)
        conflicts.extend(sorted(key for key in saved_fields
                                if key not in model or key not in current or current[key] != model[key]))
        if conflicts:
            route.fulfill(status=409, body="Order settings changed")
            return
        # A2 serializes an untouched blank minimum advance as zero on any Save.
        percent = "deal_booked_payment_min_percent"
        if model[percent] == "" and data.get(percent) in ("0", 0):
            data[percent] = ""
        route.continue_(post_data=json.dumps(data))

    page.route(SAVE, save)
    try:
        with page.expect_response(lambda r: SAVE.search(r.url) is not None) as saved:
            OrderPage(page).click(name="Сохранить", exact=True)
        if conflicts:
            raise AssertionError("Saqlashdan oldin filial sozlamalari o‘zgardi: " + ", ".join(conflicts))
        if saved.value.status != 200:
            raise AssertionError(f"Konsignatsiya sozlamasini saqlash HTTP {saved.value.status}")
    finally:
        page.unroute(SAVE, save)
    after = read_current()
    expected_model = {**model, FLAG: expected}
    changed = sorted(key for key in saved_fields if key not in after or after[key] != expected_model[key])
    if FLAG not in saved_fields or changed:
        raise AssertionError("Saqlangandan keyin filial sozlamalari mos emas: " + ", ".join(changed or [FLAG]))


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
