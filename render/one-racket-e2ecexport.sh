#!/opt/homebrew/bin/bash
# one-racket-e2ecexport.sh (2026-11-14, the Mac render node): export cloud REQUEST e2e-c (option C 'a ball at the very
# edge' for 'Edge to edge.') to mac/exports and post one EXPORTED line. Ids E2E-C-rings, E2E-C-full, E2E-Cwide-rings,
# E2E-Cwide-full, each + "-pace"; the Cwide Naked twins E2E-Cwide-nogrip-{rings,full}(-pace) ("-nogrip" after the
# shot name, as bareId puts it after the K number). Two crops per id, each from its own master: ewide = the 5120x2880
# frame whole; ephone = the 2160x3840 phone frame (its own render reframed round the ball) whole. stills.mjs exports
# one master per id, so it runs here in a scratch tree (a copy of scripts/stills.mjs, a stills.json holding only these
# ids with ewide {} / ephone {} and preview/edge-to-edge's widths ewide 1280/1920/2880, ephone 828/1170/1440; AVIF 74
# and WebP 86, stills.mjs's defaults), once per crop; the files and their stills.generated.json entries are copied
# into the worktree. The repo's stills.json is not touched (the cloud adds the entries on its release branch).
if [ -z "${KQ_XLOCKED:-}" ]; then exec env KQ_XLOCKED=1 flock "$HOME/kinetiq-render/export.lock" "$(cd "$(dirname "$0")" && pwd)/$(basename "$0")" "$@"; fi
set -euo pipefail
cd "$(dirname "$0")"
KIT=$PWD
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export PATH=/opt/homebrew/opt/node@22/bin:$PATH
W=${KQ_EXPORTS:-$HOME/kinetiq-render/kinetiq-exports}
E=$KQ_RENDER_OUT/out/final/e2e-c
T=$KQ_RENDER_OUT/tmp-e2ecexp
L=$KQ_RENDER_OUT/logs/one-racket.log
log() { echo "$(date -u +%FT%TZ) E2ECEXP $*" | tee -a "$L"; }
# id -> desktop stem, phone stem, variant
declare -A DS PS
for sh in C Cwide Cwide-nogrip; do
  for v in rings full; do
    for f in command pace; do
      id="E2E-$sh-$v"; [ $f = pace ] && id="$id-pace"
      DS[$id]="E2E-$sh-$f-$v"; PS[$id]="E2E-$sh-phone-$f-$v"
    done
  done
done
ids=($(printf '%s\n' "${!DS[@]}" | sort))
# E2ECX_IDS (comma list): export these ids alone (cloud REVIEW 10:52Z: the four Cwide Pace ids re-rendered)
if [ -n "${E2ECX_IDS:-}" ]; then
  IFS=, read -r -a ids <<< "$E2ECX_IDS"
  for id in "${ids[@]}"; do [ -n "${DS[$id]:-}" ] || { log "unknown id $id"; exit 1; }; done
fi
for id in "${ids[@]}"; do
  for s in "${DS[$id]}" "${PS[$id]}"; do [ -f "$E/$s.png" ] || { log "missing $E/$s.png"; exit 1; }; done
done
cd "$W"
[ "$(git rev-parse --abbrev-ref HEAD)" = mac/exports ] || { log "not on mac/exports"; exit 1; }
[ -z "$(git status --porcelain)" ] || { log "exports worktree not clean"; exit 1; }
git fetch -q origin
git rebase -q origin/wip/owner-update
rm -rf "$T"; mkdir -p "$T/x/scripts" "$T/x/src/content" "$T/x/public/stills" "$T/wide" "$T/phone"
cp scripts/stills.mjs "$T/x/scripts/"
ln -s "$W/node_modules" "$T/x/node_modules"
echo '{}' > "$T/x/src/content/stills.generated.json"
python3 - "$T/x/src/content/stills.json" "${ids[@]}" <<'EOF'
import json, sys
out, ids = sys.argv[1], sys.argv[2:]
json.dump({"widths": {"ewide": [1280, 1920, 2880], "ephone": [828, 1170, 1440]},
           "stills": {i: {"crops": {"ewide": {}, "ephone": {}}} for i in ids}}, open(out, "w"), indent=1)
