# A2 (migratsiya qilingan yangi) formalar

Tags: a2, migrated-forms, filial, menu, navigation, error, url, new_forms

Smartup yangi formalari (yangi Angular/modern app) eski AngularJS Biruni app ustiga qo'shilgan. Ular
`new_forms.md` (repo root) da ro'yxatlangan va URL'да **`a2`** prefiksi bilan ajraladi.

## Arxitektura

- **Page-object chegarasi:** legacy AngularJS/Biruni formalar
  `utils/base_page.py::BasePage` bilan, yangi A2 Angular formalar
  `utils/angular_base_page.py::AngularBasePage` bilan yoziladi. Legacy class
  mavjud eski formalar tugamaguncha aktual saqlanadi; ikki DOM selectorlari bitta
  helperga fallback qilib aralashtirilmaydi.
- **Alohida app.** Eski menyudan a2 forma bosilganda `{base}/a2/{path}` ga **to'liq sahifa** navigatsiya bo'ladi
  (SPA hash-route emas). `base` = `company_url()`:
  - smartup.online: `https://smartup.online/a2/{path}`
  - app3: `https://app3.greenwhite.uz/xtrade/a2/{path}`
  - `{path}` = `new_forms.md` dagi yo'l, masalan `biruni/md/company_list`, `anor/rep/mbi/mkw/purchase`.
- **Sog'lom forma signali:** `document.title` forma nomiga aylanadi (masalan "Компании", "Логистика").
  Content async yuklanadi — dashboard/list/catalog formalar title resolve bo'lgach ham 1-1.5s kontent yuklaydi.
