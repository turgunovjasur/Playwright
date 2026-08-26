from __future__ import annotations

import hmac
import io
import json
import math
import os
import re
import sys
import threading
import time
import zipfile
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone

import requests


DEFAULT_REPOSITORY = "turgunovjasur/Playwright"
DEFAULT_WORKFLOW = "daily-smoke.yml"
DEFAULT_REF = "main"
STATUS_POLL_INTERVAL_SECONDS = 30
STATUS_POLL_ERROR_LIMIT = 5
TELEGRAM_REQUEST_ATTEMPTS = 3
TELEGRAM_RETRY_DELAYS_SECONDS = (2, 5, 10)
TELEGRAM_MAX_RETRY_WAIT_SECONDS = 10
TASHKENT_TZ = timezone(timedelta(hours=5))

SUITES = {
    "smoke": "Smoke",
    "forms": "Forms",
}
WORKFLOW_JOB_SUITES = ("Smoke", "Report", "Forms")
WORKFLOW_JOB_ORDER = {suite: index for index, suite in enumerate(WORKFLOW_JOB_SUITES)}
DELIVERY_SUITE_ORDER = {
    "Smoke": 0,
    "Report": 1,
    "Report Group": 1,
    "Forms": 2,
}

SERVERS = {
    "smartup": "https://smartup.online",
    "app3": "https://app3.greenwhite.uz/xtrade",
}


class ConfigError(RuntimeError):
    pass


class TelegramAPIError(RuntimeError):
    def __init__(
        self,
        method,
        *,
        category,
        description,
        error_code=None,
        retry_after=0,
        attempts=1,
    ):
        self.method = method
        self.category = category
        safe_description = re.sub(
            r"https://api\.telegram\.org/bot[^/\s]+",
            "https://api.telegram.org/bot<redacted>",
            str(description or "Telegram API xatosi"),
        )
        self.description = safe_description[:300]
        self.error_code = error_code
        self.retry_after = max(0, int(retry_after or 0))
        self.attempts = attempts
        code = f"{error_code} " if error_code is not None else ""
        super().__init__(
            f"Telegram {method} error: {code}{self.description}; "
            f"attempts={attempts}; retry_after={self.retry_after}s"
        )

    @property
    def retryable(self):
        return self.category in {"flood_control", "network", "server"}

    def as_dict(self, *, retry_at_epoch=None):
        data = {
            "method": self.method,
            "category": self.category,
            "description": self.description,
            "error_code": self.error_code,
            "retry_after": self.retry_after,
            "attempts": self.attempts,
        }
        if retry_at_epoch is not None:
            data["retry_at_epoch"] = float(retry_at_epoch)
        return data


@dataclass(frozen=True)
class RunRequest:
    suite_key: str
    server_key: str

    @property
    def suite_label(self):
        return SUITES[self.suite_key]

@dataclass(frozen=True)
class WorkflowRun:
    run_id: int | None
    html_url: str
    status: str = ""
    conclusion: str | None = None
    event: str = ""


@dataclass(frozen=True)
class WorkflowJob:
    suite: str
    status: str
    conclusion: str | None = None
    current_step: str = ""


@dataclass(frozen=True)
class ActiveRun:
    chat_id: str
    request: RunRequest
    workflow_run: WorkflowRun
    started_at: float
    status_message_id: int | None
    extra_status_message_ids: tuple[int, ...] = ()


class ActiveRunStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._active = None

    def get(self):
        with self._lock:
            return self._active

    def set(self, active):
        with self._lock:
            if self._active is not None:
                return False
            self._active = active
            return True

    def clear(self, run_id):
        with self._lock:
            if self._active is None:
                return
            if run_id is None or self._active.workflow_run.run_id == run_id:
                self._active = None

    def add_status_message(self, run_id, message_id):
        if message_id is None:
            return
        with self._lock:
            if self._active is None:
                return
            if run_id is not None and self._active.workflow_run.run_id != run_id:
                return
            message_ids = self._active.extra_status_message_ids
            if message_id == self._active.status_message_id or message_id in message_ids:
                return
            self._active = replace(
                self._active,
                extra_status_message_ids=message_ids + (message_id,),
            )


@dataclass(frozen=True)
class PendingRun:
    request: RunRequest
    prompt_message_id: int


