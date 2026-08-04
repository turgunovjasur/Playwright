# Telegram CI

## Mundarija

- [Current architecture](#current-architecture)
- [Progress va final xabar](#progress-va-final-xabar)
- [Security](#security)
- [Windows deploy](#windows-deploy)
- [Verification](#verification)

## Current architecture

Status: code-confirmed
Verified: 2026-07-30
Source: `scripts/telegram_ci_bot.py`, `.github/workflows/daily-smoke.yml`

- Bir vaqtning o'zida faqat bitta active run bo'ladi; yangi `/run` oldingi run
  tugaguncha bloklanadi.
- Bot workflow'ni `main` ref va `daily-smoke.yml` bilan dispatch qiladi.
- Workflow targeti hozir `setup-forms`; setupdan keyin `Справочники` va A2
  admin formalarini qamrab oluvchi Forms runner ishlaydi. Schedule har soat
  `00` daqiqada.
- Bot `smartup` va `app3` serverlarini alohida secret source bilan tanlaydi.
- GitHub status polling vaqtinchalik API/network xatosini retry qiladi; ketma-ket
  5 xatodan keyin failure sifatida chiqaradi.

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
- Coverage parser direct leaf testlar bilan birga
  `test_forms_01_spravochniki` va `test_forms_02_a2_admin` wrapper
  identitylarini ham tanishi kerak.

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
