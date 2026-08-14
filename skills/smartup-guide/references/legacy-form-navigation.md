# Smartup legacy formalar navigatsiya katalogi

## Mundarija

- [Klassifikatsiya qoidasi](#klassifikatsiya-qoidasi)
- [Справочники mega-menu inventari](#справочники-legacy-mega-menu-inventari-2026-07-29-live)
- [Справочники page-link inventari](#справочники-page-link-inventari-2026-07-29-live)
- [Создать dropdownidagi yashirin formalar](#создать-dropdownidagi-yashirin-formalar-2026-07-29-live)
- [Form-opening smoke verifikatsiyasi](#справочники-form-opening-smoke-verifikatsiyasi-2026-07-29)
- [Продажа mega-menu inventari](#продажа-mega-menu-inventari-2026-08-04-live)
- [Продажа page-link va +add inventari](#продажа-page-link-va-add-inventari-2026-08-04-live)
- [Склад mega-menu inventari](#склад-mega-menu-inventari-2026-08-11-live)
- [Финансы mega-menu inventari](#финансы-mega-menu-inventari-2026-08-11-live)
- [Главное mega-menu inventari](#главное-mega-menu-inventari-2026-08-11-live)
- [Alert bleed-through gipotezasi yopildi](#alert-bleed-through--trigger-add-bilan-ketdi-2026-08-05)
- [Legacy formalarda heading har doim topiladi](#legacy-formalarda-heading-har-doim-topiladi-2026-08-05)
- [Group-0 moliyaviy sahifalari](#group-0-moliyaviy-sahifalari-2026-07-31-live)

Tags: legacy, forms, navigation, menu, navbar, page-link, dropdown, filial, administration

Bu reference Smartup foydalanuvchisi legacy formani UI orqali qayerdan va
qanday topishini saqlaydigan global katalogdir. Unda navbar tab, menu column,
menu item, filial ko'rinishi, formaning yuqori page-linklari, `Создать`
dropdownidagi yashirin actionlar, destination title va canonical URLlar
birgalikda yoziladi.

## Klassifikatsiya qoidasi

- Legacy menyu/formaning foydalanuvchi ko'radigan joylashuvi va unga yetib
  borish yo'li global navigatsiya bilimidir; u faqat bitta test yoki forma
  dossieriga bog'lanmaydi.
- URL/formaning o'zi A2 bo'lmasa, uning menu/page-link/dropdown inventari
  `a2-migrated-forms.md`ga yozilmaydi. Legacy parentdan ochiladigan ayrim
  destination A2 bo'lishi mumkin; bunda user-visible legacy yo'l shu katalogda,
  A2 destinationning texnik xususiyatlari esa A2 reference/dossierda turadi.
- Joriy katalogning tekshirilgan scope'i `navbar_tab="Справочники"`,
  `navbar_tab="Продажа"`, `navbar_tab="Склад"` va
  `navbar_tab="Главное"` hamda `navbar_tab="Финансы"`. Keyingi navbar
  inventarlari ham shu faylga alohida bo'lim sifatida qo'shiladi.

## `Справочники` legacy mega-menu inventari (2026-07-29 live)

Tags: legacy, menu, navbar, spravochniki, filial, administration, test

- Muhit: `app3.greenwhite.uz/xtrade`, ochiq admin sessiyasi. Taqqoslash
  `Администрирование` va filial ro'yxatidagi birinchi operatsion filialda
  bajarildi.
- Hisobga faqat matnli forma linklari (`menu_item`) olindi. Alohida `+add`
  ikonka-linklari menu item emas va sanalmadi.
- Har ikki filial kontekstida `navbar_tab="Справочники"` ostida 3 ta
  `menu_column` bor: `Справочники`, `Основное`, `Маркетинг`.
- Menu item locatori exact accessible name bilan ishlasin. Substring
  `has_text` ishlatilsa `Опросники` + `Опросники двойных визитов` yoki
  `Вопросы` + `Вопросы двойного визита` birga topilib strict count xatosi
  beradi. Batchdagi oldingi xato mega-menuni ochiq qoldirishi mumkinligi uchun
  `navigate_to_form` flyout allaqachon ochiq bo'lsa tabni qayta bosib yopmasin.
- `Администрирование`: jami 24 ta `menu_item`:
  - `Справочники` (13): `ТМЦ`, `Цены`, `Услуги`, `Скидки/наценки`,
    `Производители`, `Типы фото-отчетов`, `Типы видео-отчетов`,
    `Комментарии`, `Вопросы`, `Опросники`, `Регионы`,
    `Вопросы двойного визита`, `Опросники двойных визитов`.
  - `Основное` (3): `Физические лица`, `Юридические лица`, `Уведомления`.
  - `Маркетинг` (8): `Акции`, `Рекомендации`, `Сеты ТМЦ`,
    `Вопросы категоризации`, `Категоризация физических лиц`,
    `Категоризация юридических лиц`, `Публикация в бот`,
    `Минимальные обязательные ассортименты`.
- Operatsion filial: jami 36 ta `menu_item`:
  - `Справочники` (14): `ТМЦ`, `Цены`, `Услуги`, `Скидки/наценки`,
    `Производители`, `Типы фото-отчетов`, `Типы видео-отчетов`,
    `Комментарии`, `Опросники`, `Регионы`, `Вопросы двойного визита`,
    `Опросники двойных визитов`, `Презентации`, `Продавцы`.
  - `Основное` (8): `Физические лица`, `Юридические лица`, `Отделы`,
    `Должности`, `Рабочие зоны`, `Штат`, `Клиенты`, `Уведомления`.
  - `Маркетинг` (14): `Акции`, `Нагрузки`, `Рекомендации`,
    `Правила ограничений`, `Продуктовая корзина`, `Сеты ТМЦ`,
    `Лимитирование ТМЦ`, `Вопросы категоризации`,
    `Категоризация физических лиц`, `Категоризация юридических лиц`,
    `Результат категоризации`, `Отчет по результату категоризации`,
    `Публикация в бот`, `Минимальные обязательные ассортименты`.
- Kesishma: 23 ta umumiy item. Faqat `Администрирование`da: `Вопросы`.
  Faqat operatsion filialda: `Презентации`, `Продавцы`, `Отделы`,
  `Должности`, `Рабочие зоны`, `Штат`, `Клиенты`, `Нагрузки`,
  `Правила ограничений`, `Продуктовая корзина`, `Лимитирование ТМЦ`,
  `Результат категоризации`, `Отчет по результату категоризации`.
- Foydalanuvchi tasdiqlagan qoida: bir xil forma ochilish xatosi bo'lsa, u
  `Администрирование` va operatsion filialning ikkalasida ham ochilmaydi;
  umumiy formalarni ikki filialda takroran ochib tekshirish kerak emas.
- Testda ishlatish: 36 ta formani eng ko'p menyu itemi bor operatsion filialda
  tekshir; faqat u yerda yo'q `Вопросы` formasini `Администрирование`da
  tekshir. Jami 37 ta unique forma check qilinadi. Har chaqiruvda
  `navbar_tab="Справочники"` va yuqoridagi exact `menu_column`/`menu_item`
  matnlari ishlatilsin.
- 2026-07-29 live test aniqligi: operatsion filialdagi `Опросники` canonical
  pathi `anor/mqzm/quiz_set_list`; `Регионы` menu itemi esa title `Страны`,
  canonical path `anor/mr/region_list` formasini ochadi.

## `Справочники` page-link inventari (2026-07-29 live)

Tags: legacy, menu, page-link, openSibling, filial, administration, test

- Foydalanuvchi tasdiqlagan qoida: menu formasi ochilganda yuqori
  `page_links` ham test qamroviga kiradi va birma-bir ochilib, destination
  title/URL bilan tekshiriladi. Page-link tarkibi filialga bog'liq, shuning
  uchun inventar `Администрирование` va operatsion filialda alohida olindi.
- DOM kontrakti: yuqori linklar `.subheader ul.breadcrumb a`; sibling
  navigatsiya `ng-click="a.openSibling(fs)"` orqali ishlaydi.
- `Администрирование`: 24 parent formadan 10 tasida jami 22 ta page-link:
  - `ТМЦ`: `Характеристики ТМЦ` → `anor/mr/product/inventory_group_list`;
    `Производители` → `anor/mr/product/producer_list`;
    `Единицы измерения` → `anor/mr/product/measure_list`;
    `Тип кейса (1 уровень)` → `anor/mr/product/box_type_list`;
    `Наборы ТМЦ` → `anor/mr/sector_list`;
    `Единицы измерения для Didox` →
    `anor/mr/product/didox_measure_list`.
  - `Цены`: `Типы оплат` → `anor/mkr/payment_type_list`;
    `Скидки/наценки` → `anor/mkr/margin_list`.
  - `Услуги`: `Характеристики услуг` →
    `anor/mr/product/service_group_list`.
  - `Вопросы`: `Тип вопроса` → `core/mqz/quiz_type_list`.
  - `Регионы`: `Регионы` → `anor/mfk/regions`.
  - `Физические лица`: `Характеристики физических лиц` →
    `anor/mr/person/natural_person_group_list`; `Регионы` →
    `anor/mr/region_list` (destination title `Страны`).
  - `Юридические лица`: `Характеристики юридических лиц` →
    `anor/mr/person/legal_person_group_list`; `Регионы` →
    `anor/mr/region_list` (destination title `Страны`); `Должности` →
    `anor/mr/person/contact_position_list`;
    `Организационно-правовые формы` → `anor/mr/legal_form_list`;
    `Виды деятельности` → `anor/mr/person/activity_list`.
  - `Акции`: `Конструктор отчетов по акциям` →
    `a2/anor/rep/mbi/mcg/action`.
  - `Публикация в бот`: `Пользователи телеграмм` →
    `trade/txs/telegram/user_list`; `Сообщения клиентов` →
    `trade/txs/telegram/person_message_list`.
  - `Минимальные обязательные ассортименты`: `Дашборд по MML` →
    `anor/mcg/mml_dashboard`.
- Operatsion filial: 36 parent formadan 15 tasida jami 33 ta page-link:
  - `ТМЦ`: `Характеристики ТМЦ` → `anor/mr/product/inventory_group_list`;
    `Производители` → `anor/mr/product/producer_list`;
    `Единицы измерения` → `anor/mr/product/measure_list`;
    `Тип кейса (1 уровень)` → `anor/mr/product/box_type_list`;
    `Наборы ТМЦ` → `anor/mr/sector_list`.
  - `Цены`: `Типы оплат` → `anor/mkr/payment_type_list`;
    `Скидки/наценки` → `anor/mkr/margin_list`.
  - `Услуги`: `Характеристики услуг` →
    `anor/mr/product/service_group_list`.
  - `Регионы`: `Регионы` → `anor/mfk/regions`.
  - `Продавцы`: `Пользователи` → `anor/mr/user_list`; `Штат` →
    `anor/mrf/robot_list`.
  - `Физические лица`: `Характеристики физических лиц` →
    `anor/mr/person/natural_person_group_list`; `Регионы` →
    `anor/mr/region_list` (destination title `Страны`);
    `Графики доставки` → `anor/mr/person/delivery_schedule_list`.
  - `Юридические лица`: `Характеристики юридических лиц` →
    `anor/mr/person/legal_person_group_list`; `Договоры` →
    `anor/mkf/contract_list`; `Регионы` → `anor/mr/region_list`
    (destination title `Страны`); `Должности` →
    `anor/mr/person/contact_position_list`;
    `Организационно-правовые формы` → `anor/mr/legal_form_list`;
    `Виды деятельности` → `anor/mr/person/activity_list`;
    `Графики доставки` → `anor/mr/person/delivery_schedule_list`.
  - `Отделы`: `Группы отделов` → `anor/mhr/division_group_list`.
  - `Должности`: `Группы должностей` → `anor/mhr/job_group_list`.
  - `Рабочие зоны`: `Тип рабочей зоны` → `anor/mrf/room_type_list`.
  - `Акции`: `Конструктор отчетов по акциям` →
    `a2/anor/rep/mbi/mcg/action`.
  - `Правила ограничений`: `Ограничения по клиенту` →
    `anor/mcg/client_order_restriction_list`.
  - `Продуктовая корзина`: `Продуктовые корзины по клиентам` →
    `anor/mrf/client_product_set_list`;
    `Продуктовые корзины по рабочим местам` →
    `anor/mrf/room_product_set_list`;
    `Продуктовые корзины по штатам` →
    `anor/mrf/robot_product_set_list`.
  - `Публикация в бот`: `Пользователи телеграмм` →
    `trade/txs/telegram/user_list`; `Сообщения клиентов` →
    `trade/txs/telegram/person_message_list`; `Регистрации через бот` →
    `trade/txs/telegram/registered_person_list`.
  - `Минимальные обязательные ассортименты`: `Дашборд по MML` →
    `anor/mcg/mml_dashboard`.
- Kesishma (`parent + page_link` track bo'yicha): 20 ta umumiy,
  faqat `Администрирование`da 2 ta:
  - `ТМЦ → Единицы измерения для Didox`;
  - `Вопросы → Тип вопроса`.
- Faqat operatsion filialda 13 ta:
  - `Продавцы → Пользователи`, `Продавцы → Штат`;
  - `Физические лица → Графики доставки`;
  - `Юридические лица → Договоры`,
    `Юридические лица → Графики доставки`;
  - `Отделы → Группы отделов`;
  - `Должности → Группы должностей`;
  - `Рабочие зоны → Тип рабочей зоны`;
  - `Правила ограничений → Ограничения по клиенту`;
  - `Продуктовая корзина`ning uchta page-linki;
  - `Публикация в бот → Регистрации через бот`.
- Barcha 55 ta filialdagi birinchi darajali page-link holati live bosildi va
  destination ochildi. Bu son nested sub-page-linklarni o'z ichiga olmaydi.
- Foydalanuvchi aniqlashtirgan qoida: page-link destination ochilgach, o'sha
  sahifadagi `.subheader ul.breadcrumb a` linklari ham rekursiv tekshiriladi;
  terminal sahifaga yoki avval ko'rilgan canonical path sikliga yetguncha
  har bir link alohida bosiladi.
- `Администрирование`da 4 ta ikkinchi darajali track topildi:
  - `ТМЦ → Наборы ТМЦ → ТМЦ` →
    `anor/mr/product/inventory_list` (parent formaga qaytuvchi sikl);
  - `Услуги → Характеристики услуг → Услуги` →
    `anor/mr/product/service_list` (parent formaga qaytuvchi sikl);
  - `Физические лица → Регионы` (title `Страны`) `→ Регионы` →
    `anor/mfk/regions` (terminal);
  - `Юридические лица → Регионы` (title `Страны`) `→ Регионы` →
    `anor/mfk/regions` (terminal).
- Operatsion filialda 9 ta ikkinchi darajali track topildi:
  - yuqoridagi 4 ta umumiy track;
  - `Продавцы → Пользователи → Все пользователи` →
    `anor/mr/all_users_list` (terminal);
  - `Продавцы → Пользователи → Роли` → `trade/tr/role_list`;
  - `Юридические лица → Договоры → Дополнительные договоры` →
    `anor/mkf/sub_contract_list` (terminal);
  - `Отделы → Группы отделов → Отделы` →
    `anor/mhr/division_list` (parent formaga qaytuvchi sikl);
  - `Правила ограничений → Ограничения по клиенту →
    Правила ограничений` → `anor/mcg/order_restriction_list`
    (parent formaga qaytuvchi sikl).
- `Продавцы → Пользователи → Роли` destinationida yana 2 ta uchinchi
  darajali track bor:
  - `→ Пользователи` → `anor/mr/user_list` (oldingi page-link sahifasiga
    qaytuvchi sikl);
  - `→ Запросы на доступ к действиям` →
    `biruni/md/access_request_list` (terminal).
- Ayrim parentlarda linklar async kech render bo'ladi; fixed qisqa delay
  linkni topmaslik yoki click no-op bo'lishiga olib keldi. Test har bosqichda
  loader/readinessdan keyin page-link yagona va ko'rinadigan bo'lishini kutib,
  clickdan keyin URL canonical path o'zgarganini tekshirsin. Volatile
  `#/!<token>/` qismi siklni aniqlashda hisobga olinmaydi.
- Yakuniy rekursiv test qamrovi: operatsion filialda 36 direct menu forma +
  33 birinchi darajali + 9 ikkinchi darajali + 2 uchinchi darajali track;
  `Администрирование`da `Вопросы` direct forma +
  `Вопросы → Тип вопроса` va `ТМЦ → Единицы измерения для Didox`.
  Adminning 4 ta nested tracki operatsion filialdagi umumiy tracklar bilan
  qoplangan. Jami 37 direct + 35 birinchi darajali + 9 ikkinchi darajali +
  2 uchinchi darajali = 83 ta navigation tekshiruvi.

## `Создать` dropdownidagi yashirin formalar (2026-07-29 live)

Tags: legacy, menu, create, dropdown, import, attach, local-code, page-link, filial, test

- Foydalanuvchi aniqlashtirgan qoida: list formadagi `Создать` tugmasi
  yonidagi dropdown actionlar ham alohida yashirin formalar hisoblanadi.
  Ularning destinationi ochilib title/URL bilan tekshiriladi; destinationdagi
  `page_links` ham terminal yoki canonical siklgacha rekursiv tekshiriladi.
- DOM kontrakti: haqiqiy create dropdown
  `.btn-group:has(button:text-is("Создать"))`; yashirin actionlar shu guruh
  ichidagi `a` linklar. Oddiy `Создать` buttonli, ammo shu guruhga ega bo'lmagan
  parentda yashirin forma yo'q. Dropdown yopiq bo'lsa ham action linklari DOMda
  turadi, lekin test avval toggle buttonni bosib, link visible bo'lgach click
  qilishi kerak.
- `Администрирование`: 5 parent formada 6 ta dropdown action:
  - `ТМЦ → Импорт` → `anor/mr/product/inventory_import`,
    title `ТМЦ (импорт)`;
  - `ТМЦ → Импорт фото` → `anor/mr/product/inventory_photo_import`,
    title `Импорт фото`;
  - `Цены → Импорт` → `anor/mkf/product_price_import`,
    title `Цены (импорт)`;
  - `Услуги → Импорт` → `anor/mr/product/service_import`,
    title `Услуги (импорт)`;
  - `Физические лица → Импорт` →
    `anor/mr/person/natural_person_import`,
    title `Физические лица (импорт)`;
  - `Юридические лица → Импорт` →
    `anor/mr/person/legal_person_import`,
    title `Юридические лица (импорт)`.
- Operatsion filial: 6 parent formada 11 ta dropdown action:
  - `Цены → Прикрепление` → `anor/mkr/price_type_list+attach`,
    title `Цены (прикрепление)`;
  - `Цены → Импорт` → `anor/mkf/product_price_import`,
    title `Цены (импорт)`;
  - `Физические лица → Прикрепление` →
    `anor/mr/person/natural_person_list+attach`,
    title `Физические лица (прикрепление)`;
  - `Физические лица → Импорт` →
    `anor/mr/person/natural_person_import`,
    title `Физические лица (импорт)`;
  - `Физические лица → Установка локального кода` →
    `anor/mr/person/set_natural_person_local_code`,
    title `Физические лица (установка локального кода)`;
  - `Юридические лица → Прикрепление` →
    `anor/mr/person/legal_person_list+attach`,
    title `Юридические лица (прикрепление)`;
  - `Юридические лица → Импорт` →
    `anor/mr/person/legal_person_import`,
    title `Юридические лица (импорт)`;
  - `Юридические лица → Установить локальный код` →
    `anor/mr/person/set_legal_person_local_code`,
    title `Юридические лица (установка локального кода)`;
  - `Рабочие зоны → Импорт рабочих зон` → `anor/mrf/room_import`,
    title `Рабочие зоны (импорт)`;
  - `Штат → Импорт` → `anor/mrf/robot_import`,
    title `Штат (импорт)`;
  - `Сеты ТМЦ → Прикрепление` → `anor/mr/product_kit_list+attach`,
    title `Сет ТМЦ (прикрепление)`.
- Kesishma (`parent + action` track bo'yicha): 3 ta umumiy:
  `Цены → Импорт`, `Физические лица → Импорт`,
  `Юридические лица → Импорт`.
- Faqat `Администрирование`da 3 ta:
  `ТМЦ → Импорт`, `ТМЦ → Импорт фото`, `Услуги → Импорт`.
- Faqat operatsion filialda 8 ta:
  `Цены → Прикрепление`;
  `Физические лица → Прикрепление/Установка локального кода`;
  `Юридические лица → Прикрепление/Установить локальный код`;
  `Рабочие зоны → Импорт рабочих зон`; `Штат → Импорт`;
  `Сеты ТМЦ → Прикрепление`.
- Faqat `Цены → Импорт` destinationida 3 ta page-link bor; ular ikkala
  filialda ham bir xil va har ikki kontekstda live bosildi:
  - `→ Цены` → `anor/mkr/price_type_list`; bu avval tekshirilgan parentga
    qaytuvchi canonical sikl, unda `Типы оплат` va `Скидки/наценки` linklari
    qayta ko'rinadi;
  - `→ Типы оплат` → `anor/mkr/payment_type_list` (terminal);
  - `→ Скидки/наценки` → `anor/mkr/margin_list` (terminal).
- Boshqa 13 ta unique hidden-form destinationida page-link yo'q. Bu natija
  har ikki filialda loader tugagach qo'shimcha readiness bilan qayta
  tasdiqlandi.
- Test strategiyasi: operatsion filialda 11 ta hidden action + `Цены →
  Импорт`ning 3 ta page-linki tekshiriladi; so'ng `Администрирование`da faqat
  u yerga xos 3 ta hidden action tekshiriladi. Umumiy 3 hidden action va
  import page-linklari Admin kontekstida testda qayta takrorlanmaydi.
- Oldingi 83 ta direct/page-link navigatsiyaga 14 ta unique hidden action va
  3 ta import page-link qo'shiladi: yakuniy rejalashtirilgan qamrov
  **100 ta navigation tekshiruvi**.
- Live auditda 17 ta filial-action instansi (Admin 6 + operatsion 11) ochildi;
  `Цены → Импорт`ning 3 ta page-linki ikkala filialda bosildi. Barcha
  destination title va canonical URLlari ochildi.
- Screenshot arxivi:
  `forms/screenshots/spravochniki-hidden-imports/`
  (14 ta unique hidden forma, 1440×722 JPEG).
- Screenshot fayllari:
  - `admin-inventory-import.jpg`
  - `admin-inventory-photo-import.jpg`
  - `admin-service-import.jpg`
  - `legal-person-import.jpg`
  - `natural-person-import.jpg`
  - `op-legal-person-attach.jpg`
  - `op-legal-person-local-code.jpg`
  - `op-natural-person-attach.jpg`
  - `op-natural-person-local-code.jpg`
  - `op-prices-attach.jpg`
  - `op-product-kit-attach.jpg`
  - `op-robot-import.jpg`
  - `op-room-import.jpg`
  - `prices-import.jpg`

## `Справочники` form-opening smoke verifikatsiyasi (2026-07-29)

Tags: spravochniki, test, run-result, canonical-url, screenshot

- Dated run evidence is pre-renumbering: its historical compatibility identity
  is `test_forms_01_spravochniki`; it must not be read as a Forms-05 run.
- Current Forms-05 leaf: `tests/smoke/test_forms/test_05_spravochniki_forms.py`.
- Muhit/filiallar: `app3.greenwhite.uz/xtrade`, operatsion
  `api_filial-232905` + `Администрирование`.
- Natija: 100/100 navigation OK, pytest `1 passed`, 256.97s.
- Qamrov: 37 direct menu forma, 35 birinchi darajali page-link, 9 ikkinchi
  darajali, 2 uchinchi darajali, 14 hidden dropdown forma va import ichidagi
  3 page-link.
- Screenshot:
  `forms/screenshots/spravochniki-navigation/spravochniki-navigation__operational-menu__desktop-2880x1566.png`.

### Vaqtincha qamrovdan chiqarilgan menu parentlari (2026-07-29)
Tags: spravochniki, test, temporary-exclusion, sellers, telegram

- Foydalanuvchi qarori bilan `Продавцы` va `Публикация в бот` parentlariga
  tegishli barcha direct/page-link yo'llar hozircha form-opening smoke testiga
  qo'shilmaydi.
- Implementatsiya:
  `tests/smoke/test_forms/inventory/skipped_forms.py` ichidagi `SKIPPED_FORMS` canonical
  pathlar bo'yicha markaziy reja tuzilishidan oldin filterlaydi.
- Qamrov ta'siri: 100 ta inventar yo'lidan 11 tasi chiqarilib, aktiv test
  qamrovi 89 ta navigatsiya bo'ldi.
- Bu o'zgarish UI inventarini bekor qilmaydi; menular qayta yoqilganda mos
  pathlarni skip registry'dan olib tashlash yetarli.

### Aktiv 89 forma va strukturali hisobot verifikatsiyasi (2026-07-29)
Tags: spravochniki, test, report, terminal, allure, run-result

- `Продавцы` va `Публикация в бот` yo'llari chiqarilgan aktiv qamrov
  `smartup.online`da **89/89 passed, 229.90s** natija berdi.
- Har bir Allure forma stepida filial, tab, menu va destination forma;
  ichki steplarda to'liq user yo'li, kutilgan URL va haqiqiy URL saqlanadi.
- Terminal yakuniy jadvali ham har bir aktiv forma uchun filial, tab, menu,
  forma va full URLni ko'rsatadi.
- Reporting-only o'zgarishda Smartup forma UI/state o'zgarmagani uchun yangi
  screenshot olinmadi; mavjud navigation screenshotlari aktual.

## `Продажа` mega-menu inventari (2026-08-04 live)

Tags: legacy, a2, menu, navbar, sales, visits, filial, administration, test
Status: live-ui-confirmed
Verified: 2026-08-04
Source: live UI

- Muhit: `smartup.online`, admin login; taqqoslash `Администрирование` va
  birinchi operatsion filialda bajarildi.
- `Администрирование`da 2 ta `menu_column`, jami 6 ta `menu_item` bor:
  - `Отчеты по продажам`: `Дашборд по продажам (БЕТА)`,
    `Конструктор отчётов по продажам`,
    `Общий отчет по продажам (организации)`;
  - `Отчеты по визитам`: `Конструктор отчётов по визитам`,
    `Анализ маршрута`, `Отчёт о маршруте пользователей`.
- Operatsion filialda 4 ta `menu_column`, jami 27 ta `menu_item` bor:
  - `Визиты` (9): `Визиты`, `Архив визитов`,
    `Отслеживание пользователей`,
    `Отслеживание мобильных представителей`, `Планирование визитов`,
    `Планы`, `Автоформирование плана визитов`,
    `Отслеживание оборудования`, `Фото- и видеоотчеты`;
  - `Продажа` (6): `Заказы`, `Архив заказов`, `Отмененные заказы`,
    `Возвраты`, `Взаиморасчеты с клиентами`, `Лиды`;
  - `Отчеты по продажам` (8): `Дашборд`, `Дашборд по продажам`,
    `Дашборд по продажам (БЕТА)`, `Конструктор отчётов по продажам`,
    `Общий отчет по продажам (организации)`,
    `Задолженность покупателей по срокам задолженности`,
    `Расчет бонуса за оплату долга`, `Коммерческий дашборд`;
  - `Отчеты по визитам` (4): `Конструктор отчётов по визитам`,
    `Отчет по визитам`, `Анализ маршрута`,
    `Отчёт о маршруте пользователей`.
- Kesishma: adminning barcha 6 itemi operatsion filialda ham bor;
  admin-only item yo'q, filial-only itemlar 21 ta. Direct forma ochilish
  coverage'i operatsion filialdagi 27 item bilan barcha unique yo'llarni
  qoplaydi.
- A2 direct yo'llar: `Визиты`, `Архив визитов`,
  `Отслеживание пользователей`,
  `Отслеживание мобильных представителей`, `Коммерческий дашборд`,
  `Конструктор отчётов по визитам`; qolganlari legacy shellga o'tadi.

### Qlik BETA dashboard vaqtincha skip
Tags: sales, qlik, dashboard, error, skip, test
Status: live-ui-confirmed
Verified: 2026-08-04
Source: user; live UI

- Qayerda: `Продажа → Отчеты по продажам → Дашборд по продажам (БЕТА)`,
  canonical path `trade/tdeal/qlik_sales_dashboard`.
- Live UI xatosi: `A01-02001 — Нет лицензии Qlik`; joriy foydalanuvchida
  amaldagi Qlik litsenziyasi yo'q.
- Foydalanuvchi qarori: forma vaqtincha umumiy `SKIPPED_FORMS` registry'sida
  saqlanadi va Forms-02 aktiv rejasiga kiritilmaydi.

## `Продажа` page-link va `+add` inventari (2026-08-04 live)

Tags: legacy, sales, page-link, add-icon, creation, cycle, error, test
Status: live-ui-confirmed
Verified: 2026-08-04
Source: user; live UI

- Operatsion filialdagi birinchi darajali `page_links`:
  - `Отслеживание оборудования → Архив` →
    `trade/tvt/equipment_review_history_list`;
  - `Заказы → Отказы` → `anor/mdeal/order/sales_return_list`;
  - `Заказы → Детали задолженности` →
    `anor/mdeal/order/offset/offset_detail_list`;
  - `Возвраты → Причины возврата` →
    `anor/mdeal/return/return_reason_list`;
  - `Взаиморасчеты с клиентами → Взаиморасчеты` →
    `anor/mku/offset/offset_list`;
  - `Дашборд по продажам → Дашборд команды продаж` →
    `trade/tdeal/sales_team_dashboard`.
- Rekursiv yo'llar:
  - `Отслеживание оборудования → Архив → Отслеживание оборудования`
    parent canonical pathiga qaytadi;
  - `Заказы → Детали задолженности → История взаиморасчетов` →
    `anor/mdeal/order/offset/offset_history_list`; undan
    `Детали задолженности`ga qaytish canonical cycle;
  - `Взаиморасчеты с клиентами → Взаиморасчеты → Парные счета` →
    `anor/mku/coa_twin_list`; undan `Взаиморасчеты`ga qaytish cycle;
  - `Дашборд по продажам → Дашборд команды продаж →
    Дашборд по продажам` parent canonical pathiga qaytadi.
- `Продажа` menu ustunida uchta matnsiz `+add` ikonka-link bor. DOM kontrakti:
  parent forma qatoridagi `a.menu-link.menu-link-icon`, `href`da `+add`:
  - `Заказы` → `anor/mdeal/order/order+add`, heading
    `Заказ (создание)`;
  - `Возвраты` → `anor/mdeal/return/return+add`, heading
    `Возврат (создание)`;
  - `Лиды` → `anor/mdeal/order/lead+add`, heading `Лид (создание)`.
- Foydalanuvchi qarori (2026-08-04): `+add` ikonka-link tekshiruvi Forms-02
  rejasidan butunlay olib tashlandi — creation formalari bu suite'da
  tekshirilmaydi. `add_icon=True` support flow/monitor/`base_page` da qoladi,
  lekin Forms-02 da hech qanday case uni ishlatmaydi. Sabab: admin roli
  creation formalarida hujjatni faqat `Черновик` statusida saqlay oladi, shuning
  uchun bu formalar doimo ogohlantirish beradi va smoke navigatsiya tekshiruvi
  uchun ma'noli signal bermaydi.
- Aktiv Forms-02 qamrovi: 26 direct (`BETA` skipdan keyin) + 12 rekursiv
  page-link/cycle = 38 navigation check.

### `Возврат (создание)` administrator draft ogohlantirishi
Tags: sales, return, add-icon, admin, draft, warning, test
Status: code-confirmed
Verified: 2026-08-04
Source: user; `tests/smoke/test_forms/monitoring/monitor.py`

- Qayerda: `Продажа → Продажа → Возвраты → +add`, canonical path
  `anor/mdeal/return/return+add`.
- Biznes qoida: `Проведение транзакции администратором невозможна...`
  alerti application error emas. U administrator hujjatni faqat `Черновик`
  statusida saqlashi mumkinligini bildiradigan kutilgan ogohlantirish.
- **Tuzatish (2026-08-05, o'lchov bilan):** alert **barcha uchta** creation
  formasida chiqmaydi — bu avvalgi yozuv xato edi:

  | `+add` formasi | Alert | Matn oxiri |
  |---|---|---|
  | `Заказы` → `order+add` | ✅ chiqadi | ...транзакции администратором **невозможно** |
  | `Возвраты` → `return+add` | ✅ chiqadi | ...транзакции администратором **невозможна** |
  | `Лиды` → `lead+add` | ❌ **chiqmaydi** | 15 s kutishda 3 marta — hech narsa |

  Ya'ni `Заказы` va `Возвраты` matnlari **bir harf bilan farq qiladi**
  (`невозможно` / `невозможна`), `Лиды` esa toza ochiladi.
- Joriy qaror (2026-08-06): FormMonitor'dagi eski `allowed_warnings`
  exceptioni olib tashlangan. Aniq hard-error komponenti ko'rinsa matnidan
  qat'i nazar `APPLICATION_ERROR`; generic `[role="alert"]` esa o'zicha hard
  error emas. Forms-02 dagi `+add` creation case'lar qamrovdan chiqarilgani
  uchun bu administrator warninglari joriy suite'da tekshirilmaydi.

### Alert bleed-through — mexanizm tasdiqlandi, trigger hozir yo'q (2026-08-05)
Tags: forms-monitor, alert, bleed-through, add-icon, reproduced
Status: trace-confirmed
Verified: 2026-08-05
Source: `+add` creation formalarida qo'lda o'lchov; o'sha paytdagi tarixiy
Forms-01 (`Справочники`, joriy Forms-05) va Forms-03 (`Продажа`, joriy
Forms-02) `--headless` runlari (88 + 38 forma)
- Gipoteza edi: forma N da chiqqan alert ekranda qolib, forma N+1 ni yolg'ondan
  `APPLICATION_ERROR` qiladi (2026-08-04 runda 039/040/041 alert matnlari bir
  qadam surilgan ko'rinardi).
- **Qayta ishlab chiqarildi (2026-08-05):** `Заказы → Возвраты → Лиды` `+add`
  ketma-ketligi, alert tozalanmagan holda:

  | Navigatsiya | O'qilgan matn | Kutish | Kimning alerti |
  |---|---|---|---|
  | `Заказы` | ...невозмож**но** | 867 ms | o'zining (cold) |
  | `Возвраты` | ...невозмож**но** | 25 ms | **`Заказы` ning** — o'zi `невозможна` bo'lishi kerak |
  | `Лиды` | ...невозмож**но** | 20 ms | **`Заказы` ning** — `Лиды` da alert umuman yo'q |

  Har forma orasida alert yopilgan holda esa `Возвраты` o'zining
  `невозможна` matnini berdi, `Лиды` esa 15 s kutishda hech narsa bermadi.
  Ya'ni 20–25 ms lik "darhol" o'qishlar — eski alert. Mexanizm **haqiqiy**,
  avval "tekshirib bo'lmaydi" deb yopilgan edi.
- Lekin **hozirgi qamrovda trigger yo'q**: Forms-05 `Справочники` (88 forma,
  shundan 8 ta `Импорт`/`Импорт фото` action formasi) va Forms-02 `Продажа`
  (38 forma) — jami
  **126 forma, 0 ta `APPLICATION_ERROR`**. Hech bir suite `add_icon` yoki
  creation warning ishlatmaydi.
- Qayta ko'rish sharti: suite'ga creation/`+add` forma qo'shilsa **yoki**
  hisobotda birinchi real `APPLICATION_ERROR` ko'rinsa. Endi bu "ehtimol" emas —
  o'sha kuni **albatta** yolg'on fail beradi.
- Joriy tozalash shakli: `check_application_error` Biruni selectorini
  qaytargandagina, **failure screenshoti olingandan keyin**, faqat shu modalning
  `button.close` tugmasi bosiladi. A2/inline error avtomatik o'zgartirilmaydi;
  har formada shartsiz Escape bosilmaydi.

### Legacy title check visible headingni exact talab qiladi (2026-08-06)
Tags: legacy, heading, title, forms-monitor
Status: trace-confirmed
Verified: 2026-08-06
Source: qayta raqamlashdan oldingi Forms-01 `Справочники` va Forms-03
`Продажа` `--headless` runlari;
`tests/smoke/test_forms/monitoring/checks/title.py`; user-approved title contract
- Trace dalili: hozirgi nomlarda Forms-05 (87 legacy) + Forms-02 (32 legacy) =
  **119 legacy formaning** barchasida visible `role=heading` topilgan.
- Joriy qoida: `check_title` expected forma nomini visible semantic headinglar
  orasidan whitespace-normalized exact kutadi. Heading yo'q yoki faqat partial
  match bo'lsa silent pass qilmaydi; `OPENED_WITH_DEFECT / TITLE_NOT_REACHED`.
- Eski `TITLE TAQQOSLANMAGAN FORMALAR` warning bo'limi va unverified-pass yo'li
  olib tashlangan. Oldingi gate failure bo'lsa title alohida `NOT_RUN` bo'ladi.
- A2 formalar boshqa source ishlatadi: `title_source=document_title`.

## `Склад` mega-menu inventari (2026-08-11 live)

Tags: legacy, a2, menu, navbar, warehouse, filial, administration, page-link, test
Status: live-ui-confirmed
Verified: 2026-08-11
Source: live UI

- Muhit: `smartup.online`; taqqoslash `Администрирование` va birinchi
  operatsion filialda bajarildi.
- `Администрирование`da ustun headingi DOMda ko'rinmaydi, jami 7 ta
  `menu_item` bor. Ularning barchasi operatsion filialdagi `Отчеты` ustunining
  A2 report-constructor formalaridir: ichki, purchase-request, purchase,
  input, writeoff, intercompany-request va intercompany movement hisobot
  konstruktorlari.
- Operatsion filialda 4 ta `menu_column`, jami 38 ta direct `menu_item` bor:
  `Документы` 13, `Перемещения` 8, `Справочники` 7, `Отчеты` 10.
- Kesishma 7 ta; admin-only item yo'q, filial-only item 31 ta. Operatsion
  filialdagi 38 direct formaning 30 tasi legacy, 8 tasi A2. Barcha direct
  formalarda title `menu_item` bilan exact teng chiqdi.

### Operatsion filial direct formalar

| `menu_column` | `menu_item` / title | canonical `path` | birinchi darajali `page_links` |
|---|---|---|---|
| Документы | Ввод начальных остатков ТМЦ | `anor/mkw/init_balance/init_inventory_balance_list` | Ввод начального баланса счетов; Ввод начального баланса клиентов; Ввод начального баланса поставщиков; Ввод начальных остатков оборудования клиентов |
| Документы | Запросы на закупку | `anor/mkw/purchase/purchase_request_list` | Причины запросов на закупку; Заказы на закупку |
| Документы | Заказы на закупку | `anor/mkw/purchase/order_list` | Закупки |
| Документы | Закупки | `anor/mkw/purchase/purchase_list` | Поступления ТМЦ на склад; Списания при закупке; Статус закупок; Прогноз для закупки |
| Документы | Дополнительные расходы | `anor/mkw/extra_cost_list` | Виды движения |
| Документы | Поступления ТМЦ на склад | `anor/mkw/input/input_list` | Закупки; Поставщики; Дополнительные расходы; Внутренние перемещения; Списания; Инвентаризации |
| Документы | Возвраты поставщику | `anor/mkw/return/return_list` | Причины возвратов поставщику |
| Документы | Списания | `anor/mkw/writeoff/writeoff_list` | Причины списаний; Виды движения; Внутренние перемещения; Инвентаризации |
| Документы | Инвентаризации | `anor/mkw/stocktaking/stocktaking_list` | Причины инвентаризации; Виды движения; Внутренние перемещения; Списания; Остатки ТМЦ; Инвентаризация склада |
| Документы | Переоценки себестоимости ТМЦ | `anor/mkw/revaluation/revaluation_list` | — |
| Документы | Взаиморасчеты с поставщиками | `anor/mkw/purchase/offset/offset_list` | — |
| Документы | Пересчет приходных цен | `anor/mkw/recalculate_input` | — |
| Документы | Прогноз для закупки | `anor/mfc/forecast_list` | — |
| Перемещения | Запросы на внутр. перемещения | `anor/mkw/movement/movement_request_list` | — |
| Перемещения | Внутренние перемещения | `anor/mkw/movement/movement_list` | Списания; Инвентаризации; Причины перемещений |
| Перемещения | Запросы на межорг. перемещ.: отправка | `anor/mfm/from_movement_request_list` | — |
| Перемещения | Запросы на межорг. перемещ.: прием | `anor/mfm/to_movement_request_list` | — |
| Перемещения | Межорг. перемещения: отправка | `anor/mfm/from_movement_list` | Причины перемещений |
| Перемещения | Межорг. перемещения: прием | `anor/mfm/to_movement_list` | — |
| Перемещения | Архив межорг. перемещений | `anor/mfm/from_movement_history_list` | — |
| Перемещения | Отмененные межорг. перемещения | `anor/mfm/cancelled_from_movement_list` | — |
| Справочники | Поставщики | `anor/mkw/supplier_list` | — |
| Справочники | Автотранспорт | `anor/mrf/van_list` | — |
| Справочники | Склады | `anor/mkw/warehouse_list` | Типы складов |
| Справочники | Остатки ТМЦ | `anor/mkw/balance/balance_list` | Настройки сроков годности; Рекламное оборудование; Рекомендованные остатки |
| Справочники | Логистика | `trade/tdeal/logistics_list` | — |
| Справочники | Рекламное оборудование | `anor/mkw/product_serials` | Остатки ТМЦ |
| Справочники | Документы WMS | `anor/mxsx/wms/document_list` | — |
| Отчеты | Материальный отчет | `anor/rep/mkw/warehouse_inventories` | — |
| Отчеты | Общий отчет по складам | `anor/rep/mkw/warehouse_balance/warehouse_balance` | — |
| Отчеты | Конструктор отчетов по внутр. перемещениям | `anor/rep/mbi/mkw/movement` | — |
| Отчеты | Конструктор отчетов по запросам на закуп | `anor/rep/mbi/mkw/purchase_request` | — |
| Отчеты | Конструктор отчетов по закупкам | `anor/rep/mbi/mkw/purchase` | — |
| Отчеты | Конструктор отчетов по поступлениям | `anor/rep/mbi/mkw/input` | — |
| Отчеты | Конструктор отчетов по списанию | `anor/rep/mbi/mkw/writeoff` | — |
| Отчеты | Конструктор отчетов по запросам на межорг. перемещения | `anor/rep/mbi/mfm/movement_request` | — |
| Отчеты | Конструктор отчетов по межорг. перемещениям | `anor/rep/mbi/mfm/movement` | — |
| Отчеты | Отчёт по отгрузкам и оплатам | `trade/rep/warehouse_and_delivery` | — |

### Birinchi darajali page-link targetlari

- 14 ta parentda 38 ta link ko'rindi; ular 28 ta unique canonical targetga
  olib boradi. Takror targetlar parentlar orasidagi canonical cycle/shortcutdir.
- Yangi unique targetlar:
  - `Ввод начального баланса счетов` → `anor/mku/init_balance/init_balance_list`;
  - `Ввод начального баланса клиентов` → `anor/mku/init_balance/init_client_balance_list`;
  - `Ввод начального баланса поставщиков` → `anor/mku/init_balance/init_supplier_balance_list`;
  - `Ввод начальных остатков оборудования клиентов` → `anor/mkw/init_balance/init_client_inventory_balance_list`;
  - `Причины запросов на закупку` → `anor/mkw/purchase/purchase_request_reason_list`;
  - `Списания при закупке` → `anor/mkw/purchase/purchase_writeoff_list`;
  - `Статус закупок` → `anor/mkw/purchase/purchase_status_list`;
  - `Виды движения` → `anor/mkw/corr_template_list`;
  - `Причины возвратов поставщику` → `anor/mkw/return/return_reason_list`;
  - `Причины списаний` → `anor/mkw/writeoff/reason_list`;
  - `Причины инвентаризации` → `anor/mkw/stocktaking/reason_list`;
  - `Инвентаризация склада` → `anor/mkw/stocktaking/stocktaking_ban_period_list`;
  - `Причины перемещений` ichki → `anor/mkw/movement/movement_reason_list`;
  - `Причины перемещений` intercompany → `anor/mfm/movement_reason_list`;
  - `Типы складов` → `anor/mkw/warehouse_type_list`;
  - `Настройки сроков годности` → `anor/pref/expiration_date`;
  - `Рекомендованные остатки` → `anor/mkw/balance/recommended_balance_list`.
- Qolgan page-linklar yuqoridagi direct canonical pathlardan biriga qaytadi:
  purchase/order/input/supplier/extra-cost/movement/writeoff/stocktaking/balance,
  forecast yoki product-serials. Test inventarida har bir user trace alohida
  case bo'lishi mumkin, lekin canonical duplicate guard trackni
  `parent + page_links` bilan birga baholashi kerak.
- Joriy operatsion filialda `Инвентаризации` breadcrumbida
  `Инвентаризация КМ` ko'rinmadi; mavjud A2 case oldingi muhitdagi dostup
  cheklovi sabab skip holatida qoladi.

### `Склад` Forms-03 qamrovi

Tags: forms-03, inventory, mixed-shell, runner
Status: code-confirmed
Verified: 2026-08-11
Source: `tests/smoke/test_forms/inventory/sklad.py`;
`tests/smoke/test_forms/test_03_sklad_forms.py`;
`tests/smoke/test_forms/test_0_forms_runner.py`

- Forms-03 shell turiga qarab ajratilmaydi: `Склад` navbaridagi legacy va A2
  formalar bitta navbar suite'da tekshiriladi.
- Aktiv reja 76 ta navigatsiya: operatsion filialda 38 direct + 38 page-link.
  Shell kesimida 68 legacy va 8 A2 navigatsiya bor.
- `Администрирование`dagi 7 A2 report konstruktori operatsion filialda ham bor,
  shuning uchun Forms-03 ularni admin filialida ikkinchi marta tekshirmaydi.
  Admin filialidan faqat operatsion filialda topilmagan formalar qo'shiladi;
  joriy inventarda admin-only forma yo'q.
- `Инвентаризация КМ` inventarda saqlanadi, ammo umumiy skip registry sabab
  bitta intentional skip bo'lib qoladi.
- Shu A2 formalar standalone `test_a2_angular_forms.py` inventarida ham bo'lishi
  mumkin. Bu dublikat xato emas: Forms-03 navbar qamrovini, A2Angular esa barcha
  navbarlardagi A2 texnologiya qamrovini jamlaydi.

## `Финансы` mega-menu inventari (2026-08-11 live)

Tags: legacy, a2, menu, navbar, finance, filial, administration, page-link, test
Status: live-ui-confirmed
Verified: 2026-08-11
Source: smartup.online live Chromium UI; tests/smoke/test_forms/inventory/finansy.py

- Operatsion filialda 42 ta direct forma bor: `Основное` 13,
  `Денежный поток` 4, `Справочники` 6 va `Отчеты` 19.
- Rekursiv `page-link` user trace'lari 67 ta; eng chuqur trace depth'i besh.
  Aktiv reja direct va recursive trace'larni birga hisoblaganda 109 ta
  navigatsiyani, 58 ta unique canonical pathni qamraydi.
- Shell kesimida aktiv reja 106 legacy va 3 A2 navigatsiyadan iborat.
- `Администрирование`da 8 ta direct forma bor; ularning sakkalasi operatsion
  filial bilan overlap qiladi. Admin-only direct yoki page-link yo'l yo'q.
- `Обороты по контрагентам(6006)` title'i aynan shu bo'shliq va qavslar bilan
  yoziladi.
- Intentional skip yo'q.
- Approved design-spec A2 yo'llari: `anor/rep/mbi/mkcs/operation`,
  `anor/rep/mkr/pnl`, `anor/rep/mku/balance_sheet`.

### `Финансы` Forms-04 qamrovi

Tags: forms-04, inventory, mixed-shell, runner
Status: code-confirmed
Verified: 2026-08-11
Source: `tests/smoke/test_forms/inventory/finansy.py`;
`tests/smoke/test_forms/test_04_finansy_forms.py`;
`tests/smoke/test_forms/test_0_forms_runner.py`

- Current Forms-04 suite `Финансы` navbarining legacy va A2 navigation
  qamrovini bitta navbar ownershipida bajaradi.

## `Главное` mega-menu inventari (2026-08-11 live)

Tags: legacy, a2, menu, navbar, main, filial, administration, page-link, test
Status: live-ui-confirmed
Verified: 2026-08-11
Source: live UI

- Muhit: `smartup.online`; birinchi operatsion filial va
  `Администрирование` filiali taqqoslandi.
- Operatsion filialda 3 ta `menu_column` va 11 ta direct forma bor:
  `Основное` 4, `Дополнительное` 6, `Отчеты` 1. Shell kesimida 10 legacy va
  1 A2 forma.
- `Администрирование`da shu 3 ta ustunda 14 ta direct forma bor:
  `Основное` 4, `Дополнительное` 9, `Отчеты` 1. Shell kesimida 12 legacy va
  2 A2 forma.
- Direct canonical kesishma 10 ta. Operatsion-only forma `Проекты`;
  admin-only formalar `Лицензии`, `Подключения к системе`,
  `Клиенты OAuth2 сервера для компании` va `Регистры вебхуков`.
- Bir canonical direct forma ikkala filialda ko'rinsa Forms suite uni faqat
  operatsion filialda ochadi. Admin bucketda faqat yuqoridagi 4 admin-only
  parent va ulardan topilgan admin-only page-link qoladi.

### Operatsion filial direct formalar

| `menu_column` | `menu_item` / title | canonical `path` | shell | birinchi darajali `page_links` |
|---|---|---|---|---|
| Основное | Организации | `anor/mr/filial_list` | legacy | — |
| Основное | Пользователи | `anor/mr/user_list` | legacy | Все пользователи; Роли |
| Основное | Проекты | `anor/mrf/subfilial_list` | legacy | — |
| Основное | Шаблоны накладных | `anor/mr/template_list` | legacy | — |
| Дополнительное | Настройки системы | `trade/pref/system_setting` | legacy | Аппараты фискализации; Настройки сервисов доставки |
| Дополнительное | История изменений | `biruni/md/audit_list` | legacy | — |
| Дополнительное | Шаги визита | `trade/tph/role_list` | legacy | Пользователи; Роли |
| Дополнительное | Настройки интеграции со сторонним ПО | `trade/txs/external_settings` | A2 | Экспорт заказа |
| Дополнительное | Объекты | `biruni/kdyn/entity_list` | legacy | — |
| Дополнительное | Динамичные поля | `biruni/kdyn/field_list` | legacy | — |
| Отчеты | Отчeты | `anor/rep/report_list` | legacy | — |

### Admin-only direct va page-link formalar

| `menu_column` | `menu_item` / title | canonical `path` | shell | `page_links` |
|---|---|---|---|---|
| Основное | Лицензии | `biruni/kl/license_list` | legacy | — |
| Дополнительное | Подключения к системе | `biruni/kauth/session_list` | legacy | — |
| Дополнительное | Клиенты OAuth2 сервера для компании | `biruni/kauth/company_client_list` | A2 | — |
| Дополнительное | Регистры вебхуков | `core/kwh/register_list` | legacy | Логи вебхуков |

### Rekursiv page-link trace'lar

- Operatsion filialda 17 ta trace:
  - `Пользователи → Все пользователи` → `anor/mr/all_users_list`;
  - `Пользователи → Роли` → `trade/tr/role_list`;
  - `Пользователи → Роли → Пользователи` → `anor/mr/user_list` (cycle);
  - `Пользователи → Роли → Запросы на доступ к действиям` →
    `biruni/md/access_request_list`;
  - `Настройки системы → Аппараты фискализации` →
    `anor/mrf/fiscal_cash_register_list`;
  - `Настройки системы → Настройки сервисов доставки` →
    `trade/txs/delivery_service_setting`;
  - `Шаги визита → Пользователи` branchida `Пользователи`,
    `Все пользователи`, `Роли`, `Роли → Пользователи` cycle va
    `Роли → Запросы на доступ к действиям` — 5 ta trace;
  - `Шаги визита → Роли` branchida `Роли`, `Пользователи`,
    `Пользователи → Все пользователи`, `Пользователи → Роли` cycle va
    `Запросы на доступ к действиям` — 5 ta trace;
  - `Настройки интеграции со сторонним ПО → Экспорт заказа` →
    `trade/txso/order_export`.
- Admin-only parentlardan 1 ta trace:
  `Регистры вебхуков → Логи вебхуков` → `core/kwh/log_list`.
- `Лицензии` ichidagi tablar va `Отчeты` kategoriyalari canonical route'ni
  o'zgartirmaydi; ular alohida forma destination sifatida inventoryga
  qo'shilmaydi.

### `Главное` Forms-01 qamrovi

Tags: forms-01, inventory, mixed-shell, runner
Status: code-confirmed
Verified: 2026-08-11
Source: `tests/smoke/test_forms/inventory/glavnoe.py`;
`tests/smoke/test_forms/test_01_glavnoe_forms.py`;
`tests/smoke/test_forms/test_0_forms_runner.py`

- Aktiv reja 33 ta navigatsiya: operatsion filialda 11 direct + 17
  page-link, `Администрирование`da 4 admin-only direct + 1 page-link.
- Shell kesimida 31 legacy va 2 A2 case; 33 trace 22 ta unique canonical
  pathni qamraydi.
- `Настройки интеграции со сторонним ПО` va
  `Клиенты OAuth2 сервера для компании` standalone A2Angular inventarida ham
  qoladi; Forms-01 esa ularni `Главное` navbar ownershipi bo'yicha qamraydi.
- Skip registry exact `navbar_tab + menu_item + path` trace'iga scope qilinadi.
  Shu sabab `Справочники → Продавцы` uchun chiqarilgan `Пользователи`,
  `Роли` va ularning nested targetlari `Главное` trace'larini noto'g'ri
  bloklamaydi.

## Group-0 moliyaviy sahifalari (2026-07-31 live)

Tags: legacy, navigation, finance, sales, client-payment, client-offset
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- `Финансы > Основное > Оплаты от клиентов`:
  `*/trade/tcs/cashin_list`; listdagi `Создать` actioni
  `*/trade/tcs/cashin+add` va `Оплата от клиента / Создание` headingini
  ochadi.
- `Продажа > Продажа > Взаиморасчеты с клиентами`:
  `*/anor/mdeal/order/offset/offset_list`.
- Testda ishlatish: `base.navigate_to`da exact navbar tab va exact menu item
  matnlarini ishlat; ikkala forma turli top-level tabda joylashgan.
