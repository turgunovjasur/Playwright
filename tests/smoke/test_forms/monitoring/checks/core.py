"""Forma holatini baholaydigan pure hard-checklar va failure klassifikatsiyasi."""

from __future__ import annotations

import re


PASSED = "PASSED"
OBSERVED_ONLY = "OBSERVED_ONLY"
OPENED_WITH_DEFECT = "OPENED_WITH_DEFECT"
NOT_OPENED = "NOT_OPENED"
TEST_BLOCKED = "TEST_BLOCKED"
NOT_CHECKED = "NOT_CHECKED"

FORM_STATUSES = {
    PASSED,
    OBSERVED_ONLY,
    OPENED_WITH_DEFECT,
    NOT_OPENED,
    TEST_BLOCKED,
    NOT_CHECKED,
}

REASON_DESCRIPTIONS = {
    "TITLE_NOT_REACHED": (
        "Target URLga yetildi va forma kontenti yuklandi, lekin belgilangan "
        "vaqt ichida kutilgan sahifa nomi ko'rinmadi."
    ),
    "CONTENT_VALIDATION_FAILED": (
        "Target URLga yetildi, lekin forma uchun belgilangan tekshiruv "
        "muvaffaqiyatli tugamadi."
    ),
    "EXPECTED_URL_NOT_REACHED": "Belgilangan vaqt ichida kutilgan forma URLi ochilmadi.",
    "SHELL_NOT_DETECTED": "Actual forma URLidan A2 yoki legacy shell aniqlanmadi.",
    "NAVIGATION_FAILED": (
        "Menu, action yoki page-link bosqichida target forma URLiga o'tib bo'lmadi."
    ),
    "APPLICATION_ERROR": "Target sahifada aniq UI xato xabari ko'rindi.",
    "LOADER_NOT_FINISHED": "Forma yuklanish indikatori belgilangan vaqtda tugamadi.",
    "CONTENT_NOT_READY": "Target URLga yetildi, ammo forma kontenti tayyor bo'lmadi.",
    "FILIAL_SWITCH_FAILED": (
        "Kerakli filialga o'tib bo'lmadi; forma tekshiruvi boshlanmadi."
    ),
    "AUTHORIZATION_FAILED": (
        "Avtorizatsiya tugamadi; forma tekshiruvi boshlanmadi."
    ),
    "PRECONDITION_FAILED": (
        "Forma testidan oldingi majburiy tayyorlov bosqichi bajarilmadi."
    ),
    "BLOCKED_BY_PRECONDITION": (
        "Oldingi majburiy tayyorlov xatosi sabab bu forma tekshirilmadi."
    ),
    "NOT_EXECUTED": "Bu forma uchun tekshiruv ishga tushmadi.",
}

CHECK_NAMES = (
    "url",
    "loader",
    "application_error",
    "content_ready",
    "title",
)


def reason_description(reason_code):
    return REASON_DESCRIPTIONS.get(reason_code, "")


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def path_matches(case, state):
    expected_path = (case.get("expected_path") or "").strip("/")
    actual_url = str(state.get("actual_url") or "")
    actual_path = (state.get("canonical_path") or "").strip("/")
    return not expected_path or expected_path in (actual_url or actual_path)


def title_candidates(state):
    return [
        clean_text(candidate)
        for candidate in (state.get("title_candidates") or [])
        if clean_text(candidate)
    ]


def title_verified(case, state):
    """Title haqiqatan taqqoslandimi — report ``HA`` deb yolg'on aytmasin."""
    if not clean_text(case.get("title")):
        return False
    return bool(title_candidates(state) or clean_text(state.get("actual_title")))


def title_matches(case, state):
    expected_title = clean_text(case.get("title"))
    candidates = title_candidates(state)
    if not expected_title:
        return True
    if not candidates:
        actual_title = clean_text(state.get("actual_title"))
        candidates = [actual_title] if actual_title else []
    return expected_title in candidates


