"""A2 Order. Xuddi shu mahsulot qo‘lda yoki Excel’dan kiritilganda A5→B1 bonusi."""

from io import BytesIO
import re

import allure
from openpyxl import Workbook
from playwright.sync_api import expect

from tests.regression.helpers.retry.reconcile import allow_absent_ui_write, is_retry
from tests.regression.test_orders.business_cases.discounts.test_manual_discount import _header_amount, _line_amount
from tests.regression.test_orders.helpers.flows.order import (
    existing_order, open_new_order, open_order_summary, promotion_card, reopen_order_goods,
    save_order_by_reference, select_order_product,
)
from utils.base_pages.auto_base_page import AutoBasePage


# Ordered headings in the Order goods importer's mapping table.
COLUMNS = (
    "Код", "Балансовый", "Серийный номер", "Номер карточки", "Срок годности",
    "Кол-во", "Тип скидки/наценки", "Процент скидки/наценки",
)
IDENTIFIERS = {"PC": "Код продукции", "PPC": "Код на продукцию", "PI": "ИД продукции"}
WORKBOOK_MAPPING = {
    "starting": "1", "ending": "", "identify": "PC",
    "columns": {label: str(number) for number, label in enumerate(COLUMNS, 1)},
}


def _open_goods(case):
    base = AutoBasePage(case.page)
    open_new_order(case.page)
    with allure.step("1 - Guruh klientini tanlab ТМЦ bosqichini ochish"):
        base.b_input(label="Клиент", value=case.client, clear=True)
        base.click(name="Далее", exact=True)
        base.text("Название", "Кол-во")


def _eligible_bonus(case):
    base = AutoBasePage(case.page)
    base.tab(name=re.compile(r"^Акции"))
    card = promotion_card(case.page, case.promotions["bonus"]["name"])
    base.grid(case.bonus_product, "1", root=card)
    switch = card.get_by_role("switch")
    base.checkbox(locator=switch, expect_checked=False)
    return switch


def _check_saved_draft(case, order_id, reference):
    base = AutoBasePage(case.page)
    for label, expected in (
        ("ИД заказа", order_id), ("Номер ТТН", reference), ("Статус", "Черновик"),
        ("Клиент", case.client), ("Тип оплаты", "Перечисление"),
    ):
        base.form_view(label=label, expect_value=expected)
    base.form_view(label="Сумма заказа", expect_value="4300", remove_spaces=True)
    base.form_view(label="Сумма скидки/наценки на заказ", expect_value="-200", remove_spaces=True)
    grid = case.page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.product, case.price_type, "Основной склад", root=grid)
    headers = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, expected in (("Количество заказа", "5"), ("Цена", "1000"),
                            ("Сумма скидки/наценки", "-500"), ("Итого", "4500")):
        case.check(f"Saqlangan mahsulot: {label}", expected,
                   base.grid_cell(row, headers.index(label), return_value=True, remove_spaces=True))
    expect(case.page.get_by_role("tab", name="Акция", exact=True)).to_have_count(0)


def run_direct_entry_control(case):
    """Qo‘lda kiritilgan 5 donalik, 4 300 so‘mlik o‘tkazma qoralamasini saqlash."""
    base = AutoBasePage(case.page)
    order_id = existing_order(case)
    if not order_id:
        _open_goods(case)
        with allure.step("Qo‘lda kiritilgan 5 × 1000 – 5 × 100 = 4500 so‘mlik mahsulot"):
            row = select_order_product(case.page, case.product, case.price_type)
            base.input(label="Кол-во", value="5", press_tab=True)
            _line_amount(case, row, -100)
            open_order_summary(case.page, expected_total="4500")
        with allure.step("O‘tkazma, yana 200 so‘m chegirma va noyob TTN bilan qoralamani saqlash"):
            base.b_input(label="Тип оплаты", value="Перечисление", clear=True)
            base.ui_select(label="Статус", value="Черновик")
            _header_amount(case, -200)
            base.input(label="ИТОГО", expect_value="4300")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            order_id = save_order_by_reference(case.page, case.reference)
    case.remember_order(order_id)
    case.workflow["import_draft"] = {"id": order_id, "reference": case.reference}
    case.checkpoint()
    _check_saved_draft(case, order_id, case.reference)


