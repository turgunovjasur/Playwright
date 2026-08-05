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
Verified: 2026-08-05
Source: `tests/smoke/test_forms/form_monitor.py`,
`tests/smoke/test_forms/flow.py`,
`tests/smoke/test_forms/form_reporting.py`,
`tests/smoke/test_forms/form_checks.py`,
`tests/smoke/test_forms/form_diagnostics.py`,
`tests/smoke/test_forms/skipped_forms.py`,
`tests/smoke/screenshot_masking.py`

- Forms-01, Forms-02 va Forms-03 bir xil `FormMonitor` orqali ishlaydi. Yangi Forms
  runner avval barcha rejalashtirilgan formalarni ro'yxatdan o'tkazadi, so'ng
  har bir navigatsiyani shu monitor orqali bajaradi.
- Har forma faqat quyidagi holatlardan birini oladi:
  `PASSED`, `OBSERVED_ONLY`, `OPENED_WITH_DEFECT`, `NOT_OPENED`,
  `TEST_BLOCKED`, `NOT_CHECKED`. `checks=[]` bilan navigatsiya bajarilib hard
  check ishlamasa `OBSERVED_ONLY`; analyzer uni failure deb hisoblamaydi.
- `OPENED_WITH_DEFECT` target forma/URL ochilgan, lekin title, blocking loader,
  JS yoki kontent tekshiruvida nuqson borligini bildiradi. `NOT_OPENED` target URL/kontentga
  yetilmaganini bildiradi. Login, filial yoki shell tayyorlovi yiqilsa joriy
  forma `TEST_BLOCKED`, boshlanmagan qolgan formalar `NOT_CHECKED` bo'ladi.
- Har xatoda monitor actual URL/title, URL mosligi, kontent tayyorligi, blocking loader,
  ko'rinadigan UI error, xato bosqichi va qisqa QA sababini yig'adi. Bundan
  tashqari `test_started`, `test_completed`, `page_reached`,
  `validation_completed`, `validation_passed` va `usable` alohida saqlanadi.
  Nuqson topilgan forma uchun validatsiya bajarilgan, ammo undan o'tmagan deb
  ko'rsatiladi; suite bloklangan sahifa esa forma ochildi deb noto'g'ri
  hisoblanmaydi.
- Case inventaridagi `allowed_warnings` faqat whitespace-normalized exact UI
  matn uchun scoped exception beradi. Mos warning `checks.allowed_warning`da
  qayd etiladi va formani yaroqsiz qilmaydi; boshqa visible errorlar
  `APPLICATION_ERROR` bo'lib qoladi.
- Xato paytidagi full-page screenshot aynan shu forma Allure stepiga
  biriktiriladi. Default mask faqat password/secret/token elementlarini
  yashiradi; oddiy search/filter inputlari ochiq qoladi.
- Kengroq forma masklari `screenshot_masking.py`dagi opt-in profillarda turadi.
  Profil case inventarida explicit ko'rsatiladi va faqat profilga mos URL
  ochilganida ishlaydi. Hozir `company-client` profili OAuth inputlari va list
  qatorlarini to'liq yopadi.
- `run_form_cases()` uchun `FormMonitor` majburiy. Eski parallel
  `finish_form_results()`/`results` hisoboti yo'q; barcha yangi forma rejalari
  yagona `build_form_case_plan()` orqali normalizatsiya qilinadi.
- `SKIPPED_FORMS` registry'sidagi canonical pathlar active `planned_cases`ga
  kirmaydi, ammo `build_form_case_inventory()` ularni reason bilan alohida
  qaytaradi. Terminal/Allure va schema v4 JSON total inventory, active count va
  intentional skip count/listni ko'rsatadi.
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
- Post-validation snapshotda `loader_visible` faqat ko'rinadigan
  `.block-ui-overlay` yoki `.smt-skeleton`ni anglatadi. `[aria-busy=true]`
  `busy_visible`/`busy_visible_count` sifatida observation-only: nested widget
  busy bo'lsa ham sahifa usable bo'lishi mumkin.
- Effective JS manbasi shellga bog'liq va human outputda bir marta chiqadi:
  legacy uchun `pageerror`, A2 uchun app `preventDefault()`idan oldin ishlaydigan
  init-script capture listeneri. Ikkalasida uncaught exception
  `OPENED_WITH_DEFECT / JS_ERROR`; resource error va unhandled promise rejection
  observation-only.
- Failed request/resource raw namunalari va haqiqiy countlar
  `form-monitor.json`da saqlanadi. Human report `/page/tour/`, optional A2 i18n
  va empty-source resource shovqinini agregatsiya qiladi; boshqa signallarni,
  jumladan `m:load_image_v2`, forma kesimida ko'rsatadi.
- `build_form_case_inventory()` active planned va registry-skipped formalarni
  alohida normalizatsiya qiladi. `form-monitor.json` schema v4 `inventory`,
  `skipped`, `config.enabled_checks` va `config.enabled_diagnostics`ni beradi;
  intentional skip `NOT_CHECKED` emas. Har resultda `identity`, auto/explicit
  `label`, schema-v4 `hard_checks` va `diagnostics` bor. Eski consumerlar uchun
  schema-v3 flat `checks` compatibility maydoni saqlanadi.
- Konfiguratsiya faqat test/FormMonitor darajasida: `None` barcha registered
  signallar, `[]` hech biri, `list[str]` faqat tanlangan nomlar. Disabled signal
  pass sifatida ko'rsatilmaydi; nested resultda `enabled: false` bo'lib qoladi.
- Terminal/Allure human report defaultda enabled/total coverage, failed
  checklar va counti bor actionable diagnostikalarni ko'rsatadi. Disabled va
  muvaffaqiyatli signallar alohida uzun qatorlarga yoyilmaydi; to'liq signal
  inventari JSONda qoladi.

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

- Default holatda reporting kodini syntax parse, linter, read-only artifact
  inspection va `git diff --check` bilan tekshir; unit test fayllarini yaratma
  yoki o'zgartirma.
- `tests/unit/test_telegram_reporting.py` faqat user aynan unit test yozish yoki
  o'zgartirishni so'rasa tahrirlanadi; `pytest` esa user aynan `run qil` deganda
  ishga tushiriladi. Bu reference'dagi command/tavsiya o'zicha authority emas.
- Report server uchun production browser/processni o'zboshimchalik bilan ochma;
  lokal generated report yoki state/health-check ham user execution so'ragan
  scope ichida bo'lsin.
