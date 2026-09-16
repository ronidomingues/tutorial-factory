# 04 · Arquitetura

Como o framework funciona por dentro, e por que assim. Este documento existe
para que a próxima pessoa a mexer aqui — inclusive você, daqui a um ano — não
precise deduzir as decisões a partir do código.

---

## As quatro peças

```
┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE.md — o preset                                           │
│  Não é código. É a especificação do comportamento do agente:    │
│  as 6 etapas, a persona, a anatomia dos documentos, a régua.    │
└─────────────────────────────────────────────────────────────────┘
                              │ lido pelo agente ao abrir a pasta
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  O agente de IA                                                 │
│  Entrevista, pesquisa, escreve. Não é parte deste repositório:  │
│  é uma ferramenta externa, creditada em cada peça publicada.    │
└─────────────────────────────────────────────────────────────────┘
          │                                    │
          │ testa                              │ publica
          ▼                                    ▼
┌──────────────────────┐          ┌─────────────────────────────┐
│  tools/sandbox.py    │          │  tools/publish-doc.py       │
│  contêiner descartá- │          │  .md → capítulos → LaTeX →  │
│  vel; roda os coman- │          │  PDF → .tex autocontido     │
│  dos do documento    │          └──────────────┬──────────────┘
└──────────────────────┘                         │ usa
                                                 ▼
                              ┌─────────────────────────────────┐
                              │  tools/md2book/  (embarcado)    │
                              │  o conversor Markdown → LaTeX   │
                              └─────────────────────────────────┘
                                                 │ veste
                                                 ▼
                              ┌─────────────────────────────────┐
                              │  tools/course-factory-brand/    │
                              │  o kit de marca — DEPENDÊNCIA   │
                              └─────────────────────────────────┘
```

Só a primeira peça precisa da sua atenção no dia a dia. As outras três existem
para que a primeira possa ser cumprida.

---

## Os dois ponteiros

Duas perguntas descrevem **a máquina**, não o projeto: onde mora a marca e onde
mora a documentação. As duas são respondidas do mesmo jeito — um arquivo de uma
linha, ignorado pelo git.

| Ponteiro | Onde | Responde |
|---|---|---|
| `DOCUMENTATION_PATH` | raiz do repositório | onde a documentação gerada é salva |
| `BRAND_PATH` | `tools/course-factory-brand/` | onde o kit de marca realmente mora |

```bash
echo ~/Documentos/documentacao > DOCUMENTATION_PATH
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
```

Linhas em branco e linhas começadas com `#` são comentário, então o arquivo pode
explicar a si mesmo para quem o abrir daqui a um ano. Caminho relativo resolve
contra a pasta do próprio ponteiro.

### A precedência de `DOCUMENTATION_PATH`

1. `--docs <caminho>` — explícito, uma execução só;
2. `TUTORIAL_FACTORY_DOCS` no ambiente;
3. o ponteiro `DOCUMENTATION_PATH` na raiz;
4. `documentation/`, ao lado do repositório — o padrão;
5. `documentacao/`, quando é essa a pasta que existe.

`python3 tools/publish-doc.py --doctor | grep Docs` diz qual venceu, entre
parênteses.

**Nada disso cria a pasta.** Decidir onde a documentação vai é uma coisa;
criá-la é trabalho de quem escreve. O `new-doc.py` cria; os outros só leem.

### Por que um arquivo, e não uma variável de ambiente

Uma variável precisa estar definida em todo shell — inclusive no que o agente
abre, que raramente é o mesmo onde alguém exportou alguma coisa. Um arquivo é
lembrado pela máquina, não pela pessoa. É a mesma razão nos dois casos, e a
consequência de errar é diferente: com `DOCUMENTATION_PATH` errado o material
aparece no lugar errado; com `BRAND_PATH` errado ele sai **assinado por ninguém**,
e ninguém percebe.

---

## O formato de saída

