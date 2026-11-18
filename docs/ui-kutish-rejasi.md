# Smartup Angular (A2) testlarida kutishlarni yaxshilash rejasi

**Yangilangan sana:** 2026-11-18

**Hozirgi holat:** 2-bosqich jarayonda. Mavjud Order trace’ida yakunlashga o‘tish tekshirildi va flow kutadigan shart belgilandi. Kech chiqadigan yoki tugamay qoladigan bloklovchi loader uchun dalil ochiq.

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
| 3 | Rejada | Umumiy kutishlarni A2 base funksiyalariga, takrorlangan UI qadamlarini tegishli flow’ga ko‘chirish. Dashboard va ombordagi 120 soniyalik kutishlarni birinchi bo‘lib baholash. | Umumiy UI timeoutlari base qatlamidan olinadi. Mahalliy istisno qolsa, sababi ro‘yxatda ko‘rsatilgan. Tez holat ortiqcha kutmaydi, timeout xabari esa qaysi holat kutilganini bildiradi. |
| 4 | Rejada | Sonli input. UI Kit va Smartup buyurtma formasida 10 → 9 tahririni solishtirish. Maydon qiymati, oraliq 0 so‘rovi, Tab’dan keyingi hisob va yakuniy summani kuzatish. | Kiritish usulini umumiy input() metodiga qo‘llashdan oldin yana bitta sonli maydonda mosligi tekshirilgan. Summaga oid biznes tekshiruvi testda qolgan. |
| 5 | Rejada | Serverdan qidiradigan select. UI Kit va A2 formada komponent amallarini ro‘yxatga olib, har birini mavjud `b_input()` imkoniyatiga solishtirish. Har bir amal uchun tayyorlik belgisi va yetishmayotgan imkoniyatni qayd etish. | Tasdiqlangan har bir amalni test aynan `b_input()` orqali bajara olishi tekshirilgan. Sekin qidiruv, kech kelgan eski javob, bo‘sh natija va yo‘qolmay qolgan spinner uchun kutiladigan holat ko‘rsatilgan. |
| 6 | Rejada | O‘zgarishlarni statik tekshirish. Testlarni ishga tushirish so‘ralgach, ta’sirlangan ssenariylar va shu base funksiyalarini ishlatadigan boshqa formalarda tekshirish. | Run havolasi, natija va ochiq muammolar yozilgan. Sekin holat bilan birga odatiy tez holatda ortiqcha kutish paydo bo‘lmagani ham tekshirilgan. |

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

| Takror va dalil | 3-bosqichdagi qaror |
|---|---|
| Yakunlash bosqichida aynan bitta ko‘rinadigan `ИТОГО` labelini kutish **9 joyda** yozilgan. [Qo‘lda chegirma — 6 joy](../tests/regression/test_orders/business_cases/discounts/test_manual_discount.py#L131) · [Tayyor chegirma — 2 joy](../tests/regression/test_orders/business_cases/discounts/test_preset_discount.py#L46) · [Aralash aksiya — 1 joy](../tests/regression/test_orders/business_cases/promotions/test_mixed_promotions.py#L26) | Yakunlashga o‘tishni Order flow’ga yig‘ish. Flow `Далее`ni bosadi va yangi bosqichdagi `ИТОГО` maydoni tayyorligini base orqali kutadi. Bir xil label eski bosqichda ham uchrasa, yangi bosqich doirasi va yagona maydon shartini saqlash kerak. Har test o‘z chegirmasi va jamini tekshiradi. |
| Klientni tanlash → `Далее` → narx turi va ombor bo‘yicha mahsulot tanlash ketma-ketligi to‘lov va qaytarish testlarida bir xil. Miqdor chegirmasi ham shu qadamlarni ishlatadi. [To‘lov](../tests/regression/test_orders/business_cases/payments/test_promoted_order_payment.py#L59) · [Qaytarish](../tests/regression/test_orders/business_cases/returns/test_promoted_return.py#L139) · [Miqdor chegirmasi](../tests/regression/test_orders/business_cases/promotions/test_01_quantity_discount.py#L31) | Umumiy o‘tishni Order flow’ga chiqarish. Unda `b_input()` va mavjud `select_order_product()` chaqiriladi. Miqdor, aksiya va pul tekshiruvlarini ssenariy beradi. |
| Tayyor chegirma testi boshqa test modulidan `_open_goods`, `_save_draft`, `_saved_amounts` va `_number`ni import qiladi. [Import](../tests/regression/test_orders/business_cases/discounts/test_preset_discount.py#L9) · [Amaldagi helperlar](../tests/regression/test_orders/business_cases/discounts/test_manual_discount.py#L26) | Allaqachon umumiy ishlatilayotgan chegirma amallari va tekshiruvlarini Order helper moduliga ko‘chirish. Yaratish, mahsulotni tanlash, TTN bo‘yicha saqlash va tahrirga ochishda mavjud flow’lardan foydalanish. [Order flow’lari](../tests/regression/test_orders/helpers/flows/order.py#L20) |

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
