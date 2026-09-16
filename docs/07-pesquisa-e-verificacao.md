# 07 · Pesquisa e verificação

De onde vem a informação, e como ela deixa de ser um palpite.

> Um tutorial cujos comandos nunca foram executados é um palpite em tipografia
> bonita, e o leitor não consegue perceber a diferença.

---

## Parte 1 · A pesquisa

### As quatro fontes obrigatórias

Antes de escrever a primeira linha, para **aquele** sistema e **aquela** versão:

| # | Fonte | O que se busca lá |
|---|---|---|
| 1 | **A documentação oficial do projeto** | a página de instalação daquele sistema operacional, naquela versão |
| 2 | **O repositório oficial** | releases, `CHANGELOG`, notas da versão — a versão atual de verdade, e o que quebrou nela |
| 3 | **O gerenciador de pacotes que você vai mandar usar** | o nome exato do pacote e a versão que ele entrega **hoje** naquela distro |
| 4 | **Os problemas conhecidos** | issues abertas, avisos de depreciação, incompatibilidade com a versão do sistema |

A fonte 3 é a que mais gente pula, e é onde mora o erro mais caro: **o nome do
pacote muda entre distros e a versão do repositório oficial costuma estar
atrás.** `docker.io` no Ubuntu não é `docker-ce` do repositório do Docker, e a
diferença aparece três capítulos depois, quando um comando não existe.

### As regras

- **Nunca invente.** Nem versão, nem nome de pacote, nem flag, nem URL, nem saída
  de comando, nem mensagem de erro. Se não conferiu, não escreve.
- **Nada de "provavelmente".** Informação não encontrada se declara como não
  encontrada, com o que fazer a respeito. É mais útil que um palpite plausível.
- **Toda fonte entra no documento**, com URL e **data de consulta**, no capítulo
  final.
- **Desconfie do que está velho.** Um blog de 2021 sobre instalação é história,
  não instrução. Prefira a fonte primária e confira a data de publicação.
- **Confira a combinação, não os componentes.** É o par *versão do software* ×
  *versão do sistema* que quebra, não cada um isoladamente.
- **Preço, plano e licença têm data.** Preço sem data de consulta é
  desinformação.

### O capítulo de fontes

Todo documento termina com ele:

```markdown
## Fontes consultadas

- Documentação oficial do Docker, instalação no Ubuntu —
  <https://docs.docker.com/engine/install/ubuntu/> — consultado em 16/09/2026.
- Notas da versão 27.3.1 —
  <https://docs.docker.com/engine/release-notes/27/> — consultado em 16/09/2026.
- Pacote `docker-ce` no repositório oficial, série `noble` —
  consultado em 16/09/2026; versão entregue: 5:27.3.1-1~ubuntu.24.04~noble.
```

Sem URL, não é fonte. Sem data, não é verificável.

---

## Parte 2 · A verificação

### O que o sandbox faz

```bash
python3 tools/sandbox.py --image ubuntu:24.04 --network \
  --from-doc documentation/docker/installation_2026-09-16.md \
  --continue-on-error --report /tmp/verificacao-docker.md
```

Ele extrai os blocos ```` ```bash ```` do documento, **na ordem em que estão
escritos**, e executa cada um em um contêiner descartável, registrando código de
saída e saída real.

Blocos ```` ```console ```` são **saída**, não entrada: ele não os executa, porque
é isso que o leitor deve *ver*, não digitar. Essa distinção é a razão de o preset
exigir a linguagem declarada em toda cerca.

### O que fazer com o resultado

| Aconteceu | O que fazer |
|---|---|
| **Passo falhou** | o documento está errado. Corrija o documento, não o teste. |
| **Saída diferente da que você escreveu** | use a saída real. Sempre. |
| **Versão diferente da que você pesquisou** | a ficha do documento passa a dizer a versão que realmente saiu |
| **Passo que não dá para testar aqui** | **declare no documento**, nominalmente |

Um exemplo real, do primeiro teste desta fábrica:

```console
[01] FALHOU (127) lsb_release -a
     | bash: line 6: lsb_release: command not found
```

