"""Majburiy aksiya guruhi: alohida narx turlari va ikkita aniq bonus.

API faqat tayyorlovda. UI biznes natijasi consumer testlarda tekshiriladi.
Har run o'z narx turlarini oladi: retained majburiy aksiyalar keyingi running
bazaviy narx turida ishlamaydi. Shared setup narxlari almashtirilmaydi.
"""
from copy import deepcopy
from decimal import Decimal
import json
from tests.regression.retry.state import stable_uuid as uuid4

import allure
import pytest

from tests.api.client import APIError, positive_id, require_fields
from tests.api.promotion import verify_promotion
from tests.api.state import CONTRACTS
from tests.regression.test_orders.auth_recovery import RegressionSetupState

pytestmark = [pytest.mark.regression, pytest.mark.order_positive, allure.feature('Majburiy aksiyalar')]


def _persist(data, directory):
    path = directory / 'mandatory-setup.json'
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def run_prepare_prices(baseline, data, directory):
    """1. Xona payment/price bog'lanishlarini o'qish.
    2. Ikkita yangi UZS narx turi yaratish va xonaga ulanganini tekshirish.
    3. Faqat yangi narx turlariga 7 000 narx qo'yish; eski narxlar saqlanadi.
    """
    data.clear()
    data.update(status='process', run_id=uuid4("mandatory_setup").hex[:12], url=baseline['url'], filial_id=str(baseline['filial_id']), prices={}, actions={}, retention='retained')
    state = RegressionSetupState(directory / 'state.json', deepcopy(baseline))
    try:
        api = state.user()
        with allure.step('1 - Xonadagi to‘lov turlari va mavjud narxlarni tekshirish'):
            payments = api.table('anor/mrf/room_attachment:table_payment_type', ['payment_type_id', 'name'], data={'room_id': baseline['room_id'], 'attached': 'Y'})
            data['payments'] = {}
            for key, name in (('bank', 'Перечисление'), ('terminal', 'Терминал')):
                found = [row for row in payments if row['name'] == name]
                if len(found) != 1:
                    raise APIError(f'Xonada yagona {name} to‘lov turi kerak')
                data['payments'][key] = {'id': positive_id(found[0]['payment_type_id']), 'name': name}
            before = api.model('anor/mr/product/product_set_price', product_id=baseline['product_id'])['prices']
            old_prices = {(str(row[0]), str(row[3])): Decimal(str(row[5])) for row in before if row[5] not in (None, '')}
            memberships = api.table('anor/mrf/room_attachment:table_price_type', ['price_type_id'], data={'room_id': baseline['room_id'], 'attached': 'Y'})
            before_ids = {str(row['price_type_id']) for row in memberships}
            _persist(data, directory)
        for key in ('bank', 'terminal'):
            with allure.step(f'2 - {key} aksiya uchun alohida UZS narx turini yaratish'):
                payload = state.payload('price_type_uzb')
                payload.update(name=f'Order {key} UZS-pw{state.code}-{data["run_id"]}', code=f'og-{key}-{data["run_id"]}')
                result = api.call(CONTRACTS['price_type_uzb']['endpoint'], payload)
                identity = positive_id(result['price_type_id'])
                data['prices'][key] = {'id': identity, 'name': payload['name'], 'unit_price': '7000'}
                _persist(data, directory)
                model = api.model('anor/mkr/price_type_view', price_type_id=identity)
                require_fields(model, name=payload['name'], currency_name='Узбекский сум', price_type_kind_name='Цена продажи', state='A')
            with allure.step(f'3 - {key} yangi narx turiga 7 000 qo‘yish va qayta o‘qish'):
                api.call('anor/mr/product/product_set_price$save', {'product_id': baseline['product_id'], 'prices': [{'price_type_id': identity, 'card_id': '-1', 'price': '7000'}]})
                rows = api.model('anor/mr/product/product_set_price', product_id=baseline['product_id'])['prices']
                actual = {(str(row[0]), str(row[3])): Decimal(str(row[5])) for row in rows if row[5] not in (None, '')}
                if actual.get((identity, '-1')) != Decimal('7000') or any(actual.get(k) != v for k, v in old_prices.items()):
                    raise APIError('Yangi narx saqlanmagan yoki mavjud narx o‘zgargan')
                old_prices = actual
        attached = api.table('anor/mrf/room_attachment:table_price_type', ['price_type_id'], data={'room_id': baseline['room_id'], 'attached': 'Y'})
        expected_ids = before_ids | {row['id'] for row in data['prices'].values()}
        if {str(row['price_type_id']) for row in attached} != expected_ids:
            raise APIError('Xona narx bog‘lanishlari eski ro‘yxat + ikkita yangi narxga teng emas')
        data['status'] = 'prices_ready'
    except Exception as error:
        data.update(status='failed', error_type=type(error).__name__)
        raise
    finally:
        _persist(data, directory)
        allure.attach(json.dumps(data, ensure_ascii=False), 'Majburiy aksiya tayyorlovi', allure.attachment_type.JSON)
        state.close()


