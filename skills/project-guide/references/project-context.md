# Project Context

Bu fayl repo bo'ylab ishlatiladigan, secret bo'lmagan joriy loyiha kontekstini
saqlaydi. Batafsil test topology va runtime qoidalari tegishli owner
reference'larda qoladi.

## Framework Va Yo'llar

Status: code-confirmed
Verified: 2026-09-18
Source: repository layout

- Framework: Python, Playwright va pytest.
- Smoke testlar: `tests/smoke/`.
- Setup runner: `tests/smoke/test_setup/test_0_setup_runner.py`.
- Group runnerlar: Group-0/Report uchun `test_0_group_runner.py`, Visit uchun
  `test_0_visit_runner.py`; aniq targetlar `scripts/run_tests.py`da.
- Cross-platform runner: `python scripts/run_tests.py`; Mac/Linux wrapper:
  `run_tests.sh`.

## Flow Va Page-object Joylashuvi

Status: code-confirmed
Verified: 2026-09-18
Source: repository layout; consumer importlari

- Umumiy authorization: `tests/smoke/flows/flow_authorization.py`.
- Setup UI flowlari: `tests/smoke/test_setup/flow_setup/`.
- Order lifecycle flowlari: `tests/smoke/test_life_cycle/flow_order/`.
- Visit API, authorization va navigatsiya: `tests/smoke/test_groups/test_visit_grup/flow_visit/`.
- Report helperlari: `tests/smoke/test_groups/test_report_grup/flow_report/`.
- Action flowlari: `tests/smoke/test_action/flow_action/`.
- Page-objectlar: `utils/base_pages/`; `BasePage` legacy, `AngularBasePage` A2,
  `AutoBasePage` esa URL asosida mos implementationni tanlaydi.
- Har bir concrete faylning current importi consumer kodidan tekshiriladi;
  eski root-level page-object va global domain flow yo'llari ishlatilmaydi.

## Runtime Konteksti

Status: code-confirmed
Verified: 2026-09-18
Source: `tests/smoke/conftest.py`; `tests/smoke/smoke_config.py`; `scripts/smoke_environment.py`

- `code` session-scoped: `NEW_CODE=1` yangi olti xonali qiymat yaratadi,
  `NEW_CODE=0` esa `data_store.json.code`ni o'qiydi. Qiymat har testga alohida emas.
- Repo rootida `.env` bo'lsa direct pytest/PyCharm konfiguratsiyasi undan
  olinadi; bo'lmasa terminal yoki CI flaglari ishlaydi.
- Mavjud company parametrlari: `--url <server_url> --company-code
  <company_code> --company-password <company_password>`.
- Yangi company parametrlari: `--url <server_url> --company-code 1
  --head-email <head_email> --head-password <head_password>`.
- `COMPANY_CODE=0` yaroqsiz. Mavjud companyni qayta ishlatish uchun uning
  haqiqiy kodi beriladi. `USER_PASSWORD` har ikki rejimda environmentdan talab qilinadi.
- Admin default paroli kodda bo'lishi mumkin, ammo uning literal qiymati va
  user passwordlari knowledge-base'ga yozilmaydi.
