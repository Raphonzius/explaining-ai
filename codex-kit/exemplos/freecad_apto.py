"""Planta de um apartamento (9 × 7 m) com mobiliário, gerada por script no FreeCAD.

É o tipo de script que a IA escreve para você (skill apoio-cad): paredes com
vãos de porta e janela, portas com arco de abertura, pisos por ambiente e
móveis montados por partes. As áreas são calculadas pelo próprio FreeCAD.

Como rodar: no FreeCAD, Macro → Macros… → selecionar este arquivo → Executar
(ou, no console Python do FreeCAD: exec(open("freecad_apto.py").read())).
Testado no FreeCAD 26.3. Dados fictícios.
"""
import math

import FreeCAD as App
import Part

V = App.Vector
MM = 1000.0                 # o FreeCAD trabalha em milímetros; aqui tudo é em metros
T, H = 0.15, 2.70           # espessura e altura das paredes

doc = App.newDocument("Apartamento")
CORES = {}                  # nome do objeto → (cor RGB, transparência 0–100)

# Paleta
MADEIRA, MADEIRA_ESC = (0.62, 0.45, 0.30), (0.45, 0.32, 0.22)
TECIDO, TECIDO_CLARO = (0.30, 0.50, 0.53), (0.40, 0.60, 0.62)
BRANCO, PEDRA, INOX = (0.96, 0.96, 0.95), (0.55, 0.56, 0.57), (0.75, 0.77, 0.79)
PRETO, VIDRO, TAPETE = (0.12, 0.12, 0.13), (0.62, 0.80, 0.90), (0.82, 0.74, 0.62)
LINHA = (0.20, 0.22, 0.25)


def caixa(x1, y1, z1, x2, y2, z2):
    """Bloco entre dois cantos (em metros)."""
    return Part.makeBox((x2 - x1) * MM, (y2 - y1) * MM, (z2 - z1) * MM, V(x1 * MM, y1 * MM, z1 * MM))


def cilindro(x, y, z, r, h, direcao=V(0, 0, 1)):
    return Part.makeCylinder(r * MM, h * MM, V(x * MM, y * MM, z * MM), direcao)


def add(nome, forma, cor, transp=0):
    obj = doc.addObject("Part::Feature", nome)
    obj.Shape = forma
    CORES[nome] = (cor, transp)
    return obj


def junta(*formas):
    return formas[0].fuse(list(formas[1:])).removeSplitter() if len(formas) > 1 else formas[0]


# ---------------------------------------------------------------- paredes
externas = [caixa(-T/2, -T/2, 0, 9 + T/2, T/2, H), caixa(-T/2, 7 - T/2, 0, 9 + T/2, 7 + T/2, H),
            caixa(-T/2, -T/2, 0, T/2, 7 + T/2, H), caixa(9 - T/2, -T/2, 0, 9 + T/2, 7 + T/2, H)]
internas = [caixa(5.5 - T/2, 0, 0, 5.5 + T/2, 7, H),      # sala | quarto, serviço
            caixa(5.5, 3.0 - T/2, 0, 9, 3.0 + T/2, H),    # quarto | serviço, banho
            caixa(7.0 - T/2, 0, 0, 7.0 + T/2, 3.0, H)]    # serviço | banho
paredes = junta(*externas, *internas)

PORTAS = {  # nome: (x1, y1, x2, y2) do vão, altura 2,10 m
    "entrada": (2.0, -T, 2.9, T), "sala_servico": (5.5 - T, 1.0, 5.5 + T, 1.8),
    "sala_quarto": (5.5 - T, 4.5, 5.5 + T, 5.3), "servico_banho": (7.0 - T, 1.0, 7.0 + T, 1.7),
}
JANELAS = {  # nome: (x1, y1, x2, y2, peitoril, topo)
    "sala": (3.4, -T, 5.0, T, 1.0, 2.2), "cozinha": (1.0, 7 - T, 2.2, 7 + T, 1.1, 2.1),
    "quarto": (9 - T, 5.2, 9 + T, 6.6, 1.0, 2.2), "banho": (9 - T, 1.4, 9 + T, 2.2, 1.6, 2.1),
}
for x1, y1, x2, y2 in PORTAS.values():
    paredes = paredes.cut(caixa(x1, y1, 0, x2, y2, 2.10))
