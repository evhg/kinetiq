"""K05-laser-scan (v6, 2026-10-22): the canonical racket face-up on a polished black granite surface plate, scanned by
a red laser line. Precision chapter: K05 (desktop, full-bleed) and K05-phone (portrait), both from one master render.

v6 (the art director's critique of v5, fixes 1-9; WHITE_DEFAULTS holds every value, --white 0 still gives v4's black):
- Key: the spot pool moves from the wide frame's upper left to its upper right (lamp 0.55, 0.72, 0.80; 23 deg aimed at
  0.22, -0.09 past the tip), so its soft edge runs beside the laser on the crown side. The crown and tip are lit (luma
  about 190), the line lies in the falloff (face 130-150 beside it), the throat side rests in a 11 W fill (about 100).
  The phone, a CCW rotation of the master, is therefore lit from its upper left with the crown at the top in light.
- lg_face: a glossy-only band designed on the face (gloss_strip): 22 mm wide, near-vertical in the wide frame (87 deg,
  25 deg off the laser), between the V and the hole field, from 70 mm off the laser to the top rim, with a honeycomb grid
  (fb_tol) so only the coat and the fibre flip inside the band see it: luma about 228, the twill visible inside it.
  lg_lips: the same softbox for the hole lips only (a crescent on every hole). The serial rake is off on white.
- lw_wall: a camera-side card on the 38 mm wall and its rims: the near wall reads 107-134 against a face of 170-175.
- Holes: lg_holes lights a hidden stone patch under the hole field (shadow-linked, diffuse only): stone at 23-29 with
  grain in every hole (raising lg_under lit the whole plate and left the holes black: the polish mirrors the racket).
- Laser: see-through emission tubes (never darker than the face), 6 profiles at tau 7 mm, the core's paler colour for
  camera rays only, a compositor tint toward the laser round the line (tint), laser 22: halo G/R 0.59-0.65 on white,
  plate core about (220, 85, 60). The line runs off the frame at both ends (t_lo -0.40, t_hi 0.45).
- Plate: stone spill halved (80), the overhead sheen and lg_under dimmer: 23-28 beside the head, 15-17 at the edges,
  about 20 behind the numeral. Cap: a larger, dimmer softbox (0.45 x 0.30 m, 0.6 W): the Q reads as an engraved glint.

v5 (owner, 2026-10-22: Command is WHITE carbon, the logo is the Q): the racket is kq_canon's white 3K twill Command
(the K04/K10 k04_tex2 maps, resolved at about 10 px per 2.6 mm tow in the 3200 px final) and its cap carries the
engraved Q. White carbon is lit by real diffuse light, not by v4's reflections only (WHITE_DEFAULTS, canon.md note 8):
- lw_pool: a soft 16 deg spot from above the frame's upper left, head parts only: white at about luma 205 on the lit
  upper side of the head falling to about 100 in the shade toward the tip, so the face is a gradient, not a flat plate.
- lw_fill: a weak 1 m fill from the camera side: the shade stays white-in-shadow and the near wall reads.
- lw_stone: the same lamp's wider spill on the granite only, diffuse only (no hot spot or mica sparkle in the polish):
  the stone lifts in a soft pool and the racket casts its own soft shadow down-right, so it sits on the plate.
- lg_face (v4's clearcoat stripe) is off: on white its diffuse wash flattened the gradient and its gloss line showed
  only in the shade as a short dash. The rim ring is dimmer and peaks top-left (rim 8, floor 0.15).
- The laser on white: a red core (no white-hot core, which vanished into the white), 0.16 mm line, a stronger red halo,
  and a little real red scatter on the face round it (laser_indirect 0.25); the measured-profile wake is laser-tinted.
- Granite mosaic 0.6 (was 0.8): under the stone pool the crystal tones would otherwise read as grey terrazzo.
--white 0 renders the previous black Command with v4's lights exactly.

v4 (render audit, section 4): the shot's own head and K05 handle are gone. The racket is kq_canon.build_racket(
feel="command", serial="KQ-000427"): 455.0 mm (was 462.3), the crown of 8 + 34 holes (was the old hex grid), the 1.5 mm
edge with the K04/K10 twill folding over it onto the 38 mm wall (was a 9.5 mm satin bumper, which read as a frame tube),
no printed KINETIQ on the face, the one-piece neck into K05's overgrip and satin cap (engraved Q since v5) (no ferrule).
The throat carries the laser-frosted KQ-000427 (optional on a single racket; a quiet rake makes it legible).
Granite: half as many and half as bright feldspar flecks, fine grains and mica flakes as v3 (they read as a starfield),
on a crystal mosaic whose sheen varies per crystal, so the plate reads as stone. Lights are linked per canon part.

The laser is a real tilted light sheet: rays from the projector are cast against the racket and the plate, so the line
stays straight on the face, steps down into every hole it crosses, rolls over the frame edge and lands on the granite
offset by the 38 mm height (laser triangulation). Each hit carries a cosine falloff for grazing incidence (steep walls
read as the line dropping away, not as drawn ticks) and laser speckle (+-20 % on carbon, more on granite). It is a thin
emissive tube whose centre runs near-white (#fff1ea) inside the #ff3a1e; the halo is a tight red glow composited from
the laser's light group only. Behind it the profiles already measured remain as thin desaturated polylines that fade
fast with age, so the tip half shows bare carbon. (Unchanged from v3.)

Lighting (every emitter camera-invisible, see-through and light-linked):
- lg_ambient: overhead radial disc over the racket's mirror point, plate only: the centred radial sheen.
- lg_base: very wide dim disc, plate only, so no corner falls to flat black (fill rule).
- lg_under: a weak disc for the plate that the racket does not shadow (shadow linking): granite shows through every hole.
- lg_face: one clearcoat stripe along the head, linked to face, neck, holes and throat only (no floor: deep black off it).
- lg_rim: an annular band at 35 deg, linked to the 1.5 mm rim and the neck: one continuous hairline outline.
- lg_grip / lg_grip2: strips along the grip (grip, cap, K); lg_cap: a softbox in the cap band's mirror direction.
- lg_rake: K10's grazing rake for the frosted throat serial (--rake 0 drops it).

Framing (unchanged from v3): one master render covers the desktop 16:9 frame AND a centred portrait frame for phones
(racket vertical, handle down), so both crops come from the same samples:
  <out>.png (3200x1800 desktop crop), <out>-phone.png (portrait, rotated), <out>-master.png.
Usage: K05-laser-scan.py --w 960 --h 540 --spp 32 --out K05_prev   (--w/--h are the DESKTOP size; the master is taller)
Final: flock render.lock ../bpyenv/bin/python shots/K05-laser-scan.py --w 3200 --h 1800 --spp 160 --out final/K05-laser-scan
  (v6: about 50 min; writes final/K05-laser-scan.png, -phone.png, -master.png)
Dev flags: --norender, --measure, --crop x0,x1,y0,y1, --solo lg_x, --glow f, --laser f, --lw m, --amb f, --base f,
--under f, --face f, --face_lo f, --rim f, --rim_w m, --rim_floor f, --grip f, --cap f, --rake f, --t_hi m,
--fleck_n f, --fleck_b f (v3 = 1, 1), --mosaic f, --spec_var f, --serial s,
v5 (white): --white 0|1, --wpool W, --wp_x/--wp_y/--wp_z/--wp_tx/--wp_ty m, --wp_deg d, --wfill W, --wstone W, --ws_deg d,
--core r,g,b, --core_pow f, --pcol r,g,b, --laser_indirect f.
"""
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import racket  # noqa: E402
import studio  # noqa: E402
import kq_canon as C  # noqa: E402


OPT = {}

# v5 (owner, 2026-10-22): Command is WHITE carbon. Black carbon is lit by reflections only; white needs real diffuse
# light (canon.md lighting note 8): a soft spot pool for the gradient, a weak fill so the shade stays white-in-shadow,
# the reflection cards kept to thin gloss lines. These defaults apply when the racket is white (CLI flags still win);
# --white 0 renders the previous black Command with v4's lights exactly.
WHITE_DEFAULTS = dict(wpool=180.0, wp_deg=23.0, wp_x=0.55, wp_y=0.72, wp_z=0.80, wp_tx=0.22, wp_ty=-0.09, wfill=11.0,
                      wp_plate=0, rake=0.0, core="1.0,0.22,0.12", laser_indirect=0.25, pcol="1.0,0.15,0.08", pts=5.0,
                      face=120.0, fb_w=0.022, fb_tol=2.6, lips=120.0, rim=8.0, rim_floor=0.15, wstone=80.0, lw=0.00016, glow=1.8, mosaic=0.6, laser=22.0,
                      under=0.25, holefloor=55.0, core_cam_only=1, hf_x0=-0.075, tint=4.0, tint_r=0.006, tint_max=0.75, amb=0.30, prad=0.40, pool_y=-0.07, base=0.6, ws_deg=30.0, ws_ty=-0.08, wall=6.5, nprof=6, ptau=0.007, t_lo=-0.40, t_hi=0.45, fade_lo=0.06, fade_hi=0.06,
                      cap=0.6, cap_w=0.45, cap_h=0.30)
