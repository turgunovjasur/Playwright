# Marking Stocktaking List

## Quick Lookup

- Form slug: `marking-stocktaking-list`
- URL pattern: `anor/mkw/marking_stocktaking/marking_stocktaking_list`
- Navigation: `Склад → Документы → Инвентаризации → Инвентаризация КМ`

## Screenshot Paths

N/A

## Known Locators

- Parent formadagi page link: `Инвентаризация КМ`

## Flow And Tests

- Navbar suite: `tests/smoke/test_forms/test_03_sklad_forms.py`
- A2 aggregate: `tests/smoke/test_forms/test_a2_angular_forms.py`
- Skip registry: `tests/smoke/test_forms/inventory/skipped_forms.py`
- Holat: ikkala inventarda saqlanadi, test rejasi tuzilganda skip registry
  orqali aktiv caselardan chiqariladi va intentional skip sifatida hisobotga
  qo'shiladi.

## Business Rules

N/A

## Known Issues

### Joriy test muhitida dostup yo'q
Tags: a2, marking-stocktaking, access, forms, skip
Status: user-reported
Verified: pending
Source: user
- Qayerda: `anor/mkw/marking_stocktaking/marking_stocktaking_list`.
- Qoida: joriy test muhitida formaga dostup yo'q.
- Testda ishlatish: dostup berilguncha formani `SKIPPED_FORMS` registry'sida
  saqla; dostup berilgach registry'dan olib tashla.
