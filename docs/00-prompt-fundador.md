# O prompt fundador

**Data:** 16 de setembro de 2026
**Autor:** Ronivaldo Domingues de Andrade
**Agente:** Claude Code (Anthropic), modelo Opus 5

Este é o pedido que criou a Tutorial Factory. Ele está aqui como **base
histórica e referência de fundação**: quando uma decisão de projeto parecer
arbitrária daqui a dois anos, a resposta provavelmente está neste texto.

O original foi escrito em uma única mensagem, de uma sentada. Abaixo ele
aparece **revisado** — pontuação corrigida, espaços acertados, frases longas
quebradas, uma ou outra palavra trocada por clareza. **Nada foi acrescentado ao
escopo e nada foi retirado dele.** A intenção é exatamente a mesma; só a
superfície foi limpa.

---

## O pedido, revisado

> Nesta pasta vamos construir as diretrizes de comportamento, a documentação e a
> geração de tutoriais para agentes de IA.
>
> O que isso é, exatamente? Quando uma pessoa entrar neste diretório,
> inicializar um agente de IA e nele digitar, por exemplo, *"como instalar
> Docker"*, o agente deve iniciar uma entrevista: *"Para qual sistema
> operacional?"* — e outras perguntas que se fizerem necessárias.
>
> Depois disso, ele deve iniciar uma busca profunda na internet e nos
> repositórios correspondentes, buscando informação verdadeira e atualizada para
> aquele sistema, aquele software e aquela versão. Nunca, jamais, inventar.
> Sempre testar a solução que vai propor.
>
> Munido de todos esses dados, ele deverá produzir um tutorial direto, sem
> rodeios, passo a passo — de modo que um leigo completo entenda —, sem omitir
> nenhum passo e nenhum comando existente, com cada detalhe. Esse documento deve
> ser salvo em três versões — `.md`, `.tex` e `.pdf` — em uma pasta
> `documentation/<software>/installation_AAAA-MM-DD.{md,tex,pdf}`.
>
> Depois do processo detalhado de instalação, ele deverá produzir um livro (ou
> artigo) com o manual de uso do software em questão: comandos básicos, comandos
> necessários, comandos úteis, como usar e para que serve cada um. Um manual
> completo e eficiente, suficiente para que um usuário leigo consiga usar o
> software como um profissional, tendo o manual como base de consulta. Um livro
> semelhante ao livro oficial da linguagem C — conhecido como *a bíblia do C* —,
> mas direto ao ponto, e que descreva ao menos um projeto completo com a
> ferramenta. Salvar esse livro também na pasta
> `documentation/<software>/manual_AAAA-MM-DD.{md,tex,pdf}`.
>
> Para essa parte dos documentos:
>
> 1. Tudo deve ser escrito sempre em português brasileiro.
> 2. Todos os documentos gerados devem ser construídos utilizando o manual da
>    marca da Andrada's Dev. Para saber como fazer isso, visite o meu projeto
>    *course-factory*, atualmente nesta máquina em `/home/ronivaldo/course-generator`,
>    e o manual da marca usado por ele, disponível em
>    `/home/ronivaldo/course-factory-brand`.
>
> Semelhante ao que foi feito no course-factory: crie as licenças e os README, e
> faça ser possível escolher onde será salva a pasta `documentation`, pois ela
> não subirá junto do presente repositório para o git público. Tome o
> course-factory como base para construir este repositório novo, com essa nova
> funcionalidade.
>
> **Observação.** No início cheguei a pensar em fazer essa funcionalidade junto
> com o course-factory, mas ele já se encontra bem consolidado, é um projeto
> finalizado e versionado — logo, achei melhor não mexer.
>
> Em `docs/`, que você criará para documentar este framework, coloque este meu
> prompt inicial de criação (melhore-o e corrija os erros e as ausências de
> pontuação e de espaços) como base histórica e referência de fundação.

---

## O que cada frase virou

Mapa do pedido para o repositório. É o que permite auditar se a fábrica ainda
faz o que foi encomendada para fazer.

