# Smartup API va Order regressiyasini tezlashtirish rejasi

## Ishlar holati · 25-noyabr 2026

- [x] **DONE · 1.** 25-noyabrdagi API va Order regressiyasi vaqtlari qayd etildi.
- [x] **DONE · 2.** Ikki ish tanlandi: saqlangan sessiya bilan buyurtmaga bevosita kirish va Order tayyorlovida ombor qoldig‘ini API orqali tekshirish.
- [ ] **PROGRESS · 3.** SCN-028 pilotida ombor va sessiya o‘zgarishlarini baholash.
  - [x] **DONE** — ikkala o‘zgarish birga tekshirildi. 13/13 qadam o‘tdi, guruh oldingi rundan 29 soniya ko‘proq vaqt oldi.
  - [ ] **TODO** — ombor va sessiya o‘zgarishlarining ta’sirini alohida o‘lchash.
- [ ] **PROGRESS · 4.** Saqlangan sessiya bilan bevosita kirish barcha Order guruhlariga qo‘llandi. To‘liq run va ombor optimallashtirishini baholash qolgan.
- [ ] **TODO · 5.** To‘liq regressiyani takrorlab, tejalgan vaqt va qayta urinishlar sonini boshlang‘ich o‘lchov bilan solishtirish.

**Maqsad** — to‘liq `API + Order regression` boshlanishidan yakunigacha ketadigan vaqtni qisqartirish. Natijani bir xil biznes tekshiruvlari bajarilgan runlarda solishtiramiz. Guruhlar mustaqil ishlashi va xatolarni aniqlashi kerak.

**Navbatdagi ish** — to‘liq regressiyada qaysi qadam bevosita kirganini va sessiyaga qancha vaqt ketganini o‘lchash. SCN-028 ombor o‘zgarishining ta’siri alohida baholanadi.

## 25-noyabrdagi o‘lchovlar

| O‘lchov | Natija | Nimani bilamiz |
|---|---|---|
| Oxirgi to‘liq run | API tayyorlovi 1 daq 25 s, Order regressiyasi 1 soat 26 daq 29 s | Bu tarixiy o‘lchovda xatolar sabab ayrim qadamlar bajarilmay qolgan. |
| Beshta guruh tuzatilgandan keyin | Guruhlarning oxirgi natijalari bo‘yicha 46/46 qadam o‘tdi | Bu natija tuzatilgan besh guruhning qamrovini tasdiqlaydi. |
| SCN-028 piloti | 13/13 o‘tdi. Guruh vaqti 4 daq 36 s dan 5 daq 5 s ga chiqdi | Ombor qadami 25,2 s dan 9,0 s ga tushdi. Ikki qoralamani yaratish va narx turini almashtirish jami 41,6 s ko‘proq oldi. |

## Ish tartibi

### 1. Boshlang‘ich o‘lchovlarni qayd etish

- [x] API tayyorlovi va Order regressiyasining 25-noyabrdagi davomiyligi hamda natijalari quyidagi taqqoslash jadvaliga kiritildi.
- [x] SCN-028 uchun optimallashtirishdan oldingi muvaffaqiyatli vaqt qayd etildi — 13/13 qadam, 4 daq 36 s.

### 2. Tanlangan ikki optimallashtirish

- [x] **Sessiya.** Guruhda bir marta login qilish. Keyingi qadamda saqlangan sessiya bilan kerakli buyurtma sahifasini bevosita ochib, foydalanuvchi va filialni tekshirish. Oldingi to‘liq runda sessiyani qayta ochish 99 marta takrorlangan va 10 daqiqa 56 soniya olgan.
- [x] **Ombor.** Order uchun tayyorgarlikda kirim allaqachon API orqali yaratiladi. Fizik, band va erkin qoldiqni ham har bir guruhning o‘z mahsuloti va ombori bo‘yicha API orqali tekshirish. Ombor harakatini tekshiradigan biznes ssenariylari UI orqali bajariladi.

### 3. SCN-028 pilotidagi ikki o‘zgarishni alohida baholash

- [ ] Eski usulni faqat ombor qoldig‘i API orqali tekshiriladigan variant bilan solishtirish. Har ikkalasida sessiya dashboard orqali ochiladi.
- [ ] Ombor usulini bir xil qoldirib, dashboard orqali kirish va bevosita buyurtma sahifasiga kirish vaqtlarini solishtirish.
- [ ] Har variantda 13 qadamni bir xil sharoitda tekshirish. Profil, filial, ombordagi qoldiq, «Подбор»dan chiqish va miqdorni o‘zgartirishdan keyingi bonus natijalarini tasdiqlash.

**Qaror** — 13/13 natija, guruhning umumiy vaqti va qayta urinishlar asosida har bir o‘zgarishni alohida baholash. Farq noaniq bo‘lsa, o‘lchovni takrorlash.

### 4. Foydasi tasdiqlangan usullarni mos guruhlarga qo‘llash

- [x] Saqlangan sessiyada har bir Order guruhining UI qadami o‘zi ishlatadigan birinchi sahifadan boshlanadi. Birinchi login va sessiyani tiklash amallari saqlanadi.
- [ ] Ombor qoldig‘i faqat tayyorgarlik uchun kerak bo‘lgan guruhlarga tasdiqlangan API usulini qo‘llash. Ombor harakatini tekshiradigan biznes ssenariylarida UI tekshiruvini saqlash.
- [ ] O‘lchovda vaqt olayotgan takroriy qidiruvlar, sahifa ochishlar va kutishlarni bittadan qisqartirish. Har o‘zgarishdan keyin ta’sirlangan guruhning natijasi va vaqtini yozish.

**Natija** — qaysi o‘zgarish qaysi guruhda qancha vaqt tejagani ko‘rinadi.

### 5. Yakuniy natijani to‘liq regressiyada tekshirish

- [ ] 1-bosqichdagi muhit, testlar to‘plami, `HEADLESS=1` va qayta urinish sozlamalari bilan to‘liq run bajarish.
- [ ] Boshlang‘ich va yakuniy natijalarni yonma-yon yozish. To‘liq run vaqtini va amalda bajarilgan qadamlar sonini yonma-yon ko‘rsatish. Tarixiy runda 10 qadam bajarilmay qolganligi sababli tezlashish foizini ikkala runda ham to‘liq bajarilgan bir xil qadamlar uchun hisoblash.

| Ko‘rsatkich | Boshlang‘ich run | Yakuniy run |
|---|---|---|
| Order run ID | `20261125T032943Z-ff36d4c6` | — |
| API tayyorlovi | 1 daq 25 s | — |
| Order regressiyasi | 1 soat 26 daq 29 s | — |
| Order qadamlari (o‘tdi / xato / bajarilmadi) | 215 / 5 / 10 | — |
| Order qayta urinishlari | 5 | — |

**Yakuniy mezon** — to‘liq biznes qamrovi saqlangan holda butun run tezlashganini va qayta urinishlar soni oshmaganini ko‘rsatish.
