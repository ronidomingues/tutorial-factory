"""Descoberta dos arquivos Markdown, ordenação e divisão em partes."""

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from . import blocks as B
from . import latexutil as lx

LIMITE_TITULO_CURTO = 55


@dataclass
class Documento:
    """Um arquivo Markdown já lido e analisado, pronto para virar capítulo."""

    caminho: Path
    relativo: str
    titulo: str
    titulo_curto: str
    rotulo: str
    nos: List[B.No] = field(default_factory=list)
    sem_numero: bool = False


@dataclass
class Parte:
    """Uma parte do livro (agrupa capítulos)."""

    titulo: str = ""
    subtitulo: str = ""
    documentos: List[Documento] = field(default_factory=list)


@dataclass
class Estrutura:
    """O livro inteiro: aberturas, partes e o anexo de código-fonte."""

    abertura: List[Documento] = field(default_factory=list)
    partes: List[Parte] = field(default_factory=list)
    fontes: List[Path] = field(default_factory=list)

    def documentos(self):
        yield from self.abertura
        for parte in self.partes:
            yield from parte.documentos


# ------------------------------------------------------------- ordenação ----

_NUM_RE = re.compile(r"(\d+)")


def chave_natural(texto: str):
    """Ordena '2' antes de '10' e mantém o resto alfabético."""
    return [int(p) if p.isdigit() else p.lower()
            for p in _NUM_RE.split(str(texto))]


def _combina(relativo: str, padroes) -> bool:
    return any(fnmatch.fnmatch(relativo, p) or
               fnmatch.fnmatch(relativo, p.rstrip("/") + "/**") or
               relativo == p
               for p in padroes)


# --------------------------------------------------------------- títulos ----

_PREFIXO_NUM_RE = re.compile(r"^\s*\d{1,3}\s*[·.:\-–—)]\s*")
_TRAVESSAO_RE = re.compile(r"\s+[—–]\s+|\s+-\s+")


def encurtar_titulo(titulo: str, limite: int = LIMITE_TITULO_CURTO) -> str:
    """Título curto para sumário e cabeçalhos de página."""
    curto = _PREFIXO_NUM_RE.sub("", titulo).strip()
    if len(curto) <= limite:
        return curto or titulo
    primeiro = _TRAVESSAO_RE.split(curto)[0].strip()
    if primeiro and len(primeiro) <= limite:
        return primeiro
    corte = (primeiro or curto)[:limite]
    return corte[:corte.rfind(" ")].rstrip(",;:") + "…" if " " in corte else corte


def _extrair_titulo(nos: List[B.No], nome: str):
    """Tira o primeiro '#' do documento e devolve (título, nós restantes)."""
    for i, no in enumerate(nos):
        if isinstance(no, B.Cabecalho) and no.nivel == 1:
            return no.texto, nos[:i] + nos[i + 1:]
        if not isinstance(no, B.Regua):
            break
    return Path(nome).stem.replace("-", " ").replace("_", " ").strip(), nos


# ------------------------------------------------------------ descoberta ----

def coletar_markdown(cfg) -> List[Path]:
    """Todos os .md sob a raiz, menos os ignorados, em ordem natural."""
    raiz = cfg.raiz
    ignorar = cfg.get("ignorar", [])
    achados = []
    for caminho in raiz.rglob("*.md"):
        if not caminho.is_file():
            continue
        rel = caminho.relative_to(raiz).as_posix()
        if _combina(rel, ignorar):
            continue
        achados.append(caminho)
    return sorted(achados, key=lambda p: chave_natural(p.relative_to(raiz).as_posix()))


def carregar_documento(caminho: Path, raiz: Path, titulos: dict,
                       sem_numero: bool = False,
                       limpar_numeracao: bool = True) -> Documento:
    rel = caminho.relative_to(raiz).as_posix()
    texto = caminho.read_text(encoding="utf-8")
    nos = B.analisar(texto)
    titulo, nos = _extrair_titulo(nos, rel)
    titulo = titulos.get(rel, titulo)
    if limpar_numeracao:
        titulo = lx.remover_numeracao(titulo)
    return Documento(
        caminho=caminho,
        relativo=rel,
        titulo=titulo,
        titulo_curto=encurtar_titulo(titulo),
        rotulo="cap:" + lx.rotulo(rel[:-3] if rel.endswith(".md") else rel),
        nos=nos,
        sem_numero=sem_numero,
    )


