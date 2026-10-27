"""Report group uchun umumiy route va download helperlari."""

from pathlib import Path
import xml.etree.ElementTree as ET

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

DOWNLOAD_DIR = Path("test-results/downloads")
REPORT_DOWNLOAD_TIMEOUT = 240_000


# ----------------------------------------------------------------------------------------------------------------------

def open_report(base, route, heading=None, timeout=60_000):
    """Menyuda yo'q integration reportni umumiy route API orqali ochadi."""
    base.open_route(f"trade/rep/integration/{route}", heading=heading, timeout=timeout)


# ----------------------------------------------------------------------------------------------------------------------

def generate_and_verify_download(base, button_name, expected_prefix, save_name, timeout=REPORT_DOWNLOAD_TIMEOUT, expected_suffix=None):
    """Download nomi, hajmi va XML bo'lsa haqiqiy XML kontentini tekshiradi."""
    if expected_prefix is None and expected_suffix is None:
        raise ValueError("Download uchun expected_prefix yoki expected_suffix berilishi kerak")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with base.page.expect_download(timeout=timeout) as download_info:
            base.click(name=button_name, exact=True, timeout=timeout)
    except PlaywrightTimeoutError as exc:
        alerts = base.page.locator("#biruniAlert:visible, #biruniAlertExtended:visible")
        allure.attach(base.page.url, name=f"{save_name}-url", attachment_type=allure.attachment_type.TEXT)
        allure.attach("\n".join(alerts.all_inner_texts()), name=f"{save_name}-alerts", attachment_type=allure.attachment_type.TEXT)
        allure.attach(base.page.screenshot(full_page=True), name=f"{save_name}-timeout", attachment_type=allure.attachment_type.PNG)
        raise AssertionError(f"{save_name} download {timeout} ms ichida boshlanmadi") from exc
    download = download_info.value

    failure = download.failure()
    if failure:
        raise AssertionError(f"{save_name} download xato bilan tugadi: {failure}")

    suggested = download.suggested_filename
    allure.attach(suggested, name=f"{save_name}-filename", attachment_type=allure.attachment_type.TEXT)
    if expected_prefix is not None and not suggested.startswith(expected_prefix):
        raise AssertionError(f"Kutilmagan fayl nomi: {suggested} (kutilgan prefiks: {expected_prefix})")
    if expected_suffix is not None and not suggested.lower().endswith(expected_suffix.lower()):
        raise AssertionError(f"Kutilmagan fayl nomi: {suggested} (kutilgan suffix: {expected_suffix})")

    target = DOWNLOAD_DIR / save_name
    download.save_as(str(target))
    size = target.stat().st_size
    allure.attach(str(size), name=f"{save_name}-size", attachment_type=allure.attachment_type.TEXT)
    if size <= 0:
        raise AssertionError(f"{save_name} bo'sh (0 bytes)")
    if expected_suffix is not None and expected_suffix.lower() == ".xml":
        try:
            xml_root = ET.parse(target).getroot().tag
        except ET.ParseError as exc:
            raise AssertionError(f"{save_name}: yuklangan fayl yaroqli XML emas") from exc
        allure.attach(xml_root, name=f"{save_name}-xml-root", attachment_type=allure.attachment_type.TEXT)
        if xml_root.rsplit("}", 1)[-1].lower() == "html":
            raise AssertionError(
                f"{save_name}: XML o'rniga HTML sahifa yuklandi; "
                "integratsiya endpointi va server javobini tekshiring"
            )
    return suggested
