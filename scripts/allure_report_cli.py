"""Project-local Allure Report 3 CLI entrypoint and shared subprocess helper."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]


class AllureCliNotInstalled(FileNotFoundError):
    """The locked project-local Allure CLI has not been installed."""


@dataclass(frozen=True)
class AllureCommandResult:
    """Allure subprocess outcome exposed to runner, pytest, and CI callers."""

    command: tuple[str, ...]
    returncode: int


def _absolute_path(path: Path, project_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (project_root / path).resolve()


def resolve_allure_executable(project_root: Path = ROOT) -> Path:
    """Resolve only the project-local Allure executable for this platform."""
    executable_name = "allure.cmd" if os.name == "nt" else "allure"
    executable = project_root.resolve() / "node_modules" / ".bin" / executable_name
    if executable.is_file():
        return executable
    raise AllureCliNotInstalled(
        "Project-local Allure 3 CLI topilmadi. Repo rootida `npm ci` "
        "buyrug'ini bajaring."
    )


def build_generate_command(
    results_dir: Path,
    output_dir: Path,
    config_path: Path,
    *,
    project_root: Path = ROOT,
) -> tuple[str, ...]:
    """Build an explicit Allure 3 report generation command."""
    project_root = project_root.resolve()
    executable = resolve_allure_executable(project_root)
    return (
        str(executable),
        "generate",
        str(_absolute_path(results_dir, project_root)),
        "--output",
        str(_absolute_path(output_dir, project_root)),
        "--config",
        str(_absolute_path(config_path, project_root)),
    )


def generate_report(
    results_dir: Path,
    output_dir: Path,
    config_path: Path,
    *,
    project_root: Path = ROOT,
    env: Mapping[str, str] | None = None,
    clean_output: bool = True,
    dry_run: bool = False,
) -> AllureCommandResult:
    """Generate an Allure 3 report and return both command and exit code."""
    project_root = project_root.resolve()
    output_dir = _absolute_path(output_dir, project_root)
    command = build_generate_command(
        results_dir,
        output_dir,
        config_path,
        project_root=project_root,
    )
    if dry_run:
        return AllureCommandResult(command=command, returncode=0)

    if clean_output and output_dir.exists():
        filesystem_root = Path(output_dir.anchor)
        if output_dir in {filesystem_root, project_root}:
            raise ValueError(f"Unsafe Allure output directory: {output_dir}")
        if output_dir.is_symlink() or output_dir.is_file():
            output_dir.unlink()
        else:
            shutil.rmtree(output_dir)

    completed = subprocess.run(
        command,
        cwd=project_root,
        env=dict(env) if env is not None else None,
        check=False,
    )
    return AllureCommandResult(command=command, returncode=completed.returncode)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Locked project-local Allure Report 3 CLI wrapper."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate", help="Allure 3 HTML report yaratish")
    generate.add_argument("results_dir", type=Path)
    generate.add_argument("--output", "-o", required=True, type=Path)
    generate.add_argument("--config", "-c", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = generate_report(
            args.results_dir,
            args.output,
            args.config,
        )
    except (AllureCliNotInstalled, OSError, ValueError) as error:
        print(f"[ALLURE] {error}", file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
