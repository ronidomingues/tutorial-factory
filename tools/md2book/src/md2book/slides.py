"""Slides de aula: um arquivo Markdown por aula -> Beamer -> PDF.

O livro e os slides nascem do mesmo repertório de conversão (`blocks`,
`inline`, `render`), mas não do mesmo texto: um livro se lê, um slide se
projeta. Por isso a fonte dos slides é um *deck* escrito à parte, em Markdown,
com uma gramática curta:

    ---                      <- metadados opcionais da aula (chave: valor)
    aula: Aula 03
    duracao: 45 min
    ---

    # Título da aula         <- capa da aula
    ## Parte da aula         <- tela de transição
    ### Título do slide      <- um slide
    - tópicos, tabelas, código, citações...

    ```notas
    Roteiro do professor: o que falar neste slide.
    ```

Regras de conversão que valem a pena saber:

* `---` dentro de um slide continua o mesmo slide na tela seguinte;
* cabeçalhos de nível 4+ viram destaque em negrito, não seção;
* todo frame é `fragile`: código verbatim funciona em qualquer slide;
* tabelas saem como `tabular` (longtable não atravessa um frame).
"""

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from . import blocks as B
from . import build, config as cfgmod, discovery, latexutil as lx, preamble
from .inline import ContextoLink, renderizar as inline
from .render import Renderizador

NOME_PADRAO = "slides.json"

CONFIG_PADRAO = {
    # ---------------------------------------------------------- identidade ---
    "curso": "Curso",
    "subtitulo": "",
    "autor": "",
    "data": "",

    # ------------------------------------------------------------ arquivos ---
    "raiz": ".",
    # Pasta com os decks (.md), relativa à raiz.
    "entrada": "md",
    # Pasta dos .tex gerados e da compilação, relativa à raiz.
    "saida": "latex",
    # Pasta para onde os PDFs prontos são copiados, relativa à raiz.
    "saida_pdf": "pdf",
    "ignorar": ["**/.git/**", "**/node_modules/**", "README.md"],
    # Nome do PDF que junta todas as aulas (vazio = não unir).
    "pdf_unico": "slides-completo.pdf",

    # --------------------------------------------------------------- forma ---
    "classe": "beamer",
    "proporcao": "169",
    "corpo": "10pt",
    # "t" alinha o conteúdo ao topo do slide. O padrão do Beamer é centralizar,
    # e centralizar faz cada slide começar em uma altura diferente — o olho de
    # quem assiste passa a caçar o começo do texto a cada tela.
    "alinhamento_vertical": "t",
    "idioma": "brazil",
    "tema": "andradasdev",
    "opcoes_tema": "",
    "fontes": {
        "texto": "DejaVu Sans",
        "titulo": "DejaVu Sans",
        "mono": "DejaVu Sans Mono",
        "simbolos": "DejaVu Sans",
        "escala_texto": 1.0,
        "escala_mono": 0.86,
        "diretorio": None,
        "extensao": ".ttf",
        "texto_faces": {},
        "titulo_faces": {},
        "mono_faces": {},
    },
    "ligaduras_tex": False,
    # Paleta do bloco de código nos slides (fundo escuro por padrão).
    "cor_destaque": "A3FF12",
    "cor_codigo_fundo": "16161A",
    "cor_codigo_borda": "2A2A32",
    "cor_codigo_texto": "E8E8ED",
    "cor_texto_apoio": "8A8A99",
    "tamanho_codigo": 7.2,
    "entrelinha_codigo": None,
    "rotulo_linguagem": False,
    "tabela_simples": True,
    # Beamer e enumitem brigam pelo \labelenumi: no slide, lista é lista pura.
    "opcoes_lista": False,
    "remover_numeracao_titulos": True,
    "regua_horizontal": "ignorar",

    # ---------------------------------------------------------- comandos ----
    "capa_comando": "\\adcapaslide",
    "secao_comando": "\\adsecao",
    "fechamento_comando": "\\adfechamentoslide",
    "fechamento_texto": "",

    # ------------------------------------------------------------- tema ----
    "recursos": [],
    "texinputs": [],
    "pacotes_extra": [],
    "preambulo_extra": "",
    # Linhas emitidas logo depois de \\begin{document} (metadados da marca).
    "abertura_extra": "",

    # ------------------------------------------------------------ notas ----
    # nenhuma | frame | segunda-tela
    "notas": "nenhuma",

    # -------------------------------------------------------- qualidade ----
    # Aviso (não erro) quando um slide passa deste tamanho: slide didático que
    # não cabe na tela vira documento projetado, e ninguém lê documento de pé.
    "limite_linhas_slide": 12,
    "limite_caracteres_slide": 900,

    # --------------------------------------------------------- compilar ----
    "motor": "xelatex",
    "passagens": 2,
}


