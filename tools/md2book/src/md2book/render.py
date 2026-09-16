"""Renderização da árvore de nós Markdown para o corpo LaTeX de um capítulo."""

from typing import List

from . import blocks as B
from . import latexutil as lx
from .inline import ContextoLink, renderizar as inline

# Cabeçalhos: o "#" de topo já virou título do capítulo, então "##" é a
# divisão principal do texto.
SECOES = {1: "section", 2: "section", 3: "subsection",
          4: "subsubsection", 5: "paragraph", 6: "paragraph"}

# Estimativas em pontos para dimensionar colunas: largura média de um
# caractere no corpo da tabela, folga de \tabcolsep e largura útil da linha.
LARGURA_CARACTERE = 5.0
FOLGA_COLUNA = 9.0
LINHA_PT = 443.0
PISO_MAXIMO = 0.46
# Nenhuma coluna abaixo disto: uma célula só com "✅" mede pouco em
# caracteres, mas o símbolo desenhado precisa de espaço real.
PISO_ABSOLUTO = 0.075


class Renderizador:
    """Converte nós em LaTeX, acumulando as linguagens de código vistas."""

    def __init__(self, cfg, ctx: ContextoLink = None):
        self.cfg = cfg
        self.ctx = ctx or ContextoLink()
        self.linguagens = set()

    # ------------------------------------------------------------ topo ----

    def documento(self, doc) -> str:
        """Renderiza um documento inteiro, com o comando de capítulo."""
        self.ctx = ContextoLink(self.ctx.mapa, doc.relativo,
                                self.cfg.get("referencia_capitulo", True))
        partes = [self._comando_capitulo(doc), ""]
        partes.append(self.blocos(doc.nos))
        return "\n".join(partes).rstrip() + "\n"

    def _comando_capitulo(self, doc) -> str:
        titulo = inline(doc.titulo, self.ctx)
        curto = inline(doc.titulo_curto, self.ctx)
        comando = r"\chapter*" if doc.sem_numero else r"\chapter"
        linhas = []
        if doc.sem_numero:
            linhas.append(r"\chapter*{%s}" % titulo)
            linhas.append(r"\addcontentsline{toc}{chapter}{%s}" % curto)
            linhas.append(r"\markboth{%s}{%s}" % (curto, curto))
        elif curto != titulo:
            linhas.append(r"\chapter[%s]{%s}" % (curto, titulo))
        else:
            linhas.append(r"\chapter{%s}" % titulo)
        linhas.append(r"\label{%s}" % doc.rotulo)
        return "\n".join(linhas)

    # ---------------------------------------------------------- blocos ----

    def blocos(self, nos: List[B.No]) -> str:
        saida = []
        for no in nos:
            trecho = self.bloco(no)
            if trecho:
                saida.append(trecho)
        return "\n\n".join(saida)

    def bloco(self, no: B.No) -> str:
        if isinstance(no, B.Cabecalho):
            return self._cabecalho(no)
        if isinstance(no, B.Paragrafo):
            return inline(no.texto, self.ctx)
        if isinstance(no, B.Codigo):
            return self._codigo(no)
        if isinstance(no, B.Citacao):
            return self._citacao(no)
        if isinstance(no, B.Lista):
            return self._lista(no)
        if isinstance(no, B.Tabela):
            return self._tabela(no)
        if isinstance(no, B.Regua):
            return self._regua()
        return ""

    def _cabecalho(self, no: B.Cabecalho) -> str:
        comando = SECOES.get(no.nivel, "paragraph")
        bruto = no.texto
        if self.cfg.get("remover_numeracao_titulos", True):
            bruto = lx.remover_numeracao(bruto)
        return "\\%s{%s}" % (comando, inline(bruto, self.ctx))

    def _codigo(self, no: B.Codigo) -> str:
        lingua = no.linguagem or "texto"
        ambiente = "cb" + lx.nome_ambiente(lingua)
        self.linguagens.add((ambiente, lingua))
        corpo = lx.escapar_verbatim(no.codigo)
        # Blindagem: um \end{ambiente} literal dentro do código fecharia a
        # caixa cedo demais.
        corpo = corpo.replace("\\end{%s}" % ambiente, "\\end {%s}" % ambiente)
        return "\\begin{%s}\n%s\n\\end{%s}" % (ambiente, corpo, ambiente)

    def _citacao(self, no: B.Citacao) -> str:
        return "\\begin{mdquote}\n%s\n\\end{mdquote}" % self.blocos(no.filhos)

    def _regua(self) -> str:
        modo = self.cfg.get("regua_horizontal", "ignorar")
        if modo == "linha":
            return r"\mdrule{}"
        if modo == "ornamento":
            return r"\mdornament{}"
        return ""

    # ---------------------------------------------------------- listas ----

    def _lista(self, no: B.Lista) -> str:
        ambiente = "enumerate" if no.ordenada else "itemize"
        # O Beamer não convive com o enumitem: redefinir a lista lá faz
        # \labelenumi chamar a si mesmo. Sem opções, o início de contagem
        # vira \setcounter — que funciona nos dois mundos.
        sem_opcoes = not self.cfg.get("opcoes_lista", True)
        antes = []
        opcoes = []
        if no.ordenada and no.inicio != 1:
            if sem_opcoes:
                antes.append("\\setcounter{enumi}{%d}" % (no.inicio - 1))
            else:
                opcoes.append("start=%d" % no.inicio)
        if no.ordenada and not sem_opcoes:
            # Lista aninhada numera com letras, e letra acaba no 26: uma lista
            # que começa em "1990." (ano lido como marcador) estoura o contador
            # e derruba a compilação. Acima do limite, número sempre.
            ultimo = no.inicio + len(no.itens) - 1
            if ultimo > 26:
                opcoes.append("label=\\arabic*.")
        if any(item.tarefa is not None for item in no.itens) and not sem_opcoes:
            # Rótulos próprios (caixa marcada/vazia) precisam de largura fixa,
            # senão cada item começa numa coluna diferente.
            opcoes.append("leftmargin=1.7em, labelwidth=1.1em, "
                          "labelsep=0.6em, align=left")
        cabeca = "\\begin{%s}%s" % (
            ambiente, "[%s]" % ",".join(opcoes) if opcoes else "")
        linhas = antes + [cabeca]
        for item in no.itens:
            corpo = self.blocos(item.filhos).strip()
            if item.tarefa is None:
                linhas.append("\\item %s" % corpo)
            else:
                marca = r"\mdOK" if item.tarefa else r"\mdTodo"
                linhas.append("\\item[%s] %s" % (marca, corpo))
        linhas.append("\\end{%s}" % ambiente)
        return "\n".join(linhas)

    # --------------------------------------------------------- tabelas ----

    def _tabela(self, no: B.Tabela) -> str:
        n = len(no.cabecalho)
        if not n:
            return ""
        larguras = _larguras(no)
        colunas = "".join(
            "%sp{\\dimexpr %.4f\\linewidth-2\\tabcolsep\\relax}" %
            (_prefixo_alinhamento(a), w)
            for a, w in zip(no.alinhamentos, larguras))

        cabecalho = " & ".join(
            r"\textbf{%s}" % inline(c, self.ctx) for c in no.cabecalho)
        if self.cfg.get("tabela_simples"):
            # `longtable` não atravessa um frame de Beamer nem uma caixa:
            # onde a tabela não pode quebrar de página, sai um `tabular`.
            linhas = [r"\begin{mdtable}{@{}%s@{}}" % colunas,
                      r"\toprule", cabecalho + r" \\", r"\midrule"]
            for linha in no.linhas:
                linhas.append(" & ".join(inline(c, self.ctx) for c in linha)
                              + r" \\")
            linhas += [r"\bottomrule", r"\end{mdtable}"]
            return "\n".join(linhas)
        linhas = [
            r"\begin{mdtable}{@{}%s@{}}" % colunas,
            r"\toprule",
            cabecalho + r" \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            cabecalho + r" \\",
            r"\midrule",
            r"\endhead",
            r"\bottomrule",
            r"\endlastfoot",
        ]
        for linha in no.linhas:
            linhas.append(" & ".join(inline(c, self.ctx) for c in linha) + r" \\")
        linhas.append(r"\end{mdtable}")
        return "\n".join(linhas)


