"""API equivalent of UI setup step 07: User Attach Form."""

import allure
import pytest

from tests.api.client import APIError


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("User Attach Form")]


def run_user_attach_form(api_setup):
    """1. Prepare dependencies. 2. Send observed requests. 3. Verify persisted state."""
    s = api_setup
    api = s.admin()
    for position, title in ((None, "Forms"), ("R", "Reports"), ("D", "Invoices"), ("E", "External systems")):
        with allure.step(f"1 - Read available {title} for the setup user"):
            endpoint = "biruni/md/user_form_list:" + ("form_table" if position is None else "other_table")
            data = {"user_id": s["user_id"], "attached": "N"}
            if position:
                data["position"] = position
            rows = api.table(endpoint, ["form", "form_name"], data=data)
        with allure.step(f"2 - Attach available {title}"):
            if rows:
                api.call("biruni/md/user_form_list$attach", {"user_id": s["user_id"], "form": [r["form"] for r in rows]})
        with allure.step(f"3 - Verify no {title} remains available"):
            if api.table(endpoint, ["form"], data=data):
                raise APIError(f"Some {title} remain unattached")


@allure.title("API 07 - User Attach Form")
def test_07_user_attach_form(api_setup):
    run_user_attach_form(api_setup)
