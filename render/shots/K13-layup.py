"""K13-layup (Release 2, 2026-10-23): the Space-grade carbon section's photograph. An abstract macro of the KINETIQ
laminate: a polished cut through the 2.0 mm shell, the white 3K face ply (Command, the canon's white twill on top)
over dense unidirectional plies, fibres packed close and even with solid resin between them (no voids), under a cool,
precise light, in the graphite studio language of K03 / K04. No product, no text, no other objects.

Scale (true to the laminate): 7 um fibres at about 60 % by volume (hexagonal-equivalent pitch 8.6 um, random close
packing), 0.22 mm UD plies (0, 90, +45 deg) with 15 um resin lines, a 0.30 mm white 2/2 twill face ply (2.6 mm tows)
under a 30 um clear coat. The camera sees about 8 mm at the cut (about 5x, a macro, not a micrograph), so a fibre end
is about 3 px at 3200 px: the 0 deg plies read as a dense, even field of fibre ends, the 90 deg plies as fine streaks,
the 45 deg plies as elongated ends. The sample floats in a graphite void (camera-only backdrop gradient).

Usage (from blender/): ../bpyenv/bin/python shots/K13-layup.py --w 960 --h 540 --spp 32 --out p13/k13_a
Final: --w 3200 --h 1800 --spp 256 --out final/K13-layup
Crops (stills.json): wide (full), card (x .275 w .45), portrait (x .341 w .316): the subject stays in the centre 45 %.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import k03_lib as L  # noqa: E402
import k03s_lib as S  # noqa: E402
import studio  # noqa: E402

f = L.fopt
MM = 0.001
T = 2.0 * MM            # shell thickness
X0, X1 = -0.020, 0.020  # slab length (the cut runs along x)
DEPTH = 0.016           # slab depth behind the cut (y)
CH = 0.035 * MM         # polished 45 deg chamfer on the cut's top edge
FIB_R = 3.5e-6          # fibre radius (7 um fibres)
PITCH = 8.6e-6          # mean fibre spacing at about 60 % fibre volume
TOW = 2.6 * MM          # 3K tow width (the canon's twill)

# the laminate, top down: (thickness mm, kind)
PLIES = [(0.030, "coat"), (0.300, "W"), (0.015, "r")]
for _k in ("U0", "U90", "U45", "U0", "U90", "U45", "U0"):
    PLIES += [(0.220, _k), (0.015, "r")]
PLIES[-1] = (0.0, "r")
_tot = sum(t for t, _ in PLIES)
PLIES[-1] = (2.0 - _tot, "r")


def build_slab():
    """Box with a 45 deg chamfer on the cut's top edge. Material slots: 0 top / sides / back (white twill skin),
    1 the polished cut (section), 2 the chamfer."""
    bm = bmesh.new()
    V = bm.verts.new
    # profile in (y, z) at the cut end, going round: bottom-front, front-top (below chamfer), chamfer-top, back-top,
    # back-bottom
    prof = [(0.0, 0.0), (0.0, T - CH), (CH, T), (DEPTH, T), (DEPTH, 0.0)]
    nx = 160
    xs = [X0 + (X1 - X0) * i / nx for i in range(nx + 1)]
    grid = [[V((x, y, z)) for (y, z) in prof] for x in xs]
    faces = []
    for i in range(nx):
        for j in range(len(prof)):
            a, b = grid[i][j], grid[i][(j + 1) % len(prof)]
            c, d = grid[i + 1][(j + 1) % len(prof)], grid[i + 1][j]
            fc = bm.faces.new((a, d, c, b))
            fc.material_index = {0: 1, 1: 2}.get(j, 0)
            faces.append(fc)
    for col in (grid[0], grid[-1]):
        fc = bm.faces.new(col if col is grid[-1] else list(reversed(col)))
        fc.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("K13_slab")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("K13_slab", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ------------------------------------------------------------------ section material
def _between(b, t, t0, t1):
    return b.mul(b.math("GREATER_THAN", t, t0 - 1e-9), b.math("LESS_THAN", t, t1))


def _fibre_ends(b, u, z, sx=1.0, seed=0.0, o=None):
    """Close-packed fibre ends: (mask 0..1, per-fibre random 0..1). Voronoi cells of jittered points: each fibre is
    its cell, rounded (F1 < fib_r) and kept off its neighbours by a thin resin line (distance to the cell edge), so the
    ply reads dense and even with no gaps. u, z in metres; sx stretches the ends along u (45 deg ply: 1.41)."""
    o = o or {}
    vec = b.vec(b.div(u, PITCH * sx), b.div(z, PITCH), seed)

    def vor(feature):
        vo = b.nodes.new("ShaderNodeTexVoronoi")
        vo.voronoi_dimensions = "3D"
        vo.feature = feature
        b._set(vo.inputs["Vector"], vec)
        vo.inputs["Scale"].default_value = 1.0
        vo.inputs["Randomness"].default_value = f(o, "fib_rand", 0.55)
        return vo
    v1 = vor("F1")
    ve = vor("DISTANCE_TO_EDGE")
    r = f(o, "fib_r", 0.50)
    gap = f(o, "fib_gap", 0.05)
    mask = b.mul(b.sub(1.0, b.smooth(r - 0.06, r + 0.02, v1.outputs["Distance"])),
                 b.smooth(gap * 0.4, gap * 1.6, ve.outputs["Distance"]))
    rnd = b.sep(v1.outputs["Color"])[0]
    return mask, rnd


def mat_section(o):
    m = bpy.data.materials.new("K13_section")
    b = S.NB(m)
    p = b.tc("Object")
    x, y, z = b.sep(p)
    t = b.sub(T, z)                      # depth below the top surface
    # ply masks
    masks = {}
    d = 0.0
    for th, kind in PLIES:
        mk = _between(b, t, d * MM, (d + th) * MM)
        masks[kind] = mk if kind not in masks else b.add(masks[kind], mk)
        if kind == "W":
            w0, w1 = d * MM, (d + th) * MM
        d += th
    tint = (1.0, 1.0, 1.0)
    # --- UD 0: fibre ends, dense and even; carbon fibre ends polish to a graphite mirror, the resin between is darker
    f0, r0 = _fibre_ends(b, x, z, 1.0, 0.0, o)
    f45, r45 = _fibre_ends(b, x, z, 1.41, 7.0, o)
    # v2 (coordinator review of final 1: "the cut face reads grainy, like render noise, at page size"): a 3 px fibre
    # end cannot be resolved on the page, so full-contrast ends read as sensor noise. fib_con pulls each end toward the
    # ply's mean (a polished ply reads as one even, dense satin with a fine shimmer at 1:1), fib_var evens the fibres
    fc_ = f(o, "fib_con", 0.30)
    f0 = b.lerp(0.62, f0, fc_)
    f45 = b.lerp(0.62, f45, fc_)
    # --- UD 90: fibres lying along the cut: fine streaks across z at the fibre pitch, long along x
    st = b.noise(b.vec(b.div(x, f(o, "u90_len", 0.02)), b.div(z, PITCH * 1.2), 5.0), 1.0, 3.0, 0.55)
    f90 = b.smooth(f(o, "u90_lo", 0.30), f(o, "u90_hi", 0.70), st)
    n90 = b.remap(b.noise(b.vec(b.div(x, 0.0012), b.div(z, PITCH * 3), 3.0), 1.0, 2.0), 0.3, 0.7, 0.8, 1.2)
    # --- white 3K twill ply (2/2): weft tows cut across = lenses of white fibre ends; warp along the cut = streaks
    dd = b.clamp01(b.div(b.sub(t, w0), w1 - w0))
    x4 = b.math("FRACT", b.div(b.add(x, 0.0007), 4 * TOW))
    x1 = b.math("FRACT", b.mul(x4, 4.0))
    over = b.smooth(-0.4, 0.4, b.math("SINE", b.mul(b.sub(x4, 0.125), 2 * math.pi)))
    cen = b.lerp(0.30, 0.70, over)
    e = b.div(b.sub(x1, 0.5), 0.48)
    hh = b.mul(b.math("SQRT", b.clamp01(b.sub(1.0, b.mul(e, e)))), 0.30)
    dist = b.math("ABSOLUTE", b.sub(dd, cen))
    lens = b.sub(1.0, b.smooth(b.sub(hh, 0.02), hh, dist))
    rim = b.mul(b.smooth(b.sub(hh, 0.07), b.sub(hh, 0.01), dist), lens)   # the resin skin round each tow
    fw, rw = _fibre_ends(b, x, z, 1.0, 13.0, o)
    fwarp = b.smooth(0.40, 0.62, b.noise(b.vec(b.div(x, 0.0015), b.div(z, PITCH * 1.2), 9.0), 1.0, 3.0, 0.55))
    # --- shading: carbon fibre ends polish to a graphite mirror (metallic, reflectance fib_alb); the resin between is a
    # dark glossy dielectric; so the section reads under the sheen card (fibres bright, resin lines dark) and stays a
    # deep graphite elsewhere. The white face ply is diffuse white fibre in clear resin.
    a_res = f(o, "res_alb", 0.010)
    a_f = f(o, "fib_alb", 0.30)
    wa_f, wa_r = f(o, "w_fib", 0.80), f(o, "w_res", 0.55)
    U = b.add(masks["U0"], masks["U45"])
    fib = b.add(b.add(b.mul(masks["U0"], f0), b.mul(masks["U45"], f45)), b.mul(masks["U90"], f90))
    rr = b.add(b.add(b.mul(masks["U0"], r0), b.mul(masks["U45"], r45)), b.mul(masks["U90"], 0.5))
    fcol = b.mul(b.mul(fib, a_f), b.mad(rr, f(o, "fib_var", 0.35), 1.0 - f(o, "fib_var", 0.35) / 2))
    metal = b.mul(fib, b.sub(1.0, masks["W"]))
    alb_wl = b.lerp(wa_r, b.mul(wa_f, b.mad(rw, 0.16, 0.92)), fw)
    alb_ww = b.lerp(wa_r * 1.25, wa_f * 0.97, fwarp)
    alb_w = b.mul(b.lerp(alb_ww, alb_wl, lens), b.sub(1.0, b.mul(rim, 0.5)))
    alb = b.add(b.lerp(a_res, fcol, metal), b.mul(masks["W"], b.sub(alb_w, a_res)))
    rough = b.lerp(f(o, "res_r", 0.07), f(o, "fib_rgh", 0.11), metal)
    rough = b.lerp(rough, b.lerp(0.20, 0.26, lens), masks["W"])
    col = b.vmath("MULTIPLY", b.vec(alb, alb, alb), b.vec(1.0, b.lerp(1.0, 0.99, masks["W"]),
                                                         b.lerp(1.03, 0.955, masks["W"])))
    sh = b.bsdf(base=col, rough=rough, spec=0.5, metal=metal)
    return b.output(sh)


def mat_skin(o):
    m = bpy.data.materials.new("K13_skin")
    b = S.NB(m)
    return b.output(S._white_bsdf(b, dict(o, cw_coat_r=f(o, "skin_coat_r", 0.03)), "skin"))


def mat_chamfer(o):
    """The chamfer cuts through the clear coat into the white face ply: polished white under a glass coat."""
    m = bpy.data.materials.new("K13_chamfer")
    b = S.NB(m)
    tint = S._cw(o)["tint"]
    v = f(o, "cham_alb", 0.80)
    sh = b.bsdf(base=tuple(c * v for c in tint), rough=0.08, spec=0.5, coat=1.0, coat_rough=0.02)
    return b.output(sh)


# ------------------------------------------------------------------ studio
def world_backdrop(o):
    """Camera-only graphite void: a soft vertical gradient with a lifted band behind the cut; black to every other
    ray (the studio lights everything)."""
    w = bpy.context.scene.world
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    lp = nt.nodes.new("ShaderNodeLightPath")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    # radial lift centred behind the cut (window coords)
    dx = nt.nodes.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = f(o, "bg_cx", 0.5)
    nt.links.new(sep.outputs["X"], dx.inputs[0])
    dy = nt.nodes.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = f(o, "bg_cy", 0.62)
    nt.links.new(sep.outputs["Y"], dy.inputs[0])
    sx = nt.nodes.new("ShaderNodeMath"); sx.operation = "MULTIPLY"; sx.inputs[1].default_value = 1.0 / f(o, "bg_rx", 0.75)
    nt.links.new(dx.outputs[0], sx.inputs[0])
    sy = nt.nodes.new("ShaderNodeMath"); sy.operation = "MULTIPLY"; sy.inputs[1].default_value = 1.0 / f(o, "bg_ry", 0.55)
    nt.links.new(dy.outputs[0], sy.inputs[0])
    cv = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sx.outputs[0], cv.inputs[0])
    nt.links.new(sy.outputs[0], cv.inputs[1])
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    nt.links.new(cv.outputs[0], ln.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = f(o, "bg_hi", 0.0105)
    mr.inputs["To Max"].default_value = f(o, "bg_lo", 0.0036)
    nt.links.new(ln.outputs["Value"], mr.inputs["Value"])
    cc = nt.nodes.new("ShaderNodeCombineColor")
    for i, k in enumerate((0.96, 1.0, 1.07)):
        mm = nt.nodes.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = k
        nt.links.new(mr.outputs["Result"], mm.inputs[0])
        nt.links.new(mm.outputs[0], cc.inputs[i])
    nt.links.new(cc.outputs[0], bg.inputs["Color"])
    nt.links.new(lp.outputs["Is Camera Ray"], bg.inputs["Strength"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])


COOL = (0.90, 0.95, 1.0)   # about 7000 K


def lights(o, slab, cam):
    P = Vector((0.0, 0.0, T / 2))
    cl = Vector(cam.location)
    v = (cl - P).normalized()
    # 1. section key: a soft cool area light, front-left and above, diffuse only: the fibre ends read by albedo
    kaz, kel = math.radians(f(o, "key_az", -55.0)), math.radians(f(o, "key_el", 35.0))
    kd = Vector((math.sin(kaz) * math.cos(kel), -math.cos(kaz) * math.cos(kel), math.sin(kel)))
    key = studio.area_light("lg_key", tuple(P + kd * 0.12), f(o, "key_size", 0.06), f(o, "key", 0.35), color=COOL,
                            target=tuple(P))
    key.visible_glossy = f(o, "key_gloss", 0.0) > 0
    # 2. section sheen: a soft gradient card on the cut's mirror rays (the polished face as a graphite-to-silver sweep,
    # its falloff edge crossing the frame on a diagonal), and a narrow slit on the same rays (one crisp band of light
    # across the plies, the fibre ends glinting inside it)
    n = Vector((0, -1, 0))
    r = (2 * v.dot(n) * n - v).normalized()
    sd = f(o, "sheen_d", 0.10)
    sc_ = L.card("lg_sheen", tuple(P + r * sd), (f(o, "sheen_w", 0.10), f(o, "sheen_h", 0.10)), f(o, "sheen", 3.0),
                 tuple(P), color=COOL, falloff="edge", edge=f(o, "sheen_edge", 0.7), edge0=f(o, "sheen_e0", 0.0),
                 roll=f(o, "sheen_roll", 30.0))
    side = r.cross(Vector((0, 0, 1))).normalized()
    upv = side.cross(r).normalized()
    sl_c = P + (r + side * f(o, "slit_x", 0.0) + upv * f(o, "slit_y", 0.0)).normalized() * sd
    slit = L.card("lg_slit", tuple(sl_c), (f(o, "slit_w", 0.004), 0.25), f(o, "slit", 0.0), tuple(P), color=COOL,
                  falloff="flat", roll=f(o, "slit_roll", 30.0))
    # 3. the chamfer's hairline: a thin strip on the chamfer's mirror rays
    nc = Vector((0, -1, 1)).normalized()
    rc = (2 * v.dot(nc) * nc - v).normalized()
    ln = L.card("lg_line", tuple(P + rc * 0.15), (0.30, f(o, "line_h", 0.006)), f(o, "line", 25.0), tuple(P),
                color=(1.0, 1.0, 1.0), falloff="flat")
    # 4. the white top: a soft pool from behind-left (diffuse light grading the twill) and a lacquer band on its mirror
    paz, pel = math.radians(f(o, "pool_az", 150.0)), math.radians(f(o, "pool_el", 40.0))
    pd = Vector((math.sin(paz) * math.cos(pel), -math.cos(paz) * math.cos(pel), math.sin(pel)))
    tgt = Vector((f(o, "pool_tx", 0.0), f(o, "pool_ty", 0.004), T))
    pool = studio.spot_light("lg_pool", tuple(tgt + pd * 0.3), f(o, "pool", 3.0), f(o, "pool_deg", 14.0), blend=1.0,
                             color=(1.0, 0.99, 0.98), target=tuple(tgt), radius=0.01)
    pool.visible_glossy = False
    nt_ = Vector((0, 0, 1))
    rt = (2 * v.dot(nt_) * nt_ - v).normalized()
    band = L.card("lg_band", tuple(P + rt * 0.2 + Vector((0, 0, f(o, "band_dz", 0.0)))), (0.4, f(o, "band_h", 0.012)),
                  f(o, "band", 6.0), tuple(P), color=COOL, falloff="soft")
    # light linking: everything on the slab only (the void is camera-only anyway)
    rx = L.link_receivers(key, [slab], "rx_slab")
    for ob in (sc_, slit, ln, pool, band):
        ob.light_linking.receiver_collection = rx
    for ob in (sc_, slit, ln, band):
        ob.visible_shadow = False


# the look chosen on previews (out/p13/k13_t, 2026-10-23): a graphite cut with one cool light shaft through the centre
# (the slit on the cut's mirror rays), a soft sweep, the white skin and face ply above, the void below
DEFAULTS = dict(fstop=70.0, fib_var=0.15, fib_gap=0.03, bg_hi=0.035, bg_lo=0.016, bg_cy=0.5, bg_ry=0.9,
                sheen_edge=0.5, sheen_e0=0.25, w_fib=0.9, el=6.0, az=-30.0, dist=0.026, roll=-5.0, pool=0.8, key=1.5,
                fib_alb=0.13, fib_con=0.30, slit=14.0, sheen=0.6, shift_y=-0.06)


def main():
    o = L.parse_args()
    for k_, v_ in DEFAULTS.items():
        o.setdefault(k_, v_)
    t0 = time.time()
    studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc = bpy.context.scene
    sc.cycles.max_bounces = 6
    sc.cycles.glossy_bounces = 4
    sc.cycles.adaptive_threshold = f(o, "noise", 0.008)
    slab = build_slab()
    for mt in (mat_skin(o), mat_section(o), mat_chamfer(o)):
        slab.data.materials.append(mt)
    world_backdrop(o)
    # camera: yawed off the cut, a little above it; about 8 mm seen at the cut
    tgt = Vector((f(o, "tx", 0.0), 0.0, f(o, "tz", T * 0.55)))
    az, el = math.radians(f(o, "az", -32.0)), math.radians(f(o, "el", 16.0))
    dist = f(o, "dist", 0.045)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam = studio.camera(tuple(tgt + d * dist), tuple(tgt), lens=f(o, "lens", 150.0),
                        shift=(f(o, "shift_x", 0.0), f(o, "shift_y", 0.0)))
    cam.data.clip_start = 0.002
    if f(o, "roll", 0.0):
        cam.rotation_euler.rotate_axis("Z", math.radians(f(o, "roll", 0.0)))
    fs = f(o, "fstop", 40.0)
    cam.data.dof.use_dof = fs > 0
    cam.data.dof.aperture_fstop = fs
    cam.data.dof.focus_distance = (Vector((f(o, "fx", 0.0), 0.0, T / 2)) - cam.location).length
    cam.data.dof.aperture_blades = 9
    lights(o, slab, cam)
    print("setup", round(time.time() - t0, 1), "s")
    print("rendered", L.finish(o, "p13/k13"), round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
