from utils.base_page import BasePage
"""A2 formalar — real menyu orqali ochilish smoke (ADMIN profil).

Har bir a2 (yangi migratsiya) forma ESKI menyudan real foydalanuvchi kabi ochiladi
(tab bosish -> leaf bosish -> forma ochilishini kutish). Forma qayerdaligi (tab + yo'l)
`new_forms.md` da va live menyuда tasdiqlangan. Xatoda TO'XTAMAYDI: har forma alohida
allure.step, muammoда screenshot olinadi va qayd etiladi, keyingi formaga o'tiladi; oxirида hisobot.

FILIAL: menyu filialга bog'liq:
  - birinchi "Администрирование" bo'lmagan filialda:  Визиты/Логистика, dashboardlar, hisobot konstruktorlari, PnL.
  - "Администрирование" filialida:   biruni/kauth/company_client_list (+ undан Создать/Изменить bilan +add/+edit).
  Test kerakli filialга o'tib, o'sha filial menyusidan formalarni ochadi.

+add/+edit — alohida menyu leafi emas: list ochilib "Создать" (yaratish) yoki qator tanlanib "Изменить"
(o'zgartirish) bosiladi (2026-07-08 live tasdiqlangan). Forma ochilgani "Сохранить" tugmasi bilan tekshiriladi.

QOIDA: eski angular menyu orqali ochiladigan a2 formalar — barchasi ADMIN formalar; alohida head test yo'q.
Hali qamralmagan admin formalar (Компании, Логи, Объявления, ...) shu faylга qo'shib boriladi — treklar `new_forms.md` da.
"""
import re

import allure
import pytest
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from tests.smoke.flows.flow_authorization import authorization, company_url
from tests.smoke.flows.flow_navigate import navigate_to_a2

pytestmark = [
    pytest.mark.smoke_group("A2 Admin Forms"),
    allure.epic("Smoke"),
    allure.feature("A2 New Forms"),
    allure.story("Menyu orqali ochilish (admin)"),
]

ADMIN_FILIAL = "Администрирование"
A2_ADMIN_FORM_TIMEOUT = 60_000

# operatsion filialdagi a2 formalar: (tab, yo'l, forma nomi)
OPERATIONAL_FORMS = [
    ("Главное", "trade/txs/external_settings", "Настройки интеграции со сторонним ПО"),
    ("Продажа", "trade/tvt/visit_list", "Визиты"),
    ("Продажа", "trade/tvt/user_locations", "Отслеживание пользователей"),
    ("Продажа", "trade/tph/user_tracking", "Отслеживание мобильных представителей"),
    ("Продажа", "trade/tdeal/commercial_dashboard", "Коммерческий дашборд"),
    ("Продажа", "trade/rep/mbi/tvt/visit", "Конструктор отчётов по визитам"),
    ("Склад", "trade/tdeal/logistics_list", "Логистика"),
    ("Склад", "anor/rep/mbi/mkw/movement", "Конструктор отчетов по внутр. перемещениям"),
    ("Склад", "anor/rep/mbi/mkw/purchase_request", "Конструктор отчетов по запросам на закуп"),
    ("Склад", "anor/rep/mbi/mkw/purchase", "Конструктор отчетов по закупкам"),
    ("Склад", "anor/rep/mbi/mkw/input", "Конструктор отчетов по поступлениям"),
    ("Склад", "anor/rep/mbi/mkw/writeoff", "Конструктор отчетов по списанию"),
    ("Склад", "anor/rep/mbi/mfm/movement_request", "Конструктор отчетов по запросам на межорг. перемещения"),
    ("Склад", "anor/rep/mbi/mfm/movement", "Конструктор отчетов по межорг. перемещениям"),
    ("Финансы", "anor/rep/mbi/mkcs/operation", "Конструктор отчетов по финансам"),
    ("Финансы", "anor/rep/mkr/pnl", "Отчёт о прибылях и убытках (PnL)"),
    ("Торговый маркетинг", "trade/rep/mbi/tmcg/shelf_share", "Конструктор отчетов по долям на полках"),
    ("Оборудование", "anor/rep/mbi/mqpf/request", "Конструктор отчетов по заявкам на оборудование"),
    ("Плагин", "biruni/plg/plugin_catalog", "Plugin Marketplace"),
]

# "Администрирование" filialidagi a2 formalar: (tab, yo'l, forma nomi)
ADMIN_FILIAL_FORMS = [
    ("Главное", "biruni/kauth/company_client_list", "Клиенты OAuth2 сервера для компании"),
]

