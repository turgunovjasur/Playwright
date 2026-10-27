"""Order Excel importining uch testcase'da takrorlanadigan mapping amallari."""

import allure
from playwright.sync_api import expect

from utils.base_pages.auto_base_page import AutoBasePage


def read_order_import_settings(page):
    """Joriy user mappingini o'qib Settingsni ochiq qoldirish.

    Fayl mazmuni, kutilgan qatorlar va biznes tekshiruvlar leafda qoladi.
    Snapshot mapping o'zgarishidan oldin testcase cleanup registriga yoziladi.
    """
    base = AutoBasePage(page)
    with allure.step("Import — joriy user mappingini o'qish"):
        base.click(name="Настройки", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
        expect(page.locator('input[ng-model="d.starting_row"]:visible')).to_be_visible()
        settings = {"starting_row": base.input(ng_model="d.starting_row", return_value=True), "ending_row": base.input(ng_model="d.ending_row", return_value=True)}
        settings["identify"] = page.locator('input[ng-model="d.identify_product_by"]:checked').input_value()
        columns = page.locator('input[ng-model="item.column_number"]:visible')
        expect(columns).to_have_count(8)
        settings["columns"] = [base.input(ng_model="item.column_number", index=index, return_value=True) for index in range(8)]
        return settings


def apply_order_import(page, *, ending_row=""):
    """Ochiq Settingsda uch ustunli PI/quantity/Y workbook mappingini saqlash."""
    base = AutoBasePage(page)
    with allure.step("Import — ID, quantity va balance mappingini saqlash"):
        base.input(ng_model="d.starting_row", value="1")
        base.input(ng_model="d.ending_row", value=ending_row)
        base.radio(label="ИД продукции", click=True)
        for index, value in enumerate(("1", "3", "", "", "", "2", "", "")):
            base.input(ng_model="item.column_number", index=index, value=value, press_tab=True)
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
        expect(page.get_by_role("button", name="Загрузить файл", exact=True)).to_be_visible()


def restore_order_import(page, settings):
    """Import sahifasidan userning avvalgi barcha mapping maydonlarini tiklash."""
    base = AutoBasePage(page)
    with allure.step("Import — userning original sozlamalariga qaytish"):
        base.click(name="Настройки", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
        base.input(ng_model="d.starting_row", value=settings["starting_row"])
        base.input(ng_model="d.ending_row", value=settings["ending_row"])
        identify_labels = {"PC": "Код продукции", "PPC": "Код на продукцию", "PI": "ИД продукции"}
        base.radio(label=identify_labels[settings["identify"]], click=True)
        for index, value in enumerate(settings["columns"]):
            base.input(ng_model="item.column_number", index=index, value=value, press_tab=True)
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
        expect(page.get_by_role("button", name="Загрузить файл", exact=True)).to_be_visible()
    restored = read_order_import_settings(page)
    if restored != settings:
        raise AssertionError(f"Import mapping tiklanmadi: expected={settings}, actual={restored}")
    with allure.step("Import — tiklangan mappingni qayta o'qib previewga qaytish"):
        base.click(name="Назад", exact=True)
        base.expect_page(heading="Заказ (импорт ТМЦ)", url="order_import")
        expect(page.get_by_role("button", name="Загрузить файл", exact=True)).to_be_visible()
