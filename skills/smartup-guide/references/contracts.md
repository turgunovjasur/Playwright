# Contracts

## Qidiruv Kalitlari

Qidiruv kalitlari: contract, contract-add, contract-list, contract-view, limit, payment-type, currency

### Contract Navigation
Tags: contract, navigation
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_forms/inventory/finansy.py:109`; [Contract view arxivi](forms/contract-view.md#screenshot-paths)
- `Финансы → Справочники → Договоры` list yo‘li inventarda
  `anor/mkf/contract_list` deb berilgan. Arxivdagi view manzili va readonly
  maydonlar [contract-view dossierida](forms/contract-view.md).

### Minimal Order Contract
Eski Group A contract yaratish uchun kod, raqam, mijoz, valyuta va summani to‘ldirgan. Aniq fixture va assertionlar — [A va B guruhlarining arxivdagi tekshiruvlari](history.md#order-va-contract-testlarining-eski-qamrovi).

### Orderda Contract Tanlash
Tags: contract, order, b-input
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_life_cycle/flow_order/flow_order_add.py::flow_order_main_page`; `flow_order_prepare_with_contract`
- Qayerda: order add main page `Договор`.
- Qoida: Order helperi `Договор` maydoniga `contract_name` qiymatini uzatadi.
- Testda ishlatish: `base.b_input(label="Договор", value=contract_name, exact=False)`.

### Contract Sum Limit
Limitdan oshgan va limit ichida qolgan order uchun tekshirilgan tarixiy testcase hamda kutilgan xato matni — [A va B guruhlarining arxivdagi tekshiruvlari](history.md#order-va-contract-testlarining-eski-qamrovi).

### Contract + Payment Type
Contract tanlangach to‘lov turini tekshirish va o‘zgartirishning eski Group A case’i — [A va B guruhlarining arxivdagi tekshiruvlari](history.md#order-va-contract-testlarining-eski-qamrovi).

### Contract Currency
Ochiq savol: boshqa valyutadagi contract tanlanganda tanlangan TMC va
productlar ro‘yxati qanday o‘zgaradi? Eski qaydda ikkala effekt kutilgan.
Ularni tasdiqlaydigan assertion yoki trace topilmadi.
[Tekshirilgan eski manba](history.md#order-va-contract-testlarining-eski-qamrovi).
