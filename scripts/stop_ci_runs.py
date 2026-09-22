from __future__ import annotations

import os
import sys

from telegram_ci_bot import GitHubActionsClient
from telegram_ci_settings import load_public_config


def required_token():
    token = (
        os.getenv("GITHUB_TOKEN", "").strip()
        or os.getenv("GITHUB_PAT", "").strip()
    )
    if not token:
        raise RuntimeError("GITHUB_TOKEN or GITHUB_PAT environment variable is required")
    return token


def main():
    try:
        github = load_public_config()["github"]
        client = GitHubActionsClient(
            required_token(),
            github["repository"],
            github["workflow"],
            github["ref"],
        )
        result = client.force_cancel_all_active_runs()
    except Exception as exc:
        print(
            f"GitHub Actions runlarini to'xtatib bo'lmadi: {exc.__class__.__name__}",
            file=sys.stderr,
        )
        return 1

    if not result.active_run_ids:
        print("Active GitHub Actions run topilmadi.")
        return 0

    print(
        f"{len(result.cancelled_run_ids)} ta active run uchun force-cancel yuborildi."
    )
    if result.failed_run_ids:
        failed_ids = ", ".join(str(run_id) for run_id in result.failed_run_ids)
        print(f"Cancel qilib bo'lmagan run IDlari: {failed_ids}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
