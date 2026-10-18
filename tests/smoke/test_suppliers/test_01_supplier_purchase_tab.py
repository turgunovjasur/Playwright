"""A2 supplier purchase-tab regression; opt-in standalone test, not a runner item.

Creates its own legal-person prerequisite and supplier. The supplier is removed
in finally; the uniquely named legal-person prerequisite remains for diagnostics.
This focused regression does not claim coverage of the whole CRUD checklist.
"""

import re
from urllib.parse import unquote
from uuid import uuid4

import allure
from playwright.sync_api import expect

from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [allure.epic("Smoke"), allure.feature("Поставщики"), allure.story("A2 purchase tab")]


def run_supplier_purchase_tab(page, code):
    """1. Open supplier list.
    2. Open the supplier create form.
    3. Open the inline legal-person drawer.
    4. Create a unique legal-person prerequisite.
    5. Save the supplier and verify its list row.
    6. Open view and verify name/code.
    7. Open purchases and require a successful response and no error dialog.
    8. Remove only this test's supplier, including after a failed assertion.
    """
    base = AutoBasePage(page)
    suffix = f"{code}_{uuid4().hex[:6]}"
    supplier_name = f"supplier-pw{suffix}"
    supplier_code = f"c_sup_pw{suffix}"
    created = False
    failure = None

    with allure.step("1 - Supplier listni ochish"):
        base.navigate_to(tab="Склад", name="Поставщики")
        base.expect_page(heading="Поставщики", url="/a2/anor/mkw/supplier_list")

    with allure.step("2 - Supplier yaratish formasini ochish"):
        base.click(name="Создать", exact=True)
        base.expect_page(heading="Поставщик (создание)", url=re.compile(r"anor/mkw/supplier(?:\+|%2[bB])add(?:[?#]|$)"))

    with allure.step("3 - Inline yuridik shaxs formasini ochish"):
        base.b_input(label="Название").click()
        expect(page.get_by_text("Загрузка...", exact=True)).to_be_hidden()
        base.click(name="Добавить", exact=True, root="body")
        base.expect_page(heading="Юридическое лицо (создание)", root="body")  # navigation: same-url - Inline legal-person drawer keeps the supplier create route.

    with allure.step("4 - Test uchun noyob shaxsni saqlash"):
        drawer = page.get_by_role("main").last
        base.input(label="Код", value=supplier_code, root=drawer)
        base.input(label="Полное название", value=supplier_name, root=drawer)
        base.click(name="Сохранить", exact=True, root=drawer)
        base.confirm_biruni("Сохранить")
        expect(page.get_by_role("heading", name="Юридическое лицо (создание)", exact=True)).to_be_hidden()
        base.expect_page(heading="Поставщик (создание)", url=re.compile(r"anor/mkw/supplier(?:\+|%2[bB])add(?:[?#]|$)"))
        base.b_input(label="Название", expect_value=supplier_name)

    try:
        with allure.step("5 - Supplierni saqlash va listda tekshirish"):
            base.click(name="Сохранить", exact=True)
            base.confirm_biruni("Сохранить")
            # A successful save may precede a failed list assertion; cleanup still applies.
            created = True
            base.expect_page(heading="Поставщики", url="supplier_list")
            base.grid_controller(search=supplier_code)
            base.grid(supplier_code, supplier_name, "Активный", click=True)

        with allure.step("6 - Supplier view qiymatlarini tekshirish"):
            base.click(name="Просмотреть", exact=True)
            base.expect_page(heading="Поставщик (просмотр)", url="supplier_view")
            base.input(label="Название", expect_value=supplier_name)
            base.input(label="Код", expect_value=supplier_code)

        with allure.step("7 - Закупки tabi xatosiz ochilishini tekshirish"):
            # Match the endpoint reported by the observed UI error. Awaiting the
            # response prevents a negative assertion from passing before loading.
            with page.expect_response(lambda response: "anor/mkw/supplier_view:purchase" in unquote(response.url)) as pending:
                base.click(name="Закупки", exact=True, role="tab")
            response = pending.value
            response.finished()
            allure.attach(f"HTTP {response.status}", name="purchase response", attachment_type=allure.attachment_type.TEXT)
            if not response.ok:
                raise AssertionError(f"Supplier purchase response failed: HTTP {response.status}")
            base.wait_for_loader()
            base.expect_page(heading="Поставщик (просмотр)", url="supplier_view")
            expect(page.get_by_role("heading", name="Ошибка", exact=True)).to_be_hidden()
            base.text("Дата закупа", "Номер", "Договор", "Валюта", "Сумма", "Статус")
    except Exception as exc:
        failure = exc
        allure.attach(page.screenshot(), name="supplier failure before cleanup", attachment_type=allure.attachment_type.PNG)
        raise
    finally:
        if created:
            try:
                with allure.step("8 - Faqat shu test supplierini o'chirish"):
                    if page.get_by_role("heading", name="Ошибка", exact=True).is_visible():
                        base.close_biruni_alert()
                    base.navigate_to(tab="Склад", name="Поставщики")
                    base.expect_page(heading="Поставщики", url="supplier_list")
                    base.grid_controller(search=supplier_code)
                    base.grid(supplier_code, supplier_name, click=True)
                    base.click(name="Удалить", exact=True)
                    base.confirm_biruni(supplier_name)
                    base.grid(state="empty")
            except Exception as cleanup_error:
                if failure is None:
                    raise
                failure.add_note(f"Supplier cleanup also failed: {cleanup_error}")


@allure.title("A2 supplier: create, view and purchase tab without error")
def test_supplier_purchase_tab(page, code):
    authorization(page, who="admin")
    AutoBasePage(page).switch_filial(name=f"filial-pw{code}")
    run_supplier_purchase_tab(page, code)
