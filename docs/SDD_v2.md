# SDD v2 — Raio-X do Mercado de Trabalho Industrial de SC

Versão 2 · 10/11/2026 · Base: SDD v1 do Pietro. Nesta versão, os 14 pontos em aberto do v1 e mais 4 pontos novos estão fechados pela equipe (seção 2.2).

**O que mudou em relação ao v1:**

- Os pontos V1 a V18 estão fechados.
- As validações das macrofamílias passaram a se chamar M1 a M4, para não confundir com os pontos V.
- A base limpa saiu de `data/processed/` e foi para `data/interim/`, que fica fora do Git.
- As colunas são renomeadas para ASCII na ingestão.
- O LLM é o Gemini via API.
- As regiões e o mapa vêm da API do IBGE.
- Foi criada a tabela de grupos setoriais.
- A agregação dos KPIs 3 e 4 está definida.
- Os testes T2 e T5 foram operacionalizados.
- O roadmap tem 4 fases com checkpoints.
- O painel roda local e no Streamlit Community Cloud.
- O documento "contexto mestre" foi descartado: onde ele conflita com este SDD, vale o SDD.

---

## 0. Como usar este documento

Este SDD é o contrato do projeto. Nada é codado sem regra escrita aqui.

1. **Fase por fase.** Execute o roadmap da seção 10 uma fase por vez. No fim de cada fase, rode o aceite, escreva o relatório de checkpoint e **pare** até o usuário responder "pode seguir".
2. **Dúvida não se resolve no chute.** Se algo não estiver escrito aqui, ou se o dado contrariar este documento, pare e pergunte. Registre a dúvida como V19, V20… na seção 2.3.
3. **Diagnóstico antes de correção.** Antes de mudar um filtro ou uma fórmula, rode uma checagem somente leitura e mostre o número que justifica a mudança.
4. **Tudo parametrizado.** Seções CNAE, janela, volumes mínimos, cortes e nome do modelo ficam em `config.py`. Mudar uma decisão é trocar uma linha.
5. **Premissa declarada.** Toda escolha que a banca pode questionar vira uma linha em "Premissas e limites" no README. A seção 11 lista as já conhecidas.
6. **Valores de referência.** A seção 3 traz números já verificados no arquivo. Se o pipeline não reproduzir algum deles dentro da tolerância, pare e mostre a diferença.
7. **Limiares são julgamento, não referência.** Os cortes de 5 p.p., os volumes mínimos e o QL de 1,25 foram escolhidos pela equipe. Use-os, e imprima a sensibilidade sempre que este documento pedir.

---

## 1. Contexto, cliente e tese

**Pergunta central (Guia do Participante):** "Quais regiões e setores industriais de Santa Catarina estão enfrentando apagão de mão de obra ou expansão acelerada, e como os indicadores de renda e escolaridade explicam esses gargalos?"

**Cliente:** FIESC. Quem executa a recomendação de formação é o SENAI-SC. A equipe atua como consultoria de dados.

**O que o diretor precisa conseguir fazer no painel (Guia, seção 2.3):**

1. **Localizar** as regiões e os setores que pedem atenção urgente.
2. **Entender a causa raiz:** salário, escolaridade ou rotatividade.
3. **Decidir:** ler 3 recomendações práticas ligadas às macrofamílias de CBO.

**Critérios da banca** (pesos não divulgados, tratar como iguais): compreensão do problema e do contexto industrial; embasamento analítico com premissas e limites; dashboard e storytelling; recomendações ligadas às macrofamílias geradas por IA; pitch de 3 minutos.

**O que "apagão" significa aqui.** O CAGED mede fluxo (admissões e desligamentos), não vagas abertas, estoque de emprego nem desemprego. Por isso o apagão não é medido diretamente: usamos sinais indiretos de aperto do mercado, e o pitch diz isso em voz alta.

**Tese a testar: "retenção, não escassez".** A indústria de transformação de SC quase não cresce em saldo, mas metade dos desligamentos é a pedido do trabalhador. Isso é hipótese até passar nos testes da seção 7.

**Hipóteses:**

- H1: o gargalo da transformação é retenção (saídas a pedido), não falta de gente.
- H2: a expansão é pontual, concentrada em poucos municípios e empregadores.
- H3: há descasamento de escolaridade e salário em ocupações técnicas (admitidos com menos formação ou mais baratos que os desligados).

---

## 2. Decisões

### 2.1. Decisões de desenho (do v1)

| # | Decisão | Escolha |
| --- | --- | --- |
| D1 | Cenário | Diagnóstico em 3 camadas: Onde → Por quê → O quê |
| D2 | Tese | Retenção, não escassez (validar com T2) |
| D3 | Indústria | Pipeline com seções B–F; análise principal na seção C; construção (F) como segmento separado |
| D4 | Janela | `competenciamov` de 202509 a 202608 |
| D5 | Salário | Coluna `salario` (já mensal); ignorar `valorsalariofixo` |
| D6 | Estatística de salário | Mediana, nunca média |
| D7 | IA | Gemini com lista fechada de categorias, temperatura 0 e revisão humana |
| D8 | Dashboard | Streamlit lendo só tabelas agregadas; roda local e no Streamlit Community Cloud |

### 2.2. Pontos fechados (V1 a V18)

