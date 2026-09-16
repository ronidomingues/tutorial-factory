# 01 · Instalação

Pôr a máquina em condição de **publicar** (gerar os PDFs) e de **testar** (rodar
os comandos documentados). São duas condições diferentes, e a segunda é a que
mais gente esquece.

---

## O que a fábrica exige

| Peça | Para quê | Sem ela |
|---|---|---|
| **Python 3.8+** | os programas em `tools/` | nada funciona |
| **TeX Live com XeLaTeX** | compilar os PDFs | você recebe o `.md` e o `.tex`, o `.pdf` fica pendente |
| **`latexmk`** | conduzir o motor e fechar o sumário | o md2book roda o motor direto, em três passagens |
| **`poppler-utils`** (`pdfinfo`) | contar páginas | os relatórios mostram `0 página(s)` |
| **Docker ou Podman** | **testar os comandos documentados** | o documento sai por pesquisa, não por verificação |

Não há `pip install`. Não há Pandoc. Não há dependência de rede para publicar —
só para testar, e só porque instalar qualquer coisa exige rede.

---

## Diagnóstico primeiro

Antes de instalar seja lá o que for, pergunte à própria fábrica:

```bash
python3 tools/publish-doc.py --doctor
```

```console
Brand kit: /home/voce/sua-marca (pointer)
  latex      ok       /home/voce/sua-marca/latex
  templates  ok       /home/voce/sua-marca/md2book
  ...
Docs     : /home/voce/tutorial-factory/documentation (default)  — folder does not exist yet

  md2book        ok       /usr/bin/python3 .../tools/md2book/md2book.py
  brand kit      ok       /home/voce/sua-marca (pointer)
  brand fonts    ok       /home/voce/sua-marca/fonts
  xelatex        ok       /usr/bin/xelatex
  latexmk        ok       /usr/bin/latexmk
  pdfinfo        ok       /usr/bin/pdfinfo
  docker/podman  ok       /usr/bin/docker

This machine can publish documentation on its own.
```

Cada linha `MISSING` tem a correção na tabela acima e o comando abaixo.

---

## Linux — Debian, Ubuntu e derivados

```bash
sudo apt update
```

Atualiza a lista de pacotes. Sem isso, o passo seguinte pode não achar nada.

```bash
sudo apt install -y texlive-xetex texlive-latex-extra texlive-lang-portuguese \
                    latexmk poppler-utils
```

Instala o LaTeX, o condutor e o `pdfinfo`. São cerca de **1,5 GB**; em máquina
com pouco espaço, ver *Sem instalar LaTeX*, abaixo.

```bash
sudo apt install -y podman
```

Instala o motor de contêiner. **Podman é o recomendado aqui**: roda sem daemon e
sem privilégio de root, que é exatamente o que um contêiner descartável de teste
precisa. Docker serve igual — o `sandbox.py` usa o que encontrar, nesta ordem:
Docker, depois Podman.

### Verificar

```bash
xelatex --version
```

```console
XeTeX 3.141592653-2.6-0.999995 (TeX Live 2023/Debian)
```

```bash
podman --version
```

```console
podman version 4.9.3
```

---

## Linux — Fedora, RHEL, Rocky, Alma

```bash
sudo dnf install -y texlive-xetex texlive-collection-latexextra \
                    texlive-collection-langportuguese latexmk poppler-utils podman
```

O `podman` já vem instalado em boa parte das versões recentes do Fedora; o
comando acima não faz mal se já estiver lá.

---

## Linux — Arch

```bash
sudo pacman -S --needed texlive-xetex texlive-latexextra texlive-langportuguese \
                        texlive-binextra poppler podman
```

No Arch, o `latexmk` vem dentro de `texlive-binextra`.

---

## macOS

```bash
brew install --cask mactex-no-gui
```

Instala o TeX Live completo sem os aplicativos gráficos (~4 GB). A variante
`basictex` é menor, mas quase sempre falta um pacote no meio da compilação —
resolver isso a cada erro custa mais tempo do que o download.

