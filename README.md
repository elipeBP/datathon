# Raio-X do Mercado de Trabalho Industrial de SC

**Datathon CDIA 2026 · UniSENAI** — consultoria de dados para a indústria catarinense, a partir dos microdados do Novo CAGED (set/2025 a ago/2026).

**Site:** https://datathon-ebon.vercel.app · **Pipeline documentado:** [`notebooks/01_pipeline.ipynb`](notebooks/01_pipeline.ipynb) · **Modelo estatístico:** [`reports/modelo_saida_pedido.md`](reports/modelo_saida_pedido.md)

## Em 30 segundos

**Pergunta do desafio:** quais regiões e setores industriais de Santa Catarina estão enfrentando apagão de mão de obra ou expansão acelerada, e como os indicadores de renda e escolaridade explicam esses gargalos?

**Resposta:** o apagão da indústria catarinense aparece como **rotatividade**, não como falta de gente.

| Número | O que mostra |
| --- | --- |
| **50,9%** | dos 417.429 desligamentos da indústria de transformação foram a pedido do trabalhador |
| **+1.008** | saldo de empregos em 12 meses, em 835.866 movimentações: o setor gira muito e quase não cresce |
| **−0,02 p.p.** | diferença de escolaridade entre quem entra e quem sai, na mesma ocupação e região: não falta formação |
| **−2,2 p.p.** | nas saídas a pedido onde a mesma ocupação paga 10% acima da mediana dela em SC (modelo em 620 mercados, p < 0,001) |

**Onde:** o Oeste (agroindústria) cresce e perde gente; o Vale do Itajaí (têxtil) encolhe e perde gente.

**O que fazer** (aprovado pela equipe, em [`app/recomendacoes.yaml`](app/recomendacoes.yaml)):
1. **Programa de retenção na agroindústria do Oeste** — 64,6% das saídas a pedido nos ofícios da agroindústria (SC: 50,9%), num setor que ainda cresce.
2. **Revisão de faixa salarial e retenção no têxtil de Rio do Sul** — 68,6% a pedido; a reposição paga 4,3% menos.
3. **Requalificação do têxtil para eletroeletrônica em Blumenau (SENAI-SC)** — o têxtil perdeu 1.283 vagas e a eletroeletrônica criou 568.

Cada recomendação liga uma macrofamília de ocupação classificada pela IA a uma região e tem uma linha de base para acompanhar todo mês no CAGED.

## Entregáveis do Guia do Participante

