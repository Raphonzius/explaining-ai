---
name: nome-da-skill-em-minusculas
description: Faz [UMA tarefa clara] a partir de [entrada]. Use quando pedirem [palavras que a pessoa realmente usa]. Não use para [o que fica de fora]. Nunca [o que é proibido].
---

# Nome da tarefa

> Copie esta pasta (`modelo-skill`), renomeie para o nome da skill e edite.
> A pasta e o campo `name` devem ter o mesmo nome, em minúsculas e com hífen.
> Apague estes comentários depois de editar.

## Entradas
O que a skill precisa receber e onde fica (ex.: `entrada/ata.txt`).

## Passos
1. Primeiro passo, no imperativo ("Leia...", "Liste...").
2. Segundo passo. Diga o que fazer quando faltar informação: **perguntar**, nunca inventar.
3. Gere `saida/NOME-AAAA-MM-DD.md` (ou .csv) no formato abaixo.

## Formato da saída
Mostre um exemplo curto do resultado esperado (tabela, lista). Formato fixo = resultado previsível.

## Regras
- O que a skill nunca faz (enviar, apagar, assinar).
- Como tratar dado pessoal.
- Quando parar e pedir aprovação.

## Pronto significa
Arquivo em `saida/`, resumo de 3 linhas e lista de pendências.
