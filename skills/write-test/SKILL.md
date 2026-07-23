---
name: write-test
description: Yangi Playwright + pytest smoke test yozish. Foydalanuvchi yangi test, test funksiya yoki test fayl yaratmoqchi bo'lganda ishlatiladi.
---

# Yangi Test Yozish

Quyidagi qoidalarga qat'iy rioya qil:

## 1. Loyiha strukturasini tushun

- Testlar: `tests/smoke/test_setup/` yoki `tests/smoke/test_life_cycle/`
- Flowlar: `tests/smoke/flows/`
- User setup runner: `tests/smoke/test_setup/test_setup_runner.py`
- Group runnerlar: `tests/smoke/test_groups/test_<X>_grup/test_<x>_group_runner.py`
- Full/groups targetlari: `scripts/run_tests.py` ichidagi runner fayllari ro'yxati
- Fixtures: `tests/smoke/conftest.py`

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
        page.get_by_role("button", name="Создать").click()
        base.expect_page(heading="<Create heading>")
        base.input(label="Код", value=entity_code)
        base.input(label="Название", value=entity_name)
        base.checkbox(label="Статус", expect_checked=True)

    with allure.step("3 - Saqlash va ro'yxatda tekshirish"):
        page.get_by_role("button", name="Сохранить", exact=True).first.click()
        base.expect_page(heading="<Ro'yxat heading>")
        base.grid(entity_name, entity_code, "Активный")

    # Downstream testlarga kerak bo'lsa (oxirgi step):
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
- **Maksimal base funksiya**: `base = BasePage(page)` qilib olinadi va `base.navigate_to/expect_page/save_and_expect_heading/switch_filial/text/form_view/input/b_input/multiselect/checkbox/grid_controller/grid/confirm_biruni/confirm_biruni_if_visible/close_biruni_alert/wait_for_loader` ishlatiladi. Raw `page.get_by_role/locator` faqat mos base funksiya yo'q joyda (masalan maxsus tab/dropdown/upload tugmasi). Grid qatorini bosish kerak bo'lsa alohida wrapper emas, `base.grid(..., click=True)` ishlatiladi.
- **allure.step raqamlari docstring qadamlari bilan mantiqan mos** kelsin; step nomi qisqa va professional.
- **Test data** — `run_` boshida lokal `f"...{code}"` o'zgaruvchilar; downstream testga kerak bo'lsa oxirgi stepda `save_data(...)`.
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

## 3. Qoidalar

- **Fixtures** — conftest.py dan keladi, import qilma:
  - `page` — yakka test uchun fresh page; `session_page` — setup chain; `group_user_page` — group chain (login qilingan)
  - `code` — 6 xonali unikal son; `save_data` / `load_data` / `require_data` — data_store; `logger`
- **Allure**: har bir test `@allure.title()` va `with allure.step()` bilan bo'lishi SHART
- **Locator**: `page.locator()` ishlatilsin, `page.find_element()` EMAS
- **Assert**: `expect(locator).to_be_visible()` ishlatilsin, Python `assert` EMAS
- **Project helper first**: sahifa ochilishi, heading, save natijasi, grid row, form input, checkbox/switch, b-input/multiselect va loader kutish uchun avval mavjud loyiha helperlarini ishlat (`base.expect_page(...)`, `base.save_and_expect_heading(...)`, `base.grid(...)`, `base.input(...)`, `base.checkbox(...)`, `base.wait_for_loader(...)`). `utils/base_page.py` ichida mos method bor bo'lsa raw `page.locator(...)`, raw `page.get_by_role(...)` yoki yangi local helper yozilmaydi; raw `expect(...)` faqat mos helper yo'q bo'lsa yoki yangi reusable helper yozishdan oldin lokal tekshiruv uchun ishlatiladi.
- **b-input API bir xilligi**: single-select uchun `base.b_input(label=..., value=..., expect_value=..., return_value=...)`, multi-select uchun ham shu uslubdagi `base.multiselect(label=..., value=..., expect_value=..., return_value=..., clear=...)` ishlatiladi. Auto-selected chipni tekshirish uchun `expect_value`, tanlash uchun `value` beriladi.
- **BasePage scope**: `utils/base_page.py` ga hamma yoki ko'p testlar ishlatadigan umumiy UI primitive'lar yoziladi. Faqat bitta testga kerak bo'lgan biznes/helper logika test faylida `_helper_name(...)` local helper bo'lib qoladi.
- **Navigation wrapper ishlatilmaydi**: `navigate_to`, `expect_page`, `switch_filial` flow helper sifatida import qilinmaydi; test/flow ichida `base = BasePage(page)` qilib, to'g'ridan-to'g'ri `base.navigate_to(...)`, `base.expect_page(...)`, `base.switch_filial(...)` ishlatiladi.
- **Page ready check**: `base.expect_page(..., heading=...)` heading visible bo'lishi bilan birga Smartup loader (`.block-ui-overlay:visible`) yo'qolganini ham kutadi. Loader yo'q bo'lsa 2 sekund kutmaydi; darhol davom etadi. Bu route/page state check uchun yetarli; lekin keyingi action aynan grid/form ichki async reloadga bog'liq bo'lsa `base.wait_for_loader()` alohida qoladi.
- **Timeout**: DEFAULT_TIMEOUT (10s) yetarli; kerak bo'lsa `page.wait_for_timeout()` emas, `expect(...).to_be_visible()` kutish
- **Session data**: `save_data("key", value)` va `load_data("key")` orqali ma'lumot almashing
- **`code`**: har bir test uchun unikal identifikator, nom sifatida ishlating

