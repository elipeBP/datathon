# Log do pipeline

Execução: 2026-11-10 15:17

## Ingestão (R1–R2)

| Item | Valor |
| --- | --- |
| Linhas lidas | 3,397,416 |
| Colunas | 28 |
| Nulos em idade | 2,202 |
| Salário não numérico | 0 |
| Tempo de leitura | 3.5 s |
| Pico de memória do processo | 1,927 MB |

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
| R12 regiões | NÃO APLICADO (--sem-regioes). Rodar src/referencias.py com internet. |
| R12b CBO sem título | 131 linhas |
| R12b subclasse sem descrição | 0 linhas |
| Nulos em divisao_cnae | 0 |
| Nulos em cbo2002ocupacao | 0 |
| Nulos em grupo_setorial | 0 |
| Nulos em microrregiao | 1,139,633 |
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
| Recortes por microrregião, quadrantes e QL | PENDENTES: falta municipios_regioes.csv (V21) |
| Recortes por macrofamília | PENDENTES: falta macrofamilias.csv (Fase 2) |
| Tamanho de data/processed | 0.02 MB (limite 20 MB) |
