# queue-nov3: Naked, 5K hero, light-sweep swivels (owner feedback 2026-11-03)

`render/queue-nov3.sh` renders, exports and pushes, in order:

| Item | What | Outputs |
|---|---|---|
| p1a | K01 Naked stills (carbon butt), Command then Pace: beam 5120x2880 spp 64 (base, full, finale), portrait 2160x3840 spp 48 | `out/final/K01-hero-beam-nogrip[-pace]-v5k-*`, `K01-hero-frame-phone-nogrip[-pace]-v5k-*`; ids `K01-nogrip-*` |
| p1b | The other Naked twins: the cap region re-rendered (`KQ_BORDER_AUTO=1`) and pasted into the existing masters (`patch_paste.py`, ring check; a refused paste re-renders the whole still): K02, K12, K11 single/pair, K06, K07 (K08 was rendered whole) | the same `out/final/*-nogrip*` files, overwritten |
| p1c | Missing twins K09 (gallery, card) and K10, both feels, whole renders | `out/final/K09-case-three-*-nogrip*`, `K10-throat-serial-nogrip*` |
| p2a | K01 Command grip: 5K beam + portrait stills in the light-sweep scene, then the swivels (portrait 2160 spp 24, desktop 5120 spp 16, 36 frames, 0-35 deg, the band crossing the head) | `out/seq4/K01-swivel-command-{phone,desktop}` |
| p2b | K01 Command Naked swivels | `out/seq4/K01-swivel-nogrip-command-*` |
| p2c | K01 Pace grip stills + swivels (cards follow 85 %) | `out/seq4/K01-swivel-pace-*` |
| p2d | K01 Pace Naked swivels | `out/seq4/K01-swivel-nogrip-pace-*` |

Each finished group is exported from the worktree `/home/user/wt-render` (`render/export_push.sh`, never the shared
checkout) and pushed to `wip/owner-update`; masters go to the private `evhg/kinetiq-masters` through
`render/masters_push.sh` (a throwaway blobless clone per push). Swivel masters are f000 whole + region crops
(`seq_masters.py`); after their push the local frames 1.. are deleted.

## Restart (after a container restart, or to resume)
```sh
cd /home/user/kinetiq && git pull --rebase   # the kit
ls /home/user/kinetiq-render-out/bpyenv/bin/python || render/setup.sh   # only if the render dir was wiped
setsid nohup render/queue-nov3.sh >> /home/user/kinetiq-render-out/logs/queue-nov3.log 2>&1 &
```
Everything on disk is skipped: stills by their `-full.png`, swivel frames by `fNNN.png`, exports, patches and masters
pushes by their line in `logs/queue-nov3.done`. A frame or still cut off mid-render is simply rendered again. To redo an
export, delete its line from the `.done` file. `ONLY="p2a"` runs one item. Never run two queues: check
`ps aux | grep queue-nov3` first (kill by PID, never `pkill -f`).

## Progress
`grep -E "ITEM|STILL |SEQ-|PATCH|EXPORT|MASTERS|ERROR|SKIP|CROP" /home/user/kinetiq-render-out/logs/queue-nov3.log`

## Status (2026-11-04 10:30 UTC; the log has the live state)
- Kit: Naked butt, light sweep, cap-region patches, wrapped bores, 5K ladders: committed (fa5fa41 .. d23295a).
  Naked proofs in both feels: `out/naked/crop_c.png`, `crop_p.png` (white 3K / black 12K end, Q engraved, no cap).
- Done: K08 Naked (cfc7dbd); p1a K01 Naked Command (beam 5120 x 2880 spp 64: 69 min; portrait 2160: 28-34 min;
  exported 87ad2ab, masters stills/K01).
- The container restarted about 17:20 UTC on 3 Nov, during the K01 Naked Pace beam (25 of ~55 min); nothing ran until
  both queues were restarted at 02:12 UTC on 4 Nov (same commands as above). The Pace beam started again from zero.
