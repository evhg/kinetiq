"""Kdark_row (2026-11-07, cloud REQUEST k04-language): K07 (the Identical lineup) and K08 (the two feels) in K11-dark's
K04 language. The materials, glow, field and compositing are K11-dark's own functions (imported, so the K11 look and
these stay one look); this script only builds a row of rackets, frames it to the page's crops and gives every racket
its own light set, light-linked to that racket alone (so a neighbour never catches another's key):
  key   : the low raking spot from the crown side (Command white where lit, falling to deep shade across the width),
  sheen : the glossy strip above the face's mirror direction (lip crescents, edge radius); Pace also its weave card,
  rims  : Pace only, the two cool back strips (the silhouette from crown to the Q, continuous),
  wall  : Command only, the soft diffuse card on the camera-left wall and neck; Command's shaft strip.
Modes:
  --mode feels (K08): Command (KQ-000427) left, Pace (KQ-000428) right, turned toward each other, each whole inside its
                      page crop (left x .025 w .40, right x .575 w .40, full height); writes <out>-{base,full}_left/_right
  --mode row   (K07): five identical rackets, Command / Pace alternating (C P C P C, serials KQ-000427..431), the same
                      three-quarter turn, the middle three whole inside the trio crop (x .24 w .52, h .92)
Usage: flock render.lock $PY shots/Kdark_row.py --mode feels --w 5120 --h 2880 --spp 160 --out final/v5k/K08-feel-pair
  KQ_NOGRIP=1 for the Naked twins. --set KEY=VALUE overrides this script's constants; --kd KEY=VALUE K11-dark's.
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("K11dark", os.path.join(HERE, "K11-dark.py"))
KD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(KD)

bpy, C, studio, np, Vector = KD.bpy, KD.C, KD.studio, KD.np, KD.Vector
from mathutils import Matrix  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
import k789_lib as KL7  # noqa: E402

# ------------------------------------------------------------------ layout
F_YAW, F_ROLL = 30.0, 6.0          # feels: each turned toward the centre by F_YAW, leaning out by F_ROLL
F_CX = (0.225, 0.775)              # feels: racket centres in the frame (the crops' centres)
F_H = 0.80                         # feels: racket height as a fraction of the frame height
F_LENS = 85.0
R_YAW, R_ROLL = 32.0, -5.0         # row: all five turned the same way
R_N = 5
R_SPAN = 0.68                      # row: first to last racket centre, fraction of the frame width
R_H = 0.52                         # row: racket height as a fraction of the frame height
R_LENS = 70.0
R_VC = 0.47                        # row: the rackets' vertical centre (fraction from the bottom); the trio crop is h .92
CAM_EL = -2.0
FEELS_ROW = ("command", "pace", "command", "pace", "command")


def args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    o = {"w": 960, "h": 540, "spp": 32, "out": "kdr/prev", "mode": "feels"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            o[a[2:]] = argv[i + 1]
            i += 2
        else:
            o[a[2:]] = True
            i += 1
    for k in ("w", "h", "spp"):
        o[k] = int(o[k])
    for key, mod in (("set", globals()), ("kd", vars(KD))):
        if o.get(key):
            for kv in str(o[key]).split(","):
                k, v = kv.split("=")
                mod[k.strip()] = float(v)
    return o


def frame_of(r):
    M = r.matrix_world
    return (M.translation.copy(), (M.to_3x3() @ Vector((0, 1, 0))).normalized(),
            (M.to_3x3() @ Vector((1, 0, 0))).normalized(), (M.to_3x3() @ Vector((0, 0, 1))).normalized())


def proj_box(sc, cam, r):
    pts = KD.sample_points([r], every=9)
    uv = np.array([world_to_camera_view(sc, cam, p)[:2] for p in pts])
    return uv[:, 0].min(), uv[:, 0].max(), uv[:, 1].min(), uv[:, 1].max()


def place(o, roots, xs, yaws, rolls):
    for r, x, y_, rl in zip(roots, xs, yaws, rolls):
        C.pose(r, (x, 0.0, KD.HC), yaw_deg=y_, roll_deg=rl, tilt_deg=90.0)
    bpy.context.view_layer.update()


def layout(sc, o, roots):
    """Spacing, camera distance and shift: rackets' heights at H_frac, their centres at the target x fractions."""
    feels = o["mode"] == "feels"
    n = len(roots)
    if feels:
        yaws, rolls, tx = [F_YAW, -F_YAW], [-F_ROLL, F_ROLL], list(F_CX)
        hfrac, lens, vc = F_H, F_LENS, 0.5
    else:
        yaws, rolls = [R_YAW] * n, [R_ROLL] * n
        tx = [0.5 - R_SPAN / 2 + R_SPAN * i / (n - 1) for i in range(n)]
        hfrac, lens, vc = R_H, R_LENS, R_VC
    sp = 0.5
    el = math.radians(CAM_EL)
    dirn = Vector((0.0, -math.cos(el), math.sin(el)))
    cam = studio.camera((0, -3, 1), (0, 0, 1), lens=lens)
    sc.camera = cam
    d = 3.0
    for _ in range(5):
        xs = [(i - (n - 1) / 2) * sp for i in range(n)]
        place(o, roots, xs, yaws, rolls)
        pts = KD.sample_points(roots, every=11)
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        aim = (lo + hi) / 2
        aim.x = 0.0
        for _k in range(4):
            cam.location = aim + dirn * d
            studio.aim(cam, aim)
            cam.data.shift_x = cam.data.shift_y = 0.0
            bpy.context.view_layer.update()
            boxes = [proj_box(sc, cam, r) for r in roots]
            hmax = max(b[3] - b[2] for b in boxes)
            d *= hmax / hfrac
        cam.location = aim + dirn * d
        studio.aim(cam, aim)
        bpy.context.view_layer.update()
        boxes = [proj_box(sc, cam, r) for r in roots]
        cx = [(b[0] + b[1]) / 2 for b in boxes]
        span_now = cx[-1] - cx[0]
        span_want = tx[-1] - tx[0]
        sp *= span_want / span_now
    v0 = min(b[2] for b in boxes)
    v1 = max(b[3] for b in boxes)
    asp = sc.render.resolution_y / sc.render.resolution_x
    cam.data.shift_y = ((v0 + v1) / 2 - vc) * asp
    cxm = (cx[0] + cx[-1]) / 2
    cam.data.shift_x = cxm - 0.5
    bpy.context.view_layer.update()
    boxes = [proj_box(sc, cam, r) for r in roots]
    print("layout spacing %.3f m, distance %.3f m, lens %.0f" % (sp, d, lens))
    for i, b in enumerate(boxes):
        print("  racket %d box x %.3f-%.3f y %.3f-%.3f" % (i, b[0], b[1], 1 - b[3], 1 - b[2]))
    return cam, boxes


