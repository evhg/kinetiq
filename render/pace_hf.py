"""pace_hf.py: the Pace face's fine contrast at display width (owner note 7, 2026-11-02).

Run with the bpy venv (it reads the light-group index EXR through bpy):
  $PY pace_hf.py <png> <index.exr> --crop x0 x1 y0 y1 [--frame 2560 1440] [--widths 1170,1920] [--label L]

<png> is either the crop itself (a k01_lib --crop preview) or the whole frame (a final: the crop is cut out of it);
<index.exr> is the matching preview's object-index pass (face = pass index 1), so a final is measured inside the mask
of a preview rendered with the same camera and crop. For each display width W (the frame resized to W wide, LANCZOS):
  hf    the std, over the face, of luma minus its 4 px gaussian blur (normalised convolution inside the face mask, so
        hole lips and the face edge do not count); luma 0-255 (Rec.709 on the display-referred PNG)
  p50 / p95 / mean: the face's luma (the black must stay black: p50 should not climb)
"""
import sys

import numpy as np
from PIL import Image

a = sys.argv[1:]
png, exr = a[0], a[1]


def opt(name, default=None, n=1):
    if name in a:
        i = a.index(name)
        return a[i + 1] if n == 1 else a[i + 1:i + 1 + n]
    return default


x0, x1, y0, y1 = [float(v) for v in opt("--crop", None, 4)]
FW, FH = [int(v) for v in opt("--frame", ["2560", "1440"], 2)]
widths = [int(v) for v in opt("--widths", "1170,1920").split(",")]
label = opt("--label", png)
SIGMA = 4.0

px0, px1, py0, py1 = int(round(x0 * FW)), int(round(x1 * FW)), int(round(y0 * FH)), int(round(y1 * FH))
im = Image.open(png)
if im.size == (FW, FH):
    im = im.crop((px0, py0, px1, py1))
arr = np.asarray(im).astype(np.float64)
arr = arr / (65535.0 if arr.max() > 255 else 255.0)
if arr.ndim == 2:
    arr = np.stack([arr] * 3, -1)
lum = (arr[..., :3] @ np.array([0.2126, 0.7152, 0.0722])) * 255.0

import bpy  # noqa: E402

img = bpy.data.images.load(exr, check_existing=False)
w, h = img.size
px = np.empty(w * h * 4, np.float32)
img.pixels.foreach_get(px)
idx = px.reshape(h, w, 4)[::-1, :, 0]
assert (w, h) == (lum.shape[1], lum.shape[0]), ((w, h), lum.shape)
face = (np.abs(idx - 1) < 0.5).astype(np.float64)


def gauss(x, s):
    r = int(np.ceil(3 * s))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    k /= k.sum()
    p = np.pad(x, r, mode="edge")
    p = np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 1, p)
    return np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 0, p)


def erode(m, n):
    for _ in range(n):
        m = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    return m


out = [label]
for W in widths:
    s = W / FW
    sz = (max(1, int(round(lum.shape[1] * s))), max(1, int(round(lum.shape[0] * s))))
    L = np.asarray(Image.fromarray(lum.astype(np.float32), "F").resize(sz, Image.LANCZOS)).astype(np.float64)
    M = np.asarray(Image.fromarray(face.astype(np.float32), "F").resize(sz, Image.BOX)) > 0.99
    M = erode(M, 1)
    mb = gauss(M.astype(np.float64), SIGMA)
    lb = gauss(L * M, SIGMA) / np.maximum(mb, 1e-6)
    inner = erode(M, 2)
    hp = (L - lb)[inner]
    v = L[inner]
    out.append("W%d hf %.2f p50 %.1f p95 %.1f mean %.1f px %d" % (W, hp.std(), np.percentile(v, 50), np.percentile(v, 95),
                                                                   v.mean(), int(inner.sum())))
print(" | ".join(out), flush=True)
