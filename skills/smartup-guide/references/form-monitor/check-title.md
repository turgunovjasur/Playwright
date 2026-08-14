# FormMonitor `check_title` Kontrakti

Status: code-confirmed
Verified: 2026-08-11
Source: user; `tests/smoke/test_forms/monitoring/checks/title.py`;
`tests/smoke/test_forms/monitoring/monitor.py`;
`tests/smoke/test_forms/monitoring/checks/core.py`;
`tests/smoke/test_forms/monitoring/diagnostics/core.py`;
`tests/smoke/test_forms/monitoring/reporting.py`
Contract approval: approved by user
Implementation: implemented

## Mundarija

- [Maqsad](#maqsad)
- [Konseptual interfeys](#konseptual-interfeys)
- [Hard-check tartibi](#hard-check-tartibi)
- [Shell bo'yicha title manbasi](#shell-boyicha-title-manbasi)
- [Taqqoslash qoidasi](#taqqoslash-qoidasi)
- [Muvaffaqiyat natijasi](#muvaffaqiyat-natijasi)
- [Failure natijasi](#failure-natijasi)
- [Fail-fast qoidasi](#fail-fast-qoidasi)
- [Failure evidence](#failure-evidence)
- [Suite davomiyligi](#suite-davomiyligi)
- [Implementatsiya invariantlari](#implementatsiya-invariantlari)
- [Resolved regressions](#resolved-regressions)
- [Acceptance misollari](#acceptance-misollari)

## Maqsad

`check_title` URL, loader, application-error va content-ready gate'lari
o'tgandan keyingi beshinchi va oxirgi hard check. U forma nomini shellga mos
ishonchli signaldan o'z timeouti ichida kutadi va normalized exact tenglikni
tekshiradi.

## Konseptual Interfeys

```python
check_title(
    page,
    *,
    expected_title,
    shell,
    timeout=15_000,
)
```

- `expected_title` majburiy non-empty string.
- `shell` `check_url` actual URLdan aniqlagan `legacy` yoki `a2` qiymati.
- Default timeout aynan `15_000 ms`.
- Kutish va failure klassifikatsiyasi checkning o'zida; caller yoki
  `capture_form_state()` uni takrorlamaydi.
- Empty title, unsupported shell va noto'g'ri timeout UI nuqsoni emas,
  test-contract/configuration xatosi sifatida tashqariga chiqadi.

## Hard-check Tartibi

```text
check_url
→ check_loader
→ check_application_error
→ check_content_ready
→ check_title
```

`check_title` faqat oldingi barcha enabled gate'lar `PASSED` bo'lganda
ishlaydi.

## Shell Bo'yicha Title Manbasi

### Legacy

Ko'rinadigan semantic headinglarning normalized `innerText` qiymatlari
tekshiriladi:

```text
title_source: visible_heading
```

Bir nechta visible heading bo'lsa, ulardan kamida bittasi expected title'ga
exact teng bo'lishi yetarli. Bironta heading topilmasa title check silent pass
qilmaydi.

Named accessible-name exact locator ishlatilmaydi. Shu sabab heading ichidagi
matnsiz ikonka title check natijasiga qo'shilmaydi.

### A2

Browser `document.title` qiymati tekshiriladi:

```text
title_source: document_title
```

Visible A2 matni yoki Legacy heading A2 title authoritysi bo'lmaydi.

## Taqqoslash Qoidasi

Expected va actual qiymatlar taqqoslashdan oldin:

1. bosh/oxiridagi whitespace olib tashlanadi;
2. ketma-ket whitespace bitta bo'shliqqa aylantiriladi;
3. harf registri va punctuation o'zgartirilmaydi.

Partial yoki substring match qabul qilinmaydi:

```text
expected: ТМЦ
actual:   ТМЦ
result:   PASSED
```

```text
expected: ТМЦ
actual:   ТМЦ (создание)
result:   FAILED
```

## Muvaffaqiyat Natijasi

```text
passed: True
execution_status: PASSED
timeout_ms: 15000
title_source: visible_heading | document_title
expected_title: <kutilgan forma nomi>
actual_title: <topilgan forma nomi>
title_candidates: <visible headinglar yoki document.title>
```

## Failure Natijasi

Timeout ichida expected title ko'rinmasa:

```text
passed: False
execution_status: FAILED
status: OPENED_WITH_DEFECT
reason_code: TITLE_NOT_REACHED
timeout_ms: 15000
title_source: <signal manbasi>
expected_title: <kutilgan forma nomi>
actual_title: <haqiqiy forma nomi yoki bo'sh>
title_candidates: <topilgan candidate'lar>
actual_url: <joriy browser URLi>
```

Title yo'qligi va noto'g'ri title alohida timeout/mismatch reasonlariga
ajratilmaydi. Ikkalasi ham belgilangan vaqt ichida expected title yetib
kelmaganini anglatadi.

## Fail-fast Qoidasi

Oldingi gate failed bo'lsa:

```text
title: NOT_RUN
blocked_by: url | loader | application_error | content_ready
```

Title test-level configda disabled bo'lsa:

```text
title: DISABLED
```

## Failure Evidence

Failure paytida keyingi navigatsiyadan oldin quyidagilar saqlanadi:

```text
actual_url
timeout_ms
title_source
expected_title
actual_title
title_candidates
document_title
```

Redacted full-page screenshot olinadi. Check modalni yopmaydi va sahifa
holatini o'zgartirmaydi.

## Suite Davomiyligi

1. Joriy forma `OPENED_WITH_DEFECT / TITLE_NOT_REACHED` sifatida yoziladi.
2. Evidence va progress natijasi chiqariladi.
3. Forma loopi keyingi planned case'ga o'tadi.
4. Suite oxiridagi aggregate assertion top-level pytest testini `FAILED`
   qiladi.

## Implementatsiya Invariantlari

- Default timeout aynan `15_000 ms`.
- Title source `check_url` actual URLdan aniqlab uzatgan `shell` orqali tanlanadi.
- Legacy title visible heading `innerText`i orqali kutiladi; named accessible
  locator ishlatilmaydi.
- Match whitespace-normalized exact; substring ishlatilmaydi.
- Legacy missing heading failure, skip yoki unverified pass emas.
- Title kutishning yagona pass/fail authoritysi `check_title`.
- `settle_form_open()` mavjud emas.
- `capture_form_state()` title'ni kutmaydi yoki hard-check qarorini chiqarmaydi.
- Failure screenshot keyingi navigatsiyadan oldin olinadi.
- Pytest/browser run faqat user aynan `run qil` deganda bajariladi.

## Resolved Regressions

### `Продажа` mixed-shell monitori 38/38 real UI verifikatsiyasi
Tags: form-monitor, title, legacy, a2, shell, regression
Status: live-ui-confirmed
Verified: 2026-08-11
Source: user-provided PyCharm pytest output for `tests/smoke/test_forms/test_02_prodaja_forms.py::test_prodaja_forms`
- Qayerda: `Forms-02 — Продажа` suite'ining legacy va A2 destinationlari.
- Dalil: barcha 38 forma `PASSED`, top-level pytest natijasi `1 passed`, process
  exit code `0` bo'ldi.
- Tasdiqlangan qoida: actual URLdan aniqlangan shell keyingi checklarga to'g'ri
  uzatiladi; ikonkalı legacy headinglar normalized `innerText`, A2 formalar esa
  `document.title` orqali false-negative bermasdan tekshiriladi.

### Legacy heading exact locator false-negative beradi
Tags: form-monitor, title, legacy, locator, false-negative
Status: code-confirmed
Verified: 2026-08-11
Source: `test-results/traces/tests_smoke_test_forms_test_02_prodaja_forms.py__test_prodaja_forms.zip`; `test-results/allure-results/446f8d22-1cb3-4a2c-9422-65b3695114a3-attachment.json`; `tests/smoke/test_forms/monitoring/checks/title.py`
- Qayerda: legacy `.subheader` ichidagi ikonka qo'shilgan `h6` forma title'lari.
- Oldingi xato: `get_by_role("heading", name=<title>, exact=True)` locatori
  ikonkalı legacy headingda expected visible matn mavjud bo'lsa ham resolve
  bo'lmagan va false `TITLE_NOT_REACHED` bergan.
- Joriy qoida: legacy title visible semantic headinglarning normalized
  `innerText` qiymati orqali exact tekshiriladi; named accessible-name locator
  ishlatilmaydi.

### `Продажа` navbar suite'i A2 destinationlarni legacy shellga majburlaydi
Tags: form-monitor, title, legacy, a2, inventory, shell
Status: code-confirmed
Verified: 2026-08-11
Source: `test-results/traces/tests_smoke_test_forms_test_02_prodaja_forms.py__test_prodaja_forms.zip`; `test-results/allure-results/446f8d22-1cb3-4a2c-9422-65b3695114a3-attachment.json`; `tests/smoke/test_forms/monitoring/checks/url.py`; `tests/smoke/test_forms/monitoring/monitor.py`; `tests/smoke/test_forms/monitoring/suite_runner.py`
- Qayerda: `Forms-02 — Продажа` ichidagi `/a2/`ga ochiladigan oltita direct
  destination.
- Oldingi xato: suite inventory shellini destination shell authoritysi sifatida
  ishlatgan; shu sabab legacy navbardan ochilgan A2 formalar legacy heading
  qoidasi bilan tekshirilgan.
- Joriy qoida: navbar manbasi va destination shell alohida tushunchalar;
  actual URL shellni bir marta aniqlaydi va A2 title `document.title` orqali
  tekshiriladi.

## Acceptance Misollari

### 1. Legacy exact heading

```text
expected: ТМЦ
visible headings: [ТМЦ]
check_title: PASSED
```

### 2. Legacy partial heading

```text
expected: ТМЦ
visible headings: [ТМЦ (создание)]
check_title: FAILED / TITLE_NOT_REACHED
```

### 3. Legacy heading yo'q

```text
expected: ТМЦ
visible headings: []
check_title: FAILED / TITLE_NOT_REACHED
```

### 4. A2 exact document title

```text
expected: Отчет о прибылях и убытках
document.title: Отчет о прибылях и убытках
check_title: PASSED
```

### 5. Oldingi gate failure

```text
check_content_ready: FAILED / CONTENT_NOT_READY
title: NOT_RUN
blocked_by: content_ready
```
