"""TMZ limiti uchun own mahsulot va klient; limitning o‘zi UI tayyorlovidir."""
from tests.regression.helpers.retry.checkpoints import draft_or_reused_posted
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import json
import re
from urllib.parse import unquote, urlsplit
from tests.regression.helpers.retry.state import stable_uuid as uuid4
from zoneinfo import ZoneInfo

import allure
from playwright.sync_api import expect
from utils.base_pages.auto_base_page import AutoBasePage

from tests.api.client import APIError, positive_id, require_fields
from tests.api.state import CONTRACTS
from tests.regression.test_orders.helpers.preparations.resources import resource_ready, resource_status
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.test_orders.helpers.preparations.clients import prepare_order_client
from tests.regression.test_orders.helpers.flows.stock import read_stock


def persist(data, directory):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "product-limit-setup.json"
    temporary = path.with_suffix(".tmp")
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def run_prepare_product(baseline, data, directory):
    """1. Own dona mahsulot. 2. Baseline UZS narxi 7000. 3. Saved identity/narx.

    Limit baseline mahsulotiga qo‘yilmaydi: boshqa guruh orderlari ta’sir qilmaydi.
    """
    data.setdefault("orders", {})
    resource_status(data, "product", "process")
    data.update(status="process", run_id=uuid4("product_limit_setup").hex[:12], retention="retained",
                date=datetime.now(ZoneInfo("Asia/Tashkent")).strftime("%d.%m.%Y"))
    state = RegressionSetupState(directory / "product-limit-state.json", deepcopy(baseline))
    try:
        api = state.user()
        with allure.step("1 - Faqat TMZ limiti guruhiga tegishli dona mahsulot yaratish"):
            payload = state.payload("product")
            payload.update(name=f"Order product limit-pw{state.code}-{data['run_id']}",
                           code=f"opl-{data['run_id']}")
            result = api.call(CONTRACTS["product"]["endpoint"], payload)
            data["product"] = {"id": positive_id(result["product_id"]),
                               "name": payload["name"], "code": payload["code"]}
            data["price"] = {"id": str(baseline["price_type_id_uzb"]),
                             "name": f"Price Type UZB-pw{state.code}", "unit_price": "7000"}
            persist(data, directory)
        with allure.step("2 - Yangi mahsulotga mavjud UZS narx turida 7000 so‘m belgilash"):
            api.call("anor/mr/product/product_set_price$save", {
                "product_id": data["product"]["id"], "prices": [{
                    "price_type_id": data["price"]["id"], "card_id": "-1", "price": "7000"}]})
        with allure.step("3 - Saqlangan mahsulot IDsi, kodi, nomi va 7000 so‘mlik narx"):
            view = api.model("anor/mr/product/inventory_view", product_id=data["product"]["id"])
            require_fields(view, name=payload["name"], code=payload["code"], state="A")
            model = api.model("anor/mr/product/product_set_price", product_id=data["product"]["id"])
            rows = [row for row in model["prices"] if str(row[0]) == data["price"]["id"]
                    and str(row[3]) == "-1"]
            if len(rows) != 1 or Decimal(str(rows[0][5])) != Decimal("7000"):
                raise APIError("TMZ limiti mahsulotining saqlangan narxi 7000 emas")
            data["status"] = "product_ready"
            resource_status(data, "product", "passed")
    except Exception:
        data["status"] = "failed"
        resource_status(data, "product", "failed")
        raise
    finally:
        persist(data, directory)
        allure.attach(json.dumps(data, ensure_ascii=False), "TMZ limiti tayyorlovi", allure.attachment_type.JSON)
        state.close()


def run_prepare_client(baseline, data, directory):
    """1. Own klient. 2. Saved identity. 3. Mavjud roomga additive attachment."""
    data["client"] = prepare_order_client(baseline, purpose="product-limit", kind="shared", directory=directory)
    data["status"] = "client_ready"
    persist(data, directory)


