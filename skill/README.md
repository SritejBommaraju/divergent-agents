# divergent-agents skills

Two drop-in [Claude Code](https://claude.com/claude-code) skills (also work with Codex):

- **`/diverge`** — turn a task from the obvious answer into a genuinely novel one (the divergence loop).
- **`/robust-solve`** — write correct code by cross-checking diverse solutions (differential testing).

Each skill folder is **self-contained** — its helper script is bundled inside it — so installing is just
copying the folder.

## Install (one command)

**Windows** (PowerShell, from the repo root):
```powershell
powershell -ExecutionPolicy Bypass -File skill\install.ps1
```

**macOS / Linux** (from the repo root):
```bash
sh skill/install.sh
```

Add `-Project` (Windows) or `--project` (macOS/Linux) to install into the current project's
`.claude/skills` instead of your user profile.

Then **restart Claude Code** and type `/diverge` or `/robust-solve`.

## Install manually (any OS)

Copy the `divergence` and `robust-solve` folders into your Claude Code skills directory:

| OS | Skills directory |
|---|---|
| **Windows** | `%USERPROFILE%\.claude\skills\` &nbsp;(e.g. `C:\Users\you\.claude\skills\`) |
| **macOS / Linux** | `~/.claude/skills/` |
| **Project scope** (any OS) | `.claude/skills/` inside your repo |

## Requirements

- **Claude Code** (or Codex) — the skills are markdown protocols the agent follows.
- The `/robust-solve` helper (`diff_test.py`) runs under **Python 3.8+** (standard library only — no `pip install`).

## Uninstall

Delete the `divergence` and `robust-solve` folders from your skills directory.
