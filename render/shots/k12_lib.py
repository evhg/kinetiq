"""Shared helpers for K01-hero-beam and K02-edge-line.

Rounded-edge head (true 1.5 mm frame radius, 0.8 mm hole lips, analytic normals, UVs that run along every wall),
twill carbon with per-tow anisotropy under a glass-clear coat, black perforated grip, satin anodised cap with a
polished butt chamfer, emitters (strips, cards, ribbons), light linking, display-space calibration and the
display-space post grade. racket.py / studio.py / look_c.py are imported, never modified.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402

# ------------------------------------------------------------------ display calibration
# camera-visible emission radiance -> display value (0-255) under AgX Punchy (measured with shots/k12_calib.py)
_CAL_E = [0.0, 0.006, 0.010, 0.013, 0.016, 0.020, 0.025, 0.030, 0.035, 0.040, 0.05, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20, 0.3, 0.5, 1.0]
_CAL_D = [0, 1, 2, 4, 6, 10, 15, 19, 23, 27, 34, 41, 52, 61, 73, 82, 93, 115, 144, 177]


def emit_for(display):
    """Emission strength that renders as `display` (0-255 luma) through the studio view transform."""
    return float(np.interp(display, _CAL_D, _CAL_E))


def hex_luma(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def parse_args(argv, default_out, variants=("full",)):
    o = {"w": 960, "h": 540, "spp": 32, "out": default_out, "variant": variants[0], "crop": None, "lightgroups": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--w", "--h", "--spp"):
            o[a[2:]] = int(argv[i + 1]); i += 2
        elif a == "--out":
            o["out"] = argv[i + 1]; i += 2
        elif a == "--variant":
            o["variant"] = argv[i + 1]; i += 2
        elif a == "--crop":
            vals = argv[i + 1].split(",") if "," in argv[i + 1] else argv[i + 1:i + 5]
            o["crop"] = [float(v) for v in vals]
            i += 2 if "," in argv[i + 1] else 5
        elif a == "--lightgroups":
            o["lightgroups"] = True; i += 1
        else:
            i += 1
    assert o["variant"] in variants, o["variant"]
    return o


# ------------------------------------------------------------------ node helper


class NB:
    """Tiny node-graph builder: sockets or floats in, sockets out."""

    def __init__(self, mat):
        self.nt = mat.node_tree
        self.n, self.l = self.nt.nodes, self.nt.links

    def _in(self, sock, v):
        if v is None:
            return
        if isinstance(v, (int, float)):
            sock.default_value = v
        else:
            self.l.new(v, sock)

    def math(self, op, a, b=None, c=None, clamp=False):
        m = self.n.new("ShaderNodeMath"); m.operation = op; m.use_clamp = clamp
        self._in(m.inputs[0], a); self._in(m.inputs[1], b); self._in(m.inputs[2], c)
        return m.outputs[0]

    def smooth(self, v, e0, e1):
        """smoothstep from e0 to e1 (e0 > e1 gives a falling edge)."""
        m = self.n.new("ShaderNodeMapRange"); m.interpolation_type = "SMOOTHSTEP"
        m.inputs["From Min"].default_value = e0; m.inputs["From Max"].default_value = e1
        m.inputs["To Min"].default_value = 0.0; m.inputs["To Max"].default_value = 1.0
        self._in(m.inputs["Value"], v)
        return m.outputs["Result"]

    def lerp(self, t, a, b):
        """a + t (b - a) for floats/sockets."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return self.math("MULTIPLY_ADD", t, b - a, a)
        return self.math("ADD", a, self.math("MULTIPLY", t, self.math("SUBTRACT", b, a)))

    def coords(self, kind="Object"):
        tc = self.n.new("ShaderNodeTexCoord")
        sep = self.n.new("ShaderNodeSeparateXYZ")
        self.l.new(tc.outputs[kind], sep.inputs["Vector"])
        return sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]

    def gray(self, v):
        cc = self.n.new("ShaderNodeCombineColor")
        for k in range(3):
            self._in(cc.inputs[k], v)
        return cc.outputs[0]

    def gauss(self, x, c, w):
        d = self.math("DIVIDE", self.math("SUBTRACT", x, c), w)
        return self.math("EXPONENT", self.math("MULTIPLY", self.math("MULTIPLY", d, d), -1.0))


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    for n in list(m.node_tree.nodes):
        m.node_tree.nodes.remove(n)
    return m


