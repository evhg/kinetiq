"""Shared helpers for K03-section-cut and K03b-tubular (v2, owned by the K03 artist).

v2 (art-director review): slanted two-hole cut, 0.15 mm polished chamfer on every cut edge, satin floor with
contact shadow and a floor-only light pool (fill rule), camera at 24 deg elevation, reflection-only rig,
light-group glow for lg_shell, 16-bit output with 1-LSB TPDF dither.

Cut: a vertical plane through the centres of holes (-40.5, 6.5) mm and (27.0, 30.0) mm (19.2 deg to the
racket's X axis). It cuts exactly those two bores through their centres; every other hole is >= 8.88 mm from
the plane, so the plane clears their 1.1 mm lips (7.3 mm) and K03's 2 mm shell sleeves (8.2 mm). The 14 deg
line through (-67.5, 6.5) and (27, 30) suggested in review passes 6.52 mm from three neighbours: it would nick
their lips and slice their shell sleeves (three stray dark slivers in the foam). Any lattice line at 14 deg has
neighbours at 6.5 mm, so 19.2 deg is the closest clean slant.

Geometry: built in racket model space (+Z out of the face, tip +Y), bisected on the slanted plane, the open
section capped with exact 2D regions (shapely) in plane coordinates (u along the cut, z), then the object is
placed with matrix_world = cut_matrix(): the section plane becomes world y = 0 facing -Y and the kept part runs
away from camera. Object coordinates stay in model space, so the weave stays aligned with the racket.
"""
import math
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.geometry import tessellate_polygon  # noqa: E402
from shapely.geometry import Polygon, MultiPolygon  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402

HALF_T = racket.THICK / 2

# ------------------------------------------------------------------ the cut
HOLE_A = (-0.0405, 0.0065)
HOLE_B = (0.0270, 0.0300)
CUT_TH = math.atan2(HOLE_B[1] - HOLE_A[1], HOLE_B[0] - HOLE_A[0])
CUT_T = Vector((math.cos(CUT_TH), math.sin(CUT_TH), 0.0))     # along the cut (world +X)
CUT_N = Vector((-math.sin(CUT_TH), math.cos(CUT_TH), 0.0))    # kept side (world +Y)
CUT_P0 = Vector(((HOLE_A[0] + HOLE_B[0]) / 2, (HOLE_A[1] + HOLE_B[1]) / 2, 0.0)) + CUT_N * 0.00003
CHAMFER = 0.00015       # 45 deg polished chamfer leg on every cut edge
FLOOR_GAP = 0.005       # the piece floats 5 mm over the floor (invisible stand)
FLOOR_Z = -HALF_T - FLOOR_GAP


def cut_matrix():
    return Matrix.Rotation(-CUT_TH, 4, "Z") @ Matrix.Translation(-CUT_P0)


def to_uv(co):
    return ((co - CUT_P0).dot(CUT_T), co.z)


def from_uv(u, z, off=0.0):
    return CUT_P0 + CUT_T * u + CUT_N * off + Vector((0.0, 0.0, z))


def hole_u():
    """u (world x) of the two cut bores."""
    return [to_uv(Vector((h[0], h[1], 0.0)))[0] for h in (HOLE_A, HOLE_B)]


# ------------------------------------------------------------------ CLI
def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    opts = {"w": 960, "h": 540, "spp": 32, "out": None, "variant": "full"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            opts[k] = v
            i += 1
        elif a.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            opts[a[2:]] = argv[i + 1]
            i += 2
        elif a.startswith("--"):
            opts[a[2:]] = True
            i += 1
        else:
            i += 1
    for k in ("w", "h", "spp"):
        opts[k] = int(opts[k])
    return opts


def fopt(o, k, d):
    return float(o.get(k, d))


def out_path(name):
    """--out is a name under out/ ('K03_prev' -> out/K03_prev.png, 'final/K03' -> out/final/K03.png) or absolute."""
    p = name if name.endswith(".png") else name + ".png"
    if not os.path.isabs(p):
        p = os.path.join(studio.OUT, p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


LIGHTS = []


def reg(ob):
    LIGHTS.append(ob)
    return ob


def finish(o, default_name):
    """Render honouring dev flags: --crop x0,x1,y0,y1, --solo a,b (only those lights), --each.
    Every written PNG is 16-bit with a 1-LSB (8-bit scale) TPDF dither so web encodes do not band."""
    if o.get("norender"):
        return None
    name = o["out"] or default_name
    if o.get("crop"):
        x0, x1, y0, y1 = [float(v) for v in str(o["crop"]).split(",")]
        r = bpy.context.scene.render
        r.use_border = True
        r.use_crop_to_border = True
        r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = x0, x1, y0, y1
    if o.get("each"):
        paths = []
        for keep in [[x] for x in LIGHTS] + [list(LIGHTS)]:
            for ob in LIGHTS:
                ob.hide_render = ob not in keep
            tag = keep[0].name if len(keep) == 1 else "ALL"
            paths.append(render_to(out_path(name + "_" + tag), dither=not o.get("nodither")))
        return paths
    if o.get("solo"):
        keep = set(str(o["solo"]).split(","))
        for ob in LIGHTS:
            ob.hide_render = ob.name not in keep
    return render_to(out_path(name), dither=not o.get("nodither"))


def render_to(path, dither=True):
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    if dither:
        dither_png16(path)
    return path


def _png16_write(path, rgb16):
    h, w, _ = rgb16.shape
    raw = np.empty((h, 1 + w * 6), dtype=np.uint8)
    raw[:, 0] = 0
    raw[:, 1:] = rgb16.astype(">u2").view(np.uint8).reshape(h, w * 6)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 2, 0, 0, 0))
    png += chunk(b"sRGB", b"\x00")
    png += chunk(b"IDAT", zlib.compress(raw.tobytes(), 6)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def dither_png16(path, lsb=1.0, seed=7):
    """Add TPDF dither of +-`lsb` 8-bit steps to a display-referred 16-bit PNG (in place)."""
    im = bpy.data.images.load(path, check_existing=False)
    im.colorspace_settings.name = "Non-Color"
    w, h = im.size
    a = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float64)
    rng = np.random.default_rng(seed)
    a += (rng.random(a.shape) - rng.random(a.shape)) * (lsb / 255.0)
    _png16_write(path, np.clip(np.rint(a * 65535.0), 0, 65535).astype(np.uint16))


# ------------------------------------------------------------------ 2D helpers
def _clean(coords):
    pts = [tuple(c) for c in coords]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    out = []
    for p in pts:
        if not out or (p[0] - out[-1][0]) ** 2 + (p[1] - out[-1][1]) ** 2 > 1e-14:
            out.append(p)
    if len(out) > 2 and (out[0][0] - out[-1][0]) ** 2 + (out[0][1] - out[-1][1]) ** 2 <= 1e-14:
        out.pop()
    return out


def polys_of(geom):
    """Flatten any shapely geometry into a list of non-empty Polygons."""
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom] if geom.area > 1e-12 else []
    if isinstance(geom, MultiPolygon):
        return [g for g in geom.geoms if g.area > 1e-12]
    out = []
    for g in getattr(geom, "geoms", []):
        out += polys_of(g)
    return out


def signed_area(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))


def loop_normals(pts, min_d=0.00005):
    """Unit inward normals of a closed 2D loop (robust to near-duplicate points)."""
    n = len(pts)
    ccw = signed_area(pts) > 0
    out = []
    for i in range(n):
        j, k = (i + 1) % n, (i - 1) % n
        for _ in range(12):
            if math.dist(pts[j], pts[i]) >= min_d:
                break
            j = (j + 1) % n
        for _ in range(12):
            if math.dist(pts[k], pts[i]) >= min_d:
                break
            k = (k - 1) % n
        tx, tz = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]
        ln = math.hypot(tx, tz) or 1.0
        lx, lz = -tz / ln, tx / ln  # left normal
        out.append((lx, lz) if ccw else (-lx, -lz))
    return out


