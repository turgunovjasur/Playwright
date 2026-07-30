---
name: run-smoke
description: Smartup smoke testlarini scripts/run_tests.py yoki pytest orqali ishga tushiradi, natija/log/trace/Allure artefaktlarini tahlil qiladi. "testlarni ishga tushir", "smoke run", "pytest run", aniq setup/group/forms targetini run qilish so'ralganda ishlat.
---

# Smoke Testlarni Ishga Tushirish

Argument: `$ARGUMENTS` (test nomi, fayl yoki bo'sh)

## Qaysi buyruqni ishlating

### Barcha smoke testlar (to'liq run):
```bash
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password>
```

Headless run:
```bash
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --headless
```

Yangi company yaratish:
```bash
python scripts/run_tests.py --url <server_url> --create-company --head-email <head_email> --head-password <head_password>
```

Debug uchun setup yoki group:
```bash
python scripts/run_tests.py setup --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py groups --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py group-a --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py group-b --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py group-c --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py group-report --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py forms --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py setup-forms --url <server_url> --company-code <company_code> --company-password <company_password>
```

Browser ochilishi kerak bo'lsa `HEADLESS=1` yoki `--headless` ishlatma; `--headless` berilsa browser ko'rinmasligi to'g'ri holat.

### Bitta test fayl:
```bash
python -m pytest tests/smoke/test_setup/test_<nomi>.py -v
```

### Bitta test funksiya:
```bash
python -m pytest tests/smoke/test_setup/test_setup_runner.py::test_<nomi> -v
```

Repo rootda `.env` mavjud bo'lsa direct pytest/PyCharm run konfiguratsiyasi undan olinadi; `.env` yo'q bo'lsa terminal/CI flaglari ishlaydi.

### Allure hisobot ko'rish:
```bash
allure serve test-results/allure-results
```

## Ish tartibi

1. `$ARGUMENTS` bo'sh bo'lsa — to'liq `python scripts/run_tests.py --url <server_url> --company-code <code> --company-password <password>` yoki `--create-company --head-email <email> --head-password <password>` bilan ishga tushir
2. `$ARGUMENTS` fayl nomi bo'lsa — faqat shu faylni ishga tushir
3. `$ARGUMENTS` test nomi bo'lsa — faqat shu testni ishga tushir
4. Natijalarni tahlil qil:
   - **PASSED** testlar sonini ko'rsat
   - **FAILED** testlar bo'lsa — xato xabarini o'qib sababini tushuntir
   - `--maxfail=3` limit urilsa ogohlantir
5. Muvaffaqiyatsiz testlar bo'lsa: `test-results/logs/` papkasidagi log fayllarni o'qi va foydalanuvchiga ko'rsat

## Muhim

- Asosiy runner cross-platform: `python scripts/run_tests.py --url <server_url> --company-code <code> --company-password <password>`; Mac/Linux uchun `./run_tests.sh ...` wrapper ham bor.
- Precedence qat'iy: repo rootda `.env` mavjud bo'lsa u yagona asosiy konfiguratsiya hisoblanadi; terminaldagi inline env va CLI flaglar berilgan bo'lsa ham `.env` qiymatlari ishlaydi. `.env` bo'lmasa terminal/CI CLI flaglari va shell env ishlaydi.
- Mavjud company bilan run qilish uchun `--company-code` va `--company-password` majburiy.
- Yangi company yaratish uchun `--create-company`, `--head-email` va `--head-password` majburiy.
- `--create-company` bilan `--company-code` va `--company-password` berilmaydi; company code test ichida `autotest<code>` ko'rinishida yaratiladi.
- Company setupda Security tabdagi `Политика лицензирования`ni off qilish kerak bo'lsa `--create-company --head-email <email> --head-password <password> --disable-license-policy` ishlatiladi.
- `--disable-license-policy` ishlatilsa `Buy License` va `Attach License` qadamlari o'tkazib yuboriladi.
- `pytest.ini` dagi `testpaths = tests` va `addopts` avtomatik qo'llanadi
- Trace fayllari `test-results/traces/` ga, Allure natijalar `test-results/allure-results/` ga yoziladi
- `scripts/run_tests.py` Allure reportni `--open-report` yoki shell/repo `.env` dagi `OPEN_REPORT=1` bilan ochadi.
- `scripts/run_tests.py` trace viewerini faqat `--show-trace` bo'lsa ochadi.
- Directory/default collectionda runner bo'lmagan smoke testlar duplicate flow bo'lmasligi uchun deselect qilinadi; leaf testni debug qilish uchun uning fayl yo'lini pytestga aniq ber.
- Full run setup runner va barcha group runner fayllarini bitta pytest sessiyasida collect qiladi; har bir setup/group case Allure'da alohida test bo'lib ko'rinadi.

## Test dependency modeli

- User setup testlari ketma-ket va bir-biriga bog'liq: oldingi setup test keyingi setup test uchun kerakli entity yaratadi.
- User setup testlari yaxshi o'tgandan keyin group testlar run qilinadi.
- Group testlar user setup natijalariga bog'liq, lekin boshqa group testlarga bog'liq emas.
- Bir group ichida test yiqilsa, shu groupning qolgan testlari skip qilinadi; keyingi group testlar run bo'lishda davom etadi.
- Run natijasini tahlil qilganda failure setup bosqichidami yoki group bosqichidami aniq ajratib ayt.
- `tests/smoke/test_setup/test_setup_runner.py` ichidagi mavjud barcha testlar user setup testlari hisoblanadi.
- A-group testlari user setupdan keyin run qilinadi; A-groupning birinchi testi order uchun contract yaratadi.
- A-group testlari `tests/smoke/test_groups/test_A_grup/` papkasida saqlanadi; contract testlari alohida `test_create_contract.py` va `test_create_contract_with_payment_type.py` fayllarida, tartib esa runnerda beriladi.
- Order testlarida product chiqmasa, `test_20_init_balance` orqali balans qo'shib kelish yoki bron qilingan orderlarni `Canceled/Отменен` statusga o'tkazish kerak bo'lishi mumkin.
