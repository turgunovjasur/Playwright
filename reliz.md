# Smartup reliz regression jurnali

Oxirgi yangilanish: **2026-09-20, 07:51 (Asia/Tashkent)** — smartup.online yangi903410 baseline: **88/88 case, 81 PASS, 4 FAIL, 3 OBSERVED**. Quyidagi checklist regressiyasi yakunlandi; qolgan tizim qamrovi alohida ko‘rsatilgan. Xtrade natijalari tarix sifatida saqlangan.

Ushbu fayl bajarilgan caselar va relizdan keyingi qayta tekshiruv uchun yagona ishchi checklist. Har bir keyingi tekshiruvdan so‘ng tegishli natija, dalil, bug va vaqt shu faylda yangilanadi. Oldingi Xtrade natijasi saqlanadi; smartup.online natijasi alohida ustunda yoziladi. `order_beta` foydalanuvchi ko‘rsatmasi bilan qamrovdan chiqarilgan.

## Muhit va holat

| Maydon | Xtrade — relizdan oldin | smartup.online — relizdan keyin |
|---|---|---|
| URL | https://app3.greenwhite.uz/xtrade/ | https://smartup.online/ |
| Tekshiruv sanasi | 2026-09-19–20 | 20.09.2026: eski login06:38, setup06:42–06:52, biznes/UI06:58–07:49; Asia/Tashkent |
| Deploy/build identifikatori | Aniqlanmagan | Frontend resource marker20260919T060; backend release ID tasdiqlanmagan. [Dalil](outputs/online-regression-20260920/usd-forms/ui-build.json) |
| Setup | **29 passed, 0 failed, 1 deselected**, 579.35 soniya | Yangi setup903410:28passed,1skipped(licensepurchase),1deselected(company),0failed;574.26s;smartup.online |
| Bajarilish usuli | Local pytest setup; jonli Playwright, parallel bosqichda 4 alohida brauzer | Local pytest setup; keyin4mustaqil jonli Playwright brauzer |
| Natija | Asosiy order va kengaytirilgan chegirma/aksiya/return/USD ssenariylari bajarildi. Yangi saqlangan summa/bonus/qoldiq hisoblarida xato topilmadi. 5 oldingi ochiq topilma va qayta takrorlangan D1 sana nomuvofiqligi bor. F1 yopilgan | YAKUNLANDI — 88/88:81PASS,4FAIL(F2,F3,F5,F7),3OBSERVED. Checklist qamrovi; barcha Smartup formalarining to‘liq testi emas |

Bu barcha Smartup formalarining to‘liq regressioni emas. Asosiy e’tibor oddiy order, Excel import, lifecycle va hisob-kitobga qaratildi. Formalarning faqat ochilishi saqlash yoki biznes oqimi to‘liq o‘tdi degani emas.

**Belgilar:** PASS — ko‘rsatilgan tekshiruv o‘tdi; FAIL — kutilgan natijadan og‘ish; OBSERVED — xatti-harakat qayd etildi, talab aniqligi cheklangan; NOT RUN — tekshirilmagan. Jadvaldagi har bir qator regression case; setupning pytest natijalari bu88case soniga alohida qo‘shilmaydi.

## Case inventari va keyingi foydalanish

Hozir **88 ta takrorlanmaydigan case ID** bor. Bu 88 ta mustaqil pytest testi degani emas: ayrim qatorlar bitta ketma-ket oqimning qadami yoki bir nechta variantni jamlaydi. Xtrade setup29passed, Online setup28passed+1skipped natijalari SET-01 ichida qayd etilgan. Caselar uchun ma’lumotlar, bajarilgan qadamlar, kutilgan/haqiqiy natijalar, cheklovlar va bo‘limga tegishli screenshot/trace havolalari quyida saqlanadi.

| Yo‘nalish | Case IDlar | Soni | Retest/autotest uchun tayyorgarlik |
|---|---|---:|---|
| Setup | SET-01 | 1 | Yangi muhitda setup; Online903410da28passed,1skipped,1deselected,0failed |
| Oddiy order | ORD-01–11 | 11 | Narx7000, stock100, toza testclient; Save/reopen va keyingi edit bir hujjatda |
| Excel import | IMP-01–10 | 10 | Shablondagi productcode/mappingni yangi muhitga moslash; invalid Save uchun listda yangi hujjat yo‘qligini tekshirish |
| Statuslar va moliya | LIFE-01–08, FIN-01–04 | 12 | ORD-11dan keyin ketma-ket; qarz, prepay, faolorder va qoldiqni har bosqichda o‘lchash |
| Aksiyalar | ACT-01–13 | 13 | Barcha5aksiya: qty10→discount10%; qty10→bonus1; cyclic10→bonus1; amount100000→discount5%; amount100000→bonus1 |
| Hisobot/export/print | RPT-01–09 | 9 | Import draft2+3dona/35000 va prepay3000; fayl mazmunini tekshirish, printstubni fizik print deb hisoblamaslik |
| Qo‘shimcha formalar | FRM-01–11 | 11 | Har qatordagi bosqich chegarasini saqlash: ochilish, wizard yoki read-only natija; Save coverage deb kengaytirmaslik |
| Qo‘lda chegirma/to‘lov turi | DISC-01–06, PAY-01–02 | 8 | Testroomga10% preset; foiz/summa, qator/order kombinatsiyasi; saved view va reload assertionlari |
| Qaytarish | RET-01–03 | 3 | Arxivlangan2dona/14000 source; return narx turi roomga ulangan; partial1→remaining1, keyin over-return nazorati |
| USD | USD-01–04 | 4 | USD mahsulot narxi1; alohida USD qarz/prepay; payment auto-offset o‘chiq; faqat USD qatori tanlanadi |
| Sana | DATE-01–06 | 6 | Haqiqiy vaqt/timezone, server defaulti va yuborilgan sana; hisob-kitob uchun qarz ham, prepay ham musbat. Biznes sana qoidasi devdan aniqlashtiriladi |

**smartup.online’da yurish:** bu fayldagi Xtrade natijalari tarix sifatida qoladi; yangi natija smartup.online ustuniga build, vaqt, yangi hujjat IDsi va dalil bilan yoziladi. Xtrade IDlarini qayta ishlatmaslik. Asosiy zanjir: SET→ORD→IMP→LIFE/FIN; RPT/FRM uchun yuqorida ko‘rsatilgan holatni tayyorlash; keyin DISC/PAY/ACT, RET, USD va DATE. Bir clientning bir valyutadagi moliyaviy caselari ketma-ket yoki alohida clientlar bilan bajariladi. ACT-12/13ning eski absolut rezerv1/balans10000 qiymatlari Xtrade holatidir: yangi muhitda aynan11dona rezerv va56700summa deltasini ham tekshirish kerak.

**Autotestga o‘tkazish:** case IDlarini test nomi/Allure tavsifi bilan bog‘lash; avval mavjud avtomatlashtirilgan testlar bilan qamrovni solishtirish, so‘ng yetishmayotganlarini yozish. Ushbu sessiyadagi jonli Playwright tekshiruvlari reusable pytest/CI testlari tayyor degani emas. ACT-06dagi discount va bonus threshold variantlari, DISC-05dagi summa/foiz kombinatsiyalari, IMP-07dagi New/Draft Save kabi jamlangan qatorlarni alohida parametr yoki testga ajratish kerak. Har testda boshlang‘ich holat, qadam, aniq assertion, Save/reopen tekshiruvi (qo‘llansa), yakuniy data holati va dalil bo‘lsin. Fixed949382, entityID yoki20.09 sanasini hardcode qilmaslik.

**Aniqlashtirish talab qiladigan holatlar:** OBSERVED natijalarni avtomatik biznes talab deb qabul qilmaslik. D1ning xatti-harakati qayta kuzatilgan, lekin “xato yoki kutilgan biznes sana qoidasi” dev bilan hali kelishilmagan; yakuniy sana assertionini shu javobdan keyin belgilash. F1 uchun esa real Save bloklangani tasdiqlangan, shuning uchun manfiy import finalgacha yetishi o‘zi saqlash bugi sifatida assert qilinmaydi. `order_beta` qamrovdan chiqarilgan holda qoladi.

**Dalil auditi aniqliklari:** RET-02da avvalgi return haqidagi tasdiqdan keyin `Частичный возврат` o‘chiq rejim qolgan1donani olgani tekshirilgan. RET-03dagi “zero” tugagan source uchun0pozitsiya va Next bloklanishidir; literal qty0 bilan Save yoki backend over-return alohida bajarilgan deb yozilmasin. USD-02/ACT-06 editida `Количество заказа` eski qiymatni saqlagan; tahrirdagi yangi miqdor `Количество продажи` va saqlangan summa bilan tasdiqlangan. RET-01dagi prepay+7000 to‘liq hisob-kitob qilingan sourcega tegishli; RPT-03dagi32000 esa35000−prepay3000 bo‘lib, bu shartlar retestda alohida tayyorlanadi. HTTP200ning o‘zi muvaffaqiyat emas: DATE-04da javob ichida error bor, DATE-05da esa hech qanday moliyaviy o‘zgarish bo‘lmagan. Return tafsilotlari (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-return/findings.md`), USD tafsilotlari (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-usd/findings.md`).

## Qayta tekshiruv uchun boshlang‘ich ma’lumotlar