| # | Ponto | Decisão final | Evidência ou motivo |
| --- | --- | --- | --- |
| V1 | Definição de indústria | Igual a D3. A equipe ainda pergunta à comissão, mas isso não bloqueia nada | % de saídas a pedido: C 50,9%, B–E 50,6%, F 38,2%. A tese não depende de C vs B–E; F é diferente e fica separada |
| V2 | Exclusões (MOV x EX) | Assumir que a base já veio filtrada. Regra R6 condicional. Declarar no README | O arquivo não tem coluna de exclusão; a reconciliação com a FIESC fecha em até 0,2% |
| V3 | Horário do pitch | 13/11 às 10:00 (deck oficial do evento). Escopo congela em 12/11 às 18h | O edital diz 10:00 e o Guia diz 10:30; usamos o mais cedo |
| V4 | Recorte territorial | Microrregião do IBGE (20 em SC) como recorte principal; mesorregião (6) como cor e agrupamento. Fonte: API do IBGE (R12) | O Guia fala em "microrregiões"; os nomes são reconhecíveis pela banca |
| V5 | Corte do teste de composição | 5 p.p. O notebook mostra a distribuição completa das diferenças | Julgamento da equipe |
| V6 | Volumes mínimos | Os da seção 5. Se T4 reprovar, subir para 500 | Julgamento da equipe; T4 calibra |
| V7 | Corte do QL | 1,25 com 1.000 movimentos ou mais. Imprimir quantos polos surgem com 1,1, 1,25 e 1,5. Prioridade baixa: só entra se sobrar tempo | Julgamento da equipe |
| V8 | Faixa salarial | R$ 1.000 a R$ 30.000, mais as regras R8 e R9 | Em C, R8+R9 mantêm 786.129 de 835.866 linhas; mediana de admissão vai de R$ 2.176 para R$ 2.200; prêmio vai de 0,967 para 0,966; só 150 linhas entre R$ 30 mil e R$ 60 mil |
| V9 | Lista de macrofamílias | Lista do v1 com "Gestão e administrativo" renomeada para "Gestão, administrativo e comercial", mais uma 15ª área, "Cerâmica, vidro e minerais" (seção 6.2) | 64% dos movimentos de B–F são do grande grupo 7 (produção); as áreas por ramo são o que divide esse bloco. Sem a 15ª área, as ocupações do polo cerâmico do Sul cairiam de forma inconsistente em outras áreas |
| V10 | Duplicatas | **Manter.** Explicar no README | Em C há 22.211 linhas idênticas com saldo de +13.295. Removê-las levaria o saldo de C de +1.008 para cerca de −12.287. A reconciliação com a FIESC (diferença de +2) foi feita com elas, então os números oficiais as contam. Provável causa: contratações em lote no mesmo cargo e salário |
| V11 | População | Censo 2022 | O top 10 de saldo por 10 mil habitantes só muda na 10ª posição (Pinhalzinho troca com Caxambu do Sul) |
| V12 | Julho/2026 | Usar o arquivo, citar a fonte e pôr uma nota no README | São 280 vagas de diferença no estado; o painel usa o acumulado de 12 meses |
| V13 | API de LLM | Gemini via API (seção 6.3), com classificação no chat como plano B (seção 6.6) | Plano gratuito; cerca de 8 chamadas no total |
| V14 | Se a tese reprovar no T2 | O agente não trava: roda, reporta no checkpoint e segue. Tese padrão se reprovar: "retenção em ocupações de linha". A frase final do pitch é decisão da equipe | O painel já permite as duas leituras (setor ou macrofamília) |
| V15 | Grupos setoriais | Tabela R14 | Linguagem do cliente (boletim FIESC). Se a equipe conseguir o boletim, ajustar os nomes |
| V16 | Agregação dos KPIs 3 e 4 | Seção 5.2 | Evita médias de grupos pequenos e controla a composição de ocupações |
| V17 | Scripts de diagnóstico do v1 | Se o Pietro tiver, sobem em `diagnostics/`. Se não, o agente recria a partir das descrições abaixo | Rastreabilidade dos fatos da seção 3 |
| V18 | Slides do pitch | Fora do escopo do agente. O agente exporta os gráficos principais em PNG em `reports/figures/` | A equipe monta os slides |

**Descrição dos scripts de diagnóstico (V17), caso precisem ser recriados.** Todos são somente leitura:

- `diag_caged.py` mede a estrutura do arquivo: linhas, nulos, códigos, janela, duplicatas e linhas fora do prazo.
- `diag2_caged.py` calcula o comportamento por recorte: movimentos, saldo, % a pedido, mediana salarial e prêmio por seção e por divisão.
- `diag3_sensibilidade.py` é o teste T5.

### 2.3. Novos pontos

Durante o trabalho, adicione aqui uma linha V19, V20… e avise o usuário antes de seguir.

| # | Dúvida | Por que importa | Padrão provisório | Status |
| --- | --- | --- | --- | --- |
| V19 | T1 reprova na construção por margem mínima: saldo jan–mai/26 de 10.775 contra 10.721 da FIESC (+54, 0,504%; tolerância 0,5%). C, B–E e B–F passam | O SDD manda parar se o T1 reprovar. A seção 3 já registrava esses mesmos +54 como fato aceito | Manter 0,5% e declarar a diferença no README. Os filtros não têm erro: os outros 27 valores de referência bateram | **Fechado (Pietro, 10/11):** só declarar no README; T1 da construção fica registrado como reprovado e aceito |
| V20 | 9 CBOs do arquivo não existem no dicionário do evento (131 linhas em B–F, ex.: 142360, 514335, 782420) | Sem título, o LLM não tem o que classificar | Mandar ao LLM só o código, com confiança baixa forçada (vai para revisão M1) | **Fechado (Pietro, 10/11):** aprovado |
| V21 | A API do IBGE não é acessível do ambiente onde a Fase 1 foi montada | Sem ela não há microrregião, mesorregião nem GeoJSON (aceite 4.7) | Rodar `python src/referencias.py` e depois `python run_pipeline.py` numa máquina com internet | **Fechado (11/11):** rodado no Windows; 295 municípios, 20 microrregiões, 6 mesorregiões, zero nulo; GeoJSON de 0,78 MB. T4 (r = 0,80) e T5 (0 troca no top 5) aprovados |
| V22 | Pela regra M4, 751 das 1.578 CBOs de B–F não têm vizinha classificada na mesma família e ficam como "Outros" | Ficam fora das recomendações | Peso pequeno: 2,44% dos movimentos, nenhuma com mais de 271 movimentos. Alternativa, se a equipe quiser: herdar pelo subgrupo de 3 dígitos (cobriria mais 1,44% dos movimentos) | Informativo: mantida a regra do SDD |
| V23 | A tese "de setor" passou no T2b por pouco: amplitude padronizada de 5,6 p.p. contra o corte de 5 p.p. A amplitude observada é 13,3 p.p., então a mistura de ocupações explica cerca de 58% da diferença entre divisões. O T3 reprovou: sem o alimentador de linha, a madeira cai de 54,2% para 48,5% (3º → 7º) | Define a frase central do pitch (V14) | Pelo SDD a tese de setor sobrevive. Sugestão: dizer as duas coisas — o setor pesa, mas a maior parte vem das ocupações de linha | Aguardando a equipe |
| V24 | Cada recomendação ganhou o campo `indicador_de_acompanhamento` (KPI, linha de base de hoje, referência de SC e fonte), além do formato da seção 8.3 | O pitch para os diretores do SENAI vai focar na decisão e no resultado; o indicador mostra como medir se a decisão funcionou, sem inventar metas | Campo adicional; o formato 8.3 continua igual | Informativo: pedido do Pietro (foco do pitch) |
| V25 | O GeoJSON do IBGE vem com os anéis no sentido da RFC 7946 (externo anti-horário); o Plotly (d3-geo) exige o contrário, e o mapa pintava o fundo inteiro | Sem isso o mapa coroplético fica inutilizável | `referencias.orientar_para_plotly()` reorienta os anéis ao baixar; nenhuma geometria é alterada | Fechado (11/11): corrigido e conferido no PNG |
| V26 | `src/ingest.py` usava `import resource` (só Linux/macOS); o pipeline quebrava no Windows. O ambiente da equipe tem Python 3.13 | Rodar do zero na máquina da equipe | Pico de memória medido pela API do Windows; as versões fixadas do `requirements.txt` instalam e rodam no 3.13 | Fechado (11/11) |
| V27 | O mapa só mostrava o KPI 1; o lado "expansão acelerada" da pergunta central não tinha mapa | Critério 1 e 3 da banca | Seletor na página Onde: KPI 1 (apagão) ou KPI 2 (expansão); PNG `05_mapa_saldo_microrregioes.png` | Fechado (11/11) |
| V29 | Modelo estatístico das saídas a pedido, pedido pela equipe em 12/11 (após o congelamento de escopo) | Responde "como renda e escolaridade explicam" com controles, não só médias | Dois níveis: mercado (logit fracionário em células CBO × microrregião) e perfil (logística individual + benchmark de gradient boosting). O nível individual sofre seleção (quem ganha bem acima da mediana sai mais por demissão), por isso o efeito do salário é lido no nível de mercado | Fechado (12/11): `src/modelo.py`, `reports/modelo_saida_pedido.md` |
| V28 | O `gemini-3.8-flash` respondeu 503 (alta demanda) repetidamente e depois 429 (limite do plano gratuito), com 2 de 8 lotes prontos | Misturar dois modelos na mesma classificação enfraquece a validação (T6) | Refazer os 8 lotes no modelo reserva `gemini-3.5-flash-lite`; os 2 lotes do 3.8 guardados à parte, sem uso. Esperas maiores para 503 (`LLM_ESPERAS_503`) | Fechado (11/11, decisão da equipe) |

