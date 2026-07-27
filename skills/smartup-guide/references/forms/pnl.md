# PnL

Tags: pnl, finance, menu, legacy, a2, migration, locator

## Navigation

- User track: operatsion filial → `Финансы` → `Отчеты` → `PnL`.
- Exact menu locator parametri: `menu_item="PnL"`.
- `Прибыль и убыток (PnL)` menu item emas; navigatsiya locatorida
  ishlatilmasin.
- A2 testdagi eski kutuv: `/a2/anor/rep/mkr/pnl`.

## Screenshot

- [2026-07-24 dagi real Финансы menyusi](screenshots/pnl/pnl__legacy-menu-path__desktop-1440x783__operational-filial.png)

## Known issue: server menyusi legacy pathni beradi

Tags: stale-test, menu-model, route, profit-and-loss

- 2026-07-24, `app3.greenwhite.uz/xtrade`, operatsion filial: `PnL` menu
  itemining href'i A2 emas:
  `#/!<route-token>/anor/rep/mkr/profit_and_loss`.
- Shu sabab `a.menu-link[href$="/a2/anor/rep/mkr/pnl"]` DOMda topilmaydi.
  Bu run ichida PnL sahifasi ochilib keyin buzilgan emas; testning A2 path
  kutuvi joriy server menyusi bilan eskirgan.
- Testda ishlatish: PnL'ni A2 ro'yxatida qoldirishdan oldin joriy menu modelidagi
  `form`, `is_migrated` va `url` qayta tekshirilsin.
