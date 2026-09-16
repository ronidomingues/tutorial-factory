#!/usr/bin/env python3
"""Atalho para rodar o md2book direto do repositório, sem instalar nada.

    python3 md2book.py            # gera os .tex e compila o PDF
    python3 md2book.py tex        # só converte Markdown -> LaTeX
    python3 md2book.py listar     # mostra a ordem dos capítulos
    python3 md2book.py init       # cria um livro.json de exemplo

Depois de instalar (`uv tool install .`), o comando `md2book` faz o mesmo de
qualquer pasta. Os dois caminhos chamam exatamente a mesma função.
"""

import sys
from pathlib import Path

# "src" na frente do diretório do script: sem isso, "import md2book"
# encontraria este próprio arquivo em vez do pacote.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from md2book.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
