"""Share public, versioned Angular assets between isolated Chromium test sessions."""

import base64
import json
import re
import sqlite3
import time
from email.utils import parsedate_to_datetime

from playwright.sync_api import Error as PlaywrightError


# Angular build output, e.g. /a2/chunk-PBT76BKR.js or /a2/media/font-VA4M73IZ.woff2.
_ASSET = re.compile(r"(?:media/)?[\w.-]+-[A-Z0-9]{8}\.(?:js|css|woff2)\Z")
_TYPES = {"js": {"application/javascript", "text/javascript"}, "css": {"text/css"}, "woff2": {"font/woff2"}}
_BYPASS = {"range", "authorization", "if-match", "if-none-match", "if-range",
           "if-modified-since", "if-unmodified-since", "cache-control", "pragma"}
_TRANSPORT_HEADERS = {"content-length", "content-encoding", "transfer-encoding", "connection"}


def _expires(headers):
    directives = {}
    for item in headers.get("cache-control", "").lower().split(","):
        name, _, value = item.strip().partition("=")
        directives[name] = value.strip('"')
    if not {"public", "immutable"} <= directives.keys() or {"no-cache", "private", "no-store"} & directives.keys():
        return 0
    if headers.get("vary", "").lower() not in ("", "accept-encoding"):
        return 0
    if {"set-cookie", "clear-site-data", "authentication-info"} & headers.keys():
        return 0
    now = time.time()
    try:
        max_age = int(directives["max-age"])
        max_age = min(max_age, int(directives.get("s-maxage", max_age)))
        sent = parsedate_to_datetime(headers["date"]).timestamp() if "date" in headers else now
        return min(sent, now - int(headers.get("age", 0))) + max_age
    except (KeyError, ValueError, OverflowError, TypeError):
        return 0


def enable_asset_cache(page, server, directory):
    """Use Chromium's normal network path on misses, redirects and application calls."""
    prefix = server.rstrip("/") + "/a2/"
    try:
        directory.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(directory / "assets.sqlite3", isolation_level=None, timeout=0.2)
    except (sqlite3.Error, OSError):
        return
    try:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=NORMAL")
        db.execute("CREATE TABLE IF NOT EXISTS assets "
                   "(url TEXT PRIMARY KEY, expires REAL, headers TEXT, body BLOB)")
        db.execute("DELETE FROM assets WHERE expires <= ?", (time.time(),))
    except sqlite3.Error:
        db.close()
        return

    def serve(event):
        request = event["request"]
        url = request["url"]
        request_id = {"requestId": event["requestId"]}
        if request["method"] != "GET" or not url.startswith(prefix) or not _ASSET.fullmatch(url[len(prefix):]):
            return request_id
        if "responseErrorReason" in event:
            return request_id
        if "responseStatusCode" in event:
            if event["responseStatusCode"] == 200:
                save_response(url, event, request_id)
            return request_id
        if _BYPASS.intersection(k.lower() for k in request["headers"]):
            return request_id

        row = db.execute("SELECT headers, body FROM assets WHERE url = ? AND expires > ?",
                         (url, time.time())).fetchone()
        if row is None:
            return {**request_id, "interceptResponse": True}
        response_headers, body = row
        session.send("Fetch.fulfillRequest", {
            **request_id, "responseCode": 200, "responseHeaders": json.loads(response_headers),
            "body": base64.b64encode(body).decode("ascii"),
        })
        return None

    def handle(event):
        try:
            params = serve(event)
        except (sqlite3.Error, PlaywrightError, ValueError):
            # The cache is optional, including when another process owns the writer lock.
            params = {"requestId": event["requestId"]}
        if params is None:
            return
        try:
            session.send("Fetch.continueRequest", params)
        except PlaywrightError:
            if not page.is_closed():
                raise

    def save_response(url, event, request_id):
        raw_headers = event["responseHeaders"]
        headers = {}
        for header in raw_headers:
            name = header["name"].lower()
            headers[name] = headers[name] + "," + header["value"] if name in headers else header["value"]
        expiry = _expires(headers)
        mime = headers.get("content-type", "").partition(";")[0].strip().lower()
        if expiry <= time.time() or mime not in _TYPES[url.rsplit(".", 1)[1]]:
            return
        result = session.send("Fetch.getResponseBody", request_id)
        body = base64.b64decode(result["body"]) if result["base64Encoded"] else result["body"].encode("utf-8")
        # CDP returns the decoded entity. Chromium calculates its new transport length.
        keep = [h for h in raw_headers if h["name"].lower() not in _TRANSPORT_HEADERS]
        db.execute("INSERT OR REPLACE INTO assets VALUES (?, ?, ?, ?)", (url, expiry, json.dumps(keep), body))

    try:
        session = page.context.new_cdp_session(page)
        session.on("Fetch.requestPaused", handle)
        session.send("Fetch.enable", {"patterns": [
            {"urlPattern": prefix + "*." + ext, "requestStage": "Request"} for ext in _TYPES
        ]})
    except BaseException:
        db.close()
        raise
    page.once("close", lambda _: db.close())
