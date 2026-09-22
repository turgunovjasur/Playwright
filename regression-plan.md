# Smartup Regression — amalga oshirish rejasi va holat jurnali

> Ijro: ushbu sessiyada bosqichma-bosqich, `superpowers:executing-plans` va repo
> `skills/project-guide/SKILL.md` qoidalari asosida. Bu foydalanuvchi so'ragan
> ishchi reja; loyiha bilimlarining canonical manbasi `skills/` bo'lib qoladi.

**Maqsad:** mavjud smoke ssenariylarini saqlab, `tests/regression/` ichida
formalarning imkoniyatlari, validatsiyalari va biznes natijalarini tekshiradigan
takror ishlatiladigan Playwright/pytest testlarini yaratish.

**Arxitektura:** umumiy fixture, browser, konfiguratsiya va diagnostika smoke'dan
yuqoriga chiqariladi. Regression setup hozircha mavjud smoke `run_*`
funksiyalarini import qiladi. Bitta umumiy data store va umumiy natija mexanizmi
saqlanadi; smoke va regression runlari ketma-ket bajariladi.

**Texnologiya:** Python, pytest, Playwright Chromium, Allure, mavjud
`AutoBasePage` va repo helperlari; importlar uchun haqiqiy XLSX fayllar.

**Talab manbasi:** foydalanuvchining 2026-09-21 kuni tasdiqlagan suhbatdagi
talablari, quyidagi “Kelishilgan chegaralar” bo'limi va tarixiy caselar uchun
[reliz.md](reliz.md). Oldingi qo'lda run natijalari yangi autotestning PASS
natijasi hisoblanmaydi.

## Hozir qayerdamiz?

Oxirgi yangilanish: **2026-09-22 (Asia/Tashkent)**.

- **Branch:** `dev1`.
- **Main bilan birlashtirish:** `origin/main` (`d9aa9e0`) `dev1`ga
  (`ca48278`) `--no-commit --no-ff` bilan konfliktsiz birlashtirildi.
  Foydalanuvchining 2026-09-22 kungi aniq ruxsati bilan merge va reja
  yangilanishi dev1da commit orqali yakunlanadi. `main`, `debug` va remote
  branchlarga yozilmaydi; `outputs/` commitga kiritilmaydi.
- **Bajarildi:** P02 umumiy infra va P03 bazaviy setup runneri yozildi; statik tekshiruvlar o'tdi.
- **Joriy ish:** P04 inventari davomida P05 qo'lda ТМЦ yaratish caselari implementatsiyasi boshlandi.
- **Muhit:** mavjud test useriga admin orqali ERP users litsenziyasi biriktirildi;
  o'z filialidagi dashboardga kirishi tekshirildi. Oldingi biriktirilgan user saqlandi.
- **Regression kodi:** 21 ta setup wrapperi; ТМЦ uchun 12 ta item yozildi:
  6 create, ikki mahsulotli import, create-cancel, edit-save/cancel,
  2 required validation va import-cancel. Qo'shimcha ТМЦ imkoniyatlari,
  narx/kirim kodi hali tugamagan. Runtime PASS deb belgilanmaydi.
- **Test run:** bajarilmadi; collection ham bajarilmadi. Runtime mosligi hali tasdiqlanmagan.
- **Commit:** joriy merge va reja yangilanishini commit qilishga 2026-09-22 kuni
  ruxsat berildi. Bu keyingi ishlarga avtomatik commit/push ruxsati emas.

