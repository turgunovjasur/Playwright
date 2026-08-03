# Акция (Aksiya / Promotion) formasi

Smartup'da aksiya = **Акция** (chegirma/bonus kampaniyasi). Mijoz buyurtmada shart bajarsa, bonus (skidka % yoki bonus tovar) oladi.

## Navigatsiya

- Menyu: **Справочники → Маркетинг → Акции** (`navigate_to(page, tab="Справочники", name="Акции")`)
- Ro'yxat URL: `#/<session>/anor/mcg/action_list`
- Qo'shish URL: `#/<session>/anor/mcg/action+add` ("Создать" tugmasi)
- Product tanlash (Показать все): `#/<session>/anor/mcg/action_product_list` — "Акция (подбор)" modali (Доступные/Выбранные). Lekin oddiy holatda inline dropdown'dan to'g'ridan-to'g'ri tanlash yetarli.

## Tuzilma — 2 bosqichli wizard

Forma 2 tab/bosqich: **Главное** va **Условия**. Pastda "Далее" → "Завершить". "Завершить" bosilganda **"Сохранить?"** biruni confirm modali chiqadi → **да** (`#biruniConfirm button: да`). Saqlangach `Акции` ro'yxatiga qaytadi.

### 1) Главное (asosiy) — majburiy maydonlar (*)

Forma moduli barqaror: `#anor718-input-...`; ro'yxat grid moduli `#anor717-input-b_grid-table`.

- **Название*** — `#anor718-input-text-name` ichidagi textbox (ng-model `d.name`)
- **Дата начала*** / **Срок действия*** — `#anor718-input-b_input-start_date` / `...-end_date` (default: bugun → +20 kun)
- **Рабочие зоны*** — `#anor718-input-b_input-rooms` (Поиск); ish zonasi `room-pw{code}`
- **Бонусный склад*** — `#anor718-input-b_input-bonus_warehouse` (Поиск); default ombor `Основной склад`
- **Тип акции** — shart asosi: `Кол-во` (default), `Сумма`, `Вес`, `Кол-во кейс`, `Смешанный`. Select ng-model `d.calc_kind` turidagi ui-select.
- Ixtiyoriy: Тип цены, Типы оплат, Склады, Характеристика клиентов, Обязательная; Статус (`Активный`), Бонусы за заказ va h.k.

### 2) Условия (shartlar) — Условие / Бонус (barqaror ng-model selektorlar)

- **Условие** (trigger): Тип условия = `[ng-model="rule.rule_kind"]` (`Обычный`). Default qator **"Все ТМЦ"**.
  - Мин. значение = `input[ng-model="rule.main_value"]`
  - Макс. значение = `input[ng-model="rule.extra_value"]`
  - МТКП = `input[ng-model="rule.required_count"]` (default 1)
  - Shart productini qidirish: `input[ng-model="d['selected_rule_name_' + condition_index + rule_index]"]` (Поиск)
- **Бонус** (mijoz nima oladi): **Тип бонуса** = `[ng-model="bonus.bonus_kind"]` → `Кол-во` yoki **`Скидка`**.
  - `Скидка` tanlansa, bonus product qatorida ustun **Значение(%)** bo'ladi.
  - Bonus product qidirish: `#bonus_products input[placeholder="Поиск..."]` → inline dropdown'dan `product-pw{code}` tanlanadi (yoki "Показать все" modali).
  - Chegirma foizi: `input[ng-model="product.value"]`

## "10 ta productga 10% skidka" talqini va flow (tasdiqlangan)

Bu kompaniyada odatda 1 ta product (`product-pw{code}`) bo'ladi, shuning uchun "10 ta product" = **miqdor** deb talqin qilinadi:

