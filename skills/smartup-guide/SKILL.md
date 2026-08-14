---
name: smartup-guide
description: Use when Smartup sahifasi, formasi, biznes qoidasi, UI joylashuvi, contract/order flowi, locator, modal, grid, navigation yoki domain xatti-harakati bilan ishlash kerak bo'lsa.
---

# Smartup Guide

Bu skill Smartup bo'yicha bilimlarni tez topish uchun index vazifasini bajaradi. Batafsil bilimlar `references/` ichida domainlarga bo'lingan.

## Mundarija

- [Qidirish tartibi](#qidirish-tartibi)
- [Ishonchlilik modeli](#ishonchlilik-modeli)
- [Skill chegarasi](#skill-chegarasi)
- [Reference xarita](#reference-xarita)
- [Form dossier ro'yxati](#form-dossier-royxati-toliq)
- [Form dossier qoidasi](#form-dossier-qoidasi)
- [Bilim qo'shish formati](#bilim-qoshish-formati)
- [Tekshirish](#tekshirish)
- [Asosiy eslatma](#asosiy-eslatma)

## Qidirish Tartibi

1. User so'rovidagi domainni aniqlash: contract, order, list/grid, Biruni error, setup/debug.
2. Agar so'rov aniq forma haqida bo'lsa, avval `references/forms/<form-slug>.md` dossier faylini o'qi.
3. Foydalanuvchi formani UI'da qayerdan topishi, qaysi filialda ko'rinishi yoki
   menu/page-link/dropdown yo'lini so'rasa,
   `references/legacy-form-navigation.md`ni o'qi.
4. Forma rasmi kerak bo'lsa, avval shu skill ichidagi `references/forms/screenshots/<form-slug>/` papkasidan ol; `test-results` vaqtinchalik output bo'lgani uchun doimiy bilim manbasi sifatida ishlatilmasin.
5. Keyin kerak bo'lsa quyidagi domain reference fayllardan faqat keraklisini o'qi.
6. Agar kerakli bilim topilmasa, UI/test/trace orqali aniqlab, tegishli form dossier yoki reference faylga qisqa va tagli qilib qo'sh.

## Ishonchlilik Modeli

Dalillarni quyidagi ustuvorlikda ishlat:

1. `trace-confirmed` yoki `live-ui-confirmed`
2. `code-confirmed`
3. `user-reported`
4. To'liq provenance metadatasiz eski entry

- `user-reported` bilimni test/kod o'zgartirish uchun tasdiqlangan fakt sifatida
  ishlatma; avval code, trace yoki live UI bilan tekshir.
- `code-confirmed` UI aynan shunday render bo'lishini emas, faqat joriy kod
  kontraktini tasdiqlaydi.
- `Verified` sanasi eski bo'lsa bilim avtomatik noto'g'ri bo'lmaydi, lekin
  locator, menu, URL va serverga bog'liq xatti-harakatni qayta tekshir.
- `Status`, `Verified`, `Source` to'liq bo'lmagan eski entryni joriy bilimga
  nomzod deb ol, ammo riskli qarordan oldin manbasini qayta tasdiqla.
- `references/history.md` faqat tarixiy kontekst; undagi qoidani current truth
  sifatida ishlatma.
- Qarama-qarshi dalilda eng yangi va yuqori ustuvorlikdagi manbani tanla,
  current reference'ni yangila va almashtirilgan qoidani `history.md`ga ko'chir.

## Skill Chegarasi

`smartup-guide` domain knowledge va dalillar manbasi; u test bajarish workflowini
takrorlamaydi. Avval kerakli dossier/reference'ni o'qi, keyin vazifaga mos skillni
ishlat. Skill nomi harness prefiksisiz yoziladi, chunki `skills/` ikkala
entry-point uchun umumiy manba: chaqirish sintaksisini har bir agent o'zi
qo'llaydi (`skills/<name>/SKILL.md` esa har ikkisida bir xil o'qiladi).
Project bo'ylab authority va routing uchun avval
[project-guide](../project-guide/SKILL.md)ga amal qil.

- yangi test yozish: `write-test`
- reusable UI flow yaratish yoki o'zgartirish: `new-flow`
- failed test diagnostikasi: `debug-test`
- test/smoke run: `run-smoke`
- runner, config yoki reporting infrasi: `maintain-test-infra`
- test/flow/runner review: `review-test`
- tasdiqlangan yangi loyiha bilimini yozish: `learn`

Action skilldagi umumiy workflow bilan bu skilldagi Smartup-specific fakt
qarama-qarshi chiqsa, faktni dalil bilan qayta tekshir; workflow qoidasi va
domain bilimni bir faylda takrorlama.

## Reference Xarita

- Forma dossierlari: [references/forms/](references/forms/)
- Contract va contract shartlari: [references/contracts.md](references/contracts.md)
- Order biznes qoidalari va flowlar: [references/orders.md](references/orders.md)
- Order yopish va client settlement scenario coverage:
  [references/order-settlement-scenarios.md](references/order-settlement-scenarios.md)
- Smoke runner setup zanjiri: [references/smoke-runner.md](references/smoke-runner.md)
- Smartup UI, locator, modal, grid patternlari: [references/ui-patterns.md](references/ui-patterns.md)
- Legacy formalarni foydalanuvchi UI'da topish yo'llari, filial ko'rinishi,
  page-link va dropdown actionlari:
  [references/legacy-form-navigation.md](references/legacy-form-navigation.md)
- A2 (migratsiya qilingan yangi) formalar, A2 menu-tracklari va URL/error
  signallari: [references/a2-migrated-forms.md](references/a2-migrated-forms.md)
- Test setup, debug va screenshot arxivi: [references/testing-debug.md](references/testing-debug.md)
- FormMonitor hard-check kontraktlari:
  [references/form-monitor/](references/form-monitor/)
  - [check_url](references/form-monitor/check-url.md)
  - [check_loader](references/form-monitor/check-loader.md)
  - [check_application_error](references/form-monitor/check-application-error.md)
  - [check_content_ready](references/form-monitor/check-content-ready.md)
  - [check_title](references/form-monitor/check-title.md)
- Superseded qoidalar va tarixiy dalillar: [references/history.md](references/history.md)

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
- [currency-view.md](references/forms/currency-view.md) — Valyuta ko'rish va kurs qo'shish modali
- [room.md](references/forms/room.md) — Рабочая зона yaratish va prikreplenie
- [user.md](references/forms/user.md) — Foydalanuvchi, rol, ruxsatlar, parol
- [legal-person.md](references/forms/legal-person.md) — Yuridik shaxs
- [natural-person.md](references/forms/natural-person.md) — Jismoniy shaxs
- [login.md](references/forms/login.md) — Login sahifasi

Biznes formalar:
- [order-list.md](references/forms/order-list.md) — Order ro'yxati, row selection va action tugmalari
- [order-add.md](references/forms/order-add.md) — Order yaratish
- [client-payment.md](references/forms/client-payment.md) — Client to'lovi yaratish va o'tkazish
- [client-offset.md](references/forms/client-offset.md) — Client qarzi, oldindan to'lov va o'zaro hisob-kitob
- [order-list-view-settings.md](references/forms/order-list-view-settings.md) — Order list table va widget ko'rinishi sozlamalari
- [order-product-list.md](references/forms/order-product-list.md) — Order uchun ommaviy TMC tanlash
- [order-import.md](references/forms/order-import.md) — Excel orqali order TMC importi
- [contract-view.md](references/forms/contract-view.md) — Kontrakt ko'rish
- [company-client.md](references/forms/company-client.md) — Kompaniya OAuth2 klientlari, A2/filial konteksti
- [pnl.md](references/forms/pnl.md) — PnL menyu yo'li va legacy/A2 migratsiya holati
- [init-balance.md](references/forms/init-balance.md) — Boshlang'ich TMC qoldiq hujjati
- [action.md](references/forms/action.md) — Акция (aksiya/chegirma)
- [cislink.md](references/forms/cislink.md) — CIS link integratsiya
- [integration-three.md](references/forms/integration-three.md) — Integration Three hisobotlar
- [integration-reports.md](references/forms/integration-reports.md) — Integratsiya hisobotlari
- [marking-stocktaking-list.md](references/forms/marking-stocktaking-list.md) — Markirovka inventarizatsiyasi ro'yxati va test dostup holati

## Form Dossier Qoidasi

Har bir muhim forma uchun bitta dossier fayl bo'lsin:

```text
references/forms/<form-slug>.md
```

Dossier ichida shu mavzu bo'yicha bir harakatda kerak bo'ladigan ma'lumotlar turadi:

- `Quick Lookup`: form slug, URL pattern va navigation
- `Screenshot Paths`: aniq asset pathlari yoki `N/A`
- `Known Locators`: asosiy locatorlar yoki `N/A`
- `Flow And Tests`: mavjud flow/helper/test fayllari yoki `N/A`
- `Business Rules`: forma bilan bog'liq joriy qoidalar
- `Known Issues`: debug note yoki `N/A`

Yangi dossierda shu olti bo'limni ishlat. Mavjud dossierga tegilganda yetishmagan
bo'limlarni bosqichma-bosqich to'ldir. Buni validator
`dossiers_without_canonical_sections` ratcheti majburlaydi: kanonik bo'limi
yetishmagan dossier soni ko'paysa error beradi, kamaysa esa baseline'ni shu
o'zgarishda pasaytirishni talab qiladi. Screenshotlarni doim
`references/forms/screenshots/<form-slug>/` ichida arxivla va dossierda aniq
filename bilan ko'rsat; faqat papka nomini yozish yetarli emas.

Misol: contract view haqida so'ralganda avval [references/forms/contract-view.md](references/forms/contract-view.md) o'qiladi.

## Bilim Qo'shish Formati

Yangi bilim tegishli faylga quyidagi formatda qo'shilsin:

```markdown
### <qisqa mavzu>
Tags: contract, order, payment-type, grid, error, setup, locator
Status: user-reported | code-confirmed | live-ui-confirmed | trace-confirmed
Verified: YYYY-MM-DD yoki `pending`
Source: user | <fayl:qator> | live UI | <trace/log path>
- Qayerda: <sahifa yoki flow>
- Qoida: <biznes/UI xatti-harakati>
- Testda ishlatish: <qanday assert yoki flow kerak>
```

`Status`, `Verified`, `Source` uchalasi birga yozilsin. Bir entryda bir nechta
dalil bo'lsa eng kuchli statusni tanla, barcha manbalarni `Source`da `;` bilan
ajrat.

## Tekshirish

Knowledge-base o'zgargandan keyin quyidagini ishga tushir:

```bash
./.venv/bin/python skills/smartup-guide/scripts/validate_knowledge_base.py
```

Skill package, cross-skill Markdown link va `.agents/.claude` entrypoint
paritysi ham o'zgargan bo'lsa repo-level validatorni ishlat; u yuqoridagi
Smartup validatorini ham ichidan chaqiradi:

```bash
./.venv/bin/python skills/scripts/validate_skills.py
```

Validator broken Markdown linklar, indexdan tushib qolgan dossierlar, mavjud
bo'lmagan repo pathlari, to'liq bo'lmagan provenance, uzun fayldagi mundarija va
indekslanmagan screenshotlarni tekshiradi. Legacy provenance, JSON sidecar va
kanonik dossier bo'limlari qarzi ratchet bilan nazorat qilinadi: kamayishi
mumkin, lekin yangi o'zgarishda ko'paymasligi kerak. Qarzni kamaytirsang
validator ichidagi baseline'ni ham shu o'zgarishda pasaytir. Errorlarni
tuzatmasdan ishni yakunlama.

## Asosiy Eslatma

- Smartup bo'yicha yangi biznes qoida, UI xatti-harakati, xato sababi yoki locator topilsa, shu skillning mos reference fayliga yoz.
- Legacy formaning navbar/menu/page-link/dropdown yo'li va filial ko'rinishi
  global navigatsiya bilimidir: uni `references/legacy-form-navigation.md`ga
  yoz, forma A2 bo'lmasa `a2-migrated-forms.md`ga qo'shma.
- Reference/dossierlarga **statik/literal test data yozilmaydi**. Qiymatlar
  doim parametrik ko'rinishda yoziladi: `user-pw{code}@<company>`,
  `product-pw{code}`, `room-pw{code}`. Konkret session qiymatlari
  `data_store.json`da turadi, dossierda emas.
- Dublikat kod, noto'g'ri testcase yoki flowga ajratilishi kerak bo'lgan takrorlanish ko'rinsa, foydalanuvchiga alohida xabar ber.
- Current reference fayllarda faqat joriy, tasdiqlangan xatti-harakat tursin.
  Faqat foydalanuvchi aytgan va hali tekshirilmagan bilim `user-reported`
  statusida alohida saqlansin; superseded qoida `references/history.md`ga ko'chirilsin.
- Answer/review-only vazifada yangi bilim topilmasa knowledge-base'ni shunchaki
  suhbat yakuni uchun o'zgartirma. Yangi loyiha bilimi topilsa AGENTS.md va
  `learn` qoidasi bo'yicha yoz.
- Screenshot faqat yangi/o'zgargan visual state tasdiqlanganda va keyingi
  locator/debug ishiga real qiymat qo'shganda arxivlansin. Bir xil state'ning
  dublikat rasmini yaratma; mavjud screenshotni dossierdan link qil.
- Test muvaffaqiyatli ishlasa, o'zgargan testcase qadamlariga tegishli docstring
  va current knowledge bir-biriga zid emasligini tekshir.
