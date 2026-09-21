"""Legacy/A2 uchun bir xil observation; UI amallari qayta bajarilmaydi."""

import inspect
import re
from functools import wraps

from utils.report_context import current_test, page_context, page_location, record_menu, record_observation, reporting_note


def capture_filial(page):
    """Ko'rinadigan filialni waitsiz oladi; selectorni ochmaydi/almashtirmaydi."""
    context = page_context(page)
    if context.get("filial") or page.is_closed():
        return
    try:
        names = page.locator(".header-logo.custom-dropdown:visible .dropdown-locations-custom .project-filial p").all_text_contents()
        if len(names) >= 2:
            context["filial"] = " ".join(names[1].split())
            return
        if "/a2/" in page.url:
            trigger = page.locator("header").get_by_role("button", name=re.compile(r"^\s*(?:TRADE|SFA)\b", re.I)).filter(visible=True)
            names = trigger.all_text_contents()
            if len(names) == 1:
                context["filial"] = re.sub(r"^(?:TRADE|SFA)\s*", "", " ".join(names[0].split()), flags=re.I)
    except Exception:
        reporting_note("Joriy filial nomini UI'dan o'qib bo'lmadi.")


def report_web_action(method):
    signature = inspect.signature(method)

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        # Click navigatsiya qilishi mumkin: grid/form joyini amaldan oldin olamiz.
        location = None
        if current_test() is not None:
            try:
                location = page_location(self.page)
            except Exception:
                reporting_note("Ayrim forma yo'llarini qayd etib bo'lmadi.")
        result = method(self, *args, **kwargs)
        if current_test() is None:
            return result
        try:
            arguments = signature.bind(self, *args, **kwargs)
            arguments.apply_defaults()
            values = arguments.arguments
            if method.__name__ == "navigate_to":
                record_menu(self.page, [values["tab"], values["name"]])
            elif method.__name__ == "navigate_to_form":
                links = values["page_links"] or []
                links = [links] if isinstance(links, str) else links
                record_menu(self.page, [values["navbar_tab"], values["menu_column"], values["menu_item"], *links])
            elif method.__name__ == "grid" and values["text"] is not None and result is not False:
                texts = [value for value in (values["text"], *values["contains"]) if isinstance(value, (str, int, float))]
                record_observation(self.page, "Ro'yxatda topilgan qiymatlar", texts, location=location)
            elif method.__name__ == "form_view":
                value = result if values["return_value"] else values["expect_value"]
                if isinstance(value, (str, int, float)):
                    record_observation(self.page, "Formada tekshirilgan qiymat", {str(values["label"]): value}, location=location)
            elif method.__name__ == "expect_page":
                location = page_location(self.page)
                if location["ids"]:
                    fields = {"Forma": values["heading"]} if isinstance(values["heading"], str) else {}
                    fields.update(location["ids"])
                    record_observation(self.page, "Ochilgan obyekt", fields, location=location)
        except Exception:
            # Reporting asl test natijasini o'zgartirmaydi; secretli error yozilmaydi.
            reporting_note("Ayrim UI ma'lumotlarini hisobotga yozib bo'lmadi.")
        return result

    return wrapped
