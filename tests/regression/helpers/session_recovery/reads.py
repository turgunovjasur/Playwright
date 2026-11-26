"""Known A2 read resumptions. Never send a business request from recovery."""
from contextlib import ExitStack
from dataclasses import dataclass, field
import json
from urllib.parse import unquote, urlsplit

from playwright.sync_api import expect

from utils.base_pages.auto_base_page import AutoBasePage
from utils.base_pages.angular_base_page import _lookup_query_finished
from utils.base_pages.angular_page_errors import watch_errors


class SessionRecoveryError(RuntimeError):
    """Authentication/read recovery failed; the testcase must remain failed."""


ORDER_EDIT_QUANTITY = '/b/anor/mdeal/order/order+edit:get_box_quant'
ORDER_ADD_PERSONS = '/b/anor/mdeal/order/order+add:persons'
SURVEY_DATA = '/b/trade/tr/plugin:get_survey_data'


def observed_form_read(path):
    return path.endswith((ORDER_EDIT_QUANTITY, ORDER_ADD_PERSONS, SURVEY_DATA))


@dataclass(frozen=True)
class ReadRequest:
    method: str
    path: str
    url: str = field(repr=False)
    payload: str = field(repr=False)

    @classmethod
    def from_response(cls, response):
        request = response.request
        try:
            value = request.post_data_json if request.post_data else None
        except (TypeError, ValueError):
            value = {"unparsed": request.post_data}
        return cls(request.method, urlsplit(response.url).path, response.url,
                   json.dumps(value, sort_keys=True, ensure_ascii=False))

    def matches(self, response):
        return response.status == 200 and self == self.from_response(response)

    def resolved_by(self, completed):
        if self == completed:
            return True
        if not unquote(self.path).endswith(ORDER_EDIT_QUANTITY) or self.url != completed.url:
            return False
        # Clearing the quantity briefly requests zero before the typed value.
        # Only a later positive quantity for the very same line supersedes it.
        before, after = json.loads(self.payload), json.loads(completed.payload)
        fields = {'deal_id', 'modified_id', 'product_id', 'quant'}
        if not all(isinstance(body, dict) and set(body) == fields for body in (before, after)):
            return False
        quantity = str(after['quant'])
        return (before['quant'] == '0' and quantity.isascii() and quantity.isdigit()
                and int(quantity) > 0
                and all(before[k] == after[k] for k in fields - {'quant'}))


@dataclass
class LookupContext:
    input: object
    key_field: str


@dataclass
class GridSettingsContext:
    menu_name: str
    field_name: str
    search_name: str | None
    menu_open_count: int = 0


def _layout_preference(request, page_url, settings):
    """Only the observed column-save → search-menu transition, not arbitrary writes."""
    if settings is None or settings.search_name is None or settings.menu_open_count != 2:
        return False
    if not request.path.endswith('/b/biruni/m:save_user_large_setting'):
        return False
    data = json.loads(request.payload)
    route = unquote(urlsplit(page_url).path).split('/a2/', 1)[-1]
    if not isinstance(data, dict) or set(data) != {'setting_code', 'setting_value'}:
        return False
    if data['setting_code'] != '/' + route + ':table':
        return False
    try:
        value = json.loads(data['setting_value'])
    except (ValueError, TypeError):
        return False
    allowed = {'openFilterPanel', 'filterPanelDirection', 'filterPanelWidth', 'cols', 'search'}
    return (isinstance(value, dict) and set(value) <= allowed
            and isinstance(value.get('cols'), list) and isinstance(value.get('search'), list)
            and all(isinstance(c, dict) and set(c) <= {'name', 'size'} for c in value['cols'])
            and all(isinstance(c, str) for c in value['search']))


def _preference_read(request, page_url):
    if not request.path.endswith('/b/biruni/m:load_user_large_setting'):
        return False
    # A visible list can continue with its default layout/sort. Match both
    # its current route and the exact preference being read.
    _, separator, route = unquote(urlsplit(page_url).path).rpartition('/a2/')
    preferences = {
        'anor/mdeal/order/offset/offset_detail_list': (':table', ':table&sort', ':table&filter'),
        'anor/mdeal/return/return_reason_list': (':table',),
        'trade/tcs/cashin_list': (':table&sort',),
    }
    if not separator or route not in preferences:
        return False
    data = json.loads(request.payload)
    codes = {'/' + route + suffix for suffix in preferences[route]}
    return isinstance(data, dict) and set(data) == {'setting_code'} and data['setting_code'] in codes