---

## 3. Fatos verificados (valores de referência)

Use estes números para conferir o pipeline. A tolerância é zero para contagens e ±0,1 p.p. para percentuais. Os itens marcados como "v1" vieram do diagnóstico do Pietro e não foram reconferidos nesta versão, então o pipeline deve reproduzi-los e confirmá-los.

**Estrutura do arquivo `Novo_Caged_MOV_Limpo.csv`:**

| Fato | Valor |
| --- | --- |
| Formato | Separador `;`, decimal `,` (em `salário` e `horascontratuais`), UTF-8, CRLF |
| Coluna `idade` | Decimal com **ponto** (ex.: `40.0`) |
| Linhas totais | 3.397.416 |
| Linhas fora da janela 202509–202608 | 6.128 (declarações atrasadas) |
| Linhas idênticas (sem as 2 colunas de índice, arquivo inteiro) | 97.635 |
| Linhas fora do prazo (`indicadordeforadoprazo = 1`) | 36.940 |
| Nulos | Só em `idade`: 2.202 (v1) |
| CBO com 5 dígitos (zero à esquerda perdido) | 7 linhas |
| Subclasse com 6 dígitos | Todas as linhas das seções A e B |
| Admissões com tipo 97 ("ignorado") | 1.718.686 de 1.719.449 (99,96%). O restante é tipo 35. Não há tipos 10, 20, 70 nem 80 |
| Salário zero (na janela, todas as seções) | 33.854 |
| Salário máximo | R$ 3.471.600,00 |
| Colunas de exclusão | Não existem |
| Municípios | Todos os 295 casam com o CSV de municípios via código IBGE de 7 dígitos ÷ 10 |

**Comportamento (12 meses, set/2025–ago/2026):**

| Recorte | Movimentos | Saldo | % saídas a pedido | Salário mediano de admissão (sem filtros) |
| --- | --- | --- | --- | --- |
| Transformação (C) | 835.866 | +1.008 | 50,9% | R$ 2.175,80 |
| Indústria geral (B–E) | 867.570 | +1.112 | 50,6% | R$ 2.175,80 |
| Construção (F) | 272.063 | +1.533 | 38,2% | R$ 2.561,05 |

**Outros fatos:**

- C após R8+R9: 786.129 linhas; mediana de admissão R$ 2.200; de desligamento R$ 2.277; prêmio 0,966.
- Duplicatas em C: 22.211 linhas, com saldo de +13.295.
- CBOs necessárias para cobrir 95% dos movimentos de B–F: 354.
- Na transformação, 189 municípios têm 300 movimentos ou mais.
- A CBO 784205 (alimentador de linha de produção) tem cerca de 202 mil movimentos e saldo de +15,7 mil. Sem ela, a transformação fecha em cerca de −14,7 mil (v1).
- Sazonalidade na transformação: dezembro −20,2 mil; janeiro a março +22,8 mil (v1).
- % de saídas a pedido por divisão: alimentos 56,5%, confecção 55,7%, madeira 54,2%, produtos de metal 43,3% (v1).
- O prêmio de contratação fica entre 0,91 e 1,00 nas 14 maiores divisões (v1).
- Os admitidos têm de 0,4 a 1,1 p.p. menos de ensino superior que os desligados nas 14 maiores divisões (v1).
- 10 municípios concentram 37% do volume industrial (v1).

**Reconciliação com o oficial (saldo jan–mai/2026), referência do teste T1:**

| Grupo | Boletim FIESC | Arquivo | Diferença |
| --- | --- | --- | --- |
| Transformação (C) | 24.269 | 24.271 | +2 |
| Indústria geral (B–E) | 24.527 | 24.536 | +9 |
| Construção (F) | 10.721 | 10.775 | +54 |
| Indústria total (B–F) | 35.248 | 35.311 | +63 |

---

## 4. Contrato de dados

Toda análise parte de uma única base limpa, `data/interim/caged_ind.parquet`, gerada pelas regras abaixo, nesta ordem. Ninguém calcula KPI a partir do CSV bruto. Cada filtro registra em `reports/log_pipeline.md` quantas linhas entraram e quantas saíram.

### 4.1. Ingestão

- **R1. Leitura.** Ler `data/raw/Novo_Caged_MOV_Limpo.csv` com `;`, UTF-8 e **todas as colunas como texto**. O arquivo tem 413 MB e 3,4 milhões de linhas, então use uma leitura eficiente em memória: Polars com `infer_schema_length=0`, ou pandas com dtype `string[pyarrow]`. Evite `dtype=str` puro do pandas, que pode estourar a memória num notebook de 8 GB. Meça o pico de memória e registre no log. Descarte `Unnamed: 0.1` e `Unnamed: 0`. Salve `data/interim/caged_raw.parquet` para nunca mais reler o CSV.
- **R1b. Nomes de colunas.** Renomeie para ASCII snake_case com um mapa explícito em `config.py`: `competênciamov` → `competenciamov`, `região` → `regiao`, `município` → `municipio`, `seção` → `secao`, `saldomovimentação` → `saldomovimentacao`, `cbo2002ocupação` → `cbo2002ocupacao`, `graudeinstrução` → `graudeinstrucao`, `raçacor` → `racacor`, `tipomovimentação` → `tipomovimentacao`, `tipodedeficiência` → `tipodedeficiencia`, `salário` → `salario`, `origemdainformação` → `origemdainformacao`, `competênciadec` → `competenciadec`, `unidadesaláriocódigo` → `unidadesalariocodigo`, `valorsaláriofixo` → `valorsalariofixo`. As demais colunas já são ASCII. Daqui em diante, este documento usa só os nomes novos.
- **R2. Números.** Em `salario` e `horascontratuais`, troque `,` por `.` e converta para float. Em `idade`, que já usa ponto, converta para float e depois para inteiro anulável. `saldomovimentacao` vira inteiro (1 ou −1). **Códigos nunca viram inteiro.**
- **R3. Padronização.** `subclasse` com `zfill(7)`; `cbo2002ocupacao` com `zfill(6)`. Derive `divisao_cnae` com os 2 primeiros dígitos da subclasse e `grande_grupo_cbo` com o 1º dígito da CBO.

### 4.2. Filtros

