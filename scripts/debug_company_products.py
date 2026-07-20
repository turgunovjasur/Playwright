import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _debug_env import add_company_args, configure_company_env

ARCHIVE_DIR = ROOT / "skills/smartup-guide/references/forms/screenshots/company"


def _ancestor_text(locator, level):
    ancestor = locator.locator(f"xpath=ancestor::*[{level}]")
    if ancestor.count() == 0:
        return ""
    try:
        text = ancestor.first.inner_text(timeout=1_000)
    except Exception:
        return ""
    return " ".join(text.split())


def collect_product_switches(page, products_card):
    switches = products_card.get_by_role("switch")
    result = []
    for index in range(switches.count()):
        switch = switches.nth(index)
        box = switch.bounding_box() if switch.is_visible() else None
        result.append(
            {
                "index": index,
                "visible": switch.is_visible(),
                "aria_checked": switch.get_attribute("aria-checked"),
                "box": box,
                "ancestor_texts": [_ancestor_text(switch, level) for level in range(1, 7)],
            }
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    add_company_args(parser)
    parser.add_argument("--code", default="9999")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    configure_company_env(args)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    from tests.smoke.test_setup.test_company import (  # noqa: E402
        _click_trade_product,
        _fill_company_required_fields,
        _open_company_add,
        _open_company_list,
        _products_card,
        _select_required_templates,
        company_code_for,
    )
    from tests.smoke.flows.flow_authorization import authorization  # noqa: E402

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
        _open_company_add(page)
        _fill_company_required_fields(page, args.code, company_code_for(args.code))
        _select_required_templates(page)
        products_card = _products_card(page)
        before = collect_product_switches(page, products_card)
        _click_trade_product(page)
        products_card = _products_card(page)
        after = collect_product_switches(page, products_card)

        screenshot_path = ARCHIVE_DIR / "company__products-after-trade__desktop-1920x1080.png"
        products_card.screenshot(path=str(screenshot_path))

        output = {
            "url": page.url,
            "screenshot": str(screenshot_path),
            "products_text": products_card.inner_text(),
            "before_trade": before,
            "after_trade": after,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