# ============================================================ configuração ===

def carregar_config(caminho=None, raiz=None):
    """Lê o slides.json sobre os padrões acima (mesma mecânica do livro)."""
    import copy
    import json

    if caminho:
        caminho = Path(caminho).resolve()
        if not caminho.is_file():
            raise FileNotFoundError("configuração não encontrada: %s" % caminho)
    else:
        candidato = Path(raiz or ".").resolve() / NOME_PADRAO
        caminho = candidato if candidato.is_file() else None

    dados = copy.deepcopy(CONFIG_PADRAO)
    if caminho:
        with open(caminho, encoding="utf-8") as fh:
            dados = cfgmod._mesclar(dados, json.load(fh))
    if raiz:
        dados["raiz"] = str(Path(raiz).resolve())
        caminho = None
    cfg = cfgmod.Config(dados, caminho)
    return cfg


def _dir(cfg, chave, padrao) -> Path:
    return (cfg.raiz / cfg.get(chave, padrao)).resolve()


# ================================================================= leitura ===

@dataclass
class Slide:
    titulo: str
    nos: List[B.No] = field(default_factory=list)
    notas: List[str] = field(default_factory=list)
    continuacao: bool = False


@dataclass
class Secao:
    titulo: str
    subtitulo: str = ""


@dataclass
class Aula:
    caminho: Path
    nome: str                       # nome do arquivo sem extensão
    titulo: str
    subtitulo: str = ""
    meta: dict = field(default_factory=dict)
    elementos: list = field(default_factory=list)   # Secao | Slide

    @property
    def slides(self):
        return [e for e in self.elementos if isinstance(e, Slide)]


_FRONT_RE = re.compile(r"^---\s*$")
_META_RE = re.compile(r"^([A-Za-zÀ-ÿ_][\w\- ]*):\s*(.*)$")
_CERCA_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_NOTAS_ABRE_RE = re.compile(r"^\s{0,3}:::\s*notas?\s*$", re.I)
_NOTAS_FECHA_RE = re.compile(r"^\s{0,3}:::\s*$")


def _ler_front_matter(texto: str):
    """Separa os metadados `chave: valor` do topo, quando existem."""
    linhas = texto.splitlines()
    if not linhas or not _FRONT_RE.match(linhas[0]):
        return {}, texto
    meta = {}
    for i in range(1, len(linhas)):
        if _FRONT_RE.match(linhas[i]):
            return meta, "\n".join(linhas[i + 1:])
        m = _META_RE.match(linhas[i])
        if m:
            meta[m.group(1).strip().lower()] = m.group(2).strip().strip('"')
    return {}, texto                      # abertura sem fechamento: era régua


def _normalizar_notas(texto: str) -> str:
    """`:::notas ... :::` vira uma cerca de código da linguagem `notas`.

    Assim o analisador de blocos, que já sabe ler cerca, entrega a nota como
    um nó só — sem um segundo analisador para manter.
    """
    saida, dentro_cerca, dentro_nota = [], False, False
    for linha in texto.splitlines():
        if _CERCA_RE.match(linha) and not dentro_nota:
            dentro_cerca = not dentro_cerca
            saida.append(linha)
            continue
        if not dentro_cerca:
            if not dentro_nota and _NOTAS_ABRE_RE.match(linha):
                dentro_nota = True
                saida.append("```notas")
                continue
            if dentro_nota and _NOTAS_FECHA_RE.match(linha):
                dentro_nota = False
                saida.append("```")
                continue
        saida.append(linha)
    if dentro_nota:
        saida.append("```")
    return "\n".join(saida)


