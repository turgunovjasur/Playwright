"""API setup natijasini tekshirib, regression uchun baseline tanlash.

Faqat to'liq runner muvaffaqiyati tasdiqlangan baseline ko'chiriladi.
Eski UI baseline zaxiralanadi; secret yoki sessiya ko'chirilmaydi.
"""

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree


REQUIRED_KEYS = (
    "code", "url", "company_code", "filial_id", "filial_name", "user_id",
    "product_id", "product_id_usa", "client_person_id", "warehouse_id",
    "price_type_id_uzb", "price_type_id_usa",
)


# Only the known pre-refactor setup is compatible. Do not accept arbitrary
# supersets or rewrite old success evidence to match the new runner.
LEGACY_PROMOTION_STEPS = frozenset({
    "test_25_quantity_discount", "test_26_quantity_bonus",
    "test_27_amount_discount", "test_28_amount_bonus", "test_29_cyclic_bonus",
})


def _paths(root):
    directory = Path(root) / "test-results/api"
    return directory / "data_store.json", directory / "setup-success.json"


def _read_baseline(root, env):
    path, _ = _paths(root)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("API baseline JSON object bo'lishi kerak")
    missing = [key for key in REQUIRED_KEYS if data.get(key) in (None, "", {})]
    if missing:
        raise ValueError("API setup to'liq emas; yetishmaydi: " + ", ".join(missing))
    if data.get("suite") != "api_setup":
        raise ValueError("Bu API setup baseline emas")
    if data["url"].rstrip("/") != env["COMPANY_URL"].rstrip("/"):
        raise ValueError("API baseline boshqa serverga tegishli")
    if str(data["company_code"]) != env["COMPANY_CODE"]:
        raise ValueError("API baseline boshqa kompaniyaga tegishli")
    if data["filial_name"] != f"filial-pw{data['code']}":
        raise ValueError("API baseline code va filial nomi mos emas")
    return path, data


def _expected_steps(root, env):
    runner = root / "tests/api/setup/test_0_setup_runner.py"
    tree = ast.parse(runner.read_text(encoding="utf-8"))
    expected = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)
                and node.name.startswith("test_")}
    if env["COMPANY_CODE"] != "1":
        expected.discard("test_00_company")
    return runner, expected


def record_setup_success(root, env, *, started_at, junit_path=None):
    """Yangi JUnitda barcha majburiy API runner qadamlari o'tganini tasdiqlash."""
    root = Path(root)
    junit = Path(junit_path).resolve() if junit_path else root / "test-results/api/setup-runner.xml"
    if junit.stat().st_mtime < started_at:
        raise ValueError("API setup JUnit natijasi joriy runniki emas")
    runner, expected = _expected_steps(root, env)
    try:
        results = ElementTree.parse(junit).findall(".//testcase")
    except ElementTree.ParseError as error:
        raise ValueError("API setup JUnit fayli o'qilmaydi") from error
    names = [row.attrib.get("name") for row in results]
    if len(names) != len(expected) or set(names) != expected:
        raise ValueError("API setup runner to'liq bajarilmagan; baseline tanlanmaydi")
    host = (urlparse(env["COMPANY_URL"]).hostname or "").lower()
    for row in results:
        name = row.attrib["name"]
        if row.find("failure") is not None or row.find("error") is not None:
            raise ValueError(f"API setup muvaffaqiyatsiz: {name}")
        if row.find("skipped") is not None:
            allowed = name == "test_10_buy_license" and (
                host == "smartup.online" or host.endswith(".smartup.online"))
            if not allowed:
                raise ValueError(f"Majburiy API setup qadami bajarilmagan: {name}")
    path, _ = _read_baseline(root, env)
    if path.stat().st_mtime < started_at:
        raise ValueError("API baseline joriy setupda yangilanmagan")
    _, manifest_path = _paths(root)
    manifest = {
        "status": "passed", "completed_at": datetime.now(timezone.utc).isoformat(),
        "baseline_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "junit_sha256": hashlib.sha256(junit.read_bytes()).hexdigest(),
        "junit_path": str(junit.resolve()),
        "runner": str(runner.relative_to(root)), "steps": sorted(expected),
    }
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    return manifest_path


def validate_api_baseline(root, env):
    """API setup muvaffaqiyati va baseline butunligini o'zgartirmasdan tekshirish."""
    root = Path(root)
    path, data = _read_baseline(root, env)
    _, manifest_path = _paths(root)
    if not manifest_path.is_file():
        raise ValueError(
            "API setup tasdiq fayli yo‘q. API runner faylini to‘liq qayta ishga tushiring: "
            "tests/api/setup/test_0_setup_runner.py. U muvaffaqiyatli tugagach "
            "regression runnerni ishga tushiring. data_store.jsonning o‘zi yetarli emas."
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runner, expected = _expected_steps(root, env)
    if (not isinstance(manifest, dict)
            or manifest.get("steps") not in (sorted(expected), sorted(expected | LEGACY_PROMOTION_STEPS))
            or manifest.get("runner") != str(runner.relative_to(root))):
        raise ValueError("API setup tasdig'i joriy runner qadamlariga mos emas")
    if manifest.get("status") != "passed" or manifest.get("baseline_sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError("API baseline uchun to'liq muvaffaqiyat tasdig'i yo'q yoki fayl o'zgargan")
    junit = Path(manifest.get("junit_path", root / "test-results/api/setup-runner.xml"))
    if manifest.get("junit_sha256") != hashlib.sha256(junit.read_bytes()).hexdigest():
        raise ValueError("API setup natijasi o'zgargan; setupni qayta tekshiring")
    return data


def select_api_baseline(root, env):
    """Tasdiqlangan API natijasini umumiy UI storega atomik o'tkazish."""
    root = Path(root)
    validate_api_baseline(root, env)
    path, _ = _paths(root)
    target = root / "test-results/data/data_store.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backups = target.parent / "baseline-backups"
        backups.mkdir(exist_ok=True)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        (backups / f"{digest}.json").write_bytes(target.read_bytes())
    temporary = target.with_suffix(".json.tmp")
    temporary.write_bytes(path.read_bytes())
    temporary.replace(target)
    return target
