# Ata automática quando a reunião acaba

> Conferido na documentação de tarefas agendadas do Codex / ChatGPT (learn.chatgpt.com/docs/automations) em nov/2026. A interface e os planos mudam: se algo divergir, vale a documentação oficial.

**Ideia:** a reunião termina, a transcrição chega, a ata aparece no AppFlowy como **rascunho**, as pendências viram cartões, e a IA só chama você se algo estiver incompleto.

## De onde vem a transcrição
Escolha uma das duas entradas. A tarefa é a mesma.
- **Arquivo:** a ferramenta de reunião (Meet, Teams, Zoom ou um gravador com transcrição) salva o texto em `entrada/transcricoes/`. Funciona com qualquer ferramenta que exporte texto.
- **Conector:** um conector da própria ferramenta de reunião (se o seu plano e a ferramenta tiverem um).

## O gatilho (duas formas, conforme o seu plano)
| Forma | Como funciona | Quando usar |
|---|---|---|
| **Evento** | A tarefa dispara quando um evento de um app conectado acontece. Segundo a documentação, tarefas por evento existem para planos elegíveis na web/celular. | Se o seu plano e o app de reunião tiverem esse evento. |
| **Verificação agendada** | A tarefa roda a cada 15 min em horário comercial e olha se há transcrição nova. `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9,10,11,12,13,14,15,16,17;BYMINUTE=0,15,30,45` | Funciona em qualquer plano com tarefas agendadas. O computador precisa estar ligado. |

Em ambos, a skill registra o que já processou em `saida/processadas.json`, então nunca cria a mesma ata duas vezes.

## Passo a passo
1. Instale e conecte o plugin `escritorio-atas` com uma conta de **serviço restrita** (acesso só ao espaço "Atas" e ao quadro "Pendências").
2. Cole o trecho de `../regras/AGENTS-atas.md` no `AGENTS.md` do projeto.
3. **Rode o prompt abaixo uma vez, na mão**, com `exemplos/reuniao-ata.txt` (fictícia). Confira a página e os cartões.
4. Crie a tarefa (peça no chat: "agende este prompt") com o gatilho escolhido.
5. Nas primeiras reuniões, uma pessoa lê cada ata antes de confiar.

## Prompt da tarefa (cole como está)
```text
$escriba-ata-appflowy

Modo AUTOMÁTICO (ninguém vai aprovar agora).
1. Procure transcrições novas em entrada/transcricoes/ que NÃO estejam em saida/processadas.json.
   Se não houver nenhuma, responda "Nada novo" e pare.
2. Para cada uma: redija a ata no padrão do AGENTS.md, crie a página como RASCUNHO no espaço Atas
   e lance as pendências no quadro Pendências com a etiqueta "da ata (revisar)".
3. Nunca apague nem edite nada que já exista. Só crie.
4. Pendência sem dono ou prazo, valor/contrato citado, contradição com ata anterior,
   ou transcrição incompleta: marque PRECISA DE VOCÊ com 1 linha de motivo.
5. Registre o arquivo em saida/processadas.json e salve a cópia da ata em saida/.
Resposta final: "PRECISA DE VOCÊ (N)" + 1 linha por item, e depois "Página criada · N cartões · rascunho aguardando revisão."
```

## Configuração segura
| Item | Valor |
|---|---|
| Sandbox | `workspace-write` |
| Conector AppFlowy | conta de serviço **só** no espaço "Atas" e no quadro "Pendências"; só ler e criar |
| Servidor MCP | o AppFlowy não tem servidor oficial conhecido: use um da comunidade, leia o código e fixe a versão |
| Dados | só reuniões que podem ser transcritas e guardadas (avise os participantes; LGPD) |
| Revisão | a arquiteta lê, corrige e **assina** cada ata |
