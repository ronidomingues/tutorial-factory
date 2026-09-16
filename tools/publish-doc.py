#!/usr/bin/env python3
"""publish-doc.py — turns a tutorial written in Markdown into a book-grade
document in LaTeX and PDF, wearing the identity of the installed brand kit.

    python3 tools/publish-doc.py docker
    python3 tools/publish-doc.py docker --piece manual
    python3 tools/publish-doc.py docker --date 2026-09-16 --ai-model "Opus 5"
    python3 tools/publish-doc.py --doctor

Each software gets one folder under the documentation root, and each folder
holds two pieces, in three formats:

    documentation/docker/
      installation_2026-09-16.{md,tex,pdf}
      manual_2026-09-16.{md,tex,pdf}
      tema/                        the identity applied, so the .tex rebuilds
      LEIA-ME.md                   what is here and how to redo it

What it does, for each piece, in this order:

  1. reads the brand kit's `brand.env` and writes `tema/brand-env.tex`;
  2. copies the theme (the `.sty` and the logos in PDF) into `tema/`;
  3. resolves the typefaces — installed on the system, or copied from the kit;
  4. splits the single Markdown file into chapters at `##`, in a scratch
     folder, so the PDF comes out as a real book with a table of contents;
  5. calls md2book to generate the LaTeX and compile the PDF;
  6. flattens the result into ONE self-contained `.tex` next to the `.md`,
     and puts the `.pdf` beside it.

NON-NEGOTIABLE RULE: this program **never deletes or rewrites** the tutorial's
Markdown. The `.md` is the source of truth; the `.tex` and the `.pdf` derive
from it and are regenerated whenever it changes.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common                                    # noqa: E402

BRAND = common.find_brand()                      # where the identity lives

THEME_DIR = "tema"
BUILD_DIR = ".build"
FONT_DIR = "fontes"

# From the scratch build folder (<software>/.build/<stem>/out) back to the
# software folder. The flattened .tex sits one level up from `tema/`, so every
# path that points at the theme is rewritten by this prefix on the way out.
BUILD_TO_SOFTWARE = "../../../"

MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro")

RE_PIECE_FILE = re.compile(r"^(?P<stem>[a-z]+)_(?P<data>\d{4}-\d{2}-\d{2})\.md$")

# The metadata macros a brand kit may rely on. Kept in one place because the
# .sty files and this list are two halves of the same contract.
DOC_MACROS = ["cftitle", "cfsubtitle", "cfsubject", "cfversion", "cfdate",
              "cfproduced", "cfyear", "cflevel", "cfpiece", "cfadvisor",
              "cfagent", "cfaimodel", "cflicense", "cfrepo", "cfextent",
              "cfnote", "cfcourse", "cflecture", "cfassets"]


# ------------------------------------------------------------------ helpers ---

def erro(msg, codigo=2):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(codigo)


def aviso(msg):
    print("WARNING: %s" % msg, file=sys.stderr)


def escapar_tex(texto: str) -> str:
    for de, para in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                     ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                     ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}")):
        texto = texto.replace(de, para)
    return texto


def data_extenso(d: date) -> str:
    return "%d de %s de %d" % (d.day, MESES[d.month - 1], d.year)


def data_extenso_iso(iso: str) -> str:
    """"2026-09-16" -> "16 de setembro de 2026". Empty stays empty."""
    if not iso:
        return ""
    try:
        ano, mes, dia = (int(x) for x in iso.split("-"))
        return "%d de %s de %d" % (dia, MESES[mes - 1], ano)
    except (ValueError, IndexError):
        return iso


def slugificar(texto: str, limite: int = 48) -> str:
    """"2. Instalação no Ubuntu" -> "instalacao-no-ubuntu"."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    limpo = re.sub(r"[^a-zA-Z0-9]+", "-", sem_acento).strip("-").lower()
    limpo = re.sub(r"^\d+-", "", limpo)          # "2-instalacao" -> "instalacao"
    return (limpo[:limite].rstrip("-")) or "secao"


def mesclar(base: dict, extra: dict) -> dict:
    saida = json.loads(json.dumps(base))
    for chave, valor in extra.items():
        if isinstance(valor, dict) and isinstance(saida.get(chave), dict):
            saida[chave] = mesclar(saida[chave], valor)
        else:
            saida[chave] = valor
    return saida


def fonte_instalada(familia: str) -> bool:
    """Is the family installed system-wide? Decides between using and shipping."""
    if not shutil.which("fc-list"):
        return False
    try:
        saida = subprocess.run(["fc-list", ":", "family"], capture_output=True,
                               text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    alvo = familia.replace(" ", "").lower()
    for linha in saida.splitlines():
        for nome in linha.split(","):
            if nome.strip().replace(" ", "").lower() == alvo:
                return True
    return False


def paginas(pdf: Path) -> int:
    if not pdf or not Path(pdf).is_file() or not shutil.which("pdfinfo"):
        return 0
    saida = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                           text=True).stdout
    for linha in saida.splitlines():
        if linha.startswith("Pages:"):
            return int(linha.split()[1])
    return 0


# --------------------------------------------------------- finding the source ---

