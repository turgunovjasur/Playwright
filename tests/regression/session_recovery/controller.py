"""One A2 reauthentication owner per regression page, independent of testcase."""
from contextlib import contextmanager
import sys
from urllib.parse import urlsplit
from weakref import WeakKeyDictionary

import allure
from playwright.sync_api import expect

from .reads import ReadRequest, SessionRecoveryError, prepare_resume
from tests.regression.environment import RegressionEnvironmentError


ACTIVE_SESSIONS = WeakKeyDictionary()
AUTH_TIMEOUT = 30_000


def _draft_values(page):
    # Values are compared only in memory, never written to Allure/logs. Exclude
    # the password modal and file inputs. This does not read Angular internals.
    return page.locator('main input:not([type="password"]):not([type="file"]), main textarea, main select').evaluate_all(
        "elements => elements.map(e => ({name:e.name, type:e.type, value:e.value, checked:e.checked, disabled:e.disabled}))"
    )


class SessionRecovery:
    def __init__(self, page, *, server, user_id, display_name, password, verify_license, record, max_attempts=1, on_authenticated=None):
        self.page = page
        self.origin = urlsplit(server)
        self.server = server.rstrip('/')
        self.user_id = str(user_id)
        self.display_name = display_name
        self.password_value = password  # Callable; credentials never enter events.
        self.verify_license = verify_license
        self.record = record
        self.on_authenticated = on_authenticated
        self.max_attempts = max_attempts
        self.attempts = 0
        self.lookup = None
        self.grid_settings = None
        self.rejected = []
        self.successful = set()
        self.failure = None
        self.recovering = False
        self.lock = page.locator('app-session-lock')
        self.password_input = self.lock.get_by_placeholder('Пароль', exact=True)

    def capture(self, response):
        address = urlsplit(response.url)
        if (address.scheme, address.netloc) != (self.origin.scheme, self.origin.netloc):
            return
        # No UI actions, API calls, or credential payload inspection in listener.
        if response.status == 401:
            self.rejected.append(response)
        elif self.recovering and response.status == 200 and '/biruni/s$log_in' not in address.path:
            self.successful.add(ReadRequest.from_response(response))

    def event(self, status, **details):
        self.record({'kind': 'ui_session_lock', 'status': status,
                     'attempt': self.attempts, 'business_requests_replayed': 0, **details})

    def unlock(self, _locator):
        if self.failure is not None:
            raise self.failure
        try:
            self.recover()
        except Exception as error:
            self.failure = SessionRecoveryError(
                'Sessiyani tiklash yakunlanmadi: ' +
                (str(error) if isinstance(error, SessionRecoveryError) else type(error).__name__)
            )
            self.event('failed', error_type=type(error).__name__, stage=getattr(self, 'stage', 'authentication'))
            raise self.failure from error

    def recover(self):
        self.attempts += 1
        if self.recovering or self.attempts > self.max_attempts:
            raise SessionRecoveryError('Shu testdagi qayta kirish urinishlari limiti tugadi')
        self.recovering = True
        self.successful.clear()
        batch = tuple(self.rejected)
        before_url = self.page.url
        self.stage = 'identify_modal'
        self.event('observed', paths=sorted({urlsplit(r.url).path for r in batch}), idle_lock=not batch)
        expect(self.lock).to_have_count(1)
        expect(self.lock.get_by_text(self.display_name, exact=True)).to_be_visible()
        before_values = _draft_values(self.page)
        plan_error = None
        try:
            plan = prepare_resume(self.page, batch, self.lookup, self.grid_settings)
        except SessionRecoveryError as error:
            plan_error = error
            plan = None
        self.stage = 'license'
        self.verify_license()
        self.stage = 'authentication'
        with allure.step('Sessiya oynasi: ayni foydalanuvchi parolini qayta tasdiqlash'):
            self.stage = 'password_fill'
            self.password_input.fill(self.password_value(), timeout=AUTH_TIMEOUT)
            self.stage = 'login_submit'
            login_path = self.origin.path.rstrip('/') + '/b/biruni/s$log_in'
            def is_login(response):
                address = urlsplit(response.url)
                return (address.scheme, address.netloc) == (self.origin.scheme, self.origin.netloc) and address.path == login_path and response.request.method == 'POST'
            # Wait for authentication itself, never for an assumed read replay.
            with self.page.expect_response(is_login, timeout=AUTH_TIMEOUT) as login:
                self.lock.get_by_role('button', name='Войти', exact=True).click(timeout=AUTH_TIMEOUT)
            if login.value.status in (401, 403):
                raise RegressionEnvironmentError(f"Sessiya parolini tasdiqlash HTTP {login.value.status} bilan rad etildi")
            if login.value.status != 200:
                raise SessionRecoveryError(f'Parol tasdig‘i HTTP {login.value.status} bilan tugadi')
            expect(self.password_input).to_be_hidden(timeout=AUTH_TIMEOUT)
            if self.page.url != before_url:
                raise SessionRecoveryError('Qayta kirishda sahifa o‘zgardi; test davom ettirilmadi')
            session = self.page.request.post(self.server + '/b/biruni/m:session', data={},
                headers={'X-Requested-With': 'XMLHttpRequest', 'lang_code': 'ru'}, timeout=AUTH_TIMEOUT)
            if session.status != 200:
                raise SessionRecoveryError('Qayta kirgan foydalanuvchi tasdiqlanmadi')
            if str(session.json().get('user', {}).get('user_id')) != self.user_id:
                raise RegressionEnvironmentError('Qayta kirgan user API setup useriga mos emas')
            if (plan is None or plan.kind != 'model') and _draft_values(self.page) != before_values:
                raise SessionRecoveryError('Qayta kirishda formadagi qiymatlar o‘zgardi')
        # Initial model retry legitimately populates previously empty controls.
        # It still requires exact route/request200 and the test's form assertions.
        if self.on_authenticated is not None:
            self.on_authenticated()
        self.event('authenticated')
        if plan_error is not None:
            raise plan_error
        self.stage = 'resume_read'
        with allure.step('Uzilgan o‘qishni tiklash va ayni qadamdan davom etish'):
            plan.run(self.page, self.successful, AUTH_TIMEOUT)
            if plan.kind == 'lookup' and _draft_values(self.page) != before_values:
                raise SessionRecoveryError('Qidiruvni tiklashda formadagi qiymatlar o‘zgardi')
        # A second denial during login/reload must not disappear in clear().
        if len(self.rejected) != len(batch):
            raise SessionRecoveryError('Qayta kirish yoki o‘qishni tiklash vaqtida yana 401 qaytdi')
        if self.page.url != before_url:
            raise SessionRecoveryError('O‘qishni tiklashda sahifa o‘zgardi')
        del self.rejected[:len(batch)]
        self.recovering = False
        self.event('recovered', user_id=self.user_id, resumed_read=plan.kind)


@contextmanager
def recover_session(page, **options):
    """Attach before test login and detach after all business steps."""
    if page in ACTIVE_SESSIONS:
        raise SessionRecoveryError('Sahifaga sessiya kuzatuvchisi ikki marta ulanmoqda')
    controller = SessionRecovery(page, **options)
    ACTIVE_SESSIONS[page] = controller
    listening = handling = False
    try:
        page.on('response', controller.capture)
        listening = True
        page.add_locator_handler(controller.password_input, controller.unlock)
        handling = True
        try:
            yield controller
        except Exception as error:
            # Playwright can mask handler exceptions behind a locator timeout.
            if controller.failure is not None:
                raise controller.failure from error
            raise
        if controller.failure is not None:
            raise controller.failure
    finally:
        already_failed = sys.exc_info()[0] is not None
        ACTIVE_SESSIONS.pop(page, None)
        try:
            if listening:
                page.remove_listener('response', controller.capture)
            if handling and not page.is_closed():
                page.remove_locator_handler(controller.password_input)
        except Exception:
            if not already_failed:
                raise
