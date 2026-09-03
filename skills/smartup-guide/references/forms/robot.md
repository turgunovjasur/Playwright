# Штат (Robot) — yaratish

Robot = **Штат** (xodim/sotuvchi). Smoke testda "Админ" rolli, room-pw{code} biriktirilgan xodim yaratiladi.

## Navigatsiya

- Menyu: **Справочники → Штат**
- Ro'yxat heading: `Штат`
- Yaratish heading: `Штат (создание)`
- URL pattern: `.../anor/mrf/robot_list` (list), `.../anor/mrf/robot+add` (create)
- **Muhim:** "Штат" Справочники menyusida faqat to'g'ri filialga o'tilgandan keyin ko'rinadi.
  Shuning uchun test avval `switch_filial(page, name=f"filial-pw{code}")` qiladi, so'ng `navigate_to(tab="Справочники", name="Штат")`. Default/Администрирование filialida bu yo'l 404 beradi.

## Forma maydonlari

| # | Maydon | Locator | Qiymat |
|---|---|---|---|
| 1 | Код | `input(label="Код")` | `c_rb_pw{code}` |
| 2 | Название | `input(label="Название")` | `robot-pw{code}` |
| 3 | Роли (rol, multi-select) | `multiselect(label="Роли", value="Админ")` | `Админ` |
| 4 | Рабочие зоны (multi-select) | `multiselect(label="Рабочие зоны", value=room_name)` | `room-pw{code}` |

`Пользователь` (name=persons) va `Руководитель` (name=robot_manager) — single-select b-input'lar, smoke'da to'ldirilmaydi.

## Multi-select b-input ("N Выбранных") — `multiselect`

Base funksiya `b_input` bilan bir xil parametr uslubida ishlaydi:
`BasePage.multiselect(label=..., value=..., expect_value=..., return_value=..., clear=...)`.
`label` asosiy locator; label bo'lmasa `name="roles"`/`name="rooms"` fallback sifatida beriladi.

MCP bilan tasdiqlangan (2026-06-30, Штат formasi):

- `name` orqali: `b-input[name="roles"]` / `b-input[name="rooms"]` (barqaror; eski
  `filter(has_text="0 Выбранных")` mo'rt edi). Ikkalasida ham `multiple` atribut bor.
- `label` orqali: `_field_locator_by_label(..., target="b-input")` ishlatiladi. "Рабочие зоны"
  uchun bitta **ko'rinmas `span`** ham mos keladi (u `roles` ga ishora qiladi), lekin helper
  ko'rinmas labellarni o'tkazib yuborgani uchun to'g'ri `rooms` ga tushadi. Tasdiqlangan:
  "Роли"→roles, "Рабочие зоны"→rooms.
- Dropdown (`.hint > .hint-item`) **b-input ICHIDA** render bo'ladi (body'ga portal emas) →
  variant `b-input ... .hint` ichida scope qilinadi.
- Tanlangach **search maydoni bo'shaydi** (variant matnini ko'rsatmaydi) → `to_have_value()`
  ishlamaydi, shuning uchun `b_input`/`select_b_input` mos kelmaydi.
- Tanlangach **dropdown ochiq qoladi** → keyingi maydonga o'tishdan oldin **Escape** kerak
  (`multiselect` buni `close=True` bilan o'zi qiladi).
- Tasdiqlash `.multiple` ichidagi **chip** (tanlangan element matni) bo'yicha qilinadi.
- "Админ" exact tanlanadi (`exact=True`), aks holda "Администратор (системная роль)" va
  "Администратор запуска" ham mos kelib qoladi.

## Saqlash

`page.get_by_role("button", name="Сохранить", exact=True).first.click()` → `expect_page(page, heading="Штат")` — biruni confirm yo'q.

Natija ro'yxatda (`grid(robot_name, robot_code)`):
- `c_rb_pw{code}` ko'rinadi
- `robot-pw{code}` ko'rinadi

### View URLdan robot IDni olish

Tags: robot, view, id, data-store
Status: live-ui-confirmed
Verified: 2026-08-27
Source: live UI; `tests/smoke/test_setup/test_04_robot.py`

- Robot view URL patterni `anor/mrf/robot_view?robot_id=<id>`; summary ham
  `robot-pw{code} (<id>)` ko'rinishida IDni ko'rsatadi.
- Setup test save'dan keyin view'ni ochib, `robot_id`ni musbat integer sifatida
  tekshiradi va `data_store.json.robot_id`ga saqlaydi.

## Downstream ta'siri

- `test_06_user.py`: user yaratishda `robot-pw{code}` "Штат" maydoniga biriktiriladi
- Order yaratishda robot avtomatik to'ladi (room-pw{code} tanlangach)

## Test

- `tests/smoke/test_setup/test_04_robot.py` → `test_robot` → `authorization(who='admin')` →
  `switch_filial(filial-pw{code})` → `run_robot(page, code)`
