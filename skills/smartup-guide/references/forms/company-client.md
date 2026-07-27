# Kompaniya OAuth2 klientlari

Tags: a2, oauth2, company-client, filial, session, permission, error

## URL va navigation

- A2 list: `/a2/biruni/kauth/company_client_list`.
- Legacy user track: `Администрирование` filiali → `Главное` → `Дополнительное` →
  `Клиенты OAuth2 сервера для компании`.
- `+add` listdagi `Создать`, `+edit` esa list qatori → `Изменить` orqali ochiladi.

## Screenshot

- [A2 filial konteksti mos kelmagandagi access error](screenshots/company-client/company-client__access-error__desktop-1440x783__filial-context-mismatch.png)
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
- List yuklanmagani uchun `+add` va `+edit` xatolari mustaqil forma xatosi emas:
  `Создать`, `.smt-data-row` va `Изменить` bosqichlariga yetib borilmaydi.
- Testda ishlatish: legacy switch tasdiqining o'zi yetarli emas; A2 sahifaga
  kirgach shell filialini ham target filialga sinxronlash va model so'rovi shu
  filial bilan ketganini tekshirish kerak.
