# FormMonitor HTTP Diagnostics Package Design

**Date:** 2026-08-10  
**Status:** Approved by user

## Goal

FormMonitor observation diagnostikalaridan faqat HTTP `4xx/5xx` response
diagnostikasini qoldirish. Diagnostika infrasi `form_checks/`ga parallel package
bo'lib, kelajakdagi mustaqil diagnostikalarni FormMonitor'ni tarmoqlantirmasdan
qo'shishga imkon berishi kerak.

## Scope

- `busy`, `resource_errors`, `promise_rejections` va `title_metadata`
  diagnostikalarini capture, evaluation, result schema va human reportdan
  to'liq olib tashlash.
- HTTP `4xx/5xx` response diagnostikasini alohida modulga ajratish.
- `tests/smoke/test_forms/form_diagnostics.py` flat modulini
  `tests/smoke/test_forms/form_diagnostics/` package'iga almashtirish.
- FormMonitor diagnostika lifecycle'ini package public API'si orqali
  boshqarishi.
- Mavjud hard checklar, jumladan title hard-check uchun zarur title state va
  metadata'ga tegmaslik.

## Package Structure

```text
tests/smoke/test_forms/form_diagnostics/
├── __init__.py
├── core.py
└── failed_requests.py
```

### `failed_requests.py`

HTTP response observationining to'liq lifecycle'ini egallaydi:

- Playwright `response` listenerini o'rnatish;
- faqat statusi `400` yoki undan katta response'larni qabul qilish;
- query stringni saqlamasdan `status host/path` labelini yaratish;
- umumiy count va cheklangan sample ro'yxatini yig'ish;
- har forma oldidan state'ni reset qilish;
- joriy forma uchun structured snapshot qaytarish;
- suite yakunida listenerni olib tashlash.

### `core.py`

Diagnostika registry va umumiy konfiguratsiya kontraktini saqlaydi:

- hozirgi yagona nom: `failed_requests`;
- `None` barcha registered diagnostikalarni, `[]` hech birini,
  `list[str]` tanlangan diagnostikalarni yoqadi;
- noma'lum yoki takroriy nomlar validation xatosi beradi;
- kelajakdagi diagnostika alohida modul va registry entry orqali qo'shiladi.

### `__init__.py`

FormMonitor va boshqa consumerlar ishlatadigan kichik public API'ni export
qiladi. Ichki module pathlar public kontrakt hisoblanmaydi.

## FormMonitor Integration

FormMonitor HTTP response logikasini o'zida saqlamaydi. U diagnostika package'i
orqali:

1. suite boshida enabled diagnostikalarni yaratadi va ishga tushiradi;
2. har forma oldidan diagnostika state'ini reset qiladi;
3. forma holati yig'ilganda structured snapshot oladi;
4. `checks.diagnostics` va compatibility `checks.failed_requests` /
   `checks.failed_request_count` maydonlarini to'ldiradi;
5. `finish()`da listenerlarni yopadi.

URL hard gate yiqilib, diagnostika bajarilmasligi kerak bo'lgan holatda
`failed_requests` nested resulti mavjud kontraktdagi kabi `NOT_RUN` va
`blocked_by=url` bo'lib qoladi.

## Reporting And Schema

- `form-monitor.json` schema versioni o'zgarmaydi.
- `config.enabled_diagnostics` va har resultdagi `diagnostics` strukturasi
  saqlanadi; registry'da faqat `failed_requests` bo'ladi.
- Raw HTTP count va cheklangan sample'lar saqlanadi.
- Human reportdagi `BRAUZER NETWORK SIGNALLARI` bo'limi qoladi.
- `/page/tour/` va optional A2 i18n kabi tasdiqlangan request noise bucketlari
  saqlanadi.
- Resource/promise/busy/title-metadata report bo'limlari va flat compatibility
  maydonlari olib tashlanadi.

## Error Handling

- Playwright listener API mavjud bo'lmasa diagnostika formaning hard-check
  natijasini o'zgartirmaydi.
- Noto'g'ri response obyektlari e'tiborsiz qoldiriladi.
- Diagnostika observation-only bo'lib qoladi: HTTP `4xx/5xx` mavjudligi o'zi
  formani fail qilmaydi.

## Verification

Loyiha qoidasiga muvofiq user alohida test run so'ramaganligi sabab pytest yoki
test collection bajarilmaydi va unit test fayllari tahrirlanmaydi. Verification
quyidagilar bilan cheklanadi:

- o'zgargan Python fayllarini syntax parse qilish;
- diagnostika nomlari va olib tashlangan signallar bo'yicha read-only `rg`
  inspection;
- knowledge-base validator;
- `git diff --check`;
- scoped diff review.

## Non-Goals

- HTTP `4xx/5xx`ni hard checkga aylantirish;
- yangi diagnostika signalini qo'shish;
- hard checklar tartibi yoki classification'ni o'zgartirish;
- analyzerning diagnostikaga aloqasiz qismlarini refactor qilish;
- mavjud dirty worktree'dagi aloqasiz user o'zgarishlarini o'zgartirish.