def _table_query(request):
    data = json.loads(request.payload)
    params = data.get('p', data) if isinstance(data, dict) else None
    return isinstance(params, dict) and isinstance(params.get('column'), list)


def pending_list_destination(page_url, responses):
    """During A2 navigation the destination's model can fail before the URL changes."""
    current = urlsplit(page_url)
    prefix, marker, _ = current.path.partition('/a2/')
    if not marker or not current.path.endswith('_list') or len(responses) != 1:
        return page_url
    request = ReadRequest.from_response(responses[0])
    target = urlsplit(request.url)
    api_root = prefix + '/b/'
    if ((current.scheme, current.netloc) != (target.scheme, target.netloc)
            or target.query or request.method != 'POST' or request.payload != '{}'
            or not target.path.startswith(api_root) or not target.path.endswith('_list:model')):
        return page_url
    path = prefix + '/a2/' + target.path[len(api_root):].removesuffix(':model')
    if path == current.path:
        return page_url
    return current._replace(path=path, query='', fragment='').geturl()


@dataclass
class ResumeRead:
    kind: str
    request: ReadRequest | None = None
    lookup: LookupContext | None = None
    settings: GridSettingsContext | None = None
    query: str | None = field(default=None, repr=False)
    started_at: float = 0
    list_requests: tuple[ReadRequest, ...] = ()

    def run(self, page, successful, timeout, completed_forms):
        if self.kind == 'list_reload':
            if all(request in successful for request in self.list_requests):
                return
            # Reopen only the current list document via GET. The application
            # must issue and consume its own reads; never replay a stored POST.
            if page.locator('[role="dialog"]:visible, [role="menu"]:visible').count():
                raise SessionRecoveryError('Ochiq dialog yoki menyuli ro‘yxat qayta yuklanmadi')
            with ExitStack() as stack:
                pending = [stack.enter_context(page.expect_response(req.matches, timeout=timeout))
                           for req in self.list_requests]
                page.goto(page.url, wait_until='domcontentloaded', timeout=timeout)
            for read in pending:
                read.value.finished()
            if getattr(page, '_smartup_watching_page_errors', False):
                watch_errors(page)
            expect(page.locator('smt-data-table:visible')).to_have_count(1, timeout=timeout)
            return
        if self.request is None:
            return
        if self.kind == 'form_read':
            def resolves(request, started_at):
                return 0 < self.started_at < started_at and self.request.resolved_by(request)

            completed = completed_forms.get(self.request.path)
            if completed and resolves(*completed):
                return

            def is_later_read(response):
                return (response.status == 200 and response.request.method == 'POST'
                        and response.url == self.request.url
                        and resolves(ReadRequest.from_response(response), response.request.timing['startTime']))

            page.wait_for_event('response', predicate=is_later_read, timeout=timeout)
            return
        if self.kind == 'settings':
            # Replay only the UI layout Save. No order/payment call is sent here.
            # The exact same request must receive 200 before the pending search
            # menu click is given its original visible target again.
            base = AutoBasePage(page)
            if self.request not in successful:
                with page.expect_response(self.request.matches, timeout=timeout) as saved:
                    base.grid_setting(menu_name=self.settings.menu_name,
                                      field_name=self.settings.field_name, timeout=timeout)
                saved.value.finished()
            base.grid_controller(open_setting=True)
            expect(page.get_by_role('menu').filter(visible=True).last.get_by_role(
                'menuitem', name='Настройки поиска', exact=True)).to_be_visible(timeout=timeout)
            return
        if self.kind == 'lookup':
            expect(self.lookup.input).to_have_value(self.query, timeout=timeout)
            dropdown = page.locator('.cdk-overlay-container smt-select-dropdown:visible')
            # A fresh response alone does not prove the dropdown survived lock.
            if self.request in successful and dropdown.count() == 1:
                return
        elif self.request in successful:
            return
        # The response listener is already installed before login. If the app
        # retried a model during unlock, it is in successful and is not retried.
        if self.kind == 'model':
            page.wait_for_event('response', predicate=self.request.matches, timeout=timeout)
            return
        with page.expect_response(self.request.matches, timeout=timeout) as resumed:
            if self.kind == 'lookup':
                expect(self.lookup.input).to_have_value(self.query, timeout=timeout)
                self.lookup.input.press('Escape', timeout=timeout)
                self.lookup.input.press('ArrowDown', timeout=timeout)
            elif self.kind == 'table':
                grid = page.locator('smt-data-table:visible')
                expect(grid).to_have_count(1, timeout=timeout)
                AutoBasePage(page).grid_controller(reload=True, root=grid)
            else:
                raise SessionRecoveryError('Uzilgan o‘qish uchun davom ettirish yo‘li yo‘q')
        resumed.value.finished()
        if self.kind == 'lookup':
            expect(page.locator('.cdk-overlay-container smt-select-dropdown:visible')).to_have_count(1, timeout=timeout)
            expect(self.lookup.input).to_have_value(self.query, timeout=timeout)


