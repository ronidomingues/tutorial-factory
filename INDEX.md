# Catálogo — Tutorial Factory

O que esta fábrica já documentou. Uma linha por software.

> **Por que não há link para os arquivos.** `documentation/` não é versionado: o
> material pertence a quem o gerou e circula onde ele decidir. Um link para
> dentro dessa pasta morreria no clone de outra pessoa, e um link morto é pior
> que nenhum. Onde o PDF está de fato, quando está em algum lugar, é a seção
> [Onde o material está](#onde-o-material-está).

---

## Balanço

Números de **17/09/2026**. Saem de `python3 tools/publish-all.py --check`.

| Métrica | Valor |
|---|---|
| Softwares documentados | **7** |
| Manuais de instalação | **7** |
| Manuais de uso | **7** |
| Páginas em PDF | **848** |

---

## Softwares

| Software | Edição | Ambiente testado | Páginas | O que cobre |
|---|---|---|---|---|
| Java (Temurin JDK 25 LTS) | 16/09/2026 | Debian 12 (bookworm), amd64 — Temurin 25.0.4.1+1 | 65 + 72 = 137 | Do Debian 12 sem Java até o JDK 25 LTS funcionando, com `JAVA_HOME`, Maven, Gradle, convivência com o JDK 21 do Android e uma API HTTP completa |
| PostgreSQL 18 | 17/09/2026 | Debian 12 (bookworm), amd64 — PostgreSQL 18.6 (PGDG) | 60 + 60 = 120 | Do Debian 12 sem banco até o PostgreSQL 18.6 servindo em rede com TLS obrigatório, papel de aplicação separado, backup testado e capítulo próprio de Windows 11 |
| MySQL 9.7 LTS | 17/09/2026 | Debian 12 (bookworm), amd64 — MySQL 9.7.2 (repositório Oracle) | 60 + 58 = 118 | Do Debian 12, onde o MySQL não existe nos repositórios, até a 9.7.2 LTS com TLS, usuário separado do `root`, log binário e backup restaurado |
| MariaDB 12.3 LTS | 17/09/2026 | Debian 12 (bookworm), amd64 — MariaDB 12.3.3 | 54 + 56 = 110 | Do MariaDB 10.11 do Debian até a 12.3.3 LTS com TLS, `unix_socket` para o administrador, log binário por decisão e tabelas versionadas no tempo |
| SQLite 3.53 | 17/09/2026 | Debian 12 (bookworm), amd64 — SQLite 3.53.4 (compilado) e 3.40.1 (Debian) | 50 + 64 = 114 | Instala o SQLite das três formas que fazem sentido e decide o que precisa ser decidido antes de produção: WAL, chaves estrangeiras, concorrência, backup a quente e réplica |
| Node.js 24 LTS com nvm | 17/09/2026 | Debian 12 (bookworm), amd64 — Node 24.21.0, npm 11.19.0, nvm 0.40.7 | 63 + 64 = 127 | Do Debian 12 sem JavaScript até o Node 24 LTS gerenciado por nvm, npm sem `sudo`, proxy corporativo, versão fixada por projeto e uma API HTTP completa com testes |
| JavaScript (linguagem) | 17/09/2026 | Debian 12 (bookworm), amd64 — Node 24.21.0 (V8 13.6), Deno 2.9.7, Bun 1.4.2 | 42 + 80 = 122 | Monta os quatro ambientes que executam JavaScript e ensina a linguagem até a ES2026, com projeto completo que roda no terminal e no navegador |

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
| PostgreSQL, MySQL, MariaDB, SQLite | O capítulo de **Windows 11** dos quatro foi escrito a partir da documentação oficial de cada projeto, **sem execução** — não há como rodar instalador do Windows em contêiner Linux. Cada bloco está marcado com `⚠ não executado aqui` no próprio documento | 17/09/2026 |
| PostgreSQL | Arquivamento de WAL e recuperação a um instante (PITR) descritos, mas **não exercitados até a restauração**: exigem uma segunda máquina e horas de tráfego | 17/09/2026 |
| MySQL | Percona XtraBackup (backup físico) citado como recomendação, **não executado** — não estava instalado no contêiner de teste | 17/09/2026 |
| MariaDB | `mariadb-backup` **não executado**: está em pacote separado, ausente no contêiner. Papéis (roles) e Galera Cluster descritos sem execução — Galera exige três máquinas | 17/09/2026 |
| SQLite | Litestream, LiteFS e `sqlite3_rsync` **não executados**: os três exigem um destino remoto (bucket ou segunda máquina) | 17/09/2026 |
| Node.js / JavaScript | O capítulo de **Windows 11 e macOS** dos dois softwares foi escrito a partir da documentação oficial da Microsoft, do nvm-windows e do Homebrew, **sem execução** — não há como rodar `.exe` nem `brew` em contêiner Linux. Cada bloco está marcado com `⚠ não executado aqui` | 17/09/2026 |
| JavaScript | A **parte de navegador** (console do DevTools e o front-end do projeto completo) não foi executada: o contêiner de teste não tem navegador. O servidor estático e o `content-type` dos módulos, sim | 17/09/2026 |
| Node.js | `nvm install -s` (compilar do fonte) descrito e **não executado** — estouraria o tempo-limite do contêiner. `systemd` também não, por não haver PID 1 no contêiner | 17/09/2026 |

---

## Onde o material está

Se a documentação foi publicada em algum lugar — site, wiki interna, Drive,
servidor de arquivos —, o endereço entra aqui. É a única forma de alguém que
clonou este repositório encontrar o que ele produziu.

| Onde | O que tem lá | Acesso |
|---|---|---|
| `~/dev-learning-lab/java/` (máquina local, fora deste repositório) | Java — manual de instalação e manual de uso, em `.md`, `.tex` e `.pdf` | local |
| `~/dev-learning-lab/postgresql/` (idem) | PostgreSQL 18 — instalação e uso, em `.md`, `.tex` e `.pdf` | local |
| `~/dev-learning-lab/mysql/` (idem) | MySQL 9.7 LTS — instalação e uso, em `.md`, `.tex` e `.pdf` | local |
| `~/dev-learning-lab/mariadb/` (idem) | MariaDB 12.3 LTS — instalação e uso, em `.md`, `.tex` e `.pdf` | local |
| `~/dev-learning-lab/sqlite/` (idem) | SQLite 3.53 — instalação e uso, em `.md`, `.tex` e `.pdf` | local |
| `~/dev-learning-lab/nvm-nodejs/` (idem) | Node.js 24 LTS com nvm — instalação e uso, em `.md`, `.tex` e `.pdf` | local |
| `~/dev-learning-lab/javascript/` (idem) | JavaScript (linguagem) — instalação e uso, em `.md`, `.tex` e `.pdf` | local |
