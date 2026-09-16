# 06 · A entrevista

A primeira etapa, e a que mais distingue esta fábrica de um assistente comum.

---

## Por que ela existe

*"Como instalar Docker"* tem, no mínimo, estas respostas certas:

| Ambiente | O comando de verdade |
|---|---|
| Ubuntu 24.04, x86_64, com `sudo` | repositório oficial APT, chave GPG, `docker-ce` |
| Ubuntu 24.04, sem `sudo` | não instala — usa Docker rootless ou um host remoto |
| Debian 12 | quase igual ao Ubuntu, com outro caminho de repositório |
| Fedora 41 | `dnf-plugins-core`, repositório próprio, `docker-ce` |
| Arch | `pacman -S docker`, e o serviço não sobe sozinho |
| macOS, Apple Silicon | Docker Desktop ou Colima — e não há daemon nativo |
| Windows 11 | Docker Desktop com backend WSL2 |
| Dentro do WSL2 | o do Windows, ou um daemon dentro da distro — decisão não trivial |
| Servidor sem interface gráfica | Docker Engine, nunca Desktop |
| Rede corporativa com proxy | tudo acima, mais três arquivos de configuração |

**Onze dessas respostas estão erradas para quem perguntou.** Responder sem
perguntar é escolher uma ao acaso e esperar acertar. A entrevista é o que troca
sorte por informação.

E o custo é assimétrico. Perguntar custa uma mensagem. Não perguntar custa uma
instalação que falha no meio — depois que a pessoa já mexeu na máquina.

---

## O mínimo obrigatório

Seis perguntas. Faça **todas de uma vez**, em bloco, nunca uma por mensagem.

| Pergunta | Por que muda o documento |
|---|---|
| **Qual sistema operacional e versão?** | nome de pacote, gerenciador, caminho de configuração e método recomendado mudam todos |
| **Qual arquitetura?** (x86_64, ARM64/Apple Silicon) | muitos projetos têm binário só para uma; alguns exigem compilar |
| **Qual versão do software?** | a última estável, uma LTS, ou uma fixa por causa de um projeto existente |
| **Para que vai usar?** | estudo local, servidor de produção, CI, desenvolvimento — muda o que se instala e como se configura |
| **Tem acesso administrativo?** (`sudo`, admin) | sem ele o caminho é outro: instalação por usuário, gerenciador de versões, contêiner |
| **Está atrás de proxy ou rede corporativa?** | certificado interno e registry espelhado quebram o caminho padrão |

### Como fazer o bloco

Ofereça as respostas prováveis como opções, e diga o que acontece se a pessoa
não souber:

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

A última linha é importante: ela dá saída a quem não quer ser entrevistado, sem
que o documento saia sem ambiente definido.

---

## As perguntas que dependem do caso

Faça **só as que mudam o material**. Perguntar por simetria é ruído.

| Se… | Pergunte |
|---|---|
| for Windows | nativo ou WSL2 — e a pessoa sabe qual está usando? |
| for Linux | qual distro e qual gerenciador: `apt`, `dnf`, `pacman`, `zypper` |
| for macOS | tem Homebrew instalado? |
| for servidor | vai expor na rede, precisa de TLS, vai rodar como serviço? |
| houver instalação anterior | qual versão está lá, e pode ser removida? |
| o software tiver versões conflitantes | precisa conviver com outra versão na mesma máquina? |
| houver banco de dados envolvido | dados existentes a preservar? |
| for ferramenta de linguagem | qual runtime já está instalado, e em que versão? |

---

## Quando **não** perguntar

Esta metade é tão importante quanto a outra. Uma entrevista que não termina é
uma entrevista que impede o trabalho.

- **O usuário já respondeu.** Não pergunte de novo, e não peça confirmação do que
  ele acabou de dizer. Se ele escreveu "no meu Ubuntu 24.04", o sistema está
  decidido.
- **A resposta não muda o documento.** Se o procedimento é idêntico em `x86_64` e
  em ARM, não pergunte a arquitetura.
- **O usuário disse "escolhe por mim" ou "não sei".** Escolha o caminho mais
  comum, **diga qual escolheu e por quê**, e siga. Não devolva a pergunta.
- **O pedido é genérico de propósito** — "documenta o nginx para o time". Cubra
  os três sistemas operacionais em capítulos separados e diga isso no topo do
  documento.
- **A informação está no contexto.** Se a conversa anterior, o repositório aberto
  ou um arquivo do projeto já dizem a versão do runtime, use-a e mencione de onde
  veio.
