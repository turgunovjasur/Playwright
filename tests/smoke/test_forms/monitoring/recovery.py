"""Canonical Forms runner uchun fail-closed recovery policy."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Any, TypeVar
from urllib.parse import urlsplit

import allure
from playwright.sync_api import Page

from tests.smoke import smoke_reporting
from tests.smoke.flows.flow_authorization import authorization


T = TypeVar("T")
RecoveryDetails = dict[str, Any]
RecoveryMatcher = Callable[
    ["FormRecoveryContext", Exception],
    RecoveryDetails | None,
]
RecoveryAction = Callable[["FormRecoveryContext", Mapping[str, Any]], None]


@dataclass
class FormRecoveryContext:
    """Recovery matcher va actionlari ishlatadigan joriy forma konteksti."""

    page: Page
    item: Any
    session_state: MutableMapping[str, Any]
    form_case: Mapping[str, Any]


@dataclass(frozen=True)
class FormRecoveryRule:
    """Aniq recoverable signalni unga mos tiklash amali bilan bog'laydi."""

    name: str
    matches: RecoveryMatcher
    recover: RecoveryAction


def _is_login_redirect(page: Page) -> bool:
    try:
        return urlsplit(str(page.url or "")).path.endswith("/login.html")
    except (AttributeError, TypeError, ValueError):
        return False


def _session_unauthorized_match(
    context: FormRecoveryContext,
    error: Exception,
) -> RecoveryDetails | None:
    diagnostic = smoke_reporting.auth_diagnostic_for_item(context.item)
    if diagnostic and diagnostic.get("status") == 401:
        return {
            **diagnostic,
            "rule": "session_unauthorized",
            "original_error_type": type(error).__name__,
        }

    if _is_login_redirect(context.page):
        return {
            "rule": "session_unauthorized",
            "kind": "login_redirect",
            "error_type": "AuthSessionUnauthorized",
            "status": None,
            "ui_state": "login_redirect",
            "summary": "UI login sahifasiga redirect bo'ldi",
            "original_error_type": type(error).__name__,
        }

    return None


def _recover_admin_session(
    context: FormRecoveryContext,
    _details: Mapping[str, Any],
) -> None:
    context.session_state["current_filial"] = None
    smoke_reporting.reset_auth_diagnostics(context.item)
    with allure.step(
        "Recovery | Admin authorizationni yangilash va filial state'ni tozalash"
    ):
        authorization(context.page, who="admin")


FORM_RECOVERY_RULES = (
    FormRecoveryRule(
        name="session_unauthorized",
        matches=_session_unauthorized_match,
        recover=_recover_admin_session,
    ),
)


def _matching_rule(
    rules: Sequence[FormRecoveryRule],
    context: FormRecoveryContext,
    error: Exception,
) -> tuple[FormRecoveryRule, RecoveryDetails] | None:
    for rule in rules:
        details = rule.matches(context, error)
        if details is not None:
            return rule, details
    return None


def run_with_form_recovery(
    action: Callable[[], T],
    *,
    context: FormRecoveryContext,
    rules: Sequence[FormRecoveryRule] = FORM_RECOVERY_RULES,
    max_attempts: int = 2,
) -> T:
    """Actionni bounded retry bilan bajaradi; noma'lum xatoni retry qilmaydi."""
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
        raise TypeError("max_attempts int bo'lishi kerak")
    if max_attempts < 1:
        raise ValueError("max_attempts kamida 1 bo'lishi kerak")

    for attempt_number in range(1, max_attempts + 1):
        try:
            with allure.step(
                f"Forma urinish | {attempt_number}/{max_attempts} | "
                f"{context.form_case['label']}"
            ):
                return action()
        except Exception as error:
            if attempt_number == max_attempts:
                raise

            match = _matching_rule(rules, context, error)
            if match is None:
                raise

            rule, details = match
            allure.attach(
                json.dumps(details, ensure_ascii=False, indent=2),
                name=(
                    f"Recovery qarori | {rule.name} | "
                    f"{context.form_case['label']}"
                ),
                attachment_type=allure.attachment_type.JSON,
            )
            rule.recover(context, details)

    raise RuntimeError("Form recovery urinishlari kutilmaganda yakunlandi")
