---
name: levantamento-materiais
description: Gera levantamento de quantitativos de materiais de obra (piso, rodapé, pintura, revestimento) a partir de lista de ambientes com áreas e acabamentos, em planilha com fórmulas, perdas e campos de cotação. Use para orçamento preliminar de materiais.
---

# Levantamento de materiais

## Entradas
`entrada/ambientes.csv` com: ambiente, area_m2, perimetro_m, pe_direito_m, piso, parede, rodape, observacoes.

## Passos
1. Valide o CSV; liste linhas incompletas e pergunte.
2. Crie `saida/levantamento.xlsx` (ou .csv + fórmulas) com **fórmulas de planilha**, não valores digitados:
   - piso = area × (1 + perda%), perda padrão 10% (retilíneo) / 15% (diagonal) — parâmetro editável em célula separada
   - rodapé = perímetro − vãos de porta (coluna editável)
   - pintura = (perímetro × pé-direito − vãos) × demãos
3. Totais por material; colunas vazias para unidade, fornecedor, preço unitário, total.
4. Aba "Premissas" listando todas as suposições.

## Regras
- A IA escreve as fórmulas; **a planilha calcula**. Confira 2 linhas à mão e mostre a conferência.
- Não invente preços. É estimativa preliminar, não orçamento fechado.
