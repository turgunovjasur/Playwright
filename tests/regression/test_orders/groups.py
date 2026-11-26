"""Order guruhlarining SCN kodi, biznes nomi va bajarilish tartibi."""

GROUP_FEATURES = {
    "statuses": "SCN-001 · Order statuslari",
    "promotions": "SCN-002 · Order aksiyalari va chegirmalari",
    "payments": "SCN-003 · Order to‘lovlari",
    "mandatory": "SCN-004 · Majburiy aksiyalar",
    "stock": "SCN-005 · Order ombor rezervi",
    "bonus_limit": "SCN-006 · Ikki klient uchun umumiy bonus limiti",
    "returns": "SCN-007 · Bonus va chegirmali orderni qaytarish",
    "multi_payments": "SCN-008 · Bir klientning bir nechta orderini to‘lash",
    "manual_discounts": "SCN-009 · Tayyor va qo‘lda chegirma",
    "product_limit": "SCN-010 · Ikki order uchun kunlik TMZ limiti",
    "two_warehouses": "SCN-011 · Bitta orderda ikki ombor",
    "mixed_promotions": "SCN-012 · Majburiy va ixtiyoriy aksiyalar birga",
    "auto_offset": "SCN-013 · Kirimda order qarzini avtomatik yopish",
    "prepayment_first": "SCN-014 · Orderdan oldin olingan avans",
    "recovery": "SCN-015 · Retry va dublikatdan himoya",
    "catalog_price_history": "SCN-016 · Katalog narxi o‘zgarganda order summasi",
    "excel_import_promotion": "SCN-017 · Excel importidan keyin bonus aksiyasi",
    "consignment_due_dates": "SCN-018 · Konsignatsiya qarzini muddati bo‘yicha yopish",
    "archive_restore": "SCN-019 · Arxivdan tiklash va bekor qilish",
    "bulk_missing_price": "SCN-020 · Narxi yo‘q mahsulotda eski narx turini saqlash",
    "fractional_quantity": "SCN-021 · Kasr miqdoridagi KG chegirmasi",
    "discount_apply_all": "SCN-022 · Chegirmani barcha qatorlarga qo‘llash",
    "delivery_address": "SCN-023 · Buyurtmaning yetkazish manzili",
    "line_history": "SCN-024 · KG qatori o‘zgarishlari tarixi",
    "service_status": "SCN-025 · Xizmatli buyurtma statuslari",
    "goods_service_discount": "SCN-026 · Tovar va xizmatga umumiy chegirma",
    "order_xml": "SCN-027 · Ikki buyurtmani XMLga eksport qilish",
    "bonus_recalculation": "SCN-028 · Narx turi almashganda bonusni qayta hisoblash",
}

VERIFICATION_RUNNERS = {"recovery": "tests/regression/test_orders/verification/test_recovery_runner.py"}
GROUP_NAMES = tuple(group for group in GROUP_FEATURES if group not in VERIFICATION_RUNNERS)
GROUP_RUNNERS = tuple(f"tests/regression/test_orders/runners/test_{group}_runner.py" for group in GROUP_NAMES)
