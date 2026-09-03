# Mobile Visit — Bosqichma-bosqich Implementatsiya Plani

## Maqsad

Setup testlari tugagandan keyin mobil API orqali vizit yaratish va yaratilgan
vizitni webdagi `Продажа → Визиты → Визиты` formasidan topib tekshirish.
Minimal vizit barqaror ishlagach, bitta mahsulotli order bilan vizit yuborish va
uni ham webdan tekshirish.

## Status qoidasi

- `TODO` — hali boshlanmagan.
- `PROGRESS` — hozir bajarilayotgan faza.
- `DONE` — acceptance criteria bajarilgan va dalil bilan tasdiqlangan.
- Bir vaqtda faqat bitta faza `PROGRESS` bo'ladi.
- Faza tugaganda uning statusi `DONE`, navbatdagi faza `PROGRESS` qilinadi.
- Bloklovchi noma'lum qiymat yoki xato fazaning `Izoh / bloklovchi` qismiga
  yoziladi; taxmin bilan keyingi fazaga o'tilmaydi.
- Test, smoke yoki pytest faqat foydalanuvchi aynan `run qil` deganda ishga
  tushiriladi.

## Tasdiqlangan manbalar

- `authentication.md` — mobile login, session va business request headerlari.
- `tvt_save_person_visit.md` — `sync:sync` transporti va visit payload kontrakti.
- `test-results/data/data_store.json` — setup yaratgan joriy test ma'lumotlari.
- `tests/smoke/test_setup/test_0_setup_runner.py` — setup zanjiri.
- `tests/smoke/conftest.py` — strict `load_data` va `save_data` fixturelari.
- `tests/smoke/flows/flow_navigate.py` — A2 forma navigatsiyasi.
- `utils/angular_base_page.py` — A2 sahifa helperlari.

## Tasdiqlangan ID mapping

| Visit/API maydoni | `data_store.json` kaliti | Holat |
|---|---|---|
| `filial_id` | `filial_id` | tayyor |
| `room_id` | `room_id` | tayyor |
| `robot_id` | `robot_id` | tayyor |
| visit `person_id` | `client_person_id` | tayyor |
| order `sales_manager_id` | `user_person_id` | tayyor |
| order `currency_id` | `currency_id_uzb` | tayyor |
| `payment_type_id` | `payment_type_id` | tayyor |
| `price_type_id` | `price_type_id_uzb` | tayyor |
| `warehouse_id` | `warehouse_id` | tayyor |
| `product_id` | `product_id` | tayyor |

Muhim chegaralar:

- Client uchun `client_person_id` ishlatiladi.
- Savdo menejeri uchun `user_person_id` ishlatiladi; `user_id` emas.
- Minimal visit uchun boshqa ID kerak emas.
- Bir mahsulotli order uchun `contract_id` majburiy emas va dastlab `null`.
- `vat_percent` ID emas. Order fazasidan oldin uning real qiymati
  tasdiqlanishi kerak.

---

## Faza 0 — Setup ma'lumotlarini tayyorlash

**Status: DONE**

### Bajarilgan

- [x] Filial ID saqlandi.
- [x] Room ID saqlandi.
- [x] Robot ID saqlandi.
- [x] Userga bog'langan person ID `user_person_id` sifatida saqlandi.
- [x] Client person ID `client_person_id` sifatida saqlandi.
- [x] Currency ID saqlandi.
- [x] Payment type ID saqlandi.
- [x] UZS price type ID saqlandi.
- [x] Product ID saqlandi.
- [x] Warehouse ID alohida setup test orqali saqlandi.
- [x] Setup run muvaffaqiyatli o'tgani va IDlar `data_store.json`da borligi
  foydalanuvchi tomonidan tasdiqlandi.

### Acceptance criteria

- Minimal visit va bir mahsulotli order uchun zarur ID keylari mavjud.
- `client_person_id`, `user_person_id` va `user_id` semantikasi
  aralashtirilmagan.

---

## Faza 1 — Real Visit list kontraktini aniqlash

**Status: DONE**

### Bajarilgan

- [x] User sessiyasida setup yaratgan `filial-pw{code}`ga o'tildi.
- [x] A2 `trade/tvt/visit_list` formasi real UI orqali ochildi.
- [x] URL `*/a2/trade/tvt/visit_list` va title `Визиты` tasdiqlandi.
- [x] Default grid ustunlari va bo'sh `Нет результатов` holati aniqlandi.
- [x] `ИД` `Настройки таблицы` dialogida mavjudligi tasdiqlandi.
- [x] `ИД` gridda `data-smt-col-key="visit_id"` bo'lib chiqishi tasdiqlandi.
- [x] `Настройки поиска` dialogida `ИД` va visit note yo'qligi tasdiqlandi.
- [x] Visit list uchun `grid_setting(..., field_name="ИД")` ishlatilishi,
  `search_name="ИД"` berilmasligi belgilandi.
