"""K09-dark: K09 (the One of Ten case of three, gallery 4:3 and card 4:5, grip and Naked, both feels) in K04's language
(cloud REQUEST k04-language-fix (3), 2026-11-07 21:51Z): the K09 case scene as it is (shots/K09-case-three.py: case,
felt, lid LED, plaque, the three canon rackets and their per-racket rig, same cameras and frames), with
  - the near-black field: the floor's and the void's camera-only lift taken down to K11-dark's level;
  - a low raking key from the crowns' side (camera-left, behind the heads), K11-dark's 5600 K spot, linked to the
    rackets and the felt, so each head falls from a lit crown to shade at the throat;
  - the case kept readable: its silver chamfer lines, satin walls, the lid LED and the plaque as in K09, the old high key
    on the case at CASE_KEY of its power;
  - the overgrips K11-dark's canon black (no case light on them; GripStrip as in K09);
  - base and full from one render: full = base + the 2700 K glow in the bores and the throat and the warm edge line
    (K11-dark's set_glow, its own light group); the card also writes -hover-{base,full} (the lid group x 2.3).
Usage: ../bpyenv/bin/python shots/K09-dark.py --variant gallery|card [--feel pace] --w --h --spp --out <stem>
  --set KEY=VALUE[,..] overrides this file's upper-case constants.
Outputs: <out>-base.png, <out>-full.png (card: also <out>-hover-base.png, <out>-hover-full.png).
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


KC = _load("K09case", "K09-case-three.py")     # reads --feel from argv at import
KD = _load("K11dark", "K11-dark.py")
bpy, C, studio, Vector, L = KC.bpy, KC.C, KC.studio, KC.Vector, KC.L

FIELD_FLOOR = (0.0015, 0.0035)  # the floor's camera-only lift (K09: 0.030 .. 0.052)
FIELD_VOID = (0.0020, 0.0045)   # the void behind the lid (K09: 0.024 .. 0.062)
CASE_KEY = 0.45                 # K09's high key on the case and felt, scaled
RAKE_S = 900.0                  # W: the raking key from the crowns' side
RAKE_DEG, RAKE_BLEND, RAKE_SIZE = 26.0, 0.7, 0.06
RAKE_AT = (-1.05, 0.62, 0.42)   # world: camera-left and behind the heads, low
RAKE_AIM = (0.10, 0.02, 0.03)
CMD_PER = 1.0                   # Command: one raking spot per racket (same offset from each head), so all three fall
CMD_RAKE_S = 500.0              # identically from a lit crown to white-in-shade at the throat (the shared spot lit
CMD_RAKE_OFF = (-0.40, 0.10, 0.26)   # them flat); world offset from each head centre, aimed CMD_RAKE_AIM_DY toward the crown
CMD_RAKE_AIM_DY = 0.11
CMD_RAKE_DEG, CMD_RAKE_BLEND = 24.0, 0.75
CMD_POOL, CMD_NECK = 20.0, 10.0       # K09's white per-racket pool and neck spots, turned down (240 / 60)
RAKE_FELT = 0.35                # the felt's share of it (a second spot, same place, linked to the felt only)
GLOW_S = 30.0                   # K11-dark's bore / throat glow (W-equivalent emission strength)
THROAT_GLOW = 0.0               # pace-dark-fix (d): the throat drew a copper swoosh on both feels; dropped
EDGE_GLOW_CMD, EDGE_GLOW_PACE = 16.0, 2.2
HOVER_GAIN = 2.3
P_GLOW = 1.3                    # Pace: the bore glow x 1.3 (cloud REVIEW 22:20Z)
P_GLOW_LIP = 0.35               # pace-dark-fix: with the lip glow (seen almost down the bores here) x 0.35, or the rings
                                # blow out pale
P9_GRADE_S, P9_GRADE_OFF = 20.0, -20.0   # pace-dark-fix: K11-dark's graded card in the case (flat rackets, high camera)
P_OUT_S = 110.0                 # Pace: K11-dark's thin cool outline: big glossy-only cards linked to each racket's edge
P_OUT_CARDS = ((0.0, 0.30, 0.90, 1.0), (-1.6, -0.2, 1.2, 1.6), (1.6, -0.2, 1.2, 1.6))  # radius and neck: (x, y, z, size)
P_OUT_K = 8000.0
P_NAKED_NECK_OFF = 1.0       # Pace Naked: the face cards and the outline leave the neck (the bare handle) alone


def parse():
    a = L.parse_args(sys.argv[1:], "k09d/prev")
    if "--set" in sys.argv:
        for kv in sys.argv[sys.argv.index("--set") + 1].split(","):
            k, v = kv.split("=")
            g = globals()
            if k in g:
                g[k] = type(g[k])(v) if not isinstance(g[k], tuple) else tuple(float(x) for x in v.split("/"))
            elif hasattr(KC, k):
                setattr(KC, k, float(v))
            elif hasattr(KD, k):
                setattr(KD, k, float(v))
    a["lightgroups"] = True
    return a


def main():
    a = parse()
    KC.FLOOR_E, KC.VOID_E = FIELD_FLOOR, FIELD_VOID
    if not KC.PACE:
        KC.KW_POOL, KC.KW_NECK = CMD_POOL, CMD_NECK
    pfix = KC.PACE and KD.P_FIX > 0
    if pfix:   # pace-dark-fix (b): K11-dark's Pace tapes and its weave card scaled
        KC.MAT_OPTS = dict(KC.MAT_OPTS or {}, **KD.pace_opts("pace"))
        KC.P_WEAVE_S *= KD.P_WEAVE_K
        KD.P_GRADE_S, KD.P_GRADE_OFF = P9_GRADE_S, P9_GRADE_OFF
    sc = KC.build(a)
    if os.environ.get("KQ_NOGRIP") == "1":
        L.bare_handle_lights(sc)
        L.pace_handle_weave(sc, up=L.PH_K789[0], roll=L.PH_K789[1])
    vl = sc.view_layers[0]
    vl.cycles.denoising_store_passes = True
    for g in ("lg_key", "lg_lid", "lg_rim", "lg_base", "lg_glow"):
        if g not in [x.name for x in vl.lightgroups]:
            vl.lightgroups.add(name=g)
    roots = [o_ for o_ in sc.objects if o_.type == "EMPTY" and o_.get("kq_feel") is not None]
    if not roots:
        roots = [o_ for o_ in sc.objects if o_.type == "EMPTY" and o_.name in ("KQA", "KQB", "KQC")]
    # the old high key: down to CASE_KEY
    k = bpy.data.objects.get("Key")
    if k is not None:
        k.data.energy *= CASE_KEY
    # the raking key from the crowns' side: rackets (all parts but the overgrip) and, weaker, the felt
    recv = [o_ for r in roots for kk, o_ in C.parts(r).items() if kk != "grip"]
    if KC.PACE or CMD_PER <= 0:
        rk = studio.spot_light("lg_rake", RAKE_AT, RAKE_S, RAKE_DEG, blend=RAKE_BLEND, color=KD.kelvin(5600.0),
                               target=RAKE_AIM, radius=RAKE_SIZE)
        L.link_receivers(rk, recv, "recv_rake_key")
        rk.lightgroup = "lg_key"
    else:
        for r in roots:
            P = C.parts(r)
            hc = P["face"].parent.matrix_world.translation.copy()
            aim = hc + Vector((0.0, CMD_RAKE_AIM_DY, 0.0))
            rk = studio.spot_light("lg_rake_" + r.name, tuple(hc + Vector(CMD_RAKE_OFF)), CMD_RAKE_S, CMD_RAKE_DEG,
                                   blend=CMD_RAKE_BLEND, color=KD.kelvin(5600.0), target=tuple(aim), radius=RAKE_SIZE)
            L.link_receivers(rk, [o_ for kk, o_ in P.items() if kk != "grip"], "recv_rake_" + r.name)
            rk.lightgroup = "lg_key"
    if RAKE_FELT > 0:
        felt = [o_ for o_ in sc.objects if o_.name in ("Felt", "Tray")]
        rf = studio.spot_light("lg_rake_felt", RAKE_AT, RAKE_S * RAKE_FELT, RAKE_DEG + 10, blend=1.0,
                               color=KD.kelvin(5600.0), target=RAKE_AIM, radius=RAKE_SIZE)
        L.link_receivers(rf, felt, "recv_rake_felt")
        rf.lightgroup = "lg_key"
    if KC.PACE and P_OUT_S > 0:
        # the outline: the edge radius and the neck mirror big cool cards (glossy only) from behind and both sides, so
        # each black head draws a thin line round its silhouette against the tray; the face and bores stay black
        edge = [o_ for r in roots for kk, o_ in C.parts(r).items() if kk in ("rim", "neck")]
        for i, (x, y, z, sz) in enumerate(P_OUT_CARDS):
            oc = studio.area_light("lg_outline%d" % i, (x, y, z), sz, P_OUT_S * (KD.P_RIM_K if pfix else 1.0),
                                   color=KD.kelvin(P_OUT_K),
                                   target=(0.0, KC.HEAD_Y, 0.03))
            oc.visible_diffuse = False
            L.link_receivers(oc, edge, "recv_outline%d" % i)
            oc.lightgroup = "lg_key"
    if pfix:   # pace-dark-fix (a): K11-dark's broad graded card, one per racket, linked to it alone
        for r in roots:
            gc_ = KD.grade_card([r], sc.camera)
            if gc_ is not None:
                gc_.lightgroup = "lg_key"
    if KC.PACE and os.environ.get("KQ_NOGRIP") == "1" and P_NAKED_NECK_OFF > 0:
        # Pace Naked: the bare handle is the neck mesh, a glossy black cylinder that mirrored every face card linked to
        # the neck (the lid band, the lid stand-in, the weave card, the outline) as a silver shaft (fw-k09dark 22:39Z);
        # those cards light the head only, the handle keeps its own (k789 bare-handle lines and the Pace handle card)
        necks = {C.parts(r)["neck"] for r in roots if "neck" in C.parts(r)}
        for cn in ("recv_face", "recv_pacelid", "recv_paceweave", "recv_outline0", "recv_outline1", "recv_outline2") + \
                tuple(c_.name for c_ in bpy.data.collections if c_.name.startswith("recv_grade")):
            col = bpy.data.collections.get(cn)
            if col is None:
                continue
            for nk in necks:
                if nk.name in col.objects:
                    col.objects.unlink(nk)
    # the glow (full pass only): bores, throat, the warm edge line
    gs = GLOW_S * (P_GLOW if KC.PACE else 1.0) * (P_GLOW_LIP if (pfix and KD.P_LIP > 0) else 1.0)
    for r in roots:
        P = C.parts(r)
        if "holes" in P:   # pace-dark-fix (c): Pace bores glow in a thin band inside each lip
            KD.set_glow(P["holes"], "lip" if (pfix and KD.P_LIP > 0) else "depth", gs)
        for kk, ob in P.items():
            if (kk == "throat" or kk.startswith("thr") or kk == "bridgewall") and THROAT_GLOW > 0:
                KD.set_glow(ob, "depth", gs * THROAT_GLOW)
        eg = EDGE_GLOW_PACE if r.get("kq_feel") == "pace" else EDGE_GLOW_CMD
        if "rim" in P and eg > 0:
            KD.set_glow(P["rim"], "edge", eg)
        for kk, ob in P.items():
            if ob.lightgroup == "glow":
                ob.lightgroup = "lg_glow"
    # anything left without a group (Naked handle lights) goes with the key
    for o_ in sc.objects:
        if o_.type == "LIGHT" and not o_.lightgroup:
            o_.lightgroup = "lg_key"
    if sc.world is not None and not sc.world.lightgroup:
        sc.world.lightgroup = "lg_base"
    for o_ in sc.objects:
        if o_.type == "LIGHT":
            o_.visible_camera = False
    for sub in [x for x in os.environ.get("K09D_KILL", "").split(",") if x]:   # debug: lights off by name
        for o_ in sc.objects:
            if sub in o_.name and (o_.type == "LIGHT" or o_.type == "MESH" and not o_.data.vertices or True):
                if o_.type == "LIGHT":
                    o_.data.energy = 0.0
                else:
                    o_.hide_render = True
                print("killed", o_.name, flush=True)
    base = {"lg_key": 1.0, "lg_lid": 1.0, "lg_rim": 1.0, "lg_base": 1.0}
    mixes = {"base": dict(base), "full": dict(base, lg_glow=1.0)}
    if a["variant"].startswith("card"):
        mixes["hover-base"] = dict(base, lg_lid=HOVER_GAIN)
        mixes["hover-full"] = dict(base, lg_lid=HOVER_GAIN, lg_glow=1.0)
    L.mix_compositor(sc, a, mixes)
    print("roots", [r.name for r in roots], flush=True)
    ng = os.environ.pop("KQ_NOGRIP", None)     # render_main would add the Naked handle lights a second time
    try:
        L.render_main(lambda _o: sc, a)
    finally:
        if ng is not None:
            os.environ["KQ_NOGRIP"] = ng
    L.seq_rename(a)


if __name__ == "__main__":
    main()
