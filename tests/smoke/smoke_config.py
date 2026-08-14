"""Smoke test run konfiguratsiyasi va runner tanlash qoidalari."""

import os
from pathlib import Path

import pytest


CREATED_COMPANY_PASSWORD = "greenwhite"
ROOT_DIR = Path(__file__).resolve().parents[2]

_LOCAL_DOTENV_EXISTS = False


def load_local_dotenv():
    """Repo rootidagi `.env` qiymatlarini lokal pytest run uchun yuklaydi."""
    global _LOCAL_DOTENV_EXISTS
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return

    _LOCAL_DOTENV_EXISTS = True
    with env_path.open("r", encoding="utf-8") as env_file:
        for raw_line in env_file:
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


def env_flag(name):
    """Environment flag qiymatini `True` yoki `False`ga aylantiradi."""
    return os.getenv(name, "").lower() in {"1", "true", "yes", "on"}


def normalized_url(value):
    """URL oxiridagi slash va atrofidagi bo'sh joylarni olib tashlaydi."""
    return (value or "").strip().rstrip("/")


def option_or_env(config, option_name, *env_names, normalize=None):
    """Qiymatni lokal `.env`dan yoki CLI/environment manbalaridan oladi."""
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


def cli_option(config, option_name):
    """Berilgan pytest CLI optionini trim qilingan matn sifatida qaytaradi."""
    return str(config.getoption(option_name) or "").strip()


def option_flag_or_env(config, option_name, *env_names):
    """Boolean optionni lokal `.env`, CLI yoki environmentdan o'qiydi."""
    if _LOCAL_DOTENV_EXISTS:
        return any(env_flag(env_name) for env_name in env_names)
    return bool(config.getoption(option_name)) or any(
        env_flag(env_name) for env_name in env_names
    )


def company_setup_enabled(config):
    """Joriy run yangi company yaratish rejimida ekanini aniqlaydi."""
    if _LOCAL_DOTENV_EXISTS:
        return env_flag("CREATE_COMPANY")
    if config.getoption("--create-company"):
        return True
    if cli_option(config, "--company-code") or cli_option(
        config, "--company-password"
    ):
        return False
    return env_flag("CREATE_COMPANY")


def run_mode(config):
    """Joriy run rejimini `create` yoki `existing` sifatida qaytaradi."""
    if _LOCAL_DOTENV_EXISTS:
        return "create" if env_flag("CREATE_COMPANY") else "existing"
    if config.getoption("--create-company"):
        return "create"
    if cli_option(config, "--company-code") or cli_option(
        config, "--company-password"
    ):
        return "existing"
    return "create" if env_flag("CREATE_COMPANY") else "existing"


def _smoke_relative_path(path, root):
    """Path repo ichidagi `tests/smoke` fayliga tegishli bo'lsa relative path beradi."""
    try:
        relative_path = path.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return (
        relative_path
        if relative_path.parts[:2] == ("tests", "smoke")
        else None
    )


def _explicit_file_args(config):
    """Pytest buyrug'ida bevosita ko'rsatilgan test fayllarini qaytaradi."""
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


def full_runner_paths(config):
    """Full smoke run tarkibiga kiradigan runner fayllarini tartib bilan beradi."""
    root = Path(str(config.rootpath))
    return (
        (root / "tests/smoke/test_setup/test_0_setup_runner.py").resolve(),
        (
            root
            / "tests/smoke/test_groups/test_a_grup/test_0_group_runner.py"
        ).resolve(),
        (
            root
            / "tests/smoke/test_groups/test_report_grup/test_0_group_runner.py"
        ).resolve(),
        (root / "tests/smoke/test_forms/test_0_forms_runner.py").resolve(),
    )


def _selected_runner_paths(config):
    """Pytestga berilgan papka argumentlari bo'yicha runnerlarni tanlaydi."""
    all_runner_paths = set(full_runner_paths(config))
    root = Path(str(config.rootpath))
    raw_args = [
        arg
        for arg in (getattr(config.invocation_params, "args", ()) or ())
        if not arg.startswith("-")
    ]
    if not raw_args:
        return all_runner_paths

    selected = set()
    for raw_arg in raw_args:
        path_text = raw_arg.split("::", 1)[0]
        path = Path(path_text)
        if not path.is_absolute():
            path = root / path
        if not path.is_dir():
            continue
        if path.resolve() == (root / "tests/smoke").resolve():
            return all_runner_paths
        selected.update(
            runner.resolve() for runner in path.rglob("test_*_runner.py")
        )
    return selected


def add_pytest_options(parser):
    """Smartup smoke run uchun qo'shimcha pytest CLI optionlarini ro'yxatdan o'tkazadi."""
    smoke = parser.getgroup("smartup smoke")
    smoke.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Chromium ni headless rejimda ishga tushiradi",
    )
    smoke.addoption(
        "--new-code",
        action="store_true",
        default=False,
        help=(
            "Yangi 6 xonali code yaratadi; berilmasa data_store.json dagi "
            "mavjud code ishlatiladi"
        ),
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
        help=(
            "Suite boshida yangi company yaratadi va keyingi testlarda shu "
            "company_code ishlatiladi."
        ),
    )
    smoke.addoption(
        "--disable-license-policy",
        action="store_true",
        default=False,
        help=(
            "--create-company bilan yangi companyda Политика лицензирования "
            "ni o'chiradi."
        ),
    )


