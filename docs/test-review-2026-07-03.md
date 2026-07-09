# Smoke Test To'plami Tahlili — Kamchiliklar va Yaxshilanishlar

**Sana:** 2026-07-03
**Qamrov:** `tests/smoke/` — 61 fayl, ~6300 qator (conftest, runnerlar, setup, A/B/C/report grouplar, life_cycle, flows)
**Usul:** 4 yo'nalishda parallel tahlil (infrastruktura, setup testlar, group testlar, flows), kritik topilmalar qo'lda tasdiqlangan.

---

## Umumiy Xulosa

| Soha | Baho | Izoh |
|---|---|---|
| Infrastruktura (conftest, runnerlar) | **Yaxshi** | Puxta dizayn, lekin 2 ta muhim muammo bor |
| Setup testlar | **Yaxshi** | 8 fayl yangi standartda, 4 ta eski fayl orqada |
| Group testlar (A/B/C/report, life_cycle) | **O'rta** | A/B professional, C/report/life_cycle konvensiyadan chetda |
| Flows qatlami | **O'rta (yaxshiga yaqin)** | Kutish strategiyasi zo'r, lekin tozalash kerak |

Loyihaning kuchli tomoni — infratuzilma va yangi avlod testlarning sifati. Asosiy muammo — **konvensiya bir xil qo'llanmagani**: bitta `run_ + test_` standarti 4 xil talqin qilingan (A-group to'liq, B-group maxsus layout, C/report'da wrapper umuman yo'q, life_cycle'da wrapper bor lekin auth'siz).

---

## 1. Kritik / Yuqori Jiddiylikdagi Topilmalar

### 1.1. Setup chain 14–21 qadamlari kommentga olingan (commit qilinmagan lokal diff)
- **Joyi:** `tests/smoke/test_setup/test_setup_runner.py:174-237`
- **Muammo:** Price Type, Payment Type, Sector, Product, Natural Person, Room Attachment, Init Balance, Balance qadamlari lokal diff'da kommentga olingan (HEAD'da aktiv). Full run bu entitylarni yaratmaydi, holbuki A/B/C grouplar `product-pw{code}`, price type, balance'ga bog'liq — **full run grouplarda yiqiladi**.
- **Yechim:** Debug tugagan bo'lsa kommentlarni tiklash (`git checkout -- tests/smoke/test_setup/test_setup_runner.py` yoki qo'lda uncomment). Ataylab bo'lsa — sababini komment bilan yozish va mos standalone testlarni ham skip qilish.
- ⚠️ *Bu sizning joriy lokal o'zgarishingiz bo'lishi mumkin — commit'dan oldin albatta tekshiring.*

