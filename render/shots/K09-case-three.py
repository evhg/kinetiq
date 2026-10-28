"""K09-case-three: the 3-pack. Three rackets nested face-up in a machined black anodised aluminium case,
fitted charcoal-felt cavities, lid open at 100 deg with a brushed-steel plaque engraved 'No. 01 / 10'.

Revision 2 (creative-director review): dedicated cameras (4:3 gallery, 4:5 card) instead of a 16:9 master; dark
felt (albedo 0.036, sheen 0.45, AO, darker cut walls and recess floors); a lower raking key that never touches the
lacquer; a neutral hard-edged card in the faces' mirror direction (one clean band across all three faces); satin
bead-blasted shell with chamfers split into their own objects so strips in each edge's mirror direction draw one
continuous silver line (front, right side, lid top, lid side) and the ember rim touches the chamfer only; a visible
3 mm LED slot under the lid lip with a wash down the lining (light plus a camera-only gradient carried by the felt
texture) and a pour onto the felt and racket tips; a stitched felt pocket on the lining; a 230 mm brushed plate
with black-filled, bright-cut engraving and its own band card; a feathered pool on a faintly glossy floor.

Revision 3 (canon, 2026-10-22): the three rackets are the canonical racket (shots/kq_canon.py): one Command build
(KQ-000427) and two clones (KQ-000428, KQ-000429), left to right. 455.0 mm, the crown of 8 + 34 holes with carbon-lined
bores (the old EVA-cored bores under a lamp read as raised studs; the bore lamp now only draws a crescent on each lip and
the felt under the rackets is darker), the one-piece neck into the neutral-black helical overgrip (was brown-tinted and
perforated) and the satin cap with its engraved Q, the logo (was glossy, with a bright collar ring). The felt cut-outs follow the
canon outline, grip and cap. Each throat carries its laser-frosted serial, raked so it reads. Plaque "No. 01 / 10" kept.

Revision 5 (stage 3a critique, white Command): one-piece neck (a neck pool per racket on face + neck: the neck read
black, luma 20, under a white head), one soft gloss sweep per racket instead of the lid band card's hairline, and the
cap's Q as a satin engraving under canon note 5's cap softbox (the strip and key smeared it into a squiggle). Details at
KW_NECK below. Backup of revision 4: shots/K09-case-three.r4-white-precrit.bak.

Usage (from the blender dir):
  ../bpyenv/bin/python shots/K09-case-three.py --w 960 --h 720 --spp 32 --out K09_prev --variant gallery
  --variant gallery     4:3 gallery camera (default; final 2400 x 1800)
  --variant card        4:5 card camera (final 1440 x 1800)
  --variant card-hover  the card with the lid LED brightened (hover state), rendered on its own
  --hover-mix           with --variant card: also write <out>-hover.png (lg_lid x 2.3) and <out>-check.png (all
                        groups x 1, should match the main PNG) from the same render's light-group passes
  --feel pace           the three rackets in the canon Pace v6 (black 12K); finals with -pace in the name:
                        --variant gallery --w 2400 --h 1800 --spp 160 --out final/K09-case-three-gallery-pace
                        --variant card --hover-mix --w 1440 --h 1800 --spp 160 --out final/K09-case-three-card-pace
Optional: --crop x0 x1 y0 y1 (detail check), --lightgroups (lg_key, lg_lid, lg_rim, lg_base; also writes an EXR).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k789_lib as L  # noqa: E402
from k789_lib import NB, Matrix, Vector, bmesh, bpy, racket, studio  # noqa: E402
import kq_canon as C  # noqa: E402
import kw_sheen as KS  # noqa: E402
from mathutils.geometry import tessellate_polygon  # noqa: E402

# ------------------------------------------------------------------ case dimensions (metres)
T = 0.012              # wall thickness
IN_W, IN_D = 0.900, 0.540   # inner (felt) area
W, D = IN_W + 2 * T, IN_D + 2 * T
R_OUT = 0.022          # plan corner radius
Z_RIM = 0.066          # tray rim height
Z_FELT = 0.050         # felt top
Z_CAV = 0.022          # cavity floor (racket rests on it)
LID_H = 0.044          # lid thickness
LID_POCKET = 0.026     # lid pocket depth (felt-lined ceiling)
LID_OPEN = 100.0       # degrees
CHAMFER = 0.0016
PITCH = 0.292          # racket centres
HEAD_Y = IN_D / 2 - 0.036 - 0.155   # head centre: tips 36 mm from the hinge-side wall
CLEAR = 0.0028         # felt clearance around each racket

# ------------------------------------------------------------------ camera and look
LENS = 50.0
CAM_AZ = 32.0          # degrees from the front toward camera-right
CAM_EL = 40.0
CAM_DIST = 2.75
AIM = (0.0, 0.10, 0.21)
# dedicated cameras (no 16:9 master): (case width share, top, bottom) of the frame the case + open lid must fit
FRAMES = {"gallery": (0.80, 0.045, 0.885), "card": (0.90, 0.10, 0.90)}
KEY_W = 650.0
LED = {"full": 12.0, "hover": 26.0}
HOVER_GAIN = 2.3        # --hover-mix: the hover still = lg_lid x 2.3 (matches the card-hover variant)
PAINT_S = {"full": 0.05, "hover": 0.11}  # camera-only LED gradient on the lining      # wash down the lining (area-light watts, 84 cm strip)
POUR = {"full": 2.2, "hover": 6.0}    # the same slot's light pouring forward onto the felt and racket tips
SLOT_S = {"full": 9.0, "hover": 20.0}  # the visible 3 mm diffuser
LED_EDGE = 15.0
PLAQUE_Y = -0.085      # plaque centre along the lining, from the lid centre toward the free edge (closed coords: -y)
PLAQUE_S = 2.6
FLOOR_E = (0.030, 0.052)
VOID_E = (0.024, 0.062)
LED_COL = "#ff9a4a"
RIM_S = 70.0
FACE_S = float(os.environ.get('K09_FACE', 4.5))
FACE_EDGE = -0.02
CHAMFER_S = 9.0
SATIN_S = 0.30
FACE_DECAY, FACE_SOFT, FACE_LINE = 0.02, 0.003, 1.4   # canon note 1: a band (16-70 mm on the face), not a half-plane
GRIP_E = 1.0
BORE_E, BORE_SIZE = 6.0, 0.25     # hole-lip crescents (canon 'holes' part only)
RAKE_E = float(os.environ.get("K09_RAKE", 0.8))                       # serial rake per racket (K10's rake)
SERIALS = ("KQ-000427", "KQ-000428", "KQ-000429")
FELT_ALB = 0.036
FELT_DEEP = 0.15                   # felt darkening with depth: the cavity floors under the rackets (was 0.28)

# Revision 4 (owner, 2026-10-22): Command is WHITE 3K twill. Reflection-only light (the band card) leaves white a flat
# grey and its diffuse spill floods the faces, so a white racket gets real diffuse light per racket, linked to that
# racket's head parts only (canon lighting note 8): a soft spot pool from the frame's left, aimed at the upper left of
# the head (white at the crown falling to white-in-shade at the throat; the three rackets read identical); a weak fill
# from the front right; the face card becomes reflection-only (one clear-coat gloss band, no diffuse wash); the LED's
# warm edge line and the hole-lip lamp are dimmed (white takes 20x more of them than black carbon did).
FEEL, MAT_OPTS = "command", None
# --feel pace (Release 2 feel toggle, 2026-10-23): the three rackets in the canon Pace v6 (kq_canon.PACE, black 12K,
# mat_opts None), same case, cameras, crops and lid/case lights; the rackets get the black-carbon rig (WHITE_RK False:
# the lid's band card in the faces' mirror direction, the bore lamp, the serial rakes, grip strips on grip + cap) with
# K08 / K11 / K06's Pace recipe: the band dimmed (P_FACE_S), an off-specular weave card only the 12K's fibre lobes see
# (P_WEAVE_*), an indirect clamp (P_CLAMP, 12K fireflies) and no warm line on the racket rims (P_LED_EDGE: the LED's
# edge line, neutral to the eye at this level). Command (the default) is unchanged.
if "--feel" in sys.argv:
    FEEL = sys.argv[sys.argv.index("--feel") + 1]
    assert FEEL in ("command", "pace"), FEEL
PACE = FEEL == "pace"
P_FACE_S = 3.5                     # the lid band card on Pace (FACE_S 4.5 was tuned on the baked black 3K twill)
P_WEAVE_S, P_WEAVE_UP, P_WEAVE_D, P_WEAVE_SIZE = 4.0, 20.0, 1.3, (1.8, 1.0)   # weave card (W, deg off the mirror, m, m)
P_CLAMP = 4.0
P_LED_EDGE = 0.0                   # no warm LED line on the Pace rims (no ember on the racket)
P_BORE_E = 6.0
P_LID_S, P_LID_FLOOR = 0.6, 0.35       # Pace: a dim neutral card standing in for the lining in the faces' reflection
P_LINING_GLOSSY = 0.0              # 0: the lid lining is not mirrored by glossy rays (Pace only)
WHITE_RK = C.is_white(FEEL, MAT_OPTS)
KW_POOL, KW_POOL_DEG, KW_POOL_R = 240.0, 17.0, 0.06
KW_POOL_AT, KW_POOL_T = (-0.80, -0.15, 0.95), (-0.06, 0.06)   # from each head centre (world, m); aim offset (X, Y)
KW_FILL, KW_FILL_AT = 1.5, (0.90, -0.90, 0.70)
KW_FACE = 4.0                      # reflection-only face band on white (a soft clear-coat sheen over the crowns)
# Revision 5 (art director, stage 3a, 2026-10-22):
# - the neck and throat rendered black (luma ~20 under a head of ~150): the pools never reached them, so each racket read
#   as a white head on a separate black handle. A second soft spot per racket (KW_NECK), from the pool's side, aimed at
#   the neck and linked to the face, neck, rim and wall (the same parts on both sides of the face/neck split, so no
#   tone step at y -0.150; not the throat walls or the bores, which stay dark openings): the neck reads white in shade
#   and runs on from the head, as in canon front_command.
# - the shared lid band card drew a straight hairline across every face (its hot edge line): on white it is replaced
#   by one soft gloss sweep per racket (kw_sheen.gloss_sweep: glossy-only, honeycomb, smoothstep profile), identical on
#   all three; KW_FACE is 0 on white.
# - the engraved Q, seen edge-on under the raking key and the grip strip, smeared into a white squiggle (no autographs):
#   the strip lit the cap's end round the Q, so the dark mark cut a squiggle out of a hot highlight. On white the strip
#   lights the grip only and the key the cap only (its satin edge arc); the cap and its Q get canon note 5's soft cap
#   softbox (KW_CAP), so the Q reads as a quiet satin engraving, and the mark turns MARK_AZ about the handle axis toward
#   the camera (the cap itself does not turn).
KW_NECK, KW_NECK_DEG, KW_NECK_Y = 60.0, 11.0, -0.170   # W, cone (deg), model y of the aim point (the neck; 70 W gave 143)
KW_SWEEP, KW_SWEEP_W, KW_SWEEP_H = 5.0, 0.026, 0.07     # strength, half width on the face (m), card height (m)
KW_SWEEP_C, KW_SWEEP_ANG, KW_SWEEP_L = (0.0, -0.035), -32.0, 0.17   # centre (model x, y), angle (deg), half length
KW_CAP = 0.30                      # canon note 5: a 30 cm softbox in the mirror direction of each cap's front band (W)
MARK_AZ = 30.0                     # deg: the Q turned toward the camera (camera azimuth about the handle axis)
if WHITE_RK:
    BORE_E, LED_EDGE = 2.0, 6.0
    KW_FACE = 0.0
for _kv in filter(None, os.environ.get("K09_SET", "").split(",")):   # look-dev: K09_SET="KW_POOL=150,KW_FILL=2"
    _k, _v = _kv.split("=")
    _cur = globals()[_k]
    globals()[_k] = tuple(float(x) for x in _v.split(":")) if isinstance(_cur, tuple) else float(_v)
    print("set", _k, globals()[_k], flush=True)
if PACE:
    FACE_S, LED_EDGE, BORE_E = P_FACE_S, P_LED_EDGE, P_BORE_E


# ------------------------------------------------------------------ geometry helpers

def rrect(w, d, r, n=14):
    """Rounded rectangle, CCW, centred at the origin."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def area(lp):
    return 0.5 * sum(lp[i][0] * lp[(i + 1) % len(lp)][1] - lp[(i + 1) % len(lp)][0] * lp[i][1] for i in range(len(lp)))


