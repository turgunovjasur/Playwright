from utils.base_page import BasePage
"""A2 (yangi migratsiya qilingan) formalar smoke testi — 1-ETAP: URL / grid orqali ochilish.

Maqsad: new_forms.md dagi har bir a2 formani ochib, to'g'ri ochilishini tekshirish —
xatolik/404/"нет доступа"/modal error bormi? Test xatoda TO'XTAMAYDI: har forma alohida
allure.step, muammo bo'lsa screenshot olinadi va qayd etiladi, keyingi formaga o'tiladi.

Har forma "mode" bilan tekshiriladi:
  - "direct"   -> to'g'ridan-to'g'ri URL bilan ochiladi ({company_url}/a2/{path}). List/dashboard/settings/+add.
  - "via_list" -> forma id kerak (+edit/+copy/_view/_details). Mos `_list` ochiladi, grid BIRINCHI qatori
                  double-click qilinadi -> forma o'sha record id'si bilan ochiladi (URL: ...?...&{id}=...).
                  Grid qator selektori: `main .smt-data-row`. (2026-07-07 MCP tasdiqlangan.)
  - "skip"     -> a2 list mavjud emas (masalan ker/setting — ker/setting_list 404), tekshirib bo'lmaydi.

PROFIL-AWARE: har forma O'ZI OCHILADIGAN profilda sinaladi (new_forms.md 2026-07-07 tasdiqlangan):
  - "admin" profil (oddiy kompaniya admini, .env login) va "head" profil (admin@head).
  head yo'q serverda (masalan smartup.online) head qismi avtomatik pytest.skip.

FILIAL: forma ko'rinishi filialga bog'liq — operatsion formalar operatsion filial (filial-pw{code}) da,
admin/справочник formalar "Администрирование" da. Test kerakli filialga switch_filial qiladi.

Etaplar: 1) SHU FAYL — URL/grid orqali. 2) keyingi — real menyu yo'li (tab -> leaf bosib).

Yordamchi funksiyalar xaritasi (tepadan pastga, chaqiruv tartibida):
  _login_profile       -> profilga kiradi (admin/head); head bu serverda yo'q bo'lsa testni skip qiladi
  _goto_dashboard       -> bosh sahifaga o'tib "Trade" ko'rinishini kutadi (filial almashtirishdan oldin)
  _operational_filial   -> operatsion filial nomini aniqlaydi (eski angular sahifadagi $scope orqali)
  _classify             -> _INSPECT_JS natijasidan sahifa holatini aniqlaydi: ok/404/denied/error/bo'sh
  _open_direct          -> formani to'g'ridan-to'g'ri URL bilan ochib holatini qaytaradi
  _open_via_list        -> _list ochib, birinchi qatorni double-click qilib forma(id)ni ochadi
  _is_ok                -> mode+outcome asosida forma "muvaffaqiyatli ochildi"mi hal qiladi
  _render_report        -> yig'ilgan natijalarni konsol/Allure uchun chiroyli hisobotga aylantiradi
"""
import os

import allure
import pytest
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import (
    authorization, login, dashboard, company_url, company_password, admin_email,
)

pytestmark = [allure.epic("Smoke"), allure.feature("A2 New Forms"), allure.story("URL ochilish tekshiruvi")]

ADMIN_FILIAL = "Администрирование"
GRID_ROW = "main .smt-data-row"  # a2 grid data qatori (barqaror class)

# Har forma dict: path, title, profile(admin|head), filial(operational|admin), mode(direct|via_list|skip), parent
def _f(path, title, profile, filial, mode="direct", parent=None):
    return {"path": path, "title": title, "profile": profile, "filial": filial, "mode": mode, "parent": parent}

