"""K11-dark (2026-11-07, cloud REQUEST k04-language): the edition cards' whole rackets in K04's language.

Owner, 2026-11-07: "The best animated render is still the moulded holes; the worst are the vertical whole rackets in the
First 500 and single edition, especially the white ones; make the whole racket renders look more like the moulded holes
graphic including the animation." K11 (single, pair) was a flat, evenly lit racket on a grey gradient. This shot puts the
canon racket (kq_canon, the full-weave canon: K01's hero weave on every part) in K04's studio:
- near-black seamless field (camera rays only; the world lights nothing),
- one low raking key from the crown side (lg key), so the face falls from a bright highlight to deep shade across its
  width; the white Command face still reads white where it is lit,
- K04's glossy coat: a thin glossy-only strip high over the crown (lg sheen) draws a specular crescent on every hole
  lip and along the edge radius, and a faint weave card (lg sheen) carries the 12K tapes on Pace,
- a sculptural camera: lower and closer with a longer lens, three-quarter, the racket rolled a few degrees, the whole
  racket inside the card crop (4:5, the frame's centre 0.45) with air round it; the pair overlaps in depth, same light,
- TWO variants from ONE render (light groups, K04's build_comp): base = the raking light only; full = base + the warm
  2700 K glow coming up inside the 42 bores and the throat (camera-ray emission in the bore and throat walls, rising
  toward the core, lg glow) and a thin warm line along the edge radius (lg glow), so the site can fade the light up
  while the racket draws back (K04's animation).

Usage (from render/, through the lock):
  flock render.lock $PY shots/K11-dark.py [--feel pace] [--mode single|pair] [--weave command|pace|mix]
        --w 3200 --h 1800 --spp 128 --out k11d/s01
  Writes <out>-base.png, <out>-full.png (16:9 frames), <out>-base_card.png, <out>-full_card.png (the card crop, x 0.275
  w 0.45: 4:5), <out>.exr (the raw light-group passes). KQ_NOGRIP=1: the Naked twin (canon NAKED, no butt flare).
  --set KEY=VALUE[,KEY=VALUE] overrides any upper-case constant. --comp <exr> re-composites with --g_<group> gains.
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
import kqpaths  # noqa: E402,F401

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

import studio  # noqa: E402
import kq_canon as C  # noqa: E402

GROUPS = ("key", "sheen", "fill", "env", "glow")

# ------------------------------------------------------------------ layout (metres, degrees)
HC = 1.0            # head-centre height of the front racket
YAW = 40.0          # face turned toward camera-right
ROLL = -7.0         # in-plane lean (crown toward camera-left)
LENS = 90.0         # longer than K11's 85 (review 15:59Z: 105 made the handle read short and thick)
CAM_EL = -2.0       # camera elevation from the racket's mid (negative: lower, looking slightly up)
CAM_AZ = 0.0
CARD_X0, CARD_W = 0.275, 0.45   # K11's card crop (4:5 at 16:9)
FIT_TOP, FIT_BOT = 0.075, 0.075  # air above and below the racket(s) in the card (fraction of frame height)
FIT_SIDE = 0.06     # air left / right inside the card (fraction of the card width)
# pair: the rear racket behind the front one, along the face normal, shifted across the face and up
P_GAP, P_SHIFT, P_RISE = 0.09, 0.15, 0.03
# ------------------------------------------------------------------ light (W; positions relative to the front racket)
KEY_S = 1600.0       # raking key: a soft spot high at the crown's outer side, near the face plane (grazing)
KEY_DEG, KEY_BLEND, KEY_SIZE = 26.0, 0.65, 0.06
KEY_UP, KEY_SIDE, KEY_OUT = 0.55, -0.42, 0.16   # along the racket's long axis, across it, along the face normal
KEY_AIM_UP, KEY_AIM_SIDE = 0.16, -0.20
SHEEN_S = 500.0     # glossy-only strip SHEEN_EL above the face's mirror direction: lip crescents and the edge radius
SHEEN_EL, SHEEN_D = 48.0, 1.3
SHEEN_LEN, SHEEN_W = 1.6, 0.03
FILL_S = 0.4
HANDLE_S = 160.0    # a glossy-only strip along the handle at the camera's left: a line down the shaft (Naked Pace
                    # otherwise vanishes into the field)
HANDLE_AZ, HANDLE_D = -70.0, 0.9
RIM_S = 0.0         # cool thin back strips behind both sides (review 15:59Z, Pace: the silhouette from crown to the Q)
P_RIM_S = 1100.0
RIM_AZ, RIM_D, RIM_LEN, RIM_W = 150.0, 1.0, 0.9, 0.25
RIM_AZ_R = -165.0   # the right strip's azimuth (0 = -RIM_AZ)
RIM_W_R, RIM_S_R = 0.7, 3000.0   # the right strip wider (the handle's right facets mirror it all the way down)
P_HANDLE_S = 0.0    # Pace: no shaft strip (its line broke at every tape); the back strips draw the handle
WALL_S = 0.0        # Command: a soft diffuse-only card on the camera-left wall and neck (the streaky dark patch)
CMD_WALL_S = 14.0        # weak cool fill from the camera side: the shade stays carbon in shadow, not a void
WEAVE_S = 0.0       # Pace: a soft card near the face's mirror direction for the 12K tapes (glossy only)
P_WEAVE_S = 520.0
WEAVE_UP, WEAVE_SIZE = 15.0, 1.1   # degrees off the mirror direction, size (m)
BG = 0.0032         # the field (linear, camera rays only): near-black
BG_VIG = 0.45       # vignette: the corners fall to (1 - BG_VIG) of the centre
# ------------------------------------------------------------------ glow (lg glow; 2700 K)
GLOW_S = 9.0        # emission strength at the core (camera rays only)
GLOW_LAM = 0.0022   # e-folding depth from the core (m): the bores glow toward the mid-plane
GLOW_CORE = (1.0, 0.66, 0.36)
GLOW_EDGE = (1.0, 0.42, 0.13)
THROAT_GLOW = 0.0   # the throat's wall relative to the bores; 0 since pace-dark-fix (d): seen from K11's side the lit
                    # wall drew a one-sided copper swoosh (both feels), too close to a famous sportswear mark
EDGE_GLOW = 2.2     # the thin warm line along the edge radius (rim emission, grazing-weighted), Pace
CMD_EDGE_GLOW = 16.0  # Command (on white the line needs more to read)
EDGE_POW = 3.0
CLAMP_IND = 4.0
PAIR_SET = 1.0      # 1 = the First 500 pair shows its set number on both throats (canon), 0 = the single's serial
SET_TEXT = "027/500"
GRIP_DARK = 1.0     # 1 = no light reaches the overgrip (canon: neutral black; k04-language-fix 2026-11-07: it read light
                    # grey under the raking key, sheen and strips together); its wrap reads by GRIP_RIM_S alone
GRIP_RIM_S = 0.0    # W: a glossy strip from behind, linked to the overgrip only (preview 2026-11-07: 40 W, 2 x 30 cm); off
                    # since grip-edge (cloud 2026-11-08): it caught the helical wrap's edges as a white staircase
GRIP_RIM_AZ = 150.0  # deg from the camera, about the vertical: behind the handle, a crisp silhouette line
GRIP_SIDE_S = 1.5   # W: a broad dim strip from the side (35 x 70 cm since grip-edge; was 3 W, 2 x 30 cm): the wrap
                    # reads as soft charcoal bands on black, nothing brighter than the face's shade
GRIP_SIDE_AZ = -100.0
GRIP_RIM_W, GRIP_RIM_H = 0.02, 0.30    # m: the strips' size (grip-edge 2026-11-08: a thin strip drew the wrap's edges as a
GRIP_SIDE_W, GRIP_SIDE_H = 0.35, 0.70  # white staircase; broad, dim strips give a soft continuous sheen)
GRIP_DIST = 0.6                        # m from the grip's centre
G_COOL = 0.0
# pace-dark-fix:OK (cloud 09:12Z, grip twins, both feels): a broad soft card (glossy only) reaching the overgrip at low
# strength, so the wrap reads as dark charcoal bands down the whole handle (still black, never grey); GRIP_CAP 1: the
# cap and its Q lit by the grip's lights only (its highlight at the grip's level)
GRIP_FRONT_S, GRIP_FRONT_AZ, GRIP_FRONT_W, GRIP_FRONT_H, GRIP_FRONT_UP = 2.0, 0.0, 0.8, 1.4, 0.0
GRIP_CAP = 1.0
GRIP_CAP_S = 30.0   # W: the cap's own soft card (the front card's place and size, linked to the cap and its Q alone):
                    # satin black anodised metal reflects 4 %, so it needs more than the overgrip to sit at its level
# ------------------------------------------------------------------ Pace in the dark (cloud REQUEST pace-dark-fix, 2026-11-11:
# the owner's iPhone screenshots: Pace read as line art). P_FIX 0 = the 2026-11-07 Pace exactly.
P_FIX = 1.0
P_TAPE_ROUGH, P_TAPE_ANISO, P_COAT_ROUGH = 0.16, 0.60, 0.04   # (b) the tapes' fibre lobe less anisotropic (0.90 ->
                    # 0.60), a touch rougher, the coat a little softer: the 12K reads grey to black with a sheen, not a
                    # mirror-white chessboard
P_GRADE_S = 7.0     # (a) a broad soft graded card (emission, glossy rays only, never seen) along the whole racket: crown
P_GRADE_LOW = 0.25  # end W/m2-ish strength; the handle end relative to it (dimmer toward the Q, never black)
P_GRADE_OFF = 20.0  # deg off the face's mirror direction, about the racket's long axis: the coat never mirrors its edge
P_GRADE_D, P_GRADE_W, P_GRADE_L = 1.2, 1.6, 1.4   # distance (m), width across (smootherstep to 0 at the sides), length
P_GRADE_CY = -0.05  # card centre along the racket's long axis from the head centre (m)
P_RIM_K = 0.22      # (a) the back strips scaled: a soft rim light, not a hairline stroke
P_WEAVE_K = 0.6     # (b) the old weave card scaled (its mirror-white squares)
P_LIP = 1.0         # (c) Pace bores: the glow in a thin band just inside each lip, the bore's depth dark (a copper
LIP_LAM = 0.0008    #     ring round a dark centre, not a copper stud); LIP_LAM its e-folding depth from the face (m)

OPT = {}


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 960, "h": 540, "spp": 32, "out": "k11d/prev", "mode": "single", "feel": "command", "weave": "command"}
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
    if o.get("set"):
        for kv in str(o["set"]).split(","):
            k, v = kv.split("=")
            globals()[k.strip()] = float(v)
    return o


def out_path(name):
    p = name if name.endswith(".png") else name + ".png"
    if not os.path.isabs(p):
        p = os.path.join(studio.OUT, p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def _n(nodes, kind, op=None):
    n = nodes.new(kind)
    if op is not None:
        n.operation = op
    return n


def kelvin(t):
    """Approximate linear sRGB of a blackbody (normalised to max 1)."""
    t = t / 100.0
    r = 255.0 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * ((t - 60) ** -0.0755148492)
    b = 255.0 if t >= 66 else (0.0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    c = [min(max(x, 0.0), 255.0) / 255.0 for x in (r, g, b)]
    c = [x ** 2.2 for x in c]
    m = max(c)
    return tuple(x / m for x in c)


# ------------------------------------------------------------------ emission injected into a canon material
def add_glow(mat, mode, strength):
    """Add camera-ray emission to a copy of a canon material. mode 'depth': warm light rising toward the mid-plane
    (object |z|; the racket's thickness axis), incandescent core -> amber edge; mode 'edge': a thin warm line, weighted
    toward grazing view (Layer Weight facing ** EDGE_POW)."""
    m = mat.copy()
    m.name = mat.name + "_glow_" + mode
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    out = next(n for n in nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    src = out.inputs["Surface"].links[0].from_socket
    lp = nodes.new("ShaderNodeLightPath")
    if mode in ("depth", "lip"):
        tc = nodes.new("ShaderNodeTexCoord")
        sp = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tc.outputs["Object"], sp.inputs["Vector"])
        ab = _n(nodes, "ShaderNodeMath", "ABSOLUTE")
        links.new(sp.outputs["Z"], ab.inputs[0])
        if mode == "lip":   # strongest at the faces (|z| = T2), falling toward the mid-plane
            ab2 = _n(nodes, "ShaderNodeMath", "SUBTRACT")
            ab2.inputs[0].default_value = C.T2
            links.new(ab.outputs[0], ab2.inputs[1])
            ab = ab2
        t = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        t.inputs[1].default_value = -1.0 / (LIP_LAM if mode == "lip" else GLOW_LAM)
        links.new(ab.outputs[0], t.inputs[0])
        ex = _n(nodes, "ShaderNodeMath", "EXPONENT")
        links.new(t.outputs[0], ex.inputs[0])
        fac = ex.outputs[0]
        # tows running down the wall: a stretched noise (never a smooth gradient)
        nz = nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = 4.0
        mp = nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (2600.0, 2600.0, 60.0)
        links.new(tc.outputs["Object"], mp.inputs["Vector"])
        links.new(mp.outputs["Vector"], nz.inputs["Vector"])
        st = _n(nodes, "ShaderNodeMapRange")
        st.inputs["From Min"].default_value = 0.3
        st.inputs["From Max"].default_value = 0.7
        st.inputs["To Min"].default_value = 0.8
        st.inputs["To Max"].default_value = 1.12
        links.new(nz.outputs["Fac"], st.inputs["Value"])
        fm = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        links.new(fac, fm.inputs[0])
        links.new(st.outputs["Result"], fm.inputs[1])
        cpw = _n(nodes, "ShaderNodeMath", "POWER")
        cpw.inputs[1].default_value = 2.0
        links.new(ex.outputs[0], cpw.inputs[0])
        cm = nodes.new("ShaderNodeMixRGB")
        cm.inputs["Color1"].default_value = (*GLOW_EDGE, 1)
        cm.inputs["Color2"].default_value = (*GLOW_CORE, 1)
        links.new(cpw.outputs[0], cm.inputs["Fac"])
        col, val = cm.outputs["Color"], fm.outputs[0]
    else:
        lw = nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        pw = _n(nodes, "ShaderNodeMath", "POWER")
        pw.inputs[1].default_value = EDGE_POW
        links.new(lw.outputs["Facing"], pw.inputs[0])
        rgb = nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = (*kelvin(2700.0), 1)
        col, val = rgb.outputs[0], pw.outputs[0]
    g = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(val, g.inputs[0])
    links.new(lp.outputs["Is Camera Ray"], g.inputs[1])
    g2 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    g2.inputs[1].default_value = strength
    links.new(g.outputs[0], g2.inputs[0])
    em = nodes.new("ShaderNodeEmission")
    links.new(col, em.inputs["Color"])
    links.new(g2.outputs[0], em.inputs["Strength"])
    ad = nodes.new("ShaderNodeAddShader")
    links.new(src, ad.inputs[0])
    links.new(em.outputs[0], ad.inputs[1])
    links.new(ad.outputs[0], out.inputs["Surface"])
    return m


def set_glow(ob, mode, strength):
    for i, slot in enumerate(ob.material_slots):
        m0 = slot.material
        if m0 is not None:
            g = add_glow(m0, mode, strength)
            ob.material_slots[i].link = "OBJECT"
            ob.material_slots[i].material = g
    ob.lightgroup = "glow"


def continuous_coat(ob, y_cut=None):
    """Pace (cloud OK 16:10Z): the per-tape coat changes (the in-band tile flip on coat weight, RIM_FLIP on coat
    roughness) drew the back strips' lines on the handle and the neck as dashes (read as stitching). On a copy of each
    material the Coat Weight / Coat Roughness links are blended to their constant values: everywhere (y_cut None: the
    neck, the Naked butt) or below model y = y_cut (the edge radius below the head; the head's edge keeps its break)."""
    for i, slot in enumerate(ob.material_slots):
        m0 = slot.material
        if m0 is None:
            continue
        m = m0.copy()
        m.name = m0.name + "_cont"
        nt = m.node_tree
        nodes, links = nt.nodes, nt.links
        mask = None
        if y_cut is not None:
            tc = nodes.new("ShaderNodeTexCoord")
            sp = nodes.new("ShaderNodeSeparateXYZ")
            links.new(tc.outputs["Object"], sp.inputs["Vector"])
            mr = _n(nodes, "ShaderNodeMapRange")
            mr.interpolation_type = "SMOOTHSTEP"
            mr.inputs["From Min"].default_value = y_cut
            mr.inputs["From Max"].default_value = y_cut - 0.012
            mr.inputs["To Min"].default_value = 0.0
            mr.inputs["To Max"].default_value = 1.0
            links.new(sp.outputs["Y"], mr.inputs["Value"])
            mask = mr.outputs["Result"]
        for b in [n for n in nodes if n.type == "BSDF_PRINCIPLED"]:
            for name in ("Coat Weight", "Coat Roughness"):
                inp = b.inputs[name]
                if not inp.links:
                    continue
                src = inp.links[0].from_socket
                const = inp.default_value if name == "Coat Roughness" else 1.0
                if mask is None:
                    links.remove(inp.links[0])
                    inp.default_value = const
                    continue
                mx = nodes.new("ShaderNodeMix")
                mx.data_type = "FLOAT"
                links.new(mask, mx.inputs["Factor"])
                links.new(src, mx.inputs["A"])
                mx.inputs["B"].default_value = const
                links.new(mx.outputs["Result"], inp)
        ob.material_slots[i].link = "OBJECT"
        ob.material_slots[i].material = m


# ------------------------------------------------------------------ rig
def racket_frame(root):
    """World axes of a posed racket: centre (head centre), up (long axis, toward the crown), across, normal (front)."""
    M = root.matrix_world
    c = M.translation.copy()
    up = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
    across = (M.to_3x3() @ Vector((1, 0, 0))).normalized()
    nrm = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
    return c, up, across, nrm


def pace_opts(feel):
    """pace-dark-fix (b): the Pace tapes' material overrides (None: the canon's)."""
    if feel != "pace" or P_FIX <= 0:
        return None
    return {"rough": P_TAPE_ROUGH, "aniso": P_TAPE_ANISO, "coat_rough": P_COAT_ROUGH}


def build_rackets(o):
    feel = "pace" if o["feel"] == "pace" else "command"
    roots = []
    if o["mode"] == "pair":
        w = o.get("weave", "command")
        feels = {"command": ("command", "command"), "pace": ("pace", "pace"), "mix": ("command", "pace")}[w]
        # canon: a First 500 set carries its set number on BOTH throats (k04-language-fix, cloud 21:51Z); the
        # command / pace mix is not a set and keeps the single's serial
        sn = SET_TEXT if (w in ("command", "pace") and PAIR_SET > 0) else C.SERIAL
        r0, _ = C.build_racket("KQ_F", feel=feels[0], serial=sn, mat_opts=pace_opts(feels[0]))
        r1, _ = C.build_racket("KQ_R", feel=feels[1], serial=sn, mat_opts=pace_opts(feels[1]))
        roots = [r0, r1]
    else:
        r0, _ = C.build_racket("KQ_F", feel=feel, serial=C.SERIAL, mat_opts=pace_opts(feel))
        roots = [r0]
    C.pose(roots[0], (0.0, 0.0, HC), yaw_deg=YAW, roll_deg=ROLL, tilt_deg=90.0)
    if len(roots) > 1:
        bpy.context.view_layer.update()
        c, up, across, nrm = racket_frame(roots[0])
        loc = c - nrm * P_GAP + across * P_SHIFT + up * P_RISE
        C.pose(roots[1], tuple(loc), yaw_deg=YAW, roll_deg=ROLL, tilt_deg=90.0)
    bpy.context.view_layer.update()
    return roots


def sample_points(roots, every=7):
    pts = []
    for r in roots:
        for k, ob in C.parts(r).items():
            if k in ("capmark", "etchR", "etchL") or ob.hide_render:
                continue
            M = ob.matrix_world
            vs = ob.data.vertices
            for i in range(0, len(vs), every):
                pts.append(M @ vs[i].co)
    return pts


def frame_camera(sc, cam, pts, aim, dirn):
    """Distance and shift so the racket(s) fit the card crop with FIT_* air: the camera looks along -dirn at aim."""
    cd = cam.data
    asp = sc.render.resolution_y / sc.render.resolution_x
    d = 3.0
    for _ in range(6):
        cam.location = aim + dirn * d
        studio.aim(cam, aim)
        cd.shift_x = cd.shift_y = 0.0
        bpy.context.view_layer.update()
        uv = np.array([world_to_camera_view(sc, cam, p)[:2] for p in pts])
        u0, u1 = uv[:, 0].min(), uv[:, 0].max()
        v0, v1 = uv[:, 1].min(), uv[:, 1].max()
        hv = 1.0 - FIT_TOP - FIT_BOT
        hu = CARD_W * (1.0 - 2 * FIT_SIDE)
        s = max((v1 - v0) / hv, (u1 - u0) / hu)
        d *= s
    cam.location = aim + dirn * d
    studio.aim(cam, aim)
    bpy.context.view_layer.update()
    uv = np.array([world_to_camera_view(sc, cam, p)[:2] for p in pts])
    u0, u1 = uv[:, 0].min(), uv[:, 0].max()
    v0, v1 = uv[:, 1].min(), uv[:, 1].max()
    # shift (fractions of the frame's larger side = width): centre the bounding box in the card / between the fits
    cd.shift_x = ((u0 + u1) / 2 - 0.5)
    cd.shift_y = ((v0 + v1) / 2 - (FIT_BOT + (1 - FIT_TOP - FIT_BOT) / 2)) * asp
    bpy.context.view_layer.update()
    return d


def world_field(sc):
    """Near-black seamless field for camera rays (a soft vignette), nothing for the light it casts."""
    w = sc.world
    nt = w.node_tree
    nodes, links = nt.nodes, nt.links
    bg = nodes["Background"]
    bg.inputs["Strength"].default_value = 1.0
    lp = nodes.new("ShaderNodeLightPath")
    tc = nodes.new("ShaderNodeTexCoord")
    sp = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Window"], sp.inputs["Vector"])
    dx = _n(nodes, "ShaderNodeMath", "SUBTRACT")
    dx.inputs[1].default_value = 0.5
    links.new(sp.outputs["X"], dx.inputs[0])
    dy = _n(nodes, "ShaderNodeMath", "SUBTRACT")
    dy.inputs[1].default_value = 0.45
    links.new(sp.outputs["Y"], dy.inputs[0])
    cmb = nodes.new("ShaderNodeCombineXYZ")
    links.new(dx.outputs[0], cmb.inputs["X"])
    links.new(dy.outputs[0], cmb.inputs["Y"])
    ln = _n(nodes, "ShaderNodeVectorMath", "LENGTH")
    links.new(cmb.outputs[0], ln.inputs[0])
    vg = _n(nodes, "ShaderNodeMapRange")
    vg.interpolation_type = "SMOOTHSTEP"
    vg.inputs["From Min"].default_value = 0.15
    vg.inputs["From Max"].default_value = 0.75
    vg.inputs["To Min"].default_value = BG
    vg.inputs["To Max"].default_value = BG * (1.0 - BG_VIG)
    links.new(ln.outputs[0], vg.inputs["Value"])
    m = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(vg.outputs["Result"], m.inputs[0])
    links.new(lp.outputs["Is Camera Ray"], m.inputs[1])
    cc = nodes.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        links.new(m.outputs[0], cc.inputs[k])
    links.new(cc.outputs[0], bg.inputs["Color"])
    w.lightgroup = "env"


def lights(roots, o):
    # per-feel lights are linked to that feel's rackets only (the pair's command-pace mix gets both)
    pace_r = [r for r in roots if r.get("kq_feel") == "pace"]
    cmd_r = [r for r in roots if r.get("kq_feel") != "pace"]
    pace = bool(pace_r)
    c, up, across, nrm = racket_frame(roots[0])
    recv = []
    for r in roots:
        recv += C.objs(r, "all")
    cam = bpy.context.scene.camera
    v = (cam.location - c).normalized()
    mirror = (2 * v.dot(nrm) * nrm - v).normalized()     # the face's mirror direction (what the lacquer reflects)
    from mathutils import Matrix
    ax_up = mirror.cross(up).normalized()                 # rotating about it moves a direction toward the crown
    # key: low, raking, from the crown side: a soft spot high at the crown's outer side, near the face plane, its cone
    # edge crossing the head so the face falls from a bright highlight to deep shade across its width
    kl = c + up * KEY_UP + across * KEY_SIDE + nrm * KEY_OUT
    key = studio.spot_light("lg_key", tuple(kl), KEY_S, KEY_DEG, blend=KEY_BLEND, color=kelvin(5600.0),
                            target=tuple(c + up * KEY_AIM_UP + across * KEY_AIM_SIDE), radius=KEY_SIZE)
    key.lightgroup = "key"
    # sheen: a thin glossy-only strip SHEEN_EL degrees above the face's mirror direction: the face never mirrors it,
    # the lip of every hole (its upper side) and the edge radius at the crown catch it as a crescent / a line
    sd = (Matrix.Rotation(math.radians(SHEEN_EL), 3, ax_up) @ mirror).normalized()
    sh = studio.area_light("lg_sheen", tuple(c + sd * SHEEN_D), SHEEN_LEN, SHEEN_S, color=kelvin(6200.0),
                           size_y=SHEEN_W, target=tuple(c))
    # the strip's long side runs across the racket: roll the light about its own axis so local X follows `across`
    lx = sh.matrix_world.to_3x3() @ Vector((1, 0, 0))
    ang = lx.angle(across)
    sh.rotation_euler.rotate(Matrix.Rotation(ang if lx.cross(across).dot(-sd) >= 0 else -ang, 3, -sd).to_euler())
    sh.visible_diffuse = False
    sh.visible_transmission = False
    sh.visible_volume_scatter = False
    sh.lightgroup = "sheen"
    import k789_lib as KL7
    hs_ = HANDLE_S if cmd_r else P_HANDLE_S
    if hs_ > 0:
        hc = c - up * 0.24                                   # the handle's middle (head centre - 240 mm)
        vc = (cam.location - hc)
        vc.z = 0.0
        vc.normalize()
        hd = (Matrix.Rotation(math.radians(HANDLE_AZ), 3, Vector((0, 0, 1))) @ vc).normalized()
        hl = studio.area_light("lg_handle", tuple(hc + hd * HANDLE_D), 0.04, hs_, color=kelvin(6200.0),
                               size_y=0.32, target=tuple(hc))
        ly = hl.matrix_world.to_3x3() @ Vector((0, 1, 0))
        ang = ly.angle(up)
        hl.rotation_euler.rotate(Matrix.Rotation(ang if ly.cross(up).dot(-hd) >= 0 else -ang, 3, -hd).to_euler())
        hl.visible_diffuse = False
        hl.lightgroup = "sheen"
        if cmd_r and pace_r:
            KL7.link_receivers(hl, [ob_ for r in cmd_r for ob_ in C.objs(r, "all")], "recv_handle")
    rs = P_RIM_S if pace else RIM_S
    if rs > 0:
        # cool thin strips behind the racket, one each side: the edge radius, the neck and both sides of the handle
        # catch them at grazing, so the black racket's whole silhouette reads against the field (glossy only)
        vc = (cam.location - c)
        vc.z = 0.0
        vc.normalize()
        mid = c - up * 0.10
        for sgn, nm in ((1, "L"), (-1, "R")):
            az_ = sgn * RIM_AZ if (sgn > 0 or RIM_AZ_R == 0) else RIM_AZ_R
            rd = (Matrix.Rotation(math.radians(az_), 3, Vector((0, 0, 1))) @ vc).normalized()
            wr_ = RIM_W_R if (sgn < 0 and RIM_W_R > 0) else RIM_W
            rs_ = RIM_S_R if (sgn < 0 and RIM_S_R > 0) else rs
            if pace and P_FIX > 0:
                rs_ *= P_RIM_K
            rl_ = studio.area_light("lg_rim" + nm, tuple(mid + rd * RIM_D), wr_, rs_, color=kelvin(8000.0),
                                    size_y=RIM_LEN, target=tuple(mid))
            ly = rl_.matrix_world.to_3x3() @ Vector((0, 1, 0))
            ang = ly.angle(Vector((0, 0, 1)))
            rl_.rotation_euler.rotate(Matrix.Rotation(ang if ly.cross(Vector((0, 0, 1))).dot(-rd) >= 0 else -ang, 3,
                                                      -rd).to_euler())
            rl_.visible_diffuse = False
            rl_.lightgroup = "sheen"
            # not the bores or the throat: their coat mirrored the strips as a grey film over the glow
            KL7.link_receivers(rl_, [ob_ for r in (pace_r or roots) for k, ob_ in C.parts(r).items()
                                     if k not in ("holes", "throat", "bridgewall", "grip") and not k.startswith("thr")],
                               "recv_rim" + nm)
    wsl = CMD_WALL_S if cmd_r else WALL_S
    if wsl > 0:
        # Command: the wall and neck on the camera's left fall to clean, soft white-in-shade, not a streaky dark patch
        wd = (Matrix.Rotation(math.radians(-55.0), 3, Vector((0, 0, 1))) @ (cam.location - c).normalized())
        wl = studio.area_light("lg_wall", tuple(c - up * 0.12 + wd * 0.8), 0.5, wsl, color=kelvin(6500.0),
                               size_y=0.6, target=tuple(c - up * 0.12))
        wl.visible_glossy = False
        wl.lightgroup = "fill"
        wr = []
        for r in (cmd_r or roots):
            wr += C.objs(r, "wall", "neck", "rim")
        KL7.link_receivers(wl, wr, "recv_wall")
    # fill: weak, cool, from the camera side
    fl = studio.area_light("lg_fill", tuple(cam.location * 0.6 + c * 0.4 + Vector((0.0, 0.0, 0.25))), 1.2, FILL_S,
                           color=kelvin(7500.0), target=tuple(c))
    fl.lightgroup = "fill"
    ws = P_WEAVE_S if pace else WEAVE_S
    if pace and P_FIX > 0:
        ws *= P_WEAVE_K
    if ws > 0:
        # Pace: a soft card a few degrees off the face's mirror direction (glossy only): the 12K tapes' lobes read
        dirn = (Matrix.Rotation(math.radians(WEAVE_UP), 3, ax_up) @ mirror).normalized()
        wc = studio.area_light("lg_weave", tuple(c + dirn * 1.6), WEAVE_SIZE, ws, color=kelvin(6200.0), target=tuple(c))
        wc.visible_diffuse = False
        wc.lightgroup = "sheen"
        if cmd_r:
            KL7.link_receivers(wc, [ob_ for r in pace_r for ob_ in C.objs(r, "all")], "recv_weave")


def grade_card(roots, cam):
    """pace-dark-fix (a): a long soft emissive card (glossy rays only, never seen) along the whole Pace racket, P_GRADE_OFF
    degrees off the face's mirror direction about the long axis, so the clear coat never mirrors it while the tapes' fibre
    lobes catch it from the crown to the Q end; its strength falls from P_GRADE_S at the crown end to P_GRADE_LOW of it at
    the handle end (smoothstep), so the racket never drops to black below its top third."""
    pace_r = [r for r in roots if r.get("kq_feel") == "pace"]
    if not pace_r or P_FIX <= 0 or P_GRADE_S <= 0:
        return None
    from mathutils import Matrix
    import k789_lib as KL7
    c, up, across, nrm = racket_frame(pace_r[0])
    v = (cam.location - c).normalized()
    mirror = (2 * v.dot(nrm) * nrm - v).normalized()
    dirn = (Matrix.Rotation(math.radians(P_GRADE_OFF), 3, up) @ mirror).normalized()
    ctr = c + up * P_GRADE_CY + dirn * P_GRADE_D
    zl = -dirn
    yl = (up - up.dot(dirn) * dirn).normalized()
    xl = yl.cross(zl).normalized()
    w2, l2 = P_GRADE_W / 2, P_GRADE_L / 2
    me = bpy.data.meshes.new("lg_grade")
    me.from_pydata([(-w2, -l2, 0), (w2, -l2, 0), (w2, l2, 0), (-w2, l2, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("lg_grade", me)
    bpy.context.scene.collection.objects.link(ob)
    M = Matrix((xl, yl, zl)).transposed().to_4x4()
    M.translation = ctr
    ob.matrix_world = M
    m = bpy.data.materials.new("lg_grade")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*kelvin(6200.0), 1)
    tc = nodes.new("ShaderNodeTexCoord")
    sp = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sp.inputs["Vector"])
    mr = _n(nodes, "ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = -l2
    mr.inputs["From Max"].default_value = l2
    mr.inputs["To Min"].default_value = P_GRADE_S * P_GRADE_LOW
    mr.inputs["To Max"].default_value = P_GRADE_S
    links.new(sp.outputs["Y"], mr.inputs["Value"])
    # soft across its width too (a flat face mirrors a hard card edge as a hard line): 1 at the centre line, 0 at the sides
    ax = _n(nodes, "ShaderNodeMath", "ABSOLUTE")
    links.new(sp.outputs["X"], ax.inputs[0])
    mx = _n(nodes, "ShaderNodeMapRange")
    mx.interpolation_type = "SMOOTHERSTEP"
    mx.inputs["From Min"].default_value = 0.0
    mx.inputs["From Max"].default_value = w2
    mx.inputs["To Min"].default_value = 1.0
    mx.inputs["To Max"].default_value = 0.0
    links.new(ax.outputs[0], mx.inputs["Value"])
    mm = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(mr.outputs["Result"], mm.inputs[0])
    links.new(mx.outputs["Result"], mm.inputs[1])
    links.new(mm.outputs[0], em.inputs["Strength"])
    links.new(em.outputs[0], out.inputs["Surface"])
    me.materials.append(m)
    for k in ("visible_camera", "visible_diffuse", "visible_transmission", "visible_volume_scatter", "visible_shadow"):
        setattr(ob, k, False)
    ob.lightgroup = "sheen"
    KL7.link_receivers(ob, [ob_ for r in pace_r for k, ob_ in C.parts(r).items()
                            if k not in ("holes", "throat", "bridgewall", "grip", "cap", "capmark") and not k.startswith("thr")],
                       "recv_grade")
    # shadow linking: only these rackets block their card (in K07's row a neighbour stood between a Pace and its card)
    bc = bpy.data.collections.new("block_grade")
    for r in pace_r:
        for ob_ in C.objs(r, "all"):
            bc.objects.link(ob_)
    ob.light_linking.blocker_collection = bc
    return ob


def grip_dark(roots, cam):
    """Unlink every light from the overgrip (the cap keeps its light: satin black with the Q); then, with GRIP_RIM_S, a
    thin glossy strip that lights the overgrip alone, so its helical wrap reads as fine lines on black."""
    if GRIP_DARK <= 0:
        return
    import k789_lib as KL7
    grips, caps = [], {}
    for r in roots:
        P = C.parts(r)
        if "grip" in P and not P["grip"].hide_render:
            grips.append(P["grip"])
            # pace-dark-fix:OK (cloud 09:12Z): the satin cap read as a bright ring floating below a vanished overgrip;
            # with GRIP_CAP the cap (and its Q) leave the scene lights and take the grip's own, so the handle reads as
            # one object ending in the cap
            caps[P["grip"].name] = [P[k] for k in ("cap", "capmark") if k in P and not P[k].hide_render] if GRIP_CAP > 0 else []
    if not grips:
        return
    unl = grips + [c_ for v in caps.values() for c_ in v]
    allo = [ob_ for r in roots for ob_ in C.objs(r, "all") if ob_ not in unl]
    for L_ in [ob_ for ob_ in bpy.data.objects if ob_.type == "LIGHT"]:
        rc = L_.light_linking.receiver_collection
        if rc is None:
            KL7.link_receivers(L_, allo, "recv_nogrip_" + L_.name)
        else:
            for g in unl:
                if g.name in rc.objects:
                    rc.objects.unlink(g)
    from mathutils import Matrix
    for nm, gs, gaz, gw, gh in (("rim", GRIP_RIM_S, GRIP_RIM_AZ, GRIP_RIM_W, GRIP_RIM_H),
                                ("side", GRIP_SIDE_S, GRIP_SIDE_AZ, GRIP_SIDE_W, GRIP_SIDE_H),
                                ("front", GRIP_FRONT_S, GRIP_FRONT_AZ, GRIP_FRONT_W, GRIP_FRONT_H),
                                ("cap", GRIP_CAP_S, GRIP_FRONT_AZ, GRIP_FRONT_W, GRIP_FRONT_H)):
        if gs <= 0:
            continue
        for g in grips:
            if nm == "cap" and not caps.get(g.name):
                continue
            bpy.context.view_layer.update()
            bb = [g.matrix_world @ Vector(v) for v in g.bound_box]
            gc = sum(bb, Vector()) / 8.0
            vc = cam.location - gc
            vc.z = 0.0
            vc.normalize()
            d = (Matrix.Rotation(math.radians(gaz), 3, Vector((0, 0, 1))) @ vc).normalized()
            # the front card a little above the grip, so its broad sheen runs down the wrap's bands
            lp = gc + d * GRIP_DIST + Vector((0, 0, GRIP_FRONT_UP if nm == "front" else 0.0))
            gl = studio.area_light("lg_grip%s_%s" % (nm, g.name), tuple(lp), gw, gs, color=kelvin(6500.0),
                                   size_y=gh, target=tuple(gc))
            gl.visible_diffuse = False
            gl.lightgroup = "sheen"
            rcv = caps[g.name] if nm == "cap" else [g]
            KL7.link_receivers(gl, rcv, "recv_grip%s_%s" % (nm, g.name))

def build_comp(sc, src, o, out_stem):
    tr = sc.node_tree
    den = {}
    for g in GROUPS:
        dn = tr.nodes.new("CompositorNodeDenoise")
        dn.prefilter = "ACCURATE"
        dn.use_hdr = True
        tr.links.new(src[g], dn.inputs["Image"])
        tr.links.new(src["normal"], dn.inputs["Normal"])
        tr.links.new(src["albedo"], dn.inputs["Albedo"])
        gn = float(o.get("g_" + g, 1.0))
        mu = tr.nodes.new("CompositorNodeMixRGB")
        mu.blend_type = "MULTIPLY"
        mu.inputs["Fac"].default_value = 1.0
        mu.inputs[2].default_value = (gn, gn, gn, 1)
        tr.links.new(dn.outputs["Image"], mu.inputs[1])
        den[g] = mu.outputs["Image"]

    def add(a, b):
        n = tr.nodes.new("CompositorNodeMixRGB")
        n.blend_type = "ADD"
        n.inputs["Fac"].default_value = 1.0
        tr.links.new(a, n.inputs[1])
        tr.links.new(b, n.inputs[2])
        return n.outputs["Image"]

    base = add(add(add(den["key"], den["sheen"]), den["fill"]), den["env"])
    full = add(base, den["glow"])
    outs = {"full": full, "base": base}
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = os.path.dirname(out_stem)
    fo.format.file_format = "PNG"
    fo.format.color_mode = "RGB"
    fo.format.color_depth = "16"
    fo.file_slots.clear()
    written = []
    for v in ("base", "full"):
        name = os.path.basename(out_stem) + "-" + v
        fo.file_slots.new(name)
        tr.links.new(outs[v], fo.inputs[name])
        written.append(name)
    comp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(outs["full"], comp.inputs["Image"])
    return written


def finish_outputs(out_stem, written):
    d = os.path.dirname(out_stem)
    paths = []
    for name in written:
        cands = [f for f in os.listdir(d) if f.startswith(name) and f.endswith(".png") and f[len(name):-4].isdigit()]
        cands.sort(key=lambda f: os.path.getmtime(os.path.join(d, f)))
        if cands:
            dst = os.path.join(d, name + ".png")
            os.replace(os.path.join(d, cands[-1]), dst)
            paths.append(dst)
    return paths


def card_crops(paths):
    """<name>_card.png: the card crop (x CARD_X0, w CARD_W, full height), lossless 16-bit (split_master's writer)."""
    import struct
    import zlib

    def write16(path, a16):
        h, w, c = a16.shape
        raw = np.empty((h, 1 + w * c * 2), dtype=np.uint8)
        raw[:, 0] = 0
        raw[:, 1:] = a16.astype(">u2").view(np.uint8).reshape(h, w * c * 2)

        def chunk(tag, data):
            b = struct.pack(">I", len(data)) + tag + data
            return b + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 6 if c == 4 else 2, 0, 0, 0))
        png += chunk(b"sRGB", b"\x00") + chunk(b"IDAT", zlib.compress(raw.tobytes(), 6)) + chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)
    out = []
    for p in paths:
        im = bpy.data.images.load(p, check_existing=False)
        im.colorspace_settings.name = "Non-Color"
        W, H = im.size
        px = np.empty(W * H * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        a = np.rint(px.reshape(H, W, 4)[::-1, :, :3] * 65535.0).astype(np.uint16)
        x0 = int(round(CARD_X0 * W))
        x1 = x0 + int(round(CARD_W * W))
        dst = p[:-4] + "_card.png"
        write16(dst, np.ascontiguousarray(a[:, x0:x1]))
        out.append(dst)
    return out


def main():
    o = parse_args()
    OPT.update(o)
    t0 = time.time()
    studio.reset()
    sc = bpy.context.scene
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.diffuse_bounces = 3
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.use_denoising = False
    sc.cycles.seed = 11
    if CLAMP_IND > 0:
        sc.cycles.sample_clamp_indirect = CLAMP_IND
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in GROUPS:
        vl.lightgroups.add(name=g)
    roots = build_rackets(o)
    for r in roots:
        P = C.parts(r)
        for k in ("holes",):
            if k in P:
                lip = r.get("kq_feel") == "pace" and P_FIX > 0 and P_LIP > 0
                set_glow(P[k], "lip" if lip else "depth", GLOW_S)
        for k, ob in P.items():
            if (k == "throat" or k.startswith("thr") or k == "bridgewall") and THROAT_GLOW > 0:
                set_glow(ob, "depth", GLOW_S * THROAT_GLOW)
        eg = EDGE_GLOW if r.get("kq_feel") == "pace" else CMD_EDGE_GLOW
        if "rim" in P and eg > 0:
            set_glow(P["rim"], "edge", eg)
    for r in roots:
        if r.get("kq_feel") == "pace":
            P = C.parts(r)
            y_cut = None
            if "neck" in P:
                ys = [v.co.y for v in P["neck"].data.vertices]
                y_cut = max(ys)                       # the neck's top: the head's edge keeps its tow break
                continuous_coat(P["neck"])
            if "rim" in P and y_cut is not None:
                continuous_coat(P["rim"], y_cut)
            if "glow_done" not in r:
                pass
    world_field(sc)
    # camera: lower than the racket's mid, closer, longer lens; framed to the card crop
    pts = sample_points(roots)
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    aim = (lo + hi) / 2
    el, az = math.radians(CAM_EL), math.radians(CAM_AZ)
    dirn = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam = studio.camera(tuple(aim + dirn * 3.0), tuple(aim), lens=LENS)
    sc.camera = cam
    d = frame_camera(sc, cam, pts, aim, dirn)
    lights(roots, o)
    grade_card(roots, sc.camera)
    grip_dark(roots, sc.camera)
    for ob_ in sc.objects:
        if ob_.type == "LIGHT":
            ob_.visible_camera = False      # no strip or card ever seen through a hole
    print("camera", tuple(round(x, 3) for x in cam.location), "distance", round(d, 3), "lens", LENS,
          "shift", round(cam.data.shift_x, 4), round(cam.data.shift_y, 4))
    if o.get("dry"):
        return
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    rl = tr.nodes.new("CompositorNodeRLayers")
    src = {g: rl.outputs["Combined_" + g] for g in GROUPS}
    src["albedo"] = rl.outputs["Denoising Albedo"]
    src["normal"] = rl.outputs["Denoising Normal"]
    out_stem = out_path(o["out"])[:-4]
    written = build_comp(sc, src, o, out_stem)
    sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.exr_codec = "ZIP"
    sc.render.filepath = out_stem + ".exr"
    bpy.ops.render.render(write_still=True)
    paths = finish_outputs(out_stem, written)
    cards = card_crops(paths)
    print("rendered", paths + cards, round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
