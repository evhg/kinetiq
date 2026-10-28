"""Quick look-dev render: racket floating, 3/4 view, low-key studio."""
import math
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import bpy  # noqa: E402
import racket  # noqa: E402
import studio  # noqa: E402

w, h, spp = (int(a) for a in (sys.argv[1:4] if len(sys.argv) >= 4 else (1280, 720, 48)))
t0 = time.time()
studio.reset()
studio.settings(w, h, spp)
root = racket.build_racket("KQ", serial="No. 001 / 500", edition="limited")
# stand the racket up: face toward -Y (camera side), head up
root.rotation_euler = (math.radians(90), math.radians(0), math.radians(-24))
root.location = (0, 0, 0.36)
studio.floor()
# key: big soft box high camera-left
studio.area_light("Key", (-1.1, -1.4, 1.6), 1.4, 220, target=(0, 0, 0.35), size_y=0.6)
# rims: two tall strips behind, tracing the frame edge
studio.area_light("RimL", (-0.75, 0.9, 0.55), 0.08, 160, size_y=1.6, target=(0, 0, 0.35))
studio.area_light("RimR", (0.8, 0.85, 0.6), 0.08, 200, size_y=1.6, target=(0, 0, 0.35))
# light shaft on the floor
studio.spot_light("Shaft", (-2.5, -2.0, 3.2), 2600, 4.5, 0.05, target=(0.0, -0.25, 0.0))
studio.camera((0.0, -1.55, 0.42), (0.0, 0, 0.33), lens=70)
print("scene built in", round(time.time() - t0, 1), "s")
p = studio.render(f"test_{w}x{h}")
print("rendered", p, "in", round(time.time() - t0, 1), "s")
