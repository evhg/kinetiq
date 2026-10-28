"""Shared helpers for K07-lineup-five, K08-feel-pair and K09-case-three.

The product parts (rounded head, handle fix, perforated grip, anodised cap, wall etch) and the small
node/light helpers are copied from the K01/K02 shot files so every KINETIQ image shows the same racket.
Everything below the 'K07-K09 additions' line is new.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402

# ------------------------------------------------------------------ small node helper


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

    def coords(self, kind="Object"):
        tc = self.n.new("ShaderNodeTexCoord")
        sep = self.n.new("ShaderNodeSeparateXYZ")
        self.l.new(tc.outputs[kind], sep.inputs["Vector"])
        return sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]


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
    s = strength_sock_fn(nb)
    nb._in(em.inputs["Strength"], s)
    if additive:
        tr = nb.n.new("ShaderNodeBsdfTransparent")
        add = nb.n.new("ShaderNodeAddShader")
        nb.l.new(em.outputs[0], add.inputs[0]); nb.l.new(tr.outputs[0], add.inputs[1])
        nb.l.new(add.outputs[0], out.inputs["Surface"])
    else:
        nb.l.new(em.outputs[0], out.inputs["Surface"])
    return m


def plane(name, size, loc, normal_to=None, up=(0, 0, 1)):
    """Unit plane scaled to size (x, y); its +Z normal faces normal_to (a point) when given."""
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
    """Light linking: this emitter lights only `objs` (shadows unaffected)."""
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


def strip(name, loc, size, strength, target, color=(1, 1, 1), soft_ends=0.12, soft_w=0.0, additive=True):
    """Emissive strip, ends softened along local X (u) and optionally across local Y (v). Invisible to camera."""
    ob = plane(name, size, loc, normal_to=target)

    def s(nb):
        u, v, _ = nb.coords("UV")
        e1 = nb.smooth(u, 0.0, soft_ends)
        e2 = nb.smooth(u, 1.0, 1.0 - soft_ends)
        f = nb.math("MULTIPLY", e1, e2)
        if soft_w:
            f = nb.math("MULTIPLY", f, nb.math("MULTIPLY", nb.smooth(v, 0.0, soft_w), nb.smooth(v, 1.0, 1.0 - soft_w)))
        return nb.math("MULTIPLY", f, strength)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=additive))
    visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    return ob


def gradient_card(name, loc, size, strength, target, color=(1, 1, 1), axis="u", lo=0.0, hi=1.0, floor=0.0, additive=True):
    """Large soft card whose brightness ramps along one axis (its falloff edge makes the light sweep)."""
    ob = plane(name, size, loc, normal_to=target)

    def s(nb):
        u, v, _ = nb.coords("UV")
        a = u if axis == "u" else v
        g = nb.smooth(a, lo, hi)
        # soften the other axis' edges
        o = v if axis == "u" else u
        e = nb.math("MULTIPLY", nb.smooth(o, 0.0, 0.25), nb.smooth(o, 1.0, 0.75))
        g = nb.math("MULTIPLY_ADD", g, 1 - floor, floor)
        return nb.math("MULTIPLY", nb.math("MULTIPLY", g, e), strength)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=additive))
    visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    return ob


def sweep_card(name, loc, size, strength, target, grad_world, width, offset=0.0, color=(1, 1, 1), lo=0.0,
               half=1.0, band=None, additive=True):
    """Card whose brightness steps across a straight edge (direction grad_world, in world space, toward the
    bright side). Reflected in a flat face, the edge becomes the diagonal light sweep."""
    ob = plane(name, size, loc, normal_to=target)
    bpy.context.view_layer.update()
    mw = ob.matrix_world.to_3x3()
    g = Vector(grad_world).normalized()
    gx, gy = mw.col[0].normalized().dot(g), mw.col[1].normalized().dot(g)
    ln = math.hypot(gx, gy) or 1
    gx, gy = gx / ln, gy / ln

    def s(nb):
        x, y, _ = nb.coords("Object")
        t = nb.math("MULTIPLY_ADD", x, gx, nb.math("MULTIPLY", y, gy))
        f = nb.math("MULTIPLY", nb.smooth(t, offset - width / 2, offset + width / 2), half)
        if band:
            d = nb.math("DIVIDE", nb.math("SUBTRACT", t, band[0]), band[1])
            f = nb.math("ADD", f, nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", d, d), -1.0)))
        f = nb.math("MULTIPLY_ADD", f, 1 - lo, lo)
        u, v, _ = nb.coords("UV")
        e = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.1), nb.smooth(u, 1.0, 0.9)),
                    nb.math("MULTIPLY", nb.smooth(v, 0.0, 0.1), nb.smooth(v, 1.0, 0.9)))
        return nb.math("MULTIPLY", nb.math("MULTIPLY", f, e), strength)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=additive))
    visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    return ob


def radial_haze(name, loc, size, strength, target, color=(1, 1, 1), power=1.6):
    """Camera-visible additive glow card with a radial falloff (graphite lift on the cyclorama)."""
    ob = plane(name, size, loc, normal_to=target)

    def s(nb):
        u, v, _ = nb.coords("UV")
        du = nb.math("SUBTRACT", u, 0.5); dv = nb.math("SUBTRACT", v, 0.5)
        r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", du, du), nb.math("MULTIPLY", dv, dv)))
        f = nb.smooth(r, 0.5, 0.0)
        f = nb.math("POWER", f, power)
        return nb.math("MULTIPLY", f, strength)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=True))
    visibility(ob, camera=True, diffuse=False, glossy=True, shadow=False)
    return ob



# ------------------------------------------------------------------ racket with true rounded edges
# racket.build_head's bevels are clamped to ~0 by its fan-triangulated caps (edges come out knife-sharp,
# so no rim/top light can draw a line on them). This builds the same outline, throat, 42 holes and 38 mm
# thickness with an explicit quarter-round profile on every edge and analytic normals.


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


def build_head_rounded(name="KQ_Head", r_frame=0.0015, r_hole=0.0008, seg_frame=7, seg_hole=4, split_bevel=False):
    """Returns (outer, inner[, bevel]): outer = caps + side wall, inner = throat and hole walls,
    bevel (split_bevel=True) = the outline's two rounded edges, so a light can be linked to them alone."""
    from mathutils.geometry import tessellate_polygon
    U = racket.U
    outline = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, 96)
    throat = racket._loop(racket.THROAT_START, racket.THROAT_CURVES, 48)
    holes = []
    for (hx, hy) in racket.holes():
        n = 48
        holes.append([(hx * U + racket.HOLE_R * U * math.cos(2 * math.pi * k / n),
                       hy * U + racket.HOLE_R * U * math.sin(2 * math.pi * k / n)) for k in range(n)])
    if racket._area(outline) < 0:
        outline.reverse()
    loops = [(outline, r_frame, seg_frame)]
    for i, lp in enumerate([throat] + holes):
        if racket._area(lp) > 0:
            lp = lp[::-1]
        loops.append((lp, r_frame, seg_frame) if i == 0 else (lp, r_hole, seg_hole))
    T2 = racket.THICK / 2
    bm = bmesh.new()
    vnorm = []
    cap_top, cap_bot = [], []
    inner_faces = []
    bevel_faces = []
    for li, (lp, R, S) in enumerate(loops):
        outw = _outward(lp)
        # profile from the top cap edge (theta=90) down the wall and back to the bottom cap edge
        prof = []
        for k in range(S + 1):
            th = math.pi / 2 * (1 - k / S)
            prof.append((R * (1 - math.cos(th)), (T2 - R) + R * math.sin(th), math.cos(th), math.sin(th)))
        prof += [(i, -z, c, -s_) for (i, z, c, s_) in reversed(prof)]
        rings = []
        for (inset, z, c, s_) in prof:
            ring = []
            for (x, y), (ox, oy) in zip(lp, outw):
                ring.append(bm.verts.new((x - ox * inset, y - oy * inset, z)))
                vnorm.append((ox * c, oy * c, s_))
            rings.append(ring)
        cap_top.append(rings[0]); cap_bot.append(rings[-1])
        n = len(lp)
        for ri, (a, b) in enumerate(zip(rings[:-1], rings[1:])):
            for k in range(n):
                j = (k + 1) % n
                f = bm.faces.new((a[k], a[j], b[j], b[k]))
                if li > 0:
                    inner_faces.append(f)
                elif ri != S:
                    bevel_faces.append(f)
    polys = [[Vector((v.co.x, v.co.y, 0)) for v in ring] for ring in cap_top]
    tris = tessellate_polygon(polys)
    flat_t = [v for ring in cap_top for v in ring]
    flat_b = [v for ring in cap_bot for v in ring]
    for (a, b, c) in tris:
        for flat in (flat_t, flat_b):
            try:
                bm.faces.new((flat[a], flat[b], flat[c]))
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    inner_set = set(inner_faces)
    bevel_set = set(bevel_faces) if split_bevel else set()
    for f in bm.faces:
        f.material_index = 1 if f in inner_set else (2 if f in bevel_set else 0)
    nl = bm.verts.layers.float_vector.new("kq_n")
    bm.verts.ensure_lookup_table()
    for v_, n_ in zip(bm.verts, vnorm):
        v_[nl] = n_
    # two objects: outer frame + caps, and throat/hole walls (seam invisible: shared positions and normals),
    # so rim lights can be linked to the outer frame only
    objs = []
    for keep, nm in ((0, name), (1, name + "Inner")) + (((2, name + "Bevel"),) if split_bevel else ()):
        b2 = bm.copy()
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index != keep], context="FACES")
        me = bpy.data.meshes.new(nm)
        b2.to_mesh(me)
        b2.free()
        me.shade_smooth()
        nrm = [tuple(a_.vector) for a_ in me.attributes["kq_n"].data]
        me.normals_split_custom_set_from_vertices(nrm)
        me.attributes.remove(me.attributes["kq_n"])
        ob = bpy.data.objects.new(nm, me)
        bpy.context.scene.collection.objects.link(ob)
        objs.append(ob)
    bm.free()
    return tuple(objs)