def ccw(lp):
    return lp if area(lp) > 0 else lp[::-1]


def cw(lp):
    return lp[::-1] if area(lp) > 0 else lp


def add_cap(bm, loops, z, up=True, mat=0):
    """Fill outer loop (first) minus holes at height z, facing +Z (up) or -Z."""
    rings = [[bm.verts.new((x, y, z)) for (x, y) in lp] for lp in loops]
    flat = [v for r in rings for v in r]
    tris = tessellate_polygon([[Vector((x, y, 0)) for (x, y) in lp] for lp in loops])
    for a, b, c in tris:
        try:
            f = bm.faces.new((flat[a], flat[b], flat[c]) if up else (flat[c], flat[b], flat[a]))
            f.material_index = mat
        except ValueError:
            pass
    return rings


def add_wall(bm, ring_lo, ring_hi, mat=0):
    n = len(ring_lo)
    for k in range(n):
        j = (k + 1) % n
        f = bm.faces.new((ring_lo[k], ring_lo[j], ring_hi[j], ring_hi[k]))
        f.material_index = mat


def finish(bm, name, mats, smooth_angle=35):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for m in mats:
        me.materials.append(m)
    return ob


def shell(name, z0, z_rim, z_inner, mats, inner_mat=0):
    """Machined tray: outer rounded box from z0 to z_rim with a rounded pocket down to z_inner.
    Every machined edge gets a polished chamfer (material 1)."""
    outer = ccw(rrect(W, D, R_OUT))
    inner = ccw(rrect(IN_W, IN_D, R_OUT - T * 0.6))
    bm = bmesh.new()
    top_o = [bm.verts.new((x, y, z_rim)) for (x, y) in outer]
    top_i = [bm.verts.new((x, y, z_rim)) for (x, y) in inner]
    tris = tessellate_polygon([[Vector((x, y, 0)) for (x, y) in outer], [Vector((x, y, 0)) for (x, y) in inner]])
    flat = top_o + top_i
    for a, b, c in tris:
        try:
            bm.faces.new((flat[a], flat[b], flat[c]))
        except ValueError:
            pass
    bot_o = [bm.verts.new((x, y, z0)) for (x, y) in outer]
    add_wall(bm, bot_o, top_o)
    f = bm.faces.new(bot_o[::-1])
    floor_i = [bm.verts.new((x, y, z_inner)) for (x, y) in inner]
    add_wall(bm, top_i, floor_i)  # inner wall faces inward (normals fixed by recalc)
    f = bm.faces.new(floor_i)
    f.material_index = inner_mat
    ob = finish(bm, name, mats)
    bv = ob.modifiers.new("chamfer", "BEVEL")
    bv.limit_method = "ANGLE"
    bv.angle_limit = math.radians(60)
    bv.width = CHAMFER
    bv.segments = 1
    bv.material = 1
    bv.use_clamp_overlap = False  # the tessellated rim would otherwise clamp the chamfer to ~0.2 mm
    bv.harden_normals = True
    racket._apply_all(ob)
    me = ob.data
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(30))
    return ob


