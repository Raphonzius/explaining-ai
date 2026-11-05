# Orquestração: receitas para o dia a dia

Analogia: **você é a responsável técnica; os agentes são a equipe.**

## 1. Sequencial — quando uma etapa depende da anterior
Obra: fundação → estrutura → alvenaria → acabamento.
IA: briefing → programa de necessidades → memorial → levantamento de materiais.

Receita (uma conversa, etapas com "pare e espere"):
```
Vamos fazer em 4 etapas. Termine cada uma, salve em saida/ e PARE para eu aprovar.
1) Programa de necessidades a partir de entrada/briefing.md
2) Memorial usando a skill documentacao-projeto
3) Levantamento com a skill levantamento-materiais
4) Resumo de pendências
```

## 2. Paralelo — quando as tarefas não dependem uma da outra
Obra: enquanto a alvenaria sobe, o marceneiro fabrica os móveis.
Obra: os complementares (estrutural, elétrico, hidráulico) andam em paralelo e depois vem a **compatibilização**.
IA: abra **uma sessão por tarefa** (terminais/abas separados):
- Sessão A: triagem de e-mails
- Sessão B: benchmark do concorrente 1 · Sessão C: concorrente 2
- Sessão D: revisão do memorial

Regras do paralelo:
- Cada sessão escreve em **sua própria pasta de saída** (dois pedreiros na mesma parede = retrabalho).
- Ponto de junção: você lê tudo e consolida.
- Para código/scripts, use branches ou cópias separadas.

## 3. Human-in-the-loop — vistorias obrigatórias
Peça aprovação **antes** de: enviar algo para fora, apagar/sobrescrever, entregar ao cliente, gastar dinheiro.
- Modo de aprovação: `approval_policy = "on-request"` (ou `"untrusted"` no começo).
- O nome técnico disso é "human-in-the-loop": o visto da arquiteta.
- Hooks barram o que nunca pode acontecer (ver `hooks/`).
- Escala de autonomia: **sugere** → **executa com aprovação** → **executa e avisa** (só baixo risco e reversível).

## 4. Economia de tokens
- Mande o trecho que importa (lista de ambientes), não o PDF de 200 páginas.
- Uma conversa por assunto; ao trocar de assunto, peça resumo de 10 linhas e comece nova.
- Peça saída em tabela/CSV, curta.
- Rotina repetida vira **skill** (carregada só quando usada), não texto colado.
- Regras fixas ficam no AGENTS.md, não no prompt.

## 5. Previsibilidade (determinístico × probabilístico)
A IA sorteia palavras; planilha e script repetem sempre o mesmo resultado.
**IA decide e escreve; ferramenta determinística calcula e confere.**
Formato de saída fixo + exemplo + checklist + hook = menos surpresa.
