"""Casa térrea com terraço coberto e jardim, gerada por script no FreeCAD.

É o tipo de script que a IA escreve para você (skill apoio-cad):
- paredes com vãos de porta, janela e porta de correr;
- terraço coberto com deck de madeira, pergolado metálico com vidro e brise;
- jardim com pisantes e árvores;
- móveis montados por partes;
- desenho técnico na planta: cotas, códigos de esquadria (P01, S01, J01)
  e ambientes com nome e área calculada pelo FreeCAD.

Como rodar: no FreeCAD, Macro → Macros… → selecionar este arquivo → Executar
(ou, no console Python do FreeCAD: exec(open("freecad_apto.py").read())).
Testado no FreeCAD 26.3. Dados fictícios.
"""
import FreeCAD as App
import Part

V = App.Vector
MM = 1000.0                 # o FreeCAD trabalha em milímetros; aqui tudo é em metros
T, H = 0.15, 2.70           # espessura e altura das paredes

doc = App.newDocument("Casa")
CORES = {}                  # nome do objeto → (cor RGB, transparência 0–100)

# Paleta (vista 3D)
TERRACOTA, MADEIRA, MADEIRA_ESC = (0.72, 0.44, 0.32), (0.62, 0.45, 0.30), (0.45, 0.32, 0.22)
DECK, TECIDO, TECIDO_CLARO = (0.66, 0.42, 0.26), (0.30, 0.50, 0.53), (0.40, 0.60, 0.62)
BRANCO, PEDRA, INOX = (0.96, 0.96, 0.95), (0.55, 0.56, 0.57), (0.75, 0.77, 0.79)
PRETO, ACO, VIDRO = (0.12, 0.12, 0.13), (0.30, 0.32, 0.34), (0.62, 0.80, 0.90)
GRAMA, CONCRETO, FOLHA = (0.36, 0.55, 0.30), (0.78, 0.78, 0.76), (0.30, 0.48, 0.25)
TAPETE, LINHA = (0.82, 0.74, 0.62), (0.15, 0.16, 0.18)


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


# ================================================================ paredes
paredes = junta(
    caixa(-T/2, -T/2, 0, 9 + T/2, T/2, H), caixa(-T/2, 7 - T/2, 0, 9 + T/2, 7 + T/2, H),
    caixa(-T/2, -T/2, 0, T/2, 7 + T/2, H), caixa(9 - T/2, -T/2, 0, 9 + T/2, 7 + T/2, H),
    caixa(5.5 - T/2, 0, 0, 5.5 + T/2, 7, H),       # sala | quarto, serviço
    caixa(5.5, 3.0 - T/2, 0, 9, 3.0 + T/2, H),     # quarto | serviço, banho
    caixa(7.0 - T/2, 0, 0, 7.0 + T/2, 3.0, H))     # serviço | banho

# Esquadrias: código → (x1, y1, x2, y2, peitoril, altura, descrição)
ESQUADRIAS = {
    "P01": (2.0, -T, 2.9, T, 0, 2.10, "porta de entrada"),
    "S01": (3.3, -T, 5.1, T, 0, 2.20, "porta de correr para o terraço"),
    "P02": (5.5 - T, 1.0, 5.5 + T, 1.8, 0, 2.10, "sala → serviço"),
    "P03": (5.5 - T, 4.5, 5.5 + T, 5.3, 0, 2.10, "sala → quarto"),
    "P04": (7.0 - T, 1.0, 7.0 + T, 1.7, 0, 2.10, "serviço → banho"),
    "J01": (1.0, 7 - T, 2.2, 7 + T, 1.10, 1.00, "janela da cozinha"),
    "J02": (9 - T, 5.2, 9 + T, 6.6, 1.00, 1.20, "janela do quarto"),
    "J03": (9 - T, 1.4, 9 + T, 2.2, 1.60, 0.50, "basculante do banho"),
}
for x1, y1, x2, y2, z, h, _ in ESQUADRIAS.values():
    paredes = paredes.cut(caixa(x1, y1, z, x2, y2, z + h))
