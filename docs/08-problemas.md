# 08 · Problemas

Mensagens literais, causa e correção. Procure pelo texto que apareceu na sua
tela — as mensagens abaixo estão como saem, em inglês, porque é assim que os
programas falam.

---

## Publicação

### `ERROR: no documentation folder for 'X'.`

```console
ERROR: no documentation folder for 'inexistente'.
  Looked in: /home/voce/Documentos/documentacao
  Available: docker, nginx, postgresql-17
  The documentation root is set by the DOCUMENTATION_PATH pointer at the repository
  root, or by --docs <path>.
```

**Causa.** Não existe pasta com esse nome na raiz da documentação. Quase sempre é
uma das três: nome digitado diferente do nome da pasta (`postgres` × `postgresql-17`),
a raiz não é a que você pensa, ou a pasta ainda não foi criada.

**Correção.** A linha `Available:` lista o que existe. Se a pasta deveria existir,
confira a raiz:

```bash
python3 tools/publish-doc.py --doctor | grep Docs
```

Se a raiz estiver errada, corrija o ponteiro:

```bash
echo ~/Documentos/documentacao > DOCUMENTATION_PATH
```

Se a pasta não existe mesmo:

```bash
python3 tools/new-doc.py <software>
```

---

### `ERROR: no brand kit found.`

```console
ERROR: no brand kit found.
  Expected at: /home/voce/tutorial-factory/tools/course-factory-brand
  Install one (see docs/03-kit-de-marca.md) or pass --brand <path>.
  The repository ships a neutral pre-mold at .../course-factory-brand/template.
```

**Causa.** Nenhum kit no slot, nenhum `BRAND_PATH` válido, e o pré-molde também
não foi encontrado. A fábrica recusa publicar sem identidade — é proposital:
nunca sai um PDF meio-marcado.

**Correção.**

```bash
python3 tools/sync-brand.py --from-template     # começar pelo molde neutro
# ou
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check
```

---

### `ERROR: the brand kit at X does not meet the contract.`

```console
ERROR: the brand kit at /home/voce/sua-marca does not meet the contract.
  Missing: md2book/book.base.json, BRAND-MANUAL.md
  See docs/03-kit-de-marca.md.
```

**Causa.** A pasta tem o `latex/coursebook.sty` (o marcador), mas falta alguma
peça obrigatória.

**Correção.** A linha `Missing:` diz exatamente quais. Copie-as do pré-molde:

```bash
cp tools/course-factory-brand/template/md2book/book.base.json ~/sua-marca/md2book/
python3 tools/sync-brand.py --check
```

O contrato inteiro está em [`03-kit-de-marca.md`](03-kit-de-marca.md).

---

### `WARNING: X points at Y, which is not a brand kit — ignoring.`

**Causa.** O `BRAND_PATH` aponta para uma pasta que não tem `latex/coursebook.sty`.
Caminho errado, ou o repositório de marca ainda não foi clonado.

**Correção.** Confira o que está no arquivo e se o caminho existe:

```bash
cat tools/course-factory-brand/BRAND_PATH
ls "$(grep -v '^#' tools/course-factory-brand/BRAND_PATH | head -1)/latex/"
```

> **Isto é um aviso, não um erro** — a fábrica continua e cai no pré-molde. E é
> exatamente por isso que ele merece atenção: sem notá-lo, você publica material
> assinado por ninguém.

---

### `WARNING: publishing with the neutral pre-mold — this material is signed by nobody.`

**Causa.** Nenhum kit próprio foi instalado; a fábrica está usando o pré-molde.

**Correção.** Legítimo para experimentar. Antes de o PDF sair da sua máquina,
instale a sua identidade — ver [`03-kit-de-marca.md`](03-kit-de-marca.md).

---

### `WARNING: X has no `# ` title on the first line — using the file name.`

**Causa.** O documento não começa com um `#`. O publicador usa o nome do arquivo
como título, e a capa fica com `installation 2026-09-16`.

**Correção.** A primeira linha do `.md` tem de ser o título:

```markdown
# Instalação do Docker Engine — Ubuntu 24.04 LTS, do zero
```

O travessão separa título de subtítulo na capa.

---

### `Manual de uso: not written yet — expected manual_AAAA-MM-DD.md`

**Causa.** Só uma das duas peças existe. Não é erro — é relatório.

**Correção.** Escreva a outra, ou publique só a que existe:

```bash
python3 tools/publish-doc.py docker --piece installation
```

