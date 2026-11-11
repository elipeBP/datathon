"""Página 1 — Onde: quais regiões e setores pedem atenção? (SDD 8.1)"""
import polars as pl
import streamlit as st

from app.dados import cfg, disponivel, ler, rodape
from src import graficos as g

st.title("Onde a indústria catarinense perde gente")

segmento = st.session_state.get("segmento", "Transformação")
sem_dominante = st.session_state.get("sem_dominante", False)

grupo = st.session_state.get("grupo", "Todos")
sufixo = "_sem_cbo_dominante" if sem_dominante else ""
seg = ler(f"kpis_segmento{sufixo}").filter(pl.col("segmento") == segmento).row(0, named=True)
grp = ler(f"kpis_grupo_setorial{sufixo}")
ref = seg["kpi1_pct_a_pedido"]
if grupo != "Todos":
    seg = grp.filter((pl.col("segmento") == segmento) & (pl.col("grupo_setorial") == grupo)).row(0, named=True)
    st.caption(f"Cartões: {grupo}. As barras abaixo continuam mostrando todos os grupos do segmento.")

# ---------------------------------------------------------------- cartões de KPI
c1, c2, c3, c4 = st.columns(4)
c1.metric("Saídas a pedido", g.fmt_pct(seg["kpi1_pct_a_pedido"]),
          help=f"KPI 1 · desligamentos a pedido ÷ desligamentos · n = {g.fmt_int(seg['desligamentos'])}")
c2.metric("Saldo por 10 mil hab.", f"{seg['kpi2_saldo_10mil_hab']:+.1f}".replace(".", ","),
          help=f"KPI 2 · saldo de 12 meses = {g.fmt_int(seg['saldo'])} · n = {g.fmt_int(seg['movimentos'])} movimentos")
if "kpi3_premio_contratacao" in seg and seg.get("kpi3_premio_contratacao") is not None:
    c3.metric("Prêmio de contratação", f"{seg['kpi3_premio_contratacao']:.3f}".replace(".", ","),
              help=f"KPI 3 · mediana admissão ÷ desligamento, mesma CBO e microrregião · cobertura {seg['kpi3_cobertura_pct']:.0f}%")
    c4.metric("Descasamento de escolaridade", f"{seg['kpi4_descasamento_sup_pp']:+.1f}".replace(".", ",") + " p.p.",
              help=f"KPI 4 · % superior nos admitidos − nos desligados · cobertura {seg['kpi4_cobertura_pct']:.0f}%")
else:
    c3.metric("Prêmio de contratação", "—", help="Aguardando as microrregiões do IBGE (células CBO × microrregião).")
    c4.metric("Descasamento de escolaridade", "—", help="Aguardando as microrregiões do IBGE.")

# ---------------------------------------------------------------- mapa e quadrantes
if disponivel("kpis_microrregiao") and cfg.GEOJSON_MICRO.exists():
    st.plotly_chart(g.mapa_microrregioes(ler("kpis_microrregiao"), cfg.GEOJSON_MICRO, segmento), width="stretch")
if disponivel("quadrantes"):
    q = ler("quadrantes")
    if q.filter(pl.col("segmento") == segmento).height:
        st.plotly_chart(g.dispersao_quadrantes(q, segmento), width="stretch")
    mic = ler("kpis_microrregiao").filter((pl.col("segmento") == segmento) & pl.col("kpi1_suficiente"))
    st.subheader("Ranking das microrregiões por saídas a pedido")
    st.dataframe(mic.sort("kpi1_pct_a_pedido", descending=True).select(
        "microrregiao", "mesorregiao", "kpi1_pct_a_pedido", "kpi2_saldo_10mil_hab", "movimentos").to_pandas(),
        hide_index=True, width="stretch",
        column_config={"kpi1_pct_a_pedido": st.column_config.NumberColumn("% a pedido", format="%.1f"),
                       "kpi2_saldo_10mil_hab": st.column_config.NumberColumn("Saldo/10 mil hab.", format="%.1f"),
                       "movimentos": st.column_config.NumberColumn("Movimentos", format="%d")})
else:
    st.info("Mapa, quadrantes e ranking de microrregiões aparecem quando `data/reference/municipios_regioes.csv` "
            "e o GeoJSON existirem (rode `python src/referencias.py` e depois `python run_pipeline.py`).")

# ---------------------------------------------------------------- setores
st.plotly_chart(g.barras_pedido_grupo(grp, ref, segmento), width="stretch")
if segmento == "Transformação":
    with st.expander("Quanto disso é uma única ocupação? (teste T3)"):
        st.plotly_chart(g.barras_com_sem(ler("kpis_grupo_setorial"), ler("kpis_grupo_setorial_sem_cbo_dominante"),
                                         segmento, "Alimentador de linha"), width="stretch")

rodape()