1. smartup.online deploy/build va sanasini yuqorida qayd etish. Tegishli test company/filialda yangi setup baseline ishlatish; Xtrade entity ID va kodlari u yerda bor deb faraz qilmaslik.
2. Baseline: room, staff, client, asosiy ombor, UZS narx turi, 7 000 narxli mahsulot, 100 dona boshlang‘ich qoldiq, kassaga kirish. Client qarzi va oldindan to‘lovi boshida 0.
3. Aksiyalar: 10 dona uchun 10% chegirma; 10 dona uchun 1 bonus. Hisob-kitob va qoldiq caselarini quyidagi tartibda bajarish, bir clientni parallel moliyaviy testlarda o‘zgartirmaslik.
4. Import: [Excel shablon](outputs/xtrade-regression-20260919/order-import-template.xlsx). Yangi baseline mahsulot kodini A2/A3 ga qo‘yish; B2=2, B3=3, C2=C3=Y. Xtrade kodi smartup.online uchun avtomatik yaroqli emas.
5. Import mapping: boshlang‘ich qator 2; identifikatsiya `Код продукции (PC)`; kod A/1, miqdor B/2, `Балансовый` C/3; ombor va UZS narx turini tanlash. Yangi userda mappingni qayta tekshirish.
6. Local runner uchun `.env` mavjud bo‘lsa URL/NEW_CODE qiymatlari CLI flaglardan ustun. Yangi setupda NEW_CODE=1; muvaffaqiyatli baseline qayta ishlatilganda NEW_CODE=0. Secretlarni ushbu faylga yozmaslik.

## A. Setup, oddiy order va tahrirlash

| ID | Qadam / case | Kutilgan natija | Xtrade natijasi | smartup.online |
|---|---|---|---|---|
| SET-01 | Local `./.venv/bin/python scripts/run_tests.py setup` | Setup muvaffaqiyatli; test entitylar tayyor | PASS — 29 passed, 1 deselected | PASS — Yangi setup903410:28passed,1skipped(licensepurchase),1deselected(company),0failed;574.26s;smartup.online [dalil1](outputs/online-regression-20260920/setup/baseline.json) |
| ORD-01 | Yangi setup user bilan kirish → Заказы | Dashboard/list ochiladi; yangi filialda boshlang‘ich order yo‘q | PASS | PASS — Yangi903410user dashboard va orderlist ochildi; boshlang‘ich order listi bo‘sh. [dalil1](outputs/online-regression-20260920/order-lifecycle/03-baseline-order-list.png) |
| ORD-02 | Oddiy order yaratish, asosiy maydonlarni ko‘rish | Room, staff va client joriy setupga mos | PASS | PASS — Room/staff/client903410 auto-fill mos. [dalil1](outputs/online-regression-20260920/order-lifecycle/04-order-main.png) |
| ORD-03 | Sana maydonini tozalash va fokusdan chiqish | Bo‘sh sana qolmasligi | OBSERVED — oldingi valid sana tiklandi | FAIL — F7: sana maydonini Ctrl+A→Backspace bilan tozalash gen_delivery_date ga {} yuboradi; HTTP500 va UI Hashmap:deal_time not found. Mustaqil manualretestda takrorlandi. Valid sanani atomicfill yoki calendar bilan tanlashHTTP200; yangiorder saqlanmagan. Bo‘sh sananing tiklanishi bu xatoni bartaraf qilmaydi. [dalil1](outputs/online-regression-20260920/date-input-recheck/04-manual-clear-alert.png), [dalil2](outputs/online-regression-20260920/date-input-recheck/date-input-network.json) |
| ORD-04 | Mahsulotsiz ТМЦ → Далее | Keyingi bosqich bloklanadi | PASS — H02-ANOR279-004 | PASS — Mahsulotsiz Next H02-ANOR279-004 bilan bloklandi. [dalil1](outputs/online-regression-20260920/order-lifecycle/06-no-product-next.png) |
| ORD-05 | Mahsulot miqdorini 0 qilish → Далее | Miqdor validatsiyasi bloklaydi | PASS — H02-ANOR279-005 | PASS — Qty0 Next H02-ANOR279-005 bilan bloklandi. [dalil1](outputs/online-regression-20260920/order-lifecycle/07-zero-quantity.png) |
| ORD-06 | Oddiy inputga −1 yozish | Manfiy miqdor qabul qilinmaydi | OBSERVED — input 1 ga aylantirdi | OBSERVED — Oddiy inputga−1kiritilgandan keyin ko‘ringan qiymat=1 [dalil1](outputs/online-regression-20260920/order-lifecycle/08-negative-input.png) |
| ORD-07 | Qoldiq 100 bo‘lganda 101 kiritish | Qoldiqdan ortiq miqdor cheklanadi | PASS — oldingi valid qiymatga qaytdi | PASS — Qoldiq100da101kiritish qabul qilinmadi; input=10 [dalil1](outputs/online-regression-20260920/order-lifecycle/09-over-stock-input.png) |
| ORD-08 | 3 dona, narx 7 000 | Jami 21 000, mavjud qoldiq 97/100 | PASS | PASS — Qty3×7000=21000, wizardhisobi mos. [dalil1](outputs/online-regression-20260920/order-lifecycle/10-three-products.png) |
| ORD-09 | Подбор → tanlangan mahsulot miqdori 3→4 → qaytish | Jami 28 000, wizardga 4 dona o‘tadi | PASS | PASS — Подборdagi3→4wizardga ko‘chdi;28000. [dalil1](outputs/online-regression-20260920/order-lifecycle/14-picker-return.png) |
| ORD-10 | 4 dona / 28 000, naqd to‘lov, Черновик saqlash → view | Client, miqdor, summa va status saqlanadi | PASS — order 265282 | PASS — Order287769073:qty4/28000UZS naqd Черновикsaved/reopened. [dalil1](outputs/online-regression-20260920/order-lifecycle/16-saved-order-view.png) |
| ORD-11 | Shu draftni edit: 4→2 dona, izoh → saqlash → view | Jami 14 000; izoh saqlanadi | PASS | PASS — Order287769073 qty4→2,14000UZS va izoh saved/reopened. [dalil1](outputs/online-regression-20260920/order-lifecycle/17-edited-order-view.png) |

## B. Excel order import

| ID | Qadam / case | Kutilgan natija | Xtrade natijasi | smartup.online |
|---|---|---|---|---|
| IMP-01 | O‘zimiz tuzgan XLSX: bir mahsulot 2 va 3 dona; mapping yuqoridagidek; upload va tasdiq | 2 qator, 0 xato; 5 dona / 35 000 wizardga o‘tadi | PASS | PASS — 2parsed rows qty2+3, noerrors; transfer5units35000. Mapping PC,start2,code1,quantity2,balance3. [dalil1](outputs/online-regression-20260920/import-reports/IMP-01-parsed.png), [dalil2](outputs/online-regression-20260920/import-reports/IMP-01-wizard.png) |
| IMP-02 | Import natijasini Черновик saqlash va qayta ochish | 2 pozitsiya: 14 000 + 21 000; jami 35 000 | PASS — order 265283 | PASS — Draft287769065 saved/reopened withqty2+3, amounts14000+21000 total35000. [dalil1](outputs/online-regression-20260920/import-reports/IMP-02-saved.png), [dalil2](outputs/online-regression-20260920/import-reports/save-response-01.json) |
| IMP-03 | Балансовый ustuni/qiymatini bermay import | Y/N validatsiyasi, qatorlar import qilinmasligi | PASS — 2 va 3-qatorlarda aniq xato | PASS — Blankbalance causes Y/N errors for Excelrows2and3; zeroproducts parsed. [dalil1](outputs/online-regression-20260920/import-reports/IMP-03-errors.png) |
| IMP-04 | Noma’lum mahsulot kodi bilan import | Xatoda Excel qatori va mahsulot kodi ko‘rsatiladi | PASS — qator 2 rad etildi | PASS — Unknownproduct rejected atExcelrow2 withcode UNKNOWN_ONLINE_903410. [dalil1](outputs/online-regression-20260920/import-reports/IMP-04-error.png) |
| IMP-05 | Bitta valid qty2 va bitta noma’lum kodli qatorni import, valid qatorni qo‘shish | Faqat valid mahsulot: 2 dona / 14 000 | PASS | PASS — Mixedrows: validqty2 transferredalone,total14000; invalidExcelrow3 rejected. [dalil1](outputs/online-regression-20260920/import-reports/IMP-05-parsed.png), [dalil2](outputs/online-regression-20260920/import-reports/IMP-05-transferred.png) |
| IMP-06 | Qty0 import → qatorlarni qo‘shish → Далее | Nol miqdor davom etmasligi; importda ham aniq xato ma’qul | OBSERVED — importda xato yo‘q, wizardda bo‘shga aylandi; Далее bloklandi | OBSERVED — Importedzero gives noimporterror, becomesblank requiredquantity and blocksNext atproductstep. [dalil1](outputs/online-regression-20260920/import-reports/IMP-06-zero-block.png) |
| IMP-07 | Qty−1 import → qo‘shish → Далее; boshqa bo‘sh qatorlarni valid qilish → Новый va Черновик holatlarida Сохранить + tasdiq | Manfiy miqdorli order saqlanmasligi | **PASS — 23:40 retest:** ikkala Save serverda −1 validatsiyasi bilan rad etildi; reloaddan keyin yangi order yo‘q. Dastlabki FAIL bahosi almashtirildi | PASS — Both New and Draft actual Save+confirm rejected HTTP500: Кол-во заказов=-1. List reloaded; own valid35000draft remains. Other agents created independentdrafts duringrun. [dalil1](outputs/online-regression-20260920/import-reports/IMP-07-new-rejected.png), [dalil2](outputs/online-regression-20260920/import-reports/IMP-07-draft-rejected.png) |
| IMP-08 | Bir xil mahsulotni ikki qatorda import; ТМЦ, final va saved view SKUlarini solishtirish | SKU 1, pozitsiya 2 barcha bosqichda | **FAIL — F2**, ТМЦ SKU2, saved view SKU1 | FAIL — Sameproduct twice: wizard SKU2/positions2; final andsaved view SKU1/positions2. [dalil1](outputs/online-regression-20260920/import-reports/IMP-01-wizard.png), [dalil2](outputs/online-regression-20260920/import-reports/IMP-02-final.png) |
| IMP-09 | Qoldiq100, bir mahsulot ikki qator60+60 → Новый saqlash | Jami120 qoldiqdan ortiq bo‘lgani uchun saqlanmaydi | PASS — server A02-02-024; wizard oldin bloklamadi | PASS — Importedduplicate rows edited60+60 (UIstock100); actualNewSave HTTP400 A02-02-024 stockguard. Draft update rejected. [dalil1](outputs/online-regression-20260920/import-reports/IMP-09-120-wizard.png), [dalil2](outputs/online-regression-20260920/import-reports/IMP-09-save-result.png) |
| IMP-10 | IMP-09 dan so‘ng import orderni 2+3 / 35 000 draftga qaytarish → view | Valid miqdor saqlangan | PASS — 265283 draft 35 000 | PASS — Draft287769065 restored and reloaded qty2+3,total35000,cash. [dalil1](outputs/online-regression-20260920/import-reports/IMP-10-restored.png), [dalil2](outputs/online-regression-20260920/import-reports/save-response-05.json) |

