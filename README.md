# Playwright Smoke Tests — Smartup ERP

Playwright + pytest asosida yozilgan smoke test suite. Allure hisoboti va trace yozish o'rnatilgan.

---

## Mundarija

- [Tezkor boshlash](#tezkor-boshlash)
  - [Loyihani klon qilish](#loyihani-klon-qilish)
  - [Tizim talablarini tekshirish](#tizim-talablarini-tekshirish)
  - [Virtual muhit yaratish va aktivlashtirish](#virtual-muhit)
  - [Python paketlarini o'rnatish](#python-paketlari)
  - [Chromium brauzerini o'rnatish](#chromium)
  - [Test credentiallarini tayyorlash](#test-credentiallari)
  - [Testlarni ishga tushirish va hisobotni ochish](#testlarni-ishga-tushirish)
- [Talablar](#talablar)
- [O'rnatish](#ornatish)
- [Testlarni Run Qilish](#testlarni-run-qilish)
  - [Buyruqlar nima qiladi](#buyruqlar-nima-qiladi)
  - [Asosiy run yo'llari](#asosiy-run-yollari)
  - [Qo'shimcha buyruqlar](#qoshimcha-buyruqlar)
  - [Targetlar](#targetlar)
  - [Pytest Orqali Debug](#pytest-orqali-debug)
- [Test qamrovi](#test-qamrovi)
  - [Setup runner](#setup-runner)
  - [Group runnerlar](#group-runnerlar)
- [Test natijalari strukturasi](#test-natijalari)
- [Allure hisoboti](#allure-hisoboti)
  - [Yaratish va ochish](#allure-yaratish-ochish)
  - [Faqat serve qilish](#allure-serve)
- [Trace Viewer](#trace-viewer)
  - [Eng oxirgi traceni ochish](#eng-oxirgi-trace)
  - [Muayyan test traceni ochish](#muayyan-trace)
  - [Trace viewer imkoniyatlari](#trace-imkoniyatlari)
- [Codegen](#codegen)
  - [Ishga tushirish](#codegen-ishga-tushirish)
  - [Foydalanish tartibi](#codegen-foydalanish)
- [Foydali buyruqlar](#foydali-buyruqlar)

---

## <a id="tezkor-boshlash"></a>🚀 Tezkor boshlash — gitdan klon qilgandan hisobot olgungacha

Loyihani yangi olgan odam quyidagi qadamlarni **ketma-ket** bajaradi. Buyruqlar **macOS, Linux va Windows** uchun alohida berilgan — o'z tizimingizdagi varianti bo'yicha yuring. Oxirida testlar ishga tushadi va Allure hisoboti brauzerda ochiladi.

### <a id="loyihani-klon-qilish"></a>1. Loyihani klon qilish

Barcha tizimlarda bir xil:

```bash
git clone https://github.com/turgunovjasur/Playwright.git
cd Playwright
```

### <a id="tizim-talablarini-tekshirish"></a>2. Tizim talablarini tekshirish

**macOS / Linux:**
```bash
python3 --version      # 3.11+ bo'lishi kerak
allure --version
```

**Windows (PowerShell):**
```powershell
python --version       # 3.11+ bo'lishi kerak
allure --version
```

Allure CLI yo'q bo'lsa (barchasi uchun Java JDK 8+ ham kerak):

| Tizim   | O'rnatish buyrug'i |
|---------|--------------------|
| macOS   | `brew install allure` |
| Linux   | `brew install allure` yoki [scoop/manual](https://allurereport.org/docs/install/) |
| Windows | `scoop install allure` yoki `choco install allure-commandline` ([qo'llanma](https://allurereport.org/docs/install/)) |

> Python yo'q bo'lsa → https://www.python.org/downloads/ (Windowsda o'rnatishda **"Add Python to PATH"** ni belgilang).

### <a id="virtual-muhit"></a>3. Virtual muhit yaratish va aktivlashtirish

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

> Windows PowerShell'da script ishga tushmasa (execution policy xatosi), bir marta:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### <a id="python-paketlari"></a>4. Python paketlarini o'rnatish

Virtual muhit aktiv bo'lgach, barcha tizimda bir xil:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### <a id="chromium"></a>5. Chromium brauzerini o'rnatish

```bash
python -m playwright install chromium
```

> Linuxda birinchi marta tizim kutubxonalari yetishmasa: `python -m playwright install-deps chromium` (sudo so'rashi mumkin).

### <a id="test-credentiallari"></a>6. Test credentiallarini tayyorlash

`.env` ishlatilmaydi. Har bir run uchun server URL kerak: `--url <server_url>`.

Mavjud company bilan ishlaganda:

```bash
--company-code <company_code> --company-password <company_password>
```

Bu login pagega `admin@<company_code>` va `<company_password>` bilan kiradi.

Yangi company yaratganda:

```bash
--create-company --head-email <head_email> --head-password <head_password>
```

Bu avval head profilga kiradi, keyin company code ni `autotest<test_code>` ko'rinishida test ichida yaratadi. Yangi company admin paroli test ichidagi default qiymat.

### <a id="testlarni-ishga-tushirish"></a>7. Testlarni ishga tushirish va hisobotni ochish

Barcha tizimda bir xil (cross-platform Python runner):

```bash
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --open-report
```

macOS / Linuxda qisqa wrapper ham bor:

```bash
./run_tests.sh --url <server_url> --company-code <company_code> --company-password <company_password> --open-report
```

Bu bitta buyruq: eski natijalarni tozalaydi → smoke testlarni o'tkazadi → Allure hisobotini yaratadi → brauzerda ochadi.
`--open-report` o'rniga shell env yoki repo `.env` ichida `OPEN_REPORT=1` ham ishlatish mumkin.

Yangi company yaratish kerak bo'lsa shu command ishlatiladi:

```bash
python scripts/run_tests.py --url <server_url> --create-company --head-email <head_email> --head-password <head_password> --open-report
```

Test tugagach tizim xulosasi har doim yoziladi: `test-results/system-summary.md` va
`test-results/system-summary.json`. Bu AI emas; Allure JSON va tracebackdan
failed test, ichki Allure step, kod joyi va error turini chiqaradi.

AI xulosa kerak bo'lsa Gemini API keyni environment variable qilib bering. Key repo yoki commandga yozilmaydi:

```bash
export GEMINI_API_KEY="<gemini_api_key>"
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --ai-summary --open-report
```

AI default holatda off. `--ai-summary` flagi berilsa testdan keyin qo'shimcha
`test-results/ai-summary.md` va `test-results/ai-summary.json` yozadi. Allure
report ichida `System Test Summary` har doim, `AI Test Summary` esa faqat
`--ai-summary` bilan ko'rinadi.

✅ Tayyor — hisobot brauzerda ochiladi. Report tabini yopsangiz, lokal server ham avtomatik to'xtaydi.
Keyinroq hisobotni qayta ochish uchun: `python scripts/open_allure_report.py`.

---

## <a id="talablar"></a>Talablar

- Python 3.11+
- [Allure CLI](https://allurereport.org/docs/install/) (`brew install allure`)

---

## <a id="ornatish"></a>O'rnatish

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

---

## <a id="testlarni-run-qilish"></a>Testlarni Run Qilish

Asosiy runner shu:

```bash
python scripts/run_tests.py [target] --url <server_url> [company mode] [options]
```

Bu buyruq macOS, Linux va Windowsda ishlaydi. Repo rootida `.env` mavjud
bo'lsa runner mode va credentiallarni undan oladi; `.env` bo'lmasa CLI flaglari
ishlatiladi.

### <a id="buyruqlar-nima-qiladi"></a>Buyruqlar nima qiladi

| Buyruq/flag | Nima qiladi |
|-------------|-------------|
| `--url <server_url>` | Test ishlaydigan Smartup server URL. Har doim kerak. |
| `--company-code <code>` | Mavjud company code. Test loginni `admin@<code>` qilib yasaydi. |
| `--company-password <password>` | Mavjud company admin paroli. |
| `--create-company` | Test boshida yangi company yaratadi. |
| `--head-email <email>` | Yangi company yaratish uchun head profil login emaili. |
| `--head-password <password>` | Yangi company yaratish uchun head profil paroli. |
| `--disable-license-policy` | Yangi companyda license policy ni off qiladi. |
| `--open-report` / `OPEN_REPORT=1` | Testdan keyin Allure reportni generate qilib ochadi. `OPEN_REPORT=1` shell env yoki repo `.env` ichida berilishi mumkin. |
| `--headless` | Browserni ko'rsatmasdan ishlatadi. |
| `--show-trace` / `SHOW_TRACE=1` | Testdan keyin oxirgi Playwright trace viewerini ochadi. `SHOW_TRACE=1` shell env yoki repo `.env` ichida berilishi mumkin. |
| `--ai-summary` | Gemini orqali qo'shimcha AI xulosa yozadi. Default: off. |
| `--dry-run` | Testni ishga tushirmaydi, faqat pytest commandni ko'rsatadi. |
| `all` | Default target. Setup + Group-0 + Report + Forms runner ishlaydi. |
| `setup` | Faqat setup runner ishlaydi. |
| `setup-group-0` | Setup, keyin Group-0 runnerni bitta sessiyada ishlatadi. |
| `setup-report` | Lokal target: Setup, keyin Report runner ishlaydi. |
| `setup-a2-admin` | Lokal compatibility target: Setup, keyin standalone `test_a2_angular_forms.py` ishlaydi. |
| `setup-forms` | CI/bot targeti: Setup, keyin barcha form-opening testlar ishlaydi. |
| `company` | Faqat yangi company yaratish testi ishlaydi. |
| `groups` | Setupni ishlatmasdan Group-0 va Report runnerlarni ishlatadi. |
| `group-0` | Faqat Group-0 ishlaydi. |
| `group-report` | Faqat Report group ishlaydi. |
| `forms` | Setupni ishlatmasdan faqat Forms runner ishlaydi. |

### <a id="asosiy-run-yollari"></a>Asosiy run yo'llari

#### Mavjud company bilan full smoke

```bash
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: mavjud companyga `admin@<company_code>` login va
`<company_password>` parol bilan kiradi, setup, Group-0, Report hamda Forms
runnerlarini ishlatadi.

#### Yangi company yaratib full smoke

```bash
python scripts/run_tests.py --url <server_url> --create-company --head-email <head_email> --head-password <head_password>
```

Nima qiladi: head profilga kiradi, `autotest<test_code>` code bilan yangi company yaratadi, admin loginni `admin@autotest<test_code>` qilib ishlatadi, keyin full smoke testlarni shu companyda davom ettiradi.

#### Faqat yangi company yaratish

```bash
python scripts/run_tests.py company --url <server_url> --create-company --head-email <head_email> --head-password <head_password>
```

Nima qiladi: faqat `00 - Company` testini ishlatadi va company code ni `test-results/data/data_store.json` ga saqlaydi.

#### Faqat setup runner

```bash
python scripts/run_tests.py setup --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: faqat user setup zanjirini ishlatadi.

#### Barcha grouplar, setupdan tashqari

```bash
python scripts/run_tests.py groups --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: saqlangan setup data bilan Group-0 va Report runnerlarini ishlatadi.

#### Setup va Group-0

```bash
python scripts/run_tests.py setup-group-0 --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: setup va Group-0ni bitta pytest sessiyasida yangi code bilan
ishlatadi.

#### Faqat Group-0

```bash
python scripts/run_tests.py group-0 --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: saqlangan setup baseline bilan Group-0 testlarini ishlatadi.

#### Faqat Report group

```bash
python scripts/run_tests.py group-report --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: saqlangan setup data bilan Report group testlarini ishlatadi (CisLink, Integration Three, SalesWork, Optimum, Spot 2d, Integration Two). Report testlar bir-biriga bog'liq emas — biri yiqilsa qolganlari davom etadi.

### <a id="qoshimcha-buyruqlar"></a>Qo'shimcha buyruqlar

#### Allure reportni testdan keyin ochish

```bash
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --open-report
```

Nima qiladi: test tugagandan keyin Allure reportni generate qilib ochadi.

#### Gemini AI xulosa bilan run qilish

```bash
export GEMINI_API_KEY="<gemini_api_key>"
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --ai-summary --open-report
```

Nima qiladi: tizim xulosasi har doim yoziladi. `--ai-summary` berilganda Gemini qo'shimcha 1-2 gaplik AI xulosa yozadi va `test-results/ai-summary.md/json` saqlanadi. AI pass/fail, failed step yoki kod joyini hal qilmaydi; bu faktlarni tizim o'zi chiqaradi.

#### Browserni ko'rsatmasdan ishlatish

```bash
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --headless
```

Nima qiladi: Chromium headless rejimda ishlaydi.

#### Oxirgi trace ni ochish

```bash
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --show-trace
```

Nima qiladi: testdan keyin oxirgi Playwright trace viewerini ochadi.

#### Commandni faqat ko'rish

```bash
python scripts/run_tests.py --url <server_url> --create-company --head-email <head_email> --head-password <head_password> --dry-run
```

Nima qiladi: pytest commandni chiqaradi, lekin testlarni ishga tushirmaydi.

#### Yangi company yaratib license policy ni o'chirish

```bash
python scripts/run_tests.py --url <server_url> --create-company --head-email <head_email> --head-password <head_password> --disable-license-policy
```

Nima qiladi: yangi company yaratadi, company Security tabida `Политика лицензирования` ni off qiladi, license sotib olish va ulash qadamlari skip bo'ladi.

#### macOS/Linux wrapper

```bash
./run_tests.sh --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: `python scripts/run_tests.py ...` ni qisqa wrapper orqali ishlatadi.

### <a id="targetlar"></a>Targetlar

Default target `all`, ya'ni full suite.

| Target | Buyruq namunasi | Nima ishlaydi |
|--------|------------------|---------------|
| `all` | `python scripts/run_tests.py --url <url> --company-code <code> --company-password <pass>` | Setup + Group-0 + Report + Forms runner |
| `setup` | `python scripts/run_tests.py setup --url <url> --company-code <code> --company-password <pass>` | Faqat user setup |
| `setup-group-0` | `python scripts/run_tests.py setup-group-0 --url <url> --company-code <code> --company-password <pass>` | User setup + Group-0 |
| `setup-report` | `python scripts/run_tests.py setup-report --url <url> --company-code <code> --company-password <pass>` | User setup + Report group; lokal target |
| `setup-a2-admin` | `python scripts/run_tests.py setup-a2-admin --url <url> --company-code <code> --company-password <pass>` | User setup + standalone A2Angular; lokal compatibility target |
| `setup-forms` | `python scripts/run_tests.py setup-forms --url <url> --company-code <code> --company-password <pass>` | User setup + barcha form-opening testlar; CI/bot shu targetni ishlatadi |
| `company` | `python scripts/run_tests.py company --url <url> --create-company --head-email <email> --head-password <pass>` | Faqat company yaratish testi |
| `groups` | `python scripts/run_tests.py groups --url <url> --company-code <code> --company-password <pass>` | Setupdan tashqari Group-0 + Report |
| `group-0` | `python scripts/run_tests.py group-0 --url <url> --company-code <code> --company-password <pass>` | Faqat Group-0 |
| `group-report` | `python scripts/run_tests.py group-report --url <url> --company-code <code> --company-password <pass>` | Faqat Report group |
| `forms` | `python scripts/run_tests.py forms --url <url> --company-code <code> --company-password <pass>` | Faqat Forms runner |

`--create-company` `all`, `setup`, `setup-group-0`, `setup-forms` va `company`
targetlari bilan ishlatiladi. `groups`, `forms` va alohida group targetlari
uchun avval mavjud company va setup data kerak.

CI/Telegram botdagi `setup-forms` targeti `CREATE_COMPANY=0` bilan ishlaydi:
serverga mos company code/password GitHub Secrets'dan olinadi.

Code tanlovi `.env` dagi yagona `NEW_CODE` flagi bilan boshqariladi: `NEW_CODE=1` yangi 6 xonali code yaratadi, `NEW_CODE=0` esa `test-results/data/data_store.json` dagi mavjud code ni ishlatadi.

Company tanlovi alohida boshqariladi: existing rejimda `COMPANY_CODE=0`
berilsa `test-results/data/data_store.json` dagi oxirgi saqlangan
`company_code` ishlatiladi. Bu alohida tugagan `CREATE_COMPANY=1` setup
sessiyasidan keyin group runnerlarni o'sha company va `NEW_CODE=0` bilan
davom ettirish uchun ishlatiladi.

### <a id="pytest-orqali-debug"></a>Pytest Orqali Debug

Asosiy run uchun `scripts/run_tests.py` ishlatish tavsiya qilinadi. Debug uchun to'g'ridan-to'g'ri pytest yuritish mumkin:

```bash
./.venv/bin/pytest \
  tests/smoke/test_setup/test_0_setup_runner.py \
  tests/smoke/test_groups/test_a_grup/test_0_group_runner.py \
  tests/smoke/test_groups/test_report_grup/test_0_group_runner.py \
  --new-code --url <server_url> --company-code <company_code> --company-password <company_password> -v
```

Yangi company bilan:

```bash
./.venv/bin/pytest \
  tests/smoke/test_setup/test_0_setup_runner.py \
  tests/smoke/test_groups/test_a_grup/test_0_group_runner.py \
  tests/smoke/test_groups/test_report_grup/test_0_group_runner.py \
  --new-code --url <server_url> --create-company --head-email <head_email> --head-password <head_password> -v
```

---

> **Muhim:** User setup testlari bir-biriga bog'liq — har biri oldingi test yaratgan ma'lumotdan foydalanadi.
> Full smoke setup runner, keyin Group-0 va Report runner fayllarini shu tartibda bitta pytest sessiyasida collect qiladi. Oddiy `pytest` yoki directory collection duplicate flowlarni yurgizmasligi uchun runner bo'lmagan smoke testlar deselect qilinadi. Leaf testni debug qilish uchun uning fayl yo'lini pytestga aniq bering.

---

## <a id="test-qamrovi"></a>Test qamrovi

`scripts/run_tests.py` — full run uchun Setup, Group-0, Report va Forms runner
fayllarini ketma-ket pytest targetlari sifatida beradi. Alohida outer
`test_all_runner.py` ishlatilmaydi.

`tests/smoke/test_setup/test_0_setup_runner.py` — user setup testlari **bitta browser sessiyasida** ketma-ket ishlaydi.

Group runnerlar — har bir case alohida pytest/Allure test. User grouplarida group boshida bir marta login qilinadi va testlar shu module-scoped oynada davom etadi; keyingi group yangi context/page bilan boshlanadi.

### <a id="setup-runner"></a>Setup runner

| # | Test nomi              | Nima tekshiriladi                                     |
|---|------------------------|-------------------------------------------------------|
| 00 | Company               | `--create-company` bilan company yaratish va code saqlash |
| 01 | Legal Person          | Admin login, yuridik shaxs yaratish va qidirish       |
| 02 | Filial                | Organizatsiya yaratish, valyuta va yuridik shaxs bog'lash |
| 03 | Room                  | Ish zonasi yaratish                                   |
| 04 | Robot                 | Shtat birligini yaratish                              |
| 05 | Natural Person        | Jismoniy shaxs yaratish                               |
| 06 | User                  | Foydalanuvchi yaratish va robot/jismoniy shaxs bog'lash |
| 07 | User Attach Form      | Foydalanuvchiga formalar biriktirish                  |
| 08 | Role                  | Admin roliga barcha ruxsatlar berish                  |
| 09 | Role Attach Form      | Rolga barcha formlarga kirish ruxsatini berish        |
| 10 | Buy License           | Litsenziya sotib olish                                |
| 11 | Attach License        | Foydalanuvchiga litsenziya biriktirish                |
| 12 | Change Password       | Yangi foydalanuvchi parolini o'zgartirish             |
| 13 | Price Type UZB        | UZB narx turini yaratish                              |
| 14 | Price Type USA        | USA narx turini yaratish                              |
| 15 | Currency              | Valyuta yaratish                                      |
| 16 | Payment Type          | To'lov turini yaratish                                |
| 17 | Sector                | TMT to'plami (Набор ТМЦ) yaratish                     |
| 18 | Product               | TMT (mahsulot) yaratish                               |
| 19 | Natural Person For Client 1 | Qo'shimcha client uchun jismoniy shaxs yaratish |
| 20 | Room Attachment       | Ish zonasiga kerakli bog'lanishlarni biriktirish      |
| 21 | Init Balance          | Boshlang'ich qoldiq uchun hujjat yaratish             |
| 22 | Balance               | Qoldiq/harakatlar hayot siklini tekshirish            |

### <a id="group-runnerlar"></a>Group runnerlar

| Group | Runner buyrug'i | Nima tekshiriladi |
|-------|-----------------|-------------------|
| Group-0 | `group-0` | Setup baseline asosida base order create → list → view happy pathi |
| Report | `group-report` | CisLink, Integration Three, SalesWork, Optimum, Spot 2d, Integration Two — har biri mustaqil |

> **Eslatma:** Report group testlari `independent=True` — biri yiqilsa
> qolganlari davom etadi. Group-0 default chain qoidasida ishlaydi.

---

## <a id="test-natijalari"></a>Test natijalari strukturasi

```
test-results/
├── allure-results/          # pytest tomonidan yoziladigan xom natijalar
│   ├── history/             # Trend grafigi uchun tarix
│   ├── environment.properties
│   ├── executor.json
│   └── categories.json
├── allure-report/           # Allure CLI tomonidan render qilingan HTML
├── data/                    # Runnerlar orasida ishlatiladigan saqlangan code va test ma'lumotlari
│   └── data_store.json
├── playwright/              # pytest-playwright output papkasi
├── traces/                  # Playwright trace fayllari (.zip)
│   ├── smoke_trace.zip      # session_page ishlatgan testlar (to'liq sessiya)
│   └── *.zip                # group/page fixture ishlatgan testlar uchun alohida
├── logs/                    # Muvaffaqiyatsiz testlar uchun log fayllar
│   └── *.log
├── system-summary.md/json   # Har doim yoziladigan tizim xulosasi
└── ai-summary.md/json       # Faqat --ai-summary bilan yoziladigan AI xulosa
```

---

## <a id="allure-hisoboti"></a>Allure hisoboti

### <a id="allure-yaratish-ochish"></a>Yaratish va ochish

```bash
# Natijalardan hisobot yaratish
allure generate test-results/allure-results -o test-results/allure-report --clean

# Hisobotni brauzerda ochish; report tabini yopganda server ham to'xtaydi
python scripts/open_allure_report.py
```

### <a id="allure-serve"></a>Faqat serve qilish (papkani yaratmasdan)

```bash
allure serve test-results/allure-results
```

---

## <a id="trace-viewer"></a>Trace Viewer

Test xato bo'lganda Playwright avtomatik `.zip` trace saqlaydi.

### <a id="eng-oxirgi-trace"></a>Eng oxirgi traceni ochish

```bash
playwright show-trace $(ls -t test-results/traces/*.zip | head -1)
```

### <a id="muayyan-trace"></a>Muayyan test traceni ochish

```bash
# Fayl nomini ko'rish
ls test-results/traces/

# Kerakli traceni ochish
playwright show-trace test-results/traces/smoke_trace.zip
```

### <a id="trace-imkoniyatlari"></a>Trace viewer imkoniyatlari

- **Timeline** — har bir action vaqt bo'yicha
- **Screenshots** — har bir qadam skrinshotlari
- **Network** — barcha tarmoq so'rovlari
- **Console** — brauzer konsol xabarlari
- **Source** — test kodi qaysi qatorda ekanligini ko'rsatadi

---

## <a id="codegen"></a>Codegen — locator yozishda yordam

Playwright Codegen brauzerda harakatlarni yozib, avtomatik test kodi generatsiya qiladi. Yangi locator topishda ishlatiladi.

### <a id="codegen-ishga-tushirish"></a>Ishga tushirish

```bash
# URL ga o'tib codegen ochish
playwright codegen <server_url>

# Login sahifasidan boshlash
playwright codegen <server_url>/login.html
```

### <a id="codegen-foydalanish"></a>Foydalanish tartibi

1. `playwright codegen <url>` buyrug'ini terminalda ishga tushiring
2. Brauzerda kerakli sahifaga o'ting va amallarni bajaring
3. Hosil bo'lgan kodni o'ng oynadan nusxa olib test fayliga qo'ying
4. Kerak bo'lmagan qatorlarni olib tashlang

> Codegen yozgan locatorlarni to'g'ridan-to'g'ri ishlatmasdan, mavjud `flow_navigate.py`, `flow_authorization.py` patterlariga mos tarzda adaptatsiya qiling.

---

## <a id="foydali-buyruqlar"></a>Foydali buyruqlar

```bash
# Testlarni headless rejimda ishlatish
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --headless

# Faqat muvaffaqiyatsiz testlarni qayta ishlatish
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --lf

# Xato bo'lganda darhol to'xtatish
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> -x

# Verbose + to'liq xato traceback
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --tb=long
```
