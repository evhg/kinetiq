# Tileable 2x2 twill carbon weave maps: albedo, roughness, normal, anisotropy rotation.
import sys
import numpy as np
from PIL import Image

N = 2048          # texture size
TOWS = 16         # tows per direction per tile
out = sys.argv[1] if len(sys.argv) > 1 else "tex"
rng = np.random.default_rng(7)

y, x = np.mgrid[0:N, 0:N].astype(np.float32) / N * TOWS  # in tow units
i = np.floor(x).astype(int)
j = np.floor(y).astype(int)
fx = x - i
fy = y - j

# 2x2 twill: which tow is on top in each cell
horizontal_on_top = ((i - j) % 4) < 2

def across(f):
    # rounded tow cross-section, flat-ish top, dips at the gap between tows
    t = np.clip(1 - np.abs(2 * f - 1) ** 2.2, 0, 1)
    return t ** 0.6

def along(f, phase):
    # a tow is on top for 2 cells then dives under for 2: smooth hump over the 2-cell span
    p = (f + phase) / 2.0
    return 0.75 + 0.25 * np.sin(np.pi * np.clip(p, 0, 1))

# phase within the 2-cell over-run
ph_h = (((i - j) % 4) % 2).astype(np.float32)          # 0 or 1 for horizontal runs
ph_v = (((j - i + 2) % 4) % 2).astype(np.float32)

h_h = across(fy) * along(fx, ph_h)
h_v = across(fx) * along(fy, ph_v)
height = np.where(horizontal_on_top, h_h, h_v)

# filament striations along each tow, plus per-tow tone variation
def striations(coord, seed):
    r = np.random.default_rng(seed)
    acc = np.zeros_like(coord)
    for k in range(6):
        freq = r.uniform(40, 140)
        acc += r.uniform(0.2, 1.0) * np.sin(coord * freq + r.uniform(0, 6.28))
    return acc / 6

stri = np.where(horizontal_on_top, striations(fy * 1.0 + j * 3.1, 1), striations(fx * 1.0 + i * 2.7, 2))
height = height + 0.035 * stri

tone_h = rng.uniform(0.85, 1.15, size=TOWS)
tone_v = rng.uniform(0.85, 1.15, size=TOWS)
tone = np.where(horizontal_on_top, tone_h[j % TOWS], tone_v[i % TOWS])

# albedo: deep charcoal; tops of tows slightly lighter (resin-poor), gaps darker (resin-rich)
base = 0.018 + 0.03 * height * tone + 0.006 * stri
alb = np.clip(base, 0, 1)
albedo = np.stack([alb * 0.98, alb, alb * 1.03], -1)

rough = np.clip(0.30 + 0.12 * (1 - height) + 0.04 * stri, 0.05, 1)

# normal from height (tileable gradient)
s = 2.2
dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * s * N / (TOWS * 64)
dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * s * N / (TOWS * 64)
nx, ny, nz = -dx, dy, np.ones_like(dx)
ln = np.sqrt(nx * nx + ny * ny + nz * nz)
normal = np.stack([nx / ln, ny / ln, nz / ln], -1) * 0.5 + 0.5

# anisotropy rotation: 0 for horizontal tows, 0.25 (a quarter turn) for vertical
aniso = np.where(horizontal_on_top, 0.0, 0.25).astype(np.float32)

def save(name, arr, mode="RGB"):
    a = np.clip(arr, 0, 1)
    if mode == "L":
        img = Image.fromarray((a * 255 + 0.5).astype(np.uint8), "L")
    else:
        img = Image.fromarray((a * 255 + 0.5).astype(np.uint8), "RGB")
    img.save(f"{out}/{name}.png")

# albedo stored in sRGB
save("weave_albedo", albedo ** (1 / 2.2))
save("weave_rough", rough, "L")
save("weave_normal", normal)
save("weave_aniso", aniso, "L")
save("weave_height", height / height.max(), "L")
print("weave maps written", out)