# v6 (art director's critique, 2026-10-22), every change a default above or a block below:
#  1 trail: see-through emission tubes (never darker than the face), 6 profiles, tau 7 mm
#  2 lg_face: a glossy-only reflection band designed on the face (gloss_strip), clear of the laser and the serial
#  3 lw_wall: a camera-side card on the 38 mm wall, so the wall reads as white wall in shade, not a black bumper
#  4 stone through every hole: lg_holes, a diffuse-only light on a hidden stone patch under the hole field (raising
#    lg_under as asked lit the whole plate, +15 luma, and still left the holes at 0-2: the polished plate under a hole
#    mirrors the racket's own back face, and its diffuse albedo is about 0.005)
#  5+6 the key pool moves from the wide frame's upper left to its upper right, over the crown: the phone (a CCW
#    rotation) is then lit from its upper left, and the laser line lies in the pool's falloff, so it reads red
#  7 the line runs off the frame at both ends; 8 the stone spill halves; 9 a larger, dimmer cap softbox

# Pace (Release 2 feel toggle, 2026-10-23): --feel pace builds the canon Pace (kq_canon.PACE v6, black 12K) on the same
# plate, camera, laser, crops and composition. Only the face follows the feel: the plate, laser, profiles, handle and
# cap keep every WHITE_DEFAULTS value (the v6 environment), and so does the racket rig (the glossy-only coat band, rim
# ring, wall card), which on black carbon draws the lacquer band and hairlines. PACE_DEFAULTS (applied first; CLI flags
# still win) add the Pace recipe of K08 / K11 / K01: an off-specular weave card only the 12K's fibre lobes see
# (pweave, so the tapes read instead of a black hole), an indirect clamp (pclamp) against fireflies, and per-light
# Pace values. Default feel "command" leaves every Command output identical.
# Tuned on previews (out/pr2/k05p_*): the white rig's coat band (face 120) blew out on black; face 6 gives one crisp
# lacquer band. The weave card at 20 deg / 1.6 m wide was seen by the coat (a grey wash, a hard checker); at 25 deg,
# 1.2 x 0.8 m, 1.6 W only the fibre lobes catch it: the tapes read over the crown, the rest stays deep black.
# Fill rule: the white face carried most of the frame's lit pixels (Command lit 15 %); with the black face the v6 plate
# gave lit 3 %. The plate's sheen and stone pool are lifted toward v4's black-carbon plate (amb 0.30 -> 1.35, base 0.6
# -> 0.8, wstone 80 -> 260): graphite stone round a black racket, lit 12-14 % (out/pr2/k05p_a135).
PACE_DEFAULTS = dict(face=6.0, lips=30.0, pweave=1.6, pw_up=25.0, pw_d=1.3, pw_w=1.2, pw_h=0.8, pclamp=4.0,
                     amb=1.35, base=0.8, wstone=260.0)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 960, "h": 540, "spp": 32, "out": "K05_prev"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            o[k] = v
            i += 1
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
    return o


