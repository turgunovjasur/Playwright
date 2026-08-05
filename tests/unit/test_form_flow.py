import ast
import inspect
import json
import re
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

    def wait_for(self, *, state=None, timeout=None):
        self.page.wait_for_calls.append((self.selector, timeout))
        revealed = [
            selector
            for selector in self.page.late_visible_selectors
            if selector in self.selector
        ]
        if not revealed:
            raise PlaywrightError(f"Timeout {timeout}ms exceeded")
        self.page.visible_selectors.update(revealed)

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
        late_visible_selectors=None,
    ):
        self.url = url
        self.current_title = title
        self.visible_selectors = set(visible_selectors or [])
        self.text_by_selector = dict(text_by_selector or {})
        self.inner_text_errors = set(inner_text_errors or [])
        self.late_visible_selectors = set(late_visible_selectors or [])
        self.wait_for_calls = []
        self.screenshot_kwargs = None
        self.listeners = {}

    def on(self, event, handler):
        self.listeners.setdefault(event, []).append(handler)

    def remove_listener(self, event, handler):
        self.listeners.get(event, []).remove(handler)

    def emit(self, event, payload):
        for handler in list(self.listeners.get(event, [])):
            handler(payload)

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
    monitored_login = re.compile(r'monitor\.precondition\(\s*"Admin avtorizatsiyasi"')
    assert monitored_login.search(forms_01_source)
    assert monitored_login.search(forms_02_source)


def test_forms_suites_report_even_when_an_unexpected_error_escapes():
    for relative_path, suite_function in (
        (
            "tests/smoke/test_forms/test_01_spravochniki_menu_forms.py",
            "run_spravochniki_menu_forms",
        ),
        (
            "tests/smoke/test_forms/test_02_a2_admin_menu_forms.py",
            "run_a2_admin_menu_forms",
        ),
        (
            "tests/smoke/test_forms/test_03_prodaja_menu_forms.py",
            "run_prodaja_menu_forms",
        ),
    ):
        module = ast.parse((ROOT / relative_path).read_text(encoding="utf-8"))
        suite = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == suite_function
        )
        finish_calls = [
            node
            for node in ast.walk(suite)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "finish"
        ]
        assert len(finish_calls) == 1, suite_function
        guaranteed = any(
            finish_calls[0] in list(ast.walk(statement))
            for node in ast.walk(suite)
            if isinstance(node, ast.Try)
            for statement in node.finalbody
        )
        assert guaranteed, suite_function


def test_failure_is_classified_from_the_state_that_caused_it(monkeypatch):
    _silence_allure(monkeypatch)

    class VanishingAlertPage(FakePage):
        """Alert ikkinchi o'qishda yo'qoladi — holat qayta o'qilganini fosh qiladi."""

        alert_selector = "#biruniAlert:visible"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.alert_reads = 0

        def locator(self, selector):
            if selector == self.alert_selector:
                self.alert_reads += 1
                if self.alert_reads > 1:
                    self.visible_selectors.discard(self.alert_selector)
            return FakeLocator(self, selector)

    page = VanishingAlertPage(
        url="https://smartup.online/a2/trade/tvt/visit_list",
        title="Визиты",
        visible_selectors={"main", VanishingAlertPage.alert_selector},
        text_by_selector={
            "main": "Forma kontenti",
            VanishingAlertPage.alert_selector: "× Нет доступа к форме",
        },
    )
    case = _case()
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=[case])

    result = monitor.run_case(case, navigate=lambda: None, validate=lambda: None)

    assert page.alert_reads == 1
    assert result["reason_code"] == "APPLICATION_ERROR"
    assert result["status"] == OPENED_WITH_DEFECT
    assert result["checks"]["visible_error"] == "× Нет доступа к форме"
    assert "[APPLICATION_ERROR]" in result["detail"]


def test_late_application_error_is_not_missed_by_an_instant_snapshot():
    late_alert = "#biruniAlert:visible"
    page = FakePage(
        url="https://smartup.online/a2/trade/tvt/visit_list",
        title="Визиты",
        visible_selectors={"main"},
        text_by_selector={
            "main": "Forma kontenti",
            late_alert: "Нет доступа к форме",
        },
        late_visible_selectors={late_alert},
    )

    state = capture_form_state(page)

    assert state["visible_error"] == "Нет доступа к форме"
    waited_selector, waited_timeout = page.wait_for_calls[0]
    assert late_alert in waited_selector
    assert waited_timeout == form_monitor.ALERT_WAIT_MS


