"""V2-sequences (2026-11-13, cloud REQUEST v2-sequences): the /v2 landing page's three scroll-scrubbed frame sequences.

Each sequence is 72 frames (f000..f071), one Blender process per sequence, feel and format, in the one-racket canon
(kq_canon) and K04's language through K11-dark (KD): the near-black field, the raking key, the sheen strip, the warm
2700 K glow. Frame 71 holds: every move eases out by frame ~68 (smootherstep), so the last 3 frames are near still.

  assemble  "Born whole": two pale foam cores (head, handle) float apart (0-12) and meet at the throat (12-24); dry
            matte carbon fabric (the feel's weave) wraps from the crown down (24-44); the resin flood: an amber front
            runs from the throat outwards and leaves glossy lacquered carbon behind it (44-60); a bright raking sweep
            crosses the racket and the finished racket (holes, serial, finish) replaces the moulded blank inside its
            bloom (60-68). The holes are never shown being made: the blank has none, the finished racket appears
            inside the sweep. Camera: a slow 25 deg 3/4 orbit, the whole racket always in frame. Naked (no grip).
            Four coincident copies (foam, dry, finished blank, finished racket, offset 0.05 mm apart along their
            normals), each transparent outside its own region of the three moving fronts.
  dive      frame 0: the whole head face-on 15 deg off the normal, the neck leaving the bottom; one continuous dolly
            and focus pull into the middle hole of the second row (0, 83.4 mm), ending on K04-full's composition (25 deg
            over the face, the crown ahead, 40.5 mm field, f/64 equivalent): depth of field grows as it closes in.
            The bores' K04 glow rises with the dive (lip ring -> the lined bore's depth glow). KQ_HOLE_UV=cyl.
  explode   the finished Naked racket at 3/4 (camera 30 deg above, 35 deg turned); 2-30: its head's layers lift apart
            along the face normal: front plies x3 (the feel's twill, UD +45, UD 0), the core (pale foam, carbon-lined
            bores), back plies x3 (UD 90, UD -45, the twill); 30-42 hold with a slow drift; 42-64 they close, a soft
            warm glow along every edge as they meet, and the finished racket stands again (64-71).

Usage (from render/, through the lock):
  flock render.lock $PY shots/V2-sequences.py --seq assemble|dive|explode --feel command|pace --fmt desktop|phone
        [--frames all|0,12,24|10-20] [--spp 96] [--w W --h H] [--out seq/V2-x] [--set K=V ...] [--force]
  Writes <OUT>/<out>/f%03d.png (16-bit). Default out: seq/V2-<seq>-<feel>-<fmt>. Existing frames are skipped
  (--force re-renders). --sheet <png>: also paste the rendered frames into one labelled contact sheet.
"""
import importlib.util
import math
import os
import sys
import time


def _argv():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else a[1:]


def _arg(name, default=None):
    a = _argv()
    return a[a.index("--" + name) + 1] if ("--" + name) in a and a.index("--" + name) + 1 < len(a) else default


SEQ = _arg("seq", "assemble")
if SEQ == "dive":
    os.environ.setdefault("KQ_HOLE_UV", "cyl")      # the bores' twill turns over the lip (macro: no glued-in slats)

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("K11dark", os.path.join(HERE, "K11-dark.py"))
KD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(KD)
bpy, C, studio, np, Vector = KD.bpy, KD.C, KD.studio, KD.np, KD.Vector
from mathutils import Matrix  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

NF = 72
HC = 1.0
# ------------------------------------------------------------------ framing
MARGIN_D = (0.07, 0.10)      # desktop: air (fraction of frame) top/bottom, left/right
MARGIN_P = (0.08, 0.07)      # phone
LENS = 90.0
# ------------------------------------------------------------------ assemble
A_AZ0, A_AZ1 = 20.0, 45.0    # camera azimuth off the face normal (deg), orbit over the sequence
A_EL = 7.0                   # camera elevation (deg)
A_GAP = 0.085                # m between the cores at frame 0
A_GAP12 = 0.060              # m at frame 12 (they drift together, then meet at 24)
A_TILT = 7.0                 # deg: the head core's in-plane tilt at frame 0 (settles to 0 at 24)
A_HTILT = -9.0               # deg: the handle core's
OFF_STEP = 0.00005           # m between the coincident copies (outermost foam)
FOAM_RGB = (0.56, 0.56, 0.545)
FOAM_ROUGH = 0.82
FAB_EDGE = 0.004             # m: the fabric front's soft edge
FAB_WOB = 0.006              # m: its wobble (the cloth lies down unevenly)
RES_EDGE = 0.003
RES_BAND = 0.012             # m: the amber band's half width
RES_S = 24.0                 # amber band strength (camera rays)
SW_EDGE = 0.002
SW_BAND = 0.016
SW_S = 160.0                 # sweep band strength
SW_DIR = (0.42, 1.0)         # model-space direction the sweep coordinate grows along (x, y): it runs crown -> handle
GLARE_T, GLARE_SIZE = 0.0, 8
GLARE_K = 0.6                # the bands' bloom (their AOV through a fog glow) added at this gain
DRY_ROUGH, DRY_SPEC = 0.62, 0.30
DRY_SPEC_P = 0.10             # Pace: dry black 12K reads black with a satin sheen, not pale grey
# timeline (frames)
T_JOIN = 24.0
T_FAB = (24.0, 44.0)
T_RES = (44.0, 60.0)
T_SW = (60.0, 68.0)
# ------------------------------------------------------------------ dive
D_TH0, D_TH1 = 15.0, 65.0    # deg off the face normal (toward the handle): frame 0 face-on 15, frame 71 K04's 25 deg el
D_LENS = 100.0
D_FIELD1 = 0.0405            # m: the final frame's width (K04 fw 40.5 mm)
D_FIELD1_P = 0.030           # m: the phone's final width (portrait: the hole a little larger)
D_FSTOP = 64.0
D_BUMP1 = 0.3
D_PRIM_K = 0.15             # the Pace back strips in the dive
D_EXPO1 = -0.55            # the film darkens as the camera closes in: the glow carries the macro (K04-full)
D_LFADE = {"lg_sheen": 0.0, "lg_streak": 0.0, "lg_fill": 0.3, "lg_cfill": 0.4, "lg_wall": 0.5, "lg_weave": 0.3}
D_LFADE_P = {"lg_weave": 1.0}   # Pace keeps its weave card: the 12K must still read around the hole
D_EXPO1_P = -0.2
D_LFADE_U = 0.55             # fully faded by this much of the dive (log zoom)
D_HOLE = (0.0, 0.834)        # shape units: second row, middle
D_SHIFT1 = (-0.12, 0.0)      # K04's shift at the end (desktop)
D_FOCUS = 1.8                # K04: 0 = the near lip, 1 = the hole centre, 1.8 = toward the far lip (the twill folding in)
D_GLOW0, D_GLOW1 = 0.0, 5.0  # depth glow, start / end (x GLOW_S)
D_LIP0, D_LIP1 = 1.0, 1.5    # lip ring, start / end (x the feel's lip strength)
# ------------------------------------------------------------------ explode
E_EL, E_AZ = 30.0, 35.0      # camera above / turned (deg)
E_DRIFT = 5.0                # deg of azimuth drift over the whole sequence
E_GAP = 0.110                # m between neighbouring layers when fully apart (solved per format for E_WFRAC)
E_WFRAC = 0.70               # the stack's width, fully apart, as a fraction of the frame (cloud review 15:41Z)
E_GAP_MAX = 0.20             # m: at 30/35 deg the stack runs diagonally, so 16:9 fills its height first; wider than
                             # this only shrinks every piece (desktop reaches ~60%; portrait reaches E_WFRAC)
E_MARG_Y = 0.04              # top/bottom air when fully apart
E_GAP_PHONE = 0.12           # m: the phone's spacing (portrait fits the stack by its width)
E_PLY = 0.0015               # m: a ply's drawn thickness (a thin clean sheet at screen scale)
E_BEVEL = 0.0004             # m: the ply's rounded cut edge
E_ANGS = (0.0, 45.0, -45.0)  # the weave's turn per ply, outer -> inner (front; the back mirrors it)
E_YEND = -0.176              # m (model y): the plies end where the neck meets the handle
E_SQ_Y0 = -0.140             # the core's head squeeze ramps out from here down to E_YEND
E_DENSE, E_DENSE_Y0, E_DENSE_Y1 = 0.86, -0.150, -0.180   # the handle's denser foam: tone factor and its ramp
E_GLOW = 4.0                 # edge glow strength as the layers meet
E_GLOW_W = 3.0               # its width in frames (soft, ~60 to 68)
E_T = (2.0, 30.0, 42.0, 64.0)
UD_RGB = (0.020, 0.020, 0.022)
PP_COAT, PP_ROUGH = 0.12, 0.38   # prepreg: a satin resin film, no lacquer
E_FILL_S, E_FILL_SIZE, E_FILL_D = 60.0, 1.4, 2.2