- **R4. Janela.** `competenciamov` entre `202509` e `202608` (comparação de texto funciona porque o formato é AAAAMM).
- **R5. Seções.** `SECOES = ['B','C','D','E','F']` e `SECAO_PRINCIPAL = 'C'` em `config.py`. Crie a coluna `segmento`: C → "Transformação"; B, D e E → "Extrativa e utilidades"; F → "Construção".
- **R6. Exclusões.** Se uma versão nova do arquivo trouxer `indicadordeexclusão`, remova as linhas com valor 1. Hoje a coluna não existe (V2).
- **R7. Não remover** duplicatas nem linhas fora do prazo (V10). Registre as contagens no log e no README.

### 4.3. Base de salário

Use uma coluna booleana `valido_salario` na mesma base, em vez de criar outra tabela.

- **R8.** `valido_salario` só é verdadeiro se `categoria = '101'`, `indtrabintermitente = '0'`, `indtrabparcial = '0'` e `indicadoraprendiz = '0'`.
- **R9.** Além disso, o salário precisa estar entre `SAL_MIN = 1000` e `SAL_MAX = 30000`. Fora disso, a linha continua na base de contagem e só sai dos cálculos de salário.

### 4.4. Escolaridade

- **R10.** Recodifique `graudeinstrucao` em `faixa_escolaridade`. **Nunca use o código como número** (o código 80, pós-graduação, ficaria "maior" que doutorado). O dicionário oficial é: 1 analfabeto; 2 a 5 fundamental incompleto ou completo; **6 médio INCOMPLETO; 7 médio completo; 8 superior INCOMPLETO; 9 superior completo**; 10 mestrado; 11 doutorado; 80 pós-graduação; 99 não identificado.

| Faixa | Códigos |
| --- | --- |
| Até fundamental | 1, 2, 3, 4, 5 |
| Médio | 6, 7 |
| Superior incompleto | 8 |
| Superior ou mais | 9, 10, 11, 80 |
| Não identificado | 99 (fica fora dos denominadores do KPI 4) |

### 4.5. Junções e referências

- **R11. Municípios.** Leia `data/raw/Municipios_SC_limpo.csv` mantendo só as linhas cujo `Código [-]` casa com `^42\d{5}$`. Isso remove o rodapé HTML. Nas colunas numéricas, troque `'-'` por nulo e converta com `errors='coerce'`. A chave é `cod6` = código de 7 dígitos ÷ 10, ou seja, os 6 primeiros caracteres. A população usada é a do Censo 2022 (`População no último censo - pessoas [2022]`). Aceite: 295 municípios casados.
- **R12. Regiões e mapa** (`src/referencias.py`, roda uma vez e salva o resultado no Git):
  - Da API de localidades do IBGE, baixe a lista de municípios de SC com microrregião e mesorregião. Ponto de partida: `https://servicodados.ibge.gov.br/api/v1/localidades/estados/42/municipios`. Salve em `data/reference/municipios_regioes.csv` com as colunas `cod7, cod6, municipio, cod_microrregiao, microrregiao, cod_mesorregiao, mesorregiao`.
  - Da API de malhas do IBGE, baixe o GeoJSON das microrregiões de SC. Ponto de partida: `https://servicodados.ibge.gov.br/api/v3/malhas/estados/42?intrarregiao=microrregiao&formato=application/vnd.geo+json`. Salve em `data/reference/sc_microrregioes.geojson`. Se o arquivo passar de 5 MB, simplifique a geometria.
  - Confira os endereços e o formato na documentação (`servicodados.ibge.gov.br/api/docs`) antes de usar. URLs ficam em `config.py`.
  - Aceite: 295 municípios, 20 microrregiões, 6 mesorregiões, zero nulo. Se algum município vier sem microrregião, **pare e reporte; não atribua no chute**.
- **R12b. Dicionário.** Extraia de `data/raw/Dicionario_de_dados.xlsx` as abas `cbo2002ocupação` e `subclasse` para `data/reference/cbo_titulos.csv` e `data/reference/subclasse_descricao.csv`, já padronizadas com `zfill`.
- **R13. Não usar** do CSV de municípios: mortalidade infantil (42% vazia), finanças municipais (erro em Laurentino) e PIB per capita como medida de renda (distorcido por porto e indústria).

### 4.6. Grupos setoriais

- **R14.** Crie `grupo_setorial` a partir de `divisao_cnae` (tabela em `config.py`):

| Grupo setorial | Divisões CNAE |
| --- | --- |
| Alimentos e bebidas | 10, 11 |
| Têxtil, confecção e calçados | 13, 14, 15 |
| Madeira e móveis | 16, 31 |
| Papel, celulose e gráfica | 17, 18 |
| Química e farmacêutica | 19, 20, 21 |
| Plástico e borracha | 22 |
| Minerais não metálicos e cerâmica | 23 |
| Metalmecânica | 24, 25, 28, 29, 30, 33 |
| Eletroeletrônica | 26, 27 |
| Outras da transformação | 12, 32 |
| Extrativa | 05 a 09 (seção B) |
| Utilidades | 35 a 39 (seções D e E) |
| Construção | 41 a 43 (seção F) |

### 4.7. Saída e aceite

`data/interim/caged_ind.parquet` contém só as seções B–F, só a janela definida e todas as colunas originais renomeadas, mais: `segmento`, `grupo_setorial`, `divisao_cnae`, `grande_grupo_cbo`, `faixa_escolaridade`, `valido_salario`, `cod_microrregiao`, `microrregiao`, `mesorregiao`, `titulo_cbo` e `descricao_subclasse`.

**Aceite do contrato:**

- T1 aprovado.
- 295 municípios casados.
- Zero nulo em `divisao_cnae`, `cbo2002ocupacao`, `grupo_setorial` e `microrregiao`.
- Os números da seção 3 reproduzidos.

---

## 5. KPIs

### 5.1. Definições

O painel mostra 4 KPIs (o Guia exige 3). O KPI 1 carrega a tese. Os KPIs 3 e 4 explicam a causa raiz e nunca são usados sozinhos para afirmar apagão.

| KPI | Pergunta | Fórmula | Base | Volume mínimo |
| --- | --- | --- | --- | --- |
| 1. % de saídas a pedido | O trabalhador está saindo por conta própria? | desligamentos com `tipomovimentacao = '40'` ÷ total de desligamentos | Contagem | `MIN_DESL = 300` desligamentos |
| 2. Saldo por 10 mil hab. | Onde há expansão ou encolhimento? | (admissões − desligamentos) ÷ população do Censo 2022 do recorte × 10.000 | Contagem | `MIN_MOV = 300` movimentos |
| 3. Prêmio de contratação | A empresa paga mais para repor? | Mediana do salário de admissão ÷ mediana do salário de desligamento, por célula (5.2) | Salário (`valido_salario`) | `MIN_ADM_SAL = 50` e `MIN_DESL_SAL = 50` por célula |
| 4. Descasamento de escolaridade | Quem entra tem menos formação que quem sai? | % "Superior ou mais" nos admitidos − % nos desligados, em p.p., por célula (5.2) | Contagem, sem o código 99 | `MIN_ADM_ESC = 100` e `MIN_DESL_ESC = 100` por célula |

### 5.2. Agregação dos KPIs 3 e 4 (V16)

Os KPIs 3 e 4 são sempre calculados dentro da mesma ocupação, para não confundir efeito de setor com efeito de mistura de cargos.

