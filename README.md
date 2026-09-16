<!-- markdownlint-disable MD033 -->
# Tutorial Factory

**Você escreve "como instalar Docker". O agente entrevista, pesquisa, testa os
comandos em um contêiner de verdade e entrega dois livros — instalação e uso —
em Markdown, LaTeX e PDF, com a sua marca.**

Este repositório não é um projeto de software comum: é uma **linha de produção
de documentação técnica operada por um agente de IA**. Um preset de
comportamento ([`CLAUDE.md`](CLAUDE.md)) diz ao agente o que perguntar, o que
pesquisar, o que testar e o que escrever; um conversor embarcado transforma o
Markdown em livro, em LaTeX e PDF; e um **kit de marca plugável** decide como
isso se parece.

> <sup>**In English** — Tutorial Factory turns a request like "how do I install
> Docker" into two book-grade documents written by an AI agent: a field-manual
> installation guide and a K&R-style usage manual with a complete worked
> project. The agent interviews first, researches official sources, and runs the
> documented commands in a throwaway container before publishing — Markdown,
> LaTeX and print-ready PDF. The brand identity is a swappable dependency, so
> the output carries *your* identity, not the tool's. MIT licensed. Docs are in
> Brazilian Portuguese, because the tutorials are.</sup>

<p align="center">
  <a href="docs/01-instalacao.md">Instalação</a> ·
  <a href="docs/02-primeiro-tutorial.md">Primeiro tutorial</a> ·
  <a href="docs/03-kit-de-marca.md">Kit de marca</a> ·
  <a href="docs/04-arquitetura.md">Arquitetura</a> ·
  <a href="docs/05-referencia-cli.md">CLI</a> ·
  <a href="INDEX.md">Catálogo</a>
</p>

---

## O problema que isto resolve

Pergunte a um assistente como instalar qualquer coisa e você recebe um bloco de
comandos plausível. Plausível é a palavra: ele foi escrito de memória, para um
sistema operacional que ninguém perguntou qual era, em uma versão que talvez já
não exista, e **nunca foi executado**. Quando falha, falha no meio — depois que
você já mexeu na máquina.

Esta fábrica troca as quatro coisas que dão errado:

| O que costuma acontecer | O que acontece aqui |
|---|---|
| Responde sem perguntar o ambiente | **Entrevista primeiro**: SO, versão, arquitetura, objetivo, permissões, proxy |
| Escreve de memória | **Pesquisa a fonte primária**: documentação oficial, repositório, releases, o pacote que a distro entrega hoje |
| Nunca roda o que manda rodar | **Executa os comandos** em contêiner descartável e usa a saída real |
| Entrega um bloco de texto no chat | **Entrega dois livros**, em `.md`, `.tex` e `.pdf`, com capa, sumário e marca |

E diz o que não conseguiu testar, nominalmente, em vez de deixar implícito que
testou.

---

## Como funciona

Quatro peças, e só a primeira precisa da sua atenção.

```
        você digita "como instalar Docker"
                  │
                  ▼
   ┌──────────────────────────────┐
   │  CLAUDE.md — o preset        │  entrevistar → pesquisar → testar →
   │  (as 6 etapas, a régua)      │  escrever → publicar
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │  Agente de IA                │  pergunta o ambiente, busca a fonte
   │  (Claude Code, ou outro)     │  oficial, escreve os dois documentos
   └──────────────┬───────────────┘
                  │
                  ├──────────────► tools/sandbox.py
                  │                roda os comandos de verdade,
                  │                em contêiner descartável
                  ▼
   ┌──────────────────────────────┐
   │  documentation/<software>/   │  installation_AAAA-MM-DD.{md,tex,pdf}
   │                              │  manual_AAAA-MM-DD.{md,tex,pdf}
   └──────────────┬───────────────┘
                  ▲
   ┌──────────────┴───────────────┐
   │  tools/course-factory-brand/ │  a identidade aplicada — uma DEPENDÊNCIA,
   │  (kit de marca instalado)    │  não uma parte da ferramenta
   └──────────────────────────────┘
```

