"""Qaytarish guruhidan oldin yetishmayotgan ombor qoldig'ini tayyorlash.

API setup 23 kontrakti bilan faqat yangi kirim qo'shiladi. Oldingi kirim,
order va rezervlar saqlanadi. Boshlang'ich va yakuniy qoldiq UI'dan olinadi.
"""
from tests.regression.helpers.retry.checkpoints import draft_or_reused_posted
from copy import deepcopy
from decimal import Decimal
import json
from tests.regression.helpers.retry.state import stable_uuid as uuid4

import allure

from tests.api.client import APIError, positive_id, require_fields
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.test_orders.helpers.flows.stock import read_stock


def run_prepare_return_stock(case, directory):
    """1. Ikkala mahsulotning joriy erkin qoldig'ini UI orqali o'qish.
    2. Tovarni 20, bonusni 2 donagacha yetkazish uchun faqat kam qismini kirim qilish.
    3. Kirim hujjati o'tkazilganini va ombor/valyutasini tasdiqlash.
    4. UI'da fizik va erkin qoldiq aynan kirim miqdoriga oshganini tekshirish.
    5. Avvalgi rezerv o'zgarmaganini tekshirish va IDlarni saqlash.

    20 dona tovar qaytarishdagi 10 dona va keyingi ikki orderdagi 5 dona uchun
    yetarli zaxira beradi. Yetarli bo'lsa yangi kirim yaratilmaydi.
    """
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {'status': 'process', 'warehouse_id': str(case.baseline['warehouse_id']),
                'warehouse': 'Основной склад', 'products': [], 'documents': [],
                'retention': 'retained'}
    case.workflow['return_stock'] = metadata
    state = RegressionSetupState(directory / 'return-stock-state.json', deepcopy(case.baseline))

    def persist():
        case.checkpoint()
        path = directory / 'return-stock-setup.json'
        path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    try:
        for kind, key, contract, minimum, currency in (
            ('Tovar', 'product_id', 'init_balance_uzb', Decimal('20'), 'Узбекский сум'),
            ('Bonus', 'product_id_usa', 'init_balance_usa', Decimal('2'), 'Доллар США'),
        ):
            product_id = str(case.baseline[key])
            with allure.step(f"1 - {kind}: ombordagi mavjud va erkin qoldiqni tekshirish"):
                before = read_stock(case, metadata['warehouse'], product_id=product_id)
                required = max(Decimal('0'), minimum - before['available'])
                product = {'kind': kind, 'product_id': product_id, 'minimum_available': str(minimum),
                           'before': {k: str(v) for k, v in before.items()}, 'added': str(required)}
                metadata['products'].append(product)
                persist()
            if required:
                api = state.user()
                payload = state.payload(contract)
                number = 'RS' + uuid4(f'stock:{product_id}').hex[:8]
                payload['balance_number'] = number
                # Alohida kartochka mavjud boshlang'ich qoldiq bilan to'qnashmaydi.
                payload['items'][0]['card_code'] = number
                payload['items'][0]['quantity'] = str(required)
                if str(payload['items'][0]['product_id']) != product_id:
                    raise APIError('Kirim kontrakti boshqa mahsulotga tegishli')
                record = {'number': number, 'product_id': product_id, 'quantity': str(required),
                          'currency': currency, 'card_code': number, 'state': 'pending'}
                metadata['documents'].append(record)
                persist()
                with allure.step(f"2 - {kind}: yetishmayotgan {required} donaga alohida kirim yaratish"):
                    state.send(api, contract, **payload)
                    route = 'anor/mkw/init_balance/init_inventory_balance_list'
                    columns = ['balance_id', 'balance_number', 'warehouse_name', 'currency_name', 'posted']
                    saved = api.one(route + ':table', columns, filters=['balance_number', '=', number])
                    require_fields(saved, posted=draft_or_reused_posted(saved), warehouse_name=metadata['warehouse'], currency_name=currency)
                    record.update(id=positive_id(saved['balance_id']), state='draft')
                    persist()
                with allure.step('3 - Aynan yangi kirimni omborga o‘tkazish'):
                    api.call(route + ':post', {'balance_id': record['id']})
                    saved = api.one(route + ':table', columns, filters=['balance_id', '=', record['id']])
                    require_fields(saved, posted='Y', balance_number=number,
                                   warehouse_name=metadata['warehouse'], currency_name=currency)
                    record['state'] = 'posted'
                    persist()
                with allure.step(f"4 - {kind}: UI'da kirim miqdori va avvalgi rezervni tekshirish"):
                    after = read_stock(case, metadata['warehouse'], product_id=product_id)
                    expected = {**before, 'physical': before['physical'] + required,
                                'available': before['available'] + required}
                    case.check(f'{kind}: kirimdan keyingi qoldiq va o‘zgarmagan rezerv', expected, after)
            else:
                after = before
            product['after'] = {k: str(v) for k, v in after.items()}
            case.check(f'{kind}: keyingi testlarga erkin qoldiq yetarli', True, after['available'] >= minimum)
            persist()
        metadata['status'] = 'passed'
    except Exception as error:
        metadata.update(status='failed', error_type=type(error).__name__)
        raise
    finally:
        try:
            persist()
            allure.attach(json.dumps(metadata, ensure_ascii=False), 'Qaytarish uchun ombor tayyorlovi', allure.attachment_type.JSON)
        finally:
            state.close()
