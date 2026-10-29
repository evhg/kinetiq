"""K02-edge-line: the canonical racket (shots/kq_canon.py, Command = WHITE 3K twill, KQ-000427) edge-on, laid
horizontally (handle left, tip right), in a luminous graphite void. The 38 mm right side wall reads as ONE unbroken carbon band from the tip,
through the one-piece neck (no block end, no collar, no joint) into the grip's 11 mm finishing band, framed by a razor
light line on its top edge and an equal line on its bottom edge, so the image stays valid rotated 90 degrees (phones).
The racket is rolled 3.5 degrees toward camera: a lit sliver of the face shows above the band with the hole rows
(the crown of 8 at the tip end) as dark slits. Walls carry only the canonical etches (KINETIQ on this right wall).
The cap is satin black anodised (engraved Q): no chrome, no copper.

White Command is lit by real diffuse light (canon.md, lighting note 8): a long soft key in front and above the camera
axis (lg_wkey) makes the white wall one luminous band tip to grip, an overhead card (lg_wtop) keeps the face sliver
white so the hole rows read as dark slits; the reflection cards still draw the razor lines and the lacquer sheen. The
wall etch is lit by the wall light, never raked (a rake turns the graphite frost pale and it vanishes).
MAT_OPTS={"white": 0} (--set) gives back the black Command studio exactly.

ONE render writes denoised light-group passes (lg_top, lg_under, lg_face, lg_fill, lg_neck, lg_grip, lg_cap, lg_etch,
lg_wall); the comp sums them (gains adjustable without re-rendering) and applies the post grade.

Usage (from the blender dir, through the lock):
  flock render.lock ../bpyenv/bin/python shots/K02-edge-line.py --w 960 --h 540 --spp 32 --out k02v2/K02_p01 [--phone]
  final: flock render.lock ../bpyenv/bin/python shots/K02-edge-line.py --w 2560 --h 1440 --spp 192 --out final/K02-edge-line --phone
  re-comp: ../bpyenv/bin/python shots/K02-edge-line.py --comp --out k02v2/K02_p01 [--gain fill=1.2 ...] [--phone]
Dev: --set NAME=value, --crop x0 x1 y0 y1. --phone also writes <out>-phone.png, pre-rotated 90 deg CCW (handle down).
Swivel (Release 4, 2026-10-28: the Unibody chapter's scroll-scrubbed turn, as K01's hero swivel): --swivel DEG turns
the racket about its handle axis (world X through the racket's centre line) by DEG on top of ROLL, AFTER the studio is
built, so every card and lamp stays fixed and the light sweeps over the wall and face as it turns (+ = the face tips
further toward the camera). 0 (the default) changes nothing. SWIVEL_AXIS="Z" turns it about the vertical instead (dev).
--seq N --range A B --out seq/<name> renders N frames (A..B, linear) from ONE scene build into
$KQ_RENDER_OUT/out/seq/<name>-desktop/f000.png ..; with --phone each frame is also written rotated 90 deg CCW into
<name>-phone/ (the K02 portrait crop is the wide master rotated, stills.json). Frames on disk are skipped (resume).
Final (one lock per feel; scripts/sequence.mjs exports them):
  flock render.lock $PY shots/K02-edge-line.py --w 1280 --h 720 --spp 24 --seq 30 --range 0 35 --phone --out seq/K02-swivel-command
  flock render.lock $PY shots/K02-edge-line.py --feel pace --w 1280 --h 720 --spp 24 --seq 30 --range 0 35 --phone --out seq/K02-swivel-pace
  (2026-10-28: 1920 x 1080 cost 3 min of path tracing a frame at 20 spp on 4 cores, so the finals are 1280 x 720, the
  width sequence.mjs exports anyway below 1920; one frame per lock via --only i lets other shots interleave.) Pace
  holds to 35 degrees here: lg_swivel keeps its face lit (out/k02dev/sheetswP2.png), unlike the hero's 24.
v1 (k12 racket, collar, chrome cap, "SWISS MADE No. 0001"): K02-edge-line.v1.bak
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
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

ROLL = 3.5           # degrees: front face tipped toward camera -> a thin lit sliver of the face above the band
TOP_S = 11.0         # behind-above card: razor line on the band's top edge
UNDER_S = 11.0       # behind-below card: the equal line on the band's bottom edge
FACE_S = 0.35        # low card behind: the face sliver glows, hole rows read as dark slits
FILL_S = 1.6         # eye-level ring in front: the band's sheen, tip to grip
FILL_EL = (-16.0, 6.0)   # the ring's elevation band (deg)
GRIP_S = 8.0         # low soft front card, grip only
CAP_S = 0.6          # soft strip mirrored by the cap's side band (satin black, groove)
ETCH_W = 0.6         # raking light on the KINETIQ wall etch
VOID_C, VOID_E = 37, 22    # graphite void, display luma: #26262b centre, #16161a edges
BAND_D = 56          # luminous horizontal strip behind the racket, display luma on its axis
BAND_SIGMA = 0.12
CAM_D = 0.230 * 2 / 0.76 / (36 / 135)
X_SHIFT = -(C.TIP_Y + C.BUTT_Y) / 2   # centre the 455 mm racket in the frame
import k01_lib as K01  # noqa: E402  (the hero group's shared white weave settings)
import g1_detail as GD  # noqa: E402
MAT_OPTS = dict(K01.WEAVE_W)   # kq_canon mat_opts (white weave, as K01); {"white": 0} = the previous black Command
# white (critic G1): the wall is a LINE of light, not a flat white slab. Body at about luma 150-185, hottest at the
# neck / throat and falling about 20 % toward the tip; a crisp 2-3 px specular hairline (luma 235-245) on the top
# 1.5 mm edge, continued as a soft satin stripe across the grip's 11 mm finishing band at the same height.
WK_W = 12.0          # white: the long soft key in front, above the camera axis (W): the band's even base
WH_W = 126.0         # white: a soft wide spot pool centred left of the neck: the band's gradient (lg_whot)
WH_AT, WH_TGT, WH_DEG = (-0.85, -1.20, 0.45), (-0.15, 0.0, 0.0), 40.0   # from the front left: the wall facing
# the handle end takes it square, the tip end turns away from it (the gradient follows the outline's own turn)
BAND_S = 34.0         # white: the satin stripe on the grip's finishing band (a short strip behind-above, grip only)
BAND_AT, BAND_SIZE = (-0.13, 0.42, 0.25), (0.03, 0.40)
GRIPEDGE_S, GRIPEDGE_SIZE = 1.5, (2.8, 1.8)
TOPCARD_W = (2.8, 1.7)  # white: a taller top card, so the hairline covers more of the 1.5 mm edge's curve (2-3 px at 2560)
WTIP_W, WTIP_AT = 4.0, (0.95, -1.05, 0.35)    # white: a small front-right lamp on the tip's turning wall (the gentle fall)   # white: grip / cap edge lines, wide and soft (luma 110-130, no chrome)
DETAIL_W = (2.0, 1.3, 1.6, 0.55, 0.75)        # comp: g1_detail on the wall, neck and face sliver (see k01_lib)
WK_AT = (0.10, -1.50, 0.55)
WK_SIZE = (1.8, 0.35)
# the key bar in four segments, handle end to tip, each with its share of WK_W: the band's gentle fall toward the tip
WK_SEG = ((-0.36, 1.0), (-0.12, 0.88), (0.12, 0.72), (0.36, 0.58))
WT_W = 60.0          # white: overhead card for the face sliver (W)
TOP_S_W, UNDER_S_W = 55.0, 38.0   # white: the razor lines clear the wall (luma 150-185): top 235-245, bottom a step less
FACE_S_W = 0.7
WT_AT = (0.10, 0.25, 1.40)
BLOOM = (0.70, 0.12, 0.004)
BLOOM_W = (0.90, 0.08, 0.003)
# Pace (Release 2 feel toggle, 2026-10-23): --feel pace builds the canon Pace (kq_canon.PACE v6, black 12K) with the
# same camera, void, crop and composition. Black carbon takes this shot's black studio (the not-white branches: razor
# cards, face card, fill ring, etch rake; no diffuse key) plus the Pace recipe of K08 / K11 / K01: an off-specular
# weave card only the 12K's fibre lobes see (the tapes read on the wall, not a black hole), neutral 6500 K edges (no
# ember), an indirect clamp against fireflies. Default FEEL "command" leaves every Command output identical.
FEEL = "command"
P_TOP_K, P_UNDER_K = 1.0, 1.0     # Pace: multipliers on the razor-line cards
P_FILL_K = 1.0                    # Pace: multiplier on the fill ring (the wall's sheen)
P_FACE_K = 1.0                    # Pace: multiplier on the face-sliver card
P_WEAVE_S = 5.0                   # Pace weave card (W); 0 = off. 5: the tapes read on the wall at 1:1 (out/pr2/k02p_02c)
P_WEAVE_AT, P_WEAVE_SIZE = (0.0, -1.45, 0.55), (2.4, 0.9)
P_WEAVE_K = 6500.0
P_CLAMP = 4.0                     # Pace: indirect clamp (K08 CLAMP_IND); 0 = off
SWIVEL = 0.0          # deg: the scroll swivel's turn about the handle axis, on top of ROLL (see the docstring)
SWIVEL_AXIS = "X"     # "X": about the handle (the racket's long axis); "Z": about the vertical through its centre (dev)
# The swivel's face light (lg_swivel, built only for --swivel / --seq): as the face tips toward the camera it mirrors
# elevations 2 x (ROLL + swivel) behind the racket, far above the low FaceCard, and black Pace goes dark from about 10
# degrees (out/k02dev/sheetP.png). A ring card behind and above (az 180 +- SW_AZ, el SW_EL), glossy only, linked to
# the face + neck, gives the turning face a lacquer reflection that sweeps across it as it turns: a soft floor plus a
# brighter band at SW_BAND (fraction of the elevation span). Its comp gain ramps in over the first SW_RAMP degrees
# (0 at frame 0), so frame 0 stays the K02 still exactly. SW_C / SW_P: the ring's strength for Command / Pace.
SW_AZ, SW_EL = 70.0, (9.0, 82.0)
SW_BAND, SW_BAND_W, SW_FLOOR = 0.42, 0.07, 0.15
SW_C, SW_P = 1.2, 2.2
SW_RAMP = 8.0
GROUPS = ["lg_top", "lg_under", "lg_face", "lg_fill", "lg_grip", "lg_cap", "lg_etch", "lg_wall", "lg_wkey", "lg_wtop",
          "lg_whot", "lg_band"]
GAINS = {g: 1.0 for g in GROUPS}


def parse_args(argv, default_out):
    o = {"w": 960, "h": 540, "spp": 32, "out": default_out, "crop": None, "set": [], "gain": [], "phone": False,
         "comp": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--w", "--h", "--spp"):
            o[a[2:]] = int(argv[i + 1]); i += 2
        elif a == "--out":
            o["out"] = argv[i + 1]; i += 2
        elif a == "--crop":
            o["crop"] = [float(v) for v in argv[i + 1:i + 5]]; i += 5
        elif a == "--feel":
            o["feel"] = argv[i + 1]; i += 2
        elif a in ("--set", "--gain"):
            o[a[2:]].append(argv[i + 1]); i += 2
        elif a in ("--phone", "--comp"):
            o[a[2:]] = True; i += 1
        elif a == "--swivel":
            o["swivel"] = float(argv[i + 1]); i += 2
        elif a == "--seq":
            o["seq"] = int(argv[i + 1]); i += 2
        elif a == "--only":
            o["only"] = [int(v) for v in argv[i + 1].split(",")]; i += 2
        elif a == "--range":
            o["range"] = (float(argv[i + 1]), float(argv[i + 2])); i += 3
        else:
            i += 1
    g = globals()
    if o.get("feel"):
        assert o["feel"] in ("command", "pace"), o["feel"]
        g["FEEL"] = o["feel"]
        print("feel", FEEL, flush=True)
    for kv in o["set"]:
        k, v = kv.split("=", 1)
        assert k in g, k
        g[k] = eval(v)
        print("set", k, "=", g[k], flush=True)
    if o.get("swivel") is not None:
        g["SWIVEL"] = o["swivel"]
        print("swivel", SWIVEL, flush=True)
    if o.get("swivel") is not None or o.get("seq"):
        g["GROUPS"] = GROUPS + ["lg_swivel"]
        GAINS["lg_swivel"] = 1.0
    return o


def swivel_gain(deg):
    """The swivel face light's comp gain at this turn: 0 at the still, smoothly to 1 by SW_RAMP degrees."""
    t = min(1.0, max(0.0, abs(deg) / SW_RAMP)) if SW_RAMP > 0 else 1.0
    return t * t * (3 - 2 * t)


