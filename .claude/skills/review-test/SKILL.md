---
name: review-test
description: Test kodini senior QA ko'zi bilan review qilish. Sifat, barqarorlik, Allure integratsiyasi, fixture ishlatilishi va anti-patternlarni tekshiradi.
allowed-tools: Read, Glob, Grep
---

# Test Kodni Review Qilish

Fayl: `$ARGUMENTS`

## Review tekshiruv ro'yxati

### 1. Allure integratsiyasi
- [ ] `pytestmark` bilan `epic`, `feature`, `story` belgilangan
- [ ] Har bir test funksiyasida `@allure.title()` bor
- [ ] Muhim qadamlar `with allure.step()` bilan ajratilgan
- [ ] Attach (screenshot, log) kerakli joylarda qo'shilgan

### 2. Fixture ishlatilishi
- [ ] `session_page` session-scoped testlarda, `page` izolyatsiyali testlarda
- [ ] `code` fixture to'g'ri ishlatilgan (import qilinmagan, parametr sifatida kelgan)
- [ ] `save_data` / `load_data` ma'lumot uzatish uchun ishlatilgan
- [ ] `logger` xato loglash uchun to'g'ri ishlatilgan

### 3. Locator sifati
- [ ] `page.locator()` ishlatilgan (`find_element` emas)
- [ ] `expect(locator).to_be_visible()` ishlatilgan (Python `assert` emas)
- [ ] Hard-coded `wait_for_timeout()` ishlatilmagan
- [ ] Locatorlar barqaror (ID, data-testid yoki semantik CSS)

### 4. Test mustaqilligi
- [ ] Test o'z holatini `save_data` orqali saqlaydi
- [ ] Boshqa testlardan to'g'ridan to'g'ri import qilinmagan (faqat flow funksiyalari)
- [ ] Test muvaffaqiyatsiz bo'lganda aniq xato xabari chiqadi

### 5. Anti-patternlar
- [ ] `time.sleep()` yo'q (o'rniga `expect(...).to_be_visible()`)
- [ ] `try/except` bilan xatolar yashirilmagan
- [ ] Hardcoded URL yo'q (`.env` dan o'qiladi)
- [ ] Test ichida biznes logika yo'q (flows papkasida bo'lishi kerak)

## Natija formati

Har bir muammo uchun:
- **Muammo**: nima xato
- **Joyi**: fayl:qator
- **Yechim**: qanday tuzatish kerak

Oxirida umumiy baho: `Yaxshi / O'rta / Qayta ko'rib chiqish kerak`
