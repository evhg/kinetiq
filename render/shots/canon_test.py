"""canon_test: proof renders of the canonical racket (shots/kq_canon.py), one studio per view.

Views (portrait unless noted):
  front   the whole racket face-on (turned 7 deg toward camera-left: a sliver of the right wall), one diagonal
          softbox sweep across the face (lit twill / black gloss), white hairline on the upper-left edge, ember
          hairline on the right edge, a grip strip, a graphite halo behind (camera rays only)
  handle  close-up from front-left-above: throat bridge + serial, the neck flowing into the grip, wrap, cap, groove, Q
Command is WHITE carbon (owner, 2026-10-22): it gets WHITE_DEFAULTS per view (a soft spot pool or a key, a weak fill,
a stronger gloss line); Pace and {"white": 0} keep the black-carbon reflection-only studios.
  q34     (landscape) the racket at 3/4, the side wall, edge fold and the KINETIQ wall etch

Usage (from the blender dir, through the lock):
  flock render.lock ../bpyenv/bin/python shots/canon_test.py --view front --feel command --w 720 --h 1280 --spp 32 --out canon/front_command
  ../bpyenv/bin/python shots/canon_test.py --sheet   (contact sheet of out/canon/*.png -> out/canon/canon_sheet.png)
Dev flags: any --key value read with f(o, key, default) below.
"""
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402
import k12_lib as K  # noqa: E402
import k10_lib as L  # noqa: E402
import kq_canon as C  # noqa: E402

EMBER = (1.0, 0.23, 0.12)
WHITE = (0.95, 0.97, 1.0)
ZT = C.ZT


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 720, "h": 1280, "spp": 32, "out": "canon/test", "view": "front", "feel": "command"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
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


def f(o, k, d):
    return float(o.get(k, d))


def mirror(cam_loc, P, n):
    d = (Vector(P) - Vector(cam_loc)).normalized()
    n = Vector(n).normalized()
    return (d - 2 * d.dot(n) * n).normalized()


def edge_ribbon(name, cam_loc, weight_fn, phi_deg, ed, ew, strength, color, recv, step=2):
    """A camera-invisible ribbon that every point of the outline's FRONT rounded edge (at bevel angle phi) mirrors
    into the camera: one continuous hairline along the edge, brightness = weight_fn(x, y) (0..1)."""
    out = C.outline_canon()
    if racket._area(out) < 0:
        out.reverse()
    i0 = min(range(len(out)), key=lambda i: out[i][1])  # start at the butt: every ribbon is one run
    out = out[i0:] + out[:i0]
    nrm = L._normals(out, 2)
    phi = math.radians(phi_deg)
    A, B, W = [], [], []
    n = len(out)
    for i in range(0, n, step):
        x, y = out[i]
        w = weight_fn(x, y)
        if w <= 1e-3 and (not A or W[-1] <= 1e-3):
            if A:
                break
            continue
        nx, ny = nrm[i]
        R = C.edge_radius(y)
        c = Vector((x - nx * R, y - ny * R, ZT - R))
        nn = Vector((nx * math.sin(phi), ny * math.sin(phi), math.cos(phi)))
        P = c + nn * R
        r = mirror(cam_loc, P, nn)
        E = P + r * ed
        q1, q0 = out[(i + 2) % n], out[i - 2]
        t = Vector((q1[0] - q0[0], q1[1] - q0[1], 0.0)).normalized()
        bv = r.cross(t).normalized()
        A.append(tuple(E - bv * ew / 2))
        B.append(tuple(E + bv * ew / 2))
        W.append(w)
    if len(A) < 2:
        return None
    rb = L.weighted_ribbon(name, A, B, W, strength, color=color, soft_v=0.2)
    L.link_only(rb, recv, name + "_recv")
    return rb


def sm(x, e0, e1):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def backdrop(cam_loc, centre, normal, size, lum_c, lum_e, radius, name="Backdrop"):
    """Camera-only graphite plane: a soft halo (display luma lum_c) behind `centre`, falling to lum_e."""
    bg = K.plane(name, size, tuple(centre), normal_to=tuple(Vector(centre) + Vector(normal)))
    c0 = Vector(centre)

    def s(nb):
        x, y, _ = nb.coords("Object")
        r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", x, x), nb.math("MULTIPLY", nb.math("MULTIPLY", y, 1.25), nb.math("MULTIPLY", y, 1.25))))
        return nb.lerp(nb.smooth(r, 0.0, radius), K.emit_for(lum_c), K.emit_for(lum_e))

    bg.data.materials.append(K.emitter_mat(name + "Mat", (0.93, 0.95, 1.0), s, additive=False))
    K.visibility(bg, camera=True, diffuse=False, glossy=False, shadow=False)
    return bg