def out_path(name):
    p = name if name.endswith(".png") else name + ".png"
    if not os.path.isabs(p):
        p = os.path.join(studio.OUT, p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def _n(nodes, kind, op=None):
    n = nodes.new(kind)
    if op:
        n.operation = op
    return n


LASER = (1.0, 0.0423, 0.0130)   # #ff3a1e in linear
T = racket.THICK


# ------------------------------------------------------------------ granite (v4: half the flecks)


def mat_granite(name="Granite"):
    """Polished black granite: near-black ground, pale feldspar flecks (light grey on black), sparse metallic mica
    flakes tilted only a few degrees (they catch the overhead softbox and sparkle), roughness about 0.1 so the plate
    mirrors a dim structured reflection of the softbox, the frame and the laser.
    v4 (render audit): v3's flecks read as a starfield at page size, so the pale feldspar cells, the fine pale grains
    and the mica flakes are all half as many (fleck_n 0.5) and half as bright (fleck_b 0.5) as v3."""
    dens = float(OPT.get("fleck_n", 0.5))     # v3 = 1.0
    brt = float(OPT.get("fleck_b", 0.35))     # v3 = 1.0 (0.5 still read as dust specks at 1:1)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    b = nodes["Principled BSDF"]
    tc = nodes.new("ShaderNodeTexCoord")
    v1 = nodes.new("ShaderNodeTexVoronoi")
    v1.inputs["Scale"].default_value = 900.0  # grains about 1 mm
    v1.inputs["Randomness"].default_value = 1.0
    links.new(tc.outputs["Object"], v1.inputs["Vector"])
    v2 = nodes.new("ShaderNodeTexVoronoi")
    v2.inputs["Scale"].default_value = 2600.0  # fine grain
    links.new(tc.outputs["Object"], v2.inputs["Vector"])
    nz = nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 350.0
    nz.inputs["Detail"].default_value = 6.0
    links.new(tc.outputs["Object"], nz.inputs["Vector"])
    sepc = nodes.new("ShaderNodeSeparateColor")
    links.new(v1.outputs["Color"], sepc.inputs["Color"])
    sep2 = nodes.new("ShaderNodeSeparateColor")
    links.new(v2.outputs["Color"], sep2.inputs["Color"])
    # feldspar: ~10 % x dens of the coarse cells pale, graded; a sprinkle of fine pale grains (2.5 % x dens)
    sp = _n(nodes, "ShaderNodeMapRange")
    sp.inputs["From Min"].default_value = 1.0 - 0.10 * dens
    sp.inputs["From Max"].default_value = 1.0 - 0.01 * dens
    links.new(sepc.outputs["Red"], sp.inputs["Value"])
    sp2 = _n(nodes, "ShaderNodeMapRange")
    sp2.inputs["From Min"].default_value = 1.0 - 0.025 * dens
    sp2.inputs["From Max"].default_value = 1.0
    sp2.inputs["To Max"].default_value = 0.4
    links.new(sep2.outputs["Red"], sp2.inputs["Value"])
    spm = _n(nodes, "ShaderNodeMath", "MAXIMUM")
    links.new(sp.outputs["Result"], spm.inputs[0])
    links.new(sp2.outputs["Result"], spm.inputs[1])
    gr = _n(nodes, "ShaderNodeMapRange")
    gr.inputs["From Min"].default_value = 0.35
    gr.inputs["From Max"].default_value = 0.65
    gr.inputs["To Min"].default_value = 0.0030
    gr.inputs["To Max"].default_value = 0.0065
    links.new(nz.outputs["Fac"], gr.inputs["Value"])
    ground = gr.outputs["Result"]
    mos = float(OPT.get("mosaic", 0.8))
    if mos > 0:
        # v4: an interlocking crystal mosaic with a tone per crystal, so the ground reads as granite grain under the
        # polish rather than a flat black with isolated specks. Two crystal sizes (about 2.6 and 1.1 mm) on
        # domain-warped coordinates, so grain boundaries wander like real crystals (plain Voronoi cells read as CG
        # polygons at 1:1), and a fine mottle inside each crystal
        wn = nodes.new("ShaderNodeTexNoise")
        wn.inputs["Scale"].default_value = float(OPT.get("warp_scale", 420.0))
        wn.inputs["Detail"].default_value = 3.0
        links.new(tc.outputs["Object"], wn.inputs["Vector"])
        wc = _n(nodes, "ShaderNodeVectorMath", "SUBTRACT")
        wc.inputs[1].default_value = (0.5, 0.5, 0.5)
        links.new(wn.outputs["Color"], wc.inputs[0])
        wv = _n(nodes, "ShaderNodeVectorMath", "MULTIPLY_ADD")
        wa = float(OPT.get("warp", 0.0016))
        wv.inputs[1].default_value = (wa, wa, 0.0)
        links.new(wc.outputs[0], wv.inputs[0])
        links.new(tc.outputs["Object"], wv.inputs[2])
        # the flecks and flakes sit on the same warped grain, so they are irregular crystals, not polygon specks
        links.new(wv.outputs[0], v1.inputs["Vector"])
        links.new(wv.outputs[0], v2.inputs["Vector"])
        tones = []
        for sc_, ch in ((float(OPT.get("mos_scale", 380.0)), "Blue"), (float(OPT.get("mos_scale", 380.0)) * 2.4, "Green")):
            vv = nodes.new("ShaderNodeTexVoronoi")
            vv.inputs["Scale"].default_value = sc_
            vv.inputs["Randomness"].default_value = 1.0
            links.new(wv.outputs[0], vv.inputs["Vector"])
            ss = nodes.new("ShaderNodeSeparateColor")
            links.new(vv.outputs["Color"], ss.inputs["Color"])
            tones.append(ss.outputs[ch])
        tm = nodes.new("ShaderNodeMix")
        tm.data_type = "FLOAT"
        tm.inputs["Factor"].default_value = 0.4
        links.new(tones[0], tm.inputs[2])
        links.new(tones[1], tm.inputs[3])
        mn = nodes.new("ShaderNodeTexNoise")
        mn.inputs["Scale"].default_value = 2600.0
        mn.inputs["Detail"].default_value = 2.0
        links.new(tc.outputs["Object"], mn.inputs["Vector"])
        tone = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD")   # tone x (0.75 .. 1.25 mottle)
        mo = _n(nodes, "ShaderNodeMapRange")
        mo.inputs["To Min"].default_value = 0.75
        mo.inputs["To Max"].default_value = 1.25
        links.new(mn.outputs["Fac"], mo.inputs["Value"])
        links.new(tm.outputs[0], tone.inputs[0])
        links.new(mo.outputs["Result"], tone.inputs[1])
        tone.inputs[2].default_value = 0.0
        mr3 = _n(nodes, "ShaderNodeMapRange")
        mr3.clamp = False
        mr3.inputs["To Min"].default_value = 1.0 - mos
        mr3.inputs["To Max"].default_value = 1.0 + 1.6 * mos
        links.new(tone.outputs[0], mr3.inputs["Value"])
        gm = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        links.new(ground, gm.inputs[0])
        links.new(mr3.outputs["Result"], gm.inputs[1])
        ground = gm.outputs[0]
        # each crystal takes the polish a little differently (quartz, feldspar and biotite differ in index and
        # hardness): the sheen varies a little per crystal, a fine salt-and-pepper grain that reads as stone
        sv = float(OPT.get("spec_var", 0.18))
        if sv > 0:
            mr4 = _n(nodes, "ShaderNodeMapRange")
            mr4.clamp = False
            mr4.inputs["To Min"].default_value = 0.5 * (1.0 - sv)
            mr4.inputs["To Max"].default_value = 0.5 * (1.0 + sv)
            links.new(tone.outputs[0], mr4.inputs["Value"])
            links.new(mr4.outputs["Result"], b.inputs["Specular IOR Level"])
    mx = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD")
    mx.inputs[1].default_value = 0.035 * brt
    links.new(spm.outputs[0], mx.inputs[0])
    links.new(ground, mx.inputs[2])
    cmb = nodes.new("ShaderNodeCombineColor")
    links.new(mx.outputs[0], cmb.inputs["Red"])
    links.new(mx.outputs[0], cmb.inputs["Green"])
    mxb = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    mxb.inputs[1].default_value = 1.05
    links.new(mx.outputs[0], mxb.inputs[0])
    links.new(mxb.outputs[0], cmb.inputs["Blue"])
    # mica flakes: a sparse subset of coarse cells (0.25 % x dens), silver metallic, near-mirror, tilted +-4 deg
    gt = _n(nodes, "ShaderNodeMath", "GREATER_THAN")
    gt.inputs[1].default_value = 0.9570
    links.new(sepc.outputs["Green"], gt.inputs[0])
    lt = _n(nodes, "ShaderNodeMath", "LESS_THAN")
    lt.inputs[1].default_value = 0.9570 + 0.0025 * dens
    links.new(sepc.outputs["Green"], lt.inputs[0])
    flc = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(gt.outputs[0], flc.inputs[0])
    links.new(lt.outputs[0], flc.inputs[1])
    cmix = nodes.new("ShaderNodeMixRGB")
    links.new(flc.outputs[0], cmix.inputs["Fac"])
    links.new(cmb.outputs["Color"], cmix.inputs["Color1"])
    fv = 0.4 * brt
    cmix.inputs["Color2"].default_value = (fv, fv, fv * 1.03, 1)
    links.new(cmix.outputs["Color"], b.inputs["Base Color"])
    links.new(flc.outputs[0], b.inputs["Metallic"])
    rr = _n(nodes, "ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = float(OPT.get("gr0", 0.085))
    rr.inputs["To Max"].default_value = float(OPT.get("gr1", 0.12))
    links.new(nz.outputs["Fac"], rr.inputs["Value"])
    rmix = nodes.new("ShaderNodeMix")
    rmix.data_type = "FLOAT"
    links.new(flc.outputs[0], rmix.inputs["Factor"])
    links.new(rr.outputs["Result"], rmix.inputs[2])
    rmix.inputs[3].default_value = 0.05
    links.new(rmix.outputs[0], b.inputs["Roughness"])
    tilt = _n(nodes, "ShaderNodeVectorMath", "MULTIPLY_ADD")
    ta = float(OPT.get("flake_tilt", 0.14))
    tilt.inputs[1].default_value = (ta, ta, 0.0)
    tilt.inputs[2].default_value = (-ta / 2, -ta / 2, 1.0)
    links.new(v1.outputs["Color"], tilt.inputs[0])
    nm = nodes.new("ShaderNodeMix")
    nm.data_type = "VECTOR"
    links.new(flc.outputs[0], nm.inputs["Factor"])
    nm.inputs[4].default_value = (0, 0, 1)
    links.new(tilt.outputs[0], nm.inputs[5])
    nn = _n(nodes, "ShaderNodeVectorMath", "NORMALIZE")
    links.new(nm.outputs[1], nn.inputs[0])
    vt = nodes.new("ShaderNodeVectorTransform")
    vt.vector_type = "NORMAL"
    vt.convert_from = "OBJECT"
    vt.convert_to = "WORLD"
    links.new(nn.outputs[0], vt.inputs["Vector"])
    links.new(vt.outputs["Vector"], b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value = 0.5
    return m


# ------------------------------------------------------------------ lights
def see_through(ob):
    """Emission + Transparent: a light-linked emitter must not occlude the lights other surfaces are linked to
    (a card linked to the racket would otherwise black out the granite's reflection of the overhead disc)."""
    for m in ob.data.materials:
        nt = m.node_tree
        out = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputMaterial")
        src = out.inputs["Surface"].links[0].from_socket
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        ad = nt.nodes.new("ShaderNodeAddShader")
        nt.links.new(src, ad.inputs[0])
        nt.links.new(tr.outputs[0], ad.inputs[1])
        nt.links.new(ad.outputs[0], out.inputs["Surface"])
    ob.visible_shadow = False
    return ob


def disc_softbox(name, centre, radius, strength, color=(1, 1, 1), power=1.6):
    """Face-down emissive disc (camera-invisible), brightest at its centre, radial falloff to 0 at the rim."""
    bpy.ops.mesh.primitive_circle_add(vertices=128, radius=radius, fill_type="NGON", location=centre)
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_euler = (math.pi, 0, 0)
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    tc = nodes.new("ShaderNodeTexCoord")
    ln = _n(nodes, "ShaderNodeVectorMath", "LENGTH")
    links.new(tc.outputs["Object"], ln.inputs[0])
    mr = _n(nodes, "ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHERSTEP"
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = radius
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    links.new(ln.outputs["Value"], mr.inputs["Value"])
    pw = _n(nodes, "ShaderNodeMath", "POWER")
    pw.inputs[1].default_value = power
    links.new(mr.outputs["Result"], pw.inputs[0])
    st = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    st.inputs[1].default_value = strength
    links.new(pw.outputs[0], st.inputs[0])
    links.new(st.outputs[0], em.inputs["Strength"])
    links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    ob.visible_camera = False
    return ob


def ring_strip(name, centre, radius, height, width, strength, color=(1, 1, 1), peak_az=None, floor=1.0):
    """Annular band of light around the racket at a given elevation (camera-invisible): the rounded frame edge
    mirrors it as a continuous outline while the flat face never sees it. Optional azimuth emphasis."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=radius, depth=width, end_fill_type="NOTHING",
                                        location=(centre[0], centre[1], height))
    ob = bpy.context.active_object
    ob.name = name
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    acc = None
    if peak_az is not None:
        tc = nodes.new("ShaderNodeTexCoord")
        sep = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tc.outputs["Object"], sep.inputs["Vector"])
        at = _n(nodes, "ShaderNodeMath", "ARCTAN2")
        links.new(sep.outputs["Y"], at.inputs[0])
        links.new(sep.outputs["X"], at.inputs[1])
        sb = _n(nodes, "ShaderNodeMath", "SUBTRACT")
        sb.inputs[1].default_value = math.radians(peak_az)
        links.new(at.outputs[0], sb.inputs[0])
        cs = _n(nodes, "ShaderNodeMath", "COSINE")
        links.new(sb.outputs[0], cs.inputs[0])
        mr = _n(nodes, "ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = -1
        mr.inputs["To Min"].default_value = floor
        links.new(cs.outputs[0], mr.inputs["Value"])
        st = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        st.inputs[1].default_value = strength
        links.new(mr.outputs["Result"], st.inputs[0])
        links.new(st.outputs[0], em.inputs["Strength"])
    else:
        em.inputs["Strength"].default_value = strength
    links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    ob.visible_camera = False
    return ob


def look_at(ob, loc, tgt, up=(0.0, 1.0, 0.0)):
    """Orientation with an explicit world up (studio.aim rolls freely when looking along Z); local Y follows `up`."""
    fwd = (Vector(tgt) - Vector(loc)).normalized()
    rt = fwd.cross(Vector(up)).normalized()
    upv = rt.cross(fwd)
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ Matrix((rt, upv, -fwd)).transposed().to_4x4()


def link_to(light, receivers, name):
    col = bpy.data.collections.new(name)
    for r in receivers:
        col.objects.link(r)
    light.light_linking.receiver_collection = col


def sweep_card(name, loc, size, strength, angle, edge=(0.3, 0.7), lo=0.0, color=(1, 1, 1), band=None):
    """Face-down emissive card (camera-invisible) with a smooth linear ramp from `lo` to 1 across a direction at
    `angle` degrees in the card plane: a lacquered face mirrors it as one soft diagonal light sweep."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    ob.rotation_euler = (math.pi, 0, 0)
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    tc = nodes.new("ShaderNodeTexCoord")
    dp = _n(nodes, "ShaderNodeVectorMath", "DOT_PRODUCT")
    a = math.radians(angle)
    dp.inputs[1].default_value = (math.cos(a) * size[0], math.sin(a) * size[1], 0.0)
    links.new(tc.outputs["Object"], dp.inputs[0])
    mr = _n(nodes, "ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    span = abs(math.cos(a) * size[0]) / 2 + abs(math.sin(a) * size[1]) / 2
    mr.inputs["From Min"].default_value = -span + 2 * span * edge[0]
    mr.inputs["From Max"].default_value = -span + 2 * span * edge[1]
    mr.inputs["To Min"].default_value = lo
    mr.inputs["To Max"].default_value = 1.0
    links.new(dp.outputs["Value"], mr.inputs["Value"])
    res = mr.outputs["Result"]
    if band:
        # a soft stripe instead of a half-plane: falls again over band = (from, to) in the same 0..1 span units
        b2 = _n(nodes, "ShaderNodeMapRange")
        b2.interpolation_type = "SMOOTHSTEP"
        b2.inputs["From Min"].default_value = -span + 2 * span * band[0]
        b2.inputs["From Max"].default_value = -span + 2 * span * band[1]
        b2.inputs["To Min"].default_value = 1.0
        b2.inputs["To Max"].default_value = lo
        links.new(dp.outputs["Value"], b2.inputs["Value"])
        bm_ = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        links.new(res, bm_.inputs[0])
        links.new(b2.outputs["Result"], bm_.inputs[1])
        res = bm_.outputs[0]
    st = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    st.inputs[1].default_value = strength
    links.new(res, st.inputs[0])
    links.new(st.outputs[0], em.inputs["Strength"])
    links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    ob.visible_camera = False
    return ob


# ------------------------------------------------------------------ ray casting
class Scene3D:
    """BVH ray casts against several objects in world space."""

    def __init__(self, objs):
        dg = bpy.context.evaluated_depsgraph_get()
        self.items = []
        for ob in objs:
            ev = ob.evaluated_get(dg)
            me = ev.to_mesh()
            mw = ob.matrix_world.copy()
            verts = [mw @ v.co for v in me.vertices]
            polys = [tuple(p.vertices) for p in me.polygons]
            ev.to_mesh_clear()
            self.items.append((ob, BVHTree.FromPolygons(verts, polys, all_triangles=False)))

    def cast(self, o, d, dist=20.0):
        best = None
        for ob, bvh in self.items:
            loc, nrm, idx, t = bvh.ray_cast(o, d, dist)
            if loc is not None and (best is None or t < best[3]):
                best = (loc, nrm, ob, t)
        return best


# ------------------------------------------------------------------ laser (v3)
def value_noise(n, grain, rnd):
    """Smooth random values along a polyline: knots every `grain` samples, cosine interpolated."""
    nk = n // grain + 3
    kn = [rnd.random() for _ in range(nk)]
    out = []
    for i in range(n):
        f = i / grain
        k = int(f)
        t = f - k
        t = (1 - math.cos(math.pi * t)) / 2
        out.append(kn[k] * (1 - t) + kn[k + 1] * t)
    return out


def laser_tube(name, runs, radius, mat, nseg=6):
    """Thin emissive tube along each run of (point, intensity); per-vertex attribute 'li' carries the intensity."""
    bm = bmesh.new()
    vals = []
    for run in runs:
        pts = [p for (p, _) in run]
        n = len(pts)
        prev = None
        for i, (p, li) in enumerate(run):
            t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)])
            t = t.normalized() if t.length > 1e-9 else Vector((1, 0, 0))
            u = t.cross(Vector((0, 0, 1)))
            if u.length < 1e-6:
                u = t.orthogonal()
            u.normalize()
            w = t.cross(u)
            ring = [bm.verts.new(p + (u * math.cos(2 * math.pi * k / nseg) + w * math.sin(2 * math.pi * k / nseg)) * radius)
                    for k in range(nseg)]
            vals.extend([li] * nseg)
            if prev is not None:
                for k in range(nseg):
                    k2 = (k + 1) % nseg
                    bm.faces.new((prev[k], prev[k2], ring[k2], ring[k]))
            prev = ring
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    at = me.attributes.new("li", "FLOAT", "POINT")
    at.data.foreach_set("value", vals)
    me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    return ob


def mat_laser(name, strength, core=(1.0, 0.88, 0.82), core_pow=3.0):
    """Emission x attribute 'li'; the colour runs from #ff3a1e at the tube's silhouette to a near-white core where it
    faces the camera (the white-hot centre of a laser line)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    lw = nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    inv = _n(nodes, "ShaderNodeMath", "SUBTRACT")
    inv.inputs[0].default_value = 1.0
    links.new(lw.outputs["Facing"], inv.inputs[1])
    pw = _n(nodes, "ShaderNodeMath", "POWER")
    pw.inputs[1].default_value = core_pow
    links.new(inv.outputs[0], pw.inputs[0])
    cm = nodes.new("ShaderNodeMixRGB")
    cm.inputs["Color1"].default_value = (*LASER, 1)
    cm.inputs["Color2"].default_value = (*core, 1)
    lp0 = nodes.new("ShaderNodeLightPath")
    if float(OPT.get("core_cam_only", 0)):
        # v6 (fix 6): the paler core is what the camera sees of the tube only; the light it casts on the face is pure
        # #ff3a1e. Before, the face round the line was lit by the core's colour (G 0.3-0.5) and the halo went pink.
        cf = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        links.new(pw.outputs[0], cf.inputs[0])
        links.new(lp0.outputs["Is Camera Ray"], cf.inputs[1])
        links.new(cf.outputs[0], cm.inputs["Fac"])
    else:
        links.new(pw.outputs[0], cm.inputs["Fac"])
    links.new(cm.outputs["Color"], em.inputs["Color"])
    at = nodes.new("ShaderNodeAttribute")
    at.attribute_name = "li"
    st = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    st.inputs[1].default_value = strength
    links.new(at.outputs["Fac"], st.inputs[0])
    # full strength for the camera; a whisper for everything else, so the line does not light the hole lips it
    # passes into red beads (the plate still mirrors it faintly)
    lp = nodes.new("ShaderNodeLightPath")
    mr = _n(nodes, "ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = float(OPT.get("laser_indirect", 0.04))
    mr.inputs["To Max"].default_value = 1.0
    links.new(lp.outputs["Is Camera Ray"], mr.inputs["Value"])
    s2 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(st.outputs[0], s2.inputs[0])
    links.new(mr.outputs["Result"], s2.inputs[1])
    links.new(s2.outputs[0], em.inputs["Strength"])
    _emit_see_through(nodes, links, em, out)
    return m


def _emit_see_through(nodes, links, em, out):
    """v6 (critique fix 1): Emission + Transparent. An emission-only tube is opaque, so wherever its intensity li falls
    toward 0 (aged profiles, the faded ends of the line) it rendered as a BLACK hairline over the white face (the
    trail measured luma 136 against 190+). Added to a transparent BSDF it can only ever brighten what lies behind it."""
    tr = nodes.new("ShaderNodeBsdfTransparent")
    ad = nodes.new("ShaderNodeAddShader")
    links.new(em.outputs[0], ad.inputs[0])
    links.new(tr.outputs[0], ad.inputs[1])
    links.new(ad.outputs[0], out.inputs["Surface"])


def mat_points_line(name, color, strength):
    """Laser-tinted emission x attribute 'li' (the profile wake), see-through (v6)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    at = nodes.new("ShaderNodeAttribute")
    at.attribute_name = "li"
    st = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    st.inputs[1].default_value = strength
    links.new(at.outputs["Fac"], st.inputs[0])
    links.new(st.outputs[0], em.inputs["Strength"])
    _emit_see_through(nodes, links, em, out)
    return m


def gloss_strip(name, F0, F1, wf, hgt, strength, mirror, fade=(0.3, 0.08), color=(0.92, 0.95, 1.0), cprime=None,
                tol_deg=1.2):
    """v6 (critique fix 2): the clearcoat's reflection band, designed on the FACE and mapped up to the card plane.
    F0 -> F1 is the band's centreline on the face (world XY, metres), wf its width on the face (about the FWHM of a
    smooth bump profile). Every corner is mapped by `mirror` (face point -> card point at height hgt), so the camera
    sees exactly that band mirrored in the coat. Strength fades in over fade[0] of the length from F0 (so the band
    dies before it nears the laser) and out over fade[1] at F1 (beyond the rim). The caller makes it glossy-only."""
    F0, F1 = Vector((F0[0], F0[1], 0.0)), Vector((F1[0], F1[1], 0.0))
    d = (F1 - F0).normalized()
    nrm = Vector((-d.y, d.x, 0.0))
    corners = [F0 - nrm * wf, F0 + nrm * wf, F1 + nrm * wf, F1 - nrm * wf]
    pts = [mirror(c, hgt) for c in corners]
    me = bpy.data.meshes.new(name)
    me.from_pydata([(p.x, p.y, hgt) for p in pts], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name="UVMap")
    for li_, uv in zip(me.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uvl.data[li_.index].uv = uv
    if me.polygons[0].normal.z > 0:      # face down, toward the racket
        me.flip_normals()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["UV"], sep.inputs["Vector"])
    # across: a smooth bump, 1 at the centreline, 0 at +-wf (half maximum at +-wf/2: FWHM = wf)
    c2 = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD")
    c2.inputs[1].default_value = 2.0
    c2.inputs[2].default_value = -1.0
    links.new(sep.outputs["X"], c2.inputs[0])
    ab = _n(nodes, "ShaderNodeMath", "ABSOLUTE")
    links.new(c2.outputs[0], ab.inputs[0])
    acr = _n(nodes, "ShaderNodeMapRange")
    acr.interpolation_type = "SMOOTHSTEP"
    acr.inputs["From Min"].default_value = 1.0
    acr.inputs["From Max"].default_value = 0.0
    links.new(ab.outputs[0], acr.inputs["Value"])
    a0 = _n(nodes, "ShaderNodeMapRange")
    a0.interpolation_type = "SMOOTHSTEP"
    a0.inputs["From Min"].default_value = 0.0
    a0.inputs["From Max"].default_value = max(1e-3, fade[0])
    links.new(sep.outputs["Y"], a0.inputs["Value"])
    a1 = _n(nodes, "ShaderNodeMapRange")
    a1.interpolation_type = "SMOOTHSTEP"
    a1.inputs["From Min"].default_value = 1.0
    a1.inputs["From Max"].default_value = 1.0 - max(1e-3, fade[1])
    links.new(sep.outputs["Y"], a1.inputs["Value"])
    m1 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(acr.outputs["Result"], m1.inputs[0])
    links.new(a0.outputs["Result"], m1.inputs[1])
    m2 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(m1.outputs[0], m2.inputs[0])
    links.new(a1.outputs["Result"], m2.inputs[1])
    if cprime is not None:
        # a honeycomb grid on the strip: it emits only along the mirror path to the camera (from the camera mirrored
        # in the face plane, cprime), within tol_deg. The coat sees the band at full strength; the fibres' broad sheen
        # lobe (roughness 0.6) no longer collects the strip from the whole face, which lifted the shade by 30 luma.
        geo = nodes.new("ShaderNodeNewGeometry")
        vsub = _n(nodes, "ShaderNodeVectorMath", "SUBTRACT")
        vsub.inputs[0].default_value = tuple(cprime)
        links.new(geo.outputs["Position"], vsub.inputs[1])
        vn = _n(nodes, "ShaderNodeVectorMath", "NORMALIZE")
        links.new(vsub.outputs[0], vn.inputs[0])
        vd = _n(nodes, "ShaderNodeVectorMath", "DOT_PRODUCT")
        links.new(geo.outputs["Incoming"], vd.inputs[0])
        links.new(vn.outputs[0], vd.inputs[1])
        gr = _n(nodes, "ShaderNodeMapRange")
        gr.interpolation_type = "SMOOTHSTEP"
        gr.inputs["From Min"].default_value = math.cos(math.radians(tol_deg))
        gr.inputs["From Max"].default_value = math.cos(math.radians(tol_deg * 0.35))
        links.new(vd.outputs["Value"], gr.inputs["Value"])
        mg = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        links.new(m2.outputs[0], mg.inputs[0])
        links.new(gr.outputs["Result"], mg.inputs[1])
        m2 = mg
    m3 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    m3.inputs[1].default_value = strength
    links.new(m2.outputs[0], m3.inputs[0])
    links.new(m3.outputs[0], em.inputs["Strength"])
    links.new(em.outputs[0], out.inputs["Surface"])
    me.materials.append(m)
    ob.visible_camera = False
    ob.visible_diffuse = False          # glossy only: it must not wash the pool's gradient
    ob.visible_transmission = False
    ob.visible_volume_scatter = False
    return ob


# ------------------------------------------------------------------ compositor glow (v3)
def glow_comp(sc, w, amount=0.35):
    """Combined + a tight red halo: multi-scale blur of the laser's own light group (line + its reflections), turned
    to luminance and tinted #ff3a1e, so the core stays white-hot and the halo red. The widest scale of v2 is dropped."""
    vl = sc.view_layers[0]
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes):
        tr.nodes.remove(n)
    rl = tr.nodes.new("CompositorNodeRLayers")
    comp = tr.nodes.new("CompositorNodeComposite")
    src = rl.outputs["Combined_laser"]
    bw = tr.nodes.new("CompositorNodeRGBToBW")
    tr.links.new(src, bw.inputs[0])
    acc = rl.outputs["Image"]
    tk = float(OPT.get("tint", 0.0))
    if tk > 0:
        # v6 (fix 6): on the white face an additive red halo only turns the white pink (G/R 0.85: the face under it is
        # bright, and AgX's path to white desaturates whatever the red pushes up). Round the line the scene is tinted
        # toward the laser before the red is added: base x (1, 0.30, 0.25) by a factor that follows the laser's own
        # light (its mid blur, capped at tint_max), so the halo reads red (G/R <= 0.65) on white and on stone.
        tb = tr.nodes.new("CompositorNodeBlur")
        tb.filter_type = "GAUSS"
        tb.use_relative = False
        tpx = max(1, int(round(float(OPT.get("tint_r", 0.0035)) * w)))
        tb.size_x = tpx
        tb.size_y = tpx
        tr.links.new(bw.outputs[0], tb.inputs["Image"])
        tm_ = tr.nodes.new("CompositorNodeMath")
        tm_.operation = "MULTIPLY"
        tm_.inputs[1].default_value = tk
        tr.links.new(tb.outputs["Image"], tm_.inputs[0])
        tn_ = tr.nodes.new("CompositorNodeMath")
        tn_.operation = "MINIMUM"
        tn_.inputs[1].default_value = float(OPT.get("tint_max", 0.7))
        tr.links.new(tm_.outputs[0], tn_.inputs[0])
        tmix = tr.nodes.new("CompositorNodeMixRGB")
        tmix.blend_type = "MULTIPLY"
        tmix.inputs[2].default_value = (1.0, 0.30, 0.25, 1.0)
        tr.links.new(tn_.outputs[0], tmix.inputs["Fac"])
        tr.links.new(acc, tmix.inputs[1])
        acc = tmix.outputs["Image"]
    for (rel, wgt) in ((0.0012, 0.55), (0.0045, 0.35), (0.016, 0.20)):
        bl = tr.nodes.new("CompositorNodeBlur")
        bl.filter_type = "GAUSS"
        bl.use_relative = False
        px = max(1, int(round(rel * w)))
        bl.size_x = px
        bl.size_y = px
        tr.links.new(bw.outputs[0], bl.inputs["Image"])
        tint = tr.nodes.new("CompositorNodeMixRGB")
        tint.blend_type = "MULTIPLY"
        tint.inputs["Fac"].default_value = 1.0
        tint.inputs[2].default_value = (LASER[0] * 1.3, LASER[1] * 1.6, LASER[2] * 1.6, 1)
        tr.links.new(bl.outputs["Image"], tint.inputs[1])
        mx = tr.nodes.new("CompositorNodeMixRGB")
        mx.blend_type = "ADD"
        mx.inputs["Fac"].default_value = wgt * amount
        tr.links.new(acc, mx.inputs[1])
        tr.links.new(tint.outputs["Image"], mx.inputs[2])
        acc = mx.outputs["Image"]
    tr.links.new(acc, comp.inputs["Image"])


# ------------------------------------------------------------------ shot
def main():
    o = parse_args()
    OPT.update(o)
    t0 = time.time()
    rnd = random.Random(5)
    studio.reset()
    sc = bpy.context.scene
    w, h = o["w"], o["h"]
    W = float(o.get("fw", 0.843))       # desktop frame width at the target (m)
    Hd = W * h / w                      # desktop frame height
    # master frame: the desktop frame (racket centre at y 64 %) united with a portrait frame centred on the racket
    # (long axis vertical, the racket 58 % of its height, 9:16)
    Lp = float(o.get("racket_len", 0.461)) / float(o.get("phone_fill", 0.58))  # v3's 0.461 m kept: same framing
    Wp = Lp * 9 / 16
    top = 0.64 * Hd
    bot = max(0.36 * Hd, Wp / 2)
    Hm = top + bot
    hm = int(round(h * Hm / Hd))
    studio.settings(w, hm, o["spp"])
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.seed = 11
    vl = sc.view_layers[0]
    vl.lightgroups.add(name="laser")

    # the canonical racket (kq_canon), face up on its back face, head to +X, handle to -X: 455.0 mm, centre at x -0.0725
    feel = str(o.get("feel", "command"))
    assert feel in ("command", "pace"), feel
    pace = feel == "pace"
    mo = {"white": float(o["white"])} if "white" in o else None
    white = C.is_white("command", mo)   # the v6 rig and environment (Pace keeps them: only the face changes)
    if pace:
        for k_, v_ in PACE_DEFAULTS.items():
            o.setdefault(k_, v_)
        if float(o["pclamp"]) > 0:
            sc.cycles.sample_clamp_indirect = float(o["pclamp"])
        mo = None
        print("feel pace", flush=True)
    if white:
        for k_, v_ in WHITE_DEFAULTS.items():
            o.setdefault(k_, v_)
        OPT.update(o)
    root, P = C.build_racket("KQ", feel=feel, serial=str(o.get("serial", "KQ-000427")), mat_opts=mo)
    C.pose(root, (0.0, 0.0, T / 2), yaw_deg=-90.0)
    bpy.context.view_layer.update()
    if o.get("measure"):
        print("measure", C.measure(root))
    parts = C.objs(P, "all")                                        # every racket object (lights link to these)
    solid = [ob for ob in parts if ob.get("kq_part") not in ("capmark", "etchR", "etchL")]  # ray-cast surfaces
    head_set = set(C.objs(P, "head"))                               # the measured profiles live on the head only

    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, 0))
    plate = bpy.context.active_object
    plate.name = "Granite"
    plate.data.materials.append(mat_granite())

    rc = Vector((-0.0725, 0.0, 0.02))
    dist = float(o.get("dist", 3.25))
    el = math.radians(82)
    cam_loc = rc + Vector((0, -math.cos(el), math.sin(el))) * dist
    lens = 36.0 * dist / W
    cam = studio.camera(tuple(cam_loc), tuple(rc), lens=lens, shift=(0.0, ((top - bot) / 2) / W))
    cam.data.clip_start = 0.5
    cam.data.sensor_fit = "HORIZONTAL"

    # ---------------- laser sheet
    beta = math.radians(float(o.get("beta", 62.0)))
    tau = math.radians(float(o.get("tilt", 38.0)))
    a = Vector((math.cos(beta), math.sin(beta), 0))
    mvec = Vector((0, 0, 1)).cross(a)
    P0 = Vector((float(o.get("lx", 0.035)), float(o.get("ly", 0.0)), T))
    dsheet = (Vector((0, 0, -1)) * math.cos(tau) + mvec * math.sin(tau)).normalized()
    S = P0 - dsheet * (1.4 / math.cos(tau))
    world = Scene3D(solid + [plate])
    t_lo, t_hi = float(o.get("t_lo", -0.20)), float(o.get("t_hi", 0.128))
    step = float(o.get("step", 0.00012))
    n = int((t_hi - t_lo) / step)
    hits = []
    for k in range(n + 1):
        t = t_lo + k * step
        tgt = P0 + a * t
        d = (tgt - S).normalized()
        hit = world.cast(S, d)
        if hit is None:
            hits.append(None)
            continue
        cosi = max(0.0, -d.dot(hit[1]))
        hits.append((hit[0] + hit[1] * 0.00025, cosi, hit[2] is plate, t))
    grain = max(1, int(round(float(o.get("speck_mm", 0.45)) / 1000.0 / step)))
    sp_noise = value_noise(len(hits), grain, rnd)
    tc_mid = (t_lo + t_hi) / 2
    half = (t_hi - t_lo) / 2
    ccos = math.cos(tau)
    runs, cur, prev = [], [], None
    for k, hh in enumerate(hits):
        if hh is None:
            if len(cur) > 1:
                runs.append(cur)
            cur, prev = [], None
            continue
        p, cosi, on_plate, t = hh
        # full on the whole racket, fading only on the granite ends (the upper end must die before the copy zone)
        f_lo = min(max((t - t_lo) / float(o.get("fade_lo", 0.03)), 0.0), 1.0)
        f_hi = min(max((t_hi - t) / float(o.get("fade_hi", 0.012)), 0.0), 1.0)
        fade = (f_lo * f_lo * (3 - 2 * f_lo)) * (f_hi * f_hi * (3 - 2 * f_hi))
        fall = min(1.0, max(float(o.get("lmin", 0.06)), (cosi / ccos) ** float(o.get("lpow", 1.6))))
        amp = float(o.get("speck_plate", 0.35)) if on_plate else float(o.get("speck_racket", 0.2))
        spk = 1.0 + amp * (2 * sp_noise[k] - 1)
        li = fade * fall * spk * (float(o.get("plate_li", 0.85)) if on_plate else 1.0)
        if prev is not None and (p - prev).length > 0.0025:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        cur.append((p, li))
        prev = p
    if len(cur) > 1:
        runs.append(cur)
    lmat = mat_laser("LaserMat", float(o.get("laser", 60.0)),
                     core=tuple(float(v) for v in str(o.get("core", "1.0,0.88,0.82")).split(",")),
                     core_pow=float(o.get("core_pow", 3.0)))
    laser = laser_tube("lg_laser", runs, float(o.get("lw", 0.00012)), lmat)
    laser.lightgroup = "laser"
    laser.visible_shadow = False          # v6: the tube itself casts no hairline shadow on the face

    # ---------------- measurement profiles: the profiles already scanned stay behind the line as dense, thin,
    # desaturated polylines (the same light-sheet triangulation, so each one dips into the holes it crosses and curls
    # over the frame), every 1.4 mm, fading fast with age (tau 18 mm) so the tip half shows bare carbon
    behind = -mvec if mvec.x < 0 else mvec
    pstep = float(o.get("pstep", 0.0022))
    ptau = float(o.get("ptau", 0.014))
    nprof = int(o.get("nprof", 30))
    pruns = []
    sstep = float(o.get("sstep", 0.0003))
    for j in range(1, nprof + 1):
        age = pstep * j
        Pj = P0 + behind * age
        Sj = Pj - dsheet * (1.4 / math.cos(tau))
        pn = rnd.uniform(0.75, 1.15)
        nst = int((t_hi - t_lo) / sstep)
        vn = value_noise(nst + 1, max(1, int(round(0.0006 / sstep))), rnd)
        cur, prev = [], None
        for k in range(nst + 1):
            t = t_lo + k * sstep
            d = (Pj + a * t - Sj).normalized()
            hit = world.cast(Sj, d)
            ok = hit is not None and hit[2] in head_set
            if ok:
                p = hit[0] + hit[1] * 0.00012
                if prev is not None and (p - prev).length > 0.0025:
                    ok = False
            if not ok:
                if len(cur) > 1:
                    pruns.append(cur)
                cur, prev = [], None
                if hit is not None and hit[2] in head_set:
                    cur, prev = [(hit[0] + hit[1] * 0.00012, 0.0)], hit[0] + hit[1] * 0.00012
                continue
            cosi = max(0.0, -d.dot(hit[1]))
            fall = min(1.0, max(0.05, (cosi / math.cos(tau)) ** 1.6))
            li = math.exp(-age / ptau) * pn * (0.85 + 0.3 * vn[k]) * fall
            cur.append((p, li))
            prev = p
        if len(cur) > 1:
            pruns.append(cur)
    pmat = mat_points_line("ProfileMat", tuple(float(v) for v in str(o.get("pcol", "1.0,0.78,0.65")).split(",")),
                           float(o.get("pts", 10.0)))
    pobj = laser_tube("lg_points", pruns, float(o.get("pr", 0.00004)), pmat, nseg=4)
    # v6 (fix 1): a display line only: no shadow, no light on the face, no mirror double in the coat
    pobj.visible_shadow = False
    pobj.visible_diffuse = False
    pobj.visible_glossy = False
    pts = pruns

    # ---------------- light
    nadir = Vector((cam_loc.x, cam_loc.y, 0))
    rcf = Vector((float(o.get("pool_x", -0.06)), float(o.get("pool_y", -0.02)), 0))

    def mirror_pt(target, hgt):
        return nadir + (target - nadir) * (1 + hgt / cam_loc.z)

    hp = float(o.get("hp", 1.2))
    fc = mirror_pt(rcf, hp)
    amb = disc_softbox("lg_ambient", (fc.x, fc.y, hp), float(o.get("prad", 0.85)), float(o.get("amb", 0.65)),
                       color=(0.93, 0.95, 1.0), power=float(o.get("apow", 1.2)))
    link_to(amb, [plate], "amb_receivers")
    base_s = float(o.get("base", 0.5))
    if base_s > 0:
        bc = mirror_pt(rcf, 2.0)
        bb = disc_softbox("lg_base", (bc.x, bc.y, 2.0), float(o.get("brad", 6.0)), base_s, color=(0.93, 0.95, 1.0), power=0.6)
        link_to(bb, [plate], "base_receivers")
    # lg_under: the plate under the racket, unshadowed by it (shadow linking): granite shows through every hole
    under_s = float(o.get("under", 0.5))
    if under_s > 0:
        uc = mirror_pt(rcf, 1.0)
        un = disc_softbox("lg_under", (uc.x, uc.y, 1.0), float(o.get("urad", 0.7)), under_s, color=(0.93, 0.95, 1.0), power=1.0)
        link_to(un, [plate], "under_receivers")
        bcol = bpy.data.collections.new("under_blockers")
        bcol.objects.link(plate)
        un.light_linking.blocker_collection = bcol
    hfl_s = float(o.get("holefloor", 0.0))
    if hfl_s > 0:
        # v6 (fix 4): a stone patch under the hole field only (the head outline in world space, x > hf_x0, inset 7 mm so
        # no edge shows past the frame at the 8 deg view), 50 um above the plate, same granite (object coordinates =
        # world, so the grain runs on), lit by its own diffuse-only disc that the racket does not shadow (shadow
        # linking). Through each hole the camera now sees lit stone with its grain, so the 42 holes read as
        # through-holes, not printed dots, while the plate round the racket and its contact shadow stay as they were.
        from shapely.geometry import Polygon, box as sbox
        from shapely import affinity
        ol = C.outline_canon()
        poly = ol if hasattr(ol, "exterior") else Polygon(ol)
        reg = affinity.rotate(poly, -90, origin=(0, 0)).intersection(sbox(float(o.get("hf_x0", -0.062)), -1, 1, 1))
        reg = reg.buffer(-float(o.get("hf_inset", 0.007)))
        if reg.geom_type != "Polygon":
            reg = max(reg.geoms, key=lambda g: g.area)
        cs = list(reg.exterior.coords)[:-1]
        me = bpy.data.meshes.new("HoleFloor")
        me.from_pydata([(x_, y_, 0.00005) for x_, y_ in cs], [], [list(range(len(cs)))])
        hfo = bpy.data.objects.new("HoleFloor", me)
        sc.collection.objects.link(hfo)
        me.materials.append(plate.data.materials[0])
        hl = disc_softbox("lg_holes", (0.03, 0.0, 0.40), 0.30, hfl_s, color=(0.93, 0.95, 1.0), power=1.0)
        hl.visible_glossy = False
        link_to(hl, [hfo], "holes_receivers")
        hb = bpy.data.collections.new("holes_blockers")
        hb.objects.link(hfo)
        hl.light_linking.blocker_collection = hb
    face_s = float(o.get("face", 12.0))
    if face_s > 0 and white:
        # v6 (fix 2): the coat's reflection band on white, glossy only (no diffuse wash on the pool's gradient). It is
        # designed on the face: a 32 mm band, near-vertical in the wide frame (about 87 deg, 25 deg off the laser),
        # between the throat's V and the hole field, fading in from 70 mm off the laser and running off the top rim,
        # clear of the serial. The card is the band's mirror footprint at hf; every hole lip catches it as a crescent.
        hf = float(o.get("hf", 1.0))
        fb = [float(v) for v in str(o.get("fb", "-0.068,-0.05,-0.058,0.15")).split(",")]
        fade = [float(v) for v in str(o.get("fb_fade", "0.2,0.08")).split(",")]

        def mirror_face(p_, hgt):
            # the camera ray reflected at face point p_ (z = T) reaches height hgt above the face here
            return nadir + (Vector((p_.x, p_.y, 0.0)) - nadir) * (1 + hgt / (cam_loc.z - T))
        fcard = gloss_strip("lg_face", fb[:2], fb[2:], float(o.get("fb_w", 0.032)), hf - T, face_s,
                            lambda p_, hg: Vector((*mirror_face(p_, hg).xy, 0.0)), fade=fade,
                            cprime=Vector((cam_loc.x, cam_loc.y, 2 * T - cam_loc.z)) if float(o.get("fb_tol", 1.2)) > 0 else None,
                            tol_deg=float(o.get("fb_tol", 1.2)))
        fcard.location.z = T
        link_to(fcard, C.objs(P, "face", "neck", "throat", "bridgewall"), "face_receivers")
        lips_s = float(o.get("lips", 0.0))
        if lips_s > 0:
            # the same softbox seen by the 0.8 mm hole lips (no grid): every hole gets one crescent on the side facing
            # the band, so the 42 holes read as cut through a lacquered shell, not as printed dots
            # (2 cm above the band's card: two coplanar see-through cards made the face's rays skip the band)
            lc = gloss_strip("lg_lips", fb[:2], fb[2:], float(o.get("fb_w", 0.032)), hf + 0.02 - T, lips_s,
                             lambda p_, hg: Vector((*mirror_face(p_, hg).xy, 0.0)), fade=fade)
            lc.location.z = T
            link_to(lc, C.objs(P, "holes"), "lips_receivers")
    elif face_s > 0:
        hf = 1.0
        fq = mirror_pt(rcf + Vector((float(o.get("face_dx", 0.05)), float(o.get("face_dy", 0.0)), 0)), hf - T)
        fcard = sweep_card("lg_face", (fq.x, fq.y, hf), (0.9, 0.7), face_s, float(o.get("face_ang", 270.0)),
                           edge=(float(o.get("fe0", 0.565)), float(o.get("fe1", 0.60))), lo=float(o.get("face_lo", 0.0)),
                           color=(0.92, 0.95, 1.0),
                           band=None if o.get("noband") else (float(o.get("fb0", 0.62)), float(o.get("fb1", 0.64))))
        # the face, its holes and the throat only: the rough twill base under the coat would turn grey under any
        # light it does not need (canon lighting note 1)
        link_to(fcard, C.objs(P, "face", "neck", "holes", "throat", "bridgewall"), "face_receivers")
    rel = math.radians(float(o.get("rim_el", 35.0)))
    rr_ = float(o.get("rim_r", 1.2))
    rim = ring_strip("lg_rim", (-0.07, 0.0), rr_, rr_ * math.tan(rel), float(o.get("rim_w", 0.6)),
                     float(o.get("rim", 10.0)), color=(0.93, 0.95, 1.0), peak_az=float(o.get("rim_az", 110.0)),
                     floor=float(o.get("rim_floor", 0.5)))
    # v4: the 1.5 mm edge (and the neck, whose edge rounds out to 12 mm) only: one continuous hairline outline
    link_to(rim, C.objs(P, "rim", "neck"), "rim_receivers")
    # v4: the handle has its own lights (a black grip that renders grey means too much light)
    M = root.matrix_world
    gc = M @ Vector((0.0, -0.229, 0.0))                       # grip centre (world)
    g_up = (M.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()  # racket axis (world)
    side = (M.to_3x3() @ Vector((-1.0, 0.0, 0.0))).normalized()  # model -x = world +Y: the top of the frame
    for nm, off, hgt, wd, en in (("lg_grip", 0.26, 0.30, 0.02, float(o.get("grip", 1.0))),
                                 ("lg_grip2", -0.30, 0.12, 0.03, float(o.get("grip2", 0.25)))):
        loc = gc + side * off + Vector((0.0, 0.0, hgt))
        lt = studio.area_light(nm, tuple(loc), wd, en, color=(0.95, 0.97, 1.0), size_y=0.30)
        look_at(lt, loc, gc, up=g_up)
        link_to(lt, C.objs(P, "grip", "cap", "capmark") + ([P["neck"]] if nm == "lg_grip" else []), nm + "_receivers")
    # the cap's engraved Q and groove: a softbox in the mirror direction of the cap's top band
    pk = M @ Vector((0.0, -0.2925, 0.016))
    rk = (pk - cam_loc).normalized()
    rk = (rk - 2 * rk.dot(Vector((0, 0, 1))) * Vector((0, 0, 1))).normalized()
    ck = studio.area_light("lg_cap", tuple(pk + rk * 0.35), float(o.get("cap_w", 0.30)), float(o.get("cap", 0.3)),
                           color=(0.95, 0.97, 1.0), size_y=float(o.get("cap_h", 0.10)), target=tuple(pk))
    link_to(ck, C.objs(P, "cap", "capmark"), "cap_receivers")
    # the laser-frosted serial on the throat bridge (optional on a single racket; quiet unless raked)
    rake_s = float(o.get("rake", 0.35))
    if rake_s > 0 and P.get("face") is not None:
        x0, x1, y0, y1 = C.serial_box(str(o.get("serial", "KQ-000427")))
        Sm = Vector(((x0 + x1) / 2, (y0 + y1) / 2, C.ZT))
        S_ = M @ Sm
        rd = M.to_3x3() @ Vector((-math.cos(math.radians(16)), 0.25, math.sin(math.radians(16))))
        rk2 = studio.area_light("lg_rake", tuple(S_ + rd.normalized() * 0.125), 0.05, rake_s, color=(1.0, 0.985, 0.965),
                                size_y=0.005, target=tuple(S_))
        link_to(rk2, [P["face"]], "rake_receivers")

    if white:
        # the white racket's key: a soft spot pool from above the frame's upper left, so the white face carries a
        # gradient (lit upper side falling into soft shade across the head) and the tow relief and fibre sheen read
        head_recv = C.objs(P, "head")
        pool_s = float(o.get("wpool", 0.0))
        if pool_s > 0:
            pl = studio.spot_light("lw_pool", (float(o.get("wp_x", -0.40)), float(o.get("wp_y", 0.60)),
                                               float(o.get("wp_z", 0.95))),
                                   pool_s, float(o.get("wp_deg", 22.0)), blend=1.0, color=(1.0, 0.985, 0.97),
                                   target=(float(o.get("wp_tx", -0.02)), float(o.get("wp_ty", 0.03)), T),
                                   radius=float(o.get("wp_r", 0.06)))
            link_to(pl, head_recv + ([plate] if o.get("wp_plate") else []), "pool_receivers")
        stone_s = float(o.get("wstone", 0.0))
        if stone_s > 0:
            # the same lamp's wider spill on the granite (plate only): the stone lifts in a soft pool round the racket
            # and the racket casts its own soft shadow down-right on it, so it sits on the plate instead of floating
            sp_ = studio.spot_light("lw_stone", (float(o.get("wp_x", -0.40)), float(o.get("wp_y", 0.60)),
                                                 float(o.get("wp_z", 0.95))),
                                    stone_s, float(o.get("ws_deg", 44.0)), blend=1.0, color=(1.0, 0.985, 0.97),
                                    target=(float(o.get("ws_tx", 0.0)), float(o.get("ws_ty", 0.0)), 0.0),
                                    radius=float(o.get("ws_r", 0.10)))
            sp_.visible_glossy = False   # diffuse only: no hot spot or mica sparkle mirrored in the polish
            link_to(sp_, [plate], "stone_receivers")
        fill_s = float(o.get("wfill", 0.0))
        if fill_s > 0:
            fl = studio.area_light("lw_fill", (float(o.get("fill_x", 0.55)), float(o.get("fill_y", -0.70)),
                                               float(o.get("fill_z", 0.75))),
                                   1.0, fill_s, color=(0.94, 0.96, 1.0), target=(-0.0725, 0.0, T))
            link_to(fl, head_recv, "fill_receivers")
        wall_s = float(o.get("wall", 0.0))
        if wall_s > 0:
            # v6 (fix 3): light the wall itself (canon). The 38 mm near wall (the -Y side, toward the camera) saw only
            # the fill and read as a black bumper round the white head, the frame-tube read the brief removes. A long
            # low card on the camera side, linked to the wall and its 1.5 mm rims only, lifts it to white-in-shade.
            wl = studio.area_light("lw_wall", (float(o.get("wall_x", 0.0)), float(o.get("wall_y", -0.70)),
                                               float(o.get("wall_z", 0.16))),
                                   float(o.get("wall_len", 1.0)), wall_s, color=(0.95, 0.97, 1.0),
                                   size_y=float(o.get("wall_h", 0.25)), target=(0.0, -0.12, T / 2))
            link_to(wl, C.objs(P, *str(o.get("wall_recv", "wall,rim")).split(",")), "wall_receivers")

    pw_s = float(o.get("pweave", 0.0)) if pace else 0.0
    if pw_s > 0:
        # Pace: the weave card (K08 / K11 / K01): a soft graded card pw_up degrees off the face's mirror direction; the
        # clear coat cannot see it, the 12K's fibre lobes stretched along one tape direction can, so alternate tapes
        # light up (named pw_ so the lg_ see-through pass and --solo leave it alone)
        import k789_lib as KL789
        fcn = Vector((-0.02, 0.0, T))
        v_w = (cam_loc - fcn).normalized()
        d_w = (2 * v_w.z * Vector((0, 0, 1)) - v_w).normalized()
        hz_w = Vector((-d_w.y, d_w.x, 0)).normalized() if abs(d_w.z) < 0.999 else Vector((1, 0, 0))
        d_up = (Matrix.Rotation(math.radians(float(o["pw_up"])), 3, Vector((1, 0, 0)) if hz_w.length == 0 else hz_w) @ d_w).normalized()
        wv = KL789.gradient_card("pw_weave", tuple(fcn + d_up * float(o["pw_d"])), (float(o["pw_w"]), float(o["pw_h"])),
                                 pw_s, tuple(fcn), color=KL789.kelvin(6500), axis="v", lo=0.0, hi=1.0, floor=0.0)
        link_to(wv, C.objs(P, "face", "neck", "wall", "back"), "weave_receivers")

    for ob in list(sc.objects):
        if ob.name.startswith("lg_") and ob.name not in ("lg_laser", "lg_points") and ob.type == "MESH":
            see_through(ob)

    solo = o.get("solo")
    if solo:
        keep = [ob for ob in sc.objects if ob.name.startswith(solo)]
        for ob in list(sc.objects):
            if (ob.name.startswith("lg_") or ob.name.startswith("lw_")) and ob not in keep:
                ob.hide_render = True

    glow_comp(sc, w, float(o.get("glow", 0.35)))
    # crops: desktop = the top h rows; phone = a 9:16 box centred on the racket, rotated (handle down)
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    cvx = world_to_camera_view(sc, cam, Vector((float(o.get("rcx", -0.0725)), 0.0, 0.02)))
    cx_px = cvx.x * w
    cy_px = (1 - cvx.y) * hm
    pw_px = Wp / W * w
    ph_px = Lp / W * w
    phone_box = (int(round(cx_px - ph_px / 2)), int(round(cy_px - pw_px / 2)), int(round(cx_px + ph_px / 2)), int(round(cy_px + pw_px / 2)))
    print("laser runs", len(runs), "points", len(pts), "master", w, "x", hm, "phone box", phone_box,
          "build", round(time.time() - t0, 1), "s")
    if o.get("norender"):
        return
    p = out_path(o["out"])
    stem = p[:-4]
    if o.get("crop"):
        # inspection: a border render of the master (fractions x0,x1,y0,y1 with y measured from the bottom)
        x0, x1, y0, y1 = [float(v) for v in str(o["crop"]).split(",")]
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = y0, y1
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print("rendered crop", p, round(time.time() - t0, 1), "s")
        return
    sc.render.filepath = stem + "-master.png"
    bpy.ops.render.render(write_still=True)
    from PIL import Image
    im = Image.open(stem + "-master.png").convert("RGB")
    im.crop((0, 0, w, h)).save(p)
    box = (max(0, phone_box[0]), max(0, phone_box[1]), min(w, phone_box[2]), min(hm, phone_box[3]))
    im.crop(box).rotate(90, expand=True).save(stem + "-phone.png")
    print("rendered", p, stem + "-phone.png", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