A2_FORMS = [
    # ===== ADMIN profil / Администрирование filial =====
    _f("biruni/kauth/company_client_list", "Клиенты OAuth2 сервера для компании", "admin", "admin"),
    _f("biruni/kauth/company_client+add", "Клиенты OAuth2 сервера (создание)", "admin", "admin"),
    _f("biruni/kauth/company_client+edit", "Клиенты OAuth2 сервера (изменение)", "admin", "admin",
       "via_list", "biruni/kauth/company_client_list"),
    _f("biruni/ker/head_template_list+attach", "Доступные шаблоны", "admin", "admin"),
    _f("biruni/ker/setting+add", "Настройки шаблонов (создание)", "admin", "admin"),
    _f("biruni/ker/setting+edit", "Настройки шаблонов (изменение)", "admin", "admin", "skip"),  # ker/setting_list yo'q (404)
    # ===== ADMIN profil / operatsion filial =====
    _f("biruni/md/company_audit_info_audit", "История изменений компании", "admin", "operational"),
    _f("biruni/md/company_audit_info_audit_details", "Детали истории изменений компании", "admin", "operational",
       "via_list", "biruni/md/company_audit_info_audit"),
    _f("biruni/plg/plugin_catalog", "Plugin Marketplace", "admin", "operational"),
    _f("anor/mkw/marking_stocktaking/marking_stocktaking_list", "Инвентаризация КМ", "admin", "operational"),
    _f("anor/rep/mkr/pnl", "Отчёт о прибылях и убытках (PnL)", "admin", "operational"),
    _f("trade/tvt/user_locations", "Отслеживание пользователей", "admin", "operational"),
    _f("trade/tph/user_tracking", "Отслеживание мобильных представителей", "admin", "operational"),
    _f("trade/txs/external_settings", "Настройки интеграции со сторонним ПО", "admin", "operational"),
    _f("trade/tdeal/logistics_list", "Логистика", "admin", "operational"),
    _f("trade/tdeal/commercial_dashboard", "Коммерческий дашборд", "admin", "operational"),
    _f("anor/rep/mbi/mkcs/operation", "Конструктор отчетов по финансам", "admin", "operational"),
    _f("anor/rep/mbi/mcg/action", "Конструктор отчетов по акциям", "admin", "operational"),
    _f("anor/rep/mbi/mfm/movement", "Конструктор по межорг. перемещениям", "admin", "operational"),
    _f("anor/rep/mbi/mfm/movement_request", "Конструктор по запросам на межорг. перемещения", "admin", "operational"),
    _f("anor/rep/mbi/mkw/input", "Конструктор по поступлениям", "admin", "operational"),
    _f("anor/rep/mbi/mkw/movement", "Конструктор по внутр. перемещениям", "admin", "operational"),
    _f("anor/rep/mbi/mkw/purchase", "Конструктор по закупкам", "admin", "operational"),
    _f("anor/rep/mbi/mkw/purchase_request", "Конструктор по запросам на закуп", "admin", "operational"),
    _f("anor/rep/mbi/mkw/writeoff", "Конструктор по списанию", "admin", "operational"),
    _f("anor/rep/mbi/mqpf/request", "Конструктор по заявкам на оборудование", "admin", "operational"),
    _f("trade/rep/mbi/tmcg/shelf_share", "Конструктор по долям на полках", "admin", "operational"),
    _f("trade/rep/mbi/tvt/visit", "Конструктор отчётов по визитам", "admin", "operational"),
    _f("anor/rep/mbi/mfa/purchase", "Конструктор по закупкам (финансы)", "admin", "operational"),
    _f("trade/tvt/visit_list", "Визиты", "admin", "operational"),
    # ===== HEAD profil / Администрирование filial =====
    _f("biruni/kauth/client_list", "Клиенты API/OAuth2 сервера", "head", "admin"),
    _f("biruni/kauth/client+add", "Клиент API/OAuth2 (создание)", "head", "admin"),
    _f("biruni/kauth/client+edit", "Клиент API/OAuth2 (изменение)", "head", "admin",
       "via_list", "biruni/kauth/client_list"),
    _f("biruni/kauth/security_settings", "Настройки безопасности", "head", "admin"),
    _f("biruni/md/audit_setting", "Настройки истории изменений", "head", "admin"),
    _f("biruni/md/company_list", "Компании", "head", "admin"),
    _f("biruni/md/company_add", "Компания (создание)", "head", "admin"),
    _f("biruni/md/company_edit", "Компания (изменение)", "head", "admin", "via_list", "biruni/md/company_list"),
    _f("biruni/md/company_view", "Компания (просмотр)", "head", "admin", "via_list", "biruni/md/company_list"),
    _f("biruni/md/contact_info_setting", "Контактная информация", "head", "admin"),
    _f("biruni/md/feedback_list", "Фидбеки", "head", "admin"),
    _f("biruni/md/log_list", "Логи", "head", "admin"),
    _f("biruni/md/query_executor", "Запросы к базе данных", "head", "admin"),
    _f("biruni/md/request_limit_template_list", "Шаблоны лимитов (список)", "head", "admin"),
    _f("biruni/md/request_limit_template+add", "Шаблоны лимитов (создание)", "head", "admin"),
    _f("biruni/md/request_limit_template+edit", "Шаблоны лимитов (изменение)", "head", "admin",
       "via_list", "biruni/md/request_limit_template_list"),
    _f("biruni/md/request_limit_template_view", "Шаблоны лимитов (просмотр)", "head", "admin",
       "via_list", "biruni/md/request_limit_template_list"),
    _f("biruni/md/request_limit_template_audit_details", "Подробности истории шаблона лимитов", "head", "admin",
       "via_list", "biruni/md/request_limit_template_list"),
    _f("biruni/ms/announcement_list", "Объявления", "head", "admin"),
    _f("biruni/ms/announcement+add", "Объявление (создание)", "head", "admin"),
    _f("biruni/ms/announcement+copy", "Объявление (копирование)", "head", "admin", "via_list", "biruni/ms/announcement_list"),
    _f("biruni/ms/announcement+edit", "Объявление (изменение)", "head", "admin", "via_list", "biruni/ms/announcement_list"),
    # ===== HEAD profil / operatsion filial =====
    _f("billing/blda/operational_dashboard", "Операционный дашборд", "head", "operational"),
]