def split_material(ob, idx, name):
    """Move the faces with material index idx into their own object (same transform, same materials), so lights
    can be linked to the polished chamfers alone."""
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    b2 = bm.copy()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == idx], context="FACES")
    bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index != idx], context="FACES")
    bm.to_mesh(me); bm.free()
    me2 = bpy.data.meshes.new(name)
    b2.to_mesh(me2); b2.free()
    for m in me.materials:
        me2.materials.append(m)
    ob2 = bpy.data.objects.new(name, me2)
    bpy.context.scene.collection.objects.link(ob2)
    ob2.matrix_world = ob.matrix_world.copy()
    for p_ in me2.polygons:
        p_.use_smooth = True
    return ob2


def cavity_polys(xs):
    """Felt cut-outs: each canon racket's plan (head + neck, the 34 mm overgrip, the 37 mm cap with its rounded end)
    grown by the clearance, plus a thumb notch."""
    from shapely.geometry import Point, Polygon, box as sbox
    from shapely.ops import unary_union
    head = C.outline_canon(step=0.002)
    polys = []
    for x in xs:
        hp = Polygon([(x + px, HEAD_Y + py) for (px, py) in head])
        grip = sbox(x - 0.0172, HEAD_Y + C.GRIP_Y[1], x + 0.0172, HEAD_Y - 0.165)
        cap = sbox(x - 0.0187, HEAD_Y + C.BUTT_Y, x + 0.0187, HEAD_Y - 0.2817).buffer(-0.006).buffer(0.006)
        notch = Point(x + 0.034, HEAD_Y - 0.215).buffer(0.024, resolution=16)
        p = unary_union([hp, grip, cap, notch]).buffer(CLEAR, join_style=1, resolution=12)
        p = p.buffer(-0.004, join_style=1, resolution=12).buffer(0.004, join_style=1, resolution=12)  # round inner corners
        p = p.simplify(0.0002)
        polys.append(ccw(list(p.exterior.coords)[:-1]))
    return polys


def felt_insert(name, xs, mat):
    inner = ccw(rrect(IN_W - 0.0006, IN_D - 0.0006, R_OUT - T * 0.6))
    cav = cavity_polys(xs)
    bm = bmesh.new()
    rings = add_cap(bm, [inner] + [cw(c) for c in cav], Z_FELT, up=True)
    for k, c in enumerate(cav):
        lo = add_cap(bm, [c], Z_CAV, up=True)
        add_wall(bm, lo[0], rings[1 + k][::-1])
    ob = finish(bm, name, [mat])
    # felt edges are cut, not machined: a soft 1.2 mm round
    bv = ob.modifiers.new("soft", "BEVEL")
    bv.limit_method = "ANGLE"
    bv.angle_limit = math.radians(50)
    bv.width = 0.0012
    bv.segments = 3
    bv.use_clamp_overlap = False
    racket._apply_all(ob)
    ob.data.shade_smooth()
    ob.data.set_sharp_from_angle(angle=math.radians(50))
    return ob


# ------------------------------------------------------------------ materials

