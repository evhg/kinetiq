#!/usr/bin/env bash
# fw-e2e.sh (2026-11-11, the Mac render node): cloud REQUEST edge-to-edge-concepts, OK'd 10:45Z on the 10:41Z PREVIEW with
# fixes (A a warm tint ON the white twill, the head to ~80 % of the height; B the white face, a lower closer camera from
# the crown end; C the ball overhanging the rim, brighter yellow, softer rings, the white face). Finals: 5120x2880 spp
# 160, Command and Pace, masters only (no export), stills/E2E. One render per concept and feel, every stage composited
# from AOVs (pixel-registered). One STATUS line per concept. Usage: fw-e2e.sh a|b|c ... Resumable (markers "e2e ...").
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R=edge-to-edge-concepts
E=$F/e2e
mkdir -p "$E"
log "E2E-START $* device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# r1 <stem> <concept> <feel> <eset or -> <stage tags...>
r1() {
  local stem=$1 c=$2 feel=$3 es=$4; shift 4
  local files=() t
  for t in "$@"; do files+=("$E/$stem-$t.png"); done
  local ea=(); [ "$es" != "-" ] && ea=(--eset "$es")
  still "e2e-$stem" "${files[0]}" - -- $PY shots/E2E-concepts.py --concept "$c" --mode single --feel "$feel" --w 5120 --h 2880 --spp 160 --out "final/e2e/$stem" "${ea[@]}"
  need "${files[@]}" || return 1
  [ "$PUSH" = 1 ] || return 0
  masters "e2e m $stem" stills/E2E "E2E $c $feel, $R, 5120x2880" "${files[@]}"
  done_mark "e2e m $stem"
}
# redo1 <stem>: the previous final set aside and its masters marker cleared, so r1 renders and pushes it again
redo1() { aside "e2e $1" "$E/$1"-*.png; sed -i '' "/^e2e m $1\$/d" "$DONE"; }
for c in "$@"; do
  done_mark "e2e status $c" && continue
  if [ "$c" = pace-fix ]; then   # PREVIEW review 11:15Z (Mac): B Pace's crown wall read as a black void, C Pace's rings as bold stripes
    t0=$(date +%s)
    redo1 E2E-B-pace; r1 E2E-B-pace b pace - s1 s2 s3 s4 s5 s6 || exit 1
    for s in E2E-C-pace E2E-Cwide-pace; do redo1 $s; done
    r1 E2E-C-pace c pace VIEW_C=1 rings full || exit 1
    r1 E2E-Cwide-pace c pace VIEW_C=0 rings full || exit 1
    tt=$(( $(date +%s) - t0 ))
    [ "$PUSH" = 1 ] || continue
    st "e2e status $c" "$(date -u +%FT%TZ) $R:pace-fix stills/E2E/E2E-B-pace-{s1..s6}.png stills/E2E/E2E-C{,wide}-pace-{rings,full}.png $(hm $tt) $DEVNAME replaces the Pace frames of B and C posted at 11:03Z / 11:13Z (Command unchanged): B Pace, a glossy-only soft card at the crown wall's mirror direction so the black 12K wall reads as a lit gloss band instead of a void; C Pace, the rings at 3/8 of the Command strength so they read as soft light on the black weave, not as bold stripes; 5120x2880 spp 160; shots/E2E-concepts.py; masters only, no export; render time this run" || exit 1
    continue
  fi
  t0=$(date +%s)
  case $c in
    a) for f in command pace; do r1 "E2E-A-$f" a $f - s000 s020 s040 s060 s080 s100 s100-line || exit 1; done
       what="A 'the face fills with light' (7 frames each feel: 0 20 40 60 80 100 % and 100 % with the edge line): face-on (10 deg), the head framed to 80 % of the height; inside the light the studio image takes a 2700 K tint (35 %) so the white twill (and the black 12K) stays readable through it, a little under-coat emission and a soft glow on it alone; outside it the studio x 0.45; the front runs parallel to the edge (distance-to-boundary mask) and reaches the whole edge at once, round the throat too; the last frame adds the thin bright line where the flat face ends, 1 mm from the edge"
       list="stills/E2E/E2E-A-{command,pace}-{s000,s020,s040,s060,s080,s100,s100-line}.png" ;;
    b) for f in command pace; do r1 "E2E-B-$f" b $f - s1 s2 s3 s4 s5 s6 || exit 1; done
       what="B 'flat to the edge' (6 frames each feel, the line from the throat to the crown): camera beyond the crown, 16 deg above the face plane, 100 mm, f/11, looking along the face; the command-dark-lift face (studio x 0.6); a 1.5 mm warm line straight across the flat face that bends down over the 1.0 mm edge radius at both sides and fades down the wall, a faint trail behind it; holes dark"
       list="stills/E2E/E2E-B-{command,pace}-{s1,s2,s3,s4,s5,s6}.png" ;;
    c) for f in command pace; do
         r1 "E2E-C-$f" c $f VIEW_C=1 rings full || exit 1
         r1 "E2E-Cwide-$f" c $f VIEW_C=0 rings full || exit 1
       done
       what="C 'a ball at the very edge' (hero + wide, each with and without the rings, each feel): K17's padel ball (brighter yellow) pressed onto the face at the head's widest point, its contact patch 4 mm inside the outline so it overhangs the rim; soft concentric warm rings every 22 mm, even strength, across the whole face; the white face undimmed; hero 100 mm 38 deg off the face normal, wide = the K11 camera"
       list="stills/E2E/E2E-C{,wide}-{command,pace}-{rings,full}.png" ;;
  esac
  tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || continue
  st "e2e status $c" "$(date -u +%FT%TZ) $R:$c $list $(hm $tt) $DEVNAME $what; 5120x2880 spp 160, one render per feel (stages from AOVs, pixel-registered); shots/E2E-concepts.py; masters only, no export; claim guard: no words or numbers in the frames; with the $CANON; render time this run" || exit 1
done
log "E2E-DONE $*"
