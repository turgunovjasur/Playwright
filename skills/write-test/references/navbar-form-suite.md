# Yangi Navbar Form Suite Qo'llanmasi

Bu reference `Склад`, `Финансы` yoki boshqa Smartup navbar tabidagi barcha
formalarni bitta Forms smoke suite'ga qo'shishda ishlatiladi.

## Mundarija

- [Majburiy manbalar va skilllar](#majburiy-manbalar-va-skilllar)
- [Coverage chegaralari](#coverage-chegaralari)
- [Live inventory yig'ish](#live-inventory-yigish)
- [Inventory yozish](#inventory-yozish)
- [Intentional skip](#intentional-skip)
- [Leaf test](#leaf-test)
- [Forms runner](#forms-runner)
- [Documentation](#documentation)
- [Verifikatsiya](#verifikatsiya)
- [Yakuniy checklist](#yakuniy-checklist)
- [Ko'p uchraydigan xatolar](#kop-uchraydigan-xatolar)

## Majburiy manbalar va skilllar

Ishni boshlashdan oldin:

1. `smartup-guide` — `SKILL.md`, navbar navigatsiyasi reference'i va mavjud
   form dossierlarini o'qi.
2. Runtime'da mavjud browser-control capability — mavjud login sessioni kerak
   bo'lsa live navbarni operatsion hamda `Администрирование` filiallarida
   inventarizatsiya qil.
3. `write-test` — leaf, inventory va runner patterniga amal qil.
4. Yangi qoida yoki oldingi xato aniqlansa `learn` bilan knowledge-base'ga yoz.
5. Runner/path/reporting o'zgarsa `maintain-test-infra`ni qo'lla.
6. Test execution authoritysi va commandlari uchun yagona manba `run-smoke`;
   failure diagnostikasi uchun `debug-test` ishlatiladi.

## Coverage chegaralari

### Navbar suite ownership

Suite egasi `navbar_tab`; shell suite chegarasi emas:

```text
<Navbar> ichidagi legacy forma → <Navbar> suite
<Navbar> ichidagi A2 forma     → <Navbar> suite
```

Shuning uchun bitta navbar inventorysi legacy va A2 definitionlarni birga
saqlashi mumkin. A2 destinationga `shell: "a2"` explicit yoziladi; legacy
default `shell="legacy"`dan foydalanadi.

### Filial precedence va unique coverage

Inventory quyidagi tartibda tuziladi:

1. Operatsion filialdagi barcha direct va user-trace formalarni ol.
2. `Администрирование` filialidagi formalarni ol.
3. Admin/operatsion kesishmasini canonical `path`/forma identity bo'yicha
   taqqosla.
4. Admin bucketga faqat operatsion filialda topilmagan admin-only formalarni
   qo'sh.

Bir canonical forma ikkala filialda ham bo'lsa, navbar suite uni faqat
operatsion filialda tekshiradi — filiallar orasidagi menu trace ko'rinishi
farq qilsa ham admin bucketda takrorlanmaydi. Admin-only ro'yxat bo'sh bo'lsa
admin bucket umuman yozilmaydi.

### A2Angular bilan kesishma

`A2Angular` boshqa coverage o'qi:

- barcha navbarlardagi A2 formalarni jamlaydigan standalone aggregate;
- Forms runnerga kirmaydi;
- raqamsiz `test_a2_angular_forms.py` orqali ishlaydi;
- navbar suite'dagi A2 forma A2Angular inventorysida ham qoladi.

Navbar suite ↔ A2Angular kesishmasi intentional. Operatsion filial ↔ admin
kesishmasini bir navbar suite ichida ikki marta test qilish esa intentional
emas.

## Live inventory yig'ish

Har bir filial uchun quyidagilarni qayd et:

| Maydon | Ma'nosi |
|---|---|
| `filial` | Operatsion filial yoki `Администрирование` |
| `navbar_tab` | Yuqori navbar nomi |
| `menu_column` | UI'da ko'rinadigan exact ustun headingi; heading yo'q bo'lsa `None` |
| `menu_item` | Bosiladigan exact forma nomi |
| `title` | Ochilgan formaning exact heading/document title'i |
| `path` | Querysiz canonical forma pathi |
| `page_links` | Parent ochilgach bosiladigan exact linklar ketma-ketligi |
| `shell` | `legacy` yoki `a2` |

Hisobotda alohida ko'rsat:

- har filialdagi direct formalar soni;
- operatsion/admin kesishmasi;
- operatsion-only va admin-only formalar;
- legacy/A2 kesimi;
- direct va page-link trace'lar soni;
- unique canonical pathlar soni.

Bir filial ichida canonical target turli parent yoki `page_links` orqali
ochilsa, har bir real user trace alohida case bo'lib qoladi. Ya'ni filiallararo
kesishma canonical forma bo'yicha chiqariladi, bitta filial ichidagi navigatsiya
coverage'i esa parent/menu/page-link trace'ni ham hisobga oladi.

## Inventory yozish

Fayl:

```text
tests/smoke/test_forms/inventory/<navbar_slug>.py
```

Direct forma:

```python
{
    "menu_column": "Отчеты",
    "menu_item": "Конструктор отчетов по закупкам",
    "path": "anor/rep/mbi/mkw/purchase",
    "shell": "a2",
}
```

Page-link trace:

```python
{
    "menu_column": "Документы",
    "menu_item": "Инвентаризации",
    "page_links": ["Причины инвентаризации"],
    "path": "anor/mkw/stocktaking/reason_list",
}
```

`title` berilmasa:

- direct formada `menu_item`;
- page-link formada oxirgi `page_links` qiymati

expected title sifatida olinadi. UI title bundan farq qilsa `title` explicit
yoziladi.

Bucketlar:

```python
FORM_BUCKETS = (
    {
        "forms": [*OPERATIONAL_DIRECT_FORMS, *OPERATIONAL_PAGE_LINK_FORMS],
        "filial": OPERATIONAL_PLACEHOLDER,
        "section": "operational",
    },
)
```

Admin-only formalar mavjud bo'lsagina ikkinchi bucket qo'shiladi:

```python
{
    "forms": ADMIN_ONLY_FORMS,
    "filial": "Администрирование",
    "section": "admin",
}
```

Inventoryni `tests/smoke/test_forms/inventory/__init__.py` registry'siga
`navbar_tab` exact nomi bilan qo'sh.

## Intentional skip

Dostup yoki muhit cheklovi bor formani inventorydan o'chirma. Uni:

```text
tests/smoke/test_forms/inventory/skipped_forms.py
```

registry'siga canonical path va aniq sabab bilan qo'sh. Definition inventoryda
qoladi; normalizatsiyada aktiv reja va intentional skip alohida hisoblanadi.

Skip canonical pathning o'ziga global yopishtirilmaydi: registry yozuvi
`navbar_tab + menu_item + path` user trace'iga scope qilinadi. Aks holda bir
navbar parenti uchun chiqarilgan forma xuddi shu canonical path bilan boshqa
navbar orqali ochilganda ham noto'g'ri skip bo'lib qoladi.

## Leaf test

Fayl:

```text
tests/smoke/test_forms/test_XX_<navbar_slug>_forms.py
```

Leaf faqat uchta ochiq qadamdan iborat:

1. `authorization(page, who="admin")`.
2. `get_legacy_form_buckets(NAVBAR_TAB)`.
3. `run_legacy_form_monitoring(...)`.

Leaf ichida filial/menu loopi, shell branching, skip reporting yoki
`FormMonitor.finish()` qayta yozilmaydi. Har leafda bitta `run_*` va bitta
standalone `test_*` wrapper bo'ladi.

Suite identity:

```text
suite_name="Forms-XX — <Navbar>"
progress_test_id="forms_XX_<navbar_slug>"
```

`XX` keyingi bo'sh raqam emas — u Smartup navbarining joriy ko'rinish
tartibidir. Leaf fayli, runner wrapperi, `suite_name` va `progress_test_id`
bir xil raqamda bo'ladi. Yangi suite navbar tartibining o'rtasiga tushsa,
undan keyingi navbar suite'lar qayta raqamlanadi. `A2Angular` bu raqamlashga
kirmaydi.

## Forms runner

`tests/smoke/test_forms/test_0_forms_runner.py` faqat navbar suite'larni
jamlaydi. Yangi item:

- non-parametrized sibling pytest test;
- leafdagi `run_*`ni bevosita chaqiradigan thin wrapper;
- `@allure.title("<Navbar>")` bilan Smartup navbar tartibiga mos bo'ladi.

`A2Angular` importi yoki wrapperi Forms runnerga qo'shilmaydi.

## Documentation

Live inventarni `skills/smartup-guide/references/legacy-form-navigation.md`ga
provenance va status bilan yoz. Aniq formaga yangi locator, UI xatti-harakati
yoki known issue topilsa tegishli
`skills/smartup-guide/references/forms/<slug>.md` dossierini yangila.

Test docstringidagi sonlar inventory bilan bir xil bo'lishi kerak:

```text
active = operational direct + operational page-link + admin-only
skipped = intentional skip registryga tushgan definitionlar
```

## Verifikatsiya

**REQUIRED SUB-SKILL:** test/collection/smoke bajarishdan oldin `run-smoke`
authority qoidasini o'qi. Bu qo'llanma execution ruxsatini takrorlamaydi.

Execution authority bo'lmasa quyidagi statik tekshiruvlar bilan cheklan:

- source va scoped diff inspection;
- syntax/config parse;
- `git diff --check`;
- knowledge-base validator.

`run-smoke` executionga ruxsat bersa:

1. inventory normalization sonlarini;
2. runner va standalone collectionni;
3. yangi navbar leaf smoke'ini;
4. kerak bo'lsa Forms runner va standalone A2Angular'ni

tekshir. Failure bo'lsa log, trace, screenshot va Allure artefaktlarini
`debug-test` bilan tahlil qil.

## Yakuniy checklist

- [ ] Branch `dev1` yoki user tanlagan branch.
- [ ] Operatsion va admin live inventory olingan.
- [ ] Admin bucketda faqat admin-only formalar qolgan.
- [ ] Legacy/A2 shell har definitionda to'g'ri.
- [ ] Direct va page-link user trace'lar to'liq.
- [ ] Skip formalar registry orqali saqlangan.
- [ ] Inventory registryga navbar qo'shilgan.
- [ ] Leaf uch qadamli façade patternida.
- [ ] Forms runnerda bitta yangi navbar wrapper bor.
- [ ] A2Angular Forms runnerga qo'shilmagan.
- [ ] A2 formalar standalone A2Angular inventorysida ham saqlangan.
- [ ] Docstring, knowledge-base va inventory sonlari sinxron.
- [ ] `run-smoke` execution authoritysi bajarilgan.

## Ko'p uchraydigan xatolar

| Xato | To'g'ri yechim |
|---|---|
| Admin/operatsion kesishmasini ikki marta case qilish | Operatsionni saqla, faqat admin-only formalarni admin bucketga qo'sh |
| Navbar testini legacy va A2ga bo'lish | Barcha shellarni bitta `navbar_tab` suite'da saqla |
| A2Angular'ni Forms runnerga qo'shish | Uni alohida standalone aggregate sifatida saqla |
| Bir xil canonical pathli turli user trace'larni o'chirish | Parent va `page_links` farq qilsa alohida case sifatida saqla |
| Dostup yo'q formani inventorydan o'chirish | Umumiy skip registryga qo'sh |
| Visible heading yo'q bo'lsa taxminiy `menu_column` yozish | `menu_column=None` ishlat |
| Leaf ichida monitor orchestrationini takrorlash | `run_legacy_form_monitoring(...)` façade'idan foydalan |
| Execution authorityni reference'dan taxmin qilish | `run-smoke`ni yagona authority sifatida o'qi |