- Тип акции = **Кол-во**
- Условие: `rule.main_value` = **10** (10 dona olinganda ishga tushadi)
- **Условие producti SHART**: shart qatorini "Все ТМЦ" holatida QOLDIRMA — `#rule_products` (Поиск) orqali `product-pw{code}` ni tanla. Aks holda order'da aksiya umuman chiqmaydi (pastга qara).
- Бонус: `bonus.bonus_kind` = **Скидка**, ТМЦ = `product-pw{code}`, `product.value` = **10**
- Ro'yxatda: `Скидка 10% ... | Кол-во | Активный`
- Screenshot: `skills/smartup-guide/references/forms/screenshots/action/action__list-created__desktop-1200x660__20260610.png`

## Aksiyaning order'da ishlashi (end-to-end, MCP bilan 2026-06-16 tasdiqlangan)

Aksiya chegirmasi order'da qo'llanishi uchun **uchta** shart bir vaqtda bajarilishi kerak:

1. **Условие producti** = `product-pw{code}` (yuqorida). "Все ТМЦ" qolsa, order'ning "Акции" tabida `Тип цены акции не прикреплен к рабочей зоне или клиенту или штат` xatosi chiqadi va chegirma bo'lmaydi.
2. **Room'ga "Акция" narx turi prikrep qilingan** bo'lishi kerak (`run_room_attachment` step 6 — qarang [room.md] yoki `test_20_room_attachment.py`). Ulanish 2 bosqichli: `Тип цены tab -> Доступные -> Создать тип цены -> "Акция" -> Прикрепить -> Прикрепить Акция? да` (Доступныега qo'shadi), so'ng yana `Доступные -> "Акция" -> Прикрепить -> да` (Прикрепленныега o'tkazadi). Faqat 1-bosqich qilinsa, "Акция" Доступныеда qolib ketadi va order'da aksiya chiqmaydi.
3. **Order'da bonusni yoqish**: ТМЦ sahifasida product (qty=10) qo'shilgach, **"Акции" tab** paydo bo'ladi (badge bilan). Unda aksiya ko'rinadi (`Получить бонус`); chegirma avtomatik qo'llanmaydi — **"Получить" toggle**ни yoqish kerak. Toggle styled switch: `input[ng-model="condition.get"]` oddiy/force click bilan bosilmaydi, **native DOM `.click()`** (`page.evaluate`) ishonchli (ng-change orqali qayta hisoblanadi).

Natija (10 × 7 000 = 70 000, 10% skidka): **Товар** qatorida `Сумма скидки/наценки = -7 000`, `Сумма к оплате/ИТОГО = 63 000`; final sahifa va view'da ham `-7 000` / `63 000`; order list jami `63 000 сум`.

> Eslatma: aksiya formasidagi **"Тип цены"** maydoni (Главное) sotuv narx turini (`Price Type UZB-pw{code}`) beradi, **"Акция" emas** — bu C-01 da bo'sh qoldiriladi va chegirmaga ta'sir qilmaydi.

## Aksiyani o'chirish (Удалить) — cheklov (MCP 2026-06-16)

Orderda allaqachon qo'llanilgan aksiyani "Акции" ro'yxatidan **"Удалить"** bilan o'chirib bo'lmaydi — Smartup xato modali beradi:

```
ORA-02292: integrity constraint (XTRADE.MDEAL_PRODUCT_MARGINS_F3) violated - child record found
```

Sabab: aksiya order product margin (`MDEAL_PRODUCT_MARGINS`) yozuvlarini yaratgan — bular child yozuv, ular turганда parent aksiya o'chmaydi. Testda aksiyani tozalash kerak bo'lsa, avval unga bog'liq orderlarni o'chirish/bekor qilish, so'ng aksiyani o'chirish kerak.

## Login / data eslatma

- Aksiya user profil bilan yaratiladi: `user-pw{code}@<company>`, parol USER_PASS. `code` va konkret qiymatlar `data_store.json` dan olinadi (dossierга literal yozilmaydi).
- Avvalgi Group C action testlari 2026-07-31 kuni o'chirilgan; yangi testlar qaytadan yoziladi.
