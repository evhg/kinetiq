"""K04 v5 (AD stage 3a, 2026-10-22): the crisp gap line between visible floats of k04_tex2's 2/2 twill.

Why: at K04's macro scale a float is 60-100 px on screen; the baked albedo darkens a tow's edges over ~0.25 mm (the
lens profile), so the tile edges read soft (parquet / porcelain tiles), while K10's twill shows thin, crisp, darker gap
lines. This writes the distance from every texel to the nearest boundary of the float that lies on top, as a narrow
line mask (1 on the boundary, gaussian falloff), on exactly k04_tex2's grid (the geometry below is copied verbatim
from shots/k04_weave2.py: same seeds, warp, tow boundaries, undulation), so it registers with every k04_tex2 map and,
through warpx16/warpy16, with K04's warped face bake.

Boundaries: (a) the side edges of the top tow (adjacent parallel tows), distance min(f, 1 - f) * width;
            (b) the float ends, where the crossing tow comes up (H = V): first-order distance |H - V| / |grad(H - V)|.
Writes shots/k04_tex2/gap16.png (16-bit grey; 1 = on the gap line). Line half-width --w_mm (default 0.022 mm, so the
line is about 0.045 mm wide at half height: 4-5 px at K04's final scale).
Usage: ../bpyenv/bin/python shots/k04_gap.py [N] [--w_mm 0.022]
"""
import os
import sys

import numpy as np
from PIL import Image

args = [a for a in sys.argv[1:]]
W_MM = 0.022
if "--w_mm" in args:
    W_MM = float(args[args.index("--w_mm") + 1])
    del args[args.index("--w_mm"):args.index("--w_mm") + 2]
N = int(args[0]) if args else 4096
T = 16
TOW_MM = 2.6
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
OUT = kqpaths.asset("k04_tex2")

y0, x0 = (np.mgrid[0:N, 0:N].astype(np.float32) + 0.5) / N * T


def pwarp(seed, amp, terms=6):
    r = np.random.default_rng(seed)
    f = np.zeros_like(x0)
    fx = np.zeros_like(x0)
    fy = np.zeros_like(x0)
    for _ in range(terms):
        m, n = r.integers(-3, 4), r.integers(1, 5)
        if r.random() < 0.5:
            m, n = n, m
        a = amp * r.uniform(0.4, 1.0) / np.hypot(m, n)
        ph = r.uniform(0, 2 * np.pi)
        arg = 2 * np.pi * (m * x0 + n * y0) / T + ph
        f += a * np.sin(arg)
        fx += a * np.cos(arg) * 2 * np.pi * m / T
        fy += a * np.cos(arg) * 2 * np.pi * n / T
    return f, fx, fy


wx, _, _ = pwarp(1, 0.16)
wy, _, _ = pwarp(2, 0.16)
x = x0 + wx
y = y0 + wy
del wx, wy


def tows(c, seed):
    r = np.random.default_rng(seed)
    b = np.arange(T + 1, dtype=np.float64) + np.r_[r.uniform(-0.07, 0.07, T), 0.0]
    b[T] = T + b[0]
    cm = np.mod(c - b[0], T) + b[0]
    i = np.clip(np.searchsorted(b, cm, side="right") - 1, 0, T - 1)
    f = (cm - b[i]) / (b[i + 1] - b[i])
    return i, f.astype(np.float32), (b[i + 1] - b[i]).astype(np.float32)


i, fx, wi = tows(x, 5)
j, fy, wj = tows(y, 6)


def smooth_square(c, k=2.2):
    return 0.5 + 0.5 * np.tanh(k * c) / np.tanh(k)


def lens(f):
    return np.clip(1 - np.abs(2 * f - 1) ** 3.0, 0, 1) ** 0.45


u = np.mod(x - j, 4.0)
v = np.mod(y - i, 4.0)
und_h = smooth_square(np.cos(np.pi * (u - 1.0) / 2.0))
und_v = smooth_square(np.cos(np.pi * (v - 2.0) / 2.0))
A, B = 0.62, 0.38
H = A * und_h + B * lens(fy)
V = A * und_v + B * lens(fx)
top_h = H >= V
del u, v, und_h, und_v

# (a) side edges of the top tow, in tow units
side = np.where(top_h, np.minimum(fy, 1 - fy) * wj, np.minimum(fx, 1 - fx) * wi)
# (b) float ends: first-order distance to the H = V level set (texel units -> tow units)
d = (H - V).astype(np.float32)
del H, V
gy, gx = np.gradient(d)
gl = np.sqrt(gx * gx + gy * gy) * N / T + 1e-6
ends = np.abs(d) / gl
del gx, gy, gl, d
dist_mm = np.minimum(side, ends) * TOW_MM
gap = np.exp(-(dist_mm / W_MM) ** 2)
print("gap: px/mm", N / (T * TOW_MM), "line half-width px", W_MM * N / (T * TOW_MM), "coverage>0.5",
      float((gap > 0.5).mean()))
Image.fromarray((np.clip(gap, 0, 1) * 65535 + 0.5).astype(np.uint16)).save(os.path.join(OUT, "gap16.png"))
print("wrote", os.path.join(OUT, "gap16.png"))
