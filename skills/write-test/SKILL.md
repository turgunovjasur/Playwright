---
name: write-test
description: Use when yangi Smartup Playwright/pytest smoke, setup, group, Forms leaf yoki runner wrapper testi yozish, mavjud testni moslash yoxud Selenium/codegen testini migratsiya qilish so'ralsa.
---

# Yangi Smoke Test Yozish

## Skill Chegarasi

Bu skill testcase behaviori, test artifacti va unit-test scope'ini egallaydi.
Bir nechta testda takrorlanadigan UI choreography `new-flow`ga topshiriladi;
test execution va run summary `run-smoke` ownerligida qoladi.

## Avval o'qish

1. Smartup forma/UI vazifasida `skills/smartup-guide/SKILL.md` va aniq
   `references/forms/<slug>.md` dossierini o'qi.
2. Batafsil loyiha qoidalari uchun
   [references/project-rules.md](references/project-rules.md)dagi faqat
   relevant bo'limni o'qi:
   - oddiy setup/leaf test → `Test fayl shabloni`, `Asosiy qoidalar`;
   - runner/fixture/dependency → `Runnerga qo'shish`, `Loyiha xususiyatlari`;
   - Selenium/codegen → `Selenium migratsiya source fayli`;
   - yangi navbar Forms suite → avval
     [references/navbar-form-suite.md](references/navbar-form-suite.md), so'ng
     `Form-opening smoke suite arxitekturasi`;
   - Order regression scope yoki yangi Order testcase →
     [references/order-test-coverage.md](references/order-test-coverage.md);
   - har qanday kod/test o'zgarishi → `Unit test qo'shmaslik va run qilmaslik`;
   - group test → `Group testcase mustaqilligi, flow chegarasi va
     BasePage-first`, so'ng `Setup va Group test execution modeli`.
3. O'xshash amaldagi test, flow va mos page-object API'larini tekshir.

## Majburiy invariantlar

- Leaf test odatda reusable `run_<name>(page, code, ...)` va standalone
  `test_<name>(page, code, ...)` funksiyalaridan iborat.
- Testcase-specific biznes qadamlar `run_*` ichida qoladi; bir nechta testda
  takrorlanadigan UI choreography `tests/smoke/flows/`ga ajratiladi.
- Yangi yoki refactor qilingan har bir group testcase boshqa group testcase
  yaratgan data/state'ga bog'lanmaydi; uning yagona umumiy dependency'si
  tasdiqlangan `user_setup` baseline bo'lishi mumkin.
- Flow testcase'ni yashirmaydi: faqat ko'p test uchun majburiy yoki aynan bir
  xil takrorlanadigan UI choreography flowga chiqariladi. Scenario tayyorlash,
  biznes validation va expected resultlar `run_*` ichida qoladi.
- Legacy AngularJS/Biruni formada `BasePage`, A2 Angular formada
  `AngularBasePage` ishlat; ikki DOM kontraktini aralashtirma.
- Mavjud page-object helperi bo'lsa raw locator/local wrapper yozma.
- Har testda `pytestmark`, `@allure.title`, raqamlangan docstring qadamlar va
  mos `allure.step`lar bo'lsin.
- Har bir yangi page/form/modal ochilishi alohida `with allure.step(...)`
  chegarasida bo'lsin: transition actioni va undan keyingi
  `base.expect_page(heading=...)` bir step ichida turadi; bitta step ichida
  ketma-ket ikki yangi sahifa ochilmaydi.
- Fixture'ni import qilma. `save_data` setup baseline'ni group testlarga
  uzatish yoki tashqi artefakt uchun ishlatiladi; group testcase sibling
  consumer uchun data saqlamaydi.
- URL/credential hardcode qilma. Lokal `.env` mavjud bo'lsa u yutadi; aks
  holda runner/pytest CLI va shell env ishlaydi.
- Global `regression`/`scope` mode yo'q; coverage farqini alohida testcase yoki
  target bilan ifodala.
- User unit testni aynan so'ramasa yangi unit test qo'shma va mavjud unit test
  fixture/expectationlarini o'zgartirma; implementatsiya buyrug'i bunga ruxsat emas.
- `time.sleep`, hardcoded timeout va UI holati uchun Python `assert` ishlatma.

## Ish tartibi

1. Test turini aniqlash: setup, group, Forms suite, life-cycle yoki standalone.
2. Test data, shared setup baseline va testcase ichidagi preconditionlarni
   belgilash; sibling testcase dependency yaratmaslik.
3. Mos dossier va mavjud koddan navigation, locator va page-objectni tanlash.
4. `run_*` + `test_*` yoki runner wrapperni yozish.
5. Kerak bo'lsa runner target/path mappinglarini yangilash.
6. Tekshirishda `run-smoke` skillidagi user-reported execution qoidasiga amal qilish.
7. Yangi, tasdiqlangan Smartup bilimi topilsa `learn` provenance qoidasi
   bo'yicha current dossier/reference'ni yangilash.
