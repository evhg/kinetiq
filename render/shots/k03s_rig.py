"""K03 v4 camera and light rig, shared by K03-section-cut and K03b-tubular (identical, so the stills register).

World: the coupon's front (polished) cut is the plane y = 0 facing -Y; the coupon runs away from camera in +y; the
side wall is at +x; the racket face is +Z; the coupon rests on a matte graphite floor. Reflection-only cards light the
lacquer and the polished cut (KINETIQ lesson 1): one large softbox is mirrored in the polished face as a soft gradient
from top-left to bottom-right; the white chamfer kicker traces the face's top edge and, in the full variant, turns
into the 2700 K amber hairline that runs back along the rim's shoulder. 150 mm macro at f/22 focused on the face.
v5 (white Command): every v4 light as it was, plus white_lights() (w_pool, w_fill) when the skin is white.
v6 (art director, revise 6.5): white only, v4 untouched (--white 0 rebuilds v4 to the pixel): a black flag keeps v4's
key off the white top (key_flag), a low raking pool from the back-left (diffuse + 0.45 of its sheen), a gridded
glossy-only lacquer band across the back third (gloss_strip), a brighter wall fill, and the chamfer's quiet white
hairline all round the shell loop (wline_side).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import k03_lib as L  # noqa: E402
import k03s_lib as S  # noqa: E402
import studio  # noqa: E402

fopt = L.fopt
CAM = {"az": 30.0, "el": 21.0, "lens": 150.0, "d": 0.9438, "target": (0.006, 0.020, 0.0), "shift": (-0.0169, 0.0551),
       "fstop": 16.0}
AMBER = (0.768, 0.371, 0.136)      # --amber #e3a467 (linear)
AMBER_HOT = (1.0, 0.761, 0.521)    # --amber-hot #ffe2bf (linear)
SHOULDER = 40.0                    # profile angle of the rim's shoulder line (deg from the top face)


def scene(o):
    studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc = bpy.context.scene
    sc.cycles.glossy_bounces = 6
    sc.cycles.max_bounces = 8
    if S.pace_on(o) and fopt(o, "p_clamp", 4.0) > 0:  # 12K fibre-lobe fireflies (as K10/K11 Pace)
        sc.cycles.sample_clamp_indirect = fopt(o, "p_clamp", 4.0)


def cam_loc(o):
    return L.dir_loc(CAM["target"], fopt(o, "cam_az", CAM["az"]), fopt(o, "cam_el", CAM["el"]), fopt(o, "cam_d", CAM["d"]))


def fit(o, objs, box=(0.27, 0.73, 0.305, 0.805), iters=4):
    """Dev: move the camera along its axis and shift it so the objects' frame bbox fills `box` (x0, x1, y0, y1 top-down)
    as fully as the aspect allows. Prints the numbers to freeze into CAM."""
    sc = bpy.context.scene
    cam = sc.camera
    asp = sc.render.resolution_x / sc.render.resolution_y
    for _ in range(iters):
        x0, x1, y0, y1 = L.frame_bbox(objs)
        k = max((x1 - x0) / (box[1] - box[0]), (y1 - y0) / (box[3] - box[2]))
        d = (Vector(cam.location) - Vector(CAM["target"])).length * k
        cam.location = Vector(CAM["target"]) + (Vector(cam.location) - Vector(CAM["target"])).normalized() * d
        bpy.context.view_layer.update()
        x0, x1, y0, y1 = L.frame_bbox(objs)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tx, ty = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        cam.data.shift_x += (cx - tx)
        cam.data.shift_y -= (cy - ty) / asp
        bpy.context.view_layer.update()
    d = (Vector(cam.location) - Vector(CAM["target"])).length
    print("FIT cam_d %.4f shift_x %.4f shift_y %.4f bbox %s" % (d, cam.data.shift_x, cam.data.shift_y,
                                                              [round(v, 4) for v in L.frame_bbox(objs)]))
    return d, cam.data.shift_x, cam.data.shift_y


def camera(o):
    loc = cam_loc(o)
    cam = studio.camera(loc, CAM["target"], lens=fopt(o, "lens", CAM["lens"]),
                        shift=(fopt(o, "shift_x", CAM["shift"][0]), fopt(o, "shift_y", CAM["shift"][1])))
    cam.data.clip_start = 0.01
    fs = fopt(o, "fstop", CAM["fstop"])
    cam.data.dof.use_dof = fs > 0
    if fs > 0:
        cam.data.dof.aperture_fstop = fs
        fwd = (Vector(CAM["target"]) - Vector(loc)).normalized()
        focus = Vector((fopt(o, "focus_x", 0.0), 0.0, fopt(o, "focus_z", 0.0)))  # the polished face
        cam.data.dof.focus_distance = (focus - Vector(loc)).dot(fwd)
        cam.data.dof.aperture_blades = 9
    return cam


def corner_world():
    """World (u = x) of the front face's side wall and its top-corner centre, and cos(phi) of the cut vs the rim."""
    o, nr = S.outline_ccw(1200)
    k = min(range(len(o)), key=lambda i: abs(o[i][1] - S.Y_FRONT) + (0 if o[i][0] > 0 else 1))
    cphi = abs(nr[k][0])
    uw = S.to_world(Vector((o[k][0], S.Y_FRONT, 0))).x
    return uw, uw - S.FRAME_R / cphi, S.HALF_T - S.FRAME_R, cphi