def strip(name, loc, target, length, width, energy, color=WHITE, recv=None):
    """Long thin area light, long axis along world Y (studio.aim keeps local Y up)."""
    lt = studio.area_light(name, tuple(loc), width, energy, color=color, size_y=length, target=tuple(target))
    look_at(lt, loc, target)
    if recv:
        L.link_only(lt, recv, name + "_recv")
    return lt


def look_at(ob, loc, tgt, up=(0.0, 1.0, 0.0)):
    """Camera / light orientation with an explicit world up (studio.aim rolls freely when looking along Z)."""
    from mathutils import Matrix
    fwd = (Vector(tgt) - Vector(loc)).normalized()
    rt = fwd.cross(Vector(up)).normalized()
    upv = rt.cross(fwd)
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ Matrix((rt, upv, -fwd)).transposed().to_4x4()


def camera(o, cam_loc, tgt, frame_h, fstop, up=(0.0, 1.0, 0.0)):
    D = (Vector(tgt) - Vector(cam_loc)).length
    cam = studio.camera(tuple(cam_loc), tuple(tgt), lens=36.0, fstop=fstop)
    look_at(cam, cam_loc, tgt, up)
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 36.0
    cam.data.lens = 36.0 * D / frame_h
    cam.data.dof.focus_distance = D + f(o, "focus_dz", 0.0)
    return cam


def cap_light(name, cam_loc, P, energy, size=0.30, dist=0.35):
    """A small softbox in the mirror direction of the cap's front band: the groove and the engraved K catch it."""
    pr = C.cap_profile()
    yk = -0.2998 + C.CAP_SHIFT
    s_k = float(np.interp(-yk, [-y for (_, y) in pr], [s_ for (s_, _) in pr]))
    G, _ = C.section(64, grow=C.TAPE)
    Pc = Vector((0.0, yk, float(G[:, 1].max()) * s_k))
    r = mirror(cam_loc, Pc, (0, 0, 1))
    lt = studio.area_light(name, tuple(Pc + r * dist), size, energy, color=WHITE, size_y=size * 0.35, target=tuple(Pc))
    L.link_only(lt, [P["cap"], P["capmark"]], name + "_recv")
    return lt


# White Command (owner, 2026-10-22): the black-carbon studios light by reflection only, which leaves white carbon a flat
# grey. White gets a real key (a soft area light at a raking angle: it sets a gradient across the face and rakes the tow
# relief, so the twill reads in light and in shade), a weak fill so the shade side stays white-in-shadow rather than
# dirty grey, and a stronger coat sweep so the clear coat still shows one crisp gloss line. Values are per view.
WHITE_DEFAULTS = {
    "front": dict(pool=230.0, pool_deg=20.0, pool_x=-0.62, pool_y=0.57, pool_z=0.82, pool_tx=-0.06, pool_ty=0.06,
                  key=0.0, fill=1.0, wall=1.0, sky=2.0, gloss=36.0),
    "handle": dict(pool=95.0, pool_deg=24.0, pool_x=-0.55, pool_y=0.25, pool_z=0.75, pool_tx=-0.02, pool_ty=-0.12,
                   key=0.0, fill=0.8, rake=1.0, sky=1.0, gloss=30.0),
    "q34": dict(pool=0.0, key=10.0, key_x=-0.30, key_y=0.40, key_z=0.60, key_s=0.5, key_ty=-0.04, fill=2.0, side=1.4,
                sky=1.2, rake=0.0),
    "side": dict(pool=0.0, key=10.0, key_x=0.45, key_y=0.10, key_z=0.55, key_s=0.5, key_ty=-0.17, fill=2.0, side=0.7,
                 top=3.0),
}
FILL_AT = {"front": (0.75, -0.45, 0.90), "handle": (0.45, -0.30, 0.50), "q34": (0.90, -0.30, 0.20),
           "side": (0.80, -0.20, -0.30)}


