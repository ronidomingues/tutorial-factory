# `tools/` — o motor

Cinco programas em Python, um conversor embarcado e um slot de dependência.
Nenhum `pip install`: numa máquina com Python 3 e LaTeX, um `git clone` publica.

A referência de uso está em [`../docs/05-referencia-cli.md`](../docs/05-referencia-cli.md).
Este arquivo explica **como as peças se encaixam** e o que cada uma pode ou não
pode tocar.

---

## O mapa

```
tools/
├── common.py                 onde moram a marca, as fontes e o destino
│
├── new-doc.py                abre a pasta do software e semeia os esqueletos
├── sandbox.py                roda os comandos documentados em contêiner
├── publish-doc.py            .md → capítulos → LaTeX → PDF → .tex autocontido
├── publish-all.py            manutenção em lote, e --check
├── sync-brand.py             instala e confere o kit de marca
│
├── example/                  os gabaritos — o contrato de formato
│   ├── installation-modelo.md
│   └── manual-modelo.md
│
├── md2book/                  o conversor Markdown → LaTeX → PDF (MIT, embarcado)
└── course-factory-brand/     O SLOT DE MARCA
    ├── BRAND_PATH            (não versionado) onde o kit realmente mora
    └── template/             o pré-molde neutro, versionado
```

---

## A ordem em que se usam

```
new-doc.py      →  escrever  →  sandbox.py  →  publish-doc.py  →  INDEX.md
(abre a pasta)     (o .md)      (testa)        (os 3 formatos)    (catálogo)
```

`publish-all.py` e `sync-brand.py` ficam fora dessa linha: são manutenção.

---

## `common.py` — o que os outros compartilham

Não é executável. Resolve três perguntas, e só elas:

| Pergunta | Função |
|---|---|
| Onde está o kit de marca? | `find_brand()` — cinco origens, em ordem de precedência |
| Onde a documentação é salva? | `docs_root()` — cinco origens, mesma ideia |
| Como se chama o md2book aqui? | `find_md2book()` — a cópia embarcada primeiro |

Também guarda `PIECES`, o dicionário que define as duas peças
(`installation` e `manual`), seus prefixos de arquivo e o rótulo impresso na
capa. **Acrescentar uma terceira peça começa por lá** — mas pense duas vezes:
dois documentos por software foi uma decisão de projeto, não um acaso.

---

## Quem pode escrever onde

A regra que mantém a fábrica segura de si mesma:

| Programa | Escreve em | **Nunca** toca em |
|---|---|---|
| `new-doc.py` | `<docs>/<software>/*.md`, só se não existirem | nada mais |
| `sandbox.py` | o `--report`, quando pedido | a documentação, o repositório, o host |
| `publish-doc.py` | `.tex`, `.pdf`, `LEIA-ME.md`, `tema/`, `.build/` | **o `.md` do documento** |
| `publish-all.py` | `.publicacao.json`, e o que o `publish-doc.py` escreve | idem |
| `sync-brand.py` | o slot, e `palette/` do kit | a origem de um `--install`; documentação publicada |

> **A regra que não se negocia.** O Markdown do documento é a fonte da verdade.
> Nenhum programa daqui o apaga, move ou reescreve.

---

## `example/` — os gabaritos

`installation-modelo.md` e `manual-modelo.md` não são enfeite: são **o contrato de
formato**. Eles definem a gramática que o `publish-doc.py` entende e a anatomia
que o `CLAUDE.md` exige. O `new-doc.py` os copia, trocando `{{SOFTWARE}}` pelo
nome dado.

São feitos para ser **sobrescritos linha a linha**, não preenchidos educadamente
em volta. Os textos entre `{{chaves duplas}}` e o comentário do topo saem antes
de publicar — e o comentário, se ficar, não chega ao PDF: comentários HTML fora
de blocos de código são removidos na conversão.

Mudou a anatomia no `CLAUDE.md`? **Mude os gabaritos junto.** Os dois são a mesma
especificação, escrita duas vezes: uma para o agente ler, outra para o autor ver.

---

## `md2book/` — embarcado, e sem patch

Cópia fiel do repositório upstream. Duas consequências, ambas desejadas:

- **um `git clone` publica**, sem instalar nada;
- **a cópia se atualiza sem conflito**, porque nada foi alterado:

```bash
python3 tools/sync-brand.py --md2book ~/md2book
```

Os valores padrão do md2book citam a marca do autor original. Eles nunca entram
em jogo: o `publish-doc.py` monta a configuração inteira a partir do
`book.base.json` do kit instalado e sobrescreve tudo o que é estrutural.

Esta fábrica usa apenas o caminho **livro**. O gerador de slides viaja junto por
ser parte do pacote, não por ser usado aqui.

---

## `course-factory-brand/` — o slot

É uma **dependência**, não uma parte da ferramenta. O nome é o da Course Factory
de propósito: o contrato é o mesmo, e um único repositório de marca assina o que
as duas fábricas publicam.

Do conteúdo do slot, o git versiona **só** o `template/`. O kit instalado e o
`BRAND_PATH` ficam de fora — um kit privado convive aqui sem risco de subir
junto.

Contrato completo: [`../docs/03-kit-de-marca.md`](../docs/03-kit-de-marca.md).

---

## Estilo do código

Para quem for mexer:

- **Python 3.8+, biblioteca padrão apenas.** Uma dependência nova é uma máquina a
  menos onde a fábrica roda sozinha.
- **Comentário explica *por quê*, não *o quê*.** O código já diz o que faz.
- **Mensagem de erro diz o que fazer.** Toda saída de erro nomeia o arquivo, o
  caminho esperado e o comando que corrige.
- **Nomes de domínio em português, nomes de programa em inglês.** `publicar_peca`
  lida com uma *peça*, que é vocabulário desta fábrica; `main` é `main`.
- **Nada escreve no `.md` do documento.** Se uma função nova precisar disso, a
  função está errada.
