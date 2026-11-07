# Plugins: skill + conector (+ a rule da casa)

> Conferido na documentação do Codex e no padrão Agent Plugins (agent-plugins.org, v1.0.0) em nov/2026. Plugins e conectores mudam rápido: na dúvida, vale a documentação oficial. **Nada aqui foi testado com contas reais**: use contas de teste primeiro.

## O que é cada coisa

| Peça | O que é | Onde fica |
|---|---|---|
| **Skill** | A receita (passo a passo) | `skills/<nome>/SKILL.md` dentro do plugin |
| **Conector (MCP)** | A tomada para outro sistema (Gmail, AppFlowy) | `mcp.json` dentro do plugin |
| **Plugin** | A caixa que junta skills + conectores para instalar de uma vez | A pasta inteira, com `plugin.json` |
| **Rule** | O manual que vale sempre | `AGENTS.md` do **projeto** (não viaja no plugin) |

Por isso, cada plugin de exemplo traz uma pasta `regras/` com o trecho para colar no seu `AGENTS.md`. Plugin + rule = o kit completo.

## Estrutura (formato portátil)

```text
escritorio-email/
├── plugin.json         identidade do plugin
├── mcp.json            conector(es)
├── skills/
│   └── triagem-email-gmail/SKILL.md
└── regras/AGENTS-email.md   (nosso extra: texto para colar no AGENTS.md)
```

O formato portátil (`plugin.json` + `skills/` + `mcp.json`) é o **Agent Plugins 1.0** (agent-plugins.org, ago/2026), um padrão aberto com mantenedores de várias empresas. Ele padroniza **só dois componentes: skills (padrão Agent Skills, agentskills.io) e conectores MCP**. Rules, hooks e permissões continuam específicos de cada ferramenta — é por isso que a rule fica no `AGENTS.md` do projeto.

Na prática: skills e MCP já funcionam em muitas ferramentas (Codex, Claude Code, Cursor, Gemini CLI, Copilot...); o *empacotamento* em plugin está convergindo para esse padrão, mas **nem toda ferramenta adotou ainda** e cada uma cuida da própria instalação. Confira o passo de instalar na ferramenta que você usa. O scaffold `@plugin-creator` do Codex ainda gera o layout de compatibilidade (`.codex-plugin/plugin.json` + `.mcp.json`), também aceito.

## Exemplos deste kit

### 1. `escritorio-email` — Skill + Rule + Gmail
- Skill `triagem-email-gmail`: busca, lê, classifica e prepara **rascunhos**.
- Conector: servidor MCP do Gmail mantido pelo Google (`https://gmailmcp.googleapis.com/mcp/v1`). Ferramentas: buscar e ler conversas, etiquetar e **criar rascunho**. **Não envia.**
- **Atenção:** na data da conferência, o servidor está em *prévia para desenvolvedores* (programa de preview do Google Workspace) e exige projeto no Google Cloud e cliente OAuth marcado "Use this client for an AI-powered agent". Peça ajuda a quem cuida da TI/conta Google do escritório. Guia oficial: developers.google.com/workspace/gmail/api/guides/configure-mcp-server
- Escopos: `gmail.readonly` + `gmail.compose`. O segredo do cliente OAuth **não** vai no arquivo: é informado na hora de conectar.
- **Risco real: injeção de comando por e-mail.** Um e-mail malicioso pode trazer "instruções" para a IA. Por isso a rule diz que e-mail é dado, não ordem, e a skill só cria rascunho com aprovação.

### 2. `escritorio-atas` — Skill + Rule + AppFlowy (escriba de atas)
- Skill `escriba-ata-appflowy`: lê as anotações ou a transcrição da reunião, **redige a ata** no padrão do escritório (presentes, decisões, pendências com dono e prazo, pontos em aberto), cria a página no AppFlowy e, com um segundo "pode ir", lança as pendências no quadro "Pendências".
- Dois pedidos de aprovação separados: um para a **página**, outro para os **cartões**.
- Conector: o AppFlowy não tem (até onde conferimos) servidor MCP oficial; existem servidores da **comunidade** (ex.: `appflowy-mcp` no PyPI, executado com `uvx`). Código de terceiros: leia antes, use conta de serviço com acesso só ao espaço "Atas" e ao quadro de pendências e prefira versões com escrita limitada. As variáveis do `mcp.json` são um **modelo**: confira os nomes na documentação do servidor que escolher.
- Teste com `exemplos/reuniao-ata.txt` (anotações fictícias da reunião da Casa Lago, 04/11/2026).

## Como instalar (resumo)

1. Copie a pasta do plugin para onde sua ferramenta lê plugins (no Codex: marketplace local/do repositório, `@plugin-creator` ajuda a gerar; ou `codex plugin marketplace add ./pasta-da-marketplace`).
2. Conecte o conector (login/OAuth) com uma conta de **teste**, primeiro somente leitura.
3. Cole o trecho de `regras/` no `AGENTS.md` do projeto.
4. Rode com dados fictícios. Confira se pediu aprovação antes de criar rascunho/cartão.
5. Só depois, conta real.

## Checklist de segurança antes de ligar um conector

- [ ] Quem criou o conector? É oficial ou de terceiros? Li o código/documentação?
- [ ] Começa em **somente leitura**? Escrita só para criar rascunho/cartão?
- [ ] A conta usada tem acesso só ao que precisa (pasta, quadro, caixa de teste)?
- [ ] A rule manda pedir aprovação antes de qualquer escrita?
- [ ] E-mails e páginas são tratados como **dado**, não como ordem?
- [ ] Sem senha ou chave dentro de arquivos do plugin?
- [ ] Combinei com a política de privacidade do escritório (LGPD)?
