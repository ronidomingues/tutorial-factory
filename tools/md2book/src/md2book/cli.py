"""Interface de linha de comando do md2book."""

import argparse
import sys
from pathlib import Path

from . import __version__, ambiente, build, config, discovery, slides


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="md2book",
        description="Transforma uma pasta de arquivos Markdown num livro "
                    "em LaTeX/PDF.")
    p.add_argument("comando", nargs="?", default="livro",
                   choices=["livro", "tex", "slides", "slides-tex", "listar",
                            "verificar", "init"],
                   help="livro: gera .tex e compila o PDF (padrão); "
                        "tex: só gera os .tex; "
                        "slides: gera e compila os slides das aulas; "
                        "slides-tex: só gera os .tex dos slides; "
                        "listar: mostra a ordem dos capítulos; "
                        "verificar: confere LaTeX e fontes desta máquina; "
                        "init: cria um livro.json de exemplo")
    p.add_argument("-c", "--config", help="arquivo de configuração JSON")
    p.add_argument("-r", "--raiz", help="pasta com os .md (padrão: a do config)")
    p.add_argument("-s", "--saida", help="pasta de saída")
    p.add_argument("-t", "--titulo", help="título do livro")
    p.add_argument("-a", "--autor", help="nome do autor, impresso na capa")
    p.add_argument("--ambiente", default="perguntar",
                   choices=["perguntar", "instalar", "container", "parar",
                            "ignorar"],
                   help="o que fazer quando faltar LaTeX ou fontes: "
                        "perguntar (padrão, cai em 'parar' sem terminal); "
                        "instalar (instala no sistema); "
                        "container (compila no Docker, sempre); "
                        "parar (gera só os .tex); "
                        "ignorar (não verifica nada)")
    p.add_argument("-q", "--silencioso", action="store_true")
    p.add_argument("-V", "--version", action="version",
                   version="md2book %s" % __version__)
    args = p.parse_args(argv)

    if args.comando == "init":
        return _init(args)

    if args.comando in ("slides", "slides-tex"):
        return _slides(args)

    try:
        cfg = config.carregar_config(args.config, args.raiz)
    except (FileNotFoundError, ValueError) as erro:
        print("ERRO: %s" % erro, file=sys.stderr)
        return 2

    if args.saida:
        cfg.dados["saida"] = args.saida
    if args.titulo:
        cfg.dados["titulo"] = args.titulo
    if args.autor:
        cfg.dados["autor"] = args.autor
    verboso = not args.silencioso

    if args.comando == "listar":
        return _listar(cfg)

    if args.comando == "verificar":
        return _verificar(cfg)

    if verboso:
        print("Raiz : %s" % cfg.raiz)
        print("Saída: %s" % cfg.dir_saida)
        print("Convertendo Markdown -> LaTeX...")
    res = build.renderizar(cfg, verboso)
    if verboso:
        print("%d capítulos, %d arquivos de código, %d linguagens." %
              (res.capitulos, res.fontes, len(res.linguagens)))
        print("main.tex: %s" % res.main)

    if args.comando == "tex":
        return 0

    return _compilar(cfg, res, args.ambiente, verboso)


def _slides(args) -> int:
    """Converte os decks de aula em Beamer e, se pedido, compila os PDFs."""
    try:
        cfg = slides.carregar_config(args.config, args.raiz)
    except (FileNotFoundError, ValueError) as erro:
        print("ERRO: %s" % erro, file=sys.stderr)
        return 2
    if args.saida:
        cfg.dados["saida"] = args.saida
    if args.titulo:
        cfg.dados["curso"] = args.titulo
    if args.autor:
        cfg.dados["autor"] = args.autor
    verboso = not args.silencioso

    entrada = (cfg.raiz / cfg.get("entrada", "md")).resolve()
    if verboso:
        print("Decks: %s" % entrada)
        print("Convertendo Markdown -> Beamer...")
    res = slides.renderizar(cfg, verboso)
    if not res.aulas:
        print("ERRO: nenhum deck .md encontrado em %s" % entrada,
              file=sys.stderr)
        return 2
    if verboso:
        print("%d aulas, %d slides." % (len(res.aulas), res.slides))
    for aviso in res.avisos:
        print("AVISO: %s" % aviso, file=sys.stderr)

    if args.comando == "slides-tex":
        return 0

    if not slides.compilar(cfg, res, verboso):
        return 1
    slides.limpar_intermediarios(cfg)
    prontos = [item[2] for item in res.aulas if item[2]]
    print("%d PDFs de aula em %s"
          % (len(prontos), (cfg.raiz / cfg.get("saida_pdf", "pdf")).resolve()))
    return 0


