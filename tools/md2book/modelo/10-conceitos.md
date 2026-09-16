# 10. Conceitos — o modelo mental

`Nível: intermediário`

Repare no salto de `03` para `10`: a numeração dos arquivos **não precisa ser
contínua**. O md2book ordena naturalmente (`2` antes de `10`) e renumera os
capítulos do livro em sequência.

---

## 1. A definição

> **Conceito central** é aquilo que, uma vez entendido, faz o resto do curso
> parecer óbvio. Defina-o antes de usá-lo.

## 2. O diagrama

```
   O QUE O USUÁRIO VÊ              O QUE ACONTECE POR DENTRO
  ┌────────────────────┐         ┌──────────────────────────────┐
  │  um comando só     │   ≡     │  ├─ lê a configuração        │
  │  na linha de       │         │  ├─ valida os campos         │
  │  comando           │         │  └─ executa e devolve código │
  └────────────────────┘         └──────────────────────────────┘
```

## 3. Comparação

| Abordagem | Custo | Quando usar |
|---|---|---|
| Ingênua | Baixo | Protótipos e testes rápidos |
| Intermediária | Médio | Quase sempre |
| Completa | Alto | Só com requisito real de escala |

## 4. Ligações

O conceito daqui reaparece em [01-introducao.md](01-introducao.md) e é aplicado
no [projeto de exemplo](03-projeto/README.md).
