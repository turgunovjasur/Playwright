# FormMonitor `check_url` Kontrakti

Status: code-confirmed
Verified: 2026-08-11
Source: user; `tests/smoke/test_forms/monitoring/checks/url.py`; `tests/smoke/test_forms/monitoring/monitor.py`; `tests/smoke/test_forms/monitoring/checks/core.py`; `tests/smoke/test_forms/monitoring/reporting.py`
Implementation: implemented

## Mundarija

- [Maqsad](#maqsad)
- [Konseptual interfeys](#konseptual-interfeys)
- [URL ichida path mavjudligi](#url-ichida-path-mavjudligi)
- [Asosiy oqim](#asosiy-oqim)
- [Muvaffaqiyat natijasi](#muvaffaqiyat-natijasi)
- [Yagona failure natijasi](#yagona-failure-natijasi)
- [Fail-fast qoidasi](#fail-fast-qoidasi)
- [Failure evidence tartibi](#failure-evidence-tartibi)
- [Direct URL diagnostikasi](#direct-url-diagnostikasi)
- [Direct probe o'chirilgan holat](#direct-probe-ochirilgan-holat)
- [Suite davomiyligi](#suite-davomiyligi)
- [Implementatsiya invariantlari](#implementatsiya-invariantlari)
- [Acceptance misollari](#acceptance-misollari)

## Maqsad

`check_url` menu orqali forma navigatsiyasidan keyingi birinchi va majburiy
hard check hisoblanadi. U belgilangan timeout ichida inventory `path`i actual
URL ichida borligini tekshiradi va shu URLdan destination shellni aniqlaydi.
URL check muvaffaqiyatsiz bo'lsa, shu forma uchun qolgan hard checklar
bajarilmaydi.

Bu kontrakt `FormMonitor`ning joriy URL gate xatti-harakatini belgilaydi.

## Konseptual Interfeys

```python
check_url(
    page,
    expected_path,
    *,
    timeout=15_000,
    try_direct_url=True,
)
# returns: (check_result, "legacy" | "a2" | None)
```

- `page` — joriy Playwright sahifasi.
- `expected_path` — forma definitionidagi inventory path.
- `timeout` — expected path ochilishini kutish vaqti, millisekundlarda.
- `try_direct_url` — menu navigatsiyasi muvaffaqiyatsiz bo'lsa direct URL
  diagnostikasini yoqadi.
- `previous_url` kontraktga kirmaydi, saqlanmaydi va klassifikatsiyada
  ishlatilmaydi.

## URL Ichida Path Mavjudligi

Browser URLidagi host, legacy token, hash va shell prefiksi inventory pathga
qo'shilmaydi. To'liq URL tengligi talab qilinmaydi.

Misol:

```text
Browser URL:
https://smartup.online/#/!<token>/anor/mr/product/inventory_list

Canonical path:
anor/mr/product/inventory_list
```

Check quyidagi substring qoidasi bilan o'tadi:

```text
expected_path in page.url
```

Masalan `trade/tvt/auto_gen_visit_plan` pathi
`https://smartup.online/#/!<token>/trade/tvt/auto_gen_visit_plan` URLi ichida
borligi yetarli.

Path topilgach shell ham shu actual URLdan bir marta aniqlanadi:

```text
/a2/              → a2
#/!<token>/...    → legacy
aks holda         → None / SHELL_NOT_DETECTED
```

## Asosiy Oqim

1. Menu item/action/page-link navigatsiyasi bajariladi.
2. `check_url` birinchi hard check sifatida ishga tushadi.
3. `check_url` `timeout` davomida expected path actual URL ichida paydo
   bo'lishini kutadi.
4. Path topilgach actual URLdan destination shell aniqlanadi.
5. Path bor va shell aniqlangan bo'lsa URL check `PASSED/True` bo'ladi.
6. Aniqlangan shell keyingi hard checklarga parametr sifatida uzatiladi.

Keyingi hard checklar tartibi alohida kontraktlarda belgilanadi. Amaldagi
ketma-ketlik:

```text
check_url
→ check_loader
→ check_application_error
→ check_content_ready
→ check_title
```

Target loader contracti:
[check-loader.md](check-loader.md).

## Muvaffaqiyat Natijasi

Expected path timeout ichida actual URLda topilsa va shell aniqlansa:

```text
passed: True
expected_url: <expected_path>
actual_url: <page.url>
timeout_ms: <timeout>
detected_shell: <faqat ichki return qiymati>
```

Shundan keyin qolgan hard checklar ishlaydi.

## Yagona Failure Natijasi

Expected path timeout ichida actual URLda topilmasa:

```text
passed: False
status: NOT_OPENED
reason_code: EXPECTED_URL_NOT_REACHED
```

`URL_MISMATCH` va `URL_TIMEOUT` alohida reason sifatida ishlatilmaydi.
Oldingi URL yoki URL transition tarixi saqlanmaydi.

Path topilib, actual URLdan shell aniqlanmasa:

```text
passed: False
status: NOT_OPENED
reason_code: SHELL_NOT_DETECTED
```

Failure logida kamida quyidagilar bo'lishi shart:

```text
expected_url
actual_url
timeout_ms
```

## Fail-Fast Qoidasi

`check_url=False` bo'lsa, joriy forma uchun qolgan hard checklar
bajarilmaydi:

```text
loader: NOT_RUN
application_error: NOT_RUN
content_ready: NOT_RUN
title: NOT_RUN
```

Bu holatda faqat failure evidence va yoqilgan direct URL diagnostikasi
bajariladi.

## Failure Evidence Tartibi

Direct navigatsiya joriy sahifani almashtirishidan oldin birlamchi evidence
saqlanishi shart:

1. Menu navigatsiyasidan keyingi expected va actual URL logga yoziladi.
2. Menu navigatsiyasi failure holatining redacted full-page screenshoti olinadi.
3. Shundan keyingina, yoqilgan bo'lsa, direct URL diagnostikasi boshlanadi.

## Direct URL Diagnostikasi

`try_direct_url=True` bo'lsa, URL check failure'dan keyin expected path actual
URLdan aniqlangan shellga mos direct URL orqali ochib ko'riladi. Shell
aniqlanmasa direct URL qurilmaydi.

Konseptual route:

```text
Legacy: <company-url>/#/!<token>/<expected-path>
A2:     <company-url>/a2/<expected-path>
```

Direct probe ham timeout ichida expected path actual URL ichida paydo bo'lishini
tekshiradi.
U original menu URL check natijasini o'zgartirmaydi: direct URL ochilsa ham
`check_url=False` va forma `NOT_OPENED` bo'lib qoladi.

### Direct URL ochilsa

Hisobot xulosasi:

```text
Forma route'da mavjud, lekin menu navigatsiyasi target route'ga olib bormadi.
```

Structured diagnostika:

```text
direct_probe_enabled: True
direct_expected_url: <constructed direct URL>
direct_actual_url: <page.url>
direct_url_reached: True
```

Direct ochilgan holatning ikkinchi redacted screenshoti olinadi. Direct ochilgan
forma ustida qolgan hard checklar ishlamaydi.

### Direct URL ham ochilmasa

Hisobot xulosasi:

```text
Expected forma menu va direct URL orqali ham ochilmadi.
```

Structured diagnostika:

```text
direct_probe_enabled: True
direct_expected_url: <constructed direct URL>
direct_actual_url: <page.url>
direct_url_reached: False
```

Direct urinishdan keyingi ikkinchi redacted screenshot olinadi.

Ikkala direct probe natijasida ham asosiy reason code o'zgarmaydi:

```text
EXPECTED_URL_NOT_REACHED
```

## Direct Probe O'chirilgan Holat

`try_direct_url=False` bo'lsa:

- birlamchi URL failure logi va screenshoti saqlanadi;
- direct navigatsiya bajarilmaydi;
- `direct_probe_enabled=False` hisobotga yoziladi;
- forma `NOT_OPENED / EXPECTED_URL_NOT_REACHED` bo'lib qoladi.

## Suite Davomiyligi

URL failure butun suite'ni darhol to'xtatmaydi:

1. Joriy forma `NOT_OPENED` sifatida monitor natijasiga yoziladi.
2. Evidence va progress eventi saqlanadi.
3. Forma loopi keyingi planned case'ga o'tadi.
4. Suite oxirida `FormMonitor.finish()` actionable failure borligi sabab
   top-level pytest testini aggregate assertion bilan `FAILED` qiladi.

## Implementatsiya Invariantlari

- URL kutish `check_url` kontrakti ichida bo'ladi.
- `run_case()` URL check uchun `previous_url` saqlamaydi.
- Keyingi browser-aware gate'lar URL'ni takroran kutmaydi yoki
  klassifikatsiya qilmaydi.
- URL check boshqa hard checklardan oldin alohida gate bo'ladi.
- URL failure'dan keyingi hard checklar `NOT_RUN` sifatida report qilinadi.
- Destination shell inventory/case'dan emas, actual URLdan aniqlanadi.
- Shell reportga yangi success maydoni sifatida qo'shilmaydi; `check_url`
  uni `FormMonitor`ga ichki return qiymati bilan beradi.
- Direct probe diagnostika bo'lib, original menu failure'ni passga aylantirmaydi.
- Birlamchi screenshot direct navigatsiyadan oldin olinadi.
- URL failure uchun faqat `EXPECTED_URL_NOT_REACHED` reason code ishlatiladi.

## Acceptance Misollari

### Menu orqali expected URL ochildi

```text
expected_path: anor/mr/product/inventory_list
actual_path: anor/mr/product/inventory_list
result: PASSED
next_checks: RUN
```

### Menu orqali expected URL ochilmadi, direct URL ochildi

```text
result: NOT_OPENED
reason_code: EXPECTED_URL_NOT_REACHED
next_checks: NOT_RUN
direct_url_reached: True
screenshots: 2
```

### Menu va direct URL orqali expected URL ochilmadi

```text
result: NOT_OPENED
reason_code: EXPECTED_URL_NOT_REACHED
next_checks: NOT_RUN
direct_url_reached: False
screenshots: 2
```

### Direct probe o'chirilgan

```text
result: NOT_OPENED
reason_code: EXPECTED_URL_NOT_REACHED
next_checks: NOT_RUN
direct_probe_enabled: False
screenshots: 1
```