def lights_for(r, i, cam, side):
    """One racket's light set, linked to it alone. side: +1 key from the racket's left (camera view), -1 its right."""
    c, up, across, nrm = frame_of(r)
    pace = r.get("kq_feel") == "pace"
    mine = C.objs(r, "all")
    v = (cam.location - c).normalized()
    mirror = (2 * v.dot(nrm) * nrm - v).normalized()
    ax_up = mirror.cross(up).normalized()
    # the key: KD's offsets are in the racket's own frame; the across axis turns with the racket, so for a racket
    # turned the other way (side -1) the key comes from its other (outer) side
    kl = c + up * KD.KEY_UP + across * (KD.KEY_SIDE * side) + nrm * KD.KEY_OUT
    key = studio.spot_light("lg_key_%d" % i, tuple(kl), KD.KEY_S, KD.KEY_DEG, blend=KD.KEY_BLEND,
                            color=KD.kelvin(5600.0), target=tuple(c + up * KD.KEY_AIM_UP + across * (KD.KEY_AIM_SIDE * side)),
                            radius=KD.KEY_SIZE)
    key.lightgroup = "key"
    # Pace: the key never on the face or bores (from these off-axis angles its glare fell inside the 12K tapes' wide
    # sheen lobes as a bright arc; on K11's single it added nothing there); it still rakes the edge, neck and handle
    KL7.link_receivers(key, [ob_ for k, ob_ in C.parts(r).items() if not (pace and k in ("face", "holes"))],
                       "recv_key_%d" % i)
    sd = (Matrix.Rotation(math.radians(KD.SHEEN_EL), 3, ax_up) @ mirror).normalized()
    sh = studio.area_light("lg_sheen_%d" % i, tuple(c + sd * KD.SHEEN_D), KD.SHEEN_LEN, KD.SHEEN_S,
                           color=KD.kelvin(6200.0), size_y=KD.SHEEN_W, target=tuple(c))
    lx = sh.matrix_world.to_3x3() @ Vector((1, 0, 0))
    ang = lx.angle(across)
    sh.rotation_euler.rotate(Matrix.Rotation(ang if lx.cross(across).dot(-sd) >= 0 else -ang, 3, -sd).to_euler())
    sh.visible_diffuse = False
    sh.lightgroup = "sheen"
    KL7.link_receivers(sh, mine, "recv_sheen_%d" % i)
    vc = (cam.location - c)
    vc.z = 0.0
    vc.normalize()
    if pace:
        dirn = (Matrix.Rotation(math.radians(KD.WEAVE_UP), 3, ax_up) @ mirror).normalized()
        wc = studio.area_light("lg_weave_%d" % i, tuple(c + dirn * 1.6), KD.WEAVE_SIZE, KD.P_WEAVE_S,
                               color=KD.kelvin(6200.0), target=tuple(c))
        wc.visible_diffuse = False
        wc.lightgroup = "sheen"
        KL7.link_receivers(wc, mine, "recv_weave_%d" % i)
        mid = c - up * 0.10
        recv = [ob_ for k, ob_ in C.parts(r).items()
                if k not in ("holes", "throat", "bridgewall", "grip", "wall") and not k.startswith("thr")]
        for sgn, nm in ((1, "L"), (-1, "R")):
            # the wide strip on the side the face turns away from (the handle's facets there need it)
            wide = (sgn < 0) == (side > 0)
            az_ = (KD.RIM_AZ_R if wide else KD.RIM_AZ) * (-1 if sgn < 0 else 1) * (1 if sgn > 0 else 1)
            az_ = sgn * abs(KD.RIM_AZ_R if wide else KD.RIM_AZ)
            rd = (Matrix.Rotation(math.radians(az_), 3, Vector((0, 0, 1))) @ vc).normalized()
            rl_ = studio.area_light("lg_rim%s_%d" % (nm, i), tuple(mid + rd * KD.RIM_D),
                                    KD.RIM_W_R if wide else KD.RIM_W, KD.RIM_S_R if wide else KD.P_RIM_S,
                                    color=KD.kelvin(8000.0), size_y=KD.RIM_LEN, target=tuple(mid))
            ly = rl_.matrix_world.to_3x3() @ Vector((0, 1, 0))
            z = Vector((0, 0, 1))
            ang = ly.angle(z)
            rl_.rotation_euler.rotate(Matrix.Rotation(ang if ly.cross(z).dot(-rd) >= 0 else -ang, 3, -rd).to_euler())
            rl_.visible_diffuse = False
            rl_.lightgroup = "sheen"
            KL7.link_receivers(rl_, recv, "recv_rim%s_%d" % (nm, i))
    else:
        if KD.HANDLE_S > 0:
            hc = c - up * 0.24
            hd = (Matrix.Rotation(math.radians(KD.HANDLE_AZ * side), 3, Vector((0, 0, 1))) @ vc).normalized()
            hl = studio.area_light("lg_handle_%d" % i, tuple(hc + hd * KD.HANDLE_D), 0.04, KD.HANDLE_S,
                                   color=KD.kelvin(6200.0), size_y=0.32, target=tuple(hc))
            ly = hl.matrix_world.to_3x3() @ Vector((0, 1, 0))
            ang = ly.angle(up)
            hl.rotation_euler.rotate(Matrix.Rotation(ang if ly.cross(up).dot(-hd) >= 0 else -ang, 3, -hd).to_euler())
            hl.visible_diffuse = False
            hl.lightgroup = "sheen"
            KL7.link_receivers(hl, mine, "recv_handle_%d" % i)
        if KD.CMD_WALL_S > 0:
            wd = (Matrix.Rotation(math.radians(-55.0 * side), 3, Vector((0, 0, 1))) @ (cam.location - c).normalized())
            wl = studio.area_light("lg_wall_%d" % i, tuple(c - up * 0.12 + wd * 0.8), 0.5, KD.CMD_WALL_S,
                                   color=KD.kelvin(6500.0), size_y=0.6, target=tuple(c - up * 0.12))
            wl.visible_glossy = False
            wl.lightgroup = "fill"
            KL7.link_receivers(wl, C.objs(r, "wall", "neck", "rim"), "recv_wall_%d" % i)


