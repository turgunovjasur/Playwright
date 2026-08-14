# Filial (Организация) legacy Biruni formasi

## Quick Lookup

Tags: filial, organization, biruni, angularjs, setup
Status: trace-confirmed
Verified: 2026-08-13
Source: user; `tests/smoke/test_setup/test_02_filial.py`;
`test-results/allure-results/d2c3f725-feed-461b-825b-ce19d11f5baa-result.json`

- Joriy Filial list/add/view oqimi legacy Biruni formasi sifatida
  `BasePage` bilan boshqariladi; `AngularBasePage` bilan aralashtirilmaydi.
- Navigation: `Главное → Организации`.
- List heading: `Организации`; add heading: `Организация (создание)`; view
  heading: `Организация (просмотр)`.
- Test yangi `filial-pw{code}` tashkilotini shu run ichida yaratilgan
  `c_l_p_pw{code}` yuridik shaxsiga bog'laydi.

## Screenshot Paths

- `references/forms/screenshots/filial/filial__add-default__desktop-1920x1080.png`
- `references/forms/screenshots/filial/filial__add-vat-on__desktop-1200x690.png`
- `references/forms/screenshots/filial/filial__view-main__desktop-1920x1080.png`
- `references/forms/screenshots/filial/filial__view-products__desktop-1920x1080.png`
- `references/forms/screenshots/filial/filial__add-fields.json`
- `references/forms/screenshots/filial/filial__add-fields-after-switches.json`
- `references/forms/screenshots/filial/filial__add-switches.json`
- `references/forms/screenshots/filial/filial__add-switches-after-switches.json`
- `references/forms/screenshots/filial/filial__view-state.json`

## Known Locators

Tags: filial, b-input, ng-model, grid, locator
Status: code-confirmed
Verified: 2026-08-13
Source: `tests/smoke/test_setup/test_02_filial.py`; archived screenshots/JSON

- `Название`: oddiy input; test `BasePage.input(label="Название", ...)`
  ishlatadi.
- `Базовая валюта` va `Юридическое лицо`: legacy `b-input`; test
  `BasePage.b_input(...)` ishlatadi.
- Valyuta tanlangach `Продолжить?` Biruni confirmi chiqadi.
- List qidiruvi `BasePage.grid_controller(...)`, row tekshiruvi/tanlovi
  `BasePage.grid(...)` bilan bajariladi.
- Button/actionlar ikkala page objectda yagona `click(...)` API nomidan
  foydalanadi; legacy formada `BasePage.click(...)` ishlatiladi.

### Add forma field xaritasi

Tags: filial, field-discovery, ng-model, b-input, switch
Status: live-ui-confirmed
Verified: 2026-08-11
Source: archived Filial add screenshot/JSON evidence

- Oddiy inputlar: `Название → d.name`, `Порядковый номер → d.order_no`.
- Searchable legacy `b-input`lar: `Юридическое лицо → d.person_name`,
  `Базовая валюта → d.base_currency_name`, `Часовой пояс → d.timezone_name`.
- `Статус` boshlang'ich holatda `Активный`.
- `НДС → d.vat_enabled` yoqilganda `Ставка НДС (%) → d.vat_percent` inputi
  paydo bo'ladi; `Акциз → d.excise_enabled` alohida switch.
- Viewda tasdiqlangan asosiy tablar: `Основная информация` va `Продукты`.
  Eski probe'dagi `Модули`/`Настройки` candidate nomlari current truth emas.

## Flow And Tests

- Setup leaf: `tests/smoke/test_setup/test_02_filial.py::run_filial`.
- Setup runner item:
  `tests/smoke/test_setup/test_0_setup_runner.py::test_02_filial`.
- Page object: `utils/base_page.py::BasePage`.
- `AngularBasePage.button()` API nomi `AngularBasePage.click()`ga almashtirilgan;
  `BasePage` va `AngularBasePage` button click metodi bir xil nomlangan.

## Business Rules

Tags: filial, legal-person, currency, state
Status: code-confirmed
Verified: 2026-08-13
Source: `tests/smoke/test_setup/test_02_filial.py`

- Add formda `Название`, `Базовая валюта` va `Юридическое лицо` to'ldiriladi;
  `Статус` default `Активный` holatda qoladi.
- Yuridik shaxs kod bo'yicha qidiriladi va tanlangan qiymat yuridik shaxs nomi
  bilan tekshiriladi.
- Bitta yuridik shaxs filialga bog'langach keyingi add searchida chiqmasligi
  mumkin; to'g'ri setup chain avval yangi legal person, keyin filial yaratadi.
- List rowda filial nomi, yuridik shaxs kodi va `Активный` tekshiriladi. Viewda
  filial nomi, valyuta, yuridik shaxs kodi/nomi va status ko'rinishi tekshiriladi.

## Known Issues

### Filialni A2 deb noto'g'ri migratsiya qilish

Tags: filial, migration, base-page, angular-base-page
Status: trace-confirmed
Verified: 2026-08-13
Source: user;
`test-results/allure-results/d2c3f725-feed-461b-825b-ce19d11f5baa-result.json`

- Filial testini A2 deb `AngularBasePage`ga o'tkazish noto'g'ri. Joriy test
  legacy `BasePage`ga qaytarildi va relevant setup run green bo'ldi.