---

### `WARNING: the PDF for X was not produced — see the LaTeX log at ...`

**Causa.** O LaTeX falhou. Quase sempre: falta um pacote do TeX Live, ou o
documento tem um caractere que o motor não desenha.

**Correção.** Publique mantendo o rascunho e leia o log:

```bash
python3 tools/publish-doc.py docker --keep-build
grep -E "^!|LaTeX Error" documentation/docker/.build/*/out/main.log | head -20
```

Faltando pacote, no Debian/Ubuntu:

```bash
sudo apt install texlive-latex-extra texlive-lang-portuguese
```

---

### `ERROR: md2book not found.`

**Causa.** A cópia embarcada sumiu de `tools/md2book/` — clone incompleto, ou
alguém apagou.

**Correção.**

```bash
git checkout tools/md2book
# ou, de um checkout do repositório do md2book:
python3 tools/sync-brand.py --md2book ~/md2book
```

---

### O PDF saiu, mas o sumário aponta para as páginas erradas

**Causa.** Você compilou o `.tex` à mão, uma vez só. O sumário do LaTeX só fecha
da segunda passagem em diante.

**Correção.**

```bash
cd documentation/docker
xelatex installation_2026-09-16.tex
xelatex installation_2026-09-16.tex
```

O `publish-doc.py` já faz isso; o problema só aparece na compilação manual.

---

### O PDF saiu com **um capítulo só**

**Causa.** O documento não tem nenhum `##`. Cada `##` vira um capítulo; sem eles,
o documento inteiro é um capítulo, e o sumário tem uma linha.

**Correção.** Estruture o `.md` com `##` para cada capítulo e `###` para as
seções. A gramática inteira está em [`04-arquitetura.md`](04-arquitetura.md)
§ *A divisão em capítulos*.

---

### O texto do meu comentário `<!-- -->` apareceu no PDF

**Não deveria** — comentários HTML fora de blocos de código são removidos. Se
apareceu, ele estava **dentro** de uma cerca de código, e ali é conteúdo.

---

### Metade do documento sumiu do PDF

**Causa.** Uma cerca de código que abre e não fecha. Tudo depois dela vira código,
inclusive os títulos.

**Correção.** Conte as cercas:

```bash
grep -c '^```' documentation/docker/installation_2026-09-16.md
```

Número **ímpar** significa cerca aberta. Procure a última:

```bash
grep -n '^```' documentation/docker/installation_2026-09-16.md | tail -5
```

> Cerca com até três espaços de recuo conta como cerca (regra do CommonMark);
> com quatro, é bloco indentado. Se você escreveu ```` ``` ```` recuado dentro de
> um texto explicativo, recue com quatro espaços ou ponha dentro de um bloco de
> código de verdade.

---

### As fontes saíram erradas

```console
WARNING: brand fonts not found at X — the material will come out in DejaVu, off-identity.
```

**Causa.** O kit declara arquivos de fonte que não estão lá.

**Correção.** Se as famílias estão instaladas no sistema:

```bash
fc-list : family | tr ',' '\n' | grep -i "Inter"
python3 tools/publish-doc.py docker --fonts system
```

Se não estão, e o kit tem os arquivos, force a cópia:

```bash
python3 tools/publish-doc.py docker --fonts folder
```

---

## Teste em contêiner

### `ERROR: no container engine found.`

```console
ERROR: no container engine found. Install Docker or Podman, or verify the steps
on a real machine and say so in the document.
  Debian/Ubuntu: sudo apt install podman
```

**Causa.** Nem Docker nem Podman no `PATH`.

**Correção.** Instale um deles — ver [`01-instalacao.md`](01-instalacao.md). Ou
teste em máquina real e **declare no documento** onde foi testado.

---

### `ERROR: --engine podman, but podman is not on the PATH.`

**Causa.** Você pediu um motor específico e ele não existe aqui. O programa
**não** cai no outro de propósito: rodar o teste em um lugar que você não
escolheu, e em silêncio, seria pior.

**Correção.** Instale o motor pedido, ou omita `--engine`.

---

### `The container did not run the steps — nothing was tested.`

```console
The container did not run the steps — nothing was tested.
Unable to find image 'nao-existe-mesmo:99' locally
docker: Error response from daemon: pull access denied for nao-existe-mesmo...
```

**Causa.** O contêiner nem chegou a rodar o roteiro: imagem inexistente, sem
acesso ao registry, daemon parado, ou `--timeout` estourado.

