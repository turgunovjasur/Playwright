import allure

from utils.base_page import BasePage


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
    base = BasePage(page)

    with allure.step(f"1 - {price_label} TMC ro'yxatini ochish"):
        base.navigate_to(tab="Справочники", name="ТМЦ")
        base.expect_page(heading="ТМЦ")

    with allure.step(f"2 - {price_label} TMC yaratish formasini ochish va to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="ТМЦ (создание)")
        base.input(label="Код", value=product_code)
        base.input(label="Название", value=product_name)
        base.b_input(label="Ед. изм.", value="шт", search_text="")
        base.multiselect(label="Наборы ТМЦ", expect_value=sector_name)
        base.checkbox(label="Активный", expect_checked=True)
        base.checkbox(label="Товар", checked=True)

    with allure.step(f"3 - {price_label} TMCni saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name)

    with allure.step(f"4 - {price_label} TMC view formasini ochish va ID olish"):
        base.grid(product_code, product_name, click=True)
        base.click(name="Просмотреть")
        base.expect_page(heading="ТМЦ (просмотр)", url="inventory_view?product_id=")
        base.text(product_code, product_name)
        product_view_url = page.url

    with allure.step(f"5 - {price_label} TMC view formasini yopish"):
        base.click(name="Закрыть", exact=True)
        base.expect_page(heading="ТМЦ")

    with allure.step(f"6 - {price_label} TMC narx formasini ochish"):
        base.grid(product_code, product_name, click=True)
        base.click(name="Установить цены")
        base.expect_page(heading="ТМЦ (установка цен)")

    with allure.step(f"7 - {price_label} narxni saqlash va TMCni ro'yxatda tekshirish"):
        base.input(label=price_type_name, value=price)
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni(expected_text="Сохранить?")
        base.expect_page(heading="ТМЦ")
        base.grid_controller(search=product_code)
        base.grid(product_code, product_name)

    return product_view_url
