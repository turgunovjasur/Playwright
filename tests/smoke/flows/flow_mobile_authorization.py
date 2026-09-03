"""Smartup mobile login, filial selection va business request flowi."""

from dataclasses import dataclass, field
import hashlib
from time import sleep
from typing import Callable
from uuid import UUID, uuid4

from tests.smoke.flows.flow_authorization import (
    company_url,
    user_email_for,
    user_password,
)
from utils.base_api import APIConnectTimeout, APIError, BaseAPI


PROJECT_CODE = "trade"
LANG_CODE = "ru"
TIMEZONE_CODE = "Asia/Tashkent"
LOGIN_PATH = "/b/biruni/s:log_in_device"
SESSION_INFO_PATH = "/b/biruni/m:session_info_mobile"
UNAUTHENTICATED_MARKERS = (
    "ROUTE: Unauthenticated",
    "Требуется авторизация. Пожалуйста, войдите в систему",
)


@dataclass(frozen=True)
class MobileLogin:
    """Mobile login endpointidan olingan secret bo'lmagan user ma'lumoti."""

    token: str = field(repr=False)
    user_id: int
    user_name: str
    company_name: str


@dataclass(frozen=True)
class MobileSession:
    """Target filial tanlangandan keyingi mobile session ma'lumoti."""

    user_id: int
    user_name: str
    company_name: str
    filial_id: int
    filial_name: str


@dataclass
class MobileAuthorization:
    """Authenticated ``BaseAPI`` va target mobile session contexti."""

    api: BaseAPI
    session: MobileSession
    token: str = field(repr=False)
    filial_id: int
    _reauthenticate: Callable[[], "MobileAuthorization"] = field(repr=False)


def _positive_int(value, *, field_name):
    """Qiymatni musbat integerga aylantirib qaytaradi."""
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise APIError(f"Mobile API {field_name} integer emas") from exc
    if parsed <= 0:
        raise APIError(f"Mobile API {field_name} musbat integer emas")
    return parsed


def _validate_device_code(value):
    """Device code UUID ekanini tekshirib string ko'rinishida qaytaradi."""
    device_code = str(value).strip()
    try:
        UUID(device_code)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("Mobile API device_code UUID formatida bo'lishi kerak") from exc
    return device_code


def _login_payload(*, api, login, password, device_code):
    """Mobile login endpointi uchun JSON payload qaytaradi."""
    password_value = str(password)
    if not password_value:
        raise ValueError("Mobile API password bo'sh bo'lmasligi kerak")

    login_name = str(login).strip()
    if "@" not in login_name or not login_name.rsplit("@", 1)[-1]:
        raise ValueError("Mobile API login user@company formatida bo'lishi kerak")

    password_hash = hashlib.sha1(password_value.encode("utf-8")).hexdigest()
    account_source = f"{login_name}#{api.base_url}"
    account_code = hashlib.sha256(account_source.encode("utf-8")).hexdigest()
    return {
        "login": login_name,
        "password_hash": password_hash,
        "account_code": account_code,
        "device_name": "playwright-mobile-client",
        "device_code": _validate_device_code(device_code),
        "device_version": "test",
        "device_sdk": "test",
        "version_code": "1",
        "version_name": "1.0",
        "device_kind": "A",
    }


def login_mobile(api, *, login, password, device_code, connect_attempts=2, retry_delay_seconds=1):
    """Mobile loginni tekshiradi; connect timeoutda bir marta qayta urinadi."""
    if connect_attempts < 1:
        raise ValueError("Mobile login connect_attempts kamida 1 bo'lishi kerak")
    if retry_delay_seconds < 0:
        raise ValueError("Mobile login retry_delay_seconds manfiy bo'lmasligi kerak")

    login_payload = _login_payload(api=api, login=login, password=password, device_code=device_code)
    for attempt in range(1, connect_attempts + 1):
        try:
            response = api.post(LOGIN_PATH, headers={"Content-Type": "application/json", "project_code": PROJECT_CODE}, json=login_payload)
            break
        except APIConnectTimeout as exc:
            if attempt == connect_attempts:
                raise APIConnectTimeout(method=exc.method, path=exc.path, connect_timeout=exc.connect_timeout, attempts=attempt) from None
            sleep(retry_delay_seconds)

    api.require_success(response, operation="mobile login")
    payload = api.response_json(response, operation="mobile login")
    if not isinstance(payload, dict):
        raise APIError("Mobile API login javobi JSON object emas")

    token = str(payload.get("token") or "").strip()
    if not token:
        raise APIError("Mobile API login javobida token yo'q")

    return MobileLogin(
        token=token,
        user_id=_positive_int(payload.get("user_id"), field_name="login.user_id"),
        user_name=str(payload.get("user_name") or "").strip(),
        company_name=str(payload.get("company_name") or "").strip(),
    )


