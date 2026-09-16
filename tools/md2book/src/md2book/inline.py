"""Conversão do Markdown embutido (negrito, links, código...) para LaTeX.

Estratégia: cada construção reconhecida é substituída por um marcador opaco
(\\x00N\\x00) e seu LaTeX já pronto vai para uma lista. Só o texto que sobra
— texto de verdade — é escapado no fim. Assim o escape nunca corrompe o LaTeX
que nós mesmos geramos.
"""

import re

from . import latexutil as lx

_MARCADOR_RE = re.compile("\x00(\\d+)\x00")

# `código`, ``código com ` dentro``
_CODIGO_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|~<>])")
_IMAGEM_RE = re.compile(r"!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_LINK_RE = re.compile(r"\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_AUTOLINK_RE = re.compile(r"<((?:https?|ftp)://[^>\s]+|[^>\s@]+@[^>\s]+)>")
_URL_NUA_RE = re.compile(r"(?<![\w/])((?:https?)://[^\s<>\"'\\)\]]+[^\s<>\"'\\)\].,;:])")

_ENFASES = (
    (re.compile(r"(?<!\*)\*\*\*(?!\s)(.+?)(?<!\s)\*\*\*(?!\*)", re.S), r"\textbf{\textit{%s}}"),
    (re.compile(r"(?<!\*)\*\*(?!\s)(.+?)(?<!\s)\*\*(?!\*)", re.S), r"\textbf{%s}"),
    (re.compile(r"(?<![\w\\])___(?!\s)(.+?)(?<!\s)___(?!\w)", re.S), r"\textbf{\textit{%s}}"),
    (re.compile(r"(?<![\w\\])__(?!\s)(.+?)(?<!\s)__(?!\w)", re.S), r"\textbf{%s}"),
    (re.compile(r"(?<!\*)\*(?!\s)([^*]+?)(?<!\s)\*(?!\*)", re.S), r"\textit{%s}"),
    # "_" só marca ênfase entre limites de palavra: preserva node_modules.
    (re.compile(r"(?<![\w\\])_(?!\s)([^_]+?)(?<!\s)_(?!\w)", re.S), r"\textit{%s}"),
    (re.compile(r"~~(?!\s)(.+?)(?<!\s)~~", re.S), r"\mdstrike{%s}"),
)


class ContextoLink:
    """Resolve links relativos para referências internas do livro.

    `mapa` associa o caminho de um arquivo-fonte (relativo à raiz) ao rótulo
    LaTeX do capítulo correspondente. Quem não estiver no mapa vira texto.
    """

    def __init__(self, mapa=None, origem="", mostrar_capitulo=True):
        self.mapa = mapa or {}
        self.origem = origem
        self.mostrar_capitulo = mostrar_capitulo

    def resolver(self, alvo: str):
        """Devolve o rótulo do capítulo para um alvo relativo, ou None."""
        alvo = alvo.split("#", 1)[0].strip()
        if not alvo:
            return None
        import posixpath
        base = posixpath.dirname(self.origem)
        for candidato in (posixpath.normpath(posixpath.join(base, alvo)) if base else alvo,
                          alvo.lstrip("./")):
            if candidato in self.mapa:
                return self.mapa[candidato]
            if candidato.endswith("/") and candidato + "README.md" in self.mapa:
                return self.mapa[candidato + "README.md"]
        return None


_CTX_VAZIO = ContextoLink()


def renderizar(texto: str, ctx: ContextoLink = None) -> str:
    """Converte um trecho de Markdown embutido em LaTeX."""
    slots = []
    saida = _render(texto, ctx or _CTX_VAZIO, slots)
    return _expandir(saida, slots)


def _expandir(texto: str, slots) -> str:
    """Troca os marcadores pelo LaTeX guardado, inclusive os aninhados."""
    return _MARCADOR_RE.sub(
        lambda m: _expandir(slots[int(m.group(1))], slots), texto)


def _render(texto: str, ctx: ContextoLink, slots) -> str:
    """Núcleo recursivo: devolve texto escapado, ainda com marcadores.

    A lista `slots` é compartilhada com as chamadas aninhadas, para que um
    marcador criado aqui continue válido dentro de um negrito ou de um link.
    """

    def guardar(latex: str) -> str:
        slots.append(latex)
        return "\x00%d\x00" % (len(slots) - 1)

    texto = lx.limpar(texto)
    # 1. Código embutido primeiro: nada dentro dele é Markdown.
    texto = _CODIGO_RE.sub(
        lambda m: guardar(lx.codigo_embutido(m.group(2).strip())), texto)
    # 2. Escapes de barra invertida, antes que * e _ sejam interpretados.
    texto = _ESCAPE_RE.sub(lambda m: guardar(lx.escapar(m.group(1))), texto)
    # 3. Links e imagens.
    texto = _IMAGEM_RE.sub(lambda m: guardar(_imagem(m, ctx)), texto)
    texto = _LINK_RE.sub(
        lambda m: guardar(_link(m.group(1), m.group(2), ctx, slots)), texto)
    texto = _AUTOLINK_RE.sub(lambda m: guardar(_autolink(m.group(1))), texto)
    texto = _URL_NUA_RE.sub(lambda m: guardar(_autolink(m.group(1))), texto)
    # 4. Ênfases, do marcador mais longo para o mais curto.
    for regex, molde in _ENFASES:
        texto = regex.sub(
            lambda m, M=molde: guardar(M % _render(m.group(1), ctx, slots)),
            texto)
    # 5. O que sobrou é texto puro.
    return lx.escapar(texto)


def _imagem(m, ctx) -> str:
    alt, destino = m.group(1), m.group(2)
    from pathlib import Path
    if ctx and getattr(ctx, "raiz_imagens", None):
        caminho = Path(ctx.raiz_imagens) / destino
        if caminho.exists():
            return (r"\begin{center}\includegraphics[max width=\linewidth]{%s}\end{center}"
                    % caminho.as_posix())
    return r"\textit{[imagem: %s]}" % lx.escapar(alt or destino)


def _link(rotulo_txt: str, destino: str, ctx: ContextoLink, slots) -> str:
    destino = destino.strip()
    texto_latex = _render(rotulo_txt, ctx, slots) if rotulo_txt else ""

    if destino.startswith("#"):          # âncora interna ao próprio arquivo
        return texto_latex or lx.escapar(destino)

    if re.match(r"^(https?|ftp|mailto):", destino):
        if not rotulo_txt or rotulo_txt.strip() == destino:
            return r"\url{%s}" % lx.escapar_url(destino)
        return r"\href{%s}{%s}" % (lx.escapar_url(destino), texto_latex)

    alvo = ctx.resolver(destino)
    if alvo:
        # O texto do link é o próprio nome do arquivo? Vira "cap. N" e pronto.
        so_arquivo = rotulo_txt.strip().strip("`").rstrip("/") in (
            destino.strip().rstrip("/"), destino.split("/")[-1].rstrip("/"),
            destino.split("/")[0])
        if so_arquivo or not rotulo_txt:
            return r"\hyperref[%s]{cap.~\ref*{%s}}" % (alvo, alvo)
        if ctx.mostrar_capitulo:
            return r"\hyperref[%s]{%s}~(cap.~\ref*{%s})" % (alvo, texto_latex, alvo)
        return r"\hyperref[%s]{%s}" % (alvo, texto_latex)

    # Caminho relativo que não virou capítulo: mostra como caminho literal.
    if texto_latex and rotulo_txt.strip() != destino:
        return "%s~(%s)" % (texto_latex, lx.codigo_embutido(destino))
    return lx.codigo_embutido(destino)


def _autolink(destino: str) -> str:
    if "@" in destino and not destino.startswith("mailto:"):
        return r"\href{mailto:%s}{%s}" % (lx.escapar_url(destino),
                                          lx.codigo_embutido(destino))
    return r"\url{%s}" % lx.escapar_url(destino)
