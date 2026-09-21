"""Testga tegishli web konteksti; pytest/Allure va UI amallaridan mustaqil.

Credentiallar user so'ragan lokal Allure attachmenti uchungina yig'iladi.
State har testcase boshida yangilanadi; oldingi data_store to'liq ko'chirilmaydi.
"""

from contextvars import ContextVar
from copy import deepcopy
import re
from urllib.parse import parse_qsl, urlsplit


_CURRENT = ContextVar("smartup_report_context", default=None)
_PAGE_ATTR = "_smartup_web_context"


def begin_test(nodeid):
    return _CURRENT.set({"nodeid": nodeid, "code": None, "contexts": [], "saved": {}, "used": {}, "observed": [], "outcomes": {}, "notes": []})


def end_test(token):
    _CURRENT.reset(token)


def current_test():
    return _CURRENT.get()


def page_context(page):
    context = getattr(page, _PAGE_ATTR, None)
    if context is None:
        context = {"profile": "", "login": "", "password": "", "company": "", "filial": "", "menu": "", "authorization": "Kirish qayd etilmagan"}
        setattr(page, _PAGE_ATTR, context)
    return context


def remember_page(page):
    """Umumiy sessiya holatini joriy testga qiymatlar nusxasi sifatida oladi."""
    state = current_test()
    if state is None:
        return
    context = deepcopy(page_context(page))
    context.pop("menu", None)
    if not context["login"]:
        return
    if context not in state["contexts"]:
        state["contexts"].append(context)
    if context.get("code"):
        state["code"] = context["code"]


def start_login(page, *, server, company, profile, login, password, code=None):
    remember_page(page)
    context = page_context(page)
    context.clear()
    context.update(server=server, company=company, profile=profile, login=login, password=password, code=code, filial="", menu="", authorization="Kirishga urinish")


def confirm_login(page):
    page_context(page)["authorization"] = "Kirish tasdiqlangan"


def record_filial(page, name):
    remember_page(page)
    page_context(page)["filial"] = str(name)


def record_menu(page, names):
    page_context(page)["menu"] = " → ".join(str(name) for name in names if name)


def page_location(page):
    """Session tokenisiz forma yo'li va faqat biznes ID querylarini oladi."""
    parts = urlsplit(page.url)
    route = parts.fragment.split("?", 1)[0]
    if route.startswith("/"):
        segments = route.split("/", 2)
        route = segments[2] if len(segments) == 3 else ""
    else:
        route = parts.path
    query = parts.query + "&" + parts.fragment.partition("?")[2]
    identifiers = {key: value for key, value in parse_qsl(query) if (key == "id" or key.endswith("_id")) and value.isdecimal() and not re.search(r"session|token|secret|device", key, re.I)}
    context = page_context(page)
    return {"menu": context.get("menu", ""), "route": route, "ids": identifiers, "filial": context.get("filial", ""), "login": context.get("login", "")}


def record_observation(page, kind, values, *, location=None):
    state = current_test()
    if state is None or not values:
        return
    remember_page(page)
    row = {"kind": kind, "values": deepcopy(values), **(location or page_location(page))}
    if row not in state["observed"]:
        state["observed"].append(row)


def record_data(key, value, *, file_name="data_store", saved=False):
    """Read/write chaqiruvi dalili; bir xil qiymat qayta saqlansa ham qayd etadi."""
    state = current_test()
    if state is None:
        return
    if file_name == "data_store" and key == "code":
        state["code"] = value
    target = state["saved" if saved else "used"]
    target[(file_name, key)] = deepcopy(value)


def record_api_context(*, server, company, login, password, code, filial="", authorization="Kirish tasdiqlangan"):
    state = current_test()
    if state is None:
        return
    context = {"server": server, "company": company, "profile": "User (Mobile API)", "login": login, "password": password, "code": code, "filial": filial, "authorization": authorization}
    state["contexts"] = [row for row in state["contexts"] if not (row.get("profile") == context["profile"] and row.get("login") == login and row.get("authorization") == "Kirishga urinish")]
    if context not in state["contexts"]:
        state["contexts"].append(context)
    state["code"] = code


def reporting_note(message):
    state = current_test()
    if state is not None and message not in state["notes"]:
        state["notes"].append(message)
