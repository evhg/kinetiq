# Swivels in the new canon: export and release steps (2026-11-02)

`render/queue-swivels.sh` renders the K01 and K02 swivels in the new canon (HD weave, 1.0 mm edge) into
`$KQ_RENDER_OUT/out/seq3/<name>/`, the K01 Pace stills with the owner-note-7 weave light into `out/final/*-n7-*`, and
the grip-off swivels. Log: `$KQ_RENDER_OUT/logs/queue-swivels.log` (one `FRAME`, `STILL`, `JOB-DONE`, `cropcheck` line
each; per-render Blender output in `logs/queue-swivels/<name>.log`). Rule: never ship a still and its swivel from
different canons. Each step below is for one finished item; the queue keeps running meanwhile (`sequence.mjs` skips a
folder whose frames are not all there).

```sh
export KQ_RENDER_OUT=/home/user/kinetiq-render-out
S=$KQ_RENDER_OUT/out/seq3
M=/home/user/kinetiq-masters
PY=$KQ_RENDER_OUT/bpyenv/bin/python
```

## 1. A sequence is finished
`grep "JOB-DONE\|cropcheck" $KQ_RENDER_OUT/logs/queue-swivels.log`: `36 of 36` (K02: 60 or 45) on disk and the
cropcheck line `OK`.

## 2. Check it
```sh
cd /home/user/kinetiq/render
$PY shots/seq_check.py $S/K01-swivel-command-desktop $KQ_RENDER_OUT/out/final/K01-hero-beam-full.png
```
Frame-0 registration with the still the page shows under it (the swap at the start of the scrub), at display width:
```sh
python3 - "$S/K01-swivel-command-desktop/f000.png" "$KQ_RENDER_OUT/out/final/K01-hero-beam-full.png" 1920 <<'EOF'
import sys, numpy as np
from PIL import Image
a, b, w = sys.argv[1], sys.argv[2], int(sys.argv[3])
def L(p):
    im = Image.open(p).convert("RGB"); h = round(im.size[1] * w / im.size[0])
    return np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32) @ np.array([.2126, .7152, .0722])
d = np.abs(L(a) - L(b))
print("mean %.2f luma, %.2f %% of pixels over 6 luma, max %.0f" % (d.mean(), 100 * (d > 6).mean(), d.max()))
EOF
```
Pass: mean under 1 luma and under 1 % of pixels over 6 (the old-canon swivels against the new stills measured 0.6 to 0.7
and 1.5 %, all of it the weave). Frame 0 renders at the still's samples (`--spp0`), so the residue is denoiser grain.

| Sequence (`seq3/`) | Its still(s) under frame 0 (`out/final/`) |
|---|---|
| K01-swivel-command-phone | K01-hero-frame-phone-full.png (1170 and 2160 wide) |
| K01-swivel-command-desktop | K01-hero-beam-full.png (1920) |
| K02-swivel-command-desktop / -phone | K02-edge-line.png (the phone frames are it turned 90 deg CCW) |
| K01-swivel-pace-phone | K01-hero-frame-phone-pace-n7-full.png |
| K01-swivel-pace-desktop | K01-hero-beam-pace-n7-full.png |
| K02-swivel-pace-desktop / -phone | K02-edge-line-pace.png |
| K01-swivel-nogrip-command-phone / -desktop | K01-hero-frame-phone-nogrip-full.png / K01-hero-beam-nogrip-full.png |
| K01-swivel-nogrip-pace-phone / -desktop | K01-hero-frame-phone-nogrip-pace-n7-full.png / K01-hero-beam-nogrip-pace-n7-full.png |

## 3. Masters off-machine first (private repo, never the public one)
Hard links (`cp -al`) cost no disk; the git objects still take one copy, so check `df -h /` first (K01 portrait is
about 1.3 GB a sequence, desktop 0.55 GB, K02 0.36 GB; masters keep the 2560 K02 frames only).
```sh
cd $M
n=K01-swivel-command-desktop; dst=sequences/$n-2560        # portrait: $n-2160; K02: K02-swivel-command-2560 from $S/K02-swivel-command-desktop
git rm -rq --cached $dst 2>/dev/null; rm -rf $dst           # the old-canon frames stay in the history
mkdir -p $dst && cp -al $S/$n/f*.png $S/$n/frames.jsonl $dst/
git add $dst && git commit -qm "$n in the new canon (HD weave, 1.0 mm edge), 2026-11-02" && git push -q origin main
git -C $M status -sb | head -1                               # "## main" with no [ahead]
```
Then the K01 Pace stills (step 5's names) into `stills/K01/` the same way, and push.

## 4. Export to the site
From the site checkout (`/home/user/kinetiq`, branch `wip/owner-update`):
```sh
node scripts/sequence.mjs $S K01-swivel-command-desktop K01-swivel-pace-desktop K02-swivel-command-desktop K02-swivel-pace-desktop
node scripts/sequence.mjs $S K01-swivel-command-phone K01-swivel-pace-phone --formats=avif,webp --avif-quality=50
node scripts/sequence.mjs $S K02-swivel-command-phone --formats=avif,webp --avif-quality=50 --keep=45
node scripts/sequence.mjs $S K02-swivel-pace-phone --formats=avif,webp --avif-quality=50
node scripts/sequence.mjs $S K01-swivel-nogrip-command-desktop K01-swivel-nogrip-pace-desktop
node scripts/sequence.mjs $S K01-swivel-nogrip-command-phone K01-swivel-nogrip-pace-phone --formats=avif,webp --avif-quality=50
```
This rewrites `public/stills/seq/<name>/*` (new hashes; delete the old hash files `sequence.mjs` reports or leaves) and
`src/content/sequences.generated.json`. The four `K01-swivel-nogrip-*` entries are new: `Hero.tsx` plays them with no
code change (`SWIVEL.off`); `grip-store.ts`, `Hero.tsx` and CLAUDE.md say "no grip-off swivel yet", to be updated.
Check the phone load budget (`npm run check -- --only=phone,phone-short`, and `--grip=off`, `--feel=pace`).

## 5. Stills the release must switch
- K01 Pace, new weave light: rename the `-n7` finals over the old names, then re-export:
  ```sh
  cd $KQ_RENDER_OUT/out/final
  for v in base full finale; do mv K01-hero-beam-pace-n7-$v.png K01-hero-beam-pace-$v.png; done
  for v in base full; do mv K01-hero-frame-phone-pace-n7-$v.png K01-hero-frame-phone-pace-$v.png
    mv K01-hero-beam-nogrip-pace-n7-$v.png K01-hero-beam-nogrip-pace-$v.png
    mv K01-hero-frame-phone-nogrip-pace-n7-$v.png K01-hero-frame-phone-nogrip-pace-$v.png; done
  cd /home/user/kinetiq && render/link-masters.sh
  node scripts/stills.mjs $KQ_RENDER_OUT/masters K01-base-pace K01-full-pace K01-finale-pace K01-hero-base-phone-pace \
    K01-hero-full-phone-pace K01-nogrip-base-pace K01-nogrip-full-pace K01-nogrip-hero-base-phone-pace K01-nogrip-hero-full-phone-pace
  ```
  (the old Pace finals are in the masters repo, `stills/K01/*-pace.png`, if they are ever wanted back).
- K01 Command and K02 (both feels): the stills already on `wip/owner-update` (2026-11-02, HD, 1.0 mm) are the ones the
  new swivels register with; nothing to re-export.
- Ship the new K01 and K02 stills to `main` only together with their new sequences (all of `public/stills/seq/K01-*`,
  `K02-*` and `sequences.generated.json`), never one without the other.