- **Muammo signallari** (title "Smartup Online" da qoladi):
  - `Страница не найдена` — 404 (forma yo'q).
  - `Нет доступа к форме {name}` / `Не удалось загрузить` / `Что-то пошло не так` — ruxsat yo'q yoki load error.
  - `+edit`/`_view`/`_details` yakka URL bilan ochilmaydi — id (record) kerak; title shell'da qoladi.

## Yangi Angular component kontrakti (Company'da live tasdiqlangan, 2026-07-23)

- Forma maydoni: `smt-control`; oddiy input: `smt-input` ichidagi native
  `input`/`textarea`; select: `smt-data-select` → `smt-select-trigger`.
- Select optionlari `.cdk-overlay-container` ichidagi `smt-select-dropdown li`
  sifatida portal qilinadi. Ular legacy `b-input .hint-item` yoki
  `.ui-select-choices-row-inner` emas. Option clickdan keyin dropdown ochiq
  qolishi mumkin; tashqi sahifa nuqtasini bosib overlay yopiladi va backdrop
  yo'qolgani kutiladi.
- List: `smt-data-table`/`smt-table`; data qatori `.smt-data-row`; ustunlar
  `[data-smt-col-key="..."]`; search native `input[type="search"]`.
- List yuklanayotgan paytda `.smt-skeleton` qatorlari ko'rinadi;
  `.block-ui-overlay` bo'lmasligi mumkin. URL/title yangilanishi component mount
  bo'lishidan oldin sodir bo'lishi mumkin, shu sabab stabil component yoki
  skeleton yo'qolishi alohida kutiladi.
- A2 ichki menyusi CDK overlay'da `[role="menu"]` va `[role="menuitem"]`
  bilan ishlaydi. A2 filial selectorida
  `data-testid="shell-project-filial--project-list"` /
  `data-testid="shell-project-filial--filial-list"` va `[role="option"]` bor.
  Legacy `.pt-3.px-2` va `a.menu-link...` selektorlari faqat eski shell'dan A2
  formaga kirish bosqichida ishlaydi; A2 ichida qayta ishlatilmaydi.
- A2 save errorlari `role=dialog`/CDK overlay'da chiqishi mumkin. Save helperi
  target page readiness va error dialogni bir vaqtda kutadi; error chiqsa uzoq URL
  timeoutini kutmasdan dialog matni bilan fail qiladi.

## Menyu FILIALга bog'liq (eng muhim kuzatuv, 2026-07-07)

- Eski chap menyu `session.si.filial.menus` ga bog'langan — **har filialда boshqacha formalar** ko'rinadi.
  Login'дан keyingi default filial odatda **"Администрирование"**.
- Barcha filiallarning to'liq menyu daraxti login'да oldindan yuklanadi:
  `angular scope -> a.session.si.projects[0].filials[].menus[].menus[].forms[]`.
  Har `form`: `{form (path), name, add_form, is_migrated: 'Y'/'N', url, add_form_url}`.
  **`is_migrated === 'Y'` ⇒ a2 forma.** (Bu modelni `page.evaluate` bilan read-only o'qish mumkin — diagnostika uchun.)
- **ASOSIY QOIDA: eski angular menyu orqali ochiladigan a2 formalar — BARCHASI ADMIN formalar.** Alohida "head"
  profil / alohida head test KERAK EMAS; hammasi bitta admin test'да (`test_a2_admin_forms.py`) yig'iladi.
- **Forma joyi (filial + aniq user track) — AVTORITET manba: `new_forms.md` (repo root).** U formalarni
  operatsion/Администрирование filial bo'yicha guruhlab, har biriga real user track (LEAF / LIST-ACTION / SIBLING)
  beradi. Qisqacha (2026-07-08 live tasdiqlangan):
  - "Администрирование" da: `kauth/company_client_list` (+undan `+add`/`+edit` list-action).
  - Operatsion filialda LEAF: Визиты/Логистика, dashboardlar, `anor/rep/mkr/pnl` («PnL»),
    barcha `anor|trade/rep/mbi/*` report designerlar, `plg/plugin_catalog`, `external_settings`.
  - Operatsion, SIBLING (menyu modelida YO'Q, eski forma ichidan): `mcg/action` (Акции→…), `marking_stocktaking_list`
    (Инвентаризации→Инвентаризация КМ).
- **Hali live tasdiqlanmagan admin formalar** (`md/*`, `ms/announcement_list`, `kauth/client_list`,
  `kauth/security_settings`, `billing/operational_dashboard` va ularning list-action ko'rinishlari) — bular ham ADMIN
  formalar, angular menyudan ochiladi; user track hujjat asosida `new_forms.md` da, testga qo'shilганда tasdiqlanadi.
  Ba'zilari faqat head KOMPANIYASIда bor bo'lishi mumkin (boshqa kompaniyada "нет доступа") — bu profil emas, kompaniya
  masalasi; forma baribir admin menyusidan ochiladi.
  - Track hali aniqlanmagan (URL only): `mfa/purchase`, `ker/setting`, `ker/head_template_list+attach`, `company_audit_info_audit`.
- **`_list`/`+add`/`+edit` bitta formaning ko'rinishlari:** `_list` va `+add` ochiladi (URL `..._list` -> `...+add`);
  `+edit`/`+copy`/`_view`/`_audit_details` yakka URL bilan ochilmaydi — record `id` kerak.
- **`+edit`/`+view`/`+copy` ni tekshirish (2026-07-07 MCP tasdiqlangan):** mos `_list` ni ochib, grid'ning BIRINCHI
  qatorini **double-click** qilinadi -> forma o'sha record id'si bilan ochiladi. Hosil bo'lgan URL patterni:
  `{base}/a2/{path}?-project_code=trade&-filial_id={filial_id}&{id_param}={id}` (`{path}` dagi `+` URLda `%2B`).
  Misol: `company_client+edit` <- `company_client_list` grid double-click -> `client_id`=grid "Client ID" ustuni.
  `{id_param}` formaga qarab farq qiladi (client_id, company_id, setting_id...). Ochilganda `document.title`
  path bo'lib qoladi (`/biruni/.../+edit`), lekin `main` da forma maydonlari (Сохранить, Название*...) bo'ladi = ochilgan.

## Real-user navigatsiya (menyu orqali — 2-etap testlar uchun)

- Eski menyu tuzilishi: **Tab** (`a.menu-link.menu-toggle`, matn = "Главное"/"Продажа"/...) → **Sub kategoriya**
  (`h3.menu-heading` matn) → **leaf** (`a.menu-link`, `href` ichida `/a2/{path}`).
- Menyu **CLICK** bilan ochiladi (hover emas): `ng-click="a.setMenuPosition($event)"`. Tab bosilganда flyout
  ochiladi/yopiladi (toggle) — holat desync bo'lmasligi uchun leaf ko'rinishini `expect(...).to_be_visible()` bilan kut.
- Leaf'ni **ends-with** selektor bilan tanla: `a.menu-link[href$="/a2/{path}"]` (`href*=` `purchase` ni `purchase_request`
  bilan ham tutadi — noto'g'ri).
- Leaf bosilganда a2 ga to'liq sahifa navigatsiya. Keyingi formaga o'tish uchun `page.go_back()` — eski dashboard
  menyusi bilan tiklanadi (2026-07-08 MCP tasdiqlangan: go_back'dan keyin tablar/leaflar qayta ishlaydi).
- **Flow helper:** `navigate_to_a2(page, tab, path)` (flows/flow_navigate.py) — tab bosadi, leaf ko'rinishini kutadi,
  bosadi, URL `/a2/{path}` ga o'tguncha va `document.title` "Smartup Online" (shell) dan forma nomiga aylanguncha kutadi.
  Sub-kategoriya (`h3.menu-heading`) ni ochish SHART EMAS — tab bosilganda flyout barcha leaflarni ko'rsatadi.
- **Ochilgani signali:** `expect(page).not_to_have_title("Smartup Online")` — dashboardlar ham (async) title'ni
  forma nomiga o'zgartiradi. `heading`/`mainLen` ga tayanma (dashboardlarda async, false-negative).
- **Menyu leaflari filial menusidan keladi** — barcha a2 leafni bitta o'qishда olish uchun angular session
  modelini (read-only) ishlat: `a.session.si.projects[0].filials[].menus[].menus[].forms[]`, `is_migrated==='Y'`
  bo'lganlari. Har `form`: `{form(path), name, is_migrated}`. Bu real menyu leaflarining AVTORITET manbai
  (URL'да ochiladigan, lekin menyuда YO'Q formalardan farqli).

## Filial switcher DOM

- Ochish: `.pt-3.px-2` (kichik viewport'да ko'rinmasligi mumkin — testда 1920x1080).
- Optionlar: `.filial-list a.ng-binding` (matn = filial nomi), `href=""` (bo'sh) — shuning uchun **role=link**,
  ya'ni `get_by_role("link", name=filial, exact=True)` ishlaydi (flow_navigate `switch_filial` shu asosда).
  `.project-list a.ng-binding` — bu proyektlar (Trade/Финансы), filiallar emas.
- `switch_filial(page, name)` (flows/flow_navigate.py) filialга o'tadi va dashboard qayta yuklanadi.
- `test_a2_admin_forms.py` code/data_store'ga bog'lanmaydi: operatsion filial sifatida angular session modelidagi
  "Администрирование" bo'lmagan birinchi filial tanlanadi va `switch_filial(page, name=<shu filial>)` qilinadi.
- URL diagnostika testlarida operatsion filial nomini aniqlash: avval `filial-pw{code}` ({code} data_store.json dan),
  topilmasa har qanday `filial-pw*`, topilmasa "Администрирование" bo'lmagan birinchi filial.
- **head profilida `filial-pw*` YO'Q** (ular oddiy kompaniyalarda autotest yaratadi) -> 3-qadam ishlaydi va
  "Администрирование" bo'lmagan BIRINCHI filial olinadi (head'da odatda "Test org to delete"). Bu TASODIFIY tanlov,
  lekin operatsion formalar (masalan operational_dashboard) istalgan operatsion filialda ochilaveradi, shuning uchun
  shunday qoldirilgan (2026-07-07 user qarori). Aniq/barqaror filial kerak bo'lsa keyin o'zgartiriladi.

## Test

- `tests/smoke/test_life_cycle/test_a2_new_forms.py` — 1-etap: har a2 formani **URL orqali** ochib tekshiradi
  (title resolve / 404 / "нет доступа" / error / id-kerak), har forma `allure.step`, muammoda screenshot, to'xtamaydi.
- **Profil-aware + mode:** `@pytest.mark.parametrize("profile_key", ["admin","head"])`. `A2_FORMS` — dict ro'yxati:
  `{path, title, profile(admin|head), filial(operational|admin), mode(direct|via_list|skip), parent}`.
  - `direct` — URL bilan ochiladi; ochilmasa fail.
  - `via_list` — `parent` `_list` ochiladi, `main .smt-data-row` birinchi qatori double-click -> forma id bilan
    ochiladi (edit/view/copy/details); ochilmasa fail, list bo'sh bo'lsa "no_rows" (fail emas). Bir parent bir marta (cache).
  - `skip` — a2 list yo'q (ker/setting+edit), tekshirilmaydi.
  head profil (`admin@head`) yo'q serverda avtomatik `pytest.skip`.
- Ishga tushirish: `.env` joriy serverга qaratilgan bo'lsa oddiy `pytest tests/smoke/test_life_cycle/test_a2_new_forms.py`;
  boshqa serverга `.env` ni vaqtincha chetlab `--url/--company-code/--company-password` bilan.

- **2-etap (test_a2_admin_forms.py) — real menyu orqali (2026-07-08, 24/24 passed):**
  Har a2 formani ESKI menyudan `navigate_to_a2(page, tab, path)` bilan ochadi (real user yo'li), xatoda to'xtamaydi,
  filial bo'yicha guruhlangan hisobot beradi. **Barcha angular-menyu a2 formalar ADMIN** — alohida head test YO'Q;
  hali live tasdiqlanmagan admin formalar (`md/*`, `announcement`, `client_list`, `security_settings`,
  `operational_dashboard`, ...) shu SHU faylga qo'shib boriladi.
  - **Menyudan ochiladigan admin formalar (red_test, 2026-07-08 live tasdiqlangan):**
    - birinchi "Администрирование" bo'lmagan operatsion filialda 19 ta: `external_settings`, `visit_list`, `user_locations`, `user_tracking`,
      `commercial_dashboard`, `rep/mbi/tvt/visit`, `logistics_list`, `mkw/{movement,purchase_request,purchase,input,writeoff}`,
      `mfm/{movement,movement_request}`, `mkcs/operation`, `anor/rep/mkr/pnl` (leaf matni "PnL", Финансы),
      `tmcg/shelf_share`, `mqpf/request`, `plugin_catalog`.
    - "Администрирование" filialida: `biruni/kauth/company_client_list` + undan `+add` (list → «Создать») va
      `+edit` (qator bosilsa «Изменить» tugmasi chiqadi → ochiladi). Ochilish signali: main'da «Сохранить» tugmasi.
      `+add`/`+edit` menyu leafi EMAS — list ichidan tugma bilan ochiladi (dblclick shart emas, bir marta qator bosiladi).
  - **"Sibling" orqali ochiladigan a2 (menyu leafi EMAS, eski forma ICHIDAN — MUHIM):** ba'zi a2 konstruktorlar
    alohida menyu leafiga ega emas va **angular menyu modelida ham ko'rinmaydi** — eski forma menyudan ochilib, uning
    subheader'idagi sub-link (`a[ng-click*="openSibling"]`) bosiladi → `/a2/{path}` ga o'tadi. Shuning uchun forma
    "menyuda yo'q" degan xulosani FAQAT menyu modelini skanlab chiqarma — eski/qardosh formani OCHIB, subheader
    sub-linklarini ham tekshir. Tasdiqlangan (2026-07-08):
    - `anor/rep/mbi/mcg/action` = Справочники → «Акции» (eski `anor/mcg/action_list`) → sub-link «Конструктор отчетов по акциям».
    - `anor/mkw/marking_stocktaking/marking_stocktaking_list` = Склад → Документы → «Инвентаризации» (eski
      `anor/mkw/stocktaking/stocktaking_list`) → sub-link «Инвентаризация КМ».
    Test'da `_open_a2_via_sibling(...)` + `SIBLING_FORMS` ro'yxati shu patternni bajaradi.
  - **new_forms.md da bor, red_test menyusida hali topilmadi** (URL test qamraydi):
    `anor/rep/mbi/mfa/purchase` (user bermagan — keyin). Boshqa company/serverda bo'lishi mumkin.
  - Hali URL-only (real user yo'li aniqlanmagan): `ker/setting+add/+edit`, `ker/head_template_list+attach`,
    `company_audit_info_audit(+details)` — kompaniya «История изменений» tugmasidan ochilishi mumkin (tekshirilmagan).
  - **Standalone run:** `test_a2_admin_forms.py` uchun `code` fixture kerak emas; `.env` faqat login/server
    credentiallariga (`COMPANY_URL`, `COMPANY_CODE`, `COMPANY_PASSWORD`) ta'sir qiladi.

## Diagnostika natijasi (2026-07-07, app3.greenwhite.uz/xtrade — 2 passed, 0 muammo)

- **ADMIN profil (admin@red_test):** 30/30 muvaffaqiyatli (28 direct OCHILDI + 1 via_list edit OCHILDI + 1 skip[ker/setting+edit]).
- **HEAD profil (admin@head):** 23/23 muvaffaqiyatli (14 direct OCHILDI + 8 via_list edit OCHILDI, jumladan
  Компании, Логи, Настройки безопасности, Объявления, Операционный дашборд + ularning +edit/+view formalari).
- **Hech bir a2 forma buzuq emas.** +edit/+view/+copy/_details formalar mos `_list` birinchi qatoridan
  (double-click) ochiladi — hammasi OCHILDI.
- **TUZATISH (2026-07-08 user qoidasi):** "head-only" deb belgilangan formalar aslida ham ADMIN formalar — angular
  menyu orqali ochiladi. Yuqoridagi URL-diagnostikada admin@head da ochilishi shundan: forma faqat head KOMPANIYASIда
  mavjud bo'lgan (profil emas, kompaniya masalasi). Menyu-based testда bularning hammasi admin sifatida qamraladi.
- "Ochilgan" signali — `document.title` forma nomiga (yoki `+edit` da path'ga) aylanishi + `main` da kontent.
  `mainLen` ni yakka ochilish mezoni sifatida ishlatma — async/datasiz formalarda false-negative beradi.
