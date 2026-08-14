---
name: review-test
description: Use when Smartup Playwright/pytest testi, runneri yoki reusable flowi sifat, barqarorlik, Allure, fixture, page-object, dependency yoxud anti-pattern bo'yicha review qilinishi kerak bo'lsa.
---

# Test Kodni Review Qilish

Fayl: `$ARGUMENTS`

## Skill Chegarasi

Bu skill kod/diffning static sifat review'ini egallaydi va o'z-o'zidan fix
ruxsati bermaydi. Real log, trace yoki failed run root cause'i kerak bo'lsa
`debug-test`; testni ishga tushirish kerak bo'lsa `run-smoke`ga handoff qil.

## Review tekshiruv ro'yxati

### 1. Allure integratsiyasi
- [ ] `pytestmark` bilan `epic`, `feature`, `story` belgilangan
- [ ] Har bir test funksiyasida `@allure.title()` bor
- [ ] Muhim qadamlar `with allure.step()` bilan ajratilgan
- [ ] Attach (screenshot, log) kerakli joylarda qo'shilgan

### 2. Artefakt turini aniqlash

- Leaf test: testcase-specific `run_*` + standalone `test_*`.
- Runner: leaf `run_*` funksiyalarini tartibli sibling pytest testlar sifatida chaqiradi.
- Reusable flow/helper: bir nechta testda ishlatiladigan UI choreography.

Bir turga tegishli qoidani boshqa turga xato sifatida qo'llama.

### 3. Fixture ishlatilishi
- [ ] `session_page` session-scoped testlarda, `page` izolyatsiyali testlarda
- [ ] `code` fixture to'g'ri ishlatilgan (import qilinmagan, parametr sifatida kelgan)
- [ ] `save_data` faqat downstream consumer bo'lsa ishlatilgan; kerak bo'lmagan
  test majburan data-store'ga yozmaydi
- [ ] Downstream qiymat `load_data`/`require_data` orqali olinadi
- [ ] `logger` xato loglash uchun to'g'ri ishlatilgan

### 4. BasePage-first (majburiy)
- [ ] Legacy AngularJS/Biruni formada `utils.base_page.BasePage`, yangi A2 Angular
  formada `utils.angular_base_page.AngularBasePage` ishlatilgan; ikki DOM
  kontraktining helperlari aralashtirilmagan
- [ ] UI primitive uchun mos page-object metodi avval ishlatilgan:
  `expect_page`, `grid`, `grid_cell`, `grid_controller`, `text`, `form_view`,
  `input`, `select`/`b_input`, `switch`/`checkbox`, `confirm_biruni`,
  `confirm_biruni_if_visible`, `close_biruni_alert`, `wait_for_loader`
- [ ] Mos page-object metodi mavjud bo'lsa raw `page.locator()`,
  `page.get_by_role()` yoki local wrapper ishlatilmagan; raw locator faqat helper
  mavjud bo'lmagan UI harakati uchun qolgan

### 5. Locator sifati
- [ ] `page.locator()` ishlatilgan (`find_element` emas)
- [ ] `expect(locator).to_be_visible()` ishlatilgan (Python `assert` emas)
- [ ] Hard-coded `wait_for_timeout()` ishlatilmagan
- [ ] Locatorlar barqaror (ID, data-testid yoki semantik CSS)

### 6. Test va runner dependency
- [ ] Leaf test boshqa leaf testning pytest wrapperini import qilmaydi
- [ ] Runner tegishli leaf `run_*` funksiyalarini import qilishi mumkin
- [ ] Reusable UI ketma-ketligi flow/helper orqali ulashiladi
- [ ] Test boshqa groupning page state yoki data prefixiga suyanmaydi
- [ ] Test muvaffaqiyatsiz bo'lganda aniq xato xabari chiqadi

### 7. Anti-patternlar
- [ ] `time.sleep()` yo'q (o'rniga `expect(...).to_be_visible()`)
- [ ] `try/except` bilan xatolar yashirilmagan
- [ ] Hardcoded URL/credential yo'q; lokal `.env` mavjud bo'lsa undan, aks
  holda runner/pytest CLI yoki shell env'dan olinadi
- [ ] Testcase-specific biznes qadamlar `run_*` ichida; faqat bir nechta testda
  takrorlanadigan UI choreography flow/helperga ajratilgan
- [ ] Dublikat test qadamlari yoki takrorlanadigan UI flowlar aniqlansa, ularni flow/helperga ajratish bo'yicha foydalanuvchiga xabar berilgan
- [ ] Testcase noto'g'ri, ortiqcha yoki biznes flowga mos kelmasa, muammo alohida ko'rsatilgan

## Natija formati

Har bir muammo uchun:
- **Muammo**: nima xato
- **Joyi**: fayl:qator
- **Yechim**: qanday tuzatish kerak

Oxirida umumiy baho: `Yaxshi / O'rta / Qayta ko'rib chiqish kerak`

## Loyiha Xususiyatlari

### Smoke run isolation
- Setup/group smoke flowlarda har bir `run_*` o'z ro'yxat sahifasiga defensive `navigate_to(...)` qilishi kerak; session/page holatini oldingi qadamdan meros olish flaky dependency hisoblanadi.

### Dalilga asoslangan review
- Muammo sifatida faqat ko'rilgan kod, test natijasi yoki tegishli Smartup dossierida tasdiqlangan holatni yoz; boshqa testdan olingan taxminni fakt sifatida kiritma.

### Legacy va A2 Angular page-object chegarasi
- Hozirgi `BasePage` legacy formalar uchun aktual saqlanadi; A2 formalar
  `AngularBasePage` bilan yoziladi. Yangi Angular selectorni legacy metodga
  fallback sifatida qo'shib, bitta helper ichida ikki DOMni aralashtirma.

### Forms runner hisoboti
- Menu orqali forma ochadigan batch testlarda Allure va terminal hisobotining
  har bir qatori filial, navbar tab, menu ustuni, tekshirilgan forma, kutilgan
  URL va haqiqiy URLni ko'rsatishi shart; pass summary pytest capture
  tugagach `pytest_terminal_summary` orqali chiqariladi.
