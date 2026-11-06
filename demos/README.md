# Demos (vídeos e imagens)

Material para mostrar ou mandar fora do deck. Os mesmos vídeos já estão embutidos no `index.html`.

| Arquivo | O que mostra | Tipo |
|---|---|---|
| `demo-harness.mp4` | A IA lê as regras, tenta apagar arquivos, o hook bloqueia e ela devolve a decisão | Simulação animada (fiel ao Codex) |
| `demo-skill.mp4` | `$triagem-email` abre a receita e gera a triagem | Simulação animada |
| `demo-email.mp4` | Caixa de entrada → urgências → lista do dia → rascunho não enviado | Simulação animada, dados fictícios |
| `demo-planilha-libreoffice.mp4` | Planilha real no LibreOffice Calc: a perda muda de 10% para 15% e o total recalcula (89,10 → 93,15 m²) | Captura real |
| `demo-freecad-planta-para-3d.mp4` | FreeCAD: planta técnica (cotas, esquadrias, áreas) → paredes sobem → casa 3D girando | Captura real |
| `freecad-planta.png` | Planta técnica: paredes cortadas, cotas, P01–P04, S01, J01–J03, áreas, terraço e jardim | Captura real |
| `freecad-3d.png`, `freecad-3d-terraco.png` | Casa em terracota com pergolado metálico e vidro, brise, deck e jardim | Captura real |

Como reproduzir as capturas reais:
- Planilha: `codex-kit/exemplos/gerar_levantamento.py` (gera `saida/levantamento.xlsx` com fórmulas).
- FreeCAD: `codex-kit/exemplos/freecad_apto.py` (rodar como macro no FreeCAD 26.3 ou mais novo).