EOF
for id in "${ids[@]}"; do
  ln -s "$E/${DS[$id]}.png" "$T/wide/$id.png"
  ln -s "$E/${PS[$id]}.png" "$T/phone/$id.png"
done
KQ_CROPS=ewide node "$T/x/scripts/stills.mjs" "$T/wide" >> "$T/stills.log" 2>&1
KQ_CROPS=ephone node "$T/x/scripts/stills.mjs" "$T/phone" >> "$T/stills.log" 2>&1
n=$(ls "$T/x/public/stills" | wc -l | tr -d ' ')
[ "$n" -eq $(( ${#ids[@]} * 6 * 2 )) ] || { log "stills: $n files, expected $(( ${#ids[@]} * 12 ))"; exit 1; }
# into the worktree: earlier exports of these id-crops replaced, the generated entries merged (same format)
node - "$T/x" "${ids[@]}" <<'EOF'
const fs = require("fs"), path = require("path");
const [x, ...ids] = process.argv.slice(2);
const out = "public/stills", gen = "src/content/stills.generated.json";
const sizes = JSON.parse(fs.readFileSync(gen, "utf8"));
const neu = JSON.parse(fs.readFileSync(path.join(x, gen), "utf8"));
for (const id of ids) for (const crop of ["ewide", "ephone"]) {
  const key = `${id}-${crop}`;
  const re = new RegExp(`^${key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}-\\d+(\\.[0-9a-f]{10})?\\.(avif|webp)$`);
  for (const f of fs.readdirSync(out)) if (re.test(f)) fs.unlinkSync(path.join(out, f));
  for (const f of fs.readdirSync(path.join(x, out))) if (re.test(f)) fs.copyFileSync(path.join(x, out, f), path.join(out, f));
  if (!neu[key]) throw new Error("no entry " + key);
  sizes[key] = neu[key];
}
fs.writeFileSync(gen, JSON.stringify(sizes, null, 1) + "\n");
EOF
sz=$(python3 - "$T/x/src/content/stills.generated.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
print(" ".join(sorted({"%s %dx%d" % (k.rsplit("-", 1)[1], v["w"], v["h"]) for k, v in d.items()})))
EOF
)
git add -A public/stills src/content/stills.generated.json
bad=$(git diff --cached --name-only | grep -vE '^(public/stills/|src/content/stills\.generated\.json$)' || true)
[ -z "$bad" ] || { log "REFUSED: paths outside the allowed: $bad"; exit 1; }
git -c user.name=Claude -c user.email=noreply@anthropic.com commit -q -m "E2E-C in the one-racket canon (STATUS-mac e2e-c): option C 'a ball at the very edge' for 'Edge to edge.'${E2ECX_SUBJ:-}

${#ids[@]} ids ($(IFS=,; echo "${ids[*]}")), two crops
each from its own master: ewide the 5120x2880 frame whole, ephone the 2160x3840 phone frame reframed round the ball
(its own render). Widths as preview/edge-to-edge (ewide 1280/1920/2880, ephone 828/1170/1440), AVIF 74, WebP 86.
stills.json not touched: each crop is {} on its own master. Sizes: $sz.

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
cd "$KIT" && ./status_push.sh "$(date -u +%Y-%m-%dT%H:%M:%SZ) EXPORTED e2e-c mac/exports@$sha $(IFS=,; echo "${ids[*]}") (crops ewide and ephone, each from its own master: ewide = stills/E2E/<stem>-{rings,full}.png 5120x2880 whole, ephone = stills/E2E/<stem with -phone>-{rings,full}.png 2160x3840 whole, reframed round the ball; stems E2E-C-<feel>, E2E-Cwide-<feel>, E2E-Cwide-nogrip-<feel>; Naked ids carry -nogrip after the shot name (E2E-Cwide-nogrip-rings-pace); widths ewide 1280/1920/2880, ephone 828/1170/1440 as preview/edge-to-edge, AVIF 74 / WebP 86; stills.json untouched: its entries want ewide {} and ephone {}, and a re-export needs the phone master for ephone (stills.mjs reads one master per id). ${E2ECX_NOTE:-}) M3Max-METAL"
log "EXPORTED e2e-c mac/exports@$sha"
