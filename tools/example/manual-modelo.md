# {{SOFTWARE}} — manual de uso, do primeiro comando ao projeto completo

<!--
  GABARITO DO MANUAL DE USO — tutorial-factory
  ---------------------------------------------------------------------------
  Apague este comentário e TODOS os textos entre chaves duplas antes de
  publicar.

  Este documento é um LIVRO, não uma página de ajuda. A régua é o livro de
  Kernighan e Ritchie: direto ao ponto, sem enrolação, e com um projeto
  completo no meio, construído do zero até rodar.

  A gramática que o publicador entende:
    #      o título do documento — UM só, na primeira linha
    ##     um CAPÍTULO do livro
    ###    uma seção dentro do capítulo
    ####   uma subseção
    ```lang  bloco de código, com a linguagem sempre declarada

  Tudo entre o `#` e o primeiro `##` vira o capítulo de abertura.
-->

{{Uma frase: o que a pessoa vai saber fazer ao terminar este livro.}}

| Campo | Valor |
|---|---|
| Versão coberta | {{Docker Engine 27.3.1}} |
| Pré-requisito | o manual de instalação desta mesma pasta |
| Data da redação | {{DD/MM/AAAA}} |
| Projeto do capítulo final | {{o que será construído}} |

> **Como usar este livro.** Leia os capítulos 1 a 3 na ordem, uma vez. Depois
> disso ele vira consulta: o capítulo {{N}} é a referência de comandos e o
> capítulo {{N}} é o projeto completo.

## 1. O que o {{SOFTWARE}} é, e que problema resolve

{{Sem jargão. A analogia primeiro, a definição depois, e o problema real que
fez a ferramenta existir. Se a pessoa não entender por que isso existe, nenhum
comando vai fazer sentido.}}

### O modelo mental

{{A imagem que explica quase todo comportamento da ferramenta. É a página que
o leitor vai relembrar dois anos depois.}}

### Quando NÃO usar

{{O que compete com isso, e em que caso a alternativa ganha. Honestidade aqui
compra credibilidade para o resto do livro.}}

## 2. O vocabulário

{{Todo termo que o resto do livro vai usar, definido aqui, uma vez. Tabela:
termo, o que é, e um exemplo de uma linha.}}

| Termo | O que é | Exemplo |
|---|---|---|
| `{{termo}}` | {{definição}} | `{{exemplo}}` |

## 3. Os primeiros cinco minutos

{{Do ambiente pronto até algo funcionando na tela. O menor exemplo que já é
significativo, com a saída esperada mostrada.}}

### O ciclo de trabalho do dia a dia

{{Editar → rodar → ver o resultado → depurar. Este é o ritmo que a pessoa vai
repetir mil vezes; descreva-o explicitamente.}}

## 4. Comandos básicos

{{Organizado por TAREFA, não em ordem alfabética. Cada comando: o que faz,
quando usar, e um exemplo real que roda.}}

### {{Tarefa}}

```bash
{{comando}}
```

{{O que ele faz, as opções que realmente importam, e a pegadinha que todo
iniciante encontra.}}

## 5. Comandos necessários no uso real

{{O que não aparece em tutorial mas aparece no primeiro dia de trabalho: logs,
inspeção, limpeza, diagnóstico, desfazer.}}

## 6. Comandos úteis que quase ninguém conhece

{{Os atalhos e padrões que só quem usa há anos conhece. Esta é a seção que
diferencia este livro de uma tradução da documentação oficial.}}

## 7. Referência de opções

{{Tabelas consultáveis. Marque o que está OBSOLETO e diga o que o substituiu —
com a versão em que mudou.}}

| Opção | O que faz | Quando usar | Situação |
|---|---|---|---|
| `{{--flag}}` | {{o que faz}} | {{quando}} | {{atual / obsoleta desde X}} |

## 8. Receitas

{{No mínimo dez, do trivial ao de produção. Cada uma: problema → solução →
explicação. Todo código completo e executável — nada de `...` no meio.}}

### {{Problema em uma linha}}

```bash
{{solução completa}}
```

{{Por que funciona, e em que caso não funciona.}}

## 9. Projeto completo: {{nome do projeto}}

{{O capítulo que faz este livro valer. Uma aplicação pequena mas INTEIRA,
construída do zero, passo a passo, que roda de verdade. Não um trecho.}}

### O que vamos construir, e por quê

{{Descrição, o resultado final, e o que este projeto ensina que as receitas do
capítulo 8 não ensinam.}}

### Estrutura de arquivos

```text
{{árvore de diretórios comentada}}
```

### Passo 1 — {{...}}

```{{linguagem}}
{{código completo do arquivo, com o nome do arquivo dito antes do bloco}}
```

{{O que este arquivo faz e por que é assim.}}

### Passo N — Rodar

```bash
{{comandos exatos}}
```

```console
{{saída esperada}}
```

### O que quebra sob uso real

{{Tratamento de erro, configuração externa, log e um teste. É o que separa um
projeto de tutorial de um projeto de verdade.}}

## 10. Armadilhas e más práticas

{{Os erros clássicos, os mitos, e por que eles persistem. Com a correção.}}

## 11. Diagnóstico

{{A mensagem de erro literal, a causa e a correção. No mínimo os dez erros mais
comuns do uso — não da instalação, que já está no outro documento.}}

| Mensagem | Causa provável | Correção |
|---|---|---|
| `{{erro literal}}` | {{causa}} | {{correção}} |

## 12. Para onde ir depois

{{Documentação oficial com trilha, livros reais (autor, editora, edição, ano),
e o que é legalmente gratuito. Nunca invente ISBN, edição ou link.}}

## 13. Fontes consultadas

- {{Documentação oficial}} — <{{URL}}> — consultado em {{DD/MM/AAAA}}.
- {{Código-fonte, release notes, RFC, spec}} — <{{URL}}> — consultado em {{DD/MM/AAAA}}.
