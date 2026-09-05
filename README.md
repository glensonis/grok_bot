# grok_bot
Grok Bot repo used by loops Grok Bot

loops sits above coding agents. This repo is the helper loops runs locally: take one task, refuse it if a stranger could not check the result, and print a short `/goal` prompt for a cloud coding agent.

It is a CLI plus a prompt template. It is not a chat app and not a framework.

## Install

Python 3.11 or newer.

```bash
python3 -m pip install -e ".[dev]"
```

## Emit a /goal prompt

```bash
python3 -m grok_bot emit \
  --repo https://github.com/glensonis/grok_bot \
  --job "Document install and one emit command" \
  --done-when "README contains a copy-paste emit command a stranger can run" \
  --fence "Keep LICENSE as GNU GPL v3"
```

That prints a prompt you can paste into a cloud agent. `--repo` is a GitHub URL or `owner/repo`. Repeat `--done-when`, `--fence`, `--context`, and `--good` as needed. `python3 -m grok_bot emit --help` lists the flags.

## Check a prompt

```bash
python3 -m grok_bot check tests/fixtures/complete.goal.md
```

`check` exits 0 when the text names one job, a GitHub repo, a stranger-checkable done-when, and fences. It exits 1 if the repo or done-when is missing, or if the job says to edit a line number. `-` reads stdin. Pass a filled prompt, not `prompts/goal.md` (that file still has placeholders).

## Template

`prompts/goal.md` is the reusable shape. `skills/goal/SKILL.md` is the same bar for loops.

## Tests

```bash
python3 -m pytest
```

## License

GNU GPL v3. See `LICENSE`. New source files use the same license.