PROFILE_KEYS = sorted({f["profile"] for f in A2_FORMS})

# JS: sahifa "hal bo'ldi" belgisi — title o'zgargan YOKI xato/access-denied matni chiqqan.
# wait_for_function shu true qaytargunicha yoki timeout'gacha kutadi.
_WAIT_RESOLVED_JS = """() => {
  const t = document.title;
  const b = document.body ? document.body.innerText : '';
  return (t && t !== 'Smartup Online')
      || /Страница не найдена|Нет доступа к форме|Доступ запрещ|Не удалось загрузить|Что-то пошло не так/i.test(b);
}"""

# JS: joriy sahifa holatini bitta so'rovda o'qiydi — title, asosiy content uzunligi,
# 404/access-denied/xato matnlari va ko'rinadigan alert/toast xabarlari. Natija _classify() ga beriladi.
_INSPECT_JS = """() => {
  const body = document.body ? document.body.innerText : '';
  const main = document.querySelector('main');
  const alerts = [...document.querySelectorAll('[role=alert],[role=alertdialog],[class*=toast],[class*=Toast]')]
    .filter(e => e.offsetParent && (e.innerText || '').trim())
    .map(e => (e.innerText || '').trim().slice(0, 120)).slice(0, 3);
  return {
    title: document.title,
    mainLen: main ? (main.innerText || '').trim().length : 0,
    notFound: /Страница не найдена/i.test(body),
    denied: /Нет доступа к форме|Доступ запрещ|Недостаточно прав/i.test(body),
    loadError: /Не удалось загрузить|Что-то пошло не так/i.test(body),
    alerts,
  };
}"""

# Klassifikatsiya -> hisobotdagi belgi. "id_or_empty" ataylab "denied" dan boshqa belgi bilan
# ko'rsatiladi: bu holatda aniq "доступ запрещён" matni YO'Q, sahifa shunchaki bo'sh/id'siz qoldi
# (masalan double-click yangi formaga o'tkazmadi) — sabab boshqa, aralashtirib bo'lmaydi.
_OUTCOME_LABEL = {
    "ok": "✅", "no_rows": "LIST-BO'SH", "skip": "SKIP",
    "denied": "🔒", "id_or_empty": "❓", "not_found": "404", "error": "❌",
}

# ----------------------------------------------------------------------------------------------------------------------

def _login_profile(page, profile_key):
    """Profilga kiradi va login email'ni qaytaradi. head yo'q bo'lsa testni skip qiladi."""
    if profile_key == "admin":
        authorization(page, who="admin")
        return admin_email()

    email = os.getenv("HEAD_ADMIN_EMAIL") or "admin@head"
    password = os.getenv("HEAD_ADMIN_PASSWORD") or company_password()
    login(page, email=email, password=password)
    try:
        dashboard(page, timeout=30_000)  # head yo'q serverda tezroq skip qilish uchun qisqa timeout
    except (AssertionError, PlaywrightTimeoutError):
        pytest.skip(f"head profil ({email}) bu serverda login bo'lmadi — head kompaniya yo'q, skip.")
    return email

# ----------------------------------------------------------------------------------------------------------------------

