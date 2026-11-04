#!/usr/bin/env bash
# status_push.sh (2026-11-04, the Mac render node, notes/mac-handoff.md): append one line to STATUS-mac.md at the root
# of the PRIVATE masters repo and push it, so the cloud session (which polls that file) knows what is finished.
#   render/status_push.sh "<UTC time> <item> <ids/paths in the masters repo> <render time> <device> <notes>"
# Each try starts from a fresh throwaway blobless sparse clone of main (as masters_push.sh), so a line the cloud
# pushed meanwhile (REQUEST ...) is never overwritten; 5 tries.
set -u
LINE=$1
REPO=${KQ_MASTERS_URL:-https://github.com/evhg/kinetiq-masters}
for t in 1 2 3 4 5; do
  TMP=${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}/tmp-status-$$
  rm -rf "$TMP"
  if git clone -q --filter=blob:none --no-checkout --depth 1 "$REPO" "$TMP" && cd "$TMP" \
    && git sparse-checkout set --no-cone /STATUS-mac.md >/dev/null && git checkout -q main; then
    [ -f STATUS-mac.md ] || printf '# Mac render node status (render/notes/mac-handoff.md)\n# <UTC time> <item> <ids/paths in this repo> <render time> <device> <notes>\n' > STATUS-mac.md
    printf '%s\n' "$LINE" >> STATUS-mac.md
    git add --sparse STATUS-mac.md && git commit -q -m "STATUS-mac: ${LINE:0:120}" && git push -q origin main \
      && { cd /; rm -rf "$TMP"; echo "status: pushed"; exit 0; }
  fi
  cd /; rm -rf "$TMP"; sleep $((t * 5))
done
echo "status: PUSH FAILED"; exit 1