def mat_anodised(name="Anodised"):
    """Satin black anodised aluminium: dark metallic, roughness ~0.4 with bead-blast micro variation."""
    m = L.new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    b.inputs["Base Color"].default_value = (0.034, 0.034, 0.037, 1)
    b.inputs["Metallic"].default_value = 1.0
    tc = nb.n.new("ShaderNodeTexCoord")
    nz = nb.n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2800; nz.inputs["Detail"].default_value = 2
    nz2 = nb.n.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 40; nz2.inputs["Detail"].default_value = 3
    for t in (nz, nz2):
        nb.l.new(tc.outputs["Object"], t.inputs["Vector"])
    r = nb.math("MULTIPLY_ADD", nz.outputs["Fac"], 0.08, 0.36)
    r = nb.math("MULTIPLY_ADD", nz2.outputs["Fac"], 0.05, r)
    nb.l.new(r, b.inputs["Roughness"])
    bump = nb.n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.00004
    nb.l.new(nz.outputs["Fac"], bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_chamfer(name="Chamfer"):
    return racket.mat_basic(name, (0.86, 0.86, 0.88), rough=0.05, metallic=1.0)


def mat_felt(name="Felt", alb=FELT_ALB, glossy_dim=1.0, wall_dim=0.35, ao=True, stitch=None, depth_dim=1.0, paint=None):
    """Charcoal felt, albedo ~0.036 with a soft sheen that only wakes at cut edges and fibres at grazing light.
    Cut walls (horizontal normals) are darker and the contact areas take ambient occlusion, so cavities read
    as recesses. glossy_dim < 1 darkens it as seen in reflections only (the lid lining over the lacquer)."""
    m = L.new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    tc = nb.n.new("ShaderNodeTexCoord")
    fib = nb.n.new("ShaderNodeTexNoise"); fib.inputs["Scale"].default_value = 1400; fib.inputs["Detail"].default_value = 6
    fib.inputs["Roughness"].default_value = 0.7
    nap = nb.n.new("ShaderNodeTexNoise"); nap.inputs["Scale"].default_value = 260; nap.inputs["Detail"].default_value = 4
    mot = nb.n.new("ShaderNodeTexNoise"); mot.inputs["Scale"].default_value = 45; mot.inputs["Detail"].default_value = 3
    for t in (fib, nap, mot):
        nb.l.new(tc.outputs["Object"], t.inputs["Vector"])
    v = nb.math("MULTIPLY_ADD", nb.smooth(mot.outputs["Fac"], 0.3, 0.7), 0.14, 0.93)
    v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", fib.outputs["Fac"], 0.35, 0.83))
    v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", nap.outputs["Fac"], 0.2, 0.9))
    # cut walls darker (object normal nearly horizontal)
    nz_ = nb.n.new("ShaderNodeSeparateXYZ"); nb.l.new(tc.outputs["Normal"], nz_.inputs[0])
    wall = nb.smooth(nb.math("ABSOLUTE", nz_.outputs["Z"]), 0.55, 0.25)
    v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", wall, wall_dim - 1.0, 1.0))
    if depth_dim < 1.0:
        _, _, zz = nb.coords("Object")
        v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", nb.smooth(zz, Z_FELT - 0.003, Z_FELT - 0.016), depth_dim - 1.0, 1.0))
    if ao:
        aon = nb.n.new("ShaderNodeAmbientOcclusion"); aon.inputs["Distance"].default_value = 0.04; aon.samples = 8
        v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", aon.outputs["AO"], 0.75, 0.25))
    if stitch is not None:
        # a saddle-stitched seam: 4 mm stitches, 2 mm gaps, along local X at local y = stitch (lighter thread)
        x, y, _ = nb.coords("Object")
        dy = nb.math("ABSOLUTE", nb.math("SUBTRACT", y, stitch))
        line = nb.smooth(dy, 0.0011, 0.0004)
        dash = nb.smooth(nb.math("ABSOLUTE", nb.math("SUBTRACT", nb.math("FRACT", nb.math("DIVIDE", x, 0.006)), 0.4)), 0.34, 0.26)
        st = nb.math("MULTIPLY", line, dash)
        groove = nb.smooth(dy, 0.0022, 0.0008)
        v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", groove, -0.5, 1.0))
        v = nb.math("ADD", v, nb.math("MULTIPLY", st, 1.6))
        bp2 = nb.n.new("ShaderNodeBump"); bp2.inputs["Strength"].default_value = 0.6; bp2.inputs["Distance"].default_value = 0.0006
        nb.l.new(nb.math("SUBTRACT", st, groove), bp2.inputs["Height"])
    if glossy_dim < 1.0:
        lpn = nb.n.new("ShaderNodeLightPath")
        v = nb.math("MULTIPLY", v, nb.math("MULTIPLY_ADD", lpn.outputs["Is Glossy Ray"], glossy_dim - 1.0, 1.0))
    cc = nb.n.new("ShaderNodeCombineColor")
    for k, f in enumerate((1.0, 1.0, 1.04)):
        nb.l.new(nb.math("MULTIPLY", v, alb * f), cc.inputs[k])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    if paint is not None:
        # the LED's wash on the lining, seen by the camera only (never by the lacquer): a warm gradient from the
        # slot down the felt, carried by the felt's own texture so it reads as lit fibre, not a glowing panel
        strength, y0, y1, colr = paint
        _, py, _ = nb.coords("Object")
        gr_ = nb.math("POWER", nb.smooth(py, y1, y0), 1.6)
        lpp = nb.n.new("ShaderNodeLightPath")
        e_ = nb.math("MULTIPLY", nb.math("MULTIPLY", gr_, nb.math("DIVIDE", v, 0.93)), strength)
        nb.l.new(nb.math("MULTIPLY", e_, lpp.outputs["Is Camera Ray"]), b.inputs["Emission Strength"])
        b.inputs["Emission Color"].default_value = (*colr, 1)
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Specular IOR Level"].default_value = 0.15
    b.inputs["Sheen Weight"].default_value = 0.45
    b.inputs["Sheen Roughness"].default_value = 0.35
    b.inputs["Sheen Tint"].default_value = (0.55, 0.55, 0.57, 1)
    bump = nb.n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.4; bump.inputs["Distance"].default_value = 0.0003
    nb.l.new(fib.outputs["Fac"], bump.inputs["Height"])
    if stitch is not None:
        nb.l.new(bump.outputs["Normal"], bp2.inputs["Normal"])
        nb.l.new(bp2.outputs["Normal"], b.inputs["Normal"])
    else:
        nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_brushed_steel(name="BrushedSteel"):
    """Brushed stainless: anisotropic along the plate's long axis (local X), fine directional streaks."""
    m = L.new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    b.inputs["Base Color"].default_value = (0.42, 0.42, 0.43, 1)
    b.inputs["Metallic"].default_value = 1.0
    tc = nb.n.new("ShaderNodeTexCoord")
    mp = nb.n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (3.0, 3200.0, 3200.0)
    nb.l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nb.n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 5
    nb.l.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nb.l.new(nb.math("MULTIPLY_ADD", nz.outputs["Fac"], 0.08, 0.15), b.inputs["Roughness"])
    b.inputs["Anisotropic"].default_value = 0.85
    vt = nb.n.new("ShaderNodeVectorTransform")
    vt.vector_type = "VECTOR"; vt.convert_from = "OBJECT"; vt.convert_to = "WORLD"
    vt.inputs[0].default_value = (1.0, 0.0, 0.0)
    nb.l.new(vt.outputs[0], b.inputs["Tangent"])
    bump = nb.n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15; bump.inputs["Distance"].default_value = 0.00004
    nb.l.new(nz.outputs["Fac"], bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_engraved(name="Engraved"):
    """Engraved letters: black-filled floors (lacquer fill), bright-cut polished walls catching the light."""
    m = L.new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    fill = nb.n.new("ShaderNodeBsdfPrincipled")
    fill.inputs["Base Color"].default_value = (0.012, 0.012, 0.013, 1)
    fill.inputs["Roughness"].default_value = 0.35
    cut = nb.n.new("ShaderNodeBsdfPrincipled")
    cut.inputs["Base Color"].default_value = (0.92, 0.92, 0.93, 1)
    cut.inputs["Metallic"].default_value = 1.0
    cut.inputs["Roughness"].default_value = 0.06
    tc = nb.n.new("ShaderNodeTexCoord")
    sep = nb.n.new("ShaderNodeSeparateXYZ"); nb.l.new(tc.outputs["Normal"], sep.inputs[0])
    floor_ = nb.smooth(nb.math("ABSOLUTE", sep.outputs["Z"]), 0.6, 0.9)
    mix = nb.n.new("ShaderNodeMixShader")
    nb.l.new(floor_, mix.inputs[0])
    nb.l.new(cut.outputs[0], mix.inputs[1]); nb.l.new(fill.outputs[0], mix.inputs[2])
    nb.l.new(mix.outputs[0], out.inputs["Surface"])
    return m


def plaque(name, steel, engr):
    """Brushed steel plate 230 x 60 x 2.5 mm, polished 0.4 mm chamfer, 'No. 01 / 10' engraved 0.4 mm deep
    (black-filled, bright-cut walls). Built lying in XY (engraved face +Z) at the origin."""
    pw, ph, pt = 0.230, 0.060, 0.0025
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, pt / 2))
    pl = bpy.context.active_object
    pl.name = name
    pl.scale = (pw, ph, pt)
    bpy.ops.object.transform_apply(scale=True)
    pl.data.materials.append(steel)
    pl.data.materials.append(engr)
    bv = pl.modifiers.new("c", "BEVEL"); bv.width = 0.0004; bv.segments = 2
    racket._apply_all(pl)
    depth = 0.0004
    txt = racket.build_text("No. 01 / 10", 0.0265, (0, -0.0008, 0), racket.FONT_MED, name + "_Txt", None,
                            extrude=0.0007, spacing=1.10)
    me = bpy.data.meshes.new_from_object(txt.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(txt)
    cut = bpy.data.objects.new(name + "_Cut", me)
    bpy.context.scene.collection.objects.link(cut)
    cut.location = (0, -0.0008, pt - depth + 0.0007)
    cut.data.materials.append(engr)
    bo = pl.modifiers.new("engrave", "BOOLEAN")
    bo.operation = "DIFFERENCE"
    bo.solver = "EXACT"
    bo.object = cut
    try:
        bo.material_mode = "TRANSFER"
    except Exception:
        pass
    racket._apply_all(pl)
    bpy.data.objects.remove(cut)
    pl.data.shade_flat()
    return pl


def pocket_panel(name, mat):
    """Felt-covered padded pocket on the lid lining (closed coords: lies in XY, face +Z), 840 x 205 x 7 mm with
    soft 3 mm rounded edges and a stitched seam 11 mm below its top edge. Built at the origin."""
    w, h, t = 0.840, 0.205, 0.007
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, t / 2))
    pp = bpy.context.active_object
    pp.name = name
    pp.scale = (w, h, t)
    bpy.ops.object.transform_apply(scale=True)
    bv = pp.modifiers.new("soft", "BEVEL"); bv.width = 0.003; bv.segments = 5; bv.use_clamp_overlap = False
    racket._apply_all(pp)
    pp.data.shade_smooth()
    pp.data.materials.append(mat)
    return pp


# ------------------------------------------------------------------ the shot

