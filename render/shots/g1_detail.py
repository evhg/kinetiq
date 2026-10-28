"""g1_detail: the weave's detail-preserving grade for the hero group (K01, K02), applied in the comp.

Why: AgX Punchy's shoulder compresses the white face's lit third (display luma 220-232) to about 30 luma per e-fold of
scene light, so the twill's real tone and sheen variation (a few % linear) shows as a high-pass std of only 2.5-3 luma
there, whatever the material does (critic G1 sweep: dir_tone, aniso, spec, bump and a stronger fibre sheen all left
the lit third at 2.5-3.4). A base/detail split restores what the global curve flattens: the base (a normalised
gaussian of display luma inside the carbon mask, sigma about one tow) keeps the tone curve's look; the detail (luma
minus base) is scaled by a gain that rises with the base luma (where the curve is flattest). Only carbon pixels
(index pass) are touched; the mask is eroded by a pixel so hole rims and silhouettes get no halo.

    import g1_detail as GD
    GD.apply(raw_png, idx (H x W, top row first), sigma_px, parts=(1, 3, 4, 5), g_lo=1.0, g_hi=2.6, b0=0.62, b1=0.86)
"""
import numpy as np
import bpy
import k12_lib as K


def _conv(a, k):
    a = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, a)
    return np.apply_along_axis(lambda c: np.convolve(c, k, mode="same"), 0, a)


def _gauss(a, s):
    r = max(1, int(3 * s + 1))
    x = np.arange(-r, r + 1)
    k = np.exp(-x * x / (2 * s * s))
    return _conv(a, k / k.sum())


def _box(a, n):
    n = int(n) | 1
    return _conv(a, np.ones(n) / n)


def _smooth(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def apply(png, idx, sigma_px, parts=(1, 3, 4, 5), g_lo=1.0, g_hi=2.6, b0=0.62, b1=0.86, erode=1):
    """Rewrite the display-referred 16-bit PNG `png` in place. idx: object-index image, top row first, same size."""
    img = bpy.data.images.load(png)
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    a = a.reshape(h, w, 4)[::-1]  # top row first
    disp = K._oetf(a[..., :3]).astype(np.float64)
    if idx.shape != (h, w):
        print("g1_detail: index pass size %s != image %s, skipped" % (idx.shape, (h, w)), flush=True)
        return
    m = np.zeros((h, w), bool)
    for p in parts:
        m |= np.abs(idx - p) < 0.5
    if erode:
        m = _box(m.astype(np.float64), 2 * erode + 1) > 0.999
    wgt = m.astype(np.float64)
    Y = disp @ np.array([0.2126, 0.7152, 0.0722])
    s = max(0.6, float(sigma_px))
    base = _gauss(Y * wgt, s) / np.maximum(_gauss(wgt, s), 1e-6)
    det = (Y - base) * wgt
    gain = g_lo + (g_hi - g_lo) * _smooth(base, b0, b1)
    soft = _gauss(wgt, 0.7) * wgt          # feather the mask edge
    Y2 = np.clip(Y + (gain - 1.0) * det * soft, 0.0, 1.0)
    k_ = np.where(Y > 1e-4, Y2 / np.maximum(Y, 1e-4), 1.0)
    disp = np.clip(disp * k_[..., None], 0.0, 1.0)
    a = a[::-1].copy()
    a[..., :3] = K._eotf(disp[::-1].astype(np.float32))
    a[..., 3] = 1.0
    res = bpy.data.images.new("detail", w, h, alpha=True, float_buffer=True)
    res.pixels.foreach_set(a.ravel())
    sc = bpy.context.scene
    vt, lk = sc.view_settings.view_transform, sc.view_settings.look
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    res.save_render(png, scene=sc)
    sc.view_settings.view_transform, sc.view_settings.look = vt, lk
    bpy.data.images.remove(res)
    print("g1_detail: %d carbon px, sigma %.2f px, gain %.2f..%.2f" % (int(m.sum()), s, g_lo, g_hi), flush=True)