IMP-07 qayta tekshirildi (2026-09-19 23:40). Import qatorlari 1, −1, 2 dona; narx7 000, jami14 000. To‘lov turi tanlangan holda **Новый**, so‘ng **Черновик** uchun Сохранить va tasdiq bosildi. Ikkala `order+add$save` so‘rovi HTTP500 bilan `Z:Неверно указано значение "Кол-во заказов". Кол-во заказов = -1` javobini berdi; UI xatoni ko‘rsatdi. Order list reload qilinganda avvalgi yagona35 000 draft saqlandi, yangi order yaratilmagan. Foydalanuvchi mezoni bo‘yicha saqlash xatosi **tasdiqlanmadi**; manfiy miqdorning wizardda ko‘rinishi faqat kuzatuv sifatida qoldirildi.

Dalillar: Новый rad etildi (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/negative-save-retest/03-new-rejected-alert.png`), Черновик rad etildi (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/negative-save-retest/04-draft-rejected-alert.png`), reloaddan keyingi list (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/negative-save-retest/06-order-list-after-reload.png`), server javoblari (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/negative-save-retest/save-responses.json`), retest trace (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/negative-save-retest/trace.zip`).

## C. Lifecycle, qarz va to‘lov — ketma-ket bajariladi

Baseline: ORD-11 dagi 2 dona / 14 000 draft. Import drafti moliyaviy hisobga kirmasligi kerak.

| ID | Qadam / case | Kutilgan natija | Xtrade natijasi | smartup.online |
|---|---|---|---|---|
| LIFE-01 | Черновик → Новый, tasdiqlash | Новый gridda saqlanadi | PASS | PASS — Order287769073 Новый persisted; birinchi cached modified_id A02-16-157 guarddan keyin reload va takroriy edit→New control muvaffaqiyatli,guardtakrorlanmadi. [dalil1](outputs/online-regression-20260920/order-lifecycle/status-repro-after.png) |
| LIFE-02 | Новый → В обработке | Yangi status saqlanadi | PASS | PASS — Order287769073 statusВ обработке,server success1 va grid mos. [dalil1](outputs/online-regression-20260920/order-lifecycle/life-2-LIFE-02.png) |
| LIFE-03 | В обработке → В ожидании | Yangi status saqlanadi | PASS | PASS — Order287769073 statusВ ожидании,server success1 va grid mos. [dalil1](outputs/online-regression-20260920/order-lifecycle/life-3-LIFE-03.png) |
| LIFE-04 | В ожидании → Отгружен | Yangi status saqlanadi | PASS | PASS — Order287769073 statusОтгружен,server success1 va grid mos. [dalil1](outputs/online-regression-20260920/order-lifecycle/life-4-LIFE-04.png) |
| LIFE-05 | Отгружен → Доставлен; client settlement | Qarz0, oldindan0, order14 000, balans−14 000 | PASS | PASS — Order287769073 Доставлен;UZSdebt0/prepay0/order14000/balance−14000. [dalil1](outputs/online-regression-20260920/order-lifecycle/life-5-delivered-balance.png) |
| FIN-01 | Orderni arxivlash → settlement | Order0, qarz14 000, balans−14 000 | PASS | PASS — Order287769073 Архив;UZSdebt14000/prepay0/order0/balance−14000. [dalil1](outputs/online-regression-20260920/order-lifecycle/fin-1-archived-balance.png) |
| FIN-02 | 7 000 naqd to‘lov; auto-offset o‘chiq; Провести | Qarz14 000, oldindan7 000, balans−7 000 | PASS | PASS — 7000UZS paymentПровести autooffsetoff;debt14000/prepay7000/balance−7000. [dalil1](outputs/online-regression-20260920/order-lifecycle/fin-2-after-payment.png) |
| FIN-03 | Manual Взаиморасчет → tasdiqlash | Qarz7 000, oldindan0, balans−7 000 | PASS | PASS — 20.09currentdate UZSmanualoffset7000;debt7000/prepay0/balance−7000. [dalil1](outputs/online-regression-20260920/order-lifecycle/fin-3-offset-result.png) |
| FIN-04 | 10 000 to‘lov, auto-offset yoqilgan → Провести | Qarz0, oldindan3 000, balans3 000 | PASS | PASS — UZS 10 000 payment posted with automatic offset: 7 000 debt cleared; debt 0, prepay 3 000, active order 0, balance 3 000. Zero confirmed by totals; row renders empty zero cells. [dalil1](outputs/online-regression-20260920/order-lifecycle/fin-4-autooffset-result.png) |
| LIFE-06 | Yangi 3 dona / 21 000 order yaratish → settlement | Order21 000, oldindan3 000, balans−18 000 | PASS — order265284 | PASS — Order287769625 New qty3/21000; debt0/prepay3000/activeorder21000/balance−18000. [dalil1](outputs/online-regression-20260920/order-lifecycle/life06-new-ledger.png) |
| LIFE-07 | Shu yangi orderni bekor qilish → settlement | Order0, qarz0, oldindan3 000, balans3 000 | PASS | PASS — Order287769625 canceled; UZS debt0/prepay3000/activeorder0/balance3000. [dalil1](outputs/online-regression-20260920/order-lifecycle/life07-canceled-ledger.png) |
| LIFE-08 | Bekor qilishdan so‘ng yangi orderda qoldiqni ko‘rish | 100−arxivlangan2=98; canceled3 rezervdan chiqqan | PASS — 98/98 | PASS — After cancel287769625 UZSstock98/reserved0/available98; source287769073 archivedqty2. [dalil1](outputs/online-regression-20260920/order-lifecycle/life08-restored-stock.png) |

## D. Aksiyalar

Bu dastlabki caselar yakuniy wizardgacha bajarilgan edi. Keyingi **G bo‘limida** barcha5aksiya uchun haqiqiy Save/reopen, chegaralar, kombinatsiyalar va New→Canceled tekshiruvlari keltirilgan.

| ID | Qadam / case | Kutilgan natija | Xtrade natijasi | smartup.online |
|---|---|---|---|---|
| ACT-01 | Miqdor10 → Акции | Setupdagi quantity discount/bonus/cyclic aksiyalari ko‘rinadi | PASS — 3 aksiya | PASS — Quantity10 shows quantity discount, quantity bonus, cyclic bonus [dalil1](outputs/online-regression-20260920/discount-actions/20-three-actions.png) |
| ACT-02 | 10% quantity discountni tanlash → final | 70 000−7 000=63 000 | PASS | PASS — 10x7000 quantity10% discount final63000 [dalil1](outputs/online-regression-20260920/discount-actions/21-quantity-discount-final.png) |
| ACT-03 | Discountni olib, quantity bonusni tanlash → final → Акции | 10 pullik dona / 70 000 va 1 bonus mahsulot | PASS | PASS — 10paid plus1bonus quantity action saved70000; Saved action row1 at price0 [dalil1](outputs/online-regression-20260920/discount-actions/24-quantity-bonus-saved.png), [dalil2](outputs/online-regression-20260920/discount-actions/25-quantity-bonus-row.png) |

## E. Hisobot, export va print

Baseline: import drafti 2+3 dona, narx7 000, jami35 000; client oldindan to‘lovi3 000. Har bir forma Order → Накладные menyusidan ochildi.

| ID | Qadam / case | Kutilgan natija | Xtrade natijasi | smartup.online |
|---|---|---|---|---|
| RPT-01 | Лист заказов №1 | Client/product, qty5, jami35 000; header normal satrlarda | Summa PASS; **FAIL F3**, literal `<br>` | FAIL — Totalscorrectqty5/35000, but clientheader literallyrenders<br> tags. [dalil1](outputs/online-regression-20260920/import-reports/RPT-01-order-sheet.png), [dalil2](outputs/online-regression-20260920/import-reports/RPT-01-order-sheet.txt) |
| RPT-02 | Накладная №4 (2012) | Mahsulot, qty5, jami35 000 | PASS | PASS — Invoice4showsproductqty5,sum35000. [dalil1](outputs/online-regression-20260920/import-reports/RPT-02-invoice4.png), [dalil2](outputs/online-regression-20260920/import-reports/RPT-02-invoice4.txt) |
| RPT-03 | Счет на оплату | 2×7 000=14 000; 3×7 000=21 000; jami35 000, oldindan3 000, to‘lash32 000 | PASS | PASS — Invoice lines 2x7000=14000 and 3x7000=21000; total35000 minus current prepayment3000 gives payable32000. Root held financial baseline during check. [dalil1](outputs/online-regression-20260920/import-reports/RPT-03-payment-invoice.png), [dalil2](outputs/online-regression-20260920/import-reports/RPT-03-payment-invoice.txt) |
| RPT-04 | Счет-фактура с НДС | Qty5, jami35 000; baseline uchun Без НДС | PASS — boshqa soliq stavkalari tekshirilmagan | PASS — VATinvoice qty2/14000+qty3/21000 total35000,baseline БезНДС. [dalil1](outputs/online-regression-20260920/import-reports/RPT-04-vat-invoice.png), [dalil2](outputs/online-regression-20260920/import-reports/RPT-04-vat-invoice.txt) |
| RPT-05 | ТТН | Qatorlar3 va2; 21 000 va14 000; tarjima qilingan header | Summa PASS; **FAIL F4**, localization key ko‘rinadi | PASS — TTNcorrectrows3/21000and2/14000; headertranslated Альтернативное название товара. NoUI-ANOR1405key: priorF4notreproducedonline. [dalil1](outputs/online-regression-20260920/import-reports/RPT-05-ttn.png), [dalil2](outputs/online-regression-20260920/import-reports/RPT-05-ttn.txt) |
| RPT-06 | Чек-лист (80 мм) | OrderID/client/product, ikkala qator, jami35 000 | PASS | PASS — 80mmcheckID287769065,client,qty2/14000+3/21000,total35000. [dalil1](outputs/online-regression-20260920/import-reports/RPT-06-check80.png), [dalil2](outputs/online-regression-20260920/import-reports/RPT-06-check80.txt) |
| RPT-07 | Order XML exportini yuklab, faylni parse qilish | ID/statusD/kodlar, qty2+3, summalar14 000+21 000 | PASS — haqiqiy download tekshirildi | PASS — RealXMLdownload parsed ID287769065,statusD,codes903410,qty2+3,amount14000+21000,total35000. [dalil1](outputs/online-regression-20260920/import-reports/RPT-07-order.xml), [dalil2](outputs/online-regression-20260920/import-reports/RPT-07-parsed.json) |
| RPT-08 | Лист заказов Excel download → parse | Qty5, jami35 000; headerda normal newline | PASS — XLSX mazmuni tekshirildi | PASS — DownloadedXLSX parsed: productqty5,amount35000; clientheader containsrealnewlines,notliteralbr. [dalil1](outputs/online-regression-20260920/import-reports/RPT-08-order-sheet.xlsx), [dalil2](outputs/online-regression-20260920/import-reports/RPT-08-order-sheet.json) |
| RPT-09 | Order sheet Print; chek avtomatik print | `window.print` chaqiriladi | PASS — stub orqali; haqiqiy printer/PDF output tekshirilmagan | PASS — OrdersheetPrintcallswindow.print once;80mmcheckautomaticprintcalls once. Stubonly,nophysicalprinter/PDFtested. [dalil1](outputs/online-regression-20260920/import-reports/RPT-09-sheet-print.json), [dalil2](outputs/online-regression-20260920/import-reports/RPT-09-auto-print.json) |

## F. Orderga tegishli qo‘shimcha formalar

Quyidagi dastlabki caselar read-only yoki saqlanmagan forma darajasida. Keyinchalik return Save/Archive va qoldiq/hisob-kitob **G bo‘limida** bajarildi. Retail checkout va request saqlash hali qamrab olinmagan.

| ID | Qadam / case | Kutilgan natija | Xtrade natijasi | smartup.online |
|---|---|---|---|---|
| FRM-01 | Order settingsni ochish va yopish | Forma ochiladi, matnlar o‘zaro mos | Ochilish PASS; **FAIL F5**, Черновик/Отменено matni zid | FAIL — Settings opens/closes; label says change to Черновик, explanation says drafts older90days become Отменено. F5 reproduced, settings not saved. [dalil1](outputs/online-regression-20260920/usd-forms/frm01-settings-903410.png) |
| FRM-02 | Retail create ikki marta ochish | Forma, workzone va kassa defaultlari; tarjima qilingan label | Ochilish PASS; **FAIL F6**, literal `subfilial` | PASS — Retail opened twice with room-pw903410 and Основная касса. Label Проект is translated; literal subfilial not present on smartup.online. No save. [dalil1](outputs/online-regression-20260920/usd-forms/frm02-retail-first.png), [dalil2](outputs/online-regression-20260920/usd-forms/frm02-retail-second.png) |
| FRM-03 | Arxiv orderlar listi | Arxivlangan14 000 order ko‘rinadi | PASS | PASS — Archive list contains UZS 14,000 and USD 3/2.7. Read-only view confirms order 287769073, Archive, qty2 x 7,000=14,000 UZS, client903410 and delivery20.09.2026. [dalil1](outputs/online-regression-20260920/usd-forms/frm03-archive-list-903410.png), [dalil2](outputs/online-regression-20260920/usd-forms/frm03-archive-view-903410.png) |
| FRM-04 | Bekor qilingan orderlar listi | Bekor qilingan21 000 order ko‘rinadi | PASS | PASS — Canceled list contains UZS21,000; exact view confirms order287769625, statusОтменен, qty3 x 7,000=21,000 and client903410. Read-only inspection. [dalil1](outputs/online-regression-20260920/usd-forms/frm04-cancel-list-903410.png), [dalil2](outputs/online-regression-20260920/usd-forms/frm04-cancel-view-903410.png) |
| FRM-05 | Возврат listi | Bo‘sh grid to‘g‘ri ochiladi | PASS | PASS — Return list opened with empty grid on fresh baseline. [dalil1](outputs/online-regression-20260920/usd-forms/frm05-return-list.png) |
| FRM-06 | Return create | Sana, room/staff, valyuta bilan birinchi bosqich ochiladi | PASS — saqlanmagan | PASS — Return creation first step opens; room/staff defaults903410, UZS currency, date20.09 and delivery21.09. No return saved. [dalil1](outputs/online-regression-20260920/usd-forms/frm06-return-create.png) |
| FRM-07 | Order request listi | Bo‘sh grid ochiladi | PASS | PASS — Order request list opens with empty grid. [dalil1](outputs/online-regression-20260920/usd-forms/frm07-request-list.png) |
| FRM-08 | Request create → mahsulotlar bosqichi | Room/staff/client va bir oylik expiry defaulti | PASS — saqlanmagan | PASS — Wizard reaches products; room/staff/client defaults903410, request20.09 expiry20.10.2026(one month). No save. [dalil1](outputs/online-regression-20260920/usd-forms/frm08-request-main.png), [dalil2](outputs/online-regression-20260920/usd-forms/frm08-request-products.png) |
| FRM-09 | Request mahsulotsiz Далее | Aniq xato bilan bloklanadi | PASS — H02-ANOR1401-003 | PASS — Empty request products cannot advance: H02-ANOR1401-003 explicit error. No save. [dalil1](outputs/online-regression-20260920/usd-forms/frm09-request-empty-blocked.png) |
| FRM-10 | Order list → Debt details | Grid xatosiz ochiladi | PASS — bo‘sh grid | PASS — Order-list Debt details opens without error, empty grid at observation time. [dalil1](outputs/online-regression-20260920/usd-forms/frm10-debt-details.png) |
| FRM-11 | Settlement history | Offset tarixi hisob-kitobga mos | PASS — 2×7 000, jami14 000 | PASS — Settlement history has two UZS entries 7,000+7,000=14,000 and three USD entries 1+2+0.50=3.50, all dated20.09.2026. Currency totals match the actual offsets; no-debt controls created no history. [dalil1](outputs/online-regression-20260920/usd-forms/frm11-full-history.png), [dalil2](outputs/online-regression-20260920/usd-forms/frm11-usd-history.png) |

## G. Kengaytirilgan regression — 2026-09-19–20

Foydalanuvchi topshirig‘i: orderni aksiya, qo‘lda chegirma, return va USD orqali **saqlash va qayta ochishgacha** tekshirish. 4 mustaqil Playwright brauzer ishladi. UZS return tugagach, aksiya orderining New→Canceled moliyaviy/qoldiq ta’siri alohida tekshirildi. `order_beta` chiqarilgan.

| ID | Tekshiruv maqsadi | Xtrade | smartup.online |
|---|---|---|---|
| DISC-01 | Mahsulot qatoriga foiz chegirma → Save → view/edit | PASS — 265298:5×7000−10%=31500, discount3500 saved/reopened. Test10% preset yaratilib faqat testroomga ulandi | PASS — 5x7000 row10%=31500 saved/reopened ID287769076 [dalil1](outputs/online-regression-20260920/discount-actions/08-row10-saved.png) |
| DISC-02 | Mahsulot qatoriga summa chegirma → Save → view | PASS — draft265298: qty4, price7000, har donaga−2800; jami chegirma−11200, saqlangan jami16800. View (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-discount/02-row-amount-saved-view.png`) | PASS — 4x(7000-2800)=16800 persisted [dalil1](outputs/online-regression-20260920/discount-actions/09-row-amount.png) |
| DISC-03 | Order darajasida foiz chegirma → Save → view | PASS — qator discount0, order−10%:35000→31500 saved/reopened | PASS — Order10% only35000to31500 persisted [dalil1](outputs/online-regression-20260920/discount-actions/15-order10-only.png) |
| DISC-04 | Order darajasida summa chegirma → Save → view | PASS — 5×7000−800=34200 saved view; order265298 | PASS — 5x7000-800=34200 persisted [dalil1](outputs/online-regression-20260920/discount-actions/12-order-amount.png) |
| DISC-05 | Qator va order chegirmasi birgalikda; editda qayta hisob | PASS — 4×(7000−2800)−800=16000; qty5 editda20200. Qator10%+order10%:35000→31500→28350; saved view tasdiqladi | PASS — 4x(7000-2800)-800=16000 persisted; Quantity4to5 recalculates combined discount to20200 persisted; Row10% then order10% sequential35000to31500to28350 persisted [dalil1](outputs/online-regression-20260920/discount-actions/10-combined-amount.png), [dalil2](outputs/online-regression-20260920/discount-actions/11-edit-combined-amount.png) |
| DISC-06 | Chegirma chegaralari; valid/invalid Save natijasi | PASS — order35000 uchun−35001 kiritish−35000ga cheklandi; jami0 draft saqlandi, manfiy summa hosil bo‘lmadi | PASS — Input-35001 capped-35000 on35000 order; zero-total draft saved [dalil1](outputs/online-regression-20260920/discount-actions/13-discount-cap.png) |
| PAY-01 | Chegirmali orderni Перечисление to‘lov turi bilan saqlash | PASS — 265298,31500, to‘lov turi saqlandi | PASS — Payment transfer persists;31500 unchanged [dalil1](outputs/online-regression-20260920/discount-actions/16-banktransfer.png) |
| PAY-02 | Chegirmali orderni Терминал bilan saqlash → hard reload | PASS — 265298,31500, Терминал va discount10% saqlangan | PASS — Payment terminal persists;31500 unchanged; Hard reload confirms Terminal31500 [dalil1](outputs/online-regression-20260920/discount-actions/17-terminal.png), [dalil2](outputs/online-regression-20260920/discount-actions/18-discount-hardreload.png) |
| ACT-04 | Quantity discount 10% bilan draft Save/reopen | PASS — draft265299: qty10×7000−10%=63000, saved view tasdiqladi | PASS — Quantity10% discount: draft287770806 saved63000 in list and reopened for edit [dalil1](outputs/online-regression-20260920/discount-actions/21-quantity-discount-final.png), [dalil2](outputs/online-regression-20260920/discount-actions/22-quantity-discount-saved.png) |
| ACT-05 | Quantity bonus1 bilan draft Save/reopen | PASS — qty10, bonus1, jami70000 saqlandi | PASS — 10paid plus1bonus quantity action saved70000; Saved action row1 at price0 [dalil1](outputs/online-regression-20260920/discount-actions/24-quantity-bonus-saved.png), [dalil2](outputs/online-regression-20260920/discount-actions/25-quantity-bonus-row.png) |
| ACT-06 | Threshold10→9 edit; aksiya qayta hisob/persistence | PASS — discount/bonus olib tashlandi, jami63000. Tez Nextda vaqtinchalik summa farqi kuzatilgan, recalculation tugagach qaytarilmadi; saved natijalar to‘g‘ri | PASS — Quantity-discount10to9 removes discount, saved63000; Quantity-bonus10to9 removed bonus; saved63000 [dalil1](outputs/online-regression-20260920/discount-actions/trace.zip), [dalil2](outputs/online-regression-20260920/discount-actions/26-bonus-below-threshold.png) |
| ACT-07 | Cyclic bonus, qty20 → bonus2; Save/reopen | PASS — bonus2, jami140000 saved/reopened | PASS — Quantity20 cyclic2bonus saved140000; Saved action row2 at price0 [dalil1](outputs/online-regression-20260920/discount-actions/27-cyclic-bonus-saved.png), [dalil2](outputs/online-regression-20260920/discount-actions/28-cyclic2-bonus-row.png) |
| ACT-08 | Amount100000 threshold, qty15×7000; discount5% Save/reopen | PASS — 105000−5250=99750; qty14da98000 va discount0 saqlandi | PASS — Amount105000 gets5% discount saved99750; Quantity14 amount98000 removes5% discount saved98000 [dalil1](outputs/online-regression-20260920/discount-actions/29-amount-discount.png), [dalil2](outputs/online-regression-20260920/discount-actions/30-amount-discount-below.png) |
| ACT-09 | Amount100000 threshold, bonus1 Save/reopen | PASS — 105000da bonus1; 98000da bonus olib tashlandi | PASS — Amount105000 gets1free bonus saved105000; Amount98000 below100000; saved98000; Saved view has no action tab/freebonus below threshold; Saved action row1 at price0 at105000 [dalil1](outputs/online-regression-20260920/discount-actions/31-amount-bonus.png), [dalil2](outputs/online-regression-20260920/discount-actions/33-amount-bonus-below.png) |
| ACT-10 | Quantity discount10% + quantity bonus1 birgalikda Save/reload | PASS — gross70000, discount7000, total63000, freebonus1 saqlandi | PASS — 10paid quantity10% discount plus1bonus saved63000; Saved quantity bonus row1 at price0 [dalil1](outputs/online-regression-20260920/discount-actions/34-combo-discount-bonus.png), [dalil2](outputs/online-regression-20260920/discount-actions/35-combo-bonus-row.png) |
| ACT-11 | Aksiya discount+bonus ustiga order10% → Save/reload | PASS — 63000−6300=56700, freebonus1 saqlandi;265299 | PASS — Quantity10% plus1freebonus plus order10%:70000to63000to56700 saved; Hard reload56700 and1freequantitybonus persisted [dalil1](outputs/online-regression-20260920/discount-actions/36-combo-plus-order10.png), [dalil2](outputs/online-regression-20260920/discount-actions/38-combo-hardreload-bonus.png) |
| ACT-12 | Kombinatsiyali aksiya orderini Новый qilish | PASS — rezerv1→12 (10paid+1bonus); available99→88; UZSorder7000→63700, balans10000→−46700 | PASS — Promo287770806 New qty10paid+1free,total56700: reserved0→11,available100→89; UZSactiveorder0→56700,balance17000→−39700;debt7000/prepay24000unchanged. [dalil1](outputs/online-regression-20260920/order-lifecycle/act12-reserved-stock.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/act12-new-ledger.png) |
| ACT-13 | Shu orderni bekor qilish | PASS — barcha11dona rezervdan chiqdi; reserved1/available99, UZSorder7000/balance10000 tiklandi;265299 canceled listda56700 | PASS — Promo287770806 canceled: all11unitsreleased,reserved0/available100;UZSactiveorder0/balance17000restored,debt7000/prepay24000unchanged. [dalil1](outputs/online-regression-20260920/order-lifecycle/act13-canceled-stock.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/act13-canceled-ledger.png) |
| RET-01 | Partial returnni haqiqiy saqlash/post va qayta ochish | PASS — return265300, source265282, qty1/7000, Архив. Stock98→99, prepay3000→10000 (+7000), qarz0. 19.09 businessdate bilan post bo‘ldi;20.09 futureguard rad etdi | PASS — Return287770733 Archive source287769073 qty1/7000 current20.09; reopened view confirmed. UZSstock98→99, prepay3000→10000; debt0. [dalil1](outputs/online-regression-20260920/order-lifecycle/ret-partial-view.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/ret-partial-ledger.png) |
| RET-02 | Full/remaining return, qoldiq va hisob-kitob deltalari | PASS — oldingi return haqidagi tasdiqdan keyin Частичный возврат o‘chiq rejim qolgan1donani oldi;265302:1dona/7000, Архив. Ikkala returndan so‘ng stock98→100, prepay3000→17000; takroriy qayta ochish tasdiqladi | PASS — Remaining return287770765 Archive qty1/7000 after priorreturn confirmation and partialOFF; source287769073 fullyreturned2. UZSstock100/reserved0,prepay17000/debt0. [dalil1](outputs/online-regression-20260920/order-lifecycle/ret-remaining-view.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/ret-remaining-ledger.png) |
| RET-03 | Return miqdori/zero/over-return validatsiyasi, UI imkoniyatiga mos | PASS — original2dan qty3 pickerda rad etildi. To‘liq qaytgach uchinchi forma0pozitsiya; H02-ANOR311-002 Nextni blokladi, hujjat saqlanmadi | PASS — Source2 units: pickerqty3 rejected (emptyinput). After1+1archivedreturns source exhausted0positions; NextblockedH02-ANOR311-002, no3rdreturncreated. UI check, notdirectbackendoverreturn. [dalil1](outputs/online-regression-20260920/order-lifecycle/ret-over-return-picker.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/ret-exhausted-blocked.png) |
| USD-01 | USD mahsulot/narx bilan order Save/reopen | PASS — order265297: qty2×$1=$2, USD valyuta saved viewda tasdiqlandi | PASS — Saved/reopened USD order 287769071:2units×$1=$2, current20.09 order/delivery, client903410. [dalil1](outputs/online-regression-20260920/usd-forms/usd01-saved-view.png) |
| USD-02 | USD miqdor/chegirma edit va saqlangan summa | PASS —265297 qty2→3 ($3).265301 qty5×$1−10%=$4.50 → qty3edit $2.70; hardreload tasdiqladi | PASS — Main287769071 qty2→3 savedUSD3. Discount287769095 qty5×1−10%=4.50 saved/reopened; editqty3 retains−10%, saved2.70 confirmedhardreload. [dalil1](outputs/online-regression-20260920/usd-forms/usd02-qtyedit-view.png), [dalil2](outputs/online-regression-20260920/usd-forms/usd02-discount45-view.png) |
| USD-03 | USD lifecycle/archive va valyutadagi qarz | PASS — 265297 Draft→New→Archive; USD qarz3, oldindan0, balans−3 | PASS — Order 287769071 Draft→New→Archive current20.09, debtUSD3/prepay0/balance−3; exactID in debt details. [dalil1](outputs/online-regression-20260920/usd-forms/usd03-debt.png), [dalil2](outputs/online-regression-20260920/usd-forms/usd03-id-debt.png) |
| USD-04 | USD to‘lov/offset va yakuniy balans | PASS — qarz3; to‘lov1+offset→qarz2; to‘lov2.50+offset→qarz0/prepay0.50. Offset19.09 sanada o‘tdi,20.09 default futureguard bilan rad etildi | PASS — Order287769071 debt3; payment109260288 USD1+offset→debt2; payment109260289 USD2.50+offset→debt0/prepay0.50. Bothposted/reopened; current20.09offsetUSDrowonly. [dalil1](outputs/online-regression-20260920/usd-forms/usd04-pay1-view.png), [dalil2](outputs/online-regression-20260920/usd-forms/usd04-pay2-view.png) |