def build_racket_rounded(name="KQ", kind="3k", carbon=None, cap_mat=None, grip_mat=None, split_bevel=False):
    """Same parts and materials as racket.build_racket, with the rounded head. Returns (root, head)."""
    head, inner, *bevel = build_head_rounded(name + "_Head", split_bevel=split_bevel)
    grip, collar, cap = racket.build_handle(name + "_Handle")
    # racket.build_handle scales local Z (the handle axis) by 0.86, which shortens every part and opens
    # ~10 mm gaps between head, grip and cap. The intended oval belongs on local Y (the face-normal axis).
    for part in (grip, collar, cap):
        part.scale = (1.0, 0.86, 1.0)
    if carbon is None:
        carbon = racket.mat_carbon(f"Carbon_{kind}", tow_mm=2.6 if kind == "3k" else 2.2, kind=kind)
    for o_ in [head, inner] + bevel:
        o_.data.materials.clear()
        o_.data.materials.append(carbon)
        o_.data.materials.append(carbon)
    racket.assign(grip, grip_mat or bpy.data.materials.get("Grip") or racket.mat_grip())
    racket.assign(collar, bpy.data.materials.get("Titanium") or racket.mat_metal())
    racket.assign(cap, cap_mat or bpy.data.materials.get("CapCarbon") or racket.mat_carbon("CapCarbon", tow_mm=1.6))
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for p in [head, inner] + bevel + [grip, collar, cap]:
        p.parent = root
    return root, head

