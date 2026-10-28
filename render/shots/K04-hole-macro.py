"""K04-hole-macro (v4, white Command, 2026-10-22): extreme macro of the face around the sweet-spot hole (racket hole (0, 0.3)).

v5 (AD stage 3a, 2026-10-22; backup shots/K04-hole-macro.v4-white-precrit3a.bak): the art director's fixes, all in
V5_DEFAULTS (--v5 0 restores v4). Camera, geometry and light groups unchanged, so base and full stay registered.
- copy contrast: the pool gets gobo flags in frame coordinates (pool_gobo: lamp-local direction -> frame homography);
  the copy column stays dark to x .42 (steel copy >= 8:1 median in the column's last tenth at 1280-2560), the top falls
  to mid-grey (no defocused haze) and the bottom falls off for phones (card bottom 10 % luma ~45). A weak gobo'd shade
  spot (lg_shade, fill group) keeps the shade side white-in-shadow.
- weave: a crisp 0.045 mm gap line between floats (k04_gap.py -> k04_tex2/gap16.png) on face, lips and bores,
  stronger warp/weft step (dir_tone 0.26) and fibre bundles (streak_a 0.14, lips 1.6x).
- lips: diffuse-only pool (no pinpoint flashes); lg_lipline, a thin glossy-only arc high beyond the holes, draws one
  long continuous highlight along every far lip edge; the sleeve phase puts a row boundary mid-meniscus (short,
  staggered tiles); white ends at the meniscus tangent and the lining turns graphite within 0.6 mm, keeping its twill.
- full: a strong glossy amber arc (an amber crescent in the hero lip's lacquer) and the glow lighting the woven lower
  lining (tone-modulated, feathered, no flame tongues); base has no cool bounce. Focus on the far lip, f/64.

v4 (canon: Command is WHITE 3K twill, the default in any image that names no feel). Camera, geometry, light groups and
the base/full compositing are v3's, so base and full stay registered and the frame matches the v3 final pixel for pixel.
What changed (v3 below is kept and runs with --white 0; backup shots/K04-hole-macro.v3-black.bak):
- face: carbon_white_baked = kq_canon.mat_white's recipe and COMMAND_WHITE numbers on the same baked 2.6 mm maps
  (k04_bake), with the canon's fibre-bundle streaks run in the WARPED weave coordinates (k04_bake_warp.py: warpx16 /
  warpy16), so they bend with the tows round every rim; relief bump MACRO_BUMP (0.08) for the 4x macro.
- lips and bores: white_sleeve, a cylindrical twill sleeve on k04_tex2 that folds over the meniscus and lines the bore
  (tows run round the lip and down the wall), so the lip reads as woven carbon, not a polished ring; the bore lining
  darkens to a dark graphite over the ~6 mm the camera sees (the hole still reads as a through-hole).
- light (WHITE_DEFAULTS): white needs real diffuse light (canon lighting note 8): lg_pool, a soft 10 deg spot from behind
  the camera's right shoulder, in the KEY group, sweeps the white face from the right and leaves the text zone (left
  third) in shade; key strip, sheen (glossy only) and ring (glossy only + a faint diffuse warm wash on the hero lip, same
  group) are retuned. Mesh attributes 'hc' and 's' were added to the lip and bore meshes (geometry unchanged).
Previews: out/k04w/. Final: --w 3200 --h 1800 --spp 160 --variant both --out final/K04-hole-macro.
Note: --comp re-composites from the half-float EXR; a firefly above the half range can denoise to a black speck there.

Geometry (kept from v2): a local, high-resolution patch of the real face (hole centres from racket.holes(), 38 mm slab,
12.4 mm bores), every hole with a clearcoat meniscus (elliptical lip) and analytic custom normals.

Carbon (v3): racket.mat_carbon(flow_holes=...) rebuilt for a macro under a clearcoat (the procedural part is baked to
world-space maps by shots/k04_bake.py from shots/k04_tex2, which shots/k04_weave2.py generates; run both first):
- base = graphite-like anisotropic metal (the fibres), tangent ACROSS the local fibre direction from shots/k04_tex2
  (2/2 twill with per-tow width, meander and 0.04-0.12 mm filament streaks; no two cells match),
- coat weight 1, roughness 0.035, with a faint low-pass print-through of the weave in the coat normal,
- weave coordinates pin-displaced around every hole (area-preserving, wide influence), so the tows bend round the rim,
  compress against it, cross the meniscus and run down the bore; mat_carbon's flow rings survive only as faint
  concentric filaments on the meniscus (they no longer replace the weave),
- relief bump cut by ~65 % (the coat levels the face; the weave reads through anisotropy, not relief).

Light (each its own light group; the shot renders ONCE and both variants are composited from the same samples, so
base and full are pixel-registered):
- key   : hard grazing strip at 8 deg from the top-left (lips in the text zone excluded).
- sheen : a reflected softbox band with a soft but visible diagonal edge across the upper right.
- ring  : amber 2700 K kicker, an arc band behind the camera (az window, vertical gradient), light-linked to the HERO lip
          only: the far inner lip catches it as a crescent that fades round the sides and is absent on the near lip.
- glow  : warm light rising through the bores, written into the bore wall (camera-only emission), confined to the
          deepest visible crescent, incandescent core -> amber edge, modulated by the tows running down the wall.
Variants: full = key + sheen + ring + glow; base = key + sheen + a faint cool bounce (6 %) of the glow shape.
The left flag is a compositor burn. Denoising per light group (OIDN with albedo + normal).

Usage: K04-hole-macro.py --w 960 --h 540 --spp 48 --out K04_prev [--variant full|base|both]
  Writes <out>-full.png / <out>-base.png (both) or <out>.png (one variant), plus <out>.exr (raw light-group passes).
  --comp <exr>: recomposite an earlier render's passes (gains: --g_key --g_sheen --g_ring --g_glow --g_cool, --burn).
Dev flags: --yaw deg, --fw mm, --fstop f, --focus f (0 near rim .. 1 hole centre), --k warp, --crop x0,x1,y0,y1.
"""
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import kqpaths  # noqa: E402

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.geometry import tessellate_polygon  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402
from look_c import softbox  # noqa: E402,F401


# ------------------------------------------------------------------ CLI
def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 960, "h": 540, "spp": 32, "out": "K04_prev", "variant": "full"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            o[k] = v
            i += 1
        elif a.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            o[a[2:]] = argv[i + 1]
            i += 2
        elif a.startswith("--"):
            o[a[2:]] = True
            i += 1
        else:
            i += 1
    for k in ("w", "h", "spp"):
        o[k] = int(o[k])
    return o


