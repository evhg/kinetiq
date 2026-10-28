"""pace_probe.py: render a shot's Pace albedo probe (kq_canon.PACE_PROBE = "albedo"): every Pace material becomes an
emission of (base albedo luminance x 10, fibre direction hz, coat weight), view transform Standard, 1 sample per pixel,
a 0.01 px box filter and no denoising, so each pixel holds the exact shader value at its centre. Used by pace_metrics.py
for the per-tape albedo difference and as the tape-parity map for the tile-contrast measurement.

Usage (from the blender dir, through the render lock; same camera and size as the image it measures):
  flock render.lock ../bpyenv/bin/python shots/pace_probe.py K08-feel-pair --w 2560 --h 1440 --out pace_dev/K08_probe
  flock render.lock ../bpyenv/bin/python shots/pace_probe.py K11-pair --weave pace --w 3200 --h 1800 --out pace_dev/K11_probe
  add --v4 to probe the previous canon Pace (stage 3a: aniso 0.9, organic 0, flip 0.30, no fibre layer)
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
C.PACE_PROBE = "albedo"
if "--v4" in argv:
    mod.PACE_V4 = 1.0
if hasattr(mod, "parse"):
    o = mod.parse(argv)
else:
    o = L.parse_args(argv, "pace_dev/probe")
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
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    sc.cycles.samples = 1
    sc.cycles.use_adaptive_sampling = False
    sc.cycles.use_denoising = False
    sc.cycles.filter_width = 0.01
    sc.render.film_transparent = False
    return sc


os.makedirs(os.path.join(L.studio.OUT, os.path.dirname(o["out"]) or "."), exist_ok=True)
L.render_main(build, o)