def smooth_noise(seed, n_terms=5, base=0.004):
    """1D smooth noise in [-1, 1] over a length parameter (metres): a sum of sines, wavelengths ~base*[1..4]."""
    rng = np.random.default_rng(seed)
    ks = [2 * math.pi / (base * rng.uniform(0.7, 4.0)) for _ in range(n_terms)]
    ph = rng.uniform(0, 2 * math.pi, n_terms)
    amp = rng.uniform(0.5, 1.0, n_terms)
    amp = amp / amp.sum()

    def f(s):
        return float(sum(a * math.sin(k * s + p) for a, k, p in zip(amp, ks, ph)))
    return f


# ------------------------------------------------------------------ section builder
class Section:
    """Head bisected on the slanted plane + capped section with a polished chamfer on every cut edge.
    `regions(loop_uv, poly) -> [(shapely Polygon in (u, z), mat_index, tone), ...]`; the loop handed over is the
    chamfer-inset boundary (CHAMFER inside the true outer surface)."""

    def __init__(self, name, regions_fn, materials, head, chamfer=CHAMFER, chamfer_mat=None):
        me = head.data
        bm = bmesh.new()
        bm.from_mesh(me)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=CUT_P0 + CUT_N * chamfer, plane_no=CUT_N, clear_inner=True)
        for v in bm.verts:
            if (v.co - CUT_P0).dot(CUT_N) < chamfer - 1e-6:
                raise RuntimeError("bisect kept the wrong side")
        loops = self._boundary_loops(bm)
        tone_layer = bm.faces.layers.float.new("tone")
        for f in bm.faces:
            f[tone_layer] = 0.0
        mats = list(materials)
        self.ch_idx = None
        if chamfer > 0:
            self.ch_idx = len(mats)
            mats.append(chamfer_mat or mat_chamfer())
        self.loops_uv = []
        weld = []
        for lp in loops:
            uv = [to_uv(v.co) for v in lp]
            if chamfer > 0:
                inw = loop_normals(uv)
                ins = [(p[0] + n[0] * chamfer, p[1] + n[1] * chamfer) for p, n in zip(uv, inw)]
                nv = [bm.verts.new(from_uv(u, z)) for (u, z) in ins]
                weld += nv
                m = len(lp)
                for i in range(m):
                    j = (i + 1) % m
                    try:
                        f = bm.faces.new((lp[i], lp[j], nv[j], nv[i]))
                    except ValueError:
                        continue
                    f.material_index = self.ch_idx
                    f[tone_layer] = 1.0
                    f.normal_update()
                    ou = -(inw[i][0] + inw[j][0]) / 2
                    oz = -(inw[i][1] + inw[j][1]) / 2
                    expect = -CUT_N + CUT_T * ou + Vector((0, 0, oz))
                    if f.normal.dot(expect) < 0:
                        f.normal_flip()
                pts = ins
            else:
                pts = uv
            self.loops_uv.append((uv, pts))
            poly = Polygon(pts)
            if not poly.is_valid:
                poly = poly.buffer(0)
            for (rp, mi, tone) in regions_fn(pts, poly):
                weld += self._fill(bm, rp, mi, tone, tone_layer)
        bmesh.ops.remove_doubles(bm, verts=list(set(v for v in weld if v.is_valid)), dist=2e-7)
        bm.faces.ensure_lookup_table()
        strip = set()
        for f in bm.faces:
            if not f.is_valid:
                continue
            if f.material_index == self.ch_idx and self.ch_idx is not None:
                strip.add(f)
                f.smooth = True
            elif f.normal.dot(CUT_N) < -0.999 and abs((f.calc_center_median() - CUT_P0).dot(CUT_N)) < 1e-6:
                f.smooth = False
                for e in f.edges:
                    e.smooth = False
        for f in strip:
            for e in f.edges:
                if any(g not in strip for g in e.link_faces):
                    e.smooth = False
        bm.normal_update()
        me.materials.clear()
        for m in mats:
            me.materials.append(m)
        bm.to_mesh(me)
        bm.free()
        me.update()
        wn = head.modifiers.new("wn", "WEIGHTED_NORMAL")
        wn.mode = "FACE_AREA"
        wn.weight = 100
        wn.keep_sharp = True
        wn.thresh = 0.01
        racket._apply_all(head)
        self.obj = head
        head.matrix_world = cut_matrix()

    @staticmethod
    def _boundary_loops(bm):
        bnd = [e for e in bm.edges if e.is_boundary]
        adj = {}
        for e in bnd:
            a, b = e.verts
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
        seen, loops = set(), []
        for start in adj:
            if start in seen:
                continue
            lp, prev, cur = [start], None, start
            seen.add(start)
            while True:
                nxt = [n for n in adj[cur] if n is not prev and n not in seen]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                seen.add(cur)
                lp.append(cur)
            if len(lp) > 8:
                loops.append(lp)
        return loops

    def _fill(self, bm, poly, mi, tone, tone_layer):
        rings = [_clean(poly.exterior.coords)] + [_clean(r.coords) for r in poly.interiors]
        rings = [r for r in rings if len(r) >= 3]
        if not rings:
            return []
        verts = [bm.verts.new(from_uv(u, z)) for r in rings for (u, z) in r]
        tris = tessellate_polygon([[Vector((u, z, 0)) for (u, z) in r] for r in rings])
        for (a, b, c) in tris:
            try:
                f = bm.faces.new((verts[a], verts[b], verts[c]))
            except ValueError:
                continue
            f.normal_update()
            if f.normal.dot(CUT_N) > 0:
                f.normal_flip()
            f.material_index = mi
            f[tone_layer] = tone
        return verts

    def chamfer_line(self, zmin=-0.004, bore_clear=0.0085):
        """World points + normals along the middle of the chamfer facet on the OUTER cut edge (top edge and the
        upper rounded side walls; the bore edges are skipped). For the hot specular line ribbon."""
        mw = cut_matrix()
        rot = mw.to_3x3()
        hu = hole_u()
        segs = []
        for uv, ins in self.loops_uv:
            inw = loop_normals(ins)
            rows = []
            for (p, q, n) in zip(uv, ins, inw):
                u, z = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
                if z > zmin and all(abs(u - h) > bore_clear for h in hu):
                    Nm = (-CUT_N + CUT_T * (-n[0]) + Vector((0, 0, -n[1]))).normalized()
                    rows.append((mw @ from_uv(u, z, CHAMFER / 2), (rot @ Nm).normalized()))
                else:
                    rows.append(None)
            if all(r is not None for r in rows):
                segs.append(rows)
                continue
            k = next(i for i, r in enumerate(rows) if r is None)
            rows = rows[k:] + rows[:k]  # start at a gap so no run wraps the loop start
            cur = []
            for r in rows + [None]:
                if r is None:
                    if len(cur) > 2:
                        segs.append(cur)
                    cur = []
                else:
                    cur.append(r)
        return segs


