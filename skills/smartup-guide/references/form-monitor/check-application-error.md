# FormMonitor `check_application_error` Kontrakti

Status: code-confirmed
Verified: 2026-08-11
Source: user; `tests/smoke/test_forms/monitoring/checks/application_error.py`;
`tests/smoke/test_forms/monitoring/monitor.py`;
`tests/smoke/test_forms/monitoring/checks/core.py`;
`tests/smoke/test_forms/monitoring/reporting.py`;
`tests/smoke/test_forms/monitoring/diagnostics/core.py`
Contract approval: approved by user
Implementation: implemented

## Mundarija

- [Maqsad](#maqsad)
- [Konseptual interfeys](#konseptual-interfeys)
- [Hard-check tartibi](#hard-check-tartibi)
- [Hard error signallari](#hard-error-signallari)
- [Asosiy oqim](#asosiy-oqim)
- [Muvaffaqiyat natijasi](#muvaffaqiyat-natijasi)
- [Failure natijasi](#failure-natijasi)
- [Fail-fast qoidasi](#fail-fast-qoidasi)
- [Failure evidence va cleanup](#failure-evidence-va-cleanup)
- [Suite davomiyligi](#suite-davomiyligi)
- [Implementatsiya invariantlari](#implementatsiya-invariantlari)
- [Acceptance misollari](#acceptance-misollari)

## Maqsad

`check_application_error` `check_url` va `check_loader` muvaffaqiyatli
tugagandan keyingi uchinchi majburiy hard check hisoblanadi. U forma ochilishida
ko'rinadigan aniq Biruni, A2 yoki inline error komponentini belgilangan vaqt
ichida qidiradi. Hard error topilsa, keyingi readiness checklari ishonchli emas
deb hisoblanadi va bajarilmaydi.

## Konseptual Interfeys

```python
check_application_error(page, *, shell, timeout=1_200)
```

- `page` — joriy Playwright sahifasi.
- `shell` — `check_url` actual URLdan aniqlagan `legacy` yoki `a2` qiymati.
- `timeout` — hard error ko'rinishini kuzatish vaqti, millisekundlarda.
- Default timeout `1_200 ms`.
- Bu checkda timeout tugashi failure emas: error ko'rinmasa check `PASSED`.
- Errorni kutish, selectorni aniqlash va matnni olish shu check ichida bo'ladi;
  caller yoki `capture_form_state()` bu kutishni takrorlamaydi.

## Hard-check Tartibi

```text
check_url
→ check_loader
→ check_application_error
→ check_content_ready
→ check_title
```

`check_application_error` faqat URL va loader gate'lari `PASSED` bo'lgandan
keyin ishlaydi.

## Hard Error Signallari

Legacy rejimida:

```css
#biruniAlertExtended:visible
#biruniAlert:visible
.alert-danger:visible
```

A2 rejimida:

```css
.alert-danger:visible
[role="dialog"]:visible [data-testid*="error" i]
```

Ustuvorlik yuqoridagi tartibda. Bir nechta signal ko'rinsa, birinchi aniq
selector va uning matni natijaga yoziladi.

Umumiy `[role="alert"]:visible` hard error selectoriga kirmaydi: bu role
warning yoki oddiy axborot uchun ham ishlatilishi mumkin. JavaScript exception,
resource error va promise rejection ham application-error hard checkiga
kirmaydi.

## Asosiy Oqim

1. URL va loader gate'lari muvaffaqiyatli tugaydi.
2. Hard error selectorlari bitta birlashtirilgan locator orqali `timeout`
   davomida kuzatiladi.
3. Hech bir hard error ko'rinmasa, check `PASSED/True` qaytaradi.
4. Hard error ko'rinsa, uning aniq selectori va normalized matni olinadi.
5. Ko'rinadigan hard error elementi matni bo'sh bo'lsa ham failure hisoblanadi.
6. Error topilganda check darhol `FAILED/False` qaytaradi.

## Muvaffaqiyat Natijasi

```text
passed: True
execution_status: PASSED
timeout_ms: 1200
matched_selector: ""
error_text: ""
```

Shundan keyin `check_content_ready` va `title` hard checklari ishlaydi.

## Failure Natijasi

```text
passed: False
execution_status: FAILED
status: OPENED_WITH_DEFECT
reason_code: APPLICATION_ERROR
timeout_ms: 1200
matched_selector: <topilgan hard-error selectori>
error_text: <UI xato matni yoki bo'sh matn belgisi>
actual_url: <joriy browser URLi>
```

`OPENED_WITH_DEFECT` ishlatiladi, chunki target URL ochilgan va loader tugagan,
ammo sahifa aniq application error ko'rsatmoqda.

## Fail-fast Qoidasi

`check_application_error=False` bo'lsa:

```text
content_ready: NOT_RUN
title: NOT_RUN
blocked_by: application_error
```

`check_content_ready()` va `check_title()` browser kutishlari application-error
gate'dan oldin ishlamaydi.

## Failure Evidence Va Cleanup

Hard error topilganda boshqa UI amali bajarilishidan oldin quyidagilar
saqlanadi:

```text
actual_url
timeout_ms
matched_selector
error_text
```

1. Avval aynan failure holatining redacted full-page screenshoti olinadi.
2. Shundan keyin faqat `#biruniAlert` yoki `#biruniAlertExtended` uchun modalni
   `button.close` orqali yopishga urinish mumkin.
3. A2 va inline error elementlari avtomatik o'zgartirilmaydi.
4. Cleanup natijasi quyidagi maydonlarda saqlanadi:

```text
modal_cleanup_attempted
modal_cleanup_succeeded
modal_cleanup_error
```

Cleanup failure original `APPLICATION_ERROR` klassifikatsiyasini
o'zgartirmaydi va screenshotdan oldin bajarilmaydi.

## Suite Davomiyligi

1. Joriy forma `OPENED_WITH_DEFECT / APPLICATION_ERROR` sifatida yoziladi.
2. `content_ready` va `title` `NOT_RUN` bo'ladi.
3. Screenshot va cleanup natijasi hisobotga yoziladi.
4. Forma loopi keyingi planned case'ga o'tadi.
5. Suite oxiridagi aggregate assertion top-level pytest testini `FAILED`
   qiladi.

## Implementatsiya Invariantlari

- Default timeout aynan `1_200 ms`.
- Hard selectorlar shellga mos contractdagi aniq signallardan tanlanadi.
- `shell` majburiy va faqat `legacy` yoki `a2` bo'lishi mumkin.
- `[role="alert"]` o'zicha hard failure emas.
- Visible hard error matni bo'sh bo'lsa ham failure.
- `allowed_warnings` hard-error exceptioni ishlatilmaydi; hard error
  yashirilmaydi.
- `capture_form_state()` errorni kutmaydi va application-error checkini
  takrorlamaydi.
- Failure screenshot Biruni modal cleanupidan oldin olinadi.
- Faqat Biruni modali cleanup qilinadi; A2/inline elementga click qilinmaydi.
- Cleanup xatosi original failure reasonini almashtirmaydi.
- Application-error failure'dan keyingi hard checklar `NOT_RUN`.
- Pytest/browser run faqat user aynan `run qil` deganda bajariladi.

## Acceptance Misollari

### 1. Error ko'rinmadi

```text
check_url: PASSED
check_loader: PASSED
1200 ms ichida hard error yo'q
check_application_error: PASSED
check_content_ready va title: ishlaydi
```

### 2. Biruni error ko'rindi

```text
matched_selector: #biruniAlert:visible
check_application_error: FAILED / APPLICATION_ERROR
screenshot: modal ochiq holatda olinadi
modal_cleanup_attempted: true
content_ready: NOT_RUN
title: NOT_RUN
```

### 3. Inline yoki A2 error ko'rindi

```text
matched_selector: .alert-danger:visible
check_application_error: FAILED / APPLICATION_ERROR
modal_cleanup_attempted: false
content_ready: NOT_RUN
title: NOT_RUN
```

### 4. Oddiy role alert ko'rindi

```text
[role="alert"]:visible mavjud
aniq hard-error selector yo'q
check_application_error: PASSED
```
