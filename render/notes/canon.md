> Recovered 2026-10-28 (was `scratchpad/renders4/canon.md`); companion to `RENDER_NOTES.md`.

# The canonical KINETIQ racket: `shots/kq_canon.py`

One module builds the racket for every shot (render audit 2026-10-22, section 4). No shot builds its own racket any more.

**Update (owner, 2026-10-22, after the canon was built): Command is WHITE carbon, and the logo is the Q.**
`feel="command"` now builds white 3K twill with the weave clearly visible; Pace stays black 12K. Every shot that does not
name a feel shows Command (white); Pace (black) appears only where Pace is chosen or compared. The butt cap's engraved
mark is a Q (same font, size, depth and finish as the K was). Geometry, handle, rim, serial and pair marks are unchanged.
See "White Command" below; white needs different light from black (lighting note 8).

- Module: `blender/shots/kq_canon.py`.
- Proof script: `blender/shots/canon_test.py`.
- Proof renders: `blender/out/canon/`. The contact sheet is `blender/out/canon/canon_sheet.png`.

## Switching a shot (the few lines)

```python
import kq_canon as C                       # shots/ is already on sys.path in every shot script

root, P = C.build_racket("KQ", feel="command", serial="KQ-000427")   # P: part name -> object
C.pose(root, (0, 0, 1.0), yaw_deg=28, tilt_deg=90)                  # stand it up (same convention as k789_lib.pose)
r2, P2 = C.clone(root, "KQ2", serial="KQ-000428")                    # a second racket: shared meshes, its own serial
C.pose(r2, (0.19, 0.07, 1.035), yaw_deg=28, tilt_deg=90)

L.link_only(face_light, C.objs(P, "face", "neck", "holes"), "face_recv")   # light linking by part
```

Then delete the shot's own head, handle, grip, cap, collar, wordmark and serial code, and its carbon materials.

### Old part names

An old shot's light-linking lists can be kept as they are with `C.objs(P, *old_names, style=...)`:

| Old builder | Old part names | Canon parts |
|---|---|---|
| `k12_lib.build_racket_rounded` (K01, K02) | `outer`, `bevel`, `throat`, `inner`, `grip`, `collar`, `cap` | `style="k12"`: outer = face + back + wall + neck; bevel = rim; throat = throat + bridgewall; inner = holes; collar = nothing; cap = cap + capmark |
| `k789_lib.make_racket` (K07, K08, K09, K11) | `L.part(root, "_Head" / "HeadBevel" / "_HeadInner" / "_grip" / "_cap")` | `style="k789"`; `L.part(root, "_grip")` and `"_cap"` still work as they are |
| `k10_lib.build_head_k10` (K10) | `face`, `rim`, `neck`, `holes`, `bridgewall`, `thrNN` | `build_racket(..., throat_segs=k10_lib.THROAT_SEGS)` gives the same thrNN split; `style="k10"`: rim = rim + wall |

Example: `C.objs(P, "outer", "bevel", style="k12")`. A few groups also work without a style: `"head"`, `"handle"` (grip, cap and capmark) and `"all"`.

### Other changes when switching

