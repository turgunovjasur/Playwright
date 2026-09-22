"""Compatibility: umumiy implementatsiya tests.shared.authorization modulida."""

from tests.shared.authorization import (
    current_company_code as current_company_code,
    login as login,
    dashboard as dashboard,
    authorization as authorization,
)

__all__ = ["current_company_code", "login", "dashboard", "authorization"]
