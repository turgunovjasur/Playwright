# Playwright Smoke Tests — Smartup ERP

Playwright + pytest asosida yozilgan smoke test suite. Allure hisoboti va trace yozish o'rnatilgan.

---

## Talablar

- Python 3.11+
- [Allure CLI](https://allurereport.org/docs/install/) (`brew install allure`)

---

## O'rnatish

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## Muhit o'zgaruvchilari

Credentials `.env` fayldan o'qiladi. `.env` gitga kirmaydi — har kim o'zini yaratadi:

```bash
cp .env.example .env
# keyin .env ni o'z qiymatlari bilan to'ldiradi
```

| O'zgaruvchi    | Tavsif                  |
|----------------|-------------------------|
| `BASE_URL`     | Test muhiti manzili     |
| `TEST_EMAIL`   | Admin login             |
| `TEST_PASSWORD`| Admin parol             |

> `.env.example` — xavfsiz namuna fayl, gitda saqlanadi. `.env` — haqiqiy credentials, **gitga kirmaydi**.

---

## Testlarni ishga tushirish

### Tavsiya etilgan — to'liq tsikl (test + allure hisobot)

```bash
bash run_tests.sh
```

Bu buyruq:
1. Eski natijalarni tozalaydi (history saqlanadi)
2. Smoke runner testlarini o'tkazadi
3. Allure hisobotini yaratadi
4. Hisobotni brauzerda ochadi

---

### Faqat testlarni ishga tushirish (alluresiz)

```bash
pytest tests/smoke/test_smoke_runner.py -v
```

### `run_tests.sh` ga argument berish

```bash
# Verbose + qisqa xato ko'rsatish
bash run_tests.sh -v --tb=short

# Headless rejimda
bash run_tests.sh --headed=false
```

---

> **Muhim:** Testlar bir-biriga bog'liq — har biri oldingi test yaratgan ma'lumotdan foydalanadi.
> Shuning uchun har doim **`test_smoke_runner.py`** to'liq ishlatiladi. Alohida test fayllari mustaqil ishlamaydi.

---

## Test qamrovi

`test_smoke_runner.py` — barcha testlar **bitta browser sessiyasida** ketma-ket ishlaydi.

| # | Test nomi              | Nima tekshiriladi                                     |
|---|------------------------|-------------------------------------------------------|
| 01 | Authorization         | Login, dashboard yuklanishi                           |
| 02 | Legal Person          | Yuridik shaxs yaratish va qidirish                   |
| 03 | Filial                | Organizatsiya yaratish, valyuta va yuridik shaxs bog'lash |
| 04 | Room                  | Ish zonasi yaratish                                   |
| 05 | Robot                 | Shtat birligini yaratish                              |
| 06 | Natural Person        | Jismoniy shaxs yaratish                               |
| 07 | User                  | Foydalanuvchi yaratish va robot/jismoniy shaxs bog'lash |
| 08 | User Attach Form      | Foydalanuvchiga formalar biriktirish                  |
| 09 | Role                  | Admin roliga barcha ruxsatlar berish                  |
| 10 | Role Attach Form      | Rolga barcha formlarga kirish ruxsatini berish        |
| 11 | Buy License           | Litsenziya sotib olish                                |
| 12 | Attach License        | Foydalanuvchiga litsenziya biriktirish                |
| 13 | Change Password       | Yangi foydalanuvchi parolini o'zgartirish             |
| 14 | Price Type            | Narx turini yaratish                                  |
| 15 | Payment Type          | To'lov turlarini biriktirish                          |
| 16 | Sector                | TMT to'plami (Набор ТМЦ) yaratish                    |
| 17 | Product               | TMT (mahsulot) yaratish                               |

> **Eslatma:** `test_smoke_runner.py` da `#` bilan comment qilingan testlar hali faol emas.

---

## Test natijalari strukturasi

```
test-results/
├── allure-results/          # pytest tomonidan yoziladigan xom natijalar
│   ├── history/             # Trend grafigi uchun tarix
│   ├── environment.properties
│   ├── executor.json
│   └── categories.json
├── allure-report/           # Allure CLI tomonidan render qilingan HTML
├── traces/                  # Playwright trace fayllari (.zip)
│   ├── smoke_trace.zip      # session_page ishlatgan testlar (to'liq sessiya)
│   └── *.zip                # page fixture ishlatgan har bir test uchun alohida
└── logs/                    # Muvaffaqiyatsiz testlar uchun log fayllar
    └── *.log
```

---

## Allure hisoboti

### Yaratish va ochish

```bash
# Natijalardan hisobot yaratish
allure generate test-results/allure-results -o test-results/allure-report --clean

# Hisobotni brauzerda ochish
allure open test-results/allure-report
```

### Faqat serve qilish (papkani yaratmasdan)

```bash
allure serve test-results/allure-results
```

---

## Trace Viewer

Test xato bo'lganda Playwright avtomatik `.zip` trace saqlaydi.

### Eng oxirgi traceni ochish

```bash
playwright show-trace $(ls -t test-results/traces/*.zip | head -1)
```

### Muayyan test traceni ochish

```bash
# Fayl nomini ko'rish
ls test-results/traces/

# Kerakli traceni ochish
playwright show-trace test-results/traces/smoke_trace.zip
```

### Trace viewer imkoniyatlari

- **Timeline** — har bir action vaqt bo'yicha
- **Screenshots** — har bir qadam skrinshotlari
- **Network** — barcha tarmoq so'rovlari
- **Console** — brauzer konsol xabarlari
- **Source** — test kodi qaysi qatorda ekanligini ko'rsatadi

---

## Foydali buyruqlar

```bash
# Testlarni headless rejimda ishlatish
pytest tests/smoke/test_smoke_runner.py --headed=false

# Faqat muvaffaqiyatsiz testlarni qayta ishlatish
pytest tests/smoke/test_smoke_runner.py --lf

# Xato bo'lganda darhol to'xtatish
pytest tests/smoke/test_smoke_runner.py -x

# Verbose + to'liq xato traceback
pytest tests/smoke/test_smoke_runner.py -v --tb=long
```