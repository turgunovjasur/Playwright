import os
import json
import shutil
import socket
import random
import subprocess
import sys
import allure
import pytest
from pathlib import Path
from playwright.sync_api import expect, sync_playwright
from tests.smoke.flows.flow_authorization import authorization
from tests.smoke.progress import emit_progress_event
from utils.logger import write_failure_log, get_logger
from utils.timeouts import PlaywrightTimeouts

TRACE_DIR = "test-results/traces"
DATA_DIR = "test-results/data"
ALLURE_RESULTS_DIR = "test-results/allure-results"
ALLURE_REPORT_DIR = "test-results/allure-report"
CREATED_COMPANY_PASSWORD = "greenwhite"
ROOT_DIR = Path(__file__).resolve().parents[2]

_USER_SETUP_FAILED = False
_FAILED_SMOKE_GROUPS = set()
_LOCAL_DOTENV_EXISTS = False
_PROGRESS_STARTED_ATTR = "_smartup_progress_started"
_PROGRESS_FINISHED_ATTR = "_smartup_progress_finished"


def _load_local_dotenv():
    """Local run profile.

    Agar repo rootda .env mavjud bo'lsa, lokal runlar shu fayldagi qiymatlarni ishlatadi.
    .env yo'q muhitlarda (CI/yangi clone) terminal flaglari va shell env ishlaydi.
    """
    global _LOCAL_DOTENV_EXISTS
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return

    _LOCAL_DOTENV_EXISTS = True
    with env_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key:
                os.environ[key] = value


_load_local_dotenv()


def _env_flag(name):
    return os.getenv(name, "").lower() in {"1", "true", "yes", "on"}


def _normalized_url(value):
    return (value or "").strip().rstrip("/")


def _option_or_env(config, option_name, *env_names, normalize=None):
    value = ""
    if _LOCAL_DOTENV_EXISTS:
        for env_name in env_names:
            value = str(os.getenv(env_name, "") or "").strip()
            if value:
                break
    else:
        value = str(config.getoption(option_name) or "").strip()
        if not value:
            for env_name in env_names:
                value = str(os.getenv(env_name, "") or "").strip()
                if value:
                    break
    return normalize(value) if normalize else value


def _cli_option(config, option_name):
    return str(config.getoption(option_name) or "").strip()


def _option_flag_or_env(config, option_name, *env_names):
    if _LOCAL_DOTENV_EXISTS:
        return any(_env_flag(env_name) for env_name in env_names)
    return bool(config.getoption(option_name)) or any(_env_flag(env_name) for env_name in env_names)


def _company_setup_enabled(config):
    if _LOCAL_DOTENV_EXISTS:
        return _env_flag("CREATE_COMPANY")
    if config.getoption("--create-company"):
        return True
    if _cli_option(config, "--company-code") or _cli_option(config, "--company-password"):
        return False
    return _env_flag("CREATE_COMPANY")


def _run_mode_from_cli_or_env(config):
    if _LOCAL_DOTENV_EXISTS:
        return "create" if _env_flag("CREATE_COMPANY") else "existing"
    if config.getoption("--create-company"):
        return "create"
    if _cli_option(config, "--company-code") or _cli_option(config, "--company-password"):
        return "existing"
    return "create" if _env_flag("CREATE_COMPANY") else "existing"


def _smoke_relative_path(path, root):
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return rel if rel.parts[:2] == ("tests", "smoke") else None


def _explicit_file_args(config):
    root = Path(str(config.rootpath))
    result = []
    for raw_arg in getattr(config.invocation_params, "args", ()) or ():
        if raw_arg.startswith("-"):
            continue
        path_text = raw_arg.split("::", 1)[0]
        if not path_text:
            continue
        path = Path(path_text)
        if not path.is_absolute():
            path = root / path
        if path.is_file():
            result.append(path.resolve())
    return result


def _full_runner_paths(config):
    root = Path(str(config.rootpath))
    return (
        (root / "tests/smoke/test_setup/test_setup_runner.py").resolve(),
        (root / "tests/smoke/test_groups/test_A_grup/test_a_group_runner.py").resolve(),
        (root / "tests/smoke/test_groups/test_B_grup/test_b_group_runner.py").resolve(),
        (root / "tests/smoke/test_groups/test_C_grup/test_c_group_runner.py").resolve(),
        (root / "tests/smoke/test_groups/test_report_grup/test_report_group_runner.py").resolve(),
    )


