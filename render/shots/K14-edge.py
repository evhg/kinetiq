"""K14-edge (Release 4, 2026-10-28): the sweet spot's payoff, in K04's macro language. RECOVERED copy: the render kit
(scratchpad/blender) was wiped at 06:53 UTC by another process's startup cleanup while this shot was in preview. This
file is the shot as it stood (all edits applied); it belongs in blender/shots/ and needs the kit (kq_canon, studio,
K04-hole-macro.py's panel(), k12_lib, k10_lib, k04_tex2) to run.

The canonical racket (kq_canon, Command = white 3K twill by default, `--feel pace` = black 12K v6), seen from just
above its face at the head's upper-right shoulder, yawed 35 deg along the edge: the rim sweeps as a diagonal arc from
lower left to upper right, the flat face (twill crisp, the fibre flip sparkling along the edge) on the lower right, the
graphite void upper left (words' side). One crown hole lower right in soft focus. Optional: a faint amber hairline
4.0 mm in from the edge (racket-shape.ts FACE_INSET, graphics-sweetspot.ts INSET).

Light (each a light group, one render, composited by gains; --comp re-grades from the EXR, --solo writes each group):
  pool   white key: a 6 deg spot from behind the camera (az 165, el 45) aimed right of the rim point, its soft edge
         crossing the face (lit right, shade left)
  gloss  the clear coat's mirror band: a card beyond the rim at the face's mirror elevation, glossy only (on white the
         fibre sheen spreads it into a glow brightening toward the edge)
  rim    a card beyond the edge at 10 deg (below the face's mirror elevation), glossy only, linked to the rim: one crisp
         line on the 1.5 mm roll; plus lg_lip, a glossy card at 34 deg linked to the bores (lip highlights)
  rake   a grazing strip from frame left for the tow relief
  fill   weak shade fill (diffuse only); pool and fill exclude the bores so the holes stay graphite
  line   the optional hairline (emission under the coat)
  backdrop: film transparent; a frame-space graphite gradient + soft glow composited behind (make_bg), linear values
Preview settings that worked (p13/p14, 640x360 24 spp, about 22 s a preview):
  --set SHIFT_Y=-0.05 --set DIST=0.26 --set FW=0.05 --set FSTOP=40 --set RIM_EL=10 --set RIM_W=0.15 --set RIM=40
  --set RAKE=0.4 --set RAKE_AZ=80 --set FILL=0.15 --set GLOSS_LEN=0.35 --set GLOSS_W=0.04 --set GLOSS=20
  --set POOL_BLEND=1 --set POOL_EL=45 --set POOL=25 --set POOL_AZ=165 --set LIP_LEN=0.15 --set LIP=40 --set POOL_DEG=6
  --set POOL_TX=-0.022 --set POOL_TN=-0.004 --set g_gloss=0.7 --set YAW=-35 --set BG_TOP=0.015 --set BG_HOR=0.03
  --set BG_GLOW=0.04 --set BG_GX=0.35 --set BG_GY=0.35 --set BG_GRX=0.4 --set BG_GRY=0.35
  (backdrop: linear 0.0045 renders as luma ~1-4 through AgX Punchy and fails the fill rule; 0.03-0.05 reads mid-grey;
  0.015-0.03 is the target range, untested at the moment of the wipe)
Usage (from the blender dir, through the lock):
  flock render.lock ../bpyenv/bin/python shots/K14-edge.py --w 960 --h 540 --spp 32 --out k14/K14_p01 [--feel pace]
  [--set NAME=value ...]; --comp k14/K14_p01.exr --out k14/K14_p01c [--set g_<group>=k ...]; --solo
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

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import studio  # noqa: E402
import kq_canon as C  # noqa: E402

_spec = importlib.util.spec_from_file_location("k04", os.path.join(HERE, "K04-hole-macro.py"))
K04 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K04)

ZT = C.ZT
GROUPS = ("pool", "gloss", "rim", "rake", "fill", "line")

DEFAULTS = dict(
    # composition
    PHI=38.0,          # deg: outward normal of the rim point (0 = +x, 90 = +y): the upper-right shoulder
    YAW=0.0,           # deg: the camera's heading off the rim normal (a 3/4 look along the edge)
    EL=24.0,           # deg: camera elevation above the face plane
    DIST=0.24,         # m: camera to target
    FW=0.056,          # m: frame width at the target
    TIN=0.000,         # m: target point inward of the rim along the normal
    SHIFT_Y=0.10,      # lens shift (fraction of width): negative puts the rim higher in the frame
    ROLL=0.0,          # deg: camera roll
    FSTOP=40.0,
    FOCUS_IN=0.002,    # m: focus point inward of the rim (on the face)
    # backdrop: composited behind the racket in frame space (film transparent): linear values
    BG_TOP=0.0045, BG_HOR=0.012, BG_GLOW=0.03, BG_GX=0.58, BG_GRX=0.45, BG_GRY=0.22, BG_WARM=0.04, BG_GY=-1.0,
    # pool (white key)
    POOL=30.0, POOL_AZ=200.0, POOL_EL=22.0, POOL_D=0.45, POOL_DEG=14.0, POOL_BLEND=1.0, POOL_R=0.01,
    POOL_TX=0.0, POOL_TN=-0.012,     # aim point: along the rim tangent (+ = frame left at yaw 0) / normal (m)
    POOL_GLOSS=0.0,
    # gloss band (mirror of the face)
    GLOSS=14.0, GLOSS_D=0.6, GLOSS_W=0.05, GLOSS_LEN=1.2, GLOSS_DEL=0.0, GLOSS_AZ=0.0, GLOSS_EDGE0=-1.0, GLOSS_EDGE1=-0.2,
    # rim line
    RIM=30.0, RIM_EL=6.0, RIM_D=0.5, RIM_W=0.012, RIM_LEN=1.2, RIM_AZ=0.0,
    # lip line: a glossy-only card high beyond the holes, linked to the bores' lips (K04's lg_lipline)
    LIP=30.0, LIP_EL=34.0, LIP_D=0.5, LIP_W=0.05, LIP_LEN=0.5,
    # rake
    RAKE=1.0, RAKE_AZ=95.0, RAKE_EL=7.0, RAKE_D=0.4, RAKE_LEN=0.3,
    # fill
    FILL=0.6, FILL_AZ=160.0, FILL_EL=50.0,
    # hairline (amber, 4.0 mm in from the edge); 0 = off
    LINE=0.0, LINE_W=0.00012, LINE_INSET=0.004,
    # material (white): K04 v5's macro numbers
    W_BUMP=0.10, W_DIR_TONE=0.22, W_STREAK_A=0.14,
    # gains in the comp
    g_pool=1.0, g_gloss=1.0, g_rim=1.0, g_rake=1.0, g_fill=1.0, g_line=1.0,
)
PACE_SET = dict()


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 960, "h": 540, "spp": 32, "out": "k14/K14_prev", "feel": "command", "set": []}
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
    """The outline point whose outward normal is closest to phi: (point, normal n, tangent t) in metres.
    phi 38 -> rim point (104.2, 108.6) mm, normal (0.789, 0.614)."""
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


def _orient_card(ob, P, t):
    """Turn a panel about its normal so its local Y (the long side) lies along the rim tangent."""
    mw = ob.matrix_world.to_3x3()
    nz = (mw @ Vector((0, 0, 1))).normalized()
    ty = (t - nz * t.dot(nz)).normalized()
    tx = ty.cross(nz).normalized()
    sc_ = ob.scale.copy()
    ob.matrix_world = Matrix.Translation(ob.location) @ Matrix((tx, ty, nz)).transposed().to_4x4() @ Matrix.Diagonal((*sc_, 1))


def build(o, p):
    pace = o["feel"] == "pace"
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.max_bounces = 6
    sc.cycles.glossy_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.use_denoising = False
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.seed = 3
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in GROUPS:
        vl.lightgroups.add(name=g)

    mo = None if pace else {"bump": p["W_BUMP"], "dir_tone": p["W_DIR_TONE"], "streak_a": p["W_STREAK_A"]}
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
    cd.shift_y = p["SHIFT_Y"]
    cd.clip_start = 0.01
    cd.dof.use_dof = p["FSTOP"] > 0
    cd.dof.aperture_fstop = max(p["FSTOP"], 1.0)
    fpt = P - n * p["FOCUS_IN"]
    view = (T - cam_loc).normalized()
    cd.dof.focus_distance = (fpt - cam_loc).dot(view)

    def dirv(az, elv):
        """Direction from the rim point: az from the outward normal (deg, + toward the tangent), elevation (deg)."""
        a, e = math.radians(az), math.radians(elv)
        h = n * math.cos(a) + t * math.sin(a)
        return (h * math.cos(e) + z * math.sin(e)).normalized()

    head = [parts[k] for k in ("face", "rim", "wall", "holes", "back", "throat", "bridgewall") if k in parts]
    # the bores stay graphite: no diffuse key or fill reaches them (as K04's dark through-holes)
    excl = collection("no_bores", [parts["holes"]])
    for it in excl.collection_objects:
        it.light_linking.link_state = "EXCLUDE"
    aim = P + t * p["POOL_TX"] + n * p["POOL_TN"]
    if p["POOL"] > 0:
        pool = studio.spot_light("lg_pool", tuple(aim + dirv(p["POOL_AZ"], p["POOL_EL"]) * p["POOL_D"]), p["POOL"],
                                 p["POOL_DEG"], blend=p["POOL_BLEND"], color=(1.0, 0.985, 0.97), target=tuple(aim),
                                 radius=p["POOL_R"])
        pool.lightgroup = "pool"
        pool.light_linking.receiver_collection = excl
        if p["POOL_GLOSS"] <= 0:
            pool.visible_glossy = False
    vrim = (P - cam_loc).normalized()
    mir = (vrim - 2 * vrim.dot(z) * z).normalized()
    mel = math.degrees(math.asin(mir.z)) + p["GLOSS_DEL"]
    mh = Vector((mir.x, mir.y, 0)).normalized()
    maz = math.degrees(math.atan2(mh.dot(t), mh.dot(n))) + p["GLOSS_AZ"]
    if p["GLOSS"] > 0:
        gb = K04.panel("lg_gloss", tuple(P + dirv(maz, mel) * p["GLOSS_D"]), (p["GLOSS_W"], p["GLOSS_LEN"]), p["GLOSS"],
                       tuple(P), color=(0.94, 0.96, 1.0), roll=0.0, edge=(p["GLOSS_EDGE0"], p["GLOSS_EDGE1"]),
                       fade=(0, 1.0))
        _orient_card(gb, P, t)
        gb.visible_diffuse = False
        gb.lightgroup = "gloss"
    if p["RIM"] > 0:
        rk = K04.panel("lg_rim", tuple(P + dirv(maz + p["RIM_AZ"], p["RIM_EL"]) * p["RIM_D"]), (p["RIM_W"], p["RIM_LEN"]),
                       p["RIM"], tuple(P), color=(0.95, 0.97, 1.0), edge=(-1.0, -0.5), fade=(0, 1.0))
        _orient_card(rk, P, t)
        rk.visible_diffuse = False
        rk.lightgroup = "rim"
        rk.light_linking.receiver_collection = collection("rim_recv", [parts["rim"]])
    if p["LIP"] > 0:
        lp_ = K04.panel("lg_lip", tuple(P + dirv(maz, p["LIP_EL"]) * p["LIP_D"]), (p["LIP_W"], p["LIP_LEN"]),
                        p["LIP"], tuple(P), color=(0.95, 0.97, 1.0), edge=(-1.0, -0.5), fade=(0, 1.0))
        _orient_card(lp_, P, t)
        lp_.visible_diffuse = False
        lp_.lightgroup = "rim"
        lp_.light_linking.receiver_collection = collection("lip_recv", [parts["holes"]])
    if p["RAKE"] > 0:
        kd = dirv(p["RAKE_AZ"], p["RAKE_EL"])
        rake = studio.area_light("lg_rake", tuple(P - n * 0.02 + kd * p["RAKE_D"]), p["RAKE_LEN"], p["RAKE"],
                                 color=(1.0, 0.98, 0.95), size_y=0.006, target=tuple(P - n * 0.02))
        rake.lightgroup = "rake"
        rake.light_linking.receiver_collection = collection("rake_recv", head)
    if p["FILL"] > 0:
        fd = dirv(p["FILL_AZ"], p["FILL_EL"])
        fill = studio.area_light("lg_fill", tuple(P + fd * 0.6), 0.8, p["FILL"], color=(0.97, 0.98, 1.0),
                                 target=tuple(P))
        fill.visible_glossy = False
        fill.lightgroup = "fill"
        fill.light_linking.receiver_collection = excl
    sc.render.film_transparent = True
    if p["LINE"] > 0:
        add_line(parts["face"], p)
    return sc, cam, parts, (P, n, t)


def line_mask(p):
    """A 16-bit mask of the amber hairline LINE_INSET in from the canon outline over the head's upper-right quadrant, in
    face UVs (u = x, v = y metres): nested offset polygons (as K12's field_mask), 0.01 mm per pixel."""
    from PIL import Image, ImageDraw
    import numpy as np
    from shapely.geometry import Polygon, box
    d = os.path.join(HERE, "k14")
    os.makedirs(d, exist_ok=True)
    key = "%.5f_%.6f_v1" % (p["LINE_INSET"], p["LINE_W"])
    path, meta_p = os.path.join(d, "line_mask.png"), os.path.join(d, "line_mask.json")
    if os.path.exists(path) and os.path.exists(meta_p):
        meta = json.load(open(meta_p))
        if meta["key"] == key:
            return path, meta["bounds"]
    px = 0.00001
    O = Polygon(C.outline_canon()).buffer(0)
    x0, y0, x1, y1 = 0.03, 0.03, 0.135, 0.16
    W, H = int((x1 - x0) / px), int((y1 - y0) / px)
    half = p["LINE_W"]
    steps = 24
    ds = [-p["LINE_INSET"] + half * 2.5 - k * (half * 5.0 / steps) for k in range(steps + 1)]
    img = Image.new("I", (W, H), 0)
    dr = ImageDraw.Draw(img)
    for k, dd in enumerate(ds):
        g = O.buffer(dd, join_style="round", quad_segs=32).intersection(box(x0 - 0.01, y0 - 0.01, x1 + 0.01, y1 + 0.01))
        for poly in getattr(g, "geoms", [g]):
            dr.polygon([((x - x0) / px, (y1 - y) / px) for x, y in poly.exterior.coords], fill=k + 1)
    q = np.asarray(img, np.int32)
    ds_a = np.array(ds)
    sd = np.where(q > 0, ds_a[np.clip(q - 1, 0, None)] + p["LINE_INSET"], 1.0)
    e = np.clip(1.0 - np.abs(sd) / half, 0.0, 1.0)
    line = e * e * (3 - 2 * e)
    a = np.clip(np.round(line * 65535), 0, 65535).astype(np.uint16)
    Image.fromarray(a, "I;16").save(path)
    json.dump(dict(key=key, bounds=[x0, y0, x1, y1]), open(meta_p, "w"))
    return path, [x0, y0, x1, y1]


def add_line(face, p):
    """The hairline as an emission under the coat (light group 'line'). Untested at the moment of the wipe."""
    import k12_lib as K
    import k10_lib as L
    path, (x0, y0, x1, y1) = line_mask(p)
    m = face.data.materials[0].copy()
    m.name = "K14_FaceLine"
    face.data.materials[0] = m
    m.cycles.emission_sampling = "NONE"
    nb = K.NB(m)
    nodes = m.node_tree.nodes
    b = next(nd for nd in nodes if nd.type == "BSDF_PRINCIPLED" and (nd.inputs["Coat Weight"].default_value > 0.5
                                                                     or nd.inputs["Coat Weight"].is_linked))
    u, v, _ = nb.coords("UV")
    cv = nodes.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", u, x0), x1 - x0), cv.inputs[0])
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", v, y0), y1 - y0), cv.inputs[1])
    tex = L._img(nb, cv.outputs[0], path, "Non-Color", interp="Linear", ext="CLIP")
    b.inputs["Emission Color"].default_value = (1.0, 0.42, 0.12, 1)
    nb.l.new(nb.math("MULTIPLY", tex.outputs["Color"], p["LINE"]), b.inputs["Emission Strength"])
    face.lightgroup = "line"


def comp(sc, o, p, stem, src=None):
    """Sum the light groups with gains, denoise each (OIDN with albedo + normal), put the frame-space backdrop behind,
    write a 16-bit RGB PNG <stem>.png. o["solo"]: also every group alone (<stem>_<group>.png)."""
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
    fo.file_slots[0].path = os.path.basename(stem) + "_#"
    acc = None
    for g in GROUPS:
        if g not in src:
            continue
        dn = tr.nodes.new("CompositorNodeDenoise")
        dn.prefilter = "ACCURATE"
        tr.links.new(src[g], dn.inputs["Image"])
        tr.links.new(src["albedo"], dn.inputs["Albedo"])
        tr.links.new(src["normal"], dn.inputs["Normal"])
        mu = tr.nodes.new("CompositorNodeMixRGB")
        mu.blend_type = "MULTIPLY"
        mu.inputs[0].default_value = 1.0
        tr.links.new(dn.outputs[0], mu.inputs[1])
        gg = p["g_" + g]
        mu.inputs[2].default_value = (gg, gg, gg, 1)
        if o.get("solo"):
            fo.file_slots.new(os.path.basename(stem) + "_" + g + "_#")
            tr.links.new(dn.outputs[0], fo.inputs[len(fo.inputs) - 1])
        if acc is None:
            acc = mu.outputs[0]
        else:
            ad = tr.nodes.new("CompositorNodeMixRGB")
            ad.blend_type = "ADD"
            ad.inputs[0].default_value = 1.0
            tr.links.new(acc, ad.inputs[1])
            tr.links.new(mu.outputs[0], ad.inputs[2])
            acc = ad.outputs[0]
    # the backdrop behind the racket: acc (premultiplied) + bg x (1 - alpha)
    bgp = make_bg(stem, sc.render.resolution_x, sc.render.resolution_y, p)
    bi = tr.nodes.new("CompositorNodeImage")
    bi.image = bpy.data.images.load(bgp, check_existing=False)
    bi.image.colorspace_settings.name = "Non-Color"
    inv = tr.nodes.new("CompositorNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    tr.links.new(src["alpha"], inv.inputs[1])
    mb = tr.nodes.new("CompositorNodeMixRGB")
    mb.blend_type = "MULTIPLY"
    mb.inputs[0].default_value = 1.0
    tr.links.new(bi.outputs["Image"], mb.inputs[1])
    tr.links.new(inv.outputs[0], mb.inputs[2])
    ad = tr.nodes.new("CompositorNodeMixRGB")
    ad.blend_type = "ADD"
    ad.inputs[0].default_value = 1.0
    tr.links.new(acc, ad.inputs[1])
    tr.links.new(mb.outputs[0], ad.inputs[2])
    sa = tr.nodes.new("CompositorNodeSetAlpha")
    sa.mode = "REPLACE_ALPHA"
    sa.inputs["Alpha"].default_value = 1.0
    tr.links.new(ad.outputs[0], sa.inputs["Image"])
    acc = sa.outputs[0]
    co = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(acc, co.inputs["Image"])
    tr.links.new(acc, fo.inputs[0])


def make_bg(stem, w, h, p):
    """Frame-space backdrop (linear, 16-bit PNG): graphite rising from the top toward the horizon, a soft glow (a whisper
    warm). Horizon height from <stem>.json (written at render time)."""
    import numpy as np
    meta = json.load(open(stem + ".json")) if os.path.exists(stem + ".json") else {}
    hy = float(meta.get("horizon_y", 0.3))   # fraction from the top
    y = (np.arange(h) + 0.5)[:, None] / h
    x = (np.arange(w) + 0.5)[None, :] / w
    tt = np.clip(y / max(hy, 1e-3), 0, 1)
    v = p["BG_TOP"] + (p["BG_HOR"] - p["BG_TOP"]) * tt ** 1.6
    gy = hy if p["BG_GY"] < 0 else p["BG_GY"]
    r2 = ((x - p["BG_GX"]) / p["BG_GRX"]) ** 2 + ((y - gy) / p["BG_GRY"]) ** 2
    glow = p["BG_GLOW"] * np.exp(-r2 * 2.0)
    v = v + glow
    warm = np.array([1 + p["BG_WARM"], 1.0, 1 - p["BG_WARM"] * 1.5])
    wmix = (glow / max(p["BG_GLOW"], 1e-6))[..., None]
    rgb = v[..., None] * (1 + (warm[None, None, :] - 1) * wmix)
    a = np.clip(np.round(rgb * 65535), 0, 65535).astype(">u2")
    path = stem + "_bg.png"
    raw = b"".join(b"\x00" + a[r].tobytes() for r in range(h))

    def chunk(tg, d):
        c = struct.pack(">I", len(d)) + tg + d
        return c + struct.pack(">I", zlib.crc32(tg + d) & 0xFFFFFFFF)

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 2, 0, 0, 0)))
        fh.write(chunk(b"IDAT", zlib.compress(raw, 6)))
        fh.write(chunk(b"IEND", b""))
    return path


