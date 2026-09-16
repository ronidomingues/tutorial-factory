# 03 · Kit de marca

A fábrica **não tem identidade própria**. Ela publica com a identidade instalada
em `tools/course-factory-brand/`, e essa pasta é uma **dependência** — não uma
parte da ferramenta.

Sem um kit que cumpra o contrato, a fábrica **recusa publicar** e diz o que
falta. Nunca sai um PDF meio-marcado.

---

## Por que o slot se chama `course-factory-brand`

O contrato é o mesmo da **Course Factory**, a fábrica irmã que produz cursos. Um
kit de marca é um repositório de quem tem uma marca, e o dono de uma marca quer
que ela assine tudo o que ele publica: um manual e um curso não podem discordar
sobre qual é o logotipo.

Um único repositório de marca, dois `BRAND_PATH` apontando para ele, duas
fábricas assinando igual. Renomear o slot obrigaria a manter dois kits idênticos
ou a duplicar o ponteiro — custo sem benefício.

---

## Como a fábrica acha o kit

Em ordem. O primeiro acerto vence:

| # | Origem | Como se usa |
|---|---|---|
| 1 | `--brand <caminho>` | explícito, uma execução só |
| 2 | `TUTORIAL_FACTORY_BRAND` ou `COURSE_FACTORY_BRAND` | variável de ambiente; a segunda serve às duas fábricas |
| 3 | `tools/course-factory-brand/BRAND_PATH` | **o caminho recomendado** — um arquivo de uma linha apontando para onde o kit realmente mora |
| 4 | `tools/course-factory-brand/` | o kit copiado ou clonado para dentro do slot |
| 5 | `tools/course-factory-brand/template/` | o pré-molde neutro que vem no repositório |

O `--doctor` e o `--check` dizem qual venceu:

```bash
python3 tools/sync-brand.py --check
```

```console
Brand kit: /home/voce/sua-marca (pointer)
```

`(pointer)`, `(explicit)`, `(installed)` ou `(template)`. Se disser `(template)`,
a fábrica avisa a cada publicação: **o pré-molde produz PDF de verdade, mas é a
identidade de ninguém.**

### Por que um arquivo de ponteiro, e não uma variável

Uma variável de ambiente precisa estar definida em **todo** shell — inclusive no
que o agente abre. Um kit que silenciosamente cai no pré-molde publica material
assinado por ninguém, e ninguém percebe até o PDF chegar na caixa de entrada de
alguém. Um arquivo é lembrado pela máquina, não pela pessoa.

```bash
git clone git@github.com:voce/sua-marca.git ~/sua-marca
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
```

Caminho relativo também vale, e resolve contra o próprio slot — assim um
checkout irmão pode ser `../../../sua-marca` e sobrevive ao repositório mudar de
lugar. O `BRAND_PATH` é ignorado pelo git: ele descreve **esta máquina**.

---

## O contrato

Uma pasta é um kit de marca quando tem **`latex/coursebook.sty`**. Esse arquivo é
o marcador: é a peça sem a qual o livro não existe.

O que esta fábrica exige, e o que ela apenas aproveita:

| Arquivo | Obrigatório? | Para quê |
|---|---|---|
| `latex/coursebook.sty` | **sim** | a capa, o rodapé, o colofão e as cores do livro |
| `md2book/book.base.json` | **sim** | tipografia, geometria, cor de destaque, comando de capa |
| `brand.env` | **sim** | nome, tagline, dono, contato e **todas as cores** |
| `BRAND-MANUAL.md` | **sim** | o manual da marca — regras de uso de cor, logo e tipografia |
| `EDITORIAL-STANDARD.md` | não | o que o documento pode e não pode fazer editorialmente |
| `assets/*.pdf` | não | os logos em PDF, para o LaTeX |
| `fonts/` + `fonts.json` | não | a tipografia, quando o kit distribui arquivo de fonte |
| `latex/beamerthemecourseslides.sty` | não | **só a Course Factory usa** — esta fábrica não publica slides |
| `md2book/slides.base.json` | não | idem |

Confira com:

```bash
python3 tools/sync-brand.py --check
```

