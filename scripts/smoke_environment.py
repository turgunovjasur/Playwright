"""Runner va pytest uchun umumiy environment tekshiruvi."""

import os
from urllib.parse import urlsplit


CREATED_COMPANY_PASSWORD = "greenwhite"


def check_requiremants(env=None, cli_options=None):
    """Run boshida sozlamalarni tekshiradi; qiymatlarni o'zgartirmaydi."""
    if env is None:
        env = os.environ
    errors = []
    create_company = env.get("COMPANY_CODE") == "1"
    cli_options = cli_options or {}
    if create_company and cli_options.get("company_password"):
        errors.append(
            "--company-password --company-code 1 bilan berilmaydi; yangi "
            "company admin paroli test ichidagi default qiymat"
        )
    if not create_company and (cli_options.get("head_email") or cli_options.get("head_password")):
        errors.append("--head-email/--head-password faqat --company-code 1 bilan ishlaydi")

    required = ["COMPANY_URL", "COMPANY_CODE", "USER_PASSWORD"]
    if create_company:
        required.extend(["HEAD_ADMIN_EMAIL", "HEAD_ADMIN_PASSWORD"])
    else:
        required.append("COMPANY_PASSWORD")

    for name in required:
        if not env.get(name, "").strip():
            errors.append(f"{name} majburiy va bo'sh bo'lmasligi kerak")

    company_code = env.get("COMPANY_CODE", "")
    if company_code == "0":
        errors.append("COMPANY_CODE uchun 1 yoki mavjud kompaniya kodini bering")
    if company_code != company_code.strip():
        errors.append("COMPANY_CODE chetida bo'sh joy bo'lmasligi kerak")

    company_url = env.get("COMPANY_URL", "")
    if company_url:
        try:
            parsed = urlsplit(company_url)
            valid_url = parsed.scheme in {"http", "https"} and bool(parsed.hostname)
        except ValueError:
            valid_url = False
        if not valid_url or any(char.isspace() for char in company_url):
            errors.append("COMPANY_URL bo'sh joysiz http/https server manzili bo'lishi kerak")
        if company_url.endswith("/"):
            errors.append("COMPANY_URL oxirida / bo'lmasligi kerak")

    for name in (
        "HEADLESS", "NEW_CODE", "DISABLE_LICENSE_POLICY", "SHOW_TRACE",
        "OPEN_REPORT", "CLEAN_ALLURE_RESULTS", "DEFER_ALLURE_REPORT", "SMARTUP_RUNNER",
    ):
        if name in env and env[name] not in {"0", "1"}:
            errors.append(f"{name} faqat 1 yoki 0 bo'lishi kerak")

    if env.get("DISABLE_LICENSE_POLICY") == "1" and not create_company:
        errors.append("DISABLE_LICENSE_POLICY=1 faqat COMPANY_CODE=1 bilan ishlaydi")

    if errors:
        raise ValueError("Run sozlamalarida xato:\n- " + "\n- ".join(errors))
