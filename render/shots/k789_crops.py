"""Contact sheet of the page crops of a 16:9 render: python k789_crops.py <png> <out.png> [ratio ...]
ratios like 16:10 4:3 4:5 21:9 (central crops, full height unless the ratio is wider than the frame)."""
import sys
from PIL import Image, ImageDraw

src, dst = sys.argv[1], sys.argv[2]
ratios = sys.argv[3:] or ["16:10", "4:3", "4:5"]
im = Image.open(src).convert("RGB")
W, H = im.size
tiles = []
for r in ratios:
    a, b = (float(v) for v in r.split(":"))
    ar = a / b
    if ar <= W / H:
        cw, ch = int(H * ar), H
    else:
        cw, ch = W, int(W / ar)
    x0, y0 = (W - cw) // 2, (H - ch) // 2
    t = im.crop((x0, y0, x0 + cw, y0 + ch))
    t.thumbnail((10000, 360))
    tiles.append((r, t))
sheet = Image.new("RGB", (sum(t.width for _, t in tiles) + 12 * (len(tiles) + 1), 360 + 36), (255, 255, 255))
x = 12
d = ImageDraw.Draw(sheet)
for r, t in tiles:
    sheet.paste(t, (x, 30))
    d.text((x, 8), r, fill=(0, 0, 0))
    x += t.width + 12
sheet.save(dst)
print(dst)
