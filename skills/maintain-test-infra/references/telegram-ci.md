# Telegram CI

## Mundarija

- [Current architecture](#current-architecture)
- [Progress va final xabar](#progress-va-final-xabar)
- [Security](#security)
- [Windows deploy](#windows-deploy)
- [Verification](#verification)

## Current architecture

Status: code-confirmed
Verified: 2026-08-11
Source: `scripts/telegram_ci_bot.py`, `.github/workflows/daily-smoke.yml`

- Bir vaqtning o'zida faqat bitta active run bo'ladi; yangi `/run` oldingi run
  tugaguncha bloklanadi.
- Bot workflow'ni `main` ref va `daily-smoke.yml` bilan dispatch qiladi.
- Workflow targeti hozir `setup-forms`; setupdan keyin Forms runnerdagi beshta
  navbar suite (`Главное`, `Продажа`, `Склад`, `Финансы`, `Справочники`)
  ishlaydi. Standalone `A2Angular` bu targetga kirmaydi.
- Windowsdagi botning o'z auto-run loopi default yoqilgan: interval
  `AUTO_RUN_INTERVAL_SECONDS` orqali boshqariladi (default `3600` soniya),
  interval chegarasiga tekislanadi va default `smartup` serverida
  `setup-forms`ni dispatch qiladi. `AUTO_RUN_ENABLED=0` bilan o'chiriladi;
  bot kuzatayotgan run faol bo'lsa navbatdagi bot auto-runi skip qilinadi.
- GitHub workflow'ning o'zida ham `cron: "0 * * * *"` schedule bor. Bot
  auto-runi va workflow cron bir vaqtda yoqilgan bo'lsa bir soatda ikkita
  workflow run yaratilishi mumkin: botning in-memory active-run locki mustaqil
  GitHub schedule runini ko'rmaydi. Workflow `concurrency`si
  `cancel-in-progress: false` bo'lgani uchun ular parallel ishlash o'rniga
  navbatga tushishi mumkin; bitta scheduling authority tanlash kerak.
- Bot `smartup` va `app3` serverlarini alohida secret source bilan tanlaydi.
- GitHub status polling vaqtinchalik API/network xatosini retry qiladi; ketma-ket
  5 xatodan keyin failure sifatida chiqaradi.

## Desired Windows-local architecture

Status: user-reported
Verified: pending
Source: user

- GitHub Actions workflow test execution va schedulingdan chiqariladi;
  `telegram_ci_bot.py` Windows serverda manual hamda har soatlik runlarni lokal
  boshqaradigan yagona authority bo'ladi.
- Testlar ikki mustaqil run turiga ajratiladi: `Smoke` va `Forms`.
- `Smoke` run `setup` hamda `Group-0`ni ketma-ket bitta target sifatida
  bajaradi (`scripts/run_tests.py setup-group-0`).
- `Forms` run faqat markaziy Forms runnerni bajaradi
  (`scripts/run_tests.py forms`).
- Smoke va Forms bir-biridan mustaqil lifecycle, Telegram progress/final xabar,
  result artifactlari va Allure report yaratishi kerak.
- Soatlik tartib qat'iy: avval `Online Smoke`, keyin `Online Forms`; Smoke
  failed bo'lsa ham Forms run boshlanadi.
- Manual flow: avval suite (`Smoke` yoki `Forms`), keyin server, so'ng run
  password authorizationi tanlanadi.
- Active run bor paytda yangi manual yoki schedule trigger queue'ga qo'shilmaydi;
  aniq `busy` javobi bilan rad etiladi.
- Har suite alohida state, progress/final message, artifact va Allure lifecycle
  oladi. Telegramga ZIP yuborilmaydi; faqat qisqa matn va kerakli link beriladi.

## Progress va final xabar

- Progress bitta edit-in-place Telegram message'da yuradi; workflow final
  xabardan keyin progress message'ni yakunlaydi.
- Pytest progress eventlari `tests/smoke/smoke_reporting.py` va
  `scripts/telegram_progress.py` orqali group/runner/test/title asosida chiqadi.
- Final xabarda credential emas, faqat data-store'dagi parametrik run `code`
  ko'rsatilishi mumkin.
- Failure tafsiloti log va Allure'dagi faktlardan tuziladi: group, runner test,
  ichki test, nested step va error turi. Taxminiy `Ta'sir`/`Yechim` qo'shilmaydi.

### Setup + Forms final coverage
Status: code-confirmed
Verified: 2026-08-04
Source: GitHub Actions runs `30528649258`, `30878853396`; `scripts/analyze_test_result.py`; `scripts/telegram_progress.py`
- Pytest summarydagi `22 passed` forma soni emas: existing-company
  `setup-forms` runida bu 20 ta Setup case va 2 ta Forms runner case'dan iborat.
- Shu run logida `Справочники` suite `89/89`, A2 Admin suite `22/22` forma
  ochgan — jami `111/111`.
- Telegram final xabari `Pytest cases` deb aniq belgilangan case summarydan tashqari
  `Setup` passed/failed/skipped qadamlar, umumiy Forms muvaffaqiyatli/jami va
  `Справочники` hamda `A2 Admin` kesimini alohida ko'rsatishi shart.
- Forms coverage uchun asosiy manba Allure'dagi versionlangan
  `form-monitor.json`; markaziy monitor attachmenti bo'lmagan eski runlarda
  `NNN | Filial: ...` va legacy `NN — ...` Allure steplari fallback bo'ladi.
- Bitta Forms wrapper ichida bir nechta forma muammosi bo'lsa Telegram faqat
  birinchi failed stepni emas, monitor payloadidagi barcha `PASSED` bo'lmagan
  formalarni raqami, holati va sababi bilan ko'rsatadi.
- Coverage parser direct leaf testlar bilan birga joriy
  `test_forms_04_finansy` va `test_forms_05_spravochniki` wrapper
  identitylarini taniydi. Qayta raqamlashdan oldingi natijalar uchun
  `test_forms_04_spravochniki`, `test_forms_01_spravochniki` va
  `test_forms_02_a2_admin` tarixiy compatibility aliaslari sifatida qoladi.

## Security

- `TELEGRAM_BOT_TOKEN`, `GITHUB_TOKEN`/`GITHUB_PAT` va
  `TELEGRAM_RUN_PASSWORD` faqat environment/secret store'dan olinadi.
- Bot chat allow-listga tayanmaydi; manual run faqat
  `hmac.compare_digest` bilan tekshirilgan run password orqali ochiladi.
- Parol xabari qabul qilingach chatdan o'chiriladi.
- `TELEGRAM_CHAT_ID` ixtiyoriy auto-run destination; manual run authoritysi emas.

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
