"""K03 v4 shared geometry and materials (owned by the K03 artist): a machined coupon cut from the racket's edge.
v5 materials (white Command, owner 2026-10-22; geometry unchanged): see "white Command" below face_carbon(). Default
white; o["white"] = 0 gives the v4 black materials exactly.

v4 (after the stage-3 review of v3): the front cut runs through the CENTRE of one outer-row bore, (67.5, 6.5), so the
polished face starts at the lined half-bore (no land left of it: the face is one closed shell loop, bore lining / top
skin / side wall / bottom skin) and runs 54.9 mm to the side wall. The inner cut leaves the bore centre at 102 deg
(facing away from the camera) and the back cut sits at y = 66.0 mm, so two complete outer-row holes, (81.0, 30.0) and
(67.5, 53.5), are moulded into the top face at the true 27 mm pitch. Hole mouths have a 0.6 mm radius in both stills.
Materials: optically flat plies (albedo + roughness only), a flush graphite closed-cell core (no bump), a 3K 2/2
twill under a satin coat with anisotropic per-tow sheen, a glossy moulded bore lining and a matte graphite floor.

Every natural edge of a cut has a 0.15 mm 45 deg polished chamfer (cut-to-cut edges stay square). Sections are capped
with exact 2D regions (shapely) computed from the NATURAL section of the uncut head at that plane (plies are offsets of
the true surface, never of a cut edge), clipped to the cap, then noded into one planar graph (no T-junctions, no
cracks). Per-vertex attributes for the section shaders: d (depth below the true surface, m), pc/ps (cos/sin of the
phase along the surface, period 4 tows); per-face d0/t (ply depth and thickness) and pv (per-ply variation).
"""
import bisect as _bisect
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
import shapely  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.geometry import tessellate_polygon  # noqa: E402
from shapely.geometry import LineString, Point, Polygon, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402
import k03_lib as L  # noqa: E402

MM = 0.001
HALF_T = racket.THICK / 2
FRAME_R = 0.011
LIP = 0.0006           # moulded hole-mouth radius (K03b drills the same mouth, so the stills register)
CHAMFER = 0.00015
SEG = 0.00025          # max boundary segment on a cap (keeps attribute interpolation exact)
TOW = 2.1 * MM         # 3K tow width in the 2/2 twill
TOW_P4 = 4 * TOW       # phase period: four tows (a 2/2 twill repeat)

# v4 coupon: the front cut runs through the centre of the bore (67.5, 6.5) of the outer zigzag row, so the face starts
# at the lined bore (no land left of it) and runs 54.9 mm to the side wall. The inner (left) cut leaves the bore centre
# at 102 deg (it faces away from the camera) and the back cut sits 59.5 mm behind the face, so two COMPLETE outer-row
# holes, (81.0, 30.0) and (67.5, 53.5), are moulded into the top face at the true 27 mm pitch.
BORE = (0.0675, 0.0065)
COUPON_HOLES = [BORE, (0.081, 0.030), (0.0675, 0.0535)]
Y_FRONT = 0.0065
Y_BACK = 0.0660
INNER_P = BORE
INNER_DIR = (-math.sin(math.radians(12.0)), math.cos(math.radians(12.0)))
PIECE_OFFSET = Vector((0.10114, Y_FRONT, 0.0))  # model -> world translation: world origin = middle of the face span
FLOOR_GAP = 0.0001
FLOOR_Z = -HALF_T - FLOOR_GAP


# ------------------------------------------------------------------ cuts
class Cut:
    """Vertical cutting plane. N points into the KEPT side; T = N x Z is the in-plane u axis."""

    def __init__(self, name, p0, n):
        self.name = name
        self.P0 = Vector((p0[0], p0[1], 0.0))
        self.N = Vector((n[0], n[1], 0.0)).normalized()
        self.T = self.N.cross(Vector((0, 0, 1))).normalized()
        self.natural = []

    def to_uv(self, co):
        return ((co - self.P0).dot(self.T), co.z)

    def from_uv(self, u, z, off=0.0):
        return self.P0 + self.T * u + self.N * off + Vector((0.0, 0.0, z))


def coupon_cuts():
    nx, ny = INNER_DIR[1], -INNER_DIR[0]  # right of the corridor direction: toward the side wall
    return [Cut("inner", INNER_P, (nx, ny)), Cut("back", (0.0, Y_BACK), (0.0, -1.0)), Cut("front", (0.0, Y_FRONT), (0.0, 1.0))]


def front_cut(cuts):
    return [c for c in cuts if c.name == "front"][0]


# ------------------------------------------------------------------ head
def outline_ccw(per):
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
        onrm.append((ty / ln, -tx / ln))
    return outline, onrm


def build_head(name="KQ_Head", holes=COUPON_HOLES, frame_r=FRAME_R, lip=LIP, seg_frame=28, seg_lip=10, hole_n=160,
               per=240, hole_mat=0):
    """Head lofted from offset rings (true circular frame radius, lipped holes), only the holes the coupon needs."""
    outline, onrm = outline_ccw(per)
    hr = racket.HOLE_R * racket.U
    zt = HALF_T

    def o_inset(z):
        dz = abs(z) - (zt - frame_r)
        return frame_r - math.sqrt(max(frame_r * frame_r - dz * dz, 0.0)) if dz > 0 else 0.0

    def h_exp(z):
        dz = abs(z) - (zt - lip)
        return lip - math.sqrt(max(lip * lip - dz * dz, 0.0)) if dz > 0 else 0.0

    zs = set()
    for k in range(seg_frame + 1):
        zs.add(round(zt - frame_r + frame_r * math.cos(math.radians(90.0 * k / seg_frame)), 9))
    for k in range(seg_lip + 1):
        zs.add(round(zt - lip + lip * math.cos(math.radians(90.0 * k / seg_lip)), 9))
    for k in range(1, 8):
        zs.add(round((zt - frame_r) * k / 8.0, 9))
    levels = sorted(set(list(zs) + [-z for z in zs if z > 1e-9] + [0.0]), reverse=True)

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
                bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))

    stitch(rings_o)
    nf0 = len(bm.faces)
    for rh in rings_h:
        stitch(rh)
    bm.faces.ensure_lookup_table()
    for f in bm.faces[nf0:]:
        f.material_index = hole_mat
    nf1 = len(bm.faces)
    for li in (0, len(levels) - 1):
        loops = [rings_o[li]] + [rh[li] for rh in rings_h]
        tris = tessellate_polygon([[Vector((v.co.x, v.co.y, 0)) for v in lp] for lp in loops])
        flat = [v for lp in loops for v in lp]
        for (a, b, c) in tris:
            try:
                bm.faces.new((flat[a], flat[b], flat[c]))
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.faces.ensure_lookup_table()
    caps = set(bm.faces[nf1:])
    for f in caps:
        for e in f.edges:
            if any(g not in caps for g in e.link_faces):
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def outline_line(per=240):
    o, _ = outline_ccw(per)
    return LineString(o + [o[0]])


# ------------------------------------------------------------------ 2D helpers
def polys_of(g):
    return L.polys_of(g)


def largest(g):
    ps = polys_of(g)
    return max(ps, key=lambda p: p.area) if ps else None


def halfplane(u0, keep_greater, big=1.0):
    return sbox(u0, -big, u0 + big, big) if keep_greater else sbox(u0 - big, -big, u0, big)


def side_walls(cut, NP, tol=0.0006):
    """Which ends of a natural section are the racket's side wall: [(u_wall, sg)], sg=+1 if the wall is at max u."""
    ol = outline_line()
    out = []
    u0, _, u1, _ = NP.bounds
    for (u, sg) in ((u1, 1), (u0, -1)):
        P = cut.from_uv(u, 0.0)
        if ol.distance(Point(P.x, P.y)) < tol:
            out.append((u, sg))
    return out


