import allure
from playwright.sync_api import expect
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Setup"), allure.story("Init Balance")]

# ----------------------------------------------------------------------------------------------------------------------

def run_init_balance(page, code):
    base = BasePage(page)
    product_name = f"product-pw{code}"
    product_code = f"c_p_pw{code}"

    with allure.step("1 - Foydalanuvchi sifatida kirish va sahifani ochish"):
        base.navigate_to(tab="Склад", name="Ввод начальных остатков ТМЦ")
        base.expect_page(heading="Ввод начальных остатков ТМЦ")

    with allure.step("2 - Yangi hujjat yaratish va ma'lumot kiritish"):
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="Ввод начальных остатков ТМЦ (создание)")
        base.input(label="Номер", value=f"{code}")
        base.b_input(ng_model="d.warehouse_name", value="Основной склад", clear=True)
        base.b_input(label="Валюта", value="Узбекский сум", clear=True)

        product_grid = page.locator("b-pg-grid")
        base.b_input(label="Название", value=product_code, expect_value=product_name, root=product_grid)
        base.input(label="Кол-во", value="100", root=product_grid)
        base.input(label="Цена", value="5000", root=product_grid)

    with allure.step("3 - Saqlash va tasdiqlash"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")

    with allure.step("4 - Hujjatni o'tkazish (провести)"):
        base.grid(f"{code}", click=True)
        page.get_by_role("button", name="Провести").click()
        base.confirm_biruni(f"Провести документ № {code}?")
        base.expect_page(heading="Ввод начальных остатков ТМЦ", url="init_inventory_balance_list")

    with allure.step("5 - Provodkalarni tekshirish (miqdor va summa)"):
        base.grid(f"{code}", click=True)
        with page.expect_popup(timeout=30_000) as page2_info:
            page.get_by_role("button", name="Проводки").click()
        page2 = page2_info.value
        expect(page2.get_by_role("rowgroup")).to_contain_text("100")
        expect(page2.get_by_role("rowgroup")).to_contain_text("500 000")

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("Boshlang'ich qoldiqlarni kiritish va o'tkazish")
def test_init_balance (page, code):
    authorization(page, who="user", code=code)
    run_init_balance(page, code)