- ETAs from 02:12 (4 cores, one Blender): p1a Pace ~1 h 45 (beam ~70 min, portrait ~30) -> ~04:00; p1b ten cap-region
  patches ~1-2 h -> ~05:45; p1c six whole twins (K09 x4, K10 x2) ~2 h -> ~07:45; p2a K01 Command grip: stills ~1 h 45,
  portrait swivel 35 x ~3.5 min ~2 h, desktop swivel 35 x ~12 min (5120, spp 16; 4x the 2560 frames' ~3 min) ~7 h,
  exports at the end -> ~18:30 on 4 Nov; p2b Command Naked ~9 h -> ~03:30 on 5 Nov; p2c/p2d Pace ~11 h + ~9 h.
  Then queue-nov3b (p4 K15, p3 K05, p5a-p5g), about an hour per 5K still.
- 4 Nov: p1a Pace (beam 50 min, portrait 18 min) exported c99170e; p1b exported e3f8ee7 (only the K11 pairs pasted,
  every other cap patch was refused by the ring check and re-rendered whole, 4-25 min each); p1c exported 1e69436
  (K09 gallery 11 min, card 8 min; K10 50 min Command, 29 min Pace). p2a stills: beam 5120 44 min, portrait 19 min.
  08:31: the `seq()` shadowing bug (RENDER_NOTES) ended the first swivel after one frame; fixed with `command seq`,
  both queues restarted at 08:31. Measured: phone frames 170-190 s (K01 Command phone swivel done 10:17, 36/36),
  5120 desktop frames 270-280 s (the 0.46 x 0.81 crop region only). ETAs: p2a desktop ~12:55, its masters + exports
  ~13:20; p2b (Command Naked) ~17:50; p2c (Pace stills + swivels) ~23:30; p2d ~04:00 on 5 Nov; then queue-nov3b.
- Never edit a queue script or export_push.sh while it runs: bash reads scripts as it goes (an edit broke the first
  K01 export mid-run; re-run by hand). Kill the waiting queue, edit, restart. `run_locked` starts Blender under
  `setsid`, so killing a queue leaves its current render running (and holding the lock) until it ends: kill that
  Blender too (by PID) when you mean to stop everything.

## queue-nov3b (P3, P4, P5): starts when queue-nov3.sh ends
`render/queue-nov3b.sh` (functions in `render/queue_lib.sh`) waits for queue-nov3.sh, then: p4 K15 both feels at 5120
with wrapped bores (`KQ_HOLE_UV=cyl`); p3 K05 v7 at 5120, both feels and Naked (its look from `render/notes/k05-v7.args`,
read when the item starts; without the file p3 is skipped); P5 at 5120 into `out/final/v5k/` (link-masters.sh prefers
it): p5a K14, p5b K04, p5c K16 (halves 2560 x 2880), p5d K17, p5e K06 grip + Naked, p5f K07 and K08 grip + Naked.
Not queued yet: K02 (its still must ship with a new-canon swivel), K03/K03b, K09/K10/K11/K12/K13 at 5K.
```sh
setsid nohup render/queue-nov3b.sh >> /home/user/kinetiq-render-out/logs/queue-nov3b.log 2>&1 &
```

## Cloud side: exporting a Mac item (2026-11-04, p2b to p2d)
The Mac (notes/mac-handoff.md) pushes masters to `evhg/kinetiq-masters` and a `STATUS-mac.md` line; the cloud exports.
1. Fetch only what the item names (a blobless sparse clone; `git sparse-checkout add '/stills/K01/<name>-*'`, or
   `git show HEAD:<path> > <file>` for single stills). Disk: a 5120 swivel is ~0.9 GB of region masters and ~2.1 GB
   rebuilt; the container has ~16 GB free, so export one swivel and delete its frames before the next.
2. Stills: copy the finals into `$KQ_RENDER_OUT/out/final/` under their queue names (they replace the cloud's of the
   same name), `render/link-masters.sh`, then `node scripts/stills.mjs $KQ_RENDER_OUT/masters <ids>` (export_push.sh's
   ids for the item; never two stills.mjs or two sequence.mjs runs at once: each rewrites its manifest at the end).
3. Swivels: `$PY render/seq_rebuild.py <masters>/sequences/<name> <dir>/<name> k 4` for k = 0..3 in parallel, check
   frame 0 against the `-full` still (export-swivels.md step 2), then `sequence.mjs` with export_push.sh's options
   (`*-phone`: `--formats=avif,webp --avif-quality=50`; desktop: `--formats=avif,webp`). Phone ~9 min, a 5120 desktop
   ~18 min per sequence on 4 cores.
4. `og.jpg` is written from the Command grip K01-full only (stills.mjs skips `-pace` and `-nogrip` ids since
   2026-11-04: the p2c export had overwritten it with the Pace face).

## Cloud export of the Mac's queue-nov3b (2026-11-04, 17:30-21:00 UTC)
- Exported, each looked at against the live export at 5K display size first: p4 K15 (wrapped bores: the twill runs
  over the lip and down the wall as one lining; Pace bores read black as before), p3 K05 v7 (both feels and the four
  Naked twins, desktop and phone; cut from the 16-bit `-master.png`: desktop = its top 2880 rows, phone = the box
  (146, 486, 4828 x 2715) turned 90 deg CCW, found by matching the Mac's 8-bit crops, identical in the high byte),
  p5a K14, p5b K04, p5c K16, p5d K17, p5e K06, p5f K07/K08, p5g K02 (stills and the four swivels), and K03-base
  (REQUEST 14:09Z; link-masters.sh maps it). Nothing refused.
- K02 swivels: the masters repo holds only the desktop sets (seq_masters layout); `seq_rebuild.py` (4 shards) rebuilds
  them, the phone sets are the desktop frames turned 90 deg CCW at 16 bits (sharp `rotate(270)`, as K02-edge-line.py
  `--phone`), Command and Naked Command phone sets keep 45 of 60 frames. A 60-frame 5120 rebuild is 1.3 GB: one
  sequence per lane, frames deleted once exported. Two `sequence.mjs` runs at once only with `--out` for one of them
  (each rewrites the manifest it read at its start), merged by hand afterwards.

## Cloud export of K11+k789-naked-handles (2026-11-06, Release 9)
- The Mac's 2026-11-05 15:17-15:27Z lines (K08-naked-pace-handle; K11+k789-naked-handles: K11, K07, K09): masters by
  `git show origin/main:<path>` into `in-mac/r9/`, installed under their queue names (K07/K08 in `final/v5k/`, K09/K11
  in `final/`; the replaced finals kept in `final/pre-r9/`), `link-masters.sh`, one `stills.mjs` run for the 11 ids
  (K07-nogrip, K08-nogrip, K09-nogrip{,-pace}, K09-nogrip-card{,-pace}, K11-nogrip-{command,pace,command-pace},
  K11-nogrip-single{,-pace}). K09's card twin is the `--hover-mix` composite (`-card-nogrip.png`), never `-check`/`-hover`.
- K11's Naked masters are now 5120 x 2880 (were 3200): wide to 5120, the card crop 2304 x 2880 exported to 1440 with the
  1170 rung; K09's card twins gain the 1170 rung too. The grip-on K11/K09 stay on the 1.5 mm edge, and so do their twins.
- Looked at before export, against the live files and K01 Naked: weave on the Command handle, the canon butt, Q in
  the carbon, K01's two hairlines; the Pace staircase, bracket and the collar band are gone. Pace's handle reads as
  black lacquer at card size (as K01 Naked Pace does): its 12K weave shows only in the hairlines.

## Cloud export of the Mac's 2026-11-06 lines (Release 10)
- STATUS-mac 11:54Z-12:14Z (K05-command-fix, wider-5k-masters K04/K17, K03-5k-and-K03b): blobs by `git show
  origin/main:<path>` (the masters clone has `gc.auto 0`: an auto repack of its 4.6 GB pack nearly filled the disk).
- K05 v7c: `-master-a` over `-master-b` = 5760 x 3601 RGBA16; desktop = rows 0-3239, phone = the box (165, 546,
  5430 x 3055) turned 90 deg CCW, both found by matching the Mac's 8-bit crops (mean |high byte - 8 bit| 0.34-0.38),
  written as 16-bit RGB into `final/v5k/` under the queue names (replacing v7; v7 is in the masters repo's history).
- K04 6400 x 3600 and K17 5760 x 3240 into `final/v5k/`; K03 base and `-line`, K03b `-line` into `final/`
  (link-masters.sh maps K03 / K03b-tubular to `-line`). Wide crops still export to 5120 (DESIGN.md, Release 10).