class PendingRunStore:
    """Server tanlangach parol kutilayotgan run so'rovlarini chat bo'yicha saqlaydi."""

    def __init__(self):
        self._lock = threading.Lock()
        self._pending = {}

    def set(self, chat_id, pending):
        with self._lock:
            self._pending[chat_id] = pending

    def get(self, chat_id):
        with self._lock:
            return self._pending.get(chat_id)

    def has(self, chat_id):
        with self._lock:
            return chat_id in self._pending

    def clear(self, chat_id):
        with self._lock:
            self._pending.pop(chat_id, None)


@dataclass(frozen=True)
class BotConfig:
    telegram_token: str
    run_password: str
    github_token: str
    repository: str
    workflow: str
    ref: str
    allowed_server_keys: set[str]


def env_required(name, *fallbacks):
    for key in (name, *fallbacks):
        value = os.getenv(key, "").strip()
        if value:
            return value
    names = ", ".join((name, *fallbacks))
    raise ConfigError(f"Required environment variable is missing: {names}")


def env_value(name, default):
    return os.getenv(name, default).strip() or default


def split_csv(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def server_keys_from_env(value):
    if not value:
        return set(SERVERS)
    keys = set()
    for item in split_csv(value):
        lowered = item.lower().rstrip("/")
        if lowered in SERVERS:
            keys.add(lowered)
            continue
        for key, url in SERVERS.items():
            if lowered == url.rstrip("/"):
                keys.add(key)
                break
    return keys or set(SERVERS)


def load_config():
    allowed_server_keys = server_keys_from_env(os.getenv("ALLOWED_SERVER_URLS", ""))

    # Botdan hamma foydalana oladi; testni run qilish faqat to'g'ri parol bilan ochiladi.
    run_password = env_required("TELEGRAM_RUN_PASSWORD")

    return BotConfig(
        telegram_token=env_required("TELEGRAM_BOT_TOKEN"),
        run_password=run_password,
        github_token=env_required("GITHUB_TOKEN", "GITHUB_PAT"),
        repository=env_value("GITHUB_REPOSITORY", DEFAULT_REPOSITORY),
        workflow=env_value("GITHUB_WORKFLOW_FILE", DEFAULT_WORKFLOW),
        ref=env_value("GITHUB_REF", DEFAULT_REF),
        allowed_server_keys=allowed_server_keys,
    )


class TelegramClient:
    def __init__(self, token):
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = requests.Session()
        self.last_error = None
        self.last_recovered_error = None
        self._retry_not_before = {}

    @staticmethod
    def _category(error_code):
        if error_code == 429:
            return "flood_control"
        if error_code in {401, 403}:
            return "authorization"
        if error_code == 400:
            return "bad_request"
        if isinstance(error_code, int) and error_code >= 500:
            return "server"
        return "telegram"

    @staticmethod
    def _response_error(method, response, attempt):
        try:
            data = response.json()
        except ValueError:
            data = {}
        data = data if isinstance(data, dict) else {}
        error_code = data.get("error_code", response.status_code)
        try:
            error_code = int(error_code)
        except (TypeError, ValueError):
            error_code = response.status_code
        parameters = data.get("parameters")
        parameters = parameters if isinstance(parameters, dict) else {}
        retry_after = parameters.get("retry_after", 0)
        try:
            retry_after = int(retry_after or 0)
        except (TypeError, ValueError):
            retry_after = 0
        description = str(
            data.get("description")
            or response.reason
            or "Telegram API xatosi"
        )
        return TelegramAPIError(
            method,
            category=TelegramClient._category(error_code),
            description=description,
            error_code=error_code,
            retry_after=retry_after,
            attempts=attempt,
        )

    @staticmethod
    def _retry_delay(error, attempt):
        if error.retry_after:
            return error.retry_after
        index = min(max(0, attempt - 1), len(TELEGRAM_RETRY_DELAYS_SECONDS) - 1)
        return TELEGRAM_RETRY_DELAYS_SECONDS[index]

    def _remember_error(self, error, *, retry_at_epoch=None):
        if retry_at_epoch is None and error.retry_after:
            retry_at_epoch = time.time() + error.retry_after
        self.last_error = error.as_dict(retry_at_epoch=retry_at_epoch)
        if error.category == "flood_control" and retry_at_epoch is not None:
            self._retry_not_before[error.method] = retry_at_epoch

    def _cooldown_error(self, method):
        retry_at_epoch = float(self._retry_not_before.get(method) or 0)
        remaining = retry_at_epoch - time.time()
        if remaining <= 0:
            self._retry_not_before.pop(method, None)
            return None
        error = TelegramAPIError(
            method,
            category="flood_control",
            description="Too Many Requests: retry muddati hali tugamagan",
            error_code=429,
            retry_after=max(1, math.ceil(remaining)),
            attempts=0,
        )
        self._remember_error(error, retry_at_epoch=retry_at_epoch)
        return error

    def _remember_success(self, method, recovered_error=None):
        current_error = self.last_error
        if recovered_error is not None:
            self.last_recovered_error = recovered_error.as_dict()
        elif isinstance(current_error, dict) and current_error.get("method") == method:
            self.last_recovered_error = current_error
        if isinstance(current_error, dict) and current_error.get("method") == method:
            self.last_error = None
        self._retry_not_before.pop(method, None)

    def request(self, method, payload, *, max_attempts=TELEGRAM_REQUEST_ATTEMPTS):
        cooldown_error = self._cooldown_error(method)
        if cooldown_error is not None:
            raise cooldown_error

        recovered_error = None
        waited_seconds = 0
        attempts = max(1, int(max_attempts or 1))
        for attempt in range(1, attempts + 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/{method}",
                    data=payload,
                    timeout=60,
                )
            except requests.RequestException as exc:
                error = TelegramAPIError(
                    method,
                    category="network",
                    description=exc.__class__.__name__,
                    attempts=attempt,
                )
            else:
                if response.ok:
                    try:
                        data = response.json()
                    except ValueError:
                        error = TelegramAPIError(
                            method,
                            category="server",
                            description="Telegram noto'g'ri JSON javob qaytardi",
                            error_code=response.status_code,
                            attempts=attempt,
                        )
                    else:
                        if not isinstance(data, dict):
                            error = TelegramAPIError(
                                method,
                                category="server",
                                description="Telegram JSON object qaytarmadi",
                                error_code=response.status_code,
                                attempts=attempt,
                            )
                        elif data.get("ok"):
                            self._remember_success(method, recovered_error)
                            return data
                        else:
                            error = self._response_error(method, response, attempt)
                else:
                    error = self._response_error(method, response, attempt)

            if (
                error.error_code == 400
                and "message is not modified" in error.description.lower()
            ):
                self._remember_success(method, recovered_error)
                return {"ok": True, "result": True}

            self._remember_error(error)
            recovered_error = error
            if not error.retryable or attempt >= attempts:
                raise error
            delay = self._retry_delay(error, attempt)
            if waited_seconds + delay > TELEGRAM_MAX_RETRY_WAIT_SECONDS:
                raise error
            time.sleep(delay)
            waited_seconds += delay

        raise TelegramAPIError(
            method,
            category="telegram",
            description="Telegram request yakunlanmadi",
            attempts=TELEGRAM_REQUEST_ATTEMPTS,
        )

    def get_updates(self, offset):
        payload = {"timeout": 50, "allowed_updates": '["message","callback_query"]'}
        if offset is not None:
            payload["offset"] = offset
        return self.request("getUpdates", payload).get("result", [])

    def send_message(self, chat_id, text, reply_markup=None):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
        if reply_markup is not None:
            payload["reply_markup"] = json.dumps(reply_markup)
        data = self.request("sendMessage", payload).get("result")
        if isinstance(data, dict) and isinstance(data.get("message_id"), int):
            return data["message_id"]
        return None

    def edit_message(
        self,
        chat_id,
        message_id,
        text,
        reply_markup=None,
    ):
        payload = {
            "chat_id": chat_id,
            "message_id": str(message_id),
            "text": text,
            "disable_web_page_preview": "true",
        }
        if reply_markup is not None:
            payload["reply_markup"] = json.dumps(reply_markup)
        self.request(
            "editMessageText",
            payload,
        )

    def delete_message(self, chat_id, message_id):
        self.request(
            "deleteMessage",
            {"chat_id": chat_id, "message_id": str(message_id)},
            max_attempts=1,
        )

    def answer_callback(self, callback_id, text=""):
        payload = {"callback_query_id": callback_id}
        if text:
            payload["text"] = text
        self.request("answerCallbackQuery", payload)


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


def help_text():
    return (
        "Test run qilish uchun /run yuboring. Oxirgi CI va Telegram "
        "notification holati uchun /status yuboring.\n\n"
        "Bot avval Smoke yoki Forms suite'ini, keyin serverni so'raydi.\n"
        "So'ngra parol so'raladi — to'g'ri parol kiritilsa tanlangan test ishga tushadi.\n"
        "Company code/password GitHub Secrets'dan olinadi.\n"
        "Smoke: User setup va Group-0. Forms: faqat markaziy Forms runner.\n"
        "Yakuniy test natijasini GitHub Actions workflow yuboradi.\n"
        "Manual yoki GitHub cron testi jarayonda bo'lsa yangi /run rad etiladi.\n"
        "Soatlik Smoke, Report va Forms runlarini faqat GitHub cron boshqaradi; "
        "bot faqat Smoke yoki Forms manual triggeri uchun.\n\n"
        "To'liq qo'llanma uchun /start yuboring."
    )


def start_text(config):
    servers = "\n".join(f"  • {SERVERS[key]}" for key in sorted(config.allowed_server_keys))
    return (
        "👋 Salom! Bu — Playwright Smoke va Forms testlarini GitHub Actions "
        "orqali manual ishga tushiradigan CI bot.\n"
        "\n"
        "📌 Nima qiladi:\n"
        "Testlarni GitHub Actions workflowda ishga tushiradi va natijani shu chatga yuboradi. "
        "Company code/parol GitHub Secrets'da saqlanadi — bu yerda kiritilmaydi.\n"
        "\n"
        "🚀 Qanday run qilinadi:\n"
        "1. /run yuboring\n"
        "2. Smoke yoki Forms suite'ini tanlang\n"
        "3. Serverni tanlang — Online yoki Xtrade\n"
        "4. Bot parol so'raydi — to'g'ri parolni kiriting (parol QA jamoasida)\n"
        "5. Parol to'g'ri bo'lsa test boshlanadi, bitta xabar jonli yangilanadi\n"
        "6. Tugagach yakuniy natija (passed/failed) shu xabarda chiqadi\n"
        "\n"
        "🌐 Serverlar:\n"
        f"{servers}\n"
        "\n"
        "🧪 Nima test qilinadi:\n"
        "Smoke — User setup → Group-0. Forms — faqat markaziy Forms runner.\n"
        "\n"
        "📊 Natija xabari:\n"
        "Status, hozirgi qadam, passed ro'yxati; failed bo'lsa Group / Runner test / "
        "Ichki test / Step / Error turi ko'rsatiladi.\n"
        "\n"
        "⏱ Soatlik run:\nGitHub cron Online Smoke va Report'ni mustaqil "
        "boshlaydi; Online Forms Smoke tugagach ishlaydi.\n"
        "\n"
        "⚠️ Test ketayotganda yangi /run xabar bilan rad etiladi.\n"
        "\n"
        "Buyruqlar: /run  /status  /servers  /help  /start"
    )


def workflow_status_label(run):
    if run.status != "completed":
        return f"🟡 {run.status or 'queued'}"
    labels = {
        "success": "✅ SUCCESS",
        "failure": "❌ FAILED",
        "cancelled": "⚪ CANCELLED",
        "skipped": "⏭ SKIPPED",
    }
    return labels.get(
        str(run.conclusion or ""),
        str(run.conclusion or "UNKNOWN").upper(),
    )


def workflow_job_status_line(job):
    if job.status == "completed":
        labels = {
            "success": "✅ PASSED",
            "failure": "❌ FAILED",
            "cancelled": "⚪ CANCELLED",
            "skipped": "⏭ SKIPPED",
        }
        status = labels.get(
            str(job.conclusion or ""),
            str(job.conclusion or "UNKNOWN").upper(),
        )
    else:
        labels = {
            "in_progress": "🟡 RUNNING",
            "queued": "🟡 QUEUED",
            "waiting": "🟡 WAITING",
            "pending": "🟡 WAITING",
            "requested": "🟡 QUEUED",
        }
        status = labels.get(job.status, f"🟡 {job.status.upper() or 'QUEUED'}")
    line = f"{job.suite}: {status}"
    if job.current_step and job.status != "completed":
        line += f"\n  Bosqich: {job.current_step}"
    return line


def delivery_status_line(delivery):
    suite = str(delivery.get("suite") or "CI")
    status = str(delivery.get("status") or "unknown")
    labels = {
        "delivered": "✅ yetkazildi",
        "recovered": "⚠️ retry bilan yetkazildi",
        "fallback_sent": "⚠️ yangi final xabar yuborildi",
        "sent_new": "✅ yangi xabar yuborildi",
        "failed": "❌ yetkazilmadi",
        "disabled": "❌ sozlanmagan",
    }
    line = f"{suite}: {labels.get(status, status)}"
    error = delivery.get("error")
    if isinstance(error, dict) and error.get("description"):
        code = f"{error.get('error_code')} " if error.get("error_code") else ""
        line += f"\n  Telegram: {code}{str(error.get('description'))[:180]}"
        retry_after = error.get("retry_after")
        retry_at = str(error.get("retry_at") or "").strip()
        if retry_after:
            line += f"\n  Telegram kutish talabi: {retry_after}s"
        if retry_at:
            line += f" · qayta urinish: {retry_at[11:19]}"
    return line


def bot_error_line(telegram):
    current_error = telegram.last_error
    if isinstance(current_error, dict):
        retry_at_epoch = current_error.get("retry_at_epoch")
        if (
            current_error.get("category") == "flood_control"
            and isinstance(retry_at_epoch, (int, float))
            and retry_at_epoch <= time.time()
        ):
            telegram.last_recovered_error = current_error
            telegram.last_error = None
    error = telegram.last_error or telegram.last_recovered_error
    if not isinstance(error, dict):
        return "Bot Telegram API: ✅ xato qayd etilmagan"
    recovered = telegram.last_error is None
    mark = "⚠️ oldingi xato tiklangan" if recovered else "❌ joriy xato"
    code = f"{error.get('error_code')} " if error.get("error_code") else ""
    line = f"Bot Telegram API: {mark}\n  {code}{str(error.get('description') or '')[:180]}"
    retry_at_epoch = error.get("retry_at_epoch")
    if isinstance(retry_at_epoch, (int, float)) and retry_at_epoch > time.time():
        retry_at = datetime.fromtimestamp(retry_at_epoch, TASHKENT_TZ)
        remaining = max(1, math.ceil(retry_at_epoch - time.time()))
        line += f"\n  Qayta urinish: {retry_at:%H:%M:%S} ({remaining}s qoldi)"
    elif error.get("retry_after"):
        line += f"\n  Telegram kutish talabi: {error.get('retry_after')}s"
    return line


def status_text(telegram, github):
    run = github.latest_run()
    if run is None or run.run_id is None:
        return "CI run topilmadi."

    lines = [
        "📊 Oxirgi CI holati",
        f"Run: {workflow_status_label(run)}",
        f"Trigger: {run.event or 'unknown'}",
    ]
    jobs = github.suite_jobs(run.run_id)
    if jobs:
        lines.extend(["", "Suite holati:"])
        lines.extend(workflow_job_status_line(job) for job in jobs)
    deliveries = github.delivery_statuses(run.run_id)
    if deliveries:
        lines.extend(["", "Telegram notification:"])
        lines.extend(delivery_status_line(item) for item in deliveries)
    elif run.status == "completed":
        lines.extend(
            [
                "",
                "Telegram notification: status artifact topilmadi.",
            ]
        )
    else:
        lines.extend(["", "Telegram notification: ⏳ final holat kutilmoqda."])

    lines.extend(["", bot_error_line(telegram), "", f"🔗 {run.html_url}"])
    return "\n".join(lines)


def suite_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "Smoke", "callback_data": "suite:smoke"},
                {"text": "Forms", "callback_data": "suite:forms"},
            ]
        ]
    }


