"""K15-space (2026-10-29): Space-grade carbon's photograph. Replaces G16 (the "morse code" micrograph) on the owner's
feedback: "rather show a piece of great looking carbon in a space setting".

The canonical racket (kq_canon: Command = white 3K twill, `--feel pace` = black 12K v6) seen close at its crown, from
just above the face, floating in deep space: the rim an arc across the frame, the twill crisp on the face, and beyond
the edge the limb of a dark planet with a thin warm atmosphere (amber near the sun, falling to a pale graphite glow
away from it), a few faint stars. No spacecraft, logos, flags, country or maker: only the material and the light.

Light (light groups, one render, two composites by gains: --comp re-grades from the EXR, --solo writes each group):
  sun     the key: a sun lamp (small angle, sharp shadows) raking in from beyond the rim near the coat's mirror
          direction, so the twill flips and one glint runs over the lacquer
  limb    the atmosphere's light on the edge: a warm glossy-only card beyond the rim, linked to the rim (one line)
  earth   the planet's dim bounce from beyond and below the edge (diffuse, warm graphite)
  fill    a whisper of cool fill so the shade side reads (diffuse only)
  planet  the planet and its atmosphere (camera-visible emission; never lights the racket)
Composites (one render): <out>-base.png (before sunrise: limb, earth, planet, the sun low: SUN_BASE) and
<out>-full.png (the sun up). The site cross-fades base -> full as the section scrolls past (a sunrise on the weave).
Stars are composited behind (frame space, seeded), only where nothing is in front (alpha).

Usage (from render/, through the lock):
  flock render.lock $PY shots/K15-space.py --w 960 --h 540 --spp 24 --out k15/p01 [--feel pace] [--set NAME=value ...]
  flock render.lock $PY shots/K15-space.py --comp k15/p01.exr --out k15/p01c [--set g_<group>=k ...] [--solo]
Finals:
  flock render.lock $PY shots/K15-space.py --w 2560 --h 1440 --spp 64 --out final/K15-space
  flock render.lock $PY shots/K15-space.py --feel pace --w 2560 --h 1440 --spp 64 --out final/K15-space-pace
  then render/link-masters.sh and node scripts/stills.mjs $KQ_RENDER_OUT/masters K15-base K15-full K15-base-pace ...
"""
import json
import math
import os
import struct
import sys
import time
import zlib
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import kqpaths  # noqa: E402,F401

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import studio  # noqa: E402
import kq_canon as C  # noqa: E402

_spec = importlib.util.spec_from_file_location("k04", os.path.join(HERE, "K04-hole-macro.py"))
K04 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K04)

ZT = C.ZT
GROUPS = ("sun", "limb", "gloss", "earth", "fill")

