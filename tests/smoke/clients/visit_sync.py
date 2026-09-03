"""Minimal ``tvt_save_person_visit`` payload va response helperlari."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from threading import Lock
import time
from zoneinfo import ZoneInfo

from utils.base_api import APIError


VISIT_ENTRY_CODE = "tvt_save_person_visit"
VISIT_SOURCE_TABLE = "MVTM_VISIT_HEADERS"
DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
VISIT_ARRAY_FIELDS = (
    "photos",
    "videos",
    "audios",
    "quizs",
    "comments",
    "orders",
    "stocks",
    "equipments",
    "equipment_requests",
    "equipment_movements",
    "repair_requests",
    "equipment_binds",
    "presentations",
    "merchandisings",
)

_ENTRY_ID_LOCK = Lock()
_LAST_ENTRY_ID = 0


@dataclass(frozen=True)
class MinimalVisit:
    """Yuboriladigan minimal visit va web correlation qiymatlari."""

    entry_id: int
    visit_note: str
    begun_on: str
    ended_on: str
    spent_time: int
    envelope: dict


@dataclass(frozen=True)
class VisitSyncResult:
    """Sync response ichidagi bitta visit natijasi."""

    entry_id: int
    server_payload: str


@dataclass(frozen=True)
class OrderVisit:
    """Bitta normal goods orderi bor visit correlation qiymatlari."""

    entry_id: int
    visit_note: str
    begun_on: str
    ended_on: str
    spent_time: int
    order_note: str
    deal_time: str
    delivery_date: str
    price: str
    quantity: str
    vat_percent: int
    envelope: dict


def _positive_int(value, *, field):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Minimal visit {field} integer emas") from exc
    if parsed <= 0:
        raise ValueError(f"Minimal visit {field} musbat integer emas")
    return parsed


def _positive_decimal_string(value, *, field):
    text = str(value).strip()
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Order visit {field} decimal emas") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise ValueError(f"Order visit {field} musbat decimal emas")
    return text


def next_visit_entry_id():
    """Process ichida takrorlanmaydigan 13 xonali epoch-millisecond ID beradi."""
    global _LAST_ENTRY_ID
    with _ENTRY_ID_LOCK:
        current = time.time_ns() // 1_000_000
        _LAST_ENTRY_ID = max(current, _LAST_ENTRY_ID + 1)
        if not 1_000_000_000_000 <= _LAST_ENTRY_ID <= 9_999_999_999_999:
            raise ValueError("Visit entry_id 13 xonali epoch-millisecond emas")
        return _LAST_ENTRY_ID


def build_minimal_visit(
    *,
    filial_id,
    room_id,
    robot_id,
    client_person_id,
    entry_id=None,
    visit_note=None,
    ended_at=None,
    spent_time=60,
    deal_recom_calculation_method="",
    timezone_code="Asia/Tashkent",
):
    """Media, stock va ordersiz minimal mobile visit envelope yaratadi."""
    filial_id = _positive_int(filial_id, field="filial_id")
    room_id = _positive_int(room_id, field="room_id")
    robot_id = _positive_int(robot_id, field="robot_id")
    client_person_id = _positive_int(
        client_person_id, field="client_person_id"
    )
    entry_id = next_visit_entry_id() if entry_id is None else _positive_int(
        entry_id, field="entry_id"
    )
    if not 1_000_000_000_000 <= entry_id <= 9_999_999_999_999:
        raise ValueError("Minimal visit entry_id 13 xonali bo'lishi kerak")

    spent_time = _positive_int(spent_time, field="spent_time")
    if deal_recom_calculation_method not in {"", "I", "GT"}:
        raise ValueError(
            "deal_recom_calculation_method '', 'I' yoki 'GT' bo'lishi kerak"
        )

    timezone = ZoneInfo(timezone_code)
    ended_at = ended_at or datetime.now(timezone)
    if ended_at.tzinfo is None:
        ended_at = ended_at.replace(tzinfo=timezone)
    else:
        ended_at = ended_at.astimezone(timezone)
    begun_at = ended_at - timedelta(seconds=spent_time)

    begun_on = begun_at.strftime(DATETIME_FORMAT)
    ended_on = ended_at.strftime(DATETIME_FORMAT)
    visit_note = str(
        visit_note or f"playwright-mobile-visit-{entry_id}"
    ).strip()
    if not visit_note:
        raise ValueError("Minimal visit visit_note bo'sh bo'lmasligi kerak")

    value = {
        "filial_id": filial_id,
        "room_id": room_id,
        "robot_id": robot_id,
        "person_id": client_person_id,
        "begun_on": begun_on,
        "ended_on": ended_on,
        "spent_time": spent_time,
        "start_location": "",
        "end_location": "",
        "person_closed": "N",
        "has_postponed_order": "N",
        "mobile_visit_id": entry_id,
        "deal_recom_calculation_method": deal_recom_calculation_method,
        "visit_note": visit_note,
    }
    value.update({field: [] for field in VISIT_ARRAY_FIELDS})

    envelope = {
        "laststamp": "",
        "entries": [
            {
                "entry_id": entry_id,
                "filial_id": filial_id,
                "entry_code": VISIT_ENTRY_CODE,
                "value": value,
                "server_result": "",
            }
        ],
        "execute_tape": "N",
    }
    return MinimalVisit(
        entry_id=entry_id,
        visit_note=visit_note,
        begun_on=begun_on,
        ended_on=ended_on,
        spent_time=spent_time,
        envelope=envelope,
    )


def build_order_visit(
    *,
    filial_id,
    room_id,
    robot_id,
    client_person_id,
    sales_manager_id,
    currency_id,
    payment_type_id,
    price_type_id,
    warehouse_id,
    product_id,
    entry_id=None,
    visit_note=None,
    order_note=None,
    ended_at=None,
    spent_time=60,
    price="7000",
    quantity="1",
    vat_percent=0,
    deal_recom_calculation_method="",
    timezone_code="Asia/Tashkent",
):
    """Bitta normal goods orderi bilan mobile visit envelope yaratadi."""
    sales_manager_id = _positive_int(sales_manager_id, field="sales_manager_id")
    currency_id = _positive_int(currency_id, field="currency_id")
    payment_type_id = _positive_int(payment_type_id, field="payment_type_id")
    price_type_id = _positive_int(price_type_id, field="price_type_id")
    warehouse_id = _positive_int(warehouse_id, field="warehouse_id")
    product_id = _positive_int(product_id, field="product_id")
    price = _positive_decimal_string(price, field="price")
    quantity = _positive_decimal_string(quantity, field="quantity")
    try:
        vat_percent = int(vat_percent)
    except (TypeError, ValueError) as exc:
        raise ValueError("Order visit vat_percent integer emas") from exc
    if vat_percent < 0:
        raise ValueError("Order visit vat_percent manfiy bo'lishi mumkin emas")

    minimal = build_minimal_visit(
        filial_id=filial_id,
        room_id=room_id,
        robot_id=robot_id,
        client_person_id=client_person_id,
        entry_id=entry_id,
        visit_note=visit_note,
        ended_at=ended_at,
        spent_time=spent_time,
        deal_recom_calculation_method=deal_recom_calculation_method,
        timezone_code=timezone_code,
    )
    value = minimal.envelope["entries"][0]["value"]
    deal_time = minimal.ended_on
    delivery_date = (
        datetime.strptime(deal_time, DATETIME_FORMAT) + timedelta(days=1)
    ).strftime("%d.%m.%Y")
    order_note = str(
        order_note or f"playwright-mobile-order-{minimal.entry_id}"
    ).strip()
    if not order_note:
        raise ValueError("Order visit order_note bo'sh bo'lmasligi kerak")

    value["orders"] = [
        {
            "filial_id": _positive_int(filial_id, field="filial_id"),
            "subfilial_id": None,
            "room_id": _positive_int(room_id, field="room_id"),
            "person_id": _positive_int(client_person_id, field="client_person_id"),
            "currency_id": currency_id,
            "deal_time": deal_time,
            "delivery_date": delivery_date,
            "sales_manager_id": sales_manager_id,
            "robot_id": _positive_int(robot_id, field="robot_id"),
            "expeditor_id": None,
            "payment_type_id": payment_type_id,
            "agreement_cashing_date": None,
            "checkbook_amount": None,
            "check_number": None,
            "van_id": None,
            "contract_id": None,
            "status": "N",
            "invoice_number": None,
            "source_table": VISIT_SOURCE_TABLE,
            "source_id": minimal.entry_id,
            "note": order_note,
            "return_reason_id": None,
            "delivery_address_short": None,
            "delivery_address_full": None,
            "delivery_latlng": None,
            "request_id": None,
            "exchange_warehouse_id": None,
            "with_promotion": "N",
            "self_shipment": "N",
            "consignment_responsible_id": None,
            "items": [
                {
                    "inventory_kind": "G",
                    "price_type_id": price_type_id,
                    "warehouse_id": warehouse_id,
                    "product_id": product_id,
                    "card_id": None,
                    "vat_percent": vat_percent,
                    "price": price,
                    "quantity": quantity,
                    "margin_value": None,
                    "bonus_id": None,
                    "product_margins": [],
                    "is_in_mml": "N",
                    "recom_quant": None,
                    "recom_product_id": None,
                    "product_kit_id": [],
                    "is_exchange": "N",
                    "marking_ids": [],
                }
            ],
            "consignments": [],
            "deal_note": "",
        }
    ]
    return OrderVisit(
        entry_id=minimal.entry_id,
        visit_note=minimal.visit_note,
        begun_on=minimal.begun_on,
        ended_on=minimal.ended_on,
        spent_time=minimal.spent_time,
        order_note=order_note,
        deal_time=deal_time,
        delivery_date=delivery_date,
        price=price,
        quantity=quantity,
        vat_percent=vat_percent,
        envelope=minimal.envelope,
    )


def parse_visit_sync_response(response_text, *, entry_id):
    """Plain-text sync javobidan yuborilgan entry natijasini ajratadi."""
    entry_id = _positive_int(entry_id, field="entry_id")
    for raw_line in str(response_text or "").splitlines():
        line = raw_line.strip("\r")
        if not line or line.startswith("TA#") or line[0] not in {"S", "E"}:
            continue

        record, separator, payload = line.partition("\t")
        record_id = record[1:]
        if not record_id.isdigit() or int(record_id) != entry_id:
            continue
        if line[0] == "E":
            message = payload.strip() if separator else "server error text bermadi"
            raise APIError(
                f"Mobile visit entry_id={entry_id} rad etildi: {message}"
            )
        return VisitSyncResult(
            entry_id=entry_id,
            server_payload=payload.strip() if separator else "",
        )

    raise APIError(
        f"Mobile sync javobida entry_id={entry_id} uchun S/E natija topilmadi"
    )
