# Smartup legacy formalar navigatsiya katalogi

## Mundarija

- [Klassifikatsiya qoidasi](#klassifikatsiya-qoidasi)
- [Справочники mega-menu inventari](#справочники-legacy-mega-menu-inventari-2026-07-29-live)
- [Справочники page-link inventari](#справочники-page-link-inventari-2026-07-29-live)
- [Создать dropdownidagi yashirin formalar](#создать-dropdownidagi-yashirin-formalar-2026-07-29-live)
- [Form-opening smoke verifikatsiyasi](#справочники-form-opening-smoke-verifikatsiyasi-2026-07-29)

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
- Joriy katalogning tekshirilgan scope'i `navbar_tab="Справочники"`.
  Keyingi navbar inventarlari ham shu faylga alohida bo'lim sifatida qo'shiladi.

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

- Test: `tests/smoke/test_forms/test_spravochniki_menu_forms.py`.
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
  `tests/smoke/test_forms/test_spravochniki_menu_forms.py` ichidagi
  `TEMPORARILY_EXCLUDED_MENU_ITEMS` parent bo'yicha filterlaydi.
- Qamrov ta'siri: 100 ta inventar yo'lidan 11 tasi chiqarilib, aktiv test
  qamrovi 89 ta navigatsiya bo'ldi.
- Bu o'zgarish UI inventarini bekor qilmaydi; menular qayta yoqilganda
  constantdan nomlarni olib tashlash yetarli.

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