def _selected_runner_paths(config):
    full_runner_paths = set(_full_runner_paths(config))
    root = Path(str(config.rootpath))
    raw_args = [arg for arg in (getattr(config.invocation_params, "args", ()) or ()) if not arg.startswith("-")]
    if not raw_args:
        return full_runner_paths

    selected = set()
    for raw_arg in raw_args:
        path_text = raw_arg.split("::", 1)[0]
        path = Path(path_text)
        if not path.is_absolute():
            path = root / path
        if not path.is_dir():
            continue
        if path.resolve() == (root / "tests/smoke").resolve():
            return full_runner_paths
        selected.update(runner.resolve() for runner in path.rglob("test_*_runner.py"))
    return selected


def pytest_addoption(parser):
    smoke = parser.getgroup("smartup smoke")
    smoke.addoption("--headless", action="store_true", default=False, help="Chromium ni headless rejimda ishga tushiradi")
    smoke.addoption(
        "--new-code",
        action="store_true",
        default=False,
        help="Yangi 6 xonali code yaratadi; berilmasa data_store.json dagi mavjud code ishlatiladi",
    )
    smoke.addoption("--url", default="", help="Majburiy server URL")
    smoke.addoption(
        "--company-code",
        default="",
        help="Mavjud company code. --create-company bo'lmasa majburiy.",
    )
    smoke.addoption(
        "--company-password",
        default="",
        help="Mavjud company admin paroli. --create-company bo'lmasa majburiy.",
    )
    smoke.addoption(
        "--head-email",
        default="",
        help="--create-company bilan head profil emaili.",
    )
    smoke.addoption(
        "--head-password",
        default="",
        help="--create-company bilan head profil paroli.",
    )
    smoke.addoption(
        "--create-company",
        action="store_true",
        default=False,
        help="Suite boshida yangi company yaratadi va keyingi testlarda shu company_code ishlatiladi.",
    )
    smoke.addoption(
        "--disable-license-policy",
        action="store_true",
        default=False,
        help="--create-company bilan yangi companyda Политика лицензирования ni o'chiradi.",
    )


def pytest_collection_modifyitems(config, items):
    """Directory/default collectionda faqat mos runnerlar qolsin, duplicate business flowlar yurmasin."""
    if not _company_setup_enabled(config):
        skip_company = pytest.mark.skip(
            reason="Company setup faqat --create-company flagi bilan ishlaydi"
        )
        for item in items:
            path_name = Path(str(item.path)).name
            if path_name == "test_company.py" or item.name == "test_00_company":
                item.add_marker(skip_company)

    if _explicit_file_args(config):
        return

    selected_runners = _selected_runner_paths(config)
    if not selected_runners:
        return

    root = Path(str(config.rootpath))
    kept = []
    deselected = []
    for item in items:
        path = Path(str(item.path)).resolve()
        smoke_rel = _smoke_relative_path(path, root)
        if smoke_rel and path.name.startswith("test_") and path not in selected_runners:
            deselected.append(item)
            continue
        kept.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)

    runner_order = {path: index for index, path in enumerate(_full_runner_paths(config))}
    kept.sort(
        key=lambda item: runner_order.get(
            Path(str(item.path)).resolve(),
            len(runner_order),
        )
    )
    items[:] = kept


def _smoke_group_name(item):
    marker = item.get_closest_marker("smoke_group")
    if not marker:
        return None
    if not marker.args:
        raise pytest.UsageError("smoke_group marker group nomini talab qiladi: @pytest.mark.smoke_group('A')")
    return str(marker.args[0])


def _smoke_group_independent(item):
    """smoke_group('X', independent=True) bo'lsa True — group ichida test yiqilsa qolganlar skip qilinmaydi."""
    marker = item.get_closest_marker("smoke_group")
    return bool(marker and marker.kwargs.get("independent", False))


def _is_user_setup(item):
    return item.get_closest_marker("user_setup") is not None


