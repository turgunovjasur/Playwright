# Legal Person Add Form

## Mundarija

- [URL va navigation](#url-va-navigation)
- [Screenshotlar](#screenshotlar)
- [Field bilimlari](#field-bilimlari)
- [List va view tekshiruv](#list-va-view-tekshiruv)
- [Data store](#data-store)
- [Debug notes](#debug-notes)

## URL Va Navigation

### Legal person add
Tags: legal-person, setup, form, navigation
- Navigation: `Справочники` -> `Юридические лица` -> `Создать`.
- URL pattern: `/anor/mr/person/legal_person+add`.
- Test fayli: `tests/smoke/test_setup/test_01_legal_person.py`.
- Runner: `tests/smoke/test_setup/test_0_setup_runner.py`, step `01 - Legal Person`.
- Setup chainda alohida Authorization testi yo'q: `run_legal_person` birinchi
  qadamda joriy company admini bilan login qiladi.

## Screenshotlar

### Add form screenshotlari
Tags: legal-person, screenshot
- Screenshot arxivi: `references/forms/screenshots/legal-person/`.
- Add main empty: `references/forms/screenshots/legal-person/legal-person__add-main-empty__desktop-1920x1080.png`.
- GPS modal screenshot: `references/forms/screenshots/legal-person/gps-after-click.png`.
- View `Основная информация`: `references/forms/screenshots/legal-person/legal-person__view-основная-информация__desktop-1920x1080.png`.
- View `Дополнительная информация`: `references/forms/screenshots/legal-person/legal-person__view-дополнительная-информация__desktop-1920x1080.png`.
- View `Расчетный счет`: `references/forms/screenshots/legal-person/legal-person__view-расчетный-счет__desktop-1920x1080.png`.
- View `Контактные лица`: `references/forms/screenshots/legal-person/legal-person__view-контактные-лица__desktop-1920x1080.png`.
- View state JSON: `references/forms/screenshots/legal-person/legal-person__view-state.json`.
- Legal person bo'yicha screenshot arxivi faqat GPS modal bilan cheklanmasin; kamida add main va view tab screenshotlari ham shu skill papkasida bo'lishi kerak.

## Field Bilimlari

### Main legal person fields
Tags: legal-person, input, faker
- `Полное название*` yagona ko'rinadigan majburiy main input; `Код`, `Веб-сайт`, `Штрих-код`, `Почтовый индекс`, `Альтернативное название`, `Телефон`, `Телеграм`, `Email`, `Регион`, `Адрес`, `Почтовый адрес`, `ИНН`, `ОКЭД`, `Регистрационный код плательщика НДС`, `Ориентир` ixtiyoriy inputlar. Smoke code qiymati: `c_l_p_pw{code}`.
- `GPS координаты` readonly input; map button (`selectLatLng(d.latlng, 'main')`) orqali tanlanadi, oddiy `.fill()` bilan to'ldirilmaydi.
- GPS modalida `q.search_lat_lng` inputiga `41.2994958,69.2400734` yozib `Создать и закрыть` bosilganda formadagi `d.latlng` qiymati `41.2994958,69.2400734,12` bo'ladi; modal ko'rinib qolsa `Закрыть` bilan yopiladi.
- Testda Faker `ru_RU` company/name/address qiymatlari ishlatiladi; asosiy legal person nomida `legal_person-pw{code}` suffix saqlanadi, chunki keyingi filial setup shu suffixni tekshiradi.

### Owner va director
Tags: legal-person, owner, director, natural-person, relation
- `Собственник` b-input ustunlari `Код` / `Название`; u alohida legal person bo'lishi kerak.
- `Руководитель` b-input ustunlari `Ф.И.О.` / `Код`; u alohida natural person bo'lishi kerak.
- Director quick-add `Физическое лицо (создание)` sahifasiga o'tadi; owner quick-add esa yana `Юридическое лицо (создание)` ochadi. Barqaror test uchun avval owner legal person va director natural person alohida yaratiladi, keyin asosiy legal person add formida code orqali tanlanadi.
- Director natural person yaratish logikasi Legal Person ichida yozilmaydi; `tests/smoke/test_setup/test_05_natural_person.py` ichidagi `natural_person_values` va `create_natural_person_record` import qilib ishlatiladi.

### Region
Tags: legal-person, region, b-tree
- `Регион` oddiy b-input emas, b-tree search input (`_$bTree.searchValue`).
- `Ташкент` search qilishdan oldin b-tree input click/focus qilinadi; shunda `.hint` ochiladi va `город Ташкент` yoki `Ташкент` optioni hint ichidagi exact text/label yoki `.jstree-anchor` orqali tanlanadi.

### Tabs
Tags: legal-person, tabs, note, leadership
- `Примечание` tabida `d.details.note` textarea bor.
- `Руководящие должности` tabida director `Имя`, `Фамилия`, `Отчество`, `ИНН/ПНФЛ директора` va accountant `Имя`, `Фамилия`, `Отчество` inputlari bor.
- `Расчетный счет` tabida `Создать` bosilganda bank account modal ochiladi: `Название счета*`, `МФО`, `Банк*`, `Расчетный счет*`, `Валюта*`, `Примечание`. `МФО=00001` yozib `Tab` bosilsa `Банк*` avtomatik `Центр расчетов Центрального банка по г. Ташкенту` bo'ladi.
- `Контактные лица` tabida `Создать` bosilganda contact modal ochiladi: `Ф.И.О.*`, `Должность`, `Телефон`, `Дата рождения`, `Примечание`. `Должность` uchun `Добавить` bosilganda `/anor/mr/person/contact_position+add` ochiladi; `Название*` va `Код` to'ldirib saqlasa confirm chiqmaydi, legal person add sahifasiga contact modal ochiq holda qaytadi.

## List Va View Tekshiruv

### Legal person list
Tags: legal-person, list, grid, assert
- List URL/search: `Справочники` -> `Юридические лица`, global `Поиск`ga `legal_person_code` yoziladi.
- Default grid ustunlari ichida `Код`, `Название`, `Альтернативное название`, `Статус` ko'rinadi.
- Joriy smoke test listda `code`, `name`, `Активный` ni tekshiradi.
- View tugmasi: row tanlangandan keyin `Просмотреть`.

### Legal person view
Tags: legal-person, view, assert
- View URL pattern: `/anor/mr/person/legal_person_view`.
- View heading bilan tab heading birga chiqadi; heading assertda `get_by_role("heading").filter(has_text="Юридическое лицо (просмотр)")` ishlatiladi.
- `Основная информация` tabida `name`, `short_name`, owner name, `code`, `barcode`, `email` ko'rinadi.
- `Дополнительная информация` tabida director full name, phone, region, zip, address, post address, address guide, GPS, INN, OKED, note va accountant full name ko'rinadi; `vat_code`, `web`, `telegram` hozir viewda default ko'rinmaydi, assert qilinmaydi.
- `Расчетный счет` tabida bank name, account name, account code, `Да`, `Активный` ko'rinadi; MFO va currency default view gridda ko'rinmaydi.
- `Контактные лица` tabida contact full name, position, phone, birthday va note ko'rinadi.

## Data Store

### Saqlanadigan qiymatlar
Tags: legal-person, data-store
- Session `code`
- `legal_person_code`, `legal_person_name`

## Debug Notes

### 2026-06-02 verification
Tags: legal-person, run-result
- `test_01_authorization` + `test_02_legal_person` headless run passed: 2 passed in 37.87s.
- `test_01_authorization` + `test_03_filial` headless run passed: 2 passed in 17.08s.
- Run code: `2843`; data storega legal person qiymatlari yozildi.

### 2026-06-02 bank/contact verification
Tags: legal-person, bank-account, contact-person, run-result
- `test_01_authorization` + `test_02_legal_person` headless run passed: 2 passed in 42.91s.
- `test_01_authorization` + `test_03_filial` headless run passed: 2 passed in 11.08s.
- Run code: `8139`; data storega bank account (`MFO=00001`) va contact person/lavozim qiymatlari yozildi.

### 2026-06-02 GPS verification
Tags: legal-person, gps, run-result
- `test_01_authorization` + `test_02_legal_person` headless run passed: 2 passed in 51.18s.
- `test_01_authorization` + `test_03_filial` headless run passed: 2 passed in 11.53s.
- Run code: `4291`; data storega `legal_person_gps=41.2994958,69.2400734,12` yozildi.

### 2026-06-02 list/view verification
Tags: legal-person, list, view, run-result
- Legal person list row endi code, Faker name, short name va `Активный` statusni tekshiradi.
- Legal person view `Основная информация`, `Дополнительная информация`, `Расчетный счет`, `Контактные лица` tablaridagi qo'shilgan qiymatlarni tekshiradi.
- `test_01_authorization` + `test_02_legal_person --new-code --headless -s` passed: 2 passed in 62.13s.
- Run code: `5535`; data storega legal person qiymatlari view checkdan keyin yozildi.
