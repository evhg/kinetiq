"""k05_throat_luma.py <K05 desktop png>: the throat wedge's luma against the rest of the Command face (cloud REQUEST
K05-throat, 2026-11-07), measured on the frame scaled to 2560 wide: medians of fixed boxes (fractions of the frame)."""
import sys
import numpy as np
from PIL import Image
im = Image.open(sys.argv[1]).convert("L")
a = np.asarray(im.resize((1600, 900))).astype(float)
b = lambda x0, x1, y0, y1: float(np.median(a[y0:y1, x0:x1]))
wedge = np.median([b(785, 815, 470, 510), b(785, 815, 610, 650), b(790, 815, 530, 600), b(800, 860, 420, 450)])
rest = np.median([b(880, 940, 500, 540), b(1100, 1180, 360, 420), b(950, 1000, 780, 820), b(1050, 1100, 600, 640),
                  b(860, 900, 380, 420)])
print("throat wedge %d against %d for the rest of the face, neck %d" % (round(wedge), round(rest), round(b(640, 690, 520, 600))))
