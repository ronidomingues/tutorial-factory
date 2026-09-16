# 02 · Primeiro tutorial

Do repositório recém-clonado até seis arquivos na pasta — o manual de instalação
e o manual de uso, cada um em `.md`, `.tex` e `.pdf`.

Há dois caminhos. O primeiro é o que a fábrica existe para fazer; o segundo
mostra o que acontece por baixo.

---

## Caminho A · Com o agente (o normal)

Abra um agente de programação nesta pasta e peça:

```
como instalar Docker
```

O `CLAUDE.md` é lido automaticamente. A partir daí, o agente executa seis etapas.

### 1. Ele entrevista

Não responde direto — pergunta primeiro, tudo de uma vez:

> Para responder isso direito, preciso saber:
>
> - **Sistema operacional e versão?** (Ubuntu 24.04, Fedora 41, macOS 15, Windows 11…)
> - **Arquitetura?** (x86_64 ou ARM64/Apple Silicon)
> - **Qual versão do Docker?** (a última estável, ou uma fixa)
> - **Para que vai usar?** (estudo local, servidor, CI, desenvolvimento)
> - **Tem `sudo`?**
> - **Está atrás de proxy corporativo?**
>
> Se preferir, responda "escolhe por mim" e eu sigo pelo caminho mais comum,
> dizendo qual escolhi.

Na primeira vez, ele pergunta mais uma coisa — **onde salvar a documentação** — e
não pergunta de novo nunca mais. Ver [`04-arquitetura.md`](04-arquitetura.md)
§ *Os dois ponteiros*.

Por que a entrevista existe, e quando ela não deve acontecer:
[`06-entrevista.md`](06-entrevista.md).

### 2. Ele pesquisa

Documentação oficial, repositório do projeto, notas de release, e o nome e a
versão do pacote que **aquela distro entrega hoje**. Nada de memória, nada de
blog de 2021. Protocolo completo: [`07-pesquisa-e-verificacao.md`](07-pesquisa-e-verificacao.md).

### 3. Ele testa

```bash
python3 tools/sandbox.py --image ubuntu:24.04 --network \
  --from-doc documentation/docker/installation_2026-09-16.md \
  --report /tmp/verificacao-docker.md
```

Cada comando roda em um contêiner descartável, com código de saída e saída real
registrados. Passo que falha é passo que não pode ser publicado como está.

### 4. Ele escreve os dois documentos

`installation_AAAA-MM-DD.md` e `manual_AAAA-MM-DD.md`, em português brasileiro,
com a anatomia definida no `CLAUDE.md`.

### 5. Ele publica

```bash
python3 tools/publish-doc.py docker --ai-model "Claude Opus 5"
```

### 6. Ele resume no chat

Os seis caminhos, o número de páginas de cada PDF, onde os comandos foram
testados, e o que ficou pendente. Nada mais.

---

## Caminho B · À mão (para entender a mecânica)

### 1. Abrir a pasta e semear os esqueletos

```bash
python3 tools/new-doc.py docker
```

```console
Folder: /home/voce/tutorial-factory/documentation/docker
  created  installation_2026-09-16.md
  created  manual_2026-09-16.md

Write the research and the tested steps into those files, then:
  python3 tools/publish-doc.py docker
```

Os esqueletos vêm de `tools/example/` e **são o contrato de formato**: o que o
publicador entende e o que um leitor merece. Eles são para ser sobrescritos
linha a linha, não preenchidos educadamente em volta.

O programa **nunca sobrescreve** um arquivo existente. Voltar a um software
depois de uma versão nova é escrever uma edição nova, com data nova.

### 2. Escrever

Abra `documentation/docker/installation_2026-09-16.md`. A gramática:

| Marca | Vira |
|---|---|
| `#` na primeira linha | o **título** do documento — um só |
| texto entre o `#` e o primeiro `##` | o capítulo de **abertura** |
| `##` | um **capítulo** do livro |
| `###` | uma **seção** |
| `####` | uma **subseção** |
| ```` ```bash ```` | comando **para digitar** — o sandbox executa |
| ```` ```console ```` | **saída** do comando — o sandbox não executa |
| `<!-- ... -->` | comentário de edição — **não sai no PDF** |

