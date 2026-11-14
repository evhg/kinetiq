"""E2E-concepts: the cloud REQUEST edge-to-edge-concepts (2026-11-11 02:02Z; owner: options to replace K14 under "Edge to
edge.", compared on a preview page; masters only, no export). K11-dark's dark K04 look (imported: canon racket, full
weave, the command-dark-lift and pace-dark-fix as OK'd), Command and Pace, 5120x2880.

  A  "the face fills with light": the whole racket face-on (a slight three-quarter); a warm 2700 K light rises from the
     centre of the face and floods the flat face outward, stopping at a thin bright line where the flat face ends, 1 mm
     from the edge. Six stages (0, 20, 40, 60, 80, 100 %) and the 100 % with the line, all from ONE render (so they are
     pixel-registered): the flood is an emission under the face's clear coat in its own light group ("flood", camera-
     visible only, it lights nothing), and the face writes two AOVs from a mask in face coordinates: e2e_r (0 at the
     deepest point of the face, 1 at its boundary: 1 - distance to the boundary / the largest distance, so every stage's
     front runs parallel to the edge and reaches the whole edge at once) and e2e_in (1 on the flat face). The comp keeps
     the flood where e2e_r < stage, with a slightly brighter front, and adds the hairline where e2e_r -> 1.
  Claim guard: the images show the design ("as designed"); nothing in them reads as a percentage or "no dead zones".

Usage (bpy module; one render at a time):
  flock render.lock $PY shots/E2E-concepts.py --concept a --feel command --w 5120 --h 2880 --spp 160 --out final/e2e/E2E-A
  -> <out>-base.png, -full.png, -s000 ... -s100.png, -s100-line.png (and _card crops). --set KEY=VALUE sets K11-dark's
  constants (comma-separated), --eset KEY=VALUE this script's.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("K11dark", os.path.join(HERE, "K11-dark.py"))
KD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(KD)

bpy, C, studio, np, Vector = KD.bpy, KD.C, KD.studio, KD.np, KD.Vector
import k789_lib as KL7  # noqa: E402
import k10_lib as L10  # noqa: E402

# ------------------------------------------------------------------ concept A
YAW_A = 10.0             # a slight three-quarter (K11 single: 25 Command / 40 Pace)
MASK_PX = 0.00015        # m per mask pixel
MASK_STEP = 0.0004       # m between distance levels
STAGES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
SOFT = 0.035             # the front's soft width (e2e_r units)
FRONT_K, FRONT_W = 1.5, 0.03   # the brighter front: x (1 + FRONT_K) at the front, its gaussian width (e2e_r units)
FLOOD_G_PACE = 0.35      # A Pace: the under-coat light on the black 12K (0.8 read as copper paint)
FLOOD_G = 0.8            # flood emission gain in the comp (shader emission 1)
STUDIO_K = 0.45          # A: the studio outside the light (the light's advance reads; 10:45Z: not black)
TINT_A = 0.35            # A (10:45Z): inside the light the white twill takes a 2700 K tint of this much (not opaque)
IN_K = 1.05              # A: the studio inside the light, x
HEAD_FIT = 0.10          # A (10:45Z): the head framed to 80 % of the height (air top and bottom), the handle runs out
STUDIO_B = 0.6           # B, C (10:45Z): the command-dark-lift white face, undimmed
STUDIO_C = 1.0
LINE_W = 0.012           # the hairline's width (e2e_r units; the face's deepest point is ~0.1 m from its boundary)
LINE_G = 60.0             # the hairline's gain over the flood
TOW_K = (0.55, 0.45)     # Command: flood x (TOW_K[0] + TOW_K[1] x tow height)
P_TAPE_K = (0.85, 0.15)  # Pace: flood x (P_TAPE_K[0] + P_TAPE_K[1] x tape parity)
FLOOD_K = 2700.0
GLOW_K, GLOW_THR, GLOW_SIZE = 0.6, 0.8, 7   # a soft fog glow from the flood alone (the light reads as light)

# ------------------------------------------------------------------ concept B: flat to the edge
EL_B = 16.0               # deg: the camera above the face plane (grazing), looking across the face's width
LENS_B, FW_B = 100.0, 0.24   # mm; frame width at the target (m): the head, crown at frame right
TY_B = 0.03              # m: the target along the long axis from the head centre
FSTOP_B = 11.0
BACK_B = 0.10            # B (10:45Z): the camera behind the crown, looking along the face toward the throat
YS_B = (-0.075, 0.13)    # m (model y): the line's first and last stage (above the throat .. below the crown)
BW_B = 0.0015            # m: the line's half width (gaussian)
TRAIL_B, TRAIL_L = 0.10, 0.03   # a faint trail behind the line (toward the throat): x, decay length (m)
LINE_GB = 35.0            # the line's gain
WALL_B = 0.5             # the line on the 38 mm wall, x (it bends over the radius and fades down the wall)

# ------------------------------------------------------------------ concept C: a ball at the very edge
VIEW_C = 1.0             # 1 hero (close, three-quarter), 0 wide (the whole racket)
IMPACT_IN = 0.004        # m: the contact patch's centre inside the outline at the head's widest point
EL_C, AZ_C, LENS_C, FW_C = 18.0, 38.0, 100.0, 0.30   # hero camera: deg above the face plane / from the face normal
RING_SP, RING_P = 0.022, 3.0   # ring spacing (m) and sharpness (power of the raised cosine; 11 Nov: 8, read as bands)
RING_PH = 0.004          # m: ring phase
RING0 = 0.028            # m: no rings inside this radius (the ball's own patch)
RING_G = 8.0
RING_G_PACE = 3.0        # C Pace: the rings on the black 12K (8 read as bold stripes)
WALL_BP = 4.0            # B Pace: a glossy-only card at the crown wall's mirror direction (its black 12K read as a void)
BALL_KEY = 30.0          # a soft key on the ball alone
FELT_C = (0.45, 0.95, 0.0)      # e2e-c (2026-11-14): a true optic yellow (the official padel ball felt): K17's hue, brighter
                                # (11 Nov's (0.80, 0.95, 0.06) read olive / cream under AgX)
# e2e-c (cloud REQUEST 2026-11-14T09:00Z, owner chose C for the landing page's 'Edge to edge.'): the one-racket canon re-render
PHONE = 0.0              # 1: the 2160x3840 phone frame, reframed round the ball (its own render, not a crop of the wide)
FW_CP, TX_CP = 0.17, 0.012   # phone close-up: the frame width at the target (m); the target this far toward the face
FIT_PT, FIT_PB, FIT_PS = 0.07, 0.07, 0.05   # phone wide: air at the top, bottom, sides (fractions of the frame)
EXPO_C, EXPO_P = 1.0, 1.0    # C: the studio image x this (Command, Pace): the face mean matched to K01-full
BALL_EXPO = 1.6          # C: the ball's own exposure (AOV e2e_ball), apart from the racket's
WB_C = (0.97, 1.0, 1.06)  # C: a white balance on the image (linear gains): the face's neutral grey as K01-full's (the K11
                          # studio read a little warm here: b/g 0.965 against K01's 0.99)
RING_LIGHT = 1.0         # 1: the rings are soft warm light ON the face: the studio image x (1 + RING_K x ring) in a warm
                         # tint plus a little warm light on the face's albedo, so the weave reads through them (11 Nov:
                         # an additive emission, opaque copper bands); 0: the 11 Nov rings
RING_K, RING_K_PACE = 2.2, 1.2   # the ring light's gain on the studio image (Command, Pace)
RING_A, RING_A_PACE = 0.3, 0.3   # the ring light on the albedo (Command, Pace)
RING_TINT, RING_TINT_PACE = 0.55, 0.4   # how warm the ring light is (0 white .. 1 the full 2700 K colour)
RING_P_PACE = 4.0        # Pace's rings a touch narrower (the black 12K: broad rings read as brown bands)
SEAM_CLEAR = 0.0012      # m: the felt's fibres kept this far off the seam's edge (11 Nov: 0.2 mm, the fibres blurred it)
SEAM_COL = (0.80, 0.80, 0.78)   # the seam's rubber, a clean light grey

EOPT = {}


def eparse():
    argv = sys.argv
    for i, a in enumerate(argv):
        if a == "--eset" and i + 1 < len(argv):
            for kv in argv[i + 1].split(","):
                k, v = kv.split("=")
                globals()[k.strip()] = float(v)
        if a == "--concept" and i + 1 < len(argv):
            EOPT["concept"] = argv[i + 1]
        if a == "--feel" and i + 1 < len(argv):
            EOPT["feel"] = argv[i + 1]


# ------------------------------------------------------------------ the face mask (distance to the flat face's boundary)
FACE_Y0 = -0.149        # the face part's lower end (the neck's top): the flood fades into the neck there, no line
NECK_RUN = 0.05         # the distance field runs on this far below FACE_Y0, so that cut is never a boundary


def face_field(y0):
    """The flat face (the outline 1 mm in, minus the throat 1 mm out) above y0."""
    from shapely.geometry import Polygon, box
    O = Polygon(C.outline_canon()).buffer(0)
    T = Polygon(L10.throat_loop()).buffer(C.FACE_INSET, join_style="round", quad_segs=32)
    return O.buffer(-C.FACE_INSET, join_style="round", quad_segs=32).difference(T).intersection(box(-1, y0, 1, 1))


def face_mask():
    """A float image in model x, y: R = e2e_r, G = inside. Returns (image, bounds)."""
    from PIL import Image, ImageDraw
    F = face_field(FACE_Y0)
    D = face_field(FACE_Y0 - NECK_RUN)          # the distance field's region (the neck cut is not an edge)
    x0, y0, x1, y1 = F.bounds
    pad = 0.002
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    W, H = int(round((x1 - x0) / MASK_PX)), int(round((y1 - y0) / MASK_PX))

    def raster(g):
        im = Image.new("L", (W, H), 0)
        dr = ImageDraw.Draw(im)
        geoms = [g] if g.geom_type == "Polygon" else list(g.geoms)
        for p in geoms:
            dr.polygon([((x - x0) / MASK_PX, (y1 - y) / MASK_PX) for x, y in p.exterior.coords], fill=255)
            for h in p.interiors:
                dr.polygon([((x - x0) / MASK_PX, (y1 - y) / MASK_PX) for x, y in h.coords], fill=0)
        return np.asarray(im, dtype=np.float32) / 255.0

    # inside, 4x supersampled for a clean edge
    acc = np.zeros((H, W), np.float32)
    d, n = 0.0, 0
    while True:
        g = D.buffer(-d, join_style="round", quad_segs=16) if d > 0 else D
        if g.is_empty or g.area < 1e-8:
            break
        acc += raster(g)
        d += MASK_STEP
        n += 1
    dist = acc * MASK_STEP                       # ~ distance to the boundary (m)
    dmax = max(dist.max(), 1e-6)
    inside = raster(F)
    r = np.where(inside > 0, 1.0 - dist / dmax, 1.0)
    px = np.zeros((H, W, 4), np.float32)
    px[..., 0] = r
    px[..., 1] = inside
    px[..., 3] = 1.0
    im = bpy.data.images.new("E2E_mask", W, H, alpha=True, float_buffer=True)
    im.colorspace_settings.name = "Non-Color"
    im.pixels.foreach_set(np.ascontiguousarray(px[::-1]).ravel())
    im.pack()
    print("e2e mask", W, H, "levels", n, "dmax mm", round(dmax * 1000, 1))
    return im, (x0, y0, x1, y1)


def add_flood(face, img, bounds):
    """The flood: an emission under the face's clear coat (the canon's Principled emission sits below the coat), in group
    'flood'; the mask's channels go out as the AOVs e2e_r, e2e_in."""
    m = face.material_slots[0].material.copy()
    m.name = "E2E_FaceFlood"
    face.material_slots[0].link = "OBJECT"
    face.material_slots[0].material = m
    m.cycles.emission_sampling = "NONE"      # seen, not a lamp
    nb = KL7.NB(m)
    nodes = m.node_tree.nodes
    pace = any(n.type == "BSDF_PRINCIPLED" and n.inputs["Coat Weight"].is_linked for n in nodes) and not any(
        n.type == "TEX_IMAGE" and n.image and os.path.basename(n.image.filepath) == "height16.png" for n in nodes)
    bs = [n for n in nodes if n.type == "BSDF_PRINCIPLED"]
    if pace:
        b = [n for n in bs if n.inputs["Coat Weight"].is_linked] or bs
        mods = [n for n in nodes if n.type == "MATH" and n.operation == "LESS_THAN" and n.inputs[0].is_linked
                and n.inputs[0].links[0].from_node.type == "MATH" and n.inputs[0].links[0].from_node.operation == "MODULO"]
        mod = nb.math("MULTIPLY_ADD", mods[0].outputs[0], P_TAPE_K[1], P_TAPE_K[0]) if mods else None
    else:
        b = [n for n in bs if n.inputs["Anisotropic Rotation"].is_linked] or bs
        hn = [n for n in nodes if n.type == "TEX_IMAGE" and n.image and os.path.basename(n.image.filepath) == "height16.png"]
        mod = nb.math("MULTIPLY_ADD", nb.smooth(hn[0].outputs["Color"], 0.45, 0.95), TOW_K[1], TOW_K[0]) if hn else None
    x0, y0, x1, y1 = bounds
    x, y, _ = nb.coords("Object")
    cv = nodes.new("ShaderNodeCombineXYZ")
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", x, x0), x1 - x0), cv.inputs[0])
    nb.l.new(nb.math("DIVIDE", nb.math("SUBTRACT", y, y0), y1 - y0), cv.inputs[1])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    tex.extension = "CLIP"
    nb.l.new(cv.outputs[0], tex.inputs["Vector"])
    sep = nodes.new("ShaderNodeSeparateColor")
    nb.l.new(tex.outputs["Color"], sep.inputs["Color"])
    e = sep.outputs[1] if mod is None else nb.math("MULTIPLY", sep.outputs[1], mod)
    v1 = nodes.new("ShaderNodeVectorMath")
    v1.operation = "SCALE"
    v1.inputs[0].default_value = KD.kelvin(FLOOD_K)
    nb.l.new(e, v1.inputs["Scale"])
    for bb in b:
        nb.l.new(v1.outputs["Vector"], bb.inputs["Emission Color"])
        bb.inputs["Emission Strength"].default_value = 1.0 / len(b) if len(b) > 1 else 1.0
    for name, s in (("e2e_r", sep.outputs[0]), ("e2e_in", sep.outputs[1])):
        a = nodes.new("ShaderNodeOutputAOV")
        a.aov_name = name
        nb.l.new(s, a.inputs["Value"])
    face.lightgroup = "flood"
    print("e2e flood on", face.name, "pace" if pace else "command", "bsdfs", len(b), "mod", mod is not None)


