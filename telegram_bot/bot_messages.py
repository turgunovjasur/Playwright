"""Manual bot dialogs and workflow status presentation."""

from __future__ import annotations

from datetime import datetime
import math
import time

from .constants import TASHKENT_TZ


def help_text():
    return (
        "Test run qilish uchun /run yuboring. Oxirgi CI va Telegram "
        "notification holati uchun /status yuboring. Barcha active CI runlarini "
        "to'xtatish uchun /stop yuboring.\n\n"
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
    servers = "\n".join(f"  • {config.servers[key]}" for key in sorted(config.allowed_server_keys))
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
        "Buyruqlar: /run  /stop  /status  /servers  /help  /start"
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


def stop_result_text(result):
    if not result.active_run_ids:
        return "✅ Active CI run topilmadi."
    cancelled = len(result.cancelled_run_ids)
    failed = len(result.failed_run_ids)
    if failed:
        return (
            f"⚠️ {len(result.active_run_ids)} ta active CI run topildi.\n"
            f"Force-cancel yuborildi: {cancelled}\n"
            f"To'xtatib bo'lmadi: {failed}\n"
            "Qolgan runlar holatini /status orqali tekshiring."
        )
    return f"🛑 {cancelled} ta active CI run uchun force-cancel yuborildi."