def emitter_mat(name, color, strength_sock_fn, additive=True):
    """Emission (optionally added over transparency, so it never blocks what is behind)."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    em = nb.n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    nb._in(em.inputs["Strength"], strength_sock_fn(nb))
    if additive:
        tr = nb.n.new("ShaderNodeBsdfTransparent")
        add = nb.n.new("ShaderNodeAddShader")
        nb.l.new(em.outputs[0], add.inputs[0]); nb.l.new(tr.outputs[0], add.inputs[1])
        nb.l.new(add.outputs[0], out.inputs["Surface"])
    else:
        nb.l.new(em.outputs[0], out.inputs["Surface"])
    return m


def plane(name, size, loc, normal_to=None):
    """Plane of size (x, y) with UVs; its +Z normal faces normal_to (a point) when given, local Y kept up."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    sx, sy = size[0] / 2, size[1] / 2
    vs = [bm.verts.new(v) for v in ((-sx, -sy, 0), (sx, -sy, 0), (sx, sy, 0), (-sx, sy, 0))]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new()
    for lp, c in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uv].uv = c
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if normal_to is not None:
        d = (Vector(normal_to) - Vector(loc)).normalized()
        ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False, transmission=False, volume=False):
    ob.visible_camera = camera
    ob.visible_diffuse = diffuse
    ob.visible_glossy = glossy
    ob.visible_shadow = shadow
    ob.visible_transmission = transmission
    ob.visible_volume_scatter = volume


def link_receivers(emitter, objs, name):
    """Light linking: this emitter lights only `objs`."""
    c = bpy.data.collections.new(name)
    for o in objs:
        c.objects.link(o)
    emitter.light_linking.receiver_collection = c


def kelvin(t):
    """Approximate linear RGB of a blackbody, normalised to max 1."""
    t = t / 100.0
    if t <= 66:
        r = 255; g = 99.47 * math.log(t) - 161.12
        b = 0 if t <= 19 else 138.52 * math.log(t - 10) - 305.04
    else:
        r = 329.7 * (t - 60) ** -0.1332; g = 288.12 * (t - 60) ** -0.0755; b = 255
    c = [min(max(v, 0), 255) / 255 for v in (r, g, b)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    mx = max(c)
    return tuple(x / mx for x in c)


def hex_lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


# ------------------------------------------------------------------ emitters


def strip(name, loc, size, strength, target, color=(1, 1, 1), soft_ends=0.12, soft_w=0.0, ramp=None, additive=True):
    """Emissive card, ends softened along local X (u) and optionally across Y (v). Invisible to camera.
    ramp=(lo, hi, floor): brightness ramps along v (0 at v<=lo ... 1 at v>=hi, never below floor)."""
    ob = plane(name, size, loc, normal_to=target)

    def s(nb):
        u, v, _ = nb.coords("UV")
        f = nb.math("MULTIPLY", nb.smooth(u, 0.0, soft_ends), nb.smooth(u, 1.0, 1.0 - soft_ends)) if soft_ends else 1.0
        if soft_w:
            f = nb.math("MULTIPLY", f, nb.math("MULTIPLY", nb.smooth(v, 0.0, soft_w), nb.smooth(v, 1.0, 1.0 - soft_w)))
        if ramp:
            g = nb.math("MULTIPLY_ADD", nb.smooth(v, ramp[0], ramp[1]), 1 - ramp[2], ramp[2])
            f = nb.math("MULTIPLY", f, g)
        return nb.math("MULTIPLY", f, strength)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=additive))
    visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    return ob


