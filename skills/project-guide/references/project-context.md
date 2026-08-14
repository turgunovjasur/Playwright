# Project Context

Bu fayl repo bo'ylab ishlatiladigan, secret bo'lmagan joriy loyiha kontekstini
saqlaydi. Batafsil test topology va runtime qoidalari tegishli owner
reference'larda qoladi.

## Framework Va Yo'llar

Status: code-confirmed
Verified: 2026-08-14
Source: repository layout

- Framework: Python, Playwright va pytest.
- Smoke testlar: `tests/smoke/`.
- Setup runner: `tests/smoke/test_setup/test_0_setup_runner.py`.
- Group runnerlar: `tests/smoke/test_groups/**/test_*_group_runner.py`.
- Cross-platform runner: `python scripts/run_tests.py`; Mac/Linux wrapper:
  `run_tests.sh`.

## Runtime Konteksti

Status: user-reported
Verified: pending
Source: user

- `code` fixture session uchun unikal olti xonali qiymat yaratadi; runner yangi
  qiymat ishlatadi, yakka test esa `data_store.json`dan o'qishi mumkin.
- Repo rootida `.env` bo'lsa direct pytest/PyCharm konfiguratsiyasi undan
  olinadi; bo'lmasa terminal yoki CI flaglari ishlaydi.
- Mavjud company parametrlari: `--url <server_url> --company-code
  <company_code> --company-password <company_password>`.
- Yangi company parametrlari: `--url <server_url> --create-company
  --head-email <head_email> --head-password <head_password>`.
- Admin default paroli kodda bo'lishi mumkin, ammo uning literal qiymati va
  user passwordlari knowledge-base'ga yozilmaydi.
