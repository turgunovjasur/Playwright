"""Legacy navbar formalarining markaziy inventory public API'si."""

from tests.smoke.test_forms.inventory.constants import OPERATIONAL_PLACEHOLDER
from tests.smoke.test_forms.inventory.glavnoe import (
    FORM_BUCKETS as GLAVNOE_FORM_BUCKETS,
)
from tests.smoke.test_forms.inventory.prodaja import (
    FORM_BUCKETS as PRODAJA_FORM_BUCKETS,
)
from tests.smoke.test_forms.inventory.sklad import (
    FORM_BUCKETS as SKLAD_FORM_BUCKETS,
)
from tests.smoke.test_forms.inventory.finansy import (
    FORM_BUCKETS as FINANSY_FORM_BUCKETS,
)
from tests.smoke.test_forms.inventory.spravochniki import (
    FORM_BUCKETS as SPRAVOCHNIKI_FORM_BUCKETS,
)


_LEGACY_FORM_BUCKETS_BY_NAVBAR = {
    "Главное": GLAVNOE_FORM_BUCKETS,
    "Продажа": PRODAJA_FORM_BUCKETS,
    "Склад": SKLAD_FORM_BUCKETS,
    "Финансы": FINANSY_FORM_BUCKETS,
    "Справочники": SPRAVOCHNIKI_FORM_BUCKETS,
}


def _copy_definition(definition):
    copied = dict(definition)
    if "page_links" in copied:
        copied["page_links"] = list(copied["page_links"])
    return copied


def get_legacy_form_buckets(navbar_tab):
    """Navbar uchun mutationdan himoyalangan forma bucket nusxalarini qaytaradi."""
    normalized_tab = str(navbar_tab or "").strip()
    try:
        buckets = _LEGACY_FORM_BUCKETS_BY_NAVBAR[normalized_tab]
    except KeyError as exc:
        available = ", ".join(_LEGACY_FORM_BUCKETS_BY_NAVBAR)
        raise ValueError(
            f"Legacy navbar inventory topilmadi: {normalized_tab!r}. "
            f"Mavjud navbarlar: {available}"
        ) from exc

    return tuple(
        {
            "forms": [_copy_definition(definition) for definition in bucket["forms"]],
            "filial": bucket["filial"],
            "section": bucket["section"],
        }
        for bucket in buckets
    )


__all__ = ["OPERATIONAL_PLACEHOLDER", "get_legacy_form_buckets"]
