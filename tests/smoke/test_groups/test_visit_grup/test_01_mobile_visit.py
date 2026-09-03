"""Ordersiz minimal Visitni API orqali yaratib Web'da tekshirish testcase'i."""

from datetime import datetime

import allure

from tests.smoke.clients.visit_sync import build_minimal_visit
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_mobile_authorization import authorize_mobile
from tests.smoke.flows.flow_navigate import navigate_to_a2
from tests.smoke.flows.flow_visit_sync import sync_visit
from utils.angular_base_page import AngularBasePage
from utils.helper_utils import query_int_from_url


def _require_close_datetime(actual, expected, *, field, tolerance_seconds=5):
    """Ikki Smartup datetime qiymati tolerance ichida ekanini tekshiradi."""
    try:
        actual_value = datetime.strptime(actual, "%d.%m.%Y %H:%M:%S")
        expected_value = datetime.strptime(expected, "%d.%m.%Y %H:%M:%S")
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"{field} dd.MM.yyyy HH:mm:ss formatida emas: {actual!r}") from exc
    difference = abs((actual_value - expected_value).total_seconds())
    if difference > tolerance_seconds:
        raise AssertionError(f"{field} yuborilgan vaqtdan {difference}s farq qildi; ruxsat etilgan tolerance={tolerance_seconds}s")


def api_create_minimal_visit(load_data, save_data):
    """Mobile API orqali ordersiz Visit yaratib ``MinimalVisit`` qaytaradi.

    1. Mobile API orqali login qilish va target filialni tekshirish.
    2. Sync endpoint orqali ordersiz minimal Visit yaratish.
    """
    with allure.step("1 - Mobile API orqali login qilish"):
        mobile_authorization = authorize_mobile(load_data, save_data)

    with allure.step("2 - API orqali ordersiz minimal Visit yaratish"):
        visit = build_minimal_visit(filial_id=load_data("filial_id"), room_id=load_data("room_id"), robot_id=load_data("robot_id"), client_person_id=load_data("client_person_id"))
        sync_result = sync_visit(mobile_authorization, visit)
        if sync_result.entry_id != visit.entry_id:
            raise AssertionError("Sync response entry_id yuborilgan Visit bilan mos emas")
        save_data("mobile_visit_id", visit.entry_id)
        save_data("mobile_visit_note", visit.visit_note)
        save_data("mobile_visit_begun_on", visit.begun_on)
        save_data("mobile_visit_ended_on", visit.ended_on)
        save_data("mobile_visit_spent_time", visit.spent_time)

    return visit


def web_verify_minimal_visit(page, visit, load_data, save_data):
    """Minimal Visitni Web list/viewda tekshirib server Visit IDni qaytaradi.

    3. Web user sifatida login qilish.
    4. Visit listdan yaratilgan exact Visitni topish.
    5. Visit viewdagi asosiy va qo'shimcha qiymatlarni tekshirish.
    6. Visit note'ni tekshirish va server Visit IDni saqlash.
    """
    with allure.step("3 - Web user sifatida login qilish"):
        code = load_data("code")
        authorization(page, who="user", code=code)

    base = AngularBasePage(page)
    client_name = f"natural_client-pw{code}"
    user_person_name = f"natural_person-pw{code}"
    room_name = f"room-pw{code}"

    with allure.step("4 - Visit listda yaratilgan exact Visitni topish"):
        navigate_to_a2(page, tab="Продажа", path="trade/tvt/visit_list")
        base.expect_page(heading="Визиты", url="trade/tvt/visit_list")
        base.grid_setting(menu_name="Настройка таблицы", field_name="Примечание к визиту")
        visit_id_index = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД")
        base.grid_controller(search=client_name)
        visit_row = base.grid(visit.visit_note, client_name, room_name, user_person_name, "Новый")
        server_visit_id = int(base.grid_cell(visit_row, visit_id_index, return_value=True))
        if server_visit_id <= 0:
            raise AssertionError("Web Visit ID musbat integer emas")

    with allure.step("5 - Visit viewdagi asosiy va qo'shimcha qiymatlarni tekshirish"):
        visit_row.click()
        base.click(name="Просмотреть", exact=True)
        base.expect_page(heading="Визит (просмотр)", url="trade/tvt/visit_view")
        if query_int_from_url(page.url, "visit_id") != server_visit_id:
            raise AssertionError("Visit row ID va view URL ID bir xil emas")

        base.input(label="ID визита", expect_value=str(server_visit_id))
        base.input(label="Статус", expect_value="Новый")
        actual_visit_time = base.input(label="Время визита", index=0, return_value=True)
        _require_close_datetime(actual_visit_time, visit.ended_on, field="Visit view vaqti")
        base.input(label="Рабочая зона", expect_value=room_name)
        base.input(label="Пользователь", expect_value=user_person_name)
        base.input(label="Клиент", expect_value=client_name)
        base.click(name="Дополнительная информация", role="tab", exact=True)
        actual_begun_on = base.input(label="Начало визита", return_value=True)
        actual_ended_on = base.input(label="Конец визита", return_value=True)
        _require_close_datetime(actual_begun_on, visit.begun_on, field="Visit boshlanish vaqti")
        _require_close_datetime(actual_ended_on, visit.ended_on, field="Visit tugash vaqti")

    with allure.step("6 - Visit note va server Visit IDni saqlash"):
        base.click(name="Примечания", role="tab", exact=True)
        base.grid(visit.visit_note, user_person_name)
        save_data("visit_id", server_visit_id)

    return server_visit_id


def run_mobile_visit_check(page, load_data, save_data):
    """API yaratgan minimal Visitni Web orqali tekshiradi."""
    visit = api_create_minimal_visit(load_data, save_data)
    return web_verify_minimal_visit(page, visit, load_data, save_data)
