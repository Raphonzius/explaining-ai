#!/usr/bin/env python3
"""Do briefing à planta mobiliada (etapas 1 e 2 do pipeline).

O que este script faz, sem programa de desenho nenhum:
  1. lê a planta base (planta-base.json) e os requisitos (requisitos.json);
  2. posiciona o mobiliário (a proposta da IA fica na lista MOVEIS, abaixo);
  3. VALIDA com regras determinísticas: móvel dentro do ambiente, colisões,
     giro das portas, áreas mínimas, itens do briefing e circulação mínima
     (mapa de distância: o "gargalo" do caminho entre as portas);
  4. desenha a planta mobiliada em SVG e escreve o relatório de validação.

A IA propõe; este código confere. Quem decide é a arquiteta.

Uso:
    pip install shapely scipy numpy pillow
    python apto.py            # versão final: gera tudo em saida/
    python apto.py --v1       # 1ª proposta (com o defeito que a validação acusa)
Dados fictícios. Unidades: metros.
"""
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.affinity import rotate as g_rot
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

AQUI = Path(__file__).parent
SAIDA = AQUI / "saida"
PLANTA = json.loads((AQUI / "planta-base.json").read_text(encoding="utf-8"))
REQ = json.loads((AQUI / "requisitos.json").read_text(encoding="utf-8"))
H = PLANTA["pe_direito"]


# ============================================================ paredes e aberturas
def pecas_parede(w):
    """Peças retangulares da parede (x1, y1, x2, y2, z0, z1), já descontando os vãos."""
    e, f, de, ate, esp = w["eixo"], w["fixo"], w["de"], w["ate"], w["esp"]

    def r(a, b, z0, z1):
        return (a, f - esp / 2, b, f + esp / 2, z0, z1) if e == "x" else (f - esp / 2, a, f + esp / 2, b, z0, z1)

    pecas, cur = [], de
    for ab in sorted(w["aberturas"], key=lambda a: a["de"]):
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
    return pecas


def vao_retangulo(w, ab):
    e, f, esp = w["eixo"], w["fixo"], w["esp"]
    return box(ab["de"], f - esp / 2, ab["ate"], f + esp / 2) if e == "x" else box(f - esp / 2, ab["de"], f + esp / 2, ab["ate"])


def giro_porta(w, ab):
    """Folha da porta de abrir: dobradiça, ângulos e o setor (área que precisa ficar livre)."""
    e, f = w["eixo"], w["fixo"]
    larg = ab["ate"] - ab["de"]
    h_ax = ab["de"] if ab["dobradica"] == "de" else ab["ate"]
    sinal = 1 if ab["abre"] == "+" else -1
    if e == "x":
        hinge = (h_ax, f)
        fecha = 0 if ab["dobradica"] == "de" else 180        # direção da folha fechada
        abre = 90 if sinal > 0 else 270
    else:
        hinge = (f, h_ax)
        fecha = 90 if ab["dobradica"] == "de" else 270
        abre = 0 if sinal > 0 else 180
    # varre o arco do ângulo "fecha" até "abre" pelo caminho de 90°
    d = (abre - fecha + 540) % 360 - 180
    angs = [fecha + d * i / 24 for i in range(25)]
    pts = [hinge] + [(hinge[0] + larg * math.cos(math.radians(a)), hinge[1] + larg * math.sin(math.radians(a))) for a in angs]
    return {"id": ab["id"], "hinge": hinge, "larg": larg, "a0": fecha, "a1": fecha + d, "poly": Polygon(pts)}


PAREDES = PLANTA["paredes"]
PORTAS = [(w, ab) for w in PAREDES for ab in w["aberturas"] if ab["tipo"] == "porta"]
GIROS = {ab["id"]: giro_porta(w, ab) for w, ab in PORTAS}
AMBIENTES = {a["id"]: a for a in PLANTA["ambientes"]}


# ============================================================ mobiliário (a proposta)
MOVEIS = []


def m(id, tipo, amb, cx, cy, w, d, rot=0, h=0.5, z=0.0, **kw):
    """w = medida ao longo de x local; d = profundidade (y local). Costas = -y; frente = +y.
    rot = graus anti-horário (rot=90 → a frente aponta para o oeste)."""
    MOVEIS.append(dict(id=id, tipo=tipo, ambiente=amb, cx=cx, cy=cy, w=w, d=d, rot=rot, h=h, z=z, **kw))