def ler_aula(caminho: Path) -> Aula:
    """Lê um deck e devolve a aula já dividida em seções e slides."""
    bruto = caminho.read_text(encoding="utf-8")
    meta, corpo = _ler_front_matter(bruto)
    nos = B.analisar(_normalizar_notas(corpo))

    aula = Aula(caminho=caminho, nome=caminho.stem, titulo="", meta=meta)
    aula.titulo = meta.get("titulo", "")
    aula.subtitulo = meta.get("subtitulo", "")
    atual = None
    pendente_secao = None

    def fechar():
        nonlocal atual
        if atual is not None and (atual.nos or atual.titulo):
            aula.elementos.append(atual)
        atual = None

    for no in nos:
        if isinstance(no, B.Cabecalho) and no.nivel == 1:
            fechar()
            pendente_secao = None
            if not aula.titulo:
                aula.titulo = no.texto
            continue

        if isinstance(no, B.Cabecalho) and no.nivel == 2:
            fechar()
            pendente_secao = Secao(titulo=no.texto)
            aula.elementos.append(pendente_secao)
            continue

        if isinstance(no, B.Cabecalho) and no.nivel == 3:
            fechar()
            pendente_secao = None
            atual = Slide(titulo=no.texto)
            continue

        # Um parágrafo solto logo depois de "##" é a linha de apoio da seção.
        if (pendente_secao is not None and isinstance(no, B.Paragrafo)
                and not pendente_secao.subtitulo):
            pendente_secao.subtitulo = no.texto
            continue
        pendente_secao = None

        if atual is None:                 # conteúdo antes do primeiro "###"
            atual = Slide(titulo="")
        if isinstance(no, B.Codigo) and (no.linguagem or "").lower() in (
                "notas", "nota", "roteiro"):
            atual.notas.append(no.codigo)
            continue
        if isinstance(no, B.Regua):       # continua o slide na tela seguinte
            titulo = atual.titulo
            fechar()
            atual = Slide(titulo=titulo, continuacao=True)
            continue
        if isinstance(no, B.Cabecalho) and no.nivel >= 4:
            atual.nos.append(B.Paragrafo(texto="**%s**" % no.texto))
            continue
        atual.nos.append(no)

    fechar()
    if not aula.titulo:
        aula.titulo = discovery.encurtar_titulo(caminho.stem.replace("-", " "))
    return aula


def coletar_aulas(cfg) -> List[Aula]:
    """Todos os decks da pasta de entrada, em ordem natural de nome."""
    entrada = _dir(cfg, "entrada", "md")
    if not entrada.is_dir():
        return []
    ignorar = cfg.get("ignorar") or []
    arquivos = []
    for caminho in entrada.rglob("*.md"):
        relativo = caminho.relative_to(entrada).as_posix()
        if discovery._combina(relativo, ignorar):
            continue
        arquivos.append(caminho)
    arquivos.sort(key=lambda c: discovery.chave_natural(c.name))
    return [ler_aula(c) for c in arquivos]


# =============================================================== preâmbulo ===

def _cor(hexa: str) -> str:
    return str(hexa).lstrip("#").upper()