# a2 formalar "sibling" orqali (operatsion filial): eski forma menyudan ochilib, subheader'dagi
# konstruktor sub-link'i bosiladi -> a2 ochiladi. (tab, eski_leaf_href_sufiksi, sub-link nomi, a2_yo'l, forma nomi)
SIBLING_FORMS = [
    ("Справочники", "/anor/mcg/action_list", "Конструктор отчетов по акциям",
     "anor/rep/mbi/mcg/action", "Конструктор отчетов по акциям"),
    ("Склад", "/anor/mkw/stocktaking/stocktaking_list", "Инвентаризация КМ",
     "anor/mkw/marking_stocktaking/marking_stocktaking_list", "Инвентаризация КМ"),
]

# ----------------------------------------------------------------------------------------------------------------------

def _first_operational_filial(page):
    """Birinchi "Администрирование" bo'lmagan filial nomini angular session modelidan oladi."""
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
    for name in names:
        if name and name != ADMIN_FILIAL:
            return name
    raise AssertionError(
        f"A2 admin test uchun '{ADMIN_FILIAL}' bo'lmagan operatsion filial topilmadi. "
        f"Ko'ringan filiallar: {names}"
    )

# ----------------------------------------------------------------------------------------------------------------------

def _back_to_menu(page):
    """a2 formadan eski menyuli dashboardga qaytadi (keyingi forma uchun)."""
    if "/a2/" in page.url:
        page.go_back()
    expect(page.locator("a.menu-link.menu-toggle").first).to_be_visible(timeout=A2_ADMIN_FORM_TIMEOUT)

# ----------------------------------------------------------------------------------------------------------------------

def _open_form(page, filial, tab, path, name, results):
    """Bitta a2 formani menyudan ochib natijani `results` ga yozadi, so'ng menyuga qaytadi."""
    with allure.step(f"{tab} → {name}"):
        try:
            navigate_to_a2(page, tab, path)
            results.append((filial, path, name, True, page.title()))
        except (AssertionError, PlaywrightTimeoutError) as exc:
            results.append((filial, path, name, False, str(exc).splitlines()[0][:150]))
            allure.attach(page.screenshot(full_page=True),
                          name=f"MUAMMO — {path}", attachment_type=allure.attachment_type.PNG)
        _back_to_menu(page)

# ----------------------------------------------------------------------------------------------------------------------

def _open_a2_via_sibling(page, filial, tab, parent_leaf, sibling_name, a2_path, name, results):
    """Eski forma (parent_leaf) menyudan ochilib, subheader'dagi sub-link (sibling_name) orqali a2 forma ochiladi.

    Ba'zi a2 konstruktorlar (masalan "Конструктор отчетов по акциям") alohida menyu leafi emas —
    eski forma ("Акции") ichidan konstruktor sub-link'i bilan ochiladi.
    """
    with allure.step(f"{tab} → {parent_leaf} → {sibling_name}"):
        try:
            page.locator("a.menu-link.menu-toggle", has_text=tab).first.click()
            leaf = page.locator(f'a.menu-link[href$="{parent_leaf}"]').first
            expect(leaf).to_be_visible()
            leaf.click()
            sibling = page.locator('a[ng-click*="openSibling"]', has_text=sibling_name).first
            expect(sibling).to_be_visible()
            sibling.click()
            expect(page).to_have_url(re.compile(re.escape(f"/a2/{a2_path}")), timeout=A2_ADMIN_FORM_TIMEOUT)
            expect(page).not_to_have_title("Smartup Online", timeout=A2_ADMIN_FORM_TIMEOUT)
            results.append((filial, a2_path, name, True, page.title()))
        except (AssertionError, PlaywrightTimeoutError) as exc:
            results.append((filial, a2_path, name, False, str(exc).splitlines()[0][:150]))
            allure.attach(page.screenshot(full_page=True),
                          name=f"MUAMMO — {a2_path}", attachment_type=allure.attachment_type.PNG)
        _back_to_menu(page)

# ----------------------------------------------------------------------------------------------------------------------

