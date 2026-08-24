import re


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
