# Order Add Wizard (order+add / order+edit)

3 qadamli order yaratish/o'zgartirish wizard'i. MCP bilan jonli tekshirilgan
(`user-pw{code}@<company>`, 2026-06-12).

## Mundarija

- [URL va navigation](#url--navigation)
- [Modul ID](#anor279-modul-id)
- [Step 1](#step-1--main-page)
- [Step 2](#step-2--product-page)
- [Step 3](#step-3--final-page)
- [Flow/helper/test fayllari](#ishlatiladigan-flowhelpertest-fayllari)
- [Known issues](#known-issues--debug-notes)

## URL / Navigation
- Navigation: `Продажа > Заказы` → `Создать` (yoki list `flow_order_list(page, add=True)`).
- URL: `*/anor/mdeal/order/order+add` (yangi), `*/anor/mdeal/order/order+edit` (edit).
- Content heading: `Заказ (создание)` / `Заказ (изменение)`.
- Qadamlar tugmasi: `#anor279-button-next_step` (step 1-2 da "ДАЛЕЕ", oxirgi stepda "СОХРАНИТЬ"),
  orqaga `#anor279-button-prev_step`. Save tugmasida `fa-save` ikonka bor →
  `get_by_role("button", name="Сохранить", exact=True)` 0 element topadi; `exact_button=False` kerak.

## anor279 Modul ID
- Order wizard moduli ID = **`anor279`** (autotest deploymentida barqaror).
- Bu Smartup modul/forma kodi — boshqa deployment/versiyada **boshqacha bo'lishi mumkin**. Agar order add
  locatorlari to'satdan butunlay topilmasa, birinchi navbatda `anor279` prefiksining hali to'g'riligini tekshir
  (`document.querySelectorAll('[id^="anor279"]')`).
- ID prefiksida nomuvofiqlik bor: ba'zi step-1 elementlari `anor279-input-...`, product step esa
  `anor279_input-...` (underscore). Payment type wrapper id'da typo: `anor279-inpu-b_input-payment_type`
  (shuning uchun payment type label orqali tanlanadi, id orqali emas).

## Step 1 — Main page
- Stabil id'li date inputlar: `#anor279-input-deal_time` (`d.deal_time`),
  `#anor279-input-delivery_date` (`d.delivery_date`). Date inputlarda `min`/`max` atribut **yo'q**.
- 2026-07-21 live runida wizard DOMida `BasePage.input(label="Дата заказа")` fieldni topmadi; date qiymatlarini raw locator bilan emas, stabil IDni helperga berib `base.input(locator="#anor279-input-deal_time", ...)` va `base.input(locator="#anor279-input-delivery_date", ...)` orqali o'qish/tekshirish kerak.
- b-input wrapperlari (`div`, ichida `input[placeholder="Поиск..."]`):
  - `#anor279-input-b_input-room_name` — label "Рабочая зона*", `d.room_name`
  - `#anor279-input-b_input-robot_name` — label "Штат*", `d.robot_name`
  - `#anor279-input-b_input-person_name` — label "Клиент*", `d.person_name`
  - `#anor279-input-b_input-subfilial_name` — label "Проект", `d.subfilial_name`
  - `#anor279-input-b_input-contract_name` — label "Договор", `d.contract_name`
- **Auto-fill**: user-pw{code} bilan kirilganda room/robot/client default qiymatlari avtomatik to'ladi
  (room-pw{code} / robot-pw{code} / natural_client-pw{code}). `check_form=True` shuni `expect(...).to_have_value(...)`
  bilan tekshiradi (auto-retry — timing barqaror).
- b-input search role: input placeholder "Поиск..." → `get_by_role("textbox", name="Поиск")` (substring match) ishlaydi.
- Date labellar list/forma textida: "Дата заказа" (deal_time), "Дата отгрузки" (delivery_date).

## Step 2 — Product page
- Product b-input: `#anor279_input-b_input-product_name_goods0` (tag `b-input`, underscore!).
- Product grid: `#anor279_input-b_pg_grid-goods_items` (tag `b-pg-grid`).
- Quantity input: `#anor279_input-b_pg_col-quantity_0` (`item.quantity`) — **product tanlanmaguncha mavjud emas**,
  qator yaratilgach paydo bo'ladi.
- 2026-07-22 Chrome MCP live DOM: birinchi ko'rinadigan product grid `b-pg-grid[name="goods_items"]`; product `Название` headeri ostidagi `b-input`, quantity esa aniq `Кол-во` headeri ostidagi `input[ng-model="item.quantity"]`. Public helperlar ikkalasini header koordinatasi orqali topadi: `base.b_input(label="Название", ..., root=product_grid)` va `base.input(label="Кол-во", ..., root=product_grid)`. Shu sabab flowda `anor279` row IDlari kerak emas.
- **Product dropdown (flaky bo'lgan joy):**
  - Search bosilganda b-input ichida `.hint` ochiladi: `.hint-header` (Название/Цена/Остаток ustunlari) + `.hint-item` qatorlar.
  - Option matni **kombinatsiyalangan**: `"product-pw{code}  Основной склад  Price Type ...  7 000"` —
    product nomi **alohida text node emas**. Shuning uchun `page.get_by_text(product)` page-wide bo'lib bir nechta
    elementga tushadi va dropdown ochilishini kutmaydi → flaky.
  - **To'g'ri pattern** (`flow_order_product_page`):
    ```python
    product_input = page.locator("#anor279_input-b_input-product_name_goods0")
    search = product_input.get_by_role("textbox", name="Поиск")
    search.click(); search.fill(product)
    option = product_input.locator(".hint-item").filter(has_text=product).first
    expect(option).to_be_visible(); option.click()
    expect(product_input.locator("input").first).to_have_value(product)
    ```
  - `.hint-item` ni bosish to'g'ridan-to'g'ri qatorni tanlaydi (name cell ichiga emas).

## Step 3 — Final page
- Payment type b-input: `d.payment_type_name`, label "Тип оплаты" → `b_input("Тип оплаты", value=...)` (label orqali, id'da typo bor).
- Status ui-select: `#anor279-ui_select-status` (div), ichida "Select box activate" (`.ui-select-toggle`),
  optionlar `.ui-select-choices-row-inner`. Default "Новый". Tanlash va assert uchun
  `base.ui_select(label="Статус", value=...)` / `expect_value=...` ishlatiladi.
- Final summarydagi `ИТОГО` `.form-view` qiymati minglik probel bilan formatlanadi (`7 000`); testda `form_view(label="ИТОГО", expect_value="7000", remove_spaces=True)` ishlatib format whitespace'ini e'tiborsiz qilish mumkin.
- Final summarydagi `Клиент` qiymati step 1 dagi `natural_client-pw{code}`; `natural_person-pw{code}` esa alohida `Торговый представитель` qiymati, ularni assertionda almashtirib yubormaslik kerak.
- Save: `#anor279-button-next_step` matni "СОХРАНИТЬ" (`nextStep()`).
  Ikonka sabab default partial match bilan `base.click(name="Сохранить")`, keyin
  `base.confirm_biruni(expected_text="Сохранить?")` va
  `base.expect_page(heading="Заказы", url="order_list")`.

### Konsignatsiya kartasi (consignment enabled bo'lsa)
- Faqat `Главное > Настройки системы > Заказ` da `Разрешить консигнацию` yoqilgan bo'lsa ko'rinadi (`Разрешить выдачу консигнации` — eski UI matni).
- Inputlar: `item.consignment_date` (label "Дата оплаты по консигнации", placeholder "Выбрать дату"),
  `item.consignment_amount` (label "Сумма консигнации"). `+` qo'shish: `button[ng-click="addConsignment()"]`.
- Split rowlar dinamik `ng-repeat` bilan yaratiladi; bir nechta rowda qiymat kiritish/tekshirish uchun `BasePage.input(ng_model="item.consignment_date", index=...)` va `BasePage.input(ng_model="item.consignment_amount", index=...)` ishlatiladi. Labeldan `following input` topish save requestda faqat oxirgi row qolishiga olib kelgan holat trace orqali tasdiqlangan.
- **30 kunlik limit qayerda (MUHIM):**
  - Limit DOM textida YOKI date input atributida (`max`) **ko'rinmaydi**.
  - Faqat AngularJS scope'da: **`q.consignment_day_limit`** = "30". (`q.consignment_allow`="Y", `q.total_amount`=5×narx.)
  - **`d.max_consignment_date` degan field YO'Q** — max sana client-side hisoblanadi (delivery_date + limit), scope'da saqlanmaydi.
    (Eski orders.md notasi `d.max_consignment_date` deb yozgan edi — bu noto'g'ri.)
  - Scope'ni o'qish: `item.consignment_date` inputidan `angular.element(el).scope()` olib, `$parent` zanjirida `q.consignment_day_limit` qidiriladi (`order_helpers._consignment_day_limit`).
- **Eski flaky bug**: `_consignment_limit_state` page'dan o'qimasdan `"30"` + `datetime.today()+30` qaytarardi; bu
  `delivery_date+30` bilan solishtirilib, `today != delivery_date` bo'lganda (timezone/midnight/auto-inc delivery)
  AssertionError berardi. Tuzatildi: limit `q.consignment_day_limit` dan o'qiladi, max sana esa formadagi haqiqiy
  `delivery_date` + limit dan hisoblanadi.

## Ishlatiladigan flow va test fayllari
- Flowlar: `tests/smoke/flows/flow_order/flow_order_add.py` (main/product/final), `flow_order_list.py` (list/add/find_row/view/edit/status).
- Avvalgi Group A/B order testlari 2026-07-31 kuni o'chirilgan; yangi testlar qaytadan yoziladi.
- Group-0 base order:
  - `tests/smoke/test_groups/test_a_grup/test_01_create_base_order.py`
  - `tests/smoke/test_groups/test_a_grup/test_0_group_runner.py`

## Known issues / debug notes
- Product chiqmasligi → balans/booking; orders.md "Product Chiqmasa" bo'limiga qara.
- `anor279` prefiksi deploymentga bog'liq — locator butunlay topilmasa avval shuni tekshir.

### Product grid headeri asinxron render bo'ladi
Tags: order, product, grid, locator, base-page
Status: trace-confirmed
Verified: 2026-07-31
Source: `test-results/traces/tests_smoke_test_groups_test_0_grup_test_create_base_order.py__test_create_base_order.zip`
- Qayerda: step 1 dan step 2 ga `Далее` orqali o'tilgandan keyingi
  `b-pg-grid[name="goods_items"]`.
- Qoida: grid screenshot/DOMda paydo bo'lishidan oldingi birinchi immediate
  `count()` headerlar uchun `0` qaytarishi mumkin; header matnida NBSP ham bor.
- Testda ishlatish: `BasePage` grid-header fallbacki birinchi header
  ko'rinishini auto-retry bilan kutadi va header textini whitespace/NBSP
  bo'yicha normallashtiradi. Leaf test raw sleep yoki stabil modul IDiga
  qaytmaydi.

## 2026-07-31 Live UI Qo'shimchalari

### Step 1 field va permission holatlari
Tags: order, add, edit, main-step, permission, locator
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `*/anor/mdeal/order/order+add`, wizard step 1.
- Qoida: `deal_time` va `delivery_date` required; room, robot, client,
  project va contract `b-input`lari mavjud. Robot/client auto-fill qilinishi,
  project/contractning required yoki readonly bo'lishi user grant va joriy
  kontekstga bog'liq.
- Testda ishlatish: fieldning faqat ko'rinishini emas, har bir grant profilida
  required/readonly holati, auto-fill qiymati va step o'tish validatsiyasini
  alohida assert qilish kerak.

### Step 2 item turlari va bo'sh order validatsiyasi
Tags: order, product, service, material, promotion, validation
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: order wizard step 2.
- Qoida: tablar `Товар`, `Сырье`, `Продукция`, `Услуга`, `Нагрузка`,
  `Рекомендации`, `Акции`, `Промо`. TMC tablarida `Подбор`, `Импорт`,
  balance-ignore, search/Typesense va paged grid bor. Hech qanday TMC
  pozitsiyasi qo'shilmasdan davom etilganda `H02-ANOR279-004` va
  `Для продолжения добавьте несколько позиций ТМЦ` xatosi chiqadi.
- Testda ishlatish: har bir inventory kind uchun add/select/import oqimini,
  xizmat va marketing tablarini hamda bo'sh order negative case'ini alohida
  qoplash kerak.

### Product qatori hisob-kitob va split-card boshqaruvlari
Tags: order, product, grid, quantity, margin, split-card
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: order wizard step 2, `goods_items`.
- Qoida: mahsulot tanlangach warehouse, price type, price va stock ko'rinadi;
  `quantity`, shartli `quantity_box`, discount/margin, remove va split-card
  boshqaruvlari paydo bo'ladi. Tanlangan mahsulotdan keyin yangi bo'sh qator
  avtomatik yaratiladi.
- Testda ishlatish: miqdor/case miqdori o'zaro bog'liqligi, stock cheklovi,
  row va order summalari, remove, duplicate va split-card grantlarini tekshir.

### Step 3 logistika, marking va statuslar
Tags: order, final-step, delivery, marking, status, locator
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: order wizard step 3.
- Qoida: final qadamda payment type, order-level discount/margin, shartli
  booked payment va consignment, `Номер ТТН` (maxlength 20),
  `Номер счёт-фактуры` (maxlength 50), expeditor, qisqa/to'liq manzil,
  GPS xarita, marking attach method, van, note va status mavjud.
  Status variantlari: `Черновик`, `Новый`, `В обработке`, `В ожидании`,
  `Отгружен`, `Доставлен`, `Архив`.
- Testda ishlatish: har bir shartli blokni feature flag/grant bilan, maxlength
  chegaralarini, xarita save/close/clear oqimini va status variantlarini
  tekshir.

### Final summary item viewlari
Tags: order, final-step, summary, grid
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: order wizard step 3 summary.
- Qoida: summary `ТМЦ`, `Услуга`, `Нагрузка`, `Рекомендации`, `Промо`,
  `Акция`, `Обмен` kesimlarini, pozitsiya/SKU/miqdor va gross/net weight
  totalini ko'rsatadi. TMC view gridida kod, nom, card, expiry, quantity,
  new price, amount, margin, VAT, payable amount, alternative name va
  barcode ustunlari bor.
- Testda ishlatish: step 2 dagi har bir item turi va hisob natijasini final
  summary hamda saqlangandan keyingi view bilan uch tomonlama solishtir.

## User-reported

### Project va contract optionlarining test data dependency'si
Tags: order, add, project, contract, setup, dependency
Status: user-reported
Verified: pending
Source: user
- Qoida: joriy test muhitida order add formasidagi `Проект` va `Договор`
  maydonlarida tanlanadigan test data yo'q; mos project/contract entitylari
  yaratilgandan keyin optionlar order add formasida ko'rinishi kutiladi.
- Testda ishlatish: project/contract bir nechta independent case uchun bir xil
  shared baseline bo'lsa setupda yaratish; aks holda har testcase o'z Arrange
  qismida unique entity yaratadi. Sibling group testcase yaratgan `data_store`
  keyni consumer sifatida o'qimaslik; live UI bilan tasdiqlanmaguncha bu
  entryni current truth sifatida ishlatmaslik.