def get_mobile_session(api, *, login_result, target_filial_id):
    """Target trade filialini topib ``MobileSession`` qaytaradi."""
    target_filial_id = _positive_int(
        target_filial_id,
        field_name="target_filial_id",
    )
    response = api.get(
        SESSION_INFO_PATH,
        headers={"token": login_result.token, "lang_code": LANG_CODE},
    )
    api.require_success(response, operation="mobile session info")
    payload = api.response_json(response, operation="mobile session info")
    if not isinstance(payload, list) or len(payload) <= 4:
        raise APIError(
            "session_info_mobile javobi positional array kontraktiga mos emas"
        )

    projects = payload[4]
    if not isinstance(projects, list):
        raise APIError("session_info_mobile projects array emas")

    trade_project = next(
        (
            project
            for project in projects
            if isinstance(project, list)
            and len(project) >= 3
            and project[0] == PROJECT_CODE
        ),
        None,
    )
    if trade_project is None:
        raise APIError("session_info_mobile ichida trade project topilmadi")

    filials = trade_project[2]
    if not isinstance(filials, list):
        raise APIError("session_info_mobile trade filials array emas")

    matched_filial = next(
        (
            filial
            for filial in filials
            if isinstance(filial, list)
            and len(filial) >= 2
            and str(filial[0]).isdigit()
            and int(filial[0]) == target_filial_id
        ),
        None,
    )
    if matched_filial is None:
        raise APIError(
            "session_info_mobile trade projectida target filial topilmadi"
        )

    session_user_name = str(payload[0] or "").strip() if payload else ""
    company_name = (
        str(payload[7] or "").strip()
        if len(payload) > 7
        else login_result.company_name
    )
    return MobileSession(
        user_id=login_result.user_id,
        user_name=session_user_name or login_result.user_name,
        company_name=company_name or login_result.company_name,
        filial_id=target_filial_id,
        filial_name=str(matched_filial[1] or "").strip(),
    )


def _authorize_with_credentials(
    *,
    server_url,
    login,
    password,
    device_code,
    target_filial_id,
):
    """Berilgan credentiallar bilan yangi authenticated context qaytaradi."""
    api = BaseAPI(server_url)
    login_result = login_mobile(
        api,
        login=login,
        password=password,
        device_code=device_code,
    )
    session = get_mobile_session(
        api,
        login_result=login_result,
        target_filial_id=target_filial_id,
    )
    api.set_default_headers(
        token=login_result.token,
        project_code=PROJECT_CODE,
        filial_id=session.filial_id,
        timezone_code=TIMEZONE_CODE,
    )
    return MobileAuthorization(
        api=api,
        session=session,
        token=login_result.token,
        filial_id=session.filial_id,
        _reauthenticate=lambda: _authorize_with_credentials(
            server_url=server_url,
            login=login,
            password=password,
            device_code=device_code,
            target_filial_id=target_filial_id,
        ),
    )


def authorize_mobile(load_data, save_data):
    """Mobile login va target filialni tekshirib authorization qaytaradi."""
    code = load_data("code")
    device_code = load_data("mobile_device_code", allow_missing=True)
    if device_code is None:
        device_code = str(uuid4())
        save_data("mobile_device_code", device_code)

    authorization = _authorize_with_credentials(
        server_url=company_url(),
        login=user_email_for(str(code)),
        password=user_password(),
        device_code=device_code,
        target_filial_id=load_data("filial_id"),
    )
    if authorization.session.filial_name != load_data("filial_name"):
        raise AssertionError(
            "Mobile session target filial nomi data_store bilan mos emas"
        )
    return authorization


def request_mobile_business(authorization, method, path, **kwargs):
    """Business request yuboradi, unauthenticated bo'lsa bir marta qayta urinadi."""
    for attempt in range(2):
        response = authorization.api.request(method, path, **kwargs)
        body = authorization.api.response_text(response)
        unauthenticated = response.status_code == 401 or any(
            marker in body for marker in UNAUTHENTICATED_MARKERS
        )
        if not unauthenticated:
            return response
        if attempt == 1:
            raise APIError(
                "Mobile API qayta logindan keyin ham unauthenticated qaytardi"
            )

        refreshed = authorization._reauthenticate()
        authorization.api = refreshed.api
        authorization.session = refreshed.session
        authorization.token = refreshed.token
        authorization.filial_id = refreshed.filial_id
        authorization._reauthenticate = refreshed._reauthenticate

    raise APIError("Mobile API business request yakunlanmadi")