def ribbon(name, pts_a, pts_b, strength_fn_or_val, color=(1, 1, 1)):
    """Emissive ribbon between two polylines (same length). UV u runs along the ribbon (0..1), v across."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    n = len(pts_a)
    ra = [bm.verts.new(p) for p in pts_a]
    rb = [bm.verts.new(p) for p in pts_b]
    for i in range(n - 1):
        f = bm.faces.new((ra[i], ra[i + 1], rb[i + 1], rb[i]))
        for lp, uv in zip(f.loops, ((i / (n - 1), 0), ((i + 1) / (n - 1), 0), ((i + 1) / (n - 1), 1), (i / (n - 1), 1))):
            lp[uvl].uv = uv
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    fn = strength_fn_or_val if callable(strength_fn_or_val) else (lambda nb: strength_fn_or_val)
    ob.data.materials.append(emitter_mat(name + "Mat", color, fn, additive=False))
    visibility(ob, camera=False, diffuse=False, glossy=True, shadow=False)
    return ob


def ring_card(name, centre, radius, az0, az1, el0, el1, strength_fn, color=(1, 1, 1), seg=128):
    """Emissive band on a sphere around `centre`: azimuth az0..az1 (degrees from -Y toward +X), elevation el0..el1.
    strength_fn(nb, u, v) -> socket, with u along azimuth (0..1) and v along elevation (0..1)."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    rows = []
    for el in (el0, el1):
        row = []
        for i in range(seg + 1):
            az = math.radians(az0 + (az1 - az0) * i / seg)
            e = math.radians(el)
            row.append(bm.verts.new((centre[0] + radius * math.cos(e) * math.sin(az),
                                     centre[1] - radius * math.cos(e) * math.cos(az),
                                     centre[2] + radius * math.sin(e))))
        rows.append(row)
    for i in range(seg):
        f = bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
        for lp, uv in zip(f.loops, ((i / seg, 0), ((i + 1) / seg, 0), ((i + 1) / seg, 1), (i / seg, 1))):
            lp[uvl].uv = uv
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)

    def s(nb):
        u, v, _ = nb.coords("UV")
        return strength_fn(nb, u, v)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=True))
    visibility(ob, camera=False, diffuse=False, glossy=True, shadow=False)
    return ob


# ------------------------------------------------------------------ rounded head with UVs


def _outward(loop):
    n = len(loop)
    out = []
    for i in range(n):
        ax, ay = loop[i - 1]
        bx, by = loop[(i + 1) % n]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1.0
        out.append((ty / ln, -tx / ln))  # right normal = away from the solid (solid on the left)
    return out


def build_head_rounded(name="KQ_Head", r_frame=0.0015, r_hole=0.0008, seg_frame=8, seg_hole=5):
    """Head with every edge rounded. Returns dict of objects:
    outer (both faces + flat side wall), bevel (the outline's two rounded edges), throat (throat walls and
    their rounded edges), inner (the 42 hole bores and lips). One shared mesh topology: seams are invisible.
    UV map 'UVMap' in metres: faces u=x, v=y; walls u = arc length along the loop, v = arc length down the profile."""
    from mathutils.geometry import tessellate_polygon
    U = racket.U
    outline = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, 120)
    throat = racket._loop(racket.THROAT_START, racket.THROAT_CURVES, 64)
    holes = []
    for (hx, hy) in racket.holes():
        n = 48
        holes.append([(hx * U + racket.HOLE_R * U * math.cos(2 * math.pi * k / n),
                       hy * U + racket.HOLE_R * U * math.sin(2 * math.pi * k / n)) for k in range(n)])
    if racket._area(outline) < 0:
        outline.reverse()
    loops = [(outline, r_frame, seg_frame, "outline")]
    for i, lp in enumerate([throat] + holes):
        if racket._area(lp) > 0:
            lp = lp[::-1]
        loops.append((lp, r_frame, seg_frame, "throat") if i == 0 else (lp, r_hole, seg_hole, "hole"))
    T2 = racket.THICK / 2
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    vnorm = []
    cap_top, cap_bot = [], []
    tag = {}
    for li, (lp, R, S, kind) in enumerate(loops):
        outw = _outward(lp)
        prof = []
        for k in range(S + 1):
            th = math.pi / 2 * (1 - k / S)
            prof.append((R * (1 - math.cos(th)), (T2 - R) + R * math.sin(th), math.cos(th), math.sin(th)))
        prof += [(i, -z, c, -s_) for (i, z, c, s_) in reversed(prof)]
        # profile arc length (v)
        pv = [0.0]
        for a, b in zip(prof[:-1], prof[1:]):
            pv.append(pv[-1] + math.hypot(a[0] - b[0], a[1] - b[1]))
        # loop arc length (u)
        su = [0.0]
        for k in range(1, len(lp) + 1):
            p, q = lp[k - 1], lp[k % len(lp)]
            su.append(su[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
        rings = []
        for (inset, z, c, s_) in prof:
            ring = []
            for (x, y), (ox, oy) in zip(lp, outw):
                ring.append(bm.verts.new((x - ox * inset, y - oy * inset, z)))
                vnorm.append((ox * c, oy * c, s_))
            rings.append(ring)
        cap_top.append(rings[0]); cap_bot.append(rings[-1])
        n = len(lp)
        nprof = len(prof)
        for ri in range(nprof - 1):
            a, b = rings[ri], rings[ri + 1]
            for k in range(n):
                j = (k + 1) % n
                f = bm.faces.new((a[k], a[j], b[j], b[k]))
                uj = su[k + 1]
                for lp_, uv in zip(f.loops, ((su[k], -pv[ri]), (uj, -pv[ri]), (uj, -pv[ri + 1]), (su[k], -pv[ri + 1]))):
                    lp_[uvl].uv = uv
                if kind == "outline":
                    flat_wall = (ri == S)  # the straight wall segment between the two bevels
                    tag[f] = 0 if flat_wall else 1
                elif kind == "throat":
                    tag[f] = 2
                else:
                    tag[f] = 3
    polys = [[Vector((v.co.x, v.co.y, 0)) for v in ring] for ring in cap_top]
    tris = tessellate_polygon(polys)
    flat_t = [v for ring in cap_top for v in ring]
    flat_b = [v for ring in cap_bot for v in ring]
    for (a, b, c) in tris:
        for flat in (flat_t, flat_b):
            try:
                f = bm.faces.new((flat[a], flat[b], flat[c]))
            except ValueError:
                continue
            for lp_ in f.loops:
                lp_[uvl].uv = (lp_.vert.co.x, lp_.vert.co.y)
            tag[f] = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        f.material_index = tag.get(f, 0)
    nl = bm.verts.layers.float_vector.new("kq_n")
    bm.verts.ensure_lookup_table()
    for v_, n_ in zip(bm.verts, vnorm):
        v_[nl] = n_
    objs = {}
    for keep, key, nm in ((0, "outer", name), (1, "bevel", name + "Bevel"), (2, "throat", name + "Throat"), (3, "inner", name + "Inner")):
        b2 = bm.copy()
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index != keep], context="FACES")
        for f in b2.faces:
            f.material_index = 0
        me = bpy.data.meshes.new(nm)
        b2.to_mesh(me)
        b2.free()
        me.shade_smooth()
        nrm = [tuple(a_.vector) for a_ in me.attributes["kq_n"].data]
        me.normals_split_custom_set_from_vertices(nrm)
        me.attributes.remove(me.attributes["kq_n"])
        ob = bpy.data.objects.new(nm, me)
        bpy.context.scene.collection.objects.link(ob)
        objs[key] = ob
    bm.free()
    return objs