def crops16(paths, crops):
    """<name>_<crop>.png for each (name, x0, w) crop (full height), lossless 16-bit, as K11-dark's card crops."""
    out = []
    saved = (KD.CARD_X0, KD.CARD_W)
    for nm, x0, w in crops:
        KD.CARD_X0, KD.CARD_W = x0, w
        for p in KD.card_crops(paths):
            dst = p.replace("_card.png", "_" + nm + ".png")
            os.replace(p, dst)
            out.append(dst)
    KD.CARD_X0, KD.CARD_W = saved
    return out


def main():
    o = args()
    import time
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
    sc.cycles.sample_clamp_indirect = KD.CLAMP_IND
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in KD.GROUPS:
        vl.lightgroups.add(name=g)
    feels = ("command", "pace") if o["mode"] == "feels" else FEELS_ROW
    roots = []
    for i, f in enumerate(feels):
        r, _ = C.build_racket("KQ_%d" % i, feel=f, serial="KQ-%06d" % (427 + i))
        roots.append(r)
    for r in roots:
        P = C.parts(r)
        if "holes" in P:
            KD.set_glow(P["holes"], "depth", KD.GLOW_S)
        for k, ob in P.items():
            if k == "throat" or k.startswith("thr") or k == "bridgewall":
                KD.set_glow(ob, "depth", KD.GLOW_S * KD.THROAT_GLOW)
        eg = KD.EDGE_GLOW if r.get("kq_feel") == "pace" else KD.CMD_EDGE_GLOW
        if "rim" in P and eg > 0:
            KD.set_glow(P["rim"], "edge", eg)
        if r.get("kq_feel") == "pace" and "neck" in P:
            y_cut = max(v.co.y for v in P["neck"].data.vertices)
            KD.continuous_coat(P["neck"])
            if "rim" in P:
                KD.continuous_coat(P["rim"], y_cut)
    if o["mode"] == "row":
        # the row: a Pace face mirrored its lit white neighbour as a bright arc; the Command rackets are left out of
        # glossy rays (their own lacquer still mirrors the lights)
        for r in roots:
            if r.get("kq_feel") != "pace":
                for ob_ in C.objs(r, "all"):
                    ob_.visible_glossy = False
    KD.world_field(sc)
    cam, boxes = layout(sc, o, roots)
    for i, r in enumerate(roots):
        side = -1 if (o["mode"] == "feels" and i == 1) else 1
        lights_for(r, i, cam, side)
    fl = studio.area_light("lg_fill", tuple(cam.location * 0.6 + Vector((0.0, 0.0, 0.25))), 1.6, KD.FILL_S,
                           color=KD.kelvin(7500.0), target=(0.0, 0.0, KD.HC - 0.1))
    fl.lightgroup = "fill"
    for ob_ in sc.objects:
        if ob_.type == "LIGHT":
            ob_.visible_camera = False
    if o.get("dry"):
        return
    sc.use_nodes = True
    tr = sc.node_tree
    for n_ in list(tr.nodes):
        tr.nodes.remove(n_)
    rl = tr.nodes.new("CompositorNodeRLayers")
    src = {g: rl.outputs["Combined_" + g] for g in KD.GROUPS}
    src["albedo"] = rl.outputs["Denoising Albedo"]
    src["normal"] = rl.outputs["Denoising Normal"]
    out_stem = KD.out_path(o["out"])[:-4]
    written = KD.build_comp(sc, src, o, out_stem)
    sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.exr_codec = "ZIP"
    sc.render.filepath = out_stem + ".exr"
    bpy.ops.render.render(write_still=True)
    paths = KD.finish_outputs(out_stem, written)
    extra = []
    if o["mode"] == "feels":
        extra = crops16(paths, [("left", 0.025, 0.40), ("right", 0.575, 0.40)])
    print("rendered", paths + extra, round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
