"""Uch A2 biznes testcase uchun order list/create/save/reopen gatewaylari."""
from contextlib import contextmanager
import re
from urllib.parse import unquote, urlsplit
import allure
from playwright.sync_api import expect
from tests.shared.navigation import open_form_from_list
from tests.shared.list_search import find_list_record
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
    """Resolve the same saved order before Add or stock/offer selection.

    This is identity recovery only. Each consumer still checks its own amounts,
    goods, status and unfinished business assertions on the returned View.
    """
    from tests.regression.helpers.retry.reconcile import is_retry, ui_row, confirm_entity
    from tests.regression.helpers.retry.state import ACTIVE
    page, base = case.page, AutoBasePage(case.page)
    with allure.step("Yaratishdan oldin TTN bo‘yicha orderni qidirish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_setting(menu_name="Настройка таблицы", field_name="Номер ТТН", search_name="Номер ТТН")
        row = find_list_record(base, "order_list", "delivery_number", case.reference)
        identity = str(row["deal_id"]) if row else None
        if is_retry():
            journal = ACTIVE.get()
            prior_id = (journal.previous("entity:order:" + case.reference) or {}).get("entity_id")
            pinned = getattr(journal.item.config, "_retry_plan", {}).get("saved_order")
            if pinned and (pinned["reference"] != case.reference or prior_id != pinned["id"]):
                raise AssertionError("Davom ettirilayotgan order IDsi yoki TTN mos emas")
            if prior_id and identity and identity != prior_id:
                raise AssertionError("Ro‘yxatdagi TTN oldingi order ID siga mos kelmadi")
            identity = prior_id or identity
            if not identity:
                # A list filter can hide a saved order. Check before issuing another Save.
                saved = ui_row(page, "trade/tdeal/order/order_list:table",
                               ["deal_id", "delivery_number"], "delivery_number", case.reference)
                identity = str(saved["deal_id"]) if saved else None
        if not identity:
            return None
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
    from tests.regression.helpers.retry.reconcile import is_retry, ui_row, allow_absent_ui_write, confirm_entity
    if is_retry():
        with allure.step("Retry: avvalgi TTN bilan saqlangan orderni serverdan qidirish"):
            row = ui_row(page, "trade/tdeal/order/order_list:table",
                         ["deal_id", "delivery_number"], "delivery_number", reference, document_kind="order")
            if row:
                confirm_entity("order", reference, row["deal_id"])
                from tests.regression.helpers.retry.state import ACTIVE
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
            from tests.regression.helpers.retry.state import RetryBlocked
            raise RetryBlocked("Order Save’dan keyin exact TTN topilmadi; qayta Save yuborilmadi")
        confirm_entity("order", reference, saved["deal_id"])
    with allure.step("Unique TTN bo'yicha aynan yangi orderni topish"):
        column = base.grid_setting(menu_name="Настройка таблицы", field_name="Номер ТТН", search_name="Номер ТТН")
        base.wait_for_loader()
        rows = page.locator("smt-data-table:visible .smt-data-row")
        current_search = page.get_by_role("main").get_by_role("searchbox").input_value()
        already_found = (
            current_search == reference
            and rows.count() == 1
            and base.grid_cell(rows.first, column, return_value=True) == reference
        )
        if not already_found:
            if current_search == reference:
                # Let the grid apply the empty filter before submitting the same TTN again.
                def cleared(response):
                    return (unquote(urlsplit(response.url).path).endswith("/trade/tdeal/order/order_list:table")
                            and _lookup_query_finished(response.request, "", "delivery_number"))

                with page.expect_response(cleared) as pending:
                    base.grid_controller(search="")
                if not pending.value.ok:
                    raise AssertionError(f"TTN qidiruvini tozalash HTTP {pending.value.status} qaytardi")
                pending.value.finished()
            found = find_list_record(base, "order_list", "delivery_number", reference,
                                     also_match={"deal_id": saved["deal_id"]})
            if found is None:
                raise AssertionError(f"TTN {reference} qidiruvida saqlangan order {saved['deal_id']} topilmadi")
        expect(rows).to_have_count(1)
        row = base.grid(reference)
        reference_cell = base.grid_cell(row, column)
        expect(reference_cell).to_have_text(reference)
        reference_cell.get_by_text(reference, exact=True).click()
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


def open_order_summary(page, *, expected_total=None):
    """Yakunlashga o'tib, Order formasidagi yagona jami maydonini kutadi."""
    base = AutoBasePage(page)
    with allure.step("Order yakunlash bosqichini ochish"):
        base.click(name="Далее", exact=True)
        forms = page.locator("main form:visible")
        total_label = page.locator("label").filter(has_text=re.compile(r"^\s*ИТОГО\s*$"), visible=True)
        expect(forms.locator(total_label)).to_have_count(1)
        summary_form = forms.filter(has=total_label)
        if expected_total is None:
            base.input(label="ИТОГО", root=summary_form)
        else:
            base.input(label="ИТОГО", root=summary_form, expect_value=str(expected_total))


def reopen_order_goods(page):
    base = AutoBasePage(page)
    with allure.step("Saqlangan orderni tahrirga qayta ochish"):
        base.click(name="Редактировать", exact=True)
        base.expect_page(heading="Заказ (изменение)", url=re.compile(r"order(?:%2[Bb]|\+)edit"))
    with allure.step("Saqlangan mahsulotlar bosqichini ochish"):
        base.click(name="Далее", exact=True)
        base.text("Название", "Кол-во")


def select_client_product(page, client, product, price_type):
    """Klientni tanlab, mahsulot bosqichida kerakli narxdagi qatorni ochadi."""
    base = AutoBasePage(page)
    with allure.step("Klientni tanlab orderga mahsulot qo‘shish"):
        # Initial room/staff selection refreshes the client picker.
        base.b_input(label="Рабочая зона", expect_value=re.compile(r"\S"))
        base.b_input(label="Штат", expect_value=re.compile(r"\S"))
        base.b_input(label="Клиент", value=client, lookup_route="order+add:persons")
        base.click(name="Далее", exact=True)
        base.text("Название", "Кол-во")
        return select_order_product(page, product, price_type)


@contextmanager
def product_loaded(page, product_id, price_type_id):
    """Wait for this selection's price and stock before editing its quantity."""
    def matches(response):
        if not unquote(urlsplit(response.url).path).endswith("/order/order+add:get_product_data"):
            return False
        data = response.request.post_data_json
        return (str(data["product_id"]) == str(product_id)
                and str(data["price_type_id"]) == str(price_type_id))

    with page.expect_response(matches) as loaded:
        yield
    if not loaded.value.ok:
        raise AssertionError(f"Mahsulot ma’lumotlarini yuklash HTTP {loaded.value.status}")
    loaded.value.finished()


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
