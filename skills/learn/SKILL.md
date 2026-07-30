---
name: learn
description: Suhbatda aniqlangan loyihaga xos UI xatti-harakati, xato sababi, test qoidasi yoki avvalgi noto'g'ri yechimni provenance va status bilan knowledge-base'ga qo'shadi. Foydalanuvchi loyiha haqida yangi bilim berganda AGENTS.md bo'yicha proaktiv ishlat.
---

# Yangi Bilimni Skill ga Qo'shish

Argument: `$ARGUMENTS` (o'rganilgan narsa tavsifi)

## Trigger

Quyidagi holatlarda AGENTS.md bo'yicha proaktiv ishlat:
- Foydalanuvchi UI xatti-harakatini tushuntirsa ("modal shunday ishlaydi", "server shuncha vaqt ketadi")
- Xato sababini o'zi aytsa ("sabab hali modal ochilmasidan button bosilyapti")
- Loyiha qoidasini ko'rsatsa ("bu test faqat runner orqali ishlaydi")
- Avval qilgan yechim noto'g'ri chiqsa va to'g'ri yechim topilsa

## Ish tartibi

1. Bilimni umumiy qoida emas, loyihaga xos bitta aniq fakt sifatida yoz.
2. Dalil statusini tanla:
   - `user-reported` — foydalanuvchi aytgan, hali kod/UI/trace bilan tekshirilmagan;
   - `code-confirmed` — amaldagi kod bilan tasdiqlangan;
   - `live-ui-confirmed` — real UI orqali tasdiqlangan;
   - `trace-confirmed` — Playwright trace/log bilan tasdiqlangan.
3. Qaysi faylga tegishli ekanini aniqlash:
   - test/debug/flow protsedurasi → mos skillning `SKILL.md` yoki `references/`;
   - Smartup biznes flowlari, UI joylashuvlari, entitylar, locatorlar → `smartup-guide` ichidagi mos reference fayl:
     - aniq forma bo'yicha bilimlar → `smartup-guide/references/forms/<form-slug>.md`
     - contract/order shartlari → `smartup-guide/references/contracts.md`
     - order flow/product/setup → `smartup-guide/references/orders.md`
     - locator/modal/grid/screenshot → `smartup-guide/references/ui-patterns.md`
     - debug/data_store/setup dependency → `smartup-guide/references/testing-debug.md`
   - joriy arxitektura → `write-test` reference'i yoki `smartup-guide/references/testing-debug.md`;
   - superseded/eski kuzatuv → `smartup-guide/references/history.md`.
4. `user-reported` bilimni tasdiqlangan current truth bilan aralashtirma. Joriy
   qoida sifatida faqat code/live-ui/trace tasdiqli bilimni yoz; aks holda uni
   `User-reported` bo'limida saqla.
5. Mos joy topilmasa avtomatik yangi skill yaratma; foydalanuvchiga taklif qil.
6. Qo'shilgan joy va statusni foydalanuvchiga ko'rsat.

## Format

```markdown
### <mavzu>
Status: user-reported | code-confirmed | live-ui-confirmed | trace-confirmed
Verified: YYYY-MM-DD yoki `pending`
Source: user | <fayl:qator> | live UI | <trace/log path>
- Qoida: <o'rganilgan narsa — qisqa va aniq>
```

## Muhim

- Umumiy ma'lumot emas, **bu loyihaga xos** narsalarni qo'sh
- Bir fakt uchun bitta qisqa entry yoz
- Bir xil narsani ikki marta qo'shma (avval mavjudligini tekshir)
- Password, token, email, session code, real company credentiali yoki boshqa
  secret/PII'ni knowledge-base'ga yozma.
- Konkret session qiymatini emas, `user-pw{code}`, `<company_code>` kabi
  parametrik ko'rinishni yoz.
- Yangi dalil oldingi qoidani inkor qilsa, eski entry'ni current faylda
  qoldirma: `history.md`ga `Superseded by ...` izohi bilan ko'chir.
