import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _debug_env import add_company_args, configure_company_env

ARCHIVE_DIR = ROOT / "skills/smartup-guide/references/forms/screenshots/company"
DEBUG_TEXT_TIMEOUT = 1_000


def visible_texts(locator, limit=50):
    result = []
    for index in range(min(locator.count(), limit)):
        item = locator.nth(index)
        if not item.is_visible():
            continue
        text = " ".join(item.inner_text(timeout=DEBUG_TEXT_TIMEOUT).split())
        if text:
            result.append(text)
    return result


def click_visible_text_button(page, text):
    buttons = page.get_by_role("button")
    for index in range(buttons.count()):
        button = buttons.nth(index)
        if not button.is_visible():
            continue
        button_text = " ".join(button.inner_text(timeout=DEBUG_TEXT_TIMEOUT).split())
        if text.lower() in button_text.lower():
            button.click()
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    add_company_args(parser)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()

    configure_company_env(args)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    from tests.smoke.test_setup.test_00_company import (  # noqa: E402
        COMPANY_SAVE_TIMEOUT,
        _company_code_text_pattern,
        _open_company_list,
    )
    from tests.smoke.flows.flow_authorization import authorization  # noqa: E402
    from utils.base_page import BasePage  # noqa: E402

    data = json.loads((ROOT / "test-results/data/data_store.json").read_text(encoding="utf-8"))
    company_code = data["company_code"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=args.headless,
            args=[] if args.headless else ["--start-maximized"],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080} if args.headless else None,
            no_viewport=not args.headless,
        )
        context.set_default_timeout(15_000)
        page = context.new_page()

        authorization(page, who="head")
        _open_company_list(page)
        search = page.get_by_role("searchbox", name="Поиск")
        search.fill(company_code)
        search.press("Enter")
        BasePage(page).wait_for_loader()
        row = page.locator("b-grid .tbl-row").filter(has_text=_company_code_text_pattern(company_code)).first
        if row.count() == 0:
            row = page.get_by_text(_company_code_text_pattern(company_code)).first
        expect(row).to_be_visible()
        row_text = " ".join(row.inner_text().split())
        row.click()
        if click_visible_text_button(page, "Просмотреть"):
            BasePage(page).wait_for_loader()
        elif click_visible_text_button(page, "Изменить"):
            BasePage(page).wait_for_loader()

        screenshot_path = ARCHIVE_DIR / "company__view-selected__desktop-1920x1080.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        activation_tab = page.get_by_text("Активация для лицензии", exact=True).first
        if activation_tab.count() > 0 and activation_tab.is_visible():
            activation_tab.click()
            BasePage(page).wait_for_loader()
            screenshot_path = ARCHIVE_DIR / "company__license-activation__desktop-1920x1080.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
        output = {
            "url": page.url,
            "company_code": company_code,
            "screenshot": str(screenshot_path),
            "row_text": row_text,
            "buttons": visible_texts(page.get_by_role("button")),
            "links": visible_texts(page.get_by_role("link"), limit=80),
            "body": page.locator("body").inner_text(),
        }

        if args.activate:
            for name in ("Активация", "Активировать", "Activate", "Включить"):
                button = page.get_by_role("button", name=name, exact=True)
                if button.count() > 0 and button.first.is_visible():
                    button.first.click()
                    BasePage(page).confirm_biruni()
                    BasePage(page).wait_for_loader(timeout=COMPANY_SAVE_TIMEOUT)
                    output["activated_by"] = name
                    output["after_body"] = page.locator("body").inner_text()
                    break

        print(json.dumps(output, ensure_ascii=False, indent=2))

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
