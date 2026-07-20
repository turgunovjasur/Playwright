# Типы оплат (Payment Type) — ulash

To'lov turlari **yaratilmaydi** — global katalogdan company'ga ulanadi (Прикрепление).

## Navigatsiya

- Menyu: **Справочники → Цены → Типы оплат**
  - "Цены" menyusiga kirgach `Типы оплат` link chiqadi
- Ro'yxat heading: `Типы оплат`
- Prикreplenie heading: `Тип оплат (прикрепление)`

## Ulash flow

```
"Прикрепление" button
→ "Тип оплат (прикрепление)" heading kutish
→ `BasePage.grid(checkbox="all")` — barchasini belgilash
→ "Прикрепить" button
→ confirm_biruni("Прикрепить типы оплат в количестве 4?")
→ wait_for_loader()
→ `BasePage.grid(is_empty=True)` natijasi `True` ekanini tekshirish (barcha available bo'sh qolishi kerak)
→ "Закрыть" button
```

## Natija (4 ta to'lov turi)

Ro'yxatda ko'rinishi kerak:
- `Наличные деньги`
- `Перечисление`
- `Терминал`
- `Чековая книжка`

## Muhim

- `code` parametri yo'q — bu global, har bir company'ga bir xil 4 ta to'lov turi ulanadi
- Room prikreplenie (`room.md`) uchun ham shu Типы оплат ro'yxatidan tanlanadi
- Standalone pytest wrapper `authorization(page, who="user", code=code)` bilan user sifatida login qiladi; `run_payment_type(page)` esa allaqachon login qilingan page qabul qiladi.

## Test

- `tests/smoke/test_setup/test_payment_type.py` → `run_payment_type(page)`
