#!/usr/bin/env python3
"""Hook de exemplo (PreToolUse): barra comandos que apagam arquivos em projetos/.

O Codex envia um JSON no stdin descrevendo o comando que vai rodar.
Se este script sair com código 2 e escrever o motivo no stderr, o comando é
bloqueado e o motivo volta para a IA. Código 0 = liberado.
Confira o contrato atual dos hooks na documentação oficial antes de usar.
"""
import json
import re
import sys

dados = json.load(sys.stdin)
comando = (dados.get("tool_input") or {}).get("command", "")
if isinstance(comando, list):
    comando = " ".join(comando)

if re.search(r"\b(rm|del|rmdir|rd|Remove-Item)\b", comando) and "projetos" in comando:
    print("Bloqueado: apagar em projetos/ exige aprovação da arquiteta. "
          "Gere uma cópia em saida/.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