O `CLAUDE.md` é lido automaticamente pelo agente ao abrir esta pasta. Ele define
a persona (instrutor de campo + administrador veterano + autor de referência), o
roteiro da entrevista, o protocolo de pesquisa, a obrigação de testar, a
anatomia dos dois documentos e o padrão de publicação. **Mudar o `CLAUDE.md`
muda a fábrica inteira.**

---

## Começar

```bash
git clone <url-deste-repositorio> tutorial-factory && cd tutorial-factory

python3 tools/publish-doc.py --doctor           # esta máquina publica sozinha?
python3 tools/sync-brand.py --from-template     # instala a marca-molde

echo ~/Documentos/documentacao > DOCUMENTATION_PATH   # opcional: onde salvar
```

Abra um agente de programação nesta pasta e peça:

```
como instalar Docker
```

O agente entrevista, pesquisa, testa, escreve `documentation/docker/` e publica.
Ou, se preferir escrever à mão:

```bash
python3 tools/new-doc.py docker            # cria os dois esqueletos, datados
# ... escreva o Markdown ...
python3 tools/sandbox.py --image ubuntu:24.04 --network \
  --from-doc documentation/docker/installation_2026-09-16.md
python3 tools/publish-doc.py docker --ai-model "Claude Opus 5"
```

Passo a passo completo: [`docs/02-primeiro-tutorial.md`](docs/02-primeiro-tutorial.md).

---

## O que sai: anatomia de uma pasta

```
documentation/docker/
├── installation_2026-09-16.md      a fonte da verdade — manual de campo
├── installation_2026-09-16.tex     o mesmo documento, em LaTeX autocontido
├── installation_2026-09-16.pdf     pronto para ler, imprimir ou enviar
├── manual_2026-09-16.md            o livro de uso, estilo K&R
├── manual_2026-09-16.tex
├── manual_2026-09-16.pdf
├── LEIA-ME.md                      o que é cada arquivo e como refazer
└── tema/                           coursebook.sty, brand-env.tex, logos
```

O `.tex` **é autocontido**: todos os capítulos estão nele, e o tema fica ao lado,
em `tema/`. Quem recebe a pasta compila com `xelatex arquivo.tex` e nada mais —
sem o kit de marca, sem esta fábrica, sem internet.

### Manual de instalação — o que ele cobre

Ficha do ambiente testado · declaração de verificação · pré-requisitos com
comando de conferência · remoção de versões antigas · a instalação passo a passo,
**um comando por bloco**, com verificação e saída real · PATH e variáveis ·
permissões · rede corporativa · convivência de versões · atualizar, voltar atrás
e desinstalar por completo · os outros sistemas operacionais em capítulo próprio ·
tabela de erros com a **mensagem literal** · alternativa sem instalar nada ·
checklist de ambiente pronto · fontes com URL e data.

### Manual de uso — o que ele cobre

O que o software é e que problema resolve · o modelo mental · quando **não**
usar · vocabulário · os primeiros cinco minutos · comandos **por tarefa**:
básicos, necessários e os úteis que quase ninguém conhece · referência de opções
marcando o obsoleto · dez ou mais receitas completas · **um projeto inteiro,
construído do zero até rodar**, com tratamento de erro, configuração, log e
teste · armadilhas · diagnóstico com dez erros de uso · para onde ir depois ·
fontes.

---

## Testar é parte do trabalho

```bash
python3 tools/sandbox.py --list          # imagens-base à mão

# roda EXATAMENTE os comandos que o documento manda dar
python3 tools/sandbox.py --image ubuntu:24.04 --network \
  --from-doc documentation/docker/installation_2026-09-16.md \
  --report /tmp/verificacao.md
```

