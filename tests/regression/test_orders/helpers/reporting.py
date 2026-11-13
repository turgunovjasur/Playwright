"""Order Allure taqdimoti: natija va dalillarni o'zgartirmay tushunarli ko'rsatish.

Faqat positive Order runnerlariga tegishli. API, smoke va shared kod o'zgarmaydi.
Raw JSON birinchi tahrirdan oldin alohida zaxiralanadi. Faqat taqdimot maydonlari
va attachment havolalari o'zgaradi; status, vaqt, UUID va biznes qadamlar saqlanadi.
"""
import allure
import argparse
import ast
from functools import lru_cache
from collections import Counter, defaultdict
from copy import deepcopy
from html import escape
import json
import shutil
import re
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from utils.report_safety import safe_payload, safe_text

VERSION = "order-qa-report-v2"
PREFIX = ("tests.regression.test_orders.runners.", "tests.regression.test_orders.verification.")
SPECS = {
    ("promotions", "test_00_prepare_promotions"): (
        "Bonus ma’lumotlarini tayyorlash · OB-00", "Tayyorlov",
        "Order testlari uchun sotuv narxi va boshqa mahsulotdan bonusni tayyorlash.",
        "Narx 7 000 so‘m; 10 dona mahsulotga 1 dona boshqa mahsulot bonusi. Chegirma keyingi alohida tayyorlovda yaratiladi."),
    ("promotions", "test_01_quantity_discount"): (
        "10% skidkali order: saqlash va qayta ochish · OB-01", "Biznes testi",
        "Chegirma hisoblanishi va order qayta ochilganda saqlanishini tekshirish.",
        "10 × 7 000 = 70 000; chegirma 7 000; jami 63 000 so‘m. Bonus tanlanmaydi."),
    ("promotions", "test_02_other_product_bonus"): (
        "10 dona mahsulotga 1 dona bepul bonus · OB-02", "Biznes testi",
        "Boshqa mahsulot bonusi bepul berilishi va saqlanishini tekshirish.",
        "Asosiy mahsulot 10 × 7 000 = 70 000 so‘m; boshqa mahsulotdan 1 dona bonus, bonus narxi va summasi 0."),
    ("promotions", "test_03_bonus_and_discount"): (
        "Bitta orderda bonus va 10% skidka · OB-03", "Biznes testi",
        "Bonus va chegirma birga ishlashi, saqlash va qayta ochish natijalarini tekshirish.",
        "10 × 7 000 − 7 000 = 63 000 so‘m; boshqa mahsulotdan 1 dona bepul bonus."),
    ("payments", "test_00_prepare_promotions"): (
        "To‘lov testlari uchun bonus · OP-00", "Tayyorlov",
        "To‘lov guruhi uchun alohida bonus yaratish va saqlangan shartini tekshirish.",
        "10 dona mahsulotga 1 dona boshqa mahsulot bonusi; narx 7 000. Chegirma keyingi alohida tayyorlovda yaratiladi."),
    ("payments", "test_01_prepare_ordinary_client"): (
        "Oddiy to‘lov uchun alohida klient · OP-01", "Tayyorlov",
        "Klient yaratish, qayta o‘qish va mavjud xonaga bog‘lash.",
        "Yangi klient aktiv; xonaga biriktirilgan; oldingi xona bog‘lanishlari saqlangan."),
    ("payments", "test_02_prepare_promoted_client"): (
        "Aksiyali to‘lov uchun alohida klient · OP-02", "Tayyorlov",
        "Aksiyali order uchun boshqa alohida klient yaratish va xonaga bog‘lash.",
        "Yangi klient aktiv; xonaga biriktirilgan; oldingi xona bog‘lanishlari saqlangan."),
    ("payments", "test_03_partial_full_payment"): (
        "Oddiy order: jo‘natish → qisman → to‘liq to‘lov · ORD-BIZ-01", "Biznes testi",
        "Orderni bevosita Черновик → Архив o‘tkazish va kirimdan ikki bosqichda qarzini yopish.",
        "2 × 7 000 = 14 000 so‘m; bitta kirim 14 000. 6 000 ajratilgach qarz va predoplata 8 000; yana 8 000 ajratilgach ikkalasi 0."),
    ("payments", "test_04_promoted_order_payment"): (
        "Bonus + skidkali order: jo‘natish → qisman → to‘liq to‘lov · ORD-BIZ-04", "Biznes testi",
        "Bonus va 10% skidkali orderni bevosita Черновик → Архив o‘tkazish va to‘lash.",
        "Order 63 000 so‘m va 1 dona bepul bonus; bitta kirim 63 000. 25 000 ajratilgach qarz va predoplata 38 000; yana 38 000 ajratilgach ikkalasi 0."),
}


SPECS.update({
    ("statuses", "test_00_prepare_client"): (
        "Statuslar uchun alohida klient · OS-00", "Tayyorlov",
        "Boshqa testlardan ajratilgan klientni yaratib ish zonasiga biriktirish.",
        "Klient faol, saved ID va xona bog‘lanishi mos; oldingi bog‘lanishlar saqlanadi."),
    ("statuses", "test_01_status_cycle"): (
        "Bitta orderda olti status o‘tishi · OS-01", "Biznes testi",
        "Qoralama → Новый → В обработке → В ожидании → Отгружен → Доставлен → Архив.",
        "Har status saqlanadi. 2 dona rezerv bir marta olinadi; jo‘natishda fizik qoldiq 2 dona kamayadi. Arxivda aynan shu order qarzi 14 000 so‘m."),
})

