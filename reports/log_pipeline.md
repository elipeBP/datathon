# Log do pipeline

Execução: 2026-11-11 22:36

## Ingestão (R1–R2)

| Item | Valor |
| --- | --- |
| Linhas lidas | 3,397,416 |
| Colunas | 28 |
| Nulos em idade | 2,202 |
| Salário não numérico | 0 |
| Tempo de leitura | 2.6 s |
| Pico de memória do processo | 2,240 MB |

## Dicionário (R12b)

| Item | Valor |
| --- | --- |
| Títulos de CBO | 2,778 |
| Subclasses CNAE | 1,357 |

## Municípios do evento (R11)

| Item | Valor |
| --- | --- |
| Municípios válidos | 295 |
| População total (Censo 2022) | 7,610,361 |

## Limpeza e junções (R3–R14)

| Item | Valor |
| --- | --- |
| Entrada (caged_raw.parquet) | 3,397,416 |
| R4 janela 202509–202608 | 3,397,416 → 3,391,288 (−6,128) |
| R5 seções BCDEF | 3,391,288 → 1,139,633 (−2,251,655) |
| R6 exclusões | coluna ausente: nada removido (V2) |
| R7 cópias excedentes de linhas idênticas mantidas (B–F) | 26,916 |
| R7 fora do prazo mantidas | 9,599 |
| R11 municípios casados | 295 de 295; sem população: 0 |
| R12 regiões | 20 microrregiões; nulos: 0 |
| R12b CBO sem título | 131 linhas |
| R12b subclasse sem descrição | 0 linhas |
| Nulos em divisao_cnae | 0 |
| Nulos em cbo2002ocupacao | 0 |
| Nulos em grupo_setorial | 0 |
| Nulos em microrregiao | 0 |
| Saída (caged_ind.parquet) | 1,139,633 linhas, 41 colunas |

## KPIs (seção 5)

| Item | Valor |
| --- | --- |
| kpis_segmento | 3 linhas |
| kpis_grupo_setorial | 13 linhas |
| kpis_divisao | 37 linhas |
| kpis_segmento_sem_cbo_dominante | 3 linhas |
| kpis_grupo_setorial_sem_cbo_dominante | 13 linhas |
| perfil_escolaridade_grupo | 104 linhas |
| perfil_salario_grupo | 26 linhas |
| kpis_microrregiao | 60 linhas |
| kpis_micro_grupo | 257 linhas |
| quadrantes | 169 linhas |
| perfil_escolaridade_micro_grupo | 1962 linhas |
| perfil_salario_micro_grupo | 512 linhas |
| quociente_locacional | 257 linhas |
| Polos (QL > 1,1 / 1,25 / 1,5 com ≥1.000 mov.) | 62 / 54 / 41 |
| kpis_macrofamilia | 115 linhas |
| kpis_grupo_macrofamilia | 495 linhas |
| kpis_micro_macrofamilia | 1760 linhas |
| kpis_micro_grupo_macrofamilia | 5540 linhas |
| Tamanho de data/processed | 2.08 MB (limite 20 MB) |

## Modelo das saídas a pedido

| Item | Valor |
| --- | --- |
| Desligamentos na amostra | 388,489 |
| Taxa a pedido na amostra | 52.0% |
| AUC fora da amostra (logística × boosting) | 0.616 × 0.646 |
| Pseudo-R² (McFadden) | 0.030 |
| Fator de maior amplitude | porte (15.2 p.p.) |
| Tempo | 128 s |

## Modelo das saídas a pedido

| Item | Valor |
| --- | --- |
| Desligamentos na amostra | 388,489 |
| Taxa a pedido na amostra | 52.0% |
| AUC fora da amostra (logística × boosting) | 0.616 × 0.646 |
| Pseudo-R² (McFadden) | 0.030 |
| Fator de maior amplitude | faixa_sal (10.0 p.p.) |
| Mercado: células ocupação × microrregião | 620 (313,848 desligamentos) |
| Mercado: +10% de salário relativo | -2.24 p.p. de saídas a pedido (p = 0.0002) |
| Tempo | 159 s |