def gerar_preambulo(cfg, linguagens) -> str:
    """Preâmbulo do Beamer: classe, fontes, tema e caixas de código."""
    opcoes = ["aspectratio=%s" % cfg.get("proporcao", "169"),
              cfg.get("corpo", "10pt")]
    if cfg.get("alinhamento_vertical"):
        opcoes.append(cfg.get("alinhamento_vertical"))
    if cfg.get("notas") == "segunda-tela":
        opcoes.append("notes=show")
    elif cfg.get("notas") == "frame":
        opcoes.append("notes=show")

    L = []
    A = L.append
    A(r"%% Gerado por md2book slides — não edite à mão: as alterações se perdem.")
    A(r"\documentclass[%s]{%s}" % (",".join(opcoes), cfg.get("classe", "beamer")))
    A("")
    A(r"\usepackage{fontspec}")
    A(r"\usepackage{polyglossia}")
    A(r"\setmainlanguage{%s}" % cfg.get("idioma", "brazil"))
    A(r"\usepackage{xcolor}")
    A(r"\usepackage{fvextra}")
    A(r"\usepackage[breakable,skins]{tcolorbox}")
    A(r"\usepackage{booktabs,array,ragged2e}")
    A(r"\usepackage[export]{adjustbox}")
    A(r"\usepackage{etoolbox}")
    A(r"\usepackage{calc}")
    A("")
    A(preamble.bloco_fontes(cfg))
    A(r"%% --------------------------------------------------------- cores ---")
    A(r"\definecolor{mdaccent}{HTML}{%s}" % _cor(cfg.get("cor_destaque", "A3FF12")))
    A(r"\definecolor{mdcodebg}{HTML}{%s}" % _cor(cfg.get("cor_codigo_fundo", "16161A")))
    A(r"\definecolor{mdcoderule}{HTML}{%s}" % _cor(cfg.get("cor_codigo_borda", "2A2A32")))
    A(r"\definecolor{mdcodefg}{HTML}{%s}" % _cor(cfg.get("cor_codigo_texto", "E8E8ED")))
    A(r"\definecolor{mdgray}{HTML}{%s}" % _cor(cfg.get("cor_texto_apoio", "8A8A99")))
    A("")
    A(r"%% ------------------------------------------------------ símbolos ---")
    A(r'\newcommand{\mdOK}{{\mdsym\color{green!55!white}\symbol{"2713}}}')
    A(r'\newcommand{\mdNO}{{\mdsym\color{red!62!white}\symbol{"2717}}}')
    A(r'\newcommand{\mdWarn}{{\mdsym\color{orange!75!white}\symbol{"26A0}}}')
    A(r'\newcommand{\mdPartial}{{\mdsym\color{yellow!70!orange}\symbol{"25CF}}}')
    A(r'\newcommand{\mdGreen}{{\mdsym\color{green!60!white}\symbol{"25CF}}}')
    A(r'\newcommand{\mdRed}{{\mdsym\color{red!65!white}\symbol{"25CF}}}')
    A(r'\newcommand{\mdTodo}{{\mdsym\color{mdgray}\symbol{"25A1}}}')
    A(r'\newcommand{\mdStar}{{\mdsym\symbol{"2605}}}')
    A(r'\newcommand{\mdStarOpen}{{\mdsym\symbol{"2606}}}')
    A(r"\newcommand{\mdbreak}{\allowbreak}")
    A(r"\newcommand{\mdcode}[1]{{\ttfamily\color{mdaccent}#1}}")
    A(r"\newcommand{\mdstrike}[1]{%")
    A(r"  \leavevmode\hbox{\rlap{\raisebox{0.45ex}{\rule{\widthof{#1}}{0.5pt}}}#1}}")
    A(r"\newcommand{\mdrule}{\par\vspace{2pt}{\color{mdgray}\hrule height 0.4pt}"
      r"\par\vspace{3pt}}")
    A(r"\newcommand{\mdornament}{\par\vspace{3pt}\centerline{\color{mdaccent}"
      r"$\ast\ \ast\ \ast$}\par\vspace{3pt}}")
    A(r"\pdfstringdefDisableCommands{%")
    A(r"  \def\mdcode#1{#1}\def\mdbreak{}\def\mdstrike#1{#1}%")
    A(r"  \def\mdOK{[ok]}\def\mdNO{[x]}\def\mdWarn{[!]}\def\mdPartial{[~]}%")
    A(r"  \def\mdTodo{[ ]}\def\mdGreen{[ok]}\def\mdRed{[!]}%")
    A(r"  \def\mdStar{*}\def\mdStarOpen{*}\def\mdsym{}%")
    A(r"}")
    A("")
    A(r"%% ------------------------------------------------------ citações ---")
    A(r"\newtcolorbox{mdquote}{breakable, enhanced, colback=mdcodebg,")
    A(r"  colframe=mdaccent, boxrule=0pt, leftrule=2.4pt, arc=0pt,")
    A(r"  left=6pt, right=4pt, top=4pt, bottom=4pt,")
    A(r"  before skip=5pt, after skip=5pt}")
    A("")
    A(r"%% ------------------------------------------------------- tabelas ---")
    A(r"\newenvironment{mdtable}[1]")
    A(r"  {\begingroup\scriptsize\renewcommand{\arraystretch}{1.25}%")
    A(r"   \setlength{\tabcolsep}{4pt}\begin{tabular}{#1}}")
    A(r"  {\end{tabular}\endgroup}")
    A("")
    A(r"%% -------------------------------------------------------- listas ---")
    A(r"%% Sem enumitem: em Beamer, redefinir a lista faz \labelenumi chamar")
    A(r"%% a si mesmo e a compilação estoura a pilha no primeiro enumerate.")
    A(r"%% O conversor sabe disso (opcoes_lista=false) e emite lista pura.")
    A(r"\setbeamertemplate{itemize/enumerate body begin}{\vspace{1mm}}")
    A("")
    A(_caixas_codigo(cfg, linguagens))
    A(r"%% ---------------------------------------------------------- tema ---")
    opcoes_tema = cfg.get("opcoes_tema") or ""
    A(r"\usetheme%s{%s}" % ("[%s]" % opcoes_tema if opcoes_tema else "",
                            cfg.get("tema", "andradasdev")))
    A(preamble.bloco_extras(cfg))
    return "\n".join(L)


