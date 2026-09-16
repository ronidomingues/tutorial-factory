# Pré-molde de marca — Course Factory

Este é o **kit de marca de fábrica**: uma identidade neutra, em tecnologia,
ciência e conhecimento, que existe por dois motivos.

1. **Um clone novo publica um PDF de verdade no primeiro dia.** Sem isto, a
   fábrica não teria com o que assinar nada e o primeiro contato seria um erro.
2. **Ele é o molde do contrato.** Cada arquivo aqui mostra a forma que o
   arquivo equivalente do seu kit precisa ter.

> **Não publique material que circula com esta identidade.** Ela não é de
> ninguém — é um molde. Troque-a pela sua antes de qualquer coisa sair da sua
> máquina.

---

## Tornar isto a sua marca

```bash
python3 tools/sync-brand.py --from-template
```

Copia este conteúdo para a raiz do slot (`tools/course-factory-brand/`), que é
ignorado pelo git da fábrica. A partir daí é seu. Troque, nesta ordem:

| Passo | Arquivo | O que mudar |
|---|---|---|
| 1 | **`brand.env`** | nome, tagline, autor/orientador, contato **e todas as cores** |
| 2 | `logo/*.svg` → `assets/*.pdf` | o seu símbolo (`inkscape --export-type=pdf ...`) |
| 3 | `BRAND-MANUAL.md` | o manual da **sua** marca |
| 4 | `EDITORIAL-STANDARD.md` | o que o seu livro e o seu slide podem fazer |

Depois:

```bash
python3 tools/sync-brand.py --palette    # regera palette/ a partir do brand.env
python3 tools/sync-brand.py --colors     # confere quem está vencendo
python3 tools/sync-brand.py --check
python3 tools/publish-course.py <assunto>   # e olhe o PDF
```

**Recolorir não exige tocar nos `.sty`.** Cada `BRAND_COLOR_*` do `brand.env`
vira um `\definecolor` que sobrescreve o padrão do estilo. Os dois `.sty` só
mudam quando você quiser mexer na **estrutura** das páginas — capa, créditos,
colofão — e não na cor delas.

Os `md2book/*.base.json` também só mudam por estrutura: tipografia, divisão de
partes, tamanho do código. As cores deles vêm do `brand.env`.

Guarde o resultado **no seu próprio repositório** — privado, se a marca for.
O contrato inteiro está em [`docs/03-brand-kit.md`](../../../docs/03-brand-kit.md).

---

## O que tem aqui

```
template/
├── brand.env                         dados impressos na capa e nos créditos
├── BRAND-MANUAL.md                   a identidade: símbolo, cor, tipo, tom
├── EDITORIAL-STANDARD.md             o que livro e slide podem e não podem
├── latex/
│   ├── coursebook.sty                capa, créditos, rodapé e colofão do livro
│   └── beamerthemecourseslides.sty   capa, transição, rodapé e fecho da aula
├── md2book/
│   ├── book.base.json                estilo-base do livro
│   └── slides.base.json              estilo-base das aulas
├── assets/*.pdf                      o símbolo, para o LaTeX
├── logo/*.svg                        o símbolo, vetorial, para editar
└── palette/                          tokens de cor — GERADOS do brand.env
```

Não há `fonts/`: o molde usa a família **Latin Modern**, que acompanha qualquer
TeX Live. Nenhum arquivo de fonte é distribuído, e não há licença a repassar.

---

## Uma decisão de projeto que vale copiar

O símbolo **não tem o nome da marca dentro dele**. A assinatura é composta em
tempo de compilação: símbolo + `BRAND_NAME_LOWER` em tipo.

Trocar o nome no `brand.env` troca a assinatura em toda capa, todo rodapé e
todo fecho de aula — sem redesenhar nada. Se o seu logotipo já traz o nome
embutido, isso se perde; pese antes de decidir.