```
documentation/<software>/
├── installation_AAAA-MM-DD.md      ← FONTE DA VERDADE
├── installation_AAAA-MM-DD.tex     ← gerado, autocontido
├── installation_AAAA-MM-DD.pdf     ← gerado
├── manual_AAAA-MM-DD.md            ← FONTE DA VERDADE
├── manual_AAAA-MM-DD.tex           ← gerado
├── manual_AAAA-MM-DD.pdf           ← gerado
├── LEIA-ME.md                      ← gerado
└── tema/                           ← gerado
    ├── coursebook.sty
    ├── brand-env.tex
    ├── assets/*.pdf
    └── fontes/                     (só quando as fontes viajam)
```

### Por que a data está no nome

Documentação técnica envelhece. Quem abre o arquivo daqui a dois anos precisa
saber, antes da primeira linha, contra qual realidade ele foi escrito. E, como o
nome ordena sozinho em ISO, a edição mais recente é sempre a última da lista.

Uma versão nova do software é uma **edição nova**, com data nova. A antiga fica
onde está: ela continua sendo verdade sobre o dia em que foi escrita.
Sobrescrevê-la apagaria a única informação que a datava. Só correção de erro
altera um arquivo existente.

### A regra que não se negocia

> O `publish-doc.py` **nunca apaga nem reescreve** o Markdown do documento.
> Ele só cria e atualiza o `.tex`, o `.pdf`, o `LEIA-ME.md` e o `tema/`.

O `.md` é a fonte; os outros dois formatos derivam dele. Editar o `.tex` à mão
funciona até a próxima publicação; editar o `.md` e republicar funciona sempre.

---

## A divisão em capítulos

Aqui está a única transformação não óbvia do pipeline, e vale entender por quê.

**O problema.** O pedido fixou um arquivo por documento — e um arquivo único é o
que se envia por e-mail e se abre em qualquer editor. Mas um livro precisa de
capítulos: sumário que alcance, quebra de página, cabeçalho corrido. Um `.md`
inteiro vira **um** capítulo, e um sumário de uma linha só não serve para nada.

**A solução.** O publicador reconcilia os dois, mecanicamente:

| No `.md` | No livro |
|---|---|
| `#` (o primeiro, e só ele) | o **título** do documento — capa e propriedades do PDF |
| o texto entre o `#` e o primeiro `##` | um capítulo de **abertura**, sem número |
| `##` | **`\chapter`** |
| `###` | `\section` |
| `####` | `\subsection` |
| `#####` | `\subsubsection` |

Tudo abaixo de `##` sobe um nível, de modo que a hierarquia **dentro** do
capítulo fica exatamente como foi escrita. Nada é perdido, nada é resumido: o
`.md`, o `.tex` e o `.pdf` dizem a mesma coisa.

Detalhes que importam na prática:

- **Cerca de código nunca é lida como título.** Um `##` dentro de um bloco
  ```` ```bash ```` continua sendo um comentário de shell.
- **Uma cerca vale com até três espaços de recuo** (a regra do CommonMark). Com
  quatro, é bloco de código indentado. Aceitar qualquer recuo faria uma crase
  tripla escrita dentro de um comentário abrir uma cerca que nunca fecha — e
  engolir o resto do documento.
- **Comentários `<!-- ... -->` são removidos** antes da conversão, fora de blocos
  de código. Eles são instrução para quem edita o arquivo, não texto para quem lê
  o PDF.
- **Documento sem nenhum `##`** vira um capítulo único, com o título do
  documento. Não quebra; só fica com um sumário curto.
- **O sumário vai até a profundidade 2** — capítulo e seção. Um manual é
  consultado, não lido em ordem: o índice precisa alcançar a seção que responde a
  pergunta, não só o capítulo que a contém.

Os arquivos de capítulo são escritos em uma pasta de rascunho
(`<software>/.build/`), consumidos pelo md2book, e apagados no fim. `--keep-build`
os mantém, junto com o log do LaTeX, quando algo dá errado.

