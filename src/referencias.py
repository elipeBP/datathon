"""R11, R12, R12b: tabelas de referência em data/reference/.

Rodar uma vez (precisa de internet para a API do IBGE) e versionar o resultado no Git:
    python src/referencias.py            # tudo
    python src/referencias.py --offline  # só dicionário e municípios (sem IBGE)
"""
import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402
from src.log import registrar  # noqa: E402

COL_COD = "Código [-]"
COL_NOME = "Município [-]"
COL_POP = "População no último censo - pessoas [2022]"


# ---------------------------------------------------------------- R11
def ler_municipios(caminho: Path = cfg.MUNICIPIOS_CSV) -> pd.DataFrame:
    """CSV do evento: mantém só linhas com código ^42\\d{5}$ (remove o rodapé HTML)."""
    df = pd.read_csv(caminho, dtype=str, on_bad_lines="skip")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df[df[COL_COD].fillna("").str.fullmatch(r"42\d{5}")].copy()
    for c in df.columns.drop([COL_COD, COL_NOME, "Gentílico [-]", "Prefeito [2025]"], errors="ignore"):
        df[c] = pd.to_numeric(df[c].replace("-", pd.NA), errors="coerce")
    df["cod7"] = df[COL_COD]
    df["cod6"] = df["cod7"].str[:6]
    df = df.rename(columns={COL_NOME: "municipio_nome", COL_POP: "pop_censo2022"})
    return df[["cod7", "cod6", "municipio_nome", "pop_censo2022"]]


# ---------------------------------------------------------------- R12
def _get(url: str, tentativas: int = 3) -> requests.Response:
    for i in range(tentativas):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if i == tentativas - 1:
                raise
            time.sleep(2 ** i)


def baixar_regioes() -> pd.DataFrame:
    """Lista de municípios de SC com microrregião e mesorregião (API de localidades do IBGE)."""
    dados = _get(cfg.IBGE_MUNICIPIOS_URL).json()
    linhas = []
    for m in dados:
        micro = m.get("microrregiao") or {}
        meso = micro.get("mesorregiao") or {}
        linhas.append({
            "cod7": str(m["id"]),
            "cod6": str(m["id"])[:6],
            "municipio": m["nome"],
            "cod_microrregiao": str(micro["id"]) if micro.get("id") else None,
            "microrregiao": micro.get("nome"),
            "cod_mesorregiao": str(meso["id"]) if meso.get("id") else None,
            "mesorregiao": meso.get("nome"),
        })
    df = pd.DataFrame(linhas).sort_values("cod7").reset_index(drop=True)
    sem_micro = df[df["cod_microrregiao"].isna()]
    if len(sem_micro):
        # SDD R12: parar e reportar, nunca atribuir no chute.
        raise SystemExit(
            "PARAR: municípios sem microrregião na API do IBGE:\n"
            + sem_micro[["cod7", "municipio"]].to_string(index=False)
            + "\nReporte ao usuário antes de seguir."
        )
    return df


def _area_assinada(anel: list) -> float:
    """Fórmula do laço (lon = x, lat = y): positiva = anti-horário, negativa = horário."""
    return sum(x1 * y2 - x2 * y1 for (x1, y1, *_), (x2, y2, *_) in zip(anel, anel[1:] + anel[:1])) / 2


def orientar_para_plotly(geo: dict) -> dict:
    """O Plotly (d3-geo) exige anel externo no sentido horário e buracos no anti-horário.
    O IBGE segue a RFC 7946 (o contrário); sem isso, cada polígono vira 'o mundo menos a região'
    e o mapa pinta o fundo inteiro."""
    def ajustar(poligono: list) -> list:
        saida = []
        for i, anel in enumerate(poligono):
            horario = _area_assinada(anel) < 0
            externo = i == 0
            saida.append(anel if horario == externo else anel[::-1])
        return saida

    for f in geo["features"]:
        g = f["geometry"]
        if g["type"] == "Polygon":
            g["coordinates"] = ajustar(g["coordinates"])
        elif g["type"] == "MultiPolygon":
            g["coordinates"] = [ajustar(p) for p in g["coordinates"]]
    return geo


def baixar_geojson() -> Path:
    """GeoJSON das microrregiões de SC (API de malhas v3 do IBGE), com os anéis orientados para o Plotly."""
    geo = orientar_para_plotly(_get(cfg.IBGE_MALHA_MICRO_URL).json())
    cfg.GEOJSON_MICRO.write_text(json.dumps(geo), encoding="utf-8")
    mb = cfg.GEOJSON_MICRO.stat().st_size / 1e6
    if mb > cfg.GEOJSON_MAX_MB:
        print(f"Aviso: GeoJSON com {mb:.1f} MB (> {cfg.GEOJSON_MAX_MB} MB). Simplificar a geometria (SDD R12).")
    return cfg.GEOJSON_MICRO


# ---------------------------------------------------------------- R12b
def extrair_dicionario() -> None:
    """Abas cbo2002ocupação e subclasse do dicionário, já com zfill."""
    cbo = pd.read_excel(cfg.DICIONARIO_XLSX, sheet_name="cbo2002ocupação", dtype=str)
    cbo.columns = ["cbo2002ocupacao", "titulo_cbo"]
    cbo["cbo2002ocupacao"] = cbo["cbo2002ocupacao"].str.strip().str.zfill(6)
    cbo.dropna().to_csv(cfg.CBO_TITULOS_CSV, index=False)

    sub = pd.read_excel(cfg.DICIONARIO_XLSX, sheet_name="subclasse", dtype=str)
    sub.columns = ["subclasse", "descricao_subclasse"]
    sub["subclasse"] = sub["subclasse"].str.strip().str.zfill(7)
    sub.dropna().to_csv(cfg.SUBCLASSE_CSV, index=False)
    registrar("Dicionário (R12b)", [("Títulos de CBO", f"{len(cbo):,}"), ("Subclasses CNAE", f"{len(sub):,}")])


def main(offline: bool = False) -> None:
    cfg.REFERENCE.mkdir(parents=True, exist_ok=True)
    extrair_dicionario()
    mun = ler_municipios()
    registrar("Municípios do evento (R11)", [("Municípios válidos", str(len(mun))),
                                             ("População total (Censo 2022)", f"{mun['pop_censo2022'].sum():,.0f}")])
    if offline:
        print("Modo offline: regiões e GeoJSON do IBGE não foram baixados.")
        return
    reg = baixar_regioes()
    faltando = set(mun["cod6"]) - set(reg["cod6"])
    if faltando:
        raise SystemExit(f"PARAR: municípios do evento sem região no IBGE: {sorted(faltando)}")
    reg.to_csv(cfg.MUNICIPIOS_REGIOES_CSV, index=False)
    baixar_geojson()
    registrar("Regiões IBGE (R12)", [
        ("Municípios", str(reg["cod7"].nunique())),
        ("Microrregiões", str(reg["cod_microrregiao"].nunique())),
        ("Mesorregiões", str(reg["cod_mesorregiao"].nunique())),
        ("Nulos", str(int(reg.isna().sum().sum()))),
        ("GeoJSON (MB)", f"{cfg.GEOJSON_MICRO.stat().st_size / 1e6:.2f}"),
    ])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--offline", action="store_true")
    main(p.parse_args().offline)