def build_racket_rounded(name="KQ", carbon=None, cap_mat=None, grip_mat=None, collar_mat=None, throat_mat=None):
    """Rounded head + racket.build_handle parts with the handle-scale fix. Returns (root, parts dict)."""
    head = build_head_rounded(name + "_Head")
    grip, collar, cap = racket.build_handle(name + "_Handle")
    # racket.build_handle scales local Z (the handle axis) by 0.86, which shortens every part and opens gaps
    # between head, grip and cap. The intended oval belongs on local Y (the face-normal axis).
    for part in (grip, collar, cap):
        part.scale = (1.0, 0.86, 1.0)
    carbon = carbon or mat_twill("CarbonTwill")
    for k, o_ in head.items():
        o_.data.materials.clear()
        o_.data.materials.append(throat_mat if (k == "throat" and throat_mat) else carbon)
    racket.assign(grip, grip_mat or mat_grip_perforated())
    racket.assign(collar, collar_mat or racket.mat_metal("Titanium", (0.30, 0.30, 0.31), 0.24))
    racket.assign(cap, cap_mat or mat_anodised_cap())
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    parts = dict(head)
    parts.update(grip=grip, collar=collar, cap=cap)
    for p in parts.values():
        p.parent = root
    return root, parts


# ------------------------------------------------------------------ materials


