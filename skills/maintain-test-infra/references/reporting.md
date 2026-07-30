# Smoke Reporting va Allure

## Mundarija

- [Current architecture](#current-architecture)
- [Failure artifacts](#failure-artifacts)
- [Local Allure lifecycle](#local-allure-lifecycle)
- [Verification](#verification)

## Current architecture

Status: code-confirmed
Verified: 2026-07-30
Source: `tests/smoke/smoke_reporting.py`, `scripts/open_allure_report.py`

- Progress metadata marker, runner path, pytest item va Allure title'dan yig'iladi.
- `started` va final event har test uchun faqat bir marta chiqariladi.
- Allure results run boshida history, environment, categories va executor bilan
  tayyorlanadi.

## Failure artifacts

- Failed test uchun current URL, page title, full-page screenshot va mavjud
  data-store Allure'ga attach qilinadi.
- Pytest longrepr `test-results/logs/` ichiga yoziladi.
- Failure diagnostikasi add/edit formdagi asl save/error transitionini
  keyingi list/view timeoutidan oldin ko'rsatishi kerak.

## Local Allure lifecycle

- Direct pytest run `OPEN_REPORT=1` bo'lsa report generate/open qiladi;
  `SMARTUP_RUNNER=1` bo'lsa runner o'zi lifecycle'ni boshqaradi.
- `scripts/open_allure_report.py` state + lock + health-check bilan mavjud
  healthy serverni qayta ishlatadi.
- Stale state yangi server bilan almashtiriladi.
- Report tab heartbeat yuboradi; tab yopilgach lokal server grace perioddan
  keyin to'xtaydi.
- Helper process parent stdout/stderr va session lifecycle'iga bog'lanib
  qolmasligi kerak.

## Verification

- Eng tor reporting unit testlarini ishga tushir.
- Report server uchun state/health-check unit yoki lokal generated report bilan
  tekshir; production browser/processni o'zboshimchalik bilan ochma.