def _caixas_codigo(cfg, linguagens) -> str:
    """Caixa de código escura, uma por linguagem vista nos decks."""
    tamanho = cfg.get("tamanho_codigo", 7.2)
    entrelinha = cfg.get("entrelinha_codigo") or round(float(tamanho) * 1.22, 1)
    rotular = cfg.get("rotulo_linguagem", False)

    L = [r"%% --------------------------------------------------------- código ---",
         r"\newcommand{\mdcodesize}{\fontsize{%spt}{%spt}\selectfont}"
         % (tamanho, entrelinha),
         r"\tcbset{mdcodebox/.style={",
         r"  breakable, enhanced, arc=1.6pt, boxrule=0.6pt,",
         r"  colback=mdcodebg, colframe=mdcoderule,",
         r"  left=5pt, right=4pt, top=3pt, bottom=3pt,",
         r"  before skip=5pt, after skip=6pt}}", ""]

    vistas = sorted(set(linguagens)) or [("cbtexto", "texto")]
    for ambiente, lingua in vistas:
        rotulo = preamble.ROTULOS.get(lingua, lingua)
        L.append(r"\DefineVerbatimEnvironment{%s}{Verbatim}{%%" % ambiente)
        L.append(r"  breaklines=true, breakanywhere=true, fontsize=\mdcodesize,")
        L.append(r"  formatcom=\color{mdcodefg},")
        L.append(r"  breaksymbolleft={\color{mdgray}\tiny\ensuremath{\hookrightarrow}},")
        L.append(r"  breaksymbolright={}, xleftmargin=0pt}")
        if rotular and rotulo:
            L.append(r"\tcolorboxenvironment{%s}{mdcodebox," % ambiente)
            L.append(r"  attach boxed title to top right={yshift=-1.6mm, xshift=-3mm},")
            L.append(r"  title={\scriptsize\ttfamily %s}, coltitle=mdgray,"
                     % lx.escapar(rotulo))
            L.append(r"  boxed title style={colback=mdcodebg, colframe=mdcoderule,")
            L.append(r"    boxrule=0.3pt, arc=1pt, left=3pt, right=3pt,"
                     r" top=0.5pt, bottom=0.5pt}}")
        else:
            L.append(r"\tcolorboxenvironment{%s}{mdcodebox}" % ambiente)
        L.append("")
    return "\n".join(L)


# ============================================================== renderização ===

class Resultado:
    def __init__(self):
        self.aulas = []            # (Aula, Path tex, Path pdf|None)
        self.slides = 0
        self.avisos = []
        self.pdf_unico = None


def renderizar(cfg, verboso=True) -> Resultado:
    """Converte cada deck em um .tex de Beamer. Não compila."""
    res = Resultado()
    aulas = coletar_aulas(cfg)
    if not aulas:
        return res

    saida = _dir(cfg, "saida", "latex")
    saida.mkdir(parents=True, exist_ok=True)
    build.copiar_recursos(_como_projeto(cfg, saida))

    for aula in aulas:
        linguagens = set()
        corpo = _corpo_da_aula(cfg, aula, linguagens)
        texto = "\n".join([gerar_preambulo(cfg, linguagens), "",
                           _metadados(cfg, aula), "",
                           r"\begin{document}", "",
                           corpo,
                           r"\end{document}", ""])
        destino = saida / ("%s.tex" % aula.nome)
        destino.write_text(texto, encoding="utf-8")
        res.aulas.append([aula, destino, None])
        res.slides += len(aula.slides)
        res.avisos.extend(_conferir(cfg, aula))
        if verboso:
            print("  %-42s -> %s (%d slides)"
                  % (aula.caminho.name, destino.name, len(aula.slides)))
    return res