SC = "sala_cozinha"
# --- sala
m("rack1", "rack_tv", SC, 0.325, 2.3, 2.2, 0.45, 270, 0.45)
m("tv1", "tv", SC, 0.12, 2.3, 1.25, 0.06, 270, 0.72, z=1.0)
m("tapete1", "tapete", SC, 2.1, 2.3, 2.4, 2.4, 0, 0.02)
m("sofa1", "sofa3", SC, 3.0, 2.3, 2.3, 0.95, 90, 0.85)
m("mesacentro1", "mesa_centro", SC, 1.8, 2.3, 0.6, 1.1, 0, 0.38)
m("poltrona1", "poltrona", SC, 1.5, 3.95, 0.85, 0.85, 180, 0.85)
# A 1ª proposta pôs a mesa de apoio ao lado do sofá, em frente à porta da suíte (P02).
# A validação acusou o gargalo de circulação e a IA moveu a mesa para a outra ponta do sofá.
PRIMEIRA_PROPOSTA = os.environ.get("APTO_V1") == "1" or "--v1" in sys.argv
m("apoio1", "mesa_apoio_sala", SC, *((3.05, 3.85) if PRIMEIRA_PROPOSTA else (3.0, 0.9)), 0.45, 0.45, 0, 0.5)
m("abajur1", "luminaria_piso", SC, 0.45, 3.95, 0.3, 0.3, 0, 1.6)
m("planta_sala", "planta", SC, 0.45, 0.45, 0.5, 0.5, 0, 1.1)
# --- jantar (6 lugares)
m("mesaj1", "mesa_jantar", SC, 5.3, 3.1, 0.9, 1.8, 0, 0.75)
for i, (cx, cy, r) in enumerate([(4.5, 2.6, 270), (4.5, 3.6, 270), (6.1, 2.6, 90), (6.1, 3.6, 90), (5.3, 1.85, 0), (5.3, 4.32, 180)], 1):
    m(f"cadj{i}", "cadeira_jantar", SC, cx, cy, 0.42, 0.42, r, 0.9)
# --- cozinha
m("geladeira1", "geladeira", SC, 9.6, 0.4, 0.75, 0.75, 0, 1.85)
m("bancada1", "bancada", SC, 7.75, 0.3, 2.9, 0.6, 0, 0.9, cooktop_x=6.95, pia_x=8.55)
m("alto1", "armario_alto", SC, 6.725, 0.175, 0.85, 0.35, 0, 0.7, z=1.5)
m("ilha1", "ilha", SC, 8.2, 2.1, 2.2, 0.9, 0, 0.92)
for i, x in enumerate([7.6, 8.2, 8.8], 1):
    m(f"banqueta{i}", "banqueta", SC, x, 2.95, 0.38, 0.38, 0, 0.65)
# --- suíte
m("cama1", "cama_queen", "suite", 2.15, 6.95, 1.6, 2.0, 180, 0.55)
m("criado1", "criado", "suite", 1.1, 7.75, 0.4, 0.4, 180, 0.5)
m("criado2", "criado", "suite", 3.2, 7.75, 0.4, 0.4, 180, 0.5)
m("guardaroupa1", "guarda_roupa", "suite", 0.325, 6.2, 2.6, 0.55, 270, 2.4)
m("banco1", "banco_cama", "suite", 2.15, 5.7, 1.4, 0.4, 0, 0.45)
m("tapete2", "tapete", "suite", 2.15, 6.6, 2.4, 2.2, 0, 0.02)
# --- banho da suíte
m("vaso1", "vaso", "banho_suite", 4.1, 7.675, 0.38, 0.65, 180, 0.4)
m("box1", "box", "banho_suite", 4.95, 7.5, 0.85, 0.85, 0, 2.0)
m("lav1", "lavatorio", "banho_suite", 4.8, 4.9, 0.8, 0.45, 0, 0.85)
# --- banho social
m("box2", "box", "banho_social", 5.9, 7.5, 0.8, 0.8, 0, 2.0)
m("vaso2", "vaso", "banho_social", 6.64, 7.3, 0.38, 0.6, 90, 0.4)
m("lav2", "lavatorio", "banho_social", 6.7, 6.0, 0.7, 0.45, 90, 0.85)
# --- home office
m("mesa_off", "escrivaninha", "home_office", 9.6, 6.5, 1.5, 0.7, 90, 0.75)
m("cadeira_off", "cadeira_office", "home_office", 8.85, 6.5, 0.55, 0.55, 270, 0.95)
m("sofacama1", "sofa_cama", "home_office", 7.5, 7.0, 1.9, 0.9, 270, 0.8)
m("estante1", "estante", "home_office", 9.0, 7.8, 1.4, 0.35, 180, 1.9)
m("tapete3", "tapete", "home_office", 8.5, 6.3, 2.0, 1.6, 0, 0.02)
# --- varanda
m("poltv1", "poltrona_varanda", "varanda", 1.3, -0.95, 0.8, 0.8, 200, 0.8)
m("poltv2", "poltrona_varanda", "varanda", 2.9, -0.95, 0.8, 0.8, 160, 0.8)
m("mesav1", "mesa_apoio", "varanda", 2.1, -1.5, 0.6, 0.6, 0, 0.45)
m("planta_v1", "planta", "varanda", 5.45, -0.5, 0.55, 0.55, 0, 1.2)
m("planta_v2", "planta", "varanda", 5.45, -1.5, 0.55, 0.55, 0, 1.2)
m("planta_v3", "planta", "varanda", 0.45, -1.6, 0.5, 0.5, 0, 1.0)