# ------------------------------------------------------------------ materials
def _attr(nodes, name):
    a = nodes.new("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    return a


def mat_section_carbon(name="SectionCarbon", lo=0.010, hi=0.022, r_pol=0.09, r_sat=0.17, speck=0.2):
    """Polished cut face of a carbon laminate. Face attribute `tone` (0..1): ply value; tone > 0.5 marks a
    polished woven ply (roughness r_pol), tone <= 0.5 a satin UD/resin ply (r_sat). The alternation reads as
    fine striations in the satin reflection; fibre-end speckle on top."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    tone = _attr(nodes, "tone")
    col = nodes.new("ShaderNodeMapRange")
    col.inputs["To Min"].default_value = lo
    col.inputs["To Max"].default_value = hi
    links.new(tone.outputs["Fac"], col.inputs["Value"])
    tc = nodes.new("ShaderNodeTexCoord")
    vor = nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 9000.0
    links.new(tc.outputs["Object"], vor.inputs["Vector"])
    sp = nodes.new("ShaderNodeMapRange")
    sp.inputs["To Min"].default_value = 1.0 - speck
    sp.inputs["To Max"].default_value = 1.0 + speck
    links.new(vor.outputs["Distance"], sp.inputs["Value"])
    mul = nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    links.new(col.outputs["Result"], mul.inputs[0])
    links.new(sp.outputs["Result"], mul.inputs[1])
    comb = nodes.new("ShaderNodeCombineColor")
    for k in range(3):
        links.new(mul.outputs[0], comb.inputs[k])
    links.new(comb.outputs[0], b.inputs["Base Color"])
    step = nodes.new("ShaderNodeMath")
    step.operation = "GREATER_THAN"
    step.inputs[1].default_value = 0.5
    links.new(tone.outputs["Fac"], step.inputs[0])
    rr = nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = r_sat
    rr.inputs["To Max"].default_value = r_pol
    links.new(step.outputs[0], rr.inputs["Value"])
    links.new(rr.outputs["Result"], b.inputs["Roughness"])
    bp = nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 1.0
    bp.inputs["Distance"].default_value = 0.000006
    links.new(tone.outputs["Fac"], bp.inputs["Height"])
    links.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value = 0.7
    return m


def mat_chamfer(name="Chamfer"):
    """The 45 deg polished chamfer on the cut edge: black mirror lacquer."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.02, 0.02, 0.021, 1)
    b.inputs["Roughness"].default_value = 0.06
    b.inputs["Specular IOR Level"].default_value = 0.7
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.02
    b.inputs["Coat IOR"].default_value = 1.52
    return m


def mat_foam(name="Foam", color=(0.56, 0.51, 0.42), cell_mm=0.5, bump=1.2, mottle=0.035, rough_cell=0.85,
             rough_wall=0.28, sss=0.35, sss_mm=0.6, wall_w=0.10, open_pores=False, pore_dark=0.0, spec=0.45):
    """Cut cellular foam. Closed-cell (K03 core): halved cells as shallow cups whose thin walls stand proud and
    are smoother (micro-specular under a grazing key), plus sub-surface scattering. open_pores (K03b EVA): the
    cells are darker open pores, matte."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes["Principled BSDF"]
    tc = nodes.new("ShaderNodeTexCoord")
    vor = nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 1.0 / (cell_mm / 1000.0)
    vor.inputs["Randomness"].default_value = 0.95
    links.new(tc.outputs["Object"], vor.inputs["Vector"])
    # wall mask: 1 on the cell walls, 0 in the cell floors
    wm = nodes.new("ShaderNodeMapRange")
    wm.inputs["From Min"].default_value = 0.0
    wm.inputs["From Max"].default_value = wall_w
    wm.interpolation_type = "SMOOTHSTEP"
    wm.inputs["To Min"].default_value = 1.0
    wm.inputs["To Max"].default_value = 0.0
    links.new(vor.outputs["Distance"], wm.inputs["Value"])
    # cup profile: height rises toward the wall
    cup = nodes.new("ShaderNodeMapRange")
    cup.inputs["From Min"].default_value = 0.0
    cup.inputs["From Max"].default_value = 0.5
    cup.interpolation_type = "SMOOTHERSTEP"
    cup.inputs["To Min"].default_value = 1.0
    cup.inputs["To Max"].default_value = 0.0
    links.new(vor.outputs["Distance"], cup.inputs["Value"])
    bp = nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = cell_mm / 1000.0 * 0.3
    links.new(cup.outputs["Result"], bp.inputs["Height"])
    links.new(bp.outputs["Normal"], b.inputs["Normal"])
    nz = nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 140.0
    nz.inputs["Detail"].default_value = 4.0
    links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 1.0 - mottle
    mr.inputs["To Max"].default_value = 1.0 + mottle
    links.new(nz.outputs["Fac"], mr.inputs["Value"])
    # value: walls a touch brighter (or pores darker for open-cell EVA)
    val = nodes.new("ShaderNodeMapRange")
    if open_pores:
        val.inputs["To Min"].default_value = 1.0 - pore_dark
        val.inputs["To Max"].default_value = 1.04
    else:
        val.inputs["To Min"].default_value = 0.88
        val.inputs["To Max"].default_value = 1.10
    links.new(wm.outputs["Result"], val.inputs["Value"])
    f1 = nodes.new("ShaderNodeMath")
    f1.operation = "MULTIPLY"
    links.new(mr.outputs["Result"], f1.inputs[0])
    links.new(val.outputs["Result"], f1.inputs[1])
    mix = nodes.new("ShaderNodeVectorMath")
    mix.operation = "SCALE"
    mix.inputs[0].default_value = color
    links.new(f1.outputs[0], mix.inputs["Scale"])
    links.new(mix.outputs[0], b.inputs["Base Color"])
    rg = nodes.new("ShaderNodeMapRange")
    rg.inputs["To Min"].default_value = rough_cell
    rg.inputs["To Max"].default_value = rough_wall
    links.new(wm.outputs["Result"], rg.inputs["Value"])
    links.new(rg.outputs["Result"], b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = spec
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.78, 0.55)
        b.inputs["Subsurface Scale"].default_value = sss_mm / 1000.0
    return m


def face_carbon(o):
    """The racket's 3K lacquered carbon for the outer face, tuned for this cutaway: softer weave bump and a lower
    base specular so the sharp clear-coat reflection carries the gloss sweep (the bumpy base would smear any
    gradient into a flat grey wash)."""
    m = soften_bump(racket.mat_carbon("Carbon_3k", tow_mm=2.6, kind="3k"), fopt(o, "weave_bump", 0.30))
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Specular IOR Level"].default_value = fopt(o, "face_spec", 0.05)
    b.inputs["Metallic"].default_value = fopt(o, "face_metal", 0.05)
    b.inputs["Coat Roughness"].default_value = fopt(o, "face_coat_rough", 0.035)
    # the clear coat is smooth over the weave: its normal is the unbumped shading normal
    geo = m.node_tree.nodes.new("ShaderNodeNewGeometry")
    m.node_tree.links.new(geo.outputs["Normal"], b.inputs["Coat Normal"])
    if o.get("face_dbg"):
        for nd in list(m.node_tree.nodes):
            if nd.type == "BUMP":
                m.node_tree.nodes.remove(nd)
        for l in list(m.node_tree.links):
            if l.to_node == b and l.to_socket.name == "Roughness":
                m.node_tree.links.remove(l)
        b.inputs["Roughness"].default_value = 0.5
    return m


def soften_bump(mat, strength):
    for nd in mat.node_tree.nodes:
        if nd.type == "BUMP":
            nd.inputs["Strength"].default_value = strength
    return mat


EMBER = (1.0, 0.18, 0.08)       # #ff3a1e-family ember under AgX: the glue colour of the G07 drawings
RESIN = (0.40, 0.20, 0.05)
SHELL_AMBER = (1.0, 0.48, 0.14)  # 2700 K amber, a touch more saturated than the blackbody so AgX keeps it amber     # cured amber-brown epoxy


def mat_glue(name="Glue", strength=0.0, color=EMBER, base=RESIN):
    """Adhesive layer: cured amber-brown resin, slightly glossy; `strength` > 0 makes it glow ember."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = 0.22
    b.inputs["Specular IOR Level"].default_value = 0.7
    b.inputs["Coat Weight"].default_value = 0.5
    b.inputs["Coat Roughness"].default_value = 0.1
    if strength:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def mat_void(name="GlueVoid"):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.004, 0.003, 0.002, 1)
    b.inputs["Roughness"].default_value = 0.6
    return m


