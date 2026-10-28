> Recovered 2026-10-28 from the session transcripts (see ../README.md). Paths in these notes are the old scratchpad
> layout: `../bpyenv/bin/python` is now `$KQ_RENDER_OUT/bpyenv/bin/python`, `out/` is `$KQ_RENDER_OUT/out/`,
> `../renders4/canon.md` is `notes/canon.md`, and the fonts, `tex/`, `shots/k04_tex2/` and `shots/k04_bake/` live in
> `$KQ_RENDER_OUT/assets/` (render/kqpaths.py). Run shots from `render/`.

# KINETIQ render kit: notes for shot authors

Folder: this directory (`.../scratchpad/blender`). Python with Blender: `../bpyenv/bin/python` (bpy 4.2, Cycles CPU, 4 cores shared).
Run a shot: `cd <this dir> && ../bpyenv/bin/python shots/K01_hero.py --w 960 --h 540 --spp 32 --out K01_preview`.
Outputs go to `out/` (previews) and `out/final/` (finals). View PNGs with the Read tool.

## Modules
- `racket.py`
  - `build_racket(name, kind="3k"|"12k", etch=True, serial="SWISS MADE   No. 0001", face_print=False, flow_holes=None)` returns a parent Empty.
    Model space: metres, face in XY plane, +Z out of the front face, head up (+Y), handle down (-Y).
    Head 260.1 mm wide (X), 310 mm tall (Y), 38.0 mm thick (Z); handle + cap go down to about y = -0.30.
  - `build_head(name, inset=0.0)`: watertight head only (about 380k faces; booleans on it take minutes).
  - `holes()` returns the 42 hole centres in shape units (multiply by `racket.U` = 0.1 for metres). `HOLE_R` = 0.062 units (6.2 mm radius).
  - Materials: `mat_carbon(name, tow_mm, kind="3k"|"12k", coat_rough, flow_holes=[(x_m, y_m, r_m), ...])`, `mat_grip()`, `mat_metal(name, color, rough)`, `mat_basic(...)`.
  - `etch_side(head, text, y_units, size, side=±1, mat=...)`: laser-etched text on the side wall.
- `studio.py`: `reset()`, `settings(w, h, spp)`, `area_light(...)`, `spot_light(...)`, `camera(loc, target, lens, fstop, shift)`, `floor()`, `backdrop()`, `render(name)` (writes `out/<name>.png`), `aim(obj, target)`.
- `look_c.py`: `softbox(name, loc, (w, h), strength, target, gradient=True, color=...)` = emissive plane, invisible to camera, visible in reflections. This is the main lighting tool.

## What we learned (follow these)
1. Black lacquered carbon looks expensive only with **reflection-only lighting**: no big front lights (they turn carbon flat grey). Put softboxes where the surface *reflects them toward the camera*. Compute the mirror direction: r = 2(n·v)n − v for face normal n and view vector v, and place the softbox along r. Slide a narrow gradient softbox so its **falloff edge** crosses the face: that gives the luxurious diagonal light sweep (see `out/side_wn.png`, the current best look).
2. Light energies are small. Area lights 10–40 W at ~1 m. Emissive softbox strength 2–8 for gradients, 10–25 for thin rim strips. Spot for a floor beam about 1,400 W at 4.5 m, 3° cone. If a black grip renders grey, everything is overexposed.
3. Rim strips (5–8 cm wide, 1–2 m long) behind the subject trace the frame edge as a thin bright line. The ember red line in the art plan is a rim strip with colour (1.0, 0.23, 0.12).
4. Weave is only visible when a tow spans several pixels: 3K tows are 2.6 mm. Full-racket shots show a sheen, not a pattern; macros and side walls show the pattern clearly (`out/etch_test.png`).
5. Multiple rackets: build one with `build_racket`, then duplicate every child object with `obj.copy()` (sharing mesh data) and re-parent to a new Empty. Do NOT call `build_racket` five times (slow, memory).
6. Hole holes: look through them and you see what is behind: keep what is behind dark, or deliberately put a warm emitter behind (a "bore glow").
7. View transform is AgX "Punchy" (set in `studio.reset`). World is black. Grade backgrounds to near `#060607`, never flat 0 everywhere: use a backdrop plane or a large very dim gradient softbox for a graphite lift behind the subject.
8. Previews: ≤ 960 px wide, ≤ 48 spp (about 15–45 s). Finals: 2560×1440 (or the size in your brief), `--spp 160` with adaptive sampling (already on) and OIDN denoise.
9. Never render: people, signatures, logos of other brands, Tesla assets, middle-dot strings like "A · B". Weights, if any text shows one, always with a decimal ("355.0 g").
10. DOF: `studio.camera(..., fstop=...)` uses distance to target as focus. Keep f/8+ unless it's a macro.

