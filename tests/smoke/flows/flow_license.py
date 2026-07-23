"""Litsenziya setup testlari uchun umumiy policy yordamchilari."""

import os

import allure


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
