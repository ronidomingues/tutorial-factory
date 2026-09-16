"""Configuração do livro: valores padrão, leitura do JSON e mesclagem."""

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path

NOME_PADRAO = "livro.json"

CONFIG_PADRAO = {
    # ----------------------------------------------------------- capa ----
    "titulo": "Livro",
    "subtitulo": "",
    "autor": "",
    "ano": "",
    "nota_capa": "",
    "idioma": "brazil",

    # -------------------------------------------------------- arquivos ----
    "raiz": ".",
    "saida": "build",
    "nome_arquivo": "livro",
    # Ordem: entradas explícitas primeiro; o resto entra em ordem natural.
    "ignorar": ["build/**", "md2book/**", "**/node_modules/**", "**/.git/**"],
    # Capítulos sem numeração, antes das partes (mapa, prefácio...).
    "abertura": [],
    # Partes do livro: {"titulo", "subtitulo", "arquivos": [globs]}.
    "partes": [],
    # Arquivos que sobrarem entram no fim, em ordem natural?
    "incluir_restantes": True,
    # Nome da parte que recolhe os arquivos não citados em "partes".
    "titulo_restantes": "Complementos",
    # Renomeia capítulos sem tocar no Markdown: {"arquivo.md": "Novo título"}.
    "titulos": {},

    # ---------------------------------------------------------- estilo ----
    "papel": "a4paper",
    "corpo": "11pt",
    "duas_faces": True,
    # Qualquer conjunto de chaves do pacote geometry.
    "geometria": ("inner=3.0cm,outer=2.4cm,top=2.5cm,"
                  "bottom=2.7cm,headsep=14pt"),
    "cor_destaque": "1F4E79",
    "cor_codigo_fundo": "F6F6F4",
    "cor_codigo_borda": "DCDCD5",
    "ligaduras_tex": False,
    "fontes": {
        "texto": "DejaVu Serif",
        "titulo": "DejaVu Sans",
        "mono": "DejaVu Sans Mono",
        "simbolos": "DejaVu Sans",
        "escala_texto": 0.92,
        "escala_mono": 0.80,
        # Pasta com os arquivos de fonte, relativa à pasta de saída (onde o
        # main.tex é compilado). Preenchida, as fontes são carregadas do disco
        # e não precisam estar instaladas na máquina — é o que faz o mesmo
        # PDF sair igual em outro computador.
        "diretorio": None,
        "extensao": ".ttf",
        # Faces de cada família, no padrão do fontspec ("*" = nome da família).
        # Só valem quando "diretorio" está preenchido.
        "texto_faces": {},
        "titulo_faces": {},
        "mono_faces": {},
    },
    # Corpo do texto dentro das caixas de código, em pontos. Menor faz caber
    # diagramas mais largos. A entrelinha vem daqui quando fica em null.
    "tamanho_codigo": 7.8,
    "entrelinha_codigo": None,
    # Quanto as caixas de código avançam nas margens, de cada lado.
    "sangria_codigo": "0.9cm",
    # Como tratar "---" no meio do texto: ignorar | linha | ornamento
    "regua_horizontal": "ignorar",
    # "## 1. Título" já é numerado pelo LaTeX: tira a numeração escrita à mão.
    "remover_numeracao_titulos": True,
    # Mostrar "(cap. N)" ao lado de links internos com texto próprio.
    "referencia_capitulo": True,
    # Rótulo com a linguagem em cima de cada bloco de código.
    "rotulo_linguagem": True,
    "profundidade_sumario": 1,
    "profundidade_numeracao": 2,

    # ------------------------------------------------------ tema/marca ----
    # Arquivos copiados para a pasta de saída antes de compilar (pacotes .sty,
    # logos, arquivo de ambiente). Caminhos relativos à raiz do projeto.
    "recursos": [],
    # Pastas acrescentadas ao TEXINPUTS na hora de compilar.
    "texinputs": [],
    # \usepackage{...} emitidos no fim do preâmbulo, nesta ordem.
    "pacotes_extra": [],
    # Linhas LaTeX cruas no fim do preâmbulo (string ou lista de strings).
    "preambulo_extra": "",
    # Comando que abre o livro. O padrão desenha a capa do próprio md2book;
    # um tema pode trocar por um comando seu (ex.: "\\adaberturalivro").
    "capa_comando": "\\mdcapa",
    # Comandos emitidos logo antes de \end{document} (colofão, ficha final).
    "encerramento": [],
    # Tabelas como `tabular` simples em vez de `longtable` (slides e caixas).
    "tabela_simples": False,

    # ------------------------------------------------ anexo de código ----
    "apendice_fontes": {
        "ativo": False,
        "titulo": "Código-fonte do projeto modelo",
        "introducao": "",
        "padroes": [],
        "ignorar": ["**/node_modules/**", "**/.git/**", "**/*.png", "**/*.jpg",
                    "**/*.pdf", "**/*.ico", "**/*.lock"],
        "tamanho_maximo": 200000,
    },

    # -------------------------------------------------------- compilar ----
    "motor": "xelatex",
    "passagens": 3,
    # Imagem usada por "--ambiente container". Em null, o md2book constrói
    # uma imagem Debian enxuta com os mesmos pacotes da instalação nativa.
    # Preencha (ex.: "texlive/texlive:latest") para usar uma imagem pronta,
    # útil quando a máquina não alcança os espelhos do Debian.
    "imagem_latex": None,
}


@dataclass
class Config:
    """Configuração resolvida, com a raiz do projeto já absoluta."""

    dados: dict
    caminho: Path = None
    raiz: Path = field(default=None)

    def __post_init__(self):
        base = self.caminho.parent if self.caminho else Path.cwd()
        self.raiz = (base / self.dados.get("raiz", ".")).resolve()

    def __getitem__(self, chave):
        return self.dados[chave]

    def get(self, chave, padrao=None):
        return self.dados.get(chave, padrao)

    @property
    def dir_saida(self) -> Path:
        return (self.raiz / self.dados["saida"]).resolve()

    @property
    def dir_tex(self) -> Path:
        return self.dir_saida / "tex"


def _mesclar(base: dict, extra: dict) -> dict:
    """Mescla recursivamente `extra` sobre `base` (dicionários aninhados)."""
    saida = copy.deepcopy(base)
    for chave, valor in extra.items():
        if isinstance(valor, dict) and isinstance(saida.get(chave), dict):
            saida[chave] = _mesclar(saida[chave], valor)
        else:
            saida[chave] = copy.deepcopy(valor)
    return saida


def carregar_config(caminho=None, raiz=None) -> Config:
    """Lê o JSON de configuração (se houver) sobre os valores padrão."""
    if caminho:
        caminho = Path(caminho).resolve()
        if not caminho.is_file():
            raise FileNotFoundError("configuração não encontrada: %s" % caminho)
    else:
        candidato = Path(raiz or ".").resolve() / NOME_PADRAO
        caminho = candidato if candidato.is_file() else None

    dados = CONFIG_PADRAO
    if caminho:
        with open(caminho, encoding="utf-8") as fh:
            dados = _mesclar(dados, json.load(fh))
    else:
        dados = copy.deepcopy(dados)

    if raiz:
        dados["raiz"] = str(Path(raiz).resolve())
        caminho = None
    return Config(dados, caminho)


def escrever_config_exemplo(destino: Path, dados: dict) -> None:
    """Grava um JSON de configuração legível."""
    destino.write_text(
        json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
