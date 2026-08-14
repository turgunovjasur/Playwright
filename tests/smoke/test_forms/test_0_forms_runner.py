"""Har bir navbar formasini alohida pytest/Allure test sifatida ishlatish.

Bu canonical Forms runner:

- full, ``setup-forms`` va ``forms`` targetlarida avtomatik collect qilinadi;
- mavjud beshta navbar inventorysi yagona forma ma'lumotlari manbasi bo'lib
  qoladi, bu faylda forma definitionlari takrorlanmaydi;
- har bir active forma va intentional skip alohida pytest/Allure item bo'ladi;
- recoverable xatolar ``monitoring/recovery.py`` policy registrysi orqali
  maksimum bir marta retry qilinadi.

Forms run buyrug'i:

```
./.venv/bin/pytest -q -s --maxfail=0 tests/smoke/test_forms/test_0_forms_runner.py
```

Joriy inventory snapshotida Allure'da 345 ta aktiv forma alohida PASSED/FAILED
test, registrydagi 13 ta intentional skip esa alohida SKIPPED test sifatida
ko'rinadi.
``--maxfail=0`` bir nechta forma failed bo'lsa ham qolgan formalar davom
etishini explicit kafolatlaydi.
"""

import time

import allure
import pytest
from allure_commons.types import LabelType
from playwright.sync_api import Error as PlaywrightError

from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.test_forms.inventory import (
    OPERATIONAL_PLACEHOLDER,
    get_legacy_form_buckets,
)
from tests.smoke.test_forms.monitoring.monitor import FormMonitor
from tests.smoke.test_forms.monitoring.navigation import (
    first_operational_filial,
    run_form_cases,
    switch_forms_filial,
)
from tests.smoke.test_forms.monitoring.recovery import (
    FormRecoveryContext,
    run_with_form_recovery,
)
from tests.smoke.test_forms.monitoring.suite_runner import build_suite_inventory


pytestmark = [
    pytest.mark.smoke_group(
        "Forms",
        independent=True,
        setup_independent=True,
    ),
    allure.epic("Smoke"),
]


NAVBAR_SUITES = (
    ("01", "Главное"),
    ("02", "Продажа"),
    ("03", "Склад"),
    ("04", "Финансы"),
    ("05", "Справочники"),
)


def form_pytest_id(case):
    """Inventory case uchun barqaror va o'qiladigan pytest parametr ID yasash."""
    expected_path = str(case.get("expected_path") or "form")
    path_slug = expected_path.replace("/", "-").replace("+", "-")
    return (
        f"{case['global_number']:03d}-"
        f"{case['suite_number']}-"
        f"{case['navbar_tab']}-"
        f"{path_slug}"
    )


def form_allure_marks(case):
    """Test body boshlanmasa ham forma Allure guruhlarini saqlab qolish."""
    return [
        pytest.mark.allure_label(
            f"Forms — {case['navbar_tab']}",
            label_type=LabelType.FEATURE,
        ),
        pytest.mark.allure_label(
            case["menu_column"] or "Ustunsiz",
            label_type=LabelType.STORY,
        ),
    ]


def build_form_params():
    """Besh navbar inventorysidagi har bir formani alohida pytest parametr qilish."""
    params = []
    global_number = 1

    for suite_number, navbar_tab in NAVBAR_SUITES:
        form_buckets = get_legacy_form_buckets(navbar_tab)
        planned_cases, skipped_cases = build_suite_inventory(
            form_buckets,
            shell="legacy",
            navbar_tab=navbar_tab,
        )

        for inventory_case in planned_cases:
            form_case = {
                **inventory_case,
                "suite_number": suite_number,
                "global_number": global_number,
            }
            params.append(
                pytest.param(
                    form_case,
                    id=form_pytest_id(form_case),
                    marks=form_allure_marks(form_case),
                )
            )
            global_number += 1

        for inventory_case in skipped_cases:
            form_case = {
                **inventory_case,
                "suite_number": suite_number,
                "global_number": global_number,
            }
            params.append(
                pytest.param(
                    form_case,
                    id=form_pytest_id(form_case),
                    marks=[
                        *form_allure_marks(form_case),
                        pytest.mark.skip(reason=form_case["reason"]),
                    ],
                )
            )
            global_number += 1

    return tuple(params)


FORM_CASES = build_form_params()