1. A **célula** é a combinação CBO × microrregião.
2. Só entram as células que atingem o volume mínimo do KPI.
3. Para qualquer recorte maior (microrregião, grupo setorial, macrofamília ou o estado), o KPI é a **média ponderada das células elegíveis do recorte**. O peso é o número de movimentos da célula na base usada pelo KPI.
4. Ao lado do KPI, mostre sempre a **cobertura**: o percentual dos movimentos do recorte que caiu em células elegíveis.
5. Se o recorte não tiver nenhuma célula elegível, ele aparece em cinza com o rótulo "amostra insuficiente".

### 5.3. Regras de leitura

- Os KPIs 1 e 3 são lidos como **posição relativa ao estado** (acima ou abaixo da mediana de SC), nunca contra um corte absoluto. No estado, o prêmio é 0,966: "acima de 1" quase não acontece.
- Um recorte abaixo do volume mínimo aparece em cinza com o rótulo "amostra insuficiente" e nunca entra em ranking.
- O saldo é sempre o acumulado de 12 meses, nunca um mês isolado.
- Todo KPI é mostrado com o volume (n) ao lado.
- Escolaridade e salário são "associados" ao gargalo; nunca "causam".

### 5.4. Quadrantes

A unidade do gráfico é microrregião × grupo setorial, e só entram as unidades que atingem `MIN_MOV` e `MIN_DESL`. O eixo X é o KPI 2 e o eixo Y é o KPI 1. As linhas de corte ficam na mediana das unidades elegíveis.

| Quadrante | Saldo | Saídas a pedido | Leitura para o cliente |
| --- | --- | --- | --- |
| Expansão sob pressão | Acima | Acima | Cresce e perde gente: o sinal mais próximo de "apagão" |
| Expansão saudável | Acima | Abaixo | Cresce e retém |
| Retenção problemática | Abaixo | Acima | Não cresce e perde gente: foco da tese |
| Estagnado | Abaixo | Abaixo | Baixa dinâmica |

### 5.5. Quociente locacional (opcional, prioridade baixa)

```latex
QL_{s,r} = \frac{mov_{s,r} / mov_{r}}{mov_{s,SC} / mov_{SC}}
```

Aqui `mov` é o número de movimentos (proxy de emprego), `s` é o grupo setorial e `r` é a microrregião. Um QL acima de `QL_CORTE = 1,25`, com `QL_MIN_MOV = 1000` movimentos ou mais, marca um polo. Imprima quantos polos surgem com 1,1, 1,25 e 1,5.

---

## 6. Macrofamílias de CBO com IA generativa (Gemini)

### 6.1. Escopo

O LLM classifica as CBOs que cobrem `COBERTURA_CBO = 0,95` dos movimentos de B–F (cerca de 354 CBOs). As demais herdam a classificação pela regra M4. O resultado é `data/reference/macrofamilias.csv`, versionado no Git e revisado por humanos. O painel lê só esse CSV.

### 6.2. Taxonomia (lista fechada, decisão V9)

A taxonomia tem duas dimensões, no formato do Mapa do Trabalho Industrial (SENAI/CNI).

**Área (15 valores).** Regra para o modelo: se a ocupação é específica de um ramo (ex.: magarefe, costureira industrial), use a área do ramo; se é genérica de produção (ex.: alimentador de linha, embalador), use "Operação de linha e montagem".

| Área | O que entra |
| --- | --- |
| Alimentos e bebidas | Ocupações específicas do processamento de alimentos e bebidas: abate, desossa, laticínios, panificação industrial |
| Têxtil, confecção e calçados | Fiação, tecelagem, corte, costura, acabamento, calçados |
| Metalmecânica e soldagem | Usinagem, caldeiraria, soldagem, fundição, estamparia, montagem mecânica especializada |
| Manutenção industrial | Mecânicos, eletricistas e eletromecânicos de manutenção, lubrificadores |
| Eletroeletrônica e automação | Montagem e operação eletroeletrônica, instrumentação, automação, bobinagem |
| Madeira e móveis | Serraria, marcenaria, montagem de móveis |
| Plástico, borracha e química | Operação de injetoras e extrusoras, processos químicos |
| Cerâmica, vidro e minerais | Fabricação de cerâmica, porcelanato, louça, vidro, cimento e artefatos de minerais não metálicos |
| Logística e movimentação | Motoristas, operadores de empilhadeira, almoxarifes, conferentes, expedição |
| Operação de linha e montagem | Funções genéricas de produção: alimentadores de linha, operadores de máquina não específicos, montadores, embaladores |
| Construção | Pedreiros, serventes de obra, carpinteiros de obra, armadores, instaladores prediais |
| Qualidade e controle | Inspeção, controle de qualidade, laboratório, segurança do trabalho |
| Gestão, administrativo e comercial | Gerentes, supervisores administrativos, escritório, RH, finanças, compras, vendas, representantes |
| Engenharia e P&D | Engenheiros, projetistas, desenvolvedores, químicos, pesquisadores |
| Serviços de apoio | Limpeza, portaria, vigilância, cozinha, conservação |

**Nível de formação (4 valores):**

| Nível | Definição |
| --- | --- |
| Qualificação até 200h | Aprende no posto ou em curso curto (ex.: alimentador de linha, embalador, servente) |
| Qualificação acima de 200h | Ofício que exige curso de qualificação longo ou prática prolongada (ex.: soldador, eletricista de manutenção, operador de CNC) |
| Técnico | Curso técnico de nível médio (ex.: técnico em eletrotécnica, técnico de segurança do trabalho) |
| Superior | Graduação (ex.: engenheiros, analistas, contadores) |

### 6.3. Implementação com Gemini (`src/macrofamilias.py`)

- **SDK:** `google-genai` (`from google import genai`). A chave fica em `GEMINI_API_KEY` no `.env`, carregada com `python-dotenv`.
- **Modelo:** o nome fica em `GEMINI_MODEL` no `config.py`. Antes de rodar, consulte `ai.google.dev` para saber qual é o modelo Flash mais recente disponível no plano gratuito, e registre o nome exato em `prompts/macrofamilias_v1.md`.
- **Saída estruturada obrigatória:** `response_mime_type = "application/json"` e `response_schema` definido como um modelo Pydantic em que `area`, `nivel` e `confianca` são **enums** com os valores exatos da seção 6.2. Isso impede o modelo de inventar categorias.
- **Esquema de cada item:** `cbo` (texto), `area` (enum), `nivel` (enum), `confianca` (enum: `alta`, `media`, `baixa`) e `justificativa` (texto de até 15 palavras).
- **Configuração da chamada:** temperatura 0. Lotes de `LOTE_LLM = 50` CBOs.
- **Conferência do conjunto:** o conjunto de CBOs devolvido precisa ser exatamente igual ao enviado. Se não for, refaça o lote (no máximo 3 tentativas); se ainda falhar, marque o lote para classificação manual.
- **Erros de limite:** nos erros 429 e 503, tente de novo com espera exponencial.
- **Cache:** salve a resposta bruta de cada lote em `data/interim/llm_cache/lote_XX.json`. Se o arquivo já existir, não chame a API de novo.
- **Interruptor:** `RODAR_LLM = False` por padrão em `config.py`. Assim, o notebook e o pipeline só leem `macrofamilias.csv`, e quem clonar o repositório roda tudo sem chave. Com `True`, as chamadas são refeitas.
- **Saída:** `data/reference/macrofamilias.csv` com as colunas `cbo, titulo_cbo, area, nivel, confianca, justificativa, origem, revisado`. A coluna `origem` assume `llm`, `heranca`, `manual` ou `outros`.

