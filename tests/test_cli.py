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

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(SRC), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    return subprocess.run(
        [sys.executable, "-m", "grok_bot", *args],
        capture_output=True,
        text=True,
        env=env,
        input=stdin,
        cwd=ROOT,
    )


def test_readme_identifies_loops_and_documents_emit():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# grok_bot\nGrok Bot repo used by loops Grok Bot\n")
    assert "python3 -m grok_bot emit \\" in readme
    assert "--repo https://github.com/glensonis/grok_bot" in readme
    assert "--job " in readme
    assert "--done-when " in readme
    assert "python3 -m pytest" in readme


def test_cli_help_names_loops_and_flags():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "loops Grok Bot" in result.stdout
    assert "python3 -m grok_bot" in result.stdout
    help_emit = run_cli("emit", "--help")
    assert help_emit.returncode == 0
    assert "--repo" in help_emit.stdout
    assert "--job" in help_emit.stdout
    assert "--done-when" in help_emit.stdout


def test_cli_emit_happy_path():
    result = run_cli(
        "emit",
        "--repo",
        "https://github.com/glensonis/grok_bot",
        "--job",
        "Document install and one emit command",
        "--done-when",
        "README contains a copy-paste emit command a stranger can run",
        "--fence",
        "Keep LICENSE as GNU GPL v3",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("/goal\n")
    assert "https://github.com/glensonis/grok_bot" in result.stdout
    assert "Done when" in result.stdout
    assert "Fences" in result.stdout


def test_cli_emit_rejects_missing_repo_flag():
    result = run_cli(
        "emit",
        "--job",
        "Document install",
        "--done-when",
        "README names the command",
    )
    assert result.returncode != 0
    assert "--repo" in result.stderr


def test_cli_check_accepts_complete_fixture():
    result = run_cli("check", str(FIXTURES / "complete.goal.md"))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"


def test_cli_check_rejects_missing_done_when():
    result = run_cli("check", str(FIXTURES / "missing_done_when.goal.md"))
    assert result.returncode == 1
    assert "missing done-when" in result.stderr


def test_cli_check_rejects_missing_repo():
    result = run_cli("check", str(FIXTURES / "missing_repo.goal.md"))
    assert result.returncode == 1
    assert "missing repo" in result.stderr


def test_cli_emit_piped_to_check():
    emitted = run_cli(
        "emit",
        "--repo",
        "glensonis/grok_bot",
        "--job",
        "Print a /goal prompt a cloud agent can run",
        "--done-when",
        "python3 -m grok_bot check accepts the printed prompt",
    )
    assert emitted.returncode == 0, emitted.stderr
    checked = run_cli("check", "-", stdin=emitted.stdout)
    assert checked.returncode == 0, checked.stderr
    assert checked.stdout.strip() == "ok"