def swivel(sc, deg):
    """Turn the racket (its root; every part is parented to it) by deg about the handle axis: world X through the
    racket's centre line (y = z = 0), where build() lays it. Cards, lamps and the camera stay where build() put them."""
    root = bpy.data.objects[sc["racket_root"]]
    base = Matrix(json.loads(sc["racket_base"]))
    root.matrix_world = Matrix.Rotation(math.radians(deg), 4, SWIVEL_AXIS) @ base
    bpy.context.view_layer.update()


def build(o):
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.light_sampling_threshold = 0.0
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 1
    sc.cycles.glossy_bounces = 4
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.blur_glossy = 0.5
    vl = sc.view_layers[0]
    for g in GROUPS:
        vl.lightgroups.add(name=g)
    W6 = K.kelvin(6000)

    def group(ob, g):
        ob.lightgroup = g
        return ob

    # --- the canonical racket: handle left / tip right, right wall toward camera, front face up, rolled toward camera
    t0 = time.time()
    pace = FEEL == "pace"
    white = (not pace) and C.is_white("command", MAT_OPTS)
    sc["white"] = bool(white)
    root, P = C.build_racket("KQ", feel=FEEL, serial=C.SERIAL, mat_opts=None if pace else MAT_OPTS)
    if pace and P_CLAMP:
        sc.cycles.sample_clamp_indirect = P_CLAMP
    root.matrix_world = (Matrix.Translation((X_SHIFT, 0, 0)) @ Matrix.Rotation(math.radians(ROLL), 4, "X")
                         @ Matrix.Rotation(math.radians(-90), 4, "Z"))
    bpy.context.view_layer.update()
    print("racket built %.1f s" % (time.time() - t0), flush=True)
    M = root.matrix_world.copy()
    # the black handle must not mirror into the head (it would read as a glued-on block)
    for k in ("grip", "cap", "capmark"):
        P[k].visible_glossy = False
    for k_, i_ in (("face", 1), ("holes", 2), ("wall", 3), ("rim", 4), ("neck", 5), ("cap", 6), ("capmark", 7),
                   ("grip", 8), ("throat", 9), ("bridgewall", 9)):
        if k_ in P:
            P[k_].pass_index = i_
    D = CAM_D
    cam_loc = Vector((0, -D, 0))
    cam_m = M.inverted() @ cam_loc

    def place(ob):
        ob.matrix_world = M @ ob.matrix_basis
        return ob

    band = C.objs(P, "rim", "wall", "neck")      # the side band: head wall + edges + the one-piece neck
    # --- lg_top / lg_under: long cards behind the racket, above and below: one razor line per edge, tip to cap
    top = K.strip("Top", (0.0, 1.05, 0.62), TOPCARD_W if white else (2.8, 0.9), TOP_S_W if white else TOP_S * (P_TOP_K if pace else 1.0), (0, 0, 0),
                  color=W6, soft_ends=0.3, soft_w=0.12 if white else 0.2)
    L.link_only(top, C.objs(P, "rim", "wall") if white else (band if pace else band + C.objs(P, "grip", "cap")), "recv_top")
    group(top, "lg_top")
    if white:  # the neck's 12 mm rounding would spread the tall card into a hot patch: the original card, dimmer
        tn = K.strip("TopNeck", (0.0, 1.05, 0.62), (2.8, 0.9), TOP_S_W * 0.6, (0, 0, 0), color=W6, soft_ends=0.3, soft_w=0.2)
        L.link_only(tn, [P["neck"]], "recv_topneck")
        group(tn, "lg_top")
    under = K.strip("Under", (0.0, 1.05, -0.62), (2.8, 0.9), UNDER_S_W if white else UNDER_S * (P_UNDER_K if pace else 1.0), (0, 0, 0), color=W6,
                    soft_ends=0.3, soft_w=0.2)
    L.link_only(under, band if (white or pace) else band + C.objs(P, "grip", "cap"), "recv_under")
    group(under, "lg_under")
    if white or pace:  # the black grip and cap keep the black studio's edge lines: a white-wall strength outlines them in white
        # wide, soft and dim (critic G1: a crisp white lip on the satin cap and the grip's rims read as chrome)
        for nm, z_, s_, g_ in (("TopGrip", 0.62, GRIPEDGE_S, "lg_top"), ("UnderGrip", -0.62, GRIPEDGE_S, "lg_under")):
            cg = K.strip(nm, (0.0, 1.05, z_), GRIPEDGE_SIZE, s_, (0, 0, 0), color=W6, soft_ends=0.3, soft_w=0.45)
            L.link_only(cg, C.objs(P, "grip", "cap"), "recv_" + nm)
            group(cg, g_)

    # --- lg_face: low card behind, where the tipped face mirrors the camera: the face sliver glows softly and the
    # hole rows (the crown of 8 at the tip) read as dark slits
    el = math.radians(2 * ROLL)
    face = K.strip("FaceCard", (0.0, 1.6 * math.cos(el), 1.6 * math.sin(el)), (3.4, 0.16), FACE_S_W if white else FACE_S * (P_FACE_K if pace else 1.0),
                   (0, 0, 0),
                   color=W6, soft_ends=0.32, soft_w=0.3)
    L.link_only(face, [P["face"], P["neck"]], "recv_face")
    group(face, "lg_face")

    # --- lg_fill: an eye-level ring in front, centred where the tipped band mirrors (el = -2 x ROLL). It wraps from
    # the grip (az -176) to the tip (az +176) with soft ends, so the whole wall + neck read as one continuous band;
    # brightness peaks gently where the KINETIQ etch mirrors
    az0, az1 = -176.0, 176.0
    soft = 25.0 / (az1 - az0)
    pk = (etch_azimuth(M, cam_loc) - az0) / (az1 - az0)

    def fill_s(nb, u, v):
        ends = nb.math("MULTIPLY", nb.smooth(u, 0.0, soft), nb.smooth(u, 1.0, 1.0 - soft))
        rows = nb.math("MULTIPLY", nb.smooth(v, 0.0, 0.25), nb.smooth(v, 1.0, 0.75))
        peak = nb.math("MULTIPLY_ADD", nb.gauss(u, pk, 0.20), 0.52, 0.48)
        return nb.math("MULTIPLY", nb.math("MULTIPLY", nb.math("MULTIPLY", ends, rows), peak),
                       FILL_S * (P_FILL_K if pace else 1.0))

    fill = K.ring_card("Fill", (0.0, 0.0, 0.0), 2.0, az0, az1, -2 * ROLL + FILL_EL[0], -2 * ROLL + FILL_EL[1], fill_s)
    if pace and P_FILL_K != 1.0:   # Pace: the grip keeps Command's ring, the carbon band gets its own strength
        L.link_only(fill, C.objs(P, "grip"), "recv_fill")
        fpk = FILL_S * P_FILL_K

        def fill_p(nb, u, v):
            ends = nb.math("MULTIPLY", nb.smooth(u, 0.0, soft), nb.smooth(u, 1.0, 1.0 - soft))
            rows = nb.math("MULTIPLY", nb.smooth(v, 0.0, 0.25), nb.smooth(v, 1.0, 0.75))
            peak = nb.math("MULTIPLY_ADD", nb.gauss(u, pk, 0.20), 0.52, 0.48)
            return nb.math("MULTIPLY", nb.math("MULTIPLY", nb.math("MULTIPLY", ends, rows), peak), fpk)

        fp = K.ring_card("FillPace", (0.0, 0.0, 0.0), 2.0, az0, az1, -2 * ROLL + FILL_EL[0], -2 * ROLL + FILL_EL[1], fill_p)
        L.link_only(fp, band + C.objs(P, "etchR"), "recv_fillp")
        group(fp, "lg_fill")
    else:
        L.link_only(fill, band + C.objs(P, "grip", "etchR"), "recv_fill")
    group(fill, "lg_fill")

    # --- Pace: the weave card (K08 / K11 / K01): a soft graded card off the wall's mirror direction; the clear coat
    # cannot see it, the 12K's fibre lobes stretched along one tape direction can, so alternate tapes light up
    if pace and P_WEAVE_S > 0:
        import k789_lib as KL789   # Pace only: the Command scene stays exactly as before
        wv = KL789.gradient_card("PaceWeave", P_WEAVE_AT, P_WEAVE_SIZE, P_WEAVE_S, (0.0, 0.0, 0.0),
                                 color=KL789.kelvin(P_WEAVE_K), axis="v", lo=0.0, hi=1.0, floor=0.0)
        L.link_only(wv, band, "recv_weave")
        group(wv, "lg_fill")

    # --- lg_grip: a low soft front card, grip only: the helical wrap and the perforations read across the diameter
    grip_c = M @ Vector((0, (C.GRIP_Y[0] + C.GRIP_Y[1]) / 2, 0))
    gc = K.strip("GripCard", tuple(grip_c + Vector((0.0, -1.1, -0.12))), (1.0, 0.9), GRIP_S, tuple(grip_c),
                 soft_ends=0.4, soft_w=0.4)
    L.link_only(gc, [P["grip"]], "recv_grip")
    group(gc, "lg_grip")

    # --- lg_cap: satin black anodised: a soft white box in the mirror direction of its side band, the groove reads
    cap_c = M @ Vector((0, -0.2905, 0))
    nrm = (M.to_3x3() @ Vector((1, 0, 0))).normalized()   # the cap's side toward camera (model +x = right wall side)
    rr = CT.mirror(cam_loc, cap_c, nrm)
    # a long soft strip (not a small box: that reads as a lit label): a gentle sheen down the cap's side band
    cl = K.strip("CapStrip", tuple(cap_c + rr * 0.45), (0.12, 0.40), CAP_S, tuple(cap_c), soft_ends=0.45, soft_w=0.45)
    L.link_only(cl, C.objs(P, "cap", "capmark"), "recv_cap")
    group(cl, "lg_cap")

    # --- lg_etch: a short grazing strip along the wall from the tip side: the laser frost scatters it
    if not white:
        e_c = M @ Vector((C.WIDTH / 2, C.WALL_ETCH_Y * C.U, 0))
        ed = (M.to_3x3() @ Vector((0.6, 0.75, 0.0))).normalized()
        et = studio.area_light("EtchRake", tuple(e_c + ed * 0.16), 0.06, ETCH_W, color=W6, size_y=0.01, target=tuple(e_c))
        L.link_only(et, [P["etchR"]], "recv_etch")
        group(et, "lg_etch")

    # --- lg_wkey + lg_wtop (white only): real diffuse light. The key is a long soft bar in front, above the camera
    # axis, over the whole length: wall, rim, neck (and their etches) read as one white band; the grip, cap and Q
    # keep their own cards
    if white:
        # bores and the throat stay dark: slits and a dark slot (critic G1: a lit throat read as a bright white slit)
        body = [ob for k, ob in P.items() if k not in ("grip", "cap", "capmark", "holes", "throat", "bridgewall")]
        tot = sum(f_ for _, f_ in WK_SEG)
        for si, (sx, sf) in enumerate(WK_SEG):
            wk = studio.area_light("WhiteKey%d" % si, (sx, WK_AT[1], WK_AT[2]), WK_SIZE[0] / len(WK_SEG), WK_W * sf / tot * len(WK_SEG) / 4,
                                   color=(1.0, 0.985, 0.97), size_y=WK_SIZE[1], target=(sx, 0.0, 0.0))
            L.link_only(wk, body, "recv_wkey%d" % si)
            group(wk, "lg_wkey")
        wh = studio.spot_light("WhiteHot", WH_AT, WH_W, WH_DEG, blend=1.0, color=(1.0, 0.985, 0.97), target=WH_TGT,
                               radius=0.08)
        L.link_only(wh, body, "recv_whot")
        group(wh, "lg_whot")
        wtp = studio.area_light("WhiteTip", WTIP_AT, 0.5, WTIP_W, color=(1.0, 0.985, 0.97), size_y=0.3,
                                target=(0.22, 0.0, 0.0))
        wtp.visible_glossy = False   # diffuse only: no reflected hot spot on the tip's lacquer
        L.link_only(wtp, C.objs(P, "wall", "rim"), "recv_wtip")
        group(wtp, "lg_whot")
        # the satin stripe across the grip's finishing band, at the height of the wall's top hairline: a short strip
        # behind-above whose reflection on the grip's upper flank lands on the band (and eases off onto the wrap)
        bs = K.strip("BandStripe", BAND_AT, BAND_SIZE, BAND_S, (BAND_AT[0], 0.0, 0.0), color=W6,
                     soft_ends=0.45, soft_w=0.35)
        L.link_only(bs, [P["grip"]], "recv_band")
        group(bs, "lg_band")
        wt = studio.area_light("WhiteTop", WT_AT, 1.5, WT_W, color=(0.96, 0.97, 1.0), size_y=0.6, target=(WT_AT[0], 0.0, 0.0))
        L.link_only(wt, C.objs(P, "face"), "recv_wtop")   # not the throat: it stays a dark slot
        group(wt, "lg_wtop")

    if pace:   # Pace keeps Command's grip stripe (only the face follows the feel)
        bs = K.strip("BandStripe", BAND_AT, BAND_SIZE, BAND_S, (BAND_AT[0], 0.0, 0.0), color=W6,
                     soft_ends=0.45, soft_w=0.35)
        L.link_only(bs, [P["grip"]], "recv_band")
        group(bs, "lg_band")

    # --- lg_wall: luminous graphite void (camera only), symmetric so the image stays valid rotated
    wall_y = 2.6
    half_w = (D + wall_y) * 18 / 135
    half_h = half_w * o["h"] / o["w"]
    y_axis = -0.02 * 2 * half_h
    wall = K.plane("Wall", (half_w * 2.6, half_h * 2.6), (0, wall_y, 0), normal_to=(0, -D, 0))
    ec, ee, eb = K.emit_for(VOID_C), K.emit_for(VOID_E), K.emit_for(BAND_D)
    WW, WH = half_w * 2.6, half_h * 2.6

    def wall_s(nb):
        uu, vv, _ = nb.coords("UV")
        x = nb.math("MULTIPLY", nb.math("SUBTRACT", uu, 0.5), WW)
        y = nb.math("MULTIPLY", nb.math("SUBTRACT", vv, 0.5), WH)
        fx = nb.math("DIVIDE", x, half_w)
        fy = nb.math("DIVIDE", y, half_h)
        rr_ = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", fx, fx), nb.math("MULTIPLY", fy, fy)))
        radial = nb.math("POWER", nb.smooth(rr_, 1.45, 0.0), 1.1)
        base = nb.math("MULTIPLY_ADD", radial, ec - ee, ee)
        fyh = nb.math("DIVIDE", nb.math("SUBTRACT", y, y_axis), 2 * half_h)
        bnd = nb.gauss(fyh, 0.0, BAND_SIGMA)
        taper = nb.math("MULTIPLY_ADD", nb.smooth(nb.math("ABSOLUTE", fx), 1.25, 0.2), 0.45, 0.55)
        add = nb.math("MULTIPLY", nb.math("MULTIPLY", bnd, taper), eb - ec)
        return nb.math("ADD", base, nb.math("MAXIMUM", add, 0.0))

    wall.data.materials.append(K.emitter_mat("WallMat", (0.955, 0.960, 1.0), wall_s, additive=False))
    wall.data.materials[0].cycles.emission_sampling = "NONE"
    K.visibility(wall, camera=True, diffuse=False, glossy=False, shadow=False)
    group(wall, "lg_wall")

    # --- camera: 135 mm, level, racket centred at y 52 %
    shift_y = 0.02 * (o["h"] / max(o["w"], o["h"]))
    cam = studio.camera((0, -D, 0), (0, 0, 0), lens=135, shift=(0, shift_y))
    cam.data.sensor_fit = "HORIZONTAL"
    if "lg_swivel" in GROUPS:
        sw_s = SW_P if pace else SW_C

        def sw_fn(nb, u, v):
            ends = nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.3), nb.smooth(u, 1.0, 0.7))
            low = nb.smooth(v, 0.0, 0.12)
            band = nb.math("MULTIPLY_ADD", nb.gauss(v, SW_BAND, SW_BAND_W), 1.0 - SW_FLOOR, SW_FLOOR)
            return nb.math("MULTIPLY", nb.math("MULTIPLY", nb.math("MULTIPLY", ends, low), band), sw_s)

        sw = K.ring_card("SwivelFace", (0.0, 0.0, 0.0), 2.2, 180.0 - SW_AZ, 180.0 + SW_AZ, SW_EL[0], SW_EL[1], sw_fn,
                         color=W6)
        L.link_only(sw, C.objs(P, "face", "neck"), "recv_swivel")
        group(sw, "lg_swivel")
    sc["racket_root"] = root.name
    sc["racket_base"] = json.dumps([list(r) for r in M])
    if SWIVEL:
        swivel(sc, SWIVEL)
    return sc


