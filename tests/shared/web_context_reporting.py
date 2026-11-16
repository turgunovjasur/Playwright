"""Har testcase uchun bitta 'Webda tekshirish uchun' Allure attachmenti."""

import os
from html import escape

import allure

from utils.base_pages.page_reporting import capture_filial
from utils.report_context import current_test, page_location, remember_page, reporting_note


_LABELS = {
    "action_id": "Aksiya ID", "name": "Nom", "code": "Kod", "calc_kind": "Hisoblash turi",
    "rule_kind": "Shart turi", "threshold": "Chegara", "bonus_kind": "Bonus turi",
    "bonus_value": "Bonus qiymati", "product_name": "Mahsulot", "room_name": "Ish zonasi",
    "price_type_name": "Narx turi", "start_date": "Boshlanish sanasi", "end_date": "Tugash sanasi",
}
_ACTION_NAMES = {
    "input": "Maydonni to‘ldirish yoki tekshirish", "b_input": "Maydondan qiymat tanlash",
    "multiselect": "Ro‘yxatdan tanlash", "ui_select": "Ro‘yxatdan tanlash",
    "click": "Bosish", "navigate_to": "Menyuni ochish", "navigate_to_form": "Formani ochish",
    "switch_filial": "Filialni tanlash", "confirm_biruni": "Tasdiqlash",
    "expect_page": "Sahifani tekshirish", "form_view": "Qiymatni tekshirish",
}


def _text(value):
    return escape(str(value if value is not None else "Aniqlanmadi"))


def _table(values):
    return "<table>" + "".join(f"<tr><th>{_text(key)}</th><td>{_text(value)}</td></tr>" for key, value in values) + "</table>"


def _data_rows(value, prefix=""):
    """Flatten the actual per-test values for the reproduction table."""
    if isinstance(value, dict):
        for key, item in value.items():
            label = _LABELS.get(key, str(key))
            yield from _data_rows(item, f"{prefix} / {label}" if prefix else label)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value, 1):
            yield from _data_rows(item, f"{prefix} [{index}]")
    else:
        yield prefix, value


def _capture_page(page):
    if page is None:
        return
    capture_filial(page)
    remember_page(page)
    if not page.is_closed():
        location = page_location(page)
        state = current_test()
        state["location"] = location


