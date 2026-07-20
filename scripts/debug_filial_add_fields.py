import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _debug_env import add_company_args, configure_company_env
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.flows.flow_navigate import navigate_to

ARCHIVE_DIR = ROOT / "skills/smartup-guide/references/forms/screenshots/filial"


def collect_fields(page):
    return page.evaluate(
        """() => {
            const isVisible = (el) => {
                if (!el || el.offsetParent === null) return false;
                const style = getComputedStyle(el);
                return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
            };

            const fieldLabel = (el) => {
                const id = el.getAttribute('id');
                if (id) {
                    const label = document.querySelector(`label[for="${id}"]`);
                    if (label && label.textContent.trim()) return label.textContent.trim();
                }

                const group = el.closest('.form-group') || el.closest('.col-') || el.closest('.form-row');
                if (group) {
                    const labels = group.querySelectorAll('label, .form-label, .b-label');
                    for (const label of labels) {
                        const text = (label.textContent || '').trim();
                        if (text) return text;
                    }
                }

                return (el.getAttribute('placeholder') || '').trim();
            };

            return Array.from(document.querySelectorAll('input, textarea, select'))
                .filter((el) => {
                    if (!isVisible(el)) return false;
                    if (el.type === 'hidden' || el.type === 'file') return false;
                    return true;
                })
                .map((el) => ({
                    label: fieldLabel(el).replace(/\\*/g, '').trim(),
                    tag: el.tagName.toLowerCase(),
                    type: el.getAttribute('type') || '',
                    placeholder: el.getAttribute('placeholder') || '',
                    ng_model: el.getAttribute('ng-model') || '',
                    value: el.value || '',
                    checked: Boolean(el.checked),
                    readonly: Boolean(el.readOnly),
                    disabled: Boolean(el.disabled),
                }))
                .filter((field) => field.label || field.placeholder || field.ng_model);
        }"""
    )


def collect_switches(page):
    return page.evaluate(
        """() => {
            const isVisible = (el) => {
                if (!el) return false;
                const rect = el.getBoundingClientRect();
                const style = getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
            };

            const labelFor = (input) => {
                const group = input.closest('.form-group') || input.closest('.col-') || input.closest('.form-row') || input.parentElement;
                if (!group) return '';
                const directLabels = group.querySelectorAll('label, .form-label, .b-label');
                for (const label of directLabels) {
                    const text = (label.textContent || '').trim();
                    if (text && !text.includes('Да') && !text.includes('Нет')) return text;
                }
                return (group.textContent || '').trim().replace(/\\s+/g, ' ');
            };

            return Array.from(document.querySelectorAll('input[type="checkbox"], input[type="radio"]'))
                .map((input) => {
                    const group = input.closest('.form-group') || input.closest('.col-') || input.closest('.form-row') || input.parentElement;
                    return {
                        label: labelFor(input),
                        type: input.getAttribute('type') || '',
                        ng_model: input.getAttribute('ng-model') || '',
                        checked: Boolean(input.checked),
                        disabled: Boolean(input.disabled),
                        visible: isVisible(input),
                        group_text: group ? (group.textContent || '').trim().replace(/\\s+/g, ' ') : '',
                    };
                })
                .filter((item) => item.label || item.ng_model || item.group_text);
        }"""
    )


def set_checkbox(page, ng_model, checked):
    checkbox = page.locator(f'input[ng-model="{ng_model}"]').first
    if checkbox.count() == 0:
        return
    if checkbox.is_checked() != checked:
        checkbox.evaluate("el => el.click()")
    page.wait_for_timeout(300)


def collect_b_input_options(page):
    result = []
    b_inputs = page.locator("b-input").all()
    for index, b_input in enumerate(b_inputs):
        search = b_input.get_by_placeholder("Поиск").first
        if search.count() == 0 or not search.is_visible():
            continue

        label = b_input.evaluate(
            """(el) => {
                const group = el.closest('.form-group') || el.closest('.col-') || el.closest('.form-row');
                if (!group) return '';
                const label = group.querySelector('label, .form-label, .b-label');
                return label && label.textContent ? label.textContent.trim().replace(/\\*/g, '') : '';
            }"""
        )
        page.keyboard.press("Escape")
        search.click(force=True)
        page.wait_for_timeout(300)
        options = b_input.locator("div.hint:visible").evaluate_all(
            """(items) => items
                .map((item) => (item.textContent || '').trim())
                .filter(Boolean)
                .slice(0, 20)"""
        )
        result.append({"index": index, "label": label, "options": options})
        page.keyboard.press("Escape")

    return result


