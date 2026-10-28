"""Bake K04's procedural carbon (v3) into world-space maps over the visible part of the face.

The v3 shader displaced the weave coordinates around every hole with a node chain that Cycles evaluated ~7x per hit
(two bumps), which made a 3200 px final impractical on the shared machine. This bakes exactly the same maths in numpy:
- pin-displacement warp per hole (area-preserving r' = sqrt(r^2 - k R^2), plus a wider bend kw R exp(-(r - R)/(kw_l R))),
  so 3-4 tows arc visibly round each rim, compress against it and run down the bore (inside a hole the value at the rim
  is extended radially, so the bore wall shows the tows as vertical streaks),
- mat_carbon's flow rings: faint concentric filaments on the meniscus, riding on the weave (not replacing it),
- the anisotropic tangent ACROSS the physical fibre direction: texture-space tangent from k04_tex2/rot16 pushed through the
  inverse Jacobian of the warp (so near a rim it turns with the bent tows), stored as a double angle (cos 2t, sin 2t).
Maps (PNG, row 0 = y0 at the bottom as Blender expects): albedo.png, rough.png, height16.png, tan.png + bake.json.
Usage: ../bpyenv/bin/python shots/k04_bake.py [--k 0.95 --kw 0.42 --kwl 1.3 --pxx 90 --pxy 54]"""
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
SRC = kqpaths.asset("k04_tex2")
OUT = kqpaths.asset("k04_bake")
os.makedirs(OUT, exist_ok=True)

args = dict(k=0.95, kw=0.42, kwl=1.3, pxx=90.0, pxy=54.0, x0=-31.0, x1=20.0, y0=2.0, y1=64.0, ring_r=1.3, ring_amp=0.08)
a = sys.argv[1:]
for i in range(0, len(a) - 1, 2):
    args[a[i].lstrip("-")] = float(a[i + 1])

U = 0.1
R = 6.2            # mm
TILE = 2.6 * 16    # mm per weave tile (mat_carbon: 16 tows of 2.6 mm)


def holes():
    """racket.holes() (shape units), replicated here so this runs without bpy."""
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


def load(fn, mode):
    im = Image.open(os.path.join(SRC, fn))
    arr = np.asarray(im).astype(np.float32)
    if arr.dtype != np.float32:
        arr = arr.astype(np.float32)
    return arr


alb = load("albedo.png", "RGB") / 255.0
rgh = load("rough.png", "L") / 255.0
hgt = load("height16.png", "I") / 65535.0
rot = load("rot16.png", "I") / 65535.0
th = (rot * 0.5 - 0.125) * 2 * math.pi            # texture-space tangent angle (across the fibres)
c2t, s2t = np.cos(2 * th).astype(np.float32), np.sin(2 * th).astype(np.float32)
NT = hgt.shape[0]


def bilinear(img, u, v):
    """u, v in texels (float), wrapping."""
    u0 = np.floor(u).astype(np.int64)
    v0 = np.floor(v).astype(np.int64)
    fu = (u - u0).astype(np.float32)
    fv = (v - v0).astype(np.float32)
    u0 %= NT
    v0 %= NT
    u1 = (u0 + 1) % NT
    v1 = (v0 + 1) % NT
    if img.ndim == 3:
        fu = fu[..., None]
        fv = fv[..., None]
    return ((img[v0, u0] * (1 - fu) + img[v0, u1] * fu) * (1 - fv) + (img[v1, u0] * (1 - fu) + img[v1, u1] * fu) * fv)


def tex_uv(wx, wy):
    # Blender FLAT projection: u = x / tile, v = y / tile with image row 0 at the BOTTOM; numpy row 0 is the top
    u = wx / TILE * NT - 0.5
    v = (1.0 - np.mod(wy / TILE, 1.0)) * NT - 0.5
    return u, v


