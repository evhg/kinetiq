"""k01_lib: the K01 hero studio (graphite cyclorama, floor beam, finale horizon) around the CANONICAL racket.

Shared by K01-hero-beam.py (desktop 16:9: base / full / finale) and K01-hero-frame.py (phone 9:16: base / full).
The racket is kq_canon's Command (KQ-000427): 455.0 mm, crown of 8 + 34 holes, one-piece neck into the overgrip,
satin black cap with a groove and an engraved Q (the company logo), WHITE 3K twill (k04_tex2 maps, 2.6 mm tows) folding
over the 1.5 mm edge. Nothing of the old k12 racket (flat-bottom joint, collar, silver disc cap, 2.4 mm mat_twill) is
used any more; k12_lib only supplies helpers (node builder, emitters, calibration, post grade) and is not modified.

White carbon is lit by real diffuse light (canon.md, lighting note 8), not by reflections only: a soft spot pool from
the upper left (lg_wkey) whose falloff edge crosses the upper head diagonally, a weak cool fill from the front right
(lg_wfill), and the lacquer's crisp gloss line along the same diagonal (lg_gloss). MAT_OPTS={"white": 0} (--set) gives
back the black Command studio exactly (reflection-only: lg_face sweep, no pool, no fill).

ONE render per framing: every light lives in a Cycles light group, each group is denoised on its own (OIDN with
albedo + normal) and written as a linear EXR; comp() sums the groups with per-variant gains, so base, full and
finale line up pixel for pixel (the page cross-fades base -> full).

Light groups
  lg_cyc      the painted graphite cyclorama (camera-exact grade, display-calibrated)
  lg_face     the face sweep: a projected softbox whose reflection on the face is a designed diagonal: a crisp edge
              crossing the upper head, lit 3K twill trailing below it (black: black gloss elsewhere; white: the
              fibre sheen flips inside it)
  lg_wkey     white only: the soft spot pool from the upper left (white face at about luma 205 upper left, the
              falloff edge crossing the upper head diagonally, the shade side still white with its twill in tone)
  lg_wfill    white only: a weak cool fill from the front right (the shade side stays white in shadow, not grey)
  lg_gloss    a 1.4 mm gloss line along the sweep's edge (the lacquer)
  lg_top      overhead card (top curve highlight), white hairline on the upper-left edge, right-wall sliver
  lg_rim      ember hairline on the right edge, shoulder to throat
  lg_lip      grazing card on the 42 hole lips (crescents: moulded through-holes)
  lg_floor    soft overhead wash around the base (floor only)
  lg_grip     two strips on the neck, overgrip and cap
  lg_cap      a softbox in the mirror direction of the cap's front band: its groove and the engraved Q
  lg_key      the floor beam (collimated slit light + gobo) and its haze; also lights the cap and Q
  lg_horizon  finale: warm first light up the cove (camera-only overlay) and a warm rim on the head's left edge

Usage (from the blender dir, always through the lock):
  flock render.lock ../bpyenv/bin/python shots/K01-hero-beam.py --w 960 --h 540 --spp 32 --out k01v2/beam_p01
  -> out/k01v2/beam_p01-base.png, -full.png, -finale.png (+ passes in out/k01v2/passes/)
  ../bpyenv/bin/python shots/k01_lib.py comp beam k01v2/beam_p01 [--gain full.face=1.2 ...] (re-comp, no render)
Dev: --set NAME=value overrides any constant below; --crop x0 x1 y0 y1 renders a region at full resolution.
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
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import studio  # noqa: E402
import k12_lib as K  # noqa: E402
import k10_lib as L  # noqa: E402
import kq_canon as C  # noqa: E402
import canon_test as CT  # noqa: E402
import g1_detail as GD  # noqa: E402

# ------------------------------------------------------------------ constants (override with --set NAME=value)
YAW = 12.0              # face turned toward camera-left
CAM_H = 0.40            # camera height (m); level camera, lens shift only
Z_TOP = C.TIP_Y - C.BUTT_Y  # 0.455: the racket stands on its butt cap (hidden pin)
SEAM_K = (0.72 - 0.27) / (0.81 - 0.27)  # cove seam crosses mid-grip (approved: 0.72 in a 0.27-0.81 span)
COVE_R = 0.35
WALL_D, LIFT_D, HALO_D, FLOOR_D = 20, 33, 46, 24   # studio paint, display luma (k12 calibration)
# face sweep (model face coordinates, metres): the edge line runs from SW_A (left edge) to SW_B (top right)
SW_A = (-0.140, 0.000)
SW_B = (0.075, 0.170)
SW_RISE = 0.0012        # the softbox edge: crisp
SW_FALL = 0.11          # lit twill trails this far below-right of the edge
SW_POW = 1.6
SW_FLOOR = 0.0
FACE_S = 3.0            # sweep radiance (full)
SW_DIST, SW_SIZE = 0.22, 2.2   # the sweep panel sits close to the face: the rough twill base then shows a band
                               # (a far panel is blurred by the base's +-20 deg lobe into a flat grey wash)
GLOSS_S = 6.0           # gloss line radiance
GLOSS_OFF, GLOSS_W = 0.0045, 0.0007   # gloss line: offset from the edge, half width
TOP_S = 22.0
WHITE_S = 22.0          # white hairline, upper-left edge
EMBER_S = 72.0          # ember hairline, right edge
SIDE_S = 3.2
# right-wall card: a broad soft card (not a narrow strip: under the fibres' anisotropy a narrow strip draws streaks along
# the wall that read as brushed aluminium, critic G1); white: the wall reads as the same twill under an even satin
# sheen, one step darker than the face (about luma 150-170)
SIDE_SIZE, SIDE_DIST = (0.20, 0.60), 0.55
SIDE_SIZE_W, SIDE_DIST_W, SIDE_S_W = (0.90, 1.10), 0.70, 0.9
# comp: the weave's detail-preserving grade (g1_detail.py) on the carbon parts of white Command: (sigma in mm on the
# racket, gain in the shade, gain in the light, display luma where the gain starts / tops out). None = off.
DETAIL_W = (2.0, 1.15, 3.8, 0.55, 0.85)
EMBER_NEUTRAL = ("base", "full")   # comp: the ember hairline is desaturated (a neutral edge line) in these variants;
                                   # on white it read as a salmon chromatic fringe. Only the finale keeps it warm.
LIP_W = 14.0
POOL_W = 80.0
POOL_ANG = 46.0
GRIP_W, GRIP2_W = 1.0, 0.25
CAP_W = 0.30
KEY_W = 135.0
KEY_CAP = 0.30          # the beam on the satin cap and its Q, relative to KEY_W (full strength reads grey)
BEAM_AZ = -108.0
BEAM_W = 0.30
BEAM_PAST = 0.55
HAZE = 0.07
HOR_RIM_W = 26.0
HOR_D = 128
# the weave on white (critic G1: at 2560 the twill's high-pass std was 3-4 luma, invisible at 960): a stronger tone
# step between the two tow directions, more of the baked tow-to-tow tone and crevice, deeper tow relief and a stronger
# fibre sheen, so the twill reads in the shade and alternates through the key's terminator. kq_canon COMMAND_WHITE keys.
WEAVE_W = dict(dir_tone=0.26, alb_k=0.80, bump=0.45, aniso=0.85)
MAT_OPTS = dict(WEAVE_W)  # kq_canon mat_opts; {"white": 0} = the previous black Command (and its studio)
# white Command (model space: face +Z toward the camera, head up +Y; the racket's pose carries the lights)
# lg_wkey: a spot whose cone edge lies on the sweep line SW_A -> SW_B (the same diagonal as the gloss line): the circle
# of radius WK_EDGE_R on the face is centred WK_EDGE_R up-left of the line's midpoint, so its edge crosses the upper
# head as a gently curved diagonal, softened over WK_BLEND of the cone
WK_W = 1000.0           # spot pool energy (W): the lit upper-left third at luma 220-232 (critic G1)
WK_EDGE_R = 0.30        # cone radius on the face (m)
WK_BLEND = 0.15         # a tight penumbra: the diagonal light/dark transition spans about 15-20 % of the head
WK_DIR = (-0.50, 0.45, 0.75)   # from the face toward the lamp: upper left, in front
WK_DIST = 1.10
WK_R = 0.02            # the lamp radius sets the penumbra: 0.02 m -> the diagonal transition about 17 % of the head (0.05 gave 34 %)
WK_IN = 0.0             # move the edge into (+) / out of (-) the lit side along the line normal (m)
# lg_wfill: the broad soft light that keeps the shade side white in shadow (about luma 140), from the front, a touch
# right and high
WF_W = 9.5              # the shade side (lower right) at about luma 125-135: white in shadow, a real light/dark split
WF_AT = (0.45, 0.25, 1.30)
WF_SIZE = 1.2
GLOSS_S_W = 40.0        # on white the lacquer shows as a soft reflection band along the pool edge (a 1.4 mm line over
GLOSS_W_W = 0.010       # white reads as a scratch): half width 10 mm, centred on the edge
GLOSS_OFF_W = 0.0
FACE_S_W = 3.0          # the sweep on white lights the fibre sheen only (glossy rays)
BLOOM = (0.55, 0.22, 0.012)     # threshold (display luma), amount, radius (frame-height fraction)
BLOOM_W = (0.90, 0.10, 0.006)   # white face: only true glints bloom (a white plate under a 0.55 bloom glows like CG)
CYC_VIS = (True, True)  # the cyc seen by (diffuse, glossy) rays
# ------------------------------------------------------------------ Pace (Release 2 feel toggle, 2026-10-23)
# --feel pace builds the canon Pace (kq_canon.PACE v6: black 12K, 8 mm tapes) in the same studio, camera, beam and comp.
# Black carbon takes the reflection-only studio (lg_face sweep + lg_gloss line, no pool / fill, no white-weave grade),
# plus K08 / K11's Pace recipe: a dim band (P_FACE_S) and an off-specular weave card only the fibre lobes can see
# (P_WEAVE_*: one tape direction catches it, so the 12K reads as tapes, not a black hole). No ember on any racket: the
# right-edge hairline is Command's neutral 6500 K at a quarter of the ember's power (P_RIM_S, K08 RIM_PACE). Default
# FEEL "command" leaves every Command output byte-identical.
FEEL = "command"
P_FACE_S = 3.0          # Pace sweep radiance (FACE_S is black Command's)
P_GLOSS_S = 6.0         # Pace gloss line radiance
P_WEAVE_S = 7.0         # Pace weave card (K08: 5 at 1.1 x 0.62 m); 0 = off. Tuned on 1:1 crops (out/k01pace/):
                        # 15 at 18 deg / 1.1 m lit only the upper-left tapes; 10 at 12 deg or a 0.3 floor greyed the face
P_WEAVE_UP = 18.0       # the card sits this far (deg) above the face's mirror direction (K08 WEAVE_UP)
P_WEAVE_D, P_WEAVE_SIZE = 1.4, (2.2, 1.2)   # big enough to put tapes over the lower head, under the sweep
P_WEAVE_K = 6500.0      # neutral (K08's 5800 K read brown on the 12K here)
P_WEAVE_FLOOR = 0.0
P_RIM_S = 18.0          # neutral right-edge hairline (EMBER_S 72 / 4)
P_LIP_K = 1.0           # Pace: multiplier on the hole-lip card
P_TOP_K = 1.0           # Pace: multiplier on the white hairline and top card
P_SIDE_K = 1.0          # Pace: multiplier on the right-wall card
P_CLAMP = 4.0           # Pace: indirect clamp (K08 CLAMP_IND, fireflies on the 12K face); 0 = off
GLOSSY_FLOOR = 0.15     # the floor's albedo as seen by glossy rays (see mat_studio)
# ------------------------------------------------------------------ swivel (Release 3 hero scrub, 2026-10-23)
# --yaw DEG turns the racket about its handle axis (world Z through the handle; the cap stays on its floor mark) by
# DEG on top of YAW, AFTER the studio is built: every light, card and the beam stay fixed in the world, so the light
# sweeps across the face as it turns. + = the face turns further toward camera-left (the right side wall and the
# one-piece neck come round). 0 (the default) changes nothing: the stills render exactly as before.
# --seq N --yaw-range A B renders N frames (yaw A..B, linear) of the lit "full" look from ONE scene build into
# out/<--out>/f000.png ..; frames already on disk are skipped (resume). See render_seq().
SWIVEL = 0.0
SWIVEL_SIGN = 1.0       # +1: the swivel continues YAW's turn (face toward camera-left)

EMBER = K.hex_lin("#ff3a1e")
WHITE = (0.95, 0.97, 1.0)
GROUPS = ["lg_cyc", "lg_face", "lg_gloss", "lg_top", "lg_side", "lg_rim", "lg_lip", "lg_floor", "lg_grip", "lg_cap", "lg_key",
          "lg_horizon", "lg_wkey", "lg_wfill"]
VARIANTS = {
    "base": dict(lg_cyc=1, lg_face=0.35, lg_gloss=0.35, lg_top=1, lg_side=1, lg_rim=1, lg_lip=1, lg_floor=1, lg_grip=1,
                 lg_cap=0.35, lg_key=0, lg_horizon=0, lg_wkey=0.38, lg_wfill=1.0),   # white: full's face about 10-12 % darker
    "full": dict(lg_cyc=1, lg_face=1, lg_gloss=1, lg_top=1, lg_side=1, lg_rim=1, lg_lip=1, lg_floor=1, lg_grip=1, lg_cap=1,
                 lg_key=1, lg_horizon=0, lg_wkey=1, lg_wfill=1),
    "finale": dict(lg_cyc=1, lg_face=1, lg_gloss=1, lg_top=1, lg_side=1, lg_rim=1, lg_lip=1, lg_floor=1, lg_grip=1, lg_cap=1,
                   lg_key=1, lg_horizon=1, lg_wkey=1, lg_wfill=1),
}


# ------------------------------------------------------------------ args
def parse_args(argv, default_out):
    o = {"w": 960, "h": 540, "spp": 32, "out": default_out, "crop": None, "set": [], "gain": [], "variants": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--w", "--h", "--spp"):
            o[a[2:]] = int(argv[i + 1]); i += 2
        elif a == "--out":
            o["out"] = argv[i + 1]; i += 2
        elif a == "--crop":
            o["crop"] = [float(v) for v in argv[i + 1:i + 5]]; i += 5
        elif a == "--set":
            o["set"].append(argv[i + 1]); i += 2
        elif a == "--gain":
            o["gain"].append(argv[i + 1]); i += 2
        elif a == "--feel":
            o["feel"] = argv[i + 1]; i += 2
        elif a == "--variants":
            o["variants"] = argv[i + 1].split(","); i += 2
        elif a == "--yaw":
            o["yaw"] = float(argv[i + 1]); i += 2
        elif a == "--seq":
            o["seq"] = int(argv[i + 1]); i += 2
        elif a == "--only":
            o["only"] = [int(v) for v in argv[i + 1].split(",")]; i += 2
        elif a == "--yaw-range":
            o["yaw_range"] = (float(argv[i + 1]), float(argv[i + 2])); i += 3
        else:
            i += 1
    g = globals()
    if o.get("feel"):
        assert o["feel"] in ("command", "pace"), o["feel"]
        g["FEEL"] = o["feel"]
        print("feel", FEEL, flush=True)
    if o.get("yaw") is not None:
        g["SWIVEL"] = o["yaw"]
        print("swivel", SWIVEL, flush=True)
    for kv in o["set"]:
        k, v = kv.split("=", 1)
        assert k in g, k
        g[k] = eval(v)
        print("set", k, "=", g[k], flush=True)
    return o


# ------------------------------------------------------------------ framing
def framing(o, mode):
    """mode 'beam': the approved desktop camera (85 mm; the racket spans 27-81 % of the frame height).
    mode 'phone': K01-hero-frame's portrait camera (4.20 m, head top at 51 %, cap at 81 %; lens from the aspect)."""
    if mode == "beam":
        span, lens = (0.27, 0.81), 85.0
        pool_ang = POOL_ANG
    else:
        span = (0.51, 0.81) if o["h"] > o["w"] else (0.49, 0.84)
        two_ht0 = Z_TOP / ((span[1] - span[0]) * 4.20)
        lens = (o["h"] / o["w"]) * 36.0 / two_ht0
        pool_ang = 66.0
    two_ht = (o["h"] / o["w"]) * 36 / lens
    D = Z_TOP / ((span[1] - span[0]) * two_ht)
    t_bot = -CAM_H / D
    t_c = t_bot + (span[1] - 0.5) * two_ht
    shift_y = t_c / (36 / lens)
    seam = span[0] + SEAM_K * (span[1] - span[0])
    return dict(span=span, lens=lens, D=D, t_c=t_c, two_ht=two_ht, shift_y=shift_y, seam=seam, pool_ang=pool_ang)


