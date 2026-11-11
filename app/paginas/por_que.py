"""Página 2 — Por quê: o gargalo é salário, escolaridade ou rotatividade? (SDD 8.1)"""
import polars as pl
import streamlit as st

from app.dados import disponivel, ler, rodape
from src import graficos as g

segmento = st.session_state.get("segmento", "Transformação")
grupo = st.session_state.get("grupo", "Todos")
micro = st.session_state.get("micro", "Todas")
recorte = " · ".join(x for x in [segmento, None if grupo == "Todos" else grupo, None if micro == "Todas" else micro] if x)

st.title("Por que a indústria perde gente")
st.caption(f"Recorte: {recorte}. Mude o recorte na barra lateral.")

ref = ler("kpis_segmento").filter(pl.col("segmento") == segmento).row(0, named=True)


def filtrar(t: pl.DataFrame) -> pl.DataFrame:
    t = t.filter(pl.col("segmento") == segmento)
    if grupo != "Todos" and "grupo_setorial" in t.columns:
        t = t.filter(pl.col("grupo_setorial") == grupo)
    if micro != "Todas" and "microrregiao" in t.columns:
        t = t.filter(pl.col("microrregiao") == micro)
    return t


# ---------------------------------------------------------------- KPIs por macrofamília
st.header("Quais ocupações concentram as saídas")
fonte = {(False, False): "kpis_macrofamilia", (True, False): "kpis_grupo_macrofamilia",
         (False, True): "kpis_micro_macrofamilia", (True, True): "kpis_micro_grupo_macrofamilia"}[(grupo != "Todos", micro != "Todas")]
if disponivel(fonte):
    t = filtrar(ler(fonte))
    areas = sorted(t["area"].unique().to_list())
    niveis = sorted(t["nivel"].unique().to_list())
    c1, c2 = st.columns(2)
    sel_a = c1.multiselect("Área", areas, default=areas)
    sel_n = c2.multiselect("Nível de formação", niveis, default=niveis)
    t = t.filter(pl.col("area").is_in(sel_a) & pl.col("nivel").is_in(sel_n))
    if t.height:
        st.plotly_chart(g.barras_kpi_macrofamilia(t, ref["kpi1_pct_a_pedido"], recorte), width="stretch")
        cols = ["area", "nivel", "kpi1_pct_a_pedido", "desligamentos", "kpi2_saldo_10mil_hab"]
        cols += [c for c in ["kpi3_premio_contratacao", "kpi3_cobertura_pct", "kpi4_descasamento_sup_pp", "kpi4_cobertura_pct"] if c in t.columns]
        st.dataframe(t.sort("kpi1_pct_a_pedido", descending=True).select(cols).to_pandas(), hide_index=True, width="stretch",
                     column_config={
                         "area": "Área", "nivel": "Nível",
                         "kpi1_pct_a_pedido": st.column_config.NumberColumn("% a pedido", format="%.1f"),
                         "desligamentos": st.column_config.NumberColumn("n desligamentos", format="%d"),
                         "kpi2_saldo_10mil_hab": st.column_config.NumberColumn("Saldo/10 mil hab.", format="%.1f"),
                         "kpi3_premio_contratacao": st.column_config.NumberColumn("Prêmio de contratação", format="%.3f"),
                         "kpi3_cobertura_pct": st.column_config.NumberColumn("Cobertura KPI 3 (%)", format="%.0f"),
                         "kpi4_descasamento_sup_pp": st.column_config.NumberColumn("Descasamento sup. (p.p.)", format="%.1f"),
                         "kpi4_cobertura_pct": st.column_config.NumberColumn("Cobertura KPI 4 (%)", format="%.0f")})
        st.caption("Prêmio de contratação e descasamento são calculados dentro da mesma ocupação e microrregião e depois ponderados (SDD 5.2). "
                   "A cobertura mostra quanto do recorte entrou no cálculo.")
    else:
        st.info("Nenhuma macrofamília com os filtros escolhidos.")
else:
    st.info("Os KPIs por macrofamília aparecem quando `data/reference/macrofamilias.csv` existir (Fase 2, Gemini) "
            "e, para recortes por microrregião, quando as regiões do IBGE estiverem baixadas.")

# ---------------------------------------------------------------- perfil admitidos × desligados
st.header("Quem entra e quem sai")
usa_micro = micro != "Todas" and disponivel("perfil_escolaridade_micro_grupo")
esc = ler("perfil_escolaridade_micro_grupo" if usa_micro else "perfil_escolaridade_grupo")
sal = ler("perfil_salario_micro_grupo" if usa_micro else "perfil_salario_grupo")
esc_r, sal_r = filtrar(esc), filtrar(sal)
c1, c2 = st.columns(2)
if esc_r.height:
    c1.plotly_chart(g.perfil_escolaridade(esc_r, recorte), width="stretch")
if sal_r.height:
    rotulo = "grupo_setorial"
    c2.plotly_chart(g.salario_adm_desl(sal_r.group_by(rotulo, "tipo").agg(pl.col("salario_mediano").first()), rotulo), width="stretch")
st.caption("Escolaridade e salário são associados às saídas; os dados não permitem afirmar causa.")

rodape()
