# explaining-ai

Apresentação (deck HTML) e kit prático para explicar **o que é IA de verdade** a arquitetas: LLM, token, janela de contexto, inferência, harness (rules, skills, hooks, MCP), agentes e orquestração, licenciado × open source, como configurar o Codex e um hands-on de skills e plugins.

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

São 70 slides curtos (8 partes), com 9 demos e o FreeCAD como "mais uma coisa…" no final. As Partes 1–7 cabem em ~60 min com as demos e perguntas; a **Parte 8 (hands-on de skills e plugins)** soma ~25 min e pode virar uma oficina à parte.

Os exemplos são do dia a dia (teclado do celular, jantar, livro, planilha). O detalhe de arquitetura fica com elas: as notas sugerem perguntas para devolver à plateia, e as skills do `codex-kit/` trazem o passo a passo técnico.

## Demos
Nove demos ao longo do deck: skill, harness (trava em ação), e-mail, planilha real no LibreOffice, Codex (ata → tarefas), **plugin de e-mail (Skill + Rule + Gmail)**, **plugin de tarefas (Skill + Rule + AppFlowy)** e, como "mais uma coisa…" no final, a planta técnica e o 3D no FreeCAD. As demos animadas tocam sozinhas ao entrar no slide (botão "Ver de novo"); os vídeos tocam em loop. Versões avulsas em `demos/`.

## Simulações e capturas reais
Planilha e FreeCAD são capturas reais. As telas de Codex, e-mail, skill, harness e dos dois plugins (Gmail, AppFlowy) são **simulações** fiéis, marcadas como tal; se quiser, troque por capturas suas (regras em `codex-kit/README.md`).

## Parte 8: skills e plugins na prática
Anatomia de uma skill, descrição, `$skill-creator`, onde guardar e chamar, instalar com cuidado, plugin (skill + conector + rule), duas demos, "qual usar quando", erros e dicas, e plugins como padrão de mercado.

## Kit
`codex-kit/` — AGENTS.md, config.toml, skills, hooks, exemplos fictícios, `guia-skills.md`, `modelo-skill/` e `plugins/` (e-mail com Gmail e tarefas com AppFlowy). Veja o README dentro da pasta.

## Créditos
Fontes Inter e JetBrains Mono sob SIL Open Font License 1.1. Citação de abertura: paráfrase de Fabio Akita, "RANT: o Akita abriu as pernas pra IA??", akitaonrails.com, fev/2026.
