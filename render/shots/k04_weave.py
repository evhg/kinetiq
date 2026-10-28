"""Macro-grade 2/2 twill maps for K04 (and K05 if wanted): 16 tows per tile like racket's weave maps,
so they drop into mat_carbon's mapping unchanged. Smooth undulating tows (no hard steps at the crossovers),
lenticular cross-sections, filament striations along each tow, per-tow tone.
Writes shots/k04_tex/{albedo.png (sRGB), rough.png, height16.png (16-bit), dir.png (0 = tow along X, 255 = along Y)}.
Usage: python k04_weave.py [N]   (plain python with numpy + PIL)"""
import os
import sys

import numpy as np
from PIL import Image

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
T = 16
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # render/ root (kqpaths)
import kqpaths  # noqa: E402
OUT = kqpaths.asset("k04_tex")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

y, x = (np.mgrid[0:N, 0:N].astype(np.float32) + 0.5) / N * T
i = np.floor(x).astype(np.int32)
j = np.floor(y).astype(np.int32)
fx = x - i
fy = y - j


def smooth_square(c, k=2.2):
    return 0.5 + 0.5 * np.tanh(k * c) / np.tanh(k)


def lens(f):
    # flat-topped lenticular tow cross-section, 0 at the tow edges
    return np.clip(1 - np.abs(2 * f - 1) ** 3.0, 0, 1) ** 0.45


# undulation: horizontal tow j is on top for u = (x - j) mod 4 in [0, 2); vertical tow i for v = (y - i) mod 4 in [1, 3)
u = np.mod(x - j, 4.0)
v = np.mod(y - i, 4.0)
und_h = smooth_square(np.cos(np.pi * (u - 1.0) / 2.0))
und_v = smooth_square(np.cos(np.pi * (v - 2.0) / 2.0))
A, B = 0.62, 0.38
H = A * und_h + B * lens(fy)
V = A * und_v + B * lens(fx)
top_h = H >= V
height = np.maximum(H, V)


# filament striations: fine lines along each tow (function of the across-tow coordinate), slightly wavy
def stria(across, along, seed, tows):
    r = np.random.default_rng(seed)
    acc = np.zeros_like(across)
    for _ in range(7):
        f = r.uniform(30, 90)
        ph = r.uniform(0, 6.28, size=T)[tows % T]
        acc += r.uniform(0.3, 1.0) * np.sin(across * f + ph + 0.35 * np.sin(along * r.uniform(0.6, 1.6) + ph))
    return acc / 7.0


s_h = stria(fy, x, 1, j)
s_v = stria(fx, y, 2, i)
s = np.where(top_h, s_h, s_v)
height = height + 0.018 * s
height = (height - height.min()) / (height.max() - height.min())

tone_h = rng.uniform(0.86, 1.14, size=T)[j % T]
tone_v = rng.uniform(0.86, 1.14, size=T)[i % T]
tone = np.where(top_h, tone_h, tone_v)
# along-tow slow tone drift (resin film thickness)
drift = 1 + 0.06 * np.sin(np.where(top_h, x, y) * 0.9 + np.where(top_h, j, i) * 1.7)
edge = np.where(top_h, lens(fy), lens(fx))  # resin-rich gaps between tows read darker
lin = (0.020 + 0.022 * edge) * tone * drift * (1 + 0.10 * s)
lin = np.clip(lin, 0, 1)
srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
alb = np.stack([srgb * 0.985, srgb, srgb * 1.02], -1)
Image.fromarray((np.clip(alb, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(OUT, "albedo.png"))

rough = np.clip(0.26 + 0.10 * (1 - edge) + 0.035 * s, 0.05, 1)
Image.fromarray((rough * 255 + 0.5).astype(np.uint8), "L").save(os.path.join(OUT, "rough.png"))

h16 = (height * 65535 + 0.5).astype(np.uint16)
Image.fromarray(h16).save(os.path.join(OUT, "height16.png"))

d = np.where(top_h, 0, 255).astype(np.uint8)
Image.fromarray(d, "L").save(os.path.join(OUT, "dir.png"))
print("wrote", OUT, N)
