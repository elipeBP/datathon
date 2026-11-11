"""Leitura dos agregados do painel. O app nunca lê data/raw/ nem data/interim/ (SDD 8.4)."""
import sys
from pathlib import Path

import polars as pl
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import config as cfg  # noqa: E402

TEXTO = {"cod_microrregiao": pl.Utf8, "cod_mesorregiao": pl.Utf8, "divisao_cnae": pl.Utf8, "municipio": pl.Utf8}


@st.cache_data
def ler(nome: str) -> pl.DataFrame | None:
    p = cfg.PROCESSED / f"{nome}.csv"
    return pl.read_csv(p, schema_overrides=TEXTO) if p.exists() else None


def filtros_globais() -> None:
    """Barra lateral única para as três páginas (SDD 8.2). Valores ficam em st.session_state."""
    seg = ler("kpis_segmento")
    segmentos = seg["segmento"].to_list()
    st.sidebar.selectbox("Segmento", segmentos, index=segmentos.index("Transformação"), key="segmento")
    grupos = ler("kpis_grupo_setorial").filter(pl.col("segmento") == st.session_state["segmento"])["grupo_setorial"].to_list()
    st.sidebar.selectbox("Grupo setorial", ["Todos", *sorted(grupos)], key="grupo")
    mic = ler("kpis_microrregiao")
    if mic is not None:
        mesos = sorted(mic["mesorregiao"].unique().to_list())
        st.sidebar.selectbox("Mesorregião", ["Todas", *mesos], key="meso")
        m = mic if st.session_state["meso"] == "Todas" else mic.filter(pl.col("mesorregiao") == st.session_state["meso"])
        st.sidebar.selectbox("Microrregião", ["Todas", *sorted(m["microrregiao"].unique().to_list())], key="micro")
    else:
        st.session_state["meso"] = st.session_state["micro"] = "Todas"
    st.sidebar.toggle("Excluir alimentador de linha (CBO 784205)", key="sem_dominante",
                      help="Teste T3: uma única ocupação responde por cerca de um quarto dos movimentos da transformação.")


def disponivel(nome: str) -> bool:
    return (cfg.PROCESSED / f"{nome}.csv").exists()


def rodape() -> None:
    st.divider()
    st.caption("Fonte: Novo CAGED (MTE), microdados de Santa Catarina, set/2025–ago/2026. "
               "Indústria = seções CNAE B–F; análise principal na transformação (C); construção (F) separada. "
               "População: Censo 2022 (IBGE).")
    with st.expander("Premissas e limites"):
        st.markdown(
            "- O CAGED mede **fluxo** (admissões e desligamentos), não estoque nem vagas abertas. "
            "\"Apagão\" é inferido por sinais indiretos: saídas a pedido, saldo, prêmio salarial e escolaridade.\n"
            "- Escolaridade e salário são **associados** aos gargalos; os dados não permitem afirmar causalidade.\n"
            "- Recortes abaixo do volume mínimo aparecem em cinza e não entram em ranking.\n"
            "- Linhas idênticas foram mantidas, como nos números oficiais.\n"
            "- Na construção, o saldo jan–mai/2026 fica 54 vagas (0,5%) acima do boletim da FIESC.\n"
            "- A lista completa está no README do repositório.")
