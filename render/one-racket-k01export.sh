#!/opt/homebrew/bin/bash
# one-racket-k01export.sh (2026-11-14, the Mac render node): export K01 (the hero: beam base/full/finale, phone portrait
# base/full, and the eight swivels, desktop and phone) in the one-racket canon to mac/exports and post one EXPORTED line.
# Same recipe as the full-weave K01 export (bc64c9e5) and one-racket-k02export.sh: both swivel sets of a variant rebuilt
# whole from their region masters in the private masters repo (render/seq_rebuild.py), desktop AVIF 58, phone AVIF 50,
# all 36 frames; WebP 84. Frame 0 checked against its -full still at 1920 (desktop) and 1170 (phone): mean < 1 luma.
#   render/one-racket-k01export.sh [variant ...]    variants: command pace nogrip-command nogrip-pace (default all)
# one export at a time in the exports worktree (K02, K07 and K01 exports can overlap)
if [ -z "${KQ_XLOCKED:-}" ]; then exec env KQ_XLOCKED=1 flock "$HOME/kinetiq-render/export.lock" "$(cd "$(dirname "$0")" && pwd)/$(basename "$0")" "$@"; fi
set -euo pipefail
cd "$(dirname "$0")"
KIT=$PWD
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export PATH=/opt/homebrew/opt/node@22/bin:$PATH
PY=$KQ_RENDER_OUT/bpyenv/bin/python
W=${KQ_EXPORTS:-$HOME/kinetiq-render/kinetiq-exports}
F=$KQ_RENDER_OUT/out/final
T=$KQ_RENDER_OUT/tmp-k01exp
L=$KQ_RENDER_OUT/logs/one-racket.log
REPO=${KQ_MASTERS_URL:-https://github.com/evhg/kinetiq-masters}
log() { echo "$(date -u +%FT%TZ) K01EXP $*" | tee -a "$L"; }
VS=("$@"); [ ${#VS[@]} -gt 0 ] || VS=(command pace nogrip-command nogrip-pace)
declare -A TAG=([command]= [pace]=-pace [nogrip-command]=-nogrip [nogrip-pace]=-nogrip-pace)
# site ids (link-masters.sh): beam base/full/finale, phone base/full
declare -A IDS=(
  [command]="K01-base K01-full K01-finale K01-hero-base-phone K01-hero-full-phone"
  [pace]="K01-base-pace K01-full-pace K01-finale-pace K01-hero-base-phone-pace K01-hero-full-phone-pace"
  [nogrip-command]="K01-nogrip-base K01-nogrip-full K01-nogrip-finale K01-nogrip-hero-base-phone K01-nogrip-hero-full-phone"
  [nogrip-pace]="K01-nogrip-base-pace K01-nogrip-full-pace K01-nogrip-finale-pace K01-nogrip-hero-base-phone-pace K01-nogrip-hero-full-phone-pace")

cd "$W"
[ "$(git rev-parse --abbrev-ref HEAD)" = mac/exports ] || { log "not on mac/exports"; exit 1; }
[ -z "$(git status --porcelain)" ] || { log "exports worktree not clean"; exit 1; }
git fetch -q origin
git rebase -q origin/wip/owner-update
rm -rf "$T"; mkdir -p "$T/seq" "$T/m"
summary=() allids=()
f0chk() {   # f0chk <frame> <still> <width>: "mean pct"
  $PY - "$1" "$2" "$3" <<'EOF'
import sys, numpy as np
from PIL import Image
w = int(sys.argv[3])
def L(p):
    im = Image.open(p).convert("RGB"); h = round(im.size[1] * w / im.size[0])
    return np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32) @ np.array([.2126, .7152, .0722])
d = np.abs(L(sys.argv[1]) - L(sys.argv[2]))
print("%.2f %.2f" % (d.mean(), 100 * (d > 6).mean()))
EOF
}
for v in "${VS[@]}"; do
  t=${TAG[$v]}
  beam=$F/K01-hero-beam$t-v5k phone=$F/K01-hero-frame-phone$t-v5k
  srcs=("$beam-base.png" "$beam-full.png" "$beam-finale.png" "$phone-base.png" "$phone-full.png")
  read -ra ids <<< "${IDS[$v]}"
  for i in 0 1 2 3 4; do
    [ "${srcs[$i]}" -nt "$KQ_RENDER_OUT/logs/queue-nov3.done.pre-oneracket" ] || { log "$v: ${srcs[$i]##*/} not a one-racket render"; exit 1; }
    ln -sfn "${srcs[$i]}" "$T/m/${ids[$i]}.png"
  done
  allids+=("${ids[@]}")
  line="$v:"
  for kind in desktop phone; do
    n=K01-swivel-$v-$kind
    rm -rf "$T/mr"
    git clone -q --filter=blob:none --no-checkout --depth 1 "$REPO" "$T/mr"
    git -C "$T/mr" sparse-checkout set --no-cone "/sequences/$n/" >/dev/null
    git -C "$T/mr" checkout -q main
    [ -f "$T/mr/sequences/$n/crop.json" ] || { log "$n: no region masters"; exit 1; }
    for k in 0 1 2 3; do $PY "$W/render/seq_rebuild.py" "$T/mr/sequences/$n" "$T/seq/$n" $k 4 > "$T/rb-$k.log" 2>&1 & done; wait
    rm -rf "$T/mr"
    nf=$(ls "$T/seq/$n"/f???.png | wc -l | tr -d ' ')
    [ "$nf" -ge 36 ] || { log "$n: only $nf frames rebuilt"; exit 1; }
    if [ $kind = desktop ]; then chk=$(f0chk "$T/seq/$n/f000.png" "$beam-full.png" 1920); q=58
    else chk=$(f0chk "$T/seq/$n/f000.png" "$phone-full.png" 1170); q=50; fi
    log "$n: $nf frames rebuilt; frame 0 vs its still: mean ${chk% *} luma, ${chk#* } % over 6"
    awk -v m="${chk% *}" 'BEGIN{exit !(m < 1.0)}' || { log "$n: frame 0 does not match its still"; exit 1; }
    node scripts/sequence.mjs "$T/seq" "$n" --formats=avif,webp --avif-quality=$q >> "$T/seq.log" 2>&1
    rm -rf "$T/seq/$n"
    grep -q "^$n avif" "$T/seq.log" || { log "$n: sequence.mjs did not export it"; exit 1; }
    line="$line $kind ${chk% *}"
  done
  summary+=("$line")
done
# drop old hash files: keep only the hashes the manifest names
python3 - <<'EOF'
import json, os, re
m = json.load(open("src/content/sequences.generated.json"))
for name, e in m.items():
    if not name.startswith("K01-swivel-"):
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
node scripts/stills.mjs "$T/m" "${allids[@]}" >> "$T/stills.log" 2>&1
git add -A public/stills src/content/stills.generated.json src/content/sequences.generated.json
bad=$(git diff --cached --name-only | grep -vE '^(public/stills/|src/content/(stills|sequences)\.generated\.json$)' || true)
[ -z "$bad" ] || { log "REFUSED: paths outside the allowed: $bad"; exit 1; }
git -c user.name=Claude -c user.email=noreply@anthropic.com commit -q -m "K01 in the one-racket canon (STATUS-mac one-racket:K01): ${K01X_WHAT:-the hero stills and its eight swivels, grip and Naked, both feels}

One material and the face's lights on every carbon part, whole-frame renders, as the approved one-racket batch; Naked
Pace's handle card sits 35 deg round the handle and lights the handle only (one-racket.env).${K01X_NOTE:+ $K01X_NOTE} Swivels rebuilt from their
region masters (render/seq_rebuild.py), desktop AVIF 58, phone AVIF 50, 36 frames; WebP 84. Frame 0 against its
still (mean luma, desktop at 1920, phone at 1170): $(IFS=';'; echo "${summary[*]}").

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
all=$(git diff --name-only origin/wip/owner-update...HEAD)
chg=$(git diff --name-only --diff-filter=AM origin/wip/owner-update...HEAD)
out=$(printf '%s\n' "$all" | grep -vE '^(public/stills/|src/content/(stills|sequences)\.generated\.json$)' || true)
mst=$(printf '%s\n' "$all" | grep -iE '\.(png|exr)$' || true)
big=$(for f in $chg; do [ -f "$f" ] && [ "$(stat -f %z "$f")" -gt 5242880 ] && echo "$f"; done || true)
if [ -n "$out$mst$big" ]; then log "REFUSED to push: outside=[$out] masters=[$mst] over5MB=[$big]"; exit 1; fi
git push -q --force-with-lease origin HEAD:refs/heads/mac/exports
sha=$(git rev-parse --short HEAD)
rm -rf "$T"
seqs=$(for v in "${VS[@]}"; do printf 'K01-swivel-%s-desktop,K01-swivel-%s-phone,' "$v" "$v"; done | sed 's/,$//')
cd "$KIT" && ./status_push.sh "$(date -u +%Y-%m-%dT%H:%M:%SZ) EXPORTED one-racket:K01 mac/exports@$sha $(IFS=,; echo "${allids[*]}"),$seqs (${K01X_WHAT:-stills + swivels, grip and Naked, both feels}${K01X_NOTE:+; $K01X_NOTE}; frame 0 vs still, mean luma: $(IFS=';'; echo "${summary[*]}")) M3Max-METAL" >/dev/null
log "EXPORTED K01 mac/exports@$sha"