def white_key(o, view, P):
    """The white racket's key and fill (head parts only: the grip and cap keep their own strips)."""
    recv = [P[k] for k in P if k not in ("grip", "cap", "capmark")]
    tgt = (0.0, f(o, "key_ty", -0.03), 0.0)
    tgt = (f(o, "key_tx", 0.0), f(o, "key_ty", -0.03), 0.0)
    if f(o, "pool", 0.0) > 0:  # a soft spot pool: lit upper side, the shade falling away diagonally across the face
        pl = studio.spot_light("lw_pool", (f(o, "pool_x", -0.6), f(o, "pool_y", 0.55), f(o, "pool_z", 0.8)),
                               f(o, "pool", 60.0), f(o, "pool_deg", 30.0), blend=1.0, color=(1.0, 0.985, 0.97),
                               target=(f(o, "pool_tx", -0.06), f(o, "pool_ty", 0.06), 0.0), radius=f(o, "pool_r", 0.06))
        L.link_only(pl, recv, "pool_recv")
    key = studio.area_light("lw_key", (f(o, "key_x", -0.5), f(o, "key_y", 0.5), f(o, "key_z", 0.7)), f(o, "key_s", 0.5),
                            f(o, "key", 30.0), color=(1.0, 0.985, 0.97), target=tgt, spread=f(o, "key_spread", 180.0))
    L.link_only(key, recv, "key_recv")
    fill = studio.area_light("lw_fill", FILL_AT[view], 1.0, f(o, "fill", 3.0), color=(0.94, 0.96, 1.0), target=tgt)
    L.link_only(fill, recv, "fill_recv")