def lights(objs, floor, car, shell=False, o=None):
    o = o or {}
    O = (0.0, 0.02, 0.0)
    cam = Vector(cam_loc(o))
    # lg_key: soft raking strip top-left of the cut: a gentle diffuse fall-off across the core (no relief to rake)
    ka = math.radians(fopt(o, "key_ang", 15.0))
    kaz = math.radians(fopt(o, "key_az", 55.0))
    kd = fopt(o, "key_dist", 0.22)
    kdir = Vector((-math.cos(kaz) * math.cos(ka), -math.sin(ka), math.sin(kaz) * math.cos(ka)))
    if fopt(o, "key", 0.8) > 0:
        key = studio.area_light("lg_key", tuple(kdir * kd), fopt(o, "key_len", 0.20), fopt(o, "key", 0.8),
                                size_y=fopt(o, "key_w", 0.05), target=(0.0, 0.0, 0.0))
        key.data.color = (1.0, 0.985, 0.96)
        key.visible_glossy = False  # diffuse fill for the section only: no specular streaks on the twill
        L.link_receivers(key, objs, "rx_key")
        L.reg(key)
    # face softbox: ONE large card on the polished cut's mirror rays: a soft gradient sweeping the face from top-left
    # (bright) to bottom-right (s = z - u); the satin plies and the coated core roll it off, the resin lines and UD
    # plies catch it as hairline glints
    mirror_card("satin", face_samples(car, sfun=lambda u, z: fopt(o, "satin_kz", 1.0) * z - (u - S.PIECE_OFFSET.x)), cam,
                fopt(o, "satin_d", 0.6), fopt(o, "satin", 6.0), fopt(o, "satin_s0", -0.025), fopt(o, "satin_s1", 0.045),
                gamma=fopt(o, "satin_g", 1.3), margin=fopt(o, "satin_m", 1.5), floor_val=fopt(o, "satin_floor", 0.02),
                gate_y=fopt(o, "satin_gate", 0.00002))
    # bore: a soft vertical sheen down the concave lining of the half-bore (front-left, below floor level where a
    # downward camera ray leaves a vertical wall), gated off the polished face
    if fopt(o, "bore", 3.0) > 0:
        bc = L.card("bore", L.dir_loc(O, fopt(o, "bore_az", -62), -21, 0.45), (fopt(o, "bore_w", 0.24), 0.5),
                    fopt(o, "bore", 4.0), O, falloff="soft")
        gate_off_face(bc)
    # holes: a small softbox straight overhead: only the far lips of the moulded hole mouths can mirror it (the
    # flat face, the shoulder and the walls cannot), so each hole gets a crisp crescent glint
    if fopt(o, "lips", 3.0) > 0:
        L.card("lips", (0.0, fopt(o, "lips_y", 0.02), fopt(o, "lips_h", 0.30)), (fopt(o, "lips_s", 0.14),) * 2,
               fopt(o, "lips", 3.0), (0.0, fopt(o, "lips_y", 0.02), 0.0), falloff="soft")
    # sweep: card fitted to the top lacquer's mirror rays: the satin sheen rises from dark at the cut to a soft peak
    # behind the holes (s = depth from the cut), the twill reading in its roll-off
    mirror_card("sweep", top_samples(), cam, fopt(o, "sweep_d", 0.6), fopt(o, "sweep", 2.5),
                fopt(o, "sweep_s0", 0.006), fopt(o, "sweep_s1", 0.05), gamma=fopt(o, "sweep_g", 1.3), margin=0.35,
                band=(fopt(o, "sweep_b0", 1.0), fopt(o, "sweep_b1", 2.0)) if o.get("sweep_band") else None)
    # wall: card fitted to the side wall's mirror rays: a soft light sweep along its length
    mirror_card("wall", wall_samples(), cam, fopt(o, "wall_d", 0.5), fopt(o, "wall", 0.8),
                fopt(o, "wall_s0", 0.0), fopt(o, "wall_s1", 0.05), gamma=fopt(o, "wall_g", 1.0), margin=0.6,
                invert=bool(o.get("wall_inv")))
    if fopt(o, "rim", 0.0) > 0:
        rim_line(o, cam)
    # lg_line: hot white ribbon on the mirror rays of the polished chamfer round the cut: full along the top edge,
    # ending at the rim's shoulder (where the amber hairline takes over in the full variant), quiet elsewhere
    white = S.white_on(o)
    # v6 white only (art director: the white face ply must read all round the shell loop at 1280, not only along the
    # top): the polished chamfer, which cuts through that same white ply, carries a quiet hairline (wline_side of the
    # top edge's strength) round the 11 mm curve, down the side and along the bottom edge (line_zmin reaches the
    # bottom), never down the half-bore's edge. v4 and --white 0: quiet there, as before.
    zmin_d = -0.0195 if white else -0.0175
    segs = car.chamfer_line("front", z_min=fopt(o, "line_zmin", zmin_d))
    if segs:
        zt = S.HALF_T
        uw, uc, zc, cphi = corner_world()
        alpha = fopt(o, "shoulder", SHOULDER)
        bx = S.to_world(Vector((S.BORE[0] + 0.0062, 0, 0))).x
        side0 = fopt(o, "line_side", 0.0)

        def side_gain(P):
            if not white or P.x < bx + fopt(o, "wline_bx", 0.004):
                return side0
            return max(side0, fopt(o, "wline_side", 0.30))

        def line_gain(P, N, r):
            P = Vector(P)
            if P.x > uc and P.z > zc:
                th = math.degrees(math.atan2((P.x - uc) * cphi, P.z - zc))
                return max(side_gain(P), 1.0 - L_smooth(alpha - 1.0, alpha + 4.0, th))
            if P.z > zt - 0.0012:
                g = 1.0
                if P.x < bx + 0.0015:  # over the bore's lip: fade down into the bore
                    g = L_smooth(zt - 0.0009, zt - 0.0002, P.z)
                return g
            return side_gain(P)
        L.mirror_ribbon("lg_line", segs, tuple(cam), dist=fopt(o, "line_d", 0.5), width=fopt(o, "line_w", 0.012),
                        strength=fopt(o, "line", 32.0), color=(1.0, 0.99, 0.97), gain=line_gain)
    if shell:
        add_shell(o, car, cam)
    if S.pace_on(o):
        pace_lights(o)
    if S.white_on(o):
        white_lights([car.obj], o, cam)
    rx = None
    for ob in L.LIGHTS:
        if ob.type == "MESH" and ob.light_linking.receiver_collection is None and ob.name != "lg_shell":
            if rx is None:
                rx = L.link_receivers(ob, objs, "rx_piece")
            else:
                ob.light_linking.receiver_collection = rx
    floor_lights(floor, o)
    if S.white_on(o) and fopt(o, "w_flag", 1.0) > 0:
        key_flag(o)


