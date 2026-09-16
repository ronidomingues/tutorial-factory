"""Geração do preâmbulo LaTeX, da capa e do arquivo main.tex."""

from . import latexutil as lx

# Linguagens conhecidas -> rótulo bonito na etiqueta da caixa de código.
ROTULOS = {
    "bash": "bash", "sh": "sh", "shell": "shell", "zsh": "zsh",
    "console": "console", "powershell": "PowerShell", "bat": "cmd",
    "dockerfile": "Dockerfile", "yaml": "YAML", "yml": "YAML",
    "json": "JSON", "toml": "TOML", "ini": "INI", "xml": "XML",
    "javascript": "JavaScript", "js": "JavaScript", "typescript": "TypeScript",
    "python": "Python", "py": "Python", "go": "Go", "rust": "Rust",
    "c": "C", "cpp": "C++", "java": "Java", "sql": "SQL",
    "html": "HTML", "css": "CSS", "nginx": "nginx", "caddyfile": "Caddyfile",
    "make": "Makefile", "makefile": "Makefile", "diff": "diff",
    "texto": "", "text": "", "plain": "", "": "",
}


def _cor(hexa: str) -> str:
    return hexa.lstrip("#").upper()


def gerar_preambulo(cfg, linguagens) -> str:
    """Monta o preâmbulo completo, incluindo uma caixa por linguagem vista."""
    opcoes = [cfg.get("corpo", "11pt"), cfg.get("papel", "a4paper")]
    opcoes.append("twoside,openright" if cfg.get("duas_faces", True)
                  else "oneside,openany")

    L = []
    A = L.append

    A(r"%% Gerado por md2book — não edite à mão: as alterações se perdem.")
    A(r"\documentclass[%s]{book}" % ",".join(opcoes))
    A("")
    A(r"\usepackage{fontspec}")
    A(r"\usepackage{polyglossia}")
    A(r"\setmainlanguage{%s}" % cfg.get("idioma", "brazil"))
    A(r"\usepackage[%s]{geometry}" % cfg.get("geometria",
        "inner=3.0cm,outer=2.4cm,top=2.5cm,bottom=2.7cm,headsep=14pt"))
    A(r"\usepackage{xcolor}")
    A(r"\usepackage{fvextra}")
    A(r"\usepackage[breakable,skins]{tcolorbox}")
    A(r"\usepackage{longtable,booktabs,array,ragged2e}")
    A(r"\usepackage{enumitem}")
    A(r"\usepackage{titlesec}")
    A(r"\usepackage{fancyhdr}")
    A(r"\usepackage{etoolbox}")
    A(r"\usepackage{needspace}")
    A(r"\usepackage{microtype}")
    A(r"\usepackage[hidelinks]{hyperref}")
    A(r"\usepackage{bookmark}")
    A(r"\usepackage{xurl}")
    A("")

    A(bloco_fontes(cfg))

    A(r"%% -------------------------------------------------------- cores ---")
    A(r"\definecolor{mdaccent}{HTML}{%s}" % _cor(cfg.get("cor_destaque", "1F4E79")))
    A(r"\definecolor{mdcodebg}{HTML}{%s}" % _cor(cfg.get("cor_codigo_fundo", "F6F6F4")))
    A(r"\definecolor{mdcoderule}{HTML}{%s}" % _cor(cfg.get("cor_codigo_borda", "DCDCD5")))
    A(r"\definecolor{mdgray}{HTML}{5A5A5A}")
    A("")

    A(r"%% ------------------------------- quebra de linha e de página ---")
    A(r"%% Prosa técnica tem palavras longas e sem hifenização (comandos,")
    A(r"%% caminhos). Um pouco de tolerância evita linhas transbordando.")
    A(r"\tolerance=1200")
    A(r"\emergencystretch=2.2em")
    A(r"\hbadness=2500")
    A(r"\vbadness=2500")
    A(r"\widowpenalty=9000")
    A(r"\clubpenalty=9000")
    A(r"\setlength{\headheight}{15pt}")
    A(r"\setlength{\parindent}{0pt}")
    A(r"\setlength{\parskip}{5pt plus 2pt minus 1pt}")
    A("")

    A(r"%% ------------------------------------------------------ símbolos ---")
    A(r'\newcommand{\mdOK}{{\mdsym\color{green!55!black}\symbol{"2713}}}')
    A(r'\newcommand{\mdNO}{{\mdsym\color{red!72!black}\symbol{"2717}}}')
    A(r'\newcommand{\mdWarn}{{\mdsym\color{orange!85!black}\symbol{"26A0}}}')
    A(r'\newcommand{\mdPartial}{{\mdsym\color{yellow!65!orange}\symbol{"25CF}}}')
    A(r'\newcommand{\mdGreen}{{\mdsym\color{green!60!black}\symbol{"25CF}}}')
    A(r'\newcommand{\mdRed}{{\mdsym\color{red!75!black}\symbol{"25CF}}}')
    A(r'\newcommand{\mdTodo}{{\mdsym\color{black!45}\symbol{"25A1}}}')
    A(r'\newcommand{\mdStar}{{\mdsym\symbol{"2605}}}')
    A(r'\newcommand{\mdStarOpen}{{\mdsym\symbol{"2606}}}')
    A("")

    A(r"%% --------------------------------------------- texto e código ---")
    A(r"\newcommand{\mdbreak}{\allowbreak}")
    A(r"\newcommand{\mdcode}[1]{\texttt{#1}}")
    A(r"\newcommand{\mdstrike}[1]{%")
    A(r"  \leavevmode\hbox{\rlap{\raisebox{0.45ex}{\rule{\widthof{#1}}{0.5pt}}}#1}}")
    A(r"\usepackage{calc}")
    A(r"\newcommand{\mdrule}{\par\vspace{4pt}%")
    A(r"  {\color{black!25}\hrule height 0.4pt}\par\vspace{6pt}}")
    A(r"\newcommand{\mdornament}{\par\vspace{6pt}%")
    A(r"  \centerline{\color{mdaccent}\normalsize$\ast\ \ast\ \ast$}\par\vspace{8pt}}")
    A("")
    # Nos marcadores do PDF (sumário lateral) não existem macros nem cores:
    # aqui elas viram texto simples para não estourar o hyperref.
    A(r"\pdfstringdefDisableCommands{%")
    A(r"  \def\mdcode#1{#1}\def\mdbreak{}\def\mdstrike#1{#1}%")
    A(r"  \def\mdOK{[ok]}\def\mdNO{[x]}\def\mdWarn{[!]}\def\mdPartial{[~]}%")
    A(r"  \def\mdTodo{[ ]}\def\mdGreen{[ok]}\def\mdRed{[!]}%")
    A(r"  \def\mdStar{*}\def\mdStarOpen{*}\def\mdsym{}%")
    A(r"}")
    A("")

    A(r"%% --------------------------------------------------- citações ---")
    A(r"\newtcolorbox{mdquote}{breakable, enhanced, colback=white,")
    A(r"  colframe=mdaccent!70, boxrule=0pt, leftrule=2.4pt, arc=0pt,")
    A(r"  left=10pt, right=4pt, top=5pt, bottom=5pt,")
    A(r"  before skip=8pt, after skip=8pt}")
    A("")

    A(r"%% ---------------------------------------------------- tabelas ---")
    A(r"\setlength{\LTpre}{7pt}\setlength{\LTpost}{9pt}")
    A(r"\newenvironment{mdtable}[1]")
    A(r"  {\begingroup\footnotesize\renewcommand{\arraystretch}{1.22}%")
    A(r"   \setlength{\tabcolsep}{4pt}\setlength{\parskip}{0pt}%")
    A(r"   \emergencystretch=1.5em\hbadness=10000%")
    A(r"   \longtable{#1}}")
    A(r"  {\endlongtable\endgroup}")
    A("")

    A(r"%% ----------------------------------------------------- listas ---")
    A(r"\setlist[itemize]{leftmargin=1.3em, itemsep=2pt, topsep=4pt, parsep=2pt}")
    A(r"\setlist[enumerate]{leftmargin=1.6em, itemsep=2pt, topsep=4pt, parsep=2pt}")
    A(r"\setlist[itemize,1]{label=\textcolor{mdaccent}{\textbullet}}")
    A("")

    A(gerar_caixas_codigo(cfg, linguagens))
    A(gerar_titulos(cfg))
    A(gerar_cabecalhos(cfg))
    A(gerar_capa(cfg))
    # Por último: o tema vê tudo já definido e pode sobrescrever o que quiser.
    A(bloco_extras(cfg))
    return "\n".join(L)