def _column_field(page, modal, label):
    row = modal.locator("smt-table-row").filter(has=page.get_by_text(label, exact=True))
    return row.locator('[data-smt-col-key="column_number"] input')


def _read_mapping(page, base, modal):
    selected = modal.locator('input[type="radio"]:checked')
    expect(selected).to_have_count(1)
    identify = selected.input_value()
    if identify not in IDENTIFIERS:
        raise ValueError(f"Noma’lum import identifikatori: {identify}")
    labels = modal.locator('smt-table-row [data-smt-col-key="name"]')
    expect(labels).to_have_count(len(COLUMNS))
    return {
        "starting": base.input(label="Начальная строка", root=modal, return_value=True),
        "ending": base.input(label="Конечная строка", root=modal, return_value=True),
        "identify": identify,
        "columns": {label: _column_field(page, modal, label).input_value() for label in COLUMNS},
    }


def _write_mapping(page, base, modal, mapping, order_id):
    base.input(label="Начальная строка", value=mapping["starting"], root=modal, press_tab=True)
    base.input(label="Конечная строка", value=mapping["ending"], root=modal, press_tab=True)
    base.radio(IDENTIFIERS[mapping["identify"]], click=True, root=modal)
    for label, value in mapping["columns"].items():
        base.input(locator=_column_field(page, modal, label), value=value, press_tab=True)
    if is_retry():
        allow_absent_ui_write("anor/mdeal/order/order_import$save_setting",
                              identity={"deal_id": order_id, "identify_product_by": mapping["identify"],
                                        "starting_row": mapping["starting"]})
    base.click(name="Сохранить", exact=True, root=modal)
    expect(modal.get_by_role("button", name="Загрузить файл", exact=True)).to_be_visible()


def _workbook(product_code):
    workbook = Workbook()
    try:
        workbook.active.append([product_code, "N", None, None, None, 3])
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()
    finally:
        workbook.close()


