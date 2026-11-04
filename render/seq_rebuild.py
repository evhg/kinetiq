"""seq_rebuild.py (2026-11-04): the inverse of seq_masters.py. Rebuilds a swivel's whole frames from its masters (f000.png
whole plus, for frames 1.., the render region with crop.json) with k12_lib.paste_region(..., feather=1), so
scripts/sequence.mjs can export them. Shard k of n lets four processes share the frames (4 cores).
  $PY render/seq_rebuild.py <masters seq dir> <out dir> [k n]
Checked 2026-11-04 on the Mac's K01 swivels: the region matches its master to 1/255 and nothing outside it changes;
frame 0 is the -full still bit for bit (mean luma difference 0.00).
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "shots"))
sys.path.insert(0, HERE)
import k12_lib as K  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
sd, od = argv[0], argv[1]
k, n = (int(argv[2]), int(argv[3])) if len(argv) > 3 else (0, 1)
os.makedirs(od, exist_ok=True)
crop = json.load(open(os.path.join(sd, "crop.json")))["crop"]
frames = sorted(f for f in os.listdir(sd) if f.startswith("f") and f.endswith(".png"))
if k == 0 and not os.path.exists(os.path.join(od, "f000.png")):
    shutil.copy2(os.path.join(sd, "f000.png"), os.path.join(od, "f000.png"))
for j, f in enumerate(frames):
    if f == "f000.png" or j % n != k:
        continue
    dst = os.path.join(od, f)
    if os.path.exists(dst):
        continue
    K.paste_region(os.path.join(sd, "f000.png"), os.path.join(sd, f), crop, dst + ".tmp.png", feather=1)
    os.replace(dst + ".tmp.png", dst)
    print("rebuilt", dst, flush=True)
