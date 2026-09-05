# Copyright (C) 2026 Glenson Dsouza
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Command line for loops: emit a /goal prompt, or check that one meets the bar."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from grok_bot.prompt import GoalError, check_prompt, emit_prompt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m grok_bot",
        description=(
            "loops Grok Bot helper. Gather one task and print a short "
            "/goal prompt a cloud coding agent can run, or check that a "
            "prompt already names a repo and a stranger-checkable done-when."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    emit = sub.add_parser(
        "emit",
        help="print a /goal prompt from a job, repo, and done-when",
    )
    emit.add_argument(
        "--repo",
        required=True,
        help="GitHub URL or owner/repo, for example glensonis/grok_bot",
    )
    emit.add_argument(
        "--job",
        required=True,
        help="one outcome, not a list of products and not 'edit line N'",
    )
    emit.add_argument(
        "--done-when",
        action="append",
        dest="done_when",
        required=True,
        help="a check a stranger could run; repeat the flag for more checks",
    )
    emit.add_argument(
        "--fence",
        action="append",
        dest="fences",
        default=[],
        help="a constraint; repeat as needed. A secrets fence is always added",
    )
    emit.add_argument(
        "--context",
        action="append",
        dest="context",
        default=[],
        help="a fact the agent needs; repeat as needed",
    )
    emit.add_argument(
        "--good",
        action="append",
        dest="good",
        default=[],
        help="what good looks like (the outcome, not the patch); repeat as needed",
    )

    check = sub.add_parser(
        "check",
        help="exit 0 if a prompt meets the /goal bar, else print why it fails",
    )
    check.add_argument(
        "path",
        help="prompt file, or - to read stdin",
    )
    return parser


def _read_prompt(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "emit":
        try:
            text = emit_prompt(
                job=args.job,
                repo=args.repo,
                done_when=args.done_when,
                fences=args.fences,
                context=args.context,
                good=args.good,
            )
        except GoalError as exc:
            for error in exc.errors:
                print(error, file=sys.stderr)
            return 1
        sys.stdout.write(text)
        return 0

    try:
        text = _read_prompt(args.path)
    except OSError as exc:
        print(f"could not read prompt: {exc}", file=sys.stderr)
        return 1

    errors = check_prompt(text)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("ok")
    return 0