for x1, y1, x2, y2, z1, z2 in JANELAS.values():
    paredes = paredes.cut(caixa(x1, y1, z1, x2, y2, z2))
add("Paredes", paredes.removeSplitter(), (0.93, 0.93, 0.91))

# vidros das janelas
for nome, (x1, y1, x2, y2, z1, z2) in JANELAS.items():
    if x2 - x1 > y2 - y1:      # janela em parede horizontal
        ym = (y1 + y2) / 2
        add(f"Vidro_{nome}", caixa(x1, ym - 0.01, z1, x2, ym + 0.01, z2), VIDRO, 60)
    else:
        xm = (x1 + x2) / 2
        add(f"Vidro_{nome}", caixa(xm - 0.01, y1, z1, xm + 0.01, y2, z2), VIDRO, 60)

# folhas de porta (abertas a 90°) e arco de abertura na planta
FOLHAS = [  # (dobradiça x, y, largura, ângulo inicial do arco, sentido da folha)
    (2.0, T/2, 0.9, 0, "y"), (5.5 + T/2, 1.0, 0.8, 0, "x"),
    (5.5 + T/2, 5.3, 0.8, 270, "x"), (7.0 + T/2, 1.7, 0.7, 270, "x"),
]
for k, (hx, hy, w, ang, eixo) in enumerate(FOLHAS):
    sinal = 1 if ang == 0 else -1
    if eixo == "y":
        folha = caixa(hx, hy, 0, hx + 0.035, hy + w, 2.10)
    else:
        folha = caixa(hx, hy if sinal > 0 else hy - 0.035, 0, hx + w, hy + 0.035 if sinal > 0 else hy, 2.10)
    add(f"Porta_{k}", folha, MADEIRA)
    arco = Part.makeCircle(w * MM, V(hx * MM, hy * MM, 5), V(0, 0, 1), ang, ang + 90)
    add(f"Arco_{k}", arco, LINHA)

# ---------------------------------------------------------------- pisos
AMBIENTES = {
    "Sala_Cozinha": (0, 0, 5.5, 7.0, (0.86, 0.78, 0.64)),
    "Quarto": (5.5, 3.0, 9.0, 7.0, (0.80, 0.70, 0.56)),
    "Servico": (5.5, 0, 7.0, 3.0, (0.84, 0.85, 0.86)),
    "Banheiro": (7.0, 0, 9.0, 3.0, (0.82, 0.88, 0.92)),
}
for nome, (x1, y1, x2, y2, cor) in AMBIENTES.items():
    add(f"Piso_{nome}", caixa(x1, y1, -0.05, x2, y2, 0), cor)

# ---------------------------------------------------------------- sala
add("Tapete", caixa(1.3, 0.9, 0, 3.1, 2.5, 0.01), TAPETE)
add("Sofa_base", junta(caixa(0.10, 0.60, 0.10, 1.00, 2.80, 0.42),                 # assento
                       caixa(0.10, 0.60, 0.42, 0.32, 2.80, 0.86),                 # encosto
                       caixa(0.10, 0.60, 0.10, 1.00, 0.80, 0.62),                 # braço
                       caixa(0.10, 2.60, 0.10, 1.00, 2.80, 0.62)), TECIDO)        # braço
add("Sofa_almofadas", junta(caixa(0.32, 0.81, 0.42, 0.98, 1.69, 0.54),
                            caixa(0.32, 1.71, 0.42, 0.98, 2.59, 0.54)), TECIDO_CLARO)
