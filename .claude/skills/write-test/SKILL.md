---
name: write-test
description: Yangi Playwright + pytest smoke test yozish. Foydalanuvchi yangi test, test funksiya yoki test fayl yaratmoqchi bo'lganda ishlatiladi.
---

# Yangi Test Yozish

Quyidagi qoidalarga qat'iy rioya qil:

## 1. Loyiha strukturasini tushun

- Testlar: `tests/smoke/test_setup/` yoki `tests/smoke/test_life_cycle/`
- Flowlar: `tests/smoke/flows/`
- Runner: `tests/smoke/test_smoke_runner.py`
- Fixtures: `tests/smoke/conftest.py`

## 2. Test fayl shabloni

```python
import allure
from playwright.sync_api import Page

pytestmark = [allure.epic("Smoke"), allure.feature("<Feature nomi>"), allure.story("<Story nomi>")]

@allure.title("<Test nomi>")
def test_<nomi>(session_page: Page, code: str, save_data, load_data, logger):
    with allure.step("1 - <Qadam nomi>"):
        # amal
        pass
    with allure.step("2 - <Qadam nomi>"):
        # assert
        pass
```

## 3. Qoidalar

- **Fixtures**: `session_page`, `code`, `save_data`, `load_data`, `logger` — conftest.py dan keladi, import qilma
- **Allure**: har bir test `@allure.title()` va `with allure.step()` bilan bo'lishi SHART
- **Locator**: `page.locator()` ishlatilsin, `page.find_element()` EMAS
- **Assert**: `expect(locator).to_be_visible()` ishlatilsin, Python `assert` EMAS
- **Timeout**: DEFAULT_TIMEOUT (10s) yetarli; kerak bo'lsa `page.wait_for_timeout()` emas, `expect(...).to_be_visible()` kutish
- **Session data**: `save_data("key", value)` va `load_data("key")` orqali ma'lumot almashing
- **`code`**: har bir test uchun unikal identifikator, nom sifatida ishlating

## 4. Runner ga qo'shish

Yangi test yozilgandan keyin `test_smoke_runner.py` ga import va `@allure.title` bilan qo'sh:

```python
from tests.smoke.test_setup.test_<nomi> import test_<nomi> as run_<nomi>

@allure.title("XX - <Nomi>")
def test_XX_<nomi>(session_page: Page, code):
    run_<nomi>(session_page, code)
```

## 5. Loyiha Xususiyatlari

### .env va dinamik qiymatlar
- `.env` da Python f-string **ishlamaydi**: `TEST_USER_EMAIL=f"user-pw{code}@autotest"` — xato
- Dinamik email va shunga o'xshash qiymatlar test/flow ichida f-string bilan quriladi:
  ```python
  user_email = f"user-pw{code}{COMPANY_CODE}"
  ```

### code fixture
- `test_smoke_runner.py` orqali ishlaganda: yangi `random.randint(1000, 9999)` yaratadi
- Yakka test ishlaganda: `test-results/data/data_store.json` dan `"code"` kalitini o'qiydi
- Agar `data_store.json` bo'lmasa: `pytest.exit()` bilan aniq xato beradi

### authorization_user
- `authorization_user(page, code)` — `code` parametrni qabul qiladi
- Email ichida quriladi: `f"user-pw{code}{COMPANY_CODE}"`

## 6. Ish tartibi

1. Avval `$ARGUMENTS` bo'yicha kerakli fayllarni o'qi
2. Mavjud o'xshash testni o'rganib shablon chiqar
3. Yangi test yoz
4. Runner ga qo'sh
5. Foydalanuvchiga qaysi fayllarga nima qo'shilganini ko'rsat
