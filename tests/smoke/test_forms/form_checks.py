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
    "TITLE_MISMATCH": (
        "Target URLga yetildi va forma kontenti yuklandi, lekin sahifa title'i "
        "kutilgan forma nomiga mos emas."
    ),
    "CONTENT_VALIDATION_FAILED": (
        "Target URLga yetildi, lekin forma uchun belgilangan tekshiruv "
        "muvaffaqiyatli tugamadi."
    ),
    "URL_MISMATCH": "Navigatsiyadan keyin kutilgan forma o'rniga boshqa URL ochildi.",
    "NAVIGATION_FAILED": (
        "Menu, action yoki page-link bosqichida target forma URLiga o'tib bo'lmadi."
    ),
    "APPLICATION_ERROR": "Target sahifada aniq UI xato xabari ko'rindi.",
    "JS_ERROR": (
        "Forma ochilishida brauzerda JS exception yuz berdi; sahifa jim buzilgan "
        "bo'lishi mumkin."
    ),
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
    "application_error",
    "javascript",
    "loader",
    "content_ready",
    "title",
)


def reason_description(reason_code):
    return REASON_DESCRIPTIONS.get(reason_code, "")


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_allowed_warnings(value):
    if value is None:
        return []
    values = [value] if isinstance(value, str) else list(value)
    return [clean_text(item) for item in values if clean_text(item)]


def allowed_warning_text(case, state):
    visible_error = clean_text(state.get("visible_error"))
    warning_text = re.sub(r"^×\s*", "", visible_error).strip()
    if warning_text in normalize_allowed_warnings(case.get("allowed_warnings")):
        return warning_text
    return ""


def unexpected_visible_error(case, state):
    visible_error = clean_text(state.get("visible_error"))
    if visible_error and allowed_warning_text(case, state):
        return ""
    return visible_error


def path_matches(case, state):
    expected_path = (case.get("expected_path") or "").strip("/")
    actual_path = (state.get("canonical_path") or "").strip("/")
    return not expected_path or actual_path == expected_path


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
    if not title_candidates(state) and state.get("title_source") == "visible_heading":
        return False
    return True


def title_matches(case, state):
    expected_title = clean_text(case.get("title"))
    candidates = title_candidates(state)
    if not expected_title:
        return True
    if not candidates and state.get("title_source") == "visible_heading":
        return True
    if not candidates:
        candidates = [clean_text(state.get("actual_title"))]
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
        "passed": bool(passed),
        "reason_code": "" if passed else reason_code,
        "reason_summary": "" if passed else reason_description(reason_code),
        "expected": expected,
        "actual": actual,
        "detail": "" if passed else detail,
        "status": "" if passed else status,
        "opened": bool(opened),
    }


def check_url(case, state):
    passed = path_matches(case, state)
    reason_code = "URL_MISMATCH" if state.get("canonical_path") else "NAVIGATION_FAILED"
    return _check_result(
        name="url",
        passed=passed,
        reason_code=reason_code,
        expected=case.get("expected_path") or "",
        actual=state.get("canonical_path") or "",
        detail=(
            "Markaziy holat tekshiruvi [URL_MISMATCH]: "
            f"expected={case.get('expected_path') or '—'}, "
            f"actual={state.get('canonical_path') or '—'}"
        ),
        status=NOT_OPENED,
        opened=False,
    )


def check_application_error(case, state):
    visible_error = unexpected_visible_error(case, state)
    return _check_result(
        name="application_error",
        passed=not visible_error,
        reason_code="APPLICATION_ERROR",
        actual=visible_error,
        detail=f"Markaziy holat tekshiruvi [APPLICATION_ERROR]: {visible_error}",
        status=OPENED_WITH_DEFECT,
    )


def check_javascript(case, state):
    del case
    js_errors = list(state.get("js_errors") or [])
    return _check_result(
        name="javascript",
        passed=not js_errors,
        reason_code="JS_ERROR",
        actual=list(js_errors),
        detail=(
            f"Markaziy holat tekshiruvi [JS_ERROR] ({len(js_errors)}): "
            f"{'; '.join(js_errors)}"
        ),
        status=OPENED_WITH_DEFECT,
    )


def check_loader(case, state):
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


def check_content_ready(case, state):
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


def check_title(case, state):
    passed = title_matches(case, state)
    return _check_result(
        name="title",
        passed=passed,
        reason_code="TITLE_MISMATCH",
        expected=case.get("title") or "",
        actual=state.get("actual_title") or "",
        detail=(
            "Markaziy holat tekshiruvi [TITLE_MISMATCH]: "
            f"expected={case.get('title') or '—'}, "
            f"actual={state.get('actual_title') or '—'}"
        ),
        status=OPENED_WITH_DEFECT,
    )


CHECK_FUNCTIONS = {
    "url": check_url,
    "application_error": check_application_error,
    "javascript": check_javascript,
    "loader": check_loader,
    "content_ready": check_content_ready,
    "title": check_title,
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


def evaluate_checks(case, state, *, enabled_names=None):
    enabled = set(normalize_enabled_names(enabled_names))
    return {
        name: (
            CHECK_FUNCTIONS[name](case, state)
            if name in enabled
            else {
                "name": name,
                "enabled": False,
                "passed": None,
                "reason_code": "",
                "reason_summary": "",
                "expected": "",
                "actual": "",
                "detail": "",
                "status": "",
                "opened": False,
            }
        )
        for name in CHECK_NAMES
    }


def primary_check_failure(check_results):
    for name in CHECK_NAMES:
        result = check_results.get(name)
        if result and result["enabled"] and not result["passed"]:
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

    results = check_results or evaluate_checks(
        case,
        state,
        enabled_names=enabled_names,
    )
    failure = primary_check_failure(results)
    if failure:
        return {
            "status": failure["status"],
            "reason_code": failure["reason_code"],
            "reason_summary": failure["reason_summary"],
            "opened": failure["opened"],
        }

    if stage == "navigation":
        return {
            "status": NOT_OPENED,
            "reason_code": "NAVIGATION_FAILED",
            "reason_summary": reason_description("NAVIGATION_FAILED"),
            "opened": True,
        }

    return {
        "status": OPENED_WITH_DEFECT,
        "reason_code": "CONTENT_VALIDATION_FAILED",
        "reason_summary": reason_description("CONTENT_VALIDATION_FAILED"),
        "opened": True,
    }
