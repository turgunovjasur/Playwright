import re
from urllib.parse import parse_qs, urlsplit


ADMIN_FILIAL_NAME = "Администрирование"


def label_pattern(label):
    """Semantic labelni oddiy va quote-escaped DOM matniga moslaydi."""
    if isinstance(label, re.Pattern):
        return label

    parts = []
    for char in str(label):
        if char in {'"', "'"}:
            parts.append(rf"\\?{re.escape(char)}\\?")
        else:
            parts.append(re.escape(char))
    return re.compile(
        rf"^\s*{''.join(parts)}\s*(?:\*)?\s*$",
        re.IGNORECASE,
    )


def first_non_admin_filial(names):
    """Filial nomlaridan birinchi ``Администрирование`` bo'lmaganini qaytaradi."""
    cleaned_names = [str(name).strip() for name in names if str(name).strip()]
    for name in cleaned_names:
        if name != ADMIN_FILIAL_NAME:
            return name
    raise AssertionError(
        f"'{ADMIN_FILIAL_NAME}' bo'lmagan operatsion filial topilmadi. "
        f"Ko'ringan filiallar: {cleaned_names}"
    )


def query_int_from_url(url, name):
    """Oddiy yoki hash-router URL query parametridan musbat integer qaytaradi."""
    parsed_url = urlsplit(str(url or ""))
    query = parsed_url.query
    if not query and parsed_url.fragment:
        query = urlsplit(parsed_url.fragment).query

    values = parse_qs(query).get(name, [])
    if len(values) != 1 or not values[0].isdigit() or int(values[0]) <= 0:
        raise AssertionError(
            f"URL ichida musbat integer '{name}' parametri topilmadi: {url}"
        )
    return int(values[0])