def _como_projeto(cfg, saida: Path):
    """Config espelhada com `saida` absoluta, para reusar build.copiar_recursos."""
    clone = cfgmod.Config(dict(cfg.dados), cfg.caminho)
    clone.raiz = cfg.raiz
    clone.dados["saida"] = str(saida)
    return clone


def _metadados(cfg, aula: Aula) -> str:
    """Título, autor e os campos de marca lidos pelo tema."""
    meta = aula.meta
    curso = meta.get("curso") or cfg.get("curso", "")
    L = [r"\title{%s}" % inline(aula.titulo),
         r"\subtitle{%s}" % inline(aula.subtitulo or meta.get("subtitulo", "")),
         r"\author{%s}" % inline(meta.get("autor") or cfg.get("autor", "")),
         r"\date{%s}" % lx.escapar(meta.get("data") or cfg.get("data", ""))]
    L.append(r"\providecommand{\adcurso}[1]{}")
    L.append(r"\providecommand{\adaula}[1]{}")
    L.append(r"\adcurso{%s}" % inline(curso))
    rotulo_aula = meta.get("aula", "")
    if rotulo_aula:
        L.append(r"\adaula{%s}" % inline(rotulo_aula))
    abertura = cfg.get("abertura_extra") or ""
    if isinstance(abertura, (list, tuple)):
        abertura = "\n".join(abertura)
    if abertura.strip():
        L.append(abertura.rstrip())
    return "\n".join(L)


def _corpo_da_aula(cfg, aula: Aula, linguagens: set) -> str:
    ctx = ContextoLink({}, aula.caminho.name, False)
    ctx.raiz_imagens = str(aula.caminho.parent)
    r = Renderizador(cfg, ctx)
    L = []
    capa = cfg.get("capa_comando", r"\adcapaslide")
    if capa:
        L += [r"\providecommand{\adcapaslide}{\begin{frame}[plain]\titlepage"
              r"\end{frame}}", capa, ""]

    comando_secao = cfg.get("secao_comando", r"\adsecao")
    for elemento in aula.elementos:
        if isinstance(elemento, Secao):
            L.append(r"\section{%s}" % inline(elemento.titulo, ctx))
            if comando_secao:
                L.append("%s[%s]{%s}" % (comando_secao,
                                         inline(elemento.subtitulo, ctx),
                                         inline(elemento.titulo, ctx)))
            L.append("")
            continue
        L.append(_frame(cfg, elemento, r, ctx))
        L.append("")

    fechamento = cfg.get("fechamento_comando", "")
    if fechamento:
        L.append("%s[%s]" % (fechamento,
                             inline(cfg.get("fechamento_texto", ""), ctx)))
        L.append("")
    linguagens.update(r.linguagens)
    return "\n".join(L)


def _frame(cfg, slide: Slide, r: Renderizador, ctx) -> str:
    titulo = slide.titulo
    if cfg.get("remover_numeracao_titulos", True) and titulo:
        titulo = lx.remover_numeracao(titulo)
    rotulo = inline(titulo, ctx) if titulo else ""
    if slide.continuacao and rotulo:
        rotulo += r"\;{\color{mdgray}\small(cont.)}"

    L = [r"\begin{frame}[fragile]{%s}" % rotulo]
    corpo = r.blocos(slide.nos).strip()
    if corpo:
        L.append(corpo)
    for nota in slide.notas:
        L.append(r"\note{%s}" % _nota(nota, r))
    L.append(r"\end{frame}")
    return "\n".join(L)


def _nota(texto: str, r: Renderizador) -> str:
    """Roteiro do professor: Markdown simples dentro de \\note."""
    return r.blocos(B.analisar(texto)).strip()


