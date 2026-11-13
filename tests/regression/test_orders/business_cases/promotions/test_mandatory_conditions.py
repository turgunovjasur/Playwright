"""Payment/narx shartlari; faqat saved bonus va pul haqiqiy oracle.

Manual M-G-PAIR, 042–063 dalillari; id-115 noto'g'ri kartadagi yozuviga
moslashilmaydi. Majburiy bonus switchi qo'lda yoqilmaydi.
"""
from decimal import Decimal
import re
import allure
import pytest
from playwright.sync_api import expect

from tests.regression.test_orders.helpers.flows.order import existing_order, select_order_product, open_new_order, save_order_by_reference, save_edited_order, reopen_order_goods
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.feature('Majburiy aksiyalar')]
PAYMENT_MISMATCH = 'Типы оплат акции и тип оплаты заказа не совпадают. Хотите убрать акцию из заказа?'


def _saved_result(case, quantity, payment, action):
    """Shu fayl caselarining saved view oracle'i; expected callerda ochiq beriladi."""
    base, page = AutoBasePage(case.page), case.page
    amount = str(quantity * 7000)
    base.form_view(label='ИД заказа', expect_value=case.orders[-1])
    base.form_view(label='Клиент', expect_value=case.client)
    base.form_view(label='Тип оплаты', expect_value=payment)
    base.form_view(label='Сумма заказа', expect_value=amount, remove_spaces=True)
    case.check('Saqlangan order summasi', Decimal(amount), Decimal(base.form_view(label='Сумма заказа', return_value=True, remove_spaces=True)))
    goods = page.locator('smt-table:visible').last
    expect(goods.locator('.smt-data-row')).to_have_count(1)
    row = base.grid(case.product, root=goods)
    labels = [' '.join(v.split()) for v in goods.locator('.smt-grid-header [data-smt-col-key]').all_text_contents()]
    # View initial_quantity = Количество заказа; editable quantity = Количество продажи.
    # Source: captured order_view translation + order.html collectData r.quantity=row.full_quant.
    expect(base.grid_cell(row, labels.index('Количество продажи'))).to_have_text(str(quantity))
    case.check('Saqlangan joriy mahsulot miqdori (dona)', Decimal(quantity),
               Decimal(base.grid_cell(row, labels.index('Количество продажи'), return_value=True, remove_spaces=True)))
    expect(base.grid_cell(row, labels.index('Цена'))).to_have_text(re.compile(r'^\s*7\s*000\s*$'))
    if action is None:
        expect(page.get_by_role('tab', name='Акция', exact=True)).to_have_count(0)
        case.check('Saqlangan bonus bo‘limi soni', 0, page.get_by_role('tab', name='Акция', exact=True).count())
        return
    base.tab(name='Акция')
    grid = page.locator('smt-table:visible').last
    expect(grid.locator('.smt-data-row')).to_have_count(1)
    row = base.grid(case.bonus_product, action['name'], root=grid)
    labels = [' '.join(v.split()) for v in grid.locator('.smt-grid-header [data-smt-col-key]').all_text_contents()]
    for label, value in (('Количество продажи', '1'), ('Цена', '0'), ('Итого', '0')):
        expect(base.grid_cell(row, labels.index(label))).to_have_text(value)
        case.check(f'Bonus: {label}', Decimal(value), Decimal(base.grid_cell(row, labels.index(label), return_value=True, remove_spaces=True)))