- **K06** (`racket.build_racket`), **K05** (`build_kq`) and **K01**/**K02**: swap the build call. Your lights then link to canon parts.
- **The butt is now at y = −0.300** (it was −0.305 in k789 and lower in racket.py), and nothing is left of the collar. Re-check any framing solver that measures the old parts by name.
- **Multiples:** build one racket and `clone` the rest, as before. Lights linked to a part list must include each clone's parts: use `C.objs(P2, ...)`.

## What the canon racket is

Model space is the same as `racket.py`: metres, face in the XY plane, +Z out of the **front** face, head up. The root Empty sits at the head centre. Pose the root, never the parts.

### Measured (asserted by `C.measure(root)` and the self-test)

| | Spec | Measured |
|---|---|---|
| Length | 455.0 mm | 455.00 mm (tip y = +0.155, butt y = −0.300) |
| Width | 260.0 mm (the FIP maximum, as `racket-shape.ts`) | 260.12 mm (outline tessellation; 0.5 px at 3200 px) |
| Thickness | 38.0 mm | 38.00 mm |
| Holes | 42 | 42, of which 8 are crown holes (14.0 mm) |

### Holes

- `holes_canon()` gives a crown of 8 (14.0 mm) along the top, and 34 holes (12.4 mm) below in rows A B A C A C A C A B A.
- The list is asserted equal to the audit's hand-off list, so the site's `racket-shape.ts` can take the same 42.
- **Sealed core:** every bore is lined by the carbon shell. The 0.8 mm gloss lip carries the twill, and the lining darkens with depth. Each hole therefore reads as a through-hole: graphite shows through it, with one crescent on its lip.

### Neck (this is the ferrule; there is no separate part)

- The head flows into the handle as one carbon piece.
- **Width** goes from 47 to 33 mm over y = −0.146 to −0.176, with an 18 mm concave fillet into the V.
- **Thickness** goes from 38 to 29 mm (`NECK_TAPER`).
- **The rounded edge grows from 1.5 to 12 mm** (`NECK_ROUND`). The crisp frame edge softens into the handle's 33.0 × 29.0 mm section, and the twill folds round it.
- About 25 mm of bare carbon shows between the frame and the grip.
- **Neck twill** (hero group critic, 2026-10-22): the fold UVs used to offset each wall point along the outline normal,
  which folds over (fish-scale arcs) where the normal turns faster than the ~40 mm wall profile allows, in the 18 mm
  concave fillet into the V. From y = -0.095 to -0.150 (`NECK_UV`) the fold direction now blends to the racket's cross
  axis, so the tows run straight down the neck (u round the section, v = y). `head_kw={"neck_uv": None}` restores the old UVs.
- The core runs on under the grip and ends there, hidden. There is no flat end face, no collar and no joint.

### Grip

K05's overgrip, on the same section as the neck:

- **Size:** 34.0 × 30.0 mm over one layer of tape.
- **Wrap:** a real helical wrap at a 27 mm pitch. Each seam has an overlap step and the tape carries perforation rows.
- **Finishing band:** 11 mm at the top. Its cut edge stands 0.3 mm proud of the neck.
- **Span:** y = −0.174 to −0.2842.
- **Colour:** neutral black, not brown.

### Cap

- **Profile:** K05's profile moved up 7.3 mm (y = −0.2817 to −0.3000) and scaled 0.94. At most it measures 37.1 × 32.8 mm, so it stands about 1.5 mm proud of the grip and follows the grip's shape.
- **Finish:** satin black anodised, with one fine groove. No chamfer ring and no chrome.
- **Mark:** an engraved **Q**, the company logo (owner, 2026-10-22; part `capmark`). **One drawing everywhere** (hero group
  critic, 2026-10-22): the cap's Q is the site icon's Q (kinetiq `src/app/icon.svg`, commit 7d00d87): a geometric ring
  (ellipse rx 16 / ry 15, stroke 6 in the icon's 64 grid) with a diagonal tail (stroke 6, butt ends) from inside the
  counter across the bowl at 4-5 o'clock (`Q_ICON`, `q_outline()`). It is not the Archivo glyph any more. Size: the old
  K's cap height (ring 2.9 mm tall, 3.2 mm wide with the tail), centred where the K sat (y = -0.2925). Finish: an
  engraving, not a bright inlay: material 0 is the satin graphite floor (`mat_engraving_floor`), material 1 a 0.11 mm
  bright-cut chamfer round every edge with its normals sloping into the cut (`Q_MARK`). At hero scale (5-6 px) it reads
  as a quiet cut mark, never as a white ring or a rivet. `build_racket(..., mark_az=deg)` turns the mark round the handle
  axis so it faces a yawed camera (K01 uses its 12 degree yaw). `text="K"` (or any glyph) still builds the old font mark.

### Weave

**Command** is WHITE carbon and the default for every shot that names no feel (owner, 2026-10-22):

- `mat_white` (in `kq_canon.py`): K10's baked 3K twill maps (`k04_tex2`: the same 2.6 mm tows, crevices, fibre
  directions and relief), read as white fibre in clear resin. Settings: `COMMAND_WHITE`.
- **Fibre:** a dielectric white tow, linear albedo about 0.70 with a whisper of warmth (`tint`), so it reads as white
  fibre, not cold plastic. No metal.
- **Why the twill reads in shade:** the baked tow-to-tow tone and crevice shadow are kept (`alb_k` 0.65), the two tow
  directions differ by 14 % in tone (`dir_tone`: fibres scatter more across their axis than along it), fibre-bundle
  streaks run along each tow, and the tow relief is a bump (0.30) that any raking light picks out.
- **Why it reads in light:** an anisotropic fibre sheen (0.75) under the coat, rotated per tow by `rot16`, so the
  twill flips inside a highlight.
- **Coat:** glass-clear, roughness 0.03, with K10's whisper of print-through.
- Fold UVs as before: the white twill runs over the 1.5 mm edge and down the 38 mm wall under the same gloss.
- **Throat walls** darken with depth to a dark graphite (occlusion 0.60, not black-carbon's 0.93), so the throat reads
  as white walls in shadow. **Bores** darken to a dark graphite below the lip (occlusion 0.82 over 12 mm): each hole still
  reads as a through-hole, with a white lip crescent. Never foam.
- **The previous black Command** (K10's black twill, coat 0.032) is still there: `mat_opts={"white": 0}`. Use it only if
  a brief asks for the old look; it is cached as `KQc_command-black_*`.

**Pace (v5 "fibre" 12K, site review rounds 1 and 3, 2026-10-23; the old text below is v4's history):**

- The v4 tapes read as a flat grey/black checkerboard with crisp squares at phone and card size (an image editor's
  transparency grid): the tiles showed through albedo (+-11 % tone per tape, +-12 % streaks, a 30 % coat-weight flip on
  alternate tapes, a dark seam bump round every tape). Real 12K spread tow is near-uniform black under one clear coat.
- `PACE` now: tapes within a few percent of albedo (`tone` 0.04 = +-2 %, `streak_alb` +-1.5 %; measured adjacent-tape
  step about 2 %), one uniform coat (`flip` 0), no seam; the checker comes only from the fibres' sheen direction
  (`aniso` 0.70, `rough` 0.40), and each tape gets a fine fibre normal (`fib_h` 30 um bundles 0.7 mm across, 60 mm
  along), roughness streaks along the fibres (`rstreak` +-50 %, 1.8 mm across) and a slight crimp arch between its
  crossings (`crimp` 90 um), so a lit tape breaks into silky streaks and grades along its length instead of a flat tile.
  `organic` stays on (0.2 mm tape-edge wander, +-3 deg fibre angle per tape).
- Judged in K08 (right) and K11-pace at the page's sizes (420 / 600 px) and at 1:1 (`blender/out/pace_dev/`): rough 0.25
  to 0.35 read as scratches in shade, crimp 140+ as bevelled mosaic tiles at K11's scale, aniso 0.85 as the old grid.
- `mat_opts=PACE_V4` (`{"rough": 0.5, "aniso": 0.9, "organic": 0, "flip": 0.30, "fibre": 0}`) builds the v4 Pace exactly.
- Measurement: `shots/pace_probe.py` (an albedo / tape-direction / coat-weight emission probe, `PACE_PROBE`) and
  `pace_metrics.py` (tile step, high-pass, rim colour) in `blender/`.
- Rim: no Pace shot uses an ember rim any more (K08 `PACE_EMBER`, K11 `RIM_EMBER` = 0): Pace's edges are Command's
  neutral 6500 K, dimmed to a hairline. Only the face follows the feel.

**Pace v4 (history):**

- K11-pace's 12K spread tow (plain weave, 8 mm tapes, coat 0.03, K11's 30% coat flip), ported to the fold UVs so it also folds over the edge.
- **Two deliberate changes, both judged against the toy-like bar:**
  - **Anisotropy 0.65 instead of 0.9.** At 0.9, a close softbox band turned the tapes into a black-and-white chessboard.
  - **"organic" on:** tape edges wander about 0.2 mm, the fibre angle varies about ±3° per tape, and fibre-bundle streaks run through the sheen.
- The checker stays faint in shade and alternates inside a reflection. Compare `front_pace` with `K11-pair-pace`.
- `mat_opts={"aniso": 0.9, "organic": 0}` restores K11-pace exactly.

### Marks

**Throat bridge:**

- **Serial:** the racket's own serial, set like the measurement card: Saira wght 500, tabular figures, 4.6 mm cap height, tracking 0.04 em, centred at y = −0.1365. The ink is 37.7 mm wide.
- **Sub-line:** K10's KINETIQ (Archivo wdth 125, wght 560, 1.55 mm cap height, tracking 0.62 em) at y = −0.1431.
- **Finish:** both are laser-frosted into the lacquer (K10's mask-in-the-face-material technique). On black carbon the
  frost is pale (a raking light makes it read as frost; otherwise it is a satin mark). **On white Command the frost is
  graphite** (`frost` 0.075, roughness 0.6: a laser darkens white composite), so the serial reads as a crisp dark satin
  mark in any light; a rake only adds the cut-edge glint.
- **Font:** Saira is OFL-licensed; the font and its licence are at `blender/fonts_dl/`.
- **Masks:** generated per serial in `shots/canon/etch_<serial>.png`.

**Serial numbers:**

- One racket: KQ-000427.
- A pair: KQ-000427 (front) and KQ-000428 (rear).
- Three rackets: KQ-000427 to -429, left to right.
- Never 027/500, and never the same number on two rackets.

**Elsewhere:**

- **Side walls:** KINETIQ is laser-frosted on the right wall at y = −62 mm, and SWISS MADE on the left (parts `etchR` and `etchL`; leave them out with `walls=False`). On white the wall frost is graphite (`KQ_WallFrost_white`, 0.06): light the wall itself (a brighter wall card) and leave the rake off, because a rake on the etch (even 0.3 W) turns the dark mark pale and it disappears into the wall.
- **Face:** no print.
- `C.serial_box(serial)` returns the ink box on the face in metres, for framing and rake lights.

## API

| Call | Returns |
|---|---|
| `build_racket(name, feel="command"\|"pace", serial="KQ-000427", walls=True, throat_segs=None, mat_opts=None, head_kw=None, mark_az=0.0)` | `(root, parts)`. Command = white; `mat_opts` takes `COMMAND_WHITE` keys (`{"white": 0}` = old black Command) or `PACE` keys |
| `clone(src_root, name, serial=None)` | `(root, parts)`: shares meshes, and the face gets its own serial material (same feel and `mat_opts` as the source) |
| `is_white(feel, mat_opts)` | True when the racket is white Command: use it to pick white or black lighting in a shot |
| `mat_white(name, o, etch, wall)` | The white twill material (o: `COMMAND_WHITE` keys) |
| `parts(root)` | `{part: object}` for any racket or clone. Each object also carries `ob["kq_part"]` |
| `objs(root_or_parts, *names, style=None)` | A flat object list for `link_only` / `link_receivers` |
| `pose(root, loc, yaw_deg, roll_deg, tilt_deg)` | Places the racket. `tilt_deg=90` stands it up with the front face to −Y, as `k789_lib.pose` |
| `measure(root)` | Extents in mm; asserts the spec |
| `holes_canon()` | 42 × (x, y, r) in shape units |
| `outline_canon()` | The plan outline with the neck |
| `edge_radius(y)` | The rim radius along the neck |
| `section(n, grow)` | The handle section |
| `cap_profile()` | The cap profile |
| `mat_carbon(feel, role, serial, o)` | role: face, skin, throat or bore. Materials are cached and shared per feel (white Command, `command-black`, Pace) |

**Parts:** face, back, rim (the two 1.5 mm rounded edges), wall (the flat 38 mm side), neck (everything below y = −0.150), throat (or thr00..15), bridgewall, holes, grip, cap, capmark (the Q), etchR, etchL.

## Lighting notes from the proof renders

1. **Face sweeps:** use a band (`k10_lib.sky_projected(..., band=(off, half_width))`), not a half-plane. A half-plane softbox fills the rough metallic base under the coat and greys the whole face. A 16 to 70 mm band gives lit twill in one diagonal and deep black gloss elsewhere. Add a 1.2 to 1.6 mm gloss line beside it.
2. **Edge hairlines:** use a mirror-path ribbon along the outline. `canon_test.edge_ribbon`: about 30 mm wide at 15 cm, strength 25 to 35, linked to `rim` only. It gives one crisp 1 px white or ember line at full-racket scale.
3. **The face and neck are separate parts.** Link face lights to `face` + `neck`, and wall lights to `wall` + `rim` + `neck`, or the light stops at y = −0.150. A hard tone change right at the V and neck junction is real geometry: the V arm faces 47° away from the neck wall.
4. **Serial:** K10's rake, a 50 × 5 mm area light at 16° from camera-left, 12.5 cm from the mark, about 1 W, linked to `face`. It makes the serial legible without touching the gloss.
5. **Cap:** a 30 cm softbox in the mirror direction of the cap's front band, about 0.3 W, linked to `cap` + `capmark`. The groove and the bright-cut K then read on satin black. Smaller boxes read as a lit label behind the K.
6. **Grip:** a 2 cm × 30 cm strip from camera-left at about 1 W, aimed with an explicit world up. `studio.aim` rolls a strip freely; use `canon_test.look_at`. A black grip that renders grey means too much light.
7. **Face-on cameras:** `studio.camera`/`studio.aim` roll at random when the view is along Z. Use `canon_test.look_at(cam, loc, tgt, up)`.
8. **White Command needs real light.** Notes 1 to 6 are for black carbon, which is lit by reflections only. Under that
   studio white carbon renders a flat mid-grey (`out/white_dev/front_w0.png`). What works (`canon_test.WHITE_DEFAULTS`):
   - **A soft spot pool for the gradient:** a spot of 20 to 24 degrees, blend 1.0, radius 6 cm, about 1.2 m away from
     the upper left and in front, aimed at the upper-left of the head (front: 230 W; handle: 95 W). It gives white at
     about luma 205 in the upper left falling to about 150 on the bridge: a white face with a light sweep, not a flat
     plate. A plain area key or an area light with a narrow `spread` lights the face too evenly (luma 190 to 178, reads
     flat and plastic).
   - **A weak fill** (a 1 m area light, 1 W, front right): the shade side stays white in shadow, not dirty grey.
   - **Keep big reflection softboxes dim** on white: `sky_projected` panels are 2 to 3 m wide, and on white their
     diffuse light floods the face and kills the gradient (sky 6 lifted the shade side by about 40 luma). The gloss
     sweep becomes a thin line instead: a 1.6 mm band at strength 30 to 40 gives one crisp gloss line (luma about 235)
     over the white without clipping.
   - **Link the key, pool and fill to the head parts only** (not grip, cap, capmark): the grip strips stay as they are,
     so the grip stays black and the cap satin.
   - **No blown highlights:** check `max` luma; at most a few pixels at 250+ (the hairlines). The white face itself
     should top out at luma 205 to 215, as the Tesla carousel's white body does.
   - The twill reads in shade through tone and relief and in light through the fibre sheen, so a shot may leave part
     of the face in shade without losing the weave (`out/white_dev/front_w4_crops.png`: lit side left, shade side right).

## Proof

- **Self-test** (no render, about 25 s): `../bpyenv/bin/python shots/kq_canon.py`. It builds both feels and a clone, asserts the spec and prints part face counts.
- **Proof renders** (from `blender/`, through the lock, 30 to 60 s each):

```
flock render.lock ../bpyenv/bin/python shots/canon_test.py --view front  --feel command --w 720  --h 1280 --spp 40 --out canon/front_command
flock render.lock ../bpyenv/bin/python shots/canon_test.py --view front  --feel pace    --w 720  --h 1280 --spp 40 --out canon/front_pace
flock render.lock ../bpyenv/bin/python shots/canon_test.py --view handle --feel command --w 720  --h 1280 --spp 40 --out canon/handle_command
flock render.lock ../bpyenv/bin/python shots/canon_test.py --view handle --feel pace    --w 720  --h 1280 --spp 40 --out canon/handle_pace
flock render.lock ../bpyenv/bin/python shots/canon_test.py --view handle --feel command --clone_serial KQ-000428 --w 720 --h 1280 --spp 40 --out canon/handle_clone428
flock render.lock ../bpyenv/bin/python shots/canon_test.py --view side   --feel command --w 1280 --h 720  --spp 40 --out canon/side_command
flock render.lock ../bpyenv/bin/python shots/canon_test.py --view q34    --feel command --w 1280 --h 720  --spp 40 --out canon/q34_command
../bpyenv/bin/python shots/canon_test.py --sheet
```

What each render shows:

- **front_command (white) and front_pace (black):** the crown-of-8 layout, the 455 mm proportions, the hairlines and the face-on serial; on white, the twill in the lit upper left and in the shaded lower right.
- **handle_command (white) and handle_pace (black):** the neck flowing into the grip, the wrap and perforations, the satin cap with its groove and the engraved Q, and a legible KQ-000427 (graphite on white, pale frost on black).
- **handle_clone428:** `clone` gives its own serial, KQ-000428.
- **side_command (white):** the 38 → 29 mm loft, the grip, and the cap standing proud.
- **q34_command (white):** the white twill folding over the edge onto the wall, and the graphite KINETIQ wall etch.
- The black-Command proofs from before the update are kept in `blender/out/canon/bak_black_2026-10-22/`.

## Departures from the audit (decided here)

- **Module name:** the module is named `kq_canon.py`, as the task asked, not the audit's `canon_lib.py`.
- **Ferrule:** the neck is the ferrule; there is no separate ferrule part (audit 4.1).
- **Neck edge:** the neck's edge radius grows to 12 mm. The audit did not specify it. Without it, the 1.5 mm-edged 33 × 29 mm neck could not pass under an oval grip without its corners poking through. The grip and cap now share that section.
- **Bores:** they are dark carbon lining, not EVA or "core", in line with CLAIMS.md's sealed core ("the core never touches the air"). Nothing in any render may show foam inside a hole.
- **Pace:** the v5 "fibre" 12K (2026-10-23), as described above (v4: anisotropy 0.65 and the "organic" variation).
- **Serial width:** the serial measures 37.7 mm wide, against the audit's estimate of about 35 mm. It still fits the bridge, which is about 76 mm wide there.

## Step 0 acceptance (face group, 2026-10-22)

Accepted without changes. The self-test passes (455.00 x 260.12 x 38.00 mm, 42 holes, 8 crown); the mesh itself has 42
separate bores, 34 at 12.4 mm and 8 at 14.0 mm (counted from the `holes` part, not the list). The sheet matches section 4:
crown of 8 + rows A B A C A C A C A B A, one-piece neck into the overgrip and satin cap with its K, 1.5 mm edge with the
twill over it, KQ-000427 + KINETIQ frosted on the bridge, KINETIQ / SWISS MADE on the walls. First user: K05 v4.

Re-accepted after the white update (face group, 2026-10-22, later): the self-test still passes (455.00 x 260.12 x 38.00 mm,
42 holes, 8 crown, for white Command, Pace and a clone); the sheet shows white 3K Command, black 12K Pace and the engraved
Q on the cap. No change to kq_canon.py. First white user: K05 v5 (`shots/K05-laser-scan.py`, WHITE_DEFAULTS: a 16 deg
spot pool from the frame's upper left on the head parts, a 5 W fill, the same lamp's diffuse-only spill on the stone for a
contact shadow, the black-carbon clearcoat stripe off; the laser gets a red core, since a white-hot core vanishes on white).

## Width assert aligned to 260.0 mm (face group, 2026-10-22, K05 critique fix 13)

`measure()` now asserts 260.0 +- 0.3 mm (`WIDTH = 0.2600`), the FIP maximum that `racket-shape.ts`, CLAUDE.md and
DESIGN.md use. The mesh still measures 260.12 mm: 0.12 mm over, about half a pixel at 3200 px, so no still changes and
no shot needs a re-render. Cards, captions and claims quote 260.0 mm from `racket-shape.ts`, never the mesh's measured
width. Self-test passes (455.00 x 260.12 x 38.00, 42 holes, 8 crown, both feels and a clone). Backup:
`shots/kq_canon.v3-pre260.bak`.

## White Command: lessons from K05 v6 (face group, 2026-10-22)

- **A gloss band on white needs a gridded strip.** A plain strip softbox on white twill lifts the whole face: the fibres'
  rough anisotropic sheen (roughness 0.6) gathers it from everywhere (+30 luma on the shade side). K05's `gloss_strip`
  is designed on the face (centreline, width) and mapped to the card through the mirror, glossy-only, and emits only
  along the mirror path to the camera (`fb_tol` 2.6 deg, a honeycomb grid): one 34 mm lacquer band at luma 225-230 with
  the twill flipping inside it, and the shade untouched.
- **Never put two see-through cards in one plane.** A ray that passes the first skips the second (the band vanished).
- **Rakes light white faces.** A 0.35 W serial rake lit a third of the white head to luma 180; on white the graphite serial
  reads without it (rake 0).
- **Holes on a polished plate stay black** whatever lights the plate: under a hole the stone mirrors the racket's back.
  K05 puts a hidden stone patch under the hole field with its own diffuse-only light (`holefloor`, shadow-linked so the
  racket does not block it): stone at luma 23-29 with grain in every hole.
- **Red on white goes pink** under AgX. Keep the face under a red line at luma 150 or less, give the line's indirect light
  the pure laser colour (the paler core only for camera rays), and tint the scene toward the laser round the line in the
  compositor before the red halo is added (`tint`): halo G/R 0.59-0.65 on white.


## Pace v6 (review round 6, 2026-10-23; kq_canon.v5-fibre-precrit6.bak is v5)

- Measured first: the lifted black is not the coat (the backdrop is camera-only; the coat mirrors black off the band) and
  barely the weave card (-6 luma) or key (-1): with the band card off the Pace face is luma 0. It is the band card seen
  through the fibre layer. v5's lobe was wide ALONG the fibres while its fibre bumps spread it across them (near-isotropic),
  and its crimp step drew a crease round every tile.
- v6 `PACE`: narrow fibre lobes (rough 0.14, aniso 0.90, `aniso_across` 1: wide axis across the fibres), the fibre sheen
  as its own anisotropic Beckmann glossy under a coat-only Principled (`beckmann` 1), base 0.045 (+-2 % per tape), an
  analytic 30 um arch (`crimp_shape` 2: the shading normal tilts along the fibre, no height field, so no crease or pillow
  at any tape edge), fibre bumps 3 um / 0.4 mm / 120 mm / 1.5 octaves (`fib_blend` 0.04: no step at tape edges), rstreak 0.15.
- The shots dim the Pace band to match (K08 `P_BAND_S` 22 -> 9, K11 26 -> 10) and drop the weave floor (0.25 -> 0); K11
  `PACE_WEAVE` 0.5 -> 0.9. `mat_opts=C.PACE_V5` (+ the old shot constants) gives v5 back.
- Rejected on preview: crimp as a tile envelope (`crimp_shape` 1, the critic's sin x sin^p): with any narrow lobe every tile
  renders as a dome (quilted / diamond-plate); the brief's rough 0.32-0.35 / F0 0.05-0.06 lifted the face to p50 51-71.
