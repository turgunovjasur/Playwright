import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _debug_env import add_company_args, configure_company_env
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_navigate import navigate_to
from utils.base_page import BasePage


ARCHIVE_DIR = ROOT / "skills/smartup-guide/references/forms/screenshots/legal-person"
SCREENSHOT_SETTLE_INTERVAL = 500


def sanitize(value):
    return (
        value.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("\\", "-")
        .replace("(", "")
        .replace(")", "")
    )


def save_state(page, name, states):
    screenshot = ARCHIVE_DIR / f"legal-person__{name}__desktop-1920x1080.png"
    page.screenshot(path=str(screenshot), full_page=True)
    states[name] = {
        "url": page.url,
        "screenshot": str(screenshot.relative_to(ROOT / "skills/smartup-guide")),
        "body": page.evaluate("document.body.innerText"),
    }


def click_tab(page, name):
    page.locator("a:visible").filter(has_text=name).first.click()
    BasePage(page).wait_for_loader()
    page.wait_for_timeout(SCREENSHOT_SETTLE_INTERVAL)


def main():
    parser = argparse.ArgumentParser()
    add_company_args(parser)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    configure_company_env(args)
    data = json.loads((ROOT / "test-results/data/data_store.json").read_text(encoding="utf-8"))
    code = data["legal_person_code"]

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    states = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=args.headless,
            args=[] if args.headless else ["--start-maximized"],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080} if args.headless else None,
            no_viewport=not args.headless,
        )
        context.set_default_timeout(10_000)
        page = context.new_page()

        authorization(page, who="admin")
        navigate_to(page, tab="Справочники", name="Юридические лица")
        expect(page.get_by_role("heading")).to_contain_text("Юридические лица")

        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Юридическое лицо (создание)")
        save_state(page, "add-main-empty", states)

        navigate_to(page, tab="Справочники", name="Юридические лица")
        expect(page.get_by_role("heading")).to_contain_text("Юридические лица")
        page.get_by_role("searchbox", name="Поиск").fill(code)
        page.get_by_role("searchbox", name="Поиск").press("Enter")
        BasePage(page).wait_for_loader()
        row = page.locator("b-grid .tbl-row").filter(has_text=code).first
        expect(row).to_be_visible()
        row.click()
        page.get_by_role("button", name="Просмотреть", exact=True).click()
        BasePage(page).wait_for_loader()
        expect(page.get_by_role("heading").filter(has_text="Юридическое лицо (просмотр)").first).to_be_visible()

        for tab_name in (
            "Основная информация",
            "Дополнительная информация",
            "Расчетный счет",
            "Контактные лица",
        ):
            click_tab(page, tab_name)
            save_state(page, f"view-{sanitize(tab_name)}", states)

        state_path = ARCHIVE_DIR / "legal-person__view-state.json"
        state_path.write_text(json.dumps(states, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(states, ensure_ascii=False, indent=2))
        print(f"state={state_path}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
