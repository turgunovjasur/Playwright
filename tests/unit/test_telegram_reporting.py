import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


analyze_test_result = _load_script("analyze_test_result")
telegram_progress = _load_script("telegram_progress")


def test_a2_checked_forms_are_counted_from_numbered_allure_steps():
    results = [
        {
            "name": "A2 admin formalar — aniq menyu qadamlari orqali ochilish smoke",
            "fullName": (
                "tests.smoke.test_forms.test_a2_admin_menu_forms"
                "#test_a2_admin_menu_forms"
            ),
            "status": "passed",
            "steps": [
                {
                    "name": "Parent",
                    "steps": [
                        {"name": "01 — Birinchi forma", "status": "passed"},
                        {"name": "02 — Ikkinchi forma", "status": "passed"},
                        {"name": "03 — Uchinchi forma", "status": "failed"},
                        {"name": "Yo'l: menyu → forma", "status": "passed"},
                    ],
                }
            ],
        }
    ]

    deterministic = analyze_test_result.build_deterministic_summary(1, results)
    local = analyze_test_result.build_local_summary(deterministic)

    assert deterministic["a2_admin_forms"] == {
        "checked": 3,
        "passed": 2,
        "failed": 1,
        "skipped": 0,
    }
    assert deterministic["form_coverage"]["checked"] == 3
    assert local["a2_admin_forms"] == deterministic["a2_admin_forms"]
    assert local["form_coverage"] == deterministic["form_coverage"]


def test_forms_runner_wrappers_produce_combined_coverage():
    deterministic = analyze_test_result.build_deterministic_summary(
        0,
        [
            {
                "name": "Forms-01 - Справочники menu formalarini ochish",
                "fullName": (
                    "tests.smoke.test_forms.test_forms_runner"
                    "#test_forms_01_spravochniki"
                ),
                "status": "passed",
                "steps": [
                    {
                        "name": "Parent",
                        "steps": [
                            {
                                "name": "001 | Filial: filial | Forma: ТМЦ",
                                "status": "passed",
                            },
                            {
                                "name": "002 | Filial: filial | Forma: Цены",
                                "status": "passed",
                            },
                        ],
                    }
                ],
            },
            {
                "name": "Forms-02 - A2 admin menu formalarini ochish",
                "fullName": (
                    "tests.smoke.test_forms.test_forms_runner"
                    "#test_forms_02_a2_admin"
                ),
                "status": "passed",
                "steps": [
                    {
                        "name": "Parent",
                        "steps": [
                            {"name": "01 — OAuth2", "status": "passed"},
                            {"name": "02 — Визиты", "status": "passed"},
                        ],
                    }
                ],
            },
        ],
    )

    assert deterministic["form_coverage"] == {
        "checked": 4,
        "passed": 4,
        "failed": 0,
        "skipped": 0,
        "suites": {
            "spravochniki": {
                "label": "Справочники",
                "checked": 2,
                "passed": 2,
                "failed": 0,
                "skipped": 0,
            },
            "a2_admin": {
                "label": "A2 Admin",
                "checked": 2,
                "passed": 2,
                "failed": 0,
                "skipped": 0,
            },
        },
    }
    assert deterministic["a2_admin_forms"]["checked"] == 2


