"""Order testcase konteksti; bu model UI yoki API mutatsiya qilmaydi."""
from dataclasses import dataclass, field
from decimal import Decimal
import json
from typing import Any, Callable


def _json_value(value):
    """Hisobot qiymatini nusxalaydi; Decimal aniqligi yo'qolmaydi."""
    def encode(item):
        if isinstance(item, Decimal):
            return str(item)
        raise TypeError(f"Hisobot uchun qo'llanmaydigan qiymat turi: {type(item).__name__}")

    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False, default=encode))


@dataclass
class OrderContext:
    page: Any
    baseline: dict
    code: str
    room: str
    staff: str
    client: str
    product: str
    bonus_product: str
    price_type: str
    reference: str
    promotions: dict
    orders: list = field(default_factory=list)
    payments: list = field(default_factory=list)
    allocations: list = field(default_factory=list)
    returns: list = field(default_factory=list)
    workflow: dict = field(default_factory=dict)
    observations: list = field(default_factory=list)
    checkpoint: Callable[[], None] = field(default=lambda: None, repr=False)

    def remember_order(self, order_id):
        """Saqlangan order IDsi keyingi UI qadamidan oldin ledgerga tushadi."""
        if order_id not in self.orders:
            self.orders.append(order_id)
        self.checkpoint()

    def check(self, label, expected, actual):
        """Real o'qilgan qiymatni taqqoslaydi va xatodan oldin dalilni saqlaydi."""
        passed = actual == expected
        observation = {
            "label": label,
            "expected": _json_value(expected),
            "actual": _json_value(actual),
            "status": "passed" if passed else "failed",
        }
        self.observations.append(observation)
        self.checkpoint()
        if not passed:
            raise AssertionError(
                f"{label}: kutilgan qiymat — {observation['expected']}; "
                f"amalda ko'rilgan qiymat — {observation['actual']}"
            )