def achar_software(argumento: str, raiz: Path) -> Path:
    """Accepts a path or the bare software name ("docker")."""
    alvo = Path(argumento).expanduser()
    if alvo.is_dir():
        return alvo.resolve()
    candidato = raiz / argumento
    if candidato.is_dir():
        return candidato.resolve()
    disponiveis = sorted(p.name for p in raiz.glob("*")
                         if p.is_dir() and not p.name.startswith(".")) \
        if raiz.is_dir() else []
    erro("no documentation folder for %r.\n"
         "  Looked in: %s\n"
         "  Available: %s\n"
         "  The documentation root is set by the %s pointer at the repository\n"
         "  root, or by --docs <path>."
         % (argumento, raiz, ", ".join(disponiveis) or "(none yet)",
            common.DOCS_POINTER))


def achar_peca(pasta: Path, peca: str, data: str = "") -> Path:
    """The `<stem>_<date>.md` of one piece — the newest, unless pinned."""
    stem = common.PIECES[peca]["stem"]
    if data:
        alvo = pasta / ("%s_%s.md" % (stem, data))
        return alvo if alvo.is_file() else None
    achados = sorted(p for p in pasta.glob("%s_*.md" % stem)
                     if RE_PIECE_FILE.match(p.name))
    return achados[-1] if achados else None


# ------------------------------------------------------- reading the Markdown ---

# CommonMark allows a fence to be indented by up to three spaces; the fourth
# makes it an indented code block instead. Accepting any indentation, as a
# looser pattern would, turns a ``` written inside a prose comment into an
# opening fence that never closes — and swallows the rest of the document.
RE_CERCA = re.compile(r"^ {0,3}(?:`{3,}|~{3,})")
RE_TITULO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")

_METADADO = re.compile(
    r"^\s*(\*\*)?\s*(n[íi]vel|data|status|[úu]ltima atualiza|vers|testado em|"
    r"escrito em|produzido em|verificado em|aviso|level|updated)", re.I)


def _limpar_marcacao(texto: str) -> str:
    texto = re.sub(r"\[(.+?)\]\([^)]*\)", r"\1", texto)
    texto = re.sub(r"\*\*(.+?)\*\*", r"\1", texto)
    return re.sub(r"\s+", " ", re.sub(r"[`*_]", "", texto)).strip(" ·—–-")


def _encurtar(texto: str, limite: int = 200) -> str:
    """Cuts at the end of a sentence; blind truncation only as a last resort."""
    if len(texto) <= limite:
        return texto
    trecho = texto[:limite]
    for fim in (". ", "? ", "! ", "; "):
        pos = trecho.rfind(fim)
        if pos >= 60:
            return trecho[:pos + 1].strip()
    return trecho.rsplit(" ", 1)[0].rstrip(" ,;:·-") + "…"


def remover_comentarios_html(texto: str) -> str:
    """Drops `<!-- ... -->` blocks written outside fenced code.

    A Markdown comment is an instruction to whoever edits the file — the
    skeleton's own format notes are exactly that. It is invisible on GitHub, so
    an author reasonably assumes it is invisible everywhere; without this it
    would be typeset into the PDF as body text. Comments *inside* a code block
    are content, not commentary, and stay.
    """
    saida, dentro_da_cerca, cerca, comentando = [], False, "", False
    for linha in texto.splitlines():
        m = RE_CERCA.match(linha)
        if m and not comentando:
            marca = m.group(0).strip()[:3]
            if not dentro_da_cerca:
                dentro_da_cerca, cerca = True, marca
            elif marca == cerca:
                dentro_da_cerca = False
            saida.append(linha)
            continue
        if dentro_da_cerca:
            saida.append(linha)
            continue

        resto = linha
        limpo = []
        while resto:
            if comentando:
                fim = resto.find("-->")
                if fim < 0:
                    resto = ""
                    break
                resto, comentando = resto[fim + 3:], False
                continue
            inicio = resto.find("<!--")
            if inicio < 0:
                limpo.append(resto)
                break
            limpo.append(resto[:inicio])
            resto, comentando = resto[inicio + 4:], True
        junto = "".join(limpo)
        if junto.strip() or not linha.strip():
            saida.append(junto.rstrip())
    return "\n".join(saida)


def dividir_em_capitulos(texto: str):
    """Splits one Markdown file into (title, subtitle, opening, chapters).

    A tutorial is written as a single file — that is the contract with whoever
    reads the `.md`. A book is made of chapters — that is what a table of
    contents, a running head and a page break need. The two are reconciled
    here, mechanically and without losing a byte: the `#` is the title, every
    `##` becomes a chapter, and everything below it moves up one level so the
    hierarchy inside the chapter stays exactly as it was written.

    Whatever sits between the title and the first `##` becomes an unnumbered
    opening chapter. Fenced code is never read as a heading.
    """
    linhas = remover_comentarios_html(texto).splitlines()
    titulo, subtitulo = "", ""
    abertura, capitulos = [], []
    atual = None
    dentro_da_cerca = False
    cerca = ""

    for linha in linhas:
        m_cerca = RE_CERCA.match(linha)
        if m_cerca:
            marca = m_cerca.group(0).strip()[:3]
            if not dentro_da_cerca:
                dentro_da_cerca, cerca = True, marca
            elif marca == cerca:
                dentro_da_cerca = False
            (atual["linhas"] if atual else abertura).append(linha)
            continue
        if dentro_da_cerca:
            (atual["linhas"] if atual else abertura).append(linha)
            continue

        m = RE_TITULO.match(linha)
        if not m:
            (atual["linhas"] if atual else abertura).append(linha)
            continue

        nivel, bruto = len(m.group(1)), m.group(2).strip()
        if nivel == 1 and not titulo and atual is None:
            partes = re.split(r"\s+[—–]\s+", bruto, maxsplit=1)
            titulo = _limpar_marcacao(partes[0])
            if len(partes) > 1:
                subtitulo = _limpar_marcacao(partes[1])
            continue
        if nivel <= 2:                            # a new chapter starts here
            atual = {"titulo": _limpar_marcacao(bruto), "linhas": []}
            capitulos.append(atual)
            continue
        # Inside a chapter everything moves up one level: "###" was a section
        # under the "##" that became the chapter, so it is a section now.
        destino = atual["linhas"] if atual else abertura
        destino.append("#" * (nivel - 1) + " " + bruto)

    if not subtitulo:
        subtitulo = _primeiro_paragrafo(abertura)
    return titulo, subtitulo, abertura, capitulos


def _primeiro_paragrafo(linhas) -> str:
    """The first real sentence of the opening — not metadata, not a table."""
    bloco = []
    for linha in linhas[:60]:
        crua = linha.strip()
        if crua.startswith(">"):
            crua = crua.lstrip("> ").strip()
        if not crua:
            if bloco:
                break
            continue
        if (crua.startswith(("#", "|", "```", "~~~", "---", "- ", "* ", "1."))
                or _METADADO.match(crua)):
            if bloco:
                break
            continue
        bloco.append(crua)
    return _encurtar(_limpar_marcacao(" ".join(bloco)))


def escrever_fonte(fonte: Path, titulo: str, abertura, capitulos,
                   rotulo_abertura: str) -> int:
    """Writes the chapter files md2book will read. Returns how many."""
    if fonte.exists():
        shutil.rmtree(fonte)
    fonte.mkdir(parents=True)

    if "".join(abertura).strip():
        (fonte / "00-abertura.md").write_text(
            "# %s\n\n%s\n" % (rotulo_abertura, "\n".join(abertura).strip()),
            encoding="utf-8")

    if not capitulos:
        # A tutorial with no `##` at all is still a document: it becomes one
        # chapter, named after the title, rather than an empty book.
        (fonte / "01-documento.md").write_text(
            "# %s\n\n%s\n" % (titulo or "Documento",
                              "\n".join(abertura).strip()), encoding="utf-8")
        return 1

    for i, cap in enumerate(capitulos, 1):
        nome = "%02d-%s.md" % (i, slugificar(cap["titulo"]))
        corpo = "\n".join(cap["linhas"]).strip()
        (fonte / nome).write_text("# %s\n\n%s\n" % (cap["titulo"], corpo),
                                  encoding="utf-8")
    return len(capitulos)


# Fenced blocks in these languages hold commands someone will type. Counting
# them is the one number that says whether a tutorial is a walkthrough or an
# essay about a walkthrough.
LINGUAGENS_SHELL = {"bash", "sh", "shell", "zsh", "fish", "console",
                    "powershell", "pwsh", "cmd", "bat", "batch", "dos"}

RE_ABERTURA_CERCA = re.compile(r"^ {0,3}(?:`{3,}|~{3,})\s*([A-Za-z0-9_+-]*)")


def contar_comandos(texto: str) -> int:
    """Executable lines inside shell code blocks — comments and output apart.

    A `console` block shows what came back, so only its prompted lines count;
    a `bash` block is meant to be typed, so every line of it does.
    """
    total, lingua = 0, None
    for linha in texto.splitlines():
        m = RE_ABERTURA_CERCA.match(linha)
        if m:
            marca = (m.group(1) or "").lower()
            lingua = None if lingua is not None else marca
            continue
        if lingua not in LINGUAGENS_SHELL:
            continue
        corpo = linha.strip()
        if not corpo or corpo.startswith("#"):
            continue
        if lingua in ("console", "cmd", "bat", "batch", "dos") and \
                not corpo.startswith(("$", ">", "PS ", "C:\\")):
            continue                     # that line is output, not a command
        total += 1
    return total


def plural(n: int, singular: str, plural_: str) -> str:
    return "%d %s" % (n, singular if n == 1 else plural_)


def medir(texto: str, capitulos: int) -> str:
    """"14 capítulos · 1.820 linhas · 96 comandos" — the real extent."""
    linhas = len(texto.splitlines())
    pedacos = [plural(capitulos, "capítulo", "capítulos"),
               "%s linhas" % "{:,}".format(linhas).replace(",", ".")]
    comandos = contar_comandos(texto)
    if comandos:
        pedacos.append(plural(comandos, "comando", "comandos"))
    return " · ".join(pedacos)


# --------------------------------------------------------------------- theme ---

def exigir_marca() -> None:
    """Refuses to publish with a brand kit that does not meet the contract."""
    if not BRAND.exists():
        erro("no brand kit found.\n"
             "  Expected at: %s\n"
             "  Install one (see docs/03-kit-de-marca.md) or pass --brand <path>.\n"
             "  The repository ships a neutral pre-mold at %s."
             % (common.tools_dir() / common.BRAND_SLOT,
                common.tools_dir() / common.BRAND_SLOT / common.BRAND_TEMPLATE))
    gaps = BRAND.missing()
    if gaps:
        erro("the brand kit at %s does not meet the contract.\n"
             "  Missing: %s\n"
             "  See docs/03-kit-de-marca.md." % (BRAND.root, ", ".join(gaps)))
    if BRAND.origin == "template":
        aviso("publishing with the neutral pre-mold — this material is signed "
              "by nobody.\n"
              "  Install your own kit: python3 tools/sync-brand.py "
              "--from-template\n"
              "  See docs/03-kit-de-marca.md.")


