#!/bin/bash
# export_push.sh (2026-11-03): export finished masters to the site and push them to wip/owner-update from a worktree of
# its own (/home/user/wt-render, detached), so the queue never touches the shared checkout's working tree.
#   render/export_push.sh stills "<commit subject>" <still id> [...]     # scripts/stills.mjs via link-masters.sh
#   render/export_push.sh seq "<commit subject>" <seq dir> <name> [...]  # scripts/sequence.mjs (both formats)
# Retries the push 4 times, rebasing on the branch. Exit 0 = pushed (or nothing changed).
set -u
KIND=$1; MSG=$2; shift 2
BR=${KQ_BRANCH:-wip/owner-update}
MAIN=${KQ_MAIN:-$(cd "$(dirname "$0")/.." && pwd)}   # the shared checkout (was /home/user/kinetiq)
WT=${KQ_EXPORT_WT:-/home/user/wt-render}
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}
cd "$MAIN" || exit 1
git fetch -q origin "$BR" || exit 1
if [ ! -d "$WT/.git" ] && [ ! -f "$WT/.git" ]; then git worktree add -q --detach "$WT" "origin/$BR" || exit 1; fi
cd "$WT" || exit 1
git checkout -q --detach "origin/$BR" && git reset -q --hard "origin/$BR" || exit 1
[ -e node_modules ] || ln -s "$MAIN/node_modules" node_modules
"$MAIN/render/link-masters.sh" > /dev/null
if [ "$KIND" = stills ]; then
  node scripts/stills.mjs "$KQ_RENDER_OUT/masters" "$@" || exit 1
else
  SD=$1; shift
  for n in "$@"; do
    case "$n" in *-phone) Q="--avif-quality=50" ;; *) Q="" ;; esac
    case "$n" in K02-swivel*command-phone) Q="$Q --keep=45" ;; esac   # the phone load budget (sequence.mjs --keep)
    node scripts/sequence.mjs "$SD" "$n" --formats=avif,webp $Q || exit 1
  done
fi
git add -A public/stills src/content/stills.generated.json src/content/sequences.generated.json
if git diff --cached --quiet; then echo "export: nothing changed"; exit 0; fi
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hnwyPR7ur5HWbLjdnZH4i" || exit 1
for t in 1 2 3 4; do
  if git push -q origin "HEAD:$BR"; then echo "export: pushed $(git rev-parse --short HEAD) $MSG"; exit 0; fi
  git fetch -q origin "$BR" && git rebase -q "origin/$BR" || { git rebase --abort; echo "export: REBASE CONFLICT"; exit 1; }
  sleep 5
done
echo "export: PUSH FAILED"; exit 1
