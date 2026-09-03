---
name: learn
description: Use when foydalanuvchi Smartup UI xatti-harakati, xato sababi, loyiha test qoidasi yoki oldingi yechim haqidagi faktni canonical skillga yozishni aniq tasdiqlasa.
---

# Yangi Bilimni Canonical Skillga Qo'shish

Argument: `$ARGUMENTS` (o'rganilgan narsa tavsifi)

Bu skill yangi project factni `skills/` ichidagi yagona ownerga xavfsiz yozadi.
Savol, gipoteza, rad etilgan variant, tasdiqlanmagan dizayn, secret/PII yoki
vaqtinchalik session qiymatini yozma.

## Write-back Tasdig'i

- Foydalanuvchining fakt, qoida, tuzatish yoki e'tiroz aytishi write-back
  ruxsati emas.
- Yozishdan oldin agent saqlamoqchi bo'lgan faktni va tanlangan canonical
  ownerni foydalanuvchiga aytib, aniq tasdiq so'raydi.
- Faqat foydalanuvchi shu write-backni tasdiqlagandan keyin quyidagi algoritm
  bajariladi. Tasdiq bo'lmasa skill yoki knowledge-base fayli o'zgartirilmaydi.
- Foydalanuvchining joriy aniq `skillga yoz`, `qoidaga qo'sh` yoki unga teng
  buyrug'i aynan aytilgan scope uchun tasdiq hisoblanadi.

## Algoritm

1. **Approval:** joriy suhbatda aynan shu write-back uchun foydalanuvchi
   tasdig'i borligini tekshir; yo'q bo'lsa yozishni boshlama.
2. **Atomize:** xabarni bittadan tekshiriladigan, loyihaga xos faktlarga ajrat.
3. **Sanitize:** password, token, email, credential, session code va real company
   qiymatini olib tashla; `<company_code>` kabi placeholder ishlat.
4. **Evidence:** har faktga eng kuchli mavjud statusni qo'y:
   - `user-reported` — faqat foydalanuvchi aytgan;
   - `code-confirmed` — amaldagi kod tasdiqlagan;
   - `live-ui-confirmed` — real UI tasdiqlagan;
   - `trace-confirmed` — trace/log tasdiqlagan.
5. **Owner:** [project-guide](../project-guide/SKILL.md#ownership-va-routing)
   xaritasidan bitta canonical owner tanla.
6. **Search:** tanlangan current owner va `smartup-guide/references/history.md`
   ichidan semantik duplicate yoki conflictni qidir.
7. **Outcome:** quyidagi qaror jadvaliga amal qil.
8. **Validate:** har qanday yozuvdan keyin
   `./.venv/bin/python skills/scripts/validate_skills.py`ni ishlat.
9. **Report:** owner fayl, evidence status, outcome va validator natijasini ayt.

## Qaror Jadvali

- Bir xil fakt allaqachon bor → **no write**; kuchliroq mavjud dalilni
  pasaytirma.
- Bir xil fakt uchun kuchliroq yangi dalil bor → mavjud entryning status,
  verified va source qiymatini yangila.
- Yangi, conflictsiz fakt → canonical ownerga bitta entry qo'sh.
- Kuchliroq dalil current factni inkor qiladi → eski entryni `history.md`ga
  `Superseded by <new fact/source>` bilan ko'chir, keyin yangi current entry yoz.
- Dalil kuchi teng yoki conflict noaniq → yozma; foydalanuvchidan aniqlik so'ra.
- Owner topilmasa → avtomatik yangi skill yaratma; yangi owner/skillni taklif qil.

`user-reported` faktni confirmed current truth sifatida ko'rsatma. U owner
faylning `User-reported` bo'limida yoki aniq pending status bilan turadi.

## Owner Misollari

- Aniq forma UI/business/locator →
  `smartup-guide/references/forms/<form-slug>.md`.
- Contract → `contracts.md`; order → `orders.md`; settlement coverage →
  `order-settlement-scenarios.md`.
- Shared modal/grid/locator → `ui-patterns.md`; runtime/fixture/data-store →
  `testing-debug.md`; setup/group topology → `smoke-runner.md`.
- Test authoring/unit-test artifact → `write-test`; repeated choreography →
  `new-flow`; execution → `run-smoke`; observed failure → `debug-test`;
  infra → `maintain-test-infra`; static review → `review-test`.
- Governance/precedence/branch/ruxsat/current project context → `project-guide`.
- Superseded Smartup fact → `smartup-guide/references/history.md`.

## Entry Formati

```markdown
### <mavzu>
Status: user-reported | code-confirmed | live-ui-confirmed | trace-confirmed
Verified: YYYY-MM-DD | pending
Source: user | <fayl:qator> | live UI | <trace/log path>
- Qoida: <bitta qisqa va aniq project fact>
```

Forma screenshoti dalil bo'lsa uni
`smartup-guide/references/forms/screenshots/<slug>/`da arxivla va dossierdan
havola qil.
