"""Fill-rule check for a render: python fillcheck.py <png> [<png> ...]
Prints the share of flat-black pixels (luma <= 12 on 0-255 display values), lit pixels (luma >= 40), and the widest
flat-black vertical strip, for the full 16:9 frame and for the central 16:10 crop (what a 1440x900 screen shows).
PASS needs: dark <= 40%, lit >= 8%, dead strip < 25% of the width. The site's harness fails pages that break it."""
import sys
import numpy as np
from PIL import Image


def stats(a):
    l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    dark = (l <= 12).mean()
    lit = (l >= 40).mean()
    colLit = (l > 12).any(axis=0)
    run = best = 0
    for v in colLit:
        run = 0 if v else run + 1
        best = max(best, run)
    return dark, lit, best / l.shape[1]


for p in sys.argv[1:]:
    im = Image.open(p).convert("RGB")
    im.thumbnail((384, 384))
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    cw = int(h * 16 / 10)
    crop = a[:, max(0, (w - cw) // 2): (w + cw) // 2] if cw < w else a
    for name, arr in (("16:9", a), ("16:10", crop)):
        d, li, s = stats(arr)
        ok = d <= 0.40 and li >= 0.08 and s < 0.25
        print(f"{p} [{name}] dark {d:.0%} lit {li:.0%} dead-strip {s:.0%} -> {'PASS' if ok else 'FAIL'}")