### 1.2. To'rt setup testda `test_` wrapper authorization qilmaydi — standalone run buziladi
- **Joyi:** `test_payment_type.py:36`, `test_sector.py:35`, `test_price_type.py:42`, `test_product.py:44`
- **Muammo:** Konvensiya bo'yicha wrapper = auth + `run_` chaqiruv. Bu fayllarda auth yo'q — yakka/debug run birinchi `navigate_to`da yiqiladi.
- **Yechim:** Har wrapperga `authorization(page, who='admin')` (+ kerak bo'lsa `switch_filial`) qo'shish — `test_robot.py:48-51` namunasidek.

### 1.3. life_cycle testlari ham yakka run'da ishlamaydi
- **Joyi:** `test_life_cycle/test_order.py:141-143` (`test_order_add_column_order_id`), `test_life_cycle/balance.py:19-21` (`test_balance`)
- **Muammo:** Wrapper na login qiladi, na kerakli sahifaga navigate qiladi.
- **Yechim:** `authorization(page, who="user", code=code)` + defensive navigate qo'shish.

### 1.4. `--maxfail=3` group-mustaqillik dizayniga zid
- **Joyi:** `pytest.ini:6`
- **Muammo:** Full run'da 3 ta group yiqilsa sessiya to'xtaydi va `independent=True` bo'lgan Report group umuman ishlamaydi — "bitta group yiqilsa boshqalari davom etadi" qoidasiga zid.
- **Yechim:** `--maxfail`ni olib tashlash — skip mexanizmi (`_USER_SETUP_FAILED`/`_FAILED_SMOKE_GROUPS`) kaskadni allaqachon boshqaradi.

### 1.5. `fill_nps_survey` xatoni yutadi va modal yo'q bo'lganda 20s jarima
- **Joyi:** `tests/smoke/flows/flow_modal.py:8-14`
- **Muammo:** `except Exception` modal topilgandan keyingi real xatolarni ham yutadi; modal yo'q holatda har chaqiriqda 20 soniya bekor kutiladi.
- **Yechim:** Modal borligini qisqa timeout bilan aniqlash, ichki harakatlarni try tashqarisida bajarish.

### 1.6. `flow_order_list_grid_setting` — universal API, lekin `#deal_id` hardcode
- **Joyi:** `tests/smoke/flows/flow_order/flow_order_list.py:82-84`
- **Muammo:** Parametrlar universal ko'rinadi, lekin faqat bitta ustun uchun ishlaydi. Typo ham bor: `colum_name`.
- **Yechim:** Ustun ID'sini parametr qilish yoki `column_name` matni orqali dinamik topish.

### 1.7. `test_product.py` da o'ta mo'rt locatorlar
- **Joyi:** `tests/smoke/test_setup/test_product.py:19-21`
- **Muammo:** Generatsiya qilingan ID (`#anor66-input-text-measure_short_name`) va layout-klass zanjiri (`.col-sm-12.mb-4 > .form-control`) — UI ozgina o'zgarsa sinadi.
- **Yechim:** `BasePage.b_input(...)` / `input(label=...)` ga o'tkazish.

---

## 2. Struktura va Konvensiya Muammolari (O'rta)

### 2.1. C-group va report-group leaf fayllarida `test_` wrapper umuman yo'q
- **Joyi:** `test_C_grup/test_action.py`, `test_report_grup/test_cislink.py`, `test_saleswork.py`, `test_optimum.py`, `test_spot.py`, `test_integration_two.py`, `test_integration_three.py` — bironta ham `def test_` yo'q (tasdiqlangan).
- **Yechim:** Har leaf faylga B-group uslubidagi bitta `test_` entry qo'shish (auth + `run_*`), `pytest.mark.smoke_group` markerini ham qo'shish.

### 2.2. Docstring testcase yo'q yoki mos emas
- `run_company` — 270 qatorlik eng murakkab funksiya hujjatsiz (`test_company.py:55`)
- `run_payment_type`, `run_sector`, `run_product`, `run_price_type_uzb` — docstring umuman yo'q
- life_cycle: `run_order_basic`, `run_order_add_column_order_id`, `run_init_balance`, `run_balance` — docstring yo'q, step nomlari raqamlanmagan
- `test_contract.py:27-36` — docstring 7 qadam, kodda 9 step; "Dоговоры" typo (lotin D + kirill)
- **Yechim:** Har `run_`ga allure steplarga mos raqamlangan qadamli docstring.

### 2.3. Xato yutuvchi try/except bloklari
- `test_company.py:312-319` — saqlash xatosi jim yutiladi (keyingi testlar tushunarsiz joyda yiqiladi)
- `test_b_04_invoice_report_template.py:285-288, 304-307` — `confirm_biruni()` atrofida izohsiz `try/except: pass`
- `order_helpers.py:298-351` — 4 qatlamli nested try/except fallback zanjiri
- **Yechim:** "Optional UI" holatlari uchun yagona `_confirm_if_open` / `*_if_open` helper uslubi; boshqa exceptionlarni yutmaslik.

### 2.4. Waitsiz `count()` / `is_visible()` branching — flaky xavf (13+ joy)
- `test_user.py:13-16` (`_set_permission_page_size_1000` jim no-op bo'lishi mumkin)
- `test_license.py:133` (idempotentlik tekshiruvi race'ga moyil)
- `flow_order_list.py:70`, `test_integration_two.py:89-92`, `test_company.py` (bir necha joy)
- **Yechim:** Conditional UI uchun yagona pattern: qisqa timeout'li `wait_for` + hujjatlangan fallback.

### 2.5. `wait_for_timeout` polling sikli (loyihada taqiqlangan)
- **Joyi:** `test_b_04_invoice_report_template.py:150-158` — OnlyOffice iframe kutish `time.monotonic` + `wait_for_timeout(500)` bilan.
- **Yechim:** `wait_for_event("frameattached")` yoki `page.wait_for_function` asosidagi kutish.

### 2.6. Fixture bosqichida yiqilganda screenshot yo'q
- **Joyi:** `tests/smoke/conftest.py:626`
- **Muammo:** Attach hook faqat `report.when == "call"`da ishlaydi — login/fixture setupda yiqilsa Allure'da screenshot bo'lmaydi.
- **Yechim:** Shartni `report.when in ("setup", "call")`ga kengaytirish.

---

## 3. Dublikatsiya — Flow/Helperga Chiqarilishi Kerak

| Dublikat blok | Joylari | Yechim |
|---|---|---|
| Order cancel sikli ("Отменен") | `test_A_grup/test_order.py:57-65, 169-177` + `order_helpers.py:383-394` | `flows/flow_order/`da `flow_cancel_client_orders(page, client)` |
| Session-token URL + `page.goto` | report-group **6 faylda** so'zma-so'z | `report_helpers.open_integration_report(page, slug)` |
| Order-id XPath (`//t[...ИД заказа...]`) | `test_A_grup/test_order.py:131, 242` | Mavjud `flow_order_view(get_value=["ИД заказа"])` ishlatish |
| View-assert bloki (6 ta `to_contain_text`) | `test_A_grup/test_order.py:116-128, 227-239` | `flow_order_list(find_row=..., view=True)` + umumiy assert helper |
| Order save snippeti | `test_A_grup/test_order.py:109-113` + `order_helpers.py:290-295` | `flow_order_final_page(save=True)` dan foydalanish |
| "Доступные → checkall → Прикрепить" bloki ×3 | `test_room.py:69-97` | Lokal `_attach_all(page, link, grid, confirm)` helper |
| `progress_step` boilerplate (runner'da 14+ marta) | barcha runner fayllar | `functools.partial` yoki `(test_id, title, callable)` ro'yxat + loop |
| `head_admin_email/password` | `test_company.py:37-48` = `flow_authorization.py:78,86` | Flow'dan import qilish |
| data_store.json o'qish logikasi ×3 | `flow_authorization.py:39-46,106-117` + `conftest.py:283-297` | Bitta `utils/data_store.py` |
| Multiselect qo'lda takror | `test_price_type.py:24-26` | `BasePage.multiselect` (robot testidagidek) |

---

## 4. Boshqa Topilmalar (Past jiddiylik, tanlab)

- **O'lik kod:** `flow_form.py:15, 24, 50` — `fill_textarea`, `select_b_input_by_search`, `select_tashkent_region` hech qayerda chaqirilmaydi (grep tasdiqlagan); `flow_navigate.py:69` kommentga olingan qator; `test_robot.py:2` ishlatilmagan import.
- **Docstring/kod zidligi:** `flow_modal.py:18-27` — `dialog_status` docstring va return semantikasi teskari.
- **Nomlash konvensiyasi zid:** new-flow SKILL "funksiya nomi `flow_` prefikssiz" deydi, lekin barcha yangi flowlar prefiksli; `from ...flow_order_list import flow_order_list` — modul/funksiya soyalanishi. Yagona qaror kerak (SKILL'ni yangilash yoki nomlarni o'zgartirish).
- **Timeout magic numberlar:** 120_000 / 20_000 / 5_000 / 2_000 flowlarda lokal — markaziy konstantaga chiqarish kerak (`flow_navigate.py:8,23,52`, `flow_modal.py:8,18`, `flow_form.py:56,66`).
- **Hardcoded biznes-data:** `test_license.py:40-41` — `"AUTOTEST GWS"` va kontrakt nomi serverdagi holatga bog'langan; `flow_contract_add.py:35-37` — klient/valyuta flow ichiga singdirilgan, `amount`/`amount_text` juftligi qo'lda sinxronlanadi.
- **Miqdorga bog'langan confirm matnlari:** `"Прикрепить ... 4?"` (`test_payment_type.py:22`, `test_room.py:76,86,96`) — server default o'zgarsa sinadi.
- **`--new-code` help matni noto'g'ri:** "4 xonali" deydi, aslida 6 xonali (`conftest.py:162`).
- **`.env` bor bo'lsa CLI flaglar jim e'tiborsiz qoladi** (`conftest.py:66-90`) — ogohlantirish print qilish kerak; CLAUDE.md "".env ishlatilmaydi"" jumlasi kod bilan zid — hujjatni moslash.
- **`page.evaluate` bilan switch bosish:** `test_C_grup/test_action.py:148-153` — form action uchun evaluate qoidaga zid.
- **C-02 flaky xavf:** `test_action.py:170` — client bo'yicha `.first` row boshqa group qoldirgan orderni tanlashi mumkin; aksiya nomi save_data orqali emas, f-string orqali bog'langan.
- **Nisbiy fayl yo'li:** `test_b_04_invoice_report_template.py:207` — `Path("data/...")` cwd'ga bog'liq.
- **`_install_report_print_guard` to'planishi:** `order_helpers.py:146-167` — har optionda `add_init_script` qayta qo'shiladi (17 marta).
- **Legacy kalit fallbacklar:** `test_A_grup/test_order.py:53, 161-162` — prefiksiz `contract_name` o'qish "faqat o'z prefiksi" qoidasiga zid.
- **`logout` faqat admin sessiyada ishlaydi:** `flow_authorization.py:124` — "Admin" matni hardcode.
- **`save_data=None` bilan ikki uslub:** guard qilingan (`test_price_type.py:36`) vs unconditional (`test_filial.py:64-67`, `test_legal_person.py:49-50`) — bitta konvensiya tanlash.
- **Yakka test uchun har safar yangi Playwright launch:** `conftest.py:413-419` — `page` fixture'ni `session_browser`ga ulash tezlashtiradi.

---

## 5. Yaxshi Tomonlar (saqlab qolish kerak)

- **Anti-patternlar deyarli yo'q:** `time.sleep` — 0 ta, `wait_for_timeout` — faqat 1 joyda (b_04 polling); URL faqat `--url`/env orqali; hardcode credential yo'q.
- **Failure diagnostikasi kuchli:** screenshot + URL + title + data_store JSON attach, har context uchun trace.zip, maskalanagan parollar.
- **Skip/dependency mexanizmi:** user_setup yiqilsa hamma group skip, group ichida faqat shu group skip, `independent=True` davom etadi — SKILL qoidalariga to'liq mos.
- **data_store puxta:** atomic yozish, buzilgan JSON uchun aniq xato, `require_data` darhol tushunarli xato beradi.
- **Yangi avlod testlarda locator madaniyati yuqori:** `BasePage.input/b_input/multiselect/grid_row`, diagnostikali `expect_page`.
- **Idempotentlik:** company/litsenziya mavjud bo'lsa qayta yaratmaydi, consignment setting idempotent yoqiladi.
- **"Nega bunday" kommentlari** tricky joylarda saqlangan — institutsional bilim yo'qolmaydi.

---

## 6. Tavsiya Etilgan Ish Rejasi (prioritet tartibida)

1. **Darhol:** `test_setup_runner.py` dagi kommentga olingan 14–21 qadamlarni hal qilish (tiklash yoki sabab yozish) — full run buzilgan holatda.
2. **Darhol:** `pytest.ini` dan `--maxfail=3` ni olib tashlash.
3. **1-iteratsiya (standalone run tiklash):** 4 setup test + 2 life_cycle test wrapperlariga auth qo'shish; C/report leaf fayllarga `test_` entry qo'shish.
4. **2-iteratsiya (flaky himoya):** `flow_modal.fill_nps_survey` refactor; waitsiz `count()/is_visible()` branchlar uchun yagona pattern; b_04 polling'ni event-based kutishga o'tkazish; conftest attach hook'ni `setup` bosqichiga kengaytirish.
5. **3-iteratsiya (dublikatsiya):** 3-bo'limdagi jadval bo'yicha flow/helperlarga chiqarish (eng katta ROI — report-group 6×goto bloki va order cancel sikli).
6. **4-iteratsiya (sifat):** "eski to'rtlik" setup testlarni (`payment_type`, `sector`, `price_type`, `product`) yangi standartga tortish; docstringlarni to'ldirish; o'lik kodni o'chirish; timeout konstantalarini markazlashtirish; `flow_` nomlash konvensiyasi bo'yicha qaror.

---

*Hisobot 4 parallel tahlil agenti natijalarini jamlagan; kritik topilmalar (1.1, 1.2, 1.4, 2.1) qo'lda `git diff`/`grep` bilan tasdiqlangan.*
