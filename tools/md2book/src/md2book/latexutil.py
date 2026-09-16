"""Escape de texto para LaTeX e substituição de símbolos Unicode sem glifo."""

import re

# ---------------------------------------------------------------- escape ----

_ESCAPES = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "%": r"\%",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_ESCAPES_RE = re.compile("|".join(re.escape(c) for c in _ESCAPES))

# Símbolos que as fontes DejaVu não cobrem (ou só cobrem na variante sans),
# mapeados para macros definidas no preâmbulo. Explícito de propósito: é aqui
# que se estende quando outro curso usar outros emojis.
SIMBOLOS = {
    "✅": r"\mdOK{}",          # ✅ marca de seleção
    "✔": r"\mdOK{}",          # ✔
    "❌": r"\mdNO{}",          # ❌ cruz vermelha
    "✖": r"\mdNO{}",          # ✖
    "⚠": r"\mdWarn{}",        # ⚠ (ausente na DejaVu Serif)
    "\U0001F7E1": r"\mdPartial{}",  # 🟡 círculo amarelo
    "\U0001F7E2": r"\mdGreen{}",    # 🟢
    "\U0001F534": r"\mdRed{}",      # 🔴
    "⬜": r"\mdTodo{}",        # ⬜ quadrado vazio
    "★": r"\mdStar{}",        # ★ (ausente na DejaVu Serif)
    "☆": r"\mdStarOpen{}",    # ☆
}
_SIMBOLOS_RE = re.compile("|".join(re.escape(c) for c in SIMBOLOS))

# Equivalentes ASCII para dentro de blocos verbatim, onde não há macros.
SIMBOLOS_ASCII = {
    "✅": "[ok]", "✔": "[ok]", "❌": "[x]", "✖": "[x]",
    "\U0001F7E1": "[~]", "\U0001F7E2": "[ok]", "\U0001F534": "[!]",
    "⬜": "[ ]",
}

# Caracteres invisíveis que só atrapalham: seletores de variação, BOM,
# espaços de largura zero e juntores.
_INVISIVEIS_RE = re.compile("[︎️﻿​‌‍⁠]")

# Setas e afins: sem elas "iniciante→intermediário" vira uma palavra só,
# larga demais para qualquer coluna estreita de tabela.
_SETAS = "→←↔↑↓⇒⇐⇔↦⟶⟵»«"
# Trechos longos sem espaço (URLs, caminhos) ganham quebra depois da barra.
_RUN_LONGO = 18
_SENTINELA = "\x01"

# Espaços exóticos que o LaTeX trata mal, normalizados para espaço comum.
_ESPACOS = {" ": "~", " ": "~", " ": " ", " ": " "}
_ESPACOS_RE = re.compile("|".join(_ESPACOS))


def limpar(texto: str) -> str:
    """Remove caracteres invisíveis (o espaço fino/duro vira ~ inquebrável)."""
    return _controles_visiveis(_INVISIVEIS_RE.sub("", texto))


def _marcar_quebras(texto: str) -> str:
    """Insere sentinelas onde o LaTeX pode quebrar a linha.

    Feito antes do escape, sobre o texto cru: assim o sentinela nunca cai
    dentro de uma macro que este módulo mesmo gerou.
    """
    saida = []
    for pedaco in re.split(r"(\s+)", texto):
        longo = len(pedaco) > _RUN_LONGO
        for ch in pedaco:
            saida.append(ch)
            if ch in _SETAS or (longo and ch in "/"):
                saida.append(_SENTINELA)
    return "".join(saida)


def escapar(texto: str) -> str:
    """Escapa os caracteres especiais do LaTeX num trecho de texto corrido."""
    texto = _marcar_quebras(limpar(texto))
    texto = _ESCAPES_RE.sub(lambda m: _ESCAPES[m.group(0)], texto)
    texto = _SIMBOLOS_RE.sub(lambda m: SIMBOLOS[m.group(0)], texto)
    texto = _ESPACOS_RE.sub(lambda m: _ESPACOS[m.group(0)], texto)
    return texto.replace(_SENTINELA, r"\mdbreak{}")