def etch_azimuth(M, cam_loc):
    """Azimuth (deg from -Y toward +X) where the fill ring is mirrored by the wall at the KINETIQ etch."""
    out = C.outline_canon()
    y_e = C.WALL_ETCH_Y * C.U
    i = min((k for k in range(len(out)) if out[k][0] > 0), key=lambda k: abs(out[k][1] - y_e))
    nr = L._normals(out, 2)[i]
    if nr[0] < 0:
        nr = (-nr[0], -nr[1])
    p = M @ Vector((out[i][0], out[i][1], 0))
    n = (M.to_3x3() @ Vector((nr[0], nr[1], 0))).normalized()
    v = (cam_loc - p).normalized()
    r = 2 * n.dot(v) * n - v
    return math.degrees(math.atan2(r.x, -r.y))


def setup_passes(sc, out_dir, stem):
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    vl.use_pass_object_index = True
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    rl = tr.nodes.new("CompositorNodeRLayers")
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = out_dir
    fo.format.file_format = "OPEN_EXR"
    fo.format.color_mode = "RGB"
    fo.format.color_depth = "32"
    fo.format.exr_codec = "ZIP"
    fo.file_slots.clear()
    for g in GROUPS:
        dn = tr.nodes.new("CompositorNodeDenoise")
        dn.prefilter = "ACCURATE"
        dn.use_hdr = True
        tr.links.new(rl.outputs["Combined_" + g], dn.inputs["Image"])
        tr.links.new(rl.outputs["Denoising Normal"], dn.inputs["Normal"])
        tr.links.new(rl.outputs["Denoising Albedo"], dn.inputs["Albedo"])
        slot = f"{stem}_{g}_"
        fo.file_slots.new(slot)
        tr.links.new(dn.outputs["Image"], fo.inputs[slot])
    slot = f"{stem}_index_"
    fo.file_slots.new(slot)
    tr.links.new(rl.outputs["IndexOB"], fo.inputs[slot])
    comp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(rl.outputs["Image"], comp.inputs["Image"])