RASANTES = {"tapete"}


def pegada(mv):
    p = box(mv["cx"] - mv["w"] / 2, mv["cy"] - mv["d"] / 2, mv["cx"] + mv["w"] / 2, mv["cy"] + mv["d"] / 2)
    return g_rot(p, mv["rot"], origin=(mv["cx"], mv["cy"]))


for mv in MOVEIS:
    mv["_poly"] = pegada(mv)


# ============================================================ validação
def sobrepoem_em_z(a, b):
    return a["z"] < b["z"] + b["h"] and b["z"] < a["z"] + a["h"]


def validar():
    achados = []   # (severidade, titulo, detalhe)  severidade: ok | atencao
    ok = lambda t, d="": achados.append(("ok", t, d))
    aten = lambda t, d="": achados.append(("atencao", t, d))

    # 1) tudo dentro do ambiente
    fora = []
    for mv in MOVEIS:
        amb = Polygon(AMBIENTES[mv["ambiente"]]["poly"]).buffer(0.03)
        if not amb.contains(mv["_poly"]):
            fora.append(mv["id"])
    (aten if fora else ok)("Móveis dentro dos ambientes", ", ".join(fora) if fora else f"{len(MOVEIS)} itens conferidos")

    # 2) colisões entre móveis
    colis = []
    reais = [x for x in MOVEIS if x["tipo"] not in RASANTES]
    for i, a in enumerate(reais):
        for b in reais[i + 1:]:
            if sobrepoem_em_z(a, b) and a["_poly"].intersection(b["_poly"]).area > 1e-3:
                colis.append(f'{a["id"]}×{b["id"]}')
    (aten if colis else ok)("Sem colisão entre móveis", ", ".join(colis) if colis else "nenhuma sobreposição")

    # 3) giro das portas livre
    bate = []
    for pid, g in GIROS.items():
        for x in reais:
            if x["z"] < 2.0 and g["poly"].intersection(x["_poly"]).area > 1e-3:
                bate.append(f'{pid}×{x["id"]}')
    (aten if bate else ok)("Portas abrem sem bater em móveis", ", ".join(bate) if bate else f"{len(GIROS)} portas conferidas")

    # 4) áreas mínimas
    for amb, minimo in REQ["areas_minimas_m2"].items():
        area = Polygon(AMBIENTES[amb]["poly"]).area
        nome = AMBIENTES[amb]["nome"]
        if area + 1e-9 >= minimo:
            ok(f"Área mínima: {nome}", f"{area:.1f} m² (mín. {minimo:.1f})")
        else:
            aten(f"Área mínima: {nome}", f"{area:.1f} m² < {minimo:.1f} m² do briefing. As paredes são estruturais: decisão da arquiteta.")

    # 5) itens do briefing
    faltam = []
    for it in REQ["itens_obrigatorios"]:
        achados_ = [x for x in MOVEIS if x["ambiente"] == it["ambiente"] and x["tipo"] == it["tipo"]]
        if len(achados_) < it["min"]:
            faltam.append(f'{it["origem"]} ({len(achados_)}/{it["min"]})')
        elif "frente_min_m" in it and max(x["w"] for x in achados_) < it["frente_min_m"]:
            faltam.append(f'{it["origem"]}: frente menor que {it["frente_min_m"]} m')
    (aten if faltam else ok)("Itens do briefing", "; ".join(faltam) if faltam else f'{len(REQ["itens_obrigatorios"])} requisitos atendidos')

    # 6) circulação (mapa de distância)
    gargalo, caminhos = circulacao()
    alvo = REQ["circulacao_minima_m"]
    if gargalo + 1e-9 >= alvo:
        ok("Circulação mínima", f"gargalo de {gargalo:.2f} m nos caminhos entre portas (alvo {alvo:.2f} m)")
    else:
        aten("Circulação mínima", f"gargalo de {gargalo:.2f} m (alvo {alvo:.2f} m)")
    return achados, gargalo, caminhos


