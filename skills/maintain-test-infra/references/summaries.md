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
- System summary tashqi Markdown/JSON artefakt bo'lib qoladi; Allure test
  totalini sun'iy oshirmaslik uchun alohida passed pseudo-test yozilmaydi.
- Failed testcase ichidagi `00 - Failure Summary` AI'siz asosiy user-facing
  diagnostika bo'lib, system summaryni ochishni majburiy qilmaydi.

## AI summary

- AI tahlilining yagona runtime flagi `AI_ANALYSIS`: `1` yoqadi, `0`
  o'chiradi; boshqa qiymat configuration error hisoblanadi.
- Lokal va Windows runlarda flag repo rootdagi `.env`dan olinadi. GitHub
  Actions checkout lokal `.env`ni ko'rmagani uchun scheduled/manual CI ayni
  nomdagi GitHub Repository Variable (`AI_ANALYSIS`)ni environmentga uzatadi;
  variable yo'q bo'lsa default `0`.
- AI faqat deterministic natija `FAILED` bo'lganda chaqiriladi. `PASSED`
  natijada flag `1` bo'lsa ham AI chaqirilmaydi va AI artifact yaratilmaydi.
- Provider Gemini; model `GEMINI_MODEL` yoki koddagi defaultdan olinadi.
- Key faqat `GEMINI_API_KEY` environment variable orqali olinadi.
- Natija `test-results/ai-summary.md/json`ga yoziladi va Allure'ga alohida
  `AI xatolik tahlili` itemi sifatida Markdown va JSON attachmentlar bilan
  qo'shiladi.
- Telegram failed final xabarida shu JSONdan `Kuzatilgan`, `Ehtimoliy sabab`
  va Uzbekcha ishonch darajasi ko'rsatiladi; `Cheklov` va `Developer uchun`
  kabi takroriy bo'limlar chiqarilmaydi.
- AI xulosa test pass/fail statusini o'zgartirmaydi va system summary o'rnini bosmaydi.

### Server loglari va AI chegarasi
Status: user-reported
Verified: 2026-08-18
Source: user
- CI va AI tahlil oqimiga Smartup server loglari berilmaydi; AI faqat lokal
  test logi, Allure, trace'dan ajratilgan structured dalil, form monitor va
  system summaryni tahlil qilishi mumkin.
- Failure timestamp developerlar Smartup server loglarini qo'lda topishi uchun
  correlation point hisoblanadi; AI server logini ko'rmagani holda backend root
  cause'ni tasdiqlangan fakt sifatida ko'rsatmasligi kerak.

## Safety

- Key, token, credential, raw request yoki secretli URLni summary/chat/logga yozma.
- Telegram final natijasini AI availability'ga bog'lama.
- Xom provider error yoki uzun stacktrace'ni user-facing asosiy xabar qilma;
  diagnostika logida redacted ko'rinishda saqla.
