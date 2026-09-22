"""ТМЦ create/edit formasi uchun umumiy to'ldirish; biznes expectedlar leafda."""

from utils.base_pages.auto_base_page import AutoBasePage


def fill_product_card(page, product):
    """Ochiq ТМЦ kartasiga berilgan qiymatlarni yozadi; saqlashni caller bajaradi."""
    base = AutoBasePage(page)
    base.input(label="Название", value=product["name"])
    base.input(label="Альтернативное название", value=product["short_name"])
    base.input(label="Код", value=product["code"])
    base.input(label="Артикул код", value=product["article_code"])
    base.input(label="Порядковый номер", value=product["order_no"], press_tab=True)
    base.b_input(label="Ед. изм.", value=product["measure"], search_text="")
    base.multiselect(label="Наборы ТМЦ", expect_value=product["sector"])
    base.checkbox(label="Активный", checked=True)
    base.checkbox(label="Товар", checked=True)
    base.checkbox(label="Продукция", checked=product["production"])
    base.checkbox(label="Сырье", checked=product["material"])
    if product["box"]:
        base.b_input(label="Тип кейса (1 уровень)", value=product["box"], search_text="")
        base.input(label="Кол-во в кейсе (1 уровень)", value=product["box_qty"], press_tab=True)
    if product["pallet"]:
        base.b_input(label="Тип кейса (2 уровень)", value=product["pallet"], search_text="")
        base.input(label="Кол-во в кейсе (2 уровень)", value=product["pallet_qty"], press_tab=True)
    # Legacy tab anchorida href/role yo'q; semantic click helperi mos emas.
    page.locator("#kt_content a").filter(has=page.get_by_text("Вес", exact=True)).click()
    base.input(label="Вес нетто (кг)", value=product["weight_netto"], press_tab=True)
    base.input(label="Вес брутто (кг)", value=product["weight_brutto"], press_tab=True)
    base.input(label="Литр/Дециметр куб.", value=product["volume"], press_tab=True)
