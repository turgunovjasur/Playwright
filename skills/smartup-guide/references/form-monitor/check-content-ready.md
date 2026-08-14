# FormMonitor `check_content_ready` Kontrakti

Status: code-confirmed
Verified: 2026-08-11
Source: user; `tests/smoke/test_forms/monitoring/checks/content_ready.py`;
`tests/smoke/test_forms/monitoring/monitor.py`;
`tests/smoke/test_forms/monitoring/checks/core.py`;
`tests/smoke/test_forms/monitoring/diagnostics/core.py`;
`tests/smoke/test_forms/monitoring/navigation.py`;
`tests/smoke/test_forms/monitoring/reporting.py`
Contract approval: approved by user
Implementation: implemented

## Mundarija

- [Maqsad](#maqsad)
- [Konseptual interfeys](#konseptual-interfeys)
- [Hard-check tartibi](#hard-check-tartibi)
- [Ready signal tanlash](#ready-signal-tanlash)
- [Muvaffaqiyat natijasi](#muvaffaqiyat-natijasi)
- [Failure natijasi](#failure-natijasi)
- [Fail-fast qoidasi](#fail-fast-qoidasi)
- [Failure evidence](#failure-evidence)
- [Suite davomiyligi](#suite-davomiyligi)
- [Implementatsiya invariantlari](#implementatsiya-invariantlari)
- [Acceptance misollari](#acceptance-misollari)

## Maqsad

`check_content_ready` URL, loader va application-error gate'lari o'tgandan
keyingi to'rtinchi hard check. U to'g'ri URL ichida forma kontenti haqiqatan
tayyor bo'lishini o'z timeouti ichida kutadi. URLning o'zi ochilishi yoki
loader yo'qolishi kontent tayyorligini isbotlamaydi.

## Konseptual Interfeys

```python
check_content_ready(
    page,
    *,
    shell,
    ready=None,
    timeout=15_000,
)
```

- `ready` — optional explicit CSS selector.
- `shell` — `check_url` actual URLdan aniqlagan `legacy` yoki `a2` qiymati.
- `ready` berilsa non-empty string bo'lishi shart.
- Default timeout aynan `15_000 ms`.
- Kutish va timeout klassifikatsiyasi checkning o'zida; caller va
  `capture_form_state()` uni takrorlamaydi.

## Hard-check Tartibi

```text
check_url
→ check_loader
→ check_application_error
→ check_content_ready
→ check_title
```

`check_content_ready` faqat oldingi uchta gate `PASSED` bo'lganda ishlaydi.

## Ready Signal Tanlash

### Explicit

Case'da `ready` berilsa faqat shu selector visible bo'lishi kutiladi:

```text
ready_source: explicit
expected_ready: <case ready selector>
```

Selectorning matni bo'sh bo'lishi mumkin; visible markerning o'zi yetarli.

### Legacy Default

`ready` yo'q va `shell=legacy` bo'lsa quyidagilardan biri kutiladi:

```css
b-page:visible
.subheader:visible
```

```text
ready_source: legacy_default
```

### A2 Default

`ready` yo'q va `shell=a2` bo'lsa:

```text
main visible
VA
main ichida non-empty text yoki visible direct child mavjud
```

```text
ready_source: a2_default
```

## Muvaffaqiyat Natijasi

```text
passed: True
execution_status: PASSED
timeout_ms: 15000
ready_source: explicit | legacy_default | a2_default
expected_ready: <kutilgan signal>
matched_selector: <ko'ringan signal>
content_observation: <qisqa kuzatuv>
```

Shundan keyin mustaqil browser-aware `check_title` hard gate ishlaydi.

## Failure Natijasi

Timeout ichida kontent tayyor bo'lmasa:

```text
passed: False
execution_status: FAILED
status: NOT_OPENED
reason_code: CONTENT_NOT_READY
timeout_ms: 15000
ready_source: <signal manbasi>
expected_ready: <kutilgan signal>
matched_selector: ""
actual_url: <joriy browser URLi>
```

Faqat Playwright timeout `CONTENT_NOT_READY` sifatida klassifikatsiya qilinadi.
Noto'g'ri CSS selector va boshqa kod/Playwright contract xatolari yashirilmaydi.

## Fail-fast Qoidasi

`check_content_ready=False` bo'lsa:

```text
title: NOT_RUN
blocked_by: content_ready
```

`content_ready` test-level configda disabled bo'lsa `DISABLED`; title odatdagi
oqimda ishlashda davom etadi.

## Failure Evidence

Failure paytida quyidagilar hisobotga yoziladi:

```text
actual_url
timeout_ms
ready_source
expected_ready
matched_selector
content_observation
```

Keyingi forma navigatsiyasidan oldin redacted full-page screenshot olinadi.
Check modalni yopmaydi va sahifa holatini o'zgartirmaydi.

## Suite Davomiyligi

1. Joriy forma `NOT_OPENED / CONTENT_NOT_READY` sifatida yoziladi.
2. `title` `NOT_RUN`, `blocked_by=content_ready` bo'ladi.
3. Evidence va progress natijasi chiqariladi.
4. Forma loopi keyingi planned case'ga o'tadi.
5. Suite oxiridagi aggregate assertion top-level pytest testini `FAILED`
   qiladi.

## Implementatsiya Invariantlari

- Default timeout aynan `15_000 ms`.
- `ready` optional; explicit bo'lmasa shell defaulti doim mavjud.
- Shell bu check ichida URLdan qayta aniqlanmaydi; `check_url` bergan parametr
  ishlatiladi.
- Explicit signal legacy/A2 defaultdan ustun.
- Content kutishning yagona pass/fail authoritysi `check_content_ready`.
- `check_title()` title kutish va pass/failning yagona authoritysi.
- `settle_form_open()` mavjud emas.
- `capture_form_state()` content readinessni kutmaydi yoki hisoblamaydi.
- Content failure'dan keyin title bajarilmaydi.
- Failure screenshot keyingi navigatsiyadan oldin olinadi.
- Pytest/browser run faqat user aynan `run qil` deganda bajariladi.

## Acceptance Misollari

### 1. Explicit ready

```text
ready: b-grid[name='items']
selector 15 soniyadan oldin visible
check_content_ready: PASSED
title: ishlaydi
```

### 2. Legacy default

```text
ready: berilmagan
.subheader:visible topildi
ready_source: legacy_default
check_content_ready: PASSED
```

### 3. A2 default

```text
ready: berilmagan
main visible va ichida kontent bor
ready_source: a2_default
check_content_ready: PASSED
```

### 4. Timeout

```text
15 soniya ichida ready signal yo'q
check_content_ready: FAILED / CONTENT_NOT_READY
title: NOT_RUN
blocked_by: content_ready
```