def _verificar(cfg) -> int:
    """Mostra o retrato do ambiente e devolve 0 se dá para compilar."""
    diag = ambiente.diagnosticar(cfg)
    print(ambiente.relatorio(diag))
    if diag.pode_compilar:
        return 0
    gerenciador = ambiente.gerenciador_do_sistema()
    if gerenciador:
        print()
        print("Para instalar no sistema (%s):" % gerenciador.nome)
        for comando in ambiente.comandos_de_instalacao(gerenciador):
            print("  $ %s" % " ".join(comando))
    print()
    print("Ou compile sem instalar nada:  md2book --ambiente container")
    return 1


def _parar_no_tex(cfg, res) -> int:
    """Encerra sem compilar, deixando claro o que ficou pronto."""
    print()
    print("Nada foi instalado. Os arquivos .tex estão prontos em %s"
          % cfg.dir_tex)
    print("Resolva as dependências e rode de novo para gerar o PDF.")
    return 3


def _compilar(cfg, res, politica: str, verboso: bool) -> int:
    """Compila o PDF, tratando a ausência de LaTeX conforme a política."""
    if politica == "container":
        return _via_container(cfg, res, verboso)

    if politica != "ignorar":
        diag = ambiente.diagnosticar(cfg)
        if not diag.pode_compilar:
            print()
            print(ambiente.relatorio(diag, completo=False))

            escolha = politica
            if politica == "perguntar":
                if ambiente.interativo():
                    escolha = ambiente.perguntar_solucao(diag)
                else:
                    escolha = "parar"
                    print()
                    print("Sem terminal interativo: nada será instalado.")

            if escolha in ("parar", "tex"):
                return _parar_no_tex(cfg, res)
            if escolha == "container":
                return _via_container(cfg, res, verboso)
            if escolha in ("instalar", "nativo"):
                if not _instalar(diag, verboso):
                    return _parar_no_tex(cfg, res)
                diag = ambiente.diagnosticar(cfg)
                if not diag.pode_compilar:
                    print()
                    print(ambiente.relatorio(diag, completo=False))
                    print("A instalação não resolveu tudo.")
                    return _parar_no_tex(cfg, res)

    if verboso:
        print("Compilando com %s..." % cfg.get("motor", "xelatex"))
    if not build.compilar(cfg, res, verboso):
        print("Falha na compilação. Log completo em %s"
              % (cfg.dir_saida / "main.log"), file=sys.stderr)
        return 1
    print("PDF pronto: %s" % res.pdf)
    return 0


def _instalar(diag, verboso: bool) -> bool:
    gerenciador = ambiente.gerenciador_do_sistema()
    if gerenciador is None:
        print("ERRO: nenhum gerenciador de pacotes conhecido nesta máquina.",
              file=sys.stderr)
        return False
    print()
    print("Instalando com %s..." % gerenciador.nome)
    return ambiente.instalar_no_sistema(gerenciador, verboso)


def _via_container(cfg, res, verboso: bool) -> int:
    diag = ambiente.diagnosticar(cfg)
    if not diag.docker_pronto:
        print()
        print(ambiente.relatorio(diag, completo=False))
        print("Para compilar em container é preciso Docker e Docker Compose")
        print("em funcionamento: https://docs.docker.com/engine/install/")
        return _parar_no_tex(cfg, res)

    if verboso:
        print("Compilando em container...")
    if not ambiente.compilar_em_container(cfg, verboso):
        print("Falha na compilação em container. Log em %s"
              % (cfg.dir_saida / "main.log"), file=sys.stderr)
        return 1
    if not build.publicar_pdf(cfg, res):
        print("O container terminou, mas nenhum PDF foi produzido.",
              file=sys.stderr)
        return 1
    print("PDF pronto: %s" % res.pdf)
    return 0


def _listar(cfg) -> int:
    estrutura = discovery.montar_estrutura(cfg)
    if estrutura.abertura:
        print("Abertura (sem numeração):")
        for doc in estrutura.abertura:
            print("   %-40s %s" % (doc.relativo, doc.titulo_curto))
    n = 0
    for parte in estrutura.partes:
        print("\n%s" % (parte.titulo or "(capítulos)"))
        for doc in parte.documentos:
            n += 1
            print("  %2d. %-40s %s" % (n, doc.relativo, doc.titulo_curto))
    if estrutura.fontes:
        print("\nAnexo de código-fonte (%d arquivos):" % len(estrutura.fontes))
        for caminho in estrutura.fontes:
            print("   %s" % caminho.relative_to(cfg.raiz).as_posix())
    return 0


def _init(args) -> int:
    destino = Path(args.config or config.NOME_PADRAO)
    if destino.exists():
        print("ERRO: %s já existe." % destino, file=sys.stderr)
        return 2
    dados = dict(config.CONFIG_PADRAO)
    dados["titulo"] = args.titulo or "Meu livro"
    dados["autor"] = args.autor or ""
    config.escrever_config_exemplo(destino, dados)
    print("Criado: %s" % destino)
    return 0