DEFAULTS = dict(
    # composition (as K14: a rim point, the camera inward of it looking out over the edge)
    PHI=90.0, YAW=0.0, EL=26.0, DIST=0.42, FW=0.17, TIN=0.03, SHIFT_X=0.0, SHIFT_Y=0.0, ROLL=0.0,
    FSTOP=22.0, FOCUS_IN=0.03,
    # planet (composited behind, frame space): centre (u 0..1 left to right, v 0..1 top to bottom, in frame WIDTHS
    # for both axes), radius in frame widths; SUN_PA: position angle of the sunward limb (deg, 0 = +u, 90 = up)
    PL_U=-0.25, PL_V=1.25, PL_R=1.0, SUN_PA=60.0, PL_SPREAD=55.0,
    PL_BODY=0.004, PL_NIGHT=0.012, PL_NW=0.08,   # body: base, airglow toward the limb, its width (x R)
    AT_LINE=0.35, AT_LW=0.0016, AT_GLOW=0.06, AT_GW=0.03, AT_FAR=0.18,   # limb line, outer glow, far-side level
    AT_BASE=0.45,                        # base composite: the limb's level before sunrise
    CR=0.10, CR_W=0.012, CR_K=3.0,       # the day-side crescent on the sunward limb: level, width (x R), taper
    BG_BLUR=1.2,                         # px at 2560 wide (lens softness on the backdrop)
    # sun: direction from the face point (az from the rim normal toward the tangent, el above the face plane)
    SUN=6.0, SUN_AZ=-30.0, SUN_EL=14.0, SUN_ANG=1.2,
    # SUN_SPOT > 0: the sun as a narrow spot instead (cone deg), so its light lands as a pool hugging the rim and the
    # face falls into shade (a flag on the sun, as a photographer would); aim along the tangent / inward normal (m)
    SUN_SPOT=0.0, SUN_BLEND=0.5, SUN_D=1.2, SUN_TX=0.0, SUN_TN=-0.01, SUN_R=0.004,
    # limb card (glossy only, rim)
    LIMB=40.0, LIMB_EL=8.0, LIMB_D=0.5, LIMB_W=0.12, LIMB_LEN=1.2, LIMB_AZ=0.0,
    # earth bounce
    EARTH=0.6, EARTH_AZ=0.0, EARTH_EL=-20.0,
    FILL=0.05, FILL_AZ=180.0, FILL_EL=60.0,
    # stars
    ST_N=260, ST_SEED=7, ST_MAX=0.5, ST_SIGMA=0.55,
    # haze: a soft warm wash in frame space toward the sun's side (linear, behind everything)
    HZ=0.010, HZ_U=1.0, HZ_V=0.0, HZ_R=0.9,
    # gloss: a warm band card in the coat's mirror direction (the atmosphere seen in the lacquer)
    GLOSS=6.0, GLOSS_D=0.6, GLOSS_W=0.25, GLOSS_LEN=1.2, GLOSS_DEL=2.0, GLOSS_AZ=0.0, GLOSS_E0=-1.0, GLOSS_E1=-0.5,
    GLOSS_WARM=1.0,                      # 1 = the atmosphere's amber, 0 = neutral white
    # material (white): K04 v5's macro numbers (K14)
    W_BUMP=0.10, W_DIR_TONE=0.22, W_STREAK_A=0.14,
    # gains (full) and the base composite's sun level
    g_sun=1.0, g_limb=1.0, g_gloss=1.0, g_earth=1.0, g_fill=1.0, SUN_BASE=0.0, GLOSS_BASE=0.6,
)
# v1 composition (2026-10-29, previews out/k15/p06, c1): the head's upper-left crown shoulder seen from 30 deg above the
# face, looking 35 deg along the edge; the rim a rising arc, three crown holes on the lit face; the planet's limb sweeping
# across the space beyond the edge, its sunward side to the upper left.
DEFAULTS.update(
    PHI=60.0, YAW=-35.0, EL=30.0, DIST=0.28, FW=0.11, TIN=0.0, SHIFT_Y=-0.10, FSTOP=22.0, FOCUS_IN=0.01,
    SUN_ANG=2.0,
    PL_U=0.2, PL_V=1.8, PL_R=1.75,
    GLOSS=10.0, GLOSS_W=0.03, EARTH=0.3, EARTH_AZ=-80.0, EARTH_EL=6.0,
    SUN=250.0, SUN_SPOT=6.0, SUN_BLEND=1.0, SUN_AZ=30.0, SUN_EL=35.0, SUN_TX=-0.02, SUN_TN=-0.015,
    SUN_PA=118.0, AT_GLOW=0.15, AT_GW=0.05, AT_LINE=0.6, AT_LW=0.0025, CR_W=0.04, CR_K=1.5,
    ST_N=420, ST_MAX=1.2, PL_NIGHT=0.015, PL_NW=0.25, CR=0.15,
)
# Pace: black 12K shows its tapes only near the coat's mirror direction (canon Pace v6): as K14-pace, a wide graded
# neutral panel a little below the mirror band, its soft edge across the face.
PACE_SET = dict(GLOSS_W=0.5, GLOSS=6.0, GLOSS_DEL=-8.0, GLOSS_E0=-1.0, GLOSS_E1=0.6, GLOSS_WARM=0.15)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 960, "h": 540, "spp": 24, "out": "k15/prev", "feel": "command", "set": []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--set":
            o["set"].append(argv[i + 1])
            i += 2
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
    P = dict(DEFAULTS)
    if o["feel"] == "pace":
        P.update(PACE_SET)
    for s in o["set"]:
        k, v = s.split("=", 1)
        assert k in P, "unknown setting " + k
        P[k] = float(v)
    return o, P


