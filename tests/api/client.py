"""Biruni HTTP protocol observed in the setup browser network trace."""

import json
from html.parser import HTMLParser
from urllib.parse import urlsplit

import allure

from tests.smoke.test_groups.test_visit_grup.flow_visit.base_api import APIError, BaseAPI


class SmartupAPI(BaseAPI):
    """Cookie authentication, filial headers, model envelopes and paged tables."""

    def __init__(self, base_url):
        super().__init__(base_url)
        self.company_id = None
        self.user_id = None
        self.filial_id = None
        self.admin_filial_id = None
        self.project_code = "trade"
        parsed = urlsplit(self.base_url)
        self.set_default_headers(
            Origin=f"{parsed.scheme}://{parsed.netloc}",
            Referer=self.base_url + "/",
            **{"X-Requested-With": "XMLHttpRequest", "lang_code": "ru"},
        )

    def _send(self, endpoint, *, payload=None, form=None, timeout=None):
        """Send once: a timed-out mutation must never be blindly retried."""
        kwargs = {"allow_redirects": False}
        if timeout is not None:
            kwargs["timeout"] = timeout
        if form is not None:
            kwargs["data"] = form
        else:
            kwargs["json"] = {} if payload is None else payload
        response = self.post("b/" + endpoint, **kwargs)
        # Never attach cookies, credentials, request bodies or raw server errors.
        allure.attach(
            json.dumps({"method": "POST", "endpoint": endpoint,
                        "status": response.status_code}, ensure_ascii=False),
            name="API response", attachment_type=allure.attachment_type.JSON,
        )
        if response.status_code != 200:
            # Only this fixed, credential-free server message is safe to expose.
            license_message = "Нет лицензии для входа в систему!"
            reason = f" ({license_message})" if response.status_code == 401 and license_message.casefold() in response.text.casefold() else ""
            raise APIError(f"POST {endpoint}: HTTP {response.status_code}{reason}")
        if not response.text.strip():
            return None
        try:
            result = response.json()
        except ValueError:
            raise APIError(f"POST {endpoint}: expected JSON/empty body, received non-JSON") from None
        if isinstance(result, dict) and (result.get("error") or result.get("errors")):
            raise APIError(f"POST {endpoint}: server returned an application error")
        if isinstance(result, list) and result and result[0] == "(^_^)":
            if len(result) < 3:
                raise APIError(f"POST {endpoint}: incomplete model envelope")
            return result[2]
        return result

    def call(self, endpoint, payload=None, *, timeout=None):
        return self._send(endpoint, payload=payload, timeout=timeout)

    def login(self, login, password):
        # UI re-login keeps JSESSIONID; retain it when confirming a new password.
        # Dropping the cookie would create another server session/license lease.
        for key in ("company_id", "user_id", "filial_id", "project_code"):
            self.default_headers.pop(key, None)
        self._send("biruni/s$log_in", form={"login": login, "password": password, "lang_code": "ru"})
        info = self.call("biruni/m:session")
        if not isinstance(info, dict) or not info.get("user", {}).get("user_id"):
            raise APIError("Login did not produce an authenticated Biruni session")
        self.company_id = str(info["company_id"])
        self.user_id = str(info["user"]["user_id"])
        self.set_default_headers(company_id=self.company_id, user_id=self.user_id)
        project = next((p for p in info.get("projects", []) if p.get("code") == self.project_code), None)
        if project:
            filials = project.get("filials", [])
            admin = next((f for f in filials if f[1] == "Администрирование"), None)
            self.admin_filial_id = str(admin[0]) if admin else None
            if filials:
                self.use_filial(self.admin_filial_id or filials[0][0])
        return info

    def use_filial(self, filial_id):
        if not filial_id:
            raise APIError("Missing filial ID for the API request")
        self.filial_id = str(filial_id)
        self.set_default_headers(filial_id=self.filial_id, project_code=self.project_code)
        return self

    def context(self, **payload):
        return {"-project_code": self.project_code, "-filial_id": self.filial_id, **payload}

    def model(self, route, **payload):
        result = self.call(route + ":model", self.context(**payload))
        if not isinstance(result, dict):
            raise APIError(f"{route}: expected a model object")
        return result

    def table(self, endpoint, columns, *, filters=None, data=None, sort=None):
        """Decode positional table rows using requested columns; fetch every page."""
        rows = []
        while True:
            payload = {"p": {"column": list(columns), "filter": filters or [],
                             "sort": sort or [], "offset": len(rows), "limit": 1000}}
            if data is not None:
                payload["d"] = data
            result = self.call(endpoint, payload)
            if not isinstance(result, dict) or not isinstance(result.get("data"), list):
                raise APIError(f"{endpoint}: expected table data/count")
            chunk = result["data"]
            total = int(result["count"])
            for row in chunk:
                if not isinstance(row, list) or len(row) != len(columns):
                    raise APIError(f"{endpoint}: table column/row shape mismatch")
                rows.append(dict(zip(columns, row)))
            if len(rows) >= total:
                return rows
            if not chunk:
                raise APIError(f"{endpoint}: empty page before all {total} rows were read")

    def one(self, endpoint, columns, *, filters=None, data=None):
        rows = self.table(endpoint, columns, filters=filters, data=data)
        if len(rows) != 1:
            raise APIError(f"{endpoint}: expected exactly one matching row, found {len(rows)}")
        return rows[0]

    def report_rows(self, endpoint, **parameters):
        """Read the HTML report endpoint used by the UI's postings popup via HTTP."""
        response = self.get(
            "b/" + endpoint,
            params={"rt": "html", "-project_code": self.project_code,
                    "-filial_id": self.filial_id, "-user_id": self.user_id,
                    "-lang_code": "ru", **parameters},
            allow_redirects=False,
        )
        allure.attach(json.dumps({"method": "GET", "endpoint": endpoint,
                                  "status": response.status_code}),
                      name="API report", attachment_type=allure.attachment_type.JSON)
        if response.status_code != 200:
            raise APIError(f"GET {endpoint}: HTTP {response.status_code}")
        parser = _ReportRows()
        parser.feed(response.text)
        if not parser.rows:
            raise APIError(f"GET {endpoint}: expected a report table")
        return parser.rows

    def close(self):
        self.session.close()


def require_fields(actual, **expected):
    """Check persisted business values, independent of a successful save response."""
    for key, value in expected.items():
        if str(actual.get(key)) != str(value):
            raise APIError(f"Persisted field {key!r} does not match the expected setup value")


def positive_id(value):
    if not str(value).isdigit() or int(value) <= 0:
        raise APIError("Expected a positive entity ID from the server")
    return str(value)


class _ReportRows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
