"""Repository-relative CI artifacts; independent of the current directory."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


STATE_FILE = ROOT / "test-results" / "telegram-progress.json"


DELIVERY_FILE = ROOT / "test-results" / "telegram-delivery.json"


SYSTEM_SUMMARY_JSON = ROOT / "test-results" / "system-summary.json"


AI_SUMMARY_JSON = ROOT / "test-results" / "ai-summary.json"


DATA_STORE_JSON = ROOT / "test-results" / "data" / "data_store.json"