# ------------------------------------------------------------------ product materials (same as K02)


def mat_grip_perforated(name="GripPerf"):
    """Black perforated overgrip: staggered 1.3 mm holes on a 3.6 mm pitch plus the helical wrap ridge.
    Mapped in the grip's object space (local Z = handle axis)."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    x, y, z = nb.coords("Object")
    ang = nb.math("ARCTAN2", y, x)
    arc = nb.math("MULTIPLY", ang, 0.0156)  # metres around the circumference
    pitch = 0.0036
    # staggered grid: row index from z, odd rows shifted half a pitch
    row = nb.math("FLOOR", nb.math("DIVIDE", z, pitch * 0.866))
    shift = nb.math("MULTIPLY", nb.math("MODULO", row, 2.0), pitch * 0.5)
    cu = nb.math("SUBTRACT", nb.math("FRACT", nb.math("DIVIDE", nb.math("ADD", arc, shift), pitch)), 0.5)
    cv = nb.math("SUBTRACT", nb.math("FRACT", nb.math("DIVIDE", z, pitch * 0.866)), 0.5)
    du = nb.math("MULTIPLY", cu, pitch); dv = nb.math("MULTIPLY", cv, pitch * 0.866)
    d = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", du, du), nb.math("MULTIPLY", dv, dv)))
    hole = nb.smooth(d, 0.00072, 0.00058)  # 1 inside a hole, soft 0.14 mm rim
    # helical wrap ridge (overgrip overlap), as racket.mat_grip
    ph = nb.math("ADD", nb.math("DIVIDE", z, 0.022), nb.math("DIVIDE", ang, 2 * math.pi))
    ridge = nb.smooth(nb.math("FRACT", ph), 0.0, 0.16)
    base = nb.math("MULTIPLY_ADD", hole, -0.010, 0.014)
    cc = nb.n.new("ShaderNodeCombineColor")
    for k in range(3):
        nb.l.new(base, cc.inputs[k])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    nb.l.new(nb.math("MULTIPLY_ADD", hole, 0.3, 0.55), b.inputs["Roughness"])
    b.inputs["Sheen Weight"].default_value = 0.15
    b.inputs["Sheen Roughness"].default_value = 0.4
    hgt = nb.math("SUBTRACT", nb.math("MULTIPLY", ridge, 0.6), nb.math("MULTIPLY", hole, 1.0))
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.8
    bump.inputs["Distance"].default_value = 0.0005
    nb.l.new(hgt, bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_anodised_cap(name="CapAnodised"):
    """Black anodised aluminium end cap with a polished diamond-cut chamfer (selected by object-space normal)."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    body = nb.n.new("ShaderNodeBsdfPrincipled")
    body.inputs["Base Color"].default_value = (0.020, 0.020, 0.022, 1)
    body.inputs["Metallic"].default_value = 1.0
    body.inputs["Roughness"].default_value = 0.30
    chamf = nb.n.new("ShaderNodeBsdfPrincipled")
    chamf.inputs["Base Color"].default_value = (0.80, 0.80, 0.82, 1)
    chamf.inputs["Metallic"].default_value = 1.0
    chamf.inputs["Roughness"].default_value = 0.07
    tc = nb.n.new("ShaderNodeTexCoord")
    sep = nb.n.new("ShaderNodeSeparateXYZ")
    nb.l.new(tc.outputs["Normal"], sep.inputs["Vector"])
    az = nb.math("ABSOLUTE", sep.outputs["Z"])
    mask = nb.math("MULTIPLY", nb.smooth(az, 0.18, 0.30), nb.smooth(az, 0.97, 0.90))
    mix = nb.n.new("ShaderNodeMixShader")
    nb.l.new(mask, mix.inputs[0])
    nb.l.new(body.outputs[0], mix.inputs[1]); nb.l.new(chamf.outputs[0], mix.inputs[2])
    nb.l.new(mix.outputs[0], out.inputs["Surface"])
    return m