def _dirs(o):
    out = os.path.join(studio.OUT, o["out"])
    return os.path.join(os.path.dirname(out), "passes"), os.path.basename(out)


def comp(o, sc=None):
    od, stem = _dirs(o)
    with open(os.path.join(od, stem + "_meta.json")) as fh:
        meta = json.load(fh)
    if sc is None:
        sc = studio.reset()
    gains = dict(GAINS)
    for kv in o["gain"]:
        k, v = kv.split("=")
        gains[k if k.startswith("lg_") else "lg_" + k] = float(v)
    acc = None
    for g in GROUPS:
        p = os.path.join(od, f"{stem}_{g}.exr")
        if gains.get(g) and os.path.exists(p):
            a = L.load_lin(p) * gains[g]
            acc = a if acc is None else acc + a
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    raw = os.path.join(studio.OUT, o["out"] + "__raw.png")
    final = raw.replace("__raw.png", ".png")
    L.save_display(acc, raw, sc)
    ip = os.path.join(od, f"{stem}_index.exr")
    if DETAIL_W and meta.get("white") and os.path.exists(ip):
        idx = L.load_lin(ip)[..., 0]
        px_mm = meta["w"] / (CAM_D * 36 / 135 * 1000)
        sg, g_lo, g_hi, b0, b1 = DETAIL_W
        GD.apply(raw, idx[::-1], sg * px_mm, parts=(1, 3, 5), g_lo=g_lo, g_hi=g_hi, b0=b0, b1=b1)
    ff = None
    if meta.get("crop"):
        x0, x1, y0, y1 = meta["crop"]
        ff = (meta["w"], meta["h"], int(round(x0 * meta["w"])), int(round(y0 * meta["h"])))
    K.finish_png(raw, final, full_frame=ff, bloom=BLOOM_W if meta.get("white") else BLOOM)
    os.remove(raw)
    if o["phone"]:
        from PIL import Image
        Image.open(final).rotate(90, expand=True).save(final.replace(".png", "-phone.png"))
    print("comp", final, flush=True)
    return final