Um kit que serve às duas fábricas traz também as duas peças opcionais de slides.
Um kit feito só para esta pode omiti-las.

---

## O que a fábrica usa do kit, e o que ela substitui

Esta é a linha que evita confusão ao ler o `book.base.json`:

| A fábrica **mantém** do kit | A fábrica **substitui** |
|---|---|
| cores (`cor_destaque`, `cor_codigo_fundo`, `cor_codigo_borda`) | a raiz e a pasta de saída |
| tipografia (`fontes`) e tamanhos | as **partes** do livro — um manual não tem blocos numerados como um curso |
| geometria da página, papel, corpo, duas faces | a abertura e a ordem dos capítulos |
| `capa_comando`, `encerramento`, `pacotes_extra` | o apêndice de código-fonte (desligado) |
| tudo o mais que seja **aparência** | a profundidade do sumário (2, para alcançar as seções) |

Em uma frase: **a fábrica decide a anatomia, o kit decide a aparência.** Por isso
o `book.base.json` de um kit de curso funciona aqui sem edição nenhuma.

---

## Começar do zero

```bash
python3 tools/sync-brand.py --from-template
```

Copia o pré-molde neutro para dentro do slot. A partir daí ele é **seu** — edite
à vontade. A ordem que dá menos trabalho:

1. **`brand.env`** — nome, tagline, dono, contato **e todas as cores**. Recolorir
   a marca inteira não exige tocar em um `.sty` sequer.
2. **`logo/*.svg`**, e converta para PDF:
   ```bash
   inkscape --export-type=pdf --export-filename=assets/logo.pdf logo/logo.svg
   ```
3. **`BRAND-MANUAL.md`** e **`EDITORIAL-STANDARD.md`** — escreva os seus.

Depois:

```bash
python3 tools/sync-brand.py --palette   # regenera palette/tokens.{json,css}
python3 tools/sync-brand.py --colors    # qual cor vence, qual declaração morreu
python3 tools/publish-doc.py <software> # e olhe o PDF
```

---

## As cores: uma fonte, três lugares que a declaram

Três arquivos podem nomear uma cor — o `brand.env`, os `.sty` e os
`*.base.json` — e **só um vence**. A regra:

```
brand.env  >  .sty (padrões)          para as cores do LaTeX
brand.env  >  book.base.json          para as cores do conversor
```

O publicador traduz cada `BRAND_COLOR_<nome>=RRGGBB` do `brand.env` em um
`\definecolor` dentro de `tema/brand-env.tex`, que o `.sty` lê **depois** dos
próprios padrões. O que está no `brand.env` ganha.

Para ver quem está ganhando e qual declaração virou letra morta:

```bash
python3 tools/sync-brand.py --colors
```

```console
  NAME             brand.env  .sty       WINNER
  adLima           A3FF12     A3FF12     brand.env (same value)
  adVioleta        7C5CFF     5B3EE0     brand.env (the .sty value is dead)
```

É assim que se encontra a edição que não fez efeito.

---

## Tipografia

Um kit pode declarar as fontes de duas formas:

**Sem distribuir arquivo.** O `book.base.json` nomeia famílias (`Inter`,
`JetBrains Mono`) e a máquina precisa tê-las instaladas. É o que o pré-molde faz,
com a família Latin Modern, que acompanha qualquer TeX Live.

**Distribuindo os arquivos**, em `fonts/`, com um `fonts.json` que diz quais
famílias existem, quais arquivos as compõem e como o `fontspec` deve montar cada
face. A fábrica então decide, por máquina:

| `--fonts` | O que acontece |
|---|---|
| `auto` (padrão) | usa as instaladas; se faltarem, copia para `tema/fontes/` |
| `system` | usa as instaladas, e avisa se não estiverem |
| `folder` | **sempre** copia para `tema/fontes/`, para a pasta viajar inteira |

`--fonts folder` é o modo certo para mandar a documentação a alguém: a pasta
chega completa, e o `.tex` compila na máquina do destinatário sem instalar fonte
nenhuma.

Quem distribui fonte assume a licença. Regra prática:

| Licença | Pode redistribuir no kit? |
|---|---|
| SIL Open Font License 1.1 | **sim**, mantendo o arquivo de licença junto |
| Apache 2.0 | **sim**, mantendo o aviso |
| GUST Font License (Latin Modern, TeX Gyre) | **sim** |
| Comercial / EULA de foundry | **quase sempre não** — leia o contrato |

---

## Instalar um kit que já existe

```bash
# copiar de uma pasta para dentro do slot
python3 tools/sync-brand.py --install ~/minha-marca

# ver o que mudaria, sem mudar nada
python3 tools/sync-brand.py --install ~/minha-marca --dry-run

# sobrescrever um kit já instalado
python3 tools/sync-brand.py --install ~/minha-marca --force
```

O programa **nunca escreve na origem**. Ele copia só o que é kit — `brand.env`,
os manuais, `latex/*.sty`, `md2book/*.json`, `assets/`, `logo/`, `palette/`,
`fonts/` — e ignora o resto, porque um kit costuma ser um repositório com README,
histórico e arquivos de trabalho próprios.

**Clonando um repositório de marca?** Clone **fora** do slot e use o `BRAND_PATH`.
O slot não está vazio (ele contém o `template/`), e `git clone` dentro dele falha.

---

## Trocar a marca depois

Mudou o `brand.env`, o logo ou o `.sty`? O tema é **copiado para dentro de cada
pasta de documentação** no momento da publicação — é isso que mantém o `.tex`
compilável um ano depois, em outra máquina, por alguém que nunca teve o kit. A
contrapartida é que o PDF antigo não muda sozinho.

```bash
python3 tools/sync-brand.py --check     # o kit está válido?
python3 tools/publish-all.py --jobs 6   # republica tudo
```

---

## O que a marca imprime em cada documento

| Onde | O que aparece |
|---|---|
| Capa | logo, título, **a peça** (manual de instalação ou de uso), autor e orientador (`BRAND_OWNER`), o agente de IA e o modelo, nível, versão, data de produção, data de publicação, extensão |
| Rodapé de toda página | marca e título do documento |
| Colofão | símbolo, marca, tagline e os créditos outra vez |

O crédito ao agente é **explícito e por decisão editorial**. Passe o modelo com
`--ai-model "Claude Opus 5"`; sem isso, a capa credita o agente sem versão, o
que é menos honesto e igualmente permitido.

---

## O que o `brand.env` carrega

```ini
BRAND_NAME=Andrada's Dev
BRAND_TAGLINE=Do backlog ao deploy.
BRAND_OWNER=Ronivaldo Domingues de Andrade     # autoria e orientação
BRAND_AUTHOR=Ronivaldo D. Andrade              # propriedades do PDF
BRAND_EMAIL=...
BRAND_SITE_URL=...

BRAND_COURSE_LICENSE=Uso educacional. Todos os direitos reservados.
BRAND_DOC_LEVEL=do zero absoluto ao uso profissional

BRAND_COLOR_adLima=A3FF12      # o que vem depois dos seis dígitos é comentário
BRAND_BOOK_ACCENT=7FCC00       # cor que o conversor pinta, não o LaTeX
```

`BRAND_DOC_LEVEL` é a única chave que esta fábrica acrescenta ao contrato, e ela
é **opcional**: sem ela, a capa usa "do zero absoluto ao uso profissional". Um
kit que não a tenha continua válido.

> **Nenhum segredo aqui.** Senha, token e chave moram no cofre. Um kit de marca
> circula entre máquinas e, às vezes, entre pessoas.

---

## Checklist de um kit pronto

- [ ] `python3 tools/sync-brand.py --check` diz **Contract satisfied**.
- [ ] `--colors` não mostra nenhuma declaração morta que devesse estar viva.
- [ ] `--palette` não acusa `palette/` desatualizado.
- [ ] Um documento de teste publicado, e a capa aberta e conferida.
- [ ] O logo aparece na capa — e não o texto de fallback com o nome da marca.
- [ ] As fontes saíram certas (compare com o `BRAND-MANUAL.md`).
- [ ] O `BRAND_OWNER` está correto: é o nome que responde pelo material.