| ID | Bosqich | Ish holati | Run/tekshiruv holati | Dalil yoki yakun mezoni |
|---|---|---|---|---|
| P00 | Branchlarni tenglashtirish | DONE (boshlang'ich) | Git bilan tekshirildi | 2026-09-21: faol branchlar `d4f97f2`; 2026-09-22: main tuzatishlari dev1ga commitsiz merge qilindi, tafsilotlar jurnalda |
| P01 | Tasdiqlangan rejani saqlash | DONE | Hujjat tekshiruvi o'tdi | Majburiy mavzular, reliz havolasi va format tekshirildi |
| P02 | Umumiy infra: fixture, config, browser, reporting | IMPLEMENTED | Static PASS / NOT RUN | 15 Python fayl sintaksisi, pyflakes, fixture signature/scope va ko'chirilgan kod auditi |
| P03 | Regression runner va vaqtinchalik setup | IN PROGRESS | Static PASS / NOT RUN | Bazaviy 21 wrapper va regression-setup tayyor; domain target/baseline guard P05–P08 bilan tugaydi |
| P04 | Real formalarning to'liq imkoniyatlar inventari | IN PROGRESS | UI DISCOVERY | Ko'rinadigan Chromium; pytest/collection bajarilmaydi |
| P05 | ТМЦ yaratish va ТМЦ import regressioni | IN PROGRESS | Static PASS / NOT RUN | 12 item yozildi; 22 Python fayli sintaksisi, lokal importlar, pyflakes va diff check o'tdi; qolgan chuqur caselar davom etadi |
| P06 | Ikki yo'l bilan narx belgilash | PLANNED | NOT RUN | UZS/USD, qayta ochish va ikki yo'l orqali solishtirish |
| P07 | Boshlang'ich qoldiq: 3 usul × 2 hajm | PLANNED | NOT RUN | 6 ta asosiy case va forma validatsiyalari |
| P08 | Qoldiq va orderga tayyorlik | PLANNED | NOT RUN | Aniq ombor/miqdor/narx; tayyor baseline |
| P09 | Smoke saqlanganini va yangi regressionni tekshirish | PLANNED | NOT RUN | Static tekshiruv va ruxsatli real run dalillari |
| P10 | Orderning batafsil regressioni | NEXT PHASE | NOT RUN | `reliz.md` case mappingi va yangi mahsulot variantlari |
| P11 | Boshqa kirim yo'llari va mustaqil regression setup | FUTURE | NOT RUN | Quyidagi kelajak qamrovi |

## Holatni yangilash tartibi

1. Ish boshlanganda tegishli bosqichni `IN PROGRESS` qilish.
2. Har tugallangan ish yoki aniqlangan to'siqdan so'ng shu faylni yangilash:
   checkbox, bosqich holati, o'zgargan fayllar, tekshiruv, dalil va keyingi qadam.
3. Kod yozilib static tekshiruvdan o'tsa `IMPLEMENTED`, real tekshiruvlar ham
   bajarilib yakun mezoni qoplansa `DONE` qilish. Faqat hujjat/Git vazifalari
   uchun ularning o'z tekshiruvi yetarli.
4. Run natijasini alohida yozish: `NOT RUN / PASS / FAIL / BLOCKED / OBSERVED`.
   Yozilgan kodni yoki formaning ochilishini biznes case PASS deb belgilamaslik.
5. `BLOCKED` bo'lsa aniq sabab va davom etish shartini yozish; biznes talabi
   noma'lum bo'lsa kuzatuvni taxminiy PASS/FAILga aylantirmaslik.
6. `reliz.md` — case qadamlari va muhitlar bo'yicha natijalar; ushbu fayl —
   implementatsiya taraqqiyoti. Ikkalasini case ID va test node ID orqali bog'lash.
7. Oldingi run dalillarini saqlab, yangi tekshiruv vaqtini va muhitini alohida yozish.

## Kelishilgan chegaralar

- Barcha yangi ish `dev1`da; foydalanuvchi o'zgarishlarni working tree'dan ko'radi.
- Foydalanuvchi aytmaguncha commit qilinmaydi. Yangi ishlarni boshqa branchlarga
  tarqatish ushbu boshlang'ich tenglashtirishning davomiy avtomatik amali emas.
- Mavjud smoke ssenariylari saqlanadi; umumiy infra uchun import/ulanishlar
  o'zgarishi mumkin. Unrelated o'zgarishlar va `outputs/` dalillari saqlanadi.
- Bitta `test-results/data/data_store.json` ishlatiladi. Yangi setup yozgan
  kalitlari oldingi qiymatlarni almashtiradi; boshqa kalitlar avtomatik
  yangilangan hisoblanmaydi. Alohida smoke/regression data fayli kiritilmaydi.
- Runlar ketma-ket. Parallel yozuvchi smoke/regression sessiyalari rejalashtirilmaydi.
- URL, credential va run qiymatlari mavjud konfiguratsiyadan olinadi; secret
  yoki eski sessiyaning entity IDsi testga va rejaga hardcode qilinmaydi.
- Real forma kerak bo'lganda ko'rinadigan Chromium brauzeridan foydalaniladi.
  Eski screenshot/locatorga asoslanib joriy forma imkoniyatlari taxmin qilinmaydi.
- Har yangi biznes forma uchun maydonlar, tablar, amallar, validatsiya,
  saqlanish va keyingi jarayonga ta'sir iloji boricha qamrab olinadi.
- Vaqtincha import qilinadigan eski setup qadamlari batafsil regression qamrovi
  deb e'lon qilinmaydi; ularni kengaytirish P11ga tegishli.
- `order_beta` qamrovdan chiqarilgan.
- Unit testlar alohida so'ralmasa qo'shilmaydi. Pytest/collection/run foydalanuvchi
  `run qil` deganda bajariladi; reja yozishning o'zi run ruxsati emas.
- 2026-09-21: foydalanuvchi `boshla` deb implementatsiyani boshlashni tasdiqladi.
  Ish jurnali ushbu faylda yuritiladi; generic workflowdagi commit, alohida
  worktree va avtomatik test run talablari foydalanuvchi/repo cheklovlarini almashtirmaydi.

## P00–P01. Git va reja

- [x] Working tree, lokal/remote branchlar va worktreelarni tekshirish.
- [x] `git fetch origin` bilan remote holatini yangilash.
- [x] Orqada qolgan branchlarda dev1da yo'q commitlar yo'qligini tekshirish.
- [x] Lokal `debug`ni `git merge --ff-only dev1` bilan tenglashtirish.
- [x] `origin/dev1` va `origin/debug`ni oddiy fast-forward push bilan tenglashtirish;
      `main` va `origin/main` avvaldan bir xil edi.
- [x] Faol lokal/remote `dev1`, `main`, `debug`ning `d4f97f2` ekanini tekshirish.
- [x] `dev1`ga qaytish. Yangi commit yaratilmagan, force-push ishlatilmagan.
- [x] Tarixiy `origin/backup/main-before-dev1-20260723-278959a`ni `278959a`da
      saqlash; u faol rivojlantirish branchi emas, zaxira nusxa.
- [x] Ushbu rejani root'dagi `regression-plan.md`ga saqlash.

## P02. Umumiy infratuzilma

**Asosiy fayllar:** yangi `tests/conftest.py`, `tests/shared/__init__.py`,
`tests/shared/config.py`, `tests/shared/browser.py`, `tests/shared/reporting.py`;
mavjud `tests/smoke/conftest.py`, `tests/smoke/smoke_config.py`,
`tests/smoke/smoke_browser.py`, `tests/smoke/smoke_reporting.py`,
`tests/smoke/web_context_reporting.py`, `pytest.ini`, `scripts/run_tests.py`.

- [x] Umumiy fixture'larni yuqoriga chiqarish: `session_browser`,
      `session_context`, `session_page`, `page`, `code`, `logger` va umumiy
      loginli page ehtiyoji. Fixture'lar import qilinmaydi, pytest orqali olinadi.
- [x] CLI option va konfiguratsiya hooklarini bir marta ro'yxatdan o'tkazish;
      `.env` ustuvorligi, URL va `NEW_CODE` xulqini saqlash.
- [x] `ROOT_DIR` hisobini fayl ko'chgan yangi chuqurlikka moslash.
      `tests/shared/config.py` avvalgi modul bilan bir chuqurlikda; `parents[2]` saqlandi.
- [x] Browser/context/page yopilishi, timezone, download va trace saqlashni
      umumiy modulga chiqarish; mavjud diagnostika yo'qolmasin.
- [x] Umumiy screenshot, error/report attachment va Allure session yakunini
      ajratish. Child conftest va parent hooklar takroran report yaratmasin.
- [x] Smoke group skip/dependency va Forms metadata qoidalarini smoke ichida
      saqlash. Regression xatosi mustaqil smoke groupni bloklamasin.
- [x] Reporting consumerlari va importlarini `rg` bilan topib moslashtirish;
      kerak bo'lsa eski import manzillariga kichik compatibility eksport qoldirish.
- [x] Umumiy data-store API va fayl yo'lini saqlash. Regression domainlarining
      yangi/eski baseline kalitlarini ajratib tekshirishi P03/P05da yakunlanadi.
- [x] Mavjud testlarni tasodifan umumiy Smartup sozlamalariga majburlamaslik uchun
      `tests/`dagi boshqa suite consumerlarini tekshirish.
- [x] Static import/sintaksis/diff tekshiruvini yozish; real smoke natijasini P09da qayd etish.

P02 dalili: `pyflakes` va `git diff --check` o'tdi. AST orqali eski/yangi fixture
signature va scope tengligi tekshirildi; authorization/progress/web-context
ko'chirilgan implementatsiyalari bir xil. Shared modullarda smoke importi yo'q.
Existing smoke biznes test fayllari o'zgarmagan. Mustaqil static reviewdagi Forms
batch screenshot klassifikatsiyasi tuzatildi; parametrli form total alohida saqlandi.

**Yakun mezoni:** umumiy kod smoke papkasiga bog'lanmasdan ishlaydi, mavjud
smoke entrypoint va ssenariylari saqlanadi, regression bir xil infradan foydalanadi.

## P03. Regression runner va vaqtinchalik setup

**Fayllar:** yangi `tests/regression/__init__.py`, `tests/regression/conftest.py`,
`tests/regression/test_setup/test_0_setup_runner.py`; domain papkalarida alohida
runner/leaf modullar; `scripts/run_tests.py`, `pytest.ini` va README run yo'riqnomasi.

- [x] Smoke'dan `test_*` yoki butun runnerni import qilish o'rniga kerakli `run_*`
      funksiyalarini import qilish; har qadam uchun alohida pytest/Allure wrapper.
- [x] Quyidagi bazaviy ketma-ketlikni saqlash: company (faqat yangi company rejimi),
      legal person → filial → room → robot → natural person → user → formalar/
      rol huquqlari → litsenziya qadamlari → password → UZS/USD narx turlari →
      valyuta → to'lov turlari → ТМЦ to'plami → mijoz → room attachment → ombor.
- [ ] Serverga bog'liq mavjud litsenziya skip/guardlarini saqlash; setupdagi
      har skip regression davom etishiga yetarli sharoit qoldirganini tekshirish.
- [x] Eski ikki mahsulot, eski boshlang'ich qoldiq va aksiya yaratish funksiyalarini
      bu bazaviy setupga avtomatik qo'shmaslik; ularning o'rnini yangi qamrov egallaydi.
- [x] Har `run_*`ning session va oldingi sahifa dependency'sini tekshirib,
      yangi tartibda zarur login/filial/page o'tishlarini aniq belgilash.
- [ ] Setup uchun ketma-ket umumiy session; mustaqil regression case uchun
      o'z preconditioni va alohida hujjat/mahsulot. Bir biznes case boshqa
      mustaqil case yaratgan state'ni kutmasin.
- [ ] Sakkiz mahsulotli tayanchni tayyorlash alohida setup bosqichi bo'lsin;
      shu tayanchni yaratish qadamlari dependency'lari hisobotda ochiq ko'rinsin.
      Mustaqil domain run uchun tayyorlash funksiyalari qayta ishlatilsin.
- [x] `regression-setup` targeti: 21 ta bazaviy setup wrapperi; existing companyda
      Company deselect, litsenziya skip shartlari mavjud run_* funksiyalarida saqlangan.
- [ ] Qolgan targetlar:
      `setup-regression` — yangi setup + mavjud regression domainlari;
      `regression` — joriy baseline bilan. Bu ikkalasi biznes caselar yaratilganda
      qo'shiladi; bo'sh domain targetga PASS taassuroti berilmaydi.
- [ ] Baselinesiz regression va yangi code bilan setupni tashlab ketish holatini
      tushunarli sabab bilan bloklash. Mavjud smoke targetlar tarkibi saqlansin.
- [x] Hozirgi `regression-setup` faqat runner faylini target qiladi; faqat run_*
      importlari bor. Smoke/regression setupni bitta sessiyaga qo'shish bloklangan.
- [ ] Yangi domainlarda runner va standalone leafni bitta targetda ikki marta collect qilmaslik;
      test nomlari/node IDlari takrorlanmasin.

**Yakun mezoni:** regression setupda barcha zarur preconditionlar bor, har qadam
alohida natija beradi, setup xatosidan keyin faqat unga bog'liq ishlar bloklanadi.

## P04. Real forma inventari — har domain kodidan oldin

**Formalarning boshlang'ich ro'yxati:** ТМЦ list/create/view/edit/import,
ТМЦ narx belgilash, Цены list va mahsulot narxlash, boshlang'ich qoldiq
list/create/view/edit, uning Подбор va Импорт oynalari, Остатки ТМЦ va oddiy order.

- [x] Ko'rinadigan Chromiumda joriy test muhitini ochish, company/filialni tekshirish.
- [ ] Har formadagi barcha tab, maydon, default, majburiylik, switch, bog'lanish,
      list action va modalni ro'yxatlash. Dalil uchun screenshot/trace yo'lini yozish.
- [ ] UI qo'llab-quvvatlaydigan yaratish, tahrir, bekor qilish, saqlash, qator
      qo'shish/o'chirish, qidirish/filter va status amallarini case'larga bog'lash.
- [ ] Har imkoniyat uchun happy path, invalid/chegara, Save/reopen va downstream
      tekshiruv zarurligini belgilash. Son/format limitlarini taxmin qilmaslik.
- [ ] O'zaro zid sozlamalarni bitta mahsulotda yoqmaslik; alohida variantlar tuzish.
- [ ] Huquq, konfiguratsiya yoki ma'lumot yetishmasa `BLOCKED` yoki sababli
      qamrov istisnosi yozish; formani faqat ochishni to'liq regression deb hisoblamaslik.

Inventar jadvali shu bo'limga har real tekshiruvdan so'ng qo'shiladi:

| Imkoniyat ID | Forma / maydon / amal | Dalil | Precondition | Case ID | Kutilgan natija manbasi | Qamrov holati |
|---|---|---|---|---|---|---|
| INV-ACCESS | Test userining ERP users litsenziyasi va filialga kirishi | `outputs/regression-design-20260921/license-attached.png`, `user-access-restored.png` | Admin orqali mavjud litsenziyaga faqat kerakli userni biriktirish | P04 precondition | Real UI: biriktirilganlar 1→2; test useri dashboardga kirdi | RESTORED |
| INV-PRODUCT-MAIN | ТМЦ yaratish: nom, alternativ nom, ishlab chiqaruvchi, to'plam, holat/tur, birlik, ikki daraja qadoq, kodlar, yetkazib beruvchi, og'irlik/hajm | `outputs/regression-design-20260921/product-create-inventory.json`, `product-create.png` | Mavjud filial va ТМЦ to'plami | P05 | Real UI maydonlari; tablar va saqlanish xulqi hali tekshirilmoqda | DISCOVERED / NOT RUN |
| INV-PRODUCT-CHAR | Характеристики: Группа, Категория, Торговая марка | `outputs/regression-design-20260921/product-characteristics.json` | Lug'at qiymatlarini testcase preconditionida yaratish/tanlash | REG-PROD-CHAR | Uchta selector real UI'da bor; qiymat yaratish va saqlanish hali tekshirilmagan | DISCOVERED / NOT RUN |
| INV-PRODUCT-PACK | Ikki daraja qadoq va ularning miqdori | `outputs/regression-design-20260921/product-box-options.json`, `product-pallet-options.json` | Birlik va qadoq lug'atlari | REG-PROD-PACK | Joriy UI: 1-daraja Блок/Коробка, 2-daraja Паллета; koeffitsiyent va downstream natija hali tekshirilmagan | DISCOVERED / NOT RUN |
| INV-PRODUCT-BARCODE | Штрих-коды: qo'shish modali, majburiy kod, birlik soni, faol holat, ikki xil save | `outputs/regression-design-20260921/product-barcode-dialog.json` | Noyob test shtrix-kodlari | REG-PROD-BARCODE | Real modal; add/edit/delete/cancel va qayta ochish qamrovi kerak | DISCOVERED / NOT RUN |
| INV-PRODUCT-FILE | Файлы: nom, izoh, upload, holat, save/save-and-close | `outputs/regression-design-20260921/product-file-dialog.json`, `product-files.json` | Testga tegishli fayl; ko'ringan accept ro'yxati png/jpg/jpeg | REG-PROD-FILE | Majburiy nom real UI'da bor; upload/saqlanish xulqi hali tekshirilmagan | DISCOVERED / NOT RUN |
| INV-PRODUCT-VIEW | List actionlari va view: Изменить, Неактивный, Установить цены, История цен, Настройки продаж; viewda asosiy ma'lumot/xarakteristika/hujjatlar | `outputs/regression-design-20260921/product-view.json`, `product-user-list-actions.txt` | O'z mahsuloti yoki read-only mavjud mahsulot | REG-PROD-LIFECYCLE | Mavjud mahsulot bilan navigatsiya ko'rildi; mutatsiya qilinmadi | DISCOVERED / NOT RUN |
| INV-PRODUCT-IMPORT | ТМЦ importi, fayl yuklash/saqlash, shablon, mapping, xatolar jadvali | `outputs/regression-design-20260921/product-import.json`, `product-import-settings.json`, `ТМЦ.xlsx` | Admin → Администрирование → Справочники → ТМЦ → Создать dropdown → Импорт | REG-PROD-IMPORT | Operatsion filialda admin va user uchun import yo'q; Администрирование'da bor. Mapping: boshlang'ich qator 2, 28 ustun; Название/Ед. изм. majburiy | DISCOVERED / NOT RUN |

**Yakun mezoni:** aniqlangan har bir imkoniyat testga yoki aniq sababli istisnoga
bog'langan; noma'lum biznes xulqi alohida ko'rsatilgan. Yakuniy case soni shunda aniqlanadi.

## P05. ТМЦ yaratish va import

**Fayllar:** `tests/regression/test_products/` ichidagi create, edit, validation,
import leaflari va domain runner; zarur takroriy UI choreography uchun domain flow.
Aniq leaf raqamlari P04 inventaridan keyin runner bilan birga belgilanadi.

### Sakkizta tayanch mahsulot

Nom va kodlar regression prefiksi hamda `{code}` bilan noyob yaratiladi.
UZS/USD nomi mahsulot kartasidagi valyuta deb taxmin qilinmaydi; quyidagilar
keyingi sotuv narxining valyutasini ifodalaydi.

| Kalit | Yaratish yo'li | Sotuv narxi | Narxlash yo'li | P07dan so'ng maqsadli qoldiq | Vazifa |
|---|---|---:|---|---:|---|
| UZS-A | Создать | 7000 UZS | ТМЦ listi | 100 | Oddiy hisob-kitob |
| UZS-B | ТМЦ (импорт) | 12500 UZS | Цены listi | 100 | Turli narxli ko'p mahsulot |
| UZS-C | Создать | 2500 UZS | ТМЦ listi | 100 | Chegirma/kombinatsiya |
| LOW | Создать | 5000 UZS | ТМЦ listi | 3 | Qoldiq chegarasi |
| BONUS | Создать | 2000 UZS | Цены listi | 100 | Aksiya uchun bonus mahsulot |
| ZERO | Создать | 9000 UZS | Цены listi | 0 | Narx bor, kirim yo'q |
| USD-A | Создать | 1 USD | ТМЦ listi | 100 | Dollar orderi |
| USD-B | ТМЦ (импорт) | 2.35 USD | Цены listi | 100 | Kasrli narx/yaxlitlash |

### Qo'lda yaratish va forma imkoniyatlari

**Implementatsiya, hali run qilinmagan:**

| Case ID | Kod / parametr | Yozilgan qamrov | Hali qolgan qamrov |
|---|---|---|---|
| REG-PROD-CREATE | `test_01_create_product.py`, 6 mahsulot kaliti | Nom, alternativ nom, kod/artikul/tartib, birlik, to'plam, holat/turlar, 1/2-daraja qadoq, netto/brutto/hajm; save → list → view/ID → edit solishtirish | Ishlab chiqaruvchi/yetkazib beruvchi, xarakteristika, shtrix-kod, fayl, IKPU/ТН ВЭД |
| REG-PROD-CANCEL | `test_02_product_lifecycle.py` | To'ldirilgan create'ni yopish; listda mahsulot saqlanmaganligi | Real run |
| REG-PROD-LIFECYCLE | `test_02_product_lifecycle.py` | O'z mahsulotini yaratish, edit-save, qayta ochish, edit-cancel, oxirgi saqlangan qiymatlar; Новинка belgisi | Real run, status va boshqa list actionlari |
| REG-PROD-REQUIRED | `test_03_product_required_fields.py`, nom/birlik | Bitta majburiy qiymatni bo'shatish, save rad etilishi, invalid control va listda yashirin record yo'qligi | To'plam, format/uzunlik/duplicate validatsiyalari |
| REG-PROD-IMPORT | `test_04_product_import.py` | 28 ustunli shablon/mapping, faqat 2 yangi qatorli XLSX, preview, save, sector'ga attach va test userida list/view/edit solishtirish | Real run; save response/transition hali kuzatilmagan |
| REG-PROD-IMPORT-CANCEL | `test_04_product_import.py` | Noyob 2 qatorli previewni saqlamasdan yopish va listda ikkala kod yo'qligi | Real run; malformed/mixed/duplicate/update import variantlari |

`regression-products` faqat domain runnerini collect qiladi;
`setup-regression-products` core setup + shu runnerdan iborat.
Runner va standalone leaflarni birga tanlash duplicate execution sababli bloklanadi.
Mahsulot card tekshiruvi data-store'ga narx/qoldiq tayyorligini tasdiqlab yozmaydi:
ular `price_verified=False`, `stock_verified=False` bo'lib qoladi.

- [ ] Oltita mahsulotni faqat minimal maydonlar bilan emas, inventardagi
      mos qo'shimcha maydon/tab/sozlama kombinatsiyalariga taqsimlab yaratish.
- [ ] Kod, nom, o'lchov birligi, ТМЦ to'plami, faol holat va mahsulot turini tekshirish.
- [ ] Har saqlashdan keyin listdan kod bilan topish, view/editda barcha kiritilgan
      ma'lumotlarni solishtirish; auto-default bilan qo'lda kiritilganini ajratish.
- [ ] Tahrir qilib saqlash va qayta ochish; bekor qilingan tahrir saqlanmasligini tekshirish.
- [ ] Majburiy maydonlar, tasdiqlangan kod uniqueness qoidasi, uzunlik/format
      limitlari va o'zaro bog'liq sozlamalarni alohida parametr/case bilan tekshirish.
- [ ] Salbiy/destruktiv variantlar uchun alohida vaqtinchalik mahsulot yaratish;
      orderga tayanch bo'ladigan sakkiz mahsulotni noto'g'ri holatda qoldirmaslik.

### ТМЦ (импорт)

- [x] Importga kirish kontekstini aniqlash: admin profilidagi
      `Администрирование → Справочники → ТМЦ → Создать dropdown → Импорт`.
      Oddiy filialda import action yo'q; ortiqcha user huquqlarini yoqish kerak emas.
- [x] Saytdagi joriy `ТМЦ.xlsx` shablonini yuklab olish; import va Настройка
      oynalarining ustun/mapping inventarini dalilga saqlash.
- [x] Shablon tarkibini o'qish: u bo'sh emas, mavjud mahsulotlar va IDlarni ham
      olib keladi. Yangi import fayli faqat testcase qatorlarini oladi; mavjud
      shablon qatorlari va IDlari importga yuborilmaydi.
- [x] Importdan keyingi biriktirish oynasini topish: admin kontekstida
      `Наборы ТМЦ → kerakli to'plam → Прикрепить → Доступные`.
      Bu navigatsiya tekshirildi; yangi import mahsulotini biriktirish hali bajarilmadi.
- [ ] Joriy shablon va qo'llab-quvvatlanadigan ustunlarni real formada tekshirish.
- [ ] Admin orqali import qilingan ikki mahsulotni kerakli ТМЦ to'plami va
      operatsion filialga bog'lash yo'lini tekshirish; test useri listida ko'rinishini tasdiqlash.
- [ ] UZS-B va USD-B uchun kamida ikki valid qatorli XLSX yaratish; mavjud barcha
      mos qo'shimcha import maydonlarini qamrab olish, faylni dalil sifatida saqlash.
- [ ] Fayl yuklash, ustun mappingi va previewdagi qiymatlarni tekshirish.
- [ ] Importni yakunlash, ikkala mahsulotni kod bilan topib Excel bilan solishtirish.
- [ ] Yetishmagan majburiy maydon, noto'g'ri reference/format, takroriy kod,
      valid+invalid aralash fayl va importni bekor qilish caselarini ajratish.
- [ ] Atomik yoki qisman import xulqini real contract bo'yicha belgilash;
      xato chiqishidan tashqari listdagi haqiqiy saqlangan natijani tekshirish.
- [ ] Importni qayta yuborishdagi duplicate/update siyosatini aniqlab, mos assertion yozish.

**Yakun mezoni:** 6 create + 2 import mahsulot qayta ochib tekshirilgan; yaratish,
tahrir, validatsiya va import imkoniyatlari inventar bo'yicha qamrab olingan.

## P06. Ikki yo'l bilan sotuv narxi

**Fayllar:** `tests/regression/test_prices/` domain runner va leaflari.

- [ ] ТМЦ listi → Установить цены: UZS-A, UZS-C, LOW, USD-A.
- [ ] Цены listi → tegishli narx turi → mahsulot narxlash: UZS-B, BONUS, ZERO, USD-B.
- [ ] Har ikki yo'lda UZS va USD narx turi hamda valyutani tekshirish.
- [ ] Save/tasdiqdan keyin qayta ochib narxni tekshirish; ikkinchi kirish yo'li
      orqali ham ayni mahsulot va narx turining qiymatini solishtirish.
- [ ] 2.35 USD kasrining saqlanishi va ko'rsatilishini tekshirish.
- [ ] Narxni o'zgartirish va bekor qilish, majburiylik/format, nol/manfiy/chegara
      qiymatlarni tasdiqlangan biznes qoidaga muvofiq alohida caselarda tekshirish.
- [ ] Bir mahsulot/narx turiga o'zgartirish boshqa mahsulot/narx turini o'zgartirmasligini tekshirish.
- [ ] UI ko'rsatgan qo'shimcha ustun, soliq yoki narx rejimlari uchun shartlarni
      P04 inventariga yozish; hisoblash formulasini kuzatilgan xatodan ko'chirmaslik.
- [ ] Tayanch mahsulotlar narxlarini jadvaldagi qiymatlarda yakunlash.

**Yakun mezoni:** ikkala narxlash yo'li va valyuta ishlaydi, saqlangan qiymatlar
ikki tomonda mos. Sotuv narxi kirim narxidan alohida tekshiriladi.

## P07. Ввод начальных остатков ТМЦ

**Fayllar:** `tests/regression/test_init_balance/` domain runner va leaflari;
XLSX generatsiyasi mavjud kutubxonadan, takroriy yordamchi zarur bo'lsa mavjud
helper ownershipiga mos joydan foydalanadi.

### Uch usul × bitta/ko'p mahsulot

Quyidagi jadval fresh sakkiz mahsulotli baseline uchun. Qoldiqlar yig'indisi
tekshiriladi; mustaqil case runida precondition shu casening o'zida tayyorlanadi.

| Case ID | Kiritish yo'li | Mahsulot va miqdor | Hujjat valyutasi |
|---|---|---|---|
| REG-INIT-01 | Oddiy list, bitta | UZS-A: 90 | UZS |
| REG-INIT-02 | Oddiy list, ko'p | UZS-B: 100; UZS-C: 100 | UZS |
| REG-INIT-03 | Подбор, bitta | LOW: 3 | UZS |
| REG-INIT-04 | Подбор, ko'p | UZS-A: 10; BONUS: 100 | UZS |
| REG-INIT-05 | Импорт, bitta | USD-A: 90 | USD |
| REG-INIT-06 | Импорт, ko'p | USD-A: 10; USD-B: 100 | USD |

- [ ] Har hujjat uchun noyob raqam, to'g'ri ombor, valyuta, sana va inventarda
      aniqlangan boshqa mos maydonlarni to'ldirish/tekshirish.
- [ ] Kirim narxlarini alohida data sifatida belgilash; UZS-A uchun 5000 UZS
      kirim va 7000 UZS sotuv narxi farqini saqlash.
- [ ] Qator miqdori × kirim narxi va hujjat summasini mustaqil hisoblash.
- [ ] Save → qayta ochish: qatorlar, kodlar, miqdorlar, kirim narxlari,
      valyuta, ombor va summa yo'qolmaganini tekshirish.
- [ ] Провести → statusni tekshirish → ombor qoldig'idagi aniq o'zgarishni tekshirish.
- [ ] Подборda qidirish, tanlash/bekor qilish, miqdor o'zgartirish va qaytishda
      mahsulotlar to'g'ri o'tishini tekshirish; kutilmagan dublikat bo'lmasin.
- [ ] Import uchun real shablonga mos bitta va ko'p qatorli yangi Excel yaratish;
      mapping, parse natijasi va formaga ko'chgan qiymatlarni tekshirish.
- [ ] Oddiy gridda qator qo'shish, o'zgartirish va olib tashlash hisobga ta'sirini tekshirish.
- [ ] Bo'sh majburiy maydon, noma'lum kod, noto'g'ri miqdor/narx, dublikat
      mahsulot va aralash import natijalarini biznes contract bilan tekshirish.
- [ ] Invalid hujjatda haqiqiy Save/tasdiq chegarasini tekshirish va hujjat/
      qoldiq o'zgarmaganini isbotlash; wizarddan o'tishni saqlash deb hisoblamaslik.
- [ ] O'tkazilmagan hujjat, tahrir, qayta o'tkazish yoki o'tkazishni bekor qilish
      amallari UI'da mavjud bo'lsa ularning qoldiqqa ta'sirini alohida mahsulotda tekshirish.
- [ ] ZERO mahsulotiga kirim qilmaslik.

**Yakun mezoni:** 6 asosiy case, forma imkoniyatlari va xatolik yo'llari
tekshirilgan; tayanchning yakuniy qoldiqlari P05 jadvaliga mos.

## P08. Остатки ТМЦ va orderga tayyorlik

**Fayllar:** `tests/regression/test_balances/`, orderga tayyorlik uchun
`tests/regression/test_orders/`dagi alohida leaf/runner.

- [ ] Qoldiq listida mahsulot nomi mavjudligini emas, aynan tanlangan filial va
      ombordagi miqdorni tekshirish; filterlar natijaga qanday ta'sir qilishini yozish.
- [ ] UZS-A: 90 + 10 = 100; USD-A: 90 + 10 = 100; LOW: 3;
      ZERO: 0; qolganlar: 100 ekanini tekshirish.
- [ ] Nol qoldiq qatori yashirilgan bo'lsa tegishli filter/qo'llab-quvvatlanadigan
      qoldiq ko'rinishi orqali tasdiqlash; yo'q qatorni o'z-o'zidan nol deb olmaslik.
- [ ] Inventardagi qidirish/filter, ustun, batafsil ko'rish va export amallari
      mavjud bo'lsa natija mazmunigacha tekshirish.
- [ ] Oddiy orderda qoldiqli mahsulotlar tanlanishi, ombor va sotuv narxi mosligini tekshirish.
- [ ] UZS-A: 2 × 7000 = 14000; USD-B: 2 × 2.35 = 4.70 nazorat hisoblari.
- [ ] Narxi bor ZERO mahsulotining ko'rinishi/tanlanishi bo'yicha haqiqiy sozlama
      va biznes qoidani yozish; avtomatik “ko'rinmasligi shart” deb taxmin qilmaslik.
- [ ] Tayyorlik tekshiruvi orderni saqlamasdan tugasa buni aniq qayd etish;
      real order lifecycle qamrovi P10da bo'ladi.

## P09. Tekshirish, dalil va reliz.md

- [ ] Syntax/config/import ownership va `git diff --check` bilan static tekshiruv.
- [ ] Foydalanuvchi `run qil` deganda o'zgargan infraga tegishli mavjud smoke
      targetini va yangi setup-regression targetini ketma-ket ishga tushirish.
- [ ] Setup, domain, parametr va standalone variantlar tasodifan ikki marta
      bajarilmaganini real collection/run natijasidan tekshirish.
- [ ] Smoke/regression natijasi, skip sabablari va dependency bloklarini hisobotda ajratish.
- [ ] Xtrade va smartup.online uchun muhit/build/sana bilan alohida natija;
      bir muhit PASSini ikkinchisiga ko'chirmaslik.
- [ ] Har case uchun ID, precondition, aniq qadam, expected/actual, test node ID,
      screenshot/trace va import faylini `reliz.md` bilan bog'lash.
- [ ] Skill/KB o'zgartirish alohida tasdiqlangan bo'lsa canonical owner orqali
      yozish va `./.venv/bin/python skills/scripts/validate_skills.py`ni bajarish.
- [ ] Ushbu reja jadvali, checkboxlari, muammolar va keyingi qadamni yangilash.

**Birinchi bosqich tugash mezoni:** umumiy infra + regression setup + to'liq
inventar asosidagi ТМЦ/narx/kirim/qoldiq caselari + orderga tayyor baseline.
Run bo'lmasa natija `IMPLEMENTED / NOT RUN`, “barchasi o'tdi” emas.

## P10. Keyingi bosqich — orderning batafsil regressioni

- [ ] `reliz.md`dagi 88 case IDni mavjud autotestlar bilan solishtirib, alohida
      test/parametrlarga mapping qilish; 88 qatorni 88 mustaqil pytest testi deb olmaslik.
- [ ] Oddiy order, tahrir, list/Подбор/import, ko'p SKU va takroriy SKU.
- [ ] Foiz/summa chegirmalari, qator/order kombinatsiyalari va barcha aksiya turlari.
- [ ] Kam/nol qoldiq, rezerv va statuslar o'zgarishi.
- [ ] Sotuvdan keyingi partial/to'liq return va ortiqcha qaytarish nazorati.
- [ ] UZS/USD, kasrli hisoblar, to'lov, qarz, oldindan to'lov va offset.
- [ ] Sana, hisobot/export/print va tegishli sozlamalarning to'liq imkoniyatlari.
- [ ] Oldingi F2/F3/F5/F7 topilmalarini reproducer caselarga bog'lash;
      noaniq D1 biznes qoidasini tasdiqlanmaguncha qat'iy expectedga aylantirmaslik.
- [ ] Har mustaqil order case o'z hujjati va zarur moliyaviy/qoldiq preconditionini
      tayyorlasin; oldingi order sotgan miqdorga yashirin bog'lanmasin.

## P11. Kelajak qamrovi

Foydalanuvchi tushuntirgan stock entry yo'llari; quyidagi beshtasi hozirgi
boshlang'ich qoldiq bosqichidan keyin, preconditionlari bilan rejalashtiriladi:

| Yo'l | Maqsad va zarur shart | Holat |
|---|---|---|
| Ввод начальных остатков ТМЦ | Avvaldan bor mahsulotlarni boshlang'ich qoldiq sifatida kiritish | P07 |
| Закупки → Поступления ТМЦ на склад | Xarid qilib omborga qabul qilish | FUTURE |
| Инвентаризации | Qayta sanashda ortiqcha topilgan mahsulot bilan qoldiqni oshirish | FUTURE |
| Возвраты | Avval sotilgan mahsulotni qaytarish | P10 bilan bog'liq, FUTURE |
| Внутренние перемещения | Ikki ombor orasida o'tkazish; manba omborda stock kerak | FUTURE |
| Межорг. перемещения | Ikki filial orasida o'tkazish; manba filialda stock kerak | FUTURE |

- [ ] Regressionga mos alohida setup funksiyalarini yozish; vaqtinchalik smoke
      importlarini almashtirish, domain testcase kontraktlarini saqlash.
- [ ] Har yangi forma uchun P04dagi inventar va chuqur qamrov tartibini takrorlash.

## Reviewda alohida tekshiriladigan nuqtalar

1. Parent/child conftest bir xil hook/option/reportni ikki marta ishlatmasligi — P02/P09.
2. Umumiy data store'dagi eski ID yangi baseline deb ishlatilmasligi — P02/P03.
3. Narx turi/valyuta, sotuv narxi va kirim tannarxi aralashmasligi — P06/P07/P08.
4. Import xatosi yoki cancel ortidan yashirin saqlangan product/hujjat qolmasligi — P05/P07.
5. Bir case stock, status yoki qarzini o'zgartirib boshqa mustaqil caseni buzmasligi — P03/P10.

## Ish jurnali

| Sana | Bosqich | Bajarilgan ish | Tekshiruv / natija | Keyingi qadam |
|---|---|---|---|---|
| 2026-09-21 | P00 | Lokal/remote faol branchlar dev1ga fast-forward qilindi; dev1da qolindi | Barchasi d4f97f2; yangi commit/force-push yo'q; backup saqlandi | P01 |
| 2026-09-21 | P01 | Kelishilgan talablar, 8 mahsulot, 2 narxlash yo'li, 6 kirim case'i va forma inventari bitta rejaga yig'ildi | Hujjat tekshiruvi o'tdi: majburiy mavzular bor, reliz havolasi mavjud, ortiqcha satr oxiri bo'shliqlari yo'q; test kodi va run yo'q | P02 |
| 2026-09-21 | P02 | Umumiy conftest va shared config/browser/reporting/auth/progress ajratildi; eski smoke importlariga compatibility eksport qoldirildi | Linter, sintaksis, AST moslik auditi va diff tekshiruvi o'tdi; pytest/collection bajarilmadi | P03 |
| 2026-09-21 | P03 | 21 wrapperli regression setup, alohida dependency hooklari, markerlar va regression-setup CLI targeti yozildi | Static tekshiruv o'tdi; existing smoke biznes fayllari o'zgarmadi; domain targetlar hali yo'q | P04, keyin P05–P08 |
| 2026-09-21 | P02–P03 review | Mustaqil static reviewer A2 Forms batch final screenshot label farqini topdi; Forms markeriga qarab label tanlash tiklandi, form_total parametrli caselar bo'yicha saqlandi | Runtime tekshiruvsiz static fix; boshqa aniq defect topilmadi | Real run P09da |
| 2026-09-21 | P04 access | Test useri loginida litsenziya/filial xabari chiqdi. User ruxsati bilan admin mavjud ERP users litsenziyasiga kerakli userni qo'shdi; oldingi user biriktirilgan holda qoldi | Yangi user loginidan keyin o'z filialidagi Trade dashboard ochildi; screenshotlar saqlandi. Pytest/collection bajarilmadi | ТМЦ tablari va import inventarini davom ettirish |
| 2026-09-21 | P04 ТМЦ | Test userida create tablari, shtrix-kod/fayl modallari, ikki daraja qadoq variantlari va mavjud mahsulot view'i ko'rildi. Alohida admin kontekstida ТМЦ importi va mapping ochilib shablon yuklandi | JSON/screenshot/shablon dalillari `outputs/regression-design-20260921/`da. Mahsulot yaratilmagan, import bajarilmagan; bu biznes-case PASS emas | Importning filial/to'plam bog'lanishi va lug'at preconditionlari; keyin P05 kodi |
| 2026-09-21 | P04/P05 davom | Import shablonidagi mavjud ID/qatorlar aniqlandi, to'plamga biriktirish oynasi topildi. Test userining litsenziyasi yana yo'qolgan; admin ro'yxatida boshqa test useri qolgani ko'rildi va kerakli user qayta biriktirildi | Boshqa user saqlandi; login qayta ishladi. O'chirish sababi taxmin qilinmadi; smoke attach setup barcha userlarni ajratishini alohida risk sifatida qayd etamiz | Litsenziya bilan ishlaydigan parallel setup runlardan saqlanish |
| 2026-09-21 | P05 kod | 6 create varianti, mustaqil create-cancel, edit-save/cancel va 2 required validation yozildi; domain runner va 2 CLI target ulandi; baselinesiz/new-code domain va duplicate collector guard qo'shildi | Pyflakes o'tdi; pytest/collection bajarilmadi. To'liq P05 qamrovi emas | Import va qolgan ТМЦ imkoniyatlari |
| 2026-09-21 | P05 import kodi | Ikki mahsulotli import va preview-cancel kodi, template/mapping guard, sector attach va user profilida qayta tekshirish qo'shildi. openpyxl/et_xmlfile dependencylari o'rnatildi | Real UI qadoq lug'atida `Коробка→кор`, `Блок→бл` tasdiqlandi; Excel shu qisqa nomlarni yozadi. Attach confirm ko'rildi va bekor qilindi; mavjud begona mahsulot biriktirilmadi | Static review; qolgan chuqur ТМЦ maydonlari va keyingi narx/kirim bosqichlari |
| 2026-09-21 | P05 static tekshiruv va mapping | 22 Python fayli AST bilan tekshirildi, lokal importlar va 6 runner funksiyasining 12 item matritsasi tekshirildi; pyflakes va git diff --check o'tdi. reliz.mdga 12 NOT RUN item va node mapping yozildi | Pytest import/collection/business run bajarilmadi; yangi 8 mahsulot hali real tizimda yaratilmagan. Commit yo'q | P05: ishlab chiqaruvchi/yetkazib beruvchi, xarakteristika, shtrix-kod/fayl, status va negative import; keyin P06 narx |
| 2026-09-22 | Main tuzatishlarini dev1ga olish | `git fetch origin`, `git switch dev1`, `git merge --no-commit --no-ff origin/main` bajarildi. Dev1dagi regression commit `ca48278` saqlandi; mainning `3885c0f` va `d9aa9e0` tuzatishlari birlashtirildi. README va runner avtomatik moslashdi | Konflikt yo'q; 52 Python fayli AST, regression/shared/runner pyflakes va staged diff check PASS. Regression/shared/smoke fayllari, pytest.ini, requirements.txt va reliz.md dev1 HEAD bilan aynan teng. Pytest/collection bajarilmadi; merge commit va push qilinmadi; outputs saqlandi | Dev1da P05 qolgan chuqur caselarini davom ettirish; merge foydalanuvchi commitga ruxsat berguncha ochiq qoladi |

| 2026-09-22 | Merge commit | Foydalanuvchi dev1dagi o'zgarishlarni commit qilishni aniq so'radi; main tuzatishlari va reja yangilanishi merge commitga kiritiladi | Oldingi static tekshiruvlar PASS; ushbu qadamda biznes kodi o'zgarmadi. Test/collection run yo'q; push va outputs commit qamroviga kirmaydi | Dev1da P05 qolgan caselarini davom ettirish |

Keyingi har ish yakunida bu jadvalga yangi qator qo'shiladi va yuqoridagi
“Hozir qayerdamiz?” bo'limi ham birga yangilanadi.
