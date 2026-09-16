"""Verificação do ambiente de compilação e as saídas quando falta alguma coisa.

Converter Markdown em LaTeX exige só a biblioteca padrão do Python. Chegar ao
PDF exige um motor TeX, os pacotes que o preâmbulo carrega e as fontes
configuradas — tudo fora do alcance do pip.

Este módulo descobre o que falta antes de tentar compilar e oferece três
caminhos: instalar no sistema, compilar dentro de um container ou parar no
`.tex`. A terceira sempre funciona, porque não depende de nada.
"""

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

TEMPO_LIMITE = 30

OK, FALTA, DESCONHECIDO = True, False, None


# ------------------------------------------------------------ diagnóstico ---

@dataclass
class Item:
    """Uma dependência e o que se descobriu sobre ela."""

    nome: str
    ok: Optional[bool]
    detalhe: str = ""
    obrigatorio: bool = True

    @property
    def marca(self) -> str:
        if self.ok is FALTA and not self.obrigatorio:
            return "·"          # ausente, mas não impede nada
        return {OK: "✓", FALTA: "✗", DESCONHECIDO: "?"}[self.ok]


@dataclass
class Diagnostico:
    """O retrato do ambiente desta máquina para compilar o livro."""

    motor: str = "xelatex"
    programas: List[Item] = field(default_factory=list)
    pacotes: List[Item] = field(default_factory=list)
    fontes: List[Item] = field(default_factory=list)
    docker: List[Item] = field(default_factory=list)

    @property
    def essenciais(self) -> List[Item]:
        return self.programas + self.pacotes + self.fontes

    @property
    def faltando(self) -> List[Item]:
        return [i for i in self.essenciais if i.ok is FALTA and i.obrigatorio]

    @property
    def pode_compilar(self) -> bool:
        """Sem nenhuma falha obrigatória, a compilação tem chance de dar certo.

        O que não deu para verificar (`DESCONHECIDO`) não bloqueia: é melhor
        tentar compilar e deixar o LaTeX falar do que barrar por precaução.
        """
        return not self.faltando

    @property
    def docker_pronto(self) -> bool:
        return bool(self.docker) and all(i.ok is OK for i in self.docker)


