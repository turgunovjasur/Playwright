# Kompaniya OAuth2 klientlari

Tags: a2, oauth2, company-client, filial, session, permission, error

## URL va navigation

- A2 list: `/a2/biruni/kauth/company_client_list`.
- Legacy user track: `Администрирование` filiali → `Главное` → `Дополнительное` →
  `Клиенты OAuth2 сервера для компании`.
- `+add` listdagi `Создать`, `+edit` esa list qatori → `Изменить` orqali ochiladi.

## Screenshot

- [A2 filial konteksti mos kelmagandagi access error](screenshots/company-client/company-client__access-error__desktop-1440x783__filial-context-mismatch.png)
- [smartup.online Forms runnerda takrorlangan A2 filial context access error](screenshots/company-client/company-client__access-error__desktop-2880x1567__a2-filial-context-mismatch-smartup-online.png)
- [A2 list muvaffaqiyatli yuklangan holat](screenshots/company-client/company-client__list-loaded__desktop-1440x783.png)

## Known issue: legacy va A2 filial konteksti alohida qolishi mumkin

Tags: a2-shell, legacy-shell, filial-id, access-denied, cascade

- 2026-07-27 user tasdig'i: `company_client_list` joriy UI'da ochiladi va
  menyu-based testga qayta qo'shildi. `+add` va `+edit` keyinga qoldirildi.
- Menyu-based test oqimi: dashboard tekshiruvi → `Администрирование`ga switch →
  listni real menu track orqali ochish → A2 `document.title`, URL va
  `app-company-client-list` tayyorligini `AngularBasePage.expect_page()` bilan
  tasdiqlash. Shundan keyin ortga qaytmasdan joriy A2 sahifadan
  `AngularBasePage.switch_filial()` orqali oldindan saqlangan operatsion
  filialga o'tiladi.
- 2026-07-27 trace fakti: forma nomi vizual ko'rinadi, ammo DOMda semantik
  `role=heading` yo'q. URL va title to'g'ri, `company_client_list:table`
  so'rovlari HTTP 200 va list qatorlari yuklangan; shuning uchun legacy
  `BasePage.expect_page(heading=...)` bu forma uchun noto'g'ri.
- Quyidagi 403 holati 2026-07-24 runidagi tarixiy diagnostika:
- 2026-07-24, `app3.greenwhite.uz/xtrade`: legacy shell `Администрирование`
  filialiga muvaffaqiyatli o'tgan bo'lsa ham, A2 shell oldingi operatsion filialni
  saqlab qoldi.
- Trace dalili: legacy dashboard so'rovlari admin filial ID bilan ketdi, lekin
  A2 `company_client_list:model` operatsion filial ID bilan yuborildi va HTTP
  `403` qaytdi. UI: `Нет доступа к форме Клиенты OAuth2 сервера для компании`.
- `document.title` shu error holatida `Smartup Online` bo'lib qoladi.
- 2026-07-29 `smartup.online` Forms runner trace'i shu holatni qayta
  tasdiqladi: legacy shell `Администрирование`ga o'tganidan keyin A2 route
  operatsion filial kontekstida ochildi, `company_client_list:model` HTTP 403
  qaytardi va A2 header operatsion filialni ko'rsatdi. Title assertiondagi
  `Smartup Online` root cause emas, access-error sahifasining natijasi.
- List yuklanmagani uchun `+add` va `+edit` xatolari mustaqil forma xatosi emas:
  `Создать`, `.smt-data-row` va `Изменить` bosqichlariga yetib borilmaydi.
- Testda ishlatish: legacy switch tasdiqining o'zi yetarli emas; A2 sahifaga
  kirgach shell filialini ham target filialga sinxronlash va model so'rovi shu
  filial bilan ketganini tekshirish kerak.

### Forms runnerdagi A2 filial sinxronlash tuzatishi (2026-07-29)
Tags: a2-shell, legacy-shell, filial-sync, forms-runner, fix

- `tests/smoke/test_forms/test_a2_admin_menu_forms.py` OAuth2 list menu
  trackini bosgach, title/readiness tekshiruvidan oldin
  `AngularBasePage.switch_filial(name="Администрирование")` chaqiradi.
- Sabab: legacy `BasePage.switch_filial()` faqat `#/` shell kontekstini
  o'zgartiradi; A2 shell oldingi operatsion filialni mustaqil saqlashi mumkin.
- 2026-07-29 live debug: A2 filial switchi joriy list routeni saqlamaydi,
  `/a2/trade/intro/dashboard`ga redirect qiladi. Shu sabab sync'dan keyin
  `company_client_list` A2 menyusidan qayta ochiladi.
- Kutilgan oqim: legacy `Администрирование` → A2 list route → A2
  `Администрирование` sync → A2 dashboard → listni A2 menyusidan qayta ochish
  → title/component readiness → operatsion filialga A2 switch.
- Verifikatsiya: target Forms-02 headless run barcha 22 ta A2 formani ochib
  `1 passed in 137.19s` natija berdi.
- Screenshotlar o'zgarmadi: yuqoridagi access-error va list-loaded holatlari
  ushbu regressiya hamda kutilgan natijani qamraydi.
