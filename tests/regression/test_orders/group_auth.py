"""One UI login per Order group; each case still owns its context and trace.

Authentication snapshots live only in memory, never in run artifacts. Business
data and retry journals are not copied or replayed by this module.
"""
from copy import deepcopy
import json
import re
from time import monotonic
from urllib.parse import urlsplit

import allure
from playwright.sync_api import expect

from tests.regression.environment import RegressionEnvironmentError, authorization
from tests.regression.test_orders.auth_recovery import _record, verify_license
from tests.shared.authorization import dashboard, install_announcement_handler
from utils.base_pages.page_reporting import capture_filial
from utils.report_context import page_context


def _identity(baseline):
    return tuple(str(baseline[key]).rstrip('/') for key in ('url', 'company_code', 'user_id', 'code', 'filial_id'))


class GroupLogin:
    def __init__(self, baseline):
        self.identity = _identity(baseline)
        self.storage = None
        self.session_storage = {}
        self.dashboard_url = None
        self.company_id = None
        self.metadata = {}

    def snapshot(self):
        return deepcopy(self.storage)

    def clear(self):
        self.storage = None
        self.session_storage = {}
        self.dashboard_url = None
        self.metadata = {}

    def _session(self, page, baseline):
        response = page.request.post(baseline['url'].rstrip('/') + '/b/biruni/m:session', data={}, headers={'X-Requested-With': 'XMLHttpRequest', 'lang_code': 'ru'}, timeout=30_000)
        try:
            if response.status == 401:
                return None
            if response.status != 200:
                raise RegressionEnvironmentError(f'Sessiyani tekshirish HTTP {response.status} bilan tugadi')
            try:
                data = response.json()
            except ValueError:
                raise RegressionEnvironmentError('Sessiyani tekshirish javobi JSON emas') from None
            if not isinstance(data, dict) or not isinstance(data.get('user'), dict):
                raise RegressionEnvironmentError('Sessiya javobining formati kutilganiga mos emas')
            if not data['user'].get('user_id'):
                return None
            if str(data['user']['user_id']) != str(baseline['user_id']):
                self.clear()
                raise RegressionEnvironmentError('Saqlangan sessiyadagi user test useriga mos emas')
            company = data.get('company_id')
            if company is None or (self.company_id is not None and str(company) != self.company_id):
                self.clear()
                raise RegressionEnvironmentError('Saqlangan sessiyadagi kompaniya dastlabki loginga mos emas')
            projects = data.get('projects', [])
            filials = {str(f[0]) for p in projects for f in p.get('filials', []) if f}
            if str(baseline['filial_id']) not in filials:
                self.clear()
                raise RegressionEnvironmentError('Test filiali saqlangan sessiyada mavjud emas')
            return str(company)
        finally:
            response.dispose()

    def _filial(self, page, baseline):
        name = re.escape(str(baseline['filial_name']))
        expect(page.locator('header').get_by_role('button', name=re.compile(r'^\s*(?:TRADE|SFA)\s*' + name + r'\s*$', re.I))).to_be_visible(timeout=30_000)
        page_context(page)['filial'] = ''
        capture_filial(page)

    def refresh_cookies(self, page):
        """Renew auth only; never propagate a mid-test draft or changed settings."""
        if self.storage is not None:
            self.storage['cookies'] = deepcopy(page.context.cookies())

    def authorize(self, page, baseline, directory):
        if _identity(baseline) != self.identity:
            raise RegressionEnvironmentError('Guruh login konteksti server/user/filialga mos emas')
        started = monotonic()
        reused = self.storage is not None
        mode = 'reused' if reused else 'first_login'
        with allure.step('Guruh sessiyasini yangi test oynasida tekshirish' if reused else 'Guruh uchun bir marta UI login'):
            if reused:
                # Only the pristine post-login sessionStorage is installed, and
                # only for the original origin. No business-form state is saved.
                company = self._session(page, baseline)
                if company is None:
                    self.clear()
                    mode = 'expired_login'
                    _record(directory, {'kind': 'group_login', 'status': 'expired', 'business_requests_replayed': 0})
                    verify_license(baseline, directory)
                else:
                    if self.session_storage:
                        origin = urlsplit(self.dashboard_url)
                        payload = json.dumps({'origin': f'{origin.scheme}://{origin.netloc}', 'values': self.session_storage})
                        page.add_init_script('(() => { const seed = ' + payload + '; if (window === window.top && location.origin === seed.origin && !sessionStorage.getItem("__pw_order_login_seeded")) { for (const [k,v] of Object.entries(seed.values)) sessionStorage.setItem(k,v); sessionStorage.setItem("__pw_order_login_seeded","1"); } })();')
                    install_announcement_handler(page)
                    page_context(page).update(self.metadata, authorization='Guruh sessiyasi qayta tasdiqlangan')
                    page.goto(self.dashboard_url)
                    page.wait_for_url(re.compile(r'dashboard|/auth/login(?:[?#]|$)|/login\.html'), timeout=30_000)
                    if 'dashboard' not in page.url:
                        self.clear()
                        mode = 'expired_login'
                        _record(directory, {'kind': 'group_login', 'status': 'expired_on_navigation', 'business_requests_replayed': 0})
                        verify_license(baseline, directory)
                    else:
                        dashboard(page)
                        self._filial(page, baseline)
                        self.refresh_cookies(page)
            if self.storage is None:
                authorization(page, who='user', code=str(baseline['code']))
                company = self._session(page, baseline)
                if company is None:
                    raise RegressionEnvironmentError('UI logindan keyin sessiya tasdiqlanmadi')
                self._filial(page, baseline)
                self.company_id = company
                self.dashboard_url = page.url
                self.session_storage = page.evaluate('() => Object.fromEntries(Object.entries(sessionStorage).filter(([key]) => key !== "__pw_order_login_seeded"))')
                self.storage = page.context.storage_state()
                context = page_context(page)
                self.metadata = {key: context.get(key, '') for key in ('server', 'company', 'profile', 'code')}
                self.metadata['authenticated_user_id'] = str(baseline['user_id'])
        _record(directory, {'kind': 'group_login', 'status': 'ready', 'mode': mode, 'duration_seconds': round(monotonic() - started, 3), 'business_requests_replayed': 0})
