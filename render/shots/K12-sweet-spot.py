"""K12-sweet-spot: the canonical racket (shots/kq_canon.py, Command = WHITE 3K twill, KQ-000427, the engraved icon Q on
the cap) face-on, upright, handle down, in the style of Apple's edge-to-edge display shots. It sits beside the short
sweet-spot claim ("Edge to edge.", nearly 94 % of the face, 4 mm from the edge; CLAIMS.md row 6b: Illustrative).

Composition (3200 x 1800 master): tip at 6 % of the height, butt at 94 % (3.48 px/mm, so the 2.6 mm tows resolve);
the racket's centre at x 0.66 by lens shift (verticals straight); a 100 mm lens (36 mm sensor) at 2.553 m, f/11,
the racket turned 7 deg toward camera-left so the right wall shows as a sliver (about 16 px) with one rim line.
x 0 to 0.45 is the words' side: a smooth graphite gradient (display luma 16 to 28), never flat black, nothing bright.

Two variants from ONE render (light-group passes + shader AOVs), pixel for pixel registered:
  base  every studio group: the white racket in a low-key studio. A spot pool from the upper left lights the upper-left
        40 % of the face (white twill at luma 200-210) with a soft diagonal edge (about 30 mm) and a steep fall to the
        shade (luma 60-80, the twill still reading by tone and relief); a large glossy-only gradient softbox puts a
        clear-coat sheen over the lit part (soft 30 mm edge along the same diagonal, max luma <= 235); a white hairline on
        the upper-left edge, one dim ember hairline on the right edge, the right wall sliver; one long soft strip down
        the grip (helical wrap, the cap's groove and the Q); a short rake on KQ-000427; a camera-only graphite backdrop
        with a halo behind the head (about luma 30, falling to about 16 at the left and top edges).
  full  the sweet spot as designed lights up on the same white racket: the "field" group (an emission under the clear
        coat, face only, masked by the field) graded so the plateau lands at display (213, 204, 197) (#FFF4EC as seen,
        luma about 206). The studio face groups stay on: FACE_DIM inside the field; outside it the fill at BEZEL_FILL
        (base's own shade) and the pool, sky and gloss at BEZEL_DIM, cross-faded over the field's 3 mm roll-off
        (kq_plate), so the 4 mm band, the rim, the bridge and the lower head read as white Command twill in shade, as
        G15 paints them (#a4a19c to #4c4b4a): band luma about 150-170 on the pool side and 60-80 on the shade side,
        bridge and lower head about 60-95, the twill legible. Never a black frame around the field. The serial rake and
        the neck's lamp at SERIAL_FULL / NECK_FULL (KQ-000427 stays legible); the gloss sheen kept on top at GLOSS_FULL;
        the rim's ember ribbon off (EMBER_FULL = 0: no second, red line on the rim); the 0.6 mm hairline composited
        OVER the plateau in the page's amber, #e3a467 as seen (LINE_DISPLAY, solved through AgX Punchy by line_lin),
        as G15's field line and the lockup's hairline; one thin crescent on the lower-right of every hole lip (group
        "lip": a glossy-only ribbon laid out in direction space); bloom from the field and the line only (threshold
        0.42 linear, sigma 0.0008 H, amount 0.12: 1-2 mm of spill onto the band, no flare).
The field: the face above the bridge (y -86.5 mm), inset 4.0 mm from the outer edge and 4.0 mm above the throat:
racket-shape.ts / graphics-sweetspot.ts FIELD exactly (252.0 mm wide, 4 mm from the tip, 498.7 of 531.5 cm2 = 93.8 %),
ported here, not the mesh outline (260.12 mm). Plateau times (0.55 + 0.45 x the normalised k04_tex2 tow height): the
tows glow, the gaps stay darker. No emission in the bores or the throat.

The field mask is rasterised with shapely at 0.05 mm per pixel in the face UVs (u = x, v = y, metres) and written as a
16-bit RGB PNG (R = plateau with its 3 mm roll-off, G = the 0.6 mm hairline, B = inside): shots/k12/field_mask.png. The
face material writes them as AOVs (kq_plate, kq_line, kq_in) plus kq_face; the comp uses them for the line, the studio
levels inside and outside the field, and the measurements. Only the plateau is emitted (the hairline is drawn in the
comp from kq_line).

Usage (from the blender dir, through the lock):
  flock render.lock ../bpyenv/bin/python shots/K12-sweet-spot.py --w 960 --h 540 --spp 32 --out k12s/K12_p10
  re-comp only (no render): flock render.lock ../bpyenv/bin/python shots/K12-sweet-spot.py --comp --out k12s/K12_p10
      [--gain pool=0.9 ...] [--set BEZEL_FILL=1.1]; the final: --comp --out final/K12-sweet-spot (base comes out
      unchanged: only full's grade changes)
  final: flock render.lock ../bpyenv/bin/python shots/K12-sweet-spot.py --w 3200 --h 1800 --spp 160 --out final/K12-sweet-spot
  Pace (--feel pace, also on --comp): ... --feel pace --w 3200 --h 1800 --spp 160 --out final/K12-sweet-spot-pace
      -> K12-sweet-spot-pace-base.png, -pace-full.png, -pace-phone-base.png, -pace-phone-full.png (see PACE_SET)
Writes <out>-base.png, <out>-full.png (16-bit) and the phone crops <out>-phone-base.png, <out>-phone-full.png (x .435 to
.885, full height: 1440 x 1800 from the master), plus <out>-sheet.png (review).
Dev: --set NAME=value (any constant below), --crop x0 x1 y0 y1 (fractions, region render at the given w x h),
--as NAME (comp: write the outputs under another name), --gain group=k (comp: scale a light group).
The preview-only contour lines (--contours) were rejected (critique 3a: they imply a measured rebound map; CLAIMS rows 6
and 6b say rebound has not been measured). The option is gone.

White Command (owner, 2026-10-22; canon.md lighting note 8) and critique 3a (art director, revise 6), all deliberate:
- Base: white is lit by real diffuse light. The pool is a spot with a crisp cone (POOL_BLEND solved for a 30 mm edge on
  the face) aimed so its edge crosses the face diagonally with POOL_FRAC = 40 % lit; the shade is the fill alone. The
  old 1.6 mm gloss line read as a scratch: the sheen is now a big glossy-only softbox (diffuse ray visibility off, and a
  honeycomb so the fibres' broad sheen lobe cannot gather it), soft-edged along the pool's diagonal.
- The denoiser: Cycles writes emission into the Denoising Albedo pass, so OIDN printed the field boundary into every
  studio pass (base showed a warm ghost line, R-B +5..13). The studio passes are denoised with albedo minus the field
  pass; base |R-B| on the boundary must be <= 3.
- The rim is not lit by the pool (the white hairline must stand above the white face: >= 235).
- The bores darken toward the far exit (the visible far wall was a grey half-disc; now the far wall is black and the
  hole shows the graphite backdrop through it); the 0.5 m lip box (a ring) is a direction-space ribbon (a crescent).
- The grip strip is longer (0.40 m) and centred lower, so the wrap reads from the finishing band to the cap; its twin
  lamp on the neck is its own group ("neck") so the neck can recede in full.
- The cap: the current kq_canon icon Q, engraved, faced to the camera (mark_az = YAW); the cap box is dimmer and larger so
  the Q never sits on a lit label.
Review round 2 (imagery-k12-two-tone-field, 2026-10-22), re-comp only from the saved passes: full had dimmed every studio
face group outside the field to 0.058 and drawn the line in ember #FF3A1E, with the rim's ember at 0.2. The band, rim,
bridge and lower head went near-black (luma 1-25): a white D-shaped insert in a black frame, the opposite of "Edge to
edge.", of the hero's all-white racket and of DESIGN.md ("the 4 mm band and the rim stay bare carbon"; G15: "an amber
hairline on the line ... No ember"). Now the fill keeps base's shade outside the field (BEZEL_FILL 1.0), the pool,
sky and gloss sit at BEZEL_DIM 0.30, the line is the page's amber and EMBER_FULL is 0. FIELD, the grade target and
base are unchanged.
"""
import json
import math
import os
import struct
import sys
import time
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import studio  # noqa: E402
import k12_lib as K  # noqa: E402
import k10_lib as L  # noqa: E402
import kq_canon as C  # noqa: E402
import canon_test as CT  # noqa: E402

# ------------------------------------------------------------------ composition
TIP_FRAC, BUTT_FRAC = 0.06, 0.94      # tip / butt as fractions of the frame height
CX = 0.66                             # the racket's centre, fraction of the frame width (lens shift)
LENS, SENSOR = 100.0, 36.0            # mm; sensor fit horizontal, 16:9
YAW = 7.0                             # deg: the face turned toward camera-left, the right wall a sliver
FSTOP = 11.0
FRAME_H = (C.TIP_Y - C.BUTT_Y) / (BUTT_FRAC - TIP_FRAC)       # 0.517 m of frame height at the racket
CAM_D = FRAME_H / (SENSOR * 9.0 / 16.0 / LENS)               # 2.553 m
TGT = (0.0, (C.TIP_Y + C.BUTT_Y) / 2.0, 0.0)                 # the racket's centre (tip to butt)
PHONE_X = (0.435, 0.885)              # phone / card crop (fractions of the width, full height)
CLEAN_X = 0.45                        # the words' side: x 0 to 0.45

