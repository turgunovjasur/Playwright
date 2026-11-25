"""Test kompaniyasida klientning turli yetkazish manzillarini vaqtincha yoqish."""
from contextlib import contextmanager
from urllib.parse import urlsplit

from playwright.sync_api import expect

from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from utils.base_pages.auto_base_page import AutoBasePage

ROUTE = "trade/tdeal/order/order_list"
FLAG = "allow_person_delivery_addresses"


@contextmanager
def temporary_delivery_addresses(open_page, baseline, directory):
    state = RegressionSetupState(directory / "delivery-address-setting.json", baseline.copy())
    endpoint = ROUTE + ":load_order_settings"

    def change(page, api, before, value):
        base = AutoBasePage(page)
        base.open_route(ROUTE, heading="Заказы")
        base.click(name="Настройки заказа", exact=True)
        dialog = page.get_by_role("dialog").filter(has=page.get_by_role("heading", name="Настройки заказа"))
        label = dialog.get_by_text("Разрешить использовать разные адреса доставки", exact=True)
        switch = label.locator("xpath=ancestor::*[.//*[@role='switch']][1]").get_by_role("switch")
        expect(switch).to_have_attribute("aria-checked", "false" if value == "Y" else "true")
        base.click(locator=switch)
        expect(switch).to_have_attribute("aria-checked", "true" if value == "Y" else "false")
        if api.call(endpoint, {}) != before:
            raise AssertionError("Order sozlamalari tahrir vaqtida o‘zgardi")
        with page.expect_response(lambda res: urlsplit(res.url).path.endswith("/" + ROUTE + ":save_order_settings")) as saved:
            base.click(name="Сохранить", root=dialog, exact=True)
        if not saved.value.ok or api.call(endpoint, {}) != {**before, FLAG: value}:
            raise AssertionError("Yetkazish manzili yoki boshqa Order sozlamasi kutilgan holatda emas")

    restore = False
    try:
        api = state.user()
        before = api.call(endpoint, {})
        if before[FLAG] not in ("Y", "N"):
            raise AssertionError("Manzil sozlamasining holati aniqlanmadi")
        restore = before[FLAG] == "N"
        if restore:
            with open_page() as page:
                change(page, api, before, "Y")
        yield
    finally:
        try:
            if restore:
                # Re-read before restoration so unrelated subsequent edits survive.
                api = state.user(fresh=True)
                current = api.call(endpoint, {})
                if current[FLAG] != "N":
                    with open_page() as page:
                        change(page, api, current, "N")
        finally:
            state.close()
