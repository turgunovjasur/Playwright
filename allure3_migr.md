# Allure Report 3 To'liq Migratsiya Plani

> **For agentic workers:** implementatsiya faqat foydalanuvchi ushbu plan'ni
> tasdiqlagandan keyin boshlanadi. Har faza yakunida shu fayldagi status va
> checkboxlar yangilanadi; keyingi fazaga acceptance mezonlari bajarilgach
> o'tiladi.

**Maqsad:** Smartup Playwright/pytest loyihasining Allure 2 report generatori,
konfiguratsiyasi, history lifecycle'i, lokal report ochish jarayoni va GitHub
Actions integratsiyasini Allure Report 3'ga to'liq o'tkazish; mavjud test
natijalari, steplar, attachmentlar va diagnostika consumerlarini saqlash.

**Arxitektura:** `allure-pytest` test execution vaqtida Allure-compatible raw
result JSONlarini yaratishda davom etadi. Versiyasi pin qilingan project-local
Allure 3 CLI shu raw resultlardan Awesome HTML report yaratadi. Allure 3'ga xos
`allurerc.mjs` categories, history, environment va test hierarchy uchun yagona
konfiguratsiya authoritysi bo'ladi.

**Texnologiyalar:** Python 3.11/3.13, pytest, `allure-pytest`, Node.js, npm,
`allure@3.14.3`, Allure Awesome report, GitHub Actions.

**Rasmiy asoslar:**