def natural_sections(me, cut, chamfer):
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=cut.P0 + cut.N * chamfer, plane_no=cut.N, clear_inner=True)
    loops = L.Section._boundary_loops(bm)
    out = []
    for lp in loops:
        p = Polygon([cut.to_uv(v.co) for v in lp])
        if not p.is_valid:
            p = largest(p.buffer(0))
        if p is not None and p.area > 1e-8:
            out.append(p)
    bm.free()
    return out


# ------------------------------------------------------------------ carving
GRID = 1e-9


def planar(regs, A, seg):
    """Turn overlapping-edge region polygons into ONE noded planar subdivision (shared vertices everywhere, no
    T-junctions, no holes): snap to a 1 nm grid, densify, add seam lines through any hole, node all rings,
    polygonize, give each face the region that holds it."""
    snapped = []
    for (p, mi, at) in regs:
        q = shapely.set_precision(p, GRID)
        for qq in polys_of(q):
            snapped.append((qq, mi, at))
    base = []
    for (p, _, _) in snapped:
        for r in [p.exterior] + list(p.interiors):
            base.append(LineString(r.coords).segmentize(seg))
    base.append(LineString(list(A.exterior.coords)).segmentize(seg))
    u0, z0, u1, z1 = A.bounds
    seams_u = [round((u0 + u1) / 2, 9)]
    for _ in range(6):
        seams = [LineString([(su, z0 - 0.001), (su, z1 + 0.001)]).segmentize(seg) for su in seams_u]
        noded = shapely.union_all(base + seams, grid_size=GRID)  # snap-rounding noder: consistent on the grid
        faces = [f for f in shapely.polygonize(list(getattr(noded, "geoms", [noded]))).geoms if f.area > 1e-14]
        holes = [f for f in faces if len(f.interiors) and A.contains(f.representative_point())]
        if not holes:
            break
        for f in holes:
            for r in f.interiors:
                seams_u.append(round(Polygon(r).representative_point().x, 9))
    out = []
    lost = 0.0
    for f in faces:
        rp = f.representative_point()
        if not A.contains(rp):
            continue
        hit = None
        for (p, mi, at) in snapped:
            if p.contains(rp):
                hit = (mi, at)
                break
        if hit is None:
            best = min(snapped, key=lambda r: r[0].distance(rp))
            hit = (best[1], best[2])
            lost += f.area
        if hit[0] is None or hit[0] < 0:
            continue  # a declared hole (e.g. the tube void): left open
        out.append((f, hit[0], hit[1]))
    if lost > 1e-10:
        print("planar: %.3g mm2 of unassigned slivers given to nearest region" % (lost * 1e6))
    return out


def _on_plane(v, c, off):
    return abs((v.co - c.P0).dot(c.N) - off) < 1e-6


def plane_loops(bm, c, off):
    """Closed loops of open edges lying on cut plane c (offset off); other open edges (cap holes) are ignored."""
    adj = {}
    for e in bm.edges:
        if e.is_boundary and _on_plane(e.verts[0], c, off) and _on_plane(e.verts[1], c, off):
            a, b = e.verts
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    seen, loops = set(), []
    for st in adj:
        if st in seen:
            continue
        lp, prev, cur = [st], None, st
        seen.add(st)
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


def _densify_open(bm, max_len, c=None, off=0.0):
    groups = {}
    for e in bm.edges:
        if e.is_boundary and (c is None or (_on_plane(e.verts[0], c, off) and _on_plane(e.verts[1], c, off))):
            n = int(e.calc_length() / max_len)
            if n >= 1:
                groups.setdefault(min(n, 600), []).append(e)
    for n, es in groups.items():
        bmesh.ops.subdivide_edges(bm, edges=es, cuts=n, use_grid_fill=False)