def bloco_fontes(cfg) -> str:
    """Carrega as três famílias, do sistema ou de uma pasta de arquivos.

    Com `fontes.diretorio` preenchido, o fontspec lê os arquivos do disco:
    o PDF sai igual em qualquer máquina, mesmo sem a fonte instalada. Sem ele,
    vale o nome da família — o caminho curto de quem já tem a fonte no sistema.
    """
    f = cfg.get("fontes", {})
    escala_texto = f.get("escala_texto", 0.92)
    escala_mono = f.get("escala_mono", "MatchLowercase")
    escala_mono = ("Scale=MatchLowercase" if escala_mono == "MatchLowercase"
                   else "Scale=%s" % escala_mono)
    ligaduras = "Ligatures=TeX, " if cfg.get("ligaduras_tex") else ""
    diretorio = f.get("diretorio")
    extensao = f.get("extensao", ".ttf")

    def opcoes(faces, extras):
        itens = []
        if diretorio:
            caminho = str(diretorio).rstrip("/") + "/"
            itens.append("Path=%s" % caminho)
            itens.append("Extension=%s" % extensao)
            for chave, valor in (faces or {}).items():
                itens.append("%s=%s" % (chave, valor))
        itens.extend(x for x in extras if x)
        return "[%s]" % ", ".join(itens) if itens else ""

    lig = ligaduras.rstrip(", ") or None
    L = [r"%% ------------------------------------------------------- fontes ---"]
    if diretorio:
        L.append(r"%% Fontes lidas de %s — não precisam estar instaladas."
                 % diretorio)
    L.append(r"\setmainfont{%s}%s" % (
        f.get("texto", "DejaVu Serif"),
        opcoes(f.get("texto_faces"), [lig, "Scale=%s" % escala_texto])))
    L.append(r"\setsansfont{%s}%s" % (
        f.get("titulo", "DejaVu Sans"),
        opcoes(f.get("titulo_faces"), [lig, "Scale=%s" % escala_texto])))
    L.append(r"\setmonofont{%s}%s" % (
        f.get("mono", "DejaVu Sans Mono"),
        opcoes(f.get("mono_faces"), [escala_mono])))
    # A família de símbolos fica sempre no nome instalado: é a rede de
    # segurança para ✓, ✗ e ⚠, que a fonte do texto pode não desenhar.
    L.append(r"\newfontfamily\mdsym{%s}" % f.get("simbolos", "DejaVu Sans"))
    L.append("")
    return "\n".join(L)