@pytest.fixture(scope="module")
def forms_session(group_session_page):
    """Forms runner uchun bitta admin session va filial state yaratish.

    Barcha parametrized formalar bir browser context/page'dan foydalanadi.
    Admin login hamda operatsion filialni aniqlash faqat bir marta bajariladi.
    """
    with allure.step("Forms | Company admini bilan authorization"):
        authorization(group_session_page, who="admin")

    operational_filial = None
    operational_filial_error = None
    with allure.step("Forms | Operatsion filialni aniqlashga urinish"):
        try:
            operational_filial = first_operational_filial(group_session_page)
        except (AssertionError, PlaywrightError) as exc:
            operational_filial_error = exc
            allure.attach(
                str(exc),
                name="Operatsion filialni aniqlash xatosi",
                attachment_type=allure.attachment_type.TEXT,
            )

    return {
        "page": group_session_page,
        "operational_filial": operational_filial,
        "operational_filial_error": operational_filial_error,
        "current_filial": None,
    }


def target_filial(form_case, session_state):
    """Inventory placeholderini joriy running haqiqiy filial nomiga aylantirish."""
    if form_case["filial"] == OPERATIONAL_PLACEHOLDER:
        return session_state["operational_filial"]
    return form_case["filial"]


def run_single_form(
    session_state,
    *,
    form_case,
    progress_test_id,
    terminal_reporter=None,
):
    """Bitta inventory formasini alohida FormMonitor lifecycle bilan tekshirish.

    1. Inventory placeholderidan kerakli filialni aniqlash.
    2. Filial o'zgargan bo'lsa o'sha filialga o'tish.
    3. Faqat joriy formani markaziy FormMonitor orqali ochib tekshirish.
    4. Shu formaning summary va ``form-monitor.json`` attachmentini chiqarish.
    """
    page = session_state["page"]
    resolved_filial = target_filial(form_case, session_state)
    monitor_case = {
        **form_case,
        "number": 1,
        "filial": resolved_filial or OPERATIONAL_PLACEHOLDER,
    }
    suite_name = (
        f"Forms-{form_case['suite_number']} — {form_case['navbar_tab']}"
    )
    monitor = FormMonitor(
        page,
        suite_name=suite_name,
        planned_cases=[monitor_case],
        skipped_cases=[],
        terminal_reporter=terminal_reporter,
        progress_runner="test_0_forms_runner.py",
        progress_test_id=progress_test_id,
    )

    primary_error = None
    try:
        if resolved_filial is None:
            operation = "Operatsion filialni aniqlash"
            monitor.record_precondition_failure(
                operation,
                session_state["operational_filial_error"],
                affected_case_number=monitor_case["number"],
                started_at=time.monotonic(),
            )
        elif session_state["current_filial"] != resolved_filial:
            started_at = time.monotonic()
            operation = f"'{resolved_filial}' filialiga o'tish"
            try:
                with allure.step(f"Forma precondition | {operation}"):
                    switch_forms_filial(page, resolved_filial)
            except (AssertionError, PlaywrightError) as exc:
                session_state["current_filial"] = None
                monitor.record_precondition_failure(
                    operation,
                    exc,
                    affected_case_number=monitor_case["number"],
                    started_at=started_at,
                )
            else:
                session_state["current_filial"] = resolved_filial

        if not monitor.blocked:
            run_form_cases(
                page,
                monitor.cases(),
                monitor=monitor,
            )
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        try:
            with allure.step("1 ta forma natijasini jamlash"):
                results = monitor.finish()
        except BaseException:
            if primary_error is None:
                raise

    return results


@allure.title("{form_case[global_number]:03d} | {form_case[label]}")
@pytest.mark.parametrize("form_case", FORM_CASES)
def test_form_case(
    forms_session,
    form_case,
    pytestconfig,
    request,
):
    """Bitta inventory formasi = bitta pytest item = bitta Allure test.

    1. Navbar, menu, filial, URL va shell metadata'larini Allure'ga yozish.
    2. Joriy parametrdagi faqat bitta formani ``run_single_form`` bilan ochish.
    3. FormMonitor hard-checklari va diagnostikalarini shu testga biriktirish.
    """
    allure.dynamic.title(
        f"{form_case['global_number']:03d} | {form_case['label']}"
    )
    allure.dynamic.parameter("Navbar", form_case["navbar_tab"])
    allure.dynamic.parameter(
        "Menu column",
        form_case["menu_column"] or "—",
    )
    allure.dynamic.parameter(
        "Filial",
        target_filial(form_case, forms_session) or "Aniqlanmadi",
    )
    allure.dynamic.parameter("Expected URL", form_case["expected_path"])
    allure.dynamic.parameter("Shell", form_case["shell"])

    terminal_reporter = pytestconfig.pluginmanager.get_plugin("terminalreporter")
    recovery_context = FormRecoveryContext(
        page=forms_session["page"],
        item=request.node,
        session_state=forms_session,
        form_case=form_case,
    )
    run_with_form_recovery(
        lambda: run_single_form(
            forms_session,
            form_case=form_case,
            progress_test_id=request.node.name,
            terminal_reporter=terminal_reporter,
        ),
        context=recovery_context,
    )
