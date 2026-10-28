"""Where the render kit lives and where everything it generates goes.

The kit (this folder) is in git; nothing it writes is. Generated files go under KQ_RENDER_OUT
(default /home/user/kinetiq-render-out, outside the repo):
  $KQ_RENDER_OUT/out/      previews and finals (studio.OUT; --out paths are relative to it)
  $KQ_RENDER_OUT/assets/   derived inputs: fonts/, tex/, k04_tex/, k04_tex2/, k04_bake/, canon/, k10/, k12/, k14/
  $KQ_RENDER_OUT/bpyenv/   the Python 3.11 + bpy 4.2 venv (render/setup.sh)
RENDER_ROOT overrides where the kit itself is (default: this folder).
"""
import os

ROOT = os.environ.get("RENDER_ROOT") or os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.environ.get("KQ_RENDER_OUT") or "/home/user/kinetiq-render-out"
OUT = os.path.join(OUT_ROOT, "out")
ASSETS = os.path.join(OUT_ROOT, "assets")
FONTS = os.path.join(ASSETS, "fonts")


def asset(*parts):
    return os.path.join(ASSETS, *parts)


def font(name):
    return os.path.join(FONTS, name)
