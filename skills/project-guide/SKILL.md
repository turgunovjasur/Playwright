---
name: project-guide
description: Use when Playwright reposida har qanday vazifani boshlash, loyiha qoidalari ustuvorligini aniqlash, mos skill yoki knowledge ownerini tanlash kerak bo'lsa.
---

# Project Guide

Bu majburiy router: avval shu faylni, keyin task skill/reference'ni o'qi.
Canonical bilim faqat `skills/`da; `.agents/skills/` va `.claude/skills/`
symlink entry-pointlardir.

## Authority

Ko'rsatmalar ziddiyatida yuqoridan pastga:

1. foydalanuvchining joriy aniq buyrug'i;
2. shu `project-guide`dagi loyiha governance qoidalari;
3. tanlangan local task skill;
4. tashqi yoki generic skill.

Tashqi yoki generic verification qoidasi foydalanuvchi bermagan test yozish
yoki test run qilish ruxsatini yaratmaydi. Faktlar ziddiyatida dalil kuchi:
`trace/live UI > code > user-reported > legacy`.

## Ownership Va Routing

- Loyiha governance, precedence, branch, ruxsat va umumiy kontekst:
  `project-guide`; joriy arxitektura uchun
  [project-context.md](references/project-context.md).
- Smartup current truth va domain index: `smartup-guide`; aniq forma —
  `references/forms/<slug>.md`, eski kuzatuv — `references/history.md`.
- Test yozish, test artifacti va unit-test scope'i: `write-test`.
- Takrorlanuvchi UI choreography/helper: `new-flow`.
- Testni ishga tushirish, run log/trace/Allure natijasi: `run-smoke`.
- Kuzatilgan test xatosining root cause'i: `debug-test`.
- Static sifat va barqarorlik review'i: `review-test`.
- Runner, CI, Allure lifecycle va reporting infrasi: `maintain-test-infra`.
- Yangi project factni canonical joyga yozish: `learn`.

Smartup reference ownershipi:

- legacy navigatsiya — `legacy-form-navigation.md`;
- A2 migratsiya — `a2-migrated-forms.md`;
- contract — `contracts.md`; current order flow — `orders.md`;
- settlement coverage — `order-settlement-scenarios.md`;
- shared modal/grid/locator — `ui-patterns.md`;
- runtime/fixture/session/data-store — `testing-debug.md`;
- setup/group topology — `smoke-runner.md`;
- navbar Forms suite — `write-test/references/navbar-form-suite.md`.

## Handofflar

- `write-test` testcase behaviorini, `new-flow` takroriy choreography'ni egallaydi.
- `run-smoke` execution va natija summarysini, `debug-test` failure sababini egallaydi.
- Bitta failure — `debug-test`; subsystem/CI/runner muammosi —
  `maintain-test-infra`.
- Static diff/review — `review-test`; real failure artifacti — `debug-test`.
- `smartup-guide` current truthni o'qitadi; yangi bilimni faqat `learn`
  tartibi bilan yoz.

## Governance

- Savol, taklif yoki `nima deysan?` yozish ruxsati emas. Read-only tahlildan
  so'ng o'zgartirishdan oldin tasdiq ol.
- Foydalanuvchining loyiha haqida aytgan gapi o'z-o'zidan skill yoki
  knowledge-base'ga write-back ruxsati emas. Agent uni durable bilim yoki qoida
  sifatida saqlash kerak deb hisoblasa, avval nima va qaysi canonical ownerga
  yozilishini aytib, foydalanuvchidan aniq tasdiq so'rasin. Faqat tasdiqdan
  keyin `learn` orqali skill yoki reference faylini o'zgartirsin.
- `yoz`, `o'zgartir`, `tuzat`, `amalga oshir`, `qoidaga qo'sh` faqat aytilgan
  scope'ni implement qilishga ruxsat beradi; scope'ni kengaytirma.
- Boshqa branch aniq aytilmasa kod tahriridan oldin branchni tekshir va
  `dev1`da ishlagin.
- Testlarni, collectionni yoki smoke targetni faqat foydalanuvchi aynan
  `run qil` desa ishlat; aks holda handoffda `run qilinmadi` de.
- Secret, token, real credential, email, session code va PII'ni skillga yozma;
  parametrik placeholder ishlat.
- Escalation kerak bo'lsa xavfsiz, qayta ishlatiladigan `prefix_rule` taklif qil.
- Uzun inline Python o'rniga workspace scriptidan foydalan.

## Artifact Lifecycle

- Durable bilim/qoidani faqat `skills/`dagi bitta ownerda saqla.
- `docs/superpowers/{specs,plans}/` va `.superpowers/sdd/` task davomida
  vaqtinchalik. Yakunda foydali qarorni `learn` bilan ko'chir, artifactni
  workspacedan olib tashla; historical knowledge sifatida commit qilma.
- `docs/` faqat user so'ragan human deliverable; AI authority emas.
- `scripts/`da faqat runtimega ulangan yoki reusable kod qolsin. One-off
  probe/debug `/private/tmp` yoki SDD workspace'da yaratiladi va yakunda
  o'chiriladi.
- Cache, snapshot, review diff va agent ledger final validatordan oldin tozalanadi.

## Tasdiqli O'rganish

Foydalanuvchi loyiha UI xatti-harakati, root cause, project pattern yoki oldingi
yechimning noto'g'riligini aniq fakt sifatida bildirsa, agent uni canonical
bilimga nomzod deb taklif qilishi mumkin, lekin avtomatik yozmaydi. Taklifda
yoziladigan fakt va canonical owner ko'rsatiladi; foydalanuvchi aniq
tasdiqlagandan keyingina `learn` ishlatiladi. Savol, gipoteza, rad etilgan
variant, tasdiqlanmagan dizayn, secret yoki vaqtinchalik session qiymati
tasdiq bo'lsa ham durable bilimga yozilmaydi.
