"""API equivalent of UI setup step 21: Room Attachment."""

import allure
import pytest

from tests.api.client import APIError


pytestmark = [pytest.mark.api_setup, allure.epic("API"),
              allure.feature("Setup"), allure.story("Room Attachment")]


def run_room_attachment(api_setup):
    """3 - Ensure the built-in promotion price type belongs to the filial
    4 - Verify the promotion price type is attached to the room
    """
    s = api_setup
    api = s.user()
    route = "anor/mrf/room_attachment"
    for kind, key, names in (
        ("payment_type", "payment_type_id", {"Наличные деньги", "Терминал", "Перечисление", "Чековая книжка"}),
        ("warehouse", "warehouse_id", {"Основной склад"}),
        ("cashbox", "cashbox_id", {"Основная касса"}),
        ("natural_person", "person_id", {f"natural_client-pw{s.code}"}),
    ):
        with allure.step(f"1 - Read and attach {kind} to the setup room"):
            data = {"room_id": s["room_id"], "attached": "N"}
            available = api.table(route + ":table_" + kind, [key, "name"], data=data)
            selected = [row for row in available if row["name"] in names]
            if selected:
                ids = [row[key] for row in selected]
                value = ids[0] if kind == "natural_person" else ids
                if kind != "payment_type" and len(ids) != 1:
                    raise APIError(f"Expected one baseline {kind} to attach")
                api.call(route + "$attach_" + kind, api.context(room_id=s["room_id"], **{key: value}))
        with allure.step(f"2 - Verify attached {kind}"):
            attached = api.table(route + ":table_" + kind, [key, "name"], data={"room_id": s["room_id"], "attached": "Y"})
            if not names.issubset({row["name"] for row in attached}):
                raise APIError(f"Missing required room attachment: {kind}")
    with allure.step("3 - Ensure the built-in promotion price type belongs to the filial"):
        columns = ["price_type_id", "name"]
        data = {"room_id": s["room_id"], "attached": "Y"}
        attached = api.table(route + ":table_price_type", columns, data=data)
        if not any(row["name"] == "Акция" for row in attached):
            available = api.table(route + ":table_price_type", columns, data={**data, "attached": "N"})
            matches = [row for row in available if row["name"] == "Акция"]
            if not matches:
                catalog = api.one("anor/mkr/price_type_list+attach:table", columns, filters=["name", "=", "Акция"])
                api.call("anor/mkr/price_type_list+attach$attach", api.context(room_id=s["room_id"], price_type_id=catalog["price_type_id"]))
                matches = [catalog]
            if len(matches) != 1:
                raise APIError("Promotion price type is ambiguous")
            api.call(route + "$attach_price_type", api.context(room_id=s["room_id"], price_type_id=matches[0]["price_type_id"]))
    with allure.step("4 - Verify the promotion price type is attached to the room"):
        rows = api.table(route + ":table_price_type", columns, data=data)
        if not any(row["name"] == "Акция" for row in rows):
            raise APIError("Promotion price type is missing from the room")


@allure.title("API 21 - Room Attachment")
def test_21_room_attachment(api_setup):
    run_room_attachment(api_setup)
