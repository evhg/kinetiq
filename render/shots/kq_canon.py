"""kq_canon: THE canonical KINETIQ racket (render audit 2026-10-22, section 4). Every shot builds its racket here.

Spec (the owner's review site): 455.0 mm long (tip y = +0.155 to butt y = -0.300), 260.0 mm wide (mesh 260.12), 38.0 mm thick,
42 holes = a crown of 8 (14.0 mm) along the top + 34 (12.4 mm) below. Command = soft EVA core, WHITE 3K twill face
(owner, 2026-10-22: white carbon with the weave clearly visible; the default for every shot that names no feel); Pace =
two-density EVA, black 12K face built stiffer (only where Pace is chosen or compared). Sealed core: the carbon shell closes round the core and lines all 42 holes,
so every bore and the throat are carbon-lined (dark), never foam.

Model space (as racket.py): metres, face in the XY plane, +Z out of the FRONT face, head up (+Y), handle down (-Y).
The root is an Empty at the origin (head centre); pose the root, never the parts.

    import kq_canon as C
    root, P = C.build_racket("KQ", feel="command", serial="KQ-000427")   # P: part name -> object
    r2, P2 = C.clone(root, "KQ2", serial="KQ-000428")                      # shares meshes, own serial
    C.parts(r2)["face"]                                                     # parts of any racket or clone

Parts (light-linking units; every object carries ob["kq_part"]):
  face        front lacquered face of the head (above NECK_SPLIT_Y), carries the laser-frosted throat serial
  back        rear face of the head
  rim         the outline's two 1.5 mm rounded edges (the weave folds over them)
  wall        the outline's flat 38 mm side wall (same twill, same gloss)
  neck        everything below NECK_SPLIT_Y: the bare-carbon neck (it is the ferrule: no separate part, no joint)
  throat      throat lip + wall (or thr00..thr15 with throat_segs=k10_lib.THROAT_SEGS, for K10-style edge ribbons)
  bridgewall  the throat wall under its top edge
  holes       42 hole lips + carbon-lined bores (dark with depth: they read as through-holes)
  grip        neutral-black overgrip, real helical wrap (27 mm pitch, overlap step, perforations), 11 mm top band
  cap         satin black anodised butt cap with one fine groove
  capmark     the engraved Q on the cap (the company logo is the Q; owner, 2026-10-22)
  etchR/etchL laser-frosted KINETIQ (right wall) / SWISS MADE (left wall); only with walls=True

Geometry: copied from k10_lib.build_head_k10 (fold UVs: the twill runs over every edge without a seam; analytic
normals) with per-hole radii, the canonical holes, and a canonical neck whose rounded edge grows from 1.5 mm to 12 mm
as it narrows to the handle section (33.0 x 29.0 mm), so the frame flows into the grip as one piece. The grip and cap
follow that same section. Materials: Command = mat_white, white 3K twill on K10's baked twill maps (tow tone, crevices,
fibre direction, relief) under a glass-clear coat (mat_opts={"white": 0} gives back K10's black twill exactly);
Pace = the v5 "fibre" 12K (2026-10-23; was k789_lib.mat_carbon_aniso's 12K + K11's coat flip): near-uniform black
tapes under one uniform clear coat, the checker only in the fibres' sheen direction, with a fine fibre normal, roughness
streaks and a slight crimp per tape (PACE; PACE_V4 restores the old one), on the fold UVs. The throat serial is
K10's laser-frost mark (mask in the face material) set like the measurement card: Saira wght 500, tabular figures.

Do not edit racket.py, studio.py, look_c.py, k789_lib.py, k12_lib.py or k10_lib.py: they are imported, never modified.
Self-test: ../bpyenv/bin/python shots/kq_canon.py   (builds both feels, asserts the spec, prints the measurements)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.geometry import tessellate_polygon  # noqa: E402

import racket  # noqa: E402
import k12_lib as K  # noqa: E402
import k10_lib as L  # noqa: E402
import k789_lib as KL  # noqa: E402

U = racket.U
T2 = racket.THICK / 2
ZT = T2
ASSETS = kqpaths.asset("canon")  # generated etch masks
FONT_SAIRA = kqpaths.font("Saira-var.ttf")
FONT_ARCHIVO = kqpaths.font("Archivo-var.ttf")

# ------------------------------------------------------------------ the spec
TIP_Y, BUTT_Y = 0.155, -0.300           # 455.0 mm overall
WIDTH, THICK = 0.2600, racket.THICK      # 260.0 mm (the FIP maximum, as racket-shape.ts), 38.0 mm
# The mesh measures 260.12 mm across (the plan outline's tessellation and 3 mm fillets): 0.12 mm over the FIP limit,
# about 0.5 px at 3200 px, invisible in any still. Cards, captions and claims quote 260.0 mm (racket-shape.ts), never
# the mesh's measured width. measure() asserts 260.0 +- 0.3 mm.
SERIAL = "KQ-000427"                     # one racket; a pair: -427 (front) and -428 (rear); three: -427..-429, left to right

# neck: the head flows into the handle as one carbon piece. Width 47 -> 33 mm from y -0.146 to -0.176 with an 18 mm
# concave fillet; thickness 38 -> 29 mm (NECK_TAPER); the rounded edge grows 1.5 -> 12 mm (NECK_ROUND) so the section
# arrives at the grip as a soft 33.0 x 29.0 mm rounded rectangle. Below y -0.176 the core runs straight on under the
# grip and ends (round, hidden) at y_cut.
NECK = dict(y_top=-0.146, hw_top=0.0235, y_end=-0.176, hw_end=0.0165, y_cut=-0.200, r_concave=0.018)
NECK_TAPER = (-0.150, -0.176, 0.763)     # y0 (full 38 mm), y1, thickness scale at y1
NECK_ROUND = (-0.150, -0.174, 0.012)     # y0 (1.5 mm edge), y1, edge radius at y1
NECK_SPLIT_Y = -0.150                    # face / neck light-linking boundary
# neck twill: the fold UVs offset each wall point along the outline's normal, which swirls (folds over) where the
# normal turns faster than the ~40 mm wall profile allows: the 18 mm concave fillet into the V. From NECK_UV[0] down to
# NECK_UV[1] the fold direction blends to the racket's cross axis, so below it the twill is laid along the handle axis
# (u around the section, v = y) and the tows run straight down the neck (critic G1: no fish-scale arcs). None = old UVs.
NECK_UV = (-0.095, -0.150)

# handle (K05's overgrip and cap, without the ferrule, at the 455 mm positions)
GRIP_Y = (-0.174, -0.2842)               # 110 mm, wraps over the last 2 mm of the neck taper
GRIP_PITCH = 0.027
TAPE = 0.0005
GRIP_BAND = 0.011                        # finishing band at the top
CAP_SHIFT, CAP_SCALE = 0.0073, 0.94
# K05's cap profile (r, y): flare, a cylindrical band, a fine groove, rounded end
CAP_PROF_K05 = [(0.0160, -0.2890), (0.0174, -0.2895), (0.0178, -0.2905), (0.0186, -0.2935), (0.0193, -0.2960),
                (0.0196, -0.2975), (0.0196, -0.3022), (0.0193, -0.3025), (0.0193, -0.3031), (0.0196, -0.3034),
                (0.0196, -0.3042), (0.0192, -0.3056), (0.0184, -0.3065), (0.0168, -0.3071), (0.0120, -0.3073)]
K05_GRIP_OUTER = 0.0164 + 0.0005         # K05's grip radius over one tape: the cap's scale reference

# marks
SERIAL_LINE = dict(cap=0.0046, y=-0.1365, track=0.04, font=FONT_SAIRA, axes=(500, 100), features=("tnum", "lnum"))
BRAND_LINE = dict(text="KINETIQ", cap=0.00155, y=-0.1431, track=0.62, font=FONT_ARCHIVO, axes=(560, 125), level=0.80)
WALL_ETCH_Y = -0.62                      # shape units (y = -62 mm)

# Command carbon is WHITE (owner, 2026-10-22, after the canon was built): white 3K twill with the weave clearly visible,
# white tows under a glassy clear coat, the twill crisp in light and in shade; not grey, not plastic, not glowing.
# mat_white() keeps K10's baked twill maps (the same tows, crevices, fibre directions and relief, on the fold UVs, so the
# weave still folds over the 1.5 mm edge) and changes the fibre: a dielectric white tow instead of graphite.
#   tint      linear albedo of a lit tow (a whisper warm, so it reads as white fibre in resin, not as cold plastic)
#   alb_k     how much of the baked albedo's tow-to-tow tone and crevice shadow is kept (0 = flat white)
#   dir_tone  the two tow directions differ by this much in tone (fibres scatter more across than along their axis):
#             with the relief this is what makes the twill read in shade, where no reflection helps
#   aniso     anisotropic sheen of the fibres under the coat (rotated per tow by rot16): the twill flips in a highlight
#   frost     the throat serial's laser mark on white is a graphite frost (a laser darkens white composite), so it
#             reads as a crisp dark satin mark; on black carbon it stays K10's pale frost
COMMAND_WHITE = dict(tint=(0.70, 0.69, 0.665), alb_k=0.65, dir_tone=0.14, streak=1.0, streak_a=0.12, streak_r=0.6,
                     streak_h=0.25, streak_w=0.00012, streak_len=0.02, rough_s=0.60, metal=0.0, spec=0.5, ior=1.55,
                     aniso=0.75, bump=0.30, print=0.004, coat_rough=0.03,
                     frost=0.075, grain_alb=0.35, frost_rough=0.6, frost_mix=0.92, etch_coat_rough=0.30,
                     wall_occ=0.60, wall_dark=0.03, bore_occ=0.82, bore_dark=0.012, bore_col=0.025, wall_frost=0.06)
# the previous canon Command (K10's black twill): mat_opts={"white": 0}
COMMAND = dict(coat_rough=0.032)
COMMAND_WALL = dict(coat_rough=0.032)
COMMAND_BORE = dict(coat_rough=0.032, wall_occ=0.0)
# Pace carbon, v5 "fibre" 12K (site review rounds 1 and 3, 2026-10-23). The v4 tapes read as a flat two-tone grey/black
# checkerboard with crisp square edges at phone and card size (an image editor's transparency grid), because the tile
# showed through ALBEDO: a +-11 % tone per tape, +-12 % albedo streaks, a 30 % coat-weight flip on alternate tapes and a
# dark seam bump round every tape. Real 12K spread tow is near-uniform black under a uniform clear coat; the tapes show
# only through the direction of their fibres' sheen. Now:
#   tone       per-tape albedo spread, total (0.04 = +-2 %); streak_alb: fibre-bundle albedo streaks (+-1.5 %)
#   flip       0: the coat is one uniform glass-clear layer (the coat flip was a 30 % reflectance step per tile)
#   fibre      1 = each tape gets a fine fibre normal under the coat: bundle striations fib_w across (m), fib_len along,
#              fib_h micrometres deep, so a lit tape breaks into silky streaks along its fibres instead of a flat tile
#   rstreak    roughness streaks along the fibres (+- fraction of rough, rs_w across): the sheen is never uniform
#   crimp      micrometres of arch along each tape between the crossings (plain weave): the sheen grades along the tape
#   seam       the dip where two tapes butt (v4: 0.25 of a 40 um bump, a dark line round every tile); 0 under the coat
#   aniso      the fibre sheen's anisotropy: the checker is the difference between the two fibre directions
# mat_opts=PACE_V4 restores the previous canon Pace exactly (K08 / K11-pace stage 3a: rough 0.5, aniso 0.9, no organic,
# flip 0.30, no fibre layer).
#   crimp_shape 0 = v5's arch along the fibre only (full height at the tape's side edges: a 90 um step round every tile,
#              drawn by the 1 um bump as a crease); 1 = a tile envelope, crimp x sin(pi f_along) x sin(pi f_across)^crimp_p,
#              0 on all four edges, so the arch grades the sheen along each tape without outlining it (review round 6)
#   fib_blend  tape-edge crossfade of the fibre-normal noise (tile units): the two fibre orientations meet at 50/50 on
#              every edge, so the fibre bump has no step there either (0 = v5's hard switch)
#   fib_detail octaves of the fibre-normal noise (v5: 4; fewer octaves = straighter, silkier lines)
#   aniso_across 1 = the anisotropic lobe's wide axis runs across the fibres (a cylinder's highlight), in line with the
#              fibre-normal bumps; 0 = v5's (wide along the fibres)
#   crimp_shape 2 = analytic arch (round 6 default): the shading normal tilts along the fibre by the arch's slope, no
#              height field, so no crease or pillow at any tape edge; the arch alone grades each tape's sheen
#   beckmann   1 = the fibre sheen is its own anisotropic Beckmann glossy under a coat-only Principled (round 6)
# v6 (review round 6, 2026-10-23): narrow, near-mirror fibre lobes (rough 0.14, aniso 0.90, wide axis across the fibres)
# with a 30 um analytic arch: a lit tape carries its own gradient, the band's edge steps along the tapes and the tapes
# shimmer inside the wash; base 0.045 (+-2 % per tape). The shots dim their Pace band (K08 P_BAND_S 9, K11 10).
PACE = dict(tow_mm=8.0, coat_rough=0.03, base=0.045, rough=0.14, aniso=0.90, flip=0.0, organic=1.0,
            fibre=1.0, tone=0.04, streak_alb=0.03, fib_w=0.0004, fib_len=0.12, fib_h=3.0, rstreak=0.15,
            rs_w=0.0018, crimp=30.0, seam=0.0, crimp_shape=2.0, crimp_p=0.5, fib_blend=0.04, fib_detail=1.5,
            aniso_across=1.0, beckmann=1.0)
# v5 exactly as rendered in the J previews (review round 6's baseline)
PACE_V5 = dict(base=0.03, rough=0.40, aniso=0.70, rstreak=0.5, crimp=90.0, crimp_shape=0.0, fib_blend=0.0,
               fib_detail=4.0, fib_w=0.0007, fib_len=0.06, aniso_across=0.0, beckmann=0.0)
PACE_V4 = dict(rough=0.5, aniso=0.9, organic=0.0, flip=0.30, fibre=0.0)
PACE_PROBE = None   # measurement hook (shots/pace_measure.py): "albedo" turns every Pace material into an emission of
                    # (base albedo luminance x 10, fibre direction hz, coat weight) for an exact per-tape albedo read-out
# aniso: K11 used 0.9. Under a close softbox band that turned the tapes into a black-and-white chessboard (toy-like);
# 0.65 keeps the faint checker in shade and the in-band tile flip but gives the crossing tapes some sheen too.
# mat_opts={"aniso": 0.9, "organic": 0} restores K11-pace exactly.
# organic (canon addition; 0 = K11's exact material): spread tapes are never a perfect chessboard. Tape edges wander
# about 0.2 mm, each tape's fibre angle varies about +-3 deg (so lit tapes differ in brightness) and fibre bundles
# streak the sheen along each tape.
FEELS = ("command", "pace")


# ------------------------------------------------------------------ holes: the canonical 8 + 34
GRID_R, CROWN_R = 0.062, 0.070
COL, ROW, TOP_ROW = 0.245, 0.143, 0.834
CROWN_INSET, CROWN_STEP, CROWN_FIRST = 0.31, 0.32, 0.165
# the hand-off list in the audit (section 7), [x, y, r] in shape units; holes_canon() must reproduce it
HOLES_HANDOFF = [[-0.1646, 1.2304, 0.07], [0.1646, 1.2304, 0.07], [-0.4725, 1.1475, 0.07], [0.4725, 1.1475, 0.07],
                 [-0.7344, 0.9669, 0.07], [0.7344, 0.9669, 0.07], [-0.9105, 0.702, 0.07], [0.9105, 0.702, 0.07],
                 [-0.49, 0.834, 0.062], [0, 0.834, 0.062], [0.49, 0.834, 0.062], [-0.245, 0.691, 0.062],
                 [0.245, 0.691, 0.062], [-0.49, 0.548, 0.062], [0, 0.548, 0.062], [0.49, 0.548, 0.062],
                 [-0.735, 0.405, 0.062], [-0.245, 0.405, 0.062], [0.245, 0.405, 0.062], [0.735, 0.405, 0.062],
                 [-0.49, 0.262, 0.062], [0, 0.262, 0.062], [0.49, 0.262, 0.062], [-0.735, 0.119, 0.062],
                 [-0.245, 0.119, 0.062], [0.245, 0.119, 0.062], [0.735, 0.119, 0.062], [-0.49, -0.024, 0.062],
                 [0, -0.024, 0.062], [0.49, -0.024, 0.062], [-0.735, -0.167, 0.062], [-0.245, -0.167, 0.062],
                 [0.245, -0.167, 0.062], [0.735, -0.167, 0.062], [-0.49, -0.31, 0.062], [0, -0.31, 0.062],
                 [0.49, -0.31, 0.062], [-0.245, -0.453, 0.062], [0.245, -0.453, 0.062], [-0.49, -0.596, 0.062],
                 [0, -0.596, 0.062], [0.49, -0.596, 0.062]]


def _outline_units(n=2000):
    pts, p0 = [], racket.HEAD_START
    for c1, c2, p1 in racket.HEAD_CURVES:
        for k in range(n):
            t = k / n
            mt = 1 - t
            pts.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * p1[0],
                        mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * p1[1]))
        p0 = p1
    return pts


def _grid34():
    xs = {"A": (0.0, -2 * COL, 2 * COL), "B": (-COL, COL), "C": (-COL, COL, -3 * COL, 3 * COL)}
    out = []
    for i, kind in enumerate("ABACACACABA"):
        y = TOP_ROW - i * ROW
        for x in sorted(xs[kind]):
            out.append((round(x, 4), round(y, 4), GRID_R))
    return out


def _crown8():
    from shapely.geometry import LineString, Point, Polygon
    coords = list(Polygon(_outline_units()).buffer(-CROWN_INSET, join_style=1, resolution=64).exterior.coords)
    ls = LineString(coords)
    s0 = ls.project(Point(0.0, max(c[1] for c in coords)))
    out = []
    for k in range(4):
        d = CROWN_FIRST + k * CROWN_STEP
        a = ls.interpolate((s0 + d) % ls.length)
        b = ls.interpolate((s0 - d) % ls.length)
        p = a if a.x > 0 else b
        out += [(round(p.x, 4), round(p.y, 4), CROWN_R), (round(-p.x, 4), round(p.y, 4), CROWN_R)]
    return sorted(out, key=lambda h: (-h[1], h[0]))


_HOLES = None


def holes_canon():
    """[(x, y, r)] in shape units (x 0.1 = metres): the crown of 8 first (r 0.070), then the 34 (r 0.062), top down."""
    global _HOLES
    if _HOLES is None:
        hs = _crown8() + _grid34()
        assert len(hs) == 42 and all(abs(a - b) < 2e-4 for h, g in zip(hs, HOLES_HANDOFF) for a, b in zip(h, g)), \
            "holes_canon() drifted from the audit's hand-off list"
        _HOLES = hs
    return list(_HOLES)


# ------------------------------------------------------------------ plan loops
def _smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def outline_canon(r_fillet=0.003, step=0.0005, neck=NECK):
    """The head outline (racket.py curves, 3 mm plan fillets) united with the canonical neck: 47 -> 33 mm, an 18 mm
    concave fillet into the V, straight on under the grip, closed by a round end at y_cut (hidden in the grip)."""
    from shapely.geometry import Polygon
    base = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, 600)
    n = neck
    right = []
    for k in range(41):
        y = n["y_top"] + (n["y_end"] - n["y_top"]) * k / 40
        t = (n["y_top"] - y) / (n["y_top"] - n["y_end"])
        right.append((n["hw_top"] + (n["hw_end"] - n["hw_top"]) * _smooth(t), y))
    r_end = n["hw_end"]
    yc = n["y_cut"] + r_end
    right.append((r_end, yc))
    arc = [(r_end * math.cos(-math.pi * k / 48), yc + r_end * math.sin(-math.pi * k / 48)) for k in range(1, 48)]
    poly = right + arc + [(-x, y) for (x, y) in reversed(right)]
    q = Polygon(base).union(Polygon(poly))
    rc = n["r_concave"]
    q = q.buffer(rc, join_style=1, resolution=96).buffer(-rc, join_style=1, resolution=96)
    q = q.buffer(-r_fillet, join_style=1, resolution=96).buffer(r_fillet, join_style=1, resolution=96)
    return L._resample(list(q.exterior.coords)[:-1], step)


def edge_radius(y, r_frame=0.0015, ramp=NECK_ROUND):
    y0, y1, r1 = ramp
    if y >= y0:
        return r_frame
    return r_frame + (r1 - r_frame) * _smooth((y0 - y) / (y0 - y1))


def _profile(R, S):
    """Rounded-edge profile from the front cap edge (theta 90) down the wall and back to the rear cap edge:
    [(inset, z, cos, sin)] and the arc length at every point."""
    top = []
    for k in range(S + 1):
        th = math.pi / 2 * (1 - k / S)
        top.append((R * (1 - math.cos(th)), (T2 - R) + R * math.sin(th), math.cos(th), math.sin(th)))
    prof = top + [(i_, -z, c, -s_) for (i_, z, c, s_) in reversed(top)]
    pv = [0.0]
    for a, b in zip(prof[:-1], prof[1:]):
        pv.append(pv[-1] + math.hypot(a[0] - b[0], a[1] - b[1]))
    return prof, pv


# ------------------------------------------------------------------ head
T_FACE, T_BACK, T_RIM, T_WALL, T_NECK, T_HOLES, T_BRIDGE, T_THROAT, T_NECKCAP = 0, 1, 2, 3, 4, 5, 7, 8, 9
CAP_TAGS = (T_FACE, T_BACK, T_NECKCAP)


def build_head(name="KQ", holes=None, r_frame=0.0015, r_hole=0.0008, seg_frame=14, seg_hole=6, throat_fillet=0.0035,
               outline_fillet=0.003, hole_seg=72, neck=NECK, taper=NECK_TAPER, round_=NECK_ROUND,
               throat_wall="clamp", throat_segs=None, split_y=NECK_SPLIT_Y, neck_uv=NECK_UV):
    """k10_lib.build_head_k10 with the canonical holes (a radius per hole), the canonical neck (its edge radius grows
    along it) and the light-linking split. Returns {part: object}."""
    outline = outline_canon(outline_fillet, neck=neck)
    throat = L.throat_loop(throat_fillet)
    hl = holes if holes is not None else holes_canon()
    hole_loops = []
    for (hx, hy, hr) in hl:
        hole_loops.append([(hx * U + hr * U * math.cos(2 * math.pi * k / hole_seg),
                            hy * U + hr * U * math.sin(2 * math.pi * k / hole_seg)) for k in range(hole_seg)])
    if racket._area(outline) < 0:
        outline.reverse()
    loops = [(outline, "outline")]
    for i, lp in enumerate([throat] + hole_loops):
        if racket._area(lp) > 0:
            lp = lp[::-1]
        loops.append((lp, "throat" if i == 0 else "hole"))
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    nl = bm.verts.layers.float_vector.new("kq_n")
    ul = bm.verts.layers.float_vector.new("kq_uv")  # fold UV per vertex (survives the bmesh ops below)
    cap_top, cap_bot = {}, {}
    face_tag = {}
    S_f, S_h = seg_frame, seg_hole
    prof_frame = _profile(r_frame, S_f)
    prof_hole = _profile(r_hole, S_h)
    neck_rng = None
    for li, (lp, kind) in enumerate(loops):
        outw = L._normals(lp, span=2)
        n = len(lp)
        S = S_h if kind == "hole" else S_f
        if kind == "outline":
            Rs = [edge_radius(y, r_frame, round_) for (_, y) in lp]
            profs = [_profile(R, S) for R in Rs]
            below = [y < split_y for (_, y) in lp]
            # the neck run (cyclic) and its two boundary vertices, which both cap polygons share
            i0 = next(i for i in range(n) if below[i] and not below[i - 1])
            i1 = i0
            while below[(i1 + 1) % n]:
                i1 = (i1 + 1) % n
            neck_rng = ((i0 - 1) % n, (i1 + 1) % n)  # first and last vertex of the neck polygon
        else:
            Rs = [r_hole if kind == "hole" else r_frame] * n
            profs = [prof_hole if kind == "hole" else prof_frame] * n
        if kind == "throat":
            s_thr, _ = L.throat_arclength(lp)
            segb = [b_ * 0.001 for b_ in throat_segs] if throat_segs else None
        nr = 2 * (S + 1)
        rings = [[None] * n for _ in range(nr)]
        for i, ((x, y), (ox, oy)) in enumerate(zip(lp, outw)):
            prof, pv = profs[i]
            R = Rs[i]
            p_b = pv[S]
            p0x, p0y = x - ox * R, y - oy * R  # ring-0 point on the face
            fx, fy = ox, oy  # fold direction of the UVs over the edge (the outline normal; see NECK_UV for the neck)
            if kind == "outline" and neck_uv:
                wn = _smooth((neck_uv[0] - y) / (neck_uv[0] - neck_uv[1]))
                if wn > 0.0:
                    fx, fy = (1 - wn) * ox + wn * math.copysign(1.0, x), (1 - wn) * oy
                    ln_ = math.hypot(fx, fy)
                    fx, fy = fx / ln_, fy / ln_
            for k, (inset, z, c, s_) in enumerate(prof):
                v = bm.verts.new((x - ox * inset, y - oy * inset, z))
                v[nl] = (ox * c, oy * c, s_)
                if kind == "hole" or (kind == "throat" and throat_wall == "clamp"):
                    d = min(pv[k], p_b)
                    v[ul] = (p0x + ox * d, p0y + oy * d, 0.0)
                elif kind == "throat" and k > S:
                    v[ul] = (p0x + ox * p_b, p0y + oy * p_b - (pv[k] - p_b), 0.0)
                else:
                    v[ul] = (p0x + fx * pv[k], p0y + fy * pv[k], 0.0)
                rings[k][i] = v
        cap_top[li] = rings[0]
        cap_bot[li] = rings[-1]
        if kind == "outline":
            a_, b_ = neck_rng
            in_neck = set()
            k = a_
            while k != b_:
                in_neck.add(k)
                k = (k + 1) % n
        for ri in range(nr - 1):
            ra, rb = rings[ri], rings[ri + 1]
            for k in range(n):
                j = (k + 1) % n
                f = bm.faces.new((ra[k], ra[j], rb[j], rb[k]))
                if kind == "outline":
                    face_tag[f] = T_NECK if k in in_neck else (T_WALL if ri == S else T_RIM)
                elif kind == "throat":
                    ox, oy = outw[k]
                    if oy < -0.55 and ri >= S:
                        face_tag[f] = T_BRIDGE
                    elif segb:
                        sk = s_thr[k]
                        face_tag[f] = 100 + max(i_ for i_, b0 in enumerate(segb) if sk >= b0)
                    else:
                        face_tag[f] = T_THROAT
                else:
                    face_tag[f] = T_HOLES
    # caps: two polygons that share the segment across the neck at split_y, so the face / neck boundary is exact
    a_, b_ = neck_rng
    n_o = len(loops[0][0])

    def run(i, j):
        out, k = [i], i
        while k != j:
            k = (k + 1) % n_o
            out.append(k)
        return out

    upper_idx, lower_idx = run(b_, a_), run(a_, b_)
    for caps, tag_up in ((cap_top, T_FACE), (cap_bot, T_BACK)):
        ring_o = caps[0]
        polys_up = [[ring_o[i] for i in upper_idx]] + [caps[li] for li in range(1, len(loops))]
        polys_lo = [[ring_o[i] for i in lower_idx]]
        for polys, tag in ((polys_up, tag_up), (polys_lo, T_NECKCAP)):
            tris = tessellate_polygon([[Vector((v.co.x, v.co.y, 0)) for v in ring] for ring in polys])
            flat = [v for ring in polys for v in ring]
            for (a, b, c) in tris:
                try:
                    f = bm.faces.new((flat[a], flat[b], flat[c]))
                except ValueError:
                    continue
                face_tag[f] = tag
    for f in bm.faces:
        f.material_index = face_tag.get(f, T_FACE)
    is_cap = lambda f: f.material_index in CAP_TAGS
    if taper:
        y0 = taper[0]
        for _ in range(10):
            long_ = [e for e in bm.edges if min(v.co.y for v in e.verts) < y0 + 0.002 and e.calc_length() > 0.0025
                     and all(is_cap(f) for f in e.link_faces)]
            if not long_:
                break
            bmesh.ops.subdivide_edges(bm, edges=long_, cuts=1, use_grid_fill=False)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        for v in bm.verts:
            if abs(abs(v.co.z) - T2) < 1e-7 and all(is_cap(f) for f in v.link_faces):
                v[nl] = (0.0, 0.0, 1.0 if v.co.z > 0 else -1.0)
        for v in bm.verts:
            s, ds = L.neck_scale(v.co.y, taper)
            if s == 1.0 and ds == 0.0:
                continue
            nx, ny, nz = v[nl]
            z0 = v.co.z
            v.co.z = z0 * s
            v[nl] = tuple(Vector((nx, ny - ds * z0 * nz / s, nz / s)).normalized())
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        flat_cap = f.material_index in CAP_TAGS
        for lp_ in f.loops:
            lp_[uvl].uv = (lp_.vert.co.x, lp_.vert.co.y) if flat_cap else tuple(lp_.vert[ul])[:2]
    groups = {"face": {T_FACE}, "back": {T_BACK}, "rim": {T_RIM}, "wall": {T_WALL}, "neck": {T_NECK, T_NECKCAP},
              "holes": {T_HOLES}, "bridgewall": {T_BRIDGE}, "throat": {T_THROAT}}
    if throat_segs:
        for i_ in range(len(throat_segs)):
            groups["thr%02d" % i_] = {100 + i_}
    present = set(f.material_index for f in bm.faces)
    objs = {}
    for key, keep in groups.items():
        if not (keep & present):
            continue
        b2 = bm.copy()
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index not in keep], context="FACES")
        for f in b2.faces:
            f.material_index = 0
        me = bpy.data.meshes.new(name + "_" + key)
        b2.to_mesh(me)
        b2.free()
        me.shade_smooth()
        nrm = [tuple(a_.vector) for a_ in me.attributes["kq_n"].data]
        me.normals_split_custom_set_from_vertices(nrm)
        me.attributes.remove(me.attributes["kq_n"])
        me.attributes.remove(me.attributes["kq_uv"])
        ob = bpy.data.objects.new(name + "_" + key, me)
        bpy.context.scene.collection.objects.link(ob)
        ob["kq_part"] = key
        objs[key] = ob
    bm.free()
    return objs


# ------------------------------------------------------------------ handle section, grip, cap
def section(n=288, grow=0.0):
    """The handle core section (where the neck arrives): a 33.0 x 29.0 mm rounded rectangle with the neck's 12 mm
    edge radius (squashed in z by the taper), offset outward by `grow`. Returns (P, N): n points (x, z) uniform in
    arc length from the back centre (0, -b) toward +x, then the front (+z), and their outward normals."""
    a, s1, R = NECK["hw_end"], NECK_TAPER[2], NECK_ROUND[2]
    b, rx, rz = T2 * s1, R, R * s1
    pts = []
    m = 400
    pts += [(x, -b) for x in np.linspace(0.0, a - rx, m, endpoint=False)]
    pts += [(a - rx + rx * math.cos(t), -b + rz + rz * math.sin(t)) for t in np.linspace(-math.pi / 2, 0, m, endpoint=False)]
    pts += [(a, z) for z in np.linspace(-b + rz, b - rz, m, endpoint=False)]
    pts += [(a - rx + rx * math.cos(t), b - rz + rz * math.sin(t)) for t in np.linspace(0, math.pi / 2, m, endpoint=False)]
    pts += [(x, b) for x in np.linspace(a - rx, -(a - rx), m, endpoint=False)]
    pts += [(-(a - rx) + rx * math.cos(t), b - rz + rz * math.sin(t)) for t in np.linspace(math.pi / 2, math.pi, m, endpoint=False)]
    pts += [(-a, z) for z in np.linspace(b - rz, -b + rz, m, endpoint=False)]
    pts += [(-(a - rx) + rx * math.cos(t), -b + rz + rz * math.sin(t)) for t in np.linspace(math.pi, 1.5 * math.pi, m, endpoint=False)]
    pts += [(x, -b) for x in np.linspace(-(a - rx), 0.0, m, endpoint=False)]
    Pd = np.array(pts)
    seg = np.hypot(*np.diff(np.vstack([Pd, Pd[:1]]), axis=0).T)
    s = np.r_[0, np.cumsum(seg)]
    t = np.linspace(0, s[-1], n, endpoint=False)
    Pc = np.vstack([Pd, Pd[:1]])
    P = np.stack([np.interp(t, s, Pc[:, 0]), np.interp(t, s, Pc[:, 1])], 1)
    Tn = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    Tn /= np.linalg.norm(Tn, axis=1)[:, None]
    N = np.stack([Tn[:, 1], -Tn[:, 0]], 1)  # right normal of a CCW loop in (x, z): outward
    return P + N * grow, N


def _lathe_uv(name, ring_fn, ys, n, cap_end=False, uv=True):
    """Tube through the rings ring_fn(j, y) -> (n, 2) (x, z) at heights ys; UV u = around (0..1, seam at the back
    centre), v = y (metres). cap_end closes the last ring with a centre fan."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    rings = []
    for j, y in enumerate(ys):
        XZ = ring_fn(j, y)
        rings.append([bm.verts.new((float(x), float(y), float(z))) for (x, z) in XZ])
    for j in range(len(ys) - 1):
        for k in range(n):
            k2 = (k + 1) % n
            f = bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
            u0, u1 = k / n, (k + 1) / n
            for lp, (u, v) in zip(f.loops, ((u0, ys[j]), (u1, ys[j]), (u1, ys[j + 1]), (u0, ys[j + 1]))):
                lp[uvl].uv = (u, v)
    if cap_end:
        c = bm.verts.new((0.0, float(ys[-1]), 0.0))
        for k in range(n):
            f = bm.faces.new((rings[-1][k], rings[-1][(k + 1) % n], c))
            for lp in f.loops:
                lp[uvl].uv = (k / n, ys[-1])
    # winding is outward by construction (an open tube would confuse recalc_face_normals)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _ss(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def build_grip(name, n=288, dy=0.00022):
    """K05's overgrip on the canonical section: 0.5 mm tape, a real helical wrap (27 mm pitch) with an overlap step
    at each seam, an 11 mm finishing band at the top; the tape thins into the cap at the bottom."""
    y0, y1 = GRIP_Y
    P, N = section(n)
    tt = np.arange(n) / n
    n_al = int(round(abs(y1 - y0) / dy))
    ys = [y0 + (y1 - y0) * j / n_al for j in range(n_al + 1)]

    def ring(j, y):
        d_top, d_bot = y0 - y, y - y1
        ph = ((y0 - y) / GRIP_PITCH + tt) % 1.0
        over = np.array([_ss(0.0, 0.012, p) * (1 - _ss(0.30, 0.37, p)) for p in ph])
        th = TAPE * (1 + over) * _ss(0.0, 0.0025, d_top) * _ss(0.0, 0.0025, d_bot)
        if d_top < GRIP_BAND:  # finishing band: flat, double tape; its cut edge stands 0.3 mm proud
            band = 2 * TAPE * (0.3 + 0.7 * _ss(0.0, 0.0015, d_top)) * (1 - _ss(GRIP_BAND - 0.0015, GRIP_BAND, d_top))
            th = np.maximum(th, band)
        return P + N * th[:, None]

    ob = _lathe_uv(name, ring, ys, n)
    return ob