def _medida(texto: str) -> int:
    """Comprimento aparente: um símbolo desenhado ocupa mais que uma letra."""
    return sum(2 if ch in lx.SIMBOLOS else 1 for ch in texto)


def _prefixo_alinhamento(a: str) -> str:
    if a == "r":
        return r">{\RaggedLeft\arraybackslash}"
    if a == "c":
        return r">{\Centering\arraybackslash}"
    return r">{\RaggedRight\arraybackslash}"


def _larguras(no: B.Tabela) -> List[float]:
    """Reparte a largura da linha entre as colunas conforme o conteúdo.

    Duas forças em jogo: o peso (quanto texto a coluna costuma ter) e o piso
    (a maior palavra indivisível da coluna). Sem o piso, uma coluna estreita
    recebe "intermediário" e transborda; com ele, a tabela respira.
    """
    n = len(no.cabecalho)
    pesos, pisos = [], []
    for c in range(n):
        celulas = [no.cabecalho[c]]
        celulas += [linha[c] for linha in no.linhas if c < len(linha)]
        visiveis = [lx.texto_visivel(x) for x in celulas]

        tamanhos = [_medida(v) for v in visiveis] or [1]
        maior, media = max(tamanhos), sum(tamanhos) / len(tamanhos)
        pesos.append(max(1.0, (maior + media) / 2))

        palavra = max((_medida(p) for v in visiveis for p in v.split()),
                      default=1)
        pisos.append(min(PISO_MAXIMO,
                         max(PISO_ABSOLUTO,
                             (palavra * LARGURA_CARACTERE + FOLGA_COLUNA)
                             / LINHA_PT)))

    disponivel = 0.995
    if sum(pisos) >= disponivel:            # tabela apertada: só os pisos
        fator = disponivel / sum(pisos)
        return [p * fator for p in pisos]

    total = sum(pesos)
    larguras = [disponivel * p / total for p in pesos]
    # Sobe quem está abaixo do piso e cobra a diferença de quem tem folga.
    for _ in range(4):
        deficit = sum(max(0.0, pi - w) for pi, w in zip(pisos, larguras))
        if deficit < 1e-6:
            break
        folga = sum(max(0.0, w - pi) for pi, w in zip(pisos, larguras))
        if folga < 1e-6:
            break
        tomado = min(deficit, folga)
        larguras = [pi if w < pi else w - (w - pi) / folga * tomado
                    for pi, w in zip(pisos, larguras)]

    fator = disponivel / sum(larguras)
    return [w * fator for w in larguras]
