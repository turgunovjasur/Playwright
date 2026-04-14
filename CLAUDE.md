# Claude uchun Ko'rsatmalar — Playwright Loyihasi

## Avtomatik O'rganish

Foydalanuvchi quyidagi narsalarni aytganda `/learn` skillini **o'zing, so'ralmay** ishlat:

- UI yoki ilovaning qanday ishlashini tushuntirsa
- Xato sababini o'zi topib aytsa
- Avvalgi yechim noto'g'ri ekanligi ma'lum bo'lsa
- Loyihaga xos qoida yoki pattern ko'rsatsa

Maqsad: har suhbatda bir xil xatoni takrorlamaslik.

## Loyiha Haqida

- Framework: Playwright + pytest (Python)
- Test turi: Smoke testlar — `tests/smoke/`
- Runner: `tests/smoke/test_smoke_runner.py` — barcha testlarni ketma-ket ishlatadi
- `code` fixture: session uchun unikal 4 xonali son, runner da yangi, yakka testda `data_store.json` dan o'qiladi
- `.env`: `COMPANY_URL`, `COMPANY_CODE`, `COMPANY_PASSWORD`, `USER_PASSWORD`