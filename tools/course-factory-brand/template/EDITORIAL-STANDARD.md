# Padrão Editorial — Course Factory (pré-molde)

> Molde. Descreve o que o livro e os slides podem e não podem fazer.
> Substitua pelo padrão editorial da sua marca junto com o resto do kit.

Versão 1.0 · 16/09/2026

---

## 1. O que este documento resolve

O manual da marca diz como a identidade se parece. Este diz **como ela se
comporta em material didático**: o que entra na capa, quem é creditado, o que
cabe em um slide e o que é erro de composição.

Regra de ouro: **o Markdown do curso é a fonte da verdade.** O livro e os
slides derivam dele. Nada é apagado, encurtado ou resumido para caber na
publicação — se não coube, o problema é do molde, não do texto.

---

## 2. Autoria, orientação e o crédito da máquina

Três papéis, sempre nomeados:

| Papel | Quem | O que responde |
|---|---|---|
| **Autor e orientador** | uma pessoa, nome civil completo | escopo, profundidade, ordem de leitura, padrão de qualidade — e pelo resultado |
| **Escrita e materialização** | o agente de IA, nomeado e versionado | redigiu os textos, montou os projetos, gerou os PDFs |
| **Publicação** | a marca | edita, publica e distribui |

### 2.1 Por que o agente é creditado

Por decisão editorial, não por obrigação legal: **quem lê tem o direito de
saber como o material foi produzido.** Um livro de 250 páginas escrito por um
modelo de linguagem e revisado por uma pessoa não é a mesma coisa que um livro
escrito à mão, e esconder isso é desonesto com o leitor.

O crédito traz o **nome do agente e o modelo** (`--agent`, `--ai-model`),
porque "IA" sem versão não é informação.

### 2.2 Onde cada crédito aparece

| Peça | Onde |
|---|---|
| Livro | capa · página de créditos · colofão |
| Slides | capa de cada aula · tela de fechamento de cada aula |
| Pasta | `97-publicacao/LEIA-ME.md`, gerado a cada publicação |

---

## 3. A identidade aplicada

### 3.1 Livro — documento impresso, fundo claro

- Capa **escura de sangria total**; miolo em papel claro.
- Filete azul profundo marca hierarquia; o âmbar não entra no miolo.
- Rodapé de toda página: marca à esquerda no verso, título à direita na frente.
- Colofão fecha o livro — símbolo, marca, tagline, créditos outra vez.

### 3.2 Slides — projeção, fundo escuro

- Fundo `ink`, texto `paper`, azul conduzindo.
- Um destaque em âmbar por tela. Um.
- Rodapé: marca · curso · aula · número/total.
- A capa da aula repete curso, orientador, agente e data — um slide fotografado
  na plateia precisa se identificar sozinho.

---

## 4. O que um slide pode e não pode

| Medida | Valor |
|---|---|
| Slides por aula | 12 a 25 |
| Linhas por slide | até 10 (o conversor avisa a partir de 12) |
| Ideias por slide | **uma** — se o título tem "e", são dois slides |
| Duração alvo | 30 a 50 min de fala |
| Código no slide | até 12 linhas; recorte o trecho e diga onde está o inteiro |

**Não entra em slide:** parágrafo, lista de dez itens, tabela de quinze linhas,
"conforme vimos anteriormente", captura de tela ilegível no projetor.

**Entra:** uma afirmação por linha, número com unidade e data, o termo definido
na tela em que aparece, um exemplo concreto logo depois de todo conceito
abstrato, diagrama em ASCII ou tabela pequena no lugar de três frases.

### 4.1 Deck escrito e deck gerado

`tools/generate-lectures.py` converte o material em decks de **rascunho** —
serve para cobrir curso já escrito, e o cabeçalho de cada arquivo diz que é
rascunho.

Curso novo tem aula **escrita à mão**. O gerador não sabe qual é a ideia
central de uma aula, não sabe o que merece uma tela inteira e não inventa a
analogia que faz a turma entender. Reescreveu? Apague a linha
`gerado: rascunho` do cabeçalho.

---

## 5. Tom de voz aplicado ao ensino

- **Defina antes de usar.** Todo termo, na primeira ocorrência.
- **Todo conceito abstrato ganha um exemplo concreto** logo depois.
- **Separe fato, consenso e opinião** sempre que houver risco de confusão.
- **Datas absolutas.** Nunca "recentemente" ou "hoje em dia".
- **Nunca invente** referência, link, preço, ISBN ou número. Na dúvida, diga
  que é aproximado — ou omita.

---

## 6. Reprodutibilidade

- Livro e slides saem de **um comando**: `tools/publish-course.py`.
- O `.tex` fica versionado ao lado do `.pdf`: quem recebe o material pode
  recompilar, não só ler.
- Mudou a marca? **Republique.** PDF desatualizado é pior que PDF ausente: ele
  mente com aparência de pronto.

### 6.1 Mudar o estilo de todos os cursos

Edite `md2book/book.base.json` ou `md2book/slides.base.json` **no kit**, não o
`livro.json` de um curso. Depois:

```bash
python3 tools/publish-all.py courses --reset-config --jobs 6
```

---

## 7. Governança

Mudança neste documento vale para o material publicado **a partir dela** — o
que já saiu fica como está, com a sua data. Registre no changelog.

### Changelog

- **1.0** — 16/09/2026 — primeira versão do pré-molde neutro.
