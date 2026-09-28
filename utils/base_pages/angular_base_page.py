import re
from urllib.parse import urlsplit

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.date_utils import format_date, resolve_date
from utils.helper_utils import first_non_admin_filial, label_pattern
from utils.base_pages.page_diagnostics import expectation_gate, report_page_expectation
from utils.base_pages.page_reporting import report_web_action
from utils.report_context import record_filial


_UNSET = object()
_LEGACY_GRID_ROOT_RE = re.compile(
    r"""^(?:b-grid|b-pg-grid)(?:\[name=(['\"])(?P<name>[^'\"]+)\1\])?(?::visible)?$"""
)
_LEGACY_PAGE_ROOT_RE = re.compile(r"^b-page(?::visible)?$")
_ANGULAR_TABLE_SELECTOR = "smt-data-table, smt-local-table, smt-table"


def _whitespace_agnostic_pattern(value, *, exact=False):
    if isinstance(value, re.Pattern):
        return value
    normalized = re.sub(r"\s+", "", str(value))
    body = r"\s*".join(re.escape(char) for char in normalized)
    return re.compile(rf"^\s*{body}\s*$" if exact else body)


class AngularBasePage:
    """Smartup A2 yangi Angular formalarining umumiy UI primitivlari.

    Bu class ``smt-*`` komponentlari, CDK overlay va A2 shell uchun yozilgan.
    Eski AngularJS/Biruni formalarida ``utils.base_pages.base_page.BasePage`` ishlatiladi.
    Public parametrlar, assertion va return kontraktlari BasePage bilan teng;
    locator va komponent bilan ishlash implementatsiyasi A2 uchun alohida.
    """

    def __init__(self, page):
        self.page = page

    def _validate_options(self, method, **options):
        """Public helper flag/index/timeout kontrakti; ikkala page'da bir xil."""
        for name, value in options.items():
            if value is _UNSET:
                continue
            if name == "index":
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ValueError(f"{method}(): index manfiy bo'lmagan int bo'lishi kerak")
            elif name in {"timeout", "delay"}:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"{method}(): {name} manfiy bo'lmagan son bo'lishi kerak")
            elif not isinstance(value, bool):
                raise TypeError(f"{method}(): {name} bool bo'lishi kerak")

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def date(value="today", *, days=0, date_format="%d.%m.%Y"):
        return format_date(value, days=days, date_format=date_format)

    # ------------------------------------------------------------------------------------------------------------------

    def _legacy_grid_locator(self, root):
        """Biruni ``b-grid`` / ``b-pg-grid`` selectorlarini A2 table hostiga map qiladi."""
        if not isinstance(root, str):
            return None
        match = _LEGACY_GRID_ROOT_RE.fullmatch(root.strip())
        if not match:
            return None
        scope = self.page.locator("main").filter(visible=True).first
        tables = scope.locator(_ANGULAR_TABLE_SELECTOR).filter(visible=True)
        name = match.group("name")
        if not name:
            return tables.first
        named = scope.locator(
            f'smt-data-table[smtstoragekey*="{name}"], '
            f'smt-local-table[smtstoragekey*="{name}"], '
            f'smt-table[smtstoragekey*="{name}"], '
            f'smt-data-table[ng-reflect-smt-storage-key*="{name}"], '
            f'smt-local-table[ng-reflect-smt-storage-key*="{name}"], '
            f'smt-table[ng-reflect-smt-storage-key*="{name}"]'
        ).filter(visible=True)
        return named.or_(tables).first

    def _resolve_root(self, root):
        if root is None:
            return self.page
        if not isinstance(root, str):
            return root
        stripped = root.strip()
        if _LEGACY_PAGE_ROOT_RE.fullmatch(stripped):
            return self.page.locator("main").filter(visible=True).first
        mapped = self._legacy_grid_locator(root)
        if mapped is not None:
            return mapped
        return self.page.locator(root)

    def _row_plus_detail(self, root):
        """Kernel expandable actions live in sibling ``.smt-detail-row``, not inside the row."""
        if root is self.page:
            return root
        detail = root.locator(
            "xpath=self::*[contains(concat(' ', normalize-space(@class), ' '), ' smt-data-row ')]"
            "/following-sibling::*[contains(@class,'smt-detail-row')][1]"
        )
        return root.or_(detail)

    # ------------------------------------------------------------------------------------------------------------------

    def _content_root(self, root):
        return self._resolve_root("main" if root is None else root)

    def _table_host(self, root):
        """Root ichidagi ``smt-data-table`` / ``smt-local-table`` / ``smt-table`` hosti."""
        scoped = root.locator(_ANGULAR_TABLE_SELECTOR).filter(visible=True)
        if scoped.count() > 0:
            return scoped.first
        return root

    def status_button(self, entity_id):
        """Legacy Metronic ``#status-btn-{id}`` or kernel ``app-status-dropdown`` host."""
        return self.page.locator(f"#status-btn-{entity_id}, app-status-dropdown").first

    def status_row(self, entity_id):
        """Row that owns the status chip (A2 ``smt-data-row`` or legacy ``tbl-row``)."""
        chip = self.page.locator(f"#status-btn-{entity_id}, app-status-dropdown").first
        return self.page.locator(".smt-data-row, .tbl-row").filter(has=chip).first

    def _has_smt_control_label(self, label, root, timeout=0):
        """True when a visible ``smt-control`` label matches.

        After wizard Next the finish-step controls are not in the DOM yet.
        Instant ``count()`` then falls through to a table header (``Тип оплаты``
        is not a grid column) — wait for either a control label or a header.
        """
        host = root
        pat = self._label_pattern(label)
        labels = host.locator("smt-control label").filter(has_text=pat)
        if timeout:
            headers = self._table_host(host).locator(
                ".smt-grid-header [data-smt-col-key]"
            ).filter(has_text=pat)
            try:
                expect(labels.or_(headers).first).to_be_visible(timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError):
                return False
        return labels.filter(visible=True).count() > 0

    def _table_cell_by_header(self, label, *, index=0, root=None, timeout=10_000):
        """A2 table header matni (``Название``, ``Кол-во``) ostidagi birinchi row cell.

        Kernel order wizard product grid headerlari ``smt-control`` emas —
        ``smt-cell-header`` + ``data-smt-col-key``.
        """
        host = self._table_host(self._resolve_root(root))
        headers = host.locator(".smt-grid-header [data-smt-col-key]").filter(
            has_text=self._label_pattern(label),
        )
        expect(headers.nth(index)).to_be_visible(timeout=timeout)
        key = headers.nth(index).get_attribute("data-smt-col-key")
        if not key:
            shown = getattr(label, "pattern", label)
            raise AssertionError(f"Angular table header key topilmadi: label={shown}")
        cell = host.locator(f'.smt-data-row [data-smt-col-key="{key}"]').nth(index)
        expect(cell).to_be_visible(timeout=timeout)
        return cell

    def _native_field_input(self, host):
        return host.locator(
            "xpath=descendant-or-self::*[(self::input or self::textarea) "
            "and not(@type='checkbox') and not(@type='radio') and not(@type='hidden')]"
        ).first

    def _named_control_host(self, root, model_name):
        short_name = model_name.removeprefix("d.")
        return root.locator(
            f'[formcontrolname="{model_name}"], [formcontrolname="{short_name}"], '
            f'[ng-reflect-name="{model_name}"], [ng-reflect-name="{short_name}"], '
            f'smt-input[name="{short_name}"], [name="{short_name}"]'
        ).filter(visible=True)

    def _product_search_selects(self, root):
        return root.locator("smt-data-select").filter(
            has=self.page.locator("smt-select-trigger input:visible")
        )

    def _data_select_for_ng_model(self, root, model_name, index=0):
        named = root.locator(
            f'smt-data-select[formcontrolname="{model_name}"], '
            f'smt-data-select[formcontrolname="{model_name.removeprefix("d.")}"], '
            f'smt-select[formcontrolname="{model_name}"], '
            f'smt-select[formcontrolname="{model_name.removeprefix("d.")}"]'
        )
        if named.count() > 0:
            return named.nth(index)
        picks = self._product_search_selects(root)
        if "selected_bonus_name" in model_name:
            return picks.nth(1 if picks.count() > 1 else 0)
        if "selected_rule_name" in model_name:
            return picks.nth(0)
        return named.nth(index)

    def _input_el_for_ng_model(self, root, model_name, index=0):
        named = self._named_control_host(root, model_name)
        if named.count() > 0:
            return self._native_field_input(named.nth(index))
        rule_row = root.locator("div.grid.items-center.pt-2").filter(
            has=root.locator("smt-input")
        ).nth(index)
        rule_inputs = rule_row.locator(
            "input:not([type='checkbox']):not([type='radio']):not([type='hidden'])"
        )
        if model_name == "rule.main_value":
            return rule_inputs.nth(0)
        if model_name == "rule.extra_value":
            return rule_inputs.nth(1)
        if model_name == "rule.required_count":
            return rule_inputs.last
        if model_name == "product.value":
            bonus_row = root.locator("div.grid.items-center.py-1").filter(
                has=root.locator("smt-input")
            ).nth(index)
            return bonus_row.locator(
                "input:not([type='checkbox']):not([type='radio']):not([type='hidden'])"
            ).first
        return self._native_field_input(named.nth(index))

    # ------------------------------------------------------------------------------------------------------------------

    def _label_pattern(self, label):
        return label_pattern(label)

    # ------------------------------------------------------------------------------------------------------------------

    def _control(
        self,
        label,
        *,
        index=0,
        root=None,
        timeout=10_000,
    ):
        """``label`` bo'yicha ko'rinadigan ``smt-control``ni qaytaradi."""
        root = self._resolve_root(root)
        label_pattern = self._label_pattern(label)
        labels = root.locator("smt-control label").filter(
            has_text=label_pattern,
            visible=True,
        )
        expect(labels.first).to_be_visible(timeout=timeout)
        controls = root.locator("smt-control").filter(
            has=self.page.locator("label").filter(has_text=label_pattern)
        )

        visible_controls = []
        for control_index in range(controls.count()):
            candidate = controls.nth(control_index)
            try:
                expect(candidate).to_be_visible(timeout=min(timeout, 500))
            except (AssertionError, PlaywrightTimeoutError):
                continue
            visible_controls.append(candidate)

        if index >= len(visible_controls):
            shown = getattr(label, "pattern", label)
            raise AssertionError(
                f"Angular smt-control topilmadi: label={shown}, index={index}"
            )

        control = visible_controls[index]
        expect(control).to_be_visible(timeout=timeout)
        return control

    # ------------------------------------------------------------------------------------------------------------------

    def click(
        self,
        name,
        *,
        role="button",
        exact=False,
        index=0,
        root=None,
        timeout=10_000,
    ):
        """A2 elementni semantic role/name bo'yicha topib bosadi.

        Styled radio inputlar ko'rinadigan label/span ostida qolishi mumkin;
        radio tanlash uchun ``radio(label, click=True)`` ishlatiladi.
        """
        self._validate_options(
            'click',
            exact=exact,
            index=index,
            timeout=timeout,
        )
        root = self._row_plus_detail(self._resolve_root(root))
        overlay_menu = self.page.locator("[cdkmenu], [role='menu']").filter(visible=True)
        if overlay_menu.count() == 0:
            self._wait_blocking_overlay_gone()
        target = root.get_by_role(role, name=name, exact=exact)
        if role == "button":
            matcher = name if isinstance(name, re.Pattern) else (
                self._label_pattern(name) if exact else re.compile(re.escape(str(name)))
            )
            target = target.or_(root.locator("button, [smt-button]").filter(has_text=matcher))
            target = target.or_(
                overlay_menu.get_by_role("menuitem", name=name, exact=exact)
            ).or_(
                overlay_menu.locator("button, [cdkmenuitem]").filter(has_text=matcher)
            )
        if role == "tab":
            matcher = name if isinstance(name, re.Pattern) else (
                self._label_pattern(name) if exact else re.compile(re.escape(name))
            )
            smt_tab = root.locator("smt-tab-button:not([role='tab'])").filter(
                has_text=matcher,
                has_not=self.page.get_by_role("tab"),
            )
            target = target.or_(smt_tab)
        target = target.nth(index)
        expect(target).to_be_visible(timeout=timeout)
        target.click(timeout=timeout)
        return target

    # ------------------------------------------------------------------------------------------------------------------

    def hide_ui(self, locator, *, remove=False):
        """Test flowiga tegishli bo'lmagan yordamchi UI elementlarini yashiradi."""
        self._validate_options(
            'hide_ui',
            remove=remove,
        )
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.evaluate_all(
            """(elements, remove) => {
                for (const element of elements) {
                    if (remove) {
                        element.remove();
                        continue;
                    }
                    element.style.setProperty('display', 'none', 'important');
                    element.style.setProperty('visibility', 'hidden', 'important');
                    element.style.setProperty('pointer-events', 'none', 'important');
                    element.setAttribute('aria-hidden', 'true');
                }
                return elements.length;
            }""",
            remove,
        )

    # ------------------------------------------------------------------------------------------------------------------

    def input(
        self,
        locator=None,
        value=_UNSET,
        *,
        label=None,
        ng_model=None,
        placeholder=None,
        expect_value=_UNSET,
        return_value=False,
        index=0,
        root=None,
        clear=True,
        press_tab=False,
    ):
        """A2 ``smt-input`` ichidagi native input/textarea bilan ishlaydi.

        Biruni-number inputida avtomatik value asserti formatlashdagi
        whitespace'ni hisobga olmaydi; explicit expect_value aynan tekshiriladi.
        """
        self._validate_options(
            'input',
            return_value=return_value,
            index=index,
            clear=clear,
            press_tab=press_tab,
        )
        root = self._resolve_root(root)
        sources = sum(
            source is not None for source in (locator, label, ng_model, placeholder)
        )
        if sources != 1:
            raise ValueError(
                "input(): locator, label, ng_model yoki placeholder dan aynan bittasini bering"
            )

        if label is not None:
            if self._has_smt_control_label(label, root, timeout=10_000):
                control = self._control(label, index=index, root=root)
                input_el = control.locator(
                    "input:not([type='checkbox']):not([type='radio']):not([type='hidden']), "
                    "textarea"
                ).first
            else:
                cell = self._table_cell_by_header(label, index=index, root=root)
                input_el = cell.locator(
                    "input:not([type='checkbox']):not([type='radio']):not([type='hidden']), "
                    "textarea"
                ).first
        elif ng_model is not None:
            input_el = self._input_el_for_ng_model(root, str(ng_model), index)
        elif placeholder is not None:
            by_ph = root.get_by_placeholder(placeholder)
            if placeholder == "Выбрать дату":
                by_ph = by_ph.or_(root.locator("smt-date-picker input")).or_(
                    root.get_by_placeholder("Выберите дату")
                ).or_(root.get_by_placeholder("Select a date"))
            input_el = by_ph.nth(index)
        else:
            located = root.locator(locator).nth(index) if isinstance(locator, str) else locator
            # Legacy tour/IDs often sit on the smt-* host; value lives on the inner input.
            input_el = self._native_field_input(located)

        expect(input_el).to_be_visible(timeout=10_000)

        if value is not _UNSET:
            self._wait_blocking_overlay_gone()
            try:
                input_el.click(timeout=5_000)
            except PlaywrightTimeoutError:
                self._wait_blocking_overlay_gone()
                input_el.click(force=True, timeout=10_000)
            if clear:
                input_el.press("ControlOrMeta+A", timeout=10_000)
                input_el.press("Backspace", timeout=10_000)
            input_el.fill(str(value), timeout=10_000)
            if press_tab or input_el.locator("xpath=ancestor::smt-input").count():
                input_el.press("Tab", timeout=10_000)
            if input_el.locator(
                "xpath=ancestor::smt-data-select | ancestor::smt-multi-data-select | ancestor::smt-date-picker"
            ).count():
                self._dismiss_data_select_overlay()

        expected = expect_value
        if expected is _UNSET and value is not _UNSET:
            expected = str(value)
            if input_el.locator(
                "xpath=ancestor::smt-input[@smtbehavior='biruni-number']"
            ).count():
                expected = _whitespace_agnostic_pattern(expected, exact=True)
        if expected is not _UNSET:
            expect(input_el).to_have_value(expected, timeout=10_000)

        if return_value:
            return input_el.input_value()
        return input_el

    def _dismiss_session_lock(self, timeout=5_000):
        """Idle warning ``app-session-lock`` intercepts header clicks (aria-label Продолжить)."""
        host = self.page.locator("app-session-lock")
        if host.count() == 0:
            return
        backdrop = host.locator("button[aria-label]").filter(visible=True).first
        stay = host.get_by_role("button").filter(
            has_text=re.compile(r"Продолжить|Continue|Davom ettirish|Stay", re.I)
        ).filter(visible=True)
        try:
            if backdrop.count() > 0:
                backdrop.click(timeout=timeout, force=True)
                expect(backdrop).to_have_count(0, timeout=timeout)
                return
        except (AssertionError, PlaywrightTimeoutError):
            pass
        try:
            if stay.count() > 0:
                stay.first.click(timeout=timeout, force=True)
        except (AssertionError, PlaywrightTimeoutError):
            pass

    def _wait_blocking_overlay_gone(self, timeout=8_000):
        """Date-picker / select transparent backdrop qolsa keyingi click ni yopib qo'yadi.

        Dark ``smt-modal`` backdropni Escape bilan yopmaydi — modal ichidagi
        maydonlar yo'qolib ketadi (currency «Добавить курс»).
        """
        backdrop = self.page.locator(
            ".cdk-overlay-container .cdk-overlay-transparent-backdrop.cdk-overlay-backdrop-showing"
        )
        for _ in range(6):
            if backdrop.count() == 0:
                return
            self.page.keyboard.press("Escape")
            try:
                expect(backdrop).to_have_count(0, timeout=800)
                return
            except (AssertionError, PlaywrightTimeoutError):
                continue

    def _dismiss_data_select_overlay(self, timeout=8_000):
        """Typeahead overlay ochilishi (300ms debounce) va spinner tugashini kutib yopadi.

        Fill tugaganda dropdown hali yo'q; keyin spinner pointer-eventlarni yopib
        keyingi input click ni timeout qiladi (natural_person Имя → Код).
        """
        pane = self.page.locator(
            ".cdk-overlay-container smt-select-dropdown:visible, "
            ".cdk-overlay-container .cdk-overlay-transparent-backdrop:visible"
        )
        spinner = self.page.locator(".cdk-overlay-container .animate-spin:visible")
        try:
            expect(pane.first).to_be_visible(timeout=800)
        except (AssertionError, PlaywrightTimeoutError):
            return
        try:
            expect(spinner).to_have_count(0, timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError):
            pass
        for _ in range(4):
            if pane.count() == 0:
                return
            self.page.keyboard.press("Escape")
            try:
                expect(pane).to_have_count(0, timeout=400)
                return
            except (AssertionError, PlaywrightTimeoutError):
                continue

    # ------------------------------------------------------------------------------------------------------------------

    def b_input(
        self,
        label=None,
        value=_UNSET,
        *,
        ng_model=None,
        expect_value=_UNSET,
        return_value=False,
        search_text=None,
        clear=False,
        exact=True,
        server_search=False,
        select_first=False,
        delay=50,
        index=0,
        root=None,
        timeout=10_000,
    ):
        """A2 ``smt-data-select``dan option tanlaydi yoki joriy qiymatni tekshiradi.

        ``select_first=True`` qidiruvsiz birinchi optionni tanlaydi. Non-empty
        ``search_text`` qidiruv natijasidagi birinchi optionni, faqat ``value``
        esa shu qiymatga mos optionni tanlaydi.

        exact option matni va string assertioniga taalluqli; regex o'zicha ishlaydi.
        clear=True tanlovsiz ham maydonni tozalaydi. Default native input
        Locator, return_value=True esa uning string qiymatini qaytaradi.
        """
        self._validate_options(
            'b_input',
            return_value=return_value,
            clear=clear,
            exact=exact,
            server_search=server_search,
            select_first=select_first,
            delay=delay,
            index=index,
            timeout=timeout,
        )
        root = self._resolve_root(root)
        if label is not None and ng_model is not None:
            raise ValueError("b_input(): label yoki ng_model dan faqat bittasini bering")
        if label is not None:
            self._wait_blocking_overlay_gone()
            if self._has_smt_control_label(label, root, timeout=timeout):
                control = self._control(label, index=index, root=root, timeout=timeout)
                select = control.locator("smt-data-select, smt-select").first
            else:
                cell = self._table_cell_by_header(
                    label, index=index, root=root, timeout=timeout
                )
                select = cell.locator("smt-data-select, smt-select").first
        elif ng_model is not None:
            select = self._data_select_for_ng_model(root, str(ng_model), index)
        else:
            raise ValueError("b_input(): label yoki ng_model berilishi kerak")

        trigger = select.locator("smt-select-trigger").first
        search = trigger.locator(
            "input:not([type='checkbox']):not([type='radio'])"
        ).first

        expect(select).to_be_visible(timeout=timeout)
        expect(trigger).to_be_visible(timeout=timeout)
        expect(search).to_be_visible(timeout=timeout)
        self.page.keyboard.press("Escape")
        self.page.keyboard.press("Escape")
        dropdown = self.page.locator(
            ".cdk-overlay-container smt-select-dropdown:visible"
        ).last

        if clear:
            search.click(timeout=timeout)
            search.press("ControlOrMeta+A", timeout=timeout)
            search.press("Backspace", timeout=timeout)
            expect(search).to_have_value("", timeout=timeout)

        has_search_query = search_text not in (None, "")
        if value is not _UNSET or has_search_query or select_first:
            option_text = str(value) if value is not _UNSET else None
            if not dropdown.is_visible():
                trigger.click(timeout=timeout)
            query = None if select_first else option_text if search_text is None else str(search_text)
            if query:
                search.press("ControlOrMeta+A", timeout=timeout)
                search.press("Backspace", timeout=timeout)
                if server_search:
                    search.press_sequentially(query, delay=delay, timeout=timeout)
                else:
                    search.fill(query, timeout=timeout)

            expect(dropdown).to_be_visible(timeout=timeout)
            expect(dropdown.locator(".animate-spin")).to_have_count(0, timeout=timeout)
            options = dropdown.locator("li:visible")
            if option_text and not select_first:
                expect(options.filter(has_text=str(option_text)).first).to_be_visible(timeout=timeout)
            else:
                expect(options.first).to_be_visible(timeout=timeout)
            visible_dd = self.page.locator(".cdk-overlay-container smt-select-dropdown:visible")
            li = visible_dd.last.locator("li:visible")
            if option_text and not select_first:
                li = li.filter(has_text=str(option_text))
            li.first.click(force=True, timeout=timeout)
            try:
                expect(visible_dd).to_have_count(0, timeout=3_000)
            except AssertionError:
                self.page.keyboard.press("Escape")
                try:
                    expect(visible_dd).to_have_count(0, timeout=2_000)
                except AssertionError:
                    search.press("ArrowDown", timeout=timeout)
                    search.press("Enter", timeout=timeout)
                    self.page.keyboard.press("Escape")
                    expect(visible_dd).to_have_count(0, timeout=timeout)

        if clear and value is _UNSET and not has_search_query and not select_first:
            search.press("Escape", timeout=timeout)

        add_only_picker = ng_model is not None and (
            "selected_rule_name" in str(ng_model) or "selected_bonus_name" in str(ng_model)
        )
        expected = expect_value
        if expected is _UNSET and value is not _UNSET and not select_first and not has_search_query:
            expected = str(value)
        if expected is not _UNSET:
            if add_only_picker and isinstance(expected, str):
                expect(self.page.get_by_text(expected, exact=True).first).to_be_visible(
                    timeout=timeout
                )
            else:
                if isinstance(expected, str):
                    expected = (
                        re.compile(rf"^\s*{re.escape(expected)}\s*$")
                        if exact else re.compile(re.escape(expected))
                    )
                expect(search).to_have_value(expected, timeout=timeout)

        if return_value:
            return search.input_value()
        return search

    # ------------------------------------------------------------------------------------------------------------------

    def date_picker(
        self,
        label,
        date="today",
        *,
        auto_fill=False,
        index=0,
        root=None,
        timeout=10_000,
    ):
        """A2 ``smt-date-picker``da bugungi yoki ``DD.MM.YYYY`` sanani tanlaydi."""
        self._validate_options(
            'date_picker',
            auto_fill=auto_fill,
            index=index,
            timeout=timeout,
        )
        root = self._resolve_root(root)
        control = self._control(label, index=index, root=root, timeout=timeout)
        picker = control.locator("smt-date-picker").first
        trigger = picker.locator("smt-select-trigger").first
        input_el = trigger.locator("input").first
        expect(picker).to_be_visible(timeout=timeout)
        expect(trigger).to_be_visible(timeout=timeout)
        expect(input_el).to_be_visible(timeout=timeout)
        self._wait_blocking_overlay_gone()

        expected = resolve_date(date).strftime("%d.%m.%Y")
        if auto_fill:
            expect(input_el).to_have_value(expected, timeout=timeout)
            return input_el

        input_el.click(timeout=timeout)
        input_el.press("ControlOrMeta+A", timeout=timeout)
        input_el.fill(expected, timeout=timeout)
        input_el.press("Tab", timeout=timeout)

        self._wait_blocking_overlay_gone()
        expect(input_el).to_have_value(expected, timeout=timeout)
        return input_el

    # ------------------------------------------------------------------------------------------------------------------

    def _toggle_by_label(
        self,
        label,
        *,
        role,
        index=0,
        root=None,
        timeout=10_000,
    ):
        root = self._resolve_root(root)
        roles = (role,) if isinstance(role, str) else tuple(role)
        pattern = self._label_pattern(label)
        visible_label = root.get_by_text(pattern).filter(visible=True).first
        expect(visible_label).to_be_visible(timeout=timeout)

        toggle = None
        # smt-radio-group: option text lives on the wrapping <label>, not smt-control.
        labeled = root.locator("label").filter(has_text=pattern).filter(visible=True)
        for role_name in roles:
            candidates = labeled.get_by_role(role_name)
            if candidates.count() > index:
                toggle = candidates.nth(index)
                break

        controls = root.locator("smt-control").filter(
            has=self.page.locator("label").filter(has_text=pattern)
        )
        if toggle is None:
            for role_name in roles:
                candidates = controls.get_by_role(role_name)
                if candidates.count() > index:
                    toggle = candidates.nth(index)
                    break

        if toggle is None:
            header = visible_label.locator(
                "xpath=ancestor::*[contains(@class,'custom-card-header')][1]"
            )
            if header.count() > 0:
                for role_name in roles:
                    nearby = header.get_by_role(role_name)
                    if nearby.count() > index:
                        toggle = nearby.nth(index)
                        break

        if toggle is None:
            labels = root.get_by_text(pattern).filter(visible=True)
            matched = []
            for role_name in roles:
                for label_index in range(labels.count()):
                    label_item = labels.nth(label_index)
                    container = label_item.locator(
                        f"xpath=ancestor::*[.//*[@role='{role_name}']][1]"
                    )
                    if container.count() == 0:
                        continue
                    role_control = container.get_by_role(role_name).first
                    if role_control.count() > 0:
                        matched.append(role_control)
            if index >= len(matched):
                shown = getattr(label, "pattern", label)
                raise AssertionError(
                    f"Angular {'/'.join(roles)} topilmadi: label={shown}, index={index}"
                )
            toggle = matched[index]

        expect(toggle).to_be_visible(timeout=timeout)
        return toggle

    # ------------------------------------------------------------------------------------------------------------------

    def _set_toggle(self, toggle, checked, *, timeout=10_000):
        role = toggle.get_attribute("role")
        if role in {"switch", "checkbox", "radio"}:
            current = (toggle.get_attribute("aria-checked") or "").lower() == "true"
            if current != checked:
                toggle.dispatch_event("pointerdown")
                toggle.dispatch_event("mousedown")
                toggle.click(force=True, timeout=timeout)
                toggle.dispatch_event("pointerup")
            expect(toggle).to_have_attribute(
                "aria-checked",
                "true" if checked else "false",
                timeout=timeout,
            )
            return

        input_type = (toggle.get_attribute("type") or "").lower()
        if input_type in {"checkbox", "radio"}:
            if toggle.is_checked() != checked:
                toggle.set_checked(checked)
            expect(toggle).to_be_checked(timeout=timeout) if checked else expect(
                toggle
            ).not_to_be_checked(timeout=timeout)
            return

        raise AssertionError("Angular toggle role yoki checkbox/radio input emas")

    # ------------------------------------------------------------------------------------------------------------------

    def checkbox(
        self,
        locator=None,
        checked=_UNSET,
        *,
        ng_model=None,
        label=None,
        expect_checked=_UNSET,
        return_value=False,
        index=0,
        root=None,
    ):
        """A2 checkbox/switch controlini canonical API bilan boshqaradi."""
        self._validate_options(
            'checkbox',
            checked=checked,
            expect_checked=expect_checked,
            return_value=return_value,
            index=index,
        )
        root = self._resolve_root(root)

        if sum(source is not None for source in (locator, label, ng_model)) != 1:
            raise ValueError("checkbox(): label, ng_model yoki locator dan aynan bittasini bering")

        if label is not None:
            toggle = self._toggle_by_label(
                label,
                role=("checkbox", "switch"),
                index=index,
                root=root,
            )
        elif ng_model is not None:
            model_name = str(ng_model)
            short_name = model_name.removeprefix("d.")
            toggle = root.locator(
                f'[formcontrolname="{model_name}"], [formcontrolname="{short_name}"], '
                f'[ng-reflect-name="{model_name}"], [ng-reflect-name="{short_name}"]'
            ).filter(visible=True).nth(index).locator(
                "xpath=descendant-or-self::*[@role='checkbox' or @role='switch' "
                "or (self::input and @type='checkbox')]"
            ).first
        elif locator is not None:
            toggle = root.locator(locator).nth(index) if isinstance(locator, str) else locator
        else:
            raise ValueError("checkbox(): label, ng_model yoki locator dan bittasini bering")

        expect(toggle).to_be_visible(timeout=10_000)

        if checked is not _UNSET:
            self._set_toggle(toggle, bool(checked))

        expected = checked if checked is not _UNSET else expect_checked
        if expected is not _UNSET:
            role = toggle.get_attribute("role")
            if role:
                expect(toggle).to_have_attribute(
                    "aria-checked",
                    "true" if expected else "false",
                    timeout=10_000,
                )
            else:
                expect(toggle).to_be_checked(timeout=10_000) if expected else expect(
                    toggle
                ).not_to_be_checked(timeout=10_000)

        if return_value:
            if toggle.get_attribute("role"):
                return (toggle.get_attribute("aria-checked") or "").lower() == "true"
            return toggle.is_checked()
        return toggle

    # ------------------------------------------------------------------------------------------------------------------

    def radio(
        self,
        label,
        *,
        click=False,
        expect_checked=True,
        return_value=False,
        index=0,
        root=None,
    ):
        """A2 semantic radio controlini tanlaydi yoki holatini tekshiradi."""
        self._validate_options(
            'radio',
            click=click,
            expect_checked=expect_checked,
            return_value=return_value,
            index=index,
        )

        radio = self._toggle_by_label(
            label,
            role="radio",
            index=index,
            root=root,
        )
        if click:
            label_el = radio.locator("xpath=ancestor::label[1]")
            if label_el.count() > 0 and label_el.first.is_visible():
                label_el.first.click(timeout=10_000)
            else:
                radio.click(timeout=10_000)

        if expect_checked is not _UNSET:
            if radio.get_attribute("role") == "radio":
                expect(radio).to_have_attribute(
                    "aria-checked",
                    "true" if expect_checked else "false",
                    timeout=10_000,
                )
            elif expect_checked:
                expect(radio).to_be_checked(timeout=10_000)
            else:
                expect(radio).not_to_be_checked(timeout=10_000)
        if return_value:
            if radio.get_attribute("role") == "radio":
                return (radio.get_attribute("aria-checked") or "").lower() == "true"
            return radio.is_checked()
        return radio

    # ------------------------------------------------------------------------------------------------------------------

    def choice(
        self,
        label,
        option,
        *,
        index=0,
        root=None,
        timeout=10_000,
    ):
        """``smt-control`` ichidagi segmented button optionni tanlaydi."""
        self._validate_options(
            'choice',
            index=index,
            timeout=timeout,
        )
        control = self._control(label, index=index, root=root, timeout=timeout)
        button = control.get_by_role("button", name=option, exact=True).first
        expect(button).to_be_visible(timeout=timeout)
        button.click(timeout=timeout)
        return button

    # ------------------------------------------------------------------------------------------------------------------

    def text(self, *values, root="b-page", timeout=10_000):
        self._validate_options(
            'text',
            timeout=timeout,
        )
        remap_legacy_page = isinstance(root, str) and _LEGACY_PAGE_ROOT_RE.fullmatch(root.strip())
        content = self._content_root(None if remap_legacy_page else root)
        if content is self.page:
            content = self.page.locator("body")
        expect(content).to_be_visible(timeout=timeout)
        for value in values:
            if not value:
                continue
            # Kernel *_view keeps model in readonly <input value>, not innerText.
            # Older Playwright has neither Locator nor Page.get_by_display_value.
            self.page.wait_for_function(
                """(value) => {
                  const matches = (root) => {
                    if (!root) return false;
                    if ((root.innerText || '').includes(value)) return true;
                    for (const el of root.querySelectorAll('input, textarea, select')) {
                      if ((el.value || '') === value) return true;
                    }
                    for (const el of root.querySelectorAll('*')) {
                      if (el.shadowRoot && matches(el.shadowRoot)) return true;
                    }
                    return false;
                  };
                  return matches(document.body);
                }""",
                arg=value,
                timeout=timeout,
            )

    # ------------------------------------------------------------------------------------------------------------------

    @report_web_action
    def form_view(
        self,
        label,
        *,
        expect_value=_UNSET,
        return_value=False,
        remove_spaces=False,
        index=0,
        root=None,
        timeout=10_000,
    ):
        """A2 view'dagi readonly ``smt-input`` qiymatini tekshiradi yoki qaytaradi."""
        self._validate_options(
            'form_view',
            return_value=return_value,
            remove_spaces=remove_spaces,
            index=index,
            timeout=timeout,
        )
        control = self._control(label, index=index, root=root, timeout=timeout)
        field = control.locator(
            "input:not([type='checkbox']):not([type='radio']):not([type='hidden']), textarea"
        ).first
        expect(field).to_be_visible(timeout=timeout)
        expect(field).to_have_attribute("readonly", re.compile(r".*"), timeout=timeout)

        if expect_value is not _UNSET:
            if remove_spaces:
                if not isinstance(expect_value, str):
                    raise TypeError(
                        "form_view(remove_spaces=True): expect_value string bo'lishi kerak"
                    )
                expected = _whitespace_agnostic_pattern(expect_value, exact=True)
                expect(field).to_have_value(expected, timeout=timeout)
            else:
                expected = expect_value
                if isinstance(expected, str):
                    normalized = " ".join(expected.split())
                    body = r"\s+".join(re.escape(part) for part in normalized.split(" "))
                    expected = re.compile(rf"^\s*{body}\s*$")
                expect(field).to_have_value(expected, timeout=timeout)

        if return_value:
            actual = field.input_value().strip()
            return re.sub(r"\s+", "", actual) if remove_spaces else actual
        return field

    # ------------------------------------------------------------------------------------------------------------------

    def multiselect(
        self,
        label=None,
        value=_UNSET,
        *,
        name=None,
        expect_value=_UNSET,
        return_value=False,
        clear=False,
        index=0,
        close=True,
        exact=True,
        timeout=10_000,
        root=None,
    ):
        """A2 multi-select componentini canonical API bilan boshqaradi."""
        self._validate_options(
            'multiselect',
            return_value=return_value,
            clear=clear,
            index=index,
            close=close,
            exact=exact,
            timeout=timeout,
        )
        root = self._resolve_root(root)
        if label is not None and name is not None:
            raise ValueError("multiselect(): label yoki name dan faqat bittasini bering")
        if label is not None:
            control = self._control(label, index=index, root=root, timeout=timeout)
            select = control.locator(
                "smt-data-select, smt-select, smt-multi-data-select, smt-multi-select"
            ).first
        elif name is not None:
            select = root.locator(
                f'smt-data-select[formcontrolname="{name}"], '
                f'smt-select[formcontrolname="{name}"], '
                f'smt-multi-data-select[formcontrolname="{name}"], '
                f'smt-multi-select[formcontrolname="{name}"]'
            ).nth(index)
        else:
            raise ValueError("multiselect(): label yoki name berilishi kerak")

        expect(select).to_be_visible(timeout=timeout)
        trigger = select.locator("smt-select-trigger").first
        search = trigger.locator("input").first
        chips = select.locator(
            "smt-chip:visible, .smt-chip:visible, smt-tag:visible, "
            "[role='option'][aria-selected='true']:visible"
        )

        def values_list(values):
            if values is _UNSET:
                return []
            if isinstance(values, str):
                return [values]
            try:
                return [str(item) for item in values]
            except TypeError:
                return [str(values)]

        if clear:
            clear_buttons = select.locator(
                'button[aria-label*="Очист"]:visible, button[aria-label*="Clear"]:visible'
            )
            for _ in range(clear_buttons.count()):
                clear_buttons.first.click(timeout=timeout)
            expect(chips).to_have_count(0, timeout=timeout)

        selected_values = values_list(value)
        dropdown = self.page.locator(
            ".cdk-overlay-container smt-select-dropdown:visible, "
            ".cdk-overlay-container [cdkMenu]:visible, "
            ".cdk-overlay-container [cdkmenu]:visible"
        ).last
        for option_text in selected_values:
            if not dropdown.is_visible():
                trigger.click(timeout=timeout)
            expect(search).to_be_visible(timeout=timeout)
            search.press("ControlOrMeta+A", timeout=timeout)
            search.press("Backspace", timeout=timeout)
            search.fill(option_text, timeout=timeout)
            expect(dropdown).to_be_visible(timeout=timeout)
            matcher = (
                re.compile(rf"^\s*{re.escape(option_text)}\s*$")
                if exact
                else re.compile(re.escape(option_text))
            )
            option = dropdown.get_by_text(matcher).first
            expect(option).to_be_visible(timeout=timeout)
            # ui-kit multi-data-select uses mousedown.preventDefault, which drops the
            # browser click after Playwright's real mouse sequence.
            option.evaluate(
                """el => {
                  const target =
                    el.querySelector('[role="option"], [role="menuitemcheckbox"], [role="menuitem"]') ||
                    el.querySelector('[class*="cursor-pointer"]') ||
                    el;
                  for (const type of ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
                    target.dispatchEvent(new MouseEvent(type, {
                      bubbles: true,
                      cancelable: true,
                      view: window,
                      buttons: 1,
                    }));
                  }
                }"""
            )

        expected_values = (
            selected_values
            if expect_value is _UNSET and value is not _UNSET
            else values_list(expect_value)
        )
        for option_text in expected_values:
            matcher = (
                re.compile(rf"^\s*{re.escape(option_text)}\s*$")
                if exact else re.compile(re.escape(option_text))
            )
            selected = chips.filter(has_text=matcher).or_(
                chips.filter(has=self.page.get_by_text(matcher))
            ).first
            expect(selected).to_be_visible(timeout=timeout)

        if close and value is not _UNSET:
            self.page.keyboard.press("Escape")
            self.page.keyboard.press("Escape")
        if return_value:
            return [" ".join(text.split()) for text in chips.all_inner_texts() if text.strip()]
        return select

    # ------------------------------------------------------------------------------------------------------------------

    def ui_select(
        self,
        label=None,
        value=_UNSET,
        *,
        ng_model=None,
        expect_value=_UNSET,
        return_value=False,
        search_text=None,
        exact=True,
        index=0,
        root=None,
        timeout=10_000,
    ):
        """Qidiruvdan keyin valuega mos optionni tanlaydi; component Locator qaytaradi.

        search_text faqat qidiruv uchun. exact tanlash va assertionga taalluqli.
        Faqat search_text berilsa tanlov o'zgarmaydi.
        """
        self._validate_options(
            'ui_select',
            return_value=return_value,
            exact=exact,
            index=index,
            timeout=timeout,
        )
        root = self._resolve_root(root)
        if label is not None and ng_model is not None:
            raise ValueError("ui_select(): label yoki ng_model dan faqat bittasini bering")
        if label is not None:
            control = self._control(label, index=index, root=root, timeout=timeout)
            select = control.locator("smt-data-select, smt-select").first
        elif ng_model is not None:
            model_name = str(ng_model)
            short_name = model_name.removeprefix("d.")
            select = root.locator(
                f'smt-data-select[formcontrolname="{model_name}"], '
                f'smt-data-select[formcontrolname="{short_name}"], '
                f'smt-select[formcontrolname="{model_name}"], '
                f'smt-select[formcontrolname="{short_name}"]'
            ).nth(index)
        else:
            raise ValueError("ui_select(): label yoki ng_model berilishi kerak")

        trigger = select.locator("smt-select-trigger").first
        selected = trigger.locator("input:not([type='checkbox']):not([type='radio'])").first
        expect(select).to_be_visible(timeout=timeout)
        expect(trigger).to_be_visible(timeout=timeout)
        has_search_input = selected.count() > 0 and selected.is_visible()
        if has_search_input:
            expect(selected).to_be_visible(timeout=timeout)

        if value is not _UNSET:
            option_text = str(value)
            self._wait_blocking_overlay_gone()
            trigger.click(timeout=timeout)
            if search_text is not None and has_search_input:
                selected.fill(str(search_text), timeout=timeout)
            dropdown = self.page.locator(
                ".cdk-overlay-container smt-select-dropdown:visible"
            ).last
            expect(dropdown).to_be_visible(timeout=timeout)
            matcher = (
                re.compile(rf"^\s*{re.escape(option_text)}\s*$")
                if exact else re.compile(re.escape(option_text))
            )
            options = dropdown.locator("li:visible")
            option = options.filter(has_text=matcher).or_(
                options.filter(has=self.page.get_by_text(matcher))
            ).first
            expect(option).to_be_visible(timeout=timeout)
            option.click(timeout=timeout)
            if dropdown.is_visible():
                self.page.keyboard.press("Escape")
            expect(dropdown).to_be_hidden(timeout=timeout)

        expected = expect_value
        if expected is not _UNSET or (value is not _UNSET):
            if expected is _UNSET:
                expected = str(value)
            if has_search_input:
                if isinstance(expected, str):
                    normalized = " ".join(expected.split())
                    body = r"\s+".join(re.escape(part) for part in normalized.split(" "))
                    expected = re.compile(rf"^\s*{body}\s*$" if exact else body)
                expect(selected).to_have_value(expected, timeout=timeout)
            elif isinstance(expected, str):
                expect(trigger).to_contain_text(expected, timeout=timeout)
        if return_value:
            if has_search_input:
                return " ".join(selected.input_value().split())
            return " ".join(trigger.inner_text().split())
        return select

    # ------------------------------------------------------------------------------------------------------------------

    def _visible_modal_candidates(self, root="body"):
        """Ko'rinadigan A2/CDK dialog rootlarini qaytaradi."""
        root = self._resolve_root(root)
        return root.locator("[role='dialog']:visible")

    # ------------------------------------------------------------------------------------------------------------------

    def _visible_error_locator(self, root="body"):
        error_text = re.compile(r"ошибка|error|URL\s*:|Uri\s*:", re.IGNORECASE)
        return self._visible_modal_candidates(root=root).filter(
            has_text=error_text
        ).last

    # ------------------------------------------------------------------------------------------------------------------

    def _visible_error_text(self, root="body"):
        error = self._visible_error_locator(root=root)
        if error.count() == 0 or not error.is_visible():
            return ""
        return re.sub(r"\s+", " ", error.inner_text()).strip()

    # ------------------------------------------------------------------------------------------------------------------

    def _wait_for_loader(
        self,
        timeout=120_000,
        *,
        appear_timeout=2_000,
        root=None,
    ):
        """A2 skeleton/busy holati paydo bo'lsa, to'liq tugashini kutadi."""
        root = self._content_root(root)
        skeleton = root.locator(".smt-skeleton:visible")
        busy = root.locator("[aria-busy='true']:visible")
        loader = root.locator(
            ".smt-skeleton:visible, [aria-busy='true']:visible"
        )

        try:
            expect(loader.first).to_be_visible(timeout=appear_timeout)
        except (AssertionError, PlaywrightTimeoutError):
            pass

        expect(skeleton).to_have_count(0, timeout=timeout)
        expect(busy).to_have_count(0, timeout=timeout)
        return True

    # ------------------------------------------------------------------------------------------------------------------

    def wait_for_loader(self, timeout=120_000):
        self._validate_options(
            'wait_for_loader',
            timeout=timeout,
        )
        return self._wait_for_loader(timeout=timeout)

    # ------------------------------------------------------------------------------------------------------------------

    @report_web_action
    @report_page_expectation
    def expect_page(
        self,
        heading=None,
        url=None,
        timeout=30_000,
        check_unblocked=True,
        root=None,
    ):
        """A2 sahifani canonical URL/heading contracti bilan tekshiradi."""
        self._validate_options(
            'expect_page',
            timeout=timeout,
            check_unblocked=check_unblocked,
        )
        if heading is None and url is None:
            raise ValueError("expect_page: kamida 'heading' yoki 'url' berilishi kerak")

        if url is not None:
            if isinstance(url, re.Pattern):
                pattern = url
            else:
                pattern = re.compile(re.escape(url).replace(r"\+", r"(?:\+|%2B)"))
            expectation_gate(self.page, "url")
            expect(self.page).to_have_url(pattern, timeout=timeout)

        scope = self.page if root is None else self._content_root(root)
        if heading is not None:
            expectation_gate(self.page, "heading")
            role_heading = scope.get_by_role("heading").filter(has_text=heading).first
            exact_heading = not isinstance(heading, re.Pattern)
            text_heading = scope.get_by_text(heading, exact=exact_heading).filter(visible=True).first
            titled = scope.locator("app-form-stack-widget [title], [title]").filter(
                has_text=heading
            ).filter(visible=True).first
            target = role_heading.or_(text_heading).or_(titled).first
            expect(target).to_be_visible(timeout=timeout)

        if check_unblocked:
            expectation_gate(self.page, "loader")
            self._wait_for_loader(timeout=timeout, root=self.page)

    # ------------------------------------------------------------------------------------------------------------------

    @report_web_action
    def grid(
        self,
        text=None,
        *contains,
        root="b-grid",
        click=False,
        checkbox=None,
        state=None,
        return_bool=False,
        remove_spaces=True,
    ):
        """A2 ``smt-data-table`` qatorlarini BasePage contracti bilan boshqaradi."""
        self._validate_options(
            'grid',
            click=click,
            return_bool=return_bool,
            remove_spaces=remove_spaces,
        )
        if checkbox not in (None, "row", "all"):
            raise ValueError('grid(checkbox=...): "row" yoki "all" bo\'lishi kerak')
        if state not in (None, "empty"):
            raise ValueError('grid(state=...): faqat "empty" qo\'llanadi')
        if state is not None and (text is not None or contains or click or checkbox is not None):
            raise ValueError("grid(state=...) qator/click/checkbox amallari bilan birga ishlatilmaydi")
        if return_bool and (contains or click or checkbox is not None):
            raise ValueError("grid(return_bool=True) contains/click/checkbox bilan birga ishlatilmaydi")
        if checkbox == "all" and (text is not None or contains or click):
            raise ValueError('grid(checkbox="all") text/contains/click bilan birga ishlatilmaydi')
        if text is None and contains:
            raise ValueError("grid(*contains) uchun text berilishi kerak")
        if click and text is None:
            raise ValueError("grid(click=True) uchun text berilishi kerak")
        if checkbox == "row" and text is None:
            raise ValueError('grid(checkbox="row") uchun text berilishi kerak')
        if text is None and state is None and checkbox is None:
            raise ValueError("grid(): text, state yoki checkbox dan bittasini bering")

        if root is None or root is self.page:
            grid = self._legacy_grid_locator("b-grid")
        else:
            grid = self._resolve_root(root)

        rows = grid.locator(".smt-data-row")
        no_data = grid.get_by_text(
            re.compile(
                r"^\s*(нет данных|нет результатов|no data|no results|ничего не найдено)\s*$",
                re.IGNORECASE,
            )
        )
        if return_bool:
            if state == "empty":
                return no_data.is_visible()
            row_text = _whitespace_agnostic_pattern(text) if remove_spaces else text
            return rows.filter(has_text=row_text).first.is_visible()

        expect(grid).to_be_visible(timeout=10_000)
        self._wait_for_loader(timeout=10_000, root=grid)

        if state == "empty":
            expect(no_data).to_be_visible(timeout=10_000)
            return grid

        if checkbox == "all":
            toggle = grid.get_by_role("checkbox").first
            expect(toggle).to_be_visible(timeout=10_000)
            self._set_toggle(toggle, True)
            return toggle

        row_text = _whitespace_agnostic_pattern(text) if remove_spaces else text
        row = rows.filter(has_text=row_text).first
        expect(row).to_be_visible(timeout=10_000)
        for value in contains:
            expected = _whitespace_agnostic_pattern(value) if remove_spaces else value
            expect(row).to_contain_text(expected, timeout=10_000)
        if checkbox == "row":
            toggle = row.get_by_role("checkbox").first
            expect(toggle).to_be_visible(timeout=10_000)
            self._set_toggle(toggle, True)
        if click:
            self._wait_blocking_overlay_gone()
            row.click(timeout=10_000)
            detail = row.locator(
                "xpath=following-sibling::*[contains(@class,'smt-detail-row')][1]"
            )
            try:
                expect(detail).to_be_visible(timeout=3_000)
            except AssertionError:
                pass
        return row

    # ------------------------------------------------------------------------------------------------------------------

    def grid_controller(
        self,
        *,
        search=None,
        expand=None,
        reload=False,
        open_filter=False,
        open_setting=False,
        root="b-grid-controller",
    ):
        """A2 list search va page-size controlini boshqaradi."""
        self._validate_options(
            'grid_controller',
            reload=reload,
            open_filter=open_filter,
            open_setting=open_setting,
        )
        root = self._content_root(None if root == "b-grid-controller" else root)
        if search is not None:
            self._wait_blocking_overlay_gone()
            field = root.locator("input[type='search']").filter(visible=True).first
            expect(field).to_be_visible(timeout=30_000)
            field.click(timeout=30_000)
            field.press("ControlOrMeta+A", timeout=30_000)
            field.press("Backspace", timeout=30_000)
            if str(search):
                field.fill(str(search), timeout=30_000)
            expect(field).to_have_value(str(search), timeout=30_000)
            self._wait_for_loader(timeout=30_000, root=root)
            return

        if expand is not None:
            expand_value = str(expand)
            if expand_value not in {"50", "100", "500", "1000"}:
                raise ValueError(
                    'grid_controller(expand=...): "50", "100", "500" yoki "1000" bo\'lishi kerak'
                )
            page_size = root.get_by_role(
                "button",
                name=re.compile(r"Строк на странице|Rows per page", re.IGNORECASE),
            ).first
            expect(page_size).to_be_visible(timeout=30_000)
            page_size.click(timeout=30_000)
            option = self.page.locator(".cdk-overlay-container:visible").get_by_text(
                expand_value,
                exact=True,
            ).filter(visible=True).first
            expect(option).to_be_visible(timeout=30_000)
            option.click(timeout=30_000)
            self._wait_for_loader(timeout=30_000, root=root)
            return

        action = None
        if reload:
            action = root.locator('smt-data-table-menu smt-button-group-item[smtvalue="reload"] button').first
        elif open_filter:
            action = root.locator("smt-data-table-filter button").first
        elif open_setting:
            action = root.locator('smt-data-table-menu smt-button-group-item[smtvalue="menu"] button').first
        if action is None:
            raise ValueError(
                'grid_controller(): search, expand="50"/"100"/"500"/"1000", reload, open_filter yoki open_setting dan bittasini bering'
            )
        expect(action).to_be_visible(timeout=30_000)
        action.click(timeout=30_000)
        if reload:
            self._wait_for_loader(timeout=30_000, root=root)

    # ------------------------------------------------------------------------------------------------------------------

    def grid_setting(self, *, menu_name, field_name, search_name=None, timeout=30_000):
        """Grid settingda ustunni va ixtiyoriy search maydonini yoqadi.

        A2 table-setting va search-setting dialoglarini boshqaradi va
        saqlangan ustun indeksini qaytaradi.
        """
        self._validate_options(
            'grid_setting',
            timeout=timeout,
        )
        for argument_name, value in (("menu_name", menu_name), ("field_name", field_name)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"grid_setting(): {argument_name} bo'sh bo'lmagan string bo'lishi kerak")
        if search_name is not None and (not isinstance(search_name, str) or not search_name.strip()):
            raise ValueError("grid_setting(): search_name None yoki bo'sh bo'lmagan string bo'lishi kerak")

        grid = self._content_root(None).locator("smt-data-table").filter(visible=True).first
        expect(grid).to_be_visible(timeout=timeout)

        self.grid_controller(open_setting=True)
        menu = self.page.get_by_role("menu").filter(visible=True).last
        expect(menu).to_be_visible(timeout=timeout)
        menu.get_by_role("menuitem", name=menu_name, exact=True).click(timeout=timeout)

        setting_dialog = self.page.get_by_role("dialog").filter(
            has=self.page.get_by_role("heading", name="Настройки таблицы", exact=True)
        ).first
        expect(setting_dialog).to_be_visible(timeout=timeout)
        active_fields = setting_dialog.locator(".smt-main-list")
        active_field = active_fields.get_by_title(field_name, exact=True)
        if active_field.count() == 0:
            inactive_field = setting_dialog.get_by_role("button", name=field_name, exact=True).first
            expect(inactive_field).to_be_visible(timeout=timeout)
            inactive_field.click(timeout=timeout)
        expect(active_fields.get_by_title(field_name, exact=True)).to_be_visible(timeout=timeout)

        setting_dialog.get_by_role("button", name="Сохранить", exact=True).filter(visible=True).first.click(timeout=timeout)
        expect(setting_dialog).not_to_be_visible(timeout=timeout)

        if search_name is not None:
            self.grid_controller(open_setting=True)
            search_menu = self.page.get_by_role("menu").filter(visible=True).last
            expect(search_menu).to_be_visible(timeout=timeout)
            search_menu.get_by_role("menuitem", name="Настройки поиска", exact=True).click(timeout=timeout)

            search_dialog = self.page.get_by_role("dialog").filter(
                has=self.page.get_by_role("heading", name="Настройки поиска", exact=True)
            ).first
            expect(search_dialog).to_be_visible(timeout=timeout)
            search_option = search_dialog.locator("label[smt-checkbox]").filter(
                has_text=_whitespace_agnostic_pattern(search_name, exact=True)
            ).first
            expect(search_option).to_be_visible(timeout=timeout)
            self._set_toggle(search_option.get_by_role("checkbox"), True, timeout=timeout)
            search_save = search_dialog.get_by_role(
                "button",
                name=re.compile(r"^(Сохранить|Подтвердить)$"),
            ).filter(visible=True).first
            expect(search_save).to_be_visible(timeout=timeout)
            search_save.click(timeout=timeout)
            expect(search_dialog).not_to_be_visible(timeout=timeout)

        self.wait_for_loader(timeout=timeout)

        # Headerda selection/action uchun texnik ``div`` ham bo'lishi mumkin,
        # rowdagi ``.smt-data-cell`` esa faqat haqiqiy data ustunlarini sanaydi.
        # Indeks grid_cell() bilan bir xil koordinata tizimida bo'lishi uchun
        # faqat data-smt-col-key mavjud headerlarni hisoblaymiz.
        headers = grid.locator(".smt-grid-header").first.locator(
            ":scope > div[data-smt-col-key]"
        )
        expected_header = _whitespace_agnostic_pattern(field_name, exact=True)
        expect(headers.filter(has_text=expected_header).first).to_be_visible(timeout=timeout)
        for index in range(headers.count()):
            if expected_header.search(headers.nth(index).inner_text()):
                return index
        raise AssertionError(f"grid_setting(): saqlangandan keyin '{field_name}' ustuni topilmadi")

    # ------------------------------------------------------------------------------------------------------------------

    def grid_cell(
        self,
        row,
        index,
        *,
        expect_value=_UNSET,
        return_value=False,
        remove_spaces=False,
    ):
        """A2 grid row ichidagi cellni index bo'yicha tekshiradi yoki o'qiydi."""
        self._validate_options(
            'grid_cell',
            index=index,
            return_value=return_value,
            remove_spaces=remove_spaces,
        )

        # Direct row children only. Nested [data-smt-col-key] would shift
        # indices; checkbox column matches legacy tbl-cell index 0.
        cells = row.locator(":scope > .smt-data-cell")
        if cells.count() == 0:
            cells = row.locator(
                ":scope > .smt-grid-checkbox-cell, :scope > [data-smt-col-key]"
            )
        cell = cells.nth(index)
        expect(cell).to_be_visible(timeout=10_000)
        if expect_value is not _UNSET:
            expected = _whitespace_agnostic_pattern(expect_value) if remove_spaces else str(expect_value)
            expect(cell).to_contain_text(expected, timeout=10_000)
        if return_value:
            value = cell.inner_text().strip()
            return re.sub(r"\s+", "", value) if remove_spaces else " ".join(value.split())
        return cell

    # ------------------------------------------------------------------------------------------------------------------

    @report_web_action
    def navigate_to(
        self,
        tab="Главное",
        name="Организации",
        timeout=30_000,
    ):
        """A2 shell menu tabidan menuitem orqali boshqa A2 formani ochadi."""
        self._validate_options(
            'navigate_to',
            timeout=timeout,
        )
        self._dismiss_session_lock()
        root = self.page.locator("app-header, lib-navigation-menu").first
        tab_button = root.get_by_role("button", name=tab, exact=True).filter(visible=True)
        expect(tab_button).to_have_count(1, timeout=timeout)
        expect(tab_button).to_be_visible(timeout=timeout)
        tab_button.click(timeout=timeout)

        menu = self.page.locator(
            ".cdk-overlay-container [role='menu']:visible"
        ).last
        expect(menu).to_be_visible(timeout=timeout)
        item = menu.get_by_role("menuitem", name=name, exact=True).filter(visible=True)
        expect(item).to_have_count(1, timeout=timeout)
        expect(item).to_be_visible(timeout=timeout)
        item.click(timeout=timeout)
        self.wait_for_loader(timeout=timeout)

    # ------------------------------------------------------------------------------------------------------------------

    @report_web_action
    def navigate_to_form(
        self,
        *,
        navbar_tab,
        menu_column,
        menu_item,
        page_links=None,
        add_icon=False,
        timeout=60_000,
    ):
        """BasePage navigate_to_form kontraktini A2 shell orqali bajaradi.

        menu_column berilsa shu nomli ko'rinadigan guruh/submenu talab qilinadi.
        page_links string yoki ketma-ket linklar ro'yxati bo'lishi mumkin.
        """
        self._validate_options(
            'navigate_to_form',
            add_icon=add_icon,
            timeout=timeout,
        )
        links = [] if page_links is None else [page_links] if isinstance(page_links, str) else list(page_links)
        # Never bare ``header``: in-page/card headers steal .first and navbar
        # tabs resolve to count 0 (Возвраты → next Продажа).
        header = self.page.locator("app-header, lib-navigation-menu").first
        self._dismiss_session_lock()
        self.page.keyboard.press("Escape")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=min(timeout, 5_000))
        except PlaywrightTimeoutError:
            pass
        tab_button = header.get_by_role("button", name=navbar_tab, exact=True)
        try:
            expect(tab_button).to_have_count(1, timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError):
            tab_button = self.page.locator("app-header").get_by_role(
                "button", name=navbar_tab, exact=True
            )
            expect(tab_button).to_have_count(1, timeout=timeout)
        tab_button.first.evaluate(
            "el => el.scrollIntoView({inline: 'center', block: 'nearest'})"
        )
        expect(tab_button.first).to_be_visible(timeout=timeout)
        # SPA still reports the previous form navigation as in-flight; waiting
        # on that click stalls the megamenu on the old URL.
        tab_button.first.click(timeout=timeout, no_wait_after=True)
        menu = self.page.locator(
            ".cdk-overlay-container [role='menu']:visible"
        ).last
        expect(menu).to_be_visible(timeout=timeout)
        column = menu
        if menu_column is not None:
            column_name = _whitespace_agnostic_pattern(menu_column, exact=True)
            # Megamenu ustuni — ``<h3>`` (kernel navigation-menu). Ichidagi
            # menuitem bilan bir xil nom bo'lsa (Визиты) get_by_text 2 ta match.
            heading = menu.locator("h3").get_by_text(column_name).filter(visible=True)
            try:
                expect(heading).to_have_count(1, timeout=min(timeout, 3_000))
                column = heading.locator("xpath=ancestor::li[1]")
            except (AssertionError, PlaywrightTimeoutError):
                column = menu.get_by_role("menuitem", name=column_name).filter(visible=True)
                expect(column).to_have_count(1, timeout=timeout)
                expect(column).to_be_visible(timeout=timeout)
                if column.get_attribute("aria-haspopup") == "menu":
                    column.click(timeout=timeout, no_wait_after=True)
                    column = self.page.get_by_role("menu").filter(visible=True).last
            expect(column).to_be_visible(timeout=timeout)
        item = column.get_by_role("menuitem", name=menu_item, exact=True).filter(visible=True)
        expect(item).to_have_count(1, timeout=timeout)
        expect(item).to_be_visible(timeout=timeout)

        target = item
        if add_icon:
            item_row = item.locator("xpath=ancestor::*[self::li or @role='menuitem'][1]")
            add_target = item_row.get_by_role("button").or_(item_row.get_by_role("link")).filter(
                has_text=re.compile(r"^\s*(\+|создать|add)\s*$", re.IGNORECASE)
            ).first
            expect(add_target).to_be_visible(timeout=timeout)
            target = add_target
        target.click(timeout=timeout, no_wait_after=True)
        self.wait_for_loader(timeout=timeout)

        for page_link in links:
            self.click_sibling_page_link(page_link, timeout=timeout)
        return target

    def click_sibling_page_link(self, page_link, timeout=60_000):
        """Related-pages strip (``lib-page-siblings``), not any page-wide ``<a>``."""
        host = self.page.locator("lib-page-siblings").filter(visible=True).first
        try:
            expect(host).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(
                f"page_link='{page_link}' uchun lib-page-siblings topilmadi; "
                f"url={self.page.url}"
            ) from exc

        # Prefer the sibling ``<a>`` (smt-button may expose link+button roles).
        link = host.locator(":scope ul > li > a").filter(
            has_text=re.compile(rf"^{re.escape(page_link)}$")
        )
        try:
            expect(link.first).to_be_visible(timeout=min(timeout, 5_000))
        except (AssertionError, PlaywrightTimeoutError):
            link = host.get_by_role("link", name=page_link, exact=True)
            if link.count() == 0:
                link = host.get_by_role("button", name=page_link, exact=True)
        if link.count() > 1:
            current = urlsplit(self.page.url).path.rstrip("/")
            picked = None
            for i in range(link.count()):
                href = link.nth(i).get_attribute("href") or ""
                href_path = urlsplit(href).path.rstrip("/")
                if href_path and href_path != current:
                    picked = link.nth(i)
                    break
            link = picked or link.last
        try:
            expect(link).to_have_count(1, timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(
                f"page_link='{page_link}' siblings ichida yagona emas; "
                f"url={self.page.url}"
            ) from exc
        href = link.get_attribute("href") or ""
        # Overflow-clipped siblings: Playwright force-click hits the wrong point.
        link.evaluate("el => el.click()")
        self.wait_for_loader(timeout=timeout)
        href_path = urlsplit(href).path.strip("/")
        if href_path:
            try:
                self.page.wait_for_url(
                    re.compile(re.escape(href_path)),
                    timeout=min(timeout, 15_000),
                )
            except PlaywrightTimeoutError:
                pass

    # ------------------------------------------------------------------------------------------------------------------

    def _open_filial_list(self, timeout):
        """Kernel/A2 header filial pickerini ochadi."""
        root = self._resolve_root("header")
        trigger = root.locator(
            'button[data-project-filial-trigger], '
            'button[data-testid*="project-filial"]'
        ).or_(
            root.get_by_role(
                "button",
                name=re.compile(r"^\s*(?:TRADE|SFA)\b", re.IGNORECASE),
            )
        ).filter(visible=True).first
        expect(trigger).to_be_visible(timeout=timeout)
        trigger.click(timeout=timeout)
        filial_list = self.page.get_by_test_id(
            "shell-project-filial--filial-list"
        )
        expect(filial_list).to_be_visible(timeout=timeout)
        return trigger, filial_list

    def list_filials(self, timeout=30_000):
        """Filial option matnlarini o'qiydi, joriy filialni o'zgartirmaydi."""
        self._validate_options("list_filials", timeout=timeout)
        _trigger, filial_list = self._open_filial_list(timeout)
        names = filial_list.get_by_role("option").all_inner_texts()
        self.page.keyboard.press("Escape")
        expect(filial_list).to_be_hidden(timeout=timeout)
        return names

    def switch_filial(
        self,
        name=None,
        timeout=30_000,
        *,
        first_filial=False,
    ):
        """A2 shell filial selectori orqali filialni almashtiradi."""
        self._validate_options(
            'switch_filial',
            timeout=timeout,
            first_filial=first_filial,
        )
        if first_filial and name is not None:
            raise ValueError("switch_filial(): name va first_filial=True birga berilmaydi")
        if not first_filial and name is None:
            raise ValueError("switch_filial(): name yoki first_filial=True berilishi kerak")

        trigger, filial_list = self._open_filial_list(timeout)
        target_name = name
        if first_filial:
            target_name = first_non_admin_filial(
                filial_list.get_by_role("option").all_inner_texts()
            )
        option = filial_list.get_by_role("option", name=target_name, exact=True).first
        expect(option).to_be_visible(timeout=timeout)
        option.click(timeout=timeout)
        expect(trigger).to_contain_text(target_name, timeout=timeout)
        self.wait_for_loader(timeout=timeout)
        record_filial(self.page, target_name)
        return option

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni(
        self,
        expected_text=None,
        button_name="да",
    ):
        """A2/CDK confirm dialogini tasdiqlaydi."""
        matcher = (
            button_name
            if isinstance(button_name, re.Pattern)
            else re.compile(rf"^\s*{re.escape(str(button_name))}\s*$", re.IGNORECASE)
        )
        confirm = self._visible_modal_candidates(root="body").filter(
            has=self.page.get_by_role("button", name=matcher)
        ).last
        expect(confirm).to_be_visible(timeout=10_000)
        if expected_text:
            expect(confirm).to_contain_text(expected_text, timeout=10_000)
        button = confirm.get_by_role("button", name=matcher).first
        expect(button).to_be_visible(timeout=10_000)
        button.click(timeout=10_000)
        expect(confirm).to_be_hidden(timeout=10_000)
        self._wait_blocking_overlay_gone()

    # ------------------------------------------------------------------------------------------------------------------

    def close_biruni_alert(self, *expected_text):
        """Ko'rinadigan A2/CDK error dialogini tekshiradi va yopadi."""
        alert = self._visible_error_locator(root="body")
        expect(alert).to_be_visible(timeout=10_000)
        for value in expected_text:
            if value:
                expect(alert).to_contain_text(value, timeout=10_000)

        close = alert.get_by_role(
            "button",
            name=re.compile(r"закрыть|close|×", re.IGNORECASE),
        ).filter(visible=True).first
        expect(close).to_be_visible(timeout=10_000)
        close.click(timeout=10_000)
        expect(alert).to_be_hidden(timeout=10_000)
