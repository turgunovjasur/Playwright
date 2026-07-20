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


def collect_b_inputs(page):
    result = []
    b_inputs = page.locator("b-input")
    for index in range(b_inputs.count()):
        b_input = b_inputs.nth(index)
        inputs = []
        for input_index in range(b_input.locator("input").count()):
            field = b_input.locator("input").nth(input_index)
            inputs.append(
                {
                    "index": input_index,
                    "visible": field.is_visible(),
                    "placeholder": field.get_attribute("placeholder"),
                    "ng_model": field.get_attribute("ng-model"),
                    "value": field.input_value() if field.is_visible() else "",
                }
            )
        result.append(
            {
                "index": index,
                "visible": b_input.is_visible(),
                "text": " ".join(b_input.inner_text(timeout=1_000).split()),
                "inputs": inputs,
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

    from tests.smoke.flows.flow_authorization import USER_PASS, authorization  # noqa: E402
    from tests.smoke.flows.flow_navigate import navigate_to, switch_filial  # noqa: E402

    data_path = ROOT / "test-results/data/data_store.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
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
        switch_filial(page, name=data["filial_name"])
        navigate_to(page, tab="Главное", name="Пользователи")
        expect(page.get_by_role("heading")).to_contain_text("Пользователи")
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Пользователь (создание)")
        page.get_by_role("textbox").nth(2).fill(f"user-pw{code}")
        page.locator("#new_password").fill(USER_PASS)
        page.locator("#new_password").press("Tab")

        screenshot_path = ARCHIVE_DIR / "user__add-after-password__desktop-1920x1080.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        output = {
            "url": page.url,
            "screenshot": str(screenshot_path),
            "b_inputs": collect_b_inputs(page),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
