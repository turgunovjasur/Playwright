# A2 migratsiya ichki hisobi

`a2-internal-tracker.xlsx` — formalar, testcase'lar, test urinishlari va
muammolarni yuritish uchun ichki ishchi jadval. Hozir u Google Sheets'dagi
`Not given` varag'ining 1009 forma yo'li bilan to'ldirilgan. Supplier pilotidan
keyin 1003 route `not_tested`, 2 route `failed`, 4 route `needs_review`.
22 testcase, 24 manual urinish va 1 ochiq muammo bor; nashr tarixi bo'sh.
Bu fayl testlarni yoki Google Sheets sinxronizatsiyasini o'zi bajarmaydi.

Pilot hisoboti: [supplier-20260928.md](supplier-20260928.md). Natijalar va
bog'lanishlarning mashina o'qiydigan nusxasi: [supplier-20260928.json](supplier-20260928.json).
Avtotest `written_not_run`; manual natijalar pytest natijasi deb hisoblanmaydi.

## Varaqlar va bog'lanishlar

- **Holat:** reyestr va jurnallardan hisoblanadigan joriy ko'rsatkichlar.
- **Formalar:** yo'l, manbadagi menyu, ichki status, tekshiruv qamrovi,
  oxirgi run, bilim fayli, avtotest va nashr holati. `Forma ID` yo'lning
  SHA-256 hashidan olingan o'zgarmas kalit; qator raqami kalit emas.
- **Testcaselar:** `Case ID`, `Forma ID`, versiya, old shartlar, qadamlar,
  kutilgan natija va avtotestga bog'lanish. Ssenariy o'zgarsa versiya oshiriladi;
  oldingi runlarga tegishli versiya saqlanadi.
- **Runlar:** har bajarilgan urinish uchun `Run ID`, case versiyasi, muhit,
  rol/filial, vaqt, amaldagi natija, dalil va muammo IDlari. Retest yangi qator;
  oldingi natija o'chirilmaydi.
- **Muammolar:** takrorlash qadamlari, kutilgan/amaldagi natija, muhimlik,
  dalil, ochiq/yopiq holat va retest. Ilova xatosi, test xatosi, ruxsat,
  muhit va test ma'lumoti yetishmasligi ajratiladi.
- **Nashr tarixi:** yakunda Google Sheets'ga yozilgan har o'zgarishning
  eski/yangi qiymati, asos runlari, review, vaqt va qayta o'qish natijasi.

## Bitta forma bilan ishlash

1. Forma uchun kompaniya/rol/filial va tekshiruv qamrovini aniqlash.
   Manbadan kelgan menyu va root hali live UI tasdig'i emas.
2. Mavjud forma bilimini o'qish, testcase'larni tayyorlash yoki moslashtirish.
3. Bajarilgan har testcase urinishini dalili bilan Runlar'ga yozish.
   Bajarilmagan, o'tkazib yuborilgan yoki noaniq tekshiruvga `passed` yozilmaydi.
4. Xato/kamchiliklarni Muammolar'ga yozish. Tuzatishdan keyingi muvaffaqiyatli
   retest dalili bo'lmaguncha muammoni `closed` qilmaslik.
5. Tasdiqlangan forma bilimini mavjud canonical dossierga yozish va reyestrda
   unga havola berish. Foydalanuvchi shu vazifa doirasida bilim va bajarilgan
   testcase'larni saqlab borishni so'ragan. Repo bilimlarining authoritysi
   `skills/project-guide/SKILL.md`; bu hujjat foydalanuvchi uchun ishchi qo'llanma.
6. Takrorlanuvchi yoki muhim ssenariyga kerak bo'lsa `write-test` tartibi bilan
   avtotest yozish va testcase'ga node ID/faylni bog'lash. Yozilgan, lekin
   bajarilmagan avtotest: `written_not_run`. Avtotest natijasi faqat haqiqiy
   run dalili bo'lganda `run_passed` yoki `run_failed` bo'ladi.
7. Ichki status va oxirgi run havolasini yangilash. Google Sheets'ga yozishni
   yakuniy reviewgacha qoldirish.

## Status ma'nolari