def out_stem(name):
    p = name[:-4] if name.endswith(".png") else name
    if not os.path.isabs(p):
        p = os.path.join(studio.OUT, p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def rim_frame(phi_deg):
    pts = C.outline_canon()
    best = None
    n_ = len(pts)
    for i in range(n_):
        x, y = pts[i]
        if y < 0.0:
            continue
        ax, ay = pts[i - 4]
        bx, by = pts[(i + 4) % n_]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty)
        nx, ny = ty / ln, -tx / ln
        if nx * x + ny * y < 0:
            nx, ny = -nx, -ny
        a = math.degrees(math.atan2(ny, nx))
        d = abs((a - phi_deg + 180) % 360 - 180)
        if best is None or d < best[0]:
            best = (d, (x, y), (nx, ny))
    _, p, n = best
    return Vector((p[0], p[1], ZT)), Vector((n[0], n[1], 0)), Vector((-n[1], n[0], 0))


def look_at(ob, loc, tgt, up=(0.0, 0.0, 1.0), roll=0.0):
    fwd = (Vector(tgt) - Vector(loc)).normalized()
    rt = fwd.cross(Vector(up)).normalized()
    upv = rt.cross(fwd)
    m = Matrix((rt, upv, -fwd)).transposed()
    if roll:
        m = m @ Matrix.Rotation(math.radians(roll), 3, "Z")
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ m.to_4x4()


def collection(name, obs):
    c = bpy.data.collections.new(name)
    for ob in obs:
        c.objects.link(ob)
    return c


def _orient_card(ob, t):
    """Turn a panel about its normal so its long side (local Y) lies along the rim tangent (as K14)."""
    mw = ob.matrix_world.to_3x3()
    nz = (mw @ Vector((0, 0, 1))).normalized()
    ty = (t - nz * t.dot(nz)).normalized()
    tx = ty.cross(nz).normalized()
    sc_ = ob.scale.copy()
    ob.matrix_world = Matrix.Translation(ob.location) @ Matrix((tx, ty, nz)).transposed().to_4x4() @ Matrix.Diagonal((*sc_, 1))


def frame_dir(cam, sc, u, v):
    """World direction from the camera through frame point (u, v) (0..1 from the bottom left, may lie outside)."""
    cd = cam.data
    w, h = sc.render.resolution_x, sc.render.resolution_y
    sw = cd.sensor_width
    xs = (u - 0.5 + cd.shift_x) * sw
    ys = (v - 0.5) * sw * h / w + cd.shift_y * sw
    d = Vector((xs, ys, -cd.lens))
    return (cam.matrix_world.to_3x3() @ d).normalized()


def _nn(nodes, kind, op=None, **kw):
    n = nodes.new(kind)
    if op:
        n.operation = op
    for k, v in kw.items():
        n.inputs[k].default_value = v
    return n


