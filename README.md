# explaining-ai

Apresentação (deck HTML) e kit prático para explicar **o que é IA de verdade** a arquitetas: LLM, token, janela de contexto, inferência, harness (rules, skills, hooks, MCP), agentes e orquestração, licenciado × open source e como configurar o Codex.

Visual no estilo da apresentação do TCC (papel claro, teal, divisores escuros, Inter + JetBrains Mono embutidas). Linguagem direta e slides no estilo keynote: uma ideia por slide, pouco texto, exemplos do dia a dia.

**Três mensagens** que se repetem do começo ao fim:
1. É um gerador de texto.
2. O poder está no que vai em volta.
3. Quem assina é você.

## Abrir e apresentar
Abra `index.html` no navegador — funciona offline, sem instalar nada.

| Tecla | Ação |
|---|---|
| ← → / espaço | navegar |
| `N` | notas do apresentador: o que falar e respostas para "se perguntarem…" |
| `O` | visão geral de todos os slides |
| `F` | tela cheia |
| `P` | imprimir / salvar PDF (1 slide por página, 1920×1080) |

O palco é 1920×1080 e se ajusta ao projetor. No celular (ou em retrato) os slides se reorganizam em coluna.

São 80 slides curtos (7 partes), com 7 demos, com a demo do Codex no fim, como "mais uma coisa…". Para caber em ~60 min, pule os marcados como **opcional** nas notas (mapa da IA, fabricantes, concorrentes, "no dia a dia").

Os exemplos são do dia a dia (teclado do celular, jantar, livro, planilha). O detalhe de arquitetura fica com elas: as notas sugerem perguntas para devolver à plateia, e as skills do `codex-kit/` trazem o passo a passo técnico.

## Demos
Sete demos ao longo do deck: harness (trava em ação), skill, e-mail, planilha real no LibreOffice, planta e 3D no FreeCAD, e o Codex no fim. As demos animadas tocam sozinhas ao entrar no slide (botão "Ver de novo"); os vídeos tocam em loop. Versões avulsas em `demos/`.

## Recortes reais para capturar
O slide da demo tem um espaço tracejado "Captura real · substituir" para o pedido de aprovação do Codex. Veja as regras de captura em `codex-kit/README.md`. Todas as outras telas do deck são **recriações ilustrativas** marcadas "exemplo fictício".

## Kit
`codex-kit/` — AGENTS.md, config.toml, skills, hooks e exemplos fictícios. Veja o README dentro da pasta.

## Créditos
Fontes Inter e JetBrains Mono sob SIL Open Font License 1.1. Citação de abertura: paráfrase de Fabio Akita, "RANT: o Akita abriu as pernas pra IA??", akitaonrails.com, fev/2026.
