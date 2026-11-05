---
name: analise-redes-sociais
description: Analisa o desempenho de posts do próprio escritório (Instagram, LinkedIn etc.) a partir de métricas exportadas e sugere temas, formatos, horários e um calendário editorial. Use para relatório de redes sociais próprias.
---

# Análise das redes do escritório

## Entradas
CSV/planilha exportada da plataforma em `entrada/redes/` (data, formato, legenda, alcance, curtidas, comentários, salvamentos, compartilhamentos).

## Passos
1. Valide as colunas; liste o que faltou.
2. Calcule com **planilha/script** (não de cabeça): engajamento por post, mediana por formato, por dia da semana e por tema.
3. Classifique cada post por tema (obra concluída, processo, bastidores, dica, projeto 3D, depoimento…).
4. Aponte os 5 melhores e 5 piores com hipótese do porquê (marcada como hipótese).
5. Gere `saida/relatorio-redes.md` + `saida/calendario-editorial.csv` (4 semanas, tema, formato, legenda-rascunho).

## Regras
- Separe fato (dado) de interpretação.
- Amostra pequena (<20 posts): avise que a conclusão é fraca.
- Não publique nada.
