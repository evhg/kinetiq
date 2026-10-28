"""K04 v3 weave maps: 2/2 twill, 16 tows per tile (drops into mat_carbon's mapping unchanged), built for a
graphite-metal anisotropic base under a clearcoat:
- every tow has its own width and a slow periodic meander (seamless domain warp), so no two cells match,
- filament streaks along each tow at 0.04-0.12 mm pitch (height, albedo and roughness),
- resin-rich gaps between tows read darker and rougher,
- rot16.png: anisotropic tangent rotation (fraction of a turn) ACROSS the local fibre direction, including the meander,
- coat16.png: low-pass tow relief for a faint print-through in the clearcoat normal.
Writes shots/k04_tex2/{albedo.png, rough.png, height16.png, rot16.png, coat16.png}.
Usage: python k04_weave2.py [N]   (numpy + PIL)"""
import os
import sys

import numpy as np
from PIL import Image

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
T = 16
TOW_MM = 2.6
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
OUT = kqpaths.asset("k04_tex2")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(23)

y0, x0 = (np.mgrid[0:N, 0:N].astype(np.float32) + 0.5) / N * T


def pwarp(seed, amp, terms=6):
    """Seamless (period T) smooth warp field and its x/y derivatives."""
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


wx, wxx, wxy = pwarp(1, 0.16)
wy, wyx, wyy = pwarp(2, 0.16)
x = x0 + wx
y = y0 + wy


def tows(c, seed):
    """Irregular tow boundaries (period T): index and fraction across the tow."""
    r = np.random.default_rng(seed)
    b = np.arange(T + 1, dtype=np.float64) + np.r_[r.uniform(-0.07, 0.07, T), 0.0]
    b[T] = T + b[0]
    cm = np.mod(c - b[0], T) + b[0]
    i = np.clip(np.searchsorted(b, cm, side="right") - 1, 0, T - 1)
    f = (cm - b[i]) / (b[i + 1] - b[i])
    return i, f.astype(np.float32), (b[i + 1] - b[i]).astype(np.float32)


i, fx, wi = tows(x, 5)   # vertical tows (fibres along Y), indexed along x
j, fy, wj = tows(y, 6)   # horizontal tows (fibres along X), indexed along y


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
relief = np.maximum(H, V)


def filaments(across, along, idx, width, seed):
    """Fine streaks along a tow: pitches 0.04-0.12 mm, phase wandering slowly along the tow."""
    r = np.random.default_rng(seed)
    acc = np.zeros_like(across)
    wsum = 0.0
    for _ in range(9):
        pitch_mm = r.uniform(0.04, 0.12)
        k = 2 * np.pi * TOW_MM / pitch_mm  # rad per tow width
        ph = r.uniform(0, 2 * np.pi, size=T)[idx]
        wob = r.uniform(0.3, 1.2)
        w = r.uniform(0.4, 1.0)
        acc += w * np.sin(across * width * k + ph + wob * np.sin(along * r.uniform(0.5, 1.7) + ph))
        wsum += w
    return acc / wsum


s_h = filaments(fy, x, j, wj, 11)
s_v = filaments(fx, y, i, wi, 12)
s = np.where(top_h, s_h, s_v)

# fine height: tow relief + filament streaks
height = relief + 0.022 * s
height = (height - height.min()) / (height.max() - height.min())

# per-tow tone, slow along-tow drift, darker resin gaps, filament tone
tone = np.where(top_h, rng.uniform(0.82, 1.18, size=T)[j % T], rng.uniform(0.82, 1.18, size=T)[i % T])
drift = 1 + 0.07 * np.sin(np.where(top_h, x, y) * 0.9 + np.where(top_h, j, i) * 1.7)
edge = np.where(top_h, lens(fy), lens(fx))
lin = (0.30 + 0.70 * edge) * tone * drift * (1 + 0.16 * s)
lin = np.clip(lin / lin.max(), 0, 1) * 0.92
srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
alb = np.stack([srgb * 0.985, srgb, srgb * 1.015], -1)
Image.fromarray((np.clip(alb, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(OUT, "albedo.png"))

# roughness (used as the base roughness before the shader's scale): smoother tow crowns, rougher gaps
rough = np.clip(0.30 + 0.22 * (1 - edge) + 0.05 * s, 0.05, 1)
Image.fromarray((rough * 255 + 0.5).astype(np.uint8), "L").save(os.path.join(OUT, "rough.png"))

Image.fromarray((height * 65535 + 0.5).astype(np.uint16)).save(os.path.join(OUT, "height16.png"))

# tangent rotation across the local fibre direction (fraction of a turn, relative to +X)
# horizontal tows: fibres follow iso-lines of y = y0 + wy -> direction (1 + wyy, -wyx) / ...
ang_h = np.arctan2(-wyx, 1 + wyy)
# vertical tows: fibres follow iso-lines of x = x0 + wx -> direction (-wxy, 1 + wxx)
ang_v = np.arctan2(1 + wxx, -wxy)
fib = np.where(top_h, ang_h, ang_v)
# anisotropy is symmetric under a half turn; offset by 1/8 turn so neither tow family sits at the wrap
# (horizontal tows store 0.75, vertical 0.25). Shader: rotation = value * 0.5 - 0.125
rot = np.mod((fib + np.pi / 2) / (2 * np.pi) + 0.125, 0.5) * 2
Image.fromarray((rot * 65535 + 0.5).clip(0, 65535).astype(np.uint16)).save(os.path.join(OUT, "rot16.png"))

# coat print-through: periodic gaussian low-pass of the tow relief (sigma 0.12 tow)
F = np.fft.rfft2(relief.astype(np.float64))
ky = np.fft.fftfreq(N)[:, None]
kx = np.fft.rfftfreq(N)[None, :]
sig = 0.12 * N / T
F *= np.exp(-2 * (np.pi * sig) ** 2 * (kx ** 2 + ky ** 2))
coat = np.fft.irfft2(F, s=(N, N))
coat = (coat - coat.min()) / (coat.max() - coat.min())
Image.fromarray((coat * 65535 + 0.5).astype(np.uint16)).save(os.path.join(OUT, "coat16.png"))
print("wrote", OUT, N, "rot range", float(rot.min()), float(rot.max()))
