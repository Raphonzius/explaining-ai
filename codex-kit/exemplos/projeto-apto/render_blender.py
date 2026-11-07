#!/usr/bin/env python3
"""Etapas 3 e 4 do pipeline: planta mobiliada -> modelo 3D (validação) -> render com Cycles.

Lê planta-base.json + saida/layout.json (gerado por apto.py) e monta o apartamento
no Blender, só com código: paredes com vãos, pisos, esquadrias, móveis por partes,
materiais procedurais e luz. Não depende de nenhum arquivo 3D externo.

Duas formas de rodar (escolha uma):
  a) Blender instalado:  blender -b -P render_blender.py -- --vista sala --qualidade final
  b) Python + módulo:    pip install bpy numpy   (Blender como biblioteca)
                         python render_blender.py --vista sala --qualidade final

Vistas:     aerea (corte "casa de boneca"), topo (vista de cima), sala, cozinha, suite
Qualidade:  rapida (validação, ~20 amostras)  |  final (Cycles + denoise, ~160 amostras)
Saída em saida/validacao/ (rápida) ou saida/render/ (final). Dados fictícios.
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

AQUI = Path(__file__).parent
PLANTA = json.loads((AQUI / "planta-base.json").read_text(encoding="utf-8"))
LAYOUT = json.loads((AQUI / "saida" / "layout.json").read_text(encoding="utf-8"))
H = PLANTA["pe_direito"]


# ============================================================ utilidades
def hexa(h, s=1.0):
    h = h.lstrip("#")
    lin = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
    return (lin(int(h[0:2], 16)) * s, lin(int(h[2:4], 16)) * s, lin(int(h[4:6], 16)) * s, 1.0)


MATS = {}
COL = None


def mat(nome, cor="#cccccc", rough=0.6, metal=0.0, **kw):
    """Material Principled simples. kw: sheen, coat, emissao(cor, forca), transm, ior, alpha."""
    if nome in MATS:
        return MATS[nome]
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexa(cor)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "sheen" in kw:
        b.inputs["Sheen Weight"].default_value = kw["sheen"]
        b.inputs["Sheen Roughness"].default_value = 0.5
    if "coat" in kw:
        b.inputs["Coat Weight"].default_value = kw["coat"]
    if "emissao" in kw:
        b.inputs["Emission Color"].default_value = hexa(kw["emissao"][0])
        b.inputs["Emission Strength"].default_value = kw["emissao"][1]
    if "transm" in kw:
        b.inputs["Transmission Weight"].default_value = kw["transm"]
        b.inputs["IOR"].default_value = 1.45
    MATS[nome] = m
    return m


def mat_planks(nome, c1, c2, larg, alt, argamassa=0.004, rough=0.45, bump=0.25, grao=True):
    """Piso em réguas/placas: textura Brick (procedural) + veio de madeira."""
    if nome in MATS:
        return MATS[nome]
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5 if grao else 0.0
    br.offset_frequency = 2
    br.inputs["Color1"].default_value = hexa(c1)
    br.inputs["Color2"].default_value = hexa(c2)
    br.inputs["Mortar"].default_value = (0.06, 0.05, 0.04, 1)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = argamassa
    br.inputs["Mortar Smooth"].default_value = 0.1
    br.inputs["Bias"].default_value = 0.0
    br.inputs["Brick Width"].default_value = larg
    br.inputs["Row Height"].default_value = alt
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    cor = br.outputs["Color"]
    if grao:
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (2.0, 70.0, 2.0)
        ns = nt.nodes.new("ShaderNodeTexNoise")
        ns.inputs["Scale"].default_value = 3.0
        ns.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], ns.inputs["Vector"])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        mx.blend_type = "MULTIPLY"
        mx.inputs[0].default_value = 0.35
        nt.links.new(br.outputs["Color"], mx.inputs[6])
        nt.links.new(ns.outputs["Color"], mx.inputs[7])
        cor = mx.outputs[2]
    nt.links.new(cor, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.002
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    MATS[nome] = m
    return m


def mat_vidro(nome="vidro"):
    if nome in MATS:
        return MATS[nome]
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    g = nt.nodes.new("ShaderNodeBsdfGlass")
    g.inputs["Roughness"].default_value = 0.0
    g.inputs["IOR"].default_value = 1.05
    g.inputs["Color"].default_value = (0.9, 0.97, 1.0, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mix.inputs[0])
    nt.links.new(g.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    MATS[nome] = m
    return m


def paleta():
    return dict(
        tinta=mat("tinta", "#f1eee8", 0.92),
        teto=mat("teto", "#f7f5f1", 0.95),
        concreto=mat("concreto", "#b9b5ad", 0.9),
        chao_externo=mat("chao_externo", "#8f9a80", 0.95),
        madeira=mat("madeira", "#c79f6e", 0.42),
        madeira_clara=mat("madeira_clara", "#dcbf92", 0.45),
        madeira_esc=mat("madeira_esc", "#6b4a31", 0.45),
        branco=mat("branco", "#f4f3ef", 0.5),
        preto=mat("preto", "#1d2024", 0.4),
        tv=mat("tv", "#07080a", 0.12, coat=0.5),
        latao=mat("latao", "#c9a24d", 0.28, 1.0),
        inox=mat("inox", "#c4c8cc", 0.28, 1.0),
        cromo=mat("cromo", "#d9dde0", 0.1, 1.0),
        salvia=mat("salvia", "#a7b596", 0.88, sheen=0.4),
        salvia_esc=mat("salvia_esc", "#7f9272", 0.9, sheen=0.4),
        greige=mat("greige", "#cfc5b4", 0.92, sheen=0.4),
        terracota=mat("terracota", "#c9805f", 0.8, sheen=0.5),
        linho=mat("linho", "#e6dcc9", 0.95, sheen=0.3),
        tapete=mat("tapete", "#eadfcb", 1.0, sheen=0.6),
        quartzo=mat("quartzo", "#f3f2ee", 0.22, coat=0.3),
        armario=mat("armario", "#a7b79a", 0.4, coat=0.15),
        ceramica=mat("ceramica", "#fbfaf8", 0.12, coat=0.6),
        folha=mat("folha", "#4f7a43", 0.55),
        folha2=mat("folha2", "#6b9a56", 0.55),
        vaso_terra=mat("vaso_terra", "#c98f6b", 0.8),
        cinza_tec=mat("cinza_tec", "#5d666d", 0.9, sheen=0.3),
        espelho=mat("espelho", "#c9d2d8", 0.02, 1.0),
        luz_quente=mat("luz_quente", "#ffd9a0", 1.0, emissao=("#ffcf8a", 12.0)),
        luz_fraca=mat("luz_fraca", "#ffe3b8", 1.0, emissao=("#ffd9a0", 5.0)),
        vidro=mat_vidro(),
        piso_madeira=mat_planks("piso_madeira", "#c79f6c", "#b98f5d", 1.2, 0.16, 0.003, 0.4),
        piso_tile=mat_planks("piso_tile", "#e4e5e2", "#d8dad8", 0.6, 0.6, 0.006, 0.25, 0.4, grao=False),
        piso_deck=mat_planks("piso_deck", "#9b6c46", "#8c5f3c", 1.8, 0.14, 0.005, 0.55),
    )


def novo_obj(nome, bm, material, pai=None):
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    COL.objects.link(ob)
    if material:
        ob.data.materials.append(material)
    if pai:
        ob.parent = pai
    return ob


def caixa(pai, x0, y0, z0, x1, y1, z1, material, bev=0.0, rz=0.0, rx=0.0, nome="caixa"):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (v.co.x + 0.5) * (x1 - x0) + x0
        v.co.y = (v.co.y + 0.5) * (y1 - y0) + y0
        v.co.z = (v.co.z + 0.5) * (z1 - z0) + z0
    ob = novo_obj(nome, bm, material, pai)
    if rz or rx:
        c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        ob.rotation_euler = (math.radians(rx), 0, math.radians(rz))
        ob.location = c - ob.rotation_euler.to_matrix() @ c
    if bev > 0:
        md = ob.modifiers.new("b", "BEVEL")
        md.width = bev
        md.segments = 3
        md.harden_normals = True
        md.limit_method = "ANGLE"
        ob.data.shade_smooth()
    return ob


def cilindro(pai, x, y, z0, z1, r, material, r2=None, seg=32, nome="cil"):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=(z1 - z0))
    for v in bm.verts:
        v.co.x += x
        v.co.y += y
        v.co.z += (z0 + z1) / 2
    for f in bm.faces:
        f.smooth = True
    return novo_obj(nome, bm, material, pai)


def esfera(pai, x, y, z, r, material, esc=(1, 1, 1), rot=(0, 0, 0), seg=24, nome="esf"):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r)
    for v in bm.verts:
        v.co.x *= esc[0]
        v.co.y *= esc[1]
        v.co.z *= esc[2]
    for f in bm.faces:
        f.smooth = True
    ob = novo_obj(nome, bm, material, pai)
    ob.location = (x, y, z)
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    return ob


# ============================================================ móveis (coordenadas locais: frente = +y, costas = -y)
def pernas(P, pai, x0, y0, x1, y1, h, mt, esp=0.04, inset=0.0):
    for (x, y) in [(x0 + inset, y0 + inset), (x1 - inset - esp, y0 + inset), (x0 + inset, y1 - inset - esp), (x1 - inset - esp, y1 - inset - esp)]:
        caixa(pai, x, y, 0, x + esp, y + esp, h, mt, 0.004)


def sofa(P, o, w, d, assentos, tecido, almofadas=True):
    hw, hd = w / 2, d / 2
    for x in (-hw + 0.07, hw - 0.07):
        for y in (-hd + 0.07, hd - 0.07):
            cilindro(o, x, y, 0, 0.11, 0.022, P["latao"], r2=0.016, seg=12)
    caixa(o, -hw, -hd, 0.11, hw, hd, 0.4, tecido, 0.03)
    for s in (-1, 1):
        caixa(o, s * (hw - 0.09) - 0.09, -hd, 0.11, s * (hw - 0.09) + 0.09, hd, 0.62, tecido, 0.045)
    iw = (w - 0.36) / assentos
    for i in range(assentos):
        x0 = -hw + 0.18 + i * iw + 0.004
        caixa(o, x0, -hd + 0.22, 0.4, x0 + iw - 0.008, hd - 0.01, 0.56, tecido, 0.055)
        caixa(o, x0, -hd + 0.02, 0.5, x0 + iw - 0.008, -hd + 0.26, 0.86, tecido, 0.06, rx=-8)
    if almofadas:
        caixa(o, -hw + 0.24, -hd + 0.25, 0.54, -hw + 0.64, -hd + 0.36, 0.9, P["terracota"], 0.045, rz=12, rx=-12)
        caixa(o, hw - 0.62, -hd + 0.25, 0.54, hw - 0.24, -hd + 0.36, 0.88, P["linho"], 0.045, rz=-10, rx=-12)


def poltrona(P, o, w, d, tecido, pernas_mt):
    hw, hd = w / 2, d / 2
    for x in (-hw + 0.1, hw - 0.1):
        for y in (-hd + 0.1, hd - 0.1):
            cilindro(o, x, y, 0, 0.2, 0.02, pernas_mt, r2=0.014, seg=12)
    caixa(o, -hw, -hd, 0.2, hw, hd, 0.42, tecido, 0.04)
    caixa(o, -hw + 0.1, -hd + 0.2, 0.42, hw - 0.1, hd - 0.02, 0.55, tecido, 0.06)
    caixa(o, -hw, -hd, 0.3, hw, -hd + 0.2, 0.88, tecido, 0.07, rx=-6)
    for s in (-1, 1):
        caixa(o, s * (hw - 0.05) - 0.05, -hd + 0.08, 0.3, s * (hw - 0.05) + 0.05, hd, 0.62, tecido, 0.04)


def planta(P, o, h, r=0.18):
    cilindro(o, 0, 0, 0, 0.34, r, P["vaso_terra"], r2=r * 0.78, seg=24)
    cilindro(o, 0, 0, 0.33, 0.345, r * 0.9, mat("terra", "#3b2a20", 1.0), seg=24)
    n = 11
    for i in range(n):
        a = i * (360 / n) + (i % 3) * 9
        inc = 18 + (i % 4) * 11
        alt = h * (0.62 + (i % 5) * 0.08)
        L = 0.3 + (i % 3) * 0.07
        rr = 0.07 + 0.05 * (i % 2)
        mt = P["folha"] if i % 2 == 0 else P["folha2"]
        dx, dy = math.cos(math.radians(a)) * 0.09, math.sin(math.radians(a)) * 0.09
        esfera(o, dx, dy, alt - 0.25 + 0.3, 0.1, mt, esc=(0.55, 0.12, 1.6 + (i % 3) * 0.3), rot=(inc, 0, a + 90), seg=12)


def build_movel(P, mv):
    t, w, d, h, z = mv["tipo"], mv["w"], mv["d"], mv["h"], mv["z"]
    hw, hd = w / 2, d / 2
    o = bpy.data.objects.new(mv["id"], None)
    COL.objects.link(o)
    o.location = (mv["cx"], mv["cy"], z)
    o.rotation_euler = (0, 0, math.radians(mv["rot"]))
    if t == "tapete":
        caixa(o, -hw, -hd, 0, hw, hd, 0.018, P["tapete"], 0.006)
        caixa(o, -hw + 0.12, -hd + 0.12, 0.018, hw - 0.12, hd - 0.12, 0.021, P["linho"], 0.003)
    elif t == "sofa3":
        sofa(P, o, w, d, 3, P["greige"])
    elif t == "sofa_cama":
        sofa(P, o, w, d, 2, P["cinza_tec"], almofadas=False)
        caixa(o, -hw + 0.3, -hd + 0.3, 0.55, hw - 0.3, hd - 0.1, 0.6, P["salvia"], 0.03, rz=4)
    elif t == "poltrona":
        poltrona(P, o, w, d, P["terracota"], P["latao"])
    elif t == "poltrona_varanda":
        poltrona(P, o, w, d, P["linho"], P["madeira_esc"])
        caixa(o, -hw, -hd, 0.08, hw, -hd + 0.04, 0.9, P["madeira_clara"], 0.01)
    elif t == "cadeira_office":
        cilindro(o, 0, 0, 0.3, 0.46, 0.03, P["preto"], seg=12)
        for k in range(5):
            a = k * 72
            caixa(o, 0, -0.012, 0.04, 0.26, 0.012, 0.08, P["preto"], 0.005, rz=a)
        caixa(o, -0.26, -0.26, 0.46, 0.26, 0.26, 0.52, P["cinza_tec"], 0.04)
        caixa(o, -0.24, -0.27, 0.52, 0.24, -0.22, 0.95, P["cinza_tec"], 0.04, rx=-6)
    elif t == "cadeira_jantar":
        for (x, y) in [(-hw + 0.03, -hd + 0.03), (hw - 0.03, -hd + 0.03), (-hw + 0.03, hd - 0.03), (hw - 0.03, hd - 0.03)]:
            cilindro(o, x, y, 0, 0.45, 0.017, P["madeira"], r2=0.012, seg=10)
        caixa(o, -hw, -hd, 0.43, hw, hd, 0.47, P["madeira"], 0.01)
        caixa(o, -hw + 0.01, -hd, 0.47, hw - 0.01, -hd + 0.04, 0.92, P["madeira"], 0.015, rx=-6)
        caixa(o, -hw + 0.03, -hd + 0.03, 0.47, hw - 0.03, hd - 0.03, 0.495, P["linho"], 0.01)
    elif t == "banqueta":
        for a in (45, 135, 225, 315):
            dx, dy = math.cos(math.radians(a)) * 0.11, math.sin(math.radians(a)) * 0.11
            cilindro(o, dx, dy, 0, 0.62, 0.012, P["latao"], seg=8)
        cilindro(o, 0, 0, 0.62, 0.66, 0.19, P["madeira"], seg=32)
        cilindro(o, 0, 0, 0.66, 0.68, 0.17, P["linho"], seg=32)
        cilindro(o, 0, 0, 0.22, 0.235, 0.14, P["latao"], seg=24)
    elif t == "mesa_jantar":
        caixa(o, -hw, -hd, 0.71, hw, hd, 0.75, P["madeira_clara"], 0.012)
        for (x, y) in [(-hw + 0.08, -hd + 0.12), (hw - 0.08, -hd + 0.12), (-hw + 0.08, hd - 0.12), (hw - 0.08, hd - 0.12)]:
            caixa(o, x - 0.035, y - 0.035, 0, x + 0.035, y + 0.035, 0.71, P["madeira_clara"], 0.006)
        cilindro(o, 0, 0.15, 0.75, 0.83, 0.07, P["ceramica"], r2=0.05, seg=24)
        esfera(o, 0, 0.15, 0.93, 0.12, P["folha2"], esc=(1, 1, 1.2), seg=12)
        caixa(o, -0.12, -0.3, 0.75, 0.12, -0.15, 0.78, P["salvia_esc"], 0.01, rz=15)
    elif t == "mesa_centro":
        caixa(o, -hw, -hd, 0.32, hw, hd, 0.37, P["madeira_clara"], 0.012)
        caixa(o, -hw + 0.04, -hd + 0.04, 0.0, -hw + 0.08, hd - 0.04, 0.32, P["latao"], 0.004)
        caixa(o, hw - 0.08, -hd + 0.04, 0.0, hw - 0.04, hd - 0.04, 0.32, P["latao"], 0.004)
        caixa(o, -0.15, -0.3, 0.37, 0.12, -0.12, 0.4, P["terracota"], 0.008, rz=10)
        caixa(o, -0.12, -0.28, 0.4, 0.1, -0.14, 0.42, P["branco"], 0.006, rz=-6)
        cilindro(o, 0.02, 0.28, 0.37, 0.52, 0.06, P["ceramica"], r2=0.045, seg=20)
    elif t == "mesa_apoio_sala":
        cilindro(o, 0, 0, 0.0, 0.46, 0.012, P["latao"], seg=10)
        cilindro(o, 0, 0, 0.46, 0.5, 0.22, P["madeira"], seg=32)
        cilindro(o, 0, 0, 0.0, 0.015, 0.16, P["latao"], seg=24)
    elif t == "mesa_apoio":
        cilindro(o, 0, 0, 0.0, 0.42, 0.015, P["madeira_esc"], seg=10)
        cilindro(o, 0, 0, 0.42, 0.45, 0.3, P["madeira_clara"], seg=32)
        cilindro(o, 0.05, 0.03, 0.45, 0.5, 0.045, P["ceramica"], seg=16)
    elif t == "rack_tv":
        caixa(o, -hw, -hd, 0.12, hw, hd, 0.45, P["madeira_clara"], 0.012)
        for x in (-hw + 0.1, hw - 0.1):
            caixa(o, x - 0.02, -hd + 0.05, 0, x + 0.02, -hd + 0.09, 0.12, P["preto"], 0.004)
            caixa(o, x - 0.02, hd - 0.09, 0, x + 0.02, hd - 0.05, 0.12, P["preto"], 0.004)
        n = 4
        for i in range(n):
            x0 = -hw + 0.02 + i * (w - 0.04) / n
            caixa(o, x0 + 0.004, hd - 0.004, 0.14, x0 + (w - 0.04) / n - 0.004, hd + 0.008, 0.43, P["madeira"] if i % 2 else P["madeira_clara"], 0.006)
        caixa(o, -0.6, -0.12, 0.45, -0.38, 0.1, 0.62, P["terracota"], 0.01, rz=0)
        cilindro(o, 0.7, 0.0, 0.45, 0.66, 0.055, P["ceramica"], r2=0.04, seg=20)
        esfera(o, 0.7, 0.0, 0.72, 0.09, P["folha"], esc=(1, 1, 1.2), seg=12)
    elif t == "tv":
        caixa(o, -hw, -hd, 0.0, hw, hd, h, P["tv"], 0.008)
        caixa(o, -hw + 0.01, hd - 0.002, 0.01, hw - 0.01, hd + 0.001, h - 0.01, P["tv"], 0.0)
    elif t == "luminaria_piso":
        cilindro(o, 0, 0, 0, 0.02, 0.13, P["preto"], seg=24)
        cilindro(o, 0, 0, 0.02, 1.45, 0.009, P["latao"], seg=8)
        cilindro(o, 0, 0, 1.28, 1.6, 0.19, P["luz_fraca"], r2=0.13, seg=32)
    elif t == "planta":
        planta(P, o, h, r=0.19 if h > 1.05 else 0.16)
    elif t == "cama_queen":
        caixa(o, -hw, -hd, 0.1, hw, hd, 0.34, P["madeira_clara"], 0.02)
        for x in (-hw + 0.05, hw - 0.1):
            for y in (-hd + 0.05, hd - 0.1):
                caixa(o, x, y, 0, x + 0.05, y + 0.05, 0.1, P["madeira_esc"], 0.004)
        caixa(o, -hw - 0.08, -hd, 0.12, hw + 0.08, -hd + 0.09, 1.1, P["salvia_esc"], 0.05)
        caixa(o, -hw + 0.02, -hd + 0.09, 0.34, hw - 0.02, hd - 0.02, 0.56, P["branco"], 0.07)
        caixa(o, -hw + 0.01, -hd + 0.75, 0.5, hw - 0.01, hd + 0.02, 0.6, P["salvia"], 0.06)
        caixa(o, -hw + 0.01, -hd + 0.7, 0.55, hw - 0.01, -hd + 0.82, 0.63, P["linho"], 0.04)
        for sx in (-1, 1):
            caixa(o, sx * 0.4 - 0.33, -hd + 0.15, 0.56, sx * 0.4 + 0.33, -hd + 0.55, 0.7, P["branco"], 0.07, rx=-14, rz=sx * 3)
        caixa(o, -0.28, -hd + 0.55, 0.58, 0.28, -hd + 0.75, 0.74, P["terracota"], 0.06, rx=-10)
    elif t == "criado":
        caixa(o, -hw, -hd, 0.12, hw, hd, 0.5, P["madeira"], 0.012)
        for x in (-hw + 0.04, hw - 0.06):
            for y in (-hd + 0.04, hd - 0.06):
                cilindro(o, x + 0.01, y + 0.01, 0, 0.12, 0.014, P["madeira_esc"], seg=8)
        caixa(o, -hw + 0.03, hd - 0.003, 0.34, hw - 0.03, hd + 0.01, 0.48, P["madeira_clara"], 0.004)
        caixa(o, -0.05, hd + 0.005, 0.4, 0.05, hd + 0.025, 0.42, P["latao"], 0.004)
        cilindro(o, -0.05, -0.02, 0.5, 0.52, 0.09, P["latao"], seg=24)
        cilindro(o, -0.05, -0.02, 0.52, 0.8, 0.012, P["latao"], seg=8)
        cilindro(o, -0.05, -0.02, 0.62, 0.84, 0.12, P["luz_fraca"], r2=0.08, seg=24)
    elif t == "guarda_roupa":
        caixa(o, -hw, -hd, 0.0, hw, hd, h, P["branco"], 0.008)
        n = 6
        for i in range(n):
            x0 = -hw + i * w / n
            caixa(o, x0 + 0.006, hd - 0.004, 0.04, x0 + w / n - 0.006, hd + 0.014, h - 0.04, P["madeira_clara"] if i % 2 == 0 else P["madeira"], 0.006)
            caixa(o, x0 + w / n - 0.07, hd + 0.012, 1.0, x0 + w / n - 0.055, hd + 0.03, 1.3, P["latao"], 0.003)
    elif t == "banco_cama":
        pernas(P, o, -hw, -hd, hw, hd, 0.2, P["latao"], 0.03, 0.03)
        caixa(o, -hw, -hd, 0.2, hw, hd, 0.44, P["salvia"], 0.05)
    elif t == "vaso":
        caixa(o, -0.17, -hd, 0.45, 0.17, -hd + 0.2, 0.85, P["ceramica"], 0.03)
        esfera(o, 0, -hd + 0.38, 0.22, 0.2, P["ceramica"], esc=(0.9, 1.35, 0.9), seg=24)
        cilindro(o, 0, -hd + 0.38, 0.38, 0.41, 0.18, P["ceramica"], seg=32)
        cilindro(o, 0, -hd + 0.07, 0.85, 0.87, 0.03, P["cromo"], seg=16)
    elif t == "box":
        caixa(o, -hw, -hd, 0, hw, hd, 0.05, mat("box_base", "#d7dadc", 0.3), 0.01)
        caixa(o, -hw, hd - 0.01, 0.05, hw, hd, h, P["vidro"], 0.0)
        caixa(o, hw - 0.01, -hd, 0.05, hw, hd, h, P["vidro"], 0.0)
        caixa(o, -hw, hd - 0.02, h - 0.03, hw, hd, h, P["cromo"], 0.004)
        caixa(o, hw - 0.02, -hd, h - 0.03, hw, hd, h, P["cromo"], 0.004)
        cilindro(o, -hw + 0.12, -hd + 0.08, 1.9, 2.2, 0.012, P["cromo"], seg=8)
        cilindro(o, -hw + 0.12, -hd + 0.08, 2.1, 2.14, 0.09, P["cromo"], seg=24)
    elif t == "lavatorio":
        caixa(o, -hw, -hd, 0.2, hw, hd, 0.8, P["madeira"], 0.012)
        caixa(o, -hw - 0.01, -hd - 0.01, 0.8, hw + 0.01, hd + 0.01, 0.84, P["quartzo"], 0.01)
        cilindro(o, 0, 0.02, 0.84, 0.87, 0.19, P["ceramica"], r2=0.17, seg=32)
        cilindro(o, 0, -hd + 0.06, 0.84, 1.0, 0.012, P["latao"], seg=8)
        caixa(o, -hw + 0.1, -hd, 1.1, hw - 0.1, -hd + 0.015, 1.95, P["espelho"], 0.0)
        for i in range(2):
            caixa(o, -hw + 0.04 + i * (w - 0.08) / 2 + 0.003, hd - 0.003, 0.24, -hw + 0.04 + (i + 1) * (w - 0.08) / 2 - 0.003, hd + 0.008, 0.78, P["madeira_clara"], 0.004)
    elif t == "geladeira":
        caixa(o, -hw, -hd, 0.03, hw, hd, h, P["inox"], 0.02)
        caixa(o, -hw + 0.01, hd - 0.003, 0.03, hw - 0.01, hd + 0.003, 0.72, P["inox"], 0.0)
        caixa(o, -hw + 0.07, hd + 0.003, 0.4, -hw + 0.09, hd + 0.04, 0.7, P["cromo"], 0.005)
        caixa(o, -hw + 0.07, hd + 0.003, 0.9, -hw + 0.09, hd + 0.04, 1.5, P["cromo"], 0.005)
        caixa(o, -hw + 0.0, hd + 0.0, 0.745, hw, hd + 0.004, 0.755, P["preto"], 0.0)
    elif t == "bancada":
        n = 6
        for i in range(n):
            x0 = -hw + i * w / n
            caixa(o, x0 + 0.003, -hd, 0.1, x0 + w / n - 0.003, hd, 0.86, P["armario"] if i % 2 == 0 else P["armario"], 0.012)
            caixa(o, x0 + w / n - 0.09, hd + 0.001, 0.62, x0 + w / n - 0.07, hd + 0.025, 0.8, P["latao"], 0.003)
        caixa(o, -hw, -hd, 0.0, hw, hd - 0.04, 0.1, P["preto"], 0.0)
        caixa(o, -hw - 0.005, -hd, 0.86, hw + 0.005, hd + 0.025, 0.9, P["quartzo"], 0.008)
        ck = mv["cooktop_x"] - mv["cx"]
        caixa(o, ck - 0.3, -0.24, 0.9, ck + 0.3, 0.24, 0.903, P["preto"], 0.004)
        for dx in (-0.12, 0.12):
            for dy in (-0.09, 0.09):
                cilindro(o, ck + dx, dy, 0.903, 0.907, 0.05, P["luz_fraca" if False else "inox"], seg=20)
        px = mv["pia_x"] - mv["cx"]
        caixa(o, px - 0.34, -0.2, 0.86, px + 0.34, 0.2, 0.905, mat("pia", "#9aa1a6", 0.25, 1.0), 0.01)
        caixa(o, px - 0.31, -0.17, 0.88, px + 0.31, 0.17, 0.91, mat("pia_in", "#3d4348", 0.4, 1.0), 0.01)
        cilindro(o, px, -hd + 0.07, 0.9, 1.08, 0.014, P["latao"], seg=8)
        caixa(o, px, -hd + 0.07, 1.06, px, -hd + 0.2, 1.09, P["latao"], 0.006)
        caixa(o, ck - 0.32, -hd, 1.58, ck + 0.32, -hd + 0.5, 1.72, P["inox"], 0.01)
        caixa(o, ck - 0.1, -hd, 1.72, ck + 0.1, -hd + 0.2, H, P["inox"], 0.005)
        cilindro(o, ck + 0.55, 0.0, 0.9, 1.1, 0.04, P["ceramica"], seg=16)
    elif t == "armario_alto":
        n = 2
        caixa(o, -hw, -hd, 0, hw, hd, h, P["branco"], 0.01)
        for i in range(n):
            x0 = -hw + i * w / n
            caixa(o, x0 + 0.004, hd - 0.003, 0.02, x0 + w / n - 0.004, hd + 0.014, h - 0.02, P["branco"], 0.006)
    elif t == "ilha":
        caixa(o, -hw, -hd, 0.08, hw, hd, 0.87, P["armario"], 0.012)
        caixa(o, -hw + 0.04, -hd + 0.04, 0.0, hw - 0.04, hd - 0.04, 0.08, P["preto"], 0.0)
        caixa(o, -hw - 0.04, -hd - 0.02, 0.87, hw + 0.04, hd + 0.12, 0.92, P["quartzo"], 0.008)
        for i in range(1, 4):
            caixa(o, -hw + i * w / 4 - 0.004, -hd - 0.001, 0.1, -hw + i * w / 4 + 0.004, -hd + 0.004, 0.85, P["preto"], 0.0)
        cilindro(o, -0.6, 0.0, 0.92, 0.99, 0.2, P["madeira"], r2=0.14, seg=32)
        esfera(o, -0.6, 0.0, 1.02, 0.07, mat("fruta", "#d9803a", 0.6), seg=12)
        esfera(o, -0.52, 0.04, 1.02, 0.07, mat("fruta2", "#b9c44a", 0.6), seg=12)
        cilindro(o, 0.65, 0.05, 0.92, 1.08, 0.05, P["ceramica"], r2=0.035, seg=20)
        esfera(o, 0.65, 0.05, 1.18, 0.09, P["folha2"], esc=(1, 1, 1.2), seg=12)
    elif t == "escrivaninha":
        caixa(o, -hw, -hd, 0.72, hw, hd, 0.75, P["madeira_clara"], 0.01)
        for x in (-hw + 0.04, hw - 0.07):
            caixa(o, x, -hd + 0.04, 0, x + 0.03, hd - 0.04, 0.72, P["preto"], 0.004)
        caixa(o, -0.3, -0.08, 0.75, 0.1, 0.18, 0.76, P["inox"], 0.004)
        caixa(o, -0.3, -0.08, 0.76, 0.1, -0.06, 1.05, P["inox"], 0.004, rx=-12)
        caixa(o, -0.29, -0.075, 0.765, 0.09, -0.065, 1.03, P["tv"], 0.0, rx=-12)
        cilindro(o, hw - 0.14, -0.12, 0.75, 0.83, 0.04, P["ceramica"], seg=16)
        esfera(o, hw - 0.14, -0.12, 0.88, 0.08, P["folha"], esc=(1, 1, 1.2), seg=12)
        cilindro(o, -hw + 0.18, 0.1, 0.75, 0.77, 0.07, P["latao"], seg=24)
        cilindro(o, -hw + 0.18, 0.1, 0.77, 0.98, 0.01, P["latao"], seg=8)
        cilindro(o, -hw + 0.18, 0.1, 0.92, 1.0, 0.07, P["luz_fraca"], r2=0.04, seg=20)
    elif t == "estante":
        caixa(o, -hw, -hd, 0.0, -hw + 0.02, hd, h, P["madeira_clara"], 0.003)
        caixa(o, hw - 0.02, -hd, 0.0, hw, hd, h, P["madeira_clara"], 0.003)
        caixa(o, -hw, -hd, 0.0, hw, -hd + 0.01, h, P["madeira"], 0.0)
        for k in range(6):
            zz = 0.04 + k * (h - 0.06) / 5
            caixa(o, -hw, -hd, zz, hw, hd, zz + 0.025, P["madeira_clara"], 0.003)
        cores = ["#7f9272", "#c9805f", "#e6dcc9", "#4d5f6b", "#b79b6b", "#a7b596", "#d9a58a"]
        for k in range(1, 5):
            zz = 0.04 + k * (h - 0.06) / 5 + 0.025
            x = -hw + 0.06
            j = 0
            while x < hw - 0.2:
                bw = 0.025 + (j * 7 % 4) * 0.008
                bh = 0.22 + ((j + k) * 5 % 4) * 0.03
                caixa(o, x, -hd + 0.03, zz, x + bw, hd - 0.04, zz + bh, mat(f"livro{(j + k) % 7}", cores[(j + k) % 7], 0.7), 0.002)
                x += bw + 0.004
                j += 1
                if j % 6 == 5:
                    x += 0.22
        cilindro(o, hw - 0.14, 0.0, 0.0 + 0.04 + 2 * (h - 0.06) / 5 + 0.025, 0.04 + 2 * (h - 0.06) / 5 + 0.17, 0.05, P["ceramica"], seg=16)
    else:
        caixa(o, -hw, -hd, 0, hw, hd, h, P["branco"], 0.01)
    return o


# ============================================================ arquitetura
def pecas_parede(wd, corte=None):
    e, f, de, ate, esp = wd["eixo"], wd["fixo"], wd["de"], wd["ate"], wd["esp"]

    def r(a, b, z0, z1):
        if corte is not None:
            z1 = min(z1, corte)
            if z1 <= z0:
                return None
        return (a, f - esp / 2, b, f + esp / 2, z0, z1) if e == "x" else (f - esp / 2, a, f + esp / 2, b, z0, z1)

    pecas, cur = [], de
    for ab in sorted(wd["aberturas"], key=lambda a: a["de"]):
        if ab["de"] > cur:
            pecas.append(r(cur, ab["de"], 0, H))
        if ab["peitoril"] > 0:
            pecas.append(r(ab["de"], ab["ate"], 0, ab["peitoril"]))
        topo = ab["peitoril"] + ab["altura"]
        if topo < H:
            pecas.append(r(ab["de"], ab["ate"], topo, H))
        cur = ab["ate"]
    if ate > cur:
        pecas.append(r(cur, ate, 0, H))
    return [p for p in pecas if p]


def construir_arquitetura(P, corte, com_teto):
    # lajes e piso
    caixa(None, -0.4, -0.4, -0.42, 10.4, 8.4, -0.06, P["concreto"], 0.0, nome="laje")
    if corte is None:
        caixa(None, -6, -9, -0.43, 18, 14, -0.42, P["chao_externo"], 0.0, nome="terreno")
    else:
        caixa(None, -1.6, -3.4, -0.5, 11.8, 9.6, -0.42, mat("terreno_aereo", "#d9d3c7", 0.95), 0.0, nome="terreno")
    pisos = {"madeira": P["piso_madeira"], "porcelanato": P["piso_tile"], "deck": P["piso_deck"]}
    for a in PLANTA["ambientes"]:
        xs = [p[0] for p in a["poly"]]
        ys = [p[1] for p in a["poly"]]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        if a["id"] == "varanda":
            caixa(None, x0 - 0.1, y0 - 0.1, -0.2, x1 + 0.1, y1, 0.0, pisos[a["piso"]], 0.0, nome="piso_" + a["id"])
        else:
            caixa(None, x0 - 0.06, y0 - 0.06, -0.06, x1 + 0.06, y1 + 0.06, 0.0, pisos[a["piso"]], 0.0, nome="piso_" + a["id"])
    # paredes
    for wd in PLANTA["paredes"]:
        # vistas aéreas: sul/leste rasas (0,18 m), paredes internas a 1,25 m; norte/oeste inteiras
        corta = corte is not None and wd["id"] in ("E-sul", "E-leste")
        baixa = corte is not None and not wd["ext"]
        lim = corte if corta else (1.25 if baixa else None)
        for (x1, y1, x2, y2, z0, z1) in pecas_parede(wd, lim):
            caixa(None, x1, y1, z0, x2, y2, z1, P["tinta"], 0.0, nome="parede_" + wd["id"])
        if corta or baixa:
            continue
        for ab in wd["aberturas"]:
            esquadria(P, wd, ab)
    if com_teto:
        caixa(None, -0.2, -0.2, H, 10.2, 8.2, H + 0.12, P["teto"], 0.0, nome="teto")
    # guarda-corpo de vidro da varanda
    va = PLANTA["varanda"]
    gc = va["guarda_corpo"]
    caixa(None, va["x1"] - 0.05, va["y1"] - 0.05, 0, va["x2"] + 0.05, va["y1"], gc, P["vidro"], 0.0, nome="gc_vidro")
    caixa(None, va["x1"] - 0.05, va["y1"], 0, va["x1"], 0.0, gc, P["vidro"], 0.0, nome="gc_vidro")
    caixa(None, va["x2"], va["y1"], 0, va["x2"] + 0.05, 0.0, gc, P["vidro"], 0.0, nome="gc_vidro")
    caixa(None, va["x1"] - 0.06, va["y1"] - 0.06, gc, va["x2"] + 0.06, va["y1"] + 0.02, gc + 0.04, P["inox"], 0.005, nome="corrimao")
    caixa(None, va["x1"] - 0.06, va["y1"], gc, va["x1"] + 0.02, 0.0, gc + 0.04, P["inox"], 0.005, nome="corrimao")
    caixa(None, va["x2"] - 0.02, va["y1"], gc, va["x2"] + 0.06, 0.0, gc + 0.04, P["inox"], 0.005, nome="corrimao")


def esquadria(P, wd, ab):
    e, f, esp = wd["eixo"], wd["fixo"], wd["esp"]
    a, b = ab["de"], ab["ate"]
    z0, z1 = ab["peitoril"], ab["peitoril"] + ab["altura"]
    t = 0.045
    fr = P["preto"]

    def retan(u0, u1, v0, v1, zz0, zz1, mt, nome):
        # u ao longo do eixo da parede; v ao longo da espessura
        if e == "x":
            caixa(None, u0, f + v0, zz0, u1, f + v1, zz1, mt, 0.0, nome=nome)
        else:
            caixa(None, f + v0, u0, zz0, f + v1, u1, zz1, mt, 0.0, nome=nome)

    if ab["tipo"] in ("janela", "porta_correr"):
        retan(a, a + t, -0.03, 0.03, z0, z1, fr, "caixilho")
        retan(b - t, b, -0.03, 0.03, z0, z1, fr, "caixilho")
        retan(a, b, -0.03, 0.03, z1 - t, z1, fr, "caixilho")
        if ab["tipo"] == "janela":
            retan(a, b, -0.03, 0.03, z0, z0 + t, fr, "caixilho")
            retan((a + b) / 2 - t / 2, (a + b) / 2 + t / 2, -0.03, 0.03, z0, z1, fr, "caixilho")
            retan(a + t, b - t, -0.006, 0.006, z0 + t, z1 - t, P["vidro"], "vidro")
            retan(a - 0.05, b + 0.05, -esp / 2 - 0.04, esp / 2 + 0.04, z0 - 0.04, z0, P["branco"], "peitoril")
        else:
            m_ = (a + b) / 2
            retan(a + t, m_ + 0.04, -0.02, -0.008, 0, z1 - t, P["vidro"], "vidro")
            retan(m_ - 0.04, b - t, 0.008, 0.02, 0, z1 - t, P["vidro"], "vidro")
            retan(m_ - 0.04, m_ + 0.04, -0.03, 0.03, 0, z1 - t, fr, "caixilho")
    else:   # porta de abrir: folha aberta
        larg = b - a
        hinge_a = a if ab["dobradica"] == "de" else b
        sinal = 1 if ab["abre"] == "+" else -1
        # folha perpendicular à parede, aberta 80°
        ang = math.radians(80)
        folga = 0.0
        if e == "x":
            hx, hy = hinge_a, f
            dirx = 0 if True else 1
            fim = (hx + (math.cos(ang) * larg * (-1 if ab["dobradica"] == "ate" else 1)), hy + sinal * math.sin(ang) * larg)
        else:
            hx, hy = f, hinge_a
            fim = (hx + sinal * math.sin(ang) * larg, hy + (math.cos(ang) * larg * (-1 if ab["dobradica"] == "ate" else 1)))
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        cx, cy = (hx + fim[0]) / 2, (hy + fim[1]) / 2
        for v in bm.verts:
            v.co.x *= larg
            v.co.y *= 0.04
            v.co.z = (v.co.z + 0.5) * ab["altura"]
        ob = novo_obj("porta_" + ab["id"], bm, P["madeira"])
        ob.location = (cx, cy, 0)
        ob.rotation_euler = (0, 0, math.atan2(fim[1] - hy, fim[0] - hx))
        # batente: moldura DENTRO do vão (não sobrepõe a parede)
        j = 0.035
        retan(a, a + j, -esp / 2 - 0.004, esp / 2 + 0.004, 0, ab["altura"], P["branco"], "batente")
        retan(b - j, b, -esp / 2 - 0.004, esp / 2 + 0.004, 0, ab["altura"], P["branco"], "batente")
        retan(a + j, b - j, -esp / 2 - 0.004, esp / 2 + 0.004, ab["altura"] - j, ab["altura"], P["branco"], "batente")


def luz_area(nome, loc, tam, pot, cor=(1.0, 0.86, 0.68)):
    ld = bpy.data.lights.new(nome, "AREA")
    ld.energy = pot
    ld.shape = "RECTANGLE"
    ld.size, ld.size_y = tam
    ld.color = cor
    ob = bpy.data.objects.new(nome, ld)
    COL.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0, 0, 0)   # aponta para baixo
    return ob


def iluminacao(P, vista):
    mundo = bpy.data.worlds.new("ceu")
    mundo.use_nodes = True
    nt = mundo.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    if vista in ("aerea", "topo"):          # fundo de estúdio, sem céu
        bg.inputs["Color"].default_value = hexa("#ece9e2")
        bg.inputs["Strength"].default_value = 0.9
    else:
        sky = nt.nodes.new("ShaderNodeTexSky")
        sky.sky_type = "MULTIPLE_SCATTERING"
        sky.sun_disc = False
        sky.sun_elevation = math.radians(48)
        sky.sun_rotation = math.radians(200)
        bg.inputs["Strength"].default_value = 1.15
        nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bpy.context.scene.world = mundo
    # sol
    sd = bpy.data.lights.new("sol", "SUN")
    sd.energy = 2.6
    sd.angle = math.radians(1.6)
    sd.color = (1.0, 0.93, 0.82)
    so = bpy.data.objects.new("sol", sd)
    COL.objects.link(so)
    so.rotation_euler = (math.radians(52), 0, math.radians(-25))   # vem do noroeste, descendo para o sudeste
    if vista in ("aerea", "topo"):
        return
    # luz de teto (invisível) + pendentes
    teto = H - 0.02
    luz_area("sala1", (1.9, 2.3, teto), (1.4, 1.4), 120)
    luz_area("sala2", (4.8, 3.0, teto), (1.4, 1.4), 90)
    luz_area("coz", (8.2, 2.0, teto), (1.6, 1.0), 110)
    luz_area("suite", (2.0, 6.3, teto), (1.4, 1.2), 90)
    luz_area("office", (8.5, 6.3, teto), (1.2, 1.0), 70)
    luz_area("banho1", (4.5, 6.3, teto), (0.6, 0.6), 40)
    luz_area("banho2", (6.2, 6.3, teto), (0.6, 0.6), 30)
    # pendentes sobre a ilha e a mesa
    for x in (7.6, 8.2, 8.8):
        cilindro(None, x, 2.1, 1.75, H, 0.004, P["preto"], seg=6)
        esfera(None, x, 2.1, 1.62, 0.12, P["luz_quente"], esc=(1, 1, 0.9), seg=24, nome="pendente")
    cilindro(None, 5.3, 2.7, 2.0, H, 0.004, P["preto"], seg=6)
    cilindro(None, 5.3, 3.5, 2.0, H, 0.004, P["preto"], seg=6)
    caixa(None, 5.2, 2.55, 1.94, 5.4, 3.65, 2.0, P["luz_fraca"], 0.02, nome="pendente_mesa")
    luz_area("pendente_mesa", (5.3, 3.1, 1.9), (0.5, 0.9), 45)


def camera(vista, res):
    cd = bpy.data.cameras.new("cam")
    ob = bpy.data.objects.new("cam", cd)
    COL.objects.link(ob)
    bpy.context.scene.camera = ob
    cd.sensor_width = 36
    poses = {
        "aerea": ((14.6, -8.2, 10.8), (5.0, 3.0, 0.3), 36),
        "topo": ((4.9, 3.0, 22.0), (4.9, 3.0, 0.0), None),
        "sala": ((9.35, 4.15, 1.55), (1.4, 1.9, 0.9), 21),
        "cozinha": ((5.1, 0.55, 1.45), (8.6, 2.3, 0.85), 19),
        "suite": ((0.85, 5.1, 1.5), (2.5, 7.2, 0.75), 21),
    }
    loc, alvo, lente = poses[vista]
    ob.location = loc
    if lente is None:
        cd.type = "ORTHO"
        cd.ortho_scale = 13.2
        ob.rotation_euler = (0, 0, 0)
        ob.location = (4.9, 2.9, 22)
    else:
        cd.lens = lente
        d = Vector(alvo) - Vector(loc)
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob


def limpar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global COL, MATS
    MATS = {}
    COL = bpy.data.collections.new("apto")
    bpy.context.scene.collection.children.link(COL)


def montar(vista, qualidade, saida_png, largura, altura, amostras):
    limpar()
    P = paleta()
    corte = 0.18 if vista in ("aerea", "topo") else None
    construir_arquitetura(P, corte, com_teto=vista not in ("aerea", "topo"))
    for mv in LAYOUT["moveis"]:
        build_movel(P, mv)
    iluminacao(P, vista)
    camera(vista, (largura, altura))
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = amostras
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 8
    cy.diffuse_bounces = 4
    cy.glossy_bounces = 4
    cy.transmission_bounces = 6
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    sc.render.resolution_x, sc.render.resolution_y = largura, altura
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = {"aerea": -0.25, "topo": -0.1}.get(vista, 0.3)
    sc.render.image_settings.file_format = "PNG"
    sc.render.threads_mode = "AUTO"
    sc.render.filepath = str(saida_png)
    bpy.ops.render.render(write_still=True)
    if "--salvar-blend" in sys.argv:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(saida_png).with_suffix(".blend")))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--vista", default="sala", choices=["aerea", "topo", "sala", "cozinha", "suite"])
    ap.add_argument("--qualidade", default="rapida", choices=["rapida", "final"])
    ap.add_argument("--amostras", type=int, default=0)
    ap.add_argument("--largura", type=int, default=0)
    ap.add_argument("--salvar-blend", action="store_true")
    a, _ = ap.parse_known_args(argv)
    final = a.qualidade == "final"
    pasta = AQUI / "saida" / ("render" if final else "validacao")
    pasta.mkdir(parents=True, exist_ok=True)
    larg = a.largura or (1920 if final else 1280)
    alt = round(larg * 9 / 16)
    amostras = a.amostras or (160 if final else 24)
    montar(a.vista, a.qualidade, pasta / f"{a.vista}.png", larg, alt, amostras)
    print("pronto:", pasta / f"{a.vista}.png")