- [x] Tasdiqlangan faktlar `visit-list` dossieriga yozildi.

### Acceptance criteria

- Visit listga o'tish yo'li va page-ready tekshiruvi aniq.
- API visit paydo bo'lgach tekshiriladigan list kontrakti tayyor.
- Legacy `BasePage` va A2 `AngularBasePage` locatorlari aralashtirilmagan.

### Izoh / bloklovchi

- Row action, ID/global search va view locatorlari real visit mavjud bo'lgach
  Faza 5da aniqlanadi; bo'sh listdan taxmin qilinmaydi.

---

## Faza 2 — Mobile authentication client

**Status: DONE**

### Bajarilgan

- [x] Mobile API kodi `tests/smoke/clients/mobile_client.py`ga joylashtirildi.
- [x] Server URL mavjud config/environmentdan olinadi; hardcode qilinmaydi.
- [x] Login mavjud `code` va company konfiguratsiyasidan hosil qilinadi.
- [x] Parol mavjud environment/config helperidan olinadi; faylga yozilmaydi.
- [x] `password_hash` lowercase SHA-1 bilan hisoblanadi.
- [x] `account_code` `login + "#" + server_url_without_trailing_slash`
  qiymatining lowercase SHA-256 hashi sifatida hisoblash.
- [x] Stabil `device_code` caller tomonidan `data_store.json`da saqlanib,
  clientga berilishi belgilandi; client har requestda UUID yaratmaydi.
- [x] `POST /b/biruni/s:log_in_device` clienti yozildi.
- [x] `GET /b/biruni/m:session_info_mobile` orqali `trade` loyihasi va target
  filial mavjudligini tekshirish.
- [x] Business requestlar uchun `token`, `project_code=trade`, `filial_id` va
  kerak bo'lsa `timezone_code` headerlarini markazlashtirish.
- [x] `401`/unauthenticated holatida bir marta qayta login va retry yozildi.
- [x] `429` holatida darhol qayta urinish to'xtatilib, `Retry-After` qiymatli
  aniq error yozildi.
- [x] Client token, password, hash va auth bodyni loglamaydi.
- [x] Module import va `git diff --check` statik tekshiruvdan o'tdi.

### Runtime verification

- [x] Real login va target filial `session_info_mobile` javobida tasdiqlandi.

### Acceptance criteria

- Login/session kontrakti kodda implementatsiya qilingan; real server natijasi
  Faza 4 runida tasdiqlanadi.
- Token `Bearer` prefiksisiz yuboriladi.
- Secretlar test artifactlariga chiqmaydi.
- Har visit uchun qayta login qilinmaydi.

---

## Faza 3 — Minimal visit payload va sync client

**Status: DONE**

### Bajarilgan

- [x] `data_store.json`dan majburiy keylar default fail-fast `load_data`
  orqali olinadi: `filial_id`, `room_id`, `robot_id`, `client_person_id`;
  optional `mobile_device_code` uchun `allow_missing=True` ishlatiladi.
- [x] Har bir ID requestdan oldin musbat integer sifatida tekshiriladi.
- [x] Process ichida takrorlanmaydigan 13 xonali epoch-millisecond `entry_id`
  generatori yozildi.
- [x] `mobile_visit_id == entry_id` invarianti saqlandi.
- [x] `begun_on`, `ended_on` va `spent_time` o'zaro mos hosil qilinadi.
- [x] Har run uchun noyob `visit_note` yaratiladi.
- [x] Minimal root payload hujjat kontraktiga mos yig'ildi.
- [x] Ishlatilmaydigan barcha arraylar bo'sh `[]` bilan yuboriladi.
- [x] `person_closed="N"`, `has_postponed_order="N"`, `orders=[]` beriladi.
- [x] `POST /b/biruni/mt/sync:sync` requesti `Content-Type: text/plain`
  bilan yuborish.
- [x] Bir requestda bitta entry yuboriladi.
- [x] Plain-text javobdagi `S<entry_id>` va `E<entry_id>` formatlari parse
  qilish.
- [x] `E` javobidagi server xabari aniq test xatosiga aylantiriladi.
- [x] Successdan keyin `mobile_visit_id` va `mobile_visit_note`ni
  `data_store.json`ga saqlash.