Tafsilot/dalillar: qo‘lda chegirmalar va aksiya lifecycle (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-discount/results.md`), 5aksiya va kombinatsiyalar (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-actions/results.md`), qisman/to‘liq return (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-return/findings.md`), USD va to‘lov/offset (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-usd/findings.md`).

Saqlangan testga tayyorgarlik: existing `Возврат` narx turi PRCT:3 faqat testroom14650ga ulandi; `deep-discount10-pw949382` foiz10 preset yaratilib testfilial va shu roomga ulandi. Dastlabki dropdown bo‘shligi biznes xatosi deb baholanmadi. Company/global sozlamalar yoki mavjud aksiya qoidalari o‘zgartirilmagan.

**D1 — sana validatsiyasi nomuvofiqligi qayta takrorlandi:** 20.09.2026 00:xx Asia/Tashkent vaqtida joriy sana ayrim tranzaksiyalarda A02-02-039 (kelajak sana) bilan rad etildi. Yangi return265317da faqat `delivery_date`20→19 o‘zgartirilganda Archive o‘tdi; `deal_time=20.09.2026 00:01:00` o‘zgarmadi. Demak, return bo‘yicha oldingi umumiy “20.09 hujjat sanasi rad etiladi” talqini **yetkazib berish/tranzaksiya sanasi**ga toraytirildi. Serverning `offset_list:model` javobi ham default20.09 bergan. HTTP Date GMTda bo‘lishi timezone xatosini o‘zi isbotlamaydi; ichki sabab hali aniqlanmagan. Return qayta tekshiruvi (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-return/findings.md`), oldingi server sanalari (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-analysis/previous-network-dates.json`).