def _check_result(
    *,
    name,
    passed,
    reason_code,
    expected="",
    actual="",
    detail="",
    status="",
    opened=True,
):
    return {
        "name": name,
        "enabled": True,
        "execution_status": "PASSED" if passed else "FAILED",
        "passed": bool(passed),
        "reason_code": "" if passed else reason_code,
        "reason_summary": "" if passed else reason_description(reason_code),
        "expected": expected,
        "actual": actual,
        "detail": "" if passed else detail,
        "status": "" if passed else status,
        "opened": bool(opened),
    }


def check_url_state(case, state):
    """Browser-aware URL gate berilmagan compatibility holati uchun snapshot check."""
    passed = path_matches(case, state)
    return _check_result(
        name="url",
        passed=passed,
        reason_code="EXPECTED_URL_NOT_REACHED",
        expected=case.get("expected_path") or "",
        actual=state.get("canonical_path") or "",
        detail=(
            "Markaziy holat tekshiruvi [EXPECTED_URL_NOT_REACHED]: "
            f"expected={case.get('expected_path') or '—'}, "
            f"actual={state.get('canonical_path') or '—'}"
        ),
        status=NOT_OPENED,
        opened=False,
    )


def check_application_error_state(case, state):
    """Browser-aware application-error gate berilmagan compatibility check."""
    del case
    visible_error = clean_text(state.get("visible_error"))
    return _check_result(
        name="application_error",
        passed=not visible_error,
        reason_code="APPLICATION_ERROR",
        actual=visible_error,
        detail=f"Markaziy holat tekshiruvi [APPLICATION_ERROR]: {visible_error}",
        status=OPENED_WITH_DEFECT,
    )


def check_loader_state(case, state):
    """Browser-aware loader gate berilmagan compatibility snapshot check."""
    del case
    loader_visible = bool(state.get("loader_visible"))
    return _check_result(
        name="loader",
        passed=not loader_visible,
        reason_code="LOADER_NOT_FINISHED",
        actual=loader_visible,
        detail="Markaziy holat tekshiruvi [LOADER_NOT_FINISHED]",
        status=OPENED_WITH_DEFECT,
    )


def check_content_ready_state(case, state):
    """Browser-aware content-ready gate berilmagan compatibility check."""
    content_ready = bool(state.get("content_ready"))
    ready_note = (
        f"; required selector={case.get('ready')}"
        if case.get("ready")
        else ""
    )
    return _check_result(
        name="content_ready",
        passed=content_ready,
        reason_code="CONTENT_NOT_READY",
        expected=case.get("ready") or "generic form content",
        actual=content_ready,
        detail=f"Markaziy holat tekshiruvi [CONTENT_NOT_READY]{ready_note}",
        status=NOT_OPENED,
    )


def check_title_state(case, state):
    passed = title_matches(case, state)
    return _check_result(
        name="title",
        passed=passed,
        reason_code="TITLE_NOT_REACHED",
        expected=case.get("title") or "",
        actual=state.get("actual_title") or "",
        detail=(
            "Markaziy holat tekshiruvi [TITLE_NOT_REACHED]: "
            f"expected={case.get('title') or '—'}, "
            f"actual={state.get('actual_title') or '—'}"
        ),
        status=OPENED_WITH_DEFECT,
    )


CHECK_FUNCTIONS = {
    "url": check_url_state,
    "loader": check_loader_state,
    "application_error": check_application_error_state,
    "content_ready": check_content_ready_state,
    "title": check_title_state,
}


def _disabled_check_result(name):
    return {
        "name": name,
        "enabled": False,
        "execution_status": "DISABLED",
        "passed": None,
        "reason_code": "",
        "reason_summary": "",
        "expected": "",
        "actual": "",
        "detail": "",
        "status": "",
        "opened": False,
    }


