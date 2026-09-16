# md2book

Transforma uma pasta de arquivos Markdown num **livro completo em PDF**, com
capa, sumário, partes, capítulos numerados, referências cruzadas clicáveis e
anexo de código-fonte — pronto para ler na tela ou imprimir. E, do mesmo
repertório, transforma decks de aula em **slides de Beamer em PDF**.

Feito para cursos escritos em Markdown. Você escreve os arquivos como sempre
escreveu; o md2book cuida de virar livro e de virar aula.

- **Sem Pandoc.** A conversão Markdown → LaTeX é própria.
- **Sem dependências Python.** Só a biblioteca padrão.
- **Reutilizável.** O mesmo programa serve para qualquer curso com a mesma
  estrutura de pastas.
- **Com tema.** Um pacote `.sty` seu pode assumir capa, créditos e rodapé sem
  que você precise alterar o md2book — é assim que a identidade da
  [Andrada's Dev](#tema-da-marca-pacotes-e-arquivos-externos) entra.

---

## Índice

1. [Requisitos](#requisitos)
2. [Instalação](#instalação)
3. [Início rápido](#início-rápido)
4. [Quando falta LaTeX na máquina](#quando-falta-latex-na-máquina)
5. [A estrutura que o md2book aceita](#a-estrutura-que-o-md2book-aceita)
6. [Manual dos comandos](#manual-dos-comandos)
7. [Opções da linha de comando](#opções-da-linha-de-comando)
8. [O arquivo `livro.json`](#o-arquivo-livrojson)
9. [Tema da marca: pacotes e arquivos externos](#tema-da-marca-pacotes-e-arquivos-externos)
10. [Slides de aula](#slides-de-aula)
11. [Markdown suportado](#markdown-suportado)
12. [O que é gerado](#o-que-é-gerado)
13. [Usar em outro curso](#usar-em-outro-curso)
14. [Problemas comuns](#problemas-comuns)
15. [Organização do código](#organização-do-código)
16. [Licença](#licença)

---

## Requisitos

**Python 3.9 ou mais novo.** Nenhum pacote Python adicional.

**Uma distribuição LaTeX com XeLaTeX** e as fontes DejaVu. O XeLaTeX é
obrigatório (e não o pdfLaTeX) porque o material tem acentuação, setas (`→`) e
caracteres de desenho de caixa (`┌─┐│└┘├`) usados em diagramas.

No Debian/Ubuntu:

```bash
sudo apt install texlive-xetex texlive-latex-extra texlive-lang-portuguese \
                 latexmk fonts-dejavu
```

No Fedora:

```bash
sudo dnf install texlive-xetex texlive-collection-latexextra \
                 texlive-collection-langportuguese latexmk dejavu-fonts-all
```

No macOS: instale o [MacTeX](https://tug.org/mactex/). As fontes DejaVu podem
ser baixadas em [dejavu-fonts.github.io](https://dejavu-fonts.github.io/).

**Não precisa conferir isso à mão.** O próprio programa examina a máquina:

```bash
md2book verificar
```

```bash
Ambiente de compilação (motor: xelatex)

  Programas
    ✓ xelatex               — /usr/bin/xelatex
    ✓ latexmk               — /usr/bin/latexmk
    ✓ kpsewhich             — /usr/bin/kpsewhich
  Pacotes LaTeX
    ✓ 20 presentes
  Fontes
    ✓ DejaVu Serif
    ✓ DejaVu Sans
    ✓ DejaVu Sans Mono
  Docker (opcional)       ✓ 3 presentes

  → Dá para compilar o PDF.
```

E se faltar algo, ele não deixa a compilação quebrar no meio: veja
[Quando falta LaTeX na máquina](#quando-falta-latex-na-máquina).

Se o `latexmk` existir, o md2book o usa (ele decide sozinho quantas passagens
são necessárias para o sumário e as referências fecharem). Se não existir, o
programa roda o XeLaTeX três vezes.

---

## Instalação

Escolha **uma** das três formas.

### 1. Como comando do sistema (recomendado)

```bash
uv tool install .
```

A partir daí, `md2book` funciona de qualquer pasta:

```bash
cd ~/cursos/meu-curso
md2book
```

Para atualizar depois de mexer no código: `uv tool install --reinstall .`
Para remover: `uv tool uninstall md2book`

### 2. Dentro do projeto, com uv

```bash
uv sync
uv run md2book -r modelo
```

Útil enquanto você desenvolve: não instala nada fora do projeto.

### 3. Sem instalar nada

```bash
python3 md2book.py -r modelo
```

O arquivo `md2book.py` na raiz é um atalho que chama exatamente a mesma
função do comando instalado. Serve para rodar o programa direto do
repositório, sem uv e sem ambiente virtual.

> As três formas aceitam os mesmos comandos e as mesmas opções. Neste manual
> os exemplos usam `md2book`; troque por `uv run md2book` ou
> `python3 md2book.py` conforme o seu caso.

---

## Início rápido

O repositório traz um curso de exemplo em `modelo/`. Gere o livro dele:

```bash
md2book -r modelo
```

Ao final:

```
PDF pronto: .../modelo/build/livro.pdf
```

Abra o PDF. São 25 páginas que exercitam tudo o que o conversor entende:
capa, sumário, três partes, capítulo em subpasta, tabelas, diagramas em
caracteres de caixa, listas de tarefas, citações e o anexo com o código-fonte.

Para o seu curso de verdade:

```bash
cd ~/cursos/meu-curso
md2book listar          # confira a ordem dos capítulos primeiro
md2book -t "Meu Curso" -a "Seu Nome"
```

---

## Quando falta LaTeX na máquina

Antes de chamar o compilador, o md2book confere se o motor TeX, os 20 pacotes
que o preâmbulo carrega e as fontes configuradas existem. **Se estiver tudo
no lugar, nada muda** — ele compila direto, sem perguntar nada.

Se faltar alguma coisa, ele mostra exatamente o que falta e oferece três
saídas:

```
Ambiente de compilação (motor: xelatex)

  Programas
    ✗ xelatex               — não encontrado no PATH
  Fontes
    ✗ DejaVu Serif          — família não instalada

  → Faltam 2 dependências para compilar o PDF: xelatex, DejaVu Serif.

Como você quer resolver?

  1) Instalar no sistema, com apt (Debian/Ubuntu)
       $ sudo apt-get update
       $ sudo apt-get install -y texlive-xetex texlive-latex-extra ...
     Confira os comandos antes de aceitar: eles mexem no seu sistema.

  2) Compilar dentro de um container Docker
     Não instala nada no sistema. A primeira execução baixa
     o TeX Live na imagem (alguns minutos, ~2 GB).

  3) Não instalar nada
     Gera os arquivos .tex e para, sem tentar compilar.

Escolha [1/2/3] (Enter = 3):
```

### 1 — Instalar no sistema

O programa detecta o gerenciador de pacotes (`apt`, `dnf`, `zypper`,
`pacman`, `brew`, `winget`), **mostra o comando exato** e só o executa depois
que você aceita. Ao terminar, ele examina a máquina de novo: se ainda faltar
algo, avisa em vez de tentar compilar e falhar.

Nada é instalado sem a sua confirmação explícita.

### 2 — Compilar em container

Não toca no sistema. O md2book escreve um `Dockerfile` e um `compose.yaml` em
`build/docker/`, constrói uma imagem com o TeX Live e compila lá dentro:

```bash
md2book --ambiente container
```

Exige **Docker e Docker Compose** instalados e o daemon rodando — se faltar,
o programa diz o que falta e aponta para
<https://docs.docker.com/engine/install/>. A primeira execução demora
(baixa ~2 GB); as seguintes reaproveitam a imagem.

A conversão Markdown → LaTeX continua acontecendo na sua máquina (é Python
puro); o container serve **só como compilador**. Os arquivos são gravados com
o seu usuário, então o `build/` continua seu — não vira propriedade do root.

A imagem instala os **mesmos pacotes** que a opção 1 instalaria no sistema, de
modo que o PDF sai idêntico nos dois caminhos.

#### Usando uma imagem pronta

Se a sua rede bloqueia os espelhos do Debian, a construção da imagem falha com
`403 Forbidden` ou `InRelease is not signed`. Nesse caso, aponte para uma
imagem que já traga o TeX Live:

```json
{ "imagem_latex": "texlive/texlive:latest" }
```

Com esse campo preenchido, o md2book não constrói imagem nenhuma: escreve um
`compose.yaml` que usa a que você indicou.

> **Cuidado com as fontes.** Imagens genéricas de TeX Live costumam expor,
> além das DejaVu TrueType, versões **Type 1** das mesmas famílias. O XeLaTeX
> pode escolher a Type 1 para o negrito e o `xdvipdfmx` morre com
> `Error occurred while loading font: .../DejaVuSansMono.pfb`. Foi
> exatamente o que aconteceu em teste com `texlive/texlive:latest`. A imagem
> que o md2book constrói não tem esse problema, porque instala as DejaVu pelo
> `fonts-dejavu`, só em TrueType. Se você usar uma imagem pronta e topar com
> esse erro, remova do texmf dela as DejaVu Type 1 e rode `fc-cache -f`.

### 3 — Não instalar nada

Gera os `.tex` e para, sem tentar compilar. É o padrão quando não há terminal
interativo (script, CI, `cron`), justamente para não quebrar no meio:

```bash
md2book --ambiente parar
```

### Escolhendo sem perguntas

`--ambiente` fixa a política e dispensa o menu:

| Valor | Comportamento |
|---|---|
| `perguntar` | Padrão. Faltando algo, mostra o menu. Sem terminal, age como `parar` |
| `instalar` | Faltando algo, instala no sistema |
| `container` | **Sempre** compila no container, mesmo com LaTeX local |
| `parar` | Faltando algo, gera só os `.tex` |
| `ignorar` | Não verifica nada e vai direto para o compilador |

### Códigos de saída

| Código | Significado |
|---|---|
| `0` | Deu certo |
| `1` | Erro: a compilação falhou, ou a configuração é inválida |
| `2` | Erro de uso (arquivo de configuração inexistente, por exemplo) |
| `3` | Os `.tex` foram gerados, mas o PDF não — faltavam dependências |

Isso permite tratar o caso em script:

```bash
md2book --ambiente parar
if [ $? -eq 3 ]; then
    echo "LaTeX ausente nesta máquina; .tex prontos para compilar em outra."
fi
```

---

## A estrutura que o md2book aceita

### A regra mínima

**Uma pasta com arquivos `.md`.** Só isso. Sem configuração, sem convenção de
nomes obrigatória:

```
meu-curso/
├── introducao.md
├── instalacao.md
└── conceitos.md
```

```bash
md2book -r meu-curso -t "Meu Curso"
```

Três regras governam o resultado:

1. **Cada arquivo `.md` vira um capítulo.** A busca é recursiva: subpastas
   entram também.
2. **O primeiro `#` do arquivo vira o título do capítulo** e é removido do
   corpo, para não aparecer duas vezes. Se o arquivo não tiver `#`, o nome do
   arquivo é usado.
3. **A ordem é a ordem natural dos nomes**, com números lidos como números:
   `2-x.md` vem antes de `10-x.md` (e não depois, como na ordem alfabética
   pura).

### Numerando os arquivos

Como a ordem vem do nome, o jeito prático de controlar o índice é numerar os
arquivos. **A numeração não precisa ser contínua** — deixe buracos para poder
inserir capítulos depois sem renomear tudo:

```
meu-curso/
├── 00-mapa.md          ← visão geral
├── 01-introducao.md
├── 02-instalacao.md
├── 10-conceitos.md     ← salto proposital: 03..09 ficam livres
├── 20-pratica.md
├── 90-referencias.md
└── GLOSSARIO.md        ← sem número: vai para o fim
```

O md2book renumera os capítulos do livro em sequência (1, 2, 3…). Os números
dos arquivos são só para você organizar a pasta.

### Capítulo em subpasta

Uma pasta cujo conteúdo principal é um `README.md` vira **um capítulo**:

```
meu-curso/
├── 01-introducao.md
└── 03-projeto/
    ├── README.md       ← este é o capítulo
    ├── app.py          ← código: vai para o anexo, se você quiser
    └── config.yaml
```

Links para a pasta (`03-projeto/`) ou para o arquivo
(`03-projeto/README.md`) apontam para esse capítulo.

### Links entre capítulos

Escreva links relativos normais, como faria no GitHub:

```markdown
Veja [a instalação](02-instalacao.md) antes de continuar.
Detalhes em [10-conceitos.md](10-conceitos.md).
```

No livro eles viram **referências internas clicáveis**:

| No Markdown | No PDF |
|---|---|
| `[a instalação](02-instalacao.md)` | a instalação (cap. 2) |
| `[10-conceitos.md](10-conceitos.md)` | cap. 4 |
| `[texto](https://exemplo.com)` | texto (link externo clicável) |

Links para arquivos que **não** viraram capítulo (uma imagem, um `.py`)
aparecem como caminho em fonte monoespaçada, sem link quebrado.

### Estrutura completa, com partes e anexo

Para um curso grande, acrescente um `livro.json` na raiz da pasta. Ele agrupa
capítulos em partes, define a capa e liga o anexo de código:

```
meu-curso/
├── livro.json          ← configuração (opcional)
├── 00-mapa.md          ← "abertura": capítulo sem número, antes da Parte I
├── 01-introducao.md    ┐
├── 02-instalacao.md    ├─ Parte I
├── 03-projeto/         ┘
│   ├── README.md
│   ├── app.py          ← entra no anexo de código-fonte
│   └── config.yaml     ← idem
├── 10-conceitos.md     ─  Parte II
├── 90-referencias.md   ┐
├── GLOSSARIO.md        ┘─ Parte III
└── build/              ← gerado pelo md2book (não versione)
    ├── livro.pdf
    ├── main.tex
    └── tex/
```

Essa é exatamente a estrutura de `modelo/`. **Copie `modelo/` como ponto de
partida** para um curso novo:

```bash
cp -r modelo ~/cursos/curso-novo
cd ~/cursos/curso-novo
# apague os .md de exemplo, escreva os seus, ajuste o livro.json
md2book
```

### O que fica de fora

Por padrão o md2book ignora `build/`, `md2book/`, `node_modules/` e `.git/`.
Qualquer outro `.md` da pasta entra no livro. Para excluir mais coisas, use
`ignorar` no `livro.json` — lembrando que o valor **substitui** a lista
padrão, então repita o que ainda quiser fora:

```json
{ "ignorar": ["build/**", "**/.git/**", "rascunhos/**", "NOTAS.md"] }
```

> **Atenção:** rode o md2book apontando para a pasta do curso (`-r`), ou de
> dentro dela. Se você rodar na raiz **deste repositório**, ele tentará
> transformar este próprio README em capítulo.

---

## Manual dos comandos

### `md2book livro` (padrão)

Converte tudo e compila o PDF. É o que roda quando você não passa comando:

```bash
md2book                 # idêntico a: md2book livro
```

Etapas, em ordem: descobre os `.md` → converte cada um em `.tex` → monta o
`main.tex` → chama o XeLaTeX → copia o resultado para `build/livro.pdf`.

### `md2book tex`

Só a conversão Markdown → LaTeX. Não compila.

```bash
md2book tex
```

Use quando quiser inspecionar ou ajustar o LaTeX à mão, ou quando não houver
XeLaTeX na máquina. Os arquivos ficam legíveis em `build/tex/`.

### `md2book slides` e `md2book slides-tex`

Converte os decks de aula em Beamer e compila um PDF por aula, mais o PDF único
com todas. A configuração é o `slides.json`, não o `livro.json`:

```bash
md2book slides                  # decks de ./md → ./latex → ./pdf
md2book slides-tex              # só o LaTeX
md2book slides -c 97-publicacao/slides/slides.json
```

O formato do deck e os campos do `slides.json` estão em
[Slides de aula](#slides-de-aula).

### `md2book listar`

Mostra, sem gerar nada, a ordem em que os capítulos vão entrar, as partes e os
arquivos do anexo:

```bash
$ md2book listar -r modelo
Abertura (sem numeração):
   00-mapa.md                               Mapa do curso

Porta de entrada
   1. 01-introducao.md                      Introdução — o que é e por que existe
   2. 02-instalacao.md                      Instalação
   3. 03-projeto/README.md                  Projeto de exemplo
...
Anexo de código-fonte (2 arquivos):
   03-projeto/app.py
   03-projeto/config.yaml
```

**Rode isto antes de compilar.** É o jeito rápido de conferir se algum arquivo
ficou de fora ou fora de ordem, sem esperar o LaTeX.

### `md2book verificar`

Examina a máquina e diz se dá para compilar, sem gerar nada:

```bash
md2book verificar
```

Lista o motor TeX, os pacotes LaTeX exigidos, as fontes configuradas e o
estado do Docker. Sai com `0` se dá para compilar e `1` se não — útil em CI.

A lista de pacotes conferida é lida do próprio preâmbulo que o md2book gera,
então ela nunca fica desatualizada em relação ao que o livro realmente usa.

### `md2book init`

Cria um `livro.json` com todos os campos e os valores padrão, para você editar:

```bash
md2book init -t "Meu Curso" -a "Seu Nome"
```

Recusa-se a sobrescrever um `livro.json` que já exista.

---

## Opções da linha de comando

| Opção | O que faz |
|---|---|
| `-r`, `--raiz PASTA` | Pasta com os `.md`. Sem isto, usa a pasta atual |
| `-c`, `--config ARQUIVO` | Usa outro JSON de configuração |
| `-s`, `--saida PASTA` | Onde escrever (padrão: `build`) |
| `-t`, `--titulo TEXTO` | Título do livro, na capa (nos slides, o nome do curso) |
| `-a`, `--autor NOME` | Autor, impresso na capa e nos metadados do PDF |
| `--ambiente MODO` | O que fazer se faltar LaTeX: `perguntar` (padrão), `instalar`, `container`, `parar`, `ignorar` |
| `-q`, `--silencioso` | Só mostra o resultado final e os erros |
| `-V`, `--version` | Mostra a versão |
| `-h`, `--help` | Ajuda |

As opções **sobrepõem** o `livro.json`. Isso permite gerar variações sem
editar arquivo nenhum:

```bash
md2book -r modelo -t "Edição de Turma" -a "Prof. Fulano" -s build-turma
```

Quando você usa `-r PASTA`, o md2book procura o `livro.json` **dentro dessa
pasta**. É por isso que `md2book -r modelo` já sai configurado.

---

## O arquivo `livro.json`

Totalmente opcional: sem ele o programa usa os padrões. Fica na raiz da pasta
do curso. Todos os campos abaixo são opcionais — escreva só os que quiser
mudar.

### Capa e identificação

```json
{
  "titulo": "Curso Modelo",
  "subtitulo": "A estrutura que o md2book espera",
  "autor": "Seu Nome",
  "ano": "2026",
  "nota_capa": "Texto pequeno no rodapé da capa.",
  "idioma": "brazil"
}
```

`idioma` é passado ao `polyglossia`; muda a hifenização e os nomes automáticos
("Capítulo", "Sumário"). Use `portuguese`, `english`, `spanish`, `french`…

### Arquivos e ordem

```json
{
  "raiz": ".",
  "saida": "build",
  "nome_arquivo": "livro",
  "ignorar": ["build/**", "rascunhos/**", "**/node_modules/**"],
  "abertura": ["00-mapa.md"],
  "incluir_restantes": true,
  "titulos": { "00-mapa.md": "Mapa do curso" }
}
```

| Campo | Padrão | Para quê |
|---|---|---|
| `raiz` | `"."` | Pasta com os `.md`, relativa ao `livro.json` |
| `saida` | `"build"` | Onde escrever o `.tex` e o PDF |
| `nome_arquivo` | `"livro"` | Gera `livro.pdf` |
| `ignorar` | `build`, `md2book`, `node_modules`, `.git` | Curingas de exclusão (substitui o padrão) |
| `abertura` | `[]` | Capítulos **sem número**, antes da Parte I |
| `incluir_restantes` | `true` | `.md` não citado em `partes` entra no fim |
| `titulos` | `{}` | Renomeia o capítulo sem mexer no arquivo |

### Partes

Agrupam capítulos. **A ordem aqui manda** — ela vence a ordem natural dos
nomes:

```json
{
  "partes": [
    {
      "titulo": "Porta de entrada",
      "subtitulo": "O que é, como instalar e um projeto que roda",
      "arquivos": ["01-introducao.md", "02-instalacao.md", "03-projeto/README.md"]
    },
    {
      "titulo": "Núcleo",
      "subtitulo": "O modelo mental por dentro",
      "arquivos": ["10-*.md", "20-*.md"]
    }
  ]
}
```

Em `arquivos` valem curingas: `01-*.md`, `cap/**/*.md`. Um arquivo entra na
primeira parte que o encontrar. Os que sobrarem vão para uma parte final
(controlada por `incluir_restantes` e `titulo_restantes`).

Sem `partes`, o livro fica com capítulos corridos, sem divisões — o que é
adequado para um curso pequeno.

### Anexo com o código-fonte

Coloca os arquivos de um projeto no fim do livro, cada um como uma seção, com
realce de linguagem pela extensão:

```json
{
  "apendice_fontes": {
    "ativo": true,
    "titulo": "Código-fonte do projeto de exemplo",
    "introducao": "Listagem integral dos arquivos de `03-projeto/`.",
    "padroes": ["03-projeto/**/*", "03-projeto/.*"],
    "ignorar": ["**/node_modules/**", "**/*.png", "**/*.lock"],
    "tamanho_maximo": 200000
  }
}
```

Arquivos binários e maiores que `tamanho_maximo` bytes são pulados
automaticamente. O segundo padrão (`.*`) é necessário para pegar arquivos
ocultos como `.env.example` ou `.dockerignore`.

### Aparência

```json
{
  "papel": "a4paper",
  "corpo": "11pt",
  "duas_faces": true,
  "cor_destaque": "1F4E79",
  "tamanho_codigo": 7.8,
  "profundidade_sumario": 1
}
```

| Campo | Padrão | Para quê |
|---|---|---|
| `papel` | `a4paper` | `a5paper`, `letterpaper`, `b5paper`… |
| `corpo` | `11pt` | `10pt`, `12pt` |
| `duas_faces` | `true` | Margens espelhadas, capítulo abrindo à direita |
| `geometria` | `inner=3.0cm,outer=2.4cm,…` | Qualquer chave do pacote `geometry` |
| `cor_destaque` | `1F4E79` | Cor de títulos, filetes, links e etiquetas |
| `cor_codigo_fundo` | `F6F6F4` | Fundo das caixas de código |
| `fontes` | DejaVu | `texto`, `titulo`, `mono`, `simbolos`, escalas e `diretorio` (abaixo) |
| `tamanho_codigo` | `7.8` | Pontos. Menor faz caber diagramas mais largos |
| `sangria_codigo` | `0.9cm` | Quanto as caixas de código avançam nas margens |
| `rotulo_linguagem` | `true` | Etiqueta "bash", "YAML" sobre cada caixa |
| `regua_horizontal` | `ignorar` | O que fazer com `---`: `linha` ou `ornamento` |
| `remover_numeracao_titulos` | `true` | Tira o "1." de `## 1. Título` |
| `referencia_capitulo` | `true` | Mostra "(cap. N)" ao lado de links internos |
| `profundidade_sumario` | `1` | `2` inclui subseções no sumário |
| `profundidade_numeracao` | `2` | Até que nível numerar as seções |
| `entrelinha_codigo` | `null` | Entrelinha do código; em `null`, derivada do corpo |
| `titulo_restantes` | `Complementos` | Nome da parte que recolhe o que sobrou |
| `ligaduras_tex` | `false` | `true` transforma `--` em travessão e aspas em curvas |
| `motor` | `xelatex` | `lualatex` também funciona |
| `imagem_latex` | `null` | Imagem pronta para `--ambiente container`; em `null`, o md2book constrói a sua |

#### Fontes de uma pasta, sem instalar nada

Por padrão, `fontes.texto` é o **nome da família instalada** no sistema. Preencha
`fontes.diretorio` e o fontspec passa a ler os arquivos do disco — o PDF sai igual
em outra máquina, mesmo sem a fonte instalada:

```json
{
  "fontes": {
    "diretorio": "../../tema/fontes",
    "extensao": ".ttf",
    "texto": "Inter",
    "texto_faces": { "UprightFont": "*-Regular", "BoldFont": "*-Bold" },
    "mono": "JetBrainsMono",
    "mono_faces": { "UprightFont": "*-Regular", "BoldFont": "*-Bold" }
  }
}
```

O caminho é **relativo à pasta de saída** (onde o `main.tex` é compilado), e o `*`
dos `*_faces` é substituído pelo nome da família, como manda o fontspec. Sem
`diretorio`, os campos `*_faces` são ignorados.

Sobre `remover_numeracao_titulos`: se você escreve `## 1. Instalação`,
`## 2. Uso`, o LaTeX já numera as seções sozinho e o resultado sairia
"2.1 1. Instalação". Por isso a numeração escrita à mão é removida por padrão.
Títulos como `## 1979 → 2026` ou `## 512 MB de RAM` são preservados: só conta
como numeração o padrão "número + ponto/parêntese + espaço".

---

## Tema da marca: pacotes e arquivos externos

O md2book desenha uma capa simples e um miolo sóbrio. Quando o livro precisa da
identidade de uma empresa — capa própria, página de créditos, rodapé com marca —
você **não altera o md2book**: escreve um pacote LaTeX e o declara na configuração.

```json
{
  "recursos": [
    "97-publicacao/tema/andradasdev-curso.sty",
    "97-publicacao/tema/andradasdev-curso-ambiente.tex"
  ],
  "pacotes_extra": ["andradasdev-curso"],
  "capa_comando": "\\adaberturalivro",
  "encerramento": ["\\adcolofao"],
  "preambulo_extra": "\\renewcommand{\\mdcode}[1]{\\texttt{#1}}",
  "texinputs": ["97-publicacao/tema"]
}
```

| Campo | O que faz |
|---|---|
| `recursos` | Arquivos copiados para a pasta de saída antes de compilar. Caminhos relativos à raiz do projeto. Pode ser `{"de": "...", "para": "..."}` para renomear. |
| `pacotes_extra` | `\usepackage{...}` emitidos **no fim** do preâmbulo — o tema vê tudo já definido e pode sobrescrever. |
| `preambulo_extra` | Linhas LaTeX cruas no fim do preâmbulo (string ou lista). |
| `capa_comando` | Comando que abre o livro. Padrão `\mdcapa`; vazio (`""`) tira a capa. |
| `encerramento` | Comandos emitidos logo antes de `\end{document}` (colofão, ficha final). |
| `texinputs` | Pastas acrescentadas ao `TEXINPUTS` na compilação, para um `.sty` que mora fora. |
| `tabela_simples` | Tabelas como `tabular` em vez de `longtable` (dentro de caixa ou de frame). |
| `opcoes_lista` | `false` desliga as opções de `enumitem` nas listas (obrigatório em Beamer). |

Copiar o `.sty` para dentro do projeto, em vez de apontar para ele por um caminho
absoluto, é deliberado: o PDF continua reconstruível em outra máquina e daqui a
anos, inclusive por quem não tem o repositório onde o tema nasceu.

Um tema completo, pronto para copiar, está em
`08-cursos/latex/andradasdev-curso.sty` do repositório da marca Andrada's Dev.

---

## Slides de aula

O mesmo conversor que faz o livro faz os slides — mas **não do mesmo texto**. Um
livro se lê, um slide se projeta. A fonte dos slides é um *deck* escrito à parte,
um arquivo por aula.

```bash
md2book slides                 # gera os .tex e compila um PDF por aula
md2book slides-tex             # só os .tex
md2book slides -c slides.json  # apontando a configuração
```

### O formato do deck

````markdown
---
aula: Aula 03
curso: Docker e Containers
subtitulo: Camadas, cache e o que vai para a imagem
duracao: 45 min
---

# Como o Docker monta uma imagem

## Camadas
A ideia que explica quase todo comportamento estranho do build.

### Uma camada é um diff

- Cada instrução do Dockerfile cria **uma camada**.
- A camada guarda só o que mudou.

```notas
Roteiro do professor: mostre `docker history` antes da teoria.
```

### O cache quebra de cima para baixo

Tabelas, código, citações e imagens funcionam como em qualquer arquivo.
````

| Marca | Vira |
|---|---|
| bloco `---` no topo | metadados da aula (`aula`, `curso`, `subtitulo`, `data`, `autor`) |
| `#` | título da aula — a capa |
| `##` | parte da aula — tela de transição (`\adsecao`) |
| `###` | **um slide** |
| `####` e mais fundo | destaque em negrito dentro do slide |
| ` ```notas ` (ou `:::notas … :::`) | `\note{}` — roteiro do professor |
| `---` dentro de um slide | continua o slide na tela seguinte, com `(cont.)` |

Todo frame é gerado como `fragile`: código verbatim funciona em qualquer slide.

### O `slides.json`

```json
{
  "curso": "Docker e Containers",
  "entrada": "md",
  "saida": "latex",
  "saida_pdf": "pdf",
  "pdf_unico": "docker-slides-completo.pdf",
  "proporcao": "169",
  "tema": "andradasdev",
  "limite_linhas_slide": 12
}
```

| Campo | Padrão | Para quê |
|---|---|---|
| `entrada` | `md` | Pasta dos decks, relativa à raiz |
| `saida` / `saida_pdf` | `latex` / `pdf` | Onde ficam os `.tex` e os PDFs |
| `pdf_unico` | `slides-completo.pdf` | Junta as aulas num PDF só (`pdfunite` ou Ghostscript); vazio desliga |
| `proporcao` | `169` | `43` para projetor antigo |
| `alinhamento_vertical` | `t` | Conteúdo no topo; `""` volta ao centralizado do Beamer |
| `tema` / `opcoes_tema` | `andradasdev` | Qualquer tema Beamer instalado ou copiado por `recursos` |
| `capa_comando`, `secao_comando`, `fechamento_comando` | comandos do tema | Trocáveis por comandos seus |
| `notas` | `nenhuma` | `segunda-tela` compila com as notas visíveis |
| `limite_linhas_slide` | `12` | Acima disso, **avisa** (não falha): provavelmente são dois slides |
| `cor_codigo_fundo`, `cor_codigo_texto` | escuros | A caixa de código dos slides é escura por padrão |

O aviso de slide grande é intencionalmente um aviso: quem decide o que cabe na aula
é quem ensina. Mas ele quase sempre acerta.

---

## Markdown suportado

| Escrito assim | Vira |
|---|---|
| `# Título` (o primeiro do arquivo) | Título do capítulo |
| `## `, `### `, `#### ` | Seção, subseção, subsubseção |
| \`\`\`bash … \`\`\` | Caixa de código com etiqueta da linguagem |
| `` `código` `` | Fonte monoespaçada, com pontos de quebra em `/ - . : _` |
| `**negrito**`, `*itálico*`, `~~riscado~~` | Negrito, itálico, riscado |
| Tabelas GFM (`\| a \| b \|`) | Tabela com largura de coluna calculada |
| `> citação` | Caixa com filete lateral |
| `- item` / `1. item` | Lista, com aninhamento por indentação |
| `- [ ]` / `- [x]` | Lista de tarefas, com □ e ✓ |
| `[texto](arquivo.md)` | Referência interna "(cap. N)" |
| `[texto](https://…)`, `<https://…>` | Link externo clicável |
| `---` | Ignorado por padrão (veja `regua_horizontal`) |

**Blocos de código** aceitam qualquer linguagem no cabeçalho da cerca; a
etiqueta usa o nome bonito quando conhecido (`yaml` → "YAML", `dockerfile` →
"Dockerfile"). O conteúdo é tratado como verbatim puro: `\`, `{`, `$` e `%`
saem exatamente como você escreveu.

**Tabelas** têm a largura de cada coluna calculada a partir do conteúdo e da
maior palavra indivisível da coluna, para nada transbordar. Tabelas longas
quebram entre páginas repetindo o cabeçalho.

**Emojis** sem glifo nas fontes (✅ ❌ ⚠ 🟡 ⬜) viram símbolos coloridos
equivalentes. Dentro de blocos de código viram `[ok]`, `[x]`, `[!]`.

**Diagramas em caracteres de caixa** (`┌─┐│└┘├┤┬┴┼`) são preservados. As caixas
de código avançam nas margens e usam corpo 7,8 pt, o que comporta cerca de 100
colunas sem quebrar a linha.

---

## O que é gerado

```
build/
├── livro.pdf      ← o livro
├── main.tex       ← documento mestre: preâmbulo + \input de cada capítulo
├── tex/
│   ├── cap-01-introducao.tex
│   ├── cap-02-instalacao.tex
│   ├── …
│   └── anexo-fontes.tex
└── main.log       ← log do LaTeX, útil quando algo dá errado
```

**Tudo em `build/` é descartável**: apagar a pasta não perde nada, o próximo
`md2book` refaz. Por isso `build/` está no `.gitignore`.

Os `.tex` de `build/tex/` são legíveis e independentes. Se você precisa de um
ajuste fino que a configuração não cobre, pode editá-los e rodar
`latexmk -xelatex main.tex` dentro de `build/` — lembrando que o próximo
`md2book` sobrescreve.

---

## Usar em outro curso

Todo o ponto do md2book é servir a vários cursos com a mesma estrutura. Com o
comando instalado (`uv tool install .`), nada precisa ser copiado:

```bash
cd ~/cursos/curso-de-python
md2book listar
md2book -t "Curso de Python" -a "Seu Nome"
```

Ou sem sair do lugar:

```bash
md2book -r ~/cursos/curso-de-python -t "Curso de Python"
```

Para começar um curso novo do zero, use o modelo como gabarito:

```bash
cp -r modelo ~/cursos/curso-novo
```

E para gerar vários livros de uma vez:

```bash
for curso in ~/cursos/*/; do
    md2book -r "$curso" -q
done
```

---

## Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `nem latexmk nem xelatex foram encontrados` | LaTeX não instalado | Veja [Requisitos](#requisitos) |
| `Falha na compilação` | Erro de LaTeX | Abra `build/main.log` e procure a linha iniciada por `!` |
| Um capítulo não apareceu | Casou com `ignorar`, ou não é `.md` | Rode `md2book listar` para conferir |
| Capítulos fora de ordem | Ordem natural do nome | Numere os arquivos ou liste-os em `partes` |
| Este README virou capítulo | Rodou na raiz do repositório | Use `-r pasta-do-curso` |
| Quadrados no lugar de letras | Fontes DejaVu ausentes | Instale `fonts-dejavu` |
| Diagrama ASCII quebrando linha | Diagrama largo demais | Baixe `tamanho_codigo` para `7.0` |
| Tabela apertada | Muitas colunas | Reduza colunas ou use `papel: "a4paper"` com `duas_faces: false` |
| `403 Forbidden` ou `InRelease is not signed` ao construir a imagem | A rede bloqueia os espelhos do Debian | Use `imagem_latex` com uma imagem pronta |
| `xdvipdfmx: Error occurred while loading font: ...pfb` | A imagem resolveu DejaVu para Type 1 | Veja [Usando uma imagem pronta](#usando-uma-imagem-pronta) |
| `permission denied` ao falar com o Docker | Seu usuário não está no grupo `docker` | `sudo usermod -aG docker $USER` e reabra a sessão |
| O `build/` virou propriedade do root | Container antigo, sem mapeamento de usuário | Apague o `build/` e rode de novo |

Para investigar a conversão sem esperar o LaTeX, gere só o `.tex`:

```bash
md2book tex && less build/tex/cap-01-introducao.tex
```

---

## Organização do código

```
md2book/
├── pyproject.toml        ← metadados, entry point, build com uv
├── md2book.py            ← atalho para rodar sem instalar
├── modelo/               ← curso de exemplo (gabarito de estrutura)
└── src/md2book/
    ├── cli.py            ← linha de comando
    ├── ambiente.py       ← verifica LaTeX/fontes; instala ou usa container
    ├── config.py         ← padrões e leitura do livro.json
    ├── discovery.py      ← acha os .md, ordena, divide em partes
    ├── blocks.py         ← Markdown → árvore de blocos
    ├── inline.py         ← Markdown embutido → LaTeX
    ├── latexutil.py      ← escape, símbolos, pontos de quebra
    ├── render.py         ← árvore → corpo LaTeX do capítulo
    ├── preamble.py       ← preâmbulo, capa, estilos, caixas, fontes
    ├── slides.py         ← decks de aula → Beamer → PDF
    └── build.py          ← monta o main.tex, copia o tema e chama o compilador
```

O fluxo é uma passagem só, sem estado global:

```
descoberta → blocos → inline → render → preâmbulo → main.tex → XeLaTeX
                                                        ↑
                                          ambiente.py confere aqui
```

Onde mexer, conforme o que você quer mudar:

| Objetivo | Arquivo |
|---|---|
| Cores, fontes, capa, estilo dos títulos e caixas | `preamble.py` |
| Ensinar um bloco novo de Markdown (ex.: notas de rodapé) | `blocks.py` + `render.py` |
| Ensinar marcação nova dentro da linha | `inline.py` |
| Novo símbolo Unicode sem glifo na fonte | `latexutil.py` (`SIMBOLOS`) |
| Nova opção de configuração | `config.py` (`CONFIG_PADRAO`) |
| Nova opção de linha de comando | `cli.py` |
| Formato do deck, frames, aviso de slide grande | `slides.py` |
| Capa, créditos ou rodapé da sua marca | um `.sty` seu + `pacotes_extra` (não mexa no md2book) |
| Outro gerenciador de pacotes, ou outra imagem de container | `ambiente.py` |

### Desenvolvimento

```bash
uv sync                       # cria o ambiente
uv run md2book -r modelo      # testa no curso de exemplo
uv build                      # gera o wheel em dist/
```

O `modelo/` funciona como teste de fumaça: se ele compila sem erro e sem
transbordo de linha, a conversão está sã. Para os slides, o gabarito equivalente é
`08-cursos/exemplo/aula-00-modelo.md` no repositório da marca.

---

## Licença

[MIT](LICENSE) — Copyright (c) 2026 Ronivaldo D. Andrade.

Use, altere e distribua à vontade, inclusive comercialmente; basta manter o
aviso de copyright. A licença cobre o **md2book**, não os cursos que você
escrever com ele: o conteúdo dos seus `.md` e o PDF gerado continuam seus,
sob a licença que você quiser.
