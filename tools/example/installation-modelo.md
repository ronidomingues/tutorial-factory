# Instalação do {{SOFTWARE}} — {{SISTEMA}}, do zero

<!--
  GABARITO DO MANUAL DE INSTALAÇÃO — tutorial-factory
  ---------------------------------------------------------------------------
  Apague este comentário e TODOS os textos entre chaves duplas antes de
  publicar. O que fica é um documento que um leigo completo segue sem
  improvisar e sem abrir outra aba.

  A gramática que o publicador entende:
    #      o título do documento — UM só, na primeira linha
    ##     um CAPÍTULO do livro
    ###    uma seção dentro do capítulo
    ####   uma subseção
    ```lang  bloco de código, com a linguagem sempre declarada

  Tudo entre o `#` e o primeiro `##` vira o capítulo de abertura.
  Nada é resumido na conversão: o .md, o .tex e o .pdf dizem a mesma coisa.
-->

{{Uma frase dizendo exatamente o que este documento faz com a máquina de quem
lê: de que estado ela parte e em que estado ela termina.}}

| Campo | Valor |
|---|---|
| Sistema testado | {{Ubuntu 24.04.3 LTS (Noble Numbat), amd64}} |
| Versão instalada | {{Docker Engine 27.3.1}} |
| Método recomendado | {{repositório oficial APT}} |
| Data do teste | {{DD/MM/AAAA}} |
| Tempo estimado | {{15 a 25 minutos}} |
| Precisa de `sudo` | {{sim}} |
| Precisa de conta ou cartão | {{não}} |

> **Como este documento foi verificado.** {{Descreva em uma ou duas frases onde
> os comandos rodaram de verdade — contêiner, máquina virtual, máquina física —
> e o que provou que funcionaram. Se algum passo não pôde ser testado, diga
> qual e por quê, aqui, antes de qualquer comando.}}

## 1. Antes de começar

{{O que precisa ser verdade antes do primeiro comando. Cada item vira uma seção
com um comando de conferência e a saída esperada.}}

### Conferir a versão do sistema

```bash
{{comando}}
```

Saída esperada:

```console
{{saída literal, copiada da execução real}}
```

{{O que fazer se a saída for diferente — uma frase, com a rota de saída.}}

### Conferir espaço em disco, memória e arquitetura

{{Requisitos reais, com números. "Precisa de espaço" não é requisito.}}

### O caminho sem instalar nada

{{Se existir playground, contêiner pronto ou ambiente na nuvem, ofereça AQUI,
antes do caminho longo. É o que evita a desistência no primeiro dia. Se não
existir, diga que não existe.}}

## 2. Remover instalações antigas

{{O que colide com o que vai ser instalado, e como sair disso sem quebrar o
resto da máquina. Diga o que acontece se não houver nada a remover.}}

## 3. Instalar o {{SOFTWARE}}

{{Um passo por seção. Cada seção: o comando exato, o que ele faz em uma linha,
e a verificação com a saída esperada.}}

### {{Passo — o que ele faz}}

```bash
{{comando exato, copiável, um por bloco}}
```

{{O que este comando faz, em uma linha, para ninguém executar às cegas.}}

### Verificar que deu certo

```bash
{{comando de versão}}
```

```console
{{saída esperada}}
```

## 4. Configurar depois de instalar

{{PATH e variáveis de ambiente — em qual arquivo de perfil, como conferir, e
por que a mudança "não pegou" antes de reabrir o terminal.}}

{{Permissões — o caminho certo sem `sudo` onde `sudo` causa problema, e por
quê.}}

{{Rede corporativa — proxy, certificado interno, registry espelhado.}}

## 5. Conviver com outras versões

{{Como ter duas versões na mesma máquina sem conflito, e como fixar a versão
para o projeto: lockfile, arquivo de versão, imagem de contêiner.}}

## 6. Atualizar, voltar atrás e desinstalar

### Atualizar com segurança

### Voltar para a versão anterior

### Desinstalar por completo

{{Inclusive caches, configurações, volumes e o que costuma ficar para trás.}}

## 7. Instalar em outros sistemas

{{Uma seção completa por sistema operacional coberto — sem "no Windows é
parecido". Linux (Debian/Ubuntu e Fedora/RHEL), macOS (Intel e Apple Silicon,
quando importar), Windows (nativo e WSL2, dizendo qual é o recomendado e por
quê). Cada um com seus próprios comandos e sua própria verificação.}}

## 8. Problemas comuns

{{No mínimo cinco, com a mensagem de erro LITERAL.}}

| Mensagem | Causa provável | Correção |
|---|---|---|
| `{{erro literal}}` | {{causa}} | {{correção}} |

## 9. Checklist de ambiente pronto

{{Um comando por linha. Quem marca todos está pronto para o manual de uso.}}

- [ ] `{{comando}}` responde `{{saída}}`
- [ ] `{{comando}}` responde `{{saída}}`

## 10. Fontes consultadas

{{Toda fonte com URL e data de consulta. Nunca uma fonte de memória.}}

- {{Documentação oficial}} — <{{URL}}> — consultado em {{DD/MM/AAAA}}.
- {{Repositório do projeto, release notes, changelog}} — <{{URL}}> — consultado em {{DD/MM/AAAA}}.