def _executar(cmd, tempo=TEMPO_LIMITE):
    """Roda um comando e devolve (código, saída). Nunca levanta exceção."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=tempo, errors="replace")
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return 127, ""


def pacotes_exigidos(cfg) -> List[str]:
    """Lê do próprio preâmbulo quais pacotes LaTeX o livro vai carregar.

    Extrair da fonte em vez de manter uma lista à parte evita o problema
    clássico: alguém acrescenta um \\usepackage e esquece de atualizar o
    verificador.
    """
    from .preamble import gerar_preambulo

    texto = gerar_preambulo(cfg, set())
    nomes = []
    for _, grupo in re.findall(r"\\usepackage(\[[^\]]*\])?\{([^}]+)\}", texto):
        for nome in grupo.split(","):
            nome = nome.strip()
            if nome and nome not in nomes:
                nomes.append(nome)
    return nomes


def fontes_exigidas(cfg) -> List[str]:
    """As famílias de fonte configuradas, sem repetição."""
    fontes = cfg.get("fontes", {}) or {}
    nomes = []
    for chave in ("texto", "titulo", "mono", "simbolos"):
        nome = fontes.get(chave)
        if nome and nome not in nomes:
            nomes.append(nome)
    return nomes


def _familias_instaladas():
    """Conjunto de famílias de fonte conhecidas pelo fontconfig, ou None."""
    if not shutil.which("fc-list"):
        return None
    codigo, saida = _executar(["fc-list", ":", "family"])
    if codigo != 0:
        return None
    familias = set()
    for linha in saida.split("\n"):
        for nome in linha.split(","):
            nome = nome.strip().lower()
            if nome:
                familias.add(nome)
    return familias or None


def diagnosticar(cfg) -> Diagnostico:
    """Examina a máquina e devolve o retrato completo do ambiente."""
    motor = cfg.get("motor", "xelatex")
    diag = Diagnostico(motor=motor)

    # --- programas ---
    caminho = shutil.which(motor)
    diag.programas.append(
        Item(motor, OK if caminho else FALTA,
             caminho or "não encontrado no PATH"))
    for opcional, para_que in (("latexmk", "resolve sozinho as passagens"),
                               ("kpsewhich", "localiza os pacotes LaTeX")):
        caminho = shutil.which(opcional)
        diag.programas.append(
            Item(opcional, OK if caminho else FALTA,
                 caminho or "opcional — %s" % para_que, obrigatorio=False))

    # --- pacotes LaTeX ---
    exigidos = pacotes_exigidos(cfg)
    if shutil.which("kpsewhich"):
        _, saida = _executar(["kpsewhich"] + ["%s.sty" % p for p in exigidos])
        achados = {Path(l.strip()).name for l in saida.split("\n") if l.strip()}
        for nome in exigidos:
            presente = "%s.sty" % nome in achados
            diag.pacotes.append(
                Item(nome, OK if presente else FALTA,
                     "" if presente else "%s.sty não encontrado" % nome))
    else:
        for nome in exigidos:
            diag.pacotes.append(
                Item(nome, DESCONHECIDO, "sem kpsewhich para verificar"))

    # --- fontes ---
    familias = _familias_instaladas()
    for nome in fontes_exigidas(cfg):
        if familias is None:
            diag.fontes.append(
                Item(nome, DESCONHECIDO, "sem fc-list para verificar"))
        else:
            presente = nome.lower() in familias
            diag.fontes.append(
                Item(nome, OK if presente else FALTA,
                     "" if presente else "família não instalada"))

    # --- docker, só para a opção do container ---
    binario = shutil.which("docker")
    diag.docker.append(Item("docker", OK if binario else FALTA,
                            binario or "não encontrado", obrigatorio=False))
    if binario:
        compose = comando_compose()
        diag.docker.append(
            Item("docker compose", OK if compose else FALTA,
                 " ".join(compose) if compose else "plugin compose ausente",
                 obrigatorio=False))
        codigo, _ = _executar(["docker", "info"], tempo=15)
        diag.docker.append(
            Item("daemon do docker", OK if codigo == 0 else FALTA,
                 "" if codigo == 0 else "não está rodando ou sem permissão",
                 obrigatorio=False))
    return diag


def comando_compose() -> Optional[List[str]]:
    """Descobre como chamar o Compose: plugin v2 ou binário antigo."""
    if shutil.which("docker"):
        codigo, _ = _executar(["docker", "compose", "version"], tempo=15)
        if codigo == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    return None


# --------------------------------------------------------------- relatório ---

ROTULOS = {"✓": "presentes", "✗": "ausentes", "·": "ausentes (opcionais)",
           "?": "não verificados"}


def relatorio(diag: Diagnostico, completo: bool = True) -> str:
    """Texto legível do diagnóstico.

    Itens iguais são agrupados: vinte linhas dizendo "sem kpsewhich para
    verificar" não informam mais do que uma.
    """
    linhas = ["Ambiente de compilação (motor: %s)" % diag.motor, ""]

    def secao(titulo, itens):
        mostrar = itens if completo else [i for i in itens if i.ok is not OK]
        if not mostrar:
            if itens:
                linhas.append("  %-22s ✓ %d presentes" % (titulo, len(itens)))
            return

        grupos = []
        for item in mostrar:
            chave = (item.marca, item.detalhe if item.ok is not OK else "")
            for grupo in grupos:
                if grupo[0] == chave:
                    grupo[1].append(item)
                    break
            else:
                grupos.append((chave, [item]))

        linhas.append("  %s" % titulo)
        for (marca, detalhe), membros in grupos:
            if len(membros) > 3:
                sufixo = ("  — %s" % detalhe) if detalhe else ""
                linhas.append("    %s %d %s%s"
                              % (marca, len(membros),
                                 ROTULOS.get(marca, "itens"), sufixo))
                continue
            for item in membros:
                extra = ("  — %s" % item.detalhe) if item.detalhe else ""
                linhas.append(("    %s %-20s%s"
                               % (item.marca, item.nome, extra)).rstrip())

    secao("Programas", diag.programas)
    secao("Pacotes LaTeX", diag.pacotes)
    secao("Fontes", diag.fontes)
    secao("Docker (opcional)", diag.docker)

    linhas.append("")
    total = len(diag.faltando)
    if diag.pode_compilar:
        linhas.append("  → Dá para compilar o PDF.")
    elif total == 1:
        linhas.append("  → Falta 1 dependência para compilar o PDF: %s."
                      % diag.faltando[0].nome)
    else:
        linhas.append("  → Faltam %d dependências para compilar o PDF: %s."
                      % (total, ", ".join(i.nome for i in diag.faltando)))
    return "\n".join(linhas)


# --------------------------------------------------- instalação no sistema ---

@dataclass
class Gerenciador:
    """Como instalar as dependências em cada família de sistema."""

    binario: str
    nome: str
    pacotes: List[str]
    instalar: List[str]
    atualizar: Optional[List[str]] = None
    usa_sudo: bool = True
    observacao: str = ""


GERENCIADORES = (
    Gerenciador(
        "apt-get", "apt (Debian/Ubuntu)",
        ["texlive-xetex", "texlive-latex-extra", "texlive-lang-portuguese",
         "latexmk", "fonts-dejavu"],
        ["apt-get", "install", "-y"], ["apt-get", "update"]),
    Gerenciador(
        "dnf", "dnf (Fedora/RHEL)",
        ["texlive-xetex", "texlive-collection-latexextra",
         "texlive-collection-langportuguese", "latexmk", "dejavu-fonts-all"],
        ["dnf", "install", "-y"]),
    Gerenciador(
        "zypper", "zypper (openSUSE)",
        ["texlive-xetex", "texlive-latexextra", "texlive-latexextra-fonts",
         "latexmk", "dejavu-fonts"],
        ["zypper", "--non-interactive", "install"]),
    Gerenciador(
        "pacman", "pacman (Arch)",
        ["texlive-xetex", "texlive-latexextra", "texlive-langextra",
         "texlive-fontsrecommended", "ttf-dejavu"],
        ["pacman", "-S", "--needed", "--noconfirm"]),
    Gerenciador(
        "brew", "Homebrew (macOS)",
        ["--cask", "mactex-no-gui", "font-dejavu"],
        ["brew", "install"], usa_sudo=False,
        observacao="O MacTeX é grande (vários GB) e demora."),
    Gerenciador(
        "winget", "winget (Windows)",
        ["MiKTeX.MiKTeX"],
        ["winget", "install", "-e", "--id"], usa_sudo=False,
        observacao="No Windows, instale as fontes DejaVu à parte: "
                   "https://dejavu-fonts.github.io/"),
)


def gerenciador_do_sistema() -> Optional[Gerenciador]:
    """O primeiro gerenciador de pacotes disponível nesta máquina."""
    for gerenciador in GERENCIADORES:
        if shutil.which(gerenciador.binario):
            return gerenciador
    return None


def _prefixo_sudo(gerenciador: Gerenciador) -> List[str]:
    if not gerenciador.usa_sudo:
        return []
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return []
    return ["sudo"] if shutil.which("sudo") else []


def comandos_de_instalacao(gerenciador: Gerenciador) -> List[List[str]]:
    """Os comandos exatos que instalariam tudo, na ordem."""
    sudo = _prefixo_sudo(gerenciador)
    comandos = []
    if gerenciador.atualizar:
        comandos.append(sudo + gerenciador.atualizar)
    comandos.append(sudo + gerenciador.instalar + gerenciador.pacotes)
    return comandos


def instalar_no_sistema(gerenciador: Gerenciador, verboso: bool = True) -> bool:
    """Executa a instalação nativa. A saída vai direto para o terminal.

    Sem capturar a saída de propósito: o sudo precisa do terminal para pedir
    a senha, e o usuário merece ver o progresso de um download longo.
    """
    for comando in comandos_de_instalacao(gerenciador):
        if verboso:
            print("  $ %s" % " ".join(comando))
        try:
            proc = subprocess.run(comando)
        except OSError as erro:
            print("ERRO ao executar: %s" % erro, file=sys.stderr)
            return False
        if proc.returncode != 0:
            print("ERRO: o comando acima falhou (código %d)."
                  % proc.returncode, file=sys.stderr)
            return False
    return True


# ---------------------------------------------------- compilação em container ---

IMAGEM_PADRAO = "md2book-latex:bookworm"

DOCKERFILE = """\
# Gerado pelo md2book. Imagem mínima, só para compilar o LaTeX.
# Os pacotes são os mesmos que o md2book instalaria no sistema.
FROM debian:bookworm-slim

RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
         texlive-xetex \\
         texlive-latex-extra \\
         texlive-lang-portuguese \\
         latexmk \\
         fonts-dejavu \\
    && fc-cache -f \\
    && rm -rf /var/lib/apt/lists/*

# As DejaVu vêm do fonts-dejavu, em TrueType. Imagens genéricas de TeX Live
# expõem também versões Type 1 das mesmas famílias, e o xdvipdfmx falha ao
# carregá-las ("Error occurred while loading font: ...DejaVuSansMono.pfb").
# Instalar pelo apt evita isso.
WORKDIR /trabalho
"""

# Cabeçalho comum: o volume aponta para a pasta de saída do livro (o pai
# desta pasta docker/), e o container escreve com o usuário do host — sem
# isso o build/ ficaria de propriedade do root.
_SERVICO = """\
services:
  latex:
%(origem)s    working_dir: /trabalho
    volumes:
      - "..:/trabalho"
    user: "${MD2BOOK_UID:-0}:${MD2BOOK_GID:-0}"
    environment:
      HOME: /tmp
      TEXMFVAR: /tmp/texmf-var
"""

COMPOSE_COM_BUILD = """\
# Gerado pelo md2book. Compila o LaTeX já convertido, sem tocar no sistema.
#
#   docker compose build && docker compose run --rm latex latexmk -xelatex main.tex
#
""" + _SERVICO

COMPOSE_IMAGEM_PRONTA = """\
# Gerado pelo md2book. Usa uma imagem pronta: nada é construído aqui.
#
#   docker compose run --rm latex latexmk -xelatex main.tex
#
""" + _SERVICO


def imagem_configurada(cfg) -> Optional[str]:
    """Imagem pronta escolhida pelo usuário, ou None para construir a nossa."""
    imagem = cfg.get("imagem_latex")
    return imagem.strip() if isinstance(imagem, str) and imagem.strip() else None


def preparar_container(cfg) -> Path:
    """Escreve o compose (e o Dockerfile, se for o caso) na pasta de saída."""
    pasta = cfg.dir_saida / "docker"
    pasta.mkdir(parents=True, exist_ok=True)

    imagem = imagem_configurada(cfg)
    if imagem:
        origem = "    image: %s\n" % imagem
        compose = COMPOSE_IMAGEM_PRONTA % {"origem": origem}
        (pasta / "Dockerfile").unlink(missing_ok=True)
    else:
        origem = "    build: .\n    image: %s\n" % IMAGEM_PADRAO
        compose = COMPOSE_COM_BUILD % {"origem": origem}
        (pasta / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8")

    (pasta / "compose.yaml").write_text(compose, encoding="utf-8")
    return pasta


def compilar_em_container(cfg, verboso: bool = True) -> bool:
    """Prepara a imagem (se preciso) e compila o livro dentro dela."""
    compose = comando_compose()
    if not compose:
        print("ERRO: docker compose não encontrado.", file=sys.stderr)
        return False

    pasta = preparar_container(cfg)
    ambiente = os.environ.copy()
    if hasattr(os, "getuid"):
        ambiente["MD2BOOK_UID"] = str(os.getuid())
        ambiente["MD2BOOK_GID"] = str(os.getgid())

    motor = cfg.get("motor", "xelatex")
    compilacao = ["latexmk", "-%s" % motor, "-interaction=nonstopmode",
                  "-halt-on-error", "-file-line-error", "main.tex"]

    etapas = []
    if not imagem_configurada(cfg):
        etapas.append(("Construindo a imagem (a primeira vez baixa o "
                       "TeX Live e demora)", compose + ["build"]))
    elif verboso:
        # Com imagem pronta não há etapa de "pull": o próprio "run" baixa o
        # que faltar, e um "pull" explícito quebraria numa imagem local.
        print("  Usando a imagem %s (o docker baixa se faltar)..."
              % imagem_configurada(cfg))
    etapas.append(("Compilando dentro do container",
                   compose + ["run", "--rm", "latex"] + compilacao))

    for descricao, comando in etapas:
        if verboso:
            print("  %s..." % descricao)
            print("  $ %s" % " ".join(comando))
        try:
            proc = subprocess.run(comando, cwd=pasta, env=ambiente)
        except OSError as erro:
            print("ERRO ao executar o docker: %s" % erro, file=sys.stderr)
            return False
        if proc.returncode != 0:
            print("ERRO: o comando acima falhou (código %d)."
                  % proc.returncode, file=sys.stderr)
            return False
    return True


# ------------------------------------------------------------- interação ---

def interativo() -> bool:
    """Há um humano do outro lado para responder a uma pergunta?"""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def perguntar_solucao(diag: Diagnostico) -> str:
    """Mostra o menu e devolve 'nativo', 'container' ou 'tex'."""
    gerenciador = gerenciador_do_sistema()

    print()
    print("Como você quer resolver?")
    print()

    if gerenciador:
        print("  1) Instalar no sistema, com %s" % gerenciador.nome)
        for comando in comandos_de_instalacao(gerenciador):
            print("       $ %s" % " ".join(comando))
        if gerenciador.observacao:
            print("     %s" % gerenciador.observacao)
        print("     Confira os comandos antes de aceitar: eles mexem no "
              "seu sistema.")
    else:
        print("  1) Instalar no sistema — indisponível: nenhum gerenciador")
        print("     de pacotes conhecido foi encontrado.")
    print()

    if diag.docker_pronto:
        print("  2) Compilar dentro de um container Docker")
        print("     Não instala nada no sistema. A primeira execução baixa")
        print("     o TeX Live na imagem (alguns minutos, ~2 GB).")
    else:
        ausentes = [i.nome for i in diag.docker if i.ok is not OK]
        print("  2) Compilar em container — indisponível: falta %s."
              % ", ".join(ausentes))
        print("     Instale o Docker e o Docker Compose e rode de novo:")
        print("     https://docs.docker.com/engine/install/")
    print()
    print("  3) Não instalar nada")
    print("     Gera os arquivos .tex e para, sem tentar compilar.")
    print()

    validas = {"3": "tex"}
    if gerenciador:
        validas["1"] = "nativo"
    if diag.docker_pronto:
        validas["2"] = "container"

    opcoes = "/".join(sorted(validas))
    while True:
        try:
            resposta = input("Escolha [%s] (Enter = 3): " % opcoes).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "tex"
        if not resposta:
            return "tex"
        if resposta in validas:
            return validas[resposta]
        print("Opção inválida. Responda com %s." % opcoes)
