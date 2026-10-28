"""K06-mould (v20, canon, white Command; stage 3a critique applied: the near wall lifted to white-in-shade by a low
front card, a soft gloss sweep instead of the 1.6 mm line, no neck-only lights (no face/neck step) plus a neck pool, the
glow carried into the neck, grip and cap channel, a 1.6 mm land instead of 3.5 mm. See "v20" below; backup of v19:
shots/K06-mould.v19-white-precrit.bak). Born whole. The lower half of a precision tool-steel mould, the finished canonical racket
hovering above it.

Usage (from the blender dir, through the render lock):
  flock render.lock ../bpyenv/bin/python shots/K06-mould.py --w 960 --h 540 --spp 48 --out k06c/prev
  ONE render writes both page layers from its light-group passes, so they are pixel-registered by construction:
    out/<out>-base.png   cold steel (every group but lg_cavity)
    out/<out>-full.png   base + lg_cavity (the 2200 K glow rising from the cavity), pin streak at 1/3
    out/<out>.png        the Cycles-denoised combined image (= full, for reference)
  Finals: --out final/K06-mould  ->  final/K06-mould-base.png, final/K06-mould-full.png (16-bit)
Optional: --crop x0 x1 y0 y1 (fractions, top-left origin) renders only that region (detail check)
          --probe     print where the key points land in frame, do not render
          --exr       also save the raw light-group passes as a multilayer EXR
          --set K=V[,K=V]  override any upper-case module constant (look-dev)

v18 (render audit, section 4 + group brief): racket.build_racket is gone. The racket is kq_canon.build_racket(
feel="command", serial="KQ-000427"): 455.0 mm, the crown of 8 + 34 holes with carbon-lined bores, the 1.5 mm edge with
the K10 twill folding over it onto the 38 mm wall (no bumper, no edge-guard strip: the old pair read as two stacked
plates), the one-piece neck flowing into the neutral-black helical overgrip and the satin cap with its engraved Q, the logo (no
flat end, no titanium collar, no carbon disc). The mould follows it exactly: 42 pins at the canonical positions (14.0 mm
for the crown of 8, 12.4 mm for the 34) and a cavity that is the canon racket's own lower half (head, neck, grip and cap
channels), grown 0.4 % in plan, built directly from the canon surfaces (no boolean on the racket mesh).

Layout (unchanged from v17): the racket lies along the plate's LONG axis (world X, head toward +X = camera-left) and the
camera looks across the plate from the front (+Y), 47 deg down, 70 mm. The plate's lit front top edge sits at y 78.5 %
of the frame (the page sets the Swiss Made lockup below it). Model space (metres): parting face z = 0, plate
860 x 380 x 200 mm.

Lighting: the plate, pins and pillars keep v17's rig (lg_top, lg_fill, lg_rim, lg_key, lg_pins). The racket has its own
linked rig (lg_racket, canon lighting notes): a projected band softbox across the face (lit twill in one diagonal, deep
black gloss elsewhere) plus a 1.5 mm gloss line, a mirror-path ribbon on the far 1.5 mm edge (one crisp white hairline
along the top of the silhouette), a graded card on the near 38 mm wall (the twill folding over the edge, SWISS MADE),
crescents on the hole lips, a strip along the overgrip, a softbox for the cap's Q, and a cool lift from below for the
underside the polished floor mirrors. lg_cavity: the floor's 2200 K emission plus a warm area light on the floor linked
to the racket (amber bores, a warm line on the lower edge; a shadow-only shield keeps it off the flat underside).
"""
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(HERE, "shots")
for _p in (HERE, SHOTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import look_c  # noqa: E402
import racket  # noqa: E402
import studio  # noqa: E402
import kq_canon as C  # noqa: E402
import k10_lib as KT  # noqa: E402
import k789_lib as KL  # noqa: E402
import canon_test as CT  # noqa: E402
import kw_sheen as KS  # noqa: E402

# ------------------------------------------------------------------ args


def parse_args(argv):
    o = {"w": 960, "h": 540, "spp": 32, "out": "k06c/prev", "crop": None, "probe": False, "exr": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--w", "--h", "--spp"):
            o[a[2:]] = int(argv[i + 1]); i += 2
        elif a == "--out":
            o["out"] = argv[i + 1]; i += 2
        elif a == "--crop":
            o["crop"] = [float(v) for v in argv[i + 1:i + 5]]; i += 5
        elif a == "--probe":
            o["probe"] = True; i += 1
        elif a == "--exr":
            o["exr"] = True; i += 1
        elif a == "--dry":
            o["dry"] = True; i += 1
        elif a == "--set":
            for kv in argv[i + 1].split(","):
                k, v = kv.split("=")
                cur = globals()[k]
                globals()[k] = type(cur)(float(v)) if isinstance(cur, (int, float)) else tuple(float(x) for x in v.split(":"))
                print("set", k, globals()[k], flush=True)
            i += 2
        else:
            i += 1
    return o


# ------------------------------------------------------------------ dimensions

U = racket.U
T2 = C.T2
PXH, PYH, PT = 0.43, 0.19, 0.20          # plate half-width (X), half-depth (Y), thickness
CH = 0.0014                              # plate edge chamfer
CAV_SCALE = 1.004                        # cavity grown 0.4 % in plan (moulding shrink allowance)
HOVER = 0.12                             # racket centre plane above the parting face
OX = 0.0725                              # racket model y -> world X offset: the canon racket (tip +0.155 .. butt -0.300) centred
PIN_TOP = -0.0002
PIL_R, PIL_TOP = 0.013, 0.95
PIL_XY = [(sx * 0.395, sy * 0.145) for sx in (1, -1) for sy in (1, -1)]
BUSH_R, BUSH_H, BUSH_CH = 0.020, 0.004, 0.0005
LAND_W, GROOVE_IN, GROOVE_OUT = 0.0016, 0.0042, 0.0052     # v20: land 3.5 -> 1.6 mm (it read as a thick outline sticker)
LAND_OVER = 0.0003                       # the land overhangs the cavity rim by 0.3 mm (seals the cut seam)
CUT_GROW = 0.0003                        # the plate's prism cut sits 0.3 mm outside the cavity rim (hidden behind it)
ENGRAVE = "KQ-M01  CH"                   # no middle dot (house rule): two spaces separate the part number and CH
ENG_SIZE, ENG_DEPTH, ENG_MARGIN, ENG_Z = 0.0142, 0.00025, 0.017, -0.034

ELEV, LENS, CAM_D, CAM_SHIFT = 47.0, 70.0, 2.45, 0.045
CAM_T = (0.0, 0.0, 0.0)
GROUPS = ("lg_top", "lg_fill", "lg_rim", "lg_key", "lg_pins", "lg_racket", "lg_cavity")
PINS_FULL = 1.0 / 3.0                    # full: the pin streak at a third (the glow lights the pins)


def rk_matrix():
    """Racket model space -> world: turn -90 deg about Z (head +Y -> +X), then centre tip-to-butt on the plate."""
    return Matrix.Translation((OX, 0, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")


def rk2w(mx, my):
    return (my + OX, -mx)


# ------------------------------------------------------------------ node helper


class NB:
    """Tiny node-graph builder: sockets or floats in, sockets out."""

    def __init__(self, mat):
        self.nt = mat.node_tree
        self.n, self.l = self.nt.nodes, self.nt.links

    def _in(self, sock, v):
        if v is None:
            return
        if isinstance(v, (int, float, tuple, list)):
            sock.default_value = v
        else:
            self.l.new(v, sock)

    def math(self, op, a, b=None, c=None, clamp=False):
        m = self.n.new("ShaderNodeMath"); m.operation = op; m.use_clamp = clamp
        self._in(m.inputs[0], a); self._in(m.inputs[1], b); self._in(m.inputs[2], c)
        return m.outputs[0]

    def smooth(self, v, e0, e1, lo=0.0, hi=1.0):
        m = self.n.new("ShaderNodeMapRange"); m.interpolation_type = "SMOOTHSTEP"
        m.inputs["From Min"].default_value = e0; m.inputs["From Max"].default_value = e1
        m.inputs["To Min"].default_value = lo; m.inputs["To Max"].default_value = hi
        self._in(m.inputs["Value"], v)
        return m.outputs["Result"]

    def xyz(self, space="Object"):
        tc = self.n.new("ShaderNodeTexCoord")
        sep = self.n.new("ShaderNodeSeparateXYZ")
        self.l.new(tc.outputs[space], sep.inputs[0])
        return sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]

    def combine(self, x, y, z):
        c = self.n.new("ShaderNodeCombineXYZ")
        self._in(c.inputs[0], x); self._in(c.inputs[1], y); self._in(c.inputs[2], z)
        return c.outputs[0]

    def mixv(self, fac, a, b):
        m = self.n.new("ShaderNodeMix"); m.data_type = "VECTOR"
        self._in(m.inputs["Factor"], fac); self._in(m.inputs[4], a); self._in(m.inputs[5], b)
        return m.outputs[1]

    def mixc(self, fac, a, b):
        m = self.n.new("ShaderNodeMix"); m.data_type = "RGBA"
        self._in(m.inputs["Factor"], fac); self._in(m.inputs[6], a); self._in(m.inputs[7], b)
        return m.outputs[2]

    def noise(self, scale, detail=2.0, vec=None, rough=0.5):
        n = self.n.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        if vec is not None:
            self.l.new(vec, n.inputs["Vector"])
        return n.outputs["Fac"]


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


# ------------------------------------------------------------------ materials (the mould: unchanged from v17)

STEEL = (0.56, 0.565, 0.58)
SATIN_R, SATIN_ANISO, TOP_ANISO = 0.24, 0.7, 0.45
FC_R, FC_PASSES, FC_FEED = 0.05, 7, 0.0013      # fly-cut: 100 mm cutter, 7 passes along X, 1.3 mm feed
FC_BUMP = 0.14
FC_BACK = 0.35                                  # trailing-edge (back-cut) arcs: the crosshatch
FC_JIT = 0.0011                                 # pitch jitter (m, peak to peak) over ~3 cm
TAN_SWING = 0.2                                 # fraction of the radial swing kept (1 = true radial)
PASS_STEP = 0.002                               # per-pass roughness step (review: at most +-0.005)


def mat_satin():
    """Tool steel. Parting face: fly-cut along X in overlapping passes; each revolution leaves a leading arc and a
    fainter trailing (back-cut) arc of opposite curvature, so neighbouring arcs crosshatch; the feed jitters a few
    percent so the arcs never settle into vinyl-record regularity. Vertical faces: surface-ground, a fine horizontal
    lay (~0.1 mm). Anisotropic highlights follow the tool path."""
    m, b = new_mat("SatinSteel")
    nb = NB(m)
    x, y, z = nb.xyz("Object")
    R, W, feed = FC_R, 2 * PYH / FC_PASSES, FC_FEED
    k = nb.math("FLOOR", nb.math("DIVIDE", nb.math("ADD", y, PYH), W))
    yc = nb.math("ADD", nb.math("MULTIPLY", nb.math("ADD", k, 0.5), W), -PYH)
    v = nb.math("SUBTRACT", y, yc)
    s = nb.math("SQRT", nb.math("MAXIMUM", nb.math("SUBTRACT", R * R, nb.math("MULTIPLY", v, v)), 1e-6))
    jvec = nb.combine(x, nb.math("MULTIPLY", k, 7.31), 0.0)
    jit = nb.math("MULTIPLY", nb.math("SUBTRACT", nb.noise(32.0, 1.0, jvec), 0.5), FC_JIT * 2)
    xj = nb.math("ADD", x, jit)
    ph1 = nb.math("ADD", nb.math("DIVIDE", nb.math("SUBTRACT", xj, s), feed), nb.math("MULTIPLY", k, 0.37))
    ph2 = nb.math("ADD", nb.math("DIVIDE", nb.math("ADD", xj, s), feed), nb.math("MULTIPLY", k, 0.61))
    ridge = nb.math("ADD", nb.math("SINE", nb.math("MULTIPLY", ph1, 2 * math.pi)),
                    nb.math("MULTIPLY", nb.math("SINE", nb.math("MULTIPLY", ph2, 2 * math.pi)), FC_BACK))
    t_arc = nb.combine(s, nb.math("MULTIPLY", v, TAN_SWING), 0.0)
    geo = nb.n.new("ShaderNodeNewGeometry")
    nz = nb.n.new("ShaderNodeSeparateXYZ"); nb.l.new(geo.outputs["Normal"], nz.inputs[0])
    top = nb.smooth(nb.math("ABSOLUTE", nz.outputs["Z"]), 0.55, 0.75)
    t = nb.mixv(top, (0.0, 0.0, 1.0), t_arc)
    gvec = nb.combine(nb.math("MULTIPLY", x, 25.0), nb.math("MULTIPLY", y, 25.0), nb.math("MULTIPLY", z, 9000.0))
    grind = nb.math("SUBTRACT", nb.noise(1.0, 3.0, gvec, 0.6), 0.5)
    hfield = nb.math("ADD", nb.math("MULTIPLY", ridge, top),
                     nb.math("MULTIPLY", nb.math("MULTIPLY", grind, 3.0), nb.math("SUBTRACT", 1.0, top)))
    fine = nb.noise(2600.0, 2.0)
    hfield = nb.math("MULTIPLY_ADD", fine, 0.25, hfield)
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = FC_BUMP
    bump.inputs["Distance"].default_value = 0.00002
    nb.l.new(hfield, bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    drift = nb.noise(4.0, 2.0)
    step = nb.math("MULTIPLY", nb.math("SUBTRACT", nb.math("FRACT", nb.math("MULTIPLY", k, 0.618)), 0.5), top)
    rough = nb.math("MULTIPLY_ADD", step, 2 * PASS_STEP, SATIN_R)
    rough = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", drift, 0.5), 0.03, rough)
    rough = nb.math("MULTIPLY_ADD", nb.math("MULTIPLY", ridge, top), 0.02, rough)
    nb.l.new(rough, b.inputs["Roughness"])
    b.inputs["Base Color"].default_value = (*STEEL, 1)
    b.inputs["Metallic"].default_value = 1.0
    nb.l.new(nb.math("MULTIPLY_ADD", top, TOP_ANISO - SATIN_ANISO, SATIN_ANISO), b.inputs["Anisotropic"])
    nb.l.new(t, b.inputs["Tangent"])
    return m


def mat_polished(name="Polished", rough=0.035, aniso_axis=None, color=(0.66, 0.665, 0.68), aniso=0.8):
    m, b = new_mat(name)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = rough
    if aniso_axis is not None:
        nb = NB(m)
        b.inputs["Anisotropic"].default_value = aniso
        nb.l.new(nb.combine(*aniso_axis), b.inputs["Tangent"])
    return m


GLOW_S, GLOW_FLOOR = 2.4, 0.08
GLOW_EMBER = (1.0, 0.075, 0.02, 1)    # the hue of #5a1206
GLOW_K = 2200.0
GLOW_GAMMA = 2.0
WALL_R = 0.07
PIN_ROUGH = 0.05
PINTOP_R = 0.32
PILLAR_R, PILLAR_A = 0.20, 0.6


def mat_cavity_floor():
    """Mirror-polished cavity floor with the 2200 K emission (light group lg_cavity, so 'base' leaves it out): a hot
    core under the head's centre falling to deep ember at the walls (no plateau: the peak is a point)."""
    m, b = new_mat("CavityFloor")
    b.inputs["Base Color"].default_value = (0.66, 0.665, 0.68, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = WALL_R
    nb = NB(m)
    x, y, _z = nb.xyz("Object")
    cx = OX + 0.012
    ex = nb.math("DIVIDE", nb.math("SUBTRACT", x, cx), 0.150)
    ey = nb.math("DIVIDE", y, 0.118)
    e = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", ex, ex), nb.math("MULTIPLY", ey, ey)))
    f = nb.smooth(e, 1.08, 0.0)
    bb = nb.n.new("ShaderNodeBlackbody"); bb.inputs["Temperature"].default_value = GLOW_K
    col = nb.mixc(nb.math("POWER", f, 0.7), GLOW_EMBER, bb.outputs["Color"])
    nb.l.new(col, b.inputs["Emission Color"])
    nb.l.new(nb.math("MULTIPLY_ADD", nb.math("POWER", f, GLOW_GAMMA), GLOW_S, GLOW_FLOOR), b.inputs["Emission Strength"])
    return m


# v20 (critique): the head cavity glowed but the neck, grip and cap channel stayed black between two chrome rails, so the
# cavity read as a glowing head pocket beside a mechanical slot. The channel now carries the same 2200 K / ember glow:
# emission on the cavity walls from the neck (where the floor's glow ends, model y -0.150) to the butt, strongest on
# the channel's floor (normals up), falling from CH_S0 at the neck to CH_S1 at the butt; zero on the head's walls.
CH_S0, CH_S1, CH_X0, CH_X1 = 0.42, 0.14, -0.070, -0.2275     # strength at the neck / butt, their world X


def mat_cavity_walls():
    m = mat_polished("CavityWall", WALL_R)
    b = m.node_tree.nodes["Principled BSDF"]
    nb = NB(m)
    x, _y, _z = nb.xyz("Object")
    geo = nb.n.new("ShaderNodeNewGeometry")
    nz = nb.n.new("ShaderNodeSeparateXYZ"); nb.l.new(geo.outputs["Normal"], nz.inputs[0])
    bottom = nb.smooth(nz.outputs["Z"], 0.25, 0.95)
    on = nb.smooth(x, CH_X0 + 0.004, CH_X0 - 0.010)                 # 0 on the head's walls, 1 from the neck on
    t = nb.smooth(x, CH_X0, CH_X1)                                 # 0 at the neck -> 1 at the butt
    s_ = nb.math("MULTIPLY_ADD", t, CH_S1 - CH_S0, CH_S0)
    nb.l.new(nb.math("MULTIPLY", nb.math("MULTIPLY", s_, bottom), on), b.inputs["Emission Strength"])
    bb = nb.n.new("ShaderNodeBlackbody"); bb.inputs["Temperature"].default_value = GLOW_K
    col = nb.mixc(nb.math("MULTIPLY_ADD", t, -0.55, 0.65), GLOW_EMBER, bb.outputs["Color"])
    nb.l.new(col, b.inputs["Emission Color"])
    return m


def mat_basic(name, color, rough, metallic=1.0, spec=0.5):
    m, b = new_mat(name)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = spec
    return m


# ------------------------------------------------------------------ geometry helpers


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def apply_mods(ob):
    return racket._apply_all(ob)


def box(name, x0, x1, y0, y1, z0, z1, bevel=0.0, segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = ob.modifiers.new("bv", "BEVEL")
        bv.width = bevel
        bv.segments = segs
        bv.limit_method = "ANGLE"
        apply_mods(ob)
    return ob


def cylinder(name, r, z0, z1, x=0.0, y=0.0, verts=64, top_bevel=0.0, segs=4):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=r, depth=z1 - z0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    ob.location = (x, y, (z0 + z1) / 2)
    if top_bevel:
        bm = bmesh.new(); bm.from_mesh(me)
        top_edges = [e for e in bm.edges if all(v.co.z > (z1 - z0) / 2 - 1e-6 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=top_edges, offset=top_bevel, segments=segs, profile=0.5, affect="EDGES")
        bm.to_mesh(me); bm.free()
    me.shade_smooth()
    crisp_planes(me, horizontal_only=True)
    return ob


def boolean(target, cutter, op="DIFFERENCE", transfer=True):
    md = target.modifiers.new("bool", "BOOLEAN")
    md.operation = op
    md.object = cutter
    md.solver = "EXACT"
    if transfer:
        md.material_mode = "TRANSFER"
    apply_mods(target)


def crisp_planes(me, flat_tol=1e-4, crease_deg=1.0, sharp_deg=32.0, horizontal_only=False):
    """Smooth shading that keeps every flat face truly flat."""
    bm = bmesh.new()
    bm.from_mesh(me)
    cos_c = math.cos(math.radians(crease_deg))
    cos_s = math.cos(math.radians(sharp_deg))

    def axis(f):
        n = f.normal
        if abs(n.z) > 1 - flat_tol:
            return True
        if horizontal_only:
            return False
        c = f.calc_center_median()
        return (abs(n.x) > 1 - flat_tol and abs(abs(c.x) - PXH) < 0.002) or \
               (abs(n.y) > 1 - flat_tol and abs(abs(c.y) - PYH) < 0.002)

    for e in bm.edges:
        if len(e.link_faces) != 2:
            e.smooth = False
            continue
        f1, f2 = e.link_faces
        d = f1.normal.dot(f2.normal)
        e.smooth = not (d < cos_s or ((axis(f1) or axis(f2)) and d < cos_c))
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.update()


def _rings_of(geom):
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for p in polys:
        out.append([list(p.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in p.interiors])
    return out


def poly_mesh(name, geom, z, to_world=True):
    """Flat mesh at height z from a shapely (Multi)Polygon in racket model space (mapped to world unless told not)."""
    from mathutils.geometry import tessellate_polygon
    bm = bmesh.new()
    for rings in _rings_of(geom):
        if to_world:
            rings = [[rk2w(x, y) for (x, y) in ring] for ring in rings]
        verts = [[bm.verts.new((X, Y, z)) for (X, Y) in ring] for ring in rings]
        flat = [v for ring in verts for v in ring]
        tris = tessellate_polygon([[Vector((X, Y, 0)) for (X, Y) in ring] for ring in rings])
        for a, b, c in tris:
            try:
                bm.faces.new((flat[a], flat[b], flat[c]))
            except ValueError:
                pass
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return link(bpy.data.objects.new(name, me))


def prism(name, geom, z0, z1):
    """Closed prism (world) over a shapely polygon in racket model space: the plate's cavity cut."""
    from mathutils.geometry import tessellate_polygon
    bm = bmesh.new()
    for rings in _rings_of(geom):
        rings = [[rk2w(x, y) for (x, y) in ring] for ring in rings]
        lo = [[bm.verts.new((X, Y, z0)) for (X, Y) in ring] for ring in rings]
        hi = [[bm.verts.new((X, Y, z1)) for (X, Y) in ring] for ring in rings]
        tris = tessellate_polygon([[Vector((X, Y, 0)) for (X, Y) in ring] for ring in rings])
        fl, fh = [v for r in lo for v in r], [v for r in hi for v in r]
        for a, b, c in tris:
            bm.faces.new((fh[a], fh[b], fh[c]))
            bm.faces.new((fl[c], fl[b], fl[a]))
        for rl, rh in zip(lo, hi):
            n = len(rl)
            for k in range(n):
                j = (k + 1) % n
                bm.faces.new((rl[k], rl[j], rh[j], rh[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return link(bpy.data.objects.new(name, me))


def keep_faces(src, name, pred):
    """Copy of src (or src itself when name is None) keeping only the faces pred() accepts."""
    ob = src if name is None else link(bpy.data.objects.new(name, src.data.copy()))
    me = ob.data
    drop = [p.index for p in me.polygons if not pred(p)]
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in drop], context="FACES")
    bm.to_mesh(me); bm.free()
    me.update()
    return ob


# ------------------------------------------------------------------ the cavity: the canon racket's lower half


def _ss(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def half_ring(grow, s, m=96):
    """The canon handle section (grown by `grow`, scaled by `s`) below z = 0: m points (x, z) from the -x side at
    z = 0, round the back, to the +x side at z = 0 (uniform in arc length)."""
    P, _ = C.section(1440, grow=grow)
    P = np.roll(P * s, -len(P) // 2, axis=0)      # start at the front centre, walking toward -x
    z = P[:, 1]
    low = np.where(z <= 0)[0]
    i0, i1 = low[0], low[-1]

    def cross(a, b):
        t = P[a, 1] / (P[a, 1] - P[b, 1])
        return P[a] + (P[b] - P[a]) * t

    pts = np.vstack([cross(i0 - 1, i0), P[i0:i1 + 1], cross(i1, (i1 + 1) % len(P))])
    seg = np.hypot(*np.diff(pts, axis=0).T)
    sa = np.r_[0, np.cumsum(seg)]
    t = np.linspace(0, sa[-1], m)
    return np.stack([np.interp(t, sa, pts[:, 0]), np.interp(t, sa, pts[:, 1])], 1)


def handle_rings(step=0.0005, m=96):
    """[(y, ring)] for the handle channel: the grip on the canon section (its tape ramping in over the top 2.5 mm, as
    the grip does), then the cap profile (scale of the grip's one-tape section), down to the butt at y -0.300."""
    y0, y1 = C.GRIP_Y
    prof = C.cap_profile()
    py = np.array([-y for (_, y) in prof])
    ps = np.array([s for (s, _) in prof])
    ys = list(np.arange(y0, C.BUTT_Y, -step)) + [C.BUTT_Y]
    out = []
    for y in ys:
        g, s = C.TAPE * _ss(0.0, 0.0025, y0 - y), 1.0
        if y <= prof[0][1]:
            sc = float(np.interp(-y, py, ps))
            g, s = C.TAPE, (max(1.0, sc) if y >= y1 else sc)
        out.append((float(y), half_ring(g, s, m)))
    return out


def lathe_half(name, rings):
    """Open half-tube through the rings (model space) closed by a half-disc at the butt; normals face into the
    channel (up/inward), as a cavity surface."""
    bm = bmesh.new()
    vs = [[bm.verts.new((float(x), y, float(z))) for (x, z) in R] for (y, R) in rings]
    m = len(rings[0][1])
    for j in range(len(vs) - 1):
        for k in range(m - 1):
            bm.faces.new((vs[j][k], vs[j][k + 1], vs[j + 1][k + 1], vs[j + 1][k]))
    c = bm.verts.new((0.0, rings[-1][0], 0.0))
    for k in range(m - 1):
        bm.faces.new((vs[-1][k], vs[-1][k + 1], c))
    bm.normal_update()
    # the channel's lowest face (back centre) must face up into the cavity
    mid = vs[len(vs) // 2][m // 2]
    f0 = mid.link_faces[0]
    if f0.normal.z < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.shade_smooth()
    return link(bpy.data.objects.new(name, me))


def head_bowl():
    """The canon head (built without holes: the pins stand there) cut to its lower half, faces reversed: the cavity's
    head and neck. Returns (walls, floor) objects in racket model space."""
    parts = C.build_head("CavHead", holes=[])
    walls_bm, floor_bm = bmesh.new(), bmesh.new()
    for key, ob in parts.items():
        me = ob.data
        if key in ("face", "holes") or len(me.polygons) == 0:
            bpy.data.objects.remove(ob)
            continue
        if me.has_custom_normals:
            me.normals_split_custom_set([(0.0, 0.0, 0.0)] * len(me.loops))
        bm = bmesh.new(); bm.from_mesh(me)
        g = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=g, dist=1e-7, plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_outer=True)
        if key == "neck":  # the neck stops where the grip channel takes over (its core runs on under the grip)
            g = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=g, dist=1e-7, plane_co=(0, C.GRIP_Y[0], 0), plane_no=(0, -1, 0),
                                   clear_outer=True)
        bm.normal_update()
        if key == "back":
            nz = sum(f.normal.z for f in bm.faces) / max(1, len(bm.faces))
            print(f"  bowl back: {len(bm.faces)} faces, mean normal z {nz:+.3f} (outward = -1)", flush=True)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        tmp = bpy.data.meshes.new("tmp_" + key)
        bm.to_mesh(tmp); bm.free()
        (floor_bm if key == "back" else walls_bm).from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
        bpy.data.objects.remove(ob)
    out = []
    for name, bm in (("CavityWalls", walls_bm), ("CavityFloor", floor_bm)):
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me); bm.free()
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(30))
        out.append(link(bpy.data.objects.new(name, me)))
    return out


def cavity_poly(rings):
    """The cavity rim in plan (racket model space, before the 0.4 % growth): the canon outline (head + neck, the
    build_head fillets) united with the handle channel's rim, minus the throat (an island of the plate)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    head = Polygon(C.outline_canon()).buffer(0)
    throat = Polygon(KT.throat_loop(0.0035)).buffer(0)
    right = [(float(R[-1][0]), y) for (y, R) in rings]
    left = [(float(R[0][0]), y) for (y, R) in rings]
    hp = Polygon(right + left[::-1]).buffer(0)
    return unary_union([head, hp]).difference(throat)


def to_world_cavity(ob):
    ob.data.transform(rk_matrix() @ Matrix.Diagonal((CAV_SCALE, CAV_SCALE, 1.0, 1.0)))
    ob.data.update()


def build_mould(mats):
    from shapely import affinity
    from shapely.geometry import Polygon
    t0 = time.time()
    rings = handle_rings()
    walls, floor = head_bowl()
    hand = lathe_half("CavityHandle", rings)
    # join the handle channel into the walls
    bm = bmesh.new(); bm.from_mesh(walls.data); bm.from_mesh(hand.data)
    bm.to_mesh(walls.data); bm.free()
    bpy.data.objects.remove(hand)
    walls.data.shade_smooth()
    walls.data.set_sharp_from_angle(angle=math.radians(30))
    for ob in (walls, floor):
        to_world_cavity(ob)
    walls.data.materials.append(mats["walls"])
    floor.data.materials.append(mats["floor"])
    cp = affinity.scale(cavity_poly(rings), CAV_SCALE, CAV_SCALE, origin=(0, 0))
    print(f"  cavity surfaces {round(time.time() - t0, 1)} s, rim area {cp.area * 1e4:.0f} cm2", flush=True)
    # the plate, cut by a prism 0.3 mm outside the rim (its walls hide behind the cavity surfaces)
    plate = box("Plate", -PXH, PXH, -PYH, PYH, -PT, 0.0, bevel=CH, segs=3)
    plate.data.materials.append(mats["satin"])
    cut = prism("CavCut", cp.buffer(CUT_GROW, join_style=1), -0.026, 0.01)
    cut.data.materials.append(mats["cutwall"])     # plain polished steel: the plate must not inherit the channel glow
    boolean(plate, cut)
    bpy.data.objects.remove(cut)
    tx = engraving_cutter()
    tx.data.materials.append(mats["engrave"])
    boolean(plate, tx)
    bpy.data.objects.remove(tx)
    me = plate.data
    me.shade_smooth()
    crisp_planes(me)
    print(f"  plate {len(me.polygons)} faces, {round(time.time() - t0, 1)} s", flush=True)
    # shut-off land (0.3 mm over the rim) and flash groove: flat overlays on the parting face
    ext = Polygon(cp.exterior)
    land = ext.buffer(LAND_W, resolution=24).difference(ext.buffer(-LAND_OVER, resolution=24))
    lo = poly_mesh("Land", land, 0.00002)
    lo.data.materials.append(mats["land"])
    core = Polygon(cp.interiors[0]) if cp.interiors else None
    li = io = None
    if core is not None:
        isl = core.buffer(LAND_OVER, resolution=24).difference(core.buffer(-LAND_W, resolution=24))
        li = poly_mesh("LandIsland", isl, 0.00002)
        li.data.materials.append(mats["land"])
        # the throat island's top: a satin overlay the sky does not light (through the racket's throat window it
        # would otherwise mirror the sky past the racket's side as a bright wedge)
        io = poly_mesh("IslandTop", core.buffer(-LAND_W * 0.5), 0.00001)
        io.data.materials.append(mats["satin"])
    groove = ext.buffer(GROOVE_OUT, resolution=24).difference(ext.buffer(GROOVE_IN, resolution=24))
    go = poly_mesh("Groove", groove, 0.000025)
    go.data.materials.append(mats["groove"])
    for o_ in (lo, go):
        o_.data.shade_flat()
    return {"plate": plate, "walls": walls, "floor": floor, "land": lo, "groove": go, "island": [x for x in (li, io) if x]}


def engraving_cutter():
    cu = bpy.data.curves.new("Eng", "FONT")
    cu.body = ENGRAVE
    cu.font = bpy.data.fonts.load(racket.FONT_MED, check_existing=True)
    cu.size = ENG_SIZE
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.space_character = 1.08
    cu.extrude = ENG_DEPTH
    cu.bevel_depth = 0.0
    tob = link(bpy.data.objects.new("EngTmp", cu))
    me = bpy.data.meshes.new_from_object(tob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tob)
    xs = [v.co.x for v in me.vertices]
    width = max(xs) - min(xs)
    rot = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    xc = -(PXH - ENG_MARGIN - width / 2)
    me.transform(Matrix.Translation((xc, PYH, ENG_Z)) @ rot)
    return link(bpy.data.objects.new("Engrave", me))


def build_pins(mats):
    """42 pins at the canonical positions: 14.0 mm under the crown of 8, 12.4 mm under the 34 (grown 0.4 %)."""
    protos, pins = {}, []
    for (hx, hy, hr) in C.holes_canon():
        r = round(hr * U * CAV_SCALE, 6)
        if r not in protos:
            p = cylinder("Pin%d" % len(protos), r, -0.0195, PIN_TOP, verts=72, top_bevel=0.0012, segs=6)
            p.data.materials.append(mats["pin"])
            p.data.materials.append(mats["pintop"])
            for poly in p.data.polygons:
                if poly.normal.z > 0.995:
                    poly.material_index = 1
            protos[r] = p
            o_ = p
        else:
            o_ = link(protos[r].copy())
        X, Y = rk2w(hx * U * CAV_SCALE, hy * U * CAV_SCALE)
        o_.location = (X, Y, protos[r].location.z)
        pins.append(o_)
    return pins


def build_pillars(mats):
    out = []
    for (x, y) in PIL_XY:
        p = cylinder("Pillar", PIL_R, -0.006, PIL_TOP, x, y, verts=128, top_bevel=0.0025, segs=2)
        p.data.materials.append(mats["pillar"])
        out.append(p)
        bu = cylinder("Bushing", BUSH_R, -0.002, BUSH_H, x, y, verts=128, top_bevel=BUSH_CH, segs=3)
        bu.data.materials.append(mats["bushing"])
        out.append(bu)
    return out


# ------------------------------------------------------------------ the racket (canon) and its helpers

SHIELD_INSET = 0.007


def underside_shield(root):
    """Shadow-only plate 0.4 mm under the racket's flat back face, with the 42 hole openings and the throat cut out and
    inset SHIELD_INSET from the outline: the warm cavity light reaches the bores and the outer band (a thin warm line
    on the head's lower edge) but not the flat underside, which the polished floor would mirror as a broad wash."""
    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union
    cuts = unary_union([Polygon(KT.throat_loop(0.0035)).buffer(0.0095)] +
                       [Point(hx * U, hy * U).buffer(hr * U + 0.0011, resolution=16) for (hx, hy, hr) in C.holes_canon()])
    shape = Polygon(C.outline_canon()).buffer(-SHIELD_INSET).difference(cuts)
    ob = poly_mesh("UnderShield", shape, 0.0, to_world=False)
    m, b = new_mat("ShieldBlack")
    b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    b.inputs["Roughness"].default_value = 1.0
    ob.data.materials.append(m)
    ob.matrix_world = root.matrix_world @ Matrix.Translation((0, 0, -T2 - 0.0004))
    for attr in ("visible_camera", "visible_glossy", "visible_diffuse", "visible_transmission", "visible_volume_scatter"):
        setattr(ob, attr, False)
    plug = poly_mesh("ThroatPlug", Polygon(KT.throat_loop(0.0035)).buffer(0.0105), 0.0, to_world=False)
    plug.matrix_world = root.matrix_world @ Matrix.Translation((0, 0, -T2 - 0.0005))
    for attr in ("visible_camera", "visible_glossy", "visible_diffuse", "visible_transmission", "visible_volume_scatter"):
        setattr(plug, attr, False)
    return ob, plug


# ------------------------------------------------------------------ lights


def card(name, loc, size, strength, target, color=(1, 1, 1), profile="flat", group=None, roll=0.0,
         transparent=True, ell=(1.0, 1.0), power=1.0, sweep=(0.35, 0.75)):
    """Camera-invisible emissive plane. profile: flat | ellipse (radial falloff) | sweep (falloff edge along x) |
    bar (bright centre line along x) | softbox (look_c's gradient)."""
    if profile == "softbox":
        ob = look_c.softbox(name, loc, size, strength, target, gradient=True, color=color)
    else:
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
        ob = bpy.context.active_object
        ob.name = name
        ob.scale = (size[0], size[1], 1)
        studio.aim(ob, target)
        m = bpy.data.materials.new(name + "Mat")
        m.use_nodes = True
        nt = m.node_tree
        for nd in list(nt.nodes):
            nt.nodes.remove(nd)
        nb = NB(m)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*color, 1)
        if profile == "flat":
            em.inputs["Strength"].default_value = strength
        else:
            x, y, _ = nb.xyz("Generated")
            dx = nb.math("DIVIDE", nb.math("SUBTRACT", x, 0.5), 0.5 * ell[0])
            dy = nb.math("DIVIDE", nb.math("SUBTRACT", y, 0.5), 0.5 * ell[1])
            if profile == "ellipse":
                r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", dx, dx), nb.math("MULTIPLY", dy, dy)))
                f = nb.smooth(r, 1.0, 0.0)
            elif profile == "bar":
                f = nb.math("MULTIPLY", nb.smooth(nb.math("ABSOLUTE", dy), 1.0, 0.0),
                            nb.smooth(x, sweep[1], sweep[0], 1.0, 0.25))
            else:
                f = nb.math("MULTIPLY", nb.smooth(x, sweep[1], sweep[0]),
                            nb.smooth(nb.math("ABSOLUTE", dy), 1.0, 0.55))
            f = nb.math("POWER", f, power)
            nb.l.new(nb.math("MULTIPLY", f, strength), em.inputs["Strength"])
        shader = em.outputs[0]
        if transparent:
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            add = nt.nodes.new("ShaderNodeAddShader")
            nt.links.new(em.outputs[0], add.inputs[0]); nt.links.new(tr.outputs[0], add.inputs[1])
            shader = add.outputs[0]
        nt.links.new(shader, out.inputs["Surface"])
        ob.data.materials.append(m)
        ob.visible_camera = False
    if roll:
        ob.rotation_euler.rotate_axis("Z", math.radians(roll))
    if group:
        ob.lightgroup = group
    return ob


def line_strip(name, q1, q2, width, strength, target, color=(1, 1, 1), group=None, extra=0.35):
    """Thin emissive strip from q1 to q2 (plus a margin), facing target: a hairline along a whole edge."""
    mid = (q1 + q2) / 2
    along = (q2 - q1).normalized()
    to_t = (Vector(target) - mid).normalized()
    n = (to_t - along * to_t.dot(along)).normalized()
    x = along.cross(n).normalized()
    rot = Matrix((x, along, n)).transposed().to_4x4()
    bpy.ops.mesh.primitive_plane_add(size=1, location=mid)
    ob = bpy.context.active_object
    ob.name = name
    ob.matrix_world = Matrix.Translation(mid) @ rot @ Matrix.Diagonal((width, (q2 - q1).length + extra, 1, 1))
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(em.outputs[0], add.inputs[0]); nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    ob.visible_camera = False
    if group:
        ob.lightgroup = group
    return ob


def mirror_dir(n, p, cam):
    n = Vector(n).normalized()
    v = (Vector(cam) - Vector(p)).normalized()
    return (2 * n.dot(v) * n - v).normalized()


def include_only(light_obj, objs, name):
    coll = bpy.data.collections.new(name)
    for ob in objs:
        coll.objects.link(ob)
    light_obj.light_linking.receiver_collection = coll


def exclude_from(light_obj, objs, name, blocker=False):
    coll = bpy.data.collections.new(name)
    for ob in objs:
        coll.objects.link(ob)
    if blocker:
        light_obj.light_linking.blocker_collection = coll
    else:
        light_obj.light_linking.receiver_collection = coll
    for co in coll.collection_objects:
        co.light_linking.link_state = "EXCLUDE"


def backdrop_card(cam_loc, target):
    """Camera-only graded card: a soft elliptical lift behind the racket head and throat (in screen space, via Window
    coordinates), falling to near-black at the corners."""
    d = (Vector(target) - Vector(cam_loc)).normalized()
    loc = Vector(target) + d * 2.4
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = "Backdrop"
    ob.scale = (7.0, 5.0, 1)
    studio.aim(ob, cam_loc)
    m = bpy.data.materials.new("BackdropMat")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    nb = NB(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    x, y, _ = nb.xyz("Window")
    dx = nb.math("DIVIDE", nb.math("SUBTRACT", x, BACK_C[0]), BACK_R[0])
    dy = nb.math("DIVIDE", nb.math("SUBTRACT", y, BACK_C[1]), BACK_R[1])
    r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", dx, dx), nb.math("MULTIPLY", dy, dy)))
    f = nb.math("POWER", nb.smooth(r, 1.0, 0.0), BACK_P)
    val = nb.math("MULTIPLY_ADD", f, BACK_HI - BACK_LO, BACK_LO)
    em.inputs["Color"].default_value = (0.94, 0.96, 1.0, 1)
    nb.l.new(val, em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    for attr in ("visible_glossy", "visible_diffuse", "visible_transmission", "visible_volume_scatter", "visible_shadow"):
        setattr(ob, attr, False)
    ob.lightgroup = "lg_fill"
    return ob


# backdrop: window-space centre (x, y from bottom), radii, falloff power, linear emission low/high
BACK_C, BACK_R, BACK_P, BACK_LO, BACK_HI = (0.47, 0.62), (0.62, 0.62), 1.3, 0.020, 0.046

KEY_POS, KEY_AIM, KEY_E, KEY_CONE, KEY_BLEND, KEY_RAD = (0.03, -0.14, 2.6), (0.03, 0.0, 0.0), 1400.0, 11.0, 0.45, 0.10
KEY_COL = (1.0, 0.94, 0.88)               # 5600 K against the D65 white point
SKY_S, SKY_DIST, SKY_SIZE, SKY_ELL, SKY_POW = 1.3, 1.8, (2.0, 1.4), (0.8, 1.0), 1.5
FACE_S, FACE_DIST = 0.8, 0.22
EDGE_PS, RIMW_PS, RIM_PS, RIMV_PS, RIM_PW = 12.0, 8.0, 30.0, 20.0, 0.45
RIM_S = 14.0
LAND_S = 0.9
PINS_S, PINS_X = 6.0, 0.45
PIL_L, PIL_R2 = 2.5, 0.6
CAV_E = 12.0

# the racket's own rig (lg_racket)
WHITE = (0.95, 0.97, 1.0)
RK_SKY, RK_BAND, RK_A, RK_B = 2.6, 0.028, (0.115, -0.105), (-0.085, 0.125)   # band strength, half width, line a-b (world XY off OX)
RK_GLOSS, RK_GOFF, RK_GW = 6.0, -0.034, 0.0016
RK_WHITE, RK_PHI_W, RK_EW = 60.0, 42.0, 0.03       # far-edge hairline (mirror-path ribbon)
RK_NEAR, RK_PHI_N = 14.0, 55.0                      # near-edge hairline, softer
RKN_Y = (-0.10, -0.03)                              # model y where the near hairline fades in (toward the throat)
RK_WALL, RK_WALL_D = 1.6, 0.45                     # near wall graded card
RK_LIP, RK_LIP_SIZE, RK_LIP_H = 25.0, 0.3, 1.0      # hole-lip crescents
RK_GRIP, RK_GRIP2 = 1.0, 0.25
RK_CAP = 0.35
RK_UNDER = 18.0
RK_EMBER = 14.0                                    # v17's ember card from behind-right (pins, pillars, racket)

# v19 (owner, 2026-10-22): Command is WHITE 3K twill. The black-carbon rig above lights by reflection only and leaves
# white a flat grey (canon lighting note 8), so a white racket gets real diffuse light, linked to its head parts only
# (the overgrip and the cap keep their strips): a soft spot pool from the frame's upper left (the head tip, far side),
# so the face falls from white at the tip to white-in-shade at the throat; a weak fill from the front right; a low soft
# card for the near 38 mm wall (the twill folding over the edge, SWISS MADE); one thin gloss line instead of the band;
# a dim underside (the polished cavity mirrors it) and a softer cavity lift (on white bores the 2200 K glow read 20x
# hotter than on black). Values for a black racket are untouched (FEEL = "command" + {"white": 0}).
FEEL, MAT_OPTS = "command", None
# Pace (Release 2 feel toggle, 2026-10-23): --feel pace builds the canon Pace (kq_canon.PACE v6, black 12K) in the same
# mould, camera, plate rig, cavity glow and comp (base and full from one render). Only the face follows the feel: black
# carbon takes the racket's black rig above (projected band, gloss line, hairline ribbons, wall card, lip disc, the
# cool underside and v18's cavity lift on the bores), plus K08 / K11 / K01's Pace recipe: an off-specular weave card
# only the 12K's fibre lobes see (P_WEAVE_*: the tapes read instead of a black hole), and no ember on the racket (the
# plate and pins keep theirs; the racket's edges stay neutral). The handle keeps Command's lights (no neck-only light).
# Read from argv here, before the module constants are set; default "command" leaves every Command output identical.
if "--feel" in sys.argv:
    FEEL = sys.argv[sys.argv.index("--feel") + 1]
    assert FEEL in ("command", "pace"), FEEL
PACE = FEEL == "pace"
P_WEAVE_S, P_WEAVE_UP, P_WEAVE_D, P_WEAVE_SIZE = 6.0, 20.0, 1.3, (1.6, 1.0)   # weave card (W, deg off the mirror, m, m)
P_CLAMP = 0.0                                                                   # indirect clamp; 0 = off
PACE_SET = dict()                                                               # Pace overrides of the black rig
WHITE_RK = C.is_white(FEEL, MAT_OPTS)
RKW_POOL, RKW_POOL_DEG, RKW_POOL_R = 250.0, 22.0, 0.06
RKW_POOL_AT, RKW_POOL_T = (0.15, -0.32, 1.12), (0.10, -0.05)      # from the head centre (world, m); aim offset (X, Y)
# (mostly overhead: from further left the curved wall round the tip took as much light as the face and the racket
# read as a thick white block; overhead, the wall falls to white-in-shade under a face-lit top)
RKW_FILL, RKW_FILL_AT = 1.0, (-0.30, 0.30, 1.00)
RKW_WALL, RKW_WALL_AT = 0.5, (0.05, 0.75, -0.02)
# v20 (art director, stage 3a):
# - the near 38 mm wall rendered charcoal (luma 40-50 under a face of 170-210): a white plate on a black puck, the
#   "two stacked plates" again. RKW_WALL is now a real low front card (1.0 x 0.25 m, camera side, below the face
#   plane so the face and the bores never see it), linked to wall, etchL, etchR and the neck's rounding only: the
#   wall reads as white twill in shade (target 100-130, about 0.6-0.75 of the face, as canon q34).
# - the 1.6 mm gloss line read as a crease in the laminate: replaced by one soft clear-coat sweep designed on the face
#   (kw_sheen.gloss_sweep: glossy-only, honeycomb, smoothstep profile), linked to face + neck so it runs on past the
#   split; RK_GLOSS is 0 on white.
# - a hard tone step where the face meets the neck: RkGrip and the ember RimEmber lit the neck but not the face. On
#   white they no longer touch the neck (WHITE_NECK_SPLIT = False), so face and neck share every light.
# - with the neck-only lights gone, the throat and neck fell into shade together (no step, but a grey neck): a second
#   soft spot from the pool's side, aimed at the neck and linked to face, neck, rim and wall (RKW_NECK; the same parts
#   on both sides of the split, so the gradient runs on with no step; not the throat walls or bores).
RKW_NECK, RKW_NECK_DEG, RKW_NECK_Y = 60.0, 12.0, -0.165    # W, cone (deg), model y of the aim point
RKW_SWEEP, RKW_SWEEP_W, RKW_SWEEP_H = 9.0, 0.030, 0.9      # strength, half width on the face (m), card height (m)
RKW_SWEEP_C, RKW_SWEEP_ANG, RKW_SWEEP_L = (0.0, -0.012), 150.0, 0.16   # centre (model x, y), angle (deg), half length
WHITE_SET = dict(RK_SKY=0.0, RK_GLOSS=0.0, RK_UNDER=2.5, RK_LIP=6.0, RK_WALL=0.0, RK_WHITE=30.0, RK_NEAR=20.0,
                 CAV_E=1.0, RKW_WALL=4.5, RKW_WALL_AT=(0.0, 0.85, -0.10), RKN_Y=(-0.150, -0.115))
# (v20: with the wall lifted, the unlit near rim read as a dark seam line where the hairline faded out toward the
# throat; the near hairline now runs on to the neck, and the wall card also lights the rim's lower half)
if WHITE_RK:
    globals().update(WHITE_SET)
if PACE:
    globals().update(PACE_SET)


def lights(cam_loc, g):
    plate, rk = g["plate"], g["rk"]
    out = []
    # lg_top: wide elliptical-gradient panel behind the mould; the satin parting face mirrors it as a sheen that is
    # brightest behind the cavity and falls away to the plate's ends and corners
    p = Vector((0.0, -0.02, 0))
    r = mirror_dir((0, 0, 1), p, cam_loc)
    sky = card("Sky", tuple(p + r * SKY_DIST), SKY_SIZE, SKY_S, tuple(p), profile="ellipse", group="lg_top",
               ell=SKY_ELL, power=SKY_POW)
    exclude_from(sky, rk + g["island"], "SkyNoRacket")
    out.append(sky)
    # front top edge: one crisp white hairline (the chamfer mirrors a strip above and behind the camera)
    p = Vector((0, PYH - CH / 2, -CH / 2))
    r = mirror_dir((0, 0.7071, 0.7071), p, cam_loc)
    el = card("EdgeLinePlate", tuple(p + r * 1.4), (3.6, 0.30), EDGE_PS, tuple(p), color=(0.92, 0.96, 1.0),
              group="lg_top")
    el.visible_shadow = False
    include_only(el, [plate], "EdgePlateRecv")
    out.append(el)
    # camera-left end: a cool white hairline along the top edge
    ends = []
    for yy in (-PYH + 0.01, PYH - 0.01):
        q = Vector((PXH - CH / 2, yy, -CH / 2))
        ends.append(q + mirror_dir((0.7071, 0, 0.7071), q, cam_loc) * 1.6)
    lw = line_strip("RimWhitePlate", ends[0], ends[1], RIM_PW, RIMW_PS, Vector((PXH, 0, 0)), color=(0.92, 0.96, 1.0),
                    group="lg_top", extra=0.05)
    lw.visible_shadow = False
    include_only(lw, [plate], "RimWhiteRecv")
    out.append(lw)
    # lg_rim: ember #ff3a1e hairlines from behind-right on the right-hand top edge and the front-right vertical edge
    ends = []
    for yy in (-PYH + 0.01, PYH - 0.01):
        q = Vector((-PXH + CH / 2, yy, -CH / 2))
        ends.append(q + mirror_dir((-0.7071, 0, 0.7071), q, cam_loc) * 1.6)
    rp = line_strip("RimEmberPlate", ends[0], ends[1], RIM_PW, RIM_PS, Vector((-PXH, 0, 0)), color=(1.0, 0.23, 0.12),
                    group="lg_rim", extra=0.05)
    rp.visible_shadow = False
    include_only(rp, [plate], "RimPlateRecv")
    out.append(rp)
    ends = []
    for zz in (-PT + 0.01, -0.01):
        q = Vector((-PXH + CH / 2, PYH - CH / 2, zz))
        ends.append(q + mirror_dir((-0.7071, 0.7071, 0), q, cam_loc) * 1.2)
    rv = line_strip("RimEmberVert", ends[0], ends[1], RIM_PW * 0.6, RIMV_PS, Vector((-PXH, PYH, -PT / 2)),
                    color=(1.0, 0.23, 0.12), group="lg_rim", extra=0.02)
    rv.visible_shadow = False
    include_only(rv, [plate], "RimVertRecv")
    out.append(rv)
    # the same ember from behind-right for the pins and pillars (and the racket's handle end)
    re = card("RimEmber", (-1.5, -0.9, 0.55), (0.05, 1.6), RIM_EMBER_S(), (0.0, 0.0, 0.08), color=(1.0, 0.23, 0.12),
              group="lg_rim")
    include_only(re, g["pins"] + g["pillars"] + C.objs(g["P"], "grip", "cap", *(() if PACE else ("rim",) if WHITE_RK else ("rim", "neck"))),
                 "RimEmberRecv")
    out.append(re)
    # front face: a close strip in front of and below the top edge: the face fades from steel at the top to void
    p = Vector((0, PYH, -0.006))
    cpr = Vector((cam_loc[0], 2 * PYH - cam_loc[1], cam_loc[2]))
    fs = card("FaceSheen", tuple(p + (p - cpr).normalized() * FACE_DIST), (3.4, 0.04), FACE_S, tuple(p),
              group="lg_fill")
    fs.visible_shadow = False
    include_only(fs, [plate], "FaceRecv")
    out.append(fs)
    # lg_key: overhead hard key, 5600 K, 11 deg cone, a few degrees behind vertical. Through the racket's 42 holes it
    # lands on the 42 pins; it pools on the cavity zone and falls off to the plate's corners; the racket shades it.
    key = studio.spot_light("Key", KEY_POS, KEY_E, KEY_CONE, KEY_BLEND, color=KEY_COL, target=KEY_AIM, radius=KEY_RAD)
    key.lightgroup = "lg_key"
    # (not the throat island: through the racket's throat window it read as a hot white wedge)
    exclude_from(key, rk + g["island"], "KeyNoRacket")
    out.append(key)
    # the land ring: a transparent emitter sheet above the cavity that only the polished land sees
    ls = card("LandSheet", (0.0, 0.05, 0.035), (0.9, 0.27), LAND_S, (0.0, 0.05, 1.0), profile="ellipse",
              group="lg_key", transparent=True, ell=(1.1, 1.5), power=0.5)
    ls.visible_shadow = False
    include_only(ls, [g["land"]] + g["island"][:1], "LandRecv")
    out.append(ls)
    # pins (lg_pins): their flanks mirror the floor in front of them, which mirrors the space above and in front. A
    # tall thin strip there, linked to the pins and the floor, draws one vertical streak down every pin.
    ps = line_strip("PinStrip", Vector((PINS_X, 1.25, 0.25)), Vector((PINS_X, 1.25, 1.55)), 0.05, PINS_S,
                    Vector((OX, 0.0, 0.0)), color=(0.9, 0.95, 1.0), group="lg_pins", extra=0.0)
    ps.visible_shadow = False
    include_only(ps, g["pins"] + [g["floor"]], "PinStripRecv")
    out.append(ps)
    # pillars: soft graded cards left (brighter) and right, seen only by the pillars and bushings
    pil = g["pillars"]
    for nm, x, s in (("PillarL", 1.0, PIL_L), ("PillarR", -1.0, PIL_R2)):
        c = card(nm, (x * 0.55, 1.30, -0.50), (1.4, 1.2), s, (x * 0.395, 0.145, -0.50), profile="ellipse",
                 group="lg_fill", ell=(1.0, 1.0), power=0.7)
        c.visible_shadow = False
        include_only(c, pil, nm + "Recv")
        out.append(c)
    return out


def RIM_EMBER_S():
    return RK_EMBER


def look_at(ob, loc, tgt, up):
    CT.look_at(ob, loc, tgt, up)


def racket_lights(cam_loc, g):
    """lg_racket: the canon racket's own linked rig (canon lighting notes 1-6)."""
    P, root = g["P"], g["root"]
    M = root.matrix_world.copy()
    zf = HOVER + T2
    out = []
    face_set = C.objs(P, "face", "holes", "rim", "neck", "throat", "bridgewall")
    # 1. the face: a projected band softbox (lit twill in one diagonal, deep black gloss elsewhere) + a gloss line
    a_ = (OX + RK_A[0], RK_A[1], zf)
    b_ = (OX + RK_B[0], RK_B[1], zf)
    ctr = (OX + 0.01, 0.0, zf)
    if RK_SKY > 0:
        sky = KT.sky_projected("RkSky", cam_loc, zf, a_, b_, ctr, (2.4, 2.4), 1.0, 0.0, 0.0, RK_SKY, color=WHITE,
                               band=(0.0, RK_BAND), group="lg_racket")
        KT.link_only(sky, face_set, "RkSkyRecv")
        out.append(sky)
    if RK_GLOSS > 0:
        gl = KT.sky_projected("RkGloss", cam_loc, zf, a_, b_, ctr, (3.2, 3.2), 1.4, 0.0, 0.0, RK_GLOSS, color=WHITE,
                              band=(RK_GOFF, RK_GW), group="lg_racket")
        KT.link_only(gl, [P["face"]], "RkGlossRecv")
        out.append(gl)
    # 2. hairlines: mirror-path ribbons along the front 1.5 mm edge (computed in model space, then posed)
    cam_m = M.inverted() @ Vector(cam_loc)
    sm = CT.sm
    if RK_WHITE > 0:   # far edge (model +x = world -Y): the top of the silhouette, tip to the shoulders
        rb = CT.edge_ribbon("RkWhite", cam_m, lambda x, y: sm(x, -0.05, 0.0) * sm(y, -0.11, -0.05), RK_PHI_W, 0.15,
                            RK_EW, RK_WHITE, WHITE, [P["rim"]])
        if rb:
            rb.matrix_world = M
            rb.lightgroup = "lg_racket"
            out.append(rb)
    if RK_NEAR > 0:    # near edge (model -x = world +Y): a softer line between the face and the near wall
        rb = CT.edge_ribbon("RkNear", cam_m, lambda x, y: sm(-x, 0.03, 0.08) * sm(y, RKN_Y[0], RKN_Y[1]), RK_PHI_N, 0.15,
                            RK_EW, RK_NEAR, WHITE, [P["rim"]])
        if rb:
            rb.matrix_world = M
            rb.lightgroup = "lg_racket"
            out.append(rb)
    # 3. the near 38 mm wall: a graded card where it mirrors (in front of and below the racket)
    if RK_WALL > 0:
        p = Vector((OX, 0.13, HOVER))
        r = mirror_dir((0, 1, 0), p, cam_loc)
        wl = card("RkWall", tuple(p + r * RK_WALL_D), (0.8, 0.16), RK_WALL, tuple(p), profile="sweep",
                  group="lg_racket", sweep=(0.15, 0.95))
        wl.visible_shadow = False
        include_only(wl, C.objs(P, "wall", "rim", "neck", "etchL"), "RkWallRecv")
        out.append(wl)
    # 4. hole lips: a soft overhead disc linked to the holes part only (a crescent on the far lip of every hole)
    if RK_LIP > 0:
        ld = bpy.data.lights.new("RkLip", "AREA")
        ld.shape = "DISK"
        ld.size = RK_LIP_SIZE
        ld.energy = RK_LIP
        ld.color = KEY_COL
        lk = link(bpy.data.objects.new("RkLip", ld))
        lk.location = (OX + 0.012, -0.05, HOVER + RK_LIP_H)
        studio.aim(lk, (OX + 0.012, 0.0, HOVER))
        include_only(lk, [P["holes"]], "RkLipRecv")
        lk.lightgroup = "lg_racket"
        out.append(lk)
    # 5. the overgrip (strip along it from above and in front, so the helical wrap catches light) and the cap's Q
    gc = M @ Vector((0.0, -0.229, 0.0))
    axis = (M.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
    for nm, off_y, hgt, wd, en in (("RkGrip", 0.24, 0.30, 0.02, RK_GRIP), ("RkGrip2", -0.30, 0.10, 0.03, RK_GRIP2)):
        if en <= 0:
            continue
        loc = gc + Vector((0.0, off_y, hgt))
        lt = studio.area_light(nm, tuple(loc), wd, en, color=WHITE, size_y=0.30)
        look_at(lt, loc, gc, up=tuple(axis))
        include_only(lt, C.objs(P, "grip", "cap", "capmark") + ([P["neck"]] if nm == "RkGrip" and not (WHITE_RK or PACE) else []),
                     nm + "Recv")
        lt.lightgroup = "lg_racket"
        out.append(lt)
    if RK_CAP > 0:
        pr = C.cap_profile()
        yk = -0.2998 + C.CAP_SHIFT
        s_k = float(np.interp(-yk, [-y for (_, y) in pr], [s_ for (s_, _) in pr]))
        G, _ = C.section(64, grow=C.TAPE)
        pk = M @ Vector((0.0, yk, float(G[:, 1].max()) * s_k))
        rk_ = mirror_dir((0, 0, 1), pk, cam_loc)
        ck = studio.area_light("RkCap", tuple(pk + rk_ * 0.35), 0.30, RK_CAP, color=WHITE, size_y=0.10, target=tuple(pk))
        include_only(ck, C.objs(P, "cap", "capmark"), "RkCapRecv")
        ck.lightgroup = "lg_racket"
        out.append(ck)
    # 6. a soft cool light from below: the underside the polished floor and the parting face mirror reads graphite
    if RK_UNDER > 0:
        ld = bpy.data.lights.new("RkUnder", "AREA")
        ld.shape = "ELLIPSE"
        ld.size, ld.size_y = 0.42, 0.22
        ld.energy = RK_UNDER
        ld.color = (0.85, 0.9, 1.0)
        under = link(bpy.data.objects.new("RkUnder", ld))
        under.location = (0.0, 0.0, 0.012)
        under.rotation_euler = (math.pi, 0, 0)
        include_only(under, g["rk"], "RkUnderRecv")
        exclude_from(under, [g["shield"], g["plug"]], "RkUnderNoShield", blocker=True)
        under.lightgroup = "lg_racket"
        for a in ("visible_glossy", "visible_diffuse", "visible_transmission"):
            setattr(under, a, False)
        out.append(under)
    if WHITE_RK:
        out += white_lights(g)
    if PACE and P_WEAVE_S > 0:
        # the weave card (K08 / K11 / K01): a soft graded card P_WEAVE_UP degrees above the face's mirror direction; the
        # clear coat cannot see it, the 12K's fibre lobes stretched along one tape direction can, so alternate tapes light
        fc = Vector((OX - 0.02, 0.0, zf))
        d_ = mirror_dir((0, 0, 1), fc, cam_loc)
        hz_ = Vector((-d_.y, d_.x, 0)).normalized()
        d_up = (Matrix.Rotation(math.radians(P_WEAVE_UP), 3, hz_) @ d_).normalized()
        if d_up.z < d_.z:
            d_up = (Matrix.Rotation(math.radians(-P_WEAVE_UP), 3, hz_) @ d_).normalized()
        wv = KL.gradient_card("PaceWeave", tuple(fc + d_up * P_WEAVE_D), P_WEAVE_SIZE, P_WEAVE_S, tuple(fc),
                              color=KL.kelvin(6500), axis="v", lo=0.0, hi=1.0, floor=0.0)
        wv.lightgroup = "lg_racket"
        include_only(wv, C.objs(P, "face", "neck", "wall"), "PaceWeaveRecv")
        out.append(wv)
    return out


def white_lights(g):
    """The white racket's diffuse rig (lg_racket), linked to the head parts only (canon lighting note 8)."""
    P = g["P"]
    head = C.objs(P, "face", "back", "rim", "wall", "neck", "throat", "bridgewall", "holes", "etchR", "etchL")
    c = Vector((OX, 0.0, HOVER))
    out = []
    if RKW_POOL > 0:
        pl = studio.spot_light("RkPool", tuple(c + Vector(RKW_POOL_AT)), RKW_POOL, RKW_POOL_DEG, blend=1.0,
                               color=(1.0, 0.985, 0.97), target=(OX + RKW_POOL_T[0], RKW_POOL_T[1], HOVER),
                               radius=RKW_POOL_R)
        include_only(pl, head, "RkPoolRecv")
        pl.lightgroup = "lg_racket"
        out.append(pl)
    if RKW_FILL > 0:
        fl = studio.area_light("RkFill", tuple(c + Vector(RKW_FILL_AT)), 1.0, RKW_FILL, color=(0.94, 0.96, 1.0),
                               target=tuple(c))
        include_only(fl, head, "RkFillRecv")
        fl.lightgroup = "lg_racket"
        out.append(fl)
    if RKW_WALL > 0:   # the near wall faces the camera side (+Y): a low soft card in front of it
        wl = studio.area_light("RkWallW", tuple(c + Vector(RKW_WALL_AT)), 1.0, RKW_WALL, color=(1.0, 0.985, 0.97),
                               size_y=0.25, target=(OX, 0.13, HOVER))
        include_only(wl, C.objs(P, "wall", "rim", "neck", "etchL", "etchR"), "RkWallWRecv")
        wl.lightgroup = "lg_racket"
        out.append(wl)
    M = g["root"].matrix_world.copy()
    if RKW_NECK > 0:   # the throat and neck: a second soft pool from the pool's side (face + neck: no step at the split)
        tn = M @ Vector((0.0, RKW_NECK_Y, C.ZT))
        nl = studio.spot_light("RkNeckPool", tuple(tn + Vector(RKW_POOL_AT)), RKW_NECK, RKW_NECK_DEG, blend=1.0,
                               color=(1.0, 0.985, 0.97), target=tuple(tn), radius=RKW_POOL_R)
        include_only(nl, C.objs(P, "face", "neck", "rim", "wall"), "RkNeckPoolRecv")
        nl.lightgroup = "lg_racket"
        out.append(nl)
    if RKW_SWEEP > 0:  # one soft clear-coat sweep across the face, running on over the neck
        ca, sa = math.cos(math.radians(RKW_SWEEP_ANG)), math.sin(math.radians(RKW_SWEEP_ANG))
        c0 = Vector((RKW_SWEEP_C[0], RKW_SWEEP_C[1], C.ZT))
        dv = Vector((ca, sa, 0.0)) * RKW_SWEEP_L
        sw = KS.gloss_sweep("RkSweep", g["cam_loc"], M @ c0, M.to_3x3() @ Vector((0, 0, 1)), M @ (c0 - dv), M @ (c0 + dv),
                            RKW_SWEEP_W, RKW_SWEEP_H, RKW_SWEEP, C.objs(P, "face", "neck"), color=WHITE, group="lg_racket")
        out.append(sw)
    return out


def cavity_lights(g):
    """lg_cavity: a warm area light lying on the cavity floor, linked to the racket. The shadow-only shield lets it
    through the holes (amber bores) and past the outer 7 mm (a thin warm line on the head's lower edge)."""
    if CAV_E <= 0:
        return []
    ld = bpy.data.lights.new("CavityLift", "AREA")
    ld.shape = "ELLIPSE"
    ld.size, ld.size_y = 0.30, 0.22
    ld.energy = CAV_E
    ld.color = (1.0, 0.36, 0.09)
    ob = link(bpy.data.objects.new("CavityLift", ld))
    ob.location = (OX + 0.012, 0.0, -0.017)
    ob.rotation_euler = (math.pi, 0, 0)
    ob.lightgroup = "lg_cavity"
    include_only(ob, g["rk"], "CavityLiftRecv")
    # not visible to glossy rays: the shield only stops shadow rays, so the gloss underside would otherwise mirror the
    # lift itself and the satin plate would carry that reflection as a broad warm wash
    ob.visible_glossy = False
    return [ob]


# ------------------------------------------------------------------ camera


def camera():
    e = math.radians(ELEV)
    t = Vector(CAM_T)
    loc = t + Vector((0, math.cos(e), math.sin(e))) * CAM_D
    cam = studio.camera(tuple(loc), tuple(t), lens=LENS, fstop=8.0, shift=(0, CAM_SHIFT))
    # focus between the racket (hovering 12 cm up) and the pins: both within ~0.5 px of sharp at f/8
    cam.data.dof.focus_distance = (Vector(FOCUS_P) - loc).length
    return cam


FOCUS_P = (0.03, 0.0, 0.06)


def probe(cam, pts):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    for name, p in pts:
        v = world_to_camera_view(sc, cam, Vector(p))
        print(f"  {name:22s} x {v.x * 100:6.1f}%  y {100 - v.y * 100:6.1f}%  depth {v.z:.3f}")


# ------------------------------------------------------------------ main


def build(o):
    t0 = time.time()
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.light_sampling_threshold = 0.01
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 6
    sc.cycles.transparent_max_bounces = 12
    if PACE and P_CLAMP > 0:
        sc.cycles.sample_clamp_indirect = P_CLAMP
    vl = sc.view_layers[0]
    for gname in GROUPS:
        vl.lightgroups.add(name=gname)
    mats = {
        "satin": mat_satin(),
        "walls": mat_cavity_walls() if CH_S0 > 0 else mat_polished("CavityWall", WALL_R),
        "floor": mat_cavity_floor(),
        "cutwall": mat_polished("CutWall", WALL_R),
        "pin": mat_polished("PinSteel", PIN_ROUGH, color=(0.74, 0.74, 0.76)),
        "pintop": mat_polished("PinTop", PINTOP_R, color=(0.70, 0.70, 0.72)),
        "pillar": mat_polished("GroundPillar", PILLAR_R, aniso_axis=(0.0, 0.0, 1.0), color=(0.62, 0.625, 0.64),
                               aniso=PILLAR_A),
        "bushing": mat_polished("Bushing", 0.05, color=(0.70, 0.70, 0.72)),
        "land": mat_polished("Land", 0.03, color=(0.72, 0.725, 0.74)),
        "groove": mat_basic("Groove", (0.05, 0.05, 0.052), 0.45),
        "engrave": mat_basic("Engrave", (0.30, 0.30, 0.31), 0.48),
    }
    m = build_mould(mats)
    m["floor"].lightgroup = "lg_cavity"
    m["walls"].lightgroup = "lg_cavity"    # only the channel glow emits there (reflections stay in their lights' groups)
    pins = build_pins(mats)
    pillars = build_pillars(mats)
    # the canonical racket: Command, KQ-000427, face up, head toward +X, hovering HOVER above the parting face
    root, P = C.build_racket("KQ", feel=FEEL, serial="KQ-000427", mat_opts=MAT_OPTS)
    C.pose(root, (OX, 0.0, HOVER), yaw_deg=-90.0)
    bpy.context.view_layer.update()
    print("  racket", {k: round(v, 2) if isinstance(v, float) else v for k, v in C.measure(root).items()}, flush=True)
    shield, plug = underside_shield(root)
    rk = C.objs(P, "all")
    # the floor's glow lights the racket only through CavityLift (bores, lower edge), never as a broad wash
    exclude_from(m["floor"], rk, "FloorNoRacket")
    print("geometry", round(time.time() - t0, 1), "s", flush=True)
    g = dict(m, mats=mats, root=root, P=P, rk=rk, pins=pins, pillars=pillars, shield=shield, plug=plug)
    cam = camera()
    cam_loc = cam.location.copy()
    g["cam_loc"] = cam_loc
    backdrop_card(cam_loc, CAM_T)
    lights(cam_loc, g)
    racket_lights(cam_loc, g)
    cavity_lights(g)
    # every emitter must sit in a light group, or the base/full sums would drop it
    for ob in sc.objects:
        emits = ob.type == "LIGHT" or (ob.type == "MESH" and any(
            s.material and s.material.node_tree and any(n.type == "EMISSION" or (n.type == "BSDF_PRINCIPLED" and (
                n.inputs["Emission Strength"].default_value > 0 or n.inputs["Emission Strength"].is_linked))
                for n in s.material.node_tree.nodes) for s in ob.material_slots))
        if emits and not ob.lightgroup and ob.visible_camera + ob.visible_glossy + ob.visible_diffuse:
            print("  WARNING emitter without light group:", ob.name, flush=True)
    return sc, g


def render(o, sc):
    sc.render.resolution_x, sc.render.resolution_y = o["w"], o["h"]
    sc.cycles.samples = o["spp"]
    sc.render.use_border = bool(o["crop"])
    sc.render.use_crop_to_border = bool(o["crop"])
    if o["crop"]:
        x0, x1, y0, y1 = o["crop"]
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
    allg = {gname: 1.0 for gname in GROUPS}
    base = {k: v for k, v in allg.items() if k != "lg_cavity"}
    full = dict(allg, lg_pins=PINS_FULL)
    mixes = {"base": base, "full": full}
    KL.mix_compositor(sc, o, mixes)
    path = os.path.join(studio.OUT, o["out"] + ".png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render()
    rr = bpy.data.images["Render Result"]
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.color_mode = "RGB"
    rr.save_render(path, scene=sc)
    if o["exr"]:
        sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        sc.render.image_settings.exr_codec = "ZIP"
        rr.save_render(path.replace(".png", "_lg.exr"), scene=sc)
    KL.seq_rename(o)
    return path


def main():
    o = parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    t0 = time.time()
    if o["probe"]:
        studio.reset()
        studio.settings(o["w"], o["h"], o["spp"])
        cam = camera()
        bpy.context.view_layer.update()
        probe(cam, [("plate front-left top", (PXH, PYH, 0)), ("plate front-right top", (-PXH, PYH, 0)),
                    ("plate front bottom", (0, PYH, -PT)), ("plate far top", (0, -PYH, 0)),
                    ("racket tip", (OX + 0.155, 0, HOVER)), ("racket butt", (OX - 0.300, 0, HOVER)),
                    ("racket far top", (OX + 0.025, -0.13, HOVER + T2)),
                    ("cavity tip", (OX + 0.155, 0, 0)), ("cavity butt", (OX - 0.300, 0, 0))] +
              [(f"pillar {x:+.3f},{y:+.3f}", (x, y, 0)) for (x, y) in PIL_XY])
        return
    sc, g = build(o)
    if o.get("dry"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(studio.OUT, "k06c", "dry.blend"))
        print("dry", round(time.time() - t0, 1), "s")
        return
    p = render(o, sc)
    print("rendered", p, round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
