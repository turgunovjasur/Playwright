# Joriy Order testlari

Barcha guruhlar: [../run.py](../run.py). Bitta guruh: [runnerlar ro‘yxati](runners/README.md).

| Papka/fayl | Vazifasi |
|---|---|
| `runners/` | Guruhlarning pytest testlari va bog‘liqliklari. [SCN-001](runners/test_statuses_runner.py) ichida tayyorlov va biznes qadamlari ketma-ket berilgan. |
| `setup_cases/` | Ma’lumot tayyorlovchi testcase qadamlari |
| `business_cases/` | Biznes qadamlari va assertionlar, mavzular bo‘yicha |
| `helpers/flows/` | Takror ishlatiladigan UI amallari |
| `helpers/preparations/` | Klient/aksiya tayyorlov yordamchilari va resurs readiness |
| `groups.py` | SCN kodi, guruh nomi va ishga tushirish tartibi |
| `helpers/ordering.py` | Testlar tartibi va bog‘liqliklarini tekshirish |
| `helpers/reporting.py`, `helpers/run_overview.py` | Allure taqdimoti |
| `helpers/group_auth.py`, `helpers/auth_recovery.py` | Login va sessiyani tiklash |
| `helpers/models.py` | Test konteksti va ma’lumot modeli |
| `conftest.py` | Fixture va pytest hooklar |
| `verification/` | Nazoratli uzilishlar runneri; asosiy suite tarkibiga kirmaydi |

Guruhdagi birinchi brauzer testi to‘liq login qiladi. Keyingi test saqlangan sessiya bilan o‘ziga kerakli sahifani ochadi. Masalan, SCN-001 status testida avval klientning «Взаиморасчеты с клиентами» sahifasi ochiladi. Sessiya muddati o‘tsa, test qayta login qilib davom etadi.

Test kimga bog‘liqligi runnerdagi `@pytest.mark.order_requires(...)`da yozilgan.
Kerakli prerequisite o‘tmasa test sabab bilan bajarilmaydi. Mustaqil setup
xatosi boshqa mustaqil setupni to‘xtatmaydi.

Guruhlar bir-birining testcase natijasiga bog‘lanmagan, lekin umumiy API baseline
kerak. Har guruh o‘z ma’lumotini tayyorlaydi. Retry mavjud ID va jurnalni tekshiradi;
yozuvlar avtomatik o‘chirilmaydi.

To‘liq yo‘lko‘rsatkich: [regression README](../README.md).
