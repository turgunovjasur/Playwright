# CisLink integration report (`trade/rep/integration/cislink`)

### Joriy main forma
Status: trace-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `test-results/traces/tests_smoke_test_groups_test_report_grup_test_0_group_runner.zip`; `tests/smoke/test_groups/test_report_grup/test_01_cislink.py`
- Qoida: `smartup.online`da CisLink template-based inline formaga migratsiya qilingan; report endi global skip qilinmaydi.
- Heading doim `CisLink(7008)`; `7008` dynamic qiymat emas. Report menyuda yo'q va joriy session tokeni bilan direct URL orqali ochiladi.
- Main tugmalar: `Сформировать`, `Сформировать(MQ)`, `Шаблоны`, `Закрыть`. `Настройки` tugmasi yo'q.
- Main maydonlar: `Шаблон*`, `Тип периода`, `До*`.
- `Последние 45 дней` default checked, `Пользовательский период` unchecked, `До` default bugungi sana.
- Aktiv template bo'lmasa `Шаблон` bo'sh qolishi live UI'da tasdiqlangan, lekin bu doimiy default invariant emas. Test boshlang'ich bo'sh qiymatni assert qilmaydi; har bir run uchun yangi unique template yaratadi.

### Template list va create forma
Status: trace-confirmed
Verified: 2026-08-20
Source: live Chromium UI; `test-results/traces/tests_smoke_test_groups_test_report_grup_test_0_group_runner.zip`; `tests/smoke/test_groups/test_report_grup/test_01_cislink.py`
- `Шаблоны` → `cislink_template_list`; list tugmalari `Добавить` va `Закрыть`, grid ustunlari `Название` va `Статус`.
- `Добавить` → `cislink_template+add`; required maydonlar: `Название`, `Значение поля "manfid"`, `Характеристики`, `Продуктовое направление`, `Тип цены`.
- `Значение поля "manfid"`ning joriy legacy DOM matni literal backslashlar bilan render bo'ladi; trace'dagi JSON representation `"Значение поля \\\"manfid\"\\"`. Shared label resolver quote yonidagi optional backslashlarni normallashtirgani uchun test semantik `label='Значение поля "manfid"'` contractini saqlaydi.
- Create form defaultlari: `Активный` checked, separator `Табуляция`, encoding `ANSI`, product subtype tanlovi `Все`.
- Forma qo'shimcha ravishda operation mapping, file settings va CisLink export ustunlarini boshqaradi.
- Save'dan keyin template listga qaytiladi; yangi template main CisLink formasida avtomatik tanlanmaydi, uni `Шаблон` b-inputidan aniq tanlash kerak.

### End-to-end test flowi
Status: code-confirmed
Verified: 2026-08-20
Source: `tests/smoke/test_groups/test_report_grup/test_01_cislink.py`; `test_0_group_runner.py`
- Report-01 har bir run uchun UUID suffixli yangi template required person/product group va price type bilan yaratadi, listda `Активный` statusini tekshiradi va main formaga qaytadi; mavjud template qayta ishlatilmaydi.
- Price type qidiruv `code`iga bog'lanmaydi; birinchi mavjud option
  `select_first=True` bilan tanlanadi.
- Main formada aynan shu yangi template aniq tanlanadi, `До` sanasi beriladi, `Сформировать` bosiladi va `cislink` prefiksli non-empty `.zip` download tekshiriladi.
- Eski `Настройки` modaliga tayangan flow va runnerdagi global skip superseded; tarix `smartup-guide/references/history.md`da saqlanadi.
