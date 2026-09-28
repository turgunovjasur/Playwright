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
node --version
npm --version
```

**Windows (PowerShell):**
```powershell
python --version       # 3.11+ bo'lishi kerak
node --version
npm --version
```

Allure Report 3 CLI repo ichida `package-lock.json` bilan pin qilingan. Global
Allure CLI va Java o'rnatilmaydi; Node.js va npm yetarli.

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
npm ci
```

### <a id="chromium"></a>5. Chromium brauzerini o'rnatish

```bash
python -m playwright install chromium
```

> Linuxda birinchi marta tizim kutubxonalari yetishmasa: `python -m playwright install-deps chromium` (sudo so'rashi mumkin).

### <a id="test-credentiallari"></a>6. Test credentiallarini tayyorlash

Lokal `.env` bo'lsa, sozlamalar undan olinadi. Aks holda CLI yoki environment
qiymatlari ishlatiladi. Server URL har doim kerak: `COMPANY_URL` yoki `--url <server_url>`.
`URL` environment nomi ham alias sifatida qabul qilinadi; `COMPANY_URL` ustun.

User yaratish, uning parolini tasdiqlash va web/mobile user loginlari bitta
`USER_PASSWORD` qiymatidan foydalanadi. Uni lokal `.env` yoki shell environmentda
bering. `check_requiremants()` barcha runlar boshida, jumladan Forms/Report
uchun ham, bu parolni va ish rejimiga mos credentiallarni tekshiradi.
Mavjud setup userini ishlatganda uning haqiqiy parolini bering.

Tekshiruv qiymatlarni o'zgartirmaydi; xatolarni birga ko'rsatadi. Server URL
bo'sh joysiz va oxirida `/`siz yoziladi. Ixtiyoriy boolean flaglar faqat
`1` yoki `0` qabul qiladi; berilmasa o'chirilgan hisoblanadi. Testlar tekshirilgan
credentiallarni `os.environ`dan bevosita oladi.

Mavjud company bilan ishlaganda:

```bash
--company-code <company_code> --company-password <company_password>
```

Bu login pagega `admin@<company_code>` va `<company_password>` bilan kiradi.

Yangi company yaratganda:

```bash
--company-code 1 --head-email <head_email> --head-password <head_password>
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

Bu bitta buyruq: oldingi lokal raw natijalarni saqlaydi → smoke testlarni
o'tkazadi → yangi natijalarni oldingilar bilan birga Allure hisobotida
ko'rsatadi → brauzerda ochadi.
`--open-report` o'rniga shell env yoki repo `.env` ichida `OPEN_REPORT=1` ham ishlatish mumkin.

Butunlay yangi toza Allure report boshlash kerak bo'lsa user-facing
`--new-report` beriladi. Eski `--clean-results` aliasi backward compatibility
uchun saqlanadi. Direct pytest uchun ekvivalenti `CLEAN_ALLURE_RESULTS=1`:

```bash
python scripts/run_tests.py setup --url <server_url> --company-code <company_code> --company-password <company_password> --new-report --open-report
```

Bir xil test keyin qayta run qilinsa Allure 3 eng yangi natijani asosiy status
sifatida ko'rsatadi, avvalgi natijani esa retry ichida saqlaydi.

Yangi company yaratish kerak bo'lsa shu command ishlatiladi:

```bash
python scripts/run_tests.py --url <server_url> --company-code 1 --head-email <head_email> --head-password <head_password> --open-report
```

Test tugagach tizim xulosasi har doim yoziladi: `test-results/system-summary.md` va
`test-results/system-summary.json`. Bu AI emas; Allure JSON va tracebackdan
failed test, ichki Allure step, kod joyi va error turini chiqaradi.
Runner va direct pytest analizatorga run boshlanish vaqtini uzatadi; summary
natijalarni shu vaqt bo'yicha filtrlaydi. Allure report uchun oldingi raw
natijalarni saqlash tartibi davom etadi.

Testning yakuniy progress holati cleanup tugagach chiqariladi: istalgan faza
yiqilsa `FAILED`, xato bo'lmay skip bo'lsa `SKIPPED`, qolgan holatda `PASSED`.
Trace saqlashdagi xato contextni yopishni to'xtatmaydi. Qo'shimcha diagnostika
yoki log yozilmasa, `[REPORTING]` xabari chiqadi va asl test natijasi saqlanadi.

AI xulosa uchun `AI_ANALYSIS=1` va Gemini API key kerak. Kalitni lokal `.env`
yoki secret store orqali bering; repo va logga yozmang:

```bash
export GEMINI_API_KEY="<gemini_api_key>"
export AI_ANALYSIS=1
export AI_MAX_CASES=5
export GEMINI_MODEL=gemini-2.5-flash-lite
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --open-report
```

`AI_ANALYSIS=0` (default) AI'ni o'chiradi; `1` faqat failed run uchun yoqadi.
`AI_MAX_CASES=5` har analyzer/suite runidagi dastlabki beshta failed/broken
testni tanlaydi. Har tanlangan testga ko'pi bilan ikki AI so'rovi yuboriladi;
qolganlari limit sabab tahlil qilinmagani bilan Allure va summaryda saqlanadi.
Kalit bo'sh bo'lsa API chaqirilmaydi. AI tahlil yoqilganida qo'shimcha
`test-results/ai-summary.md` va `test-results/ai-summary.json` yoziladi.
Deterministic System Summary har doim tashqi Markdown/JSON artefakt bo'lib
qoladi va Allure test totaliga alohida pseudo-test qo'shmaydi. AI izohi har
failed testning Allure attachmentida ko'rinadi.

CI boshqaruvi: GitHub repository **Settings → Secrets and variables → Actions →
Variables** ichida `AI_ANALYSIS=1`, `AI_MAX_CASES=5`,
`GEMINI_MODEL=gemini-2.5-flash-lite` qo'ying. `GEMINI_API_KEY` esa **Secrets**da qoladi.
AI'ni o'chirish uchun faqat `AI_ANALYSIS=0` qiling; testlar va system summary
ishlashda davom etadi. Variables berilmasa workflow defaultlari `0`, `5` va
`gemini-2.5-flash-lite`. Sozlama keyingi joblarda olinadi; boshlangan analyzerga
ta'sir qilmaydi. Smoke, Report va Forms alohida job: limit har biriga alohida.
Noto'g'ri `AI_ANALYSIS` yoki AI yoqilgan failed run uchun musbat butun son
bo'lmagan `AI_MAX_CASES` AI configuration error beradi; API chaqirilmaydi,
yozilgan system summary va testning asl natijasi saqlanadi.

Telegram CI botning maxfiy bo'lmagan sozlamalari
[`telegram_bot/telegram_ci_config.json`](telegram_bot/telegram_ci_config.json)da:
GitHub repository/workflow/branch, serverlar va soatlik jadval tafsilotlari.
Bot, `/stop` CLI va CI server tanlovi shu fayldan o'qiydi. `.env`da bot tokenlari,
run paroli va `HOURLY_SCHEDULE_ENABLED` qoladi; eski GitHub/jadval environment
qiymatlari bot uchun ishlatilmaydi. Batafsil deploy va JSON yangilash tartibi
[`telegram_bot/deploy/README.md`](telegram_bot/deploy/README.md)da.
Telegram kodi, Windows launcher va deploy fayllari
[`telegram_bot/`](telegram_bot/README.md) papkasida jamlangan.

✅ Tayyor — hisobot brauzerda ochiladi. Report tabini yopsangiz, lokal server ham avtomatik to'xtaydi.
Keyinroq hisobotni qayta ochish uchun: `python scripts/open_allure_report.py`.

---

## <a id="talablar"></a>Talablar

- Python 3.11+
- Node.js va npm (`npm ci` project-local Allure 3 CLI'ni o'rnatadi)

---

## <a id="ornatish"></a>O'rnatish

```bash
python -m pip install -r requirements.txt
npm ci
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
| `--company-code <code>` | `1` — yangi kompaniya yaratadi; boshqa kod — mavjud kompaniya. |
| `--company-password <password>` | Mavjud company admin paroli. |
| `--head-email <email>` | Yangi company yaratish uchun head profil login emaili. |
| `--head-password <password>` | Yangi company yaratish uchun head profil paroli. |
| `--disable-license-policy` | Yangi companyda license policy ni off qiladi. |
| `--open-report` / `OPEN_REPORT=1` | Testdan keyin Allure reportni generate qilib ochadi. `OPEN_REPORT=1` shell env yoki repo `.env` ichida berilishi mumkin. |
| `--new-report` / `--clean-results` / `CLEAN_ALLURE_RESULTS=1` | Oldingi raw natijalarni o'chirib, yangi toza Allure report zanjirini boshlaydi. `--clean-results` eski alias; default lokal run oldingi natijalarni saqlaydi. |
| `--headless` | Browserni ko'rsatmasdan ishlatadi. |
| `--show-trace` / `SHOW_TRACE=1` | Testdan keyin oxirgi Playwright trace viewerini ochadi. `SHOW_TRACE=1` shell env yoki repo `.env` ichida berilishi mumkin. |
| `AI_ANALYSIS` | `1` — failed run uchun AI yoqiladi; `0` — o'chadi (default). |
| `AI_MAX_CASES` | Har suite/analyzer runidagi AI'ga yuboriladigan failed testlar limiti; musbat butun son, default `5`. |
| `GEMINI_MODEL` | Gemini model ID; default `gemini-2.5-flash-lite`. |
| `GEMINI_API_KEY` | AI yoqilganda API chaqiruvi uchun kalit; bo'sh bo'lsa chaqirilmaydi. |
| `--dry-run` | Testni ishga tushirmaydi, faqat pytest commandni ko'rsatadi. |
| `all` | Default target. Setup + Group-0 + Visit + Report + Forms runner ishlaydi. |
| `setup` | Faqat setup runner ishlaydi. |
| `regression-setup` | Regression uchun bazaviy setup: mavjud smoke run_* funksiyalari; mahsulot/kirim/aksiya kirmaydi. |
| `regression` | Asosiy regression runner: setup → hozir ulangan barcha regression domainlari (hozir ТМЦ). |
| `regression-products` | Mavjud setup bilan 3 manual TMZ testi + 3 mahsulotli bitta Excel import testi; karta va UZS/USD narxlash. |
| `setup-regression-products` | Regression bazaviy setup, keyin ТМЦ runneri; yangi muhit uchun. |
| `setup-group-0` | Setup, keyin Group-0 runnerni bitta sessiyada ishlatadi. |
| `setup-smoke` | CI Smoke targeti: Setup, Group-0 va Visit runnerlarni bitta sessiyada ishlatadi. |
| `setup-visit` | Setup, keyin Visit runnerni bitta sessiyada ishlatadi. |
| `setup-report` | Lokal target: Setup, keyin Report runner ishlaydi. |
| `setup-a2-admin` | Lokal compatibility target: Setup, keyin standalone `test_a2_angular_forms.py` ishlaydi. |
| `setup-forms` | Lokal compatibility target: Setup, keyin barcha form-opening testlar ishlaydi. |
| `company` | Faqat yangi company yaratish testi ishlaydi. |
| `groups` | Setupni ishlatmasdan Group-0, Visit va Report runnerlarni ishlatadi. |
| `group-0` | Faqat Group-0 ishlaydi. |
| `group-visit` | Faqat Visit group ishlaydi. |
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
python scripts/run_tests.py --url <server_url> --company-code 1 --head-email <head_email> --head-password <head_password>
```

Nima qiladi: head profilga kiradi, `autotest<test_code>` code bilan yangi company yaratadi, admin loginni `admin@autotest<test_code>` qilib ishlatadi, keyin full smoke testlarni shu companyda davom ettiradi.

#### Faqat yangi company yaratish

```bash
python scripts/run_tests.py company --url <server_url> --company-code 1 --head-email <head_email> --head-password <head_password>
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

Nima qiladi: saqlangan setup data bilan Group-0, Visit va Report runnerlarini ishlatadi.

#### Setup va Group-0

```bash
python scripts/run_tests.py setup-group-0 --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: setup va Group-0ni bitta pytest sessiyasida yangi code bilan
ishlatadi.

#### CI Smoke: Setup, Group-0 va Visit

```bash
python scripts/run_tests.py setup-smoke --url <server_url> --company-code <company_code> --company-password <company_password>
```

Nima qiladi: setup, Group-0 va Visit runnerlarini bitta pytest sessiyasida
yangi code bilan ishlatadi. Setup failed bo'lsa ikkala group skip qilinadi;
Group-0 va Visit bir-birining natijasiga bog'liq emas.

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
export AI_ANALYSIS=1
export AI_MAX_CASES=5
export GEMINI_MODEL=gemini-2.5-flash-lite
python scripts/run_tests.py --url <server_url> --company-code <company_code> --company-password <company_password> --open-report
```

Nima qiladi: tizim xulosasi har doim yoziladi. `AI_ANALYSIS=1` va
`GEMINI_API_KEY` berilsa failed run uchun `AI_MAX_CASES` chegarasida Gemini
qo'shimcha qisqa AI xulosa yozadi va
`test-results/ai-summary.md/json` saqlanadi. AI pass/fail, failed step yoki kod
joyini hal qilmaydi; bu faktlarni tizim o'zi chiqaradi.

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
python scripts/run_tests.py --url <server_url> --company-code 1 --head-email <head_email> --head-password <head_password> --dry-run
```

Nima qiladi: pytest commandni chiqaradi, lekin testlarni ishga tushirmaydi.

#### Yangi company yaratib license policy ni o'chirish

```bash
python scripts/run_tests.py --url <server_url> --company-code 1 --head-email <head_email> --head-password <head_password> --disable-license-policy
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
| `all` | `python scripts/run_tests.py --url <url> --company-code <code> --company-password <pass>` | Setup + Group-0 + Visit + Report + Forms runner |
| `setup` | `python scripts/run_tests.py setup --url <url> --company-code <code> --company-password <pass>` | Faqat user setup |
| `setup-group-0` | `python scripts/run_tests.py setup-group-0 --url <url> --company-code <code> --company-password <pass>` | User setup + Group-0 |
| `setup-smoke` | `python scripts/run_tests.py setup-smoke --url <url> --company-code <code> --company-password <pass>` | CI Smoke: User setup + Group-0 + Visit |
| `setup-visit` | `python scripts/run_tests.py setup-visit --url <url> --company-code <code> --company-password <pass>` | User setup + Visit |
| `setup-report` | `python scripts/run_tests.py setup-report --url <url> --company-code <code> --company-password <pass>` | User setup + Report group; lokal target |
| `setup-a2-admin` | `python scripts/run_tests.py setup-a2-admin --url <url> --company-code <code> --company-password <pass>` | User setup + standalone A2Angular; lokal compatibility target |
| `setup-forms` | `python scripts/run_tests.py setup-forms --url <url> --company-code <code> --company-password <pass>` | User setup + barcha form-opening testlar; lokal compatibility target |
| `company` | `python scripts/run_tests.py company --url <url> --company-code 1 --head-email <email> --head-password <pass>` | Faqat company yaratish testi |
| `groups` | `python scripts/run_tests.py groups --url <url> --company-code <code> --company-password <pass>` | Setupdan tashqari Group-0 + Visit + Report |
| `group-0` | `python scripts/run_tests.py group-0 --url <url> --company-code <code> --company-password <pass>` | Faqat Group-0 |
| `group-visit` | `python scripts/run_tests.py group-visit --url <url> --company-code <code> --company-password <pass>` | Faqat Visit group |
| `group-report` | `python scripts/run_tests.py group-report --url <url> --company-code <code> --company-password <pass>` | Faqat Report group |
| `forms` | `python scripts/run_tests.py forms --url <url> --company-code <code> --company-password <pass>` | Faqat Forms runner |

`--company-code 1` `all`, `setup`, `setup-smoke`, `setup-group-0`, `setup-visit`, `setup-forms` va `company`
targetlari bilan ishlatiladi. `groups`, `forms` va alohida group targetlari
uchun avval mavjud company va setup data kerak.

CI Smoke uchun `setup-smoke`, mustaqil Report job uchun `group-report`, Forms
uchun `forms` targetini alohida mavjud kompaniya kodi berilgan run sifatida ishlatadi;
serverga mos company code/password GitHub Secrets'dan olinadi. User yaratish va
login uchun repository Secrets'da `USER_PASSWORD` ham sozlangan bo'lishi kerak;
workflow uni test processiga environment orqali uzatadi. GitHub cron har
soatda Online Smoke va Report'ni mustaqil boshlaydi; Online Forms Smoke
tugagach, uning natijasidan qat'i nazar ishlaydi. Telegram bot manual menyusi
Smoke va Forms targetlarini taklif qiladi; Reportni GitHub Actions UI'dan
alohida manual dispatch qilish mumkin.

Code tanlovi `.env` dagi yagona `NEW_CODE` flagi bilan boshqariladi: `NEW_CODE=1` yangi 6 xonali code yaratadi, `NEW_CODE=0` esa `test-results/data/data_store.json` dagi mavjud code ni ishlatadi.

Company tanlovi faqat `COMPANY_CODE` bilan boshqariladi:

- `1` — kompaniya yaratish testi ishlaydi; yaratilgan `company_code` JSONga
  saqlanadi va qolgan testlarda ishlatiladi.
- Mavjud kompaniya kodi — yaratish testi tashlab ketiladi va qolgan testlar
  shu kompaniyada ishlaydi.

`0` orqali eski kompaniyani JSONdan tanlash rejimi yo'q. Alohida group run
uchun yaratilgan kompaniyaning haqiqiy kodini va `NEW_CODE=0` bering.

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
  --new-code --url <server_url> --company-code 1 --head-email <head_email> --head-password <head_password> -v
```

---

> **Muhim:** User setup testlari bir-biriga bog'liq — har biri oldingi test yaratgan ma'lumotdan foydalanadi.
> Full smoke uchun `python scripts/run_tests.py all` ishlating: runner Setup → Group-0 → Visit → Report → Forms fayllarini shu tartibda pytestga beradi. Suite uchun `run_tests.py` targetidan, yakka testni debug qilish uchun pytestga aniq fayl yoki `fayl::test_nomi` berishdan foydalaning. Oddiy `pytest` yoki papka runida runner va alohida testlar endi avtomatik ajratilmaydi; ikkalasi ham collect qilinishi mumkin. `COMPANY_CODE != 1` bo'lsa company yaratish testi ro'yxatdan chiqariladi.

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
| 00 | Company               | `--company-code 1` bilan company yaratish va code saqlash |
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

## Smoke va regression uchun umumiy infratuzilma

`tests/conftest.py` umumiy browser, context, page, loginli group page, `code`
va logger fixture'larini, CLI sozlamalarini hamda report lifecycle hooklarini
beradi. Fixture'larni import qilish kerak emas — pytest ularni test argumenti
orqali beradi.

`tests/shared/` ichida konfiguratsiya, browser lifecycle, authorization,
progress va diagnostika implementatsiyasi turadi. `tests/smoke/conftest.py`
faqat smoke setup/group dependency qoidalari va Forms metadata'sini boshqaradi.
Eski smoke helper import manzillari compatibility eksportlari orqali saqlangan;
yangi umumiy consumerlar `tests.shared`dan foydalanadi.

Smoke va regression setup ma'lumotlari uchun bitta `test-results/data/data_store.json`
hamda mavjud natija papkalaridan foydalanadi. TMZ natijalari test yonidagi
`tests/regression/test_products/data_store.json`ga yoziladi. Runlar ketma-ket bajariladi. Yangi setup yozgan
kalitlar yangilanadi, qolgan eski kalitlar avtomatik yangi baseline hisoblanmaydi.
Yangi regression ishlarining holati [regression-plan.md](regression-plan.md)da.

Regression bazaviy setup targeti:

```bash
python scripts/run_tests.py regression-setup
```

Lokal `.env` bo'lsa URL, company va `NEW_CODE` shu fayldan olinadi. Yangi setup
uchun `NEW_CODE=1` kerak. Ushbu target 21 ta alohida setup wrapperiga ega;
mavjud company rejimida Company itemi deselect qilinadi. Litsenziya qadamlari
mavjud smoke'dagi server/config shartlarini saqlaydi. Mahsulotlar, narxlash
caselari, kirim va order regressioni hali bu target tarkibiga kirmaydi.
`all` targetining mavjud smoke tarkibi o'zgarmagan.

Asosiy regression runner — `tests/regression/test_0_regression_runner.py`.
Oddiy pytest fayli: `Test01Setup`dan keyin `Test02Products` bajariladi.
U alohida runnerlardagi test funksiyalari, parametrlar va markerlarni qayta
ishlatadi. Har case alohida pytest/Allure natijasi bo'lib qoladi.

```bash
python -m pytest tests/regression/test_0_regression_runner.py
# Shu asosiy runner tarkibi umumiy CLI orqali ham ishlaydi:
python scripts/run_tests.py regression
```

Ikkalasi bir xil run uchun alternativ buyruqlar; ketma-ket ikkalasini bajarish
shart emas. PyCharm'da `test_0_regression_runner.py`ni repo `.venv`
interpreterida pytest bilan Run qilish mumkin. Alohida qismlar saqlanadi:

- Setup: `tests/regression/test_setup/test_0_setup_runner.py`.
- Mahsulotlar: `tests/regression/test_products/test_0_products_runner.py`.

ТМЦ uchun alohida targetlar:

```bash
python scripts/run_tests.py regression-products
python scripts/run_tests.py setup-regression-products
```

`regression-products` mavjud company va `NEW_CODE=0` bilan oldingi core setupni
ishlatadi. `regression` va `setup-regression-products` yangi core setup + mahsulot runnerini
bitta pytest sessiyasida bajaradi; lokal `.env` bo'lsa `NEW_CODE=1` shu faylda
beriladi. Domain-only run yangi code yoki mos code/filial baseline bo'lmasa
browser ochishdan oldin bloklanadi. Runner va uning standalone leaflarini
birga tanlash ham bloklanadi; CLI target faqat runnerni tanlaydi.
Asosiy runner bilan alohida setup/products runnerlarini birga tanlash ham
bloklanadi. Asosiy fayldagi node IDlar `Test01Setup::...` va
`Test02Products::...` bilan ajraladi; alohida runnerlarning node IDlari saqlanadi.

ТМЦ runnerida **2 ta testcase, 6 ta mahsulot** bor:

- TMZ-1: bitta yaratish testi; kod/nom search, view va ТМЦ listidan UZS/USD narxlash.
- TMZ-2, TMZ-3, TMZ-4, TMZ-5, TMZ-6: bitta 5 qatorli Excel import testi; to'plamga biriktirish, karta tekshiruvi va Цены listidan UZS/USD narxlash.

Barcha product qadamlari test fayllarida:
`test_01_create_product.py`da bitta manual test,
`test_02_import_products.py`da bitta import testi. Data, Excel tayyorlash,
UI va tekshiruvlar shu fayllardagi `run_product_full` va `run_import_product`
funksiyalarida, alohida product flow/helper papkasi yo'q. Product runner smoke
runner kabi `@allure.title` + `def test_*` wrapperlaridan shu `run_*`larni
chaqiradi. Standalone test wrapperlari ham bor. Asosiy va product runnerlarda
`test_01_tmz_1` va `test_02_import_tmz` bor. Base metodlari va umumiy fixturelar qayta ishlatiladi.

Barchasi `шт / Количество` (dona), `Товар`, birinchi ko'ringan ТМЦ to'plami va
`tmz-N-{code}` kodidan foydalanadi. Netto/brutto/hajm butun sonlar. Narxlar:
TMZ-1…6 uchun 5000/10000/15000/20000/25000/30000 UZS va 5/10/15/20/25/30 USD.
Har bir saqlangan narx qayta ochib tekshiriladi. View'da ko'rsatilmagan
birlik/to'plam Изменить formasida o'zgartirishsiz o'qiladi.

Import adminning alohida contextida bajariladi. Excel `openpyxl` bilan run
vaqtida yaratiladi; shablondagi mavjud mahsulot/IDlar ko'chirilmaydi. Schema
yoki mapping farq qilsa importdan oldin xato chiqadi. Fayl
`test-results/downloads/regression-tmz-{code}/TMZ-2-3-4-5-6.xlsx`da va Allure'da qoladi.

Natijalar `regression_tmz_1` … `regression_tmz_6` kalitlarida test yonidagi
`tests/regression/test_products/data_store.json`ga yoziladi. Har record
code/server/company bilan bog'langan. Karta va narxlar
tekshirilgandan so'ng `card_verified=True`, `price_verified=True`,
`stock_verified=False`: kirim/qoldiq va order hali yozilmagan.

Asosiy runner hozir setup + shu product testlarini birlashtiradi. Barcha
checklistlar [regression-plan.md](regression-plan.md) va [reliz.md](reliz.md)da.
**2026-09-22 local product run: 4 FAIL.** TMZ-1/2/3 karta va narxlari saqlanib,
yakuniy close locatorida xato bo'lgan; import preview input qiymatini matn deb
qidirgan. Ikkala locator tuzatildi, lekin tuzatishdan keyingi run bajarilmagan.
Shu koddagi TMZ-1/2/3 mavjud: full product retest uchun yangi setup/code bilan
asosiy regression runneridan foydalaning; kod yo'qligi tekshiruvi saqlanadi.

Smoke va regression setupni bir pytest sessiyasida tanlash bloklanadi: ular
bir xil session code bilan bir xil obyektlarni ikki marta yaratmasligi kerak.

## <a id="test-natijalari"></a>Test natijalari strukturasi

```
test-results/
├── allure-results/          # pytest tomonidan yoziladigan xom natijalar
│   ├── environment.properties
│   └── executor.json
├── allure-report/           # Allure 3 tomonidan render qilingan Awesome HTML
├── allure-history/
│   └── history.jsonl        # Allure 3 trend/status-transition tarixi
├── data/                    # Runnerlar orasida ishlatiladigan saqlangan code va test ma'lumotlari
│   └── data_store.json
├── playwright/              # pytest-playwright output papkasi
├── traces/                  # Playwright trace fayllari (.zip)
│   ├── smoke_trace.zip      # session_page ishlatgan testlar (to'liq sessiya)
│   └── *.zip                # group/page fixture ishlatgan testlar uchun alohida
├── logs/                    # Muvaffaqiyatsiz testlar uchun log fayllar
│   └── *.log
├── system-summary.md/json   # Har doim yoziladigan tizim xulosasi
└── ai-summary.md/json       # AI_ANALYSIS=1 + failed testcase mavjud bo'lsa AI holati/xulosasi
```

Allure 2'dagi `allure-report/history → allure-results/history` papka copy
lifecycle'i ishlatilmaydi. Allure 3 history migratsiyadan keyingi birinchi
generationdan `allure-history/history.jsonl`da boshlanadi; eski Allure 2
history avtomatik convert qilinmaydi.

---

## <a id="allure-hisoboti"></a>Allure hisoboti

### <a id="allure-yaratish-ochish"></a>Yaratish va ochish

```bash
# Natijalardan hisobot yaratish
python scripts/allure_report_cli.py generate \
  test-results/allure-results \
  --output test-results/allure-report \
  --config allurerc.mjs

# Hisobotni brauzerda ochish; report tabini yopganda server ham to'xtaydi
python scripts/open_allure_report.py
```

### <a id="allure-serve"></a>Tayyor reportni qayta ochish

```bash
python scripts/open_allure_report.py test-results/allure-report
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
