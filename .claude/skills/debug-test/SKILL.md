---
name: debug-test
description: Muvaffaqiyatsiz testni tahlil qilib sabab topish va tuzatish. Test xatosi, timeout, locator muammolari haqida so'ralganda ishlatiladi.
allowed-tools: Read, Glob, Grep, Bash
---

# Muvaffaqiyatsiz Testni Debug Qilish

Test: `$ARGUMENTS`

## Tahlil tartibi

### 1. Log va trace fayllarni o'qi
```
test-results/logs/          — xato loglari
test-results/traces/        — Playwright trace (.zip)
test-results/allure-results/ — Allure natijalar
```

Avval `test-results/logs/` dagi tegishli log faylni o'qi.

### 2. Xato turini aniqlash

| Xato | Sabab | Yechim |
|------|-------|--------|
| `TimeoutError` | Element ko'rinmayapti | Locator tekshir, sahifa yuklangan-yuklangani |
| `StrictModeViolation` | Bir nechta element topildi | Locator aniqroq qil |
| `ElementNotFound` | Element yo'q | Page state tekshir, flow tartibini ko'r |
| `AssertionError` | Qiymat mos kelmayapti | Kutilgan vs haqiqiy qiymatni solishtir |
| `JSONDecodeError` | data_store.json buzilgan | Faylni o'chirib qayta run qil |
| `pytest.exit` | `code` fixture topilmadi | Avval `test_smoke_runner.py` ishlatilsin |

### 3. Locator muammolari

Locator ishlayotganini tekshirish uchun Playwright konsolda:
```js
document.querySelectorAll('<selector>')
```

Yaxshi locator tartibi:
1. `data-testid` atributi (eng ishonchli)
2. `role` + `name` kombinatsiyasi
3. Matn orqali: `page.get_by_text()`
4. CSS selektor (oxirgi chora)

### 4. Session state muammolari

`session_page` ishlatilganda testlar ketma-ket ishlaydi. Agar oldingi test muvaffaqiyatsiz bo'lsa:
- `data_store.json` ni tekshir
- `code` fixture qiymati to'g'ri saqlanganmi

### 5. Tuzatish

1. Xato sababini aniq ko'rsat
2. Tuzatilgan kodni ko'rsat (faqat zarur qator)
3. Qayta test ishga tushirish buyrug'ini ber
4. Agar tizim muammosi bo'lsa (server, env) — foydalanuvchiga ayт

## Chiqish formati

```
Xato turi: <TimeoutError / AssertionError / ...>
Joyi: <fayl>:<qator>
Sabab: <nima bo'ldi>
Yechim: <nima qilish kerak>
```

## Loyiha Xususiyatlari

### #biruniConfirm modal (Bootstrap fade animatsiyasi)
- `да` tugmani bosishdan **oldin** modal opacity `1` bo'lishini kutish shart, aks holda click register bo'lmaydi:
  ```python
  page.wait_for_function("window.getComputedStyle(document.querySelector('#biruniConfirm')).opacity === '1'")
  page.locator("#biruniConfirm").get_by_role("button", name="да").click()
  page.locator("#biruniConfirm").wait_for(state="hidden")
  ```
- `да` bosilgandan keyin modal **darhol** yopiladi, keyin loader (`wait_for_loader`) ishlaydi — `wait_for(state="hidden")` uchun uzun timeout kerak emas
- `да` tugmani har doim `#biruniConfirm` ga scope qilish kerak — `page.get_by_role("button", name="да")` butun sahifada qidiradi va animatsiya davomida noto'g'ri elementni bosishi mumkin

### session_page va domino effekti
- `session_page` barcha testlar uchun umumiy — bitta test fail bo'lib modal qolsa, keyingi barcha testlar ham fail bo'ladi
- `--maxfail=3` pytest.ini da sozlangan — 3 fail dan keyin sessiya to'xtatiladi

### to_contain_text() da exact parametri yo'q
- `expect(locator).to_contain_text("text", exact=True)` — **xato**, bu parametr mavjud emas
- To'liq mos kelish uchun `to_have_text("text")` ishlatiladi
