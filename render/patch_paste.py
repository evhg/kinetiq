"""patch_paste.py (2026-11-03, the Naked cap patches): paste a border render (KQ_BORDER_AUTO=1, full-size, black
outside the border) into an existing master, feathered, and check that the two agree where they overlap.

  $PY patch_paste.py <new.png> <master.png> <border.json> [--feather 32] [--out <path>] [--max-ring 1.5]

The border region (x0 x1 y0 y1, top-left origin) is pasted with a `feather`-px smoothstep ramp inside every edge that
is inside the frame. The ring check: mean absolute difference (8-bit display units) between new and master in the band
from `feather` to 3 x `feather` px inside the region's edge, where nothing changed but the render is the same scene
and seed. Over --max-ring the paste is refused (exit 2): the shot's comp is not local (a global grade or bloom) and the
still needs a full re-render. Writes 16-bit (k12_lib._save16) to --out, default the master itself.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "shots"))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
import numpy as np  # noqa: E402
import k12_lib as K  # noqa: E402


def load(p):
    img = bpy.data.images.load(p, check_existing=False)
    img.colorspace_settings.name = "Non-Color"
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4), w, h


def main(argv):
    pos = [a for a in argv if not a.startswith("--")]
    opt = {argv[i][2:]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--")}
    new_p, base_p, bj = pos[:3]
    feather = int(opt.get("feather", 32))
    out = opt.get("out", base_p)
    max_ring = float(opt.get("max-ring", 1.5))
    b = json.load(open(bj))["border"]
    N, W, H = load(new_p)
    B, W2, H2 = load(base_p)
    if (W, H) != (W2, H2):
        print("SIZE-MISMATCH", W, H, W2, H2); return 3
    x0, x1 = int(round(b[0] * W)), int(round(b[1] * W))
    yt, yb_ = int(round(b[2] * H)), int(round(b[3] * H))
    r0, r1 = H - yb_, H - yt            # Blender rows run bottom-up
    w, h = x1 - x0, r1 - r0

    li = (x0 > 0, x1 < W, r0 > 0, r1 < H)
    big = 1e9
    kx = np.arange(w, dtype=np.float32) + 0.5
    ky = np.arange(h, dtype=np.float32) + 0.5
    dx = np.minimum(np.where(li[0], kx, big), np.where(li[1], w - kx, big))
    dy = np.minimum(np.where(li[2], ky, big), np.where(li[3], h - ky, big))
    d = np.minimum(dy[:, None], dx[None, :])          # px to the nearest edge inside the frame
    t = np.clip((d - feather) / feather, 0, 1)        # 0 over the outer `feather` px (the border render's own edge)
    mask = t * t * (3 - 2 * t)
    ring_in = (d >= 2 * feather) & (d < 4 * feather)
    sub_n = N[r0:r1, x0:x1, :3]
    sub_b = B[r0:r1, x0:x1, :3]
    diff = np.abs(sub_n - sub_b).mean(-1) * 255
    rd = float(diff[ring_in].mean()) if ring_in.any() else 0.0
    core = float(diff[mask > 0.999].mean()) if (mask > 0.999).any() else 0.0
    print("RING %.3f CORE %.3f region %d,%d %dx%d" % (rd, core, x0, yt, w, h), flush=True)
    if rd > max_ring:
        print("REFUSED ring difference %.3f > %.3f" % (rd, max_ring)); return 2
    B[r0:r1, x0:x1, :3] = sub_n * mask[..., None] + sub_b * (1 - mask[..., None])
    B[..., 3] = 1.0
    K._save16(B, W, H, out)
    print("PASTED", out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]))