def etch_wall(head, text, y_units, size, side=1, name="KQ_Etch", mat=None, font=None, z=0.0, spacing=1.35):
    """Laser-etched text on the side wall, reading toward the tip, front face up, facing outward."""
    outline = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, 400)
    pts = [p for p in outline if (p[0] > 0) == (side > 0)]
    tgt = y_units * racket.U
    best = min(range(len(pts) - 1), key=lambda k: abs(pts[k][1] - tgt))
    p, q = Vector((*pts[best], 0)), Vector((*pts[best + 1], 0))
    t = (q - p).normalized()
    if t.y < 0:
        t = -t  # read toward the tip
    nrm = Vector((t.y, -t.x, 0)) if side > 0 else Vector((-t.y, t.x, 0))
    if nrm.x * side < 0:
        nrm = -nrm
    up = t.cross(nrm) * -1  # text Y so that X x Y = outward normal
    if t.cross(up).dot(nrm) < 0:
        up = -up
    ob = racket.build_text(text, size, (0, 0, 0), font or racket.FONT_MED, name, None, extrude=0.0, spacing=spacing)
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    loc = p + nrm * 0.002 + Vector((0, 0, z))
    ob.matrix_world = Matrix(((t.x, up.x, nrm.x, loc.x), (t.y, up.y, nrm.y, loc.y), (t.z, up.z, nrm.z, loc.z), (0, 0, 0, 1)))
    sw = ob.modifiers.new("wrap", "SHRINKWRAP")
    sw.target = head
    sw.wrap_method = "NEAREST_SURFACEPOINT"
    sw.offset = 0.00004
    racket._apply_all(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob



# ================================================================== K07-K09 additions


def cyclorama(name="Cyc", wall_y=5.0, radius=1.8, half_x=14.0, near_y=-9.0, top=7.0):
    """Infinite-cove studio: floor, curved cove, back wall (one smooth mesh)."""
    prof = [(near_y, 0.0)]
    n = 24
    for k in range(n + 1):
        t = k / n * math.pi / 2
        prof.append((wall_y - radius + radius * math.sin(t), radius - radius * math.cos(t)))
    prof.append((wall_y, top))
    bm = bmesh.new()
    cols = 2
    rows = []
    for (y, z) in prof:
        rows.append([bm.verts.new((x, y, z)) for x in (-half_x, half_x)])
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        bm.faces.new((a[0], a[1], b[1], b[0]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    # normals must face the camera side (+Z on the floor)
    if me.polygons[0].normal.z < 0:
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
    return ob





def parse_args(argv, out_default):
    """--w --h --spp --out [--variant v] [--crop x0 x1 y0 y1] [--lightgroups]"""
    o = {"w": 960, "h": 540, "spp": 32, "out": out_default, "variant": "full", "crop": None, "lightgroups": False}
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
            o["crop"] = [float(v) for v in argv[i + 1:i + 5]]; i += 5
        elif a == "--lightgroups":
            o["lightgroups"] = True; i += 1
        else:
            i += 1
    return o


class Groups:
    """Assigns Cycles light groups (lg_*) only when --lightgroups is on; the combined image is identical."""

    def __init__(self, enabled):
        self.on = enabled
        self.vl = bpy.context.scene.view_layers[0]

    def __call__(self, ob, g):
        if not self.on:
            return
        if g not in [x.name for x in self.vl.lightgroups]:
            self.vl.lightgroups.add(name=g)
        ob.lightgroup = g


def make_racket(name="KQ", kind="3k", carbon=None, etch=True):
    """The KINETIQ racket as in K01/K02 (rounded head, perforated grip, anodised cap, wall etch).
    Model space: face in XY, +Z out of the front face, head up (+Y), cap bottom at y = -0.305."""
    cap = bpy.data.materials.get("CapAnodised") or mat_anodised_cap()
    grip = bpy.data.materials.get("GripPerf") or mat_grip_perforated()
    root, head = build_racket_rounded(name, kind=kind, carbon=carbon, cap_mat=cap, grip_mat=grip, split_bevel=True)
    if etch:
        etch_mat = bpy.data.materials.get("Etch") or racket.mat_basic("Etch", (0.12, 0.12, 0.125), rough=0.5)
        e = etch_wall(head, "KINETIQ", -0.62, 0.0034, side=1, name=name + "_EtchR", mat=etch_mat, font=racket.FONT_BOLD)
        e.parent = root
    return root


def clone(src, name):
    """Linked duplicate of a racket group: every child is obj.copy() (mesh data shared) under a new Empty."""
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for c in list(src.children):
        cc = c.copy()
        cc.name = name + c.name[len(src.name):]
        bpy.context.scene.collection.objects.link(cc)
        cc.parent = root
        cc.matrix_parent_inverse = c.matrix_parent_inverse.copy()
    return root


def parts(root):
    return list(root.children)


def pose(root, loc, yaw_deg=0.0, roll_deg=0.0, tilt_deg=90.0):
    """Stand the racket up: in-plane roll about the face normal, tilt about X (90 = upright, front face to -Y),
    then yaw about world Z; loc is where the model origin (head centre) goes."""
    m = (Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(yaw_deg), 4, "Z")
         @ Matrix.Rotation(math.radians(tilt_deg), 4, "X") @ Matrix.Rotation(math.radians(roll_deg), 4, "Z"))
    root.matrix_world = m
    return root


def cam_only_mat(name, strength_fn, color=(1, 1, 1), glossy=True, base=None):
    """Emission seen by camera (and glossy) rays only, so it paints the backdrop without lighting anything.
    Other rays see a dark diffuse surface (base colour) or nothing."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    em = nb.n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    nb._in(em.inputs["Strength"], strength_fn(nb))
    lp = nb.n.new("ShaderNodeLightPath")
    vis = lp.outputs["Is Camera Ray"]
    if glossy:
        vis = nb.math("MAXIMUM", vis, lp.outputs["Is Glossy Ray"])
    if base is None:
        other = nb.n.new("ShaderNodeBsdfTransparent")
    else:
        other = nb.n.new("ShaderNodeBsdfDiffuse")
        other.inputs["Color"].default_value = (*base, 1)
    mix = nb.n.new("ShaderNodeMixShader")
    nb.l.new(vis, mix.inputs[0])
    nb.l.new(other.outputs[0], mix.inputs[1]); nb.l.new(em.outputs[0], mix.inputs[2])
    nb.l.new(mix.outputs[0], out.inputs["Surface"])
    return m


def visual_only(*names):
    """Camera/glossy-only emitters (painted grades, haze, columns) never act as lights: no light sampling."""
    for m in bpy.data.materials:
        if any(m.name.startswith(n) for n in names):
            m.cycles.emission_sampling = "NONE"


def render_main(build, o):
    """Build, optional crop, render to out/<out>.png; with --lightgroups also a multilayer EXR."""
    import time
    t0 = time.time()
    sc = build(o)
    if o["crop"]:
        x0, x1, y0, y1 = o["crop"]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
    print("scene built", round(time.time() - t0, 1), "s", flush=True)
    os.makedirs(studio.OUT, exist_ok=True)
    path = os.path.join(studio.OUT, o["out"] + ".png")
    bpy.ops.render.render()
    rr = bpy.data.images["Render Result"]
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    rr.save_render(path, scene=sc)
    if o["lightgroups"] and sc.view_layers[0].lightgroups:
        # one multilayer EXR with a pass per light group, from the same render (for the page's light mixing)
        sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        sc.render.image_settings.color_depth = "16"
        rr.save_render(path.replace(".png", "_lg.exr"), scene=sc)
    print("rendered", path, round(time.time() - t0, 1), "s", flush=True)
    return path


# ================================================================== revision 2 (creative-director review)
# Anisotropic procedural carbon, layered hole bores, grip / cap lights, a hard-edged reflection band card,
# and a light-group compositor for sequenced variants.


def mat_carbon_aniso(name, kind="3k", tow_mm=2.0, coat_rough=0.035, bright=1.0, aniso=0.78, rough=0.30, base=None):
    """Procedural carbon with fibre-direction anisotropy (no image textures, mapped in the head's model space).
    3k: 2/2 twill of rounded tows with tiny resin gaps. 12k: plain-weave spread tow, flat tapes that butt
    together (no grout): the checker comes only from the fibre direction flipping the anisotropic highlight.
    The tangent is model +X; Anisotropic Rotation 0 / 0.25 per tow turns the highlight a quarter turn."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    x, y, _ = nb.coords("Object")
    tw = tow_mm / 1000.0
    u = nb.math("ADD", nb.math("DIVIDE", x, tw), 4000.0)
    v = nb.math("ADD", nb.math("DIVIDE", y, tw), 4000.0)
    i, j = nb.math("FLOOR", u), nb.math("FLOOR", v)
    fu, fv = nb.math("FRACT", u), nb.math("FRACT", v)
    if kind == "3k":
        # warp-over-2 / under-2, shifted one tow per row: diagonal twill
        hz = nb.math("LESS_THAN", nb.math("MODULO", nb.math("ADD", nb.math("SUBTRACT", i, j), 4000.0), 4.0), 2.0)
    else:
        hz = nb.math("LESS_THAN", nb.math("MODULO", nb.math("ADD", i, j), 2.0), 1.0)
    # across-tow coordinate (0..1) and crown profile
    acr = nb.n.new("ShaderNodeMix"); acr.data_type = "FLOAT"
    nb.l.new(hz, acr.inputs["Factor"]); nb.l.new(fu, acr.inputs[2]); nb.l.new(fv, acr.inputs[3])
    a = acr.outputs[0]
    d = nb.math("ABSOLUTE", nb.math("SUBTRACT", nb.math("MULTIPLY", a, 2.0), 1.0))  # 0 centre, 1 edge
    if kind == "3k":
        crown = nb.math("POWER", nb.math("MAXIMUM", nb.math("SUBTRACT", 1.0, nb.math("POWER", d, 2.2)), 0.0), 0.6)
        gap = nb.smooth(d, 0.86, 1.0)  # resin-rich seam between tows
    else:
        crown = nb.math("SUBTRACT", 1.0, nb.math("MULTIPLY", nb.smooth(d, 0.96, 1.0), 0.25))
        gap = nb.math("MULTIPLY", nb.smooth(d, 0.985, 1.0), 0.0)
    # filament striations running along each tow
    tc = nb.n.new("ShaderNodeTexCoord")
    st = []
    for sx, sy in ((3.0, 900.0), (900.0, 3.0)):
        mp = nb.n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (sx * 0.001 / tw, sy * 0.001 / tw * 2.6, 1.0)
        nb.l.new(tc.outputs["Object"], mp.inputs["Vector"])
        nz = nb.n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 3
        nb.l.new(mp.outputs["Vector"], nz.inputs["Vector"])
        st.append(nz.outputs["Fac"])
    sm = nb.n.new("ShaderNodeMix"); sm.data_type = "FLOAT"
    nb.l.new(hz, sm.inputs["Factor"]); nb.l.new(st[1], sm.inputs[2]); nb.l.new(st[0], sm.inputs[3])
    stri = nb.math("SUBTRACT", sm.outputs[0], 0.5)
    # per-tow tone (each tow is a slightly different bundle)
    cell = nb.n.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("MULTIPLY", hz, i), cell.inputs[0])
    nb.l.new(nb.math("MULTIPLY", nb.math("SUBTRACT", 1.0, hz), j), cell.inputs[1])
    nb.l.new(hz, cell.inputs[2])
    wn = nb.n.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"
    nb.l.new(cell.outputs[0], wn.inputs["Vector"])
    tone = nb.math("MULTIPLY_ADD", wn.outputs["Value"], 0.22, 0.89)
    if base is None:
        base = 0.045 if kind == "3k" else 0.05
    col = nb.math("MULTIPLY", nb.math("MULTIPLY", tone, base * bright), nb.math("MULTIPLY_ADD", gap, -0.6, 1.0))
    col = nb.math("MULTIPLY", col, nb.math("MULTIPLY_ADD", stri, 0.25, 1.0))
    cc = nb.n.new("ShaderNodeCombineColor")
    for k, f in enumerate((0.97, 1.0, 1.04)):
        nb.l.new(nb.math("MULTIPLY", col, f), cc.inputs[k])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = 1.0
    r = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", wn.outputs["Value"], 0.5), 0.06, rough)
    r = nb.math("ADD", r, nb.math("MULTIPLY", gap, 0.25))
    nb.l.new(r, b.inputs["Roughness"])
    b.inputs["Anisotropic"].default_value = aniso
    nb.l.new(nb.math("MULTIPLY", nb.math("SUBTRACT", 1.0, hz), 0.25), b.inputs["Anisotropic Rotation"])
    vt = nb.n.new("ShaderNodeVectorTransform")
    vt.vector_type = "VECTOR"; vt.convert_from = "OBJECT"; vt.convert_to = "WORLD"
    vt.inputs[0].default_value = (1.0, 0.0, 0.0)
    nb.l.new(vt.outputs[0], b.inputs["Tangent"])
    hgt = nb.math("ADD", nb.math("MULTIPLY", crown, 1.0), nb.math("MULTIPLY", stri, 0.08))
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5 if kind == "3k" else 0.25
    bump.inputs["Distance"].default_value = 0.00012 if kind == "3k" else 0.00004
    nb.l.new(hgt, bump.inputs["Height"])
    nb.l.new(bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = coat_rough
    b.inputs["Coat IOR"].default_value = 1.52
    return m


def mat_bore(name="Bore", eva=(0.30, 0.295, 0.285), skin_t=0.0018, glue_t=0.00035, throat_y=-0.080, throat_dim=0.25):
    """Inner walls of the head (hole bores + throat). Hole bores show the sandwich: carbon skin | amber glue line |
    EVA foam core | glue | skin (by model |z|), so every hole reads as a crescent. The throat is frame tube,
    not core: satin dark carbon, about two stops below the old lacquer wedge."""
    m = new_mat(name)
    nb = NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    x, y, z = nb.coords("Object")
    az = nb.math("ABSOLUTE", z)
    T2 = racket.THICK / 2
    is_skin = nb.math("GREATER_THAN", az, T2 - skin_t)
    is_glue = nb.math("GREATER_THAN", az, T2 - skin_t - glue_t)
    throat = nb.math("LESS_THAN", y, throat_y)

    def bsdf(color, rough, coat=0.0, metallic=0.0):
        b = nb.n.new("ShaderNodeBsdfPrincipled")
        b.inputs["Base Color"].default_value = (*color, 1)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Metallic"].default_value = metallic
        return b

    b_eva = bsdf(eva, 0.82)
    # closed-cell foam: fine cells
    tc = nb.n.new("ShaderNodeTexCoord")
    vor = nb.n.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"; vor.inputs["Scale"].default_value = 1500.0
    nb.l.new(tc.outputs["Object"], vor.inputs["Vector"])
    bp = nb.n.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.0001
    nb.l.new(nb.smooth(vor.outputs["Distance"], 0.0, 0.2), bp.inputs["Height"])
    nb.l.new(bp.outputs["Normal"], b_eva.inputs["Normal"])
    b_glue = bsdf((0.30, 0.13, 0.035), 0.4)
    b_skin = bsdf((0.022, 0.022, 0.024), 0.30, coat=0.6)
    b_throat = bsdf((0.012 * throat_dim / 0.25, 0.012 * throat_dim / 0.25, 0.013 * throat_dim / 0.25), 0.42)
    m1 = nb.n.new("ShaderNodeMixShader"); nb.l.new(is_glue, m1.inputs[0])
    nb.l.new(b_eva.outputs[0], m1.inputs[1]); nb.l.new(b_glue.outputs[0], m1.inputs[2])
    m2 = nb.n.new("ShaderNodeMixShader"); nb.l.new(is_skin, m2.inputs[0])
    nb.l.new(m1.outputs[0], m2.inputs[1]); nb.l.new(b_skin.outputs[0], m2.inputs[2])
    m3 = nb.n.new("ShaderNodeMixShader"); nb.l.new(throat, m3.inputs[0])
    nb.l.new(m2.outputs[0], m3.inputs[1]); nb.l.new(b_throat.outputs[0], m3.inputs[2])
    nb.l.new(m3.outputs[0], out.inputs["Surface"])
    return m


def override_material(ob, mat):
    """Per-object material (slot link OBJECT): linked duplicates keep sharing mesh data."""
    for slot in ob.material_slots:
        slot.link = "OBJECT"
        slot.material = mat


def part(root, suffix):
    return [p_ for p_ in root.children if p_.name.endswith(suffix)]


def band_card(name, loc, size, strength, target, grad_world, edge=0.0, soft=0.006, decay=0.10, line=0.0,
              line_w=0.004, floor=0.0, color=(1, 1, 1), additive=True):
    """Hard-edged reflection band: dark on one side of a straight edge, a crisp step at `edge` (metres along
    grad_world from the card centre, `soft` wide), then an exponential fall-off over `decay` toward the bright
    side's far end, plus an optional hot line on the edge. A lacquered face mirrors it as one crisp graded band."""
    ob = plane(name, size, loc, normal_to=target)
    bpy.context.view_layer.update()
    mw = ob.matrix_world.to_3x3()
    g = Vector(grad_world).normalized()
    gx, gy = mw.col[0].normalized().dot(g), mw.col[1].normalized().dot(g)
    ln = math.hypot(gx, gy) or 1
    gx, gy = gx / ln, gy / ln
    sx, sy = ob.scale.x or 1, ob.scale.y or 1

    def s(nb):
        x, y, _ = nb.coords("Object")
        t = nb.math("SUBTRACT", nb.math("MULTIPLY_ADD", x, gx, nb.math("MULTIPLY", y, gy)), edge)
        stepf = nb.smooth(t, -soft / 2, soft / 2)
        fall = nb.math("EXPONENT", nb.math("DIVIDE", nb.math("MINIMUM", nb.math("MULTIPLY", t, -1.0), 0.0), decay))
        f = nb.math("MULTIPLY", stepf, fall)
        if line:
            dd = nb.math("DIVIDE", t, line_w)
            f = nb.math("ADD", f, nb.math("MULTIPLY", nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", dd, dd), -1.0)), line))
        f = nb.math("MULTIPLY_ADD", f, 1 - floor, floor)
        u, v, _ = nb.coords("UV")
        e = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.08), nb.smooth(u, 1.0, 0.92)),
                    nb.math("MULTIPLY", nb.smooth(v, 0.0, 0.08), nb.smooth(v, 1.0, 0.92)))
        return nb.math("MULTIPLY", nb.math("MULTIPLY", f, e), strength)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=additive))
    visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    return ob