add("Paredes", paredes.removeSplitter(), TERRACOTA)

# Janelas: peitoril de pedra + caixilho + vidro
for cod in ("J01", "J02", "J03"):
    x1, y1, x2, y2, z, h, _ = ESQUADRIAS[cod]
    horizontal = x2 - x1 > y2 - y1
    if horizontal:
        ym = (y1 + y2) / 2
        add(f"Peitoril_{cod}", caixa(x1, ym - 0.10, z - 0.03, x2, ym + 0.10, z), BRANCO)
        add(f"Caixilho_{cod}", junta(caixa(x1, ym - 0.03, z, x2, ym + 0.03, z + 0.04),
                                     caixa(x1, ym - 0.03, z + h - 0.04, x2, ym + 0.03, z + h),
                                     caixa((x1 + x2) / 2 - 0.02, ym - 0.03, z, (x1 + x2) / 2 + 0.02, ym + 0.03, z + h)), ACO)
        add(f"Vidro_{cod}", caixa(x1, ym - 0.008, z, x2, ym + 0.008, z + h), VIDRO, 60)
    else:
        xm = (x1 + x2) / 2
        add(f"Peitoril_{cod}", caixa(xm - 0.10, y1, z - 0.03, xm + 0.10, y2, z), BRANCO)
        add(f"Caixilho_{cod}", junta(caixa(xm - 0.03, y1, z, xm + 0.03, y2, z + 0.04),
                                     caixa(xm - 0.03, y1, z + h - 0.04, xm + 0.03, y2, z + h),
                                     caixa(xm - 0.03, (y1 + y2) / 2 - 0.02, z, xm + 0.03, (y1 + y2) / 2 + 0.02, z + h)), ACO)
        add(f"Vidro_{cod}", caixa(xm - 0.008, y1, z, xm + 0.008, y2, z + h), VIDRO, 60)

# Porta de correr S01: duas folhas de vidro deslocadas
x1, _, x2, _, _, h, _ = ESQUADRIAS["S01"]
meio = (x1 + x2) / 2
add("Vidro_S01", junta(caixa(x1, -0.035, 0, meio + 0.05, -0.015, h), caixa(meio - 0.05, 0.015, 0, x2, 0.035, h)), VIDRO, 55)
add("Caixilho_S01", junta(caixa(x1, -0.04, 0, x1 + 0.05, 0.04, h), caixa(x2 - 0.05, -0.04, 0, x2, 0.04, h),
                          caixa(x1, -0.04, h - 0.05, x2, 0.04, h)), ACO)

# Portas de abrir: folha a 90° + arco de abertura (dobradiça x, y, largura, ângulo do arco, eixo)
FOLHAS = {"P01": (2.0, T/2, 0.9, 0, "y"), "P02": (5.5 + T/2, 1.0, 0.8, 0, "x"),
          "P03": (5.5 + T/2, 5.3, 0.8, 270, "x"), "P04": (7.0 + T/2, 1.7, 0.7, 270, "x")}
for cod, (hx, hy, w, ang, eixo) in FOLHAS.items():
    if eixo == "y":
        folha = caixa(hx, hy, 0, hx + 0.035, hy + w, 2.10)
    elif ang == 0:
        folha = caixa(hx, hy, 0, hx + w, hy + 0.035, 2.10)
    else:
        folha = caixa(hx, hy - 0.035, 0, hx + w, hy, 2.10)
    add(f"Porta_{cod}", folha, MADEIRA)
    add(f"Arco_{cod}", Part.makeCircle(w * MM, V(hx * MM, hy * MM, 5), V(0, 0, 1), ang, ang + 90), LINHA)

