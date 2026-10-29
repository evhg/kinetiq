# KINETIQ render kit

The Blender (bpy 4.2, Cycles CPU) scripts that make the site's product stills: every master behind `public/stills/`
(K01 to K13, Command and Pace) and the in-progress K14. Nothing in the site imports this folder; it is the source of
the images, kept in git so it can never be lost again.

Recovered on 2026-10-28 from the session transcripts after the scratchpad that held it was wiped. See
"Recovery status" below for what is exact and what is not.

## Layout
- `racket.py`, `studio.py`, `look_c.py`: the old shared modules (studio helpers, softboxes, the pre-canon racket and its
  fonts/textures). `fillcheck.py`: the fill-rule check. `pace_*.py`: Pace 12K checks. `make_weave.py`,
  `make_spread.py`: carbon texture generators.
- `shots/`: one script per shot (`K01-hero-beam.py` ... `K14-edge.py`) and the shared libraries: `kq_canon.py` (THE
  canonical racket, use it in every shot), `k01_lib.py`, `k03s_*.py`, `k10_lib.py`, `k12_lib.py`, `k789_lib.py`,
  `feels_lib.py`, `g1_detail.py`; asset generators `k04_weave2.py`, `k04_gap.py`, `k04_bake.py`, `k04_bake_warp.py`.
- `notes/RENDER_NOTES.md` (how to author a shot, lighting rules, the fill rule, owner overrides) and `notes/canon.md`
  (the canonical racket's spec, materials and per-shot notes). Read both before touching a shot.
- `kqpaths.py`: where things go. `prepare_assets.py`: rebuilds the derived inputs. `link-masters.sh`: maps
  `out/final/*.png` to the site's still ids for `scripts/stills.mjs`.

Generated files never go in git. `KQ_RENDER_OUT` (default `/home/user/kinetiq-render-out`) holds:
`bpyenv/` (Python 3.11 venv), `assets/` (fonts, `tex/`, `k04_tex2/`, `k04_bake/`, caches `canon/`, `k10/`, `k12/`,
`k14/`), `out/` (previews; finals in `out/final/`), `masters/` (links made by `link-masters.sh`). `RENDER_ROOT`
overrides where the kit is (default: this folder).

## Set up (once per machine, about 10 minutes)
```sh
render/setup.sh            # python3.11 venv + bpy 4.2.0 (520 MB wheel from PyPI), fonts, textures, K04 bakes
render/setup.sh --force    # rebuild every derived asset
```
Needs `python3.11` (bpy 4.2 wheels are cp311 only) and network access to PyPI and raw.githubusercontent.com (fonts:
Archivo and Saira from google/fonts, SIL OFL; the OFL texts are saved next to them).

## Render
Run from `render/`, one Blender at a time (4 cores are shared; `flock render.lock` serialises):
```sh
cd render
PY=${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}/bpyenv/bin/python
flock render.lock $PY shots/K01-hero-beam.py --w 960 --h 540 --spp 32 --out k01/beam_p01      # preview
flock render.lock $PY shots/K01-hero-beam.py --w 2560 --h 1440 --spp 256 --out final/K01-hero-beam
flock render.lock $PY shots/K01-hero-beam.py --feel pace --w 2560 --h 1440 --spp 256 --out final/K01-hero-beam-pace
$PY fillcheck.py $KQ_RENDER_OUT/out/final/K01-hero-beam-full.png
```
`--out` is relative to `$KQ_RENDER_OUT/out`. Each script's docstring has its final command (sizes, samples,
variants, `--feel pace`, `--both`, `--phone`, `--crops`); the last finals used:

| Shot | Final command (add `--feel pace` and `-pace` to the out name for Pace) |
|---|---|
| K01 beam | `K01-hero-beam.py --w 2560 --h 1440 --spp 256 --out final/K01-hero-beam` (base, full, finale) |
| K01 phone | `K01-hero-frame.py --w 1440 --h 2560 --spp 256 --out final/K01-hero-frame-phone` |
| K02 | `K02-edge-line.py --w 2560 --h 1440 --spp 256 --out final/K02-edge-line --phone` |
| K03, K03b | `PYTHONHASHSEED=0 ... K03-section-cut.py --w 3200 --h 1800 --spp 320 --both --out final/K03-section-cut` (then `k03s_line.py`, see RENDER_NOTES) |
| K04 | `K04-hole-macro.py --w 3200 --h 1800 --spp 160 --variant both --out final/K04-hole-macro` |
| K05 | `K05-laser-scan.py --w 3200 --h 1800 --spp 160 --out final/K05-laser-scan` |
| K06 | `K06-mould.py --w 3200 --h 1800 --spp 160 --out final/K06-mould` |
| K07 | `K07-lineup-five.py --w 2560 --h 1440 --spp 160 --seq --out final/K07-lineup-five` |
| K08 | `K08-feel-pair.py --w 2560 --h 1440 --spp 256 --crops --out final/K08-feel-pair` |
| K09 | `K09-case-three.py --variant gallery --w 2400 --h 1800 --spp 160 --out final/K09-case-three-gallery`; `--variant card --hover-mix --w 1440 --h 1800` for the card |
| K10 | `K10-throat-serial.py --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial` |
| K11 | `K11-pair.py --weave command --w 3200 --h 1800 --spp 256 --out final/K11-pair-command` (`--weave pace`); `K11-single.py --w 3200 --h 1800 --spp 256 --out final/K11-single` |
| K12 | `K12-sweet-spot.py --w 3200 --h 1800 --spp 160 --out final/K12-sweet-spot` |
| K13 | `K13-layup.py --w 3200 --h 1800 --spp 128 --out final/K13-layup` |
| K14 | `K14-edge.py --w 2560 --h 1440 --spp 64 --out final/K14-edge` (Pace: `--feel pace --out final/K14-edge-pace`; about 45 min each) |
| K02 swivel (2026-10-29) | `K02-edge-line.py --w 2560 --h 1440 --spp 32 --seq 60 --range 0 35 --phone --crop 0.09 0.92 0.20 0.86 --only <i> --out seq2/K02-swivel-command` (Pace: `--feel pace --seq 45`); about 75 s a frame alone, 3 min with another shot rendering. The masters repo keeps the 2560 frames only; the phone sequence is them turned 90 deg counter-clockwise (`k12_lib.rotate_png`, 16-bit) |
| K01 swivel (2026-10-29) | portrait `K01-hero-frame.py --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop 0.20 0.82 0.48 0.95 --out seq2/K01-swivel-command-phone`; desktop `K01-hero-beam.py --w 2560 --h 1440 --crop 0.27 0.73 0.19 1.0 ...`; Pace adds `--feel pace --set P_FOLLOW=0.85` (k01_lib: the face cards turn with the racket, so the black face stays lit to 35 deg). About 5 min a portrait frame, 2 min a desktop one. Take the lock per frame (`flock render.lock ... --only i`, a few seconds' pause between frames, frames on disk skipped), frame 0 and the last first, so other shots slip in between |

Swivel sequences (`--seq`): frame 0 renders whole, the rest only inside `--crop` (a Cycles border region, about a third
of the frame) and are pasted into frame 0 with a feathered edge (`k12_lib.paste_region`), with persistent data so the
scene syncs once. The region must hold everything that moves: check the last frame against frame 0 (`sequence.mjs`
reports the change crop; it must sit inside the region). Then `node scripts/sequence.mjs $KQ_RENDER_OUT/out/seq2 <names>`
(frames counted from the folder; widths up to 1440 portrait and 2560 landscape). OIDN makes 16 to 24 spp read as
48 at 100% on these shots (2026-10-29 comparison).

## Export to the site
```sh
render/link-masters.sh                                   # out/final/*.png -> $KQ_RENDER_OUT/masters/<still id>.png
node scripts/stills.mjs $KQ_RENDER_OUT/masters [id ...]  # AVIF + WebP crops into public/stills/ (stills.json)
```

## Rules
- **Commit scripts immediately.** Every change to a shot, library or note is committed as soon as it renders, never
  left only on disk. The previous kit lived only in a scratchpad and was lost with it.
- **Masters go off-machine right after each final:** copy the final PNG (plus EXR under 100 MB and the settings JSON)
  to the private repo `evhg/kinetiq-masters` (`stills/<id>/`, swivel frames in `sequences/<name>/`) and push it the
  same session. Never put masters in this public repo. To render or export elsewhere, clone that repo and point
  `link-masters.sh`/`stills.mjs` at it.
- Same racket in every image: build it with `shots/kq_canon.py` (see `notes/canon.md` and the CLAUDE.md canon rule).

## Recovery status (2026-10-28)
Rebuilt by replaying every Write, Edit and file-changing shell command from the agents' transcripts, in time order,
in a sandbox, re-synchronising on every full Read of a file and checking the replay against every read-only inspection
command (`cat`, `sed -n`, `grep -n`, `wc -l`) the agents ran. Only the path constants were changed afterwards (see
`kqpaths.py`); the logic is as replayed. `shots/K14-edge.py` is the K14 agent's own reconstruction written just after
the wipe (it was mid-development and has no final yet). The tiny-preview comparison against `public/stills/` is in
the recovery report.
