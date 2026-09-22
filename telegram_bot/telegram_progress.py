"""CI command-line entry point for progress and final notifications."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "telegram_bot"

import argparse

from .progress_commands import command_delete, command_finish, command_start, command_update
from .progress_runner import command_run


def parse_args():
    parser = argparse.ArgumentParser(description="Telegram progress message helper for GitHub Actions smoke runs.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--server", required=True)
    start.add_argument("--target", required=True)
    start.add_argument(
        "--status",
        default="Python kutubxonalari o‘rnatilmoqda",
    )
    start.add_argument("--message-id", default="")

    update = subparsers.add_parser("update")
    update.add_argument("--status", default="")
    update.add_argument("--current")

    run = subparsers.add_parser("run")
    run.add_argument("command", nargs=argparse.REMAINDER)

    finish = subparsers.add_parser("finish")
    finish.add_argument("--result", required=True)
    finish.add_argument("--run-url", default="")
    finish.add_argument("--run-code", default="")
    finish.add_argument("--summary", default="")

    subparsers.add_parser("delete")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.action == "start":
        return command_start(args)
    if args.action == "update":
        return command_update(args)
    if args.action == "run":
        if args.command and args.command[0] == "--":
            args.command = args.command[1:]
        return command_run(args)
    if args.action == "finish":
        return command_finish(args)
    if args.action == "delete":
        return command_delete(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