def _operational_filial(page, code):
    """Operatsion filial nomini aniqlaydi (read-only diagnostika): avval filial-pw{code}, keyin har qanday
    filial-pw*, keyin Администрирование bo'lmagan birinchisi. Eski app (angular) sahifasida chaqiriladi."""
    names = page.evaluate("""() => {
      try {
        const ng = window.angular; let scope = null;
        for (const el of document.querySelectorAll('*')) {
          const s = ng.element(el).scope && ng.element(el).scope();
          if (s && s.a && s.a.session && s.a.session.si) { scope = s; break; }
        }
        return (scope.a.session.si.projects[0].filials || []).map(f => f.name);
      } catch (e) { return []; }
    }""")
    prefer = f"filial-pw{code}"
    if prefer in names:
        return prefer
    pw = [n for n in names if str(n).lower().startswith("filial-pw")]
    if pw:
        return pw[0]
    others = [n for n in names if n != ADMIN_FILIAL]
    return others[0] if others else ADMIN_FILIAL

# ----------------------------------------------------------------------------------------------------------------------

def _goto_dashboard(page):
    page.goto(f"{company_url()}/")
    dashboard(page)

# ----------------------------------------------------------------------------------------------------------------------

def _classify(info):
    if info["notFound"]:
        return "not_found"
    if info["denied"]:
        return "denied"
    if info["loadError"] or info["alerts"]:
        return "error"
    if info["title"] in ("", "Smartup Online") or info["mainLen"] < 20:
        return "id_or_empty"
    return "ok"

# ----------------------------------------------------------------------------------------------------------------------

def _open_direct(page, path, timeout=30_000, settle_ms=1_200):
    """a2 formani to'g'ridan-to'g'ri URL bilan ochib holatini qaytaradi."""
    try:
        page.goto(f"{company_url()}/a2/{path}", wait_until="domcontentloaded", timeout=40_000)
    except PlaywrightTimeoutError:
        return "error", "sahifa 40s da yuklanmadi"
    try:
        page.wait_for_function(_WAIT_RESOLVED_JS, timeout=timeout)
    except PlaywrightTimeoutError:
        pass
    page.wait_for_timeout(settle_ms)
    info = page.evaluate(_INSPECT_JS)
    return _classify(info), info.get("title") or ""

# ----------------------------------------------------------------------------------------------------------------------

def _open_via_list(page, parent_list, timeout=30_000, settle_ms=1_200):
    """`_list` ochib, grid birinchi qatorini double-click qilib forma (id bilan) ochiladi.

    Qaytadi: (outcome, detail) — outcome: ok | no_rows | not_found | denied | error | id_or_empty
    """
    try:
        page.goto(f"{company_url()}/a2/{parent_list}", wait_until="domcontentloaded", timeout=40_000)
    except PlaywrightTimeoutError:
        return "error", f"{parent_list} 40s da yuklanmadi"

    # list ochildimi / grid qatori bormi?
    try:
        page.wait_for_selector(GRID_ROW, timeout=timeout)
    except PlaywrightTimeoutError:
        info = page.evaluate(_INSPECT_JS)
        st = _classify(info)
        return (st if st in ("not_found", "denied") else "no_rows"), f"list holati: {st}"

    before = page.url
    page.locator(GRID_ROW).first.dblclick()
    try:
        page.wait_for_url(lambda u: u != before, timeout=timeout)
    except PlaywrightTimeoutError:
        return "id_or_empty", "double-click formaga o'tmadi"

    try:
        page.wait_for_function(_WAIT_RESOLVED_JS, timeout=timeout)
    except PlaywrightTimeoutError:
        pass
    page.wait_for_timeout(settle_ms)
    info = page.evaluate(_INSPECT_JS)
    return _classify(info), page.url.split("?")[0]

# ----------------------------------------------------------------------------------------------------------------------

def _is_ok(mode, outcome):
    """Forma kutilgandek ochildimi (muvaffaqiyat)?"""
    if mode == "skip":
        return True  # tekshirilmaydi
    if mode == "via_list":
        return outcome in ("ok", "no_rows")  # ochildi yoki list bo'sh (formada muammo yo'q)
    return outcome == "ok"  # direct

# ----------------------------------------------------------------------------------------------------------------------

