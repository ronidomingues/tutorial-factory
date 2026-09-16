# 2. Instalação

`Nível: iniciante`

---

## 1. Por sistema operacional

| Sistema | Comando | Observação |
|---|---|---|
| Debian/Ubuntu | `sudo apt install exemplo` | Precisa de `sudo` |
| macOS | `brew install exemplo` | Requer Homebrew |
| Windows | `winget install Exemplo` | PowerShell como administrador |

## 2. Conferindo

```console
$ exemplo --version
exemplo 1.0.0
```

Se aparecer `command not found`, o `PATH` não foi atualizado — abra um
terminal novo.

## 3. Configuração mínima

```yaml
servico:
  porta: 8080
  modo: producao
```

## 4. Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `command not found` | `PATH` desatualizado | Reabra o terminal |
| `permission denied` | Falta de permissão | Use `sudo` |
| Versão antiga | Cache do gerenciador | Atualize os índices |
