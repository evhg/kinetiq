"""K17-roughness (owner, 2026-11-02, after the factory meeting): the face's engineered roughness, in K04 / K14's macro
language. The instant of a slice: a padel ball on the canonical face (Command white 3K twill by default, --feel pace =
black 12K), seen from just above the face. The face carries a moulded micro-texture under its clear coat (a regular
field of rounded micro-domes, ROUGH_PITCH apart: it reads as engineered, never as wear or grit), the ball sits slightly
compressed on it, its felt fibres pressed into the texture and dragged along the stroke, and the ball is starting to
spin (motion blur about the contact point: the felt blurs more the farther it is from the contact; an optional faint
spin arc). Words go upper left (the graphite void beyond the head); the contact sits right of centre.

Geometry (metres, the racket's model space: face in XY, +Z out of the front face, head up +Y):
  the contact point CX, CY on the face between holes; the ball (BALL_R 32.5 mm) flattened by COMPRESS onto the face
  with a smooth patch edge; the seam a 3.5 mm off-white ribbon on the classic two-lobe curve; FIBRES felt strands
  (hair curves, 5 points each, 0.5-1.4 mm, curly), roots on the camera's side of the ball, none on the seam; inside the
  patch they lie flat on the domes and are dragged along +x (the face moves +x under the ball: a slice).
  The camera looks along +y from EL degrees above the face.
Light groups (one render, composited by gains like K14; --comp re-grades from the EXR):
  key    a soft area light behind left (backlights the felt fuzz on the ball's silhouette, rakes the domes)
  pool   a spot from the front left: the white face's diffuse gradient and the ball's front
  gloss  a card in the coat's mirror direction: the micro-domes break its reflection into a field of tiny highlights,
         the roughness made visible
  rim    a low strip behind right: the felt's right silhouette and a line on the coat
  fill   weak diffuse fill
  arc    the spin arc (camera-only emission); g_arc 0 leaves it out
Outputs: <out>.png (full), <out>-base.png (key + fill + a dim pool: the scroll light's start), <out>.exr, <out>.json.

Usage (from render/, through the lock):
  flock render.lock $PY shots/K17-roughness.py --w 960 --h 540 --spp 32 --out k17/p01 [--feel pace] [--set K=v ...]
  final: flock render.lock $PY shots/K17-roughness.py --w 2560 --h 1440 --spp 96 --out final/K17-roughness
  re-comp: $PY shots/K17-roughness.py --comp final/K17-roughness.exr --out final/K17-roughness [--set g_gloss=1.2]
"""
import json
import math
import os
import sys
import time
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import kqpaths  # noqa: E402,F401

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import studio  # noqa: E402
import kq_canon as C  # noqa: E402
import k12_lib as K  # noqa: E402

_spec = importlib.util.spec_from_file_location("k14", os.path.join(HERE, "K14-edge.py"))
K14 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K14)

GROUPS = ("key", "pool", "gloss", "rim", "fill", "arc")
K14.GROUPS = GROUPS          # K14's comp / comp_from_exr sum these groups