- [Allure 2'dan Allure 3'ga migration](https://allurereport.org/docs/v3/migrate/)
- [Allure 3 konfiguratsiyasi](https://allurereport.org/docs/v3/configure/)
- [Allure 3 report navigatsiyasi](https://allurereport.org/docs/v3/navigation/)
- [Allure history va retries](https://allurereport.org/docs/history-and-retries/)
- [Allure 3 categories](https://allurereport.org/docs/categories/)
- [Allure 3 GitHub Action integratsiyasi](https://allurereport.org/docs/integrations-github-action/)

## Status Lug'ati

- `TODO` — hali boshlanmagan.
- `PROGRESS` — hozir bajarilayotgan yoki user review kutayotgan faza.
- `DONE` — acceptance mezonlari bajarilgan va dalil yozilgan.
- Har vaqtda faqat bitta faza `PROGRESS` bo'ladi.
- Checkboxlar: `[ ]` bajarilmagan, `[x]` bajarilgan.

## Joriy Holat

| Faza | Status | Natija |
|---|---|---|
| 0. Repo va Allure 3 audit | `DONE` | Joriy adapter, CLI, history, categories, runner va CI consumerlari xaritalandi |
| 1. Plan review va scope freeze | `PROGRESS` | Ushbu fayl user review'ida |
| 2. Project-local Allure 3 runtime | `TODO` | Pin qilingan npm dependency va yagona CLI entrypoint |
| 3. Allure 3 konfiguratsiya va ko'rinish | `TODO` | Awesome report, canonical hierarchy, categories va metadata |
| 4. History lifecycle migratsiyasi | `TODO` | Allure 2 history papkasisiz JSONL history |
| 5. Lokal runner va report server integratsiyasi | `TODO` | Direct pytest va `scripts/run_tests.py` bir xil generator ishlatadi |
| 6. GitHub Actions migratsiyasi | `TODO` | Java/Allure 2 olib tashlangan, reproducible Allure 3 report artifact |
| 7. Test presentation parity auditi | `TODO` | Barcha test oilalari canonical Allure 3 ko'rinishida |
| 8. Verification va rollback gate | `TODO` | Static va user ruxsat bergan runtime tekshiruvlar o'tgan |
| 9. Knowledge write-back va cleanup | `TODO` | Canonical skill yangilangan, Allure 2 qoldiqlari yo'q |

## Global Cheklovlar

- Migratsiya `dev1` branchida amalga oshiriladi.
- Userning mavjud dirty-worktree o'zgarishlari saqlanadi va ustidan yozilmaydi.
- `allure-pytest==2.15.3` va `allure-python-commons==2.15.3` Allure 3 CLI bilan
  rasmiy result-format compatibility sabab boshlang'ich migratsiyada
  o'zgartirilmaydi; Python paketidagi `2.x` raqami report generator versiyasi
  emas.
- Allure 3 CLI global o'rnatilmaydi. `package.json` va `package-lock.json` orqali
  aynan `allure@3.14.3` ishlatiladi.
- `@allure.title`, `allure.dynamic.title`, `allure.step`, parameter va
  attachmentlar faqat report parity buzilgan testlarda o'zgartiriladi.
- Secret, company password, token va PII Allure config/history/reportga
  kiritilmaydi. Joriy `environment.properties` ham credential yozmaydi.
- Existing deterministic analyzer raw `*-result.json` va attachmentlarni
  o'qishda davom etadi; HTML report strukturasi analyzer inputiga aylanmaydi.
- Allure 3'ning `allure run --rerun` wrapperi bu migratsiyada yoqilmaydi:
  retry runner, Telegram progress va fail-closed smoke semantikasini
  o'zgartiradi. Bu full migration uchun shart emas.
- Known Issues va Quality Gate config boundarysi tayyorlanadi, ammo real known
  issue ro'yxati yoki yangi CI failure policy user alohida tasdiqlamaguncha
  yoqilmaydi.
- `pytest`, smoke target yoki collection faqat user aynan `run qil` deb ruxsat
  bergandan keyin bajariladi. Bunday ruxsat bo'lmasa verification mavjud raw
  results, CLI generation, config parse va static inspection bilan cheklanadi.

## Allure 3'da Tasdiqlangan Canonical Test Ko'rinishi

Allure 3 Awesome report uchun primary hierarchy rasmiy behavior-based shaklda
bo'ladi:

```text
Epic
└── Feature
    └── Story
        └── @allure.title yoki allure.dynamic.title
            ├── Parameters
            ├── Steps
            │   └── Nested steps
            └── Attachments
```

`allurerc.mjs` ichida bu ko'rinish explicit yoziladi:

```js
plugins: {
  awesome: {
    options: {
      reportName: "Smartup Smoke Tests",
      reportLanguage: "en",
      groupBy: ["epic", "feature", "story"],
      singleFile: false,
    },
  },
}
```

### Test oilalari bo'yicha acceptance matrix

| Test oilasi | Epic | Feature | Story | Leaf/test title | Detail ichida |
|---|---|---|---|---|---|
| Setup | `Smoke` | `Setup` | biznes obyekt, masalan `Price Type` | professional `@allure.title` | raqamlangan business steplar va failure attachmentlar |
| Group A/B/C/Report | `Smoke` | tegishli group nomi | testcase domeni | runner wrapper title'i leaf title bilan bir xil | leaf `run_*` steplari, trace/screenshot/log |
| Forms navbar | `Forms — navbar` uchun amaldagi canonical epic/feature/story label mapping | navbar kesimi | menu column yoki forma grouping | `NNN | <forma label>` | forma parametrlari, hard checks, diagnostics va `form-monitor.json` |
| A2Angular | amaldagi cross-navbar label mapping | navbar tab | menu column | forma title | nested navigation track va attachmentlar |
| System summary | `System` | `Test Summary` | `Deterministic` | `System Test Summary` | Markdown va JSON attachment |
| AI summary | `AI` | `Xatolik tahlili` | `Gemini` | `AI xatolik tahlili` | Markdown va JSON attachment |

Har bir rendered test uchun quyidagilar tasdiqlanadi:

- leaf nomida Python function/nodeid emas, inson o'qiydigan Allure title chiqadi;
- `epic → feature → story` yo'li bo'sh emas va noto'g'ri fallback guruhga
  tushmaydi;
- passed, failed, broken, skipped statuslari Allure 3 semanticsida to'g'ri;
- nested step tartibi raw resultdagi tartib bilan bir xil;
- PNG, JSON, Markdown, text va Playwright trace attachmentlari ochiladi;
- failed step, status details va custom defect category bir testda mos keladi;
- parametrized Forms testlari alohida test item bo'lib qoladi;
- System/AI summary biznes testlar bilan aralashmaydi;
- `environment.properties` Metadata sifatida ko'rinadi, yangi environment
  assignment bilan conflict qilmaydi.

---

## Faza 0 — Repo va Allure 3 Audit

**Status:** `DONE`

**Tekshirilgan fayllar:**

- `requirements.txt`
- `pytest.ini`
- `allure/categories.json`
- `tests/smoke/conftest.py`
- `tests/smoke/smoke_reporting.py`
- `scripts/run_tests.py`
- `scripts/open_allure_report.py`
- `scripts/analyze_test_result.py`
- `.github/workflows/run-smartup-suite.yml`
- `skills/maintain-test-infra/references/reporting.md`

**Dalil:** lokal CLI `2.36.0`; CI `allure-commandline` o'rnatadi; Allure 2
history `allure-report/history → allure-results/history` orqali ko'chiriladi;
custom categories Allure 2 `categories.json` formatida; test metadata raw
resultlar orqali analyzerga uzatiladi.

- [x] Joriy generator va adapter versiyalarini aniqlash.
- [x] Lokal runner/direct pytest/CI generation entrypointlarini aniqlash.
- [x] History, categories, metadata va analyzer consumerlarini aniqlash.
- [x] Canonical Allure 3 hierarchy uchun rasmiy formatni tekshirish.

## Faza 1 — Plan Review va Scope Freeze

**Status:** `PROGRESS`

**Fayl:** `allure3_migr.md`

- [x] Fazalar va status tracking kontraktini yozish.
- [x] Allure 3 canonical test ko'rinishini belgilash.
- [x] Migratsiya, verification va rollback mezonlarini yozish.
- [ ] User plan scope'ini tasdiqlaydi yoki tuzatish beradi.
- [ ] Tasdiqdan keyin Faza 1 `DONE`, Faza 2 `PROGRESS` qilinadi.

**Acceptance:** user ushbu plan bo'yicha implementatsiyani boshlashga aniq
rozilik beradi.

## Faza 2 — Project-local Allure 3 Runtime

**Status:** `TODO`

**Fayllar:**

- Create: `package.json`
- Create: `package-lock.json`
- Modify: `.gitignore`
- Create: `scripts/allure_report_cli.py`
- Modify: `README.md`

**Natija:** barcha platforma va entrypointlar aynan bitta project-local Allure
3 executable va versiyadan foydalanadi.

- [ ] `package.json`da private tooling package yaratish va
  `devDependencies.allure`ni `3.14.3`ga exact pin qilish.
- [ ] `npm install --package-lock-only`/`npm install` orqali lockfile yaratish;
  lockfile'da Allure 2 `allure-commandline` yo'qligini tekshirish.
- [ ] `.gitignore`ga `node_modules/` va Allure 3 local runtime/history outputini
  aniq ignore qilish.
- [ ] `scripts/allure_report_cli.py`da Windows/macOS/Linux uchun
  `node_modules/.bin/allure[.cmd]` resolver yozish.
- [ ] Resolver global `allure`ga silent fallback qilmasin; dependency yo'q bo'lsa
  `npm ci` ko'rsatmasi bilan aniq non-zero xato qaytarsin.
- [ ] `generate` helper input results dir, output dir va config pathni explicit
  qabul qilsin; exit code va commandni callerga qaytarsin.
- [ ] README install/report commandlarini `npm ci` va project-local CLI bilan
  yangilash.

**Static verification:** `node --version`, `npm --version`, `npm ls allure`,
`npx --no-install allure --version`, Python syntax parse va `git diff --check`.

**Acceptance:** local va CI bir xil lockfile'dan `allure 3.14.3`ni resolve
qiladi; Java yoki global Allure 2 kerak emas.

## Faza 3 — Allure 3 Konfiguratsiya va Ko'rinish

**Status:** `TODO`

**Fayllar:**

- Create: `allurerc.mjs`
- Modify: `allure/categories.json` yoki migratsiya tasdiqlangach remove
- Modify: `tests/smoke/smoke_reporting.py`

**Natija:** Allure 3 Awesome report yagona config orqali canonical behavior
hierarchy, custom categories, history va xavfsiz metadata bilan generatsiya
qilinadi.

- [ ] `allurerc.mjs`da `defineConfig` va explicit output/history/plugin
  konfiguratsiyasini yozish.
- [ ] Primary `groupBy`ni `epic`, `feature`, `story` tartibida pin qilish.
- [ ] `reportName="Smartup Smoke Tests"`, `singleFile=false` va supported UI
  tilini explicit belgilash.
- [ ] Sakkizta custom defect kategoriyasini Allure 3
  `categories.rules[].matchers` formatiga ko'chirish.
- [ ] Java/Python inline `(?s)` regexlarini JavaScript-compatible `/.../s`
  RegExpga aylantirish; har category IDni kebab-case va stable qilish.
- [ ] `environment.properties`ni legacy Metadata sifatida saqlash; secret
  yozilmasligini qayta tekshirish.
- [ ] `categories.json`ni results dirga copy qilishni to'xtatish; parity
  tasdiqlangach eski source faylni olib tashlash.
- [ ] Default Product errors/Test errors kategoriyalari custom kategoriyalarni
  yutib yubormasligi uchun rule orderni rendered reportda tekshirish.

**Render verification:** mavjud `test-results/allure-results`dan Awesome report
yaratish va primary tree, title, steps, parameters, statuses va attachmentsni
ochib tekshirish.

**Acceptance:** acceptance matrixdagi kamida bittadan Setup, Group, Forms,
failed test, skipped test va System Summary item canonical tree'da ko'rinadi;
custom markerlar tegishli categoryga tushadi.

## Faza 4 — History Lifecycle Migratsiyasi

**Status:** `TODO`

**Fayllar:**

- Modify: `allurerc.mjs`
- Modify: `tests/smoke/smoke_reporting.py`
- Modify: `scripts/run_tests.py`
- Modify: `.github/workflows/run-smartup-suite.yml`

**Natija:** Allure 2 `history/` directory copy lifecycle'i butunlay yo'qoladi;
Allure 3 bitta JSONL fayl orqali trend va status transitionlarni yuritadi.

- [ ] `historyPath`ni default
  `test-results/allure-history/history.jsonl`ga bog'lash.
- [ ] `appendHistory=true` va bounded `historyLimit=50` belgilash.
- [ ] `_clean_current_allure_results()` faqat joriy raw resultlarni tozalasin;
  Allure 3 history fayliga tegmasin.
- [ ] `allure-report/history`ni `allure-results/history`ga ko'chiradigan Allure 2
  kodini olib tashlash.
- [ ] Eski Allure 2 history avtomatik format-convert qilinmasligini hujjatlash;
  Allure 3 history migratsiyadan keyingi birinchi run bilan boshlanadi.
- [ ] CI history cache'ini `server_key + target` bo'yicha izolyatsiya qilish;
  parallel server/target runlari bitta JSONLga yozmasin.
- [ ] History JSONL report artifact tarkibiga kirishini, lekin gitga
  kirmasligini tekshirish.

**Acceptance:** ketma-ket ikki generationdan keyin JSONLda ikki valid line bor;
ikkinchi report history/status-transition chartlarini ko'rsatadi va raw results
cleanup historyni o'chirmaydi.

## Faza 5 — Lokal Runner va Report Server Integratsiyasi

**Status:** `TODO`

**Fayllar:**

- Modify: `scripts/run_tests.py`
- Modify: `tests/smoke/smoke_reporting.py`
- Modify: `scripts/open_allure_report.py`
- Reuse: `scripts/allure_report_cli.py`

**Natija:** runner va direct pytest bir xil generator kontraktidan foydalanadi;
Allure 3 report generate bo'lmasa eski/stale report ochilmaydi.

- [ ] `scripts/run_tests.py::generate_report()`ni shared Allure 3 helperga
  o'tkazish.
- [ ] `tests/smoke/smoke_reporting.py::_generate_and_open_allure_report()`ni
  shu helperga o'tkazish.
- [ ] Generation failure'ni explicit log va non-success result bilan callerga
  uzatish; pytestning original exit code semantikasini o'zgartirmaslik.
- [ ] `scripts/open_allure_report.py`ning `index.html` heartbeat injectioni
  Allure 3 multi-file Awesome outputida ishlashini tekshirish.
- [ ] Allure 3 `index.html`da `</body>` bo'lmasa fail-safe heartbeat injection
  strategiyasini implement qilish.
- [ ] Stale server state, reuse, tab-close shutdown va OS path handlingni
  saqlash.

**Acceptance:** runner va `OPEN_REPORT=1` direct pytest bir xil report output
yaratadi; browser ochilganda assetlar/attachmentlar 404 bermaydi; tab yopilgach
server to'xtaydi.

## Faza 6 — GitHub Actions Migratsiyasi

**Status:** `TODO`

**Fayllar:**

- Modify: `.github/workflows/run-smartup-suite.yml`
- Reuse: `package.json`
- Reuse: `package-lock.json`
- Reuse: `scripts/allure_report_cli.py`

**Natija:** CI Allure 2 yoki global mutable dependency ishlatmaydi; Allure 3
report va history har run artifactida saqlanadi.

- [ ] Java setup stepini olib tashlash.
- [ ] `npm install --global allure-commandline`ni olib tashlash.
- [ ] Python dependency install yonida `npm ci` ishlatish.
- [ ] Report generationni shared project-local helper orqali `if: always()`da
  bajarish.
- [ ] Allure 3 history cache restore/save qadamlarini target/server kesimida
  qo'shish.
- [ ] Report directory, raw results, JSONL history, log, trace va screenshotlar
  joriy `test-results/` artifactida qolishini tekshirish.
- [ ] Generation xatosi artifact upload va Telegram finalize qadamlarini
  to'smasligi, lekin job logda aniq failure sifatida ko'rinishini ta'minlash.
- [ ] Official Allure GitHub Action PR comment/quality-gate integratsiyasini
  default yoqmaslik; repo workflowlari PR eventga o'tkazilsa alohida change
  sifatida qo'shish.

**Acceptance:** workflowda `allure-commandline`, Allure 2 va Java setup qoldig'i
yo'q; lockfile bilan Allure 3 report generatsiya qilinadi va upload qilinadi.

## Faza 7 — Test Presentation Parity Auditi

**Status:** `TODO`

**Fayllar:**

- Audit/conditional modify: `tests/smoke/test_setup/test_*.py`
- Audit/conditional modify: `tests/smoke/test_groups/**/*.py`
- Audit/conditional modify: `tests/smoke/test_forms/**/*.py`
- Audit/conditional modify: `scripts/analyze_test_result.py`

**Natija:** barcha test oilalari Allure 3 canonical tree'da professional title,
step va attachment bilan ko'rinadi; faqat real parity nuqsonlari tahrirlanadi.

- [ ] Static audit bilan har executable testda title source va
  `epic/feature/story` label mapping mavjudligini tekshirish.
- [ ] Runner wrapper title va leaf title bir-birini takrorlamasligini
  tekshirish.
- [ ] Forms parameterized itemlarda dynamic title va hierarchy marklari test
  body boshlanmasa ham raw resultga tushishini tekshirish.
- [ ] `System Test Summary` va `AI xatolik tahlili` qo'lda yaratilgan result
  JSONlari Allure 3 schema readerda warning bermasligini tekshirish.
- [ ] Missing label/title faqat aniqlangan faylda minimal patch bilan tuzatish;
  barcha testlarni ommaviy qayta yozmaslik.
- [ ] Failure attachment nomlari va MIME typelarini Allure 3 preview bilan
  tekshirish.
- [ ] `titlePath` compatibility maydoniga suyanmaslik; hierarchy authoritysi
  labels ekanini tasdiqlash.

**Acceptance:** yuqoridagi test-family matrixning har qatori rendered reportda
tekshirilgan va mismatchlar ro'yxati nolga tushgan.

## Faza 8 — Verification va Rollback Gate

**Status:** `TODO`

**Static verification — test run ruxsatisiz:**

- [ ] `allurerc.mjs` import/config parse.
- [ ] `npx --no-install allure --version` aynan `3.14.3`.
- [ ] Python o'zgargan fayllar syntax parse.
- [ ] YAML parse va workflow static inspection.
- [ ] Mavjud raw resultsdan Allure 3 report generation.
- [ ] Generated `index.html`, `summary.json`, attachment assetlari va history
  JSONL mavjudligi.
- [ ] Repo bo'ylab `allure-commandline`, Allure 2 history-copy va global CLI
  fallback qoldiqlarini `rg` bilan tekshirish.
- [ ] `git diff --check`.

**User `run qil` deb ruxsat bergandagi runtime verification:**

- [ ] Eng kichik representative direct pytest target.
- [ ] Bitta runner target.
- [ ] Forms parametrized itemdan representative kesim.
- [ ] Failed/skipped/passed statuslarni o'z ichiga oladigan artifact audit.
- [ ] `OPEN_REPORT=1` lokal browser lifecycle.
- [ ] User CI run so'rasa GitHub Actions artifact va history audit.

**Rollback mezoni:** attachment ochilmasa, canonical hierarchy buzilsa,
categories noto'g'ri match qilsa, analyzer raw resultsni o'qimasa yoki CI report
yaratmasa migratsiya `DONE` qilinmaydi. Allure 2 fayllari faqat Allure 3 parity
tasdiqlangandan keyin yakuniy patchdan olib tashlanadi; git tarixidan recovery
mavjud.

**Acceptance:** barcha ruxsat etilgan verificationlar o'tgan, topilgan regression
qolmagan va migration diffida Allure 2 runtime dependency yo'q.

## Faza 9 — Knowledge Write-back va Cleanup

**Status:** `TODO`

**Fayllar:**

- Modify: `skills/maintain-test-infra/references/reporting.md`
- Conditional modify: `skills/run-smoke/SKILL.md`
- Conditional modify: `README.md`
- Remove after parity: `allure/categories.json`
- Update throughout: `allure3_migr.md`

- [ ] Reporting reference'da Allure 3 runtime, config, JSONL history, hierarchy
  va local/CI lifecycle'ni current truth sifatida yozish.
- [ ] Eski Allure 2 current-truth matnlarini yangilash; kerakli historical
  evidence'ni history ownerga ko'chirish.
- [ ] `./.venv/bin/python skills/scripts/validate_skills.py`ni ishlatish.
- [ ] Workspace'da migration vaqtida yaratilgan vaqtinchalik output/cachelarni
  tozalash; userning avvalgi artifactlariga tegmaslik.
- [ ] `allure3_migr.md`dagi barcha fazalarni `DONE` qilish va har fazaga qisqa
  dalil/command natijasini yozish.
- [ ] Final handoffda o'zgargan fayllar, verification, run qilinmagan testlar va
  qolgan cheklovlarni aniq aytish.

**Acceptance:** skill validator o'tgan, canonical knowledge kodga mos, Allure 2
runtime/config/history qoldig'i yo'q va ushbu tracker to'liq `DONE`.

## Implementatsiya Commit Chegaralari

Implementatsiya tasdiqlansa, reviewni yengillashtirish uchun quyidagi kichik
commitlar tavsiya etiladi:

1. `build: pin project-local Allure 3 runtime`
2. `feat: configure Allure 3 report hierarchy and categories`
3. `refactor: migrate Allure history to JSONL`
4. `refactor: unify local Allure 3 report generation`
5. `ci: generate Allure 3 reports from locked dependencies`
6. `test-report: align Smartup test presentation with Allure 3`
7. `docs: document Allure 3 reporting lifecycle`

Commit faqat user so'rasa yaratiladi; bu ro'yxat implementatsiya task
chegaralarini bildiradi.

## Review Uchun Qarorlar

Plan quyidagi qarorlarni taklif qiladi:

1. CLI versiyasi exact `allure@3.14.3` bo'ladi.
2. Primary ko'rinish `epic → feature → story → test title` bo'ladi.
3. History limiti 50 run va target/server kesimida izolyatsiyalangan bo'ladi.
4. UI tili hozircha `en`; test title va step matnlari amaldagi tilda qoladi.
5. Quality Gate, Known Issues va automatic retry alohida policy tasdig'isiz
   yoqilmaydi.
6. Allure 2 history Allure 3 formatiga sun'iy convert qilinmaydi; yangi history
   migratsiyadan boshlab yuritiladi.