_MARCACAO_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)|[`*_~\[\]]")


def texto_visivel(markdown: str) -> str:
    """Aproxima o texto que o leitor verá, sem a marcação Markdown.

    Usado para estimar larguras de coluna, não para renderizar.
    """
    return _MARCACAO_RE.sub(lambda m: m.group(1) or "", limpar(markdown))


def escapar_verbatim(texto: str) -> str:
    """Prepara um bloco de código: tabs viram espaços, emojis viram ASCII."""
    texto = _INVISIVEIS_RE.sub("", texto)
    texto = texto.replace("\t", "    ").replace(" ", " ")
    for ch, ascii_ in SIMBOLOS_ASCII.items():
        texto = texto.replace(ch, ascii_)
    return _controles_visiveis_verbatim(texto)


# Caracteres de controle C0 (menos a quebra de linha), que o LaTeX recusa com
# "Text line contains an invalid character" e derrubam a compilação inteira.
# Aparecem de verdade em material técnico: sequência de escape de terminal,
# BEL, NUL vindo de um dump. Viram notação de circunflexo, como faz `cat -v`.
_CONTROLES_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")

# Fora de bloco verbatim, \x00 e \x01 NÃO são dados: são os sentinelas internos
# do conversor (o marcador de `inline._render` e o `_SENTINELA` de quebra daqui).
# Torná-los visíveis destruía todo negrito, itálico, link e código embutido,
# que saíam no LaTeX como "\textasciicircum{}@0\textasciicircum{}@".
_CONTROLES_TEXTO_RE = re.compile(r"[\x02-\x08\x0b-\x1f\x7f]")


def _visivel(m):
    codigo = ord(m.group(0))
    return "^?" if codigo == 0x7F else "^" + chr(codigo + 64)


def _controles_visiveis(texto: str) -> str:
    """Para texto corrido: preserva os sentinelas internos do conversor."""
    return _CONTROLES_TEXTO_RE.sub(_visivel, texto)


def _controles_visiveis_verbatim(texto: str) -> str:
    """Para blocos de código: nenhum sentinela circula aqui, então vale tudo."""
    return _CONTROLES_RE.sub(_visivel, texto)



# ------------------------------------------------------- código embutido ----

# Depois destes caracteres é seguro quebrar uma linha longa de código.
_PONTOS_QUEBRA = "/-.:_,=+"
_LIMIAR_QUEBRA = 14


def codigo_embutido(codigo: str, limiar: int = _LIMIAR_QUEBRA) -> str:
    """Converte `código` embutido em \\mdcode{...}, com pontos de quebra."""
    codigo = limpar(codigo).replace(" ", " ")
    for ch, ascii_ in SIMBOLOS_ASCII.items():
        codigo = codigo.replace(ch, ascii_)
    partes = []
    longo = len(codigo) > limiar
    for i, ch in enumerate(codigo):
        partes.append(_ESCAPES.get(ch, ch))
        if longo and ch in _PONTOS_QUEBRA and i < len(codigo) - 1:
            partes.append(r"\mdbreak{}")
    return r"\mdcode{" + "".join(partes) + "}"


# ------------------------------------------------------------------ URLs ----

def escapar_url(url: str) -> str:
    """Prepara uma URL para \\href: só % e # precisam de barra invertida."""
    url = limpar(url).strip()
    return url.replace("\\", r"\\").replace("%", r"\%").replace("#", r"\#")


# "1. Título", "1) Título", "10 · Título" e "3.2 Título": numeração escrita
# à mão no Markdown, que o LaTeX vai refazer sozinho. Quatro dígitos ficam de
# fora de propósito — "1979 → 2026" é conteúdo, não numeração.
_NUMERACAO_RE = re.compile(r"^\s*(?:\d{1,3}\s*[.)·:]|\d{1,3}(?:\.\d{1,3})+)\s+")


def remover_numeracao(titulo: str) -> str:
    """Tira a numeração manual do início de um título."""
    limpo = _NUMERACAO_RE.sub("", titulo).strip()
    return limpo or titulo.strip()


def rotulo(texto: str) -> str:
    """Gera um \\label seguro a partir de um caminho ou título."""
    texto = re.sub(r"[^0-9A-Za-z]+", "-", limpar(texto)).strip("-").lower()
    return texto or "sem-nome"


def nome_ambiente(nome: str) -> str:
    """Converte um nome qualquer em nome de ambiente LaTeX (só letras)."""
    tabela = {"0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
              "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine",
              "+": "Plus", "#": "Sharp"}
    saida = [ch if (ch.isalpha() and ch.isascii()) else tabela.get(ch, "")
             for ch in nome]
    return "".join(saida) or "Plain"
