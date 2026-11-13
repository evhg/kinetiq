#!/opt/homebrew/bin/bash
# one-racket-k02export.sh (2026-11-14, the Mac render node): export K02 (its four stills and four swivels, desktop and
# phone) in the one-racket canon to mac/exports and post one EXPORTED line. Same recipe as the full-weave K02 export
# (2984c3e9): desktop sets rebuilt whole from their region masters in the private masters repo (render/seq_rebuild.py,
# one sequence at a time for disk), phone sets from the local --phone frames; desktop AVIF 58, Command phone AVIF 46
# keeping 30 of 60 frames, Pace phone AVIF 50; WebP 84. Frame 0 checked against its still at 1920 (mean < 1 luma).
#   render/one-racket-k02export.sh [variant ...]    variants: command pace nogrip-command nogrip-pace (default all)
set -euo pipefail
cd "$(dirname "$0")"
KIT=$PWD
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export PATH=/opt/homebrew/opt/node@22/bin:$PATH
PY=$KQ_RENDER_OUT/bpyenv/bin/python
W=${KQ_EXPORTS:-$HOME/kinetiq-render/kinetiq-exports}
F=$KQ_RENDER_OUT/out/final
S4=$KQ_RENDER_OUT/out/seq4
T=$KQ_RENDER_OUT/tmp-k02exp
L=$KQ_RENDER_OUT/logs/one-racket.log
REPO=${KQ_MASTERS_URL:-https://github.com/evhg/kinetiq-masters}
log() { echo "$(date -u +%FT%TZ) K02EXP $*" | tee -a "$L"; }
VS=("$@"); [ ${#VS[@]} -gt 0 ] || VS=(command pace nogrip-command nogrip-pace)
declare -A STILL=([command]=K02-edge-line [pace]=K02-edge-line-pace [nogrip-command]=K02-edge-line-nogrip [nogrip-pace]=K02-edge-line-nogrip-pace)
declare -A SID=([command]=K02 [pace]=K02-pace [nogrip-command]=K02-nogrip [nogrip-pace]=K02-nogrip-pace)

cd "$W"
[ "$(git rev-parse --abbrev-ref HEAD)" = mac/exports ] || { log "not on mac/exports"; exit 1; }
[ -z "$(git status --porcelain)" ] || { log "exports worktree not clean"; exit 1; }
git fetch -q origin
git rebase -q origin/wip/owner-update
rm -rf "$T"; mkdir -p "$T/seq" "$T/m"
summary=()
for v in "${VS[@]}"; do
  st=$F/v5k/${STILL[$v]}.png
  [ "$st" -nt "$KQ_RENDER_OUT/logs/queue-nov3.done.pre-oneracket" ] || { log "$v: still not a one-racket render"; exit 1; }
  ln -sfn "$st" "$T/m/${SID[$v]}.png"
  d=K02-swivel-$v-desktop p=K02-swivel-$v-phone
  # the desktop region masters from the private masters repo (sparse, blobless), rebuilt whole
  rm -rf "$T/mr"
  git clone -q --filter=blob:none --no-checkout --depth 1 "$REPO" "$T/mr"
  git -C "$T/mr" sparse-checkout set --no-cone "/sequences/$d/" >/dev/null
  git -C "$T/mr" checkout -q main
  [ -f "$T/mr/sequences/$d/crop.json" ] || { log "$d: no region masters"; exit 1; }
  for k in 0 1 2 3; do $PY "$W/render/seq_rebuild.py" "$T/mr/sequences/$d" "$T/seq/$d" $k 4 > "$T/rb-$k.log" 2>&1 & done; wait
  rm -rf "$T/mr"
  nd=$(ls "$T/seq/$d"/f???.png | wc -l | tr -d ' ')
  np=$(ls "$S4/$p"/f???.png | wc -l | tr -d ' ')
  rm -rf "$T/seq/$p"; cp -Rl "$S4/$p" "$T/seq/$p"   # a real folder: sequence.mjs skips a symlinked one
  chk=$($PY - "$T/seq/$d/f000.png" "$st" <<'EOF'
import sys, numpy as np
from PIL import Image
w = 1920
def L(p):
    im = Image.open(p).convert("RGB"); h = round(im.size[1] * w / im.size[0])
    return np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32) @ np.array([.2126, .7152, .0722])
d = np.abs(L(sys.argv[1]) - L(sys.argv[2]))
print("%.2f %.2f" % (d.mean(), 100 * (d > 6).mean()))
EOF
)
  log "$v: desktop $nd frames rebuilt, phone $np; frame 0 vs still: mean ${chk% *} luma, ${chk#* } % over 6"
  awk -v m="${chk% *}" 'BEGIN{exit !(m < 1.0)}' || { log "$v: frame 0 does not match its still"; exit 1; }
  node scripts/sequence.mjs "$T/seq" "$d" --formats=avif,webp --avif-quality=58 >> "$T/seq.log" 2>&1
  if [[ $v == *command ]]; then
    node scripts/sequence.mjs "$T/seq" "$p" --formats=avif,webp --avif-quality=46 --keep=30 >> "$T/seq.log" 2>&1
  else
    node scripts/sequence.mjs "$T/seq" "$p" --formats=avif,webp --avif-quality=50 >> "$T/seq.log" 2>&1
  fi
  rm -rf "$T/seq/$d" "$T/seq/$p"
  grep -q "^$d avif" "$T/seq.log" && grep -q "^$p avif" "$T/seq.log" || { log "$v: sequence.mjs did not export both sets"; exit 1; }
  summary+=("$v: frame 0 mean ${chk% *} luma, ${chk#* } % over 6")
done
# drop old hash files: keep only the hashes the manifest names
python3 - <<'EOF'
import json, os, re
m = json.load(open("src/content/sequences.generated.json"))
for name, e in m.items():
    if not name.startswith("K02-swivel-"):
        continue
    d = os.path.join("public/stills/seq", name)
    if not os.path.isdir(d):
        continue
    keep = {f["hash"] for f in e.get("formats", {}).values()}
    for f in os.listdir(d):
        h = re.search(r"\.([0-9a-f]{10})\.(avif|webp)$", f)
        if h and h.group(1) not in keep:
            os.remove(os.path.join(d, f))
EOF
node scripts/stills.mjs "$T/m" $(for v in "${VS[@]}"; do echo "${SID[$v]}"; done) >> "$T/stills.log" 2>&1
git add -A public/stills src/content/stills.generated.json src/content/sequences.generated.json
bad=$(git diff --cached --name-only | grep -vE '^(public/stills/|src/content/(stills|sequences)\.generated\.json$)' || true)
[ -z "$bad" ] || { log "REFUSED: paths outside the allowed: $bad"; exit 1; }
git -c user.name=Claude -c user.email=noreply@anthropic.com commit -q -m "K02 in the one-racket canon (STATUS-mac one-racket:K02): its stills and swivels, grip and Naked, both feels

The ring fill reaches the whole racket (cloud review 2026-11-13T18:59Z). Desktop swivels rebuilt from their region
masters (render/seq_rebuild.py), AVIF 58; phone from the --phone frames, Command AVIF 46 keeping 30 of 60, Pace AVIF 50;
WebP 84. $(IFS=';'; echo "${summary[*]}").

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
chg=$(git diff --name-only --diff-filter=AM origin/wip/owner-update...HEAD)
all=$(git diff --name-only origin/wip/owner-update...HEAD)
out=$(printf '%s\n' "$all" | grep -vE '^(public/stills/|src/content/(stills|sequences)\.generated\.json$)' || true)
mst=$(printf '%s\n' "$all" | grep -iE '\.(png|exr)$' || true)
big=$(for f in $chg; do [ -f "$f" ] && [ "$(stat -f %z "$f")" -gt 5242880 ] && echo "$f"; done || true)
if [ -n "$out$mst$big" ]; then log "REFUSED to push: outside=[$out] masters=[$mst] over5MB=[$big]"; exit 1; fi
git push -q --force-with-lease origin HEAD:refs/heads/mac/exports
sha=$(git rev-parse --short HEAD)
rm -rf "$T"
ids=$(for v in "${VS[@]}"; do printf '%s,K02-swivel-%s-desktop,K02-swivel-%s-phone,' "${SID[$v]}" "$v" "$v"; done | sed 's/,$//')
cd "$KIT" && ./status_push.sh "$(date -u +%Y-%m-%dT%H:%M:%SZ) EXPORTED one-racket:K02 mac/exports@$sha $ids (stills + swivels; the ring fill reaches the whole racket; $(IFS=';'; echo "${summary[*]}")) M3Max-METAL" >/dev/null
log "EXPORTED K02 mac/exports@$sha"
