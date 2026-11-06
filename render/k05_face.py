"""k05_face.py [label=]img ... (req-nov6.sh, K05-command-fix): mean display luma of the K05 face, the v6 still vs the
new render, at 2560x1440 and 1440x810. Face mask: the head box of the K05 wide frame (x 0.415-0.775, y 0.36-0.92),
pixels with luma > 70 and a small red excess (the laser and its halo out). Prints one line: label 2560 / 1440; ..."""
import sys

import numpy as np
from PIL import Image

W = np.array([0.2126, 0.7152, 0.0722])
res = []
for arg in sys.argv[1:]:
    label, f = arg.split("=", 1) if "=" in arg else (arg.split("/")[-1], arg)
    im = Image.open(f).convert("RGB")
    v = []
    for (w, h) in ((2560, 1440), (1440, 810)):
        a = np.asarray(im.resize((w, h), Image.LANCZOS), dtype=float)
        L = a @ W
        box = np.zeros_like(L, bool)
        box[int(0.36 * h):int(0.92 * h), int(0.415 * w):int(0.775 * w)] = True
        m = box & (L > 70) & ((a[..., 0] - a[..., 1]) < 25)
        v.append("%.1f" % L[m].mean())
    res.append("%s %s" % (label, " / ".join(v)))
print("; ".join(res))
