# Modelo das saídas a pedido

Pergunta: o que está **associado** a o trabalhador pedir para sair da indústria de transformação de SC (set/2025–ago/2026)? Dois níveis, porque cada um responde uma coisa diferente. Associação, não causa.

## Nível 1 — Mercado: pagar acima do mercado retém?

Unidade: célula ocupação (CBO) × microrregião com pelo menos 100 desligamentos e 30 salários válidos: 620 células, 313.848 desligamentos (75% da transformação). Desfecho: % das saídas a pedido na célula. Logit fracionário (GLM binomial ponderado pelos desligamentos), controles fixos de setor, mesorregião e grande grupo da ocupação, erros-padrão robustos (HC1).

**Resultado principal:** onde a mesma ocupação paga 10% acima da mediana da ocupação em SC, a parcela de saídas a pedido é **-2,2 p.p.** (p < 0,001), com os outros fatores fixos.

| Característica da célula | Efeito de +1 desvio-padrão | Significância |
| --- | --- | --- |
| % de mulheres | +4,69 p.p. | p < 0,001 |
| % com superior completo | -2,18 p.p. | p < 0,001 |
| % em empresas com 500 ou mais empregados | +2,05 p.p. | p < 0,001 |
| Salário da ocupação na região × mediana da ocupação em SC | -1,97 p.p. | p < 0,001 |
| Crescimento (saldo ÷ movimentações) | +1,17 p.p. | p = 0,086 |
| % de 14 a 24 anos | -0,95 p.p. | p = 0,140 |
| Prêmio de contratação (quem entra × quem sai) | +0,21 p.p. | p = 0,725 |

- O prêmio de contratação (quem entra × quem sai) **não se sustenta** com os controles (p = 0,725): confirma que era um sinal fraco. O que se associa às saídas é o nível do salário da ocupação na região em relação ao resto do estado, não a diferença entre quem entra e quem sai.
- Mercado aquecido (crescimento) puxa as saídas a pedido para cima (p = 0,086): sinal fraco, coerente com mercado apertado.
- Composição: células com mais mulheres e com mais empresas de 500+ empregados têm mais saídas a pedido; com mais superior completo, menos.

**Robustez do efeito do salário (+10%):**

| Recorte | Células | Efeito | p (salário) | p (prêmio) |
| --- | --- | --- | --- | --- |
| Principal (≥ 100 desligamentos) | 620 | -2,24 p.p. | p < 0,001 | p = 0,725 |
| Células com ≥ 50 desligamentos | 1069 | -1,78 p.p. | p < 0,001 | p = 0,697 |
| Células com ≥ 200 desligamentos | 340 | -2,50 p.p. | p = 0,001 | p = 0,804 |
| Sem o alimentador de linha (cbo 784205) | 601 | -3,14 p.p. | p < 0,001 | p = 0,807 |

## Nível 2 — Perfil: entre quem saiu, quem saiu a pedido?

- Amostra: 388.489 desligamentos com salário válido (celetista comum, R$ 1.000 a R$ 30.000) e escolaridade, idade e sexo identificados. Fora: aposentadoria, morte e tipo ignorado. Taxa a pedido na amostra: 52,0%.
- Fatores: salário relativo (÷ mediana do salário na mesma CBO × microrregião (≥ 30 salários válidos); senão, mediana estadual da CBO, em faixas), escolaridade, idade, sexo e tamanho da empresa. Controles fixos: setor, microrregião, grande grupo da ocupação e mês. Regressão logística, erros-padrão agrupados por ocupação × microrregião. Raça/cor fica fora.
- Validação fora da amostra (80/20): AUC da logística 0,616, gradient boosting 0,646. Pseudo-R² 0,030. O desfecho individual tem muito ruído: o objetivo é medir associações, não prever pessoas.
- Importância por permutação (boosting): Microrregião 0,059; Mês 0,034; Setor 0,028; Tamanho da empresa (empregados) 0,021; Salário em relação à mediana da ocupação na região 0,020; Grande grupo da ocupação 0,015; Idade 0,010; Escolaridade 0,009; Sexo 0,005.

