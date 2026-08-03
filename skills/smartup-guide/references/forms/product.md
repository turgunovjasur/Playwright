# ТМЦ (Product) — yaratish va narx belgilash

Product = **ТМЦ** (Товарно-материальная ценность). Setup smoke testda keyingi
order testlari uchun ikkita product yaratiladi:

| Product | Kod | Price type | Narx |
|---|---|---|---|
| `product-pw{code}` | `c_p_pw{code}` | `Price Type UZB-pw{code}` | 7000 UZS |
| `product-usa-pw{code}` | `c_p_usa_pw{code}` | `Price Type USA-pw{code}` | 1 USD |

## Mundarija

- [Screenshot](#screenshot)
- [Navigatsiya](#navigatsiya)
- [Forma maydonlari](#forma-maydonlari-yaratish)
- [Saqlash pattern](#saqlash-pattern)
- [Narx belgilash](#narx-belgilash)
- [Downstream ta'siri](#downstream-tasiri)
- [Test](#test)
- [Ikkinchi USD product](#2026-07-30--ikkinchi-usd-product)

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
| Код | `BasePage.input(label="Код", ...)` | `c_p_pw{code}` yoki `c_p_usa_pw{code}` |
| Название | `BasePage.input(label="Название", ...)` | `product-pw{code}` yoki `product-usa-pw{code}` |
| Ед. изм. | `BasePage.b_input(label="Ед. изм.", value="шт", search_text="")` | `шт`; clickda ochilgan ro'yxatdan searchga yozmasdan tanlanadi |
| Наборы ТМЦ | `BasePage.multiselect(label="Наборы ТМЦ", expect_value=sector_name)` | auto-selected `sector-pw{code}` chipi |
| Статус | `BasePage.checkbox(label="Активный", expect_checked=True)` | default checked |
| Тип ТМЦ | `BasePage.checkbox(label="Товар", checked=True)` | checked |

**Precondition tekshiruvi:** `Наборы ТМЦ` multiselect fieldining o'zida `sector-pw{code}` chipi ko'rinishi kerak — sector yaratilmagan bo'lsa product to'g'ri guruhlanmaydi.

Live UI probe (2026-07-13): `Товар`, `Продукция`, `Сырье` radio emas, alohida `input[type="checkbox"][ng-model="item.enabled"]` kontrollari. Shuning uchun `Товар` faqat text click bilan emas, `BasePage.checkbox(..., checked=True)` bilan tanlanadi va checked holati tekshiriladi.

## Saqlash pattern

```python
base.click(name="Сохранить", exact=True)
base.expect_page(heading="ТМЦ")
# biruni confirm yo'q yaratishda
```

Ro'yxatda har bir product o'z kodi va nomi bilan tekshiriladi.

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

## Narx belgilash

Yaratilgan product qatori bosilgach:

```
"Установить цены" button → "ТМЦ (установка цен)" heading
→ `BasePage.input(label=price_type_name, value=price)`
→ `base.click(name="Сохранить", exact=True)`
→ `base.confirm_biruni(expected_text="Сохранить?")`
→ `base.expect_page(heading="ТМЦ")`
```

Live UI probe (2026-07-13) narx grid headerlari: `Название`, `Тип цены`, `Номер карточки`, `Средняя цена закупа`, `Цена с НДС и акцизом`, `Цена без НДС`, `Цена без НДС и акциза`. UZB narx turi qatori `price_type_name` matni orqali topilib, shu qatordagi keyingi narx inputi `BasePage.input(label=price_type_name, ...)` bilan to'ldiriladi.

- Asosiy product narxi = **7000 UZS**. Bu qiymat aksiya chegirmasi ssenariysida
  ishlatiladi: 10 × 7000 = 70 000, 10% skidka → 63 000.
- Ikkinchi product narxi = **1 USD**. Uning price type'i
  `run_price_type_usa` yaratgan `Price Type USA-pw{code}` bo'lishi shart.
- Setup 14-qadam shu USD price type'ni `Доллар США` valyutasida yaratadi va
  joriy kun kursini 10000 qilib o'rnatadi.

## Downstream ta'siri

- `action.md` aksiya ssenariysi: `product-pw{code}` x10 = 70 000; 10% skidka = 63 000
- `order-add.md`: `product-pw{code}` va `product-usa-pw{code}` ikkita alohida
  product sifatida ishlatiladi.
- Har ikkala product uchun Setup 21-qadamda 100 donadan boshlang'ich qoldiq
  o'tkaziladi; shuning uchun fresh run'da ikkalasi ham Order product pickerda
  stock preconditioniga ega.

## Test

- `tests/smoke/test_setup/test_18_product.py` → yagona `run_product(page, code)`
  UZS va USD productlarni yaratib, tegishli narx turlarini belgilaydi; `run_`
  auth qilmaydi.
- Setup runner **18 - Product** wrapperida shu bitta `run_product` funksiyasini
  chaqiradi.
- Standalone `test_product` user sifatida login qiladi, kerakli
  `filial-pw{code}` filialiga o'tadi va ikkala productni yaratadi.
- Validation (2026-07-13): production `test_product` create → list → price save oqimi `1 passed`; view → close → list → set-price navigatsiya probe'i `1 passed`.

## 2026-07-30 — Ikkinchi USD product

Tags: product, usd, price-type, setup, order
Status: live-ui-confirmed
Verified: 2026-07-30
Source: `tests/smoke/test_setup/test_0_setup_runner.py`; `smartup.online` headless
Setup run `20 passed, 1 deselected`

- `product-usa-pw{code}` / `c_p_usa_pw{code}` yaratildi.
- `ТМЦ (установка цен)` formasida aynan `Price Type USA-pw{code}` qatoriga
  `1` narx yozildi.
- Product saqlangandan keyin alohida USD boshlang'ich qoldig'i o'tkazildi va
  yakuniy `Остатки ТМЦ` sahifasida product kodi va nomi topildi.
