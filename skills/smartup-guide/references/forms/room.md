# Рабочая зона (Room) — yaratish va prikreplenie

Room = **Рабочая зона**. Create test: `tests/smoke/test_setup/test_03_room.py` (`run_room`); attachment test: `tests/smoke/test_setup/test_21_room_attachment.py` (`run_room_attachment`).

## Quick Lookup

### Navigatsiya

- Ro'yxat: **Справочники → Рабочие зоны** (user menyusida; admin'da filialga o'tilgach ko'rinadi). URL: `.../trade/trf/room_list`.
- Yaratish: `Создать` → `Рабочая зона (создание)`; `c_rm_pw{code}` code + `room-pw{code}` nom + `Активный`.
- Prikreplenie: room qatorini bosib → **`Прикрепление`** tugmasi → `Рабочая зона (прикрепление): room-pw{code}` (`.../anor/mrf/room_attachment?room_id=<id>`).

## Known Locators

### Create Form Locator/Loader Notes

Tags: room, locator, loader, helper
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_03_room.py:31`; `screenshots/room/room__add-loader__desktop-20260626.json`
- Yaratishda `Создать`dan keyin setup loader va `Рабочая зона (создание)`ni kutadi. `Код` va `Название` alohida nomlangan inputlardan to‘ldiriladi.

#### View URLdan room IDni olish

Tags: room, view, id, data-store
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI; `tests/smoke/test_setup/test_03_room.py`

- Room view URL patterni `anor/mrf/room_view?room_id=<id>`; summary ham
  `room-pw{code} (<id>)` ko'rinishida IDni ko'rsatadi.
- Setup test save'dan keyin view'ni ochib, `room_id`ni musbat integer sifatida
  tekshiradi va `data_store.json.room_id`ga saqlaydi.

## Flow And Tests

### Прикрепление tablari (link role)

`Штаты`, **`Тип цены`**, `Типы оплат`, `Наборы ТМЦ`, `Скидки/наценки`, `Склады`, `Кассы`, `Расчетные счета`, `Проект`, `Юридические лица`, `Физические лица`, `Акции`, `Ограничения`, `Опросник`, `Технологические карты`.

`run_room_attachment` ulaydigan: Типы оплат, Склады, Кассы, Физические лица (mijoz), **Тип цены (Акция)**.

#### Room attachment test arxitekturasi

Tags: room, attachment, test, base-page, idempotent
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_21_room_attachment.py:40`
- `run_room_attachment` user bilan kiradi va room qatoridagi `Прикрепление`dan ochiladi. `AutoBasePage.tab(name=..., section=True)` bo‘limni, `tab(name="Доступные")` va `tab(name="Прикрепленные")` tegishli ro‘yxatni tanlaydi.
- To‘lov turlari, ombor va kassa uchun available grid bo‘shligi alohida tekshiriladi. Har birida loaderdan keyin attached ro‘yxatdagi nomlar tasdiqlanadi. Client va aksiya narxi uchun kerakli qator borligi tekshiriladi.

#### Warehouse ID alohida setup testida olinadi

Tags: room, attachment, warehouse, ownership, data-store
Status: code-confirmed
Verified: 2026-08-27
Source: user; `tests/smoke/test_setup/test_21_room_attachment.py`;
`tests/smoke/test_setup/test_22_warehouse.py`

- `run_room_attachment` faqat `Основной склад`ni roomga biriktiradi.
- Warehouse view tekshiruvi va `warehouse_id`ni saqlash Room Attachment ichida
  bajarilmaydi; bu ish setup runnerdagi alohida **22 - Warehouse** case'ga
  tegishli. UI kontrakti uchun [warehouse.md](warehouse.md)ga qarang.

#### Oddiy tablar patterni (Типы оплат / Склады / Кассы / Физические лица)
`link → expect b-page text → "Доступные" → (grid checkall yoki kerakli qatorni bosish) → "Прикрепить" → confirm_biruni("Прикрепить N?" / "...nomi?") → "Прикрепленные"da tekshirish`.

#### "Тип цены" tab — ikki bosqichli ulash (MUHIM, MCP bilan 2026-06-16 tasdiqlangan)
"Доступные" boshida **bo'sh** (нет данных) — narx turini avval katalogdan room'ga qo'shish kerak. Shuning uchun ulash 2 bosqich:

1. **Katalogdan Доступныега qo'shish**: `Тип цены` link → `Доступные` → **`Создать тип цены`** (→ `Цены (прикрепление)` sahifa, `.../anor/mkr/price_type_list+attach`, katalog: Промо/Акция/Возврат/Передача забаланс/Обмен) → kerakli qatorni (mas. `Акция`) bosish → qatorda **`Прикрепить`** → `confirm_biruni("Прикрепить Акция?")`. Bu room_attachment'ga qaytaradi va `Акция`ni **Доступные**ga qo'shadi.
2. **Доступныеdan Прикрепленныега**: `Тип цены` link → `Доступные` → `Акция` qatorini bosish → qatorda **`Прикрепить`** → `confirm_biruni("Прикрепить Акция?")`. Endi `Прикрепленные`da `Акция` (PRCT:2) ko'rinadi.

⚠️ Faqat 1-bosqich qilinsa, `Акция` Доступныеда qoladi (Прикрепленныеда faqat setup'dagi `Price Type UZB-pw{code}` bo'ladi) — order'da aksiya chegirmasi ishlamaydi.

Setupdagi `Price Type UZB-pw{code}` room'ga narx turi FORMASI orqali ("Выбранных" rooms) ulanadi — bu Тип цены prikreplenie tabidan boshqa, alohida bog'lanish.

## Business Rules

### Nega kerak
Room'ga `Акция` narx turi ulanmasa, aksiya chegirmasi order'ning "Акции" tabида `Тип цены акции не прикреплен к рабочей зоне...` xatosi bilan ishlamaydi. To'liq aksiya zanjiri: [aksiya dosyesi](action.md).

## Known Issues

### Debug Notes

#### 2026-07-14 qoidalarga mos refactor

Eski root-scoped helper va run qaydi uchun [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi). Joriy test `Доступные`/ `Прикрепленные` almashgach loader tugashini kutib, gridni tekshiradi.

## Screenshot Paths

[Yaratish formasidagi loader](screenshots/room/room__add-loader__desktop-20260626.png).