### 6.4. Regras do prompt

1. **Entrada por CBO:** código, título oficial (`cbo_titulos.csv`), grande grupo (1º dígito) com o nome, a seção CNAE e o grupo setorial onde a CBO mais aparece, e o número de movimentos.
2. **Lista fechada:** o modelo só escolhe valores da taxonomia, com as definições da seção 6.2 dentro do prompt. Nunca gera código de CBO nem cria categoria.
3. **Exemplos:** 3 exemplos resolvidos dentro do prompt. Um operacional (use CBO 784205, alimentador de linha de produção → Operação de linha e montagem / Qualificação até 200h), um técnico (do grande grupo 3) e um superior (do grande grupo 2), os dois últimos escolhidos entre as CBOs mais frequentes, usando o título do dicionário.
4. **Dúvida:** "Em caso de dúvida, escolha a opção mais próxima e marque a confiança como baixa."
5. **Registro:** o prompt completo, o modelo, a data e a versão ficam em `prompts/macrofamilias_v1.md`. O notebook mostra o prompt e o código da chamada.

### 6.5. Validação (obrigatória antes de usar no painel)

- **M1.** Toda CBO com confiança baixa vai para a lista de revisão.
- **M2.** Coerência com o grande grupo: o grupo 2 deve cair em "Superior"; o grupo 3 em "Técnico"; os grupos 7, 8 e 9 em um dos dois níveis de "Qualificação". Toda divergência vai para a lista de revisão.
- **M3.** Amostra aleatória de 30 CBOs (com seed fixa) em `reports/revisao_macrofamilias.csv`, com as colunas `revisor_1_area`, `revisor_1_nivel`, `revisor_2_area` e `revisor_2_nivel` vazias para duas pessoas preencherem. Quando a planilha voltar preenchida, o agente calcula a concordância. Se ficar abaixo de 85%, ajuste o prompt (v2), rode de novo e repita.
- **M4.** As CBOs fora do escopo herdam a classificação mais frequente (ponderada por movimentos) entre as CBOs já classificadas da mesma família (4 primeiros dígitos), com `origem = heranca`. Sem vizinho, ficam como "Outros", com `origem = outros`, e não entram em recomendação.

### 6.6. Plano B (sem chave ou com a API fora do ar)

Exporte `data/interim/cbos_para_classificar.csv` e o prompt pronto para colar no Google AI Studio (ou em outro chat de LLM). Importe a resposta com as mesmas validações. O Guia permite. Registre o caminho usado no README.

### 6.7. Segurança

A chave fica só no `.env`, que está no `.gitignore`. Nunca imprima a chave, nunca a escreva em notebook, log ou commit. Um repositório público com chave exposta equivale a uma chave vazada. Mantenha um `.env.example` com `GEMINI_API_KEY=` vazio.

---

## 7. Testes de validação

`src/testes.py` roda os testes e escreve `reports/testes.md` com data, número obtido, critério e o resultado (aprovado ou reprovado). Nenhuma afirmação entra no pitch sem passar no teste correspondente. Teste reprovado: reporte no checkpoint e siga a coluna "Se reprovar".

| Teste | O que verifica | Como rodar | Aprova se | Se reprovar |
| --- | --- | --- | --- | --- |
| T1. Reconciliação | A base limpa bate com o oficial | Saldo jan–mai/2026 por grupo contra a tabela da seção 3 | Diferença de até 0,5% em cada grupo | **Parar:** algum filtro está errado |
| T2. Composição | A diferença de % a pedido entre divisões é do setor ou só das ocupações que ele emprega | (a) Dentro da mesma CBO: compare o % a pedido entre divisões, só nas CBOs presentes em 3 ou mais divisões com `MIN_DESL` em cada uma. (b) Padronização: para cada uma das 14 maiores divisões da transformação, calcule o % a pedido esperado (taxas por CBO do estado × mistura de CBOs da divisão) e compare com o observado | A diferença entre a maior e a menor taxa padronizada, nas 14 maiores divisões, continua acima de `T2_CORTE_PP = 5` p.p. Mostre sempre a distribuição completa | A tese vira "retenção em ocupações de linha" (V14). Se sobrarem menos de 10 CBOs no item (a), reporte em vez de afrouxar o volume sozinho |
| T3. Dependência de uma CBO | O resultado não é só o alimentador de linha | Recalcule os KPIs 1 e 2 sem a CBO 784205 | O ranking das 5 piores divisões muda no máximo 1 posição | Mostrar o resultado com e sem ela no painel |
| T4. Estabilidade | As taxas não são ruído de amostra pequena | Divida os 12 meses em dois semestres (set–fev e mar–ago) e compare o % a pedido por recorte | Correlação entre os semestres acima de 0,7 nos recortes acima do volume mínimo | Subir os volumes mínimos para 500 ou usar a mesorregião |
| T5. Sensibilidade da definição | A tese não depende de C vs B–E | Rode KPI 1 e o ranking das microrregiões em C e em B–E | O KPI 1 do estado difere menos de 1 p.p. e o top 5 de microrregiões por % a pedido tem no máximo 1 troca | Declarar a dependência no pitch |
| T6. Macrofamílias | A classificação do LLM é confiável | M1 a M4 (seção 6.5) | Concordância humana de 85% ou mais | Ajustar o prompt e rodar de novo |

A forma de medir em T2 e T5 é uma operacionalização dos critérios do v1, feita nesta versão.

---

## 8. Painel (Streamlit)

O painel tem três páginas, na ordem em que o diretor pensa: Onde, Por quê e O quê. Ele lê só `data/processed/` e `data/reference/` e abre em menos de 5 segundos.

### 8.1. Páginas

| Página | Pergunta | Conteúdo obrigatório | Gráfico |
| --- | --- | --- | --- |
| 1. Onde | Quais regiões e setores pedem atenção? | 4 cartões de KPI de SC no topo, cada um com n; mapa das microrregiões colorido pelo KPI 1; quadrantes por microrregião × grupo setorial; ranking das microrregiões | Mapa coroplético (GeoJSON da R12) e dispersão (tamanho = movimentos, cor = mesorregião, linhas na mediana) |
| 2. Por quê | O gargalo é salário, escolaridade ou rotatividade? | Ao escolher um recorte: KPIs 1, 3 e 4 por macrofamília (área e nível), com n e cobertura; perfil dos admitidos versus desligados (faixa de escolaridade e salário mediano) | Barras horizontais ordenadas, com a linha da mediana de SC |
| 3. O quê | O que o cliente deve fazer? | 3 recomendações lidas de `app/recomendacoes.yaml` | Cartões de texto |

### 8.2. Regras visuais