class Carver:
    """Cuts a head with several vertical planes in order; each opening gets a 45 deg chamfer strip and a cap of
    region polygons from regions_fn(cut, NP, A) -> [(poly, mat_index, {d0, t, pv}), ...]."""

    def __init__(self, head, cuts, regions_fn, materials, chamfer=CHAMFER, chamfer_mat=None, seg=SEG):
        self.head, self.cuts, self.ch, self.seg = head, cuts, chamfer, seg
        me = head.data
        for c in cuts:
            c.natural = natural_sections(me, c, chamfer)
        bm = bmesh.new()
        bm.from_mesh(me)
        self.L_d = bm.verts.layers.float.new("d")
        self.L_pc = bm.verts.layers.float.new("pc")
        self.L_ps = bm.verts.layers.float.new("ps")
        self.L_d0 = bm.faces.layers.float.new("d0")
        self.L_t = bm.faces.layers.float.new("t")
        self.L_pv = bm.faces.layers.float.new("pv")
        self.L_tone = bm.faces.layers.float.new("tone")
        mats = list(materials)
        self.ch_idx = len(mats)
        mats.append(chamfer_mat or L.mat_chamfer())
        self.caps = []
        self.fill_err = 0
        weld = []
        for c in cuts:
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=c.P0 + c.N * chamfer, plane_no=c.N, clear_inner=True)
            _densify_open(bm, seg, c, chamfer)
            loops = plane_loops(bm, c, chamfer)
            print("cut", c.name, "loops", len(loops), [len(lp) for lp in loops])
            for lp in loops:
                weld += self._cap(bm, c, lp, regions_fn)
            bmesh.ops.remove_doubles(bm, verts=list(set(v for v in weld if v.is_valid)), dist=1e-11)
            weld = []
            nb = sum(1 for e in bm.edges if e.is_boundary)
            nm = sum(1 for e in bm.edges if len(e.link_faces) > 2)
            print("  after", c.name, "open edges", nb, "non-manifold", nm)
        bm.normal_update()
        bm.faces.ensure_lookup_table()
        strip = set(f for f in bm.faces if f.material_index == self.ch_idx)
        for f in bm.faces:
            if f in strip:
                f.smooth = True
                continue
            for c in cuts:
                if f.normal.dot(-c.N) > 0.999 and abs((f.calc_center_median() - c.P0).dot(c.N)) < 1e-6:
                    f.smooth = False
                    for e in f.edges:
                        e.smooth = False
        for f in strip:
            for e in f.edges:
                if any(g not in strip for g in e.link_faces):
                    e.smooth = False
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
        head.matrix_world = Matrix.Translation(-PIECE_OFFSET)
        self.obj = head

    def _cap(self, bm, c, lp, regions_fn):
        ch = self.ch
        uv = [c.to_uv(v.co) for v in lp]
        raw = Polygon(uv)
        if not raw.is_valid:
            raw = largest(raw.buffer(0))
        cands = [q for q in c.natural if q.intersects(raw)]
        NP = max(cands, key=lambda q: q.intersection(raw).area) if cands else raw
        ringN = NP.exterior
        # chamfer only where the loop runs on the racket's own surface; edges on an earlier cut stay square
        nat = shapely.distance(shapely.points(np.array(uv)), ringN) < 1e-7
        inw = L.loop_normals(uv)
        ins = [(round(p[0] + n[0] * ch * k, 9), round(p[1] + n[1] * ch * k, 9)) for p, n, k in zip(uv, inw, nat)]
        A = Polygon(ins)
        if not A.is_valid:
            print("WARN invalid cap ring on", c.name, shapely.is_valid_reason(A))
            A = largest(A.buffer(0))
        regs = planar(regions_fn(c, NP, A), A, self.seg * 1.2)
        self.caps.append((c.name, NP, A, regs))
        table = {}

        def V(u, z):
            key = (round(u, 9), round(z, 9))
            v = table.get(key)
            if v is None:
                v = bm.verts.new(c.from_uv(u, z))
                table[key] = v
            return v

        # region vertices on the cap ring that are not ring vertices: split the chamfer strip there (no T-junctions)
        m = len(ins)
        ring = LineString(ins + [ins[0]])
        seglen = [math.dist(ins[i], ins[(i + 1) % m]) for i in range(m)]
        cum = [0.0]
        for sl in seglen:
            cum.append(cum[-1] + sl)
        allpts = []
        for (p, _, _) in regs:
            allpts += list(p.exterior.coords)[:-1]
        extra = {}
        if allpts:
            arr = np.array(allpts)
            dist = shapely.distance(shapely.points(arr), ring)
            seen = set((round(x, 9), round(z, 9)) for (x, z) in ins)
            done = set()
            for (x, z) in arr[dist < 2e-9]:
                key = (round(x, 9), round(z, 9))
                if key in seen or key in done:
                    continue
                done.add(key)
                sp = ring.project(Point(x, z))
                i = min(max(_bisect.bisect_right(cum, sp) - 1, 0), m - 1)
                if seglen[i] < 1e-12:
                    continue
                t = (sp - cum[i]) / seglen[i]
                if t * seglen[i] < 1e-9 or (1 - t) * seglen[i] < 1e-9:
                    continue
                extra.setdefault(i, []).append((t, (x, z)))
        outer, inner_v = [], []
        for i in range(m):
            j = (i + 1) % m
            outer.append(lp[i])
            inner_v.append(V(*ins[i]))
            if i in extra:
                last, tl = lp[i], 0.0
                for (t, (x, z)) in sorted(extra[i]):
                    e = bm.edges.get((last, lp[j]))
                    if e is None:
                        print("WARN lost strip edge")
                        break
                    fac = (t - tl) / (1.0 - tl)
                    _, vnew = bmesh.utils.edge_split(e, last, fac)
                    outer.append(vnew)
                    inner_v.append(V(x, z))
                    last, tl = vnew, t
        n2 = len(outer)
        for i in range(n2):
            j = (i + 1) % n2
            q = [outer[i], outer[j], inner_v[j], inner_v[i]]
            if len(set(q)) < 4:
                q = list(dict.fromkeys(q))
                if len(q) < 3:
                    continue
            try:
                f = bm.faces.new(q)
            except ValueError:
                continue
            f.material_index = self.ch_idx
            f[self.L_tone] = 1.0
            f.normal_update()
            mid_in = (inner_v[i].co + inner_v[j].co) / 2
            mid_out = (outer[i].co + outer[j].co) / 2
            expect = (mid_out - mid_in) - c.N * ch * 2  # outward and toward the removed side
            if f.normal.dot(expect) < 0:
                f.normal_flip()
        nper = max(1, round(ringN.length / TOW_P4))
        per = ringN.length / nper
        new_faces = []
        for (p, mi, at) in regs:
            new_faces += self._fill(bm, c, p, mi, at, V)
        res = bmesh.ops.triangulate(bm, faces=[f for f in new_faces if f.is_valid and len(f.verts) > 3],
                                    quad_method="BEAUTY", ngon_method="BEAUTY")
        cap_edges = set()
        for f in [f for f in new_faces if f.is_valid] + list(res.get("faces", [])):
            if f.is_valid:
                cap_edges.update(f.edges)
        bmesh.ops.dissolve_degenerate(bm, dist=2e-8, edges=[e for e in cap_edges if e.is_valid])
        table = {k: v for k, v in table.items() if v.is_valid}
        vs = list(table.values())
        arr = np.array([c.to_uv(v.co) for v in vs])
        pts = shapely.points(arr)
        sv = shapely.line_locate_point(ringN, pts)
        dv = shapely.distance(ringN, pts)
        for v, dd, sp in zip(vs, dv, sv):
            a = 2 * math.pi * sp / per
            v[self.L_d] = float(dd)
            v[self.L_pc] = math.cos(a)
            v[self.L_ps] = math.sin(a)
        return vs

    def _fill(self, bm, c, poly, mi, at, V):
        ring = list(poly.exterior.coords)[:-1]
        if len(ring) < 3:
            return []
        vs = [V(u, z) for (u, z) in ring]
        if len(set(vs)) != len(vs):
            vs = list(dict.fromkeys(vs))
        try:
            f = bm.faces.new(vs)
        except ValueError as e:
            self.fill_err += 1
            print("  fill failed:", e, len(vs))
            return []
        f.normal_update()
        if f.normal.dot(c.N) > 0:
            f.normal_flip()
        f.material_index = mi
        f[self.L_d0] = at.get("d0", 0.0)
        f[self.L_t] = at.get("t", 1.0)
        f[self.L_pv] = at.get("pv", 0.0)
        return [f]

    def chamfer_line(self, cut_name="front", z_min=-1.0, skip=None):
        """World points + normals along the middle of the chamfer on a cut's OUTER (natural-surface) edges.
        skip(u, z) -> True drops a point (e.g. the bore walls)."""
        mw = self.obj.matrix_world
        rot = mw.to_3x3()
        c = [k for k in self.cuts if k.name == cut_name][0]
        segs = []
        for (name, NP, A, regs) in self.caps:
            if name != cut_name:
                continue
            ring = NP.exterior
            pts = L._clean(A.exterior.coords)
            inw = L.loop_normals(pts)
            rows = []
            for (q, n) in zip(pts, inw):
                u, z = q[0] - n[0] * self.ch / 2, q[1] - n[1] * self.ch / 2
                natural = ring.distance(Point(q)) < self.ch * 1.5
                if natural and z > z_min and not (skip and skip(u, z)):
                    Nm = (-c.N + c.T * (-n[0]) + Vector((0, 0, -n[1]))).normalized()
                    rows.append((mw @ c.from_uv(u, z, self.ch / 2), (rot @ Nm).normalized()))
                else:
                    rows.append(None)
            if all(r is not None for r in rows):
                segs.append(rows)
                continue
            k = next(i for i, r in enumerate(rows) if r is None)
            rows = rows[k:] + rows[:k]
            cur = []
            for r in rows + [None]:
                if r is None:
                    if len(cur) > 2:
                        segs.append(cur)
                    cur = []
                else:
                    cur.append(r)
        return segs


# ------------------------------------------------------------------ world helpers
def to_world(p):
    return Vector(p) - PIECE_OFFSET


def frame_bbox(objs):
    return L.frame_bbox(objs)


