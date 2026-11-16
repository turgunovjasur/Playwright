# Kompaniya OAuth2 klientlari

Qidiruv kalitlari: a2, oauth2, company-client, filial, session, permission, error

## Mundarija

- [Quick Lookup](#quick-lookup)
- [Screenshot Paths](#screenshot-paths)
- [Known Locators](#known-locators)
- [Flow And Tests](#flow-and-tests)
- [Business Rules](#business-rules)
- [Known Issues](#known-issues)
- [URL va navigation](#url-va-navigation)
- [Screenshot](#screenshot)
- [Legacy va A2 filial konteksti](#known-issue-legacy-va-a2-filial-konteksti-alohida-qolishi-mumkin)
- [A2 filial sinxronlash](#a2angular-filial-sinxronlash-tuzatishi-2026-07-29)
- [Secretlarni yashirish](#monitoring-screenshotida-oauth-secretlarni-yashirish)
- [Bootstrap navigatsiyasi](#a2angular-bootstrapda-listni-ikki-marta-ochmaslik)

## Quick Lookup

### URL va navigation

- A2 list: `/a2/biruni/kauth/company_client_list`.
- Legacy user track: `Администрирование` filiali → `Главное` → `Дополнительное` →
  `Клиенты OAuth2 сервера для компании`.
- `+add` listdagi `Создать`, `+edit` esa list qatori → `Изменить` orqali ochiladi.

## Screenshot Paths

### Screenshot

- [A2 filial konteksti mos kelmagandagi access error](screenshots/company-client/company-client__access-error__desktop-1440x783__filial-context-mismatch.png)
- [2026-07-29dagi Forms runnerda takrorlangan A2 filial context access error](screenshots/company-client/company-client__access-error__desktop-2880x1567__a2-filial-context-mismatch-smartup-online.png)
- [A2 list muvaffaqiyatli yuklangan holat](screenshots/company-client/company-client__list-loaded__desktop-1440x783.png)

## Known Issues

### Known issue: legacy va A2 filial konteksti alohida qolishi mumkin

Tags: a2-shell, legacy-shell, filial-id, access-denied
Status: trace-confirmed
Verified: 2026-07-29
Source: `screenshots/company-client/company-client__access-error__desktop-2880x1567__a2-filial-context-mismatch-smartup-online.json`; `screenshots/company-client/company-client__list-loaded__desktop-1440x783.json`

- Arxivlangan failure’da A2 header operatsion filialni ko‘rsatgan. `company_client_list:model` HTTP 403 qaytargan, sahifada `Нет доступа к форме Клиенты OAuth2 сервера для компании` chiqqan va title `Smartup Online` bo‘lib qolgan.
- 2026-07-27 list-loaded holati alohida menu-based run trace’idan saqlangan. Add va editga yetib borish uchun avval list ochilishi kerak.

#### A2Angular filial sinxronlash tuzatishi (2026-07-29)

Tags: a2-shell, legacy-shell, filial-sync, a2angular
Status: code-confirmed
Verified: 2026-11-16
Source: `tests/smoke/test_forms/test_a2_angular_forms.py:478`; `tests/smoke/test_forms/test_a2_angular_forms.py:565`

- A2Angular avval legacy shellni `Администрирование`ga o‘tkazadi va texnik A2 dashboardga kiradi. Case guruhi ishlashidan **oldin** A2 filialini tanlaydi, keyin menu trackni bajaradi. Eski listni ikki marta ochish oqimi uchun [tarixiy qayd](../history.md#forma-testlarining-eski-qamrovi).

#### Monitoring screenshotida OAuth secretlarni yashirish
Tags: oauth2, client-secret, screenshot, allure, security, forms-runner
Status: code-confirmed
Verified: 2026-08-04
Source: `utils/screenshot_masking.py`;
`tests/smoke/smoke_reporting.py`;
`tests/smoke/test_forms/monitoring/monitor.py`;
`tests/smoke/test_forms/test_a2_angular_forms.py`
- Qayerda: company client list yoki uning add/edit holati xato dalili sifatida
  screenshot qilinayotganda.
- Qoida: `company-client` mask profili forma inventarida explicit beriladi va
  faqat `kauth/company_client` URLida ishlaydi. Shu formada inputlar va list
  qatorlari to'liq yopiladi; Client Secret report rasmining ochiq qismi
  bo'lmaydi. Boshqa formalarning oddiy search/filter inputlari bu profil bilan
  masklanmaydi.
- Testda ishlatish: mask kerak bo'lgan company client case definitioniga
  `screenshot_mask: company-client` ber; boshqa formaga shu profilni qo'shma.

#### A2Angular bootstrapda listni ikki marta ochmaslik
Tags: a2-shell, bootstrap, navigation, duplicate, a2angular
Status: code-confirmed
Verified: 2026-08-03
Source: `tests/smoke/test_forms/test_a2_angular_forms.py`
- Qayerda: standalone A2Angular boshida legacy shell'dan A2 shellga o'tishda.
- Qoida: A2 kontekstini tayyorlash uchun OAuth list vaqtincha ochilmaydi;
  texnik `/a2/trade/intro/dashboard` ochilib filial sinxronlanadi. Shundan
  keyin company client list real A2 menu track orqali faqat testcase sifatida
  ochiladi.
- Testda ishlatish: bootstrap qadamini forma natijasi deb sanama; listning
  yagona counted navigatsiyasi `run_form_cases()` ichida bo'lsin.

## Known Locators

A2 inventarida route `biruni/kauth/company_client_list`, title `Клиенты OAuth2 сервера для компании` va tayyorlik komponenti `app-company-client-list`.

## Flow And Tests

`tests/smoke/test_forms/test_a2_angular_forms.py` admin A2 menu trackini, `tests/smoke/test_forms/inventory/glavnoe.py` esa Главное inventaridagi listni belgilaydi.

## Business Rules

A2Angular admin bo‘limi listni `Администрирование` filialida tekshiradi. List rasmlari uchun `company-client` mask profili inventarda berilgan.
