"""Analisador de blocos Markdown: linhas -> árvore de nós.

Reconhece cabeçalhos, código cercado, citações, listas (inclusive aninhadas e
de tarefas), tabelas GFM, réguas e parágrafos. Blocos que aninham (lista e
citação) são resolvidos por recursão sobre as linhas já sem o prefixo.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

# ------------------------------------------------------------------ nós ----


@dataclass
class No:
    """Base de todos os nós."""


@dataclass
class Cabecalho(No):
    nivel: int
    texto: str


@dataclass
class Paragrafo(No):
    texto: str


@dataclass
class Codigo(No):
    linguagem: str
    codigo: str


@dataclass
class Citacao(No):
    filhos: List[No] = field(default_factory=list)


@dataclass
class Item(No):
    filhos: List[No] = field(default_factory=list)
    tarefa: Optional[bool] = None       # None = item comum; True/False = [x]/[ ]


@dataclass
class Lista(No):
    ordenada: bool = False
    inicio: int = 1
    itens: List[Item] = field(default_factory=list)


@dataclass
class Tabela(No):
    cabecalho: List[str] = field(default_factory=list)
    linhas: List[List[str]] = field(default_factory=list)
    alinhamentos: List[str] = field(default_factory=list)


@dataclass
class Regua(No):
    pass


# -------------------------------------------------------------- padrões ----

RE_CERCA = re.compile(r"^(\s{0,3})(`{3,}|~{3,})[ \t]*([^`\s]*)[^`]*$")
RE_CABECALHO = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
RE_REGUA = re.compile(r"^\s{0,3}([-*_])[ \t]*(?:\1[ \t]*){2,}$")
RE_CITACAO = re.compile(r"^\s{0,3}>[ \t]?(.*)$")
RE_ITEM = re.compile(r"^(\s*)([-*+]|\d{1,9}[.)])([ \t]+)(.*)$")
RE_TAREFA = re.compile(r"^\[([ xX])\]\s+(.*)$")
RE_SEPARADOR_TABELA = re.compile(
    r"^\s{0,3}\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")


def _e_inicio_de_bloco(linha: str) -> bool:
    """A linha interrompe um parágrafo em andamento?"""
    return bool(
        not linha.strip()
        or RE_CERCA.match(linha)
        or RE_CABECALHO.match(linha)
        or RE_REGUA.match(linha)
        or RE_CITACAO.match(linha)
        or RE_ITEM.match(linha))


# ------------------------------------------------------------- analisar ----

def analisar(texto: str) -> List[No]:
    """Converte o corpo de um arquivo Markdown numa lista de nós."""
    linhas = texto.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    linhas = _remover_front_matter(linhas)
    return _analisar_linhas(linhas)


def _remover_front_matter(linhas):
    if linhas and linhas[0].strip() == "---":
        for i in range(1, len(linhas)):
            if linhas[i].strip() in ("---", "..."):
                return linhas[i + 1:]
    return linhas


def _analisar_linhas(linhas: List[str]) -> List[No]:
    nos: List[No] = []
    i = 0
    while i < len(linhas):
        linha = linhas[i]

        if not linha.strip():
            i += 1
            continue

        cerca = RE_CERCA.match(linha)
        if cerca:
            no, i = _ler_codigo(linhas, i, cerca)
            nos.append(no)
            continue

        cab = RE_CABECALHO.match(linha)
        if cab:
            nos.append(Cabecalho(len(cab.group(1)), cab.group(2).strip()))
            i += 1
            continue

        if RE_REGUA.match(linha):
            nos.append(Regua())
            i += 1
            continue

        if RE_CITACAO.match(linha):
            no, i = _ler_citacao(linhas, i)
            nos.append(no)
            continue

        if _e_tabela(linhas, i):
            no, i = _ler_tabela(linhas, i)
            nos.append(no)
            continue

        if RE_ITEM.match(linha):
            no, i = _ler_lista(linhas, i)
            nos.append(no)
            continue

        no, i = _ler_paragrafo(linhas, i)
        nos.append(no)
    return nos


def _ler_codigo(linhas, i, cerca):
    marca = cerca.group(2)
    recuo = len(cerca.group(1))
    linguagem = cerca.group(3).strip().lower()
    fechamento = re.compile(r"^\s{0,3}%s{%d,}\s*$" % (re.escape(marca[0]), len(marca)))
    corpo = []
    i += 1
    while i < len(linhas) and not fechamento.match(linhas[i]):
        linha = linhas[i]
        corpo.append(linha[recuo:] if linha[:recuo].strip() == "" else linha)
        i += 1
    if i < len(linhas):
        i += 1                              # consome a cerca de fechamento
    return Codigo(linguagem, "\n".join(corpo)), i


def _ler_citacao(linhas, i):
    dentro = []
    while i < len(linhas):
        m = RE_CITACAO.match(linhas[i])
        if m:
            dentro.append(m.group(1))
            i += 1
        elif linhas[i].strip() and dentro and not _e_inicio_de_bloco(linhas[i]):
            dentro.append(linhas[i])        # continuação preguiçosa
            i += 1
        else:
            break
    return Citacao(_analisar_linhas(dentro)), i


def _ler_paragrafo(linhas, i):
    corpo = []
    while i < len(linhas) and not _e_inicio_de_bloco(linhas[i]):
        if _e_tabela(linhas, i):
            break
        corpo.append(linhas[i].strip())
        i += 1
    return Paragrafo("\n".join(corpo)), i


# -------------------------------------------------------------- tabelas ----

def _e_tabela(linhas, i):
    return ("|" in linhas[i]
            and i + 1 < len(linhas)
            and RE_SEPARADOR_TABELA.match(linhas[i + 1])
            and "|" in linhas[i + 1])


def dividir_celulas(linha: str) -> List[str]:
    """Divide uma linha de tabela em células, respeitando `|` e \\|."""
    linha = linha.strip()
    if linha.startswith("|"):
        linha = linha[1:]
    if linha.endswith("|") and not linha.endswith("\\|"):
        linha = linha[:-1]
    celulas, buf = [], []
    em_codigo = False
    i = 0
    while i < len(linha):
        ch = linha[i]
        if ch == "\\" and i + 1 < len(linha) and linha[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "`":
            em_codigo = not em_codigo
        if ch == "|" and not em_codigo:
            celulas.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    celulas.append("".join(buf))
    return [c.strip() for c in celulas]


def _ler_tabela(linhas, i):
    cabecalho = dividir_celulas(linhas[i])
    alinhamentos = []
    for celula in dividir_celulas(linhas[i + 1]):
        esquerda, direita = celula.startswith(":"), celula.endswith(":")
        alinhamentos.append("c" if esquerda and direita
                            else "r" if direita else "l")
    i += 2
    corpo = []
    while i < len(linhas) and linhas[i].strip() and "|" in linhas[i]:
        if RE_CABECALHO.match(linhas[i]) or RE_CERCA.match(linhas[i]):
            break
        celulas = dividir_celulas(linhas[i])
        celulas += [""] * (len(cabecalho) - len(celulas))
        corpo.append(celulas[:len(cabecalho)])
        i += 1
    alinhamentos += ["l"] * (len(cabecalho) - len(alinhamentos))
    return Tabela(cabecalho, corpo, alinhamentos[:len(cabecalho)]), i


# --------------------------------------------------------------- listas ----

def _tipo_marcador(marcador: str) -> bool:
    """True se o marcador for de lista ordenada."""
    return marcador[0].isdigit()


def _ler_lista(linhas, i):
    primeiro = RE_ITEM.match(linhas[i])
    recuo_base = len(primeiro.group(1))
    ordenada = _tipo_marcador(primeiro.group(2))
    inicio = int(primeiro.group(2)[:-1]) if ordenada else 1
    itens: List[Item] = []
    corrente: List[str] = None
    recuo_conteudo = 0
    brancos = 0

    while i < len(linhas):
        linha = linhas[i]
        m = RE_ITEM.match(linha)

        if not linha.strip():
            brancos += 1
            i += 1
            continue

        # Novo item do mesmo nível (recuo tolerante a 1 espaço de folga).
        if m and len(m.group(1)) <= recuo_base + 1 and \
                _tipo_marcador(m.group(2)) == ordenada:
            if corrente is not None:
                itens.append(_montar_item(corrente))
            recuo_conteudo = len(m.group(1)) + len(m.group(2)) + len(m.group(3))
            corrente = [m.group(4)]
            brancos = 0
            i += 1
            continue

        recuo = len(linha) - len(linha.lstrip())
        if corrente is not None and (recuo >= recuo_conteudo or
                                     (recuo >= recuo_base + 2 and m)):
            corrente.extend([""] * brancos)
            corrente.append(linha[recuo_conteudo:] if recuo >= recuo_conteudo
                            else linha[recuo_base + 2:])
            brancos = 0
            i += 1
            continue

        # Continuação preguiçosa: texto solto logo abaixo do item.
        if corrente is not None and brancos == 0 and not m and \
                not _e_inicio_de_bloco(linha):
            corrente.append(linha.strip())
            i += 1
            continue

        break

    if corrente is not None:
        itens.append(_montar_item(corrente))
    return Lista(ordenada, inicio, itens), i


def _montar_item(linhas_item: List[str]) -> Item:
    tarefa = None
    if linhas_item:
        m = RE_TAREFA.match(linhas_item[0])
        if m:
            tarefa = m.group(1).lower() == "x"
            linhas_item = [m.group(2)] + linhas_item[1:]
    return Item(_analisar_linhas(linhas_item), tarefa)
