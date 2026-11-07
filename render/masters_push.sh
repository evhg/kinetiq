#!/bin/bash
# masters_push.sh (2026-11-03): copy files into the PRIVATE masters repo (evhg/kinetiq-masters) and push them, without
# keeping a full checkout on this disk: each call makes a throwaway blobless, sparse, depth-1 clone, adds the files under
# <dir>/, commits, pushes and deletes the clone (the masters never stay twice on disk). Retries the push 3 times
# (rebasing onto a newer main). Never use this for the public kinetiq repo.
#   render/masters_push.sh <repo dir, e.g. stills/K01> "<commit message>" <file> [<file> ...]
set -u
# one masters/STATUS push at a time on this Mac (2026-11-07: the K09 batch and the full-weave pass pushed together and
# the loser's retries kept pushing its stale commit: "cannot lock ref")
if [ -z "${KQ_MLOCKED:-}" ] && command -v flock >/dev/null; then
  exec env KQ_MLOCKED=1 flock "${KQ_MASTERS_LOCK:-$HOME/kinetiq-render/masters.lock}" "$0" "$@"
fi
DIR=$1; MSG=$2; shift 2
REPO=${KQ_MASTERS_URL:-https://github.com/evhg/kinetiq-masters}
TMP=${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}/tmp-masters-$$
for t in 1 2 3 4 5 6; do   # retry the clone (a network blip must not drop a master)
  rm -rf "$TMP"
  git clone -q --filter=blob:none --no-checkout --depth 1 "$REPO" "$TMP" && break
  [ $t -eq 6 ] && { echo "masters: CLONE FAILED $DIR"; exit 1; }
  sleep $((t * 30))
done
cd "$TMP" || exit 1
git sparse-checkout set --no-cone /README.md >/dev/null
git checkout -q main || exit 1
mkdir -p "$DIR"
for f in "$@"; do cp -f "$f" "$DIR/" || { echo "missing $f"; exit 1; }; done
git add --sparse "$DIR" || exit 1
if git diff --cached --quiet; then echo "masters: nothing new for $DIR"; cd /; rm -rf "$TMP"; exit 0; fi
git commit -q -m "$MSG" || exit 1
ok=0
for t in 1 2 3; do
  if git push -q origin main; then ok=1; break; fi
  # rebuild the commit on the newest main (a shallow clone cannot rebase): reset the index to it, add the files again
  git fetch -q --depth 1 origin main && git reset -q --mixed FETCH_HEAD && git add --sparse "$DIR" \
    && { git diff --cached --quiet || git commit -q -m "$MSG"; }
  sleep $((t * 20))
done
cd / && rm -rf "$TMP"
[ $ok -eq 1 ] && echo "masters: pushed $DIR ($#)" || { echo "masters: PUSH FAILED $DIR"; exit 1; }