ZT = C.ZT
DEFAULTS = dict(
    # contact and ball
    CX=0.062, CY=-0.080,     # m: the contact point on the face: the bridge, below the last hole row, right of the
                             # throat (11 mm patch, 18 mm clear of the nearest hole, 30 mm from the edge)
    BALL_R=0.0325, COMPRESS=0.0022, PATCH_SOFT=0.0016, BULGE=0.00025,
    SEAM_A=0.70, SEAM_ROT_X=15.0, SEAM_ROT_Z=50.0, SEAM_W=0.0034,
    FIBRES=170000.0, FIB_LEN0=0.0005, FIB_LEN1=0.0014, FIB_R=0.000011, FIB_LIFT=0.45, FIB_CURL=0.55,
    FIB_VIS=0.25,            # roots only where the ball's normal faces the camera more than this (cos)
    DRAG=0.0011, DRAG_REACH=0.004,   # m: how far the pressed fibres are dragged along +x, and how far past the patch
    SPIN_DEG=2.2,            # deg: the ball's turn about the contact point during the shutter (motion blur)
    # felt
    FELT=(0.62, 0.70, 0.075), FELT_SHEEN=1.0, FIB_COL=(0.70, 0.78, 0.10), FIB_ROUGH=0.30, FIB_RROUGH=0.55,
    # roughness texture (moulded under the coat)
    ROUGH_PITCH=0.00034, ROUGH_DOME=0.36, ROUGH_H=0.000030, ROUGH_STR=1.0, ROUGH_COAT=0.06, ROUGH_GRIT=0.15,
    # camera
    EL=14.0, AZ=0.0, DIST=0.30, FW=0.10, TX=-0.022, TZ=0.014, SHIFT_X=0.0, SHIFT_Y=-0.10, FSTOP=22.0,
    FOCUS_DY=-0.006,         # m: focus this far in front of the contact (toward the camera)
    # lights
    KEY=4.0, KEY_AZ=-160.0, KEY_EL=10.0, KEY_D=0.45, KEY_SIZE=0.15,   # a low rake from behind left: every dome a glint
    POOL=25.0, POOL_AZ=-50.0, POOL_EL=50.0, POOL_D=0.5, POOL_DEG=22.0, POOL_BLEND=0.9,  # front left, high
    GLOSS=14.0, GLOSS_D=0.5, GLOSS_W=0.10, GLOSS_LEN=0.6, GLOSS_DEL=1.5, GLOSS_AZ=22.0,
    RIM=10.0, RIM_AZ=150.0, RIM_EL=8.0, RIM_D=0.45, RIM_LEN=0.5,
    FILL=0.3, FILL_AZ=30.0, FILL_EL=40.0,
    ARC=3.0, ARC_R=0.0048, ARC_A0=118.0, ARC_A1=176.0, ARC_W=0.00018,
    # backdrop (K14 make_bg, linear)
    BG_TOP=0.014, BG_HOR=0.032, BG_GLOW=0.035, BG_GX=0.30, BG_GY=-1.0, BG_GRX=0.45, BG_GRY=0.30, BG_WARM=0.03,
    # gains (full)
    g_key=1.0, g_pool=1.0, g_gloss=1.0, g_rim=1.0, g_fill=1.0, g_arc=1.0,
    # base variant gains (the scroll light's start)
    b_key=1.0, b_pool=0.35, b_gloss=0.15, b_rim=1.0, b_fill=1.0, b_arc=0.0,
)
PACE_SET = dict(GLOSS=8.0, POOL=40.0)