def run_pair(case, price_kind, payment_kind, expected_action):
    """1. O'z narx turida 10 dona order yaratish.
    2. Payment tanlash; bonusni qo'lda yoqmasdan saqlash.
    3. Viewda aynan kutilgan aksiya/B1 yoki bonus yo'qligini tekshirish.
    4. Editda narx, payment, miqdor va jami saqlanishini tekshirish.
    """
    base, data = AutoBasePage(case.page), case.promotions
    price, payment = data['prices'][price_kind], data['payments'][payment_kind]
    action = data['actions'][expected_action] if expected_action else None
    case.price_type = price['name']
    case.checkpoint()
    saved_order_id = existing_order(case)
    if not saved_order_id:
        require_available(case, 10, bonus_quantity=1 if action is not None else 0)
        open_new_order(case.page)
        with allure.step('1 - Klient va mahsulotlar bosqichi'):
            base.b_input(label='Рабочая зона', expect_value=case.room)
            base.b_input(label='Штат', expect_value=case.staff)
            base.b_input(label='Клиент', value=case.client, clear=True)
            base.click(name='Далее', exact=True)
            base.text('Название', 'Кол-во')
        with allure.step(f'2 - 10 dona; narx turi {price["name"]}; dona narxi 7 000'):
            select_order_product(case.page, case.product, price['name'])
            base.input(label='Кол-во', value='10', press_tab=True)
            goods_row = case.page.locator('.smt-data-row').filter(has=case.page.get_by_text(price['name'], exact=True))
            expect(goods_row).to_have_count(1)
            expect(goods_row.locator('[data-smt-col-key=price]')).to_have_text(re.compile(r'^\s*7\s*000\s*$'))
        with allure.step('3 - Yakunlash bosqichi va payment tanlash'):
            base.click(name='Далее', exact=True)
            base.b_input(label='Тип оплаты', value=payment['name'], clear=True)
            base.input(label='ИТОГО', expect_value='70000')
            base.input(label='Номер товарно-транспортной накладной', value=case.reference)
            base.ui_select(label='Статус', value='Черновик')
        with allure.step('Majburiy aksiyalarni ochish; bonusni qo‘lda yoqmasdan qayta hisoblash'):
            base.click(name='Назад', exact=True)
            base.tab(name=re.compile(r'^Акции'))
            if action is not None:
                base.text(action['name'])
            base.tab(name='Товар')
        with allure.step('Qayta hisoblangan orderning yakunlash bosqichi'):
            base.click(name='Далее', exact=True)
            base.input(label='ИТОГО', expect_value='70000')
            base.b_input(label='Тип оплаты', expect_value=payment['name'])
        saved_order_id = save_order_by_reference(case.page, case.reference)
    case.remember_order(saved_order_id)
    with allure.step('4 - Saqlangan pul va haqiqiy bonus tarkibi'):
        _saved_result(case, 10, payment['name'], action)
    reopen_order_goods(case.page)
    with allure.step('5 - Qayta ochilganda narx turi va miqdor saqlangan'):
        base.text(price['name'], 'Основной склад', root=case.page.locator('.smt-data-row:visible').filter(has=case.page.get_by_text(price['name'], exact=True)))
        base.input(label='Кол-во', expect_value='10')
    with allure.step('6 - Qayta ochilgan yakunlashda payment va jami'):
        base.click(name='Далее', exact=True)
        base.b_input(label='Тип оплаты', expect_value=payment['name'])
        base.input(label='ИТОГО', expect_value='70000')


def run_payment_change(case):
    """1. Bank/P1 bilan saqlangan B1 order.
    2. Terminalga o'tish, ogohlantirishda Ha: saved bonus0.
    3. Bankka qaytish: saved B1, jami 70 000 va o'sha order ID.
    """
    run_pair(case, 'bank', 'bank', 'bank')
    base, data = AutoBasePage(case.page), case.promotions
    original_id = case.orders[-1]
    with allure.step('7 - Paymentni Terminalga almashtirib eski bonusni olib tashlash'):
        base.b_input(label='Тип оплаты', value=data['payments']['terminal']['name'], clear=True, stop_after_select=True)
        base.confirm_biruni(PAYMENT_MISMATCH)
        base.b_input(label='Тип оплаты', expect_value=data['payments']['terminal']['name'])
        base.input(label='ИТОГО', expect_value='70000')
    saved_id = save_edited_order(case.page, original_id, case.reference)
    case.check('Payment almashtirilganda order ID saqlanadi', original_id, saved_id)
    with allure.step('8 - Terminal/P1 saqlangan orderda bonus yo‘q'):
        _saved_result(case, 10, data['payments']['terminal']['name'], None)
    reopen_order_goods(case.page)
    with allure.step('9 - Bankka qaytib yakunlash'):
        base.click(name='Далее', exact=True)
        base.b_input(label='Тип оплаты', value=data['payments']['bank']['name'], clear=True)
    saved_id = save_edited_order(case.page, original_id, case.reference)
    case.check('Bankka qaytganda order ID saqlanadi', original_id, saved_id)
    with allure.step('10 - Mos payment qaytganda B1 avtomatik qaytgan'):
        _saved_result(case, 10, data['payments']['bank']['name'], data['actions']['bank'])


