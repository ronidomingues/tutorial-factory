#!/usr/bin/env python3
"""new-doc.py — opens the folder for one software and seeds the two documents.

    python3 tools/new-doc.py docker
    python3 tools/new-doc.py "PostgreSQL 17" --piece installation
    python3 tools/new-doc.py docker --date 2026-09-16

It creates `<documentation root>/<software>/` and drops the skeleton of each
piece there, dated today:

    installation_AAAA-MM-DD.md
    manual_AAAA-MM-DD.md

The skeletons come from `tools/example/`, and they are the format contract:
what the publisher understands, and what a reader is owed. They are meant to be
overwritten line by line, not filled in politely around.

It **never overwrites** a file that already exists. Coming back to a software
after a new release means writing a new dated edition, not editing the old one:
the date in the name is the promise that the document was true on that day.
"""

import argparse
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common                                    # noqa: E402


def slugificar(texto: str) -> str:
    """"PostgreSQL 17" -> "postgresql-17" — the folder name."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "-", sem_acento).strip("-").lower()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Creates the documentation folder for one software and "
                    "seeds the installation and usage skeletons.")
    p.add_argument("software", help="the software being documented")
    p.add_argument("--piece", choices=["all", "installation", "manual"],
                   default="all", help="which skeleton to seed (default: all)")
    p.add_argument("--date", default="",
                   help="edition date in the file name (default: today)")
    p.add_argument("--docs", default="",
                   help="documentation root (default: the %s pointer, else "
                        "documentation/)" % common.DOCS_POINTER)
    args = p.parse_args(argv)

    if args.date and not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        print("ERROR: --date must be AAAA-MM-DD.", file=sys.stderr)
        return 2
    quando = args.date or date.today().isoformat()

    raiz = common.docs_root(args.docs)
    if not raiz.exists():
        print("The documentation root does not exist yet: %s" % raiz)
        print("Creating it. To put it somewhere else, write the path into %s "
              "at the repository root." % common.DOCS_POINTER)
    pasta = raiz / slugificar(args.software)
    pasta.mkdir(parents=True, exist_ok=True)

    pecas = ["installation", "manual"] if args.piece == "all" else [args.piece]
    criados, existentes = [], []
    for peca in pecas:
        modelo = common.example_doc(peca)
        destino = pasta / ("%s_%s.md" % (common.PIECES[peca]["stem"], quando))
        if destino.exists():
            existentes.append(destino)
            continue
        if not modelo.is_file():
            print("ERROR: skeleton missing: %s" % modelo, file=sys.stderr)
            return 2
        texto = modelo.read_text(encoding="utf-8")
        texto = texto.replace("{{SOFTWARE}}", args.software)
        destino.write_text(texto, encoding="utf-8")
        criados.append(destino)

    print("Folder: %s" % pasta)
    for caminho in criados:
        print("  created  %s" % caminho.name)
    for caminho in existentes:
        print("  kept     %s  (already written — a new edition needs a new date)"
              % caminho.name)
    if criados:
        print()
        print("Write the research and the tested steps into those files, then:")
        print("  python3 tools/publish-doc.py %s" % pasta.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
