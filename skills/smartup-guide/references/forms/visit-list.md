# Visit List

Tags: visit, a2, grid, search, view, mobile
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI `*/a2/trade/tvt/visit_list`

## Contents

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)

## Quick Lookup

- Form slug: `visit-list`
- Navigation: `Продажа > Визиты > Визиты`
- A2 URL pattern: `*/a2/trade/tvt/visit_list`
- Title: `Визиты`
- Page object: `utils/angular_base_page.py::AngularBasePage`

## Screenshot Paths

- N/A — joriy tekshiruvda locator uchun screenshot zarur bo'lmadi.

## Known Locators

### List va default grid

Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI `*/a2/trade/tvt/visit_list`

- List `main` ichidagi ko'rinadigan `smt-data-table`.
- Data qatori `.smt-data-row`; global search `input[type="search"]` va
  placeholderi `Поиск...`.
- Default ustunlar: `Клиент`, `Рабочая зона`, `Пользователь`, `Время визита`,
  `Тип визита`, `Статус`.
- Bo'sh listda `Нет результатов` ko'rinadi va pagination `0/0` bo'ladi.

### Visit ID table setting va search chegarasi

Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI `*/a2/trade/tvt/visit_list`

- Data-table actions menyusi `Настройка таблицы` va `Настройки поиска`
  menuitemlarini beradi.
- `Настройки таблицы` dialogida `ИД` inactive field sifatida mavjud. U
  yoqilgach grid headerida `data-smt-col-key="visit_id"` bilan chiqadi.
- `Настройки поиска` dialogida faqat `Клиент`, `Рабочая зона`, `Пользователь`
  va `Альтернативное название` fieldlari mavjud; `ИД` va
  `Примечание к визиту` yo'q.
- Shuning uchun Visit list consumeri
  `AngularBasePage.grid_setting(menu_name="Настройка таблицы", field_name="ИД")`
  ishlatadi; `search_name="ИД"` bermaydi.
- Mobile `entry_id`/`mobile_visit_id` webdagi server `visit_id` bilan bir xil
  emas. Ularni bitta ID deb solishtirmaslik kerak.
- Unique visit note global search fieldi emas. Barqaror correlation:
  client nomi bilan global search qilish, keyin ko'rinadigan rowni unique
  visit note bo'yicha topish va `ИД` cellidan server `visit_id`ni o'qish.
- A2 headerda selection/action uchun `data-smt-col-key` bo'lmagan texnik
  element bo'lishi mumkin. Column index faqat `data-smt-col-key` headerlari
  orasidan hisoblanishi kerak; aks holda row data cell indeksi bittaga siljiydi.

### Row action va view

Status: live-ui-and-test-confirmed
Verified: 2026-08-27
Source: live UI va dedicated Visit runner

- Qator tanlangandan keyin `Просмотреть` action page darajasida chiqadi; uni
  row ichidan qidirmaslik kerak.
- View URL: `*/a2/trade/tvt/visit_view?visit_id=<server_visit_id>`.
- View title: `Визит (просмотр)`.
- Asosiy readonly fieldlar: `ID визита`, `Статус`, birinchi `Время визита`
  (datetime), `Рабочая зона`, `Пользователь`, `Клиент`; ikkinchi
  `Время визита` human-readable duration qiymatini beradi.
- `Дополнительная информация` tabida `Начало визита` va `Конец визита` bor.
  Server va mobile timestamp orasida bir soniyalik normalizatsiya kuzatilgan,
  shuning uchun datetime assertion ±5 soniya tolerantlik bilan qilinadi.
- `Примечания` tabidagi grid `ИД`, `Примечание`, `Пользователь` va
  `Дата создания` ustunlarini ko'rsatadi. Unique note shu yerda exact
  tekshiriladi.

### Orderli visitdagi linked order

Status: live-ui-confirmed
Verified: 2026-08-28
Source: live UI; `tests/smoke/test_groups/test_visit_grup/test_02_mobile_order_visit.py`

- Visit viewdagi `Заказы` boshqaruvi ARIA `tab` emas, accessible name'i
  `Заказы` bo'lgan button; `AngularBasePage.click(name="Заказы", exact=True)`
  bilan ochiladi.
- Linked order grid ustunlari: `ТМЦ`, `Кол-во заказов`, `Цена`,
  `Сумма скидки/наценки`, `Сумма НДС`, `Продано`, `Рабочая зона`, `Клиент`,
  `Статус`, `Действия`.
- Product cell product nomi va price type badge'ini birga ko'rsatadi.
  `Действия` icon-buttoni linked orderni
  `*/a2/trade/tdeal/order/order_view?deal_id=<order_id>` sahifasida ochadi.
- Linked gridda warehouse ko'rsatilmaydi va order view DOMida ham warehouse
  field/column yo'q. Warehouse ID payload invariantida tekshiriladi; web
  assertion sifatida taxminiy locator yozilmaydi.

## Flow And Tests

- A2 navigation: `tests/smoke/flows/flow_navigate.py::navigate_to_a2`.
- API primitive'lari: `utils/base_api.py::BaseAPI`.
- Takroriy mobile login va filial session flowi:
  `tests/smoke/flows/flow_mobile_authorization.py::authorize_mobile`.
- Takroriy Visit sync flowi:
  `tests/smoke/flows/flow_visit_sync.py::sync_visit`.
- Form-opening inventory:
  `tests/smoke/test_forms/inventory/prodaja.py` va
  `tests/smoke/test_forms/test_a2_angular_forms.py`.
- Minimal Visit API va Web bosqichlarini bitta scenariyda saqlaydigan leaf:
  `tests/smoke/test_groups/test_visit_grup/test_01_mobile_visit.py`.
- Orderli Visit API, Web, linked grid va order view bosqichlarini bitta
  scenariyda saqlaydigan leaf:
  `tests/smoke/test_groups/test_visit_grup/test_02_mobile_order_visit.py`.
- Ordersiz va orderli ikkita Allure/pytest scenariyni yig'adigan runner:
  `tests/smoke/test_groups/test_visit_grup/test_0_visit_runner.py`.

## Business Rules

### Filial konteksti

Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI `*/a2/trade/tvt/visit_list`

- Visit list filialga bog'liq. A2 filial selectoridan boshqa filial tanlanganda
  ilova `*/a2/trade/intro/dashboard`ga qaytadi; Visit list qayta ochiladi.
- Setup'dan keyingi `filial-pw{code}`da hali mobile visit yuborilmagan bo'lsa
  list bo'sh bo'lishi mumkin.

## Known Issues

- `ИД` Search Settings fieldi emas. Uni `search_name="ИД"` bilan yoqishga
  urinish helper timeoutiga olib keladi.
- Table settingdan keyin column tartibi o'zgarishi mumkin. Kerakli indeksni
  barcha zarur ustunlar yoqilgandan keyin olish kerak.
