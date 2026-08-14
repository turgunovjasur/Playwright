"""Litsenziya setup testlari uchun umumiy policy yordamchilari."""

import os
from urllib.parse import urlparse

import allure
import pytest

from tests.smoke.flows.flow_authorization import company_url


def license_policy_disabled():
    """Companyda litsenziya siyosati o'chirilganini qaytaradi."""
    create_company = os.getenv("CREATE_COMPANY", "").strip().lower() in {"1", "true", "yes", "on"}
    disable_policy = os.getenv("DISABLE_LICENSE_POLICY", "").strip().lower() in {"1", "true", "yes", "on"}
    return create_company and disable_policy


def attach_license_policy_skip_note(logger, step_name):
    """Litsenziya siyosati o'chirilgan stepni Allure va logga qayd qiladi."""
    message = (
        f"{step_name} o'tkazib yuborildi: --disable-license-policy berilgani uchun "
        "companyda Политика лицензирования o'chirilgan."
    )
    allure.attach(message, name="license-policy-disabled", attachment_type=allure.attachment_type.TEXT)
    logger.info(message)


def license_purchase_server_unsupported():
    """License purchase ishlamaydigan smartup.online serverini aniqlaydi."""
    hostname = (urlparse(company_url()).hostname or "").lower()
    return hostname == "smartup.online" or hostname.endswith(".smartup.online")


def skip_license_flow_if_needed(logger, step_name):
    """Policy o'chirilgan bo'lsa license flowdan chiqadi."""
    if license_policy_disabled():
        attach_license_policy_skip_note(logger, step_name)
        return True

    return False


def skip_license_purchase_if_needed(logger, step_name):
    """Policy o'chirilgan yoki server purchase'ni qo'llamasa Buy flowdan chiqadi."""
    if skip_license_flow_if_needed(logger, step_name):
        return True

    if license_purchase_server_unsupported():
        message = (
            f"{step_name} o'tkazib yuborildi: smartup.online serverida "
            "license purchase flow ishlamaydi."
        )
        allure.attach(
            message,
            name="license-server-unsupported",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info(message)
        pytest.skip(message)

    return False
