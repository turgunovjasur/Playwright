"""Attach the HTTP exchange to the active Allure step, including rejected requests."""

import base64
import json
import logging
from email.message import Message
from urllib.parse import parse_qsl

import allure


def _body(data, content_type, *, parse=True):
    if data is None:
        return None
    if isinstance(data, bytes):
        media = Message()
        media["content-type"] = content_type or "text/plain"
        try:
            data = data.decode(media.get_content_charset() or "utf-8")
        except (LookupError, UnicodeDecodeError):
            return {"encoding": "base64", "data": base64.b64encode(data).decode("ascii")}
    if parse and isinstance(data, str):
        if (content_type or "").partition(";")[0].lower() == "application/x-www-form-urlencoded":
            return {"form": parse_qsl(data, keep_blank_values=True), "encoded": data}
        try:
            return json.loads(data)
        except (ValueError, RecursionError):
            return data
    return data


def attach_exchange(method, endpoint, url, headers, options, *, response=None, error=None):
    try:
        prepared = response.request if response is not None else getattr(error, "request", None)
        if prepared is not None:
            request = {"method": prepared.method, "url": prepared.url,
                       "headers": dict(prepared.headers),
                       "body": _body(prepared.body, prepared.headers.get("Content-Type"))}
        else:
            request = {"method": method, "url": url, "headers": dict(headers),
                       "params": options.get("params"),
                       "body": options.get("json", options.get("data"))}
        status = response.status_code if response is not None else None
        exchange = {"method": request["method"], "endpoint": endpoint, "status": status,
                    "request": request, "response": None}
        if response is not None:
            media_type = response.headers.get("Content-Type")
            raw = _body(response.content, media_type, parse=False)
            body = _body(raw, media_type)
            exchange["response"] = {"status": status, "headers": dict(response.headers),
                                    "body": body}
            application_error = isinstance(body, dict) and (body.get("error") or body.get("errors"))
            if (status != 200 or application_error) and isinstance(raw, str) and raw != body:
                exchange["response"]["body_text"] = raw
        if error is not None:
            exchange["transport_error"] = f"{type(error).__name__}: {error}"
        allure.attach(json.dumps(exchange, ensure_ascii=False, indent=2, default=str),
                      name=f"API request / response · {request['method']} {endpoint} · {status or 'transport error'}",
                      attachment_type=allure.attachment_type.JSON)
    except Exception:
        # Report generation must not change the result or retry a mutation.
        logging.getLogger(__name__).warning("HTTP exchange attachment could not be written")
