---
name: debug-test
description: Muvaffaqiyatsiz Playwright/pytest testini log, trace va Allure dalillari orqali tahlil qiladi. Test xatosi, timeout, locator, fixture yoki session-state muammosi so'ralganda ishlat; foydalanuvchi faqat sababni so'rasa kodni o'zgartirma, tuzatishni ham so'rasa fix va qayta run qil.
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
| `JSONDecodeError` | `data_store.json` buzilgan | Faylni backup qilib, keyin runner orqali qayta yarat |
| `pytest.exit` | `code` fixture topilmadi | Avval `test_0_setup_runner.py` yoki `run_tests.sh` ishlatilsin |

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
4. Eng tor relevant testni qayta ishga tushir.
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

Yangi, tasdiqlangan Smartup xatti-harakati topilsa `learn` qoidasi bo'yicha mos
dossier/reference'ga provenance bilan yoz. Vaqtinchalik failure, taxmin yoki
konkret session qiymatini doimiy qoida sifatida saqlama.
