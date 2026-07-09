---
name: smartup-guide
description: Smartup ilovasiga xos biznes bilimlar, UI joylashuvlari, contract/order flowlari, locator kuzatuvlari va test yozishda ishlatiladigan domain qoidalari. Smartup sahifalari, formalar, contract, order, payment type, modal, navigation yoki loyiha UI xatti-harakati haqida ishlaganda foydalan.
---

# Smartup Guide

Bu skill Smartup bo'yicha bilimlarni tez topish uchun index vazifasini bajaradi. Batafsil bilimlar `references/` ichida domainlarga bo'lingan.

## Qidirish Tartibi

1. User so'rovidagi domainni aniqlash: contract, order, list/grid, Biruni error, setup/debug.
2. Agar so'rov aniq forma haqida bo'lsa, avval `references/forms/<form-slug>.md` dossier faylini o'qi.
3. Forma rasmi kerak bo'lsa, avval shu skill ichidagi `references/forms/screenshots/<form-slug>/` papkasidan ol; `test-results` vaqtinchalik output bo'lgani uchun doimiy bilim manbasi sifatida ishlatilmasin.
4. Keyin kerak bo'lsa quyidagi domain reference fayllardan faqat keraklisini o'qi.
5. Agar kerakli bilim topilmasa, UI/test/trace orqali aniqlab, tegishli form dossier yoki reference faylga qisqa va tagli qilib qo'sh.

## Reference Xarita

- Forma dossierlari: [references/forms/](references/forms/)
- Contract va contract shartlari: [references/contracts.md](references/contracts.md)
- Order biznes qoidalari va flowlar: [references/orders.md](references/orders.md)
- Smoke runner setup zanjiri: [references/smoke-runner.md](references/smoke-runner.md)
- Smartup UI, locator, modal, grid patternlari: [references/ui-patterns.md](references/ui-patterns.md)
- A2 (migratsiya qilingan yangi) formalar, filial-menyu, URL/error signallari: [references/a2-migrated-forms.md](references/a2-migrated-forms.md)
- Test setup, debug va screenshot arxivi: [references/testing-debug.md](references/testing-debug.md)

## Form Dossier Ro'yxati (to'liq)

Setup formalar:
- [company.md](references/forms/company.md) — Company yaratish, shablonlar, security sozlama
- [license.md](references/forms/license.md) — Litsenziya sotib olish va foydalanuvchiga ulash
- [filial.md](references/forms/filial.md) — Filial yaratish
- [sector.md](references/forms/sector.md) — Наборы ТМЦ yaratish
- [product.md](references/forms/product.md) — ТМЦ yaratish va narx belgilash
- [robot.md](references/forms/robot.md) — Штат (xodim) yaratish
- [payment-type.md](references/forms/payment-type.md) — Типы оплат ulash
- [price-type.md](references/forms/price-type.md) — Narx turi yaratish
- [room.md](references/forms/room.md) — Рабочая зона yaratish va prikreplenie
- [user.md](references/forms/user.md) — Foydalanuvchi, rol, ruxsatlar, parol
- [legal-person.md](references/forms/legal-person.md) — Yuridik shaxs
- [natural-person.md](references/forms/natural-person.md) — Jismoniy shaxs
- [login.md](references/forms/login.md) — Login sahifasi

Biznes formalar:
- [order-add.md](references/forms/order-add.md) — Order yaratish
- [contract-view.md](references/forms/contract-view.md) — Kontrakt ko'rish
- [init-balance.md](references/forms/init-balance.md) — Boshlang'ich TMC qoldiq hujjati
- [action.md](references/forms/action.md) — Акция (aksiya/chegirma)
- [cislink.md](references/forms/cislink.md) — CIS link integratsiya
- [integration-three.md](references/forms/integration-three.md) — Integration Three hisobotlar
- [integration-reports.md](references/forms/integration-reports.md) — Integratsiya hisobotlari

## Form Dossier Qoidasi

Har bir muhim forma uchun bitta dossier fayl bo'lsin:

```text
references/forms/<form-slug>.md
```

Dossier ichida shu mavzu bo'yicha bir harakatda kerak bo'ladigan ma'lumotlar turadi:

- URL pattern va navigation
- screenshot pathlari; forma screenshotlari doim `references/forms/screenshots/<form-slug>/` ichida arxivlanadi
- visual regression uchun baseline/current screenshot state nomlari va metadata
- asosiy locatorlar
- ishlatiladigan flow/helper/test fayllari
- related business rules
- known issues/debug notes

Misol: contract view haqida so'ralganda avval [references/forms/contract-view.md](references/forms/contract-view.md) o'qiladi.

## Bilim Qo'shish Formati

Yangi bilim tegishli faylga quyidagi formatda qo'shilsin:

```markdown
### <qisqa mavzu>
Tags: contract, order, payment-type, grid, error, setup, locator
- <qayerda>: <sahifa yoki flow>
- <qoida>: <biznes/UI xatti-harakati>
- <testda ishlatish>: <qanday assert yoki flow kerak>
```

## Asosiy Eslatma

- Smartup bo'yicha yangi biznes qoida, UI xatti-harakati, xato sababi yoki locator topilsa, shu skillning mos reference fayliga yoz.
- Reference/dossierlarga **statik/literal test data yozilmaydi** (masalan `user-pw5963@autotest`, `product-pw5963`, `room-pw5963`, `autotest`). Bunday qiymatlar doim `code`'dan derive bo'ladigan ko'rinishda yoziladi: `user-pw{code}@<company>`, `product-pw{code}`, `room-pw{code}`. Konkret session qiymatlari `data_store.json` da turadi, dossierda emas.
- Dublikat kod, noto'g'ri testcase yoki flowga ajratilishi kerak bo'lgan takrorlanish ko'rinsa, foydalanuvchiga alohida xabar ber.
- **MAJBURIY — suhbat tugamasdan:** Har bir Smartup/test vazifasi yakunida quyidagilar bajarilishi shart:
  1. O'rganilgan biznes/UI bilimlar, locatorlar, tasdiqlangan flowlar → mos form dossier yoki reference faylga yoz.
  2. Yangi yoki o'zgargan forma uchun **screenshot arxivlanishi shart** (`references/forms/screenshots/<slug>/` ga) — matn yozish yetarli emas.
  3. Test muvaffaqiyatli ishlasa → test docstring + skills ma'lumoti sinxron bo'lsin.
  - Agar suhbat oxirida bu bajarilmagan bo'lsa, foydalanuvchi so'ramasdan ham "Skills yangilanmadi — hozir yangilaymizmi?" deb so'ra.
