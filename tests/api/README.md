# Smartup API setup

Mavjud UI setupning HTTP orqali bajariladigan alohida varianti. Testlar browser,
`page` fixture yoki UI loginni ishlatmaydi. Login cookie sessiyasi ham HTTP orqali
olinadi. Asosiy runner: `setup/test_0_setup_runner.py`.

API konfiguratsiyasi `pytest-playwright` pluginini o'chiradi: uning avtomatik
output cleanup fixture'i UI natijalari yoki API baseline'ni tozalamaydi.
Har run faqat tanlangan API Allure natijalar papkasini yangilaydi.
`--confcutdir=tests/api` parent `tests/conftest.py`dagi UI fixture va report
hooklarini ajratadi. Standart UI collection API papkasini yig'maydi.

Repo rootidan ishga tushirish:

```bash
./.venv/bin/python -m pytest -c tests/api/pytest.ini tests/api/setup/test_0_setup_runner.py
```

Konfiguratsiya mavjud loyiha tartibida: root `.env` ustun; u bo'lmasa
`--url`, `--company-code`, `--company-password`, `--new-code` va environment.
`USER_PASSWORD` majburiy. To'liq yangi setup uchun `NEW_CODE=1` ishlatiladi.
Parol yoki cookie kodga va API Allure attachmentlariga yozilmaydi.
Parol tasdiqlangach login qayta yuboriladi; browser networkdagi kabi cookie
jar saqlanadi, alohida server sessiyasi ochilmaydi.

API natijalari:

- `test-results/api/data_store.json`: API baseline va yaratilgan IDlar.
- `test-results/api/allure-results/`: har bir qadam va HTTP statuslari.
- `--api-data-file /absolute/path/baseline.json`: alohida API baseline yo'li.

UI `test-results/data/data_store.json` fayli o'zgarmaydi. API suite UI baselinega
qaramaydi. API yaratgan data serverda qoladi. Filial, user, mahsulot va aksiya
nomlari UI setupdagi `*-pw{code}` ko'rinishida bo'ladi. Birinchi xatodan keyin
qolgan setup qadamlari dependency sabab skip qilinadi. Parallel workerlar bilan
run qilish qo'llanmaydi.

Yakka qadam uchun `.env`da `NEW_CODE=0` qilib, oldingi API baseline'dan foydalaning:

```bash
./.venv/bin/python -m pytest -c tests/api/pytest.ini tests/api/setup/test_24_balance.py
```

Qayta bajarilgan create qadamlari avtomatik deduplication yoki cleanup qilmaydi;
yangi to'liq setup uchun yangi code ishlating.

## API setupdan keyin group testlar

Mavjud company rejimida API setup group testlarga kerak bo'lgan user, filial,
room, robot, klient, mahsulot, narx va ombor qoldig'ini yaratadi. ID va `code`
har run uchun yangi bo'ladi; biznes preconditionlar UI setupdagi kabi.
Group-0 va Visit consumerlari o'qiydigan setup kalitlari API baseline'da bor.

Hozir group testlar `test-results/data/data_store.json`ni o'qiydi. API natijasi
avtomatik shu faylga ko'chirilmaydi. API runner to'liq muvaffaqiyatli tugagach,
aynan shu server/company va parol sozlamalari bilan baseline'ni tanlang:

```bash
mkdir -p test-results/data
cp test-results/api/data_store.json test-results/data/data_store.json
```

Bu oldingi umumiy baseline'ni almashtiradi. API run failed yoki qisman bajarilgan
bo'lsa ko'chirmang. Keyin group-only targetni ishga tushiring: grouplar
`NEW_CODE` qiymatidan qat'i nazar umumiy baseline code'ni oladi, `.env`ni
almashtirish shart emas (`setup-*` targeti UI setupni qayta bajaradi):

```bash
./.venv/bin/python scripts/run_tests.py groups
# yoki faqat bitta group:
./.venv/bin/python scripts/run_tests.py group-0
./.venv/bin/python scripts/run_tests.py group-visit
```

API setup faqat tayyorlovchi UI qadamlar o'rnini bosadi. Group ichidagi UI
sahifalari ishlamayotgan bo'lsa, API baseline o'sha UI xatosini tuzatmaydi.
API setup → UI group zanjiri 2026-10-19 kuni live tekshirildi: Group-0 4/4,
Visit 2/2 passed. Dastlab Report 5 passed, 1 failed; aynan shu CisLink failure UI
setup zanjirida ham takrorlandi. CisLink birinchi operatsion filialni tanlagan va
o'sha filialda `price_types` javobi bo'sh bo'lgan. Keyingi tuzatishda CisLink
`filial_name` va `price_type_name_UZB`ni umumiy baseline'dan oladigan qilindi;
API baseline bilan yakka qayta run: 1 passed, 43.91 s.
Group-only run `.env`dagi `NEW_CODE=1` bilan API baseline code'ni qayta ishlatdi.

