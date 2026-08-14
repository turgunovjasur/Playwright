# Client Payment

## Quick Lookup

- Form slug: `client-payment`
- Navigation: `Финансы > Основное > Оплаты от клиентов`
- List URL pattern: `*/trade/tcs/cashin_list`
- Add URL pattern: `*/trade/tcs/cashin+add`
- List heading: `Оплаты от клиентов`
- Add heading: `Оплата от клиента / Создание`
- Related dossier: [client-offset.md](client-offset.md)

## Screenshot Paths

- N/A

## Known Locators

### Add form fieldlari va actionlari
Tags: client-payment, cashin, locator, b-input, posting
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `*/trade/tcs/cashin+add`.
- Qoida: toolbar actionlari `Сохранить` (`save()`), `Провести`
  (`savePost()`) va `Закрыть`. Asosiy fieldlar: `Номер оплаты`
  (`d.cashin_number`), required `Дата и время` (`d.cashin_time`), required
  `Валюта` (`d.currency_name`), required `Сумма` (`d.amount`), required
  `Тип оплаты` (`d.payment_type_name`), required `Клиент`
  (`d.client_name`), shuningdek `Проект`, `Договор`, `Инкассатор`,
  `Торговый представитель` va `Примечание`.
- Testda ishlatish: fieldlarni label orqali `BasePage` bilan boshqar;
  client balansiga ta'sir qilishi kerak bo'lgan scenario `Провести` actionini
  ishlatib, natijani settlement sahifasidagi summalar bilan tekshirsin.
- `Провести` bosilganda `Провести?` confirmi chiqadi. Muvaffaqiyatli
  postdan keyin listga qaytmaydi: `Оплата от клиента / Создание`
  (`*/trade/tcs/cashin+add`) yangi, tozalangan forma holatida ochiq qoladi.
- Testda ishlatish: confirmdan keyin `cashin_list`ni kutma; avval yangi add
  forma ochiq qolganini tekshir, keyin natijani settlement sahifasida
  tasdiqla.

### Naqd to'lov kassasi
Tags: client-payment, payment-type, cashbox, conditional-field
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: client payment add formasi.
- Qoida: `Тип оплаты = Наличные деньги` tanlanganda required `Касса`
  (`d.cashbox_name`) maydoni paydo bo'ladi. Joriy setup baseline'da
  `Основная касса` optioni mavjud.
- Testda ishlatish: payment type tanlangandan keyin `Касса`ni to'ldir;
  undan oldin conditional fieldni qidirmang.

## Flow And Tests

- Mavjud reusable flow: N/A
- Mavjud group-0 test:
  `tests/smoke/test_groups/test_a_grup/test_03_post_client_payment.py`.

## Business Rules

### Client balansi va ochiq order summasi
Tags: client-payment, balance, debt, order
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: client tanlangandan keyingi `Баланс` view fieldi.
- Qoida: payment formadagi `Баланс` clientning hisobdagi qarzini ko'rsatadi;
  settlement listidagi alohida `Заказ` summasi bu fieldga qo'shilmaydi.
  Live holatda `Задолженность = 7 000` va `Заказ = 21 000` bo'lganda payment
  form `Баланс = -7 000` ko'rsatdi.
- Testda ishlatish: to'lov summasini ochiq order totalidan emas,
  `Задолженность`/payment form `Баланс` qiymatidan ol.

### Payment ichidagi avtomatik o'zaro hisob-kitob
Tags: client-payment, auto-offset, checkbox, settlement
Status: live-ui-confirmed
Verified: 2026-07-31
Source: live UI
- Qayerda: `Провести взаимозачёт` checkboxi.
- Qoida: checkbox default o'chiq. Yoqilganda `С учётом консигнации`,
  `По договору`, `По типу оплаты`, `По проекту` optionlari ko'rinadi;
  live defaultda konsignatsiya o'chiq, qolgan uchtasi yoqilgan.
- Testda ishlatish: alohida `Взаиморасчеты с клиентами` bosqichini tekshirish
  uchun payment testida `Провести взаимозачёт` o'chiq qolsin.

## Known Issues

- `Сохранить` va `Провести` ikkalasi mavjud. Balansga ta'sir qiladigan
  smoke scenario draft-save bilan tugamasin; post natijasini downstream
  settlement summalari orqali tekshirsin.
- Bir nechta `b-input` bir xil `Поиск...` placeholderiga ega; locatorni
  label yoki aniq `b-input` scope'i bilan toraytirish kerak.
