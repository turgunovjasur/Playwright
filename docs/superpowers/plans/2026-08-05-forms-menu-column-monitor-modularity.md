# Forms Menu-Column va Configurable FormMonitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Yangi forma qo‘shishni bitta deklarativ dict bilan cheklaydigan, `shell + navbar_tab + menu_column` bo‘yicha alohida pytest item yaratadigan va check/diagnostikalari tanlanadigan markaziy `FormMonitor` qurish.

**Architecture:** `FormMonitor` testlar uchun yagona façade bo‘lib qoladi; check, diagnostika, case-normalizatsiya va reporting ichki modullarga responsibility bo‘yicha ajratiladi. Leaf testlarda faqat forma inventarlari va qisqa `run_*` wrapper qoladi; takroriy login/filial/monitor lifecycle shell-specific reusable runner orqali bajariladi. Barcha defaultlar joriy Forms xatti-harakatini saqlaydi, custom konfiguratsiya esa faqat explicit berilganda ishlaydi.

**Tech Stack:** Python, pytest, Playwright Sync API, Allure, mavjud Smartup `BasePage`/`AngularBasePage` helperlari.

## Global Constraints

- Barcha kod o‘zgarishlari `dev1` branchida qilinadi.
- Forma test identifikatori `shell + navbar_tab + menu_column` bo‘ladi; `menu_column` yolg‘iz ishlatilmaydi.
- Formalar oddiy `list` ichidagi `dict`lar bo‘lib qoladi; dataclass, NamedTuple yoki katta universal framework qo‘shilmaydi.
- `label` optional; berilmasa `menu_item`, `action`, `page_links` va `add_icon`dan avtomatik yaratiladi.
- Normal testda check/diagnostika konfiguratsiyasi yozilmaydi: default holatda barchasi yoqilgan.
- `checks=[]` barcha hard checklarni o‘chiradi va muvaffaqiyatli navigatsiya natijasi `OBSERVED_ONLY` bo‘ladi.
- `diagnostics=[]` barcha observation-only diagnostikalarni reportdan chiqaradi.
- Per-form check/diagnostic override qo‘shilmaydi; konfiguratsiya faqat bitta pytest test/FormMonitor instance darajasida bo‘ladi.
- O‘chirilgan check `expect_form_open()` yoki boshqa tashqi helper orqali yashirincha ishlamasligi kerak.
- Bitta forma bir marta navigatsiya qilinadi va checklar bitta yakuniy state’dan baholanadi.
- JS hard check yoqilgan bo‘lsa, diagnostikalar o‘chirilgan holatda ham shellga mos JS capture dependency ishlaydi.
- Unit test fayllari user alohida so‘ramagani sabab o‘zgartirilmaydi; pytest/smoke/test commandlari faqat user aynan `run qil` deganda bajariladi.
- Default verifikatsiya syntax/AST parse, import/read-only contract inspection, knowledge-base validator va `git diff --check` bilan cheklanadi.

---

## Status

| Task | Holat | Commit |
|---|---|---|
| 1. Final plan va baseline | COMPLETED | `eb87ba1` |
| 2. Check modulini ajratish | COMPLETED | `7a89862` |
| 3. Diagnostika modulini ajratish | COMPLETED | `b052b6d` |
| 4. Configurable FormMonitor va `OBSERVED_ONLY` | COMPLETED | `dee5521` |
| 5. Case identity, avtomatik label va menu-column runner | COMPLETED | `d09730a` |
| 6. Mavjud Forms testlari va runner migratsiyasi | COMPLETED | `4ec0e24` |
| 7. Reporting schema/analyzer/docs | COMPLETED | `3b27f96` |
| 8. Yakuniy static verifikatsiya | COMPLETED | `79849ed` |

## File Structure

### Yangi fayllar