## Quality bar
The owner's words: "every asset needs to be perceived by a human as expensive and high precision"; "the big animated racket looked like an unserious toy and a cheap render".
Compare your previews to these references (Read them):
- `../tesla-small/Roadster-01-Hero-Desktop.jpg` (hero beam), `../tesla-small/Roadster-03-Carousel-Slide-1-Desktop.jpg` (low-key studio), `../tesla-small/Roadster-07-Augments-Desktop.jpg` (light lines), `../tesla-small/Roadster-08-End-Desktop.jpg`.
Iterate until your image could sit on that page. Typical fixes: darker overall with fewer, sharper highlights; a single crisp rim line; a graphite lift behind the subject so it's not 90% pure black; no grey wash on the carbon; straight verticals; generous negative space where the page puts text.

## FILL RULE (owner requirement, added 11:40; read this before finals)
The owner complained the old site was "90% black" and that wide screens looked empty. The website harness now FAILS any
screen where more than 40% of pixels are flat black (luma <= 12 of 255), fewer than 8% are lit (luma >= 40), or a
flat-black vertical strip spans a quarter of the width. Full-bleed renders are most of what those screens show, so:
- Lift the background: a graphite backdrop or floor gradient (around luma 14-30, e.g. #121214 at the edges up to
  #26262b behind the subject), never pure black edges. Keep it low-key and expensive: soft, smooth, no visible banding.
- Let the subject be BIG: the racket (or object) should span a good part of the frame height in the central 16:10 area.
- Add lit area: floor sheen, a beam, rim lines, a lit backdrop band, reflections on a glossy floor.
- Check every preview and final: `../bpyenv/bin/python fillcheck.py out/<file>.png`. Target for a render on its own:
  dark <= 40% and lit >= 6% in the 16:10 crop (page text adds the rest). Do not sacrifice the luxury look: a lifted
  graphite studio with crisp highlights, like the Tesla Roadster carousel slides, not a grey wash.

## THE CANONICAL RACKET (2026-10-22): use `shots/kq_canon.py` in every shot
`root, P = kq_canon.build_racket("KQ", feel="command"|"pace", serial="KQ-000427")`; `kq_canon.clone(root, "KQ2", serial="KQ-000428")`.
455.0 mm, 38.0 mm, crown of 8 + 34 holes, one-piece neck into K05's overgrip and satin cap with an engraved Q, WHITE 3K
twill (Command) / black 12K (Pace) folding over the 1.5 mm edge, laser-frosted throat serial (graphite on white). Do not build racket.py / k12 / k789 rackets
any more. How to switch, part names, lighting notes: `../renders4/canon.md`. Proof sheet: `out/canon/canon_sheet.png`.

## OWNER OVERRIDE (2026-10-22, later than the render audit; it overrides the audit and any group brief)
- Throat marks: the pair edition is a premium, numbered run of 500 sets that ships first. Its rackets (K11 command and
  pace, both rackets, and the K10 throat macro) carry the SET NUMBER "027/500" on the throat, exactly as the earlier
  K10/K11 did (same face, size and position as K10), not "KQ-000427". Every other rule of the canonical racket stands.
- Single-racket shots (K01, K02, K05, K06, K07, K08, K12) carry no set number; a small KQ-000427 serial is optional.
- Founders set (K09): keep the plaque "No. 01 / 10".

## OWNER UPDATE (2026-10-22, later): Command is WHITE carbon
- Command = white 3K twill carbon with the weave clearly visible; Pace = black 12K. Every shot that does not name a
  feel shows Command (white). kq_canon.py builds it (feel="command").
- The company logo is the Q (owner, 2026-10-22): the butt cap's engraved mark is a "Q", not a "K" (same size, depth and
  finish as the K was). Change it in kq_canon.py.