def run_prepare_stock(case, directory):
    """1. Test mahsulotidan 20 dona kirim. 2. Kirimni post qilish. 3. UI 20/0/20."""
    data = case.workflow
    if not resource_ready(data, "product") or data.get("client", {}).get("status") != "passed":
        raise APIError("Ombor tayyorlovidan oldin own mahsulot va klient kerak")
    resource_status(data, "stock", "process")
    state = RegressionSetupState(directory / "product-limit-stock-state.json", deepcopy(case.baseline))
    try:
        api = state.user()
        payload = state.payload("init_balance_uzb")
        number = "PL" + uuid4("product_limit_stock").hex[:8]
        payload["balance_number"] = number
        payload["items"][0].update(product_id=data["product"]["id"], quantity="20", card_code=number)
        data["stock_document"] = {"number": number, "product_id": data["product"]["id"],
                                  "quantity": "20", "state": "pending"}
        persist(data, directory)
        route = "anor/mkw/init_balance/init_inventory_balance_list"
        columns = ["balance_id", "balance_number", "warehouse_name", "currency_name", "posted"]
        with allure.step("1 - Own TMZ uchun asosiy omborga alohida 20 dona kirim yaratish"):
            api.call(CONTRACTS["init_balance_uzb"]["endpoint"], payload)
            row = api.one(route + ":table", columns, filters=["balance_number", "=", number])
            require_fields(row, posted=draft_or_reused_posted(row), warehouse_name="Основной склад", currency_name="Узбекский сум")
            identity = positive_id(row["balance_id"])
            data["stock_document"].update(id=identity, state="draft")
            persist(data, directory)
        with allure.step("2 - Aynan yangi kirimni omborga o‘tkazish"):
            api.call(route + ":post", {"balance_id": identity})
            row = api.one(route + ":table", columns, filters=["balance_id", "=", identity])
            require_fields(row, posted="Y", balance_number=number, warehouse_name="Основной склад", currency_name="Узбекский сум")
            data["stock_document"]["state"] = "posted"
            persist(data, directory)
        with allure.step("3 - UI’da test mahsuloti: mavjud 20, rezerv 0, erkin 20"):
            stock = read_stock(case, "Основной склад", product_id=data["product"]["id"])
            case.check("TMZ limiti guruhi boshlang‘ich ombor qoldig‘i",
                       {"physical": Decimal(20), "booked": Decimal(0), "available": Decimal(20)}, stock)
            data["stock_before"] = {key: str(value) for key, value in stock.items()}
            data["status"] = "stock_ready"
            resource_status(data, "stock", "passed")
    except Exception:
        data["status"] = "failed"
        resource_status(data, "stock", "failed")
        raise
    finally:
        persist(data, directory)
        case.checkpoint()
        state.close()


def run_prepare_limit(case, directory):
    """1. Xona+kunlik limit10. 2. Own SKU. 3. UI Save va qayta ochish."""
    data, page, base = case.workflow, case.page, AutoBasePage(case.page)
    if not resource_ready(data, "product"):
        raise APIError("Avval TMZ limiti mahsuloti tayyorlanishi kerak")
    resource_status(data, "limit", "process")
    name = f"Order daily limit10-pw{case.code}-{data['run_id']}"
    route = "anor/mcg/order_product_limit/order_product_limit"
    state = RegressionSetupState(directory / "limit-state.json", deepcopy(case.baseline))
    try:
        with allure.step("1 - TMZ limitlari ro‘yxatini ochish"):
            base.open_route(route + "_list", heading="Лимитирование ТМЦ")
        from tests.regression.helpers.retry.reconcile import is_retry, ui_row, allow_absent_ui_write
        existing = ui_row(page, route + "_list:table", ["order_product_limit_id", "name"], "name", name) if is_retry() else None
        if not existing:
            allow_absent_ui_write("anor/mcg/order_product_limit/order_product_limit+add$save", identity={"name": name})
            with allure.step("2 - Alohida kunlik limit yaratish formasini ochish"):
                base.click(name="Создать", exact=True)
                base.expect_page(heading="Лимитирование ТМЦ (создание)", url="order_product_limit")
            with allure.step("3 - Aynan test xonasi, bugungi sana va own mahsulot"):
                base.input(label="Название", value=name)
                base.radio(label="по рабочим зонам", click=True)
                base.multiselect(label="Рабочие зоны", value=case.room, clear=True)
                base.ui_select(label="Тип ограничения", expect_value="Ежедневный")
                base.input(label="Дата начала", value=data["date"], press_tab=True)
                base.input(label="Дата окончания", value=data["date"], press_tab=True)
                base.b_input(placeholder="Подбор", value=case.product, exact=True)
            with allure.step("4 - Mahsulotning xona bo‘yicha miqdor modalini ochish"):
                base.click(name="Количество", exact=True)
                dialog = page.get_by_role("dialog")
                expect(dialog.get_by_role("heading", name=case.product, exact=True)).to_be_visible()
            with allure.step("5 - Yagona test xonasiga 10 dona belgilash"):
                expect(dialog.get_by_text(case.room, exact=True)).to_be_visible()
                expect(dialog.get_by_role("textbox")).to_have_count(1)
                base.input(locator=dialog.get_by_role("textbox"), value="10", press_tab=True)
                base.click(name="Закрыть", exact=True, root=dialog, index=1)
                expect(dialog).to_be_hidden()
            with allure.step("6 - Limitni saqlash va IDni qayd etish"):
                base.click(name="Сохранить", exact=True)
                base.expect_page(heading="Лимитирование ТМЦ", url="order_product_limit_list")
        with allure.step("Saved limit IDsi — yangi yoki qayta topilgan yozuv"):
            api = state.user()
            row = api.one(route + "_list:table", ["order_product_limit_id", "name"], filters=["name", "=", name])
            identity = positive_id(row["order_product_limit_id"])
            data["limit"] = {"id": identity, "name": name, "quantity": "10", "room_id": str(case.baseline["room_id"]), "date": data["date"]}
            persist(data, directory)
        verify_saved_limit(case)
        data["status"] = "passed"
        resource_status(data, "limit", "passed")
    except Exception as error:
        data.update(status="failed", error_type=type(error).__name__)
        resource_status(data, "limit", "failed")
        raise
    finally:
        persist(data, directory)
        case.checkpoint()
        state.close()


