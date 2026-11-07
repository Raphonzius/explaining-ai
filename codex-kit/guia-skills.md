# Skills: sua primeira receita em 10 minutos

> Conferido na documentação do Codex ("Build skills", learn.chatgpt.com) em nov/2026. Interfaces mudam rápido: se algo divergir, vale a documentação oficial.

**Skill** é uma pasta com um arquivo `SKILL.md` (nome, descrição e passo a passo). A IA lê só o nome e a descrição de todas as skills e **abre o resto apenas quando a tarefa combina**. Isso poupa a "prancheta" (janela de contexto).

`SKILL.md` segue um padrão aberto (Agent Skills): a mesma pasta funciona em várias ferramentas.

## Anatomia

```text
minha-skill/
├── SKILL.md        obrigatório: nome + descrição + passos
├── scripts/        opcional: código para o que precisa dar sempre o mesmo resultado
├── references/     opcional: documentos de apoio
└── assets/         opcional: modelos e arquivos
```

## Caminho rápido: peça ao Codex para criar

1. Abra o Codex na pasta do projeto.
2. Digite `$skill-creator` e responda às perguntas: o que a skill faz, quando deve disparar e se terá scripts (o padrão é **só instruções**, e é o que você quer no começo).
3. Revise o `SKILL.md` que ele gerou. **Você assina o que está ali.**

Prompt pronto para colar:

```text
$skill-creator
Quero uma skill para [tarefa que repito toda semana].
Entrada: [arquivo ou texto]. Saída: [tabela / CSV / rascunho] em saida/.
Regras: nunca enviar nada, nunca inventar dado; se faltar, perguntar.
Só instruções, sem scripts.
```

## Caminho manual

1. Crie a pasta `.agents/skills/nome-da-skill/` (no projeto) ou `~/.agents/skills/nome-da-skill/` (todos os projetos; no Windows `C:\Users\SeuNome\.agents\skills\`).
2. Copie `modelo-skill/SKILL.md` para dentro e edite.
3. O Codex detecta mudanças sozinho. Se a skill não aparecer, reinicie o Codex.

## Onde a skill pode morar

| Onde | Caminho | Vale para |
|---|---|---|
| Projeto | `.agents/skills/` na pasta do projeto | Só aquele projeto (e quem usar a pasta) |
| Pessoal | `~/.agents/skills/` | Todos os seus projetos |
| Instalada | via `$skill-installer` | Skills prontas de outras pessoas |

Duas skills com o mesmo nome **não se fundem**: aparecem as duas. Dê nomes diferentes.

## Como chamar e testar

- `/skills` lista o que está disponível. `$nome-da-skill` chama direto.
- Sem chamar, o Codex também pode escolher sozinho se a **descrição** combinar com o pedido.
- Para desligar a escolha automática, crie `agents/openai.yaml` na skill com `policy: allow_implicit_invocation: false` (a chamada com `$` continua funcionando).
- Teste com dados fictícios (`exemplos/`) antes de usar dados reais.

## A descrição decide tudo

| Ruim | Bom |
|---|---|
| "Ajuda com e-mails." | "Classifica e prioriza e-mails do escritório (cliente, obra, fornecedor...) e prepara rascunhos. Use quando pedirem triagem ou resumo de e-mails. Nunca envia." |

Receita: **o que faz + quando usar (palavras que você realmente fala) + o que fica de fora**. Coloque o caso de uso principal no começo: se houver muitas skills, o Codex encurta as descrições.

## Checklist antes de confiar numa skill

- [ ] Faz **uma** coisa só?
- [ ] A descrição diz quando usar e quando não usar?
- [ ] Os passos são verbos no imperativo, com entrada e saída claras?
- [ ] Diz o que fazer quando faltar dado ("perguntar, não inventar")?
- [ ] Tem a proibição que importa ("nunca enviar", "nunca apagar")?
- [ ] O formato da saída está definido?
- [ ] Testei com os exemplos fictícios e conferi o resultado?
- [ ] Prefere instruções a scripts? (script só quando o resultado precisa ser sempre idêntico)

## Instalar skill de outra pessoa (com cuidado)

`$skill-installer nome` instala skills curadas. Também dá para pedir para baixar de um repositório.

> **Skill de terceiros é como um funcionário que você não entrevistou.** Ela pode mandar a IA rodar comandos. Leia o `SKILL.md` (e qualquer arquivo em `scripts/`) **antes** de instalar. Prefira fontes oficiais e conhecidas.

## 5 erros comuns

1. Skill que faz tudo ("assistente do escritório"). Quebre em várias.
2. Descrição vaga: ela nunca dispara, ou dispara fora de hora.
3. Script onde bastava texto.
4. Sem proibições: a skill "ajuda" enviando e apagando.
5. Instalar sem ler.