# ------------------------------------------------------------------ B: the line's emission (on top of the coat)
def add_line_emit(ob, w_in):
    """B: a camera-ray-only warm emission over the whole part (group 'flood'); AOVs e2e_y (model y) and e2e_in (w_in):
    the comp keeps a thin band of it at each stage's y."""
    for i, slot in enumerate(ob.material_slots):
        m0 = slot.material
        if m0 is None:
            continue
        m = m0.copy()
        m.name = m0.name + "_e2eB"
        nt = m.node_tree
        nodes, links = nt.nodes, nt.links
        out = next(n for n in nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        src = out.inputs["Surface"].links[0].from_socket
        nb = KL7.NB(m)
        _, y, _ = nb.coords("Object")
        lp = nodes.new("ShaderNodeLightPath")
        em = nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*KD.kelvin(FLOOD_K), 1)
        links.new(lp.outputs["Is Camera Ray"], em.inputs["Strength"])
        ad = nodes.new("ShaderNodeAddShader")
        links.new(src, ad.inputs[0])
        links.new(em.outputs[0], ad.inputs[1])
        links.new(ad.outputs[0], out.inputs["Surface"])
        for name, sock, val in (("e2e_y", y, None), ("e2e_in", None, w_in)):
            a = nodes.new("ShaderNodeOutputAOV")
            a.aov_name = name
            if sock is not None:
                links.new(sock, a.inputs["Value"])
            else:
                a.inputs["Value"].default_value = val
        slot.link = "OBJECT"
        ob.material_slots[i].material = m
    ob.lightgroup = "flood"


