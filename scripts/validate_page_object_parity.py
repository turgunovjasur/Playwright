#!/usr/bin/env python3
"""Validate public API parity between BasePage and AngularBasePage."""

from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from utils.angular_base_page import AngularBasePage
from utils.base_page import BasePage


def public_methods(cls):
    return {
        name: inspect.signature(member)
        for name, member in inspect.getmembers(cls, predicate=callable)
        if not name.startswith("_")
    }


def normalize_default(value):
    if value is inspect.Parameter.empty:
        return ("empty",)
    if type(value) is object:
        return ("sentinel", "_UNSET")
    if isinstance(value, re.Pattern):
        return ("regex", value.pattern, value.flags)
    return ("value", value)


def normalize_signature(signature):
    return tuple(
        (parameter.name, parameter.kind, normalize_default(parameter.default))
        for parameter in signature.parameters.values()
    )


def main():
    base_methods = public_methods(BasePage)
    angular_methods = public_methods(AngularBasePage)
    base_names = set(base_methods)
    angular_names = set(angular_methods)
    errors = []

    for name in sorted(base_names - angular_names):
        errors.append(f"AngularBasePage methodi yo'q: {name}{base_methods[name]}")
    for name in sorted(angular_names - base_names):
        errors.append(f"AngularBasePage-only public method: {name}{angular_methods[name]}")
    for name in sorted(base_names & angular_names):
        if normalize_signature(base_methods[name]) != normalize_signature(angular_methods[name]):
            errors.append(
                f"Signature mismatch: {name}\n"
                f"  BasePage:        {base_methods[name]}\n"
                f"  AngularBasePage: {angular_methods[name]}"
            )

    if errors:
        print("BasePage/AngularBasePage public API parity: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("BasePage/AngularBasePage public API parity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
