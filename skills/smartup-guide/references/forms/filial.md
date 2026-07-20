# Filial (Организация) Add Form

## Loyiha Xususiyatlari

- Filial add formdagi real ko'rinadigan maydonlar: `Название`, `Юридическое лицо`, `Базовая валюта`, `Часовой пояс`, `Порядковый номер`, `Статус`, `НДС`, `Акциз`.
- Filial add formda `short_name`, `phone`, `email`, `website`, `address`, `note` maydonlari yo'q; ularni taxmin qilib testga qo'shmaslik kerak.
- `test_03_filial` legal person bog‘lanishini `legal_person_code`/`legal_person_name` orqali qiladi va list/view checklarini ham amalga oshiradi.
- `Юридическое лицо` filialga bir marta bog'langandan keyin keyingi filial add searchda chiqmaydi; ikkinchi filial yaratish uchun yangi legal person kerak.
- `NEW_CODE=0` bilan eski `legal_person_code` ishlatilsa filial add search faqat `Добавить -> <code>` ko'rsatishi mumkin; to'g'ri chain `NEW_CODE=1` bilan yangi legal person yaratib keyin filial yaratadi.
- Filial screenshotlari doimiy bilim sifatida `references/forms/screenshots/filial/` ichida saqlanadi; `test-results` faqat vaqtinchalik debug output.

## Field Bilimlari

### Add Form Fields
Tags: filial, add-form, fields
- `Название` input: `ng-model="d.name"`; test qiymati `filial-pw{code}`.
- `Юридическое лицо` b-input: `ng-model="d.person_name"`; shu run ichida yangi yaratilgan `legal_person_code` orqali qidiriladi.
- `Базовая валюта` b-input: `ng-model="d.base_currency_name"`; `Узбекский сум` tanlanadi va `Продолжить?` confirm bosiladi.
- `Часовой пояс` b-input: `ng-model="d.timezone_name"`; regressionda `Ташкент` search qilib `Asia/Tashkent` option tanlanadi.
- `Порядковый номер` input: `ng-model="d.order_no"`; regressionda run `code` soni yoziladi.
- `Статус` switch: `ng-model="d.state"`; default `Активный`, o'chirilmaydi.
- `НДС` switch: `ng-model="d.vat_enabled"`; regressionda yoqiladi.
- `НДС` yoqilganda `Ставка НДС (%)` required input paydo bo'ladi: `ng-model="d.vat_percent"`; regressionda `12` yoziladi.
- `Акциз` switch: `ng-model="d.excise_enabled"`; regressionda yoqiladi.

## List Va View Tekshiruv

### Filial list
Tags: filial, list, grid
- Listda `filial_name` bo'yicha row topiladi.
- Row ichida `filial_name`, `legal_person_code`, `Активный` tekshiriladi.
- `legal_person_name` list rowda har doim ko'rinmaydi, shuning uchun listda assert qilinmaydi.

### Filial view main card
Tags: filial, view, main-card
- `Основная информация` cardda add formdan saqlangan qiymatlar tekshiriladi: `filial_name`, `Узбекский сум`, `legal_person_code`, `legal_person_name`, `Ставка НДС (%)`, `12`, `Акциз`, `Да`, `(+05:00) Ташкент`, `Активный`.
- `Порядковый номер` view main cardda ko'rinmadi; hozir view assertga qo'shilmagan.

### Filial view products tab
Tags: filial, view, products, modules
- `Продукты` tabida `trade` project switchi `checked=true` bo'lishi tekshiriladi.
- Child module switchlari ham `checked=true` bo'lishi tekshiriladi: `Equipment`, `Finance - Main`, `Finance - Advanced`, `HR and Payroll`, `Image Recognition`, `Main`, `Manufacturing`, `Marking`, `Sales - Main`, `Sales - Advanced`, `Store`, `Telegram`, `Trade Marketing`, `Uzbekistan Module`, `Warehouse - Main`, `Warehouse - Advanced`.
- Product tab module switchlari DOMda `project.binded` va `module.binded` checkboxlar sifatida chiqadi; text ko'rinishi yetarli emas, `checked` holati assert qilinadi.

## Debug Notes

### 2026-06-02 verification
Tags: filial, run-result, screenshot
- Field discovery screenshot: `references/forms/screenshots/filial/filial__add-default__desktop-1920x1080.png`.
- Field discovery JSON: `references/forms/screenshots/filial/filial__add-fields.json`.
- `test_01_authorization + test_02_legal_person + test_03_filial --scope=regression --new-code -q -s` passed: 3 passed in 89.35s.
- Switch discovery JSON: `references/forms/screenshots/filial/filial__add-switches.json`.
- VAT/Excise enabled discovery JSON: `references/forms/screenshots/filial/filial__add-fields-after-switches.json`.
- `test_01_authorization + test_03_filial` saqlangan code (`NEW_CODE=0`) va regression scope bilan, `d.vat_percent=12` to'ldirilgach passed: 2 passed in 21.42s.
- View main screenshot: `references/forms/screenshots/filial/filial__view-main__desktop-1920x1080.png`.
- Product tab screenshot: `references/forms/screenshots/filial/filial__view-products__desktop-1920x1080.png`.
- View discovery JSON: `references/forms/screenshots/filial/filial__view-state.json`.
- Main card va product module checked assertlari qo'shilgandan keyin `test_01_authorization + test_02_legal_person + test_03_filial --scope=regression --new-code -q -s` passed: 3 passed in 93.76s.

### 2026-06-29 checkbox API konsolidatsiyasi
Tags: filial, switch, checkbox, refactor, locator
- `d.vat_enabled` / `d.excise_enabled` switch DOM jonli tekshirildi: `<label class="switch"> <input type=checkbox opacity:0 ng-model=...> <span>holat matni</span></label>`. Click target = `label.switch` (raw input ko'rinmas). Batafsil: [../../ui-patterns.md](../ui-patterns.md) "checkbox/switch yagona API" qoidasi.
- НДС switch yoqilganda `Ставка НДС (%)` (`d.vat_percent`) maydoni paydo bo'lishi jonli tasdiqlandi: `filial__add-vat-on__desktop-1200x690.png`.
- `test_03_filial` endi `BasePage(page).checkbox(ng_model="d.vat_enabled", checked=True)` ishlatadi (eski `flow_form.set_checkbox` o'rniga).