# ------------------------------------------------------------------ studio
def mat_studio(o, F, seam_y_world):
    """k12's cyclorama (concrete + camera-exact painted graphite grade), unchanged; the finale glow is an overlay."""
    D, t_c, two_ht, span = F["D"], F["t_c"], F["two_ht"], F["span"]
    m = K.new_mat("Studio")
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    tc = nb.n.new("ShaderNodeTexCoord")
    big = nb.n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 7.0; big.inputs["Detail"].default_value = 6
    fine = nb.n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 380; fine.inputs["Detail"].default_value = 4
    grit = nb.n.new("ShaderNodeTexVoronoi"); grit.inputs["Scale"].default_value = 240
    for t in (big, fine, grit):
        nb.l.new(tc.outputs["Object"], t.inputs["Vector"])
    mott = nb.smooth(big.outputs["Fac"], 0.30, 0.70)
    grain = nb.smooth(fine.outputs["Fac"], 0.30, 0.70)
    pores = nb.smooth(grit.outputs["Distance"], 0.04, 0.13)
    v = nb.math("MULTIPLY_ADD", mott, 0.40, 0.76)
    v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", grain, 0.40, 0.78))
    v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", pores, 0.50, 0.50))
    nb.l.new(nb.gray(nb.math("MULTIPLY", v, 0.060)), b.inputs["Base Color"])
    nb.l.new(nb.math("MULTIPLY_ADD", nb.math("MULTIPLY", grain, mott), 0.30, 0.38), b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.5
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.0006
    nb.l.new(nb.math("ADD", grain, nb.math("MULTIPLY", pores, 0.8)), bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    x, y, z = nb.coords("Object")
    e_wall, e_lift, e_halo, e_floor = (K.emit_for(d) for d in (WALL_D, LIFT_D, HALO_D, FLOOR_D))
    fz = nb.smooth(z, 0.02, COVE_R * 0.9)
    fx, fy = _frame_xy(nb, x, y, z, o, F)
    dxl = nb.math("SUBTRACT", fx, 0.42); dyl = nb.math("SUBTRACT", fy, 0.42)
    rl = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", dxl, dxl), nb.math("MULTIPLY", nb.math("MULTIPLY", dyl, dyl), 1.6)))
    lift = nb.math("POWER", nb.smooth(rl, 0.95, 0.0), 1.3)
    wall = nb.math("MULTIPLY_ADD", lift, e_lift - e_wall, e_wall)
    head_fy = 0.5 - (span[0] + (span[1] - span[0]) * 0.30)
    dxh = nb.math("DIVIDE", fx, 0.30); dyh = nb.math("DIVIDE", nb.math("SUBTRACT", fy, head_fy), 0.36)
    rh = nb.math("ADD", nb.math("MULTIPLY", dxh, dxh), nb.math("MULTIPLY", dyh, dyh))
    halo = nb.math("MULTIPLY", nb.math("EXPONENT", nb.math("MULTIPLY", rh, -1.6)), e_halo - e_wall)
    wall = nb.math("ADD", wall, nb.math("MULTIPLY", halo, nb.smooth(fz, 0.0, 1.0)))
    floor_e = nb.math("MULTIPLY_ADD", nb.smooth(y, -1.2, seam_y_world), e_floor * 0.12, e_floor * 0.94)
    e = nb.lerp(fz, floor_e, wall)
    b.inputs["Emission Color"].default_value = (0.955, 0.960, 1.0, 1)
    nb.l.new(e, b.inputs["Emission Strength"])
    # glossy rays see the painted grade over a dim matte floor: the beam on the concrete (and its grazing specular
    # glint) must not wash the face's metallic twill grey through its broad anisotropic lobe. Camera rays and
    # diffuse bounces see the real concrete.
    gd = nb.n.new("ShaderNodeBsdfDiffuse")
    nb.l.new(nb.gray(nb.math("MULTIPLY", v, 0.060 * GLOSSY_FLOOR)), gd.inputs["Color"])
    ge = nb.n.new("ShaderNodeEmission")
    ge.inputs["Color"].default_value = (0.955, 0.960, 1.0, 1)
    nb.l.new(e, ge.inputs["Strength"])
    ga = nb.n.new("ShaderNodeAddShader")
    nb.l.new(gd.outputs[0], ga.inputs[0]); nb.l.new(ge.outputs[0], ga.inputs[1])
    lpg = nb.n.new("ShaderNodeLightPath")
    mx = nb.n.new("ShaderNodeMixShader")
    nb.l.new(lpg.outputs["Is Glossy Ray"], mx.inputs[0])
    nb.l.new(b.outputs[0], mx.inputs[1]); nb.l.new(ga.outputs[0], mx.inputs[2])
    out.inputs["Surface"].links and nb.l.remove(out.inputs["Surface"].links[0])
    nb.l.new(mx.outputs[0], out.inputs["Surface"])
    m.cycles.emission_sampling = "NONE"
    return m


def _frame_xy(nb, x, y, z, o, F):
    """Frame coordinates of a world point (object coords of the cyc = world): fx -0.5..0.5, fy -0.5 (bottom)..0.5."""
    Yw = nb.math("ADD", y, F["D"])
    tx = nb.math("DIVIDE", x, Yw)
    ty = nb.math("DIVIDE", nb.math("SUBTRACT", z, CAM_H), Yw)
    two_wt = F["two_ht"] * o["w"] / o["h"]
    fx = nb.math("DIVIDE", tx, two_wt)
    fy = nb.math("DIVIDE", nb.math("SUBTRACT", ty, F["t_c"]), F["two_ht"])
    return fx, fy


def mat_horizon(o, F):
    """Finale first light (k12's painted glow): warm, brightest on the seam, rising ~15 % of the frame height up the
    wall and ~5 % onto the floor, ~30 % at the frame sides. Camera rays only, over transparency (an overlay)."""
    m = K.new_mat("Horizon")
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    x, y, z = nb.coords("Object")
    fx, fy = _frame_xy(nb, x, y, z, o, F)
    SEAM_Y = F["seam"]
    d_up = nb.math("DIVIDE", nb.math("MAXIMUM", nb.math("SUBTRACT", fy, (0.5 - SEAM_Y)), 0.0), 0.15)
    d_dn = nb.math("DIVIDE", nb.math("MAXIMUM", nb.math("SUBTRACT", (0.5 - SEAM_Y), fy), 0.0), 0.05)
    down = nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", d_dn, d_dn), -2.5))
    vert = nb.math("EXPONENT", nb.math("MULTIPLY", d_up, -2.6))
    side = nb.math("MULTIPLY_ADD", nb.math("POWER", nb.smooth(nb.math("ABSOLUTE", fx), 0.55, 0.0), 1.2), 0.70, 0.30)
    hot = nb.math("MULTIPLY", nb.math("EXPONENT", nb.math("MULTIPLY", d_up, -14.0)), 0.6)
    g = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.math("ADD", vert, hot), down), side)
    warm = nb.n.new("ShaderNodeEmission")
    warm.inputs["Color"].default_value = (*K.hex_lin("#ff9a4a"), 1)
    lp = nb.n.new("ShaderNodeLightPath")
    nb.l.new(nb.math("MULTIPLY", nb.math("MULTIPLY", g, K.emit_for(HOR_D)), lp.outputs["Is Camera Ray"]),
             warm.inputs["Strength"])
    tr = nb.n.new("ShaderNodeBsdfTransparent")
    add = nb.n.new("ShaderNodeAddShader")
    nb.l.new(warm.outputs[0], add.inputs[0]); nb.l.new(tr.outputs[0], add.inputs[1])
    nb.l.new(add.outputs[0], out.inputs["Surface"])
    m.cycles.emission_sampling = "NONE"
    return m


