#!/usr/bin/env python3
"""Lint page transitions without importing tests or starting a browser.

Page expectations need a destination URL. URL-preserving dialogs/tabs may use
``# navigation: same-url - <reason>`` on the expectation's closing line.
Literal ``+`` routes need a regex accepting both ``+`` and ``%2B``.
Named create/edit/view actions and navigate_to calls need a local expectation
before further UI actions. This is a source check, not a runtime readiness test.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import tokenize
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAME_URL = "navigation: same-url - "
FORM_ACTIONS = {"Создать", "Изменить", "Просмотреть", "Просмотр"}
UI_ACTIONS = {
    "action", "autocomplete", "b_input", "checkbox", "click", "date_picker",
    "grid", "grid_controller", "input", "multiselect", "navigate_to", "radio",
    "switch_filial", "tab",
}


def keyword(call, name, position=None):
    for item in call.keywords:
        if item.arg == name:
            return item.value
    if position is not None and len(call.args) > position:
        return call.args[position]
    return None


def has_url(call):
    value = keyword(call, "url", 1)
    if value is None:
        return False
    if isinstance(value, ast.Constant):
        return isinstance(value.value, str) and bool(value.value.strip())
    return True


def same_url_reason(call, comments):
    comment = comments.get(call.end_lineno, "").removeprefix("#").strip()
    if comment.startswith(SAME_URL):
        return comment[len(SAME_URL):].strip()
    return ""


class FunctionCalls(ast.NodeVisitor):
    """Collect executed statements separately from nested functions/callbacks."""

    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        self.calls.append(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        pass

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef


def transition(call):
    if not isinstance(call.func, ast.Attribute):
        return False
    if call.func.attr == "navigate_to":
        return True
    if call.func.attr not in {"click", "action"}:
        return False
    name = keyword(call, "name", 0)
    return isinstance(name, ast.Constant) and name.value in FORM_ACTIONS


def check_source(path, source):
    errors = []
    try:
        tree = ast.parse(source, filename=str(path))
        comments = {
            token.start[0]: token.string
            for token in tokenize.generate_tokens(io.StringIO(source).readline)
            if token.type == tokenize.COMMENT
        }
    except (SyntaxError, tokenize.TokenError) as error:
        return [(getattr(error, "lineno", 1) or 1, "PARSE", str(error))], 0, 0

    guards = 0
    exceptions = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "expect_page":
            continue
        guards += 1
        reason = same_url_reason(node, comments)
        if not has_url(node):
            if reason:
                exceptions += 1
            else:
                errors.append((node.lineno, "NAV001", "expect_page needs url=; unchanged-URL dialogs/tabs need a same-url reason"))
        elif reason:
            errors.append((node.lineno, "NAV001", "remove the stale same-url exception: this call already checks a URL"))
        url = keyword(node, "url", 1)
        if isinstance(url, ast.Constant) and isinstance(url.value, str) and re.search(r"\+|%2b", url.value, re.IGNORECASE):
            errors.append((node.lineno, "NAV002", "use a URL regex accepting both literal + and encoded %2B"))

    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        visitor = FunctionCalls()
        for statement in function.body:
            visitor.visit(statement)
        calls = sorted(visitor.calls, key=lambda node: (node.lineno, node.col_offset))
        for index, call in enumerate(calls):
            if not transition(call):
                continue
            receiver = ast.dump(call.func.value)
            guarded = False
            for following in calls[index + 1:]:
                if not isinstance(following.func, ast.Attribute) or ast.dump(following.func.value) != receiver:
                    continue
                if following.func.attr == "expect_page":
                    guarded = has_url(following) or bool(same_url_reason(following, comments))
                    break
                if following.func.attr in UI_ACTIONS:
                    break
            if not guarded:
                errors.append((call.lineno, "NAV003", "page transition needs expect_page(url=...) before the next UI action"))
    return sorted(set(errors)), guards, exceptions


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Python files or directories; default: tests/")
    args = parser.parse_args(argv)
    paths = args.paths or [ROOT / "tests"]
    files = set()
    for path in paths:
        if path.is_dir():
            files.update(path.rglob("*.py"))
        elif path.is_file() and path.suffix == ".py":
            files.add(path)
        else:
            parser.error(f"Python source path not found: {path}")
    if not files:
        parser.error("no Python source files found")

    errors = guards = exceptions = 0
    for path in sorted(files):
        findings, count, exempt = check_source(path, path.read_text(encoding="utf-8"))
        guards += count
        exceptions += exempt
        try:
            display = path.resolve().relative_to(ROOT)
        except ValueError:
            display = path
        for line, code, message in findings:
            print(f"{display}:{line}: {code}: {message}")
        errors += len(findings)
    if errors:
        print(f"Page navigation: FAILED ({errors} findings)")
        return 1
    print(f"Page navigation: OK ({len(files)} files, {guards} expectations, {exceptions} documented same-URL cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