## H. D1 qayta tekshiruvi — 2026-09-20

Yangi mustaqil Playwright sessiyalari, haqiqiy Asia/Tashkent vaqti; browser/server soati yoki global sozlamalar o‘zgartirilmagan. Order va returnning sanalari Save payload va qayta ochilgan view bilan tasdiqlandi.

| ID | Case | Xtrade qayta tekshiruv | smartup.online |
|---|---|---|---|
| DATE-01 | Yangi1dona/7000UZS orderni joriy sana bilan to‘g‘ridan-to‘g‘ri Archive saqlash | **OBSERVED — D1, aniqlashtiriladi** — deal20.09 00:01 + delivery20.09 HTTP400/A02-02-039; ikkala sana19.09 nazoratida265316 Archive yaratildi | PASS — Order287770779 qty1/7000directArchive with deal20.09 00:01 and delivery20.09. SaveHTTP200/viewArchive at07:29local; nofutureguard. Doesnotcovermidnightserverwindow. [dalil1](outputs/online-regression-20260920/order-lifecycle/date01-final.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/date01-archive-view.png) |
| DATE-02 | Return draftini deal20.09 00:01 + delivery20.09 bilan Save/reopen | PASS —265317 hujjati aynan shu sanalarda Черновик saqlandi | PASS — Return287770782 source287770779 Draft saved/reopened deal20.09 00:01:00/delivery20.09 qty1/7000. [dalil1](outputs/online-regression-20260920/order-lifecycle/date02-draft-final.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/date02-draft-view.png) |
| DATE-03 | Shu return Archive; keyin faqat delivery20→19 o‘zgartirish | **OBSERVED — D1, aniqlashtiriladi** — delivery20 Archive HTTP400/A02-02-039. Deal20 o‘zgarmagan holda delivery19 Archive HTTP200; qayta ochilgan view tasdiqladi | PASS — Return287770782 currentdelivery20.09 archivedviaactualstatuschange; deal20.09 00:01:00 retained, reload/viewArchive. D1 not reproduced at07:34; delivery19 fallbackunneeded,midnightwindowuncovered. [dalil1](outputs/online-regression-20260920/order-lifecycle/date03-archive-view.png), [dalil2](outputs/online-regression-20260920/order-lifecycle/network.jsonl) |
| DATE-04 | Mavjud USD265301 draftini Новый qilish; faqat delivery sanasini almashtirib qaytarish | **OBSERVED — D1, aniqlashtiriladi** — delivery20 bilan server HTTP200 ichida success_count0/errors_count1/A02-02-039; draft qoldi. Deal20 o‘zgarmagan holda delivery19 bilan Новый va Архив o‘tdi; qarz2.70USD hosil bo‘ldi | PASS — Current20.09 delivery New+Archive passed at07:05Asia/Tashkent. Past-delivery retry unnecessary; midnight D1 window not reproduced, no fixed claim. [dalil1](outputs/online-regression-20260920/usd-forms/date04-current-new.png), [dalil2](outputs/online-regression-20260920/usd-forms/date-network.json) |
| DATE-05 | USD qarz0/prepay0.50 holatida offset20 va offset19 | OBSERVED — ikkala so‘rovHTTP200, qoldiqlar o‘zgarmadi. Hisoblanadigan qarz bo‘lmagani uchun bu natija D1 yo‘qligini isbotlamaydi | OBSERVED — USDdebt0/prepay0.50: offsets20.09 and19.09 bothHTTP200/nochange. No-op only, not successful substantive finance and not D1 fix proof. [dalil1](outputs/online-regression-20260920/usd-forms/date05-no-debt-controls.png), [dalil2](outputs/online-regression-20260920/usd-forms/date-network.json) |
| DATE-06 | Haqiqiy USD qarz2.70/prepay0.50 holatida offset20; faqat offset sanasini19ga almashtirish | **OBSERVED — D1, aniqlashtiriladi** —20.09 HTTP400/A02-02-039; aynan shu client/currency/flaglar bilan19.09 HTTP200,0.50USD qo‘llandi: qarz2.20/prepay0. Serverning fresh modeli default20.09 beradi | PASS — At20.09 07:09Asia/Tashkent serverdefault/UI/transmitted20.09 offsetHTTP200 appliedUSD0.50: debt2.70→2.20/prepay0.50→0. Sameconditionsaspriorcaseexcepthost/timewindow; midnightD1fix NOTconfirmed. Pastretrynotneededaftercurrent success. [dalil1](outputs/online-regression-20260920/usd-forms/date06-real-before.png), [dalil2](outputs/online-regression-20260920/usd-forms/date06-real-after.png) |

