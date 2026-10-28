"""KINETIQ racket model and materials for Blender (bpy 4.2).

Geometry is the same silhouette as src/lib/racket-shape.ts (1 unit = 10 cm),
built at real size in metres: 260 mm wide, 455 mm long, 38 mm thick, 42 holes.
"""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
import kqpaths  # noqa: E402  (render/kqpaths.py: generated files live outside git)
TEX = kqpaths.asset("tex")
FONT_BOLD = kqpaths.font("Archivo-ExpandedExtraBold.ttf")
FONT_MED = kqpaths.font("Archivo-Medium.ttf")

U = 0.1  # 1 shape unit = 10 cm

HEAD_START = (0, 1.55)
HEAD_CURVES = [
    ((0.85, 1.55), (1.32, 0.95), (1.3, 0.25)),
    ((1.28, -0.55), (0.75, -1.05), (0.2, -1.55)),
    ((0.07, -1.55), (-0.07, -1.55), (-0.2, -1.55)),
    ((-0.75, -1.05), (-1.28, -0.55), (-1.3, 0.25)),
    ((-1.32, 0.95), (-0.85, 1.55), (0, 1.55)),
]
THROAT_START = (-0.32, -0.88)
THROAT_CURVES = [
    ((-0.1, -0.86), (0.1, -0.86), (0.32, -0.88)),
    ((0.3, -1.0), (0.12, -1.2), (0, -1.27)),
    ((-0.12, -1.2), (-0.3, -1.0), (-0.32, -0.88)),
]
HOLE_R = 0.062
THICK = 0.038  # metres


def holes():
    centre = (0.0, 0.3)
    step = 0.27
    cands = []
    for row in range(-6, 7):
        y = centre[1] + row * step * 0.87
        off = 0 if row % 2 == 0 else step / 2
        for col in range(-6, 7):
            x = col * step + off
            inside = (x * x) / 1.0 + ((y - centre[1]) ** 2) / (1.08 * 1.08) < 1
            if inside and y > -0.62:
                cands.append((round(x, 3), round(y, 3)))

    def d(p):
        return p[0] * p[0] * 1.1 + (p[1] - centre[1]) ** 2

    cands.sort(key=lambda p: (d(p), p[0]))
    return cands[:42]


def _bezier_spline(cu, start, curves):
    sp = cu.splines.new("BEZIER")
    n = len(curves)
    sp.bezier_points.add(n - 1)
    pts = [start] + [c[2] for c in curves[:-1]]
    for k, p in enumerate(pts):
        bp = sp.bezier_points[k]
        bp.co = (p[0] * U, p[1] * U, 0)
        bp.handle_left_type = bp.handle_right_type = "FREE"
    for k, (c1, c2, _end) in enumerate(curves):
        a = sp.bezier_points[k]
        b = sp.bezier_points[(k + 1) % n]
        a.handle_right = (c1[0] * U, c1[1] * U, 0)
        b.handle_left = (c2[0] * U, c2[1] * U, 0)
    sp.use_cyclic_u = True
    sp.resolution_u = 48
    return sp


