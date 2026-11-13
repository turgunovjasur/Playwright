"""Bir testcase'ga tegishli ma'lumotlar; boshqa testdan ID olinmaydi."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OrderCase:
    """Fixture yaratgan kataloglar va testcase yaratgan hujjatlar registri."""

    key: str
    room: str
    staff: str
    client: str
    product: str
    product_code: str
    bonus_product: str
    bonus_code: str
    price_type: str
    reference: str
    directory: Path
    warehouse: str = "Основной склад"
    currency: str = "Доллар США"
    product_id: int | None = None
    bonus_id: int | None = None
    receipt_number: str = ""
    receipt_posted: bool = False
    client_attached: bool = False
    orders: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    action_names: list[str] = field(default_factory=list)
    cashins: list[str] = field(default_factory=list)  # Own payment numbers.
    returns: list[str] = field(default_factory=list)  # Own Return IDs.
    allocations: list[str] = field(default_factory=list)  # Own offset numbers.
    allocation_pending: bool = False
    return_pending: bool = False
    import_settings: dict | None = None
