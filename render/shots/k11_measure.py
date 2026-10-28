"""K11 look metrics: python k11_measure.py <view.png> <masks.json>
Per racket (front / rear-visible): stripe (mean of the brightest 10% of bare carbon), p95, shade (p30), mean RGB of the
stripe; grip and cap; background halo peak row and the top-edge luma. Luma = Rec.709 on display values (as fillcheck)."""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

im = Image.open(sys.argv[1]).convert("RGB")
W, H = im.size
a = np.asarray(im).astype(np.float32)
Y = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
M = json.load(open(sys.argv[2]))


def poly(pts, grow=0):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(x * W, y * H) for x, y in pts], fill=255)
    if grow > 0:
        m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    elif grow < 0:
        m = m.filter(ImageFilter.MinFilter(-grow * 2 + 1))
    return np.asarray(m) > 0


def polys(lst, grow=0):
    out = np.zeros((H, W), bool)
    for p in lst:
        out |= poly(p, grow)
    return out


g = max(1, W // 800)
front_head = poly(M["front_head"], g)
masks = {}
for nm in ("front", "rear"):
    face = poly(M[nm + "_face"], -3 * g)
    excl = polys(M[nm + "_holes"], g) | polys(M[nm + "_throat"], 2 * g) | poly(M[nm + "_serial"], 4 * g)
    m = face & ~excl
    if nm == "rear":
        m &= ~front_head
    masks[nm] = m

res = {}
for nm, m in masks.items():
    y = Y[m]
    c = a[m]
    thr = np.percentile(y, 90)
    top = y >= thr
    lit = y >= 40
    res[nm] = dict(litmean=float(y[lit].mean()) if lit.any() else 0.0, litfrac=float(lit.mean()), mean=float(y.mean()),
                   p80=float(np.percentile(y, 80)), stripe=float(y[top].mean()), p95=float(np.percentile(y, 95)), shade=float(np.percentile(y, 30)),
                   med=float(np.median(y)), rgb=tuple(round(float(v), 1) for v in c[top].mean(0)), n=int(m.sum()))
    print(f"{nm:5s} stripe {res[nm]['stripe']:6.1f}  p95 {res[nm]['p95']:6.1f}  shade(p30) {res[nm]['shade']:5.1f}  "
          f"median {res[nm]['med']:5.1f}  stripe RGB {res[nm]['rgb']}  px {res[nm]['n']}")
    print(f"      mean {res[nm]['mean']:5.1f}  p80 {res[nm]['p80']:5.1f}  lit(>=40) mean {res[nm]['litmean']:5.1f} "
          f"frac {res[nm]['litfrac']:.3f}")
f, r = res["front"], res["rear"]
print(f"rear/front: mean {r['mean'] / f['mean']:.2f}  p80 {r['p80'] / f['p80']:.2f}  litmean {r['litmean'] / max(1e-6, f['litmean']):.2f}  litfrac {r['litfrac'] / max(1e-6, f['litfrac']):.2f}  med {r['med'] / f['med']:.2f}")
print(f"rear/front: stripe {r['stripe'] / f['stripe']:.2f}  p95 {r['p95'] / f['p95']:.2f}  shade {r['shade'] / f['shade']:.2f}")
for nm in ("front", "rear"):
    for part in ("_grip", "_cap"):
        m = poly(M[nm + part], -g)
        if part == "_grip" and nm == "front":
            pass
        c = a[m]
        y = Y[m]
        print(f"{nm}{part}: median {np.median(y):5.1f}  p98 {np.percentile(y, 98):6.1f}  "
              f"mean RGB {tuple(round(float(v), 1) for v in c.mean(0))}")
# carbon face reference for the grip comparison
print(f"carbon median front {f['med']:.1f}")
# background
anyr = poly(M["front_head"], 4 * g) | poly(M["rear_head"], 4 * g)
for nm in ("front", "rear"):
    anyr |= poly(M[nm + "_grip"], 4 * g) | poly(M[nm + "_cap"], 4 * g)
bg = ~anyr
x0, x1 = int(W * 0.30), int(W * 0.70)
rows = []
for yy in range(0, H, max(1, H // 60)):
    band = slice(yy, min(H, yy + max(1, H // 60)))
    mm = bg[band, x0:x1]
    if mm.sum() > 20:
        rows.append((yy / H, float(Y[band, x0:x1][mm].mean())))
pk = max(rows, key=lambda t: t[1])
print(f"background: peak row {pk[0]:.3f} luma {pk[1]:.1f};  top edge (y<0.06, x .4-.6) "
      f"{Y[: int(H * 0.06), int(W * 0.4): int(W * 0.6)].mean():.1f};  max top-edge row "
      f"{Y[: int(H * 0.02), :].mean(1).max():.1f}")
print("rows:", " ".join(f"{v:.2f}:{l:.0f}" for v, l in rows[::3]))
lit_bg = ((Y >= 40) & bg).mean()
print(f"lit share: total {(Y >= 40).mean():.3f}  background {lit_bg:.3f}")
