# Order regression

Har guruh o‘z tayyorlovlari va biznes qadamlarini ketma-ket bajaradi.
IDE’da `runners/test_*_runner.py` faylini pytest bilan Run qilish kifoya.
Interpreter — loyihadagi `.venv`; ish papkasi — Playwright repo ildizi.
Majburiy qo‘shimcha parametr yo‘q.

```sh
# Barcha 14 guruh
./.venv/bin/python tests/regression/run.py

# Bitta guruh: masalan, to‘lovlar
./.venv/bin/python -m pytest tests/regression/test_orders/runners/test_payments_runner.py
```

Avval muvaffaqiyatli API setup manifesti bo‘lishi kerak. Runner shu baseline’ni
avtomatik tanlaydi; server/kompaniya va fayl hashlarini tekshiradi. API setupni
regression ichida yashirin qayta yaratmaydi. Yangi muhit kerak bo‘lsa alohida:

```sh
./.venv/bin/python scripts/run_tests.py api-setup
```

## Guruhlar

| Runner | Biznes qamrovi | Test soni |
|---|---|---:|
| `test_statuses_runner.py` | Bitta orderda 6 status; summa, rezerv, fizik chiqim, qarz | 5 |
| `test_promotions_runner.py` | 10% aksiya; A10→B1; ikkala aksiya birga | 8 |
| `test_payments_runner.py` | Oddiy va bonus+skidkali orderga qisman/to‘liq to‘lov | 9 |
| `test_mandatory_runner.py` | Price/payment juftliklari, majburiy bonus, 10/9/10 chegara | 13 |
| `test_stock_runner.py` | New order 2 dona rezerv → Cancel → rezerv qaytishi | 4 |
| `test_bonus_limit_runner.py` | Ikki klient uchun umumiy limit 2; tugashi, Cancel, qayta ishlatish | 13 |
| `test_returns_runner.py` | 63 000 so‘mlik order → to‘lash → 2 dona + bonus → qolgan 8 donani qaytarish | 14 |
| `test_multi_payments_runner.py` | Ikki order, bitta 40 000 so‘mlik kirim; qarzlarni alohida yopish, 5 000 so‘m avans | 10 |
| `test_manual_discounts_runner.py` | Tayyor foiz, har donaga summa, orderga summa va bonus | 10 |
| `test_product_limit_runner.py` | Kunlik limit 10; 6 + 4 → Cancel → qolgan orderni 4 dan 10 donaga oshirish | 8 |
| `test_two_warehouses_runner.py` | Bitta order: omborlardan 2/3 dona → rezerv → edit 3/2 dona → Cancel | 10 |
| `test_mixed_promotions_runner.py` | Majburiy bonus + ixtiyoriy skidka; ON/OFF/ON va 9 → 10 dona | 8 |
| `test_auto_offset_runner.py` | SCN-002: arxiv order qarzi 14 000 → avtomatik hisob-kitobli kirim → qarz va avans 0 | 6 |
| `test_prepayment_first_runner.py` | SCN-005: orderdan oldin 20 000 avans → arxivda 14 000 qarz → aniq orderga ajratish → 6 000 avans | 7 |

Jami **125 test: 75 tayyorlov + 50 biznes**, 14 guruh. Son runnerlardagi test funksiyalaridan olingan;
amaldagi PASS/FAIL uchun run hisobotiga qarang. Smoke va eski legacy Order
runnerlari bu suite’ga kirmaydi. Limitdan oshgan orderni rad etish qamrovga
kiritilmagan — foydalanuvchi hozir faqat limit ichidagi musbat oqimni so‘ragan.

## Browser va guruh logini

Butun pytest run uchun bitta Chromium browser ishlaydi. Har UI test/attempt
alohida context, sahifa va trace oladi. Guruhning birinchi user UI testi login
qiladi; dashboarddagi dastlabki cookie/storage nusxasi faqat xotirada saqlanadi.
Keyingi test yangi contextga shu holatni oladi; user/kompaniya va filial
tasdiqlangach davom etadi. Admin tayyorlovi alohida contextda ishlaydi.

Tasdiqlangan sessiya eskirishi bir marta UI login bilan tiklanadi; server xatosi
yoki boshqa user/kompaniya aniqlanishi oddiy timeout sifatida yashirilmaydi.
Test ichidagi session-lock tiklanishi draftni saqlaydi va yangi cookielarni
guruh keshiga qaytaradi. Biznes yozuvlari avtomatik takrorlanmaydi; retry
journali va saqlangan IDlar tekshiruvi saqlanadi. Yangi pytest processidagi
retry xotira keshini olmaydi va birinchi testda qayta login qiladi.

## Ma’lumot va bog‘liqliklar

