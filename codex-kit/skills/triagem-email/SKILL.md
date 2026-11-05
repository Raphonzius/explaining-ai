---
name: triagem-email
description: Classifica e prioriza e-mails do escritório (cliente, obra, fornecedor, prefeitura, financeiro, spam) e prepara rascunhos de resposta e um resumo diário. Use quando pedirem triagem, resumo ou resposta de e-mails. Nunca envia.
---

# Triagem de e-mails

## Entradas
Arquivo `entrada/emails.*` (txt/eml/csv) ou e-mails lidos via conector MCP de e-mail (somente leitura/rascunho).

## Passos
1. Leia todos os e-mails. Não responda nenhum ainda.
2. Para cada um, classifique: **categoria** (cliente | obra | fornecedor | prefeitura/órgão | financeiro | interno | spam) e **urgência** (hoje | esta semana | sem pressa).
3. Extraia: remetente, assunto, pedido principal, prazo citado, anexos esperados.
4. Gere `saida/triagem-AAAA-MM-DD.md` com: tabela ordenada por urgência + "Ações de hoje" (máx. 5) + dúvidas.
5. Para os que exigem resposta, escreva **rascunhos** em `saida/rascunhos/` — tom cordial e objetivo, assinatura `<SEU_NOME>`.

## Regras
- Nunca enviar. Nunca apagar. Se houver conector, só criar **rascunho**.
- Prazo ou valor citado: copie o trecho original entre aspas.
- Em caso de dúvida sobre urgência, suba um nível e sinalize "conferir".
- Não inclua dados pessoais além do necessário.
