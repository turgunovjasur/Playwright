"""Read the result of the search submitted through a Smartup list form."""
from urllib.parse import unquote, urlsplit

import allure

from utils.base_pages import UI_TIMEOUT_MS


def _has_filter(node, field, pattern):
    if not isinstance(node, list):
        return False
    if len(node) == 3 and node[1:] == ["esearch", pattern]:
        return field is None or node[0] == field
    return any(_has_filter(child, field, pattern) for child in node if isinstance(child, list))


def search_list_by_field(base, table, field, value, *, search_field=None, setting_label=None):
    """Submit a UI search and verify which fields the grid actually sent."""
    value = str(value)
    if not value.strip():
        raise ValueError("Ro‘yxat qidiruvi uchun qiymat bo‘sh")
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{escaped}%"

    def searched(response):
        if not unquote(urlsplit(response.url).path).endswith("/" + table + ":table"):
            return False
        request = response.request
        if request.method != "POST" or not request.post_data:
            return False
        params = (request.post_data_json or {}).get("p", {})
        return _has_filter(params.get("filter"), None, pattern)

    def submit():
        with base.page.expect_response(searched, timeout=UI_TIMEOUT_MS) as pending:
            base.grid_controller(search=value)
        response = pending.value
        if not response.ok:
            raise AssertionError(f"{table} qidiruvi HTTP {response.status} qaytardi")
        response.finished()
        return response

    def includes_field(response):
        filters = response.request.post_data_json["p"]["filter"]
        return any(_has_filter(filters, key, pattern) for key in (field, search_field) if key)

    response = submit()
    if setting_label and not includes_field(response):
        base.grid_setting(menu_name="Настройка таблицы", field_name=setting_label, search_name=setting_label)
        response = submit()
    if not includes_field(response):
        raise AssertionError(f"{table}: {field} qidiruv sozlamasida yoqilmagan")
    return response


def find_list_record(base, table, field, value, *, search_field=None, also_match=None, setting_label=None):
    """Search by field and require exact matches on any additional identity columns."""
    value = str(value)
    expected = {**(also_match or {}), field: value}
    with allure.step(f"Ro‘yxatdagi Search orqali qidirish · {value}"):
        response = search_list_by_field(base, table, field, value, search_field=search_field,
                                        setting_label=setting_label)
        params = response.request.post_data_json["p"]
        result = response.json()
        columns = params.get("column", [])
        rows = result.get("data") if isinstance(result, dict) else None
        if (not isinstance(rows, list) or not expected.keys() <= set(columns)
                or str(result.get("count")) != str(len(rows)) or int(params.get("offset", 0)) != 0):
            raise AssertionError(f"{table}: {field} bo‘yicha natija to‘liq emas")
        records = [dict(zip(columns, row, strict=True)) for row in rows]
        matches = [
            row for row in records
            if all(str(row[key]) == str(wanted) for key, wanted in expected.items())
        ]
        if len(matches) > 1:
            raise AssertionError(f"{table}: {field}={value} bo‘yicha bir nechta yozuv topildi")
        if matches:
            allure.attach(value, name="Topilgan yozuv bilan davom etiladi", attachment_type=allure.attachment_type.TEXT)
            return matches[0]
        return None
