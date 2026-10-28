"""pace_metrics.py: numbers for the Pace 12K face and rim (site review rounds 1 and 3, 2026-10-23).

python pace_metrics.py <render.png> <masks.json> --racket right|front[,rear] --crop x0 x1 [--probe probe.png] [--label L]

On the page crop (x0..x1 of the frame width, full height; K08 right 0.575 0.975, K11 card 0.275 0.725):
- phone / desktop: the crop resized to 420 / 600 px wide (LANCZOS, as the site shows it). Inside each face (hull polygon
  eroded 3 px, holes at 1.25 r dilated 2 px left out): luma p50, the high-pass std (luma minus a 2.5 px gaussian,
  normalised inside the mask) and, with --probe, the tile step: in 24 px windows, |mean luma of hz=1 tapes - mean luma
  of hz=0 tapes| (pure-tape pixels only), averaged over the windows (luma 0-255).
- rim (master resolution): a band from 3 px inside each face hull to 26 px outside it (px at a 2560-wide frame, scaled),
  lit pixels (luma > 25): p99 and max |R-G|, and the count of saturated-red pixels (R > 120, R-G > 70, R-B > 80) in the
  band and in the whole crop.
- with --probe (pace_probe.py, same size as the render): per-tape albedo (decoded linear base albedo; mean of the
  hz=1 and hz=0 tapes, their difference in %, and the spread of single tapes), coat weight per direction.
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

args = sys.argv[1:]
png, mpath = args[0], args[1]


def opt(name, default=None, n=1):
    if name in args:
        i = args.index(name)
        return args[i + 1] if n == 1 else args[i + 1:i + 1 + n]
    return default


rackets = opt("--racket", "right").split(",")
cx0, cx1 = [float(v) for v in opt("--crop", ["0", "1"], 2)]
probe = opt("--probe")
label = opt("--label", png)

im = Image.open(png).convert("RGB")
W, H = im.size
M = json.load(open(mpath))


def poly_mask(polys, w, h, ox=0.0, sx=1.0):
    mk = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mk)
    for p in polys:
        d.polygon([((x - ox) * sx * w, y * h) for (x, y) in p], fill=255)
    return mk


def face_masks(w, h, ox, sx, erode_px, hole_px):
    face = Image.new("L", (w, h), 0)
    holes = Image.new("L", (w, h), 0)
    for r in rackets:
        f = M[r + "_face"]
        polys = f if (f and isinstance(f[0][0], list)) else [f]
        face = Image.fromarray(np.maximum(np.asarray(face), np.asarray(poly_mask(polys, w, h, ox, sx))))
        holes = Image.fromarray(np.maximum(np.asarray(holes), np.asarray(poly_mask(M[r + "_holes"], w, h, ox, sx))))
    if erode_px:
        face = face.filter(ImageFilter.MinFilter(2 * erode_px + 1))
    if hole_px:
        holes = holes.filter(ImageFilter.MaxFilter(2 * hole_px + 1))
    return (np.asarray(face) > 127) & ~(np.asarray(holes) > 127)


def luma(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def gblur(a, s):
    """Separable gaussian (sigma s px, zero outside the image)."""
    r = int(np.ceil(3 * s))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    k /= k.sum()
    a = a.astype(np.float64)
    a = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 1, a)
    return np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 0, a)


def srgb_to_lin(v):
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


crop = im.crop((round(W * cx0), 0, round(W * cx1), H))
pr = None
if probe:
    pim = Image.open(probe)
    pa = np.asarray(pim).astype(np.float64)
    pa = pa[..., :3] / (65535.0 if pa.max() > 255 else 255.0)
    pa = srgb_to_lin(pa)
    pr = pa
print("== %s" % label)
for tw in (420, 600):
    th = round(tw * crop.size[1] / crop.size[0])
    c = np.asarray(crop.resize((tw, th), Image.LANCZOS)).astype(np.float32)
    Y = luma(c)
    m = face_masks(tw, th, cx0, 1.0 / (cx1 - cx0), 3, 2)
    mf = m.astype(np.float32)
    lo = gblur(Y * mf, 2.5) / np.maximum(gblur(mf, 2.5), 1e-3)
    hp = (Y - lo)[m]
    # texture only: leave out where the smooth light itself changes fast (the band's edge and hot line)
    gy, gx = np.gradient(gblur(Y * mf, 4.0) / np.maximum(gblur(mf, 4.0), 1e-3))
    flat = m & (np.hypot(gx, gy) < 2.0)
    line = "  %d px: face luma p50 %.1f p90 %.1f  >40 %.0f%%  high-pass std %.2f (texture-only %.2f, %.0f%% of face)" % (
        tw, np.median(Y[m]), np.percentile(Y[m], 90), 100 * (Y[m] > 40).mean(), hp.std(), (Y - lo)[flat].std(),
        100 * flat.sum() / m.sum())
    if pr is not None:
        hz = pr[..., 1]
        hzc = Image.fromarray(hz.astype(np.float32), mode="F").crop((round(W * cx0), 0, round(W * cx1), H))
        hzr = np.asarray(hzc.resize((tw, th), Image.BILINEAR))
        on, off = m & (hzr > 0.9), m & (hzr < 0.1)
        steps, wts = [], []
        for y0 in range(0, th, 24):
            for x0 in range(0, tw, 24):
                a_, b_ = on[y0:y0 + 24, x0:x0 + 24], off[y0:y0 + 24, x0:x0 + 24]
                if a_.sum() >= 12 and b_.sum() >= 12:
                    sub = Y[y0:y0 + 24, x0:x0 + 24]
                    steps.append(abs(sub[a_].mean() - sub[b_].mean()))
                    wts.append(min(a_.sum(), b_.sum()))
        steps, wts = np.array(steps), np.array(wts)
        line += "  tile step mean %.2f p90 %.2f (%d windows)" % ((steps * wts).sum() / wts.sum(), np.percentile(steps, 90),
                                                                len(steps))
    print(line)

# rim at master resolution
s = W / 2560.0
fm = face_masks(W, H, 0.0, 1.0, 0, 0)
fimg = Image.fromarray((fm * 255).astype(np.uint8))
outer = np.asarray(fimg.filter(ImageFilter.MaxFilter(2 * round(26 * s) + 1))) > 127
inner = np.asarray(fimg.filter(ImageFilter.MinFilter(2 * round(3 * s) + 1))) > 127
band = outer & ~inner
band[:, :round(W * cx0)] = False
band[:, round(W * cx1):] = False
a = np.asarray(im).astype(np.int32)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
Yf = luma(a.astype(np.float32))
lit = band & (Yf > 25)
rg = np.abs(R - G)[lit]
red = (R > 120) & (R - G > 70) & (R - B > 80)
cropmask = np.zeros_like(band)
cropmask[:, round(W * cx0):round(W * cx1)] = True
print("  rim band (master %dx%d): lit px %d  |R-G| p50 %.1f p99 %.1f max %d   saturated red: band %d, crop %d"
      % (W, H, lit.sum(), np.median(rg) if rg.size else 0, np.percentile(rg, 99) if rg.size else 0,
         rg.max() if rg.size else 0, (red & band).sum(), (red & cropmask).sum()))
if lit.sum():
    top = np.argsort(Yf[lit])[-200:]
    print("  rim brightest 200 px: luma p50 %.0f max %.0f  mean R G B %.0f %.0f %.0f" % (
        np.median(Yf[lit][top]), Yf[lit].max(), R[lit][top].mean(), G[lit][top].mean(), B[lit][top].mean()))

if pr is not None:
    alb = pr[..., 0] / 10.0
    hz = pr[..., 1]
    cw = pr[..., 2]
    fm2 = face_masks(W, H, 0.0, 1.0, round(4 * s), round(3 * s))
    fm2[:, :round(W * cx0)] = False
    fm2[:, round(W * cx1):] = False
    on, off = fm2 & (hz > 0.99), fm2 & (hz < 0.01)
    a1, a0 = alb[on].mean(), alb[off].mean()
    # single tapes: per 8 mm tile the albedo is the tape tone x streaks; spread of tile means via a coarse grid
    print("  albedo (linear): hz=1 tapes %.5f  hz=0 tapes %.5f  difference %.2f%%  pixel spread p5-p95 %.5f-%.5f (+-%.1f%%)"
          % (a1, a0, 100 * abs(a1 - a0) / ((a1 + a0) / 2), np.percentile(alb[fm2], 5), np.percentile(alb[fm2], 95),
             100 * (np.percentile(alb[fm2], 95) - np.percentile(alb[fm2], 5)) / 2 / alb[fm2].mean()))
    # adjacent tapes: albedo step across every tape boundary (horizontal neighbours with different hz)
    hzb = hz > 0.5
    nb = fm2[:, 4:] & fm2[:, :-4] & (hzb[:, 4:] != hzb[:, :-4])
    d = np.abs(alb[:, 4:] - alb[:, :-4])[nb] / alb[fm2].mean()
    print("  adjacent-tape albedo step: mean %.2f%% p95 %.2f%%   coat weight hz=1 %.3f hz=0 %.3f"
          % (100 * d.mean(), 100 * np.percentile(d, 95), cw[on].mean(), cw[off].mean()))