def prepare_resume(page, responses, lookup, settings=None, *, expected_url=None):
    """Classify a complete 401 batch; ambiguous/mutating batches fail closed.

    Returned error is raised AFTER authentication, so an unexpected operation
    cannot prevent the modal from being handled. No save/payment is replayed.
    """
    requests = {ReadRequest.from_response(response): response for response in responses}
    reads = []
    for request, response in requests.items():
        path = unquote(request.path)
        operation = path.rsplit(':', 1)[-1]
        if request.method != 'POST' or '/b/' not in path or '$' in path:
            raise SessionRecoveryError('401 saqlash yoki noma’lum so‘rovga kelgan; amal qayta yuborilmaydi')
        if _layout_preference(request, page.url, settings):
            reads.append(ResumeRead('settings', request, settings=settings))
            continue
        if _preference_read(request, page.url):
            continue
        if path.endswith(('/biruni/m:session', '/util/session_info')):
            continue  # The controller verifies the authenticated user explicitly.
        if path.endswith('/b/biruni/m:announcements'):
            # Observed background shell poll, not the interrupted order action.
            # Do not replay it. Authentication, route/draft and the original
            # business assertions still have to succeed before the case passes.
            continue
        route = unquote(urlsplit(page.url).path)
        if (route.endswith('_list') and '/a2/' in route
                and path == route.replace('/a2/', '/b/', 1) + ':get_widget_data'
                and request.payload == '{}' and lookup is None and settings is None):
            reads.append(ResumeRead('list_reload', request))
            continue
        if (path.endswith('/b/trade/tr/plugin:get_user_data')
                and route.endswith('/a2/trade/tdeal/order/order_view') and request.payload == '{}'):
            # The contact widget reads email/phone independently of the order.
            continue
        # An active b_input supplies the exact control/key/query. This is a
        # lookup capability, not an endpoint-name guess; no option is selected.
        if lookup is not None:
            query = lookup.input.input_value()
            if _table_query(request) and _lookup_query_finished(response.request, query, lookup.key_field):
                reads.append(ResumeRead('lookup', request, lookup=lookup, query=query))
                continue
        if path == SURVEY_DATA:
            # The shell polls again after login. Require its own later,
            # identical successful read without sending a survey request.
            reads.append(ResumeRead('form_read', request, started_at=response.request.timing['startTime']))
            continue
        if (observed_form_read(path)
                and route.replace('/a2/', '/b/', 1) == path.rsplit(':', 1)[0]):
            reads.append(ResumeRead('form_read', request, started_at=response.request.timing['startTime']))
            continue
        if operation.startswith('table') and _table_query(request):
            reads.append(ResumeRead('table', request))
        elif operation == 'model' and unquote(urlsplit(expected_url or page.url).path).replace('/a2/', '/b/', 1) == path.removesuffix(':model'):
            reads.append(ResumeRead('model', request))
        else:
            raise SessionRecoveryError(f'401 dan keyingi o‘qish hali qo‘llanmaydi: {operation}; avtomatik takrorlanmadi')
    if any(read.kind == 'list_reload' for read in reads):
        # List navigation can reject its widget, grid and model together.
        # A request from another form must not be satisfied by this reload.
        list_path = unquote(urlsplit(page.url).path).replace('/a2/', '/b/', 1)
        if all(read.kind in {'list_reload', 'table', 'model'}
               and unquote(read.request.path).rsplit(':', 1)[0] == list_path for read in reads):
            return ResumeRead('list_reload', list_requests=tuple(read.request for read in reads))
    if len(reads) > 1:
        raise SessionRecoveryError('Bir nechta o‘qish uzilgan; qaysi UI amalini davom ettirish noaniq')
    return reads[0] if reads else ResumeRead('none')