def test_a2_form_steps_are_preserved_when_allure_results_are_collected(tmp_path):
    result_path = tmp_path / "a2-result.json"
    result_path.write_text(
        json.dumps(
            {
                "name": "A2 admin formalar — smoke",
                "fullName": (
                    "tests.smoke.test_forms.test_a2_admin_menu_forms"
                    "#test_a2_admin_menu_forms"
                ),
                "status": "passed",
                "steps": [
                    {
                        "name": "Parent",
                        "steps": [
                            {"name": "01 — Birinchi forma", "status": "passed"},
                            {"name": "02 — Ikkinchi forma", "status": "passed"},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    results = analyze_test_result.collect_allure_results(tmp_path, started_at=0)
    deterministic = analyze_test_result.build_deterministic_summary(0, results)

    assert results[0]["a2_form_steps"] == [
        {"name": "01 — Birinchi forma", "status": "passed"},
        {"name": "02 — Ikkinchi forma", "status": "passed"},
    ]
    assert deterministic["a2_admin_forms"]["checked"] == 2


def test_failure_uses_exact_allure_step_path_without_impact_or_solution():
    deterministic = analyze_test_result.build_deterministic_summary(
        1,
        [
            {
                "name": "A2 admin formalar — smoke",
                "fullName": (
                    "tests.smoke.test_forms.test_a2_admin_menu_forms"
                    "#test_a2_admin_menu_forms"
                ),
                "status": "failed",
                "message": "Locator.click: Timeout 10000ms exceeded.",
                "trace": "",
                "failed_steps": [
                    {
                        "path": [
                            "2 - Operatsion filial",
                            "06 — Коммерческий дашборд",
                            "Tekshiruv: title va URL",
                        ],
                        "name": "Tekshiruv: title va URL",
                        "status": "failed",
                    }
                ],
                "a2_form_steps": [
                    {"name": "06 — Коммерческий дашборд", "status": "failed"}
                ],
            }
        ],
    )

    failure = deterministic["failed_tests"][0]
    assert failure["failed_step"] == (
        "2 - Operatsion filial → 06 — Коммерческий дашборд "
        "→ Tekshiruv: title va URL"
    )
    assert "impact" not in failure
    assert "next_action" not in failure


def test_success_message_shows_setup_and_forms_coverage():
    message = telegram_progress.render_message(
        {
            "target": "setup-forms",
            "server": "https://app3.greenwhite.uz/xtrade",
            "result": "PASSED",
            "summary": "21 passed, 1 deselected in 530.93s",
            "started_clock": "15:53",
            "finished_clock": "16:02",
            "duration": "9m 25s",
            "a2_admin_forms": {"checked": 22, "passed": 22},
            "form_coverage": {
                "checked": 111,
                "passed": 111,
                "failed": 0,
                "skipped": 0,
                "suites": {
                    "spravochniki": {
                        "label": "Справочники",
                        "checked": 89,
                        "passed": 89,
                    },
                    "a2_admin": {
                        "label": "A2 Admin",
                        "checked": 22,
                        "passed": 22,
                    },
                },
            },
            "results": [
                {
                    "group": "Setup",
                    "status": "PASSED",
                    "display": "01 - Legal Person",
                },
                {
                    "group": "A2 Admin Forms group",
                    "status": "PASSED",
                    "display": "A2 admin formalar",
                },
            ],
            "run_code": "317333",
            "run_url": "https://github.com/example/actions/runs/1",
        }
    )

    assert "🧪 Pytest: 21 passed, 1 deselected in 530.93s" in message
    assert "⚙️ Setup: 1/1 qadam o'tdi" in message
    assert "🧾 Forms: 111/111 forma ochildi" in message
    assert "• Справочники: 89/89" in message
    assert "• A2 Admin: 22/22" in message
    assert "🆔 Code: 317333" in message
    assert "(+5)" not in message
    assert "user-pw317333" not in message
    assert "01 - Legal Person" not in message
    assert "A2 admin formalar\n" not in message
    assert "<blockquote expandable>" not in message


def test_failure_details_are_collapsed_and_html_escaped():
    message = telegram_progress.render_message(
        {
            "target": "setup-forms",
            "server": "https://app3.greenwhite.uz/xtrade",
            "result": "FAILED",
            "summary": "5 passed, 1 failed",
            "a2_admin_forms": {"checked": 6, "passed": 5, "failed": 1},
            "form_coverage": {
                "checked": 6,
                "passed": 5,
                "failed": 1,
                "skipped": 0,
                "suites": {
                    "a2_admin": {
                        "label": "A2 Admin",
                        "checked": 6,
                        "passed": 5,
                        "failed": 1,
                    }
                },
            },
            "results": [
                {
                    "group": "A2 Admin Forms group",
                    "status": "FAILED",
                    "display": "A2 admin formalar",
                    "failed_step": "2 - Operatsion filial → 06 — Коммерческий дашборд → Tekshiruv: title va URL",
                    "message": "Locator.click: Timeout 10000ms exceeded.",
                    "target": "<button data-test='save'>",
                    "impact": "Hardcode ta'sir",
                    "next_action": "Hardcode yechim",
                }
            ],
        }
    )

    assert "🧾 Forms: 5/6 forma ochildi" in message
    assert "• A2 Admin: 5/6" in message
    assert "<blockquote expandable>" in message
    assert "</blockquote>" in message
    assert (
        "Allure step: 2 - Operatsion filial → 06 — Коммерческий дашборд "
        "→ Tekshiruv: title va URL"
    ) in message
    assert "Xato: Locator.click: Timeout 10000ms exceeded." in message
    assert "Ta'sir" not in message
    assert "Yechim" not in message
    assert "Hardcode ta'sir" not in message
    assert "Hardcode yechim" not in message
    assert "&lt;button data-test='save'&gt;" in message
    assert "<button data-test='save'>" not in message


def test_summary_metrics_are_loaded_into_telegram_state(tmp_path, monkeypatch):
    summary_path = tmp_path / "system-summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "a2_admin_forms": {"checked": 22, "passed": 22},
                "form_coverage": {
                    "checked": 111,
                    "passed": 111,
                    "suites": {
                        "spravochniki": {
                            "label": "Справочники",
                            "checked": 89,
                            "passed": 89,
                        },
                        "a2_admin": {
                            "label": "A2 Admin",
                            "checked": 22,
                            "passed": 22,
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(telegram_progress, "SYSTEM_SUMMARY_JSON", summary_path)
    state = {}

    telegram_progress.sync_summary_metrics(state)

    assert state["a2_admin_forms"]["checked"] == 22
    assert state["form_coverage"]["checked"] == 111


def test_telegram_ci_defaults_to_setup_forms():
    bot = (ROOT / "scripts" / "telegram_ci_bot.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "daily-smoke.yml").read_text(
        encoding="utf-8"
    )

    assert 'DEFAULT_REF = "main"' in bot
    assert 'DEFAULT_TARGET = "setup-forms"' in bot
    assert "TEST_TARGET: setup-forms" in workflow
