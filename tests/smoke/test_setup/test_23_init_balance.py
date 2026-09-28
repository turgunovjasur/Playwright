import allure
import re
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Init Balance")]

# ----------------------------------------------------------------------------------------------------------------------

def _doc_on_list(base, number):
    try:
        base.grid_controller(search=str(number))
        _balance_row(base.page, number)
        return True
    except (AssertionError, Exception) as exc:
        if "Timeout" not in type(exc).__name__ and not isinstance(exc, AssertionError):
            raise
        return False

# ----------------------------------------------------------------------------------------------------------------------

def run_init_balance(page, code):
    """UZS va USD mahsulotlari uchun boshlang'ich qoldiq yaratish.

    1. Boshlang'ich qoldiq hujjatlari ro'yxatini ochish.
    2. UZS qoldiq hujjati formasini ochib, product-pw{code} uchun qiymatlarni kiritish.
    3. UZS qoldiq hujjatini saqlab, ro'yxatda tekshirish.
    4. UZS qoldiq hujjatini o'tkazish.
    5. UZS provodkalarida 100 dona va 500 000 summani tekshirish.
    6. USD qoldiq hujjati formasini ochib, product-usa-pw{code} uchun qiymatlarni kiritish.
    7. USD qoldiq hujjatini saqlab, ro'yxatda tekshirish.
    8. USD qoldiq hujjatini o'tkazish.
    """
    base = AutoBasePage(page)
    document_number = str(code)
    document_usa_number = f"1{code}"
    quantity = "100"

    with allure.step("1 - Boshlang'ich qoldiq hujjatlari ro'yxatini ochish"):
        base.navigate_to(tab="Склад", name="Ввод начальных остатков ТМЦ")
        base.expect_page(heading="Ввод начальных остатков ТМЦ")

    uzs_exists = _doc_on_list(base, document_number)
    if not uzs_exists:
        with allure.step("2 - UZS qoldiq hujjati formasini ochish va to'ldirish"):
            base.click(name="Создать")
            base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)")
            base.input(label="Номер", value=document_number)
            base.b_input(label="Склад", value="Основной склад", clear=True)
            base.b_input(label="Валюта", value="Узбекский сум", clear=True)
            _fill_init_balance_product_row(
                page,
                product_code=f"c_p_pw{code}",
                product_name=f"product-pw{code}",
                quantity=quantity,
                price="5000",
            )

        with allure.step("3 - UZS qoldiq hujjatini saqlash va ro'yxatda tekshirish"):
            base.click(name="Сохранить", exact=True)
            base.confirm_biruni("Сохранить?")
            base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
            base.grid_controller(search=document_number)
            _balance_row(page, document_number)
    else:
        with allure.step("3 - UZS qoldiq hujjati allaqachon ro'yxatda"):
            base.grid_controller(search=document_number)
            _balance_row(page, document_number)

    with allure.step("4 - UZS qoldiq hujjatini o'tkazish"):
        _post_init_balance_if_needed(base, page, document_number)

    with allure.step("5 - UZS provodkalarida miqdor va summani tekshirish"):
        _open_init_balance_postings(base, page, document_number, quantity, "500 000")

    usd_exists = _doc_on_list(base, document_usa_number)
    if not usd_exists:
        with allure.step("6 - USD qoldiq hujjati formasini ochish va to'ldirish"):
            base.click(name="Создать")
            base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)")
            base.input(label="Номер", value=document_usa_number)
            base.b_input(label="Склад", value="Основной склад", clear=True)
            base.b_input(label="Валюта", value="Доллар США", clear=True)
            _fill_init_balance_product_row(
                page,
                product_code=f"c_p_usa_pw{code}",
                product_name=f"product-usa-pw{code}",
                quantity=quantity,
                price="1",
            )

        with allure.step("7 - USD qoldiq hujjatini saqlash va ro'yxatda tekshirish"):
            base.click(name="Сохранить", exact=True)
            base.confirm_biruni("Сохранить?")
            base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")
            base.grid_controller(search=document_usa_number)
            _balance_row(page, document_usa_number)
    else:
        with allure.step("7 - USD qoldiq hujjati allaqachon ro'yxatda"):
            base.grid_controller(search=document_usa_number)
            _balance_row(page, document_usa_number)

    with allure.step("8 - USD qoldiq hujjatini o'tkazish"):
        _post_init_balance_if_needed(base, page, document_usa_number)

# ----------------------------------------------------------------------------------------------------------------------

