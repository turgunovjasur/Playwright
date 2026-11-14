"""Litsenziya setup testlari uchun umumiy policy yordamchilari."""

import os
from urllib.parse import urlparse

import allure
import pytest

def open_admin_licenses(page, base):
    """On A2 the admin menu is rebuilt after switching back to the dashboard."""
    if "/a2/" in urlparse(page.url).path:
        admin = page.get_by_role("banner").get_by_role(
            "button", name="SFA Администрирование", exact=True
        )
        if not admin.is_visible():
            base.switch_filial(name="Администрирование")
            base.expect_page(url="trade/intro/dashboard")
            base.text("Администрирование", root="main")
            # The header changes before the shell discards the previous filial menu.
            # Refresh only the dashboard: there is no pending form or purchase here.
            page.reload(wait_until="domcontentloaded")
            base.expect_page(url="trade/intro/dashboard")
            base.text("Администрирование", root="main")
    else:
        base.switch_filial(name="Администрирование")
    base.navigate_to(tab="Главное", name="Лицензии")
    base.expect_page(heading="Лицензии", url="biruni/kl/license_list")


def xtrade_license_rows(page):
    return page.get_by_test_id("smt-table-row").filter(
        has=page.get_by_text("ERP users", exact=True)
    )


def license_policy_disabled():
    """Companyda litsenziya siyosati o'chirilganini qaytaradi."""
    create_company = os.getenv("COMPANY_CODE", "").strip() == "1"
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
    company_url = os.environ["COMPANY_URL"]
    hostname = (urlparse(company_url).hostname or "").lower()
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