def _progress_metadata(item):
    if _is_user_setup(item):
        group = "Setup"
    else:
        group_name = _smoke_group_name(item)
        if not group_name:
            return None
        group = f"{group_name} group"

    title = getattr(getattr(item, "obj", None), "__allure_display_name__", None) or item.name
    return {
        "group": group,
        "runner": Path(str(item.path)).name,
        "test_id": item.name,
        "title": title,
    }


def _start_progress(item):
    metadata = _progress_metadata(item)
    if not metadata or getattr(item, _PROGRESS_STARTED_ATTR, False):
        return
    setattr(item, _PROGRESS_STARTED_ATTR, True)
    emit_progress_event(event="started", **metadata)


def _finish_progress(item, event, *, error_type=None, message=None):
    metadata = _progress_metadata(item)
    if not metadata or getattr(item, _PROGRESS_FINISHED_ATTR, False):
        return
    setattr(item, _PROGRESS_FINISHED_ATTR, True)
    emit_progress_event(
        event=event,
        error_type=error_type,
        message=message,
        **metadata,
    )


def _report_message(report):
    text = str(report.longrepr or "").strip()
    if not text:
        return ""
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def _is_headless(config):
    return _option_flag_or_env(config, "--headless", "HEADLESS")


def _browser_launch_options(config):
    headless = _is_headless(config)
    return {
        "headless": headless,
        "args": [] if headless else ["--start-maximized"],
    }


def _browser_context_options(config):
    options = {"accept_downloads": True}
    if _is_headless(config):
        options["viewport"] = {"width": 1920, "height": 1080}
    else:
        options["no_viewport"] = True
    return options


def _data_file(file_name="data_store"):
    return Path(DATA_DIR) / f"{file_name}.json"


def _load_data_file(file_name="data_store"):
    path = _data_file(file_name)
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        # Bo'sh fayl (uzilgan run qoldig'i) — yo'q fayl kabi "hali ma'lumot yo'q".
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{path} buzilgan JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AssertionError(f"{path} ichida JSON object bo'lishi kerak")
    return data


def _write_data_file(data, file_name="data_store"):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _data_file(file_name)
    tmp_path = path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    tmp_path.replace(path)


# ----------------------------------------------------------------------------------------------------------------------

