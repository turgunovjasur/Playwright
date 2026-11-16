# Legal Person Add Form

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)
- [URL va navigation](#url-va-navigation)
- [Screenshotlar](#screenshotlar)
- [Field bilimlari](#field-bilimlari)
- [List va view tekshiruv](#list-va-view-tekshiruv)
- [Data store](#data-store)
- [Debug notes](#debug-notes)

## Quick Lookup

### URL Va Navigation

#### Legal person add
Tags: legal-person, setup, form, navigation
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_01_legal_person.py:17`; `tests/smoke/test_setup/test_0_setup_runner.py::test_01_legal_person`
- Navigation: `Справочники` -> `Юридические лица` -> `Создать`.
- URL pattern: `/anor/mr/person/legal_person+add`.
- Test fayli: `tests/smoke/test_setup/test_01_legal_person.py`.
- Runner: `tests/smoke/test_setup/test_0_setup_runner.py`, step `01 - Legal Person`.
- Setup chainda alohida Authorization testi yo'q: `run_legal_person` birinchi
  qadamda joriy company admini bilan login qiladi.

#### Menu add icon route
Tags: legal-person, menu, add, navigation
Status: live-ui-confirmed
Verified: 2026-08-18
Source: live UI
- `Справочники` -> `Юридические лица` menu qatoridagi alohida `+add` ikonka-link
  `/anor/mr/person/legal_person+add` formasini record ID siz ochadi.

#### List row view va edit route'lari
Tags: legal-person, list, view, edit, navigation, person-id
Status: live-ui-confirmed
Verified: 2026-08-18
Source: live UI
- Listdagi mavjud qator tanlangach `Просмотреть` va `Изменить` actionlari
  ko'rinadi. Ular tanlangan yozuv ID sini query orqali uzatib, mos ravishda
  `/anor/mr/person/legal_person_view?person_id=<person_id>` va
  `/anor/mr/person/legal_person+edit?person_id=<person_id>` formalarini ochadi.

## Screenshot Paths

### Screenshotlar

#### Add form screenshotlari
- Screenshot arxivi: `references/forms/screenshots/legal-person/`.
- Add main empty: `references/forms/screenshots/legal-person/legal-person__add-main-empty__desktop-1920x1080.png`.
- GPS modal screenshot: `references/forms/screenshots/legal-person/gps-after-click.png`.
- View `Основная информация`: `references/forms/screenshots/legal-person/legal-person__view-основная-информация__desktop-1920x1080.png`.
- View `Дополнительная информация`: `references/forms/screenshots/legal-person/legal-person__view-дополнительная-информация__desktop-1920x1080.png`.
- View `Расчетный счет`: `references/forms/screenshots/legal-person/legal-person__view-расчетный-счет__desktop-1920x1080.png`.
- View `Контактные лица`: `references/forms/screenshots/legal-person/legal-person__view-контактные-лица__desktop-1920x1080.png`.
- View state JSON: `references/forms/screenshots/legal-person/legal-person__view-state.json`.


## Known Locators

### Field Bilimlari

#### Main legal person fields

Tags: legal-person, input, faker
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_01_legal_person.py:30`

- Joriy setup `Код`ga `c_l_p_pw{code}`, `Полное название`ga Faker kompaniya nomi va `legal_person-pw{code}` suffixini yozadi. Saqlashdan oldin `Статус` belgilanganini tekshiradi.
- GPS va ixtiyoriy maydonlarning legacy ko‘rinishi [add snapshotida](screenshots/legal-person/legal-person__view-state.json) saqlangan.

#### Owner va director

Tags: legal-person, owner, director
Status: live-ui-confirmed
Verified: 2026-11-16
Source: `screenshots/legal-person/legal-person__view-state.json` (add-main-empty va view bo‘limlari)

- Arxivlangan yaratish formasida `Собственник` va `Руководитель` alohida maydonlar. View’dagi nomlar `Владелец` va `Директор`. Joriy minimal setup bu bog‘lanishlarni to‘ldirmaydi.

#### Region

Tags: legal-person, region
Status: live-ui-confirmed
Verified: 2026-11-16
Source: `screenshots/legal-person/legal-person__view-state.json` (add-main-empty, view-дополнительная-информация)
- Arxivda `Регион` yaratish formasida va view’ning `Дополнительная информация` bo‘limida ko‘rinadi. Eski b-tree tanlash ssenariysi uchun [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi).

#### Tabs

Tags: legal-person, tabs, note, leadership
Status: live-ui-confirmed
Verified: 2026-11-16
Source: `screenshots/legal-person/legal-person__view-state.json` (add-main-empty va view bo‘limlari)
- Yaratish formasining tablari orasida `Расчетный счет`, `Контактные лица`, `Примечание` va `Руководящие должности` bor. Arxivdagi view hisob raqami uchun bank, hisob nomi, raqami va statusni, kontakt uchun ism, lavozim, telefon, tug‘ilgan sana va izohni ko‘rsatadi.

## List Va View Tekshiruv

### Legal person list

Tags: legal-person, list, grid, assert
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_01_legal_person.py:55`
- Setup listda `grid_controller(search=legal_code)` bilan yozuvni topadi, kod, nom va `Активный`ni bitta qatorda tekshiradi. Tanlangan qatordan `Просмотреть` view’ni ochadi.

### Legal person view

Tags: legal-person, view, assert
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_01_legal_person.py:58`
- Test `Юридическое лицо (просмотр)` va `legal_person_view` routeni kutadi. U kod, nom va `Активный`ni `include_input_values=True` bilan tekshiradi va `Закрыть` orqali listga qaytadi. To‘rtta arxiv view tabining tasvirlari yuqorida.

## Business Rules

### Data Store

#### Saqlanadigan qiymatlar
Tags: legal-person, data-store
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_01_legal_person.py:36`; `tests/smoke/test_setup/test_01_legal_person.py:68`
- Session `code`
- `legal_person_code`, `legal_person_name`

## Known Issues

### Debug Notes

<a id="2026-06-02-verification"></a>
<a id="2026-06-02-bankcontact-verification"></a>
<a id="2026-06-02-gps-verification"></a>
<a id="2026-06-02-listview-verification"></a>

2026-06-02 dagi to‘rtta run eski setup zanjiriga tegishli. Bank, kontakt, GPS va kengaytirilgan view tekshiruvlari uchun [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi).

## Flow And Tests

`tests/smoke/test_setup/test_01_legal_person.py::run_legal_person` admin loginidan view yopilguncha oqimni bajaradi. Keyingi `test_02_filial.py` saqlangan yuridik shaxsdan foydalanadi.
