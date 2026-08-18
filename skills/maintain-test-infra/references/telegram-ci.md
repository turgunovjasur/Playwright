# Telegram CI

## Mundarija

- [Current architecture](#current-architecture)
- [Progress va final xabar](#progress-va-final-xabar)
- [Security](#security)
- [Windows deploy](#windows-deploy)
- [Verification](#verification)

## Current architecture

Status: code-confirmed
Verified: 2026-08-18
Source: `scripts/telegram_ci_bot.py`; `.github/workflows/daily-smoke.yml`;
`.github/workflows/run-smartup-suite.yml`; `scripts/telegram_progress.py`;
`tests/smoke/progress.py`; `scripts/analyze_test_result.py`

- GitHub Actions test execution va har soatlik schedulingning yagona
  authoritysi; `daily-smoke.yml`dagi `cron: "0 * * * *"` saqlangan.
- Cron har soatda avval `Online Smoke`, keyin `Online Forms`ni alohida reusable
  workflow job sifatida ishlatadi. Forms job `if: always()` bilan Smoke
  natijasidan qat'i nazar boshlanadi.
- `Smoke` `scripts/run_tests.py setup-group-0`, `Forms` esa
  `scripts/run_tests.py forms` targetini bajaradi. Har job o'z Telegram
  progress/final xabari, `test-results`, HTML Allure reporti va artifactiga ega.
- Windows serverdagi bot faqat manual trigger qiladi; bot auto-run loopi va
  `AUTO_RUN_*` konfiguratsiyasi olib tashlangan.
- Manual flow: avval suite (`Smoke` yoki `Forms`), keyin server (`Online` yoki
  `Xtrade`), so'ng run password authorizationi tanlanadi.
- `/status` oxirgi scheduled yoki manual workflow holati, run linki, Smoke/Forms
  Telegram delivery holati va bot processining oxirgi redacted Telegram API
  xatosini ko'rsatadi. Delivery holati katta test artifactidan emas, alohida
  kichik `*-telegram-status` artifactidan o'qiladi.
- Workflow erkin URL qabul qilmaydi: `smartup` yoki `app3` keyidan URL hamda
  secret source ichkarida hosil qilinadi, boshqa key fail-closed rad etiladi.
- Bot in-memory manual run bilan birga GitHub API orqali scheduled/manual active
  workflow runlarni ham tekshiradi. Active run bo'lsa yangi manual dispatch
  queue'ga qo'shilmaydi va `Test jarayonda, yangi run boshlanmadi` mazmunidagi
  Telegram xabari bilan rad etiladi.
- Bot workflow'ni `main` ref va `daily-smoke.yml` bilan dispatch qiladi;
  `smartup` va `app3` serverlari alohida secret source ishlatadi.
- GitHub status polling vaqtinchalik API/network xatosini retry qiladi; ketma-ket
  5 xatodan keyin failure sifatida chiqaradi.
- Telegramga ZIP yuborilmaydi; final xabarda qisqa natija va GitHub run linki
  beriladi, to'liq test natijalari suite'ga mos artifactda saqlanadi.

## Progress va final xabar

- Progress bitta edit-in-place Telegram message'da yuradi; workflow final
  xabardan keyin progress message'ni yakunlaydi.
- Test processi boshlanguncha progress xabari soxta elapsed taymerni
  ko'rsatmaydi: `Bosqich` va CI boshlanish timestampi chiqadi. Workflow
  kutubxonalar o'rnatilishi, Playwright browser o'rnatilishi va test boshlanishi
  orasida statusni darhol edit qiladi. `O'tgan vaqt` faqat test processi
  boshlanganidan keyin `test_started_epoch` asosida hisoblanadi.
- Pytest eventlari lokal state'ga darhol yoziladi, ammo Telegram progress xabari
  10 soniyadan tez edit qilinmaydi. Oraliq eventlar bitta editga jamlanadi va
  render qilingan matn o'zgarmagan bo'lsa API chaqirilmaydi.
- Oddiy progress `429` olsa `retry_after` tugaguncha yangi edit yubormaydi;
  test processi Telegram flood-control kutishi bilan bloklanmaydi.
- Final `PASSED`/`FAILED` xabari throttle'dan mustasno. `429`, network timeout
  yoki `5xx`da umumiy kutish budjeti 10 soniyadan oshmagan holda uch martagacha
  retry qilinadi. Telegram uzoq `retry_after` qaytarsa CI soatlab uxlamaydi:
  delivery failure va keyingi retry vaqti status artifactiga yozilib, workflow
  davom etadi. HTML `400` format xatosida plain-text retry ishlaydi; `401/403`
  qayta urinilmaydi.
- Eski progress message'ni final holatga edit qilish bajarilmasa yangi final
  `sendMessage` yuboriladi. Retry bilan tuzalgan Telegram xatosi final xabarning
  `Telegram notification` ogohlantirishida userga ko'rsatiladi.
- Final delivery natijasi `test-results/telegram-delivery.json`, GitHub Step
  Summary va `*-telegram-status` artifactida saqlanadi. Barcha urinishlar
  tugasa Telegramga xabar yetmasligi mumkin; bunday holat GitHub warning va
  keyingi `/status` javobida ko'rinadi, testning haqiqiy conclusioni esa
  o'zgarmaydi.
- Windows bot Telegram `429`da faqat 10 soniyagacha bounded kutadi; uzoq
  `retry_after` main command loopni bloklamaydi. Har metodning cooldown vaqti
  xotirada saqlanadi, shu vaqt ichida o'sha metod API'ga qayta urilmaydi.
  Parol xabarini `deleteMessage` qilish best-effort va retrysiz: delete xatosi
  parolni tekshirish yoki workflow dispatchini to'xtatmaydi. `/status` botning
  joriy/oldingi redacted xatosi bilan birga qolgan cooldown yoki artifactdagi
  Telegram talab qilgan kutish hamda retry vaqtini ko'rsatadi.
- Pytest progress eventlari `tests/smoke/smoke_reporting.py` va
  `scripts/telegram_progress.py` orqali group/runner/test/title asosida chiqadi;
  har bir event millisekund aniqligidagi UTC timestamp saqlaydi.
- Canonical Forms runnerda har bir forma alohida pytest/Allure item bo'ladi;
  analyzer parametr IDidagi navbarni tanib, barcha beshta navbar coverage'ini
  umumiy `Forms: muvaffaqiyatli/jami` metrikasiga qo'shadi.
- Forms live progress barcha itemlarni Telegramning bitta xabariga yig'maydi.
  Limit-safe dashboard `completed/total`, foiz, passed/skipped hisoblari,
  elapsed time va `global number · forma`, `navbar → menu`, filial
  ko'rinishidagi faqat joriy formani ko'rsatadi; oxirgi passed formalar ro'yxati
  chiqarilmaydi. Operatsion filial placeholderi userga `Operatsion filial` deb
  chiqariladi.
- Forms pytest itemining Telegram display nomi Allure decoratoridagi unresolved
  `{form_case[...]}` shablonidan olinmaydi; pytest `callspec`dagi structured
  `form_case` metadata'sidan resolve qilinadi. Bu Allure title, pytest ID va
  historyni o'zgartirmaydi.
- Failed final xabarda mavjud structured monitor/system-summary dalillari bilan
  forma raqami va nomi, navbar, menu, filial, expected/actual URL, sabab hamda
  failure event vaqti UZT va UTCda ko'rsatiladi. Allure `stop` vaqti system
  summaryda fallback timestamp bo'ladi. Passed formaning to'liq texnik
  metadata'si Allure'da qoladi.
- Final xabarda credential emas, faqat data-store'dagi parametrik run `code`
  `Test data kodi` nomi bilan ko'rsatilishi mumkin; canonical `forms` targetida
  bu qator chiqarilmaydi.
- Failure tafsiloti log va Allure'dagi faktlardan tuziladi: group, runner test,
  ichki test, nested step va error turi. Taxminiy `Ta'sir`/`Yechim` qo'shilmaydi.
- `AI_ANALYSIS=1` va final natija `FAILED` bo'lsa Gemini tahlili expandable
  blokda `Kuzatilgan`, `Ehtimoliy sabab` va ishonch darajasi bilan chiqadi.
  `PASSED` xabarda AI bloki bo'lmaydi. AI xatosi deterministic final xabarni
  to'xtatmaydi.
- Final footer GitHub run URLni `Batafsil natija` yoki failed holatda
  `Xato loglari va batafsil natija` nomli bosiladigan link sifatida ko'rsatadi;
  alohida hosted Allure URL mavjud emas.

### Telegram final xabar UX talablari
Status: code-confirmed
Verified: 2026-08-18
Source: user; `tests/smoke/progress.py`; `scripts/analyze_test_result.py`;
`scripts/telegram_progress.py`
- Xato sodir bo'lgan vaqt server loglaridan tegishli yozuvni topish uchun
  Telegram xabarida va failure artifactida aniq saqlanib ko'rsatilishi kerak.
- Final xabarning status ikonkalari run natijasiga vizual zid bo'lmasin:
  `PASSED` xabarda qizil `❌` ko'rsatilmasin, `FAILED` xabarning status va xato
  indikatorlari esa qizil bo'lsin.
- User-facing duration qisqartma yoki noaniq `son` bilan emas, to'liq
  `N daqiqa M soniya` ko'rinishida chiqarilsin.

### Legacy `setup-forms` final coverage
Status: code-confirmed
Verified: 2026-08-04
Source: GitHub Actions runs `30528649258`, `30878853396`; `scripts/analyze_test_result.py`; `scripts/telegram_progress.py`
- Bu kesim eski birlashtirilgan `setup-forms` runlari va lokal compatibility
  targetiga tegishli. Joriy CI'da Smoke hamda Forms alohida final xabar oladi;
  Forms finali Setup metrikasini kutmaydi.
- Pytest summarydagi `22 passed` forma soni emas: existing-company
  `setup-forms` runida bu 20 ta Setup case va 2 ta Forms runner case'dan iborat.
- Shu run logida `Справочники` suite `89/89`, A2 Admin suite `22/22` forma
  ochgan — jami `111/111`.
- Birlashtirilgan `setup-forms` final xabari umumiy yakunlangan,
  passed/failed/skipped case hisoblaridan tashqari `Setup` qadamlar, umumiy
  Forms muvaffaqiyatli/jami va `Справочники` hamda `A2 Admin` kesimini alohida
  ko'rsatadi.
- Forms coverage uchun asosiy manba Allure'dagi versionlangan
  `form-monitor.json`; markaziy monitor attachmenti bo'lmagan eski runlarda
  `NNN | Filial: ...` va legacy `NN — ...` Allure steplari fallback bo'ladi.
- Bitta Forms wrapper ichida bir nechta forma muammosi bo'lsa Telegram faqat
  birinchi failed stepni emas, monitor payloadidagi barcha `PASSED` bo'lmagan
  formalarni raqami, holati va sababi bilan ko'rsatadi.
- Coverage parser joriy parametrized `test_form_case[...]` itemlaridagi beshta
  navbar identitysini taniydi. Eski result artifactlar uchun
  `test_forms_04_finansy` va `test_forms_05_spravochniki` wrapperlari hamda
  `test_forms_04_spravochniki`, `test_forms_01_spravochniki` va
  `test_forms_02_a2_admin` tarixiy compatibility aliaslari sifatida qoladi.

## Security

- `TELEGRAM_BOT_TOKEN`, `GITHUB_TOKEN`/`GITHUB_PAT` va
  `TELEGRAM_RUN_PASSWORD` faqat environment/secret store'dan olinadi.
- Bot chat allow-listga tayanmaydi; manual run faqat
  `hmac.compare_digest` bilan tekshirilgan run password orqali ochiladi.
- Parol xabari qabul qilingach chatdan o'chiriladi.
- `TELEGRAM_CHAT_ID` GitHub workflow progress/final xabarlari uchun destination;
  manual run authoritysi emas.
- Telegram error loglari method, kategoriya, status code, retry va redacted
  descriptionni saqlaydi; tokenli Bot API URL, payload, chat ID yoki credential
  user-facing xabar va logga chiqarilmaydi.

## Windows deploy

- CMD: `run_telegram_ci_bot.bat` yoki `scripts\run_telegram_ci_bot.cmd`.
- PowerShell: `scripts/run_telegram_ci_bot.ps1`.
- Direct: `.venv\Scripts\python.exe scripts\telegram_ci_bot.py`.
- Test/workflow kodi `main`ga push qilinsa serverdagi bot kodi o'zgarmagan
  holatda `git pull` shart emas; workflow GitHub'dagi yangi `main`ni checkout qiladi.
- Bot script, launcher, dependency yoki env/config o'zgarsa serverda pull va
  doimiy process restart kerak.
- Windows PowerShell 5.1 launcher `.ps1` fayli ASCII bo'lsin.
- Task Scheduler action Python executable, arguments bot script, working
  directory repo root bo'lsin; task bot userining User-level env'larini ko'rsin.

## Verification

- Default: workflow YAML, Python syntax, message template va command syntaxni
  read-only/statik tekshirish; unit test fayliga tegmaslik.
- Faqat user unit testni alohida so'rasa uni yozish/o'zgartirish mumkin. Faqat
  user aynan `run qil` desa
  `python -m pytest tests/unit/test_telegram_reporting.py -q`ni ishga tushirish
  mumkin; bu yerda command borligi ruxsat hisoblanmaydi.
- Real workflow dispatch yoki Telegram message faqat user explicit so'raganda.
