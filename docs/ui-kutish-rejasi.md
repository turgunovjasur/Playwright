# Smartup Angular (A2) base funksiyalari bo‘yicha ish rejasi

## Asosiy reja — 30 bosqich

2026-11-18 holatiga ko‘ra, 29 ta public metodning har biriga alohida bosqich ajratildi. 30-bosqich — yakuniy regression run. 1–3-metodlar Order’da qisman tekshirildi. 4-bosqichda ism yozish va qidiruv kutishi Smartup’da tekshirildi. Mavjud shaxsni tanlash bo‘yicha ochiq masala quyida qayd etilgan. 5-bosqichda oddiy select va qidiruvli select solishtirildi. 6–9-bosqichlarda ko‘p tanlov, sana, checkbox va radio brauzerda tekshirildi. 10–29-bosqichlarning natijalari ham jadvalda. Qayta tekshirishda birinchi navbat — 6-bosqichdagi ikki tanlovdan keyin menyuning yangilanishi. 30-bosqichdagi test runi boshlanmagan.

| Bosqich | Metod yoki ish | Holat | Tekshiriladigan amallar |
|---|---|---|---|
| 1 | `input()` | Qisman tekshirildi (Order) | Matn yozish, almashtirish, tozalash, Tab va formatlangan qiymatni o‘qish. |
| 2 | `b_input()` | Qisman tekshirildi (Order) | Menyuni ochish, qidirish, tanlash, tozalash, bo‘sh javob va komponentning qo‘shimcha rejimlari. |
| 3 | `wait_for_loader()` | Qisman tekshirildi (Order) | Sahifa va lokal yuklanish belgilarining doirasi, kech chiqishi va timeout xabari. |
| 4 | `autocomplete()` | Amaliy audit bajarildi, variant tanlash ochiq | Matn kiritish, takliflar kelishi, tanlash va natija topilmagandagi holat. |
| 5 | `ui_select()` | Audit bajarildi, alohida qidirish ochiq | Aksiya formasida tanlash va qiymatni o‘qish, UI Kit’da filtrlash va bo‘sh natija tekshirildi. |
| 6 | `multiselect()` | Audit bajarildi, ikkita qiymatni ketma-ket tanlashda xato topildi | Bir nechta variant tanlash, tanlovni o‘qish, olib tashlash va tozalash. |
| 7 | `date_picker()` | Asosiy sana amallari tekshirildi | Sana yozish, kalendardan tanlash va ko‘rsatilgan sanani tekshirish. |
| 8 | `checkbox()` | Audit bajarildi, oraliq holat ochiq | Belgilash, belgini olib tashlash va joriy holatni o‘qish. |
| 9 | `radio()` | Tanlash va guruh holati tekshirildi | Guruh ichida variant tanlash va tanlangan holatni tekshirish. |
| 10 | `choice()` | Qisman — UI Kit va Smartup kodi tekshirildi | Label orqali kerakli guruhni topish va uning variantini tanlash. |
| 11 | `click()` | Brauzerda tekshirildi | To‘g‘ri tugma yoki elementni topish va bosish mumkin bo‘lguncha kutish. |
| 12 | `tab()` | Smartup’da ishladi, UI Kit varianti farq qiladi | Kerakli tab yoki bo‘limni ochish va faol holatni aniqlash. |
| 13 | `action()` | Qisman — bevosita amal va menyu tekshirildi | Menyu amalini topish va kerakli bandni tanlash. |
| 14 | `page_link()` | Smartup’da tekshirildi | Formadagi havolani topish va ochish. |
| 15 | `confirm_biruni()` | Rad etish ikkala UI’da tekshirildi | Tasdiqlash dialogi matni, tugmalari va yopilishi. |
| 16 | `close_biruni_alert()` | UI Kit dialogi va Smartup sahifa xatosi solishtirildi | Kutilgan xabarni aniqlash va ogohlantirishni yopish. |
| 17 | `grid()` | Qator tanlash va bo‘sh holat tekshirildi | Qatorlar yuklanishi, bo‘sh jadval, qatorni belgilash va ochish. |
| 18 | `grid_controller()` | Qidirish, yangilash va sozlama menyusi tekshirildi | Qidirish, filtrlash, qayta yuklash va jadval boshqaruvlari. |
| 19 | `grid_setting()` | Qisman — dialog ochildi | Sozlamani ochish, ustunni topish va o‘zgarish qo‘llanganini tekshirish. |
| 20 | `grid_cell()` | Matnli katak tekshirildi | Qator va ustun bo‘yicha katak qiymatini o‘qish va kutish. |
| 21 | `text()` | Sahifa matni tekshirildi | Berilgan doirada matn va maydon qiymati ko‘rinishini tekshirish. |
| 22 | `form_view()` | Readonly maydon tekshirildi | Ko‘rish formasida labelga tegishli qiymatni o‘qish va tekshirish. |
| 23 | `expect_page()` | URL va sarlavha tekshirildi | Sahifa manzili, sarlavha, bloklovchi loader va xato holati. |
| 24 | `open_route()` | Ikkita ro‘yxat formasi ochildi | Formani manzili orqali ochish va kerakli sahifa tayyorligini kutish. |
| 25 | `navigate_to()` | Menyudan o‘tish tekshirildi | Asosiy menyudan maqsadli sahifaga o‘tish. |
| 26 | `navigate_to_form()` | Menyu ustuni orqali o‘tish tekshirildi | Navigatsiya bo‘limi, menyu bandi va forma havolasi orqali o‘tish. |
| 27 | `switch_filial()` | Qisman — bitta filial mavjud | Filialni almashtirish va faol filialni tasdiqlash. |
| 28 | `hide_ui()` | Yashirish amali tekshirildi | Yashirish yoki olib tashlash qayerda ishlatilganini va kuzatuvga ta’sirini tekshirish. |
| 29 | `date()` | Sana chegaralari tekshirildi | Sana hisoblash va formatlashni chaqiruvchi metodlar bilan solishtirish. |
| 30 | Yakuniy regression run | Boshlanmagan | #3689 da yiqilgan ssenariylar va o‘zgargan base funksiyalarini ishlatadigan boshqa A2 formalarida natijani tekshirish. |

Komponent bosqichini yopishda UI Kit’dagi amallar Smartup formasida solishtiriladi. Har bir amal uchun base chaqiruvi, kutish sharti va dalil yoziladi. Jadvaldagi amallar boshlang‘ich ro‘yxat. Solishtirishda topilgan qo‘shimcha amallar ham tegishli qatorga kiritiladi. UI Kit analogi bo‘lmagan yordamchi metodlarda chaqiruvchi kod va tegishli Smartup xatti-harakati tekshiriladi.

## 4-bosqich — ism maydonidagi autocomplete

