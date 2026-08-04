# PnL

Tags: pnl, finance, menu, a2, migration, locator

## Quick Lookup

### A2 menyu nomi va route
Status: live-ui-confirmed
Verified: 2026-08-04
Source: `smartup.online` live UI
- Form slug: `pnl`.
- User track: operatsion filial → `Финансы` → `Отчеты` →
  `Отчет о прибылях и убытках`.
- Exact menu locator parametri:
  `menu_item="Отчет о прибылях и убытках"`.
- Menu item href'i va canonical URL: `/a2/anor/rep/mkr/pnl`.
- Browser title va sahifa H1'i: `Отчет о прибылях и убытках`.

## Screenshot Paths

- Current A2 menu state: N/A.
- Eski legacy menu kuzatuvi:
  [2026-07-24 Финансы menyusi](screenshots/pnl/pnl__legacy-menu-path__desktop-1440x783__operational-filial.png).

## Known Locators

- Navbar: exact accessible-name button `Финансы`.
- Menu column: heading `Отчеты`.
- A2 PnL leaf: exact accessible-name menuitem
  `Отчет о прибылях и убытках`; href `/a2/anor/rep/mkr/pnl`.
- `PnL` nomli exact menuitem joriy UI'da yo'q.
- Yaqin nomli itemlarni aralashtirma:
  - `Прибыль и убыток (PnL)` → legacy
    `anor/rep/mkr/profit_and_loss`;
  - `Отчет о прибылях и убытках (БЕТА)` → legacy
    `anor/rep/mkr/profit_and_loss_two`;
  - `Отчет о прибылях и убытках` → A2 `anor/rep/mkr/pnl`.

## Flow And Tests

- Menu inventory/test:
  `tests/smoke/test_forms/test_02_a2_admin_menu_forms.py`.
- Testdagi `menu_item="PnL"` va `Title: PnL` yozuvlari 2026-08-04 live UI
  kontraktiga nisbatan eskirgan; alohida implementatsiya tasdig'i bilan
  yangilanishi kerak.

## Business Rules

- Test faqat exact `Отчет о прибылях и убытках` itemini bosishi kerak; shu
  item A2 PnL formasini ochadi.
- `Прибыль и убыток (PnL)` boshqa legacy forma, shuning uchun substring yoki
  `PnL`ga asoslangan noaniq locator ishlatilmasin.

## Known Issues

- Joriy test inventari hali eski `menu_item="PnL"` qiymatidan foydalanadi;
  live UI'da bunday exact menuitem yo'q.
