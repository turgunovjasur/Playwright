# Order regression

5 ssenariy, 17 leaf fayl va 18 alohida pytest testcase. ORD-08 ning ikkita
parametri ham o'z ma'lumotlari va browser contextiga ega. Runner —
[test_0_orders_runner.py](test_0_orders_runner.py); u umumiy regression runnerga ham ulangan.

| Ssenariy | Testcase | Tekshiriladigan natija |
|---|---|---|
| Order yaratish va tahrirlash | ORD-01 | Draft yaratish, qty2→3, bir xil ID, TTN/izoh va 200→300 USD |
| | ORD-02 | Nusxaning yangi IDsi, source/copy mustaqilligi, saqlanmagan editni tashlash |
| | ORD-03 | Bo'sh order, zero quantity va to'lov turisiz New validatsiyasi |
| | ORD-04 | Satrning per-unit −1 chegirmasi va bir martalik order −1: 200→198→197 |
| Podbor va Excel import | ORD-05 | Tanlash, olib tashlash, qayta qo'shish, qty3/300 USD |
| | ORD-06 | Valid XLSX: PI/qty/Y → preview → order → saved/edit qty2/200 USD |
| | ORD-07 | Faylsiz, empty, unknown ID qator xatosi, manfiy quantity saqlanmasligi |
| | ORD-08a | Duplicate qty1+2: preview, transfer va saved quantity/300 USD saqlanishi |
| | ORD-08b | Xuddi shu faylning faqat birinchi qatori: qty1/100 USD |
| Order statuslari | ORD-09 | Draft→New→Processing→Waiting→Shipped→Delivered; stock va saldo |
| | ORD-10 | Cancel, active/canceled ro'yxatlar, Restore Draft; rezerv/saldo qaytishi |
| | ORD-11 | Archive→Restore Delivered→Cancel; qarz/open order va physical stock |
| Order aksiyalari | ORD-12 | Own qty3–5 bonus1, chegaralar va optional tanlash |
| | ORD-13 | Own summa300–500 /10% aksiya, chegaralar va saved270 USD |
| | ORD-14 | Own siklik har3→bonus1, qty6→bonus2; New/Cancel/Restore rezervi |
| To'lov, qaytarish va report | ORD-15 | Cashin→Post→exact allocation→reversal→Unpost |
| | ORD-16 | Own reason va source orderdan Return; Draft/Sent/Archive/reversal |
| | ORD-17 | Order view va Накладная №4 HTML: ID konteksti, SKU, qty, price, total |

## Kodni o'qish va kengaytirish

Har leafda `run_<case>(page, order_case, ...)` biznes qadamlarni va expected
natijalarni ko'rsatadi. Shu fayldagi `test_*` uni alohida ishga tushirish uchun.
Runner classlari ssenariylarni guruhlaydi; ularning `test_*` metodlari tegishli
`run_*` funksiyani chaqiradi. Ichma-ich funksiya yoki ichki pytest runner yo'q.

Umumiy qatlamlar:

- `tests/regression/conftest.py::order_case`: har testcase uchun fresh login va setup/teardown.
- `order_data.py`: shu case'ning mijoz/SKU nomlari, IDlari va cleanup registri.
- `order_environment.py`: own mijozni roomga ulash, 2 SKU/narx, har biriga50 dona kirim; yakuniy cleanup.
- `order_finance.py`: allocation, Return va cashinni tartib bilan qaytarish.
- `tests/smoke/test_life_cycle/flow_order/order_regression.py`: takroriy order navigatsiyasi, ID bilan qayta ochish, status amali, stock/saldo o'qish.
- Shu papkadagi `order_import.py` va `order_summary.py`: takroriy mapping hamda summary katagini topish.

Yangi case qo'shilganda alohida leaf yarating, biznes qadam va aniq expected
qiymatlarni `run_*` ichida yozing, keyin mos scenario classiga wrapper qo'shing.
Boshqa testcase saqlagan IDni olmang. Yangi hujjatni o'z cleanup registriga
kiriting. Ko'p testda takrorlanadigan to'liq UI ketma-ketligigina flowga ajratiladi.
Mavjud `AutoBasePage` APIlari ishlatilgan; umumiy BasePage implementatsiyalari
o'zgartirilmagan.

## Mustaqillik va cleanup

Yagona umumiy dependency — regression setup yaratgan user/filial/room/staff,
price type, product set va payment type baseline. Products regression natijasi
Order testlariga dependency emas. Har case UUIDli alohida mijoz va SKUlar oladi.
Bir domain testcase xatosi keyingisini skip qilmaydi; umumiy setup yiqilsa unga
bog'liq caselar bloklanadi. Standart `--maxfail=0` saqlangan.

Cleanup faqat own klient/ID/nomlar bilan ishlaydi. Save'dan keyingi readback
xatosida ham unique klient bo'yicha orderlar uch ro'yxatdan qayta topiladi.
Avval allocation/Return/cashin, so'ng order bekor qilinadi; aksiya nofaol,
kirim unposted, own mijoz roomdan ajratilgan holatga keltiriladi. Finance yoki
order rollback xatosida bog'liq kirim bekor qilinmaydi. Xato Allure'ga yozilib,
teardown failure sifatida ko'rinadi.

Mijoz, SKU, narx va Return reason katalog yozuvlari hamda bekor qilingan
hujjatlar audit uchun qoladi. Import mappingi oldindan olinib tiklanadi.
Grid ustun/qidiruv sozlamalari va action status filtri test userida saqlanishi
mumkin. Shu user bilan caselarni ketma-ket ishlating; bir userda parallel
`xdist` run qo'llab-quvvatlanmagan.

## Ishga tushirish

Mavjud mos baseline bilan (`NEW_CODE` qiymatidan qat'i nazar code baseline'dan olinadi):

```sh
./.venv/bin/python scripts/run_tests.py regression-orders
```

Yangi regression setup bilan:

```sh
./.venv/bin/python scripts/run_tests.py setup-regression-orders
```

Bitta testcase yoki scenario class uchun runnerning pytest node IDsi yoxud
leaf faylini tanlash mumkin. Runner va uning leaflarini birga tanlash duplicate
run sababli bloklanadi. URL/credentiallar loyihaning mavjud `.env`/CLI
mexanizmidan olinadi; bu kodda hardcode qilinmagan.

## Tekshirish holati va chegarasi

Implementatsiya statik review, Python AST, import/API tekshiruvlari va
`git diff --check` bilan tekshirildi. Yangi testlar va pytest collection bu
ish davomida run qilinmadi; live passing natijasi hali yo'q. Qo'lda olingan
oldingi natijalar yangi autotestlar o'tganining isboti emas.

Ushbu paket yuqoridagi oqimlarni qoplaydi. Discount preset/ustama katalogi,
QQS siyosati, report Excel formati, visit va barcha grant kombinatsiyalari
uchun alohida testcase kerak bo'ladi.
