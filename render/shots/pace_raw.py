"""pace_raw.py: render a shot exactly as its own script would, but with the denoiser off (review round 6, issue 7:
are the fibre streaks smudged by OIDN or by the noise itself?). Same arguments as the shot (--pace / --set included).

  flock render.lock ../bpyenv/bin/python shots/pace_raw.py K11-pair --weave pace --w 3200 --h 1800 --spp 256 \
      --crop 0.33 0.67 0.08 0.56 --out pace6/K11_raw
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kq_canon as C  # noqa: E402
import k789_lib as L  # noqa: E402

shot = sys.argv[1]
argv = sys.argv[2:]
spec = importlib.util.spec_from_file_location(shot.replace("-", "_"), os.path.join(HERE, shot + ".py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if hasattr(mod, "parse"):
    o = mod.parse(argv)
else:
    o = L.parse_args(argv, "pace6/raw")
    if "--set" in argv:
        for kv in argv[argv.index("--set") + 1].split(","):
            k_, v_ = kv.split("=")
            setattr(mod, k_, float(v_))
    if "--pace" in argv:
        for kv in argv[argv.index("--pace") + 1].split(","):
            k_, v_ = kv.split("=")
            C.PACE[k_] = float(v_)


def build(o_):
    sc = mod.build(o_)
    sc.cycles.use_denoising = False
    return sc


os.makedirs(os.path.join(L.studio.OUT, os.path.dirname(o["out"]) or "."), exist_ok=True)
L.render_main(build, o)
