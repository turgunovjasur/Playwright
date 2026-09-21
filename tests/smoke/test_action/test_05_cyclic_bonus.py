"""Har 10 dona mahsulot uchun 1 dona bonus beruvchi siklik aksiya yaratish."""

import allure

from tests.smoke.test_action.flow_action.flow_action import fill_action_scope, open_action_form
from tests.smoke.flows.flow_authorization import authorization
from utils.base_pages.base_page import BasePage
from utils.data_store import save_data


pytestmark = [allure.epic("Smoke"), allure.feature("Aksiya Setup"), allure.story("05 - Har 10 dona mahsulotga 1 dona siklik bonus aksiyasi")]

# ----------------------------------------------------------------------------------------------------------------------


def run_cyclic_bonus(page, code):
    """Har 10 dona mahsulot uchun 1 dona bonus beruvchi siklik aksiya yaratish.

    1. Aksiyalar ro'yxatidan yaratish formasini ochish.
    2. Nom, kod, sanalar, ish zonasi, ombor va narx turini belgilash.
    3. Shartlar bosqichiga o'tish.
    4. Циклично shart: setup mahsuloti uchun 10 chegarasini belgilash.
    5. Кол-во bonusi: setup mahsulotiga 1 dona berish.
    6. Saqlash va ro'yxatga qaytish.
    7. ID ustunini yoqish va saqlangan aksiyani ro'yxatda tekshirish.
    8. Keyingi Visit ssenariylari uchun aksiya ma'lumotlarini saqlash.
    """
    base = BasePage(page)
    action_name = f"action-cyclic-bonus-pw{code}"
    action_code = f"c_acb_pw{code}"
    product_name = f"product-pw{code}"
    room_name = f"room-pw{code}"
    price_type_name = f"Price Type UZB-pw{code}"
    start_date = base.date()
    end_date = base.date(days=30)

    with allure.step("1 - Aksiya yaratish formasini ochish"):
        open_action_form(page)

    with allure.step("2 - Aksiyaning asosiy ma'lumotlarini to'ldirish"):
        fill_action_scope(page, name=action_name, action_code=action_code, room=room_name, price_type=price_type_name, start_date=start_date, end_date=end_date)
        base.ui_select(label="Тип акции", value="Кол-во")

    with allure.step("3 - Shartlar bosqichiga o'tish"):
        base.click(name="Далее", exact=True)
        base.expect_page(heading="Условия", url="anor/mcg/action+add")
        base.ui_select(label="Тип условия", expect_value="Обычный")

    with allure.step("4 - Циклично shart va 10 chegarasini belgilash"):
        base.checkbox(label="Ассортимент", expect_checked=False)
        base.ui_select(label="Тип условия", value="Циклично")
        # Legacy shart mahsuloti qidiruvida alohida field label yo'q.
        base.b_input(ng_model="d['selected_rule_name_' + condition_index + rule_index]", value=product_name)
        # Jadval sarlavhalari bitta qatorda; label resolver birinchi inputga tushadi.
        base.input(ng_model="rule.main_value", value="10", press_tab=True)
        base.input(ng_model="rule.required_count", value="1", press_tab=True)

    with allure.step("5 - 1 dona bonusni belgilash"):
        base.ui_select(label="Тип бонуса", expect_value="Кол-во")
        # Bonus mahsuloti qidiruvida ham label yo'q; live DOM modeli ishlatiladi.
        base.b_input(ng_model="d['selected_bonus_name_' + condition_index + bonus_index]", value=product_name)
        base.input(ng_model="product.value", value="1", press_tab=True)
        base.ui_select(label="Тип условия", expect_value="Циклично")
        base.input(ng_model="rule.main_value", expect_value="10")

    with allure.step("6 - Aksiyani saqlash va ro'yxatga qaytish"):
        base.click(name="Завершить", exact=True)
        base.confirm_biruni("Сохранить?")
        base.expect_page(heading="Акции", url="anor/mcg/action_list")

    with allure.step("7 - ID ustuni va saqlangan aksiya qiymatlarini tekshirish"):
        action_id_index = base.grid_setting(menu_name="Настройка таблицы", field_name="ИД", search_name="Название")
        base.grid_controller(search=action_name)
        action_row = base.grid(action_name, "Кол-во", start_date, end_date, "Активный")
        action_id = int(base.grid_cell(action_row, action_id_index, return_value=True).strip())
        if action_id <= 0:
            raise AssertionError("Saqlangan aksiya IDsi musbat integer bo'lishi kerak")

    with allure.step("8 - Aksiya setup ma'lumotlarini saqlash"):
        action_data = {
            "action_id": action_id,
            "name": action_name,
            "code": action_code,
            "calc_kind": "Кол-во",
            "rule_kind": "Циклично",
            "threshold": "10",
            "bonus_kind": "Кол-во",
            "bonus_value": "1",
            "product_name": product_name,
            "room_name": room_name,
            "price_type_name": price_type_name,
            "start_date": start_date,
            "end_date": end_date,
        }
        save_data("action_cyclic_bonus", action_data)

# ----------------------------------------------------------------------------------------------------------------------


@allure.title("05 - Har 10 dona mahsulotga 1 dona siklik bonus aksiyasi")
def test_cyclic_bonus(page, code):
    with allure.step("User profil bilan setup filialiga kirish"):
        authorization(page, who="user", code=code)
        BasePage(page).switch_filial(name=f"filial-pw{code}")
    run_cyclic_bonus(page, code)
