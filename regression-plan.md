# Smartup Regression — amalga oshirish rejasi va holat jurnali

> Ijro: ushbu sessiyada bosqichma-bosqich, `superpowers:executing-plans` va repo
> `skills/project-guide/SKILL.md` qoidalari asosida. Bu foydalanuvchi so'ragan
> ishchi reja; loyiha bilimlarining canonical manbasi `skills/` bo'lib qoladi.

**Maqsad:** mavjud smoke ssenariylarini saqlab, `tests/regression/` ichida
formalarning imkoniyatlari, validatsiyalari va biznes natijalarini tekshiradigan
takror ishlatiladigan Playwright/pytest testlarini yaratish.

**Arxitektura:** umumiy fixture, browser, konfiguratsiya va diagnostika smoke'dan
yuqoriga chiqariladi. Regression setup hozircha mavjud smoke `run_*`
funksiyalarini import qiladi. Setup uchun umumiy data store va umumiy natija
mexanizmi saqlanadi; TMZ natijalari test yonidagi data_store.json ga yoziladi.
Smoke va regression runlari ketma-ket bajariladi.

**Texnologiya:** Python, pytest, Playwright Chromium, Allure, mavjud
`AutoBasePage` va repo helperlari; importlar uchun haqiqiy XLSX fayllar.

**Talab manbasi:** foydalanuvchining 2026-09-21 kuni tasdiqlagan suhbatdagi
talablari, quyidagi “Kelishilgan chegaralar” bo'limi va tarixiy caselar uchun
[reliz.md](reliz.md). Oldingi qo'lda run natijalari yangi autotestning PASS
natijasi hisoblanmaydi.

## Hozir qayerdamiz?

**Joriy product tuzilmasi:** product runner smoke runner kabi explicit
`@allure.title` + `def test_*` wrapperlaridan test faylidagi `run_*`ni chaqiradi.
Barcha product data, UI, Excel va narxlash qadamlari shu test fayllarida:
`run_product_full` va `run_import_product` ichida. Alohida `flow_product/` va
`product_cases.py` yo'q. Standalone wrapperlar ham saqlanadi. Product runnerdagi
aliaslar olib tashlandi; main runner 21 setup + 2 product testidan iborat.
Product nodelari: `test_01_tmz_1` va `test_02_import_tmz`.
TMZ-1 manual yaratiladi, TMZ-2–6 bitta Excel orqali import qilinadi.
Base metodlari va fixturelar saqlanadi; refactordan keyin run yo'q.

**Multiselect:** `select_first=True` BasePage va AngularBasePagega qo'shildi.
U birinchi ko'rinadigan variantni tanlab, chipni tekshiradi. Product caselarining
ikkita joyida raw tanlash o'rniga shu metod ishlatiladi; retest NOT RUN.

**Eng yangi run — 2026-09-22, 14:05–14:08:** foydalanuvchining local product
runneri **4 FAIL / 0 PASS**. TMZ-1/2/3 yaratish/karta/narx tekshiruvlari o'tgan,
yakuniy close heading locatori yiqilgan. TMZ-4/5/6 Excel previewga xatosiz
yuklangan, ammo input qiymatini matn deb izlaydigan locator yiqilgan; savega
yetmagan. **Ikkala locator tuzatildi; tuzatishdan keyingi run NOT RUN.**
Narx close flowi faqat mavjud base metodlaridan foydalanadi: ТМЦ narx formasi
`click → expect_page`; Цены narx formasi `click → confirm_biruni(нет) → expect_page`.
Takroriy heading/confirm locatorlari olib tashlangan. Import
preview mahsulotni nom bo'yicha filtrlaydi, kod/nom/birlikni input qiymatidan
solishtiradi; qator soni faqat mahsulot inputi bor qatorlar bo'yicha olinadi.
Oldingi FAIL natijalari `reliz.md`da saqlangan; ular PASSga almashtirilmadi.

