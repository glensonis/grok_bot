<!--
  SPDX-License-Identifier: GPL-3.0-or-later
  Copyright (C) 2026 Glenson Dsouza
-->

# /goal

Reusable prompt shape for a cloud coding agent. loops fills this in; `python3 -m grok_bot emit` prints a filled copy.

One job. Name the repo. Write a done-when a stranger could check. Put constraints in Fences. Do not say "edit line N".

```text
/goal
{one job} in {https://github.com/owner/repo}

Context
- {facts the agent needs, not the patch}

What good looks like (not the patch)
- {what a stranger would see or be able to run}

Done when
1. {a check a stranger could run}

Fences
- {what the agent must not do}
```

`python3 -m grok_bot check path/to/filled-prompt.md` rejects a draft that is missing the repo, missing done-when, or that micromanages a line number.
