#!/usr/bin/env python3
"""sandbox.py — runs the documented steps for real, in a throwaway container.

    python3 tools/sandbox.py --list
    python3 tools/sandbox.py --image ubuntu:24.04 -c "apt-get update" -c "apt-get install -y curl"
    python3 tools/sandbox.py --image ubuntu:24.04 --script passos.sh
    python3 tools/sandbox.py --image ubuntu:24.04 --from-doc documentation/docker/installation_2026-09-16.md
    python3 tools/sandbox.py --image ubuntu:24.04 --from-doc <arquivo> --report verificacao.md

This is the program that makes "never invent, always test" enforceable instead
of aspirational. A tutorial whose commands were never executed is a guess in
tidy typography, and the reader cannot tell the difference — the one honest
answer is to run them.

It starts a container from a clean base image, runs each command in order,
records the exit code and the real output of each, and prints a transcript
ready to be quoted in the document. The container is destroyed afterwards, so
the next run starts from the same clean state as the reader's machine.

`--from-doc` extracts the shell blocks from a tutorial in this repository's
format and runs exactly those, in the order they are written. A block whose
language is `console` is output, not input: it is skipped, because that is what
the reader is supposed to *see*, not type.

WHAT IT DOES NOT DO: it does not run the container privileged, touch the host
network beyond what the container needs, or mount anything by default. Steps
that genuinely require a real machine — a GUI installer, a kernel module, an
Apple Silicon-only path — cannot be verified here. Say so in the document,
naming the step, instead of implying it was tested.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Base images worth keeping at hand. The list is a starting point, not a limit:
# --image takes anything the container engine can pull.
IMAGENS = [
    ("ubuntu:24.04", "Ubuntu 24.04 LTS (Noble Numbat) — o alvo mais comum"),
    ("ubuntu:22.04", "Ubuntu 22.04 LTS (Jammy Jellyfish)"),
    ("debian:12", "Debian 12 (Bookworm)"),
    ("debian:13", "Debian 13 (Trixie)"),
    ("fedora:41", "Fedora 41"),
    ("rockylinux:9", "Rocky Linux 9 — família RHEL"),
    ("archlinux:latest", "Arch Linux — rolling release"),
    ("alpine:3.20", "Alpine 3.20 — musl, sem glibc; cuidado ao generalizar"),
    ("opensuse/leap:15.6", "openSUSE Leap 15.6"),
    ("mcr.microsoft.com/powershell:latest", "PowerShell 7 em Linux — para "
     "conferir sintaxe de cmdlet, não o Windows de verdade"),
]

MARCA = "@@TF@@"
RE_CERCA = re.compile(r"^ {0,3}(?:`{3,}|~{3,})\s*([A-Za-z0-9_+-]*)")
LINGUAGENS_ENTRADA = {"bash", "sh", "shell", "zsh"}


def erro(msg, codigo=2):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(codigo)


def motor(preferido: str = "") -> list:
    """The container engine available here: docker, podman, or nothing.

    An explicitly named engine is not a preference, it is a requirement:
    falling back to the other one would run the test somewhere the caller did
    not choose, and quietly.
    """
    if preferido:
        caminho = shutil.which(preferido)
        if caminho:
            return [caminho]
        erro("--engine %s, but %s is not on the PATH." % (preferido, preferido))
    for nome in ("docker", "podman"):
        caminho = shutil.which(nome)
        if caminho:
            return [caminho]
    erro("no container engine found. Install Docker or Podman, or verify the "
         "steps on a real machine and say so in the document.\n"
         "  Debian/Ubuntu: sudo apt install podman")


# --------------------------------------------------------- reading the steps ---

def comandos_do_documento(caminho: Path) -> list:
    """The shell blocks of a tutorial, in the order they are written.

    Only blocks the reader is meant to *type* come back. A `console` block is
    the answer, not the question, and running it would execute the machine's
    own output.
    """
    texto = Path(caminho).read_text(encoding="utf-8")
    passos, lingua, bloco = [], None, []
    for linha in texto.splitlines():
        m = RE_CERCA.match(linha)
        if m:
            if lingua is None:
                lingua, bloco = (m.group(1) or "").lower(), []
            else:
                if lingua in LINGUAGENS_ENTRADA:
                    passos += [l for l in bloco if l.strip()
                               and not l.strip().startswith("#")]
                lingua, bloco = None, []
            continue
        if lingua is not None:
            bloco.append(linha)
    return passos


# A base image runs as root and ships no `sudo`, so every `sudo apt install`
# in an honest tutorial would fail here for a reason that has nothing to do
# with the tutorial. Since `sudo cmd` run by root *is* `cmd`, a two-line
# passthrough lets the documented commands be tested exactly as written —
# which is the only version worth testing.
SHIM_SUDO = r"""if [ "$(id -u)" = 0 ] && ! command -v sudo >/dev/null 2>&1; then
  printf '#!/bin/sh\nexec "$@"\n' > /usr/local/bin/sudo && chmod +x /usr/local/bin/sudo
