"""K01-hero-beam: the unveiling. The canonical Command racket (WHITE 3K twill) (shots/kq_canon.py, KQ-000427) standing on its butt cap
in a graphite studio, one floor beam. Desktop master 2560 x 1440; the racket spans 27-81 % of the frame height.

ONE render writes denoised light-group passes; the comp gives three pixel-registered variants (see k01_lib.py):
  -base    dim, waiting: cyclorama, top/rim/lip/grip lights, face sweep at 35 %; no beam (page cross-fade start)
  -full    + the floor beam (lg_key) with haze, face sweep at full, the cap's groove and Q lit (hero)
  -finale  full + lg_horizon: warm first light up the cove behind, warm rim on the head's left edge

Usage (from the blender dir, through the lock):
  flock render.lock ../bpyenv/bin/python shots/K01-hero-beam.py --w 960 --h 540 --spp 32 --out k01v2/beam_p01
  final: flock render.lock ../bpyenv/bin/python shots/K01-hero-beam.py --w 2560 --h 1440 --spp 256 --out final/K01-hero-beam
  Pace (Release 2 feel toggle): add --feel pace and write NEW files, e.g. --out final/K01-hero-beam-pace
  (-> K01-hero-beam-pace-base/-full/-finale.png); --feel command (the default) is the Command output, byte-identical.
  re-comp without rendering: ../bpyenv/bin/python shots/k01_lib.py comp beam <out> [--gain full.face=1.2 ...]
Swivel (Release 3 hero scrub): --yaw DEG (racket turned about its handle, lights fixed); --seq N --yaw-range A B
  --out seq/K01-swivel-command-desktop renders N frames f000.png.. of the full look (resumes). See k01_lib SWIVEL.
Dev: --set NAME=value (any k01_lib constant), --crop x0 x1 y0 y1 (a region at full resolution).
v1 (k12 racket, 460 mm, collar + silver cap): K01-hero-beam.v1.bak
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k01_lib as KL  # noqa: E402


def main():
    o = KL.parse_args(sys.argv[1:], "K01-hero-beam")
    if o.get("seq"):
        KL.render_seq(o, "beam", "beam")
    else:
        KL.render(o, "beam", "beam")


if __name__ == "__main__":
    main()
