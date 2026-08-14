# Smartup Order Test Coverage Catalog

Status: mixed evidence; proposed coverage
Verified: 2026-07-31
Source: Smartup live UI; repository flow/testlari;
`skills/smartup-guide/references/forms/` dossierlari

Bu reference Order regression risklari va stable `ORD-*` testcase IDlari uchun
canonical backlog. Undagi testcase expected resultlari avtomatik current product
truth emas: implementatsiyadan oldin tegishli form dossieri va joriy kod/UI
bilan qayta tasdiqlanadi. Actual automation coverage source of truth'i joriy
setup/group runnerlaridir.

Verified UI date: **2026-07-31**

Scope:

- `order_list`
- `order+add`
- `order+edit`
- order view va row actions
- table/widget `view setting`
- `product_list`
- `order_import`

Dalil manbalari:

- smartup.online live UI: add wizardning 3 qadami, list, filter, table/widget
  settings, `product_list`, `order_import`;
- repo flow/testlari: add-edit-view-status, contract limit/payment type,
  consignment, save-as-edit va invoice reportlar;
- `skills/smartup-guide/references/forms/` dossierlari.

Muhim cheklov: tekshirilgan filialda list bo'sh bo'lgani uchun edit/view
row-level UI qayta yaratilmagan. Bu qism amaldagi Playwright flowlari va
2026-07-21 trace-confirmed dossierga tayangan. Import fayli yuklanmadi va hech
qanday order/setting saqlanmadi; importdagi server validatsiyalari quyida
tekshirilishi kerak bo'lgan test case sifatida berilgan.

## Priority modeli

- **P0** — har build/deployda ishlaydigan smoke; order yaratish yoki asosiy
  hisob-kitob buzilsa release blocker.
- **P1** — to'liq regression; feature, permission, validation va persistence.
- **P2** — extended/edge; katta data, parallelizm, compatibility va UX.

## Test data va precondition matritsasi

| Data | Kerakli variantlar |
|---|---|
| User | full-access; view-only; add-only; edit-only; report-only; split-card va ignore-balance grantsiz/grantli |
| Client | active; inactive; delivery addressli; manfiy/ijobiy balance; contractli/contractsiz |
| Contract | limitsiz; limit ichida; limitdan oshgan; payment type berilgan; muddati tugagan/inactive |
| Product | stock yetarli; stock 0; stock miqdordan kam; case quantityli; card/expiryli; VATli; markingli; action/promo bilan |
| Item kind | goods, material, produce, service, overload, recommendation, action, promo, exchange |
| Warehouse/price | active/inactive warehouse; active/inactive price type; narxi bor/yo'q; turli currency |
| Order | har bir statusda kamida bittadan; oddiy, split-card, consignment, marking, delivery address/GPSli |
| Import files | valid `.xls`; valid `.xlsx`; wrong extension; empty; mixed valid/invalid rows; duplicate rows; katta fayl |
| Locale/time | Asia/Tashkent midnight atrofi; turli browser timezone; RU UI |

Test data izolyatsiyasi:

1. Har run uchun `code` bilan unikal client/product/order note ishlating.
2. Shared user view setting testini parallel ishlatmang yoki alohida user
   ajrating.
3. Stock bookingga ta'sir qilgan orderlarni teardown'da mavjud status flow
   orqali `Отменен`ga o'tkazing.
4. Har destructive setting testidan keyin `По умолчанию` yoki oldingi snapshotni
   tiklang.

## Yuqori darajadagi ssenariylar

1. Role/grant bo'yicha order moduliga kirish va action visibility.
2. List search/filter/widget/grid/report/status oqimlari.
3. Add step 1 header data, auto-fill, contract va date validatsiyasi.
4. Add step 2 barcha item kindlar, stock, quantity, margin va calculation.
5. Add step 3 payment, consignment, logistics, marking, status va save.
6. View/edit data round-trip va status lifecycle.
7. Table/widget setting persistence va isolation.
8. `product_list` orqali ommaviy tanlash/filter/totallar.
9. `order_import` Excel mapping, parse va row-level errors.
10. Cross-form consistency, concurrency, timezone, performance va recovery.

## Bu testlar aynan nimalarni tekshiradi

| Tekshiriladigan qism | Test nimani isbotlaydi | Qanday xatoni ushlaydi |
|---|---|---|
| Ruxsatlar | User faqat o'z roliga ruxsat berilgan list, create, edit, status, report va settings actionlarini ishlata olishini | Yashirin actionga URL/request orqali kirish, boshqa filial ma'lumotini ko'rish yoki o'zgartirish |
| Order list | Search, filter, sort, pagination, widget va grid bir xil order datasetini ko'rsatishini | Noto'g'ri row, stale count/amount, sana yoki status filterining xato ishlashi |
| Add step 1 | Order sanasi, yetkazish sanasi, room, staff, sales rep, client, project va contract to'g'ri auto-fill/validate qilinishini | Required fieldni bo'sh o'tkazish, client va sales repni almashtirib yuborish, noto'g'ri contract |
| Contract va balance | Contract payment type, balance va limit order summasiga to'g'ri tatbiq etilishini | Limitdan oshgan orderning saqlanishi, failed save'dan keyin balance kamayishi |
| Add step 2 | Goods, material, produce, service, overload, recommendation, action va promo itemlari qo'shilishini | Item tablari orasida data yo'qolishi, duplicate product, blank orderni davom ettirish |
| Stock va quantity | Quantity, case quantity, stock, ignore-balance va split-card qoidalarini | Stockdan ortiq sotish, case conversion xatosi, card/expiry bo'yicha noto'g'ri split |
| Hisob-kitob | Price × quantity, discount/markup, VAT, payable amount, SKU/position va weight totalini | Noto'g'ri rounding, marginni ikki marta hisoblash, promo/action totalini double-count qilish |
| Add step 3 | Payment type, consignment, TTN/invoice, expeditor, address, GPS, marking, van, note va statusni | Maxlength buzilishi, shartli fieldning noto'g'ri ko'rinishi, GPS/address yoki marking data yo'qolishi |
| Save | Confirm, cancel, double-click, network/server error va retry xavfsizligini | Bir clickdan ikki order yaratilishi, failed save'da form data yo'qolishi |
| View | Saqlangan order ID, header, items, payment, contract, status va totals create form bilan bir xil ekanini | UI save bo'ldi deb ko'rsatib, backendda boshqa qiymat saqlanishi |
| Edit | Mavjud order qiymatlari prefill bo'lishi va editdan keyin aynan shu order ID yangilanishini | Edit o'rniga yangi order yaratish, product/contract yoki totalning eski qiymatda qolishi |
| Status lifecycle | Draft→New→In Process→Waiting→Shipped→Delivered va taqiqlangan o'tishlarni | Noto'g'ri transition, cancel qilinganda status o'zgarishi, stock bookingning qaytmasligi |
| Table/widget settings | Column add/remove/reorder/default va widget position/metriclari user scope'da saqlanishini | Settingning boshqa userga o'tishi, reload'da yo'qolishi, widget va grid totalining mos kelmasligi |
| Product list | Warehouse/price type kontekstida available→selected tanlash, filter va summaryni | Noto'g'ri stock/price, tanlangan mahsulotning ikki marta wizardga qaytishi |
| Order import | `.xls/.xlsx`, mapping, identify mode, row range, valid/error rows va wizardga transferni | Noto'g'ri file qabul qilish, Excel rowni boshqa productga bog'lash, error row numberning xato chiqishi |
| Integratsiya va NFR | Add/import/select natijalari parity, parallel edit, timezone, security, accessibility va performance'ni | Lost update, sana siljishi, XSS/injection, katta data sabab freeze yoki timeout |