Return dalillari: rad etilgan holat (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-return/11-return20-archive-result.png`), faqat delivery19 bilan muvaffaqiyatli view (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-return/14-return-final-reopened.png`), aniq request/response sanalari (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-return/date-evidence.json`), trace (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-return/trace.zip`).

USD dalillari: haqiqiy qarzda20.09 rad etildi (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/11-real-offset20-result.png`), 19.09 nazorat natijasi (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/12-real-offset19-result.png`), offset request/response (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/offset-network.json`), server default sanasi (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/server-model-default.json`), USD qayta tekshiruv hisoboti (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/findings.md`).

**Xulosa:** joriy mahalliy sana20.09ni server ham modelda beradi, lekin order/return delivery20 va haqiqiy offset20 tranzaksiyalari “kelajak sana” deb bloklanadi. Draft Save ishlaydi. Order/return deal_time20 saqlangan holda delivery19 o‘tishi, offsetda esa faqat offset_date19 o‘tishi ajratildi. Backend business-date/vaqt zonasi yoki tekshiruv implementatsiyasidagi aniq sabab tekshirilmagan. smartup.online retestda server modeli defaulti, browser timezone, yuborilgan sanalar, haqiqiy qarz va statusdan keyingi qoldiqlarni birga yozish kerak.

### D1ni qo‘lda takrorlash — oxirgi baseline bilan

Oxirgi tekshiruvdan keyin `natural_client-pw949382` mijozida USD qarz2.20, prepay0 qoldi. Avvalgi0.50 allaqachon hisobga olingan, shuning uchun shu holatda offsetni qayta bosish yetarli emas. Quyidagi tayyorgarlik yangi0.50 test to‘lovini yaratadi; bu qo‘lda bajarish yo‘riqnomasi, agent tomonidan yangi to‘lov bajarilmadi.

1. Xtradega kiring va `filial-pw949382` filialini tanlang.
2. `Финансы → Оплаты от клиентов → Создать`ni oching. Клиент=`natural_client-pw949382`, Валюта=`Доллар США`, Сумма=`0.50`, Тип оплаты=`Наличные деньги`, Касса=`Основная касса`, Дата и время=`19.09.2026 19:00`. `Провести взаимозачёт` belgisi o‘chiq bo‘lsin. `Провести`ni bosib tasdiqlang.
3. `Продажа → Взаиморасчеты с клиентами`ga o‘ting. Shu mijozning USD qatorini toping. Oxirgi baseline o‘zgarmagan bo‘lsa, Задолженность=2.20 va Предоплата=0.50 bo‘lishi kerak. Haqiqiy qarz va prepay ikkalasi ham musbat bo‘lishi shart.
4. Aynan shu USD qatorining chapdagi checkboxini belgilang. Tanlangan qator1ta bo‘lsin. `Взаиморасчет`ni bosing.
5. `Дата взаиморасчета`ga joriy20.09.2026 sanasini qo‘ying. To‘rtta option (`с учетом консигнации`, `по проекту`, `по договору`, `по типу оплаты`) tekshiruvdagidek yoqilgan holda `Подтвердить`ni bosing.
6. Xato takrorlansa: `A02-02-039`, kelajak sana bilan tranzaksiya taqiqlangani haqidagi xabar chiqadi; qarz2.20/prepay0.50 o‘zgarmaydi.
7. Xabarni yoping, shu USD qatori uchun `Взаиморасчет`ni qayta oching. Faqat `Дата взаиморасчета`ni19.09.2026ga o‘zgartiring va `Подтвердить`ni bosing.
8. Nazorat natijasi:0.50 hisobga olinadi; boshlang‘ich qarz2.20 bo‘lganida yakuniy qarz1.70, prepay0 bo‘ladi.

Vaqt sharti: aniq tasdiqlangan failure20.09.2026 00:28 Asia/Tashkentda kuzatilgan. Ushbu yo‘riqnomadagi20.09 tekshiruv paytidagi joriy sana. Boshqa vaqt/sanada xato qaytishi hali isbotlanmagan; qurilma soatini o‘zgartirmasdan real sana-vaqtni qayd eting. 20.09 operatsiyasi muvaffaqiyatli o‘tsa, qarz/prepay o‘zgarganini tekshirib shu natijani yozing; prepay tugagan holatda19.09 nazorati mazmunli bo‘lmaydi.

## Bug reyestri

Prioritetlar ushbu tekshiruv bahosi; mahsulot egasi tomonidan yakuniy triage qilinmagan.

| ID | Daraja | Muammo va qayta bajarish | Dalil | Xtrade / smartup.online retest |
|---|---|---|---|---|
| F1 | Yopildi: saqlash xatosi tasdiqlanmadi | Dastlab import−1 finalga o‘tgani uchun P2 deb baholangan. 23:40 retestda Новый va Черновик Save serverda aniq−1 validatsiyasi bilan bloklandi; yangi order yo‘q. Oldingi P2 bahosi bekor qilindi | Save xatosi (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/negative-save-retest/03-new-rejected-alert.png`), server javoblari (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/negative-save-retest/save-responses.json`) | Server validatsiyasi PASS / PASS — Online903410da New va Draft Save ham rad etildi; manfiy order yaratilmagan |
| F2 | P2 | IMP-08: bir mahsulot2 qator → ТМЦ SKU2, saved view SKU1. Kutiladi: ikkala joyda SKU1 | Wizard (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/import-order-total.png`), view (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/import-saved-view.png`) | Tasdiqlangan / FAIL — Online287769065 wizardSKU2, final/viewSKU1; [Online dalil](outputs/online-regression-20260920/import-reports/IMP-01-wizard.png) |
| F3 | P3 | RPT-01 ni qayta ochish: client headerda `<br>` literal. Excel eksportida newline to‘g‘ri | Screenshot (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-reports/08-literal-br-header.png`) | Qayta takrorlandi / FAIL — HTML literal`<br>`; XLSX newline to‘g‘ri; [Online dalil](outputs/online-regression-20260920/import-reports/RPT-01-order-sheet.png) |
| F4 | P3 | RPT-05 ni qayta ochish: `UI-ANOR1405:product alternative name` tarjimasiz | Screenshot (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-reports/09-untranslated-header.png`) | Qayta takrorlandi / PASS — Online’da tarjima bor, oldingi kalit takrorlanmadi; [Online dalil](outputs/online-regression-20260920/import-reports/RPT-05-ttn.png) |
| F5 | P3 | Order settings labelida status Черновик, izohida >90 kunlik Черновик → Отменено. Backend avtomatik o‘tishi tekshirilmagan | Screenshot (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-forms/order-settings.png`) | Tasdiqlangan / FAIL — Черновик sarlavhasi va Отменено izohi ziddiyati takrorlandi; [Online dalil](outputs/online-regression-20260920/usd-forms/frm01-settings-903410.png) |
| F6 | P3 | Retail create authorization qismida `subfilial` tarjimasiz ko‘rinadi | Screenshot (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-forms/retail-create-repro.png`) | Qayta takrorlandi / PASS — Online retail ikki ochishda Проект tarjimasi bor; [Online dalil](outputs/online-regression-20260920/usd-forms/frm02-retail-second.png) |
| F7 | P2 — dastlabki baho | ORD-03: order sanasini Ctrl/Cmd+A → Backspace bilan bo‘shatish {} so‘rov/HTTP500/Hashmap:deal_time not found chiqaradi; Save shart emas. To‘liq sana va datepicker nazoratlari o‘tdi | [Qo‘lda takrorlash](outputs/online-regression-20260920/date-input-recheck/findings.md), [screenshot](outputs/online-regression-20260920/date-input-recheck/04-manual-clear-alert.png) | Xtrade uchun alohida tasdiq yo‘q / Online mustaqil qayta takrorlandi |
| D1 | Dev bilan aniqlashtiriladi; oldingi P2 dastlabki baho | DATE-01/03/04/06:20.09 mahalliy joriy sana bilan order/return delivery va haqiqiy USD offset A02-02-039 bilan bloklanadi. Return va USDorderda faqat delivery19, offsetda faqat offset_date19 nazorati o‘tdi. Xatti-harakat tasdiqlangan; biznes sana/vaqt zonasi qoidasi va “bug yoki kutilgan holat” tasnifi ochiq | Return request/response (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-return/date-evidence.json`), USD request/response (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/offset-network.json`) | Xtrade00:22–00:29da takrorlangan / Online07:05–07:34da joriy sana bilan order/return va haqiqiy offset o‘tdi. Yarim tun oynasi tekshirilmagan; tuzaldi deb yopilmaydi. [Online sanalar](outputs/online-regression-20260920/usd-forms/date-network.json) |

Qo‘shimcha diagnostika: logindan keyin bir marta `Cannot read properties of undefined (reading 'sort')`, `trade/plugin.js:89` qayd etilgan. Bu retail ochilishidan oldin sodir bo‘lgan; retailga bog‘lanmaydi, ko‘rinadigan oqimni bloklamadi. UI tour JSON uchun 404lar qayd etilgan. Qoldiq negative-testidagi HTTP400 kutilgan server validatsiyasi.

## Qolgan qamrov

- Katta hajmli import va boshqa Excel format/mapping kombinatsiyalari. F1 uchun Новый/Черновик server Save validatsiyasi tekshirildi va o‘tdi.
- Retail checkout/save va request to‘liq lifecycle; permissionlar va chuqur filterlar.
- Return multi-product/VAT/serial-number, USD return, posted returnni bekor qilish, naqd refund; full return shu safar qisman qaytarishdan keyingi barcha qolgan miqdor sifatida bajarilgan.
- USDdan boshqa valyutalar, FXkurs o‘zgarishi, soliq stavkalari, konsignatsiya. Aksiya New→Canceled o‘tdi; aksiya bilan Shipped/Delivered/Archive va aksiya bonusining returni qamrab olinmagan.
- D1 current-date/serverbusinessdate nomuvofiqligining sababi va konfiguratsiyasi aniqlanmagan.
- Qolgan15 bosma hisobot varianti, custom/OnlyOffice template, boshqa statuslar va fizik print.
- Barcha qolgan Smartup formalarining to‘liq regressioni. `order_beta` bu ro‘yxatga kirmaydi, chiqarilgan.

## Online yakuniy natija va qayta foydalanish — 2026-09-20

**88/88: 81 PASS, 4 FAIL, 3 OBSERVED.** Ochiq topilmalar: F2 SKU hisoblagichi, F3 HTMLdagi literal `<br>`, F5 sozlama matnlari ziddiyati, F7 sana maydonini tozalashdagi HTTP500. F4 va F6 bu Online run’da takrorlanmadi. D1 ertalab takrorlanmadi, yarim tun sharti ochiq qoladi. [Devga sodda takrorlash qadamlari](outputs/online-regression-20260920/bug-repro.md).

Setup `./.venv/bin/python scripts/run_tests.py setup`: **28passed,1skipped,1deselected,0failed**,574.26soniya. Skip — Online’da qo‘llanmaydigan licensepurchase; yangi userga mavjud license biriktirildi. Filial21336790, room238703, client21336794, product5425318. [Baseline](outputs/online-regression-20260920/setup/baseline.json), [setup summary](outputs/online-regression-20260920/setup/system-summary.json).

| Hujjat | Yakuniy holat |
|---|---|
| 287769073 | Archive14000UZS,2dona; ikkalasi qaytarilgan |
| 287769065 | Draft35000UZS,2+3dona; naqd; import/report uchun |
| 287769076 | Draft31500UZS,5dona,order10%chegirma; Терминал |
| 287769625 | Canceled21000UZS,3dona |
| 287770806 | Canceled56700UZS,10pullik+1bonus,aksiya10%+order10%;11rezerv to‘liq bo‘shagan |
| 287769071 / 287769095 | Archive3USD to‘liq to‘langan / Archive2.70USD,2.20qarz qolgan |
| 287770779 | Archive7000UZS,1dona; sana testi, to‘liq qaytarilgan |
| 287770733 / 287770765 | Archive7000UZSdan partial1+remaining1; source287769073 |
| 287770782 | Archive7000UZS,1dona; source287770779; draft→archive sana testi |
| To‘lov109260290 /109260291 | Posted7000UZS /10000UZS |
| To‘lov109260288 /109260289 | Posted1USD /2.50USD |

Yakuniy **UZS qarz7000, prepay24000, faolorder0, balans17000; stock100/reserved0/available100**. Sana testidagi yangi arxiv qarzi va qaytarish krediti avtomatik offset qilinmagan. **USD qarz2.20, prepay0, balans−2.20; stock94/reserved0/available94**. Test ma’lumotlari qayta tekshiruv uchun saqlandi; boshlang‘ich fresh100/zeroledger shartlari uchun yangi setup kerak. [Yakuniy JSON](outputs/online-regression-20260920/final-state.json).

Yangi testroomga10%discount preset va mavjud Возврат narx turi biriktirildi. Global sana/soat o‘zgartirilmadi. `.env` Online/NEW_CODE=1 holatida qoldi; uni o‘zgartirish bu ishga kiritilmadi. `data_store`dagi eski group/mobile IDlarini903410freshsetup sifatida ishlatmaslik.

[Jonli case natijalari](outputs/online-regression-20260920/case-results.json), [order/moliya/return](outputs/online-regression-20260920/order-lifecycle/findings.md), [import/report](outputs/online-regression-20260920/import-reports/findings.md), [discount/action](outputs/online-regression-20260920/discount-actions/findings.md), [USD/formalar](outputs/online-regression-20260920/usd-forms/findings.md), [F7 mustaqil recheck](outputs/online-regression-20260920/date-input-recheck/findings.md). [Online Excel shablon](outputs/online-regression-20260920/import-reports/valid.xlsx).

Dalillar keyingi test-run cleanupidan saqlash uchun `outputs/online-regression-20260920`ga ko‘chirildi. Auditda41noyob tarixiy Xtrade dalil fayli diskda topilmadi; matndagi tarixiy natijalar saqlandi, yo‘q dalillar ochiq belgilandi. Online dalillari mavjud. [Tarixiy yo‘q fayllar](outputs/online-regression-20260920/historical-missing-links.json), [fayl manifesti](outputs/online-regression-20260920/manifest.json). Trace’lar ichki test artefaktlari, ommaviy joyga yuborilmagan.

Ushbu run yangi reusable pytest testlari yozildi degani emas. Autotestga o‘tkazish uchun yuqoridagi88ID, precondition va aniq UI/server/delta assertionlar saqlandi. D1 bo‘yicha biznes sana qoidasi hali aniqlashtiriladi.

## Xtrade birinchi bosqich baseline — 2026-09-19 23:40

- Test suffix: 949382; filial `filial-pw949382`, client `natural_client-pw949382`, mahsulot `product-pw949382`, mahsulot kodi `c_p_pw949382`.
- 265282: arxiv, 2 dona / 14 000. 265283: draft, 5 dona / 35 000. 265284: bekor qilingan, 3 dona / 21 000.
- To‘lovlar7 000 va10 000; yakuniy qarz0, oldindan3 000; mavjud mahsulot qoldig‘i98.
- Local `.env` Xtrade URL va NEW_CODE=0 bilan qoldirildi. Setup data aynan Xtrade baselinega tegishli.
- Import tafsilotlari (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-import/results.md`), hisobotlar (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-reports/findings.md`), formalar (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-forms/findings.md`).
- Root trace (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/order-regression-trace.zip`), import trace (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-import/trace.zip`), report trace (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-reports/reports-trace.zip`), forma trace (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/parallel-forms/trace.zip`).
- Ketma-ket tekshiruv jurnali (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/checks.json`): oraliq PARTIAL/OBSERVED yozuvlar keyingi natijalar bilan aniqlashtirilgan; bu fayl qatorlari alohida yakuniy testcase soni emas.

## Kengaytirilgan tekshiruvdan keyingi holat — 2026-09-20 00:15

| Hujjat | Yakuniy holat |
|---|---|
|265282|Oldingi arxivlangan14000 order; endi to‘liq2dona qaytarilgan|
|265283|Avvalgi import draft35000, o‘zgartirilmagan|
|265297|USDorder3, Архив; qarzi to‘liq yopilgan|
|265298|Qo‘lda order10% chegirma: qty5,31500UZS, Терминал, Черновик; hardreload tasdiqlangan|
|265299|10paid+1bonus, promo10%+order10%,56700UZS; Новый→Отменен, rezerv/balans ta’siri qaytarilgan|
|265300|Partialreturn1/7000, Архив|
|265301|USD10%discount draft:qty3,total2.70; hardreload tasdiqlangan|
|265302|Fullremainingreturn1/7000, Архив|
|45361 /45362|USDpayments1 va2.50, o‘tkazilgan; USDoffset bajarilgan|

Yakuniy UZS mahsulot onhand100, reserved1, available99. Client UZS qarz0, oldindan17000, boshqa mavjud faolorder7000, balans10000. USD qarz0, oldindan/balans0.50. 7000lik boshqa faolorder bu bosqichda o‘zgartirilmadi; qayd etilgan deltalarga aralashmadi.

Tracelar: manual+promo lifecycle (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-discount/trace.zip`), aksiya (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-actions/trace.zip`), aksiya kombinatsiya (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-actions/combo-trace.zip`), return (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-return/trace.zip`), USD (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/deep-usd/deep-usd-trace.zip`).

