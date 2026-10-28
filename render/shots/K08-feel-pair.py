"""K08-feel-pair: Command (3K twill, left) and Pace (12K spread tow, right), mirror-symmetric at 3/4 face,
each in its own temperature of light, meeting dark at the seam. One render: two 8:9 panels.

Revision 2 (creative-director review): procedural anisotropic carbon (k789_lib.mat_carbon_aniso: per-tow
fibre direction flips the highlight, so the 2 mm twill shimmers and the 8 mm 12K tapes read as a bold grout-free
checker), an off-specular 'weave' card only the fibre lobes can see, a hard-edged band card per face (one crisp
graded band, the rest near-black), layered hole bores lit by a near-camera lamp (crescents), a graded side-wall
card with a KINETIQ etch on each visible wall, grip strip lights, cap ring lights, a darker satin throat, a
desaturated backdrop with grain and a faint grounding lift below each cap.

Canonical racket (2026-10-22, shots/kq_canon.py): both rackets are the canon build: 455.0 mm, a crown of 8 + 34 holes
with dark carbon-lined bores, the one-piece neck into the neutral-black helical overgrip (no brown perforated grip),
the satin anodised cap with one groove and an engraved Q, the company logo (no polished chamfer ring: the cap ring
lights are now a small softbox in each cap's mirror direction), the weave folding over the 1.5 mm edge onto the wall.
Command (left, KQ-000427) = WHITE 3K twill (owner, 2026-10-22: kq_canon mat_white on K04/K10's baked k04_tex2 maps,
2.6 mm tows; --set WHITE=0 gives the previous black), lit by its own soft spot pool and fill (white needs diffuse
light, canon lighting note 8; its black-carbon cards graded down by the W_* multipliers); Pace (right, KQ-000428) =
the canon 12K, 8 mm tapes (as K11-pace), in its unchanged black-carbon studio. Each throat carries its own laser-frosted serial (no set number: this is the single-racket edition). The
visible walls show the canon etches: SWISS MADE on Command's left wall, KINETIQ on Pace's right wall.
Page crops (src/content/stills.json): wide (Choose Feel desktop); left x .025 w .40 and right x .575 w .40, full
height (Choose Feel phone, the ConQuer Editions card, the gallery slides). The script prints each racket's projected
box and checks it sits whole inside its own crop and clear of the other's; with --crops it writes <out>_left.png and
<out>_right.png and fill-checks the frame and both crops.

Usage (from the blender dir, through the render lock):
  flock render.lock ../bpyenv/bin/python shots/K08-feel-pair.py --w 960 --h 540 --spp 48 --out k08c/K08_prev --crops
Optional: --crop x0 x1 y0 y1 (detail check), --lightgroups (lg_key, lg_rim_command, lg_rim_pace, lg_base; also a
multilayer EXR so the page can brighten one feel on hover). Final: 2560 x 1440, 160 spp.
Overrides: --set KEY=VALUE[,KEY=VALUE] for any upper-case look constant below (floats). Pre-canon: K08-feel-pair.precanon.bak.
Stage 3a (art director's critique, 2026-10-22; before: K08-feel-pair.v4-white-precrit3a.bak; helpers in feels_lib.py):
Pace was the pre-canon K08 / K11-pace 12K again (aniso 0.9, no organic, flip 0.30) under K08's own broad band (22, 45 mm,
line 0.5) and weave card (floor 0.25): one wide sheen with the hole field and tapes in it.
Pace pass (site review rounds 1 and 3, 2026-10-23; before: K08-feel-pair.v5-prepace12k.bak): (1) the 12K read as a flat
grey/black checkerboard with crisp squares at phone size (a transparency grid): Pace is now the canon v5 "fibre" 12K
(kq_canon.PACE, shared with K11-pace: tapes within a few percent of albedo, one uniform coat, the checker only in the
fibres' sheen direction, fine fibre normal, roughness streaks, slight crimp); PACE_V4=1 gives the stage 3a 12K back.
(2) Pace's ember rim (EMBER_W, #ff3a1e) read as a red trim the product does not have: Pace's edge lights are now
Command's neutral 6500 K (PACE_K: top curve, rim, wall), the rim lowered to a hairline (RIM_PACE 50 W, a quarter of the
ember's 200 W: #ff3a1e has about a quarter of white's luminance); PACE_EMBER=1 gives the warm edges back. Same camera,
same lights for Command, same crops: the Command half is unchanged (pace_diff.py). White Command: a steeper pool
(14.5 deg, 250 W, fill 0.7), one honeycombed glossy-only clearcoat streak (W_BAND_*), lifted bores (W_BORE_OCC / _COL,
bore lamp 1.0). Each cap's Q turned to the camera and lifted outside the cap (feels_lib.turn_mark), lit by
feels_lib.cap_lights. CLAMP_IND 4 (fireflies on the 12K). Final: 2560 x 1440, 256 spp. Writes <out>_masks.json (face,
holes and cap polygons) for feels_tools/fmeasure.py.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import k789_lib as L  # noqa: E402
from k789_lib import NB, Matrix, Vector, bpy, studio  # noqa: E402
import kq_canon as C  # noqa: E402
import feels_lib as FL  # noqa: E402

# ------------------------------------------------------------------ layout (metres)
LENS = 85.0
FRAME_H = 0.465 / 0.66       # racket 66% of the frame height (spec 70%: keeps the cap above the text band)
FRAME_W = FRAME_H * 16 / 9
CAM_D = FRAME_W * LENS / 36.0
X = FRAME_W / 4              # racket centres at x 25% / 75%
HC = 1.0                     # model origin (head centre) height
VIS_C = HC - 0.075           # visual centre of the racket (tip-to-cap midpoint)
CAM_Z = VIS_C - 0.06 * FRAME_H   # racket centre sits at y 44%
YAW = 20.0                   # toward the centre, measured against each racket's line of sight
ROLL = 8.0                   # heads lean in toward the seam

# ------------------------------------------------------------------ crops (frame fractions, stills.json)
CROPS = {"left": (0.025, 0.425), "right": (0.575, 0.975)}

# ------------------------------------------------------------------ look
KEY_S = 22.0
BAND_S = 10.0         # hard-edged reflection band on each face (canon: 22 with a 45 mm fall-off lit half of each face
                      # and, through the baked twill's metallic base, greyed the other half: now one blade per face)
BAND_EDGE = -0.02    # where the band's edge crosses the face (metres on the card, + toward the bright side)
BAND_DECAY = 0.012
BAND_LINE = 2.0
RIM_COOL = 220.0
EMBER_W = 200.0       # stage 3a's ember rim on Pace (#ff3a1e), only with PACE_EMBER = 1
RIM_PACE = 50.0       # 2026-10-23 (site review): Pace's rim is Command's neutral 6500 K, lowered to a hairline (the ember
                      # read as a red trim the product does not have; #ff3a1e has about a quarter of white's luminance)
PACE_K = 6500.0       # Pace's edge lights (top curve, rim, wall): neutral as Command's (stage 3a: 3200 / ember / 2700 K)
PACE_EMBER = 0.0      # 1 = the stage 3a warm Pace edges (top 3200 K, ember rim EMBER_W, wall 2700 K)
WALL_S = 0.35
TOP_S = 14.0
WEAVE_S = 5.0         # off-specular card: only one tow orientation catches it -> the weave reads
WEAVE_CMD = 0.4       # per-feel weave-card multipliers and floors (canon carbons: the baked twill's base is brighter;
WEAVE_PACE = 1.0      # the 12K keeps a faint checker in shade so the feel still reads beside the twill; stage 3a: the
WEAVE_FLOOR = 0.0     # pre-canon K08's weave card on Pace (5, floor 0.25)
WEAVE_FLOOR_PACE = 0.0   # round 6: 0 (0.25 lit every tape over the whole card: an even grid)
RAKE_S = 0.6          # throat rake per racket (K11's): a 50 x 5 mm strip 16 deg above the face from the lower left, 12.5 cm
RAKE_AZ = -135.0      # from the serial: the frosted serial reads, the tapes round it stay dark
RAKE_EL = 16.0
RAKE_D = 0.125
BAND_CMD = 1.0        # per-feel band-card multipliers
CMD_F0 = -1.0         # Command: the twill's base tint (k10_lib f0; -1 = the canon's 0.12), via kq_canon mat_opts
BAND_PACE = 1.0
# ------------------------------------------------------------------ Pace (stage 3a, art director: "Pace exactly as now")
# The pre-canon K08 / K11-pace 12K: k789_lib.mat_carbon_aniso's aniso 0.9, no organic variation, K11's 30 % coat flip,
# and K08's own broad band (22, 45 mm fall-off, hot line 0.5): one wide sheen with every hole and the tapes in it. The
# canon's 0.65 + organic and the canon band (10, 12 mm) sank the Pace head to a thin blade over a black void.
PACE_ANISO = 0.9      # PACE_* (stage 3a) apply only with PACE_V4 = 1
PACE_ORGANIC = 0.0
PACE_FLIP = 0.30
PACE_V4 = 0.0         # 2026-10-23: 0 = the canon v5 "fibre" 12K (kq_canon.PACE: near-uniform black, the tapes show through
                      # the fibres' sheen direction, fine fibre normal and roughness streaks; shared with K11-pace);
                      # 1 = the stage 3a 12K (aniso 0.9, flip 0.30: a flat grey/black checkerboard at phone size)
P_BAND_S = 9.0       # round 6: 22 -> 9 with the v6 fibre layer (face p50 35 -> 34 at 420 px; 22 gave 61)
P_BAND_DECAY = 0.045
P_BAND_LINE = 0.5
CLAMP_IND = 4.0       # indirect clamp: the fireflies on the 12K face (0 = off)
MARK_AZ = 1.0         # 1 = each cap's Q turned round the handle axis to face the camera (0 = the canon's model +Z)
CAP_CARD = 1.0      # stage 3a: 1 = the cap light set (feels_lib.cap_lights), linked to the cap and its Q, which is now
                    # turned to face the camera: a tall side strip (CAP_RS W, CAP_RSIDE deg round the handle axis from
                    # the camera, negative = camera-left) draws one rim line down the satin cap and flashes the Q's
                    # bright-cut chamfer; a soft gradient card in the mirror direction (CAP_CS) grades the cap's front;
                    # the canon proof's box (CAP_BS W). 0 = the old area light above (20 deg off-axis: a dead-black lump)
CAP_BS = 0.0        # canon box energy (W), size, distance
CAP_BSZ = 0.30
CAP_BD = 0.35
CAP_RS = 0.6        # rim strip energy (W), side angle (deg), size (m) and distance (m)
CAP_RSIDE = -75.0
CAP_RW, CAP_RH = 0.04, 0.50
CAP_RD = 0.30
CAP_CS = 20.0        # gradient card strength, size, distance, grade (u: across the cap) and floor
CAP_CW, CAP_CH = 0.30, 0.45
CAP_CD = 0.40
CAP_LO, CAP_HI, CAP_FLOOR = 0.0, 1.0, 0.15
CAP_CAZ = 20.0       # the card's reference normal turned this far (deg) past the Q's: off-axis, so the chamfer flashes
WEAVE_UP = 24.0
BORE_E = 60.0         # near-camera lamp linked to the bores only: every hole shows its layered crescent
GRIP_E = 3.0
GRIP_K = 6400.0        # neutral: the 5200 K strip tinted the black overgrip brown
CAP_S = 0.15          # cap softbox, 80 cm, 35 cm away, CAP_YAW off the cap's mirror direction (in the mirror direction
                      # the canon's 0.3 W box read as a lit badge behind the Q; off-axis the bright-cut Q reads alone)
CAP_SIZE = 0.80
CAP_YAW = -20.0       # degrees about the vertical, mirrored for the right racket
CAP_D = 0.35
# ------------------------------------------------------------------ white Command (owner, 2026-10-22; canon lighting note 8)
# Command (left) is WHITE 3K twill. Black carbon is lit by reflections only; under that studio white renders a flat
# grey, so the white racket gets real diffuse light of its own: a soft spot pool (lit upper side, the shade falling
# away down the face), a weak fill, and its reflection cards dimmed to a sheen and one gloss blade. Pool position: unit
# components in the left face's frame (t = model +X, up = world Z, n = out of the face), W_POOL_D from the aim point
# (model x, y). Every light stays linked to its own racket, so Pace (right) keeps its black-carbon studio unchanged.
WHITE = 1.0          # 0 = the previous black Command (then CMD_F0 applies)
W_POOL = 250.0
W_POOL_DEG = 14.5
W_POOL_T, W_POOL_U, W_POOL_N = -0.53, 0.485, 0.70
W_POOL_D = 1.2
W_POOL_TX, W_POOL_TY = -0.08, 0.10
W_POOL_R = 0.06
W_AKEY = 0.0       # a close raking area key instead of / beside the pool: its inverse-square fall-off sets the
W_AKEY_T, W_AKEY_U, W_AKEY_N = -0.55, 0.65, 0.52   # gradient across the face (components as the pool's)
W_AKEY_D = 0.7
W_AKEY_SZ = 0.30
W_AKEY_TX, W_AKEY_TY = -0.06, 0.08
W_FILL = 0.70
W_KEY = 0.4          # multipliers on Command's black-carbon light family
W_BAND = 1.60
W_BAND_BODY = 0.35   # stage 3a: the band's soft body on white (x W_BAND): the face keeps the pool's gradient ...
W_BAND_LINE = 14.0    # ... and one crisp clearcoat streak (x BAND_S x W_BAND) at luma 235-245
W_BAND_LW = 0.0025
W_BAND_HC = 2.6      # honeycomb tolerance (deg) + glossy-only (K05 v6): the fibres' sheen cannot gather it; 0 = off
W_BORE_OCC = 0.50    # white bores: a graphite gradient with a lit lip crescent (canon 0.82 / 0.025: printed black dots)
W_BORE_COL = 0.07
W_POOL_BLEND = 1.0
W_WEAVE = 0.0
W_TOP = 0.6
W_WALL = 2.0
W_BORE = 1.0
W_RAKE = 0.0         # the graphite frost reads in any light; a rake turns it pale (canon note)
BG = {"cool": (0.94, 0.97, 1.0), "warm": (1.0, 0.952, 0.904), "edge": 0.017, "mid": 0.026, "halo": 0.075, "seam": 0.012, "ground": 0.007}


def los(x):
    return math.degrees(math.atan2(-x, CAM_D))


def mirror_dir(n, p, cam):
    v = (Vector(cam) - Vector(p)).normalized()
    n = Vector(n).normalized()
    return (2 * n.dot(v) * n - v).normalized()


def set_head_material(root, mat):
    """Per-object material override on a linked duplicate (mesh data stays shared)."""
    for ob in root.children:
        if "_Head" in ob.name:
            for slot in ob.material_slots:
                slot.link = "OBJECT"
                slot.material = mat


def backdrop():
    """Camera-only graphite backdrop: cool left half, warm right half, dark seam, a soft halo behind each head."""
    W, H = FRAME_W * 2.2, FRAME_H * 2.2
    y = 1.6
    s = (CAM_D + y) / CAM_D
    ob = L.plane("Backdrop", (W * s, H * s), (0.0, y, CAM_Z), normal_to=(0.0, -CAM_D, CAM_Z))

    def strength(nb):
        x, yy, _ = nb.coords("Object")
        sx, sy = X * s, (VIS_C + 0.06 - CAM_Z) * s
        ax = nb.math("ABSOLUTE", x)
        # base: lifts from the frame edges toward each racket, falls into the seam
        dx = nb.math("DIVIDE", nb.math("SUBTRACT", ax, sx), 0.55 * s)
        dy = nb.math("DIVIDE", nb.math("SUBTRACT", yy, sy), 0.60 * s)
        r2 = nb.math("ADD", nb.math("MULTIPLY", dx, dx), nb.math("MULTIPLY", dy, dy))
        base = nb.math("MULTIPLY_ADD", nb.math("EXPONENT", nb.math("MULTIPLY", r2, -1.0)), BG["mid"] - BG["edge"], BG["edge"])
        # halo behind each head
        hx = nb.math("DIVIDE", nb.math("SUBTRACT", ax, sx), 0.21 * s)
        hy = nb.math("DIVIDE", nb.math("SUBTRACT", yy, nb.math("ADD", sy, 0.06 * s)), 0.27 * s)
        h2 = nb.math("ADD", nb.math("MULTIPLY", hx, hx), nb.math("MULTIPLY", hy, hy))
        e = nb.math("MULTIPLY_ADD", nb.math("EXPONENT", nb.math("MULTIPLY", h2, -1.0)), BG["halo"], base)
        # the seam: dark at x 50%
        # grounding: a faint, wide lift below each cap, as if an unseen floor caught the light (3-5 %)
        gx = nb.math("DIVIDE", nb.math("SUBTRACT", ax, sx), 0.30 * s)
        gy = nb.math("DIVIDE", nb.math("SUBTRACT", yy, (HC - 0.36 - CAM_Z) * s), 0.07 * s)
        g2 = nb.math("ADD", nb.math("MULTIPLY", gx, gx), nb.math("MULTIPLY", gy, gy))
        e = nb.math("MULTIPLY_ADD", nb.math("EXPONENT", nb.math("MULTIPLY", g2, -1.0)), BG["ground"], e)
        seam = nb.smooth(ax, 0.0, 0.16 * s)
        e = nb.math("MULTIPLY", e, nb.math("MULTIPLY_ADD", seam, 1.0 - BG["seam"] / BG["mid"], BG["seam"] / BG["mid"]))
        # fine grain: breaks 8-bit banding in the long dark gradient once exported for the web
        tcg = nb.n.new("ShaderNodeTexCoord")
        gr = nb.n.new("ShaderNodeTexWhiteNoise"); gr.noise_dimensions = "3D"
        mpg = nb.n.new("ShaderNodeMapping"); mpg.inputs["Scale"].default_value = (2600.0, 2600.0, 2600.0)
        nb.l.new(tcg.outputs["Object"], mpg.inputs["Vector"]); nb.l.new(mpg.outputs["Vector"], gr.inputs["Vector"])
        e = nb.math("MULTIPLY", e, nb.math("MULTIPLY_ADD", gr.outputs["Value"], 0.06, 0.97))
        return e

    m = L.new_mat("BackdropMat")
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    em = nb.n.new("ShaderNodeEmission")
    x, _, _ = nb.coords("Object")
    side = nb.smooth(x, -0.05, 0.05)
    mix = nb.n.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nb.l.new(side, mix.inputs["Factor"])
    mix.inputs[6].default_value = (*BG["cool"], 1)
    mix.inputs[7].default_value = (*BG["warm"], 1)
    nb.l.new(mix.outputs[2], em.inputs["Color"])
    nb._in(em.inputs["Strength"], strength(nb))
    lp = nb.n.new("ShaderNodeLightPath")
    tr = nb.n.new("ShaderNodeBsdfTransparent")
    ms = nb.n.new("ShaderNodeMixShader")
    nb.l.new(lp.outputs["Is Camera Ray"], ms.inputs[0])
    nb.l.new(tr.outputs[0], ms.inputs[1]); nb.l.new(em.outputs[0], ms.inputs[2])
    nb.l.new(ms.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    L.visibility(ob, camera=True, diffuse=False, glossy=False, shadow=False)
    return ob


def centre(ob):
    """World centre of an object's bounding box (canon parts keep their origin at the racket's head centre)."""
    bpy.context.view_layer.update()
    c = sum((Vector(v) for v in ob.bound_box), Vector()) / 8.0
    return ob.matrix_world @ c


def cap_light(name, root, cam, energy, color):
    """A small softbox in the mirror direction of the cap's front band (canon_test.cap_light in world space), linked
    to the cap and its K: the groove and the bright-cut K read on satin black."""
    P = C.parts(root)
    pr = C.cap_profile()
    yk = -0.2998 + C.CAP_SHIFT
    s_k = float(np.interp(-yk, [-y for (_, y) in pr], [s_ for (s_, _) in pr]))
    G, _ = C.section(64, grow=C.TAPE)
    mw = root.matrix_world
    Pc = mw @ Vector((0.0, yk, float(G[:, 1].max()) * s_k))
    nw = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
    r = Matrix.Rotation(math.radians(CAP_YAW * (1 if root.matrix_world.translation.x < 0 else -1)), 3, "Z") @ L.mirror_dir(nw, Pc, cam)
    lt = studio.area_light(name, tuple(Pc + r * CAP_D), CAP_SIZE, energy, color=color, size_y=CAP_SIZE * 0.35,
                           target=tuple(Pc))
    lt.visible_camera = False
    L.link_receivers(lt, [P["cap"], P["capmark"]], "recv_" + name)
    return lt


def rake_light(name, root, energy):
    """K10's throat rake (as K11): a 50 x 5 mm strip RAKE_EL above the face from RAKE_AZ (from the head direction;
    -135 = lower left, on the tapes' diagonal), RAKE_D from the serial, linked to the face only."""
    P = C.parts(root)
    x0, x1, y0, y1 = C.serial_box(root.get("kq_serial") or C.SERIAL)
    S = Vector(((x0 + x1) / 2, (y0 + y1) / 2, C.T2))
    az, el = math.radians(RAKE_AZ), math.radians(RAKE_EL)
    rd = (Vector((math.sin(az), math.cos(az), 0.0)) * math.cos(el) + Vector((0, 0, 1)) * math.sin(el)).normalized()
    mw = root.matrix_world
    lt = studio.area_light(name, tuple(mw @ (S + rd * RAKE_D)), 0.05, energy, color=(1.0, 0.985, 0.965), size_y=0.005,
                           target=tuple(mw @ (S + Vector((0, 0.004, 0)))))
    lt.visible_camera = False
    L.link_receivers(lt, [P["face"]], "recv_" + name)
    return lt


