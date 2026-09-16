# 05 · Referência da CLI

Todo programa, toda opção, o que cada uma faz. Cinco programas em `tools/`,
nenhuma dependência além do Python 3.

| Programa | Para quê |
|---|---|
| [`publish-doc.py`](#publish-docpy) | um software → `.md` + `.tex` + `.pdf` |
| [`new-doc.py`](#new-docpy) | abre a pasta e semeia os esqueletos |
| [`sandbox.py`](#sandboxpy) | roda os comandos documentados, de verdade |
| [`publish-all.py`](#publish-allpy) | manutenção em lote, e `--check` |
| [`sync-brand.py`](#sync-brandpy) | instala e confere o kit de marca |

---

## `publish-doc.py`

Transforma o Markdown de um software nos outros dois formatos, vestindo o kit de
marca instalado.

```bash
python3 tools/publish-doc.py <software> [opções]
python3 tools/publish-doc.py --doctor
```

O argumento aceita **o nome da pasta** (`docker`) ou **um caminho** completo.

### Opções

| Opção | Padrão | O que faz |
|---|---|---|
| `--piece {all,installation,manual}` | `all` | qual documento publicar |
| `--date AAAA-MM-DD` | a mais recente | publica a edição dessa data |
| `--docs <caminho>` | ponteiro, senão `documentation/` | a raiz da documentação |
| `--brand <caminho>` | o slot, senão o pré-molde | o kit de marca a usar |
| `--md2book <caminho>` | a cópia embarcada | outro md2book |
| `--doc-version <texto>` | `1.0` | o rótulo de versão impresso na capa |
| `--agent <texto>` | `Claude Code (Anthropic)` | o agente que pesquisou e escreveu |
| `--ai-model <texto>` | vazio | **o modelo** — passe sempre |
| `--advisor <nome>` | `BRAND_OWNER` do `brand.env` | autor e orientador |
| `--license <texto>` | `BRAND_COURSE_LICENSE` | a linha de licença |
| `--repo <texto>` | vazio | repositório de origem, nos créditos |
| `--note <texto>` | vazio | uma linha extra na capa |
| `--level <texto>` | `BRAND_DOC_LEVEL`, senão "do zero absoluto ao uso profissional" | a linha de nível na capa |
| `--opening-title <texto>` | `Apresentação` | o título do capítulo de abertura |
| `--fonts {auto,system,folder}` | `auto` | de onde vem a tipografia — ver abaixo |
| `--no-pdf` | — | gera só o LaTeX, sem compilar |
| `--keep-build` | — | mantém a pasta de rascunho e o log do LaTeX |
| `--doctor` | — | o que esta máquina tem e o que falta, e sai |

### `--fonts`

| Valor | Comportamento |
|---|---|
| `auto` | usa as fontes instaladas no sistema; se faltarem, copia para `tema/fontes/` |
| `system` | usa as instaladas, e **avisa** se não estiverem |
| `folder` | **sempre** copia para `tema/fontes/`, para a pasta viajar inteira |

`--fonts folder` é o modo certo para enviar a documentação a alguém: o `.tex`
compila na máquina do destinatário sem instalar fonte nenhuma.

### `--doctor`

```bash
python3 tools/publish-doc.py --doctor
```

Diz, em uma tela, se esta máquina **publica** sozinha — e, separadamente, se ela
**testa** o que documenta. São condições diferentes. Também imprime qual kit de
marca venceu e de onde a raiz da documentação foi decidida:

```console
Docs     : /home/voce/Documentos/documentacao (pointer)
```

`(pointer)` · `(environment)` · `(explicit)` · `(default)`.

### Exemplos

```bash
# os dois documentos, creditando o modelo
python3 tools/publish-doc.py docker --ai-model "Claude Opus 5"

# só o manual de uso
python3 tools/publish-doc.py docker --piece manual

# uma edição antiga, de propósito
python3 tools/publish-doc.py docker --date 2026-03-04

# máquina sem LaTeX: gera o .tex e compila em outro lugar
python3 tools/publish-doc.py docker --no-pdf

# a compilação falhou e você quer o log
python3 tools/publish-doc.py docker --keep-build
ls documentation/docker/.build/installation_2026-09-16/out/main.log
```

### Saída

| Arquivo | Escrito quando |
|---|---|
| `<peça>_<data>.tex` | sempre |
| `<peça>_<data>.pdf` | quando o LaTeX compila |
| `LEIA-ME.md` | sempre |
| `tema/` | sempre |

O `.md` **nunca é tocado**.

---

## `new-doc.py`

Abre a pasta de um software e deixa lá os dois esqueletos, datados de hoje.

```bash
python3 tools/new-doc.py <software> [opções]
```

| Opção | Padrão | O que faz |
|---|---|---|
| `--piece {all,installation,manual}` | `all` | qual esqueleto semear |
| `--date AAAA-MM-DD` | hoje | a data no nome dos arquivos |
| `--docs <caminho>` | ponteiro, senão `documentation/` | a raiz da documentação |

O nome vira `kebab-case`: `"PostgreSQL 17"` → `postgresql-17`.

**Nunca sobrescreve** um arquivo existente — ele diz `kept` e segue. Voltar a um
software depois de uma versão nova é escrever uma edição nova, com data nova.

```bash
python3 tools/new-doc.py "PostgreSQL 17"
```

```console
Folder: /home/voce/Documentos/documentacao/postgresql-17
  created  installation_2026-09-16.md
  created  manual_2026-09-16.md
```

---

## `sandbox.py`

Roda os comandos documentados em um contêiner descartável e relata o que
aconteceu de verdade.

```bash
python3 tools/sandbox.py --image <imagem> [o que rodar] [opções]
python3 tools/sandbox.py --list
```

### O que rodar — escolha uma forma, ou combine

| Opção | O que faz |
|---|---|
| `-c "<comando>"` | um comando; repita para mais, na ordem |
| `--script <arquivo>` | um arquivo com um comando por linha |
| `--from-doc <arquivo.md>` | **extrai os blocos ```` ```bash ```` do documento**, na ordem escrita |

`--from-doc` ignora blocos ```` ```console ````: eles são **saída**, não entrada —
é o que o leitor deve *ver*, não digitar. Também ignora linhas em branco e
comentários.

### Opções

| Opção | Padrão | O que faz |
|---|---|---|
| `--image <imagem>` | — | **obrigatório**; qualquer imagem que o motor baixe |
| `--report <arquivo.md>` | — | escreve a evidência em Markdown |
| `--engine {docker,podman}` | docker, depois podman | o motor de contêiner |
| `--network` | desligado | dá rede ao contêiner — **instalar exige** |
| `--privileged` | desligado | só para passos que realmente precisam |
| `--mount <host>[:<contêiner>]` | — | monta uma pasta, leitura e escrita |
| `--timeout <segundos>` | `1800` | desiste depois disso |
| `--continue-on-error` | desligado | segue depois de um passo que falha |
| `--no-sudo-shim` | desligado | não fornece o repassador de `sudo` |
| `--list` | — | as imagens-base à mão, e sai |

### O repassador de `sudo`

A imagem-base roda como root e **não traz `sudo`**. Sem isso, todo
`sudo apt install` de um tutorial honesto falharia por um motivo que nada tem a
ver com o tutorial. Como `sudo cmd` executado pelo root **é** `cmd`, o sandbox
instala um repassador de duas linhas e testa os comandos **exatamente como estão
escritos** — que é a única versão que vale testar.

`--no-sudo-shim` desliga, para quando você quer ver a falha que uma imagem sem
`sudo` produziria.

### Código de saída

| Código | Significa |
|---|---|
| `0` | todos os passos passaram |
| `1` | ao menos um passo falhou |
| `124` | estourou o `--timeout` |
| `125` | o motor de contêiner não conseguiu executar |

### Exemplos

```bash
# verificações rápidas, sem rede
python3 tools/sandbox.py --image ubuntu:24.04 \
  -c "dpkg --print-architecture" -c "cat /etc/os-release"

# uma instalação de verdade
python3 tools/sandbox.py --image debian:12 --network \
  -c "apt-get update" -c "apt-get install -y curl" -c "curl --version"

# o documento inteiro, com evidência gravada
python3 tools/sandbox.py --image ubuntu:24.04 --network \
  --from-doc documentation/docker/installation_2026-09-16.md \
  --continue-on-error --report /tmp/verificacao-docker.md

# o mesmo documento em outra distro, para conferir o capítulo dela
python3 tools/sandbox.py --image fedora:41 --network \
  --from-doc documentation/docker/installation_2026-09-16.md
```

---

## `publish-all.py`

Republica toda a documentação, ou relata o que está faltando. É manutenção, não
produção: um software por vez é o modo normal de trabalhar.

```bash
python3 tools/publish-all.py [opções]
```

| Opção | Padrão | O que faz |
|---|---|---|
| `--check` | — | **relata e não produz nada** |
| `--docs <caminho>` | ponteiro, senão `documentation/` | a raiz da documentação |
| `--piece {all,installation,manual}` | `all` | qual documento publicar |
| `--jobs <n>` | `4` | quantos softwares ao mesmo tempo |
| `--agent`, `--ai-model`, `--doc-version`, `--brand` | | repassados ao `publish-doc.py` |

### `--check`

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

Três pendências ele detecta: **peça nunca escrita**, **PDF ou `.tex` ausente**, e
**PDF mais antigo que o `.md`**. A terceira é a que importa: um PDF desatualizado
mente com aparência de pronto.

Sem `--check`, ele publica e grava `.publicacao.json` na raiz da documentação —
as contagens que mantêm o [`INDEX.md`](../INDEX.md) honesto.

```bash
# depois de trocar a marca
python3 tools/sync-brand.py --check && python3 tools/publish-all.py --jobs 6
```

---

## `sync-brand.py`

Instala, confere e atualiza o slot do kit de marca. Contrato completo em
[`03-kit-de-marca.md`](03-kit-de-marca.md).

```bash
python3 tools/sync-brand.py [ação] [opções]
```

| Ação | O que faz |
|---|---|
| *(nenhuma)* ou `--check` | confere o kit instalado contra o contrato |
| `--colors` | qual cor vence, e qual declaração virou letra morta |
| `--palette` | regenera `palette/tokens.{json,css}` a partir do `brand.env` |
| `--install <caminho>` | copia um kit daquela pasta para dentro do slot |
| `--from-template` | semeia o slot a partir do pré-molde neutro |
| `--md2book <caminho>` | atualiza o md2book embarcado de um checkout dele |

| Opção | O que faz |
|---|---|
| `--brand <caminho>` | inspeciona esse caminho, em vez do slot |
| `--dry-run` | diz o que mudaria, e não muda nada |
| `--force` | sobrescreve um kit já instalado |

Ele **nunca escreve na origem** e nunca toca em documentação publicada.

```bash
python3 tools/sync-brand.py --check
python3 tools/sync-brand.py --colors
python3 tools/sync-brand.py --install ~/minha-marca --dry-run
python3 tools/sync-brand.py --md2book ~/md2book
```

---

## Variáveis de ambiente

Existem, mas **prefira os ponteiros** — uma variável precisa estar definida em
todo shell, inclusive no que o agente abre.

| Variável | Equivale a |
|---|---|
| `TUTORIAL_FACTORY_DOCS` | o ponteiro `DOCUMENTATION_PATH` |
| `TUTORIAL_FACTORY_BRAND` | o ponteiro `BRAND_PATH` |
| `COURSE_FACTORY_BRAND` | idem — uma variável só para as duas fábricas |
| `MD2BOOK` | um md2book fora do repositório |

---

## Códigos de saída

| Programa | `0` | `1` | `2` |
|---|---|---|---|
| `publish-doc.py` | produziu algo | nada foi produzido | erro de uso, ou kit de marca inválido |
| `new-doc.py` | criou ou preservou | — | erro de uso |
| `sandbox.py` | todos os passos passaram | algum falhou | erro de uso, ou sem motor de contêiner |
| `publish-all.py` | tudo publicou | alguma publicação falhou | — |
| `sync-brand.py` | contrato satisfeito | contrato não satisfeito | erro de uso |