**2026-09-22 — tasdiqlangan yangi product scope implementatsiya qilindi.**
Oldingi 8 mahsulot/12 item matritsasi va cancel/edit/required caselari bekor
qilindi. O'shanda 3 ta manual test va 3 qatorli bitta import testi bor edi — jami
4 testcase, 6 mahsulot. 2026-09-25 kuni takroriy manual testlar birlashtirildi:
hozir 1 manual + 5 qatorli import — 2 testcase, 6 mahsulot. Karta va ikki valyutadagi narx tekshiruvlari
yozildi; birinchi local run va undan keyingi tuzatish holati yuqorida. Foydalanuvchi dona uchun mavjud
**шт / Количество** birligini tasdiqladi.

Oxirgi yangilanish: **2026-09-25 (Asia/Tashkent)**.

- **Branch:** `dev1`.
- **Main bilan birlashtirish:** `origin/main` (`d9aa9e0`) `dev1`ga
  (`ca48278`) `--no-commit --no-ff` bilan konfliktsiz birlashtirildi.
  Foydalanuvchining 2026-09-22 kungi aniq ruxsati bilan merge va reja
  yangilanishi `93816e9` commitida yakunlandi. Push qilinmadi; `outputs/`
  commitga kiritilmadi. Keyingi asosiy runner o'zgarishlari hali commit qilinmagan.
- **Bajarildi:** P02 umumiy infra va P03 bazaviy setup runneri yozildi; statik tekshiruvlar o'tdi.
- **Runnerlar:** alohida setup va products runnerlari saqlandi;
  `tests/regression/test_0_regression_runner.py` hamda `regression` CLI targeti
  setup → products tartibini bitta pytest sessiyasida birlashtiradi.
- **Joriy ish:** P05/P06 local runidagi ikki locator tuzatildi; qayta run kutilmoqda. Keyingi implementatsiya P07/P08 — kirim va qoldiq.
- **Muhit:** mavjud test useriga admin orqali ERP users litsenziyasi biriktirildi;
  o'z filialidagi dashboardga kirishi tekshirildi. Oldingi biriktirilgan user saqlandi.
- **Regression kodi:** 21 ta setup wrapperi + 2 product testi. TMZ-1
  alohida yaratiladi; TMZ-2/3/4/5/6 bitta Excel orqali import qilinadi. Kod/nom
  search, view, birlik/to'plam va narxning saqlanishi tekshiriladi.

- **Test run:** foydalanuvchining local product runi 4 FAIL; agent tuzatishdan keyin pytest/collection yoki biznes run bajarmadi.
- **Commit:** joriy merge va reja yangilanishini commit qilishga 2026-09-22 kuni
  ruxsat berildi. Bu keyingi ishlarga avtomatik commit/push ruxsati emas.