def _open_add_edit_from_list(page, filial, tab, list_path, results):
    """List formani ochib, undan +add (Создать) va +edit (qator -> Изменить) ni real user kabi ochib tekshiradi.

    Ochilish signali — formadagi "Сохранить" tugmasi ko'rinishi.
    """
    save_btn = page.locator("main").get_by_role("button", name="Сохранить")

    with allure.step(f"{tab} → {list_path} → Создать (+add)"):
        add_path = list_path.replace("_list", "+add")
        try:
            navigate_to_a2(page, tab, list_path)
            page.locator("main").get_by_role("button", name="Создать").click()
            expect(save_btn).to_be_visible()
            results.append((filial, add_path, "форма создания (+add)", True, page.url.split("?")[0]))
        except (AssertionError, PlaywrightTimeoutError) as exc:
            results.append((filial, add_path, "форма создания (+add)", False, str(exc).splitlines()[0][:150]))
            allure.attach(page.screenshot(full_page=True),
                          name=f"MUAMMO — {add_path}", attachment_type=allure.attachment_type.PNG)
        if "/a2/" in page.url and "add" in page.url.split("/a2/")[1]:
            page.go_back()  # list'ga qaytish

    with allure.step(f"{tab} → {list_path} → qator → Изменить (+edit)"):
        edit_path = list_path.replace("_list", "+edit")
        try:
            row = page.locator("main .smt-data-row").first
            expect(row).to_be_visible()
            row.click()
            page.locator("main").get_by_role("button", name="Изменить").click()
            expect(save_btn).to_be_visible()
            results.append((filial, edit_path, "форма изменения (+edit)", True, page.url.split("?")[0]))
        except (AssertionError, PlaywrightTimeoutError) as exc:
            results.append((filial, edit_path, "форма изменения (+edit)", False, str(exc).splitlines()[0][:150]))
            allure.attach(page.screenshot(full_page=True),
                          name=f"MUAMMO — {edit_path}", attachment_type=allure.attachment_type.PNG)

# ----------------------------------------------------------------------------------------------------------------------

def _report(results):
    """Natijalarni filial bo'yicha guruhlab konsol/Allure hisobotiga chiqaradi."""
    broken = [r for r in results if not r[3]]
    lines = [
        "A2 ADMIN FORMALAR — real menyu (tab → leaf) orqali ochilish",
        f"  Server: {company_url()}",
        f"  Jami: {len(results)} | ✅ OK: {len(results) - len(broken)} | ⚠ Muammo: {len(broken)}",
    ]
    cur_filial = None
    for filial, path, name, ok, detail in results:
        if filial != cur_filial:
            lines.append(f"\n  [{filial}]")
            cur_filial = filial
        icon = "✅" if ok else "⚠"
        note = "" if ok else f"  <- {detail}"
        lines.append(f"    {icon}  {name}  ({path}){note}")

    report = "\n".join(lines)
    allure.attach(report, name="HISOBOT", attachment_type=allure.attachment_type.TEXT)
    print("\n" + report + "\n")

    if broken:
        raise AssertionError(
            f"{len(broken)} ta admin a2 forma menyudan ochilmadi: "
            + ", ".join(r[1] for r in broken)
            + "\nTo'liq hisobot Allure 'HISOBOT' attachmentida."
        )

# ----------------------------------------------------------------------------------------------------------------------

def run_a2_admin_forms(page):
    """Testcase: admin profildagi a2 formalarni ESKI MENYU orqali (real user yo'li) ochib tekshirish.

    1. Birinchi "Администрирование" bo'lmagan filialga o'tib, undagi a2 formalarni menyudan ochish.
    2. "Администрирование" filialiga o'tib, company_client_list ni ochish.
    3. Shu list'dan Создать (+add) va qator -> Изменить (+edit) formalarini ochish.
    4. Har forma ochilganини tekshirib, xatoда to'xtamay natijalarni yig'ish va oxirида hisobot berish.
    """
    base = BasePage(page)
    results = []

    operational_filial = _first_operational_filial(page)
    with allure.step(f"1 - '{operational_filial}' filialidagi formalar"):
        base.switch_filial(name=operational_filial)
        for tab, path, name in OPERATIONAL_FORMS:
            _open_form(page, operational_filial, tab, path, name, results)
        for tab, parent_leaf, sibling_name, a2_path, name in SIBLING_FORMS:
            _open_a2_via_sibling(page, operational_filial, tab, parent_leaf, sibling_name, a2_path, name, results)

    with allure.step(f"2 - '{ADMIN_FILIAL}' filialidagi formalar"):
        base.switch_filial(name=ADMIN_FILIAL)
        for tab, path, name in ADMIN_FILIAL_FORMS:
            _open_form(page, ADMIN_FILIAL, tab, path, name, results)

    with allure.step("3 - Клиенты OAuth2: +add va +edit (list ichidan)"):
        _open_add_edit_from_list(page, ADMIN_FILIAL, "Главное", "biruni/kauth/company_client_list", results)

    with allure.step("4 - Yakuniy hisobot"):
        _report(results)

# ----------------------------------------------------------------------------------------------------------------------

@allure.title("A2 admin formalar — menyu orqali ochilish smoke")
def test_a2_admin_forms(page):
    authorization(page, who="admin")  # login -> default filial "Администрирование"
    run_a2_admin_forms(page)