# ------------------------------------------------------------------ emitters
def _emit_mat(name, strength, color=(1, 1, 1), blackbody=None, attr=None):
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    if blackbody:
        bb = nt.nodes.new("ShaderNodeBlackbody")
        bb.inputs["Temperature"].default_value = blackbody
        nt.links.new(bb.outputs[0], em.inputs["Color"])
    else:
        em.inputs["Color"].default_value = (*color, 1)
    if attr:
        at = nt.nodes.new("ShaderNodeAttribute")
        at.attribute_type = "GEOMETRY"
        at.attribute_name = attr
        mu = nt.nodes.new("ShaderNodeMath")
        mu.operation = "MULTIPLY"
        mu.inputs[1].default_value = strength
        nt.links.new(at.outputs["Fac"], mu.inputs[0])
        nt.links.new(mu.outputs[0], em.inputs["Strength"])
    else:
        em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m, em


def reflect_only(ob):
    """Emitter seen only in reflections: invisible to camera, adds no diffuse light, casts no shadow."""
    ob.visible_camera = False
    ob.visible_diffuse = False
    ob.visible_shadow = False
    ob.visible_transmission = False
    ob.visible_volume_scatter = False
    return ob


def card(name, loc, size, strength, target, color=(1, 1, 1), falloff="soft", edge=0.5, blackbody=None, roll=0.0,
         flip=False, diffuse=False, edge0=0.0):
    """Emissive card, invisible to camera and shadow-free. falloff: 'flat' | 'soft' (centre-bright across width,
    fading along length) | 'edge' (bright from edge0 to edge0+edge fading out across X). diffuse=False: reflections only."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    studio.aim(ob, target)
    if roll:
        ob.rotation_euler = (ob.rotation_euler.to_matrix() @ Matrix.Rotation(math.radians(roll), 3, "Z")).to_euler()
    m, em = _emit_mat(name, strength, color, blackbody)
    nodes, links = m.node_tree.nodes, m.node_tree.links
    if falloff != "flat":
        tc = nodes.new("ShaderNodeTexCoord")
        sep = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tc.outputs["Generated"], sep.inputs["Vector"])
        if falloff == "soft":
            cx = nodes.new("ShaderNodeMath"); cx.operation = "SUBTRACT"; cx.inputs[1].default_value = 0.5
            links.new(sep.outputs["X"], cx.inputs[0])
            ab = nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"
            links.new(cx.outputs[0], ab.inputs[0])
            f1 = nodes.new("ShaderNodeMapRange")
            f1.inputs["From Max"].default_value = 0.5
            f1.inputs["To Min"].default_value = 1.0
            f1.inputs["To Max"].default_value = 0.0
            f1.interpolation_type = "SMOOTHSTEP"
            links.new(ab.outputs[0], f1.inputs["Value"])
            cy = nodes.new("ShaderNodeMath"); cy.operation = "SUBTRACT"; cy.inputs[1].default_value = 0.5
            links.new(sep.outputs["Y"], cy.inputs[0])
            aby = nodes.new("ShaderNodeMath"); aby.operation = "ABSOLUTE"
            links.new(cy.outputs[0], aby.inputs[0])
            f2 = nodes.new("ShaderNodeMapRange")
            f2.inputs["From Min"].default_value = 0.25
            f2.inputs["From Max"].default_value = 0.5
            f2.inputs["To Min"].default_value = 1.0
            f2.inputs["To Max"].default_value = 0.0
            f2.interpolation_type = "SMOOTHSTEP"
            links.new(aby.outputs[0], f2.inputs["Value"])
            mul = nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
            links.new(f1.outputs["Result"], mul.inputs[0])
            links.new(f2.outputs["Result"], mul.inputs[1])
            g = mul.outputs[0]
        else:
            f1 = nodes.new("ShaderNodeMapRange")
            a0 = edge0
            f1.inputs["From Min"].default_value = (1.0 - a0) if flip else a0
            f1.inputs["From Max"].default_value = (1.0 - a0 - edge) if flip else (a0 + edge)
            f1.inputs["To Min"].default_value = 1.0
            f1.inputs["To Max"].default_value = 0.0
            f1.interpolation_type = "SMOOTHERSTEP"
            links.new(sep.outputs["X"], f1.inputs["Value"])
            # soft ends along the card length
            cy = nodes.new("ShaderNodeMath"); cy.operation = "SUBTRACT"; cy.inputs[1].default_value = 0.5
            links.new(sep.outputs["Y"], cy.inputs[0])
            aby = nodes.new("ShaderNodeMath"); aby.operation = "ABSOLUTE"
            links.new(cy.outputs[0], aby.inputs[0])
            f2 = nodes.new("ShaderNodeMapRange")
            f2.inputs["From Min"].default_value = 0.3
            f2.inputs["From Max"].default_value = 0.5
            f2.inputs["To Min"].default_value = 1.0
            f2.inputs["To Max"].default_value = 0.0
            f2.interpolation_type = "SMOOTHSTEP"
            links.new(aby.outputs[0], f2.inputs["Value"])
            mul = nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
            links.new(f1.outputs["Result"], mul.inputs[0])
            links.new(f2.outputs["Result"], mul.inputs[1])
            g = mul.outputs[0]
        st = nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = strength
        links.new(g, st.inputs[0])
        links.new(st.outputs[0], em.inputs["Strength"])
    ob.data.materials.append(m)
    ob.visible_camera = False
    ob.visible_shadow = False
    if not diffuse:
        reflect_only(ob)
    return reg(ob)


def dir_loc(target, az_deg, el_deg, dist):
    """Point at distance from target: az measured from -Y (toward camera side) toward +X, el above XY."""
    az, el = math.radians(az_deg), math.radians(el_deg)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return tuple(Vector(target) + d * dist)


def mirror_dir(P, N, cam):
    d = (Vector(P) - Vector(cam)).normalized()
    if d.dot(N) >= 0:
        return None
    return d - 2 * d.dot(N) * N


def mirror_ribbon(name, segs, cam_loc, dist=1.0, width=0.015, strength=10.0, color=(1, 1, 1), blackbody=None,
                  gain=None, max_gap=0.25, gate_mm=None):
    """Emissive ribbon on the mirror rays of surface points: the camera sees ONE line tracing them.
    segs: list of [(P_world, N_world), ...]; gain(P, N, r) -> per-point emission multiplier. Reflection-only."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    kl = bm.verts.layers.float.new("k")
    rl = [bm.verts.layers.float.new(n) for n in ("rx", "ry", "rz")]
    pl = [bm.verts.layers.float.new(n) for n in ("px", "py", "pz")]
    cam = Vector(cam_loc)
    for seg in segs:
        rows = []
        for (P, N) in seg:
            r = mirror_dir(P, N, cam)
            if r is None:
                continue
            k = gain(P, N, r) if gain else 1.0
            rows.append((Vector(P) + r * dist, r, k, Vector(P)))
        prev = None
        for j, (Q, r, k, P0) in enumerate(rows):
            if j + 1 < len(rows):
                t = rows[j + 1][0] - Q
            elif j > 0:
                t = Q - rows[j - 1][0]
            else:
                continue
            if t.length < 1e-9:
                continue
            side = t.cross(r).normalized() * (width / 2)
            a = bm.verts.new(Q + side)
            b = bm.verts.new(Q - side)
            a[kl] = b[kl] = k
            for c in range(3):
                a[rl[c]] = b[rl[c]] = r[c]
                a[pl[c]] = b[pl[c]] = P0[c]
            if prev and (Q - rows[j - 1][0]).length < max_gap:
                bm.faces.new((prev[0], prev[1], b, a))
            prev = (a, b)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    m, em = _emit_mat(name, strength, color, blackbody, attr="k")
    if gate_mm:
        # emit only toward rays that START on the designed frame-edge point (ray origin = position + incoming *
        # ray length, within gate_mm of it): the line on the frame radius lights up, the weave of the face and the
        # hole lips (which also see the ribbon) stay clean
        nodes, links = m.node_tree.nodes, m.node_tree.links
        cmb = nodes.new("ShaderNodeCombineXYZ")
        for c, n in zip(("X", "Y", "Z"), ("px", "py", "pz")):
            at = nodes.new("ShaderNodeAttribute")
            at.attribute_type = "GEOMETRY"
            at.attribute_name = n
            links.new(at.outputs["Fac"], cmb.inputs[c])
        geo = nodes.new("ShaderNodeNewGeometry")
        lp = nodes.new("ShaderNodeLightPath")
        sc_ = nodes.new("ShaderNodeVectorMath"); sc_.operation = "SCALE"
        links.new(geo.outputs["Incoming"], sc_.inputs[0])
        links.new(lp.outputs["Ray Length"], sc_.inputs["Scale"])
        org = nodes.new("ShaderNodeVectorMath"); org.operation = "ADD"
        links.new(geo.outputs["Position"], org.inputs[0])
        links.new(sc_.outputs[0], org.inputs[1])
        ds = nodes.new("ShaderNodeVectorMath"); ds.operation = "DISTANCE"
        links.new(org.outputs[0], ds.inputs[0])
        links.new(cmb.outputs[0], ds.inputs[1])
        mr = nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = gate_mm / 1000.0
        mr.inputs["From Max"].default_value = gate_mm / 2000.0
        mr.interpolation_type = "SMOOTHSTEP"
        links.new(ds.outputs["Value"], mr.inputs["Value"])
        st_link = [l for l in links if l.to_node == em and l.to_socket.name == "Strength"][0]
        src = st_link.from_socket
        links.remove(st_link)
        mu = nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"
        links.new(src, mu.inputs[0])
        links.new(mr.outputs["Result"], mu.inputs[1])
        links.new(mu.outputs[0], em.inputs["Strength"])
    me.materials.append(m)
    reflect_only(ob)
    return reg(ob)


