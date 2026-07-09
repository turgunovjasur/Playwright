import logging
import re

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


logger = logging.getLogger(__name__)

_UNSET = object()


class BasePage:
    def __init__(self, page):
        self.page = page

    # ------------------------------------------------------------------------------------------------------------------

    def _current_heading_text(self):
        try:
            headings = [item.strip() for item in self.page.get_by_role("heading").all_inner_texts()]
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
        timeout=120_000,
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
        check_all=False,
        first_visible=False,
        grid_name=None,
        expect_checked=_UNSET,
        return_value=False,
        index=0,
        root=None,
    ):
        """Smartup checkbox/switch bilan ishlash uchun yagona universal funksiya.

        Checkboxni topish (faqat bittasini bering):
          - label="НДС": ko'rinadigan field label orqali (asosiy usul)
          - ng_model="d.vat_enabled": input[ng-model=...] orqali
          - locator: tayyor Locator yoki selector string (grid checkbox va h.k.)
          - check_all=True: grid "hammasini belgilash" (input[bcheckall])
          - first_visible=True: birinchi ko'rinadigan grid checkbox

        Amal:
          - checked=True/False: shu holatga keltiradi (idempotent) va tasdiqlaydi
          - expect_checked=True/False: faqat holatni tasdiqlaydi
          - return_value=True: joriy bool holatni qaytaradi

        `root` (Page yoki modal Locator) va `index` topishni cheklaydi.
        """
        root = root or self.page

        # --- topish: bitta strategiya ---
        if label is not None:
            cb = self._field_locator_by_label(label, index=index, root=root, target="switch")
        elif ng_model is not None:
            cb = root.locator(f'input[ng-model="{ng_model}"]').nth(index)
        elif check_all or first_visible:
            # Grid ko'pincha loader (block-ui-overlay) ortidan kech render bo'ladi;
            # loader tushmasdan click qilinsa kaskad ko'rinmas input ustiga tushib qoladi.
            self.wait_for_loader()
            if first_visible:
                self.page.wait_for_load_state("networkidle")
                scope = root.locator(f'b-grid[name="{grid_name}"]') if grid_name else self.page
                cb = scope.locator("b-grid:visible input[type='checkbox']").first
            else:
                scope = root.locator(f'b-grid[name="{grid_name}"]') if grid_name else root
                cb = scope.locator("input[bcheckall]").first
            if cb.count() == 0:
                cb = scope.locator("input[type='checkbox']").first
            expect(cb).to_be_attached()
        elif locator is not None:
            cb = root.locator(locator).first if isinstance(locator, str) else locator
        else:
            raise ValueError(
                "checkbox(): label, ng_model, locator, check_all yoki first_visible dan bittasini bering"
            )

        # --- bosish: input opacity:0 (ko'rinmas) bo'lishi mumkin, shuning uchun click
        #     ko'rinadigan label/grid-cell/wrapper ustiga cascade qilinadi ---
        if checked is not _UNSET and cb.is_checked() != checked:
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

        want = checked if checked is not _UNSET else expect_checked
        if want is not _UNSET:
            expect(cb).to_be_checked() if want else expect(cb).not_to_be_checked()
        if return_value:
            return cb.is_checked()
        return cb

    # ------------------------------------------------------------------------------------------------------------------

    def wait_for_loader(self, timeout=300_000):
        """
        Loader (overlay) paydo bo'lishini va keyin yo'qolishini kutadi.
        Sahifa settled bo'lsa True qaytaradi; loader timeout ichida
        yo'qolmasa xato ko'taradi.
        """
        overlay = self.page.locator(".block-ui-overlay")
        try:
            overlay.wait_for(state="visible", timeout=2_000)
        except Exception:
            # Agar loader 2 soniyada chiqmasa, demak jarayon tugagan yoki juda tez o'tgan
            return True

        try:
            overlay.wait_for(state="hidden", timeout=timeout)
        except Exception as exc:
            logger.warning("Loader %s ms ichida yo'qolmadi: %s", timeout, exc)
            raise
        return True

    # ------------------------------------------------------------------------------------------------------------------

    def navigate_to(self, tab="Главное", name="Организации", timeout=120_000):
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

    def expect_page(self, heading=None, url=None, timeout=120_000, check_unblocked=True):
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
            target = self.page.get_by_role("heading").filter(has_text=heading).first
            try:
                expect(target).to_be_visible(timeout=timeout)
            except (AssertionError, PlaywrightTimeoutError) as exc:
                shown = getattr(heading, "pattern", heading)
                raise AssertionError(
                    f"expect_page: kutilgan heading '{shown}' ko'rinmadi; "
                    f"hozirgi heading(lar)=\"{self._current_heading_text() or 'yo`q'}\", url={self.page.url}"
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

    def switch_filial(self, name, timeout=120_000):
        self.page.locator(".pt-3.px-2").click()
        option = self.page.get_by_role("link", name=name, exact=True)
        expect(option).to_be_visible()
        option.click()

        try:
            self.wait_for_loader(timeout=timeout)
        except Exception as exc:
            raise AssertionError(
                f"switch_filial: '{name}' filialiga o'tishda loader {timeout // 1000}s ichida "
                f"yo'qolmadi, url={self.page.url}"
            ) from exc

        expect(self.page.get_by_role("paragraph").filter(has_text=name)).to_be_visible()

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

    def grid(self, text, *contains, grid_selector="b-grid", click=False):
        """`text` bo'yicha grid qatorini topadi, ko'rinishini va (berilgan bo'lsa)
        `contains` dagi har bir matnni (nom, status va h.k.) o'z ichiga olishini tekshiradi.
        `click=True` berilsa topilgan qatorni bosadi."""
        grid = self.page.locator(grid_selector)
        row = grid.locator(".tbl-row").filter(has_text=text).first
        expect(row).to_be_visible()
        for value in contains:
            expect(row).to_contain_text(value)
        if click:
            row.click()
        return row

    # ------------------------------------------------------------------------------------------------------------------

    def grid_controller(
        self,
        *,
        search=None,
        expand=False,
        reload=False,
        open_filter=False,
        open_setting=False,
        controller_selector="b-grid-controller",
    ):
        """List formadagi `b-grid-controller` boshqaruvlari. Tanlovga qarab bittasi bajariladi:

          - search="matn": qidiruv maydoniga yozib Enter bosadi (loader kutiladi)
          - expand=True: "X / Y" (page size, fa-arrow-down) tugmasini bosib ko'proq qator yuklaydi
          - reload=True: ro'yxatni yangilaydi (fa-redo)
          - open_filter=True: filtr oynasini ochadi (fa-filter)
          - open_setting=True: setting/ustunlar menyusini ochadi (fa-bars)
        """
        gc = self.page.locator(controller_selector).first

        if search is not None:
            field = gc.locator('input[ng-model="o.searchValue"]').first
            expect(field).to_be_visible()
            field.fill(search)
            field.press("Enter")
            self.wait_for_loader()
            return
        if expand:
            gc.locator("button:has(i.fa-arrow-down)").first.click()
            self.wait_for_loader()
            return
        if reload:
            gc.locator('button[ng-click="reload()"]').first.click()
            self.wait_for_loader()
            return
        if open_filter:
            gc.locator('button[ng-click="openFilter()"]').first.click()
            return
        if open_setting:
            gc.locator("button.dropdown-toggle:has(span.fa-bars)").first.click()
            return

        raise ValueError(
            "grid_controller(): search, expand, reload, open_filter yoki open_setting dan bittasini bering"
        )

    # ------------------------------------------------------------------------------------------------------------------

    def text(self, *values, root="b-page"):
        content = self.page.locator(root) if isinstance(root, str) else root
        for value in values:
            if value:
                expect(content).to_contain_text(value)

    # ------------------------------------------------------------------------------------------------------------------

    def multiselect(self, label, *option_texts, name=None, index=0, close=True, exact=True, timeout=30_000, root=None):
        """Multi-select b-input ("N Выбранных") bilan ishlash.

        label: field label (masalan "Роли", "Рабочие зоны") — b-input shu orqali topiladi.
        option_texts: tanlanadigan bir yoki bir nechta variant matni.
        name: berilsa, label e'tiborsiz va `b-input[name=...]` orqali topiladi
              (masalan name="roles"/"rooms" — UI matniga bog'liq emas, barqarorroq).

        Single-select `select_b_input`/`b_input` dan farqi (Штат formasida
        MCP bilan tasdiqlangan, 2026-06-30):
          - tanlangach search maydoni bo'shaydi (variant matnini ko'rsatmaydi),
            shuning uchun search value tasdiqlanmaydi;
          - dropdown (`.hint`) b-input ICHIDA render bo'ladi (body'ga portal emas);
          - tanlangach dropdown ochiq qoladi — ko'p variant tanlash mumkin;
          - tasdiqlash `.multiple` ichidagi chip (tanlangan element) bo'yicha qilinadi.

        close=True: oxirida Escape bilan dropdown yopiladi (keyingi b-input uchun zarur).
        """
        root = root or self.page
        if name is not None:
            b_input = root.locator(f'b-input[name="{name}"]').nth(index)
        else:
            # `_field_locator_by_label(target="b-input")` ko'rinmas labellarni o'tkazib
            # yuboradi (masalan "Рабочие зоны" yashirin span'i), shuning uchun to'g'ri
            # b-input ga tushadi; qaytadigan locator b-input elementining o'zi.
            b_input = self._field_locator_by_label(label, index=index, root=root, target="b-input")

        expect(b_input).to_be_visible()
        search = b_input.locator('input[placeholder="Поиск..."]').first
        multiple = b_input.locator(".multiple").first

        for option_text in option_texts:
            search.click()
            option = b_input.locator(".hint").get_by_text(option_text, exact=exact).first
            expect(option).to_be_visible(timeout=timeout)
            option.click()
            expect(multiple).to_contain_text(option_text)

        if close:
            search.press("Escape")
        return b_input

    # ------------------------------------------------------------------------------------------------------------------

    def _label_pattern(self, label):
        return re.compile(rf"^\s*{re.escape(label)}\s*(?:\*)?\s*$", re.IGNORECASE)

    # ------------------------------------------------------------------------------------------------------------------

    def _field_target(self, container, target):
        if target == "b-input":
            return container.locator("b-input:has(input[placeholder])").first
        if target == "switch":
            return container.locator("input[type='checkbox'], [role='switch']").first
        if target == "input":
            return container.locator(
                "xpath=.//*[self::input or self::textarea]"
                "[not(ancestor::b-input) and not(@type='checkbox') and not(@type='radio')]"
                "[not(starts-with(@id,'focusser-'))]"
            ).first
        return container.locator("input, textarea, b-input, [role='switch']").first

    # ------------------------------------------------------------------------------------------------------------------

    def _field_container_by_label(self, label, needs_search=False, index=0, root=None, target=None):
        root = root or self.page
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
        root = root or self.page
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
        root = root or self.page
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
            "switch": "following::input[@type='checkbox'][1]",
        }[target]

        match_index = 0
        for label_index in range(label_locator.count()):
            label_item = label_locator.nth(label_index)
            try:
                expect(label_item).to_be_visible(timeout=1_000)
            except (AssertionError, PlaywrightTimeoutError):
                continue

            if target == "switch":
                # Label matni <label> ning O'ZI bo'lishi mumkin (checkbox — uning ichida,
                # masalan Smartup counterparty toggle'lari <label><input><t>Клиент</t></label>).
                # `ancestor::label` self'ni hisobga olmaydi → label element uchun count 0 bo'lib
                # `following::` keyingi qatordagi checkbox'ga tushib ketardi (Клиент→Сотрудник bug).
                # `ancestor-or-self` label wrapper ichidagi to'g'ri checkbox'ni topadi.
                field = label_item.locator("xpath=(ancestor-or-self::label[1]//input[@type='checkbox'])[1]")
                if field.count() == 0:
                    field = label_item.locator(f"xpath={target_xpath}")
            else:
                field = label_item.locator(f"xpath={target_xpath}")

            if field.count() == 0:
                container = self._field_container_by_label(label, index=match_index, root=root, target=target)
                field = self._field_target(container, target)
            if field.count() == 0:
                continue

            if target != "switch":
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
        timeout=30_000,
    ):
        root = root or self.page
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

            query = search_text or option_text
            if server_search:
                search.press("ControlOrMeta+A")
                search.press("Backspace")
                search.press_sequentially(query, delay=delay)
            else:
                search.fill(query)

            option = b_input.locator(".hint-item").filter(has_text=option_text).first
            if option.count() == 0:
                option = b_input.locator("div.hint").get_by_text(option_text, exact=exact).first
            if option.count() == 0:
                option = b_input.get_by_text(option_text, exact=exact).last
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

        `index` bir nechta mos input orasidan N-chisini, `root` (Page yoki modal Locator)
        topishni cheklaydi.
        """
        root = root or self.page

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
