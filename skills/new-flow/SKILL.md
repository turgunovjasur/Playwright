---
name: new-flow
description: tests/smoke/flows ichida qayta ishlatiladigan Playwright UI flow yaratadi yoki mavjud flow'ni ajratadi. Bir xil UI ketma-ketligi bir nechta testda takrorlanganda, flow/helper ajratish yoki order flow yozish so'ralganda ishlat.
---

# Yangi Flow Funksiya Yaratish

Argument: `$ARGUMENTS` (flow nomi va qisqacha tavsif)

## Flow nima?

Flow — bu bir nechta testlarda qayta ishlatiladigan UI harakatlar ketma-ketligi.
Masalan: `authorization`, `navigate_to_menu`, `open_modal` va hokazo.

## Joylashuv

Default: `tests/smoke/flows/flow_<nomi>.py`.

Bir domain uchun bir nechta flow bo'lsa mavjud pattern bo'yicha
`tests/smoke/flows/flow_<domain>/flow_<action>.py` ishlat.

## Shablon

```python
import allure
from playwright.sync_api import Page
from utils.base_page import BasePage


def <nomi>(page: Page, **kwargs) -> None:
    """<Qisqacha tavsif>."""
    base = BasePage(page)

    with allure.step("1 - <Qadam>"):
        base.navigate_to(tab="<Tab>", name="<Menyu>")

    with allure.step("2 - <Qadam>"):
        base.expect_page(heading="<Heading>", url="<stable-url-slug>")
```

## Qoidalar

- Funksiya `Page` ni birinchi argument sifatida qabul qilsin
- Har bir muhim qadam `allure.step` bilan o'ralsin
- Legacy AngularJS/Biruni forma uchun `BasePage`, A2 Angular forma uchun
  `AngularBasePage` ishlat; ikki DOM kontraktini bitta helperda aralashtirma.
- Mavjud page-object primitive'ini raw locator yoki local wrapper bilan
  takrorlama. Raw locator faqat mos helper bo'lmagan maxsus action uchun qoladi.
- Holatni page-object asserti yoki Playwright `expect()` bilan tekshir; Python
  `assert` bilan UI holatini tekshirma.
- Flow faqat UI harakatlarni bajarsin — ma'lumot saqlash/o'qish test ichida qolsin
- Funksiya nomi `flow_` prefiksi emas, tavsifli ism bo'lsin: `authorization`, `create_room`

## Loyiha Xususiyatlari

### Order flowlarni qayta ishlatish
- Order testlari ko'p yoziladi; orderga tegishli takrorlanadigan harakatlar `tests/smoke/flows/flow_order/` ichidagi alohida flow funksiyalarga ajratilsin va yangi order case'larda shu flowlardan foydalanilsin.
- Contract testlari loyiha istisnosi: har biri alohida self-contained test faylda yoziladi va `flow_contract` ga ajratilmaydi.
- Biruni error xabarlari hamma joyda bir xil pattern bilan keladi; error kutish, text tekshirish va modal yopish umumiy flow/helper sifatida ajratilsin.
- Listlarda kerakli ustun/search yoqilmagan bo'lsa, grid setting orqali ustun va searchni yoqadigan reusable flow yozish mumkin.

## Ish tartibi

1. `$ARGUMENTS` ni o'qi — qanday flow kerak?
2. O'xshash mavjud flow larni ko'r (`tests/smoke/flows/`)
3. Legacy yoki A2 DOM kontraktini aniqlab, mos page-objectni tanla
4. Default yoki domain papkasida flow faylini yarat
5. Consumer call-site va syntaxni statik tekshir; consumer testni faqat user
   aynan `run qil` deganda ishga tushir
6. Qaysi testlarda ishlatilishini ko'rsat
