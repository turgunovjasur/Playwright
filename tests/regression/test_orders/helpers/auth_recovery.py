"""Order regression auth recovery; business requests are never replayed here.

An active license assignment is checked before one password confirmation.
Revoked/expired licenses and a repeated denial remain visible failures.
"""
from datetime import datetime, timezone
import json
import os
from time import sleep
from pathlib import Path

import allure

from tests.api.client import APIError, SmartupAPI
from tests.api.state import SetupState
from tests.regression.helpers.session_recovery import recover_session
from tests.regression.helpers.environment import RegressionEnvironmentError, classify_login_error


LICENSE_MESSAGE = "Нет лицензии для входа в систему!"


def _record(directory, event):
    event = {"time_utc": datetime.now(timezone.utc).isoformat(), **event}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "auth-recovery.jsonl"
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    if event.get("status") == "recovered":
        allure.dynamic.tag("session-recovered")
    allure.attach(json.dumps(event, ensure_ascii=False, indent=2),
                  "Sessiyani tiklash — urinish va natija",
                  allure.attachment_type.JSON)


def verify_license(baseline, directory):
    """Read the exact setup license and membership; never attach/detach users."""
    state = SetupState(Path(directory) / "auth-check-state.json", dict(baseline))
    try:
        api = state.admin(head_filial=True)
        rows = api.table("biruni/kl/license_list:table_license",
                         ["license_id", "license_name", "status"],
                         filters=["status", "=", ["A", "P"]])
        matches = [row for row in rows
                   if str(row["license_id"]) == str(baseline["license_id"])
                   and row["license_name"] == "ERP users" and row["status"] == "A"]
        event = {"license_id": str(baseline["license_id"]),
                 "user_id": str(baseline["user_id"]),
                 "active": len(matches) == 1, "attached": False}
        if matches:
            users = api.table("biruni/kl/license_user_list:table", ["user_id"],
                             data={"license_id": baseline["license_id"],
                                   "attached": "Y", "filter_license_id": None})
            event["attached"] = str(baseline["user_id"]) in {
                str(row["user_id"]) for row in users}
        _record(directory, {"kind": "license_check", **event})
        if not event["active"] or not event["attached"]:
            raise RegressionEnvironmentError("Regression user litsenziyasi faol emas yoki userdan uzilgan. "
                           "Qayta login va avtomatik biriktirish bajarilmadi.")
        return event
    finally:
        state.close()


class RegressionSetupState(SetupState):
    """Only regression preparations opt in; API setup and smoke stay unchanged."""

    def admin(self, *, head_filial=False):
        try:
            return super().admin(head_filial=head_filial)
        except APIError as error:
            classify_login_error(error)
            raise

    def user(self, *, fresh=False):
        if not fresh and "user" in self.clients:
            return self.clients["user"].use_filial(self["filial_id"])
        api = self.clients.get("user") or SmartupAPI(self["url"])
        directory = self.path.parent
        recovery_kind = None
        try:
            try:
                info = api.login(f"user-pw{self.code}@{self['company_code']}",
                                 os.environ["USER_PASSWORD"])
            except APIError as error:
                if str(error) == "POST biruni/s$log_in: HTTP 500":
                    recovery_kind = "api_login_500"
                    _record(directory, {"kind": recovery_kind, "status": "observed",
                                        "endpoint": "biruni/s$log_in", "wait_seconds": 15})
                    step = "Login HTTP 500 — 15 soniyadan so‘ng bir marta qayta kirish"
                    sleep(15)
                elif str(error) == f"POST biruni/m:session: HTTP 401 ({LICENSE_MESSAGE})":
                    recovery_kind = "api_login_401"
                    _record(directory, {"kind": recovery_kind, "status": "observed",
                                        "endpoint": "biruni/m:session"})
                    verify_license(self.values, directory)
                    step = "Faol litsenziya tasdiqlandi — ayni cookie bilan bir marta qayta kirish"
                else:
                    raise
                with allure.step(step):
                    info = api.login(f"user-pw{self.code}@{self['company_code']}",
                                     os.environ["USER_PASSWORD"])
            if str(info["user"]["user_id"]) != str(self["user_id"]):
                raise RegressionEnvironmentError("Qayta kirgan user API setup useriga mos emas")
            if recovery_kind:
                _record(directory, {"kind": recovery_kind, "status": "recovered",
                                    "user_id": str(self["user_id"]),
                                    "business_requests_replayed": 0})
            self.clients["user"] = api
            return api.use_filial(self["filial_id"])
        except Exception as error:
            if recovery_kind:
                _record(directory, {"kind": recovery_kind, "status": "failed",
                                    "error_type": type(error).__name__})
            api.close()
            self.clients.pop("user", None)
            classify_login_error(error)
            raise



def order_session_recovery(page, baseline, directory, *, on_authenticated=None):
    """Bind the reusable controller to the setup user and Order evidence sink."""
    return recover_session(
        page, server=baseline["url"], user_id=baseline["user_id"],
        display_name=f"natural_person-pw{baseline['code']}",
        password=lambda: os.environ["USER_PASSWORD"],
        verify_license=lambda: verify_license(baseline, directory),
        record=lambda event: _record(directory, event),
        on_authenticated=on_authenticated,
    )