Qisqasi, katalog faqat tugma ochilishini tekshirmaydi. Har muhim operatsiyada
quyidagi zanjir isbotlanadi:

1. UI kerakli qiymatni ko'rsatadi va validatsiya qiladi.
2. Save/request faqat ruxsatli va valid ma'lumotni qabul qiladi.
3. List, widget va reportlar saqlangan natijani to'g'ri hisoblaydi.
4. View backendda haqiqatan nima saqlanganini tasdiqlaydi.
5. Edit shu orderni yo'qotmasdan yangilaydi.
6. Xato/cancel/retry holati duplicate yoki qisman saqlangan order qoldirmaydi.

## A. Access, navigation va grantlar — 8 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-ACC-001 | P0 | Full-access user bilan `Продажа > Заказы`ni ochish. | `Заказы`, `order_list`, grid va ruxsatli toolbar actionlari ochiladi. |
| ORD-ACC-002 | P1 | View-only user bilan list va mavjud orderni ochish. | List/view bor; create/edit/status/settings mutation actionlari yo'q yoki disabled. |
| ORD-ACC-003 | P1 | Add-only user bilan `Создать` va save oqimini tekshirish. | Add ishlaydi; boshqa orderni edit/status qilish berilmaydi. |
| ORD-ACC-004 | P1 | Edit grantli va grantsiz userni solishtirish. | `Редактировать` faqat grantli user row menu'sida mavjud. |
| ORD-ACC-005 | P1 | Split-card va ignore-balance grantlarini ikki userda tekshirish. | Control visible/disabled holati grantga mos; backend grantni chetlab o'tishga yo'l qo'ymaydi. |
| ORD-ACC-006 | P1 | Report-only grant bilan individual va bulk report actionlarini tekshirish. | Ruxsatli reportlar bor; order mutation actionlari berilmaydi. |
| ORD-ACC-007 | P1 | Boshqa filial orderiga URL orqali kirishga urinish. | Cross-filial data ochilmaydi; access error yoki xavfsiz redirect. |
| ORD-ACC-008 | P2 | Deep-link add/edit/product_list/import URLlarini login bo'lmagan sessiyada ochish. | Login talab qilinadi; autentifikatsiyadan so'ng faqat ruxsatli forma ochiladi. |

## B. Order list — 22 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-LST-001 | P0 | Listni ochish va default columnsni tekshirish. | Room, client, staff, order/delivery date, currency, amount, status ko'rinadi. |
| ORD-LST-002 | P0 | Unikal client/room bo'yicha search. | Faqat mos row(lar), to'g'ri amount/status; clear qilinganda barcha rowlar qaytadi. |
| ORD-LST-003 | P1 | Searchda to'liq, qisman, registr va maxsus belgili qiymatlar. | Search kontraktiga mos natija; UI/server error yo'q. |
| ORD-LST-004 | P1 | Typesense toggle bilan bir xil qidiruvni qaytarish. | Har mode natijasi izchil yoki farqi biznes qoidaga mos. |
| ORD-LST-005 | P1 | Room, staff, sales rep va manager filterlarini bittalab qo'llash. | Har filter faqat mos rowlarni qaytaradi. |
| ORD-LST-006 | P1 | Order date va delivery date range: same day, boundary, empty side. | Inclusive/exclusive chegaralar belgilangan kontraktga mos, timezone siljishi yo'q. |
| ORD-LST-007 | P1 | Amount min/max va teng chegara. | Currency/formatdan qat'i nazar to'g'ri rowlar. |
| ORD-LST-008 | P0 | Har status bo'yicha filter: Draft...Delivered. | Tanlangan status rowlari va widget count/amount mos. |
| ORD-LST-009 | P1 | Source filterining barcha ko'rinadigan variantlari. | Har source faqat o'z orderlarini ko'rsatadi. |
| ORD-LST-010 | P1 | Bir nechta filter kombinatsiyasi, so'ng `Показать все`. | AND kombinatsiyasi to'g'ri; reset barcha filterlarni tozalaydi. |
| ORD-LST-011 | P1 | Filter template yaratish/default qilish/qayta ochish. | Template saqlanadi, qayta login/reloadda tiklanadi, boshqa userga oqmaydi. |
| ORD-LST-012 | P1 | Grid sortni date, amount, status va clientda asc/desc. | Barqaror va data-tipiga mos sort; pagination bilan izchil. |
| ORD-LST-013 | P1 | Pagination first/next/last va page-size. | Row yo'qolmaydi/takrorlanmaydi; count to'g'ri. |
| ORD-LST-014 | P1 | Reload button va pinned filter panel. | Data yangilanadi; panel holati kutilgancha saqlanadi. |
| ORD-LST-015 | P0 | Row tanlab `Просмотр`, `Редактировать`, `Изменить статус`. | Action aynan tanlangan rowga ishlaydi; yashirin/boshqa row tanlanmaydi. |
| ORD-LST-016 | P0 | Statusni New→In Process→Waiting→Shipped→Delivered o'tkazish. | Har confirm `Изменить статус на <status>?`; list/view status bir xil. |
| ORD-LST-017 | P1 | Noto'g'ri status o'tishi va confirm cancel. | Invalid transition serverda rad; cancel hech narsani o'zgartirmaydi. |
| ORD-LST-018 | P1 | `Создать`, beta create, retail create va create dropdown variantlari. | Har action to'g'ri formaga o'tadi va bir-birining state'ini aralashtirmaydi. |
| ORD-LST-019 | P1 | Summary widgetlar: total, gross/net, liter, all orders. | Count/amount/measure grid dataset bilan mos. |
| ORD-LST-020 | P1 | Payment type/status widget qiymatini bosish. | Grid shu segmentga filterlanadi; active state va clear ishlaydi. |
| ORD-LST-021 | P1 | Individual va bulk HTML/XLSX reportlardan representative subset. | To'g'ri selected order(lar), template va content-disposition; 0 selectionda xavfsiz validation. |
| ORD-LST-022 | P2 | `Чаты`, audit, export, change price type, custom invoice template actionlari. | Ruxsat va selection count to'g'ri; action target order IDs bilan ishlaydi. |

