# Documentação — Tutorial Factory

A fábrica tem quatro peças e uma regra. As peças: um **preset** que diz ao agente
de IA o que perguntar, pesquisar, testar e escrever; um **contêiner descartável**
onde os comandos documentados rodam de verdade; um **conversor** que transforma
Markdown em livro; e um **kit de marca** que decide como isso se parece. A regra:
o Markdown é a fonte da verdade, e a publicação nunca o altera.

Leia nesta ordem se está começando. Consulte fora de ordem depois.

| # | Documento | Para quê |
|---|---|---|
| 00 | [O prompt fundador](00-prompt-fundador.md) | **por que este projeto existe** — o pedido original, revisado, e as decisões que ele não tomou |
| 01 | [Instalação](01-instalacao.md) | pôr a máquina em condição de publicar e de testar |
| 02 | [Primeiro tutorial](02-primeiro-tutorial.md) | do repositório vazio aos seis arquivos na tela |
| 03 | [Kit de marca](03-kit-de-marca.md) | **instalar a sua identidade** — o contrato, o pré-molde, a troca |
| 04 | [Arquitetura](04-arquitetura.md) | como o framework funciona por dentro, e por que assim |
| 05 | [Referência da CLI](05-referencia-cli.md) | todo comando, toda opção, o que cada uma faz |
| 06 | [A entrevista](06-entrevista.md) | o que perguntar, por que, e quando **não** perguntar |
| 07 | [Pesquisa e verificação](07-pesquisa-e-verificacao.md) | de onde vem a informação e como ela é testada |
| 08 | [Problemas](08-problemas.md) | mensagens de erro literais, causa e correção |

---

## O caminho curto

Já tem Python e LaTeX na máquina? Então são cinco linhas:

```bash
git clone <este-repositório> tutorial-factory && cd tutorial-factory
python3 tools/publish-doc.py --doctor          # o que falta nesta máquina
python3 tools/sync-brand.py --from-template    # começar pela marca-molde
python3 tools/new-doc.py docker                # abre a pasta e os esqueletos
python3 tools/publish-doc.py docker            # e olhe os PDFs
```

O `--doctor` responde a pergunta que importa antes de qualquer outra: **esta
máquina publica um documento sozinha?** E diz, separadamente, se ela consegue
**testar** o que documenta — que é uma condição diferente, e mais importante.

---

## Vocabulário

Termos que aparecem em todos os documentos, definidos uma vez.

| Termo | O que é |
|---|---|
| **Software** | a ferramenta documentada, e o nome da pasta em `documentation/` |
| **Peça** | um dos dois documentos: **instalação** (`installation_*`) ou **uso** (`manual_*`) |
| **Edição** | a data no nome do arquivo: `installation_2026-09-16.md` |
| **Preset** | o `CLAUDE.md` da raiz: a persona, as seis etapas e a régua que o agente segue |
| **Entrevista** | a etapa 1: descobrir SO, versão, arquitetura e objetivo antes de escrever |
| **Sandbox** | o contêiner descartável onde os comandos documentados são executados |
| **Kit de marca** | a pasta que carrega a identidade aplicada na publicação |
| **Slot** | `tools/course-factory-brand/` — onde o kit de marca é instalado |
| **Pré-molde** | o kit neutro que vem no repositório, em `.../course-factory-brand/template/` |
| **Ponteiro** | um arquivo de uma linha que diz à máquina onde algo mora: `DOCUMENTATION_PATH`, `BRAND_PATH` |
| **md2book** | o conversor Markdown → LaTeX → PDF, embarcado em `tools/md2book/` |

---

## O que a fábrica não faz

Honestidade antecipada poupa uma tarde:

- **Não verifica fato por você.** Ela força a execução dos comandos e exige a
  fonte com data. Se o modelo entendeu errado uma nota de release, o PDF sai com
  o erro em tipografia bonita. A responsabilidade editorial é de quem orienta.
- **Não testa o que não roda em contêiner Linux.** Instalador gráfico, módulo de
  kernel, macOS, Windows nativo, hardware específico. O preset manda **declarar**
  isso no documento; ele não consegue contorná-lo.
- **Não entrevista sozinha.** A entrevista é uma instrução ao agente, não um
  programa. Um agente que ignore o `CLAUDE.md` vai responder de memória como
  qualquer outro.
- **Não hospeda nada.** O PDF sai na sua máquina. Onde ele circula é decisão sua,
  e o endereço vai para o [`INDEX.md`](../INDEX.md).
- **Não produz curso.** Assunto — álgebra linear, gestão de projetos — é trabalho
  da fábrica irmã, a Course Factory. Aqui se documenta **ferramenta**.
