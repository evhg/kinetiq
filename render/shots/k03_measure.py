"""Luma probes for K03/K03b renders: python k03_measure.py <png> [box x0,x1,y0,y1 (fractions, top-down) ...]"""
import sys
import numpy as np
from PIL import Image


def luma(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2], a


def box(l, x0, x1, y0, y1):
    h, w = l.shape
    return l[int(y0 * h):max(int(y1 * h), int(y0 * h) + 1), int(x0 * w):max(int(x1 * w), int(x0 * w) + 1)]


for p in sys.argv[1:]:
    if "," in p:
        continue
    l, a = luma(p)
    h, w = l.shape
    print(p, w, "x", h)
    probes = {
        "corner TL": (0.0, 0.05, 0.0, 0.06), "corner TR": (0.95, 1.0, 0.0, 0.06),
        "corner BL": (0.0, 0.05, 0.94, 1.0), "corner BR": (0.95, 1.0, 0.94, 1.0),
        "edge L mid": (0.0, 0.04, 0.45, 0.55), "edge R mid": (0.96, 1.0, 0.45, 0.55),
        "top mid": (0.45, 0.55, 0.0, 0.05), "bottom mid": (0.45, 0.55, 0.95, 1.0),
        "behind (above subj)": (0.42, 0.58, 0.26, 0.33), "left of subj": (0.22, 0.28, 0.45, 0.6),
        "right of subj": (0.72, 0.78, 0.45, 0.6), "below subj": (0.42, 0.58, 0.70, 0.76),
        "caption band": (0.3, 0.7, 0.80, 0.94), "x25 y35": (0.24, 0.26, 0.34, 0.36), "x75 y72": (0.74, 0.76, 0.71, 0.73),
    }
    for k, b in probes.items():
        v = box(l, *b)
        print(f"  {k:22s} mean {v.mean():6.1f}  min {v.min():5.0f} max {v.max():5.0f}")
    print(f"  max luma {l.max():.0f}  >=200 {100*(l>=200).mean():.3f}%  >=230 {100*(l>=230).mean():.3f}%")
    for extra in sys.argv[1:]:
        if "," in extra:
            b = [float(x) for x in extra.split(",")]
            v = box(l, *b)
            print(f"  box {extra}: mean {v.mean():.1f} min {v.min():.0f} max {v.max():.0f} p95 {np.percentile(v,95):.0f}")