def _not_run_check_result(name, *, blocked_by):
    return {
        "name": name,
        "enabled": True,
        "execution_status": "NOT_RUN",
        "passed": None,
        "reason_code": "",
        "reason_summary": "",
        "expected": "",
        "actual": "",
        "detail": f"'{blocked_by}' check muvaffaqiyatsiz bo'lgani uchun bajarilmadi.",
        "status": "",
        "opened": False,
        "blocked_by": blocked_by,
    }


def normalize_enabled_names(value, *, available=CHECK_NAMES, option_name="checks"):
    """``None``=all, bo'sh ro'yxat=none, ro'yxat=faqat tanlangan nomlar."""
    if value is None:
        return tuple(available)
    if not isinstance(value, list):
        raise ValueError(f"{option_name} list[str] bo'lishi kerak")
    names = list(value)
    invalid = [name for name in names if not isinstance(name, str) or not name]
    if invalid:
        raise ValueError(f"{option_name} ichida noto'g'ri nomlar: {invalid}")
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"{option_name} ichida takrorlangan nomlar: {duplicates}")
    unknown = sorted(set(names) - set(available))
    if unknown:
        raise ValueError(f"Noma'lum {option_name}: {unknown}")
    return tuple(name for name in available if name in names)


def evaluate_checks(case, state, *, enabled_names=None, precomputed_results=None, stop_after=None):
    enabled = set(normalize_enabled_names(enabled_names))
    precomputed = dict(precomputed_results or {})
    results = {}
    blocked = False
    for name in CHECK_NAMES:
        if name not in enabled:
            result = _disabled_check_result(name)
        elif blocked:
            result = _not_run_check_result(name, blocked_by=stop_after)
        elif name in precomputed:
            result = dict(precomputed[name])
        else:
            result = CHECK_FUNCTIONS[name](case, state)
        results[name] = result
        if name == stop_after and result.get("passed") is False:
            blocked = True
    return results


def primary_check_failure(check_results):
    for name in CHECK_NAMES:
        result = check_results.get(name)
        if result and result["enabled"] and result["passed"] is False:
            return result
    return None


def assert_healthy_form_state(case, state, *, enabled_names=None):
    failure = primary_check_failure(
        evaluate_checks(case, state, enabled_names=enabled_names)
    )
    if failure:
        raise AssertionError(failure["detail"])


def classify_form_failure(
    *,
    case,
    stage,
    detail,
    state,
    enabled_names=None,
    check_results=None,
):
    """Kutilgan UI exception va sahifa signallaridan QA holatini chiqaradi."""
    lower_detail = clean_text(detail).lower()

    if stage == "suite_precondition":
        lowered_operation = clean_text(case.get("failed_operation")).lower()
        if "filial" in lowered_operation or "filial" in lower_detail:
            reason_code = "FILIAL_SWITCH_FAILED"
        elif any(
            marker in lowered_operation or marker in lower_detail
            for marker in ("login", "authorization", "avtoriz")
        ):
            reason_code = "AUTHORIZATION_FAILED"
        else:
            reason_code = "PRECONDITION_FAILED"
        return {
            "status": TEST_BLOCKED,
            "reason_code": reason_code,
            "reason_summary": reason_description(reason_code),
            "opened": False,
        }

    if stage == "navigation":
        return {
            "status": NOT_OPENED,
            "reason_code": "NAVIGATION_FAILED",
            "reason_summary": reason_description("NAVIGATION_FAILED"),
            "opened": True,
        }

    results = check_results or evaluate_checks(case, state, enabled_names=enabled_names)
    failure = primary_check_failure(results)
    if failure:
        return {
            "status": failure["status"],
            "reason_code": failure["reason_code"],
            "reason_summary": failure["reason_summary"],
            "opened": failure["opened"],
        }

    return {
        "status": OPENED_WITH_DEFECT,
        "reason_code": "CONTENT_VALIDATION_FAILED",
        "reason_summary": reason_description("CONTENT_VALIDATION_FAILED"),
        "opened": True,
    }
