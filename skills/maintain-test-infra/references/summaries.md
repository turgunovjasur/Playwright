# System va AI Summary

## Mundarija

- [System summary](#system-summary)
- [AI summary](#ai-summary)
- [Safety](#safety)

## System summary

Status: code-confirmed
Verified: 2026-08-05
Source: `scripts/analyze_test_result.py`, `scripts/run_tests.py`

- System summary AI emas va har run uchun
  `test-results/system-summary.md/json`ga yoziladi.
- U failed test, ichki Allure step, source, error turi va dalilga asoslangan
  qisqa sababni jamlaydi.
- Smoke page'da HTTP 401 ushlangan bo'lsa, Allure `auth-diagnostic`
  attachmentini o'qib, `LicenseSessionUnauthorized` yoki
  `AuthSessionUnauthorized`ni locator timeoutidan ustun diagnostika qiladi;
  method, querysiz path, status, xavfsiz tanilgan server xabari va UI holatini
  system summary hamda Telegramga uzatadi.
- `setup-forms` runida Allure `form-monitor.json` attachmentidan umumiy
  `form_coverage`, `Справочники`/`A2 Admin`/`Продажа` suite kesimi va barcha
  muammoli formalarni chiqaradi. Attachment mavjud bo'lmagan eski natijalarda
  numbered Allure steplari fallback sifatida ishlatiladi.
- Failed pytest itemda form-monitor attachment bo'lsa, deterministic sabab
  generic `AssertionError`dan emas, birinchi structured form issue'dan olinadi:
  forma raqami/title, status/reason code, expected path, actual URL/title va
  readiness checklar. Bo'sh Expected/Actual/UI kabi qatorlar Markdown'da
  chiqarilmaydi.
- Form monitor attachmenti suite `finish()` Allure stepida nested bo'lishi
  mumkin; analyzer top-level `attachments` bilangina cheklanmay, butun nested
  step daraxtini ko'radi. Aks holda aniq payload mavjud bo'lsa ham summary
  generic `AssertionError`ga qaytib ketadi.
- Analyzer schema v2 payloadlarni ham defensive o'qiydi; schema v3 inventory
  qo'shimchalari eski result/status maydonlarini o'zgartirmaydi.
- Allure ichida `System Test Summary` sifatida attach qilinadi.

## AI summary

- Default off; faqat `scripts/run_tests.py ... --ai-summary` bilan yoqiladi.
- Provider Gemini; model `GEMINI_MODEL` yoki koddagi defaultdan olinadi.
- Key faqat `GEMINI_API_KEY` environment variable orqali olinadi.
- Natija `test-results/ai-summary.md/json`ga yoziladi va Allure'ga alohida
  attachment qilinadi.
- AI xulosa test pass/fail statusini o'zgartirmaydi va system summary o'rnini bosmaydi.

## Safety

- Key, token, credential, raw request yoki secretli URLni summary/chat/logga yozma.
- Telegram final natijasini AI availability'ga bog'lama.
- Xom provider error yoki uzun stacktrace'ni user-facing asosiy xabar qilma;
  diagnostika logida redacted ko'rinishda saqla.