def pace_lights(o):
    """--feel pace (Release 2): a soft weave card off the top lacquer's mirror direction (above it by p_wv_up deg, so
    the glass coat cannot mirror it): only the 12K fibre lobes catch it, so alternate tapes light and the spread-tow
    checker reads across the top in shade (K11's weave card). Coupon-linked like every other piece light."""
    O = (0.0, fopt(o, "p_wv_y", 0.02), 0.0)
    az = CAM["az"] + 180.0 + fopt(o, "p_wv_az", 0.0)
    el = CAM["el"] + fopt(o, "p_wv_up", 30.0)
    s = fopt(o, "p_wv", 14.0)
    if s > 0:
        L.card("p_weave", L.dir_loc(O, az, el, fopt(o, "p_wv_d", 0.6)), (fopt(o, "p_wv_w", 1.0), fopt(o, "p_wv_h", 1.0)),
               s, O, falloff="soft")


def white_lights(objs, o, cam=None):
    """White Command only (canon.md lighting note 8: white carbon needs real diffuse light, not only the
    reflection-only studio that black lacquer needs). Lights ADDED to v4's rig, nothing of v4 changed. All sit BEHIND
    the polished cut's plane (their direction has +y) or emit only along the top's mirror path, so they cannot reach the
    cut (it faces -y): the section, the half-bore and v4's lights read exactly as before. Linked to the coupon only (not
    the floor, not K03b's tube cavity).
    v6 (art director, 2026-10-22, "revise 6.5"): v5's pool came from 72 deg above, square to the top: a flat 168-197
    ramp, no specular cue and half the canon's weave contrast. Now:
      w_pool : a LOW raking soft spot (wp_el 35 deg above the top plane) from the back-left (wp_az 40 deg from +y
               toward -x), 0.17 m from the back-left of the top, a 22 deg cone with blend 1 (the canon's pool), 6.5 W:
               the top falls from about 205-210 at the back-left to about 150 along the cut. Diffuse at full power, its
               glossy part (w_pool_g, the fibre sheen that makes the twill flip) at wp_gk 0.45: weave high-pass about
               11 at 1600 px (6.5 % of the mean), the canon's range (K02 wall 5.4 %, K03's own wall 5.9 %), not the
               9 % chessboard of the full sheen. Only works with key_flag: v4's key otherwise floods the top.
      w_gloss: one glossy-only, gridded strip (K05's gloss_strip: emits only along the camera's mirror path off the
               top plane, within gl_tol deg; transparent elsewhere, so the v4 sweep card behind it still reads), drawn
               as a narrow lacquer band (FWHM about 4.5 mm, gl_y 46 mm behind the cut) across the back third of the
               top, about luma 225-235, the twill showing through it. The card sits only gl_h 3 cm above the top:
               f/16 focused on the cut renders the band's mirror image at its virtual distance, and a card 12 cm up
               blurred it into a 35 px smear. Its mirror path from the horizontal top cannot reach the vertical cut.
      w_fill : a soft fill from the right, low (wf_dz 0.25) and behind, on the side wall, 1.35 W: the wall's median
               about 136 (v5: 112, a dirty mid-grey), still 70 under the top's peak so the form holds."""
    if fopt(o, "w_pool", 6.5) > 0:
        el, az = math.radians(fopt(o, "wp_el", 35.0)), math.radians(fopt(o, "wp_az", 40.0))
        d = Vector((-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
        tgt = Vector((fopt(o, "wp_tx", -0.026), fopt(o, "wp_ty", 0.050), S.HALF_T))
        loc = tgt + d * fopt(o, "wp_dist", 0.17)
        # the same lamp as two lights: its diffuse part at w_pool, its glossy part (the fibre sheen that makes the
        # twill flip) at wp_gk of it, so the weave contrast can match the canon's stills without changing the pool
        gk = fopt(o, "wp_gk", 0.45)
        for nm, en, dif, glo in (("w_pool", 1.0, True, gk == 1.0), ("w_pool_g", gk, False, True)):
            if nm == "w_pool_g" and (gk == 1.0 or gk <= 0):
                continue
            pool = studio.spot_light(nm, tuple(loc), fopt(o, "w_pool", 6.5) * en, fopt(o, "wp_cone", 22.0), blend=1.0,
                                     target=tuple(tgt), radius=fopt(o, "wp_r", 0.02))
            pool.data.color = (1.0, 0.985, 0.965)
            pool.visible_camera = False      # close in: never a lamp in the frame
            pool.visible_diffuse = dif
            pool.visible_glossy = glo and bool(fopt(o, "wp_gloss", 1.0))
            L.link_receivers(pool, objs, "rx_" + nm)
            L.reg(pool)
    if fopt(o, "w_gloss", 26.0) > 0 and cam is not None:
        g = gloss_strip("w_gloss", Vector(cam), o)
        L.link_receivers(g, objs, "rx_wgloss")
        L.reg(g)
    if fopt(o, "w_fill", 1.35) > 0:
        d = Vector((fopt(o, "wf_dx", 0.85), fopt(o, "wf_dy", 0.30), fopt(o, "wf_dz", 0.25))).normalized()
        tgt = Vector((0.03, 0.03, 0.0))
        fill = studio.area_light("w_fill", tuple(tgt + d * fopt(o, "wf_dist", 0.4)), fopt(o, "wf_size", 0.3),
                                 fopt(o, "w_fill", 1.35), target=tuple(tgt))
        fill.data.color = (0.97, 0.98, 1.0)
        fill.visible_glossy = bool(fopt(o, "wf_gloss", 0.0))
        L.link_receivers(fill, objs, "rx_wfill")
        L.reg(fill)


def key_flag(o):
    """White Command only (v6): a black flag between lg_key and the TOP of the coupon, as a studio would set one. v4's
    key is a diffuse strip above-left and in front of the cut, there to shape the polished section; on black lacquer it
    did nothing to the top (albedo 0.02), but on white twill it laid a flat diffuse wash over the whole top (front 154,
    back 174 with no white light at all), which is what read as flat matte fabric. The flag is a shadow-only sheet
    flag_h above the top, cut to the top's outline from flag_y0 behind the cut (so the chamfer and the cut never see
    it) and open over every hole mouth (so the lips keep the key); it blocks lg_key ONLY (every other light gets a
    blocker set that excludes it), so the cut, the bores, the floor and every other light read exactly as before."""
    import bmesh
    from shapely.geometry import Point, box as sbox
    h, y0 = fopt(o, "flag_h", 0.2) * S.MM, fopt(o, "flag_y0", 0.17) * S.MM
    F = S.footprint().intersection(sbox(-1, S.Y_FRONT + y0, 1, S.Y_BACK + 0.01))
    for (hx, hy) in S.COUPON_HOLES:
        F = F.difference(Point(hx, hy).buffer(S.BORE_R + S.LIP, resolution=64))
    me = bpy.data.meshes.new("w_flag")
    bm = bmesh.new()
    polys = list(F.geoms) if hasattr(F, "geoms") else [F]
    for P in polys:
        tri = __import__("shapely.ops", fromlist=["triangulate"]).triangulate(P)
        for t in tri:
            if not t.representative_point().within(P):
                continue
            vs = [bm.verts.new(S.to_world(Vector((x, y, S.HALF_T + h)))) for x, y in list(t.exterior.coords)[:3]]
            bm.faces.new(vs)
    bm.to_mesh(me)
    bm.free()
    flag = bpy.data.objects.new("w_flag", me)
    bpy.context.scene.collection.objects.link(flag)
    flag.visible_camera = False
    flag.visible_diffuse = False
    flag.visible_glossy = False
    flag.visible_transmission = False
    flag.visible_volume_scatter = False
    flag.visible_shadow = True
    col = bpy.data.collections.new("kq_noflag")
    col.objects.link(flag)
    col.collection_objects[0].light_linking.link_state = "EXCLUDE"   # every object blocks, except the flag
    n = 0
    for ob in bpy.context.scene.objects:
        emits = ob.type == "LIGHT" or ob in L.LIGHTS
        if emits and ob.name != "lg_key":
            ob.light_linking.blocker_collection = col
            n += 1
    print("key_flag: %.1f mm2 at +%.2f mm, %d other emitters exempt" % (F.area * 1e6, h / S.MM, n))
    return flag


def gloss_strip(name, cam, o):
    """K05's gloss_strip on K03's top (v6): the lacquer band is designed ON THE TOP FACE (world XY at z = HALF_T):
    centreline from (gl_x0, gl_y) to (gl_x1, gl_y), FWHM gl_w (m) across, a plateau with soft edges (gl_edge: 0 = a
    smooth bump, 0.6 = a flat band with short soft edges), fading in from x0 over gl_fade0 of its length. Each corner
    is mapped up to the card plane gl_h above the top through the camera's mirror in the top plane, so the camera sees
    exactly that band in the coat. Glossy-only, and a honeycomb grid: it emits only toward rays that left the camera
    mirrored in the top plane (cprime), within gl_tol deg, so only the top's coat (and the fibres' sheen within that
    cone) sees it: the rest of the coupon, the shoulder, the bores and the vertical cut never do. Emission + transparent:
    rays it does not emit to pass on to the v4 sweep card behind it (no shadowing of the sweep)."""
    T = S.HALF_T
    hgt = fopt(o, "gl_h", 0.03)
    nadir = Vector((cam.x, cam.y, 0.0))
    k = 1.0 + hgt / (cam.z - T)

    def up(px, py):
        q = nadir + (Vector((px, py, 0.0)) - nadir) * k
        return Vector((q.x, q.y, T + hgt))
    y, w = fopt(o, "gl_y", 0.046), fopt(o, "gl_w", 0.0035)
    x0, x1 = fopt(o, "gl_x0", -0.050), fopt(o, "gl_x1", 0.030)
    dy = fopt(o, "gl_dy", 0.0)          # tilt: the centreline runs from (x0, y) to (x1, y + dy)
    corners = [(x0, y - w), (x1, y + dy - w), (x1, y + dy + w), (x0, y + w)]
    pts = [up(px, py) for px, py in corners]
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in pts], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name="UVMap")
    for li_, uv in zip(me.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uvl.data[li_.index].uv = uv
    if me.polygons[0].normal.z > 0:      # face down, toward the coupon
        me.flip_normals()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new(name + "Mat")
    b = S.NB(m)
    uvn = b.nodes.new("ShaderNodeUVMap")
    u, v, _ = b.sep(uvn.outputs["UV"])
    # across (v: 0..1 over 2 * gl_w): plateau |2v - 1| < edge, smooth to 0 at the corners' +-w (FWHM ~ w)
    e = fopt(o, "gl_edge", 0.6)
    a = b.math("ABSOLUTE", b.mad(v, 2.0, -1.0))
    across = b.sub(1.0, b.smooth(e, 1.0, a))
    along = b.mul(b.smooth(0.0, max(1e-3, fopt(o, "gl_fade0", 0.25)), u),
                  b.sub(1.0, b.smooth(1.0 - max(1e-3, fopt(o, "gl_fade1", 0.05)), 1.0, u)))
    st = b.mul(across, along)
    # honeycomb: emit only along the mirror path to the camera (camera mirrored in the top plane), within gl_tol deg
    cprime = Vector((cam.x, cam.y, 2 * T - cam.z))
    geo = b.nodes.new("ShaderNodeNewGeometry")
    dirn = b.vmath("NORMALIZE", b.vmath("SUBTRACT", tuple(cprime), geo.outputs["Position"]))
    dot = b.vmath("DOT_PRODUCT", geo.outputs["Incoming"], dirn)
    tol = fopt(o, "gl_tol", 1.2)
    gate = b.smooth(math.cos(math.radians(tol)), math.cos(math.radians(tol * 0.35)), dot)
    st = b.mul(b.mul(st, gate), fopt(o, "w_gloss", 26.0))
    em = b.nodes.new("ShaderNodeEmission")
    b._set(em.inputs["Color"], (0.95, 0.97, 1.0))
    b._set(em.inputs["Strength"], st)
    tr = b.nodes.new("ShaderNodeBsdfTransparent")
    ad = b.nodes.new("ShaderNodeAddShader")
    b.links.new(tr.outputs[0], ad.inputs[0])
    b.links.new(em.outputs[0], ad.inputs[1])
    b.output(ad)
    me.materials.append(m)
    ob.visible_camera = False
    ob.visible_diffuse = False          # glossy only: it must not wash the pool's gradient
    ob.visible_transmission = False
    ob.visible_volume_scatter = False
    ob.visible_shadow = False
    print("gloss_strip %s: band y %.4f, width %.4f, card at +%.3f m" % (name, y, w, hgt))
    return ob


def gate_off_face(ob, y_min=0.00005):
    """Emit only toward rays that did NOT start on the polished face (world y ~ 0)."""
    m = ob.data.materials[0]
    nodes, links = m.node_tree.nodes, m.node_tree.links
    em = [n for n in nodes if n.type == "EMISSION"][0]
    st_link = [l for l in links if l.to_node == em and l.to_socket.name == "Strength"]
    geo = nodes.new("ShaderNodeNewGeometry")
    lp = nodes.new("ShaderNodeLightPath")
    sc_ = nodes.new("ShaderNodeVectorMath"); sc_.operation = "SCALE"
    links.new(geo.outputs["Incoming"], sc_.inputs[0])
    links.new(lp.outputs["Ray Length"], sc_.inputs["Scale"])
    org = nodes.new("ShaderNodeVectorMath"); org.operation = "ADD"
    links.new(geo.outputs["Position"], org.inputs[0])
    links.new(sc_.outputs[0], org.inputs[1])
    sp = nodes.new("ShaderNodeSeparateXYZ")
    links.new(org.outputs[0], sp.inputs[0])
    gt = nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = y_min
    links.new(sp.outputs["Y"], gt.inputs[0])
    mg = nodes.new("ShaderNodeMath"); mg.operation = "MULTIPLY"
    if st_link:
        links.new(st_link[0].from_socket, mg.inputs[0])
        links.remove(st_link[0])
    else:
        mg.inputs[0].default_value = em.inputs["Strength"].default_value
    links.new(gt.outputs[0], mg.inputs[1])
    links.new(mg.outputs[0], em.inputs["Strength"])
    return ob


def L_smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def floor_lights(floor, o):
    sun_d = bpy.data.lights.new("floor_base", "SUN")
    sun_d.energy = fopt(o, "floor_base", 2.0)
    sun_d.angle = math.radians(fopt(o, "sun_angle", 30.0))
    sun = bpy.data.objects.new("floor_base", sun_d)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(fopt(o, "sun_tilt", -10.0)), 0, 0)
    L.link_receivers(sun, [floor], "rx_floor_base")
    L.reg(sun)
    # pool: a soft-edged spot from high above-behind the piece: the lit graphite pool round the sample, falling off
    # to quiet graphite at the frame edges
    pxyz = (fopt(o, "pool_x", 0.0), fopt(o, "pool_y", 0.10), S.FLOOR_Z + fopt(o, "pool_h", 0.5))
    pool = studio.spot_light("floor_pool", pxyz, fopt(o, "pool", 28.0), fopt(o, "pool_cone", 34.0), blend=1.0,
                             target=(pxyz[0], pxyz[1] + fopt(o, "pool_dy", 0.0), S.FLOOR_Z), radius=0.06)
    pool.data.color = (0.95, 0.96, 1.0)
    L.link_receivers(pool, [floor], "rx_floor_pool")
    L.reg(pool)
    # contact: a small softbox straight above the piece: a soft but defined contact shadow that grounds the hull
    cxyz = (fopt(o, "con_x", 0.004), fopt(o, "con_y", 0.03), S.FLOOR_Z + fopt(o, "con_h", 0.16))
    con = studio.area_light("floor_contact", cxyz, fopt(o, "con_r", 0.05), fopt(o, "con", 0.35), shape="DISK",
                            target=(cxyz[0], cxyz[1], S.FLOOR_Z))
    con.visible_camera = False
    con.visible_glossy = False
    L.link_receivers(con, [floor], "rx_floor_con")
    L.reg(con)


