"""Ikki ombor uchun own klient, ombor va alohida qoldiq tayyorlovlari.

Room attachment API21 va kirim API23 kontraktlaridan foydalaniladi.
Biznes order yaratilmaydi, mavjud fixturelar o'chirilmaydi.
"""
from tests.regression.retry.checkpoints import draft_or_reused_posted
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
from tests.regression.retry.state import stable_uuid as uuid4
from tests.shared.navigation import open_form_from_list
from utils.base_pages.auto_base_page import AutoBasePage
from playwright.sync_api import expect

import allure

from tests.api.client import APIError, positive_id, require_fields
from tests.regression.test_orders.auth_recovery import RegressionSetupState
from tests.regression.test_orders.flows.stock import read_stock
from tests.regression.test_orders.preparations.clients import prepare_order_client


def run_prepare_two_warehouse_client(baseline, data, directory):
    """1. Own klient yaratish. 2. Saved ID va additive xona membershipini tekshirish."""
    data["client"] = prepare_order_client(
        baseline, purpose="two-warehouses", kind="reserve", directory=directory,
    )


def _persist(directory, metadata):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "two-warehouses-setup.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_prepare_two_warehouses(case, directory):
    """1. UI yangi Minor ombor. 2. Xonani tanlash. 3. Saved ID va additive membership."""
    baseline, data = case.baseline, case.workflow
    base = AutoBasePage(case.page)
    suffix = uuid4("second_warehouse").hex[:10]
    name = f"Order second warehouse-pw{case.code}-{suffix}"
    code = f"ow-{suffix}"
    metadata = {"warehouse_status": "process", "status": "prepared", "documents": [],
                "warehouses": [{"id": str(baseline["warehouse_id"]), "name": "Основной склад"}],
                "retention": "retained"}
    data["two_warehouses"] = metadata
    state = RegressionSetupState(directory / "warehouse-state.json", deepcopy(baseline))
    try:
        api = state.user()
        route = "anor/mrf/room_attachment:table_warehouse"
        def attached():
            return {str(r["warehouse_id"]) for r in api.table(route, ["warehouse_id"],
                    data={"room_id": baseline["room_id"], "attached": "Y"})}
        before = attached()
        metadata["room_warehouses_before"] = sorted(before)
        with allure.step("1 - Omborlar ro‘yxatini ochish"):
            base.navigate_to(tab="Склад", name="Склады")
            base.expect_page(heading="Склады", url="warehouse_list")
        from tests.regression.retry.reconcile import is_retry, ui_row, allow_absent_ui_write
        existing = ui_row(case.page, "anor/mkw/warehouse_list:table", ["warehouse_id", "name"], "name", name) if is_retry() else None
        if not existing:
            allow_absent_ui_write("anor/mkw/warehouse+add$save", identity={"name": name})
            with allure.step("2 - Alohida ikkinchi ombor yaratish formasini ochish"):
                open_form_from_list(base.page, heading="Склад (создание)", url="warehouse")
            with allure.step("3 - Minor omborni setup xonasiga biriktirib saqlash"):
                base.input(label="Название", value=name)
                base.input(label="Код", value=code)
                base.b_input(label="Тип склада", value="Minor", exact=True)
                base.multiselect(label="Рабочие зоны", value=case.room)
                base.click(name="Сохранить", exact=True)
                base.expect_page(heading="Склады", url="warehouse_list")
        with allure.step("4 - Saved ombor IDsi, faol holati va xonadagi membershipni tekshirish"):
            saved = api.one("anor/mkw/warehouse_list:table", ["warehouse_id", "name", "state"],
                            filters=["name", "=", name])
            identity = positive_id(saved["warehouse_id"])
            metadata["warehouses"].append({"id": identity, "name": name, "code": code, "created_in_run": True})
            _persist(directory, metadata)
            require_fields(api.model("anor/mkw/warehouse_view", warehouse_id=identity), name=name, state="A")
            after = attached()
            case.check("Oldingi ombor bog‘lanishlari va bitta yangi ombor", sorted(before | {identity}), sorted(after))
            metadata.update(warehouse_status="passed", room_warehouses_after=sorted(after))
    except Exception as error:
        metadata.update(warehouse_status="failed", error_type=type(error).__name__)
        raise
    finally:
        _persist(directory, metadata)
        case.checkpoint()
        state.close()


