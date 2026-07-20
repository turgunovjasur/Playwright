# Рабочая зона (Room) — yaratish va prikreplenie

Room = **Рабочая зона**. Create test: `tests/smoke/test_setup/test_room.py` (`run_room`); attachment test: `tests/smoke/test_setup/test_room_attachment.py` (`run_room_attachment`).

## Navigatsiya

- Ro'yxat: **Справочники → Рабочие зоны** (user menyusida; admin'da filialga o'tilgach ko'rinadi). URL: `.../trade/trf/room_list`.
- Yaratish: `Создать` → `Рабочая зона (создание)`; `c_rm_pw{code}` code + `room-pw{code}` nom + `Активный`.
- Prikreplenie: room qatorini bosib → **`Прикрепление`** tugmasi → `Рабочая зона (прикрепление): room-pw{code}` (`.../anor/mrf/room_attachment?room_id=<id>`).

## Create Form Locator/Loader Notes

Tags: room, locator, loader, helper
- 2026-06-26 debug: `Создать` bosilgandan keyin `room+add` sahifasida blocking loader/title kech yuklanishi mumkin; heading assertdan oldin `BasePage(page).wait_for_loader()` chaqirilsin.
- Label helper: `Код` va `Название` ketma-ket maydonlar. Keng card/col konteyneridagi birinchi inputni olish `Название` qiymatini `Код` inputiga yozib yuboradi. `BasePage.input(...)` labeldan keyingi birinchi real inputni target qilishi kerak.
- Screenshot: `references/forms/screenshots/room/room__add-loader__desktop-20260626.png`.

## Прикрепление tablari (link role)

`Штаты`, **`Тип цены`**, `Типы оплат`, `Наборы ТМЦ`, `Скидки/наценки`, `Склады`, `Кассы`, `Расчетные счета`, `Проект`, `Юридические лица`, `Физические лица`, `Акции`, `Ограничения`, `Опросник`, `Технологические карты`.

`run_room_attachment` ulaydigan: Типы оплат, Склады, Кассы, Физические лица (mijoz), **Тип цены (Акция)**.

### Room attachment test arxitekturasi
Tags: room, attachment, test, base-page, idempotent
- `run_room_attachment` standart `authorization(page, who="user", code=code)` bilan userga o'tadi va defensive `navigate_to("Рабочие зоны")` qiladi.
- Attachment sahifa sarlavhasi `b-page` ichida emas, `#kt_content`da va heading role'ga ega; sahifa ochilishi `base.expect_page(heading=..., root="#kt_content")` bilan tekshiriladi.
- Sidebar linklarining accessible name'ida qo'shimcha matn/whitespace bo'lishi mumkin; `get_by_role("link", name=...)` partial match ishlaydi, `exact=True` timeout bergan.
- Attachment bo'lim nomi (`Типы оплат`, `Склады`, `Кассы` va boshqalar) aktiv card'ning `H5` headingida, tegishli `b-grid`dan tashqarida turadi. Bo'lim almashganini `base.expect_page(heading="...", root="b-page")` bilan tekshir; `root=<grid selector>` ishlamaydi. `base.text("...")` esa sidebar linkdagi bir xil matn sabab aktiv bo'limni isbotlamaydi.
- Типы оплат / Склады / Кассы alohida ma'noli Allure qadamlari bo'lgani uchun loopga yig'ilmaydi; har biri ochiq `with allure.step(...)` blokida bajariladi. `Доступные` grid holati raw locator bilan emas, boolean qaytaradigan `base.grid(is_empty=True, root=...)` orqali aniqlanadi.
- Mijoz va `Акция` qatorining Available/Attached holati raw `.tbl-row.filter(...).is_visible()` bilan emas, `base.grid(<row text>, is_visible=True)` orqali aniqlanadi; helper target qator ko'rinsa `True`, bo'lmasa `False` qaytaradi.
- `Типы оплат`da `Доступные`/`Прикрепленные` bosilganda mavjud `table_payment_type` grid asinxron yangilanadi: clickdan darhol keyin loader ko'rinsa ham eski tabning qatorlari qisqa vaqt DOMda qoladi. `grid(is_empty=True)` yoki `grid(..., is_visible=True)`dan oldin `base.wait_for_loader()` shart; 2026-07-14 live probe'da oldingi 4 qator sabab darhol tekshiruv `False`, loader tugagach `нет данных` sabab `True` qaytardi.
- Qayta-runda `Доступные` bo'sh bo'lsa test shunchaki skip qilmaydi: `Прикрепленные`da 4 payment type, `Основной склад`, `Основная касса`, `natural_client-pw{code}` va `Акция` mavjudligini tekshiradi.

### Oddiy tablar patterni (Типы оплат / Склады / Кассы / Физические лица)
`link → expect b-page text → "Доступные" → (grid checkall yoki kerakli qatorni bosish) → "Прикрепить" → confirm_biruni("Прикрепить N?" / "...nomi?") → "Прикрепленные"da tekshirish`.

### "Тип цены" tab — ikki bosqichli ulash (MUHIM, MCP bilan 2026-06-16 tasdiqlangan)
"Доступные" boshida **bo'sh** (нет данных) — narx turini avval katalogdan room'ga qo'shish kerak. Shuning uchun ulash 2 bosqich:

1. **Katalogdan Доступныега qo'shish**: `Тип цены` link → `Доступные` → **`Создать тип цены`** (→ `Цены (прикрепление)` sahifa, `.../anor/mkr/price_type_list+attach`, katalog: Промо/Акция/Возврат/Передача забаланс/Обмен) → kerakli qatorni (mas. `Акция`) bosish → qatorda **`Прикрепить`** → `confirm_biruni("Прикрепить Акция?")`. Bu room_attachment'ga qaytaradi va `Акция`ni **Доступные**ga qo'shadi.
2. **Доступныеdan Прикрепленныега**: `Тип цены` link → `Доступные` → `Акция` qatorini bosish → qatorda **`Прикрепить`** → `confirm_biruni("Прикрепить Акция?")`. Endi `Прикрепленные`da `Акция` (PRCT:2) ko'rinadi.

⚠️ Faqat 1-bosqich qilinsa, `Акция` Доступныеда qoladi (Прикрепленныеда faqat setup'dagi `Price Type UZB-pw{code}` bo'ladi) — order'da aksiya chegirmasi ishlamaydi.

Setupdagi `Price Type UZB-pw{code}` room'ga narx turi FORMASI orqali ("Выбранных" rooms) ulanadi — bu Тип цены prikreplenie tabidan boshqa, alohida bog'lanish.

## Nega kerak
Room'ga `Акция` narx turi ulanmasa, C-group aksiya chegirmasi order'ning "Акции" tabида `Тип цены акции не прикреплен к рабочей зоне...` xatosi bilan ishlamaydi. To'liq aksiya zanjiri: [action.md].

## Debug Notes

### 2026-07-14 qoidalarga mos refactor
Tags: room, attachment, refactor, run-result
- Raw `expect(page.locator(...))` tekshiruvlari BasePage helperlariga o'tkazildi, 3 ta attachment bo'limi alohida Allure step sifatida ochiq yozildi va oldindan attached holat uchun aniq verifikatsiya qo'shildi.
- `test_room_attachment.py` saqlangan code (`NEW_CODE=0`) va `--headless` bilan mavjud attached state, `expect_page(root="#kt_content")` hamda boolean `grid(is_empty=True/is_visible=True)` orqali **1 passed in 28.41s**.
