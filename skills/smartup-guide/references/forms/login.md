# Login Form

## Quick Lookup

Joriy login manzili `<company_url>/a2/auth/login`. `authorization(...)` rolga mos profil bilan login qiladi va dashboard routeni kutadi.

## Screenshot Paths

### Default Login Snapshot

Tags: login, auth, screenshot
Status: live-ui-confirmed
Verified: 2026-06-10
Source: [Legacy login arxivi](screenshots/login/login__default__desktop-1440x900__20260610-151534.png)
- Legacy login kartasida `Логин@компания` va `Пароль` maydonlari, til tanlovi va `ВОЙТИ` tugmasi ko‘rinadi. Arxivdagi layout eski login sahifasiga tegishli.

## Known Issues

### Sessiya Qulfi / Timeout Overlay (#closing-session)

Tags: login, auth, session, overlay, locator
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/shared/reporting.py:139`
- 401 diagnostikasi joriy sahifada `#closing-session .cs-lock.open` ko‘rinsa `session_lock`ni qayd etadi. Sababni aniqlash uchun birinchi 401 javobi va UI holati birga o‘qiladi.

### License 401 ham generic sessiya qulfini chiqaradi
Tags: login, auth, session, license, 401, overlay, ci, debug
Status: trace-confirmed
Verified: 2026-07-30
Source: GitHub Actions runs `30413648152`, `30531780519`; artifacts
`traces/smoke_trace.zip`; Allure failure screenshots
- `util/session_info` 1800 sekund ko'rsatib, UI/network activity uzluksiz davom
  etgan holatda `POST /b/anor/mkr/price_type+add:model` `401` va
  `Нет лицензии для входа в систему!` body qaytargan.
- 401 dan keyin Smartup aynan `.cs-lock.open` parol bilan qayta kirish
  overlayini ko'rsatgan. Shuning uchun bunday screenshotni avtomatik ravishda
  idle-timeout deb talqin qilma; trace networkdagi birinchi 401 response body
  asosiy sababni ajratadi.
- Xato turli forma/qadamda ko'rinishi mumkin: backend 401 qaytargan birinchi
  navbatdagi form requesti yiqiladi, failure joyi esa faqat shu requestni
  yuborgan heading yoki locator bo'ladi.
- Bir xil license 401 UI'da ikki xil yakunlangan: `30413648152` runida
  `login.html`ga to'liq redirect, `30531780519` runida esa joriy route ustida
  `.cs-lock.open` overlay. Debug ikkala state'ni ham auth/license failure deb
  tekshirishi kerak.
- Ikkala trace'da ham ketma-ketlik `license attach 200 → user login/session 200
  → change_password:save 200 → 8–14 sekund ichida license 401` bo'lgan.
  Takroriy trigger majburiy parol o'zgartirishdan keyingi session/license
  lifecycle ekanini ko'rsatadi; backend ichida license lease nima uchun
  yo'qolishini faqat server logi ajrata oladi.

### Joriy kodda sessiya-qulf recovery handleri yo'q

Tags: login, auth, session, overlay, recovery, regression
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/shared/authorization.py:30`; `tests/smoke/test_setup/test_12_change_password.py:42`
- Shared login helperi e’lon widgeti uchun handler o‘rnatadi. Parol almashtirish smoke case’i confirmdan so‘ng user bilan fresh login qilib dashboard routeni tasdiqlaydi. Eski session keepalive tarixi [history.md](../history.md)da.

### HTTP 401 failure diagnostikasi
Tags: login, auth, license, 401, diagnostics, allure, telegram
Status: code-confirmed
Verified: 2026-07-30
Source: `tests/shared/reporting.py`, `tests/smoke/conftest.py`,
`scripts/analyze_test_result.py`, `telegram_bot/telegram_progress.py`
- Har smoke page faqat Smartup bilan bir origin'dagi birinchi HTTP `401`ni
  test kesimida saqlaydi; keyingi test boshlanishidan oldin holat tozalanadi.
- Failure xabari request method + querysiz path, HTTP status, faqat xavfsiz
  tanilgan server xabari va UI holatini (`session_lock`, `login_redirect`
  yoki `current_page`) chiqaradi. Noma'lum raw response body, request body,
  header, query va credentiallar yozilmaydi.
- Server xabari `Нет лицензии для входа в систему!` bo'lsa error turi
  `LicenseSessionUnauthorized`; boshqa 401 uchun `AuthSessionUnauthorized`.
  Bu strukturali dalil Allure `auth-diagnostic` attachment, failure log va
  Telegramdagi `Auth diagnostika` qatoriga uzatiladi va oddiy locator
  timeoutidan ustun sabab sifatida ko'rsatiladi.

### Login POST 500 — UCP-29

2026-07-13 dagi backend xatosi bo‘yicha [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi). Yangi login xatosini tekshirishda o‘sha running login javobi kerak.

## Known Locators

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/shared/authorization.py:45`
- Login `Логин` va `Пароль` exact labellari yoki eski `Логин@компания` / `Пароль` placeholderlaridan topiladi. Submit tugmasi `Войти`.

## Flow And Tests

`tests/shared/authorization.py` ichidagi `authorization`, `login` va `dashboard` smoke flowlariga xizmat qiladi. `tests/smoke/test_setup/test_12_change_password.py` majburiy parol almashgach shu login oqimini takrorlaydi.

## Business Rules

`who="user"` uchun setup kodi talab qilinadi. Head va company admin profillari o‘z konfiguratsiyasidagi credentiallarni ishlatadi.