def add_dist_aov(face, xi, yi):
    """C: AOV e2e_d = the distance (m, model x y) from the contact point, on the flood material add_flood made."""
    m = face.material_slots[0].material
    nb = KL7.NB(m)
    x, y, _ = nb.coords("Object")
    dx = nb.math("SUBTRACT", x, xi)
    dy = nb.math("SUBTRACT", y, yi)
    d = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", dx, dx), nb.math("MULTIPLY", dy, dy)))
    a = nb.n.new("ShaderNodeOutputAOV")
    a.aov_name = "e2e_d"
    nb.l.new(d, a.inputs["Value"])


def impact_point():
    """C: the contact point (model x, y): IMPACT_IN inside the outline at the head's widest point, on the +x side."""
    pts = np.array(C.outline_canon())
    k = int(np.argmax(pts[:, 0]))
    return float(pts[k, 0] - IMPACT_IN), float(pts[k, 1])


def aim_roll(cam, target, up_world):
    """Aim the camera at target, then roll it about its view axis so up_world lies along the frame's +x."""
    from mathutils import Matrix
    import math
    studio.aim(cam, target)
    bpy.context.view_layer.update()
    R = cam.matrix_world.to_3x3()
    ux, uy = up_world.dot(R.col[0]), up_world.dot(R.col[1])
    a = math.atan2(uy, ux)
    cam.matrix_world = cam.matrix_world @ Matrix.Rotation(a, 4, "Z")
    bpy.context.view_layer.update()


