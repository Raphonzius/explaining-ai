#!/usr/bin/env python3
"""Hook de exemplo (PreToolUse): barra apagar/mover/sobrescrever em projetos/.

O Codex envia um JSON no stdin descrevendo a ferramenta que vai rodar
(tool_name + tool_input). Se este script sair com código 2 e escrever o motivo
no stderr, a ação é bloqueada e o motivo volta para a IA. Código 0 = liberado.

ATENÇÃO
- Hooks novos ou alterados só rodam depois que você os aprova com /hooks no Codex.
- Se o script falhar (Python ausente, erro), o Codex registra o erro e LIBERA a
  ação. Hook é trava extra, não substitui sandbox + backup.
"""
import json
import re
import sys

dados = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
entrada = dados.get("tool_input") or {}
texto = entrada.get("command") or entrada.get("input") or entrada.get("patch") or ""
if isinstance(texto, list):
    texto = " ".join(texto)
if not isinstance(texto, str):
    texto = json.dumps(texto, ensure_ascii=False)

PERIGO = re.compile(
    r"\b(rm|del|erase|rmdir|rd|Remove-Item|mv|move|Move-Item|ren|rename)\b"
    r"|\*\*\* Delete File:|\*\*\* Move to:|>",
    re.IGNORECASE,
)

if re.search(r"projetos", texto, re.IGNORECASE) and PERIGO.search(texto):
    print("Bloqueado: apagar, mover ou sobrescrever em projetos/ exige aprovação "
          "da arquiteta. Gere uma cópia em saida/.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
