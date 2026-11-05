# Kit Codex para o escritório

Modelos prontos para configurar o **harness** (rules, skills, MCP, hooks) no Codex. Tudo em português, com dados fictícios.

> Confirmado na documentação oficial (developers.openai.com/codex) e no código aberto do Codex (github.com/openai/codex). Interfaces mudam rápido: se algo divergir, vale a doc oficial.

## Passo a passo
1. **Instalar o Codex** — siga https://developers.openai.com/codex (CLI via npm/Homebrew, app ou extensão de IDE) e faça login com sua conta.
2. **Criar a pasta do projeto** com `entrada/`, `saida/`, `projetos/`.
3. **Rules**: copie `AGENTS.md` para a raiz da pasta do projeto e edite.
4. **Config**: copie `config.toml` para `~/.codex/config.toml` (Windows: `C:\Users\<você>\.codex\`). Comece com `approval_policy = "on-request"` e `sandbox_mode = "workspace-write"`.
5. **Skills**: copie as pastas de `skills/` para `~/.codex/skills/` (todas as suas conversas) ou para a pasta de skills do projeto. No Codex, liste as skills disponíveis e chame pelo nome (ex.: `$triagem-email`).
6. **MCP**: descomente só o conector que for usar, em `config.toml`. Comece somente-leitura.
7. **Hooks** (opcional): veja `hooks/` — exemplo que bloqueia apagar em `projetos/`.
8. **Teste** com `exemplos/` (e-mails, ambientes, ata, planta DXF) antes de usar dados reais.

## Glossário rápido
- **Rule** (`AGENTS.md`): regras que valem sempre. **Skill**: procedimento sob demanda. **MCP**: conector com outros sistemas. **Hook**: checagem automática. **Sandbox**: onde pode escrever. **Aprovação**: quando precisa pedir.

Receitas de sequencial/paralelo/aprovação humana/economia de tokens: [`orquestracao.md`](orquestracao.md).

## Segurança
Nunca coloque senhas ou chaves nestes arquivos. Dados reais de clientes: só com a política de privacidade do escritório em mente (LGPD).