- `not_tested`: hali tekshirilmagan.
- `in_progress`: tekshiruv davom etmoqda.
- `passed`: belgilangan qamrovdagi barcha zarur tekshiruvlar o'tgan,
  amaldagi natijalar va dalillar mavjud, shu qamrovdagi ochiq muammo yo'q.
- `failed`: kutilgan natijaga zid xatti-harakat dalil bilan qayd etilgan.
- `blocked`: ruxsat, muhit yoki test ma'lumoti sabab tekshiruv tugallanmagan.
- `needs_review`: natija, qamrov yoki dalil yetarli aniqlik bermaydi.

Forma faqat ochilgan bo'lsa qamrov `smoke` deb yoziladi. Funksional qamrov
kelishilmagan yoki tugallanmagan holat umumiy `passed` uchun yetarli emas.
`Review` va `Nashr holati` qo'lda yuritiladi; workbook ularni avtomatik
tasdiqlamaydi va tashqi yozuvni ishga tushirmaydi.

## Bilim va dalilni saqlash

Forma bilimlari `skills/smartup-guide/references/forms/`dagi tegishli dossierda
saqlanadi. Navigation, locator, biznes qoida, known issue, test havolasi hamda
`Status`, `Verified`, `Source` provenance'i loyiha qoidalariga muvofiq yoziladi.
Knowledge o'zgarsa `./.venv/bin/python skills/scripts/validate_skills.py` ishlatiladi.

Tracker'dagi dalil havolasi haqiqiy, saqlanadigan screenshot/trace/logga olib
borishi kerak. Secret, token, cookie, parol va real shaxsiy ma'lumotlar yozilmaydi;
test data uchun alias/parametr ishlatiladi. Keyingi ishda Git'ga qo'shishdan oldin
artifactlar tekshiriladi. Birgalikdagi tahrirda bitta yozuvchi bo'lishi lozim.

## Google Sheets'ni yakunda yangilash

Foydalanuvchi talabiga ko'ra umumiy jadval faqat ishning eng oxirida yangilanadi.
Hozircha hech qanday tashqi yozuv bajarilmagan va avtomatik sync ulanmagan.

1. Yakuniy qamrov bo'yicha testcase, run, muammo va dalillarni review qilish.
2. Yoziladigan aniq o'zgarishlar ro'yxatini tayyorlash; noaniq va tugallanmagan
   formalarga `passed` bermaslik.
3. Google Sheets metadata, joriy path/status va katak validatsiyasini qayta o'qish.
   Yo'lni qaytadan topish; import vaqtidagi qator raqamiga ko'r-ko'rona ishonmaslik.
4. Boshqalar statusni o'zgartirgan, yo'l yo'qolgan yoki dublikat bo'lsa
   `conflict` sifatida qayd etish va o'sha katakni yozmaslik. Ruxsat etilgan
   status qiymatlari aniqlanmaguncha yangi dropdown qiymati yaratmaslik.
5. Faqat tegishli `Test Status` kataklarini yozish. `Prod status`, format,
   formulalar va boshqa ustunlarga tegmaslik.
6. Yozilgan qiymatni qayta o'qish va Nashr tarixi'ga kiritish. Qayta o'qish
   tasdiqlanmaguncha `published` belgisi qo'yilmaydi. Sheets'dagi tekshirish va
   yozish atomar emas; yakuniy yozuv paytida birgalikdagi tahrir muvofiqlashtiriladi.

## Manba va texnik chegaralar

`source-snapshot.json` import paytidagi A:D diapazonining o'zgarmas manba nusxasi;
uni ishchi natijalar bilan tahrirlamang. Natijalar workbook'da yuritiladi.
Snapshot bu faylning qayta tiklash manbasi, live server testi dalili emas.

Holat formulalari har jurnal uchun 6–5005-qatorlarni hisoblaydi. Yangi yozuvni
tegishli Excel Table ichiga qo'shing. 5000 ta yozuvdan oshganda summary formulalari
diapazonini kengaytiring. Bo'sh jurnallarda dropdownlar dastlab 200 ta yozuvga
tayyorlangan; kengaytirishda validatsiyani ham ko'chiring.

Boshlang'ich faylda source row/path mosligi, 1009 ta noyob Forma ID, status
hisoblari va formula qayta hisoblanishi tekshiriladi. Ilova testlari bu faylni
yaratish doirasida ishga tushirilmagan.