def parse_args():
    argv = sys.argv[1:]
    o = {"w": 960, "h": 540, "spp": 32, "out": "k17/p", "feel": "command", "set": []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--set":
            o["set"].append(argv[i + 1]); i += 2
        elif a.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            o[a[2:]] = argv[i + 1]; i += 2
        elif a.startswith("--"):
            o[a[2:]] = True; i += 1
        else:
            i += 1
    for k in ("w", "h", "spp"):
        o[k] = int(o[k])
    p = dict(DEFAULTS)
    if o["feel"] == "pace":
        p.update(PACE_SET)
    for s in o["set"]:
        k, v = s.split("=", 1)
        assert k in p, "unknown setting " + k
        p[k] = eval(v)
    return o, p


# ------------------------------------------------------------------ the roughness texture
def add_roughness(mat, p):
    """The moulded micro-texture: a hexagonal field of rounded micro-domes (ROUGH_PITCH apart, ROUGH_DOME of the pitch
    in radius, ROUGH_H high) plus a whisper of fine grit, as bump on the fibre layer AND the clear coat (the coat is
    moulded with it), and a slightly less glassy coat. Object coordinates in metres (the racket at identity)."""
    nb = K.NB(mat)
    nodes = mat.node_tree.nodes
    b = next(nd for nd in nodes if nd.type == "BSDF_PRINCIPLED" and (nd.inputs["Coat Weight"].default_value > 0.5
                                                                     or nd.inputs["Coat Weight"].is_linked))
    x, y, _ = nb.coords("Object")
    s3 = math.sqrt(3.0)
    pitch = float(p["ROUGH_PITCH"])

    def vec(a, b_):
        cv = nodes.new("ShaderNodeCombineXYZ")
        nb.l.new(a, cv.inputs[0]); nb.l.new(b_, cv.inputs[1])
        return cv.outputs[0]

    px = nb.math("DIVIDE", x, pitch)
    py = nb.math("DIVIDE", y, pitch)

    def cell_d(ox, oy):
        v = vec(nb.math("SUBTRACT", px, ox), nb.math("SUBTRACT", py, oy))
        w = nodes.new("ShaderNodeVectorMath")
        w.operation = "WRAP"
        nb.l.new(v, w.inputs[0])
        w.inputs[1].default_value = (0.5, s3 / 2, 1.0)
        w.inputs[2].default_value = (-0.5, -s3 / 2, -1.0)
        ln = nodes.new("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        nb.l.new(w.outputs[0], ln.inputs[0])
        return ln.outputs["Value"]

    d = nb.math("MINIMUM", cell_d(0.0, 0.0), cell_d(0.5, s3 / 2))
    rr = float(p["ROUGH_DOME"])
    q = nb.math("MINIMUM", nb.math("DIVIDE", d, rr), 1.0)
    dome = nb.math("SQRT", nb.math("MAXIMUM", nb.math("SUBTRACT", 1.0, nb.math("MULTIPLY", q, q)), 0.0))
    # the domes' feet blend into the floor (no crease)
    dome = nb.math("MULTIPLY", dome, nb.smooth(q, 1.0, 0.82))
    h = dome
    if float(p["ROUGH_GRIT"]) > 0:
        gn = nodes.new("ShaderNodeTexNoise")
        gn.inputs["Scale"].default_value = 1.0 / (pitch * 0.35)
        gn.inputs["Detail"].default_value = 3.0
        tc = nodes.new("ShaderNodeTexCoord")
        nb.l.new(tc.outputs["Object"], gn.inputs["Vector"])
        h = nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", gn.outputs["Fac"], 0.5), float(p["ROUGH_GRIT"]), h)
    for inp in ("Normal", "Coat Normal"):
        bp = nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = float(p["ROUGH_STR"])
        bp.inputs["Distance"].default_value = float(p["ROUGH_H"])
        nb.l.new(h, bp.inputs["Height"])
        if b.inputs[inp].is_linked:
            nb.l.new(b.inputs[inp].links[0].from_socket, bp.inputs["Normal"])
        nb.l.new(bp.outputs["Normal"], b.inputs[inp])
    if not b.inputs["Coat Roughness"].is_linked:
        b.inputs["Coat Roughness"].default_value = float(p["ROUGH_COAT"])
    return mat


# ------------------------------------------------------------------ the ball
def seam_curve(a, n=1200):
    """The two-lobe ball seam on the unit sphere (a + b = 1): x = a cos t + b cos 3t, y = a sin t - b sin 3t,
    z = 2 sqrt(ab) sin 2t."""
    b = 1.0 - a
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([a * np.cos(t) + b * np.cos(3 * t), a * np.sin(t) - b * np.sin(3 * t), 2 * np.sqrt(a * b) * np.sin(2 * t)], 1)


def make_deform(p):
    """Ball-local (centre origin) -> deformed: everything below the contact plane z = -R + COMPRESS is pushed up onto it
    with a smooth max (PATCH_SOFT), and the rubber bulges a little (BULGE) round the patch."""
    R, dc, k = p["BALL_R"], p["COMPRESS"], p["PATCH_SOFT"]
    zf = -R + dc   # the face plane in ball-local z

    def smax(a, b_):
        return 0.5 * (a + b_ + np.sqrt((a - b_) ** 2 + k * k))

    # solve zp so that min over the sphere of smax(z, zp) = zf (the bottom point z = -R)
    lo, hi = zf - 0.01, zf
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if smax(-R, mid) > zf:
            hi = mid
        else:
            lo = mid
    zp = 0.5 * (lo + hi)
    rp = math.sqrt(max(R * R - zp * zp, 0.0))   # patch radius (about)

    def f(P):
        P = np.array(P, dtype=np.float64)
        z = P[:, 2]
        z2 = smax(z, zp)
        r = np.hypot(P[:, 0], P[:, 1])
        bul = p["BULGE"] * np.exp(-((z - zp - 0.004) / 0.006) ** 2) * (r > 1e-9)
        sc_ = 1.0 + bul / np.maximum(r, 1e-9)
        out = P.copy()
        out[:, 0] *= sc_
        out[:, 1] *= sc_
        out[:, 2] = z2
        return out
    return f, zf, rp


def build_ball(p, centre, cam_loc, rng):
    R = p["BALL_R"]
    deform, zf, rp = make_deform(p)
    print("contact patch radius about %.1f mm" % (rp * 1000), flush=True)
    pivot = bpy.data.objects.new("BallPivot", None)
    bpy.context.scene.collection.objects.link(pivot)
    pivot.location = Vector((centre.x, centre.y, centre.z + zf))   # the contact point
    root = bpy.data.objects.new("Ball", None)
    bpy.context.scene.collection.objects.link(root)
    root.parent = pivot
    root.location = (0.0, 0.0, -zf)                                # the ball centre, relative to the contact
    # sphere
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=6, radius=R)
    co = np.array([v.co[:] for v in bm.verts])
    co = deform(co)
    for v, c_ in zip(bm.verts, co):
        v.co = Vector(c_)
    me = bpy.data.meshes.new("BallMesh")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    sph = bpy.data.objects.new("BallSphere", me)
    bpy.context.scene.collection.objects.link(sph)
    sph.parent = root
    sph.data.materials.append(mat_felt(p))
    # seam: a ribbon on the curve, oriented by SEAM_ROT_X / _Z
    rot = (Matrix.Rotation(math.radians(p["SEAM_ROT_Z"]), 3, "Z") @ Matrix.Rotation(math.radians(p["SEAM_ROT_X"]), 3, "X"))
    Rm = np.array(rot)
    sc_ = seam_curve(p["SEAM_A"]) @ Rm.T
    tg = np.roll(sc_, -1, 0) - np.roll(sc_, 1, 0)
    tg /= np.linalg.norm(tg, axis=1)[:, None]
    side = np.cross(sc_, tg)
    side /= np.linalg.norm(side, axis=1)[:, None]
    hw = p["SEAM_W"] / 2
    rs = R + 0.00012
    rows = []
    for k_ in np.linspace(-1, 1, 5):
        q = sc_ + side * (hw * k_ / R)
        q /= np.linalg.norm(q, axis=1)[:, None]
        rows.append(deform(q * (rs - 0.00008 * k_ * k_)))
    bm = bmesh.new()
    vv = [[bm.verts.new(Vector(c_)) for c_ in row] for row in rows]
    n_ = len(sc_)
    for r_ in range(len(rows) - 1):
        for i in range(n_):
            j = (i + 1) % n_
            bm.faces.new((vv[r_][i], vv[r_][j], vv[r_ + 1][j], vv[r_ + 1][i]))
    me = bpy.data.meshes.new("SeamMesh")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    seam = bpy.data.objects.new("BallSeam", me)
    bpy.context.scene.collection.objects.link(seam)
    seam.parent = root
    seam.data.materials.append(mat_seam())
    # fibres
    hair = build_fibres(p, R, deform, zf, rp, sc_, centre, cam_loc, rng)
    hair.parent = root
    return pivot, root, [sph, seam, hair], (zf, rp)


def build_fibres(p, R, deform, zf, rp, seam_pts, centre, cam_loc, rng):
    n = int(p["FIBRES"])
    # roots: uniform on the sphere, kept where the normal faces the camera (and the patch), off the seam
    m = int(n * 3.2)
    v = rng.normal(size=(m, 3))
    v /= np.linalg.norm(v, axis=1)[:, None]
    to_cam = np.array(cam_loc - centre)
    to_cam /= np.linalg.norm(to_cam)
    keep = (v @ to_cam > p["FIB_VIS"]) | (v[:, 2] < -0.80)
    v = v[keep]
    # off the seam
    dd = np.empty(len(v))
    for i0 in range(0, len(v), 20000):
        blk = v[i0:i0 + 20000]
        dd[i0:i0 + 20000] = np.sqrt(np.maximum(2.0 - 2.0 * (blk @ seam_pts.T).max(1), 0.0))  # chord to the seam
    v = v[dd * R > p["SEAM_W"] * 0.5 + 0.0002][:n]
    n = len(v)
    print("fibres", n, flush=True)
    npt = 5
    L = rng.uniform(p["FIB_LEN0"], p["FIB_LEN1"], n)
    # a random tangent per fibre, leaning by FIB_LIFT toward the normal
    a = rng.normal(size=(n, 3))
    a -= v * (a * v).sum(1)[:, None]
    a /= np.linalg.norm(a, axis=1)[:, None]
    lift = rng.uniform(0.15, 1.0, n) * p["FIB_LIFT"]
    d0 = a + v * lift[:, None]
    d0 /= np.linalg.norm(d0, axis=1)[:, None]
    pts = np.zeros((n, npt, 3))
    pts[:, 0] = v * (R - 0.00005)
    d = d0.copy()
    for k in range(1, npt):
        curl = rng.normal(size=(n, 3)) * p["FIB_CURL"]
        d = d + curl
        d /= np.linalg.norm(d, axis=1)[:, None]
        # never back into the ball
        out = (d * v).sum(1)
        d = d - v * np.minimum(out, 0.0)[:, None] * 1.2
        d /= np.linalg.norm(d, axis=1)[:, None]
        pts[:, k] = pts[:, k - 1] + d * (L / (npt - 1))[:, None]
    flat = deform(pts.reshape(-1, 3)).reshape(n, npt, 3)
    # the patch: points under the face plane lie on it (just above the domes); near and in the patch the fibres are
    # dragged along +x by the face moving under the ball, the drag fading DRAG_REACH past the patch edge
    zmin = zf + 0.00003
    rxy = np.hypot(flat[:, :, 0], flat[:, :, 1])
    w = np.clip(1.0 - (rxy - rp) / p["DRAG_REACH"], 0.0, 1.0) * np.clip((zf + 0.006 - flat[:, :, 2]) / 0.006, 0.0, 1.0)
    w = w * (np.arange(npt) / (npt - 1))[None, :]  # roots stay, tips are dragged
    flat[:, :, 0] += w * p["DRAG"]
    flat[:, :, 2] = np.maximum(flat[:, :, 2], zmin)
    hc = bpy.data.hair_curves.new("Felt")
    hc.add_curves([npt] * n)
    hc.position_data.foreach_set("vector", flat.astype(np.float32).ravel())
    ra = hc.attributes.new("radius", "FLOAT", "POINT")
    rad = np.tile(np.linspace(1.0, 0.45, npt), n) * p["FIB_R"]
    ra.data.foreach_set("value", rad.astype(np.float32))
    ob = bpy.data.objects.new("FeltFibres", hc)
    bpy.context.scene.collection.objects.link(ob)
    hc.materials.append(mat_fibre(p))
    return ob


def mat_felt(p):
    m = K.new_mat("Felt")
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    tc = nb.n.new("ShaderNodeTexCoord")
    nz = nb.n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 900.0
    nz.inputs["Detail"].default_value = 8.0
    nz.inputs["Roughness"].default_value = 0.7
    nb.l.new(tc.outputs["Object"], nz.inputs["Vector"])
    tone = nb.math("MULTIPLY_ADD", nz.outputs["Fac"], 0.5, 0.75)
    cc = nb.n.new("ShaderNodeCombineColor")
    for k, c_ in enumerate(p["FELT"]):
        nb.l.new(nb.math("MULTIPLY", tone, float(c_)), cc.inputs[k])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Sheen Weight"].default_value = float(p["FELT_SHEEN"])
    b.inputs["Sheen Roughness"].default_value = 0.35
    b.inputs["Sheen Tint"].default_value = (*p["FIB_COL"], 1.0)
    bp = nb.n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.6
    bp.inputs["Distance"].default_value = 0.0002
    nb.l.new(nz.outputs["Fac"], bp.inputs["Height"])
    nb.l.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_fibre(p):
    m = K.new_mat("FeltFibre")
    nt = m.node_tree
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    h = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    h.parametrization = "COLOR"
    h.inputs["Color"].default_value = (*p["FIB_COL"], 1.0)
    h.inputs["Roughness"].default_value = float(p["FIB_ROUGH"])
    h.inputs["Radial Roughness"].default_value = float(p["FIB_RROUGH"])
    h.inputs["Coat"].default_value = 0.0
    h.inputs["IOR"].default_value = 1.55
    nt.links.new(h.outputs[0], out.inputs["Surface"])
    return m


def mat_seam():
    m = K.new_mat("Seam")
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.62, 0.62, 0.60, 1)
    b.inputs["Roughness"].default_value = 0.55
    nb.l.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_emit(name, strength, color=(1.0, 0.97, 0.92)):
    m = K.new_mat(name)
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    e = nb.n.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    nb.l.new(e.outputs[0], out.inputs["Surface"])
    m["strength_socket"] = 1
    return m, e, nb