- `tests/smoke/test_forms/form_checks.py` — hard check nomlari, konfiguratsiya normalizatsiyasi, har check uchun alohida evaluator va failure priority.
- `tests/smoke/test_forms/form_diagnostics.py` — browser signal scriptlari, page listener/capture state, har diagnostika uchun alohida collector.
- `tests/smoke/test_forms/form_cases.py` — forma dict normalizatsiyasi, composite identity, optional label va active/skipped inventory.
- `tests/smoke/test_forms/form_reporting.py` — result builder, terminal/Allure matni, schema-v4 payload va summary.
- `tests/smoke/test_forms/menu_column_runner.py` — legacy/A2 menu-column testlarining takroriy monitor/precondition/section lifecycle’i.

### O‘zgartiriladigan fayllar

- `tests/smoke/test_forms/form_monitor.py` — kichik façade/orchestrator; barcha enabled check va diagnostikalarni registries orqali chaqiradi.
- `tests/smoke/test_forms/flow.py` — faqat navigatsiya primitive/orchestration; tashqi `expect_form_open()` hard validation olib tashlanadi.
- `tests/smoke/test_forms/test_01_spravochniki_menu_forms.py` — legacy `Справочники` inventarlarini composite menu-column testlarga ajratadi.
- `tests/smoke/test_forms/test_02_a2_admin_menu_forms.py` — A2 inventarlarini `navbar_tab + menu_column` testlariga ajratadi.
- `tests/smoke/test_forms/test_03_prodaja_menu_forms.py` — `Продажа` inventarlarini menu-column testlariga ajratadi.
- `tests/smoke/test_forms/test_0_forms_runner.py` — har composite identity uchun alohida sibling pytest wrapper.
- `scripts/analyze_test_result.py` — schema-v3 backward compatibility va schema-v4 nested check/diagnostic parsing.
- `skills/write-test/references/project-rules.md` — yangi forma qo‘shish va menu-column test qoidasi.
- `skills/maintain-test-infra/references/reporting.md` — enabled/disabled signal va schema-v4 kontrakti.
- `skills/smartup-guide/references/testing-debug.md` — FormMonitor konfiguratsiyasi va report semantikasi.

---

### Task 1: Final Plan va Git Baseline

**Files:**
- Create: `docs/superpowers/plans/2026-08-05-forms-menu-column-monitor-modularity.md`

**Interfaces:**
- Consumes: user tasdiqlagan composite identity, `OBSERVED_ONLY`, optional auto-label va soddalashtirilgan test talablari.
- Produces: keyingi barcha tasklar uchun exact scope, status jadvali va commit chegaralari.

- [x] **Step 1: `dev1` branchini tekshirish**

  Kutilgan holat: `git branch --show-current` → `dev1`.

- [x] **Step 2: mavjud worktree o‘zgarishlarini tekshirish**

  Kutilgan holat: `git status --short --branch`da uncommitted fayl yo‘q. Agar bo‘lsa user so‘raganidek avval alohida baseline commit qilinadi.

- [x] **Step 3: final plan faylini yaratish**

  Ushbu fayl task checkboxlari va `Status` jadvalining yagona implementation tracking manbasi bo‘ladi.

- [x] **Step 4: plan self-review va commit**

  Placeholder iboralari, noto‘g‘ri fayl yo‘llari va task/interface nomlari tekshiriladi; so‘ng faqat plan fayli commit qilinadi.

---

### Task 2: Hard Checklarni Alohida Modulga Ajratish

**Files:**
- Create: `tests/smoke/test_forms/form_checks.py`
- Modify: `tests/smoke/test_forms/form_monitor.py`

**Interfaces:**
- Consumes: `case: dict`, `state: dict`.
- Produces: `CHECK_NAMES`, `normalize_enabled_names(...)`, `evaluate_checks(...)`, `primary_check_failure(...)` va olti alohida evaluator.

- [x] **Step 1: joriy hard-check kontraktini muzlatish**

  Quyidagi reason priority saqlanadi: `URL_MISMATCH`, `APPLICATION_ERROR`, `JS_ERROR`, `LOADER_NOT_FINISHED`, `CONTENT_NOT_READY`, `TITLE_MISMATCH`.

