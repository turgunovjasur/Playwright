# Contracts

## Qidiruv Kalitlari

Tags: contract, contract-add, contract-list, contract-view, limit, payment-type, currency

### Contract Navigation
Tags: contract, navigation
- Qayerda: `Финансы > Договоры`
- URLlar:
  - list: `*/anor/mkf/contract_list`
  - add: `*/anor/mkf/contract+add`
  - view: `*/anor/mkf/contract_view`
- Testda ishlatish: listda heading `Договоры`, add/view URL va `b-page` content tekshiriladi.
- Form dossier: contract view uchun [forms/contract-view.md](forms/contract-view.md) o'qi.

### Minimal Order Contract
Tags: contract, precondition, a-group
- Qayerda: contract add forma.
- Qoida: Contractlar order testlari uchun precondition bo'lishi mumkin.
- Minimal qiymatlar:
  - `Код`: `contract_code_{random}`
  - `Номер`: session `code`
  - `Название`: Faker company + `order contract-pw{code}`
  - client turi: `Физическое лицо`
  - `Физическое лицо`: `natural_client-pw{code}`
  - `Валюта`: `Узбекский сум`
  - `Сумма договора`: `500000`
- Testda ishlatish: `Код` input birinchi qidiriladi; `Номер` bilan almashtirilmaydi. Listda `contract_code` bilan qidir, viewda code/name/client/currency/amount tekshir.
- Data: `contract_code` va `contract_name` `data_store.json` ga saqlanadi.

### Orderda Contract Tanlash
Tags: contract, order, b-input
- Qayerda: order add main page `Договор`.
- Qoida: Order formasidagi `Договор` maydoni contract code bilan emas, `contract_name` bilan tanlanadi.
- Testda ishlatish: `BasePage.b_input("Договор", value=contract_name, exact=False)`.

### Contract Sum Limit
Tags: contract, limit, order, error
- Qayerda: contract add `Сумма договора`, order save.
- Qoida: Oddiy sum limit contract tanlansa, order total amount contract limitdan oshmasligi kerak.
- Testda ishlatish: 500000 contract bilan 700000 order save qilinganda Biruni error chiqishi va order saqlanmasligi tekshiriladi.
- Error text: `Сумма заказа превышает сумму остатка по договору`, `Сумма остатка по договору: 500000`, `сумма заказа = 700000`.

### Contract + Payment Type
Tags: contract, payment-type, order, auto-fill
- Qayerda: contract add `Типы оплат`.
- Qoida: Contract `Сумма договора = 500000` va `Типы оплат = Перечисление` bilan yaratilsa, orderda contract tanlangandan keyin `Тип оплаты` auto-fill `Перечисление` bo'ladi.
- Muhim: `Тип оплаты` auto-fill faqat qulaylik; user uni o'zgartirishi mumkin. Payment type o'zgarsa ham order ishlashi kerak, faqat contract sum limit tekshiriladi.
- Testda ishlatish: payment type value inputda turadi, `#kt_content` text ichiga kirmasligi mumkin. Label bo'yicha input value tekshir.

### Contract Currency
Tags: contract, currency, product-filter, order
- Qoida: Contract qaysi valyutada yaratilgan bo'lsa, orderda contract tanlanganda productlar contract valyutasi bo'yicha filterlanadi.
- Qoida: Agar orderda product tanlangan bo'lsa va contract boshqa valyutali contractga almashtirilsa, tanlangan productlar o'chib ketadi.
- Testda ishlatish: currency case yozilganda product grid/input reset bo'lishi alohida tekshirilsin.