# ================================================================ pisos internos
AMBIENTES = {  # nome: (x1, y1, x2, y2, cor, rótulo)
    "Sala_Cozinha": (0, 0, 5.5, 7.0, (0.86, 0.78, 0.64), "SALA / COZINHA"),
    "Quarto": (5.5, 3.0, 9.0, 7.0, (0.80, 0.70, 0.56), "QUARTO"),
    "Servico": (5.5, 0, 7.0, 3.0, (0.84, 0.85, 0.86), "SERVIÇO"),
    "Banheiro": (7.0, 0, 9.0, 3.0, (0.82, 0.88, 0.92), "BANHO"),
}
for nome, (x1, y1, x2, y2, cor, _) in AMBIENTES.items():
    add(f"Piso_{nome}", caixa(x1, y1, -0.05, x2, y2, 0), cor)

# ================================================================ terraço coberto
TERRACO = (0.3, -3.0, 9.0, -T/2)
x1, y1, x2, y2 = TERRACO
add("Piso_Terraco", caixa(x1, y1, -0.08, x2, y2, -0.04), CONCRETO)
tabuas, y = [], y1
while y + 0.14 <= y2 + 0.001:          # deck: tábuas de 14 cm com junta de 1 cm
    tabuas.append(caixa(x1, y, -0.04, x2, y + 0.14, 0))
    y += 0.15
add("Deck", Part.makeCompound(tabuas), DECK)
# pergolado metálico com cobertura de vidro
pilares = [caixa(x - 0.05, -2.95, 0, x + 0.05, -2.85, 2.70) for x in (0.4, 4.65, 8.9)]
viga = caixa(0.3, -2.97, 2.58, 9.0, -2.83, 2.74)
caibros = [caixa(x - 0.03, -3.0, 2.62, x + 0.03, 0, 2.74) for x in (0.4, 1.45, 2.5, 3.55, 4.6, 5.65, 6.7, 7.75, 8.8)]
add("Pilares", Part.makeCompound(pilares), ACO)
add("Pergolado", Part.makeCompound([viga] + caibros), ACO)
add("Cobertura_vidro", caixa(0.3, -3.05, 2.74, 9.0, 0, 2.76), VIDRO, 85)
# brise de madeira na lateral leste do terraço
brises = [caixa(8.86, y, 0, 8.94, y + 0.05, 2.58) for y in [-2.85 + 0.12 * k for k in range(24)]]
add("Brise", Part.makeCompound(brises), MADEIRA)
# mobiliário externo
add("Espreguicadeira", junta(caixa(1.0, -2.5, 0.15, 1.65, -0.9, 0.30), caixa(1.0, -1.15, 0.30, 1.65, -0.9, 0.75)), MADEIRA_ESC)
add("Mesa_externa", junta(cilindro(6.6, -1.5, 0.70, 0.45, 0.04), cilindro(6.6, -1.5, 0, 0.05, 0.70)), ACO)
for k, (cx, cy) in enumerate([(5.9, -1.5), (7.3, -1.5), (6.6, -2.25)]):
    add(f"Banqueta_{k}", cilindro(cx, cy, 0, 0.2, 0.45), MADEIRA)

# ================================================================ jardim
add("Grama", caixa(-1.0, -7.0, -0.10, 10.0, -3.0, -0.05), GRAMA)
add("Pisantes", Part.makeCompound([caixa(2.2, y, -0.05, 2.8, y + 0.45, -0.02) for y in (-3.75, -4.5, -5.25, -6.0, -6.75)]), CONCRETO)
for k, (tx, ty) in enumerate([(0.6, -5.4), (7.8, -5.0)]):
    add(f"Tronco_{k}", cilindro(tx, ty, -0.05, 0.12, 2.2), MADEIRA_ESC)
    bolas = [(0, 0, 3.0, 0.95), (0.55, 0.25, 2.75, 0.7), (-0.5, 0.3, 2.8, 0.72), (0.2, -0.55, 2.7, 0.7),
             (-0.3, -0.4, 3.35, 0.65), (0.35, 0.3, 3.45, 0.6)]
    add(f"Copa_{k}", junta(*[Part.makeSphere(r * MM, V((tx + dx) * MM, (ty + dy) * MM, z * MM)) for dx, dy, z, r in bolas]), FOLHA)
    # símbolo de árvore para a planta (copa + tronco em traço)
    add(f"Arco_arvore_{k}", Part.makeCompound([Part.makeCircle(r * MM, V(tx * MM, ty * MM, 10)) for r in (1.25, 1.1, 0.12)]), LINHA)