| No pedido | No repositório |
|---|---|
| "iniciar uma entrevista" | [`CLAUDE.md`](../CLAUDE.md) § *Etapa 1 · A entrevista* — o mínimo obrigatório, as perguntas condicionais, e **quando não perguntar** |
| "busca profunda na internet e nos repositórios" | `CLAUDE.md` § *Etapa 2 · A pesquisa* — documentação oficial, repositório, releases, o pacote que a distro entrega hoje |
| "nunca, jamais, inventar" | `CLAUDE.md` § *As regras da pesquisa* e § *Padrões de escrita*; toda fonte com URL e data no capítulo final de cada documento |
| "sempre testar a solução que vai propor" | [`tools/sandbox.py`](../tools/sandbox.py) — roda os comandos do próprio documento em contêiner descartável; `CLAUDE.md` § *Etapa 3 · O teste* |
| "direto, sem rodeios, passo a passo" | `CLAUDE.md` § *Persona* e § *Padrões de escrita* — um comando por bloco, verificação a cada passo, sem introdução motivacional |
| "para um leigo completo entender" | § *Etapa 4* — cada passo com o comando exato, o que ele faz em uma linha, a saída esperada, e o que fazer se vier diferente |
| "sem omitir nenhum passo e nenhum comando" | § *Cobertura obrigatória* — inclusive PATH, permissões, proxy, convivência de versões, desinstalar por completo |
| "`.md`, `.tex` e `.pdf`" | [`tools/publish-doc.py`](../tools/publish-doc.py) — o `.md` é a fonte; o `.tex` sai **autocontido**; o `.pdf` sai compilado |
| "`documentation/<software>/installation_AAAA-MM-DD`" | `tools/common.py`, `PIECES` e `docs_root()`; o nome e a data são contrato, não convenção |
| "um livro semelhante à bíblia do C, mas direto ao ponto" | § *Etapa 5 · O manual de uso* e [`tools/example/manual-modelo.md`](../tools/example/manual-modelo.md) |
| "ao menos um projeto completo com a ferramenta" | § *O projeto completo — obrigatório*, e o capítulo 9 do gabarito |
| "sempre em português brasileiro" | § *Padrões de escrita*, primeira linha |
| "utilizando o manual da marca da Andrada's Dev" | [`docs/03-kit-de-marca.md`](03-kit-de-marca.md) — o kit é uma **dependência**, instalada no slot; sem ele a fábrica recusa publicar |
| "crie as licenças e os README" | [`LICENSE`](../LICENSE) com escopo explicitado, [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md), [`README.md`](../README.md), [`INDEX.md`](../INDEX.md) |
| "escolher onde será salva a pasta documentation" | o ponteiro `DOCUMENTATION_PATH` na raiz — ver [`04-arquitetura.md`](04-arquitetura.md) § *Os dois ponteiros* |
| "não subirá junto do presente repo público" | [`.gitignore`](../.gitignore), primeira seção |
| "tome o course-factory como base" | mesma arquitetura, mesmo conversor embarcado, **mesmo contrato de kit de marca** |
| "não mexer no course-factory" | nenhum arquivo fora desta pasta foi alterado; o kit de marca é **lido**, nunca escrito |

---

## As decisões que o pedido não tomou

Onde o pedido era legitimamente ambíguo, alguém teve de decidir. Estas são as
escolhas, e o motivo de cada uma — para que possam ser revistas com conhecimento
de causa, e não por engano.

**O slot de marca continua se chamando `course-factory-brand`.**
O contrato é o mesmo da fábrica irmã, e o kit da Andrada's Dev já o cumpre. Um
nome novo obrigaria a manter dois kits idênticos, ou a duplicar o `BRAND_PATH`.
Um único repositório de marca assina tudo o que o dono publica — que é, afinal,
o que uma marca é para.

**O `.md` é uma fonte única, mas o PDF sai em capítulos.**
O pedido fixou o nome do arquivo no singular, e um arquivo único é o que se
envia por e-mail e se abre em qualquer editor. Mas um livro precisa de capítulo,
sumário e cabeçalho corrido. O publicador reconcilia os dois: o `#` é o título,
cada `##` vira um capítulo, e tudo abaixo sobe um nível. É mecânico e não perde
um byte — ver [`04-arquitetura.md`](04-arquitetura.md) § *A divisão em capítulos*.

**O `.tex` é autocontido, e o tema fica ao lado.**
Um `.tex` que só compila dentro de uma pasta de trabalho não é uma entrega, é um
subproduto. Todos os capítulos são embutidos no arquivo, e o `tema/` ao lado
carrega o `.sty`, os logos e o ambiente da marca. Quem recebe a pasta compila com
`xelatex arquivo.tex` e nada mais.

**Testar é obrigatório; conseguir testar tudo, não.**
Instalador gráfico, módulo de kernel, caminho exclusivo de macOS ou de Windows,
hardware específico — nada disso roda em um contêiner Linux. A regra que
sobrevive ao caso real é: **teste o que der, e declare nominalmente o que não
deu**. Fingir que foi testado é pior do que não testar.

**Uma versão nova é uma edição nova, não uma edição do arquivo.**
A data está no nome porque documentação técnica envelhece. Sobrescrever o
arquivo de 2026 com o conteúdo de 2028 apaga a única informação que dizia contra
qual realidade aquilo foi escrito. Edições convivem; só correção de erro altera
um arquivo existente.

---

## O que este projeto deliberadamente não é

- **Não é o course-factory.** Aquele produz cursos sobre assuntos, do zero ao
  nível de pesquisa, com livro e slides. Este produz manuais sobre **ferramentas**,
  com instalação testada e um projeto que roda. Assuntos vão para lá; softwares
  ficam aqui.
- **Não é um gerador automático.** O agente entrevista, e a entrevista é parte do
  produto. Um manual escrito sem saber o sistema operacional de destino é o
  problema que esta fábrica existe para não repetir.
- **Não é documentação oficial de nada.** Um manual sobre o Docker é um manual
  *sobre* o Docker. Ver [`LICENSE`](../LICENSE), item 2.
