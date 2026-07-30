from calendar import monthrange
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


TASHKENT_TIMEZONE = ZoneInfo("Asia/Tashkent")
DEFAULT_DATE_FORMAT = "%d.%m.%Y"
DATE_FORMAT_ALIASES = {
    "DD.MM.YYYY": "%d.%m.%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "DD-MM-YYYY": "%d-%m-%Y",
}
SUPPORTED_INPUT_FORMATS = (
    "%d.%m.%Y",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
)


def resolve_date(value="today", *, days=0):
    """Keyword, sana yoki sana matnini ``date`` obyektiga aylantiradi."""
    if not isinstance(days, int) or isinstance(days, bool):
        raise TypeError("resolve_date(): days int bo'lishi kerak")

    today = datetime.now(TASHKENT_TIMEZONE).date()

    if isinstance(value, datetime):
        resolved = value.date()
    elif isinstance(value, date):
        resolved = value
    elif isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "today":
            resolved = today
        elif normalized in {"yesterday", "previous_day"}:
            resolved = today - timedelta(days=1)
        elif normalized in {"tomorrow", "next_day"}:
            resolved = today + timedelta(days=1)
        elif normalized in {"first_day", "month_start"}:
            resolved = today.replace(day=1)
        elif normalized in {"last_day", "month_end"}:
            resolved = today.replace(day=monthrange(today.year, today.month)[1])
        else:
            for input_format in SUPPORTED_INPUT_FORMATS:
                try:
                    resolved = datetime.strptime(value.strip(), input_format).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(
                    "resolve_date(): value today/yesterday/tomorrow/"
                    "first_day/last_day yoki qo'llab-quvvatlanadigan sana bo'lishi kerak"
                )
    else:
        raise TypeError("resolve_date(): value str/date/datetime bo'lishi kerak")

    return resolved + timedelta(days=days)


def format_date(value="today", *, days=0, date_format=DEFAULT_DATE_FORMAT):
    """Hisoblangan sanani berilgan ``strftime`` formatida qaytaradi."""
    if not isinstance(date_format, str) or not date_format:
        raise TypeError("format_date(): date_format bo'sh bo'lmagan str bo'lishi kerak")
    output_format = DATE_FORMAT_ALIASES.get(date_format.upper(), date_format)
    return resolve_date(value, days=days).strftime(output_format)