## Qamrov

| UI setup qadam | API amali va tekshiruvi |
|---|---|
| 01–06 | Legal person, filial, room, robot, natural person va user yaratish; view orqali tekshirish |
| 07–09 | User form/report/invoice/external-system ruxsatlari, Admin rol funksiyalari, barcha formalarga ruxsat |
| 11–12 | ERP users litsenziyasini ulash; boshlang'ich parolni tasdiqlash va qayta login |
| 13–17 | UZS/USD narx turlari va room bog'lanishi, USD kursi, 4 to'lov turi, TMC to'plami |
| 18–20 | Ikki mahsulot, 7000 UZS/1 USD narxlari, client yaratish va qayta o'qish |
| 21–24 | Roomga kataloglar va `Акция` narx turini ulash, ombor, ikki boshlang'ich qoldiqni o'tkazish, har mahsulotdan 100 dona tekshirish |
| 25–29 | Besh aksiya; saqlangan chegirma/bonus mahsuloti va shart qiymatlarini qayta o'qib tekshirish |

Joriy capture mavjud company uchun olingan. `00 Company` mavjud company rejimida
UI suite kabi deselect qilinadi. `COMPANY_CODE=1` uchun company create/security
requestlari hali capture qilinmagan: bu rejim aniq xato bilan to'xtaydi.

`10 Buy License` `smartup.online`da UI setup kabi skip qilinadi. Boshqa serverdagi
litsenziya xaridi uchun ham capture kerak; bu amal taxminiy endpoint bilan
bajarilmaydi. `11 Attach License` UI setupdagi kabi tanlangan `ERP users`
litsenziyasidan oldingi userlarni ajratib, yangi setup userni ulaydi.

## Requestlar manbasi

`contracts.json` — browser networkdan olingan save payloadlari. Entity IDlari,
code, sanalar va user paroli runtime qiymatlari bilan almashtiriladi. UI-only
region katalogi bo'shatilgan; legal-person guruhlari esa joriy form modelidan
olinadi. Companyga tegishli currency, role va measure IDlari query orqali topiladi.

Dastlabki manba:
`outputs/online-regression-20261018/canonical-traces/preserved-setup-session-trace.zip`
ichidagi `trace.network`; `source_request_index` nolga asoslangan snapshot indeksi.
Bu trace runtime dependency emas. Testlar arxivga murojaat qilmaydi.

`client.py` umumiy `BaseAPI` transportini qayta ishlatadi va Biruni model/table
formatlarini ochadi. `state.py` faqat API baseline va sessiyalarini boshqaradi.
Biznes qadamlari raqamlangan leaf fayllardagi `run_*` funksiyalarida; runner
faqat ularni ketma-ket chaqiradi.

## Live tekshiruv

2026-10-19 kuni, `tests/api`ga ko'chirishdan oldin, `smartup.online` mavjud
company rejimida:

- UI setup: `28 passed, 1 skipped, 1 deselected`, 1298.17 soniya.
- API setup: `28 passed, 1 skipped, 1 deselected`, 51.89 soniya.

Bu ikki run orasida API taxminan 25 marta tezroq ishladi. UI run networkidagi
21 save request endpointi va payload kalitlari shablonlar bilan solishtirildi.
API tekshiruvlari serverdan qayta o'qilgan qiymatlar, 100 dona qoldiq,
500 000 UZS provodka va beshta aksiya shartlarini ham qamrab oladi.

`tests/api`ga ko'chirilgach, shu kuni ikki to'liq zanjir ketma-ket run qilindi
(Forms ishga tushirilmadi):

| Zanjir | Natija | Vaqt |
|---|---|---|
| UI setup → Group-0 → Visit → Report | 39 passed, 1 failed, 1 skipped, 1 deselected | 1743.43 s |
| API setup | 28 passed, 1 skipped, 1 deselected | 54.23 s |
| API baseline → Group-0 → Visit → Report | 11 passed, 1 failed | 425.38 s |

Ikkala group runidagi 12 test natijasi bir xil. Yagona failure:
`test_report_01_cislink` — `Тип цены` dropdownida tanlanadigan qiymat yo'q.
Har ikki tracedagi `cislink_template+add:price_types` javobi HTTP 200,
`{"count":0,"data":[]}`. Setupga tegishli 12 ta baseline maydoni group runidan
keyin saqlangan. Run tafsilotlari:
`outputs/setup-api-groups-20261019-1210/verification.md`.