def test_missing_page_signals_are_read_without_a_dead_timeout_argument():
    page = FakePage(
        url="https://smartup.online/#/!token/anor/mr/region_list",
        title="Регионы",
        visible_selectors={"b-page:visible"},
    )

    state = capture_form_state(page)

    assert state["content_ready"] is True
    assert state["loader_visible"] is False
    assert "timeout" not in inspect.signature(form_monitor._safe_locator_visible).parameters


def test_legacy_page_without_heading_reports_an_unverified_title():
    case = form_case(
        number=4,
        filial="Администрирование",
        navbar_tab="Справочники",
        menu_column="Справочники",
        menu_item="Дашборд",
        title="Дашборд",
        expected_path="anor/mcg/mml_dashboard",
        shell="legacy",
    )
    state = {
        "canonical_path": "anor/mcg/mml_dashboard",
        "title_candidates": [],
        "title_source": "visible_heading",
        "actual_title": "",
        "content_ready": True,
        "visible_error": "",
        "loader_visible": False,
    }

    checks = FormMonitor._checks(case, state)

    assert checks["title_matches"] is True
    assert checks["title_verified"] is False

    state["title_candidates"] = ["Дашборд"]
    assert FormMonitor._checks(case, state)["title_verified"] is True


def test_summary_lists_forms_whose_title_was_never_compared():
    unverified = build_form_result(
        number=1,
        filial="Администрирование",
        navbar_tab="Справочники",
        menu_column="Справочники",
        menu_item="Дашборд",
        title="Дашборд",
        expected_path="anor/mcg/mml_dashboard",
        actual_url="https://smartup.online/#/!token/anor/mcg/mml_dashboard",
        status=PASSED,
        checks={"title_matches": True, "title_verified": False},
    )
    not_checked = build_form_result(
        number=2,
        filial="Администрирование",
        navbar_tab="Справочники",
        menu_column="Справочники",
        menu_item="Цены",
        title="Цены",
        expected_path="anor/mr/price_list",
        actual_url="",
        status=NOT_CHECKED,
        reason_code="NOT_EXECUTED",
        checks={},
    )

    summary = render_monitor_summary(
        suite_name="Forms-01",
        planned_count=2,
        results=[unverified, not_checked],
        blockers=[],
    )

    assert "TITLE TAQQOSLANMAGAN FORMALAR" in summary
    assert summary.count("⚠️ 001") == 1
    assert "⚠️ 002" not in summary


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


class FakeResponse:
    def __init__(self, status, url):
        self.status = status
        self.url = url


class FakeJsError:
    def __init__(self, message):
        self.message = message


def test_failed_requests_are_recorded_without_failing_the_form(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    case = _case()
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=[case])

    def open_form_with_broken_backend():
        page.emit(
            "response",
            FakeResponse(500, "https://smartup.online/b/anor/mr/list?token=secret"),
        )
        page.emit("response", FakeResponse(200, "https://smartup.online/b/ok"))

    result = monitor.run_case(
        case,
        navigate=open_form_with_broken_backend,
        validate=lambda: None,
    )

    assert result["status"] == PASSED
    assert result["usable"] is True
    assert result["checks"]["failed_request_count"] == 1
    assert result["checks"]["failed_requests"] == ["500 smartup.online/b/anor/mr/list"]

    summary = render_monitor_summary(
        suite_name="Forms",
        planned_count=1,
        results=monitor.complete_results(),
        blockers=[],
    )
    assert "JS VA NETWORK SIGNALLARI" in summary
    assert "500 smartup.online/b/anor/mr/list" in summary
    assert "token=secret" not in summary


def test_js_error_turns_an_otherwise_healthy_form_into_a_defect(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    case = _case()
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=[case])

    result = monitor.run_case(
        case,
        navigate=lambda: page.emit(
            "pageerror", FakeJsError("TypeError: filter is not a function")
        ),
        validate=lambda: None,
    )

    assert result["status"] == OPENED_WITH_DEFECT
    assert result["reason_code"] == "JS_ERROR"
    assert result["opened"] is True
    assert result["usable"] is False
    assert result["checks"]["js_errors"] == ["TypeError: filter is not a function"]
    assert result["checks"]["js_error_count"] == 1
    assert "TypeError: filter is not a function" in result["detail"]


def test_visible_ui_error_outranks_a_js_error():
    case = {"expected_path": "trade/tvt/visit_list", "title": "Визиты"}
    state = {
        "canonical_path": "trade/tvt/visit_list",
        "actual_title": "Визиты",
        "title_candidates": ["Визиты"],
        "title_source": "document",
        "content_ready": True,
        "visible_error": "Нет доступа к форме",
        "js_errors": ["TypeError: x is not a function"],
        "loader_visible": False,
    }

    assert classify_form_failure(
        case=case, stage="validation", detail="UI error", state=state
    )["reason_code"] == "APPLICATION_ERROR"

    state["visible_error"] = ""
    assert classify_form_failure(
        case=case, stage="validation", detail="JS", state=state
    )["reason_code"] == "JS_ERROR"


