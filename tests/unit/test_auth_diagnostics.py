from tests.smoke import smoke_reporting
from tests.smoke.test_setup import test_change_password


class _FakeRequest:
    method = "POST"


class _FakeResponse:
    def __init__(self, *, status, url, body=""):
        self.status = status
        self.url = url
        self.request = _FakeRequest()
        self._body = body

    def text(self):
        return self._body


class _FakeLocator:
    def __init__(self, visible):
        self._visible = visible

    @property
    def first(self):
        return self

    def is_visible(self):
        return self._visible


class _FakePage:
    def __init__(self, *, url="https://smartup.online/#/dashboard", lock=False):
        self.url = url
        self._lock = lock
        self._listeners = {}

    def on(self, event, callback):
        self._listeners[event] = callback

    def emit_response(self, response):
        self._listeners["response"](response)

    def locator(self, selector):
        assert selector == "#closing-session .cs-lock.open"
        return _FakeLocator(self._lock)


class _FakeItem:
    def __init__(self, page):
        self.funcargs = {"session_page": page}


def test_license_401_is_reported_with_safe_request_and_lock_state():
    page = _FakePage(lock=True)
    item = _FakeItem(page)
    smoke_reporting.install_auth_diagnostics(page)

    page.emit_response(
        _FakeResponse(
            status=200,
            url="https://smartup.online/b/anor/mkr/price_type+add:model",
        )
    )
    page.emit_response(
        _FakeResponse(
            status=401,
            url="https://third-party.example/widget",
            body="unrelated unauthorized",
        )
    )
    page.emit_response(
        _FakeResponse(
            status=401,
            url=(
                "https://smartup.online/b/anor/mkr/price_type+add:model"
                "?password=must-not-leak"
            ),
            body="Нет лицензии для входа в систему!",
        )
    )

    diagnostic = smoke_reporting.auth_diagnostic_for_item(item)

    assert diagnostic == {
        "kind": "license_session_unauthorized",
        "error_type": "LicenseSessionUnauthorized",
        "method": "POST",
        "path": "/b/anor/mkr/price_type+add:model",
        "status": 401,
        "server_message": "Нет лицензии для входа в систему!",
        "ui_state": "session_lock",
        "summary": (
            "Backend license/session kirishini rad etdi: "
            "POST /b/anor/mkr/price_type+add:model → HTTP 401; "
            'server="Нет лицензии для входа в систему!"; '
            "UI=qayta login lock oynasi"
        ),
    }
    assert "must-not-leak" not in diagnostic["summary"]

    smoke_reporting.reset_auth_diagnostics(item)
    assert smoke_reporting.auth_diagnostic_for_item(item) is None


def test_unknown_401_body_is_not_exposed():
    page = _FakePage(url="https://smartup.online/login.html")
    item = _FakeItem(page)
    smoke_reporting.install_auth_diagnostics(page)
    page.emit_response(
        _FakeResponse(
            status=401,
            url="https://smartup.online/b/example:model?token=must-not-leak",
            body="token=must-not-leak user@example.com",
        )
    )

    diagnostic = smoke_reporting.auth_diagnostic_for_item(item)

    assert diagnostic["error_type"] == "AuthSessionUnauthorized"
    assert diagnostic["path"] == "/b/example:model"
    assert diagnostic["server_message"] == ""
    assert diagnostic["ui_state"] == "login_redirect"
    assert "must-not-leak" not in diagnostic["summary"]
    assert "user@example.com" not in diagnostic["summary"]


def test_change_password_requires_fresh_login_and_dashboard(monkeypatch):
    events = []

    class FakeBasePage:
        def __init__(self, page):
            self.page = page

        def text(self, **kwargs):
            events.append(("force-change", kwargs))

        def input(self, **kwargs):
            events.append(("input", kwargs["label"]))

        def confirm_biruni(self):
            events.append(("confirm",))

    class FakeButton:
        def click(self):
            events.append(("submit",))

    class FakePasswordPage:
        def get_by_role(self, role, name):
            assert (role, name) == ("button", "Подтвердить")
            return FakeButton()

    def fake_login(page, *, email, password):
        events.append(("login", email, password))

    def fake_dashboard(page):
        events.append(("dashboard",))

    monkeypatch.setattr(test_change_password, "BasePage", FakeBasePage)
    monkeypatch.setattr(test_change_password, "login", fake_login)
    monkeypatch.setattr(test_change_password, "dashboard", fake_dashboard)
    monkeypatch.setattr(
        test_change_password,
        "user_email_for",
        lambda code: f"user-pw{code}@company",
    )

    test_change_password.run_change_password(FakePasswordPage(), "900184")

    login_events = [event for event in events if event[0] == "login"]
    assert len(login_events) == 2
    assert login_events[0] == login_events[1]
    assert events[-2:] == [login_events[1], ("dashboard",)]