# ------------------------------------------------------------------ the field (the sweet spot as designed)
FIELD_SRC = "site"        # "site": racket-shape.ts / graphics-sweetspot.ts FIELD (the claim's numbers); "canon": the mesh
FIELD_INSET = 0.004       # m from the outer edge and above the throat
FIELD_PX = 0.00005        # 0.05 mm per mask pixel
FIELD_ROLL = 0.003        # the plateau rolls off over the last 3 mm
LINE_HALF = (0.00015, 0.00045)   # hairline: full within +-0.15 mm of the boundary, gone at +-0.45 mm (0.6 mm FWHM)
FIELD_E = 1.6             # plateau emission before the grade (linear; the comp solves per-channel gains to FIELD_TARGET)
FIELD_TARGET = (213.0, 204.0, 197.0)   # display rgb of the full composite on the plateau (luma about 206)
TOW_K = (0.55, 0.45)      # emission x (TOW_K[0] + TOW_K[1] x tow height)
TOW_REMAP = (0.45, 0.95)  # tow height normalised: crevice floor 0, tow crown 1 (k04_tex2 height16 spans about 0.4 to 0.98)
FIELD_HEX, LINE_HEX = "#FFF4EC", "#E3A467"
LINE_DISPLAY = (227.0, 164.0, 103.0)  # the hairline as seen: the page's amber (--amber #e3a467, G15 .fieldLine, the lockup)
LINE_ALPHA = 1.0          # the hairline's coverage scale (kq_line AOV) in the over-composite
LIP, LIP_DIST = 40.0, 2.0             # lip crescents (own group "lip", holes only, full only): ribbon radiance, distance (m)
LIP_PHI, LIP_SPAN = -50.0, 45.0       # deg: the crescent's middle on each lip (0 = +x, ccw: lower right), half its arc
LIP_TILT, LIP_DT = 30.0, 12.0         # deg: the lip normal's tilt it catches, +- (the crescent's width across the lip)
FACE_DIM = 0.32           # studio face groups inside the field (full)
BEZEL_DIM = 0.30          # the pool, sky and gloss outside the field (full): the band, rim, bridge, lower head and lips
BEZEL_FILL = 1.0          # the fill outside the field (full): base's own shade, so they read as white twill in shade
GLOSS_FULL = 0.30         # the clear-coat sheen in full, inside the field (outside: BEZEL_DIM, as the studio)
EMBER_FULL = 0.0          # the rim's ember ribbon in full: off (the amber hairline is the only line; no ember)
SERIAL_FULL = 0.35        # the serial rake in full (it lights the bridge: the chin recedes, the serial stays faintly legible)
NECK_FULL = 0.35          # the grip strip's own lamp on the neck, in full (the neck recedes with the chin)
LIP_GAIN = 1.0
BLOOM_THR, BLOOM_AMT, BLOOM_SIGMA = 0.42, 0.12, 0.0008   # linear luma threshold, amount, sigma (fraction of the height)

# ------------------------------------------------------------------ studio (white Command needs real diffuse light)
POOL, POOL_DEG, POOL_BLEND, POOL_R = 330.0, 40.0, None, 0.02   # W, full cone, blend (None: solved for POOL_EDGE), radius
POOL_DIR, POOL_DIST = (-0.62, 0.57, 0.82), 1.8
POOL_FRAC, POOL_EDGE = 0.40, 0.030    # lit share of the face (mid-edge) and the edge width on the face (10-90 %, m)
POOL_U = (-0.72, 0.69)                # in-plane direction toward the lit side (upper left)
FILL, FILL_AT = 4.2, (0.75, -0.45, 0.90)   # the shade: fill alone, luma 60-80
SKY, SKY_BW = 0.0, 0.07               # the old dim projected band (off: its diffuse floods white)
GLOSS = 40.0                          # the big glossy-only gradient softbox (coat sheen over the lit part)
GLOSS_OFF, GLOSS_EDGE = 0.012, 0.030  # its edge: offset toward the lit side from the pool's edge (m), soft width (m)
GLOSS_W, GLOSS_G0 = 0.10, 0.30        # inside: 1 at the edge, falling to G0 over W
GLOSS_BOUND = (0.0, 0.035, 0.16, 0.20)   # face coords: emits only where the face (plus margin) mirrors it
GLOSS_TOL = 3.0                       # deg: honeycomb, emits only along the mirror path to the camera
WHITE_LINE, EMBER_LINE, PHI = 280.0, 30.0, 40.0   # white: the upper-left hairline peaks at about 230-240 at 3200
RIM_POOL = 0.55                       # the pool on the rim (its own lamp): the edge a step below the face
WALL, WALL_AT = 5.0, (0.6, 0.0, 0.25)   # the right wall only: white in soft shade, one sliver
GRIP, GRIP2 = 1.2, 0.0
GRIP_AT, GRIP_TGT, GRIP_LEN, GRIP_W = (-0.32, -0.23, 0.30), (0.0, -0.23, 0.0), 0.40, 0.02
CAP, CAP_SIZE, CAP_DIST = 0.12, 0.60, 0.35
RAKE, RAKE_SPREAD = 0.008, 30.0
BORE_OCC, BORE_COL = 0.97, 0.010      # bores: dark lining, darkening toward the far exit (not symmetric)
BG_C, BG_E = 31.0, 18.5               # display luma: halo behind the head, the left and top edges
BG_RX, BG_RY, BG_Z = 0.78, 0.30, -0.45
BG_TINT = (0.96, 0.965, 1.0)

EMBER = CT.EMBER
WHITE = CT.WHITE
GROUPS = ["stage", "pool", "fill", "sky", "gloss", "rim", "ember", "wall", "handle", "neck", "serial", "lip", "field"]
FULL_ONLY = ("field", "lip")          # not in base
FACE_GROUPS = ("pool", "fill", "sky", "gloss")   # dimmed under the field (full)
AOVS = ["kq_plate", "kq_line", "kq_in", "kq_face"]
MAT_OPTS = None           # kq_canon mat_opts; {"white": 0} = the previous black Command (not lit for it here)
MASK_DIR = kqpaths.asset("k12")

# ------------------------------------------------------------------ Pace (--feel pace, Release 2 feel toggle, 2026-10-23)
# Same camera, crop, field, line, grade target and comp; the racket in the canon Pace v6 (kq_canon.PACE, black 12K,
# mat_opts None). Black carbon is lit by reflections, not by the white pool and fill (RENDER_NOTES 1, canon notes 1-2):
# the projected sky band across the face (canon front_pace's sweep), the big glossy-only coat softbox kept, an
# off-specular weave card only the 12K's fibre lobes see (in group "sky", so it is graded with the face groups), the
# upper-left hairline at canon front_pace's level, the right-edge hairline neutral (no ember on the racket), the serial
# rake at K10's ~1 W (the frost is pale on black and needs the rake). The field: the same plateau emission under the
# coat, modulated by the 12K's tapes (P_TAPE_K: alternate tapes) instead of the 3K tow height. In full the band, rim,
# bridge and lower head keep their studio reflections (P_BEZEL_DIM): 4 mm of lit black 12K in its sheen, never a flat
# black bezel. Command (the default) is unchanged.
FEEL = "pace" if ("--feel" in sys.argv and sys.argv[sys.argv.index("--feel") + 1] == "pace") else "command"
PACE = FEEL == "pace"
P_TAPE_K = (0.95, 0.05)   # field emission x (P_TAPE_K[0] + P_TAPE_K[1] x tape parity)
P_WEAVE, P_WEAVE_UP, P_WEAVE_D, P_WEAVE_SIZE, P_WEAVE_FLOOR = 3.9, 20.0, 1.4, (1.6, 1.0), 0.6
P_LOW, P_LOW_Y, P_LOW_D, P_LOW_SIZE, P_LOW_FLOOR = 1.56, -0.115, 1.0, (0.5, 0.12), 0.3   # lower-head card
PACE_SET = dict(POOL=0.0, RIM_POOL=0.0, FILL=0.0, SKY=0.2, SKY_BW=0.07, GLOSS=6.0, WHITE_LINE=30.0, EMBER_LINE=6.0,
                RAKE=1.0, RAKE_SPREAD=180.0, WALL=6.0, FACE_DIM=0.32, BEZEL_DIM=1.0, BEZEL_FILL=1.0, GLOSS_FULL=0.30,
                SERIAL_FULL=0.6)
if PACE:
    globals().update(PACE_SET)


