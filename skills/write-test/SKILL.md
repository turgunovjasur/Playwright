---
name: write-test
description: Yangi Playwright + pytest Smartup smoke testi, setup/group/forms leaf testi yoki runner wrapper yozadi va mavjud testni loyiha patterniga moslaydi. Yangi test/test fayl yaratish, Selenium/codegen migratsiyasi yoki testni runnerga qo'shish so'ralganda ishlat.
---

# Yangi Smoke Test Yozish

## Avval o'qish

1. Smartup forma/UI vazifasida `skills/smartup-guide/SKILL.md` va aniq
   `references/forms/<slug>.md` dossierini o'qi.
2. Batafsil loyiha qoidalari uchun
   [references/project-rules.md](references/project-rules.md)dagi faqat
   relevant bo'limni o'qi:
   - oddiy setup/leaf test → `Test fayl shabloni`, `Asosiy qoidalar`;
   - runner/fixture/dependency → `Runnerga qo'shish`, `Loyiha xususiyatlari`;
   - Selenium/codegen → `Selenium migratsiya source fayli`;
   - Forms batch suite → `Form-opening smoke suite arxitekturasi`;
   - group test → `Setup va Group test dependency modeli`.
3. O'xshash amaldagi test, flow va mos page-object API'larini tekshir.

## Majburiy invariantlar

- Leaf test odatda reusable `run_<name>(page, code, ...)` va standalone
  `test_<name>(page, code, ...)` funksiyalaridan iborat.
- Testcase-specific biznes qadamlar `run_*` ichida qoladi; bir nechta testda
  takrorlanadigan UI choreography `tests/smoke/flows/`ga ajratiladi.
- Legacy AngularJS/Biruni formada `BasePage`, A2 Angular formada
  `AngularBasePage` ishlat; ikki DOM kontraktini aralashtirma.
- Mavjud page-object helperi bo'lsa raw locator/local wrapper yozma.
- Har testda `pytestmark`, `@allure.title`, raqamlangan docstring qadamlar va
  mos `allure.step`lar bo'lsin.
- Fixture'ni import qilma. `save_data` faqat downstream consumerga kerak
  bo'lgan qiymat uchun ishlat.
- URL/credential hardcode qilma. Lokal `.env` mavjud bo'lsa u yutadi; aks
  holda runner/pytest CLI va shell env ishlaydi.
- Global `regression`/`scope` mode yo'q; coverage farqini alohida testcase yoki
  target bilan ifodala.
- `time.sleep`, hardcoded timeout va UI holati uchun Python `assert` ishlatma.

## Ish tartibi

1. Test turini aniqlash: setup, group, Forms suite, life-cycle yoki standalone.
2. Test data va downstream dependencylarni belgilash.
3. Mos dossier va mavjud koddan navigation, locator va page-objectni tanlash.
4. `run_*` + `test_*` yoki runner wrapperni yozish.
5. Kerak bo'lsa runner target/path mappinglarini yangilash.
6. Eng tor relevant pytest target bilan tekshirish.
7. Yangi, tasdiqlangan Smartup bilimi topilsa `learn` provenance qoidasi
   bo'yicha current dossier/reference'ni yangilash.
