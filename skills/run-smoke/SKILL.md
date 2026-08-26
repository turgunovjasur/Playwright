---
name: run-smoke
description: Use when foydalanuvchi Smartup testini aynan run qilishni, pytest/smoke targetini ishga tushirishni yoki run natijasi, log, trace va Allure artefaktlarini tahlil qilishni so'rasa.
---

# Smoke Testlarni Ishga Tushirish

Argument: `$ARGUMENTS` (test nomi, fayl yoki bo'sh)

## Skill Chegarasi

Bu skill test executioni, log/trace/Allure artifactini yig'ish va run summaryni
egallaydi. Mavjud failurening root cause tahlili `debug-test`ga, runner/CI yoki
reporting subsystemi muammosi `maintain-test-infra`ga handoff qilinadi.

## User-reported Execution Qoidasi

### Testlarni faqat foydalanuvchi aniq so'raganda ishga tushirish
Status: user-reported
Verified: 2026-08-04
Source: user
- Qoida: foydalanuvchi aniq `run qil` deb aytmaguncha `pytest`,
  `scripts/run_tests.py`, test collection, smoke yoki boshqa test commandini
  avtomatik ishga tushirma. Kod o'zgarishidan keyin test ishga tushirilmaganini
  handoffda aniq ayt.
- `Tuzat`, `o'zgartir`, `amalga oshir`, `tekshir` yoki skill/reference'dagi
  verification commandi test execution ruxsati emas. Faqat userning aynan
  `run qil` buyrug'i execution authoritysi bo'ladi.

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
python scripts/run_tests.py setup-group-0 --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py group-0 --url <server_url> --company-code <company_code> --company-password <company_password>
python scripts/run_tests.py groups --url <server_url> --company-code <company_code> --company-password <company_password>
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
python -m pytest tests/smoke/test_setup/test_0_setup_runner.py::test_<nomi> -v
```

Repo rootda `.env` mavjud bo'lsa direct pytest/PyCharm run konfiguratsiyasi undan olinadi; `.env` yo'q bo'lsa terminal/CI flaglari ishlaydi.

### Code-dependent group-only run uchun majburiy preflight

- `group-0` va `groups` targetlari setup yaratmaydi; Group-0 testlari oldin
  muvaffaqiyatli tugagan setup baseline'dagi `code`ni qayta ishlatadi.
- Repo rootda `.env` bo'lsa `NEW_CODE` ham CLI'dan ustun. `NEW_CODE=1` bilan
  code-dependent group-only targetni ishlatma: fixture yangi random code yaratadi, lekin shu
  code uchun setup user/entitylar yaratilmagan bo'ladi. Runner bunday
  kombinatsiyani configuration error bilan bloklaydi.
- Group-0ni yangi baseline bilan tekshirish uchun `setup-group-0` ishlat:
  setup va Group-0 bitta pytest sessiyasida bir xil yangi `code` bilan yuradi.
- `group-0`ni alohida qayta run qilish faqat `.env`da `NEW_CODE=0` va
  `data_store.json.code` aynan joriy server/companydagi muvaffaqiyatli setupdan
  qolganiga ishonch bo'lsa to'g'ri.
- `group-report` testlari `code` fixturega bog'liq emas; template va download
  nomlarining unikalligi run-local UUID suffix bilan ta'minlanadi.

### Allure hisobot ko'rish:
```bash
./.venv/bin/python scripts/allure_report_cli.py generate test-results/allure-results --output test-results/allure-report --config allurerc.mjs
./.venv/bin/python scripts/open_allure_report.py test-results/allure-report
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
- `.env`dagi `NEW_CODE=1` group-only debug run uchun yaroqsiz; yangi code bilan
  setup ham shu sessiyada ishlashi kerak.
- Mavjud company bilan run qilish uchun `--company-code` va `--company-password` majburiy.
- Yangi company yaratish uchun `--create-company`, `--head-email` va `--head-password` majburiy.
- `--create-company` bilan `--company-code` va `--company-password` berilmaydi; company code test ichida `autotest<code>` ko'rinishida yaratiladi.
- Company setupda Security tabdagi `Политика лицензирования`ni off qilish kerak bo'lsa `--create-company --head-email <email> --head-password <password> --disable-license-policy` ishlatiladi.
- `--disable-license-policy` ishlatilsa `Buy License` va `Attach License` qadamlari o'tkazib yuboriladi.
- `pytest.ini` dagi `testpaths = tests` va `addopts` avtomatik qo'llanadi
- Trace fayllari `test-results/traces/` ga, Allure natijalar `test-results/allure-results/` ga yoziladi
- Lokal targetlar default ketma-ket jamlanadi: masalan `setup`dan keyingi
  `group-0` reportida setup natijalari ham qoladi. Yangi toza report boshlash
  uchun runnerga user-facing `--new-report` beriladi; `--clean-results` eski
  alias sifatida qoladi. Direct pytestga `CLEAN_ALLURE_RESULTS=1` beriladi.
- `scripts/run_tests.py` Allure reportni `--open-report` yoki shell/repo `.env` dagi `OPEN_REPORT=1` bilan ochadi.
- `scripts/run_tests.py` trace viewerini faqat `--show-trace` bo'lsa ochadi.
- Directory/default collectionda runner bo'lmagan smoke testlar duplicate flow bo'lmasligi uchun deselect qilinadi; leaf testni debug qilish uchun uning fayl yo'lini pytestga aniq ber.
- Full run setup runner va barcha group runner fayllarini bitta pytest sessiyasida collect qiladi; har bir setup/group case Allure'da alohida test bo'lib ko'rinadi.

## Test dependency modeli

Setup/group topology, cascade va markerlar uchun canonical manba:
[smoke-runner.md](../smartup-guide/references/smoke-runner.md). Run natijasini
shu model asosida tahlil qil; bu faylda topology qoidalarini takrorlama.