---

## O `.tex` autocontido

Um `.tex` que só compila dentro de uma pasta de trabalho não é uma entrega — é um
subproduto. O publicador transforma o `main.tex` + `tex/*.tex` do md2book em **um
arquivo só**:

1. cada `\input{tex/...}` é substituído pelo conteúdo do capítulo;
2. logo abaixo do `\documentclass`, entra:
   ```latex
   \makeatletter
   \def\input@path{{tema/}{./}}
   \makeatother
   ```
   É o que faz o `\usepackage{coursebook}` e o `\InputIfFileExists{brand-env.tex}`
   — que está dentro do `.sty` — encontrarem o tema na subpasta, sem variável de
   ambiente e sem `TEXINPUTS`;
3. os caminhos que apontavam para o tema a partir da pasta de rascunho são
   reescritos para `tema/`.

O resultado compila com um comando, na própria pasta:

```bash
cd documentation/docker && xelatex installation_2026-09-16.tex
```

Duas ou três vezes — o sumário só fecha da segunda passagem em diante. Sem o kit
de marca, sem esta fábrica, sem rede.

O publicador também remove `.aux`, `.log` e companhia **do próprio documento**
depois de publicar: uma pasta feita para ser compactada e enviada não deve levar
entulho de compilação.

---

## Os dados da marca, e onde cada metade mora

Duas peças compartilham uma pasta, e isso decide como a identidade é escrita:

| Arquivo | Contém | Por quê |
|---|---|---|
| `tema/brand-env.tex` | **a metade da marca**: nome, tagline, dono, contato, cores | é igual para os dois documentos da pasta; o `.sty` o lê sozinho |
| o preâmbulo de cada `.tex` | **a metade do documento**: título, peça, datas, versão, agente, extensão | é diferente em cada um; um arquivo compartilhado que dissesse "o título" estaria certo para um e errado para o outro |

As macros do documento são emitidas depois do `\usepackage{coursebook}`, com um
`\providecommand` antes de cada uma: um kit que não conheça um campo simplesmente
o ignora, em vez de derrubar a compilação ou vazar o valor como texto no meio da
página.

---

## O sandbox