def build_arc(p, pivot_world, centre_world, cam_loc, rt):
    """The spin arc: a thin camera-only emissive tube on a circle ARC_R outside the ball, in the plane through the ball
    centre facing the camera, from ARC_A0 to ARC_A1 deg (0 = +x, counter-clockwise seen from the camera), fading at
    both ends."""
    R = p["BALL_R"] + p["ARC_R"]
    vc = (cam_loc - centre_world).normalized()
    ex = (rt - vc * rt.dot(vc)).normalized()   # frame right
    ey = vc.cross(ex).normalized()
    ts = np.radians(np.linspace(p["ARC_A0"], p["ARC_A1"], 160))
    bm = bmesh.new()
    rings = []
    seg = 8
    for t_ in ts:
        c_ = centre_world + (ex * math.cos(t_) + ey * math.sin(t_)) * R
        tg = (ex * -math.sin(t_) + ey * math.cos(t_)).normalized()
        u = (c_ - centre_world).normalized()
        w = tg.cross(u).normalized()
        rings.append([bm.verts.new(c_ + (u * math.cos(2 * math.pi * k / seg) + w * math.sin(2 * math.pi * k / seg)) * p["ARC_W"])
                      for k in range(seg)])
    for i in range(len(rings) - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            idx = min(range(len(rings)), key=lambda i: (rings[i][0].co - lp.vert.co).length)
            lp[uvl].uv = (idx / (len(rings) - 1), 0.0)
    me = bpy.data.meshes.new("ArcMesh")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("SpinArc", me)
    bpy.context.scene.collection.objects.link(ob)
    m = K.new_mat("ArcMat")
    nb = K.NB(m)
    out = nb.n.new("ShaderNodeOutputMaterial")
    e = nb.n.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (1.0, 0.96, 0.90, 1)
    u_, _, _ = nb.coords("UV")
    fade = nb.math("MULTIPLY", nb.smooth(u_, 0.0, 0.35), nb.smooth(u_, 1.0, 0.75))
    nb.l.new(nb.math("MULTIPLY", fade, float(p["ARC"])), e.inputs["Strength"])
    nb.l.new(e.outputs[0], out.inputs["Surface"])
    m.cycles.emission_sampling = "NONE"
    ob.data.materials.append(m)
    K.visibility(ob, camera=True, diffuse=False, glossy=False, shadow=False)
    ob.lightgroup = "arc"
    return ob


# ------------------------------------------------------------------ scene
def build(o, p):
    pace = o["feel"] == "pace"
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.use_denoising = False
    sc.cycles.seed = 7
    sc.cycles_curves.shape = "THICK"
    sc.cycles_curves.subdivisions = 2
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in GROUPS:
        vl.lightgroups.add(name=g)
    rng = np.random.default_rng(11)

    mo = None if pace else {"bump": 0.10, "dir_tone": 0.22, "streak_a": 0.14}
    root, parts = C.build_racket("KQ", feel=o["feel"], walls=False, mat_opts=mo, grip=False)
    for nm in ("cap", "capmark", "neck", "back"):
        if nm in parts:
            parts[nm].hide_render = True
    face = parts["face"]
    m = face.data.materials[0].copy()
    m.name = "K17_FaceRough"
    face.data.materials[0] = m
    add_roughness(m, p)

    Pc = Vector((p["CX"], p["CY"], ZT))
    z = Vector((0, 0, 1))
    az = math.radians(p["AZ"])
    vh = Vector((math.sin(az), math.cos(az), 0))      # the camera's heading (along +y at AZ 0)
    rt = vh.cross(z).normalized()                      # frame right
    T = Pc + rt * p["TX"] + z * p["TZ"]
    el = math.radians(p["EL"])
    cam_loc = T - vh * p["DIST"] * math.cos(el) + z * p["DIST"] * math.sin(el)
    cd = bpy.data.cameras.new("Cam")
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    K14.look_at(cam, cam_loc, T)
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
    cd.lens = 36.0 * p["DIST"] / p["FW"]
    cd.shift_x = p["SHIFT_X"]
    cd.shift_y = p["SHIFT_Y"]
    cd.clip_start = 0.01
    cd.dof.use_dof = p["FSTOP"] > 0
    cd.dof.aperture_fstop = max(p["FSTOP"], 1.0)
    view = (T - cam_loc).normalized()
    cd.dof.focus_distance = ((Pc + vh * p["FOCUS_DY"]) - cam_loc).dot(view)

    # the ball: centre above the contact by R - COMPRESS
    centre = Pc + z * (p["BALL_R"] - p["COMPRESS"])
    pivot, broot, bobs, (zf, rp) = build_ball(p, centre, cam_loc, rng)
    # the spin: a turn about the contact point (rolling on the face: the patch holds, the far felt blurs), the bottom
    # carried along +x by the face, so the top goes -x; motion blur over the shutter
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 1.0
    sc.render.motion_blur_position = "CENTER"
    ax = vh  # the turn's axis: along the view, so the felt moves across the image
    for fr, sgn in ((0, 1.0), (2, -1.0)):
        sc.frame_set(fr)
        pivot.rotation_mode = "QUATERNION"
        pivot.rotation_quaternion = Matrix.Rotation(math.radians(-p["SPIN_DEG"] * 0.5 * sgn * -1.0), 4, ax).to_quaternion()
        pivot.keyframe_insert("rotation_quaternion", frame=fr)
    for fc in pivot.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    sc.frame_set(1)
    if p["ARC"] > 0:
        build_arc(p, Pc, centre, cam_loc, rt)

    def dirv(azd, eld):
        """Direction from the contact: az from the camera's heading reversed (0 = toward the camera, + = frame right),
        elevation."""
        a, e = math.radians(azd), math.radians(eld)
        h = -vh * math.cos(a) + rt * math.sin(a)
        return (h * math.cos(e) + z * math.sin(e)).normalized()

    head = [parts[k] for k in ("face", "rim", "wall", "holes", "throat", "bridgewall") if k in parts]
    ball = bobs
    excl = K14.collection("k17_no_bores", [parts["holes"]])
    for it in excl.collection_objects:
        it.light_linking.link_state = "EXCLUDE"
    if p["KEY"] > 0:
        kd = dirv(p["KEY_AZ"], p["KEY_EL"])
        key = studio.area_light("lg_key", tuple(Pc + kd * p["KEY_D"]), p["KEY_SIZE"], p["KEY"], color=(1.0, 0.985, 0.97),
                                target=tuple(Pc + z * 0.02))
        key.lightgroup = "key"
    if p["POOL"] > 0:
        pd_ = dirv(p["POOL_AZ"], p["POOL_EL"])
        pool = studio.spot_light("lg_pool", tuple(Pc + pd_ * p["POOL_D"]), p["POOL"], p["POOL_DEG"], blend=p["POOL_BLEND"],
                                 color=(1.0, 0.985, 0.97), target=tuple(Pc + z * 0.01), radius=0.02)
        pool.lightgroup = "pool"
        pool.visible_glossy = False
        pool.light_linking.receiver_collection = excl
    # gloss: the coat's mirror direction from the camera over the face just in front of the contact
    G = Pc - vh * 0.012
    vg = (G - cam_loc).normalized()
    mir = (vg - 2 * vg.dot(z) * z).normalized()
    mel = math.degrees(math.asin(mir.z)) + p["GLOSS_DEL"]
    if p["GLOSS"] > 0:
        gd = (vh * math.cos(math.radians(mel)) + z * math.sin(math.radians(mel))).normalized()
        gd = (Matrix.Rotation(math.radians(p["GLOSS_AZ"]), 3, z) @ gd).normalized()
        gb = K14.K04.panel("lg_gloss", tuple(G + gd * p["GLOSS_D"]), (p["GLOSS_LEN"], p["GLOSS_W"]), p["GLOSS"], tuple(G),
                           color=(0.95, 0.965, 1.0), edge=(-1.0, -0.5), fade=(0, 1.0))
        K14._orient_card(gb, G, rt)
        gb.visible_diffuse = False
        gb.lightgroup = "gloss"
        gb.light_linking.receiver_collection = K14.collection("k17_gloss_recv", head)
    if p["RIM"] > 0:
        rd = dirv(p["RIM_AZ"], p["RIM_EL"])
        rim = studio.area_light("lg_rim", tuple(centre + rd * p["RIM_D"]), p["RIM_LEN"], p["RIM"], color=(0.96, 0.975, 1.0),
                                size_y=0.03, target=tuple(centre))
        rim.lightgroup = "rim"
    if p["FILL"] > 0:
        fd = dirv(p["FILL_AZ"], p["FILL_EL"])
        fill = studio.area_light("lg_fill", tuple(Pc + fd * 0.6), 0.8, p["FILL"], color=(0.97, 0.98, 1.0), target=tuple(Pc))
        fill.visible_glossy = False
        fill.lightgroup = "fill"
        fill.light_linking.receiver_collection = excl
    sc.render.film_transparent = True
    # the far edge of the head: the backdrop's horizon
    tip = Vector((0.0, C.TIP_Y, ZT))
    return sc, cam, parts, tip, ball


def comp_variant(o, p, exr, out, gains):
    """Re-grade the EXR with gains (K14's comp_from_exr) into <out>.png."""
    pp = dict(p)
    for g in GROUPS:
        pp["g_" + g] = gains.get(g, p["g_" + g])
    oo = dict(o)
    oo["comp"] = exr
    oo["out"] = out
    K14.comp_from_exr(oo, pp)


def main():
    o, p = parse_args()
    if o.get("comp"):
        K14.comp_from_exr(o, p)
        base = {g: p["b_" + g] for g in GROUPS}
        comp_variant(o, p, o["comp"], o["out"] + "-base", base)
        return
    t0 = time.time()
    stem = K14.out_stem(o["out"])
    sc, cam, parts, tip, ball = build(o, p)
    print("scene built %.1f s" % (time.time() - t0), flush=True)
    if o.get("crop"):
        x0, x1, y0, y1 = [float(v) for v in str(o["crop"]).split(",")]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = y0, y1
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    hy = 1.0 - world_to_camera_view(sc, cam, tip).y
    pc = world_to_camera_view(sc, cam, Vector((p["CX"], p["CY"], ZT)))
    print("contact in frame (x, y from top): %.3f %.3f; horizon %.3f" % (pc.x, 1 - pc.y, hy), flush=True)
    json.dump(dict(o={k: v for k, v in o.items() if k != "set"}, p={k: v for k, v in p.items()}, horizon_y=hy,
                   contact=[pc.x, 1 - pc.y], size=[sc.render.resolution_x, sc.render.resolution_y]),
              open(stem + ".json", "w"), indent=1, default=list)
    K14.comp(sc, o, p, stem)
    sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.exr_codec = "ZIP"
    sc.render.filepath = stem + ".exr"
    bpy.ops.render.render(write_still=True)
    K14.finish(stem)
    print("rendered", stem + ".png", round(time.time() - t0, 1), "s", flush=True)
    base = {g: p["b_" + g] for g in GROUPS}
    comp_variant(o, p, stem + ".exr", o["out"] + "-base", base)
    print("done", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