def project(root, cam, W, H):
    """Frame fractions (x from the left, y from the top) of a racket's vertices for the level camera looking +Y."""
    k = LENS / 36.0
    pts = []
    for ob in root.children:
        if ob.type != "MESH" or not len(ob.data.vertices):
            continue
        co = np.empty(len(ob.data.vertices) * 3)
        ob.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        mw = np.array(ob.matrix_world)
        wc = co @ mw[:3, :3].T + mw[:3, 3]
        pts.append(wc[::5] if len(wc) > 20000 else wc)
    p = np.concatenate(pts)
    dy = p[:, 1] - cam.y
    return 0.5 + k * (p[:, 0] - cam.x) / dy, 0.5 - k * (W / H) * (p[:, 2] - cam.z) / dy


def check_crops(left, right, cam, W, H):
    """Each racket, tip to cap, whole inside its own crop and clear of the other racket's crop."""
    ok = True
    for nm, r, other in (("left", left, "right"), ("right", right, "left")):
        u, v = project(r, cam, W, H)
        b = (float(u.min()), float(u.max()), float(v.min()), float(v.max()))
        c0, c1 = CROPS[nm]
        o0, o1 = CROPS[other]
        inside = c0 <= b[0] and b[1] <= c1 and b[2] >= 0.0 and b[3] <= 1.0
        clear = b[1] < o0 or b[0] > o1
        ok &= inside and clear
        print(f"framing {nm}: x {b[0]:.3f}-{b[1]:.3f} y {b[2]:.3f}-{b[3]:.3f}  crop {c0:.3f}-{c1:.3f} margins "
              f"{(b[0] - c0) * W:.0f}/{(c1 - b[1]) * W:.0f} px  inside {inside} clear {clear}", flush=True)
    print("crops", "OK" if ok else "FAIL", flush=True)