GROUP_FEATURES = {
    "statuses": "SCN-001 · Order statuslari",
    "promotions": "SCN-002 · Order aksiyalari va chegirmalari",
    "payments": "SCN-003 · Order to‘lovlari",
    "mandatory": "SCN-004 · Majburiy aksiyalar",
    "stock": "SCN-005 · Order ombor rezervi",
    "bonus_limit": "SCN-006 · Ikki klient uchun umumiy bonus limiti",
    "returns": "SCN-007 · Bonus va chegirmali orderni qaytarish",
    "multi_payments": "SCN-008 · Bir klientning bir nechta orderini to‘lash",
    "manual_discounts": "SCN-009 · Tayyor va qo‘lda chegirma",
    "product_limit": "SCN-010 · Ikki order uchun kunlik TMZ limiti",
    "two_warehouses": "SCN-011 · Bitta orderda ikki ombor",
    "mixed_promotions": "SCN-012 · Majburiy va ixtiyoriy aksiyalar birga",
    "auto_offset": "SCN-013 · Kirimda order qarzini avtomatik yopish",
    "prepayment_first": "SCN-014 · Orderdan oldin olingan avans",
    "recovery": "SCN-015 · Retry va dublikatdan himoya",
}
SPECS.update({
    ('returns', 'test_00_prepare_client'): ('Qaytarish uchun alohida klient', 'Tayyorlov', 'Qaytarish testlari uchun yangi klient yaratish va ish zonasiga biriktirish.', 'Klient faol, ish zonasiga biriktirilgan va boshqa klientlarning bog‘lanishlari saqlangan.'),
    ('returns', 'test_01_prepare_promotions'): ('Qaytarish uchun bonus aksiyasini tayyorlash', 'Tayyorlov', '10 dona mahsulot xaridiga boshqa mahsulotdan 1 dona bepul bonus aksiyasini tayyorlash.', 'Bonus saqlangan. 10% chegirma keyingi alohida tayyorlovda yaratiladi.'),
    ('returns', 'test_02_prepare_return_price'): ('Возврат narx turini biriktirish', 'Tayyorlov', 'Qaytarish formasiga kerakli tizim narx turini filial va ish zonasiga ulash.', 'Aynan Возврат narx turi filial va ish zonasiga biriktirilgan. Oldingi narx turlari va bog‘lanishlar saqlanadi.'),
    ('returns', 'test_03a_prepare_stock'): ('Qaytarish uchun ombor qoldig‘ini tayyorlash', 'Tayyorlov', 'Ombordagi erkin qoldiqni tekshirish va yetishmagan qismini alohida kirim bilan to‘ldirish.', 'Kamida 20 dona tovar va 2 dona bonus erkin. Kirimdan keyin qoldiq aynan qo‘shilgan miqdorga oshadi; avvalgi rezerv saqlanadi.'),
    ('returns', 'test_03_prepare_reason'): ('Qaytarish sababini tayyorlash', 'Tayyorlov', 'Test uchun alohida faol qaytarish sababini yaratish.', 'Saqlangan sabab ro‘yxatdan aynan nomi va kodi bilan topiladi.'),
    ('returns', 'test_04_create_promoted_order'): ('63 000 so‘mlik order va 1 dona bepul bonus', 'Biznes testi', 'Har biri 7 000 so‘mdan 10 dona mahsulotga 10% aksiya chegirmasi va 1 dona bepul bonus qo‘shib order saqlash.', 'Order jami 63 000 so‘m. Bonus 1 dona, narxi 0. Saqlangan miqdorlar tekshiriladi va ikkala mahsulotning ombordagi boshlang‘ich qoldig‘i qayd etiladi.'),
    ('returns', 'test_05_ship_order'): ('Order jo‘natilganda ombor va qarz', 'Biznes testi', 'Orderni bevosita Черновик → Архив o‘tkazgandan keyin ombor qoldig‘i hamda klient qarzini tekshirish.', 'Asosiy mahsulot 10 dona, bonus 1 dona kamayadi. Order qarzi 63 000 so‘m. Ombor rezervi boshlang‘ich miqdorga teng.'),
    ('returns', 'test_06_pay_order'): ('Qaytarishdan oldin orderni to‘liq to‘lash', 'Biznes testi', 'Klientdan 63 000 so‘m kirim qilish va shu mablag‘ bilan aynan tekshirilayotgan order qarzini yopish.', 'Order qarzi, ishlatilmagan avans va klient balansi 0. Order va to‘lov IDlari saqlanadi.'),
    ('returns', 'test_07_partial_return'): ('2 dona mahsulot va bonusni qaytarish', 'Biznes testi', 'To‘langan orderdan 2 dona mahsulot va 1 dona bepul bonusni qaytarish; qoralama va arxiv holatlaridagi natijalarni solishtirish.', 'Qoralamada ombor va balans o‘zgarmaydi. Arxivlangach mahsulot 2 dona, bonus 1 dona omborga qaytadi. Klient avansi 12 600 so‘m, order qarzi 0.'),
    ('returns', 'test_08_remaining_return'): ('Qolgan 8 dona mahsulotni qaytarish', 'Biznes testi', 'Shu orderning qolgan 8 dona mahsulotini qaytarish. Oldin qaytarilgan bonus yana qaytarilmasligini tekshirish.', 'Avans yana 50 400 so‘m oshib, jami 63 000 so‘m bo‘ladi. Ikkala mahsulotning ombor qoldig‘i boshlang‘ich miqdorga qaytadi. Order qarzi 0.'),
    ('multi_payments', 'test_00_prepare_client'): ('Ikki order uchun bitta alohida klient', 'Tayyorlov', 'Ikkala order va umumiy to‘lov uchun boshqa testlardan ajratilgan klient yaratish.', 'Yangi klient faol va kerakli ish zonasiga biriktirilgan.'),
    ('multi_payments', 'test_01_first_order'): ('Birinchi orderning qarzi: 14 000 so‘m', 'Biznes testi', 'Balansi 0 bo‘lgan klientga 2 dona mahsulotdan order yaratish, jo‘natish va arxivlash.', 'Aynan birinchi orderning qarzi 14 000 so‘m. Klient avansi 0.'),
    ('multi_payments', 'test_02_second_order'): ('Ikkinchi order: 21 000 so‘m; jami qarz 35 000', 'Biznes testi', 'Shu klientga yana 3 dona mahsulotdan alohida order yaratish, jo‘natish va arxivlash.', 'Orderlarning IDlari turlicha. Birinchi order qarzi 14 000, ikkinchisi 21 000 so‘m. Umumiy qarz 35 000, avans 0.'),
    ('multi_payments', 'test_03_shared_cashin'): ('Ikkala order uchun bitta 40 000 so‘mlik kirim', 'Biznes testi', 'Avtomatik qarz yopishni o‘chirib, klientdan 40 000 so‘m qabul qilish.', 'Ikkala order qarzi o‘zgarmaydi: 14 000 va 21 000 so‘m. Umumiy qarz 35 000, avans 40 000, balans 5 000 so‘m.'),
    ('multi_payments', 'test_04_partial_first'): ('Birinchi orderga 6 000 so‘m qisman to‘lov', 'Biznes testi', 'Umumiy avansdan faqat birinchi orderga 6 000 so‘m ajratish.', 'Birinchi orderning qolgan qarzi 8 000 so‘m bo‘ladi. Ikkinchi order qarzi 21 000 so‘mligicha qoladi. Avans 34 000 so‘m.'),
    ('multi_payments', 'test_05_finish_first'): ('Birinchi orderning qolgan 8 000 so‘mini yopish', 'Biznes testi', 'Avansdan birinchi orderning qolgan 8 000 so‘m qarzini to‘lash.', 'Birinchi order qarzi to‘liq yopiladi. Faqat ikkinchi orderning 21 000 so‘m qarzi qoladi. Avans 26 000 so‘m.'),
    ('multi_payments', 'test_06_finish_second'): ('Ikkinchi order yopiladi; avansda 5 000 so‘m qoladi', 'Biznes testi', 'Avansdan ikkinchi orderning 21 000 so‘m qarzini to‘liq to‘lash.', 'Ikkala order qarzi 0. Ortiqcha 5 000 so‘m klient avansi va balansida saqlanadi.'),
    ('manual_discounts', 'test_00_prepare_client'): ('Chegirma testlari uchun alohida klient', 'Tayyorlov', 'Chegirmali orderlar uchun yangi klient yaratish va ish zonasiga biriktirish.', 'Klient saqlangan va kerakli ish zonasiga biriktirilgan.'),
    ('manual_discounts', 'test_01_prepare_promotions'): ('Qo‘lda chegirma bilan ishlatiladigan bonus', 'Tayyorlov', '10 dona mahsulot xaridiga boshqa mahsulotdan 1 dona bepul bonus beradigan ixtiyoriy aksiyani tayyorlash.', 'Test uchun alohida bonus aksiyasi saqlangan va orderda tanlashga tayyor.'),
    ('manual_discounts', 'test_02_prepare_margin'): ('Tayyor 10% chegirmani tayyorlash va biriktirish', 'Tayyorlov', 'Katalogdagi faol 10% chegirmani ishlatish; mavjud bo‘lmasa yaratish. Uni test filiali hamda ish zonasiga biriktirish.', 'Chegirma 10% qiymat bilan saqlangan va ikkala joyga biriktirilgan. Avvalgi chegirma bog‘lanishlari saqlangan.'),
    ('manual_discounts', 'test_03_preset_discount'): ('Tayyor −10% chegirma: jami 12 600 so‘m', 'Biznes testi', 'Har biri 7 000 so‘mdan 2 dona mahsulot uchun katalogdagi tayyor −10% chegirmani tanlash.', 'Mahsulot chegirmasi 1 400, jami 12 600 so‘m. Orderga qo‘shimcha umumiy chegirma va bonus yo‘q. Saqlash va tahrirga qayta ochishda qiymatlar mos.'),
    ('manual_discounts', 'test_04_line_amount'): ('Har donaga 100 so‘m chegirma: jami 13 800', 'Biznes testi', 'Har biri 7 000 so‘mdan 2 dona mahsulotning har biriga qo‘lda 100 so‘m chegirma berish.', 'Qator chegirmasi 2 × 100 = 200 so‘m, jami 13 800 so‘m. Orderga umumiy chegirma yo‘q. Saqlangach va qayta ochilganda har dona uchun −100 qiymati saqlangan.'),
    ('manual_discounts', 'test_05_order_amount'): ('Butun orderga 200 so‘m chegirma: jami 13 800', 'Biznes testi', '14 000 so‘mlik orderga bir martalik 200 so‘m umumiy chegirma berish.', 'Qator chegirmasi yo‘q. Orderga umumiy chegirma 200 so‘m bo‘lib, mahsulot miqdoriga ko‘paymaydi. Jami 13 800 so‘m; saqlash va qayta ochish natijalari mos.'),
    ('manual_discounts', 'test_06_amounts_with_bonus'): ('Ikki qo‘lda chegirma va bepul bonus: jami 68 800', 'Biznes testi', 'Har biri 7 000 so‘mdan 10 dona mahsulotga har dona uchun 100 so‘m, butun orderga yana 200 so‘m chegirma berish va 1 dona bepul bonus tanlash.', '70 000 − 1 000 − 200 = 68 800 so‘m. Bonus 1 dona, narxi va summasi 0. Ikkala chegirma, jami va bonus tanlovi saqlash hamda qayta ochishda mos.'),
})


for _group, _case, _code in (
    ("promotions", "test_00a_prepare_discount", "OB-00A"),
    ("payments", "test_00a_prepare_discount", "OP-00A"),
    ("returns", "test_01a_prepare_discount", "OR-01A"),
):
    SPECS[(_group, _case)] = (
        f"10 dona mahsulotga 10% chegirma tayyorlash · {_code}", "Tayyorlov",
        "Faqat shu guruh uchun yangi ixtiyoriy A10 → 10% aksiyani yaratish va qayta o‘qish.",
        "Aksiya IDsi, bugundan boshlanadigan muddat, mahsulot, 10 dona sharti va 10% qiymati saqlangan. Umumiy API baseline o‘zgarmaydi.")