def frame_corner_points(alpha_deg, frame_r=0.011, per=200, alpha_fn=None):
    """World points + normals on the head's frame radius at angle alpha from the top face, for the outline beyond
    the cut (model outline transformed by cut_matrix)."""
    pts = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, per)
    if racket._area(pts) < 0:
        pts.reverse()
    n = len(pts)
    mw = cut_matrix()
    rot = mw.to_3x3()
    rows = []
    for i in range(n):
        x, y = pts[i]
        P2 = Vector((x, y, 0))
        if (P2 - CUT_P0).dot(CUT_N) < CHAMFER + 0.0004:
            rows.append(None)
            continue
        ax, ay = pts[i - 1]
        bx, by = pts[(i + 1) % n]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1.0
        nx, ny = ty / ln, -tx / ln  # outward (CCW)
        a_deg = alpha_fn(x, y) if alpha_fn else alpha_deg
        al = math.radians(a_deg)
        cx, cy = x - nx * frame_r, y - ny * frame_r
        cz = HALF_T - frame_r
        P = Vector((cx + nx * frame_r * math.sin(al), cy + ny * frame_r * math.sin(al), cz + frame_r * math.cos(al)))
        N = Vector((nx * math.sin(al), ny * math.sin(al), math.cos(al)))
        rows.append((mw @ P, (rot @ N).normalized()))
    # split into contiguous runs (rotate so a run does not wrap the array end)
    if rows[0] is not None and rows[-1] is not None:
        k = next(i for i, r in enumerate(rows) if r is None)
        rows = rows[k:] + rows[:k]
    segs, cur = [], []
    for r in rows:
        if r is None:
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append(r)
    if cur:
        segs.append(cur)
    return segs


def link_receivers(light_ob, objs, name):
    col = bpy.data.collections.new(name)
    for o in objs:
        col.objects.link(o)
    light_ob.light_linking.receiver_collection = col
    return col


# ------------------------------------------------------------------ rounded head (own builder)
def outline_ccw(per=160):
    outline = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, per)
    if racket._area(outline) < 0:
        outline.reverse()
    n = len(outline)
    onrm = []
    for i in range(n):
        ax, ay = outline[i - 1]
        bx, by = outline[(i + 1) % n]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1.0
        onrm.append((ty / ln, -tx / ln))  # outward (CCW)
    return outline, onrm


def build_rounded_head(name="KQ_Round", frame_r=0.011, lip=0.0011, seg_frame=14, seg_lip=6, hole_n=72, per=160,
                       hole_mat=0):
    """Same silhouette and holes as racket.build_head, lofted from offset rings so the frame edge has a
    true circular radius (racket.build_head's frame bevel clamps to zero width) and the hole rims a lip."""
    outline, onrm = outline_ccw(per)
    hr = racket.HOLE_R * racket.U
    holes = [(hx * racket.U, hy * racket.U) for (hx, hy) in racket.holes()]
    zt = HALF_T

    def o_inset(z):
        zc = zt - frame_r
        dz = abs(z) - zc
        return frame_r - math.sqrt(max(frame_r * frame_r - dz * dz, 0.0)) if dz > 0 else 0.0

    def h_exp(z):
        zc = zt - lip
        dz = abs(z) - zc
        return lip - math.sqrt(max(lip * lip - dz * dz, 0.0)) if dz > 0 else 0.0

    zs = set()
    for k in range(seg_frame + 1):
        zs.add(round(zt - frame_r + frame_r * math.cos(math.radians(90.0 * k / seg_frame)), 9))
    for k in range(seg_lip + 1):
        zs.add(round(zt - lip + lip * math.cos(math.radians(90.0 * k / seg_lip)), 9))
    # extra levels through the core so the bore walls and side walls are not single long quads
    for k in range(1, 6):
        zs.add(round((zt - frame_r) * k / 6.0, 9))
    top = sorted(zs, reverse=True)
    levels = sorted(set(top + [-z for z in zs if z > 1e-9] + [0.0]), reverse=True)

    bm = bmesh.new()
    rings_o, rings_h = [], [[] for _ in holes]
    for z in levels:
        d = o_inset(z)
        rings_o.append([bm.verts.new((x - nx * d, y - ny * d, z)) for (x, y), (nx, ny) in zip(outline, onrm)])
        e = h_exp(z)
        for hi, (hx, hy) in enumerate(holes):
            rr = hr + e
            rings_h[hi].append([bm.verts.new((hx + rr * math.cos(2 * math.pi * k / hole_n),
                                              hy + rr * math.sin(2 * math.pi * k / hole_n), z)) for k in range(hole_n)])

    def stitch(rings):
        for a, b in zip(rings[:-1], rings[1:]):
            m = len(a)
            for i in range(m):
                j = (i + 1) % m
                bm.faces.new((a[i], a[j], b[j], b[i]))

    stitch(rings_o)
    nf0 = len(bm.faces)
    for rh in rings_h:
        stitch(rh)
    bm.faces.ensure_lookup_table()
    for f in bm.faces[nf0:]:
        f.material_index = hole_mat

    def fill(loops, mi=0):
        tris = tessellate_polygon([[Vector((v.co.x, v.co.y, 0)) for v in lp] for lp in loops])
        flat = [v for lp in loops for v in lp]
        for (a, b, c) in tris:
            try:
                f = bm.faces.new((flat[a], flat[b], flat[c]))
                f.material_index = mi
            except ValueError:
                pass

    nf1 = len(bm.faces)
    for li in (0, len(levels) - 1):
        fill([rings_o[li]] + [rh[li] for rh in rings_h])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    # the flat faces keep exact +-Z normals (no tilt bleeding in from the frame radius / lips): the clear-coat
    # reflection across the face then stays a true mirror
    bm.faces.ensure_lookup_table()
    caps = set(bm.faces[nf1:])
    for f in caps:
        for e in f.edges:
            if any(g not in caps for g in e.link_faces):
                e.smooth = False
    me = bpy.data.meshes.new(name)
    for _ in range(hole_mat + 1):
        me.materials.append(None)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    wn = ob.modifiers.new("wn", "WEIGHTED_NORMAL")
    wn.mode = "FACE_AREA"
    wn.weight = 100
    wn.keep_sharp = True
    racket._apply_all(ob)
    return ob


