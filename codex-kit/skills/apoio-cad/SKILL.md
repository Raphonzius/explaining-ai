---
name: apoio-cad
description: Apoia o trabalho em AutoCAD/BricsCAD/progeCAD escrevendo scripts de tarefas repetitivas (AutoLISP, .scr), lendo e auditando arquivos DXF com Python (ezdxf) e conferindo padrão de layers. Use para automatizar tarefas de CAD; não desenha o projeto.
---

# Apoio a CAD

## O que fazer
- Auditar layers de um DXF: listar layers, contagem de entidades, layers fora do padrão.
- Escrever scripts pequenos e legíveis: renomear layers, numerar pranchas, extrair tabela de áreas de polilinhas fechadas.
- Explicar comandos e comentar o código linha a linha.

## Passos
1. Trabalhe só em **cópia** do arquivo (`saida/`). Nunca em `.dwg`/`.dxf` original.
2. Para DXF use Python com `ezdxf` (instale com `pip install ezdxf` se faltar). No FreeCAD, gere macros Python (modelo: `exemplos/freecad_apto.py`).
3. Entregue o script + instrução "como rodar" + o que ele altera.
4. Rode em arquivo de teste e mostre antes/depois.

## Padrão de layers do escritório (edite!)
`A-PAREDE`, `A-PORTA`, `A-JANELA`, `A-COTAS`, `A-TEXTO`, `A-MOBILIARIO`, `A-ESQUADRIAS`.

## Regras
- Scripts AutoLISP/.scr só depois de eu revisar o código.
- Não assuma unidades: pergunte (cm ou m).
- Nada de projeto novo "do zero": a IA automatiza tarefas, quem projeta é a arquiteta.