# ------------------------------------------------------------------ hooks into K11-dark
_orig_build = KD.build_rackets
_orig_frame = KD.frame_camera
ROOTS = []


def _aovs(names):
    vl = bpy.context.scene.view_layers[0]
    for name in names:
        a = vl.aovs.add()
        a.name = name
        a.type = "VALUE"


def build_rackets(o):
    roots = _orig_build(o)
    ROOTS[:] = roots
    cpt = EOPT.get("concept", "a")
    if cpt in ("a", "c"):
        img, bounds = face_mask()
        for r in roots:
            add_flood(C.parts(r)["face"], img, bounds)
        names = ["e2e_r", "e2e_in"]
        if cpt == "c":
            xi, yi = impact_point()
            for r in roots:
                add_dist_aov(C.parts(r)["face"], xi, yi)
            names += ["e2e_d", "e2e_ball"]
        _aovs(names)
    elif cpt == "b":
        for r in roots:
            P = C.parts(r)
            for k, w in (("face", 1.0), ("rim", 1.0), ("wall", WALL_B)):
                if k in P:
                    add_line_emit(P[k], w)
        _aovs(["e2e_y", "e2e_in"])
    return roots


def frame_camera(sc, cam, pts, aim, dirn):
    import math
    cpt = EOPT.get("concept", "a")
    r = ROOTS[0]
    c, up, across, nrm = KD.racket_frame(r)
    if cpt == "b":
        T = c + up * TY_B
        el = math.radians(EL_B)
        d = FW_B * LENS_B / 36.0 + BACK_B
        cam.data.lens = LENS_B
        cam.data.sensor_fit = "HORIZONTAL"
        cam.data.sensor_width = 36.0
        cam.data.shift_x = cam.data.shift_y = 0.0
        for sd in (1.0, -1.0):
            # from beyond the crown, low over the face, looking along it toward the throat: a line across the face
            # runs left-right across the frame and bends down over the radius at both side edges; the face's
            # normal up the frame
            cam.location = T + (up * math.cos(el) + nrm * math.sin(el)) * d
            aim_roll(cam, T, across * sd)
            if nrm.dot(cam.matrix_world.to_3x3().col[1]) > 0:
                break
        cam.data.dof.use_dof = FSTOP_B > 0
        cam.data.dof.aperture_fstop = max(FSTOP_B, 1.0)
        cam.data.dof.focus_distance = d
        if EOPT.get("feel") == "pace" and WALL_BP > 0:
            # the crown wall faces the camera: a soft card where its (outward, ~up) normal mirrors the view
            Wc = c + up * 0.15
            v = (cam.location - Wc).normalized()
            mir = (2 * v.dot(up) * up - v).normalized()
            wl = studio.area_light("lg_e2e_wall", tuple(Wc + mir * 0.8), 0.6, WALL_BP, color=KD.kelvin(6500.0),
                                   size_y=0.3, target=tuple(Wc))
            wl.visible_diffuse = False
            wl.lightgroup = "fill"
            P_ = C.parts(r)
            KL7.link_receivers(wl, [P_[k] for k in ("wall", "rim") if k in P_], "recv_e2e_wall")
        return d
    if cpt == "c":
        xi, yi = impact_point()
        M = r.matrix_world
        P = M @ Vector((xi, yi, C.ZT))
        if VIEW_C >= 0.5:
            from mathutils import Matrix
            el, az = math.radians(EL_C), math.radians(AZ_C)
            v = (nrm * math.cos(az) + across * math.sin(az))
            v = (v * math.cos(el) + up * math.sin(el)).normalized()
            d = (FW_CP if PHONE >= 0.5 else FW_C) * LENS_C / 36.0
            T = P - across * (TX_CP if PHONE >= 0.5 else 0.035)
            cam.data.lens = LENS_C
            cam.data.sensor_fit = "HORIZONTAL"
            cam.data.sensor_width = 36.0
            cam.data.shift_x = cam.data.shift_y = 0.0
            cam.location = T + v * d
            studio.aim(cam, T)
            bpy.context.view_layer.update()
        elif PHONE >= 0.5:
            # the whole racket and the ball in the portrait frame (the card crop is the whole frame here)
            bc = P + nrm * 0.027
            bp = [bc + v_ * 0.034 for v_ in (across, -across, up, -up, nrm)]
            keep = (KD.CARD_X0, KD.CARD_W, KD.FIT_TOP, KD.FIT_BOT, KD.FIT_SIDE)
            KD.CARD_X0, KD.CARD_W, KD.FIT_TOP, KD.FIT_BOT, KD.FIT_SIDE = 0.0, 1.0, FIT_PT, FIT_PB, FIT_PS
            d = _orig_frame(sc, cam, list(pts) + bp, aim, dirn)
            KD.CARD_X0, KD.CARD_W, KD.FIT_TOP, KD.FIT_BOT, KD.FIT_SIDE = keep
            # K11's shift assumes a landscape frame (shift in frame widths); in portrait the shift unit is the height
            from bpy_extras.object_utils import world_to_camera_view as w2c
            cd = cam.data
            cd.shift_x = cd.shift_y = 0.0
            bpy.context.view_layer.update()
            uv = np.array([w2c(sc, cam, p_)[:2] for p_ in list(pts) + bp])
            asp = sc.render.resolution_y / sc.render.resolution_x
            cd.shift_x = ((uv[:, 0].min() + uv[:, 0].max()) / 2 - 0.5) / asp
            cd.shift_y = (uv[:, 1].min() + uv[:, 1].max()) / 2 - (FIT_PB + (1 - FIT_PT - FIT_PB) / 2)
            bpy.context.view_layer.update()
        else:
            d = _orig_frame(sc, cam, pts, aim, dirn)
        add_ball(r, P, cam)
        return d
    if cpt == "a":
        head = [p_ for p_ in pts if (p_ - c).dot(up) > -0.165]
        ft = (KD.FIT_TOP, KD.FIT_BOT)
        KD.FIT_TOP = KD.FIT_BOT = HEAD_FIT
        lo = Vector((min(p_.x for p_ in head), min(p_.y for p_ in head), min(p_.z for p_ in head)))
        hi = Vector((max(p_.x for p_ in head), max(p_.y for p_ in head), max(p_.z for p_ in head)))
        d = _orig_frame(sc, cam, head, (lo + hi) / 2, dirn)
        KD.FIT_TOP, KD.FIT_BOT = ft
        return d
    return _orig_frame(sc, cam, pts, aim, dirn)


