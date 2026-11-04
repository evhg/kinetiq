"""seq_masters.py (2026-11-03): a swivel's masters for the private repo without its full frames: f000.png whole and,
for every other frame, only the render region (--crop, where frames 1.. differ from frame 0) as 16-bit PNG, plus
crop.json. Rebuild a frame with k12_lib.paste_region(f000, fNNN, crop, out, feather=1) (the region's pixels already
hold the feathered paste, so a 1 px feather reproduces it).
  $PY seq_masters.py <seq dir> <out dir> x0 x1 y0 y1
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "shots"))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
import numpy as np  # noqa: E402
import k12_lib as K  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
sd, od = argv[0], argv[1]
x0, x1, y0, y1 = [float(v) for v in argv[2:6]]
os.makedirs(od, exist_ok=True)
frames = sorted(f for f in os.listdir(sd) if f.startswith("f") and f.endswith(".png"))
shutil.copy2(os.path.join(sd, "f000.png"), os.path.join(od, "f000.png"))
for f in frames:
    if f == "f000.png" or os.path.exists(os.path.join(od, f)):
        continue
    img = bpy.data.images.load(os.path.join(sd, f), check_existing=False)
    W, H = img.size
    a = np.empty(W * H * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    a = a.reshape(H, W, 4)
    c0, c1 = int(round(x0 * W)), int(round(x1 * W))
    r0, r1 = H - int(round(y1 * H)), H - int(round(y0 * H))
    sub = np.ascontiguousarray(a[r0:r1, c0:c1])
    K._save16(sub, c1 - c0, r1 - r0, os.path.join(od, f))
json.dump(dict(crop=[x0, x1, y0, y1], frames=len(frames)), open(os.path.join(od, "crop.json"), "w"))
print("seq masters", od, len(frames))