def build(o, p):
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.max_bounces = 6
    sc.cycles.glossy_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.use_denoising = False
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.seed = 5
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in GROUPS:
        vl.lightgroups.add(name=g)

    mo = None if o["feel"] == "pace" else {"bump": p["W_BUMP"], "dir_tone": p["W_DIR_TONE"], "streak_a": p["W_STREAK_A"]}
    root, parts = C.build_racket("KQ", feel=o["feel"], walls=False, mat_opts=mo)
    for nm in ("grip", "cap", "capmark", "neck"):
        if nm in parts:
            parts[nm].hide_render = True

    P, n, t = rim_frame(p["PHI"])
    z = Vector((0, 0, 1))
    yaw = math.radians(p["YAW"])
    vh = (n * math.cos(yaw) + t * math.sin(yaw)).normalized()
    T = P - n * p["TIN"]
    el = math.radians(p["EL"])
    cam_loc = T - vh * p["DIST"] * math.cos(el) + z * p["DIST"] * math.sin(el)
    cd = bpy.data.cameras.new("Cam")
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    look_at(cam, cam_loc, T, roll=p["ROLL"])
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
    cd.lens = 36.0 * p["DIST"] / p["FW"]
    cd.shift_x = p["SHIFT_X"]
    cd.shift_y = p["SHIFT_Y"]
    cd.clip_start = 0.01
    cd.clip_end = 5000.0
    cd.dof.use_dof = p["FSTOP"] > 0
    cd.dof.aperture_fstop = max(p["FSTOP"], 1.0)
    fpt = P - n * p["FOCUS_IN"]
    view = (T - cam_loc).normalized()
    cd.dof.focus_distance = (fpt - cam_loc).dot(view)
    bpy.context.view_layer.update()

    def dirv(az, elv):
        a, e = math.radians(az), math.radians(elv)
        h = n * math.cos(a) + t * math.sin(a)
        return (h * math.cos(e) + z * math.sin(e)).normalized()

    head = [parts[k] for k in ("face", "rim", "wall", "holes", "back", "throat", "bridgewall") if k in parts]
    # sun: a sun lamp; its direction is where the light comes FROM
    sdir = dirv(p["SUN_AZ"], p["SUN_EL"])
    if p["SUN"] > 0 and p["SUN_SPOT"] > 0:
        aim = P + t * p["SUN_TX"] + n * p["SUN_TN"]
        sob = studio.spot_light("lg_sun", tuple(aim + sdir * p["SUN_D"]), p["SUN"], p["SUN_SPOT"], blend=p["SUN_BLEND"],
                                color=(1.0, 0.95, 0.88), target=tuple(aim), radius=p["SUN_R"])
        sob.lightgroup = "sun"
    elif p["SUN"] > 0:
        ld = bpy.data.lights.new("lg_sun", "SUN")
        ld.energy = p["SUN"]
        ld.angle = math.radians(p["SUN_ANG"])
        ld.color = (1.0, 0.95, 0.88)
        sob = bpy.data.objects.new("lg_sun", ld)
        sc.collection.objects.link(sob)
        sob.rotation_euler = (-sdir).to_track_quat("-Z", "Y").to_euler()
        sob.lightgroup = "sun"
    vrim = (P - cam_loc).normalized()
    mir = (vrim - 2 * vrim.dot(z) * z).normalized()
    mel = math.degrees(math.asin(mir.z))
    mh = Vector((mir.x, mir.y, 0)).normalized()
    maz = math.degrees(math.atan2(mh.dot(t), mh.dot(n)))
    if p["LIMB"] > 0:
        rk = K04.panel("lg_limb", tuple(P + dirv(maz + p["LIMB_AZ"], p["LIMB_EL"]) * p["LIMB_D"]),
                       (p["LIMB_W"], p["LIMB_LEN"]), p["LIMB"], tuple(P), color=(1.0, 0.62, 0.32), edge=(-1.0, -0.5),
                       fade=(0, 1.0))
        _orient_card(rk, t)
        rk.visible_diffuse = False
        rk.lightgroup = "limb"
        rk.light_linking.receiver_collection = collection("rim_recv", [parts["rim"]])
    if p["EARTH"] > 0:
        ed = dirv(p["EARTH_AZ"], p["EARTH_EL"])
        ea = studio.area_light("lg_earth", tuple(P - n * 0.02 + ed * 0.5), 0.3, p["EARTH"], color=(1.0, 0.72, 0.5),
                               size_y=0.01, target=tuple(P - n * 0.02))
        ea.visible_glossy = False
        ea.lightgroup = "earth"
        ea.light_linking.receiver_collection = collection("earth_recv", head)
    if p["FILL"] > 0:
        fd = dirv(p["FILL_AZ"], p["FILL_EL"])
        fill = studio.area_light("lg_fill", tuple(P + fd * 0.6), 0.8, p["FILL"], color=(0.9, 0.95, 1.0),
                                 target=tuple(P))
        fill.visible_glossy = False
        fill.lightgroup = "fill"
        fill.light_linking.receiver_collection = collection("fill_recv", head)
    if p["GLOSS"] > 0:
        gb = K04.panel("lg_gloss", tuple(P + dirv(maz + p["GLOSS_AZ"], mel + p["GLOSS_DEL"]) * p["GLOSS_D"]),
                       (p["GLOSS_W"], p["GLOSS_LEN"]), p["GLOSS"], tuple(P),
                       color=tuple(1.0 + (c - 1.0) * p["GLOSS_WARM"] for c in (1.0, 0.72, 0.46)),
                       edge=(p["GLOSS_E0"], p["GLOSS_E1"]), fade=(0, 1.0))
        _orient_card(gb, t)
        gb.visible_diffuse = False
        gb.lightgroup = "gloss"
    sc.render.film_transparent = True
    return sc, cam, parts, (P, n, t)