def run_promotion_after_excel_import(case, *, product_code):
    """1. Saqlangan qoralamani Edit’da oching, nazorat bonusini tekshirib mahsulotni olib tashlang.
    2. Guruh tovari kodi, N va 3 yozilgan faylni yuklang, qator va narxni tekshiring.
    3. Mappingni tiklab, mahsulotni orderga o‘tkazing.
    4. 5 × 1000 − 5 × 100 − 200 = 4300 va aynan bir dona bonusni tekshiring.
    """
    page = case.page
    base = AutoBasePage(page)
    draft = case.workflow["import_draft"]
    view_route = "trade/tdeal/order/order_view?deal_id=" + draft["id"]
    with allure.step("1 - Saqlangan qoralamada bonus borligini tekshirib yagona mahsulot qatorini o‘chirish"):
        base.open_route(view_route, heading="Заказ / Просмотр")
        _check_saved_draft(case, draft["id"], draft["reference"])
        reopen_order_goods(page)
        _eligible_bonus(case)
        base.tab(name="Товар")
        row = page.locator(".smt-data-row:visible").filter(has_text=case.price_type).filter(has_text="Основной склад")
        expect(row).to_have_count(1)
        base.b_input(label="Название", expect_value=case.product)
        base.click(name="Удалить", exact=True, root=row)
        expect(row).to_have_count(0)
    with allure.step("2 - Заказ (импорт ТМЦ) oynasida ombor va narx turini tanlash"):
        base.click(name="Импорт", exact=True)
        heading = page.get_by_role("heading", name="Заказ (импорт ТМЦ)", exact=True)
        expect(heading).to_be_visible()
        modal = page.locator("main:visible").filter(has=page.get_by_role("tab", name="Настройки", exact=True))
        expect(modal).to_have_count(1)
        base.b_input(label="Склад", value="Основной склад", clear=True, root=modal)
        base.b_input(label="Тип цены", value=case.price_type, clear=True, root=modal)
    with allure.step("3 - Joriy foydalanuvchining import sozlamalarini qayd etish"):
        base.tab(name="Настройки", root=modal)
        current = _read_mapping(page, base, modal)
        original = case.workflow.setdefault("original_import_mapping", current)
        case.checkpoint()
        if current not in (original, WORKBOOK_MAPPING):
            raise AssertionError("Import sozlamalari boshqa sessiyada o‘zgargan")
    preview = modal.locator(".smt-data-row").filter(has_text=case.product).filter(has_text=case.price_type)
    try:
        if current != WORKBOOK_MAPPING:
            _write_mapping(page, base, modal, WORKBOOK_MAPPING, draft["id"])
        else:
            base.click(name="Назад", exact=True, root=modal)
        with allure.step("4 - Kod / N / 3 Excel qatorini parse qilib ombor, miqdor va narxni tekshirish"):
            content = _workbook(product_code)
            allure.attach(content, "A5 aksiya uchun 3 dona mahsulot", extension="xlsx")
            modal.locator('input[type="file"]').set_input_files({
                "name": "order-promotion.xlsx",
                "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "buffer": content,
            })
            base.click(name="Загрузить файл", exact=True, root=modal)
            base.confirm_biruni("Загрузить выбранный файл?")
            expect(preview).to_have_count(1)
            expect(preview).to_contain_text("Основной склад")
            expect(preview).to_contain_text("Забалансовый")
            expect(preview.locator("input:visible").first).to_have_value("3")
            expect(preview.get_by_text(re.compile(r"^\s*1\s*000\s*$"))).to_be_visible()
    except Exception:
        # A parse failure can leave its error or confirmation over the Settings tab.
        dialogs = page.get_by_role("dialog").filter(visible=True)
        if dialogs.filter(has_text=re.compile(r"ошибка|error|URL\s*:|Uri\s*:", re.I)).count():
            base.close_biruni_alert()
        elif dialogs.filter(has_text="Загрузить выбранный файл?").count():
            base.confirm_biruni("Загрузить выбранный файл?", button_name="нет")
        raise
    finally:
        if original != WORKBOOK_MAPPING:
            with allure.step("5 - Tahlil natijasidan qat’i nazar original import sozlamalarini tiklash"):
                base.tab(name="Настройки", root=modal)
                _write_mapping(page, base, modal, original, draft["id"])
                base.tab(name="Настройки", root=modal)
                case.check("Tiklangan Excel import sozlamalari", original, _read_mapping(page, base, modal))
                base.click(name="Назад", exact=True, root=modal)
    with allure.step("6 - Tasdiqlangan mahsulotni importdan orderga o‘tkazish"):
        expect(preview).to_have_count(1)
        base.click(name="Добавить выбранные поля", exact=True, root=modal)
        expect(heading).to_be_hidden()
        expect(row).to_have_count(1)
        base.b_input(label="Название", expect_value=case.product)
        base.input(label="Кол-во", expect_value="3")
    with allure.step("7 - 3 donani 5 ga o‘zgartirish va har donaga −100 chegirma kiritish"):
        base.input(label="Кол-во", value="5", press_tab=True)
        _line_amount(case, row, -100)
        expect(row.get_by_text(re.compile(r"^\s*4\s*500\s*$"))).to_be_visible()
        open_order_summary(page)
    with allure.step("8 - O‘tkazma va avvalgi −200 so‘mlik order chegirmasidan so‘ng jami 4 300"):
        base.b_input(label="Тип оплаты", value="Перечисление", clear=True)
        base.ui_select(label="Статус", value="Черновик")
        toggle = page.get_by_role("button", name="Скидка/наценка", exact=True)
        if toggle.locator('svg-icon[aria-label="percent-01-icon"]').is_visible():
            _header_amount(case, -200)
        else:
            expect(toggle.locator('svg-icon[aria-label="bank-note-01-icon"]')).to_be_visible()
            base.input(label="Скидка/наценка к заказу", value="-200", press_tab=True)
            base.input(label="Скидка/наценка к заказу", expect_value="-200")
        base.input(label="ИТОГО", expect_value="4300")
    with allure.step("9 - Tahrir saqlanmasidan oldin mos aksiyadan 1 dona bepul bonusni tanlash"):
        base.click(name="Назад", exact=True)
        base.checkbox(locator=_eligible_bonus(case), checked=True)
    with allure.step("10 - Tahrirni saqlamasdan chiqib dastlabki qoralama va TTNni qayta tekshirish"):
        base.open_route(view_route, heading="Заказ / Просмотр")
        _check_saved_draft(case, draft["id"], draft["reference"])
