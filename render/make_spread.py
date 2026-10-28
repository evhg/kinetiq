# 12K spread-tow carbon: wide, flat tows (~8x wider than 3K) in a checker weave.
import sys
import numpy as np
from PIL import Image
N = 2048
TOWS = 4                      # 4 tows per tile -> flat, wide ribbons
out = sys.argv[1] if len(sys.argv) > 1 else "tex"
y, x = np.mgrid[0:N, 0:N].astype(np.float32) / N * TOWS
i = np.floor(x).astype(int); j = np.floor(y).astype(int)
fx = x - i; fy = y - j
horizontal = ((i + j) % 2) == 0           # plain checker, typical for spread tow
edge = lambda f: np.clip(1 - np.abs(2 * f - 1) ** 8, 0, 1) ** 0.35   # very flat top, crisp gap
h_h = edge(fy) * (0.92 + 0.08 * np.sin(np.pi * fx))
h_v = edge(fx) * (0.92 + 0.08 * np.sin(np.pi * fy))
height = np.where(horizontal, h_h, h_v)
rng = np.random.default_rng(3)
def stri(coord, seed):
    r = np.random.default_rng(seed); acc = np.zeros_like(coord)
    for k in range(10):
        acc += r.uniform(0.2, 1) * np.sin(coord * r.uniform(180, 520) + r.uniform(0, 6.28))
    return acc / 10
st = np.where(horizontal, stri(fy + j * 1.7, 5), stri(fx + i * 2.3, 6))
height = height + 0.02 * st
tone = np.where(horizontal, rng.uniform(0.9, 1.1, TOWS)[j % TOWS], rng.uniform(0.9, 1.1, TOWS)[i % TOWS])
alb = np.clip(0.016 + 0.034 * height * tone + 0.005 * st, 0, 1)
albedo = np.stack([alb * 0.98, alb, alb * 1.03], -1)
rough = np.clip(0.26 + 0.1 * (1 - height) + 0.03 * st, 0.05, 1)
def save(name, arr, mode="RGB"):
    a = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(a, mode).save(f"{out}/{name}.png")
save("spread_albedo", albedo ** (1 / 2.2))
save("spread_rough", rough, "L")
save("spread_height", height / height.max(), "L")
print("spread maps written")
