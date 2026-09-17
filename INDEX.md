# Catálogo — Tutorial Factory

O que esta fábrica já documentou. Uma linha por software.

> **Por que não há link para os arquivos.** `documentation/` não é versionado: o
> material pertence a quem o gerou e circula onde ele decidir. Um link para
> dentro dessa pasta morreria no clone de outra pessoa, e um link morto é pior
> que nenhum. Onde o PDF está de fato, quando está em algum lugar, é a seção
> [Onde o material está](#onde-o-material-está).

---

## Balanço

Números de **16/09/2026**. Saem de `python3 tools/publish-all.py --check`.

| Métrica | Valor |
|---|---|
| Softwares documentados | **1** |
| Manuais de instalação | **1** |
| Manuais de uso | **1** |
| Páginas em PDF | **137** |

---

## Softwares

| Software | Edição | Ambiente testado | Páginas | O que cobre |
|---|---|---|---|---|
| Java (Temurin JDK 25 LTS) | 16/09/2026 | Debian 12 (bookworm), amd64 — Temurin 25.0.4.1+1 | 65 + 72 = 137 | Do Debian 12 sem Java até o JDK 25 LTS funcionando, com `JAVA_HOME`, Maven, Gradle, convivência com o JDK 21 do Android e uma API HTTP completa |

**Como preencher uma linha**, quando ela existir:

| Campo | De onde sai |
|---|---|
| **Software** | o nome da pasta em `documentation/` |
| **Edição** | a data no nome dos arquivos, em dd/mm/aaaa |
| **Ambiente testado** | o sistema e a versão da ficha do manual de instalação |
| **Páginas** | instalação + uso, de `publish-all.py --check` |
| **O que cobre** | a primeira frase do manual de instalação, até ~140 caracteres |

Uma edição nova **não substitui a linha**: acrescente a nova e mantenha a antiga,
com a data que tinha. O catálogo registra o que foi produzido e quando.

---

## Pendências

Documento que ficou pela metade, PDF que não compilou, passo que não pôde ser
testado em contêiner — registre aqui, com a data, e tire quando resolver.

| Software | O que falta | Desde |
|---|---|---|
| Java | Seção 15.3 (openSUSE) não pôde ser executada: o repositório `rpm/opensuse/15.6` da Adoptium não existe, e a tentativa pelo repositório de SLES 15 esbarrou no tempo-limite do contêiner. Os comandos estão publicados marcados como não verificados | 16/09/2026 |
| Java | Capítulo 16 (Windows e macOS) escrito a partir da documentação oficial, sem execução — não há como rodar `winget` ou `brew` em contêiner Linux | 16/09/2026 |

---

## Onde o material está

Se a documentação foi publicada em algum lugar — site, wiki interna, Drive,
servidor de arquivos —, o endereço entra aqui. É a única forma de alguém que
clonou este repositório encontrar o que ele produziu.

| Onde | O que tem lá | Acesso |
|---|---|---|
| `~/dev-learning-lab/java/` (máquina local, fora deste repositório) | Java — manual de instalação e manual de uso, em `.md`, `.tex` e `.pdf` | local |
