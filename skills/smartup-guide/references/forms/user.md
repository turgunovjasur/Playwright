# Пользователи (User) — yaratish, rol va ruxsatlar

User setup 5 ta alohida funksiya: `run_user`, `run_user_attach_form`, `run_role`, `run_role_attach_form`, `run_change_password`.

## Mundarija

- [Umumiy navigatsiya](#umumiy-navigatsiya)
- [Screenshot paths](#screenshot-paths)
- [User yaratish](#run_user--foydalanuvchi-yaratish)
- [User formalarini ulash](#run_user_attach_form--formalar-ulash)
- [Admin rolini sozlash](#run_role--admin-rolini-sozlash)
- [Rolga formalar ulash](#run_role_attach_form--roliga-barcha-formalar)
- [Parolni tasdiqlash](#run_change_password--parolni-tasdiqlash)
- [Test](#test)

## Umumiy navigatsiya

`run_*` funksiyalari faqat navigatsiya qiladi (auth/switch_filial YO'Q — `run_robot`/`run_natural_person` konvensiyasi):

```python
navigate_to(page, tab="Главное", name="Пользователи")
expect_page(page, heading="Пользователи")
```

Filialga o'tish va login `test_*` wrapper'da: setup zanjirida sahifa allaqachon `filial-pw{code}` da (run_room o'tgan), shuning uchun `run_user`/`run_user_attach_form` ichida `switch_filial` **takrorlanmaydi** — u standalone/debug run uchun `test_user`/`test_user_attach_form` wrapper'ida `authorization(page, who='admin')` bilan birga chaqiriladi. `run_role`/`run_role_attach_form` code'ga bog'liq emas (rol company-level): ular o'zi Пользователи→Роли ga navigatsiya qiladi, wrapper faqat `authorization(admin)` qiladi. `run_change_password` esa o'zi user sifatida `login(...)` qiladi (wrapper bare).

## Screenshot Paths

- `references/forms/screenshots/user/user__add-after-password__desktop-1920x1080.png`
- `references/forms/screenshots/user/user__attach-forms-available-mcp-20260710__desktop-1440x1000.png`
- `references/forms/screenshots/user/user__attach-forms-available__desktop-1920x1080.png`
- `references/forms/screenshots/user/user__change-password-validation-overlay__desktop-1440x783.png`

## run_user — foydalanuvchi yaratish

**Forma heading:** `Пользователь (создание)`

| Maydon | Locator | Qiymat |
|---|---|---|
| Login | `BasePage.input(label="Логин", value=...)` | `user-pw{code}` |
| Parol | `BasePage.input(label="Пароль", value=...)` | `USER_PASS` (hardcode, qoidalarda literal yozilmaydi) |
| Физическое лицо | `BasePage.b_input("Физическое лицо", value=...)` | `natural_person-pw{code}` |
| Штат | `BasePage.b_input("Штат", value=...)` | `robot-pw{code}` |

Штат tanlanganida uning roli (**"Админ"**) avtomatik ko'rinadi. **MUHIM:** "Роли" — input EMAS, u `d.robots` ga bog'langan read-only view. DOM: `<div class="form-group"><label><t>Роли</t></label><div class="form-view" ng-if="d.robots.length">Админ</div></div>`. Shuning uchun `BasePage.input(label="Роли", expect_value="Админ")` **ISHLAMAYDI** — `input` label'dan keyingi birinchi `<input>` ni (`d.code`, qiymati `natural_person_pw{code}`) topib olib "expected 'Админ', actual natural_person_pw{code}" beradi (MCP 2026-07 tasdiqlangan). To'g'ri tekshiruv — `.form-view` matnini o'qish:

```python
roli_group = page.locator("div.form-group").filter(has=page.get_by_text("Роли", exact=True))
expect(roli_group.locator(".form-view")).to_contain_text("Админ")
```

Логин maydoni yonida **qat'iy `@<company_code>` suffiksi** ko'rsatiladi (input faqat login qismini oladi). Shuning uchun ro'yxat grid'ining login ustuni to'liq email ko'rinishida bo'ladi: `user-pw{code}@<company_code>`.

**Login email pattern:** `user-pw{code}@<company_code>` — `user_email_for(code)` helper orqali.

`base.expect_page(heading="Пользователи")` dan so'ng ro'yxatda tekshirish:

```python
base.grid(f"natural_person-pw{code}", user_email_for(code), "Активный")
```

- qator **Физическое лицо** nomi (`natural_person-pw{code}`) bo'yicha topiladi;
- login ustuni `user_email_for(code)` = `user-pw{code}@<company_code>` ni o'z ichiga oladi — **parol emas** (grid parolni ko'rsatmaydi);
- status ustuni `Активный`.

`grid(text, *contains)` qatorning ko'rinishini ham, `contains` matnlarini ham assert qilgani uchun alohida `get_by_text(...).to_be_visible()` tekshiruvlari **takror** bo'ladi — ularni qo'shmang.

MCP bilan tasdiqlangan (2026-07): grid login ustuni `<login>@<company>` formatida; mavjud `natural_client-pw{code}` qatori login'i `123456789` bo'lgani uchun grid `123456789@<company>` ko'rsatgan — bu maxsus holat, `run_user` esa login'ni `user-pw{code}` qiladi.

## run_user_attach_form — formalar ulash

User view → **Формы** link:

| Tab | Harakat |
|---|---|
| Формы | Доступные → checkall → Прикрепить → confirm → нет данных |
| Отчеты | Доступные → checkall → Прикрепить → confirm → нет данных |
| Накладные | wait_for_loader → Доступные → checkall → Прикрепить → confirm → нет данных |
| Внешние системы | wait_for_loader → Доступные → checkall → Прикрепить → confirm → нет данных |

Page size 50→1000 qilinadi (agar 50/ button ko'rinsa). Bu attach pattern faqat shu testga xos, shuning uchun `test_user_attach_form.py` ichidagi `_attach_available_permissions(page, base)` local helperida qoladi.

### User attach form grid controller
Tags: user, grid, locator, setup, mcp
- screenshot: `references/forms/screenshots/user/user__attach-forms-available-mcp-20260710__desktop-1440x1000.png`
- sahifa: `Пользователь (просмотр) → Формы → Доступные` (`natural_person-pw{code}` user view).
- MCP kuzatuv: sahifada bir nechta `b-grid-controller` DOMda qoladi; hidden tab controllerlari visible controllerdan oldin kelishi mumkin. `BasePage.grid_controller()` default selector bilan hidden controllerga tushmasligi uchun visible controllerni ishlatishi kerak.
- `expand`: faqat string limit qabul qiladi — `"50"`, `"100"`, `"500"`, `"1000"`. Dropdownni ochib, shu limit linkini tanlaydi va loaderni kutadi; `expand=True` ishlatilmaydi.
- testda ishlatish: `run_user_attach_form`da `_attach_available_permissions(page, base)` saqlansin; helper ichida page size uchun `base.grid_controller(expand="1000")` → `base.checkbox(first_visible=True, checked=True)` → `Прикрепить` → `confirm_biruni()` tartibi ishlatiladi.

## run_role — Admin rolini sozlash

```
Роли link → "Админ" qatori → Изменить → "Роль (изменение)"
→ barcha o'chiq switchlarni toggling
→ save_and_expect_heading("Роли", timeout=600_000)
```

**Base funksiyalar (raw locator EMAS):** rollar ro'yxati ham b-grid — "Админ" ni tanlash `base.grid("Админ", click=True)` bilan (raw `get_by_text("Админ", exact=True).click()` EMAS; grid `has_text` substring bilan topadi, fresh setup'da faqat bitta "Админ" roli — kolliziya yo'q, MCP 2026-07 tasdiqlangan). Heading tekshiruvi `base.expect_page(heading="Роли")` (raw `expect(page.get_by_role("heading")).to_contain_text(...)` EMAS). Ikkalasi `run_role` va `run_role_attach_form` da bir xil.

**Switch tuzilishi (MCP 2026-07 tasdiqlangan):** har bir ruxsat — `<label class="switch"><input type=checkbox ng-model="function.state" ng-true-value="'Y'" ng-false-value="'N'"><span><t ng-if="state=='N'">нет</t></span></label>`. Select-all/"включить все" tugmasi **yo'q** — har birini alohida yoqish kerak. "Роль (изменение)"da ~30 permission switch + 1 status switch (`d.state`, "Активный") bo'ladi.

**To'g'ri (sodda) yondashuv — o'rovchi `<label>` ni bosish:** ichki `<span>` ni bosish barqaror emas edi (shuning uchun eski kodda pozitsiya-retry + chat-widget zona hisob-kitobi bor edi — endi KERAK EMAS). O'rovchi `label.switch` ni bosish checkboxni ishonchli toggle qiladi. `t:text-is("нет")` faqat o'chiq (state='N') switchlarni oladi → status switch va chat-widget avtomatik chetda qoladi:

```python
off_switches = page.locator('label.switch:has(t:text-is("нет"))')
remaining = off_switches.count()
while remaining > 0:
    off_switches.first.click()
    expect(off_switches).to_have_count(remaining - 1)   # click ishlaganini tasdiqlaydi
    remaining -= 1
```

Save timeout = **600_000** (10 min) — ko'p switch bo'lishi mumkin.

### Floating widgetlar switch klikini to'ssa
Tags: role, permissions, onboarding, chat-widget, locator, debug
- Muammo: `#onboarding-launcher` va Bitrix `.b24-widget-button-popup`/`.b24-widget-button-popup-image` role switch ustiga tushib, Playwright logida `intercepts pointer events` bilan click timeout beradi.
- Yechim: `Роль (изменение)` sahifasi ochilgach, switch loopidan oldin `BasePage.hide_ui(..., remove=True)` bilan bu testga aloqasiz widgetlarni DOMdan olib tashlang. `force=True` ishlatilmadi: haqiqiy click actionabilitysi saqlanadi.

## run_role_attach_form — roliga barcha formalar

```
"Админ" qatori → Просмотреть → Формы link
→ "Доступ ко всем формам" → "Разрешить" → confirm_biruni()
→ wait_for_loader(600_000) → Доступные → нет данных
```

## run_change_password — parolni tasdiqlash

**Screenshot:** `references/forms/screenshots/user/user__change-password-validation-overlay__desktop-1440x783.png`
— validation qoidalari confirmation input ustiga tushib pointer clickni bloklagan holat.

**"Пароль (изменение)" formasi qachon chiqadi (2026-07 tasdiqlangan):** (a) user qo'shilganda — birinchi loginda majburiy, (b) user paroli o'zgartirilganda, (c) profildan "Изменить пароль" (`a.openChangePassword()`). Uchalasida ham **bir xil forma** (route `biruni/md/change_password`).

**MUHIM:** bu **mavjud company'da ham** yangi yaratilgan user (masalan setup zanjiridagi user-pw{code}) birinchi loginda force-change oladi — `test_12_change_password` Setup chain'ida green (2026-07-30 live run tasdiqlangan). Faqat **allaqachon parolini o'zgartirgan** eski user to'g'ridan-to'g'ri dashboardga kiradi (`.alert-icon` chiqmaydi). Bu `run_` o'zi user sifatida `login()` qiladi (auth wrapper'da emas) — wrapper `test_change_password` bare.

**Maydonlar:** joriy `BasePage.input(label=...)` implementatsiyasi uchala
password maydonida ishlaydi; `Новый пароль`dan keyin `press_tab=True`
validation holatini yangilaydi. Avvalgi raw `#id.fill()` majburiy degan qoida
joriy live run bilan tasdiqlanmadi va `references/history.md`ga ko'chirildi.

```python
login(page, email=user_email_for(code), password=USER_PASS)
base.text(root=".alert-icon")
base.input(label="Текущий пароль", value=USER_PASS)
base.input(label="Новый пароль", value=USER_PASS, press_tab=True)
base.input(label="Подтверждение пароля", value=USER_PASS)
page.get_by_role("button", name="Подтвердить").click()
base.confirm_biruni()
login(page, email=user_email_for(code), password=USER_PASS)
dashboard(page)
```

Parol o'zgartirilmaydi (USER_PASS → USER_PASS), lekin sistem "tasdiqlangan" deb qabul qiladi.

### Password-change'dan keyingi majburiy fresh login
Status: live-ui-confirmed
Verified: 2026-07-30
Source: `tests/smoke/test_setup/test_change_password.py`; CI trace runs
`30413648152`, `30531780519`; local `scripts/run_tests.py setup --headless`
(`20 passed, 1 deselected`)
- `change_password:save` muvaffaqiyatli tugagan sessiyada keyingi forma
  requesti license `401` olishi mumkin. Shu sabab `run_change_password`
  confirm'dan keyin eski SPA sessiyasini davom ettirmaydi: login sahifasidan
  user bilan yangidan kiradi va `dashboard()` orqali `Trade` ochilganini
  majburiy tekshiradi.
- Bu qayta login alohida Allure step:
  `3 - Parol tasdiqlangandan keyin majburiy qayta login`.

## Test

- `tests/smoke/test_setup/test_change_password.py` → `run_change_password`
