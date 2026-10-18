import re

import allure

from utils.base_pages.auto_base_page import AutoBasePage


def create_product_with_price(
    page,
    *,
    product_name,
    product_code,
    sector_name,
    price_type_name,
    price,
    price_label,
):
    """Bitta TMC yaratadi, view URLni qaytaradi va tegishli narxni belgilaydi."""
    base = AutoBasePage(page)

    with allure.step(f"1 - {price_label} TMC ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ", url="anor/mr/product/inventory_list")

    with allure.step(f"2 - {price_label} TMC yaratish formasini ochish va to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="ТМЦ (создание)", url=re.compile(r"anor/mr/product/inventory(?:\+|%2[bB])add(?:[?#]|$)"))
        base.input(label="Код", value=product_code)
        base.input(label="Название", value=product_name)
        base.b_input(label="Ед. изм.", value="шт", search_text="")
        base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)
        base.checkbox(label="Активный", expect_checked=True)
        base.checkbox(label="Товар", checked=True)

    with allure.step(f"3 - {price_label} TMCni saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ", url="anor/mr/product/inventory_list")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name, click=True)

    with allure.step(f"4 - {price_label} TMC view formasini ochish va ID olish"):
        base.click(name="Просмотреть")
        base.expect_page(heading="ТМЦ (просмотр)", url="inventory_view?product_id=")
        base.text(product_code, product_name, include_input_values=True)
        product_view_url = page.url

    with allure.step(f"5 - {price_label} TMC view formasini yopish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ", url="anor/mr/product/inventory_list")

    with allure.step(f"6 - {price_label} TMC narx formasini ochish"):
        base.grid(product_code, product_name, click=True)
        base.click(name="Установить цены")
        base.expect_page(heading="ТМЦ (установка цен)", url="anor/mr/product/product_set_price")

    with allure.step(f"7 - {price_label} narxni saqlash va TMCni ro'yxatda tekshirish"):
        price_table = page.get_by_text("Цена с НДС и акцизом", exact=True).filter(visible=True).locator(
            "xpath=ancestor::*[self::b-grid or self::b-pg-grid or self::table or self::smt-data-table or self::smt-table][1]"
        )
        price_row = base.grid(price_type_name, root=price_table)
        price_input = base.grid_cell(price_row, 4).locator("input:visible")
        base.input(locator=price_input, value=price, press_tab=True)
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni(expected_text="Сохранить?")
        base.expect_page(heading="ТМЦ", url="anor/mr/product/inventory_list")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name)

    return product_view_url
