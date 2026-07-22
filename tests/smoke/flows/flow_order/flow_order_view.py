import allure

from utils.base_page import BasePage

# ----------------------------------------------------------------------------------------------------------------------

def flow_order_view(page, get_value=None):
    base = BasePage(page)
    base.expect_page(url="order_view")
    base.text("Заказ / Просмотр", root="#kt_content")

    result = {}
    if get_value is not None:
        keys = get_value if isinstance(get_value, list) else [get_value]
        for key in keys:
            with allure.step(f"Order View: value -> '{key}' olindi"):
                result[key] = base.form_view(label=key, return_value=True)

    page.get_by_role("button", name="Закрыть", exact=True).click()
    base.expect_page(heading="Заказы", url="order_list")

    if get_value is None:
        return None

    return result if isinstance(get_value, list) else result[get_value]

# ----------------------------------------------------------------------------------------------------------------------