def _apply_all(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    old = obj.data
    obj.modifiers.clear()
    obj.data = me
    if isinstance(old, bpy.types.Mesh) and old.users == 0:
        bpy.data.meshes.remove(old)
    return obj


def fix_normals(obj):
    """Make all faces point outward (curve fills come out inconsistent)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def _link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def _cubic(p0, c1, c2, p1, n):
    out = []
    for k in range(n):
        t = k / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t**3 * p1[0]
        y = mt**3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t**3 * p1[1]
        out.append((x * U, y * U))
    return out


def _loop(start, curves, per=72):
    pts, p0 = [], start
    for c1, c2, p1 in curves:
        seg = _cubic(p0, c1, c2, p1, per)
        pts.extend(seg)
        p0 = p1
    # drop near-duplicates
    clean = [pts[0]]
    for p in pts[1:]:
        if (p[0] - clean[-1][0]) ** 2 + (p[1] - clean[-1][1]) ** 2 > 1e-10:
            clean.append(p)
    return clean


def _area(loop):
    return 0.5 * sum(loop[i][0] * loop[(i + 1) % len(loop)][1] - loop[(i + 1) % len(loop)][0] * loop[i][1] for i in range(len(loop)))


def _offset(loop, d):
    """Move every point along its left normal by d (solid is on the left for all loops)."""
    n = len(loop)
    out = []
    for i in range(n):
        ax, ay = loop[i - 1]
        bx, by = loop[(i + 1) % n]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1.0
        out.append((loop[i][0] - ty / ln * d, loop[i][1] + tx / ln * d))
    return out


def build_head(name="KQ_Head", coll=None, frame_radius=0.0095, lip=0.0011, inset=0.0):
    """Watertight slab: caps tessellated with holes, side walls stitched, edges rounded by weighted bevels.
    inset > 0 builds the matching foam core: every boundary moved into the solid by `inset`."""
    from mathutils.geometry import tessellate_polygon

    outline = _loop(HEAD_START, HEAD_CURVES, 96)
    throat = _loop(THROAT_START, THROAT_CURVES, 48)
    hole_loops = []
    for (hx, hy) in holes():
        n = 48
        hole_loops.append([(hx * U + HOLE_R * U * math.cos(2 * math.pi * k / n), hy * U + HOLE_R * U * math.sin(2 * math.pi * k / n)) for k in range(n)])
    # orientation: outline CCW, inner loops CW
    if _area(outline) < 0:
        outline.reverse()
    inner = []
    for lp in [throat] + hole_loops:
        if _area(lp) > 0:
            lp = lp[::-1]
        inner.append(lp)
    loops = [outline] + inner
    if inset:
        # robust inward buffer of the whole region (no self-intersections at corners)
        from shapely.geometry import Polygon
        poly = Polygon(outline, holes=inner).buffer(-inset, join_style=1, resolution=16)
        ext = list(poly.exterior.coords)[:-1]
        ints = [list(r.coords)[:-1] for r in poly.interiors]
        if _area(ext) < 0:
            ext.reverse()
        ints = [r[::-1] if _area(r) > 0 else r for r in ints]
        ints.sort(key=lambda r: abs(_area(r)), reverse=True)  # throat (largest) first
        loops = [ext] + ints
        frame_radius = max(frame_radius - inset, 0.001)
        lip = max(lip - inset * 0.5, 0.0003)

    zt, zb = THICK / 2 - inset, -THICK / 2 + inset
    bm = bmesh.new()
    top_rings, bot_rings = [], []
    for lp in loops:
        top_rings.append([bm.verts.new((x, y, zt)) for (x, y) in lp])
        bot_rings.append([bm.verts.new((x, y, zb)) for (x, y) in lp])
    bm.verts.ensure_lookup_table()
    # caps
    flat = [v for ring in top_rings for v in ring]
    polys = [[Vector((x, y, 0)) for (x, y) in lp] for lp in loops]
    tris = tessellate_polygon(polys)
    offsets = []
    acc = 0
    for lp in loops:
        offsets.append(acc)
        acc += len(lp)
    flat_bot = [v for ring in bot_rings for v in ring]
    for t in tris:
        a, b, c = t
        try:
            bm.faces.new((flat[a], flat[b], flat[c]))
        except ValueError:
            pass
        try:
            bm.faces.new((flat_bot[c], flat_bot[b], flat_bot[a]))
        except ValueError:
            pass
    # walls
    for top, bot in zip(top_rings, bot_rings):
        n = len(top)
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new((bot[k], bot[j], top[j], top[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    # bevel weights: outline and throat rims get the frame radius, holes get the lip
    bw_frame = bm.edges.layers.float.new("bevel_weight_edge")
    for li, (top, bot) in enumerate(zip(top_rings, bot_rings)):
        for ring in (top, bot):
            n = len(ring)
            for k in range(n):
                e = bm.edges.get((ring[k], ring[(k + 1) % n]))
                if e is None:
                    continue
                if li < 2:
                    e[bw_frame] = 1.0
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    head = _link(bpy.data.objects.new(name, me), coll)

    b1 = head.modifiers.new("frame", "BEVEL")
    b1.limit_method = "WEIGHT"
    b1.width = frame_radius
    b1.segments = 10
    b1.profile = 0.5
    b1.miter_outer = "MITER_ARC"
    _apply_all(head)
    # after the frame is rounded, the only sharp edges left are the hole rims
    b2 = head.modifiers.new("lips", "BEVEL")
    b2.limit_method = "ANGLE"
    b2.angle_limit = math.radians(45)
    b2.width = lip
    b2.segments = 5
    _apply_all(head)
    me = head.data
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(40))
    wn = head.modifiers.new("flat_faces", "WEIGHTED_NORMAL")
    wn.mode = "FACE_AREA"
    wn.weight = 100
    wn.keep_sharp = True
    wn.thresh = 0.01
    _apply_all(head)
    return head


def build_handle(name="KQ_Handle", coll=None):
    """Grip (overgrip), titanium collar at the throat, end cap."""
    parts = []
    top = -1.5 * U
    length = 0.140
    # grip: slightly oval, tapering
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.0168, depth=length, location=(0, top - length / 2 - 0.006, 0), rotation=(math.radians(90), 0, 0))
    grip = bpy.context.active_object
    grip.name = name + "_grip"
    grip.scale = (1.0, 1.0, 0.86)
    bv = grip.modifiers.new("b", "BEVEL")
    bv.width = 0.003
    bv.segments = 4
    sub = grip.modifiers.new("s", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    _apply_all(grip)
    grip.data.shade_smooth()
    parts.append(grip)
    # collar ring at the throat
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0172, minor_radius=0.0028, major_segments=96, minor_segments=24, location=(0, top - 0.004, 0), rotation=(math.radians(90), 0, 0))
    collar = bpy.context.active_object
    collar.name = name + "_collar"
    collar.scale = (1.0, 1.0, 0.86)
    collar.data.shade_smooth()
    parts.append(collar)
    # end cap
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.0192, depth=0.010, location=(0, top - length - 0.010, 0), rotation=(math.radians(90), 0, 0))
    cap = bpy.context.active_object
    cap.name = name + "_cap"
    cap.scale = (1.0, 1.0, 0.86)
    bv = cap.modifiers.new("b", "BEVEL")
    bv.width = 0.0025
    bv.segments = 5
    _apply_all(cap)
    cap.data.shade_smooth()
    parts.append(cap)
    for p in parts:
        for c in p.users_collection:
            c.objects.unlink(p)
        _link(p, coll)
    return grip, collar, cap


def build_text(body, size, loc, font=FONT_BOLD, name="KQ_Text", coll=None, extrude=0.00008, spacing=1.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(font, check_existing=True)
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = extrude
    cu.space_character = spacing
    ob = _link(bpy.data.objects.new(name, cu), coll)
    ob.location = loc
    return ob


# ---------------------------------------------------------------- materials

def _img(nodes, name, colorspace):
    n = nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(os.path.join(TEX, name), check_existing=True)
    n.image.colorspace_settings.name = colorspace
    n.projection = "BOX"
    n.projection_blend = 0.25
    n.interpolation = "Cubic"
    return n


def mat_carbon(name="Carbon", tow_mm=2.6, coat_rough=0.035, tint=(1, 1, 1), kind="3k", flow_holes=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    tc = nodes.new("ShaderNodeTexCoord")
    mp = nodes.new("ShaderNodeMapping")
    prefix = "weave" if kind == "3k" else "spread"
    tows_per_tile = 16 if kind == "3k" else 4
    tile_m = tow_mm * tows_per_tile / 1000.0
    mp.inputs["Scale"].default_value = (1 / tile_m, 1 / tile_m, 1 / tile_m)
    links.new(tc.outputs["Object"], mp.inputs["Vector"])
    alb = _img(nodes, f"{prefix}_albedo.png", "sRGB")
    rough = _img(nodes, f"{prefix}_rough.png", "Non-Color")
    hgt = _img(nodes, f"{prefix}_height.png", "Non-Color")
    for n in (alb, rough, hgt):
        links.new(mp.outputs["Vector"], n.inputs["Vector"])
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs["Fac"].default_value = 1.0
    mix.inputs["Color2"].default_value = (*tint, 1)
    links.new(alb.outputs["Color"], mix.inputs["Color1"])
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    height_out = hgt.outputs["Color"]
    if flow_holes:
        # Fibre that flows around each hole: concentric striations replace the weave near the rim.
        sep = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tc.outputs["Object"], sep.inputs["Vector"])
        mask_acc = None
        ring_acc = None
        for (hx, hy, hr) in flow_holes:
            dx = nodes.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = hx
            links.new(sep.outputs["X"], dx.inputs[0])
            dy = nodes.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = hy
            links.new(sep.outputs["Y"], dy.inputs[0])
            comb = nodes.new("ShaderNodeCombineXYZ")
            links.new(dx.outputs[0], comb.inputs["X"]); links.new(dy.outputs[0], comb.inputs["Y"])
            ln = nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
            links.new(comb.outputs[0], ln.inputs[0])
            m = nodes.new("ShaderNodeMapRange")
            m.inputs["From Min"].default_value = hr * 1.05
            m.inputs["From Max"].default_value = hr * 1.9
            m.inputs["To Min"].default_value = 1.0
            m.inputs["To Max"].default_value = 0.0
            m.interpolation_type = "SMOOTHSTEP"
            links.new(ln.outputs["Value"], m.inputs["Value"])
            ring = nodes.new("ShaderNodeMath"); ring.operation = "MULTIPLY"; ring.inputs[1].default_value = 2 * math.pi / 0.00022
            links.new(ln.outputs["Value"], ring.inputs[0])
            sn = nodes.new("ShaderNodeMath"); sn.operation = "SINE"
            links.new(ring.outputs[0], sn.inputs[0])
            sc = nodes.new("ShaderNodeMapRange")
            sc.inputs["From Min"].default_value = -1; sc.inputs["From Max"].default_value = 1
            sc.inputs["To Min"].default_value = 0.35; sc.inputs["To Max"].default_value = 0.65
            links.new(sn.outputs[0], sc.inputs["Value"])
            if mask_acc is None:
                mask_acc, ring_acc = m.outputs["Result"], sc.outputs["Result"]
            else:
                mx = nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
                links.new(mask_acc, mx.inputs[0]); links.new(m.outputs["Result"], mx.inputs[1])
                ad = nodes.new("ShaderNodeMath"); ad.operation = "ADD"
                links.new(ring_acc, ad.inputs[0]); links.new(sc.outputs["Result"], ad.inputs[1])
                mask_acc, ring_acc = mx.outputs[0], ad.outputs[0]
        mixh = nodes.new("ShaderNodeMix"); mixh.data_type = "FLOAT"
        links.new(mask_acc, mixh.inputs["Factor"])
        links.new(hgt.outputs["Color"], mixh.inputs[2])
        links.new(ring_acc, mixh.inputs[3])
        height_out = mixh.outputs[0]
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.55
    bump.inputs["Distance"].default_value = 0.00025
    links.new(height_out, bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Metallic"].default_value = 0.15
    bsdf.inputs["Specular IOR Level"].default_value = 0.6
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat Roughness"].default_value = coat_rough
    bsdf.inputs["Coat IOR"].default_value = 1.52
    return m


def mat_grip(name="Grip", color=(0.012, 0.012, 0.013)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.62
    bsdf.inputs["Sheen Weight"].default_value = 0.08
    # helical overgrip wrap: phase = y / pitch + angle / 2pi
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sep.inputs["Vector"])
    at = nodes.new("ShaderNodeMath")
    at.operation = "ARCTAN2"
    links.new(sep.outputs["X"], at.inputs[0])
    links.new(sep.outputs["Z"], at.inputs[1])
    a2 = nodes.new("ShaderNodeMath")
    a2.operation = "DIVIDE"
    a2.inputs[1].default_value = 2 * math.pi
    links.new(at.outputs[0], a2.inputs[0])
    yp = nodes.new("ShaderNodeMath")
    yp.operation = "DIVIDE"
    yp.inputs[1].default_value = 0.022  # wrap pitch 22 mm
    links.new(sep.outputs["Y"], yp.inputs[0])
    ph = nodes.new("ShaderNodeMath")
    ph.operation = "ADD"
    links.new(yp.outputs[0], ph.inputs[0])
    links.new(a2.outputs[0], ph.inputs[1])
    fr = nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    links.new(ph.outputs[0], fr.inputs[0])
    # overlap ridge near the start of each wrap
    ridge = nodes.new("ShaderNodeMapRange")
    ridge.inputs["From Min"].default_value = 0.0
    ridge.inputs["From Max"].default_value = 0.18
    ridge.inputs["To Min"].default_value = 0.0
    ridge.inputs["To Max"].default_value = 1.0
    links.new(fr.outputs[0], ridge.inputs["Value"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 900
    noise.inputs["Detail"].default_value = 2
    add = nodes.new("ShaderNodeMath")
    add.operation = "MULTIPLY_ADD"
    add.inputs[1].default_value = 0.08
    links.new(noise.outputs["Fac"], add.inputs[0])
    links.new(ridge.outputs["Result"], add.inputs[2])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.0004
    links.new(add.outputs[0], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def mat_metal(name="Titanium", color=(0.42, 0.42, 0.44), rough=0.22, brushed=True):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = rough
    if brushed:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 4000
        mp = nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1, 0.002, 1)
        tc = nodes.new("ShaderNodeTexCoord")
        links.new(tc.outputs["Object"], mp.inputs["Vector"])
        links.new(mp.outputs["Vector"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.15
        bump.inputs["Distance"].default_value = 0.0001
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def mat_basic(name, color, rough=0.5, metallic=0.0, coat=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Coat Weight"].default_value = coat
    if emission:
        b.inputs["Emission Color"].default_value = (*emission, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def build_racket(name="KQ", coll=None, edition="reserve", serial=None, kind="3k", face_print=False,
                 etch=True, flow_holes=None, carbon=None):
    """Whole racket as a parented group. Model space: face in XY, +Z out of the front face, head up (+Y).
    kind: '3k' (Command) or '12k' (Pace). etch: laser-etched KINETIQ / SWISS MADE on the side walls."""
    head = build_head(name + "_Head", coll)
    grip, collar, cap = build_handle(name + "_Handle", coll)
    if carbon is None:
        key = f"Carbon_{kind}" + ("_flow" if flow_holes else "")
        carbon = bpy.data.materials.get(key) or mat_carbon(key, tow_mm=2.6 if kind == "3k" else 2.2, kind=kind, flow_holes=flow_holes)
    assign(head, carbon)
    assign(grip, bpy.data.materials.get("Grip") or mat_grip())
    accent = bpy.data.materials.get("Titanium") or mat_metal()
    assign(collar, accent)
    assign(cap, bpy.data.materials.get("CapCarbon") or mat_carbon("CapCarbon", tow_mm=1.6))
    parts = [head, grip, collar, cap]
    z = THICK / 2 + 0.00004
    if face_print:
        word = build_text("KINETIQ", 0.0105, (0, -0.0745, z), FONT_BOLD, name + "_Word", coll, spacing=1.25)
        ink = bpy.data.materials.get("Ink") or mat_metal("Ink", (0.55, 0.55, 0.57), 0.32, brushed=False)
        word.data.materials.append(ink)
        parts.append(word)
    if etch:
        etch_mat = bpy.data.materials.get("Etch") or mat_basic("Etch", (0.05, 0.05, 0.052), rough=0.62)
        parts.append(etch_side(head, "KINETIQ", -0.95, 0.0034, side=1, name=name + "_EtchR", coll=coll, mat=etch_mat, font=FONT_BOLD))
        parts.append(etch_side(head, serial or "SWISS MADE", -0.95, 0.0026, side=-1, name=name + "_EtchL", coll=coll, mat=etch_mat))
    root = bpy.data.objects.new(name, None)
    _link(root, coll)
    for p in parts:
        p.parent = root
    return root


def etch_side(head, text, y_units, size=0.0032, side=1, name="KQ_Etch", coll=None, mat=None, font=None):
    """Laser-etched text on the frame side wall at height y (shape units), shrink-wrapped to the wall.
    side=+1 right wall, -1 left wall. Reads along the wall, letters upright in Z."""
    outline = _loop(HEAD_START, HEAD_CURVES, 400)
    pts = [p for p in outline if (p[0] > 0) == (side > 0)]
    tgt = y_units * U
    best = min(range(len(pts)), key=lambda k: abs(pts[k][1] - tgt))
    p = pts[best]
    q = pts[min(best + 1, len(pts) - 1)]
    tx, ty = q[0] - p[0], q[1] - p[1]
    ang = math.atan2(ty, tx)
    ob = build_text(text, size, (0, 0, 0), font or FONT_MED, name, coll, extrude=0.0, spacing=1.35)
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    ob = _link(bpy.data.objects.new(name, me), coll)
    # text lies in XY; stand it on the wall: rotate so its X runs along the tangent and its Y is +Z
    from mathutils import Euler
    ob.rotation_euler = Euler((math.radians(90), 0, ang + (math.pi if side < 0 else 0)), "XYZ")
    nx, ny = (ty, -tx) if side > 0 else (-ty, tx)
    ln = math.hypot(nx, ny) or 1
    ob.location = (p[0] + nx / ln * 0.002, p[1] + ny / ln * 0.002, 0)
    sw = ob.modifiers.new("wrap", "SHRINKWRAP")
    sw.target = head
    sw.wrap_method = "NEAREST_SURFACEPOINT"
    sw.offset = 0.00004
    _apply_all(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob
