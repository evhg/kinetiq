"""Look-dev C: reflection-only lighting with gradient softboxes. Usage: look_c.py W H SPP NAME"""
import math
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import bpy  # noqa: E402
import racket  # noqa: E402
import studio  # noqa: E402


def softbox(name, loc, size, strength, target, gradient=True, color=(1, 1, 1)):
    """Emissive plane with a soft falloff gradient, visible in reflections."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    studio.aim(ob, target)
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    if gradient:
        tc = nodes.new("ShaderNodeTexCoord")
        sep = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tc.outputs["Generated"], sep.inputs["Vector"])
        # brightest along the centre line, falling off to the long edges, plus along-length fade
        cx = nodes.new("ShaderNodeMath"); cx.operation = "SUBTRACT"; cx.inputs[1].default_value = 0.5
        links.new(sep.outputs["Y"], cx.inputs[0])
        ab = nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; links.new(cx.outputs[0], ab.inputs[0])
        f1 = nodes.new("ShaderNodeMapRange")
        f1.inputs["From Min"].default_value = 0.0; f1.inputs["From Max"].default_value = 0.5
        f1.inputs["To Min"].default_value = 1.0; f1.inputs["To Max"].default_value = 0.0
        f1.interpolation_type = "SMOOTHSTEP"
        links.new(ab.outputs[0], f1.inputs["Value"])
        f2 = nodes.new("ShaderNodeMapRange")
        f2.inputs["From Min"].default_value = 0.0; f2.inputs["From Max"].default_value = 1.0
        f2.inputs["To Min"].default_value = 0.15; f2.inputs["To Max"].default_value = 1.0
        f2.interpolation_type = "SMOOTHERSTEP"
        links.new(sep.outputs["X"], f2.inputs["Value"])
        mul = nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        links.new(f1.outputs["Result"], mul.inputs[0]); links.new(f2.outputs["Result"], mul.inputs[1])
        st = nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = strength
        links.new(mul.outputs[0], st.inputs[0])
        links.new(st.outputs[0], em.inputs["Strength"])
    else:
        em.inputs["Strength"].default_value = strength
    links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    ob.visible_camera = False
    return ob


if __name__ == "__main__":
    a = sys.argv[1:]
    w, h, spp, name = int(a[0]), int(a[1]), int(a[2]), a[3]
    t0 = time.time()
    studio.reset()
    studio.settings(w, h, spp)
    root = racket.build_racket("KQ", edition="reserve")
    root.rotation_euler = (math.radians(90 - 8), 0, math.radians(-30))
    centre = (0, 0, 0.5)
    root.location = (0, 0, 0.55)
    studio.floor(rough=0.14)
    # overhead gradient softbox, slightly in front: the face mirrors it as a long fading highlight
    # side gradient softbox where the face mirrors to the camera: its falloff edge sweeps the face
    softbox("Side", (-1.3, -0.25, 0.85), (1.6, 1.0), 4.0, centre)
    softbox("Overhead", (-0.15, -0.2, 1.6), (1.4, 0.6), 2.0, centre)
    # rim strips behind left and right: trace the frame
    softbox("RimL", (-0.9, 0.55, 0.6), (0.06, 1.3), 18.0, centre, gradient=False)
    softbox("RimR", (0.85, 0.6, 0.7), (0.06, 1.3), 22.0, centre, gradient=False)
    # low kicker strip camera-right for the grip and lower frame
    softbox("Kick", (0.9, -0.8, 0.25), (0.08, 0.7), 3.0, centre, gradient=False)
    studio.spot_light("Shaft", (-3.0, -1.0, 3.4), 1400, 3.0, 0.08, target=(0.35, -0.55, 0.0))
    studio.camera((0.5, -1.75, 0.6), (0.0, 0, 0.5), lens=85)
    p = studio.render(name)
    print("rendered", p, round(time.time() - t0, 1), "s")
