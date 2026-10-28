"""K07-lineup-five: five identical Command rackets in a row, each on a machined pin stand in its own tapered shaft
of light, over a glossy black floor whose reflection fades toward the camera. One ember hairline sits at the true
horizon behind the row: hidden by the heads, glinting through the lowest perforations, continuous in the gaps.

Canon (2026-10-22): the five rackets are the canonical racket (shots/kq_canon.py), one Command build and four clones,
serials KQ-000427 to KQ-000431 left to right: 455.0 mm, the crown of 8 + 34 holes with carbon-lined bores (was the old
hex grid with EVA bores), the one-piece neck into the neutral-black helical overgrip (was a perforated grip) and the satin
cap with its engraved Q, the logo (was a chamfer-ring cap, so the cap ring light is now a soft cap softbox), K10's twill folding
over the 1.5 mm edge (was the 2.6 mm aniso weave). At this size the weave reads as a sheen. The butt is at y = -0.300, so
the head centre sits 0.300 above the cap bottom.

Stage 3a critique (white Command): one soft clear-coat sweep and an edge hairline per racket (in its shaft group, so
--seq still lights one racket at a time), the throat out of every direct light (it read as a pale printed chevron), and
shared light-linking collections (the white rig went over Cycles' 64 and the fifth racket lost its links). Details at
KW_SWEEP below. Backup of the previous script: shots/K07-lineup-five.v4-white-precrit.bak.

Alternating feels (owner, 2026-10-23: "I see 5 white rackets... maybe alternate them here with black versions?"):
ROW = Command, Pace, Command, Pace, Command (the trio crop shows Pace, Command, Pace). Rackets 1, 3, 5 are one white
Command build and its clones; 2 and 4 one canon Pace (kq_canon.PACE, v6) build and its clone. Every racket keeps the same
handle, cap, edge hairline and neutral rim, and its own shaft group; only the face light differs. Pace gets K08's
black-carbon face set (P_* below: a dimmed hard band card, a weave card, no diffuse pool), a neutral rim dimmed by
P_RIM. Backup of the all-white script: shots/K07-lineup-five.v5-allwhite.bak.

Usage (from the blender dir):
  ../bpyenv/bin/python shots/K07-lineup-five.py --w 960 --h 540 --spp 32 --out K07_prev
  --variant full    all five shafts on (default)
  --variant seqN    only shafts 1..N on (N = 0..4), rendered on its own
  --seq             with the full variant: also write <out>-seq0..seq4.png from the light-group passes of the
                    same render (compositor sum + OIDN per pass), so the switch-on sequence costs no extra render
Optional: --crop x0 x1 y0 y1, --lightgroups (lg_shaft_1..5, lg_horizon, lg_base; also writes a multilayer EXR).
Master 16:9.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k789_lib as L  # noqa: E402
from k789_lib import NB, Matrix, Vector, bmesh, bpy, racket, studio  # noqa: E402
import kq_canon as C  # noqa: E402
import kw_sheen as KS  # noqa: E402
import canon_test as CT  # noqa: E402

# ------------------------------------------------------------------ layout (metres)
N = 5
PITCH = 0.505         # racket centres: 26 cm heads, ~25 cm gaps; the row spans x 10-90 %
YAW = -15.0           # face turned toward camera-left (per line of sight): the right side wall reads as a band
LIFT = 0.09           # cap bottom height: each racket stands on a 9 cm machined pin
HEAD_Z = LIFT - C.BUTT_Y  # model origin (head centre) height: the canon butt is at y = -0.300
CAM_D = 3.95
CAM_Z = HEAD_Z - 0.0183  # level; the far horizon line lands on the lowest hole row and glints through it
LENS = 50.0

# ------------------------------------------------------------------ look
SHAFT_TOP = 2.6       # apex of the light cone (just above frame): the column visibly tapers toward it
SHAFT_R0 = 0.12       # cone radius at the floor
SHAFT_S = 0.11        # column emission (camera + floor reflection only)
SHAFT_FRONT = 0.10    # near half of each column relative to the back half (keeps the racket crisp)
SHAFT_HIGH = 0.06     # column level above y 25 % of frame (text zone), relative to the core
SPOT_W = 900.0
TOP_S = 26.0
BAND_S = 8.0          # hard-edged reflection band on each face (canon twill: a narrow band; a half-plane greys it)
BAND_EDGE = -0.015
BAND_DECAY = 0.012
BAND_LINE = 1.6
WALLW_S = 0.9        # dim fill on the visible side wall
RIM_E = 260.0
BORE_E = 30.0         # hole-lip crescents (canon 'holes' part only; the carbon-lined bores stay dark)
GRIP_E = 4.0
CAP_E = 0.4
SERIALS = tuple(f"KQ-{427 + k:06d}" for k in range(N))   # KQ-000427 .. KQ-000431, left to right
STAND_E = 6.0
WALL_S = (0.028, 0.040)        # far wall radiance: top of frame, at the horizon
PAINT = (0.026, 0.031, 0.040)  # painted floor radiance: near, under the row, far
HAZE_S = 0.05
POOL_S = 0.05
HALO_S = 0.007
FLOOR_ALB = 0.030
FAR_Y = 60.0          # far wall; the ember slot runs along its foot (60 m: its floor mirror merges with it)
HORIZON_S = 22.0
HORIZON_H = 0.024     # slot height (with its mirror, a 2-3 px core at 2560 x 1440)
EMBER = (1.0, 0.23, 0.12)

# White Command (owner, 2026-10-22): the faces were lit by reflection only (a hard band card), which leaves white
# carbon a flat grey and floods it with the card's diffuse spill. A white racket gets real diffuse light in its own
# shaft group (so the switch-on sequence still lights one racket at a time), linked to that racket's head parts only
# (canon lighting note 8): a soft spot pool from the upper left in front (the crown white, falling to white-in-shade at
# the throat), a weak fill from the front right; the band card becomes reflection-only (a clear-coat gloss band); the
# hole-lip lamp, the top line and the wall card are dimmed. At this size the twill reads as a sheen.
FEEL, MAT_OPTS = "command", None
ROW = ("command", "pace", "command", "pace", "command")   # owner, 2026-10-23: alternate white Command and black Pace
WHITE_RK = C.is_white(FEEL, MAT_OPTS)
KW_POOL, KW_POOL_DEG, KW_POOL_R = 260.0, 13.0, 0.06
KW_POOL_AT, KW_POOL_T = (-0.55, -0.85, 0.75), (-0.05, 0.09)   # racket view frame (x right, y away, z up), from the head
KW_FILL, KW_FILL_AT = 1.0, (0.70, -0.90, 0.10)
KW_BAND = 3.0
# Stage 3a (art director, 2026-10-22): the white heads read as matte grey paddles (no clear-coat sweep, no edge hairline,
# the weave invisible at page size), and the throat read as a pale printed chevron (the shaft spot lit the V's walls).
# - KW_SWEEP: one soft diagonal clear-coat sweep per racket (kw_sheen.gloss_sweep: designed on the face in model space,
#   glossy-only, honeycomb, smoothstep profile), in that racket's shaft group; it replaces the hard band card on white.
#   The twill's fibre sheen flips inside it, so the weave reads as a sheen at this size.
# - KW_EDGE: the canon edge_ribbon on the rim (upper-left edge, one crisp white hairline), in the shaft group.
# - the throat and bridgewall are out of the spot, pool and fill links: the throat reads as a dark opening, like the holes.
KW_SWEEP, KW_SWEEP_W, KW_SWEEP_H = 15.0, 0.034, 0.8          # strength, half width on the face (m), card distance (m)
KW_SWEEP_C, KW_SWEEP_ANG, KW_SWEEP_L = (0.03, -0.035), 58.0, 0.17   # centre (model x, y), angle (deg), half length
KW_EDGE, KW_EDGE_PHI = 90.0, 40.0          # the rim is ~1.4 px at 2560: 25 (canon front) added only 2-8 luma
# Pace (black 12K, kq_canon.PACE v6): K08's black-carbon face set, in the racket's own shaft group
P_BAND_S, P_BAND_DECAY, P_BAND_LINE = 12.0, 0.045, 0.5  # K08's Pace band (9), up to 12: each racket is small
P_WEAVE, P_WEAVE_UP = 2.0, 24.0   # K08's weave card (5) at 2: 5 washed the upper face grey at this size; 0 lost it
P_TOP_S, P_BORE_E, P_WALLW_S = 26.0, 30.0, 0.9            # the black-carbon K07 values (v3-black)
P_RIM = 1.0          # Pace's neutral rim relative to RIM_E: the same hairline as Command (0.5 vanished at page size)
P_EDGE = 1.0         # Pace's edge ribbon relative to KW_EDGE
CLAMP_IND = 4.0      # K08: indirect clamp against fireflies on the 12K face
if WHITE_RK:
    BORE_E, TOP_S, WALLW_S, GRIP_E = 5.0, 14.0, 0.5, 2.5
    KW_BAND = 0.0
for _kv in filter(None, os.environ.get("K07_SET", "").split(",")):   # look-dev: K07_SET="KW_POOL=150,TOP_S=10"
    _k, _v = _kv.split("=")
    _cur = globals()[_k]
    globals()[_k] = tuple(float(x) for x in _v.split(":")) if isinstance(_cur, tuple) else float(_v)
    print("set", _k, globals()[_k], flush=True)


def xs():
    return [(i - (N - 1) / 2) * PITCH for i in range(N)]


def los(x):
    """Angle (deg, about +Z) from straight-ahead to the camera as seen from a racket at x."""
    return math.degrees(math.atan2(-x, CAM_D))


def frame_h():
    return 36.0 / LENS * CAM_D * 9 / 16


def z_at_frac(yf, dist=CAM_D):
    """World height at the racket plane (or `dist`) seen at fraction yf from the top of the frame."""
    return CAM_Z + (0.5 - yf) * frame_h() * dist / CAM_D


def mat_glossy_floor(name="GlossFloor"):
    """Lacquered black floor. Its reflection is crisp and strong under the row and fades (and blurs) toward the
    camera, so the mirrored stands and caps read at ~35 % and the bottom of frame falls to near-black; the far
    floor is rougher, so the horizon line's reflection is a soft glow, not a second line. A camera-only painted
    grade keeps it graphite, never flat black."""
    m = L.new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    tc = nb.n.new("ShaderNodeTexCoord")
    big = nb.n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 3.0; big.inputs["Detail"].default_value = 4
    fine = nb.n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 160.0; fine.inputs["Detail"].default_value = 3
    for t in (big, fine):
        nb.l.new(tc.outputs["Object"], t.inputs["Vector"])
    col = nb.math("MULTIPLY_ADD", nb.smooth(big.outputs["Fac"], 0.3, 0.7), FLOOR_ALB * 0.25, FLOOR_ALB * 0.85)
    cc = nb.n.new("ShaderNodeCombineColor")
    for k in range(3):
        nb.l.new(col, cc.inputs[k])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    x, y, _ = nb.coords("Object")
    yw = nb.math("ADD", y, 55.0)  # plane centred at world y = 55
    near = nb.smooth(yw, -1.75, -0.45)     # 1 from 0.45 m in front of the row backward, 0 by 1.75 m in front
    far = nb.smooth(yw, 5.0, 14.0)
    r = nb.math("MULTIPLY_ADD", nb.smooth(fine.outputs["Fac"], 0.35, 0.65), 0.012, 0.030)
    r = nb.math("ADD", r, nb.math("MULTIPLY", nb.math("SUBTRACT", 1.0, near), 0.16))
    r = nb.math("ADD", r, nb.math("MULTIPLY", far, 0.06))
    nb.l.new(r, b.inputs["Roughness"])
    spec = nb.math("MULTIPLY_ADD", nb.math("MULTIPLY", near, nb.math("MULTIPLY_ADD", far, -0.45, 1.0)), 0.50, 0.05)
    nb.l.new(spec, b.inputs["Specular IOR Level"])
    # painted graphite grade, camera rays only (lights nothing): near floor -> under the row -> far floor
    e = nb.math("MULTIPLY_ADD", nb.smooth(yw, -3.0, 0.0), PAINT[1] - PAINT[0], PAINT[0])
    e = nb.math("ADD", e, nb.math("MULTIPLY", nb.smooth(yw, 0.0, 30.0), PAINT[2] - PAINT[1]))
    side = nb.smooth(nb.math("ABSOLUTE", nb.math("DIVIDE", x, nb.math("ADD", nb.math("MAXIMUM", nb.math("ADD", yw, 4.0), 0.0), 1.0))), 0.9, 0.2)
    e = nb.math("MULTIPLY", e, nb.math("MULTIPLY_ADD", side, 0.25, 0.75))
    gr = nb.n.new("ShaderNodeTexWhiteNoise"); gr.noise_dimensions = "3D"
    mpg = nb.n.new("ShaderNodeMapping"); mpg.inputs["Scale"].default_value = (900.0, 900.0, 900.0)
    nb.l.new(tc.outputs["Object"], mpg.inputs["Vector"]); nb.l.new(mpg.outputs["Vector"], gr.inputs["Vector"])
    e = nb.math("MULTIPLY", e, nb.math("MULTIPLY_ADD", gr.outputs["Value"], 0.06, 0.97))
    lp = nb.n.new("ShaderNodeLightPath")
    nb.l.new(nb.math("MULTIPLY", e, lp.outputs["Is Camera Ray"]), b.inputs["Emission Strength"])
    b.inputs["Emission Color"].default_value = (0.93, 0.95, 1.0, 1)
    return m


def glossy_fade(nb, z, z0=0.0, z1=0.22):
    """1 for camera rays; for glossy (floor reflection) rays, fades the emitter out above z1 so the mirrored
    columns fall to near-black by y 85 % of frame."""
    lp = nb.n.new("ShaderNodeLightPath")
    fade = nb.smooth(z, z1, z0)
    return nb.math("MULTIPLY_ADD", lp.outputs["Is Glossy Ray"], nb.math("SUBTRACT", fade, 1.0), 1.0)


def shaft(name, x, strength, front=SHAFT_FRONT):
    """Fake light column: an open cone tapering toward the spot above frame. Emission follows the path length
    through it (|N.I|), the near half is weaker, the level holds the core around the racket and drops to
    SHAFT_HIGH above y 25 % (text zone), with slow low-contrast haze breakup. Camera + glossy only."""
    segs, rings = 96, 30
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    zt = 2.2
    grid = []
    for j in range(rings + 1):
        z = zt * j / rings
        r = SHAFT_R0 * (SHAFT_TOP - z) / SHAFT_TOP
        grid.append([bm.verts.new((x + r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), z))
                     for k in range(segs)])
    for j in range(rings):
        for k in range(segs):
            bm.faces.new((grid[j][k], grid[j][(k + 1) % segs], grid[j + 1][(k + 1) % segs], grid[j + 1][k]))
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    p0 = me.polygons[0]
    if (p0.center - Vector((x, 0, p0.center.z))).dot(p0.normal) < 0:
        me.flip_normals()
    z_core = z_at_frac(0.25)  # world height at y 25 % of frame

    def s(nb):
        lw = nb.n.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        mu = nb.math("SUBTRACT", 1.0, lw.outputs["Facing"])
        mu = nb.math("POWER", nb.math("MAXIMUM", mu, 0.0), 1.8)  # softer edges than a hard cylinder
        _, _, z = nb.coords("Object")
        # haze breakup: slow 3-D wisps (+-5 %) plus faint vertical streaks (+-3 %)
        tc = nb.n.new("ShaderNodeTexCoord")
        nz = nb.n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 5.0; nz.inputs["Detail"].default_value = 4
        nz.inputs["Roughness"].default_value = 0.55
        nb.l.new(tc.outputs["Object"], nz.inputs["Vector"])
        mp = nb.n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (14.0, 14.0, 0.8)
        nb.l.new(tc.outputs["Object"], mp.inputs["Vector"])
        st = nb.n.new("ShaderNodeTexNoise"); st.inputs["Scale"].default_value = 1.0; st.inputs["Detail"].default_value = 2
        nb.l.new(mp.outputs["Vector"], st.inputs["Vector"])
        brk = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", nz.outputs["Fac"], 0.5), 0.20, 1.0)
        brk = nb.math("MULTIPLY", brk, nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", st.outputs["Fac"], 0.5), 0.12, 1.0))
        mu = nb.math("MULTIPLY", mu, brk)
        # vertical level: core around the racket, SHAFT_HIGH above y 25 %, a gentle foot at the floor
        vert = nb.math("MULTIPLY_ADD", nb.smooth(z, z_core, z_core - 0.16), 1.0 - SHAFT_HIGH, SHAFT_HIGH)
        vert = nb.math("MULTIPLY", vert, nb.math("MULTIPLY_ADD", nb.smooth(z, 0.0, 0.30), 0.35, 0.65))
        vert = nb.math("MULTIPLY", vert, nb.smooth(z, 2.2, 1.8))
        geo = nb.n.new("ShaderNodeNewGeometry")
        side = nb.math("MULTIPLY_ADD", geo.outputs["Backfacing"], 1.0 - front, front)
        f = nb.math("MULTIPLY", nb.math("MULTIPLY", mu, vert), side)
        f = nb.math("MULTIPLY", f, glossy_fade(nb, z))
        return nb.math("MULTIPLY", f, strength)

    ob.data.materials.append(L.emitter_mat(name + "Mat", L.kelvin(5600), s, additive=True))
    L.visibility(ob, camera=True, diffuse=False, glossy=True, shadow=False)
    return ob


def build_stand(name):
    """Machined display stand: 84 mm satin black anodised disc, 8 mm tall, polished 1.0 mm top chamfer, and a
    6.4 mm polished steel pin up into the end cap."""
    anod = bpy.data.materials.get("StandAnod") or racket.mat_basic("StandAnod", (0.03, 0.03, 0.033), rough=0.36, metallic=1.0)
    pol = bpy.data.materials.get("StandPolish") or racket.mat_basic("StandPolish", (0.86, 0.86, 0.88), rough=0.05, metallic=1.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.042, depth=0.008, location=(0, 0, 0.004))
    base = bpy.context.active_object
    base.name = name + "_base"
    base.data.materials.append(anod); base.data.materials.append(pol)
    bv = base.modifiers.new("ch", "BEVEL"); bv.width = 0.0010; bv.segments = 2; bv.limit_method = "ANGLE"
    bv.material = 1; bv.use_clamp_overlap = False
    racket._apply_all(base)
    base.data.shade_smooth(); base.data.set_sharp_from_angle(angle=math.radians(35))
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.0032, depth=LIFT - 0.008 + 0.004,
                                        location=(0, 0, 0.008 + (LIFT - 0.008 + 0.004) / 2))
    pin = bpy.context.active_object
    pin.name = name + "_pin"
    pin.data.materials.append(pol)
    pin.data.shade_smooth()
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    base.parent = root; pin.parent = root
    return root


def build(o):
    v = o["variant"]
    on = N if v == "full" else int(v[3:]) if v.startswith("seq") else N
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.light_sampling_threshold = 0.0
    sc.cycles.transparent_max_bounces = 16
    group = L.Groups(o["lightgroups"] or o.get("seq"))
    cam_loc = Vector((0.0, -CAM_D, CAM_Z))

    # --- five linked duplicates of one racket, five of one stand
    srcs, roots = {}, []
    for i, feel in enumerate(ROW):
        if feel not in srcs:   # one build per feel, clones for the rest (shared meshes, own serial)
            srcs[feel] = C.build_racket(f"KQ{i + 1}", feel=feel, serial=SERIALS[i],
                                        mat_opts=MAT_OPTS if feel == "command" else None)[0]
            roots.append(srcs[feel])
        else:
            roots.append(C.clone(srcs[feel], f"KQ{i + 1}", serial=SERIALS[i])[0])
    if "pace" in ROW and CLAMP_IND > 0:
        sc.cycles.sample_clamp_indirect = CLAMP_IND
    stand0 = build_stand("ST1")
    stands = [stand0] + [L.clone(stand0, f"ST{i + 1}") for i in range(1, N)]
    for r, st, x in zip(roots, stands, xs()):
        # yaw measured against each racket's own line of sight, so all five read identical in the frame
        C.pose(r, (x, 0.0, HEAD_Z), yaw_deg=YAW + los(x), tilt_deg=90.0)
        st.location = (x, 0.0, 0.0)
    bpy.context.view_layer.update()
    # every racket's throat walls (the V) and bridge wall: no direct light, so the throat reads as an opening
    throats = [o_ for r in roots for o_ in C.objs(C.parts(r), "throat", "bridgewall")]
    # shared receiver collections: Cycles allows 64 light-linking collections per scene, and one per emitter (16 per
    # racket) went over it ("Maximum number of light linking collections (64) exceeded"): the last racket's links
    # were dropped and its lights lit everything. Emitters with the same receivers now share one collection (42 in all).
    throat_ex = KS.exclusion("spot_nothroat", throats)

    # --- floor and far wall
    bpy.ops.mesh.primitive_plane_add(size=140, location=(0, 55, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.data.materials.append(mat_glossy_floor())
    group(floor, "lg_base")

    wall = L.plane("Wall", (160.0, 40.0), (0.0, FAR_Y + 0.3, 20.0), normal_to=(0, 0, 20.0))

    def wall_s(nb):
        x, y, _ = nb.coords("Object")  # plane local: x across, y up
        z = nb.math("ADD", y, 20.0)
        vert = nb.math("POWER", nb.smooth(z, 13.0, 0.0), 1.5)
        side = nb.smooth(nb.math("ABSOLUTE", x), 30.0, 6.0)
        f = nb.math("MULTIPLY", vert, nb.math("MULTIPLY_ADD", side, 0.3, 0.7))
        return nb.math("MULTIPLY_ADD", f, WALL_S[1] - WALL_S[0], WALL_S[0])

    wall.data.materials.append(L.cam_only_mat("WallMat", wall_s, color=(0.92, 0.94, 1.0), glossy=False))
    L.visibility(wall, camera=True, diffuse=False, glossy=False, shadow=False)
    group(wall, "lg_base")

    # haze card just behind the row: lifts the air between the columns, strongest at racket height
    haze = L.plane("Haze", (7.0, 2.4), (0.0, 0.9, 1.2), normal_to=(0.0, -CAM_D, 1.2))

    def haze_s(nb):
        u, vv, _ = nb.coords("UV")
        z = nb.math("MULTIPLY_ADD", vv, 2.4, 0.0)
        zc = nb.math("SUBTRACT", z, HEAD_Z)
        f = nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", zc, zc), -9.0))
        f = nb.math("MULTIPLY", f, nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.42), nb.smooth(u, 1.0, 0.58)))
        f = nb.math("MULTIPLY", f, glossy_fade(nb, z))
        return nb.math("MULTIPLY", f, HAZE_S)

    haze.data.materials.append(L.emitter_mat("HazeMat", (0.95, 0.96, 1.0), haze_s, additive=True))
    L.visibility(haze, camera=True, diffuse=False, glossy=True, shadow=False)
    floor_c = KS.coll("recv_floor", [floor])
    KS.relink(haze, floor_c)
    group(haze, "lg_base")

    # --- lg_horizon: an ember slot in the far wall at camera height = the true horizon (y 50 %). The heads hide
    # it, it glints through the lowest perforations, it runs unbroken through every gap; plus a faint bloom.
    hz = L.plane("Horizon", (160.0, HORIZON_H * 3), (0.0, FAR_Y, HORIZON_H * 1.5 - HORIZON_H * 0.5), normal_to=(0, -CAM_D, CAM_Z))

    def hz_s(nb):
        u, vv, _ = nb.coords("UV")
        d = nb.math("DIVIDE", nb.math("SUBTRACT", vv, 0.5), 0.2)
        core = nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", d, d), -1.0))
        ends = nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.2), nb.smooth(u, 1.0, 0.8))
        lp = nb.n.new("ShaderNodeLightPath")
        refl = nb.math("MULTIPLY_ADD", lp.outputs["Is Glossy Ray"], -0.5, 1.0)  # its floor mirror at half strength
        return nb.math("MULTIPLY", nb.math("MULTIPLY", nb.math("MULTIPLY", core, ends), refl), HORIZON_S)

    hz.data.materials.append(L.emitter_mat("HorizonMat", EMBER, hz_s, additive=True))
    L.visibility(hz, camera=True, diffuse=False, glossy=True, shadow=False)
    group(hz, "lg_horizon")
    glow = L.plane("HorizonGlow", (160.0, 3.0), (0.0, FAR_Y - 0.2, 0.0), normal_to=(0, -CAM_D, CAM_Z))

    def gl_s(nb):
        u, vv, _ = nb.coords("UV")
        d = nb.math("ABSOLUTE", nb.math("SUBTRACT", vv, 0.5))
        f = nb.math("EXPONENT", nb.math("MULTIPLY", d, -30.0))
        f = nb.math("MULTIPLY", f, nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.25), nb.smooth(u, 1.0, 0.75)))
        return nb.math("MULTIPLY", f, 0.05)

    glow.data.materials.append(L.emitter_mat("HorizonGlowMat", EMBER, gl_s, additive=True))
    L.visibility(glow, camera=True, diffuse=False, glossy=False, shadow=False)
    group(glow, "lg_horizon")

    # --- per racket: spot + column + halo + pool + face band + top line + rim + wall fill + bores + grip + cap
    for i, (r, st, x) in enumerate(zip(roots, stands, xs())):
        g = f"lg_shaft_{i + 1}"
        lit = i < on
        wr = WHITE_RK and ROW[i] == "command"   # this racket is white Command (else black Pace)
        P = C.parts(r)
        head = C.objs(P, "_Head", style="k789")          # face, back, wall, neck
        sp = studio.spot_light(f"Spot{i + 1}", (x, 0.0, SHAFT_TOP), SPOT_W if lit else 0.0,
                               2 * math.degrees(math.atan(SHAFT_R0 * 1.15 / SHAFT_TOP)), 0.55,
                               color=L.kelvin(5600), target=(x, 0.0, 0.0), radius=0.03)
        KS.relink(sp, throat_ex)
        group(sp, g)
        if not lit:
            continue
        col = shaft(f"Shaft{i + 1}", x, SHAFT_S)
        KS.relink(col, floor_c)
        group(col, g)
        # scatter halo: the haze around the beam glows a little, wider and softer than the column
        hal = L.plane(f"Halo{i + 1}", (1.4, 2.4), (x, 0.30, 1.2), normal_to=(x, -CAM_D, 1.2))
        z_core = z_at_frac(0.25)

        def halo_s(nb):
            u, vv, _ = nb.coords("UV")
            du = nb.math("DIVIDE", nb.math("SUBTRACT", u, 0.5), 0.13)
            f = nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", du, du), -1.0))
            z = nb.math("MULTIPLY_ADD", vv, 2.4, 0.0)
            f = nb.math("MULTIPLY", f, nb.math("MULTIPLY_ADD", nb.smooth(z, z_core, z_core - 0.2), 1.0 - SHAFT_HIGH, SHAFT_HIGH))
            f = nb.math("MULTIPLY", f, nb.smooth(z, 2.4, 1.9))
            f = nb.math("MULTIPLY", f, glossy_fade(nb, z))
            return nb.math("MULTIPLY", f, HALO_S)

        hal.data.materials.append(L.emitter_mat(f"Halo{i + 1}Mat", L.kelvin(5600), halo_s, additive=True))
        L.visibility(hal, camera=True, diffuse=False, glossy=True, shadow=False)
        KS.relink(hal, floor_c)
        group(hal, g)
        # (no painted pool decal: the real spot pool, its shadows and the floor's reflection of the column foot
        # carry the light on the floor; a decal there produced straight-edged shards around the stand base)

        c = Vector((x, 0.0, HEAD_Z))
        rot = Matrix.Rotation(math.radians(los(x)), 3, "Z")  # the rig turned with this racket's view

        def at(dx, dy, dz):
            return c + rot @ Vector((dx, dy, dz))

        # top curve (K01 recipe): broad card overhead-behind; only the top bevel can mirror it
        top = L.strip(f"Top{i + 1}", tuple(at(0.0, 0.925, 0.64)), (3.0, 1.6), TOP_S if wr else P_TOP_S, tuple(at(0.0, 0.0, 0.155)),
                      color=L.kelvin(5600), soft_ends=0.45, soft_w=0.25)
        rim_c = KS.coll(f"recv_rim{i}", C.objs(P, "rim"))
        KS.relink(top, rim_c)
        group(top, g)
        # face band: hard-edged card where the face mirrors the camera -> one crisp graded band, rest near-black
        yw = math.radians(YAW + los(x))
        n = Vector((math.sin(yw), -math.cos(yw), 0))
        d = L.mirror_dir(n, c, cam_loc)
        h = Vector((-d.y, d.x, 0)).normalized()
        if h.x < 0:
            h = -h
        bright = (-h + Vector((0, 0, 1.2))).normalized()  # upper-left of the face
        bs_ = KW_BAND if wr else (P_BAND_S if ROW[i] == "pace" else BAND_S)
        if bs_ > 0:
            pace_ = ROW[i] == "pace"
            bd = L.band_card(f"Band{i + 1}", tuple(c + d * 1.5), (0.62, 0.62), bs_, tuple(c),
                             tuple(bright), edge=BAND_EDGE, soft=0.006, decay=P_BAND_DECAY if pace_ else BAND_DECAY,
                             line=P_BAND_LINE if pace_ else BAND_LINE, color=L.kelvin(6000))
            L.link_receivers(bd, head, f"recv_band{i}")
            group(bd, g)
            if wr:
                bd.visible_diffuse = False   # reflection only on white: the coat's gloss band, no diffuse wash
        if ROW[i] == "pace" and P_WEAVE > 0:
            # K08's weave card: above the mirror direction; only one tow orientation's fibre lobe sees it
            hz_axis = Vector((-d.y, d.x, 0)).normalized()
            d_up = (Matrix.Rotation(math.radians(P_WEAVE_UP), 3, hz_axis) @ d).normalized()
            if d_up.z < d.z:
                d_up = (Matrix.Rotation(math.radians(-P_WEAVE_UP), 3, hz_axis) @ d).normalized()
            wv = L.gradient_card(f"Weave{i + 1}", tuple(c + d_up * 1.4), (1.1, 0.62), P_WEAVE, tuple(c),
                                 color=L.kelvin(5800), axis="v", lo=0.0, hi=1.0, floor=0.0)
            L.link_receivers(wv, head, f"recv_weave{i}")
            group(wv, g)
        Mr = r.matrix_world.copy()
        if wr and KW_SWEEP > 0:
            # one soft diagonal clear-coat sweep, designed on the face in model space (the same on all five)
            ca, sa = math.cos(math.radians(KW_SWEEP_ANG)), math.sin(math.radians(KW_SWEEP_ANG))
            c0 = Vector((KW_SWEEP_C[0], KW_SWEEP_C[1], C.ZT))
            dv = Vector((ca, sa, 0.0)) * KW_SWEEP_L
            sw = KS.gloss_sweep(f"Sweep{i + 1}", cam_loc, Mr @ c0, Mr.to_3x3() @ Vector((0, 0, 1)), Mr @ (c0 - dv),
                                Mr @ (c0 + dv), KW_SWEEP_W, KW_SWEEP_H + 0.01 * i, KW_SWEEP, C.objs(P, "face", "neck"),
                                color=L.kelvin(6000))
            group(sw, g)
        if KW_EDGE > 0:
            # the canon edge_ribbon: one crisp white hairline along the upper-left 1.5 mm edge (model space, posed)
            cam_m = Mr.inverted() @ cam_loc
            sm = CT.sm
            rb = CT.edge_ribbon(f"Edge{i + 1}", cam_m, lambda x_, y_: sm(-x_, 0.004, 0.03) * sm(y_, 0.0, 0.06) if x_ < 0 else 0.0,
                                KW_EDGE_PHI, 0.15, 0.03, KW_EDGE * (1.0 if wr else P_EDGE), (0.95, 0.97, 1.0), [P["rim"]])
            if rb:
                rb.matrix_world = Mr
                KS.relink(rb, rim_c)
                group(rb, g)
        if wr:
            recv = C.objs(P, "face", "back", "rim", "wall", "neck", "holes", "etchR", "etchL")   # no throat walls
            recv_c = KS.coll(f"recv_pool{i}", recv)
            if KW_POOL > 0:
                pl = studio.spot_light(f"Pool{i + 1}", tuple(at(*KW_POOL_AT)), KW_POOL, KW_POOL_DEG, blend=1.0,
                                       color=(1.0, 0.985, 0.97), target=tuple(at(KW_POOL_T[0], 0.0, KW_POOL_T[1])),
                                       radius=KW_POOL_R)
                KS.relink(pl, recv_c)
                group(pl, g)
            if KW_FILL > 0:
                fl = L.area_at(f"Fill{i + 1}", at(*KW_FILL_AT), c, 1.0, 1.0, KW_FILL, color=(0.94, 0.96, 1.0))
                KS.relink(fl, recv_c)
                fl.visible_glossy = False
                group(fl, g)
        # right edge: a broad lamp front-right linked to the outline's rounded edges only -> one bright hairline
        rim = studio.area_light(f"Rim{i + 1}", tuple(at(1.10, -0.17, -0.04)), 2.4, RIM_E * (1.0 if wr else P_RIM), color=L.kelvin(5600),
                                size_y=2.0, target=tuple(at(0.12, 0, -0.04)))
        rim.visible_diffuse = False
        KS.relink(rim, rim_c)
        group(rim, g)
        # the 38 mm side wall itself: a dim tall card in its mirror direction, brighter high, fading low,
        # so the wall reads as a graded band behind the hairline (and the wall etch shows against it)
        wn = rot @ Vector((math.cos(math.radians(YAW)), math.sin(math.radians(YAW)), 0))
        wp = c + wn * 0.13 + Vector((0, 0, -0.02))
        dw = L.mirror_dir(wn, wp, cam_loc)
        wl = L.gradient_card(f"WallW{i + 1}", tuple(wp + dw * 1.2), (0.12, 1.2), WALLW_S if wr else P_WALLW_S, tuple(wp),
                             color=L.kelvin(5600), axis="v", lo=0.15, hi=0.95)
        L.link_receivers(wl, head + C.objs(P, "rim", "etchR"), f"recv_wallw{i}")
        group(wl, g)
        # bores: a soft lamp just above the camera, linked to the hole walls only -> every hole a lit crescent
        bl = L.area_at(f"Bore{i + 1}", cam_loc + Vector((0.0, 0.0, 0.5)), c, 0.3, 0.3, BORE_E if wr else P_BORE_E,
                       color=L.kelvin(5200), recv=C.objs(P, "holes"))
        group(bl, g)
        # grip: a long thin strip raking the overgrip from front-right, so the helical wrap catches light
        gp = P["grip"]
        gc = gp.matrix_world.translation
        gs = L.area_at(f"Grip{i + 1}", gc + rot @ Vector((0.30, -0.24, 0.10)), gc, 0.025, 0.45, GRIP_E,
                       color=(0.95, 0.97, 1.0), recv=[gp])   # neutral: a warm strip read the black overgrip as brown
        group(gs, g)
        # cap: satin black anodised with its engraved Q (no chamfer ring any more): a small softbox in the mirror
        # direction of the cap's front band gives it one soft graded highlight
        Mr = r.matrix_world
        pk = Mr @ Vector((0.0, -0.2925, 0.017))
        nk = (Mr.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        dk = L.mirror_dir(nk, pk, cam_loc)
        cr = L.area_at(f"Cap{i + 1}", pk + dk * 0.35, pk, 0.30, 0.10, CAP_E, color=L.kelvin(5600),
                       recv=C.objs(P, "cap", "capmark"))
        group(cr, g)
        # stand: a slim strip front-right draws a line down the polished pin and an arc on the base chamfer
        stp = L.parts(st)
        sl = L.area_at(f"StandL{i + 1}", Vector((x, 0, 0.05)) + rot @ Vector((0.35, -0.55, 0.30)), (x, 0, 0.04),
                       0.04, 0.5, STAND_E, color=L.kelvin(5600), recv=stp)
        group(sl, g)

    L.visual_only("Shaft", "Halo", "Haze", "HorizonGlow", "Wall", "GlossFloor")
    L.debug_off()
    studio.camera(tuple(cam_loc), (0.0, 0.0, CAM_Z), lens=LENS)
    if o.get("seq") and v == "full":
        L.seq_compositor(sc, o, [f"lg_shaft_{k + 1}" for k in range(N)], ["lg_base", "lg_horizon"])
    return sc


if __name__ == "__main__":
    a = L.parse_args(sys.argv[1:], "K07-lineup-five")
    a["seq"] = "--seq" in sys.argv
    L.render_main(build, a)
    L.seq_rename(a)