| Fator | Nível | Prob. prevista | Diferença vs. referência | Taxa bruta | Razão de chances (IC 95%) | n |
| --- | --- | --- | --- | --- | --- | --- |
| Salário em relação à mediana da ocupação na região | 20% ou mais abaixo | 51,7% | -2,1 p.p. | 48,1% | 0,92 (0,87–0,97) | 23.601 |
| Salário em relação à mediana da ocupação na região | 10% a 20% abaixo | 54,1% | +0,3 p.p. | 52,9% | 1,01 (0,96–1,06) | 38.475 |
| Salário em relação à mediana da ocupação na região | 3% a 10% abaixo | 54,6% | +0,8 p.p. | 55,1% | 1,03 (0,98–1,08) | 65.110 |
| Salário em relação à mediana da ocupação na região | na mediana (±3%) | 53,9% | — | 55,5% | referência | 93.292 |
| Salário em relação à mediana da ocupação na região | 3% a 10% acima | 54,0% | +0,2 p.p. | 54,9% | 1,01 (0,95–1,07) | 56.745 |
| Salário em relação à mediana da ocupação na região | 10% a 20% acima | 51,4% | -2,5 p.p. | 51,4% | 0,90 (0,85–0,96) | 43.595 |
| Salário em relação à mediana da ocupação na região | 20% ou mais acima | 44,6% | -9,3 p.p. | 42,8% | 0,68 (0,64–0,72) | 67.671 |
| Idade | até 17 | 55,4% | +3,9 p.p. | 55,8% | 1,18 (1,09–1,27) | 5.022 |
| Idade | 18 a 24 | 54,4% | +2,9 p.p. | 55,7% | 1,13 (1,10–1,16) | 110.110 |
| Idade | 25 a 29 | 52,4% | +0,9 p.p. | 52,6% | 1,04 (1,01–1,06) | 74.907 |
| Idade | 30 a 39 | 51,5% | — | 51,0% | referência | 103.540 |
| Idade | 40 a 49 | 50,0% | -1,4 p.p. | 49,1% | 0,94 (0,92–0,97) | 62.911 |
| Idade | 50 ou mais | 47,9% | -3,5 p.p. | 46,2% | 0,86 (0,83–0,90) | 31.999 |
| Escolaridade | Até fundamental | 50,0% | -1,9 p.p. | 52,5% | 0,93 (0,89–0,96) | 82.778 |
| Escolaridade | Médio | 51,8% | — | 51,7% | referência | 271.558 |
| Escolaridade | Superior incompleto | 57,9% | +6,0 p.p. | 55,1% | 1,29 (1,24–1,34) | 13.551 |
| Escolaridade | Superior ou mais | 59,0% | +7,2 p.p. | 51,4% | 1,35 (1,30–1,41) | 20.602 |
| Sexo | Homem | 50,3% | — | 49,5% | referência | 230.631 |
| Sexo | Mulher | 54,6% | +4,3 p.p. | 55,6% | 1,20 (1,16–1,24) | 157.858 |
| Tamanho da empresa (empregados) | até 19 | 47,5% | -3,4 p.p. | 47,3% | 0,87 (0,83–0,91) | 83.567 |
| Tamanho da empresa (empregados) | 20 a 99 | 51,0% | +0,1 p.p. | 51,9% | 1,01 (0,96–1,05) | 95.299 |
| Tamanho da empresa (empregados) | 100 a 499 | 50,9% | — | 51,6% | referência | 90.277 |
| Tamanho da empresa (empregados) | 500 ou mais | 54,6% | +3,7 p.p. | 57,5% | 1,17 (1,10–1,23) | 86.611 |
| Tamanho da empresa (empregados) | não informado | 62,7% | +11,8 p.p. | 50,4% | 1,66 (1,20–2,30) | 32.735 |

Leitura do perfil:
- Jovens (18 a 24 anos), mulheres, quem tem superior completo e quem trabalha em empresas de 500+ empregados têm mais chance de a saída ter sido a pedido, na mesma ocupação e região.
- O salário relativo **não deve ser lido sozinho neste nível**: entre quem saiu, quem ganhava 20% ou mais acima da mediana saiu mais vezes por demissão sem justa causa (a empresa desliga mais quem custa mais). Por isso a pergunta "pagar mais retém?" é respondida no Nível 1, que compara mercados e não depende de quem a empresa escolheu demitir.
- "Tamanho da empresa: não informado" é cadastro incompleto, não um porte; fica fora da leitura.

## Limites

- Associação, não causa: o modelo não promete que aumentar o salário reduz as saídas.
- O CAGED não traz tempo de casa nem vagas abertas; parte do que aparece como salário ou idade é tempo de casa.
- O Nível 2 só olha quem saiu; o Nível 1 compara mercados, mas ainda dentro do fluxo de 12 meses.
- Células e limiares são escolhas da equipe; a tabela de robustez mostra que o resultado principal não depende deles.
