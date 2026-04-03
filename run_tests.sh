#!/bin/bash
# Testlarni ishga tushirish va Allure hisobotini yaratish

RESULTS_DIR="test-results/allure-results"
REPORT_DIR="test-results/allure-report"

# 1. Eski natijalarni tozalash (history saqlanadi - conftest.py ko'chiradi)
find "$RESULTS_DIR" -mindepth 1 -not -path "$RESULTS_DIR/history*" -delete 2>/dev/null || true

# 2. Testlarni ishga tushirish (fail bo'lsa ham davom etadi)
pytest tests/smoke/test_smoke_runner.py "$@"

# 3. Allure hisobotini yaratish (history Trend uchun saqlanadi)
allure generate "$RESULTS_DIR" -o "$REPORT_DIR" --clean

# 4. Hisobotni ochish
allure open "$REPORT_DIR"
