# Regression: qayerdan boshlash kerak?

**Joriy 14 ta Order guruhining asosiy runneri — [run.py](run.py).**
Guruhlar ro‘yxati va tartibi [ordering.py](test_orders/helpers/ordering.py)dagi
`GROUP_RUNNERS` va `GROUP_NAMES`da. Suite 125 testcase’dan iborat.

```text
regression/
├── run.py                        ← ASOSIY RUNNER: barcha 14 Order guruhi
├── conftest.py                   ← umumiy pytest fixture va hooklar
├── test_orders/
│   ├── runners/                  ← GURUH RUNNERLARI: tartib + dependency
│   ├── setup_cases/              ← TESTLAR: katalog, narx, qoldiq, klient, aksiya
│   ├── business_cases/           ← TESTLAR: to‘lov, status, qaytarish, limit...
│   ├── helpers/                  ← YORDAMCHILAR: flow, login, model, hisobot
│   ├── verification/             ← mexanizmni tekshiruvchi alohida runner
│   └── conftest.py               ← Order fixturelari va retry/dependency hooklari
├── helpers/                      ← umumiy runtime, retry, readiness, sessiya
└── legacy/                       ← ESKI suite; joriy 125 taga kirmaydi
```

## Men nimani ochaman?

| Maqsad | Fayl yoki papka |
|---|---|
| Barcha joriy guruhlarni boshlash | [run.py](run.py) |
| Guruhni tanlash, uning testlarini ko‘rish | [runners/](test_orders/runners/README.md) |
| Test kimga bog‘liqligini ko‘rish | Runnerdagi test tepasidagi `@pytest.mark.order_requires(...)` |
| Setupning qadamlarini o‘zgartirish | [setup_cases/](test_orders/setup_cases/) |
| Biznes testining qadam va expected natijasini o‘zgartirish | [business_cases/](test_orders/business_cases/) |
| Takror ishlatiladigan UI amallarini topish | [helpers/flows/](test_orders/helpers/flows/) |
| Login/context/fixturelarni tushunish | [Order conftest.py](test_orders/conftest.py), [group_auth.py](test_orders/helpers/group_auth.py) |
| Retry qarorini ko‘rish | [immediate.py](helpers/retry/immediate.py) |
| Dependency yoki guruhlar tartibini boshqarish | [ordering.py](test_orders/helpers/ordering.py) |
| Allure ko‘rinishini boshqarish | [reporting.py](test_orders/helpers/reporting.py), [run_overview.py](test_orders/helpers/run_overview.py) |
| Oldingi regression suite | [legacy/](legacy/README.md) |

## Runner, test va helper farqi

**Runner** testlar tartibini belgilaydi. Uning `test_*` funksiyasi dependency va
report nomiga ega, tegishli `run_*`ni chaqiradi.

**Testcase** — setup yoki biznes tekshiruvining qadamlari va kutilgan natijasi.
Ular `setup_cases/` va `business_cases/` ichida. Bu yerdagi `run_*` funksiyalarni
runner chaqiradi; ishga tushiriladigan `test_*` funksiyalar `runners/` ichida.

**Helper** — testlar qayta ishlatadigan kod. Uni alohida test sifatida Run qilish
kerak emas. `conftest.py`ni pytest o‘zi yuklaydi.

Misol: [to‘lov runneri](test_orders/runners/test_payments_runner.py) →
[to‘lov testcase’i](test_orders/business_cases/payments/test_partial_full_payment.py) →
[hisob-kitob amallari](test_orders/helpers/flows/settlement.py).

## Ishga tushirish yo‘llari

Buyruqlar repo ildizidan bajariladi. Bu qo‘llanma; faylni o‘qish testni boshlamaydi.

```sh
# Joriy barcha 14 Order guruhi
./.venv/bin/python tests/regression/run.py

# Faqat SCN-003 — To‘lovlar
./.venv/bin/python -m pytest tests/regression/test_orders/runners/test_payments_runner.py
```

Butun `tests/regression/` papkasini birga Run qilmang: ichida joriy suite, eski
suite va verification bor. Ular bitta target emas. API baseline avval tayyor
bo‘lishi kerak; `run.py` uni yashirincha yaratmaydi.

## Ushbu branchdagi retry chegarasi

Allure’da testni ochganda `Bog‘liq test` maydonlari uning bevosita dependencylarini
test kodi va nomi bilan ko‘rsatadi. Bog‘liqlik bo‘lmasa bu alohida yoziladi.
Yakuniy `Qisqa QA natijasi`da dependencylar va mavjud bloklanish sababi ham chiqadi.
`Execution`da setup, test va teardownning qayd etilgan Allure steplari saqlanadi;
`Allure qadamlari` ilovasida ichki qadamlar, status va davomiylik ham bor.
Boshlanmagan qadamlar taxmin qilib qo‘shilmaydi. Eski runlarda dependency yoki
qadam dalili bo‘lmasa bu ochiq ko‘rsatiladi; eski hisobot avtomatik qayta yozilmaydi.

Dependency boshqaruvi barcha 125 testga tegishli. Avtomatik bitta retry hozircha
SCN-003 dagi 9 test uchun yoqilgan. `--order-retries=0` uni o‘chiradi.
`--maxfail=0` mustaqil testlarni davom ettiradi; boshqa qiymat yakuniy xatolar limitidir.
Bu hujjat PASS hisoboti emas; runtime tekshiruvi alohida bajariladi.

Ko‘chirish source hashni o‘zgartiradi. Eski retry/resume dalillari qayta
yozilmaydi; moslik tekshiruvlari saqlanadi.