def parse_args(argv):
    o = {"w": 960, "h": 540, "spp": 32, "out": "k12s/K12_test", "comp": False, "gain": [], "set": [], "crop": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--w", "--h", "--spp"):
            o[a[2:]] = int(argv[i + 1]); i += 2
        elif a == "--out":
            o["out"] = argv[i + 1]; i += 2
        elif a == "--as":
            o["as"] = argv[i + 1]; i += 2
        elif a in ("--gain", "--set"):
            o[a[2:]].append(argv[i + 1]); i += 2
        elif a == "--crop":
            o["crop"] = [float(v) for v in argv[i + 1:i + 5]]; i += 5
        elif a == "--comp":
            o["comp"] = True; i += 1
        else:
            i += 1
    g = globals()
    for kv in o["set"]:
        k, v = kv.split("=", 1)
        assert k in g, k
        g[k] = eval(v)
        print("set", k, "=", g[k], flush=True)
    return o


def lin_hex(h, norm="max"):
    c = K.hex_lin(h)
    s = max(c) if norm == "max" else (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])
    return tuple(x / s for x in c)


# ------------------------------------------------------------------ field geometry: racket-shape.ts, ported
# racket-shape.ts (units: 1 = 10 cm): HEAD_START, DRAWN_CURVES (x scaled so the widest point is HEAD_WIDTH 2.6),
# THROAT_START, THROAT_CURVES; graphics-sweetspot.ts: cubicPts(..., 200) in mm, BRIDGE_Y = the throat's top,
# FACE = clipAbove(HEAD, BRIDGE_Y), FIELD = clipAbove(offset(HEAD, 4 mm), BRIDGE_Y + 4 mm) (offset along each point's
# normal). The port gives the claim's own numbers: 531.5 cm2, 498.7 cm2, 93.8 %.
RS_HEAD_START = (0.0, 1.55)
RS_DRAWN = [[(0.85, 1.55), (1.32, 0.95), (1.3, 0.25)], [(1.28, -0.55), (0.75, -1.05), (0.2, -1.55)],
            [(0.07, -1.55), (-0.07, -1.55), (-0.2, -1.55)], [(-0.75, -1.05), (-1.28, -0.55), (-1.3, 0.25)],
            [(-1.32, 0.95), (-0.85, 1.55), (0.0, 1.55)]]
RS_HEAD_WIDTH = 2.6
RS_THROAT_START = (-0.32, -0.88)
RS_THROAT = [[(-0.1, -0.86), (0.1, -0.86), (0.32, -0.88)], [(0.3, -1.0), (0.12, -1.2), (0.0, -1.27)],
             [(-0.12, -1.2), (-0.3, -1.0), (-0.32, -0.88)]]


def _cub(p0, c, t):
    u = 1.0 - t
    return tuple(u * u * u * p0[i] + 3 * u * u * t * c[0][i] + 3 * u * t * t * c[1][i] + t * t * t * c[2][i] for i in (0, 1))


def _cubic_pts(start, curves, steps):
    out, p0 = [], start
    for c in curves:
        for i in range(1, steps + 1):
            x, y = _cub(p0, c, i / steps)
            out.append((x * 100.0, y * 100.0))
        p0 = c[2]
    return out


def _site_head():
    half, p0 = 0.0, RS_HEAD_START
    for c in RS_DRAWN:
        half = max(half, max(_cub(p0, c, i / 4000.0)[0] for i in range(4001)))
        p0 = c[2]
    k = RS_HEAD_WIDTH / 2.0 / half
    return [[(x * k, y) for (x, y) in c] for c in RS_DRAWN]


def _offset(pts, d):
    n = len(pts)
    out = []
    for i, p in enumerate(pts):
        a, c = pts[(i - 1) % n], pts[(i + 1) % n]
        tx, ty = c[0] - a[0], c[1] - a[1]
        ln = math.hypot(tx, ty) or 1.0
        out.append((p[0] + ty / ln * d, p[1] - tx / ln * d))
    return out


def _clip_above(poly, y0):
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ina, inb = a[1] >= y0, b[1] >= y0
        if ina:
            out.append(a)
        if ina != inb:
            t = (y0 - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * t, y0))
    return out


def field_polys():
    """(face, field, bridge_y) in model metres. FIELD_SRC "site": racket-shape.ts / graphics-sweetspot.ts exactly;
    "canon": kq_canon's mesh outline (260.12 mm) and k10 throat, inset with shapely."""
    from shapely.geometry import Polygon, box
    if FIELD_SRC == "site":
        head = _cubic_pts(RS_HEAD_START, _site_head(), 200)
        bridge = max(p[1] for p in _cubic_pts(RS_THROAT_START, RS_THROAT, 200))
        face = Polygon([(x / 1000.0, y / 1000.0) for x, y in _clip_above(head, bridge)])
        field = Polygon([(x / 1000.0, y / 1000.0) for x, y in _clip_above(_offset(head, FIELD_INSET * 1000.0),
                                                                           bridge + FIELD_INSET * 1000.0)])
        return face.buffer(0), field.buffer(0), bridge / 1000.0
    O = Polygon(C.outline_canon()).buffer(0)
    bridge = max(p[1] for p in L.throat_loop())
    face = O.intersection(box(-1, bridge, 1, 1))
    field = O.buffer(-FIELD_INSET, join_style="round", quad_segs=32).intersection(box(-1, bridge + FIELD_INSET, 1, 1))
    return face, field, bridge


def write_png16(path, rgb):
    """16-bit RGB PNG (rows top-down, values 0..1)."""
    a = np.clip(np.round(rgb * 65535.0), 0, 65535).astype(">u2")
    h, w = a.shape[:2]
    raw = b"".join(b"\x00" + a[r].tobytes() for r in range(h))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 2, 0, 0, 0)))
        fh.write(chunk(b"IDAT", zlib.compress(raw, 6)))
        fh.write(chunk(b"IEND", b""))


def field_mask():
    """Rasterise the field at FIELD_PX in face UVs: R = plateau (smoothstep over the last FIELD_ROLL inside the
    boundary), G = the hairline (centred on the boundary), B = inside (anti-aliased step). Cached; returns
    (path, (x0, y0, x1, y1), info)."""
    from PIL import Image, ImageDraw
    os.makedirs(MASK_DIR, exist_ok=True)
    key = "%s_%.5f_%.5f_%.5f_%.5f_%.5f_v3" % (FIELD_SRC, FIELD_INSET, FIELD_PX, FIELD_ROLL, LINE_HALF[0], LINE_HALF[1])
    path = os.path.join(MASK_DIR, "field_mask.png")
    meta_p = os.path.join(MASK_DIR, "field_mask.json")
    if os.path.exists(path) and os.path.exists(meta_p):
        with open(meta_p) as fh:
            meta = json.load(fh)
        if meta.get("key") == key:
            return path, tuple(meta["bounds"]), meta["info"]
    t0 = time.time()
    face, field, bridge = field_polys()
    pad = LINE_HALF[1] + 0.0004
    bx0, by0, bx1, by1 = field.bounds
    x0, y0 = bx0 - pad, by0 - pad
    Wp = int(math.ceil((bx1 + pad - x0) / FIELD_PX))
    Hp = int(math.ceil((by1 + pad - y0) / FIELD_PX))
    x1, y1 = x0 + Wp * FIELD_PX, y0 + Hp * FIELD_PX
    img = Image.new("I", (Wp, Hp), 0)
    dr = ImageDraw.Draw(img)
    steps = int(round((LINE_HALF[1] + FIELD_ROLL) / FIELD_PX)) + 2
    ds = [LINE_HALF[1] + FIELD_PX - k * FIELD_PX for k in range(steps)]   # outward offsets, outer to inner
    for k, d in enumerate(ds):
        g = field if abs(d) < 1e-12 else field.buffer(d, join_style="round", quad_segs=16)
        for poly in getattr(g, "geoms", [g]):
            pts = [((x - x0) / FIELD_PX, (y1 - y) / FIELD_PX) for x, y in poly.exterior.coords]
            dr.polygon(pts, fill=k + 1)
    q = np.asarray(img, np.int32)
    ds_a = np.array(ds)
    sd = np.where(q > 0, ds_a[np.clip(q - 1, 0, None)] - FIELD_PX * 0.5, 1.0)   # signed distance, + outside (m)
    t = np.clip(-sd / FIELD_ROLL, 0.0, 1.0)
    plate = t * t * (3 - 2 * t)
    e = np.clip((np.abs(sd) - LINE_HALF[1]) / (LINE_HALF[0] - LINE_HALF[1]), 0.0, 1.0)
    line = e * e * (3 - 2 * e)
    inside = np.clip(0.5 - sd / FIELD_PX, 0.0, 1.0)
    rgb = np.zeros((Hp, Wp, 3), np.float32)
    rgb[..., 0] = plate
    rgb[..., 1] = line
    rgb[..., 2] = inside
    write_png16(path, rgb)
    info = dict(src=FIELD_SRC, face_cm2=round(face.area * 1e4, 2), field_cm2=round(field.area * 1e4, 2),
                share=round(field.area / face.area, 4), bridge_mm=round(bridge * 1000, 2),
                field_bounds_mm=[round(v * 1000, 2) for v in field.bounds],
                field_width_mm=round((field.bounds[2] - field.bounds[0]) * 1000, 2),
                tip_gap_mm=round((C.TIP_Y - field.bounds[3]) * 1000, 2), px=[Wp, Hp])
    with open(meta_p, "w") as fh:
        json.dump(dict(key=key, bounds=[x0, y0, x1, y1], info=info), fh, indent=1)
    print("field mask %dx%d in %.1f s: %s" % (Wp, Hp, time.time() - t0, info), flush=True)
    return path, (x0, y0, x1, y1), info