def server_keyboard(config, suite_key):
    rows = []
    if "smartup" in config.allowed_server_keys:
        rows.append([{"text": "Online", "callback_data": f"server:{suite_key}:smartup"}])
    if "app3" in config.allowed_server_keys:
        rows.append([{"text": "Xtrade", "callback_data": f"server:{suite_key}:app3"}])
    return {"inline_keyboard": rows}


def active_run_text(active):
    elapsed_seconds = max(0, int(time.monotonic() - active.started_at))
    elapsed_minutes = elapsed_seconds // 60
    elapsed_text = "1 daqiqadan kam" if elapsed_minutes == 0 else f"{elapsed_minutes} daqiqa"
    return f"Test jarayonda: {elapsed_text}. Run: {active.workflow_run.html_url}"


def busy_run_text(workflow_run):
    return f"Test jarayonda, yangi run boshlanmadi. Run: {workflow_run.html_url}"


def find_busy_run(github, active_store):
    active = active_store.get()
    if active is not None:
        return active.workflow_run, active
    return github.find_active_run(), None


def transient_status_message_ids(active):
    # Only the throwaway "test jarayonda" reminder replies. The main progress
    # message (status_message_id) becomes the final report and must be kept.
    if active is None:
        return ()
    return tuple(active.extra_status_message_ids)


