"""Page crops of a K03/K03b still: phone box (x 0.25-0.75, y 0.28-0.82) and card (x 0.275-0.725, full height).
Usage: python k03s_crops.py <png> [<png> ...]  -> writes <name>_phone.png and <name>_card.png (8-bit) next to it."""
import sys
from PIL import Image
for p in sys.argv[1:]:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    base = p[:-4]
    im.crop((round(0.25 * w), round(0.28 * h), round(0.75 * w), round(0.82 * h))).save(base + "_phone.png")
    im.crop((round(0.275 * w), 0, round(0.725 * w), h)).save(base + "_card.png")
    print(base + "_phone.png", base + "_card.png")