def rim_rows(alpha_deg, inset=0.0006):
    rows = []
    y = S.Y_FRONT + S.CHAMFER + inset
    while y < S.Y_BACK - inset:
        P, N, _ = S.rim_point(y, alpha_deg)
        rows.append((S.to_world(P), N))
        y += 0.0002
    return rows


def rim_line(o, cam):
    return L.mirror_ribbon("rim", [rim_rows(fopt(o, "rim_alpha", 14.0))], tuple(cam), dist=fopt(o, "rim_d", 0.05),
                           width=fopt(o, "rim_w", 0.004), strength=fopt(o, "rim", 6.0), color=(1.0, 0.99, 0.97),
                           max_gap=0.6, gate_mm=2.0)


def add_shell(o, car, cam):
    """lg_shell: the 2700 K amber hairline on the rim's shoulder (profile angle SHOULDER), from the front cut (where
    the white chamfer line ends) back along the whole visible rim, fading with distance. A camera-only emissive strip
    lying 0.02 mm proud of the surface (transparent + emission, so the base pass sees the surface through it): a
    hot #ffe2bf core with #e3a467 amber edges, about 3 px wide at 3200. Light group 'shell'."""
    alpha = fopt(o, "shoulder", SHOULDER)
    w = fopt(o, "shell_w", 0.40) * S.MM
    y0 = S.Y_FRONT + S.CHAMFER * fopt(o, "shell_y0", 1.0)
    y1 = S.Y_BACK - 0.0004
    me = bpy.data.meshes.new("lg_shell")
    import bmesh
    bm = bmesh.new()
    la = bm.verts.layers.float.new("acr")
    lo = bm.verts.layers.float.new("alo")
    n = int((y1 - y0) / 0.0001)
    prev = None
    a = math.radians(alpha)
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        P, N, nxy = S.rim_point(y, alpha, off=fopt(o, "shell_off", 0.02) * S.MM)
        t = Vector((nxy.x * math.cos(a), nxy.y * math.cos(a), -math.sin(a))).normalized()
        row = []
        for c in (-1.0, 0.0, 1.0):
            v = bm.verts.new(S.to_world(P + t * (c * w / 2)))
            v[la] = c
            v[lo] = (y - y0) / (y1 - y0)
            row.append(v)
        if prev:
            for i in range(2):
                bm.faces.new((prev[i], prev[i + 1], row[i + 1], row[i]))
        prev = row
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("lg_shell", me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new("lg_shellMat")
    b = S.NB(m)
    acr, alo = b.attr("acr"), b.attr("alo")
    prof = b.math("EXPONENT", b.mul(b.mul(acr, acr), -fopt(o, "shell_sharp", 4.0)))
    fade = b.lerp(1.0, fopt(o, "shell_tail", 0.18), b.math("POWER", alo, fopt(o, "shell_fg", 0.7)))
    start = b.smooth(0.0, fopt(o, "shell_in", 0.004), alo)   # no square end: the line grows out of the chamfer
    mask = bool(o.get("line_mask"))
    st = b.mul(b.mul(b.mul(prof, fade), b.mad(start, 0.6, 0.4)), 1.0 if mask else fopt(o, "shell", 30.0))
    hot = b.math("POWER", prof, 3.0)
    col = b.vmath("ADD", b.vmath("SCALE", AMBER, scale=b.sub(1.0, hot)), b.vmath("SCALE", AMBER_HOT, scale=hot))
    if mask:  # --line_mask: a linear white profile pass, coloured in display space by k03s_line.py
        col = (1.0, 1.0, 1.0)
    em = b.nodes.new("ShaderNodeEmission")
    b._set(em.inputs["Color"], col)
    b._set(em.inputs["Strength"], st)
    tr = b.nodes.new("ShaderNodeBsdfTransparent")
    ad = b.nodes.new("ShaderNodeAddShader")
    b.links.new(tr.outputs[0], ad.inputs[0])
    b.links.new(em.outputs[0], ad.inputs[1])
    b.output(ad)
    me.materials.append(m)
    ob.visible_diffuse = False
    ob.visible_glossy = False
    ob.visible_transmission = False
    ob.visible_volume_scatter = False
    ob.visible_shadow = False
    vl = bpy.context.view_layer
    if "shell" not in [g.name for g in vl.lightgroups]:
        vl.lightgroups.add(name="shell")
    ob.lightgroup = "shell"
    return L.reg(ob)


def mirror_card(name, samples, cam, dist, strength, s0, s1, gamma=1.0, margin=0.25, interp="SMOOTHSTEP",
                color=(1, 1, 1), invert=False, floor_val=0.0, band=None, gate_y=None):
    """Reflection-only card fitted to a surface: samples = [(P_world, N_world, s), ...]. The card sits on the mean
    mirror ray at `dist`, faces the samples, and is just big enough to hold every sample's mirror hit (+margin).
    Emission = strength * ramp(s) where s is fitted (least squares, affine) from card coordinates, so the camera sees
    the surface brighten smoothly from s0 to s1 (invert flips it)."""
    import numpy as np
    cam = Vector(cam)
    rs = []
    for (P, N, s) in samples:
        r = L.mirror_dir(P, N, cam)
        if r is not None:
            rs.append((Vector(P), r, s))
    Pm = sum((p for p, _, _ in rs), Vector()) / len(rs)
    rm = sum((r for _, r, _ in rs), Vector()).normalized()
    C = Pm + rm * dist
    bpy.ops.mesh.primitive_plane_add(size=1, location=tuple(C))
    ob = bpy.context.active_object
    ob.name = name
    studio.aim(ob, tuple(Pm))
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    nrm = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
    ax = (mw.to_3x3() @ Vector((1, 0, 0))).normalized()
    ay = (mw.to_3x3() @ Vector((0, 1, 0))).normalized()
    pts, ss = [], []
    for (P, r, s) in rs:
        den = r.dot(nrm)
        if abs(den) < 1e-6:
            continue
        t = (C - P).dot(nrm) / den
        q = P + r * t - C
        pts.append((q.dot(ax), q.dot(ay)))
        ss.append(s)
    pts = np.array(pts)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    span = np.maximum(hi - lo, 1e-3)
    cen = (lo + hi) / 2
    size = span * (1 + 2 * margin)
    C2 = C + ax * float(cen[0]) + ay * float(cen[1])
    ob.location = C2
    ob.scale = (float(size[0]), float(size[1]), 1.0)
    A = np.c_[(pts[:, 0] - cen[0]) / size[0], (pts[:, 1] - cen[1]) / size[1], np.ones(len(pts))]
    coef = np.linalg.lstsq(A, np.array(ss), rcond=None)[0]
    res = float(np.sqrt(np.mean((A @ coef - np.array(ss)) ** 2)))
    m, em = L._emit_mat(name, strength, color)
    nodes, links = m.node_tree.nodes, m.node_tree.links
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sep.inputs[0])
    a = nodes.new("ShaderNodeMath"); a.operation = "MULTIPLY_ADD"
    a.inputs[1].default_value = float(coef[0]); a.inputs[2].default_value = float(coef[2])
    links.new(sep.outputs["X"], a.inputs[0])
    b = nodes.new("ShaderNodeMath"); b.operation = "MULTIPLY_ADD"
    b.inputs[1].default_value = float(coef[1])
    links.new(sep.outputs["Y"], b.inputs[0]); links.new(a.outputs[0], b.inputs[2])
    g = nodes.new("ShaderNodeMapRange")
    g.interpolation_type = interp
    g.inputs["From Min"].default_value = s1 if invert else s0
    g.inputs["From Max"].default_value = s0 if invert else s1
    g.inputs["To Min"].default_value = floor_val
    links.new(b.outputs[0], g.inputs["Value"])
    res_sock = g.outputs["Result"]
    if band:  # band=(s2, s3): fade back out from s2 to s3 (a soft stripe s0..s3)
        g2 = nodes.new("ShaderNodeMapRange")
        g2.interpolation_type = interp
        g2.inputs["From Min"].default_value = band[0]
        g2.inputs["From Max"].default_value = band[1]
        g2.inputs["To Min"].default_value = 1.0
        g2.inputs["To Max"].default_value = 0.0
        links.new(b.outputs[0], g2.inputs["Value"])
        mb = nodes.new("ShaderNodeMath"); mb.operation = "MULTIPLY"
        links.new(g.outputs["Result"], mb.inputs[0]); links.new(g2.outputs["Result"], mb.inputs[1])
        res_sock = mb.outputs[0]
    pw = nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = gamma
    links.new(res_sock, pw.inputs[0])
    st = nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = strength
    links.new(pw.outputs[0], st.inputs[0])
    out_s = st.outputs[0]
    if gate_y is not None:
        # emit only toward rays that START on the polished face (world y ~ 0): the chamfer kicker, the bore lining
        # and the lacquer never see this card
        geo = nodes.new("ShaderNodeNewGeometry")
        lp = nodes.new("ShaderNodeLightPath")
        sc_ = nodes.new("ShaderNodeVectorMath"); sc_.operation = "SCALE"
        links.new(geo.outputs["Incoming"], sc_.inputs[0])
        links.new(lp.outputs["Ray Length"], sc_.inputs["Scale"])
        org = nodes.new("ShaderNodeVectorMath"); org.operation = "ADD"
        links.new(geo.outputs["Position"], org.inputs[0])
        links.new(sc_.outputs[0], org.inputs[1])
        sp = nodes.new("ShaderNodeSeparateXYZ")
        links.new(org.outputs[0], sp.inputs[0])
        lt = nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = gate_y
        links.new(sp.outputs["Y"], lt.inputs[0])
        mg = nodes.new("ShaderNodeMath"); mg.operation = "MULTIPLY"
        links.new(out_s, mg.inputs[0]); links.new(lt.outputs[0], mg.inputs[1])
        out_s = mg.outputs[0]
    links.new(out_s, em.inputs["Strength"])
    ob.data.materials.append(m)
    L.reflect_only(ob)
    print("mirror_card %s size %.3f x %.3f m, fit residual %.4g" % (name, size[0], size[1], res))
    return L.reg(ob)