# ------------------------------------------------------------------ tiny shader-node DSL
class NB:
    """Node builder: NB(mat) then b.attr('d'), b.math('MULTIPLY', a, 2.0), b.mix(...). Values are sockets or floats."""

    def __init__(self, mat, clear=True):
        self.m = mat
        mat.use_nodes = True
        self.nt = mat.node_tree
        self.nodes, self.links = self.nt.nodes, self.nt.links
        if clear:
            for nd in list(self.nodes):
                self.nodes.remove(nd)
        self.out = self.nodes.new("ShaderNodeOutputMaterial")
        self._tc = None

    def _set(self, inp, v):
        if v is None:
            return
        if isinstance(v, (int, float)):
            inp.default_value = v
        elif isinstance(v, (tuple, list)):
            inp.default_value = v if len(v) == len(inp.default_value) else (*v, 1.0)
        else:
            self.links.new(v, inp)

    def attr(self, name):
        a = self.nodes.new("ShaderNodeAttribute")
        a.attribute_type = "GEOMETRY"
        a.attribute_name = name
        return a.outputs["Fac"]

    def tc(self, kind="Object"):
        if self._tc is None:
            self._tc = self.nodes.new("ShaderNodeTexCoord")
        return self._tc.outputs[kind]

    def math(self, op, a, b=None, c=None, clamp=False):
        n = self.nodes.new("ShaderNodeMath")
        n.operation = op
        n.use_clamp = clamp
        for i, v in enumerate((a, b, c)):
            self._set(n.inputs[i], v)
        return n.outputs[0]

    def add(self, a, b):
        return self.math("ADD", a, b)

    def sub(self, a, b):
        return self.math("SUBTRACT", a, b)

    def mul(self, a, b):
        return self.math("MULTIPLY", a, b)

    def div(self, a, b):
        return self.math("DIVIDE", a, b)

    def mad(self, a, b, c):
        return self.math("MULTIPLY_ADD", a, b, c)

    def clamp01(self, a):
        return self.math("ADD", a, 0.0, clamp=True)

    def remap(self, v, a0, a1, b0=0.0, b1=1.0, interp="LINEAR", clamp=True):
        n = self.nodes.new("ShaderNodeMapRange")
        n.interpolation_type = interp
        n.clamp = clamp
        self._set(n.inputs["Value"], v)
        self._set(n.inputs["From Min"], a0)
        self._set(n.inputs["From Max"], a1)
        self._set(n.inputs["To Min"], b0)
        self._set(n.inputs["To Max"], b1)
        return n.outputs["Result"]

    def smooth(self, e0, e1, v):
        return self.remap(v, e0, e1, 0.0, 1.0, "SMOOTHSTEP")

    def lerp(self, a, b, t):
        # a + (b - a) t
        return self.mad(self.sub(b, a), t, a)

    def vec(self, x, y, z):
        n = self.nodes.new("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self._set(n.inputs[i], v)
        return n.outputs[0]

    def sep(self, v):
        n = self.nodes.new("ShaderNodeSeparateXYZ")
        self._set(n.inputs[0], v)
        return n.outputs["X"], n.outputs["Y"], n.outputs["Z"]

    def vmath(self, op, a, b=None, scale=None):
        n = self.nodes.new("ShaderNodeVectorMath")
        n.operation = op
        self._set(n.inputs[0], a)
        if b is not None:
            self._set(n.inputs[1], b)
        if scale is not None:
            self._set(n.inputs["Scale"], scale)
        return n.outputs["Value"] if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else n.outputs["Vector"]

    def noise(self, vec, scale, detail=2.0, rough=0.5, dims="3D", w=None):
        n = self.nodes.new("ShaderNodeTexNoise")
        n.noise_dimensions = dims
        self._set(n.inputs["Vector"], vec)
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        if w is not None and "W" in n.inputs:
            self._set(n.inputs["W"], w)
        return n.outputs["Fac"]

    def voronoi(self, vec, scale, feature="F1", rand=1.0, out="Distance"):
        n = self.nodes.new("ShaderNodeTexVoronoi")
        n.feature = feature
        self._set(n.inputs["Vector"], vec)
        n.inputs["Scale"].default_value = scale
        n.inputs["Randomness"].default_value = rand
        return n.outputs[out]

    def rgb(self, v):
        n = self.nodes.new("ShaderNodeCombineColor")
        for i in range(3):
            self._set(n.inputs[i], v)
        return n.outputs[0]

    def tint(self, v, color):
        return self.vmath("MULTIPLY", self.vec(v, v, v), color)

    def bsdf(self, base=None, rough=None, spec=0.5, coat=0.0, coat_rough=0.05, normal=None, metal=0.0, emit=None,
             emit_strength=None, aniso=None):
        b = self.nodes.new("ShaderNodeBsdfPrincipled")
        self._set(b.inputs["Base Color"], base)
        self._set(b.inputs["Roughness"], rough)
        self._set(b.inputs["Specular IOR Level"], spec)
        self._set(b.inputs["Metallic"], metal)
        self._set(b.inputs["Coat Weight"], coat)
        self._set(b.inputs["Coat Roughness"], coat_rough)
        if normal is not None:
            self._set(b.inputs["Normal"], normal)
        if emit is not None:
            self._set(b.inputs["Emission Color"], emit)
            self._set(b.inputs["Emission Strength"], emit_strength)
        if aniso is not None:
            self._set(b.inputs["Anisotropic"], aniso)
        return b

    def bump(self, height, strength, dist):
        n = self.nodes.new("ShaderNodeBump")
        self._set(n.inputs["Height"], height)
        n.inputs["Strength"].default_value = strength
        n.inputs["Distance"].default_value = dist
        return n.outputs["Normal"]

    def mix_shader(self, fac, a, b):
        n = self.nodes.new("ShaderNodeMixShader")
        self._set(n.inputs[0], fac)
        self.links.new(a.outputs[0] if hasattr(a, "outputs") else a, n.inputs[1])
        self.links.new(b.outputs[0] if hasattr(b, "outputs") else b, n.inputs[2])
        return n

    def output(self, shader):
        self.links.new(shader.outputs[0] if hasattr(shader, "outputs") else shader, self.out.inputs["Surface"])
        return self.m


# ------------------------------------------------------------------ section materials
def _depth_frac(b):
    """dd: 0 at the ply's outer boundary, 1 at its inner boundary."""
    return b.clamp01(b.div(b.sub(b.attr("d"), b.attr("d0")), b.attr("t")))


def _phase01(b, mult=1.0):
    """Phase along the surface in [0, 1) for one TOW_P4 period (x mult, must be an integer)."""
    ang = b.math("ARCTAN2", b.attr("ps"), b.attr("pc"))
    x = b.mad(ang, 1.0 / (2 * math.pi), 0.5)
    if mult != 1.0:
        x = b.math("FRACT", b.mul(x, mult))
    return x


def mat_ply(kind, o=None, tone=1.0, keep_z=None):
    """Polished section of one ply: optically FLAT (no normal perturbation), told apart by albedo and roughness only.
    tw   : 3K twill. Weft tows cut across = long low lenses (fibre ends: a touch darker and duller) along the ply, the
           warp tow weaving over two and under two: a faint periodic tow-crossover beading.
    ud0  : unidirectional, fibres in the cut plane: the smoothest, brightest sheen (the hairline glints).
    ud90 : unidirectional, fibres crossing the cut: fibre ends, a fine dull grain.
    resin: resin-rich interlayer or surface: a thin glossy black line.
    White Command (default; --white 0 gives the black v4): the OUTER twill ply is the white face ply, so its section is
    a white hairline round the shell (white fibre ends in clear resin, same lens beading); every inner ply stays carbon.
    keep_z: depth below the face (m) where the white ply ends down a lined bore (K03: LIP + TUCK); None = no bore rule.
    """
    o = o or {}
    if white_on(o):
        m = mat_ply(kind, dict(o, white=0), tone)
        m.name = "PlyW_" + kind
        b = NB(m, clear=False)
        extra = b.out  # NB adds an output node: drop it and use the dark material's own
        b.out = next(n for n in b.nodes if n.type == "OUTPUT_MATERIAL" and n != extra)
        b.nodes.remove(extra)
        dark = b.out.inputs["Surface"].links[0].from_socket
        W = _white_zone(b, kind, keep_z)
        mx = b.nodes.new("ShaderNodeMixShader")
        b.links.new(W, mx.inputs[0])
        b.links.new(dark, mx.inputs[1])
        b.links.new(_white_section(b, o, kind).outputs[0], mx.inputs[2])
        b.links.new(mx.outputs[0], b.out.inputs["Surface"])
        return m
    m = bpy.data.materials.new("Ply_" + kind)
    b = NB(m)
    pv = b.attr("pv")
    var = b.mad(pv, 0.10, 0.95)  # +-5 % per ply
    p = b.tc("Object")
    grain = b.remap(b.noise(p, 30000.0, 0.0), 0.3, 0.7, 0.85, 1.15)  # fibre-end grain, about a pixel
    if kind == "tw":
        dd = _depth_frac(b)
        x4 = _phase01(b)
        x1 = b.math("FRACT", b.mul(x4, 4.0))
        over = b.smooth(-0.4, 0.4, b.math("SINE", b.mul(b.sub(x4, 0.125), 2 * math.pi)))
        cen = b.lerp(0.33, 0.67, over)
        e = b.div(b.sub(x1, 0.5), 0.47)
        hh = b.mul(b.math("SQRT", b.clamp01(b.sub(1.0, b.mul(e, e)))), 0.28)
        dist = b.math("ABSOLUTE", b.sub(dd, cen))
        lens = b.sub(1.0, b.smooth(b.sub(hh, 0.06), hh, dist))
        aw, al = L.fopt(o, "tw_warp", 0.022) * tone, L.fopt(o, "tw_lens", 0.016) * tone
        alb = b.mul(b.lerp(aw, al, lens), b.mul(var, b.lerp(1.0, grain, lens)))
        rough = b.lerp(L.fopt(o, "tw_rw", 0.32), L.fopt(o, "tw_rl", 0.42), lens)
        sh = b.bsdf(base=b.rgb(alb), rough=rough, spec=L.fopt(o, "tw_spec", 0.35))
    elif kind == "ud0":
        st = b.remap(b.noise(b.vmath("MULTIPLY", p, (90.0, 90.0, 6000.0)), 1.0, 2.0), 0.3, 0.7, 0.93, 1.07)
        sh = b.bsdf(base=b.rgb(b.mul(b.mul(var, st), L.fopt(o, "ud0_alb", 0.030) * tone)), rough=L.fopt(o, "ud0_r", 0.07),
                    spec=L.fopt(o, "ud0_spec", 0.7))
    elif kind == "ud90":
        sh = b.bsdf(base=b.rgb(b.mul(b.mul(var, grain), L.fopt(o, "ud90_alb", 0.018) * tone)),
                    rough=L.fopt(o, "ud90_r", 0.40), spec=0.35)
    elif kind == "resin":
        sh = b.bsdf(base=(0.005, 0.005, 0.0055), rough=L.fopt(o, "resin_r", 0.18), spec=L.fopt(o, "resin_spec", 0.3))
    else:
        raise ValueError(kind)
    return b.output(sh)


def mat_core(o=None, name="CoreFoam"):
    """Polished closed-cell structural foam, dark graphite. The cut is flush (NO bump or normal relief): the cells,
    0.3-0.5 mm, are drawn with albedo and roughness only, slightly brighter thin walls around darker, duller cell
    interiors with a little per-cell tone. A light polish coat carries the softbox gradient that shapes the face."""
    o = o or {}
    # v6 white only (art director, optional): next to the white skin the cut read as one flat black panel at page
    # size, so the closed cells get more contrast (brighter walls, darker interiors, more per-cell tone) at the SAME
    # mean (core_alb trimmed to hold it: the cut-face probes stay put). --white 0: v4's values exactly.
    wk = white_on(o)
    D = dict(cell_hi=2.1, cell_lo=0.62, cell_var=0.36, core_alb=0.033) if wk else \
        dict(cell_hi=1.55, cell_lo=0.78, cell_var=0.22, core_alb=0.036)
    m = bpy.data.materials.new(name)
    b = NB(m)
    p = b.tc("Object")
    cell = L.fopt(o, "cell_mm", 0.40) / 1000.0
    alb = L.fopt(o, "core_alb", D["core_alb"])
    warp = b.vmath("ADD", p, b.vmath("SCALE", b.vec(b.noise(p, 900.0, 1.0), b.noise(b.vmath("ADD", p, (3.1, 1.7, 0.4)),
                                                                                         900.0, 1.0), 0.0), scale=cell * 0.4))
    pB = b.vmath("ADD", warp, (0.37, 0.11, 0.0))
    mixk = b.smooth(0.42, 0.58, b.noise(p, 1.0 / (cell * 7.0), 1.0))
    vA = b.nodes.new("ShaderNodeTexVoronoi")
    vA.feature = "F1"
    b._set(vA.inputs["Vector"], warp)
    vA.inputs["Scale"].default_value = 1.0 / cell
    vA.inputs["Randomness"].default_value = 0.9
    vB = b.nodes.new("ShaderNodeTexVoronoi")
    vB.feature = "F1"
    b._set(vB.inputs["Vector"], pB)
    vB.inputs["Scale"].default_value = 1.0 / (cell * 0.75)
    vB.inputs["Randomness"].default_value = 0.9
    eda = b.voronoi(warp, 1.0 / cell, "DISTANCE_TO_EDGE", 0.9)
    edb = b.voronoi(pB, 1.0 / (cell * 0.75), "DISTANCE_TO_EDGE", 0.9)
    dist = b.lerp(eda, edb, mixk)
    f1 = b.lerp(vA.outputs["Distance"], vB.outputs["Distance"], mixk)
    rnd = b.lerp(b.sep(vA.outputs["Color"])[0], b.sep(vB.outputs["Color"])[0], mixk)
    wall = b.sub(1.0, b.smooth(0.0, L.fopt(o, "wall_w", 0.09), dist))
    inner = b.smooth(0.05, 0.45, f1)  # 0 at the cell centre, 1 near the wall
    tone_c = b.mad(rnd, L.fopt(o, "cell_var", D["cell_var"]), 1.0 - L.fopt(o, "cell_var", D["cell_var"]) / 2)
    val_in = b.mul(b.lerp(L.fopt(o, "cell_lo", D["cell_lo"]), 1.0, inner), tone_c)
    val = b.lerp(val_in, L.fopt(o, "cell_hi", D["cell_hi"]), wall)
    mot = b.remap(b.noise(p, 120.0, 3.0), 0.3, 0.7, 0.95, 1.05)
    v = b.mul(b.mul(mot, val), alb)
    col = b.vmath("MULTIPLY", b.vec(v, v, v), (1.0, 1.0, 1.035))
    rough = b.lerp(L.fopt(o, "core_r_in", 0.46), L.fopt(o, "core_r_wall", 0.30), wall)
    sh = b.bsdf(base=col, rough=rough, spec=L.fopt(o, "core_spec", 0.45), coat=L.fopt(o, "core_coat", 0.35),
                coat_rough=L.fopt(o, "core_coat_r", 0.10))
    return b.output(sh)


def mat_twill(o=None, name="Carbon_twill", coat_r=None):
    """The racket's outer 3K 2/2 twill under a SATIN clear coat (roughness ~0.18). Fabric coordinates follow the
    laminate round the rim: v along the rim (object y), u = profile arc length (x on the faces, + R(theta - sin theta)
    round the 11 mm radius, + the drop down the side wall), so the weave wraps the shoulder as one cloth. Each visible
    float is an anisotropic graphite fibre sheen whose tangent follows its tow (warp along the rim, weft across), so the
    diagonal 2/2 stair-step shows in the highlight roll-off; tow crowns are a whisper of bump under the flat coat."""
    o = o or {}
    m = bpy.data.materials.new(name)
    b = NB(m)
    p = b.tc("Object")
    x, y, z = b.sep(p)
    geo = b.nodes.new("ShaderNodeNewGeometry")
    N = geo.outputs["Normal"]
    _, _, nz = b.sep(N)
    th = b.math("ARCCOSINE", b.math("MINIMUM", b.math("MAXIMUM", nz, -1.0), 1.0))
    R, zt = FRAME_R, HALF_T
    drop = b.math("MINIMUM", b.math("MAXIMUM", b.sub(zt - R, z), 0.0), 2 * (zt - R))
    u = b.add(b.add(b.sub(x, b.mul(b.math("SINE", th), R)), b.mul(th, R)), drop)
    tow = L.fopt(o, "tow_mm", TOW / MM) / 1000.0
    cu, cv = b.div(u, tow), b.div(y, tow)
    i, j = b.math("FLOOR", cu), b.math("FLOOR", cv)
    fu, fv = b.sub(cu, i), b.sub(cv, j)
    k = b.math("FLOORED_MODULO", b.sub(j, i), 4.0)
    warp = b.math("LESS_THAN", k, 2.0)                 # 1: the warp (along the rim) floats on top
    across = b.lerp(fv, fu, warp)                      # position across the visible tow
    edge = b.math("MINIMUM", across, b.sub(1.0, across))
    crown = b.math("POWER", b.math("SINE", b.mul(b.clamp01(across), math.pi)), 0.5)
    gap = b.sub(1.0, b.smooth(0.0, 0.10, edge))       # the soft valley between tows
    wn = b.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    b._set(wn.inputs["Vector"], b.vec(i, j, warp))
    fl = b.mad(wn.outputs["Value"], 0.22, 0.89)        # +-11 % per float
    a0 = L.fopt(o, "tw_metal", 0.065)
    alb = b.mul(b.mul(fl, a0), b.sub(1.0, b.mul(gap, L.fopt(o, "gap_dark", 0.30))))
    rough = b.mad(gap, 0.10, L.fopt(o, "fib_r", 0.34))
    Y = (0.0, 1.0, 0.0)
    Tw = b.vmath("NORMALIZE", b.vmath("SUBTRACT", Y, b.vmath("SCALE", N, scale=b.vmath("DOT_PRODUCT", N, Y))))
    Tf = b.vmath("CROSS_PRODUCT", N, Tw)
    T = b.vmath("NORMALIZE", b.vmath("ADD", Tf, b.vmath("SCALE", b.vmath("SUBTRACT", Tw, Tf), scale=warp)))
    nrm = b.bump(crown, L.fopt(o, "crown", 0.35), 0.00004)
    sh = b.bsdf(base=b.rgb(alb), rough=rough, spec=0.5, metal=1.0, normal=nrm,
                coat=1.0, coat_rough=L.fopt(o, "coat_r", 0.18 if coat_r is None else coat_r), aniso=L.fopt(o, "aniso", 0.32))
    b.links.new(T, sh.inputs["Tangent"])
    sh.inputs["Coat IOR"].default_value = 1.5
    b.links.new(geo.outputs["Normal"], sh.inputs["Coat Normal"])
    return b.output(sh)


def mat_lining(o=None, name="BoreLining"):
    """Moulded bore lining: the same shell, resin-rich and glossy where it was pressed against the mould pin."""
    o = o or {}
    m = bpy.data.materials.new(name)
    b = NB(m)
    p = b.tc("Object")
    v = b.remap(b.noise(p, 400.0, 2.0), 0.3, 0.7, 0.9, 1.1)
    sh = b.bsdf(base=b.rgb(b.mul(v, L.fopt(o, "lin_alb", 0.018))), rough=0.22, spec=0.5, metal=0.0, coat=1.0,
                coat_rough=L.fopt(o, "lin_coat_r", 0.07))
    return b.output(sh)


def face_carbon(o, name="Carbon_3k"):
    """The racket's face, rim and side wall: the canon's WHITE Command twill (default), or v4's black twill (--white 0)."""
    if pace_on(o):
        return mat_pace_coupon(o, name + "_pace", "skin")
    if white_on(o):
        return mat_white_twill(o, name + "_white", "skin")
    return mat_twill(o, name)


# ------------------------------------------------------------------ white Command (owner, 2026-10-22)
# Command is white 3K twill with the weave clearly visible, the default in any image that names no feel (canon:
# ../renders4/canon.md "White Command"). The skin is kq_canon.mat_white ported to the coupon: the same baked 3K twill
# maps (k04_tex2: 2.6 mm tows, 16 per 41.6 mm tile), the same COMMAND_WHITE settings (white dielectric tow, tow tone and
# crevices, direction tone, fibre-bundle streaks, per-tow anisotropic sheen, relief bump, glass-clear 0.03 coat), laid
# on fabric coordinates that fold over the 11 mm rim and down the side wall (u: profile arc length, v: model y), so the
# face reads exactly as K01/K05/K10/K12's face. Bores (sealed core, canon: "dark carbon lining, never foam"): the white
# face ply wraps over the 0.6 mm mouth and tucks TUCK into the bore, then the moulded dark carbon lining runs on down.
import k10_lib as _K10  # noqa: E402  (TEX2, TILE: the canon's baked twill maps)
import kq_canon as _KC  # noqa: E402  (COMMAND_WHITE: the canon's white twill settings)

BORE_R = racket.HOLE_R * racket.U       # 6.2 mm
TUCK = 0.0008                           # the white face ply runs this far down a bore below the mouth, then ends
WHITE_PLY = (0.05 * MM, 0.33 * MM)      # depth of the white face ply (MAIN's outer tw ply) below the surface


def pace_on(o):
    """--feel pace (Release 2 feel toggle, 2026-10-23): the canon Pace v6 (black 12K) skin over v4's black laminate."""
    return str((o or {}).get("feel", "command")) == "pace"


def white_on(o):
    if pace_on(o):
        return False
    return float((o or {}).get("white", 1.0)) > 0


def mat_pace_coupon(o=None, name="Carbon_pace", role="skin"):
    """kq_canon.mat_pace (PACE v6: 8 mm 12K tapes, fibre-sheen weave, glass coat 0.03) on the coupon's fabric
    coordinates: every UV coordinate and UV tangent in the canon node tree is relinked to _fabric (u: profile arc
    length folding over the 11 mm rim and down the wall, v: model y), so the tapes fold over the edge as one cloth.
    --p_<key> <float> overrides PACE keys."""
    o = o or {}
    po = {k[2:]: float(v) for k, v in o.items() if k.startswith("p_") and k[2:] in _KC.PACE}
    m = _KC.mat_pace(name, o=po)
    b = NB(m, clear=False)
    b.nodes.remove(b.out)
    u, v, T = _fabric(b, role)
    uv = b.vec(u, v, 0.0)
    for nd in list(b.nodes):
        if nd.type == "TEX_COORD":
            for lk in list(nd.outputs["UV"].links):
                b.links.new(uv, lk.to_socket)
        elif nd.type == "TANGENT":
            for lk in list(nd.outputs["Tangent"].links):
                b.links.new(T, lk.to_socket)
    return m


def _cw(o):
    """COMMAND_WHITE with dev overrides --cw_<key> <float> (tint stays the canon's; --cw_tint_k scales it)."""
    p = dict(_KC.COMMAND_WHITE)
    for k, v in (o or {}).items():
        if k.startswith("cw_") and k[3:] in p and k[3:] != "tint":
            p[k[3:]] = float(v)
    k_ = float((o or {}).get("cw_tint_k", 1.0))
    p["tint"] = tuple(t * k_ for t in p["tint"])
    return p


def _timg(b, vec, fname, cs, interp="Linear"):
    n = b.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(os.path.join(_K10.TEX2, fname), check_existing=True)
    n.image.colorspace_settings.name = cs
    n.interpolation = interp
    n.extension = "REPEAT"
    b.links.new(vec, n.inputs["Vector"])
    return n.outputs["Color"]


def _fabric(b, role):
    """Fabric coordinates (metres) and the tangent along u. skin: as mat_twill (u = x on the faces, + R(theta - sin
    theta) round the rim, + the drop down the side wall; v = y), so the canon's face UVs (model x, y) carry on over the
    edge. bore: u round the bore (R * angle, the seam on the hidden near side), v = z (tows straight down the wall)."""
    p = b.tc("Object")
    x, y, z = b.sep(p)
    geo = b.nodes.new("ShaderNodeNewGeometry")
    N = geo.outputs["Normal"]
    nx, ny, nz = b.sep(N)
    if role == "bore":
        u = b.mul(b.math("ARCTAN2", nx, b.mul(ny, -1.0)), BORE_R)
        T = b.vmath("NORMALIZE", b.vmath("CROSS_PRODUCT", (0.0, 0.0, 1.0), N))
        return u, z, T
    th = b.math("ARCCOSINE", b.math("MINIMUM", b.math("MAXIMUM", nz, -1.0), 1.0))
    R, zt = FRAME_R, HALF_T
    drop = b.math("MINIMUM", b.math("MAXIMUM", b.sub(zt - R, z), 0.0), 2 * (zt - R))
    u = b.add(b.add(b.sub(x, b.mul(b.math("SINE", th), R)), b.mul(th, R)), drop)
    Y = (0.0, 1.0, 0.0)
    Tw = b.vmath("NORMALIZE", b.vmath("SUBTRACT", Y, b.vmath("SCALE", N, scale=b.vmath("DOT_PRODUCT", N, Y))))
    T = b.vmath("NORMALIZE", b.vmath("CROSS_PRODUCT", Tw, N))
    return u, y, T


def _white_bsdf(b, o, role="skin"):
    """kq_canon.mat_white's shader on fabric coordinates: returns the Principled BSDF node."""
    p = _cw(o)
    u, v, T = _fabric(b, role)
    vec = b.vec(b.div(u, _K10.TILE), b.div(v, _K10.TILE), 0.0)
    alb = _timg(b, vec, "albedo.png", "sRGB")
    rgh = _timg(b, vec, "rough.png", "Non-Color")
    hgt = _timg(b, vec, "height16.png", "Non-Color", interp="Cubic")
    rot = _timg(b, vec, "rot16.png", "Non-Color")
    cot = _timg(b, vec, "coat16.png", "Non-Color", interp="Cubic")
    along_u = b.smooth(0.42, 0.58, rot)                     # 1: fibres along u, 0: along v
    S_, Sl = 1.0 / p["streak_w"], 1.0 / p["streak_len"]

    def n1(a_, c_, zz):
        t_ = b.noise(b.vec(b.mul(a_, S_), b.mul(c_, Sl), zz), 1.0, 2.0, 0.6)
        return b.smooth(0.3, 0.7, t_)

    streak = b.sub(b.lerp(n1(u, v, 7.3), n1(v, u, 0.0), along_u), 0.5)   # -0.5..0.5, along each tow
    k_ = p["alb_k"]
    tone = b.mad(alb, k_ / 0.62, 1.0 - k_)
    tone = b.mul(tone, b.mad(b.sub(along_u, 0.5), p["dir_tone"], 1.0))
    tone = b.mul(tone, b.mad(streak, p["streak_a"], 1.0))
    tone = b.math("MINIMUM", tone, 1.12)
    base = b.vmath("MULTIPLY", b.vec(tone, tone, tone), p["tint"])
    rr = b.mul(b.mul(rgh, p["rough_s"]), b.mad(streak, p["streak_r"], 1.0))
    bs = b.nodes.new("ShaderNodeBsdfPrincipled")
    b._set(bs.inputs["Base Color"], base)
    b._set(bs.inputs["Roughness"], rr)
    bs.inputs["Metallic"].default_value = p["metal"]
    bs.inputs["IOR"].default_value = p["ior"]
    bs.inputs["Specular IOR Level"].default_value = p["spec"]
    bs.inputs["Anisotropic"].default_value = p["aniso"]
    b._set(bs.inputs["Anisotropic Rotation"], b.mad(rot, 0.5, -0.125))
    b._set(bs.inputs["Tangent"], T)
    b._set(bs.inputs["Normal"], b.bump(b.mad(streak, p["streak_h"], hgt), p["bump"], 0.00025))
    b._set(bs.inputs["Coat Normal"], b.bump(cot, p["print"], 0.00025))
    bs.inputs["Coat Weight"].default_value = 1.0
    bs.inputs["Coat IOR"].default_value = 1.5
    bs.inputs["Coat Roughness"].default_value = L.fopt(o, "cw_coat_r", p["coat_rough"])
    return bs


def mat_white_twill(o=None, name="Carbon_white", role="skin"):
    m = bpy.data.materials.new(name)
    b = NB(m)
    return b.output(_white_bsdf(b, o or {}, role))


def _lining_bsdf(b, o):
    """mat_lining's shader: the moulded bore lining, dark carbon, resin-rich and glossy (never foam)."""
    p = b.tc("Object")
    v = b.remap(b.noise(p, 400.0, 2.0), 0.3, 0.7, 0.9, 1.1)
    return b.bsdf(base=b.rgb(b.mul(v, L.fopt(o, "lin_alb", 0.018))), rough=0.22, spec=0.5, metal=0.0, coat=1.0,
                  coat_rough=L.fopt(o, "lin_coat_r", 0.07))


def _keep_white(b, keep_z, soft=0.00012):
    """1 where |z| is within keep_z of the face (the white ply's reach down a bore), 0 deeper (crisp, soft +-soft)."""
    _, _, z = b.sep(b.tc("Object"))
    return b.smooth(HALF_T - keep_z - soft, HALF_T - keep_z + soft, b.math("ABSOLUTE", z))


def mat_bore(o=None, name="BoreLining", tuck=TUCK):
    """K03's moulded bores: white face twill over the 0.6 mm mouth, tucking `tuck` into the bore, then the dark glossy
    carbon lining (mat_lining) all the way down: each hole reads as the canon's lined through-hole, a white lip
    crescent over a dark bore. --white 0: v4's all-dark lining."""
    o = o or {}
    if not white_on(o):
        return mat_lining(o, name)
    m = bpy.data.materials.new(name + "_white")
    b = NB(m)
    keep = _keep_white(b, LIP + tuck, soft=L.fopt(o, "tuck_soft", 0.15) * MM)
    return b.output(b.mix_shader(keep, _lining_bsdf(b, o), _white_bsdf(b, o, "bore")))


def _near_bore(b, reach=0.7 * MM):
    """1 within BORE_R + reach of the cut bore's axis (the half-bore at the front cut), else 0."""
    x, y, _ = b.sep(b.tc("Object"))
    dx, dy = b.sub(x, BORE[0]), b.sub(y, BORE[1])
    r = b.math("SQRT", b.add(b.mul(dx, dx), b.mul(dy, dy)))
    return b.math("LESS_THAN", r, BORE_R + reach)


def _white_zone(b, kind, keep_z):
    """Section faces that belong to the white face ply: MAIN's/SKIN's outer tw ply (d0 = 0.05 mm), and on K03b's wound
    tube (d0 >= 2.05 mm) the same 0.05-0.33 mm below the outer surface (the face ply laid over the tube). Down a lined
    bore it ends keep_z below the face."""
    d0, d = b.attr("d0"), b.attr("d")
    tube = b.mul(b.math("GREATER_THAN", d0, 2.05 * MM),
                 b.mul(b.math("GREATER_THAN", d, WHITE_PLY[0]), b.math("LESS_THAN", d, WHITE_PLY[1])))
    W = tube
    if kind == "tw":
        W = b.math("MAXIMUM", tube, b.math("LESS_THAN", d0, 0.06 * MM))
    if keep_z is not None:
        W = b.mul(W, b.sub(1.0, b.mul(_near_bore(b), b.sub(1.0, _keep_white(b, keep_z)))))
    return W


def _white_section(b, o, kind):
    """Polished section of the white face ply: white fibre ends in clear resin, a little duller in the lenses (tw)."""
    p = _cw(o)
    pv = b.attr("pv")
    var = b.mad(pv, 0.06, 0.97)
    grain = b.remap(b.noise(b.tc("Object"), 30000.0, 0.0), 0.3, 0.7, 0.92, 1.08)
    a0 = L.fopt(o, "wsec_alb", 0.92)
    r0 = L.fopt(o, "wsec_r", 0.22)
    if kind == "tw":
        dd = _depth_frac(b)
        x4 = _phase01(b)
        x1 = b.math("FRACT", b.mul(x4, 4.0))
        over = b.smooth(-0.4, 0.4, b.math("SINE", b.mul(b.sub(x4, 0.125), 2 * math.pi)))
        cen = b.lerp(0.33, 0.67, over)
        e = b.div(b.sub(x1, 0.5), 0.47)
        hh = b.mul(b.math("SQRT", b.clamp01(b.sub(1.0, b.mul(e, e)))), 0.28)
        lens = b.sub(1.0, b.smooth(b.sub(hh, 0.06), hh, b.math("ABSOLUTE", b.sub(dd, cen))))
        t = b.mul(b.lerp(a0, a0 * 0.86, lens), b.mul(var, b.lerp(1.0, grain, lens)))
        rough = b.lerp(r0, r0 + 0.10, lens)
    else:
        t = b.mul(b.mul(var, grain), a0)
        rough = r0 + 0.04
    dbg = L.fopt(o, "wsec_dbg", 0.0)  # dev: the white ply glows red, to check where it is
    return b.bsdf(base=b.vmath("MULTIPLY", b.vec(t, t, t), p["tint"]), rough=rough, spec=L.fopt(o, "wsec_spec", 0.35),
                  emit=(1.0, 0.0, 0.0) if dbg else None, emit_strength=dbg if dbg else None)


def mat_chamfer_white(o=None, keep_z=None, name="ChamferW"):
    """The 0.15 mm 45 deg polished chamfer round the cut: it cuts through the clear coat into the white face ply, so it
    is polished white (the lg_line kicker still reads in it); down a lined bore below keep_z, and on --white 0, it is
    v4's black mirror lacquer (k03_lib.mat_chamfer)."""
    o = o or {}
    if not white_on(o):
        return L.mat_chamfer()
    p = _cw(o)
    m = bpy.data.materials.new(name)
    b = NB(m)
    wv = L.fopt(o, "cham_alb", 0.80)
    wh = b.bsdf(base=tuple(t * wv for t in p["tint"]), rough=L.fopt(o, "cham_r", 0.10), spec=0.5, coat=1.0,
                coat_rough=0.02)
    wh.inputs["Coat IOR"].default_value = 1.52
    if keep_z is None:
        return b.output(wh)
    dk = b.bsdf(base=(0.02, 0.02, 0.021), rough=0.06, spec=0.7, coat=1.0, coat_rough=0.02)
    dk.inputs["Coat IOR"].default_value = 1.52
    W = b.sub(1.0, b.mul(_near_bore(b), b.sub(1.0, _keep_white(b, keep_z))))
    return b.output(b.mix_shader(W, dk, wh))


# ------------------------------------------------------------------ footprint and rim helpers (model space)
def footprint(margin=0.0, holes_r=None):
    """The coupon's top-face outline in model XY (shapely), optionally shrunk and with the hole mouths removed."""
    o, _ = outline_ccw(400)
    P = Polygon(o)
    P = P.intersection(sbox(-1, Y_FRONT, 1, Y_BACK))
    nx, ny = INNER_DIR[1], -INNER_DIR[0]
    d = INNER_DIR
    q0 = (INNER_P[0] - d[0], INNER_P[1] - d[1])
    q1 = (INNER_P[0] + d[0], INNER_P[1] + d[1])
    hp = Polygon([q0, q1, (q1[0] + nx, q1[1] + ny), (q0[0] + nx, q0[1] + ny)])
    P = P.intersection(hp)
    if margin:
        P = P.buffer(-margin)
    if holes_r:
        for (hx, hy) in COUPON_HOLES:
            P = P.difference(Point(hx, hy).buffer(holes_r, resolution=48))
    return P


def rim_point(y, alpha_deg, off=0.0):
    """Model-space point + normal on the frame radius at profile angle alpha (0 = top face, 90 = side wall), at
    height y along the right-hand rim; off pushes it outward along the normal."""
    o, nr = outline_ccw(1200)
    best = None
    for (x1, y1), (x2, y2), n1 in zip(o, o[1:] + o[:1], nr):
        if x1 > 0.05 and (y1 - y) * (y2 - y) <= 0 and y1 != y2:
            t = (y - y1) / (y2 - y1)
            best = (x1 + (x2 - x1) * t, n1)
    x, (nx, ny) = best
    a = math.radians(alpha_deg)
    cx, cy = x - nx * FRAME_R, y - ny * FRAME_R
    cz = HALF_T - FRAME_R
    N = Vector((nx * math.sin(a), ny * math.sin(a), math.cos(a)))
    P = Vector((cx, cy, cz)) + N * (FRAME_R + off)
    return P, N, Vector((nx, ny, 0.0))


# ------------------------------------------------------------------ floor and camera
def build_floor(size=3.0, o=None):
    """Matte graphite floor (no mirror: it must not read as an acrylic stand). Lit only by its own floor-linked
    lights; it takes the piece's soft contact shadow; invisible to the piece's glossy rays (the reflection cards
    below floor level still draw on the polished section)."""
    o = o or {}
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0.6, FLOOR_Z))
    fl = bpy.context.active_object
    fl.name = "Floor"
    m = bpy.data.materials.new("FloorMat")
    b = NB(m)
    p = b.tc("Object")
    r = b.remap(b.noise(p, 3.0, 2.0), 0.3, 0.7, L.fopt(o, "floor_r0", 0.62), L.fopt(o, "floor_r1", 0.70))
    c = L.fopt(o, "floor_alb", 0.030)
    grit = b.remap(b.noise(p, 2200.0, 0.0), 0.3, 0.7, 0.96, 1.04)
    cc = b.mul(grit, c)
    b.output(b.bsdf(base=b.vec(cc, cc, b.mul(cc, 1.06)), rough=r, spec=L.fopt(o, "floor_spec", 0.25)))
    fl.data.materials.append(m)
    fl.visible_glossy = False
    fl.visible_shadow = False
    return fl