## C. Add step 1 — 14 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-A1-001 | P0 | Addni ochib heading, URL va 3-step wizardni tekshirish. | `Заказ (создание)`, `order+add`; first step aktiv. |
| ORD-A1-002 | P0 | Default `deal_time` va `delivery_date`. | Tashkent bugungi sana/vaqt formatida; kutilmagan bir kun siljish yo'q. |
| ORD-A1-003 | P0 | Room, staff, client va sales rep auto-fill. | User attachmentga mos qiymatlar; client va sales rep adashmaydi. |
| ORD-A1-004 | P1 | Required fieldni grantli userda birma-bir tozalab `Далее`. | Field-level validation, step 2 ga o'tmaydi, fokus/xabar tushunarli. |
| ORD-A1-005 | P1 | Room/client/robot readonly holatini grantsiz userda tekshirish. | UI o'zgartirishga yo'l bermaydi; DOM/request orqali bypass serverda rad. |
| ORD-A1-006 | P1 | Order date valid, future, old, noto'g'ri format qiymatlari. | Permission va date biznes qoidasi bo'yicha accept/reject. |
| ORD-A1-007 | P1 | Delivery date order date'dan oldin, teng va keyin. | Oldingi sana rad; teng/keyingi sana qabul qilinadi yoki aniq biznes xabari. |
| ORD-A1-008 | P1 | Clientni almashtirish. | Contract/balance/payment/product context eski clientdan qolmaydi. |
| ORD-A1-009 | P1 | Project/subfilial required va optional deployment variantlari. | Required bo'lsa blank o'tmaydi; readonly value current contextga mos. |
| ORD-A1-010 | P1 | Active, inactive, expired va boshqa client contractlarini qidirish. | Faqat ruxsatli/mos contract tanlanadi; invalid contract saqlanmaydi. |
| ORD-A1-011 | P0 | Contract balance ichida va limitdan oshuvchi orderga tayyorlash. | Contract/balance context final savegacha saqlanadi; over-limit alohida validation oladi. |
| ORD-A1-012 | P1 | Client balance buttonini ochish/yopish. | To'g'ri client va currency balanslari; order state yo'qolmaydi. |
| ORD-A1-013 | P1 | Step 1→2→1 round-trip. | Barcha qiymatlar o'zgarmasdan qoladi; auto-fill qayta noto'g'ri trigger bo'lmaydi. |
| ORD-A1-014 | P2 | Browser back/refresh/network retry vaqtida unsaved step 1. | Duplicate order yo'q; app aniq recovery/unsaved behavior ko'rsatadi. |

## D. Add step 2 — 29 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-A2-001 | P0 | Hech qanday TMC qo'shmay `Далее`. | `H02-ANOR279-004` va bir nechta TMC qo'shish xabari; step o'zgarmaydi. |
| ORD-A2-002 | P0 | Goods inline b-inputdan mahsulot tanlash. | Product rowda warehouse, price type, price, stock chiqadi va yangi blank row yaratiladi. |
| ORD-A2-003 | P0 | Goods quantity=1. | Row amount/payable va final total `price × quantity`ga mos. |
| ORD-A2-004 | P1 | Quantity 0, blank, negative, decimal, juda katta, text. | Faqat product UOM qoidasi bo'yicha valid qiymat qabul; xato summaga kirmaydi. |
| ORD-A2-005 | P1 | Quantity stockga teng, stockdan 1 ko'p va stock 0. | Balance enforcement grant/statusga mos; oversell yashirincha saqlanmaydi. |
| ORD-A2-006 | P1 | Ignore-balance grantli userda oversell order. | Toggle ishlaydi; warning/audit va save natijasi biznes qoidaga mos. |
| ORD-A2-007 | P1 | Ignore-balance grantsiz userda UI va request bypass. | Control disabled; backend oversellni rad etadi. |
| ORD-A2-008 | P1 | Case quantityli productda `quantity_box`. | Case va base quantity conversion aniq; birini o'zgartirish ikkinchisini to'g'ri hisoblaydi. |
| ORD-A2-009 | P1 | Bir productni ikki marta tanlash. | Biznes qoidaga ko'ra merge yoki duplicate validation; total ikki marta tasodifiy oshmaydi. |
| ORD-A2-010 | P1 | Ikki product, turli price/stock/VAT. | Har row va grand total aniq, SKU/position count to'g'ri. |
| ORD-A2-011 | P1 | Row remove va barcha rowlarni remove. | Total/count darhol kamayadi; blank order keyingi stepga o'tmaydi. |
| ORD-A2-012 | P1 | Row percent discount va amount discount boundarylari. | Discount base amountdan oshmaydi; rounding va payable to'g'ri. |
| ORD-A2-013 | P1 | Row percent/amount markup. | Positive markup va summary to'g'ri; permissionga mos control. |
| ORD-A2-014 | P1 | Order-level va row-level marginni keyingi step bilan kombinatsiya. | Belgilangan calculation orderi bo'yicha bitta marta qo'llanadi. |
| ORD-A2-015 | P1 | Split-cardni yoqish va card/expiryli mahsulot tanlash. | Card/expiry kesimlari ajraladi; jami quantity/amount o'zgarmaydi. |
| ORD-A2-016 | P1 | Split-cardni o'chirish yoki grantsiz user. | Rowlar biznes qoidaga ko'ra birlashadi/disabled; data yo'qolishi haqida aniq xulq. |
| ORD-A2-017 | P1 | Goods `Подбор`dan bir nechta mahsulot qaytarish. | Wizard gridida tanlangan rowlar va quantities aynan bir marta paydo bo'ladi. |
| ORD-A2-018 | P1 | Goods `Импорт`dan valid rowlarni qaytarish. | Import context/values wizardga o'tadi; totals inline selection bilan bir xil. |
| ORD-A2-019 | P1 | Search pagination va Typesense bilan product topish. | Barcha paged data ichidan to'g'ri product; dropdown duplicate locator xatosi yo'q. |
| ORD-A2-020 | P1 | `Сырье` tabida select/import/quantity/remove. | `material_items` qoidalari va final summary material kesimiga mos. |
| ORD-A2-021 | P1 | `Продукция` tabida select/import/quantity/remove. | `produce_items` va summary izchil. |
| ORD-A2-022 | P1 | `Услуга` qo'shish, quantity, price, margin va VAT. | Stock talab qilinmaydi; service amount/VAT/payable to'g'ri. |
| ORD-A2-023 | P1 | `Нагрузка` ma'lumotini qo'shish/o'chirish. | Extra data order bilan bog'lanadi va final summaryda ko'rinadi. |
| ORD-A2-024 | P1 | `Рекомендации`ni ochish va tanlash. | Client/order contextga mos tavsiya; selected state saqlanadi. |
| ORD-A2-025 | P1 | `Акции` eligible va ineligible orderlarda. | Faqat mos action qo'llanadi; benefit va final total to'g'ri. |
| ORD-A2-026 | P1 | `Промо` itemlar va gift/promo hisobini tekshirish. | Promo rowlar alohida kesimda; to'lanadigan sumga qoidaga mos ta'sir. |
| ORD-A2-027 | P1 | Mixed order: goods+service+action+promo. | Tablararo state yo'qolmaydi; totals double-count qilinmaydi. |
| ORD-A2-028 | P2 | 100+ product row, pagination/search va calculation performance. | UI responsive; total/count to'g'ri; request timeout/duplicate row yo'q. |
| ORD-A2-029 | P2 | Step 2 refresh/back/rapid double click on `Далее`. | Bir marta transition; duplicate request/order yo'q, state recovery aniq. |