def verify_saved_limit(case):
    """Read-only saved limit oracle, used by setup and resumed-run preflight."""
    data, page, base = case.workflow, case.page, AutoBasePage(case.page)
    route = "anor/mcg/order_product_limit/order_product_limit"
    identity, name = data["limit"]["id"], data["limit"]["name"]
    with allure.step("7 - Aynan saved limitni qayta ochish"):
        base.open_route(route + "_list", heading="Лимитирование ТМЦ")
        base.grid_setting(menu_name="Настройка таблицы", field_name="Название", search_name="Название")
        base.grid_controller(search=name)
        row = base.grid(name)
        expect(row.get_by_text(name, exact=True)).to_be_visible()
        base.grid(name, click=True)
        # A2 consumes the query into form state and encodes '+' in its URL.
        # Verify the selected entity from the actual UI model response instead.
        with page.expect_response(lambda response: response.status == 200 and
                unquote(urlsplit(response.url).path).endswith("/" + route + "+edit:model")) as opened:
            base.click(name="Изменить", exact=True)
        model = opened.value.json()
        if not isinstance(model, list) or len(model) < 3 or str(model[2].get("order_product_limit_id")) != str(identity):
            raise AssertionError("Ochilgan limit IDsi saqlangan limitga mos emas")
        base.expect_page(heading="Лимитирование ТМЦ (изменение)",
                         url=re.compile(r"/order_product_limit(?:%2[Bb]|\+)edit(?:\?.*)?$"))
    with allure.step("8 - Saved nom, xona, sana, mahsulot va 10 dona"):
        base.input(label="Название", expect_value=name)
        base.multiselect(label="Рабочие зоны", expect_value=case.room)
        base.ui_select(label="Тип ограничения", expect_value="Ежедневный")
        base.input(label="Дата начала", expect_value=data["date"])
        base.input(label="Дата окончания", expect_value=data["date"])
        base.b_input(placeholder="Подбор", expect_value=case.product)
        base.click(name="Количество", exact=True)
        dialog = page.get_by_role("dialog")
        expect(dialog.get_by_role("heading", name=case.product, exact=True)).to_be_visible()
        expect(dialog.get_by_text(case.room, exact=True)).to_be_visible()
        expect(dialog.get_by_role("textbox")).to_have_count(1)
        base.input(locator=dialog.get_by_role("textbox"), expect_value="10")
        base.click(name="Закрыть", exact=True, root=dialog, index=1)
