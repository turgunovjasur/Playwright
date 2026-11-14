"""Order uchun mustaqil 10% katalog skidkasi va uning ikki bog'lanishi.

UI dalili: order-full-20261026/1154–1161, 1180–1185.
04.11.2026: bir kompaniyada percent=-10 takroran yaratish dup_val_on_index
bilan bloklanadi; shuning uchun mos mavjud skidka tekshirilib qayta ishlatiladi. Margin create faqat
Администрирование'da; filial va xona biriktirishlari alohida. API faqat
saqlangan ID/model hamda oldingi membershipni qayta o'qish uchun ishlatiladi.
"""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import re
from tests.regression.helpers.retry.state import stable_uuid as uuid4

import allure
import pytest

from tests.api.client import APIError, positive_id, require_fields
from tests.regression.test_orders.helpers.auth_recovery import RegressionSetupState
from tests.regression.helpers.environment import authorization
from tests.shared.navigation import open_form_from_list
from utils.base_pages import UI_TIMEOUT_MS
from utils.base_pages.auto_base_page import AutoBasePage

pytestmark = [pytest.mark.regression, pytest.mark.order_positive,
              allure.epic("Regression"), allure.feature("Tayyor va qo'lda skidka"),
              allure.story("Tayyor skidka ma'lumotlari")]