| Entregável | Onde está |
| --- | --- |
| **Notebook / script** com o pipeline completo, da carga e exclusão de registros até a IA e a exportação | [`notebooks/01_pipeline.ipynb`](notebooks/01_pipeline.ipynb) (executado, com as saídas) · [`run_pipeline.py`](run_pipeline.py) · módulos em [`src/`](src/) |
| **Dashboard analítico em Python** com 3 ou mais indicadores | [`app/`](app/) (Streamlit: `streamlit run app/streamlit_app.py`) · versão pública no site, que lê os dados gerados pelo pipeline Python |
| **Pitch executivo** | site em capítulos ([datathon-ebon.vercel.app](https://datathon-ebon.vercel.app)) e figuras em [`reports/figures/`](reports/figures/) |

## Como a IA generativa foi usada

1. **Classificação das ocupações (macrofamílias).** O Google Gemini classificou as 354 ocupações (CBOs) que cobrem 95% das movimentações em **15 áreas × 4 níveis de formação**, no formato do Mapa do Trabalho Industrial (SENAI/CNI). Lista fechada imposta por esquema JSON, temperatura 0, conferência do lote, validação automática (M1, M2, M4) e amostra para revisão humana (M3). Prompt e registro em [`prompts/macrofamilias_v1.md`](prompts/macrofamilias_v1.md); validação em [`reports/macrofamilias_validacao.md`](reports/macrofamilias_validacao.md).
2. **Assistente "Perguntar aos dados" no site.** Responde dúvidas durante e depois da apresentação, só com os números do estudo. Arquitetura em camadas em [`web/api/perguntar.js`](web/api/perguntar.js): triagem sem IA (saudações, manipulação, perguntas prontas e suas variações), busca dos recortes citados (20 microrregiões, 295 municípios, setores, ocupações), resposta estruturada com fonte e **verificação de que todo número da resposta existe nos dados**.

## Modelo estatístico das saídas a pedido

[`src/modelo.py`](src/modelo.py) mede o que está **associado** a o trabalhador pedir para sair, em dois níveis interpretáveis (relatório em [`reports/modelo_saida_pedido.md`](reports/modelo_saida_pedido.md)):

- **Mercado — pagar acima do mercado retém?** Logit fracionário em 620 células ocupação × microrregião (75% dos desligamentos), com efeitos fixos de setor, mesorregião e grande grupo da ocupação:

  logit(p_c) = β₀ + β₁·ln(s_c) + β₂·ln(π_c) + β₃·g_c + Σ β_k·z_kc + efeitos fixos

  β₁ = −0,963 (IC 95%: −1,468 a −0,459; z = −3,74). Onde a mesma ocupação paga 10% acima da mediana de SC, a parcela de saídas a pedido é **2,2 p.p. menor** (efeito marginal médio), entre −1,8 e −3,1 p.p. em todos os testes de robustez. O prêmio de contratação não se sustenta com os controles (p = 0,725).
- **Perfil — entre quem saiu, quem saiu a pedido?** Regressão logística em 388.489 desligamentos, validada fora da amostra contra um gradient boosting (AUC 0,616 × 0,646). Superior completo +7,2 p.p.; mulheres +4,3; empresas de 500+ empregados +3,7; 18 a 24 anos +2,9; 50 anos ou mais −3,5.

Associação, não causa. O CAGED não traz tempo de casa; o nível individual só olha quem saiu, por isso o efeito do salário é lido no nível de mercado.

## Os quatro indicadores

| KPI | Pergunta | Fórmula |
| --- | --- | --- |
| 1. % de saídas a pedido | O trabalhador sai por conta própria? | desligamentos a pedido ÷ desligamentos (adaptação da taxa de *quits* do JOLTS/BLS) |
| 2. Saldo por 10 mil hab. | Onde há expansão ou encolhimento? | saldo de 12 meses ÷ população do Censo 2022 × 10.000 |
| 3. Prêmio de contratação | A empresa paga mais para repor? | mediana do salário de admissão ÷ de desligamento, na mesma CBO e microrregião, ponderado |
| 4. Descasamento de escolaridade | Quem entra estudou menos? | % com superior nos admitidos − nos desligados, na mesma CBO e microrregião, ponderado |

## Testes de validação

Resultados em [`reports/testes.md`](reports/testes.md) e detalhes em [`reports/testes_detalhe/`](reports/testes_detalhe/).

| Teste | O que verifica | Resultado |
| --- | --- | --- |
| T1 | Saldo bate com o boletim da FIESC (jan–mai/2026) | Aprovado: 0,01% na transformação; construção 0,504% (limite 0,5%), declarado |
| T2 | O setor pesa mesmo descontada a mistura de ocupações | Aprovado por pouco (5,6 p.p. contra corte de 5) |
| T3 | O resultado não depende de uma única ocupação | **Reprovado**: o site mostra o resultado com e sem o alimentador de linha |
| T4 | Estabilidade entre semestres | Aprovado (r = 0,80) |
| T5 | Não depende da definição de indústria | Aprovado (0,28 p.p.; mesmo top 5 de microrregiões) |
| T6 | Concordância da IA com revisores humanos | Pendente: planilha [`reports/revisao_macrofamilias.csv`](reports/revisao_macrofamilias.csv) |

## Estrutura do repositório

```
├── notebooks/01_pipeline.ipynb   pipeline completo, executado e comentado
├── run_pipeline.py               o mesmo pipeline por linha de comando
├── config.py                     todos os parâmetros (janela, seções, cortes, modelos de IA)
├── src/                          ingestão, limpeza, KPIs, testes, IA (macrofamílias), modelo, exportação
├── app/                          painel Python (Streamlit) e recomendações aprovadas (recomendacoes.yaml)
├── web/                          site React (Vercel) e o assistente de IA (web/api/perguntar.js)
├── data/
│   ├── raw/                      os 3 arquivos do evento (fora do Git)
│   ├── interim/                  bases limpas em Parquet e cache da IA (fora do Git)
│   ├── reference/                regiões do IBGE, mapa, dicionário e macrofamilias.csv
│   └── processed/                agregados (KPIs, quadrantes, modelo) que os painéis leem
├── reports/                      testes, modelo, validação da IA, log do pipeline e figuras
├── prompts/                      prompt da classificação por IA e o plano B (chat)
├── diagnostics/                  scripts de diagnóstico somente leitura
└── docs/                         SDD (contrato do projeto), relatórios de cada fase e briefing de design
```

## Como rodar

1. Python 3.11 a 3.13. Crie um ambiente e instale as dependências:
   ```bash
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Baixe os 3 arquivos do evento (https://bit.ly/3WooHMp) para `data/raw/`: `Novo_Caged_MOV_Limpo.csv`, `Municipios_SC_limpo.csv` e `Dicionario_de_dados.xlsx`.
3. Rode o pipeline (cerca de 5 minutos e 2 GB de memória; baixa as regiões do IBGE na primeira vez):
   ```bash
   python run_pipeline.py
   ```
   ou abra `notebooks/01_pipeline.ipynb` e use *Restart & Run All*.
4. Painel Python:
   ```bash
   streamlit run app/streamlit_app.py
   ```
5. Site (Node 20+):
   ```bash
   cd web && npm install && npm run dev      # http://localhost:5173
   ```

**IA (opcional).** A classificação já está versionada em `data/reference/macrofamilias.csv`. Para refazê-la: `cp .env.example .env`, cole a `GEMINI_API_KEY` no `.env` e rode `python src/macrofamilias.py --llm`. Sem chave, siga [`prompts/plano_b_chat.md`](prompts/plano_b_chat.md). O assistente do site usa a mesma chave como variável de ambiente da Vercel; sem ela, as perguntas prontas continuam funcionando.

**Deploy do site.** Na Vercel: importe o repositório, **Root Directory = `web`**, e cadastre `GEMINI_API_KEY` em *Environment Variables*. Cada push na `main` publica de novo. Antes de publicar, `python src/auditoria.py` confere que nenhum dado bruto, `.env` ou chave vai para o Git.

## Premissas e limites

1. O CAGED mede fluxo, não estoque nem vagas abertas. "Apagão" é inferido por sinais indiretos (saídas a pedido, saldo, salário de reposição, escolaridade).
2. Assumimos que a base já veio sem os registros de exclusão (o arquivo não tem a coluna). Evidência: reconciliação com o boletim da FIESC dentro de 0,2% na indústria total.
3. As linhas idênticas foram mantidas (97.635 cópias excedentes no arquivo; 22.211 na transformação). Sem ID do trabalhador, não é possível distingui-las de contratações em lote, e os números oficiais as incluem. Removê-las levaria o saldo da transformação de +1.008 para −12.287.
4. As 36.940 declarações fora do prazo foram mantidas; as 6.128 linhas com competência anterior a set/2025 foram excluídas.
5. 99,96% das admissões vêm como "tipo ignorado" (97); não é possível separar primeiro emprego de reemprego.
6. Indústria = seções CNAE B–F, com análise principal na transformação (C) e a construção (F) separada, seguindo o boletim de emprego industrial da FIESC.
7. População: Censo 2022.
8. Salários: só celetistas comuns (sem aprendiz, parcial ou intermitente), entre R$ 1.000 e R$ 30.000, sempre pela mediana.
9. O prêmio de contratação era hipótese da equipe; o modelo mostrou que ele não se sustenta com controles. O que se associa às saídas é o nível do salário da ocupação na região.
10. Escolaridade e salário são associados aos gargalos; os dados não permitem afirmar causalidade.
11. As macrofamílias foram classificadas por LLM (Gemini) com lista fechada e revisão humana; a concordância fica registrada no T6.
12. O recorte territorial é a microrregião e a mesorregião do IBGE, porque o Guia usa o termo e a banca reconhece os nomes. O IBGE substituiu essa divisão em 2017 pelas regiões imediatas e intermediárias.
13. Em julho/2026, o saldo de SC no arquivo (−528) difere de uma notícia (−248); usamos o arquivo.
14. Recortes abaixo do volume mínimo não entram em ranking.
15. Os limiares (5 p.p., volumes mínimos, QL de 1,25) são escolhas da equipe; a sensibilidade está em `reports/testes.md` e no relatório do modelo.
16. Na construção, o saldo jan–mai/2026 do arquivo (10.775) fica 54 vagas (0,504%) acima do boletim da FIESC (10.721), pouco acima da tolerância de 0,5% do teste T1. Decisão da equipe: manter a tolerância e declarar a diferença.
17. 9 CBOs do arquivo (131 linhas industriais) não constam no dicionário do evento; seguem a regra de herança pela família da CBO.
18. 751 CBOs pequenas (2,44% dos movimentos) ficam como "Outros" nas macrofamílias, porque não há CBO classificada da mesma família; não entram nas recomendações.
19. Uma única ocupação, o alimentador de linha de produção (CBO 784205), responde por cerca de um quarto dos movimentos da transformação. Sem ela, o saldo da transformação seria negativo e a madeira cairia de 54,2% para 48,5% de saídas a pedido.
20. O modelo estatístico mede associação: o CAGED não traz tempo de casa, e o nível individual só olha quem saiu (viés de seleção tratado lendo o salário no nível de mercado).

## Fontes e créditos

- Microdados do Novo CAGED (Ministério do Trabalho e Emprego), Santa Catarina, set/2025 a ago/2026, fornecidos pela organização do evento.
- População (Censo 2022), microrregiões, mesorregiões e malha territorial: IBGE.
- Classificação das ocupações e assistente: Google Gemini.
- Contrato do projeto e decisões: [`docs/SDD_v2.md`](docs/SDD_v2.md); relatórios de cada fase em [`docs/processo/`](docs/processo/).

**Equipe:** _(nomes dos integrantes)_