def build_tube_cavity(name, tube_w=0.016, wall=0.002, frame_r=0.011, inner_r=0.003, seg=12, per=160):
    """Void of a conventional hollow frame tube running round the outline (model space). Normals face into
    the void."""
    outline, onrm = outline_ccw(per)
    zt = HALF_T
    Ro, Ri = frame_r - wall, inner_r - wall

    def o_c(z):
        dz = abs(z) - (zt - frame_r)
        return wall + (Ro - math.sqrt(max(Ro * Ro - dz * dz, 0.0)) if dz > 0 else 0.0)

    def i_c(z):
        dz = abs(z) - (zt - inner_r)
        return tube_w - wall - ((Ri - math.sqrt(max(Ri * Ri - dz * dz, 0.0))) if dz > 0 else 0.0)

    zs = set()
    for k in range(seg + 1):
        a = math.radians(90.0 * k / seg)
        zs.add(round(zt - frame_r + Ro * math.cos(a), 9))
        zs.add(round(zt - inner_r + Ri * math.cos(a), 9))
    zs = {z for z in zs if z <= zt - wall + 1e-9}
    levels = sorted(set(list(zs) + [-z for z in zs]), reverse=True)
    bm = bmesh.new()
    R_out, R_in = [], []
    for z in levels:
        a, b = o_c(z), i_c(z)
        R_out.append([bm.verts.new((x - nx * a, y - ny * a, z)) for (x, y), (nx, ny) in zip(outline, onrm)])
        R_in.append([bm.verts.new((x - nx * b, y - ny * b, z)) for (x, y), (nx, ny) in zip(outline, onrm)])
    for rings in (R_out, R_in):
        for A, B in zip(rings[:-1], rings[1:]):
            m = len(A)
            for i in range(m):
                j = (i + 1) % m
                bm.faces.new((A[i], A[j], B[j], B[i]))
    for li in (0, len(levels) - 1):
        loops = [R_out[li], R_in[li]]
        tris = tessellate_polygon([[Vector((v.co.x, v.co.y, 0)) for v in lp] for lp in loops])
        flat = [v for lp in loops for v in lp]
        for (a, b, c) in tris:
            try:
                bm.faces.new((flat[a], flat[b], flat[c]))
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) > 0:  # face into the void
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def bisect_open(ob):
    """Remove everything in front of the cut plane without capping; return the open loops in (u, z)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=CUT_P0, plane_no=CUT_N, clear_inner=True)
    loops = Section._boundary_loops(bm)
    loops2d = [[to_uv(v.co) for v in lp] for lp in loops]
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    ob.matrix_world = cut_matrix()
    return loops2d


# ------------------------------------------------------------------ floor
def build_floor(size=8.0):
    """Dark satin floor #151517 (roughness 0.25). It is lit only by its own floor-linked lights, receives the
    piece's soft contact shadow and reflects the piece; it is invisible to the piece's own glossy and shadow rays,
    so the reflection-only cards below floor level still draw on the polished section."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0.6, FLOOR_Z))
    fl = bpy.context.active_object
    fl.name = "Floor"
    m = bpy.data.materials.new("FloorMat")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    b = nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.0075, 0.0075, 0.0085, 1)
    b.inputs["Specular IOR Level"].default_value = 0.75
    tc = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 6.0
    links.new(tc.outputs["Object"], noise.inputs["Vector"])
    rmap = nodes.new("ShaderNodeMapRange")
    rmap.inputs["To Min"].default_value = 0.22
    rmap.inputs["To Max"].default_value = 0.29
    links.new(noise.outputs["Fac"], rmap.inputs["Value"])
    links.new(rmap.outputs["Result"], b.inputs["Roughness"])
    fl.data.materials.append(m)
    fl.visible_glossy = False
    fl.visible_shadow = False
    return fl


# ------------------------------------------------------------------ shared K03 / K03b camera and lights
CAM_AZ, CAM_EL, CAM_D = 30.0, 24.0, 1.76
CAM_TARGET = (0.0, 0.04, 0.0)
CAM_LOC = tuple(Vector(dir_loc(CAM_TARGET, CAM_AZ, CAM_EL, CAM_D)))
CAM_SHIFT = (0.001, 0.004)


def k03_camera(shift=None):
    cam = studio.camera(CAM_LOC, CAM_TARGET, lens=100, fstop=11, shift=shift or CAM_SHIFT)
    cam.data.dof.focus_distance = (Vector(CAM_LOC) - Vector((0, 0.01, 0))).length  # the section plane
    return cam


def frame_bbox(objs):
    """Normalized camera-frame bbox (x0, x1, y0_top, y1_top) of the objects' vertices."""
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    sc = bpy.context.scene
    cam = sc.camera
    xs, ys = [], []
    for ob in objs:
        mw = ob.matrix_world
        for v in ob.data.vertices:
            c = world_to_camera_view(sc, cam, mw @ v.co)
            xs.append(c.x)
            ys.append(1.0 - c.y)
    return min(xs), max(xs), min(ys), max(ys)


def k03_floor_lights(floor, o=None):
    """Floor-only lights: a soft overhead sun (base lift to luma ~18 at the frame edges, soft contact shadow) and
    a low soft disc above-behind the piece (the graphite glow behind the section)."""
    o = o or {}
    sun_d = bpy.data.lights.new("floor_base", "SUN")
    sun_d.energy = fopt(o, "floor_base", 12.0)
    sun_d.angle = math.radians(fopt(o, "sun_angle", 40.0))
    sun = bpy.data.objects.new("floor_base", sun_d)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(fopt(o, "sun_tilt", 8.0)), 0, 0)
    link_receivers(sun, [floor], "rx_floor_base")
    reg(sun)
    pool_xyz = (fopt(o, "pool_x", -0.03), fopt(o, "pool_y", 0.14), FLOOR_Z + fopt(o, "pool_h", 0.45))
    pool = studio.spot_light("floor_pool", pool_xyz, fopt(o, "pool", 100.0), fopt(o, "pool_cone", 70.0),
                             blend=fopt(o, "pool_blend", 1.0), color=(0.93, 0.95, 1.0),
                             target=(pool_xyz[0], pool_xyz[1], FLOOR_Z), radius=fopt(o, "pool_r", 0.08))
    pool.visible_camera = False
    pool.visible_glossy = False
    link_receivers(pool, [floor], "rx_floor_pool")
    reg(pool)
    return sun, pool


