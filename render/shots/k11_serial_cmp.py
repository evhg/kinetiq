"""Side-by-side of the K11 final's throat serials (3200 px, 100% and enlarged) against K10's final mark."""
import sys
import numpy as np
from PIL import Image, ImageDraw

k11 = Image.open(sys.argv[1]).convert("RGB")
k10 = Image.open(sys.argv[2]).convert("RGB")
out_path = sys.argv[3]


def bbox(im, box, thr):
    a = np.asarray(im.crop(box).convert("L")).astype(int)
    ys, xs = np.where(a > thr)
    return box[0] + xs.min(), box[1] + ys.min(), box[0] + xs.max(), box[1] + ys.max()


W, H = k11.size
b10 = bbox(k10, (1100, 980, 2100, 1110), 150)
# serial windows in the K11 frame (fractions of the 3200 x 1800 frame)
bf = bbox(k11, (int(W * 0.425), int(H * 0.56), int(W * 0.49), int(H * 0.595)), 45)
br = bbox(k11, (int(W * 0.54), int(H * 0.50), int(W * 0.60), int(H * 0.535)), 45)
print("K10 serial box", b10, "K11 front", bf, "K11 rear", br)
Hh = 150


def fit(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


rows = [("K10 final: 027/500 (scaled to the same height)", fit(k10.crop((b10[0] - 60, b10[1] - 25, b10[2] + 60, b10[3] + 25)), Hh)),
        ("K11 final, front throat (3200 px, enlarged)", fit(k11.crop((bf[0] - 10, bf[1] - 5, bf[2] + 10, bf[3] + 5)), Hh)),
        ("K11 final, rear throat (3200 px, enlarged)", fit(k11.crop((br[0] - 10, br[1] - 5, br[2] + 10, br[3] + 5)), Hh))]
t = k11.crop((int(W * 0.40), int(H * 0.44), int(W * 0.62), int(H * 0.64)))
Wd = max(max(r.width for _, r in rows), t.width) + 20
out = Image.new("RGB", (Wd, (Hh + 26) * 3 + t.height + 30), (40, 40, 40))
d = ImageDraw.Draw(out)
y = 0
for lab, r in rows:
    d.text((8, y + 4), lab, fill=(230, 230, 230))
    out.paste(r, (10, y + 20))
    y += Hh + 26
d.text((8, y + 4), "K11 final throats at 100% (3200 px)", fill=(230, 230, 230))
out.paste(t, (10, y + 20))
out.save(out_path)
print(out.size)
