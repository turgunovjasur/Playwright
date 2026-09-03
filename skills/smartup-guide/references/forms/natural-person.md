# Natural Person Add Form

## Mundarija

- [URL Va Navigation](#url-va-navigation)
- [Test Arxitekturasi](#test-arxitekturasi)
- [Field Bilimlari](#field-bilimlari)
- [List Va View Tekshiruv](#list-va-view-tekshiruv)
- [Debug Notes](#debug-notes)

## URL Va Navigation

### Natural person add
Tags: natural-person, setup, form, navigation
- Navigation: `Справочники` -> `Физические лица` -> `Создать`.
- URL pattern: `/anor/mr/person/natural_person+add`.
- Test fayli: `tests/smoke/test_setup/test_05_natural_person.py`.
- Runner: `tests/smoke/test_setup/test_0_setup_runner.py`, step `06 - Natural Person` va `18 - Natural Person For Client 1`.

## Test Arxitekturasi

### Alohida natural person flow
Tags: natural-person, legal-person, helper
- Natural Person alohida entity test hisoblanadi; testcase logikasi `tests/smoke/test_setup/test_05_natural_person.py` ichidagi `run_natural_person` va `tests/smoke/test_setup/test_20_natural_person_for_client_1.py` ichidagi `run_natural_person_for_client_1` (`test_0_setup_runner` step 05 va 20) da turadi.
- Bir nechta test ishlatadigan UI oqimi `tests/smoke/flows/flow_natural_person.py` ga ajratilgan; test fayllari bir-biridan helper import qilmaydi.
- Reusable creator: `create_natural_person(page, name, person_code, *, client=False)` — list va add formani ochib, maydonlarni to'ldiradi va saqlaydi.
- View tekshiruvi: `check_natural_person_view(page, name)` — list rowni tanlab, viewda nom/statusni tekshiradi va listga qaytadi.
- Joriy smoke oqimi faqat `person_name` + `Код`ni ishlatadi; global
  `scope`/`mode` parametri yo'q.
- **Base funksiya refactorlari (2026-07-01):**
  - ✅ BAJARILDI: `_search_list(page, text)` olib tashlandi → hamma joyda `BasePage(page).grid_controller(search=text)` (aynan bir xil `o.searchValue` element+xatti-harakat; MCP tasdiqlagan). `_search_list` faqat shu faylda ishlatilgan edi.
  - ✅ BAJARILDI: `create_natural_person` save flowi
    `base.click(name="Сохранить", exact=True)` → `base.confirm_biruni()` →
    `base.expect_page(heading="Физические лица")` ko'rinishida ochiq yoziladi.
    `expect_page` loader overlay yo'qolishini ham kutgani uchun alohida
    `wait_for_loader()` kerak emas.
  - ✅ BAJARILDI (2026-07-14): `create_natural_person` va view tekshiruvi test faylidan `flow_natural_person.py` ga ko'chirildi; joriy `test_20_natural_person_for_client_1.py` boshqa test modulidan import qilmaydi.
  - ⏳ IMKONIYAT (hali bajarilmagan): `run_natural_person` + `run_natural_person_for_client_1` bitta parametrli `run_natural_person(page, code, *, client=False)` ga birlashtirilishi mumkin (client uchun `Клиенты` list qadamini `if client:` bilan qo'shib). Ikkala pytest entry saqlanadi. `test_0_setup_runner.py` `run_*` ni to'g'ridan-to'g'ri chaqiradi (import + `test_06`/`test_18` call-site), shuning uchun birlashtirilsa runner ham yangilanadi.

## Field Bilimlari

### Natural person add fields
Tags: natural-person, input, locator
- Smoke branch: majburiy `d.first_name` (`Имя *`) va `d.code` (`Код`) to'ldiriladi. Qisqa entity patterni bo'yicha xodim kodi/nomi `c_n_p_pw{code}` / `natural_person-pw{code}`, client kodi/nomi `c_n_c_pw{code}` / `natural_client-pw{code}` bo'ladi. Keyingi user/contract/order flowlar ko'rinadigan nomni exact qidiradi.
- **Locator tuzog'i (MCP 2026-06-30 tasdiqlangan):** `input(label="Имя")` shu formada xato tarzda `d.middle_name` ni topadi — "Имя" label DOMda first_name input'idan KEYIN keladi, shuning uchun `following::input` keyingi maydonga (middle_name) tushadi. Shu sabab `d.first_name` `input(ng_model="d.first_name", value=...)` (ng-model orqali) bilan to'ldiriladi. `input(label="Код")` esa to'g'ri `d.code` ga tushadi.
- **"Имя" — b-input, oddiy textbox emas (MCP 2026-07-01):** `Имя *` maydoni `b-input` (placeholder "Поиск...", ism autocomplete). Shuning uchun `following::input` label bilan noaniq — ng-model ishonchli. `Фамилия`, `Отчество`, `Код` esa oddiy `textbox`.
- **`Клиент` toggle FILIALga bog'liq (user tuzatishi 2026-07-01):** `Клиент` maydoni add formada faqat TO'G'RI filialga o'tilганda ko'rinadi. Shu sabab `test_natural_person`/`test_natural_person_for_client_1` wrapperlari `run_*` dan oldin `switch_filial(page, name=f"filial-pw{code}")` qiladi (setup zanjirida `run_room` allaqachon shu filialга o'tган). MCP tekshiruvida `red_test` ning DEFAULT filialida edim (switch_filial qilmagan) — shuning uchun `Клиент` ko'rinmadi va DOMda faqat `d.state` (`Активный`) hamda chat-widget `a.feedback.anonymous` checkboxlari bor edi. Xulosa: bu company-config emas, filial masalasi — standalone debug/MCP'da avval to'g'ri filialга `switch_filial` qilinmasa `Клиент` bo'lmaydi. Client testni standalone run qilганда `NEW_CODE=0` bilan mavjud filial-pw{code} kerak.
- **Counterparty toggle'lari — base checkbox() (MCP, 2026-07-01/07-02):**
  to'g'ri `filial-pw{code}`da add formada 4 ta `<label>` ichidagi checkbox bor:
  `d.state` (`Активный`, default checked), `d.is_supplier` (`Поставщик`),
  `d.is_client` (`Клиент`), `d.is_employee` (`Сотрудник`). Har biri `<label>`
  ichida `input[type=checkbox]` + `<t>` label matnli. `Клиент` uchun
  `BasePage(page).checkbox(label="Клиент", checked=True)`, `Активный` uchun
  `checkbox(label="Активный", expect_checked=True)` ishlatiladi.
  - ⚠️ **BUG topildi + tuzatildi (2026-07-02):** eski `_field_locator_by_label(target="switch")` `ancestor::label//input` ishlatardi va `<label>` element uchun (self hisobga olinmagani sabab) `following::` keyingi checkbox'ga siljib, `checkbox(label="Клиент")` aslida `d.is_employee` (Сотрудник = worker) ni tanlardi. MCP'da 4-ta toggle HAMMASI 1 ga siljigani tasdiqlandi. `checked=`+`expect_checked=` bir xil xato elementга tushgani uchun test "yashil" bo'lib bug maskalanardi. Tuzatish `base_page.py:521` → `(ancestor-or-self::label[1]//input[@type='checkbox'])[1]`. To'liq tafsilot: `references/ui-patterns.md` "Switch-label wrapper resolution bug + fix".
- `Регион` legal persondagi kabi b-tree search (`_$bTree.searchValue`); avval input click/focus qilinadi, keyin `Ташкент` qidirilib hint ichidagi exact text/label yoki `.jstree-anchor` orqali `город Ташкент`/`Ташкент` optioni tanlanadi.
- Add forma to'liq maydon inventari (MCP 2026-07-01): Пол (radio Мужской/Женский), Фамилия, Имя*, Отчество, Код, Дата рождения, Серийный номер паспорта (AA + 7 raqam), Статус (checkbox Активный), Регион, Адрес, Почтовый адрес, Юридическое лицо, Телефон, ИНН/ПНФЛ (+Поиск btn), GPS координаты, Телеграм, Email, Ответственный, Веб-сайт; pastda tablar: Характеристики (Группа/Категория/Тип), Расчетный счет, Файлы, Примечание.
- Add forma screenshot: `references/forms/screenshots/natural-person/add-form-red_test-2026-07-01.png`.

## List Va View Tekshiruv

### Natural person list
Tags: natural-person, list, grid, assert
- Default list gridda `Дата создания`, `Название`, `Пол`, `Дата рождения`, `Группа`, `Категория`, `Статус` ko'rinadi; `Код` default ko'rinmaydi.
- Test global searchda code bo'yicha filter qilishi mumkin, lekin row assert ko'rinadigan nom (`natural_person-pw{code}`, `natural_client-pw{code}` yoki director F.I.O.) va `Активный` statusni tekshiradi.
- Row tanlanганда inline action toolbar chiqadi: `Просмотр` / `Изменить` / `Неактивный` / `Удалить`.
- **Search dublikati (MCP 2026-07-01 tasdiqlangan):** listdagi qidiruv testda `_search_list` (`get_by_role("searchbox", name="Поиск")`) bilan qilinadi, lekin bu aynan `BasePage.grid_controller(search=text)` ishlatadigan element — `b-grid-controller` ichidagi `input[ng-model="o.searchValue"]` (`type=search`, placeholder "Поиск...", ko'rinadigan). Sahifadagi ikkinchi input `a.search.value` (placeholder "Поисковый запрос", `type=text`, KO'RINMAS/global) `searchbox` roliga kirmaydi, shuning uchun `get_by_role("searchbox")` faqat grid controller inputiga tushadi. Xulosa: `_search_list` = `grid_controller(search=)` dublikati, base funksiya bilan almashtirilsa bo'ladi.
- View tugmasi: row tanlangandan keyin `Просмотр`.

### Natural person view
Tags: natural-person, view, assert
- View URL pattern: `/anor/mr/person/natural_person_view?person_id=<id>`.
- View heading bilan tab heading birga chiqishi mumkin; heading assertda `get_by_role("heading").filter(has_text="Физическое лицо (просмотр)")` ishlatiladi.
- View strukturasi (MCP 2026-07-01): yuqorida `Закрыть` tugmasi; summary blok `nom (id)` + `Активный`; chap tomonda Пол/Имя/Фамилия/Отчество/Код/Дата рождения; ichki tablar: `Основная информация`, `Детали`, `Характеристика контрагента`, `Расчетный счет`, `Файлы`. Smoke `BasePage(page).text(full_name, "Активный")` — default `b-page` ichida nom va statusni tekshiradi (yetarli).
- Joriy view assert yaratilgan person name va `Активный` statusini tekshiradi.
- `natural_client-pw{code}` case uchun person viewdan keyin `Клиенты` listida ham client nomi borligi tekshiriladi.

### User person IDni view URLdan olish

Tags: natural-person, user, view, id, data-store
Status: code-confirmed
Verified: 2026-08-27
Source: user; `tests/smoke/test_setup/test_05_natural_person.py`

- `natural_person-pw{code}` keyingi `run_user` testida userning
  `Физическое лицо` maydoniga bog'lanadi.
- Setup test view URLdagi `person_id`ni `data_store.json.user_person_id`
  kaliti bilan saqlaydi; bu client person IDdan alohida.

### Client person IDni view URLdan olish

Tags: natural-person, client, view, id, data-store
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI; `tests/smoke/test_setup/test_20_natural_person_for_client_1.py`

- Client view URL patterni `anor/mr/person/natural_person_view?person_id=<id>`;
  summary `natural_client-pw{code} (<id>)` ko'rinishida IDni ko'rsatadi.
- Client setup test view ochilgach `person_id`ni musbat integer sifatida
  tekshiradi va `data_store.json.client_person_id`ga saqlaydi.

## Debug Notes

### 2026-06-02 list/view verification
Tags: natural-person, client, list, view, run-result
- `test_01_authorization` + `test_03_filial` + `test_06_natural_person` + `test_18_natural_person_for_client_1` saqlangan code (`NEW_CODE=0`) va headless rejimda passed: 4 passed in 27.74s.
- Run code: `5535`; natural person va natural client list/view assertlari o'tdi.

### 2026-07-01 base-funksiya refactor verification
Tags: natural-person, client, refactor, run-result
- `_search_list` → `grid_controller(search=)` va save flow refactoridan keyin:
  `test_01_authorization` + `test_02_legal_person` + `test_03_filial` +
  `test_04_room` + `test_06_natural_person` +
  `test_18_natural_person_for_client_1` = **6 passed in 71.48s** (existing
  company `red_test`, yangi code `608492`, headed).
- `test_18` o'tishi `Клиент` toggle FILIALga bog'liqligini empirik tasdiqladi: `run_room` (test_04) `filial-pw{code}` ga o'tгач, `create_natural_person(client=True)` da `Клиент` ko'rindi va bosildi.

### 2026-07-14 reusable flow refactor verification
Tags: natural-person, flow, duplicate-code, run-result
- `create_natural_person` va `check_natural_person_view` `tests/smoke/flows/flow_natural_person.py` ga ajratilgandan keyin mavjud filialda noyob person name/code bilan create -> list search -> row assert -> view assert oqimi **1 passed in 22.38s** (`NEW_CODE=0`, headless).
- `client=True` branch ham noyob person name/code bilan create -> natural person list/view -> `Клиенты` list assert oqimida **1 passed in 23.93s** (`NEW_CODE=0`, headless).
- Refactordan oldingi `natural_person_pw{code}` formatini saqlangan eski `code` bilan standalone qayta ishlatish serverda `Найден дубликат кода` xatosini bergan. Bu locator/refactor xatosi emas.
- Oraliq uzun `code_natural_person_pw{code}` / `code_natural_client_pw{code}` formatida aynan `test_05_natural_person.py` saqlangan code (`NEW_CODE=0`) va headless rejimda **1 passed in 28.06s**, joriy `test_20_natural_person_for_client_1.py` esa **1 passed in 24.03s**. Keyin loyiha qoidasi bo'yicha ular qisqa `c_n_p_pw{code}` / `c_n_c_pw{code}` formatiga o'tkazildi.