def _aov(nodes, links, name, sock=None, value=None):
    n = nodes.new("ShaderNodeOutputAOV")
    n.aov_name = name
    if sock is not None:
        links.new(sock, n.inputs["Value"])
    else:
        n.inputs["Value"].default_value = value
    return n


def add_field(face, mask_path, bounds):
    """The field as an emission under the face's clear coat (Principled emission sits below the coat layer), face
    part only, so the holes, the throat, the 4 mm band and the wall never emit. Only the plateau is emitted; the mask's
    channels go out as AOVs (kq_plate, kq_line, kq_in, kq_face = 1) for the comp."""
    m = face.data.materials[0].copy()
    m.name = "K12_FaceField"
    face.data.materials[0] = m
    m.cycles.emission_sampling = "NONE"   # seen, not a lamp: it does not light the bores
    nb = K.NB(m)
    nodes = m.node_tree.nodes
    if PACE:
        # kq_canon.mat_pace: the coat Principled (its Coat Weight carries the tape flip) and the tape parity node
        b = next(n for n in nodes if n.type == "BSDF_PRINCIPLED" and n.inputs["Coat Weight"].is_linked)
        hz = next(n for n in nodes if n.type == "MATH" and n.operation == "LESS_THAN"
                  and n.inputs[0].is_linked and n.inputs[0].links[0].from_node.type == "MATH"
                  and n.inputs[0].links[0].from_node.operation == "MODULO")
    else:
        b = next(n for n in nodes if n.type == "BSDF_PRINCIPLED" and n.inputs["Anisotropic Rotation"].is_linked)
        hn = next(n for n in nodes if n.type == "TEX_IMAGE" and n.image and os.path.basename(n.image.filepath) == "height16.png")
    x0, y0, x1, y1 = bounds
    u, v, _ = nb.coords("UV")
    cv = nodes.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", u, x0), x1 - x0), cv.inputs[0])
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", v, y0), y1 - y0), cv.inputs[1])
    tex = L._img(nb, cv.outputs[0], mask_path, "Non-Color", interp="Linear", ext="CLIP")
    sep = nodes.new("ShaderNodeSeparateColor")
    nb.l.new(tex.outputs["Color"], sep.inputs["Color"])
    if PACE:
        mod = nb.math("MULTIPLY_ADD", hz.outputs[0], P_TAPE_K[1], P_TAPE_K[0])
    else:
        th = nb.smooth(hn.outputs["Color"], TOW_REMAP[0], TOW_REMAP[1]) if TOW_REMAP else hn.outputs["Color"]
        mod = nb.math("MULTIPLY_ADD", th, TOW_K[1], TOW_K[0])
    ew = nb.math("MULTIPLY", nb.math("MULTIPLY", sep.outputs[0], mod), FIELD_E)
    v1 = nodes.new("ShaderNodeVectorMath")
    v1.operation = "SCALE"
    v1.inputs[0].default_value = lin_hex(FIELD_HEX, "lum")
    nb.l.new(ew, v1.inputs["Scale"])
    nb.l.new(v1.outputs["Vector"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.0
    for name, s in zip(("kq_plate", "kq_line", "kq_in"), sep.outputs):
        _aov(nodes, nb.l, name, s)
    _aov(nodes, nb.l, "kq_face", value=1.0)
    face.lightgroup = "field"
    return m


def darken_bores(holes):
    """Shot-local: kq_canon's bore lining darkens with |z| (both lips light); seen 7 deg off axis through a 38 mm hole
    the far wall and its exit lip showed as a grey half-disc. Here the lining darkens toward the far exit and stays dark."""
    m = holes.data.materials[0].copy()
    m.name = "K12_Bore"
    holes.data.materials[0] = m
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.inputs["Surface"].is_linked)
    mx = out.inputs["Surface"].links[0].from_node   # kq_canon._bore_wrap's mix (lining <-> dark)
    assert mx.type == "MIX_SHADER", mx.type
    mul = mx.inputs[0].links[0].from_node            # smooth(|z|) x occ
    mul.inputs[1].default_value = BORE_OCC
    sm_ = mul.inputs[0].links[0].from_node           # the smoothstep (map range)
    ab = sm_.inputs["Value"].links[0].from_node      # ABSOLUTE(z)
    assert ab.type == "MATH" and ab.operation == "ABSOLUTE", ab.operation
    ab.operation = "MULTIPLY"                        # z itself: dark from 7.5 mm in to the far exit
    ab.inputs[1].default_value = 1.0
    blk = mx.inputs[2].links[0].from_node
    blk.inputs["Base Color"].default_value = (BORE_COL, BORE_COL, BORE_COL * 1.08, 1)
    return m


# ------------------------------------------------------------------ studio
def backdrop():
    """Camera-only graphite: an elliptical halo behind the head (BG_C) falling to BG_E at the left and top edges."""
    yaw = math.radians(YAW)
    cx = TGT[0] + (BG_Z - TGT[2]) * math.tan(yaw)   # behind the head along the camera's line of sight
    centre = Vector((cx, 0.0, BG_Z))
    bg = K.plane("Backdrop", (5.0, 3.0), tuple(centre), normal_to=tuple(centre + Vector((0, 0, 1))))
    c, e = K.emit_for(BG_C), K.emit_for(BG_E)

    def s(nb):
        x, y, _ = nb.coords("Object")
        xr = nb.math("DIVIDE", x, BG_RX)
        yr = nb.math("DIVIDE", y, BG_RY)
        r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", xr, xr), nb.math("MULTIPLY", yr, yr)))
        return nb.lerp(nb.smooth(r, 0.0, 1.0), c, e)

    bg.data.materials.append(K.emitter_mat("BackdropMat", BG_TINT, s, additive=False))
    K.visibility(bg, camera=True, diffuse=False, glossy=False, shadow=False)
    bg.lightgroup = "stage"
    return bg


def camera(sc):
    yaw = math.radians(YAW)
    cam_loc = Vector(TGT) + Vector((math.sin(yaw), 0.0, math.cos(yaw))) * CAM_D
    cd = bpy.data.cameras.new("Cam")
    cd.lens = LENS
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = SENSOR
    cd.shift_x = -(CX - 0.5)
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = FSTOP
    cd.dof.focus_distance = CAM_D - C.ZT
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    CT.look_at(cam, cam_loc, TGT)
    sc.camera = cam
    return cam, cam_loc


def grp(ob, g):
    if ob is not None:
        ob.lightgroup = g
    return ob


def _face_grid(step=0.002):
    """Face sample points (model metres, z = ZT): the field's face above the bridge, holes removed."""
    from shapely import contains_xy
    from shapely.geometry import Point
    from shapely.ops import unary_union
    face, _, _ = field_polys()
    hl = unary_union([Point(x * C.U, y * C.U).buffer(r * C.U, 16) for (x, y, r) in C.holes_canon()])
    face = face.difference(hl)
    x0, y0, x1, y1 = face.bounds
    X, Y = np.meshgrid(np.arange(x0, x1, step), np.arange(y0, y1, step))
    ok = contains_xy(face, X, Y)
    return np.stack([X[ok], Y[ok], np.full(ok.sum(), C.ZT)], axis=1)


def _spot_att(Lp, axis, pts, cos_h, smooth):
    d = pts - Lp
    d /= np.linalg.norm(d, axis=1)[:, None]
    t = np.clip((d @ axis - cos_h) / smooth, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def pool_aim():
    """The spot pool: position from POOL_DIR, a crisp cone whose edge crosses the face diagonally. Returns (Lp, target,
    blend, Q (a face point on the edge, mid-blend), info). blend is solved for POOL_EDGE (10-90 % width along POOL_U at
    Q), the edge's position for POOL_FRAC of the face lit (attenuation >= 0.5)."""
    pts = _face_grid()
    c0 = np.array([0.0, 0.03, C.ZT])
    Lp = c0 + np.array(POOL_DIR) / np.linalg.norm(POOL_DIR) * POOL_DIST
    u = np.array([POOL_U[0], POOL_U[1], 0.0])
    u /= np.linalg.norm(u)
    half = math.radians(POOL_DEG) / 2
    cos_h = math.cos(half)

    def aim(Q, blend):
        smooth = (1 - cos_h) * blend
        cos_m = cos_h + 0.5 * smooth          # mid-blend iso-angle passes through Q
        dq = (Q - Lp) / np.linalg.norm(Q - Lp)
        lo, hi = 0.0, 3.0                     # target T = Q + t u, angle(T - Lp, Q - Lp) = acos(cos_m)
        for _ in range(60):
            t = 0.5 * (lo + hi)
            T = Q + u * t
            a = (T - Lp) / np.linalg.norm(T - Lp)
            if a @ dq > cos_m:
                lo = t
            else:
                hi = t
        T = Q + u * 0.5 * (lo + hi)
        return T, (T - Lp) / np.linalg.norm(T - Lp), smooth

    def edge_w(Q, blend):
        T, ax, smooth = aim(Q, blend)
        s = np.linspace(-0.3, 0.3, 6001)
        line = Q[None, :] + s[:, None] * u[None, :]
        at = _spot_att(Lp, ax, line, cos_h, smooth)
        if not (at >= 0.9).any() or not (at < 0.1).any():
            return 1.0
        return float(s[np.argmax(at >= 0.9)] - s[np.argmax(at >= 0.1)])

    def frac(sq, blend):
        Q = c0 + u * sq
        T, ax, smooth = aim(Q, blend)
        return float((_spot_att(Lp, ax, pts, cos_h, smooth) >= 0.5).mean())

    blend = POOL_BLEND if POOL_BLEND else 0.05
    sq = 0.0
    for _ in range(3):
        lo, hi = -0.15, 0.20                  # frac falls as Q moves toward the lit side
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if frac(mid, blend) > POOL_FRAC:
                lo = mid
            else:
                hi = mid
        sq = 0.5 * (lo + hi)
        if POOL_BLEND:
            break
        Q = c0 + u * sq
        blo, bhi = 0.002, 0.6
        for _ in range(40):
            bm = math.sqrt(blo * bhi)
            if edge_w(Q, bm) < POOL_EDGE:
                blo = bm
            else:
                bhi = bm
        blend = math.sqrt(blo * bhi)
    Q = c0 + u * sq
    T, ax, smooth = aim(Q, blend)
    info = dict(Lp=[round(v, 3) for v in Lp], T=[round(v, 4) for v in T], blend=round(blend, 4), Q=[round(v, 4) for v in Q],
                lit=round(frac(sq, blend), 3), edge_mm=round(edge_w(Q, blend) * 1000, 1))
    print("pool:", info, flush=True)
    return Vector(Lp), Vector(T), blend, Vector(Q), info


def gloss_box(name, cam_loc, Q, u, strength):
    """A large glossy-only gradient softbox whose reflection in the coat IS designed on the face: k10_lib.sky_projected's
    mirrored-camera projection, a half-plane edge along the pool's diagonal (through Q, perpendicular to u, offset
    GLOSS_OFF toward the lit side, GLOSS_EDGE wide), brightest at the edge and falling to GLOSS_G0 over GLOSS_W inside,
    bounded to the face (GLOSS_BOUND). Diffuse ray visibility off, and a honeycomb (K05's): it emits only along the
    mirror path to the camera, so the fibres' broad sheen lobe cannot gather it from the whole face."""
    z_face = C.ZT
    cm = Vector((cam_loc[0], cam_loc[1], 2 * z_face - cam_loc[2]))
    Cc = Vector((0.0, 0.03, z_face))
    d = (Cc - Vector(cam_loc)).normalized()
    r = (d - 2 * d.dot(Vector((0, 0, 1))) * Vector((0, 0, 1))).normalized()
    ob = K.plane(name, (4.0, 4.0), tuple(Cc + r * 1.6), normal_to=tuple(Cc))
    ux, uy = float(u[0]), float(u[1])
    qx, qy = float(Q[0]) + ux * GLOSS_OFF, float(Q[1]) + uy * GLOSS_OFF
    bx_, by_, r0, r1 = GLOSS_BOUND
    tol = math.radians(GLOSS_TOL)

    def s(nb):
        geo = nb.n.new("ShaderNodeNewGeometry")
        sep = nb.n.new("ShaderNodeSeparateXYZ")
        nb.l.new(geo.outputs["Position"], sep.inputs["Vector"])
        X, Y, Z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
        t = nb.math("DIVIDE", z_face - cm.z, nb.math("SUBTRACT", Z, cm.z))
        px = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", X, cm.x), t, cm.x)
        py = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", Y, cm.y), t, cm.y)
        sd = nb.math("ADD", nb.math("MULTIPLY", nb.math("SUBTRACT", px, qx), ux),
                     nb.math("MULTIPLY", nb.math("SUBTRACT", py, qy), uy))     # + toward the lit side (m)
        g = nb.smooth(sd, -GLOSS_EDGE / 2, GLOSS_EDGE / 2)
        g = nb.math("MULTIPLY", g, nb.math("MULTIPLY_ADD", nb.smooth(sd, GLOSS_W, 0.0), 1 - GLOSS_G0, GLOSS_G0))
        ex, ey = nb.math("SUBTRACT", px, bx_), nb.math("SUBTRACT", py, by_)
        rr = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", ex, ex), nb.math("MULTIPLY", ey, ey)))
        g = nb.math("MULTIPLY", g, nb.smooth(rr, r1, r0))
        # honeycomb: only toward the mirrored camera
        vs = nb.n.new("ShaderNodeVectorMath"); vs.operation = "SUBTRACT"
        vs.inputs[0].default_value = tuple(cm)
        nb.l.new(geo.outputs["Position"], vs.inputs[1])
        vn = nb.n.new("ShaderNodeVectorMath"); vn.operation = "NORMALIZE"
        nb.l.new(vs.outputs[0], vn.inputs[0])
        vd = nb.n.new("ShaderNodeVectorMath"); vd.operation = "DOT_PRODUCT"
        nb.l.new(geo.outputs["Incoming"], vd.inputs[0])
        nb.l.new(vn.outputs[0], vd.inputs[1])
        g = nb.math("MULTIPLY", g, nb.smooth(vd.outputs["Value"], math.cos(tol), math.cos(tol * 0.35)))
        return nb.math("MULTIPLY", g, strength)

    ob.data.materials.append(K.emitter_mat(name + "Mat", WHITE, s, additive=True))
    K.visibility(ob, camera=False, diffuse=False, glossy=True, shadow=False)
    ob.lightgroup = "gloss"
    return ob


def lights(P, cam_loc):
    head = [P[k] for k in P if k not in ("grip", "cap", "capmark")]
    head_norim = [ob for ob in head if ob is not P["rim"]]
    ZT = C.ZT
    # face: the spot pool (a crisp diagonal edge, 40 % of the face lit), the fill alone in the shade
    Lp, T, blend, Q, info = pool_aim()
    if POOL > 0 or not PACE:
        pl = studio.spot_light("lw_pool", tuple(Lp), POOL, POOL_DEG, blend=blend, color=(1.0, 0.985, 0.97),
                               target=tuple(T), radius=POOL_R)
        L.link_only(pl, head_norim, "pool_recv")  # not the rim: the white hairline must stand above the white face
        grp(pl, "pool")
    if RIM_POOL > 0:                              # the rim gets the same pool, dimmer: the edge a step below the face
        pr = studio.spot_light("lw_pool_rim", tuple(Lp), POOL * RIM_POOL, POOL_DEG, blend=blend,
                               color=(1.0, 0.985, 0.97), target=tuple(T), radius=POOL_R)
        L.link_only(pr, [P["rim"]], "pool_rim_recv")
        grp(pr, "pool")
    if FILL > 0 or not PACE:
        fl = studio.area_light("lw_fill", FILL_AT, 1.0, FILL, color=(0.94, 0.96, 1.0), target=(0.0, -0.03, 0.0))
        L.link_only(fl, head, "fill_recv")
        grp(fl, "fill")
    if PACE and P_WEAVE > 0:
        # the weave card (K08 / K11 / K06): P_WEAVE_UP deg off the face's mirror direction, seen only by the fibre lobes
        c_ = Vector((0.0, 0.0, ZT))
        n_ = Vector((math.sin(math.radians(YAW)) * 0.0, 0.0, 1.0))
        vv_ = (Vector(cam_loc) - c_).normalized()
        d_ = (2 * n_.dot(vv_) * n_ - vv_).normalized()
        hz_ = d_.cross(Vector((0.0, 1.0, 0.0))).normalized()
        d_up = (Matrix.Rotation(math.radians(P_WEAVE_UP), 3, hz_) @ d_).normalized()
        if d_up.y < d_.y:
            d_up = (Matrix.Rotation(math.radians(-P_WEAVE_UP), 3, hz_) @ d_).normalized()
        import k789_lib as KL7
        wv = KL7.gradient_card("lg_weave", tuple(c_ + d_up * P_WEAVE_D), P_WEAVE_SIZE, P_WEAVE, tuple(c_),
                               color=WHITE, axis="v", lo=0.0, hi=1.0, floor=P_WEAVE_FLOOR)
        L.link_only(wv, [P["face"], P["neck"], P["rim"]], "weave_recv")
        grp(wv, "sky")
    if PACE and P_LOW > 0:
        # the lower head (bridge, throat shoulders, the band's lower run): a soft card only that region mirrors,
        # graded across (bright camera-left), so in full the chin reads as lit black 12K, never a black bezel
        c2 = Vector((0.0, P_LOW_Y, ZT))
        vv2 = (Vector(cam_loc) - c2).normalized()
        d2 = (2 * vv2.z * Vector((0, 0, 1)) - vv2).normalized()
        import k789_lib as KL7
        lw = KL7.gradient_card("lg_low", tuple(c2 + d2 * P_LOW_D), P_LOW_SIZE, P_LOW, tuple(c2), color=WHITE,
                               axis="u", lo=1.0, hi=0.0, floor=P_LOW_FLOOR)
        L.link_only(lw, [P["face"], P["neck"], P["rim"]], "low_recv")
        grp(lw, "sky")
    if SKY > 0:
        a_, b_ = (-0.13, 0.155, ZT), (0.13, -0.08, ZT)
        sky = L.sky_projected("lg_sky", tuple(cam_loc), ZT, a_, b_, (0.0, 0.02, ZT), (3.0, 3.0), 1.0, 0.0, 0.0, SKY,
                              color=WHITE, band=(0.0, SKY_BW), group="sky")
        L.link_only(sky, [P["face"], P["holes"], P["rim"], P["neck"]], "sky_recv")
    # gloss: the big glossy-only gradient softbox along the pool's diagonal (the coat's sheen over the lit part)
    u = Vector((POOL_U[0], POOL_U[1], 0.0)).normalized()
    gb = gloss_box("lg_gloss", cam_loc, Q, u, GLOSS)
    L.link_only(gb, [P["face"]], "gloss_recv")
    # rim: white hairline on the upper-left edge, one dim ember hairline on the right edge (own group), the wall sliver
    grp(CT.edge_ribbon("lg_white", cam_loc, lambda x, y: CT.sm(-x, 0.004, 0.03) * CT.sm(y, 0.0, 0.06) if x < 0 else 0.0,
                       PHI, 0.15, 0.03, WHITE_LINE, WHITE, [P["rim"]]), "rim")
    grp(CT.edge_ribbon("lg_ember", cam_loc,
                       lambda x, y: CT.sm(x, 0.02, 0.06) * CT.sm(y, -0.10, -0.05) * CT.sm(-y, -0.11, -0.04) if x > 0 else 0.0,
                       PHI, 0.15, 0.03, EMBER_LINE, WHITE if PACE else EMBER, [P["rim"]]), "ember")
    wl = CT.strip("lg_wall", WALL_AT, (0.13, 0.0, 0.0), 0.5, 0.1, WALL, recv=[P["wall"], P["etchR"]])
    grp(wl, "wall")
    # handle: one long soft strip down the grip (wrap from the band to the cap, groove, Q), the cap's box
    grp(CT.strip("lg_grip", GRIP_AT, GRIP_TGT, GRIP_LEN, GRIP_W, GRIP,
                 recv=[P["grip"], P["cap"], P["capmark"]]), "handle")
    grp(CT.strip("lg_grip_neck", GRIP_AT, GRIP_TGT, GRIP_LEN, GRIP_W, GRIP, recv=[P["neck"]]), "neck")   # same lamp
    if GRIP2 > 0:
        grp(CT.strip("lg_grip2", (0.30, -0.22, 0.12), (0.0, -0.22, 0.0), 0.32, 0.03, GRIP2,
                     recv=[P["grip"], P["cap"], P["neck"]]), "handle")
    if CAP > 0:
        grp(CT.cap_light("lg_cap", cam_loc, P, CAP, size=CAP_SIZE, dist=CAP_DIST), "handle")
    # serial: K10's short rake from camera-left (graphite frost on white: a rake only adds the cut-edge glint)
    S = Vector((0.0, C.SERIAL_LINE["y"], ZT))
    rd = Vector((-math.cos(math.radians(16)), 0.25, math.sin(math.radians(16)))).normalized()
    rk = studio.area_light("lg_rake", tuple(S + rd * 0.125), 0.05, RAKE, color=(1.0, 0.985, 0.965), size_y=0.005,
                           target=tuple(S), spread=RAKE_SPREAD)
    L.link_only(rk, [P["face"]], "rake_recv")
    grp(rk, "serial")
    # lip crescents (holes only, full only): one thin crescent on the lower-right of every lip (facing the key's upper
    # left), not a ring. A glossy-only ribbon 2 m away (every hole sees it from the same direction) laid out in
    # direction space: for each lip azimuth phi in LIP_PHI +- LIP_SPAN, the directions that the lip's normals tilted
    # LIP_TILT +- LIP_DT mirror into the camera. So each lip catches exactly that arc and that band of its profile.
    c0 = Vector((0.0, 0.03, ZT))
    vv = (Vector(cam_loc) - c0).normalized()

    def ldir(phd, thd):
        ph, th = math.radians(phd), math.radians(thd)
        d_in = Vector((-math.cos(ph), -math.sin(ph), 0.0))
        nl = (d_in * math.sin(th) + Vector((0.0, 0.0, 1.0)) * math.cos(th)).normalized()
        return (2 * nl.dot(vv) * nl - vv).normalized()

    A, B, W = [], [], []
    n_ = 48
    for i in range(n_ + 1):
        t = i / n_
        phd = LIP_PHI - LIP_SPAN + 2 * LIP_SPAN * t
        A.append(tuple(c0 + ldir(phd, LIP_TILT - LIP_DT) * LIP_DIST))
        B.append(tuple(c0 + ldir(phd, LIP_TILT + LIP_DT) * LIP_DIST))
        W.append(CT.sm(t, 0.0, 0.25) * CT.sm(1.0 - t, 0.0, 0.25))
    lp = L.weighted_ribbon("lg_lip", A, B, W, LIP, color=lin_hex(FIELD_HEX, "max"), soft_v=0.3)
    L.link_only(lp, [P["holes"]], "lip_recv")
    grp(lp, "lip")
    return info


def build(o):
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 6
    sc.cycles.diffuse_bounces = 2
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.blur_glossy = 0.5
    sc.cycles.light_sampling_threshold = 0.0
    t0 = time.time()
    root, P = C.build_racket("KQ", feel=FEEL, serial="KQ-000427", mat_opts=None if PACE else MAT_OPTS, mark_az=YAW)
    print("racket built %.1f s" % (time.time() - t0), flush=True)
    mask, bounds, info = field_mask()
    add_field(P["face"], mask, bounds)
    darken_bores(P["holes"])
    cam, cam_loc = camera(sc)
    backdrop()
    pinfo = lights(P, cam_loc)
    bpy.context.view_layer.update()
    # every emitter must sit in a light group, or it is missing from the passes
    for ob in sc.objects:
        if ob.type == "LIGHT" and not ob.lightgroup:
            raise RuntimeError("light without a group: " + ob.name)
        if ob.type == "MESH" and ob.data.materials and any(
                m and m.name.endswith("Mat") and any(n.type == "EMISSION" for n in m.node_tree.nodes)
                for m in ob.data.materials) and not ob.lightgroup:
            raise RuntimeError("emitter without a group: " + ob.name)
    sc["k12_info"] = json.dumps(info)
    sc["k12_pool"] = json.dumps(pinfo)
    return sc


# ------------------------------------------------------------------ passes
DENOISE = True


def setup_passes(sc, groups, out_dir, stem):
    """One OIDN-denoised linear EXR per light group (albedo + normal guides) plus the raw AOVs. Cycles writes emission
    into the Denoising Albedo pass, so every studio pass is denoised with (albedo - the field pass): with the plain
    albedo OIDN printed the field's boundary into the studio passes (a warm ghost line in base)."""
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in groups:
        vl.lightgroups.add(name=g)
    for a in AOVS:
        av = vl.aovs.add()
        av.name = a
        av.type = "VALUE"
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    rl = tr.nodes.new("CompositorNodeRLayers")
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = out_dir
    fo.format.file_format = "OPEN_EXR"
    fo.format.color_mode = "RGB"
    fo.format.color_depth = "16"
    fo.format.exr_codec = "ZIP"
    fo.file_slots.clear()
    sub = tr.nodes.new("CompositorNodeMixRGB")
    sub.blend_type = "SUBTRACT"
    sub.use_clamp = True
    sub.inputs[0].default_value = 1.0
    tr.links.new(rl.outputs["Denoising Albedo"], sub.inputs[1])
    tr.links.new(rl.outputs["Combined_field"], sub.inputs[2])
    first = None
    for g in groups:
        slot = f"{stem}_{g}_"
        fo.file_slots.new(slot)
        if DENOISE:
            dn = tr.nodes.new("CompositorNodeDenoise")
            dn.prefilter = "ACCURATE"
            dn.use_hdr = True
            tr.links.new(rl.outputs["Combined_" + g], dn.inputs["Image"])
            tr.links.new(rl.outputs["Denoising Normal"], dn.inputs["Normal"])
            tr.links.new(rl.outputs["Denoising Albedo"] if g == "field" else sub.outputs[0], dn.inputs["Albedo"])
            src = dn.outputs["Image"]
        else:
            src = rl.outputs["Combined_" + g]
        tr.links.new(src, fo.inputs[slot])
        first = first or src
    for a in AOVS:
        slot = f"{stem}_{a}_"
        fo.file_slots.new(slot)
        tr.links.new(rl.outputs[a], fo.inputs[slot])
    comp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(first, comp.inputs["Image"])


# ------------------------------------------------------------------ comp
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def _dirs(o):
    out = os.path.join(studio.OUT, o["out"])
    return os.path.join(os.path.dirname(out), "passes"), os.path.basename(out)


def gblur(a, sigma):
    """Separable Gaussian, sigma in px."""
    r = max(1, int(math.ceil(3 * sigma)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / max(sigma, 1e-3)) ** 2).astype(np.float32)
    k /= k.sum()
    out = np.zeros_like(a)
    pad = np.pad(a, ((0, 0), (r, r), (0, 0)), mode="edge")
    for i, w in enumerate(k):
        out += w * pad[:, i:i + a.shape[1]]
    pad = np.pad(out, ((r, r), (0, 0), (0, 0)), mode="edge")
    out2 = np.zeros_like(a)
    for i, w in enumerate(k):
        out2 += w * pad[i:i + a.shape[0]]
    return out2


def to_display(lin, sc):
    """Linear (n, 3) or (h, w, 3) -> display 0..255 float, through the scene view transform (via a temp PNG)."""
    from PIL import Image
    a = lin if lin.ndim == 3 else lin[None, :, :]
    tmp = os.path.join(studio.OUT, "_k12_disp_%d.png" % os.getpid())
    L.save_display(np.ascontiguousarray(a, dtype=np.float32), tmp, sc)
    d = np.asarray(Image.open(tmp)).astype(np.float32)
    os.remove(tmp)
    if d.max() > 255.5:
        d = d / 257.0
    d = d[..., :3][::-1]      # save_display takes rows bottom-up: flip back
    return d if lin.ndim == 3 else d[0]


def line_lin(sc):
    """The hairline's linear colour so that it reads as LINE_DISPLAY (the page's amber, #e3a467) through AgX Punchy.
    Per-channel fixed-point solve through the view transform, cached in shots/k12/line_cal.json."""
    p = os.path.join(MASK_DIR, "line_cal.json")
    key = "%s_%s_%s" % (sc.view_settings.view_transform, sc.view_settings.look, LINE_DISPLAY)
    if os.path.exists(p):
        with open(p) as fh:
            j = json.load(fh)
        if j.get("key") == key:
            return np.array(j["lin"], np.float32)
    tgt = np.array(LINE_DISPLAY, np.float32)

    def s2l(v):
        v = np.clip(np.asarray(v, np.float32) / 255.0, 1e-4, 1.0)
        return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)

    lin = s2l(tgt) * 1.5
    d = to_display(lin[None], sc)[0]
    for _ in range(40):
        if np.abs(d - tgt).max() <= 0.6:
            break
        lin = (lin * (s2l(tgt) / s2l(d))).astype(np.float32)
        d = to_display(lin[None], sc)[0]
    with open(p, "w") as fh:
        json.dump(dict(key=key, lin=lin.tolist(), display=d.tolist()), fh)
    print("line: linear %s -> display %s (target %s)" % (np.round(lin, 4).tolist(), np.round(d, 1).tolist(),
                                                           list(LINE_DISPLAY)), flush=True)
    return lin


def _bloom(src, h_full):
    lum = src @ LUMA
    k = np.clip(lum - BLOOM_THR, 0.0, None) / np.maximum(lum, 1e-6)
    hi = src * k[..., None]
    sig = BLOOM_SIGMA * h_full
    return gblur(hi, sig) * BLOOM_AMT if hi.max() > 0 else np.zeros_like(src)


def comp(o, sc=None):
    od, stem = _dirs(o)
    with open(os.path.join(od, stem + "_meta.json")) as fh:
        meta = json.load(fh)
    if sc is None:
        sc = studio.reset()
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    gains = {g: 1.0 for g in GROUPS}
    for kv in o["gain"]:
        k, v = kv.split("=")
        gains[k] = float(v)
    P = {}
    for g in GROUPS:
        p = os.path.join(od, f"{stem}_{g}.exr")
        P[g] = L.load_lin(p) * gains[g] if os.path.exists(p) else None
    shape = next(a for a in P.values() if a is not None).shape
    zero = np.zeros(shape, np.float32)
    for g in GROUPS:
        if P[g] is None:
            P[g] = zero
    A = {}
    for a in AOVS:
        p = os.path.join(od, f"{stem}_{a}.exr")
        A[a] = np.clip(L.load_lin(p)[..., 0], 0.0, 1.0) if os.path.exists(p) else np.zeros(shape[:2], np.float32)
    # the studio cross-fades from its in-field level (plateau) to its outside level over the field's own 3 mm roll-off
    # (kq_plate), so there is no step in the studio light at the line; on every other part of the head (rim, bores,
    # neck, throat walls) kq_plate is 0: the outside level
    w_in = A["kq_plate"][..., None]
    base = sum(P[g] for g in GROUPS if g not in FULL_ONLY)
    # full: the studio graded under the field; outside it the fill stays at base's shade (white twill in shade)
    stud = zero.copy()
    for g in GROUPS:
        if g in FULL_ONLY:
            continue
        if g in FACE_GROUPS:
            k_in = GLOSS_FULL if g == "gloss" else FACE_DIM
            k_out = BEZEL_FILL if g == "fill" else BEZEL_DIM
            stud += P[g] * (w_in * k_in + (1.0 - w_in) * k_out)
        elif g == "ember":
            stud += P[g] * EMBER_FULL
        elif g == "serial":
            stud += P[g] * SERIAL_FULL
        elif g == "neck":
            stud += P[g] * NECK_FULL
        else:
            stud += P[g]
    lip = P["lip"] * LIP_GAIN
    fld0 = P["field"]
    E = line_lin(sc)
    a_line = np.clip(A["kq_line"] * LINE_ALPHA, 0.0, 1.0)[..., None]
    # the field grade: per-channel gains so the plateau composite lands at FIELD_TARGET (median over the plateau)
    pl = (A["kq_plate"] > 0.995) & (A["kq_line"] < 0.005) & (A["kq_in"] > 0.995)
    ys, xs = np.nonzero(pl)
    fgain = np.ones(3, np.float32)
    if len(ys) > 50:
        rng = np.random.default_rng(7)
        sel = rng.choice(len(ys), size=min(4096, len(ys)), replace=False)
        s_st, s_f = stud[ys[sel], xs[sel]], fld0[ys[sel], xs[sel]]
        tgt = np.array(FIELD_TARGET, np.float32)

        def s2l(v):
            v = np.clip(v / 255.0, 1e-4, 1.0)
            return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)

        for it in range(24):
            f = s_f * fgain
            lum = f @ LUMA
            bl = f * (np.clip(lum - BLOOM_THR, 0, None) / np.maximum(lum, 1e-6))[:, None] * BLOOM_AMT
            med = np.median(to_display(s_st + f + bl, sc), axis=0)
            if np.abs(med - tgt).max() <= 0.6:
                break
            fgain *= (s2l(tgt) / s2l(med)) ** 1.4
        print("field grade: gains %s -> plateau median display %s (target %s)" % (
            np.round(fgain, 4).tolist(), np.round(med, 1).tolist(), list(FIELD_TARGET)), flush=True)
    fld = fld0 * fgain
    bloom = _bloom(fld + E * a_line, meta["full_h"])
    pre = stud + fld + lip
    full = pre * (1.0 - a_line) + E * a_line + bloom
    outs = {}
    name = o.get("as") or o["out"]
    base_p = os.path.join(studio.OUT, name + "-base.png")
    full_p = os.path.join(studio.OUT, name + "-full.png")
    L.save_display(base, base_p, sc)
    L.save_display(full, full_p, sc)
    outs["base"], outs["full"] = base_p, full_p
    report(base_p, full_p, A, meta)
    # phone / card crop (x .435 to .885, full height), only from a full frame
    if not meta.get("crop"):
        w = shape[1]
        xa, xb = int(round(PHONE_X[0] * w)), int(round(PHONE_X[1] * w))
        for k, src in (("base", base), ("full", full)):
            pp = os.path.join(studio.OUT, name + "-phone-%s.png" % k)
            L.save_display(np.ascontiguousarray(src[:, xa:xb]), pp, sc)
            outs["phone-" + k] = pp
        sheet(o, outs)
    with open(os.path.join(studio.OUT, name + "-comp.json"), "w") as fh:
        json.dump(dict(field_gain=fgain.tolist(), line=E.tolist(), outs=outs), fh)
    print("comp", json.dumps(outs), flush=True)
    return outs


