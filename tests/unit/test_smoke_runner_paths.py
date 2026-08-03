import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts import run_tests
from tests.smoke import smoke_config


def test_group_runner_paths_are_named_and_ordered_after_setup():
    expected_group_paths = [
        "tests/smoke/test_groups/test_0_grup/test_0_group_runner.py",
        "tests/smoke/test_groups/test_report_grup/test_0_group_runner.py",
    ]

    assert list(run_tests.GROUP_RUNNER_PATHS) == expected_group_paths
    assert run_tests.TARGETS["setup-group-0"] == (
        (
            "tests/smoke/test_setup/test_0_setup_runner.py",
            expected_group_paths[0],
        ),
        "--new-code",
    )
    assert run_tests.TARGETS["group-0"] == (expected_group_paths[0], "")
    assert run_tests.TARGETS["group-report"] == (expected_group_paths[1], "")
    assert "group-a" not in run_tests.TARGETS
    assert "group-b" not in run_tests.TARGETS
    assert "group-c" not in run_tests.TARGETS

    config = SimpleNamespace(rootpath=run_tests.ROOT)
    actual_full_paths = [
        path.relative_to(run_tests.ROOT).as_posix()
        for path in smoke_config.full_runner_paths(config)
    ]

    assert actual_full_paths == [
        "tests/smoke/test_setup/test_0_setup_runner.py",
        *expected_group_paths,
        "tests/smoke/test_forms/test_0_forms_runner.py",
    ]
    assert all((run_tests.ROOT / path).is_file() for path in actual_full_paths)


def test_all_and_groups_targets_include_group_0_in_runner_order():
    all_paths, all_code_mode = run_tests.TARGETS["all"]
    groups_paths, groups_code_mode = run_tests.TARGETS["groups"]

    assert all_paths == (
        "tests/smoke/test_setup/test_0_setup_runner.py",
        *run_tests.GROUP_RUNNER_PATHS,
        run_tests.FORMS_RUNNER_PATH,
    )
    assert all_code_mode == "--new-code"
    assert groups_paths == run_tests.GROUP_RUNNER_PATHS
    assert groups_code_mode == ""


def test_new_code_precedence_blocks_group_only_without_setup():
    assert run_tests.new_code_enabled(
        {"NEW_CODE": "1"},
        local_dotenv_exists=True,
        pytest_extra=[],
    )
    assert not run_tests.new_code_enabled(
        {"NEW_CODE": "0"},
        local_dotenv_exists=True,
        pytest_extra=["--new-code"],
    )
    assert run_tests.new_code_enabled(
        {},
        local_dotenv_exists=False,
        pytest_extra=["--new-code"],
    )
    assert "group-0" in run_tests.GROUP_ONLY_CODE_TARGETS
    assert "setup-group-0" not in run_tests.GROUP_ONLY_CODE_TARGETS
