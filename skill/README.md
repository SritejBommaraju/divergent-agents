# divergent-agents skills

Two drop-in [Claude Code](https://claude.com/claude-code) skills (also work with Codex):

- **`/diverge`** — turn a task from the obvious answer into a genuinely novel one (the divergence loop).
- **`/robust-solve`** — write correct code by cross-checking diverse solutions (differential testing).

Each skill folder is **self-contained** — its helper script is bundled inside it — so installing is just
copying the folder.

## Download without cloning (one line)

No repo on disk needed — pull just the two skill folders straight into your Claude Code skills directory.

> The repo is **public** — use **A** (no login). **B** is only for a private fork.

**A · Public repo** — anyone can run this (no login, no clone):

```bash
# macOS / Linux
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/SritejBommaraju/divergent-agents/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills divergent-agents-main/skill/divergence divergent-agents-main/skill/robust-solve
```
```powershell
# Windows (PowerShell)
$d="$env:USERPROFILE\.claude\skills"; mkdir $d -Force|Out-Null; curl.exe -fsSL -o "$env:TEMP\da.tgz" https://github.com/SritejBommaraju/divergent-agents/archive/refs/heads/main.tar.gz; tar -xzf "$env:TEMP\da.tgz" -C $d --strip-components=2 divergent-agents-main/skill/divergence divergent-agents-main/skill/robust-solve
```
To make it public: `gh repo edit SritejBommaraju/divergent-agents --visibility public --accept-visibility-change-consequences`

**B · While the repo is PRIVATE** — needs [`gh`](https://cli.github.com) logged in (works for you + anyone you've granted access):

```bash
# macOS / Linux
T=$(mktemp -d); gh api repos/SritejBommaraju/divergent-agents/tarball/main | tar -xz -C "$T"; mkdir -p ~/.claude/skills; cp -R "$T"/*/skill/divergence "$T"/*/skill/robust-solve ~/.claude/skills/; rm -rf "$T"
```
```powershell
# Windows (PowerShell)
$d="$env:USERPROFILE\.claude\skills"; mkdir $d -Force|Out-Null; curl.exe -fsSL -H "Authorization: Bearer $(gh auth token)" -o "$env:TEMP\da.tgz" https://api.github.com/repos/SritejBommaraju/divergent-agents/tarball/main; $x="$env:TEMP\da"; Remove-Item $x -Recurse -Force -EA 0; tar -xzf "$env:TEMP\da.tgz" -C ($env:TEMP) ; Get-ChildItem "$env:TEMP\SritejBommaraju-divergent-agents-*" -Directory | Select -First 1 | % { Copy-Item -Recurse -Force "$($_.FullName)\skill\divergence","$($_.FullName)\skill\robust-solve" $d }
```

Then **restart Claude Code** and type `/diverge` or `/robust-solve`.

> **Requirements for the one-liners:** `curl` + `tar`, which are built into **macOS**, **Linux**, and
> **Windows 10 (build 1803, April 2018) and Windows 11**. Older Windows (7/8 or pre-1803) doesn't ship them
> — use a fallback instead:
>
> ```bash
> git clone https://github.com/SritejBommaraju/divergent-agents && cd divergent-agents
> #   then:  powershell -ExecutionPolicy Bypass -File skill\install.ps1   (Windows)
> #     or:  sh skill/install.sh                                          (macOS / Linux)
> ```
> ```bash
> npx degit SritejBommaraju/divergent-agents/skill ~/.claude/skills   # no git/tar needed (needs Node)
> ```

## Install from a local clone (one command)

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
