#!/usr/bin/env python3
"""Validate Smartup Guide structure without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
REFERENCES = SKILL_ROOT / "references"
FORMS = REFERENCES / "forms"
SCREENSHOTS = FORMS / "screenshots"
SKILL_MD = SKILL_ROOT / "SKILL.md"

ALLOWED_STATUSES = {
    "user-reported",
    "code-confirmed",
    "live-ui-confirmed",
    "trace-confirmed",
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
REPO_PATH = re.compile(
    r"`((?:tests|scripts|utils|skills|data|pages|flows)/"
    r"[A-Za-z0-9_./-]+\.(?:py|sh|json|md))"
)
ALLOW_MISSING = re.compile(r"kb-allow-missing:\s*([A-Za-z0-9_./-]+)")
TOC = re.compile(
    r"^## (?:Mundarija|Table of Contents|Contents)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
VERIFIED = re.compile(r"^(?:\d{4}-\d{2}-\d{2}|pending)$")

# Debt ratchet: lower the matching baseline in the same change when debt drops.
BASELINE_LEGACY_ENTRIES_WITHOUT_PROVENANCE = 139
BASELINE_SCREENSHOTS_WITHOUT_JSON_SIDECAR = 41


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def markdown_files() -> list[Path]:
    return sorted(SKILL_ROOT.rglob("*.md"))


def check_markdown_links(files: list[Path], errors: list[str]) -> None:
    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = match.group(1).strip().strip("<>")
            if raw_target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(raw_target.split("#", 1)[0])
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(
                    f"{relative(path)}: broken Markdown link -> {raw_target}"
                )


def check_dossier_index(errors: list[str]) -> None:
    index = SKILL_MD.read_text(encoding="utf-8")
    for dossier in sorted(FORMS.glob("*.md")):
        expected = f"references/forms/{dossier.name}"
        if expected not in index:
            errors.append(
                f"{relative(dossier)}: dossier is missing from SKILL.md index"
            )


def check_long_file_toc(files: list[Path], errors: list[str]) -> None:
    for path in files:
        text = path.read_text(encoding="utf-8")
        if len(text.splitlines()) > 100 and not TOC.search(text):
            errors.append(
                f"{relative(path)}: file has more than 100 lines but no contents section"
            )


def entry_metadata(lines: list[str], start: int) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in lines[start + 1 : start + 8]:
        if line.startswith(("#", "Tags:", "- ")):
            break
        for key in ("Status", "Verified", "Source"):
            prefix = f"{key}:"
            if line.startswith(prefix):
                metadata[key] = line[len(prefix) :].strip()
    return metadata


def check_provenance(files: list[Path], errors: list[str]) -> int:
    legacy_entries = 0
    for path in files:
        if path.name == "history.md":
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not line.startswith("Tags:"):
                continue
            metadata = entry_metadata(lines, index)
            status = metadata.get("Status")
            verified = metadata.get("Verified")
            source = metadata.get("Source")
            values = (status, verified, source)
            if not any(values):
                legacy_entries += 1
                continue
            if not all(values):
                errors.append(
                    f"{relative(path)}:{index + 1}: Status, Verified and Source "
                    "must be written together"
                )
                continue
            if status not in ALLOWED_STATUSES:
                errors.append(
                    f"{relative(path)}:{index + 2}: unsupported Status '{status}'"
                )
            if not VERIFIED.fullmatch(verified or ""):
                errors.append(
                    f"{relative(path)}:{index + 3}: Verified must be YYYY-MM-DD or pending"
                )
    return legacy_entries


def check_repo_paths(files: list[Path], errors: list[str]) -> None:
    for path in files:
        if path.name == "history.md":
            continue
        text = path.read_text(encoding="utf-8")
        allowed = set(ALLOW_MISSING.findall(text))
        for repo_path in sorted(set(REPO_PATH.findall(text))):
            if repo_path in allowed:
                continue
            if not (REPO_ROOT / repo_path).exists():
                errors.append(
                    f"{relative(path)}: referenced repo path does not exist -> {repo_path}"
                )


def check_screenshots(files: list[Path], errors: list[str]) -> int:
    all_markdown = "\n".join(
        path.read_text(encoding="utf-8") for path in files
    )
    images = sorted(
        path
        for path in SCREENSHOTS.rglob("*")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    )
    for image in images:
        if image.name not in all_markdown:
            errors.append(
                f"{relative(image)}: screenshot filename is not indexed in any Markdown file"
            )
    return sum(not image.with_suffix(".json").exists() for image in images)


def main() -> int:
    files = markdown_files()
    errors: list[str] = []

    check_markdown_links(files, errors)
    check_dossier_index(errors)
    check_long_file_toc(files, errors)
    reference_files = sorted(REFERENCES.rglob("*.md"))
    legacy_entries = check_provenance(reference_files, errors)
    check_repo_paths(files, errors)
    images_without_metadata = check_screenshots(files, errors)
    if legacy_entries > BASELINE_LEGACY_ENTRIES_WITHOUT_PROVENANCE:
        errors.append(
            "legacy entries without provenance increased "
            f"from {BASELINE_LEGACY_ENTRIES_WITHOUT_PROVENANCE} "
            f"to {legacy_entries}"
        )
    elif legacy_entries < BASELINE_LEGACY_ENTRIES_WITHOUT_PROVENANCE:
        errors.append(
            "legacy provenance debt decreased; lower "
            "BASELINE_LEGACY_ENTRIES_WITHOUT_PROVENANCE to "
            f"{legacy_entries} in this validator"
        )
    if images_without_metadata > BASELINE_SCREENSHOTS_WITHOUT_JSON_SIDECAR:
        errors.append(
            "screenshots without JSON sidecar increased "
            f"from {BASELINE_SCREENSHOTS_WITHOUT_JSON_SIDECAR} "
            f"to {images_without_metadata}"
        )
    elif images_without_metadata < BASELINE_SCREENSHOTS_WITHOUT_JSON_SIDECAR:
        errors.append(
            "screenshot metadata debt decreased; lower "
            "BASELINE_SCREENSHOTS_WITHOUT_JSON_SIDECAR to "
            f"{images_without_metadata} in this validator"
        )

    print(f"markdown_files={len(files)}")
    print(f"form_dossiers={len(list(FORMS.glob('*.md')))}")
    print(f"legacy_entries_without_full_provenance={legacy_entries}")
    print(f"screenshots_without_json_sidecar={images_without_metadata}")

    if errors:
        print(f"errors={len(errors)}")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("errors=0")
    print("Smartup knowledge base is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
