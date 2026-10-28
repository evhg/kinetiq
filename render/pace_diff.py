"""pace_diff.py <old.png> <new.png> <out_diff.png>: the Command half of K08 (x 0 .. 0.5 of the frame, and the page's
left crop x 0.025 .. 0.425) compared pixel for pixel (8-bit RGB): max and mean |difference|, pixels differing by more than
0 / 2 / 8 levels, and a difference image (x16, the left crop and the right crop side by side)."""
import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(np.int32)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(np.int32)
H, W = a.shape[:2]
d = np.abs(a - b).max(axis=2)
for nm, x0, x1 in (("left half 0-0.5", 0.0, 0.5), ("left crop .025-.425", 0.025, 0.425), ("right crop .575-.975", 0.575, 0.975)):
    s = d[:, round(W * x0):round(W * x1)]
    print("%-22s max %3d  mean %.4f  px >0: %d  >2: %d  >8: %d  (of %d)" % (nm, s.max(), s.mean(), (s > 0).sum(), (s > 2).sum(),
                                                                         (s > 8).sum(), s.size))
img = np.clip(d * 16, 0, 255).astype(np.uint8)
Image.fromarray(img).save(sys.argv[3])
