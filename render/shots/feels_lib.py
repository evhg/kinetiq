"""Shared helpers for the feels group (K08-feel-pair, K11-pair), stage 3a (art-director critique, 2026-10-22).

- honeycomb(): an emitter factor that is 1 only along the mirror path to the camera (K05 v6's "gridded strip"): the
  clear coat (roughness 0.03) sees the card at full strength, the white fibres' broad sheen lobe cannot gather it from
  the whole face (which lifted the shade and greyed the white).
- band_card_hc(): k789_lib.band_card (hard edge, hot line, exponential fall-off) with an optional depth fall-off
  (K11's front-to-rear stripe), an optional honeycomb and glossy-only visibility for white Command.
- mark_az(): the angle that turns the engraved Q on the cap round the handle axis to face the camera (as k01_lib).
- cap_card(): a soft gradient card in the cap's mirror direction, linked to the cap and its Q: a satin gradient across
  the cap's front band (bright edge on one side, falling away) instead of a flat lit badge or a dead-black lump.
"""
import math

import numpy as np
import k789_lib as L
from k789_lib import Matrix, Vector, bpy
import kq_canon as C


def mirror_point(cam, n, p0):
    """The camera mirrored in the plane through p0 with normal n (the virtual camera a flat coat reflects)."""
    n = Vector(n).normalized()
    cam = Vector(cam)
    return cam - 2.0 * (cam - Vector(p0)).dot(n) * n


def honeycomb(nb, cprime, tol_deg):
    """Factor socket: 1 where the ray arriving at this emitter point comes from the direction of cprime (within
    tol_deg * 0.35), falling to 0 at tol_deg. Geometry 'Incoming' points back along the ray, toward the shading point,
    which lies on the line from the card point to the virtual camera cprime."""
    geo = nb.n.new("ShaderNodeNewGeometry")
    vs = nb.n.new("ShaderNodeVectorMath")
    vs.operation = "SUBTRACT"
    vs.inputs[0].default_value = tuple(cprime)
    nb.l.new(geo.outputs["Position"], vs.inputs[1])
    vn = nb.n.new("ShaderNodeVectorMath")
    vn.operation = "NORMALIZE"
    nb.l.new(vs.outputs[0], vn.inputs[0])
    vd = nb.n.new("ShaderNodeVectorMath")
    vd.operation = "DOT_PRODUCT"
    nb.l.new(geo.outputs["Incoming"], vd.inputs[0])
    nb.l.new(vn.outputs[0], vd.inputs[1])
    return nb.smooth(vd.outputs["Value"], math.cos(math.radians(tol_deg)), math.cos(math.radians(tol_deg * 0.35)))


def band_card_hc(name, loc, size, strength, target, grad_world, edge=0.0, soft=0.006, decay=0.10, line=0.0,
                 line_w=0.004, color=(1, 1, 1), depth=None, cprime=None, tol_deg=2.6, glossy_only=False, body=1.0):
    """Hard-edged band (k789_lib.band_card): a crisp step at `edge`, an exponential fall-off over `decay` toward the
    bright side (scaled by `body`), a Gaussian hot line `line` x strength, `line_w` wide, on the edge. depth: K11's
    front-to-rear fall-off fn(card) -> fn(nb). cprime: honeycomb toward that virtual camera. glossy_only: no diffuse."""
    ob = L.plane(name, size, loc, normal_to=target)
    bpy.context.view_layer.update()
    mw = ob.matrix_world.to_3x3()
    g = Vector(grad_world).normalized()
    gx, gy = mw.col[0].normalized().dot(g), mw.col[1].normalized().dot(g)
    ln = math.hypot(gx, gy) or 1
    gx, gy = gx / ln, gy / ln
    dfn = depth(ob) if depth else None

    def s(nb):
        x, y, _ = nb.coords("Object")
        t_ = nb.math("SUBTRACT", nb.math("MULTIPLY_ADD", x, gx, nb.math("MULTIPLY", y, gy)), edge)
        stepf = nb.smooth(t_, -soft / 2, soft / 2)
        fall = nb.math("EXPONENT", nb.math("DIVIDE", nb.math("MINIMUM", nb.math("MULTIPLY", t_, -1.0), 0.0), decay))
        f = nb.math("MULTIPLY", nb.math("MULTIPLY", stepf, fall), body)
        if line:
            dd = nb.math("DIVIDE", t_, line_w)
            f = nb.math("ADD", f, nb.math("MULTIPLY", nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", dd, dd), -1.0)), line))
        u, v, _ = nb.coords("UV")
        e = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.08), nb.smooth(u, 1.0, 0.92)),
                    nb.math("MULTIPLY", nb.smooth(v, 0.0, 0.08), nb.smooth(v, 1.0, 0.92)))
        f = nb.math("MULTIPLY", f, e)
        if dfn is not None:
            f = nb.math("MULTIPLY", f, dfn(nb))
        if cprime is not None:
            f = nb.math("MULTIPLY", f, honeycomb(nb, cprime, tol_deg))
        return nb.math("MULTIPLY", f, strength)

    ob.data.materials.append(L.emitter_mat(name + "Mat", color, s, additive=True))
    L.visibility(ob, camera=False, diffuse=not glossy_only, glossy=True, shadow=False)
    return ob


