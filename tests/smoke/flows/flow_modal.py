from playwright.sync_api import Page, expect

def fill_nps_survey(page: Page, logger):
    """NPS Survey modal chiqsa - to'ldirib yuboradi"""
    try:
        expect(page.get_by_role("heading", name="NPS Survey")).to_be_visible(timeout=20_000)
        page.get_by_role("button", name="10").click()
        page.get_by_role("button", name="Отправить").click()
        logger.info("NPS Survey modal to'ldirildi")
    except Exception:
        logger.info("NPS Survey modal - sahifada yo'q, o'tkazib yuborildi")