def top_samples(n=36):
    """Points on the coupon's flat top face (world), s = depth from the cut (m)."""
    from shapely.geometry import Point
    F = S.footprint(margin=0.0005, holes_r=0.0062 + S.LIP + 0.001)
    x0, y0, x1, y1 = F.bounds
    out = []
    for i in range(n):
        for j in range(n):
            x = x0 + (x1 - x0) * i / (n - 1)
            y = y0 + (y1 - y0) * j / (n - 1)
            if x > edge_x(y) - S.FRAME_R or not F.contains(Point(x, y)):
                continue
            out.append((S.to_world(Vector((x, y, S.HALF_T))), Vector((0, 0, 1)), y - S.Y_FRONT))
    return out


_EDGE = None


def edge_x(y):
    global _EDGE
    if _EDGE is None:
        o, _ = S.outline_ccw(600)
        _EDGE = o
    best = -1
    o = _EDGE
    for i in range(len(o)):
        (x1, y1), (x2, y2) = o[i], o[(i + 1) % len(o)]
        if x1 > 0 and (y1 - y) * (y2 - y) <= 0 and y1 != y2:
            best = max(best, x1 + (x2 - x1) * (y - y1) / (y2 - y1))
    return best


def wall_samples(n=40, zs=(-0.006, -0.002, 0.002, 0.006)):
    """Points on the flat part of the side wall (world), s = distance along the wall from the cut (m)."""
    outline, onrm = S.outline_ccw(1200)
    out = []
    for (x, y), (nx, ny) in zip(outline, onrm):
        if x < 0.1 or not (S.Y_FRONT + 0.001 < y < S.Y_BACK - 0.001):
            continue
        for z in zs:
            out.append((S.to_world(Vector((x, y, z))), Vector((nx, ny, 0)), y - S.Y_FRONT))
    return out[:: max(1, len(out) // (n * len(zs)))]


def face_samples(car, n=30, sfun=None):
    """Points on the polished front cut (world), s = sfun(u, z) (default u - z) across the face (m)."""
    out = []
    for (name, NP, A, regs) in car.caps:
        if name != "front":
            continue
        u0, z0, u1, z1 = A.bounds
        c = [k for k in car.cuts if k.name == "front"][0]
        for i in range(n):
            for j in range(n):
                u = u0 + (u1 - u0) * i / (n - 1)
                z = z0 + (z1 - z0) * j / (n - 1)
                from shapely.geometry import Point
                if A.contains(Point(u, z)):
                    out.append((S.to_world(c.from_uv(u, z)), Vector((0, -1, 0)), sfun(u, z) if sfun else u - z))
    return out
