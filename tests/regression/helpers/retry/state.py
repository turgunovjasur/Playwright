"""Per-case retry evidence. Credentials and HTTP bodies are never journalled."""
from contextvars import ContextVar
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid4 as random_uuid
from zoneinfo import ZoneInfo

from tests.regression.test_orders.helpers.models import _json_value

ACTIVE = ContextVar("order_retry_case", default=None)
FIXTURES = ("catalog_data", "business_promotions", "payment_clients", "mandatory_data", "bonus_limit_data",
            "workflow_data", "mixed_promotions_data", "product_limit_data")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(_json_value(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def digest(value):
    return hashlib.sha256(json.dumps(_json_value(value), sort_keys=True).encode()).hexdigest()


def day():
    return datetime.now(ZoneInfo("Asia/Tashkent")).date().isoformat()


class RetryBlocked(AssertionError):
    """A write cannot be safely repeated; never convert this into PASS."""


class Journal:
    def __init__(self, item, directory, source=None):
        self.item, self.directory = item, directory
        self.source = source or {}
        self.counters = {}
        self.data = {"nodeid": item.nodeid, "day": day(), "identities": {}, "operations": {},
                     "retry": bool(source), "events": []}
        self.save()

    def save(self):
        write(self.directory / "retry-journal.json", self.data)

    def event(self, kind, **fields):
        self.data["events"].append({"kind": kind, **fields})
        self.save()

    def identity(self, name):
        index = self.counters.get(name, 0)
        self.counters[name] = index + 1
        key = f"{name}:{index}"
        value = self.source.get("identities", {}).get(key) or random_uuid().hex
        self.data["identities"][key] = value
        self.save()  # before the name/number can reach any Save
        return UUID(value)

    def intent(self, key, **metadata):
        previous = self.data["operations"].get(key, {})
        self.data["operations"][key] = {**previous, **metadata,
                                        "state": previous.get("state", "intent")}
        self.save()  # a timeout after this point is an uncertain outcome

    def complete(self, key, **metadata):
        operation = self.data["operations"][key]
        operation.update(**metadata)
        if operation.get("state") not in {"confirmed", "verified"}:
            operation["state"] = "returned"
        self.save()

    def confirm(self, key, *, entity_id=None, **metadata):
        operation = self.data["operations"].setdefault(key, {})
        operation.update(state="confirmed", **metadata)
        if entity_id is not None:
            operation["entity_id"] = str(entity_id)
        self.save()

    def verify(self, key, **metadata):
        operation = self.data["operations"].get(key)
        if not operation or operation.get("state") not in {"confirmed", "verified"}:
            raise RetryBlocked("Tasdiqlanmagan operatsiya verified bo‘la olmaydi: " + key)
        operation.update(state="verified", **metadata)
        self.save()

    def previous(self, key):
        return self.data["operations"].get(key) or self.source.get("operations", {}).get(key)


def stable_uuid(logical_key=None):
    """Same call site and occurrence retains its unique identity across attempts."""
    journal = ACTIVE.get()
    if journal is None:
        return random_uuid()
    import inspect
    caller = inspect.currentframe().f_back
    name = f"{Path(caller.f_code.co_filename).name}:{caller.f_code.co_name}:" + (str(logical_key) if logical_key is not None else str(caller.f_lineno))
    return journal.identity(name)


def fixture_state(request, name):
    if name not in FIXTURES:
        raise ValueError("Retry uchun noma’lum fixture")
    group = request.node.get_closest_marker("order_group").args[0]
    config = request.config
    states = getattr(config, "_retry_states", None)
    if states is None:
        states = config._retry_states = {}
    values = states.setdefault(group, {})
    if name not in values:
        source = getattr(config, "_retry_plan", {}).get("states", {}).get(group, {})
        values[name] = deepcopy(source.get(name, {}))
    return values[name]


def snapshot(item):
    group = item.get_closest_marker("order_group").args[0]
    return _json_value(getattr(item.config, "_retry_states", {}).get(group, {}))