def cores_latex(env: dict) -> list:
    r"""The `\definecolor` lines for every colour declared in brand.env.

    They land in `brand-env.tex`, which the `.sty` inputs **after** its own
    defaults — so what the kit's `brand.env` says wins, and recolouring a brand
    is editing one file instead of hunting fourteen `\definecolor`.
    """
    cores = common.brand_colors(env)
    if not cores:
        return []
    for chave, bruto in sorted(env.items()):
        if chave.startswith(common.COLOR_PREFIX) and not common.read_hex(bruto):
            aviso("%s is not a six-digit hex colour (%r) — ignored."
                  % (chave, bruto))
    linhas = ["%% ----------------------------------------------- brand colours --",
              "%% Declared in brand.env; they override the .sty defaults."]
    linhas += [r"\definecolor{%s}{HTML}{%s}" % (nome, valor)
               for nome, valor in sorted(cores.items())]
    return linhas


def preparar_tema(pasta: Path, env: dict, politica: str) -> dict:
    """Copies the theme next to the documents and returns the font settings.

    The theme is copied rather than reached by an absolute path because the
    `.tex` has to stay compilable on another machine and a year from now —
    including by someone who never had the brand repository.
    """
    tema = pasta / THEME_DIR
    (tema / "assets").mkdir(parents=True, exist_ok=True)

    for sty in sorted(BRAND.latex.glob("*.sty")):
        shutil.copyfile(sty, tema / sty.name)
    if BRAND.assets.is_dir():
        for logo in sorted(BRAND.assets.glob("*.pdf")):
            shutil.copyfile(logo, tema / "assets" / logo.name)

    escrever_brand_env(tema / "brand-env.tex", env)
    return resolver_fontes(tema, politica)


def escrever_brand_env(destino: Path, env: dict) -> None:
    """The brand half of the identity: what every document here shares.

    The *document* half — title, piece, dates, agent — is not written here on
    purpose: two documents share this folder, and a file that claimed to hold
    the title would be right for one of them and wrong for the other. Those
    macros go into each `.tex` preamble instead.
    """
    def d(macro, valor):
        return r"\def\%s{%s}" % (macro, escapar_tex(str(valor or "")))

    linhas = [
        "%% Generated by tools/publish-doc.py — DO NOT EDIT.",
        "%% Source: brand.env of the installed brand kit.",
        "%% Shared by every document in this folder.",
        "%% ---------------------------------------------------------------",
        d("cfBrand", env.get("BRAND_NAME", "")),
        d("cfBrandLower", env.get("BRAND_NAME_LOWER", "")),
        d("cfTagline", env.get("BRAND_TAGLINE", "")),
        d("cfDescriptor", env.get("BRAND_DESCRIPTOR", "")),
        d("cfOwner", env.get("BRAND_OWNER", "")),
        d("cfAuthor", env.get("BRAND_AUTHOR", "")),
        d("cfEmail", env.get("BRAND_EMAIL", "")),
        d("cfSite", env.get("BRAND_SITE", "")),
        d("cfSiteURL", env.get("BRAND_SITE_URL", "")),
        # The prompt is raw LaTeX by design: it is a graphic element, not text.
        r"\def\cfPrompt{%s}" % (env.get("BRAND_PROMPT", "") or r"\$"),
    ] + cores_latex(env) + [r"\endinput", ""]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas), encoding="utf-8")


def resolver_fontes(tema: Path, politica: str) -> dict:
    """Decides where the brand typefaces come from on this machine.

    An installed font takes no disk space but vanishes when the folder travels;
    a copied font travels along but weighs a few MB. `auto` uses what is
    installed and copies only when nothing is — and the documentation folder is
    exactly the kind of thing that gets zipped and sent to someone.
    """
    spec = BRAND.font_spec()
    families = spec.get("families", {})
    destino = tema / FONT_DIR

    if not families:
        print("  fonts: as declared by the brand kit (no files shipped)")
        if destino.is_dir():
            shutil.rmtree(destino)
        return {}

    sistema = dict(spec.get("system", {}))
    checar = spec.get("check") or [v for k, v in sistema.items()
                                   if k != "simbolos"]
    instaladas = all(fonte_instalada(f) for f in checar)

    if politica == "system" or (politica == "auto" and instaladas):
        if not instaladas:
            aviso("--fonts system, but %s are not installed: LaTeX will fail "
                  "or substitute the typeface." % ", ".join(checar))
        print("  fonts: the brand's, installed system-wide")
        if destino.is_dir():
            shutil.rmtree(destino)
        return sistema

    if not BRAND.fonts.is_dir():
        aviso("brand fonts not found at %s — the material will come out in "
              "DejaVu, off-identity." % BRAND.fonts)
        return {"texto": "DejaVu Serif", "titulo": "DejaVu Sans",
                "mono": "DejaVu Sans Mono", "simbolos": "DejaVu Sans"}

    destino.mkdir(parents=True, exist_ok=True)
    for familia in families.values():
        for arquivo in familia.get("files", []):
            origem = BRAND.fonts / arquivo
            if origem.is_file():
                shutil.copyfile(origem, destino / arquivo)
    for licenca in list(BRAND.fonts.glob("LICENCA-*.txt")) + \
            list(BRAND.fonts.glob("LICENSE-*.txt")):
        shutil.copyfile(licenca, destino / licenca.name)
    print("  fonts: copied into %s/%s (the folder travels complete)"
          % (THEME_DIR, FONT_DIR))

    embedded = dict(spec.get("embedded", sistema))
    config = {
        # Relative to where LaTeX compiles — the scratch folder. The flattener
        # rewrites it for the .tex that ships next to the .md.
        "diretorio": "%s%s/%s" % (BUILD_TO_SOFTWARE, THEME_DIR, FONT_DIR),
        "extensao": spec.get("extension", ".ttf"),
    }
    config.update(embedded)
    for papel in ("texto", "titulo", "mono"):
        familia = families.get(embedded.get(papel, ""))
        if familia and familia.get("faces"):
            config["%s_faces" % papel] = familia["faces"]
    return config


