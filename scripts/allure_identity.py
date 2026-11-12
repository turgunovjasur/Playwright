"""Stable Forms identities shared by live reporting and existing-result migration."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


FORMS_FULL_NAME = "tests.smoke.test_forms.test_0_forms_runner#test_form_case"


def forms_history_id(full_name, parameters):
    """Identify a navigation scenario, independently of its mutable test settings."""
    if full_name != FORMS_FULL_NAME:
        return None
    parameter = next((p for p in parameters if p.get("name") == "form_case"), None)
    if parameter is None:
        raise ValueError("Forms Allure result is missing its form_case parameter")
    case = ast.literal_eval(parameter["value"])
    if not isinstance(case, dict) or any(
        not case.get(key) for key in ("navbar_tab", "menu_item", "expected_path", "filial")
    ):
        raise ValueError("Forms Allure result has an incomplete navigation identity")
    # Keep separate entry paths and filial/shell coverage distinct. Display titles,
    # ordinals, readiness selectors and intermediate action waits are not identity.
    identity = {
        "version": 1,
        "fullName": full_name,
        "navbar": case["navbar_tab"],
        "column": case.get("menu_column") or None,
        "menu": case["menu_item"],
        "action": case.get("action") or None,
        "links": list(case.get("page_links") or []),
        "add_icon": bool(case.get("add_icon", False)),
        "path": case["expected_path"].strip("/"),
        "filial": case["filial"],
        "section": case.get("section"),
        "shell": case.get("shell") or "legacy",
    }
    if "page_links" not in case:
        # Older intentional-skip records retain their entry path only in label.
        # E.g. Users and Users -> Roles -> Users must remain separate scenarios.
        identity["navigation_label"] = case.get("label") or case["menu_item"]
    payload = json.dumps(identity, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_forms_results(results_dir: Path):
    """Back up and normalize identity metadata without changing test outcomes."""
    results_dir = Path(results_dir)
    changes = []
    for path in sorted(results_dir.glob("*-result.json")):
        original = path.read_bytes()
        result = json.loads(original)
        history_id = forms_history_id(result.get("fullName"), result.get("parameters", []))
        if history_id is not None and (
            result.get("historyId") != history_id
            or result.get("testCaseId") != history_id
            or any(p.get("excluded") is not True for p in result.get("parameters", []))
        ):
            result["historyId"] = history_id
            result["testCaseId"] = history_id
            # Allure 3 derives history from testCaseId + non-excluded parameters;
            # changing only the Allure 2 historyId field has no effect there.
            for parameter in result.get("parameters", []):
                parameter["excluded"] = True
            changes.append((path, original, result))
    if not changes:
        return 0, None

    backup_dir = results_dir.parent / "allure-identity-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = backup_dir / f"{results_dir.name}-{stamp}.zip"
    with ZipFile(backup, "x", compression=ZIP_DEFLATED) as archive:
        for path, original, _ in changes:
            archive.writestr(path.name, original)
    for path, _, result in changes:
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        temporary.replace(path)
    return len(changes), backup
