import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, studio
from look_c import softbox
mode = sys.argv[-1]
OUT = os.path.join(studio.OUT, "k45")
if mode == "render":
    sc = studio.reset(); studio.settings(160, 90, 8)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3)
    s = bpy.context.active_object
    s.data.materials.append(bpy.data.materials.new("m"))
    vl = sc.view_layers[0]
    l1 = studio.area_light("A", (1, -1, 1), 0.5, 40, target=(0, 0, 0))
    l2 = studio.area_light("B", (-1, -1, 1), 0.5, 40, color=(1, .4, .1), target=(0, 0, 0))
    studio.camera((0, -2, 0.3), (0, 0, 0), lens=50)
    vl.lightgroups.add(name="ga"); vl.lightgroups.add(name="gb")
    l1.lightgroup = "ga"; l2.lightgroup = "gb"
    vl.cycles.denoising_store_passes = True
    if os.environ.get("EXR"):
        sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        sc.render.image_settings.color_depth = "32"
    sc.use_nodes = True
    tr = sc.node_tree
    rl = tr.nodes["Render Layers"]
    print([o.name for o in rl.outputs])
    fo = tr.nodes.new("CompositorNodeOutputFile")
    fo.base_path = OUT + "/fo_"
    fo.format.file_format = "PNG"
    fo.file_slots[0].path = "ga"
    tr.links.new(rl.outputs["Combined_ga"], fo.inputs[0])
    comp = tr.nodes["Composite"]
    tr.links.new(rl.outputs["Combined_ga"], comp.inputs[0])
    sc.render.filepath = OUT + ("/lgtest.exr" if os.environ.get("EXR") else "/main_ga.png")
    bpy.ops.render.render(write_still=True)
    # also save the composite directly as png for comparison
else:
    sc = studio.reset(); studio.settings(160, 90, 1)
    sc.use_nodes = True
    tr = sc.node_tree
    for n in list(tr.nodes): tr.nodes.remove(n)
    im = tr.nodes.new("CompositorNodeImage")
    img = bpy.data.images.load(OUT + "/lgtest.exr")
    im.image = img
    print(img.type, [l for l in dir(im) if 'layer' in l])
    try:
        im.layer = "ViewLayer"
    except Exception as e: print(e)
    print(img.size[:], img.type)
    im.image = None; im.image = img
    print([o.name for o in im.outputs])
    print([o.name for o in im.outputs])
    comp = tr.nodes.new("CompositorNodeComposite")
    tr.links.new(im.outputs["Combined_ga"], comp.inputs[0])
    sc.render.filepath = OUT + "/comp_ga.png"
    bpy.ops.render.render(write_still=True)
