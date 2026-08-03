# Codex uchun Ko'rsatmalar — Playwright Loyihasi

## Bilim Bazasi — `skills/` (Yagona Ishonchli Manba)

Barcha skilllar va Smartup domain bilimlari uchun **yagona source of truth** — repo root'idagi `skills/`. `.agents/skills/` (Codex) va `.claude/skills/` (Claude Code) — shu papkaga `../../skills/<name>` symlink qiluvchi entry-point'lar; ikkalasi ham aslida bir xil `skills/` faylini o'qiydi va yozadi, shuning uchun data bo'linmaydi.

- **O'qish:** Smartup sahifa, forma, contract, order, locator, modal, grid yoki UI xatti-harakati ustida ishlashdan oldin avval `skills/smartup-guide/SKILL.md` ni (index) o'qi, so'ng kerakli `references/...` yoki forma uchun `references/forms/<slug>.md` dossierini o'qi.
- **Yozish:** Yangi biznes qoida, UI xatti-harakati, locator yoki xato sababi topilsa — uni `skills/smartup-guide/` ichidagi mos reference yoki form dossier fayliga yoz (boshqa joyga emas). Forma screenshotlari `skills/smartup-guide/references/forms/screenshots/<slug>/` ichida arxivlanadi.
- `smartup-guide` Skill tool ro'yxatida bo'lmasligi mumkin — shunda ham yuqoridagi fayllarni to'g'ridan-to'g'ri Read bilan o'qi.
- **Yangi skill qo'shish:** papkani `skills/<name>/` ichida yarat, so'ng ikkala entry-point'da symlink qo'sh — `.agents/skills/<name> -> ../../skills/<name>` va `.claude/skills/<name> -> ../../skills/<name>`.

## Avtomatik O'rganish

Foydalanuvchi quyidagi narsalarni aytganda `/learn` skillini **o'zing, so'ralmay** ishlat:

- UI yoki ilovaning qanday ishlashini tushuntirsa
- Xato sababini o'zi topib aytsa
- Avvalgi yechim noto'g'ri ekanligi ma'lum bo'lsa
- Loyihaga xos qoida yoki pattern ko'rsatsa

Maqsad: har suhbatda bir xil xatoni takrorlamaslik.

## Muhokama Va Implementatsiya Tasdig'i

- Foydalanuvchi `shunday qilsak bo'ladimi?`, `nima deysan?`, `qaysi variant
  yaxshi?` kabi savol yoki taklif bersa, bu avtomatik ravishda kod yozish
  ruxsati hisoblanmaydi.
- Bunday holatda avval savolga to'g'ridan-to'g'ri javob ber, ta'sir va
  trade-offlarni tushuntir, so'ng qisqa xulosa/tavsiya qil.
- Repo kodi, testlar, skilllar, knowledge-base yoki konfiguratsiyani
  o'zgartirishdan oldin foydalanuvchidan alohida implementatsiya tasdig'ini
  so'ra.
- Read-only qidiruv va impact analysis tasdiqsiz bajarilishi mumkin, lekin
  undan keyin ham topilgan natijani tushuntirib, yozishdan oldin ruxsat ol.
- Foydalanuvchi shu xabarning o'zida `yoz`, `o'zgartir`, `tuzat`,
  `amalga oshir`, `qoidaga qo'sh` kabi aniq buyruq bergan bo'lsa, aynan
  ko'rsatilgan scope uchun bu implementatsiya tasdig'i hisoblanadi.
- Muhokama savolidan kengroq o'zgarishni taxmin qilib amalga oshirma. Tasdiq
  olinganda ham faqat kelishilgan scope'ni o'zgartir.

## Kod O'zgarishlari Uchun Branch

Status: user-reported
Verified: pending
Source: user

- Foydalanuvchi boshqa branchni aniq aytmasa, barcha kod o'zgarishlarini
  `dev1` branchida qil. Har qanday kod tahriridan oldin joriy branchni tekshir
  va kerak bo'lsa `dev1`ga o't.

## Loyiha Haqida

- Framework: Playwright + pytest (Python)
- Test turi: Smoke testlar — `tests/smoke/`
- User setup runner: `tests/smoke/test_setup/test_0_setup_runner.py` — setup testlarini ketma-ket ishlatadi
- Group runnerlar: `tests/smoke/test_groups/**/test_*_group_runner.py` — har bir group case alohida pytest testi
- Asosiy cross-platform runner: `python scripts/run_tests.py`; `run_tests.sh` — Mac/Linux wrapper
- `code` fixture: session uchun unikal 6 xonali son, runner da yangi, yakka testda `data_store.json` dan o'qiladi
- Agar repo rootda `.env` mavjud bo'lsa, direct `pytest`/PyCharm run konfiguratsiyasi undan olinadi; `.env` yo'q bo'lsa terminal/CI flaglari ishlaydi
- Mavjud company: `--url <server_url> --company-code <code> --company-password <password>`
- Yangi company: `--url <server_url> --create-company --head-email <email> --head-password <password>`; yangi company admin paroli kod ichidagi default qiymat
- User password test ichida hardcode, lekin qoida fayllarida literal qiymat yozilmaydi

[//]: # (## Suhbat Oxirida Majburiy — Skills Yangilash)

[//]: # ()
[//]: # (**Har suhbat oxirida quyidagilarni bajar &#40;so'ralmasa ham&#41;:**)

[//]: # ()
[//]: # (1. Bu suhbatda yangi UI sahifa, forma, locator, tasdiqlangan flow yoki xato sababi topildimi?)

[//]: # (2. Agar ha — `skills/smartup-guide/` ichidagi mos form dossier yoki reference fayliga yoz.)

[//]: # (3. Yangi forma bo'lsa — screenshot ham `skills/smartup-guide/references/forms/screenshots/<slug>/` ga arxivla.)

[//]: # (4. Test muvaffaqiyatli ishlasa — test docstring + skills sinxron bo'lsin.)

[//]: # ()
[//]: # (Yozmasdan suhbatni yopma.)

## Ruxsatlar

- Escalation/ruxsat kerak bo'lsa, xavfsiz va qayta ishlatiladigan holatda doim `prefix_rule` taklif qil.
- Uzun `python -c $'...'` debug buyruqlari o'rniga workspace ichidagi vaqtinchalik yoki mavjud scriptni `./.venv/bin/python path/to/script.py` ko'rinishida ishlat.
