# Test Yozish — Batafsil Loyiha Qoidalari

Bu reference `write-test` uchun setup, group, Forms suite, fixture, authorization
va migratsiya detallarini saqlaydi. Faqat vazifaga tegishli bo'limni o'qi.

## Mundarija

- [Loyiha strukturasini tushun](#1-loyiha-strukturasini-tushun)
- [Test fayl shabloni](#2-test-fayl-shabloni-run_-test_-ikki-funksiya)
- [Asosiy qoidalar](#3-asosiy-qoidalar)
- [Runnerga qo'shish](#4-runnerga-qoshish)
- [Loyiha xususiyatlari](#5-loyiha-xususiyatlari)
- [Ish tartibi](#6-ish-tartibi)

Quyidagi qoidalarga qat'iy rioya qil:

## 1. Loyiha strukturasini tushun

- Testlar: `tests/smoke/test_setup/`, `tests/smoke/test_life_cycle/`,
  `tests/smoke/test_forms/` yoki mos `tests/smoke/test_groups/.../`
- Flowlar: `tests/smoke/flows/`
- User setup runner: `tests/smoke/test_setup/test_0_setup_runner.py`
- Group runnerlar: har bir group papkasida `test_0_group_runner.py`
- Full/groups targetlari: `scripts/run_tests.py` ichidagi runner fayllari ro'yxati
- Pytest hook va fixture'lar: `tests/smoke/conftest.py`
- Run konfiguratsiyasi va runner collection: `tests/smoke/smoke_config.py`
- Progress, failure artifact va Allure report: `tests/smoke/smoke_reporting.py`

## 2. Test fayl shabloni (`run_` + `test_` ikki funksiya)

Har bir test fayl IKKI funksiyadan iborat (test_legal_person / test_filial / test_room / test_robot real namunalari):

- **`run_<nomi>(page, code, ...)`** — qayta ishlatiladigan biznes logika; setup/group runner zanjiri shuni chaqiradi. Odatda `page` ni **allaqachon login qilingan** deb qabul qiladi. Istisno: setupning birinchi umumiy itemi `run_legal_person` create/existing modega mos admin loginni o'zi bajaradi. Raqamlangan docstring testcase + `with allure.step("N - ...")` bloklari.
- **`test_<nomi>(page, code, ...)`** — `@allure.title(...)` bilan pytest entry; alohida/debug run uchun. `authorization(...)` (+ forma faqat filialda ko'rinsa `base.switch_filial(...)`) qilib, so'ng `run_<nomi>(...)` ni chaqiradi. Kerakli fixturalarni (`save_data`/`load_data`) qabul qilib `run_` ga uzatadi.

```python
import allure
from playwright.sync_api import expect            # Python assert emas, faqat kerak bo'lsa import
from tests.smoke.flows.flow_authorization import authorization
from utils.base_page import BasePage

pytestmark = [allure.epic("Smoke"), allure.feature("<Feature>"), allure.story("<Story>")]

# ----------------------------------------------------------------------------------------------------------------------

def run_<nomi>(page, code, save_data=None):
    """Testcase: <maqsad>.

    1. <Tab> -> <Menyu> ro'yxatini ochish.
    2. "Создать" -> majburiy maydonlarni to'ldirish.
    3. Saqlab, ro'yxatda nom/kod/status ko'rinishini tekshirish.
    """
    entity_name = f"<entity>-pw{code}"
    entity_code = f"c_<short_entity>_pw{code}"
    base = BasePage(page)

    with allure.step("1 - <Entity> ro'yxatiga o'tish"):
        base.navigate_to(tab="<Tab>", name="<Menyu>")
        base.expect_page(heading="<Ro'yxat heading>")

    with allure.step("2 - Yangi <entity> formasini to'ldirish"):
        base.click(name="Создать")
        base.expect_page(heading="<Create heading>")
        base.input(label="Код", value=entity_code)
        base.input(label="Название", value=entity_name)
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        base.click(name="Сохранить", exact=True)
        base.expect_page(heading="<Ro'yxat heading>")
        base.grid(entity_name, entity_code, "Активный")

    # Setup baseline'ni group testlarga uzatish kerak bo'lsa (oxirgi step):
    #     save_data("<key>", entity_code)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("<Inson o'qiydigan test nomi>")
def test_<nomi>(page, code, save_data):
    authorization(page, who='admin')
    base = BasePage(page)
    # base.switch_filial(name=f"filial-pw{code}")   # forma faqat o'sha filialda ko'rinsa
    run_<nomi>(page, code, save_data=save_data)
```

### `run_` / `test_` konvensiyasi qoidalari

- **Maksimal base funksiya**: `base = BasePage(page)` qilib olinadi va `base.navigate_to/expect_page/switch_filial/click/text/form_view/input/b_input/multiselect/checkbox/grid_controller/grid/grid_cell/confirm_biruni/confirm_biruni_if_visible/close_biruni_alert/wait_for_loader` ishlatiladi. Raw `page.get_by_role/locator` faqat mos base funksiya yo'q joyda (masalan murakkab scoped filter yoki upload elementi). Grid qatorini bosish kerak bo'lsa alohida wrapper emas, `base.grid(..., click=True)` ishlatiladi; qaytgan rowning aniq ustunini tekshirish yoki o'qish uchun raw `.tbl-cell.nth(...)` emas, `base.grid_cell(row, index, ...)` ishlatiladi.
- **allure.step raqamlari docstring qadamlari bilan mantiqan mos** kelsin; step nomi qisqa va professional.
- **Test data** — `run_` boshida lokal `f"...{code}"` o'zgaruvchilar; faqat
  setup baseline'ni group testlarga uzatish kerak bo'lsa oxirgi stepda
  `save_data(...)`. Group testcase boshqa group testcase uchun data saqlamaydi.
- **Entity name/code patterni** — yangi yoki refactor qilinayotgan setup entitylarda `entity_name = f"<entity>-pw{code}"`, `entity_code = f"c_<qisqa_entity_alias>_pw{code}"` ishlatilsin (masalan Natural Person `c_n_p_pw{code}`); code qiymati uzun entity nomini takrorlamasin. Oldindan downstream bog'liqligi tasdiqlangan biznes hujjat formatlari alohida saqlanadi.
- **`run_` odatda auth qilmaydi** (page login qilingan deb keladi).
  Istisnolar: setup chainning birinchi umumiy itemi `run_legal_person`
  `authorization(who="admin")` qiladi; rol almashtiradigan flowlar ham
  `run_` ichida kiradi (masalan `run_room_attachment` userga o'tadi).
- **Takroriy `switch_filial` qo'yma**: setup zanjiri bitta `session_page` ni bo'lishadi, shuning uchun filial konteksti `run_` lar orasida saqlanadi. Zanjirda filialga BIR MARTA o'tiladi (birinchi kerak bo'lgan `run_` — masalan `run_room` filial-pw{code} ga o'tadi), keyingi `run_` lar (robot, natural_person, ...) o'sha filialni meros qilib oladi va QAYTA `switch_filial` qilmaydi (ortiqcha kod). Standalone/debug run uchun `switch_filial` ni `test_` wrapper'ga qo'y (run_ ichiga emas) — shunda zanjirda takrorlanmaydi, alohida run'da esa default filialdan to'g'ri filialga o'tadi.
- **Verifikatsiya zanjiri**: save → `base.expect_page(list heading)` → (ro'yxatda topish uchun kerak bo'lsa) `grid_controller(search=...)` → `grid(code, name, "Активный")`.
- **Lokal helper** faqat haqiqiy biznes/flow murakkabligini yashirsa va shu faylda ishlatilsa faylda `_` prefiksi bilan qoladi; bir nechta testda kerak bo'lsa `flows/` yoki `BasePage` ga chiqariladi. 1 qatorlik wrapper yozilmaydi.
- **Soni aniq biznes qadamlari loopga yashirilmaydi**: bitta testdagi alohida Allure step va alohida ma'noga ega bo'lgan kam sonli bo'limlar (masalan room attachment'dagi `Типы оплат`, `Склады`, `Кассы`) `list + tuple` va umumiy loopga yig'ilmasin; har biri ochiq `with allure.step(...)` blokida yozilsin. Loop faqat haqiqiy batch/matrix ko'rinishidagi ko'p bir xil elementlar uchun ishlatiladi.
- Fayl boshida module-level `pytestmark = [allure.epic, allure.feature, allure.story]` va funksiyalar orasida `# ---...---` separator.

### Funksiya parametrlarini formatlash

Tags: test, style, function, parameters
Status: user-reported
Verified: 2026-08-03
Source: user

- Qoida: yangi yoki o'zgartirilayotgan test, flow va helperlarda funksiya definition hamda chaqiruv parametrlari bitta fizik qatorda yoziladi; line uzunligi sabab ularni avtomatik ko'p qatorga bo'lib yuborilmaydi.
- Testda ishlatish: `base.expect_page(...)`, `base.grid_cell(...)`, `base.form_view(...)` va boshqa chaqiruvlarning argumentlarini bir qatorda saqla.

## 3. Asosiy qoidalar

- **Fixtures** — conftest.py dan keladi, import qilma:
  - `page` — yakka test uchun fresh page; `session_page` — setup chain; `group_user_page` — group chain (login qilingan)
  - `code` — 6 xonali unikal son; `save_data` / `load_data` / `require_data` — data_store; `logger`
- **Allure**: har bir test `@allure.title()` va `with allure.step()` bilan bo'lishi SHART
- **Locator**: `page.locator()` ishlatilsin, `page.find_element()` EMAS
- **Assert**: `expect(locator).to_be_visible()` ishlatilsin, Python `assert` EMAS
- **Project helper first**: sahifa ochilishi, heading, semantic click, grid row/cell, form input, checkbox/switch, b-input/multiselect va loader kutish uchun avval mavjud loyiha helperlarini ishlat (`base.expect_page(...)`, `base.click(...)`, `base.grid(...)`, `base.grid_cell(...)`, `base.input(...)`, `base.checkbox(...)`, `base.wait_for_loader(...)`). `utils/base_page.py` ichida mos method bor bo'lsa raw `page.locator(...)`, raw `page.get_by_role(...)` yoki yangi local helper yozilmaydi; raw `expect(...)` faqat mos helper yo'q bo'lsa yoki yangi reusable helper yozishdan oldin lokal tekshiruv uchun ishlatiladi.
- **b-input API bir xilligi**: single-select uchun `base.b_input(label=..., value=..., expect_value=..., return_value=...)`, multi-select uchun ham shu uslubdagi `base.multiselect(label=..., value=..., expect_value=..., return_value=..., clear=...)` ishlatiladi. Auto-selected chipni tekshirish uchun `expect_value`, tanlash uchun `value` beriladi.
- **BasePage scope**: `utils/base_page.py` ga hamma yoki ko'p testlar ishlatadigan umumiy UI primitive'lar yoziladi. Faqat bitta testga kerak bo'lgan biznes/helper logika test faylida `_helper_name(...)` local helper bo'lib qoladi.
- **Navigation wrapper ishlatilmaydi**: `navigate_to`, `expect_page`, `switch_filial` flow helper sifatida import qilinmaydi; test/flow ichida `base = BasePage(page)` qilib, to'g'ridan-to'g'ri `base.navigate_to(...)`, `base.expect_page(...)`, `base.switch_filial(...)` ishlatiladi.
- **Page ready check**: `base.expect_page(..., heading=...)` heading visible bo'lishi bilan birga Smartup loader (`.block-ui-overlay:visible`) yo'qolganini ham kutadi. Loader yo'q bo'lsa 2 sekund kutmaydi; darhol davom etadi. Bu route/page state check uchun yetarli; lekin keyingi action aynan grid/form ichki async reloadga bog'liq bo'lsa `base.wait_for_loader()` alohida qoladi.
- **Save transition ochiq yoziladi**: `base.click(name="Сохранить", exact=True)` → confirm majburiy bo'lsa `base.confirm_biruni(...)` → `base.expect_page(heading=..., url=...)`. `expect_page(heading=...)` loader overlay yo'qolishini ham kutgani uchun yangi list/view sahifasiga o'tishda alohida `wait_for_loader()` yozilmaydi. Order wizard ikonkalı save tugmasida partial match default bo'lgani uchun faqat `base.click(name="Сохранить")` yoziladi.
- **Timeout**: DEFAULT_TIMEOUT (10s) yetarli; kerak bo'lsa `page.wait_for_timeout()` emas, `expect(...).to_be_visible()` kutish
- **Session data**: `save_data("key", value)` va `load_data("key")` setup
  baseline → group yo'nalishida ishlatiladi; group testcase'lar o'zaro data
  almashmaydi.
- **`code`**: har bir test uchun unikal identifikator, nom sifatida ishlating

## 4. Runnerga qo'shish

Yangi user setup testi yozilgandan keyin `tests/smoke/test_setup/test_0_setup_runner.py` ga import va `@allure.title` bilan qo'sh:

```python
from tests.smoke.test_setup.test_XX_<nomi> import run_<nomi>

@allure.title("XX - <Nomi>")
def test_XX_<nomi>(session_page: Page, code):
    run_<nomi>(session_page, code)
```

## 5. Loyiha Xususiyatlari

### Runner config va dinamik qiymatlar
- Repo rootda `.env` mavjud bo'lsa direct `pytest`/PyCharm run konfiguratsiyasi undan olinadi; `.env` yo'q bo'lsa terminal/CI flaglari ishlaydi.
- Lokal `.env` bo'lsa `COMPANY_URL` va company mode credentiallari o'sha yerdan
  olinadi; `.env` yo'q muhitda mos `--url`, `--company-code/--company-password`
  yoki `--create-company --head-email/--head-password` CLI flaglari ishlaydi.
- `.env`dagi `CREATE_COMPANY=1` bo'lsa setup runnerdagi `test_00_company`
  collectionda qoladi; aks holda `pytest_collection_modifyitems` uni deselect
  qiladi. Runtime `pytest.skip(...)` ishlatilmaydi, shu sabab Company testi
  Allure'da skipped test sifatida ko'rinmaydi.
- `CREATE_COMPANY=1` uchun `HEAD_ADMIN_EMAIL` va `HEAD_ADMIN_PASSWORD`
  majburiy; `DISABLE_LICENSE_POLICY` ham faqat shu rejimda ishlaydi.
- Setup authorization alohida test emas: `test_01_legal_person` boshida admin
  login qilinadi. Create rejimida admin company kodi `test_00_company`
  `data_store.json`ga saqlagan `company_code`dan, existing rejimida esa
  `COMPANY_CODE`dan olinadi. Existing rejimdagi `COMPANY_CODE=0`
  `data_store.json`dagi saqlangan `company_code`ni qayta ishlatadi; har ikki
  rejimda parol `COMPANY_PASSWORD`.
- Dinamik email va shunga o'xshash qiymatlar test/flow ichida active company code bilan quriladi:
  ```python
  user_email = f"user-pw{code}@{active_company_code}"
  ```

### code fixture
- `NEW_CODE=1` (yoki `.env` yo'q muhitda `--new-code`) bo'lsa yangi `random.randint(100000, 999999)` yaratadi (6 xonali)
- `NEW_CODE=0` bo'lsa runner yoki yakka testligidan qat'i nazar `test-results/data/data_store.json` dan `"code"` kalitini o'qiydi
- Alohida `REUSE_CODE`/`--reuse-code` ishlatilmaydi; yangi/eski code tanlovining yagona source'i `NEW_CODE`
- Agar `data_store.json` bo'lmasa: `pytest.exit()` bilan aniq xato beradi

### Tanlov holatini tekshirish
- Radio, checkbox yoki select option uchun faqat label/matn ko'rinishini emas, tanlangan holatini ham (`expect(...).to_be_checked()` yoki mos value assert) tekshir.

### Test ichidagi Allure step va helper uslubi
- Bitta testga xos create/view/security kabi ketma-ket UI qadamlari local helperga
  ajratilmaydi; ular `run_*` ichidagi tegishli `with allure.step(...)` blokida
  ochiq yoziladi. Project helper chaqiruvining parametrlari bitta qatorda yoziladi;
  alohida helper faqat qayta ishlatiladigan yoki haqiqatan murakkab flow uchun qoladi.
- Label qabul qiladigan project helper chaqiruvlarida qiymat positional berilmaydi;
  aniq `label="..."` keyword parametri bilan yoziladi.
- Accessible button/tab nomini qabul qiladigan project helperlarda ham qiymat
  positional berilmaydi; aniq `name="..."` keyword parametri bilan yoziladi.
- Project helperning default parametr qiymati testda qayta yozilmaydi; parametr
  faqat default xatti-harakatni o'zgartirish kerak bo'lsa beriladi.

#### Yangi page/form/modal uchun Allure step chegarasi
Status: code-confirmed
Verified: 2026-07-31
Source: user; `skills/write-test/SKILL.md:33`; `skills/write-test/references/project-rules.md:175`
- Qoida: har bir yangi page, forma yoki modal ochilishi alohida raqamlangan
  `with allure.step(...)` blokiga ega bo'ladi. Transition actioni va shu yangi
  state'ni tasdiqlovchi `base.expect_page(heading=...)` bir blokda turadi.
- Bir Allure step ichida ketma-ket bir nechta yangi sahifa ochib, bir nechta
  `base.expect_page(...)` yozilmaydi; har bir keyingi transition yangi stepga
  ajratiladi.
- `allure.setup` ishlatilmaydi; loyiha API'si `allure.step`.

### `expect_page` heading scope
- Heading aniq konteyner ichida tekshirilishi kerak bo'lsa `base.expect_page(heading=..., root="<selector>")` ishlat; `root` berilmasa heading butun sahifadan qidiriladi, loader esa har ikki holatda global tekshiriladi.

### `grid` holatini tekshirish
- Bo'sh gridni majburiy tasdiqlash uchun `base.grid(state="empty", root="<grid selector>")` ishlat; helper ko'rinadigan grid ichidagi aniq `нет данных` matnini auto-retry bilan kutadi.
- Grid holati bo'yicha branch qilish uchun `base.grid(state="empty", return_bool=True, root="<grid selector>")` ishlat; u bo'sh grid uchun `True`, ma'lumotli grid uchun `False` qaytaradi.
- Ma'lum grid qatori mavjudligini majburiy tasdiqlash uchun `base.grid("row text", root="<grid selector>")` ishlat. Branch kerak bo'lsa raw `.tbl-row.filter(...).is_visible()` yozma; `base.grid("row text", return_bool=True, root="<grid selector>")` qator ko'rinsa `True`, topilmasa `False` qaytaradi.
- `return_bool=True` bir martalik tekshiruv; assertion rejimi targetni retry qiladi, lekin oldingi state ham targetga mos bo'lishi mumkin. Tab yoki filter gridni almashtirsa har ikki rejimdan oldin `base.wait_for_loader()` chaqir.

### authorization (rolga qarab login)
- Yagona funksiya: `authorization(page, *, who="admin"|"user"|"head", code=None)`. `who` majburiy keyword-only parametr: har bir chaqiruv login rolini ochiq yozishi shart. **Eski `authorization_user` OLIB TASHLANGAN — ishlatma.**
- `who="user"` → `user-pw{code}@{company}` + `USER_PASSWORD`/`USER_PASS`. Avvalgi `authorization_user(page, code)` o'rniga `authorization(page, who="user", code=code)` yoz.
- `who="admin"` → `ADMIN_EMAIL`/`admin@{company}` + `ADMIN_PASSWORD`/`COMPANY_PASSWORD`.
- `who="head"` → `HEAD_ADMIN_EMAIL`/`HEAD_ADMIN_PASSWORD` (company yaratish uchun).
- `authorization` code generatsiya qilmaydi va `data_store.json`dan code o'qimaydi; `who="user"` uchun `code=code` majburiy. Yangi/eski code tanlovining yagona source'i `NEW_CODE` boshqaradigan `code` fixture.
- `authorization(...)` oxirida `dashboard(page)` orqali `Trade` heading ko'rinishini o'zi tekshiradi; undan keyin `expect(... "Trade" ...).to_be_visible()` ni qayta yozma.
- Credentiallar tashqaridan uzatilmaydi; `authorization` ularni faqat `who` qiymatiga qarab o'zi tanlaydi.
- Credentiallar `.env` dan olinadi (precedence: `.env` yutadi — `smoke_config.option_or_env`).

### Selenium migratsiya source fayli
- Foydalanuvchi Selenium test kodini rootdagi `for_migratsiya.py` fayliga qo'yadi;
  migratsiya so'ralganda shu fayldan o'qib Playwright + pytest smoke testga
  o'tkaz. UI/smoke runni faqat user aynan `run qil` deganda bajar.
- Migratsiya qilingan Playwright kodni ham `for_migratsiya.py` faylining davomiga yoz; runnerga yoki test flowga avtomatik qo'shma, foydalanuvchi tekshirib o'zi ko'chiradi.
- Migratsiyada foydalanuvchi `run_tests.sh` oldin run qilinganini aytsa, user setup tayyor deb hisobla; user bilan login qil va `code` qiymatini `test-results/data/data_store.json` dan ol.
- Agar foydalanuvchi Playwright codegen pytest kodini bersa, Seleniumdan taxminiy migratsiya qilma; codegen kodini asos qilib olib loyiha fixture, Allure step, `code`, `authorization(who="user", code=code)`, helper flow va locator patternlariga moslab ber.
- Codegen kodini moslashda har bir ochilgan sahifa, forma yoki view uchun `expect(...)` bilan ochilganini tasdiqla; mavjud login/navbar flowlari bo'lsa, codegen qatorlari o'rniga o'shalarni ishlat.
- Codegen `page.goto("https://...")` kabi hardcode to'liq URL yozadi; bularni hech qachon kodda qoldirma. Conftest `--url` ni `os.environ["COMPANY_URL"]` ga yozadi va `tests/smoke/flows/flow_authorization.company_url()` shuni o'qiydi. Har bir hardcode URL ni `f"{company_url()}/login.html"`, `f"{company_url()}/a2/biruni/md/company_list"` kabi global URL ga bog'la (path qismi qoladi, domen `company_url()` dan keladi). `company_url` ni `flow_authorization` dan import qil.
- Umumiy test ma'lumotlarini ajratish uchun random ishlatma, `code` fixture qiymatini ishlat; bu test boshida generatsiya bo'ladi va butun sessiya davomida saqlanadi.
- `code` fixture umumiy entity nomlari va testlarni ajratish uchun ishlatiladi;
  agar formaning o'z `code`/`number` maydoni setup baseline sifatida group
  testlarga kerak bo'lsa, alohida `contract_code_{random_son}` kabi qiymat
  generatsiya qil, listda aynan shu qiymat bilan recordni top va setup
  muvaffaqiyatli tugaganda `save_data` orqali saqla. Group testcase bu usul
  bilan sibling consumer yaratmaydi.
- Contract add formasida generated `contract_code_{random_son}` qiymati `Код` inputiga yoziladi; `Номер` inputi bilan almashtirib yuborma.
- Dinamik test qiymatlarini test boshida alohida o'zgaruvchiga yig'ib olma; kerakli joyida `f"...{code}"` ko'rinishida yoz.
- Barcha testlarda qayta ishlatiladigan umumiy helperlar, masalan `b-input` tanlash, local test helper emas `utils/base_page.py` ichidagi `BasePage` methodi bo'lsin.
- `input[ng-model=...]` kabi Angularga bog'langan locatorlardan iloji boricha foydalanma; label/role/text asosidagi `BasePage.fill_textbox_by_label`, `BasePage.select_b_input`, `page.get_by_role(...)` kabi locatorlarni afzal ko'r.
- Smoke UI testlarda form inputlarini to'ldirish, switch/radio/checkbox/button bosish uchun `page.evaluate()` ishlatma; real user action bo'lgan `locator.click()`, `locator.fill()`, `locator.press()` va `expect(...)` ishlat. `page.evaluate()` faqat o'qish/diagnostika yoki haqiqiy user flowga ta'sir qilmaydigan yordamchi holatlarda ishlatiladi.
- Test nomi, Allure title va step nomlari professional, sodda va test maqsadini darhol tushuntiradigan bo'lsin.
- Har bir test boshida docstringda testcase qadamlarini yoz; docstringdagi qadamlar test ichidagi `with allure.step(...)` bo'limlari bilan mantiqan mos kelsin.
- Add form testlarida birinchi navbatda `Код` inputini qidir va recordni listda code bo'yicha top; agar `Код` inputi bo'lmasa keyin nom/name bo'yicha yur.
- Add formadagi barcha majburiy `*` inputlarni albatta to'ldir.
- Test add qilgan har bir element list formada ham, view formada ham ko'ringanini tekshirishi shart.
- Agar qo'shilgan elementni list formadan topish uchun kerakli ustun yoki search yo'q bo'lsa, grid settingdan kerakli ustunni va shu ustun bo'yicha searchni yoq; Smartup listlarida bu umumiy pattern.
- Add formaga kiritiladigan nom, kompaniya, shaxs, manzil kabi biznes qiymatlarni mantiqan `Faker` bilan generatsiya qil; testda qidirish/bog'lash oson bo'lishi uchun kerakli joyda `code` yoki saqlangan entity code qo'shimchasini saqla.
- Smartup test yozish jarayonida yangi formaga kirilganda yoki URL/form state o'zgarganda screenshotni `skills/smartup-guide/references/forms/screenshots/<form-slug>/` ichiga saqla; `test-results/screens/smartup/` forma arxivi uchun ishlatilmasin.
- Natural Person alohida entity flow/test hisoblanadi; boshqa testcase jismoniy
  shaxs yaratishi kerak bo'lsa `flow_natural_person` reusable oqimini ishlatadi,
  locator/fill/assert logikasini dublikat qilmaydi.

### Group testcase mustaqilligi, flow chegarasi va BasePage-first

Status: user-reported
Verified: pending
Source: user; 2026-07-31 current group/flow code audit

Bu bo'lim yangi yoziladigan va refactor qilinadigan group testlari uchun target
architecture hisoblanadi. Eski A/B/C implementatsiyasi 2026-07-31 kuni
o'chirilgan; ular qayta yozilganda quyidagi qoidalar joriy contract bo'ladi.

#### Group testcase mustaqilligi

- Har bir group testcase `user_setup` muvaffaqiyatli tugagan fresh holatdan
  mustaqil ishlashi kerak.
- Bitta group case boshqa case yaratgan order, contract, action, project,
  setting yoki `data_store` keyni o'qimaydi. Runnerdagi `A-01`, `A-02` tartibi
  report tartibi, dependency tartibi emas.
- Testga feature-specific precondition kerak bo'lsa, u shu testcase'ning
  Arrange qismida idempotent yaratiladi/sozlanadi yoki tasdiqlangan shared setup
  baseline'dan olinadi.
- Group case natijasi keyingi case uchun `save_data` qilinmaydi. `save_data`
  faqat tashqi report/debug artefakti uchun zarur bo'lsa case-prefiksli key
  bilan ishlatilishi mumkin; consumer dependency yaratmaydi.
- Target: bitta case failed bo'lsa shu groupning boshqa caselari skip
  qilinmasin. Joriy default bunga teskari — cascade skip ishlaydi; undan chiqish
  faqat group runnerdagi `pytest.mark.smoke_group("X", independent=True)`
  markeri bilan bo'ladi. Joriy runtime xatti-harakati uchun `run-smoke`
  skillidagi `Test dependency modeli`ni o'qi.
- Cleanup faqat testcase o'zi yaratgan yoki o'z unique `code`/case IDsi bilan
  aniq topgan dataga ishlaydi; boshqa testcase datasi cancel/edit qilinmaydi.

#### Testcase ichki tuzilishi

- `run_<case>(...)` ichida Arrange → Act → Assert biznes oqimi ko'rinib turadi.
  Boshqa `run_*` testcase chaqirilmaydi va testcase ichiga boshqa testcase
  yashirilmaydi.
- Har leaf faylda bitta biznes testcase bo'ladi. Standalone `test_*` wrapper va
  runner wrapper shu bitta `run_*` funksiyani chaqiradi.
- Docstring qadamlari, `allure.step` raqamlari va real UI transitionlar bir
  ma'noda bo'ladi; duplicate step raqami yoki boshqa testcase title'i
  ishlatilmaydi.
- Save'dan keyin `print(...)` diagnostika assertion o'rnini bosmaydi: list va
  viewdagi biznes qiymatlar `BasePage` orqali tekshiriladi.

#### Setup, group va Forms runner/leaf fayllarini tartib bilan nomlash

Status: code-confirmed
Verified: 2026-07-31
Source: user; `tests/smoke/test_setup/test_0_setup_runner.py`; `tests/smoke/test_groups/test_0_grup/test_0_group_runner.py`; `tests/smoke/test_groups/test_report_grup/test_0_group_runner.py`; `tests/smoke/test_forms/test_0_forms_runner.py`

- Setup runner doim `test_0_setup_runner.py` deb nomlanadi; setup leaf fayli wrapper raqamiga mos `test_00_<case>.py`, `test_01_<case>.py`, ... prefixini oladi.
- Mustaqil setup biznes amallari alohida pytest wrapper va alohida leaf fayl oladi; masalan UZB price type `test_13_price_type_uzb.py`, USA price type `test_14_price_type_usa.py`, Currency esa `test_15_currency.py`.
- Har bir group papkasidagi runner fayli doim `test_0_group_runner.py` deb nomlanadi.
- Har bir group leaf test fayli runnerdagi o'rniga mos ikki xonali prefix bilan nomlanadi: `test_01_<case>.py`, `test_02_<case>.py`, ....
- Forms runner `test_0_forms_runner.py`; Forms leaf modullari runner tartibiga mos `test_01_<case>.py`, `test_02_<case>.py`, ... deb nomlanadi.
- Runner wrapper nomi va Allure title leaf fayl tartibini aynan takrorlaydi; yangi case orasiga qo'shilsa keyingi leaf fayllar ham runner tartibiga mos qayta raqamlanadi.

#### Unit test qo'shmaslik va run qilmaslik

Status: user-reported
Verified: 2026-08-04
Source: user

- Foydalanuvchi aynan unit test yozish yoki o'zgartirishni so'ramasa, smoke,
  infra, reporting, runner yoki boshqa kod o'zgarishi uchun yangi unit test
  qo'shilmaydi va mavjud unit test fixture/expectationlari o'zgartirilmaydi.
- `Tuzat`, `o'zgartir`, `amalga oshir` yoki umumiy verification so'rovi unit test
  artefaktini yaratish/o'zgartirishga ruxsat bermaydi; unit test uchun alohida
  explicit buyruq kerak.
- Test commandini ishga tushirish authoritysi bu yerda takrorlanmaydi; yagona
  manba — `run-smoke` skillidagi `User-reported Execution Qoidasi`. Default
  tekshiruv shu qoidaga muvofiq read-only/statik inspection, syntax/config
  parse, linter va `git diff --check` bilan cheklanadi; test yozilmagani va run
  qilinmagani handoffda aniq aytiladi.

#### Flow admission gate

Yangi `flow_*` faqat quyidagilardan kamida bittasi rost bo'lsa yaratiladi:

1. Ko'pchilik shu domain testlari o'tishga majbur bo'lgan umumiy gateway
   (`flow_order_list` kabi).
2. Kamida uchta mustaqil leaf testda aynan bir xil ko'p qadamli UI choreography
   takrorlanadi va uni ajratish test maqsadini yashirmaydi.
3. Popup/download/modal kabi texnik state machine bir nechta testda bir xil
   retry/cleanup talab qiladi.

Flowga quyidagilar kiritilmaydi:

- testcase-specific product/quantity/payment/status/expected amount;
- contract/action/project kabi biznes preconditionni yaratib, butun scenarioni
  final stepgacha tayyorlash;
- `check_form`, `save`, `next_page` kabi ko'p branchli parametrlar orqali bir
  funksiyani bir nechta testcasega aylantirish;
- testga xos business assertion, `save_data/load_data` yoki Allure testcase
  step'lari.

Bir yoki ikki testda ishlatiladigan qadam leaf testda `BasePage` bilan ochiq
qoladi. Takrorlanish real paydo bo'lmaguncha oldindan abstraksiya yaratilmaydi.

#### BasePage-first

- Page state, input, b-input, select, checkbox/radio, grid, view value, save,
  confirm, alert va loader uchun avval mavjud `BasePage`/`AngularBasePage`
  funksiyasi ishlatiladi.
- Mos base method bor joyda raw locator, local one-line wrapper yoki yangi flow
  yozilmaydi.
- Raw Playwright faqat BasePage qamramagan maxsus interaction uchun leaf testda
  minimal scope bilan ishlatiladi. Shu interaction uch yoki undan ko'p testda
  takrorlansa avval BasePage primitive sifatida umumlashtirish ko'rib chiqiladi.
- Flow BasePage'ni almashtirmaydi; flow ichida ham mavjud BasePage primitive'lari
  ishlatiladi.

#### `run_base_order` refactor mezoni

`run_base_order` uslubi target yo'nalish sifatida olinadi: order listga o'tish
uchun umumiy `flow_order_list`, qolgan qadamlar esa leaf testda BasePage bilan
ko'rinadi. Final variantda u:

- runner tartibiga mos ikki xonali raqamli leaf faylda turadi;
- unique va maqsadga mos Allure title oladi;
- docstring/allure step raqamlarini bir xil saqlaydi;
- raw locator o'rniga `base.click(name="Сохранить", ...)`, kerak bo'lsa
  `base.confirm_biruni(...)`, so'ng `base.expect_page(...)` ishlatadi;
- list/viewda order ID va barcha asosiy qiymatlarni assert qiladi, `print`
  bilan cheklanmaydi.

#### Group-0 — setup baseline asosidagi base order

Status: live-ui-confirmed
Verified: 2026-07-31
Source: user;
`tests/smoke/test_groups/test_0_grup/test_01_create_base_order.py`;
`tests/smoke/test_groups/test_0_grup/test_0_group_runner.py`; live UI

- Mavjud `run_base_order` refactor qilinib, order grouplarining birinchi
  mustaqil `Group-0` testcase'i sifatida olinadi.
- Group-0 faqat muvaffaqiyatli `test_0_setup_runner.py` yaratgan baseline
  entitylar va `code`ga tayanadi; boshqa group yaratgan contract, action, order
  yoki `data_store` keyni o'qimaydi.
- Group-0ning biznes maqsadi setupdagi room, robot, representative, client,
  product, price, payment type va balance bilan oddiy orderning
  add → list → view happy pathini tekshirishdir.
- Group-0 boshqa grouplar uchun order yoki boshqa precondition yaratmaydi;
  uning failure'i setup failure'i hisoblanmaydi va mustaqil keyingi group
  caselarini bloklamaydi.
- Leaf va Group-0 runner targetlari real UI'da alohida muvaffaqiyatli
  tekshirilgan.

### Setup va Group test execution modeli
- Group runner faylida har bir case alohida pytest test sifatida yig'iladi va `pytest.mark.smoke_group("A")` kabi decorator/marker bilan o'z groupiga biriktiriladi; group caselari full run ichida bitta chain-testga birlashtirilmaydi.
- Runner wrapperda ko'rinadigan test nomining yagona source'i `@allure.title(...)`; wrapper faqat tegishli `run_*` funksiyani chaqiradi. Telegram progress eventlari `conftest.py` hooklaridan title/marker/path orqali avtomatik chiqadi, test body ichida `progress_step` yoki takroriy title yozilmaydi.
- Group runnerdagi thin wrapper signature va uning `run_*` chaqiruvi argumentlari uzun bo'lsa ham bitta qatorda yoziladi; fixture/argumentlar alohida qatorlarga bo'linmaydi.
- Yangi testlar har doim yangi server/baza holatida ham ishlashi kerak; lokal debugda oldingi rerunlardan data ko'paygan bo'lsa ham, testni mavjud dataga suyanib yozma.
- Fresh bazada feature settinglar default o'chirilgan bo'lishi mumkin; testga kerak bo'lgan settingni mavjud holatga suyanmay, idempotent tarzda yoqib/sozlab keyin asosiy flowga o't.
- User setup testlari bir-biriga bog'liq: oldingi setup test keyingi setup test uchun kerakli ma'lumot yoki entity yaratadi; setup ichida test yiqilsa keyingi setup test yura olmasligi mumkin.
- User setup testlari muvaffaqiyatli o'tgandan keyin joriy runnerga ulangan group testlar boshlanadi.
- Har bir group test faqat user setup baseline'ga bog'liq; boshqa group yoki shu
  groupdagi boshqa testcase yaratgan data/state'ga suyanmaydi.
- Cascade/skip runtime qoidasi bu yerda takrorlanmaydi; yagona manba —
  `run-smoke` skillidagi `Test dependency modeli`. Qisqasi: group ichida test
  yiqilsa default holda shu groupning qolgan caselari skip qilinadi, keyingi
  grouplar esa run bo'lishda davom etadi.
- Group/testcase artefakti saqlanishi shart bo'lsa o'z case/group prefiksidan
  foydalanadi, lekin boshqa testcase bu keyni consumer dependency sifatida
  o'qimaydi.
- Group runnerlar `tests/smoke/test_groups/test_<X>_grup/test_0_group_runner.py` ko'rinishida bo'lsin; group ichidagi tartib wrapper test nomlari orqali `X-01`, `X-02` tarzida aniq berilsin.
- Har yangi group runner qo'shilganda `scripts/run_tests.py` ichidagi `GROUP_RUNNER_PATHS` ro'yxatiga va `tests/smoke/smoke_config.py::full_runner_paths()` ro'yxatiga qo'shilsin.
- Full run `test_0_setup_runner.py`, keyin joriy `GROUP_RUNNER_PATHS` group runner fayllarini bitta pytest sessiyasida collect qiladi; alohida `test_all_runner.py` outer-chain fayli ishlatilmaydi.
- Mexanizm pytest hook/marker orqali bo'lsin: `pytest.mark.user_setup` setup chain uchun, `pytest.mark.smoke_group("A")` kabi markerlar group chain uchun ishlatiladi.
- Bitta group failed bo'lsa BOSHQA groupning caselari skip qilinmaydi; shu group
  ichidagi keyingi caselar esa `independent=True` bo'lmasa skip qilinadi.
  `user_setup` failed bo'lsa setupga bog'liq group testlar skip qilinadi,
  `setup_independent=True` olgan runner (masalan Forms) ishlashda davom etadi.
- Grouplar bir-birining browser/page holatini meros qilib olmasin: har bir group runner modul-scoped `group_session_page` oladi; user grouplari `group_user_page` bilan bitta login/page'ni bo'lishadi.
- `group_session_page` faqat browser context/page lifecycle uchun javobgar va `code`
  fixture'ini qabul qilmaydi. `code` faqat test data yoki user login talab qiladigan
  `group_user_page`/test wrapperda so'raladi; aks holda admin-only Forms runner
  saqlangan `data_store.json` bo'lmasa fixture setupdayoq to'xtaydi.
- Fixture nomidan uning lifecycle scope'i, runnerda ulashilishi va login roli
  tushunarli bo'lsin; yangi noaniq `group`/`session` kombinatsiyalari qo'shilmasin.
- Group ichidagi `run_*` funksiyalari `login` parametrini qabul qilmaydi. User grouplarida loginni `group_user_page` fixture bir marta bajaradi; fresh `page` ishlatadigan standalone pytest wrapper esa `run_*` dan oldin `authorization(...)` qiladi. Admin rolidan boshlanishi testning o'z preconditioni bo'lgan caselar `authorization(who="admin")` ni parametrsiz va ochiq bajaradi.
- Bitta testga xos local yordamchi funksiyalar shu test faylida qolsin; helper/flow alohida faylga faqat funksiya bir nechta testda qayta ishlatilsa yoki haqiqiy umumiy flow bo'lsa chiqariladi.
- Bitta test ichidagi 1 qatorlik wrapper/helper yoki constant-getter funksiyalar yozilmasin; oddiy test data va `f"..."` kabi expressionlar test/run flow boshida local variable bo'lib tursin. Helper faqat takrorlanadigan UI harakati, conditional/retry, download/file validation yoki o'qishni aniq yengillashtiradigan blok uchun ishlatilsin.
- Download tekshiradigan testlar Windows, Linux va macOSda ishlashi kerak: contextlarda `accept_downloads=True` bo'lsin, fayl `download.save_as()` bilan `test-results/downloads/` ichiga OS-safe filename qilib saqlansin, va timeout bo'lsa Allurega URL/error/screenshot diagnostikasi yozilsin.
- Group test cleanup'i faqat shu testcase yaratgan unique recordga tegishli
  bo'lsin; boshqa testlarning oldingi recordlarini umumiy client bo'yicha
  cancel qilish mustaqillikni buzadi.
- Yangi test yozishda u setup bosqichigami yoki qaysi mustaqil groupga tegishli ekanini aniq ajrat.
- `tests/smoke/test_setup/test_0_setup_runner.py` ichidagi testlar umumiy
  baseline hisoblanadi. Yangi entity faqat kamida uchta mustaqil group
  testcasega bir xil ko'rinishda kerakligi tasdiqlansa setupga qo'shiladi;
  feature-specific variantlar testcase Arrange qismida yaratiladi.
- **authorization har test boshida chaqirilmaydi**: setup chain admin logini
  `test_01_legal_person` boshida, user group logini `group_user_page`da bir marta
  bajariladi; keyingi `run_*` funksiyalar page holatini meros qiladi.
- **Yangi test ma'lumotlari**: faqat setup baseline nom/kodlari
  `load_data(...)` yoki `code` orqali olinadi; group testcase boshqa testcase
  saqlagan keyni o'qimaydi va konkret session/company qiymati hardcode
  qilinmaydi.
- Test, funksiya va fayl nomi faqat testning o'zida bajariladigan biznes amalni
  ifodalaydi; boshqa testcase maqsadi nomga qo'shilmaydi. Group papka, marker
  va runner orqali ma'lum bo'lsa, `run_create_contract` va
  `test_create_contract` kabi sodda nom ishlatiladi.
- Order formasidagi `Договор` maydoni contract code emas, contract name bilan
  tanlanadi. Contract testcase-specific bo'lsa aynan shu case Arrange qismida
  yaratiladi; shared baseline bo'lsa setup keydan olinadi.
- Order testlari ko'p yozilishi kutiladi; yangi case avval BasePage va
  tasdiqlangan `flow_order_list`dan foydalanadi. Boshqa order flowi faqat
  yuqoridagi Flow admission gate'dan o'tsa saqlanadi/yaratiladi.
- Test yozish, migratsiya yoki debug paytida xato testcase, noto'g'ri flow, ortiqcha murakkablik yoki dublikat kod ko'rinsa, foydalanuvchiga alohida xabar ber va tavsiya qilingan tuzatishni qisqa tushuntir.
- Contract testlari alohida fayllarda, self-contained yoziladi; Contract add/list/view qadamlari `flow_contract` ga chiqarilmaydi. Har fayl o'z `run_*` va standalone `test_*` funksiyasiga ega bo'ladi.
- Order leaf testlarida page state va assertionlar uchun
  `BasePage.expect_page`, `text`, `grid`, `input`, `b_input`, `form_view`,
  `close_biruni_alert`, `click` va `confirm_biruni` ishlatiladi. Umumiy list
  gateway `flow_order_list`da qoladi; boshqa wizard flowlar faqat Flow
  admission gate'dan o'tsa saqlanadi.
- Contract + `Типы оплат` case'ida `Тип оплаты` orderda auto-fill bo'lishini tekshir; user uni o'zgartirsa ham order ishlashi kerak, faqat contract sum limit tekshiriladi.
- Contract valyutasi order productlarini filterlaydi; boshqa valyutali contractga almashtirilsa, oldin tanlangan productlar o'chishi kutiladi.

### Form-opening smoke suite arxitekturasi
Status: code-confirmed
Verified: 2026-08-05
Source: `tests/smoke/test_forms/form_cases.py`;
`tests/smoke/test_forms/menu_column_runner.py`;
`tests/smoke/test_forms/test_0_forms_runner.py`

- Barcha forma-opening testlar `tests/smoke/test_forms/` ichida saqlanadi.
  `Справочники`, `Склад`, `Продажа` va keyingi har bir navbar tab uchun alohida
  `test_XX_<tab>_menu_forms.py` leaf modul bo'ladi. Mavjud
  `test_02_a2_admin_menu_forms.py` ham `test_life_cycle/`dan shu papkaga ko'chiriladi.
- Har forma oddiy `list[dict]` inventarda turadi. Majburiy minimum:
  `menu_column`, `menu_item`, `path`; kerak bo'lsa `navbar_tab`, `title`,
  `action`, `page_links`, `ready`, `screenshot_mask`, `allowed_warnings`.
  `label` optional va berilmasa `menu_item/action/page_links/add_icon`dan
  avtomatik yaratiladi.
- Pytest itemning stable identifikatori `shell + navbar_tab + menu_column`.
  Mavjud identityga forma qo'shilsa faqat tegishli inventarga bitta dict
  qo'shiladi. Yangi identity bo'lsa leafdagi `*_MENU_TESTS` config listiga
  bitta yangi dict qo'shiladi; coverage validator formasiz yoki testsiz
  identityni import vaqtida bloklaydi. Real `menu_column=None` identityda
  `<ustunsiz>` deb ko'rsatiladi.
- Legacy va A2 lifecycle'lari `menu_column_runner.py`dagi alohida
  `run_legacy_menu_column_forms(...)` va `run_a2_menu_column_forms(...)`
  funksiyalarida turadi; bitta universal mode-dispatcher yozilmaydi.
  `flow.py` faqat navigatsiya/settle primitive'larini, `form_cases.py` case
  normalizatsiyasini, `form_reporting.py` result/schema/reportni saqlaydi.
- Umumiy runner `tests/smoke/test_forms/test_0_forms_runner.py` bo'ladi va har
  composite identityni alohida parametrized sibling pytest item sifatida
  chaqiradi.
  Fayl oddiy `runner.py` emas, `test_0_*_runner.py` patternida nomlanadi, chunki
  smoke collector shu patterndagi runnerlarni avtomatik topadi.
- Har menu identity o'z `FormMonitor` instance'i va filial/auth/shell
  preconditioniga ega; `independent=True` sabab bitta identity failure'i boshqa
  identitylarni skip qilmaydi.
- Yangi runner default/full smoke tarkibiga kirishi uchun
  `tests/smoke/smoke_config.py::full_runner_paths()` va kerak bo'lsa
  `scripts/run_tests.py` target/path mappinglari ham yangilanadi.
- Har tab inventari oddiy `list` + `dict/tuple` bilan deklarativ yoziladi;
  dataclass, classifier yoki katta universal framework qurilmaydi.
- Normal test check/diagnostika argumentlarini yozmaydi — `None` barchasini
  yoqadi. Test darajasida `checks=[]` hard checklarni o'chirib natijani
  `OBSERVED_ONLY` qiladi; `diagnostics=[]` observation signal collectionini
  o'chiradi. Tanlangan nomlar `list[str]` bilan beriladi, per-form override yo'q.

### Ko'p-elementli (batch) smoke testlarda natija hisoboti
- Bitta test ichida ko'plab element ketma-ket tekshirilsa (masalan a2 formalarni navbat bilan ochish), kodni SODDA saqla:
  **NamedTuple/dataclass/type hint ishlatma** (bu loyihada yo'q, user ularni yozmaydi). Formalar ro'yxatini oddiy
  `list` + `tuple` (masalan `(tab, path, name)`) yoki oddiy `dict` bilan ber; natijalarni ham `(filial, path, name, ok, detail)` tuple ro'yxatiga yig'.
- Har elementni bitta aniq nomli **flow/helper chaqiruvi** bilan och (masalan `navigate_to_a2(page, tab, path)`), ochilishni `expect(...)` bilan tasdiqla. Test o'zi qisqa loop bo'lsin, "framework" bo'lmasin (JS `evaluate`, klassifikator, mode-dispatcher yozma — bu tushunarsiz bo'ladi).
- Xatoda to'xtamaslik kerak bo'lsa: har elementni `try/except (AssertionError, PlaywrightTimeoutError)` bilan o'rab natija yig', muammoда screenshot attach qil.
- Yakuniy hisobotni alohida sodda funksiyaga chiqar: filial/guruh bo'yicha `✅`/`⚠` + nom + path qatorlari, tepada `Jami/OK/Muammo`. Ortiqcha bezak (box-drawing ramka va h.k.) SHART EMAS — sodda o'qiladigan matn yetarli.

## 6. Ish tartibi

1. Avval `$ARGUMENTS` bo'yicha kerakli fayllarni o'qi
2. Mavjud o'xshash testni o'rganib shablon chiqar
3. Yangi test yoz
4. Agar bu Selenium migratsiyasi bo'lsa, migrated kodni `for_migratsiya.py` davomiga yoz va runnerga avtomatik qo'shma
5. Oddiy yangi test bo'lsa, runner ga qo'sh
6. Foydalanuvchiga qaysi fayllarga nima qo'shilganini ko'rsat