Um comando por bloco. Quem copia dois comandos juntos não sabe qual falhou.

### 3. Testar

```bash
python3 tools/sandbox.py --list
```

Mostra as imagens-base à mão. Qualquer outra que o motor consiga baixar também
serve.

```bash
python3 tools/sandbox.py --image ubuntu:24.04 --network \
  --from-doc documentation/docker/installation_2026-09-16.md \
  --continue-on-error
```

```console
== Transcript · ubuntu:24.04 ==

[01] FALHOU (127) lsb_release -a
     | bash: line 6: lsb_release: command not found

[02] ok        dpkg --print-architecture
     | amd64

2 step(s): 1 ok, 1 failed, 0 never ran.
A failed step is a step that cannot be published as written.
```

Este é o retorno que justifica a ferramenta inteira: `lsb_release` **não existe**
na imagem limpa do Ubuntu 24.04. Um tutorial que começa por ele falha no primeiro
comando, na máquina de quem confiou nele. Corrija o documento — não o teste.

Sem `--network` o contêiner não alcança a rede, e instalar qualquer coisa falha.
Isso é proposital: o teste que não precisa de rede roda isolado.

### 4. Publicar

```bash
python3 tools/publish-doc.py docker --ai-model "Claude Opus 5"
```

```console
Software: /home/voce/tutorial-factory/documentation/docker
Brand   : sua-marca (pointer)
Preparing the brand theme...
  fonts: the brand's, installed system-wide

== Manual de instalação ==
  source: installation_2026-09-16.md
  10 chapter(s) from 10 section heading(s)

== Manual de uso ==
  source: manual_2026-09-16.md
  13 chapter(s) from 13 section heading(s)

== Result ==
  Manual de instalação:  installation_2026-09-16.md · installation_2026-09-16.tex · 26 page(s)
  Manual de uso:         manual_2026-09-16.md · manual_2026-09-16.tex · 32 page(s)
  Theme:                 /home/voce/tutorial-factory/documentation/docker/tema
```

### 5. Conferir

```bash
ls documentation/docker/
```

```console
installation_2026-09-16.md   manual_2026-09-16.md   LEIA-ME.md
installation_2026-09-16.tex  manual_2026-09-16.tex  tema/
installation_2026-09-16.pdf  manual_2026-09-16.pdf
```

Abra os dois PDFs. A capa traz a marca, o título, a peça, o autor e orientador, e
o crédito ao agente de IA. O sumário leva às páginas certas.

O `.tex` compila sozinho:

```bash
cd documentation/docker && xelatex installation_2026-09-16.tex
```

Duas ou três vezes — o sumário só fecha da segunda passagem em diante. É isso que
faz do `.tex` uma entrega de verdade, e não um subproduto.

---

## Republicar

Mudou o `.md`? Republique. Um PDF desatualizado é pior que um PDF ausente: ele
mente com aparência de pronto.

```bash
python3 tools/publish-doc.py docker            # os dois documentos
python3 tools/publish-doc.py docker --piece manual
```

Para descobrir o que ficou para trás em toda a documentação:

```bash
python3 tools/publish-all.py --check
```

```console
== 3 software(s) ==
  ok  docker                         58 página(s)
  !!  nginx                          31 página(s)   Manual de uso: nunca escrito
  !!  postgresql-17                  74 página(s)   Manual de instalação: PDF mais antigo que o .md — republique

Complete: 1/3 · 163 page(s) in total
```

---

## Atualize o catálogo

Uma linha em [`INDEX.md`](../INDEX.md), com o software, a edição, o ambiente
testado, as páginas e o que o documento cobre. É o único registro que sobrevive
ao clone de outra pessoa — `documentation/` não é versionado.

---

## Quando alguma coisa der errado

Mensagens de erro literais, causa e correção: [`08-problemas.md`](08-problemas.md).
