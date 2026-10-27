"""Order fixture teardownida faqat shu case'ning moliyaviy hujjatlarini qaytarish."""

import allure
from playwright.sync_api import expect

from utils.base_pages.auto_base_page import AutoBasePage


def cleanup_order_finance(page, case):
    """Avval allocation, keyin Return, so'ng cashin; source order bundan keyin.

    Pending flag submitdan oldin yoziladi: submit qabul bo'lib, readback yiqilsa
    ham yagona own klient orqali hujjat topiladi. Boshqa klientga tegilmaydi.
    Noma'lum yoki bittadan ko'p pending hujjat bo'lsa cleanup xato qaytaradi.
    """
    base = AutoBasePage(page)
    if case.allocations or case.allocation_pending:
        with allure.step("Finance cleanup: hisob-kitob ro'yxatini ochish"):
            base.navigate_to(tab="Продажа", name="Взаиморасчеты с клиентами")
            base.expect_page(heading="Взаиморасчеты с клиентами", url="offset_list")
        with allure.step("Finance cleanup: faqat own klientning allocation tarixini ochish"):
            base.click(name="История взаиморасчетов", role="link", exact=True)
            base.expect_page(heading="История взаиморасчетов", url="offset_history_list")
            number_column = base.grid_setting(menu_name="Настройка таблицы", field_name="Номер взаиморасчета", search_name="Клиент")
            base.grid_controller(search=case.client)
        with allure.step("Finance cleanup: own allocationni bekor qilish"):
            if base.grid(case.client, return_bool=True):
                expect(page.locator("b-grid:visible").get_by_text(case.client, exact=True)).to_have_count(1)
                row = base.grid(case.client, click=True)
                number = base.grid_cell(row, number_column, return_value=True).strip()
                if case.allocations and number not in case.allocations:
                    raise AssertionError(f"Cleanup boshqa allocationni tanlamaydi: {number}")
                base.click(name="Отменить взаиморасчет", exact=True, root=row)
                base.confirm_biruni("Отменить?")
                base.wait_for_loader()
                base.grid_controller(search=case.client)
            base.grid(state="empty")
            case.allocations.clear()
            case.allocation_pending = False

    if case.returns or case.return_pending:
        with allure.step("Finance cleanup: own Return ro'yxatini ochish"):
            base.navigate_to(tab="Продажа", name="Возвраты")
            base.expect_page(heading="Возвраты", url="anor/mdeal/return/return_list")
            base.grid_controller(search=case.client)
        if base.grid(case.client, return_bool=True):
            expect(page.locator("b-grid:visible").get_by_text(case.client, exact=True)).to_have_count(1)
            row = base.grid(case.client, click=True)
            with allure.step("Finance cleanup: Return ID va statusini view orqali tekshirish"):
                base.click(name="Просмотреть", exact=True, root=row)
                base.expect_page(heading="Возврат (просмотр)", url="return_view")
                return_id = base.form_view(label="ИД возврата", return_value=True).strip()
                base.form_view(label="Клиент", expect_value=case.client)
                if case.returns and return_id not in case.returns:
                    raise AssertionError(f"Cleanup boshqa Returnni tanlamaydi: {return_id}")
                status = base.form_view(label="Статус", return_value=True).strip()
            with allure.step("Finance cleanup: Return ro'yxatiga qaytish"):
                base.click(name="Закрыть", exact=True)
                base.expect_page(heading="Возвраты", url="anor/mdeal/return/return_list")
            if status != "Черновик":
                with allure.step("Finance cleanup: own Returnni Черновик holatiga qaytarish"):
                    row = base.grid(case.client, click=True)
                    base.click(name="Статус", exact=True, root=row)
                    coach = page.get_by_role("dialog", name="Статус", exact=True)
                    if coach.is_visible():
                        base.click(name="Больше не показывать", exact=True, root=coach)
                    base.click(name="Черновик", role="link", root=row)
                    base.confirm_biruni("Изменить на Черновик?")
                    base.wait_for_loader()
                    base.grid(case.client, "Черновик")
            case.returns.clear()
            case.return_pending = False
        else:
            base.grid(state="empty")
            if case.returns:
                raise AssertionError(f"Ro'yxatdan o'tgan own Return topilmadi: {case.returns}")
            case.return_pending = False

    for number in list(case.cashins):
        with allure.step(f"Finance cleanup: own to'lov {number} ro'yxatini ochish"):
            base.navigate_to(tab="Финансы", name="Оплаты от клиентов")
            base.expect_page(heading="Оплаты от клиентов", url="cashin_list")
            posted_column = base.grid_setting(menu_name="Настройка таблицы", field_name="Проведено", search_name="Номер оплаты")
            base.grid_controller(search=number)
            row = base.grid(number, case.client, click=True)
            posted = base.grid_cell(row, posted_column, return_value=True).strip()
        with allure.step(f"Finance cleanup: {number} o'tkazilmagan holatda qolishi"):
            if posted == "Да":
                base.click(name="Отменить", exact=True, root=row)
                base.confirm_biruni(f"Отменить {number}?")
                base.wait_for_loader()
                row = base.grid(number, case.client)
            base.grid_cell(row, posted_column, expect_value="Нет")
            case.cashins.remove(number)