def report(base_p, full_p, A, meta):
    """Measurements for the critique: display luma and colour of the regions that matter."""
    from PIL import Image

    def load(p):
        a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
        return a, a @ LUMA

    b, bl = load(base_p)
    f, flm = load(full_p)
    fl = lambda k: A[k][::-1]   # AOVs are bottom-up
    plate, line, ins, face = fl("kq_plate"), fl("kq_line"), fl("kq_in"), fl("kq_face")
    h, w = bl.shape
    cl = bl[:, : int(CLEAN_X * w)]
    print("base: max %.0f (>=250: %d px) clean side luma %.1f..%.1f (p1 %.1f p99 %.1f)" % (
        bl.max(), int((bl >= 250).sum()), cl.min(), cl.max(), np.percentile(cl, 1), np.percentile(cl, 99)))
    fc = (ins > 0.99) & (face > 0.99)
    if fc.any():
        v = bl[fc]
        print("base face (field area): p5 %.0f p25 %.0f p50 %.0f p75 %.0f p95 %.0f max %.0f | lit >=190: %.0f%%, >=150: %.0f%%,"
              " shade p10-p40 %.0f..%.0f" % (*np.percentile(v, [5, 25, 50, 75, 95]), v.max(), 100 * (v >= 190).mean(),
                                             100 * (v >= 150).mean(), *np.percentile(v, [10, 40])))
    ln = line > 0.5
    if ln.any():
        rb = b[..., 0] - b[..., 2]
        near = (plate > 0.3) & (plate < 0.9) & (face > 0.99)
        print("base |R-B| on the field boundary: mean %.1f p95 %.1f max %.1f (nearby inside: mean %.1f p95 %.1f)" % (
            np.abs(rb[ln]).mean(), np.percentile(np.abs(rb[ln]), 95), np.abs(rb[ln]).max(),
            np.abs(rb[near]).mean() if near.any() else -1, np.percentile(np.abs(rb[near]), 95) if near.any() else -1))
        fr = f[ln & (line > 0.9)] if (ln & (line > 0.9)).any() else f[ln]
        top = fr[np.argsort(fr[:, 0])[-max(1, len(fr) // 4):]]
        print("full hairline (top quarter by R): median rgb %s" % np.round(np.median(top, axis=0), 0).tolist())
    pz = (plate > 0.995) & (line < 0.005) & (face > 0.99)
    if pz.any():
        med = np.median(f[pz], axis=0)
        print("full plateau: median rgb %s luma %.1f, max %.0f, any channel 255: %d px" % (
            np.round(med, 0).tolist(), float(med @ LUMA), flm[pz].max(), int((f.max(axis=2) >= 254.5).sum())))
        bs = max(4, int(round(h / 64)))
        vals = []
        for y in range(0, h - bs, bs):
            for x in range(0, w - bs, bs):
                if pz[y:y + bs, x:x + bs].all():
                    vals.append(flm[y:y + bs, x:x + bs].mean())
        if vals:
            v = np.array(vals)
            m = np.median(v)
            print("full plateau blocks (%d px): median %.0f, %.0f..%.0f (%+.0f%% / %+.0f%%), n=%d" % (
                bs, m, v.min(), v.max(), 100 * (v.min() / m - 1), 100 * (v.max() / m - 1), len(v)))
    bz = (face > 0.99) & (ins < 0.01) & (line < 0.05)
    # the band: face pixels outside the field within about 4.5 mm of it
    px_mm = (BUTT_FRAC - TIP_FRAC) * meta["full_h"] / ((C.TIP_Y - C.BUTT_Y) * 1000.0)
    r = max(1, int(round(4.5 * px_mm)))
    near_f = ins > 0.5
    dil = near_f.copy()
    for _ in range(r):
        dil[1:] |= near_f[:-1]; dil[:-1] |= near_f[1:]; dil[:, 1:] |= near_f[:, :-1]; dil[:, :-1] |= near_f[:, 1:]
        near_f = dil.copy()
    band = bz & dil
    lower = bz & ~dil          # the face below the band: the bridge and the lower head around the throat
    pct = lambda v: "p10 %.0f p50 %.0f p90 %.0f" % tuple(np.percentile(v, [10, 50, 90]))
    if band.any():
        lit = bl >= 150        # where base's pool lights the band
        print("full band (4 mm, white twill in shade): pool side %s | shade side %s | base: pool side p50 %.0f, shade"
              " side p50 %.0f" % (pct(flm[band & lit]) if (band & lit).any() else "n/a", pct(flm[band & ~lit]),
                                  np.percentile(bl[band & lit], 50) if (band & lit).any() else -1,
                                  np.percentile(bl[band & ~lit], 50)))
    if lower.any():
        print("full bridge and lower head: %s | base %s" % (pct(flm[lower]), pct(bl[lower])))
    # twill legibility in the shade band: luma minus a 9 px box mean, std (away from the hairline)
    sb = band & (bl < 150) & (line < 0.001)
    if sb.sum() > 200:
        k = 9
        def hp(lum):
            c = np.pad(lum.astype(np.float64), ((k // 2 + 1, k // 2), (k // 2 + 1, k // 2))).cumsum(0).cumsum(1)
            box = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
            return float((lum - box[:lum.shape[0], :lum.shape[1]])[sb].std())
        print("twill in the shade band (high-pass std): full %.1f, base %.1f" % (hp(flm), hp(bl)))
    print("full: max %.0f (>=250: %d px)" % (flm.max(), int((flm >= 250).sum())), flush=True)


def sheet(o, outs):
    """Review sheet: base / full (wide), with the 16:10 crop and the phone crop outlined; then the phone crops."""
    from PIL import Image, ImageDraw
    ims = {k: Image.open(v).convert("RGB") for k, v in outs.items()}
    b, f = ims["base"], ims["full"]
    tw = 960
    th = int(b.height * tw / b.width)
    row = [b.resize((tw, th), Image.LANCZOS), f.resize((tw, th), Image.LANCZOS)]
    ph = [ims[k].resize((int(ims[k].width * th / ims[k].height), th), Image.LANCZOS) for k in ("phone-base", "phone-full") if k in ims]
    W = tw * 2 + 24
    Hs = th * 2 + 36
    out = Image.new("RGB", (W, Hs), (60, 60, 64))
    dr = ImageDraw.Draw(out)
    for i, im in enumerate(row):
        x = 8 + i * (tw + 8)
        out.paste(im, (x, 8))
        cw = int(th * 16 / 10)
        dr.rectangle([x + (tw - cw) // 2, 8, x + (tw + cw) // 2 - 1, 8 + th - 1], outline=(90, 160, 255))
        dr.rectangle([x + int(PHONE_X[0] * tw), 8, x + int(PHONE_X[1] * tw), 8 + th - 1], outline=(255, 150, 60))
        dr.line([x + int(CLEAN_X * tw), 8, x + int(CLEAN_X * tw), 8 + th - 1], fill=(120, 255, 120))
    x = 8
    for im in ph:
        out.paste(im, (x, th + 24))
        x += im.width + 8
    dst = os.path.join(studio.OUT, (o.get("as") or o["out"]) + "-sheet.png")
    out.save(dst)
    outs["sheet"] = dst


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = parse_args(argv)
    if o["comp"]:
        comp(o)
        return
    t0 = time.time()
    sc = build(o)
    print("scene built", round(time.time() - t0, 1), "s", flush=True)
    od, stem = _dirs(o)
    os.makedirs(od, exist_ok=True)
    setup_passes(sc, GROUPS, od, stem)
    full_w, full_h, off = o["w"], o["h"], (0, 0)
    if o["crop"]:
        x0, x1, y0, y1 = o["crop"]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
        off = (int(round(x0 * o["w"])), int(round(y0 * o["h"])))
    studio.render(os.path.join(os.path.dirname(o["out"]), "passes", stem + "__all"))
    L.collect_passes(od, stem, GROUPS + AOVS)
    with open(os.path.join(od, stem + "_meta.json"), "w") as fh:
        json.dump(dict(w=o["w"], h=o["h"], spp=o["spp"], crop=o["crop"], set=o["set"], full_w=full_w, full_h=full_h,
                       off=off, info=json.loads(sc["k12_info"]), pool=json.loads(sc["k12_pool"])), fh)
    comp(o, sc)
    print("rendered", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
