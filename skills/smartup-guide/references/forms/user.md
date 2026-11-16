# Пользователи (User) — yaratish, rol va ruxsatlar

User setup 5 ta alohida funksiya: `run_user`, `run_user_attach_form`, `run_role`, `run_role_attach_form`, `run_change_password`.

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)
- [Umumiy navigatsiya](#umumiy-navigatsiya)
- [User yaratish](#run_user--foydalanuvchi-yaratish)
- [User formalarini ulash](#run_user_attach_form--formalar-ulash)
- [Admin rolini sozlash](#run_role--admin-rolini-sozlash)
- [Rolga formalar ulash](#run_role_attach_form--roliga-barcha-formalar)
- [Parolni tasdiqlash](#run_change_password--parolni-tasdiqlash)
- [Test](#test)

## Quick Lookup

### Umumiy navigatsiya

`run_*` funksiyalari faqat navigatsiya qiladi (auth/switch_filial YO'Q — `run_robot`/`run_natural_person` konvensiyasi):

```python
base.navigate_to(tab="Главное", name="Пользователи")
base.expect_page(heading="Пользователи", url="anor/mr/user_list")
```

Filialga o'tish va login `test_*` wrapper'da: setup zanjirida sahifa allaqachon `filial-pw{code}` da (run_room o'tgan), shuning uchun `run_user`/`run_user_attach_form` ichida `switch_filial` **takrorlanmaydi** — u standalone/debug run uchun `test_user`/`test_user_attach_form` wrapper'ida `authorization(page, who='admin')` bilan birga chaqiriladi. `run_role`/`run_role_attach_form` code'ga bog'liq emas (rol company-level): ular o'zi Пользователи→Роли ga navigatsiya qiladi, wrapper faqat `authorization(admin)` qiladi. `run_change_password` esa o'zi user sifatida `login(...)` qiladi (wrapper bare).

## Screenshot Paths

- `references/forms/screenshots/user/user__add-after-password__desktop-1920x1080.png`
- `references/forms/screenshots/user/user__attach-forms-available-mcp-20260710__desktop-1440x1000.png`
- `references/forms/screenshots/user/user__attach-forms-available__desktop-1920x1080.png`
- `references/forms/screenshots/user/user__change-password-validation-overlay__desktop-1440x783.png`

## Known Locators

### run_user — foydalanuvchi yaratish

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_06_user.py:34`
- `Пользователь (создание)`da `Логин`, `Пароль` inputlari, `Физическое лицо` b-inputi va `Штат` multiselecti to‘ldiriladi. Rol `form_view(label="Роли", expect_value="Админ")` bilan, status `checkbox(label="Статус", expect_checked=True)` bilan tekshiriladi.
- Saqlangach test bitta qatorda jismoniy shaxsning nomi, to‘liq `user-pw{code}@<company_code>` logini va `Активный`ni tasdiqlaydi.

#### User IDni view URLdan olish
Tags: user, view, id, data-store
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI; `tests/smoke/test_setup/test_06_user.py`
- View URLida `anor/mr/user_view?user_id=<id>` keladi. Setup `user_id`ni `user_person_id`dan alohida saqlaydi.

## run_user_attach_form — formalar ulash

Joriy test person nomi va to‘liq login bilan user qatorini topadi va exact loginni bosib, `Просмотреть` orqali view’ni ochadi. List chizilishi actionni yopsa, shu listda qolganini tekshirib qatorni bir marta qayta tanlaydi. So‘ng view’dagi **Формы** bo‘limini ochadi.

| Tab | Harakat |
|---|---|
| Формы | Доступные → loader → 1000 → grid all → Прикрепить → confirm → loader → нет данных |
| Отчеты | Доступные → loader → 1000 → grid all → Прикрепить → confirm → loader → нет данных |
| Накладные | Доступные → loader → 500 → grid all → Прикрепить → confirm → loader → нет данных |
| Внешние системы | Доступные → loader → 1000 → grid all → Прикрепить → confirm → loader → нет данных |

Bu attach pattern faqat shu testga xos, shuning uchun
`test_07_user_attach_form.py` ichidagi
`_attach_available_permissions(base, expand=...)` local helperida qoladi.

### User attach form grid controller
Tags: user, grid, locator, setup, mcp
Status: code-confirmed
Verified: 2026-07-31
Source: `tests/smoke/test_setup/test_07_user_attach_form.py:11`; `utils/base_pages/base_page.py::BasePage.click`
- screenshot: `references/forms/screenshots/user/user__attach-forms-available-mcp-20260710__desktop-1440x1000.png`
- sahifa: `Пользователь (просмотр) → Формы → Доступные` (`natural_person-pw{code}` user view).
- MCP kuzatuv: sahifada bir nechta `b-grid-controller` DOMda qoladi; hidden tab controllerlari visible controllerdan oldin kelishi mumkin. `BasePage.grid_controller()` default selector bilan hidden controllerga tushmasligi uchun visible controllerni ishlatishi kerak.
- `expand`: faqat string limit qabul qiladi — `"50"`, `"100"`, `"500"`, `"1000"`. Dropdownni ochib, shu limit linkini tanlaydi va loaderni kutadi; `expand=True` ishlatilmaydi.
- testda ishlatish: `run_user_attach_form`da
  `_attach_available_permissions(base, expand=...)` saqlansin; helper
  `Доступные`ni ochadi, loaderni kutadi, `base.grid_controller(expand=...)` va
  `base.grid(checkbox="all")` orqali barcha qatorni tanlaydi, `Прикрепить` +
  `confirm_biruni()`dan keyin loaderni kutib, ko'rinadigan gridda
  `base.grid(state="empty")` orqali `нет данных`ni tekshiradi.

## Business Rules

### run_role — Admin rolini sozlash

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_08_role.py:68`

`Главное → Пользователи → Роли` yo‘lida `Админ` qatori tanlanadi. Test `ROLE_PERMISSIONS` ro‘yxatidagi ruxsatlarning har birini label orqali yoqadi. Saqlagach aynan shu rolni qayta ochib, har bir checkboxning checked holatini tekshiradi.

#### Floating widgetlar switch klikini to'ssa
Tags: role, permissions, onboarding, chat-widget, locator, debug
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_08_role.py:74`
- Rol ruxsatlarini tanlashdan oldin `hide_ui`ga `#onboarding-launcher`, `.b24-widget-button-popup` va `.b24-widget-button-popup-image` selektorlari beriladi.

## run_role_attach_form — roliga barcha formalar

Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_setup/test_09_role_attach_form.py:35`

Test A2 main ichidagi exact `Админ` qatoridan `Просмотреть` orqali view’ni ochib rol nomini tekshiradi. `Формы → Доступ ко всем формам → Разрешить` confirmi bilan birga `role_form_list$access_generate_all` POST javobini kutadi. Shu javob tugab, HTTP muvaffaqiyatli bo‘lgach `Доступные` gridining bo‘shligini tekshiradi.

## Known Issues

### run_change_password — parolni tasdiqlash

**Screenshot:** `references/forms/screenshots/user/user__change-password-validation-overlay__desktop-1440x783.png`
— validation qoidalari confirmation input ustiga tushib pointer clickni bloklagan holat.

**"Пароль (изменение)" formasi qachon chiqadi (2026-07 tasdiqlangan):** (a) user qo'shilganda — birinchi loginda majburiy, (b) user paroli o'zgartirilganda, (c) profildan "Изменить пароль" (`a.openChangePassword()`). Uchalasida ham **bir xil forma** (route `biruni/md/change_password`).

**MUHIM:** bu **mavjud company'da ham** yangi yaratilgan user (masalan setup zanjiridagi user-pw{code}) birinchi loginda force-change oladi — `test_12_change_password` Setup chain'ida green (2026-07-30 live run tasdiqlangan). Faqat **allaqachon parolini o'zgartirgan** eski user to'g'ridan-to'g'ri dashboardga kiradi (`.alert-icon` chiqmaydi). Bu `run_` o'zi user sifatida `login()` qiladi (auth wrapper'da emas) — wrapper `test_change_password` bare.

**Maydonlar:** joriy `BasePage.input(label=...)` implementatsiyasi uchala
password maydonida ishlaydi; `Новый пароль`dan keyin `press_tab=True`
validation holatini yangilaydi. Avvalgi raw `#id.fill()` majburiy degan qoida
joriy live run bilan tasdiqlanmadi va `references/history.md`ga ko'chirildi.

```python
login(page, email=user_email, password=user_password)
base.text(root=".alert-icon")
base.input(label="Текущий пароль", value=user_password)
base.input(label="Новый пароль", value=user_password, press_tab=True)
base.input(label="Подтверждение пароля", value=user_password)
base.click(name="Подтвердить")
base.confirm_biruni()
login(page, email=user_email, password=user_password)
dashboard(page)
```

Parol o'zgartirilmaydi (USER_PASS → USER_PASS), lekin sistem "tasdiqlangan" deb qabul qiladi.

#### Password-change'dan keyingi majburiy fresh login
Status: live-ui-confirmed
Verified: 2026-07-30
Source: `tests/smoke/test_setup/test_12_change_password.py`; CI trace runs
`30413648152`, `30531780519`; local `scripts/run_tests.py setup --headless`
(`20 passed, 1 deselected`)
- `change_password:save` muvaffaqiyatli tugagan sessiyada keyingi forma
  requesti license `401` olishi mumkin. Shu sabab `run_change_password`
  confirm'dan keyin eski SPA sessiyasini davom ettirmaydi: login sahifasidan
  user bilan yangidan kiradi va `dashboard()` orqali dashboard route ochilganini
  majburiy tekshiradi.
- Bu qayta login alohida Allure step:
  `4 - Parol tasdiqlangandan keyin majburiy qayta login`.

## Flow And Tests

### Test

Setup leaflari `tests/smoke/test_setup/test_06_user.py`, `tests/smoke/test_setup/test_07_user_attach_form.py`, `tests/smoke/test_setup/test_08_role.py`, `tests/smoke/test_setup/test_09_role_attach_form.py` va `tests/smoke/test_setup/test_12_change_password.py`.
