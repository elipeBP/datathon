## Checkpoint 4 — Painel completo e entrega

**Status:** aprovado com ressalvas. Todo o código está pronto e testado. O fechamento depende de passos que só podem rodar na sua máquina: regiões do IBGE (internet), classificação no Gemini (sua chave), revisão humana (M3), aprovação das recomendações, git e deploy.

**Entregas**
- `app/paginas/por_que.py`: KPIs 1, 3 e 4 por macrofamília (área × nível), com n e cobertura; perfil de admitidos × desligados (escolaridade e salário mediano).
- `app/paginas/o_que.py`: cartões das 3 recomendações, aviso de rascunho, linha de base e indicador de acompanhamento.
- Filtros globais na barra lateral: segmento, grupo setorial, mesorregião, microrregião e o botão do T3.
- `src/recomendacoes.py` → `reports/recomendacoes_candidatas.md` e `app/recomendacoes.yaml` (status: rascunho).
- `src/testes.py`: T6 (concordância LLM × revisores).
- `src/auditoria.py`: auditoria do repositório.
- `notebooks/01_pipeline.ipynb`: executado de cima a baixo, 11 células de código, 0 erros.
- `README.md` completo: resposta, como rodar, KPIs, testes, 19 premissas e limites, deploy.
- Novas tabelas em `data/processed/`: perfil de escolaridade e salário, setor × macrofamília e microrregião × setor × macrofamília (44 KB hoje).

**Aceite**

| Critério | Resultado |
| --- | --- |
| Painel com 3 páginas, abrindo em menos de 5 s | Sim: 1,2 s na primeira página, sem exceções nas 3 (dados reais e simulados) |
| Notebook passa no Restart & Run All | Sim, 0 erros |
| Clone limpo roda `run_pipeline.py` seguindo só o README | Sim, aqui com `--sem-regioes`; em casa, com internet, segue o README inteiro |
| Auditoria | OK: 60 arquivos versionáveis, `.env` e dados brutos fora do Git, nenhuma chave escrita; ela detecta uma chave colada de propósito |
| Deploy no Streamlit Cloud | Pendente: precisa do seu GitHub (passo a passo no README) |
| Colega acha região, setor e ação em menos de 1 minuto | Pendente: depende das recomendações reais |

**Bugs encontrados e corrigidos nesta fase:** troca de vírgula e ponto nas frases das recomendações; "p,p," no cartão do KPI 4; linhas duplicadas no registro de testes quando o notebook roda depois do pipeline; célula do notebook que não baixaria as regiões na primeira execução.

**Pontos novos:** V24, informativo. Cada recomendação traz o indicador de acompanhamento com a linha de base de hoje. É a ponte para o pitch: decisão → indicador → resultado medido no CAGED.

**O que ficou de fora:** mapa e recomendações testados só com dados simulados; o QL não aparece no painel (prioridade baixa no SDD), só em `data/processed/`.

## Checklist de entrega (em casa, nesta ordem)

- [ ] Descompactar o `datathon-sc_fase4.zip`, criar o ambiente e rodar `pip install -r requirements.txt`.
- [ ] Copiar os 3 arquivos do evento para `data/raw/`.
- [ ] `python src/referencias.py` → conferir no log 295 municípios, 20 microrregiões, 6 mesorregiões e zero nulo. Se parar, não atribuir no chute: me avisar.
- [ ] `cp .env.example .env`, colar a chave e rodar `python src/macrofamilias.py --llm` → ler `reports/macrofamilias_validacao.md`.
- [ ] `python run_pipeline.py` → conferir `reports/testes.md` (T4 e T5 deixam de ser pendentes).
- [ ] `streamlit run app/streamlit_app.py` → conferir se o mapa aparece. Se vier vazio, ver "Não testado" no `checkpoint_3.md`.
- [ ] Dois colegas preenchem `reports/revisao_macrofamilias.csv` → `python src/testes.py` calcula o T6.
- [ ] Equipe revisa `app/recomendacoes.yaml`, reescreve e troca `status: rascunho` por `status: aprovada`.
- [ ] `git init`, `git add -A`, `python src/auditoria.py` (precisa dar OK), commit, push no GitHub público.
- [ ] Deploy no Streamlit Community Cloud e o link no README e no formulário (https://bit.ly/4jBn07X).
- [ ] 12/11 às 18h: escopo congelado.

**Lista final de premissas:** seção "Premissas e limites" do README (19 itens).

**Próximo passo combinado:** preparar o pitch de 3 minutos para os diretores do SENAI, com foco na decisão e no resultado. O melhor momento é depois que as regiões e as macrofamílias reais existirem, porque as três recomendações e seus números saem delas.