def pytest_configure(config):
    """Allure hisoboti uchun environment, categories, executor va history tayyorlaydi."""
    expect.set_options(timeout=PlaywrightTimeouts.ACTION)
    company_url = _option_or_env(config, "--url", "COMPANY_URL", "URL", normalize=_normalized_url)
    run_mode = _run_mode_from_cli_or_env(config)
    create_company = run_mode == "create"

    if create_company:
        company_code = "" if _LOCAL_DOTENV_EXISTS else _cli_option(config, "--company-code").lstrip("@")
        company_password = "" if _LOCAL_DOTENV_EXISTS else _cli_option(config, "--company-password")
        head_email = _option_or_env(config, "--head-email", "HEAD_ADMIN_EMAIL", "HEAD_EMAIL")
        head_password = _option_or_env(config, "--head-password", "HEAD_ADMIN_PASSWORD", "HEAD_PASSWORD")
    else:
        company_code = _option_or_env(config, "--company-code", "COMPANY_CODE").lstrip("@")
        company_password = _option_or_env(config, "--company-password", "COMPANY_PASSWORD")
        head_email = ""
        head_password = ""

    if not company_url:
        raise pytest.UsageError("--url majburiy. Masalan: --url https://app3.greenwhite.uz/xtrade")
    os.environ["COMPANY_URL"] = company_url

    if create_company:
        if company_code:
            raise pytest.UsageError("--create-company bilan --company-code berilmaydi")
        if company_password:
            raise pytest.UsageError("--company-password --create-company bilan berilmaydi; yangi company admin paroli test ichidagi default qiymat")
        if not head_email:
            raise pytest.UsageError("--head-email majburiy: --create-company uchun head profil emailini bering")
        if not head_password:
            raise pytest.UsageError("--head-password majburiy: --create-company uchun head profil parolini bering")
        os.environ["CREATE_COMPANY"] = "1"
        os.environ["COMPANY_PASSWORD"] = CREATED_COMPANY_PASSWORD
        os.environ["HEAD_ADMIN_EMAIL"] = head_email
        os.environ["HEAD_ADMIN_PASSWORD"] = head_password
        os.environ.pop("COMPANY_CODE", None)
    else:
        if head_email or head_password:
            raise pytest.UsageError("--head-email/--head-password faqat --create-company bilan ishlaydi")
        if not company_code:
            raise pytest.UsageError("--company-code majburiy yoki --create-company flagini bering")
        if not company_password:
            raise pytest.UsageError("--company-password majburiy yoki --create-company flagini bering")
        os.environ.pop("CREATE_COMPANY", None)
        os.environ["COMPANY_CODE"] = company_code
        os.environ["COMPANY_PASSWORD"] = company_password
        os.environ.pop("HEAD_ADMIN_EMAIL", None)
        os.environ.pop("HEAD_ADMIN_PASSWORD", None)

    disable_license_policy = _option_flag_or_env(config, "--disable-license-policy", "DISABLE_LICENSE_POLICY")
    if disable_license_policy:
        if not create_company:
            raise pytest.UsageError("--disable-license-policy faqat --create-company bilan ishlaydi")
        os.environ["DISABLE_LICENSE_POLICY"] = "1"
    else:
        os.environ.pop("DISABLE_LICENSE_POLICY", None)

    os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)

    # Trend uchun: oldingi hisobotdan history ko'chirish
    history_src = os.path.join(ALLURE_REPORT_DIR, "history")
    history_dst = os.path.join(ALLURE_RESULTS_DIR, "history")
    if os.path.exists(history_src):
        shutil.rmtree(history_dst, ignore_errors=True)
        try:
            shutil.copytree(history_src, history_dst, dirs_exist_ok=True)
        except FileNotFoundError:
            pass

    # Environment
    env_path = os.path.join(ALLURE_RESULTS_DIR, "environment.properties")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("Browser=Chromium\n")
        f.write(f"Browser.Headless={_is_headless(config)}\n")
        f.write(f"Company.URL={company_url}\n")
        f.write(f"Company.Create={create_company}\n")
        if not create_company:
            f.write(f"Company.Code={company_code}\n")
        f.write("Framework=Playwright\n")
        f.write("Language=Python 3.11\n")
        f.write("Environment=Staging\n")
        f.write(f"Host={socket.gethostname()}\n")

    # Categories
    categories_src = "allure/categories.json"
    categories_dst = os.path.join(ALLURE_RESULTS_DIR, "categories.json")
    if os.path.exists(categories_src):
        shutil.copy(categories_src, categories_dst)

    # Executor
    executor_path = os.path.join(ALLURE_RESULTS_DIR, "executor.json")
    executor_data = {
        "name": socket.gethostname(),
        "type": "local",
        "buildName": "Smoke Tests",
        "reportName": "Allure Report"
    }
    with open(executor_path, "w", encoding="utf-8") as f:
        json.dump(executor_data, f, indent=2)

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture
def browser(request):
    """Bitta browser instance, to'liq ekranda ochiladi."""
    with sync_playwright() as p:
        browser_obj = p.chromium.launch(**_browser_launch_options(request.config))
        yield browser_obj
        browser_obj.close()

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session_browser(request):
    """Butun sessiya uchun bitta browser (setup/group runnerlar uchun)."""
    with sync_playwright() as p:
        browser_obj = p.chromium.launch(**_browser_launch_options(request.config))
        yield browser_obj
        browser_obj.close()

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session_context(session_browser, request):
    """Barcha smoke testlar uchun yagona context. Bitta trace yoziladi."""
    context = session_browser.new_context(**_browser_context_options(request.config))
    context.set_default_timeout(PlaywrightTimeouts.ACTION)
    context.set_default_navigation_timeout(PlaywrightTimeouts.NAVIGATION)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    os.makedirs(TRACE_DIR, exist_ok=True)
    context.tracing.stop(path=os.path.join(TRACE_DIR, "smoke_trace.zip"))
    context.close()

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session_page(session_context):
    """Barcha smoke testlar uchun yagona sahifa — holat saqlanadi."""
    page_obj = session_context.new_page()
    yield page_obj
    page_obj.close()

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def group_session_page(session_browser, request, code):
    """Bitta group runner moduli uchun bitta context/page."""
    context = session_browser.new_context(**_browser_context_options(request.config))
    context.set_default_timeout(PlaywrightTimeouts.ACTION)
    context.set_default_navigation_timeout(PlaywrightTimeouts.NAVIGATION)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page_obj = context.new_page()

    yield page_obj

    os.makedirs(TRACE_DIR, exist_ok=True)
    safe_name = request.module.__name__.replace(".", "_")
    context.tracing.stop(path=os.path.join(TRACE_DIR, f"{safe_name}.zip"))
    page_obj.close()
    context.close()