def safe_delete_message(telegram, chat_id, message_id):
    if message_id is None:
        return
    try:
        telegram.delete_message(chat_id, message_id)
    except Exception as exc:
        print(f"Telegram process message delete failed: {exc}", file=sys.stderr)


def safe_delete_transient_messages(telegram, active):
    if active is None:
        return
    for message_id in transient_status_message_ids(active):
        safe_delete_message(telegram, active.chat_id, message_id)


def show_run_start(
    telegram,
    github,
    chat_id,
    config,
    active_store,
):
    try:
        workflow_run, local_active = find_busy_run(github, active_store)
    except Exception as exc:
        print(f"GitHub active run check failed: {exc}", file=sys.stderr)
        telegram.send_message(chat_id, "Test holatini tekshirib bo'lmadi. Iltimos, qayta urinib ko'ring.")
        return
    if workflow_run is not None:
        message_id = telegram.send_message(chat_id, busy_run_text(workflow_run))
        if local_active is not None:
            active_store.add_status_message(workflow_run.run_id, message_id)
        return
    telegram.send_message(chat_id, "Qaysi testni run qilamiz?", reply_markup=suite_keyboard())


def password_matches(expected, provided):
    return hmac.compare_digest(expected, (provided or "").strip())


def verify_run_password(
    telegram,
    github,
    config,
    active_store,
    pending_store,
    chat_id,
    text,
    user_message_id,
):
    """Parol kutilayotgan chatda kelgan matnni parol sifatida tekshiradi."""
    pending = pending_store.get(chat_id)
    if pending is None:
        return

    # Parol xabari chatda qolmasligi uchun foydalanuvchi yuborgan matnni o'chiramiz.
    safe_delete_message(telegram, chat_id, user_message_id)

    try:
        workflow_run, _local_active = find_busy_run(github, active_store)
    except Exception as exc:
        print(f"GitHub active run check failed: {exc}", file=sys.stderr)
        telegram.edit_message(
            chat_id,
            pending.prompt_message_id,
            "Test holatini tekshirib bo'lmadi. /run bilan qayta urinib ko'ring.",
        )
        pending_store.clear(chat_id)
        return

    if workflow_run is not None:
        pending_store.clear(chat_id)
        telegram.edit_message(chat_id, pending.prompt_message_id, busy_run_text(workflow_run))
        return

    if password_matches(config.run_password, text):
        pending_store.clear(chat_id)
        start_run(telegram, github, chat_id, pending.prompt_message_id, pending.request, active_store)
    else:
        telegram.edit_message(
            chat_id,
            pending.prompt_message_id,
            "❌ Parol noto'g'ri. Qaytadan parolni yuboring yoki /run bilan boshidan boshlang.",
        )


