"""Calibrate camera-visible emission radiance -> display sRGB value under the studio view transform (AgX Punchy)."""
import os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import bpy, numpy as np
import studio
vals = [0.002, 0.004, 0.006, 0.008, 0.010, 0.013, 0.016, 0.020, 0.025, 0.030, 0.035, 0.040, 0.05, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20, 0.3, 0.5, 1.0]
sc = studio.reset()
studio.settings(len(vals) * 4, 4, 1)
sc.cycles.use_denoising = False
for i, v in enumerate(vals):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(i + 0.5, 0, 0))
    ob = bpy.context.active_object
    m = bpy.data.materials.new(f"e{i}"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = v
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], o.inputs[0])
    ob.data.materials.append(m)
cd = bpy.data.cameras.new("C"); cd.type = "ORTHO"; cd.ortho_scale = len(vals)
cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam)
cam.location = (len(vals) / 2, 0, 5)
sc.camera = cam
p = studio.render("k12/calib")
from PIL import Image
a = np.asarray(Image.open(p).convert("RGB")).astype(float)
row = a[2]
for i, v in enumerate(vals):
    px = row[i * 4 + 2]
    print(f"emit {v:.3f} -> display {px[0]:.0f}")
