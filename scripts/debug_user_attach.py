import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _debug_env import add_company_args, configure_company_env

ARCHIVE_DIR = ROOT / "skills/smartup-guide/references/forms/screenshots/user"


def checkbox_state(page):
    result = []
    inputs = page.locator("b-grid input[type='checkbox']")
    for index in range(min(inputs.count(), 8)):
        checkbox = inputs.nth(index)
        cell = checkbox.locator(
            "xpath=ancestor::*[contains(@class,'tbl-checkbox-cell') or contains(@class,'tbl-header-cell')][1]"
        )
        label = checkbox.locator("xpath=ancestor::label[1]")
        result.append(
            {
                "index": index,
                "checked": checkbox.is_checked(),
                "visible": checkbox.is_visible(),
                "input_box": checkbox.bounding_box(),
                "input_class": checkbox.get_attribute("class"),
                "bcheckall": checkbox.get_attribute("bcheckall"),
                "cell_visible": cell.first.is_visible() if cell.count() else False,
                "cell_box": cell.first.bounding_box() if cell.count() else None,
                "cell_class": cell.first.get_attribute("class") if cell.count() else None,
                "label_visible": label.first.is_visible() if label.count() else False,
                "label_box": label.first.bounding_box() if label.count() else None,
                "label_class": label.first.get_attribute("class") if label.count() else None,
            }
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    add_company_args(parser)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    configure_company_env(args)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    from tests.smoke.flows.flow_authorization import authorization  # noqa: E402
    from tests.smoke.flows.flow_navigate import navigate_to, switch_filial  # noqa: E402
    from utils.base_page import BasePage  # noqa: E402

    data = json.loads((ROOT / "test-results/data/data_store.json").read_text(encoding="utf-8"))
    code = data["code"]

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

        authorization(page, who="admin")
        switch_filial(page, name=f"filial-pw{code}")
        navigate_to(page, tab="Главное", name="Пользователи")
        expect(page.get_by_role("heading")).to_contain_text("Пользователи")
        page.get_by_text(f"natural_person-pw{code}").first.click()
        page.get_by_role("button", name="Просмотреть").click()
        expect(page.get_by_text(f"natural_person-pw{code}").first).to_be_visible()
        page.get_by_role("link", name=" Формы").click()
        page.get_by_role("tab", name="Формы").click()
        page.get_by_role("button", name="Доступные").click()
        page.get_by_role("button", name=" 50 /").click()
        page.get_by_role("link", name="1000").click()
        BasePage(page).wait_for_loader()

        screenshot_path = ARCHIVE_DIR / "user__attach-forms-available__desktop-1920x1080.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        before = checkbox_state(page)
        BasePage(page).grid(checkbox="all")
        after = checkbox_state(page)
        print(
            json.dumps(
                {"screenshot": str(screenshot_path), "before": before, "after": after},
                ensure_ascii=False,
                indent=2,
            )
        )

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
