"""Page readiness dalili; assertion yoki browser xatti-harakatini o'zgartirmaydi."""

import inspect
import json
import time
from functools import wraps

import allure
from utils.report_safety import safe_text


def expectation_gate(page, name):
    page._smartup_expectation_gate = name


def report_page_expectation(method):
    signature = inspect.signature(method)

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        started = time.time()
        previous_gate = getattr(self.page, "_smartup_expectation_gate", "")
        expectation_gate(self.page, "validation")
        try:
            return method(self, *args, **kwargs)
        except Exception as error:
            if getattr(error, "_smartup_expectation_reported", False):
                raise
            # Diagnostika xatosi asl exceptionni almashtirmasligi kerak.
            try:
                arguments = signature.bind(self, *args, **kwargs)
                arguments.apply_defaults()
                values = arguments.arguments
                expected_url = values.get("url")
                heading = values.get("heading")
                allure.attach(
                    json.dumps({
                        "operation": method.__name__,
                        "gate": getattr(self.page, "_smartup_expectation_gate", ""),
                        "started_at": int(started * 1000),
                        "failed_at": int(time.time() * 1000),
                        "expected_url": safe_text(getattr(expected_url, "pattern", expected_url)),
                        "url_is_regex": hasattr(expected_url, "pattern"),
                        "expected_heading": safe_text(getattr(heading, "pattern", heading)),
                        "timeout_ms": values.get("timeout"),
                    }, ensure_ascii=False),
                    name="page-expectation",
                    attachment_type=allure.attachment_type.JSON,
                )
                error._smartup_expectation_reported = True
            except Exception:
                pass
            raise
        finally:
            expectation_gate(self.page, previous_gate)

    return wrapped