fi"""


def roteiro(comandos: list, parar_no_erro: bool, shim_sudo: bool = True) -> str:
    """The bash script the container runs — one fenced step per command."""
    linhas = [
        "#!/usr/bin/env bash",
        # Error messages are the most valuable output a step produces, and they
        # arrive on stderr — a separate stream, which the engine hands back
        # unmerged and therefore unattributable to any step. Folding it into
        # stdout inside the container is what keeps `command not found` next to
        # the command that was not found.
        "exec 2>&1",
        "export DEBIAN_FRONTEND=noninteractive",
        "",
    ]
    if shim_sudo:
        linhas += [SHIM_SUDO, ""]
    for i, comando in enumerate(comandos, 1):
        linhas += [
            "printf '\\n%sBEGIN %d\\n' " % (MARCA, i),
            comando,
            "__tf_rc=$?",
            "printf '\\n%sEND %d %%d\\n' \"$__tf_rc\"" % (MARCA, i),
        ]
        if parar_no_erro:
            linhas.append('[ "$__tf_rc" -eq 0 ] || exit "$__tf_rc"')
        linhas.append("")
    return "\n".join(linhas)


RE_BEGIN = re.compile(r"^%sBEGIN (\d+)$" % re.escape(MARCA))
RE_END = re.compile(r"^%sEND (\d+) (-?\d+)$" % re.escape(MARCA))


def separar(saida: str, comandos: list) -> list:
    """Splits the raw transcript back into one record per command."""
    registros = [{"n": i, "comando": c, "saida": [], "codigo": None}
                 for i, c in enumerate(comandos, 1)]
    atual = None
    for linha in saida.splitlines():
        inicio = RE_BEGIN.match(linha.strip())
        if inicio:
            atual = registros[int(inicio.group(1)) - 1]
            continue
        fim = RE_END.match(linha.strip())
        if fim:
            registros[int(fim.group(1)) - 1]["codigo"] = int(fim.group(2))
            atual = None
            continue
        if atual is not None:
            atual["saida"].append(linha)
    for r in registros:
        while r["saida"] and not r["saida"][0].strip():
            r["saida"].pop(0)
        while r["saida"] and not r["saida"][-1].strip():
            r["saida"].pop()
    return registros


# --------------------------------------------------------------- the container ---

def executar(engine: list, imagem: str, script: str, rede: bool,
             privilegiado: bool, montar: str, tempo: int) -> tuple:
    cmd = engine + ["run", "--rm", "-i"]
    if not rede:
        cmd += ["--network", "none"]
    else:
        # A machine behind a corporate proxy reaches the internet only through
        # it, and the container inherits nothing. Forward the proxy variables
        # the host already has, so the documented commands run as written
        # instead of failing on a network the reader does not have.
        for nome in ("http_proxy", "https_proxy", "no_proxy"):
            # Tools disagree on case: curl reads `https_proxy` and `HTTPS_PROXY`
            # but ignores `HTTP_PROXY` on purpose, apt reads the lowercase pair.
            # Pass whichever the host has under both spellings.
            valor = os.environ.get(nome) or os.environ.get(nome.upper())
            if valor:
                cmd += ["-e", "%s=%s" % (nome, valor),
                        "-e", "%s=%s" % (nome.upper(), valor)]
    if privilegiado:
        cmd += ["--privileged"]
    if montar:
        origem, _, destino = montar.partition(":")
        cmd += ["-v", "%s:%s" % (Path(origem).expanduser().resolve(),
                                 destino or "/mnt/host")]
    # The script arrives on stdin. Prefer bash, because that is the shell
    # tutorials are written for, and fall back to the POSIX shell for images
    # that ship no bash at all (Alpine). `exec` keeps stdin attached, so the
    # replacement shell reads the same script.
    cmd += [imagem, "/bin/sh", "-c",
            "command -v bash >/dev/null 2>&1 && exec bash -s || exec sh -s"]

    try:
        proc = subprocess.run(cmd, input=script, capture_output=True, text=True,
                              errors="replace", timeout=tempo)
    except subprocess.TimeoutExpired:
        return "", "timed out after %d s" % tempo, 124
    except OSError as exc:
        return "", str(exc), 125
    return proc.stdout, proc.stderr, proc.returncode


# -------------------------------------------------------------------- report ---

def imprimir(registros: list, imagem: str) -> int:
    falhas = [r for r in registros if r["codigo"] not in (0, None)]
    nao_rodou = [r for r in registros if r["codigo"] is None]
    print()
    print("== Transcript · %s ==" % imagem)
    for r in registros:
        estado = ("não rodou" if r["codigo"] is None
                  else "ok" if r["codigo"] == 0 else "FALHOU (%d)" % r["codigo"])
        print("\n[%02d] %-9s %s" % (r["n"], estado, r["comando"]))
        for linha in r["saida"][:40]:
            print("     | %s" % linha)
        if len(r["saida"]) > 40:
            print("     | ... (%d more lines)" % (len(r["saida"]) - 40))
    print()
    print("%d step(s): %d ok, %d failed, %d never ran."
          % (len(registros), len(registros) - len(falhas) - len(nao_rodou),
             len(falhas), len(nao_rodou)))
    if falhas:
        print("A failed step is a step that cannot be published as written.")
    return 1 if falhas else 0


def escrever_relatorio(destino: Path, registros: list, imagem: str,
                       fonte: str) -> None:
    """The evidence, in Markdown, ready to be read next to the document."""
    agora = datetime.now()
    falhas = [r for r in registros if r["codigo"] not in (0, None)]
    linhas = [
        "# Verificação — %s" % imagem,
        "",
        "| Campo | Valor |",
        "|---|---|",
        "| Imagem base | `%s` |" % imagem,
        "| Passos executados | %d |" % len(registros),
        "| Falharam | %d |" % len(falhas),
        "| Data da execução | %s |" % agora.strftime("%d/%m/%Y %H:%M"),
    ]
    if fonte:
        linhas.append("| Origem dos passos | `%s` |" % fonte)
    linhas += [
        "",
        "> Gerado por `tools/sandbox.py`. Cada bloco abaixo é a execução real,",
        "> em um contêiner descartável, do comando que o documento manda dar.",
        "",
    ]
    for r in registros:
        estado = ("não rodou" if r["codigo"] is None
                  else "ok" if r["codigo"] == 0 else "falhou (%d)" % r["codigo"])
        linhas += ["## Passo %02d — %s" % (r["n"], estado),
                   "", "```bash", r["comando"], "```", ""]
        if r["saida"]:
            linhas += ["```console", "\n".join(r["saida"][:200]), "```", ""]
    Path(destino).write_text("\n".join(linhas), encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Runs the documented steps for real in a throwaway "
                    "container, and reports what actually happened.")
    p.add_argument("--image", default="", help="base image (see --list)")
    p.add_argument("-c", "--command", action="append", default=[],
                   help="one command to run; repeat for more, in order")
    p.add_argument("--script", default="",
                   help="file with one command per line")
    p.add_argument("--from-doc", default="",
                   help="extract and run the shell blocks of a tutorial")
    p.add_argument("--report", default="",
                   help="write the evidence to this Markdown file")
    p.add_argument("--engine", default="", choices=["", "docker", "podman"],
                   help="container engine (default: docker, then podman)")
    p.add_argument("--network", action="store_true",
                   help="give the container network access — installing "
                        "anything needs it")
    p.add_argument("--privileged", action="store_true",
                   help="run privileged; only for steps that truly need it")
    p.add_argument("--mount", default="",
                   help="<host path>[:<container path>] to mount read-write")
    p.add_argument("--timeout", type=int, default=1800,
                   help="give up after this many seconds (default: 1800)")
    p.add_argument("--continue-on-error", action="store_true",
                   help="keep going after a failed step")
    p.add_argument("--no-sudo-shim", action="store_true",
                   help="do not provide the root passthrough for `sudo`; the "
                        "documented commands then fail exactly as they would "
                        "on an image without sudo installed")
    p.add_argument("--list", action="store_true",
                   help="show the base images kept at hand, then exit")
    args = p.parse_args(argv)

    if args.list:
        print("Base images (any other one the engine can pull also works):")
        for nome, descricao in IMAGENS:
            print("  %-38s %s" % (nome, descricao))
        print()
        print("Installing anything needs --network.")
        return 0

    comandos = list(args.command)
    if args.script:
        comandos += [l for l in Path(args.script).read_text(
            encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")]
    if args.from_doc:
        caminho = Path(args.from_doc).expanduser()
        if not caminho.is_file():
            erro("document not found: %s" % caminho)
        comandos += comandos_do_documento(caminho)
    if not comandos:
        erro("nothing to run. Use -c, --script or --from-doc.")
    if not args.image:
        erro("name the base image with --image (see --list).")

    engine = motor(args.engine)
    print("Engine : %s" % engine[0])
    print("Image  : %s" % args.image)
    print("Steps  : %d" % len(comandos))
    print("Network: %s" % ("on" if args.network else "off (use --network to "
                                                     "install anything)"))

    saida, stderr, codigo = executar(
        engine, args.image,
        roteiro(comandos, not args.continue_on_error, not args.no_sudo_shim),
        args.network, args.privileged, args.mount, args.timeout)
    # Not one step marker came back: the container never got as far as running
    # the script — a missing image, an engine that refused, a timeout. Printing
    # a transcript of steps that "did not run" would bury that under noise.
    if MARCA not in saida:
        print("\nThe container did not run the steps — nothing was tested.",
              file=sys.stderr)
        print((saida + "\n" + stderr).strip()[:2000] or "(no output)",
              file=sys.stderr)
        return codigo or 1

    registros = separar(saida + "\n" + stderr, comandos)
    estado = imprimir(registros, args.image)
    if args.report:
        escrever_relatorio(Path(args.report), registros, args.image,
                           args.from_doc)
        print("Evidence written to %s" % args.report)
    return estado


if __name__ == "__main__":
    sys.exit(main())
