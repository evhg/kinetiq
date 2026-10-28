"""Bake K04's warped weave coordinates (v4, white Command): the texture-space position (mm) that k04_bake.py's
pin-displacement warp gives every face point, on exactly the same grid as shots/k04_bake/*.png (same bake.json).

Why: kq_canon.mat_white draws fibre-bundle streaks along each tow (1D noise in the weave coordinates, picked by the
tow's direction from k04_tex2/rot16). K04's weave is warped round every hole, so the shader needs the warped
coordinates to run those streaks along the bent tows (round each rim, over the meniscus and down the bore).
Adds two maps beside the existing bake (nothing else in k04_bake/ changes):
  warpx16.png, warpy16.png  (16-bit grey, row 0 = y0 at the bottom as Blender expects)  + warp.json (value ranges, mm)
warp() and holes() are copied verbatim from shots/k04_bake.py so the coordinates match the baked maps exactly.
Usage: ../bpyenv/bin/python shots/k04_bake_warp.py
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
OUT = kqpaths.asset("k04_bake")
args = json.load(open(os.path.join(OUT, "bake.json")))

U = 0.1
R = 6.2            # mm


def holes():
    """racket.holes() (shape units), replicated here so this runs without bpy (as k04_bake.py)."""
    centre = (0.0, 0.3)
    step = 0.27
    cands = []
    for row in range(-6, 7):
        y = centre[1] + row * step * 0.87
        off = 0 if row % 2 == 0 else step / 2
        for col in range(-6, 7):
            x = col * step + off
            inside = (x * x) / 1.0 + ((y - centre[1]) ** 2) / (1.08 * 1.08) < 1
            if inside and y > -0.62:
                cands.append((round(x, 3), round(y, 3)))
    cands.sort(key=lambda p: (p[0] * p[0] * 1.1 + (p[1] - centre[1]) ** 2, p[0]))
    return cands[:42]


HS = [(x * U * 1000, y * U * 1000) for (x, y) in holes()]
HS = [(hx, hy) for (hx, hy) in HS if args["x0"] - 25 < hx < args["x1"] + 25 and args["y0"] - 25 < hy < args["y1"] + 25]
assert [list(h) for h in HS] == [list(h) for h in args["holes"]], "hole list differs from the bake"
k, kw, kwl = args["k"], args["kw"], args["kwl"]


def warp(px, py):
    """Texture-space coordinates (mm) for physical points (mm). Additive per-hole displacement, as in the v3 shader."""
    wx, wy = px.copy(), py.copy()
    for (hx, hy) in HS:
        dx, dy = px - hx, py - hy
        r = np.sqrt(dx * dx + dy * dy)
        inside = r < R
        rr = np.maximum(r, R)                       # inside a hole: the rim value, extended radially
        sx = np.where(inside, dx * rr / np.maximum(r, 1e-6), dx)
        sy = np.where(inside, dy * rr / np.maximum(r, 1e-6), dy)
        rp = np.sqrt(np.maximum(rr * rr - k * R * R, 1e-10))
        t = np.minimum(-(rr - R) / (kwl * R), 0.0)
        rpp = np.maximum(rp - kw * R * np.exp(t), 0.2 * rp)
        s = rpp / rr - 1.0
        wx += sx * s + (sx - dx)
        wy += sy * s + (sy - dy)
    return wx, wy


t0 = time.time()
W = args["x1"] - args["x0"]
H = args["y1"] - args["y0"]
nx, ny = int(args["nx"]), int(args["ny"])
SS = 2  # as k04_bake.py: two sub-rows per pixel, averaged
xs = args["x0"] + (np.arange(nx, dtype=np.float64) + 0.5) / nx * W
ox = np.zeros((ny, nx), np.float64)
oy = np.zeros((ny, nx), np.float64)
chunk = 240
for j0 in range(0, ny, chunk):
    j1 = min(ny, j0 + chunk)
    ax = 0
    ay = 0
    for ss in range(SS):
        ys = args["y0"] + (np.arange(j0, j1, dtype=np.float64) + (ss + 0.5) / SS) / ny * H
        py, px = np.meshgrid(ys, xs, indexing="ij")
        wx, wy = warp(px, py)
        ax = ax + wx
        ay = ay + wy
    ox[j0:j1] = ax / SS
    oy[j0:j1] = ay / SS
    print(f"rows {j1}/{ny}  {time.time() - t0:.0f}s", flush=True)

meta = {}
for name, arr in (("x", ox), ("y", oy)):
    lo, hi = float(arr.min()), float(arr.max())
    q = ((arr[::-1] - lo) / (hi - lo) * 65535 + 0.5).astype(np.uint16)
    Image.fromarray(q).save(os.path.join(OUT, "warp%s16.png" % name))
    meta[name] = [lo, hi]
    print(name, "range mm", lo, hi, "step um", (hi - lo) / 65535 * 1000)
json.dump(meta, open(os.path.join(OUT, "warp.json"), "w"), indent=1)
print("baked warp", nx, "x", ny, f"{time.time() - t0:.0f}s")
