"""Programa de exemplo do curso: lê uma configuração e soma os valores."""

import sys


def ler_config(caminho):
    """Lê um YAML mínimo (chave: valor) sem depender de biblioteca externa."""
    dados = {}
    with open(caminho, encoding="utf-8") as fh:
        for linha in fh:
            linha = linha.split("#", 1)[0].strip()
            if not linha or ":" not in linha:
                continue
            chave, valor = linha.split(":", 1)
            dados[chave.strip()] = valor.strip()
    return dados


def main(argv):
    if len(argv) != 2:
        print("uso: python3 app.py config.yaml", file=sys.stderr)
        return 2
    config = ler_config(argv[1])
    valores = [int(v) for v in config.values() if v.lstrip("-").isdigit()]
    print("valores encontrados: %s" % valores)
    print("soma: %d" % sum(valores))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