def handle_message(
    telegram,
    github,
    config,
    active_store,
    pending_store,
    chat_id,
    text,
    message_id,
):
    is_command = text.startswith("/")

    # Parol kutilayotgan bo'lsa va bu buyruq bo'lmasa — matnni parol urinishi deb qaraymiz.
    if pending_store.has(chat_id) and not is_command:
        verify_run_password(
            telegram, github, config, active_store, pending_store, chat_id, text, message_id
        )
        return

    # Buyruq kelsa, oldingi parol kutish holatini bekor qilamiz.
    if is_command:
        pending_store.clear(chat_id)

    command = text.split(maxsplit=1)[0].split("@", 1)[0].lower() if text else ""
    if command == "/start":
        telegram.send_message(chat_id, start_text(config))
        return
    if command == "/help":
        telegram.send_message(chat_id, help_text())
        return
    if command == "/servers":
        lines = [SERVERS[key] for key in sorted(config.allowed_server_keys)]
        telegram.send_message(chat_id, "Mavjud serverlar:\n" + "\n".join(lines))
        return
    if command == "/status":
        try:
            message = status_text(telegram, github)
        except requests.RequestException as exc:
            print(
                f"GitHub status request failed: {exc.__class__.__name__}",
                file=sys.stderr,
            )
            message = (
                "❌ CI statusini GitHub'dan olib bo'lmadi. "
                "Iltimos, keyinroq qayta urinib ko'ring."
            )
        telegram.send_message(chat_id, message)
        return
    if command == "/run":
        show_run_start(telegram, github, chat_id, config, active_store)
        return

    telegram.send_message(
        chat_id,
        "Noto'g'ri command. /run, /status yoki /help yuboring.",
    )


