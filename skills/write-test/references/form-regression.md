# Forma regressiyasi uchun Playwright ssenariylari

Status: user-reported
Verified: 2026-11-16
Source: user

Funksional ssenariyni tanlaganda uch narsani belgilang. Test qaysi boshlang‘ich
holatni yaratadi? Qaysi foydalanuvchi amali uni o‘zgartiradi? O‘zgarish saqlanganini
qaysi ID va qiymat orqali qayta o‘qish mumkin? Quyidagi usullardan formadagi
boshqaruvlar va so‘ralgan qamrovga mosini tanlang.

## Yozuvni yaratish va tahrirlash

1. Test o‘z yozuviga qidiriladigan noyob kalit beradi. Minimal yaratishda faqat
   majburiy maydonlarni to‘ldiring. To‘liq yaratishda ixtiyoriy maydon va bog‘liq
   tanlovlarga ham bir-biridan ajratib bo‘ladigan qiymatlar bering.
2. Saqlangan IDni oling. Ro‘yxatda shu yozuvni toping, View va yangidan ochilgan
   Edit’da maydonlarni kiritilgan qiymatlarga solishtiring. Bog‘langan yozuv uchun
   UI ko‘rsatadigan ID yoki noyob koddan foydalaning.
3. Edit’da bitta qiymatni almashtirib, Cancel’dan keyin avvalgi qiymatni qayta o‘qing.
   Keyin o‘zgarishni saqlang. Xuddi shu IDda yangi qiymatni va yonidagi o‘zgarmas
   maydonni tekshiring. Save javobi kechiksa, takroriy Save’dan oldin test kaliti
   bilan nechta yozuv yaratilganini aniqlang.

## Maydon va amallarga mos tekshiruvlar

| Qamrov | Avtotestdagi amal va kutilgan natija |
|---|---|
| Majburiy maydon | Boshqa majburiy maydonlarni to‘g‘ri to‘ldirib, tekshirilayotgan bittasini bo‘sh qoldiring. Save’dan so‘ng aynan shu maydonning xabarini va yozuv yaratilmaganini tekshiring. Faqat shu qiymatni tuzatib, bitta yozuv saqlanganini tasdiqlang. |
| Chegara qiymatlari | Forma ko‘rsatgan matn limiti uchun limitdan bitta kam, limitga teng va bitta ortiq qiymatni sinang. Sana oralig‘i uchun bir xil kun va teskari tartibni, son uchun nol va kasrni tanlang. Qabul qilingan qiymatni qayta ochib o‘qing. Aniqlik va yaxlitlash kutilmasini forma qoidasidan oling. |
| Lookup va multi-select | Qidiruv tugagach kerakli variantni ID yoki kod bilan tanlang. Mos kelmaydigan so‘rovdan Escape bilan chiqqanda avvalgi tanlovni tekshiring. A va B tanlanganida A ni olib tashlang. Save va qayta ochishdan keyin tanlanganlar to‘plami aynan B bo‘lsin. |
| Ichki Add va Show all | Ichki Add orqali testga tegishli yozuv yarating. Ota forma qoralamasi saqlanib turganini, yangi yozuv tanlanganini va ota forma saqlangach shu ID bog‘langanini tekshiring. Show all oynasida aniq qatorni tanlab tasdiqlash va Cancel orqali qaytishni alohida sinang. |
| Bog‘liq maydon yoki jadval | Ota tanlovni almashtiring. Variantlar yangilangach eski qiymat yangi tanlovga mos kelishini yoki tozalanganini tekshiring. Qator summasi va jami uchun kutilmani test kiritgan miqdor, narx, chegirma hamda tasdiqlangan yaxlitlash qoidasidan mustaqil hisoblang. |
| Ro‘yxat va guruh amali | Filtrga mos va mos kelmaydigan test yozuvlarini tayyorlang. Qidiruv, saralash yoki sahifalashdan keyin kutilgan IDlar va ularning tartibini solishtiring. Guruh amalidan so‘ng tanlangan IDlarni ham, tanlanmagan nazorat yozuvini ham qayta oching. |
| Biriktirma va eksport | Sintetik fayl bilan preview, ota formadagi Save yoki Cancel va qayta ochishni tekshiring. Eksport qamrovda bo‘lsa, yuklangan faylni o‘qib, sarlavhalar va filtrga mos yozuvlarni test ma’lumotiga solishtiring. |
| Status, audit va o‘chirish | Status o‘zgargach yozuvni qayta oching. Tarix ko‘rsatilsa, shu ID uchun kutilgan hodisa va oldingi/yangi qiymatlarni toping. O‘chirishga maxsus test yozuvi ajrating. Cancel’dan keyin u mavjudligini, tasdiqdan keyin esa aniq qidiruv natijasi kutilgan holatga kelganini tekshiring. |

## Formalardan olingan amaliy misollar

- **Кассы.** Kassa uchun ikki ish zonasini va valyutani tanlang. Bir zonani olib
  tashlab saqlang. Qayta ochilganda qolgan zonaning kodi va avvalgi valyuta mos
  kelishi kerak. Bu bitta tanlov o‘zgarishi boshqa bog‘lanishga ta’sirini ham tekshiradi.
- **КПЭ по рабочим зонам.** Oy va ish zonasini to‘ldirib, barcha KPI qiymatlarini
  bo‘sh qoldiring. KPI talabini tekshirgach, faqat bitta ko‘rsatkichga qiymat
  kiriting. Saqlangan yozuvda oy, zona va shu ko‘rsatkichni solishtiring.
- **Договоры importi.** Yangilash ssenariysida faylga test yaratgan shartnomaning
  IDsi va yangi qiymatini yozing. Importni bekor qilib avvalgi qiymatni tekshiring.
  Faylni qayta import qilib tasdiqlang va o‘sha IDdagi yangi qiymatni o‘qing.
  Yaratish ssenariysida ID ustunini bo‘sh qoldiring. Yangi IDni ro‘yxatdan topib,
  View va qayta ochilgan Edit’dagi qiymatlarni fayldagiga solishtiring.
