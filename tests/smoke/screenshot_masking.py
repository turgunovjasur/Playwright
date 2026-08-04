"""Allure screenshotlari uchun opt-in forma mask profillari."""


MASK_COLOR = "#2f3542"

SECRET_SELECTORS = (
    "input[type='password']",
    "[data-smt-col-key*='secret' i]",
    "[data-smt-col-key*='password' i]",
    "[data-smt-col-key*='token' i]",
    "[data-column*='secret' i]",
    "[data-column*='password' i]",
    "[data-column*='token' i]",
    "[data-testid*='secret' i]",
    "[data-testid*='password' i]",
    "[data-testid*='token' i]",
    "[class*='client-secret' i]",
    "[id*='client-secret' i]",
)

SECRET_STYLE = """
input[type='password'],
[data-smt-col-key*='secret' i], [data-smt-col-key*='password' i],
[data-smt-col-key*='token' i], [data-column*='secret' i],
[data-column*='password' i], [data-column*='token' i],
[data-testid*='secret' i], [data-testid*='password' i],
[data-testid*='token' i], [class*='client-secret' i],
[id*='client-secret' i] {
  color: transparent !important;
  text-shadow: none !important;
  -webkit-text-security: disc !important;
}
"""

FORM_MASK_PROFILES = {
    "company-client": {
        "url_contains": "kauth/company_client",
        "selectors": (
            "input:not([type='hidden'])",
            "textarea",
            "app-company-client-list .smt-data-row",
            "app-company-client-list [role='rowgroup'] [role='row']",
            "app-company-client-list table tbody",
        ),
    },
}


def _profile_selectors(page, profile_name):
    """Profil faqat o'z formasining URLida turganda selectorlarni qaytaradi."""
    if profile_name is None:
        return ()
    try:
        profile = FORM_MASK_PROFILES[profile_name]
    except KeyError as exc:
        raise ValueError(
            f"Noma'lum screenshot mask profili: {profile_name}"
        ) from exc

    current_url = str(getattr(page, "url", "") or "")
    if profile["url_contains"] not in current_url:
        return ()
    return profile["selectors"]


def masked_page_screenshot(page, *, full_page=True, profile_name=None):
    """Secretlar va explicit chaqirilgan formaning profilini masklab rasm oladi."""
    selectors = list(SECRET_SELECTORS)
    selectors.extend(_profile_selectors(page, profile_name))
    return page.screenshot(
        full_page=full_page,
        mask=[page.locator(selector) for selector in selectors],
        mask_color=MASK_COLOR,
        style=SECRET_STYLE,
    )