| ID | Bosqich | Ish holati | Run/tekshiruv holati | Dalil yoki yakun mezoni |
|---|---|---|---|---|
| P00 | Branchlarni tenglashtirish | DONE (boshlang'ich) | Git bilan tekshirildi | 2026-09-21: faol branchlar `d4f97f2`; 2026-09-22: main tuzatishlari dev1ga commitsiz merge qilindi, tafsilotlar jurnalda |
| P01 | Tasdiqlangan rejani saqlash | DONE | Hujjat tekshiruvi o'tdi | Majburiy mavzular, reliz havolasi va format tekshirildi |
| P02 | Umumiy infra: fixture, config, browser, reporting | IMPLEMENTED | Static PASS / NOT RUN | 15 Python fayl sintaksisi, pyflakes, fixture signature/scope va ko'chirilgan kod auditi |
| P03 | Regression runner va vaqtinchalik setup | IMPLEMENTED | Static PASS / NOT RUN | 21 setup + 2 product wrapper; asosiy va alohida .py runnerlar, dependency/duplicate guard |
| P04 | Real formalarning to'liq imkoniyatlar inventari | IN PROGRESS | UI DISCOVERY | Ko'rinadigan Chromium; pytest/collection bajarilmaydi |
| P05 | ТМЦ yaratish va import — yangi scope | FIX IMPLEMENTED | Oldingi run FAIL / retest NOT RUN | 3 karta yaratildi; import preview input locatori tuzatildi |
| P06 | Ikki yo‘l bilan narx belgilash | FIX IMPLEMENTED | Oldingi run FAIL / retest NOT RUN | TMZ-1/2/3 narxlari tasdiqlangan; close locatori tuzatildi; import narxlashiga run yetmagan |
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
- Setup uchun bitta `test-results/data/data_store.json` ishlatiladi. Yangi setup yozgan
  kalitlari oldingi qiymatlarni almashtiradi; boshqa kalitlar avtomatik
  yangilangan hisoblanmaydi. TMZ natijalari esa
  `tests/regression/test_products/data_store.json`da saqlanadi.
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

**Fayllar:** yangi `tests/regression/test_0_regression_runner.py`, `tests/regression/__init__.py`, `tests/regression/conftest.py`,
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
- [x] Olti mahsulotli tayanch alohida product runnerida: uch manual test va
      bitta import testi. Har test shared setupga tayanadi; boshqa product
      testi yaratgan mahsulotni talab qilmaydi.
- [x] `regression-setup` targeti: 21 ta bazaviy setup wrapperi; existing companyda
      Company deselect, litsenziya skip shartlari mavjud run_* funksiyalarida saqlangan.
- [x] 2026-09-22 talabiga mos asosiy runner: `tests/regression/test_0_regression_runner.py` va
      `regression` targeti — setup + hozir tayyor regression domainlari.
      `Test01Setup` → `Test02Products`; har case alohida pytest/Allure item.
      Oddiy pytest fayli alohida runnerlardagi testlarni staticmethod orqali
      qayta ishlatadi; fixture/parametr/title va classga ko'chirilgan markerlar
      saqlanadi. Ichma-ich pytest yoki subprocess yo'q. Asosiy va alohida
      runnerlarni birga tanlash duplicate guard bilan bloklanadi.
- [x] Alohida `regression-setup`, `regression-products` va faqat shu ikki qismga
      mo'ljallangan `setup-regression-products` targetlarini saqlash.
      Oldingi rejalashtirilgan baseline-only `regression` ma'nosi almashtirildi;
      mavjud baseline uchun `regression-products` ishlatiladi.
- [x] Baselinesiz regression va yangi code bilan setupni tashlab ketish holatini
      tushunarli sabab bilan bloklash. Mavjud smoke targetlar tarkibi saqlansin.
- [x] Hozirgi `regression-setup` faqat runner faylini target qiladi; faqat run_*
      importlari bor. Smoke/regression setupni bitta sessiyaga qo'shish bloklangan.
- [x] Product domainida runner va standalone leafni bitta targetda ikki marta collect qilmaslik;
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

**Holat: IMPLEMENTED / RETEST NOT RUN.** Checkboxlar kod yozilganini bildiradi;
biznes case PASS bo'lganini emas. Foydalanuvchi rad etgan eski caselar
runner va leaf fayllaridan olib tashlandi; eski ish jurnali tarix sifatida qoldi.

### Olti mahsulotning joriy matritsasi

| Mahsulot | Yaratish | Netto / brutto / hajm | UZS | USD | Narx yo'li |
|---|---|---|---:|---:|---|
| TMZ-1 | Создать | 100 / 110 / 120 | 5000 | 5 | ТМЦ → Установить цены |
| TMZ-2 | Excel import | 200 / 210 / 220 | 10000 | 10 | Цены → Установка цен |
| TMZ-3 | Excel import | 300 / 310 / 320 | 15000 | 15 | Цены → Установка цен |
| TMZ-4 | Excel import | 400 / 410 / 420 | 20000 | 20 | Цены → Установка цен |
| TMZ-5 | Excel import | 500 / 510 / 520 | 25000 | 25 | Цены → Установка цен |
| TMZ-6 | Excel import | 600 / 610 / 620 | 30000 | 30 | Цены → Установка цен |

Barchasida nom aynan `TMZ-N`, kod `tmz-N-{code}` (conftestdan), birlik `шт`,
tur `Товар`, faol holat va filialda birinchi ko'ringan `Наборы ТМЦ` ishlatiladi.
Import narxlari manual narxlarning 5000 UZS / 5 USD qadamini davom ettiradi.

### Manual test: TMZ-1

- [x] Test filialida Справочники → ТМЦ ochish.
- [x] Har test ichidagi alohida Allure qadamida kod mavjud emasligini tekshirish.
- [x] Создать formasida nom, kod, birlik, Товар, birinchi to'plam va uchta butun sonli vazn/hajmni kiritish.
- [x] Saqlash → listga qaytish → xato yo'qligini tekshirish.
- [x] Kod va nom bilan alohida qidirish; aynan run kodi qatorini tanlash.
- [x] View'da nom, kod, tur, netto/brutto/hajm va product IDni tekshirish.
- [x] View'da birlik/to'plam yo'q: Изменить formasida qiymatlarni o'qish, o'zgartirishsiz yopish.
- [x] ТМЦ listidan Установить цены → tegishli UZS/USD price typega jadvaldagi narxlar.
- [x] Saqlash/tasdiq → qayta ochish → har ikkala narx aynan tengligini tekshirish.
- [x] Barcha product amallari test faylidagi run_* ichida, raqamlangan Allure qadamlari bilan; alohida product flow/helper papkasi yo'q. Runner smoke uslubida test_* wrapper orqali chaqiradi.
- [ ] Real run va Allure/trace dalillari.

### Bitta import testi: TMZ-2, TMZ-3, TMZ-4, TMZ-5, TMZ-6

- [x] User filialida birinchi to'plamni aniqlash; admin uchun alohida browser context.
- [x] Admin → Администрирование → Справочники → ТМЦ: beshta kod yo'qligi.
- [x] Создать dropdown → Импорт; 28 ustunli shablon/mapping va start row 2 tekshiruvi.
- [x] Yuklangan shablondagi mavjud qator/IDlarni ko'chirmasdan yangi 5 qatorli Excel yaratish.
- [x] Загрузить файл → tasdiqlash → preview'da 5 qator va xatolar yo'qligi.
- [x] Загрузить и сохранить → tasdiqlash → preview tozalanishi → listda beshta kod/nom.
- [x] Наборы ТМЦ orqali mahsulotlarni aniqlangan to'plamga biriktirish.
- [x] Oddiy userda beshta kartani kod/nom search, view va birlik/to'plam orqali solishtirish.
- [x] Цены listidan UZS va USD turini ochish → har 5 mahsulotga narx → save → qayta ochib solishtirish.
- [ ] Real run, yaratilgan Excel, product ID va saqlangan narx dalillari.

**Fayllar:** `tests/regression/test_products/test_01_create_product.py`da
bitta to'liq manual test; `test_02_import_products.py`da to'liq Excel import
testi. `test_0_products_runner.py` ularning ikkitasini
smoke uslubidagi test_* → run_* wrapperlari orqali yig'adi. Asosiy `tests/regression/test_0_regression_runner.py`
avval setup, keyin shu testlarni ishlatadi. Runner va uning leaflarini birga
tanlash bloklanadi. Alohida product flow va data factory fayllari yo'q.

Run muvaffaqiyatli bo'lsa test yonidagi `tests/regression/test_products/data_store.json`ga `regression_tmz_1` …
`regression_tmz_6` yoziladi: code/server/company/product ID, karta qiymatlari,
`card_verified=True`, `price_verified=True`, `stock_verified=False`.
Yangi attempt boshlanishida shu product recordi tozalanadi. Bu kodning xulqi;
hozir yangi TMZlar yaratilgan yoki orderga tayyor deb belgilanmaydi.

## P06. Ikki yo'l bilan sotuv narxi

**Holat: IMPLEMENTED / RETEST NOT RUN.** Narxlash kodi bevosita product
testlari ichida; alohida price flow yoki price runner yo'q.

- [x] TMZ-1: ТМЦ → Установить цены orqali UZS va USD narx.
- [x] TMZ-2/3/4/5/6: Цены → price type → Установка цен orqali har biriga UZS/USD narx.
- [x] Saqlash va qayta ochish orqali barcha 12 narx qiymatini tekshirish.
- [x] O'qish uchun ochilgan narx formasini saqlamasdan yopish; save-changes confirmda нет.
- [ ] Real run natijasi va narxlarning saqlanish dalili.

**Yakun mezoni:** 6 karta va 12 narx tekshiruvi muvaffaqiyatli; qoldiq hali
P07/P08ga tegishli. Eski negative/edit/cancel narx caselari joriy scope emas.

## P07. Ввод начальных остатков ТМЦ

**Fayllar:** `tests/regression/test_init_balance/` domain runner va leaflari;
XLSX generatsiyasi mavjud kutubxonadan, takroriy yordamchi zarur bo'lsa mavjud
helper ownershipiga mos joydan foydalanadi.

### Uch usul × bitta/ko'p mahsulot

Yangi TMZ-1…TMZ-6 matritsasi ishlatiladi. Qaysi mahsulotga qancha kirim
qilish va kirim narxlari P07 implementatsiyasida belgilanadi; eski UZS-A/LOW/ZERO
matritsasi joriy emas. Kutilgan qoldiq har hujjat oldi/keyingi delta bilan tekshiriladi.

| Case ID | Kiritish yo'li | Miqdor/valyuta |
|---|---|---|
| REG-INIT-01 | Oddiy list, bitta mahsulot | P07da belgilanadi |
| REG-INIT-02 | Oddiy list, bir nechta mahsulot | P07da belgilanadi |
| REG-INIT-03 | Подбор, bitta mahsulot | P07da belgilanadi |
| REG-INIT-04 | Подбор, bir nechta mahsulot | P07da belgilanadi |
| REG-INIT-05 | Импорт, bitta mahsulot | P07da belgilanadi |
| REG-INIT-06 | Импорт, bir nechta mahsulot | P07da belgilanadi |

- [ ] Har hujjat uchun noyob raqam, to'g'ri ombor, valyuta, sana va inventarda
      aniqlangan boshqa mos maydonlarni to'ldirish/tekshirish.
- [ ] Kirim narxlarini sotuv narxidan alohida data sifatida belgilash.
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

**Yakun mezoni:** 6 asosiy case, forma imkoniyatlari va xatolik yo'llari
tekshirilgan; yakuniy qoldiqlar P07da belgilangan miqdorlarga mos.

## P08. Остатки ТМЦ va orderga tayyorlik

**Fayllar:** `tests/regression/test_balances/`, orderga tayyorlik uchun
`tests/regression/test_orders/`dagi alohida leaf/runner.

- [ ] Qoldiq listida mahsulot nomi mavjudligini emas, aynan tanlangan filial va
      ombordagi miqdorni tekshirish; filterlar natijaga qanday ta'sir qilishini yozish.
- [ ] Har bir TMZ uchun P07 kirimlari yig‘indisi va yakuniy qoldiqni solishtirish.
- [ ] Nol qoldiq qatori yashirilgan bo'lsa tegishli filter/qo'llab-quvvatlanadigan
      qoldiq ko'rinishi orqali tasdiqlash; yo'q qatorni o'z-o'zidan nol deb olmaslik.
- [ ] Inventardagi qidirish/filter, ustun, batafsil ko'rish va export amallari
      mavjud bo'lsa natija mazmunigacha tekshirish.
- [ ] Oddiy orderda qoldiqli mahsulotlar tanlanishi, ombor va sotuv narxi mosligini tekshirish.
- [ ] TMZ-1: 2 × 5000 = 10000 UZS; 2 × 5 = 10 USD nazorat hisoblari.
- [ ] Nol qoldiqli mahsulot ssenariysi uchun haqiqiy sozlama
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

| 2026-09-22 | P03 asosiy runner | Alohida setup/products runnerlari saqlanib, `scripts/run_regression.py` va `regression` targeti qo'shildi. Tartib bitta ro'yxatdan olinadi; setup va products bitta pytest sessiyasiga uzatiladi, mavjud case/node ID va dependency hooklari saqlanadi. README va reliz yo'riqnomasi yangilandi | 15 Python fayli AST, ikki CLI fayli pyflakes, runner path mavjudligi va git diff --check PASS. Pytest/collection va real run bajarilmadi; yangi commit/push yo'q | P05 qolgan caselari |

| 2026-09-22 | P03 oddiy pytest runner | Foydalanuvchi aniqlashtirishiga ko'ra `scripts/run_regression.py` olib tashlandi. Asosiy fayl `tests/regression/test_0_regression_runner.py`: `Test01Setup` → `Test02Products`, alohida runnerlarning 21 + 6 parametrli wrapperi qayta ishlatiladi. Company deselect va duplicate guard asosiy faylga moslandi; README va reliz node prefikslari yangilandi | 16 Python fayli AST, pyflakes, original wrapperlarga alias/tartib mosligi va diff check PASS. Pytest/collection/run bajarilmadi; commit/push yo'q | P05 qolgan caselari |

Keyingi har ish yakunida bu jadvalga yangi qator qo'shiladi va yuqoridagi
“Hozir qayerdamiz?” bo'limi ham birga yangilanadi.

| 2026-09-22 | P05/P06 yangi scope | Eski 12 item o‘rniga 3 manual TMZ + bitta 3 qatorli import testi yozildi; ikki narxlash yo‘li va qayta ochish tekshiruvlari qo‘shildi. User mavjud шт / Количество birligini tasdiqladi. Main runner 21 setup + 4 product wrapperga moslandi | Static PASS; pytest/collection va biznes run bajarilmadi. Joriy o‘zgarishlar commit/push qilinmagan | P07/P08 kirim/qoldiq; alohida so‘ralganda real run |
| 2026-09-22 | Yakuniy static tekshiruv | 16 Python fayli AST va lokal import yo‘llari; main runnerning 21 + 4 alias tartibi; leaf amallarining bir qatorligi; pyflakes va git diff --check | PASS. Real UI/source orqali importdagi ikkala confirm, preview tozalanishi va Цены lokal grid search modeli aniqlanib flowga moslandi. Yangi mahsulot/import/narx save bajarilmadi | Real run hali NOT RUN; P07/P08 rejalashtirilgan |
| 2026-09-22 | Local run locator tuzatishlari | Narx close headingi DOM matni bilan tekshiriladi; import preview nom bo'yicha filtrlanib input qiymatlari tekshiriladi, qator sanog'idan header chiqarildi | 14 regression Python fayli AST, product domain pyflakes va git diff --check PASS. Retest NOT RUN; commit/push yo'q | Fresh setup/code bilan productlarni qayta tekshirish |
| 2026-09-22 | Close flowini base metodlariga qaytarish | Raw heading/confirm locatorlari va re/expect importlari olib tashlandi. ТМЦ close to'g'ridan-to'g'ri expect_page; Цены close tasdiqni confirm_biruni orqali нет bilan yopadi | Static tekshiruv; retest NOT RUN. Oldingi raw locator tuzatishi almashtirildi; commit yo'q | Ruxsatli qayta run |
| 2026-09-22 | Product kodlarini test ichiga ko'chirish | 3 manual va bitta import testining barcha data/UI/Excel/narxlash qadamlari test_* ichiga olindi; product flowlar, run_* va data factory olib tashlandi. Product runner 4 original testga alias beradi; main node nomlari saqlandi | 9 Python fayli AST, regression pyflakes, 4 test/runner/main alias va fixture signature auditi, git diff --check PASS. Pytest/collection/run bajarilmadi; commit/push yo'q | Ruxsatli qayta run |
| 2026-09-22 | Product runner smoke uslubida | User talabiga ko'ra aliaslar o'rniga 4 ta Allure title bilan explicit test_* wrapper yozildi; ular leaf test fayllaridagi run_* entrypointlarni chaqiradi. Barcha biznes qadamlar shu test fayllarida, alohida product flow yo'q; standalone wrapperlar saqlandi | 9 Python fayli AST, 4 wrapper/entrypoint signature va main runner mapping, regression pyflakes, git diff --check PASS. Pytest/collection/run va commit/push bajarilmadi | Ruxsatli qayta run |
| 2026-09-22 | Base multiselect birinchi variant | Legacy/A2 multiselectga select_first=True qo'shildi; tanlash, chip tekshiruvi, close va list return kontrakti saqlandi. 3 manual + 1 import case raw locatorlari bitta base chaqiruviga o'tdi | Public API parity, pyflakes va git diff --check PASS. Test/collection run va commit yo'q | Ruxsatli qayta run |