@pytest.fixture(scope="module")
def group_user_page(group_session_page, code):
    """Group boshida user sifatida bir marta login qiladi."""
    authorization(group_session_page, who="user", code=code)
    return group_session_page

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture
def page(browser, request):
    """Har bir test uchun yangi sahifa, to'liq ekran (no_viewport + --start-maximized). Trace yoziladi."""
    context = browser.new_context(**_browser_context_options(request.config))
    context.set_default_timeout(PlaywrightTimeouts.ACTION)
    context.set_default_navigation_timeout(PlaywrightTimeouts.NAVIGATION)

    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page_obj = context.new_page()

    yield page_obj

    os.makedirs(TRACE_DIR, exist_ok=True)
    safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
    context.tracing.stop(path=os.path.join(TRACE_DIR, f"{safe_name}.zip"))
    page_obj.close()
    context.close()

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def company_setup_enabled(request):
    """Company setup --create-company bilan yoqilgan-yoqilmaganini qaytaradi."""
    return _company_setup_enabled(request.config)

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def code(request):
    """
    NEW_CODE=1 yoki --new-code: yangi random 6 xonali code yaratadi.
    NEW_CODE=0 yoki flag berilmasa: data_store.json fayldan mavjud code ni o'qiydi.
    """
    new_code = _option_flag_or_env(request.config, "--new-code", "NEW_CODE")
    if new_code:
        return str(random.randint(100000, 999999))

    saved = _load_data_file().get("code")
    if saved:
        return saved

    pytest.exit("Yakka test uchun saqlangan 'code' topilmadi. Avval test_setup_runner ni ishga tushiring.")

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def save_data():
    """JSON faylga ma'lumot saqlash."""
    os.makedirs(DATA_DIR, exist_ok=True)

    def _save(key, value, file_name="data_store"):
        data = _load_data_file(file_name)
        data[key] = value
        _write_data_file(data, file_name)

    return _save

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def load_data():
    """JSON fayldan ma'lumot o'qish."""
    def _load(key, file_name="data_store"):
        return _load_data_file(file_name).get(key)

    return _load

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def require_data(load_data):
    """JSON dan majburiy key o'qish; yo'q bo'lsa timeout emas, aniq xato beradi."""
    def _require(key, file_name="data_store"):
        value = load_data(key, file_name=file_name)
        if value in (None, ""):
            raise AssertionError(f"{file_name}.json ichida majburiy key topilmadi: {key}")
        return value

    return _require

# ----------------------------------------------------------------------------------------------------------------------

@pytest.fixture
def logger(request):
    """Har bir test funksiyasi uchun alohida logger fixture."""
    test_logger = get_logger(request.node.nodeid)
    yield test_logger
    test_logger.close()

# ----------------------------------------------------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """User setup va smoke group dependency skip mexanizmi."""
    if _is_user_setup(item):
        if _USER_SETUP_FAILED:
            pytest.skip("Oldingi user_setup testi failed bo'lgani uchun qolgan user_setup testlari skip qilindi")
        _start_progress(item)
        return

    group_name = _smoke_group_name(item)
    if not group_name:
        return

    if _USER_SETUP_FAILED:
        pytest.skip("User setup failed bo'lgani uchun barcha group testlar skip qilindi")

    if group_name in _FAILED_SMOKE_GROUPS and not _smoke_group_independent(item):
        pytest.skip(f"{group_name} group ichidagi oldingi test failed bo'lgani uchun skip qilindi")

    _start_progress(item)

