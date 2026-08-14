"""Deklarativ forma definitionlarini monitor case/inventoryga normalizatsiya qiladi."""

from __future__ import annotations

from tests.smoke.test_forms.monitoring.checks import clean_text
from tests.smoke.test_forms.inventory.skipped_forms import skipped_form


NO_MENU_COLUMN = "<ustunsiz>"


def form_test_identity(*, shell, navbar_tab, menu_column):
    normalized_shell = clean_text(shell).lower()
    normalized_tab = clean_text(navbar_tab)
    normalized_column = clean_text(menu_column) or NO_MENU_COLUMN
    if not normalized_shell:
        raise ValueError("Form test identity uchun shell majburiy")
    if not normalized_tab:
        raise ValueError("Form test identity uchun navbar_tab majburiy")
    return f"{normalized_shell}::{normalized_tab}::{normalized_column}"


def build_form_label(
    *,
    menu_item,
    page_links=None,
    action=None,
    add_icon=False,
    label=None,
):
    explicit_label = clean_text(label)
    if explicit_label:
        return explicit_label
    parts = [clean_text(menu_item)]
    if action is not None:
        parts.extend(["Создать dropdown", clean_text(action)])
    parts.extend(clean_text(link) for link in (page_links or []))
    if add_icon:
        parts.append("+add icon")
    return " → ".join(part for part in parts if part)


def form_case_key(case):
    return (
        clean_text(case.get("shell")).lower(),
        clean_text(case.get("navbar_tab")),
        clean_text(case.get("menu_column")),
        clean_text(case.get("filial")),
        clean_text(case.get("menu_item")),
        clean_text(case.get("action")),
        tuple(clean_text(link) for link in (case.get("page_links") or [])),
        clean_text(case.get("expected_path")).strip("/"),
    )


def form_case(
    *,
    number,
    filial,
    navbar_tab,
    menu_column,
    menu_item,
    title,
    expected_path,
    page_links=None,
    action=None,
    add_icon=False,
    ready=None,
    shell="legacy",
    section=None,
    screenshot_mask=None,
    label=None,
):
    """Monitor uchun barcha runnerlarda bir xil planned-case yozuvini yaratadi."""
    if not isinstance(number, int) or number < 1:
        raise ValueError(f"Forma raqami musbat int bo'lishi kerak: {number!r}")
    for field_name, value in (
        ("filial", filial),
        ("navbar_tab", navbar_tab),
        ("menu_item", menu_item),
        ("title", title),
        ("expected_path", expected_path),
    ):
        if not clean_text(value):
            raise ValueError(f"Forma case uchun {field_name} majburiy")
    if action is not None and add_icon:
        raise ValueError("Forma case bir vaqtda action va add_icon ishlata olmaydi")

    links = list(page_links or [])
    normalized_shell = clean_text(shell).lower() or "legacy"
    case = {
        "number": number,
        "filial": filial,
        "navbar_tab": navbar_tab,
        "menu_column": menu_column,
        "menu_item": menu_item,
        "title": title,
        "expected_path": expected_path,
        "page_links": links,
        "action": action,
        "add_icon": bool(add_icon),
        "ready": ready,
        "shell": normalized_shell,
        "section": section,
        "test_identity": form_test_identity(
            shell=normalized_shell,
            navbar_tab=navbar_tab,
            menu_column=menu_column,
        ),
        "label": build_form_label(
            menu_item=menu_item,
            page_links=links,
            action=action,
            add_icon=add_icon,
            label=label,
        ),
    }
    if screenshot_mask is not None:
        case["screenshot_mask"] = screenshot_mask
    return case


def build_form_case_plan(
    definitions,
    *,
    start_number,
    filial,
    navbar_tab=None,
    shell=None,
    section=None,
):
    """Skip registry'ni chiqarib, yagona planned-case ro'yxatini yaratadi."""
    return build_form_case_inventory(
        definitions,
        start_number=start_number,
        filial=filial,
        navbar_tab=navbar_tab,
        shell=shell,
        section=section,
    )["planned"]


def build_form_case_inventory(
    definitions,
    *,
    start_number,
    filial,
    navbar_tab=None,
    shell=None,
    section=None,
):
    """Aktiv va ataylab skip qilingan formalarni bitta inventoryda qaytaradi."""
    planned = []
    skipped = []
    seen = set()
    for definition in definitions:
        links = list(definition.get("page_links") or [])
        title = (
            definition.get("title")
            or (links[-1] if links else None)
            or definition.get("action")
            or definition["menu_item"]
        )
        expected_path = definition.get("expected_path") or definition.get("path")
        effective_tab = definition.get("navbar_tab") or navbar_tab
        effective_shell = definition.get("shell") or shell or "legacy"
        effective_section = definition.get("section") or section
        normalized = form_case(
            number=start_number + len(planned),
            filial=filial,
            navbar_tab=effective_tab,
            menu_column=definition.get("menu_column"),
            menu_item=definition["menu_item"],
            title=title,
            expected_path=expected_path,
            page_links=links,
            action=definition.get("action"),
            add_icon=definition.get("add_icon", False),
            ready=definition.get("ready"),
            shell=effective_shell,
            section=effective_section,
            screenshot_mask=definition.get("screenshot_mask"),
            label=definition.get("label"),
        )
        duplicate_key = form_case_key(normalized)
        if duplicate_key in seen:
            raise ValueError(
                "Bitta inventoryda takrorlangan forma bor: "
                f"{normalized['label']} | {normalized['expected_path']}"
            )
        seen.add(duplicate_key)

        skip_metadata = skipped_form(definition, navbar_tab=effective_tab)
        if skip_metadata:
            skipped.append(
                {
                    "filial": filial,
                    "navbar_tab": effective_tab,
                    "menu_column": definition.get("menu_column"),
                    "menu_item": definition["menu_item"],
                    "title": title,
                    "expected_path": expected_path,
                    "section": effective_section,
                    "shell": normalized["shell"],
                    "test_identity": normalized["test_identity"],
                    "label": normalized["label"],
                    "reason": skip_metadata["reason"],
                }
            )
            continue
        normalized["number"] = start_number + len(planned)
        planned.append(normalized)
    return {"planned": planned, "skipped": skipped}