def render_context(state):
    """HTML escape majburiy; parol user tasdig'iga ko'ra faqat shu attachmentda."""
    server = state["server"]
    company = state["company"]
    saved_company = state["saved"].get(("data_store", "company_code"))
    if company == "1":
        company = saved_company or next((row.get("company") for row in reversed(state["contexts"]) if row.get("company")), "Yaratish tugamagan")
    rows = [("Test", state["nodeid"]), ("Server", server), ("Company", company), ("Run code", state["code"] or "Qayd etilmagan")]
    if any(outcome != "passed" for outcome in state["outcomes"].values()):
        rows.append(("Bajarilish holati", ", ".join(f"{phase}: {outcome}" for phase, outcome in state["outcomes"].items())))
    html = ["<html><head><meta charset='utf-8'><style>body{font:14px/1.5 Arial,sans-serif;color:#243047;background:#fff;margin:20px}h2{font-size:18px}h3{font-size:15px;margin-top:24px}table{border-collapse:collapse;width:100%;table-layout:fixed}th,td{text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;vertical-align:top;overflow-wrap:anywhere;white-space:pre-wrap}th{width:30%;font-weight:normal;color:#596579}details{margin-top:16px}summary{cursor:pointer}a{color:#2563eb}</style></head><body><h2>Webda tekshirish uchun</h2>", _table(rows)]
    if server.startswith(("http://", "https://")):
        html.append(f'<p><a href="{escape(server.rstrip("/") + "/login.html", quote=True)}" target="_blank" rel="noopener noreferrer">Smartup kirish sahifasini ochish</a></p>')
    for index, context in enumerate(state["contexts"], 1):
        html.append(f"<h3>Kirish ma'lumotlari {index if len(state['contexts']) > 1 else ''}</h3>")
        identity_fields = [("Login", "login"), ("Parol", "password")]
        if context.get("authenticated_user_id"):
            identity_fields.append(("Tasdiqlangan user ID", "authenticated_user_id"))
        fields = [("Profil", "profile"), ("Company", "company"), *identity_fields, ("Filial", "filial"), ("Kirish holati", "authorization")]
        html.append(_table([(label, context.get(key) or "Aniqlanmadi") for label, key in fields]))
    if not state["contexts"]:
        html.append("<p>Bu testda login bajarilgani qayd etilmagan.</p>")
    location = state.get("location", {})
    if location.get("menu") or location.get("route"):
        html.append("<h3>Webda topish</h3>" + _table([(label, location[key]) for label, key in [("Menyu", "menu"), ("Oxirgi forma yo'li", "route")] if location.get(key)] + list(location.get("ids", {}).items())))
    if state.get("failure"):
        html.append("<h3>Yiqilgan qadam</h3>" + _table(state["failure"].items()))
    for title, key in [("Test parametrlari", "parameters"), ("Setup ma’lumotlari", "baseline")]:
        if state.get(key):
            html.append(f"<h3>{title}</h3>" + _table(_data_rows(state[key])))
    if state.get("actions"):
        html.append("<h3>Brauzerda takrorlash tartibi</h3><ol>")
        for action in state["actions"]:
            place = action["location"]
            fields = [(label, place[k]) for label, k in [("Menyu", "menu"), ("Forma", "route"), ("Filial", "filial")] if place.get(k)]
            fields.extend(place["ids"].items())
            fields.extend(action["inputs"].items())
            if "result" in action:
                fields.append(("Natija", action["result"]))
            if "error" in action:
                fields.append(("Xato", action["error"]))
            title = _ACTION_NAMES.get(action["name"], action["name"])
            html.append(f"<li><b>{_text(title)}</b>{_table(fields)}</li>")
        html.append("</ol>")
    for (file_name, key), value in state["saved"].items():
        if key == "code":
            continue
        name = key if file_name == "data_store" else f"{file_name} / {key}"
        html.append(f"<h3>Test saqlagan ma'lumot: {_text(name)}</h3>" + _table(_data_rows(value, "" if isinstance(value, dict) else name)))
    if state["observed"]:
        html.append("<details><summary>Webda tekshirilgan obyekt va qiymatlar</summary>")
        for row in state["observed"]:
            values = [(label, row[key]) for label, key in [("Menyu", "menu"), ("Forma yo'li", "route")] if row.get(key)]
            values.extend([("Filial", row["filial"] or "Aniqlanmadi"), ("Login", row["login"] or "Aniqlanmadi")])
            if isinstance(row["values"], dict):
                values.extend(row["values"].items())
            else:
                values.append(("Qidirish uchun", row["values"][0]))
                if len(row["values"]) > 1:
                    values.append(("Tekshirilgan qiymatlar", " · ".join(str(value) for value in row["values"][1:])))
            values.extend((key, value) for key, value in row["ids"].items() if not isinstance(row["values"], dict) or key not in row["values"])
            html.append(f"<p>{_text(row['kind'])}</p>" + _table(values))
        html.append("</details>")
    used = [(key, value) for (file_name, key), value in state["used"].items() if (file_name, key) not in state["saved"] and key != "code"]
    if used:
        html.append("<details><summary>Test foydalangan mavjud ma'lumotlar</summary>")
        for key, value in used:
            html.append(_table(_data_rows(value, key)))
        html.append("</details>")
    if not state["saved"] and not state["observed"]:
        html.append("<p>Yaratilgan yoki tekshirilgan obyekt ma'lumoti qayd etilmagan.</p>")
    for note in state["notes"]:
        html.append(f"<p>{_text(note)}</p>")
    html.append("</body></html>")
    return "".join(html)


def record_report(item, report, page):
    state = current_test()
    if state is None:
        return
    state.setdefault("server", os.environ.get("COMPANY_URL", "Aniqlanmadi"))
    state.setdefault("company", os.environ.get("COMPANY_CODE", "Aniqlanmadi"))
    state["outcomes"][report.when] = report.outcome
    if report.failed and "failure" not in state:
        listener = item.config.pluginmanager.getplugin("allure_listener")
        result = listener.allure_logger.get_test(None) if listener else None
        steps = result.steps if result and report.when == "call" else []
        path = []
        while steps:
            failed = next((s for s in reversed(steps) if s.status in {"broken", "failed"}), None)
            if failed is None:
                break
            path.append(failed.name)
            steps = failed.steps
        message = getattr(report.longrepr, "reprcrash", None)
        state["failure"] = {"Bosqich": report.when, "Qadam": " → ".join(path) or item.name,
                            "Sabab": message.message if message else report.longreprtext}
    if report.when != "teardown":
        try:
            _capture_page(page)
        except Exception:
            reporting_note("Sahifa kontekstining ayrim maydonlarini o'qib bo'lmadi.")
    if item.funcargs.get("code") is not None:
        state["code"] = item.funcargs["code"]
    if report.when == "teardown":
        state["parameters"] = getattr(getattr(item, "callspec", None), "params", {})
        state["baseline"] = item.funcargs.get("business_baseline") or item.funcargs.get("api_business_baseline")
        allure.attach(render_context(state), name="Webda tekshirish uchun", attachment_type=allure.attachment_type.HTML)