API setup xona, filial, user, valyuta, payment/kassa kabi umumiy ma’lumotni beradi.
Har guruh esa alohida sotuv TMZsi va kerak bo‘lsa bonus TMZsini yaratadi:
**katalog → narx → qoldiq → guruhning boshqa tayyorlovlari → biznes testlar**.
TMZ limiti guruhi o‘zining mavjud alohida mahsulot tayyorlovidan foydalanadi.

- Tayyorlovlar runnerda alohida testlar; biznes testi yangi TMZ yoki kirim yaratmaydi.
- Guruhlar bir-birining test natijasiga bog‘lanmagan.
- Har bir biznes testi guruhning barcha tayyorlovlari PASS bo‘lishini kutadi. Retryda yiqilgan tayyorlov bir marta qayta bajariladi. Yana yiqilsa shu guruhning biznes testlari SKIP bo‘ladi. Biznes testlari orasidagi alohida bog‘liqliklar `order_requires`da ko‘rsatiladi.
- Oddiy va aksiyali payment alohida klientlarga ega, o‘zaro mustaqil.
- Bonus limiti tugaganini tekshiruvchi ikki sibling mustaqil. Keyingi Cancel
  ikkalasi ham o‘tishini kutadi, ularning kerakli holatini buzib yubormaydi.
- Returns/multi-payment/ikki ombor/mahsulot limiti o‘zgaruvchan biznes zanjiridir.

Yangi to‘liq run o‘z fixturelarini yaratadi. **Shu running retryi o‘sha IDlarni
ishlatadi.** Umumiy API baseline `data_store.json` o‘zgartirilmaydi. Avtomatik
cleanup yo‘q; yaratilgan hujjatlar dalil sifatida saqlanadi.

`preparations.json` tayyorlovning kaliti, scope, parametrlar, IDlari va journal
havolasini saqlaydi. Kalit server/kompaniya/filial/baseline bilan chegaralangan.
Bir xil tayyorlov joriy holatda tayyor bo‘lsa qayta yaratilmaydi. Yetishmagan
qismi explicit tayyorlov testida tugatiladi. Write budjeti — birinchi urinish
va ko‘pi bilan bitta repair; budjet yozishdan oldin diskka saqlanadi.

To‘liq Order suite birinchi FAIL yoki ERROR chiqqanda to‘xtaydi. Allure shu urinishning dalillarini saqlaydi. Tuzatishdan keyin to‘liq suite yangi run sifatida birinchi guruhdan boshlanadi. Bajarilmagan testlar `suite-outcome.json` ichidagi `not_run` ro‘yxatida turadi.

## Alohida guruh uchun bir martalik retry

Barcha tanlangan guruhlar tugagach:

1. Failed test va unga bog‘liq SKIP testlar aniqlanadi.
2. Faqat ularning haqiqiy prerequisite’lari joriy holatda tekshiriladi.
3. Yetishmagan narx yoki xona bog‘lanishi uchun tegishli explicit tayyorlov
   retry rejasiga qo‘shiladi. O‘zgargan entity yoki noaniq javob avtomatik reset qilinmaydi.
4. Failed biznes testi va bog‘liq SKIP testlar o‘z runner tartibida bajariladi.
5. Retry ichidan uchinchi urinish boshlanmaydi. PASS biznes testlari qaytarilmaydi.

Kod, sana, baseline yoki dalil hashlarining mos kelmasligi avtomatik retry’ni
bloklaydi. Login/API baseline umumiy muammo bo‘lsa barcha guruhlar to‘xtaydi;
bitta biznes xatosi mustaqil guruhlarni bloklamaydi.
Foydalanuvchi to‘xtatgan run `interrupted` bo‘ladi va avtomatik retry boshlanmaydi.
Repair testining o‘z prerequisite’i yaroqsiz bo‘lsa, repair ham yozishdan oldin bloklanadi.

### Save va dublikatdan himoya

`retry-journal.json` bosqichlari:

- `intent`: Save’dan oldingi barqaror kod/TTN va operatsiya kaliti.
- `returned`: so‘rov javob qaytargan, bu hali biznes tasdig‘i emas.
- `confirmed`: haqiqiy saqlangan entity IDsi tasdiqlangan.
- `verified`: tegishli saved qiymatlar/postcondition tekshirilgan.

| Joriy qidiruv | Qaror |
|---|---|
| Aynan 1 yozuv | O‘sha ID; saved qiymatlar va bajarilmagan assertionlar tekshiriladi |
| 0 yozuv, oldin Save yuborilmagan | Bir marta create |
| 0 yozuv, lekin oldingi Save natijasi noaniq | Qayta Save yo‘q; kech commit ehtimoli sabab BLOCKED |
| Ko‘p yozuv, HTTP xato yoki noaniq javob | Yozish bloklanadi |

Order retryida Add’dan oldin mavjud order aniqlanadi. Cashin raqami, return
TTN/source, katalog kodi/nomi, kirim raqami kabi exact belgilar ishlatiladi.
UI yozish ruxsati endpoint va target identity bilan cheklangan.

