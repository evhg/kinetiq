"""Swivel sequence checks: temporal stability, crop safety, frame-0 vs the lit final, contact sheet, check MP4.
usage: ../bpyenv/bin/python shots/seq_check.py out/seq/K01-swivel-command-desktop [final.png]"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

d = sys.argv[1]
final = sys.argv[2] if len(sys.argv) > 2 else None
fr = sorted(f for f in os.listdir(d) if f.startswith("f") and f.endswith(".png"))
meta = {}
if os.path.exists(os.path.join(d, "frames.jsonl")):
    for ln in open(os.path.join(d, "frames.jsonl")):
        r = json.loads(ln); meta[r["i"]] = r
W8 = np.array([0.2126, 0.7152, 0.0722])
def load(f):
    return np.asarray(Image.open(os.path.join(d, f)).convert("RGB")).astype(np.float32)
imgs = [load(f) for f in fr]
H, W = imgs[0].shape[:2]
phone = H > W
lum = [im @ W8 for im in imgs]
means = np.array([l.mean() for l in lum])
# background mask: outside the union of the racket's projected boxes (+3 % margin) over every frame
bm = np.ones((H, W), bool)
for r in meta.values():
    x0, y0, x1, y1 = r["bbox"]
    bm[max(0, int((y0 - .03) * H)):int((y1 + .03) * H), max(0, int((x0 - .03) * W)):int((x1 + .03) * W)] = False
def hp(l):
    im = Image.fromarray(np.clip(l, 0, 255).astype(np.uint8))
    return l - np.asarray(im.filter(ImageFilter.GaussianBlur(2))).astype(np.float32)
hps = [hp(l) for l in lum]
bg_hp = [float(np.abs(hps[i + 1] - hps[i])[bm].mean()) for i in range(len(fr) - 1)]
bg_mean = [float(abs(lum[i + 1][bm].mean() - lum[i][bm].mean())) for i in range(len(fr) - 1)]
d2 = np.abs(np.diff(means, 2)) if len(means) > 2 else np.array([0])
res = dict(frames=len(fr), size=[W, H], mean_luma_first_last=[round(float(means[0]), 2), round(float(means[-1]), 2)],
           mean_luma_step_max=round(float(np.abs(np.diff(means)).max()), 3) if len(fr) > 1 else 0,
           mean_luma_2nd_diff_max=round(float(d2.max()), 3),
           bg_highpass_diff_mean=round(float(np.mean(bg_hp)), 3) if bg_hp else 0,
           bg_highpass_diff_max=round(float(np.max(bg_hp)), 3) if bg_hp else 0,
           bg_mean_luma_step_max=round(float(np.max(bg_mean)), 3) if bg_mean else 0,
           bg_px_share=round(float(bm.mean()), 3))
# crop safety: desktop card crop x 0.30-0.70 and the widest cover crop (2560x1080: y 12.5-87.5 %);
# phone: object-fit cover, bottom-anchored, 390x844 -> x 9-91 %
bbs = np.array([r["bbox"] for r in meta.values()]) if meta else None
if bbs is not None:
    u = [float(bbs[:, 0].min()), float(bbs[:, 1].min()), float(bbs[:, 2].max()), float(bbs[:, 3].max())]
    box = (0.09, 0.0, 0.91, 1.0) if phone else (0.30, 0.125, 0.70, 0.875)
    res["bbox_union_pct"] = [round(100 * q, 1) for q in u]
    res["crop_box_pct"] = [round(100 * q, 1) for q in box]
    res["inside_crop"] = bool(u[0] >= box[0] and u[1] >= box[1] and u[2] <= box[2] and u[3] <= box[3])
    sec = [r["sec"] for r in meta.values()]
    res["sec_per_frame_median"] = float(np.median(sec)); res["spp"] = list(meta.values())[0]["spp"]
if final:
    fi = Image.open(final).convert("RGB").resize((W, H), Image.LANCZOS)
    fa = np.asarray(fi).astype(np.float32) @ W8
    diff = np.abs(fa - lum[0])
    res["f0_vs_final_mean_abs_luma"] = round(float(diff.mean()), 3)
    res["f0_vs_final_p99_abs_luma"] = round(float(np.percentile(diff, 99)), 2)
    res["f0_vs_final_mean_luma"] = [round(float(lum[0].mean()), 2), round(float(fa.mean()), 2)]
    # composition: silhouette (luma edge map) correlation
    def edges(l):
        gx = np.abs(np.diff(l, axis=1))[:-1]; gy = np.abs(np.diff(l, axis=0))[:, :-1]
        return gx + gy
    e0, e1 = edges(lum[0]), edges(fa)
    res["f0_vs_final_edge_corr"] = round(float(np.corrcoef(e0.ravel(), e1.ravel())[0, 1]), 4)
    Image.fromarray(np.clip(diff * 4, 0, 255).astype(np.uint8)).save(os.path.join(os.path.dirname(d), os.path.basename(d) + "_f0diff_x4.png"))
# contact sheet 6 x 6
cols = 6; tw = 320 if not phone else 180; th = int(tw * H / W)
rows = (len(fr) + cols - 1) // cols
sh = Image.new("RGB", (cols * tw, rows * (th + 18)), (10, 10, 11))
dr = ImageDraw.Draw(sh)
for k, f in enumerate(fr):
    t = Image.fromarray(imgs[k].astype(np.uint8)).resize((tw, th), Image.LANCZOS)
    x, y = (k % cols) * tw, (k // cols) * (th + 18)
    sh.paste(t, (x, y))
    yaw = meta.get(int(f[1:4]), {}).get("yaw", "?")
    dr.text((x + 4, y + th + 3), f"{f[:-4]}  yaw {yaw}", fill=(200, 200, 200))
sp = os.path.join(os.path.dirname(d), os.path.basename(d) + "_sheet.png")
sh.save(sp); res["sheet"] = sp
# check MP4: forward + back, 24 fps, 960 px on the long side
mp = os.path.join(os.path.dirname(d), os.path.basename(d) + "_check.mp4")
if len(fr) > 2:
    lst = os.path.join(d, "_w", "pingpong.txt"); os.makedirs(os.path.dirname(lst), exist_ok=True)
    seq = list(range(len(fr))) + list(range(len(fr) - 2, 0, -1))
    with open(lst, "w") as fh:
        for i in seq:
            fh.write(f"file '{os.path.abspath(os.path.join(d, fr[i]))}'\nduration {1/24:.5f}\n")
    sc = "scale=960:-2" if not phone else "scale=-2:960"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf", sc + ",format=yuv420p",
                        "-r", "24", "-c:v", "libx264", "-crf", "18", mp], capture_output=True, text=True)
    res["mp4"] = mp if r.returncode == 0 else "ffmpeg failed: " + r.stderr[-300:]
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(d), os.path.basename(d) + "_check.json"), "w"), indent=1)
