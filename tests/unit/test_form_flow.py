import ast
import inspect
import json
import sys
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests.smoke.smoke_reporting import safe_page_screenshot
from tests.smoke.test_forms import form_monitor
from tests.smoke.test_forms.flow import (
    _select_operational_filial,
    build_form_result,
    canonical_form_path,
    form_navigation_track,
    form_step_title,
    format_form_result,
    run_form_cases,
)
from tests.smoke.test_forms.form_monitor import (
    NOT_CHECKED,
    NOT_OPENED,
    OPENED_WITH_DEFECT,
    PASSED,
    TEST_BLOCKED,
    FormMonitor,
    build_form_case_plan,
    build_monitor_payload,
    capture_form_state,
    classify_form_failure,
    form_case,
    render_monitor_summary,
)
from tests.smoke.test_forms.test_01_spravochniki_menu_forms import (
    ADMIN_DIRECT_FORMS,
    ADMIN_HIDDEN_FORMS,
    ADMIN_PAGE_LINK_FORMS,
    OPERATIONAL_DIRECT_FORMS,
    OPERATIONAL_HIDDEN_FORMS,
    OPERATIONAL_PAGE_LINK_FORMS,
)


class FakeLocator:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    @property
    def first(self):
        return self

    def filter(self, **kwargs):
        return self

    def locator(self, selector):
        return FakeLocator(self.page, f"{self.selector} {selector}")

    def is_visible(self, timeout=None):
        return self.selector in self.page.visible_selectors

    def inner_text(self, timeout=None):
        if self.selector in self.page.inner_text_errors:
            raise PlaywrightError("inner_text failed")
        return self.page.text_by_selector.get(self.selector, "")

    def all_inner_texts(self):
        value = self.page.text_by_selector.get(self.selector, [])
        if isinstance(value, list):
            return value
        return [value] if value else []


class FakePage:
    def __init__(
        self,
        *,
        url="https://smartup.online/#/dashboard",
        title="Главное",
        visible_selectors=None,
        text_by_selector=None,
        inner_text_errors=None,
    ):
        self.url = url
        self.current_title = title
        self.visible_selectors = set(visible_selectors or [])
        self.text_by_selector = dict(text_by_selector or {})
        self.inner_text_errors = set(inner_text_errors or [])
        self.screenshot_kwargs = None

    def title(self):
        return self.current_title

    def locator(self, selector):
        return FakeLocator(self, selector)

    def get_by_role(self, role, **kwargs):
        return FakeLocator(self, f"role={role}")

    def screenshot(self, **kwargs):
        self.screenshot_kwargs = kwargs
        return b"png"


class TerminalReporter:
    def __init__(self):
        self.lines = []

    def write_line(self, line):
        self.lines.append(line)


def _a2_page(path, title, *, content="Forma kontenti"):
    return FakePage(
        url=f"https://smartup.online/a2/{path}",
        title=title,
        visible_selectors={"main"},
        text_by_selector={"main": content},
    )


def _case(number=1, *, path="trade/tvt/visit_list", title="Визиты", ready=None):
    return form_case(
        number=number,
        filial="filial-pw{code}",
        navbar_tab="Продажа",
        menu_column="Визиты",
        menu_item=title,
        title=title,
        expected_path=path,
        ready=ready,
        shell="a2",
    )


def _silence_allure(monkeypatch):
    monkeypatch.setattr(form_monitor.allure, "attach", lambda *args, **kwargs: None)


def test_canonical_form_path_supports_legacy_and_a2_urls():
    assert canonical_form_path(
        "https://app3.greenwhite.uz/xtrade/#/!abc/anor/mcg/mml_dashboard"
    ) == "anor/mcg/mml_dashboard"
    assert canonical_form_path(
        "https://app3.greenwhite.uz/xtrade/a2/anor/rep/mbi/mcg/action"
    ) == "anor/rep/mbi/mcg/action"


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


def test_operational_filial_is_required_for_form_tests():
    assert _select_operational_filial(
        ["Администрирование", "filial-pw{code}"]
    ) == "filial-pw{code}"

    with pytest.raises(AssertionError, match="operatsion filial topilmadi"):
        _select_operational_filial(["Администрирование", "  "])


