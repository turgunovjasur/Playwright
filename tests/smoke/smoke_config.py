"""Compatibility: umumiy implementatsiya tests.shared.config modulida."""

from tests.shared.config import (
    ROOT_DIR as ROOT_DIR,
    load_local_dotenv as load_local_dotenv,
    env_flag as env_flag,
    option_or_env as option_or_env,
    configure_environment as configure_environment,
    browser_launch_options as browser_launch_options,
    browser_context_options as browser_context_options,
)

__all__ = [
    "ROOT_DIR", "load_local_dotenv", "env_flag", "option_or_env",
    "configure_environment", "browser_launch_options", "browser_context_options",
]
