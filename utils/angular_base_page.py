import re

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


_UNSET = object()


class AngularBasePage:
    """Smartup A2 yangi Angular formalarining umumiy UI primitivlari.

    Bu class ``smt-*`` komponentlari, CDK overlay va A2 shell uchun yozilgan.
    Eski AngularJS/Biruni formalarida ``utils.base_page.BasePage`` ishlatiladi.
    """

    def __init__(self, page):
        self.page = page

    # ------------------------------------------------------------------------------------------------------------------

    def _resolve_root(self, root):
        if root is None:
            return self.page
        return self.page.locator(root) if isinstance(root, str) else root

    # ------------------------------------------------------------------------------------------------------------------

    def _label_pattern(self, label):
        if isinstance(label, re.Pattern):
            return label
        return re.compile(
            rf"^\s*{re.escape(str(label))}\s*(?:\*)?\s*$",
            re.IGNORECASE,
        )

    # ------------------------------------------------------------------------------------------------------------------

    def control(
        self,
        label,
        *,
        index=0,
        root="main",
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
                expect(candidate).to_be_visible(timeout=500)
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

    def button(
        self,
        name,
        *,
        click=False,
        exact=True,
        index=0,
        root="main",
        timeout=10_000,
        expect_visible=True,
    ):
        """A2 buttonni semantic role/name bo'yicha topadi va ixtiyoriy bosadi."""
        root = self._resolve_root(root)
        button = root.get_by_role("button", name=name, exact=exact).nth(index)
        if expect_visible:
            expect(button).to_be_visible(timeout=timeout)
        if click:
            button.click()
        return button

    # ------------------------------------------------------------------------------------------------------------------

    def tab(
        self,
        name,
        *,
        click=True,
        exact=True,
        index=0,
        root="main",
        timeout=10_000,
    ):
        """A2 ``smt-tab-button`` yoki semantic tab/buttonni topadi."""
        root = self._resolve_root(root)
        role_tab = root.get_by_role("tab", name=name, exact=exact).nth(index)
        role_button = root.get_by_role("button", name=name, exact=exact).nth(index)
        smt_tab = root.locator("smt-tab-button").filter(
            has_text=self._label_pattern(name)
        ).nth(index)
        tab = role_tab.or_(role_button).or_(smt_tab).first
        expect(tab).to_be_visible(timeout=timeout)
        if click:
            tab.click()
        return tab

    # ------------------------------------------------------------------------------------------------------------------

    def input(
        self,
        locator=None,
        value=_UNSET,
        *,
        label=None,
        placeholder=None,
        expect_value=_UNSET,
        return_value=False,
        index=0,
        root="main",
        clear=True,
        press_tab=False,
        timeout=10_000,
    ):
        """A2 ``smt-input`` ichidagi native input/textarea bilan ishlaydi."""
        root = self._resolve_root(root)
        sources = sum(
            source is not None for source in (locator, label, placeholder)
        )
        if sources != 1:
            raise ValueError(
                "input(): locator, label yoki placeholder dan aynan bittasini bering"
            )

        if label is not None:
            control = self.control(label, index=index, root=root, timeout=timeout)
            input_el = control.locator(
                "input:not([type='checkbox']):not([type='radio']):not([type='hidden']), "
                "textarea"
            ).first
        elif placeholder is not None:
            input_el = root.get_by_placeholder(placeholder).nth(index)
        else:
            input_el = root.locator(locator).nth(index) if isinstance(locator, str) else locator

        expect(input_el).to_be_visible(timeout=timeout)

        if value is not _UNSET:
            input_el.click()
            if clear:
                input_el.press("ControlOrMeta+A")
                input_el.press("Backspace")
            input_el.fill(str(value))
            if press_tab:
                input_el.press("Tab")

        expected = expect_value
        if expected is _UNSET and value is not _UNSET:
            expected = str(value)
        if expected is not _UNSET:
            expect(input_el).to_have_value(expected, timeout=timeout)

        if return_value:
            return input_el.input_value()
        return input_el

    # ------------------------------------------------------------------------------------------------------------------

    def select(
        self,
        label,
        value=_UNSET,
        *,
        expect_value=_UNSET,
        return_value=False,
        search_text=None,
        exact=True,
        index=0,
        root="main",
        timeout=10_000,
    ):
        """A2 ``smt-data-select``dan option tanlaydi yoki joriy qiymatni tekshiradi."""
        root = self._resolve_root(root)
        control = self.control(label, index=index, root=root, timeout=timeout)
        select = control.locator("smt-data-select").first
        trigger = select.locator("smt-select-trigger").first
        search = trigger.locator(
            "input:not([type='checkbox']):not([type='radio'])"
        ).first

        expect(select).to_be_visible(timeout=timeout)
        expect(trigger).to_be_visible(timeout=timeout)
        expect(search).to_be_visible(timeout=timeout)

        if value is not _UNSET:
            option_text = str(value)
            current_value = search.input_value().strip()
            if current_value != option_text:
                trigger.click()
                query = option_text if search_text is None else str(search_text)
                if query:
                    search.press("ControlOrMeta+A")
                    search.press("Backspace")
                    search.fill(query)

                option_matcher = (
                    re.compile(
                        rf"^\s*{re.escape(option_text)}\s*$",
                        re.IGNORECASE,
                    )
                    if exact
                    else re.compile(re.escape(option_text), re.IGNORECASE)
                )
                dropdown = self.page.locator(
                    ".cdk-overlay-container smt-select-dropdown:visible"
                ).last
                expect(dropdown).to_be_visible(timeout=timeout)
                option = dropdown.locator("li").filter(
                    has_text=option_matcher
                ).first
                expect(option).to_be_visible(timeout=timeout)
                option.click()
                if dropdown.is_visible():
                    self.page.mouse.click(1, 1)
                expect(dropdown).to_be_hidden(timeout=timeout)
                expect(
                    self.page.locator(
                        ".cdk-overlay-backdrop.cdk-overlay-backdrop-showing:visible"
                    )
                ).to_have_count(0, timeout=timeout)

        expected = expect_value
        if expected is _UNSET and value is not _UNSET:
            expected = str(value)
        if expected is not _UNSET:
            expect(search).to_have_value(expected, timeout=timeout)

        if return_value:
            return search.input_value()
        return select

    # ------------------------------------------------------------------------------------------------------------------

    def _toggle_by_label(
        self,
        label,
        *,
        role,
        index=0,
        root="main",
        timeout=10_000,
    ):
        root = self._resolve_root(root)
        pattern = self._label_pattern(label)
        visible_label = root.get_by_text(pattern).filter(visible=True).first
        expect(visible_label).to_be_visible(timeout=timeout)

        controls = root.locator("smt-control").filter(
            has=self.page.locator("label").filter(has_text=pattern)
        )
        candidates = controls.get_by_role(role)

        if candidates.count() == 0:
            labels = root.get_by_text(pattern).filter(visible=True)
            matched = []
            for label_index in range(labels.count()):
                label_item = labels.nth(label_index)
                container = label_item.locator(
                    f"xpath=ancestor::*[.//*[@role='{role}']][1]"
                )
                if container.count() == 0:
                    continue
                role_control = container.get_by_role(role).first
                if role_control.count() > 0:
                    matched.append(role_control)
            if index >= len(matched):
                shown = getattr(label, "pattern", label)
                raise AssertionError(
                    f"Angular {role} topilmadi: label={shown}, index={index}"
                )
            toggle = matched[index]
        else:
            toggle = candidates.nth(index)

        expect(toggle).to_be_visible(timeout=timeout)
        return toggle

    # ------------------------------------------------------------------------------------------------------------------

    def _set_toggle(self, toggle, checked, *, timeout=10_000):
        role = toggle.get_attribute("role")
        if role in {"switch", "checkbox", "radio"}:
            current = (toggle.get_attribute("aria-checked") or "").lower() == "true"
            if current != checked:
                toggle.click()
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

    def switch(
        self,
        locator=None,
        checked=_UNSET,
        *,
        label=None,
        expect_checked=_UNSET,
        return_value=False,
        index=0,
        root="main",
        timeout=10_000,
    ):
        """A2 ``role=switch`` controlini label yoki tayyor locator bilan boshqaradi."""
        if (locator is None) == (label is None):
            raise ValueError("switch(): locator yoki label dan aynan bittasini bering")

        if label is not None:
            toggle = self._toggle_by_label(
                label,
                role="switch",
                index=index,
                root=root,
                timeout=timeout,
            )
        else:
            root = self._resolve_root(root)
            toggle = root.locator(locator).nth(index) if isinstance(locator, str) else locator
            expect(toggle).to_be_visible(timeout=timeout)

        if checked is not _UNSET:
            self._set_toggle(toggle, bool(checked), timeout=timeout)

        expected = checked if checked is not _UNSET else expect_checked
        if expected is not _UNSET:
            if toggle.get_attribute("role"):
                expect(toggle).to_have_attribute(
                    "aria-checked",
                    "true" if expected else "false",
                    timeout=timeout,
                )
            else:
                expect(toggle).to_be_checked(timeout=timeout) if expected else expect(
                    toggle
                ).not_to_be_checked(timeout=timeout)

        if return_value:
            if toggle.get_attribute("role"):
                return (toggle.get_attribute("aria-checked") or "").lower() == "true"
            return toggle.is_checked()
        return toggle

    # ------------------------------------------------------------------------------------------------------------------

    def checkbox(
        self,
        locator=None,
        checked=_UNSET,
        *,
        label=None,
        expect_checked=_UNSET,
        return_value=False,
        index=0,
        root="main",
        timeout=10_000,
    ):
        """A2 ``role=checkbox`` controlini label yoki tayyor locator bilan boshqaradi."""
        if (locator is None) == (label is None):
            raise ValueError("checkbox(): locator yoki label dan aynan bittasini bering")

        if label is not None:
            toggle = self._toggle_by_label(
                label,
                role="checkbox",
                index=index,
                root=root,
                timeout=timeout,
            )
        else:
            root = self._resolve_root(root)
            toggle = root.locator(locator).nth(index) if isinstance(locator, str) else locator
            expect(toggle).to_be_visible(timeout=timeout)

        if checked is not _UNSET:
            self._set_toggle(toggle, bool(checked), timeout=timeout)

        expected = checked if checked is not _UNSET else expect_checked
        if expected is not _UNSET:
            role = toggle.get_attribute("role")
            if role:
                expect(toggle).to_have_attribute(
                    "aria-checked",
                    "true" if expected else "false",
                    timeout=timeout,
                )
            else:
                expect(toggle).to_be_checked(timeout=timeout) if expected else expect(
                    toggle
                ).not_to_be_checked(timeout=timeout)

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
        checked=True,
        return_value=False,
        index=0,
        root="main",
        timeout=10_000,
    ):
        """A2 semantic radio controlini tanlaydi va holatini tekshiradi."""
        radio = self._toggle_by_label(
            label,
            role="radio",
            index=index,
            root=root,
            timeout=timeout,
        )
        self._set_toggle(radio, checked, timeout=timeout)
        if return_value:
            return (radio.get_attribute("aria-checked") or "").lower() == "true"
        return radio

    # ------------------------------------------------------------------------------------------------------------------

    def choice(
        self,
        label,
        option,
        *,
        index=0,
        root="main",
        timeout=10_000,
    ):
        """``smt-control`` ichidagi segmented button optionni tanlaydi."""
        control = self.control(label, index=index, root=root, timeout=timeout)
        button = control.get_by_role("button", name=option, exact=True).first
        expect(button).to_be_visible(timeout=timeout)
        button.click()
        return button

    # ------------------------------------------------------------------------------------------------------------------

    def text(self, *values, root="main", timeout=10_000):
        content = self._resolve_root(root)
        expect(content).to_be_visible(timeout=timeout)
        for value in values:
            if value:
                expect(content).to_contain_text(value, timeout=timeout)
        return content

    # ------------------------------------------------------------------------------------------------------------------

    def form_view(
        self,
        label,
        *,
        expect_value=_UNSET,
        return_value=False,
        remove_spaces=False,
        index=0,
        root="main",
        timeout=10_000,
    ):
        """A2 view'dagi readonly ``smt-input`` qiymatini tekshiradi yoki qaytaradi."""
        field = self.input(
            label=label,
            index=index,
            root=root,
            timeout=timeout,
        )
        expect(field).to_have_attribute("readonly", re.compile(r".*"), timeout=timeout)

        actual = field.input_value()
        if expect_value is not _UNSET:
            if remove_spaces:
                if not isinstance(expect_value, str):
                    raise TypeError(
                        "form_view(remove_spaces=True): expect_value string bo'lishi kerak"
                    )
                actual_normalized = re.sub(r"\s+", "", actual)
                expected_normalized = re.sub(r"\s+", "", expect_value)
                if actual_normalized != expected_normalized:
                    raise AssertionError(
                        f"Readonly field '{label}' qiymati: "
                        f"kutilgan={expected_normalized!r}, amaldagi={actual_normalized!r}"
                    )
            else:
                expect(field).to_have_value(expect_value, timeout=timeout)

        if return_value:
            return re.sub(r"\s+", "", actual) if remove_spaces else actual
        return field

    # ------------------------------------------------------------------------------------------------------------------

    def _visible_error_locator(self, root="body"):
        error_text = re.compile(r"ошибка|error|URL\s*:", re.IGNORECASE)
        root = self._resolve_root(root)
        return root.locator(
            "#biruniAlertExtended:visible, #biruniAlert:visible, "
            "[role='alert']:visible, [role='dialog']:visible, "
            ".alert-danger:visible, .cdk-overlay-pane:visible"
        ).filter(has_text=error_text).last

    # ------------------------------------------------------------------------------------------------------------------

    def _visible_error_text(self, root="body"):
        error = self._visible_error_locator(root=root)
        if error.count() == 0 or not error.is_visible():
            return ""
        return re.sub(r"\s+", " ", error.inner_text()).strip()

    # ------------------------------------------------------------------------------------------------------------------

    def wait_for_loader(
        self,
        timeout=30_000,
        *,
        appear_timeout=2_000,
        root="main",
    ):
        """A2 skeleton/busy holati paydo bo'lsa, to'liq tugashini kutadi."""
        root = self._resolve_root(root)
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

    def expect_page(
        self,
        *,
        heading=None,
        url=None,
        title=None,
        ready=None,
        timeout=30_000,
        check_unblocked=True,
        root="main",
    ):
        """A2 sahifani URL/title/visible text/stabil component orqali tekshiradi."""
        if heading is None and url is None and title is None and ready is None:
            raise ValueError(
                "expect_page(): heading, url, title yoki ready dan kamida bittasi kerak"
            )

        if url is not None:
            pattern = url if isinstance(url, re.Pattern) else re.compile(re.escape(url))
            expect(self.page).to_have_url(pattern, timeout=timeout)

        if title is not None:
            pattern = title if isinstance(title, re.Pattern) else re.compile(re.escape(title))
            expect(self.page).to_have_title(pattern, timeout=timeout)

        scope = self._resolve_root(root)
        if heading is not None:
            target = scope.get_by_text(
                heading,
                exact=not isinstance(heading, re.Pattern),
            ).filter(visible=True).first
            expect(target).to_be_visible(timeout=timeout)

        if ready is not None:
            target = (
                scope.locator(ready)
                if isinstance(ready, str)
                else ready
            )
            expect(target.first).to_be_visible(timeout=timeout)

        if check_unblocked:
            self.wait_for_loader(timeout=timeout, root=scope)
        return True

    # ------------------------------------------------------------------------------------------------------------------

    def grid(
        self,
        text=None,
        *contains,
        root="main",
        click=False,
        checkbox=None,
        is_empty=False,
        is_visible=False,
        timeout=10_000,
    ):
        """A2 ``smt-data-table`` qatorlarini boshqaradi."""
        if checkbox not in (None, "row", "all"):
            raise ValueError('grid(checkbox=...): "row" yoki "all" bo\'lishi kerak')
        if is_empty and (text is not None or contains or click or checkbox is not None or is_visible):
            raise ValueError("grid(is_empty=True) boshqa qator amallari bilan ishlatilmaydi")
        if is_visible and text is None:
            raise ValueError("grid(is_visible=True) uchun text berilishi kerak")

        if root is None or root == "main":
            grid = self._resolve_root(root or "main").locator(
                "smt-data-table, smt-table"
            ).filter(visible=True).first
        else:
            grid = self._resolve_root(root)

        expect(grid).to_be_visible(timeout=timeout)
        self.wait_for_loader(timeout=timeout, root=grid)
        rows = grid.locator(".smt-data-row")

        if is_empty:
            return rows.count() == 0

        row = rows.filter(has_text=text).first
        if is_visible:
            return row.is_visible()

        if checkbox == "all":
            toggle = grid.get_by_role("checkbox").first
            expect(toggle).to_be_visible(timeout=timeout)
            self._set_toggle(toggle, True, timeout=timeout)
            return toggle

        expect(row).to_be_visible(timeout=timeout)
        for value in contains:
            expect(row).to_contain_text(value, timeout=timeout)
        if checkbox == "row":
            toggle = row.get_by_role("checkbox").first
            expect(toggle).to_be_visible(timeout=timeout)
            self._set_toggle(toggle, True, timeout=timeout)
        if click:
            row.click()
        return row

    # ------------------------------------------------------------------------------------------------------------------

    def grid_controller(
        self,
        *,
        search=None,
        expand=None,
        root="main",
        timeout=30_000,
    ):
        """A2 list search va page-size controlini boshqaradi."""
        if (search is None) == (expand is None):
            raise ValueError(
                "grid_controller(): search yoki expand dan aynan bittasini bering"
            )

        root = self._resolve_root(root)
        if search is not None:
            field = root.locator("input[type='search']").filter(visible=True).first
            expect(field).to_be_visible(timeout=timeout)
            field.click()
            field.press("ControlOrMeta+A")
            field.press("Backspace")
            if str(search):
                field.fill(str(search))
            expect(field).to_have_value(str(search), timeout=timeout)
            self.wait_for_loader(timeout=timeout, root=root)
            return field

        expand_value = str(expand)
        if expand_value not in {"50", "100", "500", "1000"}:
            raise ValueError(
                'grid_controller(expand=...): "50", "100", "500" yoki "1000" bo\'lishi kerak'
            )
        page_size = root.get_by_role(
            "button",
            name=re.compile(r"Строк на странице|Rows per page", re.IGNORECASE),
        ).first
        expect(page_size).to_be_visible(timeout=timeout)
        page_size.click()
        option = self.page.locator(".cdk-overlay-container:visible").get_by_text(
            expand_value,
            exact=True,
        ).filter(visible=True).first
        expect(option).to_be_visible(timeout=timeout)
        option.click()
        self.wait_for_loader(timeout=timeout, root=root)
        return page_size

    # ------------------------------------------------------------------------------------------------------------------

    def navigate_to(
        self,
        *,
        tab,
        name=None,
        path=None,
        root="header",
        timeout=30_000,
    ):
        """A2 shell menu tabidan menuitem orqali boshqa A2 formani ochadi."""
        if (name is None) == (path is None):
            raise ValueError("navigate_to(): name yoki path dan aynan bittasini bering")

        root = self._resolve_root(root)
        tab_button = root.get_by_role("button", name=tab, exact=True).first
        expect(tab_button).to_be_visible(timeout=timeout)
        tab_button.click()

        menu = self.page.locator(
            ".cdk-overlay-container [role='menu']:visible"
        ).last
        expect(menu).to_be_visible(timeout=timeout)
        if path is not None:
            item = menu.locator(
                f'a[role="menuitem"][href$="/a2/{path}"]'
            ).first
        else:
            item = menu.get_by_role("menuitem", name=name, exact=True).first
        expect(item).to_be_visible(timeout=timeout)
        item.click()
        self.wait_for_loader(timeout=timeout)
        return item

    # ------------------------------------------------------------------------------------------------------------------

    def switch_filial(
        self,
        name,
        *,
        project="SFA",
        root="header",
        timeout=30_000,
    ):
        """A2 shell filial selectori orqali filialni almashtiradi."""
        root = self._resolve_root(root)
        trigger = root.locator(
            'button[data-testid*="project-filial"]'
        ).filter(visible=True).first
        if trigger.count() == 0:
            trigger = root.get_by_role(
                "button",
                name=re.compile(rf"^\s*{re.escape(project)}\b", re.IGNORECASE),
            ).first

        expect(trigger).to_be_visible(timeout=timeout)
        trigger.click()
        filial_list = self.page.get_by_test_id(
            "shell-project-filial--filial-list"
        )
        expect(filial_list).to_be_visible(timeout=timeout)
        option = filial_list.get_by_role("option", name=name, exact=True).first
        expect(option).to_be_visible(timeout=timeout)
        option.click()
        expect(trigger).to_contain_text(name, timeout=timeout)
        self.wait_for_loader(timeout=timeout)
        return option

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni(
        self,
        expected_text=None,
        *,
        button_name=re.compile(r"^\s*(да|yes)\s*$", re.IGNORECASE),
        root="body",
        timeout=10_000,
    ):
        """Legacy Biruni yoki A2/CDK confirm dialogini tasdiqlaydi."""
        root = self._resolve_root(root)
        confirm = root.locator(
            "#biruniConfirm:visible, [role='dialog']:visible, .cdk-overlay-pane:visible"
        ).filter(
            has=self.page.get_by_role("button", name=button_name)
        ).last
        expect(confirm).to_be_visible(timeout=timeout)
        if expected_text:
            expect(confirm).to_contain_text(expected_text, timeout=timeout)
        button = confirm.get_by_role("button", name=button_name).first
        expect(button).to_be_visible(timeout=timeout)
        button.click()
        expect(confirm).to_be_hidden(timeout=timeout)
        return confirm

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni_if_visible(
        self,
        expected_text=None,
        *,
        button_name=re.compile(r"^\s*(да|yes)\s*$", re.IGNORECASE),
        root="body",
        timeout=1_000,
    ):
        root = self._resolve_root(root)
        confirm = root.locator(
            "#biruniConfirm:visible, [role='dialog']:visible, .cdk-overlay-pane:visible"
        ).filter(
            has=self.page.get_by_role("button", name=button_name)
        ).last
        try:
            expect(confirm).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError):
            return False
        if expected_text:
            expect(confirm).to_contain_text(expected_text, timeout=timeout)
        confirm.get_by_role("button", name=button_name).first.click()
        expect(confirm).to_be_hidden(timeout=timeout)
        return True

    # ------------------------------------------------------------------------------------------------------------------

    def close_biruni_alert(
        self,
        *expected_text,
        root="body",
        timeout=10_000,
    ):
        """A2/legacy ko'rinadigan error alertini tekshiradi va yopadi."""
        alert = self._visible_error_locator(root=root)
        expect(alert).to_be_visible(timeout=timeout)
        for value in expected_text:
            if value:
                expect(alert).to_contain_text(value, timeout=timeout)

        close = alert.locator("button.close").first
        if close.count() == 0:
            close = alert.get_by_role(
                "button",
                name=re.compile(r"закрыть|close|×", re.IGNORECASE),
            ).first
        expect(close).to_be_visible(timeout=timeout)
        close.click()
        expect(alert).to_be_hidden(timeout=timeout)
        return alert

    # ------------------------------------------------------------------------------------------------------------------

    def save_and_expect_page(
        self,
        *,
        expected_url=None,
        ready=None,
        expected_heading=None,
        confirm=True,
        confirm_text=None,
        button_name="Сохранить",
        root="main",
        confirm_timeout=10_000,
        timeout=30_000,
    ):
        """A2 formani saqlaydi, confirmni yopadi va target UI transitionni kutadi."""
        self.button(
            button_name,
            click=True,
            exact=True,
            root=root,
        )
        if confirm:
            self.confirm_biruni(
                expected_text=confirm_text,
                timeout=confirm_timeout,
            )

        if ready is not None:
            ready_locator = (
                self.page.locator(ready)
                if isinstance(ready, str)
                else ready
            ).first
            error = self._visible_error_locator()
            outcome = ready_locator.or_(error).filter(visible=True).first
            expect(outcome).to_be_visible(timeout=timeout)
            ui_error = self._visible_error_text()
            if ui_error:
                raise AssertionError(
                    "Angular save failed\n"
                    f"Expected URL: {expected_url or 'berilmagan'}\n"
                    f"Actual URL: {self.page.url}\n"
                    f"UI error: {ui_error}"
                )

        self.expect_page(
            url=expected_url,
            heading=expected_heading,
            ready=ready,
            timeout=timeout,
        )
        return True