def build(o):
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 6
    sc.cycles.diffuse_bounces = 2
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.blur_glossy = 0.5
    sc.cycles.adaptive_threshold = f(o, "noise", 0.01)
    t0 = time.time()
    mo = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in str(o["mat"]).split(",")} if o.get("mat") else None
    white = C.is_white(o["feel"], mo)
    if white:  # white carbon is lit by real diffuse light, not by reflections only: per-view defaults (CLI still wins)
        for k_, v_ in WHITE_DEFAULTS.get(o["view"], {}).items():
            o.setdefault(k_, v_)
    root, P = C.build_racket("KQ", feel=o["feel"], serial=o.get("serial", C.SERIAL), mat_opts=mo)
    if o.get("clone_serial"):  # prove clone(): render a linked duplicate carrying its own serial, source hidden
        r2, P2 = C.clone(root, "KQ2", serial=str(o["clone_serial"]))
        for ob in [root] + list(P.values()):
            ob.hide_render = True
        root, P = r2, P2
    print("racket built %.1f s" % (time.time() - t0), flush=True)
    view = o["view"]
    head = [P[k] for k in ("face", "rim", "holes")]
    if view == "front":
        yaw = math.radians(f(o, "yaw", 7.0))
        D = f(o, "dist", 2.3)
        tgt = Vector((0.0, -0.0725, 0.0))
        cam_loc = tgt + Vector((-math.sin(yaw), 0.0, math.cos(yaw))) * D
        frame_h = f(o, "frame_h", 0.505)
        cam = camera(o, cam_loc, tgt, frame_h, 11.0)
        backdrop(cam_loc, (0.0, 0.0, -0.45), (0, 0, 1), (3.0, 3.0), f(o, "bg_c", 36), f(o, "bg_e", 16), 0.55)
        # the sweep: a projected softbox whose reflection is a diagonal edge from upper left to lower right
        a_ = (f(o, "sa_x", -0.13), f(o, "sa_y", 0.155), ZT)
        b_ = (f(o, "sb_x", 0.13), f(o, "sb_y", -0.08), ZT)
        sky = L.sky_projected("lg_sky", cam_loc, ZT, a_, b_, (0.0, 0.02, ZT), (2.4, 2.4), 1.0,
                              0.0, 0.0, f(o, "sky", 1.2), floor=f(o, "sky_floor", 0.0), color=WHITE,
                              band=(f(o, "s_off", 0.0), f(o, "s_bw", 0.07)))
        gl = L.sky_projected("lg_gloss", cam_loc, ZT, a_, b_, (0.0, 0.02, ZT), (3.2, 3.2), 1.4, 0.0, 0.0,
                             f(o, "gloss", 4.0), color=WHITE, band=(f(o, "g_off", -0.030), f(o, "g_bw", 0.0016)))
        L.link_only(gl, [P["face"]], "gloss_recv")
        L.link_only(sky, [P["face"], P["holes"], P["rim"], P["neck"]], "sky_recv")
        # hairlines
        edge_ribbon("lg_white", cam_loc, lambda x, y: sm(-x, 0.004, 0.03) * sm(y, 0.0, 0.06) if x < 0 else 0.0,
                    f(o, "phi_w", 40), 0.15, f(o, "ew", 0.03), f(o, "white", 25.0), WHITE, [P["rim"]])
        edge_ribbon("lg_ember", cam_loc, lambda x, y: sm(x, 0.02, 0.06) * sm(y, -0.075, -0.035) * sm(-y, -0.135, -0.09) if x > 0 else 0.0,
                    f(o, "phi_e", 40), 0.15, f(o, "ew", 0.03), f(o, "ember", 35.0), EMBER, [P["rim"]])
        cap_light("lg_cap", cam_loc, P, f(o, "cap", 0.3))
        # grip + neck strip from camera-left, and a dim one from the right for the far side of the wrap
        strip("lg_grip", (-0.32, -0.22, 0.30), (0.0, -0.22, 0.0), 0.32, 0.02, f(o, "grip", 1.2),
              recv=[P["grip"], P["cap"], P["capmark"], P["neck"]])
        strip("lg_grip2", (0.30, -0.22, 0.12), (0.0, -0.22, 0.0), 0.32, 0.03, f(o, "grip2", 0.3),
              recv=[P["grip"], P["cap"], P["neck"]])
        # right wall sliver
        strip("lg_wall", (0.6, 0.0, 0.25), (0.13, 0.0, 0.0), 0.5, 0.1, f(o, "wall", 6.0), recv=[P["wall"], P["rim"]])
    elif view == "handle":
        tgt = Vector((0.0, f(o, "ty", -0.205), 0.0))
        az, el = math.radians(f(o, "az", -32.0)), math.radians(f(o, "el", 38.0))
        D = f(o, "dist", 0.95)
        dirv = Vector((math.sin(az) * math.cos(el), -math.sin(el) * f(o, "below", 0.35), math.cos(az) * math.cos(el))).normalized()
        cam_loc = tgt + dirv * D
        frame_h = f(o, "frame_h", 0.255)
        cam = camera(o, cam_loc, tgt, frame_h, f(o, "fstop", 8.0))
        backdrop(cam_loc, (0.0, -0.2, -0.35), (0, 0, 1), (3.0, 3.0), f(o, "bg_c", 34), f(o, "bg_e", 16), 0.30)
        # face sweep over the lower head and bridge
        a_ = (f(o, "sa_x", -0.10), f(o, "sa_y", -0.02), ZT)
        b_ = (f(o, "sb_x", 0.10), f(o, "sb_y", -0.14), ZT)
        sky = L.sky_projected("lg_sky", cam_loc, ZT, a_, b_, (0.0, -0.12, ZT), (2.0, 2.0), 0.8,
                              0.0, 0.0, f(o, "sky", 1.0), color=WHITE, band=(f(o, "s_off", 0.0), f(o, "s_bw", 0.016)))
        gl = L.sky_projected("lg_gloss", cam_loc, ZT, a_, b_, (0.0, -0.12, ZT), (3.0, 3.0), 1.2, 0.0, 0.0,
                             f(o, "gloss", 4.0), color=WHITE, band=(f(o, "g_off", -0.012), f(o, "g_bw", 0.0012)))
        L.link_only(gl, [P["face"]], "gloss_recv")
        cap_light("lg_cap", cam_loc, P, f(o, "cap", 0.3))
        L.link_only(sky, [P["face"], P["holes"], P["neck"], P["rim"]], "sky_recv")
        # rake for the frosted serial, from camera-left, grazing
        S = Vector((0.0, -0.1365, ZT))
        rd = Vector((-math.cos(math.radians(16)), 0.25, math.sin(math.radians(16)))).normalized()
        rake = studio.area_light("lg_rake", tuple(S + rd * 0.125), 0.05, f(o, "rake", 1.0), color=(1.0, 0.985, 0.965),
                                 size_y=0.005, target=tuple(S))
        L.link_only(rake, [P["face"]], "rake_recv")
        # grip strip and the cap
        strip("lg_grip", (-0.30, -0.23, 0.26), (0.0, -0.23, 0.0), 0.30, 0.015, f(o, "grip", 1.0),
              recv=[P["grip"], P["cap"], P["capmark"], P["neck"]])
        strip("lg_grip2", (0.28, -0.25, 0.10), (0.0, -0.25, 0.0), 0.30, 0.03, f(o, "grip2", 0.25),
              recv=[P["grip"], P["cap"], P["neck"]])
        edge_ribbon("lg_ember", cam_loc, lambda x, y: sm(x, 0.02, 0.05) * sm(y, -0.20, -0.14) * sm(-y, 0.0, 0.05) if x > 0 else 0.0,
                    f(o, "phi_e", 45), 0.12, 0.004, f(o, "ember", 40.0), EMBER, [P["rim"], P["neck"]])
        edge_ribbon("lg_white", cam_loc, lambda x, y: sm(-x, 0.02, 0.05) * sm(y, -0.20, -0.14) * sm(-y, 0.0, 0.05) if x < 0 else 0.0,
                    f(o, "phi_w", 45), 0.12, 0.004, f(o, "white", 30.0), WHITE, [P["rim"], P["neck"]])
    elif view == "q34":
        # the head's right side at 3/4: the weave folding over the 1.5 mm edge onto the 38 mm wall, the wall etch
        tgt = Vector((f(o, "tx", 0.095), f(o, "ty", -0.045), 0.0))
        az, el = math.radians(f(o, "az", 58.0)), math.radians(f(o, "el", 14.0))
        D = f(o, "dist", 1.2)
        dirv = Vector((math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el))).normalized()
        cam_loc = tgt + dirv * D
        cam = camera(o, cam_loc, tgt, f(o, "frame_h", 0.20), f(o, "fstop", 11.0))
        backdrop(cam_loc, tuple(tgt - dirv * 0.5), tuple(dirv), (3.0, 3.0), f(o, "bg_c", 36), f(o, "bg_e", 18), 0.35)
        Cf = Vector((0.06, 0.0, ZT))
        sky = L.sky_projected("lg_sky", cam_loc, ZT, (-0.05, 0.10, ZT), (0.13, -0.10, ZT), tuple(Cf), (3.0, 3.0), 1.0,
                              0.0, 0.0, f(o, "sky", 1.2), color=WHITE, band=(f(o, "s_off", 0.0), f(o, "s_bw", 0.02)))
        L.link_only(sky, [P["face"], P["holes"], P["rim"]], "sky_recv")
        # the right wall: a soft gradient card in its mirror direction, fading along it
        Pw = Vector((0.1285, -0.045, 0.0))
        nw = Vector((0.97, -0.24, 0.0)).normalized()
        rw = mirror(cam_loc, Pw, nw)
        pw = L.panel("lg_side", tuple(Pw + rw * 0.6), (1.0, 0.5), f(o, "side", 0.45), tuple(Pw), color=WHITE,
                     roll=90.0, edge=(-0.8, 1.0), fade=(0, 0.95))
        L.link_only(pw, [P["wall"], P["rim"]], "side_recv")
        rake = studio.area_light("lg_rake", (0.150, -0.20, 0.0), 0.03, f(o, "rake", 3.0), size_y=0.005,
                                 target=(0.1285, -0.062, 0.0))
        L.link_only(rake, [P["etchR"]], "rake_recv")
        edge_ribbon("lg_white", cam_loc, lambda x, y: sm(x, 0.06, 0.11) * sm(y, -0.12, -0.08) * sm(-y, -0.06, 0.0) if x > 0 else 0.0,
                    f(o, "phi_w", 30), 0.15, 0.02, f(o, "white", 25.0), WHITE, [P["rim"]])
    elif view == "side":
        # profile of the lower racket seen from its right side, face up: 38 mm head, the neck lofting to 29 mm, grip, cap
        tgt = Vector((0.0, f(o, "ty", -0.170), 0.0))
        D = f(o, "dist", 1.4)
        cam_loc = tgt + Vector((D, 0.0, f(o, "cz", 0.0)))
        cam = camera(o, cam_loc, tgt, f(o, "frame_h", 0.17), f(o, "fstop", 11.0), up=(0.0, 0.0, 1.0))
        backdrop(cam_loc, (-0.5, -0.17, 0.0), (1, 0, 0), (3.0, 3.0), f(o, "bg_c", 36), f(o, "bg_e", 18), 0.30)
        # the wall faces the camera: a soft card behind the camera, graded along the racket
        Pw = Vector((0.03, -0.17, 0.0))
        rw = mirror(cam_loc, Pw, (1, 0, 0))
        pw = L.panel("lg_side", tuple(Pw + rw * 0.5), (4.0, 1.2), f(o, "side", 0.7), tuple(Pw), color=WHITE,
                     edge=(0.0, 0.45), band=(0.55, 1.0, 0.0), fade=(0, 0.9))
        L.link_only(pw, [P["wall"], P["rim"], P["neck"], P["etchR"]], "side_recv")
        # front edge hairline (strip above), ember on the rear edge (strip below)
        st = strip("lg_top", (0.0, -0.17, 0.45), (0.0, -0.17, 0.0), 0.8, 0.02, f(o, "top", 3.0),
                   recv=[P["rim"], P["wall"], P["neck"], P["grip"], P["cap"]])
        st2 = strip("lg_bot", (0.0, -0.17, -0.45), (0.0, -0.17, 0.0), 0.8, 0.02, f(o, "bot", 2.0), color=EMBER,
                    recv=[P["rim"], P["wall"], P["neck"]])
        strip("lg_grip", (0.35, -0.24, 0.20), (0.0, -0.24, 0.0), 0.25, 0.015, f(o, "grip", 0.8),
              recv=[P["grip"], P["cap"], P["capmark"]])
    else:
        raise ValueError(view)
    if white:
        white_key(o, view, P)
    bpy.context.view_layer.update()
    return sc


