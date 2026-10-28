"""K10-throat-serial: macro of the VanQuish throat with its laser-etched number, "027/500", and a small KINETIQ.

Subject (v14): the racket face-up, seen from the handle end 40 deg above the face, 100 mm-class macro at f/10 focused
on the number. The triangle opening points down at it; the lowest row of holes is cropped by the top edge; the neck
lofts on toward the handle (k10_lib.NECK: 47 -> 32 mm wide, 38 -> 29 mm thick), so the bottom edge cuts tapering
carbon (no end face, grip or collar in frame). Face and throat lip are one continuous 3K twill (k04_tex2 maps, as K04,
plus straight fibre-bundle streaks along each tow) under a mirror-flat gloss lacquer (fold UVs). Below the bridge
lip the wall is another plane: the tows run straight down it (clamped UVs), and it falls to black with depth.
The number is a frosted laser mark in the lacquer (a 0.03 mm bevel, ~0.1 mm frost grain) that lights up under a
close raking strip from camera-left (brighter on the left glyphs).

Canonical racket (2026-10-22, shots/kq_canon.py, built with throat_segs=k10_lib.THROAT_SEGS): the canon holes (the
lowest row now the canonical A row: three holes at x -49 / 0 / +49 mm, y -59.6 mm), dark carbon-lined bores, and the
canon's shorter one-piece neck (47 -> 33 mm over y -0.146 .. -0.176, 38 -> 29 mm thick, its edge rounding growing from
1.5 to 12 mm), so the neutral-black overgrip's 11 mm finishing band (y -0.174 .. -0.185) now enters at the bottom of
the frame: kept, and lit by a dim raking strip (light group "grip") so its cut edge reads. The face carries K10's own
etch (owner override, 2026-10-22: the pair edition's set number "027/500" over KINETIQ, exactly as before: Archivo
wdth 125 / wght 360, cap 5.6 mm, tracking 0.09 em, y -0.1372; KINETIQ wght 560, 1.55 mm, 0.62 em, y -0.1446) in K10's
own carbon (k04_tex2 twill, 2.6 mm tows, options as before). Light linking maps K10's old parts onto the canon's:
K10 "face" (both caps, the neck's too) = canon face + neck; K10 "rim" (outline edge + wall, the neck's sides too) =
canon rim + wall + neck. --mark serial puts the canon serial mark (KQ-000427 in Saira, y -0.1365, + KINETIQ) instead.
WHITE Command (owner, 2026-10-22; --white 0 gives the previous black K10 carbon): every role in kq_canon.mat_white
(k04_tex2 twill, 2.6 mm tows, the throat walls darkening to graphite with depth, WHITE_MAT), the etch a graphite laser
frost. White is lit by real diffuse light: "pool" (a soft 18 deg spot from the upper left of the frame, on the face,
edges, bores, throat and neck) and "poolw" (the same spot on the side walls only, graded down), "fill", and two
glossy-only lacquer reflections ("sheen", a half-plane with a crisp edge, and "wline", one gloss line); the
black-carbon groups below are graded for white by WHITE_GAINS in comp (sky, haze and gloss off, rake low).
Page crops (src/content/stills.json): wide x .0225 y .045 w .955 h .955 and card x .285 y .045 w .43 h .955 (gallery
phone); comp writes both next to the frame and fill-checks all three.
Pre-canon version: shots/K10-throat-serial.precanon.bak.
Stage 3a (art director's critique, 2026-10-22; before: K10-throat-serial.v4-white-precrit3a.bak): white tow relief cut
by about two thirds (WHITE_MAT bump 0.10, streak_h 0.08: no parquet face or wicker walls); the throat's inner wall is a
smooth graphite lining darkening with depth like the bores (throat_lining, THROAT_LINING: no stretched-twill streaks);
the left-lip ember ribbon is a neutral silver line on white (WHITE_EMBER); the pool aims at the number (POOL) and the comp
grades the rest away (WHITE_GAINS, WHITE_VIG: an elliptical vignette, the backdrop taking only part of it): serial and
bridge about 195, upper face and top holes 75-100, walls 55-90, lower corners graphite; about 64 % of the frame lit.

Light (one light group each; the shot renders once and is graded from the denoised group passes, see --comp/--sheet):
- sky   : projected softbox: a soft diagonal band across the upper face, held clear of the bridge,
- gloss : one projected light line in the lacquer along that band,
- haze  : a dim room reflection over the face (kept low: no grey wash),
- low   : one large dim card mirrored in the lower face and neck, fading from camera-left to right,
- rake  : a hard strip 16 deg above the face from camera-left, 12.5 cm away (frost of the etch; face only: the canon
          neck's rounded left side took a hot glint from it; --rake_neck 1 links the neck again),
- edge  : ONE mirror-path ribbon along the throat lip: fades in right of the apex, up the right arm, round the
          top-right fillet, along the bridge, out before the top-left fillet (built in arc-length segments),
- ember : the same construction on the left arm only, peaking mid-arm, gone before the apex and the corner,
- wall  : light falling just under the bridge lip onto the inner wall,
- rim   : asymmetric: a crisp top-edge line on the left wall; a long soft gradient on the right wall and neck,
- bg    : a graphite backdrop below the racket (camera rays only), seen at the lower corners,
- grip  : a dim strip raking the overgrip's finishing band at the bottom edge.

--feel pace (Release 2, 2026-10-23): the canon Pace v6 under the black-carbon rig (see P_* below); final:
  --feel pace --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial-pace
  -> K10-throat-serial-pace.png, -pace-wide.png, -pace-card.png. The default (--feel command) is unchanged.
Usage: K10-throat-serial.py --w 960 --h 540 --spp 48 --out K10_p13
  writes out/k10/K10_p13.png (+ _wide.png and _card.png, the page crops) and the passes in out/k10/passes/,
  runs fillcheck.py on both. Final: --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial
  -> out/final/K10-throat-serial.png, -wide.png and -card.png.
  --comp: regrade from the passes of an earlier render with the same --out (no path tracing); gains --g_<group>.
  --sheet: every light group alone, as a contact sheet. --crop x0,x1,y0,y1 (frame fractions, y from the top).
Dev flags: --el --yaw --dist --fw --fstop --sx --sy --focus_dy, --bloom thr,amt,rad (0 = off), and every light's
strength by name (--rake, --sky, --edge ...).
"""
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import kqpaths  # noqa: E402

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402
import k12_lib as K  # noqa: E402
import k10_lib as L  # noqa: E402
import kq_canon as C  # noqa: E402

