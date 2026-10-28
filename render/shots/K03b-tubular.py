"""K03b-tubular (v5, white Command; materials only, as K03 v5 -- --white 0 rebuilds v4): the CONVENTIONAL construction, cut exactly like K03 (same coupon, holes, camera, rig and floor,
so the page cross-fades tubular -> KINETIQ pixel for pixel and only the construction changes). No brand marks.

A separate hollow frame tube runs along the edge (20 mm wide, 2.2 mm wound wall, as G07 draws it), open at the cut:
you look into its dark tunnel. Two 1.4 mm twill face skins (the same ply-strata language as K03) are bonded onto an
EVA core block; dull neutral adhesive lines (0.2-0.45 mm, noisy) under both skins and down the tube's inner wall, with
squeeze-out fillets where the skins meet the tube and a few micro-voids. The holes are DRILLED: a sharp mouth flush
with the face, the bore wall raw skin | bond | open-pore EVA | bond | skin with a little fibre fray at the skin edges.

Usage: K03b-tubular.py --w 960 --h 540 --spp 32 --out K03b_preview [--variant base|full] [--both]
  base: no amber anywhere.  full: adds the same lg_shell amber hairline as K03 (identical pixels), nothing else.
  --both: one render writes <out>-full.png and <out>-base.png (base = denoised light-group pass without lg_shell).
Dev flags as K03-section-cut (--crop, --solo, --each, --nodither, rig levels).
v6 (art director, 2026-10-22): no change in this file. The shared rig's white lights (flag, pool, lacquer band, fill),
the brighter white face ply section (k03s_lib._white_section) and the chamfer hairline apply here as in K03, so the two
still read as the same face laminate; the line is k03s_line.py --white 1 with the same mask and settings as K03.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k03s_lib as S  # noqa: E402
import k03s_rig as R  # noqa: E402
import k03_lib as L  # noqa: E402

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from shapely.geometry import Point, Polygon, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402

MM = S.MM
TUBE_W = 0.020      # frame tube width from the outer edge (G07)
TUBE_WALL = 0.0022  # wound tube wall (G07)
INNER_R = 0.003     # tube's inner-side corner radius
SKIN_T = 0.0014     # face skin
GLUE = 0.00032      # mean adhesive thickness
GLUE_VAR = 0.40
FILLET = 0.0012     # squeeze-out fillet radius where the skins meet the tube wall

KINDS = ["tw", "ud0", "ud90", "resin"]
SKIN = [(0.05, "resin"), (0.28, "tw"), (0.04, "resin"), (0.20, "ud0"), (0.04, "resin"), (0.20, "ud90"),
        (0.04, "resin"), (0.28, "tw"), (0.04, "resin"), (0.20, "ud0"), (0.02, "resin")]  # 1.4 mm
M_FACE, M_BORE = 0, 1
MI = {k: 2 + i for i, k in enumerate(KINDS)}
M_EVA, M_GLUE, M_VOID = 6, 7, 8


def g_of(noise):
    def g(s):
        return min(0.00045, max(0.0002, GLUE * (1.0 + GLUE_VAR * noise(s))))
    return g


def noisy_band(u0, u1, z_edge, g, up):
    us = np.arange(u0 - 0.001, u1 + 0.001, 0.0001)
    sgn = 1.0 if up else -1.0
    edge = [(u, z_edge + sgn * g(u)) for u in us]
    poly = Polygon([(us[0], z_edge), (us[-1], z_edge)] + edge[::-1])
    return poly if poly.is_valid else poly.buffer(0)


def noisy_ring(T, g):
    ring = T.exterior
    n = max(64, int(ring.length / 0.0001))
    pts = [ring.interpolate(ring.length * k / n) for k in range(n)]
    ccw = ring.is_ccw
    out = []
    for k in range(n):
        a, b = pts[k - 1], pts[(k + 1) % n]
        tx, tz = b.x - a.x, b.y - a.y
        ln = math.hypot(tx, tz) or 1.0
        nx, nz = (tz / ln, -tx / ln) if ccw else (-tz / ln, tx / ln)
        d = g(ring.length * k / n)
        out.append((pts[k].x + nx * d, pts[k].y + nz * d))
    return Polygon(out).buffer(0).union(T).difference(T)


def make_regions(cavities):
    """cavities: {cut name: [Polygon in that cut's uv]} of the tube void."""
    zt = S.HALF_T
    s_in = zt - SKIN_T
    counter = [0]

    def band(z0, z1):
        return sbox(-1, z0, 1, z1)

    def regions(cut, NP, A):
        counter[0] += 1
        seed = 11 * counter[0] + len(cut.name)
        rng = np.random.default_rng(seed)
        out = []

        def emit(geom, mi, d0=0.0, t=1.0, pv=None):
            pv = float(rng.uniform(0, 1)) if pv is None else pv
            for p in S.polys_of(geom.intersection(A) if mi >= 0 else geom.intersection(A.buffer(1e-6))):
                out.append((p, mi, {"d0": d0, "t": t, "pv": pv}))

        cav = None
        for C in cavities.get(cut.name, []):
            if C.intersects(NP):
                cav = C
        rest = NP
        glue_parts = []
        if cav is not None:
            walls = S.side_walls(cut, NP)
            cx = cav.centroid.x
            sg = walls[0][1] if walls else (1 if cx > 0 else -1)
            half = sbox(cx, -1, cx + 1, 1) if sg > 0 else sbox(cx - 1, -1, cx, 1)
            T = S.largest(NP.intersection(cav.buffer(TUBE_WALL, join_style=1, resolution=32).union(half)))
            # wound tube wall: concentric plies around the void
            kinds = ["resin", "ud0", "ud90", "ud0", "ud90", "resin"]
            ts = [0.12, 0.5, 0.5, 0.5, 0.46, 0.12]
            prev = cav
            acc = 0.0
            for (k, t) in zip(kinds, ts):
                acc += t
                nxt = cav.buffer(acc * MM, join_style=1, resolution=32)
                emit(T.intersection(nxt).difference(prev), MI[k], acc * MM, t * MM)
                prev = nxt
            emit(T.difference(prev), MI["ud0"], acc * MM, 1.0)
            rest = NP.difference(T)
            emit(cav, -1)  # the void stays open
            TG = noisy_ring(T, g_of(L.smooth_noise(seed + 1, base=0.003)))
            glue_parts.append(rest.intersection(TG))
        core = rest.difference(unary_union(glue_parts)) if glue_parts else rest
        u0, _, u1, _ = NP.bounds
        Gt = noisy_band(u0, u1, s_in, g_of(L.smooth_noise(seed + 2, base=0.005)), up=False)
        Gb = noisy_band(u0, u1, -s_in, g_of(L.smooth_noise(seed + 3, base=0.005)), up=True)
        skin_t = core.intersection(band(s_in, 1))
        skin_b = core.intersection(band(-1, -s_in))
        eva_zone = core.intersection(band(-s_in, s_in))
        G = unary_union(glue_parts + [eva_zone.intersection(Gt), eva_zone.intersection(Gb)])
        Gc = G.buffer(FILLET, resolution=16).buffer(-FILLET, resolution=16)  # squeeze-out fills the inner corners
        G = unary_union([G, Gc.intersection(eva_zone)])
        voids = []
        for (zc, n_v) in ((s_in, 2), (-s_in, 2)):
            for _ in range(n_v):
                u = rng.uniform(u0 + 0.004, u1 - 0.004)
                zz = zc - np.sign(zc) * 0.00016
                e = affinity.scale(Point(u, zz).buffer(1.0, resolution=12), rng.uniform(0.00025, 0.0006),
                                   rng.uniform(0.00006, 0.0001))
                v = e.intersection(G)
                if not v.is_empty:
                    voids.append(v)
        if voids:
            V = unary_union(voids)
            G = G.difference(V)
            emit(V, M_VOID)
        emit(G, M_GLUE)
        emit(eva_zone.difference(G), M_EVA)
        for (Sk, top) in ((skin_t, True), (skin_b, False)):
            d = 0.0
            for (t, kind) in SKIN:
                if top:
                    zb = band(zt - (d + t) * MM, zt - d * MM if d > 0 else 1)
                else:
                    zb = band(-1 if d == 0 else -zt + d * MM, -zt + (d + t) * MM)
                if d + t >= SKIN_T / MM - 1e-9:
                    zb = band(s_in, zt - d * MM) if top else band(-zt + d * MM, -s_in)
                emit(Sk.intersection(zb), MI[kind], d * MM, t * MM)
                d += t
        return out

    return regions


EVA_RGB = (1.0, 0.985, 0.95)
GLUE_RGB = (0.044, 0.041, 0.034)   # dull neutral adhesive, about sRGB (60, 58, 52)


def mat_eva(o, name="EVA"):
    """Plain EVA block: a dull, matte, lighter neutral grey than K03's graphite, with soft low-contrast round pores
    (albedo only)."""
    m = bpy.data.materials.new(name)
    b = S.NB(m)
    p = b.tc("Object")
    cell = L.fopt(o, "eva_cell", 0.5) / 1000.0
    f1 = b.voronoi(p, 1.0 / cell, "F1", 1.0)
    pore = b.sub(1.0, b.smooth(L.fopt(o, "pore0", 0.10), L.fopt(o, "pore1", 0.24), f1))
    pres = b.math("GREATER_THAN", b.noise(b.vmath("ADD", p, (7.0, 3.0, 1.0)), 1.0 / (cell * 0.9), 0.0), 0.5)
    pore = b.mul(pore, pres)
    mot = b.remap(b.noise(p, 150.0, 3.0), 0.3, 0.7, 0.96, 1.04)
    v = b.mul(b.mul(mot, b.lerp(1.0, 1.0 - L.fopt(o, "pore_dark", 0.28), pore)), L.fopt(o, "eva_alb", 0.52))
    sh = b.bsdf(base=b.vmath("MULTIPLY", b.vec(v, v, v), EVA_RGB), rough=0.82, spec=0.3)
    return b.output(sh)


def mat_glue(o, name="Glue"):
    m = bpy.data.materials.new(name)
    b = S.NB(m)
    p = b.tc("Object")
    v = b.remap(b.noise(p, 3000.0, 1.0), 0.3, 0.7, 0.85, 1.12)
    sh = b.bsdf(base=b.vmath("MULTIPLY", b.vec(v, v, v), GLUE_RGB), rough=0.55, spec=0.4)
    return b.output(sh)


def mat_cavity(o, front):
    """Inside of the hollow tube: raw dark composite; a faint bounce near the mouth fades to black with depth."""
    m = bpy.data.materials.new("Cavity")
    b = S.NB(m)
    p = b.tc("Object")
    depth = b.vmath("DOT_PRODUCT", b.vmath("SUBTRACT", p, tuple(front.P0)), tuple(front.N))
    fall = b.math("EXPONENT", b.mul(depth, -1.0 / L.fopt(o, "tube_lam", 0.006)))
    em = b.mul(fall, L.fopt(o, "tube_bounce", 0.03))
    sh = b.bsdf(base=(0.02, 0.02, 0.021), rough=0.5, spec=0.4, emit=(0.9, 0.92, 1.0), emit_strength=em)
    return b.output(sh)


def mat_drilled_wall(o, name="DrilledWall"):
    """Drilled bore wall, by object |z|: raw skin (dull cut fibre, a little fray reaching into the bond) | dull bond
    ring | open-pore matte EVA. The mouth is the same geometry as K03's; here it is raw cut skin."""
    m = bpy.data.materials.new(name)
    b = S.NB(m)
    p = b.tc("Object")
    _, _, z = b.sep(p)
    az = b.math("ABSOLUTE", z)
    zt = S.HALF_T
    fray = b.mul(b.sub(b.noise(b.vmath("MULTIPLY", p, (1.0, 1.0, 0.15)), 2500.0, 2.0), 0.5), 0.00022)
    s_edge = b.add(zt - SKIN_T, fray)
    gw = b.remap(b.noise(p, 260.0, 1.0), 0.3, 0.7, 0.00022, 0.00042)
    is_skin = b.math("GREATER_THAN", az, s_edge)
    is_glue = b.math("GREATER_THAN", az, b.sub(zt - SKIN_T, gw))
    # EVA with open pores
    cell = 0.0005
    f1 = b.voronoi(p, 1.0 / cell, "F1", 1.0)
    pore = b.sub(1.0, b.smooth(0.12, 0.30, f1))
    ev = b.mul(b.lerp(1.0, 0.45, pore), L.fopt(o, "eva_alb", 0.52) * 0.9)
    b_eva = b.bsdf(base=b.vmath("MULTIPLY", b.vec(ev, ev, ev), EVA_RGB), rough=0.85, spec=0.25)
    b_glue = b.bsdf(base=GLUE_RGB, rough=0.6, spec=0.35)
    fib = b.remap(b.noise(b.vmath("MULTIPLY", p, (1.0, 1.0, 0.2)), 6000.0, 1.0), 0.3, 0.7, 0.6, 1.5)
    sk = b.mul(fib, 0.020)
    b_skin = b.bsdf(base=b.vec(sk, sk, sk), rough=0.55, spec=0.4)
    m1 = b.mix_shader(is_glue, b_eva, b_glue)
    m2 = b.mix_shader(is_skin, m1, b_skin)
    if S.white_on(o):
        # white Command: the drill cuts through the white face ply, so the mouth shows a matte white ring of cut white
        # fibre (the top 0.33 mm, frayed like the skin edge) above the dark cut carbon of the rest of the skin
        wz = b.add(zt - S.WHITE_PLY[1], b.mul(fray, 0.35))
        is_white = b.smooth(b.sub(wz, 0.00003), b.add(wz, 0.00003), az)
        wv = b.mul(fib, L.fopt(o, "drill_white", 0.42))
        tint = S._cw(o)["tint"]
        b_white = b.bsdf(base=b.vmath("MULTIPLY", b.vec(wv, wv, wv), tint), rough=0.6, spec=0.4)
        m2 = b.mix_shader(is_white, m2, b_white)
    return b.output(m2)


def build(o, variant):
    cuts = S.coupon_cuts()
    cav = L.build_tube_cavity("TubeVoid", tube_w=TUBE_W, wall=TUBE_WALL, frame_r=S.FRAME_R, inner_r=INNER_R, seg=24,
                              per=240)
    loops = S.bisect_open(cav, cuts)
    cav.data.materials.append(mat_cavity(o, S.front_cut(cuts)))
    cavities = {k: [Polygon(lp).buffer(0) for lp in v] for k, v in loops.items()}
    print("cavity loops", {k: len(v) for k, v in loops.items()})
    head = S.build_head("Tub_Coupon", hole_mat=M_BORE)
    # v5 (white Command, owner 2026-10-22): materials only, as K03 v5. The skins and the tube's outside are the canon's
    # white twill; the section's white face ply runs along both skins (their outer tw ply) and over the tube (the
    # outer 0.05-0.33 mm of its wound wall), so both stills wear the same white face laminate; the drilled bores cut
    # through it (a white ring at the mouth). --white 0 rebuilds v4's black materials exactly.
    mats = [S.face_carbon(o), mat_drilled_wall(o)] + [S.mat_ply(k, o) for k in KINDS] + \
           [mat_eva(o), mat_glue(o), L.mat_void()]
    car = S.Carver(head, cuts, make_regions(cavities), mats,
                   chamfer_mat=S.mat_chamfer_white(o, keep_z=S.WHITE_PLY[1]))
    return car, cav


def setup(o, variant):
    R.scene(o)
    car, cav = build(o, variant)
    floor = S.build_floor(o=o)
    full = variant == "full" or bool(o.get("each"))
    R.lights([car.obj, cav], floor, car, shell=full, o=o)
    R.camera(o)
    if o.get("both"):
        rib = bpy.data.objects["lg_shell"]
        L.assign_groups([rib], "shell")
        L.both_variants(o, "shell", L.out_path(o["out"] + "-base")[:-4], glow_on_full=True)
    elif full:
        L.shell_glow(o)
    return car


if __name__ == "__main__":
    o = L.parse_args()
    t0 = time.time()
    car = setup(o, "full" if o.get("both") else o["variant"])
    print("geometry", round(time.time() - t0, 1), "s")
    if o.get("fit"):
        print("FRAME BBOX x0 x1 y0 y1 (top-down):", [round(v, 4) for v in L.frame_bbox([car.obj])])
    p = L.finish_both(o, o["out"]) if o.get("both") else L.finish(o, "K03b_preview")
    print("rendered", p, round(time.time() - t0, 1), "s")