def _write_png16(path, img):
    import numpy as np
    h, w = img.shape[:2]
    a = np.clip(np.round(img * 65535), 0, 65535).astype(">u2")
    raw = b"".join(b"\x00" + a[r].tobytes() for r in range(h))

    def chunk(tg, d):
        c = struct.pack(">I", len(d)) + tg + d
        return c + struct.pack(">I", zlib.crc32(tg + d) & 0xFFFFFFFF)

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 2, 0, 0, 0)))
        fh.write(chunk(b"IDAT", zlib.compress(raw, 6)))
        fh.write(chunk(b"IEND", b""))


def make_bg(stem, w, h, p, variant):
    """The space behind the racket, frame space, linear 16-bit PNG: a few stars, a warm haze toward the sun, and the
    planet: a dark body with a faint airglow toward its limb, a thin bright atmosphere line on the limb (amber on the
    sunward side, falling to a pale graphite away from it) and a soft glow outside it. variant "base": the limb before
    sunrise (AT_BASE), no haze."""
    import numpy as np
    rng = np.random.default_rng(int(p["ST_SEED"]))
    img = np.zeros((h, w, 3), np.float64)
    s = w / 2560.0
    # coordinates in frame widths: x right, y down
    yy = (np.arange(h) + 0.5)[:, None] / w
    xx = (np.arange(w) + 0.5)[None, :] / w
    lev = 1.0 if variant == "full" else p["AT_BASE"]
    # stars first (the planet body hides those behind it)
    n = int(p["ST_N"])
    xs = rng.uniform(0, w, n)
    ys = rng.uniform(0, h, n)
    br = p["ST_MAX"] * rng.power(0.25, n) ** 2.2
    tint = rng.uniform(-1, 1, n)
    sig = p["ST_SIGMA"] * max(s, 0.4) * rng.uniform(0.8, 1.4, n)
    for x0, y0, b, tn, sg in zip(xs, ys, br, tint, sig):
        r = int(math.ceil(sg * 4)) + 1
        xi, yi = int(x0), int(y0)
        xa, xb, ya, yb = max(0, xi - r), min(w, xi + r + 1), max(0, yi - r), min(h, yi + r + 1)
        gx = np.arange(xa, xb) + 0.5 - x0
        gy = np.arange(ya, yb) + 0.5 - y0
        k = np.exp(-(gy[:, None] ** 2 + gx[None, :] ** 2) / (2 * sg * sg))
        col = np.array([1.0 + 0.08 * tn, 1.0, 1.0 - 0.10 * tn])
        img[ya:yb, xa:xb] += (b * k)[..., None] * col[None, None, :]
    # planet
    dx, dy = xx - p["PL_U"], yy - p["PL_V"]
    rr = np.sqrt(dx * dx + dy * dy)
    R = p["PL_R"]
    d = rr - R                                   # signed distance to the limb (frame widths), < 0 inside
    pa = np.degrees(np.arctan2(-dy, dx))         # position angle, 0 = +x, 90 = up
    dang = np.abs((pa - p["SUN_PA"] + 180) % 360 - 180)
    sunw = np.exp(-(dang / p["PL_SPREAD"]) ** 2)   # 1 on the sunward limb
    lvl = p["AT_FAR"] + (1 - p["AT_FAR"]) * sunw
    warm = np.array([1.0, 0.60, 0.30])
    pale = np.array([0.60, 0.62, 0.68])
    col = pale[None, None, :] + (warm - pale)[None, None, :] * (sunw ** 0.7)[..., None]
    inside = (d < 0)[..., None]
    img = np.where(inside, 0.0, img)
    body = p["PL_BODY"] + p["PL_NIGHT"] * lvl * np.exp(np.minimum(d, 0) / (p["PL_NW"] * R))
    img += np.where(inside, body[..., None] * col * 0.8 + p["PL_BODY"] * 0.2, 0.0)
    # the day side: a thin crescent inside the sunward limb, narrowing away from the sun
    cw = p["CR_W"] * R * np.maximum(sunw, 1e-3) ** p["CR_K"]
    cres = p["CR"] * np.exp(np.minimum(d, 0) / cw) * sunw * (d < 0)
    img += (cres * lev)[..., None] * (col * 0.85 + 0.15)
    line = p["AT_LINE"] * np.exp(-(d / p["AT_LW"]) ** 2)
    glow = p["AT_GLOW"] * np.exp(-np.maximum(d, 0) / p["AT_GW"]) * (d > -p["AT_LW"])
    img += ((line + glow) * lvl * lev)[..., None] * col
    if variant == "full":
        vv = yy
        r2 = ((xx - p["HZ_U"]) ** 2 + (vv - p["HZ_V"]) ** 2) / max(p["HZ_R"], 1e-3) ** 2
        img += (p["HZ"] * np.exp(-r2 * 2.0))[..., None] * np.array([1.0, 0.78, 0.6])[None, None, :]
    if p["BG_BLUR"] > 0:
        sg = p["BG_BLUR"] * s
        r = int(math.ceil(sg * 3))
        k = np.exp(-(np.arange(-r, r + 1) ** 2) / (2 * sg * sg))
        k /= k.sum()
        pad = np.pad(img, ((r, r), (0, 0), (0, 0)), mode="edge")
        img = sum(k[i] * pad[i:i + h] for i in range(2 * r + 1))
        pad = np.pad(img, ((0, 0), (r, r), (0, 0)), mode="edge")
        img = sum(k[i] * pad[:, i:i + w] for i in range(2 * r + 1))
    path = stem + "_bg_" + variant + ".png"
    _write_png16(path, img)
    return path