def run_threshold(case):
    """1. Majburiy Bank/P1 A10→B1 order.
    2. Miqdor 9: saved 63 000, bonus yo'q.
    3. Miqdor 10: saved 70 000, B1 qaytadi; bir xil order ID.

    A20 uchun B2 taxmin qilinmaydi; ko'paytirish alohida konfiguratsiya talab qiladi.
    """
    run_pair(case, 'bank', 'bank', 'bank')
    base, data = AutoBasePage(case.page), case.promotions
    original_id = case.orders[-1]
    with allure.step('7 - Tovar bosqichiga qaytish'):
        base.click(name='Назад', exact=True)
        base.text('Название', 'Кол-во')
    for quantity, action in ((9, None), (10, data['actions']['bank'])):
        with allure.step(f'Miqdorni {quantity} qilish va jami {quantity * 7000} ni tekshirish'):
            base.input(label='Кол-во', value=str(quantity), press_tab=True)
            base.click(name='Далее', exact=True)
            base.input(label='ИТОГО', expect_value=str(quantity * 7000))
        saved_id = save_edited_order(case.page, original_id, case.reference)
        case.check(f'{quantity} dona holatida order ID', original_id, saved_id)
        with allure.step(f'{quantity} dona saqlanganda bonus va jami'):
            _saved_result(case, quantity, data['payments']['bank']['name'], action)
        reopen_order_goods(case.page)
        base.input(label='Кол-во', expect_value=str(quantity))


def run_price_change(case):
    """1. Bank/P1 saved B1. 2. P2: bonus yo'q. 3. P1: B1 qaytadi.

    Payment Bank va narx 7 000 saqlanadi; faqat narx turi o'zgaradi.
    Har bosqich bir xil order IDga saqlanadi va view/editdan tekshiriladi.
    """
    run_pair(case, 'bank', 'bank', 'bank')
    base, data = AutoBasePage(case.page), case.promotions
    original_id = case.orders[-1]
    with allure.step('7 - Narx turini almashtirish uchun tovarlar bosqichini ochish'):
        base.click(name='Назад', exact=True)
        base.text('Название', 'Кол-во')
    for kind, action in (('terminal', None), ('bank', data['actions']['bank'])):
        price = data['prices'][kind]
        with allure.step(f'Narx turini {price["name"]} ga almashtirish'):
            # Lookup matches the same product in the new price variant.
            base.b_input(label='Название', value=case.product, option_contains=(price['name'], 'Основной склад'), exact=True, clear=True)
            if kind == 'terminal':
                # Changing the saved action's price type opens this notice on the goods step.
                # Acknowledge it before interacting with the underlying form.
                with allure.step('Narx o‘zgargani uchun «Акция изменена!» xabarini tekshirish va yopish'):
                    base.close_biruni_alert('H02-ANOR279-009', 'Акция изменена!')
            goods_row = case.page.locator('.smt-data-row').filter(has=case.page.get_by_text(price['name'], exact=True))
            expect(goods_row).to_have_count(1)
            expect(goods_row.locator('[data-smt-col-key=price]')).to_have_text(re.compile(r'^\s*7\s*000\s*$'))
            base.input(label='Кол-во', expect_value='10')
            case.price_type = price['name']
            case.checkpoint()
        with allure.step('Bank payment va 70 000 jami saqlangan yakunlash bosqichi'):
            base.click(name='Далее', exact=True)
            base.b_input(label='Тип оплаты', expect_value=data['payments']['bank']['name'])
            base.input(label='ИТОГО', expect_value='70000')
        saved_id = save_edited_order(case.page, original_id, case.reference)
        case.check('Narx turi almashtirilganda order ID', original_id, saved_id)
        with allure.step('Tanlangan narx turiga mos saqlangan bonus tarkibi'):
            _saved_result(case, 10, data['payments']['bank']['name'], action)
        reopen_order_goods(case.page)
        base.text(price['name'], 'Основной склад', root=case.page.locator('.smt-data-row:visible').filter(has=case.page.get_by_text(price['name'], exact=True)))