## E. Add step 3 va save — 25 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-A3-001 | P0 | Payment type tanlash, status Draft va save. | `Сохранить?` confirm; listda bitta order va to'g'ri amount/status. |
| ORD-A3-002 | P0 | Contract payment type auto-fill. | Contractdagi payment type chiqadi; viewda ham saqlanadi. |
| ORD-A3-003 | P1 | Auto-filled payment typeni boshqa active typega almashtirish. | Ruxsat bo'lsa yangi type saqlanadi; contract/total buzilmaydi. |
| ORD-A3-004 | P1 | Blank/inactive payment type bilan save. | Required/business validation; invalid ID request bilan saqlanmaydi. |
| ORD-A3-005 | P0 | Har ko'rinadigan status bilan save parametrik testi. | Tanlangan status list va viewda aynan saqlanadi; ruxsatsiz status rad. |
| ORD-A3-006 | P1 | Order-level percent discount: 0, boundary, excessive. | Rounding va payable to'g'ri; negative totalga yo'l yo'q. |
| ORD-A3-007 | P1 | Order-level amount discount/markup va row margin bilan kombinatsiya. | Calculation orderi izchil, summary breakdown aniq. |
| ORD-A3-008 | P1 | Booked prepayment allowed/disabled va negative client balance. | Conditional block faqat feature/conditionda; invalid amount disabled/rad. |
| ORD-A3-009 | P0 | Consignment enabled: bitta valid date/amount. | Delivery date + allowed limit ichida save; viewda qiymatlar to'g'ri. |
| ORD-A3-010 | P1 | Consignment max boundary va +1 kun. | Boundary qabul; limitdan keyingi sana aniq error. |
| ORD-A3-011 | P1 | Bir nechta consignment row, sum totalga teng/kam/ko'p. | Rowlar yo'qolmaydi; invalid aggregate rad; edit/view round-trip to'g'ri. |
| ORD-A3-012 | P1 | Consignment disabled org. | `Консигнация ... запрещена`; input orqali bypass saqlanmaydi. |
| ORD-A3-013 | P1 | TTN number 0/20/21 chars va Unicode. | 20 gacha saqlanadi; 21 truncation yoki validation kontrakti aniq. |
| ORD-A3-014 | P1 | Invoice number 0/50/51 chars. | 50 gacha saqlanadi; 51 uchun xavfsiz behavior. |
| ORD-A3-015 | P1 | Expeditor auto-fill va boshqa active expeditor tanlash. | Ruxsatga mos; view/list custom column qiymati bir xil. |
| ORD-A3-016 | P1 | Short address 200/201 chars va full address multiline. | Maxlength va Unicode/newline round-trip to'g'ri. |
| ORD-A3-017 | P1 | GPS mapni ochish, coordinate qidirish, save-and-close. | To'g'ri lat/lng inputga yoziladi va view/editda saqlanadi. |
| ORD-A3-018 | P1 | GPS map close without save va clear. | Close eski qiymatni o'zgartirmaydi; clear qiymatni olib tashlaydi. |
| ORD-A3-019 | P1 | Marking attach method `Заказ` va `Автотранспорт`. | Feature yoqilganda selection saqlanadi; view/list setting column mos. |
| ORD-A3-020 | P1 | Van selection self-shipment/delivery shartlarida. | Van faqat tegishli holatda required/visible; stale van qolmaydi. |
| ORD-A3-021 | P1 | Note: blank, Unicode, emoji, HTML/SQL-like text, katta matn. | Xavfsiz saqlanadi/validatsiya; viewda escaped, XSS yo'q. |
| ORD-A3-022 | P0 | Contract limit ichidagi va limitdan oshgan total. | Limit ichida save; over-limit `Сумма заказа превышает...`, order yaratilmaydi. |
| ORD-A3-023 | P0 | Final summaryni step 2 bilan solishtirish. | SKU/position/qty, gross/net, VAT, margin va payable barcha kesimlarda mos. |
| ORD-A3-024 | P1 | Save confirmni cancel, keyin qayta save; double click. | Cancel mutation qilmaydi; yakunda faqat bitta order. |
| ORD-A3-025 | P2 | Save vaqtida server 4xx/5xx/network uzilishi, retry. | Error tushunarli; form state saqlanadi; retry duplicate order yaratmaydi. |

