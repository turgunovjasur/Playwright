# Smartup regressiyasida brauzer tablaridan foydalanish rejasi

## Bajarish tartibi

| № | Holat | Ish | Qachon bajarilgan hisoblanadi |
|---:|---|---|---|
| 1 | [x] DONE | Pilot va boshlang‘ich o‘lchovni belgilash | SCN-001-T05 tanlandi. Bitta tabdagi vaqt va balans o‘qishlar soni quyida qayd etildi. |
| 2 | [ ] TODO | Test uchun umumiy tab boshqaruvini yaratish | Bir brauzer oynasida nom bilan tab olish, qayta ishlatish, kerakli tabni yangilash va test oxirida yopish ishlaydi. |
| 3 | [ ] TODO | SCN-001-T05 pilotini ikki tabga o‘tkazish | Buyurtma 1-tabda davom etadi. Balans va «Детали» 2-tabda tekshiriladi. |
| 4 | [ ] TODO | Pilotni avvalgi usul bilan solishtirish | Bir xil biznes tekshiruvlari uchun natija, vaqt, qayta urinishlar va tablar holati qayd etiladi. |
| 5 | [ ] TODO | Pilot foyda bersa, qolgan testlarni tahlil qilish | Har bir nomzod uchun bitta test ichidagi qaytishlar soni, sarflangan vaqt va ochiq saqlanishi kerak bo‘lgan forma ko‘rsatiladi. |
| 6 | [ ] TODO | Tanlangan ssenariylarni guruhma-guruh o‘tkazish | Har bir guruhda natija va vaqt solishtiriladi. Yakunda to‘liq regressiya boshlang‘ich run bilan taqqoslanadi. |

**TODO** — navbatda, **PROGRESS** — ish boshlandi, **DONE** — natija tekshirildi. Ish boshlanganda shu qatorni PROGRESS ga o‘tkazamiz. Yakunida dalil yoki run havolasini qo‘shib, DONE deb belgilaymiz.

## Pilot qanday ishlaydi?

1. **1-tab — asosiy ish.** SCN-001-T05 buyurtma bilan shu tabda ishlaydi. Balansni tekshirayotganda uning ochiq sahifasi, tanlangan buyurtmasi va kiritilgan qiymatlari saqlanadi.
2. **2-tab — mijoz hisob-kitoblari.** Birinchi `read_settlement()` chaqiruvida test o‘z brauzer sessiyasida «Взаиморасчеты с клиентами» tabini ochadi. Foydalanuvchi va filialni tasdiqlaydi, kerakli ustunlar va «Клиент» qidiruvini tayyorlaydi. Keyingi chaqiruv aynan shu tabni oladi.
3. **Yangi balans.** Avval Smartup asosiy tabdagi amalni saqlaganini tasdiqlaydi. So‘ng 2-tabda kerakli sahifa va mijoz tekshiriladi. Bir xil mijoz uchun jadvalning «Yangilash» tugmasi bosiladi. Mijoz o‘zgargan bo‘lsa, yangi nom bilan qidiriladi. Sozlamalar yo‘qolgan bo‘lsa, keraklisi tiklanadi. Natija shu mijozga tegishli yangi so‘rov tugagach, so‘mdagi qatordan o‘qiladi.
4. **«Детали» ham 2-tabda.** Test umumiy qarzdan aniq buyurtmaning qarziga o‘tganda mijoz qatorini shu tabda tanlaydi. Navbatdagi balans tekshiruvi «Детали»dan boshlansa, avval ro‘yxatga qaytadi, keyin ma’lumotni yangilaydi. Pilot ikki tab bilan bajariladi. Uchinchi tab faqat ro‘yxatga qaytish xarajati o‘lchovda sezilarli chiqsa ko‘rib chiqiladi.

## Umumiy mexanizmning vazifasi

| Qatlam | Vazifasi |
|---|---|
| **Brauzer tablari** | Joriy test va urinish doirasida tablarni nom bilan boshqaradi. Tab birinchi murojaatda ochiladi. Playwright amalni kerakli tabga yuboradi, foydalanuvchining fokusini majburan o‘zgartirmaydi. Har bir murojaatda yangi brauzer oynasi ochishga ehtiyoj qolmaydi. |
| **Smartup sahifasi** | Qaysi sahifa ochiqligini, faol filialni, mijozni va jadval javobini tekshiradi. Sahifa ichidagi navigatsiya va jadvalni yangilash shu qatlamda qoladi. Tab boshqaruvchisi boshqa sahifalarda ham aynan shu usulda ishlatiladi. |
| **Biznes testi** | Amalni bajaradi va kutilgan natijani belgilaydi. Masalan, 14 000 so‘mlik buyurtmaga 6 000 so‘m to‘lov ajratilgach, mijoz balansi va aynan shu buyurtmaning 8 000 so‘m qolgan qarzini tekshiradi. |

