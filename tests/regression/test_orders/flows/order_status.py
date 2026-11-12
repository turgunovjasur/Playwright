"""Own orderni exact ID bilan bekor qilish va saved statusini tekshirish."""
import allure
from playwright.sync_api import expect
from tests.regression.test_orders.flows.settlement import _columns
from utils.base_pages.auto_base_page import AutoBasePage


def cancel_order(page, *, order_id, client, amount):
    """List → exact order → cancel reason → cancelled list → same View."""
    base = AutoBasePage(page)
    from tests.regression.retry.reconcile import is_retry, allow_absent_ui_write
    if is_retry():
        with allure.step("Retry: oldingi bekor qilish saqlanganini tekshirish"):
            base.open_route("trade/tdeal/order/order_view?deal_id=" + str(order_id), heading="Заказ / Просмотр")
            base.form_view(label="ИД заказа", expect_value=str(order_id))
            base.form_view(label="Клиент", expect_value=client)
            base.form_view(label="Сумма заказа", expect_value=amount, remove_spaces=True)
            if base.form_view(label="Статус", return_value=True).strip() == "Отменен":
                return
            allow_absent_ui_write("trade/tdeal/order/order_list:change_status", identity={"deal_id": str(order_id)})
    with allure.step("6 - Bekor qilish uchun aynan own orderni ID bilan topish"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
        id_col = _columns(page, {"id": "ИД заказа"}, search_name="ИД заказа")["id"]
        base.grid_controller(search=order_id)
        row = base.grid(order_id)
        expect(base.grid_cell(row, id_col)).to_have_text(order_id)
    with allure.step("7 - Orderni bekor qilish sababini tanlash oynasini ochish"):
        base.click(name="Изменить статус", exact=True, root=row)
        base.click(name="Отменен", role="menuitem", exact=True)
        dialog = page.get_by_role("dialog").filter(has=page.get_by_role("heading", name=f"Отмена заказа: {client}", exact=True))
        expect(dialog).to_have_count(1)
        expect(dialog).to_be_visible()
    with allure.step("8 - Клиент отменил sababi bilan own orderni bekor qilish"):
        base.click(name="Клиент отменил", exact=True, root=dialog)
        base.click(name="Изменить", exact=True, root=dialog)
        expect(dialog).not_to_be_visible()
        base.expect_page(heading="Заказы", url="order_list")
        base.grid_controller(search=order_id)
        base.grid(state="empty")
    with allure.step("9 - Bekor qilingan orderlar ro'yxatidan aynan shu IDni topish"):
        base.navigate_to(tab="Продажа", name="Отмененные заказы")
        # Route 1420-two-wh-cancel-list-retained.txt birinchi satrida tasdiqlangan.
        base.expect_page(heading="Отмененные заказы", url="order_cancelled_list")
        id_col = _columns(page, {"id": "ИД заказа"}, search_name="ИД заказа")["id"]
        base.grid_controller(search=order_id)
        row = base.grid(order_id, click=True)
        expect(base.grid_cell(row, id_col)).to_have_text(order_id)
    with allure.step("10 - Bekor qilingan order viewida ID, klient, summa va status"):
        base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Заказ / Просмотр", url="order_view")
        base.form_view(label="ИД заказа", expect_value=order_id)
        base.form_view(label="Клиент", expect_value=client)
        base.form_view(label="Статус", expect_value="Отменен")
        base.form_view(label="Сумма заказа", expect_value=amount, remove_spaces=True)