## F. Edit, view va lifecycle — 15 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-EDT-001 | P0 | Yaratilgan orderni `Просмотр`da ochish. | ID, dates, status, room, staff, client, payment, items va total create bilan mos. |
| ORD-EDT-002 | P0 | `Редактировать`ni ochib 3 qadam prefillini tekshirish. | URL `order+edit?deal_id=...`; barcha qiymatlar yo'qolmagan. |
| ORD-EDT-003 | P0 | Quantityni edit qilib save. | Shu order ID saqlanadi; amount/list/view yangi qiymatga yangilanadi. |
| ORD-EDT-004 | P1 | Editda product add/remove va item kind almashtirish. | Final summary va view faqat yangi item setni ko'rsatadi. |
| ORD-EDT-005 | P1 | Client/contractni editda almashtirish. | Payment, limits, price/stock context qayta hisoblanadi; stale data yo'q. |
| ORD-EDT-006 | P1 | Date/delivery/expeditor/address/GPS edit. | Permissionga mos fieldlar o'zgaradi va round-trip saqlanadi. |
| ORD-EDT-007 | P1 | Draft, New va keyingi statuslarda editable field matrix. | Status/grantga mos readonly/action visibility; server enforcement bor. |
| ORD-EDT-008 | P1 | Delivered/Archive/Cancelled orderni edit qilishga urinish. | Biznes qoidaga mos blok yoki cheklangan edit; audit iz qoladi. |
| ORD-EDT-009 | P1 | Editda consignment rowlarni add/remove/change. | Limit/aggregate qayta validatsiya; row index yo'qolmaydi. |
| ORD-EDT-010 | P1 | Editni save qilmasdan close/back. | Original order o'zgarmaydi; unsaved warning kontrakti izchil. |
| ORD-EDT-011 | P1 | Ikki sessiyada bir orderni parallel edit. | Lost update yo'q: optimistic lock/error yoki aniq last-write policy. |
| ORD-EDT-012 | P1 | Viewdagi barcha item tablari va totals. | Add/final bilan bir xil data, correct formatting va card/expiry rows. |
| ORD-EDT-013 | P1 | View close orqali listga qaytish. | Avvalgi search/filter/page imkon qadar saqlanadi; to'g'ri row ko'rinadi. |
| ORD-EDT-014 | P1 | Status confirm cancel va ketma-ket valid transitions. | Cancel state'ni o'zgartirmaydi; har transition audit/viewda aks etadi. |
| ORD-EDT-015 | P2 | View/edit direct URL invalid, deleted yoki boshqa filial deal_id. | Data leak yo'q; 404/access error yoki xavfsiz list redirect. |

## G. Table, widget va order settings — 22 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-VST-001 | P0 | `Настройка таблицы: Заказы`ni ochish. | Default selected fields va additional fields listi ko'rinadi. |
| ORD-VST-002 | P0 | `ИД заказа` ustunini qo'shib save. | Listda ID column paydo bo'ladi va row qiymati view IDga mos. |
| ORD-VST-003 | P1 | Bitta optional columnni remove qilib save. | Faqat shu column yo'qoladi; data/server o'zgarmaydi. |
| ORD-VST-004 | P1 | Selected columnsni reorder qilib save. | List column order aynan setting orderiga mos. |
| ORD-VST-005 | P1 | Bir columnni ikki marta qo'shishga urinish. | Duplicate selected column yaratilmaydi. |
| ORD-VST-006 | P1 | `По умолчанию` reset va confirm behavior. | Default 8 columns qaytadi; reloadda saqlanadi. |
| ORD-VST-007 | P1 | Settingni o'zgartirib `Закрыть` without save. | List oldingi configurationda qoladi. |
| ORD-VST-008 | P1 | ID, client, TTN va owner search-setting checkboxlari. | Global grid search faqat enabled fieldlarda qidiradi. |
| ORD-VST-009 | P1 | Invoice/TTN/marking/consignment/audit custom columns. | Har column to'g'ri backend field va row bilan map qilinadi. |
| ORD-VST-010 | P1 | Setting reload, logout/login va boshqa browser sessiyasi. | Shu user preference saqlanadi; boshqa userga o'tmaydi. |
| ORD-VST-011 | P1 | Widget modalda position Top→Bottom va save. | Widget bar listning pastiga o'tadi va reloadda saqlanadi. |
| ORD-VST-012 | P1 | Total orders, gross/net va liters widgetlarini alohida toggle. | Faqat yoqilgan widgetlar ko'rinadi; grid data o'zgarmaydi. |
| ORD-VST-013 | P1 | All-deals parent va quantity/amount child kombinatsiyalari. | Parent-child dependency va ko'rsatilgan metriclar aniq. |
| ORD-VST-014 | P1 | Status parent va quantity/amount child kombinatsiyalari. | Kerakli status cards/metriclar; drill-down ishlaydi. |
| ORD-VST-015 | P1 | Payment type parent va quantity/amount child kombinatsiyalari. | Kerakli cards/metriclar; values grid bilan mos. |
| ORD-VST-016 | P1 | Widget modalni save qilmasdan close. | Oldingi widget configuration o'zgarmaydi. |
| ORD-VST-017 | P1 | Table setting va widget setting isolation. | Birini save/reset qilish ikkinchisiga ta'sir qilmaydi. |
| ORD-VST-018 | P2 | Ikki tabda bir user settingini parallel o'zgartirish. | Deterministik conflict/last-write behavior; corrupt preference yo'q. |
| ORD-VST-019 | P1 | Order settingsda draft-day blank, 0, negative, decimal, text va valid kun. | Faqat ruxsatli qiymat saqlanadi; label/izohga emas, backend status natijasiga mos ishlaydi. |
| ORD-VST-020 | P1 | Draft-day thresholdning pastida, aynan chegarada va undan keyingi orderlar. | Scheduled status change faqat biznes qoidasidagi vaqt/statusga tatbiq etiladi; boshqa orderlar o'zgarmaydi. |
| ORD-VST-021 | P1 | Client delivery address toggle off/on bilan yangi va edit order. | Off/on holatida address tanlash/saqlash biznes qoidasiga mos; preference reload/login'da persist. |
| ORD-VST-022 | P1 | Consignment responsible toggle off/on, save va modal close without save. | Conditional field/validation faqat saved on holatida; cancel oldingi settingni saqlaydi. |

