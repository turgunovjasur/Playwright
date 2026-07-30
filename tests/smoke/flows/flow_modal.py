from playwright.sync_api import expect

# ----------------------------------------------------------------------------------------------------------------------

def fill_nps_survey(page, logger):
    """NPS Survey modal chiqsa - to'ldirib yuboradi"""
    try:
        expect(page.get_by_role("heading", name="NPS Survey")).to_be_visible(timeout=20_000)
        page.get_by_role("button", name="10").click()
        page.get_by_role("button", name="Отправить").click()
        logger.info("NPS Survey modal to'ldirildi")

    except Exception:
        logger.info("NPS Survey modal - sahifada yo'q, o'tkazib yuborildi")

# ----------------------------------------------------------------------------------------------------------------------

def dialog_status(page, timeout=2_000):
    """Dialog status modal chiqsa - to'ldirib yuboradi.
    Modal topilsa True, topilmasa False qaytaradi."""
    try:
        expect(page.get_by_role("dialog", name="Status")).to_be_visible(timeout=timeout)
        page.get_by_role("button", name="Больше не показывать").click()
        return False

    except Exception:
        return True

# ----------------------------------------------------------------------------------------------------------------------
