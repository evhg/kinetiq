"""K16-pair (2026-10-29): drilled against moulded, rendered, in K04's language. Owner, 2026-10-29: keep G06 (the 2D
diagram) and add "one 3D visualization": the same white 3K twill plate at the same scale, LEFT a drilled bore (the
tows cut dead at a chipped edge, frayed resin, the laminate's cut plies and the EVA core exposed in the wall), RIGHT a
moulded bore (K04: the twill flowing round a lined lip, the warm bore glow). Claims: none beyond the Holes copy
(drilling cuts the fibres and opens the core; moulding wraps them).

How: K04-hole-macro.py runs twice with one camera and one light rig (so the halves share scale, perspective and light):
  --mode moulded : K04's own scene (bake-warped twill round every hole, lined lips, bore glow)
  --mode drilled : K04's rig on a drilled plate built here: straight twill (the canon white twill on planar
                   coordinates: kq_canon's recipe via K04's white_sleeve, re-coordinated), holes cut straight through
                   with a chipped edge, a band of stress-whitened, crazed resin round each rim, fibre stubs standing
                   off the cut, and a wall that shows the cut plies (skin) over the exposed EVA core.
Both halves centre the hero hole (K04's copy-side shift, gobo, flag and burn are off). Each run writes -base and
-full (K04's composites: full adds the amber ring and the bore glow; the drilled bore has no glow: its wall is foam).
Then --combine pastes drilled | moulded side by side with a thin graphite gutter: <out>-base.png, <out>-full.png.
For the site, the "full" layer adds only the moulded side's glow (drilled half identical in both), so the scroll
light lands on the moulded hole alone.

Usage (from render/, one Blender at a time through the lock):
  flock render.lock $PY shots/K16-pair.py --mode drilled --w 720 --h 810 --spp 24 --out k16/d01
  flock render.lock $PY shots/K16-pair.py --mode moulded --w 720 --h 810 --spp 24 --out k16/m01
  $PY shots/K16-pair.py --combine k16/d01 k16/m01 --out k16/pair01      (no render: bpy reads the PNGs)
Extra K04 flags pass straight through (e.g. --pool 30 --fstop 48). K16-only: --mode, --shift_x (default 0),
--yaw, --fw (mm, default 30), --skin (mm, cut carbon skin depth, default 1.6), --chip (mm, default 0.35).
"""
import importlib.util
import inspect
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

# K16 defaults on top of K04's (a K04 flag given on the command line still wins)
K16_DEFAULTS = dict(fw="30", gobo="0", burn="1.0", flag_x="-1", shade="0", pool="26", pool_x="0.78", pool_y="0.42",
                    focus="1.0", fstop="48", glow_left="1.0", sheen_u="0.5", sheen_v="0.16")


def _argval(argv, key, default=None):
    if "--" + key in argv:
        i = argv.index("--" + key)
        return argv[i + 1]
    return default


def combine(argv):
    """drilled | moulded side by side (16-bit PNG via numpy), a thin graphite gutter between. Writes -base and -full;
    the full drilled half is the drilled base (no glow in a foam wall)."""
    import numpy as np
    import kqpaths
    i = argv.index("--combine")
    dstem, mstem = argv[i + 1], argv[i + 2]
    out = _argval(argv, "out")
    gutter = float(_argval(argv, "gutter", "0.006"))
    gcol = float(_argval(argv, "gutter_luma", "0.075"))

    def p(s):
        return s if os.path.isabs(s) else os.path.join(kqpaths.OUT, s)

    import png16
    load = png16.read

    for v in ("base", "full"):
        d = load(p(dstem) + "-base.png")
        m = load(p(mstem) + "-" + v + ".png")
        h, w = d.shape[:2]
        g = int(round(gutter * 2 * w))
        outimg = np.full((h, 2 * w + g, 3), gcol)
        outimg[:, :w] = d[..., :3]
        outimg[:, w + g:] = m[..., :3]
        import png16
        png16.write(p(out) + "-" + v + ".png", outimg)
        print("combined", p(out) + "-" + v + ".png", outimg.shape)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if "--combine" in argv:
        return combine(argv)
    mode = _argval(argv, "mode", "moulded")
    shift_x = float(_argval(argv, "shift_x", "0"))
    skin = float(_argval(argv, "skin", "1.6")) / 1000.0
    chip = float(_argval(argv, "chip", "0.35")) / 1000.0
    # strip K16-only flags, add K16 defaults, hand the rest to K04
    k04_argv = []
    skip = {"--mode", "--shift_x", "--skin", "--chip"}
    it = iter(range(len(argv)))
    for i in it:
        if argv[i] in skip:
            next(it, None)
            continue
        k04_argv.append(argv[i])
    for k, v in K16_DEFAULTS.items():
        if "--" + k not in k04_argv:
            k04_argv += ["--" + k, v]
    if "--variant" not in k04_argv:
        k04_argv += ["--variant", "both"]
    sys.argv = [sys.argv[0]] + k04_argv

    spec = importlib.util.spec_from_file_location("k04", os.path.join(HERE, "K04-hole-macro.py"))
    K04 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(K04)

    # centred framing: K04 shifts the frame for its copy column; K16 centres the hero hole
    _cam = K04.studio.camera

    def camera(loc, target, lens=85, sensor=36, dof_obj=None, fstop=None, shift=(0, 0)):
        return _cam(loc, target, lens=lens, sensor=sensor, dof_obj=dof_obj, fstop=fstop, shift=(shift_x, 0.0))

    K04.studio.camera = camera
    if mode == "drilled":
        import k16_drilled as D
        D.install(K04, skin=skin, chip=chip)
    K04.main()


if __name__ == "__main__":
    main()
