"""kw_sheen: small lighting helpers for the white-Command making group (K06, K07, K09), stage 3a critique.

gloss_sweep  the clear coat's reflection as one SOFT diagonal sweep on a flat face (any orientation), designed on the
             face and mapped to a card parallel to it through the mirrored camera (K05 v6's gloss_strip, generalised).
             Glossy-only, see-through, no shadow, with a honeycomb grid (it emits only along the mirror path to the
             camera, within tol_deg), so the white fibres' broad sheen lobe cannot collect it from the whole face and
             the shade keeps its gradient. The profile across the band is a smoothstep bump (1 on the centre line, 0 at
             +-wf): a sweep, never a hairline (critique: the old 1.6 mm band / band-card hot line read as a crease).
exclude      light linking by exclusion: the emitter lights everything except `objs`.

Imported only by K06-mould.py, K07-lineup-five.py and K09-case-three.py. No edits to the shared libraries.
"""
import math

import bpy
from mathutils import Vector


def _n(nodes, kind, op=None):
    nd = nodes.new(kind)
    if op is not None:
        nd.operation = op
    return nd


def gloss_sweep(name, cam_loc, face_c, face_n, a, b, wf, hgt, strength, recv, fade=(0.18, 0.18), tol_deg=2.6,
                color=(0.95, 0.97, 1.0), group=None, power=1.0):
    """Card whose mirror image in the face plane (point face_c, normal face_n) is the band a -> b (world points on or
    near the face; they are projected onto it), half width wf (m). Placed hgt in front of the face, toward the camera.
    Strength fades in over fade[0] of the length from a and out over fade[1] at b. power > 1 narrows the bump's top."""
    n = Vector(face_n).normalized()
    c = Vector(face_c)
    cam = Vector(cam_loc)
    dc = (cam - c).dot(n)
    assert dc > 0, "the camera must be in front of the face"
    cp = cam - 2.0 * dc * n                       # the camera mirrored in the face plane
    A, B = Vector(a), Vector(b)
    A = A - (A - c).dot(n) * n
    B = B - (B - c).dot(n) * n
    d = (B - A).normalized()
    s = n.cross(d).normalized()
    k = 1.0 + hgt / dc

    def mp(p):
        return cp + (p - cp) * k

    corners = [A - s * wf, A + s * wf, B + s * wf, B - s * wf]
    pts = [mp(p) for p in corners]
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in pts], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name="UVMap")
    for li_, uv in zip(me.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uvl.data[li_.index].uv = uv
    me.update()
    if me.polygons[0].normal.dot(n) > 0:          # emit back toward the face
        me.flip_normals()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    for nd in list(nodes):
        nodes.remove(nd)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["UV"], sep.inputs["Vector"])
    # across: |2u - 1| -> smoothstep bump (1 at the centre line, 0 at the band's edges): a soft sweep
    c2 = _n(nodes, "ShaderNodeMath", "MULTIPLY_ADD")
    c2.inputs[1].default_value = 2.0
    c2.inputs[2].default_value = -1.0
    links.new(sep.outputs["X"], c2.inputs[0])
    ab = _n(nodes, "ShaderNodeMath", "ABSOLUTE")
    links.new(c2.outputs[0], ab.inputs[0])
    acr = _n(nodes, "ShaderNodeMapRange")
    acr.interpolation_type = "SMOOTHSTEP"
    acr.inputs["From Min"].default_value = 1.0
    acr.inputs["From Max"].default_value = 0.0
    links.new(ab.outputs[0], acr.inputs["Value"])
    prof = acr.outputs["Result"]
    if power != 1.0:
        pw = _n(nodes, "ShaderNodeMath", "POWER")
        pw.inputs[1].default_value = power
        links.new(prof, pw.inputs[0])
        prof = pw.outputs[0]
    a0 = _n(nodes, "ShaderNodeMapRange")
    a0.interpolation_type = "SMOOTHSTEP"
    a0.inputs["From Min"].default_value = 0.0
    a0.inputs["From Max"].default_value = max(1e-3, fade[0])
    links.new(sep.outputs["Y"], a0.inputs["Value"])
    a1 = _n(nodes, "ShaderNodeMapRange")
    a1.interpolation_type = "SMOOTHSTEP"
    a1.inputs["From Min"].default_value = 1.0
    a1.inputs["From Max"].default_value = 1.0 - max(1e-3, fade[1])
    links.new(sep.outputs["Y"], a1.inputs["Value"])
    m1 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(prof, m1.inputs[0])
    links.new(a0.outputs["Result"], m1.inputs[1])
    m2 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    links.new(m1.outputs[0], m2.inputs[0])
    links.new(a1.outputs["Result"], m2.inputs[1])
    if tol_deg and tol_deg > 0:
        # honeycomb: emit only toward the mirrored camera (the ray came from the face along the mirror path)
        geo = nodes.new("ShaderNodeNewGeometry")
        vsub = _n(nodes, "ShaderNodeVectorMath", "SUBTRACT")
        vsub.inputs[0].default_value = tuple(cp)
        links.new(geo.outputs["Position"], vsub.inputs[1])
        vn = _n(nodes, "ShaderNodeVectorMath", "NORMALIZE")
        links.new(vsub.outputs[0], vn.inputs[0])
        vd = _n(nodes, "ShaderNodeVectorMath", "DOT_PRODUCT")
        links.new(geo.outputs["Incoming"], vd.inputs[0])
        links.new(vn.outputs[0], vd.inputs[1])
        gr = _n(nodes, "ShaderNodeMapRange")
        gr.interpolation_type = "SMOOTHSTEP"
        gr.inputs["From Min"].default_value = math.cos(math.radians(tol_deg))
        gr.inputs["From Max"].default_value = math.cos(math.radians(tol_deg * 0.35))
        links.new(vd.outputs["Value"], gr.inputs["Value"])
        mg = _n(nodes, "ShaderNodeMath", "MULTIPLY")
        links.new(m2.outputs[0], mg.inputs[0])
        links.new(gr.outputs["Result"], mg.inputs[1])
        m2 = mg
    m3 = _n(nodes, "ShaderNodeMath", "MULTIPLY")
    m3.inputs[1].default_value = strength
    links.new(m2.outputs[0], m3.inputs[0])
    links.new(m3.outputs[0], em.inputs["Strength"])
    tr = nodes.new("ShaderNodeBsdfTransparent")
    add = nodes.new("ShaderNodeAddShader")
    links.new(em.outputs[0], add.inputs[0])
    links.new(tr.outputs[0], add.inputs[1])
    links.new(add.outputs[0], out.inputs["Surface"])
    me.materials.append(m)
    ob.visible_camera = False
    ob.visible_diffuse = False          # glossy only: never a diffuse wash on white
    ob.visible_shadow = False
    ob.visible_transmission = False
    ob.visible_volume_scatter = False
    coll = bpy.data.collections.new(name + "_recv")
    for o_ in recv:
        coll.objects.link(o_)
    ob.light_linking.receiver_collection = coll
    if group:
        ob.lightgroup = group
    return ob


def exclude(emitter, objs, name):
    """The emitter lights everything except objs."""
    coll = bpy.data.collections.new(name)
    for o_ in objs:
        coll.objects.link(o_)
    emitter.light_linking.receiver_collection = coll
    for co in coll.collection_objects:
        co.light_linking.link_state = "EXCLUDE"


def coll(name, objs):
    """A receiver collection that several emitters can share (Cycles allows 64 light-linking collections per scene)."""
    c = bpy.data.collections.new(name)
    for o_ in objs:
        c.objects.link(o_)
    return c


def exclusion(name, objs):
    """A shared receiver collection that EXCLUDES objs (the emitter lights everything else)."""
    c = coll(name, objs)
    for co in c.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    return c


def relink(emitter, c):
    """Point an emitter at a shared receiver collection; drop the private one a helper made for it, if now unused."""
    old = emitter.light_linking.receiver_collection
    emitter.light_linking.receiver_collection = c
    if old is not None and old != c and old.users == 0:
        bpy.data.collections.remove(old)