- ONE Q (hero group critic, 2026-10-22, later): the cap's Q is now the site icon's drawing (ring + diagonal tail,
  kinetiq src/app/icon.svg), engraved (graphite floor + bright-cut chamfer), not the Archivo glyph; the neck twill runs
  straight down the handle (no fish-scale arcs). Both in kq_canon.py; see canon.md (Cap, Neck). Proofs re-rendered.
- DONE in kq_canon.py (2026-10-22): feel="command" builds white twill (`mat_white`), the cap mark is a Q. White carbon
  needs real diffuse light (a soft spot pool or key, a weak fill), not the reflection-only studio of black carbon: see
  "White Command" in `../renders4/canon.md`. `mat_opts={"white": 0}` gives back the old black Command.

## PACE 12K v5 and neutral rims (2026-10-23, site review rounds 1 and 3)
- `kq_canon.PACE` is now the v5 "fibre" 12K: tapes within a few percent of albedo, one uniform coat, the checker only in
  the fibres' sheen direction, with a fine fibre normal, roughness streaks and a slight crimp per tape (canon.md, Pace).
  K08 and K11-pace both use it (`PACE_V4=1` in either shot, or `mat_opts=C.PACE_V4`, gives the old grid-like 12K back).
- No ember on any racket: Pace's rim is Command's neutral 6500 K, dimmed to a hairline (K08 `RIM_PACE`, K11 `P_RIM`).
  The only ember on the page is the K05 / K07 lasers.
- Checks: `shots/pace_probe.py` + `pace_metrics.py` (tile step, high-pass, rim |R-G|, saturated-red count), `pace_diff.py`
  (K08's Command half unchanged). Tuning runs: `--pace key=value,...` on K08-feel-pair.py / K11-pair.py.

## PACE v6 (2026-10-23, review round 6)
- `kq_canon.PACE` is v6 (narrow Beckmann fibre lobes across the fibres, analytic 30 um arch, no tile creases); K08 and
  K11 dim their Pace band (P_BAND_S 9 / 10) and run the weave card without a floor. Details: canon.md "Pace v6". Dev
  previews and harness: `out/pace6/` (`pv.sh NAME PACE_KV K08_SET K11_SET`). `shots/pace_raw.py` renders any shot
  with the denoiser off.

## Release 2 Pace versions + K13 (2026-10-23)
- `--feel pace` (default Command unchanged; tiny-preview diff vs the `*.v6-prepaceR2.bak` scripts = 0 for K03, K03b, K04):
  - K03 / K03b (`k03s_lib.pace_on`, `mat_pace_coupon`: canon `mat_pace` relinked to the coupon's fabric coords; v4 black
    laminate and rig + `k03s_rig.pace_lights`, a 1 x 1 m weave card 30 deg above the top's mirror ray, strength 14;
    indirect clamp 4). Finals: `PYTHONHASHSEED=0 ... --feel pace --w 3200 --h 1800 --spp 320 --both --out
    final/K03-section-cut-pace` (and K03b), then `k03s_line.py out/k03r/v4/final/K03-line-mask2.png <base> <full>
    --halo 0.9 --sigma 5 --white 0`. Same camera/geometry as Command K03, so SealedCoreTrace still registers.
  - K04 (`pace_face`: canon `mat_pace` on the WARPED weave coords, tangent from grad(warp y); `pace_sleeve` lips/bores;
    `PACE_DEFAULTS`: weave card el 68 az 25 strength 20 whose soft lower edge crosses the face's mirror rays, sheen off,
    lip line 40). Pace v6 tapes only show near the coat's mirror direction: cards far off-mirror light nothing.
- K13-layup (`shots/K13-layup.py`, DEFAULTS in the file): floating 2.0 mm laminate, cool slit on the cut's mirror rays.
  v1 final read as render noise at page size (full-contrast 3 px fibre ends): `fib_con` 0.30 pulls ends to the ply mean.
