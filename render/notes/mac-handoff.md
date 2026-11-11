# Mac render node: hand-off for a Claude Code session on Erik's MacBook (M3 Max)

Owner decision (2026-11-04): from now on every Blender render, and anything else that is 20-40x faster on this Mac than
on the 4-core cloud container, runs on Erik's M3 Max. The cloud session keeps the site, exports (`scripts/stills.mjs`,
`scripts/sequence.mjs`), checks and releases. A cloud session cannot use this Mac's folders directly (not offered to
cloud sessions for this account), so a Claude Code session running ON the Mac does the rendering and hands results
back through GitHub.

You are that Mac session. Work in `~/kinetiq-render`. Read the repo's `CLAUDE.md` (its rules apply: public repo, never
commit masters, secrets, the factory's name, town or patents) and `render/README.md`, `render/notes/canon.md`,
`render/notes/RENDER_NOTES.md`, `render/notes/queue-nov3.md` before rendering.

## Roles and hand-off
- **Mac (you):** render. Push masters (16-bit PNG finals, swivel frames in the existing `seq_masters.py` layout) to the
  PRIVATE repo `evhg/kinetiq-masters` with `render/masters_push.sh`. Push kit changes (render/ only) to the branch
  `mac/render` of `evhg/kinetiq` (never to `main`; the cloud merges it).
- **Status for the cloud:** after every finished item, append one line to `STATUS-mac.md` at the root of
  `evhg/kinetiq-masters` and push it: `<UTC time> <item> <ids/paths in the masters repo> <render time> <device> <notes>`.
  The cloud session polls that file, exports the stills and sequences into the site, checks them and releases.
- Do not run `scripts/stills.mjs`, `sequence.mjs`, the site build or any release here.

## 1. Set up (once)
1. `mkdir -p ~/kinetiq-render && cd ~/kinetiq-render`. Check `git --version`; if macOS asks to install the command
   line tools, let Erik click Install.
2. GitHub access for the private masters repo: use `gh auth login` (install `gh` with Homebrew if Homebrew exists,
   otherwise the official macOS pkg) or HTTPS with the macOS keychain. Erik signs in once in the browser. Never print
   or store a token in a file.
3. Clone:
   `git clone -b wip/owner-update https://github.com/evhg/kinetiq.git` and
   `git clone --filter=blob:none https://github.com/evhg/kinetiq-masters.git` (blobless: about 12 GB otherwise).
   Then `cd kinetiq && git switch -c mac/render`.
4. Python 3.11 + bpy 4.2 (the kit's pins, `render/requirements.txt`; bpy 4.2 wheels are cp311): install `uv` without
   admin rights (`curl -LsSf https://astral.sh/uv/install.sh | sh`), then
   `export KQ_RENDER_OUT=~/kinetiq-render/out` and
   `uv venv -p 3.11 $KQ_RENDER_OUT/bpyenv && uv pip install --python $KQ_RENDER_OUT/bpyenv/bin/python -r render/requirements.txt`.
   If bpy 4.2.0 has no macOS arm64 wheel, stop and report: a different Blender version changes the look.
5. Derived assets: `PY311=$KQ_RENDER_OUT/bpyenv/bin/python render/setup.sh` (fonts, textures, K04 bakes into
   `$KQ_RENDER_OUT/assets`). Link the masters the queues expect with `render/link-masters.sh` (it reads `KQ_RENDER_OUT`;
   point it at `~/kinetiq-render/kinetiq-masters`, checking out only the folders an item needs:
   `git sparse-checkout` / `git checkout main -- stills/K01` to keep the disk small).
6. Paths: the kit defaults to `/home/user/...`. Always export `KQ_RENDER_OUT=~/kinetiq-render/out`,
   `KQ_LOCK=~/kinetiq-render/render.lock` and `RENDER_ROOT=~/kinetiq-render/kinetiq/render` before running anything,
   and replace any remaining hard-coded `/home/user` path you hit with an env-var default (commit to `mac/render`).
7. **GPU (Metal):** the kit renders on the CPU today. Add an opt-in `KQ_DEVICE=METAL` (default unchanged, so the
   cloud keeps working): in the one place every shot sets up Cycles (find where `scene.cycles` samples/denoiser are
   set; `studio.py`/`kq_canon.py`), when `KQ_DEVICE=METAL` set
   `prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()`,
   enable every Metal device (and leave the CPU device off unless it measures faster), and `scene.cycles.device = "GPU"`.
   Keep samples, seeds, denoiser (OIDN) and every look setting identical. Commit to `mac/render`.
8. Keep the Mac awake while rendering: run long jobs under `caffeinate -dimsu`, on power.

## 2. Prove it (before any real render)
- Render the same still on this Mac with `KQ_DEVICE=METAL` and on the Mac CPU, at the queue's real settings (take one
  K01 portrait from `render/notes/queue-nov3.md` at 2160x3840 spp 48, or a smaller shot if that is too long), and time
  both. Compare the Metal result with the cloud master in `kinetiq-masters/stills/<id>/` (mean luma difference and
  `render/fillcheck.py`; they should differ only by noise). Write the times and the difference to `STATUS-mac.md`.
