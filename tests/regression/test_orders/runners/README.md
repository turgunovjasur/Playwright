# Guruh runnerlari

Barcha guruhlarni [../../run.py](../../run.py) yig‘ib ishga tushiradi.
Runnerdagi `test_*` ustida dependency; haqiqiy qadamlar setup/business case fayllarida.

| Guruh kodi | Runner | Test soni |
|---|---|---:|
| SCN-001 | [test_statuses_runner.py](test_statuses_runner.py) | 5 |
| SCN-002 | [test_promotions_runner.py](test_promotions_runner.py) | 8 |
| SCN-003 | [test_payments_runner.py](test_payments_runner.py) | 9 |
| SCN-004 | [test_mandatory_runner.py](test_mandatory_runner.py) | 13 |
| SCN-005 | [test_stock_runner.py](test_stock_runner.py) | 4 |
| SCN-006 | [test_bonus_limit_runner.py](test_bonus_limit_runner.py) | 13 |
| SCN-007 | [test_returns_runner.py](test_returns_runner.py) | 14 |
| SCN-008 | [test_multi_payments_runner.py](test_multi_payments_runner.py) | 10 |
| SCN-009 | [test_manual_discounts_runner.py](test_manual_discounts_runner.py) | 10 |
| SCN-010 | [test_product_limit_runner.py](test_product_limit_runner.py) | 8 |
| SCN-011 | [test_two_warehouses_runner.py](test_two_warehouses_runner.py) | 10 |
| SCN-012 | [test_mixed_promotions_runner.py](test_mixed_promotions_runner.py) | 8 |
| SCN-013 | [test_auto_offset_runner.py](test_auto_offset_runner.py) | 6 |
| SCN-014 | [test_prepayment_first_runner.py](test_prepayment_first_runner.py) | 7 |
| SCN-016 | [test_catalog_price_history_runner.py](test_catalog_price_history_runner.py) | 8 |
| SCN-017 | [test_excel_import_promotion_runner.py](test_excel_import_promotion_runner.py) | 7 |
| SCN-018 | [test_consignment_due_dates_runner.py](test_consignment_due_dates_runner.py) | 9 |
| SCN-019 | [test_archive_restore_runner.py](test_archive_restore_runner.py) | 11 |
| SCN-020 | [test_bulk_missing_price_runner.py](test_bulk_missing_price_runner.py) | 6 |
| SCN-021 | [test_fractional_quantity_runner.py](test_fractional_quantity_runner.py) | 6 |
| SCN-022 | [test_discount_apply_all_runner.py](test_discount_apply_all_runner.py) | 7 |
| SCN-023 | [test_delivery_address_runner.py](test_delivery_address_runner.py) | 8 |
| SCN-024 | [test_line_history_runner.py](test_line_history_runner.py) | 7 |
| SCN-025 | [test_service_status_runner.py](test_service_status_runner.py) | 7 |
| SCN-026 | [test_goods_service_discount_runner.py](test_goods_service_discount_runner.py) | 8 |
| SCN-027 | [test_order_xml_runner.py](test_order_xml_runner.py) | 8 |
| SCN-028 | [test_bonus_recalculation_runner.py](test_bonus_recalculation_runner.py) | 13 |

Asosiy suite 27 ta guruhdagi 230 ta tayyorlov va biznes qadamini bajaradi.
SCN-015 nazoratli uzilishlar uchun alohida verification runneriga ajratilgan.

## Order biznes qadamlari

