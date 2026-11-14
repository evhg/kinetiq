#!/usr/bin/env bash
# one-racket-e2ec.sh (2026-11-14, the Mac render node): cloud REQUEST e2e-c 2026-11-14T09:00:40Z (owner chose option C,
# 'a ball at the very edge', for the landing page's 'Edge to edge.' section, replacing K14). Re-renders C in the
# one-racket canon (kq_canon.one_racket, the K11 settings of the approved batch: the wall card reaches the whole racket,
# the glossy streak and any Naked Pace handle card keep their links, the bores, throat and bridge wall their own light),
# same compositions as stills/E2E/E2E-C{,wide}-{command,pace}-{rings,full} of 11 Nov, with the 14 Nov fixes in
# shots/E2E-concepts.py (optic-yellow felt and a crisp seam; the rings as soft warm light on the face; each frame's
# exposure set so the flat face's mean luma matches K01-full's, e2ec.env, checked by e2e_face.py within 2 luma).
#   one-racket-e2ec.sh preview   C-rings Command, C-rings Pace, Cwide-rings Command grip (+ full), 2560x1440 spp 128,
#                                to previews/e2e-c, one PREVIEW line
#   one-racket-e2ec.sh final     5120x2880 spp 160 (C, Cwide grip and Naked; Command and Pace) and the 2160x3840 phone
#                                frames reframed round the ball (their own renders), masters to stills/E2E, one STATUS
#                                line per group (C, Cwide, Cwide Naked)
# Resumable (markers "e2ec ..."); the 11 Nov files go to $F/pre-e2ec-20261114 once.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R=e2e-c
E=$F/e2e-c
OLDF=$F/pre-e2ec-20261114
mkdir -p "$E" "$OLDF"
export KQ_ONE_RACKET_UNION=lg_wall KQ_ONE_RACKET_ASIS=lg_streak,PaceHandle_ KQ_ONE_RACKET_KEEP=holes,throat,bridgewall
. "$KIT/e2ec.env"   # EX_<frame>_<feel>: the exposures (C, Cwide, Cph, Cwph)
MODE=${1:-final}
log "E2EC-START $MODE device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# r1 <dir> <stem> <feel> <view 1|0> <phone 1|0> <naked 1|0> <w> <h> <spp>: render; a grip frame is rendered again (up to
# 3 tries) with its exposure corrected until its face is within 1 luma of K01 (the face mean drifts a little with the
# resolution: 1280 -> 2560 cost Command ~3 luma); a Naked frame takes its grip twin's final exposure (EXF)
declare -A EXF
r1() {
  local dir=$1 stem=$2 feel=$3 view=$4 ph=$5 nk=$6 w=$7 h=$8 spp=$9
  local fr=C; [ "$view" = 0 ] && fr=Cwide; [ "$ph" = 1 ] && fr=${fr/C/Cph}; [ "$fr" = Cphwide ] && fr=Cwph
  local ev=EX_${fr}_$feel var=EXPO_C tgt=137.4 sl=0.40; [ "$feel" = pace ] && { var=EXPO_P; tgt=44.0; sl=0.75; }
  local e=${!ev} key="$fr-$feel-$w" try m envs=(env)
  [ "$nk" = 1 ] && { envs=(env KQ_NOGRIP=1 KQ_NAKED_FLARE=0); [ -n "${EXF[$key]:-}" ] && e=${EXF[$key]}; }
  for try in 1 2 3; do
    still "e2ec-$stem" "$dir/$stem-full.png" - -- "${envs[@]}" $PY shots/E2E-concepts.py --concept c --mode single \
      --feel "$feel" --w "$w" --h "$h" --spp "$spp" --out "$dir/$stem" --eset "VIEW_C=$view,PHONE=$ph,$var=$e"
    need "$dir/$stem"-{rings,full,mask}.png || return 1
    [ "$nk" = 1 ] && break
    m=$($PY "$KIT/e2e_face.py" "$dir/$stem" "$feel" 2>&1 >/dev/null | sed -n 's/^mean=//p')
    log "E2EC-EXPO $stem try $try exposure $e face $m"
    awk -v m="$m" -v t="$tgt" 'BEGIN{exit !((m-t)^2 > 1.0)}' || break
    [ $try = 3 ] && break
    e=$(awk -v e="$e" -v m="$m" -v t="$tgt" -v s="$sl" 'BEGIN{printf "%.5f", e * exp(log(t/m)/s)}')
    rm -f "$dir/$stem"-*.png "$dir/$stem.exr"
  done
  [ "$nk" = 1 ] || EXF[$key]=$e
}
# chk <dir> <stem> <feel> [twin stem]: the face against K01-full (and the grip twin)
chk() {
  local dir=$1 stem=$2 feel=$3 r
  r=$($PY "$KIT/e2e_face.py" "$dir/$stem" "$feel" ${4:+"$dir/$4"} 2>/dev/null) || { log "E2EC-FACE-FAIL $stem $r"; return 1; }
  log "E2EC-FACE $stem $r"; FACES+=("$stem $r")
}
FACES=()
if [ "$MODE" = preview ]; then
  P=$OUT/previews/e2e-c
  mkdir -p "$P"
  t0=$(date +%s)
  r1 "$P" E2E-C-command command 1 0 0 2560 1440 128 && chk "$P" E2E-C-command command || exit 1
  r1 "$P" E2E-C-pace pace 1 0 0 2560 1440 128 && chk "$P" E2E-C-pace pace || exit 1
  r1 "$P" E2E-Cwide-command command 0 0 0 2560 1440 128 && chk "$P" E2E-Cwide-command command || exit 1
  tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || exit 0
  masters "e2ec m preview" previews/e2e-c "e2e-c PREVIEW, 2560x1440 spp 128" "$P"/E2E-C{,wide}-command-{rings,full}.png "$P"/E2E-C-pace-{rings,full}.png
  done_mark "e2ec m preview" || exit 1
  st "e2ec status preview" "$(date -u +%FT%TZ) e2e-c:PREVIEW previews/e2e-c/E2E-C-command-rings.png, E2E-C-pace-rings.png, E2E-Cwide-command-rings.png (+ each -full.png, without the rings) $(hm $tt) $DEVNAME, 2560x1440 spp 128 (finals 5120x2880 spp 160 + 2160x3840 phone frames). Same compositions as 11 Nov, in the one-racket canon (the K11 links of the approved batch: wall card to the whole racket, streak kept, bores/throat/bridge on their own light; whole frames). Fixes: (1) the ball a true optic yellow (felt and fibres (0.45, 0.95, 0.0) linear, given its own exposure in the comp so the racket's exposure leaves it), the seam a clean light grey with the felt's fibres kept 1.2 mm off it: crisp; (2) the rings a soft warm light ON the face: the studio image x (1 + k x ring) in a warm tint plus a little warm light on the face's albedo, no additive emission, so the weave reads through them (Command k 2.2, Pace k 1.2 with narrower, less warm rings); (3) the face matched to K01-full: each frame's exposure set so the flat face's mean luma (its own mask: no holes, ball or rings) is K01-full's, Command 137.4 / Pace 44.0, with a small white balance (K01's neutral grey; the K11 studio read a little warm). Face means here: $(IFS=';'; echo "${FACES[*]}"). The contact patch's centre stays 4 mm inside the outline at the head's widest point, on the 1.0 mm canon's flat face. Finals follow now; EXPORT after them." || exit 1
  log "E2EC-DONE preview"; exit 0
