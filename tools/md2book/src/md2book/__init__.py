"""
md2book — converte uma pasta de arquivos Markdown num livro em LaTeX/PDF.

Escrito para cursos escritos em Markdown: descobre os arquivos, converte cada um
num capítulo `.tex`, monta o `main.tex` e compila com XeLaTeX.

Sem dependências externas: apenas a biblioteca padrão do Python (3.9+).
Exige XeLaTeX instalado no sistema para chegar ao PDF.
"""

# Mantenha em sincronia com a versão declarada no pyproject.toml.
__version__ = "1.1.0"

from .config import Config, carregar_config, CONFIG_PADRAO  # noqa: F401

__all__ = ["Config", "carregar_config", "CONFIG_PADRAO", "__version__"]