def comp(sc, o, p, stem, src=None):
    """Denoise each group, sum with gains for two variants (base, full), put the stars behind (1 - alpha), write
    <stem>-base.png and <stem>-full.png (16-bit RGB). o["solo"]: each group alone too."""
    sc.use_nodes = True
    tr = sc.node_tree
    if src is None:
        for nd in list(tr.nodes):
            tr.nodes.remove(nd)
        rl = tr.nodes.new("CompositorNodeRLayers")
        src = {g: rl.outputs["Combined_" + g] for g in GROUPS}
        src["albedo"] = rl.outputs["Denoising Albedo"]
        src["normal"] = rl.outputs["Denoising Normal"]
        src["alpha"] = rl.outputs["Alpha"]
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = os.path.dirname(stem)
    fo.format.file_format = "PNG"
    fo.format.color_depth = "16"
    fo.format.color_mode = "RGB"
    b = os.path.basename(stem)
    fo.file_slots[0].path = b + "-base_#"
    fo.file_slots.new(b + "-full_#")
    den = {}
    for g in GROUPS:
        if g not in src:
            continue
        dn = tr.nodes.new("CompositorNodeDenoise")
        dn.prefilter = "ACCURATE"
        tr.links.new(src[g], dn.inputs["Image"])
        tr.links.new(src["albedo"], dn.inputs["Albedo"])
        tr.links.new(src["normal"], dn.inputs["Normal"])
        den[g] = dn.outputs[0]
        if o.get("solo"):
            fo.file_slots.new(b + "_" + g + "_#")
            tr.links.new(dn.outputs[0], fo.inputs[len(fo.inputs) - 1])
    inv = tr.nodes.new("CompositorNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    tr.links.new(src["alpha"], inv.inputs[1])
    for vi, variant in enumerate(("base", "full")):
        bgp = make_bg(stem, sc.render.resolution_x, sc.render.resolution_y, p, variant)
        si = tr.nodes.new("CompositorNodeImage")
        si.image = bpy.data.images.load(bgp, check_existing=False)
        si.image.colorspace_settings.name = "Non-Color"
        sm = tr.nodes.new("CompositorNodeMixRGB")
        sm.blend_type = "MULTIPLY"
        sm.inputs[0].default_value = 1.0
        tr.links.new(si.outputs["Image"], sm.inputs[1])
        tr.links.new(inv.outputs[0], sm.inputs[2])
        acc = sm.outputs[0]
        for g, s in den.items():
            k = 1.0
            if variant == "base":
                k = {"sun": p["SUN_BASE"], "gloss": p["GLOSS_BASE"], "limb": p["AT_BASE"]}.get(g, 1.0)
            gg = p["g_" + g] * k
            mu = tr.nodes.new("CompositorNodeMixRGB")
            mu.blend_type = "MULTIPLY"
            mu.inputs[0].default_value = 1.0
            tr.links.new(s, mu.inputs[1])
            mu.inputs[2].default_value = (gg, gg, gg, 1)
            ad = tr.nodes.new("CompositorNodeMixRGB")
            ad.blend_type = "ADD"
            ad.inputs[0].default_value = 1.0
            tr.links.new(acc, ad.inputs[1])
            tr.links.new(mu.outputs[0], ad.inputs[2])
            acc = ad.outputs[0]
        sa = tr.nodes.new("CompositorNodeSetAlpha")
        sa.mode = "REPLACE_ALPHA"
        sa.inputs["Alpha"].default_value = 1.0
        tr.links.new(acc, sa.inputs["Image"])
        tr.links.new(sa.outputs[0], fo.inputs[vi])
        if variant == "full":
            co = tr.nodes.new("CompositorNodeComposite")
            tr.links.new(sa.outputs[0], co.inputs["Image"])


def finish(stem):
    d = os.path.dirname(stem)
    b = os.path.basename(stem)
    for f in os.listdir(d):
        if f.startswith(b) and f.endswith(".png"):
            head = f[:-4].rsplit("_", 1)
            if len(head) == 2 and head[1].isdigit():
                os.replace(os.path.join(d, f), os.path.join(d, head[0] + ".png"))


def comp_from_exr(o, p):
    exr = o["comp"]
    if not os.path.isabs(exr):
        exr = os.path.join(studio.OUT, exr)
    sc = studio.reset()
    img = bpy.data.images.load(exr)
    sc.use_nodes = True
    tr = sc.node_tree
    for nd in list(tr.nodes):
        tr.nodes.remove(nd)
    im = tr.nodes.new("CompositorNodeImage")
    im.image = img
    im.layer = "ViewLayer"
    src = {g: im.outputs["Combined_" + g] for g in GROUPS if ("Combined_" + g) in im.outputs}
    src["albedo"] = im.outputs["Denoising Albedo"]
    src["normal"] = im.outputs["Denoising Normal"]
    src["alpha"] = im.outputs["Alpha"]
    mj0 = exr[:-4] + ".json"
    w, h = json.load(open(mj0))["size"]
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    stem = out_stem(o["out"])
    meta = json.load(open(mj0))
    meta["p"] = p
    json.dump(meta, open(stem + ".json", "w"), indent=1)
    comp(sc, o, p, stem, src)
    sc.render.filepath = stem + "_scratch.png"
    bpy.ops.render.render(write_still=True)
    finish(stem)
    os.remove(stem + "_scratch.png")
    print("composited", stem, flush=True)


def main():
    o, p = parse_args()
    if o.get("comp"):
        return comp_from_exr(o, p)
    t0 = time.time()
    stem = out_stem(o["out"])
    sc, cam, parts, (P, n, t) = build(o, p)
    json.dump(dict(o={k: v for k, v in o.items() if k != "set"}, p=p,
                   size=[sc.render.resolution_x, sc.render.resolution_y]), open(stem + ".json", "w"), indent=1)
    comp(sc, o, p, stem)
    sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.exr_codec = "ZIP"
    sc.render.filepath = stem + ".exr"
    print("rim point", [round(v * 1000, 1) for v in P], "lens", round(cam.data.lens, 1), flush=True)
    bpy.ops.render.render(write_still=True)
    finish(stem)
    print("rendered", stem, round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