def sweep_card(name, cam_loc, dist=2.0, size=(1.6, 0.6), strength=2.5, d0=0.01, d1=0.12, slant=0.35, gamma=1.0):
    """Gloss sweep for the outer face beyond the cut (normal +Z). The card sits on the face's mirror vector; its
    emission is a gradient in 'face depth from the cut' (+ a lateral slant toward the far-left), fitted by least
    squares from the mirror mapping of sample face points onto the card. So the lacquer sheen rises from near-black
    at the cut to its peak toward the far edge, along a diagonal parallel to the cut line. Reflection-only."""
    cam = Vector(cam_loc)
    Pf = Vector((0.0, 0.065, HALF_T))
    r0 = mirror_dir(Pf, Vector((0, 0, 1)), cam)
    C = Pf + r0 * dist
    bpy.ops.mesh.primitive_plane_add(size=1, location=tuple(C))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    studio.aim(ob, tuple(Pf))
    bpy.context.view_layer.update()
    inv = ob.matrix_world.inverted()
    nrm = (ob.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    # sample face points beyond the cut (world), map to card object coords
    outline = racket._loop(racket.HEAD_START, racket.HEAD_CURVES, 120)
    mw = cut_matrix()
    poly = Polygon([tuple((mw @ Vector((x, y, 0)))[:2]) for (x, y) in outline])
    rows, ys, xs = [], [], []
    for xi in np.linspace(-0.14, 0.14, 29):
        for yi in np.linspace(0.002, 0.16, 25):
            if not poly.contains(Polygon([(xi - 1e-4, yi), (xi + 1e-4, yi), (xi, yi + 1e-4)])):
                continue
            P = Vector((xi, yi, HALF_T))
            r = mirror_dir(P, Vector((0, 0, 1)), cam)
            t = (C - P).dot(nrm) / r.dot(nrm)
            q = inv @ (P + r * t)
            rows.append((q.x, q.y, 1.0))
            ys.append(yi)
            xs.append(xi)
    A = np.array(rows)
    cy = np.linalg.lstsq(A, np.array(ys), rcond=None)[0]
    cx = np.linalg.lstsq(A, np.array(xs), rcond=None)[0]
    m, em = _emit_mat(name, strength)
    nodes, links = m.node_tree.nodes, m.node_tree.links
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sep.inputs[0])

    def lin(c, scale):
        a = nodes.new("ShaderNodeMath"); a.operation = "MULTIPLY_ADD"
        a.inputs[1].default_value = c[0] * scale
        a.inputs[2].default_value = c[2] * scale
        links.new(sep.outputs["X"], a.inputs[0])
        b = nodes.new("ShaderNodeMath"); b.operation = "MULTIPLY_ADD"
        b.inputs[1].default_value = c[1] * scale
        links.new(sep.outputs["Y"], b.inputs[0])
        links.new(a.outputs[0], b.inputs[2])
        return b.outputs[0]
    # s = depth - slant * x  (metres): brighter far and toward the left
    sd = lin(cy, 1.0)
    sx = lin(cx, -slant)
    add = nodes.new("ShaderNodeMath"); add.operation = "ADD"
    links.new(sd, add.inputs[0]); links.new(sx, add.inputs[1])
    g = nodes.new("ShaderNodeMapRange")
    g.inputs["From Min"].default_value = d0
    g.inputs["From Max"].default_value = d1
    g.interpolation_type = "SMOOTHSTEP"
    links.new(add.outputs[0], g.inputs["Value"])
    pw = nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = gamma
    links.new(g.outputs["Result"], pw.inputs[0])
    st = nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = strength
    links.new(pw.outputs[0], st.inputs[0])
    links.new(st.outputs[0], em.inputs["Strength"])
    ob.data.materials.append(m)
    reflect_only(ob)
    print("sweep fit residual mm", round(1000 * float(np.sqrt(np.mean((A @ cy - np.array(ys)) ** 2))), 2))
    return reg(ob)


def k03_lights(racket_objs, floor, shell=False, chamfer_segs=None, o=None):
    """Identical rig for K03 and K03b (shell=True adds lg_shell, K03 full only)."""
    o = o or {}
    O = (0.0, 0.0, 0.0)
    cam = Vector(CAM_LOC)
    # lg_key: hard grazing strip, top-left, ~12 deg to the section plane; close, so it falls off left to right
    key = studio.area_light("lg_key", (fopt(o, "key_x", -0.75), fopt(o, "key_y", -0.075), fopt(o, "key_z", 0.38)),
                            fopt(o, "key_len", 0.30), fopt(o, "key", 52.0), size_y=0.012, target=(0.0, 0, 0))
    key.data.color = (1.0, 0.985, 0.96)
    link_receivers(key, racket_objs, "rx_key")
    reg(key)
    # fill: dim soft card high camera-right keeps the far end of the section from sinking
    f = card("fill", dir_loc(O, 55, 35, 1.2), (0.5, 0.3), fopt(o, "fill", 1.5), O, falloff="soft", diffuse=True)
    link_receivers(f, racket_objs, "rx_fill")
    # lg_top: soft top strip at ~10 %
    t = card("lg_top", (0.0, -0.25, 1.1), (0.9, 0.12), fopt(o, "top", 0.30), O, falloff="soft", diffuse=True)
    link_receivers(t, racket_objs, "rx_top")
    # satin: at the cut face's mirror direction (below floor level; the floor is invisible to glossy rays):
    # the polished section reflects it as a dark satin glow; polished and satin plies separate into striations
    sat_el = -CAM_EL
    card("satin", dir_loc(O, -CAM_AZ, sat_el, 1.5), (fopt(o, "satin_w", 1.1), fopt(o, "satin_h", 0.16)),
         fopt(o, "satin", 1.8), O, falloff="soft")
    # bores: tall narrow strip front-right at the hole walls' mirror direction -> one vertical line per bore
    card("bore", dir_loc(O, 62, -15, 1.0), (0.04, 0.7), fopt(o, "bore", 4.0), O, falloff="flat")
    # sweep: big edge-gradient card on the outer face's mirror vector (face normal +Z): a slanted lacquer sheen that
    # rises from near-black at the cut to bright toward the far edge. Linked to the piece only (not the floor).
    sw = sweep_card("sweep", CAM_LOC, dist=fopt(o, "sweep_d", 2.0), strength=fopt(o, "sweep", 0.8),
                    d0=fopt(o, "sweep_d0", 0.0), d1=fopt(o, "sweep_d1", 0.10), slant=fopt(o, "sweep_slant", 0.2),
                    gamma=fopt(o, "sweep_gamma", 1.0))
    link_receivers(sw, racket_objs, "rx_sweep")
    # far rim: low strip far behind, grazes the visible top of the tip curve
    card("rim_far", dir_loc((0.0, 0.03, 0.0), 185, 4, 1.4), (1.6, 0.02), fopt(o, "rim", 6.0), (0.0, 0.03, 0.0),
         falloff="flat")
    # lg_line: hot white ribbon on the mirror rays of the 45 deg chamfer along the outer cut edge
    if chamfer_segs:
        mirror_ribbon("lg_line", chamfer_segs, CAM_LOC, dist=fopt(o, "line_d", 0.9), width=fopt(o, "line_w", 0.05),
                      strength=fopt(o, "line", 90.0), color=(1.0, 0.99, 0.97))
    if shell:
        add_shell(o)
    # every reflection card/ribbon lights the piece only: the satin floor must not mirror them
    rx = None
    for ob in LIGHTS:
        if ob.type == "MESH" and ob.light_linking.receiver_collection is None:
            if rx is None:
                rx = link_receivers(ob, racket_objs, "rx_piece")
            else:
                ob.light_linking.receiver_collection = rx
    k03_floor_lights(floor, o)