def test_form_report_contains_user_visible_context_and_explicit_state():
    result = build_form_result(
        number=7,
        filial="filial-pw{code}",
        navbar_tab="Главное",
        menu_column="Дополнительное",
        menu_item="Клиенты OAuth2 сервера для компании",
        title="Клиенты OAuth2 сервера для компании",
        expected_path="biruni/kauth/company_client_list",
        actual_url="https://smartup.online/a2/biruni/kauth/company_client_list",
        ok=False,
        status=OPENED_WITH_DEFECT,
        reason_code="TITLE_MISMATCH",
        reason_summary="Title mos emas",
        test_started=True,
        test_completed=True,
        page_reached=True,
        validation_completed=True,
        validation_passed=False,
        usable=True,
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
    assert "Target URLga yetdimi: HA" in report
    assert "Validatsiya bajarildimi: HA" in report
    assert "Validatsiyadan o'tdimi: YOQ" in report
    assert "Foydalanishga tayyormi: HA" in report
    assert "Forma ochildimi" not in report


def test_build_form_case_plan_is_the_single_title_and_path_normalizer():
    planned = build_form_case_plan(
        [
            {
                "menu_column": "Маркетинг",
                "menu_item": "Акции",
                "page_links": ["Конструктор отчетов по акциям"],
                "path": "anor/rep/mbi/mcg/action",
            }
        ],
        start_number=57,
        filial="filial-pw{code}",
        navbar_tab="Справочники",
        shell="a2",
        section="page-link",
    )

    assert planned == [
        {
            "number": 57,
            "filial": "filial-pw{code}",
            "navbar_tab": "Справочники",
            "menu_column": "Маркетинг",
            "menu_item": "Акции",
            "title": "Конструктор отчетов по акциям",
            "expected_path": "anor/rep/mbi/mcg/action",
            "page_links": ["Конструктор отчетов по акциям"],
            "action": None,
            "add_icon": False,
            "ready": None,
            "shell": "a2",
            "section": "page-link",
            "allowed_warnings": [],
        }
    ]


def test_spravochniki_inventory_contains_100_navigation_definitions():
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


def test_authorization_is_monitored_inside_each_forms_suite():
    runner_source = (ROOT / "tests/smoke/test_forms/test_0_forms_runner.py").read_text(
        encoding="utf-8"
    )
    forms_01_source = (
        ROOT / "tests/smoke/test_forms/test_01_spravochniki_menu_forms.py"
    ).read_text(encoding="utf-8")
    forms_02_source = (
        ROOT / "tests/smoke/test_forms/test_02_a2_admin_menu_forms.py"
    ).read_text(encoding="utf-8")

    assert "forms_admin_page" not in runner_source
    assert 'monitor.precondition(\n        "Admin avtorizatsiyasi"' in forms_01_source
    assert 'monitor.precondition(\n        "Admin avtorizatsiyasi"' in forms_02_source


def test_form_monitor_classifies_loaded_page_with_wrong_title_as_defect():
    analysis = classify_form_failure(
        case={
            "expected_path": "anor/rep/mbi/mcg/action",
            "title": "Конструктор отчетов по акциям",
        },
        stage="validation",
        detail="Page title expected; to_have_title failed",
        state={
            "canonical_path": "anor/rep/mbi/mcg/action",
            "actual_title": "Заголовок",
            "content_ready": True,
            "visible_error": "",
            "loader_visible": False,
        },
    )
    assert analysis["status"] == OPENED_WITH_DEFECT
    assert analysis["reason_code"] == "TITLE_MISMATCH"
    assert analysis["opened"] is True


def test_loader_has_priority_over_title_mismatch():
    analysis = classify_form_failure(
        case={"expected_path": "trade/tvt/visit_list", "title": "Визиты"},
        stage="validation",
        detail="to_have_title failed",
        state={
            "canonical_path": "trade/tvt/visit_list",
            "actual_title": "Smartup Online",
            "content_ready": True,
            "visible_error": "",
            "loader_visible": True,
        },
    )
    assert analysis["status"] == NOT_OPENED
    assert analysis["reason_code"] == "LOADER_NOT_FINISHED"


def test_application_error_on_target_url_is_opened_with_defect():
    analysis = classify_form_failure(
        case={"expected_path": "trade/tvt/visit_list", "title": "Визиты"},
        stage="validation",
        detail="UI error",
        state={
            "canonical_path": "trade/tvt/visit_list",
            "actual_title": "Визиты",
            "content_ready": True,
            "visible_error": "Нет доступа к форме",
            "loader_visible": False,
        },
    )
    assert analysis["status"] == OPENED_WITH_DEFECT
    assert analysis["reason_code"] == "APPLICATION_ERROR"
    assert analysis["opened"] is True


def test_generic_dialog_is_not_classified_as_application_error():
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    page.visible_selectors.add("[role='dialog']:visible")
    page.text_by_selector["[role='dialog']:visible"] = "Oddiy tasdiqlash oynasi"

    state = capture_form_state(page)

    assert state["visible_error"] == ""
    assert state["content_ready"] is True


def test_inner_text_error_does_not_turn_blank_main_into_ready_content():
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    page.inner_text_errors.add("main")

    state = capture_form_state(page)

    assert state["content_ready"] is False


def test_legacy_monitor_uses_visible_heading_instead_of_document_title(monkeypatch):
    _silence_allure(monkeypatch)
    page = FakePage(
        url="https://smartup.online/#/!token/anor/mr/region_list",
        title="Регионы",
        visible_selectors={"b-page:visible"},
        text_by_selector={"role=heading": ["Страны"]},
    )
    case = form_case(
        number=10,
        filial="filial-pw{code}",
        navbar_tab="Справочники",
        menu_column="Справочники",
        menu_item="Регионы",
        title="Страны",
        expected_path="anor/mr/region_list",
        shell="legacy",
    )
    monitor = FormMonitor(page, suite_name="Forms-01", planned_cases=[case])

    result = monitor.run_case(case, navigate=lambda: None, validate=lambda: None)

    assert result["status"] == PASSED
    assert result["actual_title"] == "Страны"
    assert result["checks"]["title_source"] == "visible_heading"
    assert result["checks"]["document_title"] == "Регионы"


def test_monitor_prevents_false_pass_when_validate_returns_on_blank_form(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/tvt/visit_list", "Визиты", content="")
    case = _case()
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=[case])

    result = monitor.run_case(case, navigate=lambda: None, validate=lambda: None)

    assert result["status"] == NOT_OPENED
    assert result["reason_code"] == "CONTENT_NOT_READY"
    assert result["page_reached"] is True
    assert result["validation_completed"] is True
    assert result["validation_passed"] is False
    assert result["usable"] is False


def test_monitor_continues_after_expected_form_failure(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/intro/dashboard", "Главное")
    cases = [
        _case(1),
        _case(
            2,
            path="trade/tvt/user_locations",
            title="Отслеживание пользователей",
        ),
    ]
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=cases)

    monitor.run_case(
        cases[0],
        navigate=lambda: (_ for _ in ()).throw(AssertionError("menu topilmadi")),
        validate=lambda: None,
    )

    def open_second_form():
        page.url = "https://smartup.online/a2/trade/tvt/user_locations"
        page.current_title = "Отслеживание пользователей"
        page.visible_selectors = {"main"}
        page.text_by_selector = {"main": "Forma yuklandi"}

    monitor.run_case(cases[1], navigate=open_second_form, validate=lambda: None)

    results = monitor.complete_results()
    assert [result["status"] for result in results] == [NOT_OPENED, PASSED]
    assert results[0]["validation_completed"] is False
    assert results[0]["validation_passed"] is False
    assert results[0]["screenshot_redacted"] is True
    assert results[1]["shell"] == "a2"


def test_unexpected_programming_error_is_not_hidden_as_form_failure(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    case = _case()
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=[case])

    with pytest.raises(TypeError, match="bad helper contract"):
        monitor.run_case(
            case,
            navigate=lambda: (_ for _ in ()).throw(TypeError("bad helper contract")),
            validate=lambda: None,
        )

    assert monitor.results == []


def test_precondition_duration_and_states_are_recorded_correctly(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("biruni/kauth/company_client_list", "Заголовок")
    cases = [_case(1), _case(2, path="trade/tvt/user_locations", title="Tracking")]
    monitor = FormMonitor(page, suite_name="Forms-02", planned_cases=cases)
    ticks = iter([10.0, 10.5, 10.5])
    monkeypatch.setattr(form_monitor.time, "monotonic", lambda: next(ticks))

    monitor.precondition(
        "A2 filialini sinxronlash",
        lambda: (_ for _ in ()).throw(AssertionError("TRADE tugmasi topilmadi")),
        affected_case_number=1,
    )
    results = monitor.complete_results()

    assert monitor.blockers[0]["duration_ms"] == 500
    assert results[0]["duration_ms"] == 500
    assert results[0]["status"] == TEST_BLOCKED
    assert results[0]["test_started"] is False
    assert results[0]["page_reached"] is False
    assert results[1]["status"] == NOT_CHECKED


def test_summary_does_not_duplicate_not_checked_forms():
    results = [
        build_form_result(
            number=1,
            filial="Администрирование",
            navbar_tab="Главное",
            menu_column="Дополнительное",
            menu_item="OAuth2",
            title="OAuth2",
            expected_path="biruni/kauth/company_client_list",
            actual_url="",
            ok=False,
            status=TEST_BLOCKED,
            reason_code="FILIAL_SWITCH_FAILED",
            test_started=False,
            test_completed=False,
        ),
        build_form_result(
            number=2,
            filial="filial-pw{code}",
            navbar_tab="Продажа",
            menu_column="Визиты",
            menu_item="Визиты",
            title="Визиты",
            expected_path="trade/tvt/visit_list",
            actual_url="",
            ok=False,
            status=NOT_CHECKED,
            reason_code="BLOCKED_BY_PRECONDITION",
            reason_summary="Oldingi blocker sabab tekshirilmadi",
            test_started=False,
            test_completed=False,
        ),
    ]

    summary = render_monitor_summary(
        suite_name="Forms",
        planned_count=2,
        results=results,
        blockers=[],
    )

    assert "Testi boshlangan       : 0" in summary
    assert summary.count("⬜ 002") == 1
    assert "BARCHA FORMA NATIJALARI" not in summary
    assert "BOSHLANGAN FORMA TESTLARI" not in summary


def test_safe_screenshot_masks_inputs_and_secret_columns():
    page = FakePage(
        url="https://smartup.online/a2/biruni/kauth/company_client_list"
    )

    assert safe_page_screenshot(page) == b"png"

    assert page.screenshot_kwargs["full_page"] is True
    assert page.screenshot_kwargs["mask_color"] == "#2f3542"
    mask_selectors = {locator.selector for locator in page.screenshot_kwargs["mask"]}
    assert "input:not([type='hidden'])" in mask_selectors
    assert "[data-smt-col-key*='secret' i]" in mask_selectors
    assert "app-company-client-list .smt-data-row" in mask_selectors
    assert "client-secret" in page.screenshot_kwargs["style"]


def test_runtime_duplicate_result_is_rejected(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    case = _case()
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=[case])

    monitor.run_case(case, navigate=lambda: None, validate=lambda: None)
    with pytest.raises(RuntimeError, match="ikki marta"):
        monitor.run_case(case, navigate=lambda: None, validate=lambda: None)


def test_monitor_payload_has_versioned_metrics_and_durations():
    result = build_form_result(
        number=1,
        filial="filial-pw{code}",
        navbar_tab="Продажа",
        menu_column="Визиты",
        menu_item="Визиты",
        title="Визиты",
        expected_path="trade/tvt/visit_list",
        actual_url="https://smartup.online/a2/trade/tvt/visit_list",
        ok=True,
        duration_ms=321,
    )
    payload = build_monitor_payload(
        suite_name="Forms",
        planned_count=1,
        results=[result],
        blockers=[],
    )

    assert payload["schema_version"] == 2
    assert payload["metrics"] == {
        "started": 1,
        "completed": 1,
        "page_reached": 1,
        "validation_completed": 1,
        "validation_passed": 1,
        "usable": 1,
    }
    assert json.loads(json.dumps(payload))["results"][0]["duration_ms"] == 321


def test_form_execution_has_no_legacy_reporting_fallback():
    signature = inspect.signature(run_form_cases)
    assert list(signature.parameters) == ["page", "cases", "monitor"]
    assert signature.parameters["monitor"].default is inspect.Parameter.empty
    flow_source = (ROOT / "tests/smoke/test_forms/flow.py").read_text(encoding="utf-8")
    assert "def finish_form_results" not in flow_source
    assert "results=None" not in inspect.getsource(run_form_cases)
