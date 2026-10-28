"""Regenerate the kit's derived inputs under $KQ_RENDER_OUT/assets (run by setup.sh; safe to re-run).

What the lost scratchpad held next to the scripts, and how each was made (from the session transcripts):
  fonts/Archivo-var.ttf, OFL.txt      google/fonts ofl/archivo (2026-10-21), OFL
  fonts/Archivo-ExpandedExtraBold.ttf  instancer wdth 125, wght 800   (racket.FONT_BOLD)
  fonts/Archivo-Medium.ttf             instancer wdth 100, wght 500   (racket.FONT_MED)
  fonts/Saira-var.ttf, Saira-OFL.txt   google/fonts ofl/saira (2026-10-22), OFL (kq_canon serial etch)
  tex/                                 make_weave.py tex; make_spread.py tex (racket.py 3K / 12K maps)
  k04_tex2/                            shots/k04_weave2.py 4096, then shots/k04_gap.py (gap16.png)
  k04_bake/                            shots/k04_bake.py, then shots/k04_bake_warp.py (warpx16 / warpy16)
canon/, k10/, k12/, k14/ are caches the shots write themselves on first use.
"""
import os
import subprocess
import sys
import urllib.request

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
import kqpaths as P  # noqa: E402

PY = sys.executable
FONTS = {
    "Archivo-var.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf",
    "OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/OFL.txt",
    "Saira-var.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/saira/Saira%5Bwdth,wght%5D.ttf",
    "Saira-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/saira/OFL.txt",
}


def run(args, **kw):
    print("+", " ".join(args), flush=True)
    subprocess.run(args, check=True, **kw)


def main():
    force = "--force" in sys.argv
    for d in ("fonts", "tex", "k04_tex2", "k04_bake", "canon", "k10", "k12", "k14"):
        os.makedirs(P.asset(d), exist_ok=True)
    os.makedirs(P.OUT, exist_ok=True)
    for name, url in FONTS.items():
        dst = P.font(name)
        if force or not os.path.exists(dst):
            print("download", name, flush=True)
            urllib.request.urlretrieve(url, dst)
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for name, axes in (("Archivo-ExpandedExtraBold.ttf", {"wdth": 125, "wght": 800}),
                       ("Archivo-Medium.ttf", {"wdth": 100, "wght": 500})):
        dst = P.font(name)
        if force or not os.path.exists(dst):
            instancer.instantiateVariableFont(TTFont(P.font("Archivo-var.ttf")), axes).save(dst)
            print("instanced", name, flush=True)
    if force or not os.path.exists(P.asset("tex", "weave_normal.png")):
        run([PY, os.path.join(KIT, "make_weave.py"), P.asset("tex")])
    if force or not os.path.exists(P.asset("tex", "spread_albedo.png")):
        run([PY, os.path.join(KIT, "make_spread.py"), P.asset("tex")])
    if force or not os.path.exists(P.asset("k04_tex2", "coat16.png")):
        run([PY, os.path.join(KIT, "shots", "k04_weave2.py"), "4096"])
    if force or not os.path.exists(P.asset("k04_tex2", "gap16.png")):
        run([PY, os.path.join(KIT, "shots", "k04_gap.py")])
    if force or not os.path.exists(P.asset("k04_bake", "bake.json")):
        run([PY, os.path.join(KIT, "shots", "k04_bake.py")])
    if force or not os.path.exists(P.asset("k04_bake", "warp.json")):
        run([PY, os.path.join(KIT, "shots", "k04_bake_warp.py")])
    print("assets ready in", P.ASSETS)


if __name__ == "__main__":
    main()