def run_prepare_margin(page, baseline, data, directory):
    """1. Filial va xonaning avvalgi skidka bog'lanishlarini qayd etish.
    2. Mavjud faol −10% skidkani qayta ishlatish; yo'q bo'lsagina yaratish, ID/modelni tekshirish.
    3. Faqat yangi skidkani setup filialiga biriktirish.
    4. Xuddi shu skidkani setup xonasiga biriktirish.
    5. Har ikki ro'yxat eski bog'lanishlar + yangi ID ekanini tasdiqlash.

    Katalog, filial va xona mutatsiyalari UI orqali; mavjud skidkalar saqlanadi.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    run_id = uuid4("margin").hex[:12]
    code = str(baseline["code"])
    room_name, filial_name = f"room-pw{code}", f"filial-pw{code}"
    margin = {
        "status": "process", "stage": "planned", "run_id": run_id,
        "name": f"Order manual 10-pw{code}-{run_id}",
        "code": f"c_md10_{code}_{run_id}", "percent": "10", "percent_type": "D",
        "state": "A", "filial_id": str(baseline["filial_id"]),
        "room_id": str(baseline["room_id"]), "retention": "retained",
    }
    data["margin"] = margin
    state = RegressionSetupState(directory / "margin-state.json", deepcopy(baseline))
    base = AutoBasePage(page)
    route = "anor/mrf/room_attachment"

    def persist(stage):
        margin["stage"] = stage
        path = directory / "margin-setup.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(margin, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)

    persist("planned")
    try:
        with allure.step("1 - Filial va xonadagi mavjud skidka IDlarini qayd etish"):
            api = state.admin()
            filial_before = {positive_id(row["margin_id"]) for row in api.table("anor/mkr/margin_list:table", ["margin_id"])}
            room_before = {positive_id(row["margin_id"]) for row in api.table(
                route + ":table_margin", ["margin_id"],
                data={"room_id": margin["room_id"], "attached": "Y"})}
            margin["filial_ids_before"] = sorted(filial_before)
            margin["room_ids_before"] = sorted(room_before)
            persist("membership_snapshot")
        with allure.step("Mavjud faol −10% skidkani tekshirish; foiz kompaniyada yagona"):
            head_api = state.admin(head_filial=True)
            matches = []
            for row in head_api.table("anor/mkr/margin_list:table", ["margin_id", "name"]):
                model = head_api.model("anor/mkr/margin+edit", margin_id=positive_id(row["margin_id"]))
                if model.get("percent_type") == "D" and Decimal(str(model["percent"])) == Decimal("10"):
                    matches.append(model)
            if len(matches) > 1:
                raise APIError("Katalogda bir nechta −10% skidka topildi; aniq targetni tanlab bo'lmaydi")
            if matches:
                saved = matches[0]
                require_fields(saved, state="A", percent_type="D", percent="10")
                margin.update(id=positive_id(saved["margin_id"]), name=saved["name"],
                              code=saved["code"], preparation="reused_existing")
                persist("existing_verified")
            else:
                margin["preparation"] = "created_new"
        with allure.step("2 - Admin sifatida kirib Администрирование filialini tanlash"):
            authorization(page, who="admin")
            base.switch_filial(name="Администрирование")
        if "id" not in margin:
            with allure.step("3 - Skidkalar katalogini ochish"):
                base.navigate_to(tab="Справочники", name="Скидки/наценки")
                base.expect_page(heading="Скидки/наценки", url="anor/mkr/margin_list")
            with allure.step("4 - Alohida aktiv 10% skidka yaratish"):
                open_form_from_list(base.page, heading="Скидка/наценка (создание)", url=re.compile(r"margin(?:%2[Bb]|\+)add"))
                base.input(label="Код", value=margin["code"])
                base.input(label="Название", value=margin["name"])
                base.input(label="Процент", value=margin["percent"])
                base.radio(label="Скидка", expect_checked=True)
                base.checkbox(label="Статус", expect_checked=True)
            with allure.step('5 - Chegirmani saqlash, uning IDsi va saqlangan qiymatlarini tekshirish'):
                base.click(name="Сохранить", exact=True)
                base.expect_page(heading="Скидки/наценки", url="anor/mkr/margin_list")
                api = state.admin(head_filial=True)
                saved = api.one("anor/mkr/margin_list:table", ["margin_id", "name"],
                                filters=["name", "=", margin["name"]])
                margin["id"] = positive_id(saved["margin_id"])
                persist("created")
                require_fields(api.model("anor/mkr/margin+edit", margin_id=margin["id"]),
                               margin_id=margin["id"], name=margin["name"], code=margin["code"],
                               state="A", percent_type="D", percent="10")
                base.grid_controller(search=margin["name"])
                base.grid(margin["name"], margin["code"], "Скидка", "Активный")
                persist("created_verified")
        with allure.step("6 - Test uchun tayyorlangan filialda chegirmalar ro'yxatini ochish"):
            base.switch_filial(name=filial_name)
            base.navigate_to(tab="Справочники", name="Скидки/наценки")
            base.expect_page(heading="Скидки/наценки", url="anor/mkr/margin_list")
        if margin["id"] not in filial_before:
            with allure.step("7 - Filialga biriktirish katalogini ochish"):
                base.click(name="Прикрепление", exact=True)
                base.expect_page(heading="Скидки/наценки (прикрепление)",
                                 url=re.compile(r"margin_list(?:%2[Bb]|\+)attach"), timeout=UI_TIMEOUT_MS)
            with allure.step('8 - Faqat test uchun yaratilgan chegirmani filialga biriktirish'):
                base.grid_controller(search=margin["name"])
                base.grid(margin["name"], margin["code"], click=True)
                base.click(name="Прикрепить", exact=True)
                base.confirm_biruni(f"Прикрепить {margin['name']}?")
                base.wait_for_loader()
                persist("filial_attached")
                api = state.admin()
                filial_after = {positive_id(row["margin_id"]) for row in api.table("anor/mkr/margin_list:table", ["margin_id"])}
                margin["filial_ids_after"] = sorted(filial_after)
                if filial_after != filial_before | {margin["id"]}:
                    raise APIError("Filial skidkalari oldingi IDlar va yangi skidka IDsi yig'indisiga teng emas")
                persist("filial_verified")
        else:
            margin["filial_ids_after"] = sorted(filial_before)
            persist("filial_verified")
        with allure.step("9 - Test uchun tayyorlangan ish zonalari ro'yxatini ochish"):
            base.navigate_to(tab="Справочники", name="Рабочие зоны")
            base.expect_page(heading="Рабочие зоны", url="trade/trf/room_list")
        with allure.step('10 - Aynan test ish zonasining biriktirish formasini ochish'):
            base.grid_controller(search=room_name)
            base.grid(room_name, click=True)
            base.click(name="Прикрепление", exact=True)
            base.expect_page(heading=f"Рабочая зона (прикрепление): {room_name}", url="room_attachment")
        base.tab(name="Скидки/наценки", section=True)
        if margin["id"] not in room_before:
            with allure.step("11 - Test chegirmasini ish zonasining Доступные ro'yxatidan biriktirish"):
                base.tab(name="Доступные")
                base.wait_for_loader()
                base.grid_controller(search=margin["name"])
                base.grid(margin["name"], click=True)
                base.click(name="Прикрепить", exact=True)
                base.confirm_biruni(f"Прикрепить {margin['name']}?")
                base.wait_for_loader()
                persist("room_attached")
        with allure.step("12 - Xonada yangi −10% skidka va eski bog'lanishlar saqlanganini tekshirish"):
            base.tab(name="Прикрепленные")
            base.wait_for_loader()
            base.grid_controller(search=margin["name"])
            base.grid(margin["name"], "-10", "Активный")
            api = state.admin()
            room_after = {positive_id(row["margin_id"]) for row in api.table(
                route + ":table_margin", ["margin_id"],
                data={"room_id": margin["room_id"], "attached": "Y"})}
            margin["room_ids_after"] = sorted(room_after)
            if room_after != room_before | {margin["id"]}:
                raise APIError("Xona skidkalari oldingi IDlar va yangi skidka IDsi yig'indisiga teng emas")
            margin["status"] = "passed"
            persist("verified")
    except Exception as error:
        margin.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        persist(margin["stage"])
        allure.attach(json.dumps(margin, ensure_ascii=False), "Tayyor 10% skidka — ID va bog'lanishlar", allure.attachment_type.JSON)
        state.close()
