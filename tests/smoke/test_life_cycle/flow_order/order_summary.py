"""Order final summary jadvalidagi kategoriya miqdori katagini topish."""

import re

from playwright.sync_api import Locator, Page, expect


def summary_quantity_cell(page: Page, kind: str) -> Locator:
    """Haqiqiy header va total ustunlari soni orqali miqdor katagini qaytarish."""
    table = page.get_by_role("table").filter(has=page.get_by_role("columnheader", name=kind, exact=True))
    expect(table).to_have_count(1)
    headers = table.get_by_role("columnheader")
    expect(headers.first).to_be_visible()
    labels = [" ".join(value.split()) for value in headers.all_inner_texts()]
    column = labels.index(kind)
    quantity_row = table.get_by_role("row").filter(has_text=re.compile(r"Общее\s+кол-во\s*:"))
    expect(quantity_row).to_be_visible()
    cells = quantity_row.get_by_role("cell")
    expect(cells.last).to_be_visible()
    total_columns = cells.count() - len(labels)
    return cells.nth(total_columns + column)