fi
# finals: <group> <stems...>, each stem "<stem>:<feel>:<view>:<naked>" (+ its phone frame <stem-with -phone>)
group() {
  local g=$1 what=$2; shift 2
  done_mark "e2ec status $g" && return 0
  local t0=$(date +%s) files=() s stem feel view nk ps twin
  for s in "$@"; do
    IFS=: read -r stem feel view nk <<< "$s"
    ps=${stem/-command/-phone-command}; ps=${ps/-pace/-phone-pace}
    if ! done_mark "e2ec aside $stem"; then
      local f; for f in "$E/$stem"* "$F/e2e/$stem"-*.png; do [ -e "$f" ] && mv "$f" "$OLDF"/; done; mark "e2ec aside $stem"
    fi
    twin=; [ "$nk" = 1 ] && twin=${stem/-nogrip/}
    twp=; [ "$nk" = 1 ] && twp=${ps/-nogrip/}
    r1 "$E" "$stem" "$feel" "$view" 0 "$nk" 5120 2880 160 && chk "$E" "$stem" "$feel" $twin || return 1
    r1 "$E" "$ps" "$feel" "$view" 1 "$nk" 2160 3840 160 && chk "$E" "$ps" "$feel" $twp || return 1
    files+=("$E/$stem"-{rings,full}.png "$E/$ps"-{rings,full}.png)
  done
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || return 0
  masters "e2ec m $g" stills/E2E "E2E $g ($R), 5120x2880 + 2160x3840 phone" "${files[@]}"
  done_mark "e2ec m $g" || return 1
  local list=$(for f in "${files[@]}"; do printf 'stills/E2E/%s,' "$(basename "$f")"; done | sed 's/,$//')
  st "e2ec status $g" "$(date -u +%FT%TZ) $R:$g $list $(hm $tt) $DEVNAME $what; 5120x2880 spp 160 and the 2160x3840 phone frame reframed round the ball (its own render, not a crop), rings and full from one render each; face mean against K01-full (Command 137.4 / Pace 44.0; Naked also against its grip twin): $(IFS=';'; echo "${FACES[*]}"); shots/E2E-concepts.py; in the one-racket canon (K11's links of the approved batch, whole frames); render time this run"
}
FACES=(); group C "C close-up (the hero, 100 mm, 38 deg off the face normal), Command and Pace: the ball pressed onto the face at the head's widest point, its contact patch's centre 4 mm inside the outline on the flat face, overhanging the rim; optic-yellow felt, crisp seam; the rings soft warm light on the face, the weave through them" \
  E2E-C-command:command:1:0 E2E-C-pace:pace:1:0 || exit 1
FACES=(); group Cwide "C wide (the K11 camera, the whole racket), grip, Command and Pace" \
  E2E-Cwide-command:command:0:0 E2E-Cwide-pace:pace:0:0 || exit 1
FACES=(); group Cwide-nogrip "C wide, the Naked twin (canon Naked, KQ_NAKED_FLARE=0; any handle card on the handle only), Command and Pace" \
  E2E-Cwide-nogrip-command:command:0:1 E2E-Cwide-nogrip-pace:pace:0:1 || exit 1
log "E2EC-DONE final"
