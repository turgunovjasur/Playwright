# ТМЦ (Product) — yaratish va narx belgilash

Product = **ТМЦ** (Товарно-материальная ценность). Smoke testda bitta product yaratiladi va unga 7000 UZS narx qo'yiladi.

## Screenshot

- Add forma: `references/forms/screenshots/product/product__add__desktop-1440x783__20260713.png`
- View forma: `references/forms/screenshots/product/product__view__desktop-1440x783__20260713.png`
- Narx belgilash: `references/forms/screenshots/product/product__set-price__desktop-1440x783__20260713.png`
- Har screenshot yonida shu nomli `.json` metadata fayli bor.

## Navigatsiya

- Menyu: **Справочники → ТМЦ**
- Ro'yxat heading: `ТМЦ`
- Yaratish heading: `ТМЦ (создание)`
- Narx belgilash heading: `ТМЦ (установка цен)`

## Forma maydonlari (yaratish)

| Maydon | Locator | Qiymat |
|---|---|---|
| Код | `BasePage.input(label="Код", ...)` | `c_p_pw{code}` |
| Название | `BasePage.input(label="Название", ...)` | `product-pw{code}` |
| Ед. изм. | `BasePage.b_input(label="Ед. изм.", value="шт", search_text="")` | `шт`; clickda ochilgan ro'yxatdan searchga yozmasdan tanlanadi |
| Наборы ТМЦ | `BasePage.multiselect(label="Наборы ТМЦ", expect_value=sector_name)` | auto-selected `sector-pw{code}` chipi |
| Статус | `BasePage.checkbox(label="Активный", expect_checked=True)` | default checked |
| Тип ТМЦ | `BasePage.checkbox(label="Товар", checked=True)` | checked |

**Precondition tekshiruvi:** `Наборы ТМЦ` multiselect fieldining o'zida `sector-pw{code}` chipi ko'rinishi kerak — sector yaratilmagan bo'lsa product to'g'ri guruhlanmaydi.

Live UI probe (2026-07-13): `Товар`, `Продукция`, `Сырье` radio emas, alohida `input[type="checkbox"][ng-model="item.enabled"]` kontrollari. Shuning uchun `Товар` faqat text click bilan emas, `BasePage.checkbox(..., checked=True)` bilan tanlanadi va checked holati tekshiriladi.

## Saqlash pattern

```python
BasePage(page).save_and_expect_heading("ТМЦ", ...)
# biruni confirm yo'q yaratishda
```

Ro'yxatda: `c_p_pw{code}` ko'rinadi.

BasePage-first list/view zanjiri:

```python
base.grid_controller(search=product_code)
base.grid(product_code, product_name, click=True)
page.get_by_role("button", name="Просмотреть").click()
base.expect_page(heading="ТМЦ (просмотр)")
base.text(product_code, product_name)
page.get_by_role("button", name="Закрыть", exact=True).click()
base.expect_page(heading="ТМЦ")
```

View URL pattern: `.../anor/mr/product/inventory_view?product_id=<id>`; view ichida `Установить цены` yo'q. Narx flowi uchun viewni `Закрыть` bilan yopib, list qatorini qayta tanlash kerak.

## Narx belgilash (ikkinchi qadam)

Yaratilgan product qatori bosilgach:

```
"Установить цены" button → "ТМЦ (установка цен)" heading
→ `BasePage.input(label=price_type_name, value="7000")`
→ save_and_expect_heading("ТМЦ", confirm_text="Сохранить?")
```

Live UI probe (2026-07-13) narx grid headerlari: `Название`, `Тип цены`, `Номер карточки`, `Средняя цена закупа`, `Цена с НДС и акцизом`, `Цена без НДС`, `Цена без НДС и акциза`. UZB narx turi qatori `price_type_name` matni orqali topilib, shu qatordagi keyingi narx inputi `BasePage.input(label=price_type_name, ...)` bilan to'ldiriladi.

Narx = **7000** (UZS). Bu qiymat C-group aksiya testida ishlatiladi: 10 × 7000 = 70 000, 10% skidka → 63 000.

## Downstream ta'siri

- `action.md` C-01/C-02: `product-pw{code}` x10 = 70 000; 10% skidka = 63 000
- `order-add.md`: product sifatida ishlatiladi

## Test

- `tests/smoke/test_setup/test_product.py` → `run_product(page, code)`; `run_` auth qilmaydi.
- Standalone `test_product` user sifatida login qiladi, kerakli `filial-pw{code}` filialiga o'tadi va `run_product`ni chaqiradi.
- Validation (2026-07-13): production `test_product` create → list → price save oqimi `1 passed`; view → close → list → set-price navigatsiya probe'i `1 passed`.