def run_prepare_action(baseline, data, directory, kind):
    """1. Yangi narx va to'lov juftligiga A10→B1 majburiy aksiya yaratish.
    2. Saved qoida, bonus, forced va price/payment/room identitylarini tekshirish.
    """
    if data.get('status') not in {'prices_ready', 'bank_ready'}:
        raise APIError('Majburiy aksiya uchun oldingi tayyorlov yakunlanmagan')
    state = RegressionSetupState(directory / 'state.json', deepcopy(baseline))
    try:
        api = state.user()
        with allure.step(f'1 - {kind}: mos payment va narx uchun A10 → B1 majburiy aksiya'):
            payload = state.payload('quantity_bonus')
            payload.update(name=f'Order mandatory {kind}-pw{state.code}-{data["run_id"]}', code=f'ogb-{kind}-{data["run_id"]}', forced='Y', price_type_id=[data['prices'][kind]['id']], payment_type_id=[data['payments'][kind]['id']])
            payload['conditions'][0]['rules'][0]['main_value'] = '10'
            reward = payload['conditions'][0]['bonuses'][0]['products'][0]
            reward.update(product_id=str(baseline['product_id_usa']), value='1')
            data['actions'][kind] = {'name': payload['name'], 'price_type_id': payload['price_type_id'][0], 'payment_type_id': payload['payment_type_id'][0], 'forced': 'Y'}
            _persist(data, directory)
            api.call(CONTRACTS['quantity_bonus']['endpoint'], payload)
            row = api.one('anor/mcg/action_list:table', ['action_id', 'name'], filters=['name', '=', payload['name']])
            identity = positive_id(row['action_id'])
            data['actions'][kind]['action_id'] = identity
            _persist(data, directory)
        with allure.step('2 - Saqlangan aksiya shartlari va izolyatsiyasini qayta o‘qish'):
            verify_promotion(api, identity, payload)
            model = api.model('anor/mcg/action+edit', action_id=identity)
            require_fields(model, forced='Y', condition_operator=payload['condition_operator'])
            # Positional model contract: captured action.html maps id/name/room_ids.
            for field, expected in (('price_types', payload['price_type_id']), ('payment_types', payload['payment_type_id']), ('rooms', payload['room_ids'])):
                if {str(row[0]) for row in model[field]} != {str(value) for value in expected}:
                    raise APIError(f'Majburiy aksiya {field} bog‘lanishi expectedga mos emas')
            data['status'] = 'bank_ready' if kind == 'bank' else 'passed'
    except Exception as error:
        data.update(status='failed', error_type=type(error).__name__)
        raise
    finally:
        _persist(data, directory)
        allure.attach(json.dumps(data, ensure_ascii=False), 'Majburiy aksiya tayyorlovi', allure.attachment_type.JSON)
        state.close()