def handle_callback(
    telegram,
    github,
    config,
    active_store,
    pending_store,
    callback,
):
    callback_id = str(callback.get("id", ""))
    data = str(callback.get("data", ""))
    message = callback.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    message_id = message.get("message_id")

    if not isinstance(message_id, int):
        telegram.answer_callback(callback_id)
        return

    try:
        workflow_run, local_active = find_busy_run(github, active_store)
    except Exception as exc:
        print(f"GitHub active run check failed: {exc}", file=sys.stderr)
        telegram.answer_callback(callback_id, "Statusni tekshirib bo'lmadi")
        telegram.edit_message(
            chat_id,
            message_id,
            "Test holatini tekshirib bo'lmadi. /run bilan qayta urinib ko'ring.",
        )
        return

    if workflow_run is not None:
        telegram.answer_callback(callback_id, "Test jarayonda")
        active_message_id = telegram.send_message(chat_id, busy_run_text(workflow_run))
        if local_active is not None:
            active_store.add_status_message(workflow_run.run_id, active_message_id)
        return

    if data.startswith("suite:"):
        suite_key = data.split(":", 1)[1]
        if suite_key not in SUITES:
            telegram.answer_callback(callback_id, "Unknown suite")
            return
        telegram.answer_callback(callback_id, "Serverni tanlang")
        telegram.edit_message(
            chat_id,
            message_id,
            f"{SUITES[suite_key]}: qaysi serverda run qilamiz?",
            reply_markup=server_keyboard(config, suite_key),
        )
        return

    if data.startswith("server:"):
        parts = data.split(":")
        if len(parts) != 3:
            telegram.answer_callback(callback_id, "Unknown server action")
            return
        _action, suite_key, server_key = parts
        if suite_key not in SUITES:
            telegram.answer_callback(callback_id, "Unknown suite")
            return
        if server_key not in config.allowed_server_keys or server_key not in SERVERS:
            telegram.answer_callback(callback_id, "Server not allowed")
            return
        telegram.answer_callback(callback_id, "Parol kerak")
        request = RunRequest(
            suite_key=suite_key,
            server_key=server_key,
        )
        pending_store.set(chat_id, PendingRun(request=request, prompt_message_id=message_id))
        telegram.edit_message(
            chat_id,
            message_id,
            (
                f"🔒 {SUITES[suite_key]} · {SERVERS[server_key]}\n\n"
                "Testni run qilish uchun parolni yuboring:"
            ),
        )
        return

    telegram.answer_callback(callback_id, "Unknown action")


