import json

from scripts import analyze_test_result
from scripts import telegram_progress


HIDDEN_CLICK_MESSAGE = """playwright._impl._errors.TimeoutError: Locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator(".pt-3.px-2")
    - locator resolved to <div class="pt-3 px-2">…</div>
  - attempting click action
    - element is not visible
"""


def test_hidden_locator_is_not_reported_as_missing():
    failure = analyze_test_result._humanize_failure(
        {
            "name": "03 - Room",
            "fullName": "tests.smoke.test_setup.test_setup_runner#test_03_room",
            "status": "broken",
            "message": HIDDEN_CLICK_MESSAGE,
            "trace": (
                "tests/smoke/test_setup/test_setup_runner.py:53: in test_03_room\n"
                "tests/smoke/test_setup/test_room.py:21: in run_room"
            ),
            "failed_steps": [
                {
                    "path": ["1 - Ish zonalari ro'yxatiga o'tish"],
                    "name": "1 - Ish zonalari ro'yxatiga o'tish",
                    "status": "broken",
                    "message": HIDDEN_CLICK_MESSAGE,
                }
            ],
        },
        skipped_count=18,
    )

    assert failure["target"] == 'locator(".pt-3.px-2")'
    assert failure["element_state"] == "hidden"
    assert failure["timeout"] == "10 sekund"
    assert "Element topildi, ammo ko'rinmagani" in failure["reason"]
    assert "element topilmadi" not in failure["reason"]
    assert "ko'rinadigan elementga" in failure["next_action"]


def test_failed_telegram_block_is_compact_and_actionable():
    state = {
        "result": "FAILED",
        "target": "setup-a2-admin",
        "server": "https://smartup.online",
        "summary": "1 failed, 2 passed, 18 skipped",
        "results": [
            {
                "status": "FAILED",
                "display": "03 - Room",
                "group": "Setup",
                "runner": "test_03_room",
                "inner_test": "1 - Ish zonalari ro'yxatiga o'tish",
                "failed_step": "1 - Ish zonalari ro'yxatiga o'tish",
                "error_type": "TimeoutError",
                "timeout": "10 sekund",
                "element_state": "hidden",
                "target": 'locator(".pt-3.px-2")',
                "reason": (
                    "Element topildi, ammo ko'rinmagani uchun 10 sekund ichida bosilmadi. "
                    'Maqsad: locator(".pt-3.px-2").'
                ),
                "location": "tests/smoke/test_setup/test_room.py:21",
                "impact": "Setup tugamagani uchun keyingi 18 ta test skip bo'lgan.",
                "next_action": "Locatorni ko'rinadigan elementga aniqlashtir.",
            }
        ],
    }

    message = telegram_progress.render_message(state)

    assert "❌ Xato tafsiloti:" in message
    assert "Test: Setup → 03 - Room" in message
    assert "Qadam: 1 - Ish zonalari ro'yxatiga o'tish" in message
    assert (
        'Texnik: TimeoutError · 10 sekund · element yashirin · locator(".pt-3.px-2")'
        in message
    )
    assert "Ta'sir: Setup tugamagani uchun keyingi 18 ta test skip bo'lgan." in message
    assert "Yechim: Locatorni ko'rinadigan elementga aniqlashtir." in message
    assert "Runner:" not in message
    assert "Reason:" not in message


def test_system_summary_diagnostics_reach_telegram_state(tmp_path, monkeypatch):
    summary_path = tmp_path / "system-summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "failed_tests": [
                    {
                        "group": "Setup",
                        "runner_test": "test_03_room",
                        "inner_test": "1 - Ish zonalari ro'yxatiga o'tish",
                        "failed_step": "1 - Ish zonalari ro'yxatiga o'tish",
                        "error_type": "TimeoutError",
                        "target": 'locator(".pt-3.px-2")',
                        "element_state": "hidden",
                        "timeout": "10 sekund",
                        "impact": "18 ta test skip bo'lgan.",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(telegram_progress, "SYSTEM_SUMMARY_JSON", summary_path)

    details = telegram_progress.failed_details_from_system_summary()

    assert details["target"] == 'locator(".pt-3.px-2")'
    assert details["element_state"] == "hidden"
    assert details["timeout"] == "10 sekund"
    assert details["impact"] == "18 ta test skip bo'lgan."
