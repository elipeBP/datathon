## Checkpoint 2 — Macrofamílias com IA

**Status:** aprovado com ressalvas. O código está pronto e testado com respostas simuladas. A classificação real depende da sua `GEMINI_API_KEY`.

**Entregas**
- `src/macrofamilias.py`: taxonomia fechada em enums, prompt, chamada ao Gemini, cache, plano B, M1, M2 e M4 automáticos, amostra M3, relatório.
- `prompts/macrofamilias_v1.md` (registro do prompt; o modelo e a data são atualizados na execução real).
- `prompts/plano_b_chat.md` (instrução e os 8 lotes prontos para colar no Google AI Studio).
- `data/interim/cbos_para_classificar.csv` (354 CBOs do escopo).
- `config.py`: `GEMINI_MODEL = "gemini-3.8-flash"`, reserva `gemini-3.5-flash-lite`.
- `requirements.txt` com `google-genai` e `pydantic`; `run_pipeline.py` chama a etapa (sem API por padrão).

**Como foi implementado (seção 6.3)**
- SDK `google-genai`, saída JSON com `response_schema` = lista de um modelo Pydantic. `area`, `nivel` e `confianca` são enums com os valores exatos da seção 6.2.
- Temperatura 0, lotes de 50 (8 chamadas para 354 CBOs).
- Conferência do conjunto: se faltar ou sobrar CBO, o lote é refeito até 3 vezes; depois disso, vai para classificação manual.
- Erros 429 e 503 são repetidos com espera exponencial. Se o limite diário do plano gratuito estourar, o programa para e indica a troca para o modelo reserva.
- Cache por lote em `data/interim/llm_cache/`; reexecutar não gera novas chamadas.
- A chave só é lida do `.env`; nunca é impressa nem gravada.
- Exemplos do prompt: 784205 Alimentador de linha (fixado no SDD); 351605 Técnico em segurança no trabalho (grupo 3, 3.406 movimentos); 252405 Analista de RH (grupo 2, 2.390 movimentos).

**Testes feitos aqui, com respostas simuladas (nenhum dado simulado ficou no repositório)**

| Teste | Resultado |
| --- | --- |
| Lote com CBO faltando | Rejeitado e refeito na 2ª tentativa |
| Área fora da lista fechada | Rejeitada pelo esquema |
| 8 lotes pela API simulada | 354 CBOs; 9 chamadas (1 repetição) |
| Segunda execução | 0 chamadas novas (cache) |
| M2 com divergência proposital (784205 como Técnico) | Detectada |
| Importação do plano B | 354 CBOs validadas |
| M4 | 473 CBOs por herança, 751 como Outros, 0 sem área |

**Aceite (100% das CBOs de B–F com área e nível; zero fora da lista)**
- Atendido pela lógica nos testes simulados. **Pendente** da execução real.

**Números**
- 1.578 CBOs em B–F; 354 no escopo (95% dos movimentos), como no SDD.
- As 9 CBOs sem título (V20) ficam todas fora do escopo e seguem a regra M4: 2 por herança, as demais como Outros. A regra de confiança baixa fica ativa se alguma entrar no escopo.
- "Outros": 751 CBOs, 2,44% dos movimentos (V22, informativo).

**Ainda não disponíveis (dependem da execução real):** distribuição por área e nível, 20 CBOs de exemplo, listas M1 e M2. Tudo sai em `reports/macrofamilias_validacao.md`.

**Pontos novos:** V22 (Outros), informativo, registrado no SDD.

**Para você em casa (na ordem)**
1. `cp .env.example .env` e cole a chave no `.env` (não no chat).
2. `python src/referencias.py`, depois `python run_pipeline.py` (V21).
3. `python src/macrofamilias.py --llm`.
4. Abra `reports/macrofamilias_validacao.md` e veja as listas M1 e M2.
5. Dois revisores preenchem `reports/revisao_macrofamilias.csv` (M3). Isso pode correr em paralelo à Fase 3.

**Próxima fase (ao receber "pode seguir"):** Fase 3 — `src/kpis.py` e T2 a T5. Os KPIs por grupo setorial e o T2 não dependem de regiões nem de macrofamílias, então dá para adiantar; o que depende de microrregião e de macrofamília fica parametrizado e roda quando esses arquivos existirem.