def camera(o, az=None, el=None, lens=None, dist=None, target=(0.0, 0.016, 0.0), shift=(0.0, 0.0)):
    o = o or {}
    az = L.fopt(o, "cam_az", 32.0) if az is None else az
    el = L.fopt(o, "cam_el", 23.0) if el is None else el
    lens = L.fopt(o, "lens", 150.0) if lens is None else lens
    dist = L.fopt(o, "cam_d", 0.62) if dist is None else dist
    loc = L.dir_loc(target, az, el, dist)
    cam = studio.camera(loc, target, lens=lens, shift=(L.fopt(o, "shift_x", shift[0]), L.fopt(o, "shift_y", shift[1])))
    cam.data.dof.use_dof = False
    cam.data.clip_start = 0.01
    return cam


# ------------------------------------------------------------------ K03b: hollow frame tube
def bisect_open(ob, cuts):
    """Cut an open (uncapped) object with the coupon planes; returns {cut name: [loops in that cut's uv]}."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    out = {}
    for c in cuts:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=c.P0, plane_no=c.N,
                                     clear_inner=True)
        cutv = set(v for v in res["geom_cut"] if isinstance(v, bmesh.types.BMVert))
        es = [e for e in bm.edges if e.verts[0] in cutv and e.verts[1] in cutv and e.is_boundary]
        adj = {}
        for e in es:
            a, b = e.verts
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
        seen, loops = set(), []
        for st in adj:
            if st in seen:
                continue
            lp, prev, cur = [st], None, st
            seen.add(st)
            while True:
                nxt = [n for n in adj[cur] if n is not prev and n not in seen]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                seen.add(cur)
                lp.append(cur)
            if len(lp) > 8:
                loops.append([c.to_uv(v.co) for v in lp])
        out[c.name] = loops
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    ob.matrix_world = Matrix.Translation(-PIECE_OFFSET)
    return out
