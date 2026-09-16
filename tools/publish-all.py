#!/usr/bin/env python3
"""publish-all.py — republishes EVERY software in the documentation root.

    python3 tools/publish-all.py
    python3 tools/publish-all.py --jobs 6 --piece manual
    python3 tools/publish-all.py --check
    python3 tools/publish-all.py --docs ~/Documentos/documentacao

This is maintenance, not production. One software at a time is the normal way
to work; this exists for the day the brand changes, the template changes, or a
machine is rebuilt — and every PDF has to agree with the Markdown again.

`--check` says what is missing without producing anything: which software has
a `.md` with no `.pdf` beside it, which piece was never written, which PDF is
older than the Markdown it claims to render. A PDF that is out of date is worse
than a PDF that is missing: it lies with the appearance of being finished.

At the end it writes `.publicacao.json` in the documentation root — the counts
that keep `INDEX.md` honest.
"""

import argparse
import concurrent.futures as futuros
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common                                    # noqa: E402

TOOLS = Path(__file__).resolve().parent
PUBLISH = TOOLS / "publish-doc.py"
RE_PIECE_FILE = re.compile(r"^(?P<stem>[a-z]+)_(?P<data>\d{4}-\d{2}-\d{2})\.md$")


def paginas(pdf: Path) -> int:
    if not pdf.is_file() or not shutil.which("pdfinfo"):
        return 0
    saida = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                           text=True).stdout
    for linha in saida.splitlines():
        if linha.startswith("Pages:"):
            return int(linha.split()[1])
    return 0


def softwares(raiz: Path) -> list:
    """Every folder under the documentation root that holds a piece."""
    if not raiz.is_dir():
        return []
    achados = []
    for pasta in sorted(raiz.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith("."):
            continue
        if any(RE_PIECE_FILE.match(p.name) for p in pasta.glob("*.md")):
            achados.append(pasta)
    return achados


def peca_mais_recente(pasta: Path, stem: str):
    achados = sorted(p for p in pasta.glob("%s_*.md" % stem)
                     if RE_PIECE_FILE.match(p.name))
    return achados[-1] if achados else None


def inspecionar(pasta: Path) -> dict:
    """What this software has, what it lacks, and what went stale."""
    estado = {"software": pasta.name, "pecas": {}, "paginas": 0,
              "pendencias": []}
    for peca, dados in common.PIECES.items():
        fonte = peca_mais_recente(pasta, dados["stem"])
        if fonte is None:
            estado["pecas"][peca] = {"fonte": None}
            estado["pendencias"].append("%s: nunca escrito" % dados["label"])
            continue
        tex, pdf = fonte.with_suffix(".tex"), fonte.with_suffix(".pdf")
        n = paginas(pdf)
        estado["paginas"] += n
        estado["pecas"][peca] = {
            "fonte": fonte.name,
            "data": RE_PIECE_FILE.match(fonte.name).group("data"),
            "tex": tex.is_file(), "pdf": pdf.is_file(), "paginas": n,
        }
        if not pdf.is_file():
            estado["pendencias"].append("%s: sem PDF" % dados["label"])
        elif pdf.stat().st_mtime < fonte.stat().st_mtime:
            estado["pendencias"].append(
                "%s: PDF mais antigo que o .md — republique" % dados["label"])
        if not tex.is_file():
            estado["pendencias"].append("%s: sem .tex" % dados["label"])
    return estado


def publicar_um(pasta: Path, args) -> dict:
    inicio = time.time()
    cmd = [sys.executable, str(PUBLISH), str(pasta),
           "--piece", args.piece,
           "--agent", args.agent,
           "--doc-version", args.doc_version]
    if args.ai_model:
        cmd += ["--ai-model", args.ai_model]
    if args.brand:
        cmd += ["--brand", args.brand]
    if args.docs:
        cmd += ["--docs", args.docs]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    estado = inspecionar(pasta)
    estado["segundos"] = round(time.time() - inicio, 1)
    estado["erros"] = ([] if proc.returncode == 0 else
                       ["publish-doc exited with code %d" % proc.returncode])
    estado["avisos"] = [l for l in proc.stderr.splitlines()
                        if l.startswith("WARNING")][:50]
    return estado


def relatorio(estados: list, raiz: Path, escrever: bool) -> None:
    total_pag = sum(e["paginas"] for e in estados)
    completos = [e for e in estados if not e["pendencias"]]
    print()
    print("== %d software(s) ==" % len(estados))
    for e in estados:
        marca = "ok " if not e["pendencias"] else "!! "
        print("  %s%-28s %4d página(s)%s"
              % (marca, e["software"], e["paginas"],
                 "" if not e["pendencias"]
                 else "   " + "; ".join(e["pendencias"])))
    print()
    print("Complete: %d/%d · %d page(s) in total"
          % (len(completos), len(estados), total_pag))

    if not escrever:
        return
    destino = raiz / ".publicacao.json"
    destino.write_text(json.dumps({
        "gerado_em": date.today().isoformat(),
        "softwares": len(estados),
        "completos": len(completos),
        "paginas": total_pag,
        "detalhe": estados,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Counts written to %s" % destino)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Republishes every software in the documentation root, or "
                    "reports what is missing.")
    p.add_argument("--docs", default="",
                   help="documentation root (default: the %s pointer, else "
                        "documentation/)" % common.DOCS_POINTER)
    p.add_argument("--piece", choices=["all", "installation", "manual"],
                   default="all", help="which document to publish")
    p.add_argument("--jobs", type=int, default=4,
                   help="how many softwares at a time (default: 4)")
    p.add_argument("--check", action="store_true",
                   help="report what is missing or stale; produce nothing")
    p.add_argument("--agent", default="Claude Code (Anthropic)",
                   help="the AI agent that researched and wrote the material")
    p.add_argument("--ai-model", default="", help="model the agent ran on")
    p.add_argument("--doc-version", default="1.0",
                   help="version label of this publication")
    p.add_argument("--brand", default="", help="path to the brand kit")
    args = p.parse_args(argv)

    raiz = common.docs_root(args.docs)
    pastas = softwares(raiz)
    if not pastas:
        print("No documentation found under %s (%s)."
              % (raiz, common.docs_origin(args.docs)))
        print("Start one: python3 tools/new-doc.py <software>")
        return 1

    print("Docs: %s (%s)" % (raiz, common.docs_origin(args.docs)))
    if args.check:
        relatorio([inspecionar(pasta) for pasta in pastas], raiz, False)
        return 0

    print("Publishing %d software(s), %d at a time..." % (len(pastas), args.jobs))
    with futuros.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        estados = list(pool.map(lambda pasta: publicar_um(pasta, args), pastas))
    for e in estados:
        for aviso in e["avisos"]:
            print("  %s: %s" % (e["software"], aviso), file=sys.stderr)
    relatorio(estados, raiz, True)
    return 0 if all(not e["erros"] for e in estados) else 1


if __name__ == "__main__":
    sys.exit(main())
