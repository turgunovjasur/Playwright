import re

from playwright.sync_api import expect

A2_NAVIGATION_TIMEOUT = 60_000

# ----------------------------------------------------------------------------------------------------------------------

def navigate_to_a2(page, tab, path, timeout=A2_NAVIGATION_TIMEOUT):
    """Eski menyu orqali a2 (yangi migratsiya) formani ochadi — real foydalanuvchi yo'li.

    tab  — yuqori menyu bo'limi matni ("Продажа", "Склад", "Плагин", ...).
    path — a2 forma yo'li ("trade/tvt/visit_list"); menyu leaf href'i `/a2/{path}` bilan tugaydi.

    Tab bosiladi -> leaf ko'rinadi -> leaf bosiladi -> a2 ga TO'LIQ sahifa navigatsiya bo'ladi
    (SPA emas). URL `/a2/{path}` ga o'tguncha va `document.title` shell nomidan ("Smartup Online")
    forma nomiga aylanguncha kutiladi — bu forma yuklangani signali.
    """
    page.locator("a.menu-link.menu-toggle", has_text=tab).first.click()
    leaf = page.locator(f'a.menu-link[href$="/a2/{path}"]').first
    expect(leaf).to_be_visible()
    leaf.click()
    expect(page).to_have_url(re.compile(re.escape(f"/a2/{path}")), timeout=timeout)
    expect(page).not_to_have_title("Smartup Online", timeout=timeout)

# ----------------------------------------------------------------------------------------------------------------------