def build(o):
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.light_sampling_threshold = 0.0
    group = L.Groups(o["lightgroups"])
    cam = Vector((0.0, -CAM_D, CAM_Z))

    # the canonical rackets: Command (3K twill) left with KQ-000427, Pace (12K) right with KQ-000428
    white = WHITE > 0
    if CLAMP_IND > 0:
        sc.cycles.sample_clamp_indirect = CLAMP_IND
    left, LP = C.build_racket("KQL", feel="command", serial="KQ-000427",
                              mat_opts=dict(bore_occ=W_BORE_OCC, bore_col=W_BORE_COL) if white
                              else dict(C.COMMAND, white=0, **({"f0": CMD_F0} if CMD_F0 >= 0 else {})))
    right, RP = C.build_racket("KQR", feel="pace", serial="KQ-000428",
                               mat_opts=dict(C.PACE_V4, aniso=PACE_ANISO, organic=PACE_ORGANIC, flip=PACE_FLIP)
                               if PACE_V4 else None)
    L.pose(left, (-X, 0.0, HC), yaw_deg=YAW + los(-X), roll_deg=-ROLL)
    L.pose(right, (X, 0.0, HC), yaw_deg=-YAW + los(X), roll_deg=ROLL)
    bpy.context.view_layer.update()
    if MARK_AZ:
        for r_ in (left, right):
            AZ_USED[r_.name] = FL.turn_mark([r_], FL.face_az(r_, cam))
            print("cap Q of %s turned %.1f deg to face the camera" % (r_.name, AZ_USED[r_.name]), flush=True)
    check_crops(left, right, cam, o["w"], o["h"])
    MASKS.update(FL.masks({"left": left, "right": right}, cam, o["w"], o["h"], LENS))

    group(backdrop(), "lg_base")

    # --- lg_key: one slit overhead, slightly in front: rakes down both faces, draws both top curves (white Command
    # gets its own, dimmer copy: on white its diffuse spill greys the top of the face)
    for nm_, recv_, ks_ in (("Key", L.parts(right) + ([] if white else L.parts(left)), KEY_S),
                            ("KeyW", L.parts(left) if white else [], KEY_S * W_KEY)):
        if not recv_ or ks_ <= 0:
            continue
        key = L.strip(nm_, (0.0, -0.32, HC + 0.95), (2.4, 0.05), ks_, (0.0, 0.0, HC + 0.1), color=L.kelvin(5600),
                      soft_ends=0.3)
        L.link_receivers(key, recv_, "recv_" + nm_)
        group(key, "lg_key")

    for side, root, P, kind in ((-1, left, LP, "command"), (1, right, RP, "pace")):
        wk = (lambda k_: k_) if (white and kind == "command") else (lambda k_: 1.0)   # white-only multiplier
        g = f"lg_rim_{kind}"
        heads = C.objs(P, "_Head", style="k789")       # face, back, wall, neck
        bevel = C.objs(P, "rim")                        # the two 1.5 mm rounded edges (the weave folds over them)
        inner = C.objs(P, "_HeadInner", style="k789")  # hole bores, throat, bridge wall
        etch = C.objs(P, "etchR", "etchL")
        c = Vector((side * X, 0.0, HC))
        yw = math.radians(-side * YAW + los(side * X))
        n = Vector((math.sin(yw), -math.cos(yw), 0))
        # face band: a hard-edged card where the face mirrors the camera -> one crisp graded band, rest near-black
        d = L.mirror_dir(n, c, cam)
        h = Vector((-d.y, d.x, 0)).normalized()
        if h.x * side > 0:
            h = -h
        bright = (h + Vector((0, 0, 1.2))).normalized()  # upper outer corner of the face
        if white and kind == "command":
            # white: a faint body and one crisp clearcoat streak, honeycombed to the coat's mirror path, glossy-only
            sw = FL.band_card_hc(f"Band_{kind}", tuple(c + d * 1.5), (0.62, 0.62), BAND_S * BAND_CMD * W_BAND, tuple(c),
                                 tuple(bright), edge=BAND_EDGE, soft=0.006, decay=BAND_DECAY, line=W_BAND_LINE,
                                 line_w=W_BAND_LW, color=L.kelvin(6000),
                                 cprime=FL.mirror_point(cam, n, c) if W_BAND_HC > 0 else None,
                                 tol_deg=max(W_BAND_HC, 0.1), glossy_only=W_BAND_HC > 0, body=W_BAND_BODY)
        elif kind == "pace":
            sw = L.band_card(f"Band_{kind}", tuple(c + d * 1.5), (0.62, 0.62), P_BAND_S * BAND_PACE, tuple(c), tuple(bright),
                             edge=BAND_EDGE, soft=0.006, decay=P_BAND_DECAY, line=P_BAND_LINE, color=L.kelvin(6000))
        else:
            sw = L.band_card(f"Band_{kind}", tuple(c + d * 1.5), (0.62, 0.62), BAND_S * BAND_CMD, tuple(c), tuple(bright),
                             edge=BAND_EDGE, soft=0.006, decay=BAND_DECAY, line=BAND_LINE, color=L.kelvin(6000))
        L.link_receivers(sw, heads, f"recv_band_{kind}")
        group(sw, g)
        # weave: a soft card above the mirror direction; the clear coat cannot see it, the fibre lobes stretched
        # along one tow direction can, so alternate tows light up (twill / spread tow) in a graded field
        hz_axis = Vector((-d.y, d.x, 0)).normalized()
        d_up = (Matrix.Rotation(math.radians(WEAVE_UP), 3, hz_axis) @ d).normalized()
        if d_up.z < d.z:
            d_up = (Matrix.Rotation(math.radians(-WEAVE_UP), 3, hz_axis) @ d).normalized()
        wvs = WEAVE_S * (WEAVE_CMD if kind == "command" else WEAVE_PACE) * wk(W_WEAVE)
        if wvs > 0:
            wv = L.gradient_card(f"Weave_{kind}", tuple(c + d_up * 1.4), (1.1, 0.62), wvs, tuple(c), color=L.kelvin(5800),
                                 axis="v", lo=0.0, hi=1.0, floor=WEAVE_FLOOR if kind == "command" else WEAVE_FLOOR_PACE)
            L.link_receivers(wv, heads, f"recv_weave_{kind}")
            group(wv, g)
        rot = Matrix.Rotation(math.radians(los(side * X)), 3, "Z")

        def at(dx, dy, dz):
            return tuple(c + rot @ Vector((dx, dy, dz)))

        # top curve: broad card overhead-behind (K01 recipe), only the top edge can mirror it
        top = L.strip(f"Top_{kind}", at(0.0, 0.9, 0.64), (2.4, 1.4), TOP_S * wk(W_TOP), at(0.0, 0.0, 0.155),
                      color=L.kelvin(6500 if side < 0 else (3200 if PACE_EMBER else PACE_K)), soft_ends=0.45, soft_w=0.25)
        L.link_receivers(top, bevel, f"recv_top_{kind}")
        group(top, g)
        # rim: broad lamp in front of the outer edge, linked to the outline's rounded edges -> one hairline
        col = L.kelvin(6500) if side < 0 else L.kelvin(2700 if PACE_EMBER else PACE_K)
        rim = studio.area_light(f"Rim_{kind}", at(side * 1.10, -0.17, -0.04), 2.4,
                                RIM_COOL if side < 0 else (EMBER_W if PACE_EMBER else RIM_PACE),
                                color=col if side < 0 else (L.hex_lin("#ff3a1e") if PACE_EMBER else col), size_y=2.0,
                                target=at(side * 0.12, 0, -0.04))
        rim.visible_diffuse = False
        L.link_receivers(rim, bevel, f"recv_rim_{kind}")
        group(rim, g)
        # outer side wall: a tall card in the wall's mirror direction, bright at the top and fading down, so the
        # 38 mm band grades away behind the edge line and the etch reads against it
        wn = Vector((math.cos(yw), math.sin(yw), 0)) * side
        wp = c + wn * 0.13 + Vector((0, 0, -0.03))
        dw = L.mirror_dir(wn, wp, cam)
        wall = L.gradient_card(f"Wall_{kind}", tuple(wp + dw * 1.2), (0.10, 1.2), WALL_S * wk(W_WALL), tuple(wp), color=col,
                               axis="v", lo=0.15, hi=0.95, floor=0.0)
        L.link_receivers(wall, heads + etch, f"recv_wall_{kind}")
        group(wall, g)
        # bores: a soft lamp beside the camera, linked to the hole walls only -> each hole a lit crescent on its lip
        bl = L.area_at(f"Bore_{kind}", cam + Vector((side * 0.35, 0.0, 0.45)), c, 0.6, 0.6, BORE_E * wk(W_BORE),
                       color=L.kelvin(5200), recv=inner)
        group(bl, g)
        # grip: a long thin strip raking the overgrip from the outer side, so the helical wrap ridges catch light
        gc = centre(P["grip"])
        gs = L.area_at(f"Grip_{kind}", gc + Vector((side * 0.32, -0.22, 0.10)), gc, 0.025, 0.45, GRIP_E,
                       color=L.kelvin(GRIP_K), recv=[P["grip"]])
        group(gs, g)
        # cap: a small softbox in the satin cap's mirror direction (its groove and engraved K)
        if CAP_CARD:
            for cr in FL.cap_lights(f"Cap_{kind}", root, cam, AZ_USED.get(root.name, 0.0), box=CAP_BS, box_size=CAP_BSZ,
                                    box_d=CAP_BD, rim=CAP_RS, rim_side=CAP_RSIDE * (1 if side < 0 else -1),
                                    rim_size=(CAP_RW, CAP_RH), rim_d=CAP_RD, card=CAP_CS, card_size=(CAP_CW, CAP_CH),
                                    card_d=CAP_CD, card_lo=CAP_LO, card_hi=CAP_HI, card_floor=CAP_FLOOR, card_az=CAP_CAZ * (1 if side < 0 else -1),
                                    color=L.kelvin(5600)):
                group(cr, g)
        else:
            group(cap_light(f"Cap_{kind}", root, cam, CAP_S, L.kelvin(5600)), g)
        # throat: the frosted serial under a raking strip
        if RAKE_S * wk(W_RAKE) > 0:
            group(rake_light(f"Rake_{kind}", root, RAKE_S * wk(W_RAKE)), g)
        # white Command: a soft spot pool from the face's upper side and a weak fill (head parts only)
        if white and kind == "command":
            recv_w = heads + bevel + inner + etch
            t_ = Vector((math.cos(yw), math.sin(yw), 0.0))
            aim = root.matrix_world @ Vector((W_POOL_TX, W_POOL_TY, C.T2))
            pd = (t_ * W_POOL_T + Vector((0, 0, W_POOL_U)) + n * W_POOL_N).normalized()
            pl = None if W_POOL <= 0 else studio.spot_light("WPool", tuple(aim + pd * W_POOL_D), W_POOL, W_POOL_DEG, blend=W_POOL_BLEND,
                                   color=(1.0, 0.985, 0.97), target=tuple(aim), radius=W_POOL_R)
            if pl is not None:
                L.link_receivers(pl, recv_w, "recv_wpool")
                group(pl, g)
            if W_AKEY > 0:
                ak_aim = root.matrix_world @ Vector((W_AKEY_TX, W_AKEY_TY, C.T2))
                kd = (t_ * W_AKEY_T + Vector((0, 0, W_AKEY_U)) + n * W_AKEY_N).normalized()
                ak = studio.area_light("WAKey", tuple(ak_aim + kd * W_AKEY_D), W_AKEY_SZ, W_AKEY,
                                       color=(1.0, 0.985, 0.97), target=tuple(ak_aim))
                ak.visible_camera = False
                L.link_receivers(ak, recv_w, "recv_wakey")
                group(ak, g)
            if W_FILL > 0:
                fl = studio.area_light("WFill", tuple(c - t_ * 0.6 + n * 0.9 + Vector((0, 0, 0.25))), 1.0, W_FILL,
                                       color=(0.94, 0.96, 1.0), target=tuple(c))
                fl.visible_camera = False
                L.link_receivers(fl, recv_w, "recv_wfill")
                group(fl, g)
            print(f"white pool at {tuple(round(v_, 3) for v_ in aim + pd * W_POOL_D)}", flush=True)

    L.visual_only("Backdrop")
    L.debug_off()
    studio.camera(tuple(cam), (0.0, 0.0, CAM_Z), lens=LENS)
    return sc