## H. Product list — 20 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-PLS-001 | P0 | Goods stepdan `Подбор`ni ochish. | Headingda client; query contextdagi room/inventory kind saqlanadi. |
| ORD-PLS-002 | P0 | Warehouse va price type tanlab available productsni yuklash. | Mos narx/stockli productlar keladi; required state yo'qoladi. |
| ORD-PLS-003 | P1 | Warehouse blank yoki price type blank holatda selection/close. | Required validation; contexti to'liq bo'lmagan row wizardga o'tmaydi. |
| ORD-PLS-004 | P1 | Warehouse almashtirish. | Stock/card list yangi warehousega yangilanadi; eski selection qoidaga mos reset/reprice. |
| ORD-PLS-005 | P1 | Price type almashtirish. | Price va selected amount qayta hisoblanadi; stale price yo'q. |
| ORD-PLS-006 | P0 | Available rowga quantity berib Selected tabga o'tish. | Product bir marta selectedda, quantity/price/stock mos. |
| ORD-PLS-007 | P1 | Selected quantityni edit qilish va 0 ga tushirish. | Totals yangilanadi; 0 row remove/invalid behavior izchil. |
| ORD-PLS-008 | P1 | Case quantity conversion. | Base/case quantity va amount wizard bilan bir xil. |
| ORD-PLS-009 | P1 | Selecteddan productni olib tashlash. | Availablega qaytadi; totals/count kamayadi. |
| ORD-PLS-010 | P1 | Bir nechta product selection va close. | Wizardga barcha rowlar aynan bir marta, to'g'ri orderda o'tadi. |
| ORD-PLS-011 | P1 | Close without any selection va existing wizard rows bilan. | Existing rows yo'qolmaydi; yangi row qo'shilmaydi. |
| ORD-PLS-012 | P1 | Search exact/partial va Typesense mode. | To'g'ri available/selected rowlar, pagination bilan izchil. |
| ORD-PLS-013 | P1 | Filter text operatorlari: equal/not equal/search/exclude. | Har operator kutilgan product setni qaytaradi. |
| ORD-PLS-014 | P1 | Group/category/brand/manufacturer equal/not equal. | Categorical filterlar to'g'ri va kombinatsiyalanadi. |
| ORD-PLS-015 | P1 | Combined filters, apply, show-all, close. | AND result to'g'ri; show-all reset; close unapplied state'ni saqlamaydi. |
| ORD-PLS-016 | P1 | Selected summary: SKU, positions, qty, weight, amount, margin, revaluation. | Qiymatlar rowlardan mustaqil qayta hisoblanganda mos. |
| ORD-PLS-017 | P1 | Split-card on/off va card/expiry product. | Selected/wizard rows kartalar bo'yicha to'g'ri split/merge. |
| ORD-PLS-018 | P1 | Ignore-balance on/off va insufficient stock. | Grant/balance qoidasi wizard inline oqimi bilan bir xil. |
| ORD-PLS-019 | P1 | Initial warehouse/price setting save, reuse va delete. | Yangi ochishda setting tiklanadi; delete'dan keyin default/blank behavior. |
| ORD-PLS-020 | P2 | 500+ available va 100+ selected products. | Filter/pagination responsive; totals, close transfer va memory barqaror. |

## I. Order import — 23 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-IMP-001 | P0 | Goods stepdan `Импорт`ni ochish. | `Заказ (импорт ТМЦ)`, inventory kind/client context to'g'ri. |
| ORD-IMP-002 | P0 | Valid `.xlsx`, warehouse/price type bilan upload. | Valid products gridga parse; row count/fields faylga mos. |
| ORD-IMP-003 | P0 | Valid `.xls`ni upload. | `.xlsx` bilan funksional parity. |
| ORD-IMP-004 | P1 | Button va drag/drop orqali aynan bir fayl. | Ikkala yo'l bir xil parse/result beradi. |
| ORD-IMP-005 | P1 | `.csv`, `.txt`, renamed fake `.xlsx`, executable file. | Client/server rad; xavfsiz xabar, upload/execute yo'q. |
| ORD-IMP-006 | P1 | Empty workbook, empty selected sheet, faqat header. | 0 product va tushunarli error; wizardga blank transfer yo'q. |
| ORD-IMP-007 | P1 | Bir nechta faylni drop qilish. | Single-file contract; bittasi deterministik tanlanadi yoki validation. |
| ORD-IMP-008 | P1 | Warehouse blank yoki price type blank bilan upload/apply. | Required validation; price/stock kontekstsiz import qilinmaydi. |
| ORD-IMP-009 | P1 | Mapping `starting_row=1`, end blank. | Startdan oxirgi data rowgacha parse. |
| ORD-IMP-010 | P1 | Start/end valid subset. | Faqat inclusive configured range parse qilinadi. |
| ORD-IMP-011 | P1 | Start=0, negative, decimal, text, start>end. | Numeric/range validation; setting saqlanmaydi yoki parse boshlanmaydi. |
| ORD-IMP-012 | P1 | Identify by `Код продукции`. | Code column bo'yicha aynan mos productlar topiladi. |
| ORD-IMP-013 | P1 | Identify by `Код на продукцию`. | Product-specific code mapping to'g'ri. |
| ORD-IMP-014 | P1 | Identify by `ИД продукции`. | Valid IDs topiladi; boshqa filial/invalid ID data leak qilmaydi. |
| ORD-IMP-015 | P1 | Code/balance/serial/card/expiry/quantity/margin mappings. | Har configured column tegishli product fieldga tushadi. |
| ORD-IMP-016 | P1 | Required mapping blank, duplicate column number, out-of-range column. | Setting validation; no ambiguous parse. |
| ORD-IMP-017 | P1 | Settings save, back, formni qayta ochish. | Mapping/range/mode user scope'da persist. |
| ORD-IMP-018 | P1 | All valid rows, mixed valid-invalid va all invalid. | Products/error grids ajratilgan; errorlarda original Excel row number. |
| ORD-IMP-019 | P1 | Unknown/inactive product, no price, no stock, wrong warehouse. | Har rowga aniq biznes error; valid rowlar policy bo'yicha qoladi. |
| ORD-IMP-020 | P1 | Duplicate product rows va quantity/margin boundarylari. | Merge/duplicate policy deterministik; totals double-count qilmaydi. |
| ORD-IMP-021 | P1 | Parsed productsni wizardga qaytarish va final save. | Product/quantity/price/margin bir xil; list/view total faylga mos. |
| ORD-IMP-022 | P1 | Parse natijasidan close/cancel va re-upload. | Unsaved rows wizardga o'tmaydi; yangi file eski errors/productsni tozalaydi. |
| ORD-IMP-023 | P2 | Katta fayl, Unicode product names, formulas, hidden rows/sheets, corrupt workbook. | Belgilangan sheet/range policy; timeout/crash/XSS yo'q; progress/error tushunarli. |

