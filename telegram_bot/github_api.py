"""GitHub Actions dispatch, monitoring, artifacts and cancellation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import io
import json
import requests
import time
import zipfile

from .constants import (
    ACTIVE_WORKFLOW_RUN_STATUSES,
    DELIVERY_SUITE_ORDER,
    WORKFLOW_JOB_ORDER,
    WORKFLOW_JOB_SUITES,
)
from .models import CancelRunsResult, WorkflowJob, WorkflowRun


class GitHubActionsClient:
    def __init__(self, token, repository, workflow, ref):
        self.repository = repository
        self.workflow = workflow
        self.ref = ref
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    @property
    def workflow_url(self):
        return f"https://github.com/{self.repository}/actions/workflows/{self.workflow}"

    def dispatch(self, request, telegram_progress_message_id=None):
        started_at = datetime.now(timezone.utc)
        url = f"https://api.github.com/repos/{self.repository}/actions/workflows/{self.workflow}/dispatches"
        inputs = {
            "suite": request.suite_key,
            "server": request.server_key,
        }
        if telegram_progress_message_id is not None:
            inputs["telegram_progress_message_id"] = str(telegram_progress_message_id)
        response = self.session.post(
            url,
            json={
                "ref": self.ref,
                "inputs": inputs,
            },
            timeout=30,
        )
        if response.status_code != 204:
            raise RuntimeError(f"GitHub dispatch failed: {response.status_code} {response.text}")

        return self.find_new_run(started_at)

    def find_active_run(self):
        """Scheduled yoki manual workflow hozir active bo'lsa qaytaradi."""
        url = f"https://api.github.com/repos/{self.repository}/actions/workflows/{self.workflow}/runs"
        response = self.session.get(
            url,
            params={"branch": self.ref, "per_page": "20"},
            timeout=30,
        )
        response.raise_for_status()
        runs = response.json().get("workflow_runs", [])
        for item in runs:
            if str(item.get("event", "")) not in {"schedule", "workflow_dispatch"}:
                continue
            if str(item.get("status", "")) in {"", "completed"}:
                continue
            run_id = item.get("id")
            html_url = item.get("html_url")
            if isinstance(run_id, int) and isinstance(html_url, str):
                return WorkflowRun(run_id=run_id, html_url=html_url)
        return None

    def active_runs(self):
        """Repo bo'yicha barcha active workflow runlarini qaytaradi."""
        url = f"https://api.github.com/repos/{self.repository}/actions/runs"
        runs_by_id = {}
        for status in ACTIVE_WORKFLOW_RUN_STATUSES:
            page = 1
            while True:
                response = self.session.get(
                    url,
                    params={"status": status, "per_page": "100", "page": str(page)},
                    timeout=30,
                )
                response.raise_for_status()
                items = response.json().get("workflow_runs", [])
                for item in items:
                    run_id = item.get("id")
                    html_url = item.get("html_url")
                    if not isinstance(run_id, int) or not isinstance(html_url, str):
                        continue
                    runs_by_id[run_id] = WorkflowRun(
                        run_id=run_id,
                        html_url=html_url,
                        status=str(item.get("status") or status),
                        conclusion=(
                            str(item.get("conclusion"))
                            if item.get("conclusion") is not None
                            else None
                        ),
                        event=str(item.get("event") or ""),
                    )
                if len(items) < 100:
                    break
                page += 1
        return sorted(runs_by_id.values(), key=lambda run: run.run_id or 0)

    def force_cancel_all_active_runs(self):
        active_runs = self.active_runs()
        cancelled_run_ids = []
        failed_run_ids = []
        for run in active_runs:
            if run.run_id is None:
                continue
            url = (
                f"https://api.github.com/repos/{self.repository}/actions/"
                f"runs/{run.run_id}/force-cancel"
            )
            try:
                response = self.session.post(url, timeout=30)
                if response.status_code not in {202, 204}:
                    response.raise_for_status()
            except requests.RequestException:
                failed_run_ids.append(run.run_id)
                continue
            cancelled_run_ids.append(run.run_id)
        return CancelRunsResult(
            active_run_ids=tuple(run.run_id for run in active_runs if run.run_id is not None),
            cancelled_run_ids=tuple(cancelled_run_ids),
            failed_run_ids=tuple(failed_run_ids),
        )

    def find_new_run(self, started_at):
        deadline = time.monotonic() + 30
        earliest = started_at - timedelta(seconds=15)
        while time.monotonic() < deadline:
            run = self.latest_matching_run(earliest)
            if run is not None:
                return run
            time.sleep(3)
        return WorkflowRun(run_id=None, html_url=self.workflow_url)

    def latest_matching_run(self, earliest):
        url = f"https://api.github.com/repos/{self.repository}/actions/workflows/{self.workflow}/runs"
        response = self.session.get(
            url,
            params={"branch": self.ref, "event": "workflow_dispatch", "per_page": "10"},
            timeout=30,
        )
        response.raise_for_status()
        runs = response.json().get("workflow_runs", [])
        for item in runs:
            created_at = parse_github_time(str(item.get("created_at", "")))
            if created_at is None or created_at < earliest:
                continue
            run_id = item.get("id")
            html_url = item.get("html_url")
            if isinstance(run_id, int) and isinstance(html_url, str):
                return WorkflowRun(run_id=run_id, html_url=html_url)
        return None

    def get_run_status(self, run_id):
        url = f"https://api.github.com/repos/{self.repository}/actions/runs/{run_id}"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return str(data.get("status", "")), data.get("conclusion"), str(data.get("html_url", self.workflow_url))

    def latest_run(self):
        url = f"https://api.github.com/repos/{self.repository}/actions/workflows/{self.workflow}/runs"
        response = self.session.get(
            url,
            params={"branch": self.ref, "per_page": "20"},
            timeout=30,
        )
        response.raise_for_status()
        runs = response.json().get("workflow_runs", [])
        for item in runs:
            event = str(item.get("event") or "")
            if event not in {"schedule", "workflow_dispatch"}:
                continue
            run_id = item.get("id")
            html_url = item.get("html_url")
            if isinstance(run_id, int) and isinstance(html_url, str):
                return WorkflowRun(
                    run_id=run_id,
                    html_url=html_url,
                    status=str(item.get("status") or ""),
                    conclusion=(
                        str(item.get("conclusion"))
                        if item.get("conclusion") is not None
                        else None
                    ),
                    event=event,
                )
        return None

    def delivery_statuses(self, run_id):
        url = f"https://api.github.com/repos/{self.repository}/actions/runs/{run_id}/artifacts"
        response = self.session.get(url, params={"per_page": "100"}, timeout=30)
        response.raise_for_status()
        artifacts = response.json().get("artifacts", [])
        statuses = []
        for artifact in artifacts:
            name = str(artifact.get("name") or "")
            artifact_id = artifact.get("id")
            if not name.endswith("-telegram-status") or not isinstance(artifact_id, int):
                continue
            download_url = (
                f"https://api.github.com/repos/{self.repository}/actions/"
                f"artifacts/{artifact_id}/zip"
            )
            download = self.session.get(download_url, timeout=30)
            download.raise_for_status()
            try:
                with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
                    status_file = next(
                        (
                            member
                            for member in archive.namelist()
                            if member.endswith("telegram-delivery.json")
                        ),
                        None,
                    )
                    if status_file is None:
                        continue
                    data = json.loads(archive.read(status_file).decode("utf-8"))
            except (zipfile.BadZipFile, KeyError, UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(data, dict):
                statuses.append(data)
        return sorted(
            statuses,
            key=lambda item: DELIVERY_SUITE_ORDER.get(
                str(item.get("suite") or ""),
                len(DELIVERY_SUITE_ORDER),
            ),
        )

    def suite_jobs(self, run_id):
        url = f"https://api.github.com/repos/{self.repository}/actions/runs/{run_id}/jobs"
        response = self.session.get(url, params={"per_page": "100"}, timeout=30)
        response.raise_for_status()
        jobs = []
        for item in response.json().get("jobs", []):
            name = str(item.get("name") or "")
            suite = next(
                (
                    label
                    for label in WORKFLOW_JOB_SUITES
                    if name == label or name.startswith(f"{label} /")
                ),
                None,
            )
            if suite is None:
                continue
            current_step = next(
                (
                    str(step.get("name") or "")
                    for step in (item.get("steps") or [])
                    if str(step.get("status") or "")
                    in {"in_progress", "queued", "pending"}
                ),
                "",
            )
            jobs.append(
                WorkflowJob(
                    suite=suite,
                    status=str(item.get("status") or ""),
                    conclusion=(
                        str(item.get("conclusion"))
                        if item.get("conclusion") is not None
                        else None
                    ),
                    current_step=current_step,
                )
            )
        return sorted(
            jobs,
            key=lambda item: WORKFLOW_JOB_ORDER.get(
                item.suite,
                len(WORKFLOW_JOB_ORDER),
            ),
        )


def parse_github_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