| Guruh | Setup | Biznes va bog‘liqlik |
|---|---|---|
| SCN-016 | Guruh mahsuloti → 1 000 so‘mlik narx → 4 dona qoldiq. Klient alohida tayyorlanadi. | Klient va qoldiq → eski qoralama → katalog narxi 1 500. Shundan keyin yangi qoralamaning 3 000 so‘mlik summasi va eski qoralamaning 2 000 so‘mlik summasi alohida tekshiriladi. |
| SCN-017 | Sotuv va bonus mahsulotlari → narxlar. Narxlardan keyin qoldiq va 5 donaga 1 bonus aksiyasi tayyorlanadi. Klient alohida tayyorlanadi. | Klient, qoldiq va aksiya → qo‘lda kiritilgan 4 300 so‘mlik bank o‘tkazmali qoralama → tahrirlashda eski qatorni olib tashlash va Excel’dan qayta import qilish. Tahrir saqlanmasidan oldin jami 4 300 so‘m va 1 bonus tekshiriladi. |
| SCN-018 | Konsignatsiya, guruh mahsulotining 1 000 so‘mlik narxi va qoldig‘i, klient, loyiha, shartnoma hamda UZS bank hisobi tayyorlanadi. | Ikki muddatli qoralama → arxiv → birinchi muddatni to‘lash → ikkinchi muddatni to‘lash. Har biridan keyin aynan shu orderning ochiq muddatlari, yakunda ikkita to‘lov yozuvi tekshiriladi. |
| SCN-019 | KG va dona mahsulotlari → 1 000 va 1 500 so‘mlik narxlar → 12 kg va 12 dona qoldiq. Klient alohida tayyorlanadi. | Qoldiq + klient → 3 750 so‘mlik qoralama → rezerv → jo‘natish → arxivda qarz → yetkazilgan holatga tiklash → bekor qilish va qarz/qoldiqni tekshirish → qoralamaga tiklash va takroriy harakat yo‘qligini tekshirish. |
| SCN-020 | KG va dona mahsulotlari → KG uchun 1 000 so‘m, dona mahsulotning eski va yangi turida 1 500 so‘m, KG uchun yangi narx bo‘sh → ikkala mahsulotga qoldiq. Klient alohida tayyorlanadi. | Qoldiq + klient → ikki eski narx turida 3 750 so‘mlik qoralama → ikkala qatorni yangi narx turiga o‘tkazish. View/Edit’da faqat dona mahsulotning turi almashadi. |
| SCN-021 | KG mahsuloti → 1 000 so‘mlik narx → 12 kg qoldiq. Klient alohida tayyorlanadi. | Qoldiq + klient → 1,25 kg ga 100 so‘m/kg chegirma bilan 1 125 so‘mlik qoralama → shu orderni 2,5 kg ga o‘zgartirish va 2 250 so‘mni tekshirish. |
| SCN-022 | T01 KG va dona → T02 narxlar → T03 qoldiq. T04 klient va T05 17% chegirma mustaqil tayyorlanadi. | T03 + T04 + T05 → T06 chegirmani ikkala qatorga tarqatish. Rad etilsa 3 745, tasdiqlansa 3 320 so‘m. T06 → T07 saqlangan ikki qatorni View va Edit’da tekshirish. |
| SCN-023 | T01 manzil sozlamasi → T05 A va B manzilli klient. Mustaqil T02 mahsulot → T03 narx → T04 qoldiq. | T04 + T05 → T06 A manzilini saqlash → T07 B ga almashtirish → T08 tozalash. Har safar aynan shu buyurtma qayta ochiladi. Guruh oxirida sozlama avvalgi holatiga qaytadi. |
| SCN-024 | T01 KG mahsuloti → T02 narx → T03 qoldiq. T04 klient mustaqil tayyorlanadi. | T03 + T04 → T05 1,25 kg qoralama → T06 2,5 kg ga tahrirlash → T07 aynan shu mahsulot tarixida miqdor, chegirma va qator summasining eski va yangi qiymatlarini solishtirish. |
| SCN-025 | Ikki xizmat (1 200 so‘m), alohida klient va nazorat tovari qoldig‘i mustaqil tayyorlanadi. | Qoralama → Yangi → Jo‘natilgan → Qoralama. Har safar ikki xizmat, 3 600 so‘m hamda nazorat qoldig‘i tekshiriladi. Abgular 1450–1459. |
| SCN-026 | Tovar → 1 500 so‘mlik narx → qoldiq. Xizmat, klient va 17% chegirma alohida tayyorlanadi. | 3 000 + 1 200 → 17% chegirma → qoralama. View va Edit’da 714 so‘m chegirma va jami 3 486 so‘m. Abgular 1376–1378. |
| SCN-027 | Mahsulot → 1 000 so‘mlik narx → qoldiq. Alohida klient mustaqil tayyorlanadi. | Klient va qoldiq → 2 000 so‘mlik qoralama → shu mahsulot narxi 1 500 → 3 000 so‘mlik ikkinchi qoralama. Ikkala ID bo‘yicha XMLdagi mijoz, SKU, miqdor, narx va summalar solishtiriladi. Abgular 1309–1312. |
| SCN-028 | Ikki mahsulot, qoldiq, klient, 1 000 va 1 500 so‘mlik narxlar, 17% chegirma va faqat eski narxga 5+1 aksiyasi. | Ikki alohida qoralamada bonus tanlanadi. Ro‘yxatdan narx turi almashtirilganda jami 6 225 so‘m va bonus 1 dona. Birinchi qoralamada Подборga kirib chiqish, ikkinchisida miqdorni 5 dan 6 ga o‘zgartirish bonusni olib tashlaydi. |

SCN-022, SCN-023 va SCN-024 uchun qo‘lda bajarilgan qadamlar `abgular test/forms/order-ui-elements-20261028.md` da mos ravishda 1686–1691, 1570–1578 va 1555–1556 raqamlari bilan qayd etilgan.

Qo‘lda nazorat manbasi — `abgular test/forms/order-ui-elements-20261028.md`. SCN-019 uchun 1601–1617, SCN-020 uchun 1543–1547, SCN-021 uchun 1537–1542-qadamlar ishlatilgan.

Qo‘lda tekshirish uchun manbalar `abgular test` loyihasidagi `ORD-BIZ28-07`, `forms/cases/id-99.md` va `UI-CONTRACT-CONSIGN-PARTIAL-FULL-PAYMENT-001`.