## J. Cross-form, NFR va recovery — 12 case

| ID | P | Test case / qadam | Expected result |
|---|---:|---|---|
| ORD-E2E-001 | P0 | Add→save→list→view→edit→view round-trip. | Bir ID, barcha asosiy field/item/total izchil. |
| ORD-E2E-002 | P0 | Product_list va inline selection bilan bir xil order. | Same input uchun quantity/price/margin/total parity. |
| ORD-E2E-003 | P0 | Import va inline selection bilan bir xil order. | Same input uchun list/view natijasi parity. |
| ORD-E2E-004 | P1 | Order statusning stock bookingga ta'siri. | Draft/active/cancelled/delivered policy bo'yicha available stock to'g'ri. |
| ORD-E2E-005 | P1 | Contract balancega create/edit/cancel ta'siri. | Balance bir marta kamayadi/qaytadi; failed save ta'sir qilmaydi. |
| ORD-E2E-006 | P1 | Action/promo/payment/consignment kombinatsiyasi. | Eligibility, totals va view/reportlarda izchil. |
| ORD-E2E-007 | P1 | List widget/filter/report totalsni order view bilan solishtirish. | Bir xil dataset va currency conversion; stale cache yo'q. |
| ORD-E2E-008 | P1 | Tashkent midnight va DSTsiz timezone boundary. | Order/delivery date bir kun siljimaydi; consignment max delivery date'dan hisoblanadi. |
| ORD-E2E-009 | P1 | XSS/injection payloads: note, address, search, import cells. | Escaped rendering, query xavfsiz, boshqa userga script ta'siri yo'q. |
| ORD-E2E-010 | P2 | Accessibility: keyboard wizard, modal focus, labels, error announcement. | Core flow mouse'siz bajariladi; focus trap/restore va accessible names ishlaydi. |
| ORD-E2E-011 | P2 | Responsive 1366×768, 1440×900 va zoom 125/150%. | Toolbar/grid/modal actionlari yo'qolmaydi; horizontal scroll ishlaydi. |
| ORD-E2E-012 | P2 | Performance: list 10k+, order 100+ rows, report/import parallel. | Kelishilgan SLA ichida; browser freeze, duplicate request va data corruption yo'q. |

## P0 avtomatlashtirish paketi

Minimal release-gate uchun quyidagi caselarni birinchi avtomatlashtirish tavsiya
qilinadi:

1. `ORD-ACC-001`
2. `ORD-LST-001`, `ORD-LST-002`, `ORD-LST-008`, `ORD-LST-015`,
   `ORD-LST-016`
3. `ORD-A1-001`, `ORD-A1-002`, `ORD-A1-003`, `ORD-A1-011`
4. `ORD-A2-001`, `ORD-A2-002`, `ORD-A2-003`, `ORD-A2-017`
5. `ORD-A3-001`, `ORD-A3-002`, `ORD-A3-005`, `ORD-A3-009`,
   `ORD-A3-022`, `ORD-A3-023`
6. `ORD-EDT-001`, `ORD-EDT-002`, `ORD-EDT-003`
7. `ORD-VST-001`, `ORD-VST-002`
8. `ORD-PLS-001`, `ORD-PLS-002`, `ORD-PLS-006`
9. `ORD-IMP-001`, `ORD-IMP-002`, `ORD-IMP-003`
10. `ORD-E2E-001`, `ORD-E2E-002`, `ORD-E2E-003`

Bu tavsiya etilgan release-gate paket 34 ta case; unda asosiy P0'larga qo'shib
bir nechta integratsion P1 case ham ataylab kiritilgan. To'liq katalog taqsimoti:
P0 — 33 ta, P1 — 144 ta, P2 — 13 ta; jami **190 ta testcase**.

## Mavjud automation va asosiy gaplar

| Qism | Hozirgi repo coverage | Asosiy gap |
|---|---|---|
| Basic lifecycle | Add→view→edit→status va order ID column mavjud | Negative date/quantity, permissions, concurrent edit |
| Contract | Limit ichida/tashqarida va contract payment type mavjud | Expired/inactive/cross-client contract |
| Consignment | Create/edit, split rows va day limit mavjud | Aggregate negative boundaries va permission matrix |
| Reports | Invoice reports/custom template mavjud | Bulk selection, file content va barcha template representative coverage |
| Product selection | Inline goods selection mavjud | Barcha item kindlar va `product_list` uchun reusable flow/test yo'q |
| Import | Alohida test topilmadi | File/mapping/parser/error-grid coverage to'liq yangi |
| View settings | Order ID column qo'shish mavjud | Remove/reorder/default/search fields, widget va order settings |

## Kelajakda yangi testcase qo'shish modeli

### Asosiy qaror

Har bir group testcase mustaqil ishlaydi. Runnerdagi `A-01`, `A-02` tartibi
faqat collection/report tartibi; data dependency emas.

- Group testcase faqat tasdiqlangan `user_setup` baseline'ga suyanishi mumkin.
- Bitta group testcase boshqa case yaratgan contract, project, action, order,
  setting yoki `data_store` keyni o'qimaydi.
- Feature-specific precondition shu testcase'ning Arrange qismida yaratiladi.
- Bir xil entity kamida uchta mustaqil testcasega bir xil configurationda kerak
  bo'lsa, uni shared setup baseline'ga qo'shish ko'rib chiqiladi.
- Bitta case failed bo'lsa shu groupdagi qolgan caselar skip qilinmaydi.

Migration vaqtida esa mavjud skip hook birdan olib tashlanmaydi. A/B/C caselari
hozir sibling `data_store` keylariga bog'liq: avval har consumer self-contained
qilinadi, so'ng fresh-page isolation tekshiriladi, faqat barcha dependencylar
yo'qolgandan keyin `_FAILED_SMOKE_GROUPS` mexanizmi o'chiriladi.

