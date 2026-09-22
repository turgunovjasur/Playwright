"""Tasdiqlangan sakkiz mahsulot matritsasi; qiymatlar har run code bilan quriladi."""


# Kalit, yaratish yo'li, sotuv narxi, valyuta, narxlash yo'li, yakuniy qoldiq.
PRODUCT_MATRIX = (
    ("UZS-A", "manual", "7000", "UZS", "product", "100"),
    ("UZS-B", "import", "12500", "UZS", "price_list", "100"),
    ("UZS-C", "manual", "2500", "UZS", "product", "100"),
    ("LOW", "manual", "5000", "UZS", "product", "3"),
    ("BONUS", "manual", "2000", "UZS", "price_list", "100"),
    ("ZERO", "manual", "9000", "UZS", "price_list", "0"),
    ("USD-A", "manual", "1", "USD", "product", "100"),
    ("USD-B", "import", "2.35", "USD", "price_list", "100"),
)

MANUAL_PRODUCT_KEYS = tuple(row[0] for row in PRODUCT_MATRIX if row[1] == "manual")


def product_case(code, key, *, prefix="reg"):
    """Mahsulot kartasi va keyingi narx/qoldiq expectedlarini alohida qaytaradi.

    prefix mustaqil lifecycle/validation caselari baseline nomini band qilmasligi
    uchun beriladi. Mahsulot kartasiga sale_currency yoki stock yozilmaydi.
    """
    row = next((row for row in PRODUCT_MATRIX if row[0] == key), None)
    if row is None:
        raise ValueError(f"Noma'lum regression mahsuloti: {key}")
    index = PRODUCT_MATRIX.index(row) + 1
    slug = key.lower().replace("-", "_")
    name = f"{prefix}-product-{key.lower()}-pw{code}"
    values = {
        "UZS-A": ("0.45", "0.5", "0.75", "Коробка", "12", "Паллета", "10", False, False),
        "UZS-B": ("0.8", "0.9", "1", "Коробка", "6", "", "", False, False),
        "UZS-C": ("1.25", "1.5", "2", "Блок", "6", "", "", True, False),
        "LOW": ("0.125", "0.15", "0.25", "", "", "", "", False, False),
        "BONUS": ("0.2", "0.25", "0.5", "Коробка", "24", "", "", False, False),
        "ZERO": ("2", "2.5", "3", "", "", "", "", False, True),
        "USD-A": ("0.333", "0.4", "0.75", "Коробка", "8", "Паллета", "5", False, False),
        "USD-B": ("0.625", "0.75", "1.25", "Блок", "4", "", "", False, False),
    }[key]
    netto, brutto, volume, box, box_qty, pallet, pallet_qty, production, material = values
    return {
        "key": key,
        "method": row[1],
        "name": name,
        "code": f"c_{prefix}_{slug}_pw{code}",
        "short_name": f"{prefix}-{key}-pw{code}",
        "article_code": f"{prefix}-{slug}-{code}",
        "order_no": str(index),
        "measure": "шт",
        "sector": f"sector-pw{code}",
        "weight_netto": netto,
        "weight_brutto": brutto,
        "volume": volume,
        "box": box,
        "box_short_name": {"Коробка": "кор", "Блок": "бл", "": ""}[box],
        "box_qty": box_qty,
        "pallet": pallet,
        "pallet_qty": pallet_qty,
        "production": production,
        "material": material,
        "sale_price": row[2],
        "sale_currency": row[3],
        "pricing_path": row[4],
        "target_stock": row[5],
    }