SPECS.update({('mandatory', 'test_00_prepare_prices'): ('Ikkita alohida UZS narx turi · OM-00',
                                           'Tayyorlov',
                                           'Majburiy aksiyalarni boshqa testlardan narx turi orqali ajratish.',
                                           'Ikkita yangi narx turi xonaga biriktiriladi; narx 7 000. Oldingi narxlar '
                                           'va bog‘lanishlar saqlanadi.'),
 ('mandatory', 'test_01_prepare_bank_action'): ('Bank/P1 uchun majburiy A10 → B1 · OM-01',
                                                'Tayyorlov',
                                                'Faqat Bank va birinchi yangi narx turida ishlaydigan majburiy bonus '
                                                'yaratish.',
                                                'Saved forced=Y, A10→B1, Bank payment va P1 narx identitylari mos.'),
 ('mandatory', 'test_02_prepare_terminal_action'): ('Terminal/P2 uchun majburiy A10 → B1 · OM-02',
                                                    'Tayyorlov',
                                                    'Faqat Terminal va ikkinchi yangi narx turida ishlaydigan majburiy '
                                                    'bonus yaratish.',
                                                    'Saved forced=Y, A10→B1, Terminal payment va P2 narx identitylari '
                                                    'mos.'),
 ('mandatory', 'test_03_bank_matching'): ('Bank + narx-1: B1 avtomatik · OM-03',
                                          'Biznes testi',
                                          'Mos juftlikda majburiy Bank aksiyasi avtomatik qo‘llanishini tekshirish.',
                                          '10 × 7 000 = 70 000; Bank aksiyasidan boshqa mahsulot B1, narxi 0. '
                                          'Save/view/reopen mos.'),
 ('mandatory', 'test_04_terminal_wrong_price'): ('Terminal + narx-1: bonus yo‘q · OM-04',
                                                 'Biznes testi',
                                                 'Payment yoki narxi mos bo‘lmagan majburiy aksiyalar bonus '
                                                 'bermasligini tekshirish.',
                                                 '70 000; saqlangan bonus yo‘q. Payment Terminal, narx-1 saqlanadi.'),
 ('mandatory', 'test_05_terminal_matching'): ('Terminal + narx-2: B1 avtomatik · OM-05',
                                              'Biznes testi',
                                              'Mos juftlikda aynan Terminal aksiyasi avtomatik qo‘llanishini '
                                              'tekshirish.',
                                              '70 000; Terminal aksiyasidan B1, narxi 0. Bank aksiyasi olinmaydi.'),
 ('mandatory', 'test_06_bank_wrong_price'): ('Bank + narx-2: bonus yo‘q · OM-06',
                                             'Biznes testi',
                                             'Bank va ikkinchi narx turida ikkala aksiya sharti ham mos emasligini '
                                             'tekshirish.',
                                             '70 000; saved bonus yo‘q. Bank va narx-2 saqlanadi.'),
 ('mandatory', 'test_07_payment_change'): ('Payment o‘zgarganda bonus qayta hisoblanadi · OM-07',
                                           'Biznes testi',
                                           'Bank → Terminal → Bank holatlarini bitta orderda saqlash.',
                                           'B1 → bonus yo‘q → B1; jami 70 000, order ID o‘zgarmaydi.'),
 ('mandatory', 'test_08_quantity_threshold'): ('10 → 9 → 10 dona: bonus chegarasi · OM-08',
                                               'Biznes testi',
                                               'Majburiy bonus threshold ostiga tushganda yo‘qolishi va qaytishini '
                                               'tekshirish.',
                                               '10 dona: 70 000 + B1; 9 dona: 63 000, bonus yo‘q; 10 dona: B1 qaytadi. '
                                               'Har holat saqlanadi.'),
 ('mandatory', 'test_09_price_change'): ('Narx turi o‘zgarganda bonus qayta hisoblanadi · OM-09',
                                         'Biznes testi',
                                         'Bank payment bilan narx-1 → narx-2 → narx-1 holatlarini saqlash.',
                                         'B1 → bonus yo‘q → B1; 70 000 va order ID saqlanadi.'),
 ('stock', 'test_01_cancel_reserve'): ('Bekor qilish ombor rezervini qaytaradi · OS-01',
                                       'Biznes testi',
                                       'Yangi own order rezervi va Cancel natijasini joriy ombor qoldig‘i bilan '
                                       'solishtirish.',
                                       '2 dona New: physical o‘zgarmaydi, rezerv +2, available −2. Cancel: uchala '
                                       'qiymat baselinega qaytadi; canceled ID saqlanadi.')})


def _walk(value):
    if isinstance(value, dict):
        yield value
        for key in ("steps", "befores", "afters"):
            for child in value.get(key, []):
                yield from _walk(child)


