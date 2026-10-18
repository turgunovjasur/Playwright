# Supplier A2

## Quick Lookup

Status: live-ui-confirmed
Verified: 2026-09-28
Source: Xtrade live UI; `outputs/a2-migration-01a0e663/supplier-20260928.md`

- Menu: `Склад → Справочники → Поставщики`; list URL `/a2/anor/mkw/supplier_list`.
- Logical group: list, `supplier+add`, `supplier+edit`, `supplier_view`,
  `supplier_product_list` va `supplier_audit_details`.
- View/edit/product-list parametri: `supplier_id=<supplier_id>`.
- Source sheet rootidagi 3 ta route butun funksional guruh degani emas:
  edit/view/audit yo'llari source'ning boshqa qatorlarida ham turadi.

## Screenshot Paths

N/A — pilot dalili brauzer DOM/AX kuzatuvlari va yozma run qaydidir;
saqlangan screenshot yoki Playwright trace mavjud deb da'vo qilinmaydi.

## Known Locators

Status: live-ui-confirmed
Verified: 2026-09-28
Source: Xtrade live DOM; `outputs/a2-migration-01a0e663/supplier-20260928.md`

- Name: `smt-control` label `Название`, ichidagi `smt-data-select` textbox.
- Add'da status, НДС, Акциз switchlari; VAT yoqilganda `НДС (%)` textbox.
- Person-kind custom radio: `label.smt-radio` matni bilan scope qilib,
  `span[role="radio"]`ni tanlash mumkin; umumiy testda `base.radio` afzal.
- Row `.smt-data-row`; code/name bilan exact scope. Row clickdan keyin inline
  action tugmasi paydo bo'lishini kutish kerak.
- View tablarda outer/inner button dublikatlari bor; `base.click(role="tab")`
  tab-aware helperidan foydalaniladi.
- Search `Поиск...`: qiymat kiritilgach Enter. Bo'shatishda inputning haqiqiy
  qiymatini tekshirish kerak; pilotdagi `fill('')` no-op holati ilova bugi
  sifatida tasdiqlanmagan, select-all/backspace + Enter ishlagan.

## Flow And Tests

Status: code-confirmed
Verified: 2026-09-28
Source: `tests/smoke/test_suppliers/test_01_supplier_purchase_tab.py`

- Focused avtotest create → view → purchase tabni tekshiradi; supplierni
  `finally`da o'chiradi. Noyob legal-person prerequisite diagnostika uchun qoladi.
- Standalone wrapper admin auth va `filial-pw<code>`ni talab qiladi; `.env`
  boshqa serverni ko'rsatsa avval muhitni moslash kerak. URL/credential hardcode yo'q.
- Test yozilgan, **run qilinmagan**; endpoint response predicate'i UI error
  nomidan kelib chiqqan, real pytest executionda tasdiqlanishi kerak.
- Umumiy smoke runnerga qo'shilmagan; to'liq checklist avtotesti deb hisoblanmaydi.

## Business Rules

Status: live-ui-confirmed
Verified: 2026-09-28
Source: Xtrade live UI; `outputs/a2-migration-01a0e663/supplier-20260928.md`

- Name majburiy; dastlab Save disabled. Yuridik/jismoniy shaxsni tanlash yoki
  dropdown `Добавить` orqali prerequisite yaratish mumkin.
- Legal-person inline form: minimal `Полное название` va noyob `Код`;
  `Сохранить в качестве поставщика`ni tanlamasdan qaytib supplierni alohida saqlash.
- Natural-person inline form: `Имя` autocomplete. Pilotda yangi ism uchun
  Enter bilan qiymatni tasdiqlab dropdownni yopgach Save ishlagan; oddiy fill
  va birinchi Save yetarli bo'lmagan. Bu ilova bugi deb tasdiqlanmagan.
- Editda type/name readonly; VAT percent, VAT flag, excise va status mutable.
  VAT 12 → 15, excise true → false, active → inactive saqlanib qayta o'qilgan.
- Single row: Просмотреть, Изменить, Активный/Неактивный, Удалить,
  Прикрепить ТМЦ. Multiple: Изменить статус va Удалить N.
- Product attachment: Прикрепленные/Доступные; single va multiple
  Прикрепить/Открепить confirmation bilan; underlying product o'chirilmaydi.
- Search nom va mavjud bo'lmagan matn bilan, НДС va status filterlari,
  reset/Показать все tekshirilgan; bu barcha filter kombinatsiyalari kafolati emas.
- Delete supplier roleni olib tashlaydi; underlying shaxs kartochkasi qoladi
  (pilotda o'chirilgan supplierni o'sha legal persondan qayta qo'shish ishlagan).

## Known Issues

### Purchase tab error
Status: live-ui-confirmed
Verified: 2026-09-28
Source: Xtrade live UI; `outputs/a2-migration-01a0e663/supplier-20260928.md`

- Supplier view → `Закупки` → `Ошибка` dialogi:
  `URL: anor/mkw/supplier_view:purchase`.
- Noyob legal va natural supplierlarda qayta kuzatilgan; issue `SUP-001` ochiq.
- Kutilgan: purchase grid yoki xatosiz empty state. Actual: error modal,
  yopilgach ko'ringan empty grid muvaffaqiyat deb qabul qilinmaydi.
- HTTP status va backend root cause aniqlanmagan. Boshqa tablar o'tgani
  bu xatoni bekor qilmaydi; guruhga `passed` berilmaydi.
