"""K01-hero-frame (phone): the K01 hero look reframed for the phone's text bands. Canonical Command racket
(shots/kq_canon.py, KQ-000427). 9:16 master 1440 x 2560: camera 4.20 m back, level, lens from the aspect; head top at
51 %, cap at 81 % of the frame height (the words sit above, the CTA just below the cap).

ONE render writes denoised light-group passes; the comp gives two pixel-registered variants (see k01_lib.py):
  -base (dim, no beam, face sweep at 35 %) and -full (beam, face sweep at full, cap groove and Q lit).

Usage (from the blender dir, through the lock):
  flock render.lock ../bpyenv/bin/python shots/K01-hero-frame.py --w 540 --h 960 --spp 32 --out k01v2/phone_p01
  final: flock render.lock ../bpyenv/bin/python shots/K01-hero-frame.py --w 1440 --h 2560 --spp 256 --out final/K01-hero-frame-phone
  Pace: add --feel pace --out final/K01-hero-frame-phone-pace (-> K01-hero-frame-phone-pace-base/-full.png).
Swivel: --yaw DEG, or --seq N --yaw-range A B --out seq/<dir> (see k01_lib SWIVEL / render_seq).
The desktop hero-frame masters (K01-hero-frame-base/full.png) are unused by the site and are not re-rendered.
v1 (k12 racket): K01-hero-frame.v1.bak
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k01_lib as KL  # noqa: E402


def main():
    o = KL.parse_args(sys.argv[1:], "K01-hero-frame")
    if o.get("seq"):
        KL.render_seq(o, "phone", "phone")
    else:
        KL.render(o, "phone", "phone")


if __name__ == "__main__":
    main()
