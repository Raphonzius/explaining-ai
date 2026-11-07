# Demos (vídeos e imagens)

Material para mostrar ou mandar fora do deck. O `index.html` carrega os vídeos (planilha, FreeCAD e pipeline planta → render) direto desta pasta.

| Arquivo | O que mostra | Tipo |
|---|---|---|
| `demo-harness.mp4` | A IA lê as regras, tenta apagar arquivos, o hook bloqueia e ela devolve a decisão | Simulação animada (fiel ao Codex) |
| `demo-skill.mp4` | `$triagem-email` abre a receita e gera a triagem | Simulação animada |
| `demo-email.mp4` | Caixa de entrada → urgências → lista do dia → rascunho não enviado | Simulação animada, dados fictícios |
| `demo-rotina-email-agendada.mp4` | Rotina agendada (seg–sex 7h30): lê a caixa, classifica, cria rascunhos (nada enviado) e termina com a lista "PRECISA DE VOCÊ" | Simulação animada, dados fictícios |
| `demo-ata-automatica-appflowy.mp4` | Reunião termina → transcrição chega → ata gerada e lançada no AppFlowy sozinha; tarefa sem dono marcada `[?]` e alertada | Simulação animada, dados fictícios |
| `demo-pipeline-planta-para-render.mp4` | Planta base vista de cima → mobília entra → paredes e móveis sobem do próprio desenho (maquete para validar) → a câmera inclina e gira → a maquete vira o render Cycles. ~21 s, 1280×720, sem áudio | Render real (Blender 5 + Cycles, por script) |
| `demo-planilha-libreoffice.mp4` | Planilha real no LibreOffice Calc: a perda muda de 10% para 15% e o total recalcula (89,10 → 93,15 m²) | Captura real |
| `demo-freecad-planta-para-3d.mp4` | FreeCAD: planta técnica (cotas, esquadrias, áreas) → paredes sobem → casa 3D girando | Captura real |
| `freecad-planta.png` | Planta técnica: paredes cortadas, cotas, P01–P04, S01, J01–J03, áreas, terraço e jardim | Captura real |
| `freecad-3d.png`, `freecad-3d-terraco.png` | Casa em terracota com pergolado metálico e vidro, brise, deck e jardim | Captura real |

`demo-rotina-email-agendada.mp4` e `demo-ata-automatica-appflowy.mp4` são gravações (1920×1080, sem áudio) dos slides 63 e 64 do `index.html`. O vídeo do pipeline é exibido no slide "Da planta ao render, num giro só." e foi gerado a partir de `codex-kit/exemplos/projeto-apto/` (mesma cena do `render_blender.py`).

Como reproduzir as capturas reais:
- Planilha: `codex-kit/exemplos/gerar_levantamento.py` (gera `saida/levantamento.xlsx` com fórmulas).
- FreeCAD: `codex-kit/exemplos/freecad_apto.py` (rodar como macro no FreeCAD 26.3 ou mais novo).
