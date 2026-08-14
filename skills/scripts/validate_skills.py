#!/usr/bin/env python3
"""Validate the shared project skills tree without third-party dependencies."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


SKILLS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILLS_ROOT.parent
ENTRYPOINT_ROOTS = (REPO_ROOT / ".agents" / "skills", REPO_ROOT / ".claude" / "skills")
SMARTUP_VALIDATOR = SKILLS_ROOT / "smartup-guide" / "scripts" / "validate_knowledge_base.py"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
PROJECT_GUIDE = SKILLS_ROOT / "project-guide" / "SKILL.md"
DOCS_SUPERPOWERS = REPO_ROOT / "docs" / "superpowers"
SUPERPOWERS_SDD = REPO_ROOT / ".superpowers" / "sdd"
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
FRONTMATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
FRONTMATTER_FIELD = re.compile(r"^(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.+?)\s*$", re.MULTILINE)


def relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def skill_directories() -> list[Path]:
    return sorted(
        path
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        errors.append(f"{relative(path)}: YAML frontmatter topilmadi")
        return {}
    return {
        item.group("key"): item.group("value").strip('"\'')
        for item in FRONTMATTER_FIELD.finditer(match.group("body"))
    }


def check_skill_packages(skills: list[Path], errors: list[str]) -> None:
    for skill in skills:
        skill_md = skill / "SKILL.md"
        metadata = parse_frontmatter(skill_md, errors)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if name != skill.name:
            errors.append(
                f"{relative(skill_md)}: name={name!r}, papka nomi={skill.name!r}"
            )
        if not re.fullmatch(r"[a-z0-9-]+", name):
            errors.append(f"{relative(skill_md)}: skill name formati noto'g'ri -> {name!r}")
        if not description.startswith("Use when "):
            errors.append(
                f"{relative(skill_md)}: description 'Use when ' bilan boshlanishi kerak"
            )
        if len(description) > 500:
            errors.append(f"{relative(skill_md)}: description 500 belgidan uzun")
        agent_metadata = skill / "agents" / "openai.yaml"
        if not agent_metadata.is_file():
            errors.append(f"{relative(skill)}: agents/openai.yaml topilmadi")


def check_entrypoints(skills: list[Path], errors: list[str]) -> None:
    expected = {skill.name: skill.resolve() for skill in skills}
    for root in ENTRYPOINT_ROOTS:
        if not root.is_dir():
            errors.append(f"{relative(root)}: entrypoint papkasi topilmadi")
            continue
        actual_names = {path.name for path in root.iterdir()}
        missing = sorted(set(expected) - actual_names)
        extra = sorted(actual_names - set(expected))
        if missing:
            errors.append(f"{relative(root)}: symlinklar yetishmaydi -> {missing}")
        if extra:
            errors.append(f"{relative(root)}: ortiqcha entrypointlar -> {extra}")
        for name, target in expected.items():
            entrypoint = root / name
            if not entrypoint.is_symlink():
                errors.append(f"{relative(entrypoint)}: symlink emas")
                continue
            if entrypoint.resolve() != target:
                errors.append(
                    f"{relative(entrypoint)}: noto'g'ri target -> {entrypoint.resolve()}"
                )


def check_loaders(errors: list[str]) -> None:
    if not AGENTS_MD.is_file():
        errors.append("AGENTS.md: project bootstrap topilmadi")
    else:
        agents_text = AGENTS_MD.read_text(encoding="utf-8")
        required = (
            "skills/project-guide/SKILL.md",
            ".agents/skills/",
            ".claude/skills/",
            "skills/scripts/validate_skills.py",
        )
        for marker in required:
            if marker not in agents_text:
                errors.append(f"AGENTS.md: bootstrap marker yetishmaydi -> {marker}")

    if not CLAUDE_MD.is_file():
        errors.append("CLAUDE.md: loader topilmadi")
    elif CLAUDE_MD.read_text(encoding="utf-8").strip() != "@AGENTS.md":
        errors.append("CLAUDE.md: faqat '@AGENTS.md' importi bo'lishi kerak")


def check_project_guide(skills: list[Path], errors: list[str]) -> None:
    if not PROJECT_GUIDE.is_file():
        errors.append("skills/project-guide/SKILL.md: canonical router topilmadi")
        return
    router = PROJECT_GUIDE.read_text(encoding="utf-8")
    for skill in skills:
        if skill.name == "project-guide":
            continue
        if f"`{skill.name}`" not in router:
            errors.append(
                f"{relative(PROJECT_GUIDE)}: skill routingda yo'q -> {skill.name}"
            )


def check_stale_paths(errors: list[str]) -> None:
    stale = "tests/smoke/test_groups/test_0_grup/"
    for path in sorted(SKILLS_ROOT.rglob("*.md")):
        if stale in path.read_text(encoding="utf-8"):
            errors.append(f"{relative(path)}: stale repo path -> {stale}")


def check_tracked_generated_files(errors: list[str]) -> None:
    completed = subprocess.run(
        ["git", "ls-files", "skills"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        errors.append("git ls-files skills: tracked generated fayllar tekshirilmadi")
        return
    for item in completed.stdout.splitlines():
        if "/__pycache__/" in item or item.endswith(".pyc"):
            errors.append(f"{item}: generated Python artifact track qilingan")


def check_artifact_lifecycle(errors: list[str]) -> None:
    if DOCS_SUPERPOWERS.is_dir():
        delivery_files = sorted(path for path in DOCS_SUPERPOWERS.rglob("*") if path.is_file())
        if delivery_files:
            errors.append(
                "docs/superpowers: task delivery artifactlari yakunda skills'ga "
                f"migrate qilinib tozalanishi kerak -> {len(delivery_files)} fayl"
            )

    if SUPERPOWERS_SDD.is_dir():
        scratch_files = sorted(
            path
            for path in SUPERPOWERS_SDD.rglob("*")
            if path.is_file() and path != SUPERPOWERS_SDD / ".gitignore"
        )
        if scratch_files:
            errors.append(
                ".superpowers/sdd: temporary agent artifactlari tozalanmagan -> "
                f"{len(scratch_files)} fayl"
            )


def check_markdown_links(errors: list[str]) -> int:
    files = sorted(SKILLS_ROOT.rglob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = match.group(1).strip().strip("<>")
            if raw_target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(raw_target.split("#", 1)[0])
            if target and not (path.parent / target).resolve().exists():
                errors.append(
                    f"{relative(path)}: broken Markdown link -> {raw_target}"
                )
    return len(files)


def check_reference_routing(skills: list[Path], errors: list[str]) -> None:
    for skill in skills:
        references = skill / "references"
        if not references.is_dir():
            continue
        index = (skill / "SKILL.md").read_text(encoding="utf-8")
        for reference in sorted(references.glob("*.md")):
            expected = f"references/{reference.name}"
            if expected not in index:
                errors.append(
                    f"{relative(reference)}: SKILL.md routingida ko'rsatilmagan"
                )


def run_smartup_validator(errors: list[str]) -> str:
    completed = subprocess.run(
        [sys.executable, str(SMARTUP_VALIDATOR)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = completed.stdout.strip()
    if completed.stderr.strip():
        output = "\n".join(part for part in (output, completed.stderr.strip()) if part)
    if completed.returncode:
        errors.append("smartup-guide knowledge-base validatori muvaffaqiyatsiz")
    return output


def main() -> int:
    errors: list[str] = []
    skills = skill_directories()
    check_skill_packages(skills, errors)
    check_entrypoints(skills, errors)
    check_loaders(errors)
    check_project_guide(skills, errors)
    check_stale_paths(errors)
    check_tracked_generated_files(errors)
    check_artifact_lifecycle(errors)
    markdown_count = check_markdown_links(errors)
    check_reference_routing(skills, errors)
    smartup_output = run_smartup_validator(errors)

    print(f"skills={len(skills)}")
    print(f"markdown_files={markdown_count}")
    print(f"entrypoint_roots={len(ENTRYPOINT_ROOTS)}")
    if smartup_output:
        print("[smartup-guide]")
        print(smartup_output)
    print(f"errors={len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("Shared skills tree is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