def modify_collected_items(config, items):
    """Directory runlarda leaf testlarni chiqarib, runnerlarni kerakli tartibda qoldiradi."""
    if not company_setup_enabled(config):
        company_items = [
            item
            for item in items
            if Path(str(item.path)).name == "test_0_setup_runner.py"
            and item.name == "test_00_company"
        ]
        if company_items:
            items[:] = [item for item in items if item not in company_items]
            config.hook.pytest_deselected(items=company_items)

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
        smoke_relative_path = _smoke_relative_path(path, root)
        if (
            smoke_relative_path
            and path.name.startswith("test_")
            and path not in selected_runners
        ):
            deselected.append(item)
            continue
        kept.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)

    runner_order = {
        path: index for index, path in enumerate(full_runner_paths(config))
    }
    kept.sort(
        key=lambda item: runner_order.get(
            Path(str(item.path)).resolve(),
            len(runner_order),
        )
    )
    items[:] = kept


def configure_environment(config, load_saved_data):
    """Run credentiallarini tekshiradi, environmentni sozlaydi va run ma'lumotini qaytaradi."""
    company_url = option_or_env(
        config,
        "--url",
        "COMPANY_URL",
        "URL",
        normalize=normalized_url,
    )
    current_run_mode = run_mode(config)
    create_company = current_run_mode == "create"

    if create_company:
        company_code = (
            ""
            if _LOCAL_DOTENV_EXISTS
            else cli_option(config, "--company-code").lstrip("@")
        )
        company_password = (
            ""
            if _LOCAL_DOTENV_EXISTS
            else cli_option(config, "--company-password")
        )
        head_email = option_or_env(config, "--head-email", "HEAD_ADMIN_EMAIL")
        head_password = option_or_env(
            config, "--head-password", "HEAD_ADMIN_PASSWORD"
        )
    else:
        company_code = option_or_env(
            config, "--company-code", "COMPANY_CODE"
        ).lstrip("@")
        company_password = option_or_env(
            config, "--company-password", "COMPANY_PASSWORD"
        )
        head_email = ""
        head_password = ""
        if company_code == "0":
            saved_company_code = load_saved_data().get("company_code")
            if not saved_company_code:
                raise pytest.UsageError(
                    "COMPANY_CODE=0, lekin data_store.json ichida saqlangan "
                    "company_code topilmadi"
                )
            company_code = str(saved_company_code).strip().lstrip("@")

    if not company_url:
        raise pytest.UsageError(
            "--url majburiy. Masalan: --url https://app3.greenwhite.uz/xtrade"
        )
    os.environ["COMPANY_URL"] = company_url

    if create_company:
        if company_code:
            raise pytest.UsageError(
                "--create-company bilan --company-code berilmaydi"
            )
        if company_password:
            raise pytest.UsageError(
                "--company-password --create-company bilan berilmaydi; yangi "
                "company admin paroli test ichidagi default qiymat"
            )
        if not head_email:
            raise pytest.UsageError(
                "CREATE_COMPANY=1 uchun HEAD_ADMIN_EMAIL majburiy"
            )
        if not head_password:
            raise pytest.UsageError(
                "CREATE_COMPANY=1 uchun HEAD_ADMIN_PASSWORD majburiy"
            )
        os.environ["CREATE_COMPANY"] = "1"
        os.environ["COMPANY_PASSWORD"] = CREATED_COMPANY_PASSWORD
        os.environ["HEAD_ADMIN_EMAIL"] = head_email
        os.environ["HEAD_ADMIN_PASSWORD"] = head_password
        os.environ.pop("COMPANY_CODE", None)
    else:
        if head_email or head_password:
            raise pytest.UsageError(
                "--head-email/--head-password faqat --create-company bilan ishlaydi"
            )
        if not company_code:
            raise pytest.UsageError(
                "CREATE_COMPANY=0 uchun COMPANY_CODE majburiy"
            )
        if not company_password:
            raise pytest.UsageError(
                "CREATE_COMPANY=0 uchun COMPANY_PASSWORD majburiy"
            )
        os.environ.pop("CREATE_COMPANY", None)
        os.environ["COMPANY_CODE"] = company_code
        os.environ["COMPANY_PASSWORD"] = company_password
        os.environ.pop("HEAD_ADMIN_EMAIL", None)
        os.environ.pop("HEAD_ADMIN_PASSWORD", None)

    disable_license_policy = option_flag_or_env(
        config,
        "--disable-license-policy",
        "DISABLE_LICENSE_POLICY",
    )
    if disable_license_policy:
        if not create_company:
            raise pytest.UsageError(
                "DISABLE_LICENSE_POLICY faqat CREATE_COMPANY=1 bilan ishlaydi"
            )
        os.environ["DISABLE_LICENSE_POLICY"] = "1"
    else:
        os.environ.pop("DISABLE_LICENSE_POLICY", None)

    return {
        "company_url": company_url,
        "company_code": company_code,
        "create_company": create_company,
    }


def is_headless(config):
    """Chromium headless rejimda ishga tushirilishini aniqlaydi."""
    return option_flag_or_env(config, "--headless", "HEADLESS")


def browser_launch_options(config):
    """Chromium launch uchun Playwright optionlarini tayyorlaydi."""
    headless = is_headless(config)
    return {
        "headless": headless,
        "args": [] if headless else ["--start-maximized"],
    }


def browser_context_options(config):
    """Yangi browser context uchun umumiy Playwright optionlarini qaytaradi."""
    options = {"accept_downloads": True}
    if is_headless(config):
        options["viewport"] = {"width": 1920, "height": 1080}
    else:
        options["no_viewport"] = True
    return options
