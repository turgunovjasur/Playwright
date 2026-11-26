"""Order testlari uchun exact mahsulot/ombor qoldig‘ini UI’dan o‘qish."""
from decimal import Decimal
from urllib.parse import urlsplit, unquote
import allure
from playwright.sync_api import expect
from tests.regression.test_orders.helpers.flows.settlement import _columns
from utils.base_pages import A2_DOCUMENT_TIMEOUT_MS
from tests.regression.test_orders.helpers.navigation import OrderPage


def read_stock(case, warehouse, *, product_id=None):
    """Observe this UI's balance response to distinguish a settled zero from loading."""
    product_id = str(product_id or case.baseline["product_id"])
    observed = {}
    def capture(response):
        if not unquote(urlsplit(response.url).path).endswith("/anor/mr/product/inventory_view:balances"):
            return
        try:
            if str(response.request.post_data_json.get("d", {}).get("product_id")) == product_id:
                observed.clear()
                if response.status == 200:
                    observed.update(response.json())
                    observed["columns"] = response.request.post_data_json.get("p", {}).get("column", [])
        except (ValueError, TypeError, AttributeError):
            observed.clear()
    case.page.on("response", capture)
    try:
        return _read_stock(case, warehouse, product_id=product_id, observed=observed)
    finally:
        case.page.remove_listener("response", capture)


def _read_stock(case, warehouse, *, product_id, observed):
    """Exact SKU viewdan ombordagi barcha ko'rinadigan lotlarni yig'adi.

    Pagination to'liq ochilmasa sonlarni qisman snapshot sifatida qaytarmaydi.
    Bitta consumer uchun local domain readback; umumiy UI primitive emas.
    """
    page, base = case.page, OrderPage(case.page)
    product_id = str(product_id or case.baseline["product_id"])
    if not product_id.isdigit():
        raise ValueError("Stock readback uchun baseline product_id raqam bo'lishi kerak")
    with allure.step("Setup mahsuloti viewini aniq ID bilan ochish"):
        # This full document navigation also downloads the A2 module graph.
        base.open_route(f"anor/mr/product/inventory_view?product_id={product_id}",
                        heading="ТМЦ (просмотр)", timeout=A2_DOCUMENT_TIMEOUT_MS)
    with allure.step("Mahsulotning ombor qoldiqlarini ochish"):
        base.tab(name="Остатки")
        base.text("Доступный остаток", "Забронировано", "В наличии")
    with allure.step(f"{warehouse}: mavjud, bronlangan va dostupni barcha lotlar bo'yicha o'qish"):
        fields = {"warehouse": "Склад", "physical": "В наличии", "booked": "Забронировано", "available": "Доступный остаток"}
        cols = _columns(page, fields)
        if page.get_by_role("button", name="Next pages", exact=True).is_enabled():
            base.grid_controller(expand="1000")
        expect(page.get_by_role("button", name="Next pages", exact=True)).to_be_disabled()
        expect(page.get_by_role("button", name="Previous pages", exact=True)).to_be_disabled()
        grid = page.locator("smt-data-table:visible").first
        # Bir omborda bir nechta lot qatori bo'lishi mumkin: faqat mavjudlikni
        # kutamiz, barcha qatorlarni pastda yig'amiz; unique row talab qilinmaydi.
        warehouse_rows = grid.locator(".smt-data-row").filter(has=page.get_by_text(warehouse, exact=True))
        base.wait_for_loader()
        if not warehouse_rows.count():
            rows = grid.locator(".smt-data-row")
            if observed.get("count") == 0 and observed.get("data") == []:
                expect(rows).to_have_count(0)
                base.grid(state="empty", root=grid)
                return {key: Decimal("0") for key in ("physical", "booked", "available")}
            balances = observed.get("data", [])
            columns = observed.get("columns", [])
            if "warehouse_name" in columns and observed.get("count") == len(balances):
                index = columns.index("warehouse_name")
                if all(row[index] != warehouse for row in balances):
                    expect(rows).to_have_count(len(balances))
                    return {key: Decimal("0") for key in ("physical", "booked", "available")}
            expect(warehouse_rows.first).to_be_visible()
        result = {key: Decimal("0") for key in ("physical", "booked", "available")}
        matched = 0
        for row in grid.locator(".smt-data-row").all():
            if base.grid_cell(row, cols["warehouse"], return_value=True).strip() != warehouse:
                continue
            matched += 1
            for key in result:
                value = base.grid_cell(row, cols[key], return_value=True, remove_spaces=True)
                result[key] += Decimal(value.replace(",", "."))
        if not matched:
            raise AssertionError(f"{warehouse} uchun setup mahsulotining qoldiq qatori topilmadi")
        return result