GROUPS = ("sky", "gloss", "haze", "low", "rake", "edge", "ember", "wall", "rim", "bg", "grip", "pool", "poolw", "fill", "sheen", "wline")
CROPS = {"wide": (0.0225, 0.045, 0.955, 0.955), "card": (0.285, 0.045, 0.43, 0.955)}  # stills.json: x, y, w, h
EMBER = (1.0, 0.23, 0.12)
ZT = L.ZT
U = racket.U


def is_pace(o):
    """--feel pace (Release 2 feel toggle, 2026-10-23): the canon Pace (kq_canon.PACE v6, black 12K) under the
    black-carbon rig; --feel command (the default) is unchanged."""
    return o.get("feel", "command") == "pace"


def is_white(o):
    """Command is WHITE 3K twill (owner, 2026-10-22); --white 0 gives the previous black K10 carbon."""
    return float(o.get("white", 1.0)) > 0 and not is_pace(o)


# ------------------------------------------------------------------ Pace (--feel pace, Release 2, 2026-10-23)
# The same camera, crops and black-carbon light family as the pre-white K10 (sky band, gloss line, haze, low card,
# rake for the frost, edge ribbons, wall, rim, backdrop, grip), on the canon Pace v6 (black 12K spread tow, 8 mm
# tapes, fibre-sheen weave, kq_canon.mat_pace) in every role: face (with K10's 027/500 etch), skin, throat walls
# (mat_pace wall: falls to black with depth) and the carbon-lined bores. No ember on the racket (RENDER_NOTES, Pace
# v5/v6): the left-lip ribbon is the neutral 6500 K line at P_EMBER of the ember's strength. P_GAINS grade the light
# groups in comp (the black rig was tuned on the baked 3K twill); P_CLAMP clamps indirect light (12K fireflies, as
# K11/K06); P_MAT takes kq_canon PACE keys (--p_<key> on the command line).
P_GAINS = {"low": 2.5, "haze": 2.5, "bg": 1.5, "rim": 1.5}   # preview K10p_a: dark 49 % -> 23 % (16:10)
P_EMBER = 0.30
P_CLAMP = 4.0
P_MAT = {}


# white Command: default comp gains for the black-carbon reflection groups (each group's pass is scaled in comp, so
# these regrade without a re-render; --g_<group> still wins)
# stage 3a (art director: "a flat grey wash", 94 % of the frame lit): the pool now centres on the number (POOL below),
# a little stronger, the fill lower, and WHITE_VIG grades the rest away: serial and bridge about 195, the upper face and
# top holes about 75-100, the walls 55-90, the lower corners graphite (35); about 64 % of the frame lit
WHITE_GAINS = {"sky": 0.0, "haze": 0.0, "low": 0.1, "rake": 0.15, "gloss": 0.0, "wall": 0.05, "rim": 1.6,
               "pool": 1.25, "poolw": 0.75, "fill": 0.25, "sheen": 0.8, "wline": 0.6}
# the white pool (spot): position, aim (model metres), cone (deg). Stage 3a: aimed at the number from the frame's upper
# left (it was aimed above the throat, which made the upper face the brightest part of the frame)
POOL = dict(pool_x=-0.45, pool_y=0.05, pool_z=0.80, pool_tx=0.0, pool_ty=-0.14, pool_deg=12.0)
# white Command material defaults for this macro (kq_canon COMMAND_WHITE keys): the throat walls darken further with
# depth (0.78 instead of 0.60), so the opening reads as a through-opening and not as a lit white dish
WHITE_MAT = {"wall_occ": 0.78,
             # stage 3a (art director): at macro scale the canon's tow relief (bump 0.30 + streak height 0.25) shaded each
             # 2.6 mm tow as a bevelled brick (parquet face, wicker walls); real twill lies flat under clear resin and a
             # white diffuse base shows bump far more than black. Cut by about two thirds: the weave stays in the albedo
             # and the anisotropic sheen under a smooth coat, as in K11 and K08
             "bump": 0.10, "streak_h": 0.08}
# stage 3a: the throat's inner wall, like the bores (smooth graphite darkening with depth, no stretched twill streaks):
# below the gloss lip (THR_LIP) it blends by THR_FULL into a smooth graphite of tone THR_TOP that falls to THR_DEEP by
# THR_Z (depth from the face, metres); roughness THR_ROUGH
THROAT_LINING = dict(lip=0.0012, full=0.0035, z=0.020, top=0.16, deep=0.012, rough=0.6)
# white Command: the ember ribbon on the throat's left lip becomes a neutral silver line (a red hairline on white read
# as a pink colour fringe; the ember stays on black parts only), at this fraction of the ember's strength
WHITE_EMBER = 0.40
# stage 3a: comp vignette for white (multiplies the linear sum by 1 - vig x smoothstep(r0, r1, r)): r is the distance
# from (vig_cx, vig_cy) (frame fractions, y from the top) in frame heights, x divided by vig_sx and y by vig_sy (an
# ellipse). Keeps the serial and bridge bright and lets the upper face, the top holes and the frame's corners fall away
# (low-key, like the old black K10), while the side walls keep their graded highlight
WHITE_VIG = dict(vig=0.82, vig_r0=0.08, vig_r1=0.52, vig_cx=0.5, vig_cy=0.62, vig_sx=2.0, vig_sy=0.9, vig_bg=0.45)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 960, "h": 540, "spp": 32, "out": "K10_prev"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            o[k] = v
            i += 1
        elif a.startswith("--") and i + 1 < len(argv) and not (argv[i + 1].startswith("--")):
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


def paths(o):
    out = o["out"]
    if os.path.isabs(out):
        png = out if out.endswith(".png") else out + ".png"
    elif "/" in out:
        png = os.path.join(studio.OUT, out if out.endswith(".png") else out + ".png")
    else:
        png = os.path.join(studio.OUT, "k10", out + ".png")
    os.makedirs(os.path.dirname(png), exist_ok=True)
    stem = os.path.basename(png)[:-4]
    pdir = os.path.join(studio.OUT, "k10", "passes")
    os.makedirs(pdir, exist_ok=True)
    sep = "-" if "final" in png.split(os.sep) else "_"
    return png, png[:-4] + sep + "card.png", pdir, stem


