"""K10 helpers: a macro-grade head around the throat, the laser-etch mask, the throat carbon, emitters, light-group
passes and the numpy comp. racket.py / studio.py / look_c.py / k12_lib.py are imported, never modified.

Head (build_head_k10): racket.py's outline, throat and holes; the outline's and throat's plan corners get a small
moulded fillet (the throat triangle's three corners, the two neck corners), every edge is a true rounded profile with
analytic normals. UVs (metres) are a FOLD of the face: on the faces uv = (x, y); down each rounded edge the uv keeps
walking away from the edge along the plan normal (the ply folds over the radius), so the twill runs over every edge
without a seam. Below the bridge radius the wall continues straight down in texture space (the bridge wall is the only
deep wall the camera sees). Objects are split for light linking: face, rim (outline), bridge, armL, armR, holes.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.geometry import tessellate_polygon  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402
import k12_lib as K  # noqa: E402

U = racket.U
ZT = racket.THICK / 2
TEX2 = kqpaths.asset("k04_tex2")
TILE = 0.0026 * 16  # k04_tex2: 16 tows of 2.6 mm per tile
FONT_VAR = kqpaths.font("Archivo-var.ttf")


# ------------------------------------------------------------------ plan loops
def _resample(pts, step):
    P = np.asarray(pts, float)
    P = np.vstack([P, P[:1]])
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.r_[0, np.cumsum(seg)]
    n = max(16, int(round(s[-1] / step)))
    t = np.linspace(0, s[-1], n, endpoint=False)
    x = np.interp(t, s, P[:, 0])
    y = np.interp(t, s, P[:, 1])
    return list(zip(x.tolist(), y.tolist()))


def filleted(loop, r, step, res=96):
    """Round the convex plan corners of a closed loop (morphological opening), then resample uniformly."""
    from shapely.geometry import Polygon
    q = Polygon(loop).buffer(-r, join_style=1, resolution=res).buffer(r, join_style=1, resolution=res)
    return _resample(list(q.exterior.coords)[:-1], step)


def throat_loop(r_fillet=0.0035, step=0.00025):
    return filleted(racket._loop(racket.THROAT_START, racket.THROAT_CURVES, 400), r_fillet, step)


# The neck (v14): racket.py's head stops at a flat end face at y = -0.155. K10 continues it into the handle: the V's
# side walls run into a neck that narrows from 47 mm to 32 mm by y = -0.215 (and stays there, out of frame), joined by
# a 25 mm concave fillet; the thickness lofts from 38 mm to 29 mm over the same span (NECK_TAPER).
NECK = dict(y_top=-0.146, hw_top=0.0235, y_end=-0.215, hw_end=0.0160, y_cut=-0.262, r_concave=0.025)
NECK_TAPER = (-0.150, -0.215, 0.76)  # y0 (full 38 mm), y1, thickness scale reached at y1


# Throat lip segments (arc length in mm from the apex, walking toward +x first: right arm, top-right fillet, bridge,
# top-left fillet, left arm). Each segment is its own object so each piece of a mirror-path ribbon can be linked to
# the stretch of edge it was designed for (curved edges otherwise mirror far, bright parts of a line).
THROAT_SEGS = (0, 2, 10, 20, 34, 44, 54, 70, 90, 100, 109, 119, 130, 142, 152, 160)  # 109-119: the top-left fillet


def throat_arclength(lp):
    """Arc length (m) of every loop sample from the apex (min y), walking toward +x first; and the perimeter."""
    n = len(lp)
    seg = [math.hypot(lp[(i + 1) % n][0] - lp[i][0], lp[(i + 1) % n][1] - lp[i][1]) for i in range(n)]
    ia = min(range(n), key=lambda i: lp[i][1])
    d = 1 if lp[(ia + 8) % n][0] > lp[ia][0] else -1
    s = [0.0] * n
    acc = 0.0
    for k in range(1, n):
        i_prev, i = (ia + d * (k - 1)) % n, (ia + d * k) % n
        acc += seg[i_prev] if d == 1 else seg[i]
        s[i] = acc
    return s, sum(seg)


def _smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def neck_scale(y, taper=NECK_TAPER):
    """Thickness scale s(y) and ds/dy of the lofted neck."""
    y0, y1, s1 = taper
    if y >= y0:
        return 1.0, 0.0
    t = (y0 - y) / (y0 - y1)
    if t >= 1.0:
        return s1, 0.0
    s = 1.0 - (1.0 - s1) * _smooth(t)
    ds = (1.0 - s1) * 6 * t * (1 - t) / (y0 - y1)  # d s / d y (s grows with y)
    return s, ds


def outline_loop(r_fillet=0.003, step=0.0005, neck=None):
    base = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, 600)
    if not neck:
        return filleted(base, r_fillet, step)
    from shapely.geometry import Polygon
    n = neck
    side = []
    for k in range(41):
        y = n["y_top"] + (n["y_end"] - n["y_top"]) * k / 40
        t = (n["y_top"] - y) / (n["y_top"] - n["y_end"])
        side.append((n["hw_top"] + (n["hw_end"] - n["hw_top"]) * _smooth(t), y))
    side.append((n["hw_end"], n["y_cut"]))
    poly = side + [(-x, y) for (x, y) in reversed(side)]
    q = Polygon(base).union(Polygon(poly))
    rc = n["r_concave"]
    q = q.buffer(rc, join_style=1, resolution=96).buffer(-rc, join_style=1, resolution=96)  # concave fillet
    q = q.buffer(-r_fillet, join_style=1, resolution=96).buffer(r_fillet, join_style=1, resolution=96)
    return _resample(list(q.exterior.coords)[:-1], step)


def _normals(loop, span=2):
    """Right normal (away from the solid when the solid is on the left), central differences over +-span samples."""
    n = len(loop)
    out = []
    for i in range(n):
        ax, ay = loop[i - span]
        bx, by = loop[(i + span) % n]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1.0
        out.append((ty / ln, -tx / ln))
    return out


# ------------------------------------------------------------------ head
def build_head_k10(name="KQ10", r_frame=0.0015, r_hole=0.0008, seg_frame=14, seg_hole=6, throat_fillet=0.0035,
                   outline_fillet=0.003, hole_seg=72, neck=NECK, taper=NECK_TAPER, throat_wall="clamp", segs=THROAT_SEGS):
    """throat_wall: "clamp" (v14) = below the lip radius the wall keeps the lip's texture row, so the tows that fold
    over the edge run straight down the wall as streaks (K04's bore); "fold" = the face's twill continues down."""
    outline = outline_loop(outline_fillet, neck=neck)
    throat = throat_loop(throat_fillet)
    holes = []
    for (hx, hy) in racket.holes():
        holes.append([(hx * U + racket.HOLE_R * U * math.cos(2 * math.pi * k / hole_seg),
                       hy * U + racket.HOLE_R * U * math.sin(2 * math.pi * k / hole_seg)) for k in range(hole_seg)])
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
    nl = bm.verts.layers.float_vector.new("kq_n")
    ul = bm.verts.layers.float_vector.new("kq_uv")  # fold UV per vertex (survives the bmesh ops below)
    cap_top, cap_bot = [], []
    face_tag = {}
    for (lp, R, S, kind) in loops:
        outw = _normals(lp, span=2)
        if kind == "throat":
            s_thr, _ = throat_arclength(lp)
            segb = [b_ * 0.001 for b_ in segs]
        prof = []
        for k in range(S + 1):
            th = math.pi / 2 * (1 - k / S)
            prof.append((R * (1 - math.cos(th)), (T2 - R) + R * math.sin(th), math.cos(th), math.sin(th)))
        prof += [(i_, -z, c, -s_) for (i_, z, c, s_) in reversed(prof)]
        pv = [0.0]
        for a, b in zip(prof[:-1], prof[1:]):
            pv.append(pv[-1] + math.hypot(a[0] - b[0], a[1] - b[1]))
        p_b = pv[S]
        rings = []
        for k, (inset, z, c, s_) in enumerate(prof):
            ring = []
            for (x, y), (ox, oy) in zip(lp, outw):
                v = bm.verts.new((x - ox * inset, y - oy * inset, z))
                v[nl] = (ox * c, oy * c, s_)
                ring.append(v)
                p0x, p0y = x - ox * R, y - oy * R  # ring-0 point on the face
                if kind == "hole" or (kind == "throat" and throat_wall == "clamp"):
                    d = min(pv[k], p_b)
                    v[ul] = (p0x + ox * d, p0y + oy * d, 0.0)
                elif kind == "throat" and k > S:
                    v[ul] = (p0x + ox * p_b, p0y + oy * p_b - (pv[k] - p_b), 0.0)
                else:
                    v[ul] = (p0x + ox * pv[k], p0y + oy * pv[k], 0.0)
            rings.append(ring)
        cap_top.append(rings[0])
        cap_bot.append(rings[-1])
        n = len(lp)
        for ri in range(len(prof) - 1):
            a, b = rings[ri], rings[ri + 1]
            for k in range(n):
                j = (k + 1) % n
                f = bm.faces.new((a[k], a[j], b[j], b[k]))
                if kind == "outline":
                    ox, oy = outw[k]
                    face_tag[f] = 6 if (oy < -0.9 and lp[k][1] < (neck["y_cut"] + 0.004 if neck else -0.150)) else 1
                elif kind == "throat":
                    ox, oy = outw[k]
                    # the bridge's wall below the lip is its own object (the wall light); every other throat face
                    # belongs to its arc-length segment (100 + index)
                    if oy < -0.55 and ri >= S:
                        face_tag[f] = 7
                    else:
                        sk = s_thr[k]
                        face_tag[f] = 100 + max(i_ for i_, b_ in enumerate(segb) if sk >= b_)
                else:
                    face_tag[f] = 5
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
            face_tag[f] = 0
    for f in bm.faces:
        f.material_index = face_tag.get(f, 0)
    if taper:
        # the lofted neck: densify the caps where the thickness changes (the tessellation is long slivers there),
        # then scale z by s(y) and carry the analytic normals through the deformation (inverse transpose).
        y0 = taper[0]
        for _ in range(10):
            long_ = [e for e in bm.edges if min(v.co.y for v in e.verts) < y0 + 0.002 and e.calc_length() > 0.0025
                     and all(f.material_index == 0 for f in e.link_faces)]
            if not long_:
                break
            bmesh.ops.subdivide_edges(bm, edges=long_, cuts=1, use_grid_fill=False)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        for v in bm.verts:
            if abs(abs(v.co.z) - T2) < 1e-7 and all(f.material_index == 0 for f in v.link_faces):
                v[nl] = (0.0, 0.0, 1.0 if v.co.z > 0 else -1.0)
        for v in bm.verts:
            s, ds = neck_scale(v.co.y, taper)
            if s == 1.0 and ds == 0.0:
                continue
            nx, ny, nz = v[nl]
            z0 = v.co.z
            v.co.z = z0 * s
            nn = Vector((nx, ny - ds * z0 * nz / s, nz / s)).normalized()
            v[nl] = tuple(nn)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        tag = f.material_index
        for lp_ in f.loops:
            lp_[uvl].uv = (lp_.vert.co.x, lp_.vert.co.y) if tag == 0 else tuple(lp_.vert[ul])[:2]
    objs = {}
    names = {0: "face", 1: "rim", 5: "holes", 6: "neck", 7: "bridgewall"}
    for i_ in range(len(segs)):
        names[100 + i_] = "thr%02d" % i_
    for keep, key in names.items():
        b2 = bm.copy()
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index != keep], context="FACES")
        for f in b2.faces:
            f.material_index = 0
        me = bpy.data.meshes.new(name + "_" + key)
        b2.to_mesh(me)
        b2.free()
        me.shade_smooth()
        nrm = [tuple(a_.vector) for a_ in me.attributes["kq_n"].data]
        me.normals_split_custom_set_from_vertices(nrm)
        me.attributes.remove(me.attributes["kq_n"])
        me.attributes.remove(me.attributes["kq_uv"])
        ob = bpy.data.objects.new(name + "_" + key, me)
        bpy.context.scene.collection.objects.link(ob)
        objs[key] = ob
    bm.free()
    return objs



# ------------------------------------------------------------------ laser-etch mask (face coordinates)
def etch_mask(path, lines, px_per_m=100000, pad=0.0015, bevel=0.000022):
    """White-on-black mask of text lines laid out on the face (x right, y toward the head).
    lines: [(text, cap_height_m, centre_y_m, tracking_em, weight, width[, level])]. Archivo variable font.
    Writes path (sharp), _soft (Gaussian sigma = bevel: the cut's wall profile) and _level (per-line frost level).
    Returns (path, x0, y0, W, H) in metres: the image covers x0..x0+W, y0..y0+H (image row 0 = top = y0+H)."""
    from PIL import Image, ImageDraw, ImageFont
    rend = []
    for ln in lines:
        text, cap, cy, track, wght, wdth = ln[:6]
        f0 = ImageFont.truetype(FONT_VAR, 400)
        f0.set_variation_by_axes([wght, wdth])
        cap_ratio = (f0.getbbox("H")[3] - f0.getbbox("H")[1]) / 400.0
        size = int(round(cap / cap_ratio * px_per_m))
        f = ImageFont.truetype(FONT_VAR, size)
        f.set_variation_by_axes([wght, wdth])
        widths = [f.getlength(ch) for ch in text]
        tw = sum(widths) + track * size * (len(text) - 1)
        rend.append((text, f, size, cap, cy, track, widths, tw))
    W = max(r[7] for r in rend) / px_per_m + 2 * pad
    ytop = max(r[4] + r[3] / 2 for r in rend) + pad
    ybot = min(r[4] - r[3] / 2 for r in rend) - pad
    H = ytop - ybot
    Wp, Hp = int(round(W * px_per_m)), int(round(H * px_per_m))
    im = Image.new("L", (Wp, Hp), 0)
    dr = ImageDraw.Draw(im)
    for (text, f, size, cap, cy, track, widths, tw) in rend:
        x = (Wp - tw) / 2
        hb = f.getbbox("H")
        # place the cap-height box centred on cy
        row_top = (ytop - (cy + cap / 2)) * px_per_m
        for ch, wch in zip(text, widths):
            dr.text((x, row_top - hb[1]), ch, font=f, fill=255)
            x += wch + track * size
    im.save(path)
    from PIL import ImageFilter
    im.filter(ImageFilter.GaussianBlur(px_per_m * bevel)).save(path.replace(".png", "_soft.png"))
    # level: per-line frost strength (lines[i][6], default 1), dilated past the bevel so the frost covers it
    lv = Image.new("L", (Wp, Hp), 0)
    dl = ImageDraw.Draw(lv)
    for ln, (text, f, size, cap, cy, track, widths, tw) in zip(lines, rend):
        level = ln[6] if len(ln) > 6 else 1.0
        x = (Wp - tw) / 2
        hb = f.getbbox("H")
        row_top = (ytop - (cy + cap / 2)) * px_per_m
        for ch, wch in zip(text, widths):
            dl.text((x, row_top - hb[1]), ch, font=f, fill=int(round(255 * level)))
            x += wch + track * size
    d = max(3, int(round(px_per_m * bevel * 2.5)) | 1)
    lv.filter(ImageFilter.MaxFilter(d)).filter(ImageFilter.GaussianBlur(2)).save(path.replace(".png", "_level.png"))
    return path, -W / 2, ybot, W, H


# ------------------------------------------------------------------ materials
def _img(nb, vec, path, cs, interp="Linear", ext="REPEAT"):
    n = nb.n.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(path, check_existing=True)
    n.image.colorspace_settings.name = cs
    n.interpolation = interp
    n.extension = ext
    nb.l.new(vec, n.inputs["Vector"])
    return n


def mat_carbon_k10(name, o, etch=None, wall=False):
    """K04's carbon (k04_tex2 twill: per-tow width, meander, filament streaks, anisotropic tangent across the fibres,
    graphite-like metal under a glass-clear 0.035 coat with a whisper of print-through), mapped on the fold UVs.
    etch: (mask_png, x0, y0, W, H): a frosted laser mark in the lacquer, 12 um deep (crisp edge glints), whose frost
    scatters a raking light; outside a raking light it reads as a soft satin mark in the black gloss."""
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    tc = nb.n.new("ShaderNodeTexCoord")
    mp = nb.n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / TILE, 1 / TILE, 1)
    nb.l.new(tc.outputs["UV"], mp.inputs["Vector"])
    vec = mp.outputs["Vector"]
    alb = _img(nb, vec, os.path.join(TEX2, "albedo.png"), "sRGB")
    rgh = _img(nb, vec, os.path.join(TEX2, "rough.png"), "Non-Color")
    hgt = _img(nb, vec, os.path.join(TEX2, "height16.png"), "Non-Color", interp="Cubic")
    rot = _img(nb, vec, os.path.join(TEX2, "rot16.png"), "Non-Color")
    cot = _img(nb, vec, os.path.join(TEX2, "coat16.png"), "Non-Color", interp="Cubic")
    f0 = float(o.get("f0", 0.12))
    # fibre-bundle streaks along each tow (0.1-0.3 mm, K04's 0.04-0.12 mm filaments are sub-pixel here): a noise
    # stretched along the local fibre direction (rot16 gives the tangent ACROSS the fibres, as a fraction of a turn)
    streak = None
    if float(o.get("streak", 1.0)) > 0:
        # straight streaks: a 1D noise across u for tows running along v, across v for tows along u, picked by the
        # tow's orientation (rot16 > 0.5: fibres along u). No rotated coordinates, so no swirls at the crossovers.
        uu, vv, _ = nb.coords("UV")
        S = 1.0 / float(o.get("streak_w", 0.00012))
        Sl = 1.0 / float(o.get("streak_len", 0.02))

        def n1(a_, b_, z_):
            cv_ = nb.n.new("ShaderNodeCombineXYZ")
            nb.l.new(nb.math("MULTIPLY", a_, S), cv_.inputs[0])
            nb.l.new(nb.math("MULTIPLY", b_, Sl), cv_.inputs[1])
            cv_.inputs[2].default_value = z_
            t_ = nb.n.new("ShaderNodeTexNoise")
            t_.noise_dimensions = "3D"
            t_.inputs["Scale"].default_value = 1.0
            t_.inputs["Detail"].default_value = float(o.get("streak_detail", 2.0))
            t_.inputs["Roughness"].default_value = 0.6
            nb.l.new(cv_.outputs[0], t_.inputs["Vector"])
            return nb.smooth(t_.outputs["Fac"], 0.3, 0.7)

        s_u = n1(vv, uu, 0.0)   # fibres along u: varies across them (with v)
        s_v = n1(uu, vv, 7.3)   # fibres along v
        m_ = nb.smooth(rot.outputs["Color"], 0.42, 0.58)
        streak = nb.math("SUBTRACT", nb.lerp(m_, s_v, s_u), 0.5)  # -0.5..0.5
    tint = nb.n.new("ShaderNodeMixRGB")
    tint.blend_type = "MULTIPLY"
    tint.inputs["Fac"].default_value = 1.0
    tint.inputs["Color2"].default_value = (f0, f0, f0 * 1.02, 1)
    nb.l.new(alb.outputs["Color"], tint.inputs["Color1"])
    if streak is not None:
        sa_ = nb.n.new("ShaderNodeMixRGB")
        sa_.blend_type = "MULTIPLY"
        sa_.inputs["Fac"].default_value = 1.0
        nb.l.new(tint.outputs["Color"], sa_.inputs["Color1"])
        nb.l.new(nb.gray(nb.math("MULTIPLY_ADD", streak, float(o.get("streak_a", 0.5)), 1.0)), sa_.inputs["Color2"])
        nb.l.new(sa_.outputs["Color"], b.inputs["Base Color"])
    else:
        nb.l.new(tint.outputs["Color"], b.inputs["Base Color"])
    # v14: K04's filament relief and broad anisotropic flash (K04: bump 0.2, rough_s 0.95)
    rr = nb.math("MULTIPLY", rgh.outputs["Color"], float(o.get("rough_s", 0.65)))
    if streak is not None:
        rr = nb.math("MULTIPLY", rr, nb.math("MULTIPLY_ADD", streak, float(o.get("streak_r", 0.8)), 1.0))
    nb.l.new(rr, b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = float(o.get("metal", 0.85))
    b.inputs["IOR"].default_value = 1.6
    b.inputs["Specular IOR Level"].default_value = 0.6
    b.inputs["Anisotropic"].default_value = float(o.get("aniso", 0.95))
    rotv = nb.math("MULTIPLY_ADD", rot.outputs["Color"], 0.5, -0.125)
    tg = nb.n.new("ShaderNodeTangent")
    tg.direction_type = "UV_MAP"
    tg.uv_map = "UVMap"
    tang = tg.outputs["Tangent"]
    bump = nb.n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = float(o.get("bump", 0.18))
    bump.inputs["Distance"].default_value = 0.00025
    if streak is not None:
        nb.l.new(nb.math("MULTIPLY_ADD", streak, float(o.get("streak_h", 0.3)), hgt.outputs["Color"]), bump.inputs["Height"])
    else:
        nb.l.new(hgt.outputs["Color"], bump.inputs["Height"])
    nrm = bump.outputs["Normal"]
    cb = nb.n.new("ShaderNodeBump")
    cb.inputs["Strength"].default_value = float(o.get("print", 0.004))
    cb.inputs["Distance"].default_value = 0.00025
    nb.l.new(cot.outputs["Color"], cb.inputs["Height"])
    cnrm = cb.outputs["Normal"]
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat IOR"].default_value = 1.5
    coat_r = float(o.get("coat_rough", 0.035))
    b.inputs["Coat Roughness"].default_value = coat_r
    occ = None
    if wall:
        # Below the lip radius the throat wall is a different plane: the tows that fold over the edge run straight
        # down it (clamped UVs, so the relief reads as vertical streaks), the anisotropic tangent turns horizontal
        # (across those tows, as K04's bore), and the wall sees less and less of the room with depth (occlusion).
        _, _, z = nb.coords("Object")
        below = nb.smooth(z, ZT - 0.0015, ZT - 0.0021)
        geo = nb.n.new("ShaderNodeNewGeometry")
        cr = nb.n.new("ShaderNodeVectorMath")
        cr.operation = "CROSS_PRODUCT"
        cr.inputs[0].default_value = (0, 0, 1)
        nb.l.new(geo.outputs["Normal"], cr.inputs[1])
        cz = nb.n.new("ShaderNodeVectorMath")
        cz.operation = "NORMALIZE"
        nb.l.new(cr.outputs[0], cz.inputs[0])
        mt = nb.n.new("ShaderNodeMix")
        mt.data_type = "VECTOR"
        nb.l.new(below, mt.inputs["Factor"])
        nb.l.new(tang, mt.inputs[4])
        nb.l.new(cz.outputs[0], mt.inputs[5])
        tang = mt.outputs[1]
        rotv = nb.math("MULTIPLY", rotv, nb.math("SUBTRACT", 1.0, below))
        occ = nb.math("MULTIPLY", nb.smooth(z, ZT - float(o.get("wall_z0", 0.0025)), ZT - float(o.get("wall_z1", 0.017))),
                      float(o.get("wall_occ", 0.93)))
    nb.l.new(rotv, b.inputs["Anisotropic Rotation"])
    nb.l.new(tang, b.inputs["Tangent"])
    surf = b.outputs[0]
    if etch:
        path, x0, y0, W, H = etch
        u, v, _ = nb.coords("UV")
        cv = nb.n.new("ShaderNodeCombineXYZ")
        nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", u, x0), W), cv.inputs[0])
        nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", v, y0), H), cv.inputs[1])
        mkb = _img(nb, cv.outputs[0], path.replace(".png", "_soft.png"), "Non-Color", interp="Cubic", ext="CLIP")
        mkl = _img(nb, cv.outputs[0], path.replace(".png", "_level.png"), "Non-Color", interp="Cubic", ext="CLIP")
        _, _, nz = nb.coords("Normal")
        onface = nb.smooth(nz, 0.95, 0.99)
        soft = mkb.outputs["Color"]
        # the frost covers the floor of the mark and its bevelled wall (soft mask from 0.12): the wall's Lambert term
        # under the grazing rake is the hairline glint (facing the light) and the dark hairline (facing away)
        mask = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(soft, float(o.get("frost_lo", 0.03)), float(o.get("frost_hi", 0.22))),
                                           mkl.outputs["Color"]), onface)
        relief = nb.math("MULTIPLY", soft, onface)
        depth = float(o.get("etch_depth", 0.0001))
        eb = nb.n.new("ShaderNodeBump")
        eb.inputs["Strength"].default_value = 1.0
        eb.inputs["Distance"].default_value = depth
        nb.l.new(nb.math("MULTIPLY", relief, -1.0), eb.inputs["Height"])
        nb.l.new(nrm, eb.inputs["Normal"])
        nrm = eb.outputs["Normal"]
        eb2 = nb.n.new("ShaderNodeBump")
        eb2.inputs["Strength"].default_value = 1.0
        eb2.inputs["Distance"].default_value = depth
        nb.l.new(nb.math("MULTIPLY", relief, -1.0), eb2.inputs["Height"])
        nb.l.new(cnrm, eb2.inputs["Normal"])
        cnrm = eb2.outputs["Normal"]
        nb.l.new(nb.math("MULTIPLY_ADD", mask, float(o.get("etch_coat_rough", 0.42)) - coat_r, coat_r), b.inputs["Coat Roughness"])
        # micro-grain of the laser frost (~20-40 um pits): roughness, albedo and normal, so it glitters under the rake
        gs = 1.0 / float(o.get("grain", 0.0001))
        gv = nb.n.new("ShaderNodeCombineXYZ")
        nb.l.new(nb.math("MULTIPLY", u, gs), gv.inputs[0])
        nb.l.new(nb.math("MULTIPLY", v, gs), gv.inputs[1])
        nz_ = nb.n.new("ShaderNodeTexNoise")
        nz_.noise_dimensions = "3D"
        nz_.inputs["Scale"].default_value = 1.0
        nz_.inputs["Detail"].default_value = 2.0
        nz_.inputs["Roughness"].default_value = 0.6
        nb.l.new(gv.outputs[0], nz_.inputs["Vector"])
        gn = nb.smooth(nz_.outputs["Fac"], 0.32, 0.68)  # stretch the noise to a full 0..1 grain
        fr = nb.n.new("ShaderNodeBsdfPrincipled")
        g = float(o.get("frost", 0.46))
        ga = float(o.get("grain_alb", 0.5))
        fcol = nb.math("MULTIPLY", g, nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", gn, 0.5), ga, 1.0))
        nb.l.new(nb.gray(fcol), fr.inputs["Base Color"])
        nb.l.new(nb.math("ADD", float(o.get("frost_rough", 0.85)), nb.math("MULTIPLY", nb.math("SUBTRACT", gn, 0.5),
                                                                         float(o.get("grain_rough", 0.5))), clamp=True),
                 fr.inputs["Roughness"])
        fr.inputs["Metallic"].default_value = 0.0
        fr.inputs["Specular IOR Level"].default_value = 0.5
        gb = nb.n.new("ShaderNodeBump")
        gb.inputs["Strength"].default_value = float(o.get("grain_bump", 0.8))
        gb.inputs["Distance"].default_value = float(o.get("grain_depth", 0.000004))
        nb.l.new(gn, gb.inputs["Height"])
        nb.l.new(cnrm, gb.inputs["Normal"])  # the frost is in the lacquer: its relief is the cut, not the weave
        nb.l.new(gb.outputs["Normal"], fr.inputs["Normal"])
        mx = nb.n.new("ShaderNodeMixShader")
        nb.l.new(nb.math("MULTIPLY", mask, float(o.get("frost_mix", 0.88))), mx.inputs[0])
        nb.l.new(b.outputs[0], mx.inputs[1])
        nb.l.new(fr.outputs[0], mx.inputs[2])
        surf = mx.outputs[0]
    nb.l.new(nrm, b.inputs["Normal"])
    nb.l.new(cnrm, b.inputs["Coat Normal"])
    if occ is not None:
        blk = nb.n.new("ShaderNodeBsdfDiffuse")
        blk.inputs["Color"].default_value = (0, 0, 0, 1)
        mo = nb.n.new("ShaderNodeMixShader")
        nb.l.new(occ, mo.inputs[0])
        nb.l.new(surf, mo.inputs[1])
        nb.l.new(blk.outputs[0], mo.inputs[2])
        surf = mo.outputs[0]
    nb.l.new(surf, out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ emitters
def panel(name, loc, size, strength, target, color=(1, 1, 1), roll=0.0, edge=(-1.0, -0.5), fade=(0.0, 1.0),
          band=None, floor=0.0, group=None):
    """Camera-invisible emissive card (K04's panel): a smooth falloff edge across local X (edge = from, to in 0..1),
    a soft taper along local Y (fade), optional stripe (band = fall start, fall end, residual). roll in degrees."""
    ob = K.plane(name, size, loc, normal_to=target)
    rm = ob.rotation_euler.to_matrix() @ Matrix.Rotation(math.radians(roll), 3, "Z")
    ob.rotation_euler = rm.to_euler()

    def s(nb):
        u, v, _ = nb.coords("UV")
        ex = nb.n.new("ShaderNodeMapRange")
        ex.interpolation_type = "SMOOTHSTEP"
        ex.inputs["From Min"].default_value, ex.inputs["From Max"].default_value = edge
        ex.inputs["To Min"].default_value = floor
        nb.l.new(u, ex.inputs["Value"])
        f = ex.outputs["Result"]
        if band:
            f = nb.math("MULTIPLY", f, nb.math("MULTIPLY_ADD", nb.smooth(u, band[0], band[1]), -(1 - band[2]), 1.0))
        ay = nb.math("ABSOLUTE", nb.math("SUBTRACT", v, 0.5))
        fy = nb.smooth(ay, 0.5, 0.5 - 0.5 * fade[1]) if fade[1] > 0 else 1.0
        return nb.math("MULTIPLY", nb.math("MULTIPLY", f, fy), strength)

    ob.data.materials.append(K.emitter_mat(name + "Mat", color, s, additive=True))
    K.visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    if group:
        ob.lightgroup = group
    return ob


def weighted_ribbon(name, pts_a, pts_b, weights, strength, color=(1, 1, 1), soft_v=0.2, group=None):
    """Camera-invisible emissive ribbon between two polylines; emission = strength * weight (a per-vertex profile
    along the ribbon, interpolated) * a soft taper across it. Emission + transparency: it never blocks other rays."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    wl = bm.verts.layers.float.new("kq_w")
    n = len(pts_a)
    ra, rb = [], []
    for p, q, w in zip(pts_a, pts_b, weights):
        a_ = bm.verts.new(p)
        b_ = bm.verts.new(q)
        a_[wl] = b_[wl] = float(w)
        ra.append(a_)
        rb.append(b_)
    for i in range(n - 1):
        f = bm.faces.new((ra[i], ra[i + 1], rb[i + 1], rb[i]))
        for lp, uv in zip(f.loops, ((i / (n - 1), 0), ((i + 1) / (n - 1), 0), ((i + 1) / (n - 1), 1), (i / (n - 1), 1))):
            lp[uvl].uv = uv
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)

    def s(nb):
        at = nb.n.new("ShaderNodeAttribute")
        at.attribute_type = "GEOMETRY"
        at.attribute_name = "kq_w"
        _, v, _ = nb.coords("UV")
        fv = nb.math("MULTIPLY", nb.smooth(v, 0.0, soft_v), nb.smooth(v, 1.0, 1.0 - soft_v)) if soft_v else 1.0
        return nb.math("MULTIPLY", nb.math("MULTIPLY", at.outputs["Fac"], fv), strength)

    ob.data.materials.append(K.emitter_mat(name + "Mat", color, s, additive=True))
    K.visibility(ob, camera=False, diffuse=False, glossy=True, shadow=False)
    if group:
        ob.lightgroup = group
    return ob


def link_only(emitter, objs, name):
    c = bpy.data.collections.new(name)
    for o_ in objs:
        c.objects.link(o_)
    emitter.light_linking.receiver_collection = c


# ------------------------------------------------------------------ passes and comp
def setup_passes(sc, groups, out_dir, stem):
    """Per light group: OIDN denoise (albedo + normal), written as linear EXR files <stem>_<group>.exr."""
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in groups:
        vl.lightgroups.add(name=g)
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    rl = tr.nodes.new("CompositorNodeRLayers")
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = out_dir
    fo.format.file_format = "OPEN_EXR"
    fo.format.color_mode = "RGB"
    fo.format.color_depth = "16"
    fo.format.exr_codec = "ZIP"
    fo.file_slots.clear()
    first = None
    for g in groups:
        dn = tr.nodes.new("CompositorNodeDenoise")
        dn.prefilter = "ACCURATE"
        dn.use_hdr = True
        tr.links.new(rl.outputs["Combined_" + g], dn.inputs["Image"])
        tr.links.new(rl.outputs["Denoising Normal"], dn.inputs["Normal"])
        tr.links.new(rl.outputs["Denoising Albedo"], dn.inputs["Albedo"])
        slot = f"{stem}_{g}_"
        fo.file_slots.new(slot)
        tr.links.new(dn.outputs["Image"], fo.inputs[slot])
        first = first or dn.outputs["Image"]
    comp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(first, comp.inputs["Image"])


def collect_passes(out_dir, stem, groups):
    paths = {}
    for g in groups:
        pre = f"{stem}_{g}_"
        c = [f for f in os.listdir(out_dir) if f.startswith(pre) and f.endswith(".exr") and f[len(pre):-4].isdigit()]
        c.sort(key=lambda f: os.path.getmtime(os.path.join(out_dir, f)))
        if c:
            dst = os.path.join(out_dir, f"{stem}_{g}.exr")
            os.replace(os.path.join(out_dir, c[-1]), dst)
            paths[g] = dst
        elif os.path.exists(os.path.join(out_dir, f"{stem}_{g}.exr")):
            paths[g] = os.path.join(out_dir, f"{stem}_{g}.exr")
    return paths


def load_lin(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4)[..., :3]


def save_display(lin, path, sc):
    """Linear scene-referred RGB (rows bottom-up, as Blender stores them) -> PNG through the scene's view transform."""
    h, w = lin.shape[:2]
    a = np.ones((h, w, 4), np.float32)
    a[..., :3] = np.clip(lin, 0, None)
    res = bpy.data.images.new("k10_comp", w, h, alpha=True, float_buffer=True)
    res.pixels.foreach_set(a.ravel())
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    res.save_render(path, scene=sc)
    bpy.data.images.remove(res)
    return path


def sky_projected(name, cam_loc, z_face, a, b, centre, size, dist, s0, s1, strength, floor=0.0, pool=None,
                  color=(1, 1, 1), group=None, band=None):
    """A softbox whose reflection in the face plane IS a designed 2D gradient: every panel point is projected from the
    mirrored camera onto the face plane (where its reflection appears), and the emission is a smoothstep of that
    point's signed distance from the face line a-b (metres, s0 -> s1), times an optional radial pool
    (pool = (cx, cy, r0, r1): 1 inside r0, falling to 0 at r1). The panel faces `centre` (a face point) from the
    mirror direction, `dist` away, `size` wide (big enough to cover every reflection the frame needs)."""
    cm = Vector((cam_loc[0], cam_loc[1], 2 * z_face - cam_loc[2]))
    C = Vector(centre)
    d = (C - Vector(cam_loc)).normalized()
    r = (d - 2 * d.dot(Vector((0, 0, 1))) * Vector((0, 0, 1))).normalized()
    ob = K.plane(name, size, tuple(C + r * dist), normal_to=tuple(C))
    A, B = Vector(a), Vector(b)
    ab = (B - A)
    L_ = ab.length
    ax, ay, bx, by = A.x, A.y, ab.x / L_, ab.y / L_

    def s(nb):
        geo = nb.n.new("ShaderNodeNewGeometry")
        sep = nb.n.new("ShaderNodeSeparateXYZ")
        nb.l.new(geo.outputs["Position"], sep.inputs["Vector"])
        X, Y, Z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
        t = nb.math("DIVIDE", z_face - cm.z, nb.math("SUBTRACT", Z, cm.z))
        px = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", X, cm.x), t, cm.x)
        py = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", Y, cm.y), t, cm.y)
        dx = nb.math("SUBTRACT", px, ax)
        dy = nb.math("SUBTRACT", py, ay)
        sd = nb.math("SUBTRACT", nb.math("MULTIPLY", dx, by), nb.math("MULTIPLY", dy, bx))
        g = nb.smooth(sd, s0, s1)
        if band:
            # a soft stripe instead of a half-plane: centre offset band[0] (m), half width band[1] (m)
            g = nb.smooth(nb.math("ABSOLUTE", nb.math("SUBTRACT", sd, band[0])), band[1], 0.0)
        if pool:
            cx, cy, r0, r1 = pool
            ex = nb.math("SUBTRACT", px, cx)
            ey = nb.math("SUBTRACT", py, cy)
            rr = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", ex, ex), nb.math("MULTIPLY", ey, ey)))
            g = nb.math("MULTIPLY", g, nb.smooth(rr, r1, r0))
        g = nb.math("MULTIPLY_ADD", g, 1 - floor, floor)
        return nb.math("MULTIPLY", g, strength)

    ob.data.materials.append(K.emitter_mat(name + "Mat", color, s, additive=True))
    K.visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    if group:
        ob.lightgroup = group
    return ob
