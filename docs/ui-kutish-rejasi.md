# Smartup Angular (A2) testlarida kutishlarni yaxshilash rejasi

**Yangilangan sana:** 2026-11-18

**Hozirgi holat:** 5-bosqichda server select amallari UI Kit va Order trace’i bilan solishtirildi. Mavjud tanlash va tozalash amallari yaxshilandi. Alohida ochish, tanlamasdan qidirish va bo‘sh natijani tekshirish uchun API bo‘yicha qaror kerak. 2-bosqichdagi loader dalili va Smartup’da amaliy tasdiq ochiq.

Reja Angular (A2) formalarini qamrab oladi. Maqsad — element sekin yuklanganda kerakli holatni kutish va u tayyor bo‘lishi bilan davom etish.

## Kod qayerda turadi?

- **Har bir Angular UI komponenti uchun bitta base funksiya** shu komponentning UI’da mavjud barcha foydalanuvchi amallarini qamrab oladi. Test va flowlar kerakli amalni `AutoBasePage` orqali shu metoddan chaqiradi. Har bir amalning tayyorlik belgisi va odatiy maksimal kutish vaqti komponent metodida boshqariladi.
- **Kutish helperlari** komponent metodining ichida ishlatilishi mumkin. Masalan, test klientni tanlash uchun `b_input()`ni chaqiradi. Metod qidiruv matnini kiritgach, aynan shu matnga mos variant ko‘rinib, tanlashga tayyor bo‘lishini kutadi va uni tanlaydi. Shu shartni tekshiradigan helper mavjud bo‘lsa, metod uni qayta ishlatadi. Bir nechta komponentga bir xil kutish kerak bo‘lsa, ular shu helperni baham ko‘rishi mumkin.
- Masalan, `b_input()` orqali ro‘yxatni ochish, qidirish, variant tanlash, tanlovni tozalash, joriy qiymatni o‘qish va tekshirish mumkin bo‘lishi kerak. Bular boshlang‘ich misollar. To‘liq ro‘yxat UI Kit va haqiqiy A2 formadan olinadi. Klient tanlash `b_input()`ga tegishli. Klient tanlab, mahsulot qo‘shib, buyurtmani saqlash ketma-ketligi takrorlansa, u yordamchi flow’ga tegishli.
- **Yordamchi flow** bir nechta test ishlatadigan bir xil qadamlar ketma-ketligini base funksiyalardan yig‘adi. Masalan, saqlangan buyurtmani topish va tahrirlashga ochish. Avval mavjud flow tekshiriladi. Takrorlanish tasdiqlansa, tegishli testlar bitta flow’ni chaqiradi.
- **Test** ssenariyga xos amal va kutilgan biznes natijasini ifodalaydi. Masalan, miqdorni 9 ga o‘zgartirib, jami 63 000 bo‘lishini tekshiradi. Bitta testni o‘tkazish uchun maxsus locator yoki vaqt qiymati qo‘shishdan iloji boricha qochamiz.
- **Mahalliy kutish** faqat shart aynan shu ssenariyga xos bo‘lib, uni base yoki mavjud flow orqali ishonchli ifodalashning amaliy yo‘li bo‘lmaganda qo‘llanadi. Bunda test kuzatiladigan natijani kutadi. Shu ehtiyoj boshqa testda ham uchrasa, umumlashtirish qayta ko‘rib chiqiladi.

## Bosqichlar

