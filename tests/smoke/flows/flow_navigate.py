from playwright.sync_api import expect

from utils.auto_base_page import AutoBasePage

A2_NAVIGATION_TIMEOUT = 60_000

# ----------------------------------------------------------------------------------------------------------------------

def navigate_to_a2(page, tab, path, timeout=A2_NAVIGATION_TIMEOUT, *, name):
    """Visit flowlarining menyu navigatsiyasini AutoBasePage orqali bajaradi.

    tab  — yuqori menyu bo'limi matni ("Продажа", "Склад", "Плагин", ...).
    name — menyudagi forma nomi ("Визиты").
    path — legacy/A2 prefiksisiz forma yo'li ("trade/tvt/visit_list").

    Mavjud consumerlar uchun tarixiy funksiya nomi saqlangan. Boshlang'ich va
    ochilgan sahifa helperlari joriy URL orqali alohida tanlanadi.
    """
    base = AutoBasePage(page)
    base.navigate_to(tab=tab, name=name, timeout=timeout)
    base.expect_page(url=path, timeout=timeout)
    expect(page).not_to_have_title("Smartup Online", timeout=timeout)

# ----------------------------------------------------------------------------------------------------------------------
