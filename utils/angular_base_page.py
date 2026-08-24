import re

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.date_utils import format_date, resolve_date
from utils.helper_utils import first_non_admin_filial, label_pattern


_UNSET = object()


def _whitespace_agnostic_pattern(value, *, exact=False):
    if isinstance(value, re.Pattern):
        return value
    normalized = re.sub(r"\s+", "", str(value))
    body = r"\s*".join(re.escape(char) for char in normalized)
    return re.compile(rf"^\s*{body}\s*$" if exact else body)


class AngularBasePage:
    """Smartup A2 yangi Angular formalarining umumiy UI primitivlari.

    Bu class ``smt-*`` komponentlari, CDK overlay va A2 shell uchun yozilgan.
    Eski AngularJS/Biruni formalarida ``utils.base_page.BasePage`` ishlatiladi.
    """

    def __init__(self, page):
        self.page = page

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def date(value="today", *, days=0, date_format="%d.%m.%Y"):
        return format_date(value, days=days, date_format=date_format)

    # ------------------------------------------------------------------------------------------------------------------

    def _resolve_root(self, root):
        if root is None:
            return self.page
        return self.page.locator(root) if isinstance(root, str) else root

    # ------------------------------------------------------------------------------------------------------------------

    def _content_root(self, root):
        return self._resolve_root("main" if root is None else root)

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
        root = self._content_root(root)
        target = root.get_by_role(role, name=name, exact=exact).nth(index)
        if role == "tab":
            smt_tab = root.locator("smt-tab-button").filter(
                has_text=self._label_pattern(name)
            ).nth(index)
            target = target.or_(smt_tab).first
        expect(target).to_be_visible(timeout=timeout)
        target.click()
        return target

    # ------------------------------------------------------------------------------------------------------------------

    def hide_ui(self, locator, *, remove=False):
        """Test flowiga tegishli bo'lmagan yordamchi UI elementlarini yashiradi."""
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
        """A2 ``smt-input`` ichidagi native input/textarea bilan ishlaydi."""
        root = self._content_root(root)
        sources = sum(
            source is not None for source in (locator, label, ng_model, placeholder)
        )
        if sources != 1:
            raise ValueError(
                "input(): locator, label, ng_model yoki placeholder dan aynan bittasini bering"
            )

        if label is not None:
            control = self._control(label, index=index, root=root)
            input_el = control.locator(
                "input:not([type='checkbox']):not([type='radio']):not([type='hidden']), "
                "textarea"
            ).first
        elif ng_model is not None:
            model_name = str(ng_model)
            short_name = model_name.removeprefix("d.")
            input_el = root.locator(
                f'[formcontrolname="{model_name}"], [formcontrolname="{short_name}"], '
                f'[ng-reflect-name="{model_name}"], [ng-reflect-name="{short_name}"]'
            ).nth(index)
        elif placeholder is not None:
            input_el = root.get_by_placeholder(placeholder).nth(index)
        else:
            input_el = root.locator(locator).nth(index) if isinstance(locator, str) else locator

        expect(input_el).to_be_visible(timeout=10_000)

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
            expect(input_el).to_have_value(expected, timeout=10_000)

        if return_value:
            return input_el.input_value()
        return input_el

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
        """
        root = self._content_root(root)
        if label is not None and ng_model is not None:
            raise ValueError("b_input(): label yoki ng_model dan faqat bittasini bering")
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
            raise ValueError("b_input(): label yoki ng_model berilishi kerak")

        trigger = select.locator("smt-select-trigger").first
        search = trigger.locator(
            "input:not([type='checkbox']):not([type='radio'])"
        ).first

        expect(select).to_be_visible(timeout=timeout)
        expect(trigger).to_be_visible(timeout=timeout)
        expect(search).to_be_visible(timeout=timeout)

        has_search_query = search_text not in (None, "")
        if value is not _UNSET or has_search_query or select_first:
            option_text = str(value) if value is not _UNSET else None
            current_value = search.input_value().strip()
            if clear and current_value:
                search.click()
                search.press("ControlOrMeta+A")
                search.press("Backspace")
                current_value = ""
            if select_first or has_search_query or current_value != option_text:
                trigger.click()
                query = None if select_first else option_text if search_text is None else str(search_text)
                if query:
                    search.press("ControlOrMeta+A")
                    search.press("Backspace")
                    if server_search:
                        search.press_sequentially(query, delay=delay)
                    else:
                        search.fill(query)

                dropdown = self.page.locator(
                    ".cdk-overlay-container smt-select-dropdown:visible"
                ).last
                expect(dropdown).to_be_visible(timeout=timeout)
                options = dropdown.locator("li:visible")
                if select_first or has_search_query:
                    option = options.first
                else:
                    option_matcher = (
                        re.compile(rf"^\s*{re.escape(option_text)}\s*$", re.IGNORECASE)
                        if exact
                        else re.compile(re.escape(option_text), re.IGNORECASE)
                    )
                    option = options.filter(has_text=option_matcher).first
                expect(option).to_be_visible(timeout=timeout)
                option.click()
                if dropdown.is_visible():
                    self.page.mouse.click(1, 1)
                expect(dropdown).to_be_hidden(timeout=timeout)

        expected = expect_value
        if expected is _UNSET and value is not _UNSET and not select_first and not has_search_query:
            expected = str(value)
        if expected is not _UNSET:
            expect(search).to_have_value(expected, timeout=timeout)

        if return_value:
            return search.input_value()
        return select

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
        if not isinstance(auto_fill, bool):
            raise TypeError("date_picker(): auto_fill bool bo'lishi kerak")
        root = self._content_root(root)
        control = self._control(label, index=index, root=root, timeout=timeout)
        picker = control.locator("smt-date-picker").first
        trigger = picker.locator("smt-select-trigger").first
        input_el = trigger.locator("input").first
        expect(picker).to_be_visible(timeout=timeout)
        expect(trigger).to_be_visible(timeout=timeout)
        expect(input_el).to_be_visible(timeout=timeout)

        expected = resolve_date(date).strftime("%d.%m.%Y")
        if auto_fill:
            expect(input_el).to_have_value(expected, timeout=timeout)
            return input_el

        if date == "today":
            trigger.click()
            overlay = self.page.locator(
                ".cdk-overlay-container .cdk-overlay-pane:visible"
            ).last
            expect(overlay).to_be_visible(timeout=timeout)
            today = overlay.get_by_role("button", name="Сегодня", exact=True)
            expect(today).to_be_visible(timeout=timeout)
            today.click()
        else:
            input_el.click()
            input_el.press("ControlOrMeta+A")
            input_el.fill(expected)
            input_el.press("Tab")

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
        root = self._content_root(root)
        roles = (role,) if isinstance(role, str) else tuple(role)
        pattern = self._label_pattern(label)
        visible_label = root.get_by_text(pattern).filter(visible=True).first
        expect(visible_label).to_be_visible(timeout=timeout)

        controls = root.locator("smt-control").filter(
            has=self.page.locator("label").filter(has_text=pattern)
        )
        toggle = None
        for role_name in roles:
            candidates = controls.get_by_role(role_name)
            if candidates.count() > index:
                toggle = candidates.nth(index)
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
        root = self._content_root(root)

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
            ).nth(index)
        elif locator is not None:
            toggle = root.locator(locator).first if isinstance(locator, str) else locator
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
        if not isinstance(click, bool):
            raise TypeError("radio(): click bool bo'lishi kerak")

        radio = self._toggle_by_label(
            label,
            role="radio",
            index=index,
            root=root,
        )
        if click:
            label_el = radio.locator("xpath=ancestor::label[1]")
            if label_el.count() > 0 and label_el.first.is_visible():
                label_el.first.click()
            else:
                radio.click()

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
        control = self._control(label, index=index, root=root, timeout=timeout)
        button = control.get_by_role("button", name=option, exact=True).first
        expect(button).to_be_visible(timeout=timeout)
        button.click()
        return button

    # ------------------------------------------------------------------------------------------------------------------

    def text(self, *values, root="b-page", timeout=10_000):
        content = self._content_root(None if root == "b-page" else root)
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
        root=None,
        timeout=10_000,
    ):
        """A2 view'dagi readonly ``smt-input`` qiymatini tekshiradi yoki qaytaradi."""
        field = self.input(
            label=label,
            index=index,
            root=root,
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
        root = self._content_root(root)
        if label is not None and name is not None:
            raise ValueError("multiselect(): label yoki name dan faqat bittasini bering")
        if label is not None:
            control = self._control(label, index=index, root=root, timeout=timeout)
            select = control.locator("smt-data-select, smt-select").first
        elif name is not None:
            select = root.locator(
                f'smt-data-select[formcontrolname="{name}"], smt-select[formcontrolname="{name}"]'
            ).nth(index)
        else:
            raise ValueError("multiselect(): label yoki name berilishi kerak")

        expect(select).to_be_visible(timeout=timeout)
        trigger = select.locator("smt-select-trigger").first
        search = trigger.locator("input").first
        chips = select.locator(
            "smt-chip:visible, .smt-chip:visible, "
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
                clear_buttons.first.click()
            expect(chips).to_have_count(0, timeout=timeout)

        selected_values = values_list(value)
        for option_text in selected_values:
            trigger.click()
            expect(search).to_be_visible(timeout=timeout)
            search.press("ControlOrMeta+A")
            search.press("Backspace")
            search.fill(option_text)
            dropdown = self.page.locator(
                ".cdk-overlay-container smt-select-dropdown:visible"
            ).last
            expect(dropdown).to_be_visible(timeout=timeout)
            matcher = (
                re.compile(rf"^\s*{re.escape(option_text)}\s*$", re.IGNORECASE)
                if exact
                else re.compile(re.escape(option_text), re.IGNORECASE)
            )
            option = dropdown.locator("li:visible").filter(has_text=matcher).first
            expect(option).to_be_visible(timeout=timeout)
            option.click()

        expected_values = (
            selected_values
            if expect_value is _UNSET and value is not _UNSET
            else values_list(expect_value)
        )
        for option_text in expected_values:
            selected = select.get_by_text(option_text, exact=exact).filter(visible=True).first
            expect(selected).to_be_visible(timeout=timeout)

        if close:
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
        """A2 single-selectni legacy ui_select call shape bilan boshqaradi."""
        return self.b_input(
            label=label,
            value=value,
            ng_model=ng_model,
            expect_value=expect_value,
            return_value=return_value,
            search_text=search_text,
            exact=exact,
            index=index,
            root=root,
            timeout=timeout,
        )

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
        return self._wait_for_loader(timeout=timeout)

    # ------------------------------------------------------------------------------------------------------------------

    def expect_page(
        self,
        heading=None,
        url=None,
        timeout=30_000,
        check_unblocked=True,
        root=None,
    ):
        """A2 sahifani canonical URL/heading contracti bilan tekshiradi."""
        if heading is None and url is None:
            raise ValueError("expect_page: kamida 'heading' yoki 'url' berilishi kerak")

        if url is not None:
            pattern = url if isinstance(url, re.Pattern) else re.compile(re.escape(url))
            expect(self.page).to_have_url(pattern, timeout=timeout)

        scope = self._content_root(root)
        if heading is not None:
            role_heading = scope.get_by_role("heading").filter(has_text=heading).first
            text_heading = scope.get_by_text(
                heading, exact=not isinstance(heading, re.Pattern)
            ).filter(visible=True).first
            target = role_heading.or_(text_heading).first
            expect(target).to_be_visible(timeout=timeout)

        if check_unblocked:
            self._wait_for_loader(timeout=timeout, root=scope)

    # ------------------------------------------------------------------------------------------------------------------

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
        if checkbox not in (None, "row", "all"):
            raise ValueError('grid(checkbox=...): "row" yoki "all" bo\'lishi kerak')
        if state not in (None, "empty"):
            raise ValueError('grid(state=...): faqat "empty" qo\'llanadi')
        if not isinstance(return_bool, bool):
            raise TypeError("grid(return_bool=...): bool bo'lishi kerak")
        if not isinstance(remove_spaces, bool):
            raise TypeError("grid(remove_spaces=...): bool bo'lishi kerak")
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

        if root is None or root == "b-grid":
            grid = self._content_root(None).locator(
                "smt-data-table, smt-table"
            ).filter(visible=True).first
        else:
            grid = self._resolve_root(root)

        expect(grid).to_be_visible(timeout=10_000)
        self._wait_for_loader(timeout=10_000, root=grid)
        rows = grid.locator(".smt-data-row")

        if state == "empty":
            if return_bool:
                return rows.count() == 0
            expect(rows).to_have_count(0, timeout=10_000)
            return grid

        if checkbox == "all":
            toggle = grid.get_by_role("checkbox").first
            expect(toggle).to_be_visible(timeout=10_000)
            self._set_toggle(toggle, True)
            return toggle

        row_text = _whitespace_agnostic_pattern(text) if remove_spaces else text
        row = rows.filter(has_text=row_text).first
        if return_bool:
            return row.is_visible()

        expect(row).to_be_visible(timeout=10_000)
        for value in contains:
            expected = _whitespace_agnostic_pattern(value) if remove_spaces else value
            expect(row).to_contain_text(expected, timeout=10_000)
        if checkbox == "row":
            toggle = row.get_by_role("checkbox").first
            expect(toggle).to_be_visible(timeout=10_000)
            self._set_toggle(toggle, True)
        if click:
            row.click()
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
        root = self._content_root(None if root == "b-grid-controller" else root)
        if search is not None:
            field = root.locator("input[type='search']").filter(visible=True).first
            expect(field).to_be_visible(timeout=30_000)
            field.click()
            field.press("ControlOrMeta+A")
            field.press("Backspace")
            if str(search):
                field.fill(str(search))
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
            page_size.click()
            option = self.page.locator(".cdk-overlay-container:visible").get_by_text(
                expand_value,
                exact=True,
            ).filter(visible=True).first
            expect(option).to_be_visible(timeout=30_000)
            option.click()
            self._wait_for_loader(timeout=30_000, root=root)
            return

        action = None
        if reload:
            action = root.get_by_role("button", name=re.compile(r"обновить|reload", re.IGNORECASE)).first
        elif open_filter:
            action = root.get_by_role("button", name=re.compile(r"фильтр|filter", re.IGNORECASE)).first
        elif open_setting:
            action = root.get_by_role("button", name=re.compile(r"настрой|setting|columns", re.IGNORECASE)).first
        if action is None:
            raise ValueError(
                'grid_controller(): search, expand="50"/"100"/"500"/"1000", reload, open_filter yoki open_setting dan bittasini bering'
            )
        expect(action).to_be_visible(timeout=30_000)
        action.click()
        if reload:
            self._wait_for_loader(timeout=30_000, root=root)

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
        if not isinstance(index, int) or index < 0:
            raise ValueError("grid_cell(index=...): manfiy bo'lmagan int berilishi kerak")
        if not isinstance(return_value, bool):
            raise TypeError("grid_cell(return_value=...): bool bo'lishi kerak")
        if not isinstance(remove_spaces, bool):
            raise TypeError("grid_cell(remove_spaces=...): bool bo'lishi kerak")

        cells = row.locator(".smt-data-cell")
        if cells.count() == 0:
            cells = row.locator("[role='cell'], [data-smt-col-key]")
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

    def navigate_to(
        self,
        tab="Главное",
        name="Организации",
        timeout=30_000,
    ):
        """A2 shell menu tabidan menuitem orqali boshqa A2 formani ochadi."""
        root = self._resolve_root("header")
        tab_button = root.get_by_role("button", name=tab, exact=True).first
        expect(tab_button).to_be_visible(timeout=timeout)
        tab_button.click()

        menu = self.page.locator(
            ".cdk-overlay-container [role='menu']:visible"
        ).last
        expect(menu).to_be_visible(timeout=timeout)
        item = menu.get_by_role("menuitem", name=name, exact=True).first
        expect(item).to_be_visible(timeout=timeout)
        item.click()
        self.wait_for_loader(timeout=timeout)
        return item

    # ------------------------------------------------------------------------------------------------------------------

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
        """BasePage navigate_to_form call shape'ini A2 shell orqali bajaradi."""
        del menu_column
        header = self._resolve_root("header")
        tab_button = header.get_by_role("button", name=navbar_tab, exact=True).first
        expect(tab_button).to_be_visible(timeout=timeout)
        tab_button.click()
        menu = self.page.locator(
            ".cdk-overlay-container [role='menu']:visible"
        ).last
        expect(menu).to_be_visible(timeout=timeout)
        item = menu.get_by_role("menuitem", name=menu_item, exact=True).first
        expect(item).to_be_visible(timeout=timeout)

        target = item
        if add_icon:
            item_row = item.locator("xpath=ancestor::*[self::li or @role='menuitem'][1]")
            add_target = item_row.get_by_role("button").or_(item_row.get_by_role("link")).filter(
                has_text=re.compile(r"^\s*(\+|создать|add)\s*$", re.IGNORECASE)
            ).first
            expect(add_target).to_be_visible(timeout=timeout)
            target = add_target
        target.click()
        self.wait_for_loader(timeout=timeout)

        for page_link in [] if page_links is None else list(page_links):
            link = self.page.get_by_role("link").filter(has_text=page_link).filter(visible=True).first
            expect(link).to_be_visible(timeout=timeout)
            link.click()
            self.wait_for_loader(timeout=timeout)
        return target

    # ------------------------------------------------------------------------------------------------------------------

    def switch_filial(
        self,
        name=None,
        timeout=30_000,
        *,
        first_filial=False,
    ):
        """A2 shell filial selectori orqali filialni almashtiradi."""
        if not isinstance(first_filial, bool):
            raise TypeError("switch_filial(first_filial=...): bool bo'lishi kerak")
        if first_filial and name is not None:
            raise ValueError("switch_filial(): name va first_filial=True birga berilmaydi")
        if not first_filial and name is None:
            raise ValueError("switch_filial(): name yoki first_filial=True berilishi kerak")

        root = self._resolve_root("header")
        trigger = root.locator(
            'button[data-testid*="project-filial"]'
        ).filter(visible=True).first
        if trigger.count() == 0:
            trigger = root.get_by_role(
                "button",
                name=re.compile(r"^\s*SFA\b", re.IGNORECASE),
            ).first

        expect(trigger).to_be_visible(timeout=timeout)
        trigger.click()
        filial_list = self.page.get_by_test_id(
            "shell-project-filial--filial-list"
        )
        expect(filial_list).to_be_visible(timeout=timeout)
        target_name = name
        if first_filial:
            target_name = first_non_admin_filial(
                filial_list.get_by_role("option").all_inner_texts()
            )
        option = filial_list.get_by_role("option", name=target_name, exact=True).first
        expect(option).to_be_visible(timeout=timeout)
        option.click()
        expect(trigger).to_contain_text(target_name, timeout=timeout)
        self.wait_for_loader(timeout=timeout)
        return option

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni(
        self,
        expected_text=None,
        button_name="да",
    ):
        """Legacy Biruni yoki A2/CDK confirm dialogini tasdiqlaydi."""
        root = self._resolve_root("body")
        matcher = (
            button_name
            if isinstance(button_name, re.Pattern)
            else re.compile(rf"^\s*{re.escape(str(button_name))}\s*$", re.IGNORECASE)
        )
        confirm = root.locator(
            "#biruniConfirm:visible, [role='dialog']:visible, .cdk-overlay-pane:visible"
        ).filter(
            has=self.page.get_by_role("button", name=matcher)
        ).last
        expect(confirm).to_be_visible(timeout=10_000)
        if expected_text:
            expect(confirm).to_contain_text(expected_text, timeout=10_000)
        button = confirm.get_by_role("button", name=matcher).first
        expect(button).to_be_visible(timeout=10_000)
        button.click()
        expect(confirm).to_be_hidden(timeout=10_000)

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni_if_visible(
        self,
        expected_text=None,
        button_name="да",
        timeout=1_000,
    ):
        root = self._resolve_root("body")
        matcher = (
            button_name
            if isinstance(button_name, re.Pattern)
            else re.compile(rf"^\s*{re.escape(str(button_name))}\s*$", re.IGNORECASE)
        )
        confirm = root.locator(
            "#biruniConfirm:visible, [role='dialog']:visible, .cdk-overlay-pane:visible"
        ).filter(
            has=self.page.get_by_role("button", name=matcher)
        ).last
        try:
            expect(confirm).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError):
            return False
        if expected_text:
            expect(confirm).to_contain_text(expected_text, timeout=timeout)
        confirm.get_by_role("button", name=matcher).first.click()
        expect(confirm).to_be_hidden(timeout=timeout)
        return True

    # ------------------------------------------------------------------------------------------------------------------

    def close_biruni_alert(self, *expected_text):
        """A2/legacy ko'rinadigan error alertini tekshiradi va yopadi."""
        alert = self._visible_error_locator(root="body")
        expect(alert).to_be_visible(timeout=10_000)
        for value in expected_text:
            if value:
                expect(alert).to_contain_text(value, timeout=10_000)

        close = alert.locator("button.close").first
        if close.count() == 0:
            close = alert.get_by_role(
                "button",
                name=re.compile(r"закрыть|close|×", re.IGNORECASE),
            ).first
        expect(close).to_be_visible(timeout=10_000)
        close.click()
        expect(alert).to_be_hidden(timeout=10_000)