def render_seq(o):
    """The swivel sequence: one build, then per frame: turn, render the light-group passes, comp (as a still), and
    move the frame (and its phone rotation) into place. Frames already on disk are skipped."""
    from PIL import Image
    n = o["seq"]
    a, b = o.get("range") or (0.0, 35.0)
    name = os.path.basename(o["out"])
    base = os.path.join(studio.OUT, os.path.dirname(o["out"]))
    dirs = {"desktop": os.path.join(base, name + "-desktop")}
    if o["phone"]:
        dirs["phone"] = os.path.join(base, name + "-phone")
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    angles = [a + (b - a) * i / max(1, n - 1) for i in range(n)]
    todo = [i for i in range(n) if not all(os.path.exists(os.path.join(d, "f%03d.png" % i)) for d in dirs.values())
            and (not o.get("only") or i in o["only"])]
    print("seq %s: %d frames, %.2f..%.2f deg, %d to render" % (name, n, a, b, len(todo)), flush=True)
    if not todo:
        return
    t0 = time.time()
    sc = build(o)
    print("scene built %.1f s" % (time.time() - t0), flush=True)
    # Every group but the swivel's has gain 1 in the comp, so they render as one pass (lg_rest): 2 denoise passes a
    # frame, not 13 (at 1920 x 1080 the per-group denoise took longer than the render). The light is the same.
    global GROUPS
    sc.view_layers[0].lightgroups.add(name="lg_rest")
    for ob in sc.objects:
        if ob.lightgroup and ob.lightgroup != "lg_swivel":
            ob.lightgroup = "lg_rest"
    GROUPS = ["lg_rest", "lg_swivel"]
    GAINS["lg_rest"] = 1.0
    # One scene sync for the whole sequence: only the racket's transform changes between frames.
    sc.render.use_persistent_data = True
    # --crop x0 x1 y0 y1 (2026-10-29, as k01_lib.render_seq): frame 0 whole, every other frame only that region,
    # pasted into frame 0 with a feathered edge (the region must hold everything that moves, with margin).
    crop = o.get("crop")
    f0 = os.path.join(dirs["desktop"], "f000.png")
    if crop and 0 not in todo and not os.path.exists(f0):
        raise SystemExit("seq --crop: frame 0 must exist or be rendered first")
    work = os.path.join(o["out"] + "_w")
    for i in todo:
        t1 = time.time()
        swivel(sc, angles[i])
        fc = crop if (crop and i > 0) else None
        sc.render.use_border = bool(fc)
        sc.render.use_crop_to_border = bool(fc)
        if fc:
            x0, x1, y0, y1 = fc
            sc.render.border_min_x, sc.render.border_max_x = x0, x1
            sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
        oi = dict(o, out=os.path.join(work, "f%03d" % i), phone=False, crop=fc,
                  gain=list(o["gain"]) + ["swivel=%.4f" % (GAINS["lg_swivel"] * swivel_gain(angles[i]))])
        od, stem = _dirs(oi)
        os.makedirs(od, exist_ok=True)
        setup_passes(sc, od, stem)
        studio.render(os.path.join(work, "passes", stem + "__all"))
        L.collect_passes(od, stem, GROUPS + ["index"])
        with open(os.path.join(od, stem + "_meta.json"), "w") as fh:
            json.dump(dict(w=o["w"], h=o["h"], spp=o["spp"], crop=fc, set=o["set"], white=bool(sc["white"]),
                           swivel=angles[i]), fh)
        final = comp(oi, sc)
        if fc:
            whole = final.replace(".png", "-whole.png")
            K.paste_region(f0, final, fc, whole)
            os.replace(whole, final)
        if "phone" in dirs:
            K.rotate_png(final, os.path.join(dirs["phone"], "f%03d.png" % i))   # 16-bit, as the desktop frame
        os.replace(final, os.path.join(dirs["desktop"], "f%03d.png" % i))
        for f in os.listdir(od):
            if f.startswith(stem + "_") or f.startswith(stem + "__"):
                os.remove(os.path.join(od, f))
        dt = time.time() - t1
        with open(os.path.join(dirs["desktop"], "frames.jsonl"), "a") as fh:
            fh.write(json.dumps(dict(i=i, deg=round(angles[i], 4), sec=round(dt, 1), spp=o["spp"], w=o["w"], h=o["h"],
                                     feel=FEEL)) + "\n")
        print("frame %d %.2f deg %.1f s" % (i, angles[i], dt), flush=True)
    print("seq done %.1f s" % (time.time() - t0), flush=True)


def main():
    o = parse_args(sys.argv[1:], "K02-edge-line")
    if o.get("seq"):
        render_seq(o)
        return
    if o["comp"]:
        comp(o)
        return
    t0 = time.time()
    sc = build(o)
    print("scene built", round(time.time() - t0, 1), "s", flush=True)
    od, stem = _dirs(o)
    os.makedirs(od, exist_ok=True)
    setup_passes(sc, od, stem)
    if o["crop"]:
        x0, x1, y0, y1 = o["crop"]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
    studio.render(os.path.join(os.path.dirname(o["out"]), "passes", os.path.basename(o["out"]) + "__all"))  # sanity: all lights
    L.collect_passes(od, stem, GROUPS + ["index"])
    with open(os.path.join(od, stem + "_meta.json"), "w") as fh:
        json.dump(dict(w=o["w"], h=o["h"], spp=o["spp"], crop=o["crop"], set=o["set"], white=bool(sc["white"])), fh)
    final = comp(o, sc)
    print("rendered", final, round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
