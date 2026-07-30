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

- Unit: `python -m pytest tests/unit/test_telegram_reporting.py -q`
- Workflow YAML va command syntaxni read-only ko'rish.
- Real workflow dispatch yoki Telegram message faqat user explicit so'raganda.
