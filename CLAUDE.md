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
python src/modelo.py                # modelo das saídas a pedido (mercado e perfil)
python src/exportar_web.py          # web/public/dados.json para o site
cd web && npm run dev               # site React local
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

## Estado atual (12/11/2026)

- Fases 1 a 4 entregues (relatórios em `docs/processo/`). Regiões do IBGE baixadas; macrofamílias classificadas no `gemini-3.5-flash-lite` (V28); recomendações aprovadas em `app/recomendacoes.yaml` (o pipeline não sobrescreve).
- Modelo estatístico das saídas a pedido em `src/modelo.py` (V29), relatório em `reports/modelo_saida_pedido.md`.
- Site React em `web/` (Vercel, raiz `web`): https://datathon-ebon.vercel.app. Assistente em `web/api/perguntar.js`; a chave fica na variável `GEMINI_API_KEY` da Vercel.
- Painel Python (Streamlit) em `app/`, entregável do Guia; roda localmente.
- Pendente com a equipe: revisão humana M3 (`reports/revisao_macrofamilias.csv`) para fechar o T6.
- Depois de mudar dados: `python run_pipeline.py` regenera `data/processed/`, `web/public/dados.json` e `web/api/_base.js`/`_dados.js`; depois `cd web && npm run build`.