## D1 qayta tekshiruvidan keyingi holat — 2026-09-20 00:30

Bu yangi holat yuqoridagi00:15 snapshotni almashtiradi; oldingi snapshot tarix sifatida saqlandi.

- **265301:** oldingi2.70USD draft endi Архив; order vaqti20.09 00:08 o‘zgarmagan, delivery19.09. Qolgan qarz2.20USD. Yangi USDorder yaratilmagan.
- **265316:** yangi1dona/7000UZS test source,19.09 sanada Архив; to‘liq qaytarildi.
- **265317:** shu1dona/7000UZS return, Архив; deal_time20.09 00:01, delivery19.09.
- **UZS:** stock100/reserved1/available99 va sof balans10000 tiklandi. Gross qarz0→7000, prepay17000→24000; alohida settlement bajarilmadi. Boshqa mavjud faolorder7000 o‘zgarmadi.
- **USD:** qarz2.20, prepay0, balans−2.20;19.09 offset mavjud0.50ni yangi arxivlangan265301 qarziga qo‘lladi. Bu retest hujjati saqlab qoldirildi.
- Oldingi import265283 va posted return265300/265302 o‘zgartirilmadi. Company sozlamalari va real soat o‘zgartirilmagan.

Dalillar: return yakuniy holati (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-return/findings.md`), USD yakuniy holati (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/findings.md`), USD trace (tarixiy dalil hozir diskda yo‘q: `test-results/order-regression/date-retest-usd/date-retest-trace.zip`).

