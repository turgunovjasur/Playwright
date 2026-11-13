# Umumiy yordamchi kod

Bu papka test yoki runner emas. Uni alohida Run qilish kerak emas.

| Fayl/papka | Vazifasi |
|---|---|
| `runtime.py` | Run/attempt katalogi, context, trace va natijalarni saqlash |
| `environment.py` | Umumiy muhit xatolarini ajratish |
| `retry/` | Retry qarori, jurnal, qayta ishlatish va urinishlar hisoboti |
| `preparation/` | Registry, mavjud ma’lumot/readiness tekshiruvi va repair |
| `session_recovery/` | Sessiya va UI lookup kontekstini tiklash |
| `resume.py` | Qo‘llab-quvvatlangan saqlangan runni explicit davom ettirish |

`preparation/` — tayyorlov **mexanizmi**. Setup testcase’lar
[../test_orders/setup_cases/](../test_orders/setup_cases/) ichida.