def sheet(o):
    from PIL import Image, ImageDraw
    d = os.path.join(studio.OUT, "canon")
    order = ["front_command", "front_pace", "handle_command", "handle_pace", "handle_clone428", "side_command", "q34_command"]
    tiles = []
    for nm in order:
        p = os.path.join(d, nm + ".png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            nm = nm.replace("_command", "_command (white)").replace("_pace", "_pace (black 12K)").replace("_clone428", "_clone428 (white)")
            im.thumbnail((720, 720 if im.width > im.height else 1280))
            tiles.append((nm, im))
    H = 960
    row1 = [t for t in tiles if t[1].height >= t[1].width]
    row2 = [t for t in tiles if t[1].height < t[1].width]
    scaled = []
    for nm, im in row1:
        w = int(im.width * H / im.height)
        scaled.append((nm, im.resize((w, H), Image.LANCZOS)))
    W = sum(im.width for _, im in scaled) + 8 * (len(scaled) + 1)
    s2 = []
    w2 = (W - 8 * (len(row2) + 1)) // max(1, len(row2))
    for nm, im in row2:
        s2.append((nm, im.resize((w2, int(im.height * w2 / im.width)), Image.LANCZOS)))
    h2 = max([im.height for _, im in s2] + [0]) + 8
    out = Image.new("RGB", (W, H + 16 + h2), (40, 40, 44))
    dr = ImageDraw.Draw(out)
    x = 8
    for nm, im in scaled:
        out.paste(im, (x, 8))
        dr.text((x + 8, 14), nm, fill=(255, 140, 80))
        x += im.width + 8
    y, x = H + 16, 8
    for nm, im in s2:
        out.paste(im, (x, y))
        dr.text((x + 8, y + 6), nm, fill=(255, 140, 80))
        x += im.width + 8
    dst = os.path.join(d, "canon_sheet.png")
    out.save(dst)
    print("sheet", dst, out.size)


def main():
    o = parse_args()
    if o.get("sheet"):
        sheet(o)
        return
    t0 = time.time()
    sc = build(o)
    out = os.path.join(studio.OUT, o["out"] + ".png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    if o.get("dry"):
        print("dry", round(time.time() - t0, 1), "s")
        return
    bpy.ops.render.render(write_still=True)
    print("wrote", out, round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