**Pul:** klient balansining o‘zi saqlangan transaction dalili emas. Oldingi
noaniq offset uchun qarz o‘zgarmagan bo‘lsa ham ikkinchi POST yuborilmaydi.
Exact transaction adapteri bo‘lmagan holat aniq BLOCKED qoladi. Cashin IDsi,
klient/summa/posted holati esa qayta o‘qilib, qayta kirim qilinmaydi.

**Qoldiq:** yangi orderdan oldin own TMZning hozirgi erkin qoldig‘i o‘qiladi.
Yetishmasa “kerak 10, erkin 7” sababi beriladi; biznes xatosi kirim bilan yashirilmaydi.
Rezerv/chiqim/qaytishning biznes assertionlari UI orqali bajariladi.
Returns guruhi ikkita kirim partiyasini tayyorlaydi; qaytarish barcha lotlarga
taqsimlanadi va har lotning miqdori/summasi, jami, bonus, stock va avans tekshiriladi.

Oldingi bosqich allaqachon o‘zgargan bo‘lsa, faqat oldin tasdiqlangan checkpoint
ishlatiladi. Tekshirilmagan tarixiy assertion avtomatik PASS qilinmaydi.
Har qanday qisman bajarilgan test albatta tiklanishi kafolatlanmaydi;
noaniq yozuvni takrorlash o‘rniga sababli BLOCKED saqlanadi.

## Allure va debug

Har guruh ichida **1 · Setup** va **2 · Biznes flow** bo‘limlari bor.
Qidiruv maydoniga masalan `SCN-002`, `SCN-005` yoki `Ombor qoldig‘i` kiriting.
↻ belgisi test shu suite davomida ikkinchi marta bajarilganini bildiradi.
Setup sabab biznes qadamiga yetilmagan bo‘lsa, test tafsilotlarida bloklagan qadam ko‘rsatiladi.

Bitta hisobotda dastlabki va qayta urinish saqlanadi. Testning oxirgi statusi
asosiy natija, dastlabki xato esa urinishlar tarixida ko‘rinadi. `Urinish`
parametri 1/2, har bir urinishning alohida trace/rasm/vaqt va sababini ko‘rsatadi.

`test-results/runs/<run-id>/` ichida:

- `run.json`, har case `result.json`, `case-data.json`: actual natija va IDlar;
- `preparations.json`: tayyorlovning yaratilgani/qayta ishlatilgani;
- `retry-readiness.json`: joriy tayyorlik va explicit repair qarori;
- `retry-readiness-error.json`, `retry-error.json`, `reporting-error.json`: tegishli yakuniy bosqichda xato bo‘lsagina yoziladigan diagnostika;
- `retry-plan.json`: tanlangan testlar, dependency va source hashlar;
- `suite-outcome.json`: dastlabki/retry/yakuniy natija va exit code;
- `allure-report/`: faqat shu running yakuniy hisoboti.

Original raw resultlar o‘zgartirilmaydi; retry alohida papkaga yoziladi,
Allure uchun ikkala urinishdan nusxa birlashtiriladi.
Suite tugaganidan keyingi tayyorlov tekshiruvi alohida read-only Python jarayonida
bajariladi. U test yoki yangi setup boshlamaydi. Bu yopilgan Allure testcase’iga
API ilovasini biriktirish xatosini oldini oladi; retry xatosi dastlabki hisobotni yashirmaydi.

## Mexanizmni alohida tekshirish

```sh
./.venv/bin/python -m pytest tests/regression/test_orders/verification/test_recovery_runner.py
```

Bu 16 testli opt-in runner Save oldidan, server saqlagach lokal IDdan oldin, IDdan keyin,
UI order va cashin saqlangach ataylab uzilish beradi; suite yakunidagi retry
mavjud entityni topishi va yangi dublikat yaratmasligini tekshiradi. Room
attachmenti yarim bajarilishi va 6 000 so‘m to‘langach faqat qolgan 8 000 so‘mni
to‘lash ham tekshiriladi. Nazoratli uzilishlar oddiy 125 testli suite’da yoqilmaydi;
ular mahsulot bugi deb hisoblanmaydi. Bu qamrov tavsifi; actual natijani run
hisobotidan ko‘ring — test yozilgani uning PASS ekanini bildirmaydi.

## Eski product_limit manual resume

```sh
./.venv/bin/python tests/regression/run.py --resume-run <tugagan-run-id> --group product_limit
```

Faqat qo‘llab-quvvatlangan bosqichlar: `test_06_cancel_first_order` va
`test_07_reuse_released_limit`; oldingi prerequisite’lar PASS, sana/baseline/
limit/order/rezerv joriy holatda mos bo‘lishi shart. Bu avtomatik retrydan
alohida yo‘l. `-k`, `--lf` yoki leaf test bilan dependencylarni chetlab o‘tmang.