def cyclorama(name, seam_y, radius, half_x=8.0, near_y=-6.0, top=4.0, inset=0.0):
    """Floor, cove (starting at y = seam_y) and back wall as one smooth mesh; inset moves it into the studio."""
    prof = [(near_y, inset)]
    n = 24
    for k in range(n + 1):
        t = k / n * math.pi / 2
        r = radius - inset
        prof.append((seam_y + r * math.sin(t), inset + r - r * math.cos(t)))
    prof.append((seam_y + radius - inset, top))
    bm = bmesh.new()
    rows = [[bm.verts.new((xx, yy, zz)) for xx in (-half_x, half_x)] for (yy, zz) in prof]
    for a, b in zip(rows[:-1], rows[1:]):
        bm.faces.new((a[0], a[1], b[1], b[0]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if me.polygons[0].normal.z < 0:
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
    return ob


def beam_haze(name, mid, u, Lb, W, el, strength):
    """Thin additive glow hugging the floor stripe (k12's)."""
    H = 0.7
    ob = K.plane(name, (Lb + 1.2, H), (0, 0, 0))
    x = u.normalized(); y = Vector((0, 0, 1)); z = x.cross(y)
    c = mid + y * (H / 2) - x * 0.6
    ob.matrix_world = Matrix(((x.x, y.x, z.x, c.x), (x.y, y.y, z.y, c.y), (x.z, y.z, z.z, c.z), (0, 0, 0, 1)))
    k = 1.0 / math.tan(el)

    def s(nb):
        uu, vv, _ = nb.coords("UV")
        along = nb.math("MULTIPLY", uu, Lb + 1.2)
        hgt = nb.math("MULTIPLY", vv, H)
        a = nb.math("SUBTRACT", nb.math("ADD", along, nb.math("MULTIPLY", hgt, k)), 1.2)
        inside = nb.math("MULTIPLY", nb.math("POWER", nb.smooth(a, 0.1, Lb * 0.62), 1.3), nb.smooth(a, Lb, Lb - BEAM_PAST - 0.05))
        fall = nb.math("EXPONENT", nb.math("MULTIPLY", hgt, -9.0))
        return nb.math("MULTIPLY", nb.math("MULTIPLY", inside, fall), strength)

    ob.data.materials.append(K.emitter_mat(name + "Mat", K.kelvin(5600), s, additive=True))
    K.visibility(ob, camera=True, diffuse=False, glossy=False, shadow=False)
    return ob


# ------------------------------------------------------------------ racket-relative emitters (built in model space)
def proj_sweep(name, cam_m, a, b, centre, size, dist, strength, profile, color=WHITE):
    """A softbox whose reflection in the FRONT face (model plane z = ZT) is a designed 2D field: each panel point is
    projected from the mirrored camera onto the face plane, and its emission is profile(nb, sd) of that point's
    signed distance sd from the face line a -> b (metres; positive to the right of a -> b). Built in model space;
    the shader reads object coordinates through the panel's model transform, so it survives the racket's pose."""
    ZT = C.ZT
    cm = Vector((cam_m.x, cam_m.y, 2 * ZT - cam_m.z))
    Cc = Vector(centre)
    d = (Cc - cam_m).normalized()
    r = (d - 2 * d.dot(Vector((0, 0, 1))) * Vector((0, 0, 1))).normalized()
    ob = K.plane(name, size, tuple(Cc + r * dist), normal_to=tuple(Cc))
    loc0, rot0 = ob.location.copy(), ob.rotation_euler.copy()
    A, B = Vector(a), Vector(b)
    ab = B - A
    ln = ab.length
    ax, ay, bx, by = A.x, A.y, ab.x / ln, ab.y / ln

    def s(nb):
        tc = nb.n.new("ShaderNodeTexCoord")
        mp = nb.n.new("ShaderNodeMapping")
        mp.vector_type = "POINT"
        mp.inputs["Location"].default_value = tuple(loc0)
        mp.inputs["Rotation"].default_value = tuple(rot0)
        nb.l.new(tc.outputs["Object"], mp.inputs["Vector"])
        sep = nb.n.new("ShaderNodeSeparateXYZ")
        nb.l.new(mp.outputs["Vector"], sep.inputs["Vector"])
        X, Y, Z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
        t = nb.math("DIVIDE", ZT - cm.z, nb.math("SUBTRACT", Z, cm.z))
        px = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", X, cm.x), t, cm.x)
        py = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", Y, cm.y), t, cm.y)
        sd = nb.math("SUBTRACT", nb.math("MULTIPLY", nb.math("SUBTRACT", px, ax), by),
                     nb.math("MULTIPLY", nb.math("SUBTRACT", py, ay), bx))
        return nb.math("MULTIPLY", profile(nb, sd), strength)

    ob.data.materials.append(K.emitter_mat(name + "Mat", color, s, additive=True))
    K.visibility(ob, camera=False, diffuse=False, glossy=True, shadow=False)
    return ob


def sweep_profile(nb, sd):
    """Crisp edge at sd = 0, lit twill trailing over SW_FALL to the lower right, black gloss elsewhere."""
    rise = nb.smooth(sd, -SW_RISE, SW_RISE * 0.3)
    fall = nb.math("POWER", nb.smooth(sd, SW_FALL, 0.0), SW_POW)
    g = nb.math("MULTIPLY", rise, fall)
    return nb.math("MULTIPLY_ADD", g, 1 - SW_FLOOR, SW_FLOOR) if SW_FLOOR else g


def gloss_profile(nb, sd):
    return nb.smooth(nb.math("ABSOLUTE", nb.math("SUBTRACT", sd, GLOSS_OFF)), GLOSS_W, 0.0)


def gloss_profile_w(nb, sd):
    t = nb.smooth(nb.math("ABSOLUTE", nb.math("SUBTRACT", sd, GLOSS_OFF_W)), GLOSS_W_W, 0.0)
    return nb.math("MULTIPLY", t, t)


def sm(x, e0, e1):
    return CT.sm(x, e0, e1)


# ------------------------------------------------------------------ the scene
def build(o, mode):
    F = framing(o, mode)
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.light_sampling_threshold = 0.0
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 1
    sc.cycles.glossy_bounces = 4
    sc.cycles.transparent_max_bounces = 10
    sc.cycles.blur_glossy = 0.5
    vl = sc.view_layers[0]
    for g in GROUPS:
        vl.lightgroups.add(name=g)

    def group(ob, g):
        ob.lightgroup = g
        return ob

    D, t_c, two_ht = F["D"], F["t_c"], F["two_ht"]
    t_seam = t_c - (F["seam"] - 0.5) * two_ht
    seam_world = CAM_H / -t_seam - D
    cam_loc = Vector((0, -D, CAM_H))

    # --- the canonical racket, Command, standing on its butt cap (hidden pin), face turned 12 deg to camera-left
    t0 = time.time()
    pace = FEEL == "pace"
    white = (not pace) and C.is_white("command", MAT_OPTS)
    loc0 = (0.0, 0.0, -C.BUTT_Y + 0.0003)
    # the engraved Q turns round the handle axis to face this camera (the yawed racket shows it 12 deg off otherwise)
    M0 = (Matrix.Translation(loc0) @ Matrix.Rotation(math.radians(-YAW), 4, "Z") @ Matrix.Rotation(math.radians(90.0), 4, "X"))
    dq = M0.inverted() @ cam_loc - Vector((0.0, -0.2925, 0.0))
    mark_az = math.degrees(math.atan2(dq.x, dq.z))
    root, P = C.build_racket("KQ", feel=FEEL, serial=C.SERIAL, mat_opts=None if pace else MAT_OPTS, mark_az=mark_az)
    if pace and P_CLAMP:
        sc.cycles.sample_clamp_indirect = P_CLAMP
    C.pose(root, loc0, yaw_deg=-YAW, tilt_deg=90.0)
    print("cap mark turned %.1f deg to face the camera" % mark_az, flush=True)
    bpy.context.view_layer.update()
    print("racket built %.1f s" % (time.time() - t0), flush=True)
    M = root.matrix_world.copy()
    Mi = M.inverted()
    cam_m = Mi @ cam_loc
    P["face"].pass_index = 1
    P["holes"].pass_index = 2
    for k_, i_ in (("wall", 3), ("rim", 4), ("neck", 5), ("cap", 6), ("capmark", 7), ("grip", 8), ("throat", 9),
                   ("bridgewall", 9)):
        if k_ in P:
            P[k_].pass_index = i_

    def place(ob):
        # matrix_basis, not matrix_world: a freshly set location / rotation is not in matrix_world until a depsgraph
        # update, and a stale identity would drop the emitter onto the racket centre
        ob.matrix_world = M @ ob.matrix_basis
        return ob

    # --- studio
    cyc = cyclorama("Cyc", seam_world, COVE_R)
    cyc.data.materials.append(mat_studio(o, F, seam_world))
    K.visibility(cyc, camera=True, diffuse=CYC_VIS[0], glossy=CYC_VIS[1], shadow=True)
    group(cyc, "lg_cyc")
    hz = cyclorama("HorizonGlow", seam_world, COVE_R, inset=0.002)
    hz.data.materials.append(mat_horizon(o, F))
    K.visibility(hz, camera=True, diffuse=False, glossy=False, shadow=False)
    group(hz, "lg_horizon")
    centre = M @ Vector((0, 0, 0))

    # --- lg_face + lg_gloss: the sweep across the upper head
    fc = (-0.02, 0.05, C.ZT)
    sw = proj_sweep("FaceSweep", cam_m, SW_A, SW_B, fc, (SW_SIZE, SW_SIZE), SW_DIST,
                    P_FACE_S if pace else (FACE_S_W if white else FACE_S), sweep_profile)
    L.link_only(place(sw), C.objs(P, "face", "holes", "rim", "throat", "bridgewall"), "recv_face")
    group(sw, "lg_face")
    gl = proj_sweep("FaceGloss", cam_m, SW_A, SW_B, fc, (SW_SIZE * 1.1, SW_SIZE * 1.1), SW_DIST * 1.1,
                    P_GLOSS_S if pace else (GLOSS_S_W if white else GLOSS_S), gloss_profile_w if white else gloss_profile)
    L.link_only(place(gl), [P["face"]], "recv_gloss")
    group(gl, "lg_gloss")

    # --- Pace: the weave card (K08 / K11): a soft graded card above the face's mirror direction; the clear coat cannot
    # see it, the 12K's fibre lobes stretched along one tape direction can, so alternate tapes light up
    if pace and P_WEAVE_S > 0:
        import k789_lib as KL789   # Pace only: the Command scene stays exactly as before
        n_w = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
        c_w = M @ Vector((0.0, 0.03, C.ZT))
        v_w = (cam_loc - c_w).normalized()
        d_w = (2 * n_w.dot(v_w) * n_w - v_w).normalized()
        hz_w = Vector((-d_w.y, d_w.x, 0)).normalized()
        d_up = (Matrix.Rotation(math.radians(P_WEAVE_UP), 3, hz_w) @ d_w).normalized()
        if d_up.z < d_w.z:
            d_up = (Matrix.Rotation(math.radians(-P_WEAVE_UP), 3, hz_w) @ d_w).normalized()
        wv = KL789.gradient_card("PaceWeave", tuple(c_w + d_up * P_WEAVE_D), P_WEAVE_SIZE, P_WEAVE_S, tuple(c_w),
                                 color=KL789.kelvin(P_WEAVE_K), axis="v", lo=0.0, hi=1.0, floor=P_WEAVE_FLOOR)
        L.link_only(wv, C.objs(P, "face", "back", "wall", "neck"), "recv_weave")
        group(wv, "lg_face")

    # --- lg_wkey + lg_wfill (white Command only): real diffuse light on the head parts (grip, cap and Q keep their
    # own strips, so the grip stays black and the cap satin)
    if white:
        head = [ob for k, ob in P.items() if k not in ("grip", "cap", "capmark")]
        A_, B_ = Vector((*SW_A, 0.0)), Vector((*SW_B, 0.0))
        t_ = (B_ - A_).normalized()
        n_ = Vector((-t_.y, t_.x, 0.0))          # the line's normal toward the upper left (the lit side)
        c_ = (A_ + B_) / 2 + n_ * (WK_EDGE_R - WK_IN)
        c_.z = C.ZT
        d_ = Vector(WK_DIR).normalized()
        at_ = c_ + d_ * WK_DIST
        # the cone's half-intensity angle is the angle to the line's midpoint (an oblique cone stretches toward its far
        # side, so the axis-hit radius alone would put the edge far too low)
        e_ = (A_ + B_) / 2 - n_ * WK_IN
        e_.z = C.ZT
        half = (e_ - at_).angle(c_ - at_)
        pk = studio.spot_light("WhitePool", tuple(at_), WK_W, 2 * math.degrees(half) / (1 - WK_BLEND / 4),
                               blend=WK_BLEND, color=(1.0, 0.985, 0.97), target=tuple(c_), radius=WK_R)
        L.link_only(place(pk), head, "recv_wkey")
        group(pk, "lg_wkey")
        fl = studio.area_light("WhiteFill", WF_AT, WF_SIZE, WF_W, color=(0.94, 0.96, 1.0), target=(0.0, -0.03, 0.0))
        L.link_only(place(fl), head, "recv_wfill")
        group(fl, "lg_wfill")

    # --- lg_top: overhead card behind (top curve, wall top run, handle tops), white hairline upper-left edge,
    # right-wall sliver card in the wall's mirror direction
    top = K.strip("Top", (0.0, 0.80, 0.92), (3.0, 1.4), TOP_S * (P_TOP_K if pace else 1.0), (0, 0.0, 0.46),
                  soft_ends=0.45, soft_w=0.25)
    L.link_only(top, C.objs(P, "rim", "grip", "cap", "capmark"), "recv_top")  # not the wall: a crisp line, not a band
    group(top, "lg_top")
    wr = CT.edge_ribbon("WhiteEdge", cam_m, lambda x, y: sm(-x, 0.004, 0.03) * sm(y, -0.01, 0.05) if x < 0 else 0.0,
                        40.0, 0.15, 0.03, WHITE_S * (P_TOP_K if pace else 1.0), WHITE, [P["rim"]])
    if wr:
        group(place(wr), "lg_top")
    vv = (cam_loc - centre).normalized()
    side_dir = Vector((math.cos(math.radians(YAW)), -math.sin(math.radians(YAW)), 0))
    rs = (2 * side_dir.dot(vv) * side_dir - vv).normalized()
    s_size, s_dist, s_s = (SIDE_SIZE_W, SIDE_DIST_W, SIDE_S_W) if white else (SIDE_SIZE, SIDE_DIST, SIDE_S * (P_SIDE_K if pace else 1.0))
    swc = K.strip("SideWall", tuple(centre + rs * s_dist + Vector((0, 0, 0.02))), s_size, s_s, tuple(centre),
                  soft_ends=0.45 if white else 0.3, soft_w=0.45 if white else 0.3)
    L.link_only(swc, C.objs(P, "wall", "rim", "neck"), "recv_side")
    group(swc, "lg_side")

    # --- lg_rim: ember hairline on the right front edge, shoulder to throat, tapering toward the throat
    def ember_w(x, y):
        if x < 0.02:
            return 0.0
        return sm(-y, -0.125, -0.085) * sm(y, -0.125, -0.09) * (0.45 + 0.55 * sm(y, -0.10, 0.10))

    er = CT.edge_ribbon("EmberEdge", cam_m, ember_w, 40.0, 0.15, 0.03, P_RIM_S if pace else EMBER_S,
                        K.kelvin(6500) if pace else EMBER, [P["rim"]])
    if er:
        group(place(er), "lg_rim")

    # --- lg_lip: soft grazing card from the upper-left, linked to the hole lips and bores only
    lip_dir = (Matrix.Rotation(math.radians(-YAW), 3, "Z") @ Vector((-0.70, -0.42, 0.62))).normalized()
    lc = centre + Vector((0, 0, 0.1))
    lip = K.strip("LipLight", tuple(lc + lip_dir * 1.1), (1.3, 1.3), LIP_W * (P_LIP_K if pace else 1.0), tuple(lc),
                  soft_ends=0.3, soft_w=0.3)
    L.link_only(lip, [P["holes"]], "recv_lip")
    group(lip, "lg_lip")

    # --- lg_floor: soft overhead wash around the base (floor only)
    pool = studio.spot_light("FloorWash", (0.05, -0.30, 1.35), POOL_W, F["pool_ang"], 1.0, target=(0.02, -0.02, 0.0), radius=0.06)
    L.link_only(pool, [cyc], "recv_pool")
    group(pool, "lg_floor")

    # --- lg_grip: neck, overgrip and cap from camera-left, a dim one from the right for the wrap's far side
    g1 = CT.strip("GripL", (-0.32, -0.22, 0.30), (0.0, -0.22, 0.0), 0.32, 0.02, GRIP_W,
                  recv=C.objs(P, "grip", "cap", "capmark", "neck"))
    g2 = CT.strip("GripR", (0.30, -0.22, 0.12), (0.0, -0.22, 0.0), 0.32, 0.03, GRIP2_W, recv=C.objs(P, "grip", "cap", "neck"))
    for g_ in (g1, g2):
        group(place(g_), "lg_grip")

    # --- lg_cap: the cap's front band mirrors this softbox: the groove and the bright-cut K read on satin black
    cl = CT.cap_light("CapBox", cam_m, P, CAP_W)
    group(place(cl), "lg_cap")

    # --- lg_key: the floor beam from the lower left (collimated slit light, gobo, haze); it also catches the cap
    az = math.radians(BEAM_AZ)
    el = math.radians(35.0)
    dl = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    u = Vector((-dl.x, -dl.y, 0)).normalized()
    Lb, W = 3.4, BEAM_W
    end = u * BEAM_PAST
    mid = end - u * (Lb / 2)
    ld = bpy.data.lights.new("Key", "AREA")
    ld.shape = "RECTANGLE"
    ld.size = W * 1.4
    ld.size_y = Lb * math.sin(el)
    ld.spread = math.radians(0.6)
    ld.energy = KEY_W
    ld.color = K.kelvin(5600)
    key = bpy.data.objects.new("Key", ld)
    sc.collection.objects.link(key)
    zaxis = dl.normalized()
    yaxis = (u - zaxis * u.dot(zaxis)).normalized()
    xaxis = yaxis.cross(zaxis)
    kl = mid + dl * 2.6
    key.matrix_world = Matrix(((xaxis.x, yaxis.x, zaxis.x, kl.x), (xaxis.y, yaxis.y, zaxis.y, kl.y),
                               (xaxis.z, yaxis.z, zaxis.z, kl.z), (0, 0, 0, 1)))
    L.link_only(key, [cyc], "recv_key")
    kc = key.copy()
    kc.data = ld.copy()
    kc.data.energy = KEY_W * KEY_CAP
    sc.collection.objects.link(kc)
    L.link_only(kc, [P["cap"], P["capmark"]], "recv_keycap")
    group(kc, "lg_key")
    gobo = K.plane("KeyGobo", (W * 1.4, ld.size_y * 1.02), (0, 0, 0))
    gobo.matrix_world = key.matrix_world @ Matrix.Translation((0, 0, -0.05))
    gm = K.new_mat("KeyGoboMat")
    nb = K.NB(gm)
    uu, vv2, _ = nb.coords("UV")
    a_ = nb.math("ABSOLUTE", nb.math("SUBTRACT", uu, 0.5))
    lat = nb.smooth(a_, 0.36, 0.22)
    core = nb.math("MULTIPLY_ADD", nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", a_, a_), -60.0)), 0.30, 0.78)
    v_base = 1.0 - BEAM_PAST / Lb
    along = nb.math("MULTIPLY", nb.math("POWER", nb.smooth(vv2, 0.06, 0.62), 1.3), nb.smooth(vv2, 1.0, v_base - 0.02))
    gg = nb.math("MULTIPLY", nb.math("MULTIPLY", lat, core), along)
    tr = nb.n.new("ShaderNodeBsdfTransparent")
    nb.l.new(nb.gray(gg), tr.inputs["Color"])
    go = nb.n.new("ShaderNodeOutputMaterial")
    nb.l.new(tr.outputs[0], go.inputs["Surface"])
    gobo.data.materials.append(gm)
    K.visibility(gobo, camera=False, diffuse=False, glossy=False, shadow=True)
    group(key, "lg_key")
    group(beam_haze("BeamHaze", mid, u, Lb, W, el, HAZE), "lg_key")

    # --- lg_horizon: warm lamp low behind-left puts the first light on the head's left edge
    warm = studio.area_light("HorizonRim", (-0.75, 0.75, 0.30), 0.6, HOR_RIM_W, color=K.hex_lin("#ff9a4a"),
                             size_y=0.25, target=(0.0, 0.0, 0.32))
    warm.data.spread = math.radians(120)
    L.link_only(warm, C.objs(P, "rim", "face", "wall", "neck"), "recv_warm")
    group(warm, "lg_horizon")

    # --- camera: level, lens shift only (verticals straight)
    cam = studio.camera(tuple(cam_loc), (0, 0, CAM_H), lens=F["lens"], shift=(0, F["shift_y"]))
    cam.data.sensor_fit = "HORIZONTAL"
    sc["racket_objs"] = [ob.name for k, ob in P.items() if k not in ("etchR", "etchL")]
    sc["racket_root"] = root.name
    _BASE[sc.name] = root.matrix_world.copy()
    if SWIVEL:
        swivel(sc, SWIVEL)
    sc["white"] = bool(white)
    sc["frame"] = json.dumps({k: (list(v) if isinstance(v, tuple) else v) for k, v in F.items()})
    return sc


def racket_bbox(sc):
    """Projected bounding box of the racket meshes: (x0, y0, x1, y1) in fractions of the frame, top-left origin."""
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x, y=sc.render.resolution_y)
    Mx = np.array(proj @ cam.matrix_world.inverted())
    lo, hi = np.array([9.0, 9.0]), np.array([-9.0, -9.0])
    for name in sc["racket_objs"]:
        ob = bpy.data.objects[name]
        me = ob.data
        co = np.empty(len(me.vertices) * 3, np.float64)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        W_ = np.array(ob.matrix_world)
        hom = np.c_[co, np.ones(len(co))] @ (Mx @ W_).T
        xy = hom[:, :2] / hom[:, 3:4]
        f = np.c_[(xy[:, 0] + 1) / 2, 1 - (xy[:, 1] + 1) / 2]
        lo = np.minimum(lo, f.min(0)); hi = np.maximum(hi, f.max(0))
    return (lo[0], lo[1], hi[0], hi[1])


# ------------------------------------------------------------------ swivel
_BASE = {}


def swivel(sc, deg):
    """Turn the racket (root and every part parented to it) by deg about the handle axis, world Z through x = y = 0
    (the racket stands on its butt cap there; C.pose's translation is along Z only). Lights stay where build() put them."""
    root = bpy.data.objects[sc["racket_root"]]
    root.matrix_world = Matrix.Rotation(math.radians(-SWIVEL_SIGN * deg), 4, "Z") @ _BASE[sc.name]
    bpy.context.view_layer.update()


SEQ_GROUPS = ["lg_rest", "lg_rim"]


def render_seq(o, mode, shot):
    """The swivel sequence: one build, then per frame: turn, render, denoise, comp the "full" variant.
    Groups are merged for speed: the full variant's gains are all 1 (lg_horizon 0), so every group but lg_rim (kept
    apart for the white-face ember desaturation in comp) renders as one lg_rest pass: 2 denoise passes, not 14."""
    global GROUPS
    n = o["seq"]
    a, b = o.get("yaw_range") or (0.0, 35.0)
    seq_dir = os.path.join(studio.OUT, o["out"])
    os.makedirs(seq_dir, exist_ok=True)
    yaws = [a + (b - a) * i / max(1, n - 1) for i in range(n)]
    todo = [i for i in range(n) if not os.path.exists(os.path.join(seq_dir, "f%03d.png" % i))
            and (not o.get("only") or i in o["only"])]
    print("seq %s: %d frames, yaw %.2f..%.2f, %d to render" % (o["out"], n, a, b, len(todo)), flush=True)
    if not todo:
        return
    t0 = time.time()
    sc = build(o, mode)
    print("scene built %.1f s" % (time.time() - t0), flush=True)
    vl = sc.view_layers[0]
    vl.lightgroups.add(name="lg_rest")
    hidden = 0
    for ob in sc.objects:
        g = ob.lightgroup
        if not g:
            continue
        if g == "lg_horizon":
            ob.hide_render = True; hidden += 1
        elif g != "lg_rim":
            ob.lightgroup = "lg_rest"
    print("seq: lg_horizon objects hidden:", hidden, flush=True)
    GROUPS = list(SEQ_GROUPS)
    for v in VARIANTS.values():
        v["lg_rest"] = 1
    sc.cycles.use_denoising = False    # the Combined pass is not used: the comp denoises the two group passes
    # One scene sync for the whole sequence: only the racket's transform changes between frames.
    sc.render.use_persistent_data = True
    work = os.path.join(seq_dir, "_w")
    # --crop x0 x1 y0 y1 (2026-10-29): frame 0 renders whole; every other frame renders only that region (Cycles
    # border, the comp told the full frame) and is pasted into frame 0 with a feathered edge, so the frames on disk are
    # whole and sequence.mjs crops them as before. The region must hold everything that moves, with margin.
    crop = o.get("crop")
    if crop and 0 not in todo and not os.path.exists(os.path.join(seq_dir, "f000.png")):
        raise SystemExit("seq --crop: frame 0 must exist or be rendered first")
    for i in todo:
        t1 = time.time()
        swivel(sc, yaws[i])
        bb = racket_bbox(sc)
        fc = crop if (crop and i > 0) else None
        sc.render.use_border = bool(fc)
        sc.render.use_crop_to_border = bool(fc)
        if fc:
            x0, x1, y0, y1 = fc
            sc.render.border_min_x, sc.render.border_max_x = x0, x1
            sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
        oi = dict(o, out=os.path.join(o["out"], "_w", "f%03d" % i), variants=["full"], gain=[], crop=fc)
        od, stem = _dirs(oi)
        os.makedirs(od, exist_ok=True)
        setup_passes(sc, od, stem)
        studio.render(os.path.join(o["out"], "_w", "f%03d__all" % i))
        collect(od, stem)
        meta = dict(w=o["w"], h=o["h"], spp=o["spp"], crop=fc, mode=mode, shot=shot, frame=json.loads(sc["frame"]),
                    bbox=bb, set=o["set"], white=bool(sc["white"]), yaw=yaws[i], feel=FEEL)
        with open(os.path.join(od, stem + "_meta.json"), "w") as fh:
            json.dump(meta, fh)
        comp(oi, shot, sc=sc)
        if fc:
            K.paste_region(os.path.join(seq_dir, "f000.png"), os.path.join(work, "f%03d-full.png" % i), fc,
                         os.path.join(seq_dir, "f%03d.png" % i))
            os.remove(os.path.join(work, "f%03d-full.png" % i))
        else:
            os.replace(os.path.join(work, "f%03d-full.png" % i), os.path.join(seq_dir, "f%03d.png" % i))
        for f in os.listdir(od):
            if f.startswith(stem + "_") and f.endswith(".exr"):
                os.remove(os.path.join(od, f))
        allp = os.path.join(work, "f%03d__all.png" % i)
        if os.path.exists(allp):
            os.remove(allp)
        dt = time.time() - t1
        with open(os.path.join(seq_dir, "frames.jsonl"), "a") as fh:
            fh.write(json.dumps(dict(i=i, yaw=round(yaws[i], 4), sec=round(dt, 1), spp=o["spp"], w=o["w"], h=o["h"],
                                     bbox=[round(q, 4) for q in bb])) + "\n")
        print("frame %d yaw %.2f %.1f s bbox %s" % (i, yaws[i], dt, " ".join(f"{100 * q:.1f}" for q in bb)), flush=True)
    print("seq done %.1f s" % (time.time() - t0), flush=True)


# ------------------------------------------------------------------ passes, render, comp
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


def collect(out_dir, stem):
    paths = L.collect_passes(out_dir, stem, GROUPS + ["index"])
    return paths


def render(o, mode, shot):
    t0 = time.time()
    sc = build(o, mode)
    print("scene built %.1f s" % (time.time() - t0), flush=True)
    bb = racket_bbox(sc)
    print("projected racket bbox (x0 y0 x1 y1, %% of frame): %s" % " ".join(f"{100 * q:.1f}" for q in bb), flush=True)
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
    print("rendered %.1f s" % (time.time() - t0), flush=True)
    collect(od, stem)
    meta = dict(w=o["w"], h=o["h"], spp=o["spp"], crop=o["crop"], mode=mode, shot=shot, frame=json.loads(sc["frame"]),
                bbox=bb, set=o["set"], white=bool(sc["white"]))
    if FEEL != "command":
        meta["feel"] = FEEL
    with open(os.path.join(od, stem + "_meta.json"), "w") as fh:
        json.dump(meta, fh)
    comp(o, shot, sc=sc)
    print("done %.1f s" % (time.time() - t0), flush=True)


def _dirs(o):
    out = os.path.join(studio.OUT, o["out"])
    return os.path.join(os.path.dirname(out), "passes"), os.path.basename(out)


def comp(o, shot, sc=None):
    od, stem = _dirs(o)
    with open(os.path.join(od, stem + "_meta.json")) as fh:
        meta = json.load(fh)
    if sc is None:
        sc = studio.reset()
    paths = {g: os.path.join(od, f"{stem}_{g}.exr") for g in GROUPS}
    lin = {g: L.load_lin(p) for g, p in paths.items() if os.path.exists(p)}
    idx = L.load_lin(os.path.join(od, f"{stem}_index.exr"))[..., 0] if os.path.exists(os.path.join(od, f"{stem}_index.exr")) else None
    gains = {k: dict(v) for k, v in VARIANTS.items()}
    for kv in o["gain"]:
        k, v = kv.split("=")
        var, g = k.split(".")
        g = g if g.startswith("lg_") else "lg_" + g
        if var == "all":
            for vv_ in gains.values():
                vv_[g] = vv_[g] * float(v)
        else:
            gains[var][g] = float(v)
    variants = o["variants"] or (["base", "full", "finale"] if shot == "beam" else ["base", "full"])
    scale = (meta["frame"]["span"][1] - meta["frame"]["span"][0]) / 0.54
    crop = meta.get("crop")
    for var in variants:
        acc = None
        for g, a in lin.items():
            k = gains[var].get(g, 0.0)
            if k:
                if g == "lg_rim" and var in EMBER_NEUTRAL and meta.get("white"):  # desaturated on white: no pink fringe
                    y_ = a[..., :3] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
                    a = a.copy()
                    a[..., :3] = y_[..., None] * np.array([0.97, 0.985, 1.0], np.float32)
                acc = a * k if acc is None else acc + a * k
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
        raw = os.path.join(studio.OUT, o["out"] + f"-{var}__raw.png")
        final = raw.replace("__raw.png", ".png")
        L.save_display(acc, raw, sc)
        if DETAIL_W and meta.get("white") and idx is not None:
            px_mm = (meta["frame"]["span"][1] - meta["frame"]["span"][0]) * meta["h"] / (Z_TOP * 1000)
            sg, g_lo, g_hi, b0, b1 = DETAIL_W
            GD.apply(raw, idx[::-1], sg * px_mm, parts=(1, 3, 5), g_lo=g_lo, g_hi=g_hi, b0=b0, b1=b1)
        bl = BLOOM_W if meta.get("white") else BLOOM
        bloom = (bl[0], bl[1], bl[2] * scale) if var != "base" else None
        ff = None
        if crop:
            x0, x1, y0, y1 = crop
            ff = (meta["w"], meta["h"], int(round(x0 * meta["w"])), int(round(y0 * meta["h"])))
        K.finish_png(raw, final, full_frame=ff, bloom=bloom)
        os.remove(raw)
        print("variant", var, final, flush=True)
    # face coverage: share of face pixels where the sweep (lg_face alone) is visibly lit
    if idx is not None and "lg_face" in lin:
        fm = np.abs(idx - 1) < 0.5
        lum = lin["lg_face"] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        hm = fm | (np.abs(idx - 2) < 0.5)
        stats = {f">{t}": round(float((lum[fm] > t).sum()) / max(1, int(hm.sum())), 3) for t in (0.01, 0.02, 0.04, 0.08)}
        print("sweep coverage of the head (face+holes px):", stats, "head px", int(hm.sum()), flush=True)


if __name__ == "__main__":
    # comp only: ../bpyenv/bin/python shots/k01_lib.py comp beam|phone <out> [--gain var.group=k ...]
    a = sys.argv[1:]
    if a and a[0] == "comp":
        o = parse_args(a[3:], a[2])
        o["out"] = a[2]
        comp(o, a[1])
