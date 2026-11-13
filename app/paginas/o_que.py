"""Página 3 — O quê: o que o cliente deve fazer? (SDD 8.1 e 8.3)"""
import streamlit as st
import yaml

from app.dados import cfg, rodape

st.title("O que fazer: três decisões e como medir o resultado")

dados = yaml.safe_load(cfg.RECOMENDACOES_YAML.read_text(encoding="utf-8")) if cfg.RECOMENDACOES_YAML.exists() else None
recs = (dados or {}).get("recomendacoes") or []

if not recs:
    motivo = (dados or {}).get("motivo", "o arquivo app/recomendacoes.yaml ainda não foi gerado")
    st.info(f"Recomendações pendentes: {motivo}. Rode `python src/recomendacoes.py` depois que regiões e macrofamílias existirem.")
else:
    if any(r.get("status") != "aprovada" for r in recs):
        st.warning("Rascunho gerado automaticamente a partir dos números. A equipe ainda precisa revisar e aprovar "
                   "(`status: aprovada` em app/recomendacoes.yaml).")
    for i, r in enumerate(recs, 1):
        with st.container(border=True):
            st.subheader(f"{i}. {r.get('titulo_curto') or r['acao']}")
            st.markdown(f"**Para quem (macrofamília da IA):** {r['macrofamilia']}  \n**Onde:** {r.get('onde_curto') or r['regiao']}  \n"
                        f"**Quem executa:** {r['quem_executa']}")
            st.markdown(f"**Por quê:** {r.get('porque_curto') or r['porque'] + '.'}")
            if r.get("evidencia_modelo"):
                st.caption(f"Modelo estatístico: {r['evidencia_modelo']}")
            ind = r.get("indicador_de_acompanhamento") or {}
            if ind:
                c1, c2 = st.columns(2)
                base, ref, unidade = ind.get("linha_de_base"), ind.get("referencia_sc"), ind.get("unidade", "%")
                if unidade == "%":
                    valor = f"{base:.1f}%".replace(".", ",")
                    delta = f"{base - ref:+.1f} p.p. vs SC".replace(".", ",") if ref is not None else None
                else:
                    valor, delta = f"{base:+,.0f} {unidade}".replace(",", "."), None
                c1.metric("Linha de base hoje", valor, delta=delta, delta_color="inverse")
                c2.markdown(f"**Meta:** {r.get('meta', 'acompanhar')}. **Como saber se funcionou:** acompanhar {ind['kpi']} ({ind['fonte']}).")

rodape()