- [x] Builder va response parser network ishlatmasdan sintetik kontrakt
  tekshiruvidan o'tdi.

### Acceptance criteria

- Server aynan yuborilgan `entry_id` uchun `S` javob qaytaradi.
- `mobile_visit_id` va correlation note web verification uchun saqlanadi.
- Request kontraktida yetishmayotgan array yoki noto'g'ri sana formati yo'q.

---

## Faza 4 — Minimal mobile visit API testi

**Status: DONE**

### Bajarilgan

- [x] `run_mobile_visit(...)` va standalone `test_mobile_visit(...)` yozildi.
- [x] Test `tests/smoke/test_groups/test_visit_grup/` ichiga joylashtirildi.
- [x] Dedicated `test_0_visit_runner.py` skeleti yozildi.
- [x] Setup runner biznes visit qadamlari bilan aralashtirilmadi.
- [x] Allure epic/feature/story va raqamlangan docstring qadamlar yozildi.
- [x] Auth, session validation va payload yuborish alohida Allure steplarga
  ajratildi.
- [x] Raw token yoki auth request Allure attachment qilinmaydi.

### Runtime natija

- [x] Dedicated Visit runner real serverda ishga tushirildi.
- [x] API-only bosqich va yakuniy API + web oqimi `1 passed` natija berdi.
- [x] `S<entry_id>` acceptance va correlation keylari `data_store.json`da
  tasdiqlandi.

### Acceptance criteria

- Test setup baselinega tayanadi, sibling biznes test yaratgan state'ga emas.
- API acceptance faqat HTTP status bilan emas, `S<entry_id>` bilan
  tekshiriladi.
- Visit correlation qiymatlari keyingi web testga saqlanadi.

---

## Faza 5 — Minimal visitni webdan tekshirish

**Status: DONE**

### Bajarilgan

- [x] Oddiy user bilan web authorization qilindi.
- [x] Setup yaratgan filial `filial_name` orqali tanlandi.
- [x] `navigate_to_a2(..., path="trade/tvt/visit_list")` orqali visit list
  ochish.
- [x] Client global searchidan keyin unique `mobile_visit_note` bilan aynan
  API yaratgan qator topildi.
- [x] Grid server `visit_id` qiymati o'qilib `data_store.json`ga saqlandi.
- [x] Qator tanlanib, page-level `Просмотреть` action orqali view ochildi.
- [x] Visit ID, status, client, room, user va visit vaqti tekshirildi.
- [x] `Дополнительная информация`da boshlanish/tugash vaqtlari ±5 soniya
  tolerantlik bilan tekshirildi.
- [x] `Примечания` tabida unique note va user tekshirildi.
- [x] Tekshiruvlarda `AngularBasePage` public helperlari ishlatildi.
- [x] A2 headerdagi texnik ustun sababli `grid_setting()` indeksi
  `grid_cell()` bilan siljishi trace orqali aniqlandi va helper faqat
  `data-smt-col-key` headerlarini sanaydigan qilib tuzatildi.
- [x] Yakuniy dedicated runner natijasi: `1 passed in 30.05s`.

### Acceptance criteria

- API orqali yuborilgan vizit web listda topiladi.
- View formadagi asosiy qiymatlar yuborilgan payload bilan mos.
- Qidiruv boshqa run yaratgan vizitni tasodifan tanlamaydi.

---

## Faza 6 — Bir mahsulotli order payloadi

**Status: DONE**

### Bajarilgan

- [x] Setup filial testi `НДС`ni yoqmasligi code-confirmed bo'lgani uchun
  normal product line `vat_percent=0` qilib belgilandi.
- [x] `stocks=[]` holatida `deal_recom_calculation_method=""` target serverda
  minimal visit runi bilan qabul qilingani tasdiqlandi.
- [x] Order `person_id = client_person_id` mappingi qo'llandi.
- [x] `sales_manager_id = user_person_id` mappingi qo'llandi.
- [x] `currency_id_uzb`, `payment_type_id`, `price_type_id_uzb`, `warehouse_id` va
  `product_id`ni default fail-fast `load_data` bilan olish.
- [x] `source_table="MVTM_VISIT_HEADERS"` va `source_id=mobile_visit_id`
  invariantini saqlash.
- [x] `contract_id=null`, `subfilial_id=null` va optional maydonlar hujjat
  kontraktiga mos berish.
- [x] Bitta goods item yozildi: `inventory_kind="G"`, `quantity="1"`,
  setupdagi tasdiqlangan price va real VAT qiymati.