def start_run(
    telegram,
    github,
    chat_id,
    message_id,
    request,
    active_store,
):
    try:
        busy_run, _local_active = find_busy_run(github, active_store)
    except Exception as exc:
        print(f"GitHub active run check failed: {exc}", file=sys.stderr)
        telegram.edit_message(
            chat_id,
            message_id,
            "Test holatini tekshirib bo'lmadi. /run bilan qayta urinib ko'ring.",
        )
        return
    if busy_run is not None:
        telegram.edit_message(chat_id, message_id, busy_run_text(busy_run))
        return

    telegram.edit_message(
        chat_id,
        message_id,
        f"{request.suite_label} testi boshlanyapti...",
    )
    try:
        workflow_run = github.dispatch(request, telegram_progress_message_id=message_id)
    except Exception as exc:
        telegram.edit_message(chat_id, message_id, f"Testni boshlashda xato: {exc}")
        return

    telegram.edit_message(
        chat_id,
        message_id,
        f"{request.suite_label} run boshlandi: {workflow_run.html_url}",
    )

    if workflow_run.run_id is not None:
        active = ActiveRun(
            chat_id=chat_id,
            request=request,
            workflow_run=workflow_run,
            started_at=time.monotonic(),
            status_message_id=message_id,
        )
        if not active_store.set(active):
            current = active_store.get()
            if current is not None:
                telegram.send_message(chat_id, active_run_text(current))
            return

    if workflow_run.run_id is None:
        telegram.edit_message(chat_id, message_id, f"Run boshlandi, status GitHub linkda: {workflow_run.html_url}")
        return

    thread = threading.Thread(
        target=monitor_run,
        args=(telegram, github, chat_id, workflow_run, active_store),
        daemon=True,
    )
    thread.start()


