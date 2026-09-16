<!-- markdownlint-disable MD033 -->
# Manual da Marca — Course Factory (pré-molde)

> **Este é um molde, não uma marca.** Ele existe para que um clone novo do
> repositório publique um PDF de verdade no primeiro dia, e para mostrar a
> forma que um manual de marca precisa ter para servir de kit de publicação.
> **Substitua-o pelo manual da sua marca** antes de publicar qualquer coisa
> que circule com o seu nome.
>
> Como substituir: [`docs/03-brand-kit.md`](../../../docs/03-brand-kit.md).

Versão 1.0 · 16/09/2026

---

## 1. A marca em uma frase

**Course Factory** é a identidade neutra da fábrica: uma marca de
**tecnologia, ciência e conhecimento** — não de uma empresa, não de uma pessoa.

Direção criativa: **laboratório**. Fundo de tinta escura, geometria exata,
azul como cor que conduz. Nada decorativo: cada elemento ou informa, ou sai.

---

## 2. O símbolo

Um **hexágono** com **três nós ligados** dentro.

| Elemento | O que significa |
|---|---|
| Hexágono | ciência — a forma que a natureza repete, da colmeia ao benzeno |
| Três nós ligados | conhecimento em rede — nada se aprende isolado |
| Nó âmbar no topo | o ponto de partida: a pergunta que abre o assunto |

O símbolo **não carrega o nome dentro dele**. A assinatura é composta em tempo
de compilação: símbolo + `BRAND_NAME_LOWER` em tipo. Trocar o nome da marca no
`brand.env` troca a assinatura inteira, sem redesenhar nada — é para isso que
um pré-molde serve.

### 2.1 Arquivos

| Arquivo | Onde usar |
|---|---|
| `logo/symbol-color.svg` · `assets/symbol-color.pdf` | fundo claro |
| `logo/symbol-color-on-dark.svg` · `assets/symbol-color-on-dark.pdf` | fundo escuro |
| `logo/symbol-mono-light.svg` · `assets/symbol-mono-light.pdf` | uma cor, sobre escuro |
| `logo/symbol-mono-dark.svg` · `assets/symbol-mono-dark.pdf` | uma cor, sobre claro |

O LaTeX lê os `.pdf`; os `.svg` são a fonte. Regerou o SVG? Converta:

```bash
inkscape --export-type=pdf --export-filename=assets/symbol-color.pdf logo/symbol-color.svg
```

### 2.2 Área de proteção e tamanho mínimo

- **Área de proteção:** metade da altura do símbolo, em todos os lados.
- **Tamanho mínimo:** 7 mm de altura em impresso, 24 px em tela.
- Abaixo disso os três nós viram uma mancha — use a versão mono.

### 2.3 Usos proibidos

Não esticar, não rotacionar, não trocar as cores dos nós, não colocar sobre
fundo de contraste insuficiente, não aplicar sombra, não redesenhar "parecido".

---

## 3. Cores

### 3.1 Paleta

**A fonte dos valores é o [`brand.env`](brand.env)**, no bloco `BRAND_COLOR_*`.
É de lá que cada cor chega ao LaTeX e ao conversor, e é o único lugar a editar
para recolorir a marca inteira.

`palette/tokens.json` e `palette/tokens.css` são **gerados** dali
(`python3 tools/sync-brand.py --palette`) e existem para quem consome a
identidade fora do LaTeX. Não os edite à mão.

| Papel | Token | Hex | Onde |
|---|---|---|---|
| Tinta | `ink` | `#101620` | fundo de capa e de slide; texto sobre papel |
| Painel | `panel` | `#19202B` | superfície elevada no escuro |
| Contorno | `border` | `#2A3442` | borda de bloco e de código no escuro |
| **Azul** | `blue` | `#3B82F6` | **cor condutora** — filetes, marcadores, números |
| Azul profundo | `blueDeep` | `#1D4ED8` | o azul que passa em contraste sobre papel |
| Turquesa | `teal` | `#14B8A6` | segunda voz: subitens, diagramas |
| Âmbar | `amber` | `#F0B429` | **um destaque por tela**, nunca dois |
| Papel | `paper` | `#F6F7F9` | miolo impresso |
| Apoio | `muted` / `support` | `#8A94A6` / `#5A6472` | texto secundário, escuro / claro |

O nome da esquerda é o sufixo: `BRAND_COLOR_cfBlue`, `BRAND_COLOR_cfInk`.

### 3.2 A regra do um

Uma tela tem **uma** coisa em âmbar. Se duas coisas são o destaque, nenhuma é.
O azul pode se repetir — ele é estrutura, não ênfase.

### 3.3 Contraste — regra inegociável

- Texto normal: **mínimo 4.5:1**. Texto grande (≥ 24 px / 18 pt): **3:1**.
- `blue` sobre `paper` **não passa** — sobre papel use `blueDeep`.
- `amber` nunca é cor de texto corrido em nenhum fundo: é preenchimento, filete
  ou uma palavra em negrito.

---

## 4. Tipografia

O pré-molde **não distribui arquivo de fonte**. Ele usa a família **Latin
Modern**, que acompanha qualquer instalação de TeX Live — não há o que instalar
e não há licença a repassar.

| Papel | Família | Onde |
|---|---|---|
| Texto corrido | Latin Modern Roman | miolo do livro, corpo do slide |
| Títulos | Latin Modern Sans | capa, títulos de capítulo, frametitle |
| Código e rótulos | Latin Modern Mono | blocos de código, metadados, números |
| Símbolos | DejaVu Sans | setas, caixas de seleção, sinais fora do latino |

> **Se a sua marca tem tipografia própria**, declare-a em `fonts/fonts.json` e
> ponha os arquivos em `fonts/`. Só distribua fonte cuja licença permita —
> SIL OFL permite, a maioria das comerciais não. Ver
> [`docs/03-brand-kit.md`](../../../docs/03-brand-kit.md).

### 4.1 Regras de composição

- Rótulo em caixa alta é sempre mono, sempre pequeno, sempre em cor de apoio.
- Título nunca passa de três linhas na capa.
- Número vem com unidade e com data. `11.886 páginas (16/09/2026)`, não "muitas".

---

## 5. Tom de voz

Direto, denso, honesto. Quem lê é adulto e tem pressa.

**Como escrever:** afirmação antes de justificativa · sujeito explícito · número
com unidade e data · opinião marcada como opinião.

**Palavras banidas:** "solução inovadora", "revolucionário", "simplesmente",
"basicamente", "como todos sabem", "é fácil" (para quem?).

**O teste da frase:** se a frase continua verdadeira tirando os adjetivos, os
adjetivos sobravam.

---

## 6. Governança

Este manual governa **o molde**. A marca que você instalar por cima governa o
seu material — e o `LEIA-ME.md` do slot diz que o molde nunca é a assinatura
final de nada que circule.

| Mudou | Faça |
|---|---|
| Uma cor no `brand.env` | `--palette`, depois republique todos os cursos |
| Tipografia ou logo | republique todos os cursos |
| A estrutura de uma página (`.sty`) | republique todos os cursos |
| Só o texto deste manual | nada |

### Changelog

- **1.0** — 16/09/2026 — primeira versão do pré-molde neutro.
