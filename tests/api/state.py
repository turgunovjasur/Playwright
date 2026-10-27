"""Isolated setup state and parameterized, network-derived request payloads."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from tests.api.client import APIError, SmartupAPI, positive_id


CONTRACTS = json.loads(Path(__file__).with_name("contracts.json").read_text(encoding="utf-8"))


class SetupState:
    def __init__(self, path, values):
        self.path = path
        self.values = values
        self.clients = {}

    def __getitem__(self, key):
        value = self.values.get(key)
        if value in (None, ""):
            raise APIError(f"API baseline is missing {key!r}; run its preceding setup step")
        return value

    @property
    def code(self):
        return self["code"]

    def save(self, **values):
        self.values.update(values)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.values, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    def save_id(self, key, value):
        self.save(**{key: positive_id(value)})

    def admin(self, *, head_filial=False):
        if "admin" not in self.clients:
            api = SmartupAPI(self["url"])
            try:
                api.login(f"admin@{self['company_code']}", os.environ["COMPANY_PASSWORD"])
            except Exception:
                api.close()
                raise
            self.clients["admin"] = api
        api = self.clients["admin"]
        return api.use_filial(api.admin_filial_id if head_filial else self["filial_id"])

    def user(self, *, fresh=False):
        if fresh or "user" not in self.clients:
            api = self.clients.get("user") or SmartupAPI(self["url"])
            try:
                info = api.login(f"user-pw{self.code}@{self['company_code']}", os.environ["USER_PASSWORD"])
                if str(info["user"]["user_id"]) != str(self["user_id"]):
                    raise APIError("Authenticated user does not match the API setup user")
            except Exception:
                api.close()
                self.clients.pop("user", None)
                raise
            self.clients["user"] = api
        return self.clients["user"].use_filial(self["filial_id"])

    def payload(self, name):
        now = datetime.now(ZoneInfo("Asia/Tashkent"))
        variables = {**self.values, "user_password": os.environ["USER_PASSWORD"],
                     "today": now.strftime("%d.%m.%Y"),
                     "now": now.strftime("%d.%m.%Y %H:%M:%S"),
                     "end_date": (now + timedelta(days=30)).strftime("%d.%m.%Y")}
        def render(value):
            if isinstance(value, dict):
                return {key: render(item) for key, item in value.items()}
            if isinstance(value, list):
                return [render(item) for item in value]
            if isinstance(value, str):
                try:
                    return value.format_map(variables)
                except KeyError as exc:
                    raise APIError(f"API baseline is missing payload dependency {exc.args[0]!r}") from None
            return value
        return render(CONTRACTS[name]["payload"])

    def send(self, api, name, **overrides):
        return api.call(CONTRACTS[name]["endpoint"], {**self.payload(name), **overrides})

    def close(self):
        for client in self.clients.values():
            client.close()
