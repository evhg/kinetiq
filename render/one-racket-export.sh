#!/opt/homebrew/bin/bash
# one-racket-export.sh (2026-11-14, the Mac render node): export the one-racket stills of the given groups with
# mac_export.sh and post one EXPORTED line each (cloud 2026-11-13T18:27Z: "then export and post EXPORTED lines as before").
#   render/one-racket-export.sh <group> [<group> ...]    groups: k05 k16 k06 k10 k12 (and a "<note>" in ORE_NOTE_<group>)
# Each master is the newest of final/w5760/, final/v5k/, final/<name>.png and must be newer than the one-racket start
# (one-racket.cleared's first write), or the group is refused: only one-racket renders are exported.
set -u
cd "$(dirname "$0")"
KIT=$PWD
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
F=$KQ_RENDER_OUT/out/final
REF=$KQ_RENDER_OUT/logs/queue-nov3.done.pre-oneracket   # written once, when the batch first cleared markers
L=$KQ_RENDER_OUT/logs/one-racket.log
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$L"; }
pick() {   # pick <final name without .png>: newest candidate, newer than $REF
  local best="" c
  for c in "$F/w5760/$1.png" "$F/v5k/$1.png" "$F/$1.png"; do
    [ -f "$c" ] || continue
    if [ -z "$best" ] || [ "$c" -nt "$best" ]; then best=$c; fi
  done
  [ -n "$best" ] && [ "$best" -nt "$REF" ] && echo "$best"
}
declare -A G
G[k05]="K05=K05-laser-scan K05-pace=K05-laser-scan-pace K05-phone=K05-laser-scan-phone K05-phone-pace=K05-laser-scan-pace-phone K05-nogrip=K05-laser-scan-nogrip K05-nogrip-pace=K05-laser-scan-nogrip-pace K05-nogrip-phone=K05-laser-scan-nogrip-phone K05-nogrip-phone-pace=K05-laser-scan-nogrip-pace-phone"
G[k16]="K16-base=K16-pair-base K16-full=K16-pair-full K16-base-pace=K16-pair-pace-base K16-full-pace=K16-pair-pace-full"
G[k06]="K06-base=K06-mould-base K06-full=K06-mould-full K06-base-pace=K06-mould-pace-base K06-full-pace=K06-mould-pace-full K06-nogrip-base=K06-mould-nogrip-base K06-nogrip-full=K06-mould-nogrip-full K06-nogrip-base-pace=K06-mould-nogrip-pace-base K06-nogrip-full-pace=K06-mould-nogrip-pace-full"
G[k10]="K10=K10-throat-serial K10-pace=K10-throat-serial-pace K10-nogrip=K10-throat-serial-nogrip K10-nogrip-pace=K10-throat-serial-nogrip-pace"
G[k12]="K12-base=K12-sweet-spot-base K12-full=K12-sweet-spot-full K12-base-pace=K12-sweet-spot-pace-base K12-full-pace=K12-sweet-spot-pace-full K12-nogrip-base=K12-sweet-spot-nogrip-base"
rc=0
for g in "$@"; do
  [ -n "${G[$g]:-}" ] || { log "EXPORT $g: unknown group"; rc=1; continue; }
  args=(); ids=(); bad=""
  for kv in ${G[$g]}; do
    id=${kv%%=*}; m=$(pick "${kv#*=}") || true
    [ -n "$m" ] || { bad+=" ${kv#*=}"; continue; }
    args+=("$id=$m"); ids+=("$id")
  done
  [ -z "$bad" ] || { log "EXPORT $g REFUSED: no one-racket master for$bad"; rc=1; continue; }
  U=$(echo "$g" | tr a-z A-Z)
  out=$("$KIT/mac_export.sh" "$U in the one-racket canon (STATUS-mac one-racket:$g): one material, the face's lights on every carbon part, whole-frame renders; grip and Naked, both feels" "${args[@]}" 2>&1 | tee -a "$KQ_RENDER_OUT/logs/export.log" | tail -3)
  sha=$(printf '%s\n' "$out" | awk '/^EXPORTED-SHA /{s=$2} END{print s}')
  [ -n "$sha" ] || { log "EXPORT $g FAILED: $out"; rc=1; continue; }
  note=$(eval echo "\${ORE_NOTE_$g:-}")
  ids_csv=$(IFS=,; echo "${ids[*]}")
  ./status_push.sh "$(date -u +%Y-%m-%dT%H:%M:%SZ) EXPORTED one-racket:$g mac/exports@$sha $ids_csv${note:+ ($note)} M3Max-METAL" >/dev/null
  log "EXPORTED $g mac/exports@$sha $ids_csv"
done
exit $rc
