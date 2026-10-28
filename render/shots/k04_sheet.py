"""Contact sheet: python k04_sheet.py out.png in1.png in2.png ... (labels = file stems)."""
import os, sys
from PIL import Image, ImageDraw
ims = [Image.open(p).convert("RGB") for p in sys.argv[2:]]
w = max(i.width for i in ims); h = max(i.height for i in ims)
cols = 2 if len(ims) > 1 else 1
rows = (len(ims) + cols - 1) // cols
sh = Image.new("RGB", (cols * w, rows * h), (40, 0, 0))
d = ImageDraw.Draw(sh)
for k, (im, p) in enumerate(zip(ims, sys.argv[2:])):
    x, y = (k % cols) * w, (k // cols) * h
    sh.paste(im, (x, y))
    d.text((x + 6, y + 4), os.path.basename(p)[:-4], fill=(255, 255, 0))
sh.save(sys.argv[1])