def _conferir(cfg, aula: Aula) -> List[str]:
    """Avisa sobre slide grande demais — é aviso, não erro: quem decide é quem ensina."""
    limite_linhas = int(cfg.get("limite_linhas_slide", 12))
    limite_chars = int(cfg.get("limite_caracteres_slide", 900))
    avisos = []
    for slide in aula.slides:
        linhas, caracteres = 0, 0
        for no in slide.nos:
            if isinstance(no, B.Lista):
                linhas += len(no.itens)
            elif isinstance(no, B.Codigo):
                linhas += no.codigo.count("\n") + 1
            elif isinstance(no, B.Tabela):
                linhas += len(no.linhas) + 1
            else:
                linhas += 2
            caracteres += len(getattr(no, "texto", "") or
                              getattr(no, "codigo", "") or "")
        if linhas > limite_linhas or caracteres > limite_chars:
            avisos.append("%s: o slide \"%s\" tem ~%d linhas — divida em dois."
                          % (aula.caminho.name, slide.titulo or "(sem título)",
                             linhas))
    return avisos


# ================================================================= compilar ===

def compilar(cfg, res: Resultado, verboso=True) -> bool:
    """Compila cada aula e copia os PDFs para a pasta de PDFs."""
    motor = cfg.get("motor", "xelatex")
    saida = _dir(cfg, "saida", "latex")
    destino_pdf = _dir(cfg, "saida_pdf", "pdf")
    destino_pdf.mkdir(parents=True, exist_ok=True)
    env = build.ambiente_de_compilacao(cfg)
    ok_geral = True

    for item in res.aulas:
        aula, tex, _ = item
        if verboso:
            print("  compilando %s..." % tex.name)
        if shutil.which("latexmk"):
            comandos = [["latexmk", "-%s" % motor, "-interaction=nonstopmode",
                         "-halt-on-error", "-file-line-error", tex.name]]
        elif shutil.which(motor):
            comandos = [[motor, "-interaction=nonstopmode", "-halt-on-error",
                         "-file-line-error", tex.name]] * int(
                             cfg.get("passagens", 2))
        else:
            print("ERRO: nem latexmk nem %s no PATH." % motor, file=sys.stderr)
            return False

        if not build._rodar(comandos, saida, verboso=False, env=env):
            print("Falha ao compilar %s (log em %s)"
                  % (tex.name, saida / (tex.stem + ".log")), file=sys.stderr)
            ok_geral = False
            continue

        gerado = saida / (tex.stem + ".pdf")
        if gerado.is_file():
            final = destino_pdf / gerado.name
            shutil.copyfile(gerado, final)
            item[2] = final

    prontos = [item[2] for item in res.aulas if item[2]]
    nome_unico = cfg.get("pdf_unico")
    if nome_unico and len(prontos) > 1:
        res.pdf_unico = unir_pdfs(prontos, destino_pdf / nome_unico, verboso)
    return ok_geral


def unir_pdfs(pdfs, destino: Path, verboso=True):
    """Junta os PDFs das aulas num só. Sem ferramenta disponível, avisa e segue."""
    entradas = [str(p) for p in pdfs]
    if shutil.which("pdfunite"):
        cmd = ["pdfunite"] + entradas + [str(destino)]
    elif shutil.which("gs"):
        cmd = ["gs", "-dBATCH", "-dNOPAUSE", "-q", "-sDEVICE=pdfwrite",
               "-sOutputFile=%s" % destino] + entradas
    else:
        print("AVISO: pdfunite (poppler-utils) ou ghostscript não encontrados: "
              "os PDFs das aulas ficam separados.", file=sys.stderr)
        return None
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("AVISO: falha ao unir os PDFs: %s" % proc.stderr.strip(),
              file=sys.stderr)
        return None
    if verboso:
        print("  PDF único: %s" % destino)
    return destino


def limpar_intermediarios(cfg) -> None:
    """Remove .aux, .log e afins da pasta de LaTeX, preservando os .tex."""
    saida = _dir(cfg, "saida", "latex")
    for extensao in ("*.aux", "*.log", "*.nav", "*.out", "*.snm", "*.toc",
                     "*.fls", "*.fdb_latexmk", "*.vrb", "*.xdv"):
        for lixo in saida.glob(extensao):
            lixo.unlink()
