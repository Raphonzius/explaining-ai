# Kit Codex para o escritório

Modelos prontos para configurar o **harness** (rules, skills, MCP, hooks) no Codex. Tudo em português, com dados fictícios.

> Conferido no código aberto do Codex (github.com/openai/codex, Apache-2.0) em nov/2026. As interfaces mudam rápido: se algo divergir, vale a documentação oficial da OpenAI.

## Antes da aula (dever de casa, 15 min)
1. Instale o **app do Codex** (ou a extensão do Codex no VS Code) e faça login com sua conta do ChatGPT. Confira na página da OpenAI quais planos incluem o Codex.
2. Se travar, mande um print. Não precisa de terminal nem de Node.js para começar.

## Windows: 3 coisas que confundem
- `~` nos textos significa **sua pasta de usuário**: `C:\Users\SeuNome`. Então `~/.codex/` = `C:\Users\SeuNome\.codex\`.
- Pastas que começam com ponto ficam escondidas. No Explorador de Arquivos: **Exibir → Mostrar → Itens ocultos** e **Extensões de nomes de arquivos**.
- O Bloco de Notas salva `config.toml.txt` escondendo o `.txt`. Com as extensões visíveis, renomeie para `config.toml`.

## Nível 1 — o essencial
1. **Pasta do projeto** com `entrada/`, `saida/`, `projetos/`.
2. **Rules**: copie `AGENTS.md` para a raiz da pasta do projeto e edite.
3. **Config**: copie `config.toml` para `~/.codex/config.toml`. Comece com `approval_policy = "on-request"` e `sandbox_mode = "workspace-write"`.
4. **Skills**: copie as pastas de `skills/` para `~/.agents/skills/` (Windows: `C:\Users\SeuNome\.agents\skills\`) — vale para todos os projetos — ou para `.agents/skills/` dentro da pasta do projeto. No Codex, digite `/skills` para ver a lista, ou chame direto: `$triagem-email`.
5. **Teste** com `exemplos/` (e-mails, ambientes, ata, planta DXF) antes de usar dados reais.

## Nível 2 — outro dia
6. **MCP** (conectores): descomente só o que for usar em `config.toml`. Comece somente-leitura.
7. **Hooks**: copie `hooks/hooks.json` para `~/.codex/hooks.json` e `hooks/bloquear_apagar.py` para `~/.codex/hooks/`. Abra o Codex, rode `/hooks` e **aprove** o hook — sem aprovação ele não roda; se editar, aprove de novo. Precisa de Python instalado (no Windows, o comando `py`). Se o script falhar, o Codex libera a ação: hook é trava extra, não substitui cópia de segurança.
8. Scripts de CAD/planilha em Python: `pip install ezdxf openpyxl`.
   - `exemplos/gerar_levantamento.py` gera uma planilha real com fórmulas a partir de `ambientes.csv`.
   - `exemplos/freecad_apto.py` desenha no FreeCAD (open source) a planta de um apartamento com portas, janelas e móveis, e calcula as áreas.

## Recortes reais para a apresentação
O deck tem 3 espaços marcados "Captura real — substituir". Para capturar:
- use **só dados fictícios** (os de `exemplos/`);
- esconda nome de usuário em caminhos (`C:\Users\...`) e e-mails;
- recorte só a parte que importa e salve em 2× (PNG/WebP).

## Glossário rápido
- **Rule** (`AGENTS.md`): manual de padrões que vale sempre. **Skill**: procedimento sob demanda. **MCP**: tomada para outros sistemas. **Hook**: trava automática. **Sandbox**: o cercadinho onde a IA pode escrever. **Aprovação**: quando ela precisa pedir.

Receitas de sequencial/paralelo/aprovação/economia de tokens: [`orquestracao.md`](orquestracao.md).

## Segurança
Nunca coloque senhas ou chaves nestes arquivos. Dados reais de clientes: só com a política de privacidade do escritório em mente (LGPD).