def test_js_error_outranks_a_stuck_loader_and_blank_content():
    case = {"expected_path": "trade/tvt/visit_list", "title": "Визиты"}
    state = {
        "canonical_path": "trade/tvt/visit_list",
        "actual_title": "Визиты",
        "title_candidates": ["Визиты"],
        "title_source": "document",
        "content_ready": False,
        "visible_error": "",
        "js_errors": ["TypeError: x is not a function"],
        "loader_visible": True,
    }

    analysis = classify_form_failure(
        case=case, stage="validation", detail="JS", state=state
    )

    assert analysis["reason_code"] == "JS_ERROR"
    assert analysis["status"] == OPENED_WITH_DEFECT


def test_page_events_do_not_leak_between_forms(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    cases = [
        _case(1),
        _case(2, path="trade/tvt/user_locations", title="Отслеживание"),
    ]
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=cases)

    monitor.run_case(
        cases[0],
        navigate=lambda: page.emit("pageerror", FakeJsError("Birinchi formaning JS xatosi")),
        validate=lambda: None,
    )

    def open_second_form():
        page.url = "https://smartup.online/a2/trade/tvt/user_locations"
        page.current_title = "Отслеживание"

    second = monitor.run_case(cases[1], navigate=open_second_form, validate=lambda: None)

    assert second["checks"]["js_error_count"] == 0
    assert second["checks"]["js_errors"] == []

    monitor._remove_page_listeners()
    page.emit("pageerror", FakeJsError("finish'dan keyingi xato"))
    assert monitor.js_error_count == 0


def test_page_event_sample_is_capped_but_the_count_is_not(monkeypatch):
    _silence_allure(monkeypatch)
    page = _a2_page("trade/tvt/visit_list", "Визиты")
    case = _case()
    monitor = FormMonitor(page, suite_name="Forms", planned_cases=[case])

    def open_form_with_many_failures():
        for number in range(form_monitor.MAX_PAGE_EVENTS + 5):
            page.emit(
                "response",
                FakeResponse(404, f"https://smartup.online/b/missing/{number}"),
            )

    result = monitor.run_case(
        case,
        navigate=open_form_with_many_failures,
        validate=lambda: None,
    )

    assert result["checks"]["failed_request_count"] == form_monitor.MAX_PAGE_EVENTS + 5
    assert len(result["checks"]["failed_requests"]) == form_monitor.MAX_PAGE_EVENTS


def test_summary_reports_total_average_and_slowest_forms():
    def timed_result(number, title, duration_ms, **overrides):
        return build_form_result(
            number=number,
            filial="filial-pw{code}",
            navbar_tab="Продажа",
            menu_column="Визиты",
            menu_item=title,
            title=title,
            expected_path=f"trade/tvt/form_{number}",
            actual_url=f"https://smartup.online/a2/trade/tvt/form_{number}",
            status=overrides.pop("status", PASSED),
            duration_ms=duration_ms,
            **overrides,
        )

    results = [
        timed_result(1, "Тихая", 1_000),
        timed_result(2, "Средняя", 3_000),
        timed_result(3, "Медленная", 8_000),
        timed_result(
            4,
            "Заблокированная",
            60_000,
            status=TEST_BLOCKED,
            reason_code="FILIAL_SWITCH_FAILED",
            test_started=False,
            test_completed=False,
        ),
    ]

    summary = render_monitor_summary(
        suite_name="Forms",
        planned_count=4,
        results=results,
        blockers=[],
    )

    assert "Jami                   : 12.0 s (3 forma)" in summary
    assert "O'rtacha bitta formaga : 4.0 s" in summary
    assert "Eng sekin 3 forma:" in summary
    assert "  1. 003 | Медленная | 8.0 s" in summary
    assert "  3. 001 | Тихая | 1.0 s" in summary
    assert "Заблокированная | 60.0 s" not in summary


def test_summary_skips_duration_section_when_nothing_was_timed():
    not_checked = build_form_result(
        number=1,
        filial="filial-pw{code}",
        navbar_tab="Продажа",
        menu_column="Визиты",
        menu_item="Визиты",
        title="Визиты",
        expected_path="trade/tvt/visit_list",
        actual_url="",
        status=NOT_CHECKED,
        reason_code="NOT_EXECUTED",
        duration_ms=None,
    )

    summary = render_monitor_summary(
        suite_name="Forms",
        planned_count=1,
        results=[not_checked],
        blockers=[],
    )

    assert "FORMA DAVOMIYLIGI" not in summary


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
        status=PASSED,
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
