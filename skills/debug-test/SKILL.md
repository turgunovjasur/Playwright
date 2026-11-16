---
name: debug-test
description: Use when Smartup Playwright yoki pytest testi xato, timeout, locator, fixture, session-state, log, trace yoki Allure diagnostikasini talab qilsa.
---

# Muvaffaqiyatsiz Testni Debug Qilish

Test: `$ARGUMENTS`

## Skill Chegarasi

Bu skill mavjud failure artifactidan root cause topishni egallaydi. Testni
ishga tushirish yoki run summary — `run-smoke`; runner/CI/reporting subsystemi
muammosi — `maintain-test-infra`; failure bo'lmagan static review —
`review-test`. Faqat diagnostika so'ralgan bo'lsa kodni o'zgartirma.

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
| `AssertionError: ... buzilgan JSON` (`JSONDecodeError` cause) | `data_store.json` buzilgan | Backup qil; qayta yaratish runi faqat aniq so'ralganda |
| `pytest.exit` (`code` fixture) | UI baseline to‘liq emas yoki boshqa muhitga tegishli | Xabardagi sababni va joriy server/company mosligini tekshir. Baseline tayyorlash uchun run ruxsati `run-smoke` bo‘yicha olinadi. |

### 3. Smartup kontekstini o'qi

- Aniq forma bo'lsa avval `skills/smartup-guide/references/forms/<slug>.md` dossierini o'qi.
- Locator/modal/grid muammosi uchun `skills/smartup-guide/references/ui-patterns.md`ni o'qi.
- Fixture, runner va data-store muammosi uchun `skills/smartup-guide/references/testing-debug.md`ni o'qi.
- Dossierdagi tasdiqlangan helper yoki locator mavjud bo'lsa, qayta ixtiro qilma.

### 4. Xavfsiz diagnostika

- Avval read-only tekshiruvlar bilan sababni isbotla.
- Buzilgan `test-results/data/data_store.json`ni darhol o'chirma. Uni
  `data_store.corrupt-<timestamp>.json` nomiga backup qilgandan keyingina runner
  orqali yangi fayl yarat.
- `session_page` yoki group page ishlatilsa oldingi testdan modal, route yoki
  filial state qolganini tekshir.
- Precondition qiymati data-store'da mavjud bo'lsa, muammoga aloqasiz upstream
  entityni qayta yaratma.

### 5. Natija yoki tuzatish

1. Xato sababini dalil bilan ko'rsat.
2. Faqat diagnostika so'ralgan bo'lsa shu yerda to'xta.
3. Tuzatish ham so'ralgan bo'lsa minimal kod o'zgarishini qil.
4. Faqat user aynan `run qil` degan bo'lsa eng tor relevant testni qayta ishga
   tushir; oddiy `tuzat` buyrug'i execution authoritysi emas.
5. Tizim muammosi bo'lsa (server, env, credential, dependency) kodni taxminiy
   o'zgartirma; muammoni aniq ajratib ko'rsat.

## Chiqish formati

```
Xato turi: <TimeoutError / AssertionError / ...>
Joyi: <fayl>:<qator>
Sabab: <nima bo'ldi>
Yechim: <nima qilish kerak>
```

## Bilimni yangilash

Yangi xatti-harakatni dalili va owneri bilan bildir. Bilim bazasiga yozish
tasdiqlangan bo‘lsa [learn](../learn/SKILL.md) orqali saqla.
