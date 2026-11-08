#!/usr/bin/env bash
# mac_export.sh (2026-11-08, the Mac render node, cloud REQUEST mac-exports): export still ids from their masters on
# branch mac/exports (worktree $KQ_EXPORTS, default ~/kinetiq-render/kinetiq-exports) and push it.
#   render/mac_export.sh "<commit subject>" <id>=<master png> [<id>=<master png> ...]
# Rebases mac/exports onto the latest origin/wip/owner-update first (the cloud owns stills.json, code and docs), runs
# scripts/stills.mjs on a folder of <id>.png links (each id wholly re-exported), commits ONLY public/stills/** and
# src/content/stills.generated.json, refuses to push on any *.png/*.exr, any file over 5 MB or any other path, pushes
# mac/exports (never main or wip/owner-update) and prints "EXPORTED-SHA <sha>".
set -euo pipefail
MSG=$1; shift
W=${KQ_EXPORTS:-$HOME/kinetiq-render/kinetiq-exports}
export PATH=/opt/homebrew/opt/node@22/bin:$PATH
cd "$W"
[ "$(git rev-parse --abbrev-ref HEAD)" = mac/exports ] || { echo "not on mac/exports"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "worktree not clean"; git status --short | head; exit 1; }
git fetch -q origin
git rebase -q origin/wip/owner-update
M=$(mktemp -d "${TMPDIR:-/tmp}/kq-masters.XXXXXX")
ids=()
for kv in "$@"; do
  id=${kv%%=*}; f=${kv#*=}
  [ -f "$f" ] || { echo "no master $f"; exit 1; }
  ln -s "$f" "$M/$id.png"; ids+=("$id")
done
node scripts/stills.mjs "$M" "${ids[@]}"
rm -rf "$M"
git add -A public/stills src/content/stills.generated.json
bad=$(git diff --cached --name-only | grep -vE '^(public/stills/|src/content/stills\.generated\.json$)' || true)
[ -z "$bad" ] || { echo "REFUSED: paths outside the two allowed: $bad"; exit 1; }
git -c user.name=Claude -c user.email=noreply@anthropic.com commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
# the check before every push: everything on mac/exports past origin/wip/owner-update
chg=$(git diff --name-only --diff-filter=AM origin/wip/owner-update...HEAD)
all=$(git diff --name-only origin/wip/owner-update...HEAD)
out=$(printf '%s\n' "$all" | grep -vE '^(public/stills/|src/content/stills\.generated\.json$)' || true)
mst=$(printf '%s\n' "$all" | grep -iE '\.(png|exr)$' || true)
big=$(for f in $chg; do [ "$(stat -f %z "$f")" -gt 5242880 ] && echo "$f"; done || true)
if [ -n "$out$mst$big" ]; then echo "REFUSED to push: outside=[$out] masters=[$mst] over5MB=[$big]"; exit 1; fi
git push -q --force-with-lease origin HEAD:refs/heads/mac/exports
echo "EXPORTED-SHA $(git rev-parse --short HEAD) files $(printf '%s\n' "$all" | grep -c .)"
