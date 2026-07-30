import logging
import re

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.date_utils import format_date, resolve_date


logger = logging.getLogger(__name__)

_UNSET = object()


def _whitespace_agnostic_pattern(value, *, exact=False):
    """Matndagi barcha whitespace'ni ixtiyoriy qiladigan regex qaytaradi."""
    if isinstance(value, re.Pattern):
        return value
    normalized = re.sub(r"\s+", "", str(value))
    body = r"\s*".join(re.escape(char) for char in normalized)
    return re.compile(rf"^\s*{body}\s*$" if exact else body)


class BasePage:
    def __init__(self, page):
        self.page = page

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

    def hide_ui(self, locator, *, remove=False):
        """Berilgan selector/Locator topgan yordamchi UI elementlarini bloklaydi.

        Chat, onboarding kabi test flowiga tegishli bo'lmagan floating widgetlar
        pointer event'ni ushlab qolmasligi uchun ishlatiladi. ``remove=True``
        bo'lsa elementlar DOMdan ham olib tashlanadi; aks holda faqat yashiriladi.
        Nechta elementga amal qilinganini qaytaradi.
        """
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

    def _visible_error_text(self, timeout=1_000):
        selectors = (
            "#biruniAlertExtended",
            "#biruniAlert",
            "[role='alert']:visible",
            ".alert-danger:visible",
            ".toast-message:visible",
            ".toast:visible",
        )
        for index, selector in enumerate(selectors):
            locator = self.page.locator(selector).first
            try:
                if index == 0 and timeout:
                    expect(locator).to_be_visible(timeout=timeout)
                elif not locator.is_visible():
                    continue
                text = re.sub(r"\s+", " ", locator.inner_text(timeout=timeout)).strip()
            except Exception:
                continue
            if text:
                return text
        return ""

    # ------------------------------------------------------------------------------------------------------------------

    def _transition_failure_message(
        self,
        *,
        action,
        expected,
        before_state,
        actual_state,
        ui_error="",
        location_hint="",
    ):
        lines = [
            "Smartup transition failed",
            f"Before page: {before_state or 'unknown'}",
            f"Action: {action}",
            f"Expected: {expected}",
            f"Actual: {actual_state or 'unknown'}",
        ]
        if ui_error:
            lines.append(f"UI error: {ui_error}")
        if location_hint:
            lines.append(f"Location hint: {location_hint}")
        return "\n".join(lines)

    # ------------------------------------------------------------------------------------------------------------------

    def save_and_expect_heading(
        self,
        expected_heading,
        *,
        action="Сохранить",
        before_state=None,
        expected_state=None,
        confirm_text=None,
        button_name="Сохранить",
        exact_button=True,
        timeout=30_000,
        location_hint="",
    ):
        before = before_state or self._current_heading_text()
        button = self.page.get_by_role("button", name=button_name, exact=exact_button).first
        expect(button).to_be_visible()
        button.click()

        if confirm_text is not None:
            self.confirm_biruni(confirm_text or None)
        self.wait_for_loader(timeout=timeout)

        expected = expected_state or f"{expected_heading} heading ochilishi"
        ui_error = self._visible_error_text(timeout=1_000)
        if ui_error:
            actual = f"still on {self._current_heading_text() or before or 'unknown'}"
            raise AssertionError(
                self._transition_failure_message(
                    action=action,
                    expected=expected,
                    before_state=before,
                    actual_state=actual,
                    ui_error=ui_error,
                    location_hint=location_hint,
                )
            )

        heading = self.page.get_by_role("heading").filter(has_text=expected_heading).first
        try:
            expect(heading).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            actual = f"still on {self._current_heading_text() or before or 'unknown'}; url={self.page.url}"
            raise AssertionError(
                self._transition_failure_message(
                    action=action,
                    expected=expected,
                    before_state=before,
                    actual_state=actual,
                    ui_error=self._visible_error_text(timeout=500),
                    location_hint=location_hint,
                )
            ) from exc

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
        root = self._resolve_root(root)

        # --- topish: bitta strategiya ---
        if label is not None:
            cb = self._field_locator_by_label(label, index=index, root=root, target="switch")
        elif ng_model is not None:
            cb = root.locator(f'input[ng-model="{ng_model}"]').nth(index)
        elif locator is not None:
            cb = root.locator(locator).first if isinstance(locator, str) else locator
        else:
            raise ValueError(
                "checkbox(): label, ng_model yoki locator dan bittasini bering"
            )

        if checked is not _UNSET:
            self._toggle_checkbox(cb, checked)

        want = checked if checked is not _UNSET else expect_checked
        if want is not _UNSET:
            expect(cb).to_be_checked() if want else expect(cb).not_to_be_checked()
        if return_value:
            return cb.is_checked()
        return cb

    # ------------------------------------------------------------------------------------------------------------------

    def radio(
        self,
        label,
        *,
        expect_checked=True,
        return_value=False,
        index=0,
        root=None,
    ):
        """Label orqali forma radiosini topib, tanlangan holatini tekshiradi.

        Masalan: ``radio("Цена продажи", expect_checked=True)``.
        Radio holatini o'zgartirish bu helper vazifasi emas; kerakli optionni tanlash
        uchun alohida user action ishlatiladi.
        """
        root = self._resolve_root(root)
        radio_el = self._field_locator_by_label(label, index=index, root=root, target="radio")

        if expect_checked is not _UNSET:
            expect(radio_el).to_be_checked() if expect_checked else expect(radio_el).not_to_be_checked()
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

    # ------------------------------------------------------------------------------------------------------------------

    def wait_for_loader(self, timeout=30_000):
        """
        Loader (overlay) paydo bo'lishini va keyin yo'qolishini kutadi.
        Sahifa settled bo'lsa True qaytaradi; loader timeout ichida
        yo'qolmasa xato ko'taradi.
        """
        overlay = self.page.locator(".block-ui-overlay")
        try:
            overlay.wait_for(state="visible", timeout=2_000)
        except Exception:
            # Loader qisqa detection oralig'ida chiqmasa, jarayon tugagan yoki juda tez o'tgan.
            return True

        try:
            overlay.wait_for(state="hidden", timeout=timeout)
        except Exception as exc:
            logger.warning("Loader %s ms ichida yo'qolmadi: %s", timeout, exc)
            raise
        return True

    # ------------------------------------------------------------------------------------------------------------------

    def navigate_to(self, tab="Главное", name="Организации", timeout=30_000):
        self.page.locator("a.menu-link.menu-toggle", has_text=tab).click()
        self.page.locator("a.menu-link.menu-link-title").get_by_text(name, exact=True).click()

        try:
            self.wait_for_loader(timeout=timeout)
        except Exception as exc:
            raise AssertionError(
                f"navigate_to: '{tab} -> {name}' sahifa {timeout // 1000}s ichida yuklanmadi "
                f"(loader yo'qolmadi), url={self.page.url}"
            ) from exc

    # ------------------------------------------------------------------------------------------------------------------

    def navigate_to_form(
        self,
        *,
        navbar_tab,
        menu_column,
        menu_item,
        page_links=None,
        timeout=60_000,
    ):
        """Navbar menyusi orqali formani ochadi.

        ``navbar_tab`` yuqori navbar elementi, ``menu_column`` ochilgan mega-menu
        ustuni, ``menu_item`` esa shu ustundagi forma linkidir. Ustunsiz kichik
        menyuda ``menu_column=None`` beriladi va item bevosita flyout ichidan
        qidiriladi. ``page_links`` berilsa, menu formasi ochilgach sahifa
        yuqorisidagi linklar tartib bilan bosiladi. Forma heading va URL
        tekshiruvi chaqiruvchi kodda alohida ``expect_page(...)`` bilan qilinadi.
        """
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
            tab.click()
        flyout = flyout.filter(visible=True)
        expect(flyout).to_have_count(1, timeout=timeout)
        expect(flyout).to_be_visible(timeout=timeout)

        column = flyout
        if menu_column is not None:
            column_heading = (
                flyout.locator("h3.menu-heading")
                .filter(has_text=menu_column)
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
        item.click()

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
            link.click()

        return item

    # ------------------------------------------------------------------------------------------------------------------

    def expect_page(self, heading=None, url=None, timeout=30_000, check_unblocked=True, root=None):
        """Sahifaning URL va heading holatini tekshiradi.

        ``root`` berilsa, heading faqat shu CSS selector yoki Locator ichidan qidiriladi.
        Loader bloklanishi esa sahifa bo'yicha global tekshiriladi.
        """
        if heading is None and url is None:
            raise ValueError("expect_page: kamida 'heading' yoki 'url' berilishi kerak")

        if url is not None:
            pattern = url if isinstance(url, re.Pattern) else re.compile(re.escape(url))
            try:
                expect(self.page).to_have_url(pattern, timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                raise AssertionError(
                    f"expect_page: kutilgan URL '{getattr(url, 'pattern', url)}' ochilmadi; "
                    f"hozirgi url={self.page.url}"
                ) from exc

        if heading is not None:
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
                try:
                    expect(self.page.locator(".block-ui-overlay:visible")).to_have_count(0, timeout=timeout)
                except (AssertionError, PlaywrightTimeoutError) as exc:
                    shown = getattr(heading, "pattern", heading)
                    raise AssertionError(
                        f"expect_page: heading '{shown}' ko'rindi, lekin Smartup loader overlay bilan "
                        f"bloklangan; url={self.page.url}"
                    ) from exc

    # ------------------------------------------------------------------------------------------------------------------

    def switch_filial(self, name, timeout=30_000):
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
        option = menu.get_by_role("link", name=name, exact=True)
        expect(option).to_be_visible(timeout=timeout)
        option.click(timeout=timeout)

        try:
            self.wait_for_loader(timeout=timeout)
        except Exception as exc:
            raise AssertionError(
                f"switch_filial: '{name}' filialiga o'tishda loader {timeout // 1000}s ichida "
                f"yo'qolmadi, url={self.page.url}"
            ) from exc

        current_filial = trigger.locator(".project-filial p").nth(1)
        expect(current_filial).to_have_text(name, timeout=timeout)
        return option

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni(self, expected_text=None, button_name="да"):
        """Biruni confirm modalini barqaror tasdiqlaydi."""
        confirm = self.page.locator("#biruniConfirm")
        expect(confirm).to_be_visible()
        if expected_text:
            expect(confirm).to_contain_text(expected_text)
        expect(confirm).to_have_css("opacity", "1")
        confirm.get_by_role("button", name=button_name, exact=True).click()
        confirm.wait_for(state="hidden")

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_biruni_if_visible(
        self,
        expected_text=None,
        button_name="да",
        timeout=1_000,
    ):
        """Biruni confirm ko'rinsa tasdiqlaydi, bo'lmasa ``False`` qaytaradi."""
        confirm = self.page.locator("#biruniConfirm")
        try:
            expect(confirm).to_be_visible(timeout=timeout)
        except (AssertionError, PlaywrightTimeoutError):
            return False

        if expected_text:
            expect(confirm).to_contain_text(expected_text)
        expect(confirm).to_have_css("opacity", "1")
        confirm.get_by_role("button", name=button_name, exact=True).click()
        confirm.wait_for(state="hidden")
        return True

    # ------------------------------------------------------------------------------------------------------------------

    def close_biruni_alert(self, *expected_text):
        """Ko'rinadigan Biruni extended error alertini tekshiradi va yopadi."""
        alert = self.page.locator("#biruniAlertExtended")
        expect(alert).to_be_visible()
        for value in expected_text:
            if value:
                expect(alert).to_contain_text(value)

        close_button = alert.locator("button.close").first
        expect(close_button).to_be_visible()
        close_button.click()
        alert.wait_for(state="hidden")

    # ------------------------------------------------------------------------------------------------------------------

    def grid(
        self,
        text=None,
        *contains,
        root="b-grid",
        click=False,
        checkbox=None,
        is_empty=False,
        is_visible=False,
        remove_spaces=True,
    ):
        """`text` bo'yicha grid qatorini topadi, ko'rinishini va (berilgan bo'lsa)
        `contains` dagi har bir matnni (nom, status va h.k.) o'z ichiga olishini tekshiradi.

          - click=True: topilgan qatorni bosadi
          - checkbox="row": topilgan qator checkbox'ini belgilaydi (idempotent)
          - checkbox="all": ko'rinadigan grid tepasidagi select-all (input[bcheckall])
            checkbox'ini belgilaydi (bu holda `text` kerak emas)
          - is_empty=True: ko'rinadigan grid bo'sh bo'lsa True, aks holda False qaytaradi
          - is_visible=True: `text` qatori ko'rinsa True, aks holda False qaytaradi
          - remove_spaces=True: row qidirish va contains assertlarda barcha
            whitespace'ni avtomatik e'tiborsiz qoldiradi

        Grid checkbox'lari `opacity:0`; belgilash `_toggle_checkbox` orqali bajariladi."""
        if checkbox not in (None, "row", "all"):
            raise ValueError('grid(checkbox=...): "row" yoki "all" bo\'lishi kerak')
        if not isinstance(remove_spaces, bool):
            raise TypeError("grid(remove_spaces=...): bool bo'lishi kerak")
        if is_empty and (text is not None or contains or click or checkbox is not None or is_visible):
            raise ValueError("grid(is_empty=True) boshqa qator amallari bilan birga ishlatilmaydi")
        if is_visible and text is None:
            raise ValueError("grid(is_visible=True) uchun text berilishi kerak")
        if is_visible and (contains or click or checkbox is not None):
            raise ValueError("grid(is_visible=True) contains/click/checkbox bilan birga ishlatilmaydi")

        if is_empty:
            grid = self.page.locator(root).filter(visible=True).first
            no_data = grid.get_by_text("нет данных", exact=True)
            return no_data.is_visible()

        if checkbox == "all":
            self.wait_for_loader()
            grid = self.page.locator(root).filter(visible=True).first
            cb = grid.locator("input[bcheckall]").first
            if cb.count() == 0:
                cb = grid.locator("input[type='checkbox']").first
            expect(cb).to_be_attached()
            self._toggle_checkbox(cb, True)
            return cb

        row_text = _whitespace_agnostic_pattern(text) if remove_spaces else text

        if is_visible:
            grid = self.page.locator(root).filter(visible=True).first
            row = grid.locator(".tbl-row").filter(has_text=row_text).first
            return row.is_visible()

        grid = self.page.locator(root)
        row = grid.locator(".tbl-row").filter(has_text=row_text).first
        expect(row).to_be_visible()
        for value in contains:
            expected = _whitespace_agnostic_pattern(value) if remove_spaces else value
            expect(row).to_contain_text(expected)
        if checkbox == "row":
            self._toggle_checkbox(row.locator("input[type='checkbox']").first, True)
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
        """List formadagi `b-grid-controller` boshqaruvlari. Tanlovga qarab bittasi bajariladi:

          - search="matn": qidiruv maydoniga yozib Enter bosadi (loader kutiladi)
          - expand="50"/"100"/"500"/"1000": grid limitini shu qiymatga o'zgartiradi
          - reload=True: ro'yxatni yangilaydi (fa-redo)
          - open_filter=True: filtr oynasini ochadi (fa-filter)
          - open_setting=True: setting/ustunlar menyusini ochadi (fa-bars)
        """
        gc = self.page.locator(root).filter(visible=True).first

        if search is not None:
            field = gc.locator('input[ng-model="o.searchValue"]').first
            expect(field).to_be_visible()
            field.fill(search)
            field.press("Enter")
            self.wait_for_loader()
            return
        if expand is not None:
            if expand not in {"50", "100", "500", "1000"}:
                raise ValueError('grid_controller(expand=...): "50", "100", "500" yoki "1000" bo\'lishi kerak')
            button = gc.locator("button:has(i.fa-arrow-down)").first
            expect(button).to_be_visible()
            button.click()
            option = gc.get_by_role("link", name=expand, exact=True).first
            expect(option).to_be_visible()
            option.click()
            self.wait_for_loader(timeout=120_000)
            return
        if reload:
            gc.locator('button[ng-click="reload()"]').first.click()
            self.wait_for_loader(timeout=120_000)
            return
        if open_filter:
            gc.locator('button[ng-click="openFilter()"]').first.click()
            return
        if open_setting:
            gc.locator("button.dropdown-toggle:has(span.fa-bars)").first.click()
            return

        raise ValueError(
            'grid_controller(): search, expand="50"/"100"/"500"/"1000", reload, open_filter yoki open_setting dan bittasini bering'
        )

    # ------------------------------------------------------------------------------------------------------------------

    def text(self, *values, root="b-page", timeout=10_000):
        """Ko'rinadigan root ichida berilgan matnlar borligini tekshiradi.

        ``values`` berilmasa, faqat root locator UI'da ko'rinishini tekshiradi.
        """
        content = self.page.locator(root) if isinstance(root, str) else root
        expect(content).to_be_visible(timeout=timeout)
        for value in values:
            if value:
                expect(content).to_contain_text(value)

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
        """View formadagi ``label + .form-view`` qiymatini tekshiradi yoki qaytaradi.

        Smartup view sahifalarida read-only ko'rinadigan maydonlar ko'pincha
        ``input[readonly]`` emas, ``<span class="form-view">...</span>`` bo'ladi.
        ``index`` bir xil label/value juftliklari orasidan N-chisini tanlaydi.
        ``remove_spaces=True`` assert va return qiymatida barcha whitespace'ni
        olib tashlaydi (masalan UI'dagi ``7 000`` ni ``7000`` sifatida tekshiradi).
        """
        root = self._resolve_root(root)
        labels = root.locator("label").filter(has_text=self._label_pattern(label))

        matches = []
        for label_index in range(labels.count()):
            label_item = labels.nth(label_index)
            try:
                expect(label_item).to_be_visible(timeout=1_000)
            except (AssertionError, PlaywrightTimeoutError):
                continue

            value = label_item.locator(
                "xpath=following-sibling::*[contains(concat(' ', normalize-space(@class), ' '), ' form-view ')][1]"
            )
            if value.count() > 0:
                matches.append(value.first)

        if index >= len(matches):
            translated_labels = root.locator("t").filter(has_text=self._label_pattern(label))
            for label_index in range(translated_labels.count()):
                label_item = translated_labels.nth(label_index)
                try:
                    expect(label_item).to_be_visible(timeout=1_000)
                except (AssertionError, PlaywrightTimeoutError):
                    continue

                value = label_item.locator("xpath=../../span").first
                if value.count() > 0:
                    matches.append(value)

        if index >= len(matches):
            raise AssertionError(f"Form view field not found by label: {label} (index={index})")

        value = matches[index]
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
        if not isinstance(auto_fill, bool):
            raise TypeError("date_picker(): auto_fill bool bo'lishi kerak")

        target_date = resolve_date(date)
        target_value = target_date.strftime("%d.%m.%Y")
        root = self._resolve_root(root)
        input_el = self._field_locator_by_label(label, index=index, root=root, target="input")
        expect(input_el).to_be_visible(timeout=timeout)

        if auto_fill:
            expect(input_el).to_have_value(target_value, timeout=timeout)
            return input_el

        input_el.click()

        picker = self.page.locator(".bootstrap-datetimepicker-widget:visible").last
        expect(picker).to_be_visible(timeout=timeout)

        for _ in range(241):
            day = picker.locator(f'[data-action="selectDay"][data-day="{target_value}"]').first
            if day.count() > 0:
                if "disabled" in (day.get_attribute("class") or ""):
                    raise AssertionError(f"date_picker(): '{target_value}' sanasi tanlash uchun yopiq")
                day.click()
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
            navigation.click()

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
        root = self._resolve_root(root)
        if label is not None and name is not None:
            raise ValueError("multiselect(): label yoki name dan faqat bittasini bering")
        if label is not None:
            # `_field_locator_by_label(target="b-input")` ko'rinmas labellarni o'tkazib
            # yuboradi (masalan "Рабочие зоны" yashirin span'i), shuning uchun to'g'ri
            # b-input ga tushadi; qaytadigan locator b-input elementining o'zi.
            b_input = self._field_locator_by_label(label, index=index, root=root, target="b-input")
        elif name is not None:
            b_input = root.locator(f'b-input[name="{name}"]').nth(index)
        else:
            raise ValueError("multiselect(): label yoki name berilishi kerak")

        expect(b_input).to_be_visible()
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
                clear_button.click()
            expect(chips).to_have_count(0)

        selected_values = values_list(value)
        for option_text in selected_values:
            search.click()
            option = b_input.locator(".hint:visible").get_by_text(option_text, exact=exact).first
            expect(option).to_be_visible(timeout=timeout)
            option.click()

        expected_values = (
            selected_values
            if expect_value is _UNSET and value is not _UNSET
            else values_list(expect_value)
        )
        for option_text in expected_values:
            selected = chips.get_by_text(option_text, exact=exact).first
            expect(selected).to_be_visible(timeout=timeout)

        if close and value is not _UNSET:
            search.press("Escape")
        if return_value:
            return [text.strip() for text in chips.all_inner_texts() if text.strip()]
        return b_input

    # ------------------------------------------------------------------------------------------------------------------

    def _label_pattern(self, label):
        return re.compile(rf"^\s*{re.escape(label)}\s*(?:\*)?\s*$", re.IGNORECASE)

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

    def _field_container_by_label(self, label, needs_search=False, index=0, root=None, target=None):
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
                expect(label_item).to_be_visible(timeout=1_000)
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

    def _field_locator_by_grid_header(self, label, *, index=0, root=None, target="input"):
        """b-pg-grid ichida column header matni bo'yicha shu column inputini topadi.

        Smartup editable gridlarida `Кол-во`, `Цена`, `Название` kabi matnlar
        `<label>` emas, header cell bo'ladi. Oddiy label qidiruv topmasa, shu
        fallback headerning x-koordinatasi ostidagi input/b-inputni qaytaradi.
        """
        root = self._resolve_root(root)
        grid = root.locator("b-pg-grid:visible").first
        if grid.count() == 0:
            grid = root

        headers = grid.locator(".tbl-header-cell").filter(has_text=self._label_pattern(label))
        if headers.count() == 0:
            raise AssertionError(f"Grid header not found by label: {label}")

        header = headers.nth(index)
        expect(header).to_be_visible(timeout=1_000)
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

    def _field_locator_by_label(self, label, *, index=0, root=None, target="input"):
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
                expect(label_item).to_be_visible(timeout=1_000)
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
                container = self._field_container_by_label(label, index=match_index, root=root, target=target)
                field = self._field_target(container, target)
            if field.count() == 0:
                continue

            if target not in {"switch", "radio"}:
                try:
                    expect(field.first).to_be_visible(timeout=500)
                except (AssertionError, PlaywrightTimeoutError):
                    continue

            if match_index == index:
                return field.first
            match_index += 1

        try:
            return self._field_locator_by_grid_header(label, index=index, root=root, target=target)
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
        delay=50,
        index=0,
        root=None,
        timeout=10_000,
    ):
        root = self._resolve_root(root)
        if label is not None and ng_model is not None:
            raise ValueError("b_input(): label yoki ng_model dan faqat bittasini bering")
        if label is not None:
            b_input = self._field_locator_by_label(label, index=index, root=root, target="b-input")
        elif ng_model is not None:
            b_input = root.locator(f'b-input:has(input[ng-model="{ng_model}"])').nth(index)
        else:
            raise ValueError("b_input(): label yoki ng_model berilishi kerak")

        search = b_input.locator("input[placeholder]").first
        expect(search).to_be_visible()

        if value is not _UNSET:
            option_text = str(value)
            search.click()

            if clear:
                edit = b_input.locator(".edit")
                if edit.count() > 0 and edit.first.is_visible():
                    edit.first.click()
                search.click()

            query = option_text if search_text is None else search_text
            if query:
                if server_search:
                    search.press("ControlOrMeta+A")
                    search.press("Backspace")
                    search.press_sequentially(query, delay=delay)
                else:
                    search.fill(query)

            # b-input natijalari asinxron yuklanadi. ``count()`` bilan darhol
            # fallback qilish dropdown javobi kelishidan oldin noto'g'ri
            # locator tanlanishiga olib keladi. ``expect`` option DOMga kelib,
            # ko'ringuncha auto-retry qiladi; has_text esa qo'shimcha ustun
            # matnlari (ombor, narx turi va hokazo) bo'lsa ham mos tushadi.
            option = b_input.locator(".hint-item:visible").filter(has_text=option_text).first
            expect(option).to_be_visible(timeout=timeout)
            option.click()

        expected = expect_value
        if expected is _UNSET and value is not _UNSET:
            expected = str(value)
        if expected is not _UNSET:
            if isinstance(expected, str):
                expected = re.compile(re.escape(expected))
            expect(search).to_have_value(expected)

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
        root = self._resolve_root(root)
        if label is not None and ng_model is not None:
            raise ValueError("ui_select(): label yoki ng_model dan faqat bittasini bering")
        if label is not None:
            ui_select = self._field_locator_by_label(
                label,
                index=index,
                root=root,
                target="ui-select",
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
            toggle.click()

            if search_text is not None:
                search = ui_select.locator(".ui-select-search:visible").first
                expect(search).to_be_visible(timeout=timeout)
                search.fill(str(search_text))

            option_matcher = (
                re.compile(rf"^\s*{re.escape(option_text)}\s*$")
                if exact
                else option_text
            )
            option = ui_select.locator(
                ".ui-select-choices-row-inner:visible"
            ).filter(has_text=option_matcher).first
            expect(option).to_be_visible(timeout=timeout)
            option.click()

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
        """
        root = self._resolve_root(root)

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

        expect(input_el).to_be_visible()

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
            expect(input_el).to_have_value(expected)

        if return_value:
            return input_el.input_value()
        return input_el

    # ------------------------------------------------------------------------------------------------------------------
