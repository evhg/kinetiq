"""K16's drilled plate: K04's face patch with every hole drilled instead of moulded. install(K04) swaps K04's builders:

- build_patch    -> straight holes through the 38 mm slab, radius R (12.4 mm bore) plus a chipped, slightly ragged edge
                    (a few notches where the drill tore resin and tow out of the face), no meniscus, no lining.
                    'Lips' = the top 0.25 mm of each wall (the cut edge, its own object per hole, so K04's per-hole light
                    linking still works); 'Bores' = the rest of each wall, down through the core.
                    Fibre stubs: short bent tow ends standing off the cut edge (curve objects), the visible fray.
- carbon_white_baked -> the canon white twill on PLANAR coordinates (K04's white_sleeve recipe re-coordinated: u = x,
                    v = y, tangent +x): the tows run straight and stop dead at every rim (no warp round the holes), plus
                    a band of crazed, stress-whitened resin round each rim (coat broken, rougher, radial micro-cracks).
- white_sleeve   -> the drilled wall: the cut laminate skin (plies of cut tow ends, white fibre in resin, matte) over a
                    dark bond line and the EVA core exposed below it (foam cells), darkening with depth.
- bore_emission  -> nothing (no light comes up a foam wall).
"""
import inspect
import math
import random

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

FRAY_W = 0.0014      # stress-whitened band round each rim (m)
LIP_D = 0.00025       # the cut edge band ('Lips' objects), m below the face


