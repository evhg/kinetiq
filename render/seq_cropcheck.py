"""seq_cropcheck.py: does a swivel's --crop region hold everything that moves? (2026-11-02, queue-swivels.sh)

python3 seq_cropcheck.py <seq dir> <last index> x0 x1 y0 y1

Frames 1.. are border renders pasted into frame 0, so nothing can change outside the region; what shows a region that
is too small is CHANGE AT ITS EDGE: the racket, its shadow or a reflection cut off by the region's border. Compares
frame 0 with the last frame (the end of the turn), luma 0-255 at half size: prints the bounding box of the pixels that
changed by more than 10 luma, and the share of changed pixels in a band 2 % of the frame wide just inside each edge of
the region that lies inside the frame. Exit 0 = OK, 2 = an edge band changed (more than 0.5 % of its pixels).
"""
import os
import sys

import numpy as np
from PIL import Image

d, last = sys.argv[1], int(sys.argv[2])
x0, x1, y0, y1 = [float(v) for v in sys.argv[3:7]]
W8 = np.array([0.2126, 0.7152, 0.0722])


def load(i):
    im = Image.open(os.path.join(d, "f%03d.png" % i)).convert("RGB")
    im = im.resize((im.size[0] // 2, im.size[1] // 2), Image.BOX)
    return np.asarray(im).astype(np.float32) @ W8


a, b = load(0), load(last)
H, W = a.shape
ch = np.abs(a - b) > 10
ys, xs = np.nonzero(ch)
box = (xs.min() / W, xs.max() / W, ys.min() / H, ys.max() / H) if len(xs) else None
band = 0.02
px0, px1, py0, py1 = int(x0 * W), int(x1 * W), int(y0 * H), int(y1 * H)
bw, bh = max(1, int(band * W)), max(1, int(band * H))
edges = {}
if x0 > 0:
    edges["left"] = ch[py0:py1, px0:px0 + bw]
if x1 < 1:
    edges["right"] = ch[py0:py1, px1 - bw:px1]
if y0 > 0:
    edges["top"] = ch[py0:py0 + bh, px0:px1]
if y1 < 1:
    edges["bottom"] = ch[py1 - bh:py1, px0:px1]
frac = {k: float(v.mean()) for k, v in edges.items()}
bad = [k for k, v in frac.items() if v > 0.005]
print("cropcheck %s last=%d change box x %s y %s | region x %.2f-%.2f y %.2f-%.2f | edge bands %s -> %s" % (
    os.path.basename(d), last,
    "%.3f-%.3f" % box[:2] if box else "-", "%.3f-%.3f" % box[2:] if box else "-", x0, x1, y0, y1,
    " ".join("%s %.4f" % kv for kv in frac.items()), "FAIL " + ",".join(bad) if bad else "OK"), flush=True)
sys.exit(2 if bad else 0)