- If Metal and CPU differ visibly (not just noise), stop and report.

## 3. The queue (in this order)
From `render/notes/queue-nov3.md` (read it in full; it has the exact commands and the reasons):
1. **p2b** K01 Command Naked: re-render its stills HERE first (beam 5120x2880 spp 64 base/full/finale, portrait
   2160x3840 spp 48), then its swivels (portrait 2160 spp 24, desktop 5120 spp 16, 36 frames, 0-35 deg, the light band
   crossing the head). A still and its swivel always come from the same machine and device, so frame 0 matches the
   still the page shows.
2. **p2c** K01 Pace grip stills + swivels; **p2d** K01 Pace Naked stills + swivels.
3. **queue-nov3b:** p4 K15 at 5120, both feels, with wrapped bores (`KQ_HOLE_UV=cyl`); p3 K05 v7 at 5120, both feels
   and Naked (look in `render/notes/k05-v7.args`), including the laser layer; then p5a-p5g as listed there.
Run the queue scripts with the env vars above (`ONLY="p2b"` etc.), one Blender at a time, resumable from disk.
Skip their export steps (`export_push.sh` is the cloud's job); keep their masters pushes.
After each item: push masters, append to `STATUS-mac.md`, push.

## 4. Anything else 20-40x faster here
If the cloud asks (through `STATUS-mac.md` requests in the masters repo, lines starting `REQUEST`), run it here:
preview renders for look decisions, image comparisons on full-size masters, heavy image processing. Answer by
pushing results and a `DONE <request>` line.

## 5. Exports on the Mac (owner, 2026-11-08: "moving the image encoding to Erik's Mac")
- Since the grip-edge batch (mac/exports 96d767f2, Release 14) the Mac also EXPORTS what it renders: the AVIF/WebP
  ladders (`scripts/stills.mjs`) and swivel frames (`render/seq_rebuild.py`, then `scripts/sequence.mjs`), 20-40x faster
  than the 4-core cloud. The cloud keeps the review, the merge, the site checks and every release.
- Set-up: a worktree `~/kinetiq-render/kinetiq-exports` on branch `mac/exports`; Node 22 (Homebrew node@22, keg-only);
  `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci` (sharp 0.35.5 from the lockfile; never npm install/update).
- Parity (2026-11-08, K04-base): WebP byte-identical to the cloud's; AVIF as faithful to the pre-encode pixels (arm64
  aom takes other decisions), +2 to +5 % bytes at the smallest widths. Bounds for later checks: mean abs diff vs a cloud
  encode <= 0.7/255, size within +6 %.
- Every batch: `render/mac_export.sh` rebases mac/exports on the latest origin/wip/owner-update (the cloud owns
  stills.json crops and q values, code and docs: never edit them on the Mac), exports only the batch's ids, commits ONLY
  `public/stills/**` and `src/content/stills.generated.json`, refuses to push on any *.png/*.exr, any file over 5 MB or
  any other path, pushes `mac/exports` (never main, never wip/owner-update), then a STATUS line
  `EXPORTED <item> mac/exports@<sha> <ids>`. The cloud fast-forwards wip onto it after review.
- Previews and concept renders that are not for the site (e.g. the Edge to edge concepts) push masters only, no export.
