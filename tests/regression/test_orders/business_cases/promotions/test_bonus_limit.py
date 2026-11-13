"""Ikki klient bitta umumiy bonus limitini sarflashi va qayta ishlatishi.

Qoida manual 465/470/476/485 dalillariga tayangan. Ownprice/clients/action;
API biznes tekshiruvida ishlatilmaydi. Har saqlash o‘z runner qadamidir.
"""
from decimal import Decimal
import json
import re
from urllib.parse import urlsplit, unquote
import allure
import pytest
from playwright.sync_api import expect
from tests.regression.test_orders.helpers.flows.order import existing_order, open_new_order, select_order_product, save_order_by_reference, reopen_order_goods, promotion_card
from tests.regression.test_orders.helpers.flows.stock import read_stock
from tests.regression.test_orders.helpers.flows.order_status import cancel_order
from utils.base_pages.auto_base_page import AutoBasePage
from tests.regression.helpers.retry.checkpoints import reuse, verified
from tests.regression.helpers.preparation.stock_guard import require_available

pytestmark = [pytest.mark.regression, pytest.mark.order_positive]


def _number(value):
    return Decimal(re.sub(r"\s+", "", str(value)).replace(",", "."))


def _remember(case, directory):
    path = directory / "bonus-limit-chain.json"
    content = json.dumps(case.promotions, ensure_ascii=False, indent=2) + "\n"
    temp = path.with_suffix(".tmp")
    temp.write_text(content)
    temp.replace(path)
    allure.attach(content, "Umumiy bonus limiti zanjiri", allure.attachment_type.JSON)


def _counter(case, expected):
    """Faqat aynan shu aksiya va bonus SKU counterini UI’dan tekshirish."""
    page, base = case.page, AutoBasePage(case.page)
    action_id = str(case.promotions["bonus"]["action_id"])
    if not action_id.isdigit():
        raise ValueError("Aksiya IDsi raqam bo‘lishi kerak")
    with allure.step("Aynan test aksiyasining View formasini ochish"):
        base.open_route(f"anor/mcg/action_view?action_id={action_id}",
                        heading="Акция (просмотр)", timeout=45_000)
        base.text(case.promotions["bonus"]["name"], include_input_values=True)
    with allure.step(f"Umumiy limit 2; berilgan bonus {expected} dona ekanini tekshirish"):
        base.tab(name="Лимит бонуса")
        base.text("Кол-во выданного бонуса", "Лимит")
        grid = page.locator("smt-data-table:visible").filter(has_text="Кол-во выданного бонуса")
        expect(grid).to_have_count(1)
        row = base.grid(case.bonus_product, "Товар", root=grid)
        expect(grid.locator(".smt-data-row")).to_have_count(1)
        labels = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
        observed = []
        for label, value in (("Кол-во выданного бонуса", expected), ("Лимит", 2)):
            if labels.count(label) != 1:
                raise AssertionError(f"Bonus limitida yagona ustun kerak: {label}; {labels}")
            actual = _number(base.grid_cell(row, labels.index(label), return_value=True))
            case.check(f"Umumiy aksiya: {label}", Decimal(value), actual)
            observed.append(actual)
        allure.attach(f"Aksiya ID {action_id} · {case.bonus_product}",
                      name=f"Berilgan bonus / limit: {observed[0]:f}/{observed[1]:f}",
                      attachment_type=allure.attachment_type.TEXT)


