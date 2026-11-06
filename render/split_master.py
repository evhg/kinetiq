"""split_master.py <master.png> [rows]: split a 16-bit RGBA master (K05's taller frame, over GitHub's 100 MB file limit
at 5760) losslessly into <name>-a.png (rows 0..rows-1) and <name>-b.png (the rest), 16-bit RGBA each. Rejoin: stack a
over b (numpy vstack, or sharp/ImageMagick -append). Default rows: half the height. Run with the kit's bpy python."""
import struct
import sys
import zlib

import bpy
import numpy as np


def write16(path, a16):
    h, w, c = a16.shape
    raw = np.empty((h, 1 + w * c * 2), dtype=np.uint8)
    raw[:, 0] = 0
    raw[:, 1:] = a16.astype(">u2").view(np.uint8).reshape(h, w * c * 2)

    def chunk(tag, data):
        b = struct.pack(">I", len(data)) + tag + data
        return b + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 6 if c == 4 else 2, 0, 0, 0))
    png += chunk(b"sRGB", b"\x00") + chunk(b"IDAT", zlib.compress(raw.tobytes(), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src = args[0]
im = bpy.data.images.load(src, check_existing=False)
im.colorspace_settings.name = "Non-Color"
w, h = im.size
px = np.empty(w * h * 4, dtype=np.float32)
im.pixels.foreach_get(px)
a = np.rint(px.reshape(h, w, 4)[::-1] * 65535.0).astype(np.uint16)
r = int(args[1]) if len(args) > 1 else h // 2
base = src[:-4]
write16(base + "-a.png", a[:r])
write16(base + "-b.png", a[r:])
print("split", src, w, h, "->", r, h - r)
