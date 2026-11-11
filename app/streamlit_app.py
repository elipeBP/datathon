"""Painel do Datathon CDIA 2026 — Raio-X do Mercado de Trabalho Industrial de SC.

    streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.dados import filtros_globais  # noqa: E402

st.set_page_config(page_title="Raio-X do trabalho industrial de SC", layout="wide")

paginas = [
    st.Page("paginas/onde.py", title="1. Onde", default=True),
    st.Page("paginas/por_que.py", title="2. Por quê"),
    st.Page("paginas/o_que.py", title="3. O quê"),
]
nav = st.navigation(paginas)
filtros_globais()
nav.run()