def mirror_dir(n, p, cam):
    v = (Vector(cam) - Vector(p)).normalized()
    n = Vector(n).normalized()
    return (2 * n.dot(v) * n - v).normalized()


def area_at(name, loc, target, size, size_y, energy, color=(1, 1, 1), recv=None, spread=180):
    lt = studio.area_light(name, tuple(loc), size, energy, color=color, size_y=size_y, target=tuple(target), spread=spread)
    lt.visible_camera = False
    lt.visible_glossy = True
    if recv is not None:
        link_receivers(lt, recv, "recv_" + name)
    return lt


def cap_ring_light(name, cap_obj, axis_down, strength, color=(1, 1, 1), radius=0.09, dist=0.10):
    """Horizontal glowing annulus below the cap, camera-invisible, linked to the cap only: the polished chamfer
    ring mirrors it all the way round as one continuous line."""
    bpy.context.view_layer.update()
    c = cap_obj.matrix_world.translation.copy()
    ad = Vector(axis_down).normalized()
    p = c + ad * dist
    ob = plane(name, (radius * 2, radius * 2), tuple(p), normal_to=tuple(c))

    def s(nb):
        u, v, _ = nb.coords("UV")
        du = nb.math("SUBTRACT", u, 0.5); dv = nb.math("SUBTRACT", v, 0.5)
        r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", du, du), nb.math("MULTIPLY", dv, dv)))
        f = nb.smooth(r, 0.5, 0.30)
        return nb.math("MULTIPLY", f, strength)

    ob.data.materials.append(emitter_mat(name + "Mat", color, s, additive=True))
    visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    link_receivers(ob, [cap_obj], "recv_" + name)
    return ob


