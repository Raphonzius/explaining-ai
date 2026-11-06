# AGENTS.md — regras do escritório

> Este arquivo é lido pelo Codex no início de toda sessão (são as "rules").
> Edite à vontade: quanto mais específico, mais previsível a IA fica.
> Limite prático: mantenha curto (o Codex lê até ~32 KiB somados).

## Quem somos
Escritório de arquitetura. Projetos residenciais e comerciais. Idioma: **português do Brasil**.

## Como você deve trabalhar
1. **Plano antes de agir.** Em tarefas com mais de 2 passos, mostre o plano e espere eu dizer "pode ir".
2. **Uma tarefa por vez.** Não "aproveite" para mexer em outras coisas.
3. **Mostre as contas.** Todo número (área, quantidade, perda) deve ter a fórmula visível — de preferência em planilha, não só no texto.
4. **Diga o que não sabe.** Se faltar dado, pergunte. Nunca invente medida, norma, preço ou prazo.
5. **Cite a fonte.** Norma (NBR, código de obras, plano diretor) só com número e ano; se não tiver certeza, escreva "conferir".
6. **Formato curto.** Respostas em tabela ou lista; sem enrolação.

## Nunca faça (sem eu pedir explicitamente)
- Enviar e-mail, mensagem ou publicar em rede social. **Só rascunho.**
- Apagar, mover ou sobrescrever arquivos em `projetos/`. Crie cópia em `saida/`.
- Alterar arquivos `.dwg` originais. Trabalhe em cópias.
- Assumir responsabilidade técnica: cálculo estrutural, instalações, laudos e aprovações legais são **da arquiteta responsável** (RRT/CAU).
- Colocar dados pessoais de clientes (CPF, endereço, telefone) em arquivos de saída compartilháveis.

## Convenções
- Pastas: `entrada/` (o que eu forneço), `saida/` (o que você gera), `projetos/` (intocável).
- Unidades: metros e m²; vírgula decimal nos textos; ponto decimal em arquivos de dados.
- Layers CAD: padrão do escritório descrito em `skills/apoio-cad/SKILL.md`.
- Datas: DD/MM/AAAA.

## Pronto significa
Arquivo gerado em `saida/`, resumo de 3 linhas do que foi feito, lista de pendências/dúvidas, e o que eu preciso conferir.