add("Sofa_pes", junta(*[caixa(x, y, 0, x + 0.05, y + 0.05, 0.10)
                        for x in (0.12, 0.93) for y in (0.62, 2.73)]), MADEIRA_ESC)
add("Mesa_centro", junta(caixa(1.6, 1.3, 0.38, 2.4, 2.1, 0.42),
                         *[caixa(x, y, 0, x + 0.04, y + 0.04, 0.38) for x in (1.63, 2.33) for y in (1.33, 2.03)]),
    MADEIRA)
add("Rack", caixa(4.95, 1.9, 0.10, 5.40, 3.7, 0.50), MADEIRA)
add("TV", caixa(5.36, 2.25, 0.75, 5.40, 3.35, 1.38), PRETO)

# jantar
add("Mesa_jantar", junta(caixa(1.5, 4.3, 0.72, 3.1, 5.2, 0.76),
                         *[caixa(x, y, 0, x + 0.06, y + 0.06, 0.72) for x in (1.56, 2.98) for y in (4.36, 5.08)]),
    MADEIRA)
for k, (x, y, encosto_y) in enumerate([(1.70, 3.75, 3.75), (2.45, 3.75, 3.75), (1.70, 5.30, 5.72), (2.45, 5.30, 5.72)]):
    pes = [caixa(px, py, 0, px + 0.03, py + 0.03, 0.43) for px in (x + 0.02, x + 0.40) for py in (y + 0.02, y + 0.40)]
    add(f"Cadeira_{k}", junta(caixa(x, y, 0.43, x + 0.45, y + 0.45, 0.47),
                              caixa(x, encosto_y, 0.47, x + 0.45, encosto_y + 0.03, 0.92), *pes), MADEIRA_ESC)

# cozinha
bancada = junta(caixa(0.10, 6.30, 0.10, 3.60, 6.88, 0.86), caixa(0.12, 6.32, 0, 3.58, 6.82, 0.10))
add("Cozinha_armarios", bancada, BRANCO)
tampo = caixa(0.10, 6.28, 0.86, 3.60, 6.90, 0.90).cut(caixa(1.25, 6.40, 0.72, 1.85, 6.78, 0.90))
add("Cozinha_tampo", tampo, PEDRA)
add("Cuba_torneira", junta(caixa(1.25, 6.40, 0.72, 1.85, 6.78, 0.73),
                           cilindro(1.55, 6.82, 0.90, 0.015, 0.30),
                           cilindro(1.55, 6.82, 1.18, 0.012, 0.18, V(0, -1, 0))), INOX)
add("Cooktop", caixa(2.45, 6.40, 0.90, 3.15, 6.84, 0.91), PRETO)
add("Bocas", junta(*[cilindro(x, y, 0.91, 0.07, 0.012) for x in (2.65, 2.95) for y in (6.52, 6.72)]), PEDRA)
add("Armario_aereo", caixa(2.30, 6.55, 1.50, 3.60, 6.88, 2.20), BRANCO)
add("Geladeira", caixa(3.70, 6.25, 0, 4.40, 6.90, 1.80), INOX)
add("Geladeira_detalhes", junta(caixa(3.70, 6.235, 1.18, 4.40, 6.25, 1.20),
                                caixa(4.30, 6.21, 1.25, 4.33, 6.24, 1.65),
                                caixa(4.30, 6.21, 0.80, 4.33, 6.24, 1.10)), PRETO)

# ---------------------------------------------------------------- quarto
add("Cama_estrutura", caixa(7.00, 4.30, 0.10, 8.85, 5.70, 0.35), MADEIRA)
add("Cabeceira", caixa(8.85, 4.25, 0, 8.92, 5.75, 1.10), MADEIRA_ESC)
add("Colchao", caixa(7.05, 4.35, 0.35, 8.80, 5.65, 0.55), BRANCO)
add("Edredom", caixa(7.03, 4.33, 0.55, 8.15, 5.67, 0.60), TECIDO)
add("Travesseiros", junta(caixa(8.30, 4.45, 0.55, 8.72, 4.95, 0.66),
                          caixa(8.30, 5.05, 0.55, 8.72, 5.55, 0.66)), (0.93, 0.92, 0.88))