- **Filtros globais na barra lateral:** segmento (padrão: Transformação), grupo setorial, mesorregião ou microrregião, área e nível da macrofamília.
- **Cores:** uma cor de destaque só para o que pede atenção; o resto em cinza. As cores precisam funcionar no tema claro e no escuro.
- **Títulos:** todo gráfico tem título com a conclusão ("Alimentos perde 56% dos que saem por pedido"), não com o tema ("Saídas por setor"). Os títulos são gerados a partir dos números, para não ficarem desatualizados.
- **Amostra pequena:** recorte abaixo do volume mínimo aparece em cinza com o rótulo "amostra insuficiente".
- **Rodapé fixo:** fonte (Novo CAGED, MTE, set/2025–ago/2026), a definição de indústria usada e um expansor com "Premissas e limites".

### 8.3. Recomendações

**Formato de cada recomendação (critério 4 da banca):**

> **[Ação]** para **[área × nível da macrofamília]** em **[microrregião ou mesorregião]**, porque **[KPI com número e comparação com SC]**. Quem executa: **[FIESC, SENAI-SC ou empresas]**.

**Ações permitidas:** formação profissional direcionada, revisão de faixa salarial, programa de retenção e atração de talentos regionais.

**Fluxo:**

1. O agente gera `reports/recomendacoes_candidatas.md` com as combinações área × nível × microrregião nos quadrantes "Expansão sob pressão" e "Retenção problemática" que tenham o maior KPI 1 acima da mediana de SC e volume suficiente, cada uma com os números e um rascunho de texto no formato acima.
2. O agente preenche `app/recomendacoes.yaml` com as 3 melhores candidatas, marcadas como `status: rascunho`.
3. A equipe escolhe, reescreve e muda para `status: aprovada`.
4. O painel mostra um aviso visível enquanto alguma recomendação estiver como rascunho.
5. As recomendações só são aprovadas depois que T1 a T4 tiverem rodado.

### 8.4. Desempenho, exportação e deploy

- **Desempenho:** o app lê só tabelas pequenas (o total de `data/processed/` deve ficar abaixo de 20 MB) e usa `st.cache_data`. Ele nunca lê `data/raw/` nem `data/interim/`. Os caminhos usam `pathlib`, relativos à raiz do repositório.
- **Figuras:** `src/figuras.py` exporta os gráficos principais (mapa, quadrantes, barras da página Por quê) em PNG em `reports/figures/`, para os slides. Use Plotly com kaleido; se a instalação do kaleido der problema, fixe a versão 0.2.1.
- **Local:** `streamlit run app/streamlit_app.py`. No pitch, use o painel local. O link do Cloud e os PNGs servem de reserva.
- **Streamlit Community Cloud:**
  - Repositório público no GitHub, arquivo principal `app/streamlit_app.py`, `requirements.txt` na raiz com versões fixadas.
  - Nas configurações avançadas do Cloud, use a mesma versão do Python do ambiente local (3.11 ou 3.12).
  - O app não precisa de segredo, porque não chama o LLM em tempo de execução.
  - Coloque o link no README e no formulário de entrega.

**Aceite do painel:** um colega que não participou do projeto encontra, em menos de 1 minuto, a região e o setor de maior pressão, e diz qual é a ação recomendada.

---

## 9. Repositório

O repositório é público e precisa rodar do zero em outra máquina. O CSV bruto (413 MB) nunca entra no Git, porque o GitHub bloqueia arquivos acima de 100 MB.

```
datathon-sc/
├── CLAUDE.md
├── README.md               # pergunta, tese, como rodar, link do painel, premissas e limites
├── config.py               # todos os parâmetros e mapas (colunas, seções, grupos, cortes, URLs, modelo)
├── requirements.txt        # versões fixadas
├── .env.example            # GEMINI_API_KEY=
├── .gitignore              # data/raw/, data/interim/, .env, .venv/, __pycache__/, .ipynb_checkpoints/
├── run_pipeline.py         # roda ingestão → limpeza → KPIs → testes → exportação (sem LLM por padrão)
├── docs/
│   └── SDD_v2.md
├── data/
│   ├── raw/                # 3 arquivos originais do evento (fora do Git)
│   ├── interim/            # parquets limpos e cache do LLM (fora do Git)
│   ├── reference/          # regiões IBGE, GeoJSON, títulos CBO e subclasse, macrofamilias.csv (no Git)
│   └── processed/          # agregados que o painel lê (no Git, pequenos)
├── notebooks/
│   └── 01_pipeline.ipynb   # chama src/ e explica cada etapa em markdown
├── src/
│   ├── ingest.py · clean.py · referencias.py · macrofamilias.py · kpis.py · testes.py · figuras.py
├── prompts/
│   └── macrofamilias_v1.md
├── diagnostics/            # diag_caged.py, diag2_caged.py, diag3_sensibilidade.py (V17)
├── reports/
│   ├── log_pipeline.md · testes.md · revisao_macrofamilias.csv · recomendacoes_candidatas.md
│   └── figures/
└── app/
    ├── streamlit_app.py
    └── recomendacoes.yaml
```

**Boas práticas obrigatórias:**