def frame(camo, objs, fw, top, bottom):
    """Dolly along the view axis and shift the lens so the objects fit `fw` of the width and the band top..bottom
    (fractions from the top), whichever binds; centred horizontally and in that band."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    pts = []
    for ob in objs:
        mw = ob.matrix_world
        vs = ob.data.vertices
        pts += [mw @ vs[k].co for k in range(0, len(vs), 5)]
    aim = Vector(AIM)

    def ext():
        bpy.context.view_layer.update()
        ys = [1 - world_to_camera_view(sc, camo, p).y for p in pts]
        xs_ = [world_to_camera_view(sc, camo, p).x for p in pts]
        return min(xs_), max(xs_), min(ys), max(ys)

    for _ in range(5):
        x0, x1, y0, y1 = ext()
        k = max((y1 - y0) / (bottom - top), (x1 - x0) / fw)
        camo.location = aim + (camo.location - aim) * k
        x0, x1, y0, y1 = ext()
        ar = sc.render.resolution_x / sc.render.resolution_y
        # Blender's shift is in units of the larger frame side
        big = max(ar, 1.0)
        camo.data.shift_y -= ((y0 + y1) / 2 - (top + bottom) / 2) / (big / ar if ar >= 1 else 1.0 / 1.0) * (1.0 / ar if ar >= 1 else 1.0)
        camo.data.shift_x += ((x0 + x1) / 2 - 0.5) * (1.0 if ar >= 1 else ar)
    x0, x1, y0, y1 = ext()
    print(f"framing: x {x0:.3f}-{x1:.3f}  y {y0:.3f}-{y1:.3f}  dist {(camo.location - aim).length:.3f}"
          f"  shift {camo.data.shift_x:.4f} {camo.data.shift_y:.4f}", flush=True)
    camo.data.dof.focus_distance = (camo.location - Vector((0, 0.05, 0.10))).length


def CT_look_at(ob, loc, tgt, up):
    """Light orientation with an explicit world up (canon_test.look_at)."""
    fwd = (Vector(tgt) - Vector(loc)).normalized()
    rt = fwd.cross(Vector(up)).normalized()
    upv = rt.cross(fwd)
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ Matrix((rt, upv, -fwd)).transposed().to_4x4()


def to_world(M, v):
    return (M @ Vector(v).to_4d()).to_3d() if len(v) == 3 else M @ v


def build(o):
    v = o["variant"]
    cam_kind = "card" if v.startswith("card") else "gallery"
    led_kind = "hover" if v.endswith("hover") else "full"
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.light_sampling_threshold = 0.0
    if PACE and P_CLAMP > 0:
        sc.cycles.sample_clamp_indirect = P_CLAMP
    group = L.Groups(o["lightgroups"] or o.get("hover_mix"))

    anod, cham, felt = mat_anodised(), mat_chamfer(), mat_felt(depth_dim=FELT_DEEP)
    steel = mat_brushed_steel()
    engr = mat_engraved()

    # --- tray, felt, rackets
    tray = shell("Tray", 0.0, Z_RIM, Z_FELT - 0.004, [anod, cham, felt], inner_mat=2)
    tray_ch = split_material(tray, 1, "TrayChamfer")
    xs = [-PITCH, 0.0, PITCH]
    ins = felt_insert("Felt", xs, felt)
    # the canonical racket, three times: KQ-000427, -428, -429 left to right (camera right is world +X)
    src, _ = C.build_racket("KQA", feel=FEEL, serial=SERIALS[0], mat_opts=MAT_OPTS, mark_az=MARK_AZ)
    roots = [src] + [C.clone(src, nm, serial=sr)[0] for nm, sr in (("KQB", SERIALS[1]), ("KQC", SERIALS[2]))]
    for r, x in zip(roots, xs):
        C.pose(r, (x, HEAD_Y, Z_CAV + C.T2 + 0.0004), tilt_deg=0.0)
    bpy.context.view_layer.update()
    Ps = [C.parts(r) for r in roots]
    heads = [o_ for P in Ps for o_ in C.objs(P, "_Head", style="k789")]      # face, back, wall, neck
    bevels = [o_ for P in Ps for o_ in C.objs(P, "rim")]                      # the 1.5 mm rounded edges
    lips = [o_ for P in Ps for o_ in C.objs(P, "holes")]                      # hole lips + carbon-lined bores
    inners = [o_ for P in Ps for o_ in C.objs(P, "holes", "throat", "bridgewall")]
    small = [o_ for P in Ps for o_ in C.objs(P, "grip", "cap", "capmark")]

    # --- lid: built closed (sitting on the rim, pocket facing down), then swung open about the back top edge
    lining = mat_felt("Lining", glossy_dim=0.05, wall_dim=0.6, ao=False,
                      paint=(PAINT_S[led_kind], -IN_D / 2, 0.06, L.hex_lin(LED_COL)))
    lid = shell("Lid", 0.0, LID_H, LID_H - LID_POCKET, [anod, cham, lining], inner_mat=2)
    lid.data.transform(Matrix.Translation((0, 0, Z_RIM + LID_H)) @ Matrix.Rotation(math.pi, 4, "X"))
    lid_ch = split_material(lid, 1, "LidChamfer")
    lid_ln = split_material(lid, 2, "LidLining")
    ceil_z = Z_RIM + LID_POCKET
    FLIP = Matrix.Rotation(math.pi, 4, "X")
    pl = plaque("Plaque", steel, engr)
    pl.matrix_world = Matrix.Translation((0, PLAQUE_Y, ceil_z)) @ FLIP
    # stitched felt pocket in the lining's lower part (toward the hinge)
    pocket_mat = mat_felt("PocketFelt", alb=FELT_ALB * 1.05, glossy_dim=0.05, wall_dim=0.7, ao=False, stitch=0.205 / 2 - 0.011,
                          paint=(PAINT_S[led_kind] * 0.35, 0.205 / 2, -0.205 / 2, L.hex_lin(LED_COL)))
    pk = pocket_panel("Pocket", pocket_mat)
    pk_y = IN_D / 2 - 0.205 / 2 - 0.012
    # closed coords: +y is toward the hinge; the panel's local +y (its top edge, the stitched one) faces the free edge
    pk.matrix_world = Matrix.Translation((0, pk_y, ceil_z)) @ FLIP
    OPEN = (Matrix.Translation((0, D / 2, Z_RIM)) @ Matrix.Rotation(math.radians(-LID_OPEN), 4, "X")
            @ Matrix.Translation((0, -D / 2, -Z_RIM)))
    for ob in (lid, lid_ch, lid_ln, pl, pk):
        ob.matrix_world = OPEN @ ob.matrix_world
    group(lid_ln, "lg_lid")   # the lining's painted LED wash is emission: it belongs to the lid group
    if PACE and P_LINING_GLOSSY == 0:
        # Pace: the black 12K faces mirrored the LED-washed lining as a warm orange band (an ember look on the racket);
        # the lining and its pocket stay visible to the camera and to diffuse rays, not to glossy ones
        for ob_ in (lid_ln, pk):
            ob_.visible_glossy = False
    group(pk, "lg_lid")
    R = OPEN.to_3x3()
    up_lid = (R @ Vector((0, -1, 0))).normalized()      # hinge -> free edge, along the open lid
    lining_n = (R @ Vector((0, 0, -1))).normalized()    # the lining faces forward, slightly up

    # --- lg_lid: a visible 3 mm diffuser slot under the lid's inner top lip ...
    slot_c = OPEN @ Vector((0, -IN_D / 2 + 0.0045, ceil_z - 0.0006))
    slot = L.plane("LidSlot", (IN_W - 0.06, 0.0032), tuple(slot_c), normal_to=tuple(slot_c + lining_n))
    bpy.context.view_layer.update()
    # make its long axis world X
    zax = lining_n; xax = Vector((1, 0, 0)); yax = zax.cross(xax).normalized(); xax = yax.cross(zax).normalized()
    slot.matrix_world = Matrix(((xax.x, yax.x, zax.x, slot_c.x), (xax.y, yax.y, zax.y, slot_c.y),
                                (xax.z, yax.z, zax.z, slot_c.z), (0, 0, 0, 1)))

    def slot_s(nb):
        u, vv, _ = nb.coords("UV")
        ends = nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.02), nb.smooth(u, 1.0, 0.98))
        core = nb.math("MULTIPLY_ADD", nb.math("MULTIPLY", nb.smooth(vv, 0.0, 0.35), nb.smooth(vv, 1.0, 0.65)), 0.6, 0.4)
        return nb.math("MULTIPLY", nb.math("MULTIPLY", ends, core), SLOT_S[led_kind])

    slot.data.materials.append(L.emitter_mat("LidSlotMat", L.hex_lin(LED_COL), slot_s, additive=False))
    L.visibility(slot, camera=True, diffuse=False, glossy=False, shadow=False)
    slot.data.materials[0].cycles.emission_sampling = "NONE"
    group(slot, "lg_lid")

    def bar_light(name, energy, direction, recv, col=LED_COL):
        ld = bpy.data.lights.new(name, "AREA")
        ld.shape = "RECTANGLE"; ld.size = IN_W - 0.06; ld.size_y = 0.004
        ld.energy = energy; ld.color = L.hex_lin(col)
        ob = bpy.data.objects.new(name, ld)
        bpy.context.scene.collection.objects.link(ob)
        zx = -direction.normalized(); xx = Vector((1, 0, 0)); yx = zx.cross(xx).normalized(); xx = yx.cross(zx)
        c_ = slot_c - lining_n * 0.0 + direction.normalized() * 0.002
        ob.matrix_world = Matrix(((xx.x, yx.x, zx.x, c_.x), (xx.y, yx.y, zx.y, c_.y), (xx.z, yx.z, zx.z, c_.z), (0, 0, 0, 1)))
        ob.visible_camera = False
        L.link_receivers(ob, recv, "recv_" + name)
        group(ob, "lg_lid")
        return ob

    down_lining = (R @ Vector((0, 1, 0))).normalized()   # free edge -> hinge, along the lining
    # ... its wash grazing down the lining (the gradient that shows the slot is the source)
    bar_light("LidWash", LED[led_kind], (down_lining * 0.55 + lining_n * 0.45), [lid_ln, pk])
    # ... its light pouring forward onto the felt and the tray rim (never the rackets: on the overgrips it read brown)
    bar_light("LidPour", POUR[led_kind], (down_lining * 0.55 + lining_n * 0.45), [ins, tray, tray_ch])
    # ... and as seen by the heads' rounded edges: each top edge catches one warm hairline
    bar_light("LidEdge", LED_EDGE * (2.0 if led_kind == "hover" else 1.0), (down_lining * 0.55 + lining_n * 0.45), bevels)

    # --- studio: faint glossy floor, and a void that lifts behind the lid (camera only)
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    fm = L.new_mat("FloorMat")
    nb = NB(fm)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    b.inputs["Base Color"].default_value = (0.012, 0.012, 0.013, 1)
    x, y, _ = nb.coords("Object")
    tcf = nb.n.new("ShaderNodeTexCoord")
    fr = nb.n.new("ShaderNodeTexNoise"); fr.inputs["Scale"].default_value = 30.0; fr.inputs["Detail"].default_value = 4
    nb.l.new(tcf.outputs["Object"], fr.inputs["Vector"])
    nb.l.new(nb.math("MULTIPLY_ADD", fr.outputs["Fac"], 0.05, 0.10), b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.5
    xx_ = nb.math("MULTIPLY", x, 0.75)
    yy_ = nb.math("SUBTRACT", y, 0.35)
    r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", xx_, xx_), nb.math("MULTIPLY", yy_, yy_)))
    e = nb.math("MULTIPLY_ADD", nb.smooth(r, 2.6, 0.3), FLOOR_E[1] - FLOOR_E[0], FLOOR_E[0])
    gr = nb.n.new("ShaderNodeTexWhiteNoise"); gr.noise_dimensions = "3D"
    mpg = nb.n.new("ShaderNodeMapping"); mpg.inputs["Scale"].default_value = (1500.0, 1500.0, 1500.0)
    nb.l.new(tcf.outputs["Object"], mpg.inputs["Vector"]); nb.l.new(mpg.outputs["Vector"], gr.inputs["Vector"])
    e = nb.math("MULTIPLY", e, nb.math("MULTIPLY_ADD", gr.outputs["Value"], 0.07, 0.965))
    lp = nb.n.new("ShaderNodeLightPath")
    nb.l.new(nb.math("MULTIPLY", e, lp.outputs["Is Camera Ray"]), b.inputs["Emission Strength"])
    b.inputs["Emission Color"].default_value = (0.94, 0.95, 1.0, 1)
    floor.data.materials.append(fm)
    group(floor, "lg_base")

    wall = L.plane("Void", (14.0, 8.0), (0.0, 3.2, 2.0), normal_to=(0, -10, 2.0))

    def void_s(nb):
        x, yy, _ = nb.coords("Object")
        z = nb.math("ADD", yy, 2.0)
        dx = nb.math("DIVIDE", x, 1.6)
        dz = nb.math("DIVIDE", nb.math("SUBTRACT", z, 0.55), 1.1)
        rr = nb.math("ADD", nb.math("MULTIPLY", dx, dx), nb.math("MULTIPLY", dz, dz))
        f = nb.math("MULTIPLY_ADD", nb.math("EXPONENT", nb.math("MULTIPLY", rr, -1.0)), VOID_E[1] - VOID_E[0], VOID_E[0])
        tcv = nb.n.new("ShaderNodeTexCoord")
        g2 = nb.n.new("ShaderNodeTexWhiteNoise"); g2.noise_dimensions = "3D"
        mpv = nb.n.new("ShaderNodeMapping"); mpv.inputs["Scale"].default_value = (900.0, 900.0, 900.0)
        nb.l.new(tcv.outputs["Object"], mpv.inputs["Vector"]); nb.l.new(mpv.outputs["Vector"], g2.inputs["Vector"])
        return nb.math("MULTIPLY", f, nb.math("MULTIPLY_ADD", g2.outputs["Value"], 0.07, 0.965))

    wall.data.materials.append(L.cam_only_mat("VoidMat", void_s, color=(0.94, 0.95, 1.0), glossy=False))
    L.visibility(wall, camera=True, diffuse=False, glossy=False, shadow=False)
    group(wall, "lg_base")

    cam = Vector((math.sin(math.radians(CAM_AZ)) * math.cos(math.radians(CAM_EL)),
                  -math.cos(math.radians(CAM_AZ)) * math.cos(math.radians(CAM_EL)),
                  math.sin(math.radians(CAM_EL)))) * CAM_DIST + Vector(AIM)

    # --- lg_key: a hard key raking from front-left (lower than before, so cavity walls and racket edges throw
    # shadows into the felt), feathered so its floor pool has no rim. Never on the lacquer.
    key = studio.spot_light("Key", (-1.05, -1.25, 2.05), KEY_W, 42.0, 1.0, color=L.kelvin(5600), target=(0.05, 0.08, 0.0),
                            radius=0.04)
    caps = [o_ for P in Ps for o_ in C.objs(P, *(("cap",) if WHITE_RK else ("cap", "capmark")))]   # white: not the Q
    L.link_receivers(key, [tray, tray_ch, ins, floor] + caps, "recv_key")
    # the overgrips: a neutral 2 x 30 cm strip along each grip from front-left (canon note 6), so the helical wrap
    # reads on neutral black (the warm LED and the raking key made them read brown)
    if GRIP_E > 0:
        for P in Ps:
            gc = P["grip"].parent.matrix_world @ Vector((0.0, -0.229, 0.0))
            loc = gc + Vector((-0.24, -0.06, 0.30))
            gl_ = studio.area_light("GripStrip_" + P["grip"].name, tuple(loc), 0.02, GRIP_E, color=L.kelvin(5600),
                                    size_y=0.30)
            CT_look_at(gl_, loc, gc, (0.0, 1.0, 0.0))
            gl_.visible_camera = False
            L.link_receivers(gl_, C.objs(P, *(("grip",) if WHITE_RK else ("grip", "cap", "capmark"))), "recv_" + gl_.name)
            group(gl_, "lg_key")
    group(key, "lg_key")

    # the faces mirror the lid: a neutral 5600 K graded card just in front of the lining (camera-invisible), so
    # the three coplanar faces show one continuous clean lacquer gradient
    lid_mid = OPEN @ Vector((0, 0.0, ceil_z - 0.085))  # clear of the lid walls (they would cut it edge-on)
    fs_ = KW_FACE if WHITE_RK else FACE_S
    if fs_ > 0:
        fc = L.band_card("FaceSheen", tuple(lid_mid), (1.3, 0.56), fs_, tuple(lid_mid + lining_n),
                         tuple((up_lid * 1.0 + Vector((-0.18, 0, 0))).normalized()), edge=FACE_EDGE, soft=FACE_SOFT,
                         decay=FACE_DECAY, line=FACE_LINE, floor=0.0, color=L.kelvin(5600))
        L.link_receivers(fc, heads, "recv_face")
        group(fc, "lg_key")
        if WHITE_RK:
            fc.visible_diffuse = False   # reflection only: the coat's gloss band, never a diffuse wash on white
    if PACE and P_LID_S > 0:
        # Pace: the faces mirror the lid; with the lining glossy-invisible the upper heads were a black void (no holes),
        # so a dim neutral card just in front of the lining stands in for it: graded along the lid (brighter toward the
        # free edge), it puts a quiet graphite sheen over the heads in which the holes and the 12K read
        lc = lid_mid + lining_n * 0.03
        lcard = L.gradient_card("PaceLid", tuple(lc), (1.3, 0.62), P_LID_S, tuple(lc + lining_n), color=L.kelvin(5600),
                                axis="v", lo=0.0, hi=1.0, floor=P_LID_FLOOR)
        L.link_receivers(lcard, heads, "recv_pacelid")
        group(lcard, "lg_key")
    if PACE and P_WEAVE_S > 0:
        # the weave card (K08 / K11 / K06): a soft graded card P_WEAVE_UP degrees off the faces' mirror direction,
        # seen only by the 12K's fibre lobes: the tapes read as a faint plain weave instead of a black hole
        bpy.context.view_layer.update()
        cam_ = Vector((math.sin(math.radians(CAM_AZ)) * math.cos(math.radians(CAM_EL)),
                       -math.cos(math.radians(CAM_AZ)) * math.cos(math.radians(CAM_EL)),
                       math.sin(math.radians(CAM_EL)))) * CAM_DIST + Vector(AIM)
        fcen = Vector((0.0, HEAD_Y, Z_CAV + C.T2))
        d_ = L.mirror_dir(Vector((0, 0, 1)), fcen, cam_)
        hz_ = Vector((-d_.y, d_.x, 0)).normalized()
        d_up = (Matrix.Rotation(math.radians(P_WEAVE_UP), 3, hz_) @ d_).normalized()
        if d_up.z < d_.z:
            d_up = (Matrix.Rotation(math.radians(-P_WEAVE_UP), 3, hz_) @ d_).normalized()
        wv = L.gradient_card("PaceWeave", tuple(fcen + d_up * P_WEAVE_D), P_WEAVE_SIZE, P_WEAVE_S, tuple(fcen),
                             color=L.kelvin(5600), axis="v", lo=0.0, hi=1.0, floor=0.3)
        L.link_receivers(wv, heads, "recv_paceweave")
        group(wv, "lg_key")
    if WHITE_RK:
        for k_, P in enumerate(Ps):
            Mr = P["face"].parent.matrix_world
            if KW_NECK > 0:    # the neck: a second soft pool from the pool's side, face + neck (no step at the split)
                tn = Mr @ Vector((0.0, KW_NECK_Y, C.ZT))
                nl_ = studio.spot_light("NeckPool_" + P["face"].name, tuple(tn + Vector(KW_POOL_AT)), KW_NECK,
                                        KW_NECK_DEG, blend=1.0, color=(1.0, 0.985, 0.97), target=tuple(tn),
                                        radius=KW_POOL_R)
                L.link_receivers(nl_, C.objs(P, "face", "neck", "rim", "wall"), "recv_neck_" + P["face"].name)
                group(nl_, "lg_key")
        for P in Ps:
            hc = P["face"].parent.matrix_world.translation
            recv = C.objs(P, "face", "back", "rim", "wall", "neck", "throat", "bridgewall", "holes", "etchR", "etchL")
            if KW_POOL > 0:
                pl_ = studio.spot_light("Pool_" + P["face"].name, tuple(hc + Vector(KW_POOL_AT)), KW_POOL, KW_POOL_DEG,
                                        blend=1.0, color=(1.0, 0.985, 0.97),
                                        target=(hc.x + KW_POOL_T[0], hc.y + KW_POOL_T[1], hc.z), radius=KW_POOL_R)
                L.link_receivers(pl_, recv, "recv_pool_" + P["face"].name)
                group(pl_, "lg_key")
            if KW_FILL > 0:
                fl_ = studio.area_light("Fill_" + P["face"].name, tuple(hc + Vector(KW_FILL_AT)), 1.0, KW_FILL,
                                        color=(0.94, 0.96, 1.0), target=tuple(hc))
                fl_.visible_camera = False
                L.link_receivers(fl_, recv, "recv_fill_" + P["face"].name)
                group(fl_, "lg_key")
    # hole lips: a small soft lamp above and behind the case, linked to the canon 'holes' part only: the far lip of
    # every hole (which faces the camera) catches one thin crescent; the carbon-lined bore below it stays dark, so each
    # hole reads as a through-hole, never a stud
    if BORE_E > 0:
        bl = L.area_at("Bores", Vector((0.0, HEAD_Y + 0.9, 1.6)), (0, HEAD_Y, Z_CAV + C.T2), BORE_SIZE, BORE_SIZE,
                       BORE_E, color=L.kelvin(5200), recv=lips)
        group(bl, "lg_key")
    # the laser-frosted serials: K10's grazing rake per racket, from camera-left, linked to that racket's face only
    if RAKE_E > 0:
        for P, sr in zip(Ps, SERIALS):
            x0, x1, y0, y1 = C.serial_box(sr)
            M = P["face"].parent.matrix_world
            S_ = M @ Vector(((x0 + x1) / 2, (y0 + y1) / 2, C.ZT))
            rd = M.to_3x3() @ Vector((-math.cos(math.radians(16)), 0.25, math.sin(math.radians(16))))
            rk_ = studio.area_light("Rake_" + sr, tuple(S_ + rd.normalized() * 0.125), 0.05, RAKE_E,
                                    color=(1.0, 0.985, 0.965), size_y=0.005, target=tuple(S_))
            L.link_receivers(rk_, [P["face"]], "recv_rake_" + sr)
            group(rk_, "lg_key")

    # the plaque mirrors the tray in front of it: a crisp band card there makes the brushed steel gleam
    pc = (OPEN @ Vector((0, PLAQUE_Y, ceil_z - 0.0025)))
    vcam = (cam - pc).normalized()
    rr = (2 * lining_n.dot(vcam) * lining_n - vcam).normalized()
    pcard = L.band_card("PlaqueSheen", tuple(pc + rr * 0.45), (0.6, 0.4), PLAQUE_S, tuple(pc),
                        tuple((Vector((-1.0, 0, 0)) + up_lid * 0.35).normalized()), edge=0.10, soft=0.003, decay=0.30,
                        line=0.7, line_w=0.003, floor=0.015, color=L.kelvin(5400))
    L.link_receivers(pcard, [pl], "recv_plaque")
    group(pcard, "lg_lid")

    # machined edges: a long strip in each straight chamfer's mirror direction draws one continuous silver line
    # (front, right side, lid free edge); a low soft card gives the anodised front wall its satin gradient
    def chamfer_strip(name, pt, n, edge_dir, length, strength, recv, dist=1.2, width=0.05):
        vv = (cam - pt).normalized()
        rr_ = (2 * n.dot(vv) * n - vv).normalized()
        c_ = pt + rr_ * dist
        st = L.plane(name, (length, width), tuple(c_))
        zax_ = (pt - c_).normalized(); xax_ = (edge_dir - zax_ * edge_dir.dot(zax_)).normalized(); yax_ = zax_.cross(xax_)
        st.matrix_world = Matrix(((xax_.x, yax_.x, zax_.x, c_.x), (xax_.y, yax_.y, zax_.y, c_.y),
                                  (xax_.z, yax_.z, zax_.z, c_.z), (0, 0, 0, 1)))

        def s_(nb):
            u, vv_, _ = nb.coords("UV")
            f = nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.12), nb.smooth(u, 1.0, 0.88))
            f = nb.math("MULTIPLY", f, nb.math("MULTIPLY", nb.smooth(vv_, 0.0, 0.3), nb.smooth(vv_, 1.0, 0.7)))
            return nb.math("MULTIPLY", f, strength)

        st.data.materials.append(L.emitter_mat(name + "Mat", L.kelvin(5800), s_, additive=True))
        L.visibility(st, camera=False, diffuse=True, glossy=True, shadow=False)
        L.link_receivers(st, recv, "recv_" + name)
        group(st, "lg_key")
        return st

    s2 = 0.7071
    chamfer_strip("ChamFront", Vector((0, -D / 2 + CHAMFER / 2, Z_RIM - CHAMFER / 2)), Vector((0, -s2, s2)),
                  Vector((1, 0, 0)), 2.2, CHAMFER_S, [tray_ch])
    chamfer_strip("ChamRight", Vector((W / 2 - CHAMFER / 2, 0, Z_RIM - CHAMFER / 2)), Vector((s2, 0, s2)),
                  Vector((0, 1, 0)), 1.6, CHAMFER_S, [tray_ch])
    # lid: free edge (top when open) and its right side
    le = OPEN @ Vector((0, -D / 2 + CHAMFER / 2, Z_RIM + LID_H - CHAMFER / 2))
    ln_ = (R @ Vector((0, -s2, s2))).normalized()
    chamfer_strip("ChamLidTop", le, ln_, Vector((1, 0, 0)), 2.2, CHAMFER_S, [lid_ch])
    lr = OPEN @ Vector((W / 2 - CHAMFER / 2, 0, Z_RIM + LID_H - CHAMFER / 2))
    lrn = (R @ Vector((s2, 0, s2))).normalized()
    chamfer_strip("ChamLidRight", lr, lrn, up_lid, 1.6, CHAMFER_S, [lid_ch])

    def mirror_card(name, pt, n, dist, size, strength, grad, width, offset, lo, recv, col=(1, 1, 1)):
        vv = (cam - pt).normalized()
        rr_ = (2 * n.dot(vv) * n - vv).normalized()
        c_ = L.sweep_card(name, tuple(pt + rr_ * dist), size, strength, tuple(pt), grad, width, offset, color=col, lo=lo)
        L.link_receivers(c_, recv, "recv_" + name)
        group(c_, "lg_key")
        return c_

    mirror_card("SatinFront", Vector((0, -D / 2, Z_RIM / 2)), Vector((0, -1, 0)), 1.6, (2.6, 1.2), SATIN_S,
                (0, 0, 1), 0.5, 0.1, 0.0, [tray])
    mirror_card("SatinRight", Vector((W / 2, 0, Z_RIM / 2)), Vector((1, 0, 0)), 1.6, (2.0, 1.2), SATIN_S * 0.7,
                (0, 0, 1), 0.5, 0.1, 0.0, [tray])

    # --- lg_rim: ember hairline on the tray's right-hand top chamfer, from behind-right
    edge = Vector((W / 2 - CHAMFER / 2, 0.0, Z_RIM - CHAMFER / 2))
    n45 = Vector((s2, 0, s2))
    vr = (cam - edge).normalized()
    rd = (2 * n45.dot(vr) * n45 - vr).normalized()
    # rotate the ember source a little behind the silver one, so the two lines sit side by side, not on top
    rc = edge + (Matrix.Rotation(math.radians(-7), 3, "Z") @ rd) * 1.0
    rim = L.plane("Rim", (0.025, 1.8), tuple(rc))
    yax = Vector((0, 1, 0)); zax = (edge - rc).normalized(); xax = yax.cross(zax).normalized(); yax = zax.cross(xax)
    rim.matrix_world = Matrix(((xax.x, yax.x, zax.x, rc.x), (xax.y, yax.y, zax.y, rc.y), (xax.z, yax.z, zax.z, rc.z), (0, 0, 0, 1)))

    def rim_s(nb):
        _, vv, _ = nb.coords("UV")
        return nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(vv, 0.0, 0.25), nb.smooth(vv, 1.0, 0.75)), RIM_S)

    rim.data.materials.append(L.emitter_mat("RimMat", L.hex_lin("#ff3a1e"), rim_s, additive=True))
    L.visibility(rim, camera=False, diffuse=False, glossy=True, shadow=False)
    L.link_receivers(rim, [tray_ch], "recv_rim")
    group(rim, "lg_rim")

    L.visual_only("Void", "FloorMat")
    L.debug_off()
    camo = studio.camera(tuple(cam), AIM, lens=LENS, fstop=8.0)
    fw, top, bottom = FRAMES[cam_kind]
    frame(camo, [lid, tray], fw, top, bottom)
    if WHITE_RK and KW_SWEEP > 0:
        # one soft clear-coat sweep per racket, the same on all three (designed in model space), mapped through the
        # FRAMED camera (frame() dollies it: 2.63 m gallery, 2.31 m card)
        bpy.context.view_layer.update()
        camf = camo.matrix_world.translation.copy()
        ca, sa = math.cos(math.radians(KW_SWEEP_ANG)), math.sin(math.radians(KW_SWEEP_ANG))
        for k_, P in enumerate(Ps):
            Mr = P["face"].parent.matrix_world
            c0 = Vector((KW_SWEEP_C[0], KW_SWEEP_C[1], C.ZT))
            dv = Vector((ca, sa, 0.0)) * KW_SWEEP_L
            sw = KS.gloss_sweep("Sweep_" + P["face"].name, camf, Mr @ c0, Mr.to_3x3() @ Vector((0, 0, 1)),
                                Mr @ (c0 - dv), Mr @ (c0 + dv), KW_SWEEP_W, KW_SWEEP_H + 0.004 * k_, KW_SWEEP,
                                C.objs(P, "face", "neck"), color=L.kelvin(5600))
            group(sw, "lg_key")
    if WHITE_RK and KW_CAP > 0:
        # canon note 5: a 30 cm softbox in the mirror direction of each cap's front band, linked to the cap and its Q
        import numpy as _np
        camf = camo.matrix_world.translation.copy()
        pr = C.cap_profile()
        yk = -0.2998 + C.CAP_SHIFT
        s_k = float(_np.interp(-yk, [-y for (_, y) in pr], [s_ for (s_, _) in pr]))
        G_, _ = C.section(64, grow=C.TAPE)
        for P in Ps:
            Mr = P["face"].parent.matrix_world
            az = math.radians(MARK_AZ)
            pk = Mr @ Vector((0.0, yk, float(G_[:, 1].max()) * s_k))
            nk = (Mr.to_3x3() @ Vector((math.sin(az), 0.0, math.cos(az)))).normalized()
            rk_ = L.mirror_dir(nk, pk, camf)
            ck = studio.area_light("CapSoft_" + P["face"].name, tuple(pk + rk_ * 0.35), 0.30, KW_CAP, color=L.kelvin(5600),
                                   size_y=0.10, target=tuple(pk))
            ck.visible_camera = False
            L.link_receivers(ck, C.objs(P, "cap", "capmark"), "recv_capsoft_" + P["face"].name)
            group(ck, "lg_key")
    if o.get("hover_mix"):
        # the card's hover state from the same render: the lid group (slot, wash, pour, edge, painted lining,
        # plaque card) at HOVER_GAIN, everything else as is; plus an all-ones mix to verify the passes add up
        base = {"lg_base": 1.0, "lg_key": 1.0, "lg_rim": 1.0}
        L.mix_compositor(sc, o, {"hover": dict(base, lg_lid=HOVER_GAIN), "check": dict(base, lg_lid=1.0)})
    return sc


if __name__ == "__main__":
    a = L.parse_args(sys.argv[1:], "K09-case-three")
    a["hover_mix"] = "--hover-mix" in sys.argv
    L.render_main(build, a)
    L.seq_rename(a)
