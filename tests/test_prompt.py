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

from grok_bot.prompt import (
    DEFAULT_FENCE,
    GoalError,
    check_prompt,
    emit_prompt,
    normalize_repo,
)
import pytest


COMPLETE_PROMPT = """/goal
Add a check command in https://github.com/glensonis/grok_bot

Context
- loops sits above coding agents and needs a falsifiable prompt.

What good looks like (not the patch)
- A stranger can tell a prompt was rejected for a missing repo.

Done when
1. pytest fails a fixture prompt that has a job and no GitHub repo.
2. README still names this as the loops Grok Bot repo.

Fences
- Do not replace LICENSE.
- Do not add secrets, tokens, or private URLs.
"""


def test_normalize_repo_accepts_url_and_owner_name():
    assert (
        normalize_repo("https://github.com/glensonis/grok_bot")
        == "https://github.com/glensonis/grok_bot"
    )
    assert (
        normalize_repo("glensonis/grok_bot")
        == "https://github.com/glensonis/grok_bot"
    )
    assert normalize_repo("https://evil.example/x/y") is None
    assert normalize_repo("") is None


def test_emit_prompt_happy_path():
    text = emit_prompt(
        job="Add a check command",
        repo="glensonis/grok_bot",
        done_when=[
            "pytest fails a fixture prompt that has a job and no GitHub repo"
        ],
        fences=["Do not replace LICENSE"],
        context=["loops sits above coding agents"],
        good=["A stranger can tell why a prompt was rejected"],
    )
    assert text.startswith("/goal\n")
    assert "https://github.com/glensonis/grok_bot" in text
    assert "Done when" in text
    assert "pytest fails a fixture prompt" in text
    assert "Fences" in text
    assert "Do not replace LICENSE" in text
    assert DEFAULT_FENCE in text
    assert check_prompt(text) == []


def test_emit_prompt_rejects_missing_repo():
    with pytest.raises(GoalError) as caught:
        emit_prompt(
            job="Add tests",
            repo="",
            done_when=["pytest passes"],
        )
    assert any("missing repo" in error for error in caught.value.errors)


def test_emit_prompt_rejects_missing_done_when():
    with pytest.raises(GoalError) as caught:
        emit_prompt(
            job="Add tests",
            repo="glensonis/grok_bot",
            done_when=[],
        )
    assert any("missing done-when" in error for error in caught.value.errors)


def test_emit_prompt_rejects_line_number_edits():
    with pytest.raises(GoalError) as caught:
        emit_prompt(
            job="edit line 12 of README",
            repo="glensonis/grok_bot",
            done_when=["README is shorter"],
        )
    assert any("line-number" in error for error in caught.value.errors)


def test_check_prompt_accepts_complete_prompt():
    assert check_prompt(COMPLETE_PROMPT) == []


def test_check_prompt_rejects_missing_repo():
    text = """/goal
Add a check command

Done when
1. pytest passes.

Fences
- Do not relicense LICENSE.
"""
    errors = check_prompt(text)
    assert any("missing repo" in error for error in errors)


def test_check_prompt_rejects_missing_done_when():
    text = """/goal
Add a check command in https://github.com/glensonis/grok_bot

Fences
- Do not relicense LICENSE.
"""
    errors = check_prompt(text)
    assert any("missing done-when" in error for error in errors)