def bloco_extras(cfg) -> str:
    """Pacotes e linhas de preâmbulo acrescentados por um tema."""
    L = []
    pacotes = cfg.get("pacotes_extra") or []
    if pacotes:
        L.append(r"%% ------------------------------------------ tema da marca ---")
        for pacote in pacotes:
            L.append(r"\usepackage{%s}" % pacote)
        L.append("")
    extra = cfg.get("preambulo_extra") or ""
    if isinstance(extra, (list, tuple)):
        extra = "\n".join(extra)
    if extra.strip():
        L.append(extra.rstrip())
        L.append("")
    return "\n".join(L)


def gerar_caixas_codigo(cfg, linguagens) -> str:
    """Um ambiente Verbatim + caixa colorida por linguagem encontrada."""
    tamanho = cfg.get("tamanho_codigo", 7.8)
    entrelinha = (cfg.get("entrelinha_codigo")
                  or round(float(tamanho) * 1.21, 1))
    sangria = cfg.get("sangria_codigo", "0.9cm")
    rotular = cfg.get("rotulo_linguagem", True)

    L = [r"%% ------------------------------------------------ código ---",
         r"\newcommand{\mdcodesize}{\fontsize{%spt}{%spt}\selectfont}"
         % (tamanho, entrelinha),
         r"\tcbset{mdcodebox/.style={",
         r"  breakable, enhanced, arc=1.6pt, boxrule=0.5pt,",
         r"  colback=mdcodebg, colframe=mdcoderule,",
         r"  left=5pt, right=4pt, top=4pt, bottom=4pt,",
         r"  grow to left by=%s, grow to right by=%s," % (sangria, sangria),
         r"  before skip=9pt, after skip=10pt,",
         r"}}", ""]

    vistas = sorted(set(linguagens)) or [("cbtexto", "texto")]
    for ambiente, lingua in vistas:
        rotulo = ROTULOS.get(lingua, lingua)
        L.append(r"\DefineVerbatimEnvironment{%s}{Verbatim}{%%" % ambiente)
        L.append(r"  breaklines=true, breakanywhere=true, fontsize=\mdcodesize,")
        L.append(r"  breaksymbolleft={\color{mdgray}\tiny\ensuremath{\hookrightarrow}},")
        L.append(r"  breaksymbolright={}, xleftmargin=0pt}")
        if rotular and rotulo:
            L.append(r"\tcolorboxenvironment{%s}{mdcodebox," % ambiente)
            L.append(r"  attach boxed title to top right={yshift=-1.6mm, xshift=-3mm},")
            L.append(r"  title={\scriptsize\sffamily %s}, coltitle=mdgray,"
                     % lx.escapar(rotulo))
            L.append(r"  boxed title style={colback=mdcoderule!45, colframe=mdcoderule,")
            L.append(r"    boxrule=0.3pt, arc=1pt, left=3pt, right=3pt, top=0.5pt, bottom=0.5pt}}")
        else:
            L.append(r"\tcolorboxenvironment{%s}{mdcodebox}" % ambiente)
        L.append("")
    return "\n".join(L)