def finish(stem):
    """The File Output node appends the frame number: move <stem>_1.png (and <stem>_<group>_1.png) into place."""
    d = os.path.dirname(stem)
    b = os.path.basename(stem)
    for f in os.listdir(d):
        if f.startswith(b + "_") and f.endswith(".png"):
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
    # img.size reads (4, 4) before the multilayer EXR is decoded: take the size from the render's json
    w, h = json.load(open(mj0))["size"] if os.path.exists(mj0) else img.size[:]
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    stem = out_stem(o["out"])
    if os.path.exists(mj0) and os.path.abspath(mj0) != os.path.abspath(stem + ".json"):
        meta = json.load(open(mj0))
        meta["p"] = p
        json.dump(meta, open(stem + ".json", "w"), indent=1)
    comp(sc, o, p, stem, src)
    sc.render.filepath = stem + "_scratch.png"
    bpy.ops.render.render(write_still=True)
    finish(stem)
    os.remove(stem + "_scratch.png")
    print("composited", stem + ".png", flush=True)


def main():
    o, p = parse_args()
    if o.get("comp"):
        return comp_from_exr(o, p)
    t0 = time.time()
    stem = out_stem(o["out"])
    sc, cam, parts, (P, n, t) = build(o, p)
    if o.get("crop"):
        x0, x1, y0, y1 = [float(v) for v in str(o["crop"]).split(",")]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = y0, y1
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    hy = 1.0 - world_to_camera_view(sc, cam, P).y
    json.dump(dict(o={k: v for k, v in o.items() if k != "set"}, p=p, horizon_y=hy,
                   size=[sc.render.resolution_x, sc.render.resolution_y]), open(stem + ".json", "w"), indent=1)
    comp(sc, o, p, stem)
    sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.exr_codec = "ZIP"
    sc.render.filepath = stem + ".exr"
    print("rim point", [round(v * 1000, 1) for v in P], "normal", [round(v, 3) for v in n], "lens",
          round(cam.data.lens, 1), flush=True)
    bpy.ops.render.render(write_still=True)
    finish(stem)
    print("rendered", stem + ".png", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