# ================================================================ sala
add("Tapete", caixa(1.3, 0.9, 0, 3.1, 2.5, 0.01), TAPETE)
add("Sofa_base", junta(caixa(0.10, 0.60, 0.10, 1.00, 2.80, 0.42), caixa(0.10, 0.60, 0.42, 0.32, 2.80, 0.86),
                       caixa(0.10, 0.60, 0.10, 1.00, 0.80, 0.62), caixa(0.10, 2.60, 0.10, 1.00, 2.80, 0.62)), TECIDO)
add("Sofa_almofadas", junta(caixa(0.32, 0.81, 0.42, 0.98, 1.69, 0.54), caixa(0.32, 1.71, 0.42, 0.98, 2.59, 0.54)), TECIDO_CLARO)
add("Mesa_centro", junta(caixa(1.6, 1.3, 0.38, 2.4, 2.1, 0.42),
                         *[caixa(x, y, 0, x + 0.04, y + 0.04, 0.38) for x in (1.63, 2.33) for y in (1.33, 2.03)]), MADEIRA)
add("Rack", caixa(4.95, 1.9, 0.10, 5.40, 3.7, 0.50), MADEIRA)
add("TV", caixa(5.36, 2.25, 0.75, 5.40, 3.35, 1.38), PRETO)
add("Mesa_jantar", junta(caixa(1.5, 4.3, 0.72, 3.1, 5.2, 0.76),
                         *[caixa(x, y, 0, x + 0.06, y + 0.06, 0.72) for x in (1.56, 2.98) for y in (4.36, 5.08)]), MADEIRA)
for k, (x, y, ey) in enumerate([(1.70, 3.75, 3.75), (2.45, 3.75, 3.75), (1.70, 5.30, 5.72), (2.45, 5.30, 5.72)]):
    pes = [caixa(px, py, 0, px + 0.03, py + 0.03, 0.43) for px in (x + 0.02, x + 0.40) for py in (y + 0.02, y + 0.40)]
    add(f"Cadeira_{k}", junta(caixa(x, y, 0.43, x + 0.45, y + 0.45, 0.47), caixa(x, ey, 0.47, x + 0.45, ey + 0.03, 0.92), *pes), MADEIRA_ESC)

# cozinha
add("Cozinha_armarios", junta(caixa(0.10, 6.30, 0.10, 3.60, 6.88, 0.86), caixa(0.12, 6.32, 0, 3.58, 6.82, 0.10)), BRANCO)
add("Cozinha_tampo", caixa(0.10, 6.28, 0.86, 3.60, 6.90, 0.90).cut(caixa(1.25, 6.40, 0.72, 1.85, 6.78, 0.90)), PEDRA)
add("Cuba_torneira", junta(caixa(1.25, 6.40, 0.72, 1.85, 6.78, 0.73), cilindro(1.55, 6.82, 0.90, 0.015, 0.30),
                           cilindro(1.55, 6.82, 1.18, 0.012, 0.18, V(0, -1, 0))), INOX)
add("Cooktop", caixa(2.45, 6.40, 0.90, 3.15, 6.84, 0.91), PRETO)
add("Bocas", junta(*[cilindro(x, y, 0.91, 0.07, 0.012) for x in (2.65, 2.95) for y in (6.52, 6.72)]), PEDRA)
add("Armario_aereo", caixa(2.30, 6.55, 1.50, 3.60, 6.88, 2.20), BRANCO)
add("Geladeira", caixa(3.70, 6.25, 0, 4.40, 6.90, 1.80), INOX)
add("Geladeira_detalhes", junta(caixa(3.70, 6.235, 1.18, 4.40, 6.25, 1.20), caixa(4.30, 6.21, 1.25, 4.33, 6.24, 1.65),
                                caixa(4.30, 6.21, 0.80, 4.33, 6.24, 1.10)), PRETO)

