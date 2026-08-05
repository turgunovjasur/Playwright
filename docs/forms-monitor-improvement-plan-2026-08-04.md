# Forms Suite va FormMonitor Tahlili — Yaxshilanish Rejasi

**Sana:** 2026-08-04
**Qamrov:** `tests/smoke/test_forms/` — `form_monitor.py` (1026 qator), `flow.py` (543), `skipped_forms.py`, uchta suite (`test_01` 88 forma, `test_02` 21, `test_03` 38) va `test_0_forms_runner.py`
**Usul:** Kod o'qish + da'volarni tasdiqlash — Playwright API introspeksiyasi, forma sonlarini skript bilan hisoblash, HEAD bilan solishtirish uchun vaqtinchalik git worktree
**Branch:** `dev1`

---

## Umumiy Holat

| Bosqich | Mazmun | Holat | Commit |
|---|---|---|---|
| 0 | Forms-03 suite + `+add` tekshiruvini olib tashlash | ✅ Bajarildi | `e19cf60` |
| 1 | Mexanik tozalash (#6, #8, #9, #10, #11) | ✅ Bajarildi | `8afabb3` |
| 2 | Hisobotni ishonchli qilish (#3, #4) | ✅ Bajarildi | — |
| 3 | Aniqlashni kuchaytirish (#2, #7 bajarildi; #1 — trigger yo'q) | 🟡 Qismon | — |
| 4 | Hisobot sifati (Taklif 3) | ✅ Bajarildi | — |
| 5 | JS/network xatolari (Taklif 1) | 🟡 1-qadam bajarildi | — |
| 6 | Shell helper refactori (Taklif 4) | ⬜ Qaror kutilmoqda | — |

Har bosqich alohida commit. Bosqich 2 dan boshlab real run bilan tekshiriladi.

---

## Bajarilgan Ishlar

### Bosqich 0 — Forms-03 va `+add` qarori (`e19cf60`)

- Forms-03 `Продажа` suite qo'shildi: 26 direct menu forma + 12 rekursiv
  page-link/cycle = **38 navigatsiya**. Runnerga `test_forms_03_prodaja`
  sifatida ulandi.
- `+add` ikonka-link tekshiruvi Forms-03 rejasidan **olib tashlandi**. Sabab:
  admin roli creation formalarida hujjatni faqat `Черновик` statusida saqlay
  oladi, shuning uchun `Заказ/Возврат/Лид (создание)` doim ogohlantirish
  beradi va smoke navigatsiya tekshiruvi uchun ma'noli signal bermaydi.
- `add_icon=True` support infrada **saqlandi** (`BasePage.navigate_to_form`,
  `flow.py`, `form_monitor.py`) — boshqa suite ishlatishi mumkin.
- Qo'shimcha: `Дашборд по продажам (БЕТА)` umumiy `SKIPPED_FORMS`ga o'tdi
  (Qlik litsenziyasi yo'q); `navigate_to_form` `menu_column`ni substring
  emas, whitespace-agnostic exact pattern bilan topadi.
- Bilim bazasi: `legacy-form-navigation.md` (`+add` inventari va olib tashlash
  qarori), `history.md` (eski 41-navigation reja superseded).

**Commit paytida topilgan regressiya:** `test_form_flow.py` dagi
`test_build_form_case_plan_...` yiqilayotgan edi — `form_case` ga `add_icon` va
`allowed_warnings` kalitlari qo'shilgan, unit test aynan dict taqqoslaydi va
yangilanmagan. Kutilgan dict yangilandi. HEAD bilan solishtirish: HEAD 6 fail,
commit'dan oldingi ishchi daraxt 7 fail, tuzatgandan keyin 6 fail.

### Bosqich 1 — Mexanik tozalash (`8afabb3`)

Xatti-harakat o'zgarmadi; raqamlash tekshirildi: t01 `1..88`, t02 `1..21`,
t03 `1..38` — uzluksiz.

| # | O'zgarish |
|---|---|
| 11 | `build_form_result(ok=...)` → `status` majburiy. `ok` faqat `status or ("PASSED" if ok else "NOT_OPENED")` fallbackini oziqlantirardi, unga esa production'dagi 3 chaqiruvning hech biri yetib bormaydi. `format_form_result` ham `result["status"]` ni to'g'ridan-to'g'ri o'qiydi. |
| 10 | `run_form_cases` o'lik `return cases[-1]["number"] + 1` o'chirildi — 11 chaqiruvning hech biri o'qimaydi. |
| 6 | `classify_form_failure` dagi `title_failure` marker skani (10 qator, 5 marker) o'chirildi. Undan oldingi `content_ready` guard early-return qiladi, shuning uchun o'sha nuqtada `content_ready` doim `True` va shart allaqachon `not title_matches` ga teng edi. |
| 9b | Forms-02 `start_number` va precondition targetlarini plan uzunligidan hisoblaydi (`1`/`2` hardcode o'chdi), `planned_case(1)` → `cases(section="admin")`. Admin formasi qo'shilsa raqam to'qnashmaydi, skip qilinsa `KeyError` bo'lmaydi. |
| 9a | Forms-01/03 birinchi case izlashni guard qildi — butunlay skip qilingan section endi `IndexError` emas, `None` beradi (`precondition` buni allaqachon qo'llab-quvvatlaydi). |
| 8 | Forms-01 docstringlari haqiqiy qamrovni aytadi: **33** direct, **88** navigatsiya, **12** skip (avval 35/34, 89, 11 — uchtasi ham xato edi). |

Yo'l-yo'lakay: `detail_text` → `lower_detail` bir qatorga yig'ildi.

### Bosqich 2 — Hisobotni ishonchli qilish

#### 2.1. Kutilmagan exception butun hisobotni yo'q qiladi `#3` — hal qilindi

Uchta suite tanasi `try/finally` ichiga olindi, `finish()` `finally` da. Har
suite'da endi **bitta** `finish()` chaqiruvi bor: oldingi
`if monitor.blocked: monitor.finish()` bloklari (t01 4 ta, t02 6 ta, t03 3 ta)
`return` ga aylandi — `finally` allaqachon hisobotni chiqaradi.

`run_case` da `except Exception` **qilinmadi** — kod xatosi "forma nuqsoni"
bo'lib ko'rinmasligi kerak.

**Real run bilan tasdiqlandi** (Forms-03, `--headless`): 3-formaga sun'iy
`AttributeError` qo'yilib run qilindi. Natija — hisobot chiqdi (2 PASSED,
36 `NOT_CHECKED`/`NOT_EXECUTED`), pytest tracebackida ikkalasi ham ko'rinadi:

```
E   AttributeError: SUN'IY TEKSHIRUV: kutilmagan kod xatosi
During handling of the above exception, another exception occurred:
E   AssertionError: Forms-03 — Продажа: reja=38, muvaffaqiyatli=2, ... tekshirilmadi=36.
```

Ya'ni kod xatosi maskalanmaydi, hisobot esa yo'qolmaydi. Injektsiya
qaytarilgandan keyingi toza run: **38/38 PASSED, 146 s**.

#### 2.2. Yiqilganda holat ikki marta o'qiladi `#4` — hal qilindi

`run_case` da `state = None` bilan boshlanadi va fail bo'lganda
`_failure_result(..., state=state)` uzatiladi. Endi xatoni yiqitgan holat va
uni klassifikatsiya qiladigan holat — bitta o'qish.

Regression testi: `test_failure_is_classified_from_the_state_that_caused_it` —
alerti ikkinchi o'qishda yo'qoladigan fake page. Fix'siz `alert_reads == 2` va
`reason_code == CONTENT_VALIDATION_FAILED`; fix bilan `alert_reads == 1` va
`reason_code == APPLICATION_ERROR`. Test bugni tutishi fixni vaqtincha
qaytarib tasdiqlandi.

Struktura testi: `test_forms_suites_report_even_when_an_unexpected_error_escapes`
— AST orqali har `run_*` suite'da aynan bitta `finish()` borligini va u
`Try.finalbody` ichida ekanini tekshiradi.

Yo'l-yo'lakay: `test_authorization_is_monitored_inside_each_forms_suite`
indentatsiyaga bog'liq literal taqqoslash qilardi (`try` bloki indentni
o'zgartirgani uchun yiqilardi) — regexga o'tkazildi.

### Bosqich 3 — Aniqlashni kuchaytirish

Reja bu bosqich yangi fail keltirishini kutgan edi. **Keltirmadi:** 3.2 aniqlashni
ishonchli qildi, lekin 126 forma ustida bitta ham yangi alert topilmadi; 3.3
esa ataylab hisobot-only. Forms-01 88/88 va Forms-03 38/38 yashil qoldi.
Shu sabab "real nuqsonmi yoki artefaktmi" degan qaror hech bir formaga
kerak bo'lmadi.

#### 3.1. Alert formalar orasida tozalanmaydi `#1`
- **Joyi:** Forms suite'da alert yopadigan kod **umuman yo'q**. Loyihada helper
  bor: `test_groups/test_report_grup/test_06_integration_two.py:29`
  (`_close_alert_if_open` — Escape bosib `hidden` kutadi).
- **Muammo:** Forma N da chiqqan alert ekranda qolsa, forma N+1 uchun
  `_visible_error_text` uni o'qiydi va **N+1 ni** `APPLICATION_ERROR` deb
  belgilaydi.
- **Dalil (2026-08-04 run, hali `+add` case'lar bor edi):**

  | # | Forma | O'qilgan matn |
  |---|---|---|
  | 039 | Заказ | ...невозмож**но** ... Чернови**к** |
  | 040 | Возврат | ...невозмож**но** ... Чернови**к** ← 039 bilan aynan bir xil |
  | 041 | Лид | ...невозмож**на** ... Чернови**ка** ← KB'da **Возврат** uchun yozilgan matn |

  Matnlar bir qadam surilgan ko'rinadi. Shu sabab `Возврат`ning
  `allowed_warnings` exact-match'i buzilgan.
- **Yechim (reja):** Har case'dan keyin `finally`da alertni yopib `hidden`
  kutish. **Tartib muhim:** avval state + screenshot olinadi, **keyin** alert
  yopiladi — aks holda dalilni o'zimiz o'chiramiz.

##### Dalil yig'ildi (2026-08-05) — trigger yo'q

Foydalanuvchi savol ko'tardi: `+add` case'lar olib tashlangani uchun bu muammo
qolmaganmi? Dalil yig'ish uchun **avval 3.2 qilindi** (aks holda toza run
"alert yo'q" emas, "alertni ushlamadik" degani bo'lishi mumkin edi), so'ng
runlar bajarildi:

| Manba | Natija |
|---|---|
| `grep add_icon` uchta suite'da | 0 ta ishlatish |
| `grep allowed_warnings` uchta suite'da | 0 ta ishlatish |
| Forms-01, 88 forma, ishonchli alert o'qish bilan | **0 ta `APPLICATION_ERROR`** |
| Shundan 8 ta `Импорт`/`Импорт фото` action formasi | hammasi toza `PASSED` |
| Forms-03, 38 forma | **0 ta `APPLICATION_ERROR`** |

Ya'ni **126 formada bitta ham alert chiqmaydi**, shuning uchun bleed-through
hozir yuz bera olmaydi. 039/040/041 dalili butunlay `+add` case'lardan kelgan
va o'sha gipotezani endi tekshirib bo'lmaydi (case'lar mavjud emas).

- **Holat:** Foydalanuvchi haq — hozirgi qamrovda trigger yo'q.
- **Qayta ko'rish sharti:** biror suite'ga creation/`+add` forma qo'shilsa
  **yoki** hisobotda birinchi real `APPLICATION_ERROR` ko'rinsa. O'sha kuni
  tozalash bo'lmasa bitta real nuqson ikkita fail beradi va ikkinchisi yolg'on.
- **Agar qilinsa — tavsiya etilgan shakl:** har formada shartsiz Escape bosish
  **emas** (u o'zi flakiness manbasi bo'lishi mumkin — masalan "o'zgarishni
  bekor qilasizmi?" dialogini chaqirib yuborishi), balki faqat o'sha case'ning
  captured `state["visible_error"]` bo'sh bo'lmaganda tozalash. Bu bugungi 126
  formada **no-op**, ya'ni qo'shimcha xavf ham, qo'shimcha vaqt ham nol.

#### 3.2. `is_visible(timeout=...)` e'tiborga olinmaydi `#2` — hal qilindi

O'lik `timeout=` parametrlari olib tashlandi (`_safe_locator_visible` dan va
`loader_visible` chaqiruvidan) — ular kodni yolg'on tushuntirardi. Alert endi
kutiladi: `ALERT_SELECTORS` moduldagi konstanta bo'ldi va `_visible_error_text`
avval `_wait_for_any_visible(page, ALERT_SELECTORS, timeout=ALERT_WAIT_MS)`
chaqiradi, keyin qaysi selektor ko'rinadi deb lahzalik skan qiladi.

`loader_visible` uchun lahzalik surat **ataylab qoldirildi** — u yerda kutish
noto'g'ri bo'lardi.

**6 selektorni alohida kutish yo'li tanlanmadi** — u 6 × 1200 ms = 7.2 s har
formaga tushardi. O'rniga vergul bilan birlashtirilgan bitta locator kutiladi:
alert chiqsa **darhol** qaytadi, chiqmasa bir marta timeout to'laydi.

Birlashtirilgan selektor real Chromium'da tekshirildi (yaroqsiz selektor
`PlaywrightError` beradi va u jim yutiladi — ya'ni alert **umuman**
aniqlanmasligi xavfi bor edi): yashirin `#biruniAlert` sanalmadi, ko'rinadigan
`.alert-danger` topildi, `count()=1`.

**O'lchangan narx:** Forms-03 38 forma — 3.2 dan oldin **146.78 s**, keyin
**184.10 s** → **+0.98 s har formaga**. Bu kutish haqiqatan ishlayotganining
dalili ham (jim yiqilsa vaqt o'zgarmasdi). To'liq Forms group (147 forma) uchun
taxminan **+2.4 min**.

`ALERT_WAIT_MS = 1200` — rejadagi qiymat. Kutilgan xato oynasi 300–500 ms
bo'lgani uchun ~700 ms ga tushirish narxni ikki barobar kamaytiradi;
**foydalanuvchi qarori kutilmoqda**.

Regression testi: `test_late_application_error_is_not_missed_by_an_instant_snapshot`
— `FakeLocator.wait_for` kechikkan alertni ochib beradi. Kutish qatorini
o'chirib test yiqilishi tasdiqlandi (`visible_error == ""`).

#### 3.3. Title tekshiruvida sirg'alib o'tish yo'li `#7` — yumshoq variant qilindi

`_title_matches` xatti-harakati **o'zgarmadi** (hali ham `True`), lekin
`checks` ga `title_verified` bayrog'i qo'shildi:

- `_title_candidates(state)` helperi ajratildi (`_title_matches` va
  `_title_verified` ikkisi ham ishlatadi, takrorlanish yo'q).
- `_title_verified` faqat "taqqoslash haqiqatan bo'ldimi" degan savolga javob
  beradi: title bo'sh bo'lsa yoki heading topilmasa `False`.
- `format_form_result` ga `Title tekshirildimi: YOQ (heading topilmadi)` qatori
  qo'shildi — lekin u faqat **fail** bo'lgan formalar uchun chiqadi, holbuki
  bu teshik aynan **PASSED** formalarda yashiringan. Shuning uchun
  `render_monitor_summary` ga alohida `TITLE TAQQOSLANMAGAN FORMALAR` bo'limi
  qo'shildi — u status'ga qaramay ro'yxatlaydi.
- `NOT_CHECKED` formalar bo'limga tushmaydi (`checks` bo'sh dict).

**Qattiq variant uchun dalil (2026-08-05 runlar):** Forms-01 da 87 legacy +
1 a2, Forms-03 da 32 legacy + 6 a2 forma — **119 legacy formaning hech birida**
"heading topilmadi" holati yuz bermadi, `TITLE TAQQOSLANMAGAN` bo'limi ikkala
runda ham bo'sh chiqdi. Ya'ni sirg'alib o'tish yo'li hozirgi qamrovda **amalda
ishlatilmayapti**, va `False` qaytaradigan qattiq variant hech narsani
yiqitmasdi. Forms-02 (a2, `title_source=document`) bu yo'lga umuman tushmaydi.

Shunga qaramay yumshoq variant qoldirildi: qattiq variantning yagona foydasi —
kelajakda heading yo'qolsa fail berish; lekin o'sha holatda `content_ready`
(`b-page`/`.subheader`) ham katta ehtimol bilan yiqiladi. Hisobot bo'limi esa
teshik ochilsa darhol ko'rinadigan qiladi.

### Bosqich 4 — Hisobot sifati `Taklif 3` — bajarildi

`duration_ms` o'lchanardi (`form_monitor.py:765, 839`), lekin hisobotda vaqt
haqida hech narsa yo'q edi: run 155 s dan 240 s ga chiqsa qaysi forma
sekinlashganini bilishning yo'li yo'q. Bu server degradatsiyasining eng erta
signali — forma hali ochiladi (test yashil), lekin 2 barobar sekin.

`_duration_lines` helperi `render_monitor_summary` ga `FORMA DAVOMIYLIGI`
bo'limini qo'shadi: jami, o'rtacha va eng sekin 5 forma. Qo'shimcha o'lchov
kiritilmadi — ma'lumot allaqachon yig'ilgan edi.

Ikki nozik joy:

- Faqat `test_started` formalar hisoblanadi. `TEST_BLOCKED` yozuvidagi
  `duration_ms` — precondition vaqti (login/filial), forma ochilish vaqti emas;
  u o'rtachani buzardi (test'da 60 s bloker chiqarib tasdiqlandi).
- Hech narsa o'lchanmagan bo'lsa (hammasi `NOT_CHECKED`) bo'lim umuman
  chiqmaydi.

CI ta'siri tekshirildi: `scripts/analyze_test_result.py` faqat strukturali
`form-monitor.json` ni o'qiydi (`| form-monitor.json` attachment nomi bo'yicha),
matn hisobotini parse qilmaydi — yangi bo'lim Telegram/CI summary'ni buzmaydi.

**Real run bilan tasdiqlandi (Forms-03, 2026-08-05, 38/38 PASSED):**

```
FORMA DAVOMIYLIGI
Jami                   : 172.2 s (38 forma)
O'rtacha bitta formaga : 4.5 s
Eng sekin 5 forma:
  1. 001 | Визиты | 7.6 s
  2. 003 | Отслеживание пользователей | 7.3 s
  3. 005 | Планирование визитов | 7.1 s
  4. 004 | Отслеживание мобильных представителей | 6.8 s
  5. 024 | Отчет по визитам | 6.4 s
```

Kelajakdagi solishtiruv uchun **Forms-03 baseline: o'rtacha 4.5 s, jami 172 s**
(pytest wall-clock 187.7 s — farq auth, filial switch va hisobot overheadi).

Bu birinchi o'lchov allaqachon bir narsani ko'rsatdi: eng sekin 5 formaning
4 tasi — reja boshidagi formalar (001, 003, 004, 005). Ya'ni ular formaga xos
sekinlik emas, **cold-start** effekti. Aynan shu narsa oldin ko'rinmasdi.

---

## Qolgan Ishlar

### Bosqich 5 — JS va network xatolari `Taklif 1`

- **Muammo:** Monitor formaning sog'lig'ini faqat **ko'zga ko'rinadigan**
  narsalar bilan o'lchaydi: heading, URL, alert div'i, loader. Real hayotda
  buzuq forma ko'pincha **jim** yiqiladi:

  | Nima bo'ladi | Ekranda | Monitor |
  |---|---|---|
  | API `500`, grid bo'sh qoldi | heading bor, jadval bo'sh | ✅ PASSED |
  | JS exception, filtr paneli chizilmadi | heading bor | ✅ PASSED |
  | `403` — dostup yo'q, alert chiqmadi | heading bor | ✅ PASSED |
  | Ma'lumot so'rovi timeout bo'ldi | heading bor, spinner o'chgan | ✅ PASSED |

  Ya'ni suite hozir faqat "ochiladimi" qismini o'lchayapti, "ishlaydimi" ni yo'q.
- **Yaxshi tomoni:** pattern loyihada bor — `tests/smoke/smoke_reporting.py:80`
  (`page.on("response", remember_first_unauthorized)`).

#### 1-qadam — faqat yig'ish — bajarildi

`FormMonitor.__init__` `page.on("pageerror")` va `page.on("response")` ni
ro'yxatga oladi, `finish()` ularni olib tashlaydi. Har `run_case` va
`precondition` boshida oyna tozalanadi (`_reset_page_events`), shuning uchun
signal qo'shni formaga yozilmaydi.

Qarorlar:

- **`usable` va `classify_form_failure` tegilmadi** — signal statusga ta'sir
  qilmaydi. Bu ataylab: filtr faqat real shovqin ko'rilgandan keyin yoziladi.
- `_checks` sof funksiya bo'lib qoldi (case + state); page eventlari yangi
  `_case_checks` wrapperida qo'shiladi.
- **URLdan query string olib tashlanadi** (`404 host/path` ko'rinishi) — so'rov
  URLida token bo'lishi mumkin va hisobotga tushmasligi kerak.
- Namuna `MAX_PAGE_EVENTS=20` bilan cheklangan, **hisob cheklanmagan** — aks
  holda 200 ta 404 bo'lgan sahifa hisobotda "20 ta" bo'lib yolg'on aytardi.
- `remove_listener` bound method bilan real Chromium'da tekshirildi (aks holda
  listener suite'lar orasida oqib ketardi — `page` fixture uchta suite uchun
  umumiy).

**O'lchangan shovqin (to'liq Forms group, 2026-08-05, 147/147 PASSED, 667 s):**

| Signal | Soni | Izoh |
|---|---|---|
| `404 /page/tour/<path>.json` | **204** | Legacy UI tour/hint fayli — sahifada mavjud emas. Sof shovqin. |
| `404 /a2/assets/i18n/kernel-overlay/.../ru.json` | 1 | A2 i18n overlay, ixtiyoriy. Sof shovqin. |
| `404 /api/b/biruni/m:load_image_v2` | 1 | `Plugin Marketplace` (Forms-02 #020). **Yagona haqiqiy API chaqiruvi.** |
| JS `pageerror` | **0** | 147 formaning hech birida bitta ham JS exception yo'q. |

Jami 206 muvaffaqiyatsiz so'rov, 123/147 formada signal ko'rindi. Ya'ni
**shovqinning 99% i bitta pattern** (`/page/tour/`) va uni filtrlash oson.

Eng qimmatli topilma — **`pageerror` kanali butunlay toza**. Ya'ni JS xatosini
qattiqlashtirish uchun filtr **umuman kerak emas**.

#### 2-qadam — qattiqlashtirish — foydalanuvchi qarori kutilmoqda

1-qadam dalili quyidagini imkon beradi:

- **JS xatolari:** filtrsiz `_assert_healthy_form_state` ga qo'shish. 147 formada
  0 shovqin, ya'ni xavf minimal, foyda katta ("JS exception, filtr paneli
  chizilmadi" holati hozir jim o'tadi).
- **Network:** `/page/tour/` va `/assets/i18n/` ni ma'lum-shovqin ro'yxatiga
  yozib, qolgan 4xx/5xx ni nuqson deb hisoblash. Bunda `Plugin Marketplace`
  (`m:load_image_v2` 404) qizil bo'ladi — bu real nuqsonmi yoki yana bir
  shovqinmi degan qaror kerak.

### Bosqich 6 — Shell helper refactori `Taklif 4`

- **Joyi:** `flow.py:308, 326, 347, 384, 471` — `if "/a2/" in page.url`
  tarmoqlanishi 5 joyda takrorlanadi
- **Muammo:** Shell-ga bog'liq yangi amal qo'shganda yana yozish kerak.
  Bittasini esdan chiqarsangiz — A2 sahifada legacy locator ishlatiladi va
  xato sababi tushunarsiz bo'ladi.
- **Yechim:** `shell_page(page)` helperi — `AngularBasePage` yoki `BasePage`
  qaytaradi.
- **Holat:** Bu struktura refactori, nuqta-fix emas. **Foydalanuvchi qarori
  kutilmoqda**, majburiy emas.

---

## Qamrovdan Tashqarida Qoldirilganlar

### Skip qilingan formalar hisobotda ko'rinmaydi `#5`
Foydalanuvchi bu topilmani hozirgi rejaga qo'shmadi. Yozib qo'yiladi:

| Suite | Ro'yxatda | Aktiv | Skip |
|---|---|---|---|
| Forms-01 | 100 | 88 | 12 |
| Forms-02 | 22 | 21 | 1 |
| Forms-03 | 39 | 38 | 1 |

Summary faqat `Rejalashtirilgan: 88` deydi. Hisobotni o'qigan odam 12 forma
tekshirilmaganini bilmaydi — "hammasi qoplangan" degan taassurot qoladi.
Yechim: `build_form_case_plan` (`:404`) skip'larni ham qaytarsin, monitor
`SKIP QILINGAN FORMALAR` bo'limini chiqarsin.

### `allowed_warnings` exact-match mo'rtligi `Taklif 2`
`form_monitor.py:86` whitespace normalizatsiya + `×` prefiks olib tashlash +
**aynan** taqqoslash. Yuqoridagi matn siljishi (3.1) buning mo'rtligini
ko'rsatdi. Substring yoki kalit so'zlar ro'yxati ishonchliroq bo'lardi.
**Hozir kerak emas** — `+add` case'lar olib tashlangani uchun bu mexanizmni
hech qaysi suite ishlatmaydi. Kelajakda creation forma tekshirilsa qaytiladi.

### Natija dict'idagi `"ok"` kaliti
Bosqich 1 da `ok` **parametri** olib tashlandi, lekin natijadagi `"ok"` kaliti
qoldi. U `form-monitor.json` (`schema_version: 2`) ichida va tashqi consumer
o'qishi mumkin — o'chirish schema o'zgarishi bo'ladi.

---

## Eski Unit Test Faillari (bu ish bilan bog'liq emas)

`main` da **allaqachon** 6 ta unit test yiqiladi. Bosqich 0/1 ularni ko'paytirmadi
— har commit'dan oldin HEAD bilan solishtirib tasdiqlandi.

```
test_auth_diagnostics.py::test_change_password_requires_fresh_login_and_dashboard
test_form_flow.py::test_safe_screenshot_masks_inputs_and_secret_columns
test_product_setup.py::test_setup_products_use_separate_uzs_and_usd_price_types
test_product_setup.py::test_setup_products_receive_separate_uzs_and_usd_balances
test_telegram_reporting.py::test_success_message_shows_setup_and_forms_coverage
test_telegram_reporting.py::test_failure_details_are_collapsed_and_html_escaped
```

Telegram'dagi ikkitasi xabar formati o'zgargani sababli ko'rinadi
(`🧪 Pytest:` → `🧪 Pytest cases:`, `🧾 Forms: 5/6 forma ochildi` yo'qolgan).
Alohida ish sifatida hal qilinadi.

---

## Har Commit'dan Oldin Tekshiruv Ro'yxati

```bash
# 1. Kompilyatsiya
.venv/bin/python -m py_compile tests/smoke/test_forms/*.py

# 2. Unit testlar — 6 dan oshmasligi kerak
.venv/bin/python -m pytest tests/unit -q --maxfail=999 2>&1 | grep -c "^FAILED"

# 3. Raqamlash uzluksizligi va forma sonlari (88 / 21 / 38)

# 4. Bilim bazasi validatori
.venv/bin/python skills/smartup-guide/scripts/validate_knowledge_base.py

# 5. Bosqich 2 dan boshlab — real run
#    Tez feedback: Forms-03 (38 forma, ~2.5 min)
#    Yakuniy: to'liq Forms group (147 forma, ~10 min)
```