# ----------------------------------------------------------------------------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Test xato bo'lganda screenshot olib Allure ga qo'shadi."""
    global _USER_SETUP_FAILED
    outcome = yield
    report = outcome.get_result()

    if report.failed:
        error_type = call.excinfo.typename if call.excinfo else "Failed"
        exception_message = str(call.excinfo.value).strip() if call.excinfo else ""
        _finish_progress(
            item,
            "failed",
            error_type=error_type,
            message=exception_message or _report_message(report),
        )
    elif report.skipped:
        _finish_progress(
            item,
            "skipped",
            error_type="Skipped",
            message=_report_message(report),
        )
    elif report.when == "teardown":
        _finish_progress(item, "passed")

    if report.when == "call" and report.failed:
        page = (
            item.funcargs.get("session_page")
            or item.funcargs.get("group_user_page")
            or item.funcargs.get("group_session_page")
            or item.funcargs.get("page")
        )
        if page:
            try:
                allure.attach(page.url, name="current-url", attachment_type=allure.attachment_type.TEXT)
                allure.attach(page.title(), name="page-title", attachment_type=allure.attachment_type.TEXT)
                screenshot = page.screenshot(full_page=True)
                allure.attach(
                    screenshot,
                    name="screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as exc:
                allure.attach(str(exc), name="failure-hook-error", attachment_type=allure.attachment_type.TEXT)

        data_path = _data_file()
        if data_path.exists():
            allure.attach(
                data_path.read_text(encoding="utf-8"),
                name="data-store",
                attachment_type=allure.attachment_type.JSON,
            )

    if report.failed:
        if _is_user_setup(item):
            _USER_SETUP_FAILED = True

        group_name = _smoke_group_name(item)
        if group_name and not _smoke_group_independent(item):
            _FAILED_SMOKE_GROUPS.add(group_name)

# ----------------------------------------------------------------------------------------------------------------------

def pytest_runtest_logreport(report):
    """
    Har bir test fazasi (setup / call / teardown) tugaganda chaqiriladi.
    Agar test muvaffaqiyatsiz bo'lsa, test-results/logs/ ichiga log yozadi.
    """
    if report.failed:
        longrepr_str = str(report.longrepr) if report.longrepr else "Xabar yo'q"
        log_path = write_failure_log(report.nodeid, report.when, longrepr_str)
        print(f"\n[LOG] Xato logi saqlandi: {log_path}")

# ----------------------------------------------------------------------------------------------------------------------

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Direct pytest/PyCharm run tugaganda OPEN_REPORT=1 bo'lsa Allure reportni ochadi.

    scripts/run_tests.py o'zi report generate/open qiladi, shuning uchun u orqali kelgan runlarda bu hook skip bo'ladi.
    """
    if not _env_flag("OPEN_REPORT") or _env_flag("SMARTUP_RUNNER"):
        return

    allure_bin = shutil.which("allure")
    if not allure_bin:
        print("\n[ALLURE] OPEN_REPORT=1, lekin allure CLI topilmadi")
        return

    generate_command = [
        allure_bin,
        "generate",
        str(ROOT_DIR / ALLURE_RESULTS_DIR),
        "-o",
        str(ROOT_DIR / ALLURE_REPORT_DIR),
        "--clean",
    ]
    # `allure open` Java serverini browser oynasi yopilgandan keyin ham qoldiradi.
    # Helper report tabining heartbeatini kuzatadi va serverni avtomatik to'xtatadi.
    open_command = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "open_allure_report.py"),
        str(ROOT_DIR / ALLURE_REPORT_DIR),
    ]

    print("\n[ALLURE] Report generate qilinmoqda...")
    generate_result = subprocess.call(generate_command, cwd=ROOT_DIR)
    if generate_result != 0:
        print(f"[ALLURE] Report generate failed: exit_code={generate_result}")
        return

    print("[ALLURE] Report ochilmoqda...")
    subprocess.Popen(open_command, cwd=ROOT_DIR)

# ----------------------------------------------------------------------------------------------------------------------