## 4. Runner ga qo'shish

Yangi user setup testi yozilgandan keyin `tests/smoke/test_setup/test_setup_runner.py` ga import va `@allure.title` bilan qo'sh:

```python
from tests.smoke.test_setup.test_<nomi> import test_<nomi> as run_<nomi>

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

### `expect_page` heading scope
- Heading aniq konteyner ichida tekshirilishi kerak bo'lsa `base.expect_page(heading=..., root="<selector>")` ishlat; `root` berilmasa heading butun sahifadan qidiriladi, loader esa har ikki holatda global tekshiriladi.

### `grid` holatini tekshirish
- Grid holati bo'yicha branch qilish uchun `base.grid(is_empty=True, root="<grid selector>")` ishlat; u bo'sh grid uchun `True`, ma'lumotli grid uchun `False` qaytaradi. Eski assertion-semantikadagi `empty=True` ishlatilmaydi.
- Ma'lum grid qatori mavjudligi bo'yicha branch qilish uchun raw `.tbl-row.filter(...).is_visible()` yozma; `base.grid("row text", is_visible=True, root="<grid selector>")` ishlat. Qator ko'rinsa `True`, topilmasa `False` qaytaradi.

### authorization (rolga qarab login)
- Yagona funksiya: `authorization(page, *, who="admin"|"user"|"head", code=None)`. `who` majburiy keyword-only parametr: har bir chaqiruv login rolini ochiq yozishi shart. **Eski `authorization_user` OLIB TASHLANGAN — ishlatma.**
- `who="user"` → `user-pw{code}@{company}` + `USER_PASSWORD`/`USER_PASS`. Avvalgi `authorization_user(page, code)` o'rniga `authorization(page, who="user", code=code)` yoz.
- `who="admin"` → `ADMIN_EMAIL`/`admin@{company}` + `ADMIN_PASSWORD`/`COMPANY_PASSWORD`.
- `who="head"` → `HEAD_ADMIN_EMAIL`/`HEAD_ADMIN_PASSWORD` (company yaratish uchun).
- `authorization` code generatsiya qilmaydi va `data_store.json`dan code o'qimaydi; `who="user"` uchun `code=code` majburiy. Yangi/eski code tanlovining yagona source'i `NEW_CODE` boshqaradigan `code` fixture.
- `authorization(...)` oxirida `dashboard(page)` orqali `Trade` heading ko'rinishini o'zi tekshiradi; undan keyin `expect(... "Trade" ...).to_be_visible()` ni qayta yozma.
- Credentiallar tashqaridan uzatilmaydi; `authorization` ularni faqat `who` qiymatiga qarab o'zi tanlaydi.
- Credentiallar `.env` dan olinadi (precedence: `.env` yutadi — `conftest._option_or_env`).

### Selenium migratsiya source fayli
- Foydalanuvchi Selenium test kodini rootdagi `for_migratsiya.py` fayliga qo'yadi; migratsiya so'ralganda shu fayldan o'qib Playwright + pytest smoke testga o'tkaz, UI da run qilib xatolarini tuzat.
- Migratsiya qilingan Playwright kodni ham `for_migratsiya.py` faylining davomiga yoz; runnerga yoki test flowga avtomatik qo'shma, foydalanuvchi tekshirib o'zi ko'chiradi.
- Migratsiyada foydalanuvchi `run_tests.sh` oldin run qilinganini aytsa, user setup tayyor deb hisobla; user bilan login qil va `code` qiymatini `test-results/data/data_store.json` dan ol.
- Agar foydalanuvchi Playwright codegen pytest kodini bersa, Seleniumdan taxminiy migratsiya qilma; codegen kodini asos qilib olib loyiha fixture, Allure step, `code`, `authorization(who="user", code=code)`, helper flow va locator patternlariga moslab ber.
- Codegen kodini moslashda har bir ochilgan sahifa, forma yoki view uchun `expect(...)` bilan ochilganini tasdiqla; mavjud login/navbar flowlari bo'lsa, codegen qatorlari o'rniga o'shalarni ishlat.
- Codegen `page.goto("https://...")` kabi hardcode to'liq URL yozadi; bularni hech qachon kodda qoldirma. Conftest `--url` ni `os.environ["COMPANY_URL"]` ga yozadi va `tests/smoke/flows/flow_authorization.company_url()` shuni o'qiydi. Har bir hardcode URL ni `f"{company_url()}/login.html"`, `f"{company_url()}/a2/biruni/md/company_list"` kabi global URL ga bog'la (path qismi qoladi, domen `company_url()` dan keladi). `company_url` ni `flow_authorization` dan import qil.
- Umumiy test ma'lumotlarini ajratish uchun random ishlatma, `code` fixture qiymatini ishlat; bu test boshida generatsiya bo'ladi va butun sessiya davomida saqlanadi.
- `code` fixture umumiy entity nomlari va testlarni ajratish uchun ishlatiladi; agar formaning o'z `code`/`number` maydoni keyingi testlarda kerak bo'lsa, alohida `contract_code_{random_son}` kabi qiymat generatsiya qil, listda aynan shu qiymat bilan hozir yaratilgan recordni top, test muvaffaqiyatli tugaganda `save_data` orqali `data_store.json` ga saqla.
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
- Natural Person alohida entity flow/test hisoblanadi; Legal Person regressionda director natural person kerak bo'lsa Natural Person helperini import qilib ishlatadi, natural person locator/fill/assert logikasini Legal Person ichida dublikat qilmaydi.

### Setup va Group test dependency modeli
- Group runner faylida har bir case alohida pytest test sifatida yig'iladi va `pytest.mark.smoke_group("A")` kabi decorator/marker bilan o'z groupiga biriktiriladi; group caselari full run ichida bitta chain-testga birlashtirilmaydi.
- Runner wrapperda ko'rinadigan test nomining yagona source'i `@allure.title(...)`; wrapper faqat tegishli `run_*` funksiyani chaqiradi. Telegram progress eventlari `conftest.py` hooklaridan title/marker/path orqali avtomatik chiqadi, test body ichida `progress_step` yoki takroriy title yozilmaydi.
- Group runnerdagi thin wrapper signature va uning `run_*` chaqiruvi argumentlari uzun bo'lsa ham bitta qatorda yoziladi; fixture/argumentlar alohida qatorlarga bo'linmaydi.
- Yangi testlar har doim yangi server/baza holatida ham ishlashi kerak; lokal debugda oldingi rerunlardan data ko'paygan bo'lsa ham, testni mavjud dataga suyanib yozma.
- Fresh bazada feature settinglar default o'chirilgan bo'lishi mumkin; testga kerak bo'lgan settingni mavjud holatga suyanmay, idempotent tarzda yoqib/sozlab keyin asosiy flowga o't.
- User setup testlari bir-biriga bog'liq: oldingi setup test keyingi setup test uchun kerakli ma'lumot yoki entity yaratadi; setup ichida test yiqilsa keyingi setup test yura olmasligi mumkin.
- User setup testlari muvaffaqiyatli o'tgandan keyin group testlar boshlanadi: masalan `A group`, `B group` va boshqa guruhlar.
- Har bir group test user setup natijalariga bog'liq, lekin boshqa group testlarga bog'liq emas.
- Bir group ichida test yiqilsa, shu groupning qolgan testlari skip qilinadi; keyingi group testlari esa run bo'lishda davom etadi.
- Group testlar boshqa group yaratgan data yoki statega suyanmasin; A failed bo'lsa ham B, C, D... group testlari user_setup natijalaridan mustaqil run bo'lishi kerak.
- Har bir group ichki dependency uchun o'z data_store key prefixidan foydalansin (`a_group_*`, `b_group_*`, `c_group_*`), boshqa group prefixlarini o'qimasin.
- Group runnerlar `tests/smoke/test_groups/test_<X>_grup/test_<x>_group_runner.py` ko'rinishida bo'lsin; group ichidagi tartib wrapper test nomlari orqali `X-01`, `X-02` tarzida aniq berilsin.
- Har yangi group runner qo'shilganda `scripts/run_tests.py` ichidagi `GROUP_RUNNER_PATHS` ro'yxatiga va `tests/smoke/conftest.py` default runner tanloviga qo'shilsin.
- Full run `test_setup_runner.py`, keyin A/B/C/Report group runner fayllarini shu tartibda bitta pytest sessiyasida collect qiladi; alohida `test_all_runner.py` outer-chain fayli ishlatilmaydi.
- Mexanizm pytest hook/marker orqali bo'lsin: `pytest.mark.user_setup` setup chain uchun, `pytest.mark.smoke_group("A")` kabi markerlar group chain uchun ishlatiladi.
- Bitta group testi failed bo'lsa faqat shu groupning keyingi testlari skip qilinadi, boshqa group markerlari skip qilinmaydi; user_setup failed bo'lsa barcha group testlar skip qilinadi.
- Grouplar bir-birining browser/page holatini meros qilib olmasin: har bir group runner modul-scoped `group_session_page` oladi; user grouplari `group_user_page` bilan bitta login/page'ni bo'lishadi.
- Group ichidagi `run_*` funksiyalari `login` parametrini qabul qilmaydi. User grouplarida loginni `group_user_page` fixture bir marta bajaradi; fresh `page` ishlatadigan standalone pytest wrapper esa `run_*` dan oldin `authorization(...)` qiladi. Admin rolidan boshlanishi testning o'z preconditioni bo'lgan B-04/Report caselari `authorization(who="admin")` ni parametrsiz va ochiq bajaradi.
- B-group leaf testlari alohida, tartib raqamisiz fayllarda turadi: `test_create_order_with_consignment_limit.py`, `test_edit_order_with_consignment_limit.py`, `test_order_invoice_reports.py`, `test_invoice_report_template.py`. Tartib raqami faqat `test_b_group_runner.py` wrapper nomi/title'ida (`B-01`...`B-04`) beriladi. Umumiy order logikasi `order_helpers.py` ichidagi `run_*` funksiyalarda saqlanadi; `run_*` nomida `b_group` takrorlanmaydi.
- Bitta testga xos local yordamchi funksiyalar shu test faylida qolsin; helper/flow alohida faylga faqat funksiya bir nechta testda qayta ishlatilsa yoki haqiqiy umumiy flow bo'lsa chiqariladi.
- Bitta test ichidagi 1 qatorlik wrapper/helper yoki constant-getter funksiyalar yozilmasin; oddiy test data va `f"..."` kabi expressionlar test/run flow boshida local variable bo'lib tursin. Helper faqat takrorlanadigan UI harakati, conditional/retry, download/file validation yoki o'qishni aniq yengillashtiradigan blok uchun ishlatilsin.
- Download tekshiradigan testlar Windows, Linux va macOSda ishlashi kerak: contextlarda `accept_downloads=True` bo'lsin, fayl `download.save_as()` bilan `test-results/downloads/` ichiga OS-safe filename qilib saqlansin, va timeout bo'lsa Allurega URL/error/screenshot diagnostikasi yozilsin.
- Group test ichida cleanup yoki oldingi recordlarni cancel qilish faqat optional bo'lsin: data topilmasa no-op bo'lib, test yangi record yaratib davom etishi kerak.
- Yangi test yozishda u setup bosqichigami yoki qaysi mustaqil groupga tegishli ekanini aniq ajrat.
- `tests/smoke/test_setup/test_setup_runner.py` ichidagi mavjud barcha testlar user setup testlari hisoblanadi; runner setup testlari bilan bir papkada turadi va ular yozib bo'lingan.
- **user_setup yakunlangan**: `tests/smoke/test_setup/` ga YANGI test QO'SHILMAYDI. Yangi testlar `tests/smoke/test_life_cycle/` yoki yangi group (`tests/smoke/test_groups/test_<X>_grup/`) ichida yoziladi.
- **authorization har test boshida chaqirilmaydi**: setup chain admin logini
  `test_01_legal_person` boshida, user group logini `group_user_page`da bir marta
  bajariladi; keyingi `run_*` funksiyalar page holatini meros qiladi.
- **Yangi test ma'lumotlari `data_store.json` dan olinadi**: setup yaratgan entity nom/kodlari `load_data(...)` yoki `code` fixture orqali olinadi; test ichiga literal qiymat (`autotest`, `product-pw5963` kabi) hardcode qilinmaydi.
- A-groupning birinchi testi UZS contract yaratadi; order yaratish uning keyingi downstream testdagi maqsadi bo'lsa ham, test nomiga `order` qo'shilmaydi.
- A-group testlari `tests/smoke/test_groups/test_A_grup/` papkasiga yozib boriladi; contract testlari alohida `test_create_contract.py` va `test_create_contract_with_payment_type.py` fayllarida saqlanadi.
- Group leaf test fayllariga tartib raqami yozilmaydi; `A-01`, `A-02` kabi tartib faqat group runner wrapper nomi va Allure title'da beriladi.
- Test, funksiya va fayl nomi faqat testning o'zida bajariladigan biznes amalni ifodalaydi; downstream maqsad nomga qo'shilmaydi. A-group papka, marker va runner orqali ma'lum bo'lsa, `run_create_contract` va `test_create_contract` kabi sodda nom ishlatiladi. Downstream dependency uchun `a_group_*` data keylari o'zgartirilmaydi.
- A-group contract testida `a_group_contract_code` bilan birga `a_group_contract_name` ham `data_store.json` ga saqlanadi; order formasidagi `Договор` maydoni contract code emas, contract name bilan tanlanadi.
- Order testlari ko'p yozilishi kutiladi; yangi order case yozishda avval `tests/smoke/flows/flow_order/` ichidagi mavjud flowlardan foydalan, takrorlanadigan order harakatlari paydo bo'lsa ularni test ichida qoldirmay alohida order flowga ajrat.
- Test yozish, migratsiya yoki debug paytida xato testcase, noto'g'ri flow, ortiqcha murakkablik yoki dublikat kod ko'rinsa, foydalanuvchiga alohida xabar ber va tavsiya qilingan tuzatishni qisqa tushuntir.
- A-group Contract A-01 va A-02 testlari alohida fayllarda, self-contained yoziladi; Contract add/list/view qadamlari `flow_contract` ga chiqarilmaydi. Har fayl o'z `run_*` va standalone `test_*` funksiyasiga ega bo'ladi.
- A-group order A-03/A-04/A-05 caselari ham bittadan raqamsiz leaf faylda saqlanadi: `test_contract_limit_validation_and_valid_order.py`, `test_order_uses_contract_payment_type.py`, `test_edit_order_and_save_as_new.py`. Eski ko'p-testli `test_order.py` ishlatilmaydi; tartib faqat runnerda beriladi.
- A-group order leaf testlarida page state va assertionlar uchun `BasePage.expect_page`, `text`, `grid`, `input`, `b_input`, `form_view`, `close_biruni_alert` va `save_and_expect_heading` ishlatiladi; maxsus wizard/list harakatlari mavjud `flow_order` funksiyalarida qoladi.
- Contract + `Типы оплат` case'ida `Тип оплаты` orderda auto-fill bo'lishini tekshir; user uni o'zgartirsa ham order ishlashi kerak, faqat contract sum limit tekshiriladi.
- Contract valyutasi order productlarini filterlaydi; boshqa valyutali contractga almashtirilsa, oldin tanlangan productlar o'chishi kutiladi.

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
