# FormMonitor `check_loader` Kontrakti

Status: code-confirmed
Verified: 2026-08-11
Source: user; `tests/smoke/test_forms/monitoring/checks/loader.py`; `tests/smoke/test_forms/monitoring/monitor.py`; `tests/smoke/test_forms/monitoring/checks/core.py`; `tests/smoke/test_forms/monitoring/navigation.py`; `tests/smoke/test_forms/monitoring/reporting.py`; `utils/angular_base_page.py`
Contract approval: approved by user
Implementation: implemented

## Mundarija

- [Maqsad](#maqsad)
- [Konseptual interfeys](#konseptual-interfeys)
- [Hard-check tartibi](#hard-check-tartibi)
- [Blocking loader signallari](#blocking-loader-signallari)
- [Asosiy oqim](#asosiy-oqim)
- [Muvaffaqiyat natijasi](#muvaffaqiyat-natijasi)
- [Failure natijasi](#failure-natijasi)
- [Fail-fast qoidasi](#fail-fast-qoidasi)
- [Failure evidence](#failure-evidence)
- [Suite davomiyligi](#suite-davomiyligi)
- [Implementatsiya invariantlari](#implementatsiya-invariantlari)
- [Acceptance misollari](#acceptance-misollari)

## Maqsad

`check_loader` `check_url` muvaffaqiyatli tugagandan keyingi ikkinchi va
majburiy hard check hisoblanadi. U blocking loader belgilangan vaqt ichida
yo'qolishini kutadi. Loader timeout ichida yo'qolmasa, keyingi hard checklar
ishonchli emas deb hisoblanadi va bajarilmaydi.

## Konseptual Interfeys

```python
check_loader(
    page,
    *,
    shell,
    timeout=60_000,
)
```

- `page` — joriy Playwright sahifasi.
- `shell` — `check_url` actual URLdan aniqlagan `legacy` yoki `a2` qiymati.
- `timeout` — blocking loader yo'qolishini kutish vaqti, millisekundlarda.
- Default timeout `60_000 ms`.
- Timeout loader checkning o'z contractida saqlanadi; caller alohida loader
  kutish logikasini takrorlamaydi.

## Hard-check Tartibi

Tasdiqlangan target ketma-ketlik:

```text
check_url
→ check_loader
→ check_application_error
→ check_content_ready
→ check_title
```

`check_loader` faqat `check_url=PASSED` bo'lgandan keyin ishga tushadi.

## Blocking Loader Signallari

Shell asosiy selector tartibini belgilaydi; hybrid sahifani o'tkazib yubormaslik
uchun ikkinchi shell selectori fallback bo'lib qoladi:

```css
legacy: .block-ui-overlay:visible, .smt-skeleton:visible
a2:     .smt-skeleton:visible, .block-ui-overlay:visible
```

`[aria-busy="true"]` blocking loader contractiga kirmaydi. U alohida
observation-only diagnostika bo'lib qoladi va o'zicha formani failed qilmaydi.

## Asosiy Oqim

1. `check_url` expected path actual URL ichida borligini va shell aniqlanganini
   tasdiqlaydi.
2. `check_loader` blocking loaderlarni tekshiradi.
3. Loader ko'rinmasa, check kutmasdan `PASSED/True` qaytaradi.
4. Loader ko'rinsa, check uning yo'qolishini `timeout` davomida kutadi.
5. Loader timeout ichida yo'qolsa, check `PASSED/True` qaytaradi.
6. Loader timeout oxirida ham ko'rinsa, check `FAILED/False` qaytaradi.

Loaderning bir marta paydo bo'lishi failure emas. Failure faqat loader
belgilangan vaqt ichida yo'qolmaganda yuz beradi.

## Muvaffaqiyat Natijasi

Loader yo'q bo'lsa yoki timeout ichida yo'qolsa:

```text
passed: True
execution_status: PASSED
timeout_ms: 60000
visible_loaders: []
```

Shundan keyin `check_application_error`, `check_content_ready` va `title` hard checklari
ishlaydi.

## Failure Natijasi

Loader timeout oxirida ham ko'rinsa:

```text
passed: False
execution_status: FAILED
status: OPENED_WITH_DEFECT
reason_code: LOADER_NOT_FINISHED
timeout_ms: 60000
visible_loaders: [<timeout paytida ko'ringan loader selectorlari>]
```

`OPENED_WITH_DEFECT` ishlatiladi, chunki `check_url` target URLga yetilganini
allaqachon tasdiqlagan, ammo forma blocking loader sabab foydalanishga tayyor
emas.

## Fail-fast Qoidasi

`check_loader=False` bo'lsa, joriy forma uchun keyingi hard checklar
bajarilmaydi:

```text
application_error: NOT_RUN
content_ready: NOT_RUN
title: NOT_RUN
```

Ularning `blocked_by` qiymati `loader` bo'ladi. Loader failure joriy forma
natijasini failed qiladi, lekin butun suite loopini darhol to'xtatmaydi.

## Failure Evidence

Loader timeout bo'lganda, boshqa sahifaga o'tishdan oldin quyidagilar
saqlanishi shart:

```text
actual_url
timeout_ms
visible_loaders
loader_count
```

Shu failure holatining redacted full-page screenshoti olinadi. Log va
screenshot aynan loader timeout tugagan paytdagi joriy formaga bog'lanadi.

## Suite Davomiyligi

Loader failure butun suite'ni darhol to'xtatmaydi:

1. Joriy forma `OPENED_WITH_DEFECT / LOADER_NOT_FINISHED` sifatida yoziladi.
2. Keyingi hard checklar `NOT_RUN` sifatida saqlanadi.
3. Evidence va progress eventi chiqariladi.
4. Forma loopi keyingi planned case'ga o'tadi.
5. Suite oxirida aggregate assertion actionable failure sabab top-level
   pytest testini `FAILED` qiladi.

## Implementatsiya Invariantlari

- Loader kutish va timeout klassifikatsiyasi `check_loader` ichida bo'ladi.
- `shell` majburiy va faqat `legacy` yoki `a2` bo'lishi mumkin.
- Default timeout aynan `60_000 ms` bo'ladi.
- `check_loader` `check_url`dan darhol keyin ishlaydi.
- Forms oqimida navigation helper yoki keyingi hard gate loaderni oldindan
  kutib, alohida `NAVIGATION_FAILED` sifatida klassifikatsiya qilmaydi.
- Forms oqimida loader uchun yagona pass/fail authority `check_loader` bo'ladi.
- `check_loader` caller'i loader timeoutini takroran kutmaydi.
- Loader failure'dan keyingi hard checklar `NOT_RUN` bo'ladi.
- `[aria-busy="true"]` hard loader emas va observation-only bo'lib qoladi.
- Failure screenshot keyingi forma navigatsiyasidan oldin olinadi.

Bu invariantlar faqat Forms monitoring oqimiga tegishli. Boshqa setup/group
testlaridagi umumiy `BasePage.wait_for_loader()` va
`AngularBasePage.wait_for_loader()` helper contractlari o'zgarmaydi.

## Acceptance Misollari

### 1. Loader umuman ko'rinmadi

```text
check_url: PASSED
loader boshida yo'q
check_loader: PASSED
application_error: ishlaydi
```

### 2. Loader ko'rindi va timeout ichida yo'qoldi

```text
check_url: PASSED
loader: visible
loader 60 soniyadan oldin yo'qoldi
check_loader: PASSED
check_content_ready va title: ishlaydi
```

### 3. Loader timeout oxirida ham ko'rindi

```text
check_url: PASSED
loader 60 soniya davomida visible
check_loader: FAILED / LOADER_NOT_FINISHED
application_error: NOT_RUN
content_ready: NOT_RUN
title: NOT_RUN
```

### 4. URL check o'tmadi

```text
check_url: FAILED / EXPECTED_URL_NOT_REACHED
check_loader: NOT_RUN
application_error: NOT_RUN
content_ready: NOT_RUN
title: NOT_RUN
```