**Correção.** Confira o nome da imagem em `--list`, e se o motor está de pé:

```bash
docker info | head -5      # ou: podman info | head -5
```

Atrás de proxy, o `docker pull` precisa do proxy configurado no **daemon**, não
só no shell.

---

### Todos os passos falham com `command not found: sudo`

**Causa.** O repassador de `sudo` foi desligado com `--no-sudo-shim`, ou a imagem
não roda como root.

**Correção.** Retire o `--no-sudo-shim`. A imagem-base roda como root e não traz
`sudo`; como `sudo cmd` executado pelo root **é** `cmd`, o repassador permite
testar os comandos exatamente como estão escritos.

---

### Toda instalação falha com `Temporary failure resolving` ou `403 Forbidden`

**Causa.** O contêiner está sem rede, ou atrás de um proxy que o bloqueia.

**Correção.** Sem `--network` o contêiner não alcança a rede — isso é o padrão, e
é proposital:

```bash
python3 tools/sandbox.py --image ubuntu:24.04 --network --from-doc <documento>
```

Se mesmo com `--network` o `apt` responde `403 Forbidden` ou "not signed", o
bloqueio é da rede da máquina, não do contêiner. Teste em outra rede, configure o
proxy no motor de contêiner, ou verifique em máquina real — e **diga no documento
onde foi verificado**.

---

### O passo `cd` "não funciona"

**Causa.** Funciona — cada comando roda na mesma sessão de shell, e o `cd`
persiste. Se não persistiu, o comando anterior falhou e, sem
`--continue-on-error`, a execução parou.

**Correção.** Leia a transcrição de cima para baixo: o primeiro `FALHOU` é a
causa; o resto é consequência.

---

### Passos de outra distro falham no meio do relatório

**Causa.** `--from-doc` roda **todos** os blocos ```` ```bash ```` do documento,
inclusive os do capítulo de outro sistema operacional.

**Correção.** Duas saídas:

```bash
# ver tudo, sabendo o que era de outro sistema
python3 tools/sandbox.py --image ubuntu:24.04 --network \
  --from-doc <documento> --continue-on-error

# ou extrair só os comandos daquele capítulo
python3 tools/sandbox.py --image fedora:41 --network --script /tmp/passos-fedora.sh
```

A segunda dá um relatório limpo, e vale a pena quando o documento cobre três
sistemas.

---

## Destino e ponteiros

### A documentação foi parar no lugar errado

```bash
python3 tools/publish-doc.py --doctor | grep Docs
```

```console
Docs     : /home/voce/tutorial-factory/documentation (default)
```

O que está entre parênteses diz **quem decidiu**:

| Marca | Significa |
|---|---|
| `(explicit)` | veio de `--docs` |
| `(environment)` | veio de `TUTORIAL_FACTORY_DOCS` |
| `(pointer)` | veio do `DOCUMENTATION_PATH` |
| `(default)` | ninguém decidiu — está em `documentation/` |

**Correção.**

```bash
echo ~/Documentos/documentacao > DOCUMENTATION_PATH
```

O material já escrito não se move sozinho — mova a pasta à mão e republique.

---

### `DOCUMENTATION_PATH` existe e mesmo assim diz `(default)`

**Causa.** O arquivo está em outro lugar (ele tem de estar na **raiz do
repositório**), ou a única linha dele é um comentário.

**Correção.**

```bash
ls -la DOCUMENTATION_PATH
cat DOCUMENTATION_PATH
```

Linhas em branco e linhas começadas com `#` são comentário. Precisa haver **uma
linha com um caminho**.

---

### A documentação apareceu no `git status`

**Causa.** Ela está dentro do repositório com um nome que não é `documentation/`
nem `documentacao/`.

**Correção.** Acrescente a pasta ao `.gitignore`, ou — melhor — mande-a para fora
do repositório com o ponteiro. A fábrica é pública; o material é de quem o gerou.

---

## Quando nada acima serve

```bash
python3 tools/publish-doc.py --doctor     # o que esta máquina tem e não tem
python3 tools/sync-brand.py --check       # o kit cumpre o contrato?
python3 tools/sync-brand.py --colors      # qual cor está vencendo
python3 tools/publish-all.py --check      # o que está faltando ou desatualizado
python3 tools/publish-doc.py X --keep-build   # e leia o log do LaTeX
```

Essas cinco linhas respondem a maior parte do que dá errado.
