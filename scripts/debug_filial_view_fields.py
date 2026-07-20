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

ARCHIVE_DIR = ROOT / "skills/smartup-guide/references/forms/screenshots/filial"


def visible_texts(page, selector):
    return page.locator(selector).evaluate_all(
        """(items) => items
            .filter((el) => {
                const rect = el.getBoundingClientRect();
                const style = getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
            })
            .map((el) => (el.textContent || '').trim().replace(/\\s+/g, ' '))
            .filter(Boolean)"""
    )


def collect_view_state(page):
    return {
        "url": page.url,
        "heading_texts": visible_texts(page, "h1, h2, h3, h4, h5, .card-title, .page-title"),
        "tabs": visible_texts(page, "a:visible, button:visible, [role='tab']:visible"),
        "cards": visible_texts(page, ".card:visible, b-card:visible, .form-group:visible"),
        "switches": collect_switches(page),
        "body": page.evaluate("document.body.innerText"),
    }


def collect_switches(page):
    return page.evaluate(
        """() => {
            const visible = (el) => {
                if (!el) return false;
                const rect = el.getBoundingClientRect();
                const style = getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
            };

            const nearestText = (input) => {
                const ancestors = [];
                let node = input.parentElement;
                for (let i = 0; i < 6 && node; i += 1, node = node.parentElement) {
                    ancestors.push(node);
                }
                for (const el of ancestors) {
                    const text = (el.textContent || '').trim().replace(/\\s+/g, ' ');
                    if (text && text.length <= 120) return text;
                }
                return '';
            };

            return Array.from(document.querySelectorAll('input[type="checkbox"], input[type="radio"]'))
                .map((input) => ({
                    text: nearestText(input),
                    type: input.getAttribute('type') || '',
                    ng_model: input.getAttribute('ng-model') || '',
                    checked: Boolean(input.checked),
                    disabled: Boolean(input.disabled),
                    visible: visible(input),
                }))
                .filter((item) => item.visible || item.text || item.ng_model);
        }"""
    )


def click_tab_by_text(page, text):
    tab = page.locator("a:visible, button:visible, [role='tab']:visible").filter(has_text=text).first
    if tab.count() == 0:
        return False
    tab.click()
    BasePage(page).wait_for_loader()
    page.wait_for_timeout(500)
    return True


def screenshot_name_for_tab(tab_name):
    mapping = {
        "Основная информация": "filial__view-main__desktop-1920x1080.png",
        "Продукты": "filial__view-products__desktop-1920x1080.png",
        "Products": "filial__view-products__desktop-1920x1080.png",
    }
    if tab_name in mapping:
        return mapping[tab_name]
    slug = tab_name.lower().replace(" ", "-")
    return f"filial__view-{slug}__desktop-1920x1080.png"


def main():
    parser = argparse.ArgumentParser()
    add_company_args(parser)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    configure_company_env(args)
    data_path = Path("test-results/data/data_store.json")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    filial_name = data["filial_name"]

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

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
        navigate_to(page, tab="Главное", name="Организации")
        expect(page.get_by_role("heading")).to_contain_text("Организации")
        page.get_by_role("searchbox", name="Поиск").fill(filial_name)
        page.get_by_role("searchbox", name="Поиск").press("Enter")
        BasePage(page).wait_for_loader()

        row = page.locator("b-grid .tbl-row").filter(has_text=filial_name).first
        expect(row).to_be_visible()
        row.click()
        page.get_by_role("button", name="Просмотреть", exact=True).click()
        BasePage(page).wait_for_loader()
        expect(page.get_by_role("heading").filter(has_text="Организация")).to_be_visible()

        states = {"initial": collect_view_state(page)}
        page.screenshot(path=str(ARCHIVE_DIR / "filial__view-initial__desktop-1920x1080.png"), full_page=True)

        for tab_name in ("Основная информация", "Продукты", "Products", "Модули", "Настройки"):
            if click_tab_by_text(page, tab_name):
                states[tab_name] = collect_view_state(page)
                page.screenshot(
                    path=str(ARCHIVE_DIR / screenshot_name_for_tab(tab_name)),
                    full_page=True,
                )

        state_path = ARCHIVE_DIR / "filial__view-state.json"
        state_path.write_text(json.dumps(states, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(states, ensure_ascii=False, indent=2))
        print(f"state={state_path}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