RES = 0.05
X0, Y0, X1, Y1 = -0.5, -2.5, 11.6, 8.5


def _px(x, y):
    return ((x - X0) / RES, (Y1 - y) / RES)


def _desenhar(dr, geom, fill):
    for p in (geom.geoms if hasattr(geom, "geoms") else [geom]):
        if p.is_empty or p.geom_type != "Polygon":
            continue
        dr.polygon([_px(*c) for c in p.exterior.coords], fill=fill)
        for r in p.interiors:
            dr.polygon([_px(*c) for c in r.coords], fill=0 if fill else 1)


def circulacao():
    """Largura máxima de passagem que mantém todas as portas conectadas à entrada."""
    W, Hh = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
    img = Image.new("L", (W, Hh), 0)
    dr = ImageDraw.Draw(img)
    for a in AMBIENTES.values():
        dr.polygon([_px(*c) for c in a["poly"]], fill=1)
    vaos = []
    for w in PAREDES:
        for ab in w["aberturas"]:
            if ab["tipo"] in ("porta", "porta_correr"):
                v = vao_retangulo(w, ab)
                vaos.append(v)
                dr.polygon([_px(*c) for c in v.exterior.coords], fill=1)
    dr.polygon([_px(*c) for c in [(10.2, 2.4), (11.6, 2.4), (11.6, 5.6), (10.2, 5.6)]], fill=1)   # patamar da entrada
    livre = np.array(img, dtype=bool)
    obst = Image.new("L", (W, Hh), 0)
    do = ImageDraw.Draw(obst)
    for x in MOVEIS:
        if x["tipo"] in RASANTES or x["z"] >= 1.0 or x["h"] < 0.1:
            continue
        do.polygon([_px(*c) for c in x["_poly"].exterior.coords], fill=1)
    livre &= ~np.array(obst, dtype=bool)
    dt = ndimage.distance_transform_edt(livre) * RES
    forca = np.zeros_like(livre)
    mask_vaos = Image.new("L", (W, Hh), 0)
    dv = ImageDraw.Draw(mask_vaos)
    for v in vaos:
        dv.polygon([_px(*c) for c in v.exterior.coords], fill=1)
    forca = np.array(mask_vaos, dtype=bool) & livre
    ent = _px(10.7, 3.95)
    ent = (int(ent[1]), int(ent[0]))
    alvos = [(int(_px(*v.centroid.coords[0])[1]), int(_px(*v.centroid.coords[0])[0])) for v in vaos]
    melhor, ult = 0.0, {}
    for wd in np.arange(0.40, 1.51, 0.05):
        regiao = ((dt >= wd / 2 - RES / 2) | forca) & livre
        lab, _ = ndimage.label(regiao, structure=np.ones((3, 3)))
        base = lab[ent]
        if base and all(lab[a] == base for a in alvos):
            melhor = float(wd)
            ult = {"largura": melhor}
        else:
            break
    return melhor, ult


# ============================================================ desenho (SVG)
S = 100          # px por metro
MX, MY = 70, 70  # margem
XMIN, XMAX, YMIN, YMAX = -0.6, 11.3, -2.6, 8.6
SVG_W, SVG_H = int((XMAX - XMIN) * S + 2 * MX), int((YMAX - YMIN) * S + 2 * MY + 40)
INK, POCHE = "#1f252b", "#262c33"
PISO = {"madeira": "#eadcc3", "porcelanato": "#dfe6e8", "deck": "#d8c09b"}


def X(x):
    return (x - XMIN) * S + MX


def Y(y):
    return (YMAX - y) * S + MY


def f2(v):
    return f"{v:.2f}".replace(".", ",")