| № | Holat | Ish | Bosqichni yopish mezoni |
|---|---|---|---|
| 0 | Bajarildi | #3689 logi va tracelarini ko‘rish, UI Kit’dagi input va skeletonni brauzerda tekshirish. | Boshlang‘ich dalillar quyida qayd etilgan. #3689 tuzatishlari uchun CI tasdig‘i hali kutilmoqda. |
| 1 | Bajarildi | A2 base funksiyalari va Angular Order ssenariylaridagi raqamli timeoutlar, majburiy pauzalar va takroriy UI qadamlarini topish. | Quyida kod joylari, iste’molchilar va har bir takror bo‘yicha qaror yozildi. |
| 2 | Jarayonda | A2 skeleton, komponent spinneri va ichki vidjetning band holatini haqiqiy Angular forma yoki trace bilan solishtirish. | Tez ochilish, loader kech paydo bo‘lishi, loader tugamay qolishi va bitta vidjet bandligi uchun keyingi amal qachon bajarilishi yozilgan. |
| 3 | Jarayonda | Umumiy kutishlarni A2 base funksiyalariga, takrorlangan UI qadamlarini tegishli flow’ga ko‘chirish. Dashboard va ombordagi 120 soniyalik kutishlarni birinchi bo‘lib baholash. | Umumiy UI timeoutlari base qatlamidan olinadi. Mahalliy istisno qolsa, sababi ro‘yxatda ko‘rsatilgan. Tez holat ortiqcha kutmaydi, timeout xabari esa qaysi holat kutilganini bildiradi. |
| 4 | Tekshiruv kutilmoqda | Sonli input. UI Kit va Smartup buyurtma formasida 10 → 9 tahririni solishtirish. Maydon qiymati, oraliq 0 so‘rovi, Tab’dan keyingi hisob va yakuniy summani kuzatish. | Kiritish usulini umumiy input() metodiga qo‘llashdan oldin yana bitta sonli maydonda mosligi tekshirilgan. Summaga oid biznes tekshiruvi testda qolgan. |
| 5 | Jarayonda | Serverdan qidiradigan select. UI Kit va A2 formada komponent amallarini ro‘yxatga olib, har birini mavjud `b_input()` imkoniyatiga solishtirish. Har bir amal uchun tayyorlik belgisi va yetishmayotgan imkoniyatni qayd etish. | Tasdiqlangan har bir amalni test aynan `b_input()` orqali bajara olishi tekshirilgan. Sekin qidiruv, kech kelgan eski javob, bo‘sh natija va yo‘qolmay qolgan spinner uchun kutiladigan holat ko‘rsatilgan. |
| 6 | Statik tekshirildi; run kutilmoqda | O‘zgarishlarni statik tekshirish. Testlarni ishga tushirish so‘ralgach, ta’sirlangan ssenariylar va shu base funksiyalarini ishlatadigan boshqa formalarda tekshirish. | Run havolasi, natija va ochiq muammolar yozilgan. Sekin holat bilan birga odatiy tez holatda ortiqcha kutish paydo bo‘lmagani ham tekshirilgan. |

## 1-bosqich natijalari