def collect_timezone_search_options(page, query):
    return collect_b_input_search_options(page, "d.timezone_name", query)


def collect_b_input_search_options(page, ng_model, query):
    b_input = page.locator(f'b-input:has(input[ng-model="{ng_model}"])').first
    search = b_input.get_by_placeholder("Поиск").first
    page.keyboard.press("Escape")
    search.click(force=True)
    search.fill(query)
    page.wait_for_timeout(500)
    options = b_input.locator("div.hint:visible").evaluate_all(
        """(items) => items
            .map((item) => (item.textContent || '').trim())
            .filter(Boolean)
            .slice(0, 20)"""
    )
    page.keyboard.press("Escape")
    return options


def main():
    parser = argparse.ArgumentParser()
    add_company_args(parser)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    configure_company_env(args)
    data_path = Path("test-results/data/data_store.json")
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {}
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
        page.get_by_role("button", name="Создать").click()
        expect(page.get_by_role("heading")).to_contain_text("Организация (создание)")

        fields = collect_fields(page)
        switches = collect_switches(page)
        set_checkbox(page, "d.vat_enabled", True)
        set_checkbox(page, "d.excise_enabled", True)
        fields_after_switches = collect_fields(page)
        switches_after_switches = collect_switches(page)
        options = collect_b_input_options(page)
        timezone_options = collect_timezone_search_options(page, "Ташкент")
        legal_query = data.get("legal_person_code", "")
        legal_options = collect_b_input_search_options(page, "d.person_name", legal_query) if legal_query else []
        screenshot_path = ARCHIVE_DIR / "filial__add-default__desktop-1920x1080.png"
        fields_path = ARCHIVE_DIR / "filial__add-fields.json"
        options_path = ARCHIVE_DIR / "filial__add-b-input-options.json"
        switches_path = ARCHIVE_DIR / "filial__add-switches.json"
        fields_after_switches_path = ARCHIVE_DIR / "filial__add-fields-after-switches.json"
        switches_after_switches_path = ARCHIVE_DIR / "filial__add-switches-after-switches.json"
        timezone_path = ARCHIVE_DIR / "filial__add-timezone-search.json"
        legal_path = ARCHIVE_DIR / "filial__add-legal-person-search.json"

        page.screenshot(path=str(screenshot_path), full_page=True)
        fields_path.write_text(json.dumps(fields, ensure_ascii=False, indent=2), encoding="utf-8")
        switches_path.write_text(json.dumps(switches, ensure_ascii=False, indent=2), encoding="utf-8")
        fields_after_switches_path.write_text(json.dumps(fields_after_switches, ensure_ascii=False, indent=2), encoding="utf-8")
        switches_after_switches_path.write_text(json.dumps(switches_after_switches, ensure_ascii=False, indent=2), encoding="utf-8")
        options_path.write_text(json.dumps(options, ensure_ascii=False, indent=2), encoding="utf-8")
        timezone_path.write_text(json.dumps(timezone_options, ensure_ascii=False, indent=2), encoding="utf-8")
        legal_path.write_text(json.dumps(legal_options, ensure_ascii=False, indent=2), encoding="utf-8")

        print(json.dumps(fields, ensure_ascii=False, indent=2))
        print("switches=")
        print(json.dumps(switches, ensure_ascii=False, indent=2))
        print("fields-after-switches=")
        print(json.dumps(fields_after_switches, ensure_ascii=False, indent=2))
        print("switches-after-switches=")
        print(json.dumps(switches_after_switches, ensure_ascii=False, indent=2))
        print("b-input-options=")
        print(json.dumps(options, ensure_ascii=False, indent=2))
        print("timezone-search-options=")
        print(json.dumps(timezone_options, ensure_ascii=False, indent=2))
        print("legal-person-search-options=")
        print(json.dumps(legal_options, ensure_ascii=False, indent=2))
        print(f"screenshot={screenshot_path}")
        print(f"fields={fields_path}")
        print(f"switches={switches_path}")
        print(f"fields_after_switches={fields_after_switches_path}")
        print(f"switches_after_switches={switches_after_switches_path}")
        print(f"options={options_path}")
        print(f"timezone={timezone_path}")
        print(f"legal_person={legal_path}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
