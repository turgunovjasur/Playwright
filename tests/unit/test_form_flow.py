import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests.smoke.test_forms import flow as form_flow
from tests.smoke.test_forms.flow import (
    build_form_result,
    canonical_form_path,
    finish_form_results,
    form_navigation_track,
    form_step_title,
    format_form_result,
)
from tests.smoke.test_forms.test_spravochniki_menu_forms import (
    ADMIN_DIRECT_FORMS,
    ADMIN_HIDDEN_FORMS,
    ADMIN_PAGE_LINK_FORMS,
    OPERATIONAL_DIRECT_FORMS,
    OPERATIONAL_HIDDEN_FORMS,
    OPERATIONAL_PAGE_LINK_FORMS,
)


def test_canonical_form_path_supports_legacy_and_a2_urls():
    assert (
        canonical_form_path(
            "https://app3.greenwhite.uz/xtrade/#/!abc/anor/mcg/mml_dashboard"
        )
        == "anor/mcg/mml_dashboard"
    )
    assert (
        canonical_form_path(
            "https://app3.greenwhite.uz/xtrade/a2/anor/rep/mbi/mcg/action"
        )
        == "anor/rep/mbi/mcg/action"
    )


def test_form_navigation_track_includes_menu_action_and_page_links():
    assert form_navigation_track(
        navbar_tab="Справочники",
        menu_column="Справочники",
        menu_item="Цены",
        action="Импорт",
        page_links=["Типы оплат"],
    ) == (
        "Справочники → Справочники → Цены → "
        "Создать dropdown → Импорт → Типы оплат"
    )


def test_form_report_contains_user_visible_context_and_urls():
    result = build_form_result(
        number=7,
        filial="filial-pw{code}",
        navbar_tab="Главное",
        menu_column="Дополнительное",
        menu_item="Клиенты OAuth2 сервера для компании",
        title="Клиенты OAuth2 сервера для компании",
        expected_path="biruni/kauth/company_client_list",
        actual_url="https://smartup.online/a2/biruni/kauth/company_client_list",
        ok=True,
    )

    assert form_step_title(
        number=7,
        filial=result["filial"],
        navbar_tab=result["navbar_tab"],
        menu_column=result["menu_column"],
        title=result["title"],
    ) == (
        "007 | Filial: filial-pw{code} | "
        "Forma: Клиенты OAuth2 сервера для компании | "
        "Tab: Главное | Menu: Дополнительное"
    )

    report = format_form_result(result)
    assert "Filial             : filial-pw{code}" in report
    assert "Tab                : Главное" in report
    assert "Menu               : Дополнительное" in report
    assert "Menyu formasi      : Клиенты OAuth2 сервера для компании" in report
    assert "Kutilgan URL       : biruni/kauth/company_client_list" in report
    assert (
        "Haqiqiy URL        : "
        "https://smartup.online/a2/biruni/kauth/company_client_list"
    ) in report


def test_finish_form_results_writes_summary_to_pytest_terminal(monkeypatch):
    result = build_form_result(
        number=1,
        filial="Администрирование",
        navbar_tab="Главное",
        menu_column="Дополнительное",
        menu_item="Клиенты OAuth2 сервера для компании",
        title="Клиенты OAuth2 сервера для компании",
        expected_path="biruni/kauth/company_client_list",
        actual_url="https://smartup.online/a2/biruni/kauth/company_client_list",
        ok=True,
    )
    class TerminalReporter:
        pass

    monkeypatch.setattr(form_flow.allure, "attach", lambda *args, **kwargs: None)

    terminal_reporter = TerminalReporter()
    finish_form_results([result], terminal_reporter=terminal_reporter)

    output = terminal_reporter._smartup_forms_reports[0]
    assert "FORMA OCHILISH HISOBOTI" in output
    assert "Filial: Администрирование" in output
    assert "Tab: Главное" in output
    assert "Menu: Дополнительное" in output
    assert "Menyu formasi: Клиенты OAuth2 сервера для компании" in output
    assert "Forma: Клиенты OAuth2 сервера для компании" in output
    assert (
        "Yo'l: Главное → Дополнительное → "
        "Клиенты OAuth2 сервера для компании"
    ) in output
    assert "Kutilgan URL: biruni/kauth/company_client_list" in output
    assert (
        "Haqiqiy URL: "
        "https://smartup.online/a2/biruni/kauth/company_client_list"
    ) in output


def test_spravochniki_inventory_contains_100_navigation_cases():
    inventories = (
        OPERATIONAL_DIRECT_FORMS,
        OPERATIONAL_PAGE_LINK_FORMS,
        OPERATIONAL_HIDDEN_FORMS,
        ADMIN_DIRECT_FORMS,
        ADMIN_PAGE_LINK_FORMS,
        ADMIN_HIDDEN_FORMS,
    )

    assert [len(items) for items in inventories] == [36, 44, 14, 1, 2, 3]
    assert sum(len(items) for items in inventories) == 100


def test_group_session_page_does_not_require_code_fixture():
    conftest_path = ROOT / "tests" / "smoke" / "conftest.py"
    module = ast.parse(conftest_path.read_text(encoding="utf-8"))
    fixture = next(
        node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "group_session_page"
    )

    assert [argument.arg for argument in fixture.args.args] == [
        "session_browser",
        "request",
    ]
