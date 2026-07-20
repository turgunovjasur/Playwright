# CisLink integration report (trade/rep/integration/cislink)

> **STATUS: SKIP (barcha serverda) — 2026-06-12.** CisLink sahifasi Smartup deploymentlar bo'ylab o'zgarmoqda (pastdagi "Server farqi" bo'limiga qarang), shuning uchun test barcha serverda o'tkazib yuborilgan. Joyi: `test_report_group_runner.py` — chain'dan CisLink progress_step bloki olib tashlangan, standalone `test_report_01_cislink` ga `@pytest.mark.skip(reason=CISLINK_SKIP_REASON)` qo'yilgan. Qayta yoqish: chain blokini tiklab, skip markerni olib tashlash (sahifa barqarorlashganda).

CisLink — sotuv/qoldiq ma'lumotlarini tashqi tizim (CisLink) uchun `.txt` fayllar jamlangan **.zip** ko'rinishida eksport qiluvchi integration report.

## Navigatsiya

- Sahifa **menyuda yo'q** — faqat URL orqali ochiladi: `#/<session_token>/trade/rep/integration/cislink`.
- Testda token login'dan keyingi `page.url` dan olinadi:
  ```python
  base, _, rest = page.url.partition("#/")
  session_token = rest.split("/", 1)[0]
  page.goto(f"{base}#/{session_token}/trade/rep/integration/cislink")
  ```
- Sahifa heading: `CisLink(NNNN)` (NNNN — dinamik raqam) → `get_by_role("heading").filter(has_text="CisLink")`.

## Asosiy sahifa

- Buttonlar: **Сформировать** (`button[ng-click="generate()"]`), **Сформировать(MQ)** (`generateMQ()`), **Настройки** (`get_by_role("button", name="Настройки", exact=True)`), **Закрыть**.
- Body: Тип периода radiolari (`Последние 45 дней` default checked / `Пользовательский период`), `До` sana (default bugun). Default qoldirilsa ishlaydi.

## Настройки modal (filtrlar)

Modal `[role=dialog]` emas — inline panel. Сохранить tugmasi `button[b-hotkey="save"]` (modal ochiqligini shu bilan tekshirish mumkin).

Majburiy (*) maydonlar va barqaror selektorlar:

| Maydon (label) | Selektor | Qiymat (test) |
|---|---|---|
| Идентификация (`Значение поля "manfid"*`) | `input[ng-model="d.identification_code"]` | `test` |
| Характеристики* (person group) | `b-input[name="person_groups"]` (Поиск → div.hint) | `Группа` |
| Продуктовое направление* (product group) | `b-input[name="product_groups"]` | `Группа` |
| Тип цены* (price type) | `b-input[name="price_types"]` | `Price Type UZB-pw{code}` |

Ixtiyoriy: `person_types` (Подтип характеристики лиц), `product_types` (Подтипы характеристик), Разделитель/Кодировка, Настройка типов операций, Настройки файлов va eksport ustunlari (catal, code, ... — 100+ field).

Mavjud group variantlari (autotest'da): person — `Группа/Категория/Тип`; product — `Группа/Категория/Торговая марка`.

## Saqlash va generatsiya (tasdiqlangan flow)

1. Настройки → filtrlar → `button[b-hotkey="save"]` → modal yopiladi, asosiy sahifa qaytadi.
2. `button[ng-click="generate()"]` → **`cislink.zip`** yuklanadi (Playwright `page.expect_download`). Fayl `cislink` bilan boshlanadi, `.zip` bilan tugaydi, bo'sh emas (misol: 6508 bayt, ichida 16 ta `.txt`: catal/code/promo/disc...).
3. Selenium-dagi `clear_old_download`/`before_files`/papka-polling KERAK EMAS — Playwright `expect_download` yuklash tugashini o'zi kutadi va `download.save_as(...)` bilan saqlaydi.

## Checklistdan FARQLAR (gaps)

- **Filial maydoni YO'Q**: bu CisLink versiyasida settings'da ham, asosiy sahifada ham `Филиал` yo'q. Report **aktiv filial** uchun ishlaydi → admin sifatida avval `switch_filial(filial-pw{code})` qilinadi (checklistdagi (h) qadam o'rniga).
- **Price type nomi**: checklistda `Цена продажи UZB-{cod}` — bu eski Selenium loyiha nomi. Bu loyihada `Price Type UZB-pw{code}` (test_price_type yaratgan nom). `Цена продажи` — narx turi (kind), nom emas.
- **Login**: checklist admin login talab qiladi → `authorization(page, who="admin")` (admin@`<company>`). Lekin user (`user-pw{code}`) ham sahifaga kira oladi.
- Generatsiyada confirm modal chiqmaydi — to'g'ridan-to'g'ri download bo'ladi.

## Server farqi: app3.greenwhite.uz/xtrade ≠ smartup.online (MUHIM)

Yuqoridagi flow **`smartup.online`** deployment uchun to'g'ri. **`app3.greenwhite.uz/xtrade`** (CI'da `--url https://app3.greenwhite.uz/xtrade`, APP3 company) deploymentida CisLink sahifasi **boshqacha versiya** — test shu yerda yiqiladi:

- **`Настройки` tugmasi YO'Q.** Filtrlar modal ortida emas, to'g'ridan-to'g'ri asosiy sahifada inline ko'rsatiladi: `Шаблон` (template tanlash), `Тип периода` (`Последние 45 дней` / `Пользовательский период`), `До` (sana). `identification_code`, `person_groups`, `product_groups`, `price_types` maydonlari bu versiyada yo'q.
- Asosiy sahifada ikkita generatsiya tugmasi: **`Сформировать`** va **`Сформировать(CISLINK)`** (online'da `Сформировать(MQ)` edi), hamda `Шаблоны`, `Закрыть`.
- Natija: `run_report_cislink_check` step 2'da `get_by_role("button", name="Настройки", exact=True).click()` → `TimeoutError` (10s), chunki tugma sahifada mavjud emas. Heading `CisLink(NNNN)` esa ko'rinadi (step 1 o'tadi).
- Dalil: CI run 27402337118 (2026-06-12), trace screenshot `CisLink(7008)` sahifasi.
- Xulosa: bu **test bug emas**, ikki Smartup deploymentining UI versiyasi farqi. Test online uchun yozilgan; xtrade'da CisLink reportni qo'llab-quvvatlash kerak bo'lsa, sahifa layoutiga qarab branch qilish (Настройки bormi → modal, yo'q bo'lsa → inline Шаблон/период) kerak.

## Test

- `tests/smoke/test_groups/test_report_grup/` — **Report group** (`smoke_group("Report")`), all-runner'da `test_05_report_group_runner`.
- Leaf: `test_cislink.py::run_report_cislink_check(page, code, scope, login)`; admin login + filialga o'tish, settings, generate+download verify.
- Screenshot: `skills/smartup-guide/references/forms/screenshots/cislink/cislink__main__desktop-1200x660__20260610.png`.