A2 base metodlari, ular chaqiradigan umumiy helperlar va `tests/regression/test_orders` ichidagi 78 ta Python fayli statik tekshirildi. Order katalogida `wait_for_timeout()` chaqiruvi topilmadi. Pytest assertionlari, brauzer amallari va navigatsiya sukut bo‘yicha bir xil `UI_TIMEOUT_MS` (60 s) oladi. Bu maksimal vaqt, shart bajarilishi bilan kutish tugaydi. [Umumiy qiymat](../utils/base_pages/__init__.py#L3) · [Assertionlar](../tests/conftest.py#L91) · [Brauzer konteksti](../tests/shared/browser.py#L20)

### Kutishlar va mavjud helperlar

| Qayerda | Kod hozir nimani kutadi | Qaror |
|---|---|---|
| Sahifa va jadval. [A2 loader](../utils/base_pages/angular_base_page.py#L1283), [Order fixture](../tests/regression/test_orders/conftest.py#L26) | Loader darhol ko‘rinmasa, base uning paydo bo‘lishini 8 s gacha kuzatadi. Faqat `order_group` markerli testlarda fixture bu oynani 250 ms qiladi. Keyin ko‘rinadigan skeleton va `aria-busy=true` soni nolga tushishini kutadi. | `_wait_for_loader(root=...)` qayta ishlatiladi. [expect_page](../utils/base_pages/angular_base_page.py#L1369) butun sahifaga, [grid](../utils/base_pages/angular_base_page.py#L1446) jadvalga qaraydi. 2-bosqichda 250 ms dan kech chiqqan loader va band qo‘shni vidjetni tekshiramiz. 3-bosqichda kuzatish oynasini base ichidan boshqaramiz. |
| Sahifa xatosi. [expect_no_application_error](../utils/base_pages/page_errors.py#L11) | `expect_page()` xato chiqishini 4,8 s gacha kuzatadi, tekshiruvlar oralig‘i ko‘pi bilan 100 ms. Xato ko‘rinsa, matnini o‘qishga 2 s beriladi. A2 metodining izohida eski 2,4 s qolgan. | Mavjud helper xato diagnostikasi uchun saqlanadi. Tez ochilgan sahifa vaqtini o‘lchaganda loader oynasi va shu kuzatuvni alohida hisoblaymiz. |
| Klient, mahsulot qidiruvi. [b_input](../utils/base_pages/angular_base_page.py#L550), [multiselect](../utils/base_pages/angular_base_page.py#L1087), [Order mahsulot tanlovi](../tests/regression/test_orders/helpers/flows/order.py#L176) | Ikkala komponent server qidiruvida so‘rovni matn va maydon bo‘yicha `_lookup_query_finished` bilan moslaydi. Keyin `b_input()` o‘z spinneri va variantini, `multiselect()` o‘z menyusi, yuklanish matni va variantini tekshiradi. | Ochish yoki qidirish amalidan oldin so‘rovni tinglash ikkala metodda takrorlangan. 5-bosqichda shu qismni ichki helperga yig‘ish mumkin. Har bir komponent o‘z tayyorlik belgisini tekshiradi. [Moslik helperi](../utils/base_pages/angular_base_page.py#L32) |
| Miqdor va jami. [input](../utils/base_pages/angular_base_page.py#L350), [miqdor chegirmasi](../tests/regression/test_orders/business_cases/promotions/test_01_quantity_discount.py#L35) | `input()` maydon ko‘rinishini kutadi, yozadi, so‘ralsa Tab bosadi va kutilgan qiymatni kutadi. Yozilgan miqdor ko‘rinishi order summasi qayta hisoblanganini tasdiqlamaydi. | Maydon uchun mavjud `_control()` va `input(expect_value=...)` ishlatiladi. 4-bosqichda tahrirlashni tekshiramiz. Ssenariy kutilgan summani beradi, base shu qiymat maydonda paydo bo‘lishini kutadi. |
| Guruh sessiyasi. [Dashboard va filial](../tests/regression/test_orders/helpers/group_auth.py#L75), [Order fixture](../tests/regression/test_orders/conftest.py#L80) | Saqlangan sessiya bilan dashboard hujjatini ochish uchun 120 s, dashboard yoki login URL’iga o‘tish uchun 30 s, kerakli filial tugmasi ko‘rinishi uchun 30 s belgilangan. | Navigatsiya chegarasi va filial tugmasining UI kutishini base orqali boshqarish. Dashboardga kirish va sessiya tugab loginga qaytish yo‘llarini ajratish login flow’ida qoladi. |
| Ombor qoldig‘i. [read_stock](../tests/regression/test_orders/helpers/flows/stock.py#L43), [open_route](../utils/base_pages/angular_base_page.py#L320) | `read_stock()` aniq mahsulot ID va sarlavha bilan `open_route(..., timeout=120_000)` chaqiradi. Base ichida `main` DOM’ga qo‘shilishi uchun 20 s gacha beriladi. Qoldiqlar jadvalida lot qatorlari hamda bo‘sh natija alohida tekshiriladi. | Bitta joydagi navigatsiya chegarasini base’ga ko‘chirish rezerv, ikki ombor va qaytarish testlariga birga ta’sir qiladi. Jadval uchun `grid(root=...)` va `grid(state="empty")` mavjud. Bir omborda bir nechta lot bo‘lishi va qoldiq haqiqatan nol ekanini `read_stock()` tekshiradi. [Rezerv](../tests/regression/test_orders/business_cases/stock/test_cancel_reserve.py#L44) · [Ikki ombor](../tests/regression/test_orders/business_cases/stock/test_two_warehouses.py#L19) · [Qaytarish](../tests/regression/test_orders/business_cases/returns/test_promoted_return.py#L18) |
| API orqali sessiyani tiklash. [Sessiya so‘rovi](../tests/regression/test_orders/helpers/group_auth.py#L45), [login retry](../tests/regression/test_orders/helpers/auth_recovery.py#L92) | Sessiya HTTP so‘roviga 30 s berilgan. Order katalogidagi yagona `sleep()` API login HTTP 500 qaytargach, bir martalik qayta urinish oldidan 15 s kutadi. | Ikkalasi sessiya helperida qoladi. Ular uchun kutishni qisqartirish yoki uzaytirish UI komponentining sekin yuklanishini hal qilmaydi. |

### Takrorlangan Order qadamlari

Quyidagi havolalar 1-bosqichdagi, refaktordan oldingi kodni ko‘rsatadi.

| Takror va dalil | 3-bosqichdagi qaror |
|---|---|
| Yakunlash bosqichida aynan bitta ko‘rinadigan `ИТОГО` labelini kutish **9 joyda** yozilgan. [Qo‘lda chegirma — 6 joy](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_manual_discount.py#L131) · [Tayyor chegirma — 2 joy](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_preset_discount.py#L46) · [Aralash aksiya — 1 joy](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/promotions/test_mixed_promotions.py#L26) | Yakunlashga o‘tishni Order flow’ga yig‘ish. Flow `Далее`ni bosadi va yangi bosqichdagi `ИТОГО` maydoni tayyorligini base orqali kutadi. Bir xil label eski bosqichda ham uchrasa, yangi bosqich doirasi va yagona maydon shartini saqlash kerak. Har test o‘z chegirmasi va jamini tekshiradi. |
| Klientni tanlash → `Далее` → narx turi va ombor bo‘yicha mahsulot tanlash ketma-ketligi to‘lov va qaytarish testlarida bir xil. Miqdor chegirmasi ham shu qadamlarni ishlatadi. [To‘lov](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/payments/test_promoted_order_payment.py#L59) · [Qaytarish](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/returns/test_promoted_return.py#L139) · [Miqdor chegirmasi](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/promotions/test_01_quantity_discount.py#L31) | Umumiy o‘tishni Order flow’ga chiqarish. Unda `b_input()` va mavjud `select_order_product()` chaqiriladi. Miqdor, aksiya va pul tekshiruvlarini ssenariy beradi. |
| Tayyor chegirma testi boshqa test modulidan `_open_goods`, `_save_draft`, `_saved_amounts` va `_number`ni import qiladi. [Import](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_preset_discount.py#L9) · [Amaldagi helperlar](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_manual_discount.py#L26) | Allaqachon umumiy ishlatilayotgan chegirma amallari va tekshiruvlarini Order helper moduliga ko‘chirish. Yaratish, mahsulotni tanlash, TTN bo‘yicha saqlash va tahrirga ochishda mavjud flow’lardan foydalanish. [Order flow’lari](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/helpers/flows/order.py#L20) |

**2-bosqichda birinchi tekshiruv** — Order’da `Далее` bosilgandan keyin eski bosqich qachon yopilishi, yangi `ИТОГО` maydoni qachon tayyor bo‘lishi va shu orada qaysi loader ko‘rinishini trace yoki haqiqiy formada solishtirish. Shu dalil flow uchun tayyorlik shartini belgilaydi. 1-bosqichdagi xulosalar kod tahliliga asoslangan.

## 2-bosqich — Order yakunlash bosqichi

**Dalil.** 2026-11-15 dagi mahalliy `test_09_second_client_reuses_limit` yozuvi, birinchi urinish. Ssenariy Order yaratishda bonus takliflarini ko‘rgach, ikkinchi `Далее` bilan yakunlashga o‘tadi. Quyidagi vaqtlar `call@41643` click **chaqiruvi boshidan** hisoblangan. Playwright bosishni +27 ms da bajara boshlagan va +31 ms da tugatgan. DOM kadrlari orasidagi o‘zgarishning aniq millisekundini bu yozuv bermaydi. [Ssenariydagi qadam](../tests/regression/test_orders/business_cases/promotions/test_bonus_limit.py#L143)

| Vaqt | Trace’dagi dalil |
|---|---|
| +36 ms | `before@call@41649` kadrida oldingi bosqichning takliflar jadvali hali DOM’da. Yakuniy `ИТОГО` maydoni yo‘q. |
| +106 ms | `after@call@41649` kadrida Order formasi ichida bitta `smt-control` ostida aynan `ИТОГО` labeli va `readonly` input bor. Input qiymati allaqachon `140 000`. Demak, maydon birinchi marta +36 va +106 ms oralig‘ida qayd etilgan holatga kelgan. |
| +422 va +553 ms | `input@call@41699` kadrida `Тип оплаты` selectining ichida `smt-icon[key="loader"]` bor. `after@call@41715` kadrida u yo‘q. Shu oraliqda `ИТОГО` qiymati `140 000` bo‘lib turgan. |
| +1 280 va +1 295 ms | To‘lov turi tanlangach, `call@41761` input ko‘rinishini, `call@41763` qiymati `140 000` ekanini muvaffaqiyatli tasdiqlagan. Bu assertionlar qachon bajarilganini ko‘rsatadi. Maydon DOM’da oldinroq mavjud edi. |

Click boshidan yakuniy maydon qayd etilguncha olingan kadrlarda `.smt-skeleton`, `.block-ui-overlay` yoki `[aria-busy="true"]` topilmadi. Ikki kadr orasida qisqa loader chiqib yo‘qolganini trace orqali istisno qilib bo‘lmaydi.

**Flow kutadigan shart**

1. Order flow `Далее`ni bir marta bosadi. Faol Order formasida yakunlash bosqichiga xos, aynan `ИТОГО` labeliga tegishli yagona ko‘rinadigan maydonni kutadi. Trace’da bu maydon `readonly`, shuning uchun uni o‘qish uchun tahrirlashga tayyor bo‘lishini talab qilish xato bo‘ladi.
2. Ssenariy kutilgan summani bilsa, uni parametr sifatida beradi. Flow mavjud `AutoBasePage.input(label="ИТОГО", expect_value=...)` orqali qiymat mos kelguncha kutadi. Sonning minglik bo‘shliqlarini base hisobga oladi. Kutilgan summa berilmasa, maydonning ko‘rinishi faqat bosqich ochilganini tasdiqlaydi. Summani tekshiradigan ssenariy o‘z qiymatini alohida beradi. [A2 input](../utils/base_pages/angular_base_page.py#L350)
3. Tez o‘tishda shart bajarilishi bilan davom etadi. Kechikkan renderda shu shart umumiy UI timeoutigacha qayta tekshiriladi. Butun sahifada spinner paydo bo‘lishi yoki yo‘qolishini majburiy kutish bu qadamga qo‘shilmaydi. Keyingi amal to‘lov turini tanlash bo‘lsa, uning tayyorligini `b_input()` o‘z dropdown’i ichida tekshiradi. [A2 select](../utils/base_pages/angular_base_page.py#L550)
4. **Ochiq tekshiruv.** Agar haqiqiy bloklovchi overlay tayyor qiymat ustida qolsa, faqat readonly qiymatni o‘qish bloklanishni aniqlay olmaydi. Keyingi interaktiv amal bosish yoki tanlash mumkin bo‘lguncha kutishi kerak. Bloklovchi loader kech chiqqan yoki tugamagan o‘tish uchun mos trace topilganda uning doirasi va timeout diagnostikasini tasdiqlaymiz. Bu yozuvdan universal millisekund yoki global loader locatori chiqarilmaydi.

**Qayta topish uchun.** Dastlabki ishchi nusxadagi `test-results/runs/20261115T005850Z-8e4a4f38/test_09_second_client_reuses_limit-dbe8a32c/attempt-01/trace.zip`, SHA-256 `34207fc8cabb5ea5db86927cd88a02eab4e017fefb3dfc0fd9ab567934e57740`. Yuqoridagi kadrlar arxivning `trace.trace` faylidan olindi. Arxiv mahalliy test artifactidir.

## 3-bosqich — joriy qilingan o‘zgarishlar

- **Trace qamrovi.** Asosiy ishchi nusxadagi `test-results/`, `output/`, `outputs/` hamda `local-ci-validation` worktree’dagi `test-results/` ZIP arxivlarida 53 ta noyob `.trace` oqimi ko‘rib chiqildi. Asosiy frame’ning A2 Order URL’i va `Далее` locatori birga qayd etilgan ikkita click bitta yozuvga tegishli. Ikkinchisi yuqorida tahlil qilingan yakunlash o‘tishi. Qidiruv boshqa selector orqali bosilgan yoki snapshoti yo‘q amallarni qamramaydi. Kechikkan yoki doimiy bloklovchi loader masalasi ochiq.
- **Yakunlash.** `open_order_summary()` bir marta bosadi, Order formasidagi bitta ko‘rinadigan `ИТОГО` labelini kutadi va maydonni mavjud `base.input()` orqali tekshiradi. Kutilgan summa berilsa, shu qiymatni ham kutadi. Qo‘lda chegirma, tayyor chegirma va aralash aksiyadagi 9 ta mahalliy locator tekshiruvi shu flow bilan almashtirildi. Aralash aksiya turida summa to‘lov parametrlari kiritilgach tekshiriladigan ssenariyning ketma-ketligi saqlandi. [Order flow](../tests/regression/test_orders/helpers/flows/order.py#L166)
- **Loader oynasi.** Umumiy A2 oynasi (8 s) va markerli Order guruhi oynasi (250 ms) endi base qatlamida belgilangan. Fixture faqat Order guruhiga qaysi qiymat qo‘llanishini tanlaydi. Bu ko‘chirish loaderning paydo bo‘lish yoki tugash shartini o‘zgartirmaydi. [Vaqtlar](../utils/base_pages/__init__.py)
- **Navigatsiya.** Yangi kontekstdagi dashboard hujjatini va ID bo‘yicha ombor sahifasini ochish chegarasi base qatlamidagi `A2_DOCUMENT_TIMEOUT_MS` (120 s) orqali boshqariladi. Dashboard hujjati `domcontentloaded`gacha kutiladi, so‘ng dashboard yoki login URL’i va tegishli filial tekshiriladi. URL hamda filial kutishi umumiy UI chegarasini (60 s) oladi. Sessiya HTTP so‘rovining o‘z vaqti saqlandi. [Vaqtlar](../utils/base_pages/__init__.py) · [Dashboard](../tests/regression/test_orders/helpers/group_auth.py) · [Ombor](../tests/regression/test_orders/helpers/flows/stock.py)
- **Klient va mahsulot.** To‘lov, qaytarish, miqdor chegirmasi va ikki chegirma modulining tayyorlov qadami bir xil `select_client_product()` flow’idan foydalanadi. Flow klientni tanlaydi, mahsulot bosqichini kutadi va mavjud `select_order_product()`ga uzatadi. Kutilgan miqdor, narx va chegirmani ssenariy tekshiradi. [Order flow’lari](../tests/regression/test_orders/helpers/flows/order.py)
- **Chegirmalar.** Qo‘lda va tayyor chegirma testlari uchun umumiy mahsulot tayyorlash, summani o‘qish, qoralamani saqlash va saqlangan qiymatlarni tekshirish bitta modulga chiqarildi. [Umumiy helperlar](../tests/regression/test_orders/helpers/discounts.py)
- **Tekshiruv.** O‘zgargan Python fayllari sintaksisi, importlar, flow chaqiriladigan joylar va diff statik tekshirildi. Testlar va collection ishga tushirilmadi. Loader kuzatish oynasi bo‘yicha qaror uchun kechikish dalili kerak.

## 4-bosqich — sonli maydonni tahrirlash

**Order dalili.** #3689 hisobotidagi `test_08_quantity_threshold` ssenariysi mavjud buyurtmada miqdorni 10 dan 9 ga o‘zgartirgan. Vaqtlar `call@34236` (`fill("9")`) boshiga nisbatan berilgan. Tarmoq so‘rovi boshlangan vaqt va HTTP javob holati bir qatorda keltirilgan. [#3689 Allure hisoboti](https://qa-assistant.uz/playwright-reports/44229787309-1.html) · [Order ssenariysi](../tests/regression/test_orders/business_cases/promotions/test_mandatory_conditions.py#L150)

| Vaqt | Kuzatuv |
|---|---|
| −54 ms | Mahsulot qatorida `quantity` qiymati 10. Miqdor va quti miqdori (`quantity_box`) maydonlari `smt-input[smtbehavior="biruni-number"]` ichida joylashgan. |
| −27…−2 ms | `Backspace` bosilgan. −10 ms da `get_box_quant` so‘rovi `quant="0"` bilan boshlangan va HTTP 401 qaytargan. `after@call@34230` kadrida input bo‘sh. |
| 0…+57 ms | `fill("9")` bajarilgan. +21 ms da ayni endpointga `quant="9"` yuborilgan va HTTP 200 qaytgan. `Tab` +26 ms da bosilgan. +57 ms da maydon qiymati 9 ekani tasdiqlangan. |
| +90…+220 ms | `Далее` bosilgach, `before@call@34260` kadrida `ИТОГО` qiymati `63 000` bo‘lgan. Bu qayd etilgan qiymat. Hisobning aynan qachon tugagani va uni `Tab` hodisasi boshlagani trace’dan aniqlanmaydi. |

Test kartasida sessiyani tiklash vaqtida `get_box_quant` uchun 401 javobini qayta ishlash qo‘llanmagani qayd etilgan. Miqdorni almashtirishdagi ortiqcha so‘rovni bartaraf qilish sessiyani tiklash muammosini hal qilganini ushbu trace tasdiqlamaydi.

**UI Kit solishtiruvi.** Brauzerda ikki Biruni maydoni tekshirildi: `precision=14, scale=2, fillwithzero` va `precision=10, scale=2`. Ikkalasida 10 dan 9 ga o‘tishda `Backspace` va keyingi `fill` ikkita `input` hodisasini berdi (bo‘sh qiymat, so‘ng 9). Bevosita `fill("9")` faqat 9 hodisasini berdi. `Tab`dan keyin har ikkisining ko‘rsatilgan va model qiymati 9 bo‘ldi. Birinchi maydonga 1234.50 va ataylab 0 kiritish ham tekshirildi. Order’dagi ikkinchi maydonning DOM turi ko‘rildi, uning tahriri ushbu CI trace’da bajarilmagan. [UI Kit Input](https://uikit.greenwhite.uz/input)

**Joriy qilingan o‘zgarish.** A2 `input()` Biruni sonli maydonida qiymatni bitta `fill` bilan almashtiradi. So‘ralgan `Tab`, maydon qiymatini tekshirish va umumiy UI kutishi saqlanadi. Order summasi uchun biznes tekshiruvi ssenariyda turadi. Amaliy tasdiq mezoni — yangi Smartup trace’da 10 → 9 uchun faqat 9 so‘rovi ketishi va `ИТОГО` 63 000 ga teng bo‘lishi. [A2 input](../utils/base_pages/angular_base_page.py#L350)

## 5-bosqich — serverdan qidiradigan select

**Qamrov.** UI Kit’dagi Single Data Select va 15-noyabrdagi Order `test_09_second_client_reuses_limit` trace’i solishtirildi. Trace faylining yo‘li va SHA-256 qiymati 2-bosqichda berilgan. UI Kit’da Role List so‘roviga 401 qaytganda ham “Ничего не найдено” chiqdi. Bu demo orqali haqiqiy bo‘sh 200 javobini tasdiqlab bo‘lmaydi. [UI Kit Data Select](https://uikit.greenwhite.uz/data-select) · [A2 b_input](../utils/base_pages/angular_base_page.py#L449)

| UI amali | Mavjud imkoniyat va tayyorlik belgisi |
|---|---|
| Klient yoki mahsulotni qidirib tanlash | `value` yoki `search_text` tanlashgacha olib boradi. Server selectida so‘rov maydon kaliti va matniga mos kelishi, spinner yashirinishi va kerakli variant ko‘rinishi kutiladi. Odatiy tanlashdan so‘ng menyu yopiladi. `expect_value` yakuniy qiymatni ham tasdiqlaydi. `stop_after_select` esa ataylab bosishdan keyin qaytadi. |
| Birinchi variant yoki aniq ombor/narx variantini tanlash | `select_first` ko‘rinadigan birinchi variantni oladi. `option_contains` tanlangan matn va qo‘shimcha belgilar mos keladigan bitta variantni kutadi. Sekin renderda endi avval birinchi qator ko‘rinadi, keyin zarur bo‘lsa scroll bilan navbatdagi sahifa kutiladi. |
| Tanlovni tozalash, qiymatni o‘qish va tekshirish | `clear=True` yolg‘iz chaqirilganda Escape’dan so‘ng menyu yopilgani va qiymat bo‘shligi tekshiriladi. `return_value` o‘qiydi, `expect_value` esa kutilgan qiymatni kutadi. UI Kit rol maydonida tozalash va Escape brauzerda tekshirildi. |
| Faqat ochish, qidirib ro‘yxatni tanlamasdan ko‘rish, mustaqil yopish | Demo’da ochish va Escape bilan yopish mumkin. Joriy `b_input()` parametrlarsiz input locatorini qaytaradi. `search_text` avtomatik tanlaydi. Uch amal uchun alohida public chaqiruv hozir yo‘q. |
| Bo‘sh natijani tekshirish | Alohida assertion yo‘q. Taklif etiladigan shart — aynan shu qidiruvga muvaffaqiyatli javob kelgan, komponent spinneri tugagan, ro‘yxatda variant yo‘q va bo‘sh holat ko‘ringan. HTTP yoki sessiya xatosi alohida ko‘rsatilishi kerak. |
| UI Kit’dagi qo‘shimcha rejimlar | Demo’da bir natijani avtomatik tanlash, All belgisi, pin, smart search tugmasi, qo‘shimcha tugmalar va disabled/required holatlari bor. Joriy metod tanlangan qiymatni tekshira oladi. Bu maxsus amallar uchun alohida parametr yo‘q. Ularning qaysi biri kerakligini Smartup formasida shu rejim uchraganda tasdiqlaymiz. |

**Order dalili.** Quyidagi vaqtlar tegishli `fill` boshidan olingan. Mos so‘rov muvaffaqiyatli tugagach, kerakli variant bosilgan. Trace’dan olingan uchta haqiqiy payload mavjud `_lookup_query_finished` bilan ham solishtirildi: mos matn va kalit qabul qilindi, boshqa matn yoki kalit rad etildi.

| Maydon | So‘rov boshlanishi va davomiyligi | Variantni bosish |
|---|---|---|
| Klient, `call@41331` | `persons`, +311 ms, 162 ms, HTTP 200 | +504 ms |
| Mahsulot, `call@41467` | `inventory_products`, +318 ms, 216 ms, HTTP 200 | +585 ms |
| To‘lov turi, `call@41729` | `payment_type`, +320 ms, 152 ms, HTTP 200 | +515 ms |

**Locator tuzatishi.** Order kadrida `Выберите...` faqat ichki inputda edi. UI Kit’dagi `Search roles...` bitta komponentda ikki marta topildi. Eski locator `index=0` uchun hostning ajdodlaridan select qidirib, hech narsa topmadi. Endi avval har bir mos element eng yaqin selectga bog‘lanadi, keyin komponentlar orasidan indeks tanlanadi. Demo’da `Search roles...` uchun bitta, `Search users...` uchun 15 ta DOM mosligidan 8 ta alohida komponent chiqdi. Order’dagi ikkinchi mahsulot qatorini tanlash ham shu yo‘ldan foydalanadi. [Locator](../utils/base_pages/angular_base_page.py#L527) · [Mahsulot tanlovi](../tests/regression/test_orders/helpers/flows/order.py#L202)

**Kutish qarori.** Sekin qidiruvda umumiy timeout ichida aynan so‘ralgan matnning javobi, keyin komponent holati kutiladi. Eski matn javobi yangi qidiruvni tugatmaydi. Bir xil kalit va aynan bir xil matn bilan takror so‘rovlarni hozirgi predicate ajratmaydi. Spinner yo‘qolmay qolsa tanlash kutishda to‘xtashi kerak. Bu nosozlik va teskari tartibda keladigan javoblar uchun real Order yozuvi hali yo‘q. Single va multi select so‘rovni tinglash qismini birga ishlatadi; har biri o‘z menyusi va variantini tekshiradi. [Ichki helper](../utils/base_pages/angular_base_page.py#L63)

**Keyingi qaror.** Ochiq qolgan asosiy amallar uchun mavjud `b_input()`da mustaqil ochish, qidirish, yopish va bo‘sh natijani kutishni ifodalash taklif qilinadi. Bu Order’da klient, mahsulot yoki to‘lov turini tanlamasdan turib natijani tekshirish imkonini beradi. Public kontrakt kengayishi loyiha qoidasiga ko‘ra alohida tasdiqlanadi. [Loyiha qoidasi](../skills/project-guide/SKILL.md)

## Boshlang‘ich dalillar

- Base qatlamidagi umumiy UI vaqti hozir 60 soniya. #3689 bo‘yicha ishchi nusxada dashboard va ombor oqimlari 120 soniyani o‘zi belgilaydi. Birinchi ko‘chirish nomzodlari shular. [Umumiy vaqt](../utils/base_pages/__init__.py) · [Dashboard](../tests/regression/test_orders/helpers/group_auth.py) · [Ombor](../tests/regression/test_orders/helpers/flows/stock.py)
- A2 base ko‘rinadigan skeleton va aria-busy holatini kutadi. Forms monitorida ichki vidjet band turganda ham sahifa ishlagani oldin kuzatilgan. Shu sabab keyingi amal uchun kerakli tugma, tahrirlash mumkin bo‘lgan maydon yoki jadval qatorini ham tekshiramiz. [A2 base](../utils/base_pages/angular_base_page.py) · [Loader bo‘yicha kuzatuv](../skills/smartup-guide/references/form-monitor/check-loader.md)
- UI Kit’da komponentning tuzilishi va hodisalarini o‘rganamiz. Umumiy locator tanlashdan oldin uni Smartup formasida tasdiqlaymiz. #3689 dagi sessiya bloklanishini sekin yuklanishdan alohida ko‘rib chiqamiz. [UI Kit Input](https://uikit.greenwhite.uz/input) · [UI Kit Skeleton](https://uikit.greenwhite.uz/skeleton) · [#3689 run](https://github.com/turgunovjasur/Playwright/actions/runs/44229787309)

## Yangilanishlar

Har bosqich boshlanganda holati **Jarayonda** deb belgilanadi. Yakunida sana, o‘zgarish yoki dalil havolasi va keyingi qadam yoziladi. Kod yozilgan, lekin amaliy tekshiruv qolgan ish **Tekshiruv kutilmoqda** holatida turadi.

| Sana | O‘zgarish | Keyingi qadam |
|---|---|---|
| 2026-11-18 | Reja yaratildi. #3689 va UI Kit bo‘yicha avvalgi kuzatuvlar kiritildi. | 1-bosqich — kutishlar ro‘yxatini tuzish. |
| 2026-11-18 | Ish doirasi Angular A2 bilan cheklandi. Base, umumiy flow va test vazifalari hamda mahalliy kutish istisnosi aniqlashtirildi. | A2 Order ssenariylarida kutishlar bilan birga takrorlangan UI qadamlarini ham ro‘yxatga olish. |
| 2026-11-18 | Base funksiya chegarasi komponent bo‘yicha belgilandi. Komponentning UI’da tasdiqlangan barcha amallari bitta metod orqali bajarilishi rejaning qabul mezoniga kiritildi. | Komponent auditida UI amali, mos base chaqiruvi va tayyorlik belgisini yonma-yon yozish. |
| 2026-11-18 | Komponent metodi mos kutish helperini ichkaridan chaqirishi aniqlashtirildi. | Kutishlar ro‘yxatida qayta foydalanish mumkin bo‘lgan mavjud helperlarni belgilash. |
| 2026-11-18 | 1-bosqich bajarildi. A2 va Order kutishlari, 250 ms fixture, qayta ishlatiladigan helperlar va takrorlangan Order qadamlari yozildi. Testlar ishga tushirilmadi. | 2-bosqich — Order bosqichi almashishida loader va kerakli maydon tayyorligi orasidagi bog‘lanishni tekshirish. |
| 2026-11-18 | 2-bosqich alohida `codex/angular-order-kutish` branchida boshlandi. Order trace’idan yakuniy maydon va to‘lov selecti spinnerining vaqt tartibi yozildi. | Kechikadigan yoki tugamaydigan bloklovchi loader kuzatilgan yozuv bilan qolgan holatlarni tasdiqlash. |
| 2026-11-18 | 3-bosqich boshlandi. Yakunlash qadami umumlashtirildi, dashboard va ombor navigatsiyasi base vaqtidan foydalanadi. | Klient va mahsulot tanlash, yakunlash va chegirma helperlari ajratildi. Qolgan ish — loader oynasi uchun dalil va amaliy tekshiruv. |
| 2026-11-18 | 4-bosqichda #3689 asl trace’i va ikki UI Kit sonli maydoni solishtirildi. A2 input ichidagi oraliq tozalash olib tashlandi. | Smartup’da qayta tekshirish ruxsatini kutish. Navbatdagi tahlil — 5-bosqichdagi server select amallari. |
| 2026-11-18 | 5-bosqichda UI Kit, Order trace’i va public API solishtirildi. Placeholder indeksi, sekin ro‘yxat va tozalash kutishlari yangilandi. Branchdagi Python sintaksisi va diff statik tekshirildi. | Yetishmayotgan select amallari uchun kontraktni kelishish. Smartup test runi uchun tasdiq kutilmoqda. |
