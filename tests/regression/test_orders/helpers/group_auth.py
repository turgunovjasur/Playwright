"""One UI login per Order group; each case still owns its context and trace.

Authentication snapshots live only in memory, never in run artifacts. Business
data and retry journals are not copied or replayed by this module.
"""
from copy import deepcopy
from functools import partial
import json
import re
from time import monotonic
from urllib.parse import urlsplit

import allure
from playwright.sync_api import expect

from tests.regression.helpers.environment import RegressionEnvironmentError, authorization
from tests.regression.test_orders.helpers.auth_recovery import _record, verify_license
from tests.shared.authorization import dashboard, install_announcement_handler
from utils.base_pages import A2_DOCUMENT_TIMEOUT_MS, UI_TIMEOUT_MS
from utils.base_pages.page_errors import load_a2_document
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
        response = page.request.post(baseline['url'].rstrip('/') + '/b/biruni/m:session', data={}, headers={'X-Requested-With': 'XMLHttpRequest', 'lang_code': 'ru'}, timeout=30_000, max_retries=1)
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
        expect(page.locator('header').get_by_role('button', name=re.compile(r'^\s*(?:TRADE|SFA)\s*' + name + r'\s*$', re.I))).to_be_visible(timeout=UI_TIMEOUT_MS)
        page_context(page)['filial'] = ''
        capture_filial(page)

    def refresh_cookies(self, page):
        """Renew auth only; never propagate a mid-test draft or changed settings."""
        if self.storage is not None:
            self.storage['cookies'] = deepcopy(page.context.cookies())

    def prepare_page(self, page, baseline, directory):
        if self.storage is None:
            self.authorize(page, baseline, directory)
        else:
            # The flow installs response listeners before requesting its first page.
            page._order_first_navigation = partial(self.authorize, baseline=baseline, directory=directory)

    def authorize(self, page, baseline, directory, *, order_entry=None):
        if _identity(baseline) != self.identity:
            raise RegressionEnvironmentError('Guruh login konteksti server/user/filialga mos emas')
        survey = page.get_by_role('dialog').filter(
            has=page.get_by_role('heading', name='NPS Survey', exact=True)
        )
        page.add_locator_handler(
            survey, lambda dialog: dialog.get_by_role('button', name='Закрыть', exact=True).click()
        )
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
                    destination = self.dashboard_url
                    if order_entry:
                        target = urlsplit(order_entry)
                        if (target.scheme or target.netloc or target.fragment or not target.path
                                or target.path.startswith("/") or ".." in target.path.split("/")):
                            raise ValueError("Order sahifasi uchun relative A2 route kerak")
                        destination = self.dashboard_url.split('/a2/', 1)[0] + '/a2/' + order_entry
                        load_a2_document(page, destination, A2_DOCUMENT_TIMEOUT_MS)
                        # A2 can redirect to login after the document has loaded.
                        ready = page.locator('header').get_by_role('button', name=re.compile(r'^\s*(?:TRADE|SFA)\s+', re.I))
                        login_form = page.get_by_label('Логин', exact=True).or_(page.get_by_placeholder('Логин@компания', exact=True))
                        expect(ready.or_(login_form).first).to_be_visible(timeout=A2_DOCUMENT_TIMEOUT_MS)
                    else:
                        page.goto(destination, wait_until="domcontentloaded", timeout=A2_DOCUMENT_TIMEOUT_MS)
                        page.wait_for_url(re.compile(r'dashboard|/auth/login(?:[?#]|$)|/login\.html'),
                                          wait_until='domcontentloaded', timeout=UI_TIMEOUT_MS)
                    if re.search(r'/auth/login(?:[?#]|$)|/login\.html', page.url):
                        self.clear()
                        mode = 'expired_login'
                        _record(directory, {'kind': 'group_login', 'status': 'expired_on_navigation', 'business_requests_replayed': 0})
                        verify_license(baseline, directory)
                    else:
                        if order_entry:
                            expect(page).to_have_url(destination, timeout=UI_TIMEOUT_MS)
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
                self.metadata = {key: context.get(key, '') for key in ('server', 'company', 'profile', 'code', 'login', 'password')}
                self.metadata['authenticated_user_id'] = str(baseline['user_id'])
        opened = order_entry if mode == 'reused' else None
        _record(directory, {'kind': 'group_login', 'status': 'ready', 'mode': mode,
                            'direct_order_entry': bool(opened), 'duration_seconds': round(monotonic() - started, 3),
                            'business_requests_replayed': 0})
        return opened
