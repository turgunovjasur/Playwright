from playwright.sync_api import expect


def dialog_status(page, timeout=2_000):
    """Dialog status modal chiqsa - to'ldirib yuboradi.
    Modal topilsa True, topilmasa False qaytaradi."""
    try:
        expect(page.get_by_role("dialog", name="Status")).to_be_visible(timeout=timeout)
        page.get_by_role("button", name="Больше не показывать").click()
        return False

    except Exception:
        return True