def add_ball(r, P, cam):
    """C: K17's padel ball (felt, seam, fibres), pressed onto the face at P (its contact patch flattened on the face)."""
    from mathutils import Matrix
    spec = importlib.util.spec_from_file_location("K17r", os.path.join(HERE, "K17-roughness.py"))
    K17 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(K17)
    p = dict(K17.DEFAULTS)
    p["COMPRESS"] = 0.006           # the instant of the strike: pressed harder than K17's slice
    p["FELT"] = FELT_C
    p["FIB_COL"] = FELT_C
    p["SEAM_CLEAR"] = SEAM_CLEAR
    p["SEAM_COL"] = SEAM_COL
    Mw = Matrix.Translation(P) @ r.matrix_world.to_3x3().normalized().to_4x4()
    cam_local = Mw.inverted() @ cam.location
    centre = Vector((0.0, 0.0, p["BALL_R"] - p["COMPRESS"]))
    pivot, broot, bobs, _ = K17.build_ball(p, centre, cam_local, np.random.default_rng(11))
    bpy.context.view_layer.update()
    pivot.matrix_world = Mw @ pivot.matrix_world
    bpy.context.view_layer.update()
    c, up, across, nrm = KD.racket_frame(r)
    kl = studio.area_light("lg_ballkey", tuple(P + (nrm * 0.6 - across * 0.3 + up * 0.4)), 0.4, BALL_KEY,
                           color=KD.kelvin(5600.0), target=tuple(P + nrm * 0.03))
    kl.lightgroup = "key"
    KL7.link_receivers(kl, bobs, "recv_ballkey")
    # AOV e2e_ball = 1 on the ball (felt, seam, fibres): the comp gives it its own exposure (BALL_EXPO), so the racket's
    # exposure (EXPO_C / EXPO_P, matched to K01) leaves the ball's optic yellow as it is
    for ob in bobs:
        for slot in ob.material_slots:
            mt = slot.material
            if mt is None or any(n.type == "OUTPUT_AOV" and n.aov_name == "e2e_ball" for n in mt.node_tree.nodes):
                continue
            a = mt.node_tree.nodes.new("ShaderNodeOutputAOV")
            a.aov_name = "e2e_ball"
            a.inputs["Value"].default_value = 1.0
    print("e2e ball at", tuple(round(x, 4) for x in P))


