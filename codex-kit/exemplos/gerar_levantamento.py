"""Gera saida/levantamento.xlsx a partir de ambientes.csv — o que a skill
levantamento-materiais produz. A planilha leva FÓRMULAS (quem calcula é o
Excel/LibreOffice), não valores digitados.

Uso: pip install openpyxl && python gerar_levantamento.py
"""
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

AQUI = Path(__file__).parent
SAIDA = AQUI / "saida"
SAIDA.mkdir(exist_ok=True)

TEAL, SOFT, RULE = "0E6B73", "E3EFEF", "D9DDE0"
fino = Side(style="thin", color=RULE)
borda = Border(left=fino, right=fino, top=fino, bottom=fino)
cab = Font(bold=True, color="FFFFFF")
fundo_cab = PatternFill("solid", fgColor=TEAL)

wb = Workbook()
ws = wb.active
ws.title = "Levantamento"
pr = wb.create_sheet("Premissas")

# Premissas editáveis (uma célula = um número que você pode mudar)
pr.append(["Premissa", "Valor"])
pr.append(["Perda de piso", 0.10])
pr.append(["Demãos de tinta", 2])
pr.append(["Rendimento da tinta (m²/L por demão)", 10])
for c in pr[1]:
    c.font, c.fill = cab, fundo_cab
pr["B2"].number_format = "0%"
pr.column_dimensions["A"].width = 38
pr.column_dimensions["B"].width = 10

ws.append(["Ambiente", "Área (m²)", "Perímetro (m)", "Pé-direito (m)",
           "Piso", "Piso c/ perda (m²)", "Parede (m²)", "Tinta (L)"])
with open(AQUI / "ambientes.csv", encoding="utf-8") as f:
    for i, r in enumerate(csv.DictReader(f), start=2):
        ws.append([
            r["ambiente"], float(r["area_m2"]), float(r["perimetro_m"]), float(r["pe_direito_m"]),
            r["piso"],
            f"=B{i}*(1+Premissas!$B$2)",
            f"=C{i}*D{i}",
            f"=IF(ISNUMBER(SEARCH(\"pintura\",\"{r['parede']}\")),G{i}*Premissas!$B$3/Premissas!$B$4,0)",
        ])
ultima = ws.max_row
ws.append(["TOTAL", f"=SUM(B2:B{ultima})", "", "", "",
           f"=SUM(F2:F{ultima})", f"=SUM(G2:G{ultima})", f"=SUM(H2:H{ultima})"])

for c in ws[1]:
    c.font, c.fill = cab, fundo_cab
    c.alignment = Alignment(wrap_text=True, vertical="center")
for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
    for c in row:
        c.border = borda
for c in ws[ws.max_row]:
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor=SOFT)
for col in "BCDFGH":
    for c in ws[col][1:]:
        c.number_format = "0.00"
for col, w in zip("ABCDEFGH", (18, 10, 12, 12, 26, 16, 12, 10)):
    ws.column_dimensions[col].width = w
ws.row_dimensions[1].height = 34

destino = SAIDA / "levantamento.xlsx"
wb.save(destino)
print(destino)