def mark_az(pose_m, cam):
    """Degrees to turn the cap's Q round the handle axis (toward model +x) so it faces cam, for a racket whose
    root will have matrix pose_m (k01_lib's construction)."""
    dq = pose_m.inverted() @ Vector(cam) - Vector((0.0, -0.2925, 0.0))
    return math.degrees(math.atan2(dq.x, dq.z))


def pose_matrix(loc, yaw_deg=0.0, roll_deg=0.0, tilt_deg=90.0):
    """k789_lib.pose's matrix, without a root to set it on."""
    return (Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(yaw_deg), 4, "Z")
            @ Matrix.Rotation(math.radians(tilt_deg), 4, "X") @ Matrix.Rotation(math.radians(roll_deg), 4, "Z"))


def cap_point(root):
    """World point and outward normal of the cap's front band at the mark's height."""
    pr = C.cap_profile()
    yk = -0.2998 + C.CAP_SHIFT
    s_k = float(np.interp(-yk, [-y for (_, y) in pr], [s_ for (s_, _) in pr]))
    G, _ = C.section(64, grow=C.TAPE)
    mw = root.matrix_world
    Pc = mw @ Vector((0.0, yk, float(G[:, 1].max()) * s_k))
    nw = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
    return Pc, nw


def cap_card(name, root, cam, energy, size=(0.30, 0.50), dist=0.40, yaw_deg=0.0, lo=0.0, hi=1.0, floor=0.0,
             axis="u", color=(1.0, 0.985, 0.97), az_deg=0.0):
    """A soft gradient card in the cap's mirror direction (turned yaw_deg about the vertical, and its own normal turned
    az_deg about the handle axis so it follows the Q), linked to the cap and its Q only. The satin cap (roughness 0.3)
    mirrors it as a soft graded band across its front, the groove reads as a dark line through it, and the Q's
    bright-cut chamfer (its normals sloping 45 deg into the cut) catches its upper part. axis/lo/hi grade it."""
    P = C.parts(root)
    Pc, nw = cap_point(root)
    ax = (root.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    nw = (Matrix.Rotation(math.radians(az_deg), 3, ax) @ nw).normalized()
    r = Matrix.Rotation(math.radians(yaw_deg), 3, "Z") @ L.mirror_dir(nw, Pc, cam)
    ob = L.gradient_card(name, tuple(Pc + r * dist), size, energy, tuple(Pc), color=color, axis=axis, lo=lo, hi=hi,
                         floor=floor)
    L.link_receivers(ob, [P["cap"], P["capmark"]], "recv_" + name)
    return ob


def lift_outside(mk, cap, offset=0.00002):
    """kq_canon.build_cap_mark shrink-wraps the mark to the NEAREST cap surface point and keeps the side it started
    on. Turned (az != 0) round the oval cap, the flat mark starts inside it, so the whole Q ends 0.02 mm under the
    surface and never renders (at az 12 deg, K01's, about two thirds of it). Put every vertex `offset` outside the cap
    along the cap's normal there (what wrap_mode OUTSIDE_SURFACE does)."""
    ci = cap.matrix_world.inverted()
    cn = cap.matrix_world.to_3x3()
    mw = mk.matrix_world
    mi = mw.inverted()
    moved = 0
    for v in mk.data.vertices:
        w = mw @ v.co
        ok, loc, n, _ = cap.closest_point_on_mesh(ci @ w)
        if not ok:
            continue
        nw = (cn @ n).normalized()
        lw = cap.matrix_world @ loc
        if (w - lw).dot(nw) < offset * 0.5:
            v.co = mi @ (lw + nw * offset)
            moved += 1
    mk.data.update()
    print("cap mark: %d of %d vertices lifted outside the cap" % (moved, len(mk.data.vertices)), flush=True)
    return moved


def turn_mark(roots, az):
    """Rebuild the cap's engraved Q turned az degrees round the handle axis (kq_canon.build_cap_mark's az) and give it
    to every racket in roots (a racket and its clones share the mesh). The racket is moved back to model space while
    the mark is shrink-wrapped onto its cap, so this works after posing; light-linking collections keep their objects."""
    import os
    if os.environ.get("KQ_AZ_TEST"):  # debug: force this angle
        az = float(os.environ["KQ_AZ_TEST"])
    src = roots[0]
    P = C.parts(src)
    M = src.matrix_world.copy()
    src.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()
    mk = C.build_cap_mark(src.name + "_capmark_az", P["cap"], az=az)
    lift_outside(mk, P["cap"])
    for m in P["capmark"].data.materials:
        if os.environ.get("KQ_MARK_EMIT"):  # debug: show where the mark is
            m = bpy.data.materials.get("KQdbg_emit") or bpy.data.materials.new("KQdbg_emit")
            m.use_nodes = True
            em = m.node_tree.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (1, 0, 0, 1)
            em.inputs["Strength"].default_value = 2.0
            m.node_tree.links.new(em.outputs[0], m.node_tree.nodes["Material Output"].inputs["Surface"])
        mk.data.materials.append(m)
    basis = mk.matrix_world.copy()
    src.matrix_world = M
    for r in roots:
        old = C.parts(r)["capmark"]
        old.data = mk.data
        old.matrix_parent_inverse = Matrix.Identity(4)
        old.matrix_basis = basis.copy()
    bpy.data.objects.remove(mk)
    bpy.context.view_layer.update()
    return az


def face_az(root, cam):
    """The az that faces this (posed) racket's Q to cam."""
    return mark_az(root.matrix_world, cam)


def _hull(u, v):
    pts = sorted(set(zip(np.round(u, 5).tolist(), np.round(v, 5).tolist())))
    if len(pts) < 3:
        return pts

    def cross(o_, a_, b_):
        return (a_[0] - o_[0]) * (b_[1] - o_[1]) - (a_[1] - o_[1]) * (b_[0] - o_[0])
    lo_, hi_ = [], []
    for p_ in pts:
        while len(lo_) >= 2 and cross(lo_[-2], lo_[-1], p_) <= 0:
            lo_.pop()
        lo_.append(p_)
    for p_ in reversed(pts):
        while len(hi_) >= 2 and cross(hi_[-2], hi_[-1], p_) <= 0:
            hi_.pop()
        hi_.append(p_)
    return lo_[:-1] + hi_[:-1]


def masks(named, cam, W, H, lens):
    """Frame-fraction polygons (x from the left, y from the top) for a level camera looking +Y: each racket's front
    face, holes (1.25 x radius circles) and cap, keyed '<name>_face' etc. (for feels_tools/fmeasure.py)."""
    k = lens / 36.0

    def proj(ob, co):
        mw = np.array(ob.matrix_world)
        wc = co @ mw[:3, :3].T + mw[:3, 3]
        dy = wc[:, 1] - cam.y
        return 0.5 + k * (wc[:, 0] - cam.x) / dy, 0.5 - k * (W / H) * (wc[:, 2] - cam.z) / dy

    def verts(ob):
        co = np.empty(len(ob.data.vertices) * 3)
        ob.data.vertices.foreach_get("co", co)
        return co.reshape(-1, 3)

    res = {}
    for nm, r in named.items():
        P = C.parts(r)
        face = P["face"]
        co = verts(face)
        res[nm + "_face"] = _hull(*proj(face, co[co[:, 2] > C.T2 - 1e-4]))
        hl = []
        for (hx, hy, hr) in C.holes_canon():
            ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
            rr = hr * C.U * 1.25
            c = np.stack([hx * C.U + rr * np.cos(ang), hy * C.U + rr * np.sin(ang), np.full(24, C.T2)], 1)
            u, v = proj(face, c)
            hl.append(list(zip(u.tolist(), v.tolist())))
        res[nm + "_holes"] = hl
        res[nm + "_cap"] = _hull(*proj(P["cap"], verts(P["cap"])[::3]))
    return res


def cap_box(name, root, cam, energy, size=0.30, dist=0.35, az_deg=0.0, yaw_deg=0.0, color=(1.0, 0.985, 0.97)):
    """canon_test.cap_light (the proof's lit satin band behind a crisp Q) in world space, for a posed racket: a small
    softbox (size x 0.35 size) in the mirror direction of the cap's front band where the Q sits, its normal turned
    az_deg round the handle axis (the Q's own turn, so the band lights round the mark that faces the camera), linked to
    the cap and its Q only."""
    P = C.parts(root)
    Pc, nw = cap_point(root)
    ax = (root.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    R = Matrix.Rotation(math.radians(az_deg), 3, ax)
    o = root.matrix_world.translation
    Pc = o + R @ (Pc - o)  # the mark's point on the band (approximately: the section is an oval, not a circle)
    nw = (R @ nw).normalized()
    r = Matrix.Rotation(math.radians(yaw_deg), 3, "Z") @ L.mirror_dir(nw, Pc, cam)
    import studio
    lt = studio.area_light(name, tuple(Pc + r * dist), size, energy, color=color, size_y=size * 0.35, target=tuple(Pc))
    lt.visible_camera = False
    L.link_receivers(lt, [P["cap"], P["capmark"]], "recv_" + name)
    return lt


def look_at(ob, loc, tgt, up):
    """Light orientation with an explicit up (canon_test.look_at): local X right, local Y up, -Z toward tgt."""
    fwd = (Vector(tgt) - Vector(loc)).normalized()
    rt = fwd.cross(Vector(up)).normalized()
    upv = rt.cross(fwd)
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ Matrix((rt, upv, -fwd)).transposed().to_4x4()


def cap_rim(name, root, cam, energy, side_deg=-60.0, size=(0.04, 0.50), dist=0.30, az_deg=0.0, color=(1.0, 0.985, 0.97)):
    """A tall thin strip beside the cap: its direction is the camera's, turned side_deg round the handle axis (negative =
    camera-left), so the satin cap carries one vertical highlight line down its curve (a rim) and the Q's bright-cut
    chamfer, whose normals slope 45 deg into the cut, flashes on the side facing it. Linked to the cap and its Q."""
    import studio
    P = C.parts(root)
    Pc, _ = cap_point(root)
    ax = (root.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    o = root.matrix_world.translation
    Pc = o + Matrix.Rotation(math.radians(az_deg), 3, ax) @ (Pc - o)
    v = Vector(cam) - Pc
    v = (v - v.dot(ax) * ax).normalized()
    d = (Matrix.Rotation(math.radians(side_deg), 3, ax) @ v).normalized()
    lt = studio.area_light(name, tuple(Pc + d * dist), size[0], energy, color=color, size_y=size[1])
    look_at(lt, Pc + d * dist, Pc, ax)
    lt.visible_camera = False
    L.link_receivers(lt, [P["cap"], P["capmark"]], "recv_" + name)
    return lt


def cap_lights(name, root, cam, az_deg, k=1.0, box=0.0, box_size=0.30, box_d=0.35, rim=0.0, rim_side=-60.0,
               rim_size=(0.04, 0.50), rim_d=0.30, card=0.0, card_size=(0.30, 0.45), card_d=0.40, card_lo=0.0,
               card_hi=1.0, card_floor=0.15, card_az=0.0, color=(1.0, 0.985, 0.97)):
    """The cap's light set (stage 3a): any of the canon box (box W), a side rim strip (rim W) and a soft gradient card
    in the cap's mirror direction (card strength), each scaled by k; all linked to the cap and its Q only. card_az
    turns the card's reference normal card_az degrees past the Q's own (az_deg): the Q's bright-cut chamfer slopes 45 deg
    into the cut, so it flashes only for a light well off the view axis; a card straight in front lights the satin round
    the Q as much as the Q (no mark)."""
    out = []
    if box * k > 0:
        out.append(cap_box(name + "_box", root, cam, box * k, size=box_size, dist=box_d, az_deg=az_deg, color=color))
    if rim * k > 0:
        out.append(cap_rim(name + "_rim", root, cam, rim * k, side_deg=rim_side, size=rim_size, dist=rim_d, az_deg=az_deg,
                           color=color))
    if card * k > 0:
        out.append(cap_card(name + "_card", root, cam, card * k, size=card_size, dist=card_d, lo=card_lo, hi=card_hi,
                            floor=card_floor, axis="u", color=color, az_deg=az_deg + card_az))
    return out