def run_prepare_two_warehouse_stock(case, directory):
    """1. Asosiy omborning fresh qoldig'ini UI orqali o'qish.
    2. Main uchun kam qismini 5gacha; yangi own omborga 5 dona alohida kirim.
    3. Har kirimning IDsi, ombori, valyutasi va posted holatini qayta o'qish.
    4. UI'da Mainning fizik/available deltasi va o'zgarmagan rezervni tekshirish.
    5. Yangi own omborning 5 fizik, 0 rezerv, 5 erkin qoldig'ini tasdiqlash.

    Yangi omborning kirimdan oldingi 0 qoldig'i UI'dan o'qilgan deb ko'rsatilmaydi.
    U shu guruh tayyorlovida yaratilgan; biznes baseline kirimdan keyin olinadi.
    """
    metadata = case.workflow.get("two_warehouses", {})
    if metadata.get("warehouse_status") != "passed" or len(metadata.get("warehouses", [])) != 2:
        raise APIError("Own ikkinchi ombor va uning bog'lanishlari tayyorlanmagan")
    if metadata.get("documents"):
        raise APIError("Stock tayyorlovini leaf sifatida qayta ishlatish mumkin emas; to'liq guruh kerak")
    directory = Path(directory)
    state = RegressionSetupState(directory / "stock-state.json", deepcopy(case.baseline))
    metadata.update(status="process", documents=[], stock_preparation=[])

    def persist():
        case.checkpoint()
        _persist(directory, metadata)

    persist()
    try:
        for index, warehouse in enumerate(metadata["warehouses"]):
            minimum = Decimal("5")
            with allure.step(f'1 - {warehouse["name"]}: kirim preconditionini aniqlash'):
                before = read_stock(case, warehouse["name"]) if index == 0 else None
                if index == 1 and warehouse.get("created_in_run") is not True:
                    raise APIError("5 dona fixed kirim faqat shu run yaratgan own ikkinchi omborga ruxsat")
                quantity = max(Decimal("0"), minimum - before["available"]) if before else minimum
                entry = {"warehouse_id": warehouse["id"], "warehouse": warehouse["name"],
                         "minimum_available": str(minimum), "added": str(quantity),
                         "before": {key: str(value) for key, value in before.items()} if before else None}
                metadata["stock_preparation"].append(entry)
                persist()
            if quantity:
                api = state.user()
                payload = state.payload("init_balance_uzb")
                number = "TW" + uuid4(f"stock:{warehouse['id']}").hex[:8]
                payload.update(balance_number=number, warehouse_id=warehouse["id"])
                payload["items"][0].update(quantity=str(quantity), card_code=number)
                if str(payload["items"][0]["product_id"]) != str(case.baseline["product_id"]):
                    raise APIError("Ikki ombor kirim kontraktida mahsulot IDsi mos emas")
                document = {"number": number, "warehouse_id": warehouse["id"],
                            "product_id": str(case.baseline["product_id"]),
                            "quantity": str(quantity), "card_code": number, "state": "pending"}
                metadata["documents"].append(document)
                persist()
                route = "anor/mkw/init_balance/init_inventory_balance_list"
                columns = ["balance_id", "balance_number", "warehouse_name", "currency_name", "posted"]
                with allure.step(f'2 - {warehouse["name"]} uchun {quantity} donali own kirim'):
                    state.send(api, "init_balance_uzb", **payload)
                    saved = api.one(route + ":table", columns, filters=["balance_number", "=", number])
                    document.update(id=positive_id(saved["balance_id"]), state="draft")
                    persist()
                    require_fields(saved, balance_number=number, posted=draft_or_reused_posted(saved),
                                   warehouse_name=warehouse["name"], currency_name="Узбекский сум")
                with allure.step("3 - Aynan own kirimni o'tkazish va saved posted holatini tekshirish"):
                    api.call(route + ":post", {"balance_id": document["id"]})
                    saved = api.one(route + ":table", columns, filters=["balance_id", "=", document["id"]])
                    require_fields(saved, balance_number=number, posted="Y",
                                   warehouse_name=warehouse["name"], currency_name="Узбекский сум")
                    document["state"] = "posted"
                    persist()
            with allure.step(f'4 - {warehouse["name"]}: UI orqali real qoldiqni tasdiqlash'):
                after = read_stock(case, warehouse["name"]) if quantity else before
                expected = ({**before, "physical": before["physical"] + quantity,
                             "available": before["available"] + quantity} if before else
                            {"physical": minimum, "booked": Decimal("0"), "available": minimum})
                entry["after"] = {key: str(value) for key, value in after.items()}
                case.check(f'{warehouse["name"]}: tayyorlovdan keyingi fizik qoldiq, rezerv va available', expected, after)
                case.check(f'{warehouse["name"]}: kamida 5 dona erkin qoldiq', True, after["available"] >= minimum)
                persist()
        metadata["status"] = "passed"
    except Exception as error:
        metadata.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        try:
            persist()
            allure.attach(json.dumps(metadata, ensure_ascii=False), "Ikki ombor qoldiq tayyorlovi", allure.attachment_type.JSON)
        finally:
            state.close()
