"""Order guruhida saqlangan sessiyani testning birinchi sahifasida ochish."""
from utils.base_pages import UI_TIMEOUT_MS
from utils.base_pages.auto_base_page import AutoBasePage


MENU_ROUTES = {
    ("Продажа", "Заказы"): "trade/tdeal/order/order_list",
    ("Продажа", "Архив заказов"): "trade/tdeal/order/order_history_list",
    ("Продажа", "Отмененные заказы"): "trade/tdeal/order/order_cancelled_list",
    ("Продажа", "Взаиморасчеты с клиентами"): "anor/mdeal/order/offset/offset_list",
    ("Продажа", "Возвраты"): "anor/mdeal/return/return_list",
    ("Финансы", "Оплаты от клиентов"): "trade/tcs/cashin_list",
    ("Склад", "Склады"): "anor/mkw/warehouse_list",
    ("Главное", "Настройки системы"): "trade/pref/system_setting",
}


class OrderPage(AutoBasePage):
    def _enter_session(self, route):
        authorize = getattr(self.page, "_order_first_navigation", None)
        if authorize is None:
            return False
        opened = authorize(self.page, order_entry=route)
        self.page._order_first_navigation = None
        return route is not None and opened == route

    def open_route(self, route, *, heading=None, timeout=UI_TIMEOUT_MS):
        if self._enter_session(route):
            return self.expect_page(url=route, heading=heading, timeout=timeout)
        return self._current_base().open_route(route, heading=heading, timeout=timeout)

    def navigate_to(self, tab="Главное", name="Организации", timeout=UI_TIMEOUT_MS):
        route = MENU_ROUTES.get((tab, name))
        if self._enter_session(route):
            return  # GroupLogin already verified the exact destination URL.
        menu = AutoBasePage(self.page)
        menu.navigate_to(tab=tab, name=name, timeout=timeout)
        if route is not None:
            menu.expect_page(url=route, timeout=timeout)