`lsb_release` **não existe** na imagem limpa do Ubuntu 24.04. Um tutorial que
começa por ele falha no primeiro comando, na máquina de quem confiou nele. Era um
comando plausível, pesquisável, documentado em dezenas de blogs — e errado.
Nenhuma quantidade de pesquisa teria pego isso; um teste pegou em quatro
segundos.

### O que o contêiner não alcança

Ele é Linux, sem interface gráfica, sem hardware específico, sem kernel próprio.
Não verifica:

- instalador gráfico (`.dmg`, `.msi`, assistente de instalação);
- caminho exclusivo de **macOS** ou de **Windows nativo**;
- módulo de kernel, driver, aceleração de GPU;
- comportamento que dependa de systemd em máquina real (o contêiner não tem PID 1
  de verdade, salvo configuração específica);
- rede corporativa, proxy com certificado interno, registry espelhado;
- hardware: placa, dispositivo USB, quantidade real de memória.

**Nada disso é motivo para não testar o resto.** A regra é: teste o que der, e
declare nominalmente o que não deu.

### A declaração de verificação

Todo manual de instalação traz, logo abaixo da ficha, um bloco que diz onde os
comandos rodaram, em que data, e o que **não** pôde ser verificado:

```markdown
> **Como este documento foi verificado.** Todos os comandos do capítulo 3 foram
> executados em um contêiner `ubuntu:24.04` limpo, em 16/09/2026, e a saída
> mostrada é a real. O capítulo 7 (outros sistemas) **não foi testado**: macOS e
> Windows não rodam em contêiner Linux, e os comandos vieram da documentação
> oficial de cada um, consultada na mesma data.
```

Esse bloco é obrigatório. Sem ele, o leitor não tem como calibrar a confiança — e
"testado" vira uma palavra sem conteúdo.

### Testar em mais de um sistema

Cada capítulo de sistema operacional pede a sua imagem:

```bash
python3 tools/sandbox.py --image ubuntu:24.04   --network --from-doc <doc>
python3 tools/sandbox.py --image debian:12      --network --from-doc <doc>
python3 tools/sandbox.py --image fedora:41      --network --from-doc <doc>
```

O `--from-doc` roda **todos** os blocos do documento, inclusive os de outra
distro — que naturalmente falham na imagem errada. Duas saídas:

- use `--continue-on-error` e leia a transcrição sabendo quais passos eram de
  outro sistema;
- ou extraia os comandos daquele capítulo para um `--script` e rode só eles.

A segunda dá um relatório limpo, e é a que vale a pena quando o documento cobre
três sistemas.

### O projeto do manual de uso também é testado

O capítulo do projeto completo constrói uma aplicação que **roda**. Se ela não
roda no contêiner, ela não vai para o documento.

```bash
python3 tools/sandbox.py --image python:3.12 --network \
  --script /tmp/passos-do-projeto.sh
```

---

## O limite honesto

A fábrica **não verifica fato por você.** Ela força a execução dos comandos e
exige a fonte com data. Mas:

- se o modelo entendeu errado uma nota de release, o PDF sai com o erro;
- se a documentação oficial está desatualizada, o documento herda o problema;
- se o passo não pôde ser testado, "não testado" é a única coisa honesta a
  escrever;
- um comando pode passar no contêiner e falhar na máquina do leitor por uma
  diferença que o contêiner não tem — e isso não é um defeito do teste, é o
  motivo de a declaração de verificação existir.

A responsabilidade editorial é de quem orienta. É o nome dele que está na capa,
em `BRAND_OWNER`, junto com o do agente.

---

## Checklist

**Pesquisa**
- [ ] Documentação oficial do projeto, para aquele sistema e aquela versão.
- [ ] Repositório oficial: releases e notas da versão.
- [ ] O nome e a versão do pacote que **aquela distro entrega hoje**.
- [ ] Problemas conhecidos e avisos de depreciação.
- [ ] Toda fonte com URL e data no capítulo final.

**Verificação**
- [ ] `--from-doc` rodou contra a imagem do sistema documentado.
- [ ] Nenhum passo falhando — ou, se falha, ela está documentada como esperada.
- [ ] Toda saída mostrada no documento é a **real**.
- [ ] A versão na ficha é a que realmente saiu no teste.
- [ ] A declaração de verificação existe, com imagem, data e o que não foi testado.
- [ ] O projeto do manual de uso roda.