def build_comp(sc, src, o, out_stem):
    tr = sc.node_tree
    rl = next(n for n in tr.nodes if n.type == "R_LAYERS")
    den = {}
    for g in KD.GROUPS:
        dn = tr.nodes.new("CompositorNodeDenoise")
        dn.prefilter = "ACCURATE"
        dn.use_hdr = True
        tr.links.new(src[g], dn.inputs["Image"])
        tr.links.new(src["normal"], dn.inputs["Normal"])
        tr.links.new(src["albedo"], dn.inputs["Albedo"])
        den[g] = dn.outputs["Image"]

    def mix(op, a, b, fac=1.0):
        n = tr.nodes.new("CompositorNodeMixRGB")
        n.blend_type = op
        n.inputs["Fac"].default_value = fac
        for i, v in ((1, a), (2, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = (v, v, v, 1)
            else:
                tr.links.new(v, n.inputs[i])
        return n.outputs["Image"]

    def m(op, a, b=None, clamp=False):
        n = tr.nodes.new("CompositorNodeMath")
        n.operation = op
        n.use_clamp = clamp
        for i, v in ((0, a), (1, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                tr.links.new(v, n.inputs[i])
        return n.outputs[0]

    def glow(img):
        """img + GLOW_K x its fog glow (threshold GLOW_THR)."""
        if GLOW_K <= 0:
            return img
        g = tr.nodes.new("CompositorNodeGlare")
        g.glare_type = "FOG_GLOW"
        g.quality = "HIGH"
        g.mix = 1.0
        g.threshold = GLOW_THR
        g.size = int(GLOW_SIZE)
        tr.links.new(img, g.inputs["Image"])
        return mix("ADD", img, mix("MULTIPLY", g.outputs["Image"], GLOW_K))

    base = mix("ADD", mix("ADD", mix("ADD", den["key"], den["sheen"]), den["fill"]), den["env"])
    full = mix("ADD", base, den["glow"])
    outs = {"base": base, "full": full}
    cpt = EOPT.get("concept", "a")
    if "flood" in den and cpt == "b":
        y, inside = rl.outputs["e2e_y"], rl.outputs["e2e_in"]
        lit = mix("ADD", mix("MULTIPLY", base, STUDIO_B), den["glow"])
        fl = mix("MULTIPLY", den["flood"], LINE_GB)
        for k in range(6):
            ys = YS_B[0] + (YS_B[1] - YS_B[0]) * k / 5.0
            band = m("EXPONENT", m("MULTIPLY", m("POWER", m("DIVIDE", m("SUBTRACT", y, ys), BW_B), 2.0), -1.0))
            # the trail: behind the line (y < ys), exp decay
            tr_ = m("MULTIPLY", m("EXPONENT", m("MULTIPLY", m("MAXIMUM", m("SUBTRACT", ys, y), 0.0), -1.0 / TRAIL_L)),
                    m("LESS_THAN", y, ys))
            k_ = m("MULTIPLY", m("ADD", band, m("MULTIPLY", tr_, TRAIL_B)), inside)
            outs["s%d" % (k + 1)] = mix("ADD", lit, glow(mix("MULTIPLY", fl, k_)))
    if "flood" in den and cpt == "c":
        dd, inside = rl.outputs["e2e_d"], rl.outputs["e2e_in"]
        pc = EOPT.get("feel") == "pace"
        ex = EXPO_P if pc else EXPO_C
        # the exposure per pixel: ex on the racket and field, BALL_EXPO on the ball
        ev = m("ADD", ex, m("MULTIPLY", rl.outputs["e2e_ball"], BALL_EXPO - ex))
        def wb(img):
            n = tr.nodes.new("CompositorNodeMixRGB")
            n.blend_type = "MULTIPLY"
            n.inputs["Fac"].default_value = 1.0
            tr.links.new(img, n.inputs[1])
            n.inputs[2].default_value = (*WB_C, 1)
            return n.outputs["Image"]
        lit = mix("MULTIPLY", wb(mix("ADD", mix("MULTIPLY", base, STUDIO_C), den["glow"])), ev)
        outs["base"] = mix("MULTIPLY", wb(mix("MULTIPLY", base, STUDIO_C)), ev)
        outs["full"] = lit
        outs["mask"] = inside                      # the flat face (no holes, no ball): the face-mean check, not a master
        import math as _m
        ph = m("MULTIPLY", m("SUBTRACT", dd, RING_PH), 2.0 * _m.pi / RING_SP)
        ring = m("POWER", m("ADD", m("MULTIPLY", m("COSINE", ph), 0.5), 0.5), RING_P_PACE if pc else RING_P)
        k_ = m("MULTIPLY", m("MULTIPLY", ring, m("GREATER_THAN", dd, RING0)), inside)
        if RING_LIGHT >= 0.5:
            kv = KD.kelvin(FLOOD_K)
            tcol = [1.0 - (RING_TINT_PACE if pc else RING_TINT) * (1.0 - x) for x in kv]

            def tint(img):
                n = tr.nodes.new("CompositorNodeMixRGB")
                n.blend_type = "MULTIPLY"
                n.inputs["Fac"].default_value = 1.0
                tr.links.new(img, n.inputs[1])
                n.inputs[2].default_value = (*tcol, 1)
                return n.outputs["Image"]
            on_img = mix("MULTIPLY", mix("MULTIPLY", tint(lit), k_), RING_K_PACE if pc else RING_K)
            on_alb = mix("MULTIPLY", mix("MULTIPLY", tint(src["albedo"]), k_), (RING_A_PACE if pc else RING_A) * ex)
            outs["rings"] = mix("ADD", lit, mix("ADD", on_img, on_alb))
        else:
            fl = mix("MULTIPLY", den["flood"], RING_G_PACE if pc else RING_G)
            outs["rings"] = mix("ADD", lit, glow(mix("MULTIPLY", fl, k_)))
    if "flood" in den and cpt == "a":
        r, inside = rl.outputs["e2e_r"], rl.outputs["e2e_in"]
        # 10:45Z: a warm light ON the white twill: inside the light the studio image x a 2700 K tint (TINT_A) and
        # IN_K, plus a little of the flood emission; outside the studio x STUDIO_K. The weave reads through it.
        lit = mix("ADD", mix("MULTIPLY", base, STUDIO_K), den["glow"])
        kv = KD.kelvin(FLOOD_K)
        tn = tr.nodes.new("CompositorNodeMixRGB")
        tn.blend_type = "MULTIPLY"
        tn.inputs["Fac"].default_value = 1.0
        tr.links.new(base, tn.inputs[1])
        tn.inputs[2].default_value = (*[IN_K * (1.0 - TINT_A * (1.0 - x)) for x in kv], 1)
        warm = mix("ADD", tn.outputs["Image"], den["glow"])

        def blend(a, b, fac):
            n = tr.nodes.new("CompositorNodeMixRGB")
            n.blend_type = "MIX"
            tr.links.new(fac, n.inputs["Fac"])
            tr.links.new(a, n.inputs[1])
            tr.links.new(b, n.inputs[2])
            return n.outputs["Image"]
        fl = mix("MULTIPLY", den["flood"], FLOOD_G_PACE if EOPT.get("feel") == "pace" else FLOOD_G)
        for s in STAGES:
            tag = "s%03d" % round(s * 100)
            if s <= 0:
                outs[tag] = lit
                continue
            se = s * (1.0 + SOFT)
            mk = m("MULTIPLY", m("ADD", m("DIVIDE", m("SUBTRACT", se, r), SOFT), 0.5, clamp=True), inside)
            band = m("MULTIPLY", m("EXPONENT", m("MULTIPLY", m("POWER", m("DIVIDE", m("SUBTRACT", r, s), FRONT_W), 2.0),
                                                     -1.0)), inside)
            k = m("MULTIPLY", mk, m("ADD", m("MULTIPLY", band, FRONT_K if s < 1.0 else 0.0), 1.0))
            outs[tag] = mix("ADD", blend(lit, warm, mk), glow(mix("MULTIPLY", fl, k)))
        ln = m("MULTIPLY", m("MULTIPLY", m("SUBTRACT", r, 1.0 - LINE_W), 1.0 / LINE_W, clamp=False), inside)
        ln = m("MULTIPLY", m("MINIMUM", m("MAXIMUM", ln, 0.0), 1.0), LINE_G)
        se = 1.0 + SOFT
        k1 = m("MULTIPLY", m("ADD", m("DIVIDE", m("SUBTRACT", se, r), SOFT), 0.5, clamp=True), inside)
        outs["s100-line"] = mix("ADD", blend(lit, warm, k1), glow(mix("MULTIPLY", fl, m("ADD", k1, ln))))
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = os.path.dirname(out_stem)
    fo.format.file_format = "PNG"
    fo.format.color_mode = "RGB"
    fo.format.color_depth = "16"
    fo.file_slots.clear()
    written = []
    for v, sock in outs.items():
        name = os.path.basename(out_stem) + "-" + v
        fo.file_slots.new(name)
        tr.links.new(sock, fo.inputs[name])
        written.append(name)
    comp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(outs["full"], comp.inputs["Image"])
    return written


def main():
    eparse()
    KD.build_rackets = build_rackets
    KD.build_comp = build_comp
    KD.frame_camera = frame_camera
    KD.GROUPS = tuple(KD.GROUPS) + ("flood",)
    KD.C_YAW = KD.YAW = YAW_A
    KD.main()


if __name__ == "__main__":
    main()