### `Проект`ni qo'shish namunasi

Project bir nechta order case uchun shared baseline bo'lsa, setup
`project-pw{code}`ni yaratadi. D-groupdagi har bir test shu setup qiymatini
mustaqil ishlatadi va o'z orderini o'zi yaratadi:

```text
tests/smoke/test_groups/test_D_grup/
├── test_order_uses_project.py
├── test_order_requires_project.py
├── test_edit_order_project.py
└── test_d_group_runner.py
```

| Runner case | Mustaqil testcase |
|---|---|
| D-01 | Setup project bilan yangi order yaratadi va viewda tekshiradi |
| D-02 | O'z yangi orderida required/blank project validatsiyasini tekshiradi |
| D-03 | O'z orderini yaratib, shu testcase ichida edit/project round-trip qiladi |

Project faqat bitta yoki ikkita casega kerak bo'lsa setup kengaytirilmaydi:
har case o'z Arrange qismida unique project yaratadi. Project formasi
choreography'si kamida uchta mustaqil leafda aynan takrorlangandagina reusable
flow/helperga nomzod bo'ladi.

Order qadamlarini yashiradigan `flow_order_with_project` yoki ko'p optional
parametrli `flow_order_main_page` kengaytmasi yaratilmaydi. Project selection va
assertion leaf testda `BasePage.b_input(...)`/`form_view(...)` bilan ko'rinadi.

### `Договор`ni qo'shish

Mavjud A-groupda A-03/A-04/A-05 oldingi case datalarini o'qiydi; bu legacy
dependency va refactor qilinadi.

- Contract creationning o'zi tekshiriladigan case o'z contractini yaratadi.
- Contract-limit order case o'ziga kerakli limit contractni Arrange'da yaratadi
  yoki setupdagi aynan shu shared baseline'dan foydalanadi.
- Payment-type order case boshqa A-case keyini emas, o'z preconditionini
  yaratadi.
- Edit case o'z orderini yaratib, shu testcase ichida edit/viewni tugatadi.

`flow_order_prepare_with_contract` kabi butun scenarioni tayyorlaydigan flow
ishlatilmaydi; contract selection, product, payment/status va expected total
testcase ichida ochiq qoladi.

### `Акция`ni qo'shish

Mavjud C-02 C-01 yaratgan actionga bog'langan; refactordan keyin C-02 o'z action
preconditionini o'zi yaratadi yoki setupdagi shared actionni ishlatadi. C-01
failure C-02ni bloklamaydi.

Bonus-product, amount-based va quantity-based actionlar alohida independent
testcase bo'ladi. Faqat test data farq qilsa parametrik matrix ishlatiladi.
Action yaratish UI choreography'si kamida uchta testcase'da aynan takrorlansa
flowga ajratiladi; discount va final total assertionlari leaf testda qoladi.

### Setupni qachon kengaytirish kerak?

Setup faqat quyidagi uch shart birga bajarilganda kengaytiriladi:

1. Entity kamida uchta mustaqil testcasega kerak.
2. Barcha consumerlar bir xil configurationdan foydalanadi.
3. Entity yaratishning o'zi consumer testning biznes maqsadi emas.

Expired contract, max-limit contract yoki maxsus action kabi variantlar setupga
kiritilmaydi; tegishli testcase Arrange qismida yaratiladi.

### Duplicate testcase va duplicate kodni boshqarish

Har yangi case uchun quyidagi gate ishlatiladi:

1. **Coverage search:** katalogdagi `ORD-*` IDlar, `@allure.title`, test fayl
   nomi va UI label bo'yicha `rg` bilan qidirish.
2. **Business intent:** yangi case yangi biznes riskni tekshiradimi? Faqat data
   varianti bo'lsa yangi copy-paste test emas, parametrik matrix ishlatiladi.
3. **Independence:** boshqa case yaratgan data yoki `data_store` key
   ishlatilmaydi.
4. **Flow admission:** faqat umumiy gateway yoki kamida uch leafda aynan
   takrorlangan choreography flowga chiqariladi.
5. **BasePage-first:** mavjud input/grid/view/save/helper bo'lsa raw locator yoki
   local wrapper yozilmaydi.
6. **Assertion ownership:** scenario-specific expected result leaf testda
   qoladi; flow biznes natijani yashirmaydi.
7. **Catalog mapping:** automated bo'lganda katalog IDsi, runner case,
   leaf path va status bitta inventory entryda belgilanadi.

### Bizda qanday testlar borligini aniqlash

Actual full-suite inventoryning source of truth'i — setup va group runnerlar.
Collectionni testlarni ishlatmasdan ko'rish:

```bash
./.venv/bin/pytest --collect-only -q \
  tests/smoke/test_setup/test_0_setup_runner.py \
  tests/smoke/test_groups/test_a_grup/test_0_group_runner.py \
  tests/smoke/test_groups/test_report_grup/test_0_group_runner.py
```

2026-07-31 current group inventory: Group-0 va Report; eski A/B/C testlari o'chirilgan.

Order bo'yicha semantic qidiruv:

```bash
rg -n "order|contract|consignment|action|Проект|Договор|Акци" \
  tests/smoke -g '*.py'
```

PR reviewda `pytest --collect-only` natijasi va ushbu katalogdagi automation
mapping solishtiriladi. Shunda runnerga qo'shilmagan leaf test va bir maqsadni
takrorlaydigan yangi testcase tez ko'rinadi.

## Automation arxitekturasi tavsiyasi

- Order listga kirish/create/view/edit/status uchun `flow_order_list` umumiy
  gateway bo'lib qoladi.
- Add/edit main, product va final qadamlar leaf testda BasePage bilan ochiq
  yoziladi; `OrderWizard` scenario-orchestrator flow yaratilmaydi.
- `product_list` va `order_import` uchun flow faqat kamida uch independent
  testcase'da bir xil choreography real takrorlangandan keyin yaratiladi.
- Table/widget setting testlari isolated user bilan ishlasin va teardown'da
  defaultga qaytarsin.
- Har save testida faqat heading emas, list row + order view + ID orqali
  round-trip tekshirilsin.
- Calculation testlari UI matnidan tashqari mustaqil Decimal formula bilan
  expected qiymat hisoblasin.
- Status, item kind, payment type va import identify mode parametrik test
  bo'lsin; 190 caseni 190 ta copy-paste test funksiyasiga aylantirmang.
