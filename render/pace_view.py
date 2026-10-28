"""pace_view.py <crop.png> <out_prefix>: the page crop at phone (420 px) and desktop (600 px) width, and a side-by-side."""
import sys
from PIL import Image
a = Image.open(sys.argv[1]).convert("RGB")
pre = sys.argv[2]
for w in (420, 600):
    a.resize((w, round(w * a.size[1] / a.size[0])), Image.LANCZOS).save("%s_%d.png" % (pre, w))