def debug_off():
    """KQ_OFF=Key,Band_ removes every object whose name starts with one of the prefixes (look-dev only)."""
    pre = [p_ for p_ in os.environ.get("KQ_OFF", "").split(",") if p_]
    for ob in list(bpy.data.objects):
        if any(ob.name.startswith(p_) for p_ in pre):
            bpy.data.objects.remove(ob)


def seq_compositor(sc, o, seq_groups, base_groups):
    """One render, a whole switch-on sequence: writes <out>-seqN.png for N = 0..len(seq_groups)-1 (the base
    groups plus the first N sequence groups). Light-group passes are linear and additive; each is denoised
    (OIDN with the render's albedo/normal) and summed, then saved through the scene's view transform.
    The main PNG stays the normal Cycles-denoised combined image."""
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    sc.use_nodes = True
    nt = sc.node_tree
    for n_ in list(nt.nodes):
        nt.nodes.remove(n_)
    rl = nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(rl.outputs["Image"], comp.inputs["Image"])

    def den(sock):
        d = nt.nodes.new("CompositorNodeDenoise")
        d.prefilter = "ACCURATE"
        nt.links.new(sock, d.inputs["Image"])
        nt.links.new(rl.outputs["Denoising Normal"], d.inputs["Normal"])
        nt.links.new(rl.outputs["Denoising Albedo"], d.inputs["Albedo"])
        return d.outputs[0]

    def add(a, b):
        if a is None:
            return b
        m = nt.nodes.new("CompositorNodeMixRGB")
        m.blend_type = "ADD"
        m.inputs[0].default_value = 1.0
        nt.links.new(a, m.inputs[1]); nt.links.new(b, m.inputs[2])
        return m.outputs[0]

    passes = {g: den(rl.outputs["Combined_" + g]) for g in base_groups + seq_groups}
    acc = None
    for g in base_groups:
        acc = add(acc, passes[g])
    fo = nt.nodes.new("CompositorNodeOutputFile")
    path = os.path.join(studio.OUT, o["out"])
    fo.base_path = os.path.dirname(path)
    fo.format.file_format = "PNG"
    fo.format.color_depth = "16"
    fo.format.color_mode = "RGB"
    fo.file_slots.clear()
    for k in range(len(seq_groups)):
        if k > 0:
            acc = add(acc, passes[seq_groups[k - 1]])
        fo.file_slots.new(os.path.basename(path) + f"-seq{k}_")
        nt.links.new(acc, fo.inputs[k])
    o["seq_files"] = [path + f"-seq{k}_" for k in range(len(seq_groups))]


