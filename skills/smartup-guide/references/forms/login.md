## Login Form

### Default Login Snapshot
Tags: login, auth, screenshot, locator
- URL pattern: `<company_url>/login.html`; odatiy server uchun `https://smartup.online/login.html`.
- Screenshot: `skills/smartup-guide/references/forms/screenshots/login/login__default__desktop-1440x900__20260610-151534.png`.
- UI holati: markazda Smartup login kartasi, yuqorida til selector (`Язык: РУС`), maydonlar `Логин@компания` va `Пароль`, asosiy tugma `ВОЙТИ`, linklar `Забыли пароль?` va `Войти через номер телефона`.
- Test locatorlari: `page.get_by_placeholder("Логин@компания")`, `page.get_by_role("textbox", name="Пароль")`, `page.get_by_role("button", name="Войти")`.
- Debug note: snapshot credential kiritmasdan, faqat default login sahifasi yuklangandan keyin olindi.

### Sessiya Qulfi / Timeout Overlay (#closing-session)
Tags: login, auth, session, timeout, overlay, flaky, locator
- **Muammo (flaky)**: Smartup belgilangan idle vaqtdan keyin test o'rtasida sessiya overlayini ko'rsatadi.
  Overlay `<div id="closing-session">` ichidagi `<div class="cs-backdrop open">` **barcha kliklarni intercept qiladi** →
  menu/list clicklari `TimeoutError` bilan yiqiladi (masalan `flow_navigate.py:7` da `... cs-backdrop open ... intercepts pointer events`).
- **Ikki holat** (MCP bilan smartup.online da tasdiqlangan):
  - Timeout-warning (`.cs-dialog.cs-timeout`): "Закрытие сессии", countdown "Осталось N сек.", **"Продолжить"** tugmasi → `a.session.sessionStay()` sessiyani **parolsiz** uzaytiradi.
  - Lock/expired (`.cs-dialog.cs-lock.open`): avatar + user nomi + **"Пароль"** input + **"Войти"** (`a.relogin()`) + "Это не вы??" (`a.logout(true)`). Bu CI screenshotidagi holat.
- **Yechim** (`flow_authorization.install_session_keepalive`, har `login()` da avtomatik o'rnatiladi):
  - `page.add_locator_handler("#closing-session .cs-backdrop.open", ...)` — overlay har qanday action'ni to'sganda avtomatik ishlaydi.
  - Avval "Продолжить" (sessionStay) ko'rinsa bosadi; bo'lmasa parol (`input[type=password]`) + **`press("Tab")`** (ng-model `a.session.si.rePassword` commit bo'lsin) + "Войти".
  - Tugmadan keyin handler **`.cs-backdrop.open` yo'qolguncha kutadi** — aks holda async relogin tugamasdan Playwright handlerni qayta chaqirib uzib yuboradi.
  - Parol: oxirgi `login()` dagi parol (admin: company_password, user: 123456789) `id(page)` bo'yicha saqlanadi.
- **Muhim nuance**: `press("Tab")`siz `fill`+`click` ishlamaydi (ng-model commit bo'lmaydi, relogin bo'sh parol bilan ketadi). relogin URL'ni o'zgartirmaydi (`url_changed=False`), in-place sessiyani tiklaydi.
- Trigger (debug uchun): `angular.element(document.getElementById('closing-session')).scope()` zanjirida `a.session.lockScreen()` overlayni summon qiladi.

### Login POST 500 — UCP-29
Tags: login, auth, backend, connection-pool, 500, debug
- Belgisi: login maydonlari to'g'ri to'ldirilib `Войти` bosilgach sahifa `login.html`da qoladi; `dashboard()` `Trade` headingni kutib timeout bo'ladi va UI'da aniq credential xatosi ko'rinmasligi mumkin.
- Tasdiqlangan sabab (2026-07-13): trace networkda `POST /b/biruni/s$log_in` javobi `500`, response body `UCP-29: Failed to get a connection` bo'lgan.
- Tahlil qoidasi: bunday holatni darhol noto'g'ri `code` yoki parol deb xulosa qilma; trace networkdagi login POST statusi va response bodyni tekshir. `UCP-29` Smartup backend connection pool xatosi, test locator xatosi emas.
