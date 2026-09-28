import allure
from playwright.sync_api import Page

from utils.base_pages.auto_base_page import AutoBasePage


def _ensure_natural_person_list(base: AutoBasePage, page: Page) -> None:
    if "natural_person" in page.url and "natural_person+" not in page.url and "_view" not in page.url:
        base.expect_page(heading="Физические лица")
        return
    base.navigate_to(tab="Справочники", name="Физические лица")
    base.expect_page(heading="Физические лица")


def open_natural_person_list(page: Page, *, step_name: str) -> None:
    """Jismoniy shaxslar ro'yxatini ochadi va sahifa holatini tekshiradi."""
    base = AutoBasePage(page)
    with allure.step(step_name):
        _ensure_natural_person_list(base, page)


# ----------------------------------------------------------------------------------------------------------------------

def open_natural_person_create(page: Page, *, step_name: str) -> None:
    """Jismoniy shaxs yaratish formasini ochadi."""
    base = AutoBasePage(page)
    with allure.step(step_name):
        base.click(name="Создать")
        base.expect_page(heading="Физическое лицо (создание)")


# ----------------------------------------------------------------------------------------------------------------------

def create_natural_person(page: Page, name: str, person_code: str, *, step_name: str, client: bool = False) -> None:
    """Ochiq create formani to'ldirib, jismoniy shaxsni saqlaydi."""
    base = AutoBasePage(page)
    with allure.step(step_name):
        base.input(label="Имя", value=name)
        base.input(label="Код", value=person_code)
        if client:
            base.checkbox(label="Клиент", checked=True)
        base.checkbox(label="Статус", expect_checked=True)
        base.click(name="Сохранить", exact=True)
        base.confirm_biruni()
        try:
            base.expect_page(heading="Физические лица")
        except AssertionError:
            _ensure_natural_person_list(base, page)


# ----------------------------------------------------------------------------------------------------------------------

def open_natural_person_view(page: Page, name: str, *, step_name: str) -> None:
    """Tanlangan jismoniy shaxs view formasini ochadi."""
    base = AutoBasePage(page)
    with allure.step(step_name):
        base.grid(name, click=True)
        base.click(name="Просмотр", exact=True)
        base.expect_page(heading="Физическое лицо (просмотр)")


# ----------------------------------------------------------------------------------------------------------------------

def close_natural_person_view(page: Page, *, step_name: str) -> None:
    """Jismoniy shaxs view formasini yopib, ro'yxatga qaytadi."""
    base = AutoBasePage(page)
    with allure.step(step_name):
        try:
            base.click(name="Закрыть")
        except Exception:
            pass
        try:
            base.expect_page(heading="Физические лица")
        except AssertionError:
            _ensure_natural_person_list(base, page)