OPT = {}


def parse():
    a = _argv()
    o = {"seq": "assemble", "feel": "command", "fmt": "desktop", "frames": "all", "spp": "96", "sets": []}
    i = 0
    while i < len(a):
        k = a[i]
        if k == "--set" and i + 1 < len(a):
            o["sets"].append(a[i + 1])
            i += 2
        elif k.startswith("--") and i + 1 < len(a) and not a[i + 1].startswith("--"):
            o[k[2:]] = a[i + 1]
            i += 2
        elif k.startswith("--"):
            o[k[2:]] = True
            i += 1
        else:
            i += 1
    for kv in o["sets"]:
        for part in kv.split(","):
            k, v = part.split("=")
            k = k.strip()
            tgt = KD if (hasattr(KD, k) and not k in globals()) else None
            val = float(v)
            if tgt is not None:
                setattr(KD, k, val)
            else:
                globals()[k] = val
    o["spp"] = int(o["spp"])
    if o["fmt"] == "phone":
        o.setdefault("w", 1080)
        o.setdefault("h", 1920)
    else:
        o.setdefault("w", 2560)
        o.setdefault("h", 1440)
    o["w"], o["h"] = int(o["w"]), int(o["h"])
    fr = str(o["frames"])
    if fr == "all":
        o["frames"] = list(range(NF))
    else:
        out = []
        for p in fr.split(","):
            if "-" in p:
                x, y = p.split("-")
                out += list(range(int(x), int(y) + 1))
            else:
                out.append(int(p))
        o["frames"] = out
    o.setdefault("out", "seq/V2-%s-%s-%s" % (o["seq"], o["feel"], o["fmt"]))
    return o


# ------------------------------------------------------------------ easing
def sstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * t * (t * (t * 6 - 15) + 10)


def glide(t, k=0.18):
    """0..1 with quadratic ease-in / ease-out over the first and last k, constant speed between (C1)."""
    t = min(max(t, 0.0), 1.0)
    v = 1.0 / (1.0 - k)
    if t < k:
        return 0.5 * v * t * t / k
    if t > 1 - k:
        return 1.0 - 0.5 * v * (1 - t) * (1 - t) / k
    return 0.5 * v * k + v * (t - k)


def ramp(f, a, b):
    return sstep((f - a) / (b - a)) if b > a else float(f >= b)


# ------------------------------------------------------------------ scene
def setup(o):
    studio.reset()
    sc = bpy.context.scene
    studio.settings(o["w"], o["h"], o["spp"])
    # Metal: no background kernel specialisation (its compile thread crashed a test run: NSException in
    # ShaderCache::compile_thread_func while the shaders changed between frames)
    pr = bpy.context.preferences.addons["cycles"].preferences
    if hasattr(pr, "kernel_optimization_level"):
        pr.kernel_optimization_level = "OFF"
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.diffuse_bounces = 3
    sc.cycles.transparent_max_bounces = 24
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    sc.cycles.denoising_prefilter = "ACCURATE"
    sc.cycles.seed = 11
    sc.cycles.sample_clamp_indirect = KD.CLAMP_IND
    sc.render.use_persistent_data = True
    vl = sc.view_layers[0]
    for g in KD.GROUPS:
        vl.lightgroups.add(name=g)
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    return sc


def glare(sc):
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    # only the moving bands bloom (their own AOV), never a lacquer highlight
    vl = sc.view_layers[0]
    if "bloom" not in [a.name for a in vl.aovs]:
        a = vl.aovs.add()
        a.name = "bloom"
        a.type = "COLOR"
    rl = tr.nodes.new("CompositorNodeRLayers")
    gl = tr.nodes.new("CompositorNodeGlare")
    gl.glare_type = "FOG_GLOW"
    gl.quality = "HIGH"
    gl.threshold = 0.0
    gl.size = int(GLARE_SIZE)
    gl.mix = 1.0                     # the glow alone
    gk = tr.nodes.new("CompositorNodeMixRGB")
    gk.blend_type = "MULTIPLY"
    gk.inputs["Fac"].default_value = 1.0
    gk.inputs[2].default_value = (GLARE_K, GLARE_K, GLARE_K, 1)
    ad = tr.nodes.new("CompositorNodeMixRGB")
    ad.blend_type = "ADD"
    ad.inputs["Fac"].default_value = 1.0
    cp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(rl.outputs["bloom"], gl.inputs["Image"])
    tr.links.new(gl.outputs["Image"], gk.inputs[1])
    tr.links.new(rl.outputs["Image"], ad.inputs[1])
    tr.links.new(gk.outputs["Image"], ad.inputs[2])
    tr.links.new(ad.outputs["Image"], cp.inputs["Image"])


def racket(name, feel, holes=None, serial=C.SERIAL, walls=True):
    r, P = C.build_racket(name, feel=feel, serial=serial, walls=walls, holes=holes, mat_opts=KD.pace_opts(feel),
                          grip=False)
    return r, P


def k11_glow(r, lip_k=1.0, depth=0.0):
    """KD.main's glow pass for one racket; returns {"lip": [math nodes], "depth": [...], "edge": [...]} whose
    inputs[1] is the strength (so a sequence can animate them)."""
    P = C.parts(r)
    pc = r.get("kq_feel") == "pace"
    h = {"lip": [], "depth": [], "edge": []}

    def tagged(ob, mode, s):
        before = {m.name for m in bpy.data.materials}
        KD.set_glow(ob, mode, s)
        for m in bpy.data.materials:
            if m.name in before or not m.use_nodes:
                continue
            for n in m.node_tree.nodes:
                if n.type == "EMISSION" and n.inputs["Strength"].links and not n.get("kq_tag"):
                    n["kq_tag"] = mode
                    h[mode].append((n.inputs["Strength"].links[0].from_node, s))
    if "holes" in P and len(P["holes"].data.polygons):
        lip = (pc and KD.P_FIX > 0 and KD.P_LIP > 0) or (not pc and KD.C_LIP > 0)
        s = KD.GLOW_S * (KD.C_LIP_K if (not pc and KD.C_LIP > 0) else 1.0)
        tagged(P["holes"], "lip" if lip else "depth", s * lip_k)
        if depth > 0:
            tagged(P["holes"], "depth", KD.GLOW_S * depth)
    eg = KD.EDGE_GLOW if pc else KD.CMD_EDGE_GLOW
    if "rim" in P and eg > 0:
        tagged(P["rim"], "edge", eg)
    if pc:
        if "neck" in P:
            y_cut = max(v.co.y for v in P["neck"].data.vertices)
            KD.continuous_coat(P["neck"])
            if "rim" in P:
                KD.continuous_coat(P["rim"], y_cut)
    return h


def set_strength(handles, mode, k):
    for node, s in handles.get(mode, []):
        node.inputs[1].default_value = s * k


def look(cam, loc, target, up):
    cam.location = Vector(loc)
    f = (Vector(target) - Vector(loc)).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f).normalized()
    M = Matrix((r, u, -f)).transposed()
    cam.rotation_euler = M.to_euler()


