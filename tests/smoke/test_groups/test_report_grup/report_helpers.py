"""Report group uchun umumiy helperlar: b-input tanlash va download tekshirish."""
from pathlib import Path

import allure
from playwright.sync_api import expect

DOWNLOAD_DIR = Path("test-results/downloads")
REPORT_SEARCH_TYPE_DELAY = 50
REPORT_OPTION_TIMEOUT = 30_000
REPORT_DOWNLOAD_TIMEOUT = 120_000


# ----------------------------------------------------------------------------------------------------------------------

def select_b_input_option(page, b_input_name, option, search_text=None):
    """`b-input[name=...]` ichidan Поиск orqali option tanlaydi (.hint-body/div.hint).

    search_text berilsa — qidiruvga shu yoziladi (server-search b-input, masalan price_types,
    real keystroke bilan press_sequentially orqali filterlanadi), option esa bosiladigan to'liq nom.
    Aks holda option'ning o'zi fill bilan yoziladi (client-search b-input).
    """
    b_input = page.locator(f'b-input[name="{b_input_name}"]')
    search = b_input.locator("input[placeholder]").first
    # Oldin saqlangan qiymat bo'lsa, avval clear qilish kerak (.edit = X tugmasi)
    clear_btn = b_input.locator(".edit")
    if clear_btn.is_visible():
        clear_btn.click()
    else:
        search.click()
    if search_text is None:
        search.fill(option)
    else:
        search.press_sequentially(search_text, delay=REPORT_SEARCH_TYPE_DELAY)
    opt = b_input.locator(".hint-item").filter(has_text=option).first
    expect(opt).to_be_visible(timeout=REPORT_OPTION_TIMEOUT)
    opt.click()


# ----------------------------------------------------------------------------------------------------------------------

def generate_and_verify_download(page, trigger, expected_prefix, save_name, timeout=REPORT_DOWNLOAD_TIMEOUT):
    """`trigger` (Locator) bosilganda yuklanadigan faylni kutadi va tekshiradi: prefiks + bo'sh emasligi."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with page.expect_download(timeout=timeout) as download_info:
        trigger.click()
    download = download_info.value

    failure = download.failure()
    if failure:
        raise AssertionError(f"{save_name} download xato bilan tugadi: {failure}")

    suggested = download.suggested_filename
    allure.attach(suggested, name=f"{save_name}-filename", attachment_type=allure.attachment_type.TEXT)
    if not suggested.startswith(expected_prefix):
        raise AssertionError(f"Kutilmagan fayl nomi: {suggested} (kutilgan prefiks: {expected_prefix})")

    target = DOWNLOAD_DIR / save_name
    download.save_as(str(target))
    size = target.stat().st_size
    allure.attach(str(size), name=f"{save_name}-size", attachment_type=allure.attachment_type.TEXT)
    if size <= 0:
        raise AssertionError(f"{save_name} bo'sh (0 bytes)")
    return suggested