def add_shell(o):
    """lg_shell: amber 2700 K line tracing the frame's outer curve beyond the cut, from the left side wall over the
    tip to the right side wall; per-point gain flattens Fresnel so the line stays even. Light group 'shell'."""
    a0 = fopt(o, "shell_alpha", 12.0)
    ar = fopt(o, "shell_alpha_r", 24.0)

    def alpha_fn(x, y):
        return a0 + (ar - a0) * min(1.0, max(0.0, x / 0.12)) ** 2

    segs = frame_corner_points(a0, alpha_fn=alpha_fn)
    cam = Vector(CAM_LOC)
    f0 = 0.043

    # measured evenness correction along the curve (world x of the point): the middle of the tip reads weakest
    xs = [-0.13, -0.06, 0.0, 0.05, 0.09, 0.13]
    ks = [fopt(o, "shell_kl", 1.3), 1.7, fopt(o, "shell_km", 2.2), 1.9, 1.1, fopt(o, "shell_kr", 0.6)]

    def even(x):
        if x <= xs[0]:
            return ks[0]
        for i in range(len(xs) - 1):
            if x <= xs[i + 1]:
                t = (x - xs[i]) / (xs[i + 1] - xs[i])
                return ks[i] + (ks[i + 1] - ks[i]) * t
        return ks[-1]

    def gain(P, N, r):
        c = max(0.0, -(Vector(P) - cam).normalized().dot(N))
        fr = f0 + (1 - f0) * (1 - c) ** 5
        return min(1.5, (0.12 / fr) ** fopt(o, "shell_flat", 0.8)) * even(Vector(P).x)

    rib = mirror_ribbon("lg_shell", segs, CAM_LOC, dist=fopt(o, "shell_d", 2.5), width=fopt(o, "shell_w", 0.8),
                        strength=fopt(o, "shell", 22.0), color=SHELL_AMBER, gain=gain, max_gap=0.6,
                        gate_mm=fopt(o, "shell_gate", 6.0))
    vl = bpy.context.view_layer
    if "shell" not in [g.name for g in vl.lightgroups]:
        vl.lightgroups.add(name="shell")
    rib.lightgroup = "shell"
    return rib


def shell_glow(o):
    """Compositor: fog glow (threshold 0.9) on the lg_shell light-group pass only, added onto the image."""
    sc = bpy.context.scene
    sc.use_nodes = True
    sc.render.use_compositing = True
    nt = sc.node_tree
    rl = nt.nodes.get("Render Layers") or nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.get("Composite") or nt.nodes.new("CompositorNodeComposite")
    sock = None
    for s in rl.outputs:
        if "shell" in s.name:
            sock = s
    if sock is None:
        print("WARN: no shell light-group socket", [s.name for s in rl.outputs])
        return
    gl = nt.nodes.new("CompositorNodeGlare")
    gl.glare_type = "FOG_GLOW"
    gl.quality = "HIGH"
    gl.threshold = fopt(o, "glow_thr", 0.9)
    gl.size = int(fopt(o, "glow_size", 6))
    gl.mix = 1.0
    nt.links.new(sock, gl.inputs[0])
    sc_ = nt.nodes.new("CompositorNodeMixRGB")
    sc_.blend_type = "MULTIPLY"
    sc_.inputs[0].default_value = 1.0
    g = fopt(o, "glow", 1.6)
    sc_.inputs[2].default_value = (g, g, g, 1)
    nt.links.new(gl.outputs[0], sc_.inputs[1])
    add = nt.nodes.new("CompositorNodeMixRGB")
    add.blend_type = "ADD"
    add.inputs[0].default_value = 1.0
    nt.links.new(rl.outputs["Image"], add.inputs[1])
    nt.links.new(sc_.outputs[0], add.inputs[2])
    nt.links.new(add.outputs[0], comp.inputs["Image"])


# ------------------------------------------------------------------ one render, both variants
def assign_groups(glow_objs, glow_group):
    """Light groups: everything that emits goes to 'rest' except glow_objs (-> glow_group). The base variant is
    then the denoised 'rest' pass of the very same render, so base and full register exactly."""
    vl = bpy.context.view_layer
    for g in ("rest", glow_group):
        if g not in [x.name for x in vl.lightgroups]:
            vl.lightgroups.add(name=g)
    for ob in bpy.context.scene.objects:
        if ob.type in ("LIGHT", "MESH"):
            ob.lightgroup = glow_group if ob in glow_objs else "rest"
    bpy.context.scene.world.lightgroup = "rest"
    vl.cycles.denoising_store_passes = True


def both_variants(o, glow_group, base_path, glow_on_full=False):
    """Compositor: Composite = full (the denoised image, + fog glow of the glow group if glow_on_full);
    File Output = base (OIDN-denoised 'rest' light-group pass) written as `base_path`."""
    sc = bpy.context.scene
    sc.use_nodes = True
    sc.render.use_compositing = True
    nt = sc.node_tree
    rl = nt.nodes.get("Render Layers") or nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.get("Composite") or nt.nodes.new("CompositorNodeComposite")
    out = {s.name: s for s in rl.outputs}
    dn = nt.nodes.new("CompositorNodeDenoise")
    dn.prefilter = "ACCURATE"
    dn.use_hdr = True
    nt.links.new(out["Combined_rest"], dn.inputs["Image"])
    nt.links.new(out["Denoising Normal"], dn.inputs["Normal"])
    nt.links.new(out["Denoising Albedo"], dn.inputs["Albedo"])
    fo = nt.nodes.new("CompositorNodeOutputFile")
    d, fn = os.path.split(base_path)
    fo.base_path = d + os.sep
    fo.file_slots[0].path = fn + "_####"
    fo.format.file_format = "PNG"
    fo.format.color_depth = "16"
    fo.format.color_mode = "RGB"
    nt.links.new(dn.outputs[0], fo.inputs[0])
    if glow_on_full:
        gl = nt.nodes.new("CompositorNodeGlare")
        gl.glare_type = "FOG_GLOW"
        gl.quality = "HIGH"
        gl.threshold = fopt(o, "glow_thr", 0.9)
        gl.size = int(fopt(o, "glow_size", 6))
        gl.mix = 1.0
        nt.links.new(out["Combined_" + glow_group], gl.inputs[0])
        mul = nt.nodes.new("CompositorNodeMixRGB")
        mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        g = fopt(o, "glow", 1.6)
        mul.inputs[2].default_value = (g, g, g, 1)
        nt.links.new(gl.outputs[0], mul.inputs[1])
        add = nt.nodes.new("CompositorNodeMixRGB")
        add.blend_type = "ADD"
        add.inputs[0].default_value = 1.0
        nt.links.new(out["Image"], add.inputs[1])
        nt.links.new(mul.outputs[0], add.inputs[2])
        nt.links.new(add.outputs[0], comp.inputs["Image"])
    else:
        nt.links.new(out["Image"], comp.inputs["Image"])
    return fo


def finish_both(o, name):
    """Render once, write <name>-full.png (Composite) and <name>-base.png (File Output), both dithered."""
    full = out_path(name + "-full")
    base = out_path(name + "-base")
    sc = bpy.context.scene
    sc.frame_current = 1
    if o.get("crop"):
        x0, x1, y0, y1 = [float(v) for v in str(o["crop"]).split(",")]
        r = sc.render
        r.use_border = True
        r.use_crop_to_border = True
        r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = x0, x1, y0, y1
    render_to(full, dither=not o.get("nodither"))
    tmp = base[:-4] + "_0001.png"
    if os.path.exists(tmp):
        os.replace(tmp, base)
        if not o.get("nodither"):
            dither_png16(base)
    else:
        print("WARN: base file output missing", tmp)
    return full, base
