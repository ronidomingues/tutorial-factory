# 3. Projeto de exemplo

Um capítulo pode morar numa **subpasta**. Basta que o arquivo se chame
`README.md`: o md2book o trata como o capítulo daquela pasta, e links para a
pasta (`03-projeto/`) apontam para cá.

---

## 1. O que este projeto faz

Lê uma configuração, soma alguns números e imprime o resultado. O código
completo está no apêndice, no fim do livro — é o `apendice_fontes` do
`livro.json` que o coloca lá.

## 2. Como rodar

```bash
cd 03-projeto
python3 app.py config.yaml
```

## 3. Estrutura

```
03-projeto/
├── README.md      ← este capítulo
├── app.py         ← o programa
└── config.yaml    ← a configuração
```

Desenhos em caracteres de caixa (`├─└│`) são preservados: as caixas de código
usam fonte monoespaçada e avançam nas margens para caber.

## 4. Autoteste

1. Rode o programa e confira a saída.
2. Mude um valor em `config.yaml` e rode de novo.
3. Explique por que o programa falha se o arquivo não existir.