t0 = time.time()
W = args["x1"] - args["x0"]
H = args["y1"] - args["y0"]
nx = int(round(W * args["pxx"]))
ny = int(round(H * args["pxy"]))
SS = 2  # supersample in y (the face is foreshortened there; streaks across y must not alias)
out_alb = np.zeros((ny, nx, 3), np.float32)
out_rgh = np.zeros((ny, nx), np.float32)
out_hgt = np.zeros((ny, nx), np.float32)
out_c = np.zeros((ny, nx), np.float32)
out_s = np.zeros((ny, nx), np.float32)
out_b = np.zeros((ny, nx), np.float32)
xs = args["x0"] + (np.arange(nx, dtype=np.float32) + 0.5) / nx * W
chunk = 160
eps = 0.004  # mm, for the Jacobian
for j0 in range(0, ny, chunk):
    j1 = min(ny, j0 + chunk)
    acc = {key: 0 for key in ("a", "r", "h", "c", "s", "b")}
    for ss in range(SS):
        ys = args["y0"] + (np.arange(j0, j1, dtype=np.float32) + (ss + 0.5) / SS) / ny * H
        py, px = np.meshgrid(ys, xs, indexing="ij")
        wx, wy = warp(px, py)
        u, v = tex_uv(wx, wy)
        A = bilinear(alb, u, v)
        Rg = bilinear(rgh, u, v)
        Hh = bilinear(hgt, u, v)
        C2 = bilinear(c2t, u, v)
        S2 = bilinear(s2t, u, v)
        # flow rings on the meniscus: per hole masked filaments riding on the weave
        num = np.zeros_like(px)
        den = np.zeros_like(px)
        streak = np.zeros_like(px)
        dmin = np.full_like(px, 1e9)
        for hi, (hx, hy) in enumerate(HS):
            r = np.maximum(np.hypot(px - hx, py - hy), R)
            # tows running down the bore wall: brightness streaks along the rim circumference (nearest hole wins)
            arc = np.arctan2(py - hy, px - hx) * R
            rs_ = np.random.default_rng(100 + hi)
            st = np.zeros_like(px)
            for _ in range(11):
                pitch = rs_.uniform(0.04, 0.6)
                pitch = (2 * np.pi * R) / max(1, round(2 * np.pi * R / pitch))  # whole number round the rim: seamless
                st += rs_.uniform(0.3, 1.0) * np.sin(2 * np.pi * arc / pitch + rs_.uniform(0, 6.28))
            # irregular: a slow random envelope round the rim, so the streaks never read as a grille
            env = 0.6 + 0.4 * np.sin(arc / R * 3 + hi) * np.sin(arc / R * 5 + 2 * hi + 1)
            near_ = r - R < dmin
            streak = np.where(near_, st / 5.0 * env, streak)
            dmin = np.minimum(dmin, r - R)
            m = np.clip((r - R * 1.02) / (R * args["ring_r"] - R * 1.02), 0, 1)
            m = 1 - m * m * (3 - 2 * m)
            fib = (0.5 * np.sin(2 * np.pi * r / 0.061 + 0.3 + hi) + 0.3 * np.sin(2 * np.pi * r / 0.097 + 1.9 + hi)
                   + 0.2 * np.sin(2 * np.pi * r / 0.149 + 4.1 + hi))
            num += m * fib
            den += m
        mmax = np.clip(den, 0, 1)
        Hh = Hh + args["ring_amp"] * mmax * num / np.maximum(den, 1e-4)
        # tangent: texture-space angle -> physical via the inverse Jacobian of the warp
        wxa, wya = warp(px + eps, py)
        wxb, wyb = warp(px, py + eps)
        j11, j21 = (wxa - wx) / eps, (wya - wy) / eps
        j12, j22 = (wxb - wx) / eps, (wyb - wy) / eps
        tt = 0.5 * np.arctan2(S2, C2)                   # texture tangent angle (mod pi)
        fx_, fy_ = -np.sin(tt), np.cos(tt)              # texture fibre direction (perpendicular to the tangent)
        det = j11 * j22 - j12 * j21
        det = np.where(np.abs(det) < 1e-8, 1e-8, det)
        gx = (j22 * fx_ - j12 * fy_) / det              # physical fibre direction J^-1 f
        gy = (-j21 * fx_ + j11 * fy_) / det
        tp = np.arctan2(gy, gx) + np.pi / 2              # physical tangent across the fibres
        strength = np.clip(np.hypot(C2, S2), 0, 1)       # tow boundaries average to no preferred direction
        acc["a"] = acc["a"] + A
        acc["r"] = acc["r"] + Rg
        acc["h"] = acc["h"] + Hh
        acc["c"] = acc["c"] + np.cos(2 * tp) * strength
        acc["s"] = acc["s"] + np.sin(2 * tp) * strength
        acc["b"] = acc.get("b", 0) + np.clip(0.5 + 0.5 * streak, 0, 1)
    out_alb[j0:j1] = acc["a"] / SS
    out_rgh[j0:j1] = acc["r"] / SS
    out_hgt[j0:j1] = acc["h"] / SS
    out_c[j0:j1] = acc["c"] / SS
    out_s[j0:j1] = acc["s"] / SS
    out_b[j0:j1] = acc["b"] / SS
    print(f"rows {j1}/{ny}  {time.time() - t0:.0f}s", flush=True)

flip = lambda z: z[::-1]  # noqa: E731  (row 0 = y0 at the bottom)
Image.fromarray((np.clip(flip(out_alb), 0, 1) * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(OUT, "albedo.png"))
Image.fromarray((np.clip(flip(out_rgh), 0, 1) * 255 + 0.5).astype(np.uint8), "L").save(os.path.join(OUT, "rough.png"))
h = out_hgt
lo, hi = float(h.min()), float(h.max())
Image.fromarray(((flip(h) - lo) / (hi - lo) * 65535 + 0.5).astype(np.uint16)).save(os.path.join(OUT, "height16.png"))
tan = np.stack([flip(out_c) * 0.5 + 0.5, flip(out_s) * 0.5 + 0.5, flip(out_b)], -1)  # B: bore-wall streaks
Image.fromarray((np.clip(tan, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(OUT, "tan.png"))
meta = dict(args, nx=nx, ny=ny, holes=HS, height_range=[lo, hi])
json.dump(meta, open(os.path.join(OUT, "bake.json"), "w"), indent=1)
print("baked", OUT, nx, "x", ny, "holes", len(HS), f"{time.time() - t0:.0f}s")