# ================================================================ quarto
add("Cama_estrutura", caixa(7.00, 4.30, 0.10, 8.85, 5.70, 0.35), MADEIRA)
add("Cabeceira", caixa(8.85, 4.25, 0, 8.92, 5.75, 1.10), MADEIRA_ESC)
add("Colchao", caixa(7.05, 4.35, 0.35, 8.80, 5.65, 0.55), BRANCO)
add("Edredom", caixa(7.03, 4.33, 0.55, 8.15, 5.67, 0.60), TECIDO)
add("Travesseiros", junta(caixa(8.30, 4.45, 0.55, 8.72, 4.95, 0.66), caixa(8.30, 5.05, 0.55, 8.72, 5.55, 0.66)), (0.93, 0.92, 0.88))
for k, y in enumerate((3.78, 5.77)):
    add(f"Criado_{k}", caixa(8.45, y, 0, 8.92, y + 0.45, 0.55), MADEIRA)
    add(f"Abajur_{k}", junta(cilindro(8.68, y + 0.22, 0.55, 0.05, 0.25), cilindro(8.68, y + 0.22, 0.80, 0.12, 0.18)), (0.95, 0.90, 0.78))
add("Guarda_roupa", caixa(6.20, 6.30, 0, 8.70, 6.90, 2.10), BRANCO)
add("Guarda_roupa_portas", junta(*[caixa(x - 0.004, 6.29, 0.05, x + 0.004, 6.30, 2.05) for x in (6.825, 7.45, 8.075)],
                                 *[caixa(x, 6.27, 0.95, x + 0.02, 6.30, 1.25) for x in (6.79, 6.85, 7.415, 7.475, 8.04, 8.10)]), LINHA)

# ================================================================ serviço e banheiro
add("Lavadora", caixa(5.60, 2.30, 0, 6.20, 2.90, 0.85), BRANCO)
add("Lavadora_porta", cilindro(5.90, 2.30, 0.42, 0.20, 0.02, V(0, -1, 0)), INOX)
add("Tanque", caixa(6.30, 2.35, 0, 6.90, 2.90, 0.90).cut(caixa(6.38, 2.43, 0.65, 6.82, 2.82, 0.90)), BRANCO)
add("Box_piso", caixa(7.90, 0.10, 0, 8.90, 1.10, 0.05), BRANCO)
add("Box_vidro", caixa(7.88, 0.10, 0.05, 7.90, 1.10, 2.00), VIDRO, 60)
add("Chuveiro", junta(cilindro(8.85, 0.60, 1.95, 0.012, 0.15, V(-1, 0, 0)), cilindro(8.70, 0.60, 1.90, 0.10, 0.03)), INOX)
vaso = junta(cilindro(8.50, 1.85, 0, 0.17, 0.40), caixa(8.72, 1.65, 0.40, 8.92, 2.05, 0.80), caixa(8.50, 1.68, 0, 8.72, 2.02, 0.40))
add("Vaso", vaso.cut(cilindro(8.50, 1.85, 0.25, 0.12, 0.20)), BRANCO)
add("Gabinete_pia", caixa(7.30, 2.45, 0.10, 8.20, 2.92, 0.80), MADEIRA)
add("Pia", caixa(7.28, 2.43, 0.80, 8.22, 2.94, 0.84).cut(cilindro(7.75, 2.68, 0.72, 0.17, 0.15)), BRANCO)
add("Espelho", caixa(7.40, 2.915, 1.15, 8.10, 2.925, 1.90), VIDRO, 30)

doc.recompute()

# ================================================================ desenho técnico (anotações)
import Draft  # noqa: E402

AREAS = {nome: doc.getObject(f"Piso_{nome}").Shape.Volume / (0.05 * MM) / (MM * MM) for nome in AMBIENTES}
AREAS["Terraco"] = (TERRACO[2] - TERRACO[0]) * (TERRACO[3] - TERRACO[1])
ANOTACOES = []


def m2(v):
    return f"{v:.2f}".replace(".", ",") + " m²"


def texto(linhas, x, y, tam=0.30):
    t = Draft.make_text(linhas, V(x * MM, y * MM, 3.0 * MM))
    ANOTACOES.append((t, tam))
    return t


