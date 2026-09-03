"""API testlari uchun umumiy HTTP primitive'lari."""

from typing import Any

import requests


DEFAULT_API_TIMEOUT = (10, 60)


class APIError(AssertionError):
    """API transporti yoki response kontrakti bajarilmaganda ko'tariladi."""


class APIConnectTimeout(APIError):
    """HTTPS ulanishi belgilangan vaqtda o'rnatilmaganini ifodalaydi."""

    def __init__(self, *, method, path, connect_timeout, attempts=1):
        self.method = str(method).upper()
        self.path = str(path)
        self.connect_timeout = connect_timeout
        self.attempts = int(attempts)
        timeout_text = f"{connect_timeout:g} sekund" if isinstance(connect_timeout, (int, float)) else "belgilangan vaqt"
        super().__init__(f"API HTTPS ulanishi {timeout_text}da o'rnatilmadi: {self.method} {self.path}; urinishlar={self.attempts}")


class APIRateLimitError(APIError):
    """HTTP 429 javobi va ixtiyoriy Retry-After qiymatini saqlaydi."""

    def __init__(self, retry_after):
        self.retry_after = retry_after
        suffix = (
            f" Retry-After={retry_after}s."
            if retry_after is not None
            else ""
        )
        super().__init__(f"API 429 rate limit qaytardi.{suffix}")


class BaseAPI:
    """API testlari uchun URL, session, request va response'ni boshqaradi."""

    def __init__(
        self,
        base_url,
        *,
        session=None,
        timeout=DEFAULT_API_TIMEOUT,
    ):
        """Base URL va HTTP sessionni tayyorlab ``BaseAPI`` qaytaradi."""
        self.base_url = str(base_url).strip().rstrip("/")
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("BaseAPI: base_url HTTP(S) URL bo'lishi kerak")

        self.session = session or requests.Session()
        self.timeout = timeout
        self.default_headers = {}

    def _url(self, path):
        """Relative pathdan to'liq endpoint URLini qaytaradi."""
        return f"{self.base_url}/{str(path).lstrip('/')}"

    @staticmethod
    def _retry_after(response):
        """Response Retry-After headerini integer yoki ``None`` qiladi."""
        value = response.headers.get("Retry-After")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def set_default_headers(self, **headers):
        """Keyingi requestlar uchun bo'sh bo'lmagan default headerlarni saqlaydi."""
        self.default_headers.update(
            {
                str(key): str(value)
                for key, value in headers.items()
                if value not in (None, "")
            }
        )

    def request(self, method, path, **kwargs):
        """HTTP so'rov yuboradi va ``requests.Response`` qaytaradi."""
        request_method = str(method).upper()
        request_path = str(path)
        headers: dict[str, Any] = dict(self.default_headers)
        headers.update(dict(kwargs.pop("headers", {}) or {}))
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self.session.request(
                request_method,
                self._url(request_path),
                headers=headers,
                **kwargs,
            )
        except requests.ConnectTimeout:
            timeout = kwargs.get("timeout")
            connect_timeout = timeout[0] if isinstance(timeout, tuple) else timeout
            raise APIConnectTimeout(method=request_method, path=request_path, connect_timeout=connect_timeout) from None
        except requests.RequestException as exc:
            raise APIError(f"API request bajarilmadi: {request_method} {request_path}") from exc

        if response.status_code == 429:
            raise APIRateLimitError(self._retry_after(response))
        return response

    def get(self, path, **kwargs):
        """GET so'rov yuboradi va ``requests.Response`` qaytaradi."""
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        """POST so'rov yuboradi va ``requests.Response`` qaytaradi."""
        return self.request("POST", path, **kwargs)

    def require_success(self, response, *, operation):
        """2xx response'ni qaytaradi, aks holda operationli ``APIError`` beradi."""
        if 200 <= response.status_code < 300:
            return response

        message = self.response_text(response)
        suffix = f": {message[:500]}" if message else ""
        raise APIError(
            f"API {operation} HTTP {response.status_code} qaytardi{suffix}"
        )

    def response_json(self, response, *, operation):
        """Response JSON qiymatini qaytaradi, invalid JSONda ``APIError`` beradi."""
        try:
            return response.json()
        except ValueError as exc:
            raise APIError(f"API {operation} javobi JSON emas") from exc

    @staticmethod
    def response_text(response):
        """Response'ning trim qilingan text qiymatini qaytaradi."""
        return (response.text or "").strip()
