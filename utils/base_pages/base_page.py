import re

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.date_utils import format_date, resolve_date
from utils.helper_utils import first_non_admin_filial, label_pattern
from utils.base_pages.page_diagnostics import expectation_gate, report_page_expectation
from utils.base_pages.page_reporting import report_web_action
from utils.report_context import record_filial


_UNSET = object()


def _whitespace_agnostic_pattern(value, *, exact=False):
    """Matndagi barcha whitespace'ni ixtiyoriy qiladigan regex qaytaradi."""
    if isinstance(value, re.Pattern):
        return value
    normalized = re.sub(r"\s+", "", str(value))
    body = r"\s*".join(re.escape(char) for char in normalized)
    return re.compile(rf"^\s*{body}\s*$" if exact else body)


class BasePage:
    """Legacy DOM implementatsiyasi; public API AngularBasePage bilan teng.

    Parametrlar, assertion va return kontraktlari ikkala class'da saqlanadi.
    Explicit locator/root/model qiymatlari tegishli UI uchun beriladi.
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
        """Testlarda ishlatish uchun hisoblangan sanani matn ko'rinishida qaytaradi.
        value:
            Hisoblash uchun boshlang'ich sana. Quyidagilarni qabul qiladi:

            - ``"today"`` — bugungi sana;
            - ``"yesterday"`` / ``"previous_day"`` — kechagi sana;
            - ``"tomorrow"`` / ``"next_day"`` — ertangi sana;
            - ``"first_day"`` / ``"month_start"`` — joriy oyning boshi;
            - ``"last_day"`` / ``"month_end"`` — joriy oyning oxiri;
            - ``date`` yoki ``datetime`` obyekti;
            - ``DD.MM.YYYY``, ``YYYY-MM-DD``, ``DD/MM/YYYY`` yoki
              ``DD-MM-YYYY`` formatidagi sana matni.
        days:
            Boshlang'ich sanaga qo'shiladigan kunlar soni. Musbat qiymat
            keyingi, manfiy qiymat oldingi sanani qaytaradi.
        date_format:
            Natija formati. Python ``strftime`` formati yoki
            ``DD.MM.YYYY``, ``YYYY-MM-DD``, ``DD/MM/YYYY``,
            ``DD-MM-YYYY`` aliaslaridan biri.
        """
        return format_date(value, days=days, date_format=date_format)

    # ------------------------------------------------------------------------------------------------------------------

    def _resolve_root(self, root):
        """``root`` selector stringini Locatorga aylantiradi; None bo'lsa Page qaytaradi."""
        if root is None:
            return self.page
        return self.page.locator(root) if isinstance(root, str) else root

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
        """Semantic role va accessible name orqali elementni topib bosadi.

        Styled radio inputlar ko'rinadigan label/span ostida qolishi mumkin;
        radio tanlash uchun ``radio(label, click=True)`` ishlatiladi.
        """
        self._validate_options(
            'click',
            exact=exact,
            index=index,
            timeout=timeout,
        )
        root = self._resolve_root(root)
        target = root.get_by_role(role, name=name, exact=exact).nth(index)
        expect(target).to_be_visible(timeout=timeout)
        target.click(timeout=timeout)
        return target

    # ------------------------------------------------------------------------------------------------------------------

    def choice(self, label, option, *, index=0, root=None, timeout=10_000):
        """Label bilan bog'langan segmented button optionni tanlaydi."""
        self._validate_options(
            'choice',
            index=index,
            timeout=timeout,
        )
        root = self._resolve_root(root)
        label_item = root.get_by_text(self._label_pattern(label)).filter(visible=True).nth(index)
        expect(label_item).to_be_visible(timeout=timeout)
        container = label_item.locator(
            "xpath=ancestor::*[self::div or self::section or self::fieldset][.//button][1]"
        )
        expect(container).to_be_visible(timeout=timeout)
        button = container.get_by_role("button", name=option, exact=True).first
        expect(button).to_be_visible(timeout=timeout)
        button.click(timeout=timeout)
        return button

    # ------------------------------------------------------------------------------------------------------------------

    def hide_ui(self, locator, *, remove=False):
        """Berilgan selector/Locator topgan yordamchi UI elementlarini bloklaydi.

        Chat, onboarding kabi test flowiga tegishli bo'lmagan floating widgetlar
        pointer event'ni ushlab qolmasligi uchun ishlatiladi. ``remove=True``
        bo'lsa elementlar DOMdan ham olib tashlanadi; aks holda faqat yashiriladi.
        Nechta elementga amal qilinganini qaytaradi.
        """
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

    def _current_heading_text(self, root=None):
        scope = self.page if root is None else self.page.locator(root) if isinstance(root, str) else root
        try:
            headings = [item.strip() for item in scope.get_by_role("heading").all_inner_texts()]
        except Exception:
            return ""
        return " | ".join(item for item in headings if item)

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
        """Smartup forma checkbox/switch bilan ishlash uchun universal funksiya.
        (Grid checkbox'lari uchun `grid(checkbox="row"/"all")` ishlatiladi.)

        Checkboxni topish (faqat bittasini bering):
          - label="НДС": ko'rinadigan field label orqali (asosiy usul)
          - ng_model="d.vat_enabled": input[ng-model=...] orqali
          - locator: tayyor Locator yoki selector string

        Amal:
          - checked=True/False: shu holatga keltiradi (idempotent) va tasdiqlaydi
          - expect_checked=True/False: faqat holatni tasdiqlaydi
          - return_value=True: joriy bool holatni qaytaradi

        `root` (Page, Locator yoki selector string) va `index` topishni cheklaydi.
        """
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

        # --- topish: bitta strategiya ---
        if label is not None:
            cb = self._field_locator_by_label(label, index=index, root=root, target="switch")
        elif ng_model is not None:
            cb = root.locator(f'input[ng-model="{ng_model}"]').nth(index)
        elif locator is not None:
            cb = root.locator(locator).nth(index) if isinstance(locator, str) else locator
        else:
            raise ValueError(
                "checkbox(): label, ng_model yoki locator dan bittasini bering"
            )

        if checked is not _UNSET:
            self._toggle_checkbox(cb, checked)

        want = checked if checked is not _UNSET else expect_checked
        if want is not _UNSET:
            expect(cb).to_be_checked(timeout=10_000) if want else expect(cb).not_to_be_checked(timeout=10_000)
        if return_value:
            return cb.is_checked()
        return cb

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
        """Label orqali forma radiosini tanlaydi yoki holatini tekshiradi.

        ``click=True`` bo'lsa styled inputning o'zini emas, ko'rinadigan parent
        labelni bosadi. Masalan: ``radio("Цена продажи", click=True)``.
        """
        self._validate_options(
            'radio',
            click=click,
            expect_checked=expect_checked,
            return_value=return_value,
            index=index,
        )

        root = self._resolve_root(root)
        radio_el = self._field_locator_by_label(label, index=index, root=root, target="radio")

        if click:
            label_el = radio_el.locator("xpath=ancestor::label[1]")
            if label_el.count() > 0 and label_el.first.is_visible():
                label_el.first.click(timeout=10_000)
            else:
                radio_el.click(timeout=10_000)

        if expect_checked is not _UNSET:
            expect(radio_el).to_be_checked(timeout=10_000) if expect_checked else expect(radio_el).not_to_be_checked(timeout=10_000)
        if return_value:
            return radio_el.is_checked()
        return radio_el

    # ------------------------------------------------------------------------------------------------------------------

    def _toggle_checkbox(self, cb, checked):
        """`cb` checkbox/switch/grid-checkbox'ni `checked` holatiga keltiradi (idempotent).

        Input `opacity:0` (ko'rinmas) bo'lishi mumkin — shuning uchun click ko'rinadigan
        label/grid-cell/wrapper ustiga, kerak bo'lsa koordinata bo'yicha, cascade qilinadi.
        Grid header select-all da label balandligi 0 bo'ladi: checkbox tepada tursa katak
        markazi uni chetlab o'tadi, shuning uchun label-x + checkbox-y koordinatasiga bosiladi."""
        if cb.is_checked() == checked:
            return

        def reached():
            try:
                expect(cb).to_be_checked(timeout=1_000) if checked else expect(cb).not_to_be_checked(timeout=1_000)
                return True
            except (AssertionError, PlaywrightTimeoutError):
                return False

        label_el = cb.locator("xpath=ancestor::label[1]")
        cell_el = cb.locator(
            "xpath=ancestor::*[contains(@class,'tbl-checkbox-cell') or contains(@class,'tbl-header-cell')][1]"
        )
        wrap_el = cb.locator(
            "xpath=ancestor::*[contains(@class,'switch') or contains(@class,'checkbox') or contains(@class,'smt-checkbox') or contains(@class,'custom-control')][1]"
        )

        done = False
        if label_el.count() > 0 and label_el.first.is_visible():
            label_el.first.click()
            done = True
        elif label_el.count() > 0:
            # label bor, lekin ko'rinmas (masalan grid header'da balandligi 0) —
            # checkbox koordinatasi bo'yicha to'g'ridan-to'g'ri mouse click
            label_box = label_el.first.bounding_box()
            cb_box = cb.bounding_box()
            if label_box is not None and cb_box is not None and label_box["width"] > 0:
                self.page.mouse.click(
                    label_box["x"] + min(10, label_box["width"] / 2),
                    cb_box["y"] + cb_box["height"] / 2,
                )
                done = reached()

        if not done and cell_el.count() > 0 and cell_el.first.is_visible():
            cell = cell_el.first
            cell.scroll_into_view_if_needed()
            box = cell.bounding_box()
            if box is not None and box["width"] > 0 and box["height"] > 0:
                y = box["height"] / 2
                for x in (min(24, box["width"] / 2), min(12, box["width"] / 2), box["width"] / 2):
                    cell.click(position={"x": x, "y": y})
                    if reached():
                        break
            done = True

        if not done:
            if wrap_el.count() > 0 and wrap_el.first.is_visible():
                wrap_el.first.click()
            else:
                expect(cb).to_be_visible()
                cb.click()
        expect(cb).to_be_checked(timeout=10_000) if checked else expect(cb).not_to_be_checked(timeout=10_000)

    # ------------------------------------------------------------------------------------------------------------------

    def wait_for_loader(self, timeout=120_000):
        """
        Loader (overlay) paydo bo'lishini va keyin yo'qolishini kutadi.
        Sahifa settled bo'lsa True qaytaradi; loader timeout ichida
        yo'qolmasa xato ko'taradi.
        """
        self._validate_options(
            'wait_for_loader',
            timeout=timeout,
        )
        overlay = self.page.locator(".block-ui-overlay:visible")
        try:
            expect(overlay.first).to_be_visible(timeout=2_000)
        except (AssertionError, PlaywrightTimeoutError):
            pass
        expect(overlay).to_have_count(0, timeout=timeout)
        return True

    # ------------------------------------------------------------------------------------------------------------------

    @report_web_action
    def navigate_to(self, tab="Главное", name="Организации", timeout=30_000):
        self._validate_options(
            'navigate_to',
            timeout=timeout,
        )
        tab_link = self.page.locator("a.menu-link.menu-toggle").filter(
            has_text=_whitespace_agnostic_pattern(tab, exact=True), visible=True
        )
        expect(tab_link).to_have_count(1, timeout=timeout)
        tab_link.click(timeout=timeout)
        item = self.page.locator("a.menu-link.menu-link-title").get_by_text(name, exact=True).filter(visible=True)
        expect(item).to_have_count(1, timeout=timeout)
        item.click(timeout=timeout)

        try:
            self.wait_for_loader(timeout=timeout)
        except Exception as exc:
            raise AssertionError(
                f"navigate_to: '{tab} -> {name}' sahifa {timeout // 1000}s ichida yuklanmadi "
                f"(loader yo'qolmadi), url={self.page.url}"
            ) from exc

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
        """Navbar menyusi orqali formani ochadi.

        ``navbar_tab`` yuqori navbar elementi, ``menu_column`` ochilgan mega-menu
        ustuni, ``menu_item`` esa shu ustundagi forma linkidir. Ustunsiz kichik
        menyuda ``menu_column=None`` beriladi va item bevosita flyout ichidan
        qidiriladi. ``add_icon=True`` bo'lsa menu item matnli linki o'rniga
        shu item qatoridagi ``+add`` ikonka-link bosiladi. ``page_links``
        berilsa, menu formasi ochilgach sahifa yuqorisidagi linklar tartib bilan
        bosiladi. Forma heading va URL tekshiruvi chaqiruvchi kodda alohida
        ``expect_page(...)`` bilan qilinadi.
        """
        self._validate_options(
            'navigate_to_form',
            add_icon=add_icon,
            timeout=timeout,
        )
        links = [] if page_links is None else [page_links] if isinstance(page_links, str) else list(page_links)

        tab = (
            self.page.locator("a.menu-link.menu-toggle")
            .filter(has_text=navbar_tab)
            .filter(visible=True)
        )
        try:
            expect(tab).to_have_count(1, timeout=timeout)
            expect(tab).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(
                f"navigate_to_form: navbar_tab='{navbar_tab}' yagona ko'rinadigan element sifatida topilmadi"
            ) from exc
        flyout = (
            tab.locator("xpath=ancestor::li[contains(@class, 'menu-item-submenu')][1]")
            .locator(".menu-submenu")
        )
        if flyout.filter(visible=True).count() == 0:
            tab.click(timeout=timeout)
        flyout = flyout.filter(visible=True)
        expect(flyout).to_have_count(1, timeout=timeout)
        expect(flyout).to_be_visible(timeout=timeout)

        column = flyout
        if menu_column is not None:
            column_heading = (
                flyout.locator("h3.menu-heading")
                .filter(
                    has_text=_whitespace_agnostic_pattern(
                        menu_column,
                        exact=True,
                    )
                )
                .filter(visible=True)
            )
            try:
                expect(column_heading).to_have_count(1, timeout=timeout)
                expect(column_heading).to_be_visible(timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                raise AssertionError(
                    f"navigate_to_form: '{navbar_tab}' menyusida "
                    f"menu_column='{menu_column}' topilmadi"
                ) from exc

            column = column_heading.locator(
                "xpath=ancestor::li[contains(@class, 'menu-item')][1]"
            )
        item = column.get_by_role(
            "link",
            name=menu_item,
            exact=True,
        ).filter(visible=True)
        try:
            expect(item).to_have_count(1, timeout=timeout)
            expect(item).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            menu_scope = (
                f"{navbar_tab} → {menu_column}"
                if menu_column is not None
                else navbar_tab
            )
            raise AssertionError(
                f"navigate_to_form: '{menu_scope}' ichida "
                f"menu_item='{menu_item}' topilmadi"
            ) from exc
        if add_icon:
            item_row = item.locator(
                "xpath=ancestor::li[contains(@class, 'menu-item')][1]"
            )
            add_link = item_row.locator(
                ":scope > a.menu-link-icon"
            ).filter(visible=True)
            try:
                expect(add_link).to_have_count(1, timeout=timeout)
                expect(add_link).to_be_visible(timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                raise AssertionError(
                    f"navigate_to_form: menu_item='{menu_item}' qatorida "
                    "yagona ko'rinadigan +add ikonka-link topilmadi"
                ) from exc

            add_href = add_link.get_attribute("href") or ""
            if "+add" not in add_href:
                raise AssertionError(
                    f"navigate_to_form: menu_item='{menu_item}' ikonka-link URLida "
                    f"'+add' yo'q; href={add_href or '—'}"
                )
            add_link.click(timeout=timeout)
        else:
            item.click(timeout=timeout)

        for page_link in links:
            link = (
                self.page.get_by_role("link")
                .filter(has_text=page_link)
                .filter(visible=True)
            )
            try:
                expect(link).to_have_count(1, timeout=timeout)
                expect(link).to_be_visible(timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                raise AssertionError(
                    f"navigate_to_form: '{menu_item}' formasida page_link='{page_link}' topilmadi"
                ) from exc
            link.click(timeout=timeout)

        return add_link if add_icon else item

    # ------------------------------------------------------------------------------------------------------------------

    @report_web_action
    @report_page_expectation
    def expect_page(self, heading=None, url=None, timeout=30_000, check_unblocked=True, root=None):
        """Sahifaning URL va heading holatini tekshiradi.

        ``root`` berilsa, heading faqat shu CSS selector yoki Locator ichidan qidiriladi.
        Loader bloklanishi esa sahifa bo'yicha global tekshiriladi.
        """
        self._validate_options(
            'expect_page',
            timeout=timeout,
            check_unblocked=check_unblocked,
        )
        if heading is None and url is None:
            raise ValueError("expect_page: kamida 'heading' yoki 'url' berilishi kerak")

        if url is not None:
            pattern = url if isinstance(url, re.Pattern) else re.compile(re.escape(url))
            expectation_gate(self.page, "url")
            try:
                expect(self.page).to_have_url(pattern, timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                raise AssertionError(
                    f"expect_page: kutilgan URL '{getattr(url, 'pattern', url)}' ochilmadi; "
                    f"hozirgi url={self.page.url}"
                ) from exc

        if heading is not None:
            expectation_gate(self.page, "heading")
            scope = self.page if root is None else self.page.locator(root) if isinstance(root, str) else root
            target = scope.get_by_role("heading").filter(has_text=heading).first
            try:
                expect(target).to_be_visible(timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                shown = getattr(heading, "pattern", heading)
                raise AssertionError(
                    f"expect_page: kutilgan heading '{shown}' ko'rinmadi; "
                    f"hozirgi heading(lar)=\"{self._current_heading_text(root=root) or 'yo`q'}\", "
                    f"root={root or 'page'}, url={self.page.url}"
                ) from exc

        if check_unblocked:
            expectation_gate(self.page, "loader")
            expect(self.page.locator(".block-ui-overlay:visible")).to_have_count(0, timeout=timeout)

    # ------------------------------------------------------------------------------------------------------------------

    def switch_filial(self, name=None, timeout=30_000, *, first_filial=False):
        self._validate_options(
            'switch_filial',
            timeout=timeout,
            first_filial=first_filial,
        )
        if first_filial and name is not None:
            raise ValueError("switch_filial(): name va first_filial=True birga berilmaydi")
        if not first_filial and name is None:
            raise ValueError("switch_filial(): name yoki first_filial=True berilishi kerak")

        locations = (
            self.page.locator(".header-logo.custom-dropdown:visible")
            .filter(has=self.page.locator(".dropdown-locations-custom"))
            .first
        )
        trigger = locations.locator(".dropdown-locations-custom")
        expect(trigger).to_be_visible(timeout=timeout)
        trigger.click(timeout=timeout)

        menu = locations.locator(".dropdown-menu")
        expect(menu).to_be_visible(timeout=timeout)
        target_name = name
        if first_filial:
            target_name = first_non_admin_filial(
                menu.locator(".filial-list").get_by_role("link").all_inner_texts()
            )
        option = menu.get_by_role("link", name=target_name, exact=True)
        expect(option).to_be_visible(timeout=timeout)
        option.click(timeout=timeout)

        try:
            self.wait_for_loader(timeout=timeout)
        except Exception as exc:
            raise AssertionError(
                f"switch_filial: '{target_name}' filialiga o'tishda loader {timeout // 1000}s ichida "
                f"yo'qolmadi, url={self.page.url}"
            ) from exc

        current_filial = trigger.locator(".project-filial p").nth(1)
        expect(current_filial).to_have_text(target_name, timeout=timeout)
        record_filial(self.page, target_name)
        return option

    # ------------------------------------------------------------------------------------------------------------------

    def _visible_modal_candidates(self):
        """Ko'rinadigan legacy Biruni modal rootlarini qaytaradi."""
        return self.page.locator(
            "#biruniConfirm:visible, "
            "#biruniAlertExtended:visible, "
            "#biruniAlert:visible"
        )

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni(self, expected_text=None, button_name="да"):
        """Biruni confirm modalini barqaror tasdiqlaydi."""
        matcher = button_name if isinstance(button_name, re.Pattern) else re.compile(
            rf"^\s*{re.escape(str(button_name))}\s*$", re.IGNORECASE
        )
        button = self.page.get_by_role(
            "button",
            name=matcher,
        )
        confirm = self._visible_modal_candidates().filter(has=button).first
        expect(confirm).to_be_visible(timeout=10_000)
        if expected_text:
            expect(confirm).to_contain_text(expected_text, timeout=10_000)
        expect(confirm).to_have_css("opacity", "1", timeout=10_000)
        confirm.get_by_role("button", name=matcher).first.click(timeout=10_000)
        confirm.wait_for(state="hidden", timeout=10_000)

    # ------------------------------------------------------------------------------------------------------------------

    def close_biruni_alert(self, *expected_text):
        """Ko'rinadigan Biruni error alertini tekshiradi va yopadi."""
        error_text = re.compile(r"ошибка|error|URL\s*:|Uri\s*:", re.IGNORECASE)
        alert = self._visible_modal_candidates().filter(has_text=error_text).first
        expect(alert).to_be_visible(timeout=10_000)
        for value in expected_text:
            if value:
                expect(alert).to_contain_text(value, timeout=10_000)

        close_button = alert.locator("button.close").filter(visible=True).first
        if close_button.count() == 0:
            close_button = alert.get_by_role(
                "button",
                name=re.compile(r"закрыть|close|×", re.IGNORECASE),
            ).filter(visible=True).first
        expect(close_button).to_be_visible(timeout=10_000)
        close_button.click(timeout=10_000)
        expect(alert).to_be_hidden(timeout=10_000)

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
        """`text` bo'yicha grid qatorini topadi, ko'rinishini va (berilgan bo'lsa)
        `contains` dagi har bir matnni (nom, status va h.k.) o'z ichiga olishini tekshiradi.

          - click=True: topilgan qatorni bosadi
          - checkbox="row": topilgan qator checkbox'ini belgilaydi (idempotent)
          - checkbox="all": ko'rinadigan grid tepasidagi select-all (input[bcheckall])
            checkbox'ini belgilaydi (bu holda `text` kerak emas)
          - state="empty": ko'rinadigan grid bo'shashini retry bilan tasdiqlaydi
          - return_bool=True: row yoki state holatini bir marta o'qib bool qaytaradi
          - remove_spaces=True: row qidirish va contains assertlarda barcha
            whitespace'ni avtomatik e'tiborsiz qoldiradi

        Grid checkbox'lari `opacity:0`; belgilash `_toggle_checkbox` orqali bajariladi."""
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

        if root is None or root == "b-grid" or root is self.page:
            grid = self.page.locator("b-grid").filter(visible=True).first
        else:
            grid = self._resolve_root(root)

        if state == "empty":
            no_data = grid.get_by_text("нет данных", exact=True)
            if return_bool:
                return no_data.is_visible()
            expect(no_data).to_be_visible(timeout=10_000)
            return grid

        if checkbox == "all":
            cb = grid.locator("input[bcheckall]").first
            if cb.count() == 0:
                cb = grid.locator("input[type='checkbox']").first
            expect(cb).to_be_attached(timeout=10_000)
            self._toggle_checkbox(cb, True)
            return cb

        row_text = _whitespace_agnostic_pattern(text) if remove_spaces else text

        if return_bool:
            row = grid.locator(".tbl-row").filter(has_text=row_text).first
            return row.is_visible()

        row = grid.locator(".tbl-row").filter(has_text=row_text).first
        expect(row).to_be_visible(timeout=10_000)
        for value in contains:
            expected = _whitespace_agnostic_pattern(value) if remove_spaces else value
            expect(row).to_contain_text(expected, timeout=10_000)
        if checkbox == "row":
            self._toggle_checkbox(row.locator("input[type='checkbox']").first, True)
        if click:
            row.click(timeout=10_000)
        return row

    # ------------------------------------------------------------------------------------------------------------------

    def grid_cell(self, row, index, *, expect_value=_UNSET, return_value=False, remove_spaces=False):
        """``grid()`` qaytargan row ichidagi bitta cellni tekshiradi yoki o'qiydi.

        ``expect_value`` cell matnini tasdiqlaydi. ``return_value=True`` joriy
        matnni qaytaradi. ``remove_spaces=True`` bo'lsa oddiy va NBSP
        whitespace'lar assert hamda return qiymatida e'tiborsiz qoldiriladi.
        """
        self._validate_options(
            'grid_cell',
            index=index,
            return_value=return_value,
            remove_spaces=remove_spaces,
        )

        cell = row.locator(".tbl-cell").nth(index)
        expect(cell).to_be_visible(timeout=10_000)

        if expect_value is not _UNSET:
            expected = _whitespace_agnostic_pattern(expect_value) if remove_spaces else str(expect_value)
            expect(cell).to_contain_text(expected, timeout=10_000)

        if return_value:
            value = cell.inner_text().strip()
            return re.sub(r"\s+", "", value) if remove_spaces else " ".join(value.split())
        return cell

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
        """List formadagi `b-grid-controller` boshqaruvlari. Tanlovga qarab bittasi bajariladi:

          - search="matn": qidiruv maydoniga yozib Enter bosadi (loader kutiladi)
          - expand="50"/"100"/"500"/"1000": grid limitini shu qiymatga o'zgartiradi
          - reload=True: ro'yxatni yangilaydi (fa-redo)
          - open_filter=True: filtr oynasini ochadi (fa-filter)
          - open_setting=True: setting/ustunlar menyusini ochadi (fa-bars)
        """
        self._validate_options(
            'grid_controller',
            reload=reload,
            open_filter=open_filter,
            open_setting=open_setting,
        )
        gc = self._resolve_root("b-grid-controller" if root is None else root)
        if isinstance(root, str) or root is None:
            gc = gc.filter(visible=True).first

        if search is not None:
            field = gc.locator('input[ng-model="o.searchValue"]').first
            expect(field).to_be_visible(timeout=30_000)
            field.fill(str(search), timeout=30_000)
            field.press("Enter", timeout=30_000)
            self.wait_for_loader(timeout=30_000)
            return
        if expand is not None:
            expand = str(expand)
            if expand not in {"50", "100", "500", "1000"}:
                raise ValueError('grid_controller(expand=...): "50", "100", "500" yoki "1000" bo\'lishi kerak')
            button = gc.locator("button:has(i.fa-arrow-down)").first
            expect(button).to_be_visible(timeout=30_000)
            button.click(timeout=30_000)
            option = gc.get_by_role("link", name=expand, exact=True).first
            expect(option).to_be_visible(timeout=30_000)
            option.click(timeout=30_000)
            self.wait_for_loader(timeout=30_000)
            return
        if reload:
            gc.locator('button[ng-click="reload()"]').first.click(timeout=30_000)
            self.wait_for_loader(timeout=30_000)
            return
        if open_filter:
            gc.locator('button[ng-click="openFilter()"]').first.click(timeout=30_000)
            return
        if open_setting:
            gc.locator("button.dropdown-toggle:has(span.fa-bars)").first.click(timeout=30_000)
            return

        raise ValueError(
            'grid_controller(): search, expand="50"/"100"/"500"/"1000", reload, open_filter yoki open_setting dan bittasini bering'
        )

    # ------------------------------------------------------------------------------------------------------------------

    def grid_setting(self, *, menu_name, field_name, search_name=None, timeout=30_000):
        """Grid settingda ustunni va ixtiyoriy search maydonini yoqadi.

        Setting saqlanib listga qaytilgach, ``field_name`` ustunining grid
        indeksini qaytaradi. Ustun/search oldindan yoqilgan bo'lsa qayta
        o'zgartirilmaydi.
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

        list_url = self.page.url
        self.grid_controller(open_setting=True)
        menu = self.page.get_by_role("link", name=menu_name).filter(visible=True).first
        additional_heading = self.page.get_by_role("heading", name="Дополнительные поля", exact=True).first
        expect(menu.or_(additional_heading).first).to_be_visible(timeout=timeout)
        if menu.is_visible():
            menu.click(timeout=timeout)
        expect(additional_heading).to_be_visible(timeout=timeout)
        selected_fields = additional_heading.locator(
            "xpath=preceding-sibling::div[1]//ul[contains(@class, 'gs-main-list')]"
        )
        additional_fields = additional_heading.locator(
            "xpath=following-sibling::ul[contains(@class, 'gs-extra-list')][1]"
        )
        selected_field = selected_fields.get_by_text(field_name, exact=True)
        if selected_field.count() == 0:
            field = additional_fields.get_by_text(field_name, exact=True).first
            expect(field).to_be_visible(timeout=timeout)
            field.click(timeout=timeout)
        expect(selected_fields.get_by_text(field_name, exact=True)).to_be_visible(timeout=timeout)

        if search_name is not None:
            search_heading = self.page.get_by_role("heading", name="Настройки поиска", exact=True).first
            expect(search_heading).to_be_visible(timeout=timeout)
            search_card = search_heading.locator(
                "xpath=ancestor::div["
                "contains(concat(' ', normalize-space(@class), ' '), ' card ')"
                "][1]"
            )
            self.checkbox(label=search_name, checked=True, root=search_card)

        self.page.get_by_role("button", name="Сохранить", exact=True).click(timeout=timeout)
        self.page.wait_for_url(list_url, timeout=timeout)
        self.wait_for_loader(timeout=timeout)

        headers = self.page.locator("b-grid:visible .tbl-header-cell")
        expected_header = _whitespace_agnostic_pattern(field_name, exact=True)
        expect(headers.filter(has_text=expected_header).first).to_be_visible(timeout=timeout)
        for index in range(headers.count()):
            if expected_header.search(headers.nth(index).inner_text()):
                return index
        raise AssertionError(f"grid_setting(): saqlangandan keyin '{field_name}' ustuni topilmadi")

    # ------------------------------------------------------------------------------------------------------------------

    def text(self, *values, root="b-page", timeout=10_000):
        """Ko'rinadigan root ichida berilgan matnlar borligini tekshiradi.

        ``values`` berilmasa, faqat root locator UI'da ko'rinishini tekshiradi.
        """
        self._validate_options(
            'text',
            timeout=timeout,
        )
        content = self._resolve_root("b-page" if root is None else root)
        if content is self.page:
            content = self.page.locator("body")
        expect(content).to_be_visible(timeout=timeout)
        for value in values:
            if value:
                expect(content).to_contain_text(value, timeout=timeout)

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
        """View formadagi ``label + .form-view`` qiymatini tekshiradi yoki qaytaradi.

        Smartup view sahifalarida read-only ko'rinadigan maydonlar ko'pincha
        ``input[readonly]`` emas, ``<span class="form-view">...</span>`` bo'ladi.
        ``index`` bir xil label/value juftliklari orasidan N-chisini tanlaydi.
        ``remove_spaces=True`` assert va return qiymatida barcha whitespace'ni
        olib tashlaydi (masalan UI'dagi ``7 000`` ni ``7000`` sifatida tekshiradi).
        """
        self._validate_options(
            'form_view',
            return_value=return_value,
            remove_spaces=remove_spaces,
            index=index,
            timeout=timeout,
        )
        root = self._resolve_root(root)
        pattern = self._label_pattern(label)
        labels = root.locator("label").filter(has_text=pattern)
        translated_labels = root.locator("t").filter(has_text=pattern)
        # Locatorlar lazy: label/value kech render bo'lsa ham expect retry qiladi.
        labelled_values = labels.locator(
            "xpath=following-sibling::*[contains(concat(' ', normalize-space(@class), ' '), ' form-view ')][1]"
        )
        translated_values = translated_labels.locator("xpath=(../../span)[1]")
        value = labelled_values.or_(translated_values).filter(visible=True).nth(index)
        expect(value).to_be_visible(timeout=timeout)
        if expect_value is not _UNSET:
            if remove_spaces:
                if not isinstance(expect_value, str):
                    raise TypeError(
                        "form_view(remove_spaces=True): expect_value string bo'lishi kerak"
                    )
                normalized = re.sub(r"\s+", "", expect_value)
                whitespace_agnostic = _whitespace_agnostic_pattern(normalized, exact=True)
                expect(value).to_have_text(whitespace_agnostic, timeout=timeout)
            else:
                expect(value).to_have_text(expect_value, timeout=timeout)

        if return_value:
            text = value.inner_text().strip()
            return re.sub(r"\s+", "", text) if remove_spaces else text
        return value

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
        """Label orqali Bootstrap datepickerdan berilgan sanani tanlaydi.

        ``date``: relative keyword, ``date``/``datetime`` yoki qo'llab-
        quvvatlanadigan sana matni. ``auto_fill=True`` bo'lsa inputda shu sana
        avvaldan mavjudligi tekshiriladi va kalendar ochilmaydi. Aks holda sana
        typing bilan emas, datepickerning o'zidagi kun tugmasi bilan tanlanadi.
        """
        self._validate_options(
            'date_picker',
            auto_fill=auto_fill,
            index=index,
            timeout=timeout,
        )

        target_date = resolve_date(date)
        target_value = target_date.strftime("%d.%m.%Y")
        root = self._resolve_root(root)
        input_el = self._field_locator_by_label(label, index=index, root=root, target="input", timeout=timeout)
        expect(input_el).to_be_visible(timeout=timeout)

        if auto_fill:
            expect(input_el).to_have_value(target_value, timeout=timeout)
            return input_el

        input_el.click(timeout=timeout)

        picker = self.page.locator(".bootstrap-datetimepicker-widget:visible").last
        expect(picker).to_be_visible(timeout=timeout)

        for _ in range(241):
            day = picker.locator(f'[data-action="selectDay"][data-day="{target_value}"]').first
            if day.count() > 0:
                if "disabled" in (day.get_attribute("class") or ""):
                    raise AssertionError(f"date_picker(): '{target_value}' sanasi tanlash uchun yopiq")
                day.click(timeout=timeout)
                expect(input_el).to_have_value(target_value, timeout=timeout)
                return input_el

            shown_days = picker.locator('[data-action="selectDay"]')
            shown_dates = [
                resolve_date(shown_days.nth(day_index).get_attribute("data-day"))
                for day_index in range(shown_days.count())
            ]
            if not shown_dates:
                raise AssertionError("date_picker(): calendar kunlari topilmadi")

            direction = "prev" if target_date < min(shown_dates) else "next"
            navigation = picker.locator(f'th.{direction}').first
            if "disabled" in (navigation.get_attribute("class") or ""):
                raise AssertionError(f"date_picker(): '{target_value}' sanasiga o'tib bo'lmaydi")
            navigation.click(timeout=timeout)

        raise AssertionError(f"date_picker(): '{target_value}' sanasi 20 yil oralig'ida topilmadi")

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
        """Multi-select b-input ("N Выбранных") bilan ishlash.

        Topish (faqat bittasini bering):
          - label="Роли": ko'rinadigan field label orqali (asosiy usul)
          - name="roles": `b-input[name=...]` orqali fallback

        Amal (`b_input()` bilan bir xil parametr uslubi):
          - value="Админ" yoki value=["Админ", ...]: variantlarni tanlaydi
          - expect_value="Админ" yoki ro'yxat: selected chiplarni tekshiradi
          - return_value=True: tanlangan chip matnlarini list qilib qaytaradi
          - clear=True: mavjud tanlovlarning barchasini tozalaydi

        Single-select `select_b_input`/`b_input` dan farqi (Штат formasida
        MCP bilan tasdiqlangan, 2026-06-30):
          - tanlangach search maydoni bo'shaydi (variant matnini ko'rsatmaydi),
            shuning uchun search value tasdiqlanmaydi;
          - dropdown (`.hint`) b-input ICHIDA render bo'ladi (body'ga portal emas);
          - tanlangach dropdown ochiq qoladi — ko'p variant tanlash mumkin;
          - tasdiqlash `.multiple` ichidagi chip (tanlangan element) bo'yicha qilinadi.

        close=True: oxirida Escape bilan dropdown yopiladi (keyingi b-input uchun zarur).
        """
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
            # `_field_locator_by_label(target="b-input")` ko'rinmas labellarni o'tkazib
            # yuboradi (masalan "Рабочие зоны" yashirin span'i), shuning uchun to'g'ri
            # b-input ga tushadi; qaytadigan locator b-input elementining o'zi.
            b_input = self._field_locator_by_label(label, index=index, root=root, target="b-input", timeout=timeout)
        elif name is not None:
            b_input = root.locator(f'b-input[name="{name}"]').nth(index)
        else:
            raise ValueError("multiselect(): label yoki name berilishi kerak")

        expect(b_input).to_be_visible(timeout=timeout)
        search = b_input.locator('input[placeholder="Поиск..."]').first
        multiple = b_input.locator(".multiple").first
        chips = multiple.locator("a.btn")

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
            clear_button = b_input.locator(".edit").first
            if clear_button.count() > 0 and clear_button.is_visible():
                clear_button.click(timeout=timeout)
            expect(chips).to_have_count(0, timeout=timeout)

        selected_values = values_list(value)
        for option_text in selected_values:
            search.click(timeout=timeout)
            option = b_input.locator(".hint:visible").get_by_text(option_text, exact=exact).first
            expect(option).to_be_visible(timeout=timeout)
            option.click(timeout=timeout)

        expected_values = (
            selected_values
            if expect_value is _UNSET and value is not _UNSET
            else values_list(expect_value)
        )
        for option_text in expected_values:
            selected = chips.get_by_text(option_text, exact=exact).first
            expect(selected).to_be_visible(timeout=timeout)

        if close and value is not _UNSET:
            search.press("Escape", timeout=timeout)
        if return_value:
            return [" ".join(text.split()) for text in chips.all_inner_texts() if text.strip()]
        return b_input

    # ------------------------------------------------------------------------------------------------------------------

    def _label_pattern(self, label):
        return label_pattern(label)

    # ------------------------------------------------------------------------------------------------------------------

    def _field_target(self, container, target):
        if target == "b-input":
            return container.locator("b-input:has(input[placeholder])").first
        if target == "ui-select":
            return container.locator(".ui-select-container").first
        if target == "switch":
            return container.locator("input[type='checkbox'], [role='switch']").first
        if target == "radio":
            return container.locator("input[type='radio']").first
        if target == "input":
            return container.locator(
                "xpath=.//*[self::input or self::textarea]"
                "[not(ancestor::b-input) and not(@type='checkbox') and not(@type='radio')]"
                "[not(starts-with(@id,'focusser-'))]"
            ).first
        return container.locator("input, textarea, b-input, [role='switch']").first

    # ------------------------------------------------------------------------------------------------------------------

    def _field_container_by_label(self, label, needs_search=False, index=0, root=None, target=None, timeout=10_000):
        root = self._resolve_root(root)
        target = target or ("b-input" if needs_search else "input")
        label_locator = root.locator(
            "label, t, span, .control-label, .col-form-label, .form-label"
        ).filter(has_text=self._label_pattern(label))
        if label_locator.count() == 0:
            label_locator = root.get_by_text(self._label_pattern(label))

        match_index = 0
        ancestor_paths = (
            "ancestor::*[contains(concat(' ', normalize-space(@class), ' '), ' col ') or contains(@class,'col-')][1]",
            "ancestor::*[contains(@class,'input-group')][1]",
            "ancestor::*[contains(@class,'form-group')][1]",
            "ancestor::*[contains(@class,'form-row')][1]",
            "ancestor::*[contains(@class,'row')][1]",
            "..",
        )

        for label_index in range(label_locator.count()):
            label_item = label_locator.nth(label_index)
            try:
                expect(label_item).to_be_visible(timeout=min(timeout, 1_000))
            except (AssertionError, PlaywrightTimeoutError):
                continue

            for ancestor in ancestor_paths:
                container = label_item.locator(f"xpath={ancestor}")
                if container.count() == 0:
                    continue
                field_target = self._field_target(container.first, target)
                if field_target.count() == 0:
                    continue
                if match_index == index:
                    return container.first
                match_index += 1
                break

        raise AssertionError(f"Field container not found by label: {label} (target={target})")

    # ------------------------------------------------------------------------------------------------------------------

    def _field_locator_by_grid_header(self, label, *, index=0, root=None, target="input", timeout=10_000):
        """b-pg-grid ichida column header matni bo'yicha shu column inputini topadi.

        Smartup editable gridlarida `Кол-во`, `Цена`, `Название` kabi matnlar
        `<label>` emas, header cell bo'ladi. Oddiy label qidiruv topmasa, shu
        fallback headerning x-koordinatasi ostidagi input/b-inputni qaytaradi.
        """
        root = self._resolve_root(root)
        grid = root.locator("b-pg-grid:visible").first
        if grid.count() == 0:
            grid = root

        headers = grid.locator(".tbl-header-cell")
        try:
            expect(headers.first).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(f"Grid headers not visible for label: {label}") from exc

        normalized_label = re.sub(r"\s+", " ", label).strip().casefold()
        matching_headers = []
        for header_index in range(headers.count()):
            header_item = headers.nth(header_index)
            header_text = re.sub(
                r"\s+",
                " ",
                header_item.inner_text(),
            ).strip().casefold()
            if header_text == normalized_label:
                matching_headers.append(header_item)

        if index >= len(matching_headers):
            raise AssertionError(f"Grid header not found by label: {label}")

        header = matching_headers[index]
        expect(header).to_be_visible(timeout=min(timeout, 1_000))
        header_box = header.bounding_box()
        if header_box is None:
            raise AssertionError(f"Grid header has no bounding box: {label}")

        if target == "b-input":
            candidates = grid.locator("b-input:visible")
        elif target == "ui-select":
            candidates = grid.locator(".ui-select-container:visible")
        elif target == "input":
            candidates = grid.locator(
                "input:visible:not([ng-model='g.searchValue']), textarea:visible"
            )
        else:
            candidates = grid.locator("input:visible, textarea:visible, b-input:visible")

        try:
            expect(candidates.first).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            raise AssertionError(
                f"Grid field candidates not visible for label: {label} (target={target})"
            ) from exc

        header_left = header_box["x"]
        header_right = header_box["x"] + header_box["width"]

        for candidate_index in range(candidates.count()):
            candidate = candidates.nth(candidate_index)
            box = candidate.bounding_box()
            if box is None:
                continue
            center_x = box["x"] + box["width"] / 2
            if header_left <= center_x <= header_right:
                return candidate

        raise AssertionError(f"Field not found under grid header: {label} (target={target})")

    # ------------------------------------------------------------------------------------------------------------------

    def _field_locator_by_label(self, label, *, index=0, root=None, target="input", timeout=10_000):
        root = self._resolve_root(root)
        label_locator = root.locator(
            "label, t, span, .control-label, .col-form-label, .form-label"
        ).filter(has_text=self._label_pattern(label))
        if label_locator.count() == 0:
            label_locator = root.get_by_text(self._label_pattern(label))

        target_xpath = {
            "input": (
                "following::*[(self::input or self::textarea)"
                " and not(ancestor::b-input)"
                " and not(@type='checkbox') and not(@type='radio') and not(@type='hidden')"
                " and not(starts-with(@id,'focusser-'))][1]"
            ),
            "b-input": "following::b-input[.//input][1]",
            "ui-select": (
                "following::*[contains(concat(' ', normalize-space(@class), ' '),"
                " ' ui-select-container ')][1]"
            ),
            "switch": "following::input[@type='checkbox'][1]",
            "radio": "following::input[@type='radio'][1]",
        }[target]

        match_index = 0
        for label_index in range(label_locator.count()):
            label_item = label_locator.nth(label_index)
            try:
                expect(label_item).to_be_visible(timeout=min(timeout, 1_000))
            except (AssertionError, PlaywrightTimeoutError):
                continue

            if target in {"switch", "radio"}:
                # Label matni <label> ning O'ZI bo'lishi mumkin (checkbox — uning ichida,
                # masalan Smartup counterparty toggle'lari <label><input><t>Клиент</t></label>).
                # `ancestor::label` self'ni hisobga olmaydi → label element uchun count 0 bo'lib
                # keyingi inputga tushib ketishi mumkin. `ancestor-or-self` label wrapper ichidagi
                # to'g'ri checkbox/radioni topadi.
                input_type = "checkbox" if target == "switch" else "radio"
                field = label_item.locator(
                    f"xpath=(ancestor-or-self::label[1]//input[@type='{input_type}'])[1]"
                )
                if field.count() == 0:
                    field = label_item.locator(f"xpath={target_xpath}")
            else:
                field = label_item.locator(f"xpath={target_xpath}")

            if field.count() == 0:
                container = self._field_container_by_label(label, index=match_index, root=root, target=target, timeout=timeout)
                field = self._field_target(container, target)
            if field.count() == 0:
                continue

            if target not in {"switch", "radio"}:
                try:
                    expect(field.first).to_be_visible(timeout=min(timeout, 500))
                except (AssertionError, PlaywrightTimeoutError):
                    continue

            if match_index == index:
                return field.first
            match_index += 1

        try:
            return self._field_locator_by_grid_header(label, index=index, root=root, target=target, timeout=timeout)
        except AssertionError:
            pass

        raise AssertionError(f"Field not found by label: {label} (target={target})")

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
        """Legacy b-inputni label/model orqali tanlaydi yoki tekshiradi.

        ``select_first=True`` qidiruvga hech narsa yozmasdan ochilgan ro'yxatdagi
        birinchi optionni tanlaydi. Non-empty ``search_text`` berilsa qidiradi
        va qaytgan birinchi optionni tanlaydi. Faqat ``value`` berilganda esa
        shu qiymatga mos option tanlanadi.

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
            b_input = self._field_locator_by_label(label, index=index, root=root, target="b-input", timeout=timeout)
        elif ng_model is not None:
            b_input = root.locator(f'b-input:has(input[ng-model="{ng_model}"])').nth(index)
        else:
            raise ValueError("b_input(): label yoki ng_model berilishi kerak")

        search = b_input.locator("input[placeholder]").first
        expect(search).to_be_visible(timeout=timeout)

        if clear:
            edit = b_input.locator(".edit")
            if edit.count() > 0 and edit.first.is_visible():
                edit.first.click(timeout=timeout)
            search.fill("", timeout=timeout)
            expect(search).to_have_value("", timeout=timeout)

        has_search_query = search_text not in (None, "")
        if value is not _UNSET or has_search_query or select_first:
            option_text = str(value) if value is not _UNSET else None
            search.click(timeout=timeout)

            query = None if select_first else option_text if search_text is None else str(search_text)
            if query:
                if server_search:
                    search.press("ControlOrMeta+A", timeout=timeout)
                    search.press("Backspace", timeout=timeout)
                    search.press_sequentially(query, delay=delay, timeout=timeout)
                else:
                    search.fill(query, timeout=timeout)

            # b-input natijalari asinxron yuklanadi. ``count()`` bilan darhol
            # fallback qilish dropdown javobi kelishidan oldin noto'g'ri
            # locator tanlanishiga olib keladi. ``expect`` option DOMga kelib,
            # ko'ringuncha auto-retry qiladi; has_text esa qo'shimcha ustun
            # matnlari (ombor, narx turi va hokazo) bo'lsa ham mos tushadi.
            options = b_input.locator(".hint-item:visible")
            if select_first or has_search_query:
                option = options.first
            else:
                option_matcher = (
                    re.compile(rf"^\s*{re.escape(option_text)}\s*$")
                    if exact else re.compile(re.escape(option_text))
                )
                option = options.filter(has_text=option_matcher).or_(
                    options.filter(has=self.page.get_by_text(option_matcher))
                )
                if exact:
                    # Product nomi metadata bilan bitta elementda turishi mumkin.
                    # Butun row emas, alohida text node ham exact mos keladi.
                    parts = option_text.split("'")
                    text_literal = (
                        "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"
                        if len(parts) > 1 else f"'{option_text}'"
                    )
                    option = option.or_(options.filter(has=self.page.locator(
                        f"xpath=.//*[text()[normalize-space(.)={text_literal}]]"
                    )))
                option = option.first
            expect(option).to_be_visible(timeout=timeout)
            option.click(timeout=timeout)

        if clear and value is _UNSET and not has_search_query and not select_first:
            search.press("Escape", timeout=timeout)

        expected = expect_value
        if expected is _UNSET and value is not _UNSET and not select_first and not has_search_query:
            expected = str(value)
        if expected is not _UNSET:
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
        """Angular UI Select komponentini tanlaydi, tekshiradi yoki qiymatini qaytaradi.

        Fieldni ``label`` yoki ``ng_model`` orqali topadi. ``value`` berilsa
        dropdownni ochib mos visible optionni tanlaydi; ``expect_value`` joriy
        tanlangan matnni tekshiradi; ``return_value=True`` shu matnni qaytaradi.
        Search yoqilgan ui-selectlar uchun ``search_text`` berish mumkin.
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
            ui_select = self._field_locator_by_label(
                label,
                index=index,
                root=root,
                target="ui-select",
                timeout=timeout,
            )
        elif ng_model is not None:
            ui_select = root.locator(
                f'.ui-select-container[ng-model="{ng_model}"]:visible'
            ).nth(index)
        else:
            raise ValueError("ui_select(): label yoki ng_model berilishi kerak")

        expect(ui_select).to_be_visible(timeout=timeout)
        toggle = ui_select.locator(".ui-select-toggle").first
        selected = ui_select.locator(".ui-select-match-text").first
        expect(toggle).to_be_visible(timeout=timeout)

        if value is not _UNSET:
            option_text = str(value)
            toggle.click(timeout=timeout)

            if search_text is not None:
                search = ui_select.locator(".ui-select-search:visible").first
                expect(search).to_be_visible(timeout=timeout)
                search.fill(str(search_text), timeout=timeout)

            option_matcher = (
                re.compile(rf"^\s*{re.escape(option_text)}\s*$")
                if exact
                else option_text
            )
            option = ui_select.locator(
                ".ui-select-choices-row-inner:visible"
            ).filter(has_text=option_matcher).first
            expect(option).to_be_visible(timeout=timeout)
            option.click(timeout=timeout)

        expected = expect_value
        if expected is _UNSET and value is not _UNSET:
            expected = str(value)
        if expected is not _UNSET:
            expect(selected).to_be_visible(timeout=timeout)
            if exact:
                expect(selected).to_have_text(expected, timeout=timeout)
            else:
                expect(selected).to_contain_text(expected, timeout=timeout)

        if return_value:
            expect(selected).to_be_visible(timeout=timeout)
            return " ".join(selected.inner_text().split())
        return ui_select

    # ------------------------------------------------------------------------------------------------------------------

    def _label_field_container(self, label, index=0, root=None, target="input"):
        """Label matni orqali form-group/col/form-row konteynerini topadi."""
        return self._field_container_by_label(label, index=index, root=root, target=target)

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
        """Oddiy text input/textarea bilan ishlash uchun yagona universal funksiya
        (`checkbox()` kabi pattern).

        Inputni topish (faqat bittasini bering):
          - label="Код": ko'rinadigan field label orqali (label -> following input)
          - ng_model="d.first_name": `input[ng-model=...]` orqali (label ishonchsiz
            bo'lganda, masalan label DOMda inputdan keyin kelsa)
          - placeholder="Поиск": placeholder orqali
          - locator: tayyor Locator yoki selector string

        Amal:
          - value=...: maydonni tozalab (clear=True) shu qiymat bilan to'ldiradi
          - expect_value=...: qiymatni tasdiqlaydi (value berilsa, default expect_value=value)
          - return_value=True: joriy qiymatni (str) qaytaradi
          - press_tab=True: to'ldirgach Tab bosadi

        `index` bir nechta mos input orasidan N-chisini, `root` (Page, Locator yoki
        selector string) topishni cheklaydi.

        b-number inputida avtomatik value asserti formatlashdagi whitespace'ni
        hisobga olmaydi; explicit expect_value aynan tekshiriladi.
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
            input_el = self._field_locator_by_label(label, index=index, root=root, target="input")
        elif ng_model is not None:
            input_el = root.locator(
                f'input[ng-model="{ng_model}"]:visible, textarea[ng-model="{ng_model}"]:visible'
            ).nth(index)
        elif placeholder is not None:
            input_el = root.get_by_placeholder(placeholder).nth(index)
        elif locator is not None:
            input_el = root.locator(locator).nth(index) if isinstance(locator, str) else locator
        else:
            raise ValueError("input(): label, ng_model, placeholder yoki locator dan bittasini bering")

        expect(input_el).to_be_visible(timeout=10_000)

        if value is not _UNSET:
            input_el.click(timeout=10_000)
            if clear:
                input_el.press("ControlOrMeta+A", timeout=10_000)
                input_el.press("Backspace", timeout=10_000)
            input_el.fill(str(value), timeout=10_000)
            if press_tab:
                input_el.press("Tab", timeout=10_000)

        expected = expect_value
        if expected is _UNSET and value is not _UNSET:
            expected = str(value)
            if input_el.get_attribute("b-number") is not None:
                expected = _whitespace_agnostic_pattern(expected, exact=True)
        if expected is not _UNSET:
            expect(input_el).to_have_value(expected, timeout=10_000)

        if return_value:
            return input_el.input_value()
        return input_el

    # ------------------------------------------------------------------------------------------------------------------
