# Raio-X do Mercado de Trabalho Industrial de SC — Datathon CDIA 2026

**Pergunta:** quais regiões e setores industriais de Santa Catarina enfrentam apagão de mão de obra ou expansão acelerada, e como renda e escolaridade explicam esses gargalos?

**Resposta que os dados sustentam até aqui:** a transformação catarinense quase não cresce em saldo (+1.008 vagas em 12 meses, em 835.866 movimentações), mas **51% dos desligamentos são a pedido do trabalhador**. Alimentos e bebidas (56%), madeira e móveis (53%) e têxtil (52%) lideram. O setor pesa, mas a maior parte da diferença entre setores vem das ocupações de linha: descontada a mistura de ocupações, a diferença cai de 13,3 para 5,6 pontos percentuais (teste T2). O gargalo é de **retenção**, não de falta de gente.

**Painel:** `streamlit run app/streamlit_app.py` · Streamlit Community Cloud: _(colocar o link aqui depois do deploy)_

O contrato do projeto é [`docs/SDD_v2.md`](docs/SDD_v2.md). O pipeline está documentado em [`notebooks/01_pipeline.ipynb`](notebooks/01_pipeline.ipynb).

## Como rodar

1. Python 3.11 ou 3.12. Crie um ambiente e instale as dependências:
   ```bash
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Baixe os 3 arquivos do evento (https://bit.ly/3WooHMp) e coloque em `data/raw/`:
   `Novo_Caged_MOV_Limpo.csv`, `Municipios_SC_limpo.csv`, `Dicionario_de_dados.xlsx`.
3. Baixe as regiões do IBGE (uma vez; precisa de internet):
   ```bash
   python src/referencias.py
   ```
4. (Opcional) Classifique as macrofamílias de CBO no Gemini. O resultado já versionado em `data/reference/macrofamilias.csv` dispensa este passo:
   ```bash
   cp .env.example .env        # e cole a GEMINI_API_KEY dentro do .env
   python src/macrofamilias.py --llm
   ```
   Sem chave: siga `prompts/plano_b_chat.md` (classificação no Google AI Studio).
5. Rode o pipeline completo (cerca de 1 minuto e 2 GB de memória):
   ```bash
   python run_pipeline.py
   ```
6. Abra o painel:
   ```bash
   streamlit run app/streamlit_app.py
   ```

Se a exportação de PNG reclamar do Chrome, rode `plotly_get_chrome`; se ainda falhar, `pip install kaleido==0.2.1`.

## O que cada etapa produz

| Etapa | Código | Saída |
| --- | --- | --- |
| Ingestão | `src/ingest.py` | `data/interim/caged_raw.parquet` |
| Referências | `src/referencias.py` | `data/reference/` (regiões, GeoJSON, títulos CBO e CNAE) |
| Limpeza e junções | `src/clean.py` | `data/interim/caged_ind.parquet`, `reports/log_pipeline.md` |
| Macrofamílias (Gemini) | `src/macrofamilias.py` | `data/reference/macrofamilias.csv`, `reports/macrofamilias_validacao.md` |
| KPIs | `src/kpis.py` | `data/processed/*.csv` |
| Testes T1–T5 | `src/testes.py` | `reports/testes.md`, `reports/testes_detalhe/` |
| Figuras | `src/figuras.py` | `reports/figures/*.png` |
| Recomendações | `src/recomendacoes.py` | `reports/recomendacoes_candidatas.md`, `app/recomendacoes.yaml` |
| Auditoria | `src/auditoria.py` | verificação antes do push |

## Os quatro KPIs

| KPI | Pergunta | Fórmula |
| --- | --- | --- |
| 1. % de saídas a pedido | O trabalhador está saindo por conta própria? | desligamentos a pedido ÷ desligamentos (adaptação da taxa de *quits* do JOLTS/BLS) |
| 2. Saldo por 10 mil hab. | Onde há expansão ou encolhimento? | saldo de 12 meses ÷ população do Censo 2022 × 10.000 |
| 3. Prêmio de contratação | A empresa paga mais para repor? | mediana do salário de admissão ÷ de desligamento, na mesma CBO e microrregião |
| 4. Descasamento de escolaridade | Quem entra tem menos formação que quem sai? | % com superior nos admitidos − nos desligados, na mesma CBO e microrregião |

## Resultados dos testes

Ver [`reports/testes.md`](reports/testes.md). Resumo: T1 (reconciliação com a FIESC) aprovado na transformação, indústria geral e total; T2 (efeito de setor) aprovado por pouco; T3 (dependência do alimentador de linha) reprovado, e por isso o painel mostra os resultados com e sem essa ocupação; T5 aprovado no nível do estado.

## Premissas e limites

1. O CAGED mede fluxo, não estoque nem vagas abertas. "Apagão" é inferido por sinais indiretos (saídas a pedido, saldo, prêmio salarial, escolaridade).
2. Assumimos que a base já veio sem os registros de exclusão (o arquivo não tem a coluna). Evidência: reconciliação com o boletim da FIESC dentro de 0,2% na indústria total.
3. As linhas idênticas foram mantidas (97.635 cópias excedentes no arquivo; 22.211 na transformação). Sem ID do trabalhador, não é possível distingui-las de contratações em lote, e os números oficiais as incluem. Removê-las levaria o saldo da transformação de +1.008 para −12.287.
4. As 36.940 declarações fora do prazo foram mantidas; as 6.128 linhas com competência anterior a set/2025 foram excluídas.
5. 99,96% das admissões vêm como "tipo ignorado" (97); não é possível separar primeiro emprego de reemprego.
6. Indústria = seções CNAE B–F, com análise principal na transformação (C) e a construção (F) separada, seguindo o boletim de emprego industrial da FIESC.
7. População: Censo 2022.
8. Salários: só celetistas comuns (sem aprendiz, parcial ou intermitente), entre R$ 1.000 e R$ 30.000, sempre pela mediana.
9. O prêmio de contratação é hipótese da equipe, não referência consagrada: tratar como sinal fraco.
10. Escolaridade e salário são associados aos gargalos; os dados não permitem afirmar causalidade.
11. As macrofamílias foram classificadas por LLM (Gemini) com lista fechada e revisão humana; a concordância está registrada no T6.
12. O recorte territorial é a microrregião e a mesorregião do IBGE, porque o Guia usa o termo e a banca reconhece os nomes. O IBGE substituiu essa divisão em 2017 pelas regiões imediatas e intermediárias.
13. Em julho/2026, o saldo de SC no arquivo (−528) difere de uma notícia (−248); usamos o arquivo.
14. Recortes abaixo do volume mínimo não entram em ranking.
15. Os limiares (5 p.p., volumes mínimos, QL de 1,25) são escolhas da equipe; a sensibilidade está em `reports/testes.md`.
16. Na construção, o saldo jan–mai/2026 do arquivo (10.775) fica 54 vagas (0,504%) acima do boletim da FIESC (10.721), pouco acima da tolerância de 0,5% do teste T1. Decisão da equipe: manter a tolerância e declarar a diferença.
17. 9 CBOs do arquivo (131 linhas industriais) não constam no dicionário do evento; seguem a regra de herança pela família da CBO.
18. 751 CBOs pequenas (2,44% dos movimentos) ficam como "Outros" nas macrofamílias, porque não há CBO classificada da mesma família; não entram nas recomendações.
19. Uma única ocupação, o alimentador de linha de produção (CBO 784205), responde por cerca de um quarto dos movimentos da transformação. Sem ela, o saldo da transformação seria negativo e a madeira cairia de 54,2% para 48,5% de saídas a pedido.

## Deploy no Streamlit Community Cloud

1. Suba o repositório público no GitHub (depois de `python src/auditoria.py` dar OK).
2. Em share.streamlit.io: **New app** → escolha o repositório → arquivo principal `app/streamlit_app.py`.
3. Em **Advanced settings**, use a mesma versão do Python do seu ambiente (3.11 ou 3.12).
4. O app não precisa de segredos: ele não chama o Gemini, só lê `data/processed/` e `data/reference/`.
5. Cole o link no topo deste README e no formulário de entrega (https://bit.ly/4jBn07X).

No pitch, use o painel local; o link do Cloud e os PNGs de `reports/figures/` são a reserva.