def pts_of(objs, every=None, target=4000):
    """World points of the objects' vertices (evaluated: modifiers on), about `target` in all."""
    dg = bpy.context.evaluated_depsgraph_get()
    arrs = []
    for ob in objs:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        n = len(me.vertices)
        co = np.empty(n * 3, dtype=np.float64)
        me.vertices.foreach_get("co", co)
        ev.to_mesh_clear()
        co = co.reshape(n, 3)
        M = np.array(ob.matrix_world)
        arrs.append(co @ M[:3, :3].T + M[:3, 3])
    if not arrs:
        return np.zeros((0, 3))
    P_ = np.concatenate(arrs)
    st = max(1, len(P_) // target) if every is None else every
    return P_[::st]


def project(sc, cam, P_):
    """(u, v) in 0..1 frame coordinates (shift included) of world points (N x 3)."""
    dg = bpy.context.evaluated_depsgraph_get()
    rx, ry = sc.render.resolution_x, sc.render.resolution_y
    K = np.array(cam.calc_matrix_camera(dg, x=rx, y=ry)) @ np.array(cam.matrix_world.inverted())
    h = np.c_[np.asarray(P_), np.ones(len(P_))] @ K.T
    ndc = h[:, :2] / h[:, 3:4]
    return (ndc + 1.0) / 2.0


def fit(sc, cam, pts, aim, dirn, up, margin, shift=True):
    """Distance along dirn so every point fits inside the frame minus margin (top/bottom, sides); centred by shift."""
    cd = cam.data
    asp = sc.render.resolution_y / sc.render.resolution_x
    d = 3.0
    my, mx = margin
    for _ in range(7):
        look(cam, aim + dirn * d, aim, up)
        cd.shift_x = cd.shift_y = 0.0
        bpy.context.view_layer.update()
        uv = project(sc, cam, pts)
        su = (uv[:, 0].max() - uv[:, 0].min()) / (1 - 2 * mx)
        sv = (uv[:, 1].max() - uv[:, 1].min()) / (1 - 2 * my)
        d *= max(su, sv)
    look(cam, aim + dirn * d, aim, up)
    bpy.context.view_layer.update()
    uv = project(sc, cam, pts)
    cu = (uv[:, 0].min() + uv[:, 0].max()) / 2 - 0.5
    cv = (uv[:, 1].min() + uv[:, 1].max()) / 2 - 0.5
    big = max(sc.render.resolution_x, sc.render.resolution_y)
    sx = cu * sc.render.resolution_x / big
    sy = cv * sc.render.resolution_y / big
    return d, (sx, sy) if shift else (0.0, 0.0)


def finish_lights(sc):
    for ob_ in sc.objects:
        if ob_.type == "LIGHT":
            ob_.visible_camera = False


def exclude_from(emitter, objs):
    """`emitter` (a light or emissive mesh) no longer reaches `objs`."""
    L_ = bpy.data.objects.get(emitter)
    if L_ is None:
        return
    rc = L_.light_linking.receiver_collection
    if rc is None:
        rc = bpy.data.collections.new("recv_" + emitter)
        L_.light_linking.receiver_collection = rc
    has_inc = any(co.light_linking.link_state == "INCLUDE" for co in rc.collection_objects)
    for ob in objs:
        names = [o_.name for o_ in rc.objects]
        if ob.name in names:
            if has_inc:
                rc.objects.unlink(ob)
            else:
                rc.collection_objects[names.index(ob.name)].light_linking.link_state = "EXCLUDE"
        elif not has_inc:
            rc.objects.link(ob)
            rc.collection_objects[[o_.name for o_ in rc.objects].index(ob.name)].light_linking.link_state = "EXCLUDE"


def share_links(src, news):
    """Every light linked to `src` (include or exclude) treats `news` the same way."""
    for L_ in [o_ for o_ in bpy.data.objects if o_.type == "LIGHT" or (o_.type == "MESH" and o_.name == "lg_grade")]:
        rc = L_.light_linking.receiver_collection
        if rc is None:
            continue
        names = [ob.name for ob in rc.objects]
        if src.name not in names:
            has_inc = any(co.light_linking.link_state == "INCLUDE" for co in rc.collection_objects)
            if has_inc:
                continue            # not on the include list: not lit, nor are the copies
            continue                # exclude list without src: src lit, the copies too
        st = rc.collection_objects[names.index(src.name)].light_linking.link_state
        for n in news:
            if n.name in [ob.name for ob in rc.objects]:
                continue
            rc.objects.link(n)
            rc.collection_objects[[ob.name for ob in rc.objects].index(n.name)].light_linking.link_state = st


def mesh_copy(ob, name, parent=None, data=False):
    c = ob.copy()
    if data:
        c.data = ob.data.copy()
    c.name = name
    bpy.context.scene.collection.objects.link(c)
    mw = ob.matrix_world.copy()
    c.parent = parent
    if parent is not None:
        c.matrix_parent_inverse = parent.matrix_world.inverted()
    c.matrix_world = mw
    for k in list(c.keys()):
        if k.startswith("kq_"):
            del c[k]
    return c


def set_mat(ob, m):
    for i in range(len(ob.material_slots)):
        ob.material_slots[i].link = "OBJECT"
        ob.material_slots[i].material = m
    if not ob.material_slots:
        ob.data.materials.append(m)


def _n(nt, kind, op=None, **kw):
    n = nt.nodes.new(kind)
    if op is not None:
        n.operation = op
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def mat_foam(name="V2_Foam"):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*FOAM_RGB, 1)
    b.inputs["Roughness"].default_value = FOAM_ROUGH
    b.inputs["Specular IOR Level"].default_value = 0.25
    tc = _n(nt, "ShaderNodeTexCoord")
    vo = _n(nt, "ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 1800.0          # ~0.55 mm closed cells
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    nz = _n(nt, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 60.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = _n(nt, "ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.35
    mr.inputs["From Max"].default_value = 0.65
    mr.inputs["To Min"].default_value = 0.93
    mr.inputs["To Max"].default_value = 1.04
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    mc = _n(nt, "ShaderNodeMix")
    mc.data_type = "RGBA"
    mc.blend_type = "MULTIPLY"
    mc.inputs["Factor"].default_value = 1.0
    mc.inputs["A"].default_value = (*FOAM_RGB, 1)
    cmb = _n(nt, "ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        nt.links.new(mr.outputs["Result"], cmb.inputs[k])
    nt.links.new(cmb.outputs["Color"], mc.inputs["B"])
    nt.links.new(mc.outputs["Result"], b.inputs["Base Color"])
    bu = _n(nt, "ShaderNodeBump")
    bu.inputs["Strength"].default_value = 0.35
    bu.inputs["Distance"].default_value = 0.0002
    nt.links.new(vo.outputs["Distance"], bu.inputs["Height"])
    nt.links.new(bu.outputs["Normal"], b.inputs["Normal"])
    return m


def matte_copy(m0, tag="dry", spec=None):
    m = m0.copy()
    m.name = m0.name + "_" + tag
    nt = m.node_tree
    for b in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
        for nm, v in (("Coat Weight", 0.0), ("Roughness", DRY_ROUGH), ("Specular IOR Level", DRY_SPEC if spec is None else spec)):
            inp = b.inputs[nm]
            for l_ in list(inp.links):
                nt.links.remove(l_)
            inp.default_value = v
    return m


def prepreg(m0):
    m = m0.copy()
    m.name = m0.name + "_prepreg"
    for b in [n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"]:
        for nm, v in (("Coat Weight", PP_COAT), ("Roughness", PP_ROUGH)):
            inp = b.inputs[nm]
            for l_ in list(inp.links):
                m.node_tree.links.remove(l_)
            inp.default_value = v
    return m


def mat_ud(name, ang):
    """A unidirectional prepreg ply: black, satin, anisotropic along `ang` (deg, model space), fine tow streaks."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.30
    b.inputs["Anisotropic"].default_value = 0.85
    b.inputs["Specular IOR Level"].default_value = 0.5
    b.inputs["Coat Weight"].default_value = PP_COAT
    b.inputs["Coat Roughness"].default_value = 0.2
    a = math.radians(ang)
    tv = _n(nt, "ShaderNodeCombineXYZ")
    tv.inputs[0].default_value = math.cos(a)
    tv.inputs[1].default_value = math.sin(a)
    vt = _n(nt, "ShaderNodeVectorTransform", vector_type="VECTOR", convert_from="OBJECT", convert_to="WORLD")
    nt.links.new(tv.outputs[0], vt.inputs[0])
    nt.links.new(vt.outputs[0], b.inputs["Tangent"])
    tc = _n(nt, "ShaderNodeTexCoord")
    m1 = _n(nt, "ShaderNodeMapping")
    m1.inputs["Rotation"].default_value = (0, 0, -a)
    nt.links.new(tc.outputs["Object"], m1.inputs["Vector"])
    m2 = _n(nt, "ShaderNodeMapping")
    m2.inputs["Scale"].default_value = (8.0, 1400.0, 8.0)       # streaks along the fibre, ~0.7 mm across
    nt.links.new(m1.outputs["Vector"], m2.inputs["Vector"])
    nz = _n(nt, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 3.0
    nt.links.new(m2.outputs["Vector"], nz.inputs["Vector"])
    cr = _n(nt, "ShaderNodeMapRange")
    cr.inputs["From Min"].default_value = 0.3
    cr.inputs["From Max"].default_value = 0.7
    cr.inputs["To Min"].default_value = 0.6
    cr.inputs["To Max"].default_value = 1.6
    nt.links.new(nz.outputs["Fac"], cr.inputs["Value"])
    cc = _n(nt, "ShaderNodeCombineColor")
    for i, k in enumerate(("Red", "Green", "Blue")):
        mu = _n(nt, "ShaderNodeMath", "MULTIPLY")
        mu.inputs[1].default_value = UD_RGB[i]
        nt.links.new(cr.outputs["Result"], mu.inputs[0])
        nt.links.new(mu.outputs[0], cc.inputs[k])
    nt.links.new(cc.outputs["Color"], b.inputs["Base Color"])
    rr = _n(nt, "ShaderNodeMapRange")
    rr.inputs["From Min"].default_value = 0.3
    rr.inputs["From Max"].default_value = 0.7
    rr.inputs["To Min"].default_value = 0.24
    rr.inputs["To Max"].default_value = 0.38
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    return m


def mat_edge_glow(name="V2_EdgeGlow"):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = _n(nt, "ShaderNodeOutputMaterial")
    b = _n(nt, "ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.03, 0.03, 0.032, 1)
    b.inputs["Roughness"].default_value = 0.35
    em = _n(nt, "ShaderNodeEmission")
    em.inputs["Color"].default_value = (*KD.GLOW_EDGE, 1)
    lp = _n(nt, "ShaderNodeLightPath")
    g = _n(nt, "ShaderNodeMath", "MULTIPLY")
    g.name = "kq_edge"
    g.inputs[1].default_value = 0.0
    nt.links.new(lp.outputs["Is Camera Ray"], g.inputs[0])
    nt.links.new(g.outputs[0], em.inputs["Strength"])
    ad = _n(nt, "ShaderNodeAddShader")
    nt.links.new(b.outputs[0], ad.inputs[0])
    nt.links.new(em.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs["Surface"])
    return m


# ================================================================== ASSEMBLE
def assemble_group(ymax, ymin, throat):
    """Shader group: P (model space) -> the four copies' opacities and the two bands, from three Value nodes (Yw:
    the fabric front, y; R: the resin front, distance from the throat; S: the sweep front)."""
    g = bpy.data.node_groups.new("V2_assemble", "ShaderNodeTree")
    g.interface.new_socket("P", in_out="INPUT", socket_type="NodeSocketVector")
    for nm in ("op_foam", "op_dry", "op_fin", "op_final", "res", "swp"):
        g.interface.new_socket(nm, in_out="OUTPUT", socket_type="NodeSocketFloat")
    nt = g
    gi = _n(nt, "NodeGroupInput")
    go = _n(nt, "NodeGroupOutput")
    vals = {}
    for nm, v in (("Yw", ymax + 0.02), ("R", -0.02), ("S", -1.0), ("res_k", 0.0), ("swp_k", 0.0)):
        vn = _n(nt, "ShaderNodeValue")
        vn.name = nm
        vn.outputs[0].default_value = v
        vals[nm] = vn.outputs[0]
    sp = _n(nt, "ShaderNodeSeparateXYZ")
    nt.links.new(gi.outputs["P"], sp.inputs[0])

    def M(op, a, b=None, c=None):
        n = _n(nt, "ShaderNodeMath", op)
        for i, x in enumerate((a, b, c)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                nt.links.new(x, n.inputs[i])
        return n.outputs[0]

    def step(x, e):      # smoothstep(-e, e, x)
        n = _n(nt, "ShaderNodeMapRange")
        n.interpolation_type = "SMOOTHSTEP"
        n.inputs["From Min"].default_value = -e
        n.inputs["From Max"].default_value = e
        nt.links.new(x, n.inputs["Value"])
        return n.outputs["Result"]

    def gauss(x, w):     # exp(-(x/w)^2)
        return M("EXPONENT", M("MULTIPLY", M("POWER", M("DIVIDE", x, w), 2.0), -1.0))

    # fabric: dry where y > Yw (+ wobble across x)
    nz = _n(nt, "ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 18.0
    nz.inputs["Detail"].default_value = 2.0
    nt.links.new(gi.outputs["P"], nz.inputs["Vector"])
    wob = M("MULTIPLY", M("SUBTRACT", nz.outputs["Fac"], 0.5), FAB_WOB * 2)
    a = step(M("ADD", M("SUBTRACT", sp.outputs["Y"], vals["Yw"]), wob), FAB_EDGE)
    # resin: r = |P - throat|
    tv = _n(nt, "ShaderNodeCombineXYZ")
    tv.inputs[0].default_value, tv.inputs[1].default_value, tv.inputs[2].default_value = throat
    dv = _n(nt, "ShaderNodeVectorMath", "DISTANCE")
    nt.links.new(gi.outputs["P"], dv.inputs[0])
    nt.links.new(tv.outputs[0], dv.inputs[1])
    r = dv.outputs["Value"]
    rd = M("SUBTRACT", vals["R"], r)
    b = step(rd, RES_EDGE)
    # sweep: s = P . dir
    k = math.hypot(*SW_DIR)
    s = M("ADD", M("MULTIPLY", sp.outputs["X"], SW_DIR[0] / k), M("MULTIPLY", sp.outputs["Y"], SW_DIR[1] / k))
    sd = M("SUBTRACT", vals["S"], s)
    c = step(sd, SW_EDGE)
    nt.links.new(M("SUBTRACT", 1.0, a), go.inputs["op_foam"])
    nt.links.new(M("MULTIPLY", a, M("SUBTRACT", 1.0, b)), go.inputs["op_dry"])
    nt.links.new(M("MULTIPLY", b, M("SUBTRACT", 1.0, c)), go.inputs["op_fin"])
    nt.links.new(c, go.inputs["op_final"])
    nt.links.new(M("MULTIPLY", gauss(rd, RES_BAND), vals["res_k"]), go.inputs["res"])
    nt.links.new(M("MULTIPLY", gauss(sd, SW_BAND), vals["swp_k"]), go.inputs["swp"])
    return g


def wrap_mat(m0, role, grp):
    m = m0.copy()
    m.name = m0.name + "_" + role
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    src = out.inputs["Surface"].links[0].from_socket
    gn = _n(nt, "ShaderNodeGroup")
    gn.node_tree = grp
    tc = _n(nt, "ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Object"], gn.inputs["P"])
    tr = _n(nt, "ShaderNodeBsdfTransparent")
    mx = _n(nt, "ShaderNodeMixShader")
    nt.links.new(gn.outputs["op_" + role], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(src, mx.inputs[2])
    last = mx.outputs[0]
    lp = _n(nt, "ShaderNodeLightPath")
    aov_col = None
    for band, col, k, roles in (("res", KD.GLOW_EDGE, RES_S, ("dry", "fin")),
                                ("swp", KD.kelvin(5200.0), SW_S, ("fin", "final"))):
        if role not in roles:
            continue
        e1 = _n(nt, "ShaderNodeMath", "MULTIPLY")
        nt.links.new(gn.outputs[band], e1.inputs[0])
        nt.links.new(gn.outputs["op_" + role], e1.inputs[1])
        e2 = _n(nt, "ShaderNodeMath", "MULTIPLY")
        nt.links.new(e1.outputs[0], e2.inputs[0])
        nt.links.new(lp.outputs["Is Camera Ray"], e2.inputs[1])
        e3 = _n(nt, "ShaderNodeMath", "MULTIPLY")
        e3.inputs[1].default_value = k
        nt.links.new(e2.outputs[0], e3.inputs[0])
        em = _n(nt, "ShaderNodeEmission")
        em.inputs["Color"].default_value = (*col, 1)
        nt.links.new(e3.outputs[0], em.inputs["Strength"])
        sc_ = _n(nt, "ShaderNodeVectorMath", "SCALE")
        sc_.inputs[0].default_value = col
        nt.links.new(e3.outputs[0], sc_.inputs["Scale"])
        if aov_col is None:
            aov_col = sc_.outputs[0]
        else:
            av = _n(nt, "ShaderNodeVectorMath", "ADD")
            nt.links.new(aov_col, av.inputs[0])
            nt.links.new(sc_.outputs[0], av.inputs[1])
            aov_col = av.outputs[0]
        ad = _n(nt, "ShaderNodeAddShader")
        nt.links.new(last, ad.inputs[0])
        nt.links.new(em.outputs[0], ad.inputs[1])
        last = ad.outputs[0]
    nt.links.new(last, out.inputs["Surface"])
    if aov_col is not None:
        ao = _n(nt, "ShaderNodeOutputAOV")
        ao.aov_name = "bloom"
        nt.links.new(aov_col, ao.inputs["Color"])
    return m


def displace(ob, off):
    if off <= 0 or ob.type != "MESH":
        return
    md = ob.modifiers.new("v2_off", "DISPLACE")
    md.direction = "NORMAL"
    md.mid_level = 0.0
    md.strength = off


def section_cap(objs, y, name, mat, keep_side):
    """A flat cap at model y (the cut between the two cores): the convex hull of the parts' vertices near y."""
    pts = []
    for ob in objs:
        for v in ob.data.vertices:
            if abs(v.co.y - y) < 0.0004:
                pts.append((v.co.x, v.co.z))
    pts = sorted(set((round(x, 6), round(z, 6)) for x, z in pts))
    if len(pts) < 3:
        return None

    def cross(o_, a_, b_):
        return (a_[0] - o_[0]) * (b_[1] - o_[1]) - (a_[1] - o_[1]) * (b_[0] - o_[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    hull = lo[:-1] + hi[:-1]
    vs = [(x, y, z) for x, z in hull]
    face = list(range(len(vs)))
    if keep_side < 0:
        face.reverse()
    me = bpy.data.meshes.new(name)
    me.from_pydata(vs, [], [face])
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def run_assemble(o, sc):
    feel = o["feel"]
    final, PF = racket("KQ_FINAL", feel)
    blank, PB = racket("KQ_BLANK", feel, holes=[], serial=None, walls=False)
    dry, PD = C.clone(blank, "KQ_DRY")
    foam, PO = C.clone(blank, "KQ_FOAM")
    roots = [final, blank, dry, foam]
    for r in roots:
        C.pose(r, (0.0, 0.0, HC), tilt_deg=90.0)
        for k in ("capmark",):
            if k in C.parts(r) and r is not final:
                C.parts(r)[k].hide_render = True
    bpy.context.view_layer.update()
    hf = k11_glow(final)
    hb = k11_glow(blank)
    # model extents
    ys = [v.co.y for ob in PB.values() if ob.type == "MESH" and not ob.hide_render for v in ob.data.vertices]
    ymax, ymin = max(ys), min(ys)
    throat = (0.0, C.NECK_SPLIT_Y, 0.0)
    rmax = max(math.hypot(v.co.x - throat[0], v.co.y - throat[1]) for ob in PB.values() if ob.type == "MESH"
               for v in ob.data.vertices) + 0.004
    k = math.hypot(*SW_DIR)
    ss = [(v.co.x * SW_DIR[0] + v.co.y * SW_DIR[1]) / k for ob in PB.values() if ob.type == "MESH" for v in ob.data.vertices]
    smin, smax = min(ss), max(ss)
    grp = assemble_group(ymax, ymin, throat)
    gv = {n.name: n for n in grp.nodes if n.type == "VALUE"}
    foam_m = mat_foam()
    cache = {}
    for role, r, off in (("final", final, 0.0), ("fin", blank, OFF_STEP), ("dry", dry, 2 * OFF_STEP),
                         ("foam", foam, 3 * OFF_STEP)):
        for key, ob in C.parts(r).items():
            if ob.type != "MESH":
                continue
            for i, slot in enumerate(ob.material_slots):
                m0 = slot.material
                if m0 is None:
                    continue
                base = foam_m if role == "foam" else (matte_copy(m0, spec=DRY_SPEC_P if feel == "pace" else None) if role == "dry" else m0)
                ck = (role, base.name)
                if ck not in cache:
                    cache[ck] = wrap_mat(base, role, grp)
                ob.material_slots[i].link = "OBJECT"
                ob.material_slots[i].material = cache[ck]
            displace(ob, off)
    # the two foam cores: head (every part but the neck) and handle (the neck with the Naked butt), capped at the cut
    PO = C.parts(foam)
    head_core = [ob for k_, ob in PO.items() if k_ not in ("neck", "capmark") and ob.type == "MESH" and not ob.hide_render]
    neck_core = [PO["neck"]]
    cap_m = cache[("foam", foam_m.name)]
    cap_h = section_cap(head_core, C.NECK_SPLIT_Y, "V2_cap_head", cap_m, -1)
    cap_n = section_cap(neck_core, C.NECK_SPLIT_Y, "V2_cap_neck", cap_m, 1)
    for cp_ in (cap_h, cap_n):
        if cp_ is not None:
            cp_.parent = foam
            cp_.matrix_parent_inverse = Matrix.Identity(4)
    if cap_h is not None:
        head_core.append(cap_h)
    if cap_n is not None:
        neck_core.append(cap_n)
    base_mb = {ob.name: ob.matrix_basis.copy() for ob in head_core + neck_core}
    # pivot (model space): the throat cut's centre
    piv = Vector((0.0, C.NECK_SPLIT_Y, 0.0))

    def core_pose(f):
        if f >= T_JOIN:
            g, th, tn = 0.0, 0.0, 0.0
        else:
            if f <= 12:
                u = f / 12.0
                g = A_GAP + (A_GAP12 - A_GAP) * u
                th, tn = A_TILT * (1 - 0.3 * u), A_HTILT * (1 - 0.3 * u)
            else:
                e = sstep((f - 12) / (T_JOIN - 12))
                # velocity-matched: the drift's speed carries into the approach
                g = A_GAP12 * (1 - e)
                th, tn = A_TILT * 0.7 * (1 - e), A_HTILT * 0.7 * (1 - e)
        for obs, dy, tl in ((head_core, g / 2, th), (neck_core, -g / 2, tn)):
            R = (Matrix.Translation(piv + Vector((0, dy, 0))) @ Matrix.Rotation(math.radians(tl), 4, "Z")
                 @ Matrix.Translation(-piv))
            for ob in obs:
                ob.matrix_basis = R @ base_mb[ob.name]
        for cp_ in (cap_h, cap_n):
            if cp_ is not None:
                cp_.hide_render = f >= T_JOIN
    # camera path: orbit about the racket's centre, distance fitted to every frame's extent (non-increasing, smoothed)
    world_c = Vector((0.0, 0.0, HC + (ymax + ymin) / 2))
    cam = studio.camera(tuple(world_c + Vector((0, -3, 0))), tuple(world_c), lens=LENS)
    sc.camera = cam
    margin = MARGIN_P if o["fmt"] == "phone" else MARGIN_D
    up = Vector((0, 0, 1))

    def cdir(f):
        az = math.radians(A_AZ0 + (A_AZ1 - A_AZ0) * sstep(f / 70.0))
        el = math.radians(A_EL)
        return Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    need, shifts = [], []
    allp = lambda: pts_of([ob for ob in head_core + neck_core if not ob.hide_render])
    for f in range(NF):
        core_pose(f)
        bpy.context.view_layer.update()
        d, sh = fit(sc, cam, allp(), world_c, cdir(f), up, margin)
        need.append(d)
        shifts.append(sh)
    env = [max(need[f:]) for f in range(NF)]
    sm = []
    for f in range(NF):
        w = [env[min(max(f + j, 0), NF - 1)] for j in range(-6, 7)]
        sm.append(max(sum(w) / len(w), need[f]))
    # shift: smooth too
    shx = [sum(shifts[min(max(f + j, 0), NF - 1)][0] for j in range(-6, 7)) / 13 for f in range(NF)]
    shy = [sum(shifts[min(max(f + j, 0), NF - 1)][1] for j in range(-6, 7)) / 13 for f in range(NF)]
    # lights: built once from the mid-orbit camera
    look(cam, world_c + cdir(35) * sm[35], world_c, up)
    bpy.context.view_layer.update()
    KD.world_field(sc)
    KD.lights([final], o)
    KD.grade_card([final], cam)
    finish_lights(sc)
    C.one_racket(verbose=False)
    for r in (blank, dry, foam):
        for key, ob in C.parts(r).items():
            if key in C.parts(final):
                share_links(C.parts(final)[key], [ob])
    for cp_ in (cap_h, cap_n):
        if cp_ is not None:
            share_links(C.parts(final)["neck"], [cp_])
    glare(sc)
    rmin = -0.01

    def frame(f):
        core_pose(f)
        yw = ymax + 0.02 - (ymax - ymin + 0.04) * ramp(f, *T_FAB)
        R = rmin + (rmax - rmin + 0.02) * ramp(f, *T_RES)
        S = smin - 0.03 + (smax - smin + 0.06) * ramp(f, *T_SW)
        gv["Yw"].outputs[0].default_value = yw
        gv["R"].outputs[0].default_value = R
        gv["S"].outputs[0].default_value = S
        # the bands fade in/out at their phase's ends
        gv["res_k"].outputs[0].default_value = ramp(f, T_RES[0] - 1, T_RES[0] + 2) * (1 - ramp(f, T_RES[1] - 2, T_RES[1] + 1))
        gv["swp_k"].outputs[0].default_value = ramp(f, T_SW[0] - 1, T_SW[0] + 1.5) * (1 - ramp(f, T_SW[1] - 1.5, T_SW[1] + 0.5))
        vis = {
            foam: yw > ymin - 0.012,
            dry: (yw < ymax + 0.012) and R < rmax + 0.005,
            blank: R > rmin + 0.002 and S < smax + 0.02,
            final: S > smin - 0.02,
        }
        for r, v in vis.items():
            for key, ob in C.parts(r).items():
                if key == "capmark" and r is not final:
                    continue
                if key in ("cap",) or ob.get("kq_stub"):
                    continue
                ob.hide_render = not v
        for cp_ in (cap_h, cap_n):
            if cp_ is not None:
                cp_.hide_render = (f >= T_JOIN) or not vis[foam]
        look(cam, world_c + cdir(f) * sm[f], world_c, up)
        cam.data.shift_x, cam.data.shift_y = shx[f], shy[f]
    return frame


# ================================================================== DIVE
def run_dive(o, sc):
    feel = o["feel"]
    r, P = racket("KQ_F", feel)
    C.pose(r, (0.0, 0.0, HC), tilt_deg=90.0)
    bpy.context.view_layer.update()
    hd = k11_glow(r, depth=1.0)
    c, upv, across, nrm = KD.racket_frame(r)
    nrm = -nrm if nrm.dot(Vector((0, -1, 0))) < 0 else nrm      # toward the camera side (-Y)
    zt = C.T2 if hasattr(C, "T2") else C.ZT
    M = r.matrix_world
    hole = M @ Vector((D_HOLE[0] * C.U, D_HOLE[1] * C.U, zt if nrm.dot(M.to_3x3() @ Vector((0, 0, 1))) > 0 else -zt))
    hr = 0.062 * C.U
    phone = o["fmt"] == "phone"
    cam = studio.camera(tuple(c + nrm * 2), tuple(c), lens=D_LENS)
    sc.camera = cam
    cd = cam.data
    cd.clip_start = 0.002
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = D_FSTOP
    # the canon weave relief is set for whole-racket views; at K04's magnification it reads as quilted pillows (K04
    # MACRO_BUMP 0.08 vs 0.30): every bump eases down to D_BUMP1 of itself as the camera closes in
    bumps = []
    for ob in P.values():
        for sl in ob.material_slots:
            if sl.material is not None and sl.material.use_nodes:
                for n in sl.material.node_tree.nodes:
                    if n.type == "BUMP" and not n.inputs["Strength"].links:
                        bumps.append((n, n.inputs["Strength"].default_value))
    # frame 0: fit the head (every head part above the neck's lower end in view) face-on at D_TH0
    head = [ob for k_, ob in P.items() if k_ in ("face", "back", "rim", "wall", "holes", "throat", "bridgewall")
            or k_.startswith("thr")]
    pts = pts_of(head)

    def dirn(th):
        t = math.radians(th)
        return (nrm * math.cos(t) - upv * math.sin(t)).normalized()
    mg = MARGIN_P if phone else (0.05, 0.10)
    d0, sh0 = fit(sc, cam, pts, c, dirn(D_TH0), upv, mg)
    # the head's top sits at the frame's top margin; the neck runs out of the bottom: aim lower by the fit's own shift
    a0 = c
    asp = o["h"] / o["w"]
    big_w = max(o["w"], o["h"])
    sens = 36.0
    # field width at distance d for this lens (sensor fit AUTO: the larger side gets 36 mm)
    fw = lambda d: sens / D_LENS * d * (o["w"] / big_w)
    f1w = D_FIELD1_P if phone else D_FIELD1
    d1 = f1w * D_LENS / sens / (o["w"] / big_w)
    # hole's screen offset at frame 0 (in frame-width units), from the fitted camera
    look(cam, a0 + dirn(D_TH0) * d0, a0, upv)
    cd.shift_x, cd.shift_y = sh0
    bpy.context.view_layer.update()
    # lights from the frame-0 camera
    KD.world_field(sc)
    KD.lights([r], o)
    KD.grade_card([r], cam)
    finish_lights(sc)
    # Pace: the back strips mirror in the bores face-on (one racket: the bores take the face's lights) as white discs
    for nm in ("lg_rimL", "lg_rimR"):
        if nm in bpy.data.objects:
            bpy.data.objects[nm].data.energy *= D_PRIM_K
    if feel == "pace" and "holes" in P:
        # ... and so does the grade card: the bore linings keep K11-dark's own links (no back strips, no grade card;
        # its note: "their coat mirrored the strips as a grey film over the glow"). The face, rim, wall and neck stay
        # one racket; one_racket() skips the bores (kq_stub) so it does not widen those two links onto them
        P["holes"]["kq_stub"] = 1
    sh1 = (0.0, 0.0) if phone else D_SHIFT1
    fade = dict(D_LFADE, **(D_LFADE_P if feel == "pace" else {}))
    expo1 = D_EXPO1_P if feel == "pace" else D_EXPO1
    lfade = [(L_, L_.data.energy) for L_ in sc.objects if L_.type == "LIGHT" and L_.name in fade]

    def frame(f):
        e = glide(f / 69.0)
        th = D_TH0 + (D_TH1 - D_TH0) * sstep(min(1.0, (f - 4) / 62.0)) if f > 4 else D_TH0
        d = d0 * (d1 / d0) ** e
        # aim: from the head centre to the hole's focus point; the blend runs on the zoom's own log scale so the hole
        # drifts smoothly to its place (no swing out of frame)
        u = (math.log(d0) - math.log(d)) / (math.log(d0) - math.log(d1))
        # K04: aim at the hole's centre, focus D_FOCUS of the way from the near lip (handle side) past the centre
        fpt = hole - upv * (hr + 0.0008) * (1 - D_FOCUS)
        v0 = hole - a0
        aim = hole - v0 * (1 - sstep(u)) * (d / d0)    # the hole slides to its place in frame units, never out
        loc = aim + dirn(th) * d
        look(cam, loc, aim, upv)
        cd.shift_x = sh0[0] + (sh1[0] - sh0[0]) * sstep(u)
        cd.shift_y = sh0[1] + (sh1[1] - sh0[1]) * sstep(u)
        cd.dof.focus_distance = (fpt - loc).length
        gk = sstep((f - 14) / 50.0)
        set_strength(hd, "depth", D_GLOW0 + (D_GLOW1 - D_GLOW0) * gk)
        set_strength(hd, "lip", D_LIP0 + (D_LIP1 - D_LIP0) * gk)
        for n, s0 in bumps:
            n.inputs["Strength"].default_value = s0 * (1.0 + (D_BUMP1 - 1.0) * sstep(u))
        # the whole-racket strips mirror as white bands in the grazing macro: they fade as the camera closes in
        sc.view_settings.exposure = expo1 * sstep(min(1.0, u / 0.8))
        for L_, e0 in lfade:
            L_.data.energy = e0 * (1.0 + (fade.get(L_.name, 1.0) - 1.0) * sstep(min(1.0, u / D_LFADE_U)))
    return frame


# ================================================================== EXPLODE
# Cloud review 2026-11-13 15:41Z: exactly seven pieces, front to back 3 face plies (the feel's weave at 0, +45, -45),
# the foam core (one piece, head and handle, the handle a shade denser), 3 back plies; each ply a thin flat clean sheet
# (no displacement, the skin's own bump), round holes, the throat a clean opening, covering the head and neck only;
# the stack about 70% of the frame wide at full separation, evenly spaced, the camera still; a soft glow as they close.
def _model_xyz(ob, R_inv):
    me = ob.data
    n = len(me.vertices)
    co = np.empty(n * 3)
    me.vertices.foreach_get("co", co)
    M = np.array(R_inv @ ob.matrix_world)
    return co.reshape(n, 3) @ M[:3, :3].T + M[:3, 3]


def ply_outline(P, R_inv):
    """The ply's plan in model space (metres): the canon outline (head and neck) down to E_YEND, less the 42 holes and
    the throat, both taken from the face mesh's own boundary loops."""
    import bmesh
    from shapely.geometry import LineString, Polygon, box
    from shapely.ops import polygonize, unary_union
    face = P["face"]
    M = R_inv @ face.matrix_world
    bm = bmesh.new()
    bm.from_mesh(face.data)
    segs = []
    for e in bm.edges:
        if e.is_boundary:
            a, b = (M @ v.co for v in e.verts)
            segs.append(LineString([(round(a.x, 7), round(a.y, 7)), (round(b.x, 7), round(b.y, 7))]))
    bm.free()
    polys = sorted(polygonize(segs), key=lambda p: -p.area)
    outer = Polygon(C.outline_canon())
    cuts = [p for p in polys[1:] if p.area < 0.2 * polys[0].area]
    ply = outer.intersection(box(-1.0, E_YEND, 1.0, 1.0)).difference(unary_union(cuts))
    if ply.geom_type != "Polygon":
        ply = max(ply.geoms, key=lambda g: g.area)
    print("explode: ply plan %.1f x %.1f mm, %d openings (face loops %d), outline y %.3f..%.3f"
          % (1000 * (ply.bounds[2] - ply.bounds[0]), 1000 * (ply.bounds[3] - ply.bounds[1]), len(ply.interiors),
             len(polys), outer.bounds[1], outer.bounds[3]), flush=True)
    return ply


def skin_uv_fit(ob, R_inv):
    """UV = A @ (x, y) + b over the skin's loops (model space): the weave's own scale and direction."""
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers[0]
    nl = len(me.loops)
    vi = np.empty(nl, dtype=np.int64)
    me.loops.foreach_get("vertex_index", vi)
    uv = np.empty(nl * 2)
    uvl.data.foreach_get("uv", uv)
    uv = uv.reshape(nl, 2)
    xyz = _model_xyz(ob, R_inv)[vi]
    X = np.c_[xyz[:, 0], xyz[:, 1], np.ones(nl)]
    sol, *_ = np.linalg.lstsq(X, uv, rcond=None)
    res = np.abs(X @ sol - uv).max()
    A, b = sol[:2].T, sol[2]
    print("explode: skin UV fit residual %.4f (A %s)" % (res, np.round(A, 2).tolist()), flush=True)
    return A, b


def mat_ply_edge(feel, name="V2_PlyEdge"):
    """The ply's cut edge: the feel's tone, satin, with the closing glow (camera rays, node "kq_edge")."""
    m = mat_edge_glow(name)
    b = [n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    if feel == "pace":
        b.inputs["Base Color"].default_value = (0.030, 0.030, 0.032, 1)
        b.inputs["Roughness"].default_value = 0.35
    else:
        b.inputs["Base Color"].default_value = (0.50, 0.495, 0.475, 1)
        b.inputs["Roughness"].default_value = 0.45
    return m


def mat_core(name="V2_Core"):
    """The foam core, one piece: the handle (attribute kq_dense 1) a shade denser."""
    m = mat_foam(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    src = b.inputs["Base Color"].links[0].from_socket
    at = _n(nt, "ShaderNodeAttribute")
    at.attribute_name = "kq_dense"
    mr = _n(nt, "ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = E_DENSE
    nt.links.new(at.outputs["Fac"], mr.inputs["Value"])
    cmb = _n(nt, "ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        nt.links.new(mr.outputs["Result"], cmb.inputs[k])
    mx = _n(nt, "ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = "MULTIPLY"
    mx.inputs["Factor"].default_value = 1.0
    nt.links.new(src, mx.inputs["A"])
    nt.links.new(cmb.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], b.inputs["Base Color"])
    return m


def ply_object(name, poly, zp, up, A, b0, ang, mat, rim_mat):
    import bmesh
    c0 = np.array(poly.centroid.coords[0])
    a = math.radians(ang)
    Rm = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    bm = bmesh.new()
    vmap = {}

    def V(p):
        k = (round(p[0], 7), round(p[1], 7))
        if k not in vmap:
            vmap[k] = bm.verts.new((p[0], p[1], zp))
        return vmap[k]
    for t in C._poly_tris(poly):
        vs = [V(p) for p in t]
        if len(set(vs)) == 3:
            try:
                bm.faces.new(vs)
            except ValueError:
                pass
    bm.normal_update()
    for f in bm.faces:
        if (f.normal.z > 0) != up:
            f.normal_flip()
    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            p = np.array((lp.vert.co.x, lp.vert.co.y))
            q = Rm @ (p - c0) + c0
            lp[uvl].uv = tuple(A @ q + b0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    me.materials.append(rim_mat)
    sd = ob.modifiers.new("ply", "SOLIDIFY")
    sd.thickness = E_PLY
    sd.offset = -1.0                     # inward from the skin plane (normals point out of the racket)
    sd.use_rim = True
    sd.material_offset_rim = 1
    bv = ob.modifiers.new("edge", "BEVEL")
    bv.width = E_BEVEL
    bv.segments = 3
    bv.limit_method = "ANGLE"
    bv.angle_limit = math.radians(40.0)
    return ob


def run_explode(o, sc):
    feel = o["feel"]
    r, P = racket("KQ_F", feel)
    C.pose(r, (0.0, 0.0, HC), tilt_deg=90.0)
    bpy.context.view_layer.update()
    hf = k11_glow(r)
    Mw = r.matrix_world
    R_inv = Mw.inverted()
    zax = (Mw.to_3x3() @ Vector((0, 0, 1))).normalized()        # model +z: the front face's normal
    zf = float(_model_xyz(P["face"], R_inv)[:, 2].max())
    zb = float(_model_xyz(P["back"], R_inv)[:, 2].min())
    print("explode: parts %s; face z %.4f back z %.4f" % (sorted(P), zf, zb), flush=True)
    stack = bpy.data.objects.new("V2_stack", None)
    bpy.context.scene.collection.objects.link(stack)
    stack.matrix_world = Mw.copy()
    # ---- the core: every visible carbon part of the finished racket, in foam, as one piece; the head squeezed so the
    # plies close onto it (ramped out down the neck: the handle keeps its own section)
    core_m = mat_core()
    core = []
    skip = ("capmark", "cap", "etchR", "etchL")
    for k_, ob in P.items():
        if ob.type != "MESH" or ob.hide_render or ob.get("kq_stub") or k_ in skip or not len(ob.data.vertices):
            continue
        cc = mesh_copy(ob, "V2_core_" + k_, data=True)
        cc.parent = stack
        cc.matrix_parent_inverse = Matrix.Identity(4)
        Mp = R_inv @ ob.matrix_world
        cc.matrix_basis = Mp
        me = cc.data
        n = len(me.vertices)
        co = np.empty(n * 3)
        me.vertices.foreach_get("co", co)
        co = co.reshape(n, 3)
        Mn = np.array(Mp)
        mod = co @ Mn[:3, :3].T + Mn[:3, 3]
        y = mod[:, 1]
        t = np.clip((E_SQ_Y0 - y) / (E_SQ_Y0 - E_YEND), 0.0, 1.0)
        t = t * t * (3 - 2 * t)
        kz_top = (zf - 3 * E_PLY) / zf
        kz_bot = (-zb - 3 * E_PLY) / -zb
        kz = np.where(mod[:, 2] >= 0, kz_top, kz_bot)
        mod[:, 2] *= kz + (1.0 - kz) * t
        Mi = np.linalg.inv(Mn)
        co = mod @ Mi[:3, :3].T + Mi[:3, 3]
        me.vertices.foreach_set("co", co.ravel())
        dz = np.clip((E_DENSE_Y0 - y) / (E_DENSE_Y0 - E_DENSE_Y1), 0.0, 1.0)
        at = me.attributes.new("kq_dense", "FLOAT", "POINT")
        at.data.foreach_set("value", (dz * dz * (3 - 2 * dz)).astype(np.float32))
        me.update()
        set_mat(cc, core_m)
        core.append(cc)
    # ---- plies: flat sheets on the face (front) and back planes, E_PLY thick inward, the weave turned per ply
    poly = ply_outline(P, R_inv)
    skin = P["back"]
    counts = {}
    for p_ in skin.data.polygons:
        counts[p_.material_index] = counts.get(p_.material_index, 0) + 1
    skin_m = skin.material_slots[max(counts, key=counts.get)].material
    if feel == "pace":                          # a lacquered black ply mirrors the stage like chrome: satin prepreg
        skin_m = prepreg(skin_m)
    A, b0 = skin_uv_fit(skin, R_inv)
    edge_m = mat_ply_edge(feel)
    plies = []                                                   # (empty, side +1/-1, rank from the core 1..3, mesh)
    for side, z0 in ((1, zf), (-1, zb)):
        for i, ang in enumerate(E_ANGS):                         # outer -> inner
            pe = bpy.data.objects.new("V2_ply%+d_%d" % (side, i), None)
            bpy.context.scene.collection.objects.link(pe)
            pe.parent = stack
            pe.matrix_basis = Matrix.Identity(4)
            pc = ply_object("V2_plymesh%+d_%d" % (side, i), poly, z0 - side * i * E_PLY, side > 0, A, b0,
                            side * ang, skin_m, edge_m)
            pc.parent = pe
            pc.matrix_parent_inverse = Matrix.Identity(4)
            pc.matrix_basis = Matrix.Identity(4)
            plies.append((pe, side, 3 - i, pc))
    # ---- camera: 30 deg above, 35 deg turned, a slow drift; still otherwise (one distance and shift for all frames)
    phone = o["fmt"] == "phone"
    margin = MARGIN_P if phone else MARGIN_D
    up = Vector((0, 0, 1))
    nfront = zax if zax.dot(Vector((0, -1, 0))) > 0 else -zax

    def cdir(f):
        az = math.radians(E_AZ + E_DRIFT * (sstep(f / 70.0) - 0.5))
        el = math.radians(E_EL)
        h = (Matrix.Rotation(az, 3, Vector((0, 0, 1))) @ nfront)
        h.z = 0
        h.normalize()
        return (h * math.cos(el) + up * math.sin(el)).normalized()

    def sep(f):
        a, b, c_, d_ = E_T
        if f <= a:
            return 0.0
        if f <= b:
            return ramp(f, a, b)
        if f <= c_:
            return 1.0 + 0.03 * math.sin(math.pi * (f - b) / (c_ - b))
        return 1.0 - ramp(f, c_, d_)

    gap = [E_GAP]

    def place(s):
        for pe, side, rank, pc in plies:
            pe.matrix_basis = Matrix.Translation(Vector((0, 0, side * rank * gap[0] * s)))
    cam = studio.camera(tuple(Mw.translation + nfront * 3), tuple(Mw.translation), lens=LENS)
    sc.camera = cam
    shown = [ob for ob in P.values() if not ob.hide_render and not ob.get("kq_stub")]
    closed = pts_of([ob for k_, ob in P.items() if not ob.hide_render and k_ not in ("capmark",)])
    aimc = Vector(((closed.min(0) + closed.max(0)) / 2).tolist())
    stack_objs = core + [pc for _, _, _, pc in plies]

    def marg(s):          # apart, the stack may use more of the height (the camera looks down the diagonal it makes);
        k = sstep(min(1.0, max(0.0, s)))       # portrait: more side air, so the stack spans about E_WFRAC of the width
        if phone:
            return (margin[0], margin[1] + (0.5 * (1.0 - E_WFRAC) - margin[1]) * k)
        return (margin[0] + (E_MARG_Y - margin[0]) * k, margin[1])

    def width_at(g):
        gap[0] = g
        place(1.0)
        bpy.context.view_layer.update()
        sp = pts_of(stack_objs)
        fit(sc, cam, sp, aimc, cdir(36), up, marg(1.0))
        return float(np.ptp(project(sc, cam, sp)[:, 0]))
    # the gap: the stack E_WFRAC of the frame wide if the frame allows (portrait), else as wide as E_GAP_MAX gives
    lo, hi = 0.01, E_GAP_MAX
    if phone:                                   # portrait is width-bound at any gap: a fixed spacing
        lo = E_GAP_PHONE
    elif width_at(hi) <= E_WFRAC:
        lo = hi
    else:
        for _ in range(16):
            mid = 0.5 * (lo + hi)
            if width_at(mid) < E_WFRAC:
                lo = mid
            else:
                hi = mid
    wf = width_at(lo)
    print("explode: gap %.1f mm, stack %.0f%% of the frame wide at full separation" % (1000 * gap[0], 100 * wf),
          flush=True)
    # the camera follows the stack (as the preview): fitted to every frame's extent, then smoothed (a moving max,
    # then a moving mean, never closer than the frame's own fit)
    base = pts_of([ob for k_, ob in P.items() if not ob.hide_render and k_ not in ("capmark",)])
    need, shs0 = [], []
    for f in range(NF):
        s_ = sep(f)
        place(s_)
        bpy.context.view_layer.update()
        pf = np.concatenate([base, pts_of(stack_objs)]) if s_ > 0 else base
        d_, sh_ = fit(sc, cam, pf, aimc, cdir(f), up, marg(s_))
        need.append(d_)
        shs0.append(sh_)
    W_ = 5
    mx_ = [max(need[max(0, f - W_):f + W_ + 1]) for f in range(NF)]
    dist_f = [max(need[f], sum(mx_[max(0, f - W_):f + W_ + 1]) / len(mx_[max(0, f - W_):f + W_ + 1])) for f in range(NF)]
    shx = [sum(x[0] for x in shs0[max(0, f - W_):f + W_ + 1]) / len(shs0[max(0, f - W_):f + W_ + 1]) for f in range(NF)]
    shy = [sum(x[1] for x in shs0[max(0, f - W_):f + W_ + 1]) / len(shs0[max(0, f - W_):f + W_ + 1]) for f in range(NF)]
    dist = dist_f[36]
    shift = (shx[36], shy[36])
    # lights from the hold's camera, built on the finished racket; the stack shares its links
    look(cam, aimc + cdir(36) * dist, aimc, up)
    cam.data.shift_x, cam.data.shift_y = shift
    bpy.context.view_layer.update()
    KD.world_field(sc)
    KD.lights([r], o)
    KD.grade_card([r], cam)
    finish_lights(sc)
    C.one_racket(verbose=False)
    share_links(P["face"], stack_objs)
    if os.environ.get("KQ_E_NOGRADE", "1") == "1":     # the Pace grade card is aimed off the face's mirror; moved toward
        exclude_from("lg_grade", [pc for _, _, _, pc in plies])   # the camera, the plies would mirror it grey
    # the stack's own soft fill from just above the camera (every ply shades the next); it fades as the layers close
    import k789_lib as KL7
    fd = (cdir(36) + up * 0.35).normalized()
    xf = studio.area_light("lg_xfill", tuple(aimc + fd * E_FILL_D), E_FILL_SIZE, E_FILL_S, color=KD.kelvin(6000.0),
                           target=tuple(aimc))
    xf.visible_camera = False
    xf.visible_glossy = False                   # diffuse only: its reflection washed the near Pace plies grey
    KL7.link_receivers(xf, stack_objs, "recv_xfill")

    def frame(f):
        s = sep(f)
        place(s)
        stacked = E_T[0] < f < E_T[3]
        for ob in shown:
            ob.hide_render = stacked
        for ob in stack_objs:
            ob.hide_render = not stacked
        # the soft warm edge glow as they meet (frames ~60 to 68)
        g = math.exp(-((f - E_T[3]) / E_GLOW_W) ** 2)
        edge_m.node_tree.nodes["kq_edge"].inputs[1].default_value = E_GLOW * g
        set_strength(hf, "edge", 1.0 + 3.0 * g)
        xf.data.energy = E_FILL_S * sstep(min(1.0, s / 0.5))
        look(cam, aimc + cdir(f) * dist_f[f], aimc, up)
        cam.data.shift_x, cam.data.shift_y = shx[f], shy[f]
    return frame


# ================================================================== main
def contact_sheet(paths, out_png, width=1280):
    from PIL import Image, ImageDraw
    ims = []
    for f, p in paths:
        im = bpy.data.images.load(p, check_existing=False)
        W, H = im.size
        px = np.empty(W * H * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        a = (np.clip(px.reshape(H, W, 4)[::-1, :, :3], 0, 1) * 255 + 0.5).astype(np.uint8)
        pi = Image.fromarray(a, "RGB")
        h = int(round(H * width / W))
        pi = pi.resize((width, h), Image.LANCZOS)
        ImageDraw.Draw(pi).text((14, 10), "f%03d" % f, fill=(200, 200, 200))
        ims.append(pi)
        bpy.data.images.remove(im)
    gap = 6
    sheet = Image.new("RGB", (width, sum(i.height for i in ims) + gap * (len(ims) - 1)), (40, 40, 40))
    y = 0
    for i in ims:
        sheet.paste(i, (0, y))
        y += i.height + gap
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    sheet.save(out_png)
    return out_png


def main():
    o = parse()
    OPT.update(o)
    t0 = time.time()
    sc = setup(o)
    run = {"assemble": run_assemble, "dive": run_dive, "explode": run_explode}[o["seq"]]
    frame = run(o, sc)
    out_dir = KD.out_path(os.path.join(o["out"], "x"))[:-6]
    os.makedirs(out_dir, exist_ok=True)
    print("v2: built in %.1fs; %s -> %s" % (time.time() - t0, o["seq"], out_dir), flush=True)
    if o.get("dry"):
        return
    done = []
    for f in o["frames"]:
        dst = os.path.join(out_dir, "f%03d.png" % f)
        if os.path.exists(dst) and not o.get("force"):
            done.append((f, dst))
            continue
        t1 = time.time()
        frame(f)
        for nm in str(o.get("off") or "").split(","):
            if nm and nm in bpy.data.objects:
                bpy.data.objects[nm].data.energy = 0.0
        bpy.context.view_layer.update()
        sc.frame_current = 1
        sc.render.filepath = dst + ".tmp.png"
        bpy.ops.render.render(write_still=True)
        os.replace(dst + ".tmp.png", dst)
        done.append((f, dst))
        print("v2: f%03d %.1fs" % (f, time.time() - t1), flush=True)
        with open(os.path.join(out_dir, "frames.log"), "a") as fh:
            fh.write("f%03d %.1fs spp %d %dx%d\n" % (f, time.time() - t1, o["spp"], o["w"], o["h"]))
    if o.get("sheet"):
        print("sheet", contact_sheet(done, KD.out_path(o["sheet"])), flush=True)
    print("v2: done %d frames in %.1fs" % (len(done), time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
