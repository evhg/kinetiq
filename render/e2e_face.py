"""e2e_face.py (2026-11-14, the Mac render node): cloud REQUEST e2e-c's face check: the flat face's mean luma (8-bit sRGB,
Rec. 709 weights) on <stem>-full.png over <stem>-mask.png (the face's own AOV: no holes, no ball, no rings), against
K01-full's face at the same measure: Command 137.4, Pace 44.0 (K01-hero-beam(-pace)-v5k-full.png, the box x 0.44-0.57,
y 0.30-0.55 with the holes taken out: Command's are ~6.4 % of it, black).
  python e2e_face.py <stem> <command|pace> [<twin stem>]    exit 3 if more than 2 luma off K01 (or off the twin)
"""
import sys

import numpy as np
from PIL import Image

K01 = {"command": 137.4, "pace": 44.0}


def face(stem):
    a = np.asarray(Image.open(stem + "-full.png").convert("RGB")).astype(np.float32) @ np.array([.2126, .7152, .0722])
    mk = np.asarray(Image.open(stem + "-mask.png").convert("L")) > 250
    return float(a[mk].mean())


def main():
    stem, feel = sys.argv[1], sys.argv[2]
    m = face(stem)
    ok = abs(m - K01[feel]) <= 2.0
    msg = "face %.1f (K01 %.1f)" % (m, K01[feel])
    if len(sys.argv) > 3:
        t = face(sys.argv[3])
        ok = ok and abs(m - t) <= 2.0
        msg += ", twin %.1f" % t
    print(msg)
    print("mean=%.2f" % m, file=sys.stderr)
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
