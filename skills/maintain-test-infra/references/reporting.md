# Smoke Reporting va Allure

## Mundarija

- [Current architecture](#current-architecture)
- [Forms central monitoring](#forms-central-monitoring)
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

## Forms central monitoring

Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_forms/form_monitor.py`,
`tests/smoke/test_forms/flow.py`

- Forms-01 va Forms-02 bir xil `FormMonitor` orqali ishlaydi. Yangi Forms
  runner avval barcha rejalashtirilgan formalarni ro'yxatdan o'tkazadi, so'ng
  har bir navigatsiyani shu monitor orqali bajaradi.
- Har forma faqat quyidagi holatlardan birini oladi:
  `PASSED`, `OPENED_WITH_DEFECT`, `NOT_OPENED`, `TEST_BLOCKED`,
  `NOT_CHECKED`.
- `OPENED_WITH_DEFECT` forma va URL ochilgan, lekin title yoki kontent
  tekshiruvida nuqson borligini bildiradi. `NOT_OPENED` target URL/kontentga
  yetilmaganini bildiradi. Login, filial yoki shell tayyorlovi yiqilsa joriy
  forma `TEST_BLOCKED`, boshlanmagan qolgan formalar `NOT_CHECKED` bo'ladi.
- Har xatoda monitor actual URL/title, URL mosligi, kontent tayyorligi, loader,
  ko'rinadigan UI error, xato bosqichi va qisqa QA sababini yig'adi. Bundan
  tashqari `test_started`, `test_completed`, `page_reached`,
  `validation_completed`, `validation_passed` va `usable` alohida saqlanadi.
  Nuqson topilgan forma uchun validatsiya bajarilgan, ammo undan o'tmagan deb
  ko'rsatiladi; suite bloklangan sahifa esa forma ochildi deb noto'g'ri
  hisoblanmaydi.
- Xato paytidagi full-page screenshot aynan shu forma Allure stepiga
  biriktiriladi. Barcha inputlar va secret/password/token ustunlari masklanadi;
  OAuth client listda data qatorlari to'liq yopiladi.
- `run_form_cases()` uchun `FormMonitor` majburiy. Eski parallel
  `finish_form_results()`/`results` hisoboti yo'q; barcha yangi forma rejalari
  yagona `build_form_case_plan()` orqali normalizatsiya qilinadi.
- Har forma tugashi bilan terminal reporter orqali bitta ixcham
  `[FORM MONITOR]` qatori
  chiqariladi; uzoq Forms run vaqtida joriy progress va oxirgi forma holati
  ko'rinib turadi. Shu natija `SMARTUP_PROGRESS form_result` eventiga ham
  aylanadi va Telegram progress consumeri uni joriy forma sifatida o'qiydi.
  Ko'p qatorli tafsilot faqat yakuniy summaryda beriladi.
- Yakuniy terminal text, Allure text va `form-monitor.json` bir xil natijalar
  ro'yxatidan quriladi; shu sabab hisoblar va forma tafsilotlari bir-biridan
  farq qilmasligi kerak.
- A2 uchun forma nomi manbasi browser `document.title`; legacy uchun visible
  page heading. JSONdagi `checks.title_source` qaysi signal ishlatilganini,
  `checks.document_title` esa diagnostika uchun asl browser title'ini saqlaydi.

## Failure artifacts

- Failed test uchun current URL, page title, redacted full-page screenshot va mavjud
  data-store Allure'ga attach qilinadi.
- Forms runnerda umumiy pytest failure screenshoti bilan birga har bir muammo
  aniqlangan paytdagi forma screenshoti ham alohida attach qilinadi. Yakuniy
  sahifa screenshoti `pytest-final-page-context — failed-form dalili emas` deb
  nomlanadi va oldingi forma xatosining dalili sifatida ishlatilmaydi.
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