def install(K04, skin=0.0016, chip=0.00012, seed=16):
    R, ZT, ZB, U = K04.R, K04.ZT, K04.ZB, K04.U
    rng = random.Random(seed)
    state = {"holes": []}

    def rim_fn(hero):
        """Radius of the cut edge at angle a: R plus chips (notches torn out by the drill) and a fine ragged noise."""
        notches = []
        for _ in range(9 if hero else 5):
            notches.append((rng.uniform(0, 2 * math.pi), rng.uniform(0.25, 1.0) * chip, math.radians(rng.uniform(1.5, 7))))
        ph = [rng.uniform(0, 6.283) for _ in range(4)]

        def r_at(a, depth):
            # chips go through the first ply or two only; the core wall is a clean drilled cylinder
            k = max(0.0, 1.0 - depth / max(skin * 0.6, 1e-6))
            c = 0.0
            for (a0, d0, w0) in notches:
                da = (a - a0 + math.pi) % (2 * math.pi) - math.pi
                c += d0 * math.exp(-(da / w0) ** 2)
            fine = 0.000012 * (math.sin(37 * a + ph[0]) + 0.6 * math.sin(91 * a + ph[1]) + 0.4 * math.sin(173 * a + ph[2]))
            return R + (c + fine) * k + 0.000004 * math.sin(11 * a + ph[3])
        return r_at

    def build_patch(centre_m, radius=0.075, seg_hero=768, seg_other=384):
        cx, cy = centre_m
        import racket
        hs = []
        for (hx, hy) in racket.holes():
            x, y = hx * U, hy * U
            if math.hypot(x - cx, y - cy) + R + 0.0016 < radius - 0.004:
                hs.append((x, y))
        state["holes"] = hs
        F = {"v": [], "n": [], "f": []}
        L = {"v": [], "n": [], "f": []}
        B = {"v": [], "n": [], "f": []}

        def add(D, p, n):
            D["v"].append(p)
            D["n"].append(n)
            return len(D["v"]) - 1

        # wall rows: dense at the top (the cut edge, the skin), sparse through the core
        rows = [0.0, 0.00004, 0.0001, 0.00018, LIP_D]
        z_ = LIP_D
        while z_ < skin + 0.0006:
            z_ += 0.0002
            rows.append(z_)
        for d in (0.003, 0.006, 0.010, 0.016, 0.024, 0.032, ZT - ZB):
            if d > rows[-1]:
                rows.append(d)
        top_loops, bot_loops = [], []
        for (x, y) in hs:
            hero = abs(x - cx) < 1e-6 and abs(y - cy) < 1e-6
            n = seg_hero if hero else seg_other
            r_at = rim_fn(hero)
            grids = {}
            for D, rr in ((L, [r for r in rows if r <= LIP_D + 1e-9]), (B, [r for r in rows if r >= LIP_D - 1e-9])):
                grid = []
                for depth in rr:
                    row = []
                    for j in range(n):
                        a = 2 * math.pi * j / n
                        r = r_at(a, depth)
                        row.append(add(D, (x + r * math.cos(a), y + r * math.sin(a), ZT - depth),
                                       (-math.cos(a), -math.sin(a), 0.0)))
                    grid.append(row)
                for k in range(len(grid) - 1):
                    for j in range(n):
                        j2 = (j + 1) % n
                        D["f"].append((grid[k][j], grid[k + 1][j], grid[k + 1][j2], grid[k][j2]))
                grids[id(D)] = grid
            top_loops.append([add(F, L["v"][i], (0, 0, 1)) for i in grids[id(L)][0]])
            bot_loops.append([add(F, B["v"][i], (0, 0, -1)) for i in grids[id(B)][-1]])
            if hero or math.hypot(x - cx, y - cy) < 0.03:
                stubs(x, y, r_at, hero)
        nout = 512
        ring = [(cx + radius * math.cos(2 * math.pi * j / nout), cy + radius * math.sin(2 * math.pi * j / nout))
                for j in range(nout)]
        otop = [add(F, (px, py, ZT), (0, 0, 1)) for (px, py) in ring]
        obot = [add(F, (px, py, ZB), (0, 0, -1)) for (px, py) in ring]
        wt = [add(F, (px, py, ZT), (px - cx, py - cy, 0)) for (px, py) in ring]
        wb = [add(F, (px, py, ZB), (px - cx, py - cy, 0)) for (px, py) in ring]
        for j in range(nout):
            j2 = (j + 1) % nout
            F["f"].append((wb[j], wb[j2], wt[j2], wt[j]))
        for loops, z in (([otop] + top_loops, ZT), ([obot] + bot_loops, ZB)):
            polys = [[Vector((F["v"][i][0], F["v"][i][1], 0)) for i in lp] for lp in loops]
            flat = [i for lp in loops for i in lp]
            for (a, b, c) in tessellate_polygon(polys):
                F["f"].append((flat[a], flat[b], flat[c]) if z > 0 else (flat[c], flat[b], flat[a]))
        face = K04._mesh_object("FacePatch", F["v"], F["n"], F["f"])
        lips = K04._mesh_object("Lips", L["v"], L["n"], L["f"])
        bpy.context.view_layer.objects.active = lips
        for o2 in bpy.context.selected_objects:
            o2.select_set(False)
        lips.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")
        lips = [o2 for o2 in bpy.context.scene.objects if o2.name.startswith("Lips")]
        bores = K04._mesh_object("Bores", B["v"], B["n"], B["f"])
        return face, lips, bores, hs

    def stubs(x, y, r_at, hero):
        """Tow ends standing off the cut: short, bent, white bundles (0.02-0.05 mm thick) from the edge and the skin."""
        cu = bpy.data.curves.new("Stubs", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 1.0
        cu.bevel_resolution = 1
        cu.use_fill_caps = True
        count = 90 if hero else 30
        for _ in range(count):
            a = rng.uniform(0, 2 * math.pi)
            depth = abs(rng.gauss(0, skin * 0.35))
            depth = min(depth, skin * 0.95)
            r0 = r_at(a, depth) - 0.00002
            ln = rng.uniform(0.00012, 0.0007) * (1.4 if depth < 0.0002 else 1.0)
            thick = rng.uniform(0.000010, 0.000028)
            rad = Vector((-math.cos(a), -math.sin(a), 0))
            tang = Vector((-math.sin(a), math.cos(a), 0))
            d = (rad * rng.uniform(0.6, 1.0) + tang * rng.uniform(-0.5, 0.5)
                 + Vector((0, 0, rng.uniform(-0.2, 0.6)))).normalized()
            bend = (tang * rng.uniform(-1, 1) + Vector((0, 0, rng.uniform(-1, 0.3)))).normalized()
            p0 = Vector((x + r0 * math.cos(a), y + r0 * math.sin(a), ZT - depth))
            sp = cu.splines.new("POLY")
            sp.points.add(3)
            for k in range(4):
                t = k / 3
                q = p0 + d * ln * t + bend * ln * 0.35 * t * t
                sp.points[k].co = (q.x, q.y, q.z, 1.0)
                sp.points[k].radius = thick * (1.0 - 0.55 * t) / 1.0
        ob = bpy.data.objects.new("Stubs", cu)
        bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(stub_mat())
        return ob

    _stub = {}

    def stub_mat():
        if "m" in _stub:
            return _stub["m"]
        m = bpy.data.materials.new("K16_Stub")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.62, 0.61, 0.58, 1)
        b.inputs["Roughness"].default_value = 0.45
        b.inputs["Coat Weight"].default_value = 0.0
        _stub["m"] = m
        return m

    # ---------------------------------------------------------------- the face: canon twill on planar coordinates
    src = inspect.getsource(K04.white_sleeve)
    src = src.replace("def white_sleeve(", "def planar_white(")
    src = src.replace('u = nb.math("MULTIPLY", th, rc)', 'u = sd.outputs["X"]')
    src = src.replace('v = nb.math("ADD", sa.outputs["Fac"], float(o.get("sleeve_v0", 0.0)))', 'v = sd.outputs["Y"]')
    src = src.replace('links.new(nz.outputs[0], b.inputs["Tangent"])',
                      '_tx = nodes.new("ShaderNodeCombineXYZ"); _tx.inputs["X"].default_value = 1.0; '
                      'links.new(_tx.outputs[0], b.inputs["Tangent"])')
    assert 'u = sd.outputs["X"]' in src and "_tx" in src
    ns = dict(K04.__dict__)
    exec(compile(src, "k16_planar_white", "exec"), ns)
    planar_white = ns["planar_white"]

    def carbon_white_baked(holes_m, o):
        m, _ = planar_white("K16_FacePlanar", o, bore=False)
        add_fray(m, state["holes"], o)
        return m

    def add_fray(m, holes, o):
        """Stress-whitened, crazed resin in a band round each rim: lighter, rougher, the coat broken, radial cracks."""
        nt = m.node_tree
        nodes, links = nt.nodes, nt.links
        b = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
        tc = nodes.new("ShaderNodeTexCoord")
        dmin = None
        for (hx, hy) in holes:
            d = nodes.new("ShaderNodeVectorMath")
            d.operation = "DISTANCE"
            d.inputs[1].default_value = (hx, hy, ZT)
            links.new(tc.outputs["Object"], d.inputs[0])
            if dmin is None:
                dmin = d.outputs["Value"]
            else:
                mn = nodes.new("ShaderNodeMath")
                mn.operation = "MINIMUM"
                links.new(dmin, mn.inputs[0])
                links.new(d.outputs["Value"], mn.inputs[1])
                dmin = mn.outputs[0]
        band = nodes.new("ShaderNodeMapRange")
        band.interpolation_type = "SMOOTHSTEP"
        band.inputs["From Min"].default_value = R + chip * 0.2
        band.inputs["From Max"].default_value = R + float(o.get("fray_w", FRAY_W))
        band.inputs["To Min"].default_value = 1.0
        band.inputs["To Max"].default_value = 0.0
        links.new(dmin, band.inputs["Value"])
        # radial micro-cracks: noise stretched along the radius (angle about the nearest hole ~ x, y direction)
        nz = nodes.new("ShaderNodeTexNoise")
        nz.noise_dimensions = "3D"
        nz.inputs["Scale"].default_value = 9000.0
        nz.inputs["Detail"].default_value = 6.0
        nz.inputs["Roughness"].default_value = 0.65
        links.new(tc.outputs["Object"], nz.inputs["Vector"])
        crack = nodes.new("ShaderNodeMapRange")
        crack.inputs["From Min"].default_value = 0.45
        crack.inputs["From Max"].default_value = 0.62
        links.new(nz.outputs["Fac"], crack.inputs["Value"])
        fr = nodes.new("ShaderNodeMath")
        fr.operation = "MULTIPLY"
        links.new(band.outputs["Result"], fr.inputs[0])
        links.new(crack.outputs["Result"], fr.inputs[1])
        fray = nodes.new("ShaderNodeMath")
        fray.operation = "MAXIMUM"
        links.new(fr.outputs[0], fray.inputs[0])
        bm_ = nodes.new("ShaderNodeMath")
        bm_.operation = "MULTIPLY"
        bm_.inputs[1].default_value = float(o.get("fray_base", 0.25))
        links.new(band.outputs["Result"], bm_.inputs[0])
        links.new(bm_.outputs[0], fray.inputs[1])
        # base colour: whiten toward a chalky resin white
        bc_src = b.inputs["Base Color"].links[0].from_socket
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["B"].default_value = tuple(float(v) for v in str(o.get("fray_col", "0.6,0.58,0.55")).split(",")) + (1.0,)
        links.new(fray.outputs[0], mix.inputs["Factor"])
        links.new(bc_src, mix.inputs["A"])
        links.new(mix.outputs["Result"], b.inputs["Base Color"])
        # roughness up, coat broken
        r_src = b.inputs["Roughness"].links[0].from_socket
        rm = nodes.new("ShaderNodeMix")
        rm.data_type = "FLOAT"
        rm.inputs["B"].default_value = 0.75
        links.new(fray.outputs[0], rm.inputs["Factor"])
        links.new(r_src, rm.inputs["A"])
        links.new(rm.outputs["Result"], b.inputs["Roughness"])
        cw = nodes.new("ShaderNodeMath")
        cw.operation = "MULTIPLY_ADD"
        cw.inputs[1].default_value = -0.9
        cw.inputs[2].default_value = 1.0
        links.new(fray.outputs[0], cw.inputs[0])
        links.new(cw.outputs[0], b.inputs["Coat Weight"])

    # ---------------------------------------------------------------- the drilled wall
    def white_sleeve(name, o, bore=False):
        m = bpy.data.materials.new(name.replace("CarbonW_K04", "K16_Drilled"))
        m.use_nodes = True
        nt = m.node_tree
        nodes, links = nt.nodes, nt.links
        b = nodes["Principled BSDF"]
        tc = nodes.new("ShaderNodeTexCoord")
        sp = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tc.outputs["Object"], sp.inputs["Vector"])

        def math_(op, a, bb=None, cc_=None):
            n = nodes.new("ShaderNodeMath")
            n.operation = op
            for i, v in enumerate((a, bb, cc_)):
                if v is None:
                    continue
                if isinstance(v, (int, float)):
                    n.inputs[i].default_value = v
                else:
                    links.new(v, n.inputs[i])
            return n.outputs[0]

        def ramp(v, a, bb, lo=0.0, hi=1.0, smooth=True):
            n = nodes.new("ShaderNodeMapRange")
            if smooth:
                n.interpolation_type = "SMOOTHSTEP"
            n.inputs["From Min"].default_value = a
            n.inputs["From Max"].default_value = bb
            n.inputs["To Min"].default_value = lo
            n.inputs["To Max"].default_value = hi
            links.new(v, n.inputs["Value"])
            return n.outputs["Result"]

        depth = math_("SUBTRACT", ZT, sp.outputs["Z"])
        in_core = ramp(depth, skin - 0.00004, skin + 0.00004)
        # skin: plies 0.2 mm thick, alternating: one shows cut tow ends (speckle), the next the tows lying along the
        # wall (streaks round the hole); white fibre in amber-clear resin, matte (a cut, not a moulded surface)
        ply = math_("FRACT", math_("DIVIDE", depth, 0.0004))
        ply_a = ramp(ply, 0.46, 0.54)
        vor = nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 1.0 / 0.000045
        links.new(tc.outputs["Object"], vor.inputs["Vector"])
        dots = ramp(vor.outputs["Distance"], 0.12, 0.5, 1.25, 0.45)
        nz = nodes.new("ShaderNodeTexNoise")
        nz.noise_dimensions = "3D"
        mp = nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1 / 0.00006, 1 / 0.00006, 1 / 0.000012)
        links.new(tc.outputs["Object"], mp.inputs["Vector"])
        links.new(mp.outputs[0], nz.inputs["Vector"])
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = 3.0
        streaks = ramp(nz.outputs["Fac"], 0.35, 0.7, 0.6, 1.0)
        skin_tone = nodes.new("ShaderNodeMix")
        skin_tone.data_type = "FLOAT"
        links.new(ply_a, skin_tone.inputs["Factor"])
        links.new(dots, skin_tone.inputs["A"])
        links.new(streaks, skin_tone.inputs["B"])
        skin_v = math_("MULTIPLY", skin_tone.outputs["Result"], float(o.get("skin_tone", 0.62)))
        # resin lines between plies
        resin = ramp(math_("ABSOLUTE", math_("SUBTRACT", ply, 0.5)), 0.44, 0.5, 1.0, 0.55)
        skin_v = math_("MULTIPLY", skin_v, resin)
        # bond line at the skin's foot, then the EVA core: open foam cells, a soft grey with a whisper of warmth
        bond = ramp(math_("ABSOLUTE", math_("SUBTRACT", depth, skin)), 0.00002, 0.00007, 0.12, 1.0)
        cells = nodes.new("ShaderNodeTexVoronoi")
        cells.feature = "DISTANCE_TO_EDGE"
        cells.inputs["Scale"].default_value = 1.0 / float(o.get("cell", 0.00022))
        links.new(tc.outputs["Object"], cells.inputs["Vector"])
        cell_wall = ramp(cells.outputs["Distance"], 0.0, 0.12, 1.0, 0.0)
        core_v = math_("MULTIPLY_ADD", cell_wall, 0.12, float(o.get("core_tone", 0.2)))
        tone = nodes.new("ShaderNodeMix")
        tone.data_type = "FLOAT"
        links.new(in_core, tone.inputs["Factor"])
        links.new(skin_v, tone.inputs["A"])
        links.new(core_v, tone.inputs["B"])
        t = math_("MULTIPLY", tone.outputs["Result"], bond)
        # depth occlusion: the hole still reads as a hole (graphite by about 5 mm)
        occ = ramp(depth, skin + 0.0002, float(o.get("drill_dark", 0.0035)), 1.0, 0.06)
        t = math_("MULTIPLY", t, occ)
        cc = nodes.new("ShaderNodeCombineColor")
        core_tint = (0.98, 0.97, 0.94)
        skin_tint = (0.97, 0.96, 0.92)
        for i in range(3):
            tint = nodes.new("ShaderNodeMix")
            tint.data_type = "FLOAT"
            links.new(in_core, tint.inputs["Factor"])
            tint.inputs["A"].default_value = skin_tint[i]
            tint.inputs["B"].default_value = core_tint[i]
            links.new(math_("MULTIPLY", t, tint.outputs["Result"]), cc.inputs[i])
        links.new(cc.outputs[0], b.inputs["Base Color"])
        rgh = nodes.new("ShaderNodeMix")
        rgh.data_type = "FLOAT"
        links.new(in_core, rgh.inputs["Factor"])
        rgh.inputs["A"].default_value = 0.5
        rgh.inputs["B"].default_value = 0.85
        links.new(rgh.outputs["Result"], b.inputs["Roughness"])
        b.inputs["Coat Weight"].default_value = 0.0
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.6
        bump.inputs["Distance"].default_value = 0.00003
        h = nodes.new("ShaderNodeMix")
        h.data_type = "FLOAT"
        links.new(in_core, h.inputs["Factor"])
        links.new(dots, h.inputs["A"])
        links.new(math_("SUBTRACT", 1.0, cell_wall), h.inputs["B"])
        links.new(h.outputs["Result"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], b.inputs["Normal"])
        return m, dots

    def bore_emission(mat, stria_sock, hero_xy, o, left_x=0.32):
        return None

    K04.build_patch = build_patch
    K04.carbon_white_baked = carbon_white_baked
    K04.white_sleeve = white_sleeve
    K04.bore_emission = bore_emission
