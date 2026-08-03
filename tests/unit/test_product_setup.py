from tests.smoke.test_setup import test_21_init_balance as test_init_balance
from tests.smoke.test_setup import test_18_product as test_product


def test_setup_products_use_separate_uzs_and_usd_price_types(monkeypatch):
    calls = []

    def fake_create(page, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(
        test_product,
        "_create_product_with_price",
        fake_create,
    )

    test_product.run_product(object(), "900184")
    test_product.run_product_usa(object(), "900184")

    assert calls == [
        {
            "product_name": "product-pw900184",
            "product_code": "c_p_pw900184",
            "sector_name": "sector-pw900184",
            "price_type_name": "Price Type UZB-pw900184",
            "price": "7000",
            "price_label": "UZS",
        },
        {
            "product_name": "product-usa-pw900184",
            "product_code": "c_p_usa_pw900184",
            "sector_name": "sector-pw900184",
            "price_type_name": "Price Type USA-pw900184",
            "price": "1",
            "price_label": "USD",
        },
    ]


def test_setup_products_receive_separate_uzs_and_usd_balances(monkeypatch):
    calls = []

    def fake_create(page, **kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(
        test_init_balance,
        "_create_and_post_init_balance",
        fake_create,
    )

    test_init_balance.run_init_balance(object(), "900184")
    test_init_balance.run_init_balance_usa(object(), "900184")

    assert calls == [
        {
            "document_number": "900184",
            "currency_name": "Узбекский сум",
            "product_name": "product-pw900184",
            "product_code": "c_p_pw900184",
            "quantity": "100",
            "price": "5000",
            "balance_label": "UZS",
            "expected_posting_amount": "500 000",
        },
        {
            "document_number": "1900184",
            "currency_name": "Доллар США",
            "product_name": "product-usa-pw900184",
            "product_code": "c_p_usa_pw900184",
            "quantity": "100",
            "price": "1",
            "balance_label": "USD",
        },
    ]