- [x] **Step 2: oltita pure evaluator yaratish**

  Exact funksiyalar:

  ```python
  check_url(case, state)
  check_application_error(case, state)
  check_javascript(case, state)
  check_loader(case, state)
  check_content_ready(case, state)
  check_title(case, state)
  ```

  Har biri bir xil result shape qaytaradi:

  ```python
  {
      "enabled": True,
      "passed": True,
      "reason_code": "",
      "expected": "...",
      "actual": "...",
      "detail": "...",
  }
  ```

- [x] **Step 3: ordered registry va primary failure helperini qo‘shish**

  `CHECK_FUNCTIONS` yuqoridagi fixed priority tartibida bo‘ladi. Barcha enabled checklar natijasi saqlanadi, overall status birinchi failed checkdan olinadi.

- [x] **Step 4: FormMonitor’ni yangi evaluatorlarga ulash**

  Eski `_assert_healthy_form_state()` va takroriy boolean hisoblar yangi result modelidan foydalanadi; default xatti-harakat o‘zgarmaydi.

- [x] **Step 5: static verifikatsiya va commit**

  Changed Python fayllari AST/syntax parse qilinadi, `git diff --check` bajariladi va task alohida commit qilinadi.

---

### Task 3: Diagnostikalarni Alohida Modulga Ajratish

**Files:**
- Create: `tests/smoke/test_forms/form_diagnostics.py`
- Modify: `tests/smoke/test_forms/form_monitor.py`

**Interfaces:**
- Consumes: Playwright `page`, final `state`, bounded page-event buffers.
- Produces: `DIAGNOSTIC_NAMES`, capture install/read/reset helperlari va beshta alohida diagnostic collector.

- [x] **Step 1: browser capture primitive’larini ko‘chirish**

  A2 init-script JS/resource/promise capture, legacy `pageerror`, HTTP response label, visible error/loader/content state read logiclari bitta modulga ko‘chiriladi.

- [x] **Step 2: alohida diagnostic funksiyalar yaratish**

  Exact funksiyalar:

  ```python
  diagnose_busy(state)
  diagnose_resource_errors(state)
  diagnose_promise_rejections(state)
  diagnose_failed_requests(page_events)
  diagnose_title_metadata(state)
  ```

- [x] **Step 3: signal sample limit va count kontraktini saqlash**

  Raw sample maksimumi `MAX_PAGE_EVENTS`; count to‘liq qoladi. Query string reportga yozilmaydi.

- [x] **Step 4: FormMonitor event lifecycle’ini yangi modulga ulash**

  Listener install/reset/remove har case chegarasida ishlaydi va qo‘shni forma signali keyingi case’ga o‘tmaydi.

- [x] **Step 5: static verifikatsiya va commit**

  Syntax parse, import-cycle inspection va `git diff --check`dan keyin alohida commit.

---

### Task 4: Configurable FormMonitor va OBSERVED_ONLY

**Files:**
- Modify: `tests/smoke/test_forms/form_checks.py`
- Modify: `tests/smoke/test_forms/form_diagnostics.py`
- Modify: `tests/smoke/test_forms/form_monitor.py`
- Modify: `tests/smoke/test_forms/flow.py`

**Interfaces:**
- Consumes: `checks=None | list[str]`, `diagnostics=None | list[str]`.
- Produces: test-level enabled-name contract, `OBSERVED_ONLY` status va bitta final snapshotdan result.

- [x] **Step 1: konfiguratsiya semantikasini implement qilish**

  - `None` → barcha registered nomlar;
  - `[]` → hech biri;
  - `list[str]` → faqat ko‘rsatilganlari;
  - unknown yoki duplicate nom → aniq `ValueError`.

- [x] **Step 2: tashqi hard-validation dublikatini olib tashlash**

  `run_form_cases()` endi `validate=lambda: expect_form_open(...)` bermaydi. `FormMonitor.run_case(case, navigate=...)` enabled checklarni o‘zi bajaradi.

