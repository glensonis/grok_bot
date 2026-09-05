---
name: goal
description: >
  Gather one task and emit a short, falsifiable /goal prompt for a cloud
  coding agent. Use when loops needs a cloud-agent prompt, or when checking
  that a prompt names a repo and a stranger-checkable done-when.
---

<!--
  SPDX-License-Identifier: GPL-3.0-or-later
  Copyright (C) 2026 Glenson Dsouza
-->

# /goal for loops

loops sits above coding agents. This skill is the first local helper: turn a task into a prompt a stranger could grade, or refuse the task until it is that sharp.

Do not invent other products. Do not turn this into a chat app. The helper is a CLI plus this prompt shape.

## The bar

A usable `/goal` prompt has:

1. **One job.** A single outcome, with the GitHub repo named in the first paragraph.
2. **Done when** a stranger could check, without trusting the agent's summary. Commands, files, and visible behavior. Not "it works".
3. **Fences.** Constraints as a list of things not to do.
4. **No line edits.** Never "edit line 12". Say the outcome.

`prompts/goal.md` is the fill-in template.

## Emit

If the human gave a repo, a job, and at least one done-when, run:

```bash
python3 -m grok_bot emit \
  --repo {repo} \
  --job "{one job}" \
  --done-when "{a check a stranger could run}" \
  --fence "{constraint}"
```

Print the stdout prompt. That is the artifact to hand to a cloud coding agent.

## Refuse until the bar is met

If repo or done-when is missing, do not guess. Ask for the missing piece, or run emit and show the CLI error. Same if the job says to edit a line number.

To grade an existing prompt:

```bash
python3 -m grok_bot check path/to/prompt.md
```

Exit 0 is usable. Exit 1 prints the gaps. Fix the prompt; do not weaken the checker.