MASKS = {}
AZ_USED = {}


def crops(png):
    """8-bit copies of the two page crops (left / right, full height) and the fill check on the frame and both."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    w, h = im.size
    outs = [png]
    for nm, (c0, c1) in CROPS.items():
        dst = png.replace(".png", "_" + nm + ".png")
        im.crop((round(w * c0), 0, round(w * c1), h)).save(dst)
        outs.append(dst)
    subprocess.run([sys.executable, os.path.join(ROOT, "fillcheck.py")] + outs, check=False)


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--pace" in argv:   # canon Pace material keys for this run (tuning): --pace aniso=0.6,fib_h=1.5
        for kv in argv[argv.index("--pace") + 1].split(","):
            k_, v_ = kv.split("=")
            C.PACE[k_] = float(v_)
    if "--set" in argv:
        for kv in argv[argv.index("--set") + 1].split(","):
            k_, v_ = kv.split("=")
            globals()[k_] = float(v_)
    o = L.parse_args(argv, "k08c/K08_prev")
    os.makedirs(os.path.join(studio.OUT, os.path.dirname(o["out"]) or "."), exist_ok=True)
    path = L.render_main(build, o)
    import json
    with open(path.replace(".png", "_masks.json"), "w") as fh_:
        json.dump(MASKS, fh_)
    if "--crops" in argv and not o["crop"]:
        crops(path)