**Tabni tanlash va ma’lumotni yangilash alohida amallar.** Oddiy tab almashganda sahifa ochiq holicha qoladi. Yangilash kerak bo‘lsa, birinchi tanlov — jadvalning o‘zini yangilash. Bu imkoniyat bo‘lmasa, faqat ishlatilayotgan tab sahifasi qayta yuklanadi. Shu tabda saqlanmagan qiymat bo‘lsa, avval amal yakunlanadi. Butun brauzerni qayta yuklash rejaning bir qismi emas.

**Sessiya va xato dalillari.** Ikkinchi tab amaldagi test foydalanuvchisi va filialida ishlashi kerak. Unda 401 chiqsa, mavjud sessiyani tiklash mexanizmi shu tabda ham ishlashi, uzilgan o‘qish davom etishi va saqlash yoki to‘lov amali takrorlanmasligi tekshiriladi. Xato rasmi xato chiqqan tabdan olinadi, trace orqali o‘sha qadam topiladi. Test muvaffaqiyatli yoki xato bilan tugaganda yordamchi tab yopiladi. Qayta urinish o‘z tablari bilan boshlanadi.

## Pilotni qanday baholaymiz?

Boshlang‘ich run — `20261126T053918Z-de0c7832`, HEADLESS=1, 230/230 birinchi urinishda o‘tgan. Hisob-kitoblar 22 ta test ichida 62 marta o‘qilgan. Shu testlar bo‘yicha 40 ta takroriy murojaatda tayyor tabdan foydalanish imkoniyati bor. [Boshlang‘ich run](../test-results/runs/20261126T053918Z-de0c7832/run.json)

| SCN-001-T05 ko‘rsatkichi | Bitta tab | Ikki tabli pilot |
|---|---:|---|
| Testning bajarilish vaqti (Allure, setup va teardown alohida) | 155,6 s | O‘lchanadi |
| Balansni o‘qish | 8 marta | 8 ta natija tekshiriladi |
| Hisob-kitoblar sahifasiga kirish + qidirish va balansni o‘qish | 18,1 s + 25,8 s = 43,9 s | Birinchi ochilish va keyingi 7 murojaat alohida qayd etiladi |
| Biznes natijasi va qayta urinishlar | 6 ta status o‘tishi tekshirildi, 0 qayta urinish | Solishtiriladi |

Vaqtlarni bir xil test, HEADLESS=1 va bir xil qayta urinish sozlamasida solishtiramiz. 43,9 soniya ichiga yangi balansni serverdan olish ham kiradi. Pilot jadvaliga balans tekshiruvlarining jami vaqtini va butun test vaqtini yozamiz. Natija noaniq bo‘lsa, bir xil sharoitda takroriy o‘lchov qilamiz.

**Kengaytirish qarori.** Pilotda 1-tabdagi ish joyi saqlansa, sakkiz tekshiruvda ham yangi balans o‘qilsa, «Детали» qadamida aynan kerakli buyurtmaning qarzi tasdiqlansa, vaqt tejalishi ko‘rinsa va qayta urinishlar oshmasa, keyingi guruhga o‘tamiz. Hisob-kitoblar sahifasi ochiq turishini kutadigan chaqiruvchilarni birga ko‘chiramiz. Bunga `read_settlement()`, `open_debt_details()`, `read_debts()` va to‘lovni qarzga ajratadigan qadamlar kiradi. Keyingi nomzodlar — SCN-003-T08 va T09, har birida balans 8 marta o‘qilgan. Boshqa sahifalar uchun ham mezon — **bitta test ichida** qayta murojaat qilish yoki tugallanmagan asosiy formani ochiq saqlash zarurati. [Hisob-kitoblar kodi](../tests/regression/test_orders/helpers/flows/settlement.py) · [Umumiy optimizatsiya rejasi](regressiyani-tezlashtirish-rejasi.md)
