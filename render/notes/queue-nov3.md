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

## Status
Updated by the render owner as items finish (see the log for the live state).

## queue-nov3b (P3, P4, P5): starts when queue-nov3.sh ends
`render/queue-nov3b.sh` (functions in `render/queue_lib.sh`) waits for queue-nov3.sh, then: p4 K15 both feels at 5120
with wrapped bores (`KQ_HOLE_UV=cyl`); p3 K05 v7 at 5120, both feels and Naked (its look from `render/notes/k05-v7.args`,
read when the item starts; without the file p3 is skipped); P5 at 5120 into `out/final/v5k/` (link-masters.sh prefers
it): p5a K14, p5b K04, p5c K16 (halves 2560 x 2880), p5d K17, p5e K06 grip + Naked, p5f K07 and K08 grip + Naked.
Not queued yet: K02 (its still must ship with a new-canon swivel), K03/K03b, K09/K10/K11/K12/K13 at 5K.
```sh
setsid nohup render/queue-nov3b.sh >> /home/user/kinetiq-render-out/logs/queue-nov3b.log 2>&1 &
```
