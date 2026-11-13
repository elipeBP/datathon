## Checkpoint 3 — KPIs, testes e painel mínimo

**Status:** aprovado com ressalvas. Os KPIs 1 e 2, os testes T2, T3 e T5 (parte estadual) e a página "Onde" rodam com os dados reais. Os KPIs 3 e 4, os quadrantes, o QL, o mapa, o T4 e o T5 por microrregião dependem das regiões do IBGE (V21). Os recortes por macrofamília dependem da Fase 2. O código desses recortes foi validado com regiões e macrofamílias simuladas, fora do repositório.

**Entregas**
- `src/kpis.py`: KPIs 1–4 (5.1), células CBO × microrregião com média ponderada e cobertura (5.2), quadrantes (5.4) e QL com sensibilidade 1,1/1,25/1,5 (5.5).
- `src/testes.py`: T2a, T2b, T3, T4 e T5, com tabelas completas em `reports/testes_detalhe/`.
- `src/graficos.py` (gráficos compartilhados) e `src/figuras.py` (PNGs em `reports/figures/`).
- `app/streamlit_app.py` e `app/paginas/onde.py`: página Onde com 4 cartões, mapa, quadrantes, ranking, barras por grupo setorial e o botão do T3.
- `data/processed/`: 5 tabelas hoje (0,01 MB); 10 quando houver regiões e macrofamílias.
- `run_pipeline.py` roda todas as etapas.

**Testes**

| Teste | Resultado | Leitura |
| --- | --- | --- |
| T2a | 15 CBOs presentes em ≥3 divisões; amplitude mediana de 11,1 p.p. | A mesma ocupação varia muito de setor para setor |
| T2b | **Aprovado por pouco:** amplitude padronizada de 5,6 p.p. (corte 5); observada 13,3 p.p. | A mistura de ocupações explica cerca de 58% da diferença entre divisões |
| T3 (KPI 1) | **Reprovado:** sem a CBO 784205, a madeira (16) vai de 3º para 7º (54,2% → 48,5%) | O painel tem o botão "Excluir alimentador de linha" e o PNG 02 mostra os dois cenários |
| T3 (KPI 2) | **Reprovado:** minerais não metálicos (23) vai de 4º para 7º | Idem |
| T4 | r = 0,86 em 153 recortes município × grupo (provisório) | Promissor; o resultado oficial sai por microrregião |
| T5 | KPI 1 do estado: 50,91% (C) × 50,63% (B–E), diferença de 0,28 p.p.: aprovado | O top 5 de microrregiões está pendente (V21) |

**Taxas padronizadas pela mistura de ocupações (T2b, as 3 maiores):** veículos (29) 53,5% · madeira (16) 53,3% · alimentos (10) 52,9%. Na taxa observada, alimentos lidera (56,5%).

**Qual tese sobrevive (V14):** pela regra do SDD, a tese de setor ("retenção, não escassez") sobrevive, porque o T2b passou. Mas a margem é pequena (5,6 contra 5) e o T3 reprovou. Registrei isso como V23 e a frase do pitch fica com a equipe.

**Top 5 de cada quadrante:** pendente; depende das microrregiões (V21).

**Painel mínimo**
- Comando: `streamlit run app/streamlit_app.py`.
- A página roda em 0,65 s, sem exceções, inclusive com o botão do T3 e a troca de segmento (teste automático `AppTest`).
- Sem regiões, a página mostra um aviso no lugar do mapa e dos quadrantes, e os cartões dos KPIs 3 e 4 mostram "—".

**Bugs encontrados e corrigidos nesta fase:** chave duplicada nas células quando o recorte já é a microrregião (achado pelo teste de encanamento); estouro de inteiro sem sinal no cálculo de mudança de posição do T3; ponto decimal nos rótulos dos gráficos.

**Não testado:** o mapa, porque precisa do GeoJSON real. O código assume que cada polígono traz o código da microrregião em `properties.codarea`, que é o padrão da API de malhas do IBGE. Se o mapa vier vazio, é o primeiro lugar a olhar.

**Decisões que preciso do usuário**
1. V23: no pitch, a frase central fica "o problema é de retenção no setor" ou "retenção, concentrada nas ocupações de linha"? Minha sugestão: as duas na mesma frase, com os números do T2b.

**Próxima fase (ao receber "pode seguir"):** Fase 4 — páginas "Por quê" e "O quê", recomendações candidatas, README completo, notebook, auditoria do repositório e instruções de deploy. As recomendações só ganham números quando as regiões e as macrofamílias reais existirem.