- [x] **Step 3: bitta bounded settle va final snapshot ishlatish**

  Navigatsiyadan keyin shell transitioni bir marta settle qilinadi; barcha enabled checklar bir xil final state’dan baholanadi. Har check uchun ketma-ket 15 soniyalik alohida timeout ishlatilmaydi.

- [x] **Step 4: `OBSERVED_ONLY` statusini qo‘shish**

  Navigatsiya muvaffaqiyatli va enabled hard checklar soni nol bo‘lsa result `OBSERVED_ONLY`. Navigation yoki precondition failure mavjud status/reason bilan qoladi. `finish()` `OBSERVED_ONLY`ni actionable failure deb hisoblamaydi.

- [x] **Step 5: disabled signal report kontraktini saqlash**

  Har registered check/diagnostic JSONda `enabled` holati bilan ko‘rinadi; disabled signal pass sifatida ko‘rsatilmaydi.

- [x] **Step 6: static verifikatsiya va commit**

  Syntax parse, exact API/reference search va `git diff --check`dan keyin alohida commit.

---

### Task 5: Composite Case Identity, Auto-Label va Menu-Column Runner

**Files:**
- Create: `tests/smoke/test_forms/form_cases.py`
- Create: `tests/smoke/test_forms/menu_column_runner.py`
- Modify: `tests/smoke/test_forms/form_monitor.py`
- Modify: `tests/smoke/test_forms/flow.py`

**Interfaces:**
- Consumes: oddiy forma definition listlari va `shell`, `navbar_tab`, `menu_column`.
- Produces: normalized planned cases, stable `test_identity`, generated `label`, shell-specific reusable runnerlar.

- [x] **Step 1: composite identity helperini qo‘shish**

  Exact helper:

  ```python
  form_test_identity(*, shell, navbar_tab, menu_column)
  ```

  Normalized identity uchala qismni saqlaydi. `shell` va `navbar_tab` missing
  bo‘lsa `ValueError`; real ustunsiz menu (`menu_column=None`) identity’da
  `<ustunsiz>` nomi bilan aniq ko‘rsatiladi.

- [x] **Step 2: optional labelni normalizatsiya qilish**

  `label` berilgan bo‘lsa whitespace-normalized qiymat ishlatiladi. Bo‘lmasa user-visible track `menu_item → Создать dropdown/action → page_links → +add icon`dan avtomatik yaratiladi; `navbar_tab` va `menu_column` Allure test identityda allaqachon ko‘rsatilgani sabab labelda takrorlanmaydi.

- [x] **Step 3: duplicate definition guard qo‘shish**

  Bitta composite test ichida `filial + menu_item + action + page_links + canonical path` bir xil bo‘lsa inventory construction `ValueError` beradi.

- [x] **Step 4: shell-specific menu-column runnerlarni yaratish**

  Exact public APIlar:

  ```python
  run_legacy_menu_column_forms(...)
  run_a2_menu_column_forms(...)
  ```

  Helperlar inventory/monitor/finalizationni takrorlamaydi, ammo legacy va A2 filial/shell kontraktlarini bitta mode-dispatcherga aralashtirmaydi.

- [x] **Step 5: normal leaf testni data-only qilish**

  Leaf modulda constants, separate form lists, bitta qisqa `run_*` va standalone `test_*` qoladi. Default check/diagnostika argumentlari yozilmaydi.

- [x] **Step 6: static verifikatsiya va commit**

  Syntax parse, duplicate inventory read-only inspection va `git diff --check`dan keyin alohida commit.

---

### Task 6: Mavjud Forms Suites va Runner Migratsiyasi

**Files:**
- Modify: `tests/smoke/test_forms/test_01_spravochniki_menu_forms.py`
- Modify: `tests/smoke/test_forms/test_02_a2_admin_menu_forms.py`
- Modify: `tests/smoke/test_forms/test_03_prodaja_menu_forms.py`
- Modify: `tests/smoke/test_forms/test_0_forms_runner.py`

