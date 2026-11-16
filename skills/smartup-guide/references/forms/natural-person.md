# Natural Person Add Form

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)
- [URL Va Navigation](#url-va-navigation)
- [Test Arxitekturasi](#test-arxitekturasi)
- [Field Bilimlari](#field-bilimlari)
- [List Va View Tekshiruv](#list-va-view-tekshiruv)
- [Debug Notes](#debug-notes)

## Quick Lookup

### URL Va Navigation

#### Natural person add
Tags: natural-person, setup, form, navigation
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/flow_setup/flow_natural_person.py:9`; `tests/smoke/test_setup/test_0_setup_runner.py`
- Navigation: `Справочники` -> `Физические лица` -> `Создать`.
- URL pattern: `/anor/mr/person/natural_person+add`.
- Test fayli: `tests/smoke/test_setup/test_05_natural_person.py`.
- Runner: `tests/smoke/test_setup/test_0_setup_runner.py`, step `05 - Natural Person` va `20 - Natural Person For Client 1`.

## Flow And Tests

### Test Arxitekturasi

#### Alohida natural person flow
Tags: natural-person, legal-person, helper
Status: code-confirmed
Verified: 2026-09-18
Source: `tests/smoke/test_setup/flow_setup/flow_natural_person.py`; `tests/smoke/test_setup/test_05_natural_person.py`; `tests/smoke/test_setup/test_20_natural_person_for_client_1.py`
- Natural Person alohida entity test hisoblanadi; testcase logikasi `tests/smoke/test_setup/test_05_natural_person.py` ichidagi `run_natural_person` va `tests/smoke/test_setup/test_20_natural_person_for_client_1.py` ichidagi `run_natural_person_for_client_1` (`test_0_setup_runner` step 05 va 20) da turadi.
- Bir nechta test ishlatadigan UI oqimi `tests/smoke/test_setup/flow_setup/flow_natural_person.py` ga ajratilgan; test fayllari bir-biridan helper import qilmaydi.
- List/create alohida `open_natural_person_list(page, *, step_name)` va
  `open_natural_person_create(page, *, step_name)` flowlari bilan ochiladi.
- `create_natural_person(page, name, person_code, *, step_name, client=False)`
  ochiq create formani to'ldiradi va saqlaydi; navigatsiyani o'zi boshlamaydi.
- `open_natural_person_view(page, name, *, step_name)` viewni ochadi,
  `close_natural_person_view(page, *, step_name)` yopadi. Ism/status assertioni
  va person IDni saqlash testcase ichida qoladi.
- Joriy smoke oqimi faqat `person_name` + `Код`ni ishlatadi; global
  `scope`/`mode` parametri yo'q.
## Known Locators

### Field Bilimlari

#### Natural person add fields

Tags: natural-person, input, locator
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/flow_setup/flow_natural_person.py:31`
- `AutoBasePage.autocomplete(label="Имя", ng_model="d.first_name", ...)` person qidiruvining `:table_persons` javobini kuzatadi. `Код` alohida input. `client=True` bo‘lganda `Клиент` belgilanadi, har ikki oqim `Статус`ni tekshiradi.
- Eski add formasidagi ko‘rinadigan maydonlar [arxiv rasmida](screenshots/natural-person/add-form-red_test-2026-07-01.png) qayd etilgan.

##### Filial konteksti
Status: user-reported
Verified: pending
Source: user — 2026-07-01, `Клиент` maydonining filialga bog‘liqligi bo‘yicha tuzatish
- User kuzatuvida client belgisining ko‘rinishi tanlangan filialga bog‘liq. Xodim va mijozning standalone wrapperlari `filial-pw{code}`ga o‘tadi.

## Business Rules

### List Va View Tekshiruv

#### Natural person list

Tags: natural-person, list, grid, assert
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_05_natural_person.py:43`; `tests/smoke/test_setup/test_20_natural_person_for_client_1.py:42`
- Ikkala test listda `grid_controller(search=person_code)` orqali filtrlab, ko‘rinadigan ism va `Активный`ni bir qatorda tekshiradi. View ochishda aynan ismli qator tanlanadi va `Просмотр` bosiladi.

#### Natural person view

Tags: natural-person, view, assert
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/flow_setup/flow_natural_person.py:51`; `tests/smoke/test_setup/test_20_natural_person_for_client_1.py:47`; `tests/smoke/test_setup/test_05_natural_person.py:47`
- View headingi `Физическое лицо (просмотр)`, routeda `natural_person_view` keladi. Testlar nom va `Активный`ni `include_input_values=True` bilan tekshiradi. Client testi keyin `Справочники → Клиенты` ro‘yxatida yaratilgan ismni qidiradi.

#### User person IDni view URLdan olish

Tags: natural-person, user, view, id, data-store
Status: code-confirmed
Verified: 2026-08-27
Source: user; `tests/smoke/test_setup/test_05_natural_person.py`

- `natural_person-pw{code}` keyingi `run_user` testida userning
  `Физическое лицо` maydoniga bog'lanadi.
- Setup test view URLdagi `person_id`ni `data_store.json.user_person_id`
  kaliti bilan saqlaydi; bu client person IDdan alohida.

#### Client person IDni view URLdan olish

Tags: natural-person, client, view, id, data-store
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI; `tests/smoke/test_setup/test_20_natural_person_for_client_1.py`

- Client view URL patterni `anor/mr/person/natural_person_view?person_id=<id>`;
  summary `natural_client-pw{code} (<id>)` ko'rinishida IDni ko'rsatadi.
- Client setup test view ochilgach `person_id`ni musbat integer sifatida
  tekshiradi va `data_store.json.client_person_id`ga saqlaydi.

## Known Issues

### Debug Notes

<a id="2026-06-02-listview-verification"></a>
<a id="2026-07-01-base-funksiya-refactor-verification"></a>
<a id="2026-07-14-reusable-flow-refactor-verification"></a>

Eski create/view helperlari hamda oldingi runlar uchun [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi). Joriy client oqimida kerakli filial tanlangani va `Клиент` belgilangani yakunda `Клиенты` ro‘yxatidagi qator bilan tekshiriladi.

## Screenshot Paths

[Legacy yaratish formasining boshlang‘ich holati](screenshots/natural-person/add-form-red_test-2026-07-01.png).