- O notebook roda de cima a baixo sem intervenção (`Restart & Run All`) antes de cada commit relevante.
- As funções ficam em `src/`; o notebook só chama e explica, e cada célula tem um título do que faz.
- Seeds fixas e versões fixadas em `requirements.txt`.
- Commits pequenos e descritivos, em português. No fim de cada fase, o agente propõe um commit e o usuário aprova.
- O README tem a seção "Premissas e limites" com todos os itens da seção 11.
- O README explica onde colocar os 3 arquivos originais em `data/raw/` (link do evento: https://bit.ly/3WooHMp).

---

## 10. Roadmap

São 4 fases. No fim de cada uma, o agente **para** e entrega o relatório de checkpoint no formato definido no `CLAUDE.md`.

### Fase 1 — Fundação de dados (10/11)

**Entregas:**

- Estrutura do repositório, `config.py`, `requirements.txt`, `.gitignore` e `.env.example`.
- `src/ingest.py`, `src/clean.py` e `src/referencias.py`.
- `data/reference/` completo, exceto `macrofamilias.csv`.
- `data/interim/caged_ind.parquet` e `reports/log_pipeline.md`.
- T1 em `reports/testes.md`.
- `diagnostics/` (V17).

**Aceite:** o da seção 4.7.

**Checkpoint 1 (mostrar ao usuário):**

- Tabela de linhas por regra.
- Resultado do T1.
- Contagem de municípios casados, microrregiões e mesorregiões.
- Quantas microrregiões passam de 1.000 movimentos em C.
- Qualquer número da seção 3 que não bateu.
- Pico de memória da leitura.

### Fase 2 — Macrofamílias com IA (10/11 e 11/11)

**Pré-requisito:** `GEMINI_API_KEY` no `.env`. O agente pede ao usuário que crie o arquivo e nunca pede para colar a chave no chat.

**Entregas:**

- `src/macrofamilias.py` e `prompts/macrofamilias_v1.md`.
- `data/reference/macrofamilias.csv`.
- M1, M2 e M4 aplicados automaticamente.
- `reports/revisao_macrofamilias.csv` (M3).
- Plano B pronto (6.6).

**Aceite:** 100% das CBOs de B–F com área e nível; zero valor fora da lista fechada.

**Checkpoint 2 (mostrar ao usuário):**

- Distribuição dos movimentos por área e por nível.
- 20 CBOs de exemplo classificadas.
- Lista de confiança baixa (M1) e de divergências (M2).
- Pedido para dois revisores preencherem a amostra M3.

A revisão humana pode acontecer em paralelo à Fase 3. O T6 fecha quando a planilha voltar preenchida.

### Fase 3 — KPIs, testes e painel mínimo (11/11)

**Entregas:**

- `src/kpis.py` e `src/testes.py`.
- Agregados em `data/processed/`: KPIs por microrregião × grupo setorial, por macrofamília e por microrregião, quadrantes e QL (opcional).
- T2 a T5 em `reports/testes.md`.
- PNGs em `reports/figures/`.
- **Painel mínimo:** a página "Onde" funcionando localmente. É o piso de entrega caso algo dê errado depois.

**Aceite:** todos os testes rodados e registrados; o painel mínimo abre em menos de 5 segundos.

**Checkpoint 3 (mostrar ao usuário):**

- Tabela de testes com os números.
- Resultado do T2 e qual tese sobrevive (V14).
- Top 5 de cada quadrante.
- Comando para abrir o painel mínimo.

### Fase 4 — Painel completo e entrega (12/11, até 18h)

**Entregas:**

- Páginas "Por quê" e "O quê".
- `reports/recomendacoes_candidatas.md` e `app/recomendacoes.yaml` em rascunho.
- README completo com "Premissas e limites" e o link do painel.
- Notebook passando no `Restart & Run All`.
- Deploy no Streamlit Community Cloud.
- PNGs finais.
- Auditoria do repositório: nenhum arquivo de `data/raw/` ou `data/interim/` versionado, nenhum `.env`, nenhum arquivo acima de 50 MB, e o tamanho de `data/processed/`.

**Aceite:** o aceite do painel (8.4); um clone limpo roda `run_pipeline.py` e o app seguindo só o README.

**Checkpoint 4 (mostrar ao usuário):**

- Link do Cloud.
- Checklist de entrega.
- Lista final de premissas.
- O que ficou de fora.

**13/11:** só ajuste do pitch e entrega pelo formulário (https://bit.ly/4jBn07X). Nada de código novo.

---

## 11. Premissas e limites (para o README)

1. O CAGED mede fluxo, não estoque nem vagas abertas. "Apagão" é inferido por sinais indiretos (saídas a pedido, saldo, prêmio salarial, escolaridade).
2. Assumimos que a base já veio sem os registros de exclusão (o arquivo não tem a coluna). Evidência: reconciliação com a FIESC dentro de 0,2%.
3. As duplicatas exatas foram mantidas (97.635 no arquivo; 22.211 na transformação). Sem ID do trabalhador, não é possível distingui-las de contratações em lote, e os números oficiais as incluem.
4. As 36.940 declarações fora do prazo foram mantidas; as 6.128 linhas de competência anterior a set/2025 foram excluídas.
5. 99,96% das admissões vêm como "tipo ignorado" (97), por isso não é possível separar primeiro emprego de reemprego.
6. Indústria = seções B–F, com análise principal na transformação (C) e a construção (F) separada.
7. A população usada é a do Censo 2022.
8. Salários: só celetistas comuns (sem aprendiz, parcial ou intermitente), na faixa de R$ 1.000 a R$ 30.000, sempre pela mediana.
9. O prêmio de contratação é hipótese da equipe, não referência consagrada: deve ser tratado como sinal fraco.
10. Escolaridade e salário são associados aos gargalos; os dados não permitem afirmar causalidade.
11. As macrofamílias foram classificadas por LLM (Gemini) com lista fechada e revisão humana; a concordância está registrada no T6.
12. O recorte territorial é a microrregião e a mesorregião do IBGE, porque o Guia usa o termo e a banca reconhece os nomes. O IBGE substituiu essa divisão em 2017 pelas regiões imediatas e intermediárias.
13. Em julho/2026, o saldo de SC no arquivo (−528) difere de uma notícia (−248); usamos o arquivo.
14. Recortes abaixo do volume mínimo não entram em ranking.
15. Os limiares (5 p.p., volumes mínimos, QL de 1,25) são escolhas da equipe; a sensibilidade está em `reports/testes.md`.

---

## 12. Erros a evitar

A maioria destes erros é silenciosa: o código roda e o número sai errado.

| # | Erro | Consequência | Como evitamos |
| --- | --- | --- | --- |
| E1 | Ler códigos como inteiro | CNAE da agricultura vira divisão têxtil; CBOs de 5 dígitos somem | R1 e R3 |
| E2 | Juntar município de 6 dígitos com código IBGE de 7 | Join vazio sem erro | R11 |
| E3 | Ler o CSV de municípios sem tratar o rodapé HTML | Linha fantasma e colunas como texto | R11 |
| E4 | Tratar o CAGED como estoque ou desemprego | Conclusões impossíveis com o dado | Dizer "fluxo" e "proxy de aperto" |
| E5 | Chamar todo saldo positivo de "apagão" | Diagnóstico sem base | KPI 1 e quadrantes |
| E6 | Usar média salarial | Máximo de R$ 3,47 milhões distorce tudo | D6 e R9 |
| E7 | Usar `valorsalariofixo` | Salário por hora misturado com mensal | D5 |
| E8 | Escolaridade como número, ou a tabela de códigos errada | Código 80 "maior" que doutorado; médio incompleto tratado como completo | R10 |
| E9 | Ranking em números absolutos | Joinville e Blumenau sempre no topo só pelo tamanho | KPI 2 per capita |
| E10 | Ranking com município pequeno | Extremos são cidades com um empregador (Guatambú: +668 por 10 mil) | Volume mínimo e recorte regional |
| E11 | Olhar um mês isolado | Dezembro é sempre negativo | Acumulado de 12 meses |
| E12 | Somar construção e transformação | Dilui o sinal (38% contra 51% a pedido) | D3 |
| E13 | Esquecer a CBO que domina | Conclusão que vale só para o alimentador de linha | T3 |
| E14 | Confundir setor com ocupação | Atribuir ao setor o que é da função | T2 e 5.2 |
| E15 | IA decorativa (KMeans no código da CBO, chatbot) | A banca não vê valor | LLM com lista fechada e validação |
| E16 | LLM inventando categorias ou códigos | Macrofamílias incoerentes | Enum no esquema, conferência do conjunto, T6 |
| E17 | Dizer que escolaridade "causa" o gargalo | Afirmação sem sustentação | "Associado", nunca "causa" |
| E18 | Remover duplicatas | O saldo de C passa de +1.008 para cerca de −12.300 | R7 e V10 |
| E19 | Subir o CSV de 413 MB ou a chave de API no GitHub | Push bloqueado ou chave vazada | `.gitignore` e `.env` |
| E20 | Painel com 20 gráficos e nenhuma resposta | A banca não acha a decisão | 3 páginas, títulos com conclusão |
| E21 | Usar a taxa de primeiro emprego | 99,96% das admissões vêm como tipo 97 | Seção 3 e premissa 5 |
| E22 | Deixar painel e ensaio para a última noite | Estoura os 3 minutos ou não entrega | Escopo congelado em 12/11 às 18h |