**Interfaces:**
- Consumes: `run_legacy_menu_column_forms(...)`, `run_a2_menu_column_forms(...)` va mavjud form definitionlar.
- Produces: har unique `shell + navbar_tab + menu_column` uchun alohida pytest wrapper va o‘zgarmagan total active/skipped inventory.

- [x] **Step 1: mavjud definitionlarni composite identity bo‘yicha inventory qilish**

  Har forma aynan bitta groupda qolishi, admin/operational/direct/page-link/action sectioni saqlanishi tekshiriladi.

- [x] **Step 2: `Справочники` leafini menu-column run funksiyalariga ajratish**

  `Справочники`, `Основное`, `Маркетинг` identitylari alohida test bo‘ladi; admin-only va operational sectionlar tegishli identity ichida qoladi.

- [x] **Step 3: `Продажа` leafini menu-column run funksiyalariga ajratish**

  Har mavjud `menu_column` alohida test; active/intentional skip pathlar yo‘qolmaydi.

- [x] **Step 4: A2 leafini composite identitylarga ajratish**

  Takrorlanuvchi column nomlari `navbar_tab` bilan ajratiladi; admin va operational filial konteksti saqlanadi.

- [x] **Step 5: Forms runner wrapperlarini yangilash**

  Har parametrized wrapperda stable `allure.dynamic.title`, `progress_test_id` va bitta `run_*` chaqiruvi bo‘ladi. Bir leaf test boshqa leaf testni chain qilmaydi.

- [x] **Step 6: total inventory va duplicate consumerlarni read-only tekshirish**

  Migrationdan oldingi active/intentional skip total bilan keyingi total teng bo‘lishi kerak; bir forma ikki testda takrorlanmasligi kerak.

- [x] **Step 7: static verifikatsiya va commit**

  Syntax parse va `git diff --check`dan keyin alohida commit.

---

### Task 7: Reporting Schema, Analyzer va Knowledge Sync

**Files:**
- Create: `tests/smoke/test_forms/form_reporting.py`
- Modify: `tests/smoke/test_forms/form_monitor.py`
- Modify: `tests/smoke/test_forms/flow.py`
- Modify: `scripts/analyze_test_result.py`
- Modify: `skills/write-test/references/project-rules.md`
- Modify: `skills/maintain-test-infra/references/reporting.md`
- Modify: `skills/smartup-guide/references/testing-debug.md`

**Interfaces:**
- Consumes: nested check/diagnostic results, `OBSERVED_ONLY`, auto-label va composite identity.
- Produces: schema-v4 JSON, v3/v4 analyzer compatibility va user-readable terminal/Allure summary.

- [x] **Step 1: reporting helperlarini alohida modulga ko‘chirish**

  Result build, status counts, metrics, noise aggregation, duration va summary rendering behavior saqlanadi.

- [x] **Step 2: schema-v4 payloadni chiqarish**

  Har resultda `identity`, `label`, nested `checks` va nested `diagnostics`; payloadda enabled-name config saqlanadi. Oldingi status/URL/title/lifecycle fieldlar compatibility uchun qoladi.

- [x] **Step 3: human reportni ixcham saqlash**

  Terminal/Allure default holatda failed checklar va actionable diagnosticlarni ko‘rsatadi; disabled yoki pass bo‘lgan har signal alohida uzun qatorga aylantirilmaydi. Summary tepada `enabled/total` coverage beradi.

- [x] **Step 4: analyzerga v3/v4 compatibility qo‘shish**

  Eski flat `checks` va yangi nested results ikkalasi bitta issue modeliga normalizatsiya qilinadi. `OBSERVED_ONLY` failure sifatida chiqarilmaydi.

- [x] **Step 5: current knowledge/reference fayllarini yangilash**

  Yangi grouping, label, configuration, schema va report semantikasi `code-confirmed` provenance bilan mos reference’larga yoziladi.

- [x] **Step 6: static verifikatsiya va commit**

  Syntax parse, knowledge-base validator va `git diff --check`dan keyin alohida commit.

