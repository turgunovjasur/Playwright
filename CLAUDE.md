# Claude uchun Ko'rsatmalar — Playwright Loyihasi

## Bilim Bazasi — `skills/` (Yagona Ishonchli Manba)

Barcha skilllar va Smartup domain bilimlari uchun **yagona source of truth** — repo root'idagi `skills/`. `.claude/skills/` (Claude Code) va `.agents/skills/` (Codex) — shu papkaga `../../skills/<name>` symlink qiluvchi entry-point'lar; ikkalasi ham aslida bir xil `skills/` faylini o'qiydi va yozadi, shuning uchun data bo'linmaydi. Doim `skills/` ni manba deb bil:

- **O'qish:** Smartup sahifa, forma, contract, order, locator, modal, grid yoki UI xatti-harakati ustida ishlashdan oldin avval `skills/smartup-guide/SKILL.md` ni (index) o'qi, so'ng kerakli `references/...` yoki forma uchun `references/forms/<slug>.md` dossierini o'qi.
- **Yozish:** Yangi biznes qoida, UI xatti-harakati, locator yoki xato sababi topilsa — uni `skills/smartup-guide/` ichidagi mos reference yoki form dossier fayliga yoz (boshqa joyga emas). Forma screenshotlari `skills/smartup-guide/references/forms/screenshots/<slug>/` ichida arxivlanadi.
- `smartup-guide` Skill tool ro'yxatida bo'lmasligi mumkin — shunda ham yuqoridagi fayllarni to'g'ridan-to'g'ri Read bilan o'qi.
- **Yangi skill qo'shish:** papkani `skills/<name>/` ichida yarat, so'ng ikkala entry-point'da symlink qo'sh — `.claude/skills/<name> -> ../../skills/<name>` va `.agents/skills/<name> -> ../../skills/<name>`.

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
- User setup runner: `tests/smoke/test_setup/test_0_setup_runner.py` — setup testlarini ketma-ket ishlatadi
- Group runnerlar: `tests/smoke/test_groups/**/test_*_group_runner.py` — har bir group case alohida pytest testi
- Full script: `run_tests.sh` — setup va barcha group runner fayllarini bitta pytest sessiyasida Allure bilan ishlatadi
- `code` fixture: session uchun unikal 6 xonali son, runner da yangi, yakka testda `data_store.json` dan o'qiladi
- `.env` ishlatilmaydi; runnerda `--url` majburiy
- Mavjud company: `--url <server_url> --company-code <code> --company-password <password>`
- Yangi company: `--url <server_url> --create-company`; yangi company admin paroli kod ichidagi default qiymat
- User password test ichida hardcode, lekin qoida fayllarida literal qiymat yozilmaydi