for k, y in enumerate((3.78, 5.77)):
    add(f"Criado_{k}", caixa(8.45, y, 0, 8.92, y + 0.45, 0.55), MADEIRA)
    add(f"Abajur_{k}", junta(cilindro(8.68, y + 0.22, 0.55, 0.05, 0.25),
                             cilindro(8.68, y + 0.22, 0.80, 0.12, 0.18)), (0.95, 0.90, 0.78))
guarda = caixa(6.20, 6.30, 0, 8.70, 6.90, 2.10)
add("Guarda_roupa", guarda, BRANCO)
frisos = [caixa(x - 0.004, 6.29, 0.05, x + 0.004, 6.30, 2.05) for x in (6.825, 7.45, 8.075)]
puxadores = [caixa(x, 6.27, 0.95, x + 0.02, 6.30, 1.25) for x in (6.79, 6.85, 7.415, 7.475, 8.04, 8.10)]
add("Guarda_roupa_portas", junta(*frisos, *puxadores), LINHA)

# ---------------------------------------------------------------- serviço
add("Lavadora", caixa(5.60, 2.30, 0, 6.20, 2.90, 0.85), BRANCO)
add("Lavadora_porta", cilindro(5.90, 2.30, 0.42, 0.20, 0.02, V(0, -1, 0)), INOX)
tanque = caixa(6.30, 2.35, 0, 6.90, 2.90, 0.90).cut(caixa(6.38, 2.43, 0.65, 6.82, 2.82, 0.90))
add("Tanque", tanque, BRANCO)

# ---------------------------------------------------------------- banheiro
add("Box_piso", caixa(7.90, 0.10, 0, 8.90, 1.10, 0.05), BRANCO)
add("Box_vidro", caixa(7.88, 0.10, 0.05, 7.90, 1.10, 2.00), VIDRO, 60)
add("Chuveiro", junta(cilindro(8.85, 0.60, 1.95, 0.012, 0.15, V(-1, 0, 0)),
                      cilindro(8.70, 0.60, 1.90, 0.10, 0.03)), INOX)
vaso = junta(cilindro(8.50, 1.85, 0, 0.17, 0.40), caixa(8.72, 1.65, 0.40, 8.92, 2.05, 0.80),
             caixa(8.50, 1.68, 0, 8.72, 2.02, 0.40))
vaso = vaso.cut(cilindro(8.50, 1.85, 0.25, 0.12, 0.20))
add("Vaso", vaso, BRANCO)
add("Gabinete_pia", caixa(7.30, 2.45, 0.10, 8.20, 2.92, 0.80), MADEIRA)
pia = caixa(7.28, 2.43, 0.80, 8.22, 2.94, 0.84).cut(cilindro(7.75, 2.68, 0.72, 0.17, 0.15))
add("Pia", pia, BRANCO)
add("Espelho", caixa(7.40, 2.915, 1.15, 8.10, 2.925, 1.90), VIDRO, 30)

doc.recompute()

print("Áreas calculadas pelo FreeCAD:")
for nome in AMBIENTES:
    area = doc.getObject(f"Piso_{nome}").Shape.Volume / (0.05 * MM) / (MM * MM)
    print(f"  {nome.replace('_', ' / '):16s} {area:6.2f} m²")

if App.GuiUp:
    import FreeCADGui as Gui
    for nome, (cor, transp) in CORES.items():
        vo = Gui.ActiveDocument.getObject(nome)
        if nome.startswith("Arco_"):
            vo.LineColor, vo.LineWidth = cor, 1.5
        else:
            vo.ShapeColor, vo.Transparency = cor, transp
    Gui.SendMsgToActiveView("ViewFit")
    Gui.activeDocument().activeView().viewIsometric()