---

### Task 8: Yakuniy Static Verification va Status Closure

**Files:**
- Modify: `docs/superpowers/plans/2026-08-05-forms-menu-column-monitor-modularity.md`

**Interfaces:**
- Consumes: Task 2–7 commitlari va final worktree.
- Produces: completed status matrix, verification evidence va clean committed `dev1` worktree.

- [x] **Step 1: barcha changed Python fayllarini syntax parse qilish**

  Pytest collection yoki smoke run ishlatilmaydi.

- [x] **Step 2: contract qidiruvlarini bajarish**

  Eski `validate=` callback, tashqi hard validation, schema-v3-only parser va duplicate inventory consumerlari qolmaganini `rg` bilan tekshirish.

- [x] **Step 3: knowledge-base validator va patch tekshiruvini bajarish**

  `validate_knowledge_base.py` va `git diff --check` muvaffaqiyatli tugashi kerak.

- [x] **Step 4: plan statusini yakunlash**

  Har task `COMPLETED` yoki aniq sabab bilan `BLOCKED`; commit hashlar Status jadvaliga yoziladi.

- [x] **Step 5: barcha qolgan in-scope o‘zgarishlarni commit qilish**

  `git status --short` clean bo‘ladi. Pytest/smoke bajarilmagani final handoffda aniq yoziladi.

### Final Verification Evidence

- AST parse: Forms modullari, analyzer va knowledge validator — `15` fayl, xatosiz.
- Pyflakes: barcha changed Python fayllari — xatosiz.
- Composite identity: `19` pytest item, `19` unique identity.
- Inventory: Forms-01 `100 = 88 active + 12 skip`; Forms-02 `22 = 21 + 1`; Forms-03 `39 = 38 + 1`.
- Analyzer read-only sample: schema-v3 flat va schema-v4 nested resultlar normalizatsiya qilindi; `OBSERVED_ONLY` failurega kirmadi.
- Knowledge validator: `errors=0`.
- Forbidden contract search: `validate=`, `expect_form_open()`, eski suite runnerlari va schema-v3-only writer topilmadi.
- `git diff --check`: xatosiz.
- Pytest/smoke: user `run qil` demagani uchun bajarilmadi.

## Acceptance Criteria

- Yangi forma mavjud composite identityga bitta dict qo‘shish bilan testga kiradi.
- Yangi composite identity uchun yangi alohida pytest wrapper yaratiladi.
- Oddiy leaf testda login/filial/monitor boilerplate takrorlanmaydi.
- Default FormMonitor hozirgi oltita hard check va beshta diagnostikani bajaradi.
- `checks=[]` + muvaffaqiyatli navigation → `OBSERVED_ONLY`.
- Individual enabled list faqat tanlangan check/diagnostikalarni report qiladi.
- `label` yo‘q bo‘lsa deterministic user-visible label yaratiladi.
- O‘chirilgan check tashqi helper orqali failure bermaydi.
- Barcha enabled checklar bitta final state’dan baholanadi.
- Har forma bitta inventory/test identityda va bir marta navigatsiya qilinadi.
- Terminal, Allure va schema-v4 JSON bitta result modelidan quriladi.
- Analyzer schema-v3 eski artifact va schema-v4 yangi artifactni o‘qiydi.
- Unit test/pytest/smoke userning alohida `run qil` authoritysisiz bajarilmaydi.

## Self-Review

- Spec coverage: composite identity, `OBSERVED_ONLY`, optional auto-label, per-test check/diagnostic selection, separate functions, runner integration, modularity va report compatibility Task 2–7da qamrab olingan.
- Scope control: per-form overrides, yangi dataclass/type framework, production workflow dispatch va UI biznes flowlari scope’dan tashqarida.
- Type consistency: public configuration `None | list[str]`; identity va case/resultlar oddiy dict; shell-specific runnerlar alohida funksiyalar.
- Performance guard: bitta navigation, bitta bounded settle, bitta final snapshot; per-check sequential timeout yo‘q.
