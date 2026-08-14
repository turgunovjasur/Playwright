# Order Va Client Settlement Scenario Coverage

## Mundarija

- [Coverage statuslari](#coverage-statuslari)
- [Group-0 joriy manual settlement oqimi](#group-0-joriy-manual-settlement-oqimi)
- [Group-0 testlar kesimidagi coverage](#group-0-testlar-kesimidagi-coverage)
- [Order yopish va settlement ssenariylari](#order-yopish-va-settlement-ssenariylari)
- [Keyingi ustuvorlik](#keyingi-ustuvorlik)
- [Yangilash qoidasi](#yangilash-qoidasi)

## Coverage Statuslari

### Scenario coverage registrini yuritish
Tags: order, settlement, coverage, scenario, test-plan
Status: user-reported
Verified: 2026-07-31
Source: user
- Qoida: order yopish va client settlement ssenariylari shu registrda
  saqlanadi; yangi test yozilganda qaysi ssenariy bajarilgani va qaysi biri
  qolganligi yangilanadi.
- Testda ishlatish: `DONE` faqat tegishli biznes natijalari assert qilingan va
  test live run orqali o'tganida qo'yiladi.

| Belgi | Status | Ma'nosi |
|---|---|---|
| ✅ | `DONE` | Test mavjud, biznes natijasi assert qilingan va live run o'tgan |
| 🟡 | `PARTIAL` | Oqimning bir qismi bor, lekin muhim biznes natijasi tekshirilmagan |
| ⬜ | `NOT_STARTED` | Alohida test hali yozilmagan |
| 🔍 | `NEEDS_ANALYSIS` | UI mavjud, ammo kutiladigan biznes natija live aniqlanishi kerak |
| 🔴 | `REGRESSION` | Test mavjud, lekin eng so'nggi tasdiqlangan run yiqilgan |

## Group-0 Joriy Manual Settlement Oqimi

### Archive debt, payment va manual offset
Tags: group-0, order, archive, payment, offset, lifecycle
Status: trace-confirmed
Verified: 2026-07-31
Source: `tests/smoke/test_groups/test_a_grup/test_0_group_runner.py`;
`tests/smoke/test_groups/test_a_grup/test_01_create_base_order.py`;
`tests/smoke/test_groups/test_a_grup/test_02_archive_base_order.py`;
`tests/smoke/test_groups/test_a_grup/test_03_post_client_payment.py`;
`tests/smoke/test_groups/test_a_grup/test_04_offset_client_balance.py`;
live Group-0 run (`4 passed`)
- Qayerda: `Заказы`, `Оплаты от клиентов`,
  `Взаиморасчеты с клиентами`.
- Qoida: joriy Group-0 `Новый → Архив → payment (auto-offset o'chiq) →
  manual Взаиморасчет` ssenariysini qoplaydi.
- Testda ishlatish: aniq order ID, baseline-delta settlement summalari va
  debt detaildagi order ID/summa/status tekshiriladi.

Toza client uchun kutiladigan biznes o'tishlari:

| Test | Harakat | Задолженность | Предоплата | Заказ | Баланс |
|---|---|---:|---:|---:|---:|
| `0-01` | Order yaratish | 0 → 0 | 0 → 0 | 0 → summa | 0 → -summa |
| `0-02` | Orderni `Архив` qilish | 0 → summa | 0 → 0 | summa → 0 | -summa → -summa |
| `0-03` | Paymentni `Провести` qilish | summa → summa | 0 → summa | 0 → 0 | -summa → 0 |
| `0-04` | Manual `Взаиморасчет` | summa → 0 | summa → 0 | 0 → 0 | 0 → 0 |

Rerun yoki oldindan ma'lumot mavjud clientda test absolute nollarni emas,
saqlangan `baseline → expected → actual` qiymatlarini ishlatadi.

## Group-0 Testlar Kesimidagi Coverage

| Test | Status | Hozir tekshiriladi | Qolgan yaxshilash |
|---|---|---|---|
| `0-01` | ✅ `DONE` | Order create, list/view, qiymatlar va exact IDni saqlash | Order yaratilgach settlementdagi `Заказ +summa`ni bevosita assert qilish |
| `0-02` | ✅ `DONE` | Exact IDni archive qilish, active listdan yo'qolishi, debt aggregate va debt detail | N/A |
| `0-03` | ✅ `DONE` | Paymentni auto-offsetsiz post qilish, debt saqlanishi va prepayment oshishi | N/A |
| `0-04` | ✅ `DONE` | Manual offset modal defaultlari va debt/prepayment net natijasi | Nol holatda client row qolishi yoki yo'qolishini alohida clean-data case bilan aniqlash |
| Allure state table | ⬜ `NOT_STARTED` | Hozir har bir settlement ustuni `BasePage.grid_cell` bilan alohida tekshiriladi | Har testga `before → expected → actual` jadval attachmenti qo'shish |

## Order Yopish Va Settlement Ssenariylari

| ID | Ssenariy | Coverage | Mavjud dalil yoki qolgan savol |
|---|---|---|---|
| `SCN-001` | `Новый → Архив → Payment → manual Взаиморасчет` | ✅ `DONE` | Group-0 `0-01`–`0-04`, live `4 passed` |
| `SCN-002` | Payment ichida `Провести взаимозачёт` orqali avtomatik yopish | ⬜ `NOT_STARTED` | Checkbox va optionlar live tasdiqlangan; debt/prepayment yakuniy natijasi uchun test yo'q |
| `SCN-003` | Normal operational lifecycle: `Черновик → Новый → В обработке → В ожидании → Отгружен → Доставлен → Архив` | 🟡 `PARTIAL` | `tests/smoke/test_life_cycle/test_order.py` statuslarni `Доставлен`gacha o'tkazadi; settlement natijasi tekshirilmaydi |
| `SCN-004` | Orderni `Отменен` qilish | ⬜ `NOT_STARTED` | Avvalgi A/B implementatsiyasi o'chirilgan; stock booking va client debt/balance oldin-keyin tekshirilishi kerak |
| `SCN-005` | Payment order/debtdan oldin kelishi: prepayment-first | ⬜ `NOT_STARTED` | Prepayment keyingi order qarziga qanday bog'lanishi tekshirilishi kerak |
| `SCN-006` | Qisman payment: payment debt summasidan kichik | ⬜ `NOT_STARTED` | Offsetdan keyin qolgan debt assert qilinishi kerak |
| `SCN-007` | Ortiqcha payment: payment debt summasidan katta | ⬜ `NOT_STARTED` | Offsetdan keyin qolgan prepayment assert qilinishi kerak |
| `SCN-008` | Bitta payment bilan bir nechta order/debtni yopish | ⬜ `NOT_STARTED` | Debt detail va qaysi orderlar yopilganini tekshirish kerak |
| `SCN-009` | Project, contract yoki payment type bo'yicha ajratilgan offset | ⬜ `NOT_STARTED` | Offset modal optionlari live mavjud; allocation natijasi test qilinmagan |
| `SCN-010` | Konsignatsiyali order settlementi | ⬜ `NOT_STARTED` | Avvalgi B implementatsiyasi o'chirilgan; payment/debt/offset lifecycle qaytadan yozilishi kerak |

`SCN-003` va `SCN-004` uchun moliyaviy natija hali current truth sifatida
qabul qilinmaydi. Avval live UI'da qaysi status `Заказ` summasini
`Задолженность`ka o'tkazishi va cancellation debt yaratmasligini tekshirish
kerak.

## Keyingi Ustuvorlik

1. `SCN-003`: normal delivery lifecycle'da debt qaysi statusda paydo
   bo'lishini aniqlash va settlement assertionlarini qo'shish.
2. `SCN-004`: `Отменен` holatida stock booking bo'shashi va qarz
   yaratilmasligini tekshirish.
3. `SCN-002`: payment ichidagi avtomatik offsetni alohida test qilish.
4. `SCN-006` va `SCN-007`: partial va overpayment qoldiqlarini tekshirish.
5. `SCN-005`, `SCN-008`, `SCN-009`, `SCN-010`: murakkab allocation va
   konsignatsiya ssenariylari.

## Yangilash Qoidasi

- Test yozishdan oldin scenario ID tanlanadi va test docstring/Allure titleda
  uning biznes maqsadi aniq ko'rsatiladi.
- Faqat UI action bosilgani coverage hisoblanmaydi; settlement, debt,
  prepayment, order yoki stockdagi tegishli natija assert qilinishi kerak.
- Live run o'tgach status `DONE`, test path va `Verified` sanasi yangilanadi.
- Testning faqat bir qismi mavjud bo'lsa `PARTIAL` saqlanadi va qolgan assertion
  jadvalda yoziladi.
- Eng so'nggi tasdiqlangan run regressiya bersa `REGRESSION` qo'yiladi; muammo
  tuzatilib qayta o'tmaguncha `DONE`ga qaytarilmaydi.
- Yangi ssenariy topilsa keyingi bo'sh `SCN-xxx` ID bilan shu registrga
  qo'shiladi; yopilgan ssenariy o'chirilmaydi.
