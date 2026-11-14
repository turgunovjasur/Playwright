from playwright.sync_api import expect
from utils.base_pages import UI_TIMEOUT_MS


def fill_nps_survey(page, logger):
    """NPS Survey modal chiqsa - to'ldirib yuboradi"""
    try:
        expect(page.get_by_role("heading", name="NPS Survey")).to_be_visible(timeout=UI_TIMEOUT_MS)
        page.get_by_role("button", name="10").click()
        page.get_by_role("button", name="Отправить").click()
        logger.info("NPS Survey modal to'ldirildi")

    except Exception:
        logger.info("NPS Survey modal - sahifada yo'q, o'tkazib yuborildi")
