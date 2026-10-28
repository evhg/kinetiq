"""K03-section-cut (v5, white Command): a machined coupon cut from the racket's edge, polished like a metallurgy sample.

v6 (art director "revise 6.5", 2026-10-22; still materials and white-only lights, camera, rig, floor and geometry v4's):
the top was flat matte grey (168-197, no specular cue, half the canon's weave contrast) because v4's diffuse key lit it
flat. A flag keeps the key off the top; a low pool from the back-left, a gridded lacquer band and a brighter wall fill
light the white (k03s_rig.white_lights, key_flag, gloss_strip); the white face ply is brighter and polished and the
chamfer's hairline runs quietly round the whole shell loop; the closed cells get more contrast at the same mean; the
amber line is laid OVER the white (k03s_line.py --white 1). --white 0 still rebuilds v4 to the pixel (PYTHONHASHSEED=0:
kq_regions seeds each ply's tone from hash(), so reruns differ by a few 16-bit LSB without it).
Finals v6 (renders4/final5-K03.md): PYTHONHASHSEED=0 ... --w 3200 --h 1800 --spp 320 --both --out final/K03-section-cut,
then k03s_line.py <K03-line-mask2.png> <base> <full> --halo 0.9 --sigma 5 --white 1 --tint 0.6 (K03 AND K03b).

v5 (owner, 2026-10-22: Command is white 3K twill, the default in any image that names no feel): MATERIALS ONLY, plus
two white-only lights added to the shared rig (k03s_rig.white_lights: behind the cut's plane, coupon-linked, so the
section, floor and every v4 light are untouched). Camera, rig, floor and geometry are v4's to the pixel (K03b still
cross-fades into it and SealedCoreTrace.tsx still traces it). The skin is the canon's white twill (k03s_lib.face_carbon),
the section's outer twill ply is the white face ply (a white hairline round the shell), the inner plies, resin lines,
rim build-up and graphite core stay v4's dark laminate, the bores are white over the mouth then dark carbon lining.
--white 0 rebuilds v4 exactly (no white lights, v4 materials).


The front cut passes through the centre of ONE bore of the outer row, so the polished face starts at the lined
half-bore and runs to the side wall: one closed shell loop (bore lining, top skin, side wall, bottom skin) round the
graphite closed-cell core. The shell is 2.0 mm of plies (3K twill / UD 0 / UD 90 x3, with thin resin lines between
plies), the same laminate on the outside, round the 11 mm side-wall radius and down every moulded bore, without a
break. Inside the side-wall radius zone only, eight extra UD plies (0.31 mm each, each with its resin line) build the
wall to 4.5 mm; they drop off one by one round the radius with short tapered ends, so the core keeps straight faces
and a clean rounded corner (G07 draws the same 4.5 mm wall). Two complete outer-row holes are moulded into the top face
behind the cut at the true 27 mm pitch. No glue line anywhere.

Usage: K03-section-cut.py --w 960 --h 540 --spp 32 --out K03_preview [--variant base|full] [--both]
  base: the rig without lg_shell.  full: adds lg_shell, the 2700 K amber hairline along the rim's shoulder.
  --both: one render writes <out>-full.png and <out>-base.png (base = denoised light-group pass without lg_shell).
  --line_mask: render only the hairline as a linear white profile (rim region, no bounces, no denoise).
Finals (v4): --both --spp 320 at 3200x1800 for <out>-base.png; the full stills are then
  k03s_line.py <mask> <base> <full> --halo 0.9 --sigma 5   (mask: --line_mask --shell_w 0.55 --shell_tail 0.32)
  for K03 AND K03b, so the line lands on --amber #e3a467 / --amber-hot #ffe2bf exactly and is identical in all fulls.
Dev flags: --crop x0,x1,y0,y1, --solo a,b, --each, --fit, --nodither, and every rig level via k03s_rig.
Camera, rig and floor are shared with K03b-tubular via k03s_rig, so the two register pixel for pixel.
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
from shapely.geometry import Point, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

MM = S.MM
# main shell, outer surface inward: (thickness mm, kind); 2.0 mm
MAIN = [(0.05, "resin"), (0.28, "tw"), (0.04, "resin"), (0.20, "ud0"), (0.04, "resin"), (0.20, "ud90"),
        (0.04, "resin"), (0.28, "tw"), (0.04, "resin"), (0.20, "ud0"), (0.04, "resin"), (0.20, "ud90"),
        (0.04, "resin"), (0.28, "tw"), (0.07, "resin")]
SHELL = sum(t for t, _ in MAIN)
RIM_N, RIM_T, RIM_RES = 8, 0.3125, 0.035   # build-up to 4.5 mm in the side-wall radius zone
RIM_TH0, RIM_DTH, RIM_TAU = 4.0, 7.0, 7.0  # ply j starts tapering in at theta = TH0 + j*DTH (deg round the radius)
KINDS = ["tw", "ud0", "ud90", "resin"]
M_FACE, M_BORE = 0, 1
MI = {k: 2 + i for i, k in enumerate(KINDS)}
M_CORE = 2 + len(KINDS)


def wall_frames(cut, NP):
    """[(u_wall, sg, cos_phi)] for each side-wall end of a natural section (phi: rim normal vs the cut's u axis)."""
    out = []
    o, nr = S.outline_ccw(1200)
    for (uw, sg) in S.side_walls(cut, NP):
        P = cut.from_uv(uw, 0.0)
        k = min(range(len(o)), key=lambda i: (o[i][0] - P.x) ** 2 + (o[i][1] - P.y) ** 2)
        c = abs(nr[k][0] * cut.T.x + nr[k][1] * cut.T.y)
        if c > 0.9:  # only where the cut meets the rim square (the front and back faces)
            out.append((uw, sg, c))
    return out


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def buildup_polys(uw, sg, cphi):
    """Tapered build-up layers in the side-wall radius zone: [(Polygon, kind)], outermost first. Layer depths are
    measured from the true surface round the corner ellipse (the cut meets the rim at cphi); each ply's thickness
    grows from 0 at its start angle over RIM_TAU deg (a short tapered end), so the core corner stays clean."""
    R = S.FRAME_R
    zt = S.HALF_T
    uc = uw - sg * R / cphi
    zc = zt - R
    ths = list(np.arange(0.0, 90.0001, 0.25))
    TH = ths + [180.0 - t for t in reversed(ths)]

    def pt(T, D):
        if T <= 90.0:
            a = math.radians(T)
            return (uc + sg * (R - D) / cphi * math.sin(a), zc + (R - D) * math.cos(a))
        a = math.radians(T)
        return (uc + sg * (R - D) / cphi * math.sin(a), -zc + (R - D) * math.cos(a))

    layers = []
    for j in range(RIM_N):
        th0 = RIM_TH0 + j * RIM_DTH
        layers.append((RIM_RES, "resin", th0))
        layers.append((RIM_T - RIM_RES, "ud90" if j % 2 == 0 else "ud0", th0))
    out = []
    Dprev = [SHELL * MM] * len(TH)
    for li, (t, kind, th0) in enumerate(layers):
        Dn = [d + t * MM * smoothstep(th0, th0 + RIM_TAU, min(T, 180.0 - T)) for d, T in zip(Dprev, TH)]
        keep = [k for k, T in enumerate(TH) if th0 - 0.3 <= min(T, 180.0 - T)]
        if len(keep) > 2:
            Do = [Dprev[k] - (0.25 * MM if li == 0 else 0.0) for k in keep]
            outer = [pt(TH[k], d) for k, d in zip(keep, Do)]
            inner = [pt(TH[k], Dn[k]) for k in keep]
            poly = Polygon(outer + inner[::-1])
            if not poly.is_valid:
                poly = poly.buffer(0)
            out.append((poly, kind))
        Dprev = Dn
    core_cut = Polygon([pt(T, d) for T, d in zip(TH, Dprev)] + [(uc - sg * 0.05, -zt - 0.01), (uc - sg * 0.05, zt + 0.01)])
    return out, core_cut


def kq_regions(cut, NP, A):
    rng = np.random.default_rng(abs(hash(cut.name)) % 997)
    bufs = {}

    def B(dmm):
        k = round(dmm, 6)
        if k == 0:
            return NP
        if k not in bufs:
            bufs[k] = NP.buffer(-dmm * MM, join_style=1, resolution=48)
        return bufs[k]

    out = []

    def emit(geom, kind_or_mi, d0, t, pv=None):
        mi = MI[kind_or_mi] if isinstance(kind_or_mi, str) else kind_or_mi
        pv = float(rng.uniform(0, 1)) if pv is None else pv
        for p in S.polys_of(geom.intersection(A)):
            out.append((p, mi, {"d0": d0 * MM, "t": t * MM, "pv": pv}))

    d = 0.0
    for (t, kind) in MAIN:
        emit(B(d).difference(B(d + t)), kind, d, t)
        d += t
    inner = B(SHELL)
    core = inner
    for (uw, sg, cphi) in wall_frames(cut, NP):
        polys, core_keep = buildup_polys(uw, sg, cphi)
        used = None
        for (poly, kind) in polys:
            g = poly.intersection(inner)
            if used is not None:
                g = g.difference(used)
            used = g if used is None else used.union(g)
            emit(g, kind, SHELL, RIM_T)
        core = core.difference(used).intersection(core_keep.union(S.halfplane(uw - sg * 0.02, sg < 0)))
    emit(core, M_CORE, 0.0, 1.0, 0.0)
    return out


def build(o):
    """v5 (white Command, owner 2026-10-22): materials only; geometry, camera, rig and floor are v4's exactly.
    Face, rim, side wall and bottom skin: the canon's white 3K twill (S.face_carbon). Section: the outer tw ply is the
    white face ply (a white hairline round the shell); the UD plies, resin lines, inner twill plies, the rim build-up and
    the graphite core stay v4's dark laminate. Bores: white twill over the mouth, tucking TUCK into the bore, then v4's
    dark glossy lining (the canon's lined through-hole); the section's white ply ends at the same depth down the
    half-bore. Chamfer: polished white, dark down the bore. --white 0 rebuilds v4's black materials exactly."""
    head = S.build_head("KQ_Coupon", hole_mat=M_BORE)
    tuck = L.fopt(o, "tuck", S.TUCK / MM) * MM
    keep = S.LIP + tuck
    mats = [S.face_carbon(o), S.mat_bore(o, tuck=tuck)] + [S.mat_ply(k, o, keep_z=keep) for k in KINDS] + \
        [S.mat_core(o)]
    cuts = S.coupon_cuts()
    return S.Carver(head, cuts, kq_regions, mats, chamfer_mat=S.mat_chamfer_white(o, keep_z=keep))


def setup(o, variant):
    R.scene(o)
    car = build(o)
    floor = S.build_floor(o=o)
    full = variant == "full" or bool(o.get("each"))
    R.lights([car.obj], floor, car, shell=full, o=o)
    R.camera(o)
    if o.get("autofit"):
        R.fit(o, [car.obj])
    if o.get("both"):
        rib = bpy.data.objects["lg_shell"]
        L.assign_groups([rib], "shell")
        L.both_variants(o, "shell", L.out_path(o["out"] + "-base")[:-4], glow_on_full=True)
    elif full:
        L.shell_glow(o)
    return car


def line_mask(o):
    """--line_mask: render ONLY the lg_shell hairline as a linear white profile (Standard view, no bounces, no
    denoise): geometry, occlusion and depth of field come from the render; k03s_line.py colours it (#ffe2bf core,
    #e3a467 edges, a soft amber halo) and lays it over a base still, so base and full differ only at the line and
    K03 and K03b carry the identical line."""
    sc = bpy.context.scene
    for ob in L.LIGHTS:
        ob.hide_render = ob.name != "lg_shell"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.cycles.max_bounces = 0
    sc.cycles.use_denoising = False
    sc.cycles.use_adaptive_sampling = False
    r = sc.render  # only the rim region is rendered; the rest of the full-size frame stays black
    r.use_border = True
    r.use_crop_to_border = False
    r.border_min_x, r.border_max_x = L.fopt(o, "mx0", 0.50), L.fopt(o, "mx1", 0.70)
    r.border_min_y, r.border_max_y = L.fopt(o, "my0", 0.40), L.fopt(o, "my1", 0.64)
    o["nodither"] = True


if __name__ == "__main__":
    o = L.parse_args()
    t0 = time.time()
    if o.get("line_mask"):
        car = setup(o, "full")
        line_mask(o)
        print("rendered", L.finish(o, "K03_line_mask"), round(time.time() - t0, 1), "s")
        sys.exit(0)
    car = setup(o, "full" if o.get("both") else o["variant"])
    print("geometry", round(time.time() - t0, 1), "s")
    if o.get("fit"):
        print("FRAME BBOX x0 x1 y0 y1 (top-down):", [round(v, 4) for v in L.frame_bbox([car.obj])])
    p = L.finish_both(o, o["out"]) if o.get("both") else L.finish(o, "K03_preview")
    print("rendered", p, round(time.time() - t0, 1), "s")