def _read_attachment(directory, attachment):
    name = attachment.get("source", "")
    if not name or Path(name).name != name:
        return None
    try:
        return json.loads((directory / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


SPECS.update({
    ("bonus_limit", "test_00_prepare_price"): ("Alohida 7 000 so‘mlik narx · OL-00", "Tayyorlov", "Global bonus limitini boshqa aksiyalardan narx turi orqali ajratish.", "Own narx 7 000; oldingi narxlar va xona bog‘lanishlari saqlangan."),
    ("bonus_limit", "test_01_prepare_first_client"): ("Birinchi klient · OL-01", "Tayyorlov", "Birinchi alohida klientni yaratish va xonaga biriktirish.", "Saved ID/nom va eski bog‘lanishlar saqlangan."),
    ("bonus_limit", "test_02_prepare_second_client"): ("Ikkinchi klient · OL-02", "Tayyorlov", "Boshqa alohida klientni yaratish va xonaga biriktirish.", "Birinchi klientdan farqli ID; eski bog‘lanishlar saqlangan."),
    ("bonus_limit", "test_03_prepare_action"): ("Umumiy bonus limiti 2 · OL-03", "Tayyorlov", "10 dona uchun boshqa mahsulotdan1 bonus, ikki klientga umumiy limit 2.", "Ixtiyoriy cyclic aksiya; own narx turi; bonusning alohida max_value chegarasi yo‘q."),
    ("bonus_limit", "test_04_first_client_uses_bonus"): ("Birinchi klient birinchi bonusni oladi · OL-04", "Biznes testi", "10 dona, 70 000 so‘mlik Новый order va bepul bonus 1.", "Counter 0→1; Save/View/Edit mos; kamida 40 dona mahsulot va2 bonus mavjud."),
    ("bonus_limit", "test_05_second_client_uses_remaining"): ("Ikkinchi klient faqat qolgan bonusni oladi · OL-05", "Biznes testi", "20 dona, 140 000 so‘mlik Новый orderga global qoldiq sabab faqat1 bonus.", "Preview 1; saved bonus 1 bepul; counter 1→2."),
    ("bonus_limit", "test_06_first_client_exhausted"): ("Limit tugadi: birinchi klient · OL-06", "Biznes testi", "Birinchi klient yangi orderida shu aksiya taklif qilinmaydi.", "10 dona, 70 000 so‘m Draft; bonus 0; counter 2 qoladi; qayta ochish mos."),
    ("bonus_limit", "test_07_second_client_exhausted"): ("Limit tugadi: ikkinchi klient · OL-07", "Biznes testi", "Umumiy cheklov ikkinchi klientga ham ishlaydi.", "10 dona, 70 000 so‘m Draft; bonus 0; counter 2 qoladi; qayta ochish mos."),
    ("bonus_limit", "test_08_cancel_releases_limit"): ("Bekor qilish bonus limitini qaytaradi · OL-08", "Biznes testi", "Birinchi klientning aynan shu Новый orderini bekor qilish.", "SameID Отменен; counter 2→1."),
    ("bonus_limit", "test_09_second_client_reuses_limit"): ("Bo‘shagan bonusni boshqa klient qayta oladi · OL-09", "Biznes testi", "Ikkinchi klient yangi 20 dona orderda qaytgan1 bonusni oladi.", "140000 so‘m, bonus 1 bepul; counter 1→2; Save/View/Edit mos."),
})




SPECS.update({
    ("product_limit", "test_00_prepare_product"): (
        "TMZ limiti uchun alohida mahsulot · OPL-00", "Tayyorlov",
        "Boshqa guruhlar limitiga ta’sir qilmasdan, faqat shu test uchun mahsulot yaratish.",
        "Yangi mahsulot IDsi, nomi va kodi saqlangan; sotuv narxi 7 000 so‘m."),
    ("product_limit", "test_01_prepare_client"): (
        "TMZ limiti orderlari uchun alohida klient · OPL-01", "Tayyorlov",
        "Ikki order uchun bitta yangi klient yaratib test ish zonasiga biriktirish.",
        "Klientning saved IDsi va xona bog‘lanishi mos; oldingi bog‘lanishlar saqlangan."),
    ("product_limit", "test_02_prepare_stock"): (
        "TMZ limiti mahsulotidan 20 dona kirim · OPL-02", "Tayyorlov",
        "Test mahsuloti uchun asosiy omborga alohida kirim yaratish va o‘tkazish.",
        "Kirim IDsi va posted holati tasdiqlangan; UI’da 20 dona fizik va erkin qoldiq, rezerv 0."),
    ("product_limit", "test_03_prepare_limit"): (
        "Test xonasi va mahsulotiga kunlik 10 dona limit · OPL-03", "Tayyorlov",
        "Aynan test mahsuloti, ish zonasi va kun uchun limitni UI orqali saqlash.",
        "Qayta ochilgan limitda nom, xona, sanalar, Ежедневный turi va 10 dona mos. Bu qadam limitdan oshishni rad etishni tekshirmaydi."),
    ("product_limit", "test_04_first_order_six"): (
        "Birinchi order: 6 dona va 42 000 so‘m · OPL-04", "Biznes testi",
        "Kunlik 10 dona limit sozlangan mahsulotdan birinchi Новый orderni yaratish.",
        "6 × 7 000 = 42 000; bonus va chegirma yo‘q. Save/view/reopen mos, rezerv 0→6; fizik qoldiq o‘zgarmaydi."),
    ("product_limit", "test_05_second_order_four"): (
        "Ikkinchi order: 4 dona; jami rezerv 10 · OPL-05", "Biznes testi",
        "Shu klient, xona va kunda yana 4 dona mahsulotli alohida order yaratish.",
        "Ikkinchi order 28 000 so‘m, saved ID va miqdor mos. Ikkala orderning jami rezervi 6+4=10; fizik qoldiq o‘zgarmaydi."),
    ("product_limit", "test_06_cancel_first_order"): (
        "Birinchi order bekor: rezervda 4 dona qoladi · OPL-06", "Biznes testi",
        "Aynan birinchi 6 donali orderni bekor qilib ikkinchi order rezervini saqlash.",
        "Birinchi order Отменен. Jami rezerv 10→4; 6 dona erkin qoldiqqa qaytadi, fizik qoldiq o‘zgarmaydi."),
    ("product_limit", "test_07_reuse_released_limit"): (
        "Bekor qilishdan keyin ikkinchi order 4→10 · OPL-07", "Biznes testi",
        "Birinchi order bekor qilingach ikkinchi order miqdorini 10 donaga oshirib saqlash.",
        "Ayni ikkinchi order 10 dona va 70 000 so‘m; Save/view/reopen mos, rezerv yana 10. Bu musbat oqim limitdan ortiq miqdorni rad etish yoki used-limit hisoblagichini tasdiqlamaydi."),
    ("two_warehouses", "test_00_prepare_client"): (
        "Ikki omborli order uchun alohida klient · OW-00", "Tayyorlov",
        "Ikki ombor testiga tegishli klient yaratish va ish zonasiga biriktirish.",
        "Saved klient IDsi va xona bog‘lanishi mos; boshqa klient va bog‘lanishlar saqlangan."),
    ("two_warehouses", "test_01_prepare_warehouses"): (
        "Alohida ikkinchi omborni yaratish · OW-01", "Tayyorlov",
        "UI orqali yangi Minor ombor yaratib test ish zonasiga bog‘lash.",
        "Yangi faol ombor IDsi qayta o‘qilgan; xonada oldingi omborlar va aynan yangi ombor mavjud."),
    ("two_warehouses", "test_02_prepare_stock"): (
        "Ikkala ombor uchun yetarli qoldiq · OW-02", "Tayyorlov",
        "Asosiy ombordagi yetishmagan qismini 5 donagacha to‘ldirish va yangi omborga 5 dona kiritish.",
        "Ikkala omborda kamida 5 dona erkin. Main qoldig‘i faqat kirim miqdoriga oshadi, oldingi rezerv saqlanadi; yangi omborda physical 5, booked 0, available 5."),
    ("two_warehouses", "test_03_create_draft"): (
        "Bitta SKU ikki omborda 2/3 dona · OW-03", "Biznes testi",
        "Bitta orderga asosiy ombordan 2 va ikkinchi ombordan 3 dona bir xil mahsulot qo‘shish.",
        "5 × 7 000 = 35 000 so‘mlik Черновик. Ikkala qatorning ombori va miqdori Save/view/reopenda mos; ikkala ombor qoldig‘i o‘zgarmaydi."),
    ("two_warehouses", "test_04_reserve_both"): (
        "Новый order: omborlarda alohida 2/3 rezerv · OW-04", "Biznes testi",
        "Shu ikki omborli qoralamani Новыйga o‘tkazib har ombor ta’sirini alohida tekshirish.",
        "Order 35 000 so‘mligicha qoladi. Main rezervi +2, ikkinchi ombor rezervi +3; physical o‘zgarmaydi, available tegishlicha kamayadi."),
    ("two_warehouses", "test_05_reallocate"): (
        "Tahrir: ombor miqdorlari 2/3→3/2 · OW-05", "Biznes testi",
        "Ayni Новый orderning jami miqdorini o‘zgartirmasdan omborlar bo‘yicha taqsimotni almashtirish.",
        "Saved order IDsi va 35 000 jami saqlanadi. View/reopenda 3/2 dona; rezervlar baselinega nisbatan +3/+2, physical o‘zgarmaydi."),
    ("two_warehouses", "test_06_cancel_both"): (
        "Cancel: ikkala ombor rezervi qaytadi · OW-06", "Biznes testi",
        "Aynan shu ikki omborli orderni bekor qilib har omborning fresh baseline qoldig‘ini qaytarish.",
        "Saved ID, ikki qator va 35 000 summa saqlanadi, status Отменен. Ikkala omborning physical/booked/available qiymatlari baselinega qaytadi; boshqa rezervlar saqlanadi."),
    ("mixed_promotions", "test_00_prepare_price"): (
        "Birgalikdagi aksiyalar uchun alohida narx · OM-00", "Tayyorlov",
        "Majburiy bonus va ixtiyoriy chegirmani boshqa aksiyalardan yangi narx turi orqali ajratish.",
        "Yangi UZS narx turi va mahsulot narxi 7 000; xona bog‘lanishi mos, oldingi narxlar saqlangan. Перечисление to‘lov turi mavjud."),
    ("mixed_promotions", "test_01_prepare_mandatory_bonus"): (
        "10 donaga 1 majburiy bonus · OM-01", "Tayyorlov",
        "Faqat guruhning narx turi va Bank to‘lovi uchun A10→B1 majburiy aksiyani yaratish.",
        "Aksiya IDsi, forced=Y, 10 dona sharti va boshqa mahsulotdan 1 dona bonus saved modelda mos."),
    ("mixed_promotions", "test_02_prepare_optional_discount"): (
        "10 donaga ixtiyoriy 10% chegirma · OM-02", "Tayyorlov",
        "Majburiy bonus bilan bir xil narx va Bank shartida ishlaydigan alohida ixtiyoriy chegirma yaratish.",
        "Saved aksiya forced=N; mahsulot sharti 10 dona, chegirma 10%; narx va payment IDlari mos."),
    ("mixed_promotions", "test_03_toggle_discount"): (
        "Chegirma ON/OFF/ON; majburiy bonus qoladi · OM-03", "Biznes testi",
        "10 donali orderda majburiy bonusga tegmasdan ixtiyoriy chegirmani yoqish, o‘chirish va qayta yoqish.",
        "Ayni orderda jami 63 000→70 000→63 000. Har Save/viewda 1 dona bepul majburiy bonus saqlanadi; yakuniy reopenda chegirma tanlangan."),
    ("mixed_promotions", "test_04_quantity_boundary"): (
        "9→10 dona: jami bir xil, tarkib o‘zgaradi · OM-04", "Biznes testi",
        "Aksiya chegarasidan past 9 dona orderni saqlab, shu orderni 10 donaga oshirish va ixtiyoriy chegirmani tanlash.",
        "9 dona: jami 63 000, chegirma 0, bonus 0. 10 dona: jami 63 000, chegirma 7 000, bepul B1. Saved ID, miqdor, chegirma va bonus alohida tekshiriladi."),
})


SPECS.update({
    ("auto_offset", "test_00_prepare_client"): (
        "Alohida klient yaratish", "Tayyorlov",
        "Guruh uchun yangi klient yaratish va xonaga biriktirish.",
        "Klient IDsi va xona bog‘lanishi tekshirilgan."),
    ("auto_offset", "test_01_archive_order"): (
        "14 000 so‘mlik order yaratish va arxivlash", "Biznes testi",
        "2 dona TMZli buyurtmani saqlash va arxivga o‘tkazish.",
        "Aynan shu order IDsi uchun 14 000 qarz, avans 0."),
    ("auto_offset", "test_02_post_auto_offset"): (
        "Kirim orqali order qarzini avtomatik yopish", "Biznes testi",
        "Avtomatik hisob-kitobni yoqib, 14 000 so‘m kirimni o‘tkazish.",
        "Kirim IDsi va posted holati tasdiqlanadi. Tarixda bitta 14 000 so‘mlik yozuv shu orderga tegishli, avans va balans 0."),
    ("prepayment_first", "test_00_prepare_client"): (
        "Alohida klient yaratish", "Tayyorlov",
        "Guruh uchun yangi klient yaratish va xonaga biriktirish.",
        "Klient IDsi va xona bog‘lanishi tekshirilgan."),
    ("prepayment_first", "test_01_post_advance"): (
        "Orderdan oldin 20 000 so‘m avans olish", "Biznes testi",
        "Toza klient uchun avtomatik hisob-kitobsiz kirim o‘tkazish.",
        "Kirim IDsi, avans 20 000, qarz va ochiq order summasi 0."),
    ("prepayment_first", "test_02_archive_after_advance"): (
        "Avansdan keyin 14 000 so‘mlik order yaratish va arxivlash", "Biznes testi",
        "Klientning oldingi avansini tekshirib, 2 dona TMZli order yaratish va arxivlash.",
        "Aynan shu order bo‘yicha qarz 14 000 va mavjud avans 20 000."),
    ("prepayment_first", "test_03_apply_advance"): (
        "Avansdan order qarzini yopish", "Biznes testi",
        "Avansdan aniq order IDsi uchun 14 000 so‘m ajratish.",
        "Tarixda aynan shu orderga 14 000 ajratilgan. Qarz 0, avans va balans 6 000."),
})

for _group in GROUP_FEATURES:
    for _test, _title, _expected in (
        ("test_000_catalog", "Alohida mahsulot tayyorlash", "Exact kod bo‘yicha yagona faol mahsulot; ID va nom mos. Mavjud entity qayta yaratilmaydi."),
        ("test_001_prices", "Mahsulot narxini 7 000 so‘m qilib belgilash", "Own mahsulotlarga 7000 so‘mlik saved narx. Boshqa guruh narxi o‘zgarmaydi."),
        ("test_002_stock", "Ombor qoldig‘ini tayyorlash va tekshirish", "Own kirimlar posted; UI’dagi fizik qoldiq, rezerv va erkin qoldiq guruh talabiga mos."),
    ):
        SPECS[(_group, _test)] = (_title, "Tayyorlov", _title + ": mavjudini tekshirish yoki yetishmagan qismini tayyorlash.", _expected)
for _test, _title in (
    ("test_03_before_save", "Save oldidan uzilish"),
    ("test_04_commit_before_id", "Server saqlagach ID yozilishidan oldin uzilish"),
    ("test_05_after_id", "ID yozilgach uzilish"),
    ("test_06_shared_create", "Umumiy tayyorlovni yaratish"),
    ("test_07_shared_reuse", "Umumiy tayyorlovni qayta ishlatish"),
    ("test_08_order_saved", "UI order saqlangach qayta davom etish"),
):
    SPECS[("recovery", _test)] = (_title, "Mexanizm tekshiruvi",
        "Faqat verification runneridagi boshqariladigan uzilish; dastlabki FAIL ataylab yaratiladi. Normal biznes suite’da uzilish kiritilmaydi.",
        "Bitta avtomatik retry; exact kalit bo‘yicha aynan 1 entity; mavjud IDdan davom etish; saqlangan qiymatlar tekshiriladi.")

SPECS.update({
    ("recovery", "test_09_prepare_payment_client"): (
        "Cashin retry uchun alohida klient", "Tayyorlov",
        "Birinchi to‘lov oqimiga alohida klientni tayyorlash.",
        "Faol klient saqlangan va ish zonasiga biriktirilgan."),
    ("recovery", "test_09b_prepare_second_client"): (
        "Ikki bosqichli to‘lov retry uchun alohida klient", "Tayyorlov",
        "Ikkinchi to‘lov oqimini boshqa klientda tekshirish.",
        "Faol klient saqlangan va ish zonasiga biriktirilgan."),
    ("recovery", "test_10_cashin_saved"): (
        "Saqlangan cashinni qayta yaratmasdan davom etish", "Mexanizm tekshiruvi",
        "14 000 so‘m cashin tasdiqlangach boshqariladigan uzilish; keyin shu cashindan qarzni yopish.",
        "Aynan 1 ta cashin. 6 000 + 8 000 ajratilgach qarz va predoplata 0; ikkinchi kirim yaratilmaydi."),
    ("recovery", "test_11_unknown_offset"): (
        "Noaniq to‘lov holatida ikkinchi POST yuborilmaydi", "Mexanizm tekshiruvi",
        "Noaniq saqlash jurnalini nazoratli yaratib, haqiqiy qarz holatida qayta yozish himoyasini tekshirish.",
        "RetryBlocked sababi aniq. Qarz yopish uchun yangi POST yuborilmagan."),
    ("recovery", "test_12_partial_attachment"): (
        "Klient bor: retry faqat xona bog‘lanishini tugatadi", "Mexanizm tekshiruvi",
        "Klient saqlangach, xonaga biriktirish oldida boshqariladigan uzilish.",
        "Retry aynan shu klient IDsi bilan davom etadi; yangi klient yaratmaydi; xona bog‘lanishi tasdiqlanadi."),
    ("recovery", "test_13_ambiguous_lookup"): (
        "Noaniq qidiruv javobi yaratishga ruxsat bermaydi", "Mexanizm tekshiruvi",
        "Faqat protokol himoyasi: 2 ta yozuv, count yo‘qligi va count/data nomosligini tekshirish.",
        "Uch holat ham RetryBlocked. Bu sun’iy javoblar mahsulot biznes testi natijasi hisoblanmaydi."),
    ("recovery", "test_14_between_installments"): (
        "6 000 to‘langach uzilish: retry faqat qolgan 8 000 ni to‘laydi", "Mexanizm tekshiruvi",
        "Birinchi qisman to‘lov tasdiqlangach boshqariladigan uzilish; qolgan to‘lovni davom ettirish.",
        "Retryda aynan 1 ta offset POST. Yakuniy qarz va predoplata 0; birinchi 6 000 takrorlanmaydi."),
})


def _metadata(directory, scopes):
    case, phase, preparation = {}, {}, {}
    prep_names = {
        "Возврат narxi — ID va bog'lanishlar": "return_price",
        "Tayyor 10% skidka — ID va bog'lanishlar": "margin",
    }
    for scope in scopes:
        for node in _walk(scope):
            for attachment in node.get("attachments", []):
                name = attachment.get("name", "")
                if (name in {"Order, klient va to'lov IDlari", "Order fazalari natijasi", "Order biznes setup ma'lumotlari"}
                        or name.startswith(("Payment klient —", "Bonus limiti klienti —",
                                            "Qaytarish klienti —", "Ikki order klienti —", "Chegirmalar klienti —"))
                        or name in {"Majburiy aksiya tayyorlovi", "Umumiy bonus limiti tayyorlovi", "Umumiy bonus limiti zanjiri"}
                        or name in prep_names):
                    data = _read_attachment(directory, attachment)
                    if not isinstance(data, dict):
                        continue
                    if name == "Order, klient va to'lov IDlari": case = data
                    elif name == "Order fazalari natijasi": phase = data
                    elif name in prep_names:
                        # Name belongs to a price/discount, never to a client.
                        preparation = {**data, "preparation_kind": prep_names[name]}
                    else: preparation = data
    return case, phase, preparation


def _text(value):
    if isinstance(value, (dict, list)):
        value = json.dumps(safe_payload(value), ensure_ascii=False, sort_keys=True)
    return escape(safe_text(str(value)), quote=True)


def _table(headers, rows):
    return "<table><thead><tr>" + "".join(f"<th>{_text(h)}</th>" for h in headers) + "</tr></thead><tbody>" + "".join(
        "<tr>" + "".join(f"<td>{_text(v)}</td>" for v in row) + "</tr>" for row in rows
    ) + "</tbody></table>"


def _links(case, preparation):
    server = case.get("server") or preparation.get("url", "")
    parsed = urlsplit(server)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.password:
        return []
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
    if base.endswith("/a2"): base = base[:-3]
    links = []
    targets = [("Order", i, "trade/tdeal/order/order_view", "deal_id") for i in case.get("order_ids", [])]
    targets += [("To‘lov", p.get("id"), "trade/tcs/cashin_view", "cashin_id") for p in case.get("payments", [])]
    targets += [("Qaytarish", p.get("id"), "anor/mdeal/return/return_view", "deal_id") for p in case.get("returns", [])]
    client_id = case.get("client", {}).get("person_id") or preparation.get("person_id")
    targets.append(("Klient", client_id, "anor/mr/person/natural_person_view", "person_id"))
    for label, identity, route, key in targets:
        if identity is not None and str(identity).isdigit():
            links.append({"name": f"{label} №{identity}", "url": f"{base}/a2/{route}?{urlencode({key: str(identity)})}", "type": "link"})
    return links


def _description(result, spec, case, phase, preparation, api_count):
    title, kind, purpose, expected = spec
    status = result.get("status", "unknown")
    status_name = {"passed": "PASS — test o‘tdi", "failed": "FAIL — tekshiruvdan o‘tmadi",
                   "broken": "ERROR — test yakunlanmadi", "skipped": "BAJARILMADI"}.get(status, status)
    blocks = [f'<!-- {VERSION} -->', f"<h3>{_text(status_name)}</h3>",
              f"<p><b>Turi:</b> {_text(kind)}. <b>Maqsad:</b> {_text(purpose)}</p>"]
    if status in {"failed", "broken", "skipped"}:
        failed = next((s for s in result.get("steps", []) if s.get("status") in {"failed", "broken"}), None)
        failed_phase = next(((name, data) for name, data in phase.get("phases", {}).items()
                             if data.get("outcome") in {"failed", "skipped"}), None)
        if phase.get("blocked_by"):
            blocks.append(f"<p><b>Sabab:</b> bloklagan tayyorlov yoki test: {_text(phase['blocked_by'])}.</p>")
        elif failed_phase or failed:
            stage = failed.get("name") if failed else {"setup": "Testga tayyorlanish", "teardown": "Dalillarni saqlash / testni yakunlash"}.get(failed_phase[0], "Test bajarilishi")
            blocks.append(f"<p><b>To‘xtagan bosqich:</b> {_text(stage)}.</p>")
        message = (failed_phase[1].get("message", "") if failed_phase else "") or result.get("statusDetails", {}).get("message", "")
        blocks.append(f"<p><b>Kuzatilgan xabar:</b> {_text(message[:1200] or 'Batafsil sabab texnik dalillarda ko‘rsatilgan.')}</p>")
        blocks.append("<p>Muammo mahsulotda yoki testda ekanligi tekshirilishi kerak. Keyingi bajarilmagan qadamlar PASS hisoblanmaydi; screenshot va trace ilovalarda.</p>")
    blocks += ["<h3>Kutiladigan biznes natija</h3>", f"<p>{_text(expected)}</p>"]
    rows = []
    for label, value in (("Server", case.get("server") or preparation.get("url")),
                         ("Filial ID", case.get("filial_id") or preparation.get("filial_id")),
                         ("Klient", case.get("client", {}).get("name") or (preparation.get("name") if not preparation.get("preparation_kind") else None))):
        if value: rows.append((label, value))
    for key, label in (("product", "Sotuv mahsuloti"), ("bonus_product", "Bonus mahsuloti"), ("room", "Xona"), ("price_type", "Narx turi")):
        data = case.get("fixtures", {}).get(key, {})
        if data: rows.append((label, f"{data.get('name', '')} (ID {data.get('id', '')})"))
    if case.get("fixtures", {}).get("staff_name"): rows.append(("Shtat", case["fixtures"]["staff_name"]))
    if case.get("fixtures", {}).get("warehouse_id"): rows.append(("Ombor ID", case["fixtures"]["warehouse_id"]))
    if preparation.get("product_name"): rows.append(("Sotuv mahsuloti", preparation["product_name"]))
    if preparation.get("bonus_product_name"): rows.append(("Bonus mahsuloti", preparation["bonus_product_name"]))
    if preparation.get("preparation_kind") in {"return_price", "margin"}:
        caption = "Qaytarish narx turi" if preparation["preparation_kind"] == "return_price" else "Tayyor chegirma"
        rows.append((caption, preparation.get("name", "")))
        for key, label in (("id", "ID"), ("room_id", "Ish zonasi ID"),
                           ("percent", "Chegirma foizi"), ("stage", "Oxirgi qayd etilgan bosqich")):
            if preparation.get(key) is not None:
                rows.append((label, preparation[key]))
        state = preparation.get("status")
        if state:
            rows.append(("Tayyorlov natijasi", {"passed": "Tekshirildi", "failed": "Yakunlanmadi", "process": "Jarayonda"}.get(state, state)))
    if rows: blocks += ["<h3>Test ma’lumotlari</h3>", _table(["Maydon", "Qiymat"], rows)]
    observations = case.get("observations", [])
    if observations:
        blocks += ["<h3>Kutilgan va amaldagi qiymatlar</h3>", _table(
            ["Tekshiruv", "Kutilgan", "Amaldagi", "Natija"],
            [(r.get("label"), r.get("expected"), r.get("actual"), str(r.get("status", "")).upper()) for r in observations])]
    elif kind == "Biznes testi":
        blocks.append("<p><b>Ushbu natijada:</b> amaldagi qiymatlar jadvali mavjud emas (oldingi format yoki bosqich bajarilmagan). Quyida original qadam natijalari va saqlangan yozuvlar ko‘rsatilgan; qiymatlar PASS belgisidan taxmin qilib to‘ldirilmagan.</p>")
    if case.get("allocations"):
        blocks += ["<h3>Qarzga ajratish dalillari</h3>", _table(["Order ID", "Ajratilgan summa", "Qayd etilgan natija"],
            [(a.get("order_id"), a.get("amount"), "Order qarzi va klient balansi bilan tasdiqlangan" if a.get("state") == "verified_by_order_debt_and_balance" else "Boshlangan; yakuniy tasdiq yo‘q") for a in case["allocations"]])]
    steps = [(s.get("name"), {"passed":"PASS", "failed":"FAIL", "broken":"ERROR", "skipped":"BAJARILMADI"}.get(s.get("status"), "TUGALLANMAGAN")) for s in result.get("steps", [])]
    if steps: blocks += ["<h3>Bajarilgan biznes qadamlar</h3>", _table(["Qadam", "Natija"], steps)]
    if api_count:
        blocks.append(f"<p><b>API dalillari:</b> {api_count} ta chaqiruv bitta «API so‘rovlar jurnali» ilovasida. HTTP 200 biznes natijasi to‘g‘riligini o‘zi isbotlamaydi.</p>")
    blocks.append("<p><b>Qamrov:</b> ushbu case va yuqoridagi tekshiruvlar. Tayyorlov testi biznes testi soniga qo‘shib talqin qilinmaydi. Yaratilgan test yozuvlari saqlanadi.</p>")
    return "\n".join(blocks)


def _markdown(html):
    """Allure native Markdown uchun jadval va izohlarni tayyorlash."""
    def table(match):
        rows = []
        for row in re.findall(r"<tr>(.*?)</tr>", match[0], re.S):
            cells = re.findall(r"<t[hd]>(.*?)</t[hd]>", row, re.S)
            rows.append("| " + " | ".join(c.replace("|", r"\|").replace("\n", " ") for c in cells) + " |")
        if rows:
            columns = len(re.findall(r"<th>", match[0]))
            rows.insert(1, "| " + " | ".join(["---"] * columns) + " |")
        return "\n\n" + "\n".join(rows) + "\n\n"
    html = re.sub(r"<table>.*?</table>", table, html, flags=re.S)
    html = re.sub(r"<h3>(.*?)</h3>", r"\n\n### \1\n\n", html)
    html = html.replace("<b>", "**").replace("</b>", "**")
    html = html.replace("<p>", "\n\n").replace("</p>", "\n\n")
    return html.strip()


def _backup_write(path, data, backup):
    backup.mkdir(parents=True, exist_ok=True)
    target = backup / path.name
    if not target.exists(): target.write_bytes(path.read_bytes())
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def prepare_presentation(source, target, *, started_at_ms=None):
    """Faqat shu run Order natijalarini va ularga bog‘langan ilovalarni nusxalash."""
    source, target = Path(source).resolve(), Path(target).resolve()
    if source == target:
        raise ValueError("Allure taqdimot nusxasi asl natijalardan alohida bo‘lishi kerak")
    target.mkdir(parents=True, exist_ok=True)
    selected = []
    for path in source.glob("*-result.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("fullName", "").startswith(PREFIX): continue
        if started_at_ms is not None and data.get("start", 0) < started_at_ms: continue
        selected.append((path, data))
    context = None
    if target.name != "allure-results":
        # Retain every attempt. A blocked retry must not hide the original FAIL.
        context = _run_context(source, (data for _, data in selected))
    identities = {data["uuid"] for _, data in selected}
    for path in source.glob("*-container.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if identities.intersection(data.get("children", [])):
            data["children"] = [child for child in data["children"] if child in identities]
            selected.append((path, data))
    copied_attachments = set()
    for path, data in selected:
        (target / path.name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for node in _walk(data):
            for attachment in node.get("attachments", []):
                name = attachment.get("source", "")
                if name and Path(name).name == name and (source / name).is_file():
                    if not (target / name).exists():
                        copied_attachments.add(name)
                    shutil.copy2(source / name, target / name)
    for name in ("environment.properties", "executor.json", "categories.json"):
        if (source / name).is_file(): shutil.copy2(source / name, target / name)
    # The standalone runner first snapshots raw attempts, then builds its combined report.
    if target.name != "allure-results":
        from tests.regression.test_orders.helpers.run_overview import reconcile_results
        reconcile_results(target, target.parent)
        # Refresh statuses after ledger reconciliation, retaining both attempts.
        reconciled = [json.loads(p.read_text(encoding="utf-8")) for p in target.glob("*-result.json")]
        current_attempts, current_impact = _run_context(target, reconciled)
        attempts, impact = context
        for name, states in current_attempts.items():
            attempts[name].update(states)
        impact.update(current_impact)
        enrich_results(target, context=(attempts, impact))
        # Prune only files newly copied by this call and no longer referenced.
        # Raw sources, existing target files, and generated summary files stay intact.
        referenced = set()
        for pattern in ("*-result.json", "*-container.json"):
            for path in target.glob(pattern):
                for node in _walk(json.loads(path.read_text(encoding="utf-8"))):
                    referenced.update(a.get("source") for a in node.get("attachments", []))
        for name in copied_attachments - referenced:
            (target / name).unlink(missing_ok=True)
    return target


STATUS_NAMES = {"passed": "o‘tdi", "failed": "yiqildi", "broken": "xato bilan to‘xtadi", "skipped": "bajarilmadi", "interrupted": "to‘xtatildi", "not_run": "boshlanmadi"}
TECHNICAL_STEP = "Texnik tafsilotlar"
DEPENDENCY_LABEL = "Bog‘liq test"


def order_dependency_labels(group, names):
    """Capture direct prerequisites using the same titles as their runner tests."""
    values = [order_report_title(group, name) for name in names]
    return [{"name": DEPENDENCY_LABEL, "value": value}
            for value in (values or ["Boshqa testga bog‘liq emas"])]


def _dependency_summary(result):
    values = [label["value"] for label in result.get("labels", [])
              if label.get("name") == DEPENDENCY_LABEL]
    return "\n".join(sorted(values)) if values else "Bu run uchun dependency ma’lumoti qayd etilmagan."


def _recorded_steps(result, related):
    """Render only recorded Allure steps, preserving phase and nested order."""
    rows = []

    def visit(steps, phase, prefix=""):
        for index, step in enumerate(steps, 1):
            if step.get("name") == TECHNICAL_STEP:
                continue
            number = f"{prefix}{index}"
            start, stop = step.get("start"), step.get("stop")
            duration = (f"{(stop - start) / 1000:.3f} s"
                        if isinstance(start, (int, float)) and isinstance(stop, (int, float))
                        and stop >= start else "Qayd etilmagan")
            status = {"passed": "PASS", "failed": "FAIL", "broken": "ERROR",
                      "skipped": "BAJARILMADI"}.get(step.get("status"), "TUGALLANMAGAN")
            rows.append((phase, number, step.get("name", "Nomsiz qadam"), status, duration))
            visit(step.get("steps", []), phase, number + ".")

    def fixture_steps(key):
        stages = [stage for container in related.values() for stage in container.get(key, [])]
        # Unknown starts follow timed entries; never invent their chronology.
        return sorted(stages, key=lambda stage: (
            not isinstance(stage.get("start"), (int, float)),
            stage["start"] if isinstance(stage.get("start"), (int, float)) else 0,
        ))

    visit(fixture_steps("befores"), "Setup")
    visit(result.get("steps", []), "Test")
    visit(fixture_steps("afters"), "Teardown")
    return rows


def _identity(full_name):
    module, _, test = full_name.partition("#")
    group = next((g for g in GROUP_FEATURES if module.endswith(f"test_{g}_runner")), None)
    return group, test



def order_report_section(group, test):
    return "1 · Setup" if SPECS[group, test][1] == "Tayyorlov" else "2 · Biznes flow"


@lru_cache(maxsize=None)
def _group_test_numbers(group):
    """Number tests in runner source order without importing or executing them."""
    folder = "verification" if group == "recovery" else "runners"
    runner = Path(__file__).resolve().parent.parent / folder / f"test_{group}_runner.py"
    functions = (
        node.name for node in ast.parse(runner.read_text(encoding="utf-8")).body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    )
    return {name: number for number, name in enumerate(functions, 1)}


def order_report_title(group, test, *, rerun=False):
    title = re.sub(r" · [A-Z][A-Z0-9-]*-[0-9]+[A-Z]?$", "", SPECS[group, test][0])
    scenario = GROUP_FEATURES[group].split(" · ", 1)[0]
    number = _group_test_numbers(group)[test]
    if group in {"auto_offset", "prepayment_first"} and test == "test_002_stock":
        title = "Ombor qoldig‘ini tekshirish (2 dona mahsulot)"
    retry = " ↻" if rerun else ""
    return f"{scenario}-T{number:02d} · {title}{retry}"


def order_report_case(function):
    """Use the same searchable names in raw Allure results and in the final report."""
    group, test = _identity(f"{function.__module__}#{function.__name__}")
    allure.title(order_report_title(group, test))(function)
    declaration = next((mark for mark in getattr(function, "pytestmark", [])
                        if mark.name == "order_requires"), None)
    if declaration is not None:
        for label in order_dependency_labels(group, declaration.args):
            allure.label(label["name"], label["value"])(function)
    return allure.story(order_report_section(group, test))(function)


def _attempt_number(result):
    value = next((str(p.get("value", "")) for p in result.get("parameters", [])
                  if p.get("name") == "Urinish"), "")
    return 2 if value.strip("'\" ").startswith("2") else 1


def _phase_evidence(directory, result):
    attachment = next((a for a in result.get("attachments", [])
                       if a.get("name") == "Order fazalari natijasi"), {})
    return _read_attachment(directory, attachment) or {}


def _run_context(directory, results):
    attempts, impact = defaultdict(dict), defaultdict(Counter)
    for result in results:
        name = result.get("fullName", "")
        number = _attempt_number(result)
        phase = _phase_evidence(directory, result)
        state = phase.get("status") or result.get("status")
        attempts[name][number] = STATUS_NAMES.get(state, "noma’lum")
        if result.get("status") != "skipped":
            continue
        phase = _phase_evidence(directory, result)
        kind = SPECS.get(_identity(name), (None, "Test"))[1]
        for root in set(phase.get("blocked_by", "").split("; ")):
            if "::" in root:
                impact[(root, number)][kind] += 1
    return attempts, impact


def _readable_blocker(root):
    if "::" in root:
        module, test = root.split("::", 1)
        group, test = _identity(module.removesuffix(".py").replace("/", ".") + "#" + test)
        if (group, test) in SPECS:
            return order_report_title(group, test)
    return safe_text(root)[:240]


def _actual(result, case, phase):
    status = result.get("status")
    blocked_by = phase.get("blocked_by", "")
    if status == "skipped" and blocked_by:
        return "Bajarishga to‘sqinlik qilgan qadam: " + ", ".join(
            _readable_blocker(root) for root in blocked_by.split("; "))
    failed = status in {"failed", "broken"}
    observations = case.get("observations", [])
    if failed:
        observations = [row for row in observations if row.get("status") == "failed"]
    if observations:
        return " · ".join(f"{r.get('label')}: {r.get('actual')}" for r in observations[-3:])
    message = result.get("statusDetails", {}).get("message", "")
    if "TypeError:" in message and ("required positional argument" in message or "unexpected keyword argument" in message):
        if _identity(result["fullName"]) == ("mandatory", "test_00_prepare_prices") and "run_prepare_prices()" in message and "'group'" in message:
            return "Avtotest narx tayyorlash funksiyasini noto‘g‘ri chaqirdi. Ikkita narx turini yaratish boshlanmadi."
        return "Avtotest funksiyani unga mos kelmaydigan parametr bilan chaqirdi."
    if status == "passed":
        return "Test barcha tekshiruvlardan o‘tdi."
    lines = safe_text(message).strip().splitlines()
    stage = next((step.get("name") for step in result.get("steps", [])
                  if step.get("status") in {"broken", "failed"}), None)
    return " ".join(part for part in ((stage + ".") if stage else "", lines[0][:320] if lines else
                    STATUS_NAMES.get(status, "Natija noma’lum")) if part)


def _failed_step(result):
    # Prefer the innermost recorded failure, rather than its enclosing business flow.
    failed = [node for node in _walk(result) if node is not result
              and node.get("status") in {"failed", "broken"} and node.get("name")]
    return failed[-1].get("name") if failed else None


def _qa_summary(result, spec, case, phase, attempts, impact, preparation):
    name = result["fullName"]
    status = phase.get("status") if phase.get("status") in {"interrupted", "not_run"} else result.get("status")
    failed = status in {"failed", "broken", "interrupted"}
    observations = case.get("observations", [])
    failures = [row for row in observations if row.get("status") == "failed"] if failed else []
    expected = " · ".join(f"{row.get('label')}: {row.get('expected')}" for row in failures) if failures else spec[3]
    actual = "Test bajarilishi to‘xtatildi; yakuniy muvaffaqiyat tasdiqlanmagan." if status == "interrupted" else _actual(result, case, phase)
    if status == "not_run":
        actual = "Ushbu test boshlanmagan; amaldagi natija yo‘q."
    lines = [("Holat", STATUS_NAMES.get(status, "noma’lum")), ("Turi", spec[1]),
             ("Nima tekshiriladi", spec[2]), ("Kutilgan", expected), ("Amalda", actual)]
    lines.append(("Bevosita bog‘liq testlar", _dependency_summary(result)))
    if phase.get("blocked_by"):
        lines.append(("Testni bloklagan sabab / test", phase["blocked_by"]))
    lines.append(("Allure qadamlari", "Execution bo‘limida; to‘liq ro‘yxat «Allure qadamlari» ilovasida. Faqat qayd etilgan qadamlar ko‘rsatiladi."))
    phases = phase.get("phases", {})
    timing = []
    for key, label in (("setup", "Tayyorlanish"), ("call", "Test bajarilishi"), ("teardown", "Yakunlash")):
        duration = phases.get(key, {}).get("duration_seconds")
        if isinstance(duration, (int, float)):
            timing.append(f"{label}: {duration:.2f} s")
    if timing:
        lines.append(("Vaqt", " · ".join(timing)))
    identities = []
    for label, values in (("Order", case.get("order_ids", [])),
                          ("To‘lov", [row.get("id") for row in case.get("payments", [])]),
                          ("Qaytarish", [row.get("id") for row in case.get("returns", [])]),
                          ("Klient", [case.get("client", {}).get("person_id") or preparation.get("person_id")])):
        values = [str(value) for value in values if value is not None and str(value).isdigit()]
        if values:
            identities.append(f"{label}: {', '.join(values)}")
    for key, label in (("product", "Mahsulot"), ("bonus_product", "Bonus mahsuloti"), ("room", "Xona"), ("price_type", "Narx turi")):
        identity = case.get("fixtures", {}).get(key, {}).get("id")
        if identity is not None:
            identities.append(f"{label}: {identity}")
    if preparation.get("preparation_kind") and preparation.get("id") is not None:
        identities.append(f"Tayyorlov yozuvi: {preparation['id']}")
    if identities:
        lines.append(("Test yozuvlari IDlari", " · ".join(identities)))
    if failed:
        failed_phase = next((key for key, data in phases.items() if data.get("outcome") == "failed"), None)
        stage = _failed_step(result) or {"setup": "Tayyorlanish", "call": "Test bajarilishi",
                                       "teardown": "Yakunlash / dalillarni saqlash"}.get(failed_phase)
        if stage:
            lines.append(("Xato qayd etilgan qadam", stage))
        if phases.get("call", {}).get("outcome") == "passed":
            remaining = "Asosiy test qismi o‘tgan; yakunlash to‘liq muvaffaqiyatli tugamagan."
        elif failed_phase == "setup":
            remaining = "Tayyorlanish tugamagan; asosiy test qismi boshlanmagan."
        else:
            remaining = "Faqat qayd etilgan qadamlar baholanadi; keyingi qadamlarning bajarilishi tasdiqlanmagan."
        lines.append(("Bajarilmagan qamrov", remaining))
    attempt_states = attempts.get(name, {})
    if attempt_states:
        lines.append(("Urinishlar", " · ".join(
            ("Birinchi urinish" if num == 1 else "Qayta urinish") + " — " + state
            for num, state in sorted(attempt_states.items()))))
    counts = impact.get((phase.get("nodeid"), _attempt_number(result)), {})
    if counts:
        counts_text = ", ".join(f"{count} ta {kind.lower()}" for kind, count in counts.items())
        lines.append(("Shu urinishda bajarilmagan", counts_text))
    if observations:
        lines.append(("Barcha tekshirilgan qiymatlar", f"{len(observations)} ta tekshiruvning kutilgan/amaldagi qiymatlari «Texnik tafsilotlar → Qadamlar va tekshiruv dalillari» ichida."))
    return "\n\n".join(f"**{label}** — {_text(value)}" for label, value in lines)


def _technical_details(directory, result, summary, related, *, keep_failure_evidence):
    # Failure screenshot/trace stay directly accessible; logs remain collapsed.
    sources, attachments, evidence = set(), [], []
    for scope in [result, *related.values()]:
        for node in _walk(scope):
            for attachment in node.get("attachments", []):
                source = attachment.get("source")
                if source and source not in sources:
                    kind = attachment.get("type", "")
                    is_visual = kind.startswith(("image/", "video/")) or (kind == "application/zip" and "trace" in attachment.get("name", "").lower())
                    is_reference = attachment.get("name") == "trace-reference"
                    if is_visual:
                        if keep_failure_evidence:
                            evidence.append(attachment)
                    elif not is_reference or keep_failure_evidence:
                        attachments.append(attachment)
                    sources.add(source)
            node.pop("attachments", None)
    filename = result["uuid"] + "-details.txt"
    trace = result.get("statusDetails", {}).pop("trace", "")
    (directory / filename).write_text(summary + ("\n\n" + safe_text(trace) if trace else ""), encoding="utf-8")
    attachments.insert(0, {"name": "Qadamlar va tekshiruv dalillari", "source": filename, "type": "text/plain"})
    if evidence:
        result["attachments"] = evidence
    result.setdefault("steps", []).append({"name": TECHNICAL_STEP, "attachments": attachments})


def enrich_results(directory, *, started_at_ms=None, context=None):
    """Tugagan Order natijalarini taqdimot uchun boyitish; idempotent, test run emas."""
    directory = Path(directory).resolve()
    containers = {}
    for path in directory.glob("*-container.json"):
        containers[path] = json.loads(path.read_text(encoding="utf-8"))
    backup = directory.parent / f".{directory.name}-order-originals"
    changed, api_total = 0, 0
    originals = {p: json.loads(p.read_text(encoding="utf-8")) for p in directory.glob("*-result.json")}
    originals = {p: r for p, r in originals.items() if r.get("fullName", "").startswith(PREFIX)
                 and (started_at_ms is None or r.get("start", 0) >= started_at_ms)}
    attempts, impact = context or _run_context(directory, originals.values())
    for path, original in originals.items():
        if any(step.get("name") == TECHNICAL_STEP for step in original.get("steps", [])):
            continue
        group, test = _identity(original["fullName"])
        spec = SPECS.get((group, test))
        if spec is None:
            continue
        result = deepcopy(original)
        related = {p: c for p, c in containers.items() if result["uuid"] in c.get("children", [])}
        scopes = [result, *related.values()]
        case, phase, preparation = _metadata(directory, scopes)
        phase = _phase_evidence(directory, result) or phase
        journal = []
        for scope in scopes:
            for node in _walk(scope):
                for a in node.get("attachments", []):
                    if a.get("name") == "API response":
                        data = _read_attachment(directory, a)
                        if isinstance(data, dict):
                            journal.append({"step": safe_text(node.get("name", "Tayyorlov")),
                                            **{k: safe_payload(data.get(k)) for k in ("method", "endpoint", "status")}})
        # API ilovalari faqat o‘qilganidan so‘ng taqdimotdan olinadi; diskdagi dalil qoladi.
        for scope_path, scope in [(path, result), *related.items()]:
            edited = False
            for node in _walk(scope):
                details = node.get("statusDetails", {})
                for key in ("message", "trace"):
                    if key in details:
                        safe = safe_text(details[key])
                        if safe != details[key]:
                            details[key] = safe
                            edited = True
                attachments = node.get("attachments", [])
                kept = [a for a in attachments if a.get("name") != "API response" or not isinstance(_read_attachment(directory, a), dict)]
                if kept != attachments:
                    node["attachments"] = kept
                    edited = True
            if edited and scope_path != path: _backup_write(scope_path, scope, backup)
        if journal:
            filename = f"{result['uuid']}-order-api-journal.json"
            (directory / filename).write_text(json.dumps(journal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result.setdefault("attachments", []).insert(0, {"name": f"API so‘rovlar jurnali ({len(journal)} ta)", "source": filename, "type": "application/json"})
        # Runtime retains original traces only for failures or interrupted execution.
        keep_failure_evidence = result.get("status") in {"failed", "broken"} or phase.get("status") == "interrupted"
        for scope in scopes if keep_failure_evidence else []:
            for node in _walk(scope):
                for attachment in list(node.get("attachments", [])):
                    if attachment.get("name") != "trace-reference": continue
                    reference = _read_attachment(directory, attachment)
                    if not isinstance(reference, dict): continue
                    root = Path(__file__).resolve().parents[4]
                    trace = (root / reference.get("path", "")).resolve()
                    if not trace.is_relative_to(root / "test-results/runs") or trace.suffix != ".zip" or not trace.is_file(): continue
                    filename = f"{result['uuid']}-order-trace.zip"
                    if not (directory / filename).exists(): shutil.copy2(trace, directory / filename)
                    attachments = result.setdefault("attachments", [])
                    if not any(a.get("source") == filename for a in attachments):
                        attachments.append({"name": "Playwright trace — UI qadamlar dalili", "source": filename, "type": "application/zip"})
        rerun = _attempt_number(result) == 2 and "call" in phase.get("phases", {})
        result["name"] = order_report_title(group, test, rerun=rerun)
        result.pop("descriptionHtml", None)
        detail = _markdown(_description(result, spec, case, phase, preparation, len(journal)))
        result["description"] = _qa_summary(result, spec, case, phase, attempts, impact, preparation)
        recorded_steps = _recorded_steps(result, related)
        # Containers may be shared by several attempts: keep their evidence available
        # until every test has collected its own technical details.
        _technical_details(directory, result, detail, deepcopy(related), keep_failure_evidence=keep_failure_evidence)
        steps_file = f"{result['uuid']}-allure-steps.txt"
        steps_text = "\n".join(
            f"{stage} {number} | {status} | {duration} | {safe_text(str(name))}"
            for stage, number, name, status, duration in recorded_steps
        ) or "Bu test uchun bajarilgan Allure qadamlari qayd etilmagan."
        (directory / steps_file).write_text(
            "Qayd etilgan Allure qadamlari\nIchki qadam vaqti ota qadam vaqtiga kiradi.\n"
            "Umumiy fixture bir nechta testga tegishli bo‘lishi mumkin; bu qayta bajarilganini anglatmaydi.\n"
            "Boshlanish vaqti yo‘q fixturelar faza oxirida; ularning vaqt bo‘yicha tartibi noma’lum.\n\n"
            + steps_text + "\n", encoding="utf-8")
        result.setdefault("attachments", []).append({
            "name": "Allure qadamlari", "source": steps_file, "type": "text/plain",
        })
        # Native plain-text fallback also works where Description's blob iframe does not render.
        summary_file = f"{result['uuid']}-qa-summary.txt"
        (directory / summary_file).write_text(result["description"].replace("**", "") + "\n", encoding="utf-8")
        result.setdefault("attachments", []).insert(0, {
            "name": "Qisqa QA natijasi", "source": summary_file, "type": "text/plain",
        })
        labels = [l for l in result.get("labels", []) if l["name"] not in {"epic", "feature", "story"}]
        result["labels"] = labels + [{"name": "epic", "value": "Regression"},
            {"name": "feature", "value": GROUP_FEATURES[group]},
            {"name": "story", "value": order_report_section(group, test)}]
        links = result.setdefault("links", [])
        for link in _links(case, preparation):
            if not any(existing.get("url") == link["url"] for existing in links): links.append(link)
        _backup_write(path, result, backup)
        changed += 1
        api_total += len(journal)
    # All fixture attachments have been copied to their matching attempts above.
    # Keep the native step tree, but do not re-expose PASS screenshots/traces.
    presented = {r["uuid"] for r in originals.values() if _identity(r["fullName"]) in SPECS}
    for path, container in containers.items():
        if set(container.get("children", [])) <= presented:
            edited = False
            for stage in _walk(container):
                if "attachments" in stage:
                    stage.pop("attachments")
                    edited = True
            if edited:
                _backup_write(path, container, backup)
    return {"updated_tests": changed, "grouped_api_attachments": api_total, "backup": str(backup)}


def main():
    parser = argparse.ArgumentParser(description="Tayyor Order Allure natijalarini tushunarli ko‘rinishga keltirish; test ishlatmaydi")
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    print(json.dumps(enrich_results(args.results), ensure_ascii=False))


if __name__ == "__main__":
    main()