Setup’dagi jismoniy shaxs va klient yaratish ssenariylari bitta umumiy flow orqali `autocomplete()`ni chaqiradi. Ikkalasi yangi ism yozib, bo‘sh natijani kutadi. [Flow](../tests/smoke/test_setup/flow_setup/flow_natural_person.py#L30) · [A2 metodi](../utils/base_pages/angular_base_page.py#L312)

| Amal | Brauzerda ko‘rilgan natija | Base qamrovi |
|---|---|---|
| Yozish va yopish | UI Kit’dagi Data Select rol maydonida yozish menyuni ochdi. Escape menyuni yopdi va qidiruv matni saqlandi. Smartup’dagi «Физическое лицо (создание) → Имя» maydoni ham `smt-data-select` ichidagi `smt-select-trigger` va inputdan iborat. | Mavjud `autocomplete()` shu amallarni bitta chaqiruvda bajaradi. [UI Kit misoli](https://uikit.greenwhite.uz/data-select) |
| Yangi ism va sekin javob | Smartup’da noyob matn uchun `:table_persons` HTTP 200, `count=0`, `data=[]` qaytardi. «Ничего не найдено» ko‘rindi. Alohida kuzatuvda so‘rov kamida 1,2 s ushlanganida menyu ochiq turdi va «Ищем результаты» ko‘rindi. Javobdan keyin helper menyuni yopdi va ism maydonda qoldi. | Metod mos javob statusini tekshiradi va selectning mavjud bandlik helperini chaqiradi. Lokal HTTP 401 avval elementni kutish xatosiga olib keldi. Tuzatishdan so‘ng xabarda aynan HTTP 401 chiqdi. |
| Mavjud ismni tanlash | Smartup’da ma’lum QA ismi uchun HTTP 200 va bitta variant qaytdi. Qatorni bosish mavjud shaxsni tahrirlashga o‘tish haqidagi tasdiq oynasini ochdi. «Нет» bosildi. Shu ismni odatdagi `autocomplete()` bilan yozish esa tanlashni ishga tushirmadi. | Mavjud metod qatorni tanlamaydi. Smartup ism maydonida `smtkeyfield` atributi ham topilmadi, shuning uchun kalitga tayanuvchi `b_input()` qidiruvini bu yerga bevosita ko‘chirish tekshirilmagan. |

**Ochiq qaror.** Bitta komponent uchun tanlash kodini takrorlamaslik maqsadida `b_input()`ga chaqiruvchi bergan qidiruv javobi sharti bilan ishlash imkoniyatini ko‘rib chiqish kerak. Yangi ismni tanlamasdan qoldiradigan mavjud ikki setup ssenariysining xatti-harakati saqlanishi kerak. Tahrirlashga o‘tish haqidagi biznes dialogi formaga tegishli. Yangi public API alohida kelishiladi.

## 5-bosqich — bitta variant tanlash

2026-11-18 kuni UI Kit’dagi Select misoli va Smartup A2 «Акция (создание)» formasidagi «Тип акции» maydoni brauzerda solishtirildi. Aksiya saqlanmadi. [UI Kit Select](https://uikit.greenwhite.uz/select) · [Smartup formasi](https://smartup.online/a2/anor/mcg/action%2Badd) · [A2 ui_select()](../utils/base_pages/angular_base_page.py#L1305)

| Amal | Brauzerda kuzatilgan natija | Base qamrovi va kutish sharti |
|---|---|---|
| Oddiy ro‘yxatni ochish va tanlash | Smartup’da `smt-select-trigger` ichidagi `span.truncate` dastlab «Кол-во»ni ko‘rsatdi. Qidiruv inputi yo‘q. Ro‘yxat ochilganda beshta variant ko‘rindi, jumladan «Кол-во» va «Кол-во кейс». Escape tanlamasdan yopdi. | `ui_select(label="Тип акции", value="Сумма", return_value=True)` «Сумма» qaytardi va menyu yopildi. Shu metod bilan «Кол-во» qayta tanlandi. To‘liq matn bo‘yicha tanlash ikki o‘xshash variantni ajratdi. |
| Qidirib tanlash | UI Kit’dagi Country maydonida qidiruv inputi bor. `search_text="Cana", value="Canada"` berilganda metod «Canada»ni tanladi va o‘qidi. | Metod maydon, trigger va variant ko‘rinishini, bosishdan keyin menyu yopilishini hamda input qiymati yoki trigger matni mosligini kutadi. Smartup’dagi «Тип акции»da qidirish amali mavjud emas. |
| Faqat filtrlash va bo‘sh natija | UI Kit’da inputga mos kelmaydigan matn yozilganda «Ничего не найдено» chiqdi. Escape menyuni yopdi. Faqat `search_text="Japan"` berilganda esa helper menyuni ochmadi, oldingi «Canada» qiymati qoldi. | Kodda qidiruv `value` berilgan shox ichida bajariladi. Alohida qidirish, uning bo‘sh natijasini kutish va tanlovni tozalash uchun public amal yo‘q. |

**Base bo‘yicha qaror.** Oddiy tanlashda mavjud variant va yakuniy qiymat tekshiruvlari qayta ishlatiladi. Qidirishni alohida qo‘llashda base aynan ochilgan komponentdagi mos variant yoki bo‘sh natijani kutishi kerak. Hozir dropdown sahifadagi oxirgi ko‘rinadigan menyu orqali olinadi. Bir nechta overlay bilan ishlashi bu auditda tekshirilmagan. UI Kit’da qo‘shimcha All, pin va clear sozlamalari ham bor. Ularning «Тип акции»da ishlatilishi tasdiqlanmagan. Testga lokal timeout qo‘shish talab etilmadi.

## 6-bosqich — ko‘p variant tanlash

UI Kit Multi Data Select’dagi birinchi qidiruvda menyu triggerning `aria-controls` atributi orqali bog‘landi. Avval «Загрузка… / Ищем результаты», keyin «Ничего не найдено» ko‘rindi. Jonli Smartup A2 «Акция (создание)» formasida xuddi shu `smt-multi-data-select` komponenti haqiqiy variantlar bilan tekshirildi. [UI Kit Multi Data Select](https://uikit.greenwhite.uz/multi-data-select) · [A2 multiselect()](../utils/base_pages/angular_base_page.py#L1158)

| Amal | Smartup’da kuzatilgan natija | Base uchun xulosa |
|---|---|---|
| Faollashishni kutish | «Рабочие зоны» bo‘shligida «Тип цены» komponentida `disabled` bor, ichida qidiruv inputi yo‘q. Birinchi ish zonasi tanlangach, `disabled` olib tashlandi va input paydo bo‘ldi. | Ish zonasini tanlash flowga tegishli. Komponent ichida amal boshlanishidan oldin enabled holat va input tayyorligini shu chaqiruvning timeouti bilan kutish kerak. Hozir birinchi `input_value()` sahifa timeoutidan foydalanadi. |
| Ikki variantni ketma-ket tanlash | Ikkita turli narx turi bitta `value=[a, b]` chaqiruvida berildi. Birinchi chip paydo bo‘ldi. Keyingi tanlovda helper DOM’da topilmagan menyu ID’sini kutib timeout berdi. Xuddi shu sahifada ikkinchi qiymat alohida chaqiruvda tanlangach ikkala chip ham o‘qildi. | Har bir tanlovdan keyin chipni tasdiqlash va keyingi qidiruvdan oldin triggerga ayni paytda bog‘langan menyuni qayta topish kerak. Ikkita tanlovni bitta chaqiruvda ishonchli bajarish ochiq. |
| Bittasini olib tashlash va tozalash | Birinchi chipning olib tashlash tugmasi bosilgach, ikkinchi chip qoldi. `clear=True, return_value=True` bo‘sh ro‘yxat qaytardi. | Qo‘shish, o‘qish va hammasini tozalash bor. Berilgan bitta chipni nomi bo‘yicha olib tashlash amali yetishmaydi. UI Kit’dagi All, yig‘ilgan chiplar va pin rejimlari bu Smartup maydonlarida tekshirilmagan. |

## 7–9-bosqichlar — sana, checkbox va radio

| Bosqich | UI Kit va Smartup dalili | Base qamrovi va ochiq joy |
|---|---|---|
| 7 · `date_picker()` | UI Kit «Birth Date» va Smartup «Акция → Срок действия»da bir xil ertangi sana yozildi. Ikkalasida `DD.MM.YYYY` qiymati tasdiqlandi. UI Kit «Due date» va Smartup «Дата начала»da kalendardan «Сегодня» bosildi va `18.11.2026` qaytdi. | Yozishda Enter’dan so‘ng overlay yopilishi va input qiymati kutiladi. Bugungi sanani tanlashda natija kutiladi. UI Kit kalendarida boshqa kunlar va «Очистить» ham bor. Istalgan kunni kalendardan bosish va tozalash public metodda yo‘q. [UI Kit](https://uikit.greenwhite.uz/date-picker) · [Base](../utils/base_pages/angular_base_page.py#L787) |
| 8 · `checkbox()` | UI Kit checkbox va Smartup «Физическое лицо → Клиент» brauzerda bir xil holatlardan o‘tdi — `False → True → False`. Smartup’da element `span[role=checkbox]`. UI Kit’da `aria-checked="mixed"` bo‘lgan namunada base `False` qaytardi. | Belgilash va olib tashlashda base yakuniy holatni kutadi. Qisman belgilangan holatni o‘chirilgan holatdan ajratib o‘qish ochiq. «Клиент» maydonida oraliq holat kuzatilmadi. [UI Kit](https://uikit.greenwhite.uz/checkbox) · [Base](../utils/base_pages/angular_base_page.py#L929) |
| 9 · `radio()` | UI Kit’da «Blue» tanlangach «Red» belgisi yechildi. Smartup «Физическое лицо → Пол»da «Женский» tanlangach «Мужской» belgisi yechildi. «Мужской» qayta tanlandi. | Mavjud metod variantni tanlaydi va ikkala holatni ham tekshiradi. `return_value=True` bilan ham sukut bo‘yicha tanlangan holat kutiladi. Tanlanmagan variantni tekshirishda `expect_checked=False` berildi. Klaviatura bilan boshqarish tekshirilmagan. [UI Kit](https://uikit.greenwhite.uz/radio) · [Base](../utils/base_pages/angular_base_page.py#L1004) |

## 10–29-bosqichlar — 18-noyabrdagi tekshiruvlar

| Bosqich | Qayerda va nima tekshirildi | Base kutishi yoki ochiq joy |
|---|---|---|
| 10 · `choice()` | UI Kit Button Group’da «Day» bosilgach uning `aria-pressed` qiymati true, «Week»niki false bo‘ldi. Smartup’dagi yagona chaqiruvchi company security formasida sessiyalar soni sozlamasini tanlaydi. Loyiha dossieriga ko‘ra, bosish uni darhol saqlaydi. Ko‘rilgan 52 ta noyob mahalliy trace oqimida security forma selektori yoki shu label bilan kadr topilmadi. | Metod tugmani bosish bilan tugaydi. Smartup’dagi faol variantning DOM belgisini jonli sozlamani almashtirmasdan tasdiqlash ochiq. [UI Kit](https://uikit.greenwhite.uz/button-group) · [Base](../utils/base_pages/angular_base_page.py#L1056) · [Smartup dossier](../skills/smartup-guide/references/forms/company.md#company-viewda-security-sozlamalar-har-doim) |
| 11 · `click()` | UI Kit’da tugma guruhidagi «Day», Smartup «Акции»da «Создать» bosildi. Ikkinchi holatda «Акция (создание)» ochildi. | Tugma ko‘rinishi va bosilishi base’da kutiladi. Keyingi forma tayyorligini chaqiruvchi `expect_page()` bilan tekshiradi. |
| 12 · `tab()` | Smartup «Физическое лицо (просмотр) → Детали»da metod muvaffaqiyatli qaytdi. UI Kit Tab Bar’dagi «Profile» bosilgach tanlangan tugmada `bg-brand-50` va `text-brand-700` bor edi. Helper kutgan `border-b-brand-600` yo‘qligidan assertion yiqildi. | Faol tabni faqat bitta bezak klassiga bog‘lash barcha variantni qamramaydi. Barqaror semantik belgi ikkala ko‘rinishda aniqlanishi kerak. [UI Kit](https://uikit.greenwhite.uz/tab-bar) · [Base](../utils/base_pages/angular_base_page.py#L262) |
| 13 · `action()` | Smartup jismoniy shaxslar ro‘yxatida tanlangan qator uchun «Просмотр» bosilib, ko‘rish formasi ochildi. UI Kit Dropdown Button’da trigger menyusi «Edit», «Duplicate», «Archive» bandlarini chiqardi. | Bevosita tugma va menyu tuzilishi tekshirildi. Smartup’da dropdown ichidagi biznes amalini bajarish ochiq. [UI Kit](https://uikit.greenwhite.uz/dropdown-button) |
| 14 · `page_link()` | «Акции» ro‘yxatidan «Конструктор отчетов по акциям» havolasi `/a2/anor/rep/mbi/mcg/action`ga o‘tdi. | Yagona ko‘rinadigan aniq nomli havola va loader kutiladi. Manzil va sarlavha ham kuzatildi. |
| 15 · `confirm_biruni()` | UI Kit Modal Confirm va Smartup’da mavjud ism qatori tanlanganda «Да / Нет» dialogi chiqdi. `button_name="Нет"` ikkala dialogni yopdi. | Base ko‘rinadigan dialog, tugma va yopilishni kutdi. Smartup’da ism bo‘yicha tahrirlashga o‘tish rad etildi. [UI Kit](https://uikit.greenwhite.uz/modal-confirm) |
| 16 · `close_biruni_alert()` | UI Kit HTTP xato misolida «USR-409» matni tekshirildi va «Закрыть» dialogni yopdi. Smartup’da faqat audit brauzerida `action_list:model` uchun HTTP 500 qaytarildi. «Ошибка / Не удалось загрузить» main ichida chiqdi, bitta alert va nol dialog kuzatildi. | Dialogni yopish shu yuzaga qo‘llanmaydi. Sahifani ochish tekshiruvida main ichidagi yuklanish xatosi ham aniqlanishini alohida tekshirish kerak. Smartup’dagi modal xatoni yopish ochiq. [UI Kit](https://uikit.greenwhite.uz/alert-dialog) |
| 17–18 · `grid()`, `grid_controller()` | «Акции»da «Нет результатов», qidirish, qidiruvni tozalash, reload va sozlama menyusi tekshirildi. «Физические лица» ochilganda dastlab qatorlar soni 0 edi. Keyin ikkita qator chiqdi va ulardan biri matni bilan tanlandi. UI Kit Data Table’da Local Filters, Custom Actions va boshqa rejimlar ko‘rindi. | Natijani tekshiradigan flow kerakli qator yoki aniq bo‘sh xabarni kutadi. `return_bool=True` faqat shu ondagi ko‘rinishni qaytaradi. Barcha satrlarni belgilash va filtrni qo‘llash bu auditda bajarilmadi. [UI Kit](https://uikit.greenwhite.uz/data-table) |
| 19 · `grid_setting()` | Smartup «Акции → Настройка таблицы»da dialog, faol ustunlar ro‘yxati, «Отменить» va «Сохранить» ko‘rindi. | Dialog ochilishi tekshirildi. Ustunni o‘zgartirib saqlash va yangilangan jadvalni tasdiqlash ochiq. |
| 20 · `grid_cell()` | «Физические лица» qatorida `.smt-data-cell` topilmadi, oltita `[data-smt-col-key]` katak topildi. Base birinchi matnli katakni mavjud muqobil locator bilan o‘qib, kutilgan qiymatga mosligini tasdiqladi. | Katak ko‘rinishi, joylashuvi va matn uchun mavjud kutish ishladi. Tahrirlanadigan katak bu kuzatuvga kirmadi. |
| 21–22 · `text()`, `form_view()` | «Акции» asosiy kontentidagi matn tasdiqlandi. «Физическое лицо (просмотр) → Имя» qiymati readonly maydondan o‘qilib, o‘sha qiymat `expect_value` bilan qayta tekshirildi. | Ko‘rish formasida label bilan bog‘langan maydon va `readonly` atributi kutiladi. |
| 23–24 · `expect_page()`, `open_route()` | «Акции» va «Заказы» ro‘yxatlari relative route orqali ochildi. URL va sarlavhalar tasdiqlandi. | Sarlavha ochilgach qatorlar alohida yuklanishi mumkin. Sahifa xatosi bo‘yicha ochiq masala 16-qatorga yozilgan. |
| 25–26 · `navigate_to()`, `navigate_to_form()` | Oddiy menyudan «Справочники → Акции» va ustun bilan «Справочники → Маркетинг → Акции» bir xil `action_list` manzilini ochdi. | Ustun berilganda aniq guruh va shu guruhdagi menuitem kutiladi. Qo‘shish ikonkasidan o‘tish ochiq. |
| 27 · `switch_filial()` | QA foydalanuvchisida ro‘yxatda bitta filial ko‘rindi. Nomi bilan qayta tanlash va trigger matnini tasdiqlash ishladi. | Boshqa filialga o‘tish va uning kontenti yangilanishi uchun ikkita filialga kirishi bor profil kerak. |
| 28 · `hide_ui()` | Role setup ishlatadigan yordamchi vidjet selektori Smartup brauzerida ikkita elementga mos tushdi, metod 2 qaytardi. | Bu bir martalik DOM amali. Keyin paydo bo‘ladigan elementlar uchun kutish yoki kuzatuvchi o‘rnatmaydi. [Chaqiruvchi](../tests/smoke/test_setup/test_08_role.py#L74) |
| 29 · `date()` | Base hisobida 28.02.2024 + 1 kun → 29.02.2024, 31.12.2025 + 1 kun → 01.01.2026 chiqdi. | Bu UI kutishiga bog‘liq bo‘lmagan hisob. Sana maydonining amaliy tekshiruvi 7-bosqichda. |

**Keyingi ish.** Avval 6-bosqichdagi ikkinchi tanlovni qayta ishlatiladigan base metodida barqarorlashtirish, keyin 5-bosqichdagi alohida qidirish va 12-bosqichdagi tabning faol holatini tekshirish. 30-bosqichdagi regression run alohida qoladi.

## Kod qayerda turadi?

- **Har bir Angular UI komponenti uchun bitta base funksiya** shu komponentning UI’da mavjud barcha foydalanuvchi amallarini qamrab oladi. Test va flowlar kerakli amalni `AutoBasePage` orqali shu metoddan chaqiradi. Har bir amalning tayyorlik belgisi va odatiy maksimal kutish vaqti komponent metodida boshqariladi.
- **Kutish helperlari** komponent metodining ichida ishlatilishi mumkin. Masalan, test klientni tanlash uchun `b_input()`ni chaqiradi. Metod qidiruv matnini kiritgach, aynan shu matnga mos variant ko‘rinib, tanlashga tayyor bo‘lishini kutadi va uni tanlaydi. Shu shartni tekshiradigan helper mavjud bo‘lsa, metod uni qayta ishlatadi. Bir nechta komponentga bir xil kutish kerak bo‘lsa, ular shu helperni baham ko‘rishi mumkin.
- Masalan, `b_input()` orqali ro‘yxatni ochish, qidirish, variant tanlash, tanlovni tozalash, joriy qiymatni o‘qish va tekshirish mumkin bo‘lishi kerak. Bular boshlang‘ich misollar. To‘liq ro‘yxat UI Kit va haqiqiy A2 formadan olinadi. Klient tanlash `b_input()`ga tegishli. Klient tanlab, mahsulot qo‘shib, buyurtmani saqlash ketma-ketligi takrorlansa, u yordamchi flow’ga tegishli.
- **Yordamchi flow** bir nechta test ishlatadigan bir xil qadamlar ketma-ketligini base funksiyalardan yig‘adi. Masalan, saqlangan buyurtmani topish va tahrirlashga ochish. Avval mavjud flow tekshiriladi. Takrorlanish tasdiqlansa, tegishli testlar bitta flow’ni chaqiradi.
- **Test** ssenariyga xos amal va kutilgan biznes natijasini ifodalaydi. Masalan, miqdorni 9 ga o‘zgartirib, jami 63 000 bo‘lishini tekshiradi. Bitta testni o‘tkazish uchun maxsus locator yoki vaqt qiymati qo‘shishdan iloji boricha qochamiz.
- **Mahalliy kutish** faqat shart aynan shu ssenariyga xos bo‘lib, uni base yoki mavjud flow orqali ishonchli ifodalashning amaliy yo‘li bo‘lmaganda qo‘llanadi. Bunda test kuzatiladigan natijani kutadi. Shu ehtiyoj boshqa testda ham uchrasa, umumlashtirish qayta ko‘rib chiqiladi.

## Order bo‘yicha tekshiruv tarixi

O0–O6 belgilari quyidagi Order yozuvlariga tegishli. O6 runi asosiy rejaning 30-bosqichiga kiritilgan.

| № | Holat | Ish | Bosqichni yopish mezoni |
|---|---|---|---|
| O0 | Bajarildi | #3689 logi va tracelarini ko‘rish, UI Kit’dagi input va skeletonni brauzerda tekshirish. | Boshlang‘ich dalillar quyida qayd etilgan. #3689 tuzatishlari uchun CI tasdig‘i hali kutilmoqda. |
| O1 | Bajarildi | A2 base funksiyalari va Angular Order ssenariylaridagi raqamli timeoutlar, majburiy pauzalar va takroriy UI qadamlarini topish. | Quyida kod joylari, iste’molchilar va har bir takror bo‘yicha qaror yozildi. |
| O2 | Bajarildi | A2 skeleton, komponent spinneri va ichki vidjetning band holatini haqiqiy Angular forma yoki trace bilan solishtirish. | Tez ochilish, loader kech paydo bo‘lishi, loader tugamay qolishi va bitta vidjet bandligi uchun keyingi amal qachon bajarilishi yozilgan. |
| O3 | Bajarildi | Umumiy kutishlarni A2 base funksiyalariga, takrorlangan UI qadamlarini tegishli flow’ga ko‘chirish. Dashboard va ombordagi 120 soniyalik kutishlarni birinchi bo‘lib baholash. | Umumiy UI timeoutlari base qatlamidan olinadi. Mahalliy istisno qolsa, sababi ro‘yxatda ko‘rsatilgan. Tez holat ortiqcha kutmaydi, timeout xabari esa qaysi holat kutilganini bildiradi. |
| O4 | Bajarildi | Sonli input. UI Kit va Smartup buyurtma formasida 10 → 9 tahririni solishtirish. Maydon qiymati, oraliq 0 so‘rovi, Tab’dan keyingi hisob va yakuniy summani kuzatish. | Kiritish usulini umumiy input() metodiga qo‘llashdan oldin yana bitta sonli maydonda mosligi tekshirilgan. Summaga oid biznes tekshiruvi testda qolgan. |
| O5 | Bajarildi | Serverdan qidiradigan select. UI Kit va A2 formada komponent amallarini ro‘yxatga olib, har birini mavjud `b_input()` imkoniyatiga solishtirish. Har bir amal uchun tayyorlik belgisi va yetishmayotgan imkoniyatni qayd etish. | Tasdiqlangan har bir amalni test aynan `b_input()` orqali bajara olishi tekshirilgan. Sekin qidiruv, kech kelgan eski javob, bo‘sh natija va yo‘qolmay qolgan spinner uchun kutiladigan holat ko‘rsatilgan. |
| O6 | Rejada — test runi boshlanmagan | O‘zgarishlarni statik tekshirish. Testlarni ishga tushirish so‘ralgach, ta’sirlangan ssenariylar va shu base funksiyalarini ishlatadigan boshqa formalarda tekshirish. | Run havolasi, natija va ochiq muammolar yozilgan. Sekin holat bilan birga odatiy tez holatda ortiqcha kutish paydo bo‘lmagani ham tekshirilgan. |

## Order O1 natijalari

A2 base metodlari, ular chaqiradigan umumiy helperlar va `tests/regression/test_orders` ichidagi 78 ta Python fayli statik tekshirildi. Order katalogida `wait_for_timeout()` chaqiruvi topilmadi. Pytest assertionlari, brauzer amallari va navigatsiya sukut bo‘yicha bir xil `UI_TIMEOUT_MS` (60 s) oladi. Bu maksimal vaqt, shart bajarilishi bilan kutish tugaydi. [Umumiy qiymat](../utils/base_pages/__init__.py#L3) · [Assertionlar](../tests/conftest.py#L91) · [Brauzer konteksti](../tests/shared/browser.py#L20)

### Kutishlar va mavjud helperlar

| Qayerda | Kod hozir nimani kutadi | Qaror |
|---|---|---|
| Sahifa va jadval. [A2 loader](../utils/base_pages/angular_base_page.py#L1420), [Order fixture](../tests/regression/test_orders/conftest.py#L26) | Loader darhol ko‘rinmasa, base uning paydo bo‘lishini 8 s gacha kuzatadi. Faqat `order_group` markerli testlarda fixture bu oynani 250 ms qiladi. Keyin ko‘rinadigan skeleton va `aria-busy=true` soni nolga tushishini kutadi. | `_wait_for_loader(root=...)` qayta ishlatiladi. [expect_page](../utils/base_pages/angular_base_page.py#L1480) butun sahifaga, [grid](../utils/base_pages/angular_base_page.py#L1557) jadvalga qaraydi. 2-bosqichda 250 ms dan kech chiqqan loader va band qo‘shni vidjetni tekshiramiz. 3-bosqichda kuzatish oynasini base ichidan boshqaramiz. |
| Sahifa xatosi. [expect_no_application_error](../utils/base_pages/page_errors.py#L11) | `expect_page()` xato chiqishini 4,8 s gacha kuzatadi, tekshiruvlar oralig‘i ko‘pi bilan 100 ms. Xato ko‘rinsa, matnini o‘qishga 2 s beriladi. A2 metodining izohida eski 2,4 s qolgan. | Mavjud helper xato diagnostikasi uchun saqlanadi. Tez ochilgan sahifa vaqtini o‘lchaganda loader oynasi va shu kuzatuvni alohida hisoblaymiz. |
| Klient, mahsulot qidiruvi. [b_input](../utils/base_pages/angular_base_page.py#L552), [multiselect](../utils/base_pages/angular_base_page.py#L1198), [Order mahsulot tanlovi](../tests/regression/test_orders/helpers/flows/order.py#L176) | Ikkala komponent server qidiruvida so‘rovni matn va maydon bo‘yicha `_lookup_query_finished` bilan moslaydi. Keyin `b_input()` o‘z spinneri va variantini, `multiselect()` o‘z menyusi, yuklanish matni va variantini tekshiradi. | Ochish yoki qidirish amalidan oldin so‘rovni tinglash ikkala metodda takrorlangan. 5-bosqichda shu qismni ichki helperga yig‘ish mumkin. Har bir komponent o‘z tayyorlik belgisini tekshiradi. [Moslik helperi](../utils/base_pages/angular_base_page.py#L32) |
| Miqdor va jami. [input](../utils/base_pages/angular_base_page.py#L366), [miqdor chegirmasi](../tests/regression/test_orders/business_cases/promotions/test_01_quantity_discount.py#L35) | `input()` maydon ko‘rinishini kutadi, yozadi, so‘ralsa Tab bosadi va kutilgan qiymatni kutadi. Yozilgan miqdor ko‘rinishi order summasi qayta hisoblanganini tasdiqlamaydi. | Maydon uchun mavjud `_control()` va `input(expect_value=...)` ishlatiladi. 4-bosqichda tahrirlashni tekshiramiz. Ssenariy kutilgan summani beradi, base shu qiymat maydonda paydo bo‘lishini kutadi. |
| Guruh sessiyasi. [Dashboard va filial](../tests/regression/test_orders/helpers/group_auth.py#L75), [Order fixture](../tests/regression/test_orders/conftest.py#L80) | Saqlangan sessiya bilan dashboard hujjatini ochish uchun 120 s, dashboard yoki login URL’iga o‘tish uchun 30 s, kerakli filial tugmasi ko‘rinishi uchun 30 s belgilangan. | Navigatsiya chegarasi va filial tugmasining UI kutishini base orqali boshqarish. Dashboardga kirish va sessiya tugab loginga qaytish yo‘llarini ajratish login flow’ida qoladi. |
| Ombor qoldig‘i. [read_stock](../tests/regression/test_orders/helpers/flows/stock.py#L43), [open_route](../utils/base_pages/angular_base_page.py#L328) | `read_stock()` aniq mahsulot ID va sarlavha bilan `open_route(..., timeout=120_000)` chaqiradi. Base ichida `main` DOM’ga qo‘shilishi uchun 20 s gacha beriladi. Qoldiqlar jadvalida lot qatorlari hamda bo‘sh natija alohida tekshiriladi. | Bitta joydagi navigatsiya chegarasini base’ga ko‘chirish rezerv, ikki ombor va qaytarish testlariga birga ta’sir qiladi. Jadval uchun `grid(root=...)` va `grid(state="empty")` mavjud. Bir omborda bir nechta lot bo‘lishi va qoldiq haqiqatan nol ekanini `read_stock()` tekshiradi. [Rezerv](../tests/regression/test_orders/business_cases/stock/test_cancel_reserve.py#L44) · [Ikki ombor](../tests/regression/test_orders/business_cases/stock/test_two_warehouses.py#L19) · [Qaytarish](../tests/regression/test_orders/business_cases/returns/test_promoted_return.py#L18) |
| API orqali sessiyani tiklash. [Sessiya so‘rovi](../tests/regression/test_orders/helpers/group_auth.py#L45), [login retry](../tests/regression/test_orders/helpers/auth_recovery.py#L92) | Sessiya HTTP so‘roviga 30 s berilgan. Order katalogidagi yagona `sleep()` API login HTTP 500 qaytargach, bir martalik qayta urinish oldidan 15 s kutadi. | Ikkalasi sessiya helperida qoladi. Ular uchun kutishni qisqartirish yoki uzaytirish UI komponentining sekin yuklanishini hal qilmaydi. |

### Takrorlangan Order qadamlari

Quyidagi havolalar 1-bosqichdagi, refaktordan oldingi kodni ko‘rsatadi.

| Takror va dalil | 3-bosqichdagi qaror |
|---|---|
| Yakunlash bosqichida aynan bitta ko‘rinadigan `ИТОГО` labelini kutish **9 joyda** yozilgan. [Qo‘lda chegirma — 6 joy](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_manual_discount.py#L131) · [Tayyor chegirma — 2 joy](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_preset_discount.py#L46) · [Aralash aksiya — 1 joy](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/promotions/test_mixed_promotions.py#L26) | Yakunlashga o‘tishni Order flow’ga yig‘ish. Flow `Далее`ni bosadi va yangi bosqichdagi `ИТОГО` maydoni tayyorligini base orqali kutadi. Bir xil label eski bosqichda ham uchrasa, yangi bosqich doirasi va yagona maydon shartini saqlash kerak. Har test o‘z chegirmasi va jamini tekshiradi. |
| Klientni tanlash → `Далее` → narx turi va ombor bo‘yicha mahsulot tanlash ketma-ketligi to‘lov va qaytarish testlarida bir xil. Miqdor chegirmasi ham shu qadamlarni ishlatadi. [To‘lov](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/payments/test_promoted_order_payment.py#L59) · [Qaytarish](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/returns/test_promoted_return.py#L139) · [Miqdor chegirmasi](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/promotions/test_01_quantity_discount.py#L31) | Umumiy o‘tishni Order flow’ga chiqarish. Unda `b_input()` va mavjud `select_order_product()` chaqiriladi. Miqdor, aksiya va pul tekshiruvlarini ssenariy beradi. |
| Tayyor chegirma testi boshqa test modulidan `_open_goods`, `_save_draft`, `_saved_amounts` va `_number`ni import qiladi. [Import](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_preset_discount.py#L9) · [Amaldagi helperlar](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/business_cases/discounts/test_manual_discount.py#L26) | Allaqachon umumiy ishlatilayotgan chegirma amallari va tekshiruvlarini Order helper moduliga ko‘chirish. Yaratish, mahsulotni tanlash, TTN bo‘yicha saqlash va tahrirga ochishda mavjud flow’lardan foydalanish. [Order flow’lari](https://github.com/turgunovjasur/Playwright/blob/d49971459df521149c8159d2cb98099bdc897da7/tests/regression/test_orders/helpers/flows/order.py#L20) |

**2-bosqichda birinchi tekshiruv** — Order’da `Далее` bosilgandan keyin eski bosqich qachon yopilishi, yangi `ИТОГО` maydoni qachon tayyor bo‘lishi va shu orada qaysi loader ko‘rinishini trace yoki haqiqiy formada solishtirish. Shu dalil flow uchun tayyorlik shartini belgilaydi. 1-bosqichdagi xulosalar kod tahliliga asoslangan.

## Order O2 — Order yakunlash bosqichi

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
2. Ssenariy kutilgan summani bilsa, uni parametr sifatida beradi. Flow mavjud `AutoBasePage.input(label="ИТОГО", expect_value=...)` orqali qiymat mos kelguncha kutadi. Sonning minglik bo‘shliqlarini base hisobga oladi. Kutilgan summa berilmasa, maydonning ko‘rinishi faqat bosqich ochilganini tasdiqlaydi. Summani tekshiradigan ssenariy o‘z qiymatini alohida beradi. [A2 input](../utils/base_pages/angular_base_page.py#L366)
3. Tez o‘tishda shart bajarilishi bilan davom etadi. Kechikkan renderda shu shart umumiy UI timeoutigacha qayta tekshiriladi. Butun sahifada spinner paydo bo‘lishi yoki yo‘qolishini majburiy kutish bu qadamga qo‘shilmaydi. Keyingi amal to‘lov turini tanlash bo‘lsa, uning tayyorligini `b_input()` o‘z dropdown’i ichida tekshiradi. [A2 select](../utils/base_pages/angular_base_page.py#L552)
4. Readonly qiymatni o‘qish ekran ustidagi to‘siqni aniqlamaydi. Order formasini ochishda butun oynani qoplaydigan loader uchun base kutishi ishlatiladi. Yakunlashda o‘ziga tegishli maydon va qiymat kutiladi. Keyingi interaktiv amal o‘sha elementni bosish mumkinligini ham tekshiradi.

**Qayta topish uchun.** Dastlabki ishchi nusxadagi `test-results/runs/20261115T005850Z-8e4a4f38/test_09_second_client_reuses_limit-dbe8a32c/attempt-01/trace.zip`, SHA-256 `34207fc8cabb5ea5db86927cd88a02eab4e017fefb3dfc0fd9ab567934e57740`. Yuqoridagi kadrlar arxivning `trace.trace` faylidan olindi. Arxiv mahalliy test artifactidir.

### 18-noyabr — forma ochilishi va yakunlashdagi farq

| Kuzatuv | Natija |
|---|---|
| **Order yaratish formasini ochish.** Brauzerda faqat `order+add:model` o‘qish so‘rovi yuborilishi vaqtincha ushlab turildi. | `app-global-page-loader` ichidagi `aria-busy="true"` element `main` tashqarisida edi. U 1280 × 720 oynani to‘liq qopladi va markazdagi bosishni oldi. 3 s kuzatuv oxirida ham klient maydoni tayyor emas edi. Eski page-scope kutishi bloklandi, odatiy main-scope kutishi esa loader ko‘rinib turganda qaytdi. |
| **Kech chiqish va band qolish.** Alohida kuzatuvda «Создать» amali kutish boshlanganidan 500 ms keyinga rejalashtirildi. Haqiqiy loader +1 174 ms da qayd etildi. | Tuzatilgan `wait_for_loader()`ning kuzatish oynasi uni ushladi. Model so‘rovi ushlab turilganda, odatiy va jadval doirasidagi ikkita qisqa diagnostik kutish ham 650 ms chegarasida bandlik xatosini berdi. So‘rov +2 486 ms da qo‘yib yuborildi, tashqi kutish +5 446 ms da tugadi. Loader yo‘qolgani va klient maydoni ochilgani tasdiqlandi. |
| **Mahsulotlardan yakunlashga o‘tish.** Mavjud Order trace’ida balans so‘rovi click boshidan +31 ms da boshlangan. Jonli formada `Далее` bosilganda shu balans so‘rovlarini brauzerda ushlab turdik. | Birinchi ushlangan so‘rovdan +415 ms da `ИТОГО = 63 000` edi. To‘lov maydoni ustida ekran to‘sig‘i kuzatilmadi. Playwright maydonni bosish mumkinligini balans so‘rovi hali kutilayotganda tasdiqladi. |

Bu kechikishlar QA brauzerida boshqarildi. Doimiy server nosozligi yuz bergani haqida dalil yo‘q. Markerli guruhdagi 250 ms loaderning boshlanishini kuzatish oynasidir. Undan keyin boshlanadigan ish uchun flow maqsadli maydon yoki qiymatni ham kutadi. Kutish vaqtlari base qatlamida saqlandi.

## Order O3 — joriy qilingan o‘zgarishlar

- **Trace qamrovi.** Asosiy ishchi nusxadagi `test-results/`, `output/`, `outputs/` hamda `local-ci-validation` worktree’dagi `test-results/` ZIP arxivlarida 53 ta noyob `.trace` oqimi ko‘rib chiqildi. Asosiy frame’ning A2 Order URL’i va `Далее` locatori birga qayd etilgan ikkita click bitta yozuvga tegishli. Ikkinchisi yuqorida tahlil qilingan yakunlash o‘tishi. Qidiruv boshqa selector orqali bosilgan yoki snapshoti yo‘q amallarni qamramaydi. Trace qidiruvidan keyingi boshqarilgan kuzatuv yuqorida berilgan.
- **Yakunlash.** `open_order_summary()` bir marta bosadi, Order formasidagi bitta ko‘rinadigan `ИТОГО` labelini kutadi va maydonni mavjud `base.input()` orqali tekshiradi. Kutilgan summa berilsa, shu qiymatni ham kutadi. Qo‘lda chegirma, tayyor chegirma va aralash aksiyadagi 9 ta mahalliy locator tekshiruvi shu flow bilan almashtirildi. Aralash aksiya turida summa to‘lov parametrlari kiritilgach tekshiriladigan ssenariyning ketma-ketligi saqlandi. [Order flow](../tests/regression/test_orders/helpers/flows/order.py#L166)
- **Loader oynasi.** Umumiy A2 oynasi (8 s) va markerli Order guruhi oynasi (250 ms) endi base qatlamida belgilangan. Fixture faqat Order guruhiga qaysi qiymat qo‘llanishini tanlaydi. Bu ko‘chirish loaderning paydo bo‘lish yoki tugash shartini o‘zgartirmaydi. [Vaqtlar](../utils/base_pages/__init__.py)
- **Loader tugashi.** Avval helper skeleton soni nolga tushishini, so‘ng ko‘rinadigan `aria-busy=true` elementlari yo‘qolishini kutardi. Ikkinchi kutishda skeleton qaytsa, birinchi shart qayta tekshirilmasdi. Endi bitta Playwright assertion shu doirada ikkala belgining umumiy soni bir paytda nolga tushishini kutadi. Sahifa va jadval chaqiruvlari o‘z doirasini saqlaydi. 8 s va 250 ms kuzatish oynalari o‘zgarishsiz. Bu kod tahlilida topilgan holat. #3689 da aynan shu ketma-ketlik yuz bergani tasdiqlanmagan. [A2 loader](../utils/base_pages/angular_base_page.py#L1420)
- **Navigatsiya.** Yangi kontekstdagi dashboard hujjatini va ID bo‘yicha ombor sahifasini ochish chegarasi base qatlamidagi `A2_DOCUMENT_TIMEOUT_MS` (120 s) orqali boshqariladi. Dashboard hujjati `domcontentloaded`gacha kutiladi, so‘ng dashboard yoki login URL’i va tegishli filial tekshiriladi. URL hamda filial kutishi umumiy UI chegarasini (60 s) oladi. Sessiya HTTP so‘rovining o‘z vaqti saqlandi. [Vaqtlar](../utils/base_pages/__init__.py) · [Dashboard](../tests/regression/test_orders/helpers/group_auth.py) · [Ombor](../tests/regression/test_orders/helpers/flows/stock.py)
- **Klient va mahsulot.** To‘lov, qaytarish, miqdor chegirmasi va ikki chegirma modulining tayyorlov qadami bir xil `select_client_product()` flow’idan foydalanadi. Flow klientni tanlaydi, mahsulot bosqichini kutadi va mavjud `select_order_product()`ga uzatadi. Kutilgan miqdor, narx va chegirmani ssenariy tekshiradi. [Order flow’lari](../tests/regression/test_orders/helpers/flows/order.py)
- **Chegirmalar.** Qo‘lda va tayyor chegirma testlari uchun umumiy mahsulot tayyorlash, summani o‘qish, qoralamani saqlash va saqlangan qiymatlarni tekshirish bitta modulga chiqarildi. [Umumiy helperlar](../tests/regression/test_orders/helpers/discounts.py)
- **Tekshiruv.** O‘zgargan Python fayllari sintaksisi, importlar, flow chaqiriladigan joylar va diff statik tekshirildi. Testlar va collection ishga tushirilmadi. Jonli tekshiruvdan keyin global loader uchun kuzatish va yakuniy tekshiruv qamrovi kengaytirildi. Asosiy va jadval kutishlari o‘z lokal belgilariga qo‘shimcha ravishda shell loaderini ham ko‘radi. Timeout xabarida sahifa loaderi yoki tegishli qism bandligi ko‘rsatiladi.

## Order O4 — sonli maydonni tahrirlash

**Order dalili.** #3689 hisobotidagi `test_08_quantity_threshold` ssenariysi mavjud buyurtmada miqdorni 10 dan 9 ga o‘zgartirgan. Vaqtlar `call@34236` (`fill("9")`) boshiga nisbatan berilgan. Tarmoq so‘rovi boshlangan vaqt va HTTP javob holati bir qatorda keltirilgan. [#3689 Allure hisoboti](https://qa-assistant.uz/playwright-reports/44229787309-1.html) · [Order ssenariysi](../tests/regression/test_orders/business_cases/promotions/test_mandatory_conditions.py#L150)

| Vaqt | Kuzatuv |
|---|---|
| −54 ms | Mahsulot qatorida `quantity` qiymati 10. Miqdor va quti miqdori (`quantity_box`) maydonlari `smt-input[smtbehavior="biruni-number"]` ichida joylashgan. |
| −27…−2 ms | `Backspace` bosilgan. −10 ms da `get_box_quant` so‘rovi `quant="0"` bilan boshlangan va HTTP 401 qaytargan. `after@call@34230` kadrida input bo‘sh. |
| 0…+57 ms | `fill("9")` bajarilgan. +21 ms da ayni endpointga `quant="9"` yuborilgan va HTTP 200 qaytgan. `Tab` +26 ms da bosilgan. +57 ms da maydon qiymati 9 ekani tasdiqlangan. |
| +90…+220 ms | `Далее` bosilgach, `before@call@34260` kadrida `ИТОГО` qiymati `63 000` bo‘lgan. Bu qayd etilgan qiymat. Hisobning aynan qachon tugagani va uni `Tab` hodisasi boshlagani trace’dan aniqlanmaydi. |

Test kartasida sessiyani tiklash vaqtida `get_box_quant` uchun 401 javobini qayta ishlash qo‘llanmagani qayd etilgan. Miqdorni almashtirishdagi ortiqcha so‘rovni bartaraf qilish sessiyani tiklash muammosini hal qilganini ushbu trace tasdiqlamaydi.

**UI Kit solishtiruvi.** Brauzerda ikki Biruni maydoni tekshirildi: `precision=14, scale=2, fillwithzero` va `precision=10, scale=2`. Ikkalasida 10 dan 9 ga o‘tishda `Backspace` va keyingi `fill` ikkita `input` hodisasini berdi (bo‘sh qiymat, so‘ng 9). Bevosita `fill("9")` faqat 9 hodisasini berdi. `Tab`dan keyin har ikkisining ko‘rsatilgan va model qiymati 9 bo‘ldi. Birinchi maydonga 1234.50 va ataylab 0 kiritish ham tekshirildi. Order’dagi ikkinchi maydonning DOM turi ko‘rildi, uning tahriri ushbu CI trace’da bajarilmagan. [UI Kit Input](https://uikit.greenwhite.uz/input)

**Joriy qilingan o‘zgarish.** A2 `input()` Biruni sonli maydonida qiymatni bitta `fill` bilan almashtiradi. So‘ralgan `Tab`, maydon qiymatini tekshirish va umumiy UI kutishi saqlanadi. Order summasi uchun biznes tekshiruvi ssenariyda turadi. Amaliy tasdiq mezoni — yangi Smartup trace’da 10 → 9 uchun faqat 9 so‘rovi ketishi va `ИТОГО` 63 000 ga teng bo‘lishi. [A2 input](../utils/base_pages/angular_base_page.py#L366)

**18-noyabr, jonli Order.** Saqlanmagan buyurtmaga narxi 7 000 bo‘lgan mahsulot qo‘shildi. A2 `input()` bilan 10, keyin 9 yozilib, har safar Tab bosildi. `get_box_quant` uchun ketma-ket `quant=10` va `quant=9` qayd etildi, ikkala javob HTTP 200. Orada nol so‘rovi kelmadi. Qator summasi 70 000 dan 63 000 ga o‘zgardi. Order flow’i `Далее`ni bosganda DOM kuzatuvchisi bosish vaqtida jami maydonini ko‘rmadi, birinchi kuzatuvda +58 ms, yakuniy kod bilan ikkinchi kuzatuvda +65 ms da unda 63 000 ni qayd etdi. Kuzatuvda sahifani bloklaydigan loader chiqmadi. `Кол-во кейсов` shu mahsulotda o‘chiq edi. Ikkinchi tahrirlanadigan sonli maydon bo‘yicha dalil yuqoridagi UI Kit kuzatuvidir.

## Order O5 — serverdan qidiradigan select

**Qamrov.** UI Kit’dagi Single Data Select va 15-noyabrdagi Order `test_09_second_client_reuses_limit` trace’i solishtirildi. Trace faylining yo‘li va SHA-256 qiymati 2-bosqichda berilgan. UI Kit’da Role List so‘roviga 401 qaytganda ham “Ничего не найдено” chiqdi. Bu demo orqali haqiqiy bo‘sh 200 javobini tasdiqlab bo‘lmaydi. [UI Kit Data Select](https://uikit.greenwhite.uz/data-select) · [A2 b_input](../utils/base_pages/angular_base_page.py#L552)

| UI amali | Mavjud imkoniyat va tayyorlik belgisi |
|---|---|
| Klient yoki mahsulotni qidirib tanlash | `value` yoki `search_text` tanlashgacha olib boradi. Server selectida so‘rov maydon kaliti va matniga mos kelishi, spinner yashirinishi va kerakli variant ko‘rinishi kutiladi. Odatiy tanlashdan so‘ng menyu yopiladi. `expect_value` yakuniy qiymatni ham tasdiqlaydi. `stop_after_select` esa ataylab bosishdan keyin qaytadi. |
| Birinchi variant yoki aniq ombor/narx variantini tanlash | `select_first` ko‘rinadigan birinchi variantni oladi. `option_contains` tanlangan matn va qo‘shimcha belgilar mos keladigan bitta variantni kutadi. Sekin renderda endi avval birinchi qator ko‘rinadi, keyin zarur bo‘lsa scroll bilan navbatdagi sahifa kutiladi. |
| Tanlovni tozalash, qiymatni o‘qish va tekshirish | `clear=True` yolg‘iz chaqirilganda Escape’dan so‘ng menyu yopilgani va qiymat bo‘shligi tekshiriladi. `return_value` o‘qiydi, `expect_value` esa kutilgan qiymatni kutadi. UI Kit rol maydonida tozalash va Escape brauzerda tekshirildi. |
| Faqat ochish, qidirish, yopish | `action="open"` kerakli maydonga fokus beradi va menyu ko‘rinishini kutadi. `action="search"` matn bo‘yicha javob va ro‘yxat renderini kutadi, variant tanlamaydi. `action="close"` faol maydon menyusini Escape bilan yopadi. |
| Bo‘sh natijani tekshirish | `action="expect_empty"` shu amal davomida boshlangan, maydon kaliti va matni mos birinchi sahifa so‘rovini kutadi. Muvaffaqiyatli HTTP javobi, `count=0`, `data=[]`, spinner yo‘qligi, bo‘sh holat matni va ko‘rinadigan variantlar soni nol bo‘lishi kerak. |
| UI Kit’dagi qo‘shimcha rejimlar | Demo’da bir natijani avtomatik tanlash, All belgisi, pin, smart search tugmasi, qo‘shimcha tugmalar va disabled/required holatlari bor. Joriy metod tanlangan qiymatni tekshira oladi. Bu maxsus amallar uchun alohida parametr yo‘q. Ularning qaysi biri kerakligini Smartup formasida shu rejim uchraganda tasdiqlaymiz. |

**Order dalili.** Quyidagi vaqtlar tegishli `fill` boshidan olingan. Mos so‘rov muvaffaqiyatli tugagach, kerakli variant bosilgan. Trace’dan olingan uchta haqiqiy payload mavjud `_lookup_query_finished` bilan ham solishtirildi: mos matn va kalit qabul qilindi, boshqa matn yoki kalit rad etildi.

| Maydon | So‘rov boshlanishi va davomiyligi | Variantni bosish |
|---|---|---|
| Klient, `call@41331` | `persons`, +311 ms, 162 ms, HTTP 200 | +504 ms |
| Mahsulot, `call@41467` | `inventory_products`, +318 ms, 216 ms, HTTP 200 | +585 ms |
| To‘lov turi, `call@41729` | `payment_type`, +320 ms, 152 ms, HTTP 200 | +515 ms |

**Locator tuzatishi.** Order kadrida `Выберите...` faqat ichki inputda edi. UI Kit’dagi `Search roles...` bitta komponentda ikki marta topildi. Eski locator `index=0` uchun hostning ajdodlaridan select qidirib, hech narsa topmadi. Endi avval har bir mos element eng yaqin selectga bog‘lanadi, keyin komponentlar orasidan indeks tanlanadi. Demo’da `Search roles...` uchun bitta, `Search users...` uchun 15 ta DOM mosligidan 8 ta alohida komponent chiqdi. Order’dagi ikkinchi mahsulot qatorini tanlash ham shu yo‘ldan foydalanadi. [Locator](../utils/base_pages/angular_base_page.py#L622) · [Mahsulot tanlovi](../tests/regression/test_orders/helpers/flows/order.py#L202)

**Kutish qarori.** Sekin qidiruvda umumiy timeout ichida aynan so‘ralgan matnning javobi, keyin komponent holati kutiladi. Eski matn javobi yangi qidiruvni tugatmaydi. Bir xil kalit va aynan bir xil matn bilan takror so‘rovlarni hozirgi predicate ajratmaydi. Spinner yo‘qolmay qolsa tanlash kutishda to‘xtashi kerak. Bu nosozlik va teskari tartibda keladigan javoblar uchun real Order yozuvi hali yo‘q. Single va multi select so‘rovni tinglash qismini birga ishlatadi; har biri o‘z menyusi va variantini tekshiradi. [Ichki helper](../utils/base_pages/angular_base_page.py#L63)

**Order’da chaqirish.** Quyidagi misollarda `base` — `AutoBasePage(page)`. Har biri mustaqil chaqiriladi va maydonning input locatorini qaytaradi. Mavjud tanlash chaqiruvlari avvalgi tartibda ishlaydi.

```python
base.b_input(label="Клиент", action="open")
base.b_input(label="Клиент", action="search", search_text=client_name)
base.b_input(label="Клиент", action="expect_empty", search_text=missing_client_name)
base.b_input(label="Клиент", action="close")
```

UI Kit rol maydonida Escape’dan keyin qidiruv matni saqlandi. ArrowDown shu matn uchun yana bir POST yubordi. Oldindan to‘ldirilgan Smartup klient maydonida ArrowDown menyuni ochmadi. Bunday qiymatni qayta qidirishda helper matnni vaqtincha tahrirlab, mos so‘rov bajarilgach asl matnni tiklaydi va yangi javobni kutadi. HTTP 401 yoki javob formati buzilsa, bo‘sh holat muvaffaqiyatli hisoblanmaydi. Order trace’ida klient, mahsulot va to‘lov turi uchun birinchi sahifa so‘rovlarida `offset=0`, muvaffaqiyatli javoblarda `count` va `data` qayd etildi.

**Amaliy qabul mezoni.** Order’da mavjud klientni tanlamasdan qidirish, so‘ng mavjud bo‘lmagan klient uchun bo‘sh 200 javobini tekshirish va menyuni yopish. Ketma-ket ikki maydon bilan ishlaganda amal kerakli maydonga tegishi, qidiruv tanlovni tasdiqlamasligi va sessiya xatosi bo‘sh javob sifatida o‘tmasligi tekshiriladi. UI Kit’dagi qo‘shimcha rejimlarning Smartup’da ishlatilishi alohida kuzatiladi.

### 18-noyabr — Smartup’da amaliy tekshiruv

- **Order muhiti.** `validate_api_baseline()` mahalliy API setup natijasi, server va kompaniya mosligini tasdiqladi. Shu baseline’dagi QA foydalanuvchisi uchun login HTTP 200 qaytardi. Keyingi `m:session` so‘rovi HTTP 401 qaytardi va brauzerda “Нет лицензии для входа в систему!” ko‘rindi. `verify_license()` aynan shu baseline’dagi `ERP users` litsenziyasi faolligini va foydalanuvchi unga biriktirilmaganini ko‘rsatdi. [Baseline tekshiruvi](../scripts/api_setup_bridge.py#L106) · [Litsenziya tekshiruvi](../tests/regression/test_orders/helpers/auth_recovery.py#L37)
- **UI Kit dalili.** Branchdagi `b_input(action="open")` rol maydonida bitta ko‘rinadigan menyu ochdi. `close`dan keyin ko‘rinadigan menyular soni nol bo‘ldi. Alohida qidiruvda kutilgan `requestfinished` 10 s ichida kelmadi va `expect_empty` timeout bilan tugadi. UI Kit’da spinner hamda “Ищем результаты” holati kuzatildi. Muvaffaqiyatli bo‘sh 200 javobi bu safar qayd etilmadi.
- **Davom etish sharti.** Tasdiqlangan test foydalanuvchisiga faol `ERP users` litsenziyasi biriktirilgach, Order’da mavjud klientni tanlamasdan qidirish, boshqa maydon bilan ishlash, keyin noyob matn uchun bo‘sh 200 javobini tekshirish mumkin. Shu safar Order formasi ochilmadi. Litsenziya biriktirish va buyurtma saqlash bajarilmadi.

Litsenziya qayta tekshirilganda ham faol, foydalanuvchi esa biriktirilmagan edi. 2-bosqichdagi bonus Order trace’ida klient, mahsulot va to‘lov turiga tegishli 8 ta HTTP 200 javobi topildi (mos ravishda 4, 2 va 2 ta). Sakkiztasida ham `data` ichida qator bor. Bo‘sh natija uchun amaliy qabul mezoni ochiq.

### Litsenziya biriktirilgandan keyingi Order tekshiruvi

- Yangi QA sessiyasida Order formasining oldindan tanlangan klienti bilan `open`, `close`, `search` va `expect_empty` tekshirildi. Oddiy bosish menyuni ochmagan holatda ham `open`dan keyin klient matni saqlandi. Xuddi shu klientni qidirish uning qatorini ko‘rsatdi, tanlashga xos kontrakt va balans so‘rovlari qaytadan ketmadi.
- `Проект` menyusi ochiq turganda klientga berilgan `close` loyiha menyusini ochiq qoldirdi. `Проект`ga berilgan `close` uni yopdi. Noyob klient matni uchun `persons` javobi HTTP 200, `count=0`, `data=[]` bo‘ldi. «Ничего не найдено» ko‘rindi va ko‘rinadigan variantlar soni nol bo‘ldi.
- **Qidiruv cho‘zilganda.** Izolyatsiyalangan brauzerda haqiqiy klient so‘rovi kamida 1,2 s ushlab turildi. Maydonda `smt-icon[key="loader"]` ko‘rinmadi. Ochiq menyuda «Загрузка...» va «Ищем результаты» ko‘rindi. `b_input()` endi bandlik tugashini tekshirayotganda maydon ikonkasini ham, menyuning variant qatorlaridan tashqaridagi yuklanish matnini ham hisobga oladi. So‘rov 1,53 s ushlangan yakuniy tekshiruvda bandlik matni ko‘rinib turgan paytda base kutishi tugamadi. So‘rov qo‘yib yuborilgach, klient qatori ko‘rindi. [A2 select kutishi](../utils/base_pages/angular_base_page.py#L71)
- **Kechikish va xato javobi.** Bir so‘rov javobsiz ushlab turilganda `expect_empty` timeout bilan tugadi. Oldingi qidiruv so‘rovi ushlab turilgan paytda yangi matnning bo‘sh javobi o‘z so‘rovi bilan tasdiqlandi. Brauzerda faqat shu lookup uchun hosil qilingan HTTP 401 ni helper xato sifatida qaytardi. Bu holatlar boshqarilgan brauzer kuzatuvlari. Tabiiy sessiya uzilishi yoki Order sahifasini bloklaydigan loader haqida ulardan xulosa chiqarilmaydi.

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
| 2026-11-18 | 5-bosqichdagi open, search, expect_empty va close amallari A2 base metodiga qo‘shildi. Mavjud Order trace’i va UI Kit’dagi qayta qidirish harakati solishtirildi. | Yangi amallarni Smartup’da tekshirish uchun run ruxsati kutilmoqda. |
| 2026-11-18 | 5-bosqichda Order’ga kirish tekshirildi. Login muvaffaqiyatli, sessiya uchun litsenziya biriktirilmagan. UI Kit’da ochish, yopish va javobni kutish kuzatildi. | Faol litsenziyali Order QA foydalanuvchisi bilan amaliy tekshiruvni davom ettirish. |
| 2026-11-18 | 3-bosqichda A2 loaderining ikki belgisi bitta kutishga birlashtirildi. | Order’da kechikkan loader uchun trace va 5-bosqich uchun litsenziyali sessiya kutilmoqda. |
| 2026-11-18 | Avvalgi test akkauntidan bo‘shatilgan ERP users litsenziyasi Order QA akkauntiga o‘tkazildi. Yangi biriktirish Smartup’dagi «Прикрепленные» ro‘yxatida tasdiqlandi. | Order formasida klient qidiruvi va bo‘sh natijani tekshirish. |
| 2026-11-18 | Litsenziyali Order’da select amallari va miqdor tahriri jonli tekshirildi, oldindan to‘ldirilgan selectni qayta ochish A2 base’da tuzatildi. | Sahifani bloklaydigan kech loader uchun real dalil hamda ruxsat berilganda test runi. |
| 2026-11-18 | 2–3-bosqichlar yakunlandi. Order sahifa loaderining DOM doirasi, kech chiqishi va uzoq bandligi jonli tekshirildi. | 6-bosqich — ruxsat berilganda ta’sirlangan Order ssenariylari va umumiy base ishlatadigan boshqa A2 formalarida test runi. |
