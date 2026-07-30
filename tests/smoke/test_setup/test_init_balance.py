import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Init Balance")]
POSTINGS_POPUP_TIMEOUT = 30_000

# ----------------------------------------------------------------------------------------------------------------------


def _create_and_post_init_balance(
    page,
    *,
    document_number,
    currency_name,
    product_name,
    product_code,
    quantity,
    price,
    balance_label,
    expected_posting_amount=None,
):
    """Bitta TMC uchun boshlang'ich qoldiq hujjatini yaratib o'tkazadi."""
    base = BasePage(page)

    with allure.step(f"1 - {balance_label} qoldiq hujjatlari sahifasini ochish"):
        base.navigate_to(tab="Склад", name="Ввод начальных остатков ТМЦ")
        base.expect_page(heading="Ввод начальных остатков ТМЦ")

    with allure.step(f"2 - {balance_label} qoldiq hujjatini to'ldirish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)")
        base.input(label="Номер", value=document_number)
        base.b_input(ng_model="d.warehouse_name", value="Основной склад", clear=True)
        base.b_input(label="Валюта", value=currency_name, clear=True)

        product_grid = page.locator("b-pg-grid")
        base.b_input(label="Название", value=product_code, expect_value=product_name, root=product_grid)
        base.input(label="Кол-во", value=quantity, root=product_grid)
        base.input(label="Цена", value=price, root=product_grid)

    with allure.step(f"3 - {balance_label} qoldiq hujjatini saqlash"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")

    with allure.step(f"4 - {balance_label} qoldiq hujjatini o'tkazish"):
        base.grid(document_number, click=True)
        page.get_by_role("button", name="Провести").click()
        base.confirm_biruni(f"Провести документ № {document_number}?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")

    if expected_posting_amount:
        with allure.step(
            f"5 - {balance_label} provodkalarida miqdor va summani tekshirish"
        ):
            base.grid(document_number, click=True)
            with page.expect_popup(timeout=POSTINGS_POPUP_TIMEOUT) as page2_info:
                page.get_by_role("button", name="Проводки").click()
            page2 = page2_info.value
            expect(page2.get_by_role("rowgroup")).to_contain_text(quantity)
            expect(page2.get_by_role("rowgroup")).to_contain_text(
                expected_posting_amount
            )
            page2.close()


# ----------------------------------------------------------------------------------------------------------------------

def run_init_balance(page, code):
    """Asosiy UZS mahsuloti uchun boshlang'ich qoldiq yaratish.

    1. Boshlang'ich qoldiq hujjatlari sahifasini ochish.
    2. `product-pw{code}` uchun 100 dona va 5000 UZS kirim narxini kiritish.
    3. Hujjatni saqlash.
    4. Hujjatni o'tkazish.
    5. Provodkalarda 100 dona va 500 000 summani tekshirish.
    """
    _create_and_post_init_balance(
        page,
        document_number=str(code),
        currency_name="Узбекский сум",
        product_name=f"product-pw{code}",
        product_code=f"c_p_pw{code}",
        quantity="100",
        price="5000",
        balance_label="UZS",
        expected_posting_amount="500 000",
    )


# ----------------------------------------------------------------------------------------------------------------------

def run_init_balance_usa(page, code):
    """Ikkinchi USD mahsuloti uchun boshlang'ich qoldiq yaratish.

    1. Boshlang'ich qoldiq hujjatlari sahifasini ochish.
    2. `product-usa-pw{code}` uchun 100 dona va 1 USD kirim narxini kiritish.
    3. Hujjatni saqlash.
    4. Hujjatni o'tkazish.
    """
    _create_and_post_init_balance(
        page,
        document_number=f"1{code}",
        currency_name="Доллар США",
        product_name=f"product-usa-pw{code}",
        product_code=f"c_p_usa_pw{code}",
        quantity="100",
        price="1",
        balance_label="USD",
    )

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("UZS va USD mahsulotlari uchun boshlang'ich qoldiqlar")
def test_init_balance(page, code):
    authorization(page, who="user", code=code)
    run_init_balance(page, code)
    run_init_balance_usa(page, code)