```
documento.md ──► extrai blocos ```bash ──► roteiro ──► contêiner descartável
                 (```console é saída,      com marcas    (--rm, sem rede por
                  não entrada)             por passo      padrão)
                                                │
                                                ▼
                                    transcrição: comando,
                                    código de saída, saída real
```

Decisões que valem registrar:

- **`--rm` sempre.** O próximo teste começa do mesmo estado limpo da máquina do
  leitor. Um contêiner reaproveitado mente: o passo 5 passa porque o passo 2 de
  uma execução anterior deixou algo lá.
- **Sem rede por padrão.** Quem testa uma verificação (`--version`, `lsb_release`)
  não precisa de rede, e o teste isolado é mais fiel. Instalar exige `--network`,
  explicitamente.
- **`exec 2>&1` dentro do contêiner.** A mensagem de erro é a saída mais valiosa
  que um passo produz, e ela chega por `stderr` — um fluxo separado, devolvido
  sem intercalação e portanto impossível de atribuir a um passo. Dobrá-lo no
  `stdout` **dentro** do contêiner é o que mantém `command not found` ao lado do
  comando que não foi encontrado.
- **Um atalho para o `sudo`.** A imagem-base roda como root e não traz `sudo`, de
  modo que todo `sudo apt install` de um tutorial honesto falharia por um motivo
  que nada tem a ver com o tutorial. Como `sudo cmd` executado pelo root **é**
  `cmd`, um repassador de duas linhas permite testar os comandos exatamente como
  estão escritos — que é a única versão que vale testar. `--no-sudo-shim`
  desliga.
- **bash quando existir, `sh` quando não.** Tutoriais são escritos para bash;
  Alpine não tem bash. O contêiner começa em `/bin/sh` e faz `exec bash -s` se
  houver — o `exec` mantém o `stdin`, então o script é lido pelo shell que
  assumiu.

O que ele **não** faz: não roda privilegiado, não monta nada por padrão, não toca
na rede do host além do que o contêiner precisa. E não testa o que não é Linux —
ver [`07-pesquisa-e-verificacao.md`](07-pesquisa-e-verificacao.md).

---

## Por que o md2book é embarcado

`tools/md2book/` é uma cópia fiel do repositório upstream, sem patch local. Duas
consequências, ambas desejadas:

- **numa máquina com Python e LaTeX, um `git clone` publica.** Não há
  `pip install`, não há Pandoc, não há dependência de rede;
- **a cópia se atualiza do upstream sem conflito**, porque nada foi alterado:
  ```bash
  python3 tools/sync-brand.py --md2book ~/md2book
  ```

Os valores padrão do md2book citam a marca do autor original. Eles nunca entram
em jogo: o `publish-doc.py` monta a configuração inteira a partir do
`book.base.json` do kit instalado, e sobrescreve tudo o que é estrutural.

Esta fábrica usa apenas o caminho **livro** do md2book. O gerador de slides viaja
junto por ser parte do pacote, não por ser usado aqui.

---

## O que é versionado e o que não é

| Caminho | Versionado? | Por quê |
|---|---|---|
| `CLAUDE.md`, `docs/`, `tools/*.py` | **sim** | é a ferramenta |
| `tools/md2book/` | **sim** | embarcado, para o clone publicar sozinho |
| `tools/course-factory-brand/template/` | **sim** | o pré-molde neutro |
| `tools/course-factory-brand/` (o resto) | **não** | o kit instalado é de quem o instalou, e pode ser privado |
| `tools/course-factory-brand/BRAND_PATH` | **não** | descreve a máquina |
| `documentation/` | **não** | o material é de quem o gerou; são dezenas de MB por software |
| `DOCUMENTATION_PATH` | **não** | descreve a máquina |
| `INDEX.md` | **sim** | é o catálogo público do que foi produzido |

O `INDEX.md` é versionado justamente porque `documentation/` não é: ele é o único
registro que sobrevive ao clone de outra pessoa. Por isso ele **não leva link
para dentro da pasta** — um link que morre no clone alheio é pior que nenhum.

---

## O crédito ao agente

Toda peça publicada nomeia o agente de IA que a escreveu, e a versão do modelo
(`--ai-model`). Não é enfeite nem cautela jurídica: **quem lê tem o direito de
saber como o material foi produzido.** Um manual de 80 páginas pesquisado e
redigido por um modelo de linguagem, orientado por uma pessoa, não é a mesma
coisa que um manual escrito à mão — e esconder isso é desonesto com o leitor.

A divisão de responsabilidade impressa é esta:

| Papel | O que fez |
|---|---|
| **Autor e orientador** (`BRAND_OWNER`) | definiu escopo, profundidade e padrão de qualidade, e **responde pelo resultado** |
| **Agente de IA** (`--agent`, `--ai-model`) | entrevistou, pesquisou, testou, redigiu e gerou os PDFs |

---

## Relação com a Course Factory

Mesma arquitetura, mesmo conversor, **mesmo contrato de kit de marca**. O que
muda é o produto:

| | Course Factory | Tutorial Factory |
|---|---|---|
| Entrada | um **assunto** ("álgebra linear") | um **software** ("Docker") |
| Entrevista | não — o assunto basta | **sim, sempre** — SO, versão, arquitetura, objetivo |
| Teste | não se aplica | **obrigatório**, em contêiner |
| Saída | pasta de curso + livro + slides | dois documentos × três formatos |
| Profundidade | do zero ao nível de pesquisa | do zero ao uso profissional |

As duas convivem na mesma máquina, com o mesmo `BRAND_PATH`. Assunto vai para
lá; ferramenta fica aqui.