def icone(mv):
    """Ícone em coordenadas locais (m); frente = +y, costas = -y."""
    w, d, t = mv["w"], mv["d"], mv["tipo"]
    hw, hd = w / 2, d / 2
    sk = f'stroke="{INK}" stroke-width="1.4" vector-effect="non-scaling-stroke"'
    R = lambda x, y, ww, hh, fill, rx=0.04, extra="": f'<rect x="{x:.3f}" y="{y:.3f}" width="{ww:.3f}" height="{hh:.3f}" rx="{rx}" fill="{fill}" {sk} {extra}/>'
    C = lambda x, y, r, fill: f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" fill="{fill}" {sk}/>'
    o = []
    if t == "tapete":
        o.append(R(-hw, -hd, w, d, "#efe6d4", 0.02, 'stroke-dasharray="6 4"'))
    elif t in ("sofa3", "sofa_cama"):
        o.append(R(-hw, -hd, w, d, "#c9cfbf"))
        o.append(R(-hw, -hd, w, 0.2, "#aab397"))
        o.append(R(-hw, -hd + 0.2, 0.18, d - 0.2, "#aab397"))
        o.append(R(hw - 0.18, -hd + 0.2, 0.18, d - 0.2, "#aab397"))
        n = 3 if t == "sofa3" else 2
        iw = (w - 0.36) / n
        for i in range(1, n):
            o.append(f'<line x1="{-hw + 0.18 + i * iw:.3f}" y1="{-hd + 0.2:.3f}" x2="{-hw + 0.18 + i * iw:.3f}" y2="{hd:.3f}" {sk}/>')
    elif t == "cama_queen":
        o.append(R(-hw, -hd, w, d, "#f3efe6"))
        o.append(R(-hw, -hd, w, 0.12, "#a98a66"))
        o.append(R(-hw + 0.1, -hd + 0.18, w / 2 - 0.15, 0.4, "#ffffff", 0.06))
        o.append(R(0.05, -hd + 0.18, w / 2 - 0.15, 0.4, "#ffffff", 0.06))
        o.append(R(-hw, -hd + 0.75, w, d - 0.75, "#aab397", 0.03))
    elif t in ("poltrona", "poltrona_varanda", "cadeira_office"):
        o.append(R(-hw, -hd, w, d, "#d9a58a" if t != "cadeira_office" else "#8b949b", 0.1))
        o.append(R(-hw, -hd, w, 0.16, "#b98468" if t != "cadeira_office" else "#5f686f", 0.06))
    elif t == "cadeira_jantar" or t == "banqueta":
        if t == "banqueta":
            o.append(C(0, 0, hw, "#cdb48f"))
        else:
            o.append(R(-hw, -hd, w, d, "#cdb48f", 0.05))
            o.append(R(-hw, -hd, w, 0.07, "#a98a66", 0.03))
    elif t in ("mesa_jantar", "escrivaninha", "mesa_centro", "estante", "rack_tv", "banco_cama", "criado", "mesa_apoio_sala"):
        cor = {"mesa_jantar": "#cdb48f", "escrivaninha": "#cdb48f", "mesa_centro": "#e8d3b0", "estante": "#cdb48f", "rack_tv": "#cdb48f", "banco_cama": "#c9cfbf", "criado": "#cdb48f", "mesa_apoio_sala": "#e8d3b0"}[t]
        o.append(R(-hw, -hd, w, d, cor))
        if t == "estante":
            for i in range(1, 5):
                o.append(f'<line x1="{-hw + i * w / 5:.3f}" y1="{-hd:.3f}" x2="{-hw + i * w / 5:.3f}" y2="{hd:.3f}" {sk}/>')
    elif t == "mesa_apoio":
        o.append(C(0, 0, hw, "#e8d3b0"))
    elif t == "tv":
        o.append(R(-hw, -hd, w, d, "#20252a", 0.01))
    elif t == "guarda_roupa":
        o.append(R(-hw, -hd, w, d, "#e4d8c3"))
        for i in range(1, 6):
            o.append(f'<line x1="{-hw + i * w / 6:.3f}" y1="{-hd:.3f}" x2="{-hw + i * w / 6:.3f}" y2="{hd:.3f}" {sk}/>')
    elif t == "planta":
        o.append(C(0, 0, hw, "#9bc08a"))
        o.append(C(0, 0, hw * 0.45, "#6fa066"))
    elif t == "luminaria_piso":
        o.append(C(0, 0, hw, "#f2d98a"))
    elif t == "geladeira":
        o.append(R(-hw, -hd, w, d, "#dfe3e6"))
        o.append(f'<line x1="{-hw:.3f}" y1="0" x2="{hw:.3f}" y2="0" {sk}/>')
    elif t == "bancada":
        o.append(R(-hw, -hd, w, d, "#f2f0ea"))
        cx = mv["cooktop_x"] - mv["cx"]
        for dx in (-0.12, 0.12):
            for dy in (-0.12, 0.12):
                o.append(C(cx + dx, dy, 0.08, "#2a2f35"))
        px = mv["pia_x"] - mv["cx"]
        o.append(R(px - 0.35, -0.2, 0.7, 0.4, "#c8d0d6", 0.03))
        o.append(C(px, 0, 0.04, "#6c747b"))
    elif t == "armario_alto":
        o.append(R(-hw, -hd, w, d, "none", 0.02, 'stroke-dasharray="5 4"'))
    elif t == "ilha":
        o.append(R(-hw, -hd, w, d, "#a9b79a"))
        o.append(R(-hw - 0.05, -hd - 0.03, w + 0.1, d + 0.06, "none", 0.02))
    elif t == "vaso":
        o.append(R(-hw + 0.04, -hd, w - 0.08, 0.2, "#ffffff", 0.03))
        o.append(f'<ellipse cx="0" cy="{-hd + 0.43:.3f}" rx="{hw - 0.02:.3f}" ry="{0.24:.3f}" fill="#ffffff" {sk}/>')
    elif t == "lavatorio":
        o.append(R(-hw, -hd, w, d, "#f2f0ea"))
        o.append(f'<ellipse cx="0" cy="0.02" rx="{min(hw - 0.12, 0.22):.3f}" ry="0.13" fill="#c8d0d6" {sk}/>')
    elif t == "box":
        o.append(R(-hw, -hd, w, d, "#e3eef2", 0.02))
        o.append(f'<line x1="{-hw:.3f}" y1="{-hd:.3f}" x2="{hw:.3f}" y2="{hd:.3f}" {sk}/>')
        o.append(C(0, 0, 0.05, "#9aa3aa"))
    else:
        o.append(R(-hw, -hd, w, d, "#dddddd"))
    return "".join(o)