def _smooth_prof(prof, n):
    """Catmull-Rom resample of a (r, y) profile: n points per segment (K05)."""
    out = []
    P = [Vector(p) for p in prof]
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]
        p1, p2 = P[i], P[i + 1]
        p3 = P[min(i + 2, len(P) - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((q.x, q.y))
    out.append(tuple(P[-1]))
    return out


def cap_profile():
    """[(scale, y)]: K05's cap moved up 7.3 mm (y -0.2817 .. -0.3000) and scaled 0.94, as a scale of the grip's
    one-tape section, so the cap stands about 1.5 mm proud of the grip and follows its shape."""
    return [(r * CAP_SCALE / K05_GRIP_OUTER, y + CAP_SHIFT) for (r, y) in _smooth_prof(CAP_PROF_K05, 3)]


def build_cap(name, n=192):
    G, _ = section(n, grow=TAPE)
    prof = cap_profile()
    ys = [y for (_, y) in prof]
    cap = _lathe_uv(name, lambda j, y: G * prof[j][0], ys, n, cap_end=True)
    return cap


# THE company mark (owner, 2026-10-22: the logo is the Q). One drawing everywhere: the site icon
# (kinetiq src/app/icon.svg, commit 7d00d87, viewBox 64): a geometric ring, ellipse centre (31, 30), rx 16 / ry 15,
# stroke 6, and a diagonal tail stroke 6 (butt ends) from (36, 35) inside the counter across the bowl at 4-5 o'clock
# to (49.5, 47.5). On the cap it is engraved at the old K's cap height (the ring 2.9 mm tall): a satin graphite floor
# and a bright-cut chamfer round every edge, so it reads as an engraving on satin black, not as a white ring or a rivet.
Q_ICON = dict(cx=31.0, cy=30.0, rx=16.0, ry=15.0, stroke=6.0, tail=((36.0, 35.0), (49.5, 47.5)))
Q_MARK = dict(height=0.0029, chamfer=0.00011, tilt=45.0)   # ring outer height (m), chamfer width (m), chamfer slope (deg)


def q_outline(height=None, q=Q_ICON):
    """The Q as a shapely geometry in metres: x right, y up, the ring's centre at the origin."""
    from shapely.geometry import LineString, Point
    from shapely import affinity
    h = float(height or Q_MARK["height"])
    sw = q["stroke"]
    s = h / (2 * q["ry"] + sw)
    outer = affinity.scale(Point(0, 0).buffer(1.0, resolution=96), q["rx"] + sw / 2, q["ry"] + sw / 2)
    inner = affinity.scale(Point(0, 0).buffer(1.0, resolution=96), q["rx"] - sw / 2, q["ry"] - sw / 2)
    (ax, ay), (bx, by) = q["tail"]
    tail = LineString([(ax - q["cx"], -(ay - q["cy"])), (bx - q["cx"], -(by - q["cy"]))]).buffer(sw / 2, cap_style=2)
    g = outer.difference(inner).union(tail)
    return affinity.scale(g, s, s, origin=(0, 0))


def _poly_tris(geom):
    """Triangles [(a, b, c)] of 2D points for a (multi)polygon with holes."""
    out = []
    geoms = getattr(geom, "geoms", [geom])
    for g in geoms:
        if g.is_empty or g.area <= 0:
            continue
        loops = [list(g.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in g.interiors]
        flat = [pt for lp in loops for pt in lp]
        for (a, b, c) in tessellate_polygon([[Vector((x, y, 0)) for (x, y) in lp] for lp in loops]):
            out.append((flat[a], flat[b], flat[c]))
    return out


def build_cap_mark(name, cap, text="Q", size=0.0042, font=None, az=0.0, height=None):
    """The engraved company mark on the cap's front band, upright when the racket stands handle-down, its ring centred
    where the K sat (y = -0.2925). text="Q" builds the icon.svg Q (Q_ICON) as an engraving: material 0 = the satin
    graphite floor, material 1 = the bright-cut chamfer round every edge (its normals slope into the cut). Any other
    text keeps the old font glyph (size, font). az (deg): turn the mark round the handle axis toward +x (model right),
    so a shot can face it to its camera. Returns the object (shrink-wrapped onto `cap`)."""
    prof = cap_profile()
    y_k = -0.2998 + CAP_SHIFT
    s_k = float(np.interp(-y_k, [-y for (_, y) in prof], [s for (s, _) in prof]))
    G, _ = section(64, grow=TAPE)
    z = float(G[:, 1].max()) * s_k + 0.0003
    if text != "Q":
        mk = racket.build_text(text, size, (0.0, y_k, z), font or racket.FONT_BOLD, name, extrude=0.0)
        me = bpy.data.meshes.new_from_object(mk.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(mk)
        mk = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(mk)
        mk.location = (0.0, y_k, z)
    else:
        g = q_outline(height)
        e = float(Q_MARK["chamfer"])
        floor_ = g.buffer(-e, join_style=1, resolution=24)
        band = g.difference(floor_)
        bm = bmesh.new()
        tilt = math.tan(math.radians(float(Q_MARK["tilt"])))
        nrm_l = bm.verts.layers.float_vector.new("kq_n")
        bnd = floor_.boundary
        for mi, part in ((0, floor_), (1, band)):
            for tri in _poly_tris(part):
                vs = []
                for (x, y) in tri:
                    v = bm.verts.new((x, y, 0.0))
                    if mi == 1:  # the chamfer slopes down into the cut: its normal leans toward the floor's edge
                        from shapely.geometry import Point
                        pp = bnd.interpolate(bnd.project(Point(x, y)))
                        dx, dy = pp.x - x, pp.y - y
                        ln_ = math.hypot(dx, dy)
                        if ln_ < 1e-9:
                            dx, dy = 0.0, 0.0
                        else:
                            dx, dy = dx / ln_ * tilt, dy / ln_ * tilt
                        v[nrm_l] = tuple(Vector((dx, dy, 1.0)).normalized())
                    else:
                        v[nrm_l] = (0.0, 0.0, 1.0)
                    vs.append(v)
                f = bm.faces.new(vs)
                f.material_index = mi
                f.normal_update()
                if f.normal.z < 0:
                    f.normal_flip()
        # fine enough to follow the cap's curvature under the shrinkwrap
        for _ in range(6):
            long_ = [ed for ed in bm.edges if ed.calc_length() > 0.00025]
            if not long_:
                break
            bmesh.ops.subdivide_edges(bm, edges=long_, cuts=1, use_grid_fill=False)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        mk = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(mk)
        mk.matrix_world = Matrix.Translation((0.0, y_k, z))
    if az:
        mk.matrix_world = Matrix.Rotation(math.radians(az), 4, "Y") @ mk.matrix_world
    sw = mk.modifiers.new("wrap", "SHRINKWRAP")
    sw.target = cap
    sw.wrap_method = "NEAREST_SURFACEPOINT"
    sw.offset = 0.00002
    racket._apply_all(mk)
    me = mk.data
    if "kq_n" in me.attributes:
        # each stored normal (mark plane: +z out) is turned onto the cap's own surface normal under that vertex
        Rz = Matrix.Rotation(math.radians(az), 3, "Y")
        Ri = mk.matrix_world.to_3x3().normalized().inverted()
        ci = cap.matrix_world.inverted()
        n0 = Rz @ Vector((0.0, 0.0, 1.0))
        nrm = []
        for v, a_ in zip(me.vertices, me.attributes["kq_n"].data):
            ok, _, ns, _ = cap.closest_point_on_mesh(ci @ (mk.matrix_world @ v.co))
            q = n0.rotation_difference((cap.matrix_world.to_3x3() @ ns).normalized()) if ok else None
            nw = Rz @ Vector(a_.vector)
            if q is not None:
                nw = q @ nw
            nrm.append(tuple((Ri @ nw).normalized()))
        me.shade_smooth()
        me.normals_split_custom_set_from_vertices(nrm)
        me.attributes.remove(me.attributes["kq_n"])
    return mk


# ------------------------------------------------------------------ marks: the laser-frost etch mask
def etch_mask(path, lines, px_per_m=100000, pad=0.0015, bevel=0.00003):
    """k10_lib.etch_mask with a font, axes and OpenType features per line (the serial is Saira 500 with tabular
    figures, like the measurement card; the sub-line is K10's Archivo). lines: dicts with text, cap (cap height, m),
    y (centre of the cap-height box, m), track (em), font, axes (wght, wdth), features, level.
    Writes path, _soft and _level; returns (path, x0, y0, W, H) for k10_lib.mat_carbon_k10(etch=...)."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    rend = []
    for ln in lines:
        feats = list(ln.get("features", ())) or None
        f0 = ImageFont.truetype(ln["font"], 400)
        f0.set_variation_by_axes(list(ln["axes"]))
        hb = f0.getbbox("H")
        cap_ratio = (hb[3] - hb[1]) / 400.0
        size = int(round(ln["cap"] / cap_ratio * px_per_m))
        f = ImageFont.truetype(ln["font"], size)
        f.set_variation_by_axes(list(ln["axes"]))
        widths = [f.getlength(ch, features=feats) for ch in ln["text"]]
        tw = sum(widths) + ln["track"] * size * (len(ln["text"]) - 1)
        rend.append((ln, f, size, widths, tw, feats))
    W = max(r[4] for r in rend) / px_per_m + 2 * pad
    ytop = max(r[0]["y"] + r[0]["cap"] / 2 for r in rend) + pad
    ybot = min(r[0]["y"] - r[0]["cap"] / 2 for r in rend) - pad
    H = ytop - ybot
    Wp, Hp = int(round(W * px_per_m)), int(round(H * px_per_m))
    im = Image.new("L", (Wp, Hp), 0)
    lv = Image.new("L", (Wp, Hp), 0)
    for img, use_level in ((im, False), (lv, True)):
        dr = ImageDraw.Draw(img)
        for (ln, f, size, widths, tw, feats) in rend:
            x = (Wp - tw) / 2
            hb = f.getbbox("H")
            row_top = (ytop - (ln["y"] + ln["cap"] / 2)) * px_per_m
            fill = int(round(255 * ln.get("level", 1.0))) if use_level else 255
            for ch, wch in zip(ln["text"], widths):
                dr.text((x, row_top - hb[1]), ch, font=f, fill=fill, features=feats)
                x += wch + ln["track"] * size
    im.save(path)
    im.filter(ImageFilter.GaussianBlur(px_per_m * bevel)).save(path.replace(".png", "_soft.png"))
    d = max(3, int(round(px_per_m * bevel * 2.5)) | 1)
    lv.filter(ImageFilter.MaxFilter(d)).filter(ImageFilter.GaussianBlur(2)).save(path.replace(".png", "_level.png"))
    return path, -W / 2, ybot, W, H


def serial_lines(serial):
    return [dict(SERIAL_LINE, text=serial), dict(BRAND_LINE)]


def serial_etch(serial):
    """The throat-bridge mark for one racket: its serial over a KINETIQ sub-line (cached per serial)."""
    os.makedirs(ASSETS, exist_ok=True)
    path = os.path.join(ASSETS, "etch_%s.png" % serial.replace("/", "_"))
    return etch_mask(path, serial_lines(serial))


def serial_box(serial):
    """(x0, x1, y0, y1) of the serial's ink on the face (metres), for framing and rake lights."""
    path, x0, y0, W, H = serial_etch(serial)
    from PIL import Image
    a = np.asarray(Image.open(path)) > 127
    rows, cols = np.where(a)
    Hp, Wp = a.shape
    return (x0 + cols.min() / Wp * W, x0 + (cols.max() + 1) / Wp * W, y0 + (Hp - rows.max() - 1) / Hp * H, y0 + (Hp - rows.min()) / Hp * H)


# ------------------------------------------------------------------ materials
def _out_surface(m):
    out = next(n_ for n_ in m.node_tree.nodes if n_.type == "OUTPUT_MATERIAL")
    return out, out.inputs["Surface"].links[0].from_socket


def _bore_wrap(m, z_lip=0.0012, z_dark=0.0075, occ=0.95, col=0.006):
    """The bores are lined by the carbon shell (sealed core): below the 0.8 mm lip the lining darkens with depth
    (|z| from the faces), so each hole reads as a through-hole with one gloss crescent on its lip."""
    nb = K.NB(m)
    out, surf = _out_surface(m)
    _, _, z = nb.coords("Object")
    az = nb.math("ABSOLUTE", z)
    o_ = nb.math("MULTIPLY", nb.smooth(az, T2 - z_lip, T2 - z_dark), occ)
    blk = nb.n.new("ShaderNodeBsdfPrincipled")
    blk.inputs["Base Color"].default_value = (col, col, col * 1.08, 1)
    blk.inputs["Roughness"].default_value = 0.6
    blk.inputs["Specular IOR Level"].default_value = 0.2
    mx = nb.n.new("ShaderNodeMixShader")
    nb.l.new(o_, mx.inputs[0])
    nb.l.new(surf, mx.inputs[1])
    nb.l.new(blk.outputs[0], mx.inputs[2])
    nb.l.new(mx.outputs[0], out.inputs["Surface"])
    return m


def _etch_layer(m, b, etch, o, coat_r):
    """k10_lib's laser-frost mark (12 um cut, frosted floor that scatters a raking light), added to any carbon whose
    face UVs are model (x, y): used for Pace (Command uses mat_carbon_k10's own, identical code)."""
    nb = K.NB(m)
    out, surf = _out_surface(m)
    path, x0, y0, W, H = etch
    u, v, _ = nb.coords("UV")
    cv = nb.n.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", u, x0), W), cv.inputs[0])
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", v, y0), H), cv.inputs[1])
    mkb = L._img(nb, cv.outputs[0], path.replace(".png", "_soft.png"), "Non-Color", interp="Cubic", ext="CLIP")
    mkl = L._img(nb, cv.outputs[0], path.replace(".png", "_level.png"), "Non-Color", interp="Cubic", ext="CLIP")
    _, _, nz = nb.coords("Normal")
    onface = nb.smooth(nz, 0.95, 0.99)
    soft = mkb.outputs["Color"]
    mask = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(soft, float(o.get("frost_lo", 0.03)), float(o.get("frost_hi", 0.22))),
                                       mkl.outputs["Color"]), onface)
    relief = nb.math("MULTIPLY", soft, onface)
    depth = float(o.get("etch_depth", 0.0001))
    for sock_name in ("Normal", "Coat Normal"):
        sock = b.inputs[sock_name]
        prev = sock.links[0].from_socket if sock.links else None
        eb = nb.n.new("ShaderNodeBump")
        eb.inputs["Strength"].default_value = 1.0
        eb.inputs["Distance"].default_value = depth
        nb.l.new(nb.math("MULTIPLY", relief, -1.0), eb.inputs["Height"])
        if prev is not None:
            nb.l.new(prev, eb.inputs["Normal"])
        nb.l.new(eb.outputs["Normal"], sock)
        if sock_name == "Coat Normal":
            cnrm = eb.outputs["Normal"]
    nb.l.new(nb.math("MULTIPLY_ADD", mask, float(o.get("etch_coat_rough", 0.42)) - coat_r, coat_r), b.inputs["Coat Roughness"])
    gs = 1.0 / float(o.get("grain", 0.0001))
    gv = nb.n.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("MULTIPLY", u, gs), gv.inputs[0])
    nb.l.new(nb.math("MULTIPLY", v, gs), gv.inputs[1])
    nz_ = nb.n.new("ShaderNodeTexNoise")
    nz_.noise_dimensions = "3D"
    nz_.inputs["Scale"].default_value = 1.0
    nz_.inputs["Detail"].default_value = 2.0
    nz_.inputs["Roughness"].default_value = 0.6
    nb.l.new(gv.outputs[0], nz_.inputs["Vector"])
    gn = nb.smooth(nz_.outputs["Fac"], 0.32, 0.68)
    fr = nb.n.new("ShaderNodeBsdfPrincipled")
    g, ga = float(o.get("frost", 0.46)), float(o.get("grain_alb", 0.5))
    nb.l.new(nb.gray(nb.math("MULTIPLY", g, nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", gn, 0.5), ga, 1.0))), fr.inputs["Base Color"])
    nb.l.new(nb.math("ADD", float(o.get("frost_rough", 0.85)), nb.math("MULTIPLY", nb.math("SUBTRACT", gn, 0.5),
                                                                     float(o.get("grain_rough", 0.5))), clamp=True), fr.inputs["Roughness"])
    fr.inputs["Metallic"].default_value = 0.0
    fr.inputs["Specular IOR Level"].default_value = 0.5
    gb = nb.n.new("ShaderNodeBump")
    gb.inputs["Strength"].default_value = float(o.get("grain_bump", 0.8))
    gb.inputs["Distance"].default_value = float(o.get("grain_depth", 0.000004))
    nb.l.new(gn, gb.inputs["Height"])
    nb.l.new(cnrm, gb.inputs["Normal"])
    nb.l.new(gb.outputs["Normal"], fr.inputs["Normal"])
    mx = nb.n.new("ShaderNodeMixShader")
    nb.l.new(nb.math("MULTIPLY", mask, float(o.get("frost_mix", 0.88))), mx.inputs[0])
    nb.l.new(surf, mx.inputs[1])
    nb.l.new(fr.outputs[0], mx.inputs[2])
    nb.l.new(mx.outputs[0], out.inputs["Surface"])
    return m


def mat_pace(name, etch=None, wall=False, o=None):
    """12K spread tow, plain weave, 8 mm flat tapes that butt together (no grout), glass-clear coat 0.03, on the fold UVs
    (u, v = model x, y on the faces, folding over every edge), with a UV-aligned tangent. v5 (fibre=1, the default,
    2026-10-23): albedo within a few percent from tape to tape, one uniform coat, and per tape a fine fibre normal,
    roughness streaks along the fibres and a slight crimp, so the tapes read only through the direction of their sheen.
    fibre=0 (PACE_V4) builds the previous k789_lib.mat_carbon_aniso("12k") port with K11's 30 % coat flip exactly."""
    p = dict(PACE, **(o or {}))
    fib = float(p.get("fibre", 0.0)) > 0
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    x, y, _ = nb.coords("UV")
    org = float(p.get("organic", 0.0))
    if org > 0:
        tcu = nb.n.new("ShaderNodeTexCoord")
        wv = nb.n.new("ShaderNodeTexNoise")
        wv.noise_dimensions = "3D"
        wv.inputs["Scale"].default_value = 45.0      # ~22 mm wander wavelength (UV in metres)
        wv.inputs["Detail"].default_value = 1.0
        nb.l.new(tcu.outputs["UV"], wv.inputs["Vector"])
        sep = nb.n.new("ShaderNodeSeparateColor")
        nb.l.new(wv.outputs["Color"], sep.inputs["Color"])
        amp = 0.0004 * org
        x = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", sep.outputs[0], 0.5), amp, x)
        y = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", sep.outputs[1], 0.5), amp, y)
    tw = p["tow_mm"] / 1000.0
    u = nb.math("ADD", nb.math("DIVIDE", x, tw), 4000.0)
    v = nb.math("ADD", nb.math("DIVIDE", y, tw), 4000.0)
    i, j = nb.math("FLOOR", u), nb.math("FLOOR", v)
    fu, fv = nb.math("FRACT", u), nb.math("FRACT", v)
    hz = nb.math("LESS_THAN", nb.math("MODULO", nb.math("ADD", i, j), 2.0), 1.0)
    acr = nb.n.new("ShaderNodeMix")
    acr.data_type = "FLOAT"
    nb.l.new(hz, acr.inputs["Factor"])
    nb.l.new(fu, acr.inputs[2])
    nb.l.new(fv, acr.inputs[3])
    d = nb.math("ABSOLUTE", nb.math("SUBTRACT", nb.math("MULTIPLY", acr.outputs[0], 2.0), 1.0))
    crown = nb.math("SUBTRACT", 1.0, nb.math("MULTIPLY", nb.smooth(d, 0.96, 1.0), 0.25))
    tc = nb.n.new("ShaderNodeTexCoord")
    st = []
    for sx, sy in ((3.0, 900.0), (900.0, 3.0)):
        mp = nb.n.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (sx * 0.001 / tw, sy * 0.001 / tw * 2.6, 1.0)
        nb.l.new(tc.outputs["UV"], mp.inputs["Vector"])
        nz = nb.n.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = 3
        nb.l.new(mp.outputs["Vector"], nz.inputs["Vector"])
        st.append(nz.outputs["Fac"])
    sm = nb.n.new("ShaderNodeMix")
    sm.data_type = "FLOAT"
    nb.l.new(hz, sm.inputs["Factor"])
    nb.l.new(st[1], sm.inputs[2])
    nb.l.new(st[0], sm.inputs[3])
    stri = nb.math("SUBTRACT", sm.outputs[0], 0.5)
    cell = nb.n.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("MULTIPLY", hz, i), cell.inputs[0])
    nb.l.new(nb.math("MULTIPLY", nb.math("SUBTRACT", 1.0, hz), j), cell.inputs[1])
    nb.l.new(hz, cell.inputs[2])
    wn = nb.n.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    nb.l.new(cell.outputs[0], wn.inputs["Vector"])
    if fib:
        # near-uniform black: a few percent of albedo between tapes, never a tile you can see in shade
        tone = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", wn.outputs["Value"], 0.5), float(p["tone"]), 1.0)
        col = nb.math("MULTIPLY", nb.math("MULTIPLY", tone, p["base"]),
                      nb.math("MULTIPLY_ADD", stri, 2.0 * float(p["streak_alb"]), 1.0))
    else:
        tone = nb.math("MULTIPLY_ADD", wn.outputs["Value"], 0.22, 0.89)
        col = nb.math("MULTIPLY", nb.math("MULTIPLY", tone, p["base"]), nb.math("MULTIPLY_ADD", stri, 0.25, 1.0))
    cc = nb.n.new("ShaderNodeCombineColor")
    for k, f in enumerate((0.97, 1.0, 1.04)):
        nb.l.new(nb.math("MULTIPLY", col, f), cc.inputs[k])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = 1.0
    if fib:
        # fibre-direction streaks for the normal (fine bundles) and the roughness (coarser), per tape orientation:
        # stretched noises in UV metres, long along the fibres, narrow across them (continuous along each tape)
        def along_noise(across, along, detail, seed, fac=None):
            outs_ = []
            for sx, sy in ((1.0 / along, 1.0 / across), (1.0 / across, 1.0 / along)):
                mp_ = nb.n.new("ShaderNodeMapping")
                mp_.inputs["Scale"].default_value = (sx, sy, 1.0)
                mp_.inputs["Location"].default_value = (seed, 2.0 * seed, 0.0)
                nb.l.new(tc.outputs["UV"], mp_.inputs["Vector"])
                nz_ = nb.n.new("ShaderNodeTexNoise")
                nz_.inputs["Scale"].default_value = 1.0
                nz_.inputs["Detail"].default_value = detail
                nz_.inputs["Roughness"].default_value = 0.55
                nb.l.new(mp_.outputs["Vector"], nz_.inputs["Vector"])
                outs_.append(nz_.outputs["Fac"])
            mx_ = nb.n.new("ShaderNodeMix")
            mx_.data_type = "FLOAT"
            nb.l.new(hz if fac is None else fac, mx_.inputs["Factor"])
            nb.l.new(outs_[1], mx_.inputs[2])   # hz = 0: fibres along v
            nb.l.new(outs_[0], mx_.inputs[3])   # hz = 1: fibres along u
            return nb.math("SUBTRACT", mx_.outputs[0], 0.5)
        fbl = float(p.get("fib_blend", 0.0))
        bfac = None
        if fbl > 0:
            # own orientation weight 1 inside the tape, 0.5 on its edges (where the neighbour's is 0.5 too)
            dedge = nb.math("MINIMUM", nb.math("MINIMUM", fu, nb.math("SUBTRACT", 1.0, fu)),
                            nb.math("MINIMUM", fv, nb.math("SUBTRACT", 1.0, fv)))
            own = nb.math("MULTIPLY_ADD", nb.smooth(dedge, 0.0, fbl), 0.5, 0.5)
            # factor toward 'fibres along u': own for hz = 1, 1 - own for hz = 0
            bfac = nb.math("ADD", nb.math("MULTIPLY", hz, nb.math("SUBTRACT", nb.math("MULTIPLY", own, 2.0), 1.0)),
                           nb.math("SUBTRACT", 1.0, own))
        fibn = along_noise(float(p["fib_w"]), float(p["fib_len"]), float(p.get("fib_detail", 4.0)), 3.7, fac=bfac)
        rsn = along_noise(float(p["rs_w"]), float(p["fib_len"]) * 1.5, 2.0, 11.3)
        rgh = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", wn.outputs["Value"], 0.5), 0.04, p["rough"])
        rgh = nb.math("MULTIPLY", rgh, nb.math("MULTIPLY_ADD", rsn, 2.0 * float(p["rstreak"]), 1.0), clamp=True)
    else:
        rgh = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", wn.outputs["Value"], 0.5), 0.06, p["rough"])
        if org > 0:
            rgh = nb.math("MULTIPLY", rgh, nb.math("MULTIPLY_ADD", stri, 0.5 * org, 1.0))
    nb.l.new(rgh, b.inputs["Roughness"])
    b.inputs["Anisotropic"].default_value = p["aniso"]
    rotv = nb.math("MULTIPLY", nb.math("SUBTRACT", 1.0, hz), 0.25)
    if float(p.get("aniso_across", 0.0)) > 0:
        # the wide axis of the lobe ACROSS the fibres, as a cylinder's (and as the fibre-normal bumps): v5 ran it along
        # them, so the stretched lobe and the across-fibre bumps cancelled into a near-isotropic sheen (round 6, issue 5)
        rotv = nb.math("ADD", rotv, 0.25)
    if org > 0:
        wn2 = nb.n.new("ShaderNodeTexWhiteNoise")
        wn2.noise_dimensions = "3D"
        off = nb.n.new("ShaderNodeVectorMath")
        off.operation = "ADD"
        off.inputs[1].default_value = (17.3, 5.1, 2.9)  # decorrelated from the tone noise
        nb.l.new(cell.outputs[0], off.inputs[0])
        nb.l.new(off.outputs[0], wn2.inputs["Vector"])
        rotv = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", wn2.outputs["Value"], 0.5), 0.02 * org, rotv)
    nb.l.new(rotv, b.inputs["Anisotropic Rotation"])
    tg = nb.n.new("ShaderNodeTangent")
    tg.direction_type = "UV_MAP"
    tg.uv_map = "UVMap"
    nb.l.new(tg.outputs["Tangent"], b.inputs["Tangent"])
    if fib:
        # heights in micrometres (bump distance 1 um): the crimp arch along each tape between its crossings, the fibre
        # bundles across it, and (seam > 0) the butt line between tapes. Under the coat only: the coat stays glass.
        alg = nb.n.new("ShaderNodeMix")
        alg.data_type = "FLOAT"
        nb.l.new(hz, alg.inputs["Factor"])
        nb.l.new(fv, alg.inputs[2])
        nb.l.new(fu, alg.inputs[3])
        cshape = float(p.get("crimp_shape", 0.0))
        crimp_n = None
        if cshape >= 2:
            # analytic arch: the shading normal tilts along the fibre by the arch's slope (crimp x pi / tape width x
            # cos(pi f_along)), with no height field at all, so nothing is differentiated across a tape edge: the arch
            # grades the sheen along each tape and the tape edges are only where the fibre direction changes
            geo = nb.n.new("ShaderNodeNewGeometry")
            bit = nb.n.new("ShaderNodeVectorMath")
            bit.operation = "CROSS_PRODUCT"
            nb.l.new(geo.outputs["Normal"], bit.inputs[0])
            nb.l.new(tg.outputs["Tangent"], bit.inputs[1])
            dvec = nb.n.new("ShaderNodeMix")
            dvec.data_type = "VECTOR"
            nb.l.new(hz, dvec.inputs["Factor"])
            nb.l.new(bit.outputs["Vector"], dvec.inputs[4])        # hz = 0: fibres along v
            nb.l.new(tg.outputs["Tangent"], dvec.inputs[5])        # hz = 1: fibres along u
            slope = nb.math("MULTIPLY", nb.math("COSINE", nb.math("MULTIPLY", alg.outputs[0], math.pi)),
                            float(p["crimp"]) * 1e-6 * math.pi / tw)
            sc_ = nb.n.new("ShaderNodeVectorMath")
            sc_.operation = "SCALE"
            nb.l.new(dvec.outputs[1], sc_.inputs[0])
            nb.l.new(slope, sc_.inputs["Scale"])
            sub_ = nb.n.new("ShaderNodeVectorMath")
            sub_.operation = "SUBTRACT"
            nb.l.new(geo.outputs["Normal"], sub_.inputs[0])
            nb.l.new(sc_.outputs["Vector"], sub_.inputs[1])
            nrm_ = nb.n.new("ShaderNodeVectorMath")
            nrm_.operation = "NORMALIZE"
            nb.l.new(sub_.outputs["Vector"], nrm_.inputs[0])
            crimp_n = nrm_.outputs["Vector"]
            arch = 0.0
        elif cshape > 0:
            # tile envelope: 0 on all four edges (the crossing tapes are at 0 there too), so no step round the tile
            acx = nb.n.new("ShaderNodeMix")
            acx.data_type = "FLOAT"
            nb.l.new(hz, acx.inputs["Factor"])
            nb.l.new(fu, acx.inputs[2])
            nb.l.new(fv, acx.inputs[3])
            s_al = nb.math("SINE", nb.math("MULTIPLY", alg.outputs[0], math.pi))
            s_ac = nb.math("POWER", nb.math("MAXIMUM", nb.math("SINE", nb.math("MULTIPLY", acx.outputs[0], math.pi)), 0.0),
                           float(p.get("crimp_p", 0.5)))
            arch = nb.math("MULTIPLY", s_al, s_ac)
        else:
            e_ = nb.math("SUBTRACT", nb.math("MULTIPLY", alg.outputs[0], 2.0), 1.0)
            arch = nb.math("SUBTRACT", 1.0, nb.math("MULTIPLY", e_, e_))
        hgt = nb.math("MULTIPLY", arch, float(p["crimp"]) if crimp_n is None else 0.0)
        hgt = nb.math("MULTIPLY_ADD", fibn, 2.0 * float(p["fib_h"]), hgt)
        if float(p["seam"]) > 0:
            hgt = nb.math("SUBTRACT", hgt, nb.math("MULTIPLY", nb.smooth(d, 0.96, 1.0), float(p["seam"])))
        bump = nb.n.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 1.0
        bump.inputs["Distance"].default_value = 1e-6
        if crimp_n is not None:
            nb.l.new(crimp_n, bump.inputs["Normal"])
    else:
        hgt = nb.math("ADD", crown, nb.math("MULTIPLY", stri, 0.08))
        bump = nb.n.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.25
        bump.inputs["Distance"].default_value = 0.00004
    nb.l.new(hgt, bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = p["coat_rough"]
    b.inputs["Coat IOR"].default_value = 1.52
    # K11's in-band tile flip: the coat of alternate tapes mirrors the light (1 - flip) as strongly (v5: flip 0)
    coat_w = nb.math("SUBTRACT", 1.0, nb.math("MULTIPLY", hz, p["flip"]))
    nb.l.new(coat_w, b.inputs["Coat Weight"])
    if fib and float(p.get("beckmann", 0.0)) > 0:
        # round 6: the fibre sheen as its own anisotropic BECKMANN glossy under the coat, added to a Principled that
        # keeps only the clear coat. GGX's long tails let the very bright band card (strength 14-26) glow across the
        # whole face through the fibre lobe (the 'lifted black'); Beckmann's tails fall off as exp(-tan^2/a^2), so the
        # tapes catch the band near it and the rest of the face stays black. Same lobe as the Principled's: Glossy
        # anisotropy sqrt(1 - 0.9 aniso) - 1 (negative = wide along the tangent, as Principled), same rotation and
        # tangent, the fibre / crimp normal, reflectance = the tape albedo x 0.92 (the coat's two passes).
        for l_ in list(b.inputs["Base Color"].links):
            nb.l.remove(l_)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        b.inputs["Metallic"].default_value = 0.0
        b.inputs["Specular IOR Level"].default_value = 0.0
        gl = nb.n.new("ShaderNodeBsdfAnisotropic")
        gl.distribution = "BECKMANN"
        cg = nb.n.new("ShaderNodeCombineColor")
        for k, f in enumerate((0.97, 1.0, 1.04)):
            nb.l.new(nb.math("MULTIPLY", col, f * 0.92), cg.inputs[k])
        nb.l.new(cg.outputs[0], gl.inputs["Color"])
        nb.l.new(rgh, gl.inputs["Roughness"])
        gl.inputs["Anisotropy"].default_value = math.sqrt(1.0 - 0.9 * float(p["aniso"])) - 1.0
        nb.l.new(rotv, gl.inputs["Rotation"])
        nb.l.new(tg.outputs["Tangent"], gl.inputs["Tangent"])
        nb.l.new(bump.outputs["Normal"], gl.inputs["Normal"])
        add_ = nb.n.new("ShaderNodeAddShader")
        nb.l.new(b.outputs[0], add_.inputs[0])
        nb.l.new(gl.outputs[0], add_.inputs[1])
        nb.l.new(add_.outputs[0], out.inputs["Surface"])
    if PACE_PROBE == "albedo":
        # measurement: emission (R = albedo luminance x 10, G = hz, B = coat weight), read by shots/pace_measure.py
        lum = nb.math("MULTIPLY", col, 10.0 * (0.2126 * 0.97 + 0.7152 * 1.0 + 0.0722 * 1.04))
        pc = nb.n.new("ShaderNodeCombineColor")
        nb.l.new(lum, pc.inputs[0])
        nb.l.new(hz, pc.inputs[1])
        nb.l.new(coat_w, pc.inputs[2])
        em = nb.n.new("ShaderNodeEmission")
        nb.l.new(pc.outputs[0], em.inputs["Color"])
        nb.l.new(em.outputs[0], out.inputs["Surface"])
        return m
    if etch:
        _etch_layer(m, b, etch, p, p["coat_rough"])
    if wall:  # throat wall: falls to black with depth, as k10_lib's wall
        out_, surf = _out_surface(m)
        _, _, z = nb.coords("Object")
        occ = nb.math("MULTIPLY", nb.smooth(z, ZT - 0.0025, ZT - 0.017), 0.93)
        blk = nb.n.new("ShaderNodeBsdfDiffuse")
        blk.inputs["Color"].default_value = (0, 0, 0, 1)
        mo = nb.n.new("ShaderNodeMixShader")
        nb.l.new(occ, mo.inputs[0])
        nb.l.new(surf, mo.inputs[1])
        nb.l.new(blk.outputs[0], mo.inputs[2])
        nb.l.new(mo.outputs[0], out_.inputs["Surface"])
    return m


def mat_white(name, o=None, etch=None, wall=False):
    """Command's WHITE 3K twill: K10's baked twill maps (k04_tex2, 2.6 mm tows, fold UVs) read as white fibre in clear
    resin. Base: a dielectric white tow whose tone carries the baked tow-to-tow variation and crevice shadow (alb_k),
    a tone step between the two fibre directions (dir_tone) and fibre-bundle streaks; an anisotropic fibre sheen rotated
    per tow (so the twill flips inside a highlight); the tow relief as bump (so it also reads in shade); a glass-clear
    coat (0.03) with K10's whisper of print-through. etch: the laser mark (a graphite frost on white, see
    COMMAND_WHITE). wall: the throat wall (tows run straight down it, occlusion toward a dark graphite with depth)."""
    p = dict(COMMAND_WHITE, **(o or {}))
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    tc = nb.n.new("ShaderNodeTexCoord")
    mp = nb.n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / L.TILE, 1 / L.TILE, 1)
    nb.l.new(tc.outputs["UV"], mp.inputs["Vector"])
    vec = mp.outputs["Vector"]
    alb = L._img(nb, vec, os.path.join(L.TEX2, "albedo.png"), "sRGB")
    rgh = L._img(nb, vec, os.path.join(L.TEX2, "rough.png"), "Non-Color")
    hgt = L._img(nb, vec, os.path.join(L.TEX2, "height16.png"), "Non-Color", interp="Cubic")
    rot = L._img(nb, vec, os.path.join(L.TEX2, "rot16.png"), "Non-Color")
    cot = L._img(nb, vec, os.path.join(L.TEX2, "coat16.png"), "Non-Color", interp="Cubic")
    along_u = nb.smooth(rot.outputs["Color"], 0.42, 0.58)  # 1: fibres along u, 0: along v
    # fibre-bundle streaks along each tow (k10_lib's straight 1D noise, picked by the tow's direction)
    streak = None
    if float(p["streak"]) > 0:
        uu, vv, _ = nb.coords("UV")
        S, Sl = 1.0 / float(p["streak_w"]), 1.0 / float(p["streak_len"])

        def n1(a_, b_, z_):
            cv_ = nb.n.new("ShaderNodeCombineXYZ")
            nb.l.new(nb.math("MULTIPLY", a_, S), cv_.inputs[0])
            nb.l.new(nb.math("MULTIPLY", b_, Sl), cv_.inputs[1])
            cv_.inputs[2].default_value = z_
            t_ = nb.n.new("ShaderNodeTexNoise")
            t_.noise_dimensions = "3D"
            t_.inputs["Scale"].default_value = 1.0
            t_.inputs["Detail"].default_value = 2.0
            t_.inputs["Roughness"].default_value = 0.6
            nb.l.new(cv_.outputs[0], t_.inputs["Vector"])
            return nb.smooth(t_.outputs["Fac"], 0.3, 0.7)

        streak = nb.math("SUBTRACT", nb.lerp(along_u, n1(uu, vv, 7.3), n1(vv, uu, 0.0)), 0.5)  # -0.5..0.5
    # tone: baked albedo (linear, median about 0.61; crevices about 0.30) normalised so a typical tow is 1.0
    k_ = float(p["alb_k"])
    tone = nb.math("MULTIPLY_ADD", alb.outputs["Color"], k_ / 0.62, 1.0 - k_)
    tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", along_u, 0.5), float(p["dir_tone"]), 1.0))
    if streak is not None:
        tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", streak, float(p["streak_a"]), 1.0))
    tone = nb.math("MINIMUM", tone, 1.12)
    cc = nb.n.new("ShaderNodeCombineColor")
    for k, t_ in enumerate(p["tint"]):
        nb.l.new(nb.math("MULTIPLY", tone, float(t_)), cc.inputs[k])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    rr = nb.math("MULTIPLY", rgh.outputs["Color"], float(p["rough_s"]))
    if streak is not None:
        rr = nb.math("MULTIPLY", rr, nb.math("MULTIPLY_ADD", streak, float(p["streak_r"]), 1.0))
    nb.l.new(rr, b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = float(p["metal"])
    b.inputs["IOR"].default_value = float(p["ior"])
    b.inputs["Specular IOR Level"].default_value = float(p["spec"])
    b.inputs["Anisotropic"].default_value = float(p["aniso"])
    rotv = nb.math("MULTIPLY_ADD", rot.outputs["Color"], 0.5, -0.125)
    tg = nb.n.new("ShaderNodeTangent")
    tg.direction_type = "UV_MAP"
    tg.uv_map = "UVMap"
    tang = tg.outputs["Tangent"]
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = float(p["bump"])
    bump.inputs["Distance"].default_value = 0.00025
    if streak is not None:
        nb.l.new(nb.math("MULTIPLY_ADD", streak, float(p["streak_h"]), hgt.outputs["Color"]), bump.inputs["Height"])
    else:
        nb.l.new(hgt.outputs["Color"], bump.inputs["Height"])
    cb = nb.n.new("ShaderNodeBump")
    cb.inputs["Strength"].default_value = float(p["print"])
    cb.inputs["Distance"].default_value = 0.00025
    nb.l.new(cot.outputs["Color"], cb.inputs["Height"])
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat IOR"].default_value = 1.5
    coat_r = float(p["coat_rough"])
    b.inputs["Coat Roughness"].default_value = coat_r
    occ = None
    if wall:  # as k10_lib's throat wall: tows fold straight down it, the fibre tangent turns horizontal, occlusion
        _, _, z = nb.coords("Object")
        below = nb.smooth(z, ZT - 0.0015, ZT - 0.0021)
        geo = nb.n.new("ShaderNodeNewGeometry")
        cr = nb.n.new("ShaderNodeVectorMath")
        cr.operation = "CROSS_PRODUCT"
        cr.inputs[0].default_value = (0, 0, 1)
        nb.l.new(geo.outputs["Normal"], cr.inputs[1])
        cz = nb.n.new("ShaderNodeVectorMath")
        cz.operation = "NORMALIZE"
        nb.l.new(cr.outputs[0], cz.inputs[0])
        mt = nb.n.new("ShaderNodeMix")
        mt.data_type = "VECTOR"
        nb.l.new(below, mt.inputs["Factor"])
        nb.l.new(tang, mt.inputs[4])
        nb.l.new(cz.outputs[0], mt.inputs[5])
        tang = mt.outputs[1]
        rotv = nb.math("MULTIPLY", rotv, nb.math("SUBTRACT", 1.0, below))
        occ = nb.math("MULTIPLY", nb.smooth(z, ZT - 0.0025, ZT - 0.017), float(p["wall_occ"]))
    nb.l.new(rotv, b.inputs["Anisotropic Rotation"])
    nb.l.new(tang, b.inputs["Tangent"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    nb.l.new(cb.outputs["Normal"], b.inputs["Coat Normal"])
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    if etch:
        _etch_layer(m, b, etch, p, coat_r)
    if occ is not None:
        out_, surf = _out_surface(m)
        dk = nb.n.new("ShaderNodeBsdfDiffuse")
        wd = float(p["wall_dark"])
        dk.inputs["Color"].default_value = (wd, wd, wd * 1.04, 1)
        mo = nb.n.new("ShaderNodeMixShader")
        nb.l.new(occ, mo.inputs[0])
        nb.l.new(surf, mo.inputs[1])
        nb.l.new(dk.outputs[0], mo.inputs[2])
        nb.l.new(mo.outputs[0], out_.inputs["Surface"])
    return m


def is_white(feel, o=None):
    """Command builds white carbon unless mat_opts={"white": 0} (the previous canon's black K10 twill)."""
    return feel == "command" and float((o or {}).get("white", 1.0)) > 0


def mat_carbon(feel, role, serial=None, o=None):
    """role: face (with the serial etch), skin (back, rim, wall, neck), throat (throat walls), bore (holes).
    Cached by name: every racket of a feel shares its materials; each serial gets its own face material.
    Command is white (mat_white); o={"white": 0} gives the previous canon's black K10 twill (cached as command-black)."""
    white = is_white(feel, o)
    rest = {k: v for k, v in (o or {}).items() if k != "white"}
    tag = "command-black" if (feel == "command" and not white) else feel
    key = "KQc_%s_%s" % (tag, role) + ("_" + serial if role == "face" else "")
    m = bpy.data.materials.get(key)
    if m is not None and not rest:
        return m
    o = rest or None
    etch = serial_etch(serial) if (role == "face" and serial) else None
    if white:
        p = dict(COMMAND_WHITE, **(o or {}))
        if role == "throat":
            m = mat_white(key, o, wall=True)
        elif role == "bore":
            m = _bore_wrap(mat_white(key, o, wall=True), z_dark=float(p["bore_dark"]), occ=float(p["bore_occ"]),
                           col=float(p["bore_col"]))
        else:
            m = mat_white(key, o, etch=etch)
    elif feel == "command":
        base = dict(COMMAND, **(o or {}))
        if role == "throat":
            m = L.mat_carbon_k10(key, dict(COMMAND_WALL, **(o or {})), wall=True)
        elif role == "bore":
            m = _bore_wrap(L.mat_carbon_k10(key, dict(COMMAND_BORE, **(o or {})), wall=True))
        else:
            m = L.mat_carbon_k10(key, base, etch=etch)
    elif feel == "pace":
        if role == "throat":
            m = mat_pace(key, wall=True, o=o)
        elif role == "bore":
            m = _bore_wrap(mat_pace(key, o=o))
        else:
            m = mat_pace(key, etch=etch, o=o)
    else:
        raise ValueError("feel must be one of %s" % (FEELS,))
    return m


def mat_overgrip(name="KQ_Overgrip", base=0.016):
    """Neutral black perforated overgrip (K05's, on the grip's UVs: u around, v = y): satin with a little sheen,
    9 rows of fine perforations across each wrap, about 40 per turn; the wrap's seams and overlap are geometry."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (base, base, base * 1.06, 1)
    b.inputs["Roughness"].default_value = 0.5
    b.inputs["Sheen Weight"].default_value = 0.15
    b.inputs["Sheen Tint"].default_value = (0.8, 0.82, 0.86, 1)
    b.inputs["Coat Weight"].default_value = 0.25
    b.inputs["Coat Roughness"].default_value = 0.3
    u, v, _ = nb.coords("UV")
    y0 = GRIP_Y[0]
    ph = nb.math("FRACT", nb.math("ADD", nb.math("MULTIPLY_ADD", v, -1.0 / GRIP_PITCH, y0 / GRIP_PITCH), u))
    across = nb.math("MULTIPLY", ph, 9.0)
    row = nb.math("FLOOR", across)
    fa = nb.math("FRACT", across)
    along = nb.math("FRACT", nb.math("MULTIPLY_ADD", u, 40.0, nb.math("MULTIPLY", row, 0.5)))
    cmb = nb.n.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("SUBTRACT", fa, 0.5), cmb.inputs["X"])
    nb.l.new(nb.math("SUBTRACT", along, 0.5), cmb.inputs["Y"])
    ln = nb.n.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nb.l.new(cmb.outputs[0], ln.inputs[0])
    hole = nb.smooth(ln.outputs["Value"], 0.13, 0.2)  # 0 in a perforation, 1 on the tape
    tc = nb.n.new("ShaderNodeTexCoord")
    nz = nb.n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1400
    nz.inputs["Detail"].default_value = 2
    nb.l.new(tc.outputs["Object"], nz.inputs["Vector"])
    h = nb.math("MULTIPLY_ADD", nz.outputs["Fac"], 0.12, hole)
    bp = nb.n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.5
    bp.inputs["Distance"].default_value = 0.0003
    nb.l.new(h, bp.inputs["Height"])
    nb.l.new(bp.outputs["Normal"], b.inputs["Normal"])
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_cap(name="KQ_CapAnodised"):
    """Satin black anodised aluminium: no polished chamfer, no chrome."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.040, 0.040, 0.044, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.30
    b.inputs["Anisotropic"].default_value = 0.3
    tc = nb.n.new("ShaderNodeTexCoord")
    nz = nb.n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 6000
    nz.inputs["Detail"].default_value = 1
    nb.l.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = nb.n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.05
    bp.inputs["Distance"].default_value = 0.00002
    nb.l.new(nz.outputs["Fac"], bp.inputs["Height"])
    nb.l.new(bp.outputs["Normal"], b.inputs["Normal"])
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_engraving(name="KQ_Engraving"):
    """Bright-cut aluminium (K05's finish): the Q's chamfer, and the whole mark when a glyph text is used."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.55, 0.55, 0.57, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.35
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_engraving_floor(name="KQ_EngravingFloor"):
    """The floor of the engraved Q: satin graphite (the cut through the black anodising, dulled), a step lighter than
    the cap in diffuse light and darker than the chamfer: the mark reads as cut, never as a white ring."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.17, 0.17, 0.176, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.50
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_wall_frost(name="KQ_WallFrost", level=0.30):
    """Laser frost on the side wall (K11's mat_frost, a little darker): pale satin grey under a rake, quiet otherwise."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (level, level, level * 1.02, 1)
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Specular IOR Level"].default_value = 0.35
    tc = nb.n.new("ShaderNodeTexCoord")
    wn = nb.n.new("ShaderNodeTexNoise")
    wn.inputs["Scale"].default_value = 9000.0
    wn.inputs["Detail"].default_value = 2
    nb.l.new(tc.outputs["Object"], wn.inputs["Vector"])
    bp = nb.n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.25
    bp.inputs["Distance"].default_value = 0.00002
    nb.l.new(wn.outputs["Fac"], bp.inputs["Height"])
    nb.l.new(bp.outputs["Normal"], b.inputs["Normal"])
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ the racket
ROLE = {"face": "face", "back": "skin", "rim": "skin", "wall": "skin", "neck": "skin", "bridgewall": "throat",
        "throat": "throat", "holes": "bore"}


def _role(key):
    return "throat" if key.startswith("thr") else ROLE[key]


def build_racket(name="KQ", feel="command", serial=SERIAL, walls=True, holes=None, throat_segs=None, mat_opts=None,
                 head_kw=None, mark_az=0.0):
    """The canonical racket under an Empty `name` at the origin. Returns (root, parts {part: object}).
    feel: "command" (WHITE 3K twill: the default for every shot that names no feel) or "pace" (black 12K, only where
    Pace is chosen or compared). serial: the throat mark (None = no mark). walls: the side-wall etches (graphite frost on
    white, pale frost on black). throat_segs: k10_lib.THROAT_SEGS for K10's per-segment throat.
    mat_opts: material overrides for every role: COMMAND_WHITE keys for Command ({"white": 0} gives the previous canon's
    black K10 twill, then k10_lib.mat_carbon_k10 keys), PACE keys for Pace. mark_az (deg): turn the engraved Q round the
    handle axis toward model +x so it faces a shot's camera (the cap itself follows the grip section and does not turn)."""
    assert feel in FEELS, feel
    head = build_head(name, holes=holes, throat_segs=throat_segs, **(head_kw or {}))
    for key, ob in head.items():
        ob.data.materials.append(mat_carbon(feel, _role(key), serial, mat_opts))
    grip = build_grip(name + "_grip")
    grip.data.materials.append(mat_overgrip())
    grip["kq_part"] = "grip"
    cap = build_cap(name + "_cap")
    cap.data.materials.append(mat_cap())
    cap["kq_part"] = "cap"
    mark = build_cap_mark(name + "_capmark", cap, az=mark_az)
    mark.data.materials.append(mat_engraving_floor())   # 0: the floor of the cut
    mark.data.materials.append(mat_engraving())         # 1: the bright-cut chamfer
    mark["kq_part"] = "capmark"
    parts_ = dict(head)
    parts_.update(grip=grip, cap=cap, capmark=mark)
    if walls:
        if is_white(feel, mat_opts):  # a graphite laser mark on the white wall
            fr = mat_wall_frost("KQ_WallFrost_white", level=float(dict(COMMAND_WHITE, **(mat_opts or {}))["wall_frost"]))
        else:
            fr = mat_wall_frost()
        e = KL.etch_wall(head["wall"], "KINETIQ", WALL_ETCH_Y, 0.0034, side=1, name=name + "_etchR", mat=fr, font=racket.FONT_BOLD)
        e["kq_part"] = "etchR"
        e2 = KL.etch_wall(head["wall"], "SWISS MADE", WALL_ETCH_Y, 0.0030, side=-1, name=name + "_etchL", mat=fr,
                          font=racket.FONT_MED, spacing=1.25)
        e2["kq_part"] = "etchL"
        parts_.update(etchR=e, etchL=e2)
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for ob in parts_.values():
        mw = ob.matrix_world.copy()
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_world = mw
    root["kq_feel"] = feel
    root["kq_serial"] = serial or ""
    root["kq_mat_opts"] = repr(dict(mat_opts or {}))
    return root, parts_


def parts(root):
    """{part: object} of a racket or a clone."""
    return {c["kq_part"]: c for c in root.children if "kq_part" in c}


# Part names of the old builders -> canon parts, so a shot can switch with few edits (objs(P, "outer", style="k12")).
LEGACY = {
    # k12_lib.build_racket_rounded (K01, K02): P["outer"], P["bevel"], P["throat"], P["inner"], grip, collar, cap
    "k12": {"outer": ("face", "back", "wall", "neck"), "bevel": ("rim",), "throat": ("throat", "bridgewall"),
            "inner": ("holes",), "grip": ("grip",), "collar": (), "cap": ("cap", "capmark")},
    # k789_lib.make_racket (K07, K08, K09, K11): L.part(root, suffix)
    "k789": {"_Head": ("face", "back", "wall", "neck"), "HeadBevel": ("rim",), "_HeadBevel": ("rim",),
             "_HeadInner": ("holes", "throat", "bridgewall"), "_grip": ("grip",), "_collar": (), "_cap": ("cap", "capmark"),
             "_EtchR": ("etchR",)},
    # k10_lib.build_head_k10 (K10): head[key]
    "k10": {"face": ("face",), "rim": ("rim", "wall"), "neck": ("neck",), "holes": ("holes",), "bridgewall": ("bridgewall",)},
}


def objs(src, *names, style=None):
    """Flat list of part objects for light linking. src: a racket root or its parts dict; names: canon part names,
    'head' (every head part), 'handle' (grip, cap, capmark), 'all', or an old builder's names with style=k12|k789|k10."""
    P = parts(src) if isinstance(src, bpy.types.Object) else src
    head = [k for k in P if k in ("face", "back", "rim", "wall", "neck", "holes", "bridgewall", "throat") or k.startswith("thr")]
    out = []
    for n in names:
        if style and n in LEGACY[style]:
            keys = LEGACY[style][n]
            if n == "throat" or n == "_HeadInner":
                keys = tuple(keys) + tuple(k for k in P if k.startswith("thr") and k != "throat")
        elif n == "head":
            keys = head
        elif n == "handle":
            keys = ("grip", "cap", "capmark")
        elif n == "all":
            keys = tuple(P)
        else:
            keys = (n,)
        out += [P[k] for k in keys if k in P and P[k] not in out]
    return out


def clone(src, name, serial=None):
    """Linked duplicate (every part shares its mesh) under a new Empty with the same transform; with `serial`, its
    face gets its own material carrying that serial (slot linked to the object, the mesh stays shared)."""
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    root.matrix_world = src.matrix_world.copy()
    feel = src.get("kq_feel", "command")
    import ast
    mo = ast.literal_eval(src.get("kq_mat_opts", "{}")) or None  # the source's material options (e.g. {"white": 0})
    for c in list(src.children):
        cc = c.copy()
        cc.name = name + "_" + c.get("kq_part", c.name)
        bpy.context.scene.collection.objects.link(cc)
        cc.parent = root
        cc.matrix_parent_inverse = c.matrix_parent_inverse.copy()
        cc.matrix_basis = c.matrix_basis.copy()
        if serial and c.get("kq_part") == "face":
            KL.override_material(cc, mat_carbon(feel, "face", serial, mo))
    root["kq_feel"] = feel
    root["kq_mat_opts"] = src.get("kq_mat_opts", "{}")
    root["kq_serial"] = serial or src.get("kq_serial", "")
    return root, parts(root)


def pose(root, loc, yaw_deg=0.0, roll_deg=0.0, tilt_deg=0.0):
    """Place a racket: in-plane roll about the face normal, tilt about X (90 = stood upright, front face to -Y), then
    yaw about world Z; loc = where the head centre goes. tilt 0 keeps the model frame (face up +Z, head +Y)."""
    root.matrix_world = (Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(yaw_deg), 4, "Z")
                         @ Matrix.Rotation(math.radians(tilt_deg), 4, "X") @ Matrix.Rotation(math.radians(roll_deg), 4, "Z"))
    return root


# ------------------------------------------------------------------ spec check
def measure(root):
    """Model-space extents (mm) of the racket's surfaces (marks excluded) and its hole count, asserted against the
    spec: 455.0 +- 0.3 long, 260.0 +- 0.3 wide (FIP maximum; see WIDTH), 38.0 +- 0.05 thick, 42 holes of which 8 are
    14 mm."""
    inv = root.matrix_world.inverted()
    lo, hi = np.full(3, 1e9), np.full(3, -1e9)
    for key, ob in parts(root).items():
        if key in ("capmark", "etchR", "etchL"):
            continue
        M = np.array(inv @ ob.matrix_world)
        co = np.empty(len(ob.data.vertices) * 3)
        ob.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
        lo, hi = np.minimum(lo, co.min(0)), np.maximum(hi, co.max(0))
    ext = (hi - lo) * 1000
    hs = holes_canon()
    r = dict(length=ext[1], width=ext[0], thick=ext[2], tip=hi[1] * 1000, butt=lo[1] * 1000, holes=len(hs),
             crown=sum(1 for h in hs if abs(h[2] - CROWN_R) < 1e-6))
    assert abs(r["length"] - 455.0) <= 0.3, r
    assert abs(r["width"] - WIDTH * 1000) <= 0.3, r
    assert abs(r["thick"] - 38.0) <= 0.05, r
    assert r["holes"] == 42 and r["crown"] == 8, r
    return r


if __name__ == "__main__":
    import time
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for feel in FEELS:
        rt, P = build_racket("KQ_" + feel, feel=feel)
        m = measure(rt)
        print(feel, " ".join("%s %.2f" % (k, v) if isinstance(v, float) else "%s %s" % (k, v) for k, v in m.items()))
        print("  parts:", ", ".join("%s %d" % (k, len(o.data.polygons)) for k, o in P.items()))
        print("  face", P["face"].material_slots[0].material.name, "| wall etch", P["etchR"].material_slots[0].material.name,
              "| cap mark", P["capmark"].dimensions.x * 1000, "x", P["capmark"].dimensions.y * 1000, "mm")
    r2, P2 = clone(rt, "KQ_clone", serial="KQ-000428")
    print("clone", measure(r2)["length"], P2["face"].material_slots[0].material.name)
    print("serial box (mm)", [round(v * 1000, 2) for v in serial_box(SERIAL)])
    print("ok %.1f s" % (time.time() - t0))
