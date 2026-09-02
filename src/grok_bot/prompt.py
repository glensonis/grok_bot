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

"""Build and check short, falsifiable /goal prompts for cloud coding agents.

The bar is small on purpose. A prompt is usable when it names one job, a
GitHub repo, a done-when a stranger could check, and fences. It is not
usable when it tells the agent to edit line N.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

GITHUB_URL = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)
GITHUB_URL_ANYWHERE = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
)
OWNER_REPO = re.compile(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$")
IN_OWNER_REPO = re.compile(
    r"\bin\s+(?:https://github\.com/)?([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
LINE_EDIT = re.compile(
    r"(?i)\b(?:edit|change|modify|update|fix)\s+line\s+\d+\b"
)
HEADING = re.compile(
    r"^(Context|What good looks like(?:\s*\(not the patch\))?|Done when|Fences)\s*$",
    re.IGNORECASE,
)

MISSING_JOB = "missing job: describe one outcome"
MISSING_REPO = "missing repo: pass a GitHub URL or owner/repo"
BAD_REPO = "repo must be a GitHub URL or owner/repo (no private hosts)"
MISSING_DONE_WHEN = (
    "missing done-when: a stranger must be able to check the result"
)
LINE_EDIT_MSG = "rejecting line-number edits: say the outcome, not 'edit line N'"
MISSING_GOAL = "missing /goal opener"
MISSING_FENCES = "missing fences: constraints belong in a Fences section"
DEFAULT_FENCE = "Do not add secrets, tokens, or private URLs."


class GoalError(ValueError):
    """The task is too incomplete to emit or accept as a /goal prompt."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class GoalSpec:
    job: str
    repo: str
    done_when: tuple[str, ...]
    fences: tuple[str, ...]
    context: tuple[str, ...] = ()
    good: tuple[str, ...] = ()


def normalize_repo(value: str | None) -> str | None:
    """Return a canonical https://github.com/owner/repo URL, or None."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    match = GITHUB_URL.match(text.rstrip("/"))
    if match:
        return f"https://github.com/{match.group(1)}/{match.group(2)}"
    match = OWNER_REPO.match(text)
    if match:
        return f"https://github.com/{match.group(1)}/{match.group(2)}"
    return None


def looks_like_line_edit(text: str) -> bool:
    return bool(LINE_EDIT.search(text))


def _clean_items(items: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    if not items:
        return ()
    cleaned: list[str] = []
    for item in items:
        text = item.strip()
        text = re.sub(r"^\d+\.\s*", "", text)
        text = text.lstrip("-").lstrip("*").strip()
        if text:
            cleaned.append(text)
    return tuple(cleaned)


def build_spec(
    *,
    job: str | None,
    repo: str | None,
    done_when: list[str] | tuple[str, ...] | None,
    fences: list[str] | tuple[str, ...] | None = None,
    context: list[str] | tuple[str, ...] | None = None,
    good: list[str] | tuple[str, ...] | None = None,
) -> GoalSpec:
    errors: list[str] = []
    job_text = (job or "").strip()
    if not job_text:
        errors.append(MISSING_JOB)
    elif looks_like_line_edit(job_text):
        errors.append(LINE_EDIT_MSG)

    raw_repo = (repo or "").strip()
    repo_url = normalize_repo(raw_repo)
    if not raw_repo:
        errors.append(MISSING_REPO)
    elif repo_url is None:
        errors.append(BAD_REPO)

    done = _clean_items(done_when)
    if not done:
        errors.append(MISSING_DONE_WHEN)
    elif any(looks_like_line_edit(item) for item in done):
        errors.append(LINE_EDIT_MSG)

    fence_items = list(_clean_items(fences))
    if DEFAULT_FENCE not in fence_items:
        fence_items.append(DEFAULT_FENCE)

    if errors:
        raise GoalError(errors)

    assert repo_url is not None
    return GoalSpec(
        job=job_text,
        repo=repo_url,
        done_when=done,
        fences=tuple(fence_items),
        context=_clean_items(context),
        good=_clean_items(good),
    )


def _bullet(items: tuple[str, ...], numbered: bool = False) -> str:
    lines: list[str] = []
    for index, item in enumerate(items, start=1):
        if numbered:
            lines.append(f"{index}. {item}")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def render(spec: GoalSpec) -> str:
    job = spec.job.rstrip(".")
    if spec.repo not in job and not IN_OWNER_REPO.search(job):
        job = f"{job} in {spec.repo}"

    parts = [f"/goal\n{job}\n"]
    if spec.context:
        parts.append("Context\n" + _bullet(spec.context) + "\n")
    if spec.good:
        parts.append(
            "What good looks like (not the patch)\n" + _bullet(spec.good) + "\n"
        )
    parts.append("Done when\n" + _bullet(spec.done_when, numbered=True) + "\n")
    parts.append("Fences\n" + _bullet(spec.fences) + "\n")
    return "\n".join(parts).strip() + "\n"


def emit_prompt(
    *,
    job: str | None,
    repo: str | None,
    done_when: list[str] | tuple[str, ...] | None,
    fences: list[str] | tuple[str, ...] | None = None,
    context: list[str] | tuple[str, ...] | None = None,
    good: list[str] | tuple[str, ...] | None = None,
) -> str:
    spec = build_spec(
        job=job,
        repo=repo,
        done_when=done_when,
        fences=fences,
        context=context,
        good=good,
    )
    text = render(spec)
    problems = check_prompt(text)
    if problems:
        raise GoalError(problems)
    return text


def _section_body(lines: list[str], heading: str) -> str:
    capture = False
    body: list[str] = []
    for line in lines:
        match = HEADING.match(line.strip())
        if match:
            if match.group(1).lower().startswith(heading.lower()):
                capture = True
                continue
            if capture:
                break
        elif capture:
            body.append(line)
    return "\n".join(body).strip()


def _job_text(lines: list[str]) -> str:
    started = False
    job_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not started:
            if stripped.lower().startswith("/goal"):
                started = True
                rest = stripped[5:].strip()
                if rest:
                    job_lines.append(rest)
            continue
        if HEADING.match(stripped):
            break
        job_lines.append(line)
    return "\n".join(job_lines).strip()


def check_prompt(text: str) -> list[str]:
    """Return problems that would make this prompt unusable. Empty means ok."""
    errors: list[str] = []
    if not text or not text.strip():
        return [MISSING_GOAL, MISSING_JOB, MISSING_REPO, MISSING_DONE_WHEN]

    lines = text.replace("\r\n", "\n").split("\n")
    first = next((line.strip() for line in lines if line.strip()), "")
    if not first.lower().startswith("/goal"):
        errors.append(MISSING_GOAL)

    job = _job_text(lines)
    if not job:
        errors.append(MISSING_JOB)
    elif looks_like_line_edit(job):
        errors.append(LINE_EDIT_MSG)

    repo_found = GITHUB_URL_ANYWHERE.search(text) or IN_OWNER_REPO.search(text)
    if not repo_found:
        errors.append(MISSING_REPO)

    done_body = _section_body(lines, "Done when")
    if not done_body:
        errors.append(MISSING_DONE_WHEN)
    elif looks_like_line_edit(done_body):
        errors.append(LINE_EDIT_MSG)

    fences_body = _section_body(lines, "Fences")
    if not fences_body:
        errors.append(MISSING_FENCES)

    return errors