def cota(x1, y1, x2, y2, deslocamento, rotulo=None):
    """Cota linear entre dois pontos; 'deslocamento' afasta a linha de cota (m)."""
    if y1 == y2:
        d = Draft.make_linear_dimension(V(x1 * MM, y1 * MM, 3000), V(x2 * MM, y2 * MM, 3000),
                                        V((x1 + x2) / 2 * MM, (y1 + deslocamento) * MM, 3000))
    else:
        d = Draft.make_linear_dimension(V(x1 * MM, y1 * MM, 3000), V(x2 * MM, y2 * MM, 3000),
                                        V((x1 + deslocamento) * MM, (y1 + y2) / 2 * MM, 3000))
    ANOTACOES.append((d, rotulo))
    return d


# ambientes: nome + área
ROTULOS = {"Sala_Cozinha": (3.55, 3.15), "Quarto": (6.4, 3.6), "Servico": (6.25, 0.45), "Banheiro": (7.5, 0.45)}
for nome, (x, y) in ROTULOS.items():
    texto([AMBIENTES[nome][5], m2(AREAS[nome])], x, y, 0.26 if nome in ("Servico", "Banheiro") else 0.30)
texto(["TERRAÇO COBERTO", m2(AREAS["Terraco"])], 6.6, -0.75)
texto(["JARDIM"], 5.2, -5.2)
# códigos das esquadrias
for cod, (x, y) in {"P01": (2.45, -0.35), "S01": (4.2, -0.35), "P02": (5.15, 1.4), "P03": (5.15, 4.9),
                    "P04": (7.45, 2.05), "J01": (1.6, 7.45), "J02": (9.45, 5.9), "J03": (9.45, 1.8)}.items():
    texto([cod], x, y, 0.22)
# cotas: cadeia externa sul, totais e internas
for a, b, r in [(0, 2.0, None), (2.0, 2.9, "0,90/2,10"), (3.3, 5.1, "1,80/2,20"), (5.1, 9.0, None)]:
    cota(a, 0, b, 0, -3.45, r)
cota(0, 7, 9, 7, 0.9)
cota(-0.075, 0, -0.075, 7, -0.9)
cota(9.075, 0, 9.075, 3.0, 0.9)
cota(9.075, 3.0, 9.075, 7.0, 0.9)

if App.GuiUp:
    import FreeCADGui as Gui
    for nome, (cor, transp) in CORES.items():
        vo = Gui.ActiveDocument.getObject(nome)
        if nome.startswith("Arco_"):
            vo.LineColor, vo.LineWidth = cor, 1.5
        else:
            vo.ShapeColor, vo.Transparency = cor, transp
    for obj, extra in ANOTACOES:
        vo = obj.ViewObject
        for prop, val in (("FontName", "osifont"), ("TextColor", (0.1, 0.1, 0.1)), ("LineColor", (0.1, 0.1, 0.1))):
            if hasattr(vo, prop):
                setattr(vo, prop, val)
        if obj.TypeId.startswith("App::FeaturePython") and hasattr(obj, "Text"):
            vo.FontSize = (extra or 0.22) * MM
            vo.Justification = "Center"
        else:   # cota
            for prop, val in (("FontSize", 230), ("ArrowSize", 70), ("ArrowType", "Tick"), ("Decimals", 2),
                              ("ShowUnit", False), ("UnitOverride", "m"), ("ExtLines", 0), ("ExtOvershoot", 80),
                              ("DimOvershoot", 80), ("TextSpacing", 40)):
                if hasattr(vo, prop):
                    try:
                        setattr(vo, prop, val)
                    except Exception:
                        pass
            if extra and hasattr(vo, "Override"):
                vo.Override = extra
    Gui.SendMsgToActiveView("ViewFit")
    Gui.activeDocument().activeView().viewIsometric()

print("Áreas calculadas pelo FreeCAD:")
for nome, area in AREAS.items():
    print(f"  {nome.replace('_', ' / '):16s} {m2(area)}")