```bash
brew install poppler
```

```bash
brew install podman
podman machine init
podman machine start
```

No macOS o contêiner roda dentro de uma máquina virtual Linux — as duas últimas
linhas a criam e a ligam. É preciso repetir `podman machine start` depois de
reiniciar o computador.

> **Atenção ao testar no macOS.** O contêiner é **Linux**, mesmo rodando em um
> Mac. Ele verifica o capítulo de Linux do seu documento, não o de macOS. O
> caminho do macOS precisa ser testado na própria máquina — e o documento deve
> dizer isso.

---

## Windows

O caminho recomendado é o **WSL2**, e não a instalação nativa: a fábrica é feita
de programas de linha de comando, e o contêiner de teste é Linux de qualquer
forma.

```powershell
wsl --install -d Ubuntu-24.04
```

Instala o WSL2 com o Ubuntu 24.04. Reinicie quando ele pedir, abra o Ubuntu pelo
menu Iniciar e **siga as instruções de Debian/Ubuntu deste documento, dentro
dele**.

O Docker Desktop para Windows se integra ao WSL2 e aparece como `docker` lá
dentro; com ele instalado, não é preciso o Podman.

> **Instalação nativa em Windows** — MiKTeX mais Strawberry Perl — funciona para
> publicar, mas não para testar, e exige ajustar caminhos em vários pontos. Se
> for esse o caso, use `--no-pdf` e compile os `.tex` onde houver LaTeX.

---

## Sem instalar LaTeX

Duas saídas legítimas:

**Gerar só o Markdown e o LaTeX.** O `.tex` sai autocontido e compila em
qualquer outra máquina:

```bash
python3 tools/publish-doc.py docker --no-pdf
```

**Compilar em contêiner.** Se a máquina tem Docker ou Podman mas não tem LaTeX:

```bash
podman run --rm -v "$PWD/documentation/docker:/doc" -w /doc \
  texlive/texlive:latest xelatex installation_2026-09-16.tex
```

O `.tex` já vem preparado para isso: o tema está em `tema/`, ao lado dele, e o
arquivo o encontra sozinho. Rode duas ou três vezes — o sumário só fecha da
segunda passagem em diante.

---

## Instalar o kit de marca

A fábrica não tem identidade própria e **recusa publicar sem uma**. Escolha um
dos caminhos:

```bash
# começar pelo pré-molde neutro que vem no repositório
python3 tools/sync-brand.py --from-template
```

```bash
# ou apontar para a sua marca, num repositório separado
git clone git@github.com:voce/sua-marca.git ~/sua-marca
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check
```

O contrato inteiro está em [`03-kit-de-marca.md`](03-kit-de-marca.md).

---

## Escolher onde a documentação é salva

```bash
echo ~/Documentos/documentacao > DOCUMENTATION_PATH
```

Uma linha, uma vez por máquina. Todos os programas leem esse arquivo, e ele é
ignorado pelo git — ele descreve **esta máquina**, não o projeto. Sem ele, a
documentação vai para `documentation/`, dentro do repositório, que já está no
`.gitignore`.

```bash
python3 tools/publish-doc.py --doctor | grep Docs
```

```console
Docs     : /home/voce/Documentos/documentacao (pointer)
```

`(pointer)` confirma que o arquivo foi lido. `(default)` significa que a máquina
ainda não escolheu.

---

## Confirmação final

```bash
python3 tools/publish-doc.py --doctor
```

Todas as linhas `ok`, e a mensagem final:

```console
This machine can publish documentation on its own.
```

Se `docker/podman` estiver `MISSING`, a máquina publica mas **não verifica** — e
o `--doctor` diz isso explicitamente. É uma condição de trabalho aceitável desde
que os comandos sejam testados em outro lugar e o documento diga onde.

Próximo passo: [`02-primeiro-tutorial.md`](02-primeiro-tutorial.md).
