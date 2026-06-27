#!/usr/bin/env bash
# Install divergent-agents skills for Claude Code on macOS / Linux.
#
#   sh skill/install.sh             # user-wide  (~/.claude/skills)
#   sh skill/install.sh --project   # this project only  (./.claude/skills)
#
set -e
here="$(cd "$(dirname "$0")" && pwd)"
if [ "$1" = "--project" ]; then dest="$(pwd)/.claude/skills"; else dest="$HOME/.claude/skills"; fi
mkdir -p "$dest"
for s in divergence robust-solve; do
  rm -rf "$dest/$s"
  cp -R "$here/$s" "$dest/$s"
  echo "  installed  $s  ->  $dest/$s"
done
echo ""
echo "Done. Restart Claude Code, then type  /diverge  or  /robust-solve"
