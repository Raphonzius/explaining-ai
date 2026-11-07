---
name: briefing-para-render
description: Leva o briefing e a planta base de um apartamento até a planta mobiliada, um modelo 3D para validação e o render com Cycles (Blender), em etapas com visto humano. Use quando pedirem mobiliar uma planta, estudo de layout, modelo 3D de validação ou render. Não projeta: propõe, confere com regras e entrega para a arquiteta aprovar cada etapa.
---

# Do briefing ao render

## Entradas
`entrada/briefing.md` (requisitos em texto) e `entrada/planta-base.json` (paredes, portas, janelas, ambientes). Modelo completo e scripts em `exemplos/projeto-apto/`.

## Etapas (a IA faz, você dá o visto)
1. **Requisitos.** Leia o briefing e escreva `requisitos.json`: itens obrigatórios por ambiente, áreas mínimas, circulação mínima. Se algo for ambíguo, vire pergunta, não suposição.
2. **Planta mobiliada.** Proponha o layout e rode `python apto.py`. O script confere: móvel dentro do ambiente, colisões, giro das portas, áreas mínimas, itens do briefing e circulação (mapa de distância). **Se a conferência acusar erro, corrija o layout e rode de novo (no máximo 3 tentativas).** Registre o que mudou.
3. **PARE · visto A.** Entregue `planta-mobiliada.svg` + `relatorio-validacao.md`. Liste em "PRECISA DE VOCÊ" tudo que a conferência não resolve (ex.: área abaixo do pedido com parede estrutural).
4. **Modelo 3D para validação.** Só depois do visto A: rode `render_blender.py --vista aerea|topo|sala --qualidade rapida`. Entregue as imagens.
5. **PARE · visto B.** A arquiteta valida volumes, aberturas, pé-direito e circulação no 3D.
6. **Render final com Cycles.** Só depois do visto B: `render_blender.py --vista ... --qualidade final` (leva alguns minutos; rode em segundo plano).

## Regras
- Nunca altere `planta-base.json`: parede e abertura são da arquiteta. Se o layout não cabe, diga e proponha, não mexa na planta.
- Cada número vem do script (área, circulação), não de estimativa.
- Móvel e medida de catálogo são suposições: marque "conferir com fornecedor".
- O render é ilustração para validação, não projeto executivo. Quem assina é a arquiteta (RRT/CAU).
- Em tarefa automática: execute só as etapas 1–3 e **avise**; as demais esperam o visto.

## Pronto significa
Para cada etapa: arquivos em `saida/`, resumo de 3 linhas, lista PRECISA DE VOCÊ, e a pergunta clara "posso seguir para a próxima etapa?".