def crop_path(png, name):
    sep = "-" if "final" in png.split(os.sep) else "_"
    return png[:-4] + sep + name + ".png"


# ------------------------------------------------------------------ etch
def etch_lines(o):
    ys = f(o, "serial_y", -0.1372)
    return [
        ("027/500", f(o, "serial_cap", 0.0056), ys, f(o, "serial_track", 0.09), f(o, "serial_wght", 360), 125, 1.0),
        ("KINETIQ", f(o, "brand_cap", 0.00155), ys + f(o, "brand_dy", -0.0074), f(o, "brand_track", 0.62),
         f(o, "brand_wght", 560), 125, f(o, "brand_level", 0.80)),
    ]


def throat_lining(m, o):
    """Stage 3a: the throat's inner wall read as the bores do: below the gloss lip the lining blends into a smooth
    graphite that darkens with depth (the white twill's wall UVs run straight down the wall and stretched into vertical
    streaks, a striped curtain on white). Same treatment as kq_canon._bore_wrap, but fully smooth below the lip."""
    p = dict(THROAT_LINING, **{k_[4:]: float(v_) for k_, v_ in o.items() if k_.startswith("thr_")})
    nb = K.NB(m)
    out, surf = C._out_surface(m)
    _, _, z = nb.coords("Object")
    az = nb.math("ABSOLUTE", z)
    mixf = nb.smooth(az, ZT - p["lip"], ZT - p["full"])
    g = nb.smooth(az, ZT - p["full"], ZT - p["z"])
    tone = nb.lerp(g, p["top"], p["deep"])
    b = nb.n.new("ShaderNodeBsdfPrincipled")
    cc = nb.n.new("ShaderNodeCombineColor")
    for k_, f_ in enumerate((0.98, 1.0, 1.04)):
        nb.l.new(nb.math("MULTIPLY", tone, f_), cc.inputs[k_])
    nb.l.new(cc.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = p["rough"]
    b.inputs["Specular IOR Level"].default_value = 0.3
    mx = nb.n.new("ShaderNodeMixShader")
    nb.l.new(mixf, mx.inputs[0])
    nb.l.new(surf, mx.inputs[1])
    nb.l.new(b.outputs[0], mx.inputs[2])
    nb.l.new(mx.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ scene
def build(o):
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 6
    sc.cycles.diffuse_bounces = 2
    sc.cycles.transmission_bounces = 2
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.use_denoising = False
    sc.cycles.adaptive_threshold = f(o, "noise", 0.01)
    sc.cycles.seed = 10
    sc.cycles.blur_glossy = 0.5
    sc.render.film_transparent = False

    # the canonical racket, its throat split in K10's arc-length segments; its own materials replaced by K10's (the
    # same k04_tex2 twill with K10's options) and the face by K10's etched face
    white = is_white(o)
    pace = is_pace(o)
    if pace and f(o, "p_clamp", P_CLAMP) > 0:
        sc.cycles.sample_clamp_indirect = f(o, "p_clamp", P_CLAMP)
    root, head = C.build_racket("KQ10", feel="pace" if pace else "command", serial="", throat_segs=L.THROAT_SEGS,
                                mat_opts=None if (white or pace) else {"white": 0})
    if o.get("mark", "set") == "serial":
        etch = C.serial_etch(C.SERIAL)
    else:
        mask = kqpaths.asset("k10", "etch_mask.png")
        etch = L.etch_mask(mask, etch_lines(o), bevel=f(o, "bevel", 0.00003))
    if pace:
        # canon Pace v6 in every role (kq_canon.mat_pace), K10's etch frosted into the face lacquer
        po = dict(P_MAT, **{k_[2:]: float(v_) for k_, v_ in o.items() if k_.startswith("p_") and k_[2:] in C.PACE})
        po = po or None
        carbon_face = C.mat_pace("K10p_face", etch=etch, o=po)
        carbon = C.mat_pace("K10p", o=po)
        carbon_wall = C.mat_pace("K10p_wall", wall=True, o=po)
        carbon_bore = C._bore_wrap(C.mat_pace("K10p_bore", o=po))
    elif white:
        # WHITE Command (owner, 2026-10-22): kq_canon.mat_white on every role, the etch a graphite laser frost;
        # material overrides from the command line as --w_<COMMAND_WHITE key>
        wo = dict(WHITE_MAT, **{k_[2:]: float(v_) for k_, v_ in o.items() if k_.startswith("w_") and k_[2:] in C.COMMAND_WHITE})
        pw = dict(C.COMMAND_WHITE, **wo)
        carbon_face = C.mat_white("K10w_face", wo, etch=etch)
        carbon = C.mat_white("K10w", wo)
        carbon_wall = throat_lining(C.mat_white("K10w_wall", wo, wall=True), o) if f(o, "lining", 1.0) else \
            C.mat_white("K10w_wall", wo, wall=True)
        carbon_bore = C._bore_wrap(C.mat_white("K10w_bore", wo, wall=True), z_dark=float(pw["bore_dark"]),
                                   occ=float(pw["bore_occ"]), col=float(pw["bore_col"]))
    else:
        carbon_face = L.mat_carbon_k10("CarbonK10_face", o, etch=etch)
        carbon = L.mat_carbon_k10("CarbonK10", o)
        carbon_wall = L.mat_carbon_k10("CarbonK10_wall", o, wall=True)
        # bores: the canon's carbon lining that darkens with depth (sealed core), in K10's carbon
        carbon_bore = C._bore_wrap(L.mat_carbon_k10("CarbonK10_bore", dict(o, wall_occ=0.0), wall=True))
    for k_, ob in head.items():
        if k_ in ("grip", "cap", "capmark", "etchR", "etchL"):
            continue
        m_ = (carbon_face if k_ == "face" else carbon_wall if (k_.startswith("thr") or k_ in ("bridgewall", "throat"))
              else carbon_bore if k_ == "holes" else carbon)
        ob.data.materials.clear()
        ob.data.materials.append(m_)
    FACE = [head["face"], head["neck"]]                           # K10's "face": both caps, the neck's too
    RIM = [head["rim"], head["wall"], head["neck"]]               # K10's "rim": outline edge + wall, the neck's sides

    # ---------------- camera: from the handle end, low over the face, centred on the number
    S = Vector((0.0, f(o, "serial_y", -0.1372) + f(o, "aim_dy", 0.0), ZT))
    el = math.radians(f(o, "el", 40.0))
    yaw = math.radians(f(o, "yaw", 0.0))
    fwd = Vector((math.sin(yaw), math.cos(yaw), 0.0))
    up = Vector((0, 0, 1))
    dist = f(o, "dist", 0.34)
    fw = f(o, "fw", 0.158)
    cam_loc = S - fwd * dist * math.cos(el) + up * dist * math.sin(el)
    cam = studio.camera(tuple(cam_loc), tuple(S), lens=36.0 * dist / fw, shift=(f(o, "sx", 0.0), f(o, "sy", 0.046)))
    cd = cam.data
    cd.clip_start = 0.01
    fstop = f(o, "fstop", 10.0)
    cd.dof.use_dof = fstop > 0
    cd.dof.aperture_fstop = max(fstop, 0.5)
    cd.dof.aperture_blades = 9
    cd.dof.aperture_ratio = 1.0
    fp = Vector((0.0, f(o, "serial_y", -0.1372) + f(o, "focus_dy", -0.0037), ZT))
    view = (S - cam_loc).normalized()
    cd.dof.focus_distance = (fp - cam_loc).dot(view)
    bpy.context.view_layer.update()

    def mirror(P, n):
        d = (Vector(P) - cam_loc).normalized()
        n = Vector(n).normalized()
        return (d - 2 * d.dot(n) * n).normalized()

    def face_point(u, v):
        vf = cd.view_frame(scene=sc)
        tr_, br, bl_, tl = vf[0], vf[1], vf[2], vf[3]
        p_local = tl.lerp(tr_, u).lerp(bl_.lerp(br, u), v)
        d = (cam.matrix_world.to_3x3() @ p_local).normalized()
        t_ = (ZT - cam_loc.z) / d.z
        return cam_loc + d * t_, d

    # ---------------- backdrop: graphite, below the racket, camera + glossy rays only
    zb = f(o, "bg_z", -0.13)
    bgc = Vector((0.0, f(o, "bg_cy", -0.11), zb))
    bg = K.plane("Backdrop", (4.0, 4.0), (0, 0, zb))
    bi, bo, br_ = f(o, "bg_in", 68.0), f(o, "bg_out", 34.0), f(o, "bg_r", 0.30)

    def bgs(nb):
        x, y, _ = nb.coords("Object")
        dx = nb.math("SUBTRACT", x, bgc.x)
        dy = nb.math("MULTIPLY", nb.math("SUBTRACT", y, bgc.y), 1.4)
        r = nb.math("SQRT", nb.math("ADD", nb.math("MULTIPLY", dx, dx), nb.math("MULTIPLY", dy, dy)))
        t = nb.smooth(r, 0.0, br_)
        return nb.lerp(t, K.emit_for(bi), K.emit_for(bo))

    bg.data.materials.append(K.emitter_mat("BackdropMat", (0.93, 0.95, 1.0), bgs, additive=False))
    K.visibility(bg, camera=True, diffuse=False, glossy=False, shadow=False)
    bg.lightgroup = "bg"


    # ---------------- sky: a projected softbox; its reflection is a designed diagonal sweep on the face.
    # The sweep's soft edge runs along the frame line (sky_u1, sky_v1) -> (sky_u2, sky_v2): bright on its upper-right
    # side, black lacquer on the number's side. v14: 0.75x and lifted away from the bridge (the frame was top-heavy).
    A_, _ = face_point(f(o, "sky_u1", 0.02), f(o, "sky_v1", -0.03))
    B_, _ = face_point(f(o, "sky_u2", 0.98), f(o, "sky_v2", 0.17))
    Cs, _ = face_point(0.6, 0.25)
    pc, _ = face_point(f(o, "pool_u", 0.62), f(o, "pool_v", 0.07))
    bw = f(o, "sky_bw", 0.015)
    sky = L.sky_projected("lg_sky", cam_loc, ZT, A_, B_, Cs, (f(o, "sky_size", 3.0), f(o, "sky_size", 3.0)),
                          f(o, "sky_d", 1.0), f(o, "sky_s0", 0.004), f(o, "sky_s1", -0.030), f(o, "sky", 1.26),
                          floor=f(o, "sky_floor", 0.0), pool=(pc.x, pc.y, f(o, "pool_r0", 0.03), f(o, "pool_r1", 0.16)),
                          color=(0.93, 0.96, 1.0), group="sky", band=(f(o, "sky_off", 0.0), bw) if bw > 0 else None)
    THR = [head[k_] for k_ in sorted(head) if k_.startswith("thr")]  # the throat lip, in arc-length segments
    link_sky = FACE + RIM[:2] + [head["holes"]] + THR
    L.link_only(sky, link_sky, "sky_recv")

    # ---------------- gloss: one crisp light line in the lacquer, riding the sweep (the coat reads as glass)
    Ag, _ = face_point(f(o, "gl_u1", 0.0), f(o, "gl_v1", 0.01))
    Bg, _ = face_point(f(o, "gl_u2", 1.0), f(o, "gl_v2", 0.125))
    pg, _ = face_point(f(o, "gl_pu", 0.70), f(o, "gl_pv", 0.07))
    # never coplanar with lg_sky: a glossy ray stops at the first of two coincident transparent emitters
    gl = L.sky_projected("lg_gloss", cam_loc, ZT, Ag, Bg, Cs, (4.2, 4.2), 1.4, 0.0, 0.0, f(o, "gloss", 4.8),
                         pool=(pg.x, pg.y, f(o, "gl_r0", 0.02), f(o, "gl_r1", 0.12)), color=(0.95, 0.97, 1.0),
                         group="gloss", band=(0.0, f(o, "gl_w", 0.0012)))
    L.link_only(gl, FACE, "gloss_recv")

    # ---------------- haze: a dim, even room reflection over the carbon (v14: 40 % less; no longer on the neck)
    Ch, _ = face_point(0.5, 0.40)
    rh = mirror(Ch, (0, 0, 1))
    hz = L.panel("lg_haze", tuple(Ch + rh * 1.2), (4.0, 4.0), f(o, "haze", 0.08), tuple(Ch), color=(0.93, 0.96, 1.0),
                 edge=(-1.0, -0.5), fade=(0, 0.5), group="haze")
    L.link_only(hz, FACE + RIM[:2] + [head["holes"]], "haze_recv")

    # ---------------- low: one large dim card mirrored in the lower face and the neck. Its reflection fades from
    # camera-left to right across the neck (tows flash on the left, drop on the right) and carries the carbon down to
    # the bottom edge. Edge line (low_u1, low_v1) -> (low_u2, low_v2) in frame fractions; bright on its left.
    Al, _ = face_point(f(o, "low_u1", 0.50), f(o, "low_v1", 0.40))
    Bl, _ = face_point(f(o, "low_u2", 0.56), f(o, "low_v2", 1.10))
    Cl, _ = face_point(0.45, 0.85)
    plc, _ = face_point(f(o, "low_pu", 0.42), f(o, "low_pv", 0.90))
    low = L.sky_projected("lg_low", cam_loc, ZT, Al, Bl, Cl, (3.2, 3.2), f(o, "low_d", 0.9), f(o, "low_s0", -0.030),
                          f(o, "low_s1", 0.035), f(o, "low", 0.50), floor=f(o, "low_floor", 0.2),
                          pool=(plc.x, plc.y, f(o, "low_r0", 0.012), f(o, "low_r1", 0.060)), color=(0.93, 0.96, 1.0),
                          group="low")
    L.link_only(low, FACE, "low_recv")

    # ---------------- rake: hard grazing strip from camera-left, close enough that the serial's glyphs fall off
    # left to right (about 15-20 % across its 25 mm). v14: the holes are off its list (identical glints).
    az = math.radians(f(o, "rake_az", -75.0))  # degrees from the view direction, negative = camera-left
    rel = math.radians(f(o, "rake_el", 16.0))
    hdir = fwd * math.cos(az) + fwd.cross(up) * math.sin(az)
    rd = (hdir * math.cos(rel) + up * math.sin(rel)).normalized()
    rake = studio.area_light("lg_rake", tuple(S + rd * f(o, "rake_d", 0.125)), f(o, "rake_len", 0.05),
                             f(o, "rake", 1.06), color=(1.0, 0.985, 0.965), size_y=f(o, "rake_th", 0.005),
                             target=tuple(S + Vector((0, f(o, "rake_ty", 0.004), 0))))
    rake.data.spread = math.radians(f(o, "rake_spread", 180.0))
    rake.lightgroup = "rake"
    # the face only: on the throat lip the grazing rake made a separate glint bead in the top-right fillet; the
    # throat edges carry only the designed mirror-path lines
    # canon: the face only. The neck's 12 mm rounded left side faces this strip and took a hot glint from it (the
    # old K10 neck was flat there); the neck's front tows keep the low card
    L.link_only(rake, [head["face"]] + ([head["neck"]] if o.get("rake_neck") else []), "rake_recv")

    # ---------------- edges: ONE mirror-path ribbon per colour around the throat's rounded edge. Every throat point
    # at bevel angle edge_phi mirrors a ribbon point edge_d away, so the line follows the edge continuously around the
    # 3.5 mm fillets, and its brightness is a profile in arc length:
    #   white: fades in 3-14 mm right of the apex, up the right arm, round the top-right fillet, along the bridge,
    #          and fades out before the top-left fillet;
    #   ember: on the left arm only, peaking mid-arm and gone 9 mm before the apex.
    thr = L.throat_loop()
    xs = np.array([p[0] for p in thr])
    ys = np.array([p[1] for p in thr])
    yb = float(ys[np.abs(xs) < 0.004].max())  # bridge edge (wall line) at the centre
    R = 0.0015
    tn = L._normals(thr, 2)
    if racket._area(thr) > 0:  # loop is CCW: the right normal points into the solid; flip to point into the opening
        tn = [(-a, -b) for (a, b) in tn]
    nt = len(thr)
    s_of, ltot = L.throat_arclength(thr)
    order = sorted(range(nt), key=lambda i: s_of[i])
    sa = [s_of[i] for i in order]
    k_tr = order.index(int(np.argmax(xs)))
    k_tl = order.index(int(np.argmin(xs)))
    s_tr, s_tl = sa[k_tr], sa[k_tl]

    def sm(x, e0, e1):
        t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
        return t * t * (3 - 2 * t)

    def bevel_point(p2, n2, phi_):
        """Point and normal on a rounded edge whose wall line passes p2 with outward plan normal n2."""
        c = Vector((p2[0] - n2[0] * R, p2[1] - n2[1] * R, ZT - R))
        nn = Vector((n2[0] * math.sin(phi_), n2[1] * math.sin(phi_), math.cos(phi_)))
        return c + nn * R, nn

    phi = math.radians(f(o, "edge_phi", 20.0))
    # close to the edge (8 cm): the line's mirror image then sits near the focus plane (crisp), and the lens
    # aperture's parallax moves it < 1 mm along the edge, so each segment's piece stays local (no dashes)
    ed, ew = f(o, "edge_d", 0.08), f(o, "edge_w", 0.0016)
    mm = 0.001
    # both lines end with matched fades outside the fillets' own segments (apex 0-2 / 160+, top-left 109-119 mm)
    w_white = [sm(s, f(o, "wh_in0", 5) * mm, f(o, "wh_in1", 15) * mm) * sm(s, s_tl - f(o, "wh_out0", 8) * mm, s_tl - f(o, "wh_out1", 18) * mm)
               for s in sa]
    a_l = ltot - s_tl
    w_ember = [sm(ltot - s, f(o, "em_in0", 9) * mm, f(o, "em_in1", 19) * mm) * sm(ltot - s, a_l - f(o, "em_out0", 8) * mm, a_l - f(o, "em_out1", 20) * mm)
               if s > s_tl else 0.0 for s in sa]

    def ribbon(nm, wts, strength, col, grp, recv, s0, s1, dk=1.0):
        ks = [k for k in range(nt) if s0 <= sa[k] <= s1]
        if not ks or max(wts[k] for k in ks) < 1e-3:
            return None
        A, B, W = [], [], []
        for k in ks:
            i = order[k]
            Pp, Nn = bevel_point(thr[i], tn[i], phi)
            r = mirror(Pp, Nn)
            E = Pp + r * ed * dk
            q1, q0 = thr[order[min(k + 2, nt - 1)]], thr[order[max(k - 2, 0)]]
            t_ = Vector((q1[0] - q0[0], q1[1] - q0[1], 0.0)).normalized()
            bv = r.cross(t_).normalized()
            A.append(tuple(E - bv * ew * dk / 2))
            B.append(tuple(E + bv * ew * dk / 2))
            W.append(wts[k])
        rb = L.weighted_ribbon(nm, A, B, W, strength, color=col, soft_v=0.2, group=grp)
        L.link_only(rb, recv, nm + "_recv")
        return rb

    # one ribbon piece per lip segment, overlapping its neighbours by 1.5 mm, linked to that segment only
    segb = [b_ * mm for b_ in L.THROAT_SEGS] + [ltot]
    for i_ in range(len(L.THROAT_SEGS)):
        lo_, hi_ = segb[i_] - 3 * mm, segb[i_ + 1] + 3 * mm
        recv = [head["thr%02d" % i_]]
        # neighbouring pieces overlap, so they sit at alternating distances (same angular size): two coincident
        # transparent emitters would hide each other from a glossy ray
        dk = 1.0 + 0.05 * (i_ % 2)
        ribbon("lg_edge%02d" % i_, w_white, f(o, "edge", 150.0), (0.95, 0.97, 1.0), "edge", recv, lo_, hi_, dk)
        ribbon("lg_ember%02d" % i_, w_ember, f(o, "ember", 220.0) * (f(o, "white_ember", WHITE_EMBER) if white else
                                                                    f(o, "p_ember", P_EMBER) if pace else 1.0),
               (0.95, 0.97, 1.0) if (white or pace) else EMBER, "ember", recv, lo_, hi_, dk * 1.025)

    # ---------------- wall: light falling into the throat just under the bridge lip; the wall material's depth
    # occlusion takes it down to near black at the bottom of the opening (a through-opening, not a dish)
    Pw = Vector((0.0, yb, ZT - f(o, "wall_depth", 0.005)))
    wl = studio.area_light("lg_wall", (0.0, yb - f(o, "wall_back", 0.022), ZT + f(o, "wall_up", 0.05)), f(o, "wall_len", 0.09),
                           f(o, "wall", 0.8), color=(0.95, 0.97, 1.0), size_y=f(o, "wall_th", 0.010), target=tuple(Pw))
    wl.lightgroup = "wall"
    L.link_only(wl, [head["bridgewall"]], "wall_recv")

    # ---------------- rim (v14, asymmetric): the left wall (ember side) gets one crisp top-edge line and no fill; the
    # right wall a long soft gradient card and a quieter line
    out_ = C.outline_canon()
    if racket._area(out_) < 0:
        out_.reverse()
    on = L._normals(out_, 2)
    from mathutils import Matrix
    for side in (1, -1):
        yr = f(o, "rim_y", -0.128)
        cand = [i for i, p in enumerate(out_) if p[0] * side > 0 and abs(p[1] - yr) < 0.002]
        i = cand[len(cand) // 2]
        p = out_[i]
        n_ = on[i]
        Pr, nr_ = bevel_point(p, n_, math.radians(f(o, "rim_phi", 55.0)))
        er = mirror(Pr, nr_)
        q = out_[(i + 8) % len(out_)]
        t_ = Vector((q[0] - p[0], q[1] - p[1], 0)).normalized()
        st = K.plane("lg_rim%+d" % side, (f(o, "rim_len", 0.5), f(o, "rim_w", 0.012)), tuple(Pr + er * f(o, "rim_d", 0.6)),
                     normal_to=tuple(Pr))
        zax = (Pr - st.location).normalized()
        xax = (t_ - t_.dot(zax) * zax).normalized()  # long axis along the edge: the line follows the outline
        yax = zax.cross(xax)
        st.rotation_euler = Matrix((xax, yax, zax)).transposed().to_euler()
        rs_ = f(o, "rim", 8.0) * (f(o, "rim_r", 0.45) if side > 0 else f(o, "rim_l", 1.0))

        def rfn(nb, s_=rs_):
            u, v, _ = nb.coords("UV")
            return nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.2), nb.smooth(u, 1.0, 0.8)), s_)

        st.data.materials.append(K.emitter_mat(st.name + "Mat", (0.95, 0.97, 1.0), rfn, additive=True))
        K.visibility(st, camera=False, diffuse=True, glossy=True, shadow=False)
        st.lightgroup = "rim"
        L.link_only(st, RIM, st.name + "_recv")

    # the right wall's long soft gradient (a broad card mirrored in its flat 38 mm side, fading along it)
    yr = f(o, "side_y", -0.140)
    cand = [i for i, p in enumerate(out_) if p[0] > 0 and abs(p[1] - yr) < 0.002]
    i = cand[len(cand) // 2]
    p = out_[i]
    n_ = on[i]
    Pw2 = Vector((p[0], p[1], 0.0))
    ew2 = mirror(Pw2, (n_[0], n_[1], 0.0))
    sp = L.panel("lg_side", tuple(Pw2 + ew2 * f(o, "side_d", 0.45)), (f(o, "side_w", 0.9), f(o, "side_h", 0.40)),
                 f(o, "side", 0.30), tuple(Pw2), color=(0.93, 0.96, 1.0), roll=90.0,
                 edge=(f(o, "side_e0", -0.6), f(o, "side_e1", 1.0)), fade=(0, 0.95), group="rim")
    L.link_only(sp, RIM, "side_recv")
    # ... continued down the neck's right side wall by a second soft card (the gradient runs out of frame)
    yr = f(o, "side2_y", -0.172)
    cand = [i for i, p in enumerate(out_) if p[0] > 0 and abs(p[1] - yr) < 0.002]
    i = cand[len(cand) // 2]
    p = out_[i]
    n_ = on[i]
    sz = ZT * L.neck_scale(p[1], C.NECK_TAPER)[0]
    Pn2 = Vector((p[0], p[1], 0.0))
    en2 = mirror(Pn2, (n_[0], n_[1], 0.0))
    sp2 = L.panel("lg_side2", tuple(Pn2 + en2 * f(o, "side2_d", 0.40)), (f(o, "side2_w", 0.6), f(o, "side2_h", 0.30)),
                  f(o, "side2", 0.22), tuple(Pn2), color=(0.93, 0.96, 1.0), roll=90.0,
                  edge=(f(o, "side2_e0", -0.6), f(o, "side2_e1", 1.0)), fade=(0, 0.95), group="rim")
    L.link_only(sp2, RIM, "side2_recv")

    # ---------------- grip: the overgrip's finishing band at the bottom edge. A dim strip from camera-left rakes it,
    # so the band's cut edge and the first wrap read as tape (a black grip that renders grey means too much light)
    Gc = Vector((0.0, f(o, "grip_y", -0.180), ZT * C.NECK_TAPER[2]))
    ga = math.radians(f(o, "grip_az", -70.0))
    gdir = (fwd * math.cos(ga) + fwd.cross(up) * math.sin(ga)) * math.cos(math.radians(f(o, "grip_el", 35.0))) \
        + up * math.sin(math.radians(f(o, "grip_el", 35.0)))
    gl_ = studio.area_light("lg_grip", tuple(Gc + gdir.normalized() * f(o, "grip_d", 0.25)), f(o, "grip_w", 0.02),
                            f(o, "grip", 0.6), color=(0.95, 0.97, 1.0), size_y=f(o, "grip_len", 0.30), target=tuple(Gc))
    gl_.lightgroup = "grip"
    L.link_only(gl_, [head["grip"]], "grip_recv")

    # ---------------- white Command: a soft spot pool from the upper left of the frame (toward the head) and a weak
    # fill from the front right, on the head parts only (canon lighting note 8: white needs real diffuse light; the
    # reflection groups above are graded down for it in comp, see WHITE_GAINS)
    if white:
        HEADP = [head[k_] for k_ in head if k_ not in ("grip", "cap", "capmark")]
        # the same pool twice: "pool" on the face, edges, bores, throat and neck; "poolw" on the 38 mm side walls
        # only (graded separately: at full strength the pool grazes the left wall and its twill relief turns busy)
        for g_, recv_ in (("pool", [ob for ob in HEADP if ob is not head["wall"]]), ("poolw", [head["wall"]])):
            pl = studio.spot_light("lw_" + g_, (f(o, "pool_x", POOL["pool_x"]), f(o, "pool_y", POOL["pool_y"]),
                                                f(o, "pool_z", POOL["pool_z"])),
                                   f(o, "pool", 95.0), f(o, "pool_deg", POOL["pool_deg"]), blend=1.0, color=(1.0, 0.985, 0.97),
                                   target=(f(o, "pool_tx", POOL["pool_tx"]), f(o, "pool_ty", POOL["pool_ty"]), 0.0),
                                   radius=f(o, "pool_r", 0.06))
            pl.lightgroup = g_
            L.link_only(pl, recv_, g_ + "_recv")
        fl = studio.area_light("lw_fill", (f(o, "fill_x", 0.45), f(o, "fill_y", -0.30), f(o, "fill_z", 0.50)), 1.0,
                               f(o, "fill", 0.8), color=(0.94, 0.96, 1.0), target=(0.0, -0.03, 0.0))
        fl.lightgroup = "fill"
        L.link_only(fl, HEADP, "fill_recv")
        # the clear coat on white: the black-carbon sweeps above barely read over a white base, so white gets its own
        # GLOSSY-ONLY reflections (no diffuse wash): "sheen", a big softbox whose reflection is a half-plane with a
        # crisp edge along the frame line (sh_u1, sh_v1) -> (sh_u2, sh_v2) (the lacquer lifts on one side of it), and
        # "wline", one crisp gloss line beside that edge
        As, _ = face_point(f(o, "sh_u1", 0.0), f(o, "sh_v1", 0.42))
        Bs, _ = face_point(f(o, "sh_u2", 1.0), f(o, "sh_v2", 0.08))
        Csh, _ = face_point(0.6, 0.25)
        shp, _ = face_point(f(o, "sh_pu", 0.75), f(o, "sh_pv", 0.10))
        sh = L.sky_projected("lw_sheen", cam_loc, ZT, As, Bs, Csh, (4.0, 4.0), f(o, "sh_d", 1.1), f(o, "sh_s0", 0.0),
                             f(o, "sh_s1", -0.004), f(o, "sheen", 3.0), pool=(shp.x, shp.y, f(o, "sh_r0", 0.04), f(o, "sh_r1", 0.20)),
                             color=(0.95, 0.97, 1.0), group="sheen")
        K.visibility(sh, camera=False, diffuse=False, glossy=True, shadow=False)
        L.link_only(sh, FACE, "sheen_recv")
        wl_ = L.sky_projected("lw_line", cam_loc, ZT, As, Bs, Csh, (4.4, 4.4), f(o, "wl_d", 1.5), 0.0, 0.0, f(o, "wline", 20.0),
                              pool=(shp.x, shp.y, f(o, "sh_r0", 0.04), f(o, "sh_r1", 0.20)), color=(0.95, 0.97, 1.0),
                              group="wline", band=(f(o, "wl_off", -0.010), f(o, "wl_w", 0.0012)))
        K.visibility(wl_, camera=False, diffuse=False, glossy=True, shadow=False)
        L.link_only(wl_, FACE, "wline_recv")

    # ---------------- report key points in frame coordinates
    def fc(p):
        v = world_to_camera_view(sc, cam, Vector(p))
        return (round(v.x, 3), round(1 - v.y, 3))

    apex_y = float(ys[np.abs(xs) < 0.004].min())
    corner = thr[int(np.argmax(np.where(ys > yb - 0.006, xs, -1)))]
    lines = etch_lines(o)
    print("frame (x, y from top): bridge", fc((0, yb, ZT)), "apex", fc((0, apex_y, ZT)),
          "corner R", fc((corner[0], corner[1], ZT)), "corner L", fc((-corner[0], corner[1], ZT)))
    print("serial", fc((0, lines[0][2] + lines[0][1] / 2, ZT)), fc((0, lines[0][2] - lines[0][1] / 2, ZT)),
          "brand", fc((0, lines[1][2], ZT)), "etch box x", fc((etch[1], lines[0][2], ZT)), fc((etch[1] + etch[3], lines[0][2], ZT)))
    hs = []
    for (hx, hy, hr) in C.holes_canon():
        c_ = fc((hx * U, hy * U + hr * U, ZT))
        if -0.2 < c_[1] < 0.4 and 0.0 < c_[0] < 1.0:
            hs.append(c_)
    print("hole tops", sorted(hs))
    yb_frame = [(round(y_, 3), fc((0, y_, ZT * L.neck_scale(y_, C.NECK_TAPER)[0]))) for y_ in (-0.15, -0.17, -0.174, -0.185, -0.19)]
    print("neck centre line", yb_frame)
    pts = [fc((x_, y_, ZT * L.neck_scale(y_, C.NECK_TAPER)[0])) for (x_, y_) in out_[::4]]
    vis = [q for q in pts if 0 <= q[0] <= 1 and 0 <= q[1] <= 1]
    print("outline in frame: x", min(q[0] for q in vis), max(q[0] for q in vis), "y", min(q[1] for q in vis), max(q[1] for q in vis))
    print("throat arc: total %.1f mm, TR %.1f, TL %.1f" % (ltot * 1000, s_tr * 1000, s_tl * 1000))
    if o.get("segdbg"):
        for b_ in L.THROAT_SEGS:
            k = min(range(nt), key=lambda k_: abs(sa[k_] - b_ * mm))
            print("  seg boundary %5.1f mm -> frame" % b_, fc((thr[order[k]][0], thr[order[k]][1], ZT)))
    print("lens %.1f mm, focus %.3f m" % (cd.lens, cd.dof.focus_distance))
    return sc, cam


# ------------------------------------------------------------------ comp
def comp(o, sc, pdir, stem, png, card):
    ps = L.collect_passes(pdir, stem, GROUPS)
    acc = None
    wg = WHITE_GAINS if is_white(o) else P_GAINS if is_pace(o) else {}
    vd = WHITE_VIG if is_white(o) else dict(vig=0.0, vig_r0=0.15, vig_r1=0.85, vig_cx=0.5, vig_cy=0.6, vig_sx=1.0,
                                            vig_sy=1.0, vig_bg=0.5)
    vig = f(o, "vig", vd["vig"])
    bg_ = None
    for g, pth in ps.items():
        a = L.load_lin(pth) * f(o, "g_" + g, wg.get(g, 1.0))
        if g == "bg" and vig > 0:
            bg_ = a   # the graphite backdrop takes only vig_bg of the vignette (the corners stay graphite, not black)
            continue
        acc = a if acc is None else acc + a
    if vig > 0:
        # a soft elliptical vignette on the linear sum (rows bottom-up, as Blender stores them): 1 inside vig_r0,
        # falling by vig at vig_r1 (frame heights from vig_cx / vig_cy, y from the top; x / vig_sx, y / vig_sy)
        h_, w_ = acc.shape[:2]
        yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
        yt = 1.0 - (yy + 0.5) / h_
        cx_, cy_ = f(o, "vig_cx", vd["vig_cx"]), f(o, "vig_cy", vd["vig_cy"])
        dx_ = ((xx + 0.5) / w_ - cx_) * (w_ / h_) / f(o, "vig_sx", vd["vig_sx"])
        dy_ = (yt - cy_) / f(o, "vig_sy", vd["vig_sy"])
        r_ = np.sqrt(dx_ * dx_ + dy_ * dy_)
        r0, r1 = f(o, "vig_r0", vd["vig_r0"]), f(o, "vig_r1", vd["vig_r1"])
        t_ = np.clip((r_ - r0) / (r1 - r0), 0, 1)
        sm_ = (t_ * t_ * (3 - 2 * t_))[..., None]
        acc = acc * (1.0 - vig * sm_)
        if bg_ is not None:
            acc = acc + bg_ * (1.0 - vig * f(o, "vig_bg", vd["vig_bg"]) * sm_)
    L.save_display(acc, png, sc)
    # display-space finish: optional gentle edge floor so no corner is flat black (fill rule)
    lift = o.get("lift")
    bloom = o.get("bloom", "0.80,0.18,0.006")
    bl = tuple(float(v) for v in str(bloom).split(",")) if bloom and str(bloom) != "0" else None
    if lift or bl:
        K.finish_png(png, png, floor_hex=str(lift) if lift else None, floor_band=f(o, "lift_band", 0.12), bloom=bl)
    from PIL import Image
    if o.get("crop"):
        return
    im = Image.open(png)
    w, h = im.size
    outs = [png]
    for nm, (cx, cy, cw, ch) in CROPS.items():
        dst = crop_path(png, nm)
        im.crop((int(round(cx * w)), int(round(cy * h)), int(round((cx + cw) * w)), int(round((cy + ch) * h)))).save(dst)
        outs.append(dst)
    fc_ = os.path.join(ROOT, "fillcheck.py")
    r = subprocess.run([sys.executable, fc_] + outs, capture_output=True, text=True)
    print(r.stdout.strip())


def sheet(o, sc, pdir, stem):
    """Contact sheet: every light group alone (gain 1, or --g_<group>), each through the view transform."""
    from PIL import Image, ImageDraw
    ps = L.collect_passes(pdir, stem, GROUPS)
    tiles = []
    for g in GROUPS:
        if g not in ps:
            continue
        t = os.path.join(pdir, stem + "__sheet_" + g + ".png")
        L.save_display(L.load_lin(ps[g]) * f(o, "g_" + g, 1.0), t, sc)
        im = Image.open(t).convert("RGB")
        im.thumbnail((640, 360))
        ImageDraw.Draw(im).text((8, 6), g, fill=(255, 120, 60))
        tiles.append(im)
    w, h = tiles[0].size
    out = Image.new("RGB", (w * 3, h * ((len(tiles) + 2) // 3)), (40, 0, 0))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % 3) * w, (i // 3) * h))
    dst = os.path.join(studio.OUT, "k10", stem + "_sheet.png")
    out.save(dst)
    print("sheet", dst)


def main():
    o = parse_args()
    t0 = time.time()
    png, card, pdir, stem = paths(o)
    if o.get("sheet"):
        sc = studio.reset()
        sheet(o, sc, pdir, stem)
        return
    if o.get("comp"):
        sc = studio.reset()
        comp(o, sc, pdir, stem, png, card)
        print("comp", png, round(time.time() - t0, 1), "s")
        return
    sc, cam = build(o)
    if o.get("crop"):
        x0, x1, y0, y1 = [float(v) for v in str(o["crop"]).split(",")]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
    L.setup_passes(sc, GROUPS, pdir, stem)
    sc.render.filepath = os.path.join(pdir, stem + "__composite.png")
    sc.render.image_settings.file_format = "PNG"
    print("built", round(time.time() - t0, 1), "s")
    if o.get("dry"):
        return
    bpy.ops.render.render(write_still=True)
    print("rendered", round(time.time() - t0, 1), "s")
    comp(o, sc, pdir, stem, png, card)
    print("wrote", png, card, round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