- **Já existe documentação daquele software nesta pasta.** Leia a ficha da edição
  anterior: o ambiente provavelmente é o mesmo, e a pergunta vira uma
  confirmação de uma linha.

Regra prática: **se você consegue prever a resposta com alta confiança e a
resposta errada é barata de corrigir, não pergunte.** Assuma, diga que assumiu, e
siga.

---

## O que fazer com as respostas

### 1. Vão para a ficha do documento

A tabela logo abaixo do título do manual de instalação. Quem lê precisa saber
para qual máquina aquilo foi escrito.

```markdown
| Campo | Valor |
|---|---|
| Sistema testado | Ubuntu 24.04.5 LTS (Noble Numbat), amd64 |
| Versão instalada | Docker Engine 27.3.1 |
| Método recomendado | repositório oficial APT |
| Data do teste | 16/09/2026 |
| Tempo estimado | 15 a 25 minutos |
| Precisa de `sudo` | sim |
| Precisa de conta ou cartão | não |
```

### 2. Decidem a imagem do teste

A resposta sobre o sistema operacional **é** o `--image` do sandbox:

```bash
python3 tools/sandbox.py --image ubuntu:24.04 --network --from-doc <documento>
```

Documentou Fedora? Teste em `fedora:41`. Documentou os três sistemas? Teste os
capítulos de Linux nos contêineres correspondentes e **declare** que macOS e
Windows não foram testados em contêiner.

### 3. Decidem o que entra e o que não entra

Uma resposta de "servidor de produção" acrescenta capítulos que "estudo local"
não precisa: serviço no `systemd`, TLS, usuário dedicado, limites de recurso,
log. E remove outros: instalador gráfico não tem lugar em servidor sem interface.

---

## A pergunta que não é sobre o software

Na **primeira vez** em que a fábrica roda numa máquina, há uma pergunta a mais:
**onde salvar a documentação.** Ela entra junto com o bloco da entrevista, e
nunca mais volta.

```bash
python3 tools/publish-doc.py --doctor | grep Docs
```

- `(pointer)`, `(environment)` ou `(explicit)` — já foi escolhido. Diga qual é,
  em uma linha, e siga.
- `(default)` e sem `DOCUMENTATION_PATH` na raiz — pergunte, **uma vez**:

  > **Onde salvar a documentação gerada?** Selecione uma opção ou cole o caminho.
  >
  > - `documentation/` — dentro do repositório (padrão; já está no `.gitignore`)
  > - `~/Documentos/documentacao` — fora do repositório, junto dos seus documentos
  > - *(outro)* — cole aqui o caminho

  ```bash
  echo "<caminho escolhido>" > DOCUMENTATION_PATH
  ```

> Perguntar **onde** não é perguntar **se**. Escrever a documentação continua
> sendo o trabalho pedido, sem autorização nenhuma.

---

## Exemplo de entrevista completa

**Usuário:** `como instalar o nginx`

**Agente:**

> Antes de escrever, seis perguntas — e uma que só faço uma vez por máquina.
>
> - **Sistema operacional e versão?**
> - **É servidor ou máquina de desenvolvimento?** (muda TLS, serviço e usuário dedicado)
> - **Vai servir site estático, proxy reverso, ou os dois?**
> - **Precisa de uma versão específica**, ou a que a distro entrega serve?
> - **Tem `sudo`?**
> - **Proxy corporativo?**
>
> E: **onde salvar a documentação gerada?** (`documentation/` aqui dentro, ou um
> caminho seu — pergunto só desta vez)
>
> Se preferir, "escolhe por mim" e eu sigo por Ubuntu 24.04, proxy reverso com
> TLS, versão da distro.

**Usuário:** `ubuntu 24.04 servidor, proxy reverso com https, versão da distro serve, tenho sudo, sem proxy. salva em ~/docs`

**Agente:** grava o ponteiro, pesquisa, testa em `ubuntu:24.04`, escreve os dois
documentos e publica. Não pergunta mais nada.

---

## O erro mais comum

Fazer a entrevista **e ignorar as respostas** — escrever o documento genérico de
sempre, com a ficha preenchida por cima. O sinal de que isso aconteceu é o
documento cobrir três sistemas operacionais com o mesmo peso quando a pessoa
disse qual era o dela.

O ambiente respondido ganha o corpo do documento, testado e verificado. Os outros
sistemas vão para **um capítulo próprio**, no fim, e o texto diz que são um
complemento — não o que foi verificado.