def _render_report(profile_key, profile_login, results):
    """Natijalarni o'qish oson konsol/Allure hisobotiga aylantiradi: sarlavha qutisi + filial bo'yicha ro'yxat."""
    header = [
        "A2 YANGI FORMALAR — OCHILISH SMOKE",
        f"Profil : {profile_key.upper()}  ({profile_login})",
        f"Server : {company_url()}",
    ]
    inner_width = max(60, max(len(line) for line in header))
    rule = "─" * (inner_width + 2)

    lines = [f"┌{rule}┐"]
    lines += [f"│ {line.ljust(inner_width)} │" for line in header]
    lines.append(f"└{rule}┘")

    broken = [r for r in results if not r["ok"]]
    lines.append("")
    lines.append(
        f"  Jami: {len(results)}   ✅ Muvaffaqiyatli: {len(results) - len(broken)}   ⚠ Muammo: {len(broken)}"
    )

    section_rule = "─" * (inner_width + 4)
    cur_filial = None
    for r in results:
        if r["filial"] != cur_filial:
            count = sum(1 for x in results if x["filial"] == r["filial"])
            lines += ["", f"  ▸ FILIAL: {r['filial']} ({count} forma)", f"  {section_rule}"]
            cur_filial = r["filial"]
        flag = "   ⚠ MUAMMO" if not r["ok"] else ""
        icon = _OUTCOME_LABEL.get(r["outcome"], r["outcome"])
        lines.append(f"      {icon:<4} {r['mode']:<9} {r['path']}{flag}")

    return "\n".join(lines)

# ----------------------------------------------------------------------------------------------------------------------

def run_a2_new_forms_url(page, code, profile_key, profile_login):
    """Berilgan profilga tegishli a2 formalarni ochib tekshiradi (page login qilingan)."""
    base = BasePage(page)
    forms = [f for f in A2_FORMS if f["profile"] == profile_key]
    operational_filial = None
    results = []
    via_list_cache = {}  # (filial, parent) -> (outcome, detail) — bir parent bir marta tekshiriladi

    for filial_kind in ("operational", "admin"):
        group = [f for f in forms if f["filial"] == filial_kind]
        if not group:
            continue

        with allure.step(f"Filialga o'tish: {filial_kind}"):
            _goto_dashboard(page)
            if filial_kind == "admin":
                target_filial = ADMIN_FILIAL
            else:
                operational_filial = operational_filial or _operational_filial(page, code)
                target_filial = operational_filial
            base.switch_filial(name=target_filial)

        for form in group:
            path, title, mode, parent = form["path"], form["title"], form["mode"], form["parent"]
            with allure.step(f"[{mode}] {path} — {title}"):
                if mode == "skip":
                    outcome, detail = "skip", "a2 list mavjud emas — tekshirib bo'lmaydi"
                elif mode == "via_list":
                    key = (target_filial, parent)
                    if key not in via_list_cache:
                        via_list_cache[key] = _open_via_list(page, parent)
                    outcome, detail = via_list_cache[key]
                else:
                    outcome, detail = _open_direct(page, path)

                ok = _is_ok(mode, outcome)
                results.append({
                    "path": path, "title": title, "filial": target_filial,
                    "mode": mode, "outcome": outcome, "ok": ok, "detail": detail,
                })

                allure.attach(
                    f"path: {path}\nsarlavha: {title}\nprofil: {profile_login}\nfilial: {target_filial}\n"
                    f"mode: {mode}\nnatija: {_OUTCOME_LABEL.get(outcome, outcome)} ({outcome})\ntafsilot: {detail}",
                    name="natija", attachment_type=allure.attachment_type.TEXT,
                )
                if not ok:
                    allure.attach(page.screenshot(full_page=True),
                                  name=f"MUAMMO — {path}", attachment_type=allure.attachment_type.PNG)

    report = _render_report(profile_key, profile_login, results)
    allure.attach(report, name="HISOBOT", attachment_type=allure.attachment_type.TEXT)
    print("\n" + report + "\n")

    broken = [r for r in results if not r["ok"]]
    if broken:
        broken_txt = "\n".join(
            f"  - {r['path']} ({r['title']}) — filial={r['filial']}, mode={r['mode']}, "
            f"holat={_OUTCOME_LABEL.get(r['outcome'], r['outcome'])}, {r['detail']}"
            for r in broken
        )
        raise AssertionError(
            f"{profile_key} profil: {len(broken)} ta a2 forma ochilmadi:\n{broken_txt}\n\n"
            f"To'liq hisobot Allure 'HISOBOT' attachmentida."
        )

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("A2 yangi formalar — ochilish smoke ({profile_key} profil)")
@pytest.mark.parametrize("profile_key", PROFILE_KEYS)
def test_a2_new_forms_url(page, code, profile_key):
    profile_login = _login_profile(page, profile_key)
    run_a2_new_forms_url(page, code, profile_key, profile_login)