def gerar_titulos(cfg) -> str:
    return "\n".join([
        r"%% ------------------------------------------- títulos de seção ---",
        r"\titleformat{\part}[display]",
        r"  {\normalfont\sffamily\bfseries\filcenter\color{mdaccent}}",
        r"  {\Large\MakeUppercase{\partname}\ \thepart}{18pt}{\Huge}",
        r"\titleformat{\chapter}[display]",
        r"  {\normalfont\sffamily\bfseries}",
        r"  {\normalsize\color{mdaccent}\MakeUppercase{\chaptertitlename}\ \thechapter}",
        r"  {6pt}{\LARGE\raggedright}",
        r"  [\vspace{5pt}{\color{mdaccent}\titlerule[1.1pt]}]",
        r"\titleformat{name=\chapter,numberless}[display]",
        r"  {\normalfont\sffamily\bfseries}{}{0pt}{\LARGE\raggedright}",
        r"  [\vspace{5pt}{\color{mdaccent}\titlerule[1.1pt]}]",
        r"\titlespacing*{\chapter}{0pt}{6pt}{22pt}",
        r"\titleformat{\section}",
        r"  {\normalfont\sffamily\Large\bfseries\color{mdaccent!88!black}}",
        r"  {\thesection}{0.7em}{}",
        r"\titleformat{\subsection}",
        r"  {\normalfont\sffamily\large\bfseries\color{black!85}}",
        r"  {\thesubsection}{0.6em}{}",
        r"\titleformat{\subsubsection}",
        r"  {\normalfont\sffamily\normalsize\bfseries\color{black!80}}",
        r"  {\thesubsubsection}{0.5em}{}",
        r"\titlespacing*{\section}{0pt}{16pt}{6pt}",
        r"\titlespacing*{\subsection}{0pt}{12pt}{4pt}",
        r"\titlespacing*{\subsubsection}{0pt}{10pt}{3pt}",
        r"\setcounter{tocdepth}{%d}" % cfg.get("profundidade_sumario", 1),
        r"\setcounter{secnumdepth}{%d}" % cfg.get("profundidade_numeracao", 2),
        "",
        r"%% Parte com subtítulo. O subtítulo entra dentro do próprio título:",
        r"%% texto colocado depois de \part cairia na página seguinte.",
        r"\newcommand{\mdpart}[2]{\ifblank{#2}{\part{#1}}{%",
        r"  \part[#1]{#1\\[10pt]%",
        r"    {\normalsize\normalfont\sffamily\color{black!58}#2}}}}",
        "",
    ])


