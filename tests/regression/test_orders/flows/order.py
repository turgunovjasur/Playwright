"""Uch A2 biznes testcase uchun order list/create/save/reopen gatewaylari."""
import re
from urllib.parse import unquote, urlsplit
import allure
from playwright.sync_api import expect
from tests.shared.navigation import open_form_from_list
from utils.base_pages.auto_base_page import AutoBasePage
from utils.base_pages.angular_base_page import _lookup_query_finished


def promotion_card(page, name):
    """02.11.2026 live A2 DOM: aksiya nomi va switch bitta article ichida."""
    card = page.locator("article").filter(has=page.get_by_text(name, exact=True))
    expect(card).to_have_count(1)
    expect(card).to_be_visible()
    return card


def open_new_order(page):
    base = AutoBasePage(page)
    with allure.step("Order ro'yxatini ochish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="/a2/trade/tdeal/order/order_list")
    with allure.step("Oddiy order yaratish formasini ochish"):
        open_form_from_list(page, heading="Заказ (создание)",
                            url=re.compile(r"/a2/.*/order(?:%2[Bb]|\+)add"))


def existing_order(case):
    """Resolve the same saved order before Add or stock/offer selection on retry.

    This is identity recovery only. Each consumer still checks its own amounts,
    goods, status and unfinished business assertions on the returned View.
    """
    from tests.regression.retry.reconcile import is_retry, ui_row, confirm_entity, allow_absent_ui_write
    from tests.regression.retry.state import ACTIVE
    if not is_retry():
        return None
    page, base = case.page, AutoBasePage(case.page)
    with allure.step("Retry: Add’dan oldin shu TTNli order mavjudligini tekshirish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        journal = ACTIVE.get()
        previous = journal.previous("entity:order:" + case.reference)
        pinned = getattr(journal.item.config, "_retry_plan", {}).get("saved_order")
        if pinned and (pinned["reference"] != case.reference or
                       (previous or {}).get("entity_id") != pinned["id"]):
            raise AssertionError("Davom ettirilayotgan order IDsi yoki TTN mos emas")
        if previous and previous.get("entity_id"):
            identity = previous["entity_id"]
        else:
            row = ui_row(page, "trade/tdeal/order/order_list:table",
                         ["deal_id", "delivery_number"], "delivery_number", case.reference)
            if not row:
                allow_absent_ui_write("anor/mdeal/order/order+add$save",
                                      identity={"delivery_number": case.reference},
                                      operation="order:" + case.reference)
                return None
            identity = str(row["deal_id"])
        base.open_route("trade/tdeal/order/order_view?deal_id=" + str(identity), heading="Заказ / Просмотр")
        base.form_view(label="ИД заказа", expect_value=str(identity))
        base.form_view(label="Номер ТТН", expect_value=case.reference)
        base.form_view(label="Клиент", expect_value=case.client)
        confirm_entity("order", case.reference, identity)
        return str(identity)


def saved_quantities(page, product, price_type, warehouses):
    """Read current saved quantities to distinguish pre-edit and post-edit states."""
    from decimal import Decimal
    base = AutoBasePage(page)
    grid = page.locator("smt-table:visible").last
    headers = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    if headers.count("Количество продажи") != 1:
        raise AssertionError("Saved order miqdor ustuni yagona emas")
    expect(grid.locator(".smt-data-row")).to_have_count(len(warehouses))
    values = []
    for warehouse in warehouses:
        row = grid.locator(".smt-data-row").filter(has=page.get_by_text(product, exact=True)).filter(
            has=page.get_by_text(price_type, exact=True)).filter(has=page.get_by_text(warehouse, exact=True))
        expect(row).to_have_count(1)
        values.append(Decimal(base.grid_cell(row, headers.index("Количество продажи"), return_value=True, remove_spaces=True).replace(",", ".")))
    return tuple(values)


def save_order_by_reference(page, reference):
    base = AutoBasePage(page)
    from tests.regression.retry.reconcile import is_retry, ui_row, allow_absent_ui_write, confirm_entity
    if is_retry():
        with allure.step("Retry: avvalgi TTN bilan saqlangan orderni serverdan qidirish"):
            row = ui_row(page, "trade/tdeal/order/order_list:table",
                         ["deal_id", "delivery_number"], "delivery_number", reference)
            if row:
                confirm_entity("order", reference, row["deal_id"])
                from tests.regression.retry.state import ACTIVE
                page.goto(ACTIVE.get().ui_root + "/a2/trade/tdeal/order/order_view?deal_id=" + str(row["deal_id"]))
                base.expect_page(heading="Заказ / Просмотр", url="order_view")
                base.form_view(label="Номер ТТН", expect_value=reference)
                base.form_view(label="ИД заказа", expect_value=str(row["deal_id"]))
                return str(row["deal_id"])
            allow_absent_ui_write("anor/mdeal/order/order+add$save", identity={"delivery_number": reference})
    with allure.step("Orderni saqlab ro'yxatga qaytish"):
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Заказы", url="order_list")
        saved = ui_row(page, "trade/tdeal/order/order_list:table", ["deal_id", "delivery_number"], "delivery_number", reference)
        if not saved:
            from tests.regression.retry.state import RetryBlocked
            raise RetryBlocked("Order Save’dan keyin exact TTN topilmadi; qayta Save yuborilmadi")
        confirm_entity("order", reference, saved["deal_id"])
    with allure.step("Unique TTN bo'yicha aynan yangi orderni topish"):
        column = base.grid_setting(menu_name="Настройка таблицы", field_name="Номер ТТН", search_name="Номер ТТН")
        def searched(response):
            return (response.status == 200
                    and unquote(urlsplit(response.url).path).endswith('/trade/tdeal/order/order_list:table')
                    and _lookup_query_finished(response.request, reference, "delivery_number"))

        # The previous dataset may already contain this TTN. Select only after
        # this exact search response and its rendered row have settled.
        with page.expect_response(searched) as search_response:
            base.grid_controller(search=reference)
        search_response.value.finished()
        base.wait_for_loader()
        expect(page.locator("smt-data-table:visible .smt-data-row")).to_have_count(1)
        row = base.grid(reference)
        expect(base.grid_cell(row, column)).to_have_text(reference)
        base.grid(reference, click=True)
    with allure.step("Saqlangan order viewini ochish"):
        base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        base.form_view(label="Номер ТТН", expect_value=reference)
        identity = base.form_view(label="ИД заказа", expect_value=str(saved["deal_id"]), return_value=True).strip()
        return identity


def save_edited_order(page, order_id, reference):
    """Viewdan ochilgan edit Save'dan keyin o'sha Viewga qaytadi.

    Create flow ro'yxatga qaytadi; bu yo'l esa saqlangan target ID va TTNni
    bevosita qaytgan viewdan tekshiradi. Kutilmagan route fallback qilinmaydi.
    """
    base = AutoBasePage(page)
    with allure.step("Tahrirlangan orderni saqlash va o‘sha order viewiga qaytish"):
        base.expect_page(heading="Заказ (изменение)", url=re.compile(r"order(?:%2[Bb]|\+)edit"))
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        base.form_view(label="Номер ТТН", expect_value=reference)
        return base.form_view(label="ИД заказа", expect_value=order_id, return_value=True).strip()


def reopen_order_goods(page):
    base = AutoBasePage(page)
    with allure.step("Saqlangan orderni tahrirga qayta ochish"):
        base.click(name="Редактировать", exact=True)
        base.expect_page(heading="Заказ (изменение)", url=re.compile(r"order(?:%2[Bb]|\+)edit"))
    with allure.step("Saqlangan mahsulotlar bosqichini ochish"):
        base.click(name="Далее", exact=True)
        base.text("Название", "Кол-во")


def select_order_product(page, product, price_type, *, warehouse="Основной склад", index=0):
    """Mahsulotni ombor va narx varianti bilan tanlash; pagination b_input ichida."""
    base = AutoBasePage(page)
    if index == 0:
        base.b_input(label="Название", value=product,
                     option_contains=(price_type, warehouse), exact=True)
    else:
        grid = page.locator("smt-table:visible").first
        base.b_input(placeholder="Выберите...", index=index, root=grid, value=product,
                     option_contains=(price_type, warehouse), exact=True)
    row = page.locator(".smt-data-row:visible").filter(
        has=page.get_by_text(price_type, exact=True)).filter(
        has=page.get_by_text(warehouse, exact=True))
    expect(row).to_have_count(1)
    base.text(price_type, warehouse, root=row)
    return row
