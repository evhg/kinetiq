"""Shared studio helpers: reset, render settings, lights, camera, floor."""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kqpaths  # noqa: E402
OUT = kqpaths.OUT  # previews and finals: $KQ_RENDER_OUT/out (outside git)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 6
    sc.cycles.transparent_max_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.threads_mode = "AUTO"
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.world = world
    return sc


def settings(w, h, samples=128, pct=100):
    sc = bpy.context.scene
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = pct
    sc.cycles.samples = samples


def area_light(name, loc, size, energy, color=(1, 1, 1), shape="RECTANGLE", size_y=None, target=None, spread=180):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = shape
    ld.size = size
    if size_y is not None:
        ld.size_y = size_y
    ld.energy = energy
    ld.color = color
    ld.spread = math.radians(spread)
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if target is not None:
        aim(ob, target)
    return ob


def spot_light(name, loc, energy, angle_deg, blend=0.15, color=(1, 1, 1), target=None, radius=0.01):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy = energy
    ld.spot_size = math.radians(angle_deg)
    ld.spot_blend = blend
    ld.color = color
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if target is not None:
        aim(ob, target)
    return ob


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=85, sensor=36, dof_obj=None, fstop=None, shift=(0, 0)):
    cd = bpy.data.cameras.new("Cam")
    cd.lens = lens
    cd.sensor_width = sensor
    cd.shift_x, cd.shift_y = shift
    ob = bpy.data.objects.new("Cam", cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        if dof_obj is not None:
            cd.dof.focus_object = dof_obj
        else:
            cd.dof.focus_distance = (Vector(target) - Vector(loc)).length
    bpy.context.scene.camera = ob
    return ob


def floor(color=(0.004, 0.004, 0.0045), rough=0.22, size=40):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    fl = bpy.context.active_object
    fl.name = "Floor"
    m = bpy.data.materials.new("FloorMat")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.5
    # very subtle concrete-like micro variation
    nodes, links = m.node_tree.nodes, m.node_tree.links
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 60
    noise.inputs["Detail"].default_value = 8
    rmap = nodes.new("ShaderNodeMapRange")
    rmap.inputs["To Min"].default_value = rough * 0.8
    rmap.inputs["To Max"].default_value = rough * 1.4
    links.new(noise.outputs["Fac"], rmap.inputs["Value"])
    links.new(rmap.outputs["Result"], b.inputs["Roughness"])
    fl.data.materials.append(m)
    return fl


def backdrop(color=(0.003, 0.003, 0.0035), rough=0.6, y=3.0, height=6):
    bpy.ops.mesh.primitive_plane_add(size=height * 2, location=(0, y, height / 2), rotation=(math.radians(90), 0, 0))
    bd = bpy.context.active_object
    bd.name = "Backdrop"
    m = bpy.data.materials.new("BackdropMat")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    bd.data.materials.append(m)
    return bd


def _auto_border(sc, path):
    """KQ_BORDER_AUTO=1 (2026-11-03, the Naked cap patches): render only the butt region (Cycles border, full-size
    output, black outside), found from the projected bounding box of every racket's cap (the hidden stub under Naked)
    and Q mark, grown by KQ_BORDER_GROW (default 0.6 of its size) and 48 px, and KQ_BORDER_DOWN (default 1.5 heights)
    further down for floor reflections. Writes <path>.border.json (x0 x1 y0 y1, top-left origin) for patch_paste.py."""
    import json
    import numpy as np
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    W, H = sc.render.resolution_x, sc.render.resolution_y
    proj = np.array(cam.calc_matrix_camera(dg, x=W, y=H) @ cam.matrix_world.inverted())
    lo, hi = np.array([9.0, 9.0]), np.array([-9.0, -9.0])
    for ob in sc.objects:
        if ob.type != "MESH" or ob.get("kq_part") not in ("cap", "capmark"):
            continue
        me = ob.data
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        hom = np.c_[co, np.ones(len(co))] @ (proj @ np.array(ob.matrix_world)).T
        ok = hom[:, 3] > 1e-6
        xy = hom[ok, :2] / hom[ok, 3:4]
        f = np.c_[(xy[:, 0] + 1) / 2, 1 - (xy[:, 1] + 1) / 2]
        lo = np.minimum(lo, f.min(0)); hi = np.maximum(hi, f.max(0))
    if hi[0] < lo[0]:
        raise SystemExit("KQ_BORDER_AUTO: no cap in the scene")
    g = float(os.environ.get("KQ_BORDER_GROW", "0.6"))
    dn = float(os.environ.get("KQ_BORDER_DOWN", "1.5"))
    sz = hi - lo
    x0 = lo[0] - sz[0] * g - 48 / W
    x1 = hi[0] + sz[0] * g + 48 / W
    y0 = lo[1] - sz[1] * g - 48 / H
    y1 = hi[1] + sz[1] * (g + dn) + 48 / H
    b = [max(0.0, x0), min(1.0, x1), max(0.0, y0), min(1.0, y1)]
    r = sc.render
    r.use_border = True
    r.use_crop_to_border = False
    r.border_min_x, r.border_max_x = b[0], b[1]
    r.border_min_y, r.border_max_y = 1 - b[3], 1 - b[2]
    with open(path + ".border.json", "w") as fh:
        json.dump(dict(border=b, w=W, h=H), fh)
    print("KQ_BORDER_AUTO border", " ".join("%.4f" % v for v in b), flush=True)


def render(name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".png")
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


# KQ_BORDER_AUTO=1: every render of the process (studio.render or a shot's own bpy.ops.render.render) takes the cap
# border first: bpy.ops.render.render is wrapped through the bpy.ops module's __getattr__ (a render_pre handler runs
# after the render has read its settings). The sidecar is named after the scene's output path, or out/_border/<n>
# when a shot saves its result itself.
_BORDER_N = [0]


def _border_now():
    scene = bpy.context.scene
    fp = bpy.path.abspath(scene.render.filepath or "")
    if not fp or fp.endswith(os.sep) or fp.endswith("/tmp/"):
        os.makedirs(os.path.join(OUT, "_border"), exist_ok=True)
        _BORDER_N[0] += 1
        fp = os.path.join(OUT, "_border", "%03d" % _BORDER_N[0])
    _auto_border(scene, fp)


class _RenderOpsProxy:
    """bpy.ops.render with .render wrapped (_border_now first); everything else forwarded."""
    def __init__(self, sub):
        self._sub = sub

    def __getattr__(self, name):
        if name == "render":
            orig = self._sub.render

            def render_wrapped(*a, **k):
                _border_now()
                return orig(*a, **k)
            return render_wrapped
        return getattr(self._sub, name)


if os.environ.get("KQ_BORDER_AUTO") == "1":
    _ops = sys.modules["bpy.ops"]
    if not isinstance(_ops.__dict__.get("render"), _RenderOpsProxy):
        setattr(_ops, "render", _RenderOpsProxy(getattr(_ops, "render")))
