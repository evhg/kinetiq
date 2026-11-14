"""e2e_wall.py (2026-11-14, the Mac render node): cloud REVIEW e2e-c 10:52Z: Cwide Pace's left wall must be no brighter
than K11-full-pace's. Per row of the head (rows with flat-face pixels in <stem>-mask.png), the peak luma (8-bit sRGB,
Rec. 709) of <stem>-full.png between the racket's first pixel from the left (luma > 12) and the first flat-face pixel:
the wall and rim band. K11-single-pace-full (v5k) measured the same way by hand: median 150, p90 193 (its wall left of
the face). Pass: median <= 152 and at most 5 % of the rows with a clipped (>= 250) pixel (a small crown highlight from
the face's own sheen strip stays, as in K11-full-pace, which has 55 clipped pixels at 1920; the fixed line ran down
every row).
  python e2e_wall.py <stem>     prints "wall median M p90 P clipped N", exit 3 if it fails
"""
import sys

import numpy as np
from PIL import Image

K11 = (150.0, 193.0)


def wall(stem):
    l = np.asarray(Image.open(stem + "-full.png").convert("RGB")).astype(np.float32) @ np.array([.2126, .7152, .0722])
    mk = np.asarray(Image.open(stem + "-mask.png").convert("L")) > 250
    pk, clip, rows = [], 0, 0
    for y in np.nonzero(mk.any(1))[0]:
        f = int(np.argmax(mk[y]))
        r = l[y, :f]
        if not (r > 12).any():
            continue
        x0 = int(np.argmax(r > 12))
        b = r[x0:f]
        pk.append(float(b.max()))
        c = int((b >= 250).sum())
        clip += c
        rows += c > 0
    return float(np.median(pk)), float(np.percentile(pk, 90)), clip, rows / max(len(pk), 1)


def main():
    med, p90, clip, fr = wall(sys.argv[1])
    print("wall median %.0f p90 %.0f, clipped %d px in %.1f %% of rows (K11-full-pace %.0f / %.0f)" % (med, p90, clip, fr * 100, *K11))
    sys.exit(0 if med <= K11[0] + 2 and fr <= 0.05 else 3)


if __name__ == "__main__":
    main()