# ----------------------------------------------------------------- publishing ---

def preambulo_do_documento(meta: dict) -> str:
    """The macros that describe THIS document, emitted into its own preamble."""
    linhas = [
        "%% --------------------------------------- dados deste documento ---",
        "%% Escrito por tools/publish-doc.py. Um kit de marca que não conheça",
        "%% um destes campos simplesmente o ignora.",
    ]
    linhas += [r"\providecommand{\%s}[1]{}" % m for m in DOC_MACROS]
    linhas += [
        r"\cfassets{assets}",
        r"\cftitle{%s}" % escapar_tex(meta["titulo"]),
        r"\cfsubtitle{%s}" % escapar_tex(meta["subtitulo"]),
        r"\cfsubject{%s}" % escapar_tex(meta["software"]),
        r"\cfversion{%s}" % escapar_tex(meta["versao"]),
        r"\cfdate{%s}" % escapar_tex(meta["data"]),
        r"\cfproduced{%s}" % escapar_tex(meta["data_documento"]),
        r"\cfyear{%s}" % escapar_tex(meta["ano"]),
        r"\cflevel{%s}" % escapar_tex(meta["nivel"]),
        r"\cfpiece{%s}" % escapar_tex(meta["peca"]),
        r"\cfadvisor{%s}" % escapar_tex(meta["orientador"]),
        r"\cfagent{%s}" % escapar_tex(meta["agente"]),
        r"\cfaimodel{%s}" % escapar_tex(meta["modelo"]),
        r"\cflicense{%s}" % escapar_tex(meta["licenca"]),
        r"\cfrepo{%s}" % escapar_tex(meta["repositorio"]),
        r"\cfextent{%s}" % escapar_tex(meta["extensao"]),
        r"\cfnote{%s}" % escapar_tex(meta["nota"]),
        r"\cfcourse{%s}" % escapar_tex(meta["titulo"]),
    ]
    return "\n".join(linhas)


