## Checkpoint 1 — Fundação de dados

**Status:** aprovado com ressalvas (T1 reprova na construção por 0,004 ponto; regiões do IBGE pendentes)

**Entregas**
- Estrutura do repositório, `CLAUDE.md`, `config.py`, `requirements.txt`, `.gitignore`, `.env.example`, `run_pipeline.py`
- `src/ingest.py`, `src/clean.py`, `src/referencias.py`, `src/testes.py` (T1 + conferência), `src/log.py`
- `data/reference/cbo_titulos.csv`, `data/reference/subclasse_descricao.csv`
- `data/interim/caged_raw.parquet` (42 MB) e `data/interim/caged_ind.parquet` (fora do Git)
- `reports/log_pipeline.md`, `reports/testes.md`, `reports/conferencia_secao3.md`
- `diagnostics/` com os 3 scripts do v1 (V17)

**Aceite (seção 4.7)**

| Critério | Resultado |
| --- | --- |
| T1 aprovado | C 0,01% · B–E 0,04% · B–F 0,18% aprovados; **F 0,504% reprovado** (V19) |
| 295 municípios casados | 295 de 295; nenhum sem população |
| Zero nulo em `divisao_cnae`, `cbo2002ocupacao`, `grupo_setorial` | 0 · 0 · 0 |
| Zero nulo em `microrregiao` | **Pendente:** API do IBGE inacessível daqui (V21) |
| Números da seção 3 reproduzidos | 27 de 27 |

**Tabela de linhas por regra**

| Regra | Linhas |
| --- | --- |
| Entrada | 3.397.416 |
| R4 janela 202509–202608 | 3.391.288 (−6.128) |
| R5 seções B–F | 1.139.633 (−2.251.655) |
| R6 exclusões | coluna ausente, nada removido |
| R7 cópias excedentes mantidas (B–F) | 26.916 |
| R7 fora do prazo mantidas (B–F) | 9.599 |
| Saída | 1.139.633 linhas, 41 colunas |

**Outros números pedidos**
- Pico de memória da leitura: cerca de 1,8 GB (8 s com Polars).
- Microrregiões e mesorregiões, e quantas microrregiões passam de 1.000 movimentos em C: pendentes (V21).

**Números que não bateram com o SDD**
- Nenhum. Um teste media "CBO com 5 dígitos" no arquivo inteiro (8); na janela são 7, como diz o SDD. Nenhuma dessas linhas é da indústria. O teste foi corrigido.

**Pontos novos:** V19, V20 e V21, registrados na seção 2.3 de `docs/SDD_v2.md`.

**Decisões que preciso do usuário**
1. V19: aceitar 1% de tolerância só para a construção, ou manter 0,5% e só declarar a diferença?
2. V20: CBOs sem título vão ao LLM só com o código (confiança baixa, revisão manual)?
3. V21: rodar `python src/referencias.py` na sua máquina, ou eu sigo para a Fase 2 sem regiões e as regiões entram depois?

**Próxima fase (ao receber "pode seguir"):** Fase 2 — macrofamílias com Gemini (`src/macrofamilias.py`, prompt v1, plano B pronto). Só a chamada real precisa da sua `GEMINI_API_KEY` no `.env`.