def out_path(name):
    p = name if name.endswith(".png") else name + ".png"
    if not os.path.isabs(p):
        p = os.path.join(studio.OUT, p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# ------------------------------------------------------------------ geometry
U = racket.U
R = racket.HOLE_R * U          # 6.2 mm bore radius
ZT = racket.THICK / 2           # front face z
ZB = -racket.THICK / 2
FO = 0.0016                     # meniscus: radial run on the face
FZ = 0.0011                     # meniscus: depth into the bore
HERO = (0.0, 0.3)               # sweet-spot hole, shape units


def hole_profile(n_lip=28, n_bore=6, n_back=6):
    """(r, z, nr, nz) from the face edge of the lip, over the meniscus, down the bore, out the back."""
    pts = []
    for k in range(n_lip + 1):
        t = k / n_lip * math.pi / 2
        r = R + FO * (1 - math.sin(t))
        z = ZT - FZ * (1 - math.cos(t))
        nr, nz = -math.sin(t) / FO, math.cos(t) / FZ
        ln = math.hypot(nr, nz)
        pts.append((r, z, nr / ln, nz / ln))
    for k in range(1, n_bore):
        z = (ZT - FZ) + (ZB + FZ - (ZT - FZ)) * k / n_bore
        pts.append((R, z, -1.0, 0.0))
    for k in range(n_back + 1):
        t = math.pi / 2 - k / n_back * math.pi / 2
        r = R + FO * (1 - math.sin(t))
        z = ZB + FZ * (1 - math.cos(t))
        nr, nz = -math.sin(t) / FO, -math.cos(t) / FZ
        ln = math.hypot(nr, nz)
        pts.append((r, z, nr / ln, nz / ln))
    return pts


def _mesh_object(name, verts, norms, faces):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(clean_customdata=False)
    # orient every face so its geometric normal agrees with the analytic vertex normals
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    flip = []
    for f in bm.faces:
        avg = Vector((0, 0, 0))
        for v in f.verts:
            avg += Vector(norms[v.index])
        if f.normal.dot(avg) < 0:
            flip.append(f)
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.normals_split_custom_set_from_vertices([Vector(n).normalized() for n in norms])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build_patch(centre_m, radius=0.075, seg_hero=768, seg_other=384):
    """Disc of the face around centre_m with every racket hole inside it. Two objects with coincident seams:
    'FacePatch' (flat caps and outer wall) and 'Lips' (every hole's meniscus, bore and back lip), so lights can be
    linked to the lips alone."""
    cx, cy = centre_m
    hs = []
    for (hx, hy) in racket.holes():
        x, y = hx * U, hy * U
        if math.hypot(x - cx, y - cy) + R + FO < radius - 0.004:
            hs.append((x, y))
    prof = hole_profile()
    F = {"v": [], "n": [], "f": []}
    L = {"v": [], "n": [], "f": [], "hc": [], "s": []}
    Bo = {"v": [], "n": [], "f": [], "hc": [], "s": []}
    n_lip = 28  # hole_profile default: rows 0..n_lip are the front meniscus
    # v4: arc length along the profile from the face edge of the lip (m), and each vertex's hole centre, as mesh
    # attributes for the white twill sleeve that folds over the lip and lines the bore (geometry unchanged)
    s_prof = [0.0]
    for k in range(1, len(prof)):
        s_prof.append(s_prof[-1] + math.hypot(prof[k][0] - prof[k - 1][0], prof[k][1] - prof[k - 1][1]))

    def add(D, p, n, hc=None, s_=None):
        D["v"].append(p)
        D["n"].append(n)
        if "hc" in D:
            D["hc"].append(hc)
            D["s"].append(s_)
        return len(D["v"]) - 1

    top_loops, bot_loops = [], []
    for (x, y) in hs:
        hero = abs(x - cx) < 1e-6 and abs(y - cy) < 1e-6
        n = seg_hero if hero else seg_other
        for D, rows in ((L, range(0, n_lip + 1)), (Bo, range(n_lip, len(prof)))):
            grid = []
            for k in rows:
                r, z, nr, nz = prof[k]
                row = []
                for j in range(n):
                    a = 2 * math.pi * j / n
                    ca, sa = math.cos(a), math.sin(a)
                    row.append(add(D, (x + r * ca, y + r * sa, z), (nr * ca, nr * sa, nz), (x, y, 0.0), s_prof[k]))
                grid.append(row)
            for k in range(len(grid) - 1):
                for j in range(n):
                    j2 = (j + 1) % n
                    D["f"].append((grid[k][j], grid[k + 1][j], grid[k + 1][j2], grid[k][j2]))
            if D is L:
                top_loops.append([add(F, D["v"][i], (0, 0, 1)) for i in grid[0]])
            else:
                bot_loops.append([add(F, D["v"][i], (0, 0, -1)) for i in grid[-1]])
    nout = 512
    ring = [(cx + radius * math.cos(2 * math.pi * j / nout), cy + radius * math.sin(2 * math.pi * j / nout)) for j in range(nout)]
    otop = [add(F, (px, py, ZT), (0, 0, 1)) for (px, py) in ring]
    obot = [add(F, (px, py, ZB), (0, 0, -1)) for (px, py) in ring]
    wt = [add(F, (px, py, ZT), (px - cx, py - cy, 0)) for (px, py) in ring]
    wb = [add(F, (px, py, ZB), (px - cx, py - cy, 0)) for (px, py) in ring]
    for j in range(nout):
        j2 = (j + 1) % nout
        F["f"].append((wb[j], wb[j2], wt[j2], wt[j]))
    for loops, z in (([otop] + top_loops, ZT), ([obot] + bot_loops, ZB)):
        polys = [[Vector((F["v"][i][0], F["v"][i][1], 0)) for i in lp] for lp in loops]
        flat = [i for lp in loops for i in lp]
        for (a, b, c) in tessellate_polygon(polys):
            F["f"].append((flat[a], flat[b], flat[c]) if z > 0 else (flat[c], flat[b], flat[a]))
    face = _mesh_object("FacePatch", F["v"], F["n"], F["f"])
    lips = _mesh_object("Lips", L["v"], L["n"], L["f"])
    _point_attrs(lips, L)
    # one object per hole lip (same verts), so lights can be flagged per hole
    bpy.context.view_layer.objects.active = lips
    for o2 in bpy.context.selected_objects:
        o2.select_set(False)
    lips.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    lips = [o2 for o2 in bpy.context.scene.objects if o2.name.startswith("Lips")]
    bores = _mesh_object("Bores", Bo["v"], Bo["n"], Bo["f"])
    _point_attrs(bores, Bo)
    return face, lips, bores, hs


def _point_attrs(ob, D):
    """Per-vertex hole centre ('hc') and profile arc length ('s') on a lip or bore mesh (vertex order as built)."""
    me = ob.data
    assert len(me.vertices) == len(D["hc"])
    a = me.attributes.new("hc", "FLOAT_VECTOR", "POINT")
    a.data.foreach_set("vector", [c for v in D["hc"] for c in v])
    b = me.attributes.new("s", "FLOAT", "POINT")
    b.data.foreach_set("value", D["s"])


# ------------------------------------------------------------------ material
def _n(nodes, kind, op=None, **kw):
    n = nodes.new(kind)
    if op:
        n.operation = op
    for k, v in kw.items():
        n.inputs[k].default_value = v
    return n


BAKE = kqpaths.asset("k04_bake")


def _bimg(nodes, links, vec, fn, cs, interp="Linear"):
    n = nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(os.path.join(BAKE, fn), check_existing=True)
    n.image.colorspace_settings.name = cs
    n.projection = "FLAT"
    n.interpolation = interp
    n.extension = "EXTEND"
    links.new(vec, n.inputs["Vector"])
    return n


def carbon_baked(holes_m, o):
    """racket.mat_carbon(flow_holes=...) as the base material, with its procedural weave and flow rings replaced by the
    world-space bake of the same maths (shots/k04_bake.py: warped 2/2 twill, flow rings, physical fibre tangent).
    Base = graphite-like anisotropic metal (the fibres) under a 0.035-rough clearcoat with a whisper of print-through."""
    import json
    meta = json.load(open(os.path.join(BAKE, "bake.json")))
    racket.mat_carbon("Carbon_K04", tow_mm=2.6, kind="3k", coat_rough=float(o.get("coat_rough", 0.035)),
                      flow_holes=[(x, y, R) for (x, y) in holes_m])
    m = bpy.data.materials["Carbon_K04"]
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    for n in list(nodes):  # drop mat_carbon's procedural chain; the bake replaces it
        if n.name not in ("Principled BSDF", "Material Output"):
            nodes.remove(n)
    tc = nodes.new("ShaderNodeTexCoord")
    mp = nodes.new("ShaderNodeMapping")
    W = (meta["x1"] - meta["x0"]) / 1000.0
    H = (meta["y1"] - meta["y0"]) / 1000.0
    mp.inputs["Scale"].default_value = (1 / W, 1 / H, 1)
    mp.inputs["Location"].default_value = (-meta["x0"] / 1000.0 / W, -meta["y0"] / 1000.0 / H, 0)
    links.new(tc.outputs["Object"], mp.inputs["Vector"])
    vec = mp.outputs["Vector"]
    alb = _bimg(nodes, links, vec, "albedo.png", "sRGB")
    rgh = _bimg(nodes, links, vec, "rough.png", "Non-Color")
    hgt = _bimg(nodes, links, vec, "height16.png", "Non-Color", interp="Cubic")
    tan = _bimg(nodes, links, vec, "tan.png", "Non-Color")
    f0 = float(o.get("f0", 0.16))
    tint = nodes.new("ShaderNodeMixRGB")
    tint.blend_type = "MULTIPLY"
    tint.inputs["Fac"].default_value = 1.0
    tint.inputs["Color2"].default_value = (f0, f0, f0 * 1.02, 1)
    links.new(alb.outputs["Color"], tint.inputs["Color1"])
    links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])
    rs = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    rs.inputs[1].default_value = float(o.get("rough_s", 0.95))
    links.new(rgh.outputs["Color"], rs.inputs[0])
    links.new(rs.outputs[0], bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = float(o.get("metal", 0.85))
    bsdf.inputs["IOR"].default_value = 1.6
    bsdf.inputs["Specular IOR Level"].default_value = 0.6
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = float(o.get("bump", 0.2))
    bump.inputs["Distance"].default_value = 0.00025
    links.new(hgt.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    # anisotropy: tangent X, rotation from the baked double angle; strength fades where no direction dominates
    sp = nodes.new("ShaderNodeSeparateColor")
    links.new(tan.outputs["Color"], sp.inputs["Color"])
    cc = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD", **{})
    cc.inputs[1].default_value = 2.0
    cc.inputs[2].default_value = -1.0
    links.new(sp.outputs["Red"], cc.inputs[0])
    ss = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD")
    ss.inputs[1].default_value = 2.0
    ss.inputs[2].default_value = -1.0
    links.new(sp.outputs["Green"], ss.inputs[0])
    at = _n(nodes, "ShaderNodeMath", "ARCTAN2")
    links.new(ss.outputs[0], at.inputs[0])
    links.new(cc.outputs[0], at.inputs[1])
    rot = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    rot.inputs[1].default_value = 1.0 / (4 * math.pi)
    links.new(at.outputs[0], rot.inputs[0])
    links.new(rot.outputs[0], bsdf.inputs["Anisotropic Rotation"])
    cmb = nodes.new("ShaderNodeCombineXYZ")
    links.new(cc.outputs[0], cmb.inputs["X"])
    links.new(ss.outputs[0], cmb.inputs["Y"])
    ln = _n(nodes, "ShaderNodeVectorMath", "LENGTH")
    links.new(cmb.outputs[0], ln.inputs[0])
    an = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    an.use_clamp = True
    an.inputs[1].default_value = float(o.get("aniso", 0.9))
    links.new(ln.outputs["Value"], an.inputs[0])
    links.new(an.outputs[0], bsdf.inputs["Anisotropic"])
    tx = nodes.new("ShaderNodeCombineXYZ")
    tx.inputs["X"].default_value = 1.0
    links.new(tx.outputs[0], bsdf.inputs["Tangent"])
    # coat: weight 1, glossy, with a whisper of the weave printing through (mix of the smooth and the bumped normal)
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat IOR"].default_value = 1.5
    bsdf.inputs["Coat Roughness"].default_value = float(o.get("coat_rough", 0.035))
    geo = nodes.new("ShaderNodeNewGeometry")
    cm = nodes.new("ShaderNodeMix")
    cm.data_type = "VECTOR"
    cm.inputs["Factor"].default_value = float(o.get("print", 0.08))
    links.new(geo.outputs["Normal"], cm.inputs[4])
    links.new(bump.outputs["Normal"], cm.inputs[5])
    cn = _n(nodes, "ShaderNodeVectorMath", "NORMALIZE")
    links.new(cm.outputs[1], cn.inputs[0])
    links.new(cn.outputs[0], bsdf.inputs["Coat Normal"])
    return m


def bore_material(mat, o):
    """The bore walls: same baked carbon (on the wall it is the rim value, so the tows show as vertical streaks),
    moulded against a polished pin (lower roughness); fibres run DOWN the wall, so the tangent is circumferential."""
    bmat = mat.copy()
    bmat.name = "Carbon_K04_bore"
    nt = bmat.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    rs = b.inputs["Roughness"].links[0].from_node
    rs.inputs[1].default_value = float(o.get("bore_rough", 0.6))
    links.remove(b.inputs["Anisotropic Rotation"].links[0])
    b.inputs["Anisotropic Rotation"].default_value = 0.0
    links.remove(b.inputs["Anisotropic"].links[0])
    b.inputs["Anisotropic"].default_value = float(o.get("bore_aniso", 0.85))
    geo = nodes.new("ShaderNodeNewGeometry")
    cr = _n(nodes, "ShaderNodeVectorMath", "CROSS_PRODUCT")
    cr.inputs[0].default_value = (0, 0, 1)
    links.new(geo.outputs["Normal"], cr.inputs[1])
    nz = _n(nodes, "ShaderNodeVectorMath", "NORMALIZE")
    links.new(cr.outputs[0], nz.inputs[0])
    links.new(nz.outputs[0], b.inputs["Tangent"])
    tint = next(n for n in nodes if n.bl_idname == "ShaderNodeMixRGB")
    v = float(o.get("bore_f0", 0.13))
    tint.inputs["Color2"].default_value = (v, v, v * 1.02, 1)
    # the tows running down the wall show in the relief too: bump from the baked streak channel
    tan = next(n for n in nodes if n.bl_idname == "ShaderNodeTexImage" and "tan" in n.image.name)
    sp = nodes.new("ShaderNodeSeparateColor")
    links.new(tan.outputs["Color"], sp.inputs["Color"])
    bump = b.inputs["Normal"].links[0].from_node
    hsrc = bump.inputs["Height"].links[0].from_socket
    mx = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD")
    mx.inputs[1].default_value = float(o.get("bore_stria_bump", 0.6))
    links.new(sp.outputs["Blue"], mx.inputs[0])
    links.new(hsrc, mx.inputs[2])
    links.new(mx.outputs[0], bump.inputs["Height"])
    return bmat, sp.outputs["Blue"]


# ------------------------------------------------------------------ white Command (v4, canon 2026-10-22)
MACRO_BUMP = 0.08   # canon bump 0.30 is set for K10's 12 px tows; at K04's 4x magnification it reads as quilted pillows


def _gap_line(nodes, links, tile_vec):
    """v5: k04_tex2/gap16.png (shots/k04_gap.py) at weave-tile coordinates: 1 on the thin gap line between visible
    floats (about 0.045 mm wide), 0 elsewhere."""
    n_ = nodes.new("ShaderNodeTexImage")
    n_.image = bpy.data.images.load(os.path.join(kqpaths.asset("k04_tex2"), "gap16.png"), check_existing=True)
    n_.image.colorspace_settings.name = "Non-Color"
    n_.interpolation = "Linear"
    n_.extension = "REPEAT"
    links.new(tile_vec, n_.inputs["Vector"])
    return n_.outputs["Color"]


def _wopt(o, key):
    """A COMMAND_WHITE setting, overridable from the command line as --w_<key>."""
    import kq_canon
    return float(o.get("w_" + key, kq_canon.COMMAND_WHITE[key]))


def carbon_white_baked(holes_m, o):
    """kq_canon.mat_white (Command's white 3K twill) on K04's baked 2.6 mm maps (the same k04_tex2 twill, warped round
    every hole, so the tows still bend round each rim, cross the meniscus and run down the bore). The canon's recipe and
    numbers (COMMAND_WHITE): a dielectric white tow whose tone keeps the baked tow-to-tow variation and crevice shadow
    (alb_k), a tone step between the two fibre directions (dir_tone), fibre-bundle streaks along each tow (streak_*: tone,
    roughness and relief), an anisotropic fibre sheen rotated per tow (the twill flips inside a highlight), the tow
    relief as a bump, and a glass-clear coat (0.03) with a whisper of print-through.
    K04 specifics: the tow direction and the streaks are computed in the WARPED weave coordinates (k04_bake_warp.py:
    warpx16/warpy16, the same warp as the bake), so the streaks bend with the tows; the anisotropy keeps the bake's
    physical tangent; the relief bump is scaled for the macro (w_bump, default MACRO_BUMP)."""
    import json
    import k12_lib as K
    import kq_canon
    meta = json.load(open(os.path.join(BAKE, "bake.json")))
    wmeta = json.load(open(os.path.join(BAKE, "warp.json")))
    m = bpy.data.materials.new("CarbonW_K04")
    m.use_nodes = True
    nb = K.NB(m)
    nodes, links = nb.n, nb.l
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    b = nodes.new("ShaderNodeBsdfPrincipled")
    tc = nodes.new("ShaderNodeTexCoord")
    mp = nodes.new("ShaderNodeMapping")
    W = (meta["x1"] - meta["x0"]) / 1000.0
    H = (meta["y1"] - meta["y0"]) / 1000.0
    mp.inputs["Scale"].default_value = (1 / W, 1 / H, 1)
    mp.inputs["Location"].default_value = (-meta["x0"] / 1000.0 / W, -meta["y0"] / 1000.0 / H, 0)
    links.new(tc.outputs["Object"], mp.inputs["Vector"])
    vec = mp.outputs["Vector"]
    alb = _bimg(nodes, links, vec, "albedo.png", "sRGB")
    rgh = _bimg(nodes, links, vec, "rough.png", "Non-Color")
    hgt = _bimg(nodes, links, vec, "height16.png", "Non-Color", interp="Cubic")
    tan = _bimg(nodes, links, vec, "tan.png", "Non-Color")
    wxi = _bimg(nodes, links, vec, "warpx16.png", "Non-Color")
    wyi = _bimg(nodes, links, vec, "warpy16.png", "Non-Color")
    sp = nodes.new("ShaderNodeSeparateColor")
    links.new(tan.outputs["Color"], sp.inputs["Color"])
    sp.name = "tan_sep"
    # warped weave coordinates in metres (texture space of k04_tex2)
    wxm = nb.math("MULTIPLY_ADD", wxi.outputs["Color"], (wmeta["x"][1] - wmeta["x"][0]) / 1000.0, wmeta["x"][0] / 1000.0)
    wym = nb.math("MULTIPLY_ADD", wyi.outputs["Color"], (wmeta["y"][1] - wmeta["y"][0]) / 1000.0, wmeta["y"][0] / 1000.0)
    # tow direction exactly as the canon reads it: k04_tex2/rot16 at the warped coordinates (1: fibres along u)
    tile = 2.6 * 16 / 1000.0
    tv = nodes.new("ShaderNodeCombineXYZ")
    links.new(nb.math("DIVIDE", wxm, tile), tv.inputs["X"])
    links.new(nb.math("DIVIDE", wym, tile), tv.inputs["Y"])
    rot = nodes.new("ShaderNodeTexImage")
    rot.image = bpy.data.images.load(os.path.join(kqpaths.asset("k04_tex2"), "rot16.png"), check_existing=True)
    rot.image.colorspace_settings.name = "Non-Color"
    rot.interpolation = "Closest"
    rot.extension = "REPEAT"
    links.new(tv.outputs[0], rot.inputs["Vector"])
    along_u = nb.smooth(rot.outputs["Color"], 0.42, 0.58)
    # v5: the crisp gap line between visible floats (k04_gap.py), read at the same warped coordinates
    gap = _gap_line(nodes, links, tv.outputs[0])
    # fibre-bundle streaks along each tow (kq_canon.mat_white's 1D noise, in the warped coordinates)
    S, Sl = 1.0 / _wopt(o, "streak_w"), 1.0 / _wopt(o, "streak_len")

    def n1(a_, b_, z_):
        cv_ = nodes.new("ShaderNodeCombineXYZ")
        links.new(nb.math("MULTIPLY", a_, S), cv_.inputs[0])
        links.new(nb.math("MULTIPLY", b_, Sl), cv_.inputs[1])
        cv_.inputs[2].default_value = z_
        t_ = nodes.new("ShaderNodeTexNoise")
        t_.noise_dimensions = "3D"
        t_.inputs["Scale"].default_value = 1.0
        t_.inputs["Detail"].default_value = 2.0
        t_.inputs["Roughness"].default_value = 0.6
        links.new(cv_.outputs[0], t_.inputs["Vector"])
        return nb.smooth(t_.outputs["Fac"], 0.3, 0.7)

    streak = nb.math("SUBTRACT", nb.lerp(along_u, n1(wxm, wym, 7.3), n1(wym, wxm, 0.0)), 0.5)  # -0.5..0.5
    streak = nb.math("MULTIPLY", streak, _wopt(o, "streak"))
    k_ = _wopt(o, "alb_k")
    gl = nb.math("MULTIPLY", alb.outputs["Color"], 1.0)  # colour -> grey
    tone = nb.math("MULTIPLY_ADD", gl, k_ / 0.62, 1.0 - k_)
    tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", along_u, 0.5), _wopt(o, "dir_tone"), 1.0))
    tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", streak, _wopt(o, "streak_a"), 1.0))
    tone = nb.math("MINIMUM", tone, 1.12)
    tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", gap, -float(o.get("gap_a", 0.0)), 1.0))
    cc = nodes.new("ShaderNodeCombineColor")
    cc.name = "white_tint"
    for i, t_ in enumerate(kq_canon.COMMAND_WHITE["tint"]):
        links.new(nb.math("MULTIPLY", tone, float(t_) * float(o.get("w_gain", 1.0))), cc.inputs[i])
    links.new(cc.outputs[0], b.inputs["Base Color"])
    rr = nb.math("MULTIPLY", rgh.outputs["Color"], _wopt(o, "rough_s"))
    rr = nb.math("MULTIPLY", rr, nb.math("MULTIPLY_ADD", streak, _wopt(o, "streak_r"), 1.0))
    rr = nb.math("MULTIPLY_ADD", gap, float(o.get("gap_r", 0.0)), rr)   # resin-rich gap: a touch rougher
    links.new(rr, b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = _wopt(o, "metal")
    b.inputs["IOR"].default_value = _wopt(o, "ior")
    b.inputs["Specular IOR Level"].default_value = _wopt(o, "spec")
    # anisotropic fibre sheen: tangent X, rotated per tow by the baked physical double angle
    cc2 = nb.math("MULTIPLY_ADD", sp.outputs["Red"], 2.0, -1.0)
    ss2 = nb.math("MULTIPLY_ADD", sp.outputs["Green"], 2.0, -1.0)
    at = nb.math("ARCTAN2", ss2, cc2)
    links.new(nb.math("MULTIPLY", at, 1.0 / (4 * math.pi)), b.inputs["Anisotropic Rotation"])
    cmb = nodes.new("ShaderNodeCombineXYZ")
    links.new(cc2, cmb.inputs["X"])
    links.new(ss2, cmb.inputs["Y"])
    ln = nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    links.new(cmb.outputs[0], ln.inputs[0])
    links.new(nb.math("MULTIPLY", ln.outputs["Value"], _wopt(o, "aniso"), clamp=True), b.inputs["Anisotropic"])
    tx = nodes.new("ShaderNodeCombineXYZ")
    tx.inputs["X"].default_value = 1.0
    links.new(tx.outputs[0], b.inputs["Tangent"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = float(o.get("w_bump", MACRO_BUMP))
    bump.inputs["Distance"].default_value = 0.00025
    hh = nb.math("MULTIPLY_ADD", streak, _wopt(o, "streak_h"), hgt.outputs["Color"])
    hh = nb.math("MULTIPLY_ADD", gap, -float(o.get("gap_h", 0.0)), hh)
    links.new(hh, bump.inputs["Height"])
    links.new(bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat IOR"].default_value = 1.5
    b.inputs["Coat Roughness"].default_value = _wopt(o, "coat_rough")
    geo = nodes.new("ShaderNodeNewGeometry")
    cm = nodes.new("ShaderNodeMix")
    cm.data_type = "VECTOR"
    cm.inputs["Factor"].default_value = float(o.get("w_printmix", 0.05))
    links.new(geo.outputs["Normal"], cm.inputs[4])
    links.new(bump.outputs["Normal"], cm.inputs[5])
    cn = nodes.new("ShaderNodeVectorMath")
    cn.operation = "NORMALIZE"
    links.new(cm.outputs[1], cn.inputs[0])
    links.new(cn.outputs[0], b.inputs["Coat Normal"])
    links.new(b.outputs[0], out.inputs["Surface"])
    return m


def white_sleeve(name, o, bore=False):
    """The white twill folding over each hole's lip and lining its bore (canon: "every bore is lined by the carbon shell;
    the gloss lip carries the twill"). A cylindrical twill sleeve on k04_tex2 (the same 2.6 mm tows and maps the face
    bake reads): u = arc length round the hole (one full turn = one 41.6 mm weave tile, so it closes without a seam;
    the angle's cut lies on the near side, which the camera never sees), v = arc length along the profile from the face
    edge of the meniscus, over the lip and down the bore. So tows run round the lip and fold down the wall, and the lip
    reads as carbon, not as a polished ring. The canon mat_white recipe: tone (alb_k, dir_tone), fibre-bundle streaks,
    anisotropic fibre sheen (rot16 on the circumferential tangent), relief bump, clear coat. bore=True: the lining
    darkens with depth to a dark graphite (canon bore occlusion), inside the Principled, so the glow emission written
    later by bore_emission is not darkened with it. Returns (material, the 0..1 down-the-wall streak socket for the glow)."""
    import k12_lib as K
    import kq_canon
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nb = K.NB(m)
    nodes, links = nb.n, nb.l
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    b = nodes.new("ShaderNodeBsdfPrincipled")
    # sleeve coordinates (m)
    hc = nodes.new("ShaderNodeAttribute")
    hc.attribute_type = "GEOMETRY"
    hc.attribute_name = "hc"
    sa = nodes.new("ShaderNodeAttribute")
    sa.attribute_type = "GEOMETRY"
    sa.attribute_name = "s"
    geo = nodes.new("ShaderNodeNewGeometry")
    d = nodes.new("ShaderNodeVectorMath")
    d.operation = "SUBTRACT"
    links.new(geo.outputs["Position"], d.inputs[0])
    links.new(hc.outputs["Vector"], d.inputs[1])
    sd = nodes.new("ShaderNodeSeparateXYZ")
    links.new(d.outputs[0], sd.inputs[0])
    tile = 2.6 * 16 / 1000.0
    rc = tile / (2 * math.pi)
    th = nb.math("ARCTAN2", nb.math("MULTIPLY", sd.outputs["X"], -1.0), sd.outputs["Y"])  # cut on the near side (-y)
    u = nb.math("MULTIPLY", th, rc)
    v = nb.math("ADD", sa.outputs["Fac"], float(o.get("sleeve_v0", 0.0)))
    tv = nodes.new("ShaderNodeCombineXYZ")
    links.new(nb.math("DIVIDE", u, tile), tv.inputs["X"])
    links.new(nb.math("DIVIDE", v, tile), tv.inputs["Y"])
    T2 = kqpaths.asset("k04_tex2")

    def img(fn, cs, interp="Linear"):
        n_ = nodes.new("ShaderNodeTexImage")
        n_.image = bpy.data.images.load(os.path.join(T2, fn), check_existing=True)
        n_.image.colorspace_settings.name = cs
        n_.interpolation = interp
        n_.extension = "REPEAT"
        links.new(tv.outputs[0], n_.inputs["Vector"])
        return n_.outputs["Color"]

    alb = img("albedo.png", "sRGB")
    rgh = img("rough.png", "Non-Color")
    hgt = img("height16.png", "Non-Color", "Cubic")
    rot = img("rot16.png", "Non-Color")
    gap = _gap_line(nodes, links, tv.outputs[0])
    along_u = nb.smooth(rot, 0.42, 0.58)
    # fibre-bundle streaks (canon), seamless round the hole: the long axis of a round-running streak uses cos/sin
    S, Sl = 1.0 / _wopt(o, "streak_w"), 1.0 / _wopt(o, "streak_len")

    def noise(x_, y_, z_):
        cv_ = nodes.new("ShaderNodeCombineXYZ")
        for k_, c_ in enumerate((x_, y_, z_)):
            if isinstance(c_, (int, float)):
                cv_.inputs[k_].default_value = c_
            else:
                links.new(c_, cv_.inputs[k_])
        t_ = nodes.new("ShaderNodeTexNoise")
        t_.noise_dimensions = "3D"
        t_.inputs["Scale"].default_value = 1.0
        t_.inputs["Detail"].default_value = 2.0
        t_.inputs["Roughness"].default_value = 0.6
        links.new(cv_.outputs[0], t_.inputs["Vector"])
        return nb.smooth(t_.outputs["Fac"], 0.3, 0.7)

    n_down = noise(nb.math("MULTIPLY", u, S), nb.math("MULTIPLY", v, Sl), 7.3)            # fibres running down
    n_round = noise(nb.math("MULTIPLY", v, S), nb.math("MULTIPLY", nb.math("COSINE", th), rc * Sl),
                    nb.math("MULTIPLY", nb.math("SINE", th), rc * Sl))                       # fibres running round
    streak01 = nb.lerp(along_u, n_down, n_round)
    streak = nb.math("MULTIPLY", nb.math("SUBTRACT", streak01, 0.5),
                      _wopt(o, "streak") * float(o.get("bore_streak" if bore else "lip_streak", 1.0)))
    k_ = _wopt(o, "alb_k")
    tone = nb.math("MULTIPLY_ADD", nb.math("MULTIPLY", alb, 1.0), k_ / 0.62, 1.0 - k_)
    tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", along_u, 0.5), _wopt(o, "dir_tone"), 1.0))
    tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", streak, _wopt(o, "streak_a"), 1.0))
    tone = nb.math("MINIMUM", tone, 1.12)
    tone = nb.math("MULTIPLY", tone, nb.math("MULTIPLY_ADD", gap, -float(o.get("gap_a", 0.0)), 1.0))
    rr = nb.math("MULTIPLY", rgh, _wopt(o, "rough_s"))
    rr = nb.math("MULTIPLY", rr, nb.math("MULTIPLY_ADD", streak, _wopt(o, "streak_r"), 1.0))
    rr = nb.math("MULTIPLY_ADD", gap, float(o.get("gap_r", 0.0)), rr)
    occ = None
    if bore:
        _, _, z = nb.coords("Object")
        depth = nb.smooth(nb.math("ABSOLUTE", z), ZT - float(o.get("bore_lip", 0.0011)), ZT - float(o.get("bore_dark", 0.0035)))
        occ = nb.math("MULTIPLY", depth, float(o.get("bore_occ", 0.95)))
    cc = nodes.new("ShaderNodeCombineColor")
    col = float(o.get("bore_col", 0.02))
    bore_k = float(o.get("bore_k", 0.0))   # v5: > 0 keeps the twill in the dark lining (lining = tone x bore_k)
    for i, t_ in enumerate(kq_canon.COMMAND_WHITE["tint"]):
        ch = nb.math("MULTIPLY", tone, float(t_))
        if occ is not None:
            dark = nb.math("MULTIPLY", tone, bore_k * float(t_)) if bore_k > 0 else col * (1.0, 1.0, 1.06)[i]
            ch = nb.lerp(occ, ch, dark)
        links.new(ch, cc.inputs[i])
    links.new(cc.outputs[0], b.inputs["Base Color"])
    links.new(rr if occ is None else nb.lerp(occ, rr, 0.6), b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = _wopt(o, "metal")
    b.inputs["IOR"].default_value = _wopt(o, "ior")
    b.inputs["Specular IOR Level"].default_value = _wopt(o, "spec")
    # anisotropic sheen: tangent round the hole (the sleeve's u), rotated per tow as the canon (rot16 / 2 - 1/8)
    cr = nodes.new("ShaderNodeVectorMath")
    cr.operation = "CROSS_PRODUCT"
    cr.inputs[0].default_value = (0, 0, 1)
    links.new(geo.outputs["Normal"], cr.inputs[1])
    nz = nodes.new("ShaderNodeVectorMath")
    nz.operation = "NORMALIZE"
    links.new(cr.outputs[0], nz.inputs[0])
    links.new(nz.outputs[0], b.inputs["Tangent"])
    links.new(nb.math("MULTIPLY_ADD", rot, 0.5, -0.125), b.inputs["Anisotropic Rotation"])
    an = _wopt(o, "aniso")
    if occ is None:
        b.inputs["Anisotropic"].default_value = an
    else:
        links.new(nb.math("MULTIPLY", nb.math("SUBTRACT", 1.0, occ), an), b.inputs["Anisotropic"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = float(o.get("w_bump", MACRO_BUMP))
    bump.inputs["Distance"].default_value = 0.00025
    hh = nb.math("MULTIPLY_ADD", streak, _wopt(o, "streak_h"), hgt)
    hh = nb.math("MULTIPLY_ADD", gap, -float(o.get("gap_h", 0.0)), hh)
    links.new(hh, bump.inputs["Height"])
    links.new(bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Coat IOR"].default_value = 1.5
    b.inputs["Coat Roughness"].default_value = _wopt(o, "coat_rough")
    if occ is None:
        b.inputs["Coat Weight"].default_value = 1.0
    else:  # a deep bore never mirrors the studio
        links.new(nb.math("SUBTRACT", 1.0, nb.math("MULTIPLY", occ, float(o.get("bore_coat_occ", 0.85)))), b.inputs["Coat Weight"])
    cm = nodes.new("ShaderNodeMix")
    cm.data_type = "VECTOR"
    cm.inputs["Factor"].default_value = float(o.get("w_printmix", 0.05))
    links.new(geo.outputs["Normal"], cm.inputs[4])
    links.new(bump.outputs["Normal"], cm.inputs[5])
    cn = nodes.new("ShaderNodeVectorMath")
    cn.operation = "NORMALIZE"
    links.new(cm.outputs[1], cn.inputs[0])
    links.new(cn.outputs[0], b.inputs["Coat Normal"])
    links.new(b.outputs[0], out.inputs["Surface"])
    if str(o.get("glow_mod_src", "streak")) == "tone":
        # v5: the glow lights the woven lining: modulate it by the lining's own twill tone (floats, gap lines and the
        # warp/weft step), 0..1, not by down-running streaks (those read as a comb of flame tongues)
        return m, nb.smooth(tone, 0.55, 1.12)
    return m, n_down   # the glow is modulated by the tows running DOWN the wall only (vertical striations, as v3)


def bore_emission(mat, stria_sock, hero_xy, o, left_x=0.32):
    """Warm light rising up the bore from a source behind the face, written into the bore wall itself (camera rays
    only, so it cannot light the other walls into a cup). Grows exponentially with depth (e-folding lam) up to the
    deepest visible point d_ref, so only the deepest visible crescent glows. Colour runs from amber at the edge to an
    incandescent core at the deepest point. Modulated by the tows running down the wall (baked streaks + the weave
    height on the rim): vertical fibre striations, never a smooth gradient."""
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    lam = float(o.get("glow_lam", 0.0003))
    d_ref = float(o.get("glow_d", 0.0064))
    strength = float(o.get("glow", 3.0))
    others = float(o.get("glow_others", 0.3))
    left_f = float(o.get("glow_left", 0.0))
    core = tuple(float(v) for v in str(o.get("glow_core", "1.0,0.62,0.32")).split(","))
    edge = tuple(float(v) for v in str(o.get("glow_edge", "1.0,0.42,0.13")).split(","))
    tc = nodes.new("ShaderNodeTexCoord")
    sp = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sp.inputs["Vector"])
    t = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD")
    t.inputs[1].default_value = -1.0 / lam
    t.inputs[2].default_value = (ZT - d_ref) / lam
    links.new(sp.outputs["Z"], t.inputs[0])
    mn = _n(nodes, "ShaderNodeMath", "MINIMUM")
    mn.inputs[1].default_value = 0.0
    links.new(t.outputs[0], mn.inputs[0])
    ex = _n(nodes, "ShaderNodeMath", "EXPONENT")
    links.new(mn.outputs[0], ex.inputs[0])
    cm = nodes.new("ShaderNodeMixRGB")
    cm.inputs["Color1"].default_value = (*edge, 1)
    cm.inputs["Color2"].default_value = (*core, 1)
    cpw = _n(nodes, "ShaderNodeMath", "POWER")
    cpw.inputs[1].default_value = float(o.get("core_pow", 2.0))
    links.new(ex.outputs[0], cpw.inputs[0])
    links.new(cpw.outputs[0], cm.inputs["Fac"])
    d = _n(nodes, "ShaderNodeVectorMath", "SUBTRACT")
    d.inputs[1].default_value = (hero_xy[0], hero_xy[1], 0)
    links.new(tc.outputs["Object"], d.inputs[0])
    dm = _n(nodes, "ShaderNodeVectorMath", "MULTIPLY")
    dm.inputs[1].default_value = (1, 1, 0)
    links.new(d.outputs[0], dm.inputs[0])
    ln = _n(nodes, "ShaderNodeVectorMath", "LENGTH")
    links.new(dm.outputs[0], ln.inputs[0])
    hm = _n(nodes, "ShaderNodeMapRange")
    hm.inputs["From Min"].default_value = R * 1.3
    hm.inputs["From Max"].default_value = R * 1.8
    hm.inputs["To Min"].default_value = 1.0
    hm.inputs["To Max"].default_value = others
    links.new(ln.outputs["Value"], hm.inputs["Value"])
    # striations: baked streaks (contrast-stretched) times the rim's weave height
    st = _n(nodes, "ShaderNodeMapRange")
    st.inputs["From Min"].default_value = float(o.get("stria_f0", 0.2))
    st.inputs["From Max"].default_value = float(o.get("stria_f1", 0.8))
    st.inputs["To Min"].default_value = float(o.get("stria_min", 0.3))
    st.inputs["To Max"].default_value = float(o.get("stria_max", 1.35))
    links.new(stria_sock, st.inputs["Value"])
    m1 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(ex.outputs[0], m1.inputs[0])
    links.new(hm.outputs["Result"], m1.inputs[1])
    m2 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(m1.outputs[0], m2.inputs[0])
    links.new(st.outputs["Result"], m2.inputs[1])
    m3 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    m3.inputs[1].default_value = strength
    links.new(m2.outputs[0], m3.inputs[0])
    lp = nodes.new("ShaderNodeLightPath")
    g = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(m3.outputs[0], g.inputs[0])
    links.new(lp.outputs["Is Camera Ray"], g.inputs[1])
    sw = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Window"], sw.inputs["Vector"])
    lm = _n(nodes, "ShaderNodeMapRange")
    lm.interpolation_type = "SMOOTHSTEP"
    lm.inputs["From Min"].default_value = left_x - 0.08
    lm.inputs["From Max"].default_value = left_x + 0.08
    lm.inputs["To Min"].default_value = left_f
    lm.inputs["To Max"].default_value = 1.0
    links.new(sw.outputs["X"], lm.inputs["Value"])
    g2 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(g.outputs[0], g2.inputs[0])
    links.new(lm.outputs["Result"], g2.inputs[1])
    links.new(cm.outputs["Color"], b.inputs["Emission Color"])
    links.new(g2.outputs[0], b.inputs["Emission Strength"])


# ------------------------------------------------------------------ Pace (--feel pace, Release 2 feel toggle, 2026-10-23)
# The canon Pace v6 (kq_canon.mat_pace: black 12K spread tow, 8 mm plain-weave tapes, the checker only in the fibres'
# sheen direction, glass coat 0.03) on K04's geometry. Face: the canon node tree with its UV coordinates relinked to the
# WARPED weave coordinates (k04_bake_warp: warpx16 / warpy16, the same warp the 3K bake uses), so the tapes bend round
# every moulded hole; the tangent follows the warped u axis (perpendicular to grad(warp y), from two offset taps).
# Lips and bores: a 12K sleeve (u round the hole, 6 tapes per turn; v along the profile from the face edge of the
# meniscus), so the tapes fold over the lip and line the bore, which darkens with depth to a carbon lining (sealed core,
# never foam). The full variant's glow is a separate emission-only Principled added after the lining, so the depth
# occlusion never dims it. Lights: v3's black-carbon studio plus v5's lip line, a weave card for the fibre lobes and the
# v5 far-lip focus (PACE_DEFAULTS); P_CLAMP clamps indirect light (12K fireflies, as K10/K11 Pace).
PACE_DEFAULTS = dict(lipline=40.0, focus=1.8, fstop=64.0, p_clamp=4.0, g_cool=0.05, cool_tint="1,1,1", sheen=0.0,
                     p_wv=20.0, p_wv_el=68.0, p_wv_az=25.0, p_wv_w=0.8, p_wv_h=1.0, p_fib_w=0.00015, p_rs_w=0.0006)
# (previews out/p13/k04p_*: the weave card is placed so its lower edge crosses the face's mirror rays from the lower right:
# the 12K tapes read along that soft edge, bending round every hole, the top left stays black for the copy)


def is_pace(o):
    return str(o.get("feel", "command")) == "pace"


def _pace_opts(o):
    import kq_canon
    return {k[2:]: float(v) for k, v in o.items() if k.startswith("p_") and k[2:] in kq_canon.PACE}


def _pace_relink(m, uv_sock, tan_sock, canon_nodes):
    """Relink the canon tree's UV coordinates and UV tangent (only the nodes listed in canon_nodes) to our sockets."""
    links = m.node_tree.links
    for nd in canon_nodes:
        if nd.type == "TEX_COORD":
            for lk in list(nd.outputs["UV"].links):
                links.new(uv_sock, lk.to_socket)
        elif nd.type == "TANGENT":
            for lk in list(nd.outputs["Tangent"].links):
                links.new(tan_sock, lk.to_socket)


def pace_face(o):
    import json
    import k12_lib as K
    import kq_canon
    meta = json.load(open(os.path.join(BAKE, "bake.json")))
    wmeta = json.load(open(os.path.join(BAKE, "warp.json")))
    m = kq_canon.mat_pace("PaceK04", o=_pace_opts(o))
    canon_nodes = list(m.node_tree.nodes)
    nb = K.NB(m)
    nodes, links = nb.n, nb.l
    tc = nodes.new("ShaderNodeTexCoord")
    mp = nodes.new("ShaderNodeMapping")
    W = (meta["x1"] - meta["x0"]) / 1000.0
    H = (meta["y1"] - meta["y0"]) / 1000.0
    mp.inputs["Scale"].default_value = (1 / W, 1 / H, 1)
    mp.inputs["Location"].default_value = (-meta["x0"] / 1000.0 / W, -meta["y0"] / 1000.0 / H, 0)
    links.new(tc.outputs["Object"], mp.inputs["Vector"])
    vec = mp.outputs["Vector"]
    sx = (wmeta["x"][1] - wmeta["x"][0]) / 1000.0
    sy = (wmeta["y"][1] - wmeta["y"][0]) / 1000.0
    wxm = nb.math("MULTIPLY_ADD", _bimg(nodes, links, vec, "warpx16.png", "Non-Color").outputs["Color"], sx,
                  wmeta["x"][0] / 1000.0)
    wym = nb.math("MULTIPLY_ADD", _bimg(nodes, links, vec, "warpy16.png", "Non-Color").outputs["Color"], sy,
                  wmeta["y"][0] / 1000.0)
    uv = nodes.new("ShaderNodeCombineXYZ")
    links.new(wxm, uv.inputs[0])
    links.new(wym, uv.inputs[1])
    # tangent along the warped u axis: perpendicular to grad(warp y) (finite differences, h = 0.06 mm)
    h = float(o.get("p_grad_h", 0.06)) / 1000.0
    taps = []
    for dx, dy in ((h / W, 0.0), (0.0, h / H)):
        ad = nodes.new("ShaderNodeVectorMath")
        ad.operation = "ADD"
        ad.inputs[1].default_value = (dx, dy, 0.0)
        links.new(vec, ad.inputs[0])
        taps.append(nb.math("MULTIPLY_ADD", _bimg(nodes, links, ad.outputs[0], "warpy16.png", "Non-Color").outputs["Color"],
                            sy, wmeta["y"][0] / 1000.0))
    gx = nb.math("SUBTRACT", taps[0], wym)
    gy = nb.math("SUBTRACT", taps[1], wym)
    tv = nodes.new("ShaderNodeCombineXYZ")
    links.new(gy, tv.inputs[0])
    links.new(nb.math("MULTIPLY", gx, -1.0), tv.inputs[1])
    tn = nodes.new("ShaderNodeVectorMath")
    tn.operation = "NORMALIZE"
    links.new(tv.outputs[0], tn.inputs[0])
    _pace_relink(m, uv.outputs[0], tn.outputs[0], canon_nodes)
    return m


def pace_sleeve(name, o, bore=False):
    """12K sleeve over each lip and down its bore (see the block comment). Returns (material, glow modulation socket)."""
    import k12_lib as K
    import kq_canon
    m = kq_canon.mat_pace(name, o=_pace_opts(o))
    canon_nodes = list(m.node_tree.nodes)
    nb = K.NB(m)
    nodes, links = nb.n, nb.l
    hc = nodes.new("ShaderNodeAttribute")
    hc.attribute_type = "GEOMETRY"
    hc.attribute_name = "hc"
    sa = nodes.new("ShaderNodeAttribute")
    sa.attribute_type = "GEOMETRY"
    sa.attribute_name = "s"
    geo = nodes.new("ShaderNodeNewGeometry")
    d = nodes.new("ShaderNodeVectorMath")
    d.operation = "SUBTRACT"
    links.new(geo.outputs["Position"], d.inputs[0])
    links.new(hc.outputs["Vector"], d.inputs[1])
    sd = nodes.new("ShaderNodeSeparateXYZ")
    links.new(d.outputs[0], sd.inputs[0])
    turn = float(o.get("p_sleeve_turn", 48.0)) / 1000.0   # 6 tapes of 8 mm per turn (closes the checker)
    th = nb.math("ARCTAN2", nb.math("MULTIPLY", sd.outputs["X"], -1.0), sd.outputs["Y"])  # cut on the near side (-y)
    u = nb.math("MULTIPLY", th, turn / (2 * math.pi))
    v = nb.math("ADD", sa.outputs["Fac"], float(o.get("p_sleeve_v0", 0.0)) / 1000.0)
    uv = nodes.new("ShaderNodeCombineXYZ")
    links.new(u, uv.inputs[0])
    links.new(v, uv.inputs[1])
    cr = nodes.new("ShaderNodeVectorMath")
    cr.operation = "CROSS_PRODUCT"
    cr.inputs[0].default_value = (0, 0, 1)
    links.new(geo.outputs["Normal"], cr.inputs[1])
    nz = nodes.new("ShaderNodeVectorMath")
    nz.operation = "NORMALIZE"
    links.new(cr.outputs[0], nz.inputs[0])
    _pace_relink(m, uv.outputs[0], nz.outputs[0], canon_nodes)
    # glow modulation: fine fibre striations running down the wall (subtle; stria_* map them)
    cv = nodes.new("ShaderNodeCombineXYZ")
    links.new(nb.math("MULTIPLY", u, 1.0 / 0.0005), cv.inputs[0])
    links.new(nb.math("MULTIPLY", v, 1.0 / 0.02), cv.inputs[1])
    nn = nodes.new("ShaderNodeTexNoise")
    nn.inputs["Scale"].default_value = 1.0
    nn.inputs["Detail"].default_value = 2.0
    links.new(cv.outputs[0], nn.inputs["Vector"])
    stria = nn.outputs["Fac"]
    if not bore:
        return m, stria
    # the lining darkens with depth below the lip (K04 sees ~6 mm of bore): a carbon lining, never foam
    out = next(n_ for n_ in nodes if n_.type == "OUTPUT_MATERIAL")
    surf = out.inputs["Surface"].links[0].from_socket
    _, _, z = nb.coords("Object")
    occ = nb.math("MULTIPLY", nb.smooth(nb.math("ABSOLUTE", z), ZT - float(o.get("p_bore_lip", 0.0011)),
                                        ZT - float(o.get("p_bore_dark", 0.0040))), float(o.get("p_bore_occ", 0.92)))
    blk = nodes.new("ShaderNodeBsdfPrincipled")
    c_ = float(o.get("p_bore_col", 0.006))
    blk.inputs["Base Color"].default_value = (c_, c_, c_ * 1.06, 1)
    blk.inputs["Roughness"].default_value = 0.5
    blk.inputs["Specular IOR Level"].default_value = 0.25
    mx = nodes.new("ShaderNodeMixShader")
    links.new(occ, mx.inputs[0])
    links.new(surf, mx.inputs[1])
    links.new(blk.outputs[0], mx.inputs[2])
    # glow carrier for bore_emission (it writes into nodes["Principled BSDF"]): an emission-only Principled added
    # after the lining mix, so the depth occlusion never dims the glow
    for n_ in nodes:
        if n_.name == "Principled BSDF":
            n_.name = "PaceCanonBSDF"
    gp = nodes.new("ShaderNodeBsdfPrincipled")
    gp.name = "Principled BSDF"
    gp.inputs["Base Color"].default_value = (0, 0, 0, 1)
    gp.inputs["Specular IOR Level"].default_value = 0.0
    gp.inputs["Roughness"].default_value = 1.0
    gp.inputs["Emission Strength"].default_value = 0.0
    ad = nodes.new("ShaderNodeAddShader")
    links.new(mx.outputs[0], ad.inputs[0])
    links.new(gp.outputs[0], ad.inputs[1])
    links.new(ad.outputs[0], out.inputs["Surface"])
    return m, stria


# ------------------------------------------------------------------ lights
def panel(name, loc, size, strength, target, color=(1, 1, 1), roll=0.0, edge=(0.35, 0.75), fade=(0.0, 1.0), off=(0.0, 0.0),
          band=None, floor=0.0):
    """Emissive card (camera-invisible) with a linear falloff edge across its local X (edge = from, to in 0..1)
    times a soft taper along its local Y (fade). roll turns the card about its own axis (degrees)."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    studio.aim(ob, target)
    rm = ob.rotation_euler.to_matrix() @ Matrix.Rotation(math.radians(roll), 3, "Z")
    ob.rotation_euler = rm.to_euler()
    ob.location = Vector(loc) + rm @ Vector((off[0], off[1], 0))
    mt = bpy.data.materials.new(name + "Mat")
    mt.use_nodes = True
    nodes, links = mt.node_tree.nodes, mt.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    ex = _n(nodes, "ShaderNodeMapRange")
    ex.interpolation_type = "SMOOTHSTEP"
    ex.inputs["From Min"].default_value, ex.inputs["From Max"].default_value = edge
    ex.inputs["To Min"].default_value = floor
    links.new(sep.outputs["X"], ex.inputs["Value"])
    cy = _n(nodes, "ShaderNodeMath", "SUBTRACT")
    cy.inputs[1].default_value = 0.5
    links.new(sep.outputs["Y"], cy.inputs[0])
    ay = _n(nodes, "ShaderNodeMath", "ABSOLUTE")
    links.new(cy.outputs[0], ay.inputs[0])
    fy = _n(nodes, "ShaderNodeMapRange")
    fy.interpolation_type = "SMOOTHSTEP"
    fy.inputs["From Min"].default_value = 0.5 - 0.5 * fade[1]
    fy.inputs["From Max"].default_value = 0.5
    fy.inputs["To Min"].default_value = 1.0
    fy.inputs["To Max"].default_value = 0.0
    links.new(ay.outputs[0], fy.inputs["Value"])
    exo = ex.outputs["Result"]
    if band:
        # a stripe rather than a half-plane: falls again from band[0] to band[1] (with a residual floor band[2])
        bx = _n(nodes, "ShaderNodeMapRange")
        bx.interpolation_type = "SMOOTHSTEP"
        bx.inputs["From Min"].default_value, bx.inputs["From Max"].default_value = band[0], band[1]
        bx.inputs["To Min"].default_value = 1.0
        bx.inputs["To Max"].default_value = band[2]
        links.new(sep.outputs["X"], bx.inputs["Value"])
        bm_ = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        links.new(exo, bm_.inputs[0])
        links.new(bx.outputs["Result"], bm_.inputs[1])
        exo = bm_.outputs[0]
    mul = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(exo, mul.inputs[0])
    links.new(fy.outputs["Result"], mul.inputs[1])
    st = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    st.inputs[1].default_value = strength
    links.new(mul.outputs[0], st.inputs[0])
    links.new(st.outputs[0], em.inputs["Strength"])
    links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(mt)
    ob.visible_camera = False
    return ob


def emit_mat(name, color, strength):
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    nodes, links = mt.node_tree.nodes, mt.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    links.new(em.outputs[0], out.inputs["Surface"])
    return mt


def ring_arc(centre, radius, el0, el1, peak_az, half_w, strength, color, grad=0.25, name="lg_ring"):
    """Amber kicker as an arc band round the hero hole axis (camera-invisible, see-through, casts no shadow): a vertical
    cylinder section from elevation el0 to el1 (deg, seen from the hole), emitting only inside an azimuth window of
    +-half_w (deg, smooth) around peak_az (world deg), brightest at its lower edge (grad = relative top brightness).
    The concave inner lip mirrors it as a crescent that fades round the sides; the near lip never sees it."""
    h0 = radius * math.tan(math.radians(el0))
    h1 = radius * math.tan(math.radians(el1))
    bpy.ops.mesh.primitive_cylinder_add(vertices=384, radius=radius, depth=h1 - h0, end_fill_type="NOTHING",
                                        location=(centre[0], centre[1], centre[2] + (h0 + h1) / 2))
    ob = bpy.context.active_object
    ob.name = name
    me = ob.data
    for f in me.polygons:  # subdivide nothing; the emission pattern is procedural
        f.use_smooth = True
    mt = bpy.data.materials.new(name + "Mat")
    mt.use_nodes = True
    nodes, links = mt.node_tree.nodes, mt.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sep.inputs["Vector"])
    at = _n(nodes, "ShaderNodeMath", "ARCTAN2")
    links.new(sep.outputs["Y"], at.inputs[0])
    links.new(sep.outputs["X"], at.inputs[1])
    sb = _n(nodes, "ShaderNodeMath", "SUBTRACT")
    sb.inputs[1].default_value = math.radians(peak_az)
    links.new(at.outputs[0], sb.inputs[0])
    cs = _n(nodes, "ShaderNodeMath", "COSINE")
    links.new(sb.outputs[0], cs.inputs[0])
    wa = _n(nodes, "ShaderNodeMapRange")
    wa.interpolation_type = "SMOOTHSTEP"
    wa.inputs["From Min"].default_value = math.cos(math.radians(half_w))
    wa.inputs["From Max"].default_value = 1.0
    links.new(cs.outputs[0], wa.inputs["Value"])
    # vertical: bright at the bottom, falling to `grad` at the top, soft top and bottom edges
    hz = (h1 - h0) / 2
    we = _n(nodes, "ShaderNodeMapRange")
    we.inputs["From Min"].default_value = -hz
    we.inputs["From Max"].default_value = hz
    we.inputs["To Min"].default_value = 1.0
    we.inputs["To Max"].default_value = grad
    links.new(sep.outputs["Z"], we.inputs["Value"])
    az_ = _n(nodes, "ShaderNodeMath", "ABSOLUTE")
    links.new(sep.outputs["Z"], az_.inputs[0])
    soft = _n(nodes, "ShaderNodeMapRange")
    soft.interpolation_type = "SMOOTHSTEP"
    soft.inputs["From Min"].default_value = hz * 0.7
    soft.inputs["From Max"].default_value = hz
    soft.inputs["To Min"].default_value = 1.0
    soft.inputs["To Max"].default_value = 0.0
    links.new(az_.outputs[0], soft.inputs["Value"])
    m1 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(wa.outputs["Result"], m1.inputs[0])
    links.new(we.outputs["Result"], m1.inputs[1])
    m2 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(m1.outputs[0], m2.inputs[0])
    links.new(soft.outputs["Result"], m2.inputs[1])
    st = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    st.inputs[1].default_value = strength
    links.new(m2.outputs[0], st.inputs[0])
    links.new(st.outputs[0], em.inputs["Strength"])
    tr = nodes.new("ShaderNodeBsdfTransparent")
    ad = nodes.new("ShaderNodeAddShader")
    links.new(em.outputs[0], ad.inputs[0])
    links.new(tr.outputs[0], ad.inputs[1])
    links.new(ad.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(mt)
    ob.visible_camera = False
    ob.visible_shadow = False
    return ob


def pool_gobo(pool, face_point, o, pre="gobo"):
    """v5: soft flags on the white pool, as a gobo in frame coordinates. The light's Texture Coordinate 'Normal' is the
    emitted direction in the lamp's local space (verified); its planar projection (x/-z, y/-z) maps to frame
    coordinates of the face plane through a homography fitted here (face_point: frame -> face). Mask, in frame
    coordinates (x from the left, y down from the top):
      left flag  : 0 -> 1 from gobo_x0 to gobo_x1 (keeps the copy column dark, AD: luma <= ~90 up to x .42),
      top flag   : gobo_top -> 1 from y gobo_t0 to gobo_t1 (the defocused far field falls to mid-grey),
      bottom flag: 1 -> gobo_bot from y gobo_b0 to gobo_b1 (phones show the frame's edges with no band fade)."""
    import numpy as np
    bpy.context.view_layer.update()
    Mi = pool.matrix_world.inverted()
    A, bvec = [], []
    for fx in np.linspace(-0.3, 1.3, 9):
        for fy in np.linspace(-0.3, 1.3, 9):
            P, _ = face_point(1.0 - fy, 1.0 - fx)
            d = Mi @ P
            px, py = d.x / -d.z, d.y / -d.z
            A.append([px, py, 1, 0, 0, 0, -fx * px, -fx * py])
            bvec.append(fx)
            A.append([0, 0, 0, px, py, 1, -fy * px, -fy * py])
            bvec.append(fy)
    h, res, _, _ = np.linalg.lstsq(np.array(A), np.array(bvec), rcond=None)
    print("pool gobo homography residual", float(np.sqrt(res.mean())) if len(res) else 0.0)
    ld = pool.data
    ld.use_nodes = True
    nt = ld.node_tree
    nodes, links = nt.nodes, nt.links
    em = nodes["Emission"]
    tc = nodes.new("ShaderNodeTexCoord")
    sp = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Normal"], sp.inputs[0])

    def m(op, a, b_=None, c_=None):
        n_ = nodes.new("ShaderNodeMath")
        n_.operation = op
        for k_, v_ in enumerate((a, b_, c_)):
            if v_ is None:
                continue
            if isinstance(v_, (int, float)):
                n_.inputs[k_].default_value = float(v_)
            else:
                links.new(v_, n_.inputs[k_])
        return n_.outputs[0]

    nz = m("MULTIPLY", sp.outputs["Z"], -1.0)
    px = m("DIVIDE", sp.outputs["X"], nz)
    py = m("DIVIDE", sp.outputs["Y"], nz)

    def lin(a_, b_, c_):
        return m("ADD", m("MULTIPLY_ADD", px, float(a_), m("MULTIPLY", py, float(b_))), float(c_))

    den = lin(h[6], h[7], 1.0)
    FX = m("DIVIDE", lin(h[0], h[1], h[2]), den)
    FY = m("DIVIDE", lin(h[3], h[4], h[5]), den)

    def ramp(v_, e0, e1, lo, hi):
        r_ = nodes.new("ShaderNodeMapRange")
        r_.interpolation_type = "SMOOTHSTEP"
        r_.inputs["From Min"].default_value = e0
        r_.inputs["From Max"].default_value = e1
        r_.inputs["To Min"].default_value = lo
        r_.inputs["To Max"].default_value = hi
        links.new(v_, r_.inputs["Value"])
        return r_.outputs["Result"]

    g_ = lambda k_, d_: float(o.get(pre + "_" + k_, d_))  # noqa: E731
    mx = ramp(FX, g_("x0", -1.0), g_("x1", -0.5), g_("xlo", 0.0), g_("xhi", 1.0))
    mt = ramp(FY, g_("t0", -1.0), g_("t1", -0.5), g_("top", 1.0), 1.0)
    mb = ramp(FY, g_("b0", 1.5), g_("b1", 2.0), 1.0, g_("bot", 1.0))
    links.new(m("MULTIPLY", m("MULTIPLY", mx, mt), mb), em.inputs["Strength"])


# ------------------------------------------------------------------ compositing
GROUPS =("key", "sheen", "fill", "ring", "glow", "pool")  # "pool" is used only by dev renders (--pool_lg pool)


def build_comp(sc, src, o, out_stem, variants, crop=False):
    """src: dict group -> socket (noisy light-group pass) plus 'albedo', 'normal'. Denoise each group (OIDN guided by
    albedo + normal), apply gains, sum into the variants, apply the left flag burn, write PNGs via File Output."""
    tr = sc.node_tree
    gains = {g: float(o.get("g_" + g, 1.0)) for g in GROUPS}
    den = {}
    for g in GROUPS:
        if g not in src:
            continue
        dn = tr.nodes.new("CompositorNodeDenoise")
        dn.prefilter = "ACCURATE"
        dn.use_hdr = True
        tr.links.new(src[g], dn.inputs["Image"])
        tr.links.new(src["normal"], dn.inputs["Normal"])
        tr.links.new(src["albedo"], dn.inputs["Albedo"])
        mu = tr.nodes.new("CompositorNodeMixRGB")
        mu.blend_type = "MULTIPLY"
        mu.inputs["Fac"].default_value = 1.0
        mu.inputs[2].default_value = (gains[g], gains[g], gains[g], 1)
        tr.links.new(dn.outputs["Image"], mu.inputs[1])
        den[g] = mu.outputs["Image"]

    def add(a, b):
        n = tr.nodes.new("CompositorNodeMixRGB")
        n.blend_type = "ADD"
        n.inputs["Fac"].default_value = 1.0
        tr.links.new(a, n.inputs[1])
        tr.links.new(b, n.inputs[2])
        return n.outputs["Image"]

    base = add(add(den["key"], den["sheen"]), den["fill"])
    if "pool" in den:
        base = add(base, den["pool"])
    full = add(add(base, den["ring"]), den["glow"])
    # base: a faint cool bounce in the deepest crescent, 6 % of the glow, so the black bore still reads as a hole
    bw = tr.nodes.new("CompositorNodeRGBToBW")
    tr.links.new(den["glow"], bw.inputs[0])
    cool = tr.nodes.new("CompositorNodeMixRGB")
    cool.blend_type = "MULTIPLY"
    cool.inputs["Fac"].default_value = 1.0
    gc = float(o.get("g_cool", 0.08))
    ct = tuple(float(v) for v in str(o.get("cool_tint", "0.62,0.78,1.0")).split(","))   # v5 white: neutral
    cool.inputs[2].default_value = (ct[0] * gc, ct[1] * gc, ct[2] * gc, 1)
    tr.links.new(bw.outputs[0], cool.inputs[1])
    base = add(base, cool.outputs["Image"])
    outs = {"full": full, "base": base}
    burn = float(o.get("burn", 0.68))
    if burn < 1.0 and not crop:
        box = tr.nodes.new("CompositorNodeBoxMask")
        box.x = 0.0
        box.y = 0.5
        box.mask_width = 2 * float(o.get("burn_x", 0.34))
        box.mask_height = 3.0
        bl = tr.nodes.new("CompositorNodeBlur")
        bl.filter_type = "GAUSS"
        bl.use_relative = True
        bl.aspect_correction = "NONE"
        bl.factor_x = float(o.get("burn_soft", 0.16)) * 100
        bl.factor_y = 0.0
        tr.links.new(box.outputs["Mask"], bl.inputs["Image"])
        for k in list(outs):
            mx = tr.nodes.new("CompositorNodeMixRGB")
            mx.blend_type = "MULTIPLY"
            mx.inputs[2].default_value = (burn, burn, burn, 1)
            tr.links.new(bl.outputs["Image"], mx.inputs["Fac"])
            tr.links.new(outs[k], mx.inputs[1])
            outs[k] = mx.outputs["Image"]
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = os.path.dirname(out_stem)
    fo.format.file_format = "PNG"
    fo.format.color_mode = "RGB"
    fo.format.color_depth = "16"
    fo.file_slots.clear()
    written = []
    for v in variants:
        name = os.path.basename(out_stem) + ("-" + v if len(variants) > 1 else "")
        fo.file_slots.new(name)
        tr.links.new(outs[v], fo.inputs[name])
        written.append(name)
    comp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(outs[variants[0]], comp.inputs["Image"])
    return written


def finish_outputs(out_stem, written):
    d = os.path.dirname(out_stem)
    paths = []
    for name in written:
        cands = [f for f in os.listdir(d) if f.startswith(name) and f.endswith(".png") and f[len(name):-4].isdigit()]
        cands.sort(key=lambda f: os.path.getmtime(os.path.join(d, f)))
        if cands:
            dst = os.path.join(d, name + ".png")
            os.replace(os.path.join(d, cands[-1]), dst)
            paths.append(dst)
    return paths


def comp_from_exr(o):
    """Recomposite the variants from an earlier render's raw light-group passes (no path tracing)."""
    exr = o["comp"]
    if not os.path.isabs(exr):
        exr = os.path.join(studio.OUT, exr)
    sc = studio.reset()
    img = bpy.data.images.load(exr)
    sc.render.resolution_x, sc.render.resolution_y = img.size[0] or o["w"], img.size[1] or o["h"]
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    im = tr.nodes.new("CompositorNodeImage")
    im.image = img
    im.layer = "ViewLayer"
    im.image = None
    im.image = img
    src = {g: im.outputs["Combined_" + g] for g in GROUPS if ("Combined_" + g) in im.outputs}
    src["albedo"] = im.outputs["Denoising Albedo"]
    src["normal"] = im.outputs["Denoising Normal"]
    variants = ["full", "base"] if o["variant"] == "both" else [o["variant"]]
    out_stem = out_path(o["out"])[:-4]
    w, h = img.size[:]
    sc.render.resolution_x, sc.render.resolution_y = w, h
    written = build_comp(sc, src, o, out_stem, variants, crop=bool(o.get("crop")))
    sc.render.filepath = os.path.join(studio.OUT, "k45", "_comp_scratch.png")
    bpy.ops.render.render(write_still=True)
    print("composited", finish_outputs(out_stem, written))


# ------------------------------------------------------------------ shot
# v4 white Command: light settings that differ from v3's black-carbon studio (any --flag still overrides them)
WHITE_DEFAULTS = dict(key=0.4, sheen=13.0, sheen_diff=0.0, pool=30.0, pool_deg=10.0, pool_x=1.10, pool_y=0.5,
                      pool_az=172.0, pool_r=0.010, ring_diff=0.0, ring_wash=0.2,
                      bore_dark=0.0024, bore_occ=1.0, bore_col=0.012, bore_coat_occ=0.95)
# v5 (AD stage 3a, 2026-10-22): the critique's fixes, on top of v4's white defaults (each still overridable by --flag;
# --v5 0 gives v4's look back)
V5_DEFAULTS = dict(
    # weave at macro scale: crisp 0.045 mm gap line at 0.78x tone (k04_gap.py), stronger warp/weft step and bundles
    gap_a=0.22, gap_r=0.1, w_dir_tone=0.26, w_streak_a=0.14,
    # lips: the meniscus straddles a row boundary (staggered short tiles, not 8 long ones), stronger streaks
    sleeve_v0=0.0013, lip_streak=1.6,
    # bore: white ends at the meniscus's inner tangent, graphite within 0.6 mm; the lining keeps its twill (tone x k)
    bore_dark=0.0017, bore_k=0.012, bore_streak=0.4,
    # glow: lights the woven lining (28 % tone modulation, no flame tongues), feathered over 0.6 mm; base bounce off
    glow_mod_src="tone", stria_f0=0.0, stria_f1=1.0, stria_min=0.72, stria_max=1.0, glow_lam=0.0006, g_cool=0.0,
    cool_tint="1,1,1",
    # ring: a clear amber crescent in the hero lip's lacquer (glossy arc), less diffuse wash
    ring=340.0, ring_el0=4.0, ring_el1=28.0, ring_wash=0.08,
    # pool: diffuse only (no pinpoint flashes on the lips), gobo flags in frame coordinates (copy column dark to x .42,
    # far field mid-grey at the top, near field falling off at the bottom for phones); tiny radius for a crisp gobo
    pool=28.0, pool_gloss=0.0, pool_r=0.0005, gobo=1.0, gobo_x0=0.30, gobo_x1=0.58,
    gobo_t0=0.0, gobo_t1=0.38, gobo_top=0.12, gobo_b0=0.55, gobo_b1=0.95, gobo_bot=0.0,
    # shade fill: white in shadow stays white (canon note 8), gobo'd to the left, faded top and bottom
    shade=1.2, shg_x0=0.30, shg_x1=0.46, shg_xlo=1.0, shg_xhi=0.0, shg_t0=0.0, shg_t1=0.35, shg_top=0.3,
    shg_b0=0.6, shg_b1=0.95, shg_bot=0.2,
    # reflection-only strips: lg_lipline draws the long thin line along every far lip edge; the sheen band is shorter
    # and stronger, centred in the in-focus band at the right (no bright smear at the top of the frame)
    lipline=150.0, sheen=22.0, sheen_u=0.55, sheen_v=0.12, sheen_len=0.08,
    # focus on the far lip (the subject: where the twill folds into the bore), stopped down a little
    focus=1.8, fstop=64.0)
# key: the grazing strip from the top-left at 8 deg, now a quiet relief light (white fibre needs little of it).
# sheen: the same 6 mm strip band, glossy only, so on white it is the fibre flip inside a soft diagonal sheen, not a lit
#   stripe. pool: the white key (canon lighting note 8), a 10 deg soft spot from behind the camera's right shoulder,
#   centred off the right edge so its falloff sweeps across the frame (pool_x / pool_y are frame coordinates).
# ring: glossy only (an amber reflection in the hero lip's lacquer, never an amber-painted lip).
# bore_dark: the lining darkens over the ~6 mm of bore the camera sees (the canon's 12 mm is for face-on views).


def main():
    o = parse_args()
    if is_pace(o):
        o["white"] = 0
        for k_, v_ in PACE_DEFAULTS.items():
            o.setdefault(k_, v_)
    if float(o.get("white", 1.0)) > 0:
        if float(o.get("v5", 1.0)) > 0:
            for k_, v_ in V5_DEFAULTS.items():
                o.setdefault(k_, v_)
        for k_, v_ in WHITE_DEFAULTS.items():
            o.setdefault(k_, v_)
    if o.get("comp"):
        return comp_from_exr(o)
    t0 = time.time()
    variant = o["variant"]
    variants = ["full", "base"] if variant == "both" else [variant]
    yaw = float(o.get("yaw", 0.0))
    fw = float(o.get("fw", 40.5)) / 1000.0
    fstop = float(o.get("fstop", 48.0))

    studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc = bpy.context.scene
    sc.cycles.max_bounces = 6
    sc.cycles.glossy_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.transmission_bounces = 2
    sc.cycles.transparent_max_bounces = 6
    sc.cycles.use_denoising = False
    sc.cycles.adaptive_threshold = float(o.get("noise", 0.01))
    sc.cycles.seed = 7
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    groups = [g for g in GROUPS if g != "pool" or str(o.get("pool_lg", "key")) == "pool"]
    for g in groups:
        vl.lightgroups.add(name=g)

    c = (HERO[0] * U, HERO[1] * U)
    patch, lips, bores, hs = build_patch(c)
    near = [(x, y) for (x, y) in hs if math.hypot(x - c[0], y - c[1]) < 0.045]
    white = float(o.get("white", 1.0)) > 0   # v4: white Command (canon); --white 0 gives v3's graphite carbon
    if is_pace(o):
        if float(o.get("p_clamp", 0.0)) > 0:
            sc.cycles.sample_clamp_indirect = float(o["p_clamp"])
        mat = pace_face(o)
        lmat, _ = pace_sleeve("PaceK04_lip", o)
        bmat, stria = pace_sleeve("PaceK04_bore", o, bore=True)
    elif white:
        mat = carbon_white_baked(near, o)
        lmat, _ = white_sleeve("CarbonW_K04_lip", o)
        bmat, stria = white_sleeve("CarbonW_K04_bore", o, bore=True)
    else:
        mat = carbon_baked(near, o)
        lmat = mat
        bmat, stria = bore_material(mat, o)
    patch.data.materials.append(mat)
    for lp in lips:
        lp.data.materials.clear()
        lp.data.materials.append(lmat)
    bores.data.materials.append(bmat)

    C = Vector((c[0], c[1], ZT))
    a = math.radians(90 + yaw)
    fwd = Vector((math.cos(a), math.sin(a), 0))
    rt = fwd.cross(Vector((0, 0, 1))).normalized()
    up = Vector((0, 0, 1))
    el = math.radians(25)
    dist = 0.22
    lens = 36.0 * dist / fw
    cam_loc = C - fwd * dist * math.cos(el) + up * dist * math.sin(el)
    cam = studio.camera(tuple(cam_loc), tuple(C), lens=lens, shift=(-0.12, 0.0))
    cd = cam.data
    cd.dof.use_dof = fstop > 0
    cd.dof.aperture_fstop = max(fstop, 1.0)
    focus = float(o.get("focus", 0.35))  # 0 = near rim, 1 = hole centre
    fpt = C - fwd * (R + FO * 0.5) * (1 - focus)
    view = (C - cam_loc).normalized()
    cd.dof.focus_distance = (fpt - cam_loc).dot(view)
    cd.clip_start = 0.01

    def dirv(az_from_fwd, elev_deg):
        az = math.radians(az_from_fwd)
        e = math.radians(elev_deg)
        hdir = fwd * math.cos(az) + rt * math.sin(az)
        return (hdir * math.cos(e) + up * math.sin(e)).normalized()

    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    flag_x = float(o.get("flag_x", 0.30))
    left_lips, hero_lip = [], None
    for lp in lips:
        bb = [lp.matrix_world @ Vector(v) for v in lp.bound_box]
        ctr = sum(bb, Vector((0, 0, 0))) / 8
        if (Vector((ctr.x, ctr.y)) - Vector(c)).length < 0.002:
            hero_lip = lp
        elif world_to_camera_view(sc, cam, ctr).x < flag_x:
            left_lips.append(lp)

    # bores carry the glow emission: their own light group
    bores.lightgroup = "glow"
    bore_emission(bmat, stria, c, o, left_x=float(o.get("glow_left_x", 0.32)))

    # lg_sheen: a long strip softbox whose clearcoat reflection crosses the upper right as one crisp diagonal line; the
    # anisotropic fibres under the coat catch it over a broad band around that line (tows flash, grooves stay dark)
    import mathutils.geometry as mg

    def face_point(u, v):
        """World point on the face seen at frame coordinates (u, v) (0..1, v down)."""
        vf = cam.data.view_frame(scene=sc)
        tl, bl_, br, trr = vf[1], vf[2], vf[3], vf[0]
        p_local = (tl.lerp(trr, u)).lerp(bl_.lerp(br, u), v)
        d = (cam.matrix_world.to_3x3() @ p_local).normalized()
        o_ = cam.matrix_world.translation
        t_ = (ZT - o_.z) / d.z
        return o_ + d * t_, d

    su, sv = float(o.get("sheen_u", 0.84)), float(o.get("sheen_v", 0.26))
    P, dv = face_point(su, sv)
    rdir = (dv - 2 * dv.dot(up) * up).normalized()
    sheen = panel("lg_sheen", tuple(P + rdir * float(o.get("sheen_d", 0.6))), (float(o.get("sheen_w", 0.006)), float(o.get("sheen_len", 0.7))),
                  float(o.get("sheen", 26.0)), tuple(P), color=(0.92, 0.95, 1.0), roll=float(o.get("roll", 45.0)),
                  edge=(-1.0, -0.5), fade=(0, float(o.get("sheen_fade", 1.0))))
    sheen.lightgroup = "sheen"
    if float(o.get("sheen_diff", 1.0)) <= 0:
        sheen.visible_diffuse = False   # white: glossy only (a lacquer line and the fibre flip, never a lit stripe)
    # lg_fill: a broad dim card overhead and behind the camera, in the plane of the tows that run ACROSS the frame:
    # those tows flash softly, the receding ones stay dark (the 3K checker at 2-3x, not on/off)
    fill = panel("lg_fill", tuple(C + dirv(float(o.get("fill_az", 180.0)), float(o.get("fill_el", 62.0))) * 0.5),
                 (float(o.get("fill_w", 0.35)), float(o.get("fill_h", 0.5))), float(o.get("fill", 0.38)), tuple(C),
                 color=(0.93, 0.95, 1.0), roll=float(o.get("fill_roll", 0.0)), edge=(-1.0, -0.5), fade=(0, 1.0))
    fill.lightgroup = "fill"
    # lg_key: hard grazing strip from the top-left at 8 deg (text-zone lips excluded: no glints by the copy)
    kd = dirv(float(o.get("key_az", -45.0)), float(o.get("key_el", 8.0)))
    key = studio.area_light("lg_key", tuple(C + kd * 0.5), float(o.get("key_len", 0.30)), float(o.get("key", 3.0)),
                            color=(1.0, 0.98, 0.95), size_y=0.006, target=tuple(C))
    key.lightgroup = "key"
    flagged = [key, sheen, fill]
    if is_pace(o) and float(o.get("p_wv", 0.0)) > 0:
        # Pace: the weave card (as K03 / K11 Pace): a large soft card above the face's mirror direction, seen by the
        # 12K fibre lobes (alternate tapes light up, the checker reads across the face) and barely by the glass coat;
        # in the fill group (base and full)
        import k03_lib as L3
        wv = L3.card("lg_pweave", tuple(C + dirv(float(o.get("p_wv_az", 0.0)), float(o.get("p_wv_el", 55.0)))
                                        * float(o.get("p_wv_d", 0.5))),
                     (float(o.get("p_wv_w", 1.0)), float(o.get("p_wv_h", 1.0))), float(o["p_wv"]), tuple(C),
                     color=(0.95, 0.97, 1.0), falloff="soft")
        wv.lightgroup = "fill"
        wv.visible_shadow = False
        flagged.append(wv)
    if white and float(o.get("pool", 0.0)) > 0:
        # white Command needs real diffuse light (canon lighting note 8): a soft spot pool from behind the camera's
        # right shoulder, in the key group. It lights the white face with a falloff toward the text zone on the left
        # and the far inner lip of every hole (the white lip crescent); its mirror image never lands on the flat face.
        # face_point's (u, v) are (up from the bottom, in from the RIGHT) (view_frame corner order); pool_x / pool_y
        # are plain frame coordinates (x from the left, y down from the top)
        tgt, _ = face_point(1.0 - float(o.get("pool_y", 0.5)), 1.0 - float(o.get("pool_x", 0.82)))
        pdir = dirv(float(o.get("pool_az", 158.0)), float(o.get("pool_el", 46.0)))
        pool = studio.spot_light("lg_pool", tuple(tgt + pdir * float(o.get("pool_d", 0.35))), float(o.get("pool", 20.0)),
                                 float(o.get("pool_deg", 10.0)), blend=1.0, color=(1.0, 0.985, 0.97), target=tuple(tgt),
                                 radius=float(o.get("pool_r", 0.012)))
        pool.lightgroup = str(o.get("pool_lg", "key"))
        if float(o.get("pool_gloss", 1.0)) <= 0:
            # v5: diffuse only. Its 10 deg disc mirrored in the lip lacquer read as a pinpoint flash (glossy ceramic);
            # the lips' highlights are the reflection-only strips' job (lg_lipline, lg_sheen)
            pool.visible_glossy = False
            if float(o.get("pool_face_gloss", 0.0)) > 0:
                # ...but the flat face keeps the pool's glossy part: the anisotropic fibre sheen under the coat is what
                # flips warp against weft inside the lit area (the coat never mirrors the pool on the flat face). A
                # glossy-only twin of the pool, light-linked to the face patch alone, so no lip sees it.
                pg = studio.spot_light("lg_pool_g", tuple(pool.location), float(o.get("pool", 20.0)) * float(o["pool_face_gloss"]),
                                       float(o.get("pool_deg", 10.0)), blend=1.0, color=(1.0, 0.985, 0.97),
                                       target=tuple(tgt), radius=pool.data.shadow_soft_size)
                pg.visible_diffuse = False
                pg.lightgroup = pool.lightgroup
                pgc = bpy.data.collections.new("pool_gloss_receivers")
                pgc.objects.link(patch)
                pg.light_linking.receiver_collection = pgc
                if float(o.get("gobo", 0.0)) > 0:
                    pool_gobo(pg, face_point, o)
        if float(o.get("gobo", 0.0)) > 0:
            pool_gobo(pool, face_point, o)
        if float(o.get("pool_flag", 0.0)) > 0:
            flagged.append(pool)
    if white and float(o.get("shade", 0.0)) > 0:
        # v5: lg_shade, a soft, weak diffuse fill on the shade side (canon lighting note 8: white in shadow stays
        # white, not dirty grey): a wide spot from behind the camera's left shoulder, gobo'd to the left of the frame
        # (off before the hero hole, faded top and bottom), diffuse only, in the fill group
        stgt, _ = face_point(1.0 - float(o.get("shade_y", 0.5)), 1.0 - float(o.get("shade_x", 0.15)))
        sdir = dirv(float(o.get("shade_az", -160.0)), float(o.get("shade_el", 40.0)))
        shade = studio.spot_light("lg_shade", tuple(stgt + sdir * float(o.get("shade_d", 0.35))), float(o["shade"]),
                                  float(o.get("shade_deg", 40.0)), blend=1.0, color=(1.0, 0.99, 0.98), target=tuple(stgt),
                                  radius=0.0005)
        shade.visible_glossy = False
        shade.lightgroup = "fill"
        pool_gobo(shade, face_point, o, pre="shg")
    if left_lips:
        # the flag: lips in the text zone see none of the white lights (no curved glints beside the copy)
        kc = bpy.data.collections.new("key_flagged")
        for lp in left_lips:
            kc.objects.link(lp)
        for item in kc.collection_objects:
            item.light_linking.link_state = "EXCLUDE"
        for lt in flagged:
            lt.light_linking.receiver_collection = kc
    if float(o.get("lipline", 0.0)) > 0:
        # v5: lg_lipline, the reflection-only strip that draws one long, thin, continuous highlight along the far lip
        # edge of every hole (outside the text zone): a thin arc band far beyond the holes, high enough (lipline_el)
        # that the flat face never mirrors it (the face mirrors 22-28 deg), so only the curved lips pick it up, where
        # the meniscus turns from the face (t of a few degrees). Glossy only, in the sheen group (base and full).
        fwd_az = math.degrees(math.atan2(fwd.y, fwd.x)) + float(o.get("lipline_az", 0.0))
        el_c, el_w = float(o.get("lipline_el", 35.0)), float(o.get("lipline_w", 4.0))
        ll = ring_arc((C.x, C.y, C.z), float(o.get("lipline_r", 0.30)), el_c - el_w / 2, el_c + el_w / 2, fwd_az,
                      float(o.get("lipline_hw", 70.0)), float(o["lipline"]), (0.95, 0.97, 1.0), grad=1.0,
                      name="lg_lipline")
        ll.visible_diffuse = False
        ll.lightgroup = "sheen"
        llc = bpy.data.collections.new("lipline_receivers")
        for lp in lips:
            if lp not in left_lips:
                llc.objects.link(lp)
        ll.light_linking.receiver_collection = llc
    # lg_ring: amber arc kicker, hero lip only
    warm = (1.0, 0.52, 0.22)
    peak = math.degrees(math.atan2(dirv(float(o.get("ring_az", -150.0)), 0).y, dirv(float(o.get("ring_az", -150.0)), 0).x))
    rk = ring_arc((C.x, C.y, C.z), float(o.get("ring_r", 0.16)), float(o.get("ring_el0", 2.0)), float(o.get("ring_el1", 34.0)),
                  peak, float(o.get("ring_hw", 105.0)), float(o.get("ring", 40.0)), warm, grad=float(o.get("ring_grad", 0.2)))
    rk.lightgroup = "ring"
    if float(o.get("ring_diff", 1.0)) <= 0:
        rk.visible_diffuse = False   # glossy only: the amber crescent stays a reflection on the far lip
    rc = bpy.data.collections.new("ring_receivers")
    rc.objects.link(hero_lip)
    rk.light_linking.receiver_collection = rc
    if float(o.get("ring_wash", 0.0)) > 0:
        # white: a faint warm wash on the hero's inner lip as well (the light rising through the bore catching the white
        # lacquer), from the same arc, diffuse only, same group; the crisp amber reflection stays the glossy arc's
        rw = ring_arc((C.x, C.y, C.z), float(o.get("ring_r", 0.16)) * 1.01, float(o.get("ring_el0", 2.0)), float(o.get("ring_el1", 34.0)),
                      peak, float(o.get("ring_hw", 105.0)), float(o.get("ring", 40.0)) * float(o["ring_wash"]), warm,
                      grad=float(o.get("ring_grad", 0.2)), name="lg_ring_wash")
        rw.visible_glossy = False
        rw.lightgroup = "ring"
        rw.light_linking.receiver_collection = rc

    if o.get("crop"):
        x0, x1, y0, y1 = [float(v) for v in str(o["crop"]).split(",")]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = y0, y1
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    rl = tr.nodes.new("CompositorNodeRLayers")
    src = {g: rl.outputs["Combined_" + g] for g in groups}
    src["albedo"] = rl.outputs["Denoising Albedo"]
    src["normal"] = rl.outputs["Denoising Normal"]
    out_stem = out_path(o["out"])[:-4]
    written = build_comp(sc, src, o, out_stem, variants, crop=bool(o.get("crop")))
    sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.exr_codec = "ZIP"
    sc.render.filepath = out_stem + ".exr"
    bpy.ops.render.render(write_still=True)
    print("rendered", finish_outputs(out_stem, written), round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
