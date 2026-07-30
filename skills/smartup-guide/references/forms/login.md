## Login Form

### Default Login Snapshot
Tags: login, auth, screenshot, locator
- URL pattern: `<company_url>/login.html`; odatiy server uchun `https://smartup.online/login.html`.
- Screenshot: `skills/smartup-guide/references/forms/screenshots/login/login__default__desktop-1440x900__20260610-151534.png`.
- UI holati: markazda Smartup login kartasi, yuqorida til selector (`Язык: РУС`), maydonlar `Логин@компания` va `Пароль`, asosiy tugma `ВОЙТИ`, linklar `Забыли пароль?` va `Войти через номер телефона`.
- Test locatorlari: `page.get_by_placeholder("Логин@компания")`, `page.get_by_role("textbox", name="Пароль")`, `page.get_by_role("button", name="Войти")`.
- `authorization(...)` login oxirida `dashboard(page)` orqali `Trade` headingni tekshiradi; caller bu assertni qayta yozmaydi.
- Debug note: snapshot credential kiritmasdan, faqat default login sahifasi yuklangandan keyin olindi.

### Sessiya Qulfi / Timeout Overlay (#closing-session)
Tags: login, auth, session, timeout, overlay, flaky, locator
- **Muammo (flaky)**: Smartup test o'rtasida sessiya overlayini ko'rsatishi
  mumkin. Overlay `<div id="closing-session">` ichidagi
  `<div class="cs-backdrop open">` **barcha kliklarni intercept qiladi**;
  heading, menu yoki list actioni keyingi ko'rinadigan simptom sifatida
  `TimeoutError`/`AssertionError` bilan yiqilishi mumkin.
- **Ikki holat** (MCP bilan smartup.online da tasdiqlangan):
  - Timeout-warning (`.cs-dialog.cs-timeout`): "Закрытие сессии", countdown "Осталось N сек.", **"Продолжить"** tugmasi → `a.session.sessionStay()` sessiyani **parolsiz** uzaytiradi.
  - Lock/expired (`.cs-dialog.cs-lock.open`): avatar + user nomi +
    **"Пароль"** input + **"Войти"** (`a.relogin()`) + "Это не вы??"
    (`a.logout(true)`).
- Trigger (debug uchun): `angular.element(document.getElementById('closing-session')).scope()` zanjirida `a.session.lockScreen()` overlayni summon qiladi.

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
Verified: 2026-07-30
Source: `tests/smoke/flows/flow_authorization.py`; git commits `21bdc3c`,
`f94b377`; CI head `0670b8f`
- `login()` hozir faqat login formasini to'ldirib `Войти`ni bosadi;
  `page.add_locator_handler(...)` o'rnatmaydi. Shu sabab lock overlay chiqqanda
  test o'z-o'zidan qayta login qilmaydi.
- Oldingi `install_session_keepalive()` implementatsiyasi `21bdc3c`da
  qo'shilgan, lekin `f94b377` refaktorida olib tashlangan. Tarixiy kontrakt
  `references/history.md`ga ko'chirilgan.
- Generic auto-relogin handler hali qaytarilmagan. `change_password:save`
  boundarysi uchun tor va deterministik himoya mavjud:
  `run_change_password()` majburiy fresh login qiladi va dashboardni
  tekshiradi.

### HTTP 401 failure diagnostikasi
Tags: login, auth, license, 401, diagnostics, allure, telegram
Status: code-confirmed
Verified: 2026-07-30
Source: `tests/smoke/smoke_reporting.py`, `tests/smoke/conftest.py`,
`scripts/analyze_test_result.py`, `scripts/telegram_progress.py`
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
Tags: login, auth, backend, connection-pool, 500, debug
- Belgisi: login maydonlari to'g'ri to'ldirilib `Войти` bosilgach sahifa `login.html`da qoladi; `dashboard()` `Trade` headingni kutib timeout bo'ladi va UI'da aniq credential xatosi ko'rinmasligi mumkin.
- Tasdiqlangan sabab (2026-07-13): trace networkda `POST /b/biruni/s$log_in` javobi `500`, response body `UCP-29: Failed to get a connection` bo'lgan.
- Tahlil qoidasi: bunday holatni darhol noto'g'ri `code` yoki parol deb xulosa qilma; trace networkdagi login POST statusi va response bodyni tekshir. `UCP-29` Smartup backend connection pool xatosi, test locator xatosi emas.