def desenhar_svg(com_moveis=True, achados=None, gargalo=None):
    L = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}" font-family="Inter, Helvetica, Arial, sans-serif">')
    L.append(f'<rect width="{SVG_W}" height="{SVG_H}" fill="#f7f6f2"/>')
    # pisos
    for a in PLANTA["ambientes"]:
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in a["poly"])
        L.append(f'<polygon points="{pts}" fill="{PISO[a["piso"]]}"/>')
    # paredes (corte a 1,20 m: peitoris altos fecham o vão)
    for w in PAREDES:
        for (x1, y1, x2, y2, z0, z1) in pecas_parede(w):
            if z0 == 0 and (z1 >= H - 1e-6):
                L.append(f'<rect x="{X(x1):.1f}" y="{Y(y2):.1f}" width="{(x2 - x1) * S:.1f}" height="{(y2 - y1) * S:.1f}" fill="{POCHE}"/>')
        for ab in w["aberturas"]:
            v = vao_retangulo(w, ab)
            x1, y1, x2, y2 = v.bounds
            if ab["tipo"] == "janela":
                if ab["peitoril"] >= 1.2:       # acima do corte: parede segue desenhada, símbolo tracejado
                    L.append(f'<rect x="{X(x1):.1f}" y="{Y(y2):.1f}" width="{(x2 - x1) * S:.1f}" height="{(y2 - y1) * S:.1f}" fill="{POCHE}"/>')
                    cx, cy = X((x1 + x2) / 2), Y((y1 + y2) / 2)
                    if w["eixo"] == "x":
                        L.append(f'<line x1="{X(x1):.1f}" y1="{cy:.1f}" x2="{X(x2):.1f}" y2="{cy:.1f}" stroke="#f7f6f2" stroke-width="2" stroke-dasharray="6 4"/>')
                else:
                    L.append(f'<rect x="{X(x1):.1f}" y="{Y(y2):.1f}" width="{(x2 - x1) * S:.1f}" height="{(y2 - y1) * S:.1f}" fill="#f7f6f2"/>')
                    if w["eixo"] == "x":
                        for k in (0.25, 0.5, 0.75):
                            yy = Y(y1 + (y2 - y1) * k)
                            L.append(f'<line x1="{X(x1):.1f}" y1="{yy:.1f}" x2="{X(x2):.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="1.4"/>')
                    else:
                        for k in (0.25, 0.5, 0.75):
                            xx = X(x1 + (x2 - x1) * k)
                            L.append(f'<line x1="{xx:.1f}" y1="{Y(y1):.1f}" x2="{xx:.1f}" y2="{Y(y2):.1f}" stroke="{INK}" stroke-width="1.4"/>')
            else:
                L.append(f'<rect x="{X(x1):.1f}" y="{Y(y2):.1f}" width="{(x2 - x1) * S:.1f}" height="{(y2 - y1) * S:.1f}" fill="#f7f6f2"/>')
                if ab["tipo"] == "porta_correr":
                    mx = (ab["de"] + ab["ate"]) / 2
                    L.append(f'<line x1="{X(ab["de"]):.1f}" y1="{Y(w["fixo"] + 0.03):.1f}" x2="{X(mx + 0.1):.1f}" y2="{Y(w["fixo"] + 0.03):.1f}" stroke="{INK}" stroke-width="2.5"/>')
                    L.append(f'<line x1="{X(mx - 0.1):.1f}" y1="{Y(w["fixo"] - 0.03):.1f}" x2="{X(ab["ate"]):.1f}" y2="{Y(w["fixo"] - 0.03):.1f}" stroke="{INK}" stroke-width="2.5"/>')
        # soleiras/rótulos de esquadria
        for ab in w["aberturas"]:
            v = vao_retangulo(w, ab)
            cx, cy = v.centroid.coords[0]
            off = 0.38 if w["ext"] else 0.0
            if not w["ext"]:
                continue
            if ab["tipo"] == "porta_correr":
                tx, ty = X(cx), Y(0.3)
            elif w["eixo"] == "x":
                tx, ty = X(cx), Y(cy + (off if w["fixo"] > 4 else -off - 0.08))
            else:
                tx, ty = X(cx + (off if w["fixo"] > 4 else -off)), Y(cy)
            L.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="13" fill="#5f6873" text-anchor="middle" dominant-baseline="middle" font-family="JetBrains Mono, monospace">{ab["id"]}</text>')
    # portas de abrir
    for pid, g in GIROS.items():
        hx, hy = g["hinge"]
        r = g["larg"]
        a0, a1 = math.radians(g["a0"]), math.radians(g["a1"])
        p0 = (hx + r * math.cos(a0), hy + r * math.sin(a0))
        p1 = (hx + r * math.cos(a1), hy + r * math.sin(a1))
        sweep = 0 if (g["a1"] - g["a0"]) > 0 else 1   # eixo y do SVG é invertido
        L.append(f'<line x1="{X(hx):.1f}" y1="{Y(hy):.1f}" x2="{X(p1[0]):.1f}" y2="{Y(p1[1]):.1f}" stroke="{INK}" stroke-width="3"/>')
        L.append(f'<path d="M {X(p0[0]):.1f} {Y(p0[1]):.1f} A {r * S:.1f} {r * S:.1f} 0 0 {sweep} {X(p1[0]):.1f} {Y(p1[1]):.1f}" fill="none" stroke="#7b848d" stroke-width="1.4" stroke-dasharray="4 3"/>')
    # guarda-corpo da varanda
    va = PLANTA["varanda"]
    L.append(f'<polyline points="{X(va["x1"]):.1f},{Y(0):.1f} {X(va["x1"]):.1f},{Y(va["y1"]):.1f} {X(va["x2"]):.1f},{Y(va["y1"]):.1f} {X(va["x2"]):.1f},{Y(0):.1f}" fill="none" stroke="#6aa0b8" stroke-width="5"/>')
    # móveis
    if com_moveis:
        for mv in sorted(MOVEIS, key=lambda q: (q["tipo"] != "tapete", q["z"])):
            L.append(f'<g transform="translate({X(mv["cx"]):.1f},{Y(mv["cy"]):.1f}) scale({S},{-S}) rotate({mv["rot"]})">{icone(mv)}</g>')
    # marca o defeito da 1ª proposta (mesa de apoio em frente à porta da suíte)
    if com_moveis and PRIMEIRA_PROPOSTA:
        a = next(x for x in MOVEIS if x["id"] == "apoio1")
        L.append(f'<circle cx="{X(a["cx"]):.1f}" cy="{Y(a["cy"]):.1f}" r="46" fill="none" stroke="#c9553a" stroke-width="4" stroke-dasharray="9 6"/>')
        L.append(f'<rect x="{X(a["cx"]) + 54:.1f}" y="{Y(a["cy"]) - 22:.1f}" width="236" height="44" rx="8" fill="#fbeee8" stroke="#c9553a" stroke-width="2"/>')
        L.append(f'<text x="{X(a["cx"]) + 172:.1f}" y="{Y(a["cy"]) + 6:.1f}" font-size="17" font-weight="700" fill="#a94a2d" text-anchor="middle">gargalo 0,60 m</text>')
    # nomes e áreas
    for a in PLANTA["ambientes"]:
        p = Polygon(a["poly"])
        cx, cy = p.centroid.coords[0]
        ajuste = {"sala_cozinha": (5.0, 0.95), "suite": (1.8, 5.1), "banho_suite": (4.5, 6.3), "banho_social": (6.0, 6.55), "home_office": (8.95, 5.2), "varanda": (4.35, -0.5)}[a["id"]]
        linhas = a["nome"].upper().split(" ", 1) if a["id"].startswith("banho") else [a["nome"].upper()]
        yy = Y(ajuste[1])
        for ln in linhas:
            L.append(f'<text x="{X(ajuste[0]):.1f}" y="{yy:.1f}" font-size="15" font-weight="600" fill="{INK}" text-anchor="middle" letter-spacing=".5">{ln}</text>')
            yy += 18
        L.append(f'<text x="{X(ajuste[0]):.1f}" y="{yy + 1:.1f}" font-size="14" fill="#5f6873" text-anchor="middle" font-family="JetBrains Mono, monospace">{f2(p.area)} m²</text>')
    # cotas gerais
    yb = Y(-2.2)
    L.append(f'<line x1="{X(0):.1f}" y1="{yb:.1f}" x2="{X(10):.1f}" y2="{yb:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    for xx in (0, 10):
        L.append(f'<line x1="{X(xx):.1f}" y1="{yb - 6:.1f}" x2="{X(xx):.1f}" y2="{yb + 6:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    L.append(f'<text x="{X(5):.1f}" y="{yb + 20:.1f}" font-size="14" text-anchor="middle" fill="{INK}" font-family="JetBrains Mono, monospace">10,00 m</text>')
    xr = X(10.95)
    L.append(f'<line x1="{xr:.1f}" y1="{Y(0):.1f}" x2="{xr:.1f}" y2="{Y(8):.1f}" stroke="{INK}" stroke-width="1.2"/>')
    for yy in (0, 8):
        L.append(f'<line x1="{xr - 6:.1f}" y1="{Y(yy):.1f}" x2="{xr + 6:.1f}" y2="{Y(yy):.1f}" stroke="{INK}" stroke-width="1.2"/>')
    L.append(f'<text x="{xr + 16:.1f}" y="{Y(4):.1f}" font-size="14" text-anchor="middle" fill="{INK}" transform="rotate(-90 {xr + 16:.1f} {Y(4):.1f})" font-family="JetBrains Mono, monospace">8,00 m</text>')
    # norte e título
    nx, ny = X(10.2), Y(-1.7)
    L.append(f'<g transform="translate({nx:.1f},{ny:.1f})"><circle r="22" fill="none" stroke="{INK}" stroke-width="1.5"/><path d="M0 -17 L7 8 L0 3 L-7 8 Z" fill="{INK}"/><text y="-28" font-size="14" font-weight="700" text-anchor="middle" fill="{INK}">N</text></g>')
    titulo = "PLANTA MOBILIADA" if com_moveis else "PLANTA BASE"
    L.append(f'<text x="{MX}" y="{SVG_H - 34}" font-size="20" font-weight="700" fill="{INK}" letter-spacing="1">{PLANTA["projeto"].upper()} · {titulo}</text>')
    L.append(f'<text x="{MX}" y="{SVG_H - 12}" font-size="14" fill="#5f6873" font-family="JetBrains Mono, monospace">rascunho para validação · esc. 1:100 · dados fictícios · quem assina é a arquiteta</text>')
    L.append("</svg>")
    return "\n".join(L)


def relatorio(achados, gargalo):
    ok = [a for a in achados if a[0] == "ok"]
    at = [a for a in achados if a[0] == "atencao"]
    L = [f"# Relatório de validação — {PLANTA['projeto']}", "",
         f"Móveis: {len(MOVEIS)} · Verificações: {len(achados)} · OK: {len(ok)} · **Precisa de decisão humana: {len(at)}**", ""]
    if at:
        L += ["## Precisa de você", ""] + [f"- **{t}** — {d}" for _, t, d in at] + [""]
    L += ["## Conferido", ""] + [f"- ✅ {t} — {d}" for _, t, d in ok]
    L += ["", "> Validação determinística (geometria). Não substitui a análise da arquiteta responsável."]
    return re.sub(r"(\d)\.(\d)", r"\1,\2", "\n".join(L)) + "\n"


def exportar_layout():
    saida = {"projeto": PLANTA["projeto"], "pe_direito": H, "moveis": [{k: v for k, v in mv.items() if not k.startswith("_")} for mv in MOVEIS]}
    (SAIDA / "layout.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    achados, gargalo, _ = validar()
    sufixo = "-v1" if PRIMEIRA_PROPOSTA else ""
    if not PRIMEIRA_PROPOSTA:
        (SAIDA / "planta-base.svg").write_text(desenhar_svg(False), encoding="utf-8")
        exportar_layout()
    (SAIDA / f"planta-mobiliada{sufixo}.svg").write_text(desenhar_svg(True, achados, gargalo), encoding="utf-8")
    (SAIDA / f"relatorio-validacao{sufixo}.md").write_text(relatorio(achados, gargalo), encoding="utf-8")
    print(relatorio(achados, gargalo))
