# CLAUDE.md — Datathon CDIA 2026 (Raio-X do Mercado de Trabalho Industrial de SC)

O contrato do projeto é `docs/SDD_v2.md`. Leia-o inteiro antes de qualquer tarefa. Onde algo conflitar, vale o SDD.

## Regras de trabalho

1. **Fase por fase** (SDD seção 10). No fim de cada fase: rode o aceite, escreva o relatório de checkpoint abaixo e **pare** até o usuário responder "pode seguir".
2. **Dúvida não se resolve no chute.** Se algo não está no SDD ou o dado o contradiz, pare, registre como V19, V20… na seção 2.3 do SDD e pergunte ao usuário (o decisor é o Pietro).
3. **Diagnóstico antes de correção.** Antes de mudar filtro ou fórmula, rode uma checagem somente leitura e mostre o número que justifica.
4. **Tudo parametrizado** em `config.py`.
5. **Nunca** versionar `data/raw/`, `data/interim/` ou `.env`. Nunca imprimir, logar ou pedir no chat a `GEMINI_API_KEY`.
6. Códigos (CBO, CNAE, município) **sempre como texto**.
7. Commits pequenos, em português, propostos ao usuário no fim de cada fase.

## Comandos

```bash
python run_pipeline.py              # ingestão → referências → limpeza → testes (sem LLM)
python src/referencias.py           # baixa regiões e GeoJSON do IBGE (precisa de internet; rodar uma vez)
python src/testes.py                # T1 + conferência da seção 3
python src/kpis.py                  # KPIs em data/processed/
python src/figuras.py               # PNGs em reports/figures/
streamlit run app/streamlit_app.py  # painel
python src/recomendacoes.py         # rascunho das 3 recomendações
python src/auditoria.py             # antes do push
python src/macrofamilias.py --llm   # classifica as 354 CBOs no Gemini (~8 chamadas, com cache)
python src/macrofamilias.py --plano-b data/interim/resposta_plano_b.json   # plano B (chat)
```

## Formato do relatório de checkpoint

```
## Checkpoint N — <nome da fase>
**Status:** aprovado | aprovado com ressalvas | reprovado
**Entregas:** lista de arquivos criados ou alterados
**Aceite:** cada critério da fase → resultado com número
**Números que não bateram com o SDD:** fato · obtido · esperado · explicação
**Pontos novos (V19…):** dúvida · por que importa · padrão provisório
**Decisões que preciso do usuário:** perguntas objetivas, numeradas
**Próxima fase:** o que será feito ao receber "pode seguir"
```

## Estado atual

- Fase 1 entregue e aprovada (`reports/checkpoint_1.md`). Pendente do usuário: rodar `python src/referencias.py` (V21).
- Fase 4 entregue (`reports/checkpoint_4.md`). Falta o fechamento na máquina do Pietro: regiões, Gemini, revisão M3, aprovação das recomendações, git e deploy.
- Fase 3 entregue (`reports/checkpoint_3.md`): KPIs, T2–T5, figuras e página Onde. Recortes regionais e por macrofamília rodam quando os arquivos existirem.
- Fase 2 entregue em código (`reports/checkpoint_2.md`). Falta a execução real: criar `.env` e rodar `python src/macrofamilias.py --llm`; depois dois revisores preenchem `reports/revisao_macrofamilias.csv` (M3).
