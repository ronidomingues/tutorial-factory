# Componentes de terceiros

O que este repositório distribui e não é de autoria própria, com a licença de
cada item. Conferido em **16/09/2026**.

---

## Software

| Componente | Onde | Licença | Titular |
|---|---|---|---|
| **md2book** | `tools/md2book/` | MIT | Ronivaldo D. Andrade — repositório próprio: <https://github.com/ronidomingues/md2book> |

`md2book` é cópia embarcada (*vendored*) do repositório acima: a fábrica
funciona sem instalar nada além do LaTeX. A cópia traz o `LICENSE` original em
`tools/md2book/LICENSE` e é atualizada com
`python3 tools/sync-brand.py --md2book <caminho-do-checkout>`.

A cópia é **fiel ao upstream, sem patch local** — inclusive nos valores padrão,
que citam a marca do autor (por exemplo, `"tema": "andradasdev"` como default
de slides em `src/md2book/slides.py`). Esses padrões nunca entram em jogo aqui:
o `publish-doc.py` monta a configuração inteira a partir do `book.base.json` do
kit de marca instalado. Manter a cópia sem alterações é o que permite
atualizá-la do upstream sem conflito.

Esta fábrica usa apenas o caminho **livro** do md2book. O gerador de slides
viaja junto por ser parte do pacote, não por ser usado aqui.

---

## Tipografia

**Este repositório não distribui arquivo de fonte.**

O pré-molde de marca (`tools/course-factory-brand/template/`) usa a família
**Latin Modern**, que acompanha qualquer instalação de TeX Live (GUST Font
License, livre e aprovada, equivalente à OFL), e **DejaVu Sans** para símbolos,
presente na maioria dos sistemas. Nenhuma das duas é copiada para cá — elas já
estão na máquina de quem compila.

Um kit de marca instalado no slot **pode** distribuir tipografia própria. Se o
fizer, a licença é responsabilidade de quem monta o kit. Regra prática:

| Licença da fonte | Pode redistribuir no kit? |
|---|---|
| SIL Open Font License 1.1 (Inter, JetBrains Mono, a maioria das do Google Fonts) | **Sim** — mantendo o arquivo de licença junto |
| Apache 2.0 | **Sim** — mantendo o aviso |
| GUST Font License (Latin Modern, TeX Gyre) | **Sim** |
| Comercial / EULA de foundry | **Quase sempre não** — leia o contrato |

Ver [`docs/03-kit-de-marca.md`](docs/03-kit-de-marca.md), seção "Tipografia".

---

## LaTeX

A compilação depende de pacotes distribuídos com o TeX Live — `graphicx`,
`xcolor`, `fontspec`, `polyglossia`, `fancyhdr`, `eso-pic`, `etoolbox`,
`needspace`, `tcolorbox`, `fvextra`, `hyperref`, entre outros. Não são
redistribuídos aqui; vêm da instalação do TeX Live, cada um sob a sua própria
licença (LPPL, na maioria).

---

## Imagens de contêiner

O `tools/sandbox.py` **não distribui imagem nenhuma**. Ele executa imagens que
o motor de contêiner da máquina baixa dos respectivos registries no momento do
teste — `ubuntu`, `debian`, `fedora`, `alpine` e as demais listadas em
`--list`. Cada imagem é do seu mantenedor e segue a licença dele. Nada é
armazenado neste repositório.

---

## Software documentado

A documentação produzida com esta fábrica descreve software de terceiros. Os
manuais gerados **não são documentação oficial** dos projetos descritos, não
são endossados por eles, e não concedem direito nenhum sobre eles. Nomes,
marcas e logotipos citados pertencem aos respectivos titulares e aparecem
apenas para identificar o software de que o documento trata.

---

## Agente de IA

A documentação produzida com esta fábrica é pesquisada, testada e redigida por
um agente de inteligência artificial — por padrão **Claude Code (Anthropic)**.
O agente não é um componente deste repositório: é uma ferramenta externa, usada
por quem executa a fábrica, sob os termos do respectivo fornecedor.

O crédito ao agente é impresso em toda peça publicada, por decisão editorial.
Ver [`docs/04-arquitetura.md`](docs/04-arquitetura.md).
