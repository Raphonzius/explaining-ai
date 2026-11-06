---
name: organizacao-projeto
description: Transforma atas, anotações e transcrições de reunião em pendências com responsável e prazo, monta cronograma por etapas de projeto (estudo, anteprojeto, executivo, obra) e gera status semanal para o cliente. Use ao organizar um projeto ou preparar reunião/status.
---

# Organização de projeto

## Entradas
Ata ou transcrição (`entrada/`), lista de etapas e datas-alvo, quem é quem na equipe.

## Passos
1. Extraia **decisões**, **pendências** (o quê / quem / prazo) e **riscos**.
2. Se faltar responsável ou prazo, liste em "Perguntas" — não invente.
3. Gere `saida/pendencias.csv` (colunas: id, descricao, responsavel, prazo, etapa, status) para abrir em planilha.
4. Gere `saida/cronograma.md` por etapa, marcando dependências (o que só começa depois de quê).
5. Gere `saida/status-cliente.md`: máx. 12 linhas, linguagem simples, sem jargão: feito / em andamento / precisa de decisão do cliente.

## Regras
- Datas relativas ("semana que vem") viram datas absolutas só se a data da reunião estiver no texto.
- Status ao cliente é rascunho: a arquiteta revisa antes de enviar.