O `--from-doc` extrai os blocos ```` ```bash ```` do documento, na ordem escrita,
e executa cada um em um contêiner descartável, registrando código de saída e
saída real. Blocos ```` ```console ```` são **saída**, não entrada: ele não os
executa.

Um passo que falha é um passo que não pode ser publicado como está.

E o limite, dito na frente: **o que não dá para testar em contêiner não é
testado.** Instalador gráfico, módulo de kernel, caminho exclusivo de macOS ou
Windows, hardware específico. O preset manda **declarar isso no documento**,
nominalmente, em vez de deixar implícito que foi verificado.

---

## A marca é sua, não da ferramenta

`tools/course-factory-brand/` é um **slot de dependência**. Quem publica instala
ali a própria identidade — logotipo, paleta, tipografia, manual, `.sty` — e o
material sai assinado com ela.

```bash
# começar pelo molde neutro que vem no repositório
python3 tools/sync-brand.py --from-template

# ou apontar para a sua, num repositório separado (privado, se a marca for)
git clone git@github.com:voce/sua-marca.git ~/sua-marca
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check
```

O slot mantém o nome `course-factory-brand` de propósito: **o contrato é o mesmo
da [Course Factory](https://github.com/ronidomingues)**, a fábrica irmã que
produz cursos. Um único repositório de marca assina tudo o que o dono publica, e
o mesmo `BRAND_PATH` serve às duas.

Sem um kit que cumpra o contrato, a fábrica **recusa publicar** — nunca sai um
PDF meio-marcado. Trocar a identidade é editar **um arquivo**: nome, tagline,
autor e cores vivem todos no `brand.env` do kit.

O que toda peça publicada traz, qualquer que seja a marca:

| Onde | O que aparece |
|---|---|
| Capa | marca, título, a peça (instalação ou uso), **autor e orientador**, o **agente de IA** que escreveu, nível, versão, datas e extensão |
| Rodapé de toda página | marca e título do documento |
| Colofão | símbolo, marca, tagline e os créditos outra vez |

Contrato completo: [`docs/03-kit-de-marca.md`](docs/03-kit-de-marca.md).

> **Por que creditar a IA.** Quem lê tem o direito de saber como o material foi
> produzido. Um manual de 80 páginas pesquisado e redigido por um modelo de
> linguagem, orientado por uma pessoa, não é a mesma coisa que um manual escrito
> à mão — e esconder isso é desonesto com o leitor. Por isso o crédito traz o
> nome **e a versão** do modelo (`--ai-model`).

---

## As regras que o agente segue

Todas detalhadas no [`CLAUDE.md`](CLAUDE.md).

| Regra | O que significa na prática |
|---|---|
| **Entrevista antes de escrever** | SO, versão, arquitetura, objetivo, permissões e proxy. "Como instalar X" tem doze respostas certas e onze estão erradas para quem perguntou. |
| **Fonte primária, sempre** | Documentação oficial, repositório, releases e o pacote que a distro entrega hoje. Blog de 2021 é história, não instrução. |
| **Executar o que se manda executar** | Contêiner descartável, saída real, código de saída registrado. |
| **Declarar o não testado** | Nominalmente, no documento, antes dos comandos. |
| **Um comando por bloco** | Quem copia dois comandos juntos não sabe qual falhou. |
| **Verificação a cada passo** | Comando, o que ele faz em uma linha, saída esperada, e o que fazer se vier diferente. |
| **Mensagem de erro literal** | A tabela de problemas traz o texto exato que aparece na tela, não uma paráfrase. |
| **Nada inventado** | Nunca uma versão, flag, URL, ISBN ou saída fabricada. Na dúvida, diz que não encontrou. |
| **Datas absolutas** | "Em 16/09/2026", nunca "recentemente". |
| **Um projeto completo** | O manual de uso constrói uma aplicação inteira, que roda, com erro tratado e teste. |

E o limite, dito na frente: **a fábrica não verifica fato por você.** Ela força o
teste dos comandos e exige a fonte; o julgamento editorial continua sendo de
quem orienta.

---

## Estrutura do repositório

```
tutorial-factory/
├── CLAUDE.md                     O PRESET — as regras que o agente obedece
├── INDEX.md                      catálogo do que foi documentado
├── LICENSE                       MIT, com o escopo explicitado
├── THIRD-PARTY-NOTICES.md        o que é de terceiros, e sob que licença
├── docs/                         a documentação do framework
├── documentation/                o material gerado  (NÃO versionado)
└── tools/                        o motor
    ├── publish-doc.py            um software → .md + .tex + .pdf
    ├── publish-all.py            manutenção em lote, e --check
    ├── new-doc.py                abre a pasta e semeia os esqueletos
    ├── sandbox.py                roda os comandos de verdade, em contêiner
    ├── sync-brand.py             instala e confere o kit de marca
    ├── common.py                 onde moram marca, fontes e destino
    ├── example/                  os gabaritos dos dois documentos
    ├── md2book/                  o conversor Markdown → LaTeX → PDF (MIT)
    └── course-factory-brand/     O SLOT DE MARCA
        └── template/             o pré-molde neutro, versionado
```

**Autossuficiente:** numa máquina com Python 3 e LaTeX, um `git clone` publica.
Não há `pip install`, não há Pandoc, não há dependência de rede. O contêiner só
é necessário para **testar**, não para publicar.

---

## Requisitos

Para **escrever**, basta o agente. Para **publicar** em PDF:

```bash
sudo apt install texlive-xetex texlive-latex-extra texlive-lang-portuguese \
                 latexmk poppler-utils
```

Para **testar os comandos**, um motor de contêiner:

```bash
sudo apt install podman      # ou Docker
```

macOS, Windows/WSL2, Fedora e a alternativa sem instalar nada:
[`docs/01-instalacao.md`](docs/01-instalacao.md).

---

## Onde fica a documentação

`documentation/` **não é versionado**. A ferramenta é pública; o material
produzido pertence a quem o gerou e circula onde cada um decidir — site, wiki,
Drive, servidor próprio ou um repositório à parte.

Para mandá-lo para outro lugar, uma linha:

```bash
echo ~/Documentos/documentacao > DOCUMENTATION_PATH
```

O ponteiro é a memória da máquina: todos os programas o leem, e ele mesmo é
ignorado pelo git. Detalhes em [`docs/04-arquitetura.md`](docs/04-arquitetura.md).

---

## Licença

**MIT** — ver [`LICENSE`](LICENSE), que traz o escopo explicitado. Em resumo:

- **A fábrica é livre.** Preset, programas, documentação e pré-molde de marca:
  use, modifique, redistribua, inclusive comercialmente.
- **A documentação produzida é de quem a produziu.** Este repositório não
  distribui manual nenhum.
- **O software documentado não é seu nem meu.** Um manual sobre o Docker não é
  documentação oficial do Docker e não concede direito sobre ele.
- **Kits de marca de terceiros seguem a licença deles.**
- **A marca Andrada's Dev não está aqui e não é licenciada por este documento.**

Componentes de terceiros: [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

---

## Créditos

| Papel | Quem |
|---|---|
| **Autor e orientador** | **Ronivaldo Domingues de Andrade** — concebeu a fábrica, definiu o preset, o escopo, o padrão de qualidade, e responde pelo resultado |
| **Pesquisa, verificação e redação** | Agente de IA (Claude Code, Anthropic), nomeado e versionado em cada peça publicada |
| **Conversor** | [md2book](https://github.com/ronidomingues/md2book) — MIT, mesmo autor |
| **Fábrica irmã** | Course Factory — mesma arquitetura, mesmo kit de marca, cursos em vez de manuais |

O prompt que fundou este projeto está preservado em
[`docs/00-prompt-fundador.md`](docs/00-prompt-fundador.md).

---

<div align="center">
<sub>Entrevista, pesquisa, teste, publicação.<br>
O resto é o software que você escolher.</sub>
</div>