def mat_twill(name="CarbonTwill", tow=0.0024, f0=0.045, base_rough=0.11, aniso=0.55, coat_rough=0.03,
              coat_ior=1.5, contrast=0.12, bump_s=0.3, coat_w=1.0, etch=None):
    """2x2 twill, 3K tows, mapped on the head's UVs (metres). Base: dark metallic fibre with per-tow anisotropy,
    tangent flipped 90 degrees between warp and weft, per-tow random sheen. So the weave only appears inside a
    reflection and falls to black outside it (no diffuse term at all). Coat: glass-clear lacquer, rough 0.03.
    etch: dict(p0, t, n, z0, w, h, image, depth): a frosted (satin) mask in the coat, seen only via reflections."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    u, v, _ = nb.coords("UV")
    uu = nb.math("ADD", nb.math("DIVIDE", u, tow), 4000.0)
    vv = nb.math("ADD", nb.math("DIVIDE", v, tow), 4000.0)
    i = nb.math("FLOOR", uu); j = nb.math("FLOOR", vv)
    fu = nb.math("FRACT", uu); fv = nb.math("FRACT", vv)
    over = nb.math("LESS_THAN", nb.math("MODULO", nb.math("ADD", i, j), 4.0), 1.5)  # 1: warp (v-running) on top
    # tow cross profile (rounded bundle) and a dip where it dives under the crossing tow
    prof_w = nb.math("SINE", nb.math("MULTIPLY", fu, math.pi))  # warp: profile across u
    prof_f = nb.math("SINE", nb.math("MULTIPLY", fv, math.pi))
    prof = nb.lerp(over, prof_f, prof_w)
    # along-tow phase within its 2-tow float: warp floats run along v, weft floats along u
    ph_w = nb.math("FRACT", nb.math("DIVIDE", nb.math("ADD", nb.math("ADD", vv, i), 0.0), 2.0))
    ph_f = nb.math("FRACT", nb.math("DIVIDE", nb.math("ADD", uu, j), 2.0))
    ph = nb.lerp(over, ph_f, ph_w)
    dip = nb.math("SINE", nb.math("MULTIPLY", ph, math.pi))
    hgt = nb.math("MULTIPLY", nb.math("POWER", prof, 0.6), nb.math("MULTIPLY_ADD", dip, 0.5, 0.5))
    # per-tow random
    wn = nb.n.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"
    cxyz = nb.n.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.lerp(over, j, i), cxyz.inputs[0])
    nb.l.new(over, cxyz.inputs[1])
    nb.l.new(nb.lerp(over, nb.math("FLOOR", nb.math("DIVIDE", nb.math("ADD", uu, j), 2.0)),
                     nb.math("FLOOR", nb.math("DIVIDE", nb.math("ADD", vv, i), 2.0))), cxyz.inputs[2])
    nb.l.new(cxyz.outputs[0], wn.inputs["Vector"])
    rnd = wn.outputs["Value"]
    # large, slow variation so 460 mm of weave never reads as a tiled texture
    big = nb.n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 9.0; big.inputs["Detail"].default_value = 3
    tco = nb.n.new("ShaderNodeTexCoord")
    nb.l.new(tco.outputs["Object"], big.inputs["Vector"])
    slow = nb.math("MULTIPLY_ADD", big.outputs["Fac"], 0.5, 0.75)
    col = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.math("MULTIPLY_ADD", rnd, contrast, 1 - contrast / 2), slow), f0)
    nb.l.new(nb.gray(col), b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = 1.0
    nb.l.new(nb.math("MULTIPLY_ADD", rnd, 0.04, base_rough - 0.02), b.inputs["Roughness"])
    b.inputs["Anisotropic"].default_value = aniso
    nb.l.new(nb.math("MULTIPLY", over, 0.25), b.inputs["Anisotropic Rotation"])
    tg = nb.n.new("ShaderNodeTangent"); tg.direction_type = "UV_MAP"; tg.uv_map = "UVMap"
    nb.l.new(tg.outputs["Tangent"], b.inputs["Tangent"])
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_s
    bump.inputs["Distance"].default_value = 0.00012
    nb.l.new(hgt, bump.inputs["Height"])
    nrm_base = bump.outputs["Normal"]
    b.inputs["Coat Weight"].default_value = coat_w
    b.inputs["Coat IOR"].default_value = coat_ior
    b.inputs["Coat Roughness"].default_value = coat_rough
    if etch:
        e = etch
        x, y, z = nb.coords("Object")
        p0, t, nv = Vector(e["p0"]), Vector(e["t"]), Vector(e["n"])
        dx = nb.math("SUBTRACT", x, p0.x); dy = nb.math("SUBTRACT", y, p0.y); dz = nb.math("SUBTRACT", z, p0.z)
        along = nb.math("ADD", nb.math("MULTIPLY", dx, t.x), nb.math("MULTIPLY", dy, t.y))
        normal_d = nb.math("ABSOLUTE", nb.math("ADD", nb.math("MULTIPLY", dx, nv.x), nb.math("MULTIPLY", dy, nv.y)))
        tu = nb.math("ADD", nb.math("DIVIDE", along, e["w"]), 0.5)
        tv = nb.math("ADD", nb.math("DIVIDE", nb.math("SUBTRACT", z, e["z0"]), e["h"]), 0.5)
        cvec = nb.n.new("ShaderNodeCombineXYZ")
        nb.l.new(tu, cvec.inputs[0]); nb.l.new(tv, cvec.inputs[1])
        img = nb.n.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(e["image"], check_existing=True)
        img.image.colorspace_settings.name = "Non-Color"
        img.extension = "CLIP"
        img.interpolation = "Cubic"
        nb.l.new(cvec.outputs[0], img.inputs["Vector"])
        mask = nb.math("MULTIPLY", img.outputs["Color"], nb.smooth(normal_d, 0.004, 0.002))
        nb.l.new(nb.math("MULTIPLY_ADD", mask, e.get("coat_rough", 0.30) - coat_rough, coat_rough), b.inputs["Coat Roughness"])
        # 15 um relief (the laser takes the lacquer down a touch)
        eb = nb.n.new("ShaderNodeBump")
        eb.inputs["Strength"].default_value = 1.0
        eb.inputs["Distance"].default_value = e.get("depth", 0.000015)
        nb.l.new(nb.math("MULTIPLY", mask, -1.0), eb.inputs["Height"])
        nb.l.new(nrm_base, eb.inputs["Normal"])
        nrm_base = eb.outputs["Normal"]
        eb2 = nb.n.new("ShaderNodeBump")
        eb2.inputs["Strength"].default_value = 1.0
        eb2.inputs["Distance"].default_value = e.get("depth", 0.000015)
        nb.l.new(nb.math("MULTIPLY", mask, -1.0), eb2.inputs["Height"])
        nb.l.new(eb2.outputs["Normal"], b.inputs["Coat Normal"])
    nb.l.new(nrm_base, b.inputs["Normal"])
    return m


def mat_grip_perforated(name="GripPerf", silhouette_clean=False, base=0.014):
    """Black perforated overgrip: staggered 1.3 mm holes on a 3.6 mm pitch plus the helical wrap ridge.
    Mapped in the grip's object space (local Z = handle axis). silhouette_clean fades the perforation relief
    out toward grazing view angles, so an edge light runs along the grip as one unbroken line."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    x, y, z = nb.coords("Object")
    ang = nb.math("ARCTAN2", y, x)
    arc = nb.math("MULTIPLY", ang, 0.0156)
    pitch = 0.0036
    row = nb.math("FLOOR", nb.math("DIVIDE", nb.math("ADD", z, 10.0), pitch * 0.866))
    shift = nb.math("MULTIPLY", nb.math("MODULO", row, 2.0), pitch * 0.5)
    cu = nb.math("SUBTRACT", nb.math("FRACT", nb.math("DIVIDE", nb.math("ADD", nb.math("ADD", arc, shift), 10.0), pitch)), 0.5)
    cv = nb.math("SUBTRACT", nb.math("FRACT", nb.math("DIVIDE", nb.math("ADD", z, 10.0), pitch * 0.866)), 0.5)
    du = nb.math("MULTIPLY", cu, pitch); dv = nb.math("MULTIPLY", cv, pitch * 0.866)
    d = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", du, du), nb.math("MULTIPLY", dv, dv)))
    hole = nb.smooth(d, 0.00072, 0.00058)
    if silhouette_clean:
        lw = nb.n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
        hole = nb.math("MULTIPLY", hole, nb.smooth(lw.outputs["Facing"], 0.78, 0.55))
    ph = nb.math("ADD", nb.math("DIVIDE", z, 0.022), nb.math("DIVIDE", ang, 2 * math.pi))
    ridge = nb.smooth(nb.math("FRACT", ph), 0.0, 0.16)
    col = nb.math("MULTIPLY_ADD", hole, -base * 0.75, base)
    nb.l.new(nb.gray(col), b.inputs["Base Color"])
    nb.l.new(nb.math("MULTIPLY_ADD", hole, 0.3, 0.52), b.inputs["Roughness"])
    b.inputs["Sheen Weight"].default_value = 0.25
    b.inputs["Sheen Roughness"].default_value = 0.35
    hgt = nb.math("SUBTRACT", nb.math("MULTIPLY", ridge, 0.6), nb.math("MULTIPLY", hole, 1.0))
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.8
    bump.inputs["Distance"].default_value = 0.0005
    nb.l.new(hgt, bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_anodised_cap(name="CapAnodised"):
    """Black anodised aluminium end cap, satin; only the butt-end chamfer is diamond-cut and polished.
    (cap object space: local +Z points to the butt end; the grip-side rim stays satin black)."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    body = nb.n.new("ShaderNodeBsdfPrincipled")
    body.inputs["Base Color"].default_value = (0.010, 0.010, 0.011, 1)
    body.inputs["Metallic"].default_value = 0.7
    body.inputs["Roughness"].default_value = 0.42
    body.inputs["Coat Weight"].default_value = 0.0
    chamf = nb.n.new("ShaderNodeBsdfPrincipled")
    chamf.inputs["Base Color"].default_value = (0.78, 0.78, 0.80, 1)
    chamf.inputs["Metallic"].default_value = 1.0
    chamf.inputs["Roughness"].default_value = 0.08
    tc = nb.n.new("ShaderNodeTexCoord")
    sep = nb.n.new("ShaderNodeSeparateXYZ")
    nb.l.new(tc.outputs["Normal"], sep.inputs["Vector"])
    zz = sep.outputs["Z"]
    mask = nb.math("MULTIPLY", nb.smooth(zz, 0.22, 0.34), nb.smooth(zz, 0.96, 0.88))
    mix = nb.n.new("ShaderNodeMixShader")
    nb.l.new(mask, mix.inputs[0])
    nb.l.new(body.outputs[0], mix.inputs[1]); nb.l.new(chamf.outputs[0], mix.inputs[2])
    nb.l.new(mix.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ text mask for etches


def etch_mask_png(path, lines, px_per_m=60000, pad=0.002):
    """Render text lines to a white-on-black mask PNG.
    lines: [(text, font_path, cap_height_m, centre_z_m, tracking_em)]. Returns (path, width_m, height_m, z0)."""
    from PIL import Image, ImageDraw, ImageFont
    rendered = []
    for (text, font, cap_h, cz, track) in lines:
        size_px = int(cap_h * px_per_m / 0.72)
        f = ImageFont.truetype(font, size_px)
        # measure with tracking
        widths = [f.getlength(ch) for ch in text]
        tw = sum(widths) + track * size_px * (len(text) - 1)
        rendered.append((text, f, size_px, cz, track, widths, tw))
    W_m = max(r[6] for r in rendered) / px_per_m + 2 * pad
    zs = [r[3] for r in rendered]
    caps = [r[2] * 0.72 / px_per_m for r in rendered]
    ztop = max(z + c for z, c in zip(zs, caps)) + pad
    zbot = min(z - c for z, c in zip(zs, caps)) - pad
    H_m = ztop - zbot
    z0 = (ztop + zbot) / 2
    W, H = int(W_m * px_per_m), int(H_m * px_per_m)
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for (text, f, size_px, cz, track, widths, tw) in rendered:
        x = (W - tw) / 2
        cap_px = size_px * 0.72
        ybase = (ztop - cz) * px_per_m + cap_px / 2  # baseline in image rows
        asc = f.getmetrics()[0]
        for ch, wch in zip(text, widths):
            dr.text((x, ybase - asc), ch, font=f, fill=255)
            x += wch + track * size_px
    im.save(path)
    return path, W_m, H_m, z0


# ------------------------------------------------------------------ post: display-space edge grade


def _oetf(x):
    x = np.clip(x, 0, None)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def _eotf(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.04045, x / 12.92, np.power((x + 0.055) / 1.055, 2.4))


def finish_png(raw_path, out_path, floor_hex=None, floor_band=0.0, full_frame=None, bloom=None):
    """Load the raw render (display-referred PNG), optionally lift every pixel near the frame edge to at least
    floor_hex (a soft floor, never a darkening frame), optionally add a gentle bloom, save 16-bit PNG."""
    img = bpy.data.images.load(raw_path)
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    disp = _oetf(a[..., :3])
    if bloom:
        thr, amt, rad = bloom
        lum = disp @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        hi = np.clip((lum - thr) / (1 - thr), 0, 1)[..., None] * disp
        from PIL import Image, ImageFilter
        hb = Image.fromarray(np.uint8(np.clip(hi, 0, 1) * 255))
        r = max(1, int(rad * (full_frame[1] if full_frame else h)))   # a crop blooms as its whole frame
        hb = np.asarray(hb.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
        disp = 1 - (1 - disp) * (1 - amt * hb)  # screen
    if floor_hex:
        W, H, x0, y0 = full_frame if full_frame else (w, h, 0, 0)
        ys = (np.arange(h)[::-1] + y0 + 0.5)
        xs = np.arange(w) + x0 + 0.5
        dx = np.minimum(xs, W - xs)[None, :] / H
        dy = np.minimum(ys, H - ys)[:, None] / H
        d = np.minimum(dx, dy)
        t = np.clip(d / floor_band, 0, 1) if floor_band else np.ones_like(d)
        k = (t * t * (3 - 2 * t))[..., None]
        tgt = np.array([int(floor_hex[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)
        lifted = np.maximum(disp, tgt)
        disp = lifted * (1 - k) + disp * k
    a[..., :3] = _eotf(disp)
    a[..., 3] = 1.0
    res = bpy.data.images.new("graded", w, h, alpha=True, float_buffer=True)
    res.pixels.foreach_set(a.ravel())
    sc = bpy.context.scene
    vt, lk = sc.view_settings.view_transform, sc.view_settings.look
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    res.save_render(out_path, scene=sc)
    sc.view_settings.view_transform, sc.view_settings.look = vt, lk
    bpy.data.images.remove(img)
    bpy.data.images.remove(res)


def _save16(A, W, H, out_png):
    res = bpy.data.images.new("out16", W, H, alpha=True, float_buffer=True)
    res.pixels.foreach_set(np.ascontiguousarray(A).ravel())
    sc = bpy.context.scene
    vt, lk = sc.view_settings.view_transform, sc.view_settings.look
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    res.save_render(out_png, scene=sc)
    sc.view_settings.view_transform, sc.view_settings.look = vt, lk
    bpy.data.images.remove(res)


def rotate_png(src_png, out_png):
    """A 16-bit PNG turned 90 degrees counter-clockwise, kept at 16 bits (PIL would make it 8-bit)."""
    im = bpy.data.images.load(src_png, check_existing=False)
    W, H = im.size
    A = np.empty(W * H * 4, np.float32); im.pixels.foreach_get(A)
    bpy.data.images.remove(im)
    A = A.reshape(H, W, 4)[::-1]                 # top-down
    A = np.rot90(A, 1)[::-1]                     # counter-clockwise, back to bottom-up
    _save16(A, H, W, out_png)


def paste_region(base_png, region_png, crop, out_png, feather=24):
    """Paste a border-rendered region (crop = x0 x1 y0 y1, fractions, top-left origin) into a whole frame, blending
    over `feather` px at every edge that is inside the frame; writes a 16-bit PNG (as K.finish_png)."""
    b = bpy.data.images.load(base_png, check_existing=False)
    r = bpy.data.images.load(region_png, check_existing=False)
    W, H = b.size
    w, h = r.size
    A = np.empty(W * H * 4, np.float32); b.pixels.foreach_get(A); A = A.reshape(H, W, 4)
    R = np.empty(w * h * 4, np.float32); r.pixels.foreach_get(R); R = R.reshape(h, w, 4)
    x0 = int(round(crop[0] * W)); yt = int(round(crop[2] * H))
    yb = H - yt - h                      # Blender rows run bottom-up
    def ramp(n, lo_in, hi_in):
        t = np.ones(n, np.float32)
        k = np.arange(n, dtype=np.float32)
        if lo_in:
            t = np.minimum(t, (k + 0.5) / feather)
        if hi_in:
            t = np.minimum(t, (n - k - 0.5) / feather)
        t = np.clip(t, 0, 1)
        return t * t * (3 - 2 * t)
    wx = ramp(w, x0 > 0, x0 + w < W)
    wy = ramp(h, yb > 0, yb + h < H)
    m = (wy[:, None] * wx[None, :])[..., None]
    A[yb:yb + h, x0:x0 + w, :3] = R[..., :3] * m + A[yb:yb + h, x0:x0 + w, :3] * (1 - m)
    A[..., 3] = 1.0
    bpy.data.images.remove(b)
    bpy.data.images.remove(r)
    _save16(A, W, H, out_png)


def render_and_finish(sc, o, **finish_kw):
    if o["crop"]:
        x0, x1, y0, y1 = o["crop"]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
    raw = studio.render(o["out"] + "__raw")
    final = raw.replace("__raw.png", ".png")
    ff = None
    if o["crop"]:
        x0, x1, y0, y1 = o["crop"]
        ff = (o["w"], o["h"], int(round(x0 * o["w"])), int(round(y0 * o["h"])))
    finish_png(raw, final, full_frame=ff, **finish_kw)
    os.remove(raw)
    return final