- [x] Consignment va ishlatilmaydigan nested arraylar bo'sh yuborildi.
- [x] Successdan keyin orderli visit uchun alohida `mobile_visit_id` va note
  saqlash; minimal visit qiymatlarini ustidan yozmaslik.
- [x] `build_order_visit(...)`, `save_order_visit(...)` va mustaqil
  `test_02_mobile_visit_with_order.py` testcase'i yozildi.
- [x] Dedicated Visit runnerga ikkinchi wrapper qo'shildi.
- [x] Python syntax va `git diff --check` statik tekshiruvi o'tdi.

### Runtime natija

- [x] Orderli visit testcase'i real
  serverda bajarish.
- [x] `S<entry_id>` acceptance va alohida `mobile_order_*` correlation
  keylarini `data_store.json`da tasdiqlash.
- [x] Dastlabki run `currency_id` USD, `price_type_id_uzb` esa UZS bo'lgani
  uchun `A02-16-011` bilan rad etildi; setup UZS IDni alohida
  `currency_id_uzb` sifatida saqlaydigan qilib tuzatildi.
- [x] Fresh setupdan keyingi orderli API + web leaf run `1 passed in 53.07s`.

### Acceptance criteria

- Orderli visit `S<entry_id>` bilan qabul qilinadi.
- Payloadda client person va sales manager person IDlari to'g'ri ajratilgan.
- VAT, status yoki filial settingi taxmin bilan kiritilmagan.

---

## Faza 7 — Orderli visitni webdan tekshirish

**Status: DONE**

### Bajarilgan

- [x] Orderli visitni o'zining alohida ID/note qiymati bilan topish.
- [x] Visit viewda client, sales manager va asosiy visit maydonlarini
  tekshirish.
- [x] Visit viewdagi `Заказы` bo'limida linked order mavjudligini tekshirish.
- [x] Linked gridda product, price type, quantity, price, VAT, room, client va
  status qiymatlarini tekshirish.
- [x] Warehouse joriy linked grid/order viewda render qilinmasligi live DOMda
  tasdiqlandi; uning IDsi payload invariantida tekshirildi.
- [x] `Действия` orqali A2 order viewga transition va page assertni
  alohida Allure stepga ajratish.
- [x] Order viewda server order ID, sales manager, client, room, payment type,
  currency, status va total summa tekshirildi.

### Acceptance criteria

- Mobile API yaratgan visit va order web UI orqali ko'rinadi.
- Web qiymatlari request payload va setup data bilan mos.

---

## Faza 8 — Runner, verification va yakuniy knowledge write-back

**Status: DONE**

### Bajarilgan

- [x] Dedicated visit runnerning setup baseline bilan dependency modelini
  yakunlash.
- [x] `scripts/run_tests.py`ga `setup-visit` va `group-visit` targetlari
  qo'shildi; Visit runner `all/groups` tarkibiga kiritildi.
- [x] Collectionda faqat 24 setup + 2 Visit runner item tanlandi; leaf va
  runner dublikat bajarilmadi.
- [x] Minimal API + web verification bajarildi.
- [x] Orderli visit API + linked grid + order view verification bajarildi.
- [x] Failure response/log/trace orqali root cause aniqlandi; locator yoki
  payloadni taxmin bilan almashtirmaslik.
- [x] Tasdiqlangan visit UI/API bilimlarini canonical Smartup dossier/referencega
  provenance bilan yozish.
- [x] `skills/scripts/validate_skills.py` `errors=0` natija berdi.
- [x] Plan statuslarini yakuniy natijaga mos yangilash.
- [x] Yakuniy `setup-visit` pytest natijasi:
  `25 passed, 1 skipped, 1 deselected in 537.09s`.

### Acceptance criteria

- Minimal visit API + web verification o'tadi.
- Orderli visit API + web verification o'tadi.
- Runner bir xil testni ikki marta yig'maydi.
- Canonical knowledge va test docstringlari real xatti-harakatga zid emas.
- `start_vizit.md`dagi barcha fazalar `DONE` holatiga o'tkazilgan.

---

## Umumiy yakuniy natija

Setup zanjiri zarur IDlarni tayyorlaydi. Dedicated visit runner mobil client
sifatida autentifikatsiya qiladi, API orqali minimal vizit va keyin orderli
vizit yaratadi. Har bir API natijasi o'z `mobile_visit_id`/note qiymati bilan
`data_store.json`ga yoziladi va keyingi web testcase A2 Visit formasida aynan
shu yozuvni topib tekshiradi.