def gerar_cabecalhos(cfg) -> str:
    return "\n".join([
        r"%% --------------------------------------- cabeçalhos e rodapés ---",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\fancyhead[LE]{\small\sffamily\color{mdgray}\nouppercase{\leftmark}}",
        r"\fancyhead[RO]{\small\sffamily\color{mdgray}\nouppercase{\rightmark}}",
        r"\fancyfoot[LE,RO]{\small\sffamily\color{mdgray}\thepage}",
        r"\renewcommand{\headrulewidth}{0.4pt}",
        r"\renewcommand{\footrulewidth}{0pt}",
        r"\fancypagestyle{plain}{\fancyhf{}%",
        r"  \fancyfoot[LE,RO]{\small\sffamily\color{mdgray}\thepage}%",
        r"  \renewcommand{\headrulewidth}{0pt}}",
        r"\renewcommand{\chaptermark}[1]{\markboth{#1}{#1}}",
        r"\renewcommand{\sectionmark}[1]{\markright{#1}}",
        "",
        r"%% O verso em branco antes de um capítulo não leva cabeçalho.",
        r"\makeatletter",
        r"\def\cleardoublepage{\clearpage\if@twoside",
        r"  \ifodd\c@page\else\hbox{}\thispagestyle{empty}\newpage\fi\fi}",
        r"%% Espaço para os números do sumário: '1.10' não cabe no padrão.",
        r"\renewcommand*\l@section{\@dottedtocline{1}{1.5em}{3.0em}}",
        r"\renewcommand*\l@subsection{\@dottedtocline{2}{4.6em}{3.7em}}",
        r"\makeatother",
        "",
        r"\hypersetup{",
        r"  bookmarksnumbered=true, bookmarksopen=true, bookmarksopenlevel=0,",
        r"  pdftitle={%s}," % lx.escapar(cfg.get("titulo", "")),
        r"  pdfauthor={%s}," % lx.escapar(cfg.get("autor", "")),
        r"  colorlinks=true, linkcolor=mdaccent!85!black,",
        r"  urlcolor=mdaccent!85!black, citecolor=mdaccent!85!black}",
        "",
    ])


def gerar_capa(cfg) -> str:
    """Define \\mdcapa: a página de rosto do livro."""
    from .inline import renderizar as inline
    titulo = inline(cfg.get("titulo", ""))
    subtitulo = inline(cfg.get("subtitulo", ""))
    autor = inline(cfg.get("autor", ""))
    ano = lx.escapar(str(cfg.get("ano", "")))
    nota = inline(cfg.get("nota_capa", ""))

    L = [r"%% ---------------------------------------------------- capa ---",
         r"\newcommand{\mdcapa}{%",
         r"\begin{titlepage}\sffamily\raggedright",
         r"  \vspace*{2.2cm}",
         r"  {\color{mdaccent}\rule{\linewidth}{2.4pt}}\par\vspace{18pt}",
         r"  {\fontsize{34}{40}\selectfont\bfseries %s\par}" % titulo]
    if subtitulo:
        L.append(r"  \vspace{14pt}{\Large\color{black!62} %s\par}" % subtitulo)
    L.append(r"  \vspace{16pt}{\color{mdaccent}\rule{\linewidth}{0.9pt}}\par")
    L.append(r"  \vfill")
    if nota:
        L.append(r"  {\small\color{black!58}\begin{minipage}{0.86\linewidth}"
                 r"\RaggedRight %s\end{minipage}\par}\vspace{22pt}" % nota)
    if autor:
        L.append(r"  {\large\bfseries %s\par}" % autor)
    if ano:
        L.append(r"  \vspace{4pt}{\color{black!55} %s\par}" % ano)
    L.append(r"  \vspace{1.2cm}")
    L.append(r"\end{titlepage}}")
    L.append("")
    return "\n".join(L)
