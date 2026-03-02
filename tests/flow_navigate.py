from playwright.sync_api import Page, expect

# ----------------------------------------------------------------------------------------------------------------------

def navigate_to(page: Page, tab: str = "Главное", name: str = "Организации") -> None:
    page.get_by_role("link", name=tab).click()
    page.get_by_role("link", name=name).click()

# ----------------------------------------------------------------------------------------------------------------------

def switch_filial(page: Page, name: str = "Администрирование") -> None:
    page.locator(".pt-3.px-2").click()
    page.get_by_role("textbox", name="Поиск организации").fill(name)

    if name == "Администрирование":
        page.get_by_role("link", name=name).click()
    else:
        page.get_by_role("link", name=name, exact=True).click()

    expect(page.get_by_role("paragraph").filter(has_text=name)).to_be_visible()

# ----------------------------------------------------------------------------------------------------------------------
