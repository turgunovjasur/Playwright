"""Ikki tanlangan buyurtmaning haqiqiy XML fayli. Abgular 1309–1312."""
from decimal import Decimal
from xml.etree import ElementTree

import allure

from tests.regression.test_orders.business_cases.pricing.test_catalog_price_history import run_create_price_draft
from utils.base_pages.auto_base_page import AutoBasePage


def run_xml_draft(case, catalog, *, key, price):
    """1. Umumiy TTN prefiksi. 2. Alohida qoralama. 3. Saqlangan qator va summa."""
    prefix = "X" + catalog["goods"]["code"].removeprefix("rg-").removesuffix("-a")
    case.reference = f"{prefix}-{price}"
    case.workflow["xml_prefix"] = prefix
    run_create_price_draft(case, key=key, price=price, payment_type="Перечисление")


def run_export(case, directory):
    """1. Ikki qatorni tanlash. 2. XML yuklash. 3. Har hujjat va qatorni solishtirish."""
    base = AutoBasePage(case.page)
    drafts = {case.workflow[key]["id"]: (case.workflow[key]["reference"], price)
              for key, price in (("original_draft", 1000), ("new_draft", 1500))}
    with allure.step("Buyurtmalar ro‘yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
    with allure.step("Guruh TTN prefiksini qidirib, ikkala qoralamani alohida tanlash"):
        base.grid_setting(menu_name="Настройка таблицы", field_name="Номер ТТН", search_name="Номер ТТН")
        base.grid_controller(search=case.workflow["xml_prefix"])
        for reference, _ in drafts.values():
            base.grid(reference, checkbox="row")
    with allure.step("Ikki tanlangan buyurtmaning XML faylini yuklab olish"):
        base.click(name="Накладные 2", exact=True)
        with case.page.expect_download() as pending:
            base.click(name="Экспортировать заказы (2)", role="menuitem", exact=True)
        path = directory / "two-orders.xml"
        pending.value.save_as(path)
        allure.attach.file(str(path), name="Tanlangan buyurtmalar", extension="xml")
    with allure.step("XMLdagi hujjatlar va mahsulot qatorlarini saqlangan buyurtmalarga solishtirish"):
        deals = ElementTree.parse(path).getroot().findall("Сделка")
        case.check("Faylda aynan tanlangan ikkita ID", sorted(drafts), sorted(d.findtext("СделкаИд") for d in deals))
        for deal in deals:
            oid = deal.findtext("СделкаИд")
            _, price = drafts[oid]
            case.check(f"{oid} · klient, nom va status",
                       [str(case.workflow["client"]["person_id"]), case.client, "D"],
                       [deal.findtext(key) for key in ("КонтрагентИд", "КонтрагентНазвание", "СостояниеЗаказа")])
            lines = deal.findall("Строки")
            case.check(f"{oid} · mahsulot qatorlari", 1, len(lines))
            line = lines[0]
            case.check(f"{oid} · mahsulot ID", str(case.baseline["product_id"]), line.findtext("НоменклатураИд"))
            case.check(f"{oid} · miqdor, narx, qator va hujjat summasi",
                       [2, price, 2 * price, 2 * price],
                       [Decimal(line.findtext(key)) for key in ("ПроданоКоличество", "Цена", "СуммаСоСкидкой")]
                       + [Decimal(deal.findtext("Оплата/Сумма"))])