def seq_rename(o):
    """File Output appends the frame number: <out>-seqN_0001.png -> <out>-seqN.png."""
    import glob
    for stem in o.get("seq_files", []):
        hits = sorted(glob.glob(stem + "*.png"))
        if hits:
            os.replace(hits[-1], stem[:-1] + ".png")
            print("seq", stem[:-1] + ".png", flush=True)


def mix_compositor(sc, o, mixes):
    """Extra stills from the same render: mixes = {suffix: {lightgroup: weight}} -> <out>-<suffix>.png, each the
    weighted sum of denoised light-group passes through the scene's view transform (e.g. a hover state with one
    group brighter). The main PNG stays the normal Cycles-denoised combined image."""
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    sc.use_nodes = True
    nt = sc.node_tree
    for n_ in list(nt.nodes):
        nt.nodes.remove(n_)
    rl = nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(rl.outputs["Image"], comp.inputs["Image"])
    dn = {}

    def den(g):
        if g not in dn:
            d = nt.nodes.new("CompositorNodeDenoise")
            d.prefilter = "ACCURATE"
            nt.links.new(rl.outputs["Combined_" + g], d.inputs["Image"])
            nt.links.new(rl.outputs["Denoising Normal"], d.inputs["Normal"])
            nt.links.new(rl.outputs["Denoising Albedo"], d.inputs["Albedo"])
            dn[g] = d.outputs[0]
        return dn[g]

    fo = nt.nodes.new("CompositorNodeOutputFile")
    path = os.path.join(studio.OUT, o["out"])
    fo.base_path = os.path.dirname(path)
    fo.format.file_format = "PNG"
    fo.format.color_depth = "16"
    fo.format.color_mode = "RGB"
    fo.file_slots.clear()
    o["seq_files"] = []
    for k, (suffix, weights) in enumerate(mixes.items()):
        acc = None
        for g, w in weights.items():
            s_ = den(g)
            if w != 1.0:
                m = nt.nodes.new("CompositorNodeMixRGB"); m.blend_type = "MULTIPLY"; m.inputs[0].default_value = 1.0
                nt.links.new(s_, m.inputs[1]); m.inputs[2].default_value = (w, w, w, 1)
                s_ = m.outputs[0]
            if acc is None:
                acc = s_
            else:
                a_ = nt.nodes.new("CompositorNodeMixRGB"); a_.blend_type = "ADD"; a_.inputs[0].default_value = 1.0
                nt.links.new(acc, a_.inputs[1]); nt.links.new(s_, a_.inputs[2])
                acc = a_.outputs[0]
        fo.file_slots.new(os.path.basename(path) + f"-{suffix}_")
        nt.links.new(acc, fo.inputs[k])
        o["seq_files"].append(path + f"-{suffix}_")