def _balance_row(page, number, *, prefer_posted=False):
    rows = page.locator("smt-data-table").filter(visible=True).first.locator(".smt-data-row")
    expect(rows.first).to_be_visible(timeout=10_000)
    needle = str(number)
    count = rows.count()
    matches = []
    texts = []
    for i in range(count):
        compact = re.sub(r"\s+", "", rows.nth(i).inner_text())
        texts.append(compact)
        if re.match(rf"^{re.escape(needle)}\d{{2}}\.", compact):
            posted = compact.endswith("Да") or compact.endswith("Yes")
            matches.append((posted, rows.nth(i)))
    if not matches:
        raise AssertionError(f"Balance document {needle} not found in grid: {texts}")
    if prefer_posted:
        for posted, row in matches:
            if posted:
                return row
    return matches[0][1]


def _expand_balance_row(row):
    classes = row.get_attribute("class") or ""
    if "smt-expanded" not in classes:
        row.click(timeout=10_000)
        expect(row).to_have_class(re.compile(r"smt-expanded"), timeout=10_000)


def _row_action_button(page, row, name):
    _expand_balance_row(row)
    matcher = re.compile(name, re.IGNORECASE)
    btn = page.locator("button:visible").filter(has_text=matcher).first
    if btn.count() == 0:
        labels = [t.strip() for t in page.locator("button:visible").all_inner_texts() if t.strip()]
        raise AssertionError(f"Row action {name!r} not found. Visible buttons: {labels}")
    expect(btn).to_be_visible(timeout=10_000)
    return btn


def _post_init_balance_if_needed(base, page, document_number):
    base.grid_controller(search=str(document_number))
    row = _balance_row(page, document_number, prefer_posted=True)
    _expand_balance_row(row)
    posted_action = page.locator("button:visible").filter(has_text=re.compile(r"Проводк|Transaction", re.IGNORECASE))
    if posted_action.count():
        return
    toggle = row.get_by_role("checkbox").first
    if toggle.count():
        toggle.check(force=True)
    bulk = page.locator("button:visible").filter(has_text=re.compile(r"Провести\s+\d+|Post\s+\d+", re.IGNORECASE))
    if bulk.count() == 0:
        _expand_balance_row(row)
        bulk = page.locator("button:visible").filter(has_text=re.compile(r"Провести", re.IGNORECASE))
        if bulk.count() == 0:
            return
    bulk.first.click()
    base.confirm_biruni()
    error = page.locator("[role='dialog']:visible")
    try:
        expect(error).to_have_count(0, timeout=3_000)
    except (AssertionError, Exception):
        if error.count():
            raise AssertionError(error.first.inner_text()) from None
    page.wait_for_timeout(1_000)
    base.grid_controller(search=str(document_number))
    row = _balance_row(page, document_number, prefer_posted=True)
    _expand_balance_row(row)
    expect(page.locator("button:visible").filter(has_text=re.compile(r"Проводк|Transaction", re.IGNORECASE))).to_be_visible(
        timeout=15_000
    )


def _open_init_balance_postings(base, page, document_number, quantity, amount):
    base.grid_controller(search=str(document_number))
    row = _balance_row(page, document_number, prefer_posted=True)
    with page.expect_popup(timeout=30_000) as postings_page_info:
        _row_action_button(page, row, r"Проводки|Transactions").click()
    postings_page = postings_page_info.value
    expect(postings_page.get_by_role("rowgroup")).to_contain_text(quantity)
    expect(postings_page.get_by_role("rowgroup")).to_contain_text(amount)
    postings_page.close()


def _fill_init_balance_product_row(page, *, product_code, product_name, quantity, price):
    table = page.locator("smt-data-table").filter(visible=True).first
    expect(table).to_be_visible(timeout=10_000)
    search = table.locator(".smt-data-row smt-data-select smt-select-trigger input").first
    expect(search).to_be_visible(timeout=10_000)
    search.click(force=True)
    search.fill(product_code)
    dropdown = page.locator(".cdk-overlay-container smt-select-dropdown:visible").last
    expect(dropdown).to_be_visible(timeout=10_000)
    expect(dropdown.locator(".animate-spin")).to_have_count(0, timeout=10_000)
    option = dropdown.locator("li:visible").filter(has_text=product_name).first
    expect(option).to_be_visible(timeout=10_000)
    option.click(force=True)
    row = table.locator(".smt-data-row").filter(has_text=product_code).first
    expect(row).to_be_visible(timeout=10_000)
    qty = row.locator('[data-smt-col-key="quantity"] input').first
    expect(qty).to_be_visible(timeout=10_000)
    qty.fill(quantity)
    price_el = row.locator('[data-smt-col-key="price"] input').first
    expect(price_el).to_be_visible(timeout=10_000)
    price_el.fill(price)


@allure.title("UZS va USD mahsulotlari uchun boshlang'ich qoldiqlar")
def test_init_balance(page, code):
    authorization(page, who="user", code=code)
    run_init_balance(page, code)