def _saved_order(case, quantity, status, bonus_expected):
    """Saqlangan ID, klient, joriy miqdor, pul va haqiqiy bonus tarkibi."""
    page, base = case.page, AutoBasePage(case.page)
    amount = Decimal(quantity) * Decimal("7000")
    for label, value in (("ИД заказа", case.orders[-1]), ("Клиент", case.client), ("Статус", status), ("Тип оплаты", "Наличные деньги")):
        base.form_view(label=label, expect_value=value)
    case.check("Saqlangan order summasi", amount, _number(base.form_view(label="Сумма заказа", return_value=True)))
    grid = page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.product, case.price_type, "Основной склад", root=grid)
    labels = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, value in (("Количество продажи", quantity), ("Цена", 7000), ("Итого", amount)):
        case.check(f"Saqlangan mahsulot: {label}", Decimal(value), _number(base.grid_cell(row, labels.index(label), return_value=True)))
    if not bonus_expected:
        expect(page.get_by_role("tab", name="Акция", exact=True)).to_have_count(0)
        case.check("Saqlangan bonus bo‘limi soni", 0, page.get_by_role("tab", name="Акция", exact=True).count())
        return
    base.tab(name="Акция")
    grid = page.locator("smt-table:visible").last
    expect(grid.locator(".smt-data-row")).to_have_count(1)
    row = base.grid(case.bonus_product, case.promotions["bonus"]["name"], root=grid)
    labels = [" ".join(v.split()) for v in grid.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
    for label, value in (("Количество продажи", 1), ("Цена", 0), ("Итого", 0)):
        case.check(f"Saqlangan bonus: {label}", Decimal(value), _number(base.grid_cell(row, labels.index(label), return_value=True)))


def run_quota_order(case, directory, *, key, quantity, used_before, used_after, bonus_expected, status, initial_stock=False):
    """1. Oldingi counter. 2. Own klient orderi. 3. Taklif va Save.
    4. View/Edit persistence. 5. Shu aksiya counteri. Expectedlar runnerda ochiq.
    """
    page, base = case.page, AutoBasePage(case.page)
    case.price_type = case.promotions["prices"]["quota"]["name"]
    case.checkpoint()
    with allure.step("1 - Oddiy orderlar ro‘yxatidan boshlash"):
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
    identity = existing_order(case)
    if not identity:
        if initial_stock:
            with allure.step("Butun ketma-ketlik uchun 40 dona mahsulot va 2 dona bonus mavjud"):
                goods = read_stock(case, "Основной склад")
                bonus = read_stock(case, "Основной склад", product_id=case.baseline["product_id_usa"])
                case.check("Asosiy mahsulotning erkin qoldig‘i kamida 40", True, goods["available"] >= 40)
                case.check("Bonus mahsulotining erkin qoldig‘i kamida 2", True, bonus["available"] >= 2)
        _counter(case, used_before)
        require_available(case, quantity, bonus_quantity=1 if bonus_expected else 0)
        open_new_order(page)
        with allure.step(f"2 - {case.client}: {quantity} dona mahsulot"):
            base.b_input(label="Рабочая зона", expect_value=case.room)
            base.b_input(label="Штат", expect_value=case.staff)
            base.b_input(label="Клиент", value=case.client, clear=True)
            base.click(name="Далее", exact=True)
            select_order_product(page, case.product, case.price_type)
            base.input(label="Кол-во", value=str(quantity), press_tab=True)
        with allure.step("3 - Global limitga mos bonus taklifi"):
            # Fresh Add lazily fetches the offers when this tab is opened.
            with page.expect_response(lambda response: response.request.method == "POST" and unquote(urlsplit(response.url).path).endswith("/order/order+add:find_extra_data")) as offers:
                base.tab(name=re.compile(r"^Акции"))
            case.check("Aksiya ro‘yxati yuklash javobi", 200, offers.value.status)
            offers.value.finished()
            base.wait_for_loader()
            card = page.locator("article").filter(has=page.get_by_text(case.promotions["bonus"]["name"], exact=True))
            if bonus_expected:
                card = promotion_card(page, case.promotions["bonus"]["name"])
                base.checkbox(locator=card.get_by_role("switch"), expect_checked=False)
                row = base.grid(case.bonus_product, "Товар", root=card)
                headers = [" ".join(v.split()) for v in card.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
                if headers.count("Значение") != 1:
                    raise AssertionError(f"Bonus previewda Значение ustuni yagona emas: {headers}")
                case.check("Limitdan oshmagan taklif: bonus 1", Decimal(1), _number(base.grid_cell(row, headers.index("Значение"), return_value=True)))
                base.checkbox(locator=card.get_by_role("switch"), checked=True)
            else:
                expect(card).to_have_count(0)
                case.check("Limit tugagach shu aksiya taklifi soni", 0, card.count())
            expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1 if bonus_expected else 0)
        with allure.step("4 - To‘lov turi, summa va saqlash statusi"):
            base.click(name="Далее", exact=True)
            base.b_input(label="Тип оплаты", value="Наличные деньги", clear=True)
            base.input(label="ИТОГО", expect_value=str(quantity * 7000))
            base.input(label="Сумма скидки/наценки", expect_value="0")
            base.input(label="Номер товарно-транспортной накладной", value=case.reference)
            base.ui_select(label="Статус", value=status)
        identity = save_order_by_reference(page, case.reference)
    case.remember_order(identity)
    case.promotions["orders"][key] = {"id": identity, "client": case.client, "reference": case.reference, "quantity": quantity, "status": status, "stage": "saved_unverified"}
    _remember(case, directory)
    with allure.step("5 - Saqlangan order qiymatlari va bonus tarkibi"):
        _saved_order(case, quantity, status, bonus_expected)
    # Edit fetches offers while opening, before the user opens the Actions tab.
    with page.expect_response(lambda response: response.request.method == "POST" and unquote(urlsplit(response.url).path).endswith("/order/order+edit:find_extra_data")) as reopened_offers:
        reopen_order_goods(page)
    case.check("Qayta ochilgan aksiya ro‘yxati yuklash javobi", 200, reopened_offers.value.status)
    reopened_offers.value.finished()
    base.wait_for_loader()
    with allure.step("6 - Qayta ochilganda mahsulot, narx turi va bonus saqlangan"):
        base.input(label="Кол-во", expect_value=str(quantity))
        row = page.locator(".smt-data-row:visible").filter(has=page.get_by_text(case.price_type, exact=True))
        expect(row).to_have_count(1)
        base.b_input(label="Название", expect_value=case.product)
        base.text(case.price_type, "Основной склад", root=row)
        base.tab(name=re.compile(r"^Акции"))
        base.wait_for_loader()
        reopened_card = page.locator("article").filter(has=page.get_by_text(case.promotions["bonus"]["name"], exact=True))
        if bonus_expected:
            reopened_card = promotion_card(page, case.promotions["bonus"]["name"])
            base.checkbox(locator=reopened_card.get_by_role("switch"), expect_checked=True)
            bonus_row = base.grid(case.bonus_product, "Товар", root=reopened_card)
            headers = [" ".join(v.split()) for v in reopened_card.locator(".smt-grid-header [data-smt-col-key]").all_text_contents()]
            if headers.count("Значение") != 1:
                raise AssertionError(f"Qayta ochilgan bonusda Значение ustuni yagona emas: {headers}")
            case.check("Qayta ochilgan bonus miqdori", Decimal(1), _number(base.grid_cell(bonus_row, headers.index("Значение"), return_value=True)))
        else:
            expect(reopened_card).to_have_count(0)
            case.check("Qayta ochilganda tugagan aksiya taklifi soni", 0, reopened_card.count())
        expect(page.locator("article [role='switch'][aria-checked='true']")).to_have_count(1 if bonus_expected else 0)
        base.click(name="Далее", exact=True)
        base.b_input(label="Тип оплаты", expect_value="Наличные деньги")
        base.input(label="ИТОГО", expect_value=str(quantity * 7000))
    _counter(case, used_after)
    case.promotions["orders"][key]["stage"] = "verified"
    _remember(case, directory)


def run_release_limit(case, directory):
    """1. Used2. 2. Birinchi klientning own orderini bekor qilish. 3. Used1."""
    data = case.promotions
    original = data["orders"]["first"]
    if original["client"] != case.client or original["stage"] != "verified":
        raise AssertionError("Bekor qilish uchun aynan birinchi klientning tekshirilgan orderi kerak")
    case.reference = original["reference"]
    case.remember_order(original["id"])
    with allure.step("1 - Order listdan boshlash"):
        base = AutoBasePage(case.page)
        base.navigate_to(tab="Продажа", name="Заказы")
        base.expect_page(heading="Заказы", url="order_list")
    if not reuse("bonus_before_cancel"):
        _counter(case, 2)
        verified("bonus_before_cancel")
    cancel_order(case.page, order_id=original["id"], client=case.client, amount="70000")
    original.update(status="Отменен", stage="cancelled_view_verified")
    _remember(case, directory)
    _counter(case, 1)
    original["stage"] = "cancelled_limit_released"
    _remember(case, directory)