## smartup.online run jurnali — 2026-09-20

-06:38preflight: `.env` targetsmartup.online, existingcompany, NEW_CODE1; eski data_storecode432477. Fresh testuser login serverda “Нет лицензии для входа в систему! Пользователь не прикреплен ни к одному филиалу или проекту” bilan to‘sildi. Shu preflightda order/payment yaratilmagan; businesscaseFAIL deb baholanmagan.
-06:42foydalanuvchining yangi ko‘rsatmasi: avvalsetupni qayta run qilish, so‘ng aynan yangi ma’lumotlardan regressionda foydalanish. `./.venv/bin/python scripts/run_tests.py setup` boshlandi;29selected,1deselected. Eski432477baseline retest uchun ishlatilmaydi.
-Online dalillar `outputs/online-regression-20260920/` ostida yig‘iladi. Har qatordagi onlineNOTRUN faqat bajarilgan case dalili tekshirilgandan keyin o‘zgartiriladi. Userning oldingi keng run summarysi ushbu88case bajarilgani deb hisoblanmaydi.

## Yangilanishlar

| Vaqt | Yangilanish |
|---|---|
| 2026-09-19 23:14 | Bajarilgan Xtrade caselar, 6 topilma, Excel shablon va smartup.online retest ustunlari jamlandi; order_beta chiqarildi |
| 2026-09-19 23:40 | F1 real Save bilan qayta tekshirildi: Новый va Черновик serverda rad etildi; list reload yangi order yo‘qligini tasdiqladi. IMP-07 PASS; F1 saqlash xatosi sifatida yopildi, 5 ochiq topilma qoldi |
| 2026-09-20 00:15 | Qo‘lda foiz/summa va kombinatsiya chegirmalari; barcha5aksiya Save/reopen; aksiya+bonus+orderdiscount; promoNew/cancel rezerv; partial+fullremaining returnArchive; USDorder/discount/payment/offset bajarildi. D1 sana masalasi qayd etildi. Oldingi qamrov cheklovlari yangilandi |
| 2026-09-20 00:30 | D1 ikki yangi sessiyada qayta takrorlandi. DATE-01–06 qo‘shildi; return/orderda faqat delivery20→19, haqiqiy USD offsetda offset_date20→19 nazorati bajarildi. DraftSave ishlashi va qarzsiz offsetning bo‘sh200 javobi ajratildi. D1 reyestrga P2 sifatida kiritildi; root cause ochiq |
| 2026-09-20 00:50 | 88 ta case ID va dalil havolalari tekshirildi; yo‘nalishlar inventari, smartup.online precondition/tartibi va autotestga ajratish izohlari qo‘shildi. D1ning eski P2/FAIL bahosi dev bilan aniqlashtiriladigan OBSERVEDga o‘zgartirildi; haqiqiy natijalar saqlandi. Yangi live test yoki autotest yozilmadi |

| 2026-09-20 06:52 | Online903410setup28passed,1skipped,1deselected,0failed;574.26s. Freshbaseline bilan4parallelbrauzer regressiyasi boshlandi |
| 2026-09-20 07:49 | 88/88yakunlandi:81PASS,4FAIL,3OBSERVED. F7mustaqil manualretestbilan tasdiqlandi. Aksiya11reservcancelda bo‘shadi; hujjatlar/dalillaroutputsda saqlandi |

Keyingi run yakunida: muhit/build/vaqtni qayd etish; bajarilgan case natijasini real dalil bilan yangilash; FAIL uchun bug ID, screenshot va trace qo‘shish; tekshirilmagan case NOT RUN qolishi; oldingi natijalarni o‘chirmasdan yangi sanali ustun yoki run bo‘limi qo‘shish.
