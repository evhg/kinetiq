"""Lay the K03 amber hairline over a base still (display space).
Usage (Blender python): k03s_line.py <mask.png> <base.png> <out_full.png> [--core 0.45] [--halo 0.5] [--sigma 4.0]
mask: K03-section-cut.py --line_mask render (linear white profile, sRGB-encoded 16-bit). The colour follows the brand
tokens: --amber-hot #ffe2bf in the core, --amber #e3a467 at the edges and in the halo; a dimmer (more distant) part of
the line stays amber. Screen blend, so the base under the line is never darkened; output is 16-bit with TPDF dither.
--white 1 (v6, white Command; art director 2026-10-22): screen over white washes the amber out (line saturation 0.33 ->
0.17, a pale gold streak that no longer matches SealedCoreTrace's --amber). On white the line is laid OVER the base with
the mask as alpha, so its edges land exactly on #e3a467 and only the hottest centre pixels on #ffe2bf; the halo first
tints the base toward amber inside its footprint (multiply, --tint) and is then screened on (K05's tint lesson for red
on white). Default --white 0 is v4's screen blend, unchanged."""
import os
import sys

import bpy  # noqa: F401
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k03_lib as L  # noqa: E402

AMBER = np.array([227, 164, 103]) / 255.0
HOT = np.array([255, 226, 191]) / 255.0


def load16(path):
    im = bpy.data.images.load(path, check_existing=False)
    im.colorspace_settings.name = "Non-Color"
    w, h = im.size
    a = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float64)


def srgb_to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def gblur(a, sigma):
    r = int(sigma * 3 + 1)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    b = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, b)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    mask_p, base_p, out_p = args[:3]
    opt = {k[2:]: float(v) for k, v in zip(args[3::2], args[4::2])}
    v = srgb_to_lin(load16(mask_p)).mean(axis=2)
    base = load16(base_p)
    core = opt.get("core", 0.45)
    t = np.clip((v - 0.25) / 0.6, 0.0, 1.0)
    t = t * t * (3 - 2 * t)
    col = AMBER[None, None, :] * (1 - t[..., None]) + HOT[None, None, :] * t[..., None]
    a = np.clip(v / core, 0.0, 1.0)[..., None]
    line = col * a
    hal = opt.get("halo", 0.5) * gblur(v, opt.get("sigma", 4.0))
    halo = AMBER[None, None, :] * hal[..., None]
    if opt.get("white", 0.0) > 0:
        # tint toward amber inside the halo footprint (multiply by amber normalised to its red), then screen the halo,
        # then the line OVER it (mask as alpha): on white the colour of the line is the token colour itself
        k = np.clip(opt.get("tint", 0.6) * hal / max(1e-6, hal.max()), 0.0, 1.0)[..., None]
        an = AMBER / AMBER.max()
        out = base * (1 - k * (1 - an[None, None, :]))
        out = 1 - (1 - out) * (1 - np.clip(halo, 0, 1))
        out = out * (1 - a) + col * a
    else:
        out = 1 - (1 - base) * (1 - line)
        out = 1 - (1 - out) * (1 - np.clip(halo, 0, 1))
    rng = np.random.default_rng(11)
    out += (rng.random(out.shape) - rng.random(out.shape)) / 255.0 * (v[..., None] > 0.002)
    L._png16_write(out_p, np.clip(np.rint(np.clip(out, 0, 1) * 65535.0), 0, 65535).astype(np.uint16))
    print("wrote", out_p, "line px", int((v > 0.05).sum()))


main()