def montar_config(pasta: Path, build: Path, meta: dict, config_fontes: dict,
                  cores: dict, tem_abertura: bool) -> dict:
    """The md2book configuration for one piece, over the brand kit's base.

    The kit's `book.base.json` is a course's shape — numbered blocks, parts,
    a source-code appendix. Everything structural is replaced here; everything
    that is *identity* — colours, typography, geometry, cover command,
    colophon — is kept exactly as the kit declares it. That is the line between
    the two: the factory decides the anatomy, the kit decides the looks.
    """
    base = json.loads((BRAND.templates / "book.base.json").read_text("utf-8"))
    base.pop("_comentario", None)
    tema = (pasta / THEME_DIR).resolve()

    config = mesclar(base, {
        "titulo": meta["titulo"],
        "subtitulo": meta["subtitulo"],
        "autor": meta["orientador"],
        "ano": meta["ano"],
        "nota_capa": meta["nota"],
        "nome_arquivo": meta["stem"],

        "raiz": "fonte",
        "saida": "../out",
        "ignorar": ["**/.git/**"],
        "abertura": ["00-abertura.md"] if tem_abertura else [],
        "partes": [],
        "incluir_restantes": True,
        "titulo_restantes": "",
        "apendice_fontes": {"ativo": False, "padroes": []},

        # A tutorial is consulted, not read front to back: the table of
        # contents has to reach the section that answers the question, not
        # just the chapter that contains it.
        "profundidade_sumario": 2,
        "profundidade_numeracao": 2,

        "recursos": [str(tema / "coursebook.sty"),
                     str(tema / "brand-env.tex"),
                     str(tema / "assets")],
        "pacotes_extra": ["coursebook"],
        "preambulo_extra": preambulo_do_documento(meta),
        "fontes": mesclar(base.get("fontes", {}), config_fontes),
    })
    config.update(cores)          # brand.env wins over the kit's base JSON
    (build / "doc.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    return config


RE_INPUT = re.compile(r"^\\input\{tex/(?P<nome>[^}]+)\}\s*$", re.M)
RE_DOCCLASS = re.compile(r"^\\documentclass.*$", re.M)

CABECALHO_PLANO = r"""%% ---------------------------------------------------------------------
%%  Documento autocontido: todos os capítulos estão neste arquivo.
%%  O tema da marca (coursebook.sty, brand-env.tex, assets/) fica em tema/,
%%  ao lado deste .tex — é o que permite recompilar sem o kit de marca:
%%
%%      xelatex %(arquivo)s     (rode duas ou três vezes, pelo sumário)
%%
%%  Gerado por tools/publish-doc.py a partir de %(fonte)s.
%%  Editar aqui funciona até a próxima publicação: a fonte da verdade é o .md.
%% ---------------------------------------------------------------------
\makeatletter
\def\input@path{{tema/}{./}}
\makeatother"""


def achatar_tex(build_out: Path, destino: Path, fonte_md: str) -> bool:
    r"""Turns md2book's `main.tex` + `tex/*.tex` into ONE deliverable file.

    A `.tex` that only compiles inside a scratch folder is not a deliverable,
    it is a by-product. Inlining the chapters and repointing the theme at
    `tema/` is what makes the third format as real as the other two: the person
    who receives the folder can open the `.tex`, read it, edit it and compile
    it — with nothing else installed but LaTeX.
    """
    main = build_out / "main.tex"
    if not main.is_file():
        return False
    texto = main.read_text(encoding="utf-8")

    def inlinar(m):
        parte = build_out / "tex" / ("%s.tex" % m.group("nome"))
        if not parte.is_file():
            aviso("chapter %s missing from the build — the .tex will have a "
                  "hole in it." % m.group("nome"))
            return m.group(0)
        corpo = parte.read_text(encoding="utf-8")
        corpo = re.sub(r"^%%.*\n", "", corpo)      # md2book's per-file header
        return ("%%%% ---- %s ----------------------------------------------\n%s"
                % (m.group("nome"), corpo.rstrip()))

    texto = RE_INPUT.sub(inlinar, texto)
    # The theme moved one level up relative to where this file now lives.
    texto = texto.replace(r"\cfassets{assets}",
                          r"\cfassets{%s/assets}" % THEME_DIR)
    texto = texto.replace(BUILD_TO_SOFTWARE, "")
    cabecalho = CABECALHO_PLANO % {"arquivo": destino.name, "fonte": fonte_md}
    texto = RE_DOCCLASS.sub(lambda m: m.group(0) + "\n\n" + cabecalho, texto,
                            count=1)
    destino.write_text(texto, encoding="utf-8")
    return True


def publicar_peca(pasta: Path, peca: str, args, env: dict,
                  config_fontes: dict, cores: dict) -> dict:
    """Publishes one piece. Returns what came out, for the report."""
    origem = achar_peca(pasta, peca, args.date)
    rotulo = common.PIECES[peca]["label"]
    if origem is None:
        return {"peca": peca, "rotulo": rotulo, "fonte": None}

    m = RE_PIECE_FILE.match(origem.name)
    stem, data_doc = m.group("stem"), m.group("data")
    nome_base = origem.stem                       # installation_2026-09-16
    print("\n== %s ==" % rotulo)
    print("  source: %s" % origem.name)

    texto = origem.read_text(encoding="utf-8")
    titulo, subtitulo, abertura, capitulos = dividir_em_capitulos(texto)
    if not titulo:
        aviso("%s has no `# ` title on the first line — using the file name."
              % origem.name)
        titulo = nome_base.replace("_", " ")

    build = pasta / BUILD_DIR / nome_base
    build.mkdir(parents=True, exist_ok=True)
    total = escrever_fonte(build / "fonte", titulo, abertura, capitulos,
                           args.opening_title)
    print("  %d chapter(s) from %d section heading(s)" % (total, len(capitulos)))

    hoje = date.today()
    meta = {
        "titulo": titulo,
        "subtitulo": subtitulo,
        "software": pasta.name,
        "stem": nome_base,
        "versao": args.doc_version,
        "data": data_extenso(hoje),
        "data_documento": data_extenso_iso(data_doc),
        "ano": str(hoje.year),
        "nivel": args.level or env.get("BRAND_DOC_LEVEL",
                                       "do zero absoluto ao uso profissional"),
        "peca": rotulo,
        "orientador": args.advisor or env.get("BRAND_OWNER", ""),
        "agente": args.agent,
        "modelo": args.ai_model,
        "licenca": args.license or env.get("BRAND_COURSE_LICENSE", ""),
        "repositorio": args.repo,
        "extensao": medir(texto, total),
        "nota": args.note,
    }
    montar_config(pasta, build, meta, config_fontes, cores,
                  bool("".join(abertura).strip()))

    comando = achar_md2book(args.md2book) + \
        ["livro" if not args.no_pdf else "tex",
         "-c", str(build / "doc.json"), "--ambiente", "ignorar"]
    proc = subprocess.run(comando)
    if proc.returncode != 0:
        aviso("md2book exited with code %d on %s." % (proc.returncode, peca))

    saida = build / "out"
    tex_final = pasta / ("%s.tex" % nome_base)
    pdf_final = pasta / ("%s.pdf" % nome_base)

    tex_ok = achatar_tex(saida, tex_final, origem.name)
    gerado = saida / ("%s.pdf" % nome_base)
    if gerado.is_file():
        shutil.move(str(gerado), str(pdf_final))
    elif not args.no_pdf:
        aviso("the PDF for %s was not produced — see the LaTeX log at %s."
              % (peca, saida / "main.log"))

    if not args.keep_build:
        shutil.rmtree(build, ignore_errors=True)
    limpar_intermediarios(pasta, nome_base)

    return {
        "peca": peca,
        "rotulo": rotulo,
        "fonte": origem,
        "titulo": titulo,
        "data": data_doc,
        "capitulos": total,
        "tex": tex_final if tex_ok else None,
        "pdf": pdf_final if pdf_final.is_file() else None,
        "paginas": paginas(pdf_final),
        "meta": meta,
    }


def limpar_intermediarios(pasta: Path, stem: str) -> None:
    """Removes LaTeX by-products of THIS document from the delivery folder.

    Nothing this program writes lands there — it compiles in the scratch
    folder. But whoever recompiles the `.tex` by hand, as the LEIA-ME invites
    them to, leaves an `.aux` and a `.log` behind, and a folder meant to be
    zipped and sent should not carry them. Only the extensions below, and only
    for this document's own name.
    """
    for extensao in (".aux", ".log", ".out", ".toc", ".lof", ".lot", ".fls",
                     ".fdb_latexmk", ".xdv", ".synctex.gz", ".bbl", ".blg"):
        alvo = pasta / (stem + extensao)
        if alvo.is_file():
            alvo.unlink()


def achar_md2book(indicado=None) -> list:
    cmd = common.find_md2book(indicado)
    if cmd:
        return cmd
    erro("md2book not found. It should be vendored at %s, or point the "
         "MD2BOOK variable at its folder, or pass --md2book <path>."
         % (common.tools_dir() / "md2book"))


# -------------------------------------------------------------------- report ---

def escrever_leiame(pasta: Path, resultados, env: dict, args) -> None:
    """Explains, inside the folder, what each file is and how to redo it."""
    linhas = [
        "# Documentação — %s" % pasta.name,
        "",
        "> **Os `.tex` e os `.pdf` desta pasta são gerados.** A fonte da verdade",
        "> é o `.md` de cada documento. Editar o `.tex` à mão funciona até a",
        "> próxima publicação; editar o `.md` e republicar funciona sempre.",
        "",
        "| Documento | Fonte | LaTeX | PDF | Páginas |",
        "|---|---|---|---|---|",
    ]
    for r in resultados:
        if not r.get("fonte"):
            linhas.append("| %s | *ainda não escrito* | — | — | — |" % r["rotulo"])
            continue
        linhas.append("| %s | `%s` | %s | %s | %s |" % (
            r["rotulo"], r["fonte"].name,
            "`%s`" % r["tex"].name if r.get("tex") else "—",
            "`%s`" % r["pdf"].name if r.get("pdf") else "—",
            r.get("paginas") or "—"))

    linhas += [
        "",
        "## Refazer",
        "",
        "```bash",
        "python3 tools/publish-doc.py %s" % pasta.name,
        "```",
        "",
        "Só uma das peças: `--piece installation` ou `--piece manual`.",
        "Só o LaTeX, sem compilar: `--no-pdf`.",
        "",
        "## Recompilar um `.tex` à mão",
        "",
        "Cada `.tex` é autocontido e usa o tema em `tema/`, nesta mesma pasta:",
        "",
        "```bash",
        "xelatex %s.tex" % (resultados[0]["fonte"].stem
                            if resultados and resultados[0].get("fonte")
                            else "<documento>"),
        "```",
        "",
        "Rode duas ou três vezes — o sumário só fecha na segunda passagem.",
        "",
        "| Pasta | O que tem dentro |",
        "|---|---|",
        "| `tema/` | A identidade aplicada: `coursebook.sty`, `brand-env.tex` e os logos. |",
        "",
        "## Créditos",
        "",
    ]
    orientador = args.advisor or env.get("BRAND_OWNER", "")
    if orientador:
        linhas.append("- **Autor e orientador:** %s" % orientador)
    linhas += [
        "- **Pesquisa, verificação e redação:** %s%s" % (
            args.agent, " (%s)" % args.ai_model if args.ai_model else ""),
        "- **Publicação:** %s%s" % (
            env.get("BRAND_NAME", ""),
            " — %s" % env.get("BRAND_TAGLINE", "")
            if env.get("BRAND_TAGLINE") else ""),
        "",
        "Gerado em %s." % data_extenso(date.today()),
        "",
    ]
    (pasta / "LEIA-ME.md").write_text("\n".join(linhas), encoding="utf-8")


# -------------------------------------------------------------------- doctor ---

def diagnostico(docs=None) -> int:
    """Says, in one screen, whether this machine can publish on its own."""
    print(BRAND.report())
    raiz = common.docs_root(docs)
    print("Docs     : %s (%s)%s"
          % (raiz, common.docs_origin(docs),
             "" if raiz.is_dir() else "  — folder does not exist yet"))
    print()
    md2book = common.find_md2book()
    linhas = [
        ("md2book", bool(md2book), " ".join(md2book) if md2book else
         "missing — no conversion without it"),
        ("brand kit", BRAND.exists() and not BRAND.missing(),
         "%s (%s)" % (BRAND.root, BRAND.origin) if BRAND.exists() else
         "missing — install one, see docs/03-kit-de-marca.md"),
        ("brand fonts", BRAND.has_fonts(),
         str(BRAND.fonts) if BRAND.has_fonts() else
         "kit ships none — it uses typefaces installed on the machine"),
        ("xelatex", bool(shutil.which("xelatex")),
         shutil.which("xelatex") or "missing — you get the .tex, not the PDF"),
        ("latexmk", bool(shutil.which("latexmk")),
         shutil.which("latexmk") or "missing — md2book drives the engine directly"),
        ("pdfinfo", bool(shutil.which("pdfinfo")),
         shutil.which("pdfinfo") or "missing — page counts will read 0"),
        ("docker/podman", bool(shutil.which("docker") or shutil.which("podman")),
         shutil.which("docker") or shutil.which("podman") or
         "missing — tools/sandbox.py cannot test the steps for real"),
    ]
    for nome, ok, detalhe in linhas:
        print("  %-14s %-8s %s" % (nome, "ok" if ok else "MISSING", detalhe))

    print()
    if all([linhas[0][1], linhas[1][1], bool(shutil.which("xelatex"))]):
        print("This machine can publish documentation on its own.")
        if not linhas[6][1]:
            print("It cannot TEST what it documents: install Docker or Podman,")
            print("or verify the steps on a real machine and say so in the text.")
        return 0
    print("Something essential is missing. On Debian/Ubuntu:")
    print("  sudo apt install texlive-xetex texlive-latex-extra "
          "texlive-lang-portuguese latexmk poppler-utils")
    return 1


# ---------------------------------------------------------------------- main ---

def main(argv=None) -> int:
    global BRAND
    p = argparse.ArgumentParser(
        description="Publishes a software's tutorials as book-grade documents "
                    "(Markdown + LaTeX + PDF), wearing the installed brand kit.")
    p.add_argument("software", nargs="?", default="",
                   help="the software folder under the documentation root")
    p.add_argument("--piece", choices=["all", "installation", "manual"],
                   default="all", help="which document to publish (default: all)")
    p.add_argument("--date", default="",
                   help="publish the edition of this date (default: the newest)")
    p.add_argument("--docs", default="",
                   help="documentation root (default: the %s pointer, else "
                        "documentation/)" % common.DOCS_POINTER)
    p.add_argument("--brand", default="",
                   help="path to the brand kit (default: "
                        "tools/course-factory-brand, then its template/)")
    p.add_argument("--md2book", help="path to md2book (repo or md2book.py)")
    p.add_argument("--doc-version", default="1.0",
                   help="version label of this publication")
    p.add_argument("--agent", default="Claude Code (Anthropic)",
                   help="the AI agent that researched and wrote the material")
    p.add_argument("--ai-model", default="", help="model the agent ran on")
    p.add_argument("--advisor", default="",
                   help="author and advisor (default: BRAND_OWNER from brand.env)")
    p.add_argument("--license", default="",
                   help="licence line printed on the credits page")
    p.add_argument("--repo", default="", help="source repository, for credits")
    p.add_argument("--note", default="", help="extra line on cover/credits")
    p.add_argument("--level", default="",
                   help="level line printed on the cover")
    p.add_argument("--opening-title", default="Apresentação",
                   help="chapter title for whatever precedes the first `##`")
    p.add_argument("--fonts", choices=["auto", "system", "folder"],
                   default="auto",
                   help="where the brand typefaces come from: auto (use the "
                        "installed ones, else copy); system; folder (always "
                        "copy into tema/fontes, so the folder travels whole)")
    p.add_argument("--no-pdf", action="store_true",
                   help="generate the LaTeX only, without compiling")
    p.add_argument("--keep-build", action="store_true",
                   help="keep the scratch folder, to inspect the LaTeX log")
    p.add_argument("--doctor", action="store_true",
                   help="show what this machine has and lacks, then exit")
    args = p.parse_args(argv)

    if args.brand:
        BRAND = common.find_brand(args.brand)
    if args.doctor:
        return diagnostico(args.docs)
    if not args.software:
        p.error("name the software (or use --doctor)")
    exigir_marca()

    raiz = common.docs_root(args.docs)
    pasta = achar_software(args.software, raiz)
    env = common.read_env(BRAND.env)

    print("Software: %s" % pasta)
    print("Brand   : %s (%s)" % (BRAND.root.name, BRAND.origin))
    print("Preparing the brand theme...")
    config_fontes = preparar_tema(pasta, env, args.fonts)
    cores = common.converter_colors(env, "BOOK")

    pecas = ["installation", "manual"] if args.piece == "all" else [args.piece]
    resultados = [publicar_peca(pasta, peca, args, env, config_fontes, cores)
                  for peca in pecas]
    escrever_leiame(pasta, resultados, env, args)

    print("\n== Result ==")
    faltando = []
    for r in resultados:
        if not r.get("fonte"):
            faltando.append(r["peca"])
            print("  %-22s not written yet — expected %s_AAAA-MM-DD.md"
                  % (r["rotulo"] + ":", common.PIECES[r["peca"]]["stem"]))
            continue
        print("  %-22s %s · %s · %d page(s)"
              % (r["rotulo"] + ":", r["fonte"].name,
                 r["tex"].name if r.get("tex") else "no .tex",
                 r.get("paginas") or 0))
    print("  Theme:                 %s" % (pasta / THEME_DIR))
    if faltando:
        print("\nMissing piece(s): %s. Write the Markdown, then publish again."
              % ", ".join(faltando))
    produziu = any(r.get("pdf") or r.get("tex") for r in resultados)
    return 0 if produziu else 1


if __name__ == "__main__":
    sys.exit(main())
