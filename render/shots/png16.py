"""16-bit RGB PNG in and out as float arrays (0..1, top row first). Reading goes through bpy (PIL drops 16-bit RGB to
8 bits); writing is a plain zlib encoder. Values are the file's code values (no colour management)."""
import struct
import zlib

import numpy as np


def read(path):
    import bpy
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = "Non-Color"
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float64)


def write(path, img):
    h, w = img.shape[:2]
    a = np.clip(np.round(img[..., :3] * 65535), 0, 65535).astype(">u2")
    raw = b"".join(b"\x00" + a[r].tobytes() for r in range(h))

    def chunk(tg, d):
        c = struct.pack(">I", len(d)) + tg + d
        return c + struct.pack(">I", zlib.crc32(tg + d) & 0xFFFFFFFF)

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 2, 0, 0, 0)))
        fh.write(chunk(b"IDAT", zlib.compress(raw, 6)))
        fh.write(chunk(b"IEND", b""))
