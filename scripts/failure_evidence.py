"""Failed test vaqt oynasidagi Playwright dalillari. Browserga ulanmaydi."""

import json
import re
import zipfile
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from utils.report_safety import safe_text, safe_url

try:
    REPORT_TIMEZONE = ZoneInfo("Asia/Tashkent")
except ZoneInfoNotFoundError:
    REPORT_TIMEZONE = timezone(timedelta(hours=5))


def local_time(milliseconds):
    if not milliseconds:
        return "aniqlanmadi"
    try:
        return datetime.fromtimestamp(float(milliseconds) / 1000, timezone.utc).astimezone(
            REPORT_TIMEZONE
        ).strftime("%d.%m.%Y %H:%M:%S.%f")[:-3] + " (Toshkent, UTC+5)"
    except (ValueError, TypeError, OverflowError, OSError):
        return "aniqlanmadi"


def _events(archive, name):
    # Buzilgan yoki haddan katta artifact asosiy hisobotni to'xtatmasin.
    if archive.getinfo(name).file_size > 192 * 1024 * 1024:
        raise ValueError("Trace member hajmi diagnostika limitidan katta")
    with archive.open(name) as stream:
        for line in stream:
            if len(line) > 4 * 1024 * 1024:
                continue
            try:
                yield json.loads(line)
            except (ValueError, UnicodeDecodeError):
                continue


@lru_cache(maxsize=2)
def _trace_index(path, size, mtime):
    """ZIP bir marta o'qiladi; body/header/input qiymatlari saqlanmaydi."""
    calls, network = [], []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        for name in names:
            if not name.endswith(".trace"):
                continue
            offset, pending = None, {}
            for event in _events(archive, name):
                kind = event.get("type")
                if kind == "context-options":
                    if event.get("wallTime") is not None and event.get("monotonicTime") is not None:
                        offset = event["wallTime"] - event["monotonicTime"]
                elif kind == "before" and offset is not None:
                    params = event.get("params") or {}
                    expected = params.get("expectedText") or []
                    pending[event["callId"]] = {
                        "id": event["callId"], "page": event.get("pageId"),
                        "start": offset + event["startTime"],
                        "method": event.get("method", ""),
                        "expression": params.get("expression", ""),
                        "negated": bool(params.get("isNot")),
                        "timeout_ms": params.get("timeout"),
                        "url": safe_url(params.get("url", "")),
                        "expected_url": safe_text(expected[0].get("regexSource") or expected[0].get("string", ""))
                        if expected and params.get("expression") == "to.have.url" else "",
                        "selector": safe_text(params.get("selector", ""))[:400],
                    }
                elif kind == "after" and event.get("callId") in pending:
                    call = pending.pop(event["callId"])
                    call.update(stop=offset + event["endTime"], failed=bool(event.get("error")))
                    calls.append(call)
        for name in names:
            if not name.endswith(".network"):
                continue
            for event in _events(archive, name):
                entry = event.get("snapshot") or {}
                try:
                    start = datetime.fromisoformat(entry["startedDateTime"].replace("Z", "+00:00")).timestamp() * 1000
                    duration = max(float(entry.get("time") or 0), 0)
                except (KeyError, TypeError, ValueError):
                    continue
                response = entry.get("response") or {}
                network.append({
                    "page": entry.get("pageref"), "start": start,
                    "stop": start + duration, "duration_ms": round(duration),
                    "method": entry.get("request", {}).get("method", ""),
                    "url": safe_url(entry.get("request", {}).get("url", "")),
                    "status": response.get("status", 0),
                    "failed": bool(entry.get("_failureText") or response.get("_failureText")),
                })
    return calls, network


def trace_evidence(path, started, stopped, failure_text=""):
    """Faqat failed action bilan mos page va vaqt; post-failure alohida."""
    result = {"available": False, "timeline": [], "network": []}
    if not path:
        return {**result, "note": "Playwright trace mavjud emas; log va runtime dalillari ishlatildi."}
    method_match = re.search(r"(?:Locator|Page|Frame)\.(\w+):", failure_text)
    expected_method = method_match.group(1) if method_match else (
        "expect" if any(s in failure_text for s in ("Locator expected", "Page URL expected", "expect_page:")) else ""
    )
    if not expected_method:
        return {**result, "note": "Xato aniq Playwright amaliga bog'lanmadi; tasodifiy trace xatosi sabab sifatida olinmadi."}
    try:
        path = Path(path)
        stat = path.stat()
        calls, network = _trace_index(str(path.resolve()), stat.st_size, stat.st_mtime_ns)
        start, stop = float(started or 0), float(stopped or 0)
        # Ichki caught assertionlarni asosiy failure deb belgilamaslik.
        failed = [c for c in calls if c["failed"] and c["method"] == expected_method
                  and start <= c["start"] <= c["stop"] <= stop + 250
                  and abs(c["stop"] - stop) <= 2500]
        if not failed:
            return {**result, "note": "Trace ichida ayni failure vaqtiga mos failed UI amal topilmadi."}
        action = max(failed, key=lambda c: c["stop"])
        page = action["page"]
        if not page:
            return {**result, "note": "Failed amalning browser sahifasi aniqlanmadi."}
        scoped = [c for c in calls if c["page"] == page and start <= c["start"] <= action["stop"]]
        url_checks = [c for c in scoped if c["expected_url"] and not c["failed"] and not c["negated"]]
        mutations = {"goto", "reload", "goBack", "goForward", "click", "fill", "press", "check", "selectOption"}
        last_url_check = url_checks[-1] if url_checks else None
        if last_url_check and any(c["method"] in mutations and c["start"] > last_url_check["stop"] for c in scoped):
            last_url_check = None
        if action["expression"] == "to.have.url":
            expected_url, reached = action["expected_url"], None if action["negated"] else False
        else:
            expected_url = last_url_check["expected_url"] if last_url_check else ""
            reached = True if last_url_check else None
        next_action = min((c["start"] for c in calls if c["page"] == page and c["start"] > stop
                           and c["method"] in mutations), default=stop + 15000)
        end = min(stop + 15000, next_action)
        rows = [r for r in network if r["page"] == page and start <= r["start"] < end]
        # Faqat foydali namuna; bu requestlar o'z-o'zidan root cause isboti emas.
        important = [r for r in rows if r["duration_ms"] >= 2000 or r["status"] >= 400 or r["failed"]]
        after = [r for r in rows if r["start"] > stop]
        selected = sorted(important, key=lambda r: r["duration_ms"], reverse=True)[:8]
        for row in after[:6]:
            if row not in selected:
                selected.append(row)
        selected.sort(key=lambda r: r["start"])
        for row in selected:
            row = dict(row)
            row["after_failure"] = row["start"] > stop
            result["network"].append(row)
        result.update(
            available=True, action=action,
            expected_url=expected_url,
            target_url_reached=reached,
            delayed_requests=sum(r["start"] <= stop < r["stop"] for r in rows),
            post_failure_requests=len(after),
            note="Network so'rovlari shu sahifa va test vaqtiga tegishli; ular sababni yakka o'zi isbotlamaydi.",
        )
        result["timeline"] = [
            {"at": action["start"], "text": f"{action['method']} / {action['expression'] or 'UI amal'} boshlandi."},
            {"at": action["stop"], "text": "UI amal xato bilan tugadi."},
        ]
        return result
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError):
        return {**result, "note": "Trace o'qilmadi yoki formati qo'llab-quvvatlanmadi; asosiy failure saqlandi."}