def monitor_run(
    telegram,
    github,
    chat_id,
    workflow_run,
    active_store,
):
    assert workflow_run.run_id is not None
    status_errors = 0

    while True:
        try:
            status, _conclusion, _html_url = github.get_run_status(workflow_run.run_id)
        except Exception as exc:
            status_errors += 1
            print(
                f"Temporary GitHub status polling error for run {workflow_run.run_id}: {exc}",
                file=sys.stderr,
            )
            if status_errors >= STATUS_POLL_ERROR_LIMIT:
                active = active_store.get()
                active_store.clear(workflow_run.run_id)
                safe_delete_transient_messages(telegram, active)
                telegram.send_message(
                    chat_id,
                    (
                        f"Run statusini {STATUS_POLL_ERROR_LIMIT} marta olishda xato bo'ldi.\n"
                        "Test GitHub Actionsda davom etayotgan bo'lishi mumkin.\n"
                        f"Run: {workflow_run.html_url}"
                    ),
                )
                return
            time.sleep(STATUS_POLL_INTERVAL_SECONDS)
            continue

        status_errors = 0

        if status == "completed":
            active = active_store.get()
            active_store.clear(workflow_run.run_id)
            safe_delete_transient_messages(telegram, active)
            return

        time.sleep(STATUS_POLL_INTERVAL_SECONDS)


def main():
    try:
        config = load_config()
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2

    telegram = TelegramClient(config.telegram_token)
    github = GitHubActionsClient(config.github_token, config.repository, config.workflow, config.ref)
    active_store = ActiveRunStore()
    pending_store = PendingRunStore()

    offset = None
    print(f"Telegram CI bot started for {config.repository}/{config.workflow} on {config.ref}")
    print("Bot manual trigger rejimida; soatlik schedule GitHub cron tomonidan boshqariladi.")

    while True:
        try:
            updates = telegram.get_updates(offset)
            for update in updates:
                update_id = update.get("update_id")
                if isinstance(update_id, int):
                    offset = update_id + 1

                message = update.get("message")
                if isinstance(message, dict):
                    chat = message.get("chat") or {}
                    chat_id = str(chat.get("id", ""))
                    text = message.get("text")
                    message_id = message.get("message_id")
                    if isinstance(text, str):
                        handle_message(
                            telegram,
                            github,
                            config,
                            active_store,
                            pending_store,
                            chat_id,
                            text.strip(),
                            message_id if isinstance(message_id, int) else None,
                        )
                    continue

                callback = update.get("callback_query")
                if isinstance(callback, dict):
                    handle_callback(telegram, github, config, active_store, pending_store, callback)
        except KeyboardInterrupt:
            print("Stopping Telegram CI bot.")
            return 0
        except Exception as exc:
            print(f"Bot loop error: {exc}", file=sys.stderr)
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