def montar_estrutura(cfg) -> Estrutura:
    """Lê todos os documentos e os distribui em aberturas e partes."""
    raiz = cfg.raiz
    titulos = cfg.get("titulos", {}) or {}
    limpar_num = cfg.get("remover_numeracao_titulos", True)
    arquivos = coletar_markdown(cfg)
    restantes = {p.relative_to(raiz).as_posix(): p for p in arquivos}
    estrutura = Estrutura()

    def retirar(padroes) -> List[Path]:
        escolhidos = [rel for rel in restantes if _combina(rel, padroes)]
        # Respeita a ordem em que os padrões foram escritos na configuração.
        def posicao(rel):
            for i, p in enumerate(padroes):
                if _combina(rel, [p]):
                    return (i, chave_natural(rel))
            return (len(padroes), chave_natural(rel))
        escolhidos.sort(key=posicao)
        return [restantes.pop(rel) for rel in escolhidos]

    for caminho in retirar(cfg.get("abertura", []) or []):
        estrutura.abertura.append(
            carregar_documento(caminho, raiz, titulos, sem_numero=True,
                               limpar_numeracao=limpar_num))

    for definicao in cfg.get("partes", []) or []:
        parte = Parte(definicao.get("titulo", ""), definicao.get("subtitulo", ""))
        for caminho in retirar(definicao.get("arquivos", [])):
            parte.documentos.append(
                carregar_documento(caminho, raiz, titulos,
                                   limpar_numeracao=limpar_num))
        if parte.documentos:
            estrutura.partes.append(parte)

    if restantes and cfg.get("incluir_restantes", True):
        sobras = [restantes[rel] for rel in
                  sorted(restantes, key=chave_natural)]
        docs = [carregar_documento(c, raiz, titulos, limpar_numeracao=limpar_num)
                for c in sobras]
        if estrutura.partes:
            extra = cfg.get("titulo_restantes", "Complementos")
            estrutura.partes.append(Parte(extra, "", docs))
        else:
            estrutura.partes.append(Parte("", "", docs))

    estrutura.fontes = coletar_fontes(cfg)
    return estrutura


def coletar_fontes(cfg) -> List[Path]:
    """Arquivos de código-fonte que entram no anexo, em ordem natural."""
    ap = cfg.get("apendice_fontes", {}) or {}
    if not ap.get("ativo"):
        return []
    raiz = cfg.raiz
    ignorar = ap.get("ignorar", [])
    limite = ap.get("tamanho_maximo", 200000)
    achados = []
    for padrao in ap.get("padroes", []):
        for caminho in sorted(raiz.glob(padrao), key=chave_natural):
            if not caminho.is_file():
                continue
            rel = caminho.relative_to(raiz).as_posix()
            if _combina(rel, ignorar) or rel.endswith(".md"):
                continue
            if caminho.stat().st_size > limite or not _e_texto(caminho):
                continue
            if caminho not in achados:
                achados.append(caminho)
    return achados


def _e_texto(caminho: Path) -> bool:
    """Heurística simples: sem bytes nulos nos primeiros 4 KB e decodifica."""
    try:
        amostra = caminho.open("rb").read(4096)
    except OSError:
        return False
    if b"\x00" in amostra:
        return False
    try:
        amostra.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def mapa_de_links(estrutura: Estrutura) -> dict:
    """Caminho relativo -> rótulo do capítulo, para resolver links internos."""
    mapa = {}
    for doc in estrutura.documentos():
        mapa[doc.relativo] = doc.rotulo
        mapa[doc.relativo.lstrip("./")] = doc.rotulo
        if doc.relativo.endswith("/README.md"):
            mapa[doc.relativo[:-len("README.md")]] = doc.rotulo
            mapa[doc.relativo[:-len("/README.md")]] = doc.rotulo
    return mapa
