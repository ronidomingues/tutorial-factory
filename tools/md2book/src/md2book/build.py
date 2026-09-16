"""Orquestração: renderiza os capítulos, monta o main.tex e compila o PDF."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import discovery, latexutil as lx, preamble
from .inline import ContextoLink
from .render import Renderizador

# Extensão -> linguagem, para o anexo de código-fonte.
LINGUAGEM_POR_EXTENSAO = {
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".py": "python", ".go": "go", ".rs": "rust",
    ".java": "java", ".c": "c", ".h": "c", ".cpp": "cpp", ".sh": "bash",
    ".bash": "bash", ".zsh": "bash", ".ps1": "powershell", ".sql": "sql",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".ini": "ini", ".cfg": "ini", ".conf": "nginx", ".xml": "xml",
    ".html": "html", ".css": "css", ".env": "ini", ".example": "ini",
}
NOME_PARA_LINGUAGEM = {
    "dockerfile": "dockerfile", "containerfile": "dockerfile",
    "makefile": "make", "compose.yaml": "yaml", "compose.yml": "yaml",
    "docker-compose.yaml": "yaml", "docker-compose.yml": "yaml",
    ".dockerignore": "texto", ".gitignore": "texto", ".env.example": "ini",
}


class Resultado:
    """O que o build produziu, para o relatório final."""

    def __init__(self):
        self.capitulos = 0
        self.fontes = 0
        self.linguagens = set()
        self.main = None
        self.pdf = None
        self.avisos = []


# ------------------------------------------------------------ renderizar ----

def renderizar(cfg, verboso=True) -> Resultado:
    """Converte todos os .md em .tex e escreve o main.tex. Não compila."""
    res = Resultado()
    estrutura = discovery.montar_estrutura(cfg)
    mapa = discovery.mapa_de_links(estrutura)
    ctx = ContextoLink(mapa, "", cfg.get("referencia_capitulo", True))
    r = Renderizador(cfg, ctx)

    dir_tex = cfg.dir_tex
    if dir_tex.exists():
        for antigo in dir_tex.glob("*.tex"):
            antigo.unlink()
    dir_tex.mkdir(parents=True, exist_ok=True)

    for doc in estrutura.documentos():
        corpo = r.documento(doc)
        destino = dir_tex / (doc.rotulo.replace(":", "-") + ".tex")
        destino.write_text(_cabecalho_arquivo(doc.relativo) + corpo,
                           encoding="utf-8")
        doc.arquivo_tex = destino.name
        res.capitulos += 1
        if verboso:
            print("  %-42s -> tex/%s" % (doc.relativo, destino.name))

    anexo = None
    if estrutura.fontes:
        anexo, res.fontes = _renderizar_anexo(cfg, estrutura, r)
        if verboso:
            print("  anexo de código-fonte: %d arquivos" % res.fontes)

    res.linguagens = set(r.linguagens)
    copiados = copiar_recursos(cfg)
    if copiados and verboso:
        for nome in copiados:
            print("  recurso do tema -> %s" % nome)
    conteudo = _montar_main(cfg, estrutura, r.linguagens, anexo)
    res.main = cfg.dir_saida / "main.tex"
    res.main.parent.mkdir(parents=True, exist_ok=True)
    res.main.write_text(conteudo, encoding="utf-8")
    return res


def copiar_recursos(cfg):
    r"""Copia os arquivos do tema (.sty, logos, ambiente) para a pasta de saída.

    O LaTeX resolve `\usepackage` no diretório de compilação, e o PDF precisa
    continuar sendo reconstruível meses depois: por isso o tema é copiado para
    dentro do projeto em vez de ser alcançado por um caminho absoluto.
    """
    recursos = cfg.get("recursos") or []
    if not recursos:
        return []
    destino_base = cfg.dir_saida
    destino_base.mkdir(parents=True, exist_ok=True)
    copiados = []
    for item in recursos:
        if isinstance(item, dict):
            origem, destino = item.get("de"), item.get("para")
        else:
            origem, destino = item, None
        caminho = Path(origem)
        if not caminho.is_absolute():
            caminho = cfg.raiz / caminho
        if not caminho.exists():
            print("AVISO: recurso do tema não encontrado: %s" % caminho,
                  file=sys.stderr)
            continue
        alvo = destino_base / (destino or caminho.name)
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if caminho.is_dir():
            shutil.copytree(caminho, alvo, dirs_exist_ok=True)
        else:
            shutil.copyfile(caminho, alvo)
        copiados.append(str(alvo.relative_to(destino_base)))
    return copiados


def _cabecalho_arquivo(relativo: str) -> str:
    return ("%% Gerado por md2book a partir de %s\n"
            "%% Edite o Markdown de origem, não este arquivo.\n\n" % relativo)


def _renderizar_anexo(cfg, estrutura, r: Renderizador):
    """Um capítulo de apêndice com o código-fonte integral do projeto."""
    ap = cfg.get("apendice_fontes", {})
    from .inline import renderizar as inline

    L = [r"\chapter{%s}" % inline(ap.get("titulo", "Código-fonte")),
         r"\label{ap:fontes}", ""]
    if ap.get("introducao"):
        L += [inline(ap["introducao"], r.ctx), ""]

    total = 0
    for caminho in estrutura.fontes:
        rel = caminho.relative_to(cfg.raiz).as_posix()
        lingua = _linguagem(caminho)
        ambiente = "cb" + lx.nome_ambiente(lingua)
        r.linguagens.add((ambiente, lingua))
        corpo = lx.escapar_verbatim(caminho.read_text(encoding="utf-8",
                                                      errors="replace"))
        corpo = corpo.replace("\\end{%s}" % ambiente, "\\end {%s}" % ambiente)
        L += [r"\section{%s}" % lx.codigo_embutido(rel),
              r"\begin{%s}" % ambiente, corpo.rstrip("\n"),
              r"\end{%s}" % ambiente, ""]
        total += 1

    destino = cfg.dir_tex / "anexo-fontes.tex"
    destino.write_text(_cabecalho_arquivo("arquivos do projeto") +
                       "\n".join(L), encoding="utf-8")
    return destino.name, total


def _linguagem(caminho: Path) -> str:
    nome = caminho.name.lower()
    if nome in NOME_PARA_LINGUAGEM:
        return NOME_PARA_LINGUAGEM[nome]
    return LINGUAGEM_POR_EXTENSAO.get(caminho.suffix.lower(), "texto")


def _montar_main(cfg, estrutura, linguagens, anexo) -> str:
    from .inline import renderizar as inline
    capa = cfg.get("capa_comando", r"\mdcapa") or ""
    L = [preamble.gerar_preambulo(cfg, linguagens), "",
         r"\begin{document}", "",
         r"\frontmatter"]
    if capa:
        L.append(capa)
    L += [r"\tableofcontents", ""]

    if estrutura.abertura:
        # No miolo pré-textual as seções não levam número: um "0.3" antes do
        # capítulo 1 confunde mais do que orienta.
        L.append(r"\setcounter{secnumdepth}{-1}")
        for doc in estrutura.abertura:
            L.append(r"\input{tex/%s}" % doc.arquivo_tex[:-4])
        L += [r"\setcounter{secnumdepth}{%d}"
              % cfg.get("profundidade_numeracao", 2), ""]

    L += [r"\mainmatter", ""]
    for parte in estrutura.partes:
        if parte.titulo:
            L.append(r"\mdpart{%s}{%s}" % (inline(parte.titulo),
                                           inline(parte.subtitulo)))
        for doc in parte.documentos:
            L.append(r"\input{tex/%s}" % doc.arquivo_tex[:-4])
        L.append("")

    if anexo:
        L += [r"\appendix", r"\input{tex/%s}" % anexo[:-4], ""]

    for comando in cfg.get("encerramento") or []:
        L.append(comando)
    if cfg.get("encerramento"):
        L.append("")

    L += [r"\end{document}", ""]
    return "\n".join(L)


# --------------------------------------------------------------- compilar ----

def compilar(cfg, res: Resultado, verboso=True) -> bool:
    """Compila o main.tex com latexmk (ou N passagens do motor direto)."""
    motor = cfg.get("motor", "xelatex")
    diretorio = cfg.dir_saida

    ambiente_tex = ambiente_de_compilacao(cfg)
    if shutil.which("latexmk"):
        cmd = ["latexmk", "-%s" % motor, "-interaction=nonstopmode",
               "-halt-on-error", "-file-line-error", "main.tex"]
        ok = _rodar([cmd], diretorio, verboso, ambiente_tex)
    elif shutil.which(motor):
        cmd = [motor, "-interaction=nonstopmode", "-halt-on-error",
               "-file-line-error", "main.tex"]
        ok = _rodar([cmd] * int(cfg.get("passagens", 3)), diretorio, verboso,
                    ambiente_tex)
    else:
        print("ERRO: nem latexmk nem %s foram encontrados no PATH." % motor,
              file=sys.stderr)
        return False

    return ok and publicar_pdf(cfg, res)


def publicar_pdf(cfg, res: Resultado) -> bool:
    """Copia o main.pdf recém-compilado para o nome final do livro.

    Separado de `compilar` porque a compilação em container produz o mesmo
    main.pdf por fora, e o resultado precisa ser publicado do mesmo jeito.
    """
    gerado = cfg.dir_saida / "main.pdf"
    if not gerado.is_file():
        return False
    final = cfg.dir_saida / ("%s.pdf" % cfg.get("nome_arquivo", "livro"))
    shutil.copyfile(gerado, final)
    res.pdf = final
    return True


def ambiente_de_compilacao(cfg):
    """Variáveis de ambiente do LaTeX, com as pastas extras no TEXINPUTS.

    O ponto-e-vírgula final (":" no Unix) preserva os caminhos padrão do
    TeX Live — sem ele, o LaTeX deixaria de achar os próprios pacotes.
    """
    extras = [str((cfg.raiz / d).resolve()) for d in cfg.get("texinputs") or []]
    if not extras:
        return None
    env = dict(os.environ)
    atual = env.get("TEXINPUTS", "")
    env["TEXINPUTS"] = os.pathsep.join(extras) + os.pathsep + (atual or "")
    return env


def _rodar(comandos, diretorio: Path, verboso: bool, env=None) -> bool:
    for i, cmd in enumerate(comandos, 1):
        if verboso:
            print("  [%d/%d] %s" % (i, len(comandos), " ".join(cmd)))
        proc = subprocess.run(cmd, cwd=diretorio, capture_output=True,
                              text=True, errors="replace", env=env)
        if proc.returncode != 0:
            print(_resumo_erro(proc.stdout + proc.stderr), file=sys.stderr)
            return False
    return True


def _resumo_erro(saida: str, linhas=40) -> str:
    """Mostra só o que interessa de um log de LaTeX gigante."""
    interessantes = [l for l in saida.split("\n")
                     if l.startswith("!") or ".tex:" in l or
                     "LaTeX Error" in l or "Emergency stop" in l or
                     "Undefined control sequence" in l]
    corpo = interessantes[:linhas] or saida.split("\n")[-linhas:]
    return "\n--- erro de compilação ---\n" + "\n".join(corpo) + "\n"
