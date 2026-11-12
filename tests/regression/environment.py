"""Explicit shared-environment failures; ordinary UI/business failures stay local."""

from urllib.parse import unquote, urlsplit


class RegressionEnvironmentError(RuntimeError):
    """Evidence shows the shared baseline/authentication cannot be used."""


def environment_failure(error):
    # Recovery/fixture teardown may wrap the original typed failure.
    pending, seen = [error], set()
    while pending:
        current = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, RegressionEnvironmentError):
            return current
        pending.extend((current.__cause__, current.__context__))
    return None


def classify_login_error(error):
    # Match the authentication endpoint only. A business HTTP 401 or a loader
    # timeout does not prove that the whole environment is unavailable.
    if str(error) in {
        "POST biruni/s$log_in: HTTP 401",
        "POST biruni/s$log_in: HTTP 403",
        "POST biruni/s$log_in: HTTP 401 (Нет лицензии для входа в систему!)",
        "Login did not produce an authenticated Biruni session",
    }:
        raise RegressionEnvironmentError("API login rad etildi yoki autentifikatsiyalangan sessiya yaratilmagan") from error


def authorization(page, *, who, code=None):
    """Keep shared login intact; only a proven login rejection blocks all groups."""
    from tests.shared.authorization import authorization as shared_authorization

    login_status = None

    def capture(response):
        nonlocal login_status
        if (response.request.method == "POST"
                and unquote(urlsplit(response.url).path).endswith("/biruni/s$log_in")):
            login_status = response.status

    page.on("response", capture)
    try:
        shared_authorization(page, who=who, code=code)
    except Exception as error:
        if login_status in (401, 403):
            raise RegressionEnvironmentError(f"UI login HTTP {login_status} bilan rad etildi") from error
        raise
    finally:
        page.remove_listener("response", capture)